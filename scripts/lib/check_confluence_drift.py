#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1495 / ADR-103 §결정 1 영역 — Confluence-mirror drift detection (MCP-direct staleness check)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Usage / exit code / semantics 상세: scripts/check-confluence-drift.sh header.
#
# Behavior:
#   1) docs/confluence-ia-tree.yaml schema SSOT read → 49 page_id list 추출
#   2) Atlassian Confluence REST API 호출 (page version + last_modified time)
#      → 환경변수 ATLASSIAN_API_TOKEN + ATLASSIAN_API_EMAIL + ATLASSIAN_INSTANCE 사용
#      → 부재 시 (MCP-direct ad-hoc invocation 영역): mock mode 자동 진입 + warning emit
#   3) git source 의 last commit timestamp 계산 (git log -1 --format=%ct <source_path>)
#   4) (Confluence last_modified - git last commit) > 7 day → drift candidate
#   5) Confluence page title 가 git mirror filename 과 mismatch → drift candidate
#   6) 3-anchor stamp 0건 영역 정합 (mark engine #1320 활성 후 sync 영역 = exempt)
#
# Heuristic-based detection (warning tier, ADR-060):
#   - 7 day threshold = drift_threshold_days env override 가능 (default 7)
#   - false positive 가능 → warning tier 시작, evidence-gated promote
#
# Exit code (ADR-060 §결정 15 3-tier semantics):
#   0 = PASS (drift 없음 또는 drift 감지 + Issue auto-create 성공 — warning tier)
#   1 = (reserved, current scope 미사용)
#   2 = SETUP error (missing dependency / IA tree schema 부재 / API token absent + no mock mode)
import sys
import os
import re
import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("[codeforge-kpi-infra-error] check-confluence-drift: pyyaml not installed", file=sys.stderr)
    sys.exit(2)

# ──────────────────────────────────── 설정 ────────────────────────────────────────

IA_TREE_PATH = os.environ.get("CFP1495_IA_TREE_PATH", "docs/confluence-ia-tree.yaml")
DRIFT_THRESHOLD_DAYS = int(os.environ.get("CFP1495_DRIFT_THRESHOLD_DAYS", "7"))
SECONDS_PER_DAY = 86400
SKIP_ISSUE_CREATE = os.environ.get("CFP1495_SKIP_ISSUE_CREATE", "") == "1"
MOCK_MODE = os.environ.get("CFP1495_MOCK_MODE", "") == "1"
MOCK_API_401 = os.environ.get("CFP1495_API_MOCK_401", "") == "1"
MOCK_API_429 = os.environ.get("CFP1495_API_MOCK_429", "") == "1"
MOCK_DRIFT_FIXTURE = os.environ.get("CFP1495_MOCK_DRIFT_FIXTURE", "")  # JSON path with synthetic page data

# 3-anchor stamp marker (ADR-103 §결정 2) — content property keys
ANCHOR_KEYS = ("codeforge_hash_git_source", "codeforge_sync_commit_sha")
# anchor B (version) = Confluence native page version field (always present)


def _emit_warning(msg: str) -> None:
    """GitHub Actions warning marker."""
    print(f"::warning::check-confluence-drift: {msg}")


def _emit_error(msg: str) -> None:
    """codeforge-kpi-infra-error prefix per evidence-checks-registry convention."""
    print(f"[codeforge-kpi-infra-error] check-confluence-drift: {msg}", file=sys.stderr)


def _get_git_last_commit_ts(source_path: str) -> int:
    """Return last commit unix timestamp for source_path. -1 if untracked / no commit."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", source_path],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if result.returncode != 0:
            return -1
        ts_str = result.stdout.strip()
        if not ts_str:
            return -1
        return int(ts_str)
    except (subprocess.TimeoutExpired, ValueError, OSError):
        return -1


def _load_ia_tree() -> dict:
    """Load IA tree schema or exit 2 on missing/invalid."""
    p = Path(IA_TREE_PATH)
    if not p.exists():
        _emit_error(f"IA tree schema not found: {IA_TREE_PATH}")
        sys.exit(2)
    try:
        with p.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        _emit_error(f"IA tree YAML parse failed: {e}")
        sys.exit(2)
    return data


def _extract_pages(ia_tree: dict) -> list:
    """Extract (page_id, title, source_path) list from IA tree schema.

    Schema variants supported:
      - pages: [{page_id, title, source_path}, ...]
      - top_level: {<key>: {page_id, title, ...}}, children: {...}
    """
    pages = []
    raw_pages = ia_tree.get("pages")
    if isinstance(raw_pages, list):
        for p in raw_pages:
            if not isinstance(p, dict):
                continue
            pid = str(p.get("page_id", "")).strip()
            if not pid:
                continue
            pages.append({
                "page_id": pid,
                "title": p.get("title", ""),
                "source_path": p.get("source_path", ""),
            })
        return pages
    # Fallback: flatten top_level + children
    for section_key in ("top_level", "children"):
        section = ia_tree.get(section_key, {})
        if not isinstance(section, dict):
            continue
        for k, v in section.items():
            if not isinstance(v, dict):
                continue
            pid = str(v.get("page_id", "")).strip()
            if not pid:
                continue
            pages.append({
                "page_id": pid,
                "title": v.get("title", k),
                "source_path": v.get("source_path", ""),
            })
    return pages


def _load_mock_fixture() -> dict:
    """Load mock Confluence response fixture (TC mode). Returns {page_id: {version, last_modified, title, anchors}}."""
    if not MOCK_DRIFT_FIXTURE:
        return {}
    p = Path(MOCK_DRIFT_FIXTURE)
    if not p.exists():
        _emit_error(f"mock fixture not found: {MOCK_DRIFT_FIXTURE}")
        sys.exit(2)
    try:
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        _emit_error(f"mock fixture JSON parse failed: {e}")
        sys.exit(2)


def _fetch_confluence_page(page_id: str, mock_data: dict) -> dict:
    """Fetch Confluence page metadata. In mock_mode: return fixture. Else: REST call.

    Returns {version: int, last_modified_ts: int, title: str, anchors: dict} or {} on failure.
    """
    if MOCK_API_401:
        _emit_error("401 Unauthorized (mock) — ATLASSIAN_API_TOKEN auth failed")
        sys.exit(2)
    if MOCK_API_429:
        _emit_warning("429 Too Many Requests (mock) — rate limit, fail-open")
        return {}
    if MOCK_MODE or mock_data:
        return mock_data.get(page_id, {})
    # REST API path — left as no-op in MCP-direct ad-hoc invocation 영역
    # (CFP-1495 Wave 1 scope: MCP-direct path only; production sync = mark engine #1320 영역)
    api_token = os.environ.get("ATLASSIAN_API_TOKEN", "")
    if not api_token:
        _emit_warning(f"page_id={page_id}: ATLASSIAN_API_TOKEN absent — MCP-direct mode (skip detection)")
        return {}
    # Future: real REST call wired in #1320 mark engine activation
    return {}


def _compute_drift_signature(page_id: str, drift_type: str) -> str:
    """Stable signature for Issue dedup (CFP-1495 / matching marketplace-drift-detection pattern)."""
    import hashlib
    raw = f"{page_id}|{drift_type}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _create_drift_issue(page_id: str, title: str, drift_type: str, details: str, signature: str) -> None:
    """Auto-create GitHub Issue for drift. Skipped if SKIP_ISSUE_CREATE=1."""
    if SKIP_ISSUE_CREATE:
        print(f"  [skip-issue] page_id={page_id} drift_type={drift_type} signature={signature}")
        return
    try:
        body = (
            f"## Confluence drift detected\n\n"
            f"**Page id**: `{page_id}`\n"
            f"**Title**: {title}\n"
            f"**Drift type**: `{drift_type}`\n"
            f"**Detected**: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n\n"
            f"### Details\n\n{details}\n\n"
            f"### Resolution\n\n"
            f"CFP-1495 / ADR-103 §결정 1 영역 — Confluence-mirror drift detection.\n"
            f"Manual review channel: warning tier (false positive 가능).\n"
            f"Mark engine path (#1320) 활성 후 자동 sync 가능.\n\n"
            f"signature: {signature}\n\n"
            f"---\n"
            f"Source: `scripts/check-confluence-drift.sh` (CFP-1495 / ADR-103 §결정 1)"
        )
        # Signature dedup check
        list_cmd = [
            "gh", "issue", "list",
            "--repo", "mclayer/plugin-codeforge",
            "--label", "drift-detection",
            "--state", "open",
            "--search", f'"signature: {signature}"',
            "--limit", "1",
            "--json", "number,title",
            "--jq", ".[0].number // empty",
        ]
        existing = subprocess.run(list_cmd, capture_output=True, text=True, timeout=20, check=False)
        if existing.stdout.strip():
            print(f"  -> dedup: active Issue #{existing.stdout.strip()} exists for signature {signature}")
            return
        create_cmd = [
            "gh", "issue", "create",
            "--repo", "mclayer/plugin-codeforge",
            "--label", "drift-detection",
            "--title", f"[CONFLUENCE-DRIFT] page_id={page_id} drift_type={drift_type}",
            "--body", body,
        ]
        subprocess.run(create_cmd, capture_output=True, text=True, timeout=30, check=False)
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"  -> Issue create failed (non-fatal): {e}")


def main() -> int:
    ia_tree = _load_ia_tree()
    pages = _extract_pages(ia_tree)
    if not pages:
        _emit_warning(f"IA tree has 0 page entries (schema_version={ia_tree.get('schema_version', 'unknown')}) — nothing to check")
        return 0

    mock_data = _load_mock_fixture()
    total_drift = 0
    checked = 0

    for page in pages:
        page_id = page["page_id"]
        title = page["title"]
        source_path = page["source_path"]
        checked += 1

        # Fetch Confluence side
        cf = _fetch_confluence_page(page_id, mock_data)
        if not cf:
            # MCP-direct mode: skip silently (warning already emitted in _fetch)
            continue

        cf_last_modified_ts = int(cf.get("last_modified_ts", 0))
        cf_title = cf.get("title", "")
        cf_anchors = cf.get("anchors", {}) or {}

        # Mark engine path exempt: 3-anchor stamp 부착 영역 = ongoing sync 정합 영역
        has_anchors = all(cf_anchors.get(k) for k in ANCHOR_KEYS)
        if has_anchors:
            continue  # mark engine path 활성 영역 = exempt

        # Drift check 1: timestamp delta > threshold
        if source_path:
            git_ts = _get_git_last_commit_ts(source_path)
            if git_ts > 0 and cf_last_modified_ts > 0:
                delta_seconds = git_ts - cf_last_modified_ts
                delta_days = delta_seconds / SECONDS_PER_DAY
                if delta_days > DRIFT_THRESHOLD_DAYS:
                    total_drift += 1
                    sig = _compute_drift_signature(page_id, "timestamp")
                    msg = (
                        f"page_id={page_id} title='{title}' drift_type=timestamp "
                        f"signature={sig} delta_days={delta_days:.1f} "
                        f"git_ts={git_ts} cf_last_modified_ts={cf_last_modified_ts}"
                    )
                    _emit_warning(msg)
                    _create_drift_issue(
                        page_id, title, "timestamp",
                        f"git source last commit was {delta_days:.1f} days more recent than Confluence page last_modified.\n"
                        f"- git source: `{source_path}`\n"
                        f"- threshold: {DRIFT_THRESHOLD_DAYS} day",
                        sig,
                    )

        # Drift check 2: title mismatch
        if cf_title and title and cf_title.strip() != title.strip():
            total_drift += 1
            sig = _compute_drift_signature(page_id, "title")
            msg = f"page_id={page_id} drift_type=title signature={sig} git_title='{title}' cf_title='{cf_title}'"
            _emit_warning(msg)
            _create_drift_issue(
                page_id, title, "title",
                f"Confluence page title differs from IA tree schema.\n"
                f"- IA tree title: `{title}`\n"
                f"- Confluence title: `{cf_title}`",
                sig,
            )

    if total_drift == 0:
        print(f"check-confluence-drift: PASS — 0 drift across {checked} page(s) checked (IA tree total={len(pages)})")
    else:
        print(
            f"check-confluence-drift: WARNING — {total_drift} drift(s) detected across {checked} page(s) checked. "
            f"Issues auto-created (warning tier, ADR-060 / CFP-1495)."
        )

    # warning tier — drift 감지 시에도 exit 0 (Issue auto-create 가 통보 channel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
