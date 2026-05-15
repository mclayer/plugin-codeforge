# tests/scripts/check-evidence-registry-anomaly/

CFP-442 Phase 2 / ADR-060 Amendment 11 §결정 25 — evidence-registry anomaly lint 테스트 suite.

## TC 매핑표

| TC | fixture | Expected | 상태 |
|---|---|---|---|
| TC-1 | `fixtures/01-positive-current-state.yaml` | exit 0 (PASS) — Group A 18 entry 전체 포함 | mandatory |
| TC-2 | `fixtures/02-negative-registry-missing-entry.yaml` | exit 1 (anomaly DETECTED) — lane-evidence-trail 누락 | mandatory |
| TC-3 | 현행 SSOT 활용 (fixture-less in-place) | exit 0 (PASS) — ALLOWLIST 4-path self-exempt 통과 | mandatory |
| TC-4 | `fixtures/04-negative-fake-new-lint.sh` + `04-negative-fake-new-lint-check.yml` + `04-negative-registry-no-fake.yaml` | exit 1 (anomaly) — sub-check 2 fake lint 미등록 감지 | optional |
| TC-5 | `fixtures/05a-meta-error-yaml-parse-fail.yaml` | exit 2 (META-ERROR) — broken yaml parse fail | optional |

## 실행 방법

```bash
# pytest 전체 실행
cd <worktree-root>
python -m pytest tests/scripts/check-evidence-registry-anomaly/test_check_evidence_registry_anomaly.py -v

# 개별 TC
python -m pytest tests/scripts/check-evidence-registry-anomaly/test_check_evidence_registry_anomaly.py::test_tc1_positive_current_state -v
python -m pytest tests/scripts/check-evidence-registry-anomaly/test_check_evidence_registry_anomaly.py::test_tc2_negative_missing_entry -v
python -m pytest tests/scripts/check-evidence-registry-anomaly/test_check_evidence_registry_anomaly.py::test_tc3_allowlist_self_exempt -v
```

## 의존성

- `pyyaml` (`python3 -m pip install --user pyyaml`)
- worktree root 에서 실행 (ALLOWLIST 4-path assertion 통과 위해)

## SSOT 참조

- ADR-060 Amendment 11 §결정 25: `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` line 1101+
- Change Plan §3: `codeforge-internal-docs/wrapper/change-plans/2026-05-14-cfp-442-evidence-registry-anomaly-lint.md`
