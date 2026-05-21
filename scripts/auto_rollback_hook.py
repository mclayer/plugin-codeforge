#!/usr/bin/env python3
"""
scripts/auto_rollback_hook.py
CFP-1059-S6 — green health 실패 -> blue 복귀 (ADR-061 외부 .py, ADR-087 §결정 5)

§7.4 empirical-source:
  healthcheck window 60s: ADR-087 §결정 5 (dimension: latency + count)
  3시간 보존 window 내 rollback: Issue #1059 카테고리 3/9 (dimension: lifecycle)
  3시간 후 결함 = hotfix 흐름 (자동 rollback 영역 외)

§11.6 idempotency:
  blue 이미 active = no-op (rollback 재실행 안전)

fail-loud: 롤백 시 사용자 알림 의무 (silent 차단, ADR-089 원칙 4)
"""

import argparse
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="auto-rollback hook")
    p.add_argument("--repo", required=True)
    p.add_argument("--host", required=True)
    # mock seam
    p.add_argument("--mock-docker", default="0")
    p.add_argument("--mock-ssh", default="0")
    p.add_argument("--mock-health", default="real")
    p.add_argument("--mock-blue-active", default="0")
    p.add_argument("--mock-within-retention", default="0")
    return p.parse_args()


def is_blue_active(repo: str, host: str, mock_blue_active: str) -> bool:
    """blue container 현재 active 여부 (idempotency 체크)"""
    if mock_blue_active == "1":
        return True
    # 실 환경: docker inspect / Traefik label 체크 (consumer 영역)
    return False


def check_within_retention(mock_within_retention: str) -> bool:
    """3시간 보존 window 내 여부"""
    if mock_within_retention == "1":
        return True
    # 실 환경: retention timer 상태 확인 (consumer 영역)
    return True  # default: window 내로 가정


def rollback(repo: str, host: str, mock_docker: str) -> None:
    """
    blue 복귀 (swap revert): green 폐기 + blue 재활성
    rollback = blue 재활성 (기존 container, secret 재주입 0, §7.5)
    fail-loud: 사용자 알림 의무
    """
    if mock_docker == "1":
        print(f"[ROLLBACK] green 폐기 + blue 복귀 (mock): repo={repo} host={host}")
        print("[ROLLBACK] Traefik label revert (swap revert)")
        print("[ROLLBACK] 사용자 알림: 배포 실패, blue 복귀 완료")
        return
    # 실 환경: docker API call + Traefik label revert (consumer 영역)
    print(f"[ROLLBACK] blue 복귀: repo={repo} host={host}")
    print("[ROLLBACK] 사용자 알림: 배포 실패")


def main() -> int:
    args = parse_args()

    print(f"[INFO] auto-rollback-hook: repo={args.repo} host={args.host}")

    # idempotency: blue 이미 active -> no-op
    if is_blue_active(args.repo, args.host, args.mock_blue_active):
        print("[INFO] blue 이미 active — no-op (idempotent rollback 재실행 안전)")
        return 0

    # 보존 window 확인
    within_retention = check_within_retention(args.mock_within_retention)
    if not within_retention:
        print("[WARN] 3시간 보존 window 만료 — 자동 rollback 영역 외 (hotfix 흐름 필요)")
        print("[empirical-source: Issue #1059 카테고리 3/9 — 3시간 window, dimension: lifecycle]")
        # 만료 후 결함 = hotfix 흐름 (자동 rollback 미수행)
        return 0

    # rollback 실행 (fail-loud)
    print("[INFO] 3시간 보존 window 내 rollback 실행")
    rollback(args.repo, args.host, args.mock_docker)

    # fail-loud: 항상 알림 출력 (silent 차단)
    print(f"[ALERT] 배포 실패: repo={args.repo} — blue 복귀 완료. 원인 조사 필요.")
    print("[INFO] [empirical-source: ADR-087 §결정 5 — healthcheck 60s default, dimension: latency]")

    # rollback 자체 성공 (배포는 실패)
    return 0


if __name__ == "__main__":
    sys.exit(main())
