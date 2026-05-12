---
story_key: CFP-476
phase: Phase 2
prior_art_chain: CFP-393 → CFP-455 → CFP-476
byte_identity_invariant_ref: ADR-026 Amendment 1 §결정 5.B
test_harness: tests/workflows/test_post-merge-followup-yml.sh
fixture_dir: tests/fixtures/post-merge-followup/
test_mapping_date: 2026-05-12
---

# CFP-476 Phase 2 — Test Mapping & Coverage

## Prior art chain (CFP-393 → CFP-455 → CFP-476)

| CFP | Focus | Test artifact | Lesson applied to CFP-476 |
|---|---|---|---|
| CFP-393 | Rate-limit fallback KPI dashboard | `test_rate-limit-fallback-kpi-yml.sh` | YAML validity + keyword grep pattern |
| CFP-455 | Evidence-registry-check workflow YAML | `test_evidence-registry-check-yml.sh` | Block structure (YAML + grep + yq), byte-identity invariant (ADR-029→ADR-026 Amendment 1 §결정 5.B) |
| CFP-476 | Post-merge-followup workflow YAML (Amendment 1) | `test_post-merge-followup-yml.sh` | Extension: Action 3 algorithm + bash mock simulation (13 fixture) + security T1/T2 verification |

## Byte-identity invariant section

**ADR-026 Amendment 1 §결정 5.B**: `templates/github-workflows/post-merge-followup.yml` ↔ `.github/workflows/post-merge-followup.yml` byte-identical. Invariant source = ADR-026 (not CFP-455 stale reference).

Test verification: `test_post-merge-followup-yml.sh` Block B `assert_files_identical` function.

## Coverage matrix (13 mandatory + 2 bonus fixture)

| # | Fixture key | Scenario summary | Expected outcome | Path diversity | Story §8.5 mapping | Status |
|---|---|---|---|---|---|---|
| 1 | cfp-391-false-positive | PR #400/#403 body missing `Closes #396` keyword | skip_no_close_keyword | bare #N absent (Source A fail) | UC-1 / EC-9 | ✓ |
| 2 | cfp-412-false-positive | PR #421 body missing `Closes #412` keyword | skip_no_close_keyword | bare #N absent (Source A fail) | UC-1 / EC-9 | ✓ |
| 3 | cfp-455-phase1-skip | Phase 1 PR #460 label `phase:설계-리뷰` | skip_phase1 / skip_not_terminal_phase | mid-phase block (terminal-phase gate fail) | UC-2 / EC-1 | ✓ |
| 4 | cfp-455-phase2-success | Phase 2 PR #461 label `phase:보안-테스트`, body `Closes #455`, closedByPullRequestsReferences=[#461] | success + `[close-success]` audit marker | bare #N happy path (Source A ∩ B non-empty) | UC-3 / AC-2 | ✓ |
| 5 | terminal-phase-success | `lanes.security_ai: false` consumer, label `phase:구현-테스트`, body `Closes #N` | success | terminal phase variant (security_ai=false → phase:구현-테스트) | UC-2.5 / AC-3 | ✓ |
| 6 | dual-source-mismatch | body `Closes #100` but closedByPullRequestsReferences=[] | skip_dual_source_mismatch + `[dual-source-mismatch]` audit | Source A✓ ∩ Source B✗ = empty (mismatch) | UC-4 / AC-4 | ✓ |
| 7 | multi-issue-warning-skip | body `Closes #100\nCloses #101` multiple issues | skip_multi_issue + `[multi-match-skip]` audit with detected_issues list | EC-4 (multi-match X✣∩Y detection) | AC-5 | ✓ |
| 8 | qualified-syntax-same-repo | body `Closes mclayer/plugin-codeforge#N` qualified same-repo | success | qualified same-repo syntax parsing | AC-6 | ✓ |
| 9 | qualified-syntax-cross-repo-skip | body `Closes other-org/other-repo#N` qualified cross-repo | skip_cross_repo_unsupported + `[cross-repo-skip]` audit | cross-repo limit (same-repo only) | EC-3 / AC-7 | ✓ |
| 10 | mid-phase-blocked | label `phase:구현-리뷰` (mid-phase variant) | skip_not_terminal_phase | 4 mid-phase label variant (구현, 구현-리뷰, 설계-리뷰, 설계) | UC-2 / EC-1 | ✓ |
| 11 | chore-pr-skip | PR title `chore(*):` prefix | skip_no_issue | guard preservation (line 50-65 existing Extract PR metadata logic) | UC-1 | ✓ |
| 12 | multi-cfp-aggregating-skip | PR title `CFP-N1 + CFP-N2` multiple CFP refs | skip_multi_issue | guard preservation (line 58-65 existing logic) | UC-1 | ✓ |
| 13 | source-b-lazy-sync | Source A normal + Source B `[]` initially, then retry succeeds (GitHub API propagation delay) | success | lazy timing (Source B eventual consistency) | UC-6 / AC-15 | ✓ |
| 14 | pr-title-with-singlequote | PR title `cfp-476: it's a fix` single quote escape | success | T2 mitigation regression (shell expansion prevention) | AC-16 | ✓ |
| 15 | idempotency-probe-dedupe | Same (PR, Issue) pair re-trigger workflow | success | AC-17 idempotency (audit comment pre-grep dedupe) | AC-17 | ✓ |

## Bash mock gap inventory (7 영역)

Test harness `tests/workflows/test_post-merge-followup-yml.sh` 가 workflow shell 로직 simulate. DeveloperPL workflow yml Action 3 `run:` block 을 `tests/scripts/post-merge-followup/action3-logic.sh` 로 추출 후 bash mock 분기 시뮬레이션.

| Area | Mock target | Input schema | Output schema |
|---|---|---|---|
| Area A | Source A regex extraction (close keyword + bare/qualified #N) | `PR_BODY`, `PR_TITLE` | `SOURCE_A_ISSUES=[#100, #101, ...]` |
| Area B | Source B (closedByPullRequestsReferences API) | `ISSUE_NUM` | `SOURCE_B_ISSUES=[#461, ...]` |
| Area C | dual-source AND (X ∩ Y) | SOURCE_A_ISSUES + SOURCE_B_ISSUES | `SHOULD_CLOSE=true/false`, `MISMATCH_REASON` |
| Area D | terminal-phase gate (label + consumer config `lanes.security_ai`) | `PHASE_LABEL`, `SECURITY_AI_ENABLED` | `SHOULD_CLOSE_GATED=true/false`, `GATE_REASON` |
| Area E | multi-issue dedupe (|X| > 1) | `SOURCE_A_ISSUES` size | `SKIP_REASON=multi_issue`, `CARRIER_ISSUE`, `DETECTED_ISSUES_JSON` |
| Area F | cross-repo limit (same-repo only) | `SOURCE_A_ISSUES` qualified syntax parse | `SKIP_REASON=cross_repo_unsupported`, `FOLLOW_UP_CARRIER` |
| Area G | audit comment formatting (4-marker namespace) | `SHOULD_CLOSE` + `SKIP_REASON` | `AUDIT_COMMENT_PREFIX` = `[close-success]` / `[multi-match-skip]` / `[cross-repo-skip]` / `[dual-source-mismatch]` |

## Sibling test harness reference

Fixture runner (bash mock) 는 prior art `test_evidence-registry-check-yml.sh` 패턴 재사용:
- assert_yaml_valid (2 workflow files)
- assert_files_identical (byte-identity)
- assert_contains (regex + keyword grep, 11 entry for algorithm verification)
- assert_yq_query (AC-16 security T1/T2 mitigation)
- custom bash_mock_run (13 fixture simulation, Area A-G)

## Notes for implementation (QADev turn)

1. DeveloperPL workflow yml 구현 완료 대기 (예상 ~19:35 KST)
2. Workflow yml 완료 후:
   - fixture/ 디렉토리 14 yml 신설
   - test harness bash mock area A-G 검증 logic 작성
   - Block A-F (YAML/byte-identity/Action 3 algorithm) grep assertion 작성
3. TEST-MAPPING coverage 표 위 Status column `✓` 로 업데이트
4. Story §8.5 cross-ref 정합성 확인

---

Generated: 2026-05-12 ~19:31 KST  
Last updated: (pending DeveloperPL workflow implementation)
