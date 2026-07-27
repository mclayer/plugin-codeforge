#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""path_safety.py — rel_path 컨테인먼트 검증 (F-SEC-01 path-traversal 방어).

backward substrate write / gate staging 이 attacker-영향 가능 rel_path 로 repo·staging
밖을 벗어나지 못하도록 fail-closed 검증. sync·gate 양 모듈이 공유(중복 하드코딩 금지).
InvariantViolation(도메인 예외)은 confluence_backward_sync 에만 있어 순환 import 회피 위해
여기서는 stdlib ValueError 로 신호 — 소비측이 각자 fail-closed 처리(sync=InvariantViolation
re-raise / gate=return False).
"""
from pathlib import Path, PurePosixPath


def safe_rel_path(rel_path: str) -> str:
    """repo-relative canonical rel_path 를 검증·정규화.

    거부(→ ValueError, fail-closed): 부재/비문자열 / 절대경로 / Windows 드라이브(`C:`) /
    `..` 세그먼트(path-traversal) / 빈·현재 경로. 정상 → forward-slash·leading-slash 제거 rel.
    """
    if not rel_path or not isinstance(rel_path, str):
        raise ValueError("rel_path 부재/비문자열")
    rel = rel_path.replace("\\", "/").strip()
    if rel.startswith("/"):
        raise ValueError(f"절대경로 거부: {rel_path!r}")
    if len(rel) >= 2 and rel[1] == ":":
        raise ValueError(f"드라이브 경로 거부: {rel_path!r}")
    parts = PurePosixPath(rel).parts
    if any(p == ".." for p in parts):
        raise ValueError(f"'..' 세그먼트 거부(path-traversal): {rel_path!r}")
    cleaned = rel.lstrip("/")
    if not cleaned or cleaned in (".", "./"):
        raise ValueError(f"빈/현재 경로 거부: {rel_path!r}")
    return cleaned


def contained_target(base, rel_path: str) -> Path:
    """base 하위로 컨테인먼트 검증된 target Path 반환 — 벗어나면 ValueError(fail-closed).

    safe_rel_path 로 `..`/절대경로 1차 거부 후, resolve() 재확인(symlink/잔여 `..` 방어)으로
    target 이 base.resolve() 하위인지 재검증.
    """
    cleaned = safe_rel_path(rel_path)
    base_resolved = Path(base).resolve()
    target = (base_resolved / cleaned).resolve()
    try:
        target.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"컨테인먼트 위반: {rel_path!r} escapes {base}")
    return target
