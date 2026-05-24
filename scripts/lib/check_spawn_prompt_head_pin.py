#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1489 / Wave 2-A of CFP-1389 (Sub-CFP A CFP-1437 mechanical wire)
# ADR-073 Amendment 11 §결정 1-A `spawn_prompt_emit` transition trigger 10번째 entry
# ADR-082 Amendment 15 §결정 1 layer 1 sub-scope (1-E) spawn prompt SHA-anchor write-time verify
#
# Pre-spawn HEAD-pin protocol mechanical lint (warning-tier per ADR-060 §결정 5).
#
# Detection scope (declarative anchor — Wave 1 SSOT):
#   - 변경된 파일 중 spawn-prompt candidate (Story §14 Lane Evidence transcripts /
#     Issue body active_sessions context / spawn dispatcher logs) 안에서
#     `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block 존재 + 형식 검증.
#
# 두 가지 검사 (warning-tier — exit 0 항상 for warnings):
#
#   Check (a) — PRE-SPAWN-ORIGIN-MAIN-SHA block presence (PRIMARY):
#     candidate file 안에 spawn evidence marker (e.g. "ArchitectAgent spawn",
#     "RequirementsPLAgent spawn", "deputy spawn", "Lane evidence" 등) 존재 시:
#       block 부재 → [WARN-ABSENT] (advisory, spawn prompt 형식 위반)
#       block 존재 + 형식 무효 → [WARN-INVALID] (SHA non-40-char-hex)
#       block 존재 + 형식 유효 → PASS
#
#   Check (b) — SHA format strict (SECONDARY):
#     regex `^\[PRE-SPAWN-ORIGIN-MAIN-SHA: [0-9a-f]{40}\]$` 위반 시 [WARN-INVALID].
#
# Skip rule (FP-완화 guard):
#   - templates/** 경로 = canonical example 면제 (FP-완화 guard 1).
#   - spawn evidence marker 부재 file = silent skip (lint scope 외).
#
# Bypass channel:
#   - HOTFIX_BYPASS_SPAWN_PROMPT_HEAD_PIN=1 env (label `hotfix-bypass:spawn-prompt-head-pin` 부착 시 workflow 에서 주입)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (예: yaml 파싱 실패 — 본 lint 는 yaml 미사용으로 거의 없음)
#   2 — setup error (예: 파일 시스템 접근 오류)
#
# Usage:
#   python3 check_spawn_prompt_head_pin.py [file ...]
#
# SSOT carrier: CFP-1437 Wave 1 declarative anchor (PR #1444 merged) + 본 Wave 2-A wire.
# Precedent byte-pattern: scripts/lib/check_amendment_number_stale.py (CFP-1216).

import sys
import re
import os
from pathlib import Path

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_SPAWN_PROMPT_HEAD_PIN", "")
if BYPASS_ENV == "1":
    print("[check-spawn-prompt-head-pin] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[check-spawn-prompt-head-pin]"

# strict 40-char lowercase hex SHA — git object name 표준 (ADR-073 Amd 11 §결정 1-A regex 정합)
# 1-A SSOT regex: ^\[PRE-SPAWN-ORIGIN-MAIN-SHA: [0-9a-f]{40}\]$
BLOCK_STRICT_RE = re.compile(
    r"^\[PRE-SPAWN-ORIGIN-MAIN-SHA: ([0-9a-f]{40})\]$",
    re.MULTILINE,
)

# 느슨한 감지용 — block-shape 만 있고 SHA 형식이 다른 경우 catch (Check b)
# `[PRE-SPAWN-ORIGIN-MAIN-SHA: <anything-up-to-100-char>]` 매칭
BLOCK_LOOSE_RE = re.compile(
    r"\[PRE-SPAWN-ORIGIN-MAIN-SHA:\s*([^\]\r\n]{0,100})\s*\]",
)

# spawn evidence marker — 본 file 이 spawn prompt 영역에 속하는지 1차 판별 (FP-완화 guard 2)
# Story §14 Lane Evidence transcripts / Issue body active_sessions / spawn dispatcher log
# 후보 marker (CFP-1437 Wave 1 declarative scope 정합):
SPAWN_EVIDENCE_MARKERS = [
    r"ArchitectAgent\s+spawn",
    r"ArchitectPLAgent\s+spawn",
    r"RequirementsPLAgent\s+spawn",
    r"RequirementsAnalystAgent\s+spawn",
    r"DeveloperPLAgent\s+spawn",
    r"DeveloperAgent\s+spawn",
    r"QADeveloperAgent\s+spawn",
    r"deputy\s+spawn",
    r"sub[- ]?agent\s+spawn",
    r"DesignReviewPLAgent\s+spawn",
    r"CodeReviewPLAgent\s+spawn",
    r"PMOAgent\s+spawn",
    r"Lane\s+evidence",  # Story §14 header
    r"§14\s+Lane",        # 한글 section header
    r"USER-UTTERANCE-VERBATIM",  # ADR-082 sub-scope 1-C precedent — spawn prompt body marker
    r"chief\s+author\s+spawn",
    r"You\s+are\s+codeforge",  # spawn prompt 본문 첫 줄 marker (canonical)
]
SPAWN_EVIDENCE_RE = re.compile("|".join(SPAWN_EVIDENCE_MARKERS), re.IGNORECASE)


# ── path filter (FP-완화 guard 1) ───────────────────────────────────────────
def _is_template_path(filepath):
    """templates/** 경로 식별 — canonical example 면제."""
    # OS-agnostic — both POSIX and Windows separators
    parts = Path(filepath).parts
    return "templates" in parts


def _is_test_fixture_path(filepath):
    """tests/** 경로 식별 — bats fixture 면제 (자기 자신 detection avoid)."""
    parts = Path(filepath).parts
    return "tests" in parts or "fixtures" in parts


def _is_governance_meta_path(filepath):
    """
    Governance / lint metadata 경로 식별 — 본 lint 메커니즘에 대한 documentation 영역 면제
    (FP 완화 guard 4 — CFP-1489 self-app discovery).
    이 영역의 file 들은 본 lint 의 설명 / 정책 / 메커니즘을 기술 (예: '[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]'
    같은 placeholder + regex 인용)이므로 실제 spawn prompt artifact 아님.

    Scope (closed enum):
      - docs/inter-plugin-contracts/**       (label-registry / MANIFEST 등 — lint metadata)
      - docs/evidence-checks-registry.yaml   (본 lint 자체 entry 가 정의된 file)
      - docs/adr/**                          (ADR-073 Amendment 11 / ADR-082 Amendment 15 등 — 정책 본문 + regex 인용)
      - docs/domain-knowledge/**             (governance narrative)
      - docs/parallel-work/**                (governance narrative)
      - docs/security/**                     (PAT rotation log 등)
      - CLAUDE.md                            (wrapper governance — Amendment cross-ref + ADR-082 §결정 1 layer 표 등)
      - docs/orchestrator-playbook.md        (Orchestrator policy)
      - scripts/**                           (lint script 자체 + sibling scripts)
      - .github/workflows/**                 (workflow self-app)
    """
    p = Path(filepath).as_posix()
    # docs/inter-plugin-contracts/** = registry metadata (lint definition surface)
    if "docs/inter-plugin-contracts/" in p:
        return True
    # docs/evidence-checks-registry.yaml = lint registry self
    if p.endswith("docs/evidence-checks-registry.yaml"):
        return True
    # docs/adr/** = ADR body (regex + policy text)
    if "docs/adr/" in p:
        return True
    # docs/domain-knowledge/** + docs/parallel-work/** + docs/security/** = governance narrative
    if "docs/domain-knowledge/" in p or "docs/parallel-work/" in p or "docs/security/" in p:
        return True
    # CLAUDE.md (top-level wrapper governance)
    if p == "CLAUDE.md" or p.endswith("/CLAUDE.md"):
        return True
    # docs/orchestrator-playbook.md
    if p.endswith("docs/orchestrator-playbook.md"):
        return True
    # scripts/** (lint script + sibling scripts)
    if p.startswith("scripts/") or "/scripts/" in p:
        return True
    # .github/workflows/** (workflow self-app — templates/github-workflows/** caught by _is_template_path)
    if ".github/workflows/" in p:
        return True
    return False


# ── 단일 file 검사 ────────────────────────────────────────────────────────────
def check_file(filepath):
    """
    단일 file 검사. 반환: warn_count (int).

    flow:
      1. path filter (templates/**, tests/**, governance-meta skip)
      2. read content
      3. spawn evidence marker 검색 → 부재 시 silent skip (scope 외)
      4. BLOCK_STRICT_RE 매칭 → 있으면 PASS
      5. BLOCK_LOOSE_RE 매칭 → 형식 무효 ([WARN-INVALID])
      6. 둘 다 부재 → [WARN-ABSENT]
    """
    path = Path(filepath)
    if not path.exists():
        # 삭제된 file — silent skip (git diff 가 deletion 도 잡지만 검사 의미 없음)
        return 0

    # FP-완화 guard 1: templates/** 면제
    if _is_template_path(filepath):
        return 0

    # FP-완화 guard 2: tests/** + fixtures/** 면제 (bats fixture self-detection avoid)
    if _is_test_fixture_path(filepath):
        return 0

    # FP-완화 guard 4: governance / lint metadata 영역 면제 (CFP-1489 self-app discovery)
    # 본 lint 의 정책 / 메커니즘을 기술하는 docs/inter-plugin-contracts/** / docs/adr/** /
    # CLAUDE.md / scripts/** / .github/workflows/** 영역은 placeholder + regex 인용을 포함하므로
    # 실제 spawn prompt artifact 아님 — silent skip.
    if _is_governance_meta_path(filepath):
        return 0

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError) as e:
        print(f"{SCRIPT_NAME} [WARN] {filepath}: file read error ({e}) — skip", file=sys.stderr)
        return 0

    # spawn evidence marker 부재 → scope 외 (silent skip)
    if not SPAWN_EVIDENCE_RE.search(text):
        return 0

    # 모든 block-shape 수집 (loose) → 형식 strict 검증 분리 (Check a + Check b 통합)
    # discriminating TC 대응: 같은 file 안 valid + invalid block 공존 시 invalid 도 catch.
    loose_matches = BLOCK_LOOSE_RE.findall(text)

    if not loose_matches:
        # block 자체 부재 = absent (Check a 실패)
        print(
            f"{SCRIPT_NAME} [WARN-ABSENT] {filepath}: "
            f"spawn evidence marker detected but PRE-SPAWN-ORIGIN-MAIN-SHA block absent. "
            f"ADR-073 Amendment 11 §결정 1-A + ADR-082 Amendment 15 §결정 1 layer 1 sub-scope (1-E) — "
            f"spawn prompt body 첫 줄 (또는 [USER-UTTERANCE-VERBATIM] block 다음 줄) 에 "
            f"`[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block 부착 의무. "
            f"hotfix bypass: hotfix-bypass:spawn-prompt-head-pin label",
            file=sys.stderr,
        )
        return 1

    # block 발견 — 각 block 의 SHA 형식 strict 검증 (40-char lowercase hex)
    # ADR-073 Amd 11 §결정 1-A regex: ^\[PRE-SPAWN-ORIGIN-MAIN-SHA: [0-9a-f]{40}\]$
    STRICT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
    invalid_count = 0
    valid_count = 0
    for sha_candidate in loose_matches:
        sha_stripped = sha_candidate.strip()
        if STRICT_SHA_RE.match(sha_stripped):
            valid_count += 1
        else:
            invalid_count += 1
            print(
                f"{SCRIPT_NAME} [WARN-INVALID] {filepath}: "
                f"PRE-SPAWN-ORIGIN-MAIN-SHA block detected but SHA format invalid "
                f"(expected 40-char lowercase hex, got {len(sha_stripped)}-char '{sha_stripped[:50]}'). "
                f"ADR-073 Amendment 11 §결정 1-A regex: ^\\[PRE-SPAWN-ORIGIN-MAIN-SHA: [0-9a-f]{{40}}\\]$",
                file=sys.stderr,
            )

    if invalid_count > 0:
        # invalid block 1+ 발견 = WARN-INVALID (valid block 공존 여부 무관 — discriminating)
        return invalid_count

    # 모든 block valid = PASS
    print(
        f"{SCRIPT_NAME} OK: {filepath} (PRE-SPAWN-ORIGIN-MAIN-SHA block valid, {valid_count} match)",
        file=sys.stderr,
    )
    return 0


# ── main ──────────────────────────────────────────────────────────────────────
def main(argv):
    if not argv:
        print(f"{SCRIPT_NAME} INFO: no files supplied — skip (exit 0)", file=sys.stderr)
        return 0

    total_warn = 0
    for filepath in argv:
        try:
            total_warn += check_file(filepath)
        except Exception as e:
            # 단일 file 검사 실패 = 다음 file 계속 진행 (graceful degradation)
            print(f"{SCRIPT_NAME} [WARN] {filepath}: unexpected error ({type(e).__name__}: {e}) — skip", file=sys.stderr)

    if total_warn == 0:
        print(f"{SCRIPT_NAME} PASS: all files validated ({len(argv)} file(s) scanned)", file=sys.stderr)
    else:
        print(f"{SCRIPT_NAME} SUMMARY: {total_warn} warning(s) emitted (warning-tier, exit 0)", file=sys.stderr)

    # warning-tier — 항상 exit 0 (PR merge 미차단, ADR-060 §결정 5 정합)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
