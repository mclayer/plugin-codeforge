#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_validate_overlay_config.py

consumer overlay 설정 검증 스크립트 (scripts/validate_overlay_config.py) 테스트.

검증 대상 요구사항:
  - 필수 키 3개(github_org, story_key_prefix, codeowners_team) 존재 확인
  - 누락 키 → exit 1, stderr 에 누락 키 이름 출력
  - 파싱 실패(파일 없음, YAML 구문 오류, 최상위 비-dict) → exit 2
  - 기본 경로 = .claude/_overlay/project.yaml

pytest framework. TDD RED → GREEN.
"""

import os
import textwrap
from pathlib import Path

import pytest

# 테스트 대상 스크립트는 import 방식으로 호출 (subprocess 없이)
import sys

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_overlay_config as voc  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────────────────────────────────────

def _write_yaml(tmp_path: Path, content: str, subpath: str = "project.yaml") -> Path:
    """tmp_path 아래 subpath 에 YAML 파일 생성 후 경로 반환."""
    target = tmp_path / subpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


# ─────────────────────────────────────────────────────────────────────────────
# 케이스 1: 모든 필수 키 존재 → exit 0, stdout "OK"
# ─────────────────────────────────────────────────────────────────────────────

def test_all_keys_present(tmp_path: Path, capsys):
    """필수 키 3개가 모두 있으면 exit 0 이고 stdout 에 OK 가 출력된다."""
    yaml_file = _write_yaml(tmp_path, textwrap.dedent("""\
        github_org: mclayer
        story_key_prefix: CFP
        codeowners_team: codeforge-owners
        extra_key: ignored
    """))

    ret = voc.main([str(yaml_file)])

    captured = capsys.readouterr()
    assert ret == 0
    assert "OK" in captured.out
    assert captured.err == ""


# ─────────────────────────────────────────────────────────────────────────────
# 케이스 2: 키 1개 누락 → exit 1, stderr 에 누락 키 이름 포함
# ─────────────────────────────────────────────────────────────────────────────

def test_one_key_missing(tmp_path: Path, capsys):
    """codeowners_team 누락 시 exit 1, stderr 에 해당 키 이름이 있다."""
    yaml_file = _write_yaml(tmp_path, textwrap.dedent("""\
        github_org: mclayer
        story_key_prefix: CFP
    """))

    ret = voc.main([str(yaml_file)])

    captured = capsys.readouterr()
    assert ret == 1
    assert "codeowners_team" in captured.err
    # 존재하는 키 이름은 stderr 에 없어야 한다
    assert "github_org" not in captured.err
    assert "story_key_prefix" not in captured.err


# ─────────────────────────────────────────────────────────────────────────────
# 케이스 3: 키 여러 개 누락 → exit 1, stderr 에 누락 키 전부 포함
# ─────────────────────────────────────────────────────────────────────────────

def test_multiple_keys_missing(tmp_path: Path, capsys):
    """github_org 만 있고 나머지 2개 누락 시, stderr 에 두 키 모두 등장한다."""
    yaml_file = _write_yaml(tmp_path, textwrap.dedent("""\
        github_org: mclayer
    """))

    ret = voc.main([str(yaml_file)])

    captured = capsys.readouterr()
    assert ret == 1
    assert "story_key_prefix" in captured.err
    assert "codeowners_team" in captured.err


# ─────────────────────────────────────────────────────────────────────────────
# 케이스 4: 잘못된 YAML (구문 오류) → exit 2, 명확 에러 메시지
# ─────────────────────────────────────────────────────────────────────────────

def test_invalid_yaml_syntax(tmp_path: Path, capsys):
    """YAML 구문 오류가 있는 파일이면 exit 2, stderr 에 에러 메시지가 있다."""
    yaml_file = _write_yaml(tmp_path, textwrap.dedent("""\
        github_org: mclayer
        broken: [unclosed
        story_key_prefix: CFP
    """))

    ret = voc.main([str(yaml_file)])

    captured = capsys.readouterr()
    assert ret == 2
    assert captured.err.strip() != ""


# ─────────────────────────────────────────────────────────────────────────────
# 케이스 5: 파일 없음 → exit 2
# ─────────────────────────────────────────────────────────────────────────────

def test_file_not_found(tmp_path: Path, capsys):
    """존재하지 않는 경로를 지정하면 exit 2, stderr 에 에러 메시지가 있다."""
    missing = tmp_path / "nonexistent.yaml"

    ret = voc.main([str(missing)])

    captured = capsys.readouterr()
    assert ret == 2
    assert captured.err.strip() != ""


# ─────────────────────────────────────────────────────────────────────────────
# 케이스 6: 최상위가 dict 아님 (리스트) → exit 2
# ─────────────────────────────────────────────────────────────────────────────

def test_top_level_not_dict(tmp_path: Path, capsys):
    """YAML 최상위가 리스트이면 exit 2, stderr 에 에러 메시지가 있다."""
    yaml_file = _write_yaml(tmp_path, textwrap.dedent("""\
        - github_org: mclayer
        - story_key_prefix: CFP
        - codeowners_team: codeforge-owners
    """))

    ret = voc.main([str(yaml_file)])

    captured = capsys.readouterr()
    assert ret == 2
    assert captured.err.strip() != ""


# ─────────────────────────────────────────────────────────────────────────────
# 케이스 7: 기본 경로 동작 — 인자 없이 호출 시 .claude/_overlay/project.yaml 참조
# ─────────────────────────────────────────────────────────────────────────────

def test_default_path(tmp_path: Path, monkeypatch, capsys):
    """인자 없이 main() 호출 시 .claude/_overlay/project.yaml 을 찾는다."""
    # tmp_path 를 작업 디렉터리로 변경
    monkeypatch.chdir(tmp_path)

    # 기본 경로에 유효한 YAML 생성
    _write_yaml(tmp_path, textwrap.dedent("""\
        github_org: mclayer
        story_key_prefix: CFP
        codeowners_team: codeforge-owners
    """), subpath=".claude/_overlay/project.yaml")

    ret = voc.main([])  # 인자 없음

    captured = capsys.readouterr()
    assert ret == 0
    assert "OK" in captured.out


def test_default_path_missing(tmp_path: Path, monkeypatch, capsys):
    """인자 없이 호출했을 때 기본 경로 파일이 없으면 exit 2 가 된다."""
    monkeypatch.chdir(tmp_path)
    # .claude/_overlay/project.yaml 생성하지 않음

    ret = voc.main([])

    assert ret == 2
