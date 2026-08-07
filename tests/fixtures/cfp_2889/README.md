# CFP-2889 Captured-Golden Fixtures

## golden = 실측 산출물

`property_envelope_shape_golden.json` (shape golden) 과 `property_list_shape_golden.json` (list golden) 은 §9 step 4-6 실측(live write → captured-response) 의 산출물이다.

**합성 생성 금지.** Confluence v2 property API 와의 2-layer DTO contract (envelope 골격 + payload) 를 고정하기 위한 유일한 신뢰 출처는 실 API 응답이며, 테스트 bootstrap 단계(§9 step 1 — suite-A) 에서는 golden 부재가 정상이다.

## D-13 negative-control (suite-A bootstrap)

suite-A (`-m "not requires_golden"`) 실행 시 `requires_golden` marker 테스트는 **deselect** 된다 (마커 필터 — 실행 자체가 안 됨). golden 부재 시 "명시적으로 실패 (skip 하지 않음)" 거동은 마커 필터 없는 실행(full suite)에서 성립하며, D-13 negative-control (`test_d13_*`) 이 golden-부재 모사(`CFP2889_GOLDEN_DIR` override)로 그 거동 자체를 고정한다. golden 커밋 이후 full suite 실행 시 GREEN 이 된다. *(FIX iter1 F-CL-02 정정 — 구 서술 "suite-A 실행 시 명시적으로 실패" 는 실거동(deselect)과 불일치)*

- **suite-A (golden-비의존)**: D-1~D-6 + D-8~D-13 — golden 부재 상태에서 GREEN
- **suite-B (golden-의존, `@pytest.mark.requires_golden`)**: D-7 + shape/list replay 테스트 — golden 실존 필요

## provenance

- [empirical-source: 2026-08-06T06:02:00+09:00, v2 property CRUD (measure run), RECONCILED, tenant=redacted, run_id=20260806T060155] — §9 step 4-6 실측 완료 (FIX iter1 F-CL-03 갱신)
- **갱신 트리거 2종 (§3.9 정밀화 註 — 보안테스트 FIX iter1 정정)**: ① 실 재측정 **또는** ② 값-축 sanitize 규칙의 소급 적용. ②는 "합성 편집 금지"(= 측정치 변조 금지, anti-fabrication 축) 위반이 **아니며**, 허용 조건은 **키·중첩·타입·수치 불변** + 치환 필드명 병기다. 구 문언 "재갱신 = 실 재측정 시에만" 은 본 정정으로 대체된다.

## redaction 이력 (보안테스트 FIX iter1, 2026-08-06 — finding F3 P1)

shape/list golden 에 서버 유래 `authorId`(Atlassian account id) 가 유입돼 있었고 **repo 가 PUBLIC** 이었다. §3.9 값-축 3분류 allowlist 를 **소급 적용**했다 (production 빌더와 **동일 함수** `sanitize_golden_values` 재사용 — 소급용 로직 2벌 금지). **단 상수는 동일하지 않다**: 소급 1회에 한해 `value` 를 value-allow 로 **추가 지정**했다 — production 상수(`SHAPE_GOLDEN_VALUE_ALLOW` 에 `value` 미포함 · `SHAPE_GOLDEN_PAYLOAD_PATHS=("value",)`)를 그대로 적용하면 이미 digest 인 값이 재-digest 돼 수치가 변조된다(아래 3번째 bullet). 따라서 커밋본은 "함수 동일 · 인자 1건 예외" 의 산물이며, production 상수만으로는 재현되지 않는다.

| 파일 | 치환 필드 | 보존(측정치 무변조) |
|---|---|---|
| `property_envelope_shape_golden.json` | `version.message` · `version.minorEdit` · `version.authorId` · `version.createdAt` | `id` · `key` · `version.number` · `value`(b64 digest) · `empirical_source` · `endpoint_omitted_by_validator` |
| `property_list_shape_golden.json` | `results[0].version.{message,minorEdit,authorId,createdAt}` · `_links.base`(tenant 호스트) | 동일 + `results[0].id` |

- `_links.base` 치환은 provenance 의 `tenant=redacted` 규약과 list golden 실물 사이의 **기존 자기모순**도 함께 해소한다.
- **`value` 는 value-allow 로 보존**했다 — 이미 digest 치환된 값이라 재투입하면 `redact_payload` 가 digest 를 재계산해(`len=184` → `29`) **수치가 변조**된다 (실측 확인).
- 본 클래스는 emit 파이프라인 deny-scan 이 잡지 못한다 (account-id 형 `<digits>:<uuid>` 는 `:`·`-` 로 분절돼 20+ run 미형성) — **allowlist 가 유일 차단층**이고 deny-scan 은 이 축의 backstop 이 아니다.
- `measurement_basis_golden.json` 의 `v2_control_status: null` = W4 control write 가 **성공**해 오류 status 가 없었다는 뜻 (미실행 아님 — run NDJSON `overlimit-control` cleanup 레코드의 `ok`+`property_id` 가 실행·성공을 증거, `test_basis_control_status_null_disambiguated_by_ndjson` 결박). future-run 부터 emit 이 `v2_control_write_success` 필드를 동반 기록한다 (F-CL-07).

## fuzz_corpus/ (합성 seed — §3.9 비적용)

`fuzz_corpus/` 하위 seed 는 **synthetic seed, not captured** — §3.9 captured-golden 규약 비적용 (상세 = `fuzz_corpus/README.md`). captured-golden 3종·run NDJSON 과 규약이 다르므로 혼동 금지.
