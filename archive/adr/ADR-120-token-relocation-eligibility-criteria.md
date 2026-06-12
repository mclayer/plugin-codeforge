---
adr_number: 120
title: "token-relocation-eligibility-criteria — 상시 로드 지침의 on-demand 이전 적격 기준 (호출 빈도 필터 × skill 확률 활성화 제약)"
status: Accepted
category: governance
date: 2026-06-12
carrier_story: CFP-2190
parent_epic: "mclayer/plugin-codeforge#2189"
supersedes: null
amends: null
amendments: []
related_stories:
  - CFP-2190
related_adrs:
  - ADR-051  # 부모 선례 — 추출 기준 3종(결정 1) + anchor-vs-reference 판정자(본문 '결정 7', amendment_log 표기 '§결정 4') + 3-층 안전망(본문 '결정 9'). 본 ADR 2 새 축 = disjoint 확장 (§결정 6)
  - ADR-012  # CLAUDE.md 4-층 scope — keep-vs-relocate 기존 분류 base (cross-ref only)
  - ADR-115  # gate runtime-enforceable 강제 경로 = hook injection (scope = 4-hook 종, blocking 은 PreToolUse(Agent) 단일 — 필터 2 논거)
  - ADR-060  # 4-tier enforcement promotion framework (후속 mechanical 승격 경로)
  - ADR-054  # §결정 6.1 declarative seed fast-path (본 ADR Wave 1 declarative-only 적격 근거)
  - ADR-119  # frontmatter 패턴 복제 원본 (신규-but-declarative-only ADR fast-path 직전 선례) + 외부 지식 인용 규약
  - ADR-039  # §결정 2 inline whitelist — 본 ADR 판정 절차가 침범하지 않는 면제 경계
  - ADR-058  # §결정 5 ratchet — 약화 amendment sunset_justification 의무
  - ADR-064  # §결정 7 evidence-gated symmetric ratchet (약화 시 evidence-grounded justification)
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - plugins/codeforge-review/templates/review-pl-base.md
  - skills/  # 이전 target surface (skills/<slug>/SKILL.md × 12 — ADR-051 결정 2 형식 SSOT)
  - plugins/  # */agents/*.md — corollary 적용 대상 dir (반복 블록 3종 실측 surface)
mechanical_enforcement_actions: []  # Wave 1 declarative-only — 실 wire(lint/script) = 후속 carrier CFP full-lane 의무 (ADR-054 §결정 6.1)
wave_2_wire_carrier: "Epic #2189 S2 (playbook cold 섹션 skill 분리) + S3 (agent 반복 블록 압축 + 참조-time base 검토) + 후속 lint CFP (ADR-060 4-tier 경로)"
is_transitional: false
---

# ADR-120: token-relocation-eligibility-criteria — 상시 로드 지침의 on-demand 이전 적격 기준

## 상태

Accepted (2026-06-12 KST, CFP-2190 carrier — Epic #2189 S1 선행 Story). `is_transitional: false` — 영구 정책 (governance criteria).

## 본질 선언

> **상시/반복 로드 지침을 on-demand 위치 (skill body 등) 로 이전할 수 있는가의 판정 기준 = 호출 빈도 (hot/cold) × 활성화 유형 (gate/guide) 2축 AND 필터 + net-savings 정성 게이트.** 본 ADR 은 판정 룰만 codify 한다 — 단 한 줄도 실제로 옮기지 않는다 (실 이전 = Epic #2189 S2/S3 범위).

## 컨텍스트

### 동기 (Epic #2189 §1 사용자 원문 verbatim)

> "codeforge repo 통합이 완료되었다. 다시한번 사용할 토큰 양을 최적화하고 싶은데 반복되는 지침들을 집계해서 skill화 해보자"

근본 동기 = 토큰 절감 + attention 희석 감소. 무기준 이전은 두 가지 실패 모드를 낳는다: (a) 핫패스 지침 이전 = 재로드로 순절감 0/음수, (b) 게이트성 지침 이전 = skill 확률 활성화로 게이트 약화. 본 ADR 이 이 두 실패 모드를 각각 필터 1 / 필터 2 로 차단한다.

### skill 메커니즘 전제 (외부 지식 — ADR-119 인용 규약 적용)

- **progressive disclosure**: skill metadata (name + description) 는 상시 로드, body 는 trigger 매칭 시 on-demand 로드. 신설 N skill = N × metadata 상시 비용 (~60-100 token/skill 추정) → 작은 body 이전 시 순손실 가능 (§결정 5 근거). `source:` Claude Code 공식 Agent Skills 문서 + Story CFP-2190 §6.1 (ResearcherAgent WebSearch 조사 인용). `[verification-out-of-scope: 외부 런타임 메커니즘]`
- **확률적 활성화**: skill body 호출 = trigger 매칭에 대한 모델 재량 — 호출 보장 없음 (실측 보고 ~50%, 측정 환경 의존 추정치. 지시형 description 으로 개선 가능하나 보장 불가). `source:` Story CFP-2190 §6.1 (ResearcherAgent 조사 인용). `[verification-out-of-scope: 모델 런타임 행동]`
- **gate 절대-준수 강제의 runtime-enforceable 경로 = hook injection** — [`ADR-115`](ADR-115-runtime-hook-enforcement.md) `[verified]`. 단 ADR-115 scope = 4-hook 종 한정 + 실제 blocking 은 PreToolUse(matcher:"Agent") 단일 (§결정 1 / §결정 6) — 전 gate 의 만능 캐리어가 아니다. hook 으로 강제 불가한 gate 는 CLAUDE.md anchor inline (ADR-051) + CI lint (ADR-060) 경로. 필터 2 의 "gate 는 skill 이 아니라 hook/anchor/lint 로" 논거.

### 실측 baseline (origin/main `a41962d4`, 2026-06-12 KST 직접 측정)

| 대상 | 실측값 | 측정 방법 |
|---|---|---|
| `docs/orchestrator-playbook.md` | 4,095줄 / 330,954B (~331KB) | `wc -lc` |
| playbook "CRITICAL Step 0 — pre-spawn-pin" | L675~L2278 = 1,604줄 (39.2%) | `grep -nE '^## '` 섹션 경계 |
| `plugins/*/agents/*.md` | 44개 / 438,612B (~439KB) | `find + du -bc` |
| `plugins/codeforge-review/templates/review-pl-base.md` | 609줄, 참조 빌드 스크립트 **0건** | `wc -l` + `grep -rln review-pl-base --include='*.sh' --include='*.yml' --include='*.py'` = 0 |
| 반복 블록: "Re-entry 제약 3종" | 31 파일 | `grep -rl` (plugins, *.md) |
| 반복 블록: "외부 지식 인용 규약" (ADR-119) | 15 파일 (문구 기준; `(ADR-119)` 괄호 정확 표기 heading = 11) | `grep -rl` — 측정 문구에 따라 11/15 분기, 양 수치 병기 |
| 반복 블록: "재조사 수신부" | 7 파일 | `grep -rl` (plugins, *.md) |

## 결정

### §결정 1 — 2축 적격성 매트릭스 (본 ADR 의 심장)

**축 1 판별 (hot/cold)**:

- **hot** = 매 spawn / 매 턴 / 또는 **모든 lane 공통으로 진입마다** 무조건 로드·참조되는 핫패스.
- **cold** = 특정 상황·이벤트·**특정 lane 진입 시에만** 조건부 참조되는 절차형. 특정 lane 한정 조건부 참조 (lane-conditional) = cold — ADR-051 결정 1 (b) lane-conditional 추출 기준과 정합 (기존 lane 진입 skill 들이 이 분류의 실증 선례, 외관 충돌 없음).
- **중간 빈도 tie-breaker (보수 룰)**: hot/cold 판별 모호 시 **hot 으로 보수 분류** (= 이전 보류). 핫패스 오이전 = 순손실 확정이므로, 절감 기회 유보보다 우선 차단 (ADR-054 §결정 2 "모호 시 안전 방향" 동형).

**축 2 판별 (gate/guide)** — 판별 기준 명문화:

- **gate-type** = 절대-준수 지침. 위반 = 차단·정합 파손인 invariant ("금지" / "MUST" / 게이트 통과 조건). 예: main 직접 push 금지, marketplace atomic invariant.
- **guide-type** = 참조·절차 안내. 따라가면 좋은 how-to / lookup — 미참조가 즉시 정합 파손으로 이어지지 않음.
- **판별자 = 위반 결과, 표현 아님 (semantic-over-wording)**: 유일 판별자는 "위반 시 차단·정합 파손인가" — "금지"/"MUST" 표지어는 예시일 뿐이며, 실질 gate 를 부드러운 표현으로 재포장해도 분류는 불변 (게이트 약화 오용 차단).
- **혼합 콘텐츠 (fail-safe)**: 한 블록에 절차 안내 + 절대-준수가 혼합된 경우, gate 성분이 1줄이라도 있으면 **전체를 gate-type 으로 보수 분류**한다. 혼합을 guide 로 낙관 분류하면 gate 누수.
- **"블록" 단위 정의 + 분리 후 재판정 (granularity)**: 판정 최소 단위 = 이전/압축을 함께 적용할 연속 마크다운 구획 (heading 하위 섹션 또는 list 묶음). 혼합 블록에서 gate 줄을 별도 블록으로 분리한 경우 잔여 guide 부분은 독립 블록으로 재판정 가능 — 단 분리된 gate 줄은 §결정 3 (skill 이전 금지) + §결정 4 gate 명제 보존 의무 대상 그대로.

**매트릭스 (두 필터 AND — 모두 통과해야 적격)**:

| | guide/절차형 | gate/절대-준수형 |
|---|---|---|
| **cold** | **ELIGIBLE** (§결정 5 ROI 게이트 통과 조건) | **INELIGIBLE** — 필터 2 우선 |
| **hot** | **INELIGIBLE** — 필터 1 | **INELIGIBLE** — 이중 부적격 (trivial, verdict 충돌 없음) |

**cold ∧ gate 셀 우선순위 룰**: 활성화 필터 (필터 2) 가 빈도 절감 이득에 **우선**한다 — 확률 활성화로 gate 가 약화되면 보안/정합 게이트 파손이므로, 빈도 측 절감이 아무리 커도 INELIGIBLE. 이 우선순위 룰이 없으면 gate/guide 판별의 실효성이 붕괴한다.

**load-scope layer 어휘 (1회 명시)**: wrapper-global / lane-specific / agent-init-inline 3-layer 중 **판별 축 2종 (빈도 / 활성화 유형) 의 정의는 layer-independent** 다. 단 **agent-init-inline layer (spawn 시 무조건 로드되는 agent 정의 본문) 는 본 매트릭스 verdict 의 대상이 아니다** — §결정 6 step 2 가 매트릭스 적용 전에 §결정 4 corollary 경로로 routing 한다 (runtime skill 이전 자체가 무의미한 layer 이므로 ELIGIBLE/INELIGIBLE verdict 를 부여하지 않음).

### §결정 2 — 필터 1: 호출 빈도 (hot path 이전 금지)

**매 spawn / 매 턴 핫패스 지침 = on-demand 이전 INELIGIBLE.** 근거: on-demand 로 옮겨도 핫패스는 매번 재로드되므로 순절감 ≤ 0 — skill metadata 상시 비용만 추가된다.

- **INELIGIBLE 예시 (실측)**: playbook "CRITICAL Step 0 — pre-spawn-pin" (L675~L2278, 1,604줄 = 39.2%, a41962d4) — 매 spawn 핫패스. 이전 금지. (Step 0 의 압축·스크립트화는 별개 경로 — Epic #2189 out-of-scope, 후속 CFP. "이전" 이 아니라 "축소" 다.)
- 드물게 참조되는 cold 절차형만 적격 진영에 남는다.

### §결정 3 — 필터 2: skill 확률적 활성화 제약 (gate-type 이전 금지)

**skill 활성화는 확률적이다 (모델 재량, 호출 보장 없음).** 따라서 gate-type 절대-준수 지침을 skill 로 이전하면 미활성 turn 에서 게이트가 통째로 우회된다 = 게이트 약화 → **INELIGIBLE**.

- gate 강제가 필요한 지침의 경로 = **hook injection** ([`ADR-115`](ADR-115-runtime-hook-enforcement.md) — runtime-enforceable subset 한정: 4-hook scope, blocking 은 PreToolUse(Agent) 단일) 또는 **CLAUDE.md anchor inline 유지** (ADR-051 anchor 판정 — §결정 6) + **CI lint** (ADR-060 4-tier). skill 은 게이트 캐리어가 아니다.
- guide/절차형만 skill 이전 적격.

### §결정 4 — corollary: 에이전트 반복 블록 = runtime skill 이전 부적합

agent 정의 본문 (agent-init-inline layer) 의 반복 블록은 skill 로 "등록" 해도 **원본 블록이 spawn 시 여전히 로드**되므로 절감 0 이다 (등록 ≠ 실효 — `docs/domain-knowledge/` wording-discipline 2-layer 함정과 동형). runtime skill 이전 부적합.

**적합한 대안 2종 (둘 다 열거 — 택일은 분기 룰)**:

- **(a) 1줄 압축 + SSOT 참조** — 반복 블록을 1줄 pointer 로 줄이고 본문은 SSOT 1곳에만 유지.
- **(b) 참조-time 공통 base SSOT (dedup-at-source)** — `plugins/codeforge-review/templates/review-pl-base.md` 패턴 (609줄, 3 리뷰 lane PL 공유 SSOT — 각 PL md 가 base 를 참조하고 lane-specific delta 만 inline). **표현 정정**: 이 패턴은 "빌드타임 base 합성" 이 아니다 — review-pl-base.md 를 참조하는 빌드 스크립트는 0건 (실측, 컨텍스트 표). 정확한 명칭 = **참조-time 공통 base SSOT**.

**분기 룰 (a vs b)**: 반복 블록이 소수 agent 에 산재 + 분량 짧음 → (a). 다수 agent 공통 + 분량 큼 (drift 위험 / 중복 라인 임계 초과) → (b). **모호 시 fallback = (a) 보수 채택** — (b) 는 신규 base 파일 + 참조 wiring 의 구조 변경이므로 명확한 근거 (다수 공통 + drift 실위험 입증) 시에만. "소수/다수·짧음/큼" 의 정량 임계 = §결정 5 와 동일하게 S2 baseline 측정 deferred.

**gate 명제 보존 의무 (corollary 공통 단서)**: corollary 대상 블록에 gate 성분이 있으면 — 1순위 실측 후보 Re-entry 제약 3종 (31 파일, 재귀 spawn 금지 등) 이 바로 gate 성분 블록이다 — (a) 1줄 압축 시에도 **gate 명제 자체 (금지/차단 의미) 는 agent 본문에 잔존 의무** (압축 = 표현 축약이지 게이트 제거 아님. 게이트 명제를 참조 pointer 로만 대체하면 참조 미추적 시 §결정 3 과 동형의 게이트 약화). (b) 참조-time 공통 base 는 spawn 시 base 가 함께 로드되는 구성일 때만 gate 성분 블록에 사용 가능.

**corollary 적용 실측 후보** (S3 가 실제 적용 — 본 ADR 은 기준만): Re-entry 제약 3종 31 파일 / ADR-119 인용 규약 15 파일 / 재조사 수신부 7 파일 (컨텍스트 실측 표).

**실 이전 시 상속 의무**: 신규 skill = wrapper-canonical (consumer overlay 는 확장만 가능, 축소 불가 — CLAUDE.md overlay invariant) + ADR-051 3-층 안전망 (CLAUDE.md 표 row + frontmatter trigger + agent-prompt 호출 path — 본문 '결정 9') 상속.

### §결정 5 — ROI net-savings 게이트 (정성 — 정량 임계 = S2 deferred)

- **net-positive 의무**: 이전 후보는 relocated body 의 절감이 신규 skill metadata 상시 비용 (~60-100 token/skill 추정 — 컨텍스트 출처 참조) 을 초과해야 한다. 작은 body 양산 = 이주 자체가 순손실.
- **batch amortize 지침**: 여러 작은 body 는 단일 skill 로 묶어 metadata 비용을 amortize 한다.
- **amortized 판정 기준**: net-savings 는 단발 세션이 아닌 **다세션 amortized 기준**으로 판정한다. 단발성 body 와 batch 가능 body 를 구분할 것.
- **정량 임계 + 측정 절차 = S2 baseline 측정 deferred**: 정확한 임계 토큰·cache 할인 계수는 측정 산출물이다 — S1 (criteria codify) 시점에 숫자를 박으면 S2 실측과 충돌 시 ADR 수정이 발생하므로 의도적으로 deferred.
- **S2 측정 전 임시 운영 룰 (borderline)**: 정량 임계 부재 동안 net-positive 정성 판단이 불확실한 borderline 후보 = **측정 선행 → 이전** 순서 의무 (이전 보류가 default — 보수 방향, §결정 1 tie-breaker 와 동형).

### §결정 6 — ADR-051 위 disjoint 새 축 (중복 금지) + 판정 합성 순서

[`ADR-051`](ADR-051-ssot-skill-extraction-pattern.md) 은 본 ADR 의 **부모 선례**다 — 본 ADR 은 ADR-051 을 변경/흡수하지 않는다:

| ADR-051 기존 축 | 본 ADR 새 축 | disjoint 근거 |
|---|---|---|
| 추출 기준 3종 (결정 1: ≥20줄 / lane-conditional / cap 위반 기여) | 호출 빈도 (hot/cold) | 크기·위치 기준 ↔ 로드 빈도 기준 — 서로 환원 불가 |
| anchor-vs-reference 판정자 (본문 '결정 7'; amendment_log 표기 '§결정 4' — 동일 결정): "Orchestrator 매 turn 자기검열?" | 활성화 유형 (gate/guide) | anchor 판정 = Orchestrator 자기검열 축 ↔ gate 판정 = 위반 시 차단성 축. 부분 겹침처럼 보이나 gate 는 agent-side 지침에도 존재 (anchor 판정자의 적용 범위 밖) |

**판정 합성 순서 (전체 파이프라인 — 기존 판정자 먼저, layer routing 다음, 새 필터 마지막. 종료 상태 = step 1/2 의 분기 또는 step 3/4 의 INELIGIBLE 또는 step 5 의 확정뿐 — 중간 step "적격 확정" 없음)**:

1. ADR-051 anchor-vs-reference 판정자 — anchor 면 CLAUDE.md inline 유지, 판정 종료. **ADR-051 결정 1 추출 기준 3종 (≥20줄 / lane-conditional / cap 위반 기여) 의 적용 경계**: CLAUDE.md-sourced 후보는 본 파이프라인 외에 3종 AND 병행 충족 의무 (ADR-051 무변경 — 본 ADR 이 대체·흡수하지 않음). 비-CLAUDE.md 표면 (playbook / agents / lane CLAUDE.md) 후보 = 3종의 적용 경계 밖 — 본 ADR 2축 + ROI 게이트만 적용.
2. 대상이 agent-init-inline layer 면 §결정 4 corollary routing — runtime skill 후보에서 즉시 제외, 대안 (a)/(b) 경로로 분기 후 판정 종료 (후속 step 미적용. gate 성분 블록 = §결정 4 gate 명제 보존 의무 동반).
3. 본 ADR 필터 2 (gate-type?) → gate 면 INELIGIBLE (hook/anchor/lint 경로 — §결정 3).
4. 본 ADR 필터 1 (hot path?) → hot 이면 INELIGIBLE.
5. §결정 5 ROI 게이트 — net-positive 시 적격 확정.

[`ADR-012`](ADR-012-wrapper-claudemd-ssot-boundary.md) §결정 5 4-층 scope (keep-vs-relocate 기존 분류) 와의 관계 = cross-ref only (본 ADR 은 CLAUDE.md scope 분류를 변경하지 않음).

### §결정 7 — 적용 경계 + enforcement 경로 (Wave 1 declarative-only)

- **적용 대상**: wrapper 의 상시/반복 로드 지침 표면 (CLAUDE.md / `docs/orchestrator-playbook.md` / `plugins/*/agents/*.md` / lane CLAUDE.md). lane-specific agent mandate 자체는 침범하지 않는다 (ADR-119 §결정 5 패턴 — 원칙 보편 ↔ 실행 전담, ADR-046 §결정 1 경계 보존).
- **ADR-039 §결정 2 inline whitelist 면제 경계 무손상** — 본 ADR 은 위치 판정 기준이지 행위 면제 변경이 아니다.
- **Wave 1 declarative-only**: `mechanical_enforcement_actions: []` — lint / script / hook wire 0. 본 carrier Story 안에 wire 를 넣으면 doc-only fast-path 즉시 full-lane 전환 (ADR-054 §결정 2 + §결정 6.1 boundary invariant) — wire 는 `wave_2_wire_carrier` 의 후속 carrier CFP full-lane 의무.
- mechanical 승격 경로 = ADR-060 4-tier promotion framework (warning-tier entry → 승격 gate).
- 약화 amendment = ADR-058 §결정 5 sunset_justification + ADR-064 §결정 7 evidence-gated symmetric ratchet 의무.

## 적격/부적격 예시

| 대상 (실측 — a41962d4) | 축 판정 | verdict |
|---|---|---|
| playbook "CRITICAL Step 0 — pre-spawn-pin" (1,604줄/39.2%) | hot × (gate 성분 포함 혼합 → gate 보수 분류) | **INELIGIBLE** (이중 — 필터 1 + 필터 2) |
| CLAUDE.md 작업 규칙 게이트 (예: "main 직접 push 금지") | hot × gate | **INELIGIBLE** — anchor inline 유지 (ADR-051) / 강제는 hook 영역 (ADR-115) |
| playbook cold 절차 섹션 (트러블슈팅·세션 재개류 — Epic spec S2 후보 §7/§9/§16/§18/§14, hot/cold 최종 판정 = S2 설계 lane) | cold × guide | **ELIGIBLE** (§결정 5 ROI 게이트 통과 조건부) |
| agent 반복 블록 3종 (재진입 31 / 인용규약 15 / 재조사 수신부 7 파일) | agent-init-inline layer | **runtime skill 부적합** → §결정 4 대안 (a) 1줄 압축+SSOT 참조 또는 (b) 참조-time 공통 base SSOT |

## 범위 밖

- **실제 이전 (S2/S3)** — 본 ADR 은 단 한 줄도 실제로 옮기지 않는다. S2 = playbook cold 섹션 skill 분리, S3 = agent 반복 블록 압축/base 검토.
- **net-savings 정량 임계·baseline 토큰 실측 인프라** — S2 deferred (§결정 5).
- **agent 도구/권한 변경, lint/script wire** — 후속 carrier CFP (full-lane).
- **Step 0 pre-spawn-pin 압축·스크립트화** — Epic #2189 out-of-scope 후속 CFP (본 ADR 적용 1순위 후보이나 "이전" 아닌 "축소" 경로).

## 결과

- "무엇을 skill 로 옮겨도 되는가" 의 normative 판정 기준 신설 — Epic #2189 S2/S3 + 후속 모든 token-relocation 작업이 상속.
- 두 실패 모드 (핫패스 재로드 순손실 / 게이트 약화) 의 사전 차단.
- ADR-051 (위치·크기·anchor 축) 위에 빈도 × 활성화 축이 합성되어 추출 판정 파이프라인 완결 (§결정 6 순서 — CLAUDE.md-sourced 후보는 ADR-051 결정 1 추출 기준 3종 AND 병행 검증, 비-CLAUDE.md 표면은 본 ADR 2축 + ROI 만).
- 비용: 이전 작업마다 5-step 판정 절차 수행. 정량 임계 부재 (S2 까지) 동안 ROI 판정은 정성 게이트.

## 해소 기준

N/A — permanent policy.

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) — 상시 로드 지침 표면 (anchor / skill pointer 표)
- [`docs/orchestrator-playbook.md`](../../docs/orchestrator-playbook.md) — Step 0 핫패스 (필터 1 부적격 예시) + cold 절차 섹션 (S2 후보)
- [`plugins/codeforge-review/templates/review-pl-base.md`](../../plugins/codeforge-review/templates/review-pl-base.md) — 참조-time 공통 base SSOT prior art (§결정 4 (b))
- `skills/<slug>/SKILL.md` × 12 — 이전 target surface (ADR-051 결정 2 형식 SSOT)
- `plugins/*/agents/*.md` × 44 — corollary 적용 대상 (반복 블록 3종 실측 surface)
