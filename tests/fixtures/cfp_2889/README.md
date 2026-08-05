# CFP-2889 Captured-Golden Fixtures

## golden = 실측 산출물

`property_envelope_shape_golden.json` (shape golden) 과 `property_list_shape_golden.json` (list golden) 은 §9 step 4-6 실측(live write → captured-response) 의 산출물이다.

**합성 생성 금지.** Confluence v2 property API 와의 2-layer DTO contract (envelope 골격 + payload) 를 고정하기 위한 유일한 신뢰 출처는 실 API 응답이며, 테스트 bootstrap 단계(§9 step 1 — suite-A) 에서는 golden 부재가 정상이다.

## D-13 negative-control (suite-A bootstrap)

§9 step 1 에서 suite-A (`-m "not requires_golden"`) 를 실행할 때, `requires_golden` marker 가 있는 테스트는 **명시적으로 실패**한다 (skip 하지 않음). 이것이 정상 거동이며, golden 커밋 이후 suite-B 를 포함한 full suite 를 실행할 때 GREEN 이 된다.

- **suite-A (golden-비의존)**: D-1~D-6 + D-8~D-13 — golden 부재 상태에서 GREEN
- **suite-B (golden-의존, `@pytest.mark.requires_golden`)**: D-7 + shape/list replay 테스트 — golden 실존 필요

## provenance

- [empirical-source: TBD → §9 step 4-6 실측 후 갱신]
