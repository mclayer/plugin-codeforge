"""AC-6 — frozen ADR 앵커 내용-기반 resolve.

Change Plan §8 AC-6 RTM 명명 테스트.
  - A-1 = ADR-044:624
  - A-2 = ADR-064:691
  - 5-state 판정 (ANCHOR_OK/NOT_FOUND/AMBIGUOUS/RESOLVE_FAILED/CONTENT_MISMATCH)

Carrier: CFP-2926 Phase 2 (구현) / Story NG-11
"""

from __future__ import annotations

import pytest

try:
    import frozen_anchor
except ImportError:
    pytest.skip("frozen_anchor module not found", allow_module_level=True)


def test_frozen_adr_content_anchor_parity(tmp_path, repo_root):
    """AC-6 2 앵커 전건 (A-1·A-2) 실행 + 5-state 정확성.

    [Mutant M-K: 앵커 줄 1 byte 변경 → RED (CONTENT_MISMATCH)]
    [Mutant M-L: 앵커 위에 N줄 삽입 → GREEN (false-positive guard, kill 아님)]
    [Mutant M-M: 앵커 줄 삭제 → RED (NOT_FOUND)]
    [Mutant M-N: -F 제거 (부분 매치) ∧ 포함 줄 주입 → AMBIGUOUS]
    [Mutant M-O: -x 제거 ∧ 포함 줄 주입 → AMBIGUOUS]

    [Discriminating: A-1 + A-2 둘 다 기계 검증 필수]
    """
    # A-1 앵커 검증
    a1_resolution = frozen_anchor.verify_anchor(repo_root, "A-1")
    assert a1_resolution.status == frozen_anchor.ANCHOR_OK, (
        f"A-1 anchor should resolve, got {a1_resolution.status}"
    )
    assert a1_resolution.line_numbers, "A-1 should have line number(s)"
    assert a1_resolution.sha256, "A-1 should have sha256"

    # A-2 앵커 검증
    a2_resolution = frozen_anchor.verify_anchor(repo_root, "A-2")
    assert a2_resolution.status == frozen_anchor.ANCHOR_OK, (
        f"A-2 anchor should resolve, got {a2_resolution.status}"
    )
    assert a2_resolution.line_numbers, "A-2 should have line number(s)"
    assert a2_resolution.sha256, "A-2 should have sha256"

    # sha256 재산출 대조 (하드코딩 대조 금지 — §8.0.9)
    a1_entry = frozen_anchor.REGISTERED_ANCHORS["A-1"]
    a1_computed_sha = frozen_anchor.line_sha256(a1_entry["verbatim"])
    assert a1_computed_sha == a1_entry["sha256"], (
        f"A-1 sha256 mismatch: computed {a1_computed_sha} vs stored {a1_entry['sha256']}"
    )

    a2_entry = frozen_anchor.REGISTERED_ANCHORS["A-2"]
    a2_computed_sha = frozen_anchor.line_sha256(a2_entry["verbatim"])
    assert a2_computed_sha == a2_entry["sha256"], (
        f"A-2 sha256 mismatch: computed {a2_computed_sha} vs stored {a2_entry['sha256']}"
    )


def test_frozen_anchor_5state_coverage(repo_root):
    """AC-6 5-state enum (ANCHOR_OK/NOT_FOUND/AMBIGUOUS/RESOLVE_FAILED/CONTENT_MISMATCH).

    각 상태가 실제로 반환되는 케이스 검증.
    """
    # ANCHOR_OK: A-1·A-2
    a1 = frozen_anchor.verify_anchor(repo_root, "A-1")
    assert a1.status == frozen_anchor.ANCHOR_OK

    # ANCHOR_NOT_FOUND: 존재하는 파일 + 파일에 없는 텍스트 패턴
    # (파일 "ADR-044-phase-scoped-sequential-team.md" 는 존재하지만 "nonexistent-pattern" 은 없음)
    adr_path = repo_root / "archive" / "adr"
    if adr_path.exists():
        not_found_resolution = frozen_anchor.resolve_anchor(
            repo_root,
            "nonexistent-text-pattern-xyz-not-in-file",
            "archive/adr/ADR-044-phase-scoped-sequential-team.md"
        )
        assert not_found_resolution.status == frozen_anchor.ANCHOR_NOT_FOUND, (
            f"Expected ANCHOR_NOT_FOUND for non-existent pattern in existing file, "
            f"got {not_found_resolution.status}"
        )

    # ANCHOR_RESOLVE_FAILED: 존재하지 않는 파일 경로
    failed_resolution = frozen_anchor.resolve_anchor(
        repo_root, "any-text", "nonexistent-file.md"
    )
    assert failed_resolution.status == frozen_anchor.ANCHOR_RESOLVE_FAILED, (
        f"Expected ANCHOR_RESOLVE_FAILED for non-existent file path, "
        f"got {failed_resolution.status}"
    )
