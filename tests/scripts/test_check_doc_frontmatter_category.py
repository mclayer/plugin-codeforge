#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFP-2680 / ADR-153 — CATEGORY_VALID(check_doc_frontmatter.py) execution-backed self-test.

계약(scripts/lib/check_doc_frontmatter.py CATEGORY_VALID 블록) firsthand 검증:
  - enum = docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum CWD-relative 동적 read,
    casefold whole-string membership.
  - scope = docs/adr + archive/adr. category None→skip / non-str·blank·미지값→fail-closed.
  - grandfather = FROZEN_BASELINE_3 (file-keyed 3 tuple, shrink-only).
  - enum-source 부재/unparseable → fail-OPEN(skip) + stderr 경고.

RTM: AC-1..8 (Change Plan §8.2) 각 pos+neg discriminating + §8.3 edge / shrink-only / mutation-kill.
oracle = 실 checker subprocess exit code + stdout/stderr substring 결박 (false-oracle 0; ADR-145 §결정 5).
structural test(sentinel presence / ast-extract grandfather)만 source 읽음.

정적 lint 이므로 runtime numeric invariant N/A — discriminating pos/neg + mutation-kill 로 대체.
"""
import ast
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_doc_frontmatter.py"
REAL_IA = REPO_ROOT / "docs" / "confluence-ia-tree.yaml"

# 대부분 테스트는 minimal 합성 enum 사용 (실 SSOT 미read — SSOT-coupling 회피).
MINIMAL_ENUM = ["governance", "architecture", "security", "agent-tier", "team & process", "process"]

# grandfather baseline (test-local 독립 하드코딩 — source 자기비교 금지; ⊆ shrink-only 대비용).
# source FROZEN_BASELINE_3 과 별개 객체로 유지해 tautology 봉인.
_EXPECTED_BASELINE_3 = {
    ("archive/adr/ADR-131-cross-repo-responsibility-placement-governance.md", "orchestration/governance"),
    ("archive/adr/ADR-132-consumer-branch-protection-auto-wire.md", "governance/security"),
    ("archive/adr/ADR-133-adr-reservation-atomic-claim.md", "orchestration/governance"),
}

# CFP-2603 branch-protection required contexts (7-tuple, 하드코딩 상수).
SEVEN_TUPLE = [
    "phase-gate-mergeable",
    "invariant-check",
    "doc frontmatter schema (CFP-28 — strict)",
    "doc section schema (CFP-28 — strict)",
    "check-gate",
    "Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)",
    "ac-traceability-matrix",
]


# ─────────────────────────── helpers ───────────────────────────
def run_checker(cwd):
    """실 checker 를 subprocess 로 실행 (CWD-relative scan). exit + stdout/stderr 반환."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def write_adr(fixture, name, category_line, subdir="archive/adr", body=""):
    """완전 frontmatter(5 필드) ADR — 유일 실패 원인이 category membership 이도록."""
    d = fixture / subdir
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(
        "---\nadr_number: 999\ntitle: T\nstatus: Accepted\n"
        f"category:{category_line}\ndate: 2026-07-14\n---\n\n# T\n{body}\n",
        encoding="utf-8",
    )


def write_ia(fixture, enum=None):
    """minimal 합성 enum yaml 을 CWD-relative 위치(docs/confluence-ia-tree.yaml)에 배치."""
    if enum is None:
        enum = MINIMAL_ENUM
    d = fixture / "docs"
    d.mkdir(parents=True, exist_ok=True)
    lines = "\n".join(f"    - {e}" for e in enum)
    (d / "confluence-ia-tree.yaml").write_text(
        "lane_mapping_rule:\n  closed_enum:\n" + lines + "\n",
        encoding="utf-8",
    )


def write_change_plan(fixture, name):
    """완전 change-plan frontmatter(6 필드) + stray category — non-ADR path 는 category 미검사 증명용."""
    d = fixture / "docs" / "change-plans"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(
        "---\ntitle: T\nslug: t\nstatus: draft\nauthor: a\n"
        "created: 2026-07-14\nstory: CFP-2680\ncategory: bogus/value\n---\n\n# T\n",
        encoding="utf-8",
    )


def extract_frozen_baseline_3():
    """SCRIPT source 를 ast.parse → FROZEN_BASELINE_3 Assign 노드 literal_eval → set."""
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "FROZEN_BASELINE_3" for t in node.targets
        ):
            return set(ast.literal_eval(node.value))
    raise AssertionError("FROZEN_BASELINE_3 not found")


# ─────────────────────────── AC-1 ───────────────────────────
def test_ac1_capitalized_architecture_passes(tmp_path):
    # category `Architecture` → casefold → `architecture` ∈ enum → exit 0 (case-fold membership).
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-901-cap-arch.md", " Architecture")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ac1_bogus_not_in_enum_fails(tmp_path):
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-902-bogus.md", " bogus-not-in-enum")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "category" in r.stdout
    assert "bogus-not-in-enum" in r.stdout


# ─────────────────────────── AC-2 ───────────────────────────
def test_ac2_invalid_emits_amendment_and_sunset_substrings(tmp_path):
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-903-inv.md", " bogus-xyz")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "ADR Amendment" in r.stdout
    assert "sunset_justification" in r.stdout


def test_ac2_valid_no_guidance_substring(tmp_path):
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-904-valid.md", " governance")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "sunset_justification" not in r.stdout


# ─────────────────────────── AC-3 ───────────────────────────
def test_ac3_reserved_agent_tier_passes(tmp_path):
    # enum 에 agent-tier 포함(MINIMAL_ENUM) + category agent-tier → exit 0.
    # positive-control: enum 이 하드코딩 16-상수 집합이 아니라 yaml 동적 read 임을 확인(예약값도 통과).
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-905-agent-tier.md", " agent-tier")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ac3_yaml_mutation_added_enum_passes(tmp_path):
    # SOLE SSOT-reading test: 실 REAL_IA copy → closed_enum 에 신규 lowercase enum 추가 mutate →
    # 동일 category ADR → exit 0. enum 이 하드코딩이 아니라 yaml 동적 read 임을 실증.
    # oracle = 하드코딩 리터럴 `zzz-novel-enum` (enum-count assert 금지).
    ia_text = REAL_IA.read_text(encoding="utf-8")
    mutated = ia_text.replace("  closed_enum:\n", "  closed_enum:\n    - zzz-novel-enum\n", 1)
    assert mutated != ia_text, "closed_enum 앵커 치환 실패 — REAL_IA 구조 변경?"
    d = tmp_path / "docs"
    d.mkdir(parents=True, exist_ok=True)
    (d / "confluence-ia-tree.yaml").write_text(mutated, encoding="utf-8")
    write_adr(tmp_path, "ADR-906-novel.md", " zzz-novel-enum")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


# ─────────────────────────── AC-4 ───────────────────────────
def test_ac4_multiword_team_and_process_passes(tmp_path):
    # category `Team & Process` → casefold `team & process` ∈ enum → exit 0 (split 없음, whole-string).
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-907-team.md", " Team & Process")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ac4_compound_slash_fails(tmp_path):
    # 신규 ADR(grandfather 파일명 아님) category `orchestration/governance` → whole-string → 실패.
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-908-compound.md", " orchestration/governance")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "orchestration/governance" in r.stdout


# ─────────────────────────── AC-5 ───────────────────────────
def test_ac5_body_stray_category_ignored(tmp_path):
    # frontmatter category valid + body 에 stray `category: bogus/value` → frontmatter parse 만 → 통과.
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-909-body.md", " governance", body="category: bogus/value")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ac5_frontmatter_invalid_fails(tmp_path):
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-910-fm.md", " bogus/value")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "bogus/value" in r.stdout


# ─────────────────────────── AC-6 ───────────────────────────
def test_ac6_membership_failure_via_frontmatter_checker(tmp_path):
    # 실패가 기존 required checker(::error::CFP-28 doc-frontmatter STRICT)에 귀속됨을 확인.
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-911-inv.md", " bogus-membership")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "::error::CFP-28 doc-frontmatter (STRICT)" in r.stdout


def test_ac6_no_new_required_context_no_standalone_workflow():
    # structural: 신규 standalone script 부재 + 전용 self-test workflow 존재 + 7-tuple 무등재.
    assert not (REPO_ROOT / "scripts" / "check-adr-category-lane-coverage.sh").exists()
    wf = REPO_ROOT / ".github" / "workflows" / "doc-frontmatter-category-test.yml"
    assert wf.exists(), "전용 self-test workflow 부재"
    assert "doc-frontmatter-category-test" not in SEVEN_TUPLE


# ─────────────────────────── AC-7 ───────────────────────────
def test_ac7_current_corpus_green_with_grandfather():
    # 실 repo 코퍼스 — ADR-131/132/133 grandfather 통과 실증 (born-red 가드).
    r = run_checker(REPO_ROOT)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ac7_new_compound_fails_live(tmp_path):
    # fixture 신규 ADR compound (파일명 grandfather 아님) → 실패 (file-keyed grandfather 증명).
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-912-new-compound.md", " orchestration/governance")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "orchestration/governance" in r.stdout


# ─────────────────────────── AC-8 ───────────────────────────
def test_ac8_non_adr_path_category_excluded(tmp_path):
    # change-plan(완전 frontmatter) + stray category, ADR 파일 0 → category 는 ADR-scoped → 통과.
    write_change_plan(tmp_path, "CFP-2680-plan.md")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_ac8_docs_adr_and_archive_adr_both_enforced(tmp_path):
    # 동일 invalid category 를 docs/adr 와 archive/adr 양쪽 배치 → 둘 다 실패 보고.
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-913-in-docs-adr.md", " bogus/value", subdir="docs/adr")
    write_adr(tmp_path, "ADR-914-in-archive-adr.md", " bogus/value", subdir="archive/adr")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "ADR-913-in-docs-adr.md" in r.stdout
    assert "ADR-914-in-archive-adr.md" in r.stdout


# ─────────────────────── §8.3 edge / discriminating ───────────────────────
def test_edge_blank_category_fails(tmp_path):
    # category "" → strip 후 empty → fail-closed (D4-esc-1).
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-920-blank.md", ' ""')
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "category" in r.stdout
    assert "blank" in r.stdout


def test_edge_present_null_category_fails(tmp_path):
    # category: (bare, YAML null) → 키 존재·값 null(present-null) → fail-closed (F-CR-2680-1).
    # blank("")·absent(키 부재)와 disjoint — present-null 별도 커버. 값 표기 `(null)`.
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-931-present-null.md", "")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "category" in r.stdout
    assert "(null)" in r.stdout


def test_edge_nonstr_category_no_crash_fails(tmp_path):
    # category [foo, bar] (list) → non-str guard → fail-closed, crash 없음 (D4-esc-2).
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-921-list.md", " [foo, bar]")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "Traceback" not in r.stderr
    assert "category" in r.stdout


def test_edge_case_fold_mixed_case_passes(tmp_path):
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-922-mixed.md", " GoVeRnAnce")
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_edge_trailing_whitespace_stripped_passes(tmp_path):
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-923-trail.md", ' "governance "')
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_edge_enum_source_absent_fails_open_with_warning(tmp_path):
    # yaml 미생성 → enum None → fail-open(membership skip) + stderr 경고. invalid category 라도 exit 0.
    write_adr(tmp_path, "ADR-924-bogus.md", " bogus-xyz")  # no write_ia
    r = run_checker(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "fail-open" in r.stderr


def test_edge_multi_file_all_failures_reported(tmp_path):
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-925-a.md", " bogus-aaa")
    write_adr(tmp_path, "ADR-926-b.md", " bogus-bbb")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "ADR-925-a.md" in r.stdout
    assert "ADR-926-b.md" in r.stdout


def test_security_log_injection_value_sanitized(tmp_path):
    # category "::evil\r\nsecond" (double-quoted yaml escape → 실 CR/LF) → sanitize 로 공백 치환.
    # 값 라인 단일 라인 유지 (미sanitize 면 evil/second 분리). 헤더 `::error::` 는 정당하니 값 라인만 검사.
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-927-inj.md", ' "::evil\\r\\nsecond"')
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    lines = r.stdout.splitlines()
    # sanitize 성공 = CR/LF→공백 → evil 과 second 가 동일 라인 (미sanitize 면 splitlines 로 분리됨).
    assert any("evil" in ln and "second" in ln for ln in lines), r.stdout
    # 값에서 유래한 standalone 주입 라인(log-injection) 부재.
    assert not any(ln.strip() == "second" for ln in lines), r.stdout


# ─────────────────────── shrink-only / grandfather (structural) ───────────────────────
def test_grandfather_source_subset_of_expected_local():
    # ast-extract 한 source FROZEN_BASELINE_3 ⊆ test-local _EXPECTED_BASELINE_3 (source 자기비교 금지, ⊆ only).
    extracted = extract_frozen_baseline_3()
    assert extracted <= _EXPECTED_BASELINE_3, (
        f"grandfather 가 예상 baseline 초과(append=ratchet 약화): {extracted - _EXPECTED_BASELINE_3}"
    )


def test_grandfather_values_not_in_closed_enum():
    # 실 REAL_IA closed_enum casefold set 로드 → 각 grandfather 값 ∉ enum (grandfather 필요성 실증).
    data = yaml.safe_load(REAL_IA.read_text(encoding="utf-8"))
    enum_folded = {str(e).strip().casefold() for e in data["lane_mapping_rule"]["closed_enum"]}
    for _path, val in _EXPECTED_BASELINE_3:
        assert val not in enum_folded, f"grandfather 값 '{val}' 이 enum 에 존재 — grandfather 불필요"


def test_grandfather_files_exist():
    for path, _val in _EXPECTED_BASELINE_3:
        assert (REPO_ROOT / path).exists(), f"grandfather 파일 부재: {path}"


def test_grandfather_count_le_3():
    assert len(extract_frozen_baseline_3()) <= 3


def test_sentinel_cat_membership_fail_present():
    # sibling-guard: membership warn append 라인 sentinel 주석 존재.
    assert "# CAT-MEMBERSHIP-FAIL" in SCRIPT.read_text(encoding="utf-8")


def test_mutation_kill_membership_append_line(tmp_path):
    # membership append 라인 load-bearing 결박: known-bad category leak 확인.
    write_ia(tmp_path)
    write_adr(tmp_path, "ADR-930-leak.md", " known-bad-leak-marker")
    r = run_checker(tmp_path)
    assert r.returncode != 0, r.stdout
    assert "known-bad-leak-marker" in r.stdout
