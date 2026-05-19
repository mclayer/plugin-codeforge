#!/usr/bin/env python3
# scripts/lib/extract_4tuple_measurement_source.py
# CFP-991 Phase 2 — 4-tuple measurement_source 추출 helper (ADR-061 §결정 1 external py file)
#
# Usage: python3 extract_4tuple_measurement_source.py <yaml_path> <sub_field>
#   yaml_path  = reconcile-protocol-v1.md 절대경로 (POSIX /c/... 또는 Windows C:\... 양형 지원)
#   sub_field  = functional | security | monitoring | testing
#
# Exit codes:
#   0 = PASS (measurement_source 추출 성공)
#   1 = WARNING (field 부재 — additive only invariant)
#   2 = ERROR (yaml 파싱 실패 / 파일 부재 / invalid sub_field)

import sys
import re
import os

# Windows CP949 환경에서 Unicode 출력 강제 (ADR-061 §결정 3 Windows 호환)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def posix_to_windows(path: str) -> str:
    """Git Bash POSIX 경로 → Windows 경로 변환 (예: /c/Users/... → C:/Users/...)"""
    if path.startswith('/') and len(path) >= 3 and path[2] == '/':
        drive = path[1].upper()
        return drive + ':' + path[2:]
    return path


def extract_measurement_source(yaml_path: str, sub_field: str) -> int:
    """4-tuple measurement_source 추출 (reconcile-protocol-v1.md §4.14)"""
    # Windows 경로 변환
    yaml_path = posix_to_windows(yaml_path)

    if not os.path.exists(yaml_path):
        print(f'[canary-compat] ERROR: yaml_path not found: {yaml_path}', file=sys.stderr)
        return 2

    # sub_field enum 검증
    valid_sub_fields = ('functional', 'security', 'monitoring', 'testing')
    if sub_field not in valid_sub_fields:
        print(
            f'[canary-compat] ERROR: invalid sub-field \'{sub_field}\''
            f' — expected one of: {" / ".join(valid_sub_fields)}',
            file=sys.stderr
        )
        return 2

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        print(f'[canary-compat] ERROR: cannot read yaml_path: {e}', file=sys.stderr)
        return 2

    # canary_compatibility_check_binding 블록 위치 (§4.14)
    block_match = re.search(
        r'canary_compatibility_check_binding:.*?(?=^[a-z_]+:|\Z)',
        content,
        re.MULTILINE | re.DOTALL
    )
    if not block_match:
        print('[canary-compat] WARNING: canary_compatibility_check_binding block not found', file=sys.stderr)
        return 1

    block = block_match.group(0)

    # promotion_criteria_4tuple sub-block 위치
    sub_block_match = re.search(
        r'promotion_criteria_4tuple:.*?(?=^  [a-z_]+:|\Z)',
        block,
        re.MULTILINE | re.DOTALL
    )
    if not sub_block_match:
        print('[canary-compat] WARNING: promotion_criteria_4tuple block not found', file=sys.stderr)
        return 1

    sub_block = sub_block_match.group(0)

    # sub_field 블록 추출 (6-space indent 기준)
    field_pattern = rf'^      {re.escape(sub_field)}:\s*\n(.*?)(?=^      [a-z_]+:|\Z)'
    field_match = re.search(field_pattern, sub_block, re.MULTILINE | re.DOTALL)
    if not field_match:
        print(f'[canary-compat] WARNING: sub_field \'{sub_field}\' not found in promotion_criteria_4tuple', file=sys.stderr)
        return 1

    field_content = field_match.group(1)

    # measurement_source 추출 (double-quote 형식)
    ms_match = re.search(r'measurement_source:\s*"([^"]+)"', field_content)
    if not ms_match:
        print(f'[canary-compat] WARNING: measurement_source not found for sub_field \'{sub_field}\'', file=sys.stderr)
        return 1

    print(ms_match.group(1))
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <yaml_path> <sub_field>', file=sys.stderr)
        sys.exit(2)

    _yaml_path = sys.argv[1]
    _sub_field = sys.argv[2]
    sys.exit(extract_measurement_source(_yaml_path, _sub_field))
