#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# dedup_section14_spawn_event.py — §14 Lane Evidence ↔ spawn-event 정합 reconciliation
#
# Carrier: CFP-2393 Phase 2 (구현) / Epic CFP-2391 S3
# 출처: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
#       — per-agent registry 차용 (본 reconciliation 은 codeforge 측 §14↔spawn-event boundary
#       검증으로, OMC 차용은 spawn-event row 모델 한정). enforcement 비-차용.
#
# 책임 (ADR-042 §결정 13 precondition AC):
#   - §14 Lane Evidence(lane-coarse) row 의 lane set ↔ spawn-event ledger(per-agent fine)
#     의 lane_label set 정합 검증. §14 = lane 단위, spawn-event = agent 단위 (1 lane N agent).
#   - 정합 규칙: spawn-event 에 존재하는 lane_label 이 §14 에도 표현됐는지 (모순 없음).
#   - parent_event_id chain dedup 으로 nested spawn 이중계산 방지.
#   - read-time dedup: deterministic event_id 중복 제거 (JSONL append-only, DB UNIQUE 부재 OK).
#   - read-time/aggregate 위치 (append-time 아님 — cross-channel coupling + 50ms 위반 회피).
#
# 불변식:
#   - 0 API call, local read only.
#   - exit 0 = 정합 / exit 1 = mismatch (warning, advisory) / exit 2 = setup error.
#
# 사용:
#   python3 dedup_section14_spawn_event.py check \
#     [--story-path <path>] [--ledger-path <path>] [--repo-root <path>]
#
# Prior art: check_deferred_followup_reconcile.py (registry 파싱 + 3-tier exit + UTF-8 reconfigure)
#            check-lane-evidence.sh (§14 YAML block 파싱 — ## (§)?14 heading + ```yaml block)

import argparse
import json
import os
import re
import sys

# Windows cp949 인코딩 회피 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


_LEDGER_BASENAME = "spawn-event.jsonl"
_DEFAULT_LEDGER_PARENT_REL = os.path.join(".claude", "ledger")

# spawn-event-v1 lane_label closed enum (append_spawn_event 와 동일 SSOT)
_LANE_LABELS = {
    "요구사항", "요구사항-리뷰", "설계", "설계-리뷰", "구현", "구현-리뷰",
    "구현-테스트", "보안-테스트", "배포", "배포-리뷰", "없음",
}


# ─────────────────────── §14 Lane Evidence 파싱 ──────────────────────────────

def _extract_section14_yaml_block(story_text):
    """Story §14 Lane Evidence 의 ```yaml block 텍스트 추출.

    check-lane-evidence.sh parse_story_section_14 와 동일 규칙:
      heading `## (§)?14` ~ 다음 `## (§)?[0-9]` 사이의 ```yaml ... ``` block.

    Returns yaml block 문자열 (없으면 "").
    """
    lines = story_text.splitlines()
    in14 = False
    in_yaml = False
    collected = []
    head_re = re.compile(r"^#{2,4}\s*(§)?14\b")
    next_sec_re = re.compile(r"^#{2,4}\s*(§)?[0-9]")
    for line in lines:
        if not in14:
            if head_re.match(line):
                in14 = True
            continue
        # in14 — 다음 섹션 heading 만나면 종료 (단 14 자신 재매칭 제외)
        if next_sec_re.match(line) and not head_re.match(line):
            break
        if not in_yaml:
            if line.strip().startswith("```yaml"):
                in_yaml = True
            continue
        # in_yaml
        if line.strip().startswith("```"):
            in_yaml = False
            continue
        collected.append(line)
    return "\n".join(collected)


def _extract_section14_lanes(story_path):
    """Story §14 의 lane name set 추출.

    YAML block 우선 파싱 (yaml.safe_load). 실패 시 정규식 fallback (`- lane: <name>`).

    Returns (lane_set, error_str | None).
    """
    if not story_path or not os.path.isfile(story_path):
        return set(), "story file 부재: %s" % story_path
    try:
        with open(story_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        return set(), "story file read 실패: %s" % e

    block = _extract_section14_yaml_block(text)
    if not block.strip():
        return set(), "§14 Lane Evidence YAML block 부재"

    lanes = set()

    # 1차: yaml.safe_load 시도
    if yaml is not None:
        try:
            data = yaml.safe_load(block)
            lanes |= _collect_lane_values(data)
        except yaml.YAMLError:
            pass

    # 2차 fallback: 정규식 `lane: <name>` (yaml 파싱 실패/부분 보완)
    for m in re.finditer(r"(?m)^\s*-?\s*lane:\s*([^\s#]+)", block):
        lanes.add(m.group(1).strip())

    return lanes, None


def _collect_lane_values(data):
    """yaml 파싱 결과에서 lane: 값 전부 수집 (중첩 list/dict 재귀)."""
    found = set()
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "lane" and isinstance(v, str):
                found.add(v.strip())
            else:
                found |= _collect_lane_values(v)
    elif isinstance(data, list):
        for item in data:
            found |= _collect_lane_values(item)
    return found


# ─────────────────────── spawn-event ledger 파싱 + dedup ─────────────────────

def _resolve_ledger_path(ledger_path_arg, repo_root):
    if ledger_path_arg:
        return ledger_path_arg
    base = repo_root or os.environ.get("CLAUDE_PROJECT_DIR", "") or "."
    return os.path.join(base, _DEFAULT_LEDGER_PARENT_REL, _LEDGER_BASENAME)


def _read_ledger_rows(ledger_path):
    """JSONL ledger read → list[dict]. 부재 → [] (graceful)."""
    rows = []
    if not os.path.isfile(ledger_path):
        return rows
    try:
        with open(ledger_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    rows.append(obj)
    except OSError:
        return rows
    return rows


def _dedup_rows(rows):
    """read-time dedup — deterministic event_id 중복 제거 (first-wins).

    + parent_event_id chain nested dedup: nested spawn(parent_event_id != null)은
    이중계산 방지 위해 lane 정합 검증에선 root/nested 모두 lane set 에 기여하되
    event_id 중복만 제거 (행 개수 dedup). nested 이중계산 = 동일 event_id 재append.
    """
    seen = set()
    deduped = []
    for row in rows:
        eid = row.get("event_id")
        if eid is not None:
            if eid in seen:
                continue
            seen.add(eid)
        deduped.append(row)
    return deduped


def _extract_ledger_lanes(rows, story_key_filter):
    """ledger row 에서 lane_label set 추출 (story_key filter 적용).

    Returns (lane_set, row_count_after_dedup).
    """
    if story_key_filter:
        rows = [r for r in rows if r.get("story_key") == story_key_filter]
    lanes = set()
    for row in rows:
        ll = row.get("lane_label")
        if isinstance(ll, str) and ll.strip():
            lanes.add(ll.strip())
    return lanes, len(rows)


def _infer_story_key(story_path):
    """story file path 에서 KEY 추론 (e.g. docs/stories/CFP-2393.md → CFP-2393)."""
    if not story_path:
        return None
    base = os.path.basename(story_path)
    m = re.match(r"([A-Za-z]+-[0-9]+)", base)
    return m.group(1) if m else None


# ─────────────────────── 정합 검증 ───────────────────────────────────────────

def reconcile(story_path, ledger_path, repo_root):
    """§14 lane set ↔ spawn-event lane_label set 정합 검증.

    정합 규칙: spawn-event ledger 에 존재하는 lane_label 이 §14 에도 표현됐는지.
      - mismatch = ledger 에 있는 lane 이 §14 에 없음 (spawn 됐는데 evidence 미기록).
      - §14 에만 있고 ledger 에 없는 lane = mismatch 아님 (telemetry opt-in off 가능 — 정상).

    Returns dict {status, section14_lanes, ledger_lanes, missing_in_section14,
                  ledger_row_count, error}.
    """
    section14_lanes, s14_err = _extract_section14_lanes(story_path)
    if s14_err is not None:
        return {"status": "setup_error", "error": s14_err}

    story_key = _infer_story_key(story_path)
    rows = _read_ledger_rows(ledger_path)
    rows = _dedup_rows(rows)
    ledger_lanes, row_count = _extract_ledger_lanes(rows, story_key)

    # spawn-event 에 있는 lane 중 §14 에 없는 것 = mismatch
    # ('없음' fallback 은 §14 lane 단위 표현 대상 아님 — 정합 비교에서 제외)
    comparable = {l for l in ledger_lanes if l != "없음"}
    missing_in_section14 = sorted(comparable - section14_lanes)

    status = "mismatch" if missing_in_section14 else "consistent"
    return {
        "status": status,
        "section14_lanes": sorted(section14_lanes),
        "ledger_lanes": sorted(ledger_lanes),
        "missing_in_section14": missing_in_section14,
        "ledger_row_count": row_count,
        "error": None,
    }


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    story_path = args.story_path
    ledger_path = _resolve_ledger_path(args.ledger_path, repo_root)

    result = reconcile(story_path, ledger_path, repo_root)

    if result["status"] == "setup_error":
        print(
            "[codeforge-spawn-event-dedup-setup-error] §14↔spawn-event reconcile: %s"
            % result["error"],
            file=sys.stderr,
        )
        sys.exit(2)

    if result["status"] == "mismatch":
        print(
            "::warning::dedup-section14-spawn-event: MISMATCH — "
            "spawn-event lane 이 §14 Lane Evidence 에 미표현: [%s]"
            % ", ".join(result["missing_in_section14"])
        )
        print(
            "  §14 lanes=[%s] / ledger lanes=[%s] / ledger rows=%d (dedup 후)"
            % (
                ", ".join(result["section14_lanes"]),
                ", ".join(result["ledger_lanes"]),
                result["ledger_row_count"],
            )
        )
        print(
            "  advisory (ADR-042 §결정 13 AC — warning tier, 비차단). "
            "§14 에 누락 lane evidence 추가 또는 spawn-event lane_label 정정 검토."
        )
        sys.exit(1)

    print(
        "dedup-section14-spawn-event: CONSISTENT — "
        "§14 lanes=[%s] / ledger lanes=[%s] / ledger rows=%d (dedup 후)"
        % (
            ", ".join(result["section14_lanes"]),
            ", ".join(result["ledger_lanes"]),
            result["ledger_row_count"],
        )
    )
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="§14 Lane Evidence ↔ spawn-event 정합 reconcile (CFP-2393 / ADR-042 §결정 13)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="§14 ↔ spawn-event lane 정합 검증")
    check_p.add_argument("--story-path", default="",
                         help="Story file 경로 (§14 Lane Evidence 원천)")
    check_p.add_argument("--ledger-path", default="",
                         help="spawn-event.jsonl 경로 (default: <repo-root>/.claude/ledger/...)")
    check_p.add_argument("--repo-root", default=".",
                         help="repo root (default 현재 디렉터리)")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
