---
adr_number: 141
title: 전 에이전트 opus(1M) 단일 tier 정책 — fable 폐기 + 3-tier 폐지
status: Accepted
category: governance
date: 2026-07-03
carrier_story: CFP-2560
supersedes:
  - ADR-117   # Fable 5 surgical 모델 tier — 본 ADR 이 fable 를 영구 폐기하며 supersede (본체 텍스트는 이력 보존)
is_transitional: false
related_adrs:
  - ADR-042   # Agent model selection policy — §결정 1 3-tier 표 supersede + §결정 3 신규 agent ADR 의무 승계 (Amd19)
  - ADR-057   # Orchestrator opus mandate + 비-opus fallback — §결정 1 흡수 / §결정 2 moot / §결정 4 dead (Amd6 → Superseded)
  - ADR-117   # Fable 5 surgical tier — 본 ADR carrier 로 Superseded (Amendment 3)
  - ADR-058   # ADR sunset criteria mandate — §결정 5 약화 evidence-gate (본 ADR = 3-tier 축소 방향)
  - ADR-064   # is_transitional:false governance 약화 symmetric evidence-gate
  - ADR-063   # marketplace atomic invariant — Phase 2 plugin bump mirrored-field sync
  - ADR-109   # 429 rate-limit mitigation — opus rate-limit 대응 소관 (ADR-057 §결정 2 moot 후 이관 명시)
  - ADR-127   # 정식 full-flow 비협상 + consumer overlay 확장-only (down-tier 불허 정합)
  - ADR-078   # architecture doc lane gate — Amendment 1 A1-5 architecture mirror(codeforge-design.md L39) accuracy 편집 인용
  - ADR-119   # research-before-claims accuracy — Amendment 1 A1-4 framing 정정 + A1-3/A1-5 근본사실·mirror drift accuracy 정정 인용
  - ADR-087   # deploy lane + lifecycle — Amendment 2 A2-4 DeployPL asymmetry 완화(healthcheck 기계화 rollback) 인용
amendment_log:
  - amendment: 1
    carrier_story: CFP-2735
    date: 2026-07-17
    scope: >-
      외부위임·기계적 워커 7종(CodexReviewAgent · RequirementsAnalystAgent · TestAgent ·
      CodebaseMapperAgent · QADeveloperAgent · DataEngineerAgent · InfraEngineerAgent)을
      단일 opus tier 에서 `model: haiku` 로 carve-out (설계 lane 확정 = Amendment 1;
      브랜치명 "Amendment-7" 의 "7" 은 amendment 번호 아닌 대상 에이전트 수).
      (a) 7종 예외 = CFP-2560 sweep(2026-07-03) 직전 의도적 tier 배정(6종 haiku +
      CodebaseMapper sonnet, git 3a8317fc7^ 실측) 복원 성격 — fable↔opus 진동 청산이
      목적이었지 haiku 배정 부정 아님. (b) §결정 5 waiver reversal — 외부위임 래퍼 2종
      (CodexReview·RequirementsAnalyst)을 opus 로 올린 "의식적 waiver" 를 역전(트리거 =
      §해소 기준 재산정 트리거 "사용자 directive 로 tier 다양화 재요구" 발동). (c)
      non-opus-via-amendment 정상화 — amendment 로 carve-out 된 non-opus tier 는 정상
      상태이며, subagent self-refusal guard(#846) rationale 와 결속. (d) framing 정정 —
      opus→haiku delta 는 "품질영향 ≈0" 아닌 "명세-제한 역할의 bounded·consciously-accepted
      tradeoff" (source: Anthropic — Haiku 4.5 SWE-bench Verified 73.3% = Sonnet-4급·Opus
      4.8 미만; "opus orchestrator + 다수 Haiku 4.5 sub-agent" 패턴 endorse; $1/$5 vs Opus
      $5/$25 = 5x 저렴). doer 3종(QADeveloper·DataEngineer·InfraEngineer)은 Change Plan
      §5/§8 명세-제한 저추론. subagent self-refusal guard 필수 번들(#846 정산): subagent 는
      자기 `model:` tier 를 self-check/self-refuse 대상으로 해석 금지 — "전 에이전트 opus
      단일 tier"·"Sonnet/Haiku 세션 중단" 규범 = Orchestrator/거버넌스 scope. guard live
      SSOT = ADR-141(본문) + CLAUDE.md + 7 agent .md body(subagent guaranteed read-surface).
      ADR-141 정책 자체는 철회 아님 — 7종 carve-out 예외만 추가. 상세 = 본문 `## Amendment 1`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 본 amendment 는
      단일-tier uniformity 를 부분 축소(7종 carve-out)하므로 ADR-058 §결정 5 + ADR-064
      §결정 7 약화-evidence gate 대상 — evidence 4축: ① 사용자 directive(tier 다양화
      재요구) = §해소 기준 재산정 트리거 명시 매칭(애매성 0) ② 비용 방향 = 하향
      (opus→haiku = 절감, 약화 아닌 절감 방향) ③ 능력 근거 = Haiku 4.5 SWE-bench Verified
      73.3% + Anthropic "opus orchestrator + Haiku sub-agent" 패턴 endorse 로 대상 7 역할
      (외부위임 2 + 기계-doer 5)의 bounded tradeoff 명시 수용, doer 3종은 명세-제한 저추론
      ④ 재진동 회피 = amendment durable 기록(dormant 보존 아님)으로 fable↔opus 진동 부채
      구조 미재생산 + role-based carve-out(stakes-based dead ADR-042 Amd15/16/17 부활 아님).
      3rd-party pin 정합 = haiku alias `claude-haiku-4-5`(200K 전용, `[1m]` suffix 없음 —
      opus pin 과 비대칭).
  - amendment: 2
    carrier_story: CFP-2748
    date: 2026-07-18
    scope: >-
      중간추론 역할 14종(Group C)을 단일 opus 에서 `model: sonnet` 으로 carve-out
      (Amendment 1 직속 후속 — 사용자 directive "sonnet 으로 전환도 하자"). 14종 = 설계
      단일축 advocate 4(ModuleArchitect · APIContractArchitect · Refactor · ArchitectAnalyst)
      + 요구 델타 1(ChangeImpact) + 배포 실행 3(DeployPL · DeployWorker · DeployReviewWorker)
      + git ops 1(GitOps) + 테스트 실행 2(IntegrationTest · StatefulTest) + preset codegen 3
      (ServiceDeveloper · Backend/FrontendDeveloper). CFP-2560 sweep(2026-07-03) **직전** 의
      ADR-042 Amd7/8/9/16 sonnet 배정 복원 성격(git `3a8317fc7^` 실측 = 14종 전부 sonnet).
      (a) guard sonnet 일반화 — per-agent guard = 각자 자기 tier 명명(14 sonnet agent =
      `sonnet`; Amendment 1 haiku 7 agent = `haiku` 무변경 — "haiku"→"haiku/sonnet" 치환은
      오류), SHARED/blanket SSOT prose 만 tier-agnostic("non-opus(haiku 7 + sonnet 14)")
      일반화. (b) framing 정정 — opus→sonnet delta 는 "품질영향 ≈0" 아닌 bounded·consciously-
      accepted tradeoff(sonnet 은 haiku 보다 tier 실효 크나 sweep-직전 sonnet 판정 역할군).
      (c) DeployPL asymmetry 명시 — 전 PL 중 유일 하향 PL + 비가역 production rollback 단독
      보유, 완화 = ADR-087 healthcheck 기계화 rollback(rule-driven) + DeployReviewPL opus 유지
      (adversarial backstop). (d) §결정 6 overlay-floor 2-clause→3-clause(haiku 7 하한=haiku /
      sonnet 14 하한=sonnet / 그 외 opus 미만 down-tier 불허). 누적 carve-out = Amendment 1
      haiku 7 + Amendment 2 sonnet 14. sonnet tier 부활 ≠ rate-limit fallback machinery 부활 —
      evidence-registry "fallback 대상 0"·"tier-flip 대상 0" dead-mark 보존(단일 tier 폐기
      상속). ADR-141 정책 자체 철회 아님 — 14종 carve-out 예외 추가만. 상세 = 본문 `## Amendment 2`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 본 amendment 는
      단일-tier uniformity 를 추가 축소(14종 carve-out)하므로 ADR-058 §결정 5 + ADR-064
      §결정 7 약화-evidence gate 대상 — evidence 4축: ① 사용자 directive("sonnet 으로 전환도
      하자" = tier 다양화 재요구) = §해소 기준 재산정 트리거 "사용자 directive 로 tier 다양화
      재요구" 명시 매칭(애매성 0) ② 비용 방향 = 하향(opus→sonnet = 절감, 약화 아닌 절감
      방향) ③ 능력 근거 = sweep-직전 ADR-042 sonnet 배정 존재 + sonnet SWE-bench 근거
      (요구사항리뷰 corroborated, source Anthropic 모델 카드)로 14 역할 bounded tradeoff
      명시 수용 — codegen 3(ServiceDeveloper·Backend/FrontendDeveloper) + DeployPL rollback 은
      tier 실효 실재 구간이나 요구사항리뷰 다출처 corroborate(escalate 미발동) ④ 재진동
      회피 = amendment durable 기록(dormant 보존 아님) + role-based carve-out(stakes-gated
      dead ADR-042 §결정 1/Amd15/16/17 부활 아님). 3rd-party pin 정합 = sonnet alias 는
      1M-capable(opus 와 symmetric — haiku 200K `[1m]` 금지 비대칭과 다름); pin 값·`[1m]`
      여부 = 요구사항리뷰 확정치 인용(무출처 정밀 단정 회피 — ADR-119).
  - amendment: 3
    carrier_story: CFP-2782
    date: 2026-07-22
    scope: >-
      deploy agent 4종(DeployPLAgent · DeployWorkerAgent · DeployReviewPLAgent ·
      DeployReviewWorkerAgent) 물리 제거 note — CFP-2782 / ADR-121 Wave 2 로 deploy·deploy-review
      2 lane plugin dir 삭제. Amendment 1/2 carve-out 표 + §결정 prose 가 참조하던 deploy agent 가
      더 이상 실재하지 않음을 기록. (a) Amendment 2 tier 표(sonnet carve-out: DeployPL · DeployWorker ·
      DeployReviewWorker)는 dated Amendment 이력 = Event Sourcing frozen(byte 무변경 — 그 시점
      tier 결정 이력 보존). (b) A2-4 DeployPL asymmetry 단락 + A2-5 Phase-2 실행 범위(L405-408
      deploy CLAUDE.md tier 표 인용) = 삭제 대상 파일 참조라 정합(이미 CFP-2735/2748 Phase 2
      이행분). (c) all-opus §결정 1 = 무영향 — agent 수 감소일 뿐 tier 정책 동일(전 잔존 에이전트 opus
      단일 tier 무변경). (d) ProductionEvidenceDeputy = ADR-141 §결정 6 opus 명시 유지, CFP-2782 로
      codeforge-design CONDITIONAL deputy RELOCATE 회귀(ADR-072 Amendment 5). ADR-141 정책 자체
      철회 아님 — 물리 제거된 4 deploy agent 참조 note 만. 상세 = 본문 `## Amendment 3`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 본 amendment 는 tier
      정책 약화가 아니라 상위 ADR-121 로 물리 제거된 4 deploy agent 의 참조 note 다 — all-opus
      §결정 1(전 에이전트 opus 단일 tier) 무영향(agent 수 감소, tier 동일), Amendment 1/2 carve-out
      표는 frozen 역사 보존(byte 무변경). governance surface 축소 0 — dead-agent reference cleanup.
  - amendment: 4
    carrier_story: CFP-2803
    date: 2026-07-23
    scope: >-
      고레버리지 apex 역할 10종을 opus default 에서 `model: fable`(Claude Fable 5, `claude-fable-5`)
      으로 carve-out — codeforge 재발 실패모드(verify-before-trust 위반 / fabricated-status 보고 /
      born-broken over-PASS)를 표적 타격하는 **고정 named-role 배정**. 10종 = 9× opus→fable(6 lane PL:
      RequirementsPL · RequirementsReviewPL · ArchitectPL · DesignReviewPL · DeveloperPL · CodeReviewPL +
      chief author ArchitectAgent + 개념정립 ResearcherAgent + 프로젝트관리 arbiter PMOAgent) + 1×
      sonnet→fable(IntegrationTestAgent). SecurityTestPLAgent = opus 유지(명시 제외 — Fable cyber 안전
      분류기 refusal 이 보안 lane 실 가치[exec-backed 취약점 탐지] 무력화 = 순손실). (a) §결정 2("fable
      완전 폐기 — dormant 아님") **부분 역전** — §해소 기준 재산정 트리거 2개 동시 충족(사용자 directive
      로 tier 다양화 재요구 + 모델 세대 전환 = Fable 5 GA 2026-06-09 "most capable widely released
      model"). 재도입은 고정 named-role carve-out(dormant toggle 아님)이라 fable↔opus 진동 부채 구조
      미재생산. (b) **"3-tier 자동선택 부활 아님"** — 10 named agent 고정 열거(enumeration)이지 선택
      함수(§결정 3 이 폐기한 stakes-gated lookup + role-pattern 매칭 + re-audit machinery)가 아니다.
      ADR-042 §결정 1 3-tier · Amd15/16/17 stakes-flip = dead 유지. ADR-117(fable surgical, Superseded)
      부활도 아님(다른 근거[failure-mode 표적] · 다른 대상집합). (c) 방향 = **상향**(2배+ 비용, 조율·
      anti-fabrication 강화 획득) — haiku 7 / sonnet 14 하향 carve-out 과 방향 반대. 따라서 약화-evidence
      gate("약화")가 아니라 표적-강화(cost-up but not governance-weakening) 로 프레이밍. (d) self-refusal
      guard(#846 계보) fable 10종 확장 = hard co-requirement(Phase 2). (e) 누적 carve-out = haiku 7 +
      sonnet 10 + fable 10 + opus 14 = 41. **stale "sonnet 14" reconcile: Amendment 2 의 "sonnet 14" 는
      CFP-2782/ADR-121(Amendment 3) deploy agent 3종(DeployPL · DeployWorker · DeployReviewWorker) 물리
      제거로 live count 11 로 감소했고, 본 Amendment 가 IntegrationTest sonnet→fable 로 옮기며 sonnet=10
      확정**(Amendment 2 dated 표는 frozen 무변경 — live 총계만 본 Amendment 가 reconcile). rate-limit
      fallback machinery 부활 아님(ADR-109 / ADR-057 §결정 2 dead 무변경 — server-side *refusal* fallback
      ≠ rate-limit fallback, 별 mechanism). ADR-141 정책 자체 철회 아님 — fable carve-out 예외 추가만.
      상세 = 본문 `## Amendment 4`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 본 amendment 는 tier 정책의
      약화(거버넌스 축소)가 아니라 **표적-강화(cost-up)** 다 — 방향이 Amendment 1/2 하향 carve-out 과
      반대이므로 ADR-058 §결정 5 + ADR-064 §결정 7 약화-evidence gate 의 "약화" 요건에 해당하지 않는다
      (비용 상향 = 거버넌스 약화 아님, 오히려 조율·anti-fabrication 강화). 정당성 evidence: ① §해소 기준
      재산정 트리거 2개 동시 충족(사용자 directive tier 다양화 재요구 + 모델 세대 전환 Fable 5 GA) —
      애매성 0 ② 재진동 회피 = 고정 named-role carve-out(dormant toggle 아님)으로 fable↔opus 진동 부채
      미재생산 ③ 표적성 = apex 10종 한정(finder/leaf/doer/deputy/preset 미배정 — "정점에만" 원칙)으로
      2배+ 비용이 저volume·고가치 지점에만 결속 ④ over-claim 회피 = anti-fabrication 은 프롬프트-달성
      강화 default("nearly eliminated", 기계 보장 아님)로 프레이밍(ADR-119 verify-before-trust 동결).
      3-tier 선택 함수 · stakes-gating · rate-limit fallback machinery 부활 0.
  - amendment: 5
    carrier_story: CFP-2811
    date: 2026-07-24
    scope: >-
      ADR-117 obsolete 외부 제약 서사(구 Amendment 1 CFP-2241 임시 override + 구 Amendment 2
      CFP-2554 원복) 본문 삭제에 따른 **보존지시 한정 override** — §상태(구 L170 "ADR-117 →
      Superseded (본체 텍스트 이력 보존, 삭제 아님)") + §결정 2(구 L228 "ADR-117 본체 텍스트는
      이력 보존한다") 의 보존지시를 obsolete 외부 제약 서사에 한정해 override 한다 (anchor =
      §결정 2 이지 §결정 1 아님 — CFP-2811 요구사항리뷰 F1 정정). paired = ADR-117 Amendment 4
      (Amd3 §결정 3 override + 삭제 집행) + ADR-058 §결정 11(obsolete 사실서사 제거 이중 게이트
      codify). ADR-117 결정 1~5 + Amendment 3(supersede 기록) + 본 ADR §컨텍스트 진동 부채
      ledger(CFP-2241/2554 결정-사실 rows) + plugins 4 CHANGELOG 원복 기록 = 보존 무변경
      (audit trail 무손실 — 의미 손실 0). §결정 2 의 실 substance(fable 폐기 — Amendment 4 가
      이미 부분 역전) 및 Event Sourcing frozen-default 원칙 자체는 무변경 — 보존지시의 적용
      범위 1건 한정 축소만. tier 정책(§결정 1~6) 무접촉. 상세 = 본문 `## Amendment 5`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 본 amendment 는
      tier 정책 무접촉이며 이력-보존지시의 적용 범위 한정 축소(문서 거버넌스 완화 방향)라
      ADR-058 §결정 5 + ADR-064 §결정 7 약화-evidence gate 대상 — evidence: ① 사용자 명시
      비준(CFP-2811 Story §9 Option B sign-off, 2026-07-24 — 애매성 0) ② obsolete 3중 무효화
      (CFP-2554 해소 → 본 ADR fable 폐기 → CFP-2803/Amendment 4 fable 정식 재도입 6.120.0
      live)로 서사가 기술한 상태 불성립 + stale 인과 참조의 하류 드리프트 실증(ADR-042 4곳)
      ③ 결정-사실 substance 는 본 ADR ledger + CHANGELOG + git history 에 완전 복구 가능 —
      외부 append-only 관례의 core concern(substance·이력 무결성) 무손상(ADR-058 §결정 10/11
      정합), silent 삭제 금지(amendment 열거 의무) 준수.
  - amendment: 6
    carrier_story: CFP-2823
    date: 2026-07-24
    scope: >-
      fable-리밋 한정 runtime opus failover 신설 — fable 배정 subagent 10종(Amendment 4
      A4-1 roster: 6 lane PL + ArchitectAgent + Researcher + PMO + IntegrationTest)이
      spawn-시점 거부 또는 실행 중(mid-run) 조기종료로 리밋 계열 신호(ADR-109 §결정 1
      amendment 감지집합 any-match)를 반환하면, Orchestrator(ADR-039 spawn monopoly)가
      동일 입력 패킷 + `model: opus` override 로 **fresh re-spawn 정확히 1회**(Option A
      즉시전환 — fable same-model full-soak bypass) 수행. §결정 2("fable 완전 폐기")의
      dead-mark("rate-limit fallback machinery 부활 0" / A4-6 fable 429 "fallback tier
      부재")를 **fable-리밋 한정 부분 override**(신규 failover 경로 도입) — 단 그 dead
      row 는 frozen dated audit trail 이라 byte 무변경 보존, 본 Amendment 가 override
      SSOT. ADR-057 §결정 2/4 설계 shape 자산 4종 답습(fresh-spawn-only[SendMessage
      resume 금지] / max 1회 per-spawn-attempt 독립 카운터 / §14 전용 태그 KPI 격리 /
      미분류=task-failure silent-fallback 금지) — ADR-057 Superseded 유지(부활 아님,
      sonnet 축 moot 불변, 신규 규범 carrier = 본 Amendment 6). cascade_depth =
      fable→opus hop COUNT-IN(depth 1); opus 착지 후 same-model soak 소진 후 cascade≥2 =
      user manual resume only(ADR-109 §결정 5). §14 전용 신규 태그
      `[rate-limit-failover:fable→opus]`(§10 FIX Ledger 금지, 기존 dead 태그 비합산·별 이름).
      ADR-109 §결정 3 step2 dead slot(구 ADR-057 §결정 2, moot) re-tenant + fable step1
      bypass. 감지 SSOT = ADR-109 §결정 1 Amendment 1(session/usage-limit class 편입).
      상세 = 본문 `## Amendment 6`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 본 Amendment 는
      tier 정책 약화(거버넌스 축소)가 아니라 **운영 연속성 강화**(fable-리밋 시 작업 정지
      공백 메움)다 — 방향 = Amendment 4 "표적-강화(cost-up but not governance-weakening)"
      선례 동형이며, 본 건은 오히려 비용 절반 방향(fable→opus 는 A4 근거상 상시 2배였으나
      failover 는 리밋 시에만 opus, 상시 아님). §해소 기준 재산정 트리거 매칭 = "사용자
      directive 로 tier 다양화 재요구"(§1 verbatim "시도하고 리밋에 걸리면 failover하게하자",
      애매성 0). ADR-058 §결정 5 + ADR-064 §결정 7 evidence-gate: ① 사용자 directive
      애매성 0 ② rate-limit fallback machinery(sonnet 축) 부활 아님 — 별 trigger(fable
      리밋)·별 SSOT(본 Amendment 6)·별 태그([rate-limit-failover:fable→opus]);
      evidence-registry "fallback 대상 0"·"tier-flip 대상 0" dead-mark 무접촉 보존
      ③ 연속성 강화 방향(machinery 재도입 아닌 fable-리밋 공백 메움). 3-tier 자동선택
      부활 0 — Amendment 4 의 10 named-role 고정 enumeration 대상 한정, 선택 함수 아님.
related_files:
  - CLAUDE.md
  - docs/consumer-guide.md
  - docs/orchestrator-playbook.md
  - docs/architecture/codeforge-family.md
---

# ADR-141: 전 에이전트 opus(1M) 단일 tier 정책 — fable 폐기 + 3-tier 폐지

## 상태

Accepted (2026-07-03 KST — CFP-2560 carrier). codeforge family 의 **전 에이전트 model tier 를 단일 `opus`(최신 Opus tier, 1M 컨텍스트 native)로 통일**하고, fable 을 완전 폐기하며, Opus/Sonnet/Haiku 3-tier 선택 기준을 폐지하는 governance SSOT.

본 ADR 은 다음 3개 ADR 을 carrier 로 재편한다:
- **ADR-117** (Fable 5 surgical tier) → **Superseded** (본체 텍스트 이력 보존, 삭제 아님).
- **ADR-042** (Agent model selection policy) → §결정 1 3-tier 표 supersede + Amd15/16/17 tier-flip dead + §결정 3 의무 승계 (Amendment 19).
- **ADR-057** (Orchestrator opus mandate + fallback) → §결정 1 흡수 / §결정 2 moot / §결정 4 dead → 전체 Superseded (Amendment 6).

> **Amendment 1 (2026-07-17 KST, CFP-2735)**: 외부위임·기계적 워커 7종을 단일 opus 에서 `model: haiku` 로 carve-out + subagent self-refusal guard(#846 정산). 아래 §결정 1·§결정 5 의 원문(frozen audit trail)은 그대로 두되, 그 override 는 본문 말미 **`## Amendment 1`** 이 SSOT 이다. 이후 "전 에이전트 opus 단일 tier" 문언은 **"opus default + Amendment 1 carve-out"** 로 읽는다.
>
> **Amendment 2 (2026-07-18 KST, CFP-2748)**: 중간추론 역할 14종(Group C)을 단일 opus 에서 `model: sonnet` 으로 carve-out(Amendment 1 직속 후속) + self-refusal guard sonnet 일반화. 아래 §결정 1·§결정 6 의 원문(frozen audit trail)은 그대로 두되, 그 override 는 본문 말미 **`## Amendment 2`** 이 SSOT 이다. 이후 "opus default + Amendment 1 carve-out" 문언은 **"opus default + Amendment 1(haiku 7) + Amendment 2(sonnet 14) carve-out"** 로 읽는다(누적 carve-out = haiku 7 + sonnet 14).
>
> **Amendment 4 (2026-07-23 KST, CFP-2803)**: 고레버리지 apex 역할 10종을 opus default 에서 `model: fable`(Claude Fable 5) 로 carve-out — §결정 2("fable 완전 폐기") **부분 역전**(고정 named-role, **"3-tier 자동선택 부활 아님"** — enumeration ≠ 선택 함수). 아래 §결정 1·§결정 2·§결정 6 의 원문(frozen audit trail)은 그대로 두되, 그 override 는 본문 말미 **`## Amendment 4`** 이 SSOT 이다. 이후 누적 carve-out 문언은 **"opus default + haiku 7 + sonnet 10 + fable 10 (opus 14) = 41"** 로 읽는다 — **Amendment 2 의 "sonnet 14" 는 Amendment 3(deploy 3종 물리 제거)로 live 11 → 본 Amendment(IntegrationTest sonnet→fable)로 10 으로 reconcile**(Amendment 2 dated 표는 byte-frozen, live 총계만 갱신).
>
> **Amendment 5 (2026-07-24 KST, CFP-2811)**: ADR-117 obsolete 외부 제약 서사(구 Amendment 1·2) 삭제에 따른 **보존지시 한정 override** — 본 §상태 의 "ADR-117 → Superseded (본체 텍스트 이력 보존, 삭제 아님)" 및 §결정 2 의 "ADR-117 본체 텍스트는 이력 보존" 은 이후 **"obsolete 외부 제약 서사(구 Amendment 1·2)를 제외한 본체 보존"** 으로 읽는다. tier 정책(§결정 1~6 substance) 무접촉. §컨텍스트 진동 부채 ledger(CFP-2241/2554 rows) = byte 무변경 보존. 상세 = 본문 말미 **`## Amendment 5`**.
>
> **Amendment 6 (2026-07-24 KST, CFP-2823)**: fable-리밋 한정 **runtime opus failover 신설** — fable 배정 subagent(Amendment 4 roster 10종)가 리밋 계열 신호(ADR-109 §결정 1 amendment 감지집합)를 spawn-시점 거부 또는 mid-run 조기종료로 반환하면 Orchestrator 가 동일 입력 패킷 + `model: opus` override 로 fresh re-spawn 1회(Option A 즉시전환). §결정 2 dead-mark("rate-limit fallback machinery 부활 0")를 fable-리밋 한정 부분 override — rate-limit *fallback* 축(sonnet, dead) 부활 아님(별 trigger·별 SSOT·별 태그 `[rate-limit-failover:fable→opus]`). agent frontmatter·tier 정책(§결정 1~6) 무접촉(runtime spawn-시점 override 한정). 상세 = 본문 말미 **`## Amendment 6`**.

## 컨텍스트

### 사용자 directive (트리거)

2026-07-03 KST, 사용자 directive verbatim: **"fable 안쓸거다. 전부 opus with 1M로 돌려라"**. 이는 CFP-2554 (2026-07-02, 하루 전 fable 원복)의 직접 revert 이자, 이번에는 **영구·전면**(sonnet/haiku 포함) + **1M 컨텍스트 통일**이다.

### fable↔opus 진동 부채 (환경 변화)

fable 과 opus 사이 model tier 가 **2일간 4회 진동**했다 (ContinuityAgent 실측 경고):
- CFP-2134 (2026-06-10) — fable surgical 11 채택 (ADR-117 §결정 1).
- CFP-2241 (2026-06-14) — 미 정부 제약으로 fable→opus 임시 override (ADR-117 Amendment 1, transitional).
- CFP-2554 (2026-07-02) — 제약 해제로 fable 원복 (ADR-117 Amendment 2).
- CFP-2560 (2026-07-03) — 본 ADR, fable 영구 폐기.

이 진동은 dormant 보존(정책은 두되 model alias 만 교체)이 매번 재활성 유혹(4번째 진동)을 남긴 구조에 기인한다. 사용자 directive 는 이 진동 부채를 **완전 청산**(fable 삭제 + 3-tier 기계 소멸)하라는 신호로 해석한다.

### 1M 컨텍스트 인코딩 사실 (요구사항리뷰 lane 확정 — F3)

요구사항리뷰 lane 이 확정한 인코딩 결론(source: 요구사항리뷰 lane, Claude Code v2.1.197 실측):
- Opus 4.8 은 Anthropic API / Max 플랜에서 **server-side 1M 컨텍스트를 native 로 제공**한다 — plain `model: opus` frontmatter 로 1M 이 활성화된다.
- `opus[1m]` suffix frontmatter 도 v2.1.197 에서 동작하나, Pro·credit-gated 플랜에서 hard-fail 위험이 있어(fail-soft 이식성 손실) plain `opus` 를 권장한다. `[1m]` fix-floor 는 미bisect(확인 불가) 이므로 floor 인용 근거로 쓰지 않는다.
- `CLAUDE_CODE_SUBAGENT_MODEL` env 는 **global 단일 override** 라 per-agent roster 를 붕괴시킨다 → 기각.

### 기존 3-tier 정책의 소멸 대상

- ADR-042 §결정 1 = Opus/Sonnet/Haiku 3-tier role-pattern 선택 기준.
- ADR-042 Amd15/16/17 = stakes-gated opus→sonnet tier-flip (ServiceDeveloper / InfraOpArch / DomainAgent).
- ADR-057 §결정 2 = sonnet rate-limit → opus fallback. §결정 4 = fable model-unavailable → opus fallback.
- ADR-117 = fable surgical 11 + Claude Code v2.1.170 floor.

전 에이전트가 opus 단일 tier 가 되면 위 machinery 는 모두 대상(sonnet/fable)이 0 이 되어 무의미해진다.

## 결정

### 결정 1: 전 에이전트 단일 tier = plain `model: opus` (1M native)

codeforge family 의 **모든 lane plugin 에이전트 frontmatter `model:` field = plain `opus`** 로 통일한다 (45 파일). Orchestrator 세션 모델도 `opus` 유지(결정 4). 단일 tier 이탈(특정 에이전트를 opus 아닌 tier 로 두기)은 **본 ADR amendment 를 의무**로 한다.

**인코딩 = plain `opus`** (요구사항리뷰 F3 근거):
- 근거: Opus 4.8 이 Anthropic API/Max 에서 1M native (server-side) 이므로 plain `opus` 로 1M 활성. `[1m]` suffix 는 Pro·credit-gated 플랜 hard-fail 위험(fail-soft 이식성)이라 기각. `CLAUDE_CODE_SUBAGENT_MODEL` env 는 global 단일 override 라 roster 붕괴 → 기각.
- **3rd-party provider pin (Bedrock/Vertex 소비자)**: Anthropic first-party 가 아닌 provider 를 쓰는 consumer 는 overlay 에 `ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8[1m]'` 를 pin 하도록 consumer-guide (Phase 2) 에 안내한다. wrapper self 및 first-party consumer 는 plain `opus` 로 충분.

45 파일 = agents 44 (field-bearing) + ProductionEvidenceDeputyAgent 1 (현 field 부재 → 결정 6 에서 `model: opus` 명시 추가). 실측 AS-IS(origin/main, `grep -rln "^model: <tier>" plugins/`): fable 11 / sonnet 15 / haiku 6 / opus 12 = 44 field-bearing + 1 field 부재.

### 결정 2: fable 완전 폐기 (dormant 아님)

`model: fable` alias 를 codeforge family 에서 **완전 폐기**한다 — surgical 표 / v2.1.170 floor / ADR-057 fallback / SSOT 문장을 모두 청산한다 (dormant 보존 아님). 근거 = fable↔opus 진동 부채(컨텍스트) — dormant 보존은 4번째 진동 유혹을 남긴다.

단 **ADR-117 본체 텍스트는 이력 보존**한다 (Superseded 마킹 + Amendment 3 append). frozen audit trail 원칙 상 과거 결정 시점 서술은 삭제하지 않는다 (Event Sourcing — ADR-042 Amd12 선례).

### 결정 3: 3-tier 선택 기준 폐지 + ADR-042 §결정 3 의무 승계

Opus/Sonnet/Haiku 3-tier role-pattern 선택 기준(ADR-042 §결정 1)을 **폐지**한다. 단일 tier = opus 이므로 role 개별 tier 판정이 불요하다. ADR-042 Amd15(ServiceDev sonnet) / Amd16(InfraOpArch stakes-gated sonnet) / Amd17(DomainAgent financial-invariant-0 sonnet) tier-flip 은 대상 tier(sonnet)가 소멸하므로 **dead** 이다 (ADR-042 Amendment 19 로 dead 마킹).

**신규 agent 도입 의무 승계**: ADR-042 §결정 3("신규 agent 도입 / model 변경 시 ADR 의무")은 본 ADR 로 승계한다 — **신규 agent 는 `model: opus` default 이며, 단일 tier 이탈은 본 ADR amendment 의무**. (ADR-023 lane lifecycle + ADR-037 version bump 와 계속 연동.)

**ADR-042 §결정 2 invariant 의 지위 판정**: §결정 2 는 "Sonnet 으로 fully cover 가능 = role 재정의 시그널"이라는 원칙이었다. 본 ADR 하에서:
- **tier 신호로서는 폐지** — sonnet tier 자체가 없으므로 "Sonnet cover 가능성" 을 tier 선택 신호로 쓸 수 없다.
- **role-정합 원칙으로서는 잔존** — "에이전트 mandate 가 얕으면 role 을 재정의하라"는 설계 규율은 tier 와 무관하게 유효하다. 단, 그 결론이 더는 "model downgrade" 로 이어지지 않고 "mandate 명확화 / role 재편" 으로만 이어진다. 즉 §결정 2 는 tier-선택 함수에서 분리되어 **순수 role-설계 원칙**으로 잔존한다.

### 결정 4: Orchestrator opus mandate 흡수 (ADR-057 §결정 1 carrier 이전)

ADR-057 §결정 1(Orchestrator 세션 모델 = opus 필수, consumer overlay 축소 불가)을 본 ADR 로 흡수한다. CLAUDE.md 세션 개시 체크리스트의 "Orchestrator 모델 = opus" 근거는 유지되며 그 SSOT 만 ADR-141 로 이전한다. 전 에이전트 opus 단일 tier 이므로 Orchestrator opus 는 그 특수 사례가 아니라 정책 전체의 자연 귀결이 된다.

### 결정 5: 외부위임 래퍼 2종 포함 + 의식적 waiver 기록

사용자 "전부" 문언에 따라 외부위임 dispatch 래퍼 2종(RequirementsAnalystAgent · CodexReviewAgent, 현 haiku)도 `model: opus` 로 포함한다. 이는 ADR-042 §결정 1 (b) invariant("opus = 깊은 mandate 를 요구하는 역할") 에 대한 **의식적 waiver** 로 명시 기록한다:
- **uniformity > marginal cost** — 단일 tier 의 운영 단순화(tier 판정 machinery 소멸)가 이 2종의 marginal 비용 상향을 정당화한다.
- **거버넌스 약화 아님** — 이 2종은 비용 상향뿐이며, dispatch role(Claude 측은 prompt 조립·relay, 실 추론은 외부 GPT-5.4) 은 무변경. mandate 재정의 불요.
- **tier 실효 제한적** — 실 추론이 외부 GPT-5.4 이므로 Claude 측 model tier 의 산출물 품질 영향은 제한적임을 기록.

### 결정 6: CC floor + consumer overlay 규율 + ProductionEvidenceDeputy

- **Claude Code floor**: fable floor(v2.1.170)를 폐기하고 **Opus 4.8 인식 최소 버전 = v2.1.154** 로 갱신한다 (source: anthropics/claude-code CHANGELOG v2.1.154 — Opus 4.8 최초 릴리스 ("Opus 4.8 is here!"), 요구사항리뷰 lane 확정). consumer-guide "필수 의존성" 갱신 (Phase 2).
- **consumer overlay down-tier 불허**: overlay 는 opus 미만으로의 down-tier 를 불허한다 (보수 방향만 허용). ADR-127 §결정 6 확장-only 정합.
- **ProductionEvidenceDeputyAgent**: 현재 `model:` field 부재(상속) → **`model: opus` 명시 추가** (Phase 2). model-field 파일 수 44 → **45**.

### 결정 7: dead-path 처리 + Phase 2 실행 범위

**dead-path 처리 (실 파일 제거 0 — live-machinery 존치)**:
- `scripts/check-stakes-tier-gating.sh` (177줄) + `tests/scripts/test-check-stakes-tier-gating.sh` (435줄) = **존치**. env-driven 이고 frontmatter 무결합이라, 삭제 시 `docs/evidence-checks-registry.yaml` 의 `detect_command` 가 broken 된다. 본 ADR 텍스트로 "정책상 dead(전 에이전트 opus 라 flip 대상 0)" 만 판정.
- `docs/evidence-checks-registry.yaml` 2 entry (`stakes-tier-flip-evidence` ~L3267 / `rate-limit-fallback-rate` ~L55) = **존치 + dead 마킹** (Phase 2 에서 description 에 dead-policy 주석). entry 제거 시 `check-tier-downgrade-guard.sh` 가 `tier-downgrade-justification:` 마커를 요구하며 exit1 → CI red 위험 회피.
- `docs/domain-knowledge/concept/stakes-gated-model-tier-baseline.md` = **존치** (역사 참고).
- `rate-limit-fallback-kpi.yml` = 실측 NOT FOUND (registry 가 없는 파일을 참조) — 이 사실을 Phase 2 정리 항목으로 기록만.
- ADR-042 Amd16/17 = ADR 텍스트로 dead 판정만 (기계 정리 0).

**Phase 2 실행 범위 (구현 PR — 본 Phase 1 문서 PR 밖)**:
1. 45 frontmatter `model: opus` 통일 (fable 11 / sonnet 15 / haiku 6 → opus + ProductionEvidenceDeputy field 신설).
2. SSOT 3 문서 fable·stakes-gated·v2.1.170 잔재 청산 (CLAUDE.md L86·88 / consumer-guide L59 / playbook L513-521·547·564).
3. registry 2 entry dead 마킹 (description 주석).
4. plugin bump 9 (wrapper 6.64.0 / design 0.33.0 / develop 0.15.0 / requirements 0.12.0 / review 1.19.0 / pmo 0.5.0 / deploy 1.0.4 / test 1.3.5 / deploy-review 1.0.5).
5. CHANGELOG 갱신 + marketplace sync (ADR-063 atomic invariant).
6. CFP-2134 Epic(#2134 OPEN, fable 채택 Epic) close (실 close = Orchestrator).
7. **stale-mirror 정책 지시문 4개 층 청산** (아래 "stale-mirror 층" 참조).

**stale-mirror 층 (P1-1 — live 정책 지시문, ADR-141 단일 opus 와 정면모순)**:

앞의 "SSOT 3 문서"(CLAUDE.md / consumer-guide / playbook) 외에도, **live normative 지시문**(Sonnet tier 표 / opus fallback / 조건부 tier override / consumer-facing dead schema)이 4개 층에 분산돼 있다. 이들은 dead-path 처리(env-driven·frontmatter 무결합 live-machinery 존치)와 **다른 부류**다 — 리뷰어·소비자가 실제로 읽고 따르는 *지시* 이므로 존치 시 ADR-141 단일 opus 와 정면모순한 정책이 잔존한다. 따라서 **F5(SSOT 3 문서 청산) 동형의 처리 = 청산**(의식적 존치 아님). Phase 2 실행:

- **(a) lane-plugin CLAUDE.md 4파일** — `plugins/codeforge-deploy/CLAUDE.md`(DeployPL/Worker Sonnet 표 + ADR-057 opus fallback 문장) · `plugins/codeforge-deploy-review/CLAUDE.md`(DeployReviewWorker Sonnet 표) · `plugins/codeforge-design/CLAUDE.md`(ModuleArch/APIContractArch/Mapper/Refactor/Analyst 등 Sonnet tier 표) · `plugins/codeforge-test/CLAUDE.md`(IntegrationTestAgent Sonnet 표기). repo 정책상 lane plugin CLAUDE.md = "에이전트 상세 SSOT" → ADR-141(단일 opus)과 모순하는 normative 문장. Phase 2 = tier 열 opus 통일 + ADR-057 fallback 문장 청산. 동 4 lane 의 `docs/architecture/<plugin>.md` mirror(codeforge-deploy.md / codeforge-deploy-review.md / codeforge-test.md)도 동반 정정(architecture doc lane gate — ADR-078 interfaces 영역).
- **(b) agent frontmatter 주석 9파일** — `# rate-limit 시 Orchestrator가 model:opus로 fallback spawn — ADR-057` frontmatter 주석 (ADR-057 §결정2 moot 후 dead 인용). 실측(origin/main, `grep -rln "^# rate-limit 시 Orchestrator" plugins/ --include="*.md"`) = **9파일**: DeployPLAgent · DeployWorkerAgent · DeployReviewWorkerAgent · DeveloperAgent · ServiceDeveloperAgent · BackendDeveloperAgent · FrontendDeveloperAgent · IntegrationTestAgent · StatefulTestAgent. (spec 상 "12파일" 추정은 over-count — line-anchored 주석 정밀 실측 = 9. body prose 산발 ADR-057 인용은 별도 검출 규칙 = `grep -rln "ADR-057" plugins/ --include="*.md" | xargs grep -l "opus.*fallback\|rate.limit"` = 15파일, agent 9 + lane CLAUDE.md·architecture 6 중복). Phase 2 = 주석 제거 또는 "단일 opus tier — fallback 대상 없음(ADR-141)" 로 대체.
- **(c) 조건부 tier 지시문 3파일** — `plugins/codeforge-design/agents/InfraOperationalArchitectAgent.md`(frontmatter 주석 L5-9 low-stakes 4-AND `opts.model:sonnet` override + 본문 "low-stakes shape 표면" subsection, Amd16 dead) · `plugins/codeforge-requirements/agents/DomainAgent.md`(frontmatter 주석 L4-9 financial-invariant-0 sonnet + 본문 "financial-invariant-0 shape mandate 표면" 섹션, Amd17 dead) · `plugins/codeforge-develop/presets/backend-service/agents/ServiceDeveloperAgent.md`(`model: sonnet` frontmatter + "sonnet 구현자" description, Amd15 dead). Phase 2 = `model: opus` 통일(위 항목 1 45-frontmatter 와 교집합) + 조건부 override 지시문/mandate-표면 섹션 청산.
- **(d) `docs/project-config-schema.md`** — L287-323 `story_stakes` 조건부 tier config 블록 + L445-457 `story_stakes` 섹션 설명(dead mechanism 을 live consumer-facing schema 로 노출). Phase 2 = 블록 제거 또는 "ADR-141 로 폐지(전 에이전트 opus 단일 tier — stakes 조건부 tier 소멸)" dead-policy 주석.

## 근거 (Rationale)

### 약화-evidence 3축 (ADR-058 §결정 5 + ADR-064 §결정 7 — is_transitional:false governance 약화 evidence-gate)

비용 거버넌스(3-tier stakes-gating) 축소 = 약화 방향이므로 각 개정 ADR amendment_log row 에 `sunset_justification` 을 의무 기재한다. evidence 3축:

- **(a) 사용자 directive 명확 + 환경 변화** — directive verbatim("fable 안쓸거다. 전부 opus with 1M로 돌려라") 는 애매성 0. 환경 변화 = fable↔opus 2일 4진동 obsolescence(tier 진동 부채) — dormant 보존이 진동을 재생산하는 구조를 청산.
- **(b) 능력 상향 방향 + 운영 단순화** — opus ≥ sonnet/haiku reasoning depth (하향 아닌 상향). stakes-gated / fallback / floor machinery 소멸 = 운영 표면 대폭 축소.
- **(c) fable→opus 11종 = 비용 절반** — fable $10/$50 (input/output per MTok) = opus $5/$25 의 정확히 2배 (source: ADR-117 컨텍스트 실측 인용). 즉 surgical 11종은 오히려 **비용 절반**이다. sonnet/haiku 21+종의 상향 비용은 사용자 명시 수용.

### 채택/기각 옵션 대조

- **옵션 A (전 에이전트 opus 단일 tier) 채택** — 사용자 directive 직접 이행. 진동 부채 완전 청산(fable 삭제 + 3-tier 기계 소멸) + 운영 단순화 + surgical 11 비용 절반. sonnet/haiku 상향 비용은 사용자 수용.
- **옵션 B (현행 유지 — fable surgical + 3-tier) 기각** — 사용자 directive("fable 안쓸거다") 정면 위배. 진동 부채 존속.
- **옵션 C (부분 — fable 만 폐기, sonnet/haiku 3-tier 유지) 기각** — 사용자 "전부 opus" 문언 위배. 3-tier machinery(stakes-gating / rate-limit fallback / 재-audit) 존속으로 운영 단순화 이득 미실현.

## 결과

### 긍정
- model tier machinery 대폭 소멸 (surgical 표 / v2.1.170 floor / fable fallback / sonnet fallback / stakes-gating 3종 / 재-audit 규칙) → 운영·거버넌스 표면 축소.
- fable↔opus 진동 부채 완전 청산 (dormant 재활성 유혹 제거).
- 전 에이전트 1M 컨텍스트 native → 긴 컨텍스트 작업 일관성.
- surgical 11종(fable→opus) 비용 절반.

### 부정 (trade-off)
- sonnet/haiku 21+종 opus 상향 = 토큰 비용 증가 (사용자 명시 수용 — uniformity·1M > cost).
- 외부위임 래퍼 2종(dispatch-only) opus = marginal 비용 상향, tier 실효 제한적 (결정 5 waiver).
- opus rate-limit(429) 위험 재발 시 sonnet fallback 이 더는 없음 → **ADR-109 (429 mitigation)** 소관으로 이관 (ADR-057 §결정 2 moot 후 유일 대응 채널).

### 영향 경계 (블라스트)
- 45 agent frontmatter (fable 11 / sonnet 15 / haiku 6 / opus 12 + ProductionEvidenceDeputy field 신설).
- SSOT 3 문서 (CLAUDE.md / consumer-guide.md / orchestrator-playbook.md).
- stale-mirror 4 층 (P1-1, Phase 2 청산): lane-plugin CLAUDE.md 4 + agent frontmatter 주석 9 + 조건부 tier 지시문 3 + project-config-schema 1 (+ architecture doc mirror 3). §결정 7 "stale-mirror 층" 참조.
- ADR 4 (ADR-141 신규 + ADR-117 Superseded + ADR-042 Amd19 + ADR-057 Amd6→Superseded).
- registry 2 entry (dead 마킹, 존치).
- live-machinery 2 (check-stakes-tier-gating.sh + test, 존치).
- plugin bump 9 + CHANGELOG + marketplace sync.
- architecture doc 1 (codeforge-family.md tier 서술 갱신) + lane architecture mirror 3 (deploy/deploy-review/test — stale-mirror (a) 동반).

## 해소 기준

N/A — permanent policy. 본 ADR 은 전 에이전트 단일 tier 정책의 상시 기준으로 sunset 대상이 아니다. 단 아래 재산정 트리거 발생 시 본 ADR 을 amend 하여 tier 정책을 재산정한다 (ADR-117 동형):
- 모델 세대 전환 (차기 최강 모델 GA / Opus 가격 구조 변동 / 1M 컨텍스트 정책 변경).
- 사용자 directive 로 tier 다양화 재요구.

## 관련 파일

- `CLAUDE.md` — 세션 개시 체크리스트(Orchestrator opus) + "비-opus tier → Opus fallback" 섹션 (Phase 2 청산).
- `docs/consumer-guide.md` — 필수 의존성 CC floor(v2.1.170 → v2.1.154) + fable 문장 청산 + 3rd-party provider pin note (Phase 2).
- `docs/orchestrator-playbook.md` — §3.0.12 fallback + §3.0.12a stakes-gated 절차 (Phase 2 청산/dead 마킹).
- `docs/architecture/codeforge-family.md` — model-tier 서술 앵커 (본 Phase 1 갱신).
- `archive/adr/ADR-117-fable-5-surgical-model-tier.md` — Superseded (Amendment 3).
- `archive/adr/ADR-042-agent-model-selection-policy.md` — Amendment 19 (3-tier supersede + tier-flip dead + §결정 3 승계).
- `archive/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md` — Amendment 6 (§결정 1 흡수 / §결정 2 moot / §결정 4 dead → Superseded).
- `docs/evidence-checks-registry.yaml` — 2 entry dead 마킹 (Phase 2, 존치).
- `scripts/check-stakes-tier-gating.sh` + `tests/scripts/test-check-stakes-tier-gating.sh` — 존치 (live-machinery, 정책 dead).
- 45 agent frontmatter (Phase 2 `model: opus` 통일).

## Amendment 1 (CFP-2735 — 외부위임·기계 워커 7종 opus→haiku carve-out + subagent self-refusal guard)

**날짜**: 2026-07-17 KST · **carrier**: CFP-2735 · **방향**: 단일-tier uniformity 부분 축소(carve-out) + 비용 하향(절감). 본 Amendment 가 §결정 1(전 에이전트 opus)·§결정 5(외부위임 래퍼 opus waiver)의 **override SSOT** 이다 (§결정 1·5 원문 = frozen audit trail, 무손상).

### A1-1. 7종 carve-out (§결정 1 이탈 = amendment 의무 이행)

§결정 1 "단일 tier 이탈은 본 ADR amendment 를 의무" 에 따라, 아래 7 에이전트를 `model: opus` → `model: haiku` 로 carve-out 한다. 이는 CFP-2560 sweep(2026-07-03) **직전** 의 의도적 tier 배정을 복원하는 성격이다(sweep 은 fable↔opus 진동 청산이 목적이었지 haiku 배정 부정이 아님).

| 에이전트 | host plugin | sweep 직전 tier (git `3a8317fc7^` 실측) | Amendment 1 tier | 역할 근거 |
|---|---|---|---|---|
| CodexReviewAgent | codeforge-review | haiku | **haiku** | 실 추론 = 외부 Codex/GPT-5, Claude = packet 검증·prompt 조립·relay·정규화 |
| RequirementsAnalystAgent | codeforge-requirements | haiku | **haiku** | GPT-5.4 래퍼 (실 분석 = `codex exec -m gpt-5.4` 위임) |
| TestAgent | codeforge-test | haiku | **haiku** | 테스트 러너 실행 + PASS/FAIL 구조화 보고 (판정 없음) |
| CodebaseMapperAgent | codeforge-design | **sonnet** | **haiku** | fact source 인용 + structured template, 추론·synthesis 금지 mandate = haiku 정합 (sonnet 대비 한 칸 추가 하향) |
| QADeveloperAgent | codeforge-develop | haiku | **haiku** | 명세(§8 Test Contract)-제한 TDD 코드 작성 |
| DataEngineerAgent | codeforge-develop | haiku | **haiku** | 명세-제한 파이프라인 어댑터/포트/스키마 |
| InfraEngineerAgent | codeforge-develop | haiku | **haiku** | 명세-제한 Docker/compose/설정/운영 스크립트 |

- **7종 외 tier 불변** — Group C(sonnet 단일축 deputy 등) + opus 유지 12종(전 PL·chief author·adversarial 리뷰어·SecurityArch·Researcher·Domain·live 안전 deputy·DeveloperAgent)은 무변경. ADR-141 정책 자체 철회 아님 — carve-out 예외 추가만.
- **role-based ≠ stakes-based** — 본 carve-out 은 role(외부위임·기계-doer) 기준이며, §결정 3 으로 dead 된 stakes-gated tier-flip(ADR-042 Amd15/16/17 — ServiceDeveloper/InfraOperationalArchitect/DomainAgent)을 **부활시키지 않는다**(대상 3종 모두 우리 7종 아님).

### A1-2. §결정 5 waiver reversal (트리거 = §해소 기준 재산정)

§결정 5 는 외부위임 dispatch 래퍼 2종(RequirementsAnalyst · CodexReview)을 "uniformity > marginal cost" 근거로 opus 로 올리며 "**tier 실효 제한적**(실 추론이 외부 GPT-5.4 이므로 Claude 측 model tier 산출물 품질 영향은 제한적)" 임을 **의식적 waiver** 로 기록했다. 본 Amendment 는 그 waiver 를 **역전**한다:

- **트리거**: §해소 기준 재산정 트리거 "**사용자 directive 로 tier 다양화 재요구**" 정확 매칭 (CFP-2735 §1 사용자 요구사항).
- **근거**: §결정 5 가 이미 "tier 실효 제한적" 을 인정했으므로, 이 2종 haiku 하향은 dispatch role(prompt 조립·relay·정규화, 실 추론 외부 GPT-5.4) 무변경 하에 marginal 비용을 절감한다. carve-out 근거가 가장 강한 영역(§결정 5 self-admission).

### A1-3. non-opus-via-amendment 정상화 + subagent self-refusal guard (#846 정산)

- **정상화 규범**: amendment 로 carve-out 된 non-opus(haiku) tier subagent 는 **정상 상태**이다. "전 에이전트 opus 단일 tier" 는 이제 문자적으로 거짓이므로 "**opus default + Amendment 1 carve-out**" 로 읽는다.
- **#846 재무장 리스크**: #846(OPEN, P2)은 haiku tier subagent(TestAgent)가 "Orchestrator = opus 필수" mandate 를 self-check 로 오독해 자기거부(self-refusal)한 실증이다. all-opus 하에선 mooted 됐으나, 7종을 haiku 로 내리면 그 조건이 **재무장**된다 → guard 는 선택이 아닌 **hard co-requirement**(7종 tier 변경과 분리 merge 금지).
- **guard 배치 mechanism 결정 (설계 lane 확정 — AC-2 outcome-binding 충족)**:
  - **근본 사실 (#846 root — firsthand 재확인)**: spawned subagent 는 project(wrapper) `CLAUDE.md` 를 자기 context 에 **"project instructions"로 주입받는다**(설계리뷰 PL·워커·Orchestrator 모두 자기 context 에서 firsthand 확인). **#846 자체가 실증**: TestAgent(subagent)가 self-refuse 한 것은 CLAUDE.md L79 "Sonnet/Haiku 세션이면 중단" 을 **self-read** 했기 때문 = subagent 가 CLAUDE.md 를 읽는다는 직접 증거. 따라서 self-refuse 트리거가 subagent 에 **실제 도달**한다. (구 rationale "subagent 는 wrapper CLAUDE.md 미상속" 은 자기가 인용한 #846 메커니즘과 모순 = ADR-119 위반이라 정정 — OUTCOME(2-layer guard)은 무손상, rationale-accuracy 만 정정.)
  - **채택 (2-layer — 양 layer 모두 subagent 도달 = over-determined coverage)**:
    1. **primary at-source defuse** — **CLAUDE.md L79/L98-99 = subagent 가 실제 읽는 self-refuse 트리거의 규범 옆(at-source) disambiguation**. 오독 유발 문장("Sonnet/Haiku 세션 중단" + "전 에이전트 opus 단일 tier") 바로 옆에서 scope(Orchestrator 세션/거버넌스 한정)를 명확화해 오독을 원천 차단.
    2. **guaranteed reinforcement** — **7 agent `.md` body 각각에 disambiguation 1줄**. agent `.md` 가 곧 subagent 의 system prompt 이므로 **system-prompt-embedded 보장 도달**(agent 개별 명시). AC-2 "≥1 subagent-read layer surface" outcome 충족 — 실제로는 CLAUDE.md·agent md 두 layer 모두 subagent-read 이므로 over-determined.
  - **기각 (considered)**: lane plugin `CLAUDE.md` 에 blanket guard 배치 — 해당 plugin 은 opus·non-opus 에이전트를 혼재 host 하므로 blanket guard 는 over-broad·오독 유발. **per-agent `.md` 정밀 배치가 우월**하여 미채택(단, design plugin CLAUDE.md L61 CodebaseMapper tier 값 정정은 mirror-accuracy 로 별도 수행 — A1-5).
  - **canonical guard 문구 (Phase 2 가 CLAUDE.md + 7 agent .md 로 미러)**:
    - *(subagent-facing, 7 agent .md body)* — "**model tier (ADR-141 Amendment 1)**: 이 에이전트는 ADR-141 Amendment 1(CFP-2735)로 non-opus(`haiku`) tier 로 **의도 배정**된다. wrapper `CLAUDE.md` 의 '전 에이전트 opus 단일 tier'·'Sonnet/Haiku 세션이면 중단' 규범은 Orchestrator 세션/거버넌스 scope 이며, 이 에이전트가 자기 `model:` tier 를 self-check·self-refuse 대상으로 해석하는 것을 금지한다(#846 재무장 차단)."
    - *(Orchestrator-facing, CLAUDE.md)* — "'전 에이전트 opus 단일 tier'·'Sonnet/Haiku 세션 중단' 규범은 Orchestrator 세션·거버넌스 default scope 이다. Amendment 1 carve-out non-opus(haiku) subagent 는 정상 상태이며 self-refuse 대상 아님."
  - **#846 정산**: guard 적용 후 #846 을 fix 방향 (b)(disambiguation guard)로 close/fold 하고 guard 를 fix 로 cross-ref (Phase 2).

### A1-4. framing 정정 (요구사항리뷰 F2 — "≈0" → bounded tradeoff)

CFP-2735 §1 사용자 원문은 opus→haiku 를 "Claude 측 model tier 산출물 품질 영향 ≈0" 으로 서술하나(verbatim·immutable), **본 ADR rationale 는 이를 "품질영향 ≈0" 이 아닌 "명세-제한 역할의 bounded·consciously-accepted tradeoff" 로 프레이밍**한다:
- **source (Anthropic)**: Haiku 4.5 = SWE-bench Verified **73.3%**(Sonnet-4급, Opus 4.8 미만) + Anthropic "opus orchestrator + 다수 Haiku 4.5 sub-agent" 패턴 endorse + 가격 $1/$5 vs Opus $5/$25 (5x 저렴).
- **doer 3종**(QADeveloper·DataEngineer·InfraEngineer)은 Claude 가 실제 코드를 쓰나 Change Plan §5/§8 로 **명세-제한 저추론** 역할이므로 bounded tradeoff 수용 가능. 외부위임 2종 = Claude tier 실효 최소(§결정 5 self-admission). 요구사항리뷰 lane 이 doer 3종 haiku 적합성을 3-way 만장일치 CORROBORATE(escalate 미발동).

### A1-5. Phase 2 실행 범위 (구현 PR — 본 Phase 1 ADR PR 밖)

1. **7 frontmatter** `model: opus` → `model: haiku` (RequirementsAnalyst 는 `# ...codex exec -m gpt-5.4 위임` 주석 보존).
2. **guard 배치** — 7 agent `.md` body disambiguation 1줄(A1-3 subagent-facing) + CLAUDE.md L79/L98-99 scope 명확화(A1-3 Orchestrator-facing).
3. **본문 tier 잔재 재정합** — CodebaseMapperAgent.md L33 `## Mandate boundary (Sonnet tier 정합)` + L35 "Opus tier synthesis pattern" → haiku 정합; RequirementsAnalystAgent.md 본문 L30 "Claude 래퍼(haiku)" = 이미 haiku(frontmatter 정합화로 무손실).
4. **mirror drift 정정** — `plugins/codeforge-design/CLAUDE.md` L61 CodebaseMapper "(opus …)" → haiku; `plugins/codeforge-design/docs/architecture/codeforge-design.md` L39 CodebaseMapper 표값 "Sonnet"(CFP-2560 sweep 미청산 pre-existing drift) → haiku (ADR-078 architecture doc lane gate + ADR-119 accuracy — 두 mirror site 상호 불일치 해소).
5. **SSOT prose 정정** — CLAUDE.md L98-99 + `docs/evidence-checks-registry.yaml` dead-mark 문구(L86 부근 "전 에이전트 opus 단일 tier. sonnet fallback 대상 0")를 "opus default + Amendment 1 carve-out; sonnet fallback 대상 0 불변" 로 정정.
6. **bump/sync** — plugin bump 5(review/requirements/test/design/develop) + wrapper(guard·ADR host) + marketplace mirrored field sync(ADR-063 atomic — sync PR 선행) + CHANGELOG.
7. **consumer-guide haiku pin (AC-8)** — `ANTHROPIC_DEFAULT_HAIKU_MODEL` 계열 안내 추가. pin 값 = `claude-haiku-4-5`(또는 dated `claude-haiku-4-5-20251001`). **`[1m]` suffix 금지** (Haiku 4.5 = 200K 전용, `claude-haiku-4-5[1m]` = invalid model id — opus pin 과 비대칭).
8. **#846 close/fold** + guard cross-ref.

### A1-6. 영향 경계 / accuracy note

- **blast radius**: 7 agent frontmatter + 7 agent .md guard/tier 잔재 + CLAUDE.md(guard·SSOT prose) + design CLAUDE.md·architecture mirror 2 + evidence-checks-registry dead-mark + consumer-guide + 5 plugin bump + marketplace sync.
- **amendment 번호 정정**: 브랜치명 `...ADR-141-Amendment-7-...` 의 "7" = 대상 에이전트 수(7종)이며 amendment 번호 아님. `amendment_log` 실측 = 본 건이 **최초 amendment (Amendment 1)**.
- **§결정6 reconciliation (consumer overlay 하한)**: §결정6 "consumer overlay opus 미만 down-tier 불허"는 Amendment 1 이후 **"각 에이전트 ADR-정의 tier(7 carve-out=haiku, 그 외=opus) 미만 down-tier 불허"** 로 읽는다. 7 carve-out 에이전트의 overlay 하한 = haiku. 보수(상향)만 허용 — 소비자 intent 무변경(overlay 확장-only 정합, ADR-127 §결정6).
- **haiku 429**: haiku 는 opus 와 별도 pool·별도 429 거동 → ADR-109(opus-scoped 429 mitigation) 미적용, fallback tier 부재(단일 tier 폐기 상속). 리스크 낮음(경고) — 운영 관찰 대상.

## Amendment 2 (CFP-2748 — 중간추론 워커 14종 opus→sonnet carve-out + self-refusal guard sonnet 일반화)

**날짜**: 2026-07-18 KST · **carrier**: CFP-2748 · **방향**: 단일-tier uniformity 추가 축소(carve-out) + 비용 하향(절감). Amendment 1(haiku 7)의 **직속 후속** — Amendment 1 A1-1 이 "Group C(sonnet 단일축 deputy 등) … 무변경" 으로 남겨둔 carve-out 후보를 집행한다. 본 Amendment 가 §결정 1(전 에이전트 opus)·§결정 6(overlay 하한)의 **override SSOT** 이다 (§결정 1·6 원문 = frozen audit trail, 무손상). 누적 carve-out = **Amendment 1 haiku 7 + Amendment 2 sonnet 14**.

### A2-1. 14종 carve-out (§결정 1 이탈 = amendment 의무 이행)

§결정 1 "단일 tier 이탈은 본 ADR amendment 를 의무" 에 따라, 아래 14 에이전트를 `model: opus` → `model: sonnet` 으로 carve-out 한다. CFP-2560 sweep(2026-07-03) **직전** 의 의도적 tier 배정(ADR-042 §결정 1 / Amd7/8/9/16 이 판정한 sonnet)을 복원하는 성격이다(sweep 은 fable↔opus 진동 청산이 목적이었지 sonnet 배정 부정이 아님). sweep-직전 tier = `git 3a8317fc7^` 실측 = 14종 전부 sonnet [verified].

| 에이전트 | host plugin | sweep-직전 tier (git `3a8317fc7^`) | Amendment 2 tier | 역할 근거 |
|---|---|---|---|---|
| ModuleArchitectAgent | codeforge-design | sonnet | **sonnet** | boundary axis 통합 단일 advocate (single-mandate advocacy) |
| APIContractArchitectAgent | codeforge-design | sonnet | **sonnet** | API transport contract 단일 advocate |
| RefactorAgent | codeforge-design | sonnet | **sonnet** | decoupling/pattern/interface 구조 3축 advocacy |
| ArchitectAnalystAgent | codeforge-design | sonnet | **sonnet** | 변경 전 기존 설계(ADR/Change Plan/Story) 분석 단일 축 |
| ChangeImpactAgent | codeforge-requirements | sonnet | **sonnet** | src/** AS-IS → DELTA 매핑 |
| DeployPLAgent | codeforge-deploy | sonnet | **sonnet** | blue-green 실행 lead + **비가역 rollback 판정 단독 보유 — scrutiny (A2-4)** |
| DeployWorkerAgent | codeforge-deploy | sonnet | **sonnet** | 9-step 마이그레이션 sequence 실행 |
| DeployReviewWorkerAgent | codeforge-deploy-review | sonnet | **sonnet** | smoke/성능 baseline 측정 worker |
| GitOpsAgent | codeforge-pmo | sonnet | **sonnet** | git 오케스트레이션(branch tree/worktree/merge sequence) |
| IntegrationTestAgent | codeforge-test | sonnet | **sonnet** | Epic 통합테스트 실행 |
| StatefulTestAgent | codeforge-test | sonnet | **sonnet** | §8.5 stateful test 실행 |
| ServiceDeveloperAgent | codeforge-develop (presets/backend-service) | sonnet | **sonnet** | consumer backend 앱 코드 작성(codegen) |
| BackendDeveloperAgent | codeforge-develop (presets/webapp) | sonnet | **sonnet** | consumer webapp backend 코드 작성(codegen) |
| FrontendDeveloperAgent | codeforge-develop (presets/webapp) | sonnet | **sonnet** | consumer webapp frontend 코드 작성(codegen) |

- **14종 외 tier 불변** — Amendment 1 haiku 7종은 무변경(haiku 유지) + opus 유지 core(전 PL 중 DeployPL 외 전원·chief author ArchitectAgent·adversarial ClaudeReviewAgent·SecurityArchitect·Researcher·Domain·Feasibility·Continuity·live 안전 deputy(LiveOps/LiveOrdering/InfraOperationalArch)·DataArchitect·TestContractArch·**DeveloperAgent**(production 코드))도 무변경.
- **role-based ≠ stakes-based** — 본 carve-out 은 role(중간추론 단일축 advocate / 시퀀스 실행 / codegen) 기준이며, §결정 3 으로 dead 된 stakes-gated tier-flip(ADR-042 Amd15/16/17 — ServiceDeveloper/InfraOperationalArchitect/DomainAgent)을 **부활시키지 않는다**. ADR-042 §결정 1 3-tier 선택 기준 자체 재도입도 아님 — 대상별 amendment carve-out 형식이다.

### A2-2. §결정 5 관계 (외부위임 래퍼 + DeveloperAgent OOS)

- **§결정 5(외부위임 waiver)는 이미 Amendment 1 A1-2 가 reversal** — dispatch 래퍼 2종(RequirementsAnalyst · CodexReview)을 haiku 로 내렸다. Amendment 2 는 그 2종을 **미접촉**(haiku 유지).
- **DeveloperAgent = OOS(opus 유지)** — production 애플리케이션 코드 작성 역할은 sweep-직전 tier 가 fable/premium 이었고 본 Amendment 하향 대상이 아니다. codegen 3종(ServiceDeveloper/Backend/FrontendDeveloper)은 preset codegen(단일 preset scope 명세-제한)이라 carve-out 하나, DeveloperAgent(범용 production 로직)는 opus 유지로 구분한다.

### A2-3. guard sonnet 일반화 (핵심 설계 결정)

#846 재무장 차단 guard 는 Amendment 1 A1-3 이 확립한 2-layer mechanism(CLAUDE.md at-source defuse + per-agent `.md` body)을 **재사용**한다(신규 mechanism 0). Amendment 2 는 그 guard 문언을 sonnet carve-out 을 커버하도록 다음 규칙으로 일반화한다:

- **per-agent guard = 각자 자기 tier 명명** — 14 sonnet 에이전트 `.md` body 는 canonical 문구에 `non-opus(`sonnet`)` substitution 을 배치한다. **Amendment 1 haiku 7종의 guard 는 "haiku" 그대로 무변경** — "haiku" 를 "haiku/sonnet" 로 바꾸면 오류다(각 agent 는 자기 tier 만 명명; guard 는 자기 tier self-refuse 방지가 목적이라 타 tier 열거 불요). 회귀 금지 scope 7 haiku 파일 = CodebaseMapper · DataEngineer · InfraEngineer · QADeveloper · RequirementsAnalyst · CodexReview · TestAgent.
- **SHARED/blanket SSOT prose 만 tier-agnostic 일반화** — 여러 tier 를 총괄 서술하는 prose(`CLAUDE.md` L79·L98-99 · `docs/architecture/codeforge-family.md` L36 · `docs/evidence-checks-registry.yaml` · `docs/consumer-guide.md`)는 "non-opus(haiku 7 + sonnet 14)" 로 일반화한다.
- **#846 재무장 리스크 — sonnet 은 haiku 보다 self-refuse 표면이 더 큼**: `CLAUDE.md` L79 mandate 가 "**Sonnet**/Haiku 세션이면 중단" 으로 **Sonnet 을 명시 지칭**한다. 따라서 sonnet subagent 가 이 규범을 self-read 해 자기거부할 표면이 명명돼 있음 → guard sonnet 일반화 = hard co-requirement(14 frontmatter 하향과 분리 merge 금지). 근본 사실(subagent 가 project `CLAUDE.md` 를 "project instructions" 로 주입받음 = #846 실증)은 Amendment 1 A1-3 확립 자산이라 재도출 대상 아님.
- **canonical guard 문구 (Phase 2 가 14 sonnet agent `.md` body 에 배치 — Amendment 1 A1-3 verbatim + sonnet substitution)**:

  > **model tier (ADR-141 Amendment 2)**: 이 에이전트는 ADR-141 Amendment 2(CFP-2748)로 non-opus(`sonnet`) tier 로 **의도 배정**된다. wrapper `CLAUDE.md` 의 '전 에이전트 opus 단일 tier'·'Sonnet/Haiku 세션이면 중단' 규범은 Orchestrator 세션/거버넌스 scope 이며, 이 에이전트가 자기 `model:` tier 를 self-check·self-refuse 대상으로 해석하는 것을 금지한다(#846 재무장 차단).

### A2-4. framing 정정 (ADR-119 — "품질영향 ≈0" 금지)

CFP-2748 §1 사용자 원문은 opus→sonnet 을 비용 절감으로 서술하나, **본 ADR rationale 는 이를 "품질영향 ≈0" 이 아닌 "명세/단일축-제한 역할의 bounded·consciously-accepted tradeoff"** 로 프레이밍한다(Amendment 1 A1-4 선례 동형). sonnet 은 haiku 보다 tier 실효가 크나 sweep-직전 ADR-042 가 이미 sonnet 으로 판정한 역할군이다.

- **source (요구사항리뷰 corroborated — source: Anthropic 모델 카드)**: 현세대 Sonnet 은 SWE-bench Verified 가 Opus 와 근소차(수 pt 이내) 구간이며 가격은 약 40% 저렴(sonnet ≈$3/$15 vs opus $5/$25 per MTok). **정확한 세대별 수치는 요구사항리뷰 확정치 인용이며, 본 ADR 은 과도한 정밀 단정을 회피한다(ADR-119 abstention — 무출처 firsthand 단정 금지).**
- **DeployPL asymmetry 명시 (codegen 3종과 동일취급 금지)**: DeployPL 은 **전 PL 중 유일 하향 PL + 비가역 production rollback 결정을 단독 보유**하는 asymmetry 를 지닌다. 이 asymmetry 는 다음 2중 완화와 함께 bounded tradeoff 로 기록한다 — ① **ADR-087 healthcheck 기계화 rollback**(rule-driven·자동, open-ended 추론 아님 → tier 실효가 rollback 정확도에 미치는 영향 제한) ② **DeployReviewPL opus 유지**(adversarial backstop — 하향 안 된 opus PL 이 배포 후 검토를 담당). codegen 3종(preset 명세-제한) + DeployPL rollback = AC-5 escalate 경로 대상이었으나 요구사항리뷰가 다출처 corroborate(escalate 미발동).

### A2-5. Phase 2 실행 범위 (구현 PR — 본 Phase 1 ADR PR 밖, **열거만**)

under-enumeration 이 지배 실패축(Amendment 1 self-ref 교훈)이므로 누락 0 로 전 site 를 열거한다(Change Plan §3 SSOT). 실 실행은 별도 Phase 2 PR:

1. **14 frontmatter** `model: opus` → `model: sonnet` (plain alias — sweep-직전 형식과 동일).
2. **guard 배치** — 14 sonnet agent `.md` body 각각에 A2-3 canonical 문구(sonnet-facing) 추가.
3. **DELTA-C frontmatter comment 정정 (8 site)** — `# 단일 opus tier — fallback 대상 없음` 주석이 sonnet carve-out 후 거짓이 되는 8 파일(DeployPL · DeployWorker · DeployReviewWorker · IntegrationTest · StatefulTest · ServiceDeveloper · BackendDeveloper · FrontendDeveloper) → guard 참조/carve-out 서술로 정정.
4. **body tier 잔재 정정 (ADR-119 accuracy)** — ChangeImpactAgent.md L3-6(opus-비준 comment block) · ServiceDeveloperAgent.md L6("opus" desc, L65 는 이미 sonnet) · ModuleArchitect L36/L72 · APIContractArchitect L24 · StatefulTest L3 desc · DeployPL L161(coincidentally correct) 재정합. **★ ArchitectAnalystAgent.md L58 `CodebaseMapperAgent | Sonnet` = STALE(Mapper 는 Amendment 1 로 haiku) → haiku 동반 정정**(Amendment 1 miss, 본 Story 가 이 표 touch 하는 기회적 accuracy).
5. **SHARED SSOT prose tier-agnostic 일반화** — `CLAUDE.md` L79/L98-99 · `docs/architecture/codeforge-family.md` L36 · `docs/evidence-checks-registry.yaml` **L63 · L86 · L3292 · L3313 · L3314**(2개 dead entry 전부 — rate-limit-fallback-rate + stakes-tier-flip-evidence) → "non-opus(haiku 7 + sonnet 14)". **evidence-registry 의 "sonnet fallback 대상 0"·"tier-flip 대상 0" 은 보존**(A2-6 fallback 구분).
6. **lane CLAUDE.md tier 표 + architecture mirror(ADR-078)** — design(L44/45/62/63) · deploy(L21/22 + SSOT ptr L24/79) · deploy-review(L22 DeployReviewWorker 만; **DeployReviewPL L25/L79 은 opus 유지**) · test(L3) CLAUDE.md + `docs/architecture/codeforge-{deploy,deploy-review,test}.md` mirror. `codeforge-design.md`(L32/33/40/41)는 이미 "Sonnet"(CFP-2560 sweep 미청산 pre-existing drift) → 본 Story 후 coincidentally correct, drift 이력 명시.
7. **consumer-guide sonnet pin (L59)** — `ANTHROPIC_DEFAULT_SONNET_MODEL` 3rd-party pin 안내 추가. pin 값·`[1m]` 여부 = 요구사항리뷰 확정치(sonnet 은 1M-capable → opus-유비 가능, haiku `[1m]` 금지 비대칭과 다름).
8. **bump/sync** — plugin bump 8(design/requirements/deploy/deploy-review/pmo/test/develop + wrapper) + 각 CHANGELOG + marketplace mirrored-field sync(wrapper, ADR-063 atomic — sync PR 선행). **baseline 은 merge 직전 origin/main 재실측(wrapper 이미 6.103.1 로 drift 중 — collision).**

### A2-6. §결정 6 overlay-floor 3-clause + rate-limit fallback 구분

- **§결정 6 하한 재해석 (2-clause → 3-clause)**: Amendment 1 A1-6 의 2-clause(haiku 7 하한=haiku / 그 외=opus)를 **3-clause** 로 확장한다 — **haiku 7 하한=haiku / sonnet 14 하한=sonnet / 그 외 = opus 미만 down-tier 불허**. consumer overlay 는 각 에이전트 ADR-정의 tier 미만으로의 down-tier 를 불허(보수 상향만 허용, ADR-127 §결정 6 확장-only 정합). 소비자 intent 무변경.
- **rate-limit fallback machinery 구분 (K-5 — false 정정 리스크 차단)**: sonnet tier 가 carve-out 으로 부활해도 ADR-057 §결정 2(sonnet rate-limit → opus fallback) machinery 는 여전히 dead 이다(단일 tier 폐기 상속, fallback tier 부재). 따라서 `evidence-checks-registry.yaml` 의 "sonnet fallback 대상 0"(rate-limit-fallback-rate) 및 "tier-flip 대상 0"(stakes-tier-flip-evidence) dead-mark 은 **보존**한다 — prose 정정 = "carve-out 열거 확장(+ sonnet 14)" 이지 "fallback/tier-flip 대상 부활" 이 아니다.
- **sonnet 429**: sonnet 은 opus 와 별도 pool·별도 429 거동 → ADR-109(opus-scoped 429 mitigation) 미적용, fallback tier 부재. Amendment 1 A1-6 haiku 429 note 와 동형 — 리스크 낮음(경고), 운영 관찰 대상.

## Amendment 3 (CFP-2782, 2026-07-22) — deploy agent 4종 물리 제거 note

### 대상 + 판정

CFP-2782 / [ADR-121](ADR-121-deprecate-deploy-lanes.md) Wave 2 로 deploy·deploy-review 2 lane plugin dir 이 삭제되며 **DeployPLAgent · DeployWorkerAgent · DeployReviewPLAgent · DeployReviewWorkerAgent** 4종이 물리 제거됐다. 본 ADR(Accepted, NOT Superseded)이 Amendment 1/2 carve-out 표 + §결정 prose 에서 이 deploy agent 를 live-ref 로 보유했으므로, 그 referent 가 소멸했음을 note 로 기록한다.

### frozen 이력 (Event Sourcing)

- **Amendment 2 tier 표** (sonnet carve-out: DeployPL · DeployWorker · DeployReviewWorker) = **dated Amendment 이력**, byte 무변경 frozen — 그 시점 tier 결정 이력 보존.
- **A2-4 DeployPL asymmetry** 단락 + **A2-5 Phase-2 실행 범위**(deploy CLAUDE.md tier 표 인용, L405-408) = 이미 CFP-2735/2748 Phase 2 이행분 + 삭제 대상 파일 참조라 정합. byte 무변경.

### all-opus 정책 무영향

**§결정 1 (전 에이전트 opus 단일 tier) = 무영향** — deploy agent 4종 물리 제거는 agent 수 감소일 뿐, 잔존 전 에이전트의 tier(opus 단일)는 동일. ProductionEvidenceDeputy = §결정 6 opus 명시 유지, CFP-2782 로 codeforge-design CONDITIONAL deputy RELOCATE 회귀(ADR-072 Amendment 5).

### sunset_justification

N/A — is_transitional: false permanent policy 유지. tier 정책 약화가 아니라 상위 ADR-121 로 물리 제거된 4 deploy agent 의 참조 note (dead-agent reference cleanup). all-opus §결정 1 무영향, Amendment 1/2 carve-out 표 frozen 보존. governance surface 축소 0.

### Cross-ref

- [ADR-121](ADR-121-deprecate-deploy-lanes.md) — deploy·deploy-review lane deprecate (deploy agent 제거 authority)
- ADR-141 Amendment 1/2 (carve-out 표 — deploy agent live-ref 보유처, frozen 역사)
- [ADR-042 Amendment 20](ADR-042-agent-model-selection-policy.md) — 4-agent deploy roster deprecated (sibling)
- [ADR-072 Amendment 5](ADR-072-production-evidence-deputy-and-epic-cutover-gate.md) — ProductionEvidenceDeputy RELOCATE 회귀

## Amendment 4 (CFP-2803 — 고레버리지 apex 역할 10종 opus/sonnet→fable carve-out + self-refusal guard fable 확장)

**날짜**: 2026-07-23 KST · **carrier**: CFP-2803 · **방향**: 단일-tier uniformity 부분 축소(carve-out) + 비용 **상향**(표적-강화, 절감 아님). Amendment 1(haiku 7 하향)/Amendment 2(sonnet 14→live 11→본 건 후 10 하향)와 **방향이 반대** — codeforge 재발 실패모드를 표적 타격하는 고레버리지 apex 강화. 본 Amendment 가 §결정 1(전 에이전트 opus)·§결정 2(fable 완전 폐기)·§결정 6(overlay 하한)의 **override SSOT** 이다 (§결정 1·2·6 원문 = frozen audit trail, 무손상). 누적 carve-out = **haiku 7 + sonnet 10 + fable 10 + opus 14 = 41**.

### A4-1. 10종 carve-out (§결정 1 이탈 = amendment 의무 이행)

§결정 1 "단일 tier 이탈은 본 ADR amendment 를 의무" 에 따라, 아래 10 에이전트를 `model: fable`(Claude Fable 5) 로 carve-out 한다. 근거 = §1 사용자 directive("더 똑똑해서가 아니라 이 프로젝트의 재발 결함을 특정해 잡는다") — Fable 의 (a) 장수명 sub/peer 조율 강점 + (b) progress claim ↔ tool-result 대조 강제 anti-fabrication 특성이 codeforge 3대 재발 실패모드(verify-before-trust 위반 / fabricated-status / born-broken over-PASS)를 표적 타격. 배정 원칙 = **"정점(apex)에만"** (조율·판정 apex + 소수 고레버리지 task; finder/leaf/doer/deputy/preset 미배정 — 2배+ 비용을 저volume·고가치 지점에만 결속).

| 에이전트 | host plugin | AS-IS tier (firsthand grep) | Amendment 4 tier | Tier | 역할 근거 |
|---|---|---|---|---|---|
| RequirementsPLAgent | codeforge-requirements | opus | **fable** | A | 요구 lane PL synthesis/arbiter |
| RequirementsReviewPLAgent | codeforge-review | opus | **fable** | A | 요구리뷰 lane PL arbiter |
| ArchitectPLAgent | codeforge-design | opus | **fable** | A | 설계 lane PL + FIX 최종 원인 판정 arbiter |
| DesignReviewPLAgent | codeforge-review | opus | **fable** | A | 설계리뷰 lane PL arbiter |
| DeveloperPLAgent | codeforge-develop | opus | **fable** | A | 구현 lane PL + FIX 1차 진단 arbiter |
| CodeReviewPLAgent | codeforge-review | opus | **fable** | A | 구현리뷰 lane PL arbiter |
| PMOAgent | codeforge-pmo | opus | **fable** | A | 프로젝트관리 arbiter (8-lane 밖이나 §5.5-Q1 사용자 확정 편입 — retro/gate 감사·ESCALATE→ADR 발의) |
| ArchitectAgent | codeforge-design | opus | **fable** | B | 설계 chief-author (6 deputy 산출물 통합 synthesis) |
| ResearcherAgent | codeforge-requirements | opus | **fable** | B | 요구 개념 정립 (long-horizon exploration) |
| IntegrationTestAgent | codeforge-test | **sonnet** | **fable** | B | Epic 통합테스트 lane 리드 (long-running deployability soak) |

- **명시 제외 (opus 유지)** — **SecurityTestPLAgent**: lane PL 이나 보안 lane 소속. Fable cyber 안전분류기가 취약점(cyber) reasoning/synthesis 를 refusal → §1 하드-NO("이 lane 실 가치 무력화 = 순손실")가 PL 층위에도 적용. 근거 = Anthropic 명시 "bug-finding gains **exclude security-focused analysis, where the cyber classifiers apply**"(§6.4). §1 원문이 SecurityTestPL 을 "각 lane PL" 에서 명시 carve 하지 않았으므로 accidental sweep 방지 위해 opus 고정.
- **하드-NO 제외군 tier 무변경** — leaf haiku 7(CodebaseMapper · CodexReview · TestAgent · QADeveloper · DataEngineer · InfraEngineer · RequirementsAnalyst) + 고fan-out adversarial verify finder(ClaudeReview[opus] · CodexReview[haiku] · codex-proactive-check[opus]) + production doer(DeveloperAgent[opus]) + deputy/preset(sonnet/opus 유지). "다수 저가 독립 투표" verify 경제학 보존 — Fable 은 verify **arbiter 정점**(review PL)에만.
- **role-based ≠ stakes-based** — 본 carve-out 은 role(조율·판정 apex + 고레버리지 task) 기준의 **고정 열거**이며, §결정 3 으로 dead 된 stakes-gated tier-flip(ADR-042 Amd15/16/17)을 부활시키지 않는다.

### A4-2. §결정 2 부분 역전 + "3-tier 자동선택 부활 아님" (정직 프레이밍)

- **§결정 2("fable 완전 폐기 — dormant 아님") 부분 역전** — ADR-141 은 fable↔opus 2일 4진동 부채를 청산하려 fable 을 완전 폐기(dormant 보존조차 거부)했다. 본 Amendment 는 fable 을 **재도입**하므로 §결정 2 를 정면 역전한다("사소한 추가"로 위장 금지 — ADR-119). 정당성 = ADR-141 자신의 **§해소 기준(재산정 트리거) 2개 동시 발동**: ① "사용자 directive 로 tier 다양화 재요구"(§1 fable 배정 directive 정확 매칭) ② "모델 세대 전환(차기 최강 모델 GA)"(Fable 5 = 2026-06-09 GA, 현 "most capable widely released model" — ADR-141 폐기 당시 2026-07-03 fable 과 세대·포지션 갱신). 재도입 = 고정 named-role carve-out 이라 dormant toggle(진동 재생산) 구조 미형성.
- **"3-tier 자동선택 부활 아님" (핵심 구별)** — ADR-141 §결정 3 이 폐기한 것 = **선택 함수**(stakes-gated lookup + role-pattern 매칭 + re-audit machinery), 폐기 이유 = 선택 기준의 모호성·운영 복잡도. 본 Amendment 가 하는 것 = **10 named agent 를 고정 열거(enumeration)** + 각각 failure-mode-표적 근거 명시. **enumeration ≠ 선택 함수** — re-audit machinery·stakes-gating 재도입 0, 모호성 0. ADR-042 §결정 1 3-tier · Amd15/16/17 stakes-flip = **dead 유지**.
- **ADR-117(fable surgical, Superseded) 부활 아님** — ADR-117 = fable surgical 11종 + stakes/role-pattern 선택 + CC v2.1.170 floor. 본 Amendment 와 **다른 근거·다른 선택 기준**(ADR-117 = "깊은 mandate 역할", 본 건 = "재발 실패모드 표적") + 다른 대상 집합(11 ≠ 10). ADR-117 부활로 프레이밍하면 부정확(ADR-119). 단 **CC floor 개념은 재사용** — fable 인식 최소 CC 버전을 consumer-guide 에 재확립(Phase 2, floor 버전 정확치는 미bisect = 확인 불가로 표기).

### A4-3. self-refusal guard fable 확장 (#846 계보 — hard co-requirement)

Amendment 1 A1-3 이 확립한 근본 사실(spawned subagent 는 project `CLAUDE.md` 를 "project instructions" 로 주입받음 = #846 실증)은 재도출 대상 아님. fable subagent 도 "opus default"·"opus 단일 tier" 규범을 self-check 해 자기거부할 표면이 있으므로 guard 를 fable 10종에 확장한다(Phase 2, hard co-requirement — 10 frontmatter 변경과 분리 merge 금지).

- **트리거 표면 차이 (정직)** — `CLAUDE.md` L79 는 "**Sonnet/Haiku** 세션이면 중단" 으로 sonnet/haiku 만 명시 지칭하므로 fable 은 문자 매칭 안 됨. 그러나 "**전 에이전트 opus 단일 tier**"·"opus default" 규범은 여전히 fable subagent 의 self-check 유발 가능 → guard 필요(문자 매칭 부재 ≠ 위험 부재).
- **mechanism 재사용 (신규 0)** — Amendment 1 A1-3 2-layer(CLAUDE.md at-source defuse + per-agent `.md` body) 재사용. canonical guard 문구(Phase 2 가 10 agent `.md` body 에 배치, Amd1/2 verbatim + fable substitution):

  > **model tier (ADR-141 Amendment 4)**: 이 에이전트는 ADR-141 Amendment 4(CFP-2803)로 non-opus(`fable`) tier 로 **의도 배정**된다. wrapper `CLAUDE.md` 의 '전 에이전트 opus 단일 tier'·'opus default'·'Sonnet/Haiku 세션이면 중단' 규범은 Orchestrator 세션/거버넌스 scope 이며, 이 에이전트가 자기 `model:` tier 를 self-check·self-refuse 대상으로 해석하는 것을 금지한다(#846 재무장 차단).

### A4-4. framing 정정 + refusal 방어설계 (ADR-119)

- **"품질영향 ≈0" 금지 → 표적-강화 tradeoff** — 본 건은 **cost-up**(2배+ 실효 비용)이나 "약화(거버넌스 축소)" 가 아니라 "재발 실패모드 표적 강화" 다. anti-fabrication 은 **모델 내재 속성이 아니라 프롬프트 지시("audit progress against actual tool results")로 달성되는 강화된 default** 이며 Anthropic 표현도 "**nearly** eliminated"(완전 제거 아님, source: Anthropic prompting 가이드 §6.1b). 따라서 "fabricated-status 기계적 근절" 로 over-claim 하지 않고 codeforge verify-before-trust / research-before-claims(ADR-119)와 **같은 결의 강화** 로만 프레이밍. Anthropic 은 "fresh-context verifier subagents tend to outperform self-critique" 를 권고 → fable 을 arbiter 정점에 두고 finder 는 저가 독립 투표로 유지하는 설계와 정합.
- **refusal 방어설계 (harness fallback 미확정 → 수동 opus 재spawn)** — fable refusal 표면 2종: (i) cyber(보안 lane 배제로 주 표면 제거) + (ii) `reasoning_extraction`(harness 패턴, lane-무관). server-side `fallbacks:[{model:"claude-opus-4-8"}]` param 은 **직접 Messages API opt-in** 이며 Claude Code harness(Agent SDK)의 frontmatter-spawn 이 이를 노출하는지 **공개 문서로 "지원됨" 확정 불가**(요구사항리뷰 lane firsthand cross-check = Agent SDK 범위 밖, per-frontmatter-subagent refusal fallback 문서 근거 없음 — §9). 따라서 **자동 fallback 없음 가정** 하에 방어 경로 확정: **fable agent/PL 이 refusal(`stop_reason:"refusal"`, category ∈ cyber/bio/reasoning_extraction/frontier_llm) 히트 시 Orchestrator 가 해당 task 를 opus 로 재spawn**(수동 fallback). 이는 ADR-119 runtime-failure 처리(runtime 실패 = 표면 증상 아닌 lane 재진입/재spawn)와 정합 — refusal 은 게이트 FIX loop 아닌 재spawn 대상. 발동률 낮음(Anthropic "95% 이상 세션 fallback 없음", <5%, §6.3).
- **`reasoning_extraction` 감사기준 (정당 근거인용 과대차단 방지)** — Phase 2 프롬프트 감사기준: **"외부 evidence 인용(file:line / tool-result / 출처 URL) = 정당한 응답-텍스트 산출물 ≠ 내부 추론(thinking) 재현"**. `reasoning_extraction` 위험 = "echo/transcribe/explain its **internal reasoning** as response text" 지시(§6.3). codeforge 렌더 프리픽스(액션 요약)·상태보고·근거 인용(verify-before-trust 의 file:line 증거)은 **내부 추론 재현이 아니므로 안전** — 감사는 실제 "내부 thinking 을 텍스트로 재현하라" 는 지시만 표적(정당 근거인용 과대차단 금지 + 실제 reasoning-echo 지시 과소차단 금지, 양방향 정밀).

### A4-5. Phase 2 실행 범위 (구현 PR — 본 Phase 1 ADR PR 밖, 열거만)

Change Plan(CFP-2803) 이 SSOT. 실 실행 = 별도 Phase 2 PR:

1. **10 frontmatter** `model:` → `fable` (9× opus→fable + IntegrationTest sonnet→fable). SecurityTestPL = opus 무변경(회귀 금지).
2. **guard 배치** — 10 agent `.md` body 각각에 A4-3 canonical 문구(fable-facing) 추가.
3. **CLAUDE.md** — (a) L79 Orchestrator mandate: "Sonnet/Haiku 세션이면 중단" 을 **fable 은 valid Orchestrator 세션 모델**로 갱신(fable 세션 self-halt 방지, halt 대상 = Sonnet/Haiku 만) + Orchestrator 모델 mandate `opus` → **fable**(문서 codify; 실 세션 모델 = 사용자 launch handoff, 비-PR-enforceable) (b) `## opus default + ADR-141 carve-out` 절 = fable carve-out(10 named role) 추가, 3-clause → **4-clause**(haiku 7 / sonnet 10 / **fable 10** / opus). fable Orchestrator = 정상 명시(self-refuse 대상 아님).
4. **SHARED SSOT prose + lane-plugin CLAUDE.md tier 주석 일반화** — `docs/architecture/codeforge-family.md` tier 서술 + 각 lane architecture mirror(ADR-078) → 누적 "haiku 7 + sonnet 10 + fable 10 (opus 14)". **lane-plugin CLAUDE.md tier 주석 2 stale site(firsthand grep-sweep, zero-drop)**: `plugins/codeforge-design/CLAUDE.md:60`(ArchitectAgent "Opus" → fable) + `plugins/codeforge-test/CLAUDE.md:3`(IntegrationTestAgent "sonnet — Amendment 2" → fable — Amendment 4). 나머지 8 fable 대상(6 lane PL + Researcher + PMO)은 lane CLAUDE.md model-tier 주석 미보유 = **추가 stale site 0 확정**(design/CLAUDE.md L40-45·62·63 비-fable deputy 는 무변경). Change Plan §3.1 SSOT.
5. **consumer-guide** — fable pin(3rd-party: Bedrock `anthropic.claude-fable-5` / Vertex `claude-fable-5`) + CC floor(fable 인식 최소 버전) + **30일 데이터 보존 요건**(ZDR/30일 미만 org = 전 요청 400) 명시.
6. **overlay-floor 4-clause (§결정 6)** — haiku 7 하한=haiku / sonnet 10 하한=sonnet / **fable 10 하한=fable(down-tier 불허)** / 그 외 opus 미만 불허. fable clause 도 확장-only(ADR-127 §결정 6 정합, §5.5-Q2 사용자 확정) — 소비자는 fable 을 상속하며 opus 로의 down-tier(비용 escape) **불허**. **2배+ 비용 소비자 파급은 완화 없이 정직 문서화**(비용 escape 경로 의도적 부재).
7. **§8 roster-integrity 게이트 신설** — enumeration = **globstar-robust `find plugins -path "*/agents/*.md"`(= 41 ground-truth firsthand; default bash `plugins/**/agents/*.md` globstar-OFF = 38 → preset-depth 3종[ServiceDeveloper·Backend/FrontendDeveloper] drop 회피 — census/drift 축 false-RED[born-broken]/hollow 함정)**. count=10 fable(glob-safe, non-preset) + 정확 파일 bijection + **SecurityTestPL NOT fable** + **census/drift 총계 == 41(`find` 필수)** 검증. RED→GREEN discriminating(한 파일 flip → FAIL) + **self-test 에 "실 repo enumeration == 41" liveness 축**(preset-drop discriminating kill — inline-fixture 논리만 태우는 self-test 로는 미surface) + self-test enroll(selftest-execution-liveness bijection) + hard-gate cross-seal(born-broken 회피 — CFP-2635/881/2762 계보). **기존 agent-model-tier roster lint 부재 firsthand 확인**(check-stakes-tier-gating[dead]/check-tier-downgrade-guard[registry]/check-tier-honesty[stop-lever] 3종 모두 frontmatter roster 미검증) → 신규 gate.
8. **bump/sync** — plugin bump 6(requirements/review/design/develop/test/pmo + wrapper guard·ADR host) + marketplace mirrored-field sync(ADR-063 atomic — sync PR 선행) + CHANGELOG. baseline = merge 직전 origin/main 재실측.

### A4-6. 영향 경계 / count reconcile / rate-limit fallback 구분

- **count reconcile (I-1 정정)** — AS-IS firsthand grep(`grep -rn "^model:" plugins/**/agents/*.md`) = haiku 7 / sonnet **11** / opus 23 = 41. Amendment 2 의 "sonnet 14" 는 CFP-2782/ADR-121(Amendment 3) deploy 3종 물리 제거로 live 11 로 감소(Amendment 2 dated 표 = frozen 무변경). 본 Amendment 후 = haiku 7 / **sonnet 10**(IntegrationTest 이전) / **fable 10** / **opus 14**(23 − 9) = 41. Amendment 2/3 dated 이력 표는 byte-frozen, **live 총계만 본 Amendment 가 reconcile**.
- **rate-limit fallback 구분 (K-note)** — fable refusal-fallback(server-side *refusal* fallback)은 rate-limit fallback 과 **별 mechanism**. ADR-057 §결정 2(rate-limit → opus fallback) machinery 는 dead 유지, `evidence-checks-registry.yaml` "fallback 대상 0"·"tier-flip 대상 0" dead-mark **무접촉 보존**. prose 정정 = "carve-out 열거 확장(+fable 10)" 이지 "rate-limit/tier-flip 대상 부활" 아님.
- **fable 429** — fable 은 opus 와 별 pool·별 429 거동 → ADR-109(opus-scoped 429 mitigation) 미적용, fallback tier 부재(단일 tier 폐기 상속). Amendment 1/2 haiku/sonnet 429 note 동형 — 리스크 낮음(경고), 운영 관찰 대상.
- **blast radius** — 10 agent frontmatter + 10 agent `.md` guard + CLAUDE.md(L79 mandate·guard 절 4-clause) + architecture doc mirror + consumer-guide(fable pin/floor/retention) + §8 roster-integrity gate 신설 + 6 plugin bump + marketplace sync.

### Cross-ref

- [ADR-117](ADR-117-fable-5-surgical-model-tier.md) — fable 최초 도입(Superseded); 본 Amendment 는 **부활 아님**(다른 근거·다른 대상)
- ADR-141 §결정 2(fable 완전 폐기 — 본 Amendment 가 부분 역전) / §결정 3(3-tier 선택 함수 폐지 — **부활 안 함**) / §결정 6(overlay 하한 — 4-clause 확장)
- [ADR-119](ADR-119-research-before-claims.md) — anti-fabrication over-claim 회피 + runtime-failure(refusal) 재spawn 정합
- [ADR-127](ADR-127-mandatory-full-flow-no-exemption.md) §결정 6 — overlay 확장-only(fable clause down-tier 불허 정합)
- [ADR-142](ADR-142-orchestrator-self-read-synthesis-context-discipline.md) §결정 1 L1 — Orchestrator raw-read offload = fable 2배 비용 주 완화축

## Amendment 5 (CFP-2811, 2026-07-24) — ADR-117 보존지시 한정 override (obsolete 외부 제약 서사 삭제 승인)

**날짜**: 2026-07-24 KST · **carrier**: CFP-2811 · **방향**: tier 정책 무접촉 — 문서 이력-보존지시의 적용 범위 한정 축소(governed 예외 1건). 본 Amendment 가 §상태·§결정 2 의 ADR-117 보존지시에 대한 **override SSOT** 이다 (원문 = frozen audit trail, 무손상).

### A5-1. 대상 + override 범위

ADR-117 의 obsolete 외부 제약 서사 — 구 `## Amendment 1`(CFP-2241 임시 override) + 구 `## Amendment 2`(CFP-2554 원복) — 가 CFP-2803(본 ADR Amendment 4, fable 정식 재도입 6.120.0 live)으로 3중 무효화되어 CFP-2811 이 삭제한다 (집행 = ADR-117 Amendment 4). 본 ADR 의 다음 2개 보존지시를 **그 서사에 한정해 override** 한다:

- **§상태** — "ADR-117 (Fable 5 surgical tier) → Superseded (본체 텍스트 이력 보존, 삭제 아님)" (구 L170).
- **§결정 2** — "단 ADR-117 본체 텍스트는 이력 보존한다 (Superseded 마킹 + Amendment 3 append)" (구 L228). [anchor = §결정 2 — §결정 1 아님 (CFP-2811 요구사항리뷰 F1 정정).]

**한정성**: ADR-117 의 결정 1~5 + `## Amendment 3`(supersede 기록)는 계속 보존지시 하에 있다(frozen). §결정 2 의 실 substance(fable 완전 폐기 — 그 자체는 Amendment 4 가 이미 부분 역전) 및 Event Sourcing frozen-default 원칙은 무변경 — 본 override 는 obsolete 사실서사 1건에만 미친다.

### A5-2. 보존 (audit trail 무손실 — 의미 손실 0)

- **본 ADR §컨텍스트 "fable↔opus 진동 부채" ledger** — CFP-2241(외부 제약 override 부과) + CFP-2554(원복) rows = **byte 무변경 보존** (결정-사실 최소 audit 위치, CFP-2811 PRESERVE set).
- **`plugins/{codeforge-design,codeforge-develop,codeforge-requirements,codeforge-review}/CHANGELOG.md`** — ADR-117 구 Amendment 2 원복 기록 = append-only audit, 무접촉.
- **git history** — 삭제 서사 전문 복구 채널.

### A5-3. 거버넌스 근거

- **ADR-058 §결정 11**(CFP-2811 신설) — obsolete 사실서사 제거 이중 게이트(① 보존결정 명시 amendment override ② 사용자 명시 비준) + 결정-사실 복구가능성 의무 충족. 사용자 비준 = CFP-2811 Story §9 Option B sign-off (2026-07-24).
- silent 삭제 아님 — 삭제 범위는 ADR-117 Amendment 4 가 열거하고, 본 Amendment 가 보존지시 override 를 명시 기록한다.

### Cross-ref

- [ADR-117 Amendment 4](ADR-117-fable-5-surgical-model-tier.md) — 삭제 집행 + Amendment 3 §결정 3 override (paired)
- [ADR-058 §결정 11](ADR-058-adr-sunset-criteria-mandate.md) — obsolete 사실서사 제거 이중 게이트 codify (첫 적용 = CFP-2811)
- [ADR-042](ADR-042-agent-model-selection-policy.md) — stale 인과절 4곳 동반 정정 (stale-mirror accuracy 축 — 보존결정 override 아님, amendment 불요 분류)

## Amendment 6 (CFP-2823 — fable-리밋 한정 runtime opus failover 신설)

**날짜**: 2026-07-24 KST · **carrier**: CFP-2823 · **방향**: tier 정책 약화 아님 — **운영 연속성 강화**(fable-리밋 시 작업 정지 공백 메움). 본 Amendment 가 §결정 2("fable 완전 폐기")의 dead-mark("rate-limit fallback machinery 부활 0" / A4-6 fable 429 "fallback tier 부재")에 대한 **fable-리밋 한정 부분 override SSOT** 이다 (그 dead row 는 frozen dated audit trail = byte 무변경, 신규 failover 규범 carrier = 본 Amendment 6). ADR-057 §결정 2/4 설계 shape 자산 4종 답습 — **ADR-057 부활 아님**(Superseded 유지, sonnet 축 moot 불변). 감지 SSOT = [ADR-109](ADR-109-in-process-429-mitigation-framework.md) §결정 1 Amendment 1(session/usage-limit class 편입).

### A6-1. 대상 + 트리거

- **대상 roster** = Amendment 4 A4-1 이 fable 로 carve-out 한 **10 named role**(6 lane PL: RequirementsPL · RequirementsReviewPL · ArchitectPL · DesignReviewPL · DeveloperPL · CodeReviewPL + ArchitectAgent + ResearcherAgent + PMOAgent + IntegrationTestAgent). **SecurityTestPL = 대상 아님**(A4-1 명시 제외 opus 유지) + 비-fable tier(haiku 7 / sonnet 10 / opus)도 대상 아님(A6-3).
- **트리거** = Orchestrator 가 fable 배정 subagent 를 spawn 한 결과가 **리밋 계열 신호**(ADR-109 §결정 1 Amendment 1 감지집합 any-match — base 4-tuple + `session limit` + `usage limit` = 6 literal)를 동반해 실패. 시점-무관(사용자 §1 verbatim "리밋에 걸리면") — 2 표면 포괄: (a) **spawn-시점 거부** ∪ (b) **mid-run 조기종료**(`Agent terminated early due to an API error: ...` task-notification. 본 Story 진행 중 fable PL 이 세션 리밋으로 mid-run 종료한 실관측 = 이 시나리오의 실전 실증 — Story §9).
- **감지 scope 불변식** = 리밋 문자열 매칭은 **error/termination notification 표면 한정**(task-notification 또는 spawn-거부 메시지). subagent substantive output 본문은 매칭 대상 아님 — 본 Story 텍스트 자체가 `rate limit`/`429` 를 수십 회 포함 = live false-positive hazard 이므로 scope 한정이 필수.

### A6-2. failover 절차 (Option A 즉시전환 + step1 bypass + 1-hop + fresh-spawn-only)

리밋 감지 시 Orchestrator(ADR-039 spawn monopoly — 실행 주체, lane PL 자가-재spawn 불가):

1. **fable same-model 재시도 SKIP** — Option A 즉시전환. ADR-109 §결정 3 step1(same-model exp-backoff soak)을 fable 브랜치에서 **bypass** 하고 step2(cross-model substitution)로 직행. 근거 3층: (a) session/usage-limit reset = long-horizon(실관측 `resets 10:20pm` ≈ 관측 대비 ~3.5h 미래 ≫ §결정 2 backoff budget ~1-6min)라 fable same-model 재시도 futile-by-construction (b) fable·opus 는 **별 pool**(A4-6 note)이라 리밋 해소 remedy = pool 전환(opus)이지 소진된 fable pool 대기 아님 (c) §결정 2 Retry-After-우선이 실관측 `resets 10:20pm` reset hint 를 존중하면 fable 에서 ~3h 대기 = AC-1 "fable full-soak 대기 금지" 정면 위반 → Option A 만 회피.
2. **fresh re-spawn 1회** — 새 `Agent` spawn + `model: opus` override(동일 입력 패킷). **SendMessage resume 금지**(원본 frontmatter `model: fable` 가 resume 시 재해석 재실패 = CFP-2236 실측 root cause). **max 1회 per-spawn-attempt 독립 카운터**(비합산, 재진입/FIX 루프 재spawn 시 시도마다 리셋 — Story 누적 아님; "1회/시도" 가 무한 failover 차단).
3. **§14 태그 기록** — `[rate-limit-failover:fable→opus]`(A6-4).

**dead slot re-tenant (부활 아님 프레이밍)**: §결정 3 step2 slot 은 구 ADR-057 §결정 2(sonnet rate-limit→opus)를 cross-ref 했으나 그 축은 ADR-141 로 moot/dead 라 **구조적으로 비어 있다**. fable 브랜치가 그 dead slot 을 신규 trigger(fable 리밋)·신규 SSOT(본 Amendment 6)로 **re-tenant** 한다 — ADR-057 Superseded 유지, sonnet fallback machinery 부활 아님.

### A6-3. 비대상 3종 (AC-3)

- **(a) Orchestrator 세션 자체 리밋** — launch 시점 모델 고정이라 자동 전환 구조 불가. 기존 대기 / 수동 세션 handoff 유지(ADR-110 축 disjoint).
- **(b) refusal**(`stop_reason: refusal` — cyber/reasoning_extraction 등) — 별 축. 수동 opus 재spawn 방어(CFP-2803 / A4-4) 유지. 리밋 아님.
- **(c) 비-fable tier subagent 리밋**(haiku 7 / sonnet 10 / opus) — 기존 "운영 관찰 대상" note(A1-6/A2-6/A4-6) 무변경. 본 failover 는 fable-리밋 한정.

### A6-4. cascade / §14 격리 / idempotency

- **cascade_depth = fable→opus hop COUNT-IN(depth 1)** — opus 착지 후 opus 자기 within-model soak 은 미증가. opus soak 소진 후에도 리밋 = cascade ≥ 2 → **user manual resume only**(ADR-109 §결정 5). disjoint 카운터 금지(bound 약화 — count-in 이 "1-hop then manual" semantics 강제, AC-2 정합). opus 착지 **후** 비로소 §결정 2 exp-backoff / §결정 3 step1·3·4 가 opus 를 same-model 로 재정박.
- **§14 전용 태그 격리** — `[rate-limit-failover:fable→opus]`. 기존 dead 태그(`[rate-limit-fallback:sonnet→opus]` / `[model-unavailable-fallback:fable→opus]`)와 **비합산·별 이름·별 measurement**("failover" token 이 "fallback" 과 분별). **§10 FIX Ledger row 금지**(ADR-109 §결정 9 / ADR-057 §결정 4 격리 동형 — failover = 운영 telemetry ≠ FIX). matched detection literal 기록 권고(auditability — false-positive[특히 `usage limit` negated-context] post-hoc audit). secret 금지(ADR-109 §결정 10 redaction matrix 상속 — account_id/org_id 임베드 금지; reset time KST 는 비밀 아님).
- **idempotency(mid-run 재수행, E11)** — base_sha reconcile(입력 패킷 = idempotency contract) + owned-section replace-whole(fragment append 아님, last-writer-wins) + append-only 섹션 idempotency-key dedup. 구조적 안전판 = §10 Ledger append 는 Orchestrator 독점(§결정 9 + ADR-039)이라 mid-run fable 종료가 half-appended row 를 남길 수 없음. external non-idempotent side-effect = safe-replay 밖 → silent re-spawn 금지, task-failure escalation.

### A6-5. Phase 2 실행 범위 (구현 PR — 본 Phase 1 ADR PR 밖, 열거만)

Change Plan 면제(ADR-carrier 선례 정합 — ADR-141 A1-5/A2-5/A4-5 동형, 본 Amendment + ADR-109 §결정 1 Amendment 1 이 설계 SSOT; ADR-013 은 산출물 위치 정책으로 면제를 금지하지 않음). 실 배선 = 별도 Phase 2 PR:

1. **CLAUDE.md `## opus default + ADR-141 carve-out` 절** — fable-리밋 예외 1문 추가("fable subagent 리밋 감지 시 opus fresh re-spawn 1회 — ADR-141 Amendment 6"). rate-limit *fallback* machinery(sonnet 축) 부활 아님 명시.
2. **playbook §3.0.12 부근** — failover 절차 명문화(Option A 즉시전환 / step1 bypass / 1-hop / fresh-spawn-only / 비대상 3종 / cascade count-in).
3. **skill `codeforge:rate-limit-429-mitigation`** — fable-branch 편입(fable 리밋 → opus fresh re-spawn → opus 리밋 → §결정 2 same-model 경로). ADR-109 §결정 1 Amendment 1 감지집합 cross-ref(중복 enum 정의 0).
4. **§14 태그 스키마** — `[rate-limit-failover:fable→opus]` 신규 태그 등록(§10 금지 명문 + 기존 dead 태그 비합산).
5. **bump/sync** — CLAUDE.md/skill/playbook 변경 시 wrapper bump + CHANGELOG(marketplace sync 는 plugin.json mirrored field 변경 시만 — ADR-063, 본 건 mirrored field 무변경).

### A6-6. 영향 경계 + dead-mark 보존

- **blast radius** = CLAUDE.md(opus default 절 1문) + playbook §3.0.12 + skill rate-limit-429-mitigation + §14 태그 스키마 + ADR-109 §결정 1 Amendment 1(감지집합 확장, cross-carrier) + wrapper bump. **agent frontmatter 무변경**(AC-7 — failover = runtime spawn-시점 override 한정, 정적 down-tier 아님, roster-integrity fable=10 GREEN 유지). **A4-3 guard 무손상**(AC-9 — failover-spawn opus 인스턴스가 자기 `.md` "fable 의도 배정" guard 를 self-refuse 하지 않도록 guard 의 tier self-check 금지 규범 유지; #846 계보).
- **dead-mark 보존 (byte 무접촉)** — A4-6 note("fable 은 opus 와 별 pool·별 429 거동 → ADR-109 미적용, fallback tier 부재") + A2-6/A4-6 "rate-limit fallback machinery 부활 0" + `evidence-checks-registry.yaml` "fallback 대상 0"·"tier-flip 대상 0" dead-mark = **frozen dated audit trail, 무변경 보존**. 본 Amendment 6 은 그 "fallback tier 부재" 를 **fable-리밋 한정 부분 override**(신규 failover 경로)하되 rate-limit *fallback machinery*(sonnet 축)는 dead 유지 — 별 mechanism·별 trigger(fable 리밋)·별 태그. "fallback"(sonnet 축, dead) ≠ "failover"(fable-리밋, 본 Amendment) 분별.
- **fail-open 안전 방향** — 감지 미탐(포맷 변경/미노출) → failover 미발동 → 현행 동작(대기/수동) degrade(회귀 0, born-broken 아님). 오탐 = 더 높은 리스크(opus 낭비 + 실결함 은폐) → bounding: closed-set literal-substring + per-spawn 1회 + fable-first 복귀.

### Cross-ref

- [ADR-109](ADR-109-in-process-429-mitigation-framework.md) §결정 1 Amendment 1 — session/usage-limit class 감지집합 편입(감지 SSOT) + §결정 3 step2 re-tenant + cascade count-in 합성 배치 codify
- ADR-141 Amendment 4 — A4-1(fable 10 roster = failover 대상 집합) / A4-3(guard — AC-9 무손상) / A4-6 note(fable 429 dead-mark — byte 보존 + fable-리밋 한정 override)
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) §결정 2/4 — 설계 shape 자산 4종 답습처(Superseded 유지, 부활 아님)
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — spawn monopoly(failover 실행 주체 = Orchestrator)
- ADR-013 — change-plan 면제 근거(ADR carrier = 설계 SSOT, 별도 change-plan 없이 amendment 내 Phase 2 열거)
