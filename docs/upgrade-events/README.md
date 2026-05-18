# docs/upgrade-events/ — upgrade event log artifact schema

CFP-900 Phase 2 — reconcile-protocol-v1 v1.10 §4.13 `upgrade_event_honest_record` carrier.

## 목적

`scripts/reconcile-overlay.sh` 실행 후 result enum 4-value 집계 결과를 영속 artifact 로 기록.
`result: SUCCESS` hardcode 금지 — exit code → result enum deterministic mapping 의무.

## artifact naming 규칙

```
docs/upgrade-events/<YYYY-MM-DD>-<version>.json
예: docs/upgrade-events/2026-05-18-5.91.0.json
```

`--output-file` 환경 변수 `RESULT_FIDELITY_OUTPUT_FILE` 로 경로 주입 가능 (test seam).

## result enum 4-value schema

```json
{
  "result": "<SUCCESS | SUCCESS_WITH_DEGRADATION | PARTIAL_FAILURE | FAILED>",
  "s1_exit": "<int: S1 §4.11 closure resolver exit code>",
  "s2_exit": "<int: S2 §4.12 consumer-applicability filter exit code>",
  "sanity_check": "<PASS | PARTIAL_MISMATCH | WARNING>",
  "sanity_warnings": ["<string>", ...]
}
```

## result enum 의미 (§4.13 degradation_propagation SSOT verbatim)

| result | 의미 | trigger |
|---|---|---|
| `SUCCESS` | 전 영역 mirror + 0 degradation | S1 exit 0 + S2 exit 0 + sanity PASS |
| `SUCCESS_WITH_DEGRADATION` | mirror 완료 but warning 발생 | S1/S2 exit 2 (degraded) OR sanity WARNING |
| `PARTIAL_FAILURE` | 일부 영역 skip | S1 partial OR sanity PARTIAL_MISMATCH |
| `FAILED` | mirror abort | S1 exit 1 (fail-closed) OR S2 exit 1 (unknown abort) |

## EC 규칙

- **EC-1**: S1 + S2 동시 abort → `FAILED` 우선 (가장 심각 enum 우선, abort > partial)
- **EC-2**: dry-run mode → result field 미적용 (preview only, ADR-076 §결정 3)
- **EC-3**: wrapper self-app mixed repo (S2 filter skip) + S1 OK → `SUCCESS`

## 관련 SSOT

- `reconcile-protocol-v1.md` §4.13 `result_fidelity_binding` (v1.10, CFP-900)
- `templates/scripts/result-fidelity-aggregator.py` — result enum 집계 logic
- `scripts/reconcile-overlay.sh` — hook_integration step_4 (cp 후 post-mirror sanity + 집계)
- ADR-076 Amendment 3 §결정 3 sub-clause — transaction 사후 sanity check + result fidelity false SUCCESS 차단
