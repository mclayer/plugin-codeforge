---
adr_number: 170
title: Orchestrator subagent default for codeforge modification work — binary always-spawn + inline whitelist (ADR-039 재제정)
status: Accepted
category: orchestration-discipline
date: 2026-07-31
carrier_story: CFP-2869
supersedes:
  - ADR-039
amends: null
amendment_log:
  # ★ Amendment 1 = CFP-2948 예약 (미머지 브랜치 `origin/cfp-2948`, open PR 없음 — 커밋 `a42b305a5`/`1c48fdddf` 가
  #   `amendment_log: - amendment: 1` 로 선점). 본 Amendment 2 는 그 slot 을 양보하고 다음 번호를 쓴다.
  #   cfp-2948 이 폐기되면 번호 1 공백이 잔존한다 — 정직 declare (renumber 요구 안 함, ADR-082 Amd36 1-Y §A ascending 정렬만 의무).
  # ★ 컨테이너 키 = `amendment_log:` (`amendments:` 아님). 근거 = 들어올 Amd 1 이 `amendment_log:` 를 쓰므로 단일 파일 내
  #   컨테이너 이종 혼재 회피 + corpus 우세형. 기계 소비자는 양 키 합산이라 선택이 count 를 바꾸지 않는다
  #   (`scripts/lib/check_adr_amendment_threshold.py:113` `for key in ("amendment_log", "amendments")` — first-key-wins 아님).
  - amendment: 2
    date: "2026-08-18"
    carrier_story: CFP-2994
    issue: https://github.com/mclayer/plugin-codeforge/issues/2994
    summary: |
      저작 ⊥ 전사 (authority) 축 — 기록 표면의 소유자가 타 주체 몫을 자기 것으로 처리하는 **4번째 형태** 신설.
      (A) 신설 형태 ④ = 「타 주체 저작을 흡수하며 귀속을 자기로 표기」. 기존 3형(① verbatim 전사 + 명시 귀속 = 합법
      ② 자기 관측으로 덮어쓰기 = 위반 ③ 관측 주체 없이 창작 = 위반) 어디에도 걸리지 않는다 — 내용 무손실 · 덮어쓰기 아님 ·
      창작 아님이고 **귀속만 틀렸다**. 원 사건(내용 증발)과 피해 축은 다르나 기전(기록 표면 소유자가 타 주체 몫을 자기 것으로
      처리)은 동형. `[verified — CFP-2994 설계 lane 자기 관측]`: 본 Story 를 진행하는 lane 안에서 deputy 커밋이 lane PL 의
      미커밋 저작을 자기 커밋에 흡수했고 git log 가 그 귀속을 잘못 말했다.
      (B) **예외(§결정 2 entry #5)는 좁힐 수 없음 — 확정.** inline whitelist 축소는 ① CFP-2994 §9.1~§9.4 원장 retrofit
      (Orchestrator 전사)을 소급 위법화하고 ② 본 ADR §결정 2 writer monopoly 와 충돌한다. ⇒ 채택 방향 = 예외 축소가 아니라
      **분류에 ④를 추가하는 확장**(ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향).
      (C) **2층(지시 ⊕ 산출물) — 규범 완결 · 기제 공백 정직 declare.** 원 지시 함정(「미수령으로 declare」의 `미수령` 이
      「공란 아닌 명시 상태값」을 충족)은 셀 공란을 재는 술어에만 작동하고 delta-부호 술어는 통과하지 못한다 `[verified]`.
      단 지시층 판정은 **압박 당사자만 평가 가능**(반사실 필요) ∧ 지시 표면이 런타임 ephemeral ⇒ 등급 = `normative` 이나
      **집행 표면 0**. 이 비대칭을 감추지 않는다(ADR-119 §결정 10 outcome-honesty 상속).
      (D) **`receipt_state` = 도달(arrival) 전용 경계.** 산출물 존재·귀속 기록은 허용, **충분성·품질 판정은 금지** —
      「받았다 ⇒ 쓸 만하다」 함의가 붙는 순간 ADR-139 INV-L4(verdict 판정 = lead 소유)를 침범한다.
      (E) amendment slot 충돌 오라클 교훈 = ADR-139 Amendment 3 + Change Plan §10 (본 Amendment 는 cross-ref 만).
      강화(ratchet↑) 방향 — §결정 1~21 · inline whitelist 7-entry count · writer monopoly 전부 무변경, 분류 1형 추가만.
    sunset_justification: null   # 강화 방향(4번째 형태 추가 = 분류 확장 ratchet↑, 예외 축소 0) — ADR-058 §결정 5 약화 evidence-gate 비대상. §결정 2 7-entry enumeration 무손상.
reinterpretation: false  # ADR-167 §결정 1(b) — 본 ADR 은 ADR-039 실효 규범의 의미 무변경 재제정(restatement)이지 소급 재해석이 아니다. 신규 저작(재해석 marker false).
is_transitional: false
related_adrs:
  - ADR-039  # 재제정 대상 — 본 ADR 이 supersede. 구본 = 본문 byte-보존 in-place 동결(이력 담보), 실효 규범은 본 ADR 로 이관
  - ADR-167  # 재제정(compaction) ratchet SSOT — 본 건 트리거 = 기계 count 축(effective_count 12 > grandfathered_at 11, f/u #2862)
  - ADR-168  # 재제정 선례 실물(ADR-082→168) — 구조 준거(번호 보존 restatement + 처분표 + R2 해석우선순위)
  - ADR-009  # explicit codify 계승 — 구 ADR-039 frontmatter `amends: ADR-009` 관계 이관(ADR-054→ADR-127 후계 선례 동형, §결정 10 carrier-preserved)
  - ADR-025  # stop discipline + Epic-level continuity — motivation(policy_violation_subdecision 발화 채널 제거)
  - ADR-029  # phase execution visibility — narration interaction
  - ADR-031  # lane-spawn evidence trail — §14 row append ownership(§결정 3/12), Amendment 1 = delegate cover
  - ADR-035  # codeforge agent teams Epic — subagent semantics 분기
  - ADR-134  # 병렬 적격성 5조건 + per-Story dispatch — §결정 19 spawn-권한 layer sibling
  - ADR-139  # background-wait liveness gate — §결정 20 cross-ref carrier SSOT(INV-L4 spawn-권한 게이트 소유)
  - ADR-109  # in-process 429 mitigation framework — §결정 9 rate-limit second-order risk carryover SSOT
  - ADR-115  # inline-write gate hook frame — §결정 9 Write/Edit/MultiEdit 축 실현 paired
  - ADR-142  # Orchestrator-self READ/synthesis 규율 — §결정 9 Read-axis advisory 천장의 holder=Orchestrator-self realization anchor + disjoint-axis lint carrier
  - ADR-143  # 렌더 라인 프리픽스 display 축 — §결정 2 disjoint-axis note paired
  - ADR-058  # §결정 5 evidence-gate — inline whitelist entry 신설·약화 방향 게이트(§결정 2 exhaustiveness)
  - ADR-064  # §결정 7 evidence-gated symmetric ratchet
  - ADR-133  # ADR 번호 atomic claim — 본 ADR 번호(170) 발급(§결정 4 fallback 경로 — 설계 lane push 금지)
  - ADR-050  # ADR-RESERVATION registry — row 170 append
related_stories:
  - CFP-2869
related_files:
  - scripts/lib/check_disjoint_axis_whitelist.py  # 기계 결박 1 — Phase 2 재저작(declared-vs-actual self-consistency)
  - scripts/test-check-disjoint-axis-whitelist.sh  # 기계 결박 2 — 자매 discriminating test(M1~M9 mutation — 정의 소재 Story §8.3, Phase 2)
  - .github/workflows/disjoint-axis-whitelist-lint.yml  # 기계 결박 3 — 헤더 주석 pin 재기술(Phase 2)
  - docs/inter-plugin-contracts/return-envelope-v1.md  # 기계 결박 4 — lint LDOC 검사 대상, §5 disjoint-axis 선언 현행화 + PATCH bump(Phase 2)
  - docs/inter-plugin-contracts/spawn-event-v1.md  # 기계 결박 5 — writer 정의 authority 인용 재지향 + PATCH bump(Phase 2)
  - tests/unit/cfp_2850/test_ac4_writer_monopoly.py  # 기계 결박 5 짝 — "ADR-039" 문자열 assert 동기 갱신(Phase 2)
  - docs/parallel-work/section-ownership.yaml  # owner_adr ADR-039 2행 re-home(Phase 2)
  - docs/adr-amendment-threshold-baseline.yaml  # ADR-039 행 제거 17→16(--write-baseline 단일 writer, Phase 2)
  - archive/adr/ADR-RESERVATION.md  # ADR-number row 170 신설(Phase 1, 본 Story)
# effective_count 재시작 = 0: 본문 `^#{2,4} Amendment` 헤딩 0 ∧ frontmatter amendments:/amendment_log: 키 자체 생략(양쪽 결합, AC-1). ADR-167 §결정 5 재제정 신규 count 0 재시작 정합.
---

# ADR-170: Orchestrator subagent default for codeforge modification work — binary always-spawn + inline whitelist (ADR-039 재제정)

## 상태

**Accepted** (2026-07-31 KST, CFP-2869 Phase 1 carrier).

**재제정 선언 (no-substantive-change — ADR-167 §결정 4(a) 필수 요소 (a))**: 본 ADR 은 **ADR-039(Orchestrator subagent default for codeforge modification work)의 현행 실효 규범을 의미 무변경으로 깨끗한 신규 record 에 재작성한 재제정(re-enactment / recodification)**이다. 허용 변경 = **구조 개선·obsolete 제거·모호 해소·기술 정정 4종 한정**. 의무/금지/조건/예외의 규범 효력은 무변경이다. 의미 변경이 필요하면 재제정이 아니라 **별개 amendment 또는 신규 결정으로 분리**한다(본 Story 는 그런 항목을 발견하지 않았다 — 발견 시 해당 항목을 재제정에서 제외하고 분리, AC-8). 구 ADR-039 는 **본문 byte 무변경 in-place 동결**로 잔존하며(이력 담보), `status: Superseded by ADR-170` 로 전이한다(전이 = Phase 2). 실효 규범의 단일 canonical source = 본 ADR-170. 재제정 배경 = ADR-167 ratchet 의 **2번째 실물 정산**(1번째 = ADR-082→ADR-168) — 트리거 = 기계 count 축(effective_count 12 ≥ THRESHOLD 10 ∧ 12 > grandfathered_at 11, adr-amendment-threshold CI RED, follow-up #2862). amendment 12건 중 **11건 = `direction: strengthening`**(ratchet-up) 으로, 해당 실효 규범은 "가장 넓게 확장된 최종 상태"의 단일 스냅샷으로 fold 가능하며 본 ADR 은 그 fold 를 §결정-level 로 수행한다.

**약화 fold 예외 declare — Amendment 2 (`direction: weakening_partial`)**: 구 ADR-039 amendment 중 유일한 비-strengthening 인 Amendment 2(CFP-1340, §결정 15 신설)는 §결정 1 closed enumeration("Story file write §1-§14 = subagent spawn 의무") 의 **§9/§10/§14/phase 4-sub-scope 한정 partial rollback**(사용자 explicit directive 기반, ADR-058 §결정 5 약화 evidence-gate 통과분)이다. 이 약화분은 "확장 최종상태" arithmetic 병합의 대상이 아니다 — **§결정 15 의 partial rollback 이 그 자체로 이미 최종 effective 상태**이며, 본 ADR 은 그 상태(4-sub-scope 만 inline 허용 + 나머지 §1-§8/§11-§13 always-spawn 유지)를 그대로 재기술한다(arithmetic 병합 불요). all-strengthening 전제(ADR-168 fold 논거)의 복붙은 본 건에 적용되지 않음을 명시한다.

## 본질 선언

codeforge 를 이용한 **수정 작업**에서 Orchestrator(top-level Claude 세션)는 "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 없이 **무조건 subagent spawn** 으로 수행한다(사용자 directive verbatim "무조건 subagent" — 컨텍스트 참조). inline 수행이 허용되는 표면은 §결정 2 의 closed inline whitelist 가 전부다. 본 ADR 이 충족되지 않으면 나머지 §결정 mechanism 을 몇 개 쌓든 의미 없다 — §결정 3~15·18·19·21 은 이 binary always-spawn 본질을 보조하는 scaffolding 이며, §결정 16(permission UI)·§결정 17(span guideline)·§결정 20(background-wait liveness)은 각자 선언한 disjoint axis 를 규율한다.

## 컨텍스트

### 사용자 directive (verbatim — 정책의 규범 원천)

> "무조건 subagent만 하도록 하자. 그것 때문에 user stop이 자꾸 발생한다." (2026-05-08)

> "codeforge를 이용한 수정 작업에서는 무조건 subagent이다." (2026-05-08)

> "그러니까 story 발의해서 적용해" (2026-05-08)

> "agent teams 기능을 적극적으로 사용할 수 있도록... 토큰의 양 효율성은 중요하지 않다." (ADR-035 §컨텍스트 verbatim — 운영 risk(rate limit / token cost) trade-off 수용 근거)

동인 = "inline vs subagent" 결정 분기가 ADR-025 §결정 7 `policy_violation_subdecision` user-stop 발화 채널이었음. binary 정책(branch logic 제거)이 그 채널을 mechanism level 에서 제거한다.

### 재제정 대상 · fold 소스 구조

구 ADR-039(2026-05-08 제정, 원 carrier CFP-275)는 원 §결정 1~13 + amendment 12건이 누적된 847행 record 다. fold 소스 구조는 선례 ADR-082(본문 `## Amendment` 절 38개)와 다르다 — ADR-039 는 본문 Amendment 헤딩 0 이며 **12건 중 11건이 이미 본문에 fold 완료** 상태다: 신설형 8건(Amd 1/2/3/5/6/7/10/12 → §결정 14~21 헤딩 신설) + in-place fold형 3건(Amd 8/9 → §결정 9 인라인 amend, Amd 11 → §결정 2 note). 나머지 1건 **Amd 4(rate-limit carryover)는 구본 본문 미반영**(frontmatter `amendment_log[4]` 전용 — 구본 body ADR-109 언급 0건, firsthand grep) — 본 재제정이 §결정 9 재기술 + §결정 18 disjoint 논거로 최초 본문 승계한다. 따라서 본 재제정의 실체 = **§결정 1~21 의 의미 보존 재구성(dated 서사 제거 + 분산 표 통합) + Amd 4 본문 승계 + frontmatter amendment_log 12행 제거(count 0 재시작)** 다.

### 해석 우선순위 조항 (R2 — no-substantive-change presumption)

본 ADR-170 의 문언과 구 ADR-039 규범이 상충하는 것으로 보일 때, **재제정 처분표(아래 §재제정 처분표)에 명시 변경으로 표기된 지점 외에는 구 규범의 의미가 우선**한다(no-substantive-change presumption). SSOT 지위 자체는 ADR-170 이 보유하되, 이 우선순위는 **상충 해소 한정 semantics** 이며 이중원본을 뜻하지 않는다 — 구 ADR-039 는 이력 담보로 동결 잔존할 뿐 규범 source 가 아니다. 재제정 처분표는 재제정 후에도 코드·문서의 "ADR-039 §결정 N / Amendment M" 인용을 신 위치로 해소하는 **영구 참조 해소 자료(lookup)**로 기능한다.

## 결정

> 번호 보존 restatement — 생존 §결정은 ADR-039 원번호를 유지한다(§결정 19 는 그대로 §결정 19). 외부 인용("ADR-039 §결정 N")은 번호 무변으로 "ADR-170 §결정 N" 재지향만으로 해소된다.

### 결정 1 — codeforge 수정 작업 = Orchestrator default subagent spawn

codeforge 를 이용한 **수정 작업** 진행 중, Orchestrator (top-level Claude 세션, ADR-009) 는 모든 work 을 `Agent` tool spawn (subagent) 으로 수행한다. inline 수행 (Orchestrator turn 안에서 Read / Write / Edit / Bash / Grep / Glob / mcp__github__\* 직접 호출) 은 §결정 2 의 inline whitelist 외 영역에서 금지.

**수정 작업 정의** (closed enumeration):

- file edit / write (`docs/**`, `src/**`, `templates/**` 포함)
- GitHub state change (Issue / PR / comment / label / milestone / sub-issue / branch / merge)
- Story file write (§1-§14 어느 섹션이든 — **단 §9 verdict / §10 FIX Ledger / §14 Lane Evidence / phase transition 4-sub-scope 제외 = §결정 2 entry 5 / §결정 15 scope, partial rollback**)
- FIX Ledger §10 row append (fix-event-v1 contract — ownership 무변, mechanism 만 spawn 또는 Orchestrator inline — §결정 15)
- Lane-spawn evidence §14 row append (ADR-031 — ownership 무변, mechanism 만 spawn 또는 Orchestrator inline — §결정 15)
- gate label transition (`gate:design-review-pass` 등)
- phase label transition (`phase:요구사항` → `phase:설계` 등)
- workflow yaml 수정·추가
- ADR / Change Plan / domain-knowledge 페이지 write
- **trivial Read 1건 도 spawn 의무** (사용자 verbatim 명시 — trivial-threshold-zero)

"이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 자체 금지 — branch logic 제거가 본 ADR 의 핵심.

### 결정 2 — Inline whitelist (closed enumeration — 7-entry flat 단일표)

| # | Category | 설명 | Mechanism rationale |
|---|---|---|---|
| 1 | 사용자 dialog | `AskUserQuestion` / 확답 step / 정보 요청 답변 (Yes/No / 옵션 선택) | Subagent one-shot 이라 continuous dialog 자체 mechanism 불가능 (ADR-009 §결정 + CLAUDE.md "플랫폼 제약"). DialogFidelityAgent verifier subagent spawn 은 본 entry scope 안 cognitive 보강 — 사용자 dialog 본 발화 inline 유지 + 직전/직후 verifier spawn = §결정 1 default subagent spawn 정합 (신규 entry 신설 아님, closed enumeration 보존 — ADR-071 §결정 13 / CFP-818). (DialogFidelityAgent verifier = CFP-2236 sunset — ADR-071 Amendment 9. 본 entry #1 enum 자체는 무손상 active.) |
| 2 | TodoWrite scratchpad | progress visualization marker write | TodoWrite = file write 아님, Orchestrator scratchpad / meta progress channel — 수정 작업 enumeration 미포함. (참고: ADR-038 = TodoWrite progress visualization 도입 informational reference, 본 entry 정당화에 normative dependency 아님 — TodoWrite tool surface 자체가 file system / GitHub state mutation 미발화이므로 본 ADR 내 standalone 정당화) |
| 3 | Read-only Q&A 답변 | 사용자 정보 요청에 대한 응답 (state report / option enumeration / 도메인 설명) | 수정 작업 아님 — codeforge orchestration scope 외 |
| 4 | Status report | Phase 완료 / Story close / final report | 수정 작업 아님 (read-only synthesis) — ADR-025 Amendment 1 §결정 11 의 "1번 final report" |
| 5 | Orchestrator-monopoly Story-file handoff inline write (§결정 15) | Story file 의 Orchestrator-monopoly 4-sub-scope inline write — §9 verdict / §10 FIX Ledger row append / §14 Lane Evidence row append / phase transition (`phase:요구사항` → `phase:설계` 등) | Orchestrator-monopoly Story-file section 의 monopoly 명목 보존 (ADR-031 §14 + fix-event-v1 §10 contract invariant). general-purpose editor subagent 위임 시 inline cost (~60-70KB 큰 파일 inline reconstruction) + Orchestrator-monopoly intent 희석 우려 — 사용자 explicit reject (2026-05-17 KST CFP-848 directive verbatim "Orchestrator-monopoly Story-file section handoff 시 general-purpose editor subagent 위임 reject"). lane agent self-write 영역 (§1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13) = 본 entry scope 외 — §결정 1 binary always-spawn 유지. |
| 6 | Merge-time Codex adversarial gate dispatch (§결정 18) | ADR-052 touchpoint #7 (merge-time adversarial gate) 의 Codex worker dispatch — 구현리뷰 PASS + CI gate PASS 후 "merge gate 진입" 직후 / `gh pr merge` 직전, Orchestrator top-level inline 에서 `codex exec --sandbox read-only < <promptfile>` (ADR-081 D8 file-redirect) 1패스 발동 + result-via-file 수신 | **재귀 가드 회피 critical (H1 게이트 연극화 차단)**. sub-agent / PL 을 게이트 owner 로 두면 platform-inherent 재귀 가드("subagent → Agent tool 호출 금지")로 Codex worker spawn 이 silent fallback skip (`subagent_recursion_blocked` fail-mode, ADR-070 Amendment 6) → 게이트 무발동 = 연극화. 따라서 dispatch 주체 = Orchestrator top-level inline 고정 의무. dispatch 자체 = read-only adversarial check (verify-before-trust 무조건 적용 — mismatch finding reject) 이라 §결정 1 "수정 작업" 정의 (file edit / GitHub state change) 와 disjoint axis — mutation 발생 0. 머지 보류·FIX 회부 등 후속 mutation 은 §결정 1 / entry 5 영역 (별도 mechanism). |
| 7 | Tier-3 measurement-channel ledger row append (§결정 21) | Orchestrator 가 Agent task-notification / spawn-completion 수신 시점, spawn-event-v1 (또는 sibling Tier-3 measurement channel) row 를 구조화 CLI/args-file invocation 으로 append. 범위 한정: (a) free-form content 0 (numeric/enum/hash only) (b) args-file = ASCII path + UTF-8 JSON content (argv string-interp injection 회피) (c) record-only (gate/block/deny 금지) (d) 0-API + 50ms ceiling + exit-0 | measurement 배선 전용 — 판정/게이트 로직 inline 금지. evidence-gate 통과 논거(ADR-058 §결정 5) = entry 5(Story-file 구조화 append)·entry 6(merge-time Codex dispatch) 와 동형 "Orchestrator monopoly 소형 구조화 append · free-form 0 · 판정 로직 부재" 3-조건 충족 (§결정 21). writer monopoly 무약화 — lane plugin 직접 write = 여전히 policy_violation. |

**현행 effective inline-whitelist total = 7-entry** — 위 flat 단일표가 count 의 live SSOT 이며, 표 row 수(7)와 본 정형 선언의 일치가 기계 판정 대상이다(disjoint-axis lint declared-vs-actual self-consistency — 관련 파일 참조).

위 7-entry **외** 의 모든 codeforge orchestration 행위 = subagent spawn 의무. **모호 시 = 수정 작업 측 분류** (안전 방향 — ADR-013 cutoff precedent 정합).

**8번째 entry 신설 = 본 ADR amendment 의무** (ADR-058 §결정 5 evidence-gate). 본 closed enumeration 이 future "Skill 호출 / Glob / Grep / Read tool 분류 enum 확장" 압박을 차단 — 모두 현행 7-entry 의 어느 하나로 routing 또는 수정 작업 측 분류.

**역사 해석 note (구본 표기 해소)**: 구 ADR-039 및 타 문서의 "4-entry closed enumeration 무변경" 표현 = 구본 base 표(entry 1-4) 무변경 의미이고, "현 5-entry / 6-entry" 표기 = 각 저작 시점의 historical snapshot 이다 — 현행 count 는 항상 본 §결정 2 표를 read 한다(효력 무모순).

**disjoint-axis note (display 축 경계 — §결정 2 note, enumeration 무변경)**: 위 whitelist entry #4 "Status report" = 사용자 대상 **prose 대화 채널**(mechanism 축 — inline vs spawn). 이는 ADR-143 §결정 1 이 규율하는 **렌더 UI action/상태 LINE**(display 축 — harness 진행 줄)과 **별도 표면(disjoint axis)** 이다. ADR-143 Amendment 2 가 Orchestrator 자기 렌더 action/상태 LINE 에 self-subject `[Orchestrator]` 프리픽스를 허용(INV-2 subset 완화)하되, 이는 본 whitelist "상태 보고" prose(prefix-exempt 유지)를 **건드리지 않는다** — mechanism 축 ≠ display 축. Orchestrator 에게 신규 inline 실행 권한 미부여(이미 발생 중인 top-level 액션의 렌더 LINE 라벨링일 뿐). paired = ADR-143 Amendment 2.

### 결정 3 — Ownership ≠ Mechanism 분리

본 정책은 **mechanism (어떻게 수행)** 규율이다. **ownership (누가 작성권)** 무변.

- Orchestrator monopoly ownership (유지 — invariant 무손상):
  - Story §10 FIX Ledger row append (fix-event-v1 contract)
  - Story §14 Lane Evidence row append (ADR-031)
  - review-verdict final write (Story §9 / GitHub comment / gate label / phase transition)
  - branch protection / CI workflow / cross-plugin schema templates
- Mechanism: 위 ownership 영역의 file write / GitHub state change 는 **subagent spawn 으로 수행** (default mechanism) **또는 Orchestrator inline write** (§결정 2 entry 5 scope = §9/§10/§14/phase 4-sub-scope 한정). Orchestrator 가 "§10 row append 전용 subagent" / "§14 row append 전용 subagent" / "label transition 전용 subagent" 를 spawn 해 Edit / mcp__github__\* tool 호출 (default) — 또는 Orchestrator-monopoly Story-file 4-sub-scope 영역은 inline write 직접 수행 가능 (§결정 15).

**Orchestrator-owned delegate subagent (spawn mechanism) + Orchestrator inline (§결정 15 mechanism) 양 mechanism 모두 valid** — ownership identity (Orchestrator monopoly) 보존, mechanism level 양 path 허용. 본 분리는 ADR-031 §결과 invariant 무손상 + lane plugin agent 변경 부재의 핵심 근거다(§결정 12 cross-ADR 정합 anchor).

### 결정 4 — Scope = codeforge orchestration 한정

본 정책 적용 범위 = **codeforge orchestration**. 즉 wrapper Orchestrator 가 codeforge family (wrapper + 6 lane plugin) 의 spawn / docs/** / GitHub state / Story file / FIX Ledger / lane-spawn evidence 영역에서 수행하는 행위. 일반 Q&A / conversational 응답 / non-codeforge 작업 (예: 단순 정보 답변 / 사용자 dialog) 은 비적용 — §결정 2 Inline whitelist 가 boundary clarification.

### 결정 5 — Lane plugin / design SubAgent / inter-plugin contract = 0 변경

본 정책은 Orchestrator-side mechanism 정책이다 — 다음을 변경하지 않는다:

- 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) agent 변경 0건.
- design lane deputy SubAgent 변경 0건 (현행 roster SSOT = `codeforge:deputy-mandate` skill).
- Inter-plugin contract 변경 0건 (registry SSOT = `codeforge:inter-plugin-contract-registry` skill).
- ADR-009 §결과 invariant 무손상 (Writer 단독 invariant precedent — ADR-029 / ADR-031 와 동일 패턴).

(기술정정 note: 구본의 deputy·contract 개별 열거는 2026-05-08 시점 스냅샷 명칭이었다 — 현행 구성은 위 skill SSOT 를 read 한다. "변경 0" invariant 자체는 무변.)

### 결정 6 — Hotfix path 동일 적용 (no exception)

`docs/hotfix-playbook.md` 의 Hotfix 경로 (운영 장애 대응 / 사후 감사 의무) 도 본 정책 적용. 사용자 verbatim "무조건" — emergency 시에도 spawn 의무. Hotfix 의 fast-path 본질 (Phase skip / lane skip) 은 무변, **mechanism 만 spawn 의무**.

### 결정 7 — Consumer scope (wrapper + consumer Orchestrator 동일 적용)

본 정책 = wrapper Orchestrator + consumer Orchestrator (예: mctrader Orchestrator / 추후 다른 consumer) 모두 적용. consumer Orchestrator 가 codeforge family plugin 을 사용하는 시점부터 본 정책 inheritance — `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" 가 SSOT cross-ref. ADR-025 §결정 9 (consumer scope) 와 동일 enforcement 패턴.

### 결정 8 — 기본 enforcement = doc trust model

본 정책의 기본 enforcement 강도 = doc trust — 매 Orchestrator 행위 시 (1) 본 ADR / (2) playbook §3.0 / (3) CLAUDE.md subagent default 단락 / (4) consumer-guide § "Subagent default" / (5) hotfix-playbook 1줄 reading 시 자체 인지. 기계 enforcement 의 도입 여부·강도는 §결정 9 가 규율한다 (Write/Edit/MultiEdit 축 warning-tier hook 실현분 포함 — doc trust 는 그 실현 후에도 base layer 로 병존).

### 결정 9 — Enforcement / measurement 현황 + deferred 목록

본 정책의 기계 enforcement / measurement 는 다음 상태다 (현재형 최종 상태 — 진행 이력은 동결 구본·처분표 참조):

- **stop-event-v1 ledger** (deferred): Orchestrator user-stop 발화 시 ledger row append → `reason_class: policy_violation_subdecision` 발생률 측정 → 본 정책 효과 검증 (ADR-025 §결정 10 deferred 승계).
- **Orchestrator inline write detect hook — Write/Edit/MultiEdit 축 = IMPLEMENTED (Wave1 warning-tier)**: hooks.json PreToolUse `Write|Edit|MultiEdit` matcher + `hooks/pretooluse-inline-write-gate` polyglot hook + `scripts/lib/check_inline_write_gate.py` verifier (agent_id caller 판정: non-empty string = subagent = allow / 부재·null·빈문자열 = Orchestrator = block-candidate, fail-safe) + `scripts/check-inline-write-gate.sh` thin wrapper. Wave1 = exit 0 + stderr (NEVER deny — ADR-115 §결정 4/5 graceful degradation). Wave2 deny (exit 2) 승격 = ADR-060 evidence-gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 후 별도 CFP. **mcp__github__\* 축 + Read 축 + Bash-redirect 파일작성 우회 = deferred** (별도 CFP). paired = ADR-115 Amendment 1.
- **spawn cost telemetry** (deferred): token / latency 정량 측정 — spawn latency 정량 데이터 부재 gap 충당.
- **rate-limit second-order risk 측정 carryover**: rate-limited error → unwanted user-stop 위험의 측정·완화 SSOT = ADR-109 (in-process 429 mitigation framework — retry primitive 위치 = `codeforge:rate-limit-429-mitigation` skill body / telemetry = ADR-109 §결정 8). retry primitive 는 §결정 2 inline whitelist entry 로 신설하지 않는다 (closed enumeration 보호 — "429 retry inline allowed" 압박 차단, 신설 advocacy REJECTED 이력은 처분표 Amd 4 참조).
- **DevPL-side "PL self-read advisory detection"** (ADR-044 §결정 11 D3 enforcement home): lane-PL(특히 DeveloperPL)이 비-essential 경로를 직접 read 하는 fat self-implementer drift 검출. **advisory/warning-tier ONLY (즉시 blocking FORBIDDEN)** — 두 측정 layer:
  - **layer 1 — delegation-ratio proxy** via spawn-event-v1 (EXISTING wired channel — opt-in default-false, ADR-043 §결정 1). PL 세션당 delegation-worker spawn 수 = coarse proxy. 신규 channel/wiring 신설 0. granularity = 1 spawn = 1 row, per-read-path 검출 불가.
  - **layer 2 — inline-detect hook** = 위 detect hook 과 동일 family. **Read 축 = 영구 advisory 천장** (hook 은 Read-for-Q&A vs Read-as-modification 구별 불가 → fine per-read 정밀 검출 infeasible). Write/Edit/MultiEdit 은 mutation 자체 명백하므로 blockable (Wave2 deny 승격 가능, ADR-060 gate).
  - 승격 = ADR-060 evidence-gate 후만. **§결정 2 inline whitelist 와 disjoint axis** — PL read/compute boundary 는 Orchestrator inline whitelist 과 다른 차원 (entry 신설 0).
- **Orchestrator-self realization cross-ref**: 위 Read-axis "영구 advisory 천장" 을 holder=Orchestrator-self 로 realize 한 것 = **ADR-142** (Orchestrator-self READ/synthesis/verbose-return 규율). ADR-142 는 본 §결정 을 재결정하지 않고 위로 가리키는 disjoint anchor 이며, §결정 2 inline whitelist(WRITE 축)와 disjoint axis — entry 신설 0.

ROI 평가 후 enforcement 강도 결정. §결정 14 Pre-spawn-pin mandate 는 doc-trust enforcement 에 자연 흡수 — hook enforcement layer 확장 시 hook-level 자동 verify 로 격상.

### 결정 10 — ADR-009 계승 관계 (explicit codify)

본 ADR 의 규범(구 ADR-039 로부터 승계)은 ADR-009 (wrapper-only decomposition) 의 **자연 확장** / **explicit 격상**이다. 새 invariant 가 아닌 기존 invariant 의 codification — ADR-009 의 "wrapper agent 0개 → Orchestrator 가 모든 work 을 spawn" 원칙을 **explicit policy 로 stamping** + branch logic 제거 + Inline whitelist codification.

관계 표기 (기술정정 — 표기 방식만 이관, substance 무변): 구 ADR-039 는 frontmatter `amends: ADR-009` 로 이 관계를 표기했다. 재제정 후계인 본 ADR 은 `amends: null` + `supersedes: [ADR-039]` + frontmatter `related_adrs` 의 `ADR-009 # explicit codify 계승` 주석으로 관계를 이관한다 (ADR-054→ADR-127 후계 선례 동형).

### 결정 11 — ADR-022 (Deprecated) 와의 충돌 자동 해소

ADR-022 (Sonnet decider 5-trigger 자동 발동) = Deprecated by ADR-035. 본 정책 하에서도 Sonnet 자동 dispatch 부재 — 사용자 ad-hoc 호출 전용 도구. 사용자 ad-hoc Sonnet 호출 시에도 본 정책 적용 — Sonnet 호출 자체가 subagent spawn (`Agent` tool with `model:sonnet`) 이므로 자연 정합.

### 결정 12 — Cross-ADR invariant 정합 (Ownership ≠ Mechanism normative anchoring)

§결정 3 의 Ownership ≠ Mechanism 분리 (Orchestrator-spawned delegate subagent = Orchestrator-owned) 가 normative 정합을 갖도록, ADR-031 (lane-spawn evidence) + fix-event-v1 contract (Story §10 FIX Ledger) 의 "Orchestrator self-write" / "Writer monopoly: Orchestrator 단독" invariant 는 **Orchestrator-owned delegate subagent 의 self-write 행위를 explicitly cover** 한다:

- ADR-031 Amendment 1 — Orchestrator-owned delegate subagent 의 §14 lane evidence write = "Wrapper Orchestrator self-write" 정의에 포함 (이행 실재 — ADR-031 본문 Amendment 1 절).
- fix-event-v1 `append_rules.writer` — "Orchestrator 단독" 의 Orchestrator 정의 = top-level Claude 세션 + Orchestrator 가 §10 row append 전용으로 spawn 한 delegate subagent 모두 포함 (**2-mechanism** — 계약 원문 verbatim 정합; 이행 실재 = fix-event-v1 §1 Amendment(CFP-275) 단락 + `append_rules.writer` 3항 + §4 Writer monopoly 주석).

**Orchestrator inline (§결정 15) 의 지위 — 계약 writer 정의 확장 아님**: Orchestrator inline write 는 위 계약 writer 정의의 3번째 mechanism 이 아니다 — inline 은 top-level Claude 세션 자체가 수행하는 mechanism 으로서 §결정 15 / §결정 2 entry 5 가 규율하며, 계약 writer 정의(2-mechanism)의 "top-level Claude 세션" 항에 이미 포섭된다 (fix-event-v1 writer 문언 확장 0).

lane plugin agent 의 자체 임의 §10/§14 직접 append 는 여전히 금지 (lane plugin spawn ≠ Orchestrator-owned delegate spawn). fix-event-v1 canonical = wrapper 단일 — sibling sync overhead 0건. (기술정정 note: 구본 §결정 12 는 위 두 amendment 의 "commit 동반 의무" 를 규정했고 그 의무는 원 carrier Story 에서 이행 완료 — 본 §결정 은 이행된 정합 상태를 현재형 invariant 로 재기술한다.)

### 결정 13 — SSOT 인지 표면 (4 SSOT doc — 도입 시점 동일-PR 정렬 발효 완료)

본 정책의 인지 표면 = 4 SSOT doc: `docs/orchestrator-playbook.md` §3.0 / `CLAUDE.md` 오케스트레이션 규칙(subagent default 단락) / `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" / `docs/hotfix-playbook.md` cross-ref 1줄. 이 4 doc 는 도입 시점(원 carrier CFP-275)에 구 ADR-039 와 **동일 PR 안에서 정렬 갱신되어 "Accepted but not effective" normative gap 없이 발효 완료**된 상태다 — 본 §결정 은 그 이행-완료 상태를 현재형으로 기술한다 (§결정 12 동형). (기술정정 note: 구본 §결정 13 의 Phase 1 PR scope 확정·effective date 서사 = 도입기 이력 — 동결 구본 보존.)

### 결정 14 — Pre-spawn-pin mandate (DeveloperPL + branch-creating subagent)

새 git branch 를 생성하는 모든 subagent (특히 DeveloperPLAgent, codeforge-develop:DeveloperAgent, 기타 codeforge-develop role:dev 가 PR 생성 시) 는 **branch 생성 직전 Step 0** 에서 current origin/main HEAD 를 explicit pin 의무. self-claim / Orchestrator packet-provided SHA / local working dir HEAD / 이전 memory SHA 무조건 신뢰 금지.

**의무 절차** (subagent prompt Step 0 cohort):

```bash
# Step 0 — pin current origin/main HEAD (subagent self-execution, single source of truth)
git fetch origin
MAIN_HEAD=$(git rev-parse origin/main)
# 또는: MAIN_HEAD=$(gh api repos/<org>/<repo>/commits/main --jq .sha)
echo "PINNED_MAIN_HEAD=$MAIN_HEAD"
# 모든 후속 branch 생성 + git rebase --onto + PR open 시 본 SHA 사용 의무
# packet-provided reference SHA = 단순 baseline 참고 (subagent self-pin 우선)
```

**Orchestrator post-spawn verify**: DeveloperPL 또는 branch-creating subagent return 직후 Orchestrator 가 PR `head.sha` parent commit 을 current main HEAD (`gh api repos/<org>/<repo>/commits/main --jq .sha` 또는 `mcp__github__list_commits main`) 와 비교. **mismatch = FIX trigger** (구현-side stale-base, RESET=NO, 동일 subagent 재dispatch with explicit current-main-HEAD pin). spurious merge gate 차단 forcing function (playbook §3.0.16 짝).

**self-reset 금지**: re-dispatch 시 subagent prompt 안 **"self-reset 금지 / 기존 작업 content 보존, only rebase the base"** 명시 의무. `git reset --hard origin/<branch>` 같은 destructive 회복 = 이전 작업 손실 → production 이력 회복 곤란.

**Closed enumeration 무손상**: 본 mandate 는 §결정 1 의 mechanism level 강화 (pre-spawn-pin Step 0 추가) 일 뿐 — §결정 1 default subagent spawn 정책 + §결정 2 inline whitelist 무변. (3차 누적 stale-base incident 근거 표 = 동결 구본 §결정 14 보존.)

### 결정 15 — Orchestrator-monopoly Story-file handoff inline write (§결정 2 entry 5 — partial rollback)

§결정 1 closed enumeration 안 "Story file write §1-§14 = subagent spawn 의무" 의 **§9/§10/§14/phase 4-sub-scope 만** inline 허용으로 완화한 **partial rollback** 이다 (약화 방향 declare = 상태 절 "약화 fold 예외" 참조 — ADR-058 §결정 5 evidence-gate 통과, 사용자 explicit directive 기반). 4-sub-scope 외 §1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13 = §결정 1 binary always-spawn 유지. entry 정의 = §결정 2 표 row 5.

**4-sub-scope 명세** (closed enumeration):

1. **§9 verdict inline write** — lane verdict write / GitHub gate label transition. final pl_recommendation (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE) write 시.
2. **§10 FIX Ledger row append** — fix-event-v1 contract row append. Orchestrator 단독 monopoly 보존.
3. **§14 Lane Evidence row append** — ADR-031 lane-spawn evidence trail. Orchestrator self-write monopoly invariant 보존.
4. **Phase transition** — `phase:요구사항` → `phase:설계` → ... label transition (단일 label flip + Story file frontmatter `phase` field 갱신).

**Lane agent self-write exclusion 명시** — lane plugin agent 가 owned section (§1/§2/§3/§4/§5/§6/§7/§8/§11/§12/§13) write 시 = 본 entry scope 외. §결정 1 binary always-spawn 정책 유지.

**Edge case 처리**:

- **Edge-1 — Lane agent self-write 영역 inline write claim**: lane agent owned section 을 Orchestrator inline 으로 write 하는 행위 = 본 entry scope 외 + §결정 1 binary always-spawn violation. ownership 정합 우선 — lane agent self-write 영역은 subagent spawn 의무 유지.
- **Edge-2 — Session 재개 시 stale state 처리**: session 재개 후 Orchestrator-monopoly 4-sub-scope state (예: 이전 §10 row append 진행 중 중단) 가 stale 한 경우 — Orchestrator 가 inline read-verify (§10 row count / 최신 timestamp) 후 inline write 재개. subagent spawn 우회 정당 (state 복원 동안 1-shot subagent overhead 회피).

**Ownership ≠ Mechanism 분리 confirm** — Orchestrator monopoly ownership 보존 + mechanism level inline write 추가 (subagent spawn 과 병존, 양 mechanism 모두 valid — §결정 3/§결정 12 정합).

**exhaustiveness declare**: 4-sub-scope = **closed enum** — 5번째 sub-scope 추가 = 별도 ADR Amendment 의무 (sub-scope 확장 = inline write 영역 확장). inline whitelist entry 자체의 추가 = §결정 2 exhaustiveness declare (8번째 entry = amendment 의무) 적용.

### 결정 16 — Autonomous permission UI behavior (destructive-only ask, reversible auto-proceed)

Orchestrator 의 permission UI behavior normative SSOT. **destructive-only ask, reversible auto-proceed** binary 분류. §결정 1 binary always-spawn 과 disjoint axis (permission UI 차원 vs mechanism 차원).

**Destructive closed enum (8 항목)** — ask permission 의무 (사용자 explicit approval 후 진행):

1. `git reset --hard` (working tree / branch state 복구 불능)
2. `git push --force` / `git push --force-with-lease` (remote ref 비대화식 overwrite)
3. file delete (`rm -rf` / file system level delete — git untracked file 포함)
4. branch delete (`git branch -D` / remote branch delete `gh api -X DELETE`)
5. Issue mutation (close / state change / lock)
6. label create (registry mutation)
7. workflow yaml 변경 (`.github/workflows/**` add / edit / delete — CI/CD policy mutation)
8. ADR row append (`archive/adr/ADR-RESERVATION.md` yaml mutation — sequential append registry, collision rebase 영역)

**외부 visible (destructive enum 동격)** — ask permission 의무: PR create / merge / close / comment to shared main branch + external notification (public Issue comment / Discussion post / external webhook trigger).

**Reversible closed enum (8 항목 — 기술정정: 구본 헤더 "≥6 항목" 은 실 항목 수 8 과 불일치한 stale 표기)** — auto-proceed (no permission UI reflex prompt):

1. local file Edit (`Edit` tool — git reflog 복구 가능)
2. local script run (`python file.py` / `bash script.sh` — destructive side effect 부재 시)
3. temp-file mechanics (`.tmp-*.md` / scratchpad write — manual delete 가능)
4. `.claude/settings.local.json` edit (per-project local config, git untracked default)
5. `git add` (staging area — `git restore --staged` 복구 가능)
6. branch create (`git branch <name>` / `git checkout -b <name>` — `git branch -D` 회수 가능)
7. commit (`git commit` — `git reset --soft HEAD~1` 회수 가능)
8. Edit on `docs/**` (governance docs — git reflog + PR review process 복구 가능)

**Reversibility test 근거**: git reflog (90-day default retention — local edit / commit / branch create / git add recovery point) / Issue history (GitHub immutable audit log) / branch 복구 가능성 (reflog SHA 로 `git branch <name> <sha>` recovery).

**§결정 1 과 disjoint axis** — §결정 1 = mechanism 차원 (inline vs spawn). 본 §결정 = permission UI 차원 (ask vs auto-proceed). 두 axis 완전 disjoint:

| | §결정 1 binary always-spawn (mechanism) | §결정 16 autonomous permission (UI) |
|---|---|---|
| destructive + inline whitelist scope | inline 허용 + ask permission | (whitelist scope 안 mechanism, destructive 여부 별도 평가) |
| destructive + 외 영역 | subagent spawn 의무 + ask permission | (subagent prompt 안 destructive action 도 ask) |
| reversible + inline whitelist scope | inline 허용 + auto-proceed | (whitelist scope 안 mechanism, reversible action auto-proceed) |
| reversible + 외 영역 | subagent spawn 의무 + auto-proceed | (subagent prompt 안 reversible action 도 auto-proceed) |

**사용자 directive verbatim citation** (2026-05-17 KST CFP-848): "아 묻지말고 그냥 하라고" / "쓰잘데기 없는 권한 묻지말고 전부 수정하라".

**exhaustiveness declare**: destructive enum 8 항목 → 9번째 추가 = 별도 ADR Amendment 의무 (강화 방향 ratchet 정합). reversible enum 8 항목 → 9번째 추가 = 별도 ADR Amendment 의무 (auto-proceed 영역 확장 = 사용자 burden 영향). 외부 visible super-class 확장 = 별도 ADR Amendment 의무. 강화 ratchet — closed enumeration **확장만, 약화 0** (ADR-064 §결정 7 symmetric ratchet 정합).

### 결정 17 — Chief author spawn span guideline

Chief author (특히 ArchitectAgent) 의 single spawn 안 monolithic span (15-40min wide drift surface) 패턴을 **anti-pattern declare** + multi-step sequential smaller spawn 권장 (recommendation tier — mechanical enforcement 는 별 sub-CFP carrier).

**Anti-pattern (declared, recommendation tier)**: chief author 단일 spawn 안 (a) deputy 산출물 분석 + (b) Change Plan 전체 draft + (c) ADR draft + (d) Story mirror write + (e) 부속 갱신 + (f) verify 전부를 한 번에 — span ≈ 15-40min 단일 spawn = wide drift surface (mid-spawn 에 sibling PR merge → stale base race amplification).

**Recommended pattern (multi-step sequential smaller spawn, 각 ~5-7min)**:

1. **Skeleton spawn**: frontmatter + section heading + placeholder + RESERVATION row append + slot pre-claim.
2. **Body spawn**: substantive content (Change Plan / ADR §결정 본문 / Story mirror 본문). previous skeleton state passed as input.
3. **Integration spawn**: cross-refs verify + lint validation + finalize + commit. previous body state passed as input.

**Trade-off**: (이득) drift surface per spawn ↓ — preventive complement to ADR-073 Amd 11 SHA pin·Amd 12 mid-spawn drift detection + ADR-168 §결정 1 sub-scope 1-E(spawn prompt SHA-anchor)/1-F(mid-spawn drift detection)/1-G(amendment-slot pre-reservation) (구 ADR-082 Amd 15/16/17 — 현 위치 해소는 ADR-168 처분표 lookup). (비용) spawn 수 ↑ / coordination complexity ↑ / spawn 간 state 전달 불완전 위험. 측정 metric (telemetry carrier deferred): spawn time histogram + per-spawn collision count + chief author span KPI.

**Recommendation tier, NOT mandatory** — monolithic span 채택 시 결격 0. 승격(warning-tier 등재)은 evidence-gated (ADR-060 gate) 별 sub-CFP.

**§결정 1 / §결정 2 무영향 invariant**: multi-step spawn 도 여전히 subagent spawn 의무 (1개 → 3개 sequential 일 뿐). recommendation tier 는 inline whitelist entry 신설 아님. ADR-031 / fix-event-v1 invariant 무변 (span split 은 ownership 영역 변경 아님). paired = ADR-044 Amendment 3 (team-spec yaml multi-step lifecycle pattern — axis disjoint).

### 결정 18 — Inline whitelist entry 6 (merge-time Codex adversarial gate dispatch)

ADR-052 touchpoint #7 (merge-time adversarial gate) 의 Codex worker dispatch 를 Orchestrator top-level inline 으로 허용하는 entry. entry 정의 = §결정 2 표 row 6. 도입 근거 = 구본 §결정 15 의 entry 신설 evidence-gate (ADR-058 §결정 5) 충족 carrier.

**적용 범위 (closed enumeration)**:

1. **dispatch trigger**: ADR-052 touchpoint #7 (merge-time adversarial gate) 단일 — 다른 touchpoint (lane-time) 는 본 entry scope 외 (lane PL/Orchestrator 영역 기존 분류 유지).
2. **dispatch 형식**: ADR-081 D8 file-redirect (`codex exec --sandbox read-only < <promptfile>`) + result-via-file (synchronous block-wait 금지 — non-blocking 회귀 차단 정합).
3. **mutation 0 invariant**: dispatch 행위 자체 = file write / GitHub state change 미발생 (read-only Codex check). 결과 처리(머지 보류 / FIX Ledger row / phase transition)는 §결정 1 (lane spawn) 또는 §결정 2 entry 5 (Story-file 4-sub-scope inline) 영역 — 본 entry 와 disjoint.

**재귀 가드 회피 critical (H1 게이트 연극화 차단)**: sub-agent / PL 을 게이트 owner 로 두면 platform-inherent 재귀 가드 ("subagent → Agent tool 호출 금지") 로 Codex worker spawn 이 silent fallback skip (`subagent_recursion_blocked` fail-mode, ADR-070 Amendment 6) → 게이트 무발동 = 연극화. 따라서 dispatch 주체 = Orchestrator top-level inline 고정 의무.

**§결정 1 binary always-spawn 무손상 (disjoint axis)**: §결정 1 "수정 작업" 정의 영역은 모두 subagent spawn 의무 유지 — 본 entry 는 read-only Codex dispatch mechanism (mutation 0) 만 inline 허용.

**rate-limit retry 영역과 disjoint**: retry primitive inline 허용 압박 (§결정 9 carryover — REJECTED, retry = skill body) 과 본 entry 는 별개 mechanism category (merge-time read-only adversarial dispatch) — closed enumeration 보호 invariant 무손상.

**exhaustiveness**: 추가 entry 신설 = §결정 2 exhaustiveness declare (8번째 entry = amendment 의무) 적용 — 현행 count 는 §결정 2 표를 read 한다.

### 결정 19 — Story-teammate = lead 위임 per-Story Orchestrator (spawn scope 단위 위임)

§결정 1 의 "Orchestrator-only spawn" 불변식을 **폐기가 아니라 "Story scope 단위 위임"으로 재정의**한다. lead (top-level Claude 세션, ADR-009 Orchestrator) 가 적격 Story 별로 **Story-teammate** (background-Agent, SendMessage-addressable Story-runner) 를 dispatch 하고, 각 Story-teammate 는 **자기 Story scope 안에서만** lane PL subagent 를 spawn 한다. 이것이 ADR-134 (병렬 적격성 5조건 + merge-time 재검증 + Orchestrator per-Story dispatch) 의 **spawn-권한 layer** 다.

본 §결정은 **spawn-scope 위임 축** 이며, §결정 2 의 **inline vs spawn mechanism 축** 과 disjoint 다. inline whitelist 는 본 §결정 으로 **변경 0** (entry 신설 아님 — 현행 count 는 §결정 2 표 read).

**dispatch 메커니즘 = background-Agent-as-Story-runner (검증된 경로)**: dispatch 주체 = lead 가 `Agent` tool 로 spawn 한 background-Agent (run_in_background, SendMessage addressable). background-Agent 는 depth-0 독립 세션이므로 자기 sub-agent tree 보유 (lane PL → SubAgent fan-out; depth 0→1→2 실작동 dogfood 실증). **공식문서 의존 회피 명시**: 본 §결정은 공식문서가 보장하는 background-Agent → 자기 sub-agent spawn 경로에만 의존하며, 공식문서가 침묵하는 agent-teams "teammate" 특정 dispatch 경로에 의존하지 않는다 (over-claim 차단, ADR-119 검증-후-단언 정합).

**2-level 토폴로지 (closed)**:

- **lead 1 + teammate N** — lead 가 유일 dispatch 주체. Story-teammate 는 자기 Story scope 안에서 lane PL → SubAgent spawn (depth 0→1→2).
- **teammate → teammate spawn 불가 (lead 고정)** — 산업 lead-worker 패턴의 bounded 1-level 위임. 무한 재귀 중첩과 구분 (resource-aware concurrency limit 걸린 bounded 위임).
- **scope-confine = Orchestrator-only 명목 보존** — teammate 의 spawn 권한은 "lead 가 confine 한 Story scope" 안에서만 유효. "Orchestrator(lead) 만 spawn 위임 권한 보유" 불변식 보존 — teammate 는 위임받아 자기 scope 안에서 실행하는 delegate (§결정 3 Ownership ≠ Mechanism 정합 — 위임한 spawn 행위의 ownership identity = lead).

**stall 마찰 정직 기술 (구조적 한계 — 은폐 금지)**: child (손자 = teammate 가 spawn 한 lane PL 의 SubAgent) 완료 통지가 parent (lane PL) 아닌 **lead (main)** 로 surface 되는 경우 → parent 는 오지 않는 통지를 기다리며 무한대기 (stall). **처리 책임 (dispatch 운영절차 — playbook §4.5 + ADR-134 carrier)**: lead 는 dispatch 한 모든 teammate 의 진행을 **능동 모니터** 하고, stall 검출 시 **force-resume (SendMessage 로 parent 깨우기) 또는 TaskStop (회수)** 책임을 진다. 이 책임은 옵션이 아니라 dispatch 운영절차의 의무 단계 — 마찰을 메커니즘으로 완전 제거하지 못함을 정직히 기술하고 (ADR-119 검사연극 금지), lead 능동 감독으로 흡수한다. (정량 게이트화 = §결정 20 / ADR-139.)

**§결정 1 binary always-spawn 무손상**: 위임받은 Story-teammate 도 자기 Story scope 안 수정 작업을 **subagent spawn 으로 수행** (inline 우회 아님). §결정 5 lane plugin 0 변경 invariant 무손상. ADR-031 §14 + fix-event-v1 §10 Orchestrator monopoly 무손상 (dispatch 토폴로지 변경 ≠ ownership 변경).

**ADR-009 amends 관계 정합**: "Orchestrator 가 모든 work spawn" 은 "Orchestrator 가 spawn 위임의 단일 권위" 로 정합 확장 — Story-teammate 는 lead 가 Story scope 단위로 위임한 delegate 이며 자생적 spawn 권한을 갖지 않는다 (2-level bounded).

### 결정 20 — background subagent spawn liveness (ADR-139 cross-ref)

lead 가 background subagent/worker 응답을 대기할 때의 **유한성(liveness)** = §결정 19 (lead force-resume/`TaskStop` 개입 축)의 **정량 mechanical 게이트화**다. 원리 carrier SSOT = ADR-139 (background-wait liveness gate). 본 §결정 = spawn-권한 기반 cross-ref — 게이트 소유 = Orchestrator/lead 고정(INV-L4)이 §결정 1/§결정 19 의 spawn-권한 위임 topology 에 근거함을 명시한다.

**ADR-139 4 불변식 (INV-L1~L4) 상속**:

- **INV-L1 (wall-clock ceiling 존재)** — background subagent 대기 지점에 명시적 max-wait 상한 (암묵 무한 금지). stall 판정 = outcome ground-truth 기반 (internal proxy loop-lag/CPU 금지, ADR-119 상속).
- **INV-L2 (fail-open 금지)** — stall = inconclusive (PASS 자동승격 금지, PASS-only-if-explicit). 부분 stall → ANY(inconclusive) → 전체 inconclusive.
- **INV-L3 ("0-byte ≠ stall" 3-state marker)** — wall-clock ceiling + progress-marker (output mtime + content grep + task-notification). 0-byte stdout 단독 stall 단정 금지.
- **INV-L4 (게이트 소유 = Orchestrator/lead 고정)** — worker 자가-spawn 금지. 값 순서 불변식 `timeout N < liveness max-wait`. 이 소유 고정이 본 ADR spawn-권한 근거 — 대기 주체 ↔ 판정 주체 분리 (worker self-attestation 차단).

**§결정 19 body 무변경**: §결정 19 의 "lead force-resume/TaskStop 책임" 은 정성 기술 — 본 §결정 = 그 개입 축을 ADR-139 4 불변식 (wall-clock 상한 + progress-marker 관측 + fail-open 금지 + 게이트 소유 Orchestrator/lead 고정(INV-L4)) 으로 정량화하는 cross-ref. (기술정정 — 구본 동 위치 괄호 열거의 4번째 항 "re-dispatch max-retry cap 2" 는 INV-L4 오기의 canonical 정정 대상; cap 값 SSOT = parallel-dispatch-protocol-v1 §6.3.1.)

**§결정 9 slot 미침범 (disjoint axis)**: §결정 9 detect hook slot = **inline-write-detect 축** (Orchestrator 직접 mutation 감지). 본 §결정 = **background-wait liveness (완료 감지) 축** — 대기 중 subagent 생존 판정. 두 축 완전 별개 — liveness 를 §결정 9 에 밀어넣으면 scope 오염이므로 별도 §결정 으로 분리 유지.

**§결정 2 inline whitelist 무손상 (disjoint axis)**: liveness 게이트는 "inline vs spawn" (mechanism 차원) 이 아니라 "대기 중 subagent liveness 판정" (완료-감지 차원) — entry 신설 아님 (현행 count 는 §결정 2 표 read). §결정 1 binary always-spawn 무변경 — 대기 대상 = 이미 spawn 된 subagent 응답이며 spawn 의무와 무관.

### 결정 21 — Inline whitelist entry 7 (Tier-3 measurement-channel ledger row append)

Orchestrator 가 spawn-event-v1 (또는 sibling Tier-3 measurement channel) 실측 aggregate row 를 task-notification/spawn-completion 수신 시점에 구조화 CLI/args-file invocation 으로 append 하는 measurement 배선 entry. entry 정의 = §결정 2 표 row 7. 도입 근거 = 구본 §결정 18 의 entry 신설 evidence-gate (ADR-058 §결정 5) 충족 carrier.

**적용 범위 (closed enumeration)**:

1. **dispatch trigger**: Orchestrator 가 Agent task-notification `<usage>` 블록 또는 spawn-completion 을 수신하는 시점 단일 — 다른 mechanism(수정 작업)은 본 entry scope 외.
2. **invocation 형식**: `python3 scripts/lib/append_spawn_event.py --args-file <ascii-path>` (UTF-8 JSON content) — argv 는 ASCII path 만, 한국어 lane_label 등 실값·content 는 파일 내부 (string-interp injection 표면 제거).
3. **mutation 0 invariant (measurement-only)**: append 행위 자체 = spawn-event.jsonl 한 row record-only. gate/block/deny 미발생 · 0-API · transcript content/path 미도달. outcome/termination_cause 는 판정 결과 저장이지 판정 로직 inline 실행 아님.

**evidence-gate 통과 논거 (ADR-058 §결정 5)**: entry 5 (Story-file 구조화 append) · entry 6 (merge-time Codex dispatch) 와 동형 — "Orchestrator monopoly 소형 구조화 append · free-form content 0 · 판정 로직 부재" 3-조건 충족. 강화 방향 additive only (measurement 배선 1종 narrow 추가 — inline 허용 범위 일반 확대 아님).

**§결정 1 binary always-spawn 무손상 + writer monopoly 무약화**: 수정 작업 영역 spawn 의무 무변경 — 본 entry 는 Tier-3 measurement 소형 구조화 append mechanism 만 inline 허용. ledger write ownership = Orchestrator 단독 (§결정 3 / spawn-event-v1 append_rules) 유지, lane plugin agent 자체 append = 여전히 policy_violation (약화 0). paired = spawn-event-v1 Amendment 4 + ADR-043 Amendment 5 + ADR-163 §결정 13 realization.

**exhaustiveness**: 추가 entry 신설 = §결정 2 exhaustiveness declare (**8번째 entry 신설 = 본 ADR amendment 의무**) 적용.

## 결과

- Orchestrator binary always-spawn (§결정 1) + closed inline whitelist 7-entry flat 단일표 (§결정 2) 가 단일 record 로 재계보화 — "inline 으로 충분한가" 결정 분기 제거 본질 무변경.
- Ownership ≠ Mechanism (§결정 3/12) / scope (§결정 4/7) / lane plugin 0 변경 (§결정 5) / hotfix 동일 적용 (§결정 6) / doc trust + enforcement 현황 (§결정 8/9) / 계승·해소 관계 (§결정 10/11) / 인지 표면 (§결정 13 — 도입 시점 동일-PR 정렬 발효 완료) invariant 전량 승계.
- 운영 discipline 4종 (§결정 14 pre-spawn-pin / §결정 16 permission UI / §결정 17 span guideline / §결정 19·20 위임 topology + liveness) 원번호 보존 승계.
- 구본 대비 정리: 분산 3곳 표(base 4 + entry 5 + entry 6) + prose(entry 7) → 7-entry flat 단일표 / "현 N-entry" dated snapshot → §결정 2 라이브 포인터 / `## 결정 (17)` 류 stale 괄호 카운트 제거 / dated 진행 서사·저작 증적 제거 (동결 구본이 이력 담보).
- (−) 의미 무변경(semantic fidelity) 검증 oracle 은 기계화 불가 (ADR-167 §결정 7 honest ceiling) — 담보 = no-substantive-change 선언 + 재제정 처분표 + 8-lane 리뷰 신구 대조. "완전 봉인" 류 hard-claim 없음.
- (−) 기계 결박 5표면 (disjoint-axis lint + 자매 test + workflow 주석 + return-envelope-v1 + spawn-event-v1/test_ac4) 의 재지향·재저작 = Phase 2 atomic bundle — Phase 1 종료 상태에서 구본·결박은 무변 GREEN.

## 재제정 처분표 (disposition table — ADR-167 §결정 4(b) 필수 요소 (b))

> 구 §결정/amendment → 신 위치 매핑(zero-drop = 원 §결정 13 + amendment-신설 §결정 8 + amendment 12 = **33 row**) + 처리 태그. 태그 enum = carrier-preserved / 기술정정 / obsolete제거 (+ 본 건 신규 태그 `carrier-preserved (inline fold into §결정 M)` — 전용 본문 헤딩이 없는 in-place fold형 amendment 용, 앵커 = frontmatter `amendment_log[N]` + fold 대상 §결정). 구 앵커 열 = 동결 ADR-039 에서 row 단위 spot-check 지점.

### (1) 원 §결정 1-13 (ADR-039 최초 codify, CFP-275) → §결정 1-13 (번호 보존)

| 구 §결정 | 신 위치 | 태그 | 구 앵커 (ADR-039) | 비고 |
|---|---|---|---|---|
| §결정 1 (binary always-spawn) | §결정 1 | carrier-preserved | `### 결정 1` | 수정 작업 closed enumeration + branch logic 제거. Story-file 4-sub-scope 제외절 = §결정 15 partial rollback 기반영분 그대로 승계 |
| §결정 2 (inline whitelist) | §결정 2 | **기술정정(구조개선)** | `### 결정 2` | base 4-entry 표 + 분산 entry 5/6(§결정 15/18 절내 표) + entry 7(§결정 21 prose) → **7-entry flat 단일표 통합** (규범 무변경 — dated 표기 기술정정(entry 1 "5번째 entry 신설 아님"→"신규 entry 신설 아님") + entry 5/6/7 저작 증적 제거 + 위치 통합 + entry 7 표-row 형식 통일). "Count 정합" 이중 서술 → 정형 선언 라인 1개 + 역사 해석 note. Amd 11 disjoint-axis note = in-place fold 존치. exhaustiveness("8번째 entry = amendment 의무") 현재형 승계 |
| §결정 3 (Ownership ≠ Mechanism) | §결정 3 | carrier-preserved | `### 결정 3` | "Amendment 2" 시점 표기 → "§결정 15" 앵커 재지정만 |
| §결정 4 (scope 한정) | §결정 4 | carrier-preserved | `### 결정 4` | — |
| §결정 5 (lane plugin 0 변경) | §결정 5 | **기술정정** | `### 결정 5` | 2026-05-08 시점 deputy·contract 개별 열거(구명칭 OpRiskArch/DataMigrationArch 등) → 현행 roster/registry skill SSOT pointer 로 교체. "변경 0" invariant 무변 |
| §결정 6 (hotfix 동일 적용) | §결정 6 | carrier-preserved | `### 결정 6` | — |
| §결정 7 (consumer scope) | §결정 7 | carrier-preserved | `### 결정 7` | — |
| §결정 8 (Phase 1 doc-only trust) | §결정 8 | **기술정정** | `### 결정 8` | "Phase 1" 도입기 라벨 → "기본 enforcement = doc trust" 현재형 (§결정 9 hook 실현분과의 병존 명시). 인지 표면 5곳 무변 |
| §결정 9 (Phase 2 enforcement deferred) | §결정 9 | **기술정정** | `### 결정 9` | Amd 4/8/9 in-place fold 의 "Update (Amendment N)" 진행 서사 제거 → 현재형 최종 상태만 재기술 (Write/Edit/MultiEdit = IMPLEMENTED Wave1 / Read 축 영구 advisory 천장 / mcp·Bash-redirect deferred / ADR-142 cross-ref stub) |
| §결정 10 (ADR-009 amends 관계) | §결정 10 | **기술정정** | `### 결정 10` | 규범 substance(자연 확장/explicit 격상) 무변. 관계 표기만 frontmatter `amends` → `related_adrs` 주석 이관 (ADR-054→ADR-127 선례 동형 — §7 OQ-3 B안) |
| §결정 11 (ADR-022 충돌 해소) | §결정 11 | carrier-preserved | `### 결정 11` | — |
| §결정 12 (Cross-ADR amendment 의무) | §결정 12 | **기술정정** | `### 결정 12` | 일회성 "commit 동반 의무" = 원 carrier 에서 이행 완료 → 이행된 정합 상태를 현재형 invariant 로 재기술. attestation = 존재-attest 한정(ADR-031 본문 Amendment 1 절 + fix-event-v1 §1 Amendment(CFP-275) 단락 실재 — firsthand 확인; 문언 내용 SSOT = 각 원문). writer 정의 = **2-mechanism** (inline 은 §결정 15 규율 — 계약 writer 확장 아님) |
| §결정 13 (Phase 1 scope 4 SSOT doc) | §결정 13 | **기술정정** | `### 결정 13` | dated effective-date·PR scope 확정 서사 제거 → 도입 시점 동일-PR 정렬 발효 완료 상태의 현재형 재기술 (§결정 12 동형 — 상시 동기 의무 신설 0) |

### (2) amendment-신설 §결정 14-21 → §결정 14-21 (번호 보존)

| 신 §결정 | 유래 Amd | 태그 | 구 앵커 (ADR-039) | 비고 |
|---|---|---|---|---|
| §결정 14 (Pre-spawn-pin mandate) | Amd 1 | **기술정정(부분)** | `### 결정 14` | 행위 규범 전량 보존 (Step 0 pin 절차 + post-spawn verify + self-reset 금지). 3-row incident evidence 표 + verification evidence 목록 = 저작 증적 제거 (동결 구본 보존) |
| §결정 15 (Story-file handoff entry 5) | Amd 2 | **기술정정(구조개선)** | `### 결정 15` | 4-sub-scope + exclusion + Edge-1/2 + exhaustiveness 보존. 절내 5-entry 확장 mini-table 삭제 (row 5 = §결정 2 flat 표). "6번째 entry 추가 의무" dated arithmetic → §결정 2 라이브 포인터. **weakening_partial 최종 상태 그대로 승계** (상태 절 약화 fold 예외 declare) |
| §결정 16 (permission UI) | Amd 3 | **기술정정(부분)** | `### 결정 16` | destructive 8 + 외부 visible + reversible 8 + disjoint 표 + directive verbatim 보존. "Reversible closed enum (≥6 항목)" 헤더 ↔ 실 8 항목 불일치 stale 표기 기술정정 + Destructive 헤더 "(≥8 항목)"→"(8 항목)" 확정 표기 동조(closed enum 9번째 = amendment 의무와 정합 — 확장만, 약화 0) |
| §결정 17 (chief span guideline) | Amd 5 | **기술정정(부분)** | `### 결정 17` | anti-pattern + 3-step + trade-off + recommendation tier 보존. "ADR-082 Amd 15/16/17" 인용 → ADR-168 §결정 1 sub-scope 1-E/1-F/1-G 현 위치 해소 (ADR-168 처분표 lookup). META-self-application demonstration 서사 = 저작 증적 제거 |
| §결정 18 (entry 6 Codex dispatch) | Amd 6 | **기술정정(구조개선)** | `### 결정 18` | 적용 범위 3항 + H1 재귀 가드 rationale + Amd 4 disjoint 논거 보존. 절내 6-entry 확장 mini-table 삭제 (row 6 = §결정 2 flat 표). "현 5-entry / 7번째 entry" dated arithmetic → §결정 2 라이브 포인터 |
| §결정 19 (Story-teammate 위임) | Amd 7 | **기술정정(부분)** | `### 결정 19` | 재정의 + dispatch 메커니즘 + 2-level 토폴로지 + stall 마찰 정직 기술 + lead 처리 책임 보존. "현 6-entry" snapshot → 라이브 포인터. "Phase A 위험 흡수 (E2/E3 가드 아직 LIVE 아님)" 도입기 한시 단락 = obsolete 제거 (lead 능동 모니터 책임 규범은 존치; atomic claim 은 ADR-133 으로 LIVE) |
| §결정 20 (liveness ADR-139 cross-ref) | Amd 10 | **기술정정(부분)** | `### 결정 20` | INV-L1~L4 상속 + §결정 9 slot 미침범 + §결정 19 관계 보존. "현 6-entry" snapshot → 라이브 포인터. 구본 §결정 20 괄호 열거 4번째 항 "re-dispatch max-retry cap 2" → INV-L4(게이트 소유 고정) 기술정정 — cap-2 값은 본문 미승계 **삭제**(값 SSOT = parallel-dispatch-protocol-v1 §6.3.1 "max-retry cap = 2", 삭제 정당) |
| §결정 21 (entry 7 measurement) | Amd 12 | **기술정정(구조개선)** | `### 결정 21` | 적용 범위 3항 + evidence-gate 3-조건 논거 + monopoly 무약화 보존. entry 7 정의 prose → §결정 2 flat 표 row 이동 (표-row 형식 통일). "8번째 entry = amendment 의무" exhaustiveness = §결정 2 로 현재형 승계 |

### (3) amendment 1-12 처분 (provenance — 이원 앵커)

> 신설형(전용 본문 헤딩 보유) 앵커 = 본문 `### 결정 N` 헤딩 / in-place fold형(전용 헤딩 부재) 앵커 = frontmatter `amendment_log[N]` + fold 대상 §결정.

| Amd | carrier | 신 위치 | 태그 | 구 앵커 (ADR-039) | 비고 |
|---|---|---|---|---|---|
| 1 | CFP-895 | §결정 14 | carrier-preserved | `amendment_log[1]` + `### 결정 14` | Pre-spawn-pin mandate 신설형. direction: strengthening |
| 2 | CFP-1340 | §결정 15 + §결정 2 row 5 | carrier-preserved | `amendment_log[2]` + `### 결정 15` | **direction: weakening_partial (유일)** — §결정 15 partial rollback 자체가 최종 effective 상태 (상태 절 약화 fold 예외 declare 참조, arithmetic 병합 불요) |
| 3 | CFP-1340 | §결정 16 | carrier-preserved | `amendment_log[3]` + `### 결정 16` | permission UI 신설형 |
| 4 | CFP-1354 | §결정 9 | **carrier-preserved (inline fold into §결정 9)** | `amendment_log[4]` (전용 헤딩 부재) | rate-limit second-order risk carryover — ADR-109 SSOT + "entry 신설 REJECTED, retry = skill body" 기록. 구본 본문 미반영(`amendment_log[4]` 전용 — body ADR-109 언급 0건) — 본 재제정이 §결정 9 재기술 + §결정 18 disjoint 논거로 최초 본문 승계 |
| 5 | CFP-1438 | §결정 17 | carrier-preserved | `amendment_log[5]` + `### 결정 17` | chief span guideline 신설형 |
| 6 | CFP-2458 | §결정 18 + §결정 2 row 6 | carrier-preserved | `amendment_log[6]` + `### 결정 18` | entry 6 신설형 (evidence-gate 충족 carrier) |
| 7 | CFP-2488 | §결정 19 | carrier-preserved | `amendment_log[7]` + `### 결정 19` | Story-teammate 위임 신설형 (ADR-134 paired) |
| 8 | CFP-2521 | §결정 9 | **carrier-preserved (inline fold into §결정 9)** | `amendment_log[8]` (전용 헤딩 부재) | DevPL self-read advisory detection D3 slot (layer 1/2 + advisory 천장) — §결정 9 재기술에 승계 |
| 9 | CFP-2544 | §결정 9 | **기술정정 (inline fold into §결정 9)** | `amendment_log[9]` (전용 헤딩 부재) | Write/Edit/MultiEdit 축 IMPLEMENTED Wave1 — "Update (Amendment 9)" 진행 서사 제거, 최종 상태만 현재형 재기술 (ADR-115 paired) |
| 10 | CFP-2549 | §결정 20 | carrier-preserved | `amendment_log[10]` + `### 결정 20` | liveness cross-ref 신설형 (ADR-139 sibling) |
| 11 | CFP-2770 | §결정 2 | **carrier-preserved (inline fold into §결정 2)** | `amendment_log[11]` (전용 헤딩 부재) | disjoint-axis note (display 축 — ADR-143 Amendment 2 paired) — §결정 2 note 로 존치 |
| 12 | CFP-2850 | §결정 21 + §결정 2 row 7 | carrier-preserved | `amendment_log[12]` + `### 결정 21` | entry 7 신설형 (`reinterpretation: false` marker 보유) |

**공통 dated-history 제거 (전 row 적용)**: "Update (Amendment N)" 진행 서사 / 시점별 entry 누적 arithmetic ("현 4/5/6-entry") / incident evidence 표 / verification evidence 목록 / META demonstration·Phase A 한시 서술 / `## 결정 (17)` stale 괄호 카운트 = 의무·금지·조건·예외가 아닌 **저작 증적·시점 표기** → 본 ADR 본문 전량 제거 (동결 구본 ADR-039 가 이력 담보). 이는 문언 실질 변경이 아닌 obsolete 제거·기술 정정 (재제정 허용 변경 4종 안).

**비-§결정 섹션 처분**: 구본 컨텍스트(사용자 directive verbatim / Gap 분석) 중 규범 원천(directive 4 발화)은 본 ADR 컨텍스트로 승계, Gap 분석·"회피된 대안"(A~D)·"외부 fact"·"검증 채널"·"결과/Out-of-scope" = 도입기 rationale·이력 서사 → **동결 구본 보존** (ADR-168 선례 동형 — 각 §결정 이 필요 rationale 을 자체 내장하도록 재기술했으므로 규범 손실 0. 회피된 대안의 거부 논거 중 살아있는 것: 대안 A selective spawn 거부 = §결정 1 본문 / 대안 B 즉시 hook enforcement 거부 = §결정 8 doc trust + §결정 9 enforcement 현황 / 대안 C lane plugin 적용 거부 = §결정 5 / 대안 D 무제한 재귀 거부 = §결정 19 2-level bounded — 전부 §결정 내장 승계).

## 관련 파일

**기계 결박 5표면 (Phase 2 재저작·재지향 — atomic bundle)**:

- `scripts/lib/check_disjoint_axis_whitelist.py` (+ thin wrapper `scripts/check-disjoint-axis-whitelist.sh`) — 결박 1: `_DEFAULT_ADR_REL`(구본 파일명 하드코드) + `_EXPECTED_BASE=4`/`_EXPECTED_EFFECTIVE=6` 상수 + `### 결정 2/15/18` 헤딩·"N번째 entry" 문자열 결박 → **본 ADR 대상 + declared-vs-actual self-consistency(§결정 2 정형 선언 ↔ flat 표 row count) 알고리즘으로 재저작** + 대상 ADR Superseded-status 동결사체 가드
- `scripts/test-check-disjoint-axis-whitelist.sh` — 결박 2: 자매 discriminating test — sed 콘텐츠 앵커 → 구조-패턴(마지막 `| N |` row) 앵커 + fake row `| 99 |` out-of-band + M1~M9 mutation 세트(정의 소재 = Story CFP-2869 §8.3 — M9 = 섹션 경계 lookahead 검증) + negative-control fixture (C3 부정어미 오탐 0)
- `.github/workflows/disjoint-axis-whitelist-lint.yml` — 결박 3: 헤더 주석 "(C1) == 6" pin → self-consistency 서술로 동기 재기술
- `docs/inter-plugin-contracts/return-envelope-v1.md` — 결박 4 (lint `_DEFAULT_LDOC_REL` 검사 대상): §5 disjoint-axis 선언(:81)의 "현재 유효 6-entry"·"7번째 whitelist entry 가 아니며" → 7-entry + "8번째 entry 가 아니며" 현행화 + :79 §5 헤딩·:103 §9 cross-ref 의 "ADR-039 §결정 2" 인용 재지향 + **PATCH bump + MANIFEST row 갱신**
- `docs/inter-plugin-contracts/spawn-event-v1.md` + `tests/unit/cfp_2850/test_ac4_writer_monopoly.py` — 결박 5: writer 정의 authority 인용(ADR-039 §결정 2/3) 번호 재지향(:16 related_adrs 주석 포함) + :145 §2.1.5 disjoint-axis note 의 "6-entry" stale → §결정 2 현행 표(7-entry) 현행화 + "ADR-039" 문자열 assert 동기 갱신 + **PATCH bump + MANIFEST row 갱신** (changelog dated 이력 인용은 보존)

**Phase 2 전역 re-grep 규율**: 위 결박 표면의 라인 번호(spawn-event-v1 :16/:145, return-envelope-v1 :79/:81/:103 등)는 Phase 1 저작 시점 실측 스냅샷이다 — Phase 2 재지향 시 파일별 전 인용 라인을 re-grep 으로 재실측한 뒤 전수 재지향한다 (라인 드리프트·누락 방어).

**Phase 2 나머지 대상**:

- `archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` — `status: Superseded by ADR-170` 전이 (frontmatter 최소행, 본문 byte-frozen)
- `docs/adr-amendment-threshold-baseline.yaml` — ADR-039 행 제거 17→16 (`--write-baseline` 단일 writer 경유, 손편집 금지)
- `docs/parallel-work/section-ownership.yaml` — `owner_adr: ADR-039` 2행 (CLAUDE.md 오케스트레이션 규칙 / playbook §3) re-home
- A분류 직접 규범 anchor re-home: `CLAUDE.md` / `docs/orchestrator-playbook.md` / `docs/consumer-guide.md` / `docs/hotfix-playbook.md` / `docs/inter-plugin-contracts/fix-event-v1.md` / `plugins/{codeforge-design,codeforge-requirements,codeforge-pmo}/CLAUDE.md` (**PATCH bump + marketplace sync 연동 — ADR-063**) / `docs/architecture/codeforge-family.md` (flat spawn invariant + inline-write mechanical block anchor 2줄) / `docs/domain-knowledge/domain/orchestrator-discipline/spawn-default.md`
- 광역 역참조 sweep (타 ADR cross-ref / 스크립트 주석 / skill·template / 이력) = **follow-up 분리** (ADR-168 선례 — 구본 파일 존속으로 링크 불파손)

**Phase 1 (본 Story)**:

- `archive/adr/ADR-RESERVATION.md` — ADR-number row 170 신설 (dual-key 3-leg)

## 해소 기준

N/A — permanent policy (Orchestrator subagent default + inline whitelist 상시 적용, is_transitional: false). 구 ADR-039 의 동일 선언 승계.

## Amendment 2 (CFP-2994 — 저작 ⊥ 전사 4번째 형태 + `receipt_state` 도달-전용 경계 + 2층 공백 declare)

> **[Amendment 2 / CFP-2994, 2026-08-18 KST]** 축 = **authority**(누가 어떤 사실의 기록자인가). 본 Amendment 는 §결정 2 의
> inline whitelist 7-entry enumeration 을 **변경하지 않는다** — entry 신설 0 · entry 축소 0 · count 무변경. 추가되는 것은
> **기록 귀속의 분류 1형**이다. carrier = CFP-2994(수령 사실의 single-writer 부재).

### A2-1 — 신설: 저작 ⊥ 전사 위반의 **4번째 형태** ④

기록 표면(Story 절 · 원장 · git 커밋 등)의 소유자가 타 주체의 몫을 처리하는 형태를 다음 4형으로 분류한다. ①~③ 은 기존 분류의
재기술(의미 무변경)이고 **④ 가 본 Amendment 의 신설분**이다.

| 형태 | 내용 | 판정 |
|---|---|---|
| ① | 타 주체 산출을 **verbatim 전사 + 귀속 명시** | 합법 (§결정 2 entry #5 가 허용하는 정확한 형태) |
| ② | 타 주체 사실을 **자기 관측으로 덮어쓰기** | 위반 |
| ③ | **관측 주체 없이** 상태를 창작 | 위반 |
| ④ | **타 주체 저작을 흡수하며 귀속을 자기로 표기** (신설) | 위반 |

**④ 가 기존 3형에 걸리지 않는 이유**: 내용이 무손실이므로 ② 가 아니고, 실 저작이 존재하므로 ③ 도 아니며, 귀속이 없으므로
① 의 합법 조건(귀속 명시)도 불성립이다. 즉 **세 술어 전건이 거짓인 채 위반이 성립**한다.

**실 발현 `[verified — CFP-2994 설계 lane 자기 관측]`**: 본 Story 를 진행하는 설계 lane 안에서, 한 deputy 의 커밋이 lane PL 의
미커밋 저작을 함께 스테이징해 자기 커밋에 담았다. 커밋 메시지는 그 deputy 의 작업을 말하는데 담긴 저작의 일부는 PL 것이었고
**원장(git log)이 그 귀속을 잘못 말한다**. 내용은 무손실이었다. 기전 = 복수 에이전트가 같은 worktree·같은 index 를 공유할 때
`git add <dir>`/`git add -A` 가 형제의 미커밋 저작을 스테이징한다 — `index.lock` 은 **동시성만** 막고 **범위 침범은 막지 않는다**.
근거 = Phase 1 PL 산출 §R + 해당 커밋 `--stat`.

★ 원 사건(CFP-2994 §1)과의 관계: 원 사건은 **내용이 증발**했고 본 발현은 **귀속만 틀렸다** — **피해 축이 다르나 기전은 동형**
(기록 표면의 소유자가 타 주체 몫을 자기 것으로 처리). 두 사건을 같은 심각도로 읽지 말 것.

### A2-2 — 예외(§결정 2 entry #5)는 **좁힐 수 없다** (결론)

*"Orchestrator 가 타 주체의 수령 사실을 §9 에 쓰는 경로를 막으면 된다"* 는 처방은 **성립하지 않는다**:

1. **소급 위법화** — CFP-2994 §9.1~§9.4 의 원장 retrofit 은 Orchestrator 가 타 주체 수령 사실을 전사한 것이며, 그것이
   §결정 2 entry #5 가 허용하는 정확한 형태다. 예외를 좁히면 **이미 옳게 수행된 전사가 위법**이 된다.
2. **writer monopoly 와 충돌** — §9/§10 은 Orchestrator write monopoly(entry #5) 이므로, Orchestrator 를 그 표면에서 배제하면
   기록자가 0 이 된다.

⇒ **채택 방향은 예외 축소가 아니라 분류 확장**이다(A2-1 ④ 추가). ADR-064 §결정 7 evidence-gated symmetric ratchet 상
**강화 방향**이며 ADR-058 §결정 5 약화 evidence-gate 비대상.

### A2-3 — 2층(지시 ⊕ 산출물): 규범으로 완결 · 기제로 공백

원 사건의 파괴적 지시(*"미수령으로 declare 유지"*)는 **명제가 아니라 지시**다. 두 층을 분리 성문한다.

- **산출물 층** — 기록된 상태값·귀속·근거 셀이 대상. 기계 술어를 붙일 표면이 실재한다.
- **지시 층** — 발화된 지시가 가산적(additive)인가 파괴적인가가 대상.

★ **원 지시 함정은 재발하지 않는다** `[verified]`: *"미수령으로 declare"* 의 `미수령` 이 「공란 아닌 명시 상태값」 요구를
충족하는 함정은 **셀 공란을 재는 술어에만** 작동하고, 수신자 산출물의 **delta 부호를 재는 술어는 통과하지 못한다**.

★ **그러나 지시 층은 기제로 공백이다 — 감추지 않는다**:

- **압박 당사자만 평가 가능** — delta 부호 판정에 *"지시가 없었다면 무엇을 썼을지"* 라는 **반사실**이 필요하고, 그것을 아는
  주체는 지시 수신자 단 하나다. 검출을 하위 주체의 자발적 정직에 위임하는 형상이며 **원 사건의 복구 경로(PL 자진 신고)와 같은 기전**.
- **관측면 원리적 부재** — 지시는 spawn prompt·메시지 = 런타임 ephemeral.

⇒ 지시 층 규범의 등급 = **`normative` 이나 집행 표면 0**. tier ⊥ 집행을 분리 표기하며, 「차단한다」로 읽히는 문면을 쓰지 않는다
(ADR-119 §결정 10 outcome-honesty 상속). 실효 이득은 **「1개 누락 → 2개 독립 누락 필요」** 뿐이다.

### A2-4 — `receipt_state` = 도달(arrival) 전용 경계

수령 상태 field 의 정의역을 **도달 사실**로 한정한다.

- **허용** — 산출물이 도달했는가 · 어느 주체 채널에 도달했는가 · 무엇을 근거로 그렇게 판정했는가.
- **금지** — 도달분의 **충분성 · 품질 · 채택 가치** 판정.

근거: 「받았다 ⇒ 쓸 만하다」 함의가 붙는 순간 그 field 는 성과 verdict 가 되고, verdict 판정 권한은 ADR-139 INV-L4
(*"대기 주체 ↔ 판정 주체 분리 (worker self-attestation 차단, 신뢰 경계)"* — `archive/adr/ADR-139-background-wait-liveness-gate.md:71`
verbatim)가 lead 에 고정한다. 도달-전용 경계가 **INV-L4 를 침범하지 않는 유일한 형태**다. 상세 = ADR-139 Amendment 3.

### A2-5 — cross-ref

- **ADR-139 Amendment 3** — P-1(수령 사실 single-writer) ↔ INV-L4 정의역 분리 + amendment slot 충돌 오라클 교훈 SSOT.
- **Change Plan** `mclayer/codeforge-internal-docs` `wrapper/change-plans/cfp-2994-receipt-single-writer.md` §10 — 오라클 교훈 전문.
- **CFP-2929 (ADR-139 Amendment 2, §결정 8)** — mechanism 축이며 본 authority 축과 disjoint (상세 = ADR-139 Amd 3).

### A2-6 — 정직 천장

- ④ 의 근거는 **1 lane 1회 자기 관측**이다. 빈도·재현율을 주장하지 않는다.
- 본 Amendment 는 **분류를 추가**할 뿐 **검출 기제를 배선하지 않는다**. 산출물 층 기계 검사의 CI 배선 상태는 CFP-2994 설계
  결정(착지면 4단) 대기이며, 현 상태는 **강제층 미배선**이다 — 「게이트가 막는다」로 읽히는 문면을 본 Amendment 에 두지 않는다.
- 지시 층은 A2-3 대로 **집행 표면 0**. 「기계 강제」 주장 금지.
