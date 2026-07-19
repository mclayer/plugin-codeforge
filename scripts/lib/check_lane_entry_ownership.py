#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_lane_entry_ownership.py
CFP-2761 §5.2 / ADR-085 §결정3 + ADR-073 Amendment 2 (4th source) — lane-entry ownership verify.
HOOK-ONLY (workflow:null) — CI 워크플로 게이트 아님, hook 경유 advisory 검증 (warning tier).

lane 진입 시 4-step 소유 polling (ADR-085 §결정3 + ADR-073 Amendment 2 4th source). 진입 세션이
active_sessions 기록에 소유 entry(matching entry_phase) 를 갖는지, 동일 lane 에 경합하는 별개
동시 소유자가 없는지를 검증한다.

검사:
  --sessions-file = active_sessions entry list (JSON 또는 YAML). 각 entry: git_identity,
    worktree_path, entry_phase.
  진입 세션 = (--git-identity, --lane).
    - 소유 기록 부재(matching entry_phase==lane & git_identity==id 없음) → warn
      (re-adjudication candidate).
    - 동일 lane 에 별개 concurrent 소유자(entry_phase==lane & git_identity!=id) → warn
      (coordination check).
  --sessions-file 부재 = live advisory no-op (exit 0 + 명시 non-silent line).

DoS guard (§8.6, ADR-082 Amendment 38 resource-safety): sessions-file bounded read (byte cap),
  구조 파싱만 (재귀 없음), O(n) entry iterate. bounded degradation — 임의 입력 무해 아님.

CLI 계약 (ADR-061 house style — 고정, hook + self-test 소비):
  bash scripts/check-lane-entry-ownership.sh [--repo-root DIR] --lane NAME --git-identity ID
       [--sessions-file FILE]

Exit codes (ADR-060 §결정5 tri-tier — warning tier, advisory NEVER blocks):
  0 = clean (owner 정합) OR warning finding 방출 OR live advisory no-op.
      finding 은 STDOUT 에 `::warning::lane-entry-ownership-verify: <detail>` 로 surface.
  2 = usage/argparse 오류 (--lane/--git-identity 누락) OR sessions-file unparseable (TC-UNKNOWN).
  3 = 미사용.
  1 = strict-tier 미사용 (warning tier).

ADR refs: CFP-2761 §5.2 (carrier) / ADR-085 §결정3 (lane-entry ownership) / ADR-073 Amendment 2
  (polling 4th source) / ADR-060 §결정5 (warning tri-tier) / ADR-082 Amendment 38 §8.6
  (resource-safety) / ADR-061 §결정1 (Python SSOT + thin wrapper).
"""

import argparse
import json
import os
import sys

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제 (ADR-061 portability 답습).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

CHECK_NAME = "lane-entry-ownership-verify"

MAX_READ_BYTES = 4 * 1024 * 1024  # sessions-file 상한 4MB (§8.6 bounded read).


def _load_sessions(path):
    """sessions-file 을 entry list 로 로드. JSON 우선, 실패 시 YAML. 파싱 불가 → 'PARSE_ERROR'.

    top-level list, 또는 {active_sessions: [...]} dict 지원.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read(MAX_READ_BYTES)
    except OSError:
        return "PARSE_ERROR"

    data = None
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        try:
            import yaml
        except ImportError:
            return "PARSE_ERROR"
        try:
            data = yaml.safe_load(raw)
        except Exception:
            return "PARSE_ERROR"

    if isinstance(data, dict):
        data = data.get("active_sessions", [])
    if not isinstance(data, list):
        return "PARSE_ERROR"
    # entry 는 dict 만 (비-dict 는 무시 — 방어).
    return [e for e in data if isinstance(e, dict)]


def _evaluate(entries, lane, git_identity):
    """소유 판정 → findings=[detail]."""
    findings = []
    lane_entries = [e for e in entries if e.get("entry_phase") == lane]
    own = [e for e in lane_entries if e.get("git_identity") == git_identity]
    others = sorted(
        {str(e.get("git_identity")) for e in lane_entries if e.get("git_identity") != git_identity}
    )

    if others:
        for other in others:
            findings.append(
                "lane=%s concurrent distinct owner %s — coordination check" % (lane, other)
            )
    if not own:
        findings.append(
            "lane=%s identity=%s no recorded active_sessions ownership (re-adjudication candidate)"
            % (lane, git_identity)
        )
    return findings


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_lane_entry_ownership.py",
        description="lane-entry ownership verify (HOOK-ONLY, warning tier).",
    )
    parser.add_argument("--repo-root", default=None, help="루트 (advisory, live no-op 경로용).")
    parser.add_argument("--lane", required=True, help="진입 lane 이름.")
    parser.add_argument("--git-identity", required=True, help="진입 세션 git identity.")
    parser.add_argument("--sessions-file", default=None, help="active_sessions entry list (JSON/YAML).")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    if args.sessions_file is None:
        # fixture 부재 = live advisory no-op (silent-green 금지 — 명시 line).
        print(
            "%s: lane=%s identity=%s — sessions fixture 부재, live advisory no-op (honest no-op)"
            % (CHECK_NAME, args.lane, args.git_identity)
        )
        return 0

    entries = _load_sessions(args.sessions_file)
    if entries == "PARSE_ERROR":
        print(
            "::error::%s: sessions-file 파싱 불가(JSON/YAML): %s (TC-UNKNOWN fail-closed)"
            % (CHECK_NAME, args.sessions_file),
            file=sys.stderr,
        )
        return 2

    findings = _evaluate(entries, args.lane, args.git_identity)
    if findings:
        for detail in findings:
            print("::warning::%s: %s" % (CHECK_NAME, detail))
        return 0

    print(
        "%s: lane=%s identity=%s — ownership 정합 (concurrent 경합 0, advisory)"
        % (CHECK_NAME, args.lane, args.git_identity)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
