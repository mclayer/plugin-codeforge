# walk-entry 스키마 정의

`docs/walk-entries/` 디렉토리는 `reconcile-protocol-v1` (v1.13 Deprecated, CFP-1125) 의
선언적 §4.x 바인딩을 **명령형 walk-entry** 로 재표현한 YAML 파일 모음이다.

## 목적

ADR-097 §결정 3 carrier-preserved sunset 을 인스턴스화한다.
`reconcile-protocol-v1` §4.x 바인딩이 Story-11 에서 sunset 될 때,
각 바인딩이 가진 실질적 효용이 imperative walk-entry 로 lossless 이전된다.

## walk-entry YAML 필드 정의

```yaml
walk_entry_id:     # 문자열. 고유 식별자 (예: "WE-CFP-906-multi-version-channel")
paradigm:          # 고정 값: "imperative-walk"
carrier_cfp:       # 문자열. 이 entry 를 실제로 구현한 원본 CFP (예: "CFP-906")
carrier_prs:       # 문자열 목록. 병합된 PR / 커밋 참조 (역사 불변 — 변조 금지)
source_binding:    # 문자열. carry 대상 reconcile-protocol-v1 §4.x 바인딩 명칭
source_section:    # 문자열. reconcile-protocol-v1 내 섹션 참조 (예: "§4.10")
carry_fidelity:    # 고정 값: "lossless" (ADR-097 §결정 3 정합)
history_immutable: # 고정 값: true — carrier_prs 가 가리키는 병합 기록은 변조 불가
walk_result_mapping:         # 선언적 바인딩 결과 → imperative walker §2.A walk_result 매핑
  SUCCESS:         # 문자열. 성공 조건 설명
  SUCCESS_WITH_DEGRADATION: # 문자열. 저하 조건 설명 (해당 시)
  PARTIAL_FAILURE: # 문자열. 부분 실패 조건 설명 (해당 시)
  FAILED:          # 문자열. 실패 조건 설명
walk_steps:        # 목록. 선언적 바인딩의 효용을 재현하는 명령형 단계들
  - step_id:       # 문자열. 단계 식별자
    description:   # 문자열. 단계 설명
    check_command: # 문자열 (선택). 검증 명령
    failure_mode:  # 문자열 (선택). 실패 시 walker 행동
invariants_preserved: # 목록. 원본 바인딩의 핵심 불변 조건 (closed_enum, 경계 등)
open_extension:    # 고정 값: false — walk_step 목록 임의 확장 금지 (walker contract ADR-093 §결정 2 정합)
```

## closed_enum / open_extension 정책

- `walk_result_mapping` 의 enum 값 = imperative-walker-protocol-v1 §2.A.1 4-value closed_enum
  (`SUCCESS` / `SUCCESS_WITH_DEGRADATION` / `PARTIAL_FAILURE` / `FAILED`) 그대로 사용.
  5번째 enum 값 신설 = ADR-093 amendment (강화 방향) 으로만 가능.
- `open_extension: false` = 각 walk-entry 의 `walk_steps` 임의 확장 금지.
  확장 시 walk-entry YAML 개정 + 본 스키마 버전 갱신 의무.

## 참조

- imperative-walker-protocol-v1 §2.A (walk_result schema): `docs/inter-plugin-contracts/imperative-walker-protocol-v1.md`
- ADR-097 §결정 3 carrier-preserved sunset: `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md`
- reconcile-protocol-v1 (v1.13 Deprecated): `docs/inter-plugin-contracts/reconcile-protocol-v1.md`
