---
adr_number: 71
title: Orchestrator-user dialog convergence — frame mode + 4 layer 검증 + cross-Story 영속 incidents file
status: Accepted
category: governance
date: 2026-05-14
carrier_story: CFP-612
parent_epic: CFP-525  # ancestor
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    date: "2026-05-16"
    carrier_story: CFP-777
    issue: https://github.com/mclayer/plugin-codeforge/issues/777
    summary: DialogFidelityAgent external verifier auxiliary layer additive (Layer 1-4 보존, sunset_justification null 강화 ratchet)
    sunset_justification: null
  - amendment_id: 2
    date: "2026-05-17"
    carrier_story: CFP-818
    issue: https://github.com/mclayer/plugin-codeforge/issues/818
    summary: DialogFidelityAgent 3-anchor 운영 정의 + turn-shape edge × 3-anchor 12 cell 활성 표 신설 + ADR-039 inline whitelist 1번 entry 정합 명문화 + ADR-064 §결정 9 Q-3check disjoint scope cross-ref (additive, Layer 1-4 보존 + 5번째 cognitive layer 신설 금지 invariant 보존, sunset_justification null 강화 ratchet)
    sunset_justification: null
  - amendment_id: 3
    date: "2026-05-17"
    carrier_story: CFP-833
    issue: https://github.com/mclayer/plugin-codeforge/issues/833
    summary: DialogFidelityAgent effectiveness measurement wiring (Epic CFP-761 Story-3 closing-the-loop) — Layer 4 incident realtime detect incident append-rate delta (proxy signal — not causal effectiveness measure) metric + evidence-checks-registry.yaml dialog-fidelity-effect warning-tier entry (owner_adr ADR-071 / carrier_adr ADR-060, precedent rate-limit-fallback-rate 동형) + mechanical_enforcement_actions[] 갱신 (ADR-040 §결정 7.A governance 의무) + 본문 §결정 14 신설. additive — Layer 1-4 + DialogFidelityAgent auxiliary layer 보존, ## 해소 기준 무변경 (permanent governance recursive sunset 회피), ADR-058 §결정 3 측정성 self-application 강화 ratchet. Epic plan Task 4 invariant 5 (label-registry MINOR) deviation = precedent override (OQ-3 사용자 확정 2026-05-17 KST, ADR-064 §결정 10 precedence)
    sunset_justification: null
  - amendment_id: 4
    date: "2026-05-17"
    carrier_story: CFP-851
    issue: https://github.com/mclayer/plugin-codeforge/issues/851
    summary: Conversational reporting frequency suppression contract — Orchestrator ↔ user dialog 의 발화 허용 touchpoint 3종 closed enumeration codify (§결정 15 신설). (a) 결과-명세 확인 (사용자 선언 결과 자체 모호 + rollback 비싼 경우, verifiable outcome surface 안전판) / (b) 사용자만 풀 수 있는 차단 (인증·권한 등 codeforge 자체 해소 불가) / (c) 최종 완료 보고 1회 (요청 작업 단위 전체 완료). 그 외 진행·중간 결정·근거·중간 결과 = 산출물 (Story / change-plan / ADR / PR / TodoWrite panel) 전용 기록. 무약화 invariant — frequency 축소 ≠ richness 축소, §결정 2(c) "3 줄 제약 거부 · 길이 자유 · 배경 포함" 보존 + Layer 1/2 preamble·declare 의무 turn 발생 시 그대로 적용. ADR-039 inline whitelist 1번·4번 entry scope 안 작동 (closed 4-entry 보존, 신규 entry 신설 0). 4번째 touchpoint 확장 시 별도 CFP 의무 (§결정 13.6 closed-enum 확장 패턴 정합). mechanical lint = behavioral directive only, 별도 follow-up CFP (§결정 10 패턴 정합). additive — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 2(c) 무약화, is_transitional=false 보존, ADR-058 §결정 5 약화 차단 영역 미적용
    sunset_justification: null
  - amendment_id: 5
    date: "2026-05-20"
    carrier_story: CFP-1104
    issue: https://github.com/mclayer/plugin-codeforge/issues/1106
    summary: Natural-language action trigger lookup table codify (§결정 16 신설) — consumer 가 자연어 token "codeforge upgrade" (또는 한글 변형) 발화 시 orchestrator 가 dialog reflex (AskUserQuestion 모드/채널 재질의) 차단 + 7 차원 derived default (trigger phrase regex / repo cwd 자동 주입 / mode dry-run → apply 자동 / channel overlay resolve fallback stable / scope 단일 plugin default / dirty tree abort / 실패 시 자동 rollback) 결정론적 mapping closed enumeration 1 entry. ADR-076 invariant `user_decision_branches=0` 를 dialog 진입 단계로 확장 carrier — 본 ADR-071 §결정 5 사실/가치 분리의 dialog reflex 차단 first applied case. closed enumeration 보존 invariant — 본 lookup table 이 ADR-071 내 4번째 closed enumeration 인스턴스 (3-anchor enum §13.6 / 4 차원 enum §4 / 3 touchpoint enum §15.5 / **trigger table §16**) 신설, 2번째 trigger token 확장 시 별도 CFP 의무 (§결정 13.6 closed-enum 확장 패턴 정합 — ADR-064 §결정 7 top-down ratchet 강화 방향 + ADR-058 §결정 5 sunset_justification null 보존). ADR-039 inline whitelist 1번 entry scope 안 작동 (사용자 dialog 허용 영역, 5번째 entry 신설 0). doc-only fast-path Story (src/tests touch 0). additive — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 2(c) richness / 3 touchpoint enum (§15) 모두 보존, dialog reflex 차단 layer 추가만. is_transitional=false 보존, ADR-058 §결정 5 약화 차단 영역 미적용
    sunset_justification: null
  - amendment_id: 6
    date: "2026-05-20"
    carrier_story: CFP-1110
    issue: https://github.com/mclayer/plugin-codeforge/issues/1110
    summary: Lane back-translation gate binding — DialogFidelityAgent read-only verifier (Amendment 1/2/3 3-anchor) → lane return 직후 binding 강화 (§결정 17 신설). lane traversal fidelity loss 차단 — 각 lane PL deliverable return 직후 사용자 원문 언어로 산출물 reverse summary 의무 부착. DialogFidelityAgent 가 user-utterance anchor (paired ADR-082 Amendment 5 §결정 1 sub-scope (1-C) verbatim block) vs lane PL reverse summary 간 divergence 검출 시 lane 재실행 trigger (read-only verifier → binding mechanism 확장). 사용자 직권 minimal path 첫 적용 (codeforge process 가 lane traversal fidelity loss source 라는 평가 결과 정합 — Researcher 35% 정당화 / Codex ROI indeterminate-부정쪽 confidence medium 수렴, 2026-05-20 KST). pattern corpus 누적 evidence — synthesizer-stale-reference 6 (CFP-722/801/792/810/819/825) + Researcher 12 occurrence 정정 (CFP-698) + scope drift 만성 (CFP-758) + unverified-self-write-claim super-class 5 + DesignReviewPL cross-PL false-negative (CFP-906) — ADR-045 §D-9 pattern_count ≥ 6 ≫ threshold 2 escalation 정합. minimal path 정합 — Story file 0 / Lane spawn 0 / FIX iter 0 / Phase 분리 0 / Retro 0 / ADR-013 명시 위배 (사용자 승인 2026-05-20 KST) — closed-loop break 외부 결정 채널. Wave 1 = behavioral mandate (PL return 직후 reverse summary + Orchestrator divergence detection trigger) — Wave 2 mechanical lint + DialogFidelityAgent runtime hook 확장 = 별 CFP carrier (deferred-followup). additive — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 12-15 + §결정 16 (CFP-1104 Amendment 5) 모두 보존, is_transitional=false 유지, ADR-058 §결정 5 약화 차단 영역 미적용. paired sibling Amendment = ADR-082 Amendment 5 (lane PL spawn prompt user-utterance verbatim anchor, 동일 CFP-1110 carrier — disjoint axis 정합, 본 ADR = return-time output gate / ADR-082 = write-time input anchor). collision rebase 정합 — CFP-1104 Amendment 5 mid-flight merge 후 본 CFP-1110 amendment_id 5 → 6 정정 + §결정 16 → 17 rename.
    sunset_justification: null
  - amendment_id: 7
    date: "2026-05-24"
    carrier_story: CFP-1340
    issue: https://github.com/mclayer/plugin-codeforge/issues/1340
    summary: |
      Unjustified session swap reflex 차단 + /compact normative (§결정 18 신설). Orchestrator 가 사용자에게 "새 세션 만들어 주세요" / "세션 교체해 주세요" / "처음부터 다시 시작해 주세요" / "다음 작업은 새 세션에서" 발화는 closed 2-trigger 만 정당: (1) ADR-053 (구조 변경 재구동) / (2) ADR-057 (Sonnet/Haiku 세션). 그 외 trigger ("context 가득" / "메모리 차서" / "큰 Story" / "token budget" / "MEMORY.md 한도 초과" / "자기 보존" / "토큰 절약") = anti-pattern, 발화 차단. `/compact` slash command 활용 normative + MEMORY.md 한도 초과 = 인덱스 entry 슬림화 trigger (세션 분리 아님) + harness auto-compress 신뢰. 재발 incident 2건 verbatim citation:
      (a) 2026-05-21 KST Epic CFP-1059 Story transition 4회 ("S4 / S5/S6 / S7 진입 시점 매번 본 세션 context 극한 → 별 세션 권장" reflex)
      (b) 2026-05-23 KST 세션 시작 시 시스템 reminder "MEMORY.md is 53.2KB (limit: 24.4KB)" 발화 trigger
      memory `feedback_unjustified_session_swap_reflex` normative 승격 carrier. pattern_count 2 reach (ADR-045 §D-9 threshold). §결정 4 sub-mechanism 2 "차원 enum 4종 closed" 와 axis disjoint — §결정 18 = "결정 구조" 차원 sub-pattern routing (5번째 차원 신설 회피). Amendment 6 §결정 17 (lane back-translation gate) 와 disjoint axis (return-time output gate ↔ session lifecycle reflex). additive — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 12-17 모두 보존, is_transitional=false 유지, ADR-058 §결정 5 약화 차단 영역 미적용.
    sunset_justification: null
  - amendment_id: 8
    date: "2026-05-27"
    carrier_story: CFP-1764
    issue: https://github.com/mclayer/plugin-codeforge/issues/1764
    summary: |
      Agent burst output paste 합성 시 mid-turn glossary lookup 의무 (§결정 19 신설). Orchestrator 가 agent burst output (DomainAgent / ResearcherAgent / RequirementsAnalystAgent / PMOAgent 등 4+ 부속 작업자) 결과를 사용자 메시지로 합성 (paste-and-translate) 할 때 `docs/wording-dictionary.md` 카테고리 (c) codename → 평이 어휘 mapping table lookup 의무 — 1:1 치환 또는 평문 풀이 동반. lookup table SSOT location = wording-dictionary 카테고리 (c) (ADR 본문 / skill SKILL.md / domain-knowledge 별 SSOT 금지, single source of truth). closed enumeration cap = 15 codename 첫 batch + ratchet extensibility (신규 어휘 등장 시 별 후속 CFP). Scope = 사용자 dialog turn (Orchestrator 직접 발화) 영역만 — governance artifact (ADR / spec / change-plan / Story file) scope 외. §결정 2(a) frame mode step 4 (message 작성) 직전 step 3 cognitive 단계 "glossary lookup 필수 실행". 면제 channel = `hotfix-bypass:codename-glossary-lookup` label (audit-trailed exception, Story-2 carrier 75번째 hotfix-bypass family member). Consumer false positive handling = consumer overlay `jargon_filter_exempt_vocabulary: [...]` field 별 follow-up CFP carrier (본 Amendment 8 scope 외). Source incident = mctrader-hub#517 consumer brainstorm Phase 1 dialog 4-turn 누적 jargon leak (사용자 directive 4건 verbatim + consumer ad-hoc fix 거부 + wrapper canonical path 의무). Axis disjoint declare 3종 — §결정 17 (Amendment 6 lane back-translation gate) = return-time output gate per-lane vertical axis ↔ 본 §결정 19 = mid-turn paste-and-translate horizontal axis (lane-agnostic Orchestrator 합성) / §결정 14 (effectiveness measurement, CFP-833) = post-hoc metric layer ↔ 본 §결정 19 = mid-turn forcing function layer / ADR-064 §결정 9 (question quality 3-check) = dialog 진입 결정 분기 self-check ↔ 본 §결정 19 = dialog 진입 후 발화 작성 mid-turn 단계. mechanical_enforcement_actions[] frontmatter `codename-glossary-lookup` entry append (Story-2 declarative anchor, deferred-followup). additive — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 12-18 모두 보존, 5번째 cognitive layer 신설 금지 invariant 보존 (§결정 12.3 정합 — §결정 19 = mechanism 추가, cognitive layer count 변경 아님). is_transitional=false 유지, ADR-058 §결정 5 약화 차단 영역 미적용.
    sunset_justification: null
  - amendment_id: 9
    date: "2026-06-14"
    carrier_story: CFP-2236
    issue: https://github.com/mclayer/plugin-codeforge/issues/2236
    summary: |
      DialogFidelityAgent 전면 폐지 (sunset) — §결정 12 (external verifier auxiliary layer) / §결정 13 (3-anchor spawn trigger 운영 정의) / §결정 14 (effectiveness measurement wiring) + §17.4.3 (post_lane_return 4번째 anchor) 의 DialogFidelity 부분 carrier-preserved in-place 강등 (본문 보존 + Sunsetted banner). 보존 (무손상): §결정 1 (frame mode 4 step) / §결정 3 (Layer 1-4 cognitive enum + 5번째 layer 신설 금지 invariant re-home 수령) / §결정 15 (3 touchpoint frequency-richness 본체 §15.1/15.2/15.4) / §17.4.1 (PL self-attestation back-translation body) / §17.4.2 (Orchestrator divergence detection trigger) — 모두 DialogFidelity-independent. 검증 ground 보존 = 동일 anchor 의 Codex TP#2/TP#3 (mandatory P0/P1 inline FIX, ADR-052) + ADR-064 §결정 9 Q-3check (Orchestrator self-check). codeforge-pmo agent count 3→2.

      **이전 8개 Amendment 와 정반대 — sunset_justification 이 null 이 아니라 3축 evidence object** (ADR-058 §결정 5 약화 evidence-gate + ADR-064 §결정 7 symmetric ratchet 정합, first weaken-direction amendment, 약화 방향 1급 허용 evidence-grounded):
      (1) dead_mandate — 3-anchor spawn 의무 (특히 pre_architectpl_synthesis "항상 active") 런타임 미준수. CFP-2234 ArchitectPL synthesis 사용자 보고 시점 미spawn (CFP-2215 이전 TodoWrite dead 동형). 추가: 본 CFP-2236 설계 lane fable→opus fallback = fable 의존 불안정성.
      (2) verification_ground_redundancy — 동일 anchor Codex TP#2/TP#3 (mandatory P0/P1 inline FIX) + ADR-064 Q-3check 이미 cover. DialogFidelity = correction_action_hint 5-enum 권고만 = 최저 구속력.
      (3) cost_vs_effect_zero — 매 synthesis·매 FIX 직전 Opus verifier spawn 누적 비용, 측정 효과 0 (§결정 14 measurement deferred-followup 실 wiring 0).

      §15.3 무약화 표 DialogFidelity auxiliary(§결정 12) 행 + 3-anchor spawn(§결정 13) 행 + §결정 14 measurement 행 외과 제거 (frequency-richness 본체 + Layer 1-4 행 + §결정 2(c) richness 행 + Sub-mechanism 행 무손상). §결정 12.3 "5번째 cognitive layer 신설 금지 invariant" → §결정 3 (Layer 1-4 enum) re-home (삭제 아님, FeasibilityAgent §4.2 보존 명제 #2 SSOT). mechanical_enforcement_actions[] dialog-fidelity-effect action status → sunsetted (제거보다 status 변경 보수). codename-glossary-lookup action 무변경.

      ADR-071 전체 폐지 아님 — verifier auxiliary sub-layer 만 외과 절제, dialog governance 본체 (frame mode + 4 layer + 3 touchpoint) 유지. is_transitional=false permanent 유지 (부분 §결정 sunset, ADR 전체 강등 아님). paired sibling 정리 = live cross-ref (ADR-064:426 / ADR-039:138 = 최소 inline sunset pointer 추가 — additive cross-ref, 기존 본문 immutability 미충돌, 1급 active SSOT 오독 차단. forward-pointer sunset amendment 가 dangling 차단). 본 ADR-071 amendment forward-pointer 가 ADR-042 Amendment 6 (Opus pilot tier entry) 의 retired 표기 충분 (ADR-042 본문 무수정 보수).
    sunset_justification:
      dead_mandate: "3-anchor spawn 의무 (pre_architectpl_synthesis '항상 active' 포함) 런타임 미준수 — CFP-2234 ArchitectPL synthesis 사용자 보고 시점 미spawn (CFP-2215 이전 TodoWrite dead 동형) + CFP-2236 설계 lane fable→opus fallback (fable 의존 불안정성)"
      verification_ground_redundancy: "동일 anchor Codex TP#2/TP#3 (mandatory P0/P1 inline FIX, ADR-052) + ADR-064 §결정 9 Q-3check (Orchestrator self-check) 이미 cover — DialogFidelity = correction_action_hint 5-enum 권고만 = 최저 구속력"
      cost_vs_effect_zero: "매 synthesis·매 FIX 직전 Opus verifier spawn 누적 비용, 측정 효과 0 (§결정 14 measurement deferred-followup 실 wiring 0)"
      meta_policy_alignment: "ADR-058 §결정 5 (약화 evidence-gate, sunset_justification = 약화 evidence requirement) + ADR-064 §결정 7 (evidence-gated symmetric ratchet, 강화/약화 양방향 1급 허용) — first weaken-direction amendment, evidence-grounded 1급 허용"
  - amendment_id: 10
    date: "2026-06-19"
    carrier_story: CFP-2371
    issue: https://github.com/mclayer/plugin-codeforge/issues/2371
    summary: |
      §결정 5 결정 트리 redirect — over-asking 안전편향 제거, ask-trigger 3종 한정 (§결정 20 신설). 기존 "모호 → 가치 측 분류(safe direction) → AskUserQuestion" 폐기. 대신 ask-trigger 3종 (① 사용자 요구 자체 애매 = 명확화 필요 / ② 확실히 짚어야 하는 진짜 가치 trade-off = default 비자명 + 사용자 선호가 결과를 가름 / ③ 비가역·고비용 = 중대 결함 대응·대거 삭제·rollback·배포·외부 발송) 에 해당할 때만 AskUserQuestion 발화. 그 외 전부 — 모호 포함 — derived default 적용 + declare + 진행 + 1줄 정정 초대 ("안전하니 일단 물어" = safe-direction default-to-ask 금지). §결정 5 본문에 "§결정 20 으로 redirect" 1줄 cross-ref 추가 (본문 통째 삭제 아님 — 이력 보존).

      근거 (사용자 반복 directive 3회 — 2026-05-26 / 2026-06-09 / 2026-06-19): "묻는 건 ① 내 요구에 애매함 있을 때 ② 확실하게 짚고 가야 할 때만. 그 외엔 무조건 진행. 중대한 결함·대거 삭제·rollback 같은 거 아니면 무조건 진행." over-asking 안전편향이 CLAUDE.md "## 결정 · 대화 원칙" 자율 정책("자명하면 묻지 말고 진행")을 위반 — safe-direction-ask 가 기계적 default (문서화·착수·lane 진입·FIX 진행) 를 질문으로 오분류해 정주행을 중단시킴.

      무손상 invariant — frame mode 4 step (§결정 1) / Layer 1-4 cognitive enum (§결정 3) / sub-mechanism 2 종 (§결정 4) / §결정 2(c) richness (3 줄 제약 거부 · 길이 자유 · 배경 포함) / 3 touchpoint frequency-richness (§결정 15) 모두 무변경. 말 거는 빈도 (frequency / 어떤 결정에서 멈추느냐) 만 좁히고 말할 때의 풍부함은 그대로 보존 (ADR-071 §결정 15 frequency-richness 분리 invariant 정합). 5번째 cognitive layer 신설 아님 (§결정 3 Layer 1-4 enum count 불변, §결정 12.3 re-home invariant 정합 — 본 amendment 는 §결정 5 분류 규칙 변경, cognitive layer 추가 아님).

      ratchet 방향 — 본 amendment 는 "묻기 강화" 가 아니라 "묻기 절제" (weaken-direction). Amendment 9 (DialogFidelityAgent sunset) 에 이은 두 번째 weaken-direction amendment — ADR-058 §결정 5 약화 evidence-gate + ADR-064 §결정 7 evidence-gated symmetric ratchet 정합. sunset_justification 3축 evidence object 로 약화 근거 명시 (사용자 반복 directive = behavioral evidence). doc-only fast-path Story (ADR-054, src/tests touch 0, 단일 PR). additive cross-ref — §결정 5 본문 immutability 미충돌 (redirect pointer 1줄만 추가, 기존 본문 보존).
    sunset_justification:
      dead_mandate: "기존 §결정 5 'AMBIGUOUS → 가치 측 분류(safe direction) → AskUserQuestion' 룰이 CLAUDE.md \"## 결정 · 대화 원칙\" 자율 정책('합리적 default 가 자명하면 묻지 말고 진행')과 직접 충돌 — 기계적 default (문서화·착수·lane 진입·FIX 진행) 를 가치 측으로 오분류해 over-asking 유발. 사용자 반복 directive 3회 (2026-05-26 / 2026-06-09 / 2026-06-19) = behavioral evidence, pattern_count 3 ≫ ADR-045 §D-9 threshold 2."
      verification_ground_redundancy: "진짜 멈춰야 하는 가치 trade-off (default 비자명 + 사용자 선호가 결과를 가름) 는 ask-trigger ② 로 보존, 비가역·고비용 안전판은 ask-trigger ③ (+ touchpoint (a) 결과-명세 확인) 으로 보존 — safe-direction 모호 자동 격상 없이도 진짜 결정 분기는 그대로 cover. 모호 영역의 derived default 추론 능력은 ADR-064 §결정 3 룰 1 (사실 판단 default) 과 동형."
      cost_vs_effect_zero: "모호 자동 ask 격상의 효과 (잘못된 default 회피) < 비용 (정주행 중단 + 사용자 burden + 자율 정책 위반) — derived default 추론 가능 시 future 영향 큼만으론 ask 사유 부족. 잘못 추측 비용이 진짜 큰 경우는 ask-trigger ③ (rollback 비쌈) + touchpoint (a) 가 이미 잡음."
      meta_policy_alignment: "ADR-058 §결정 5 (약화 evidence-gate) + ADR-064 §결정 7 (evidence-gated symmetric ratchet, 강화/약화 양방향 1급) — Amendment 9 에 이은 second weaken-direction amendment, evidence-grounded 1급 허용. CLAUDE.md \"## 결정 · 대화 원칙\" 자율 정책 + feedback_autonomous_until_decision (진짜 가치 선택 분기에서만 정지) 정합."
  - amendment_id: 11
    date: "2026-06-20"
    carrier_story: CFP-2374
    issue: https://github.com/mclayer/plugin-codeforge/issues/2374
    summary: |
      §결정 21 신설 — dialog skip-offer 금지. 런타임에 Orchestrator 가 사용자에게 "생략/간소화/빠르게/경량으로 갈까요" 를 선택지로 제시하는 것 금지. 정식 풀 플로우는 비협상(non-negotiable) 기본값(ADR-127)이므로 생략은 애초에 결정 분기가 아니다 → AskUserQuestion 비대상. §결정 20 (Amendment 10, CFP-2371) ask-trigger 3종 한정과 정합 — CFP-2371 = 질문 빈도 절제, 본 Amendment = 특정 질문 종류(skip-offer)의 PATH 폐지. "생략 여부" 는 derived default 항상 정식으로 자명 → ask-trigger ② 미해당 → 묻지 않고 정식 진행. 둘 다 "불필요한 멈춤 제거" 방향 정합. SSOT = ADR-127 §결정 4.
    sunset_justification: null   # 강화 방향 (skip-offer 라는 약화 옵션 제거 = ratchet 강화) — Amendment 9/10 의 weaken-direction(묻기 절제)과 달리 본 Amendment 는 정식성 약화 선택지 자체 제거 = 강화 방향 → ADR-058 §결정 5 약화 evidence-gate 비대상. 무손상 — frame mode(§결정 1) / Layer 1-4(§결정 3) / sub-mechanism(§결정 4) / §결정 2(c) richness / 3 touchpoint(§결정 15) / 5번째 cognitive layer 신설 금지 invariant 전부 보존 (§결정 5 분류 규칙 변경 아닌 skip-offer PATH 폐지, layer count 불변).
  - amendment_id: 12
    date: "2026-06-24"
    carrier_story: CFP-2392
    issue: https://github.com/mclayer/plugin-codeforge/issues/2392
    summary: |
      §18.7 deferred carrier 해제 — "MEMORY.md 인덱스 entry 슬림화 mechanism" 의 별 carrier 가 ADR-129 로 확정. §18.7 deferred 마커에 `resolved_carrier: ADR-129` 추가 (defer 해제). ADR-129(OMC-adopt 지식캡처 + 메모리 다이어트) §결정 2 가 §18.2 24.4KB cap + §18.3 슬림화 normative 를 실 mechanism(2-layer budget: per-entry ~200자 one-line(harness reminder 도출) + total 24.4KB(§18.2 도출) + oldest-first/completed-Story consolidate 슬림화 + archive-not-delete + active-Story preserve lossless invariant)으로 실현. §18 본문(§결정 18 / anti-pattern 7종 / axis disjoint / §18.1-18.6) 의미 변경 0건 — §18.7 out-of-scope 항목 1건의 carrier 지정만(deferred → resolved). char-budget 은 OMC 차용 아님(firsthand: OMC skillify char-cap/descriptor-only split 없음) = internal 도출 명시. paired sibling = ADR-045 Amendment 14 (§D-13 phase:완료 capture self-check) + ADR-129 (umbrella). ADR-051 skill form(skills/knowledge-capture-gate/SKILL.md §2 slimming-protocol SSOT). SSOT = ADR-129 §결정 2.
    sunset_justification: null   # 강화 방향 (deferred mechanism 을 실 규약으로 실현 = forcing function 추가, ratchet 강화) — ADR-058 §결정 5 약화 evidence-gate 비대상. 무손상 — §결정 18 / anti-pattern 7종 / §18.1-18.6 / §18.8 전부 보존 (§18.7 out-of-scope 항목 1건 carrier 지정만, deferred → resolved).
  - amendment_id: 13
    date: "2026-07-04"
    carrier_story: CFP-2567
    issue: https://github.com/mclayer/plugin-codeforge/issues/2567
    summary: |
      §결정 22 신설 — Epic 내 Story 전환 자율 진행 (전환 지점 over-halt/over-ask 방지). Epic 을 한 세션에서 여러 child Story 로 진행할 때 Story N→N+1 전환 경계 (및 단일 Story Phase1→Phase2 전환) 에서 Orchestrator 가 무발화로 정지(over-halt) 하거나 "다음 Story 진행할까요?" 확인 질문(over-ask) 하는 것을 차단. 전환 = 자동 이어서 진행이 derived default, 멈춤·질문은 default 아님. D1 = 전환이 실제로 일어나는 지점 문서(skills/story-epic-flow-preflight/SKILL.md Epic-flow child-transition point PRIMARY + docs/orchestrator-playbook.md §3.4/§1.2 operational mirror + CLAUDE.md "## 결정 · 대화 원칙" peer bullet) 에 자율 진행 norm 국소 명시 — 지금까지 전역 dialog 규칙(§결정 15/20)에만 암묵 존재하던 것을 전환 지점에 surface. D2 = UserPromptSubmit 예방 reminder hook 신설(hooks/story-transition-autonomy-reminder + .py, hooks.json UserPromptSubmit 배열 5번째 entry append) — skip-offer-reminder(§결정 21 / Amendment 11) 동형 hook-frame(ADR-115 5층 graceful degradation, 전경로 exit 0, JSON additionalContext emit) 재사용 = 구조 novelty ~0. reminder TEXT 는 정당 멈춤 3종(ask-trigger ① 요구 애매 / ② 진짜 가치 trade-off / ③ 비가역·고비용) carve-out 을 반드시 포함해 over-suppression(EDGE-1) 차단. **D2 채널 2 (FIX-3)** = PreToolUse(Agent) additionalContext non-block inject — 기존 배선된 hooks/pretooluse-agent-spawn-gate 확장(NEVER deny), Story k+1 lane-PL spawn = UserPromptSubmit 가 dark 인 autonomous 전환 창에 도달하는 유일 lever = 본 Story 존재 이유.

      §결정 22 = §결정 15(over-halt = 3-touchpoint 미해당 발화 정지) + §결정 20(over-ask = ask-trigger 미해당 확인 질문) 를 전환 지점에 적용 강화(매핑, 재정의 아님). §결정 18(session-swap reflex) 와 disjoint 축 — cross-ref only, session-swap 재codify 0. **closed-enum 무손상 명제(핵심)**: 본 §결정은 §결정 15 3-touchpoint / §결정 20 ask-trigger 3종 enum 에 member 를 추가하지 않는다. "Story 전환 진행 확인" 은 어느 enum 에도 미등재(= 발화 정당 사유 아님)이며, 본 §결정은 그 비-등재 상태를 전환 지점에서 surface + 예방강제할 뿐 → §15.5/§16.6 closed-enum 확장 규약 미발동(touchpoint 추가 0, trigger 추가 0, 사용자 burden 증가 0). D2 = UserPromptSubmit 예방 reminder(신규 sibling hook, user-turn 창) + PreToolUse(Agent) additionalContext non-block inject(pretooluse-agent-spawn-gate 확장, autonomous 전환 창 — Story 존재 이유) 2-channel. Stop/SubagentStop force-continue/개입 REJECT(ADR-115 §결정 2 platform-broken #10412/#55754 + 정당/부당 구분 불가). ASM-2 platform-limit 재확인 — runtime 발화 前 hard-block 불가(PreToolUse(AskUserQuestion) 미지원 anthropics/claude-code#15872 CLOSED/NOT_PLANNED); over-halt(무발화, no-spawn) 순간 = Stop/SubagentStop fire 하나 개입 불가 + PreToolUse(Agent)·UserPromptSubmit 는 fire 안 함 → correct lever 없음 = prevention/priming only(AC-3 documented blind-spot). D2 = warning-tier 예방/surface only, hollow-detection gate 아님.

      무손상 invariant — frame mode 4 step(§결정 1) / Layer 1-4 cognitive enum(§결정 3) / sub-mechanism 2 종(§결정 4) / §결정 2(c) richness(3 줄 제약 거부·길이 자유·배경 포함) / 3 touchpoint frequency-richness(§결정 15) / ask-trigger 3종(§결정 20) / skip-offer 금지(§결정 21) / 5번째 cognitive layer 신설 금지 invariant 전부 보존 (§결정 22 = 기존 §결정 15/20 의 전환 지점 적용 강화, cognitive layer·touchpoint·trigger enum count 전부 불변). third strengthen-direction amendment(Amendment 11/12 에 이음). doc+hook carrier — D1 doc 명시 + D2 reminder hook(skip-offer 동형, mechanical_enforcement_actions[] reminder-only precedent 정합 — 별 action entry 불요). is_transitional=false 보존, 해소 기준 무변경.
    sunset_justification: null   # 강화 방향 (전환 지점 자율 진행 norm surface + 예방 reminder 추가 = forcing function 강화 ratchet) — ADR-058 §결정 5 약화 evidence-gate 비대상. 무손상 — frame mode(§결정 1) / Layer 1-4(§결정 3) / sub-mechanism(§결정 4) / §결정 2(c) richness / 3 touchpoint(§결정 15) / ask-trigger 3종(§결정 20) / skip-offer(§결정 21) / 5번째 cognitive layer 신설 금지 invariant 전부 보존 (§결정 15/20 enum member 추가 0 — 전환 지점 적용 강화만).
  - amendment_id: 14
    date: "2026-07-05"
    carrier_story: CFP-2573
    issue: https://github.com/mclayer/plugin-codeforge/issues/2573
    summary: |
      §결정 22 scope 일반화 (transition-only → 모든 자명-진행 지점) + consumer 전파 (§22.9 신설). ADR-144 §결정 3(L2) + §결정 6(L6) realization. Amendment 13(§결정 22) 이 "Story 전환 지점" 에 한정했던 D2 reminder TEXT scope 를 "모든 자명-진행 지점(전환 + lane 경계 + 완료-후 + vague-pause 금지 포함)" 으로 넓힌다. 2채널(UserPromptSubmit user-turn 창 = hooks/story-transition-autonomy-reminder.py + PreToolUse(Agent) autonomous 창 = hooks/pretooluse-agent-spawn-gate) 모두 내부 TEXT+docstring broaden.

      **hook public identity 무변경 (ModuleArch binding)**: 신규 hook 파일 0 — 기존 hook 의 파일명·hooks.json 5번째 entry·run-hook.cmd·§22.7 back-refs 전부 stable. 한 hook 의 TEXT 를 넓혀도 concern 은 여전히 하나(autonomous-progress priming) = one-concern-per-hook 정합. §22.7 "shared reminder-base 추출 금지" 의 의미 = cross-hook **CODE** abstraction 금지(YAGNI/fail-isolation, hook 은 self-contained stdlib zero cross-import 유지)이지 TEXT-scope 금지가 아니다 → TEXT broadening 은 §결정 22 generalization 정합.

      **closed-enum 무손상 (§22.3 상속)**: §결정 15 3-touchpoint / §결정 20 ask-trigger 3종 enum 에 member 추가 0. "자명-진행" 은 어느 enum 에도 미등재(= 발화 정당 사유 아님) 상태를 더 많은 지점에서 surface 할 뿐. vague-pause 금지 문구 = ADR-025 Amendment 3(§결정 7 illegal 표 6번째 행) 의 dialog-side priming mirror — 정당 멈춤 3종(ask-trigger ①②③) carve-out **verbatim 보존**(over-suppression 차단, EDGE-1). **NEVER block** — GAP-1/GAP-2 순간엔 어떤 hook 도 fire 안 함(documented blind-spot, ADR-144 §결정 7). warning-tier 예방/priming only.

      **L6 consumer 전파**: reminder TEXT 확장을 hooks/hooks.json 배선으로 두면 plugin 설치 시 consumer 자동전파(overlay 변경 0, CFP-2456 skip-offer 선례 동형 — §22.7 "consumer 전파 out-of-scope" 를 본 Amendment 가 해소). reminder TEXT 는 STATIC(runtime value interpolation 금지, no PII). consumer telemetry sharing = opt-in default-false 보존(ADR-043 §결정 1) — 로컬 ledger append 는 이미 wrapper+consumer 양쪽 ungated(기존 CFP-1743 behavior, 새 flip 아님, ADR-144 §결정 6 정직 nuance).

      무손상 invariant — frame mode 4 step(§결정 1) / Layer 1-4 cognitive enum(§결정 3) / sub-mechanism 2 종(§결정 4) / §결정 2(c) richness / 3 touchpoint(§결정 15) / ask-trigger 3종(§결정 20) / skip-offer(§결정 21) / §결정 22 D1·D2 2-channel 구조 / 5번째 cognitive layer 신설 금지 invariant 전부 보존 (§결정 22 의 TEXT scope broaden + consumer 전파만 = mechanism 확장, cognitive layer·touchpoint·trigger enum count 전부 불변). fourth strengthen-direction amendment(Amendment 11/12/13 에 이음).
    sunset_justification: null   # 강화 방향 (자명-진행 priming scope 확장 + consumer 전파 = forcing function 강화 ratchet) — ADR-058 §결정 5 약화 evidence-gate 비대상. 무손상 — §결정 22 D1/D2 구조 + closed-enum(§결정 15/20 member 추가 0) + carve-out verbatim 전부 보존.
  - amendment_id: 15
    date: "2026-07-17"
    carrier_story: CFP-2725
    issue: https://github.com/mclayer/plugin-codeforge/issues/2725
    summary: |
      §결정 23 신설 — 요구사항 lane intake 항상 declare touchpoint (4번째, §15.5 확장) + §결정 20 lane-scoped carve-out 명문 + design-entry 확정 gate = §결정 22 정당 멈춤 carve-out. 신규 ADR-159 (요구사항 lane enrichment 일급 + design-entry 확정 gate) 의 발화 frequency 축 짝 wiring. 3부:
      (a) **intake 항상 declare = 4번째 touchpoint (§15.5 closed-enum 확장 규약 첫 실사용)** — §결정 15 3-touchpoint closed enum 에 요구사항 lane-scoped 4번째 touchpoint "intake 배경·의도 재진술 declare" 를 §15.5 확장 규약(별도 CFP 신설 의무 + Story §1 사용자 explicit 승인 의무 + 강화 ratchet)으로 추가. CFP-2725 + §1 사용자 확정 선호 4항이 §15.5 forcing function 요건 충족(발동 항상 = 사용자 explicit 승인). **STRENGTHEN frame — mandatory DECLARE ≠ mandatory ASK**: intake 왕복 = derived-default 재진술 declare 패턴(§결정 16 natural-language trigger no-dialog-reflex derived-default 동형)이지 매 접수마다 사용자를 멈춰 세우는 ASK 아님. trivial 최소형 = 재진술 1~3줄 + "이의 없으면 진행" + 열린 질문 0~1개(명시 답변 대기 없이 진행 가능), 모호(ask-trigger ① 해당) 시만 ASK escalate. 이 DECLARE≠ASK 구분이 §결정 20 (ask-trigger 3종 한정) 과의 충돌을 원천 해소.
      (b) **§결정 20 lane-scoped carve-out 명문** — 요구사항 lane 한정 "항상 declare" carve-out 을 §결정 20 에 명시하되 **타 lane 일반화 명시 금지** (§결정 20 본체 = ask-trigger 3종 한정 보존). 요구사항 lane 의 what(요구 명세) disambiguation 은 §15.1 "how/what 경계 — what disambiguation 은 억제 비대상" 의 lane-scoped 강화 (frequency 축소 ≠ richness 축소 invariant 정합).
      (c) **design-entry 확정 gate = 발화 touchpoint + §결정 22 정당 멈춤 carve-out** — 요구사항리뷰 PASS 후·설계 진입 직전 사용자 최종 확정 요청 = 기존 §결정 15 touchpoint (a) 결과-명세 확인 성격(사용자 선언 결과 자체 확인) + ask-trigger ①(요구 애매)/③(비가역·고비용). 확정 대기 stop = ask-trigger 정당 stop(payload>0, ADR-144 A1)이라 §결정 22 정당 멈춤 3종 carve-out 에 명시적 귀속 — transition-autonomy hook(§22.1 D2)이 설계 진입 지점을 over-halt 오탐하지 않도록 명문화. §결정 22 정당 멈춤 3종(ask-trigger ①②③) carve-out verbatim 무변경.
      무손상 invariant (전부 보존): frame mode 4 step(§결정 1) / Layer 1-4 cognitive enum(§결정 3) / sub-mechanism 2 종(§결정 4) / §결정 2(c) richness / 3 touchpoint frequency-richness 본체(§결정 15 §15.1 how·what 경계) / ask-trigger 3종 본체(§결정 20) / skip-offer 금지(§결정 21) / §결정 22 D1·D2 2-channel 구조·carve-out / 5번째 cognitive layer 신설 금지 invariant. 4번째 touchpoint 추가 = §15.5 확장 규약 준수(요구사항 lane-scoped, 사용자 explicit 승인) — closed-enum 우회 아님. fifth strengthen-direction amendment(Amendment 11/12/13/14 에 이음). ADR-159 SSOT / ADR-077 Amendment 1(terminal event·counter) / ADR-125 Amendment 3(확정 위치·내부적합) 짝.
    sunset_justification: null   # 강화 방향 (§15.5 확장 규약 준수 4번째 touchpoint 추가 = 발화 frequency 증가 강화 ratchet, 요구사항 lane-scoped) — ADR-058 §결정 5 약화 evidence-gate 비대상. 무손상 — frame mode(§결정 1) / Layer 1-4(§결정 3) / sub-mechanism(§결정 4) / §결정 2(c) richness / 3 touchpoint 본체(§결정 15) / ask-trigger 3종 본체(§결정 20) / skip-offer(§결정 21) / §결정 22 carve-out / 5번째 cognitive layer 신설 금지 invariant 전부 보존. DECLARE≠ASK — mandatory ASK 신설 아님.
  - amendment_id: 16
    date: "2026-07-18"
    carrier_story: CFP-2742
    issue: https://github.com/mclayer/plugin-codeforge/issues/2742
    summary: |
      §결정 24 신설 — Session-swap controlled-path: 자족 handoff 프롬프트 동반 시 세션 전환 권유 허용 (§결정 18 조건부 완화, first weaken for §결정 18). 7부(a~g + sunset):
      (a) controlled-path 정의 = 전환 권유 前 자족 handoff 프롬프트 선제 생성·동반 시 허용, bare reflex 전환 = §결정 18 anti-pattern 7종 그대로 차단(handoff 미동반 케이스 무손상 — carve-out 은 handoff-present 케이스 한정).
      (b) handoff 6 필수요소(① 진행 Story/PR·Epic 번호 ② 완료 vs 남은 lane·단계 ③ worktree·브랜치 경로 ④ 기결정=재논의 금지 목록 ⑤ 이번 세션 gotcha ⑥ 다음 세션 첫 액션 1문) + 자족성 2축(현세션 참조 0 / 복붙 1회) = ADR-085 §결정 9 4-rule specialization(재발명 금지 cross-ref).
      (c) Q1 = 모든 전환 권유(정당 2-trigger ADR-053/057 포함)에 handoff 의무 — 재도출 비용은 전환 이유(WHY)와 무관하게 발생. trigger SET 무변경(anti-pattern 7종·정당 2종 member 추가/삭제 0), handoff = 직교 cross-cutting 의무(AC-4 정합).
      (d) forced-continuation(§결정 24 scope = 동일 sequential stream 을 fresh 세션이 이어감) vs planned-lane-split(ADR-085 §결정 9 rule 1 이 금지 = 한 Story lane 을 병렬/단계 인위 분할) disjoint 경계 — controlled-path 는 planned-division 미허가(rule 1 여전히 금지).
      (e) consumer 전파 vehicle = Phase 2 설계 명세: 신규 sibling hook session-swap-handoff-reminder(.py, self-contained stdlib, ADR-115 5층, 全경로 exit0 fail-open, UserPromptSubmit additionalContext STATIC no-PII) + hooks.json 6th UserPromptSubmit entry + ADR-144 §결정 6 L6 자동전파(overlay 변경 0, CFP-2456/CFP-2573 선례) + TestContractArch objection#1(first-class self-test + §7.3 co-fire marker).
      (f) advisory ceiling 정직 — GAP-1(pre-utterance hard-block)/GAP-2(over-halt 실시간 검출) hard-block 불가(ADR-144 §결정 7, #15872/#10412/#55754), priming/PRIMING 채널 only(배선됨 ≠ 규범 준수 증명), "100% 기계강제" over-claim = 산출물 결함.
      (g) axis disjoint — §결정 22(line 1285 무손상, transition-autonomy cross-ref only 재codify 0) / §결정 18 anti-pattern 7종 enum 텍스트 무변경(본문 immutability, §18.1 상단 1-line cross-ref pointer만 additive) / §결정 23 disjoint.

      **WEAKEN-direction (부분 약화, §결정 18 첫 weaken)** — anti-pattern 7종의 "무조건 발화 차단" → "handoff 동반 시 조건부 허용" = prohibition scope 축소. Amendment 9/10 에 이은 third weaken-direction amendment. ADR-058 §결정 5 약화 evidence-gate 적용 → sunset_justification = null 아닌 4-key evidence object 충족(1급 허용, 차단 아님). Phase 1(본 PR) = ADR-071 §결정 24 + §18.1 cross-ref pointer + CLAUDE.md L65 정합 + consumer-guide §7.6(정책 prose only). Phase 2(별 PR, 본 PR 미포함) = hook 파일 + hooks.json 6th entry + §2h.6 + self-test(§8). 무손상 — frame mode(§결정 1) / Layer 1-4(§결정 3) / sub-mechanism(§결정 4) / §결정 2(c) richness / 3 touchpoint(§결정 15) / ask-trigger 3종(§결정 20) / skip-offer(§결정 21) / §결정 22 D1·D2 구조·carve-out / §결정 23 / 5번째 cognitive layer 신설 금지 invariant 전부 보존(정당 trigger 2종 + anti-pattern 7종 enum member 추가·삭제 0 — controlled-path gate 만 신설).
    sunset_justification:
      dead_mandate: "§결정 18 anti-pattern 7종의 '무조건 차단' 이 우려한 실체 = session swap 시 in-session cached state(진행 맥락/결정 이력/worktree·branch 위치/gotcha) 소실 → 새 세션 처음부터 재도출(§18.1/§18.3). 자족 handoff 프롬프트가 이 손실 대상을 전량 이월하면(6 필수요소) '재도출 비용' 근거가 handoff-present 케이스에서 소멸 → '무조건 차단' 의 정당 근거가 그 케이스에 한해 dead. 사용자 directive 2건(2026-07-17~18: '세션 전환 추천 시 다음 세션 프롬프트 일단 생성' + 'memory 아닌 consumer 전파') = behavioral evidence."
      verification_ground_redundancy: "§결정 18 이 지키려던 것(무준비 전환 방지)은 controlled-path 가 handoff 6요소 의무로 오히려 강화 — bare reflex 전환은 여전히 anti-pattern 차단(handoff 미동반 케이스 무손상), 정당 2-trigger(ADR-053/057)도 handoff 의무 부착. /compact·MEMORY.md 슬림화 대체 path(§18.3) 무손상 보존 — controlled-path 는 전환을 장려하지 않고 '전환이 발생하면 handoff 의무화' 하는 직교 forcing function."
      cost_vs_effect_zero: "'무조건 차단' 을 handoff-present 케이스까지 유지하는 효과(전환 억제) < 비용(handoff 로 재도출 비용 0 인데도 정당한 인계형 전환까지 금지 → context/memory 포화 mid-work 에서 정주행 불가). handoff 동반 controlled-path 는 재도출 비용을 제거하므로 '무조건 차단' 의 보호 효과가 handoff-present 케이스에서 0 으로 수렴."
      meta_policy_alignment: "ADR-058 §결정 5 (약화 evidence-gate, sunset_justification = 약화 evidence requirement) + ADR-064 §결정 7 (evidence-gated symmetric ratchet, 강화/약화 양방향 1급) — §결정 18 첫 weaken-direction amendment, evidence-grounded 1급 허용. 사용자 §1 요구 #3 verbatim('anti-pattern 을 gated 경로로 격상') = 완화 프레이밍 정합."
related_stories:
  - CFP-612  # carrier
  - CFP-525  # ancestor Epic (closed 2026-05-13)
  - CFP-582  # conceptual pair (agent ↔ agent debate domain)
  - CFP-445  # ADR-064 carrier (proposing-time 5 룰 mother policy)
  - CFP-387  # ADR-058 sunset criteria carrier
  - CFP-436  # ADR-063 atomic invariant carrier
  - CFP-438  # ADR-065 mechanical self-check carrier
  - CFP-411  # ADR-052 Amendment 1 (touchpoint #4) carrier
  - CFP-578  # ADR-070 verify-before-trust carrier
  - CFP-777  # Amendment 1 carrier (DialogFidelityAgent additive auxiliary)
  - CFP-761  # parent Epic (DialogFidelityAgent 도입)
  - CFP-818  # Amendment 2 carrier (spawn trigger 운영 정의)
  - CFP-833  # Amendment 3 carrier (effectiveness measurement wiring — closing-the-loop)
  - CFP-851  # Amendment 4 carrier (conversational reporting frequency suppression contract)
  - CFP-1104 # Amendment 5 carrier (natural-language action trigger lookup table — "codeforge upgrade" mapping)
  - CFP-1110 # Amendment 6 carrier (lane back-translation gate binding — paired ADR-082 Amendment 5, 사용자 직권 minimal path first application, paradox-break)
  - CFP-1340 # Amendment 7 carrier (unjustified session swap reflex 차단 + /compact normative — §결정 18 신설, ADR-053/057 trigger closed 2-set + anti-pattern 7종, 재발 incident 2건 evidence pattern_count 2 reach)
  - CFP-1764 # Amendment 8 carrier (agent burst output paste 합성 시 mid-turn glossary lookup 의무 — §결정 19 신설, docs/wording-dictionary.md 카테고리 (c) codename → 평이 어휘 mapping table SSOT, closed 15 codename 첫 batch + ratchet extensibility, source incident mctrader-hub#517 4-turn 누적 jargon leak)
  - CFP-2236 # Amendment 9 carrier (DialogFidelityAgent 전면 폐지 sunset — §결정 12/13/14 + §17.4.3 DialogFidelity 부분 carrier-preserved 강등, first weaken-direction amendment, sunset_justification 3축 evidence object, codeforge-pmo agent count 3→2, ADR-058 §결정 5 + ADR-064 §결정 7 evidence-gated symmetric ratchet 정합)
  - CFP-2371 # Amendment 10 carrier (§결정 5 결정 트리 redirect — over-asking 안전편향 제거, ask-trigger 3종 한정 §결정 20 신설, "모호 → 가치 측(safe direction)" 폐기 → 모호 포함 전부 derived default+진행이 기본, second weaken-direction amendment, sunset_justification 3축 evidence object, 사용자 반복 directive 3회 evidence pattern_count 3 reach, frame mode/Layer 1-4/sub-mechanism/3 touchpoint richness 무손상)
  - CFP-2374 # Amendment 11 carrier (§결정 21 신설 — dialog skip-offer 금지, third strengthen-direction amendment, ADR-127 §결정 4 SSOT)
  - CFP-2392 # Amendment 12 carrier (§18.7 MEMORY.md 슬림화 mechanism deferred 해제 resolved_carrier: ADR-129, OMC-adopt 지식캡처+메모리다이어트 묶음, paired sibling ADR-045 Amendment 14)
  - CFP-2567 # Amendment 13 carrier (§결정 22 신설 — Epic 내 Story 전환 자율 진행, 전환 지점 over-halt/over-ask 방지. D1 doc 국소 명시 + D2 2-channel(UserPromptSubmit 예방 reminder hook skip-offer 동형, user-turn 창 + PreToolUse(Agent) additionalContext non-block inject pretooluse-agent-spawn-gate 확장, autonomous 전환 창), §결정 15/20 전환 지점 적용 강화 = enum member 추가 0, §결정 18 disjoint cross-ref, third strengthen-direction, Stop/SubagentStop force-continue/개입 REJECT ADR-115 §결정 2)
  - CFP-2573 # Amendment 14 carrier (§결정 22 scope 일반화 transition-only → 모든 자명-진행 지점 + vague-pause 금지 + consumer 전파, ADR-144 §결정 3(L2)/§결정 6(L6) realization. hook TEXT+docstring broaden only — 파일명·hooks.json entry·§22.7 back-refs stable, closed-enum member 추가 0, carve-out verbatim 보존, NEVER block, fourth strengthen-direction)
  - CFP-2725 # Amendment 15 carrier (§결정 23 신설 — 요구사항 lane intake 항상 declare 4번째 touchpoint §15.5 확장 + §결정 20 lane-scoped carve-out + design-entry 확정 gate §결정 22 정당 멈춤 carve-out. mandatory DECLARE≠ASK, fifth strengthen-direction. ADR-159 SSOT 짝)
  - CFP-2742 # Amendment 16 carrier (§결정 24 신설 — session-swap controlled-path: 자족 handoff 프롬프트 동반 시 전환 권유 허용, §결정 18 첫 weaken-direction. handoff 6 필수요소 = ADR-085 §결정 9 4-rule specialization, Q1 모든 전환에 handoff 의무 trigger SET 무변경, forced-continuation≠planned-lane-split disjoint, consumer 전파 Phase 2 hook 설계 명세, advisory ceiling ADR-144 §결정 7 GAP, §결정 18 본문 immutability + §18.1 cross-ref pointer만, sunset_justification 4-key evidence object)
related_adrs:
  - ADR-064  # 결정 원칙 mandate — proposing-time 5 룰 mother policy (mechanical version 승격 source)
  - ADR-058  # sunset criteria mandate (is_transitional: false 정합)
  - ADR-052  # Codex Proactive Check 6 touchpoint (Amendment 1 multi-round debate + Amendment 3 fact-check marker)
  - ADR-059  # debate-protocol-v1 (conceptual cross-ref only — schema fit 부적합)
  - ADR-063  # marketplace atomic invariant (plugin.json MINOR bump 발화)
  - ADR-065  # ArchitectAgent Phase 1 mechanical self-check 7-item
  - ADR-070  # Codex verify-before-trust (fact-check marker source)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무 (governance category)
  - ADR-039  # inline whitelist 1번 entry (사용자 dialog) cognitive layer 강화
  - ADR-060  # evidence-enforceable framework (Amendment 3 dialog-fidelity-effect entry carrier — CFP-833)
  - ADR-076  # declarative-reconciliation-upgrade (Amendment 5 — invariant `user_decision_branches: 0` dialog 단계 enforcement carrier)
  - ADR-054  # doc-only fast-path (Amendment 5 — Story 분류 정합)
  - ADR-082  # Amendment 6 — paired sibling carrier (lane PL spawn prompt user-utterance verbatim anchor / write-time input anchor ↔ 본 ADR Amendment 6 §결정 17 = lane return back-translation gate / return-time output gate, disjoint axis)
  - ADR-053  # Amendment 7 — session swap reflex trigger #1 (구조 변경 재구동) closed 2-set first entry
  - ADR-057  # Amendment 7 — session swap reflex trigger #2 (Sonnet/Haiku → Opus fallback) closed 2-set second entry
  - ADR-024  # Amendment 8 — hotfix-bypass:codename-glossary-lookup 75번째 family member (Story-2 carrier)
  - ADR-060  # Amendment 8 — evidence-checks-registry warning-tier 23번째 entry codename-glossary-lookup (Story-2 carrier)
  - ADR-037  # Amendment 9 — plugin bump semantics (DialogFidelityAgent 제거 = capability 축소 = MINOR, CFP-777 신규 agent MINOR 와 대칭)
  - ADR-042  # Amendment 9 — Amendment 6 Opus pilot tier entry (DialogFidelityAgent) retired (ADR-042 본문 무수정 — 본 ADR-071 amendment forward-pointer 충분)
  - ADR-129  # Amendment 12 — §18.7 MEMORY.md 슬림화 mechanism deferred 해제 resolved_carrier (OMC-adopt 지식캡처+메모리다이어트 umbrella)
  - ADR-045  # Amendment 12 — paired sibling Amendment 14 (§D-13 phase:완료 capture self-check precondition)
  - ADR-115  # Amendment 13 — hook 5층 graceful degradation + Stop hook block 금지 record-only (D2 reminder hook-frame 재사용 SSOT + Stop force-continue REJECT 근거 §결정 2)
  - ADR-061  # Amendment 13 — thin wrapper hook 구조 규약 (D2 hook = self-contained stdlib, scripts/lib SSOT 패턴)
  - ADR-127  # Amendment 13 — 정식 풀 플로우 비협상 (자동 진행 ≠ 게이트 skip ≠ lane 생략 ASM-1, skip-offer §결정 21 SSOT)
  - ADR-144  # Amendment 14 — anchor SSOT (stop taxonomy 3축 + decision-null pause 신설, §결정 3 L2 = 본 §결정 22 scope 일반화 realization / §결정 6 L6 = consumer 전파)
  - ADR-043  # Amendment 14 — telemetry privacy (consumer telemetry sharing opt-in default-false 보존, L6 정직 nuance)
  - ADR-159  # Amendment 15 — 요구사항 lane enrichment 일급 + design-entry 확정 gate SSOT (본 Amendment = 발화 frequency 축 짝 wiring)
  - ADR-077  # Amendment 15 — 짝 (terminal event + counter disjoint, ADR-077 Amendment 1). 확정 발화 event taxonomy
  - ADR-125  # Amendment 15 — 짝 (사용자 확정 = 리뷰 PASS 후·설계 진입 전 위치, ADR-125 Amendment 3). design-entry gate 시퀀스 전제
  - ADR-144  # Amendment 15 — 확정 대기 stop = payload>0 정당 멈춤(A1), §결정 22 정당 멈춤 carve-out anchor
  - ADR-085  # Amendment 16 — §결정 9 multi-session prompt design 4-rule prior art (handoff 6 필수요소 = specialization, 재발명 금지 cross-ref) + §결정 9 rule 1 planned-lane-split 금지 = forced-continuation disjoint 경계 SSOT
  - ADR-058  # Amendment 16 — §결정 5 약화 evidence-gate 적용 (§결정 18 첫 weaken-direction, sunset_justification 4-key evidence object)
  - ADR-144  # Amendment 16 — §결정 6 L6 consumer 전파 vehicle(hook 자동전파, overlay 변경 0) + §결정 7 advisory ceiling GAP-1/GAP-2 (runtime hard-block 불가 정직)
  - ADR-053  # Amendment 16 — controlled-path 무변경 보존 대상: 정당 trigger #1(구조 변경 재구동) — handoff 의무만 부착
  - ADR-057  # Amendment 16 — controlled-path 무변경 보존 대상: 정당 trigger #2(모델 fallback) — handoff 의무만 부착
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/orchestrator-communication-incidents.md
  - docs/wording-dictionary.md  # Amendment 8 — 카테고리 (c) codename → 평이 어휘 mapping table SSOT
  - skills/user-dialog-mode/SKILL.md
  - docs/parallel-work/section-ownership.yaml
  - plugins/codeforge-pmo/agents/DialogFidelityAgent.md  # Amendment 9 — DELETE (sunset)
  - plugins/codeforge-pmo/CLAUDE.md  # Amendment 9 — 3→2 sibling roster
  - plugins/codeforge-pmo/docs/architecture/codeforge-pmo.md  # Amendment 9 — 모듈 표 3→2 + verifier surface 제거
  - plugins/codeforge-pmo/.claude-plugin/plugin.json  # Amendment 9 — version 0.3.4→0.4.0 MINOR + description sunset 절
  - docs/architecture/codeforge-family.md  # Amendment 9 — family roster 3→2 + mermaid node 제거
  - skills/story-epic-flow-preflight/SKILL.md  # Amendment 13 — Epic-flow child-transition point 자율 진행 norm PRIMARY local annotation (D1, AC-1/AC-2)
  - hooks/hooks.json  # Amendment 13 — UserPromptSubmit 배열 5번째 entry append (D2)
  - hooks/story-transition-autonomy-reminder  # Amendment 13 — D2 신규 sibling hook (bash dispatcher, skip-offer-reminder 동형)
  - hooks/story-transition-autonomy-reminder.py  # Amendment 13 — D2 hook body (self-contained stdlib, UserPromptSubmit 예방 reminder)
  - hooks/pretooluse-agent-spawn-gate  # Amendment 13 — D2 PreToolUse(Agent) additionalContext 전환 reminder inject (autonomous 창)
  - docs/consumer-guide.md  # Amendment 16 — §7.6 consumer 전파 cross-ref anchor (session-swap controlled-path 상속, 확장-only)
  - hooks/session-swap-handoff-reminder  # Amendment 16 — Phase 2 forward-ref: 신규 sibling hook bash dispatcher (story-transition-autonomy-reminder 동형, 본 Phase 1 미생성)
  - hooks/session-swap-handoff-reminder.py  # Amendment 16 — Phase 2 forward-ref: hook body self-contained stdlib (UserPromptSubmit 예방 reminder, STATIC no-PII, 본 Phase 1 미생성)
is_transitional: false
mechanical_enforcement_actions:
  - action: dialog-fidelity-effect
    status: sunsetted  # Amendment 9 (CFP-2236) — DialogFidelityAgent sunset 동반. measurement subject (DialogFidelityAgent) 폐지로 metric 무의미화. status 변경 (registry entry 제거보다 보수 — historical record).
    progress_note: "[SUNSETTED Amendment 9 / CFP-2236] DialogFidelityAgent 폐지로 본 effectiveness measurement action 무의미화 (측정 대상 부재). Phase 2 carrier (dialog-fidelity-measurement.yml + check-dialog-fidelity-effect.sh + lib .py) 실 wiring 0 = cost_vs_effect_zero sunset evidence 의 일부. 원 Phase 1 (CFP-833) = registry entry skeleton + ADR-071 Amendment 3 + 본문 §결정 14 (historical, carrier-preserved). evidence-checks-registry dialog-fidelity-effect entry 실 cleanup = 별도 follow-up (본 doc-only fast-path scope 외)."
    target_section: §결정 14
  - action: codename-glossary-lookup
    status: deferred-followup
    progress_note: "Phase 1 (CFP-1764 Story-1, 본 Amendment 8) = §결정 19 신설 + docs/wording-dictionary.md 카테고리 (c) SSOT codify (closed 15 codename 첫 batch + ratchet extensibility) + skill SKILL.md cross-ref + CLAUDE.md cross-ref. Phase 2 carrier (CFP-1764 Story-2 — #797 unblock) = scripts/check-codename-glossary-lookup.sh PR diff scan + templates/github-workflows/codename-glossary-lookup.yml + .github/workflows self-app byte-identical + evidence-checks-registry-v1 23번째 warning entry + label-registry-v2 v2.37 → v2.38 (`hotfix-bypass:codename-glossary-lookup` 75번째 family member). warning tier — turn-final hook 부재 platform 한계 (lint-time post-write detection only, runtime mid-turn block 불가)"
    target_section: §결정 19
# Wave 5 = cognitive + persistence layer. Amendment 3 (CFP-833) = effectiveness measurement layer (additive — Layer 1-4 + auxiliary 보존).
# Layer 1 mechanical lint (preamble presence check) = 별도 follow-up CFP 분리 (Story §1 verbatim).
# 본 ADR effective 후 신설 evidence-enforceable entry 가 follow-up CFP carrier 에서 추가될 때
# mechanical_enforcement_actions[] 갱신 + Amendment 발의 (강화 방향만 — ADR-058 §결정 5 / ADR-064 §결정 7
# top-down ratchet 정합).
---

# ADR-071: Orchestrator-user dialog convergence — frame mode + 4 layer 검증 + cross-Story 영속 incidents file

## 상태

Accepted (2026-05-14 KST, CFP-612 carrier). `is_transitional: false` — 영구 정책 (governance carrier, ADR-064 / ADR-058 self carrier 패턴 정합).

## 본질 선언 (Wave 5 핵심)

> **Orchestrator 가 사용자와 대화할 때, mechanical rule 추종이 아니라 진짜 수렴 대화에 참여하도록 codeforge SSOT 를 영구적으로 바꾸는 변화.**

위 본질 선언 (CFP-612 사용자 directive verbatim) 이 본 ADR 의 **anchor**. 본 ADR 의 모든 §결정 (frame mode / 4 layer / sub-mechanism / Layer 4 영속 file) 은 본질을 보조하는 **scaffolding** — mechanism 만 codify 하고 본질을 놓치면 가설 E (mechanical 규칙 자체 한계) 의 self-defeating trap. 본 anchor 가 §결정 1 보다 먼저 배치된 이유 = mechanism 우선 reading risk 회피 forcing function (CFP-612 RequirementsPL §4.2.3 경고 힌트 1번 정합).

## 컨텍스트

본 ADR 의 동인은 CFP-612 §1 verbatim "관찰된 vulnerability 4 종 + 심층 원인 가설 5 종" — 기존 soft 안전망 (memory entry / ADR-064 § "결정 제시" 5 룰) 의 mechanical enforcement 부재. 4 vulnerability:

1. 식별자 (ADR / CFP / 영문 약어) 사전 요약 없이 사용자에게 던지는 패턴
2. subagent 결과를 abstract packet 형태로 보고 → 사용자가 큰 그림 잡기 어려움
3. 가치 판단 영역에서 derived default 단독 선언하고 진행
4. 한 번 지적 받은 패턴이 다음 turn 에 반복되는 경향

5 심층 원인 가설 (서로 겹침): (A) 입력 context 의 중력 — codeforge 내부 vocabulary 비중 / (B) 두 역할 (codeforge 운영 + 사용자 대화) 미분리 / (C) 사용자 지식 경계 모델 부재 / (D) 진행감의 비용 인식 / (E) **Mechanical 규칙 자체 한계** — 외형 검사 규칙이 본래 의도와 반대로 작동 가능 (메타 경고).

선행 SSOT 정합:

- [ADR-064](ADR-064-decision-principle-mandate.md) — `결정 제시` 5 룰 (derived default / 옵션 dump 금지 / 식별자 사전 요약 / brevity / AskUserQuestion 범위) 의 **mechanical version 승격 + scope 확장** carrier. proposing-time 만 → 전 turn 적용. ADR-064 §결정 7 top-down ratchet 정합 (강화 방향 only).
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — `is_transitional: false` 영구 정책 + `## 해소 기준` "N/A — permanent policy" 1줄 패턴 정합.
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) — 본 ADR 신설 = CLAUDE.md 의미 변경 = plugin.json MINOR bump = 3-file atomic invariant 발화.
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) — Phase 1 산출물 7-item mechanical sync self-check 적용 (link target Phase 분배 / MANIFEST.yaml 갱신 NA declare / section-ownership row append).
- [ADR-052 Amendment 1](ADR-052-codex-proactive-check-touchpoints.md) — touchpoint #4 (RequirementsPL §1-§6 완료 직후) multi-round debate 격상. 본 Story §2-§6 가 첫 사례.
- [ADR-070](ADR-070-codex-verify-before-trust.md) — fact-check marker 4 + reverse-explicit `[verification-out-of-scope]` 1 종 verify-before-trust source.
- [ADR-059](ADR-059-debate-protocol-v1.md) — agent ↔ agent debate domain. 본 ADR 은 Orchestrator ↔ user domain — **direct schema mapping 부적합** (CFP-582 의 3 marker pattern 은 debate transcript verification schema, turn-by-turn user dialog 에 fit 안 함). Conceptual cross-ref only — schema 재사용 절대 금지.
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — inline whitelist 4-entry 의 1번 entry (사용자 dialog) 안 cognitive layer 강화. ADR-039 위반 아님 (inline whitelist scope 안 cognitive 보강).
- [ADR-040 Amendment 3](ADR-040-worktree-convention.md) — governance category ADR 의 `mechanical_enforcement_actions[]` frontmatter 의무. Wave 5 = cognitive + persistence layer only, Layer 1 mechanical lint 별도 follow-up CFP — actions list `[]` empty + retroactive 면제 표시 (§결정 7.C 정합).

## 결정

### §결정 1 — 사용자 대화 모드 frame (frame mode 의무)

Orchestrator 가 사용자에게 메시지를 발화하는 turn (= ADR-039 inline whitelist 1번 entry = 사용자 dialog turn) 시 **다른 사고 모드 진입 의식**. 본 frame mode 진입은 매 user-facing turn 의 의무. mechanism 만 적용하고 frame mode 진입 의식을 놓치면 본 ADR 본질 anchor 가 충족되지 못함.

**thinking 절차 4 step** (CFP-612 §1 verbatim "후보 4 — 사용자 대화 모드 진입 의식 (frame, 후보 1·2·3 위에)" 4 sub-bullet 정합):

1. **codeforge 내부 어휘 "내부 메모" 분류 격리** — Orchestrator 입력 context 의 codeforge vocabulary (ADR-NNN / CFP-NNN / lane plugin name / hook name / inter-plugin contract name 등) 를 "내부 메모" 영역으로 분류. 사용자 발화 본문에 직접 등장 금지 (식별자 인용 시 사전 요약 의무 — ADR-064 §결정 3 룰 3 정합).
2. **사용자 지금까지 무엇 알고 있는지 정리** — 사용자 mental model 추정. 사용자가 이미 알고 있는 사항 (이전 turn 발화 기준) 과 미공개 컨텍스트 분리.
3. **사용자 이 turn 무엇 답·결정해야 하는지 한 문장** — 본 turn 의 사용자 입장 action item 1 문장 정리. 사용자가 답해야 할 것이 한 문장으로 명확하지 않으면 본 step 미완.
4. **위 셋 바탕으로 메시지 작성** — step 1 (격리) + step 2 (사용자 지식) + step 3 (turn 결정) 의 통합 위에 메시지 본문 작성.

frame mode 진입 marker 형식 (visible vs hidden cognitive layer) = playbook §3.14 본문 결정 영역 (본 ADR scope = 의무 declare 까지).

### §결정 2 — frame mode 안 세부 규칙 3 종 (후보 1·2·3 흡수)

frame mode 진입 후 적용되는 세부 룰. CFP-612 §1 verbatim "후보 1·2·3" 흡수.

**(a) 후보 1 — 메시지 보내기 직전 self-check 3 문항**:
1. 사용자가 답해야 할 것이 한 문장으로 명확한가
2. 비-codeforge 맥락 사람이 이해 가능한가
3. 답하는 데 필요한 배경 (왜 / trade-off / 걸려있는 것) 충분한가

길이 제약 없음 (3 문항 모두 PASS 후 메시지 발화 의무).

**(b) 후보 2 — 사실/가치 분리, 모호 시 진행 기본 (ask-trigger 3종 한정 — §결정 20 redirect)**:
- 사실 판단 → derived default 적용 (ADR-064 §결정 3 룰 1 정합)
- 가치 판단 (ask-trigger ② 해당 — 진짜 가치 trade-off·default 비자명) → explicit 사용자 확인 (`AskUserQuestion` 발화, ADR-064 §결정 3 룰 5 정합)
- 모호 시(ask-trigger 미해당) → derived default 적용 + 진행 + 1줄 정정 초대. AskUserQuestion 은 ask-trigger 3종(① 요구 애매 / ② 진짜 가치 trade-off·default 비자명 / ③ 비가역·고비용)일 때만 — **safe-direction default-to-ask 폐기, §결정 20 redirect**

memory entry `feedback_question_quality` 의 normative 승격 carrier (§결정 8 mapping 표 참조).

**(c) 후보 3 — sub-agent 결과의 사용자용 평이 번역**:
- raw packet 그대로 노출 금지
- codeforge 내부 용어 평이한 한글로 번역
- **3 줄 제약 명시적 거부** — 길이 자유
- "왜 / trade-off / 걸려있는 것" 배경 포함
- 원본 packet 은 사용자 요청 시 별도 제공

### §결정 3 — 4 layer 검증 (모두 도입)

frame mode + §결정 2 세부 룰을 보조하는 4 검증 layer. CFP-612 §1 verbatim "Layer 1 / 2 / 3 / 4" 정합.

| Layer | 동작 | 발화 위치 |
|---|---|---|
| **Layer 1 — 가시적 preamble** | 메시지 맨 위 "지금 답해주실 것" 1 문장 가시 | 매 user-facing turn 의 메시지 맨 윗줄. trivial turn (E12) 면제 + turn-shape edge 분기 (E9 streaming / E10 tool-call-only / E11 AskUserQuestion popup) 적용. 분기 derived default = playbook §3.14 본문 "Turn-shape derived defaults" 표 결정 영역. **mechanical lint 별도 follow-up CFP** — 본 Wave 5 scope 외 |
| **Layer 2 — 자기 declare** | turn 끝 "주의한 가설" 1 줄 declare (보조 신호) | 매 user-facing turn 의 메시지 맨 아랫줄. trivial turn (E12) + E10 tool-call-only + E11 popup turn 면제. E9 streaming = final flush 시 적용. derived default = playbook §3.14 |
| **Layer 3 — keyword "추상" 즉시 halt** | 사용자 메시지 본문 안 "추상" 한글 token 등장 시 즉시 halt + 재작성 의무 | 사용자 발화 token detection 시점. Hanja form ("抽象") 면제 (CLAUDE.md §1 한자 금지 정책 정합). stem match (예: "추상적" / "추상화") = 적용. **모든 turn-shape edge (E9-E12) 에서 active** — popup option_text 안 "추상" 등장 가능. playbook §3.14 본문이 stem vs exact match 결정 영역 |
| **Layer 4 — 누적 detection** | N=1 즉시 halt (같은 양상 다음 turn 재발 시) + M=5 max threshold 사용자 escalation (`AskUserQuestion` 발화) + 누적 file 영속 | `docs/orchestrator-communication-incidents.md` (cross-Story append-only). **모든 turn-shape edge (E9-E12) 에서 active** — 단 E10 tool-call-only turn 자체는 incident 분류 외 (no user-facing prose = pattern detection 영역 외). §결정 6 참조 |

**Turn-shape edge derived default (E9 / E10 / E11) cross-ref**: 본 ADR §결정 10 (scope out) 정합 — 4 layer × 4 turn-shape edge 의 정량 default matrix 는 **playbook §3.14 "Turn-shape derived defaults" 표 결정 영역**. 본 ADR §결정 3 안 mapping 만 명시 (cross-ref boundary 보존). E10 tool-call-only 정량 정의 (prose 0 줄 + cosmetic 1-줄 미만) + E11 popup turn Layer 2 면제 사유 (popup 본문 자체 declare semantic 충당) 도 playbook 결정 영역. RequirementsPL §5.3 E9-E12 의 `[fact-check-pending]` marker 가 본 FIX-1 으로 모두 resolved.

**신규 5번째 cognitive layer 신설 금지 invariant** (Amendment 9 / CFP-2236 re-home from §12.3 — §결정 12 Sunsetted 시 dangling 회피): 위 Layer 1-4 cognitive enum 은 **closed enumeration**. 신규 5번째 cognitive layer 신설 = 별도 ADR Amendment 의무 (강화 방향 ratchet 정합). mechanism 추가 (예: 외부 verifier — 구 §결정 12, mid-turn glossary — §결정 19) 는 cognitive layer count 변경 아님 (mechanism ≠ cognitive layer). pattern_dimension 4 차원 enum (§결정 4) closed 와 짝 invariant. FeasibilityAgent 보존 명제 SSOT — 본 invariant 는 DialogFidelity sunset 과 무관하게 active (verifier 제거 = mechanism 제거, cognitive layer count 불변).

### §결정 4 — Sub-mechanism 2 종 (수렴 보장)

CFP-612 §1 verbatim "Sub-mechanism" 정합. 4 layer 가 detect 만 하고 수렴 보장 못함 → 본 sub-mechanism 이 수렴 forcing function.

**Sub-mechanism 1 — 매 halt 후 재작성 시 "이전과 다르게 한 점" 1 줄 명시 의무**: Layer 3 또는 Layer 4 N=1 halt 후 재작성 메시지의 맨 아랫줄 (Layer 2 declare 와 별도 줄) 에 "이전과 다르게 한 점:" prefix + 1 줄 본문. 단순 표현 다듬기 (예: 어휘 변경 / 문장 길이 압축) 이 아닌 **차원 전환** 의무.

**Sub-mechanism 2 — 같은 양상 재발 시 다른 차원 전환 의무**: Layer 4 누적 file 에 동일 양상 row count ≥ 2 시점 (즉 같은 양상이 한 번 재발 시점) 부터 단순 표현 다듬기 금지. **4 차원 enum** 중 다른 차원으로 강제 전환:

| 차원 | 의미 | 전환 예시 |
|---|---|---|
| **표현** | 어휘 / 문장 길이 / 구조 변경 | "ADR-064 §결정 3" → "결정 제시 5 룰" |
| **결정 구조** | 옵션 제시 방식 / derived default 적용 / AskUserQuestion 형식 | numbered list → 권장 1 + 대안 1 (ADR-064 §결정 3 룰 4 정합) |
| **보고 형식** | sub-agent 결과 packet 표시 / 평이 번역 / 길이 | raw JSON → 평이 한글 (3 줄 제약 거부) |
| **질문 자체** | 어떤 결정을 사용자에게 묻는지 자체 변경 | "방향 X / Y 중 어느 것" → "본 결정의 user value 우선순위는?" |

차원 전환 의무 = 같은 양상 재발 사이클을 break 하는 forcing function. memory `feedback_explain_before_ask` 의 normative 승격 carrier (§결정 8 mapping 표 참조).

**4 차원 enum exhaustiveness declare**: 본 4 차원 (표현 / 결정 구조 / 보고 형식 / 질문 자체) 은 **closed enum**. 5번째 차원 추가는 별도 ADR Amendment 의무 (강화 방향 ratchet 정합 단 사용자 burden 변화 영역 — pattern_dimension column 분류 schema 변경). Layer 4 영속 file `pattern_dimension` column 의 valid value enum 도 본 4 종으로 한정 (schema 안정성 보장).

### §결정 5 — 사실/가치 판단 분류 결정 트리 (§결정 2 (b) 확장)

> **[REDIRECT — Amendment 10 / CFP-2371, 2026-06-19 KST]** 아래 결정 트리의 `AMBIGUOUS → 가치 측 분류(safe direction) → AskUserQuestion` 룰은 **§결정 20 (ask-trigger 3종 한정)** 으로 redirect 됨 (over-asking 안전편향 제거). 현행 룰 = 모호 포함 ask-trigger 미해당 전부 derived default 적용 + 진행 + 1줄 정정 초대 (멈춰 묻는 건 ask-trigger 3종 — ① 요구 애매 ② 진짜 가치 trade-off ③ 비가역·고비용 — 일 때만). 아래 본문 = historical record (이력 보존, 통째 삭제 아님). 현행 SSOT = §결정 20.

§결정 2 (b) 의 mechanical 분류 절차. Orchestrator 매 turn 의 결정 후보에 적용:

```
결정 후보 발화 직전:
  is_factual?
    YES → derived default 적용 (단 derived default 가 추론 가능한 컨텍스트 보유 시)
                   ↓
                  declare default + 결과 보고 + 사용자 정정 의무
    NO (가치 판단 영역) → AskUserQuestion 발화 의무 (ADR-064 §결정 3 룰 5 정합)
    AMBIGUOUS → 가치 측 분류 (safe direction)
                   ↓
                  AskUserQuestion 발화 의무
```

**사실 판단 예시**: 파일 존재 확인 / `wc -l` 결과 / `git log` 출력 / SHA 식별자 / `grep` 결과 (모두 derived default 적용 가능 영역).

**가치 판단 예시**: 사용자 선호 (UX / 보고 길이 / 식별자 인용 빈도) / 정책 강화 방향 (warning → blocking) / scope 결정 (1 CFP 안 vs 분리) / brainstorm 후 채택안 결정 (모두 AskUserQuestion 의무 영역).

**모호 영역 예시**: derived default 가 컨텍스트로 추론 가능 but 사용자 explicit 발화 없음 + 결과가 future 작업에 영향 큼 — 가치 측 분류 (사용자 확인 후 진행).

### §결정 6 — Layer 4 영속 file 영역 + schema

cross-Story append-only file (wrapper repo 레벨 단일 file). owner = Orchestrator 단독 monopoly (FIX Ledger / Git Ops Log 패턴 유사).

**file path**: `docs/orchestrator-communication-incidents.md` (wrapper repo). consumer 측은 자기 repo 의 `docs/orchestrator-communication-incidents.md` (별도 lifecycle, consumer-guide §1 cross-ref 의무).

**initial content** (CL-3 derived default — Phase 1 commit 시 본 ADR 동반 신설):

```markdown
---
title: Orchestrator Communication Incidents (Layer 4 누적 file)
status: Active
category: governance
date: 2026-05-14
carrier_story: CFP-612
related_adrs:
  - ADR-071
schema_version: "1.0"
---

# Orchestrator Communication Incidents

> Layer 4 누적 detection file (ADR-071 §결정 6).
> owner = Orchestrator 단독 monopoly. append-only. cross-Story 영속 (Story 종료 시 reset 없음).
> M=5 max threshold 누적 시 사용자 escalation (`AskUserQuestion` 발화).
> reset 정책: manual archive only (yearly file rotate 또는 별 row delineator marker).

## Schema

| Column | 의미 |
|---|---|
| iter | 누적 incident sequential id (전체 file 기준) |
| timestamp | KST ISO8601 |
| story_key | 발생 시점 active Story KEY (cross-Story 추적) |
| pattern_dimension | 4 차원 enum (표현 / 결정 구조 / 보고 형식 / 질문 자체) |
| pattern_summary | 어떤 양상이 detect 됐는지 1 줄 |
| trigger | Layer 3 (사용자 "추상" keyword) / Layer 4 N=1 (같은 양상 재발) / Layer 4 M=5 (escalation) |
| different_dimension_after_halt | Sub-mechanism 1 — "이전과 다르게 한 점" 1 줄 |
| escalation_outcome | M=5 escalation 시 사용자 답변 요약 (`AskUserQuestion` outcome) — N=1 / Layer 3 시 비어있음 |

## Incidents

| iter | timestamp | story_key | pattern_dimension | pattern_summary | trigger | different_dimension_after_halt | escalation_outcome |
|------|-----------|-----------|-------------------|-----------------|---------|-------------------------------|--------------------|

<!-- 비어있는 table — Orchestrator 가 incident detect 시 row append -->
```

**lifecycle 룰**:
- append-only (Orchestrator 단독)
- Story 종료 시 reset 없음 (cross-Story 영속)
- M=5 카운터 = lifetime 영속 (manual reset 만 허용 — 사용자 explicit reset request 시)
- pattern_dimension 분류는 §결정 4 4 차원 enum 만 허용
- 사용자 escalation 후 다음 incident = pattern_dimension 강제 전환 (§결정 4 sub-mechanism 2 정합)

### §결정 7 — Layer 3 keyword "추상" semantics

CFP-612 §1 verbatim "Layer 3 — keyword '추상'" + RequirementsPL §5.3 E1·E2 derived default 정합.

- **한글 token "추상"** 등장 시 trigger (substring stem match — "추상" / "추상적" / "추상화" 등 모두 trigger)
- **Hanja form "抽象"** 면제 (CLAUDE.md §1 한자 금지 정책 정합 — 한자 형태 자체는 codeforge 안에서 발화되지 않음)
- **영문 alias** ("abstract" / "abstraction") = trigger 아님 (한글 token 만 anchor)
- **false positive 양 증가 risk** 인지 — stem match 가 false positive 발생 가능 영역 (예: "추상 미술" 같은 도메인 어휘) — playbook §3.14 본문이 false positive 처리 결정 영역
- **keyword 확장 ratchet 의무** — Layer 3 trigger keyword 영역 확장 (예: "두루뭉술" / "막연히" 추가) 시 별도 ADR Amendment 의무 (사용자 burden 변화 영역 — Layer 3 가 사용자 발화 token detection 기반이므로 keyword 추가 = 사용자 표현 자유도 축소). ADR-058 §결정 5 sunset_justification 불요 (강화 방향 ratchet 정합) 단 별도 CFP carrier + Story §1 사용자 explicit 승인 의무.

### §결정 8 — 3 memory entry normative 승격 mapping 표

CFP-612 §1 verbatim "기존 memory entry normative 승격" + AC-12 measurement column 정합:

| memory entry | 정책 위치 SSOT 이전 | unchanged scope |
|---|---|---|
| `feedback_explain_before_ask` | **playbook §3.14** (frame mode 본문 SSOT) + 본 ADR §결정 1 step 4 (메시지 작성 시 식별자 사전 요약 의무) + §결정 4 sub-mechanism 1 (이전과 다르게 한 점) | — |
| `feedback_question_quality` | **playbook §3.14** (frame mode 본문 SSOT) + 본 ADR §결정 2 (b) (사실/가치 분리) + §결정 5 (분류 결정 트리) | — |
| `feedback_subagent_driven_auto_select` | **변경 없음** — playbook §3.0.5 기존 정책 유지 (Subagent-Driven 자동 선택) | codeforge wrapper side SSOT 변경 0 (사용자 personal memory side 의 entry 자체는 영향 받지 않음 — 사용자 영역, codeforge wrapper scope 외) |

**승격 시점**: 본 Story Phase 2 PR merge 시점 (effective 단계 완료 — CLAUDE.md cross-ref + playbook §3.14 + Layer 4 file 동반 반영). ADR-071 Accepted 직후는 effective 단계 미완. Phase 2 PR retro (PMOAgent ADR-045 mandate) 의제로 사용자 personal memory entry 삭제 제안 — 사용자 결정 영역 (codeforge wrapper scope 외).

### §결정 9 — CFP-582 conceptual cross-ref + schema fit 부적합 declare

[ADR-059 Amendment 2](ADR-059-debate-protocol-v1.md) + CFP-582 = **agent ↔ agent debate domain**. 본 ADR-071 = **Orchestrator ↔ user dialog domain**. 두 도메인 의 conceptual common ground = "수렴 dialog 가 본질" 1 점. 단:

- CFP-582 의 3 marker pattern (`counterargument_present` / `alternative_proposed` / `debate_purpose_statement_present`) = **debate transcript verification schema** — multi-round adversarial debate 의 convergence_quality_invariant 검증용.
- 본 ADR-071 = **turn-by-turn Orchestrator-user dialog** — single-turn cognitive frame + cross-Story 누적 detection.

**Schema fit**: CFP-582 의 3 marker = 라운드 단위 transcript 검증, 본 ADR-071 = turn 단위 메시지 검증. **직접 schema mapping 부적합**. ADR-071 §결정 1-7 의 frame mode + 4 layer + sub-mechanism 어느 항목도 CFP-582 의 3 marker schema 를 import 하지 않는다. CFP-582 의 본질 (수렴 dialog) 만 conceptual cross-ref. **schema 재사용 절대 금지**.

**`anchor_recurrence_count` reset 의미 (Wave 5 scope)**: ADR-059 Amendment 1 의 `anchor_recurrence_count` 는 debate 라운드 영역 카운터 — Wave 5 영역에서는 항상 0 (debate 미발동 = 본 Story 의 첫 review = 누적 영역 외). Layer 4 영속 file (`docs/orchestrator-communication-incidents.md`) 의 M=5 lifetime counter 는 `anchor_recurrence_count` 와 다른 차원 (cross-Story 영속 vs single-debate 라운드). 두 카운터 간 mapping 절대 금지.

ADR-059 = lane-agnostic protocol contract — lane 정보를 인자로 받는 일반 schema. 본 ADR-071 = lane 분기 영역 아님 (Orchestrator-user turn 자체는 모든 lane 진입 직전·직후·중간에 발생 — lane-agnostic 도 아니고 single-lane 도 아닌 별도 layer). 본 declare 가 미래 CodeReview / SecurityTest lane 의 debate 확장 (deferred CFP-C scope) 와 본 ADR 의 sibling 발의 가능성을 분리.

### §결정 10 — Scope out (별도 follow-up CFP)

CFP-612 §1 verbatim "Scope 가 아닌 것" + RequirementsPL §5.4 정합:

- **Layer 1 preamble mechanical lint** — 별도 follow-up CFP 분리 (본 Wave 5 = cognitive + persistence layer 만). 본 ADR effective 후 evidence-enforceable warning-tier entry 신설 carrier 가 follow-up CFP.
- **agent ↔ agent debate domain** — CFP-582 cover 완료, 본 ADR scope 외.
- **코드 품질 / 보안 / 성능** — 본 Wave 5 = cognitive + persistence layer SSOT only.
- **사용자 personal memory entry 자체 삭제** — 사용자 영역, codeforge wrapper scope 외. PMOAgent retro 의제로 제안만.
- **consumer overlay 영역 customization** — consumer overlay 가 정책 축소 불허 (CLAUDE.md L155-156 정합) — Wave 5 정책 자체는 wrapper-level normative.
- **debate-protocol-v1 의 3 marker import** — §결정 9 verbatim "직접 mapping 부적합", schema 직접 채택 절대 금지.
- **frame mode 진입 marker 의 visible vs hidden 형식 결정** — playbook §3.14 본문 결정 영역.
- **Layer 3 stem match vs exact match 결정** — playbook §3.14 본문 결정 영역.
- **Layer 4 file rotate / archive 정책** — playbook §3.14 본문 결정 영역.

### §결정 11 — ADR-039 inline whitelist 1번 entry cognitive 강화 declare

[ADR-039 §결정 7](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) inline whitelist 4-entry 의 1번 entry (사용자 dialog) 에 frame mode + 4 layer 의 추가 cognitive layer 부착 = **ADR-039 위반 아님**. inline whitelist scope 안 cognitive 보강 (file write / Bash 실행 / Agent spawn 분류 영역 외).

본 declare = ArchitectAgent over-engineer 회피 forcing function (RequirementsPL §4.2.4 ADR-039 충돌 후보 → 해소 경로 명시).

## 결과

### Phase 1 산출물

본 ADR effective 후 매 codeforge session 의 Orchestrator 가 user-facing turn 시 frame mode 진입 의무. Phase 1 산출물 (본 ADR + playbook §3.14 + 신규 skill `codeforge:user-dialog-mode` + Layer 4 file 신설 + CLAUDE.md cross-ref + plugin.json MINOR bump + marketplace sync) 동시 발효.

### measurable signal

본 ADR `is_transitional: false` 영구 정책 + ADR-058 `## 해소 기준` "N/A — permanent policy". 본 ADR 의 effective signal:

- Layer 4 file (`docs/orchestrator-communication-incidents.md`) row count
- M=5 escalation 발생 빈도 (`AskUserQuestion` 발화 count)
- §결정 4 sub-mechanism 2 차원 전환 횟수 (pattern_dimension column distinct count)
- PMOAgent retro 의 user feedback (수렴 dialog 체감 / 식별자 사전 요약 누락 빈도)

### Follow-up scope

- **Layer 1 preamble mechanical lint** = 별도 follow-up CFP (Wave 5 §결정 10 scope out)
- **frame mode marker 형식** = playbook §3.14 본문 결정 영역
- **Layer 3 stem vs exact match** = playbook §3.14 본문 결정 영역
- **Layer 4 file rotate / archive** = playbook §3.14 본문 결정 영역

## §결정 12. DialogFidelityAgent external verifier auxiliary layer (Amendment 1, CFP-777)

> **[SUNSETTED — Amendment 9 / CFP-2236, 2026-06-14 KST]** DialogFidelityAgent 전면 폐지. 본 §결정 의 DialogFidelity mandate 는 active 아님 (sunset_justification = Amendment 9 3축 evidence: dead_mandate / verification_ground_redundancy / cost_vs_effect_zero). 같은 anchor 의 Codex TP#2/TP#3 (mandatory P0/P1 inline FIX, ADR-052) + ADR-064 §결정 9 Q-3check (Orchestrator self-check) 가 검증 ground 보존. 본문 = historical record carrier-preserved. **§12.3 "신규 5번째 cognitive layer 신설 금지 invariant"** = §결정 3 (Layer 1-4 enum) 으로 re-home (active 보존, 삭제 아님 — FeasibilityAgent §4.2 보존 명제 #2 SSOT).

### 12.1 결정 요약

Layer 1-4 = ADR-071 **§결정 3** 의 4-layer cognitive enum (preamble 의무 / declare 의무 / "추상" halt / N=1+M=5 incidents append) 골격 **보존 invariant**.

별개 §결정 family 분리 (5-element squash 회피):
- frame mode 4 step = ADR-071 **§결정 1** (4-step protocol — 사용자 요건 파악 / mental model 추정 / 1-sentence frame / forcing-function declare)
- sub-mechanism 2 종 = ADR-071 **§결정 4** (turn-final hook 부재 → cognitive substitute)
- Layer 4 영속 file = ADR-071 **§결정 6** (cross-Story incidents.md ledger Orchestrator monopoly)

DialogFidelityAgent = **additive auxiliary layer**, 신규 **5번째 cognitive layer 신설 금지** (§결정 3 의 4-layer cognitive enum scope 만, 다른 §결정 family 와 무관).

발화 entity (Orchestrator) 와 검증 entity (DialogFidelityAgent) **분리** — ADR-071 anchor 단락 (line 57) 가설 E (mechanism 만 codify, 본질 미codify 한계 — self-defeating trap) 다층 방어 채널 (mechanism scaffolding 강화 + 본질 anchor 동시 보존).

### 12.2 Mandate scope (read-only inspection only)

verifier-narrower-than-generator 패턴 강제:

| 항목 | scope |
|---|---|
| input | (a) 세션 개시 요건 (Story §1 immutable verbatim) + (b) 누적 결정/제약 ledger (Layer 4 incidents file verbatim row) + (c) 현 Orchestrator turn 출력 (SHA-256 hash-pinned verbatim) |
| output | `verify_result: enum<fidelity_ok \| drift_detected \| ledger_gap>` + `evidence_path[]` (non-empty when != ledger_gap) + `incident_row_match: {row_id, layer, criterion}` + `correction_action_hint: enum<rescan_ledger \| escalate_user \| self_correct \| no_action> \| null` |
| 추론 재실행 | **금지** (검증자 역설 회피, generator 역할 침범 금지) |

### 12.3 Layer 1-4 보존 invariant (ADR-071 §결정 3 의 4-layer cognitive enum scope)

| Layer (§결정 3 cognitive enum) | AS-IS | 본 Amendment 후 |
|---|---|---|
| Layer 1 (preamble 의무) | mechanical lint deferred (§결정 10 정합) | 보존, 무변경 |
| Layer 2 (declare 의무) | behavioral directive | 보존, 무변경 |
| Layer 3 ("추상" halt) | behavioral directive | 보존, 무변경 |
| Layer 4 (N=1 + M=5 incidents append) | Orchestrator monopoly write (§결정 6) | 보존, 무변경. DialogFidelityAgent read-only inspection only |

**신규 5번째 cognitive layer 신설 금지 invariant** (§결정 3 enum scope 만, 다른 §결정 family 와 무관): pattern_dimension 4 차원 enum closed (보고 형식 / 질문 자체 / sub-mechanism 2종 — §결정 4 carrier) 보존. verifier 도입 = mechanism (verification entity) 추가, §결정 3 cognitive layer count 변경 아님.

### 12.4 ADR-071 anchor 단락 line 57 가설 E 다층 방어 채널

`[verified — git show origin/main:docs/adr/ADR-071-orchestrator-user-dialog-convergence.md line 57 anchor 단락 verbatim]` ADR-071 anchor 단락 본문:
> "본 ADR 의 모든 §결정 ... 은 본질을 보조하는 scaffolding — mechanism 만 codify 하고 본질을 놓치면 가설 E (mechanical 규칙 자체 한계) 의 self-defeating trap"

본질 anchor = 발화 entity ≠ 검증 entity 분리 (Orchestrator self-check 만으로는 mechanical 규칙이 본질을 놓침). 가설 E location = **§결정 11 본문이 아닌 anchor 단락 line 57** (§결정 family 보다 상위 framing context).

**다층 방어 메커니즘**: 발화 entity (Orchestrator) ≠ 검증 entity (DialogFidelityAgent codeforge-pmo agent). mechanism scaffolding 강화 + 본질 anchor (entity 분리) 동시 보존. 4-layer mechanical defense (Change Plan CFP-777 §7.3):

| Layer | mitigation |
|---|---|
| M1 | `tools:` field read-only subset only `[Read, Grep, Glob, ToolSearch]` — Write/Edit/Bash/SendMessage/Agent 차단 (input integrity input scope 제한) |
| M2 | output schema closed enum (verify_result 3-value `fidelity_ok \| drift_detected \| ledger_gap` + correction_action_hint 4-value `rescan_ledger \| escalate_user \| self_correct \| no_action` + `null`) — narrative free-form 차단 (generator 영역 reasoning 재실행 차단 = M1 + M2 combined forcing function) |
| M3 | input contract SHA-256 hash-pinned (current_output_hash) — Orchestrator turn output verbatim 이 spawn 시점과 동일한지 확인 (input integrity verification only, reasoning re-execution 차단은 M1+M2 combined 위임) |
| ADR-070 §B final safety net | Orchestrator post-verify ground truth direct Read: evidence_path[] direct Read verify 의무, mismatch 시 verdict reject + tally |

### 12.5 Spawn anchor 3종 (ADR-039 §결정 2 inline whitelist 보존)

ADR-039 **§결정 2** Inline whitelist 4-entry (사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report) **보존 invariant**. 매 user-facing turn spawn 금지. (note: base ADR-071 §결정 11 본문이 ADR-039 §결정 7 을 인용한 self-error — 본 Amendment 는 §결정 2 정확 cite 채택.)

선별 anchor 3종:

| anchor | 발동 시점 |
|---|---|
| `post_user_turn` | 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / AskUserQuestion 직전) |
| `pre_architectpl_synthesis` | ArchitectPL synthesis 완료 직전 (Codex TP#2 augment) |
| `pre_fix_rootcause` | FIX 루프 root cause 판정 직전 (Codex TP#3 augment) |

자동 발동 hook 부재 (turn-final hook unavailable, ADR-039 §결정 9 deferred 영역 정합). Orchestrator 자율 채택 layer (behavioral directive).

### 12.6 Cross-ref (deputy 산출물 통합 anchor)

- **SecurityArch §7.1-§7.6** (Change Plan CFP-777 §7): trust boundary / threat (T1 tampering, T2 silent drift) / mitigation M1/M2/M3 / auth / audit
- **TestContractArch §8** (Change Plan CFP-777 §8): unit AC-U1/U2/U3 / integration 5 baseline incident catch / boundary AC-B1-B4 / stateful §8.5
- **DataMigrationArch §11** (Change Plan CFP-777 §11): 분기 A schema 무변경 / 5 baseline integrity invariants / ADR-079 KST timestamp display 정합
- **OpRiskArch §7.4** (Change Plan CFP-777 §7.4): DR (non-blocking + Story §14 outcome marker) / rate-limit (3-anchor only) / env (env=0 default) / sibling cross-repo (ADR-063 6-file atomic)

### 12.7 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment = **additive ratchet** (Layer 1-4 골격 보존, 검증 mechanism 만 추가). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격.

## §결정 13. DialogFidelityAgent spawn trigger 운영 정의 (Amendment 2, CFP-818)

> **[SUNSETTED — Amendment 9 / CFP-2236, 2026-06-14 KST]** DialogFidelityAgent 전면 폐지. 본 §결정 의 3-anchor spawn trigger mandate (`post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause` + 12 cell 활성 표) 는 active 아님 (sunset_justification = Amendment 9 3축 evidence). 같은 anchor 의 Codex TP#2/TP#3 (mandatory P0/P1 inline FIX, ADR-052) + ADR-064 §결정 9 Q-3check 가 검증 ground 보존. §13.4 ADR-039 inline whitelist 4-entry closed enumeration 보존 invariant + §13.5 Q-3check disjoint scope + §13.6 closed enum 확장 패턴 = DialogFidelity-independent 명제로 보존 (verifier 제거와 무관 active). 본문 = historical record carrier-preserved.

### 13.1 결정 요약

Amendment 1 (§결정 12) 가 도입한 DialogFidelityAgent (cross-cutting read-only verifier, codeforge-pmo) 의 **spawn trigger 운영 정의** + ADR-039 inline whitelist 1번 entry **정합 명문화** + turn-shape edge × 3-anchor **12 cell 활성 표** 신설 + ADR-064 §결정 9 Q-3check **disjoint scope cross-ref**.

Story-2 (CFP-818) 채택 = **spawn-on-marker (closed 3-anchor)** — Anthropic Constitutional AI critique pattern (Bai et al. 2022) selective spawn 패턴 정합 + ADR-052 6 touchpoint precedent (codeforge 내부 precedent — 전수 아닌 6 touchpoint 만 활성) + verifier-narrower-than-generator forcing function (Epic CFP-761 spec § "근거 1" verbatim).

회피 대안:
- **spawn-everywhere** (전수 spawn, 매 user-facing turn) — cover 100% 단 30x overhead + verifier-narrower-than-generator 위반 (검증 범위 ≥ 생성 범위 시 검증자 역설). 회피.
- **gradient spawn** (사용자 turn 형태별 활성 비율) — 비율 정의 자체 추가 결정 영역 + 12 cell discrete 표 보다 mental model 복잡 + Story-3 effectiveness metric carrier 가 closed enum baseline 측정 후 확장 영역. 회피 (closed 3-enum + 별도 CFP 의무 — §13.6).

본 §결정 13 = additive 강화 (Layer 1-4 보존 + 5번째 cognitive layer 신설 금지 invariant 보존 + Inline whitelist 4-entry 보존 + Q-3check 7 anti-pattern 보존). §결정 12 family 정합 — 새 §결정 family 분리 (5-element squash 회피 패턴 정합).

### 13.2 3-anchor 발화 형태 매핑 표

§결정 12.5 의 3-anchor enum 의 운영 정의 (각 anchor 가 어떤 turn shape 직전 활성):

| anchor | 발동 시점 | 발화 형태 매핑 (UC) | Codex touchpoint dedup |
|---|---|---|---|
| `post_user_turn` | 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / `AskUserQuestion` 직전) | UC-1 (`AskUserQuestion` 발화 직전) / UC-2 (numbered list 또는 dialog format 발화 직전) / Layer 3 "추상" stem detect 직후 | 없음 (Codex 6 touchpoint 와 disjoint) |
| `pre_architectpl_synthesis` | ArchitectPL synthesis 완료 직전 (사용자 보고 발화 직전) | UC-3 (Orchestrator 가 ArchitectPL synthesis 결과 사용자 보고 발화 직전) | **Codex TP#2 (mandatory, [ADR-052](ADR-052-codex-proactive-check-touchpoints.md) Amendment 4) 와 동일 위치** — 양 verifier 활성 (EC-6 dedup) |
| `pre_fix_rootcause` | FIX 루프 root cause 판정 직전 (ArchitectPL 1차 진단 후 최종 판정 직전) | UC-4 (Orchestrator 가 FIX 루프 root cause 판정 직전) | **Codex TP#3 (FIX 2+ 감지 시) 와 동일 위치** — 양 verifier 활성 (EC-5 dedup) |

dedup 패턴 (EC-5/EC-6): 동일 위치 활성 시 — Codex = P0/P1 inline FIX mandatory (TP#2) / single-shot 검토 (TP#3) / DialogFidelityAgent = correction_action_hint 5-enum 권고. Orchestrator 가 양 verdict 통합 (verify-before-trust ADR-070 의무).

### 13.3 turn-shape edge × 3-anchor 12 cell 활성 표

[playbook §3.14 "Turn-shape derived defaults" 표](../orchestrator-playbook.md) 의 E9/E10/E11/E12 edge × 3-anchor cross-product 활성 매핑:

| anchor \ edge | E9 streaming token | E10 tool-call-only | E11 AskUserQuestion popup | E12 trivial answer |
|---|---|---|---|---|
| `post_user_turn` | **final flush 시 활성** (mid-stream spawn 금지 — idempotency) | **면제** (사용자 발화 직접 미발생) | **active** (popup 본문 자체가 dialog convergence anchor — popup option_text/body Layer 3 "추상" detect 영역) | **면제** (cost > benefit, trivial turn 3-criteria AND 충족 시 cognitive overhead 정당화 불가) |
| `pre_architectpl_synthesis` | active (edge-independent — Story 1회 발동, ArchitectPL synthesis 완료 직전 fixed timepoint) | active | active | active |
| `pre_fix_rootcause` | active (edge-independent — FIX 발동 시점 fixed, ADR-067 FIX 3 카운터 범위 안 ≤ 3/Story) | active | active | active |

cell 값 enum: `active` (spawn 의무) / `면제` (spawn 금지) / `final flush 시 활성` (E9 streaming 의 final flush 단계 1회만 spawn — mid-stream 금지).

12 cell 모두 derived default 값 (Story §5.5 OQ-3 채택, 사실 측 분류 — 본 §결정 3 (4 layer) + playbook §3.14 SSOT 정합).

**E11 popup × `post_user_turn` 결정 근거**: popup 본문 자체가 dialog convergence anchor — Layer 1 가시적 preamble (= "AskUserQuestion 으로 답해주실 것: ..." 1 문장, playbook §3.14 E11 derived default) 의 발화가 곧 dialog turn, popup option_text 안 Layer 3 "추상" stem detect 영역 = active 의무.

empirical-source annotation (ADR-068 Amendment 1 I-5 dimensional empirical grounding):
- **latency**: `[hypothesis]` subagent one-shot ~ 2-10 sec (codeforge telemetry 부재 — Story-3 effectiveness metric carrier 영역)
- **cost**: `[hypothesis]` read-only inspection ~ 5-15k input + 0.5-2k output (model tier `inherit` Story-1 [ADR-042 Amendment 6](ADR-042-agent-model-selection-policy.md))
- **count**: `[verified]` max upper bound ≤ 34/Story (`post_user_turn` ≤ 30 — `AskUserQuestion` / numbered list / 추상-detect trigger subset / `pre_architectpl_synthesis` 1 + `pre_fix_rootcause` ≤ 3 — [ADR-067 §결정 3](ADR-067-fix-ledger-implementability-escalation.md) FIX 3 카운터 정합)

### 13.4 ADR-039 Inline whitelist 1번 entry 정합 명문화

[ADR-039 §결정 2](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Inline whitelist 4-entry **closed enumeration** 보존 (5번째 entry 신설 금지 invariant).

DialogFidelityAgent verifier subagent spawn = 1번 entry (사용자 dialog) **scope 안** cognitive 보강:
- 사용자 dialog **본 발화** = inline 유지 (Inline whitelist 1번 entry 원래 mandate)
- 본 발화 **직전/직후** verifier subagent spawn = ADR-039 §결정 1 default subagent spawn 정합 (subagent 형태 자체는 inline 영역 외 — 정상 default 적용)

5번째 entry 신설 X — 새 카테고리 enumeration 추가 아님, 기존 1번 entry 의 "cognitive 보강 채널" 1 문장 명문화. closed enumeration 보존 invariant + 5번째 entry 신설 시 Amendment 의무 invariant 양 보존.

ADR-039 §결정 2 표 row 1 Mechanism rationale 컬럼이 본 정합 1 문장 verbatim 명시 (CFP-818 Phase 1 PR Edit).

### 13.5 ADR-064 §결정 9 Q-3check disjoint scope cross-ref

[ADR-064 §결정 9](ADR-064-decision-principle-mandate.md) Question quality 3-check = **Orchestrator self-check** (proposing-time + stop-time).

DialogFidelityAgent = **외부 verifier** (발화 entity ≠ 검증 entity 분리, self-referential trap 회피 — 본 §결정 12 anchor 단락 가설 E 다층 방어 메커니즘 정합).

disjoint scope — 양자 cross-cutting 보강:

| 영역 | 3-check cover | DialogFidelityAgent cover |
|---|---|---|
| turn-internal cognitive frame (1-option 묻기 / Implementation detail 묻기 / Confirm-of-confirm 등 7 anti-pattern P1-P7) | ✅ | — |
| 누적 결정 ledger drift (Layer 4 영속 file `docs/orchestrator-communication-incidents.md` row 일관성) | — | ✅ |
| 세션 개시 요건 일관성 (Story §1 immutable verbatim vs 현 turn 출력) | — | ✅ |
| 가치 판단 vs 사실 판단 분류 self-check (§결정 9 Question quality 3-check 1번 항목) | ✅ | — |
| derived default 자명성 self-check (§결정 9 Question quality 3-check 2번 항목) | ✅ | — |

양자 동시 활성 (3-check 의 anti-pattern 7종 + DialogFidelityAgent output 4-enum) 이 dialog fidelity 보장 강화 forcing function. ADR-064 §결정 9 단락 말미가 본 disjoint scope 1 단락 verbatim 명시 (CFP-818 Phase 1 PR Edit).

### 13.6 closed enum 확장 시 별도 CFP 의무 codification

3-anchor enum (`post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause`) = **closed enumeration**. 확장 후보 3종 발생 시 (Story §5.4 IA-4 정합):

- `pre_lane_spawn`: 매 lane spawn 직전 verifier dispatch
- `pre_phase_transition`: phase label transition 직전 (요구사항 → 설계 / 설계 → 설계-리뷰 등)
- `pre_pause_decision`: ADR-067 §결정 3 Pause/Resume 결정 직전

→ **별도 CFP 신설 의무** (사용자 burden 변화 영역 — spawn frequency 증가 + ROI 측정 baseline 갱신 의무). ADR-064 §결정 7 top-down ratchet 정합 (강화 방향 only) + ADR-058 §결정 5 sunset_justification 의무 (anchor 축소 시).

본 §13.6 codification = scope creep 차단 forcing function (Story §5.4 IA-4 + §결정 12 5번째 cognitive layer 신설 금지 invariant pattern 정합).

### 13.7 sunset_justification: null (additive ratchet, §결정 12 family 정합)

본 Amendment 2 = **additive 강화** (Layer 1-4 보존 + Inline whitelist 4-entry 보존 + Q-3check 7 anti-pattern 보존 + closed 3-anchor 보존). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§결정 12 family pattern 정합).

## §결정 14. DialogFidelityAgent effectiveness measurement wiring (Amendment 3, CFP-833)

> **[SUNSETTED — Amendment 9 / CFP-2236, 2026-06-14 KST]** DialogFidelityAgent 전면 폐지. 본 §결정 의 effectiveness measurement mandate (incident append-rate delta proxy signal + `dialog-fidelity-effect` registry entry wiring) 는 active 아님 — 측정 대상 (DialogFidelityAgent) 부재로 metric 무의미화. 본 §결정 14 의 measurement deferred-followup 실 wiring 0 = Amendment 9 sunset_justification 의 `cost_vs_effect_zero` 축 직접 evidence. frontmatter `mechanical_enforcement_actions[] dialog-fidelity-effect` action status = sunsetted. 본문 = historical record carrier-preserved.

> Epic CFP-761 Story-3 (마지막 Story — closing-the-loop). carrier: CFP-833, issue https://github.com/mclayer/plugin-codeforge/issues/833. additive 강화 — Layer 1-4 + DialogFidelityAgent auxiliary layer 보존, measurement layer 추가만.

### 14.1 WHY (ADR-058 §결정 3 측정성 self-application)

Story-1 (CFP-777) 이 DialogFidelityAgent 를 신설하고 Story-2 (CFP-818) 가 spawn trigger 를 운영 정의했다. 그러나 **그 verifier 가 실제로 맥락 fidelity 손실을 줄였는지 정량 측정하지 않으면 ADR-071 이 측정 기준 없는 영구 안전망으로 굳는다** (ADR-058 §결정 3 측정성 forcing function 미적용 상태). 본 §결정 14 = ADR-058 의 측정성 mandate 를 DialogFidelityAgent 효과에 wiring 하는 self-application — verifier 자신이 ADR-058 §결정 3 forcing function 의 적용 대상이 된다 (verifier 도 측정 없이 영구화되면 안 됨).

### 14.2 measurement SSOT 분리 (`## 해소 기준` 무변경 invariant)

ADR-071 = `is_transitional: false` permanent governance → `## 해소 기준` = "N/A — permanent policy" **무변경** (permanent governance recursive sunset 회피 invariant — 측정 metric 을 `## 해소 기준` 섹션 자체에 적지 않는다). measurement 실체 = 분리된 2 SSOT:

1. **본 amendment_log Amendment 3** (`sunset_justification: null` 강화 ratchet — Amendment 1/2 family pattern)
2. **`docs/evidence-checks-registry.yaml` `dialog-fidelity-effect` warning-tier entry** (`owner_adr: ADR-071` / `carrier_adr: ADR-060`) = metric 의 mechanical SSOT

ADR 본문 = cross-ref only (precedent `rate-limit-fallback-rate` ↔ ADR-057 §결정 2 sunset gate wiring 동형 — registry entry 가 measurement SSOT, ADR 본문은 reference).

### 14.3 metric 정의 + proxy signal qualification (Codex TP#2 P1 정합)

metric = **incident append-rate delta (proxy signal — not causal effectiveness measure)**. DialogFidelityAgent 도입 (Story-1 merge `577f96f`, 2026-05-17 KST) 전후 Layer 4 incident realtime detect row append rate A-B baseline delta. 정량 3-tuple (metric/who/how) + sample insufficient sentinel + baseline normalization 의 SSOT = `dialog-fidelity-effect` registry entry `description` (Change Plan CFP-833 §3.1 cross-ref).

**proxy 한계 명시 (over-claim 차단 — ADR-058 §결정 3 metric 정직성 정합)**: `before` = Story-0 retroactive backfill marker row / `after` = Story-1 merge 이후 realtime detect row → 두 collection mode 가 상이하므로 delta 는 DialogFidelityAgent 효과뿐 아니라 instrumentation mode change / backfill completeness / reviewer detection behavior 변화도 반영할 수 있다. 따라서 본 metric 은 **advisory operational signal only — 효과 "판정" 이 아니라 측정 "신호"** (Story §5.4 가정 2 + EC-3 정합). sunset 판정 자체 (DialogFidelityAgent archive / 강화 amendment) 는 별도 후속 carrier (precedent `rate-limit-fallback-rate` 의 `kpi_dashboard_3month_window_evidence` 도 독립 carrier).

### 14.4 strengthening ratchet 정합 (sunset_justification: null 근거)

measurement wiring = **강화 방향** (측정성 forcing function 도입 = ADR-058 carrier WHY 동형). ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification ratchet 차단 정합 — `sunset_justification: null` 적격 (Amendment 1 §12.7 / Amendment 2 §13.7 family pattern). additive 강화: Layer 1-4 + DialogFidelityAgent auxiliary 보존, measurement layer 추가만. `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

### 14.5 Epic plan Task 4 invariant 5 deviation (precedent override)

Epic plan (`mclayer/codeforge-internal-docs:wrapper/plans/2026-05-16-dialog-fidelity-agent-epic.md` Task 4 invariant 5) = "label-registry MINOR — `hotfix-bypass:dialog-fidelity` 1 entry + frontmatter version MINOR bump". **본 Story-3 는 이 invariant 5 를 deviation 한다**:

- **deviation 사유**: Epic plan invariant 5 는 evidence-check entry 가 static-lint (PR block) 임을 가정한 산물. 본 metric pattern = runtime cron measurement (precedent `rate-limit-fallback-rate` 동형 — advisory warning tier, PR block 안 함) → bypass label 의 의미 (PR block conditional skip) 부적용. label 신설 시 dead label 발생.
- **precedence**: ADR-064 §결정 10 = normative 우선순위 ADR > planning doc. Epic plan = planning artifact (normative SSOT 아님). precedent (`rate-limit-fallback-rate`) + ADR-060 §결정 3 (warning tier bypass 의미) 가 Epic plan invariant 5 보다 우선.
- **사용자 확정**: 2026-05-17 KST AskUserQuestion — OQ-3 = precedent 우선, label-registry MINOR 면제 명시 결정.
- **EPIC-RESULTS cross-ref 의무**: Epic close 시 `EPIC-RESULTS-CFP-761` 에 본 deviation 기록 의무 (PMOAgent Epic close 영역, Story §11 회고 cross-ref). 본 §14.5 + Change Plan CFP-833 §3.7 = SSOT 이중 anchor.

## §결정 15. Conversational reporting frequency suppression contract (Amendment 4, CFP-851)

> Story-1 (CFP-777) DialogFidelityAgent 도입 + Story-2 (CFP-818) spawn trigger 운영 정의 + Story-3 (CFP-833) effectiveness measurement wiring 이후 **누적 governance gap** — Orchestrator ↔ user dialog 의 **말 거는 시점·빈도** (frequency / timing) 가 SSOT 미codified 상태. carrier: CFP-851, issue https://github.com/mclayer/plugin-codeforge/issues/851. additive 강화 — Layer 1-4 + DialogFidelityAgent auxiliary + §결정 2(c) richness 보존, frequency 축소 layer 추가만.

### 15.1 본질 anchor — frequency vs richness 분리 (가장 중요한 invariant)

본 Amendment 4 가 좁히는 것은 Orchestrator 가 사용자에게 **말 거는 횟수·시점** (frequency / timing) 만이다. **말할 때의 풍부함은 보존된다.** 두 축 분리 invariant:

| 축 | 본 Amendment 4 의 작용 | SSOT |
|---|---|---|
| **frequency / timing** (말 거는 횟수·시점) | 좁힘 — 3 touchpoint closed enumeration (§15.2) | 본 §결정 15 신설 |
| **richness** (말할 때의 풍부함 — 길이 / 배경 / 평이 번역) | 보존 — 무약화 | §결정 2(c) verbatim 유지 (3 줄 제약 거부 · 길이 자유 · 배경 포함) |

이 분리가 본 Amendment 의 핵심 invariant 이며 ADR-058 §결정 5 약화 차단 (`sunset_justification: null`) 의 근거다. 3 touchpoint 발화 시 Layer 1 가시적 preamble + Layer 2 자기 declare + §결정 2(c) richness 그대로 적용 — turn-shape edge (E9/E10/E11/E12) derived default 도 무변경 (playbook §3.14 본문 결정 영역).

**Verifiable outcome surface 경계** (RE 안전판): 본 Amendment 가 억제하는 것은 **"how" (구현 과정)** 의 중간 보고이고, 억제하지 않는 것은 **"what" (요구 명세)** 의 disambiguation. 사용자가 선언한 결과가 모호하여 잘못 추측 시 rollback 비용이 큰 경우, 그 명세를 확인하는 것은 **요구사항 disambiguation** 이며 억제 대상이 아니다 (touchpoint (a)). 전면 보고 / 질문 억제 = 검증되지 않은 한쪽 극단 (wrong-dataset risk — requirements ambiguity 미해소 → 끝까지 wrong deliverable → rollback 비용 ≫ 보고 비용). SI 아웃소싱 / SQL 개발자 비유 (Story §1 사용자 directive verbatim) 도 동일 구조 — 고객은 "어떻게 뽑았는지" 의 중간 보고 불요지만 "무엇을 뽑을지" 의 명세는 ambiguous 시 SI 가 확인한다.

### 15.2 3 touchpoint closed enumeration

Orchestrator 의 사용자 발화 허용 시점 = closed enumeration 3 종. 그 외 진행·중간 결정·근거·중간 결과는 **산출물** (Story / change-plan / ADR / PR / TodoWrite panel) 전용 기록.

| touchpoint | 발화 사유 | 분류 |
|---|---|---|
| **(a) 결과-명세 확인** | 사용자가 선언한 결과 자체가 모호 + 잘못 추측 시 rollback 비싼 경우 | 요구사항 disambiguation (§결정 20 ask-trigger ① 요구 모호 + ③ rollback 비쌈 해당 — 일반 모호 자동 ask 아님), `AskUserQuestion` 의무 |
| **(b) 사용자만 풀 수 있는 차단** | 인증·권한 등 codeforge 자체 해소 불가, 사용자 행동 필요 | 차단 해소 (ADR-039 inline whitelist 1번 entry scope 안 — 사용자 dialog) |
| **(c) 최종 완료 보고 1회** | 요청한 작업 단위 전체 완료 | 산출물 = 최종 결과 자체 (ADR-039 inline whitelist 4번 entry scope 안 — Status report) |

**산출물 channel enumeration** (대화 turn 아닌 정상 기록 경로):
- `docs/stories/<KEY>.md` (Story file — §0 Live Progress / §9 / §10 FIX Ledger / §14 Lane Evidence)
- `docs/change-plans/<slug>.md` (Change Plan)
- `docs/adr/ADR-NNN-<slug>.md` (ADR)
- PR description / GitHub Issue comment
- TodoWrite panel (ADR-038 progress visualization — 산출물 channel, 대화 turn 아님)

### 15.3 무약화 invariant — §결정 2(c) 와의 정합

`[verified — Read ADR-071 §결정 2(c) lines 142-147]` 기존 §결정 2(c) "sub-agent 결과의 사용자용 평이 번역" = `3 줄 제약 명시적 거부 — 길이 자유` + `"왜 / trade-off / 걸려있는 것" 배경 포함`. 본 Amendment 4 는 이 정책을 **무약화** — 3 touchpoint 발화 시 Layer 1/2 preamble·declare + §결정 2(c) 풍부함 그대로 적용된다.

| Layer / 정책 | 본 Amendment 4 후 |
|---|---|
| Layer 1 가시적 preamble (§결정 3) | 보존 — 3 touchpoint 발화 시 매 turn 맨 윗줄 "지금 답해주실 것" 1 문장 (turn-shape edge derived default 무변경) |
| Layer 2 자기 declare (§결정 3) | 보존 — 3 touchpoint 발화 시 매 turn 맨 아랫줄 "주의한 가설" 1 줄 (E11 popup 면제 derived default 무변경) |
| Layer 3 "추상" halt (§결정 3) | 보존 — 모든 user-facing turn 에서 active |
| Layer 4 누적 detection (§결정 3 / §결정 6) | 보존 — cross-Story 영속 file append-only Orchestrator monopoly |
| §결정 2(c) richness (3 줄 제약 거부 + 배경 포함) | 보존 — 3 touchpoint 발화 시 그대로 적용 |
| Sub-mechanism 1/2 (§결정 4) | 보존 — halt 후 재작성 시 "이전과 다르게 한 점" + 4 차원 enum 강제 전환 |

> **[Amendment 9 / CFP-2236]** 위 표에서 DialogFidelity 관련 3 행 (DialogFidelityAgent auxiliary §결정 12 / DialogFidelityAgent 3-anchor spawn §결정 13 / §결정 14 measurement) 은 DialogFidelityAgent sunset 동반 제거. frequency-richness 본체 (§15.1/15.2/15.4) + Layer 1-4 행 + §결정 2(c) richness 행 + Sub-mechanism 행 무손상.

**5번째 cognitive layer 신설 금지 invariant (§결정 3 carrier — Amendment 9 re-home) 와의 정합**: 본 §결정 15 = mechanism (말 거는 시점 closed enumeration) 추가, §결정 3 cognitive layer count 변경 아님 (verifier 도입 = mechanism 추가, cognitive layer 신설 아님 동형 — 구 §12.3 family pattern, Amendment 9 후 invariant SSOT = §결정 3).

### 15.4 ADR-039 inline whitelist 정합 — closed 4-entry 보존

[ADR-039 §결정 2](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Inline whitelist 4-entry **closed enumeration** 보존 invariant. 3 touchpoint 는 기존 entry scope 안에서 작동 — 신규 entry 신설 0.

| touchpoint | ADR-039 inline whitelist entry |
|---|---|
| (a) 결과-명세 확인 | 1번 entry (사용자 dialog) — `AskUserQuestion` 발화 |
| (b) 사용자만 풀 수 있는 차단 | 1번 entry (사용자 dialog) — 사용자 행동 요청 발화 |
| (c) 최종 완료 보고 1회 | 4번 entry (Status report) — 작업 완료 통지 |

**5번째 entry 신설 X** — 새 카테고리 enumeration 추가 아님, 기존 1번·4번 entry 의 frequency 영역 명문화. closed enumeration 보존 invariant + 5번째 entry 신설 시 Amendment 의무 invariant 양 보존 (§결정 13.4 ADR-039 정합 명문화 family pattern 정합).

### 15.5 closed-enum 확장 패턴 (§결정 13.6 정합)

3 touchpoint enum = **closed enumeration**. 확장 후보 발생 시 (예: "사용자 explicit 과정 설명 요청" / "FIX 3 회 escalation 시점" / "보안 incident detect 시점") → **별도 CFP 신설 의무** (사용자 burden 변화 영역 — 발화 frequency 증가).

| 룰 | 적용 |
|---|---|
| ADR-064 §결정 7 top-down ratchet | 강화 방향 only (touchpoint 추가 = 발화 빈도 증가 강화 ratchet) |
| ADR-058 §결정 5 sunset_justification | touchpoint 축소 시 의무 (frequency 축소 = 사용자 burden 추가 변화 영역) |
| Story §1 사용자 explicit 승인 | 별도 CFP 의 Story §1 verbatim 명시 의무 (CFP-851 §1 declared outcome 1번 항목 verbatim pattern 정합) |

본 §15.5 codification = scope creep 차단 forcing function (§결정 13.6 closed-enum 확장 패턴 verbatim 적용 — 본 ADR 안 3번째 closed enumeration 인스턴스: 3-anchor enum (§13.6) / 4 차원 enum (§4) / 3 touchpoint enum (§15.5)).

### 15.6 measurement gap declare — behavioral directive only

본 §결정 15 = **behavioral directive only** (mechanical lint 부재). 3 touchpoint 외 발화 자동 감지 / 억제-induced rework 측정 채널 = 별도 follow-up CFP scope (ADR-071 §결정 10 "Layer 1 preamble mechanical lint = 별도 follow-up CFP" 패턴 정합 + §결정 14 measurement wiring precedent — advisory operational signal, blocking 승격 의미 부적용).

| 측정 axis | 본 Amendment 4 scope | 별도 follow-up CFP scope |
|---|---|---|
| 3 touchpoint 외 발화 detect | — | mechanical lint (별도 CFP, advisory warning tier 첫 도입 시 evidence-checks-registry entry 추가) |
| 억제-induced rework 빈도 | — | runtime cron metric (precedent `dialog-fidelity-effect` / `rate-limit-fallback-rate` 동형) |
| 사용자 explicit 과정 설명 요청 후 발화 frequency | — | 별도 CFP scope (확장 candidate, §15.5 정합) |

**ADR-058 §결정 3 측정성 self-application 정합**: 본 Amendment 가 measurement wiring 없이 영구화되면 안 됨을 인지. 단 measurement 자체 = behavioral baseline 누적 후 별도 CFP carrier 영역 — Amendment 4 effective 후 incident pattern (Layer 4 file row pattern_dimension="보고 형식") + PMOAgent retro user feedback 누적 가 baseline. §결정 14 measurement (CFP-833) precedent 동형 — measurement entry 가 ADR 본문 외부 (registry yaml) 에서 wiring.

### 15.7 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 4 = **additive 강화** (Layer 1-4 + DialogFidelityAgent auxiliary + §결정 2(c) richness + Inline whitelist 4-entry + 3-anchor enum + 4 차원 enum 모두 보존, frequency 축소 layer 추가만). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§12.7 / §13.7 / §14.4 family pattern 정합 — Amendment 1/2/3/4 모두 동일).

## §결정 16. Natural-language action trigger lookup table (Amendment 5, CFP-1104)

> CFP-1104 carrier 사용자 directive verbatim: Turn 1 "codeforge upgrade" / Turn 2 "항상 모호하다고 그러는데 codeforge를 통해 upgrade 절차에 대해 정립해둔게 있을거다. codeforge plugin에 반영해라" / Turn 3 "mctrader-hub와 mctrader-data에서 codeforge upgrade를 요구하면 애매하네요? 이런 소리 말고 바로 수행할 수 있도록". 본 §결정 16 = ADR-076 invariant `user_decision_branches: 0` 을 dialog 진입 단계로 확장 carrier — base ADR-071 §결정 5 사실/가치 분리 원칙의 dialog reflex (AskUserQuestion "어떤 upgrade?" "어느 채널?") 차단 first applied case.

### 16.1 본질 anchor

사용자가 IDE 에서 wrapper-managed-manifest.json 을 열어 둔 상태에서 단어 `codeforge upgrade` 하나만 발화 시 orchestrator 는 즉시 cwd + consumer overlay project.yaml + ADR-076 derived default 로 추론·실행한다. derived default 자명 (ADR-076 invariant + cwd 자동 / overlay channel resolve / dry-run → apply 자동 reflex) 이므로 발화 금지 — ADR-064 §결정 7 + ADR-071 §결정 5 가치/사실 분리 + ADR-039 inline whitelist 1번 entry "사용자 dialog 허용 영역이지만 derived default 자명 시 발화 금지" cognitive 강화 carrier.

### 16.2 Closed enumeration — 1 entry

| Trigger token (regex, case-insensitive) | Action |
|---|---|
| `\b(codeforge\s+upgrade\|codeforge\s+업그레이드)\b` | `scripts/codeforge-upgrade.sh` invocation per ADR-076 §결정 5 (§16.3 7 차원 derived default 자동 적용) |

본 lookup table = **closed enumeration**. 2번째 trigger token 확장 후보 (예: `codeforge rollback` / `codeforge family upgrade` / `codeforge plan` 등) 발생 시:

| 룰 | 적용 |
|---|---|
| ADR-064 §결정 7 top-down ratchet | 강화 방향 only (trigger token 추가 = 자율 reflex 영역 확장 강화 ratchet) |
| ADR-058 §결정 5 sunset_justification | trigger token 회수 시 의무 (사용자 burden 영역 — automatic reflex 가 dialog reflex 로 후퇴) |
| Story §1 사용자 explicit 승인 | 별도 CFP 의 Story §1 verbatim 명시 의무 (CFP-1104 §1 declared outcome verbatim pattern 정합) |
| SecurityArch consult | trust boundary 영역 — closed enum 확장 시 security review 의무 (ADR-039 entry 1 derived default 자명성 검토 의무, 의도 외 명령 실행 위험 평가) |

본 §16.2 codification = ADR 안 4번째 closed enumeration 인스턴스: 3-anchor enum (§13.6) / 4 차원 enum (§4) / 3 touchpoint enum (§15.5) / **trigger table (§16.2)**. §15.5 codify pattern verbatim 적용 — scope creep 차단 forcing function.

### 16.3 Derived default 7 차원 (CFP-1104 §5 verbatim)

orchestrator 가 사용자 발화 token detect 시 다음 7 차원 default 자동 적용. 사용자 정정 의무 (dialog reflex 차단 — Layer 1 preamble "발화하신 'codeforge upgrade' → 다음 default 로 즉시 수행" 1 문장 자기 발화만 의무, AskUserQuestion 0):

| 차원 | derived default | 근거 |
|---|---|---|
| trigger phrase | regex `\b(codeforge\s+upgrade\|codeforge\s+업그레이드)\b` (case-insensitive, 한글 변형 포함) | RequirementsAnalyst Edge Case + lint pattern 정합 (CFP-1104 §5) |
| repo | cwd 자동 주입 (`--repo $(pwd)`) | Researcher Unknown #3 해소 (CFP-1104 §5) |
| mode | dry-run 자동 → evidence 자동 verify → apply 자동 (사용자 확인 분기 0) | ADR-076 invariant + MCT-202 자율 full-run |
| channel | consumer overlay `.claude/_overlay/project.yaml::codeforge.channel.tier` resolve → fallback `"stable"` | ADR-076 v1.7 (CFP-906) |
| scope | 단일 codeforge plugin (default). 사용자가 "family" / "7-plugin" / "전체" 명시 시만 `atomic-upgrade-7-plugins.sh` | Researcher Unknown #2 — 단어 그대로 해석 |
| dirty tree | abort + 사용자 보고 (safe direction). `--force-dirty` opt-in flag 별도 follow-up | Researcher Unknown #3 + InfraOperationalArch §7.4.5 env containment consult |
| 실패 처리 | dry-run 실패 → abort + 사실 보고 / apply 실패 → 자동 rollback + 사실 보고 + 사용자 정정 의무 | ADR-076 §결정 3 snapshot/rollback |

### 16.4 ADR-076 invariant carrier 명문화

ADR-076 invariant `user_decision_branches: 0` (Epic CFP-699 §1 WHY "0 자리" verbatim, ADR-076 line 177/200 명시) = **CLI argument fix 단계** scope 명시. 본 §결정 16 = 동일 invariant 를 **dialog 진입 단계** 로 확장 carrier — 사용자 발화 → orchestrator 추론 → CLI invocation 사이 dialog reflex (AskUserQuestion / "어떤 ~?" / "어느 ~?") 차단.

- 두 단계 disjoint scope: ADR-076 = CLI argument 결정 분기 / 본 §결정 16 = 자연어 발화 → CLI mapping 결정 분기
- 동일 invariant 표현 ("결정 분기 0") 이지만 layer 다름 (CLI vs dialog) — 두 ADR carrier 의 합집합 = end-to-end "결정 분기 0"

### 16.5 ADR-039 inline whitelist 1번 entry 정합 명문화

[ADR-039 §결정 2](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Inline whitelist 4-entry **closed enumeration** 보존 invariant. 본 §결정 16 의 dialog reflex 차단은 기존 1번 entry "사용자 dialog 허용 영역" scope 안에서 작동 — 신규 entry 신설 0.

**구체 적용**: 사용자 token detect 시 Orchestrator inline 발화 = 1번 entry scope 안. 단 발화 내용 = derived default declare 1 문장 (Layer 1 preamble) + `scripts/codeforge-upgrade.sh` 즉시 실행 (E10 tool-call-only edge, AskUserQuestion 0). 발화 자체 차단 아님 — **dialog reflex (AskUserQuestion / 모호함 호소 / 옵션 dump) 차단** 만.

**5번째 entry 신설 X** — 새 카테고리 enumeration 추가 아님, 기존 1번 entry 의 "derived default 자명 시 발화 금지" 1 문장 명문화 (§결정 11 family pattern 정합).

### 16.6 closed-enum 확장 패턴 (§결정 13.6 + §15.5 정합)

본 §16.2 trigger table = **closed enumeration** (1 entry). 확장 후보 발생 시:

| 룰 | 적용 |
|---|---|
| ADR-064 §결정 7 top-down ratchet | 강화 방향 only (trigger token 추가 = 자율 reflex 영역 확장) |
| ADR-058 §결정 5 sunset_justification | trigger token 회수 시 의무 (사용자 burden 영역) |
| Story §1 사용자 explicit 승인 | 별도 CFP 의 Story §1 verbatim 명시 의무 |
| SecurityArch consult | trust boundary 영역 — 의도 외 명령 실행 위험 평가 의무 |

본 §16.6 codification = §결정 13.6 + §15.5 closed-enum 확장 패턴 family pattern 정합 — 본 ADR 안 4번째 closed enumeration 인스턴스 (3-anchor enum (§13.6) / 4 차원 enum (§4) / 3 touchpoint enum (§15.5) / **trigger table (§16.2)**).

### 16.7 measurement gap declare — behavioral directive only

본 §결정 16 = **behavioral directive only** (mechanical lint 부재). orchestrator 자연어 token detect 자체의 false negative (token detect 실패 → AskUserQuestion 발화) / false positive (의도 외 token match → 잘못된 upgrade 실행) 자동 감지 채널 = 별도 follow-up CFP scope (ADR-071 §결정 10 "Layer 1 preamble mechanical lint = 별도 follow-up CFP" + §결정 14 measurement wiring precedent + §결정 15.6 measurement gap declare 패턴 정합 — advisory operational signal, blocking 승격 의미 부적용).

| 측정 axis | 본 Amendment 5 scope | 별도 follow-up CFP scope |
|---|---|---|
| token detect false negative (AskUserQuestion 발화 회귀) | — | runtime cron metric (precedent `dialog-fidelity-effect` 동형) |
| token detect false positive (의도 외 명령 실행) | — | SecurityArch consult mandate + audit log (precedent `rate-limit-fallback-rate` 동형) |
| dirty tree abort 정확성 | — | regression test (별도 CFP scope) |

**ADR-058 §결정 3 측정성 self-application 정합**: 본 Amendment 5 가 measurement wiring 없이 영구화되면 안 됨을 인지. 단 measurement 자체 = behavioral baseline 누적 후 별도 CFP carrier 영역 — Amendment 5 effective 후 PMOAgent retro user feedback (token detect 회귀 incident) 누적 가 baseline. §결정 14 measurement (CFP-833) precedent 동형 — measurement entry 가 ADR 본문 외부 (registry yaml) 에서 wiring.

### 16.8 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 5 = **additive 강화** (Layer 1-4 + DialogFidelityAgent auxiliary + §결정 2(c) richness + Inline whitelist 4-entry + 3-anchor enum + 4 차원 enum + 3 touchpoint enum 모두 보존, dialog reflex 차단 layer 추가만). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§12.7 / §13.7 / §14.4 / §15.7 family pattern 정합 — Amendment 1/2/3/4/5 모두 동일).

## §결정 17. Lane back-translation gate binding (Amendment 6, CFP-1110)

### 17.1 컨텍스트 + 사용자 directive verbatim

본 §결정 17 = **사용자 직권 minimal path 첫 적용** (paradox-break first application). 사용자 directive 2026-05-20 KST verbatim:

> "어쨌든 시간이 오래걸리든 비용이 많이 나오든 무관하게 성능이 제일 중요하다. 근데 시간도 오래걸리는데 레인이 지날수록 내가 요구했던 요건이 흩어지고 이상한 작업만 수행하는 것 같아서 그렇다."

본질 = **lane traversal fidelity loss** — 사용자 발화 원문이 lane 통과마다 재합성되며 weight 가 희석, lane 내부 invariant 가 그 자리를 차지하는 현상. Researcher (general-purpose) + Codex 병렬 critical evaluation 수렴 결과:

- Researcher net 35% 정당화 (verify-before-trust + Epic gate 영역만)
- Codex ROI indeterminate, 부정 쪽 기울기, confidence medium — denominator (consumer-protective fraction) 측정 부재
- 구조적 결함: sunset asymmetry (실 retire 0건 since codeforge 정상 운영 진입) / self-referential dogfood paradox 만성화 / mechanical layer 가 race 차단 불가 입증

### 17.2 pattern corpus 누적 evidence

| # | 출처 | 패턴 | count |
|---|---|---|---|
| 17-A | CFP-722/801/792/810/819/825 | synthesizer-stale-reference (synthesis layer 원본 drift) | 6 |
| 17-B | CFP-698 | Researcher agent fact drift (12 occurrence 정정) | 12 |
| 17-C | CFP-758 | scope 재확대 금지 invariant 6+ 위치 (scope drift 만성 evidence) | 6+ |
| 17-D | unverified-self-write-claim super-class (CFP-746/770/1000/1001/1002) | write-time semantic truth verify 부재 | 5 |
| 17-E | CFP-906 | DesignReviewPL cross-PL false-negative (review 가 사실과 다른 결론) | 1 |

PMOAgent ADR-045 §D-9 정량 임계값: pattern_count **≥ 6** ≫ threshold 2 → Mandatory framing + escalation_action `escalate_user` → 사용자 단일 super-class 통합 결정 (본 §결정 17 + paired ADR-082 Amendment 5 §결정 1 sub-scope (1-C)).

### 17.3 구조적 원인 (3)

본 ADR-071 §결정 13 (DialogFidelityAgent codify) + §결정 14 (effectiveness measurement wiring) 의 read-only verifier 패턴이 lane traversal fidelity loss 차단에 부족한 구조적 원인:

1. **Story §1 원문 → §2 Why / §3 Design 재합성 손실** — 매 lane PL spawn prompt 안 anchor 가 재합성된 weight 만 흘러간다. paired ADR-082 Amendment 5 §결정 1 sub-scope (1-C) Lane PL spawn prompt user-utterance verbatim anchor 가 write-time input anchor 차원 해소 (본 §결정 17 의 sister carrier).
2. **codeforge-design lane fan-out 불균형** — chief + 5 deputy + 4-tuple sub-tuple = 10+ agent advocacy. 1 user 요구 vs 10+ deputy mandate 의 weight 비대칭, deputy 가 자기 mandate 영역 expansion 만 강화 (cross-lane requirement traceability 약화). scope_boundary 영역 (17.6 참조 — 별도 CFP carrier).
3. **DialogFidelityAgent read-only binding 약함** — `post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause` 3-anchor (§결정 13.6) 에서 divergence 검출은 가능하나, lane 재실행 강제 못함. 본 §결정 17 = read-only verifier → binding mechanism 확장 carrier (return-time output gate 차원).

### 17.4 결정 — Lane return back-translation gate (binding 강화)

각 lane PL agent (RequirementsPLAgent / ArchitectPLAgent / DesignReviewPLAgent / DeveloperPLAgent / CodeReviewPLAgent / SecurityTestPLAgent) 가 spawn 결과를 Orchestrator 로 return 할 때:

#### 17.4.1 PL self-write deliverable verify (lane PL 의무)

lane PL deliverable (Story §-N section / Change Plan section / verdict packet / FIX root cause 등) return 시 PL 자체가 다음 reverse summary block 부착 의무:

```
[LANE-RETURN-BACK-TRANSLATION]
사용자 원문 (verbatim, paired ADR-082 Amendment 5 §결정 1 sub-scope (1-C) anchor block 의 USER-UTTERANCE-VERBATIM 와 동일):
> <사용자 원문 verbatim>

본 lane 산출물 reverse summary (사용자 원문 언어로):
- <산출물 요약 1, 사용자 발화 언어 어휘로 재구성, lane 내부 vocabulary / invariant / mandate ratchet 어휘 사용 회피>
- <산출물 요약 2>
- ...

산출물 ↔ 사용자 원문 alignment self-attestation:
- aligned: <list of aligned points>
- divergence (의도된 scope 확장 OR fidelity loss 가능): <list of divergence points + 분류 (intended_expansion | fidelity_loss_candidate)>
[/LANE-RETURN-BACK-TRANSLATION]
```

PL self-attestation 의도된 scope 확장 vs fidelity loss 분류 명시 의무. self-attestation 자체가 ADR-082 §결정 2 write-time verify 영역 (PL self-write deliverable — 본 자기 attestation 도 verify-before-trust 대상).

#### 17.4.2 Orchestrator divergence detection trigger (binding mechanism)

Orchestrator lane return 수신 직후 `[LANE-RETURN-BACK-TRANSLATION]` block 안 `divergence` list 항목 검토:

- `intended_expansion` 분류 = Orchestrator approve (사용자 directive 외 scope 확장 의도 명시, fidelity 차원 무관 정합)
- `fidelity_loss_candidate` 분류 = Orchestrator 가 **lane 재실행 trigger** (PL re-spawn with refined spawn prompt — 사용자 원문 verbatim anchor weight 강화 + 발산 영역 explicit guardrail). 재실행 후 lane PL return 시 17.4.1 self-attestation 재수행 의무.

lane 재실행 횟수 cap = ADR-067 §결정 1 (max FIX 3/3 reassessment trigger) + §결정 3 (RESET vs escalation 권한) 복합 재사용 (ADR-082 §결정 3 정정 재귀 무한루프 cap 패턴 verbatim 답습). 3회 reach 시 사용자 escalation (ADR-067 §결정 2 escalation 의무 trigger 3종 평가).

#### 17.4.3 DialogFidelityAgent 3-anchor scope 확장

> **[SUNSETTED — Amendment 9 / CFP-2236, 2026-06-14 KST]** 본 §17.4.3 의 4번째 anchor `post_lane_return` (DialogFidelityAgent binding-capable anchor) 만 sunset — DialogFidelityAgent 전면 폐지. **§17.4.1 (PL self-attestation back-translation body) + §17.4.2 (Orchestrator divergence detection trigger) 는 DialogFidelity-independent → 보존** (lane PL self-write deliverable verify + Orchestrator lane 재실행 trigger 는 verifier 없이 작동). lane back-translation gate 본체 무손상. 본문 = historical record carrier-preserved.

§결정 13.6 DialogFidelityAgent 3-anchor (`post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause`) 에 4번째 anchor 신설:

| anchor | trigger | scope | binding |
|---|---|---|---|
| `post_user_turn` (§결정 13.6) | Orchestrator user-facing turn 직후 | dialog turn 자체 fidelity check | read-only verifier (Amendment 1-3 유지) |
| `pre_architectpl_synthesis` (§결정 13.6) | ArchitectPLAgent synthesis 직전 | synthesis layer drift check | read-only verifier (Amendment 1-3 유지) |
| `pre_fix_rootcause` (§결정 13.6) | FIX root cause 판정 직전 | root cause drift check | read-only verifier (Amendment 1-3 유지) |
| **`post_lane_return` (Amendment 6 신설)** | **lane PL return 직후 (17.4.1 self-attestation 후)** | **사용자 원문 anchor vs PL reverse summary divergence detection — `fidelity_loss_candidate` 항목 cross-validate** | **binding (17.4.2 Orchestrator lane 재실행 trigger 보조 — DialogFidelityAgent verdict 가 Orchestrator decision 의 input)** |

4번째 anchor = read-only verifier 패턴 (Amendment 1) 외 첫 binding-capable anchor. 단 DialogFidelityAgent 자체는 read-only 유지 — binding mechanism = Orchestrator 가 DialogFidelityAgent verdict + PL self-attestation 양 input 으로 lane 재실행 결정 (DialogFidelityAgent 가 lane 재실행 강제 권한 직접 보유하지 않음 — Orchestrator monopoly 보존, ADR-039 inline whitelist 4-entry scope 안).

### 17.5 Wave 1 (behavioral) + Wave 2 (mechanical) progression chain

ADR-040 Amendment 3 self-application Wave 1→Wave 2 progression chain (ADR-082 §결정 6 / §A2-2 / §A5-3 정합):

| Wave | scope | enforcement | carrier |
|---|---|---|---|
| Wave 1 (Amendment 6) | §결정 17.4.1 PL self-attestation behavioral mandate + 17.4.2 Orchestrator divergence detection behavioral mandate + 17.4.3 DialogFidelityAgent 4번째 anchor codification | playbook §3.19 신설 (Orchestrator self-discipline — lane return back-translation gate handling) + DialogFidelityAgent SKILL.md §X (post_lane_return anchor codification) | CFP-1110 (본 carrier) |
| Wave 2 (후속 CFP) | mechanical lint — `[LANE-RETURN-BACK-TRANSLATION]` block presence + `divergence` field schema valid + `fidelity_loss_candidate` count tracking | `scripts/check-lane-return-back-translation.sh` (deferred-followup, ADR-060 §결정 5 모든 신규 entry warning 시작 강제 정합) + evidence-checks-registry `lane-return-back-translation-gate` entry warning tier | 후속 CFP (별 carrier, brainstorm 단계 결정) |
| Wave 3 (DialogFidelityAgent runtime hook 확장) | post_lane_return anchor 실 runtime invocation (현 SessionStart hook + 3-anchor 외 4번째 anchor 자동 spawn) | DialogFidelityAgent SKILL.md runtime wire + codeforge-pmo lane plugin (DialogFidelityAgent owner) sibling sync (ADR-010 정합) | 별도 cross-repo CFP carrier (codeforge-pmo plugin) |

Wave 2/3 = deferred-followup. 본 Amendment 6 frontmatter `mechanical_enforcement_actions[]` 갱신 0건 (Wave 1 = behavioral mandate + playbook codification + SKILL.md 4번째 anchor 정의, mechanical lint + runtime hook 자체는 Wave 2/3 carrier). §결정 14 의 `dialog-fidelity-effect` 1 entry 유지 — 본 Amendment 6 scope 4번째 anchor 와 disjoint sub-decision (`dialog-fidelity-effect` = incident append-rate delta proxy signal, post_lane_return anchor = lane-level divergence detection, 측정 axis 다름).

### 17.6 scope_boundary (out-of-scope)

본 Amendment 6 **포함**: §결정 17 (back-translation gate binding) + 4번째 anchor `post_lane_return` codification + Wave 1 behavioral mandate + playbook §3.19 + SKILL.md §X 추가.

본 Amendment 6 **out-of-scope** (유지 / 별 carrier):

- **codeforge-design lane fan-out 축소** (chief + 5 deputy + 4-tuple = 10+ agent → 핵심 4-5 축소) — fidelity vs coverage trade, 별도 가치 판단 영역 → 별도 CFP carrier (brainstorm 단계 결정).
- **Wave 2 mechanical lint** (`scripts/check-lane-return-back-translation.sh`) + evidence-checks-registry entry = 후속 CFP carrier (deferred-followup).
- **Wave 3 DialogFidelityAgent runtime hook 확장** (codeforge-pmo plugin sibling sync) = 별도 cross-repo CFP carrier (ADR-010 정합).
- **paired sibling Amendment scope** (lane PL spawn prompt user-utterance verbatim anchor — write-time input anchor 차원) = ADR-082 Amendment 5 SSOT (본 CFP-1110 동일 carrier, ADR 분리 — disjoint axis: 본 ADR = return-time output gate / ADR-082 = write-time input anchor).
- 신규 ADR 창설 = Amendment only.

### 17.7 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 6 = **additive 강화** (Layer 1-4 + DialogFidelityAgent auxiliary + §결정 12-16 모두 보존, 4번째 anchor `post_lane_return` 추가 + binding mechanism Orchestrator-mediated 추가 only). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§12.7 / §13.7 / §14.4 / §15.7 / §16.8 family pattern 정합 — Amendment 1/2/3/4/5/6 모두 동일).

**사용자 직권 minimal path = closed-loop break 외부 결정 채널, ratchet 강화 self-application 정직 명시** — 본 Amendment 자체가 monotonic-increasing governance 의 부분 (verify-before-trust + DialogFidelityAgent binding 영역 안 — Researcher critical evaluation net positive 35% 영역 직접 확장). codeforge full flow 적용 paradox 회피 정합.

## §결정 18. Unjustified session swap reflex 차단 + /compact normative (Amendment 7, CFP-1340)

### 18.1 결정 요약

> **[Amendment 16 / §결정 24, CFP-2742]** 자족 handoff 프롬프트 동반 시 전환 권유를 허용하는 **controlled-path carve-out 은 §결정 24 신설** — 본 anti-pattern 7종 enum·정당 2-trigger 표는 **무변경**(handoff 미동반 = 여전히 차단). 조건부 허용 gate 는 §결정 24 소관 (본문 immutability, 본 pointer 1줄만 additive).

Orchestrator 가 사용자에게 **session swap 권유 발화** ("새 세션 만들어 주세요" / "세션 교체해 주세요" / "처음부터 다시 시작해 주세요" / "다음 작업은 새 세션에서") 는 **closed 2-trigger** 만 정당:

| trigger | 정의 | 정당 사유 |
|---|---|---|
| (1) ADR-053 (구조 변경 재구동) | 직전 세션의 구조 변경 (hook / settings / plugin install / agent file 도입) 후 재구동 필요 | session 안 cached state 가 새 구조 미반영 — 새 세션이 fresh load 필요 |
| (2) ADR-057 (Sonnet/Haiku → Opus fallback) | Orchestrator model = `claude-opus-4-7` 의무, Sonnet/Haiku 세션 detect 시 즉시 중단 | model tier mismatch — Opus 재시작이 유일 path |

그 외 모든 trigger = **anti-pattern, Orchestrator 발화 차단**.

### 18.2 Anti-pattern 7종 (closed enum)

발화 차단 대상 trigger phrase + 처리 path:

| # | anti-pattern trigger | 처리 path |
|---|---|---|
| 1 | "context 가득" / "context window 한계" | `/compact` slash command 활용 normative (harness auto-compress 신뢰) |
| 2 | "메모리 차서" / "메모리 한도 초과" | MEMORY.md 한도 초과 = 인덱스 entry 슬림화 trigger (세션 분리 아님) |
| 3 | "큰 Story" / "스코프 크다" | Story scope 자체는 single session 안 진행 가능 (Phase 분리 + ADR-067 RESET cap 활용) |
| 4 | "token budget" / "토큰 절약" | token budget = Sonnet/Opus tier 선택 영역 (ADR-042) 또는 `/compact` — session swap 영역 아님 |
| 5 | "MEMORY.md 한도 초과" | 24.4KB cap 초과 = 인덱스 entry 슬림화 (consolidate / archive) 의무, session 재시작 아님 |
| 6 | "자기 보존" / "session lifecycle" | session = ephemeral resource, lifecycle 결정은 사용자 영역 — Orchestrator self-recommendation 차단 |
| 7 | "토큰 절약" / "비용 최적화" | cost optimization = model tier 영역 (ADR-042) — session swap 영역 아님 |

7종 anti-pattern enum **closed**. 8번째 anti-pattern 추가 = 별도 ADR Amendment 의무 (강화 방향 ratchet 정합).

### 18.3 `/compact` slash command + MEMORY.md 슬림화 normative

session 안 context 압박 시 정당 path:

1. **`/compact` slash command 활용** — Claude Code harness 의 in-session compression mechanism. session 유지 + token usage 압축.
2. **MEMORY.md 인덱스 entry 슬림화** — auto-memory file 한도 초과 시 entry consolidate / archive (oldest-first + completed-Story entry consolidate). session 재시작 trigger 아님.
3. **harness auto-compress 신뢰** — Claude Code harness 가 자동 context window 관리 — Orchestrator 가 manual session swap reflex 발화 금지.

**Forbidden**: Orchestrator 가 "context 압박" 감지 시 "별도 세션에서 진행" / "새 세션 만들어" reflex 발화. 본 reflex 발화는 ADR-039 inline whitelist 1번 entry (사용자 dialog) scope 외 발화 — Anti-pattern 7종 detect 시 발화 차단.

### 18.4 재발 incident 2건 evidence (verbatim citation)

**Incident (a)** — 2026-05-21 KST Epic CFP-1059 Story transition 4회:

> "Epic CFP-1059 Story-2/3/4/5/6/7 전환 시점 매번 본 세션 context 극한 도달 — 별 세션 권장. Story 단위 session 분리 정책 수립 권유."

→ Orchestrator self-recommendation reflex 발화 — anti-pattern 1 "context 가득" + anti-pattern 3 "큰 Story" 동시 trigger. 4회 누적 reflex.

**Incident (b)** — 2026-05-23 KST 세션 시작 시 시스템 reminder:

> "MEMORY.md is 53.2KB (limit: 24.4KB). Consider archiving old entries or starting a new session."

→ Orchestrator 가 시스템 reminder 자체 wording ("new session") 을 그대로 수용 발화 — anti-pattern 5 "MEMORY.md 한도 초과" trigger. system reminder = 정보 surface 만, action prescription 아님 → Orchestrator 해석 단계에서 차단 의무 위반.

**pattern_count 2 reach** (ADR-045 §D-9 threshold). normative codify 정당 evidence base.

### 18.5 axis disjoint declare

본 §결정 18 = **session lifecycle reflex** sub-pattern (Orchestrator 의 session lifecycle 결정 영역 self-restriction). axis disjoint with:

- **§결정 4 sub-mechanism 2 "차원 enum 4종 closed"** (표현 / 결정 구조 / 보고 형식 / 질문 자체) — 본 §결정 18 = "결정 구조" 차원 sub-pattern routing (5번째 차원 신설 회피, closed enumeration 보존 invariant). session lifecycle reflex 는 "결정 구조" 차원 의 sub-routing — 사용자 결정 영역 (가치 판단) 으로 분류 강제.
- **§결정 17 (Amendment 6) lane back-translation gate** — return-time output gate 차원. 본 §결정 18 = session lifecycle reflex 차원. 두 axis 완전 disjoint (lane traversal fidelity ↔ session lifecycle reflex).
- **§결정 5 사실/가치 판단 분류 결정 트리** — session swap 결정 = 가치 판단 영역 (사용자 cognitive bandwidth / session continuity 선호) — Orchestrator self-recommendation 차단 정합 (`AskUserQuestion` 발화 의무 영역).

### 18.6 ADR-039 inline whitelist 1번 entry 정합

본 §결정 18 = ADR-039 inline whitelist 1번 entry (사용자 dialog) scope 안 **사용자 dialog 본 발화 제약**. dialog turn 자체는 inline 유지 — anti-pattern 7종 detect 시 발화 self-restriction.

DialogFidelityAgent (Amendment 1-3 3-anchor / Amendment 6 4-anchor) 가 `post_user_turn` anchor 에서 anti-pattern 7종 detect 가능 (5번째 anchor 신설 아님 — 기존 `post_user_turn` anchor scope 확장 only). pattern_dimension 분류 = "결정 구조" (§결정 4 4 차원 enum).

### 18.7 scope_boundary (out-of-scope)

본 Amendment 7 **포함**: §결정 18 신설 + closed 2-trigger 정당 / 7종 anti-pattern 차단 / `/compact` + MEMORY.md 슬림화 normative + 재발 incident 2건 evidence codify + axis disjoint declare + ADR-039 정합 명문화.

본 Amendment 7 **out-of-scope** (별 carrier):

- **`/compact` slash command 자체 정의 / 실 mechanism** — Claude Code harness 영역 (외부), codeforge governance scope 외.
- **MEMORY.md 인덱스 entry 슬림화 mechanism** — auto-memory file 영역 (Claude Code harness), codeforge governance scope 외. 별 carrier (사용자 memory management protocol) defer. `resolved_carrier: ADR-129` (Amendment 12, CFP-2392, 2026-06-24 — defer 해제: ADR-129 §결정 2 가 2-layer budget + oldest-first/completed-Story consolidate 슬림화 + lossless invariant 로 mechanism 실현. skills/knowledge-capture-gate/SKILL.md §2 slimming-protocol SSOT).
- **Mechanical lint** — anti-pattern 7종 detect mechanical check = behavioral directive only, 별도 follow-up CFP carrier (deferred-followup, ADR-060 §결정 5 모든 신규 entry warning 시작 정합).
- **DialogFidelityAgent runtime hook 확장** (`post_user_turn` anchor 안 anti-pattern 7종 detect) — Wave 2 별도 cross-repo CFP carrier (codeforge-pmo plugin).
- **session lifecycle 결정 mechanism 자체** (어떤 session 을 어떻게 끝낼지) — 사용자 영역, Orchestrator self-determination scope 외.

### 18.8 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 7 = **additive 강화** (Layer 1-4 / DialogFidelityAgent auxiliary / §결정 12-17 모두 보존, session lifecycle reflex sub-pattern 차단 layer 추가 only). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§12.7 / §13.7 / §14.4 / §15.7 / §16.8 / §17.7 family pattern 정합 — Amendment 1/2/3/4/5/6/7 모두 동일).

## §결정 19. Agent burst output paste 합성 시 mid-turn glossary lookup 의무 (Amendment 8, CFP-1764)

### 19.1 결정 요약

Orchestrator 가 agent burst output (DomainAgent / ResearcherAgent / RequirementsAnalystAgent / PMOAgent 등 4+ 부속 작업자) 결과를 사용자 메시지로 합성 (paste-and-translate) 할 때 의무 lookup:

1. **mid-turn glossary lookup 의무** — `docs/wording-dictionary.md` 카테고리 (c) codename → 평이 어휘 mapping table 을 lookup 후 1:1 치환 또는 평문 풀이 동반.
2. **lookup table SSOT location** = `docs/wording-dictionary.md` 카테고리 (c). ADR 본문 / skill SKILL.md / domain-knowledge 별도 SSOT 금지 (중복 codification 0, single source of truth).
3. **closed enumeration cap = 15 codename** (첫 batch). 신규 어휘 등장 시 별도 후속 CFP 의무 (ratchet extensibility).
4. **Scope** = 사용자 dialog turn (Orchestrator 직접 발화) 영역만. governance artifact (ADR / spec / change-plan / Story file) = scope 외 (codename 자연 사용).
5. **§결정 2(a) frame mode step 4 (message 작성) 직전 cognitive 단계** — "glossary lookup 필수 실행". codename 발견 시 평이 어휘 치환 또는 평문 풀이 동반. step 1 (격리) + step 2 (사용자 지식 추정) + step 3 (turn 결정 1 문장) + **step 3.5 glossary lookup** + step 4 (메시지 작성).
6. **Mechanical layer (Story-2 carrier)** — `codename-glossary-lookup` warning-tier evidence-check entry (23번째 entry) + `hotfix-bypass:codename-glossary-lookup` 75번째 hotfix-bypass family member + PR diff scan workflow.

### 19.2 배경 — mctrader-hub#517 4-turn 누적 jargon leak

consumer mctrader-hub#517 PR 안 brainstorm Phase 1 dialog 도중 4-turn 누적 jargon leak 재발. wired mechanism 10+ 종 (§결정 1-18 + DialogFidelityAgent + UserPromptSubmit hook rule 1) 모두 차단 실패. 사용자 directive 4건 verbatim:

| turn | 사용자 발화 |
|------|------------|
| 1차 | "여전히 어투가 사용자 친화적이지 않다. 적용되지 않은 것 같아" |
| 2차 | "아니 그렇게 넘어가지 말고 codeforge에서 넘어온 내용 있잖아. 그게 왜 적용이 안되는거야" |
| 3차 | "너가 memory에 적은 내용은 제거해" (consumer ad-hoc fix 거부) |
| 4차 | "제발 이번엔 제대로 하자. 다시 하는 일 없도록 꼼꼼하게 검토하여 계획하라." |
| confirm | "오케이 그렇게 escalation 하자. 그렇게 버전업되면 버전 업그레이드 통해 적용받는 식으로" |

사용자 confirm directive verbatim = wrapper canonical path 의무 anchor (consumer ad-hoc fix 거부 + wrapper Amendment LAND → version bump → consumer plugin update).

### 19.3 Root cause

§결정 2(c) "평이 번역 의무" 는 명시되나 *번역 mechanism 부재* — agent output prose 가 codeforge vocabulary 로 작성된 채 Orchestrator 가 합성 발화에 그대로 옮긴다. Axis = "mid-turn output composition" — §결정 17 (lane-return scope) 와 disjoint axis (lane return = boundary, paste 합성 = mid-turn).

### 19.4 면제 channel

`hotfix-bypass:codename-glossary-lookup` label (audit-trailed exception, [ADR-024](ADR-024-story-scoped-branch-policy.md) §결정 6 per-entry namespace 정합). 카테고리 (a) forbid 의 `hotfix-bypass:wording-dictionary` 와 별도 channel — disjoint scope. Story-2 carrier 75번째 hotfix-bypass family member 신설.

### 19.5 Consumer false positive handling

consumer project (mctrader-hub 등) 가 동일 codename 을 비즈니스 용어로 사용하는 경우 (예: "drift" = 포트폴리오 변동 감지), consumer overlay `jargon_filter_exempt_vocabulary: [...]` field 신설 — 별도 follow-up CFP carrier (본 Amendment 8 scope 외). consumer overlay 가 wrapper 정책 축소 불가 invariant 정합 — exempt 선언은 false positive 회피 channel only (wrapper 정책 자체 약화 아님).

### 19.6 Axis disjoint declare (3종)

| 기존 §결정 | axis | 본 §결정 19 axis | 관계 |
|---|---|---|---|
| §결정 17 (Amendment 6, lane back-translation gate) | return-time output gate per-lane vertical axis | mid-turn paste-and-translate horizontal axis (lane-agnostic Orchestrator 합성) | disjoint cross-cutting |
| §결정 14 (effectiveness measurement, CFP-833) | post-hoc metric layer | mid-turn forcing function layer | disjoint sibling |
| ADR-064 §결정 9 (question quality 3-check) | dialog 진입 결정 분기 self-check | dialog 진입 후 발화 작성 mid-turn 단계 | disjoint sibling |

본 §결정 19 = mid-turn paste-and-translate **mechanism 추가** — §결정 12.3 invariant "신규 5번째 cognitive layer 신설 금지" 보존 (§결정 3 4-layer cognitive enum count 변경 아님, mechanism 만 추가).

### 19.7 효과 measurement

- Layer 4 영속 file (`docs/orchestrator-communication-incidents.md`) pattern_dimension `표현` 차원 신규 incident 발생률 < 1건/100 turn (Story-2 warning-tier lint 측정 baseline)
- `hotfix-bypass:codename-glossary-lookup` 발화 count 누적 추세 (Story-2 lint warning false positive proxy)
- consumer Layer 4 영속 file row 신규 추가 빈도 (mctrader-hub#517 baseline 4-turn 누적 → 1-turn 이하 감소 KPI)

3 dimension 정량 metric — empirical-source annotation: Story-2 land 후 30-day rolling window. KPI artifact = 별 sub-CFP carrier (Wave 2 mechanical wire 후).

### 19.8 scope_boundary (out-of-scope)

본 Amendment 8 **포함**: §결정 19 신설 + wording-dictionary 카테고리 (c) SSOT codify (closed 15 codename 첫 batch + ratchet extensibility) + CLAUDE.md cross-ref + skill SKILL.md cross-ref + plugin.json MINOR bump + CHANGELOG row + marketplace sibling sync.

본 Amendment 8 **out-of-scope** (별 carrier):

- **mechanical lint backbone** (`scripts/check-codename-glossary-lookup.sh` + workflow + evidence-checks-registry row + label-registry MINOR) — **Story-2 carrier** (#797 unblock).
- **4 부속 작업자 prompt template 갱신** (DomainAgent / ResearcherAgent / RequirementsAnalystAgent / PMOAgent 평이 번역 directive 추가) — **Story-3 carrier** (codeforge-requirements + codeforge-pmo sibling 2-PR).
- **consumer overlay `jargon_filter_exempt_vocabulary` field** — consumer customization 영역, 별도 follow-up CFP carrier (consumer-guide.md schema 확장).
- **신규 codename 추가** (16번째 entry 이상) — ratchet extensibility, 별도 후속 CFP 의무 (ADR-064 §결정 5 CFP scope unitary 정합).
- **turn-final hook mechanical wire** — Claude Code harness 영역 (외부), platform inherent limit. runtime mid-turn block 불가 — Story-2 lint = PR diff scan layer (post-write detection only).

### 19.9 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 8 = **additive 강화** (Layer 1-4 / DialogFidelityAgent auxiliary / §결정 12-18 모두 보존, mid-turn paste-and-translate mechanism 추가 only). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§12.7 / §13.7 / §14.4 / §15.7 / §16.8 / §17.7 / §18.8 family pattern 정합 — Amendment 1/2/3/4/5/6/7/8 모두 동일).

## §결정 20. §결정 5 결정 트리 redirect — over-asking 안전편향 제거, ask-trigger 3종 한정 (Amendment 10, CFP-2371)

> **[REDIRECT carrier — Amendment 10 / CFP-2371, 2026-06-19 KST]** §결정 5 의 `AMBIGUOUS → 가치 측 분류(safe direction) → AskUserQuestion` 룰 폐기. 현행 SSOT = 본 §결정 20. §결정 5 본문은 historical record (carrier-preserved, 통째 삭제 아님).

### 20.1 결정 요약 (redirect)

기존 §결정 5 (사실/가치 분류 결정 트리) 의 모호(`AMBIGUOUS`) 처리 — "가치 측 분류(safe direction) → AskUserQuestion 발화 의무" — 를 폐기하고, **ask-trigger 3종에 해당할 때만 `AskUserQuestion`, 그 외(모호 포함) 전부 derived default 적용 + declare + 진행 + 1줄 정정 초대** 로 전환.

**ask-trigger 3종 (이 셋일 때만 멈춰 묻는다)**:

| trigger | 의미 |
|---|---|
| ① 요구 애매 | 사용자 요구 자체에 애매함이 있어 진행 방향이 안 잡힘 — 명확화 필요 |
| ② 진짜 가치 trade-off | 확실히 짚어야 하는 가치 결정 — default 비자명 + 사용자 선호가 결과를 가름 (제품 방향·우선순위 등) |
| ③ 비가역·고비용 | 중대 결함 대응 / 대거 삭제 / rollback / 배포·외부 발송 |

그 외 전부 — **모호 포함** — = 무조건 진행 (derived default 적용 + declare + 1줄 정정 초대). **"안전하니 일단 물어"(safe-direction default-to-ask) 금지.**

### 20.2 근거 (사용자 반복 directive 3회)

사용자 directive verbatim (3회 반복 지적 — 2026-05-26 / 2026-06-09 / 2026-06-19 KST): "묻는 건 ① 내 요구에 애매함이 있을 때 ② 확실하게 짚고 가야 할 때만. 그 외엔 무조건 진행. 중대한 결함·대거 삭제·rollback 같은 거 아니면 무조건 진행."

- over-asking 안전편향이 [CLAUDE.md](../../CLAUDE.md) "## 결정 · 대화 원칙" 자율 정책 ("합리적 default 가 자명하면 묻지 말고 진행") 을 위반.
- safe-direction-ask 가 기계적 default (문서화·착수·lane 진입·FIX 진행) 를 가치 측으로 오분류 → 정주행 중단 + 사용자 burden.
- pattern_count 3 ≫ [ADR-045](ADR-045-pmo-retro-batch-and-escalation.md) §D-9 threshold 2 (behavioral evidence — 사용자 반복 directive).
- [feedback_autonomous_until_decision](../../CLAUDE.md) 정합 — "진짜 가치 선택 분기에서만 정지, 정주행 중 lane 경계 checkpoint 금지".

### 20.3 무손상 invariant

본 redirect 는 **말 거는 빈도 (frequency / 어떤 결정에서 멈추느냐)** 만 좁힌다 — **말할 때의 풍부함 (richness) 은 그대로 보존** (§결정 15 frequency-richness 분리 invariant 정합). 무변경 항목:

- **§결정 1** frame mode 진입 4 step
- **§결정 3** Layer 1-4 cognitive enum (+ 5번째 cognitive layer 신설 금지 invariant)
- **§결정 4** sub-mechanism 2 종 (이전과 다르게 한 점 / 4 차원 enum)
- **§결정 2(c)** richness (3 줄 제약 거부 · 길이 자유 · "왜 / trade-off / 걸려있는 것" 배경 포함)
- **§결정 15** 3 touchpoint frequency-richness 본체 (touchpoint (a) 결과-명세 확인 = ask-trigger ①+③ 와 일치, 유지)

**5번째 cognitive layer 신설 아님** — 본 §결정 20 은 §결정 5 의 분류 규칙(모호 처리 방향) 변경이지 cognitive layer 추가가 아님 (§결정 3 Layer 1-4 enum count 불변, §결정 12.3 re-home invariant 정합).

### 20.4 ratchet 방향 — second weaken-direction amendment

본 amendment 는 "묻기 강화" 가 아니라 **"묻기 절제" (weaken-direction)** — Amendment 9 (DialogFidelityAgent sunset) 에 이은 두 번째 weaken-direction amendment.

- [ADR-058 §결정 5](ADR-058-adr-sunset-criteria-mandate.md) 약화 evidence-gate + [ADR-064 §결정 7](ADR-064-decision-principle-mandate.md) evidence-gated symmetric ratchet (강화/약화 양방향 1급 허용) 정합.
- `sunset_justification` = 3축 evidence object (frontmatter Amendment 10 — dead_mandate / verification_ground_redundancy / cost_vs_effect_zero + meta_policy_alignment). 사용자 반복 directive = behavioral evidence.
- 진짜 멈춰야 하는 결정 분기는 ask-trigger ②(진짜 가치 trade-off)·③(비가역·고비용) + touchpoint (a) 로 보존 — 약화 ≠ 안전판 제거. safe-direction 모호 자동 격상만 제거.

### 20.5 scope / 분류

- **doc-only fast-path Story** ([ADR-054](ADR-054-doc-only-story-fast-path.md), src/tests touch 0, 단일 PR).
- 4 file 동시 반영: 본 ADR (§결정 5 redirect 1줄 + 본 §결정 20 신설) + [skills/user-dialog-mode/SKILL.md](../../skills/user-dialog-mode/SKILL.md) §결정 5 결정 트리·touchpoint (a) scope 칸 + [CLAUDE.md](../../CLAUDE.md) "## 결정 · 대화 원칙" bullet 1개 + [docs/orchestrator-playbook.md](../orchestrator-playbook.md) §3.14 정합 (SSOT mirror).
- **playbook §3.14 SSOT mirror 정합 수정** (related-change, SSOT 추적): `docs/orchestrator-playbook.md` §3.14 의 (b) 사실/가치 분리 prose + 사실/가치 판단 결정 트리 표 (AMBIGUOUS 행) + touchpoint (a) scope 칸 3곳을 §결정 5 → §결정 20 redirect 와 1:1 일치시킴 ("모호 → 가치 측(safe direction) → AskUserQuestion" 폐기 → 모호 포함 ask-trigger 미해당 전부 진행). playbook 은 §결정 5/§결정 15 의 본문 SSOT mirror 이므로 동반 수정 없이는 ADR·skill 과 정면 모순 (반쪽 fix 회피) — 같은 PR 에 fold.
- mechanical lint (over-asking 자동 검출) = platform inherent limit (turn-final hook 부재, runtime 발화 시점 block 불가) — behavioral directive only, 별도 follow-up CFP scope.

### 20.6 sunset_justification: 3축 evidence object (weaken-direction)

본 Amendment 10 = weaken-direction (묻기 절제) — `sunset_justification` = null 아닌 3축 evidence object (frontmatter SSOT). Amendment 9 와 동형 (second weaken-direction). ADR-058 §결정 5 + ADR-064 §결정 7 evidence-gated symmetric ratchet 충족.

## §결정 21. dialog skip-offer 금지 — 생략을 "묻는" 것 자체 금지 (Amendment 11, CFP-2374)

> **[Amendment 11 / CFP-2374, 2026-06-20 KST]** 런타임에 Orchestrator 가 사용자에게 "생략할까요 / 간소화할까요 / 빠르게 갈까요 / 경량으로 갈까요" 를 **선택지로 제시하는 것을 금지**한다. 정식 풀 플로우는 비협상(non-negotiable) 기본값이므로 (ADR-127), 생략 여부는 애초에 결정 분기가 아니다 → `AskUserQuestion` 발화 대상이 아니다.

### 21.1 ask-trigger 정합 (§결정 5 / §결정 20 — CFP-2371 과 충돌 없음)

본 Amendment 는 §결정 20(Amendment 10, CFP-2371)의 ask-trigger 3종 한정과 **정합**한다 (충돌 없음):

- CFP-2371(§결정 20) = 질문 **빈도** 절제 (over-asking 안전편향 제거 — 모호 포함 ask-trigger 미해당 전부 진행).
- 본 Amendment 11 = 특정 질문 **종류**(skip-offer)의 PATH 폐지.
- "process 생략/단축" 은 ask-trigger ②(진짜 가치 trade-off — default 비자명) 로 오분류될 여지가 있으나, **정식이 비협상 기본값이므로 default 가 항상 정식으로 자명** → ask-trigger ② 미해당 → 묻지 않고 정식 진행. 둘 다 "불필요한 멈춤 제거" 방향으로 정합.

### 21.2 처리

- skip-offer 발견 시 (스킬이 "구현 실행 방식 선택지" / "경량 vs full" 등을 제시하더라도) → playbook §3.0.5 Subagent-Driven 자동 선택 정합으로 **자동 정식 측 채택** (묻지 않음).
- §결정 2(b) 결정 트리 / §결정 5 / §결정 20 의 ask-trigger 판정에서 "생략 여부" 는 derived default = 항상 정식 → `AskUserQuestion` 비대상.

### 21.3 ratchet 방향 — 강화 (skip-offer 제거)

본 Amendment 11 = 강화 방향 (생략 선택지라는 약화 옵션 제거). Amendment 9/10 의 weaken-direction(묻기 절제)과 달리, 본 Amendment 는 "정식성을 약화시키는 선택지 자체를 제거" = 강화 ratchet → `sunset_justification` 비대상 (ADR-058 §결정 5 약화 evidence-gate 불요). 무손상 — frame mode (§결정 1) / Layer 1-4 (§결정 3) / sub-mechanism (§결정 4) / §결정 2(c) richness / 3 touchpoint (§결정 15) / 5번째 cognitive layer 신설 금지 invariant 전부 보존. SSOT = [ADR-127](ADR-127-mandatory-full-flow-no-exemption.md) §결정 4.

## §결정 22. Epic 내 Story 전환 자율 진행 — 전환 지점 over-halt/over-ask 방지 (Amendment 13, CFP-2567)

> **[Amendment 13 / CFP-2567, 2026-07-04 KST]** Epic 을 한 세션에서 여러 child Story 로 진행할 때, Story N→N+1 전환 경계 (및 단일 Story Phase1→Phase2 전환) 에서 Orchestrator 가 **무발화로 정지(over-halt)** 하거나 **"다음 Story 진행할까요?" 확인 질문(over-ask)** 하는 것을 차단한다. 전환 = 자동 이어서 진행이 derived default, 멈춤·질문은 default 아님. 본 §결정 = 기존 §결정 15(3-touchpoint)·§결정 20(ask-trigger 3종) 를 **전환 지점에 적용 강화**(매핑)하는 것이지 두 enum 을 재정의·확장하지 않는다. carrier CFP-2567, issue https://github.com/mclayer/plugin-codeforge/issues/2567.

### 22.1 결정 요약 (D1 + D2)

**D1 — 전환 지점 정책 국소 명시**: 전환이 실제로 일어나는 지점 문서에 "Epic 내 Story 전환 = 자동 진행 default, 멈춤·질문 금지(정당 멈춤 3종 예외)" norm 을 국소 명시한다. 지금까지 이 norm 은 전역 dialog 규칙(§결정 15/20)에만 암묵 존재했고, 전환이 발생하는 그 지점 문서에는 미명시라 Orchestrator 가 통과 시점에 규칙을 surface 하지 못했다 (재발 원인, §18.4 incident (a) 정합). SSOT/mirror map:

| 문서 | 역할 |
|---|---|
| 본 §결정 22 (ADR-071) | normative decision SSOT |
| `skills/story-epic-flow-preflight/SKILL.md` Epic-flow child-transition point | PRIMARY local annotation (전환이 일어나는 그 지점 — AC-1) + §결정 18 disjoint-axis cross-ref (AC-2) |
| `docs/orchestrator-playbook.md` §3.4 / §1.2 | operational mirror 1-line + ref |
| `CLAUDE.md` "## 결정 · 대화 원칙" | 1-line peer bullet + ref |

**HARD GUARD**: `docs/orchestrator-playbook.md` §3.12 세션 재시작 Resume 경로의 "이 Epic 을 이어서 진행할까요?" confirmation = **out-of-scope, 무변경**. in-session 전환(본 §결정) ≠ session restart cold-resume — cold-resume 는 세션 context 소실 상태라 사용자 재확인이 정당(별도 경로). 두 경로 conflation 금지.

**D2 — 예방 강제층 신호 (2-channel, disjoint context-injection 창)**: **채널 1 (user-turn 창)** = `UserPromptSubmit` 예방 reminder hook(`hooks/story-transition-autonomy-reminder` + `.py`) 신설 — `hooks/hooks.json` UserPromptSubmit 배열에 5번째 entry append. skip-offer-reminder(§결정 21 / Amendment 11) 동형 hook-frame(ADR-115 5층 graceful degradation, 전경로 exit 0, JSON `additionalContext` emit) 재사용 = 구조 novelty ~0. reminder TEXT 는 전환 자율 진행 norm 을 매 user turn 에 salient 하게 유지하되, **정당 멈춤 3종(ask-trigger ① 요구 애매 / ② 진짜 가치 trade-off / ③ 비가역·고비용) carve-out 을 반드시 포함**해 over-suppression(EDGE-1) 을 차단한다. **채널 2 (autonomous 전환 창 — FIX-3)** = 기존 배선된 `hooks/pretooluse-agent-spawn-gate`(PreToolUse(Agent), 매 Agent spawn fire) 확장 — non-block `hookSpecificOutput.additionalContext` 로 전환 reminder inject(**NEVER deny**, 1차 출처 확정 code.claude.com/docs/en/hooks). Story k+1 lane-PL(RequirementsPL) spawn = UserPromptSubmit 가 dark 인 autonomous 전환 창에서 fire 하는 유일 lever = **본 Story 존재 이유**. over-fire 완화 = 간결 text + 가능시 payload `subagent_type` 판별(RequirementsPL-class → ~1×/Story). 두 채널은 disjoint 창(user-turn + agent-spawn)을 커버하며 둘 다 warning-tier 예방/priming only(감지·차단 아님).

### 22.2 axis disjoint declare (§18.5 형식)

본 §결정 22 = **transition-point autonomy** 축 (전환 경계에서 §결정 15/20 을 국소 surface + 예방 강제). axis mapping / disjoint:

- **§결정 15 (3-touchpoint frequency)** — 본 §결정 22 의 over-halt 절반이 매핑되는 mother enum. 전환 경계 무발화 정지 = 3-touchpoint 어느 항목(결과-명세 확인 / 사용자만 풀 차단 / 최종 완료 보고)도 아니면서 "진행"을 발화 touchpoint 로 오인해 멈춤 → §15.2 위반. **재정의 0** — touchpoint 추가 없이 전환 지점에 적용만 강화.
- **§결정 20 (ask-trigger 3종)** — 본 §결정 22 의 over-ask 절반이 매핑되는 mother enum. "다음 Story 진행할까요?" = ask-trigger ①②③ 어디에도 미해당 → §20.1 위반. **재정의 0** — trigger 추가 없이 전환 지점에 적용만 강화.
- **§결정 18 (session-swap reflex)** — **disjoint 축, cross-ref only, 재codify 금지**. session-swap("context 가득 → 별도 세션")은 §결정 18 anti-pattern 7종이 이미 codify. 전환 경계에서 co-occur(§18.4 incident 처럼)하나 별도 축 — 본 §결정은 over-halt/over-ask 절반만 신규 커버하고 session-swap 절반은 §결정 18 로 위임(중복 codification 회피, disjoint-axis invariant 보존).

### 22.3 closed-enum 무손상 명제 (AC-5 핵심)

**본 §결정은 §결정 15 3-touchpoint enum / §결정 20 ask-trigger 3종 enum 에 member 를 추가하지 않는다.** "Story 전환 진행 확인" 은 어느 enum 에도 등재되지 않으며(= 발화 정당 사유가 아니며), 본 §결정은 그 **비-등재 상태를 전환 지점에서 surface + 예방 강제**할 뿐이다. 따라서:

- §15.5 / §16.6 closed-enum 확장 규약(강화 ratchet + 별도 CFP + Story §1 사용자 승인 의무)은 **미발동** — touchpoint 추가 0, trigger 추가 0, 사용자 발화 burden 증가 0.
- §결정 15/18/20/21 의 closed-enum **텍스트 무변경**(재정의 0). D2 가 새 정당 touchpoint 를 신설하지 않는다 — 신설 시 §결정 15 enum 확장 = 위반이나, 본 §결정은 "미등재 = 발화 부당" 을 확정·강제하는 정반대 방향.
- 5번째 cognitive layer 신설 아님 (§결정 3 Layer 1-4 enum count 불변) — D2 hook = mechanism 추가이지 cognitive layer 추가 아님 (§결정 12.3 re-home invariant / §15.3 family pattern 정합).

### 22.4 D2 lever 실효 범위 + hollow-gate 회피 (AC-3 / AC-4)

D2 강제층은 **runtime 발화 前 hard-block 이 아니다** (§22.6 platform-limit). 실현 lever 의 정직한 실효 범위:

| lever | tier | 실효 범위 | 한계 | 채택 |
|---|---|---|---|---|
| (a) D1 정책 명시 | 정책 | **가장 강함** — 전환 지점에 norm 을 못박아 Orchestrator self-governance 근거 제공 | 기계 강제 아님(behavioral) | ✅ (D1) |
| (b) UserPromptSubmit 예방 reminder (신규 sibling hook) | warning(예방) | 매 user turn(user-turn 창)에 전환 자율 norm 을 salient 하게 유지 (execution-backed test) | autonomous run 중 Story 간 전환에는 **re-fire 안 함**(그 사이 user prompt 부재) / 감지·차단 안 함 / payload 에 Epic/Story state 없음 | ✅ (D2) |
| (e) PreToolUse(Agent) additionalContext (pretooluse-agent-spawn-gate 확장, FIX-3) | warning(예방/priming) | **autonomous 전환 창(agent-spawn)에서 fire** — Story k+1 lane-PL(RequirementsPL) spawn 포함(UserPromptSubmit dark 구간에 도달하는 유일 lever). non-block `additionalContext` 전환 reminder inject(**NEVER deny**, 1차 출처 확정) | 매 Agent spawn(intra-Story 포함) fire → over-fire(완화: 간결 text + 가능시 `subagent_type`=RequirementsPL-class 판별 → ~1×/Story) / no-spawn over-halt 못 잡음 = priming 이지 감지 아님 / payload 에 Epic/Story state 없음 | ✅ (D2) |
| (c) Stop 사후 advisory | 가장 약함 | 이론상 turn-END 사후 over-ask 문구 lint | ADR-115 §결정 2 record-only — over-ask 감지에 **미사용**(§22.5) | ❌ |
| (d) Stop force-continue | — | over-halt 사후 교정 lever(실재) | **REJECT** — §22.5 (정당/부당 정지 semantic 구분 불가 + ADR-115 §결정 2 platform-broken) | ❌ |
| (f) SubagentStop | — | subagent 완료(전환 경계)서 fire | **REJECT** — Stop-family 동일 platform-broken(#10412/#55754 + reason Claude 미전달) + 정당/부당 정지 구분 불가 → 개입 불가(Stop 동일 기각 basis) | ❌ |

**hollow-gate 회피 논증**: D2 는 "감지 gate" 가 아니라 **예방(prevention) + surface** 다. D2 를 "over-halt/over-ask 감지 lint" 로 팔면 (i) **over-halt(무발화)** 는 tool call·발화가 전무해 어떤 hook 도 감지 불가 = 원천 미검출(§22.6), (ii) 정당 ask 를 오탐해 alert fatigue → 검사연극. 따라서 본 §결정은:

- **AC-3 documented gap**: over-halt(무발화) = fire 조건 자체가 없음 = true-positive test 불가(근본적 untestable). over-ask "전환 지점 감지" = reminder 는 예방일 뿐 감지 아님. 이 두 blind-spot 을 커버되지 않는 gap 으로 **명시**(감지 주장 금지).
- **AC-4 over-suppression 억제**: warning-tier 시작(ADR-060 §결정 5) + reminder TEXT 의 정당 멈춤 3종 carve-out(§22.1 D2) = 구조적으로 false-positive suppression 불가 — hook 이 `additionalContext` append-only advisory 라 발화·정지를 물리적으로 막지 못하므로 정당 멈춤을 억제할 능력 자체가 없다.

### 22.5 Stop force-continue 재평가 결론 — REJECT (ADR-115 §결정 2)

over-halt 사후 교정 lever 로 **Stop hook force-continue(block/continue)** 가 기술적으로는 실재하나(turn-END fire), 본 §결정은 이를 **채택하지 않는다**. dual reason:

1. **semantic (결정적)** — Stop hook 은 정지의 정당성을 구분할 수 없다. 정당 멈춤(ask-trigger ③ 비가역·고비용 등)과 부당 over-halt 를 hook 이 판별 불가 → force-continue 는 **정당 멈춤까지 뚫는 over-suppression = active harm**(EDGE-1 / Researcher C5 automation-bias 정합). 자동 진행이 wrong-direction 을 silent 통과시키는 것은 새 결함.
2. **platform (ADR-115 §결정 2)** — Stop block(continue) 은 plugin-distributed mode 에서 broken(#10412) + 50분 세션 소진(#55754) + 결정 사유가 Claude 에 미전달. codeforge 규약상 Stop hook = **advisory record-only**.

∴ Stop force-continue REJECT. §결정 2 record-only 보존, **ADR-115 Amendment 없음** (본 §결정은 ADR-115 를 재확인만 — 재평가 후 유효).

### 22.6 ASM-2 platform-limit 재확인

D2 강제층은 Orchestrator 발화를 hook 으로 물리적으로 막을 수 없다:

- **PreToolUse(AskUserQuestion) 미지원** — `anthropics/claude-code#15872` CLOSED/NOT_PLANNED (외부 1차 출처 확정, 요구사항리뷰 게이트 CONFIRMED). pre-utterance block hook 부재.
- **over-halt(무발화, no-spawn) 순간 = 어떤 lever 도 correct 불가** — turn-END 무발화 정지 시 Stop/SubagentStop 은 **fire 하나** plugin-broken block(#10412/#55754) + reason Claude 미전달 + 정당/부당 정지 구분 불가로 **개입 불가**. PreToolUse(Agent) 는 spawn 이 없어(no-spawn) **fire 안 함**. UserPromptSubmit 도 user prompt 부재로 **fire 안 함**. ∴ over-halt 를 그 순간 correct 하는 lever 없음 = **prevention/priming only**(두 injection 창에 norm 을 salient 유지해 애초에 over-halt 확률↓, 근본 blind-spot AC-3).
- §결정 20.5 "runtime 발화 前 hard-block 불가, behavioral directive only" = 재확인, 유효.

∴ D2 = 정책 명시(D1) + 예방 reminder(warning-tier) + surface 조합으로 한정 (hard-block 기대 금지).

### 22.7 module placement 요지

- D2 = **신규 sibling hook** `hooks/story-transition-autonomy-reminder`(bash) + `.py`(self-contained stdlib, pattern A). skip-offer-reminder 확장 아님 — 별도 mother ADR(§결정 22 vs §결정 21) + 별도 governance 축, one-concern-per-hook 정착 패턴. shared reminder-base 추출 금지(YAGNI, fail-isolation).
- `hooks/hooks.json` UserPromptSubmit 배열 5번째 entry append. `run-hook.cmd` = generic basename dispatcher (수정 불요). leaf hook — inbound/outbound module dep 0, stateless, harness-driven.
- **D2 채널 2 (FIX-3)** = `hooks/pretooluse-agent-spawn-gate`(PreToolUse(Agent), `hooks.json` 에 이미 배선된 matcher `Agent`) **EDIT** — 전환 reminder `additionalContext` non-block inject 추가(**NEVER deny**, 기존 4-block spawn-format warning 로직 무손상). 신규 hook 파일 아닌 기존 gate 확장 = 구조 novelty 0. over-fire 완화 = 간결 text + 가능시 payload `subagent_type` 판별. 채널 1(신규 sibling hook, UserPromptSubmit)과 disjoint fire 창 — 별도 matcher 등록으로 상호 독립.
- consumer 전파 = out-of-scope (EDGE-4, 후속 CFP).

### 22.8 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 13 = **additive 강화** (전환 지점 자율 진행 norm surface + 예방 reminder 추가 = forcing function 강화 ratchet). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 evidence-gate 미적용. Amendment 11/12 에 이은 third strengthen-direction amendment (`sunset_justification: null` family).

무손상 invariant (전부 보존): frame mode 4 step(§결정 1) / Layer 1-4 cognitive enum(§결정 3) / sub-mechanism 2 종(§결정 4) / §결정 2(c) richness / 3 touchpoint frequency-richness(§결정 15) / natural-language trigger table(§결정 16) / lane back-translation gate(§결정 17) / session-swap anti-pattern 7종(§결정 18) / mid-turn glossary(§결정 19) / ask-trigger 3종(§결정 20) / skip-offer 금지(§결정 21) / 5번째 cognitive layer 신설 금지 invariant. §결정 15/20 enum member 추가 0 (전환 지점 적용 강화만).

`sunset_justification: null` 적격 (§21.3 family pattern 정합 — Amendment 11/12/13 strengthen-direction).

## §22.9 §결정 22 scope 일반화 + consumer 전파 (Amendment 14, CFP-2573)

> **[Amendment 14 / CFP-2573, 2026-07-05 KST]** ADR-144(stop taxonomy 3축 + decision-null pause) §결정 3(L2) + §결정 6(L6) realization. Amendment 13(§22.1 D2)이 reminder TEXT 를 "Story 전환 지점" 에 한정했던 scope 를 **"모든 자명-진행 지점"** 으로 넓히고, §22.7 이 out-of-scope 로 뒀던 **consumer 전파** 를 해소한다. carrier CFP-2573, issue https://github.com/mclayer/plugin-codeforge/issues/2573.

### 22.9.1 scope 일반화 (L2 — reminder TEXT broaden only)

D2 2채널의 reminder **TEXT** 를 아래 자명-진행 지점 전부를 salient 하게 유지하도록 넓힌다:

- **전환** (Story N→N+1, Phase1→Phase2 — Amendment 13 기존 scope)
- **lane 경계** (lane PASS 후 다음 lane 자동 진입)
- **완료-후** (작업 단위 final report 후 backlog 자동 발굴·진행)
- **vague-pause 금지** ("한 숨 쉬어가자" 류 decision-null verbalized 정지 = 발화 정당 사유 부재 — ADR-025 Amendment 3 §결정 7 illegal 표 6번째 행의 dialog-side priming mirror)

두 채널 모두 TEXT+docstring 만 broaden — **채널 1** = `hooks/story-transition-autonomy-reminder.py`(UserPromptSubmit user-turn 창), **채널 2** = `hooks/pretooluse-agent-spawn-gate`(PreToolUse(Agent) autonomous 창).

### 22.9.2 hook public identity 무변경 (ModuleArch binding)

- **신규 hook 파일 0** — 기존 hook 의 파일명 · `hooks/hooks.json` UserPromptSubmit 5번째 entry · `run-hook.cmd` generic dispatcher · §22.7 back-refs 전부 stable(public id 불변).
- 한 hook 의 TEXT 를 넓혀도 concern 은 여전히 하나(**autonomous-progress priming**) = one-concern-per-hook 정합. §22.7 "shared reminder-base 추출 금지" 의 의미 = cross-hook **CODE** abstraction 금지(YAGNI/fail-isolation, hook 은 self-contained stdlib zero cross-import 유지)이지 TEXT-scope 금지가 아니다 → **TEXT broadening = §결정 22 generalization, one-concern-per-hook intact**.

### 22.9.3 closed-enum 무손상 + carve-out 보존 (§22.3 상속)

- §결정 15 3-touchpoint / §결정 20 ask-trigger 3종 enum 에 **member 추가 0**. "자명-진행" 은 어느 enum 에도 미등재(= 발화 정당 사유 아님) 상태를 **더 많은 지점에서 surface** 할 뿐 — §15.5/§16.6 closed-enum 확장 규약 미발동.
- reminder TEXT 의 정당 멈춤 3종(ask-trigger ① 요구 애매 / ② 진짜 가치 trade-off / ③ 비가역·고비용) **carve-out verbatim 보존**(over-suppression EDGE-1 차단).
- **NEVER block** — GAP-1/GAP-2 순간엔 어떤 hook 도 fire 안 함(documented blind-spot, ADR-144 §결정 7). reminder = `additionalContext` append-only advisory 라 발화·정지를 물리적으로 막을 능력 자체가 없다(§22.4 AC-4 논증 상속). warning-tier 예방/priming only, 감지·차단 아님.

### 22.9.4 consumer 전파 (L6)

- reminder TEXT 확장을 `hooks/hooks.json` 배선으로 두면 plugin 설치 시 **consumer 자동전파**(overlay 변경 0, CFP-2456 skip-offer 선례 동형). §22.7 "consumer 전파 = out-of-scope(EDGE-4, 후속 CFP)" 를 본 Amendment 가 해소.
- reminder TEXT 는 **STATIC**(runtime value interpolation 금지, no PII).
- consumer **telemetry sharing** = opt-in default-false 보존(ADR-043 §결정 1). **정직 nuance**: 로컬 ledger append 는 wrapper+consumer 양쪽에서 이미 ungated(기존 CFP-1743 behavior) — 새 flip 아님. wrapper always-on ≠ global default flip(ADR-144 §결정 6).

## §결정 23. 요구사항 lane intake 항상 declare touchpoint (4번째) + §결정 20 lane-scoped carve-out + design-entry 확정 gate 발화 touchpoint (Amendment 15, CFP-2725)

> **[Amendment 15 / CFP-2725, 2026-07-17 KST]** 요구사항 lane 사용자 대화 프로세스 정식화 — 신규 [ADR-159](ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md) (요구사항 lane enrichment 일급 목적 + design-entry 확정 gate SSOT) 의 **발화 frequency 축 짝 wiring**. 본 §결정 = ADR-071 이 소유하는 dialog frequency 축(§결정 15/20/22)에 요구사항 lane-scoped 강화를 3부(a/b/c)로 적용한다. terminal event·counter 축 = ADR-077 Amendment 1 / lane 시퀀스·확정 위치·내부적합 검증축 = ADR-125 Amendment 3 (짝, 본 §결정 밖). carrier CFP-2725, issue https://github.com/mclayer/plugin-codeforge/issues/2725.

### 23.1 (a) intake 항상 declare = 4번째 touchpoint (§15.5 closed-enum 확장 규약 첫 실사용)

§결정 15 의 3-touchpoint closed enumeration(§15.2)에 **요구사항 lane-scoped 4번째 touchpoint** 를 추가한다:

| touchpoint | 발화 사유 | 분류 |
|---|---|---|
| **(d) 요구사항 intake 배경·의도 재진술 declare** (요구사항 lane 한정) | 새 요구사항 접수 시 이해한 배경·의도를 먼저 제시·재진술하고 확인 왕복을 시작 (자명해 보여도 생략 없음) | **mandatory DECLARE** (derived-default 재진술 — §결정 16 no-dialog-reflex derived-default 동형). ADR-039 inline whitelist 1번 entry(사용자 dialog) scope 안 작동 |

**§15.5 확장 규약 준수 (첫 실사용)**: 본 4번째 touchpoint 추가는 §15.5 closed-enum 확장 규약을 정확히 발동한다 — (1) ADR-064 §결정 7 top-down ratchet 강화 방향(touchpoint 추가 = 발화 frequency 증가) (2) 별도 CFP 신설 의무 = CFP-2725 (3) Story §1 사용자 explicit 승인 의무 = CFP-2725 §1 사용자 확정 선호 4항("발동 기준 = 항상" verbatim). §15.5 가 사전에 마련해 둔 정규 확장 경로의 **첫 실사용**이며 closed-enum 우회가 아니다.

**scope = 요구사항 lane 한정**: 본 touchpoint (d)는 요구사항 lane intake 에만 적용된다. 타 lane 일반화 명시 금지 — 다른 lane 은 기존 3-touchpoint(a/b/c) + §결정 20 ask-trigger 3종 그대로.

### 23.2 STRENGTHEN frame — mandatory DECLARE ≠ mandatory ASK (핵심 명제, 원천 회피)

touchpoint (d) 는 **mandatory DECLARE 이지 mandatory ASK 가 아니다.** 이 구분이 §결정 20(ask-trigger 3종 한정)과의 충돌을 원천에서 해소한다:

- **DECLARE 패턴**: intake 왕복 = 이해한 배경·의도의 derived-default 재진술 + "이의 없으면 진행" 고지. trivial 최소형 = 재진술 1~3줄 + 열린 질문 0~1개 — **명시 답변 대기 없이 진행 가능**(사용자가 정정하면 반영). §결정 16 natural-language action trigger 의 no-dialog-reflex derived-default 와 동형(발화하되 멈춰 묻지 않음).
- **ASK 로 escalate 하는 경우**: 요구가 모호(ask-trigger ① 해당)하면 그때 실제 `AskUserQuestion` 으로 escalate. 즉 touchpoint (d) 는 "항상 declare + 모호할 때만 ask" 이지 "항상 ask" 아님.
- **§결정 20 충돌 해소**: §결정 20 이 폐기한 것은 "safe-direction default-to-ask(모호하니 일단 물어)" 다. touchpoint (d) 는 ask 를 늘리지 않고 declare 를 강제하므로 §결정 20 본체(ask-trigger 3종 한정)와 직교·정합. 5번째 cognitive layer 신설 아님(§결정 3 Layer 1-4 enum count 불변) — touchpoint(mechanism) 추가이지 cognitive layer 추가 아님(§12.3 re-home / §15.3 family pattern 정합).

### 23.3 (b) §결정 20 lane-scoped carve-out 명문 (요구사항 lane 한정, 타 lane 일반화 금지)

§결정 20 에 요구사항 lane 한정 carve-out 을 **명문**한다:

- **carve-out**: 요구사항 lane intake 는 "항상 declare"(touchpoint (d)) — §결정 20 ask-trigger 3종 한정의 요구사항 lane-scoped 강화.
- **§결정 20 본체 보존 + 타 lane 일반화 금지**: 본 carve-out 은 요구사항 lane 에만 적용되며 타 lane(설계·구현 등)으로 일반화 명시 금지. §결정 20 본체(전역 ask-trigger 3종 한정 — over-asking 안전편향 제거)는 무변경. 이념적 기반 = §15.1 "how(구현 과정) 중간 보고는 억제, what(요구 명세) disambiguation 은 억제 비대상" — 요구사항 lane intake = what disambiguation 의 lane-scoped frequency 강화(richness 무감소, frequency-richness 분리 invariant 정합).

### 23.4 (c) design-entry 확정 gate = 발화 touchpoint + §결정 22 정당 멈춤 carve-out

요구사항리뷰 PASS 후·설계 진입 직전 사용자 최종 확정 요청(ADR-159 결정 3, informed sign-off)을 발화 touchpoint 로 명문화한다:

- **성격 = touchpoint (a) 결과-명세 확인**: 확정 요청 = 사용자가 선언한 결과(요구 명세)의 최종 확인 + ask-trigger ①(요구 애매 잔량 해소)/③(비가역·고비용 — 설계 = 첫 비가역 지점). 신규 touchpoint 신설 아님 — 기존 touchpoint (a) 의 frequency 영역(설계 진입 경계) 적용.
- **§결정 22 정당 멈춤 carve-out 명시(over-halt 오탐 차단)**: 사용자 최종 확정 대기 stop = ask-trigger 정당 stop(payload>0, [ADR-144](ADR-144-orchestrator-autonomy-stop-taxonomy.md) A1). §결정 22 정당 멈춤 3종(ask-trigger ①②③) carve-out 에 **명시적 귀속** — §22.1 D2 transition-autonomy hook 이 "요구사항 → 설계 진입 지점" 을 over-halt(자명-진행 위반)로 오탐하지 않도록 명문화. §결정 22 정당 멈춤 3종 carve-out **verbatim 무변경**(EDGE-1 over-suppression 차단 상속). in-session 전환 자율 진행(§결정 22) 과 design-entry 확정 대기(정당 멈춤)는 disjoint — 확정 대기는 §결정 22 예외 carve-out 안.

### 23.5 무손상 invariant (전부 보존) + advisory ceiling

무손상 invariant: frame mode 4 step(§결정 1) / Layer 1-4 cognitive enum(§결정 3) / sub-mechanism 2 종(§결정 4) / §결정 2(c) richness / 3 touchpoint frequency-richness 본체(§결정 15 §15.1 how·what 경계) / ask-trigger 3종 본체(§결정 20) / skip-offer 금지(§결정 21) / §결정 22 D1·D2 2-channel 구조·정당 멈춤 3종 carve-out / 5번째 cognitive layer 신설 금지 invariant — 전부 보존. touchpoint 추가 = 4번째(요구사항 lane-scoped, §15.5 규약 준수), ask-trigger enum member 추가 0.

**advisory ceiling(정직)**: design-entry 확정 gate 의 기계 검증 = "확정 기록·규칙의 presence 까지"(ADR-159 결정 6). 발화 touchpoint 명문화 = behavioral directive — turn-final hook 부재 platform 한계로 runtime 발화 시점 hard-block 불가(§20.5 / §22.6 재확인). "기계 강제 100%" over-claim 금지.

### 23.6 sunset_justification: null (ADR-058 §결정 5 정합, fifth strengthen-direction)

본 Amendment 15 = **additive 강화** (§15.5 확장 규약 준수 4번째 touchpoint 추가 = 발화 frequency 증가 강화 ratchet, 요구사항 lane-scoped + §결정 20 carve-out 명문 + design-entry gate §결정 22 carve-out 명시). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 evidence-gate 미적용. Amendment 11/12/13/14 에 이은 fifth strengthen-direction amendment(`sunset_justification: null` family). mandatory DECLARE — mandatory ASK 신설 아님(사용자 burden 은 declare 최소형으로 완화). ADR-159 SSOT / ADR-077 Amendment 1(terminal event·counter) / ADR-125 Amendment 3(확정 위치·내부적합) 짝.

## §결정 24. Session-swap controlled-path — 자족 handoff 프롬프트 동반 시 전환 권유 허용 (Amendment 16, CFP-2742)

> **[Amendment 16 / CFP-2742, 2026-07-18 KST]** context/메모리 포화 등으로 세션 전환을 권유하려는 순간, Orchestrator 가 **자족(self-contained) handoff 프롬프트를 선제 생성·동반**하면 전환 권유를 **조건부 허용**한다. handoff 프롬프트가 §결정 18 이 우려한 **맥락 손실·재도출 비용을 제거**하므로, "무조건 anti-pattern" 을 handoff-present 케이스에 한해 controlled-path gate 로 격상한다. 본 §결정 = **§결정 18 의 첫 weaken-direction amendment**(prohibition scope 축소, ADR-058 §결정 5 evidence-gate 충족). §결정 18 anti-pattern 7종 enum·정당 2-trigger 표는 **무변경**(본문 immutability — §18.1 상단 1-line cross-ref pointer만 additive). carrier CFP-2742, issue https://github.com/mclayer/plugin-codeforge/issues/2742.

### 24.1 결정 요약 (controlled-path 정의)

- **controlled-path 정의**: 전환 권유 발화 **前** 자족 handoff 프롬프트(§24.2 6 필수요소) 생성·동반 = 전환 권유 **허용**. 생성 주체 = 전환을 권유하려는 Orchestrator 본인(선제·先制 생성 — 사용자 요청 대기 아님, §1 요구 #1 "일단 생성" verbatim).
- **bare reflex 전환 = 여전히 차단**: handoff 프롬프트 **미동반** 전환 권유("context 가득 → 새 세션에서" 류 reflex)는 §결정 18 anti-pattern 7종 그대로 발화 차단. carve-out 은 **handoff-present 케이스 한정** — anti-pattern 자체 무력화 아님.
- **격상 근거**: handoff 프롬프트가 §18.1/§18.3 우려의 실체(cached state 소실 → 새 세션 재도출 비용)를 제거하면, 그 케이스에서 "무조건 차단" 의 정당 근거가 소멸(§24.8 sunset_justification `dead_mandate`). 근거가 남아 있는 handoff 미동반 케이스는 차단 유지 → **부분 약화(handoff-present 만 허용)**.

### 24.2 handoff 6 필수요소 + 자족성 2축 (ADR-085 §결정 9 specialization)

전환 권유 동반 handoff 프롬프트가 담아야 하는 **6 필수요소** (§2.2 손실 대상의 operationalization — 이 전량 이월이 "재도출 비용 0" 성립 조건):

| # | 요소 | 무엇 |
|---|---|---|
| ① | 진행 Story/PR·Epic 번호 | 어떤 작업 단위인지 — Story key + 활성 PR + (해당 시) Epic 번호 |
| ② | 완료 vs 남은 lane·단계 | 어느 lane·Phase 까지 끝났고 어디서 이어받는지 |
| ③ | worktree·브랜치 경로 | 작업 중 worktree 절대경로 + feature 브랜치명 |
| ④ | 기결정 = 재논의 금지 목록 | 이미 확정된 결정(재열지 말 것) — 새 세션 re-litigation 차단 |
| ⑤ | 이번 세션 gotcha | 이 세션에서 부딪힌 함정·주의점(반복 회피) |
| ⑥ | 다음 세션 첫 액션 1문 | 붙여넣은 직후 할 첫 행동 한 문장 |

**자족성 2축**: (i) **현세션 참조 0** — 다음 세션 Orchestrator 가 현재 세션을 전혀 참조하지 않고(0-context) 재개 가능 (ii) **복붙 1회** — 사용자가 그대로 붙여넣기만 하면 완결.

**ADR-085 §결정 9 4-rule specialization (재발명 금지 cross-ref)**: 위 6요소 + 2축 = [ADR-085](ADR-085-multi-session-collaboration-protocol.md) §결정 9 multi-session prompt design 4-rule(① self-contained end-to-end ② session 사이 axis-disjoint ③ sequential dependency → 한 session ④ copy-paste 준비 = context+scope+preflight+done+reference)의 **구체화(specialization)** 이며 새 원칙 창설 아님. 본 §결정은 §결정 9 rule 4(copy-paste 자족)를 session-swap 축에 적용한다.

### 24.3 Q1 — 모든 전환 권유에 handoff 의무 (trigger SET 무변경)

- **Q1 = YES**: handoff 의무는 **모든** 전환 권유에 적용된다 — 정당 2-trigger([ADR-053](ADR-053-structural-change-restart-prerequisite.md) 구조 변경 재구동 / [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) 모델 fallback) 발화까지 포함. **근거**: 맥락 손실·재도출 비용은 전환 이유(WHY)와 무관하게 발생한다 — 정당 전환이라도 handoff 없이 넘어가면 새 세션이 재도출한다.
- **trigger SET 무변경 (AC-4 정합)**: 정당 2-trigger·anti-pattern 7종 **enum member 추가·삭제 0**. handoff 는 기존 trigger 집합에 얹히는 **직교(orthogonal) cross-cutting 의무** — 정당 trigger 는 "handoff 동반 + 전환 허용", anti-pattern 은 "handoff 동반 시 controlled-path 허용 / 미동반 시 차단" 으로 각 trigger 의 처리에 handoff 요건만 부착. 새 trigger 종류를 만들지 않는다.
- **/compact·MEMORY.md 슬림화 대체 path 무손상**: §18.3 정당 path(`/compact` + 인덱스 슬림화 + harness auto-compress) 는 controlled-path 신설과 무관하게 보존 — controlled-path 는 전환을 **장려하지 않는다**, "전환이 발생하면 handoff 의무화" 할 뿐(skip-offer §결정 21 정신 정합 — 전환 장려 아님).

### 24.4 forced-continuation vs planned-lane-split disjoint 경계 (P2-1)

controlled-path 의 scope 를 인접 개념과 명확히 분리한다:

| 축 | 정의 | §결정 24 관계 |
|---|---|---|
| **forced-continuation** (§결정 24 scope) | context/memory 포화로 mid-work 에서 **동일 sequential stream** 을 fresh 세션이 이어감 (세션 A 소진 → B 가 A 멈춘 지점 continue, 같은 Story·같은 in-progress lane) | **controlled-path 적용 대상** |
| **planned-lane-split** (§결정 24 scope 밖) | 한 Story 의 lane 을 병렬/단계로 **인위 분할**해 여러 세션에 pre-assign ("Session 1 = step1-3, Session 2 = step4" 류) | **ADR-085 §결정 9 rule 1 이 금지** — controlled-path 미허가 |

- **disjoint**: 하나의 stream 을 이어받는 것(continuation) ≠ 분할된 lane 을 사전 배정하는 것(pre-division). ADR-085 §결정 9 rule 1("각 session = self-contained end-to-end, artificial lane split reject")은 **후자**를 금지하지 전자를 금지하지 않는다.
- handoff 프롬프트는 rule 4(copy-paste 자족)를 충족하고 rule 1 의 정신(fresh 세션이 **남은 작업 전체**에 대해 self-contained)도 만족한다. **controlled-path 는 planned-division 을 허가하지 않는다** — rule 1 은 여전히 유효하며, 본 §결정은 lane 을 나눠 병렬 세션에 뿌리는 것을 허용하지 않는다.

### 24.5 consumer 전파 vehicle — Phase 2 설계 명세 (본 Phase 1 미구현)

요구 #2("memory 아닌 consumer 전파")의 자동 도달 vehicle. **본 Phase 1 = 설계 명세만**(hook 파일·hooks.json 미생성) — 실배선 = Phase 2 별 PR.

- **신규 sibling hook** `hooks/session-swap-handoff-reminder`(bash dispatcher) + `.py`(body): `story-transition-autonomy-reminder`(§22.1 D2 채널 1) 동형 hook-frame — [ADR-115](ADR-115-runtime-hook-enforcement.md) 5층 graceful degradation, self-contained stdlib(zero cross-import), **全경로 exit 0 fail-open**, `UserPromptSubmit` `additionalContext` emit, TEXT = **STATIC**(runtime value interpolation 금지, no PII).
- **hooks.json 6th UserPromptSubmit entry**: 기존 5 entry(korean-english-recovery / bootstrap-first-gate / skip-offer-reminder / deferred-recovery-reminder / story-transition-autonomy-reminder) 무손상 co-fire + 6번째 append.
- **신규 hook 근거 (별도 sibling 정당)**: §결정 18(session lifecycle reflex) ⊥ §결정 22(transition autonomy) **disjoint** (§22.2 line "§결정 18 disjoint, cross-ref only, 재codify 금지" 무손상) + one-concern-per-hook(§22.7) — session-swap-handoff priming 은 transition-autonomy 와 별도 concern 이므로 기존 hook TEXT 확장 아닌 신규 sibling 이 정합.
- **consumer 자동전파**: reminder TEXT 를 `hooks/hooks.json` 배선으로 두면 plugin 설치만으로 consumer Orchestrator 세션 자동전파([ADR-144](ADR-144-orchestrator-autonomy-stop-taxonomy.md) §결정 6 L6, overlay 변경 0, CFP-2456/CFP-2573 선례 동형). CLAUDE.md 단독은 consumer 미도달(ADR-039 §결정 7 — wrapper 루트 CLAUDE.md consumer 세션 자동 로드 안 됨) → hook 배선 필수.
- **TestContractArch objection#1 (Phase 2 요건)**: sibling reminder hook(skip-offer / story-transition-autonomy)은 현재 dedicated self-test 0(§7.3 co-fire guard 로만 간접 cover). 신규 hook 은 이 under-coverage 를 상속하지 않는다 → Phase 2 는 **first-class dedicated self-test** `tests/scripts/test_session_swap_handoff_reminder.sh` 신설 + 신규 marker 를 기존 `tests/scripts/test_spawn_description_prefix.sh` §7.3 co-fire guard 에 추가.

### 24.6 advisory ceiling (정직 — hollow-gate 금지)

- **runtime hard-block 불가**: controlled-path 의 "handoff 프롬프트 동반" 요건은 runtime 발화 시점에 기계 강제되지 않는다 — GAP-1(pre-utterance hard-block: PreToolUse(AskUserQuestion) 미지원 #15872) / GAP-2(over-halt 실시간 검출) 는 platform 한계로 닫히지 않음([ADR-144](ADR-144-orchestrator-autonomy-stop-taxonomy.md) §결정 7, #15872/#10412/#55754).
- **priming/PRIMING 채널 only**: hook 은 `additionalContext` **priming** 이지 enforcement 아니다 — **배선됨 ≠ 규범 준수 증명**. Orchestrator 가 실제로 6요소 handoff 를 생성했는지는 runtime untestable.
- **over-claim 금지**: "100% 기계강제 / hard-gate / 닫았다" 주장 = 산출물 결함(ADR-119 검사연극 금지). 본 §결정은 예방(prevention)·surface 이지 감지 gate 아님(§23.5 / §22.6 advisory ceiling 선례 정합).

### 24.7 axis disjoint declare (§18.5 형식)

본 §결정 24 = **session lifecycle controlled-path** 축. axis disjoint / cross-ref:

- **§결정 22 (transition autonomy)** — **disjoint 축, cross-ref only, 재codify 0**. line 1285("§결정 18 disjoint, cross-ref only, 재codify 금지") **무손상**. §결정 22 = in-session Story 전환 자율 진행(전환 지점 over-halt/over-ask 방지), 본 §결정 24 = 세션 교체(swap) 시 handoff 인계 — 목적·대상 세션 disjoint. 두 "경계에서 상태 포착" 산출물의 요소 재사용(남은 lane·기결정)은 최적화이지 축 병합 아님.
- **§결정 18 (session-swap reflex)** — anti-pattern 7종 enum 텍스트·정당 2-trigger 표 **무변경(본문 immutability)**. 본 §결정은 §18.1 상단에 1-line cross-ref pointer만 additive(§결정 5 → §결정 20 redirect pointer 선례 동형) — enum 재정의·member 추가·삭제 0.
- **§결정 23 (요구사항 lane touchpoint)** — disjoint(요구사항 lane dialog frequency 축 ↔ session lifecycle 축). §결정 23 은 §결정 18 을 touch 하지 않고(§4.3 firsthand 확인), 본 §결정도 §결정 23 을 touch 하지 않음.

### 24.8 sunset_justification 4-key (ADR-058 §결정 5, WEAKEN, §결정 18 첫 weaken)

본 Amendment 16 = **weaken-direction (부분 약화)** — anti-pattern 7종의 "무조건 발화 차단" → "handoff 동반 시 조건부 허용" = prohibition scope 축소. §결정 18 의 **첫 weaken-direction amendment**(Amendment 7 = 강화 `null` 이었음). Amendment 9/10 에 이은 third weaken-direction amendment. ADR-058 §결정 5 약화 evidence-gate 적용 → `sunset_justification` = **null 아닌 4-key evidence object** (frontmatter Amendment 16 SSOT와 동일):

- **dead_mandate**: "무조건 차단" 이 우려한 재도출 비용은 handoff 6요소 전량 이월 시 handoff-present 케이스에서 소멸 → 그 케이스에 한해 "무조건 차단" 의 정당 근거 dead. 사용자 directive 2건(§1 요구 #1/#2) = behavioral evidence.
- **verification_ground_redundancy**: 무준비 전환 방지는 controlled-path 가 handoff 의무로 오히려 강화 — bare reflex(handoff 미동반)는 여전히 차단, 정당 2-trigger 도 handoff 부착. /compact·슬림화 대체 path 무손상.
- **cost_vs_effect_zero**: "무조건 차단" 을 handoff-present 케이스까지 유지하는 효과(전환 억제) < 비용(재도출 비용 0 인데 정당 인계형 전환까지 금지 → mid-work 정주행 불가). 보호 효과가 handoff-present 케이스에서 0 수렴.
- **meta_policy_alignment**: ADR-058 §결정 5(약화 evidence requirement) + ADR-064 §결정 7(evidence-gated symmetric ratchet, 강화/약화 양방향 1급) — §결정 18 첫 weaken, evidence-grounded 1급 허용(차단 아님). 사용자 §1 요구 #3 verbatim("anti-pattern 을 gated 경로로 격상") = 완화 프레이밍 정합.

**무손상 invariant**: frame mode 4 step(§결정 1) / Layer 1-4 cognitive enum(§결정 3) / sub-mechanism 2 종(§결정 4) / §결정 2(c) richness / 3 touchpoint(§결정 15) / ask-trigger 3종(§결정 20) / skip-offer(§결정 21) / §결정 22 D1·D2 2-channel 구조·정당 멈춤 carve-out / §결정 23 / 5번째 cognitive layer 신설 금지 invariant — 전부 보존. 정당 trigger 2종 + anti-pattern 7종 enum member 추가·삭제 0(controlled-path gate 만 신설).

## self-application top-down ratchet

본 ADR amendment 는 [ADR-064 §결정 7](ADR-064-decision-principle-mandate.md) top-down ratchet 정합 — 강화 방향만 허용 (scope 확장 / 강도 강화). 약화 방향 (`is_transitional: false → true` 다운그레이드 / 4 layer 축소 / 3 memory entry mapping 회수 / Sub-mechanism 2 차원 enum 축소 / **3 touchpoint enum 축소 — §결정 15 Amendment 4** / **trigger table 회수 — §결정 16 Amendment 5** / **§결정 17 back-translation gate 회수 — Amendment 6** / **§결정 18 session swap reflex anti-pattern 7종 enum 축소 — Amendment 7** / **§결정 19 mid-turn glossary lookup 의무 회수 또는 codename 15-batch 축소 — Amendment 8** / **§결정 2(c) richness 약화 — frequency 축소 ≠ richness 축소 invariant 위반**) 은 [ADR-058 §결정 5](ADR-058-adr-sunset-criteria-mandate.md) `sunset_justification` 의무로 **차단** (evidence 없을 때). 본 ADR-071 = ADR-064 ratchet 의 직접 carrier (mechanical version 승격 + scope 확장 = strict superset). Amendment 1/2/3/4/5/6/7/8 = `sunset_justification: null` family pattern.

**Amendment 9 (CFP-2236) = 첫 weaken-direction amendment**: ADR-064 §결정 7 이 CFP-1149 Amd 8 로 **evidence-gated symmetric ratchet** (강화/약화 양방향 1급 허용) 로 재정의 + ADR-058 §결정 5 가 `sunset_justification` 을 "약화 차단 logic" 이 아니라 "약화 evidence requirement" 로 재정의 (CFP-1149). 따라서 약화 방향 (DialogFidelityAgent §결정 12/13/14 + §17.4.3 sunset) 은 `sunset_justification` 이 **null 이 아닌 3축 evidence object** (dead_mandate / verification_ground_redundancy / cost_vs_effect_zero) 를 충족하면 **1급 허용** (차단 아님). 단 약화 = 부분 §결정 sunset 한정 — `is_transitional: false` 본체 + dialog governance 골격 (frame mode + 4 layer + 3 touchpoint) 무손상 (ADR 전체 강등 아님).

**Amendment 10 (CFP-2371) = second weaken-direction amendment**: §결정 5 결정 트리의 `AMBIGUOUS → 가치 측 분류(safe direction) → AskUserQuestion` 룰 redirect (§결정 20 — ask-trigger 3종 한정, 모호 포함 ask-trigger 미해당 전부 진행). over-asking 안전편향 제거 = 묻기 절제 (약화 방향). `sunset_justification` = 3축 evidence object (사용자 반복 directive 3회 = behavioral evidence) 충족 → evidence-gated symmetric ratchet 1급 허용. 무손상 — frame mode (§결정 1) / Layer 1-4 (§결정 3) / sub-mechanism (§결정 4) / §결정 2(c) richness / 3 touchpoint (§결정 15) 골격 보존, 5번째 cognitive layer 신설 아님 (§결정 5 분류 규칙 변경, layer count 불변).

**Amendment 11 (CFP-2374) / Amendment 12 (CFP-2392) / Amendment 13 (CFP-2567) / Amendment 14 (CFP-2573) / Amendment 15 (CFP-2725) = 강화 방향 `sunset_justification: null` family** — skip-offer PATH 폐지 (§결정 21) / MEMORY.md 슬림화 mechanism deferred 해제 resolve (§18.7 resolved_carrier ADR-129) / Epic 내 Story 전환 autonomy surface + 예방 reminder (§결정 22) / §결정 22 scope 일반화(transition-only → 모든 자명-진행 지점 + vague-pause 금지) + consumer 전파 (§22.9, ADR-144 §결정 3/6 realization) / **요구사항 lane intake 항상 declare 4번째 touchpoint(§15.5 확장 규약 첫 실사용) + §결정 20 lane-scoped carve-out + design-entry 확정 gate §결정 22 정당 멈춤 carve-out (§결정 23, ADR-159 SSOT 짝)**. Amendment 9/10 의 weaken-direction 과 달리 다섯 다 정식성·자율 진행·요구 disambiguation 강화 방향 → ADR-058 §결정 5 약화 evidence-gate 비대상. §결정 22 / §22.9 = §결정 15/20 enum member 추가 0. **§결정 23 = §결정 15 에 요구사항 lane-scoped 4번째 touchpoint 추가(§15.5 확장 규약 준수 — 별도 CFP + Story §1 사용자 explicit 승인 충족)이나 §결정 20 ask-trigger enum member 추가 0(mandatory DECLARE≠ASK)** — cognitive layer count 불변 (touchpoint = mechanism 추가, cognitive layer 추가 아님).

**Amendment 16 (CFP-2742) = third weaken-direction amendment (§결정 18 첫 weaken)**: §결정 24 신설 — session-swap controlled-path(자족 handoff 프롬프트 동반 시 전환 권유 허용). §결정 18 anti-pattern 7종의 "무조건 발화 차단" → "handoff 동반 시 조건부 허용" = prohibition scope 축소(부분 약화). Amendment 9(DialogFidelityAgent sunset) / Amendment 10(§결정 5 redirect over-asking 절제) 에 이은 third weaken-direction amendment이며 **§결정 18 의 첫 weaken**(Amendment 7 = 강화 `null` 이었음). `sunset_justification` = null 아닌 4-key evidence object(dead_mandate / verification_ground_redundancy / cost_vs_effect_zero / meta_policy_alignment) 충족 → ADR-058 §결정 5 + ADR-064 §결정 7 evidence-gated symmetric ratchet 1급 허용(차단 아님). 무손상 — 정당 trigger 2종(ADR-053/057) + anti-pattern 7종 enum member 추가·삭제 0(controlled-path gate 만 신설), 본문 immutability(§18.1 상단 1-line cross-ref pointer만 additive), §결정 22 line 1285 무손상, §결정 23 disjoint, frame mode/Layer 1-4/sub-mechanism/3 touchpoint/ask-trigger 3종/skip-offer/5번째 cognitive layer 신설 금지 invariant 전부 보존.

## 해소 기준

N/A — permanent policy (ADR 전체).

본 ADR 전체 의 sunset 은 codeforge dialog governance 자체 폐지 (예: codeforge plugin family 전체 deprecate) 또는 본 ADR supersede (예: ADR-071 의 강화 amendment 발의) 시점에만 가능. ADR-064 / ADR-058 / ADR-063 / ADR-065 / ADR-039 governance carrier 의 `is_transitional: false` 패턴 정합 (recursive sunset 회피).

**부분 §결정 sunset 가능 (Amendment 9 / CFP-2236)**: ADR 전체 `is_transitional: false` permanent 유지와 별개로, 개별 §결정 의 부분 sunset 은 evidence-gated 로 가능 — Amendment 9 가 §결정 12/13/14 + §17.4.3 의 DialogFidelity 부분을 sunset_justification 3축 evidence 로 강등 (carrier-preserved in-place). 이는 ADR 전체 강등 (is_transitional false→true) 이 아니라 sub-decision 단위 weaken-direction amendment — dialog governance 본체 (frame mode + 4 layer + 3 touchpoint) 는 permanent 보존. verifier auxiliary 만 sunset.

## 관련 파일

- [ADR-064](ADR-064-decision-principle-mandate.md) — 결정 원칙 mandate (proposing-time 5 룰, 본 ADR mechanical 승격 source)
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — sunset criteria mandate (`is_transitional: false` 정합 anchor)
- [ADR-052](ADR-052-codex-proactive-check-touchpoints.md) — Codex Proactive Check 6 touchpoint (Amendment 1 multi-round debate + Amendment 3 fact-check marker)
- [ADR-059](ADR-059-debate-protocol-v1.md) — debate-protocol-v1 (conceptual cross-ref only, §결정 9)
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) — plugin.json MINOR bump atomic invariant
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) — Phase 1 mechanical sync self-check 7-item
- [ADR-070](ADR-070-codex-verify-before-trust.md) — fact-check marker source
- [ADR-040](ADR-040-worktree-convention.md) — `mechanical_enforcement_actions[]` frontmatter 의무
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — inline whitelist 1번 entry cognitive 강화 (§결정 11)
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — declarative reconciliation upgrade (Amendment 5 — invariant `user_decision_branches: 0` dialog 단계 enforcement carrier)
- [ADR-054](ADR-054-doc-only-story-fast-path.md) — doc-only fast-path (Amendment 5 — Story 분류 정합)
- [CLAUDE.md](../../CLAUDE.md) — cross-ref 1-2 줄 (320 cap compression 정합)
- [docs/orchestrator-playbook.md](../orchestrator-playbook.md) — §3.14 frame + 4 layer + sub-mechanism 본문 SSOT
- [docs/orchestrator-communication-incidents.md](../orchestrator-communication-incidents.md) — Layer 4 영속 file
- [skills/user-dialog-mode/SKILL.md](../../skills/user-dialog-mode/SKILL.md) — frame mode + 4 layer lookup table skill
- [CFP-612](https://github.com/mclayer/plugin-codeforge/issues/612) — carrier Issue
- [CFP-525](https://github.com/mclayer/plugin-codeforge/issues/525) — ancestor Epic (closed)
- [CFP-1104](https://github.com/mclayer/plugin-codeforge/issues/1104) — Amendment 5 carrier Issue (natural-language action trigger lookup table)
- [CFP-1110](https://github.com/mclayer/plugin-codeforge/issues/1110) — Amendment 6 carrier Issue (lane back-translation gate binding — paired ADR-082 Amendment 5)
- [CFP-1340](https://github.com/mclayer/plugin-codeforge/issues/1340) — Amendment 7 carrier Issue (unjustified session swap reflex 차단 + /compact normative)
- [CFP-1764](https://github.com/mclayer/plugin-codeforge/issues/1764) — Amendment 8 carrier Issue (agent burst output paste 합성 시 mid-turn glossary lookup 의무 — §결정 19 신설, docs/wording-dictionary.md 카테고리 (c) codename → 평이 어휘 mapping table SSOT, mctrader-hub#517 evidence)
- [docs/wording-dictionary.md](../wording-dictionary.md) — Amendment 8 — 카테고리 (c) codename → 평이 어휘 mapping table SSOT
- [CFP-582](https://github.com/mclayer/plugin-codeforge/issues/589) — sibling (agent ↔ agent domain, conceptual cross-ref)
- [ADR-053](ADR-053-structural-change-restart-prerequisite.md) — session swap reflex trigger #1 (구조 변경 재구동) closed 2-set first entry
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — session swap reflex trigger #2 (Sonnet/Haiku → Opus fallback) closed 2-set second entry
- [CFP-2236](https://github.com/mclayer/plugin-codeforge/issues/2236) — Amendment 9 carrier Issue (DialogFidelityAgent 전면 폐지 sunset — §결정 12/13/14 + §17.4.3 DialogFidelity 부분 carrier-preserved 강등, first weaken-direction amendment, sunset_justification 3축 evidence object, codeforge-pmo agent count 3→2)
- [ADR-037](ADR-037-plugin-bump-semantics.md) — Amendment 9 plugin bump semantics (DialogFidelityAgent 제거 = capability 축소 = MINOR)
- [CFP-2567](https://github.com/mclayer/plugin-codeforge/issues/2567) — Amendment 13 carrier Issue (§결정 22 신설 — Epic 내 Story 전환 자율 진행, 전환 지점 over-halt/over-ask 방지, D1 doc 국소 명시 + D2 2-channel(UserPromptSubmit 예방 reminder hook skip-offer 동형 + PreToolUse(Agent) additionalContext non-block inject pretooluse-agent-spawn-gate 확장, autonomous 전환 창), §결정 15/20 전환 지점 적용 강화 enum member 추가 0, Stop/SubagentStop REJECT)
- [ADR-115](ADR-115-runtime-hook-enforcement.md) — Amendment 13 hook 5층 graceful degradation + Stop block 금지 record-only (D2 reminder hook-frame 재사용 + §결정 2 Stop force-continue REJECT 근거)
- [ADR-061](ADR-061-python-script-writing-convention.md) — Amendment 13 hook script 작성 규약 (D2 hook self-contained stdlib)
- [ADR-127](ADR-127-mandatory-full-flow-no-exemption.md) — Amendment 13 정식 풀 플로우 비협상 (자동 진행 ≠ 게이트 skip ≠ lane 생략 ASM-1)
- [skills/story-epic-flow-preflight/SKILL.md](../../skills/story-epic-flow-preflight/SKILL.md) — Amendment 13 Epic-flow child-transition point 자율 진행 norm PRIMARY local annotation (D1)
- [hooks/hooks.json](../../hooks/hooks.json) — Amendment 13 UserPromptSubmit 배열 5번째 entry (D2)
- hooks/story-transition-autonomy-reminder(.py) — Amendment 13 D2 채널 1 신규 sibling hook (skip-offer-reminder 동형 UserPromptSubmit 예방 reminder)
- [hooks/pretooluse-agent-spawn-gate](../../hooks/pretooluse-agent-spawn-gate) — Amendment 13 D2 채널 2 (PreToolUse(Agent) additionalContext 전환 reminder inject, 기존 배선 gate 확장, autonomous 전환 창)
- [CFP-2742](https://github.com/mclayer/plugin-codeforge/issues/2742) — Amendment 16 carrier Issue (§결정 24 session-swap controlled-path — 자족 handoff 프롬프트 동반 시 전환 권유 허용, §결정 18 첫 weaken-direction, handoff 6 필수요소 = ADR-085 §결정 9 4-rule specialization)
- [ADR-085](ADR-085-multi-session-collaboration-protocol.md) — Amendment 16 §결정 9 multi-session prompt design 4-rule prior art (handoff 6요소 = specialization, 재발명 금지) + rule 1 planned-lane-split 금지 = forced-continuation disjoint 경계
- [docs/consumer-guide.md](../consumer-guide.md) — Amendment 16 §7.6 consumer 전파 cross-ref anchor (session-swap controlled-path 상속, 확장-only)
- hooks/session-swap-handoff-reminder(.py) — Amendment 16 Phase 2 forward-ref 신규 sibling hook (story-transition-autonomy-reminder 동형 UserPromptSubmit 예방 reminder, 본 Phase 1 미생성)
