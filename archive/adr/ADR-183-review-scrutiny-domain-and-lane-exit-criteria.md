---
adr_number: 183
title: 리뷰 심사 정의역 결속 + lane PASS 종결 기준 — FIX 발생 자격 축(scrutiny domain) 신설 (⊥ ADR-181 검증 정의역 V ⊥ §10 원인 판정 축)
status: Proposed
is_transitional: false
category: review-governance
date: 2026-08-17
carrier_story: CFP-3011
related_adrs:
  - ADR-181-verification-domain-deficit-normative  # 미머지 선행 의존 (PR #3000, origin/cfp-2985-fix-telemetry 판독). "검증 정의역"(V = close-time 재검사 도달 범위) 과 본 ADR "심사 정의역"(FIX 발생 자격 범위) 은 동음이의 별 축 — §결정 1 재진술 금지·§결정 4 접합부 선언·§결정 5 admission·§결정 6 advisory 등급 신설 금지·§결정 7 기존 검사 확대 우선·INV-R 축 혼합 금지 전부 인용(pointer only)으로 상속. merge 시 문면 변동 가능 정직 declare
  - ADR-067-fix-ledger-implementability-escalation  # §결정 8 "닫기 게이트 ≠ 카운터 소비" disjoint 형판 인용. §결정 1~4 (max-FIX 카운터·escalation trigger·RESET 권한·cross-lane RESET) = 무접촉 (Epic #3010 child 2 소관) — 본 ADR 은 카운터 소비 빈도에만 간접 영향
  - ADR-154-hard-gate-self-verification-forcing-function  # INV-5 ceiling immutable — semantic 판정(분류 정확성·심사 실질) 기계강제 격상 금지. 신규/확대 검사 = 2-control(§결정 5) + 5-piece chain(§결정 8) 상속
  - ADR-145-ac-traceability-zero-drop-gate  # "심사 완결" 분모 = §5.3 AC coverage_required=Y 재사용 (새 완결 술어 발명 = 2-SSOT 금지). Risk5(tier 오분류 = 강제 약화) 동형 경고 상속
  - ADR-180-story-growth-axis-externalization  # §결정 3 성질 술어(감사 기록물 = 이벤트 로그 계열 §9/§10) pointer 참조만(레지스트리 실물 의존 배선 금지) + §결정 6 배선 형상 제약 5종 + §결정 7 효과 분리 승계. R-5 처방 수신자 Orchestrator 포함
  - ADR-171-evidence-enforceable-promotion-framework  # 신규/확대 검사 warning-first(:172) + registry entry + 승격 3-AND. required-host 충돌 해소 = 본 ADR §결정 10
  - ADR-139-background-wait-liveness-gate  # INV-L2 — 미측정 = INCONCLUSIVE ≠ 잔존 0. 종결 술어의 입력 전제
  - ADR-127-no-exemption-full-flow  # 정의역 한정 = lane 생략 아닌 제3범주 (심사 축소 0 — FIX 발생 권한 라우팅). 면제 0 무손상
  - ADR-119-research-before-claims  # §결정 9 3문 게이트 → follow-up 라우팅 삽입. Amd2 ④ PASS ground-truth — "심사 완결" hollow oracle 방어
  - ADR-044-phase-scoped-sequential-team  # Amd4 §결정 10 검증 floor(≥1 independent peer·SoD·silent degrade 금지) 무손상 declare
  - ADR-008-inter-plugin-contract-versioning  # review-verdict-v4 optional 필드·enum literal 추가 = MINOR bump (additive 선례)
  - ADR-159-requirements-lane-enrichment-and-design-entry-signoff  # §결정 6 정직 라벨 형판 — "분류 presence 는 testable, 분류가 옳은지는 NOT testable"
  - ADR-022-review-decider-model  # Deprecated — review-pl-base.md:133 이 현재형 인용 중 (stale). 처분 = 본 ADR §결정 12-5 (부분 in-scope)
related_files:
  - plugins/codeforge-review/templates/review-pl-base.md  # Phase 2 1차 착지면 — §2 정의역 결속 1문 / §3 판정표 conjunct / §3.4 신설 / :133 정정
  - docs/inter-plugin-contracts/review-verdict-v4.md  # Phase 2 — v4.17 → v4.18 MINOR (optional 필드군)
  - plugins/codeforge-review/agents/DesignReviewPLAgent.md  # Phase 2 — credential-exposure literal + cross-ref
  - plugins/codeforge-review/agents/RequirementsReviewPLAgent.md  # Phase 2 — 동형
  - skills/root-cause-decision/SKILL.md  # Phase 2 — 2-strike 처방-층 전환 별 조항
  - templates/story-page-structure.md  # Phase 2 — §9 verdict embed PASS-라운드 의무화 (:364 개정)
related_stories:
  - CFP-3011
  - CFP-2985  # ADR-181 carrier — 경계 상대 (FIX 닫기 축 / 본 ADR = FIX 열기 축)
  - CFP-2986  # ADR-180 carrier — §9/§10 위치·크기 축 (본 ADR = 심사 자격 축)
  - CFP-2878  # 정상/병리 판별 + 2-strike 층 전환 규범 원본 (§5 Q1 verbatim 승계)
---

## 상태

Proposed — CFP-3011 Phase 1 설계 PR carrier. PL 검수 + 설계리뷰 PASS 후 Accepted 전환.

## 컨텍스트

리뷰 lane FIX 루프의 비수렴 구조 실측 (Story CFP-3011 §1, wrapper origin/main `07ea04163` 시점 20 Story 113 FIX 라운드 전수 분류, 수기 재량 ±5% 정직 선언): FIX 라운드의 67.3% 가 제품 실질 결함이 아닌 검증계 자신(검사도구·오라클 32.7% / 프로세스·서식 29.2% / 감사 기록물 기재 5.3%)에서 발원. 첫 회차 통과 1/20, Story 당 평균 5.65 라운드. 후반 라운드일수록 finding 원료가 감사 기록물(§9/§10)로 이동하는 자기 준거 루프.

구조 원인 2개 (Story §2.1 실측):

1. **심사 정의역 무한정** — 선언면(scope_globs·checklist "리뷰 대상")은 4 lane 전건 기존재하나, 그 선언이 `findings[]` 를 구속하는 필드·규칙이 계약에 0건 (review-verdict-v4.md:169-190 실측). 감사 기록물 발 finding 이 제품 category 를 빌려 위장 유입(category-laundering)해도 발생 시점 라벨이 없어 사후 라우팅 불가.
2. **종결 기준 부재** — PASS = 부재 명제("blocking 없음")뿐, coverage(심사 완결) 명제가 계약 어디에도 없음 (review-pl-base.md:137-143). 종결이 정의상 "관측자 전원 소진"으로만 성립.

핵심 판정 (FeasibilityAgent 실측 승계): **요구 1 의 실체는 선언 신설이 아니라 결속이다.** 선언면을 하나 더 만들면 다섯 번째 선언면만 추가된다. 신설 불가피분은 정확히 1건 — finding→정의역 결속 필드 + 그 필드의 pl_recommendation 산정 결정론 효과.

## 결정

### 결정 1 — 심사 정의역(scrutiny domain) 정의 + 결속 원칙

**심사 정의역** = 각 리뷰 lane 이 FIX 라운드를 발생시킬 수 있는 심사 대상 산출물의 양성 열거 범위. **FIX 발생 자격의 축**이며, 관측(무엇을 읽는가)·검증 실행 도달(ADR-181 V)·재진입 라우팅(§10 `원인 판정`)의 어느 축도 아니다.

- **양성 열거 = 기존 선언 재사용**: 각 lane 의 `scope_globs`(4 PL md 기존값) ∩ `category_enum`(기존값) 이 FIX-eligible 정의역의 양성 열거다. **새 목록을 작성하지 않는다** (다섯 번째 선언면 금지). 열거 밖 = default-out.
- **감사 기록물**(§9/§10 원장·카운터·서식·집계 수치 — ADR-180 §결정 3 "이벤트 로그 계열" 성질 술어 pointer) = out. 단 **좁은 해석**: 서식·표기·집계 표현 축만 out — 기재 진실성·보안 침해 축은 §결정 9 로 in 유지.
- **심사 대상 제외 ≠ 입력 제외**: §9/§10 은 리뷰 입력(증거·판별 재료 — anchor_recurrence 의 §9 grep 경로 포함)으로 계속 읽는다. 제외되는 것은 FIX 라운드를 여는 자격뿐이다.
- **선행 시점 고정**: 정의역 선언은 Story-독립 계약(base·checklist)에 고정되고 PL 은 per-finding **조회**만 한다. 단 정직 잔여 — "조회로 환원"은 재량을 0 으로 만들지 않는다(어느 열거항에 해당하는가의 사상 자체가 semantic). 선행 고정의 실효 = 재량 제거가 아니라 **재량 행사에 근거 인용을 강제**하는 것 (SecurityArch 잔여 선언 승계). "PL 은 결정하지 않는다" 식 과대 진술 금지.
- ADR-127 정합: 정의역 한정 = lane 생략이 아닌 제3범주 — 4 lane 전부 진입·심사 전부 수행, FIX 발생 권한만 라우팅. 심사 축소 0.

### 결정 2 — 결속 필드 `scrutiny_domain` (별 키) + 접합부 선언

review-verdict-v4 `findings[]` 에 신규 **optional** 필드 (MINOR bump v4.17→v4.18, ADR-008 §2):

- `scrutiny_domain: in | out | out-provisional` — **closed-enum 3값**.
  - `in` = FIX-eligible (pl_recommendation 카운트 기여).
  - `out` = 정의역 밖 (기여 0, follow-up/비차단 기록 채널로만 — §결정 7).
  - `out-provisional` = 경계 불확실 잠정 out (인용할 열거 조항이 없는 상태의 정직 표기 — 라운드 종료 시 PL 일괄 판정 의무, §결정 8-3).
- `domain_basis: <string>` (optional) — 분류 근거 조항 인용. `out` 분류 및 "감사표면 경로 ∧ in"(§결정 9 예외 발동) 조합에서 절차상 필수.
- 스키마 카디널리티 축(optional — backward-compat, 기존 producer 비위반)과 집행 축(부재 = RED)은 **분리**한다: "in/out 미분류 finding = 종합 차단"은 review-pl-base §3 절차 규칙이지 스키마 required 가 아니다 (RefactorAgent 양 관측 수렴 채택 — required 격상은 ADR-008 additive 선례를 깨는 breaking).

**접합부 선언 (ADR-181 §결정 4 이행 — 재진술 없이 인용)**: `scrutiny_domain` 은 다음 기존 술어들과 **다른 대상**을 본다 —

| 기존 술어 | 그 술어가 보는 것 | 본 필드가 보는 것 | 값공간 관계 |
|---|---|---|---|
| ADR-181 V (검증 정의역) | close-time 에 실제 재검사한 site 집합 (실행 도달) | finding 발생 시점의 산출물 class 자격 | 교차 키 없음 |
| §10 `원인 판정` enum (CFP-2985 소유) | FIX 재진입 라우팅 lane | FIX 발생 자격 | **별 키 착지 — 같은 enum·같은 집계 키 금지 (ADR-181 INV-R 보존)** |
| `mechanical_category` (review-pl-base.md:145-161) | fast-path 자격 (수정 경량성) | FIX 발생 자격 | 별 키. 상호작용 = §결정 8-5 |
| `valid/noise` (review-pl-base §3) | finding 의 실재성 | FIX 발생 자격 | 별 키. 우선순위 전순서 = noise 판정 선행 → scrutiny_domain 은 valid finding 에만 의미 부하 (noise 는 어느 값이든 기여 0) |

### 결정 3 — pl_recommendation 산정: 기존 판정표에 "정의역 내" conjunct 삽입

- review-pl-base §3 종합 판정표(:137-143)의 P0/P1/P2 카운트 대상을 **"`scrutiny_domain: in` 인 finding"** 으로 한정하는 conjunct 를 삽입한다. **표 shape(행·열) 무변경, 신규 판정표 신설 금지** — :131 "유일한 매핑 SSOT" 선언 무손상 (Story §4.3 E-1 최소 델타).
- **산술 항등 (mechanical floor)**: out/out-provisional finding 의 P0/P1 카운트 기여 = 0. 검증 형식 = `recompute(in-domain findings) == declared pl_recommendation`.
- **P1=1 재량 구간 분기 (TestContractArch 이의 #4 채택)**: P1=1 에서 FIX 와 PASS 가 둘 다 계약 적합이므로(FIX_DISCRETIONARY) 항등 검사는 **P1≠1 구간에서만** 발화한다. P1=1 재량 발동 시 `discretion_rationale`(재량 주체·근거) 기록이 절차상 필수 — 항등 대신 사유 presence 를 강제한다. 이 분기 없이 전 구간 항등을 걸면 정상 재량 PASS 가 거짓 RED (검증계-발원 FIX 재생산).
- FIX_DISCRETIONARY 는 **존치** (F-4) — 폐지하지 않고 근거 기록 의무만 신설.

### 결정 4 — lane PASS 종결 술어 (소진 아닌 상태 명제)

lane PASS = 다음 동시 충족의 명시 판정 (신규 §3.4 로 착지 — 배치 세부는 Change Plan §3, blanket_designrefactor debate 대상):

1. **심사 완결** — 해당 lane 적용분 §5.3 AC 중 `coverage_required=Y` 행 **전수** + packet checklist 전수 심사 선언. 분모 = ADR-145 coverage_required 재사용 (새 완결 술어 발명 = 2-SSOT 금지).
2. **양성 증거 emit** — `examined_count` 와 `required_count` 를 verdict 에 emit 하고 **등식 `examined_count == required_count`** 로 판정한다 (TestContractArch 이의 #5 채택). `>=` 금지 — 부등식 배선은 `examined_count: 999` 를 GREEN 으로 통과시키는 항진이며 분모 부풀리기 게이밍 통로다. 하한 위반(미완결)과 상한 위반(분모 조작) **양방향 RED**. 잔존-0 음성 단독 선언 금지 (vacuous-PASS 반증).
3. **정의역 내 P0/P1 잔존 0** — 단 ADR-139 INV-L2: 미측정 worker = INCONCLUSIVE 로 취급, "잔존 0" ≠ "미측정 0". peer stall/미도달 상태에서 잔존 0 단정 금지.
4. 위 3항 충족 시 **신규 P2 이하 발견의 존재만으로 PASS 를 차단하지 않는다** — P2 는 PASS 와 동시에 follow-up 착지 (§결정 7). P2 개수 cap 없음 (수치 비목표화 — Goodhart 방어).

- **2-control 상속 (ADR-154 §결정 5)**: 완결 판정 장치에 positive-control(coverage_required=Y 행 1개를 examined 에서 의도 제거 → 반드시 RED, curated 1-mutant 상시) ⊕ internal-control identity-probe(파싱한 AC 행 수 emit ↔ sentinel 대조 — 측정 exit code 재사용 금지, 파싱 결과 축) 을 건다.
- **ADR-067 §결정 8 disjoint 형판 인용**: 본 종결 술어는 max-FIX cap 의 **대체가 아니라** 정상 종료 조건의 신설이다. 카운터 소비·escalation trigger 와 disjoint axis — §결정 1~4 무접촉.
- **PASS verdict 의 §9 embed 의무화**: PASS 라운드의 review-verdict yaml embed 는 "권장"(story-page-structure.md:364, CFP-410)에서 **의무**로 승격한다 (PASS 라운드 한정 — FIX 라운드는 권장 유지). 근거 = verdict 는 ephemeral 이고 이를 읽는 CI 가 0 이라(TestContractArch F-1 실측) 종결 양성 증거의 유일한 영속·기계검사 표면이 §9 embed 다. 검사 subject = §9 h3 heading 의 `verdict: PASS` 앵커 조건부 (관행 실재 — 계약화는 Phase 2). 회피 구멍(헤딩에서 verdict 어휘 제거) = 정직 declare, 기계 봉인 주장 금지.

### 결정 5 — 라운드 N+1 정상/병리 판별 (승계 + 정의역 확대, 재발명 금지)

- **판별 기준 = CFP-2878 §5 Q1 verbatim 인용 승계** (회고 2026-08-10 §13.1-15): "라운드 N+1 의 결함이 ⑴ N 이 연 seam 의 마감 누락이거나 ⑵ 새 축이면 계속한다. ⑶ N 이 닫았다고 선언한 축의 재개방이면 병리이며 carrier 분리한다." 재작성 금지 — 인용.
- **검출 기계 술어 = anchor_recurrence 정의역 확대**: review-pl-base §3.2(grep count ≥ 2 → escalation, 현행 DesignReview 단독)를 4 lane 으로 확대한다. 신규 판별 체계 발명 0. §3.2 는 §9 를 읽으므로 결정 1 의 "심사 대상 제외 ≠ 입력 제외"가 이 술어의 생존 전제다.
- **닫은 축 기록 표면 (판별의 실행 전제)**: 라운드 종결 시 그 라운드가 닫았다고 선언한 축을 verdict `closed_axes[]`(anchor_id 배열 — 기존 anchor_id 식별 체계 재사용, 신규 발명 0)로 emit 하고 §9 embed 로 영속한다. 미기록 = 판별 불가가 아니라 기록 의무 위반.
- **병리 판정 이벤트 = Epic child 2 정지 장치의 입력 인터페이스**: 병리 판정(닫힌 축 재개방)은 FIX 라운드를 생성하지 않고(§10 Iter 행 append 0) carrier 분리 또는 escalation 경로로 처리한다. 본 ADR 은 이 **이벤트의 발생 계약까지만** 정의한다 — 그것을 소비하는 카운터·trigger 술어·정지 장치는 child 2 소관 (ADR-067 §결정 1~4 무접촉). 부수 경고 전달 의무: 종결 기준이 3/3 도달 빈도를 낮춰 무력 게이트를 더 조용하게 만들 수 있음 — child 2 착수 packet 에 명시 전달.

### 결정 6 — 2-strike 처방-층 전환 (별 조항 — 축-재개방과 한 칸 합침 금지)

- **CFP-2878 §5 Q1 ⑵ verbatim 승계**: "동일 층의 처방이 2회 연속 새 사각을 낳으면 3번째 처방을 같은 층에서 내지 않는다. 층을 바꾸거나 정지하고 carrier 로 보낸다."
- 착지 = `skills/root-cause-decision/SKILL.md` 기존 "iteration 가설 차별화 원칙" **옆에 별 조항**으로 (기존 "같은 가설 2회 연속 FAIL 시 1차 가정 재분류" = 원인-층 축, 신규 = **처방-층 축** — 두 축을 한 칸에 합치면 판정 불능, Story §2.3·AC-23).
- 처방-층 구분 = **문면 / 값 / 파싱 / 실행** 4값 폐쇄 구분 + "2회 연속" 카운트 술어를 조항 문면에 명시 (AC-23 3연언: 별도 조항 ∧ 층 구분 ∧ 2회 연속 카운트).
- 진단-시점(root-cause-decision) 도구이며 판정-시점(§결정 3/4) 규칙과 파일·owner 분리 유지 — "같은 규칙 두 벌" 금지 (CFP-2878 §5 Q2·CFP-2965 §6 선례).

### 결정 7 — out/P2 finding 라우팅: 3문 게이트 + disposition + drop 폐지

- out·out-provisional·P2 finding 을 follow-up 으로 보낼 때 **ADR-119 §결정 9 3문 게이트** 경유 의무. 미통과 = "관찰됨·미조치 + 사유" 1줄 기록으로 종결. 착지 항목에는 disposition(`tracked` | `observed-only` + 사유) 명시 — silent drop 금지.
- **unclassified drop 경로 폐지 (F-3 확정)**: 현행 "unclassified → 근거 추출 불가 시 findings[] 에서 drop"(review-pl-base:168) 의 **무기록 소거를 폐지**한다. drop 되는 건은 `dropped` 계수 + 1줄 사유(§9 packet 기록)를 의무 동반 — "0건 drop" 도 양성 emit 한다. 근거 = drop 된 건은 정의역 라벨조차 안 붙어 presence 게이트를 원천 통과하는 상류 소거 경로 (SecurityArch T1-b + TestContractArch (f) 독립 수렴). severity 날조로 findings[] 에 강제 잔존시키지는 않는다 (contract enum 무손상 — 계수·사유 기록 동반 제외로 전환).
- **out finding 의 구조 착지 (T1-e)**: out finding 은 findings[] 안에 구조화 잔존시키고(`scrutiny_domain: out`, 기여만 0) §9 산문 단독 착지를 금지한다 — out 기록이 out 정의역에 착지해 아무도 못 보는 자기참조 폐회로 차단.
- **cross-repo 유출 가드**: internal-docs(private) 발 finding 을 wrapper(public) follow-up Issue 로 착지시킬 때 deny-scan 규약(jira-decision-channel 의 deny-scan 계약 동형 — secret·token·절대경로·자격증명 패턴)을 발의 절차에 이식한다 (PRIVATE→PUBLIC 유출 경로 차단, CFP-2984 secret PUBLIC 착지 재현 선례).

### 결정 8 — 분류 게이밍 방어 5종 (SecurityArch 채택분)

1. **라벨↔앵커 정합 술어 (P-B, mechanical floor)**: `scrutiny_domain == out ⟹ findings[].file ∈ 감사표면 경로집합` 을 기계 검사 (고정 prefix 비교, 결정론). `file ∈ 감사표면 ∧ in` 조합 = §결정 9 예외 발동 건 — `domain_basis` 예외 사유 필수. 부수 이득: 라벨 조작이 앵커 조작을 동반해야 하고(위조 비용 상승), 예외 발동이 계수 가능해진다.
2. **single-peer degrade 구간 축소-재량 금지 (T2-c, mechanical floor)**: `peer_degrade.peer_count == 1`(v4.15 기존 필드) 상태에서 P0/P1→P2 하향 또는 in→out 재분류 = 금지(escalation 회부). 견제자 0 구간에서 축소 방향 재량을 산술적으로 차단 — 두 필드 모두 구조화 존재라 결정론 conjunction.
3. **out-provisional 잔존 = 미처리 (P-C)**: 잠정 out 건이 라운드 종료 시 일괄 판정되지 않고 남으면 미처리로 취급 — 잠정이 무흔적으로 최종 굳는 경로 차단. 판정 결과는 기록 표면에 남긴다.
4. **열거 ratchet 비대칭 (P-A)**: 정의역 양성 열거에서 항목 **제거·축소**는 lane 내 판정으로 불가 — ADR/carrier 경유 의무. 추가는 자유 (additive-only 형판, ADR-008 동형).
5. **fast-path 직교성 (T1-c 명시 인수)**: `mechanical_category` fast-path 의 자기회복 전제("분류 잘못이면 다음 iteration 이 발견")는 다음 iteration 이 존재할 때만 성립하는데, 본 ADR §결정 4 가 P2-only PASS 를 명시 허용해 그 전제를 약화시킨다 — 이 사실을 **명시 인수**한다. 완화 = fast-path 자격에 "`scrutiny_domain: out` 과 동시 적용 금지" conjunct 추가 (두 억제 채널 직교성 강제).
- **관측 카운트 (advisory)**: verdict-level `scrutiny_counts` — `{in, out, out_provisional, dropped, noise}` 5-tuple + `ac17_exception` 계수. **presence 만 normative, 값·추이 목표화 금지** (관찰 전용, 목표치 없음 — Goodhart·역-Goodhart 방어). out 분류 남발에 대한 유일한 falsifiable 관측면.

### 결정 9 — 침해 속성 우선 분류 (AC-17 관찰 술어 조작화) + secret 착지면

- 감사 기록물 표면 finding 이라도 **침해 속성** 포함 시 in-domain (표면 위치 기준 분류 금지). 침해 속성 술어는 **의도 무관 관찰 술어**로 정의한다 (T1-a 채택 — "날조·조작" 등 의도 함의 어휘는 산출물 표면에서 판정 불능):
  - 기록값 ≠ 실측 (재현 명령 대조로 확인 가능한 불일치)
  - 기록되어야 할 행/필드의 부재 (결손)
  - 재현 명령 부재 또는 재현 실패 (산출 명령 없는 수치)
  - secret·credential·private 절대경로의 착지
  = **in (의도 불문)**. §10:429 reproducer 패턴(산출 명령 + 결정론 재현)이 판정 기준 형판.
- **정직 잔여 (over-claim 금지)**: 본 술어는 "정합한 날조"(기록값이 실측과 일치하도록 함께 조작된 경우 — finding 자체가 발생하지 않음)를 방어하지 못한다. 다중 관측(AC-14)이 유일한 견제이며 그 견제는 single-peer degrade 구간에서 0 이 된다 (§결정 8-2 가 그 구간을 겨눔). #3006(peer 산출 날조) 의 검출 경로가 자진 신고뿐이었다는 실사건을 상속 리스크로 선언한다.
- **착지 category 신설**: design·requirements-review lane `category_enum` 에 `credential-exposure` literal 추가 (additive MINOR 동형). 현행 실측 — design 12종에 credential 축 0, `credential` literal 은 security lane 에만 있는데 그 lane 은 Story 파일을 안 봄 → AC-17 in 판정이 등록할 category 부재 (category-laundering 역강요) 해소.
- **secret backstop 결손 정직 선언 + 완화 (SecurityArch §7.5 실측 승계)**: 감사 기록물 표면(internal-docs)은 secret scanning DISABLED repo 위에 있다 (2026-08-17 gh api 실측). 완화 4종 — ① internal-docs secret scanning + push protection 활성화 (조직 설정 축 — 본 ADR scope 밖, Orchestrator 실행 권고 항목으로 기록) ② `credential-exposure` literal (위) ③ §10 time-lint 정의역 확대에 secret 패턴 축 1개 (warning-tier, day-1 차단력 0 정직 선언) ④ §10 reproducer 기재 규약 1줄 — "명령은 값 치환형(`$TOKEN`)으로, 실값 금지" (AC-19 가 재현 명령 기재를 늘려 secret 동반 확률을 올리는 신규 압력의 상쇄).

### 결정 10 — 기계검사 이관: 검사 정의역 2분 + repo 좌표 + required-host 충돌 해소

- **검사 정의역 2분 (TestContractArch 이의 #1 채택)**: **D-contract**(계약 문서 자신 — wrapper 파일) / **D-instance**(실 verdict·라운드 인스턴스 — internal-docs Story §9/§10). 이 구분 없이 "기계 강제"를 선언하면 계약 문서 presence 검사가 "모든 finding 이 분류를 동반한다"를 재는 것처럼 위장된다 — `verification-domain-mismatch` class (CFP-2965 P-1) 재현이자 ADR-181 INV-D 위반 형상.
- **repo 좌표 명시 (이의 #2 채택)**: wrapper-self Story 의 §9 기계 커버리지는 현재 **0** (wrapper `docs/stories/` 부재 → wrapper host no-op / internal-docs 에 doc-section-schema workflow 부재 — F-3 실측). 따라서 D-instance 축 host = **internal-docs**(`story-section10-time-lint.yml` 정의역 확대) / D-contract 축 host = **wrapper**(`check_doc_section_schema.py` 정의역 확대 — `docs/inter-plugin-contracts` prefix 기존재). wrapper 쪽만 확대하면 정작 본 Story 가 겨냥한 자기 기록면에 0 효과.
- **required-host 충돌 해소 (이의 #3, A안 채택)**: 기존 host 확대 1순위(ADR-181 §결정 7)와 warning-first(ADR-171:172)가 required-tier host(`doc frontmatter/section schema`·`ac-traceability-matrix` — branch protection 8-tuple) 위에서 충돌한다. 해소 = required host 안에 **exit code 무기여 warning 서브체크**로 착지 — 신규 실패 모드는 `total_fails` 합산 배열(check_doc_section_schema.py:746)에 **넣지 않는** 별도 warning 리스트로 분리(`::warning::` emit only). 승격은 ADR-171 3-AND 별도 경로.
- **부속 전액 상속**: 신규/확대 검사 = ADR-181 §결정 5 admission 3항(registry entry warning 출생 + 미래형 금지 + carrier·만기 병기) + ADR-154 2-control + 5-piece chain(기존 host 확대 시 ①~④ 신규 0, ⑤ discriminating self-test + registry row 는 여전히 의무) + ADR-180 §결정 6 배선 형상 제약 5종. 확대 시 (가) 지정 mutant RED ∧ (나) 형제 site 회귀 0 실증 (ADR-181 §결정 7 승계).
- **착지면 기존 결함 처분 동반**: 이관 착지면의 기존 결함 #3007(§10 시각열 "확인 불가" 표현 부재 → 정직 기록 RED)·#3008(time-lint 검사 정의역 PR 경계 초과)은 이관 델타에 **동반 처분** — 미처분 시 결함 상속.
- **삭제된 검사기 부활 조건**: `check-story-section-9-typed.sh` 는 workflow 부재 theater 판정으로 삭제된 이력(`de63ed014`) — 부활한다면 workflow 동반이 전제조건 (동일 사유 재상속 금지).

### 결정 11 — 집행력 3층 정직 라벨 (ceiling 불변)

| 층 | 내용 | 예 |
|---|---|---|
| **mechanical floor (normative)** | presence·closed-enum·산술 항등·등식·계수 emit·키 disjoint | `scrutiny_domain` presence / enum 값 / out 기여 0 (P1≠1) / examined==required / dropped 계수 / 라벨↔앵커 정합 / degrade-구간 conjunction |
| **review-tier (declared)** | semantic 정확성 — 분류가 옳은가, 심사가 실질인가, 침해 속성인가 | "P0 가 out 으로 밀려나지 않았는가" checklist 의무 |
| **advisory (관측)** | 빈도·추이 — 목표화 금지 | scrutiny_counts 값 / out 남발 추이 / 재량 발동 빈도 |

- 정직 라벨 형판 (ADR-159 §결정 6 동형): **"분류 presence 는 testable, 분류가 옳은지는 NOT testable."**
- **ADR-154 INV-5 ceiling immutable 승계**: 어떤 Amendment 도 분류·완결 판정의 semantic 정확성을 normative(기계강제)로 격상 금지. "100% 기계강제 / hard-gate / 완전 봉인" 표현으로 본 ADR 의 어느 층도 서술 금지.
- advisory **등급** 신설 0 — 위 advisory 는 관측 층위 라벨이지 severity 등급이 아니다 (ADR-181 §결정 6 인용 — 기존 채널 P2 비차단 + follow-up + declared 재사용).

### 결정 12 — 경계 (disjoint/보완 선언)

1. **#2948 (리뷰 실행 파이프라인)**: 본 ADR 은 심사 자격과 종결 술어만 정의하며 리뷰 실행 채널을 지정·변경하지 않는다. #2948 파이프라인은 본 술어의 입력 생산자이고, 술어는 어느 생산 채널의 finding 에도 동일 적용된다. 파일면 실측 — wrapper cfp-2948 브랜치는 review-pl-base 미접촉(ADR 5개뿐), 실 경합 = internal-docs #2746 Change Plan 계획 문면(review-pl-base:101 §2 매트릭스 1행)으로 본 ADR 착지 절(§3/§3.4)과 다른 절 — 선착 merge 후 rebase 정합.
2. **CFP-2985 / ADR-181**: 본 ADR 의 심사 정의역은 ADR-181 검증 정의역 V 와 별개 술어이며 정의를 재진술하지 않고 인용한다. `원인 판정` enum·verification_domain 필드·max-FIX 카운터를 일절 수정하지 않으며 분류 축은 별 키로 착지 (INV-R 보존). ADR-181 = 선행 의존(미머지 — merge 시 문면 변동 가능, 표기 정직).
3. **CFP-2986 / ADR-180**: CFP-2986 은 §9/§10 의 위치·크기 축, 본 ADR 은 심사 자격 축을 소유. 본 ADR 은 물리 배치를 결정하지 않고 CFP-2986 은 FIX 자격을 결정하지 않는다. 게이트 배선 시 ADR-180 §결정 6 형상 제약 + §결정 7 효과 분리 승계. 레지스트리 실물 미착지 — pointer 참조만.
4. **Epic #3010 child 2 (FIX 정지 장치)**: 본 ADR 은 병리 판정 이벤트의 발생 계약까지만 (§결정 5). 카운터·trigger 술어·정지 장치 재설계 = child 2. 본 ADR 이 FIX 발생 자격을 좁혀 카운터 소비율·escalation baseline 이 이동함 + 무력 게이트를 더 조용하게 만들 위험을 child 2 착수 packet 에 전달 의무.
5. **ADR-022 stale 인용 처분 (F-6 — 3문 게이트 판정)**: `review-pl-base.md:133`("Sonnet 이 sonnet_final_status 를 최종 결정" — Deprecated ADR-022 현재형 인용) 은 종결 판정 주체 규정의 전제와 정면 상충(v4 실계약 = "PL pl_recommendation 자체가 final verdict") — 3문 전부 YES → **본 Story Phase 2 정정 대상 in-scope** (:133 1개 문단 한정, v4 현행 문면으로 교체). §5.4/§5.5 의 v3 contract surface 잔재(:462·:469·:486-504·:537·:541·:546-550) = **관찰됨·미조치** — 본 Story 종결 술어(§3.4)가 §5.4 를 참조하지 않도록 격리 배치하는 것으로 오염을 차단하고, 전면 정정은 v4 계약 개정 carrier 발생 시 그 Story 소관 (3문 게이트 ② 불충족 — scope 팽창 > 이득). architecture doc(codeforge-review.md:43)의 ADR-022 인용은 Phase 1 본 커밋에서 historical 표기로 정정.

## 결과

**긍정**: ① FIX 라운드 발생 자격이 결정론 필드로 결속 — 자기 준거 루프(감사 기록물 발 finding 의 위장 유입)의 구조 차단 ② PASS 가 소진이 아닌 상태 명제로 판정 — 신규 P2 가 종결을 인질로 잡지 못함 ③ 병리 재개방이 FIX 라운드 대신 carrier/escalation 으로 라우팅 ④ 게이밍 4경로(severity 축·정의역 축·분모 축·drop 축)에 각각 기계 검사 가능한 방어 배치.

**부정/비용**: ① Phase 2 접촉면이 넓다 (base + 계약 + PL md 2 + checklist 4 + skill 2 + template + host 2 + tests) — 단 계약 의미 변경은 additive MINOR 1회 ② day-1 은 전부 warning-tier — 차단력 0 공백 구간이 존재하며 이는 선언이다 (ADR-171) ③ 분류·완결의 semantic 정확성은 영원히 기계강제 밖 (INV-5 ceiling) — 다중 관측이 유일 견제이고 single-peer degrade 구간에서 그 견제가 0 이 됨을 §결정 8-2 로 부분 완화할 뿐 제거하지 못한다 ④ out 분류 남발 리스크는 관측(계수)으로만 falsifiable — 목표화 금지라 자동 교정 루프 없음 ⑤ ADR-181 미머지 의존 — merge 시 접합부 재검 필요 가능.

**측정 (관찰 전용, 목표치 0 — CFP-2878 confound 차단 승계)**: scrutiny_counts 추이 / 검증계-발원 FIX 비율 / 첫 회차 통과율. 어느 것도 AC·성공 기준이 아니다.

## 해소 기준

N/A — permanent policy (is_transitional: false). 재검토 trigger: ① ADR-181 merge 후 접합부 문면 변동 ② child 2 정지 장치가 병리 이벤트 입력 계약의 개정을 요구 ③ warning→blocking 승격 시점 (ADR-171 3-AND).

## 관련 파일

- `plugins/codeforge-review/templates/review-pl-base.md` — Phase 2 1차 착지면
- `docs/inter-plugin-contracts/review-verdict-v4.md` — v4.18 MINOR (Phase 2)
- `skills/root-cause-decision/SKILL.md` / `skills/fix-ledger-schema/SKILL.md` — §결정 6 착지 / cross-ref
- `plugins/codeforge-review/docs/architecture/codeforge-review.md` — 4 영역 갱신 (Phase 1 동반)
- internal-docs `wrapper/change-plans/cfp-3011-review-scrutiny-domain-exit-criteria.md` — 배치·델타·AC traceability SSOT
