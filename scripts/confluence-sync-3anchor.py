#!/usr/bin/env python3
"""
confluence-sync-3anchor.py — git→Confluence 3-anchor stamp/verify 유틸리티 (ADR-103 §결정 2/3)

2 subcommand:
  stamp   — write path: 3-anchor 생성 후 Confluence content property 에 저장
  verify  — read path: content property 에서 3-anchor 읽어 git source 와 AND 비교

3-anchor 정의:
  A (git_source_sha256): sha256(정규화 markdown — CRLF→LF, trailing-whitespace 제거)
  B (page_version):      Confluence page version.number (REST API 응답)
  C (sync_commit_sha):   git rev-parse HEAD (sync 시점 commit SHA)

content property JSON schema (key: "codeforge.sync.anchors"):
  {
    "git_source_sha256": "<64자 hex>",
    "page_version": <int>,
    "sync_commit_sha": "<40자 hex>"
  }

exit code:
  0 — PASS (stamp 성공 또는 verify 3-anchor 전부 match)
  1 — FAIL (stamp 실패 또는 verify mismatch → git fallback)

[H3 resolve 결과 — WebFetch: developer.atlassian.com Confluence Cloud REST v1]
  WebFetch 로 SPA 렌더 문서 접근 실패 → well-known 패턴 사용 + [hypothesis] 박제.
  v1 content property endpoint 패턴:
    GET    /wiki/rest/api/content/{id}/property/{key}
    POST   /wiki/rest/api/content/{id}/property
    PUT    /wiki/rest/api/content/{id}/property/{key}
  [hypothesis] H3: v1 PUT vs POST (key 충돌 시 동작) / v2 /wiki/api/v2/pages/{id}/properties
  호환 여부 = A.4 cutover live 검증 필요.

token: os.environ["ATLASSIAN_API_TOKEN"] + os.environ["ATLASSIAN_USER_EMAIL"] (basic-auth)
literal 0 — 환경변수 간접 참조만 사용.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from typing import Optional

# ── 상수 ────────────────────────────────────────────────────────────────────
PROPERTY_KEY = "codeforge.sync.anchors"


# ── 공통 유틸 ────────────────────────────────────────────────────────────────

def _normalize_markdown(content: bytes) -> bytes:
    """정규화: CRLF→LF + trailing whitespace 제거 (anchor A 재현성 보장)."""
    text = content.decode("utf-8", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).encode("utf-8")


def _sha256_of_file(path: str) -> str:
    """git source 파일의 정규화 sha256 hex 반환."""
    with open(path, "rb") as f:
        raw = f.read()
    normalized = _normalize_markdown(raw)
    return hashlib.sha256(normalized).hexdigest()


def _sha256_of_text(text: str) -> str:
    """text 의 정규화 sha256 hex 반환 (verify path 재hash)."""
    raw = text.encode("utf-8")
    normalized = _normalize_markdown(raw)
    return hashlib.sha256(normalized).hexdigest()


def _git_head_sha(worktree: Optional[str] = None) -> str:
    """git rev-parse HEAD 로 현재 commit SHA 반환."""
    cmd = ["git"]
    if worktree:
        cmd += ["-C", worktree]
    cmd += ["rev-parse", "HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _git_sha_exists(sha: str, worktree: Optional[str] = None) -> bool:
    """git log 에서 특정 SHA 존재 여부 확인 (anchor C verify)."""
    cmd = ["git"]
    if worktree:
        cmd += ["-C", worktree]
    cmd += ["cat-file", "-e", f"{sha}^{{commit}}"]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def _basic_auth_header(email: str, token: str) -> str:
    """Atlassian basic auth header 값 생성 (literal 0)."""
    credential = f"{email}:{token}"
    encoded = base64.b64encode(credential.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


def _confluence_get_page(base_url: str, page_id: str, auth_header: str) -> dict:
    """Confluence REST v1: GET /wiki/rest/api/content/{id}?expand=version"""
    import urllib.request
    url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}?expand=version"
    req = urllib.request.Request(url, headers={
        "Authorization": auth_header,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _confluence_get_property(base_url: str, page_id: str, key: str,
                              auth_header: str) -> Optional[dict]:
    """
    Confluence REST v1: GET /wiki/rest/api/content/{id}/property/{key}
    [hypothesis] H3: 이 endpoint 가 실제 Cloud v1 에서 동작하는지 A.4 live 검증 필요.
    404 → None 반환 (property 미존재).
    """
    import urllib.request
    import urllib.error
    url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}/property/{key}"
    req = urllib.request.Request(url, headers={
        "Authorization": auth_header,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def _confluence_create_property(base_url: str, page_id: str, key: str,
                                  value: dict, auth_header: str) -> None:
    """
    Confluence REST v1: POST /wiki/rest/api/content/{id}/property
    [hypothesis] H3: key 충돌 시 동작 미검증 — A.4 cutover 에서 확인.
    """
    import urllib.request
    url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}/property"
    body = json.dumps({"key": key, "value": value}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        resp.read()


def _confluence_update_property(base_url: str, page_id: str, key: str,
                                  value: dict, version: int,
                                  auth_header: str) -> None:
    """
    Confluence REST v1: PUT /wiki/rest/api/content/{id}/property/{key}
    version 필드 포함 필수 (v1 낙관적 동시성 제어).
    [hypothesis] H3: 정확한 request body schema = A.4 live 검증.
    """
    import urllib.request
    url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}/property/{key}"
    body = json.dumps({
        "key": key,
        "value": value,
        "version": {"number": version},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT", headers={
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        resp.read()


def _upsert_property(base_url: str, page_id: str, key: str, value: dict,
                      auth_header: str) -> None:
    """GET 후 없으면 POST, 있으면 PUT (upsert)."""
    existing = _confluence_get_property(base_url, page_id, key, auth_header)
    if existing is None:
        _confluence_create_property(base_url, page_id, key, value, auth_header)
    else:
        current_version = existing.get("version", {}).get("number", 1)
        _confluence_update_property(base_url, page_id, key, value,
                                    current_version + 1, auth_header)


# ── subcommand: stamp ────────────────────────────────────────────────────────

def cmd_stamp(args: argparse.Namespace) -> int:
    """
    write path: 3-anchor 생성 + Confluence content property upsert.
    출력: stdout 에 JSON {git_source_sha256, page_version, sync_commit_sha}.
    exit 0 성공 / exit 1 실패.
    """
    email = os.environ["ATLASSIAN_USER_EMAIL"]   # literal 0
    token = os.environ["ATLASSIAN_API_TOKEN"]     # literal 0
    auth = _basic_auth_header(email, token)

    # anchor A
    anchor_a = _sha256_of_file(args.source_file)

    # anchor B — page 현재 version (stamp 후 최신 version 반영)
    page_data = _confluence_get_page(args.base_url, args.page_id, auth)
    anchor_b = page_data["version"]["number"]

    # anchor C
    anchor_c = _git_head_sha(args.worktree)

    payload = {
        "git_source_sha256": anchor_a,
        "page_version": anchor_b,
        "sync_commit_sha": anchor_c,
    }

    _upsert_property(args.base_url, args.page_id, PROPERTY_KEY, payload, auth)

    print(json.dumps(payload, ensure_ascii=False))
    return 0


# ── subcommand: verify ───────────────────────────────────────────────────────

def cmd_verify(args: argparse.Namespace) -> int:
    """
    read path: content property 3-anchor 읽어 git source 와 AND 비교.
    exit 0 = PASS (3-anchor 전부 match).
    exit 1 = MISMATCH (git fallback 트리거).
    stdout: JSON {verify_result, mismatches[]}.
    """
    email = os.environ["ATLASSIAN_USER_EMAIL"]   # literal 0
    token = os.environ["ATLASSIAN_API_TOKEN"]     # literal 0
    auth = _basic_auth_header(email, token)

    prop = _confluence_get_property(args.base_url, args.page_id,
                                    PROPERTY_KEY, auth)
    if prop is None:
        result = {"verify_result": "MISMATCH", "mismatches": ["property_not_found"]}
        print(json.dumps(result, ensure_ascii=False))
        return 1

    stored = prop.get("value", {})
    mismatches = []

    # anchor A — 재hash
    if args.source_file and os.path.exists(args.source_file):
        expected_a = _sha256_of_file(args.source_file)
        if stored.get("git_source_sha256") != expected_a:
            mismatches.append("anchor_a_hash_mismatch")

    # anchor B — page 현재 version
    page_data = _confluence_get_page(args.base_url, args.page_id, auth)
    current_version = page_data["version"]["number"]
    if stored.get("page_version") != current_version:
        mismatches.append("anchor_b_version_mismatch")

    # anchor C — git log 에서 SHA 존재 확인
    stored_sha = stored.get("sync_commit_sha", "")
    if stored_sha and not _git_sha_exists(stored_sha, args.worktree):
        mismatches.append("anchor_c_sha_not_in_history")

    if mismatches:
        result = {"verify_result": "MISMATCH", "mismatches": mismatches}
        print(json.dumps(result, ensure_ascii=False))
        return 1

    result = {"verify_result": "PASS", "mismatches": []}
    print(json.dumps(result, ensure_ascii=False))
    return 0


# ── CLI 진입점 ───────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="git→Confluence 3-anchor stamp/verify (ADR-103 §결정 2/3)"
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # stamp
    p_stamp = sub.add_parser("stamp", help="write path: 3-anchor stamp")
    p_stamp.add_argument("--page-id", required=True, help="Confluence page ID")
    p_stamp.add_argument("--source-file", required=True,
                         help="git source markdown 파일 경로")
    p_stamp.add_argument("--base-url",
                         default=os.environ.get("CONFLUENCE_BASE_URL",
                                                "https://mclayer.atlassian.net/wiki"),
                         help="Confluence base URL (기본값: CONFLUENCE_BASE_URL env)")
    p_stamp.add_argument("--worktree", default=None,
                         help="git worktree 절대 경로 (기본값: cwd)")

    # verify
    p_verify = sub.add_parser("verify", help="read path: 3-anchor verify")
    p_verify.add_argument("--page-id", required=True, help="Confluence page ID")
    p_verify.add_argument("--source-file", default=None,
                          help="anchor A 재hash 용 git source 파일 (선택)")
    p_verify.add_argument("--base-url",
                          default=os.environ.get("CONFLUENCE_BASE_URL",
                                                 "https://mclayer.atlassian.net/wiki"),
                          help="Confluence base URL")
    p_verify.add_argument("--worktree", default=None,
                          help="git worktree 절대 경로 (기본값: cwd)")

    args = parser.parse_args()

    if args.subcommand == "stamp":
        return cmd_stamp(args)
    elif args.subcommand == "verify":
        return cmd_verify(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
