#!/usr/bin/env python3
# tests/scripts/cfp-1225/test_dispatcher_derive.py
# CFP-1225 — dispatcher derive test helper (ADR-061 외부 .py 의무)
#
# bats 에서 python3 path 정규화 문제 해소:
#   Git Bash /c/... 경로 → Windows C:/... 경로 자동 변환 (subprocess os.path 호환)
#
# 사용법:
#   python3 tests/scripts/cfp-1225/test_dispatcher_derive.py <walk_plan_dir> <test_case>
#
# test_case:
#   prereq_importable              — walk_plan import + 필수 심볼 확인
#   tc_topological_order           — get_topological_order() 반환값 출력 (개행 구분)
#   tc_topological_count           — len(get_topological_order()) 출력
#   tc_first_plugin                — get_topological_order()[0] 출력
#   tc_contains_deploy             — codeforge-deploy 포함 확인
#   tc_contains_deploy_review      — codeforge-deploy-review 포함 확인

import sys
import os


def _resolve_walk_plan_dir(raw_dir: str) -> str:
    """Git Bash /c/... 경로를 os.path 가 인식하는 경로로 변환.

    Windows 환경에서 Git Bash 가 반환하는 /c/workspace/... 형태를
    Python os.path.exists 가 인식하는 C:/workspace/... 형태로 변환.
    Unix/Linux 환경에서는 변환 불필요 (os.path.exists 직접 통과).
    """
    # 이미 존재하면 변환 불필요
    if os.path.isdir(raw_dir):
        return raw_dir

    # /c/... → C:/... 변환 시도 (Windows Git Bash POSIX path)
    if raw_dir.startswith('/') and len(raw_dir) >= 3 and raw_dir[2] == '/':
        drive_letter = raw_dir[1].upper()
        windows_path = drive_letter + ':' + raw_dir[2:]
        if os.path.isdir(windows_path):
            return windows_path

    # cygpath -w fallback (cygpath 가용 시)
    try:
        import subprocess
        result = subprocess.run(
            ['cygpath', '-w', raw_dir],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            converted = result.stdout.strip()
            if os.path.isdir(converted):
                return converted
    except (FileNotFoundError, Exception):
        pass

    # 변환 실패 — 원본 반환 (호출자가 에러 처리)
    return raw_dir


def main():
    if len(sys.argv) < 3:
        print(f"사용법: {sys.argv[0]} <walk_plan_dir> <test_case>", file=sys.stderr)
        sys.exit(1)

    raw_dir = sys.argv[1]
    test_case = sys.argv[2]

    walk_plan_dir = _resolve_walk_plan_dir(raw_dir)

    if not os.path.isdir(walk_plan_dir):
        print(f"오류: walk_plan 디렉터리 없음: {raw_dir!r} (변환 후: {walk_plan_dir!r})", file=sys.stderr)
        sys.exit(1)

    # walk_plan 모듈 import
    if walk_plan_dir not in sys.path:
        sys.path.insert(0, walk_plan_dir)

    try:
        import walk_plan
    except ImportError as e:
        print(f"오류: walk_plan import 실패: {e}", file=sys.stderr)
        sys.exit(1)

    if test_case == "prereq_importable":
        # 필수 심볼 확인
        required_symbols = [
            "TOPOLOGICAL_ORDER",
            "get_topological_order",
            "LANE_PLUGINS",
            "WRAPPER_PLUGIN",
        ]
        missing = [s for s in required_symbols if not hasattr(walk_plan, s)]
        if missing:
            print(f"오류: walk_plan 필수 심볼 없음: {missing}", file=sys.stderr)
            sys.exit(1)
        print("ok: 필수 심볼 모두 존재")
        sys.exit(0)

    elif test_case == "tc_topological_order":
        # get_topological_order() 반환값 출력 (bats 비교용)
        order = walk_plan.get_topological_order()
        print('\n'.join(order))
        sys.exit(0)

    elif test_case == "tc_topological_count":
        count = len(walk_plan.get_topological_order())
        print(count)
        sys.exit(0)

    elif test_case == "tc_first_plugin":
        first = walk_plan.get_topological_order()[0]
        print(first)
        sys.exit(0)

    elif test_case == "tc_contains_deploy":
        order = walk_plan.get_topological_order()
        if "codeforge-deploy" not in order:
            print("오류: codeforge-deploy TOPOLOGICAL_ORDER 에 없음", file=sys.stderr)
            sys.exit(1)
        print("ok: codeforge-deploy 포함")
        sys.exit(0)

    elif test_case == "tc_contains_deploy_review":
        order = walk_plan.get_topological_order()
        if "codeforge-deploy-review" not in order:
            print("오류: codeforge-deploy-review TOPOLOGICAL_ORDER 에 없음", file=sys.stderr)
            sys.exit(1)
        print("ok: codeforge-deploy-review 포함")
        sys.exit(0)

    else:
        print(f"오류: 알 수 없는 test_case: {test_case!r}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
