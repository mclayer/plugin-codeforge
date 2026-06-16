#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ADR-103 Amendment 3 §결정 7-B — A-prime forward 동기화 스캐폴드 (git → Confluence 자동)
# ADR-061 §결정 1 — 외부 .py 파일 (bash heredoc 안 multi-line Python 금지)
# ADR-111 §결정 1/2 — mirror 대상 closed-enum + Issue-only retain 면제
# ADR-123 — 읽기 표준 (AI 재렌더 기준)
"""git → Confluence forward 동기화 스캐폴드 (A-prime 운영 모델, 앞 방향).

운영 모델 (A-prime, ADR-103 Amendment 3 §결정 7):
    git = 작성 정본(SoR-work) — 변하지 않음.
    Confluence = 공식 "정본 읽기 + 사람 편집 화면" 으로 격상.
    forward (본 스크립트) = git 문서 변경(main 머지) → Confluence 자동 갱신.
    backward (별도, 설계만) = 사람이 Confluence 편집 → git PR 제안 으로 역류.

모드 2개:
    --build-manifest : Confluence space 의 페이지(title → id)를 조회해 git 문서와
                       title 로 매칭하고 docs/confluence-mirror-manifest.yaml 을 생성/갱신.
    (기본 sync 모드)  : 인자로 받은 변경 파일 목록(또는 --git-diff 으로 git diff 추출)에서
                       mirror 대상 doc 만 골라 → manifest 에서 page id 찾기 →
                       Anthropic API 로 ADR-123 읽기 표준 HTML 재렌더 →
                       Confluence REST 로 update. manifest 에 없으면 "최초 수동 발행 필요" 로그.

환경변수 (secret):
    ANTHROPIC_API_KEY      : AI 재렌더용 Anthropic API 키.
    CONFLUENCE_BASE_URL    : Confluence 인스턴스 base URL (예: https://x.atlassian.net).
    CONFLUENCE_USER_EMAIL  : Confluence basic-auth 사용자 이메일.
    CONFLUENCE_API_TOKEN   : Confluence API 토큰.
    CONFLUENCE_SPACE_ID    : 대상 space id (--build-manifest 에 필요).

한계 (정직 declare):
    - secret 부재 시 dry-run — 실제 네트워크 호출 0건. 무엇이 바뀌었고 어느 page 로
      갈지만 로그한다 (안전 동작, ADR-103 Amendment 3 §결정 7-E).
    - ADF / Confluence storage format 은 LOSSY (round-trip 비-deterministic). 본
      스크립트는 git source 를 정본으로 한 방향 push 만 한다 (backward 미포함).
    - scaffold-only — 실제 Anthropic / Confluence REST 호출부는 의존성(requests 등)
      가용 시에만 동작하며, 미가용/secret 부재 시 dry-run 으로 안전 fallback.
    - manifest 에 없는 문서는 자동 신규 생성하지 않는다 (중복 페이지 대량 생성 차단,
      playbook §재이관 절차 정합) — "최초 수동 발행 필요" 로그 후 skip.

본 스크립트는 declaration + scaffold 수준이다 — 실제 자동 발행 활성화는 secret 주입 +
manifest 전수 채움(후속 과제) 이후다.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── 상수 ──────────────────────────────────────────────────────────────────

MANIFEST_PATH = Path("docs/confluence-mirror-manifest.yaml")

# mirror 대상 path prefix (ADR-111 §결정 1 closed-enum 5 + 사람이 읽는 안내서).
#   ADR / Living Architecture / Change Plan / Domain Knowledge / Orchestrator Playbook
#   + guides (안내서). wrapper repo 는 ADR 을 archive/adr/ 에 둔다 (소비자는 docs/adr/).
MIRROR_PREFIXES = (
    "archive/adr/",
    "docs/adr/",
    "docs/architecture/",
    "docs/change-plans/",
    "docs/domain-knowledge/",
    "docs/orchestrator-playbook.md",
    "docs/consumer-guide.md",
    "docs/confluence-mirror-playbook.md",
)

# Issue-only retain 면제 (ADR-111 §결정 2) — Confluence mirror 금지.
#   Story file / FIX Ledger / Lane Evidence / decision packet / spawn prompt.
RETAIN_BAN_PREFIXES = (
    "docs/stories/",
    "decisions/",
)

# secret 환경변수 이름 (부재 시 dry-run).
SECRET_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "CONFLUENCE_BASE_URL",
    "CONFLUENCE_USER_EMAIL",
    "CONFLUENCE_API_TOKEN",
)


# ── secret / 모드 판정 ────────────────────────────────────────────────────

def secrets_present(extra=()):
    """필수 secret 환경변수가 모두 채워졌는지 확인. 하나라도 비면 False (→ dry-run)."""
    need = tuple(SECRET_ENV_VARS) + tuple(extra)
    return all(os.environ.get(v) for v in need)


def missing_secrets(extra=()):
    need = tuple(SECRET_ENV_VARS) + tuple(extra)
    return [v for v in need if not os.environ.get(v)]


# ── mirror 대상 분류 ──────────────────────────────────────────────────────

def is_retain_ban(path_str):
    """ADR-111 §결정 2 Issue-only retain 면제 영역인가 (Confluence mirror 금지)."""
    p = path_str.replace("\\", "/")
    if any(p.startswith(prefix) for prefix in RETAIN_BAN_PREFIXES):
        return True
    # Story file naming (docs/stories/<KEY>.md) 외에도 §10 FIX / §14 Lane Evidence 는
    # Story file 안 sub-section 이라 별도 파일이 아님 — path prefix 로 충분히 cover.
    return False


def is_mirror_target(path_str):
    """ADR-111 §결정 1 closed-enum + guides 영역인가 (Confluence mirror 대상)."""
    p = path_str.replace("\\", "/")
    if is_retain_ban(p):
        return False
    if not p.endswith(".md"):
        return False
    return any(
        p == prefix or p.startswith(prefix) if prefix.endswith("/") else p == prefix
        for prefix in MIRROR_PREFIXES
    )


def collect_changed_docs(explicit_files, use_git_diff, diff_base):
    """변경 doc 목록을 mirror 대상으로 필터링해 반환.

    explicit_files: 인자로 받은 파일 경로 목록 (우선).
    use_git_diff:   True 면 git diff 으로 변경 파일 추출.
    diff_base:      git diff base ref (기본 origin/main).
    """
    candidates = []
    if explicit_files:
        candidates = list(explicit_files)
    elif use_git_diff:
        candidates = _git_diff_files(diff_base)
    targets = [c for c in candidates if is_mirror_target(c)]
    skipped_retain = [c for c in candidates if c.endswith(".md") and is_retain_ban(c)]
    return targets, skipped_retain


def _git_diff_files(base):
    """git diff --name-only <base>...HEAD 로 변경 파일 목록을 얻는다 (실패 시 빈 목록)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if out.returncode != 0:
            print(f"⚠ git diff 실패 (base={base}) — 빈 목록 처리", file=sys.stderr)
            return []
        return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    except FileNotFoundError:
        print("⚠ git 미설치 — 빈 목록 처리", file=sys.stderr)
        return []


# ── manifest 입출력 ───────────────────────────────────────────────────────

def load_manifest():
    """manifest YAML 을 dict 로 로드. 부재/파싱 실패 시 빈 mapping."""
    if not MANIFEST_PATH.exists():
        return {"pages": {}}
    try:
        import yaml
    except ImportError:
        print("⚠ pyyaml 미설치 — manifest 파싱 skip (dry-run 로그만)", file=sys.stderr)
        return {"pages": {}}
    try:
        data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"pages": {}}
        data.setdefault("pages", {})
        return data
    except Exception as e:
        print(f"⚠ manifest 파싱 실패 ({type(e).__name__}) — 빈 처리", file=sys.stderr)
        return {"pages": {}}


def page_id_for(manifest, path_str):
    """manifest 에서 파일경로 → page_id 조회. 없으면 None."""
    pages = manifest.get("pages", {}) or {}
    p = path_str.replace("\\", "/")
    entry = pages.get(p)
    if isinstance(entry, dict):
        return entry.get("page_id")
    return entry  # scalar page_id 도 허용


# ── ADR-123 읽기 표준 AI 재렌더 (scaffold) ────────────────────────────────

def render_reading_html(md_path, dry_run):
    """git markdown 을 ADR-123 읽기 표준 HTML 로 재렌더.

    dry_run 또는 의존성/secret 부재 시 실제 Anthropic 호출을 하지 않고 None 반환.
    실제 호출부는 scaffold — requests/anthropic SDK 가용 + secret 존재 시에만 동작.
    """
    if dry_run:
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    # NOTE(scaffold): 실제 Anthropic API 호출은 후속 과제. ADR-123 읽기 표준
    #   (쉬운 말 / 구조 결론 우선 / 출처 패널 data-type="panel-note" / 한글 제목)
    #   프롬프트로 md → HTML 재렌더. 의존성(anthropic SDK 또는 requests) 가용 시 wire.
    #   현 단계는 declaration + scaffold 이므로 미구현 표식 후 None 반환 (dry-run 동급).
    print(
        f"  · [scaffold] ADR-123 AI 재렌더 미구현 — 실제 호출부는 후속 과제 ({md_path})",
        file=sys.stderr,
    )
    return None


# ── Confluence REST update (scaffold) ─────────────────────────────────────

def push_to_confluence(page_id, html, md_path, dry_run):
    """Confluence REST 로 page update (3-anchor stamp 동반, §결정 2).

    dry_run 시 실제 호출 0건 — 무엇을 어느 page 로 보낼지만 로그.
    """
    if dry_run:
        print(f"  · [dry-run] update 예정: {md_path} → page_id={page_id} (실 호출 0)")
        return "dry-run"
    # NOTE(scaffold): 실제 Confluence REST v2 update + content property 3-anchor stamp
    #   (A git-source-hash / B native version / C sync commit SHA, ADR-103 §결정 2)
    #   는 후속 과제. 의존성/secret 가용 시 wire.
    print(
        f"  · [scaffold] Confluence push 미구현 — 후속 과제: {md_path} → page_id={page_id}",
        file=sys.stderr,
    )
    return "scaffold-skip"


# ── 모드: --build-manifest ────────────────────────────────────────────────

def cmd_build_manifest(args):
    """Confluence space 페이지를 조회해 git 문서와 title 매칭, manifest 생성/갱신.

    secret(특히 CONFLUENCE_SPACE_ID 포함) 부재 시 dry-run — 실제 조회 0건,
    현재 manifest 상태 + mirror 대상 doc 목록만 로그.
    """
    extra = ("CONFLUENCE_SPACE_ID",)
    dry_run = not secrets_present(extra)
    if dry_run:
        miss = missing_secrets(extra)
        print(f"[build-manifest] dry-run (secret 부재: {miss}) — 실제 space 조회 0건.")

    manifest = load_manifest()
    existing = manifest.get("pages", {}) or {}
    print(f"[build-manifest] 현재 manifest entry 수: {len(existing)}")

    if dry_run:
        # mirror 대상 git 문서를 열거만 (실제 page id 매칭은 secret 필요).
        found = _enumerate_mirror_docs()
        print(f"[build-manifest] repo 내 mirror 대상 doc 수: {len(found)} (dry-run, 매칭 skip)")
        for f in found[:20]:
            mapped = "✓ manifest 존재" if f in existing else "· 좌표 미등록 (최초 수동 발행 필요)"
            print(f"  - {f} — {mapped}")
        if len(found) > 20:
            print(f"  … 외 {len(found) - 20} 건")
        print("[build-manifest] dry-run 종료 — secret 주입 후 실제 title→id 매칭 수행.")
        return 0

    # NOTE(scaffold): 실제 space 페이지 조회(getPagesInConfluenceSpace) + title 매칭은
    #   후속 과제. secret 가용 시 wire.
    print("[build-manifest] scaffold — 실제 space 조회/매칭은 후속 과제 (secret 가용).")
    return 0


def _enumerate_mirror_docs():
    """repo 안 mirror 대상 doc 경로를 enumerate (정렬)."""
    found = []
    for prefix in MIRROR_PREFIXES:
        if prefix.endswith("/"):
            base = Path(prefix)
            if base.exists():
                for md in sorted(base.rglob("*.md")):
                    s = str(md).replace("\\", "/")
                    if is_mirror_target(s):
                        found.append(s)
        else:
            if Path(prefix).exists() and is_mirror_target(prefix):
                found.append(prefix)
    return sorted(set(found))


# ── 모드: 기본 sync ───────────────────────────────────────────────────────

def cmd_sync(args):
    """변경 doc → manifest page id → AI 재렌더 → Confluence update (forward).

    secret 부재 시 dry-run — 변경 추출 + 매칭 결과만 로그, 실제 호출 0건.
    """
    dry_run = args.dry_run or not secrets_present()
    if dry_run:
        miss = missing_secrets() if not args.dry_run else ["(--dry-run 강제)"]
        print(f"[sync] dry-run (사유: {miss}) — 실제 AI/Confluence 호출 0건.")

    targets, skipped_retain = collect_changed_docs(
        args.files, args.git_diff, args.diff_base
    )

    if skipped_retain:
        print(f"[sync] Issue-only retain 면제 skip (ADR-111 §결정 2): {len(skipped_retain)} 건")
        for s in skipped_retain:
            print(f"  - {s} (Confluence mirror 금지 — git/Issue 채널 한정)")

    if not targets:
        print("[sync] mirror 대상 변경 doc 0건 — 종료.")
        return 0

    print(f"[sync] mirror 대상 변경 doc: {len(targets)} 건")
    manifest = load_manifest()
    need_manual = []
    pushed = 0

    for md in targets:
        page_id = page_id_for(manifest, md)
        if not page_id:
            need_manual.append(md)
            print(f"  - {md} → 좌표(page_id) 미등록 — 최초 수동 발행 필요 (skip)")
            continue
        print(f"  - {md} → page_id={page_id}")
        html = render_reading_html(md, dry_run)
        result = push_to_confluence(page_id, html, md, dry_run)
        if result == "dry-run":
            pushed += 1  # dry-run 도 "처리 예정" 으로 집계

    print(
        f"[sync] 처리 예정 {pushed} 건 / 최초 수동 발행 필요 {len(need_manual)} 건 "
        f"/ retain 면제 skip {len(skipped_retain)} 건"
    )
    if dry_run:
        print("[sync] dry-run 종료 — secret 주입 후 실제 재렌더 + 발행 수행.")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        prog="confluence_forward_sync.py",
        description="A-prime forward 동기화 (git → Confluence 자동). secret 부재 시 dry-run.",
    )
    p.add_argument(
        "--build-manifest",
        action="store_true",
        help="Confluence space 페이지를 조회해 git 문서와 title 매칭, manifest 생성/갱신.",
    )
    p.add_argument(
        "files",
        nargs="*",
        help="변경 파일 경로 목록 (기본 sync 모드). 비우고 --git-diff 사용 가능.",
    )
    p.add_argument(
        "--git-diff",
        action="store_true",
        help="git diff <base>...HEAD 으로 변경 파일 추출 (files 미지정 시).",
    )
    p.add_argument(
        "--diff-base",
        default="origin/main",
        help="git diff base ref (기본 origin/main).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="secret 유무와 무관하게 강제 dry-run (실제 호출 0).",
    )
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.build_manifest:
        return cmd_build_manifest(args)
    return cmd_sync(args)


if __name__ == "__main__":
    sys.exit(main())
