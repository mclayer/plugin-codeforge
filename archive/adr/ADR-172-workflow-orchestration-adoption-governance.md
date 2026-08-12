---
adr_number: 172
title: Workflow 오케스트레이션 채택 거버넌스 + 운영 불변식 (opt-in 세션 선언 / non-substitution / 채택 철회 5-premise / INV-W1~W9 tier 고정 / 무신뢰 데이터 경계 / 정직 천장)
status: Accepted
category: orchestration-discipline  # 신규 category 0 — 기존 재사용 (ADR-RESERVATION row 172 선언 정합)
date: 2026-08-13
carrier_story: CFP-2948
parent_epic: null  # independent Story — 플랫폼 신기능 채택 backlog 4건 중 1건 (#2946/#2947/#2949 sibling backlog 와 번호 경합만 공유)
supersedes: null
amends: null  # new-sibling — ADR-170 Amendment 1 / ADR-141 Amendment 8 / ADR-115 Amendment 2 는 동일 carrier(CFP-2948)의 별도 amendment sibling 이며, 본 ADR 이 흡수하지 않는다.
reinterpretation: false  # ADR-167 §결정 1(b) — 신규 저작(기존 규범의 소급 재해석 아님)
is_transitional: false  # 영구 거버넌스 정책. 채택 유효성이 §결정 3 의 5-premise 에 조건부인 것은 transitional 과 별개 축이다 — 철회는 "해소" 가 아니라 fail-closed 트리거(발화 시 처분 = 본문 해소 기준 절).
related_adrs:
  - ADR-170  # Orchestrator subagent default + inline whitelist. Amendment 1(동일 carrier sibling) = §결정 1 spawn 채널 집합 기술정정. §결정 3(Ownership ≠ Mechanism) + §결정 19(위임 토폴로지 depth 0→1 슬롯) 포섭 논법 = 본 ADR 대안 (c) 채택 근거 — ★§결정 12 는 앵커 아님(writer monopoly 축 — 대안 표 아래 경계 문단 참조)★. §결정 2 whitelist 7-entry closed 무변경(대안 (b) 기각)
  - ADR-141  # tier 정책. Amendment 7 = ≤ ceiling invariant / Amendment 8(동일 carrier sibling) = workflow 채널 negative 집행 형태 확정 — 본 ADR §결정 6 은 그 규범의 소비자(INV-W9 wiring, 중복 규범 아님)
  - ADR-115  # runtime hook enforcement. Amendment 2(동일 carrier sibling) = PreToolUse(matcher:"Workflow") 진입점 게이트 — §결정 1 의 유일 기계 표면 축(상한 = 진입점 1회 차단·기록)
  - ADR-139  # background-wait liveness — INV-L4(워커 self-attestation 차단). INV-W1 은 그 인스턴스(본 ADR 은 인스턴스 선언만, 신규 규범 증식 0)
  - ADR-119  # research-before-claims + 정직 라벨 + §결정 9 제안 필요성 게이트 — §결정 8 정직 천장의 규율 원천
  - ADR-127  # 정식 full 8-lane 비협상 — §결정 2 non-substitution 정합(lane·게이트·FIX 회전 대체 0)
  - ADR-143  # advisory ceiling 정직 라벨 선례 + "spawner-asserted, subagent-unverified" 계열 비검증 귀속 라벨 동형(§결정 8 lane confinement 라벨)
  - ADR-145  # AC-traceability zero-drop 게이트 — §결정 8 의 review-tier 단독 보증 declare 대상(게이트 vacuous 보고 = plugin-codeforge#2951)
  - ADR-109  # in-process 429 mitigation — INV-W8(완화 primitive 의 workflow 내부 미도달 declare) 대조 SSOT
  - ADR-169  # 세션 잔재 수명 규약 — INV-9(제3자 소유 자산 삭제 0). INV-W6 수명 공백 declare 정합(신규 GC 도입 안 함)
  - ADR-126  # on-demand research gate — §결정 4 인접 egress 거버넌스 축("Orchestrator 가 부르니 게이트 만족" 논법 금지의 준거)
  - ADR-124  # 외부지식 충당 3-단계 — egress 처분(stage 계약 declare)의 상위 모델
  - ADR-058  # sunset criteria mandate + §결정 5 약화 evidence-gate — 본 ADR = 강화(ratchet) 방향, 약화 표면 0
  - ADR-013  # dogfood-out — Change Plan(본 ADR 의 SSOT 참조 대상) 소재 repo 근거(mclayer/codeforge-internal-docs)
related_stories:
  - CFP-2948
related_files:
  - archive/adr/ADR-RESERVATION.md  # row 172 — Phase 1(본 Story) 기재 완료. claim 채널 stale 실측 + 복구 기록 포함
  - hooks/hooks.json  # Phase 2 — PreToolUse `Workflow` entry append + capability-gate sibling append (처분 SSOT = ADR-115 Amendment 2)
  - hooks/pretooluse-workflow-optin-gate  # Phase 2 신설 — 진입점 게이트 (deny-at-birth, exit 2)
  - hooks/pretooluse-workflow-agent-capability-gate  # Phase 2 신설 — 파이프라인 내부 능력 경계 (판정 리터럴 = C-2 probe 실측 후 확정)
  - plugins/codeforge-review/workflows/find-verify.js  # Phase 2 신설 — 체크인 정본 스크립트 (§결정 7 lint 정의역)
  - scripts/check-review-pipeline-script.sh  # Phase 2 신설 — 정적 lint thin wrapper (ADR-061 관용구)
  - scripts/lib/check_review_pipeline_script.py  # Phase 2 신설 — 정적 lint 로직 SSOT (§결정 6 negative 검사 포함)
  - CLAUDE.md  # Phase 2 — opt-in 거버넌스 3항 등재 (§결정 1 인지 표면)
  - plugins/codeforge-review/templates/review-pl-base.md  # Phase 2 — packet 선택 필드 매트릭스 1행 (§결정 2 seam)
  - plugins/codeforge-review/agents/CodeReviewPLAgent.md  # Phase 2 — pipeline_output 수신 절 + 무신뢰 인용 데이터 declare (§결정 4 B3)
mechanical_enforcement_actions: []  # Phase 1 doc-only. 기계 표면(hook 2종 + 정적 lint)은 Phase 2 carrier 소관이며, evidence-checks registry 등록(warning 출생 — ADR-171 §결정 5)도 Phase 2. 그마저 상한 = "진입점 1회 차단·기록까지"(§결정 8) — 본 frontmatter 에 선등록하면 선언-실물 불일치가 된다.
---

# ADR-172: Workflow 오케스트레이션 채택 거버넌스 + 운영 불변식

> ★★**경고 — 본 ADR 전체가 1회 probe run 결과에 조건부다**★★ — §결정 3 의 5-premise(U13 · U11 · C-1 · C-2 · U12)는 저작 시점 현재 **전건 미해소/미확인**이며, **하나라도 부정으로 실측 확정되면 Workflow 채택은 철회**되고(`scope_redefinition_required` 회부) 본 ADR 의 §결정 1·4~7 은 규범 대상 자체를 잃는다. ★단 **U12 단독 부정 ∧ leg-1 3-conjunct(C-1·C-2·C-3) 전건 성립** 은 §결정 3 **규범 5** carve-out 대상이며 철회가 아니다.★ 5건은 1회 probe run 으로 동시 해소 가능하다. 본 문서의 어떤 §결정도 이 전제가 "성립한다" 고 서술하지 않는다(ADR-119).

## 상태

**Accepted** (2026-08-13 KST, CFP-2948 Phase 1 carrier). ★단 **조건부 Accepted** — 문서 최상단 경고 블록 + §결정 3 이 유효 조건을 고정한다. probe run 이전의 본 ADR 은 "발효된 규범" 이되 "실증된 채택" 이 아니다.★

동일 carrier(CFP-2948)의 sibling 산출물 3건 — **ADR-170 Amendment 1**(spawn 채널 집합 기술정정) / **ADR-141 Amendment 8**(workflow 채널 tier negative 집행) / **ADR-115 Amendment 2**(PreToolUse `Workflow` matcher 진입점 게이트) — 은 각자의 모 ADR 에 귀속된 **별도 amendment 이며 본 ADR 이 흡수하지 않는다**. 본 ADR 은 그 셋이 다루지 않는 축(채택 조건·철회·운영 불변식·데이터 경계·정직 천장)만 소유한다.

## 컨텍스트

**Workflow 도구** = 스크립트가 계획을 소유하는 결정론적 멀티에이전트 오케스트레이션 — 체크인(또는 런타임 저작)된 JS 스크립트가 `agent(prompt, opts)` 로 워커를 spawn 하고, stage 산출을 schema 로 수집한다. opt-in 경로는 태스크 단위 키워드(P1/P2)·세션 선언 `/effort ultracode`(P3)·named workflow 직접 실행(P4)로 나뉜다 `[source: Claude Code 공식 workflows 문서 — Story CFP-2948 §6.1 PL WebFetch 인용 경유. 본 ADR 저작 세션은 공식문서를 직접 재확인하지 않았다(확실도 high — Story 인용이 verbatim 문면 보유)]`.

**거버넌스 공백(as-is)** — Change Plan §2.4 를 SSOT 로 참조한다: ① `Workflow` 도구 호출의 진입점 관측·audit·deny 표면 부재 ② 예방 leg 을 제공하는 write-gate 배선 부재 ③ 무신뢰 데이터(injection) 경계 부재 ④ run 완결성 ground truth 부재. ★본 절은 그 4건의 수치·실측 문장을 **재기술하지 않는다** — 재기술이 정정 미전파를 낳은 실이력(CFP-2913 계열)이 있으므로, 항목 식별자만 남기고 상세는 Change Plan §2.4 원문이 SSOT 다.★

**1호 적용** = 구현리뷰 lane 의 find→adversarial-verify 파이프라인화(기결정 D3 — Story §5.5). 설계 상세 = Change Plan(§3 to-be / §4 API 계약 / §7 보안 / §8 Test Contract). Change Plan 소재 = `mclayer/codeforge-internal-docs` repo `wrapper/change-plans/cfp-2948-workflow-opt-in-verify-pipeline.md` (dogfood-out — ADR-013).

## 결정

### 결정 1 — opt-in = 세션 1회 선언 (capability gate, Orchestrator 최상위 세션 전용)

Workflow 도구 채택의 opt-in 을 **세션 1회 선언**으로 규범화한다. 운용 정의 = **`/effort ultracode`(P3) 단독 경로**(기결정 D1 — Story §5.5). 호출 주체 = **Orchestrator 최상위 세션 전용**(기결정 D4) — lane agent 의 자가 호출 금지.

- **capability gate 이지 per-call authorization 이 아니다** — 선언은 세션에 능력을 켜는 행위이며 호출 건별 승인이 아니다. 호출별로 남는 것은 **권한 부여가 아니라 audit 기록**(allow/deny 무관 1줄 — Change Plan §7.1.1)뿐이다.
- **미선언 세션 = 기존 dual-peer 경로 자동 선택** — 신규 코드 경로 미발화(Change Plan §3.4 seam). 진입점에서 이를 기계로 받치는 표면 = PreToolUse(matcher `Workflow`) 게이트이며 그 처분·정당화는 **ADR-115 Amendment 2 가 SSOT** 다(본 결정은 정책 규범만 소유).
- **lane confinement 는 정책층 규율이다** — P3 는 세션 전역 능력이며 플랫폼 mechanism 은 lane 을 구분하지 않는다 `[source: Story §2 RR-2 정정 — 공식 문면 "This applies to every task in the session" 인용]`. "P3 를 켜면 구현리뷰만 파이프라인화된다" 는 서술은 **금지**(거짓). 구현리뷰 단일 적용(D3)은 codeforge 가 스스로 지키는 규율 + audit `lane` 필드 사후 검출로만 성립한다(§결정 8 항목 2 의 비검증 귀속 라벨 의무 참조).

### 결정 2 — non-substitution: 파이프라인 = 기존 dual-peer 리뷰의 additive

파이프라인은 기존 dual-peer 리뷰(ClaudeReviewAgent ⊕ CodexReviewAgent, PL 종합)의 **추가(additive)이지 대체가 아니다**(기결정 D2).

- **검증 floor 무손상** — ≥1 independent peer ∧ implementer ≠ certifier 의 floor 를 대체·축소하지 않는다. 축소가 필요한 경우 `peer_degrade` **명시 선언 의무**(silent degrade 금지) — floor 규범의 SSOT = `plugins/codeforge-review/templates/review-pl-base.md` §검증 floor(Change Plan §2.1 앵커).
- **파이프라인 산출물 ≠ independent peer** — stage 산출물은 PL 판정의 **입력**이며 `peer_count` 충족 근거로 **계상 금지**(floor inflation 차단 — Change Plan §3.4).
- **lane·게이트·FIX 회전 대체 0** — 8 lane 시퀀스·`phase:*`/`gate:*`·verdict·FIX Ledger append 는 전부 무변경이고 스크립트 밖 Orchestrator·PL 소유다(ADR-127 정합, Change Plan §3.9).
- run 결손·중단·세션 교체 시 = INCONCLUSIVE 상향 후 **기존 경로 단독 완결** — 기존 경로의 상시 가용성이 additive 설계의 실질 failover 다(INV-W8 대체 경로와 동일 구조).

### 결정 3 — 채택 철회 5-premise (fail-closed stacked) ★본 ADR 전체의 유효 조건★

Workflow 채택은 아래 5-premise 가 **전건 긍정일 때만 유효**하다. **하나라도 부정으로 실측 확정되면 채택을 철회**하고 `scope_redefinition_required` 로 요구사항 층에 회부한다. ★단 하나의 예외 = **규범 5**(U12 단일 carve-out) — 조건·대체 처분이 사전 확정돼 있다.★ 각 premise 의 정의·검증 방법·부정 시 상세 거동의 SSOT = **Change Plan §12.A**(저작 시점 스냅샷에서 §12.A 절 본문은 저작 진행 중 — 5건의 식별과 fail-closed 거동은 Change Plan 헤더·§7.1-b 및 Story §5.3 AC-1a/AC-5 fail-closed 조항·§6.5 U-목록에 이미 실재하며, 본 ADR 은 그 착지 지점을 §12.A 로 참조한다).

| premise | 식별 (정의 SSOT = Change Plan §12.A) | 부정 시 붕괴 지점 | 현재 상태 |
|---|---|---|---|
| **U13** | P3(auto-planned) 경로가 `Workflow` **도구 호출**로 표면화되어 PreToolUse 에 도달하는가 | 진입점 게이트 전체(AC-1a) — ADR-115 Amd 2 실현 전제 | 미확인 |
| **U11** | opt-in 마커 writer 표면(`UserPromptSubmit`)이 `/effort ultracode` 에서 실재 발화하는가 | AC-1a — 상시 deny 붕괴 또는 self-attest 구멍 재개봉 | 미검증 |
| **C-1** | workflow agent 의 도구 호출이 PreToolUse 를 발화하는가 (구 U2) | AC-5 예방 leg | 미확인 |
| **C-2** | 발화 시 hook 입력이 workflow agent 를 판별 가능한 값으로 주는가 | AC-5 예방 leg — deny 판정식 리터럴 확정 불가 | 미확인 |
| **U12** | `agent()` 의 per-agent 도구 allowlist 축소 인터페이스가 존재하는가 | AC-5 leg-2 **도구 축 한정** (★규범 5 carve-out 대상 — leg-1 전건 성립 시 철회 아님★) | 미확인 (문서 침묵 — 반증 아님) |

**철회 트리거 규범** (본 ADR 소유):

1. **판정 기준 = 실측 확정** — 부정은 probe run(또는 동등 firsthand 실측)으로만 확정한다. 미측정·측정 불가는 부정이 아니라 **INCONCLUSIVE**(미측정→PASS 금지, ADR-139 INV-L2 준용)이며, INCONCLUSIVE 상태에서는 채택 실증도 철회도 선언하지 않는다.
2. **완화 금지** — 부정 확정 시 "정직 declare 후 진행" / "deny 를 allow 로 완화" / premise 재정의로 회피하는 경로를 전부 금지한다(Story §5.3 AC-5 fail-closed 조항이 봉쇄한 경로의 ADR-tier 재확인).
3. **철회 처분** — 채택 철회 = 본 ADR `status: Deprecated` 전이 + sibling 3 amendment 의 조건부 실현 조항 발화(각자의 문면이 이미 "부정 시 채택 철회 — ADR-172 §결정 3" 으로 본 결정을 지시한다) + `scope_redefinition_required` 회부. 부분 채택(일부 premise 만 성립한 축소 운용)은 **본 ADR amendment 없이 불가**. ★단 **U12 단일 축**의 부분 채택은 아래 **규범 5** 가 조건·처분을 고정해 사전 승인한다(별도 amendment 불요 — 본 조항이 요구한 승인 절차의 본문 내 이행).★
4. **동시 해소 권고** — 5건은 1회 probe run 으로 동시 해소 가능하므로, 설계리뷰 진입 전(또는 병렬) 실행을 권고한다(Change Plan 헤더 동일 권고).
5. **U12 단일 carve-out (부분 채택 사전 승인)** — ★**U12 단독 부정 확정** ∧ **leg-1 3-conjunct(C-1 · C-2 · C-3) 전건 성립**★ 인 경우에 한해, 처분은 채택 철회가 **아니라** 아래 3항 고정 처분이다:
   - (i) AC-5 leg-2 를 `model` negative **단독 conjunct 로 축소**
   - (ii) **도구 allowlist 축 미보장 declare**(§결정 8 로스터 6 *"파일 쓰기 차단 축"* 과 동일 성질의 정직 declare)
   - (iii) AC-5 ① statement 정정 — *"파일 쓰기 능력 부재"* → *"`Write`/`Edit`/`MultiEdit` 축 차단 ∧ `Bash` 경유 쓰기 미보장 명시"*

   상세 거동 SSOT = Change Plan §7.3 · §8.2-D · §12.A(U12 행).

   **U12 에만 여는 이유** — 나머지 4 premise(U13 · U11 · C-1 · C-2) 부정은 **게이트 자체가 무대상**이 되어 as-is 공백(Change Plan §2.4)이 그대로 남는다 = 채택 전제의 붕괴. U12 부정은 성격이 다르다 — 예방 leg 의 주 담당은 **leg-1(C-3 신규 capability-gate hook)** 이고 U12 는 그 위에 얹는 **추가 축소 수단**이다. 그 추가분의 부재는 *"보호가 사라진다"* 가 아니라 *"보호 범위가 도구 축까지 넓어지지 못한다"* 이며, 잔여는 declare 로 관리된다.

   ★**3중 협착 — 규범 2 무손상**★ — (α) 대상 = **U12 단일 premise**(타 premise 유추 적용 **금지**) (β) 조건 = **leg-1 전건 성립**(C-1·C-2·C-3 중 하나라도 부정이면 본 carve-out **미발동** → 규범 3 철회 그대로) (γ) 대체 처분이 위 (i)(ii)(iii) 로 **사전 확정**돼 발화 시점의 재량 완화가 불가능. ⇒ 본 carve-out 은 규범 2 *"완화 금지"* 의 예외가 **아니라**, 규범 3 이 요구한 승인 절차를 본문에서 미리 이행한 것이다.

   ★**정직 declare**★ — 본 규범 5 는 §결정 3 저작 시점의 blanket 문면이 같은 Story 기착지 설계 판단(Change Plan §7.3 *"leg-1 만 성립하면 leg-2 를 축소"* · §8.2-D 처분 3)과 정면 충돌한 것을 **규범 층에서 해소**한 것이다(설계리뷰 iter1 D-02 택1 결과). 문면 해석으로 덮지 않았음을 명시한다.

### 결정 4 — 무신뢰 데이터 경계: 조립 주체 = 스크립트

리뷰 대상 diff / PR 본문·코멘트 / 코드 주석 / web·MCP 응답 / 사용자 원문(Story §1)을 **무신뢰 구획**으로 규범화하고, stage 프롬프트 조립 시 구획 B 로 감싼다. 상세 계약(B1/B2/B3 흐름 · CFP-2911 R-A~R-D 상속 · nonce late-bound)의 SSOT = **Change Plan §7.2** — 본 결정은 다음 3 규범만 ADR-tier 로 고정한다:

1. **조립 주체 = 스크립트** — 스크립트는 FS·셸 접근이 0 이라 스스로 데이터를 못 읽고, 데이터는 `args` 주입 후 **스크립트가 구획 B 를 조립**한다. ★agent 내부에서 데이터를 취득해 스스로 감싸는 구성은 금지★ — 조립 주체가 곧 오염 대상이 되어 계약이 공허해진다(CFP-2911 "helper 가 유일 write 주체" 불변식 동형).
2. **파생물 무승격** — stage1 산출 전체를 stage2 구획 B 로 재감싼다(B2). verify 의 판정 근거 = 원 아티팩트 재독이며 stage1 텍스트가 아니다.
3. **하류 sink declare** — 파이프라인 산출물을 수신하는 리뷰 PL 에 "무신뢰 인용 데이터" declare 를 의무화한다(B3 — PL 이 새 injection sink 가 되므로).

★정직 상한★ — 본 경계의 완화 tier 상한 = **delimiting**(Spotlighting 계열)이다. *"injection 방어 완료"* 서술 금지(§결정 8).

### 결정 5 — 운영 불변식 INV-W1~W9 규범 승격 + 집행 tier 고정

Change Plan §7.4.0 로스터의 운영 불변식 9건을 본 ADR 규범으로 **승격**한다. ★9건의 내용(판정식·근거 실측·정밀화)은 여기 재기술하지 않는다 — 내용 SSOT = Change Plan §7.4.0(및 §7.4.1~§7.4.8 상세). 본 ADR 이 고정하는 것은 각 불변식의 **집행 tier** 뿐이다.★

| # | 식별 라벨 | 집행 tier (본 ADR 고정) |
|---|---|---|
| **INV-W1** | run 자기보고 금지 | 검출 |
| **INV-W2** | 완결성 ground truth = journal 전수 | 검출 (fail-closed — 위반 = INCONCLUSIVE) |
| **INV-W3** | 결손 run 부분 소비 금지 | 봉쇄 |
| **INV-W4** | 정적 fan-out cap | 예방 |
| **INV-W5** | wall-clock 3층 | 검출·판정 (★예방 없음 — §결정 8 정직 라벨 의무★) |
| **INV-W6** | 세션 경계·수명 공백 | 봉쇄 |
| **INV-W7** | 재시도 통제 (in-script 자동 재호출 금지) | 봉쇄 |
| **INV-W8** | rate-limit 완화 미도달 declare | advisory (정직 declare) |
| **INV-W9** | 모델 tier negative 집행 | 예방 — ★정의역 = "체크인 정본 스크립트에 `model` 키 부재" 축 한정★ (lint fail-closed — §결정 6). ★실행 tier ≤ ceiling **실현**의 보증 아님 — 아래 지위 선언★ |

**INV-W1 지위 선언 (중복 규범 증식 차단)** — INV-W1 은 [ADR-139](ADR-139-background-wait-liveness-gate.md) **INV-L4**(대기 주체 ↔ 판정 주체 분리, worker self-attestation 차단 — `archive/adr/ADR-139-background-wait-liveness-gate.md:71`)의 **인스턴스이지 신규 규범이 아니다**. run 의 `status`/`agentCount`/`summary` 자기보고를 완결성 판정 근거로 쓰는 것 = worker self-attestation 의 workflow 채널 발현형이며, 상위 규범은 ADR-139 가 계속 소유한다.

**INV-W9 지위 선언 + ★예방 tier 의 조건 병기 (설계리뷰 iter1 D-15)★** — 규범 본문 = §결정 6 (ADR-141 Amendment 8 소비). 본 표의 row 는 tier 고정용 참조다. ★단 "예방" 이 덮는 정의역을 아래로 협착한다★:

- **덮는 것** = 체크인 정본 스크립트의 `agent()` `opts` 에 `model` 키가 **존재하면 RED**(fail-closed 정적 lint). 위반 형태 자체가 검출 대상이므로 예방으로 계상한다.
- **덮지 않는 것** = *"워커가 실제로 ≤ ceiling tier 로 돌았다"*. 그 결론은 A8-1 의 **"플랫폼 default = 세션 모델 위임"** 전제 위에 서 있는데, ADR-141 **A8-4.3 자신이** 그 전제를 *"실재하는 유일 관측점은 run meta `defaultModel` 이라는 **run-level 1점**뿐이고, **그 값이 세션 모델과 동일하다는 것 자체가 미확인**이다(확실도 **med**)"* 로 자인한다(`archive/adr/ADR-141-all-opus-single-tier.md:982`). ⇒ 본 예방 tier 를 *"≤ ceiling 이 실현됨"* 의 근거로 인용하는 것을 **금지**한다(§결정 8 로스터 3 과 동일 처분).
- ★**6번째 premise 로 등재하지 않는 이유**★ — 이 전제는 **probe run 으로 결판나지 않는다**(A8-4.3 = per-agent 실행 tier 사후 검증 **불가**). §결정 3 의 premise 값공간은 규범 1(실측 확정)과 규범 4(1회 probe 동시 해소)를 전제하므로, 구조적 미검증 항목을 등재하면 규범 1 에 의해 **영구 INCONCLUSIVE** 가 되어 채택 실증도 철회도 영원히 선언 불가해진다 — 로스터 자체가 사문화된다. ⇒ premise 등재 대신 **본 tier 조건 병기 + §결정 8 로스터 3 재게시**로 처분한다. 이 처분의 성격 = 완화가 아니라 ★**보증 범위 축소(over-claim 제거)**★다.
- **§7.6 자기적용** — Change Plan §7.6 검증 열 규약(*"성립 가정 위의 완화를 성립한 것처럼 쓰지 않는다"*)을 본 tier 표 자신에 적용한 결과다.

### 결정 6 — 모델 tier = negative 집행: `agent()` opts 에 `model` 키를 두지 않는다

workflow 스크립트의 `agent()` `opts` 에 **`model` 키를 두지 않는다** — 키 부재가 곧 집행이다(플랫폼 default = 세션 모델 위임 ⇒ 워커 tier = Orchestrator effective tier 와 동급 ⇒ ADR-141 Amendment 7 의 ≤ ceiling 자동 충족). 명시 지정은 금지한다.

- **근거 (관측 정합)** — probe run 의 per-agent meta 는 `agentType: 'workflow-subagent'`(고정) + `spawnDepth: 1` 2키이며 ★`model` 필드가 부재★한다 `[ArchitectPL firsthand 실측 보고(199/199) — 본 ADR 저작 세션 재현 미수행, 확실도 med-high]`. 즉 세션 모델 상속이 관측 사실과 정합하며, `opts.model` 지정은 ADR-141 Amendment 7 tier-cap 집행점(`min(frontmatter, orchestrator)` — frontmatter 항이 workflow agent 에 부재)을 **우회할 표면을 신설**하는 유일한 수단이다.
- **규범 owner = [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 8** — 그 amendment 가 ≤ ceiling 의 집행 정의역을 workflow 채널(`agent()` opts)로 확장 확정했다(집행 형태 = negative: 키 부재 의무 + 명시 금지 — "집행점을 `opts.model` 로 확장" 한 것이 아니라 그 반대 형태임은 Amendment 8 자신의 문면이 고정한다). 본 결정은 **그 확장분의 소비자**로서 파이프라인 설계 계약(INV-W9 · Change Plan §4.2)에 wiring 하는 것이며 **중복 규범이 아니다** — 문면 상충 시 ADR-141 Amendment 8 이 우선한다.
- **검사 형태** — 정적 lint 는 "`opts` 에 `model` 키 존재 → RED"(fail-closed). 판별력·천장(리터럴 스팟체크 한정 / env override 정의역 밖 / per-agent 실행 tier 사후 검증 불가)은 ADR-141 Amendment 8 A8-3/A8-4 가 SSOT — §결정 8 이 그 천장을 본 ADR 로스터에 재게시한다.

### 결정 7 — 호출 경로 강제: 체크인 정본 지정(named/scriptPath) 경유 + ad-hoc 경로 정의역 밖 declare

정적 lint(스크립트 계약 검사 — Change Plan §3.6)는 **실제로 도는 스크립트가 체크인 정본일 때만 구속력을 가진다**. 체크인 정본이 도는 것은 호출이 그 정본을 지정하는 형태 — named workflow(슬래시 커맨드 `/codeforge-review:find-verify`) 또는 스크립트 경로 지정 — 일 때뿐이다. 따라서:

1. **설계 조건으로 강제** — 구현리뷰 lane 파이프라인 실행은 Orchestrator 의 **명시 named 호출**로 수행한다(Change Plan §3.2 하이브리드 (a): P4 를 실 실행 경로로 승격, P3 세션 선언은 선행 게이트로 유지). 이 경로에서 "체크인 정본 ↔ 실행 스크립트 동일성"(Story §6.5 U9) 질문이 소멸하고 lint 가 CI 에 도달한다.
2. **ad-hoc 경로 = lint 정의역 밖 정직 declare** — P1/P2/P3 auto-plan 이 런타임 저작하는 스크립트는 체크인 정본 lint 의 정의역 밖이다. 이를 감추지 않고 declare 하며, 보완 = 실행 산출물(`~/.claude/projects/` 하위 실물) 대상 2차 lint 병존(Change Plan §3.2 (b) / Story §4.1 RR-4 — **검출이지 예방 아님**).
3. ★over-claim 봉인★ — (1) 은 Orchestrator 준수에 의존하는 **advisory** 경로다(Orchestrator 세션 = 비-PR-enforceable). *"이로써 실행 경로가 100% 결정론적이 된다"* 는 서술 금지. 두 겹(1)+(2) 모두 예방이 아니라 **규율 + 검출**이다.

### 결정 8 — 정직 천장: 기계강제 불가 지점의 advisory 라벨 로스터

기계강제가 불가한 지점 전부에 advisory 라벨 + 사유를 의무화한다. 본 Story 산출물 전반(본 ADR · sibling 3 amendment · Change Plan · Phase 2 구현물)에서 ★*"100% 기계강제"* · *"hard-gate"* · *"injection 방어 완료"* 표현을 금지한다★ (ADR-119 정합, ADR-143 advisory ceiling 선례 동형).

| # | 지점 | tier / 상한 | 사유 |
|---|---|---|---|
| 1 | opt-in 세션 선언 실준수 (§결정 1) | advisory (문서 규범) | Orchestrator 세션 = 비-PR-enforceable. 유일 기계 표면 = ADR-115 Amd 2 진입점 게이트이며 그 상한 = ★진입점 1회 차단·기록까지★(스폰된 agent 의 도구 호출은 정의역 밖 — "Workflow matcher 로 파이프라인을 감시한다" 서술 금지) |
| 2 | lane confinement (D3) | 사후 검출 | mechanism 은 lane 미구분(§결정 1). audit `lane` 값 = ★orchestrator-asserted, hook-unverified★ 라벨 의무(ADR-143 동형 — 검증된 귀속 참칭 금지) |
| 3 | `model` negative lint (§결정 6) | advisory — 리터럴 스팟체크 한정 | 계산 키·spread 우회 가능 + env override 는 정적 lint 정의역 밖 + per-agent 실행 tier 사후 검증 불가 (SSOT = ADR-141 Amd 8 A8-4) |
| 4 | wall-clock (INV-W5) | 검출·판정 — ★예방 없음★ | run 중단 채널 부재. *"wall-clock 상한을 건다"* 서술 금지 (상세 = Change Plan §7.4.3) |
| 5 | injection 완화 (§결정 4) | delimiting tier 상한 | Spotlighting 계열 완화의 구조적 상한 — 완전 차단 아님 (상세 = Change Plan §7.2-a) |
| 6 | 파일 쓰기 차단 축 | `Write`/`Edit`/`MultiEdit` 축 한정 — ★`Bash` 경유 쓰기 미보장★ | 기존 write-gate 가 자인한 공백의 상속 (상세 = Change Plan §7.1-b). "파일 쓰기 능력 부재" 서술 금지(달성 불가) |
| 7 | egress (web·MCP) | stage 계약 declare = advisory / MCP matcher 매칭 = 확인 불가 | 조건부 예방 배선(C-1·C-2 성립 시)이 성립하기 전 *"egress 가 통제된다"* 서술 금지 (상세 = Change Plan §7.2-d) |
| 8 | AC zero-drop 보증 | ★review-tier 단독★ | `ac-traceability-matrix` required 게이트의 vacuous 상태 보고 = plugin-codeforge#2951 `[보고 상태 인용 — 본 ADR 저작 세션 firsthand 재현 미수행]`. 게이트 GREEN 을 본 Story AC zero-drop 의 증거로 계상 금지 — 보증 주체 = 리뷰 lane 판정 |

로스터 밖 신규 기계강제-불가 지점이 Phase 2 에서 드러나면 같은 형식(라벨 + 사유)으로 declare 한다 — declare 누락은 리뷰 P0 대상.

## 대안

| 안 | 내용 | 처분 |
|---|---|---|
| (a) | **채택 안 함** — Workflow 도구를 codeforge 가 쓰지 않는다 | 기각 — 구현리뷰 find 단계의 결정론적 fan-out·schema 수집 가치가 실재하고, 본 ADR 이 그 채택을 5-premise 조건부 + additive 로 좁혀 리스크를 봉쇄한다. 단 ★§결정 3 부정 확정 시 결과적으로 (a) 로 회귀한다★ — 그 경로가 열려 있는 것 자체가 본 채택안의 fail-closed 설계다 |
| (b) | **ADR-170 §결정 2 에 8번째 inline whitelist entry 신설** — Workflow 호출을 inline 허용 목록에 등재 | 기각 — ① entry 7 이 evidence-gate 통과 근거로 제시한 3-조건(monopoly 소형 구조화 append / free-form 0 / 판정 로직 부재)을 free-form prompt + schema VERDICT 를 싣는 workflow 스크립트가 **정면 미충족** ② whitelist entry = "inline 으로 해도 되는 것" 목록이므로 위임 mechanism 을 inline 예외로 등재하는 **범주 오류** (ADR-170 Amendment 1 근거 4 동일 판정 — 7-entry closed 무손상) |
| (c) | **채택 + ADR-170 §결정 3 + §결정 19 포섭 논법 재사용** — workflow 스크립트가 spawn 하는 agent 를 Orchestrator-owned delegate subagent 로 포섭(Ownership ≠ Mechanism), whitelist·writer 정의 신설 0 | ★**채택**★ — 기존 규범(ADR-170 §결정 3 / §결정 19)의 정의가 이미 이 형상을 담고, ADR-170 Amendment 1 이 채널 표기만 정정했다 — 그 amendment 의 **근거 4항** = §결정 2 fail-closed 룰 / 금지 조항 정의역 / §결정 3+§결정 19 / 범주 오류이며 ★§결정 12 는 **미사용**★ `[chief firsthand — ADR-170:532-537 실독]`. 신규 규범 증식 최소(본 ADR 은 기존 규범이 다루지 않는 축만 저작) |

★**포섭 논법의 경계 (설계리뷰 iter1 D-05 — 앵커 협착)**★ — 대안 (c) 의 포섭은 ★**spawn 채널 정합 축 한정**★이다. workflow 스크립트가 spawn 하는 agent 는 §결정 1 의 **subagent 위임 의무를 충족하는 채널**로 포섭될 뿐이며, **writer 정의는 조금도 확장되지 않는다**.

- **§결정 12 를 앵커로 쓰지 않는 이유** — ADR-170 §결정 12 의 실문면은 ADR-031 §14 lane evidence + fix-event-v1 §10 FIX Ledger 의 ★**writer monopoly**★ 를 "Orchestrator-owned delegate subagent 의 self-write" 로 확장 커버하는 조항이다. 그 조항으로 포섭하면 Change Plan §7.1.0 이 ★**반신뢰**★로 분류한 workflow agent 가 Story §10/§14 **self-write 자격자**가 된다 — 신뢰 등급과 write 권한이 정면 모순한다.
- **경계 문면 (규범)** — workflow agent 는 Story **§9 verdict · §10 FIX Ledger · §14 Lane Evidence 에 write 하지 않는다**. 이 3면의 writer 정의는 본 ADR 로 **무변경**이며(ADR-031 / fix-event-v1 / ADR-170 §결정 12 문면 **무접촉**), 파이프라인 산출물은 §결정 2 대로 **PL 판정의 입력**일 뿐이다.
- **정정 성격** — 본 ADR 이 기대는 **amendment 자체(ADR-170 Amendment 1)는 정합**하다. 정정 대상은 그 amendment 를 가리키는 **인용 앵커**뿐이며, 대안 (c) 채택 결론·§결정 1~8 문면은 무변경이다.

## 결과

### 긍정

- as-is 공백 4건(Change Plan §2.4)에 규범이 착지한다 — 진입점 정책(§결정 1, 기계 표면 = ADR-115 Amd 2) / 능력 경계·tier(§결정 5·6) / injection 경계(§결정 4) / 완결성 ground truth(INV-W2 tier 고정).
- **희망적 채택 차단** — §결정 3 이 "미확인 전제 위의 채택" 을 구조적으로 금지한다. 부정 확정 시 거동(철회 + 회부)이 사전에 규범화되어 있어, probe 결과가 나쁠 때 "정직 declare 후 진행" 으로 미끄러질 경로가 없다.
- **Phase 2 구현 계약화** — INV tier 고정(§결정 5)과 negative lint 형태(§결정 6)가 구현 lane 의 판별 기준을 선확정한다(값-blind hollow 검사 유입 차단).
- 신규 규범 증식 최소 — INV-W1 = ADR-139 인스턴스 선언, §결정 6 = ADR-141 Amd 8 소비자, 대안 (c) 포섭 논법으로 whitelist·writer 정의 무접촉.

### 부정 · trade-off

- **P3 의 세션 전역 부작용을 수용한다** — 세션 전역 effort 상승 + 플랫폼 자체 안전 표면 일부 소거(상세·인용 = Story §2 RR-2(c), 재기술 생략). codeforge 측 대체 = 호출별 audit + 능력 경계(AC-5 축) — 대체가 등가라는 주장은 하지 않는다.
- **조건부 상태의 관리 부담** — probe run 전까지 본 ADR 은 "발효-미실증" 상태로 존재하며, 그 사실을 문서 최상단 경고 블록이 상시 노출한다. 해소가 지연되면 설계리뷰가 이 ADR 을 근거로 삼는 판정마다 조건부 단서를 끌고 다녀야 한다.
- **advisory 잔존면이 넓다** — §결정 8 로스터 8건. 이는 은폐가 아니라 declare 로 관리되는 상한이며, "기계강제" 로 오표기하는 순간부터가 결함이다.

### 불변식 (약화 0 확인)

- **신규 required context 0** — branch-protection 8-tuple 무변경 (Phase 1 doc-only).
- **inter-plugin 계약 무변경** — 신규 contract/registry 파일 0 (packet 선택 필드 `pipeline_output` 은 Phase 2 lane 파일 소관이며 verdict envelope 스키마 무접촉 — Change Plan §4.5).
- **신규 category 0** — `orchestration-discipline` 재사용.
- ADR-058 §결정 5 관점 = **강화(ratchet) 방향** — 신규 채택 거버넌스 + fail-closed 불변식의 additive 신설, 기존 규범 완화 표면 0. sunset_justification N/A.

## 해소 기준

N/A — permanent policy (`is_transitional: false`). 채택 철회(§결정 3)는 해소 기준이 아니라 **fail-closed 트리거**다 — 발화 시 처분 = 본 ADR `status: Deprecated` 전이 + `scope_redefinition_required` 회부(§결정 3 트리거 규범 3). 5-premise 전건 긍정 실측 시에는 본 ADR 최상단 경고 블록을 "해소 완료(probe 결과 기록 링크)" 로 갱신하는 amendment 를 동반한다.

## 관련 파일

- `archive/adr/ADR-RESERVATION.md` — row 172 (Phase 1, 기재 완료)
- `archive/adr/ADR-170-orchestrator-subagent-default-inline-whitelist.md` — Amendment 1 (동일 carrier sibling)
- `archive/adr/ADR-141-all-opus-single-tier.md` — Amendment 8 (동일 carrier sibling, §결정 6 규범 owner)
- `archive/adr/ADR-115-runtime-hook-enforcement.md` — Amendment 2 (동일 carrier sibling, §결정 1 기계 표면)
- Change Plan: `wrapper/change-plans/cfp-2948-workflow-opt-in-verify-pipeline.md` (`mclayer/codeforge-internal-docs` — ADR-013 dogfood-out. §2.4 as-is / §7.2 데이터 경계 / §7.4.0 INV 로스터 / §12.A 5-premise 의 SSOT)
- Phase 2 예정 표면 (본 문서는 링크하지 않고 경로 산문 표기만 — Phase 1 dangling 차단): `hooks/hooks.json` · `hooks/pretooluse-workflow-optin-gate` · `hooks/pretooluse-workflow-agent-capability-gate` · `plugins/codeforge-review/workflows/find-verify.js` · `scripts/check-review-pipeline-script.sh` · `scripts/lib/check_review_pipeline_script.py` · `CLAUDE.md` · `plugins/codeforge-review/templates/review-pl-base.md` · `plugins/codeforge-review/agents/CodeReviewPLAgent.md`
