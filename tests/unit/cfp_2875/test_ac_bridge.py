"""test_ac_bridge.py — CFP-2875 ac-traceability 브리지 pytest.

Story §8.1.1 RTM 명시 식별자 10개 (AC-1~AC-10) — CFP-2869 F-CR-001 선례 동형 선제 저작.
각 테스트는 discriminating(tautology 금지) — 실 게이트 subprocess exit/출력·실 파일 상태 assert,
변조 시 RED 되는 구조. AC-5 는 skip-fired negative-control(S2/S3 반전)을 tmp corpus 로 내장.

의미보존(AC-7 리뷰축)·증적 원본(AC-10 §8.5 실측 표)은 review-tier honest ceiling —
본 브리지의 기계 판정은 구조·상태·exit 관측까지만.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
LIB = REPO_ROOT / "scripts" / "lib"
ADR_171 = REPO_ROOT / "archive/adr/ADR-171-evidence-enforceable-promotion-framework.md"
ADR_060 = REPO_ROOT / "archive/adr/ADR-060-evidence-enforceable-promotion-framework.md"
BASELINE = REPO_ROOT / "docs/adr-amendment-threshold-baseline.yaml"
REGISTRY = REPO_ROOT / "docs/evidence-checks-registry.yaml"
RESERVATION = REPO_ROOT / "archive/adr/ADR-RESERVATION.md"

AMENDMENT_HEADING_RE = re.compile(r"^#{2,4}\s{0,80}Amendment", re.M)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    assert len(parts) >= 3, "frontmatter 구획 부재"
    return parts[1]


def _run_gate(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(LIB / "check_adr_amendment_threshold.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=cwd or REPO_ROOT,
    )


def _predicate():
    sys.path.insert(0, str(LIB))
    try:
        from check_adr_amendment_threshold import is_superseded_status
        return is_superseded_status
    finally:
        sys.path.pop(0)


# ── AC-1 (phase 1) ──────────────────────────────────────────────────────────

def test_ac1_adr171_count0_supersedes_disposition():
    text = _read(ADR_171)
    fm = _frontmatter(text)
    assert re.search(r"^status: Accepted\s*$", fm, re.M)
    assert re.search(r"^supersedes:\n  - ADR-060\s*$", fm, re.M)
    assert re.search(r"^reinterpretation: false", fm, re.M)
    # count-0 재시작: amendment 배열 키 생략 (amends: null 은 별개 키)
    assert not re.search(r"^amendments:", fm, re.M)
    assert not re.search(r"^amendment_log:", fm, re.M)
    # 본문 ratchet-매칭 Amendment 헤딩 0 (born-count 0)
    body = text.split("---", 2)[2]
    assert len(AMENDMENT_HEADING_RE.findall(body)) == 0


# ── AC-2 (phase 2) ──────────────────────────────────────────────────────────

def test_ac2_adr060_superseded_transition():
    text = _read(ADR_060)
    assert len(re.findall(r"^status: Superseded by ADR-171\s*$", text, re.M)) == 1
    assert _predicate()("Superseded by ADR-171") is True


# ── AC-3 (phase 2) ──────────────────────────────────────────────────────────

def test_ac3_baseline_15_adr060_removed():
    text = _read(BASELINE)
    assert len(re.findall(r"^- adr: ", text, re.M)) == 15
    assert "ADR-060" not in text


# ── AC-4 (phase 2) ──────────────────────────────────────────────────────────

def test_ac4_rehome_bijection_seven_surfaces():
    reg = _read(REGISTRY)
    # 역방향 카운트 (값-앵커)
    def field_count(field: str, adr: str) -> int:
        return len(re.findall(
            rf"^\s*{field}:\s+{adr}([^0-9]|$)", reg, re.M))
    assert field_count("owner_adr", "ADR-171") == 11
    assert field_count("paired_owner_adr", "ADR-171") == 3
    assert field_count("carrier_adr", "ADR-171") == 104
    # 쌍-보존 예외 1건 잔존 (carrier_adr: ADR-060 + carrier_amendment: 5 인접 페어)
    assert (field_count("owner_adr", "ADR-060")
            + field_count("paired_owner_adr", "ADR-060")
            + field_count("carrier_adr", "ADR-060")) == 1
    assert re.search(
        r"^\s*carrier_adr: ADR-060.*\n\s*carrier_amendment: 5\s*$", reg, re.M)
    # 헤더 L4 재지향
    assert reg.splitlines()[3].startswith("# Carrier ADR: ADR-171")
    # comment-제외 대사: 값-층에서 신 ADR 오귀속 조합 0
    assert len(re.findall(r"ADR-171[^#\n]*Amendment [0-9]+", reg)) == 0
    # RESERVATION 요약표 row 60 archived + sub-tree 60/25 무접촉(active 잔존)
    res = _read(RESERVATION)
    assert len(re.findall(r"^\| 60 \| CFP-389 \| archived \|", res, re.M)) == 1
    assert re.search(
        r"adr_number: 60\n\s*amendment_id: 25\n\s*reserved_by_cfp: CFP-2650\n"
        r"\s*reserved_at: [0-9-]+\n\s*status: active", res)


# ── AC-5 (phase 2) ──────────────────────────────────────────────────────────

def test_ac5_threshold_gate_green_and_superseded_skip(tmp_path):
    # (a-1) census + GREEN
    r = _run_gate("--mode", "threshold", "--repo-root", str(REPO_ROOT))
    out = r.stdout + r.stderr
    assert r.returncode == 0, out
    assert "adr_candidates=171" in out and "files_checked=170" in out
    assert "::error::" not in out
    # (a-2) predicate
    assert _predicate()("Superseded by ADR-171") is True
    # (a-3) skip-fired negative-control: S3(최종상태) exit 0 ↔ S2(status revert) exit 1
    corpus = tmp_path / "archive" / "adr"
    corpus.mkdir(parents=True)
    for p in (REPO_ROOT / "archive/adr").glob("ADR-*.md"):
        shutil.copy(p, corpus / p.name)
    (tmp_path / "docs").mkdir()
    shutil.copy(BASELINE, tmp_path / "docs" / BASELINE.name)
    s3 = _run_gate("--mode", "threshold", "--repo-root", str(tmp_path))
    assert s3.returncode == 0, s3.stdout + s3.stderr
    target = corpus / ADR_060.name
    target.write_text(
        _read(target).replace(
            "status: Superseded by ADR-171", "status: Accepted", 1),
        encoding="utf-8")
    s2 = _run_gate("--mode", "threshold", "--repo-root", str(tmp_path))
    assert s2.returncode == 1
    assert "ADR-060" in (s2.stdout + s2.stderr)
    assert "baseline 미등재" in (s2.stdout + s2.stderr)


# ── AC-6 (phase 2) ──────────────────────────────────────────────────────────

def test_ac6_selftest_no_regression():
    for script, expect in (
        ("tests/scripts/test_adr-amendment-threshold.sh", "42 passed, 0 failed"),
        ("tests/scripts/test_adr-amendment-parity.sh", "13 passed, 0 failed"),
    ):
        # sh(Git Bash) 사용 — Windows 에서 bash 가 WSL 로 해석되는 문제 회피 (CFP-2869 브리지 선례)
        r = subprocess.run(
            ["sh", str(REPO_ROOT / script)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=REPO_ROOT)
        out = r.stdout + r.stderr
        assert r.returncode == 0, out
        assert expect in out, out


# ── AC-7 (phase 1 — 기계 판정 = 처분표 구조 대사, 의미보존 = review-tier) ──

def test_ac7_disposition_zero_drop_structure_ceiling():
    text = _read(ADR_171)
    assert len(re.findall(r"^\| [0-9]+ \| `", text, re.M)) == 40      # block(1)
    assert len(re.findall(r"^\| `amendment_log\[", text, re.M)) == 8  # (1)-보충
    assert len(re.findall(r"^\| §결정 [0-9]+", text, re.M)) == 12     # block(2)
    assert len(re.findall(r"^\| [0-9]+ \| [a-z]", text, re.M)) == 13  # block(3)


# ── AC-8 (phase 1) ──────────────────────────────────────────────────────────

def test_ac8_number_claim_3leg():
    files = list((REPO_ROOT / "archive/adr").glob("ADR-171-*.md"))
    assert len(files) == 1
    assert len(re.findall(r"^adr_number: 171\s*$", _read(ADR_171), re.M)) == 1
    assert len(re.findall(r"^\| 171 \| CFP-2875 \|", _read(RESERVATION), re.M)) == 1


# ── AC-9 (phase 2 — 이동 표적 재실측) ───────────────────────────────────────

def test_ac9_moving_target_remeasure():
    body_060 = _read(ADR_060).split("---", 2)[2]
    assert len(AMENDMENT_HEADING_RE.findall(body_060)) == 40  # 구본 동결 유지
    body_171 = _read(ADR_171).split("---", 2)[2]
    assert len(AMENDMENT_HEADING_RE.findall(body_171)) == 0   # 신본 count-0 유지


# ── AC-10 (phase 1 — measure-at-authoring replay 재현, 증적 원본 = §8.5) ────

def test_ac10_measure_at_authoring_gate_replay():
    for mode in ("threshold", "parity"):
        r = _run_gate("--mode", mode, "--repo-root", str(REPO_ROOT))
        assert r.returncode == 0, r.stdout + r.stderr
