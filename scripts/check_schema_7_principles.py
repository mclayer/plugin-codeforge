#!/usr/bin/env python3
"""
scripts/check_schema_7_principles.py
CFP-1059-S6 §3.3 — ADR-089 7 원칙 self-check + ADR-068 I-5 dimensional grounding (ADR-061 외부 .py)

7 원칙 (ADR-089 §결정 1):
  1. backward-compatible 우선 (additive 우선, drop 후속)
  2. 단방향 변경 (한 PR 안 add+drop 동시 금지)
  3. compatibility window 유지 (bidirectional-smoke 분담)
  4. fail-loud (silent fallback / safe-default 차단)
  5. rollback path 명시
  6. empirical evidence annotation (ADR-068 I-5 dimensional grounding)
  7. hard limit 명시 (column 100+ / row 1억+ / lock 5분+ / depth 7+)

ADR-068 I-5 dimensional grounding:
  10 dimension enum: latency / scale / cardinality / throughput / cost /
                     accuracy / lifecycle / volume / rate / count
  [empirical-source: <ref>] annotation 의무 (design-time binding)
"""

import argparse
import os
import re
import sys
from pathlib import Path


# hard limit 기준 (ADR-089 §결정 1 원칙 7)
# [empirical-source: ADR-089 §결정 1 원칙 7 — 사용자 정의 hard limit]
HARD_LIMIT_PATTERNS = [
    # column count (dimension: count)
    r"column.{0,20}(?:100\+|>=\s*100|over\s*100|백\s*개)",
    # row count (dimension: scale)
    r"row.{0,20}(?:1억\+|>=\s*1억|100,?000,?000|1e8)",
    # lock duration (dimension: latency)
    r"lock.{0,20}(?:5분\+|>=\s*5\s*min|300\s*s)",
    # depth (dimension: count)
    r"depth.{0,20}(?:7\+|>=\s*7|depth\s*7)",
]

# empirical-source annotation 패턴 (ADR-068 I-5)
EMPIRICAL_ANNOTATION_PATTERN = r"\[empirical-source:"

# rollback path 패턴 (원칙 5)
ROLLBACK_PATTERN = r"rollback|downgrade|revert"

# fail-loud 패턴 (원칙 4)
FAIL_LOUD_PATTERN = r"fail.loud|fail_loud|exit\s+[1-9]|raise\s+\w+Error"

# add+drop 동시 패턴 (원칙 2 위반 감지)
ADD_PATTERN = r"op_add|add_column|AddColumn|add column"
DROP_PATTERN = r"op_drop|drop_column|DropColumn|drop column"


def check_migration_file(file_path: Path, violations: list) -> None:
    """migration 파일 7 원칙 self-check"""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    filename = file_path.name

    print(f"  검사: {file_path}")

    # 원칙 2: 단방향 변경 (add+drop 동시 금지)
    has_add = bool(re.search(ADD_PATTERN, content, re.IGNORECASE))
    has_drop = bool(re.search(DROP_PATTERN, content, re.IGNORECASE))
    if has_add and has_drop:
        msg = f"원칙 2 위반: {filename} — add+drop 동시 (단방향 변경 원칙 위반)"
        print(f"  [WARN] {msg}")
        violations.append(msg)

    # 원칙 4: fail-loud 패턴 확인 (Python/SQL migration)
    if not re.search(FAIL_LOUD_PATTERN, content, re.IGNORECASE):
        print(f"  [INFO] {filename}: fail-loud 패턴 미발견 (원칙 4 권고)")

    # 원칙 6: empirical-source annotation 확인 (ADR-068 I-5)
    if not re.search(EMPIRICAL_ANNOTATION_PATTERN, content):
        print(f"  [INFO] {filename}: [empirical-source:] annotation 미발견 (ADR-068 I-5 권고)")

    # 원칙 7: hard limit 패턴 확인
    for pattern in HARD_LIMIT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            if not re.search(EMPIRICAL_ANNOTATION_PATTERN, content):
                msg = f"원칙 7: {filename} — hard limit 감지, empirical-source annotation 필요 (I-5)"
                print(f"  [WARN] {msg}")
                violations.append(msg)
            break


def check_change_plan_file(file_path: Path, violations: list) -> None:
    """change-plan 파일 7 원칙 self-check (§11 데이터 마이그레이션)"""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    filename = file_path.name

    print(f"  검사: {file_path}")

    # 원칙 5: rollback path 명시 확인
    if "§11" in content or "migration" in content.lower():
        if not re.search(ROLLBACK_PATTERN, content, re.IGNORECASE):
            msg = f"원칙 5 권고: {filename} — rollback path 미명시 (§11 migration 영역)"
            print(f"  [INFO] {msg}")

    # 원칙 6: empirical-source annotation 확인
    has_empirical = re.search(EMPIRICAL_ANNOTATION_PATTERN, content)
    if has_empirical:
        print(f"  [OK] {filename}: [empirical-source:] annotation 발견 (ADR-068 I-5)")
    else:
        print(f"  [INFO] {filename}: [empirical-source:] annotation 미발견 (ADR-068 I-5 권고)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ADR-089 7 원칙 self-check + ADR-068 I-5 dimensional grounding"
    )
    parser.add_argument("--path", default=".", help="검사 대상 루트 경로")
    parser.add_argument("--strict", action="store_true", help="위반 시 exit 1 (strict mode)")
    args = parser.parse_args()

    root = Path(args.path)
    violations: list = []

    print("=== ADR-089 7 원칙 self-check ===")
    print(f"경로: {root.absolute()}")
    print()

    # migration 파일 검사
    migration_dirs = ["migrations", "schema"]
    for d in migration_dirs:
        mdir = root / d
        if mdir.is_dir():
            print(f"[INFO] {d}/ 디렉토리 검사")
            for f in sorted(mdir.glob("**/*.py")) + sorted(mdir.glob("**/*.sql")):
                check_migration_file(f, violations)
        else:
            print(f"[INFO] {d}/ 없음 — 스킵")

    # change-plan 파일 검사 (§11 데이터 마이그레이션)
    change_plan_dir = root / "docs" / "change-plans"
    if change_plan_dir.is_dir():
        print(f"[INFO] docs/change-plans/ 검사 (§11 migration 영역)")
        for f in sorted(change_plan_dir.glob("*.md")):
            check_change_plan_file(f, violations)
    else:
        print("[INFO] docs/change-plans/ 없음 — 스킵")

    print()
    print("=== 결과 ===")
    print(f"7 원칙 위반: {len(violations)}건")

    if violations:
        for v in violations:
            print(f"  - {v}")
        if args.strict:
            print("[ERROR] strict mode: 위반 존재 — exit 1")
            return 1
        else:
            print("[WARN] warning tier: 위반 존재 (PR 차단 0, ADR-060 §결정 5)")

    print("[INFO] ADR-089 7 원칙 self-check 완료 (warning tier)")
    print("[INFO] [empirical-source: ADR-068 I-5 — dimensional grounding annotation 의무]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
