---
adr_number: 104
title: 운영 phase 1st-class 정의 — 배포검토 이후 ongoing 신호 회수 mechanism layer (lane 아님) + 0 API call / wrapper-N/A invariant
status: Accepted
category: governance
date: 2026-05-22
carrier_story: CFP-1190
parent_epic: CFP-1187
related_stories:
  - CFP-1190     # 본 carrier (Epic CFP-1187 Story-1, 운영 phase 1st-class 정의 anchor)
  - CFP-1187     # umbrella Epic — 운영 phase 신설
related_adrs:
  - ADR-087      # Deploy lane 신설 (lane lifecycle 6→8) — 운영 phase 는 그 disjoint 후속 (release lifecycle 위치)
  - ADR-088      # Deploy Review lane 신설 ("한 번 끝나는 검증" — 운영 phase 와 disjoint, §결정 3 + L81 "운영 phase 8 후보 = 별 Epic carrier" 가 본 Epic origin)
  - ADR-083      # 직접 제약 — filesystem-only signal invariant (network call 0 / gh api 0) — 0 API call constraint 의 동형 source
  - ADR-045      # §D-9 cross-Story pattern_count ≥ 2 → ADR escalation forcing function — self-improving loop narrative 답습 source
  - ADR-72       # ProductionEvidenceDeputy + wrapper-self-app Tier-1 declare-time exemption — wrapper-N/A invariant 패턴 source (file명 = ADR-72 2-digit form, ADR-088 precedent 정합)
  - ADR-023      # lane plugin lifecycle — lane count invariant (운영 phase = 9번째 lane 아님 정합)
  - ADR-054      # doc-only fast-path — 본 Story 는 신규 정의 ADR 포함 → fast-path 비대상 (full-lane)
  - ADR-064      # 모달 어휘 forbid-list — 운영 신호 정량 (숫자 임계) 원칙 정합
  - ADR-057      # consumer overlay 정책 축소 불가 — 0 API call / wrapper-N/A invariant 축소 차단
  - ADR-084      # pattern_count ≥ 2 재발 시 mechanical promote precedent (frontmatter clause 형식)
related_files:
  - docs/adr/ADR-RESERVATION.md                                              # row 104 reserved → active 전환
  - docs/domain-knowledge/domain/operational-phase/README.md                 # narrative SSOT hub (Phase 2 carrier)
  - docs/domain-knowledge/domain/operational-phase/operational-phase-definition.md  # lifecycle 위치 + lane vs mechanism (Phase 2 carrier)
  - docs/domain-knowledge/domain/operational-phase/measurement-channel.md    # 0 API call constraint (Phase 2 carrier)
  - docs/domain-knowledge/domain/operational-phase/self-improving-loop.md    # loop narrative + closure gate 위험 (Phase 2 carrier)
  - docs/domain-knowledge/domain/production-cutover/README.md                # 5-stage channel distribution taxonomy ↔ 본 ADR 시간축 taxonomy disambiguation 대상
  - CLAUDE.md                                                                # L84 "운영 phase 와 disjoint" forward-reference 의 referent (의미 변경 0)
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-082 §결정 6 / ADR-070 §D5 / ADR-076 / ADR-086 / ADR-097 retain pattern 답습 (behavioral directive only, 운영 phase = 신규 정의 layer / 실 mechanism 은 S4~S7 carrier 가 신설 시 evidence-checks-registry row append; pattern_count >= 2 recurrence 시 follow-up CFP MUST promote to mechanical lint — ADR-084 precedent)
is_transitional: false  # permanent governance anchor — ADR-087/088 (lane lifecycle, is_transitional: false) 정합. 운영 phase 정의 (lifecycle 위치 / mechanism layer / 0 API call / wrapper-N/A / self-improving loop) 는 future 재사용 permanent. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (scope 확장 / 강도 강화)
amendment_log: []
---

# ADR-104 — 운영 phase 1st-class 정의

## 상태

`Accepted` (2026-05-22 KST) — CFP-1190 carrier (Epic CFP-1187 Story-1, 운영 phase 1st-class 정의 anchor). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 / ADR-097 row 97 chief author precedent 정합).

## 컨텍스트

### 동인

codeforge 는 Epic CFP-1059 (CLOSED) 에서 배포(deploy) + 배포검토(deploy-review) lane 을 신설했다 (ADR-087 / ADR-088). 그러나 "배포가 끝난 뒤에도 **계속 돌면서** 배포 때 약속한 성능·안정성이 실제 지켜지는지 감시하고, 문제 시 자동으로 되돌리는(rollback)" 단계 — **운영 phase** — 가 1st-class 개념으로 정의돼 있지 않다.

증거 — ADR-088 §결정 3 (`docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md` L101-109) 이 배포검토 lane scope 를 "한 번 끝나는 검증" 만으로 명시하면서, ADR-088 본문 (동 file L81) 이 "운영 phase 8 후보 (canary promote / rollback 신호 회수 / 사용자 피드백 / regression 감지 / channel drift / 우선순위 입력 / cutover monitoring / smoke ongoing) = **별 Epic carrier** (본 Epic close 후 발의)" 를 명시한다. 본 Epic CFP-1187 가 정확히 그 carrier 다. 또 wrapper CLAUDE.md L84 가 "배포 리뷰 lane = production smoke / 성능 비교 / cutover 사후 검증 (한 번 끝나는 — **운영 phase 와 disjoint**)" 라는 forward-reference 를 보유하나, "운영 phase" 의 1st-class 정의는 부재. 본 ADR 이 그 forward-reference 의 **referent** 를 채운다 (CLAUDE.md L84 의 disjoint 의미는 변경하지 않는다 — §결정 1 / boundary I-2 참조).

### 근본 mismatch

운영 phase 의 시간축 ongoing 성격 ↔ codeforge 의 기존 8 lane 구조 (Story-scoped: delta + 종료 게이트, CLAUDE.md "1 Story = Phase 1 PR (§1-7) + Phase 2 PR (§8-11)") 사이의 mismatch 가 본 정의의 핵심이다. lane 은 "한 Story 가 들어가서 게이트를 통과하고 끝나는" 구조이나, 운영 phase 는 "시간축에서 계속 도는" 구조다. 이 mismatch 를 9번째 lane 신설로 해소하면 ADR-023 lane count invariant (6→8 = scope 확장 only) 와 충돌하고, lane 의 종료-게이트 의미가 무너진다. 따라서 운영 phase 는 **lane 이 아니라 mechanism layer** (monitor / alert / 자동 Issue 생성) 로 정의된다 (§결정 2).

## 결정

운영 phase 를 codeforge 의 1st-class 개념으로 정의한다. 정의는 아래 5 substantive invariant + 1 disambiguation 표로 구성된다. 본 ADR 이 normative SSOT 이고, `docs/domain-knowledge/domain/operational-phase/` 4 파일 (Phase 2 carrier) 은 서술적 elaboration (narrative) 이다 — ADR 이 결정, domain-knowledge 가 해설.

### §결정 1 — release lifecycle 위치 (배포 → 배포검토 → 운영 phase)

운영 phase 는 codeforge release lifecycle 의 **시간축 마지막 ongoing 단계**다:

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포(deploy) → 배포검토(deploy-review) → [운영 phase: ongoing 신호 회수]
```

- **배포검토 lane (ADR-088)** = 일회성 검증 — production smoke / 성능 비교 / cutover 사후 검증. "한 번 끝나는" (ADR-088 §결정 3, L109).
- **운영 phase (본 ADR)** = 배포검토가 끝난 *그 이후* 시간축에서 **지속(ongoing)** 감시. 배포 때 약속한 성능·안정성이 시간이 지나도 지켜지는지를 계속 회수한다.

두 영역은 disjoint 하다 (CLAUDE.md L84 forward-reference 의 referent). 경계 기준은 시간 성격: **"한 번 끝나는" = 배포검토 / "계속 도는" = 운영 phase**.

### §결정 2 — lane 아님 (mechanism layer) — ADR-023 lane count invariant 정합

운영 phase 는 **9번째 lane 이 아니다**. codeforge 의 lane 은 Story-scoped (delta + 종료 게이트) 구조인데, 운영 phase 의 시간축 ongoing 성격은 이 구조에 들어맞지 않는다 (위 "근본 mismatch" 참조). 따라서 운영 phase 는 **mechanism layer** = monitor / alert / 자동 Issue 생성 mechanism (cron workflow / filesystem signal / 자동 Issue) 으로 실현된다.

정합 invariant:
- **lane count 변경 0** — ADR-023 lane plugin lifecycle 의 lane count invariant (6→8 = scope 확장 only) 가 본 ADR 로 인해 변경되지 않는다. 운영 phase 는 lane plugin 신설을 수반하지 않는다.
- **`phase:운영` label 신설 불요** — `phase:*` label 은 Story-scoped lane 전용 (phase-gate-mergeable label mapping). 운영 phase 는 Story-scoped lane 이 아니므로 `phase:운영` label 을 신설하지 않는다. 운영 신호로 생성되는 자동 Issue 는 일반 Story / Epic 후보 label 체계를 따른다 (label-registry 변경 0 — S1).
- **mechanism 실 구현은 후속 Story carrier** — ongoing monitor mechanism (workflow yml / script) 의 실 구현은 S4~S7 영역. 본 ADR 은 "mechanism layer 답습" 원칙만 declare 한다.

### §결정 3 — 0 API call constraint (filesystem / cron 우선)

운영 신호 측정 채널(measurement-channel)은 가능한 한 **filesystem / cron 기반**이며 network call 을 최소화한다. 이는 ADR-083 (consumer-applicability-filter) §결정 (L133) 의 filesystem-only signal invariant — "두 signal 모두 consumer-side filesystem 안 — network call 0, gh api 0, marketplace.json membership check 0" — 의 운영 도메인 확장이다.

근거 3종 (ADR-083 L133 답습):
- (a) **offline-first invariant** — ADR-066 PAT scope 최소화 정합. 측정이 외부 credential / network 의존을 만들지 않는다.
- (b) **trust boundary 명확** — filesystem-only = consumer 권한 area only. 측정 채널이 production secret / credential / cross-repo trust 영역에 접근하지 않는다 (§7 보안 경계).
- (c) **측정 비용 최소** — 측정 자체가 부작용·비용을 만들지 않아야 한다 (single read / cron tick).

network-heavy 측정(실시간 metric API 등)은 0 API call constraint 위반이다. 외부 SRE 패턴(progressive delivery 의 실시간 metric API 기반 canary analysis)을 직접 복사하지 않고, codeforge 는 filesystem/cron 측정으로 답습한다.

### §결정 4 — wrapper-self-app N/A invariant

wrapper (codeforge 자체) 는 production 배포 환경이 없다 (plugin = code 0 + runtime behavior 0 + production deploy state 부재, ADR-72 L172 정합). 따라서:

- **wrapper = declarative SSOT only** — wrapper repo 는 운영 phase 의 정의 / 정책 (본 ADR + domain-knowledge 4 파일) 만 보유한다. 실측 0.
- **consumer = 실측 Tier-2** — 운영 phase mechanism 의 실제 신호 회수는 consumer (mctrader 등 실 배포 환경) 대상이다.

이는 ADR-72 §결정 6 wrapper-self-app N/A invariant + production-cutover-evidence.yml Tier-1 declare-time exemption 패턴 (`production_cutover_touching=true AND repo=wrapper AND code_change=0` triple-AND fast-PASS) 의 도메인 일반화다. 운영 phase workflow 가 wrapper repo 에 trigger 되면 Tier-1 declare-time exemption 으로 fast-pass / skip 한다 (실 mechanism 신설 = S4~S7 carrier 영역).

**consumer overlay 축소 차단** — 0 API call constraint + wrapper-N/A invariant 는 wrapper-canonical invariant 다. consumer overlay (`.claude/_overlay/`) 는 정책 확장만 가능하고 축소 불가 (ADR-057 정합).

### §결정 5 — self-improving loop narrative + loop closure gate 위험 식별

운영 phase 의 신호는 codeforge 의 다음 작업거리로 환류된다:

```
운영 신호 (에러율 급증 / 회귀 / rollback 발생) → 자동 Issue 생성 → PMOAgent escalation → 다음 Epic 후보
```

이는 ADR-045 §D-9 (cross-Story pattern_count ≥ 2 → ADR escalation forcing function + escalation_action 2-value `adr_draft_emitted | escalate_user`) 패턴의 답습이다 — retro pattern 이 ADR escalation 으로 환류되듯, 운영 신호가 다음 Epic 후보로 환류된다.

**무한 발산 위험 식별 (loop closure gate 는 S6 carrier)** — monitor Issue → escalation → 다음 Epic → 또 Issue 의 무한 자기 증식 위험이 존재한다. 본 S1 (ADR-104) 은 이 위험을 **식별만** 하고, loop closure gate (dedup + max-depth + escalate_user 사용자 gate) 의 실 구현은 **S6 carrier** 로 명시한다. self-improving-loop.md (Phase 2) 에 "loop closure 필요 (S6)" 를 narrative 로 기록한다.

또 운영 신호는 **정량(숫자 임계) 우선**이고 모달·정성 어휘("성능이 나쁘면" 등)는 금지된다 (ADR-064 모달 어휘 forbid-list 정합). 이는 S2 (자동 rollback) 의 "숫자 임계" 정의 layer anchor 다.

## 경계 (Boundary)

### 운영 phase ↔ 인접 영역 disjoint 표

| 영역 | 시간 성격 | 담당 | 운영 phase 와의 관계 |
|---|---|---|---|
| 8 lane (요구사항~보안테스트~배포~배포검토) | Story-scoped (delta + 종료 게이트) | lane plugin | disjoint — 운영 phase 는 lane 아님 (mechanism layer, §결정 2) |
| 배포검토 lane (smoke / 성능 비교 / cutover 사후 검증) | 한 번 끝나는 (일회성) | codeforge-deploy-review (ADR-088) | disjoint — 배포검토 *이후* 가 운영 phase (§결정 1) |
| 운영 phase (에러율 / 회귀 / rollback 신호) | 계속 도는 (ongoing) | mechanism layer (monitor / cron / 자동 Issue) | **본 ADR 정의 영역** |
| 운영 실행 *절차 결정* (OpsExecutionArchitect) | decision axis | CFP-1079 (예정) | disjoint axis — 운영 phase = observation axis (배포 후 신호 회수), CFP-1079 = decision axis (운영 실행 절차 결정) |

### 두 release lifecycle taxonomy disambiguation 표 (필수 — EC-4 해소)

⚠️ "release lifecycle" 용어는 codeforge 안에서 **서로 다른 두 축**으로 쓰인다. 혼동 차단을 위해 명문화한다:

| 축 | SSOT | stage 열거 | 의미 축 |
|---|---|---|---|
| **channel distribution lifecycle** | `docs/domain-knowledge/domain/production-cutover/README.md` (L40-48) | schema declare → runtime activation → production cutover → promotion criteria → downgrade asymmetry (5-stage) | **버전 배포 채널** (canary / beta / stable 채널을 거쳐 어떻게 배포 버전이 승격/강등되는가) |
| **시간축 lifecycle** | 본 ADR-104 §결정 1 + CLAUDE.md L84 | 요구사항 → 설계 → ... → 배포 → 배포검토 → **운영 phase** | **시간축 단계** (한 작업이 요구사항부터 배포 후 운영까지 시간순으로 거치는 단계) |

**두 축은 disjoint** — channel distribution 5-stage 의 "cutover" / "promotion" 은 *버전 채널 승격* 의미이고, 시간축 lifecycle 의 "배포" / "운영 phase" 는 *시간순 단계* 의미다. 운영 phase 는 시간축 lifecycle 의 마지막 ongoing 단계이지, channel distribution taxonomy 의 6번째 stage 가 **아니다**. Epic 표현 "release lifecycle stage 6 ongoing 운영" 은 시간축 축으로만 해석해야 한다 (channel distribution 5-stage 에 1 더한 것 아님).

### Anti-scope (본 ADR 이 결정하지 않는 영역 — 후속 Story carrier)

- **자동 rollback 도메인 재정의** (rollback-protocol.md Step 4 amend + 안전장치 4) = **S2**. 본 ADR §결정 5 는 정량 신호 원칙만 declare.
- **운영 metric → PMOAgent input 회로 ADR 구현** (self-improving loop 실 구현) = **S3**. 본 ADR §결정 5 는 narrative 정의만.
- **ongoing monitor mechanism 실 구현** (workflow yml / script) = **S4~S7**.
- **loop closure gate 실 구현** (dedup + max-depth + 사용자 gate) = **S6**. 본 ADR §결정 5 는 위험 식별만.
- **label-registry / evidence-checks-registry / doc-locations row append** = mechanism 신설 시 (S4~S7).
- **Cross-Story 통합 검증** = **S8**.

## 결과

### 긍정적 효과

- CLAUDE.md L84 의 dangling forward-reference ("운영 phase 와 disjoint") 가 referent 를 획득 — governance 자기참조 정합성 회복.
- 운영 phase 가 lane 인지 mechanism 인지의 governance 모호성 해소 (mechanism layer 확정, ADR-023 정합).
- 후속 S2~S8 의 단일 정의 anchor 확보 (각 후속 Story 가 본 ADR 을 SSOT 로 참조).

### 부정적 효과 / trade-off

- 운영 phase 가 mechanism layer 이므로 lane 의 종료-게이트 보장(8 lane 통과)을 받지 못한다 — 운영 신호의 품질 게이트는 mechanism 자체 (cron / 자동 Issue 의 dedup) 에 의존. loop closure gate (S6) 가 이 trade-off 의 안전망.
- wrapper-N/A invariant 로 인해 wrapper 자체는 운영 phase mechanism 을 dogfood 검증할 수 없다 (production 환경 부재) — declarative SSOT 만 검증 가능. consumer (mctrader) 가 실 검증 carrier.

### mechanical enforcement

`mechanical_enforcement_actions: []` (declaration-only Wave 1 — ADR-082 §결정 6 / ADR-070 §D5 / ADR-076 / ADR-086 / ADR-097 retain pattern 답습). 운영 phase = 신규 정의 layer 이고 실 mechanism 은 S4~S7 carrier 가 신설 시 evidence-checks-registry row 를 append 한다. **pattern_count ≥ 2 recurrence 시 follow-up CFP MUST promote to mechanical lint** (ADR-084 precedent — 운영 phase 정의 위반이 2회 이상 재발하면 mechanical lint 로 격상 의무).

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-087](ADR-087-deploy-lane-and-lifecycle-extension.md) — Deploy lane (운영 phase 의 release lifecycle 선행 단계)
- [ADR-088](ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — Deploy Review lane (§결정 3 "한 번 끝나는" + L81 운영 phase 8 후보 = 본 Epic origin)
- [ADR-083](ADR-083-consumer-applicability-filter.md) — filesystem-only signal invariant (0 API call source)
- [ADR-045](ADR-045-story-retro-mandatory-trigger.md) — §D-9 pattern → ADR escalation forcing function (self-improving loop source)
- [ADR-72](ADR-72-production-evidence-deputy-and-epic-cutover-gate.md) — wrapper-self-app N/A + Tier-1 declare-time exemption (wrapper-N/A source)
- [ADR-023](ADR-023-lane-plugin-lifecycle.md) — lane count invariant (9번째 lane 아님 정합)
- `docs/domain-knowledge/domain/operational-phase/` — narrative SSOT 4 파일 (Phase 2 carrier)
- `docs/domain-knowledge/domain/production-cutover/README.md` — channel distribution 5-stage taxonomy (disambiguation 대상)
