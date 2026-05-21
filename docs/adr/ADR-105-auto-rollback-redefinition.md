---
adr_number: 105
title: 자동 rollback 도메인 재정의 — user-decision layer ↔ auto-rollback layer disjoint + 안전장치 4 AND codify
status: Accepted
category: governance
date: 2026-05-22
carrier_story: CFP-1191
parent_epic: CFP-1187
related_stories:
  - CFP-1191     # 본 carrier (Epic CFP-1187 Story-2, 자동 rollback 도메인 재정의 anchor)
  - CFP-1190     # prerequisite (Story-1, ADR-104 운영 phase 1st-class 정의 — §결정 5 정량 신호 원칙 = 안전장치 1 layer anchor)
  - CFP-1187     # umbrella Epic — 운영 phase 신설
related_adrs:
  - ADR-104      # 직접 제약 (S1) — §결정 5 정량 신호 원칙 + S2 숫자 임계 layer anchor (L115 verbatim) / §결정 3 (0 API call) / §결정 4 (wrapper-N/A) 계승
  - ADR-064      # 직접 제약 — 모달 어휘 forbid-list (안전장치 1) + §self-application user_decision_branches (§결정 2 핵심)
  - ADR-045      # 직접 제약 — §D-9 escalation forcing function (안전장치 3 사후 알림 답습 source — 자동 실행 ≠ 침묵 실행)
  - ADR-087      # 직접 제약 — §결정 5 blue-green + atomic swap + 3-시간 보존 + 자동 rollback 단일 매커니즘 (안전장치 2 보존 기간 default 3h anchor, L142 [empirical-source: TBD])
  - ADR-014      # 배경 — operational risk boundary axis (DR / disconnect / clock / rate / env) — 안전장치 4 kill-switch boundary 정합 (단 도메인 다름: ADR-014 = operator kill-switch / 본 ADR = 자동 mechanism disable 토글)
  - ADR-058      # 직접 제약 — §해소 기준 정량 명시 의무 (안전장치 1 모달 어휘 금지 정합)
  - ADR-057      # 배경 — consumer overlay 정책 축소 불가 (보존 기간 default 3h consumer 확장 가능 / 축소 불가)
  - ADR-72       # 배경 — ProductionEvidenceDeputy + production cutover incident response 영역 (rollback-protocol.md 의 owner SubAgent — Step 6 4-evidence-quad re-verify 정합). file명 = ADR-72 2-digit form (ADR-088 precedent 정합)
  - ADR-084      # pattern_count >= 2 재발 시 mechanical promote precedent (frontmatter clause 형식)
  - ADR-054      # 배경 — doc-only fast-path — 본 Story 는 신규 ADR 포함 → fast-path 비대상 (full-lane)
related_files:
  - docs/adr/ADR-RESERVATION.md                                                       # row 105 reserved → active 전환
  - docs/domain-knowledge/domain/production-cutover/rollback-protocol.md              # Step 4 + L36/L67/L70/L108 amend (2-layer 분리 표 추가, user-decision layer 보존)
  - reconcile-protocol-v1 §4.14                                                       # rollback ≠ demotion disjoint (downgrade_asymmetry_marker — 무변경, AC-7)
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-082 §결정 6 / ADR-070 §D5 / ADR-076 / ADR-086 / ADR-097 / ADR-104 retain pattern 답습 (behavioral directive only, 자동 rollback = 신규 정책 정의 layer / 실 mechanism (숫자 임계 trigger + 사후 알림 Issue + kill-switch workflow) = S4 carrier 가 신설 시 evidence-checks-registry row append; pattern_count >= 2 recurrence 시 follow-up CFP MUST promote to mechanical lint — ADR-084 precedent)
is_transitional: false  # permanent governance anchor — ADR-087/088/104 (lane lifecycle / 운영 phase, is_transitional: false) 정합. 자동 rollback 재정의 (2-layer disjoint / 안전장치 4 AND / §self-application 2-layer / kill-switch disambiguation) 는 future 재사용 permanent. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합 — Amendment 1 evidence-gate symmetric 재정의 후에도 약화 시 evidence requirement 의무)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용 (안전장치 추가 / disjoint 강도 강화). 안전장치 축소 / AND→OR 완화 = ADR-058 §결정 5 (Amendment 1) 약화 evidence-gate 의무
amendment_log: []
---

# ADR-105 — 자동 rollback 도메인 재정의

## 상태

`Accepted` (2026-05-22 KST) — CFP-1191 carrier (Epic CFP-1187 Story-2, 자동 rollback 도메인 재정의 anchor). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 / ADR-097 row 97 / ADR-104 row 104 chief author precedent 정합).

## 컨텍스트

### 동인

S1 (ADR-104) 가 **운영 phase** 를 codeforge release lifecycle 의 시간축 마지막 ongoing 단계로 1st-class 정의했다 — 배포검토(deploy-review) 가 끝난 *그 이후* 시간축에서 배포 때 약속한 성능·안정성이 계속 지켜지는지 감시하고, 문제 시 자동으로 되돌리는(rollback) 영역. 그런데 현재 rollback 결정 게이트가 운영 phase 의 "계속 도는" 자동 감시 효용과 충돌한다.

증거 — `docs/domain-knowledge/domain/production-cutover/rollback-protocol.md` (wrapper main 실재, Read 직접 확인) 의 rollback 결정 게이트는 **"사용자 explicit go-ahead 의무"** 단일 layer 로 박혀 있다:
- L36 (컨텍스트) — "rollback ... 결정 게이트 = 사용자 explicit decision 의무 영역 (reconcile-protocol-v1 user_decision_branches 0 invariant 영역 외 — production cutover rollback = 사용자 결정 분기 허용 영역, ADR-064 §self-application 정합)"
- L64-70 (Step 4 — Rollback decision) — "rollback path: production state 영향 reversible + 사용자 explicit decision 의무"
- L70 (강조) — "**사용자 explicit go-ahead 의무 영역** (reconcile-protocol-v1 user_decision_branches: 0 invariant 영역 외, ADR-064 §self-application — production cutover rollback = 사용자 결정 분기 허용 영역)"
- L108 (경계) — "rollback decision 의 사용자 결정 분기 = reconcile-protocol-v1 user_decision_branches 0 invariant 영역 외 (production cutover rollback 한정 허용, ADR-064 §self-application)"

즉 되돌리기 전 사람이 매번 명시적으로 승인해야만 rollback 이 일어난다. 운영 phase 는 사람이 자리에 없는 시간에도 "계속 도는" 감시 영역인데, 신호가 임계를 넘어도 사람 승인을 기다려야 한다면 약속 위반이 방치된다.

### 근본 mismatch + 산업 evidence

운영 phase 의 ongoing 자동 감시 성격 ↔ 기존 rollback 게이트의 사람 승인 의무 사이의 mismatch 가 본 재정의의 핵심이다. 산업 표준 (Researcher §6, WebSearch 2026-05 verified) — 자동 rollback 은 MTTR 를 평균 57분(수동)에서 3.7분(자동)으로 줄인다. progressive delivery 의 deployment gate 는 SLO degradation / error budget burn 감지 시 promotion 을 자동 차단한다. 사람 승인 대기는 governance 신뢰의 병목이다.

따라서 본 ADR 은 rollback 결정을 **자동 실행까지 허용** (Epic CFP-1187 §1 사용자 확정 "b") 으로 재정의한다. 단 자동 실행이 폭주(false rollback / oscillation / 무음 실행 / 데이터 손실)하지 않도록 **안전장치 4** 를 의무로 codify 한다 (§결정 3). 그리고 **단순 치환이 아니라** — 기존 user-decision layer 와 신규 auto-rollback layer 를 disjoint 로 분리한다 (둘 다 보존, §결정 1).

## 결정

자동 rollback 을 codeforge production-cutover 도메인의 1st-class 정책으로 재정의한다. 본 ADR 이 normative SSOT 이고, `rollback-protocol.md` (production cutover incident response narrative SSOT) 의 Step 4 + L36/L67/L70/L108 amend (2-layer 분리 표 추가) 가 서술적 elaboration 이다.

### §결정 1 — 2-layer disjoint 재정의 (단순 치환 금지)

rollback 결정 게이트를 **단일 user-decision layer 에서 2-layer 로 분리**한다. 기존 user-decision layer 는 **제거하지 않고 보존**한다. auto-rollback layer 는 이를 대체하는 것이 아니라, "안전장치 4 모두 충족 + 보존 기간 안" 이라는 좁은 영역에서만 작동한다.

| layer | 발동 조건 | 결정 주체 | 결정 분기 | 보존 기간 | SSOT 영역 |
|---|---|---|---|---|---|
| **user-decision layer** (기존, 보존) | 안전장치 4 중 1+ 미충족 / 보존 기간 초과 / kill-switch 활성 / 임계 모호 / forward-fix 판단 필요 | 사용자 (explicit go-ahead) | **있음** (rollback vs forward-fix 사용자 결정 분기 허용 — ADR-064 §self-application `user_decision_branches: 0 invariant` 영역 외) | 무관 (사람이 판단) | rollback-protocol Step 4 user-decision path |
| **auto-rollback layer** (신규) | 안전장치 4 **모두 충족** (AND) | mechanism (deterministic) | **없음** (숫자 임계 deterministic — 결정 분기 0) | green→blue default 3h **안에서만** | 본 ADR §결정 3 + rollback-protocol Step 4 auto path |

**disjoint 보장 normative** — 한 layer 가 다른 layer 를 약화하지 않는다 (둘 다 보존). auto-rollback layer 진입 자격을 잃는 모든 영역(안전장치 미충족 / 보존 기간 초과 / kill-switch 활성 / 임계 모호)은 전부 user-decision layer 로 복귀한다. 두 layer 의 합집합 = 모든 rollback 상황 (완전 cover) / 교집합 = 공집합 (disjoint).

### §결정 2 — ADR-064 §self-application 2-layer 정밀 명시

> ⚠️ **본 §결정 = 설계 리뷰 집중 검증 대상.** 기존 박힘은 "rollback decision = `user_decision_branches: 0` invariant 영역 외 (사용자 결정 분기 허용)" 라는 단일 진술이었다. 본 ADR 후 이를 **2-layer 로 정밀화**한다.

ADR-064 §self-application 의 `user_decision_branches: 0 invariant` 관점에서 두 layer 는 **disjoint** 하다:

| layer | `user_decision_branches` | invariant 영역 | 근거 |
|---|---|---|---|
| **auto-rollback layer** | **0** (deterministic) | **invariant 영역 *내*** | 숫자 임계(에러율 / latency burn rate) 가 사전 정의된 deterministic 조건. 사람이 끼어들 결정 분기가 없다 (안전장치 4 AND 충족 시 mechanism 이 자동 발동). 따라서 `user_decision_branches: 0` invariant 를 *준수* 한다 |
| **user-decision layer** | **있음** (분기 허용) | **invariant 영역 *외*** (유지) | rollback vs forward-fix 는 production state reversibility / 데이터 보존 의무 등 가치 판단을 요구한다 → 사용자 결정 분기 허용. ADR-064 §self-application 의 기존 "production cutover rollback = 분기 허용" 영역을 *유지* |

**"rollback 은 분기 허용" 단순 표현 금지** — 본 ADR 이후 rollback 을 ADR-064 §self-application 관점에서 인용할 때, "rollback decision = 분기 허용" 이라는 단일 진술을 쓰지 않는다. 반드시 2-layer 로 분리한다: "**auto-rollback layer 는 분기 0 (deterministic, invariant 영역 내) / user-decision layer 는 분기 허용 (invariant 영역 외 유지)**". 이는 ADR-064 §self-application top-down ratchet 강화 방향 (분기 0 영역의 명시적 확대 — auto layer 가 새로 invariant 영역에 편입)이며 약화가 아니다 (user layer 의 분기 허용 영역은 무변경 유지).

### §결정 3 — 안전장치 4 AND codify (정량·검증 가능)

auto-rollback layer 진입은 **안전장치 4 가 모두 충족(AND)** 될 때에만 허용된다. 1개라도 미충족 시 user-decision layer 로 복귀한다 (EC-6). "의무로 동반" (사용자 verbatim) = AND 해석.

| # | 안전장치 | 정량 / 검증 기준 | 미충족 시 |
|---|---|---|---|
| 1 | **명확한 숫자 임계** | 에러율 / latency burn rate 등 **숫자 + window** 형식으로만 trigger (예: burn rate ≥ N over Mh window). 모달·정성 어휘("성능이 나쁘면" 등) 0 (ADR-064 모달 어휘 forbid-list + ADR-058 §해소 기준 정량 명시 정합). 구체 수치는 consumer SLO 의존 (consumer overlay) — 본 ADR 은 *형식*(숫자 + window 명시) 만 강제 | 임계 모호(숫자 미정의 / 모달 표현) = auto 진입 자격 없음 → user layer (EC-3) |
| 2 | **보존 기간 안에서만** | green→blue 복귀가 데이터 손실 0 으로 가능한 보존 기간 **안에서만** 자동. CFP-1059 / ADR-087 §결정 5 blue 보존 default 3시간 정합 (`[empirical-source: ADR-087 §결정 5 L142 — brainstorm Phase 1 합의 default, consumer override 가능 project.yaml deploy.retention_hours]`). consumer overlay 확장 가능(더 길게) / 축소 불가(더 짧게 금지 — ADR-057) | 보존 기간 초과 = 자동 rollback 금지 → user-decision layer → hotfix 흐름(rollback-protocol Step 5b forward-fix path) (EC-1) |
| 3 | **자동 rollback 후 사후 알림** | 자동 실행 ≠ 침묵 실행. 되돌린 직후 **Issue 자동 발의 + PMOAgent escalation** 의무 (무음 rollback 금지). ADR-045 §D-9 답습 — "자동 감지 → escalation → 인간 확인 게이트". escalation 회로 실 구현 = S3 영역 (본 ADR 은 "사후 알림 의무" 만 declare) | 사후 알림 mechanism 부재 = auto 진입 자격 없음 (무음 = 위반) |
| 4 | **kill-switch** | 자동 rollback mechanism **자체를 비활성화** 하는 토글 (filesystem flag 예: `.codeforge/auto-rollback.disabled`, 또는 config flag). 운영자가 자동을 끄고 수동 통제로 복귀할 수 있어야 한다. ADR-014 operational risk boundary axis 정합 (단 도메인 다름 — §결정 5 disambiguation) | kill-switch 활성 시 auto layer **전체 무력화** → user-decision layer 만 동작. **kill-switch 가 다른 안전장치보다 우선** (활성 시 무조건 auto 무력화, EC-2) |

### §결정 4 — rollback ≠ demotion disjoint 보존 + wrapper-N/A / 0 API call 계승

**rollback ≠ demotion 보존 (AC-7)** — rollback-protocol Step 5 L75 가 이미 박은 disjoint ("rollback = operational version revert layer / demotion = channel tier 하향 declare 차단 layer (forward-only ratchet wired)") 를 amend 후에도 보존한다. 본 ADR 은 rollback layer 에 auto path 만 추가하고, demotion invariant (reconcile-protocol-v1 §4.14 `downgrade_asymmetry_marker.status: wired`) 는 **무변경**이다. 자동 rollback 은 version revert(green→blue) 이지 channel tier 하향이 아니다.

**ADR-104 계승 invariant** (S1 직접 제약):
- **wrapper-self-app N/A invariant** (ADR-104 §결정 4) — 자동 rollback mechanism 실측 0 (wrapper = production 환경 부재). wrapper repo 는 정의 / 정책 (본 ADR + rollback-protocol amend) 만 보유. 실측은 consumer 한정 (S4 mechanism).
- **0 API call constraint** (ADR-104 §결정 3) — 자동 rollback trigger 신호 측정은 filesystem / cron 우선. 실시간 metric API 직접 의존 금지. 산업 progressive delivery 의 실시간 metric 기반 canary analysis 를 직접 복사하지 않고, filesystem / cron 측정으로 답습 (Researcher §6.2).

### §결정 5 — kill-switch disambiguation (산업 ↔ codeforge 반대 방향)

> ⚠️ **boundary 명문 — 용어 충돌 차단.** 산업 "kill switch" 와 codeforge 안전장치 4 "kill-switch" 는 **이름이 같으나 의미가 반대 방향**이다.

| 용어 | 의미 | 방향 |
|---|---|---|
| **산업 kill switch** (SRE / progressive delivery) | rollback 실행 *수단* — traffic 을 stable 로 instant reroute 하여 *되돌리는* 메커니즘 | 되돌림을 *발동* |
| **codeforge kill-switch** (안전장치 4) | 자동 rollback mechanism *자체를 비활성화* 하는 토글 — 자동으로 되돌리는 것을 *끄고* 수동 통제로 복귀 | 되돌림 자동화를 *차단* |

산업 kill switch 는 *되돌리는* 수단(rollback 을 일으킴)이고, codeforge kill-switch 는 *자동으로 되돌리는 것을 끄는* 토글(auto-rollback 을 막음)이다. 본 ADR 의 안전장치 4 = **codeforge kill-switch 의미** (mechanism disable). 두 용어를 혼동하면 안전장치가 거꾸로 해석될 수 있으므로(예: kill-switch 를 "rollback 강제 발동" 으로 오인) 본 boundary 를 명문화한다.

## 결과

### 긍정

- 운영 phase 의 "계속 도는" 자동 감시가 사람 부재 시간에도 약속 위반을 자동 시정 (MTTR 57→3.7분 산업 evidence).
- 안전장치 4 AND + kill-switch 우선 + 사후 알림 의무로 자동 실행 폭주 차단.
- 2-layer disjoint 로 기존 user-decision 의미 보존 (단순 치환 회피 — 사용자 가치 판단 영역 유지).
- ADR-064 §self-application 2-layer 정밀화로 "분기 0" 영역의 명시적 확대 (ratchet 강화).

### 부정 / trade-off

- **oscillation 위험** (EC-5) — 연쇄 자동 rollback (A→B rollback 후 B 도 임계 초과 → A 로 또 rollback ...) 가능성. 본 ADR 은 이 위험을 **식별만** 한다. loop closure gate (max-depth / cooldown / dedup) 실 구현 = **S6 영역** (forward-ref). 본 ADR 의 안전장치 4 는 단발 자동 rollback 의 폭주는 막으나(AND + kill-switch), 연쇄 oscillation 자체의 closure 는 S6 carrier.
- **자동 rollback 자체 실패** (EC-4) — green 버전 복귀 중 오류 시 escalation (즉시 Issue + PMOAgent + 사용자 통지) + **자동 재시도 금지** (사람 개입 대기, ADR-057 rate-limit fallback "자동 재시도 금지" 패턴 정합).
- **declaration-only** — 본 ADR 은 정책 정의 layer. 실 trigger / 사후 알림 Issue / kill-switch workflow mechanism = S4 carrier (`mechanical_enforcement_actions: []`). pattern_count >= 2 recurrence 시 follow-up CFP MUST promote to mechanical lint (ADR-084 precedent).

### Edge Case 처리 요약 (요구사항 §5.2)

| EC | 시나리오 | 처리 |
|---|---|---|
| EC-1 | 보존 기간 초과 | 자동 불가 → user-decision layer → hotfix(Step 5b forward-fix) |
| EC-2 | kill-switch 활성 | auto layer 전체 무력화 → user-decision layer 만 (kill-switch 우선) |
| EC-3 | 임계 모호 (모달 / 숫자 미정의) | 자동 불가 (보수적) → user-decision layer |
| EC-4 | 자동 rollback 자체 실패 | escalation + 자동 재시도 금지 → 사람 개입 대기 |
| EC-5 | 연쇄 oscillation | 위험 식별만 (본 ADR §결과 trade-off) / closure 실 구현 = S6 |
| EC-6 | 안전장치 일부만 충족 | auto 진입 불가 (AND 조건) → user-decision layer |

## 경계 (boundary)

- **본 ADR scope** = 자동 rollback **정책 재정의** (2-layer disjoint + 안전장치 4 AND + §self-application 2-layer + kill-switch disambiguation). declarative SSOT.
- **S3 (#1192)** = self-improving loop 회로 ADR — 사후 알림 Issue 의 escalation 회로 실 구현. 본 ADR 은 "사후 알림 의무" 만 declare (안전장치 3).
- **S4** = ongoing rollback signal monitor 실 mechanism (숫자 임계 trigger + 사후 알림 Issue + kill-switch workflow yml/script). 본 ADR 은 안전장치 4 정의만.
- **S6** = loop closure gate (oscillation / 연쇄 rollback 방지 실 구현). 본 ADR 은 EC-5 위험 식별만.
- **rollback-protocol.md amend** = 본 ADR 의 elaboration (Step 4 + L36/L67/L70/L108 2-layer 분리 표 추가). user-decision layer 보존 + auto-rollback layer disjoint.

## 해소 기준

N/A — permanent policy

`is_transitional: false` permanent governance anchor. 자동 rollback 재정의 (2-layer disjoint / 안전장치 4 AND / §self-application 2-layer / kill-switch disambiguation) 는 future 재사용 permanent. amendment 시 ratchet 강화 방향만 허용 (안전장치 추가 / disjoint 강도 강화). 안전장치 축소 / AND→OR 완화 = 약화 방향 → ADR-058 §결정 5 (Amendment 1 evidence-gate symmetric 재정의) 약화 evidence requirement 의무.

## 관련 ADR

- **ADR-104 §결정 5** — 정량 신호 원칙 + S2 숫자 임계 layer anchor (L115 verbatim "이는 S2 (자동 rollback) 의 '숫자 임계' 정의 layer anchor 다")
- **ADR-104 §결정 3 / §결정 4** — 0 API call constraint / wrapper-N/A invariant 계승 (§결정 4)
- **ADR-064 §self-application** — `user_decision_branches: 0 invariant` 2-layer 정밀화 (§결정 2) + 모달 어휘 forbid-list (안전장치 1)
- **ADR-045 §D-9** — escalation forcing function (안전장치 3 사후 알림 답습 — 자동 실행 ≠ 침묵 실행)
- **ADR-087 §결정 5** — blue-green + 3-시간 보존 (안전장치 2 default anchor, L142)
- **ADR-014** — operational risk boundary axis (안전장치 4 kill-switch boundary — 단 도메인 다름, §결정 5 disambiguation)
- **ADR-058 §결정 5** — §해소 기준 정량 명시 (안전장치 1) + 약화 evidence-gate (sunset_justification)
- **ADR-72** — ProductionEvidenceDeputy + production cutover (rollback-protocol owner SubAgent, file명 2-digit form)

## 변경 이력

| 날짜 (KST) | Story | 변경 |
|---|---|---|
| 2026-05-22 | CFP-1191 | 최초 작성 — 자동 rollback 도메인 재정의 (2-layer disjoint + 안전장치 4 AND codify + ADR-064 §self-application 2-layer 정밀 명시 + kill-switch disambiguation + rollback ≠ demotion 보존). ArchitectAgent chief author direct write. Epic CFP-1187 Story-2. |
