#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CFP-2804 pytest — paradigm hygiene no-effect-change validation (AC-4 + AC-5 + discriminating).
Validates: (a) per-target corrections applied (37 pairs old absent + new present)
           (b) per-file preserve-counts exact (24 files, 3-pattern distinct-line hits)
           (c) descriptor qualified (5 files, oldform=0, qual=6 total)
           (d) discriminating fixture teeth (RED→GREEN proof of concept)
"""
import re
from pathlib import Path
import pytest

# Repo root: tests/scripts/test_*.py → repo/
REPO_ROOT = Path(__file__).resolve().parents[2]

# AC-4: 37 correction targets (rel, old, new)
CORR = [
    # ---------- archive/adr (group 2) ----------
    ("archive/adr/ADR-122-superpowers-dependency-removal.md",
     "  - ADR-058 (sunset_justification 의무 — 약화 차단)",
     "  - ADR-058 (sunset_justification 의무 — 약화 evidence-gate)"),
    ("archive/adr/ADR-122-superpowers-dependency-removal.md",
     "## sunset_justification (ADR-058 §결정5 — 약화 차단)",
     "## sunset_justification (ADR-058 §결정5 — 약화 evidence-gate)"),
    ("archive/adr/ADR-123-document-readability-and-communication-standard.md",
     "## sunset_justification (ADR-058 §결정 5 — 약화 차단)",
     "## sunset_justification (ADR-058 §결정 5 — 약화 evidence-gate)"),
    ("archive/adr/ADR-124-external-knowledge-provisioning-model.md",
     "## sunset_justification (ADR-058 §결정 5 — 약화 차단)",
     "## sunset_justification (ADR-058 §결정 5 — 약화 evidence-gate)"),
    ("archive/adr/ADR-125-requirements-review-lane.md",
     "## sunset_justification (ADR-058 §결정 5 — 약화 차단)",
     "## sunset_justification (ADR-058 §결정 5 — 약화 evidence-gate)"),
    ("archive/adr/ADR-126-on-demand-research-request-gate.md",
     "| ADR-058 §결정 5 | sunset_justification | **약화 차단** — additive skill + cross-ref only, strengthen 방향, null. |",
     "| ADR-058 §결정 5 | sunset_justification | **약화 evidence-gate** — additive skill + cross-ref only, strengthen 방향, null. |"),
    ("archive/adr/ADR-126-on-demand-research-request-gate.md",
     "## sunset_justification (ADR-058 §결정 5 — 약화 차단)",
     "## sunset_justification (ADR-058 §결정 5 — 약화 evidence-gate)"),
    ("archive/adr/ADR-143-agent-action-render-line-prefix.md",
     "약화 방향 amendment(sub-layer scope 축소 / KST anchor 제거 / persist-guard 해제)는 ADR-058 §결정 5 `sunset_justification` 의무로 차단(ratchet — 강화 방향만).",
     "약화 방향 amendment(sub-layer scope 축소 / KST anchor 제거 / persist-guard 해제)는 ADR-058 §결정 5 `sunset_justification` 의무로 gate (evidence-gated symmetric ratchet — evidence 있으면 약화 1급 허용)."),
    ("archive/adr/ADR-155-dev-process-observability-substrate.md",
     "N/A — permanent substrate policy (약화 방향 차단 ratchet, is_transitional: false)",
     "N/A — permanent substrate policy (약화 방향 evidence-gate ratchet, is_transitional: false)"),
    ("archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md",
     "## sunset_justification (ADR-058 §결정 5 — 약화 차단)",
     "## sunset_justification (ADR-058 §결정 5 — 약화 evidence-gate)"),
    ("archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md",
     "Amendment 는 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application 정합).",
     "Amendment 는 evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무, ADR-058 §결정 5 + ADR-064 §결정 7 self-application 정합)."),
    # ---------- ArchitectAgent (codeforge-design) — discriminating fixture target ----------
    ("plugins/codeforge-design/agents/ArchitectAgent.md",
     "codify). ratchet 강화 방향만.",
     "codify). ratchet = evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무)."),
    # ---------- live 비-ADR (group 1) ----------
    ("docs/wording-dictionary.md",
     '| ratchet | "강화 방향만 허용 + 약화 차단" — ADR amendment top-down rule. forbid-list 축소 / sequential 강제 사유 확장 등 약화 방향 = sunset_justification 의무 |',
     '| ratchet | "evidence-gated symmetric ratchet — 강화·약화 양방향 허용 + 양방향 evidence 의무" — ADR amendment symmetric rule. forbid-list 축소 / sequential 강제 사유 확장 등 약화 방향 = sunset_justification 의무 |'),
    ("docs/domain-knowledge/domain/governance-principle/adr-active-sunset-procedure.md",
     "sunset **기준·메트릭·약화 차단** 기계장치",
     "sunset **기준·메트릭·약화 evidence-gate** 기계장치"),
    ("docs/domain-knowledge/domain/governance-principle/adr-active-sunset-procedure.md",
     "sunset 기준·메트릭·약화 차단 기계장치가 이미 존재하나",
     "sunset 기준·메트릭·약화 evidence-gate 기계장치가 이미 존재하나"),
    ("docs/domain-knowledge/domain/governance-principle/adr-active-sunset-procedure.md",
     "ADR-058 §결정 5 약화 차단 대상 — 본 절차 비대상.",
     "ADR-058 §결정 5 약화 evidence-gate 대상 — 본 절차 비대상."),
    ("docs/domain-knowledge/domain/governance-principle/adr-active-sunset-procedure.md",
     "ADR 일몰 **기준·메트릭·약화 차단** 기계장치가 이미 존재한다",
     "ADR 일몰 **기준·메트릭·약화 evidence-gate** 기계장치가 이미 존재한다"),
    ("docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md",
     'governance `ratchet` ("강화 방향만 허용 + 약화 차단" — ADR amendment top-down rule)',
     'governance `ratchet` ("evidence-gated symmetric ratchet — 강화·약화 양방향 허용 + 양방향 evidence 의무" — ADR amendment symmetric rule)'),
    ("docs/domain-knowledge/domain/governance-principle/decision-style.md",
     "| active amendment | 강화 방향 amendment 적극 발의. 약화 방향은 ADR-058 §결정 5 sunset_justification 의무로 차단 (top-down ratchet) |",
     "| active amendment | 강화 방향 amendment 적극 발의. 약화 방향은 ADR-058 §결정 5 sunset_justification 의무로 gate (evidence-gated symmetric ratchet — evidence 있으면 약화 1급 허용) |"),
    ("docs/domain-knowledge/domain/governance-principle/wording-discipline-enforcement.md",
     "ADR-064 §결정 7 self-application top-down ratchet 은 amendment 를 강화 방향만 허용하고, 약화 방향은 ADR-058 §결정 5 sunset_justification 의무로 차단한다.",
     "ADR-064 §결정 7 self-application evidence-gated symmetric ratchet 은 amendment 를 강화·약화 양방향 허용하되 양방향 evidence 를 요구하고, 약화 방향은 ADR-058 §결정 5 sunset_justification 의무로 gate 한다."),
    ("docs/domain-knowledge/concept/clarification-driven-reinvestigation.md",
     "**약화 방향 차단** (layer 합치 / cap 완화) = ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 정량 명시 의무.",
     "**약화 방향 evidence-gate** (layer 합치 / cap 완화) = ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 정량 명시 의무."),
    ("docs/orchestrator-playbook.md",
     "closed enum — 4번째 trigger 추가 = ADR-073 Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합).",
     "closed enum — 4번째 trigger 추가 = ADR-073 Amendment = evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무, ADR-058 §결정 5 / ADR-064 §결정 7 정합)."),
    ("docs/orchestrator-playbook.md",
     "2번째 trigger token 확장 시 별도 CFP 의무 (ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification null 보존",
     "2번째 trigger token 확장 시 별도 CFP 의무 (ADR-064 §결정 7 evidence-gated symmetric ratchet + ADR-058 §결정 5 sunset_justification null 보존"),
    ("skills/user-dialog-mode/SKILL.md",
     "그대로 보존** (ADR-058 §결정 5 약화 차단 근거).",
     "그대로 보존** (ADR-058 §결정 5 약화 evidence-gate 근거)."),
    ("scripts/check_handoff_wording.py",
     '"ADR Amendment 또는 rename 의무 — ADR-058/064 top-down ratchet "',
     '"ADR Amendment 또는 rename 의무 — ADR-058/064 evidence-gated symmetric ratchet "'),
    ("overlay/hooks/validate_config.py",
     "# ADR-064 §결정 7 ratchet — 약화 방향 차단 (강화 방향만 허용).",
     "# ADR-064 §결정 7 ratchet — evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무)."),
    ("overlay/_overlay/project.yaml.example",
     "# Consumer overlay default 영역. ADR-064 §결정 7 ratchet — 약화 방향 차단 (강화 방향만 허용).",
     "# Consumer overlay default 영역. ADR-064 §결정 7 ratchet — evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무)."),
    ("docs/inter-plugin-contracts/severity-propagation-v1.md",
     "- **Amendment**: ratchet 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application)",
     "- **Amendment**: ratchet evidence-gated symmetric (강화·약화 양방향 + 양방향 evidence 의무, ADR-058 §결정 5 + ADR-064 §결정 7 self-application)"),
    ("docs/inter-plugin-contracts/severity-propagation-v1.md",
     "본 contract 의 모든 Amendment 는 강화 방향만 허용 (ADR-064 top-down self-application). 약화 방향",
     "본 contract 의 모든 Amendment 는 evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무, ADR-064 §결정 7 self-application). 약화 방향"),
    ("docs/inter-plugin-contracts/imperative-walker-protocol-v1.md",
     "- **ADR-064 §self-application**: CFP scope unitary + amendment 강화 방향만 anchor.",
     "- **ADR-064 §self-application**: CFP scope unitary + amendment evidence-gated symmetric ratchet anchor (강화·약화 양방향 + 양방향 evidence 의무)."),
    ("docs/inter-plugin-contracts/imperative-walker-protocol-v1.md",
     "- **Amendment trigger**: ratchet 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application)",
     "- **Amendment trigger**: ratchet evidence-gated symmetric (강화·약화 양방향 + 양방향 evidence 의무, ADR-058 §결정 5 + ADR-064 §결정 7 self-application)"),
    # ---------- descriptor 6 (AC-5) ----------
    ("docs/architecture/codeforge-family.md",
     "- ADR (`docs/adr/`) = 단일 결정 단위 (불변).",
     "- ADR (`docs/adr/`) = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)."),
    ("plugins/codeforge-test/docs/architecture/codeforge-test.md",
     "- ADR = 단일 결정 단위 (불변).",
     "- ADR = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)."),
    ("plugins/codeforge-review/docs/architecture/codeforge-review.md",
     "- ADR = 단일 결정 단위, 불변",
     "- ADR = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)"),
    ("plugins/codeforge-pmo/docs/architecture/codeforge-pmo.md",
     "- ADR = 단일 결정 단위, 불변",
     "- ADR = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)"),
    ("plugins/codeforge-design/docs/architecture/codeforge-design.md",
     "- ADR = 단일 결정 단위, 불변",
     "- ADR = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)"),
    ("plugins/codeforge-design/docs/architecture/codeforge-design.md",
     "- ADR (`docs/adr/`) = 단일 결정 단위 (불변)",
     "- ADR (`docs/adr/`) = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)"),
]

# AC-4: 3-pattern regex (used for preserve-count validation)
PATTERNS = [
    re.compile(r"강화\s*방향만"),
    re.compile(r"약화[^\n]{0,8}차단"),
    re.compile(r"top-down\s+(ratchet|rule|self-application)")
]

# AC-4: 24 allow-list files with expected post-correction preserve-count (distinct-line hits)
EXPECT = {
    "archive/adr/ADR-122-superpowers-dependency-removal.md": 2,
    "archive/adr/ADR-123-document-readability-and-communication-standard.md": 0,
    "archive/adr/ADR-124-external-knowledge-provisioning-model.md": 4,
    "archive/adr/ADR-125-requirements-review-lane.md": 0,
    "archive/adr/ADR-126-on-demand-research-request-gate.md": 2,
    "archive/adr/ADR-143-agent-action-render-line-prefix.md": 0,
    "archive/adr/ADR-155-dev-process-observability-substrate.md": 0,
    "archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md": 1,
    "docs/wording-dictionary.md": 0,
    "docs/domain-knowledge/domain/governance-principle/adr-active-sunset-procedure.md": 0,
    "docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md": 0,
    "docs/domain-knowledge/domain/governance-principle/decision-style.md": 1,
    "docs/domain-knowledge/domain/governance-principle/wording-discipline-enforcement.md": 1,
    "docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md": 3,
    "docs/domain-knowledge/concept/clarification-driven-reinvestigation.md": 0,
    "docs/orchestrator-playbook.md": 1,
    "skills/user-dialog-mode/SKILL.md": 1,
    "scripts/check_handoff_wording.py": 0,
    "overlay/hooks/validate_config.py": 2,
    "overlay/_overlay/project.yaml.example": 0,
    "docs/parallel-work/section-ownership.yaml": 9,
    "docs/inter-plugin-contracts/severity-propagation-v1.md": 3,
    "docs/inter-plugin-contracts/imperative-walker-protocol-v1.md": 3,
    "plugins/codeforge-design/agents/ArchitectAgent.md": 0,
}

# AC-5: descriptor targets (5 files)
DESC_FILES = [
    "docs/architecture/codeforge-family.md",
    "plugins/codeforge-test/docs/architecture/codeforge-test.md",
    "plugins/codeforge-review/docs/architecture/codeforge-review.md",
    "plugins/codeforge-pmo/docs/architecture/codeforge-pmo.md",
    "plugins/codeforge-design/docs/architecture/codeforge-design.md",
]
DESC_OLDFORM = re.compile(r"단일 결정 단위\s*[(,]\s*불변")
DESC_QUAL = "결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10"


def read_file(relpath: str) -> str:
    """Read file from repo root as UTF-8."""
    p = REPO_ROOT / relpath.replace("/", "\\") if "\\" in str(REPO_ROOT) else REPO_ROOT / relpath
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def count_distinct_line_hits(text: str) -> int:
    """Count lines matching any of 3 patterns (each line counted at most once)."""
    count = 0
    for line in text.split("\n"):
        if any(p.search(line) for p in PATTERNS):
            count += 1
    return count


class TestAC4PerTargetCorrected:
    """AC-4: Per-target corrections (37 pairs) — old absent, new present."""

    @pytest.mark.parametrize("relpath,old,new", CORR)
    def test_correction_applied(self, relpath, old, new):
        """Assert old substring absent and new substring present in file."""
        text = read_file(relpath)
        assert old not in text, f"OLD still present in {relpath}: {old[:80]!r}"
        assert new in text, f"NEW missing in {relpath}: {new[:80]!r}"


class TestAC4PerFilePreserveCount:
    """AC-4: Per-file preserve-count validation (24 files, 3-pattern distinct-line hits)."""

    @pytest.mark.parametrize("relpath,expected_hits", list(EXPECT.items()))
    def test_preserve_count_exact(self, relpath, expected_hits):
        """Assert pattern hit count == expected preserve-count per file."""
        text = read_file(relpath)
        got_hits = count_distinct_line_hits(text)
        assert got_hits == expected_hits, (
            f"{relpath}: preserve-count mismatch: "
            f"got {got_hits} hits, expected {expected_hits}"
        )


class TestAC5DescriptorQualified:
    """AC-5: Descriptor qualification (5 files, oldform=0, qual=6 total)."""

    def test_descriptor_oldform_absent(self):
        """Assert unqualified descriptor oldform absent from all 5 DESC_FILES."""
        for relpath in DESC_FILES:
            text = read_file(relpath)
            assert not DESC_OLDFORM.search(text), (
                f"AC-5 unqualified descriptor still present in {relpath}"
            )

    def test_descriptor_qual_count(self):
        """Assert qualifier string appears exactly 6 times across 5 DESC_FILES."""
        total_qual = 0
        for relpath in DESC_FILES:
            text = read_file(relpath)
            total_qual += text.count(DESC_QUAL)
        assert total_qual == 6, (
            f"AC-5 qualifier total = {total_qual} (expected 6)"
        )


class TestDiscriminatingPositiveControl:
    """Discriminating fixture: prove teeth by RED→GREEN (mutate & verify)."""

    def test_pattern1_mutate_catches_regression(self):
        """Pattern-1 (강화\\s*방향만) correctly catches reverted text in-memory.

        Proof: Simulate pre-correction state by revert, verify pattern matches.
        This demonstrates fixture discriminating power (not vacuous GREEN).
        """
        # Read original corrected content
        arch_path = REPO_ROOT / "plugins/codeforge-design/agents/ArchitectAgent.md"
        original_text = arch_path.read_text(encoding="utf-8")

        # Verify current state: new text present, old text absent
        new_text = "ratchet = evidence-gated symmetric ratchet (강화·약화 양방향 + 양방향 evidence 의무)."
        old_text = "ratchet 강화 방향만."

        assert new_text in original_text, "Current state must have new text"
        assert old_text not in original_text, "Current state must NOT have old text"

        # Simulate PRE-CORRECTION state: replace new → old
        mutated_text = original_text.replace(new_text, old_text)

        # Verify mutation occurred
        assert old_text in mutated_text, "Mutation must inject old text"
        assert new_text not in mutated_text, "Mutation must remove new text"

        # NOW: Pattern-1 should MATCH on mutated_text (RED condition)
        pattern1 = PATTERNS[0]  # r"강화\s*방향만"
        line_hits_before = count_distinct_line_hits(mutated_text)

        # Verify pattern catches the reverted form (discriminating)
        has_pattern = any(pattern1.search(line) for line in mutated_text.split("\n") if "ratchet" in line)
        assert has_pattern, "Pattern-1 must match reverted text (RED test condition)"

        # Verify on ORIGINAL (corrected) state: pattern should NOT match in ratchet lines
        line_hits_after = count_distinct_line_hits(original_text)

        # The ArchitectAgent.md should preserve 0 hits post-correction
        assert EXPECT["plugins/codeforge-design/agents/ArchitectAgent.md"] == 0
        assert line_hits_after == 0, "Post-correction ArchitectAgent.md must have 0 pattern hits"

    def test_descriptor_mutate_catches_regression(self):
        """Descriptor oldform correctly catches injected bare (불변) in-memory.

        Proof: Simulate pre-correction state by injecting bare descriptor.
        """
        # Read one DESC_FILE
        relpath = DESC_FILES[0]  # docs/architecture/codeforge-family.md
        original_text = read_file(relpath)

        # Verify current state: qual present, oldform absent
        assert DESC_QUAL in original_text, "Current state must have qualified descriptor"
        assert not DESC_OLDFORM.search(original_text), "Current state must NOT have oldform"

        # Simulate PRE-CORRECTION: inject bare (불변)
        # Find a line with "단일 결정 단위" and inject bare (불변)
        mutated_text = original_text.replace(
            f"단일 결정 단위 (결정 시점 고정",
            "단일 결정 단위 (불변"
        )

        # Verify mutation worked (oldform now present)
        assert DESC_OLDFORM.search(mutated_text), "Mutation must inject oldform"

        # Verify current state still matches none
        assert not DESC_OLDFORM.search(original_text), "Original must still have no oldform"


class TestAC6AmbiguousCohortUntouched:
    """AC-6: Ambiguous 20-cohort no-processing guard (fail-closed preservation).

    These files are out-of-allow-list (not in EXPECT) and should NOT be swept
    by CFP-2804 — they contain 模糊 content where corrections are uncertain.
    Guard: verify they still contain ≥1 old-paradigm pattern (sweep not applied).
    """

    # Ambiguous cohort (10 files: 9 ADR + 1 examples)
    AMBIGUOUS_COHORT = [
        "archive/adr/ADR-095-sunset-metric-standardization.md",
        "archive/adr/ADR-096-min-prerequisite-version-manifest-schema.md",
        "archive/adr/ADR-098-upgrade-agent-runtime-ownership.md",
        "archive/adr/ADR-099-atlassian-allow-redefinition.md",
        "archive/adr/ADR-100-confluence-doc-ssot-recognition.md",
        "archive/adr/ADR-101-verify-before-trust-confluence-rest.md",
        "archive/adr/ADR-103-git-confluence-sync-mechanism.md",
        "archive/adr/ADR-104-operational-phase-definition.md",
        "archive/adr/ADR-107-plugin-declarative-seed-drift-detection.md",
        "examples/ddd-golden-path-mct031.md",
    ]

    def test_ambiguous_cohort_untouched(self):
        """AC-6 no-processing guard: cohort files untouched (still have old-paradigm language).

        Each cohort file must:
        1. NOT be in EXPECT allow-list (confirmation of out-of-sweep scope)
        2. Still contain ≥1 hit from 3-family patterns (sweep not applied)
        """
        for relpath in self.AMBIGUOUS_COHORT:
            # Guard 1: file NOT in allow-list (must be out-of-scope)
            assert relpath not in EXPECT, (
                f"AC-6: {relpath} should be out-of-allow-list (ambiguous cohort), "
                f"but found in EXPECT. This breaks fail-closed preservation intent."
            )

            # Guard 2: file still has ≥1 old-paradigm pattern (no sweep applied)
            text = read_file(relpath)
            hits = count_distinct_line_hits(text)
            assert hits >= 1, (
                f"AC-6: {relpath} must preserve ≥1 old-paradigm pattern hit "
                f"(sweep not applied), but got {hits} hits. "
                f"This breaks fail-closed no-processing intent."
            )

    def test_ambiguous_cohort_discriminating_control(self):
        """Discriminating control: prove fixture detects pattern removal (fixture teeth).

        Pick one ambiguous file, mutate to remove all patterns in-memory,
        verify hits become 0 (fixture actually detects the sweep).
        """
        test_file = self.AMBIGUOUS_COHORT[0]  # ADR-095
        original_text = read_file(test_file)

        # Verify pre-mutation: original has ≥1 hit
        original_hits = count_distinct_line_hits(original_text)
        assert original_hits >= 1, f"Test precondition: {test_file} must have ≥1 hit"

        # Simulate hypothetical sweep: remove pattern-1 and pattern-2 text
        mutated_text = original_text
        for pattern in PATTERNS[:2]:  # pattern-1 and pattern-2 only
            # Replace pattern matches with placeholder
            for line in mutated_text.split("\n"):
                if pattern.search(line):
                    mutated_text = mutated_text.replace(line, "# [pattern removed during mutation]")

        # Verify mutation reduced hits (not strictly 0, but demonstrates removal)
        mutated_hits = count_distinct_line_hits(mutated_text)
        assert mutated_hits < original_hits, (
            f"Mutation must reduce hits: {test_file} had {original_hits} hits, "
            f"after mutation got {mutated_hits} hits. "
            f"Fixture has teeth (detects pattern removal)."
        )
