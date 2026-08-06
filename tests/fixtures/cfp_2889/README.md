# CFP-2889 Captured-Golden Fixtures

## golden = 실측 산출물

`property_envelope_shape_golden.json` (shape golden) 과 `property_list_shape_golden.json` (list golden) 은 §9 step 4-6 실측(live write → captured-response) 의 산출물이다.

**합성 생성 금지.** Confluence v2 property API 와의 2-layer DTO contract (envelope 골격 + payload) 를 고정하기 위한 유일한 신뢰 출처는 실 API 응답이며, 테스트 bootstrap 단계(§9 step 1 — suite-A) 에서는 golden 부재가 정상이다.

## D-13 negative-control (suite-A bootstrap)

suite-A (`-m "not requires_golden"`) 실행 시 `requires_golden` marker 테스트는 **deselect** 된다 (마커 필터 — 실행 자체가 안 됨). golden 부재 시 "명시적으로 실패 (skip 하지 않음)" 거동은 마커 필터 없는 실행(full suite)에서 성립하며, D-13 negative-control (`test_d13_*`) 이 golden-부재 모사(`CFP2889_GOLDEN_DIR` override)로 그 거동 자체를 고정한다. golden 커밋 이후 full suite 실행 시 GREEN 이 된다. *(FIX iter1 F-CL-02 정정 — 구 서술 "suite-A 실행 시 명시적으로 실패" 는 실거동(deselect)과 불일치)*

- **suite-A (golden-비의존)**: D-1~D-6 + D-8~D-13 — golden 부재 상태에서 GREEN
- **suite-B (golden-의존, `@pytest.mark.requires_golden`)**: D-7 + shape/list replay 테스트 — golden 실존 필요

## provenance

- [empirical-source: 2026-08-06T06:02:00+09:00, v2 property CRUD (measure run), RECONCILED, tenant=redacted, run_id=20260806T060155] — §9 step 4-6 실측 완료 (FIX iter1 F-CL-03 갱신. 재갱신 = 실 재측정 시에만, §3.9)
- `measurement_basis_golden.json` 의 `v2_control_status: null` = W4 control write 가 **성공**해 오류 status 가 없었다는 뜻 (미실행 아님 — run NDJSON `overlimit-control` cleanup 레코드의 `ok`+`property_id` 가 실행·성공을 증거, `test_basis_control_status_null_disambiguated_by_ndjson` 결박). future-run 부터 emit 이 `v2_control_write_success` 필드를 동반 기록한다 (F-CL-07).

## fuzz_corpus/ (합성 seed — §3.9 비적용)

`fuzz_corpus/` 하위 seed 는 **synthetic seed, not captured** — §3.9 captured-golden 규약 비적용 (상세 = `fuzz_corpus/README.md`). captured-golden 3종·run NDJSON 과 규약이 다르므로 혼동 금지.
