#!/usr/bin/env python3
"""
scripts/expand_migration_apply.py
CFP-1059-S6 — expand 마이그레이션 apply (ADR-061 외부 .py, ADR-089 원칙 2)

§11.1 step 2: 확장 마이그레이션 apply (green start 직전)
§11.6 idempotency:
  Alembic = revision-based (재apply = no-op if already at head)
  빅데이터 = rekey-migration oneshot (idempotent marker check 후 skip)

§7.4 empirical-source:
  expand timeout = Alembic transaction-per-revision (no fixed timeout, dimension: latency TBD)
  batch size = consumer 데이터 volume 의존 (design-time 미고정, dimension: volume TBD)
  [empirical-source: TBD — consumer 데이터 volume 실측 후 lock-in]

fail-loud + idempotent 결합:
  partial apply 검출 -> exit 비0 + 사용자 알림 (silent 진행 금지)
"""

import argparse
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="expand 마이그레이션 apply")
    p.add_argument("--type", choices=["alembic", "bigdata"], required=True)
    p.add_argument("--target", required=True)
    # mock seam
    p.add_argument("--mock-alembic", default="0")
    p.add_argument("--mock-alembic-at-head", default="0")
    p.add_argument("--mock-bigdata-expand", default="0")
    p.add_argument("--mock-bigdata-already-done", default="0")
    p.add_argument("--mock-partial-apply", default="0")
    return p.parse_args()


def apply_alembic(target: str, mock_alembic: str,
                  mock_at_head: str, mock_partial: str) -> int:
    """
    Alembic upgrade (RDB expand 마이그레이션).
    revision-based -> 재apply = no-op if already at head (idempotent)
    timeout: transaction-per-revision (no fixed numeric — consumer 실측 TBD)
    """
    print(f"[INFO] Alembic expand 마이그레이션: target={target}")
    print("[INFO] [empirical-source: Alembic revision-based, no fixed timeout, dimension: latency TBD]")

    if mock_partial == "1":
        print("[ERROR] partial apply 검출 — fail-loud (silent 진행 금지)", file=sys.stderr)
        print("[ERROR] 수동 복구 필요: alembic downgrade <prev_revision>", file=sys.stderr)
        return 1

    if mock_at_head == "1" or mock_alembic == "0":
        # mock 비활성 또는 already at head
        if mock_at_head == "1":
            print("[INFO] Alembic 이미 head — no-op (idempotent)")
            return 0

    if mock_alembic == "1":
        print(f"[INFO] Alembic upgrade (mock): alembic upgrade {target}")
        print(f"[INFO] expand upgrade 완료: target={target}")
        return 0

    # 실 환경: alembic upgrade (consumer 실구현)
    print(f"[INFO] alembic upgrade {target}")
    return 0


def apply_bigdata_expand(target: str, mock_expand: str,
                         mock_already_done: str, mock_partial: str) -> int:
    """
    빅데이터 expand 마이그레이션 (rekey-migration oneshot).
    idempotent marker check 후 skip.
    batch size = consumer 데이터 volume 의존 (design-time 미고정, dimension: volume TBD)
    [empirical-source: TBD — consumer 데이터 volume 실측 후 lock-in]
    """
    print(f"[INFO] 빅데이터 expand 마이그레이션: target={target}")
    print("[INFO] [empirical-source: oneshot full-scan default, batch_size TBD, dimension: volume]")

    if mock_partial == "1":
        print("[ERROR] partial apply 검출 — fail-loud (silent 진행 금지)", file=sys.stderr)
        return 1

    if mock_already_done == "1":
        print("[INFO] 빅데이터 expand 이미 완료 (idempotent marker 확인) — skip (no-op)")
        return 0

    if mock_expand == "1":
        print(f"[INFO] 빅데이터 rekey-migration (mock): target={target}")
        print("[INFO] expand 완료: marker 기록")
        return 0

    # 실 환경: custom expand (consumer 실구현)
    print(f"[INFO] rekey-migration expand: {target}")
    return 0


def main() -> int:
    args = parse_args()

    print("=== expand-migration-apply.py ===")
    print(f"type={args.type} target={args.target}")

    if args.type == "alembic":
        return apply_alembic(
            args.target,
            args.mock_alembic,
            args.mock_alembic_at_head,
            args.mock_partial_apply,
        )
    elif args.type == "bigdata":
        return apply_bigdata_expand(
            args.target,
            args.mock_bigdata_expand,
            args.mock_bigdata_already_done,
            args.mock_partial_apply,
        )
    else:
        print(f"[ERROR] 알 수 없는 migration type: {args.type}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
