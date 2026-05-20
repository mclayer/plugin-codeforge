---
adr_number: 97
title: Paradigm replacement governance anchor — ADR-064 CFP scope unitary 면제 channel + 9-ADR bulk sunset carrier-preserved 개념 SSOT
status: Accepted
category: governance
date: 2026-05-21
carrier_story: CFP-1134
parent_epic: CFP-1111
related_stories:
  - CFP-1134     # 본 carrier (CFP-1111 Wave 1 Story-2, ADR-097 sub-Story #1 sequential first)
  - CFP-1111     # umbrella Epic
related_adrs:
  - ADR-064      # decision principle mandate — §결정 5 CFP scope unitary 면제 channel 연동 (Amendment 7 carrier)
  - ADR-058      # ADR sunset criteria mandate — §결정 5 sunset_justification ratchet 차단 정합
  - ADR-076      # declarative reconciliation upgrade — paradigm replacement 대상 paradigm 의 1st-class 정의 anchor
  - ADR-054      # doc-only fast-path — paradigm replacement = 신규 ADR 도입 governance behavior 변경 영역 (fast-path 비대상)
related_files:
  - docs/adr/ADR-064-decision-principle-mandate.md  # §결정 5 exception clause Amendment 7
  - docs/adr/ADR-RESERVATION.md                     # row 97 reserved → active 전환
  - CLAUDE.md                                       # ADR 단락 link + 결정 원칙 §결정 1 면제 channel cross-ref
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 (behavioral directive only, paradigm replacement = 저빈도 governance event, mechanical lint 비용 > 효용; pattern_count >= 2 재발 시 follow-up CFP MUST promote)
is_transitional: false  # permanent governance anchor — paradigm replacement 자체는 저빈도 event 이나 anchor (면제 channel + carrier-preserved sunset 개념) 는 future 재사용 permanent. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용
amendment_log: []
---

# ADR-097 — Paradigm replacement governance anchor

## 상태

`Accepted` (2026-05-21 KST) — CFP-1134 carrier (CFP-1111 Wave 1 Story-2, ADR-097 sub-Story #1 sequential first). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 CFP-899 precedent 정합 — chief author scope).

## 컨텍스트

### 동인

codeforge 의 governance 진화는 incremental amendment 가 default (ADR-064 §결정 5 CFP scope unitary — 한 CFP 안 "경량 → full" 단계 채택 금지, 별개 CFP 분리만 허용). 그러나 **paradigm-level replacement** — 기존 normative paradigm 전체를 다른 paradigm 으로 wholesale 대체하는 영역 — 은 incremental amendment 패턴에 들어맞지 않는다.

구체 trigger 사례 (CFP-1111 Wave 1 umbrella scope): declarative reconciliation paradigm (ADR-076) 을 imperative changelog walk paradigm 으로 전면 전환하는 후속 Epic 검토 영역. 이런 wholesale 전환은 단일 incremental amendment 로 표현 불가 — 기존 paradigm 을 떠받치는 9+ ADR/contract 가 동시에 sunset 되고, 대체 paradigm 의 새 anchor 묶음이 atomic 하게 도입돼야 한다.

여기서 두 governance 원칙이 표면적으로 충돌한다:

1. **ADR-064 §결정 5 (CFP scope unitary)** — 한 CFP 안 "경량 → full" 단계 채택 금지. paradigm replacement 는 단일 atomic Epic 안에서 9+ ADR/contract 를 동시에 sunset + 신설하므로, scope 가 단일 CFP 단위를 초과하는 것처럼 보인다.
2. **ADR-058 §결정 5 (amendment ratchet 차단)** — `is_transitional` ADR 의 약화 방향 amendment 차단. 9 ADR 동시 sunset 은 "여러 ADR 의 효력을 한 번에 종료"하므로 ratchet 약화처럼 보인다.

본 ADR 은 이 표면적 충돌이 **paradigm replacement 영역에서는 paradox 가 아님**을 governance anchor 로 codify 한다. 면제 channel (§결정 2) + carrier-preserved sunset 개념 (§결정 3) 두 mechanism 으로 해소.

> verified-via: Read docs/adr/ADR-064-decision-principle-mandate.md (L248-252 §결정 5 CFP scope unitary 본문 — "한 CFP 안에서 '경량 → full' 단계 채택 금지. 별개 CFP 분리는 허용" verbatim)
> verified-via: Read docs/adr/ADR-058-adr-sunset-criteria-mandate.md (L78-95 §결정 5 — "is_transitional: true ADR amendment 시 amendment_log entry 에 '왜 기존 sunset 미충족인지' 본문 명시 의무" + 옵션 B justification 의무 채택)

### CFP scope unitary §결정 번호 정합 (verify-via)

본 ADR 의 모든 cross-ref 는 ADR-064 본문 §결정 번호 기준이다. CFP scope unitary = **ADR-064 §결정 5** (본문 L248). CLAUDE.md `## 결정 원칙` 단락의 "결정 내용 (Trace 1)" 묶음 안 "CFP scope unitary" bullet 은 동일 결정의 narrative mirror 이며, ADR 본문 §결정 번호 (5) 가 SSOT 다. 본 ADR 은 ADR-064 §결정 5 를 정확 인용한다 (Trace 1 narrative grouping ≠ §결정 번호).

## 결정

### §결정 0 — preamble: 3 carry-over 보존 declare + 첫 적용 audit trail

본 ADR 신설 시점에 다음 3 carry-over invariant 를 명시 보존한다 (paradigm replacement 면제 channel 이 인접 governance layer 를 약화하지 않음을 박아두는 anchor):

1. **closed_enum open_extension:false 보존** — paradigm replacement scope boundary (§결정 1) 의 3 조건 (a/b/c) 은 closed-set. 면제 trigger 확장은 본 ADR amendment (강화 방향, ADR-058 §결정 5 sunset_justification 의무) 로만 가능 — runtime ad-hoc 확장 금지.
2. **ADR-026 Amendment 5 PR-gate layer 독립 보존** — paradigm replacement 의 atomic Epic 도 phase-gate-mergeable / post-merge-followup 등 PR-gate mechanical layer (ADR-026) 를 우회하지 않는다. 면제는 "CFP scope 단위" 면제이지 "PR gate" 면제 아님 (disjoint layer).
3. **ADR-067 disjoint invariant 보존** — Story progression layer (max FIX 3/3 RESET cap) ↔ paradigm replacement transaction layer 는 disjoint. paradigm replacement 의 다중-CFP coordination 이 ADR-067 RESET 룰을 변경하지 않는다 (ADR-076 §ADR-067 disjoint layer cross-ref 답습).

**첫 적용 audit trail**: 본 7-bundle (CFP-1111 Wave 1 Story-2 — ADR-092~098 7 ADR sibling carrier) 가 paradigm replacement 면제 channel 의 **첫 적용 사례**다. 단, 7-bundle 자체는 paradigm replacement 의 *governance anchor 묶음* (changelog SSOT / 4-field 보고 schema / fallback 정책 / sunset metric 표준화 / manifest schema / 본 anchor / UpgradeAgent ownership) 도입이며, declarative → imperative 전환의 *실 paradigm shift* 는 후속 Epic (별 carrier) 에서 본 anchor 를 인용해 진행한다. 본 anchor 신설 자체 = §결정 1 scope boundary (c) ratchet 강화 방향 (governance 표현력 확장).

### §결정 1 — paradigm replacement 정의 + scope boundary

**paradigm replacement** 정의: codeforge 의 기존 normative paradigm (예: declarative reconciliation — ADR-076) 을 다른 paradigm (예: imperative changelog walk) 으로 **wholesale 대체**하는 governance event. 단순 amendment (기존 paradigm 안 강화/확장) 와 disjoint — paradigm 의 근간 (desired-state 선언 vs imperative walk 절차) 자체가 교체된다.

**scope boundary** (closed-set 3 조건, AND — §결정 0 open_extension:false 정합):

| 조건 | 정의 | verify 신호 |
|---|---|---|
| **(a) 9+ ADR/contract 동시 sunset 동반** | 기존 paradigm 을 떠받치는 normative anchor 9 개 이상이 동시에 sunset (또는 supersede) 됨 | sunset 대상 ADR/contract 목록 enumeration + 각 효용 carry 경로 명시 (§결정 3 carrier-preserved 정합) |
| **(b) 단일 atomic Epic** | 전환이 단일 atomic Epic (다중 sub-Story sibling carrier) 안에서 진행 — sub-Story 간 sequential coordination 의무 (ADR-064 §결정 4 ordering invariant) | Epic Issue + N sub-Story + atomic merge order |
| **(c) ratchet 강화 방향 (carve-out, 약화 아님)** | 전환이 governance 효용을 lossless 보존 + 강화 방향 (β2 audit LOSSLESS evidence). 약화 방향 paradigm shift 는 본 면제 비대상 — ADR-058 §결정 5 sunset_justification 별도 의무 | β audit lossless 비율 9/9 (CFP-1113 carrier evidence) + ratchet direction declare |

3 조건 모두 충족 시에만 paradigm replacement = §결정 2 면제 channel 자격. 1+ 조건 부재 = 일반 amendment 영역 (ADR-064 §결정 5 unitary 원칙 그대로 적용 — 별개 CFP 분리 의무).

scope boundary 밖 (면제 비대상): 단일 ADR amendment / 단일 contract version bump / incremental layer 부착 / 기존 paradigm 안 강화. 이 영역은 ADR-064 §결정 5 CFP scope unitary 무조건 적용.

### §결정 2 — CFP scope unitary 면제 channel (ADR-064 §결정 5 Amendment 7 연동)

paradigm replacement (§결정 1 3 조건 충족) 영역은 ADR-064 §결정 5 "한 CFP 안 '경량 → full' 단계 채택 금지" 의 **면제**다. 단일 atomic Epic 안에서 9+ ADR/contract 동시 sunset + 신규 anchor 묶음 atomic 도입이 허용된다.

**exception clause 형식 (K-1 결정)**: 본 면제는 ADR-064 에 **별 §결정 신설이 아니라 §결정 5 본문 안 exception clause 추가**로 codify 한다 (ADR-064 Amendment 7 carrier — 본 ADR sibling). 이유:

- 면제는 §결정 5 (CFP scope unitary) 의 carve-out 이지 독립 결정이 아님 — §결정 5 본문 인접 배치가 reader 가독성 + drift 차단에 유리 (§결정 5 읽는 자가 면제 조건을 같은 자리에서 확인).
- 별 §결정 신설 = ADR-064 §결정 번호 inflation + cross-ref 표면 증가 (disjoint 결정으로 오인 risk).

**면제 = 명시적 carve-out (scope 약화 아님)**: 면제는 ADR-064 §결정 5 의 적용 범위를 좁히는 것이 아니라, paradigm replacement 라는 명시 영역에 대한 carve-out 이다. 일반 amendment 영역에서 §결정 5 의 강도는 0건 약화 — 면제는 scope boundary (§결정 1) 충족 영역에 한정. ADR-064 §결정 7 self-application top-down ratchet 정합 (governance 표현력 확장 = 강화 방향).

**sunset_justification 의무 (ADR-058 §결정 5 정합)**: 면제 channel 발동 (paradigm replacement Epic) 시, sunset 대상 9+ ADR 각각의 amendment_log entry 에 sunset_justification 명시 의무. 면제는 "sunset justification 면제"가 아니다 — 면제는 "단일 CFP scope 단위 초과 허용"이며, sunset 자체의 정당화 의무는 그대로 (§결정 3 carrier-preserved 개념이 sunset_justification 본문 내용).

### §결정 3 — 9-ADR 동시 sunset = carrier-preserved sunset (ADR-058 §결정 5 paradox 해소)

9 ADR/contract 동시 sunset = **bulk sunset**. 표면적으로 ADR-058 §결정 5 (약화 방향 차단) 와 충돌하는 것처럼 보인다 — "9 ADR 효력을 한 번에 종료 = ratchet 약화 9건". 본 §결정 이 이 paradox 를 해소한다.

**carrier-preserved sunset 개념**: bulk sunset 이 ratchet 약화가 **아닌** 조건 = sunset 되는 각 ADR 의 governance 효용이 대체 paradigm (예: imperative walker) 안으로 **lossless carry** 되는 경우. 효용 carrier 가 paradigm replace 후 reproduce 되면, 개별 ADR 의 sunset 은 "효용 소멸"이 아니라 "효용 이전 (carrier shift)"이다 — 강화 방향 (paradigm 전환으로 더 나은 표현/enforcement 획득).

| | sunset 의미 | ratchet 방향 | ADR-058 §결정 5 |
|---|---|---|---|
| **carrier-preserved sunset** (본 §결정) | 효용이 대체 paradigm carrier 로 lossless 이전 — sunset 은 carrier shift | 강화 (전환 후 표현력/enforcement 향상) | sunset_justification 본문 = 효용 carry 경로 명시 (paradox 해소) |
| **naive sunset** (면제 비대상) | 효용 소멸 — carrier 부재 | 약화 | ADR-058 §결정 5 차단 (별도 sunset_justification 의무, 면제 무자격) |

**lossless verify 의무**: bulk sunset 발동 시 각 ADR 의 효용 carry 경로를 enumeration + lossless 검증 의무. CFP-1113 β2 audit (LOSSLESS 9/9 evidence) 가 본 개념의 carrier evidence — 9 ADR 효용이 imperative walker 안으로 lossless carry 됨을 audit 으로 입증한 첫 사례. lossless 미달 (효용 carry 누락) ADR 은 bulk sunset 비대상 — 해당 ADR 은 면제 channel 밖, ADR-058 §결정 5 naive sunset 차단 무조건 적용.

본 carrier-preserved sunset 개념은 ADR-058 §결정 5 를 약화하지 않는다 — 오히려 §결정 5 의 "왜 기존 sunset 미충족인지" justification 의무를 paradigm replacement 영역에 specialize 한 형태 (justification 본문 = lossless carry 경로). ADR-058 §결정 5 의 ratchet 차단 mechanism 은 그대로 (carrier 부재 sunset = naive = 차단).

## 결과

### 긍정

- paradigm-level governance evolution 의 1st-class 표현 획득 — incremental amendment 패턴에 안 들어맞던 wholesale 전환을 명시 channel 로 codify.
- ADR-064 §결정 5 ↔ ADR-058 §결정 5 표면 충돌 (paradox) 해소 — 면제 channel + carrier-preserved sunset 2 mechanism.
- 면제 = carve-out (약화 아님) 박제 — 일반 amendment 영역 §결정 5 강도 0건 약화, scope boundary (§결정 1 closed-set 3 조건) 한정.
- 후속 paradigm shift Epic (declarative → imperative 등) 의 governance anchor 재사용 — permanent anchor.

### 부정 / trade-off

- paradigm replacement 면제 channel 오용 risk (일반 amendment 를 paradigm replacement 로 위장 → scope 폭발). 완화 = §결정 1 closed-set 3 조건 AND (특히 (a) 9+ ADR 동시 sunset + (c) lossless ratchet 강화) + DesignReview lane MUST flag 영역 (behavioral directive, Wave 1 declaration-only).
- carrier-preserved sunset 의 lossless verify 가 manual (β audit). mechanical enforcement Wave 1 부재 (`mechanical_enforcement_actions: []`) — pattern_count >= 2 재발 시 follow-up CFP MUST promote to mechanical lint (ADR-082 §결정 6 retain rationale 답습).
- paradigm replacement = 저빈도 governance event — 본 anchor 의 실 적용 빈도 낮음. 그러나 anchor 부재 시 매 paradigm shift 마다 ad-hoc paradox 재논쟁 = governance 비용. anchor 도입이 1회성 비용으로 future 재논쟁 차단 (trade-off 정당).

## 해소 기준

N/A — permanent policy (is_transitional: false). paradigm replacement governance anchor = 영구 거버넌스 정책. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: scope boundary 3 조건 강화 / carrier-preserved lossless verify mechanical 승격 / 면제 channel mechanical lint 추가). 약화 방향 (예: scope boundary 조건 축소 / 면제 channel 무자격 영역 확장 / closed_enum open_extension true 다운그레이드) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 아님 (category = governance, 보안 ADR default `false` presumption 무관).

## 관련 파일

- `docs/adr/ADR-064-decision-principle-mandate.md` — §결정 5 exception clause Amendment 7 (본 ADR sibling carrier)
- `docs/adr/ADR-RESERVATION.md` — row 97 reserved → active 전환
- `CLAUDE.md` — ADR 단락 link + 결정 원칙 §결정 1 (Trace 1) 면제 channel cross-ref
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — paradigm replacement 대상 paradigm 의 1st-class 정의 anchor (cross-ref)
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — §결정 5 sunset_justification ratchet 차단 정합 (cross-ref)
