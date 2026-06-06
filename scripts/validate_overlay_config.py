#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_overlay_config.py — consumer overlay project.yaml 필수 키 검증 CLI

목적:
  consumer 프로젝트의 .claude/_overlay/project.yaml 에
  필수 최상위 키(github_org, story_key_prefix, codeowners_team)가
  모두 존재하는지 검사한다.

요구사항 요약:
  - 입력: project.yaml 경로 (positional, optional). 기본값 .claude/_overlay/project.yaml
  - 모든 키 존재 → stdout "OK", exit 0
  - 누락 키 존재 → 누락 키 목록을 stderr 출력, exit 1
  - YAML 파싱 실패 / 파일 없음 / 최상위 비-dict → stderr 오류 메시지, exit 2

Usage:
  python3 scripts/validate_overlay_config.py [project_yaml_path]
"""

import argparse
import sys
from pathlib import Path

import yaml

# 검사할 필수 최상위 키 목록
REQUIRED_KEYS: list[str] = ["github_org", "story_key_prefix", "codeowners_team"]

# 인자 미지정 시 사용하는 기본 경로 (실행 시점 cwd 기준)
DEFAULT_CONFIG_PATH = ".claude/_overlay/project.yaml"


def validate(path: str | Path) -> list[str]:
    """
    지정된 경로의 project.yaml 을 읽어 필수 키 누락 목록을 반환한다.

    반환값:
      list[str] — 누락된 키 이름 목록. 비어 있으면 모두 존재.

    예외:
      FileNotFoundError  — 파일이 존재하지 않을 때
      yaml.YAMLError     — YAML 구문 오류
      TypeError          — 최상위가 dict 가 아닐 때 (예: 리스트, 스칼라)
    """
    path = Path(path)

    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if not isinstance(data, dict):
        raise TypeError(
            f"YAML 최상위가 매핑(dict)이 아닙니다: {type(data).__name__} — {path}"
        )

    missing = [key for key in REQUIRED_KEYS if key not in data]
    return missing


def main(argv: list[str] | None = None) -> int:
    """
    CLI 진입점. argv 를 받아 처리 결과를 int (exit code) 로 반환한다.

    exit code:
      0 — 모든 필수 키 존재
      1 — 누락 키 있음
      2 — YAML 파싱 불가 (파일 없음 / 구문 오류 / 비-dict 최상위)
    """
    parser = argparse.ArgumentParser(
        description="consumer overlay project.yaml 필수 키 검증"
    )
    parser.add_argument(
        "config",
        nargs="?",
        default=DEFAULT_CONFIG_PATH,
        metavar="project_yaml_path",
        help=f"검사할 project.yaml 경로 (기본값: {DEFAULT_CONFIG_PATH})",
    )
    args = parser.parse_args(argv)

    try:
        missing = validate(args.config)
    except FileNotFoundError:
        print(
            f"오류: 파일을 찾을 수 없습니다 — {args.config}",
            file=sys.stderr,
        )
        return 2
    except yaml.YAMLError as exc:
        print(
            f"오류: YAML 구문 오류 — {args.config}: {exc}",
            file=sys.stderr,
        )
        return 2
    except TypeError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 2

    if missing:
        print(
            f"누락된 필수 키: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
