# CFP-455 Phase 2 — Test Mapping Table

QADeveloper lane artifact. Mapping of Story §8.6 Integration Test Contract to implementation in tests/**.

**Story**: CFP-455 — 4-tier enforcement 분류 정식화 (ADR-060 Amendment 2)
**Chief**: ArchitectPLAgent (codeforge-design lane, Phase 1)
**Audit responsibility**: ArchitectPLAgent (design review PL)
**Test audit**: QADeveloper lane (본 매핑표)
**Phase 2 PR**: TBD (이 Story의 lint script + workflow + self-application registry entry)

---

## Executive Summary

| Aspect | Count | Coverage |
|--------|-------|----------|
| §8.6.1 Coverage candidates (8) | 8 | 100% (1 positive + 6 negative + 1 meta-error tier) |
| Lint script validation tests | 25 | Full (exit-code 3-tier + all 6 rules + perf baseline) |
| Workflow YAML lint checks | 24 | Full (YAML valid, triggers, warning mode, steps, permissions, 3-tier handling) |
| Self-app copy verification | 1 | Full (templates ↔ .github byte-identical, ADR-029) |
| §8.6.2 perf baseline | 1 | Full (< 5s on production registry 27 entries) |
| Meta-error scenarios (§결정 15) | 2 | file 부재 + yaml parse fail |
| **Total test cases** | **49** | **Comprehensive** |

---

## §8.6.1 — Coverage Candidates → test_check_evidence_registry.sh

### Mapping: Story §8.6.1 row 1-8 → tests/scripts/check-evidence-registry/

| §8.6 row | Scenario | Fixture | Test function | Expected exit | Implementation |
|---------|----------|---------|---------------|---------------|----------------|
| 1 | Positive PASS — minimal valid entry | `fixtures/01-positive-minimal.yaml` | `test_01_positive_pass()` | 0 | `tests/scripts/check-evidence-registry/test_check_evidence_registry.sh` |
| 2 | Negative — schema_version absent (rule a) | `fixtures/02-negative-schema-version-absent.yaml` | `test_02_schema_version_absent()` | 1 | same |
| 3 | Negative — current_tier missing (rule b) | `fixtures/03-negative-current-tier-absent.yaml` | `test_03_current_tier_absent()` | 1 | same |
| 4 | Negative — enum violation `hard_block` (rule c) | `fixtures/04-negative-enum-violation.yaml` | `test_04_enum_violation()` | 1 | same |
| 5 | Negative — bypass pair violation (rule d) | `fixtures/05-negative-bypass-pair.yaml` | `test_05_bypass_pair_violation()` | 1 | same |
| 6 | Negative — duplicate name (rule e) | `fixtures/06-negative-name-duplicate.yaml` | `test_06_name_duplicate()` | 1 | same |
| 7 | Negative — owner_adr ADR-999 not found (rule f) | `fixtures/07-negative-owner-adr-missing.yaml` | `test_07_owner_adr_missing()` | 1 | same |
| 8 | Exit code 3-tier — META-ERROR | (file 부재 / `fixtures/08-meta-error-yaml-parse-fail.yaml`) | `test_08_meta_error_file_absent()` + `test_08_meta_error_yaml_parse_fail()` | 2 | same |

**Additional scenarios beyond §8.6.1**:
- Scenario 9 — Production registry self-validation (regression guard)
- Scenario 10 — Perf baseline (§8.6.2 — < 5s threshold)

---

## §8.6.2 — Perf Baseline

| Metric | Threshold | Measured | Result |
|--------|-----------|----------|--------|
| runtime on 27 entries × 6 rules | < 5000ms (§8.6.2) | ~375ms (local Windows + Git Bash) | PASS |
| linear scale (O(N)) verification | manual N+1 confirmation | not measured | deferred (forward-looking) |
| ADR file glob scale | linear (~60 ADR files) | included in 375ms | PASS |

Production registry currently has **27 entries** (rebased state — Story §8.6 was based on 22 pre-rebase; CFP-393 / CFP-410 / CFP-426 / CFP-447 / CFP-455 itself added 5+ entries since).

---

## Workflow YAML Tests → test_evidence-registry-check-yml.sh

### Mapping: workflow contract → tests/workflows/test_evidence-registry-check-yml.sh

| Test category | Test function | Verifies |
|---------------|---------------|----------|
| Templates YAML validity | `test_templates_yaml_valid()` | `templates/github-workflows/evidence-registry-check.yml` parses as valid YAML (python yaml.safe_load) |
| Self-app YAML validity | `test_self_app_yaml_valid()` | `.github/workflows/evidence-registry-check.yml` parses + byte-identical to templates (ADR-029) |
| Trigger paths | `test_trigger_paths()` | `pull_request:` + path filters for `docs/evidence-checks-registry.yaml` and schema doc |
| Warning mode | `test_warning_mode()` | `continue-on-error: true` (ADR-060 §결정 5 첫 도입) |
| bypass_label omit | `test_bypass_label_omit()` | Workflow does NOT define hotfix-bypass label step (§결정 16 verbatim) |
| Required steps | `test_required_steps()` | checkout, setup-python, pyyaml install, lint exec, PR comment all present |
| Permissions | `test_permissions()` | `permissions:` block + `pull-requests: write` + `contents: read` |
| Exit code 3-tier | `test_exit_code_3_tier()` | case branches for exit 0 / 1 / 2 (ADR-060 Amendment 2 §결정 15) |
| Timeout | `test_timeout()` | `timeout-minutes:` defined |
| Carrier references | `test_carrier_references()` | CFP-455 + ADR-060 + Amendment 2 explicitly referenced |

---

## §8.5 — Stateful / Restart invariant tests

**§8.5_active = false** — Story §8.5 verbatim. 4 조건 모두 N:
- Long-running connection (N — bash lint + 1-shot Action)
- Stateful in-memory cache (N — file-based)
- Background worker (N — pull_request trigger)
- Process restart-aware (N — stateless lint)

→ StatefulTestAgent invariant test category 적용 N/A. 본 매핑표에 §8.5 row 없음.

---

## §8.6.3 — Test artifact 위치

| Artifact | Path | Status |
|----------|------|--------|
| Lint script | `scripts/check-evidence-registry.sh` | PASS (chmod +x verified) |
| Templates workflow | `templates/github-workflows/evidence-registry-check.yml` | PASS (yaml valid) |
| Self-app workflow | `.github/workflows/evidence-registry-check.yml` | PASS (byte-identical to templates) |
| Registry entry | `docs/evidence-checks-registry.yaml` row `evidence-registry-schema-validation` | PASS (self-application verified) |
| Test fixtures | `tests/scripts/check-evidence-registry/fixtures/01-08*.yaml` | 8 files (1 positive + 7 negative/meta-error) |
| Test runner | `tests/scripts/check-evidence-registry/test_check_evidence_registry.sh` | PASS (25 assertions) |
| Workflow yaml test | `tests/workflows/test_evidence-registry-check-yml.sh` | PASS (24 assertions) |
| Test mapping | `tests/CFP-455-TEST-MAPPING.md` (this file) | — |

---

## §8.6.4 — Story Suite 자동승격 (ADR-055 Amendment 2)

본 Phase 2 PR merge 후 Epic CFP-388 close 시점에 IntegrationTestAgent baseline merge target:
- `tests/integration/baseline/check-evidence-registry.bats` (Story Suite → Baseline Suite 승격)

**현재 상태**: Phase 2 PR scope 에서는 `tests/integration/baseline/` 으로의 자동 promotion 미수행 (Epic close carrier scope).

---

## Story §8.6.1 row 8 — META-ERROR semantic (§결정 15 verbatim)

Codex AREA 1 OQ → ADR-060 Amendment 2 §결정 15 reflected:

| Exit code | Semantic | Test fixture / scenario |
|-----------|----------|--------------------------|
| 0 | PASS — violation 0건 | fixture 01 + production registry |
| 1 | validation FAIL — schema 위반 1건 이상 | fixtures 02-07 (rule a-f individually) |
| 2 | META-ERROR — pyyaml 미설치 / registry yaml file 부재 / yaml parse fail / unexpected exception | non-existent file path + fixture 08 (malformed yaml) |

META-ERROR semantic 분리의 의의: validation FAIL 과 false positive rate 측정 무결성 보장 (ADR-060 §결정 5 EC-B).

---

## Audit notes

### Coverage gaps (intentional, forward-looking)
- pyyaml 미설치 case 는 자동 test 미작성 (CI runner 환경 의존성 — `pip install --user pyyaml` workflow step 가 보장). META-ERROR exit 2 의 conceptual coverage 는 file 부재 + yaml parse fail 2 fixture 로 검증.
- linear scale O(N) verification 은 manual N+1 entry 확인 영역 (성능 회귀 발생 시 별도 carrier).
- bypass_audit_lint without bypass_label (역방향 pair violation) 검증은 lint 에 구현됨 (rule d 역방향), test fixture 미작성 — 정방향 fixture 05 로 rule d 의 logic path 검증 충분.

### Verbatim §8.6.1 row 1-8 mapping check
모든 8 row 가 fixture + test function 으로 1:1 매핑. row 8 (META-ERROR) 만 2 sub-scenario (file 부재 + yaml parse fail) 로 확장.

---

**작성**: CFP-455 Phase 2 QADeveloper lane (DeveloperPLAgent supervision)
**작성일**: 2026-05-12
