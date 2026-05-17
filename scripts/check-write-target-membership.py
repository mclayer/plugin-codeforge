#!/usr/bin/env python3
# CFP-843 Phase 2 — write-target-path worktree-membership lint (canonical Python logic)
# ADR-040 Amendment 6 §결정 7.J.2 — scope CWD → write-target-path 확장
# ADR-061 정합: 5+ 줄 multi-line 로직 = 외부 .py 파일 의무
#
# 알고리즘 (Change Plan §3.2):
#   1. WRITE_TARGET_PATHS env (newline-delimited) 로부터 target path list 추출
#   2. ENFORCE_FROM env 비교 — "future" timestamp 면 skip (false-positive 회피, 5-layer layer 3)
#   3. 각 target path → EXPECTED_WORKTREE_ROOT 와 prefix 비교
#      - common-dir (.git/common 포함) → skip (5-layer layer 5)
#      - worktree root prefix 충족 → PASS
#      - 그 외 → violation WARN
#   4. BYPASS_WORKTREE_FIRST=1 → 즉시 exit 0 (5-layer layer 4)
#   5. exit 0 (warning tier — blocking 없음)
#
# 환경 변수:
#   WRITE_TARGET_PATHS — 검사할 write target 경로 (newline-delimited)
#   EXPECTED_WORKTREE_ROOT — 기대되는 worktree root prefix
#   ENFORCE_FROM — ISO8601 timestamp 기준 (이 시각 이후만 enforce)
#   BYPASS_WORKTREE_FIRST — 1 = short-circuit (5-layer layer 4)
#
# Exit code:
#   0 — always (warning tier, non-blocking — ADR-040 Amendment 6 §결정 7.J.2)
#
# Cross-platform MSYS path drift 처리:
#   Windows "C:\" ↔ POSIX "/c/" 변환 지원 (Story §6 hypothesis)

import os
import sys
from datetime import datetime, timezone


def normalize_path(p: str) -> str:
    """MSYS/POSIX path 정규화: C-drive to /c/ prefix, backslash to slash."""
    if not p:
        return p
    # Windows 드라이브 문자 변환: C:/ → /c/ (MSYS Git Bash 정합)
    if len(p) >= 3 and p[1] == ':' and p[2] in ('/', '\\'):
        drive = p[0].lower()
        rest = p[3:].replace('\\', '/')
        return f'/{drive}/{rest}'
    # 백슬래시 → 슬래시
    return p.replace('\\', '/')


def is_common_dir_path(path: str) -> bool:
    """common-dir ambiguity 경로 여부 (5-layer layer 5)."""
    norm = normalize_path(path)
    # .git/common 또는 .git/ 내부 메타 경로
    if '/.git/' in norm or norm.endswith('/.git'):
        return True
    return False


def path_is_within_root(target: str, root: str) -> bool:
    """target 이 root 의 하위 경로인지 확인 (MSYS 정규화 포함)."""
    norm_target = normalize_path(target)
    norm_root = normalize_path(root)
    # trailing slash 정규화
    if not norm_root.endswith('/'):
        norm_root += '/'
    return norm_target.startswith(norm_root) or normalize_path(target) == normalize_path(root)


def parse_iso8601(ts: str):
    """ISO8601 timestamp → datetime (UTC, tz-aware). 파싱 실패 시 None."""
    try:
        # Python 3.7+ fromisoformat (Z suffix 처리)
        ts_clean = ts.replace('Z', '+00:00')
        dt = datetime.fromisoformat(ts_clean)
        if dt.tzinfo is None:
            # offset-naive → UTC 가정 (line-91 aware 비교 TypeError 회피, FIX-1)
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def main():
    prefix = '[write-target-membership]'

    # 5-layer layer 4: BYPASS_WORKTREE_FIRST=1 short-circuit
    if os.environ.get('BYPASS_WORKTREE_FIRST', '') == '1':
        print(f'{prefix} BYPASS_WORKTREE_FIRST=1 — skip', file=sys.stderr)
        sys.exit(0)

    # ENFORCE_FROM 기준 — 미래이면 skip (5-layer layer 3: enforce-from filter)
    enforce_from_str = os.environ.get('ENFORCE_FROM', '')
    if enforce_from_str:
        enforce_from = parse_iso8601(enforce_from_str)
        if enforce_from is None:
            print(f'{prefix} WARN: ENFORCE_FROM parse 실패: {enforce_from_str} — skip', file=sys.stderr)
            sys.exit(0)
        now = datetime.now(tz=timezone.utc)
        if enforce_from > now:
            print(f'{prefix} ENFORCE_FROM {enforce_from_str} is in the future — skip (false-positive 0)', file=sys.stderr)
            sys.exit(0)

    # WRITE_TARGET_PATHS: newline-delimited 경로 목록
    targets_raw = os.environ.get('WRITE_TARGET_PATHS', '')
    if not targets_raw.strip():
        print(f'{prefix} WRITE_TARGET_PATHS 미설정 — skip', file=sys.stderr)
        sys.exit(0)

    # EXPECTED_WORKTREE_ROOT: 기대 worktree root
    expected_root = os.environ.get('EXPECTED_WORKTREE_ROOT', '')
    if not expected_root.strip():
        print(f'{prefix} EXPECTED_WORKTREE_ROOT 미설정 — skip', file=sys.stderr)
        sys.exit(0)

    targets = [t.strip() for t in targets_raw.splitlines() if t.strip()]
    warn_count = 0

    for target in targets:
        # 5-layer layer 5: common-dir skip
        if is_common_dir_path(target):
            print(f'{prefix} common-dir path skip: {target}', file=sys.stderr)
            continue

        # 5-layer layer 1: worktree-internal work PASS
        if path_is_within_root(target, expected_root):
            # PASS
            continue
        else:
            # worktree-membership FAIL → WARN (violation)
            print(
                f'{prefix} WARN: write-target worktree-membership violation — '
                f'target={target!r} is NOT within expected_root={expected_root!r}',
                file=sys.stderr
            )
            warn_count += 1

    if warn_count > 0:
        print(f'{prefix} WARN total: {warn_count} violation(s) detected', file=sys.stderr)
    else:
        print(f'{prefix} PASS: all {len(targets)} target(s) within worktree root', file=sys.stderr)

    # warning tier — exit 0 always
    sys.exit(0)


if __name__ == '__main__':
    main()
