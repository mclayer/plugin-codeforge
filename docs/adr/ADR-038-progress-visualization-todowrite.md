---
adr_number: 38
title: Progress visualization via TodoWrite (single-Story, hierarchical 4-marker)
date: 2026-05-08
status: Accepted
category: orchestration
carrier_story: CFP-274
supersedes: null
is_transitional: false
amendments:
  - id: 1
    carrier_story: CFP-375
    date: 2026-05-11
    title: TodoWrite 호출 시도 의무 (non-skippable attempt)
  - id: 2
    carrier_story: CFP-500
    date: 2026-05-12
    title: Deferred tool 스키마 선제 로드 = SessionStart hook tier 격상
  - id: 3
    carrier_story: CFP-475
    date: 2026-05-12
    title: Hook 등록 위치 SSOT (plugin-root) + polyglot wrapper + one-channel rule + mechanical_enforcement_actions[] self-application
    sunset_justification: "N/A — is_transitional: false (permanent governance mandate). Amendment 3 = §결정 10·11·12·13·14 신설 (implementation correction of CFP-500 path mismatch root cause + ADR-040 Amendment 3 §결정 7.D self-application 두 번째 사례). 기존 정책 폐기/축소 0건."
  - id: 4
    carrier_story: CFP-707
    date: 2026-05-15
    title: 4-marker vocabulary swap (pending ⏳→⬜ / in_progress 🔄→⏳ / FIX 검출 lane ❌→🔄) + §결정 3 semantic 정정 (FIX 마커 부여 위치 = 원인 lane → 검출 lane)
    sunset_justification: "N/A — is_transitional: false (permanent governance mandate). Amendment 4 = §결정 2 4-marker enum vocabulary swap + §결정 3 semantic 정정 + §결정 6 재진입 row marker swap (cosmetic + 직관성 정정, semantic 영역 변경 0건 — 검출 lane retry trigger 책임 추적 의미는 동등 유지). 기존 결정 폐기 0건. ⏳ semantic = blocked → pending (Amendment 0) → in_progress (Amendment 4) 2-step transition: TodoWrite checkbox 패러다임 (⬜) align + 모래시계 직관 (시간 흐름 = 진행 중) align + 회전 (🔄) → 검출 lane retry trigger semantic align (직관 — 검출한 쪽이 retry 를 trigger). 4 vocab 모두 사용자 dialog 5 turn 합의 (2026-05-15 KST) — 실제 4-marker 사용 현장 (CFP-274 deploy 후 5 day 누적) 직관성 evidence. broad coverage scope = ADR-038 §결정 2/3/6 + playbook §14.3/§14.4/§14.5/§14.7/§14.8 + CLAUDE.md L202 mirror (3 file). full-scope active amendment — vocab swap 부분 적용 금지 (ratchet anti-pattern 차단)."
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.D self-application 두 번째 사례 (CFP-475 carrier).
  # CFP-426 self-application 첫 사례 (ADR-040 frontmatter 자체) 와 동등 패턴.
  - action: duplicate-session-start-hook-check
    status: warning
    target_section: §결정 12 (one-channel rule + plain stdout SSOT)
    progress_note: "actual wire CFP-475 (scripts/check-no-duplicate-session-start-hook.sh + templates/github-workflows/duplicate-session-start-hook-check.yml)"
---

# ADR-038: Progress visualization via TodoWrite (single-Story, hierarchical 4-marker)

## 상태

Accepted (2026-05-08). carrier_story = CFP-274. Effective = Phase 2 wrapper PR merge timestamp (retroactive 미적용).

## 컨텍스트

CFP-20 (`docs/orchestrator-playbook.md` §14, `.claude-work/progress/<KEY>.md` derivative cache file) + ADR-029 (sub-step stderr narration) 가 진행상황 가시화 2 channel 제공. 사용자 directive (2026-05-08, 11 turn) — TodoWrite 가 CC 네이티브 sticky UI 로 가장 시각적인 channel 인데 codeforge 가 미사용. 본 ADR 가 3번째 channel 로 추가.

추가 사용자 directive (2026-05-08) — Sonnet decider 는 codeforge 가 자동 dispatch 하는 도구가 아닌, 사용자 임의 호출 전용 도구. ADR-022 deprecate 예정 (CFP-134 carrier). 본 ADR 는 codeforge 자동 dispatch 가정하지 않음.

## 결정 요약 (8 결정 — Amendment 1: §결정 8 추가 2026-05-11)

### 결정 1 — TodoWrite 를 CFP-20 §14.7 render flow 의 3번째 channel 로 추가

state source 무변경, §0 file 보존 (resume 안전망). render flow step 5 신규 (TodoWrite update). state source = Story §10 + Issue label + §-fill state 그대로 (CFP-20 §14.2 invariant). TodoWrite + §0 file 둘 다 derivative cache.

### 결정 2 — 4 marker vocabulary

⬜ pending (empty checkbox) / ⏳ in_progress (모래시계 — 시간 흐름) / ✅ completed (PASS / N/A) / 🔄 FIX 검출 lane (회전 — retry trigger). 기존 CFP-20 8 marker (⏸ ⏳ 🔄 ✅ ❌ 🔁 ⊘ N/A) 단순화. file / TodoWrite 두 channel 동일 어휘.

> **CFP-707 Amendment 4 vocabulary swap (2026-05-15)**: 직관성 정정 — `⏳ pending` (모래시계 = "시간 흐른다 = 진행 중" 인지 모델) → `⬜` (TodoWrite checkbox 패러다임 정합) / `🔄 in_progress` (회전) → `⏳` (모래시계 시간 흐름 = 진행 중 자연 align) / `❌ FIX 원인` (실패 mark) → `🔄` 위치 swap (검출 lane = retry trigger semantic 으로 회전 의미 align, §결정 3 semantic 정정 동반). ⏳ semantic = Amendment 0 (blocked → pending) + Amendment 4 (pending → in_progress) 2-step transition.

검출 label 정규화: review/test lane 의 terminal detection FAIL 인 경우에도 TodoWrite content label 은 `FIX-N detected` 정규화 (RESET 시 `FIX-N detected (cause: <원인 lane>, RESET-N)`). `FAIL` 은 review/test 판정 흐름의 terminal outcome vocabulary 로만 남음.

blocked / waiting 처리: 4-marker vocabulary 범위 밖. ⬜ pending 으로 표현, 진행 중 차단성 작업은 ⏳ in_progress row 의 content 1줄 설명으로 표현.

### 결정 3 — FIX 검출 lane semantic (CFP-707 Amendment 4 정정)

**검출 lane** (review/test 자체) 에 `🔄` 표시 — retry trigger 의미 align. 검출 lane row content = `FIX-N detected (cause: <원인 lane>)`. 원인 lane 은 기존 ✅ marker 유지 + content suffix `FIX-N 원인 · <원인 판정 1줄>` 으로 책임 추적 (lane PASS evidence 는 보존, FIX trigger origin 은 content text 로 기록). 재진입 lane 은 새 row append (⏳ 시작, content suffix `(재진입)` 또는 `(재진입 RESET-N)`).

> **CFP-707 Amendment 4 semantic 정정 (2026-05-15)**: Amendment 0 (CFP-274) = 검출 lane ✅ + 원인 lane ❌ flip (책임 추적 정확하지만 lane row 만 훑어보면 검출 lane PASS 와 원인 lane FAIL 의미 분리 인지 부담). Amendment 4 = 검출 lane 🔄 (retry trigger 직관 — "검출한 쪽이 retry 를 trigger") + 원인 lane ✅ + content suffix (책임 추적은 row content text 로 보존). 책임 추적 의미 영역 변경 0건 — 표기 위치만 swap.

### 결정 4 — Single-Story 모드

1 세션 = 1 active Story. TodoWrite row 의 `[KEY]` prefix drop. multi-Story TodoWrite 지원은 후속 CFP. single-Story collision (두 concurrent lane spawn 이 같은 Story TodoWrite write) 발생 시 hard-reset (canonical state 에서 full rewrite).

### 결정 5 — Hierarchical 2-level

lane row (0-indent) + agent sub-row (2-space indent). active lane 만 펼침. 다중 in_progress (TodoWrite "ONE in_progress" 가이드 deviation) 의도적 허용 — codeforge 의 병렬 agent 모델 (deputy 6/8 / workers parallel / parallel diagnosis) 본질상 불가피. 본 ADR 가 wrapper-specific deviation 명시.

cross-plugin generalization (lane plugins 에 동일 protocol 적용) 은 별도 CFP — 본 ADR scope 외부.

### 결정 6 — 재진입 = 새 row 추가

`(재진입)` 또는 `(재진입 RESET-N)` suffix. 기존 검출 lane `🔄` row 는 retrospective 기록으로 보존 (immutable). 다중 FIX (FIX-1 → FIX-2 동일 검출 lane) 도 새 row append: 이전 `🔄` row patch 안 함, 새 `🔄` row append + 새 재진입 row append.

> **CFP-707 Amendment 4 marker swap (2026-05-15)**: 기존 `❌` 표기는 §결정 3 Amendment 4 정정으로 검출 lane `🔄` 마커로 대체. 책임 추적 (FIX-N 원인 판정) 은 §결정 3 정합 — 원인 lane content suffix `FIX-N 원인 · <판정>` 로 보존.

### 결정 7 — TodoWrite update best-effort / non-blocking

TodoWrite 갱신 실패 시 lane primary work 미차단 — warning 으로 surface. update 가 실패하거나 skipped 되어도 lane 은 계속 진행. 사용자 confirmation / polling / acknowledgment wait 도입 없음 (ADR-029 stop discipline 정책 무영향).

Sonnet decider / Codex review 등 외부 도구는 codeforge 가 자동 dispatch 하지 않음 — 사용자 임의 호출 전용. 본 ADR sample / vocabulary 는 Sonnet decider 자동 dispatch 가정하지 않음. 원인 판정 / FIX synthesis 은 PL agent (DesignReviewPL / CodeReviewPL / SecurityTestPL) 의 pl_recommendation 으로 표현.

### 결정 8 — TodoWrite 호출 시도 의무 (non-skippable attempt / Amendment 1)

§결정 7 은 시도 후 실패를 다루며, 시도 자체의 의무를 명시하지 않았다. 이 gap 이 Amendment 1 의 동인.

**시도 의무 (non-skippable)**:
Orchestrator 는 아래 6개 이벤트 각각에서 TodoWrite 갱신을 **반드시 시도**해야 한다:
lane 진입 / lane PASS / lane FIX 검출 / FIX 원인 판정 / lane 재진입 / Story 완료.
"시도를 건너뛰는 것" 은 §결정 7 의 best-effort 허용 범위 밖이다.

**전제 조건 — deferred tool 스키마 선제 로드 (non-skippable)**:
TodoWrite 는 deferred tool — `ToolSearch("select:TodoWrite")` 로 스키마를 먼저 fetch 해야 호출 가능.
Orchestrator 는 세션 시작 시 (§1.1 checklist 0i) 선제 수행. 로드 실패 시 재시도 1회.
재시도 실패 시 §결정 7 경로(warning only) 로 폴백.

**실패 처리 — §결정 7 그대로 유지 (non-blocking)**:
시도 후 실패는 §결정 7 이 처리 — warning, lane primary work 미차단.
"시도를 건너뛰는 것" 과 "시도했으나 실패한 것" 은 별개의 위반이다.

carrier_story: CFP-375
Amendment 날짜: 2026-05-11

### 결정 9 — Deferred tool 스키마 선제 로드 = SessionStart hook tier 격상 (Amendment 2)

§결정 8 의 **전제 조건 — "Orchestrator 가 세션 시작 시 `ToolSearch("select:TodoWrite")` 로 스키마를 선제 로드한다"** 의무는 두 차례의 runtime advisory 적용 (CFP-375 본 §결정 8 + CFP-385 CLAUDE.md 0i 직접 명시) 모두 반복적으로 스킵된 history 가 있다. **선언적 규칙 = 신뢰 불가** 가 두 번 검증되었다. 본 §결정 9 가 enforcement layer 를 (c) runtime advisory 에서 **(b) SessionStart hook tier** 로 격상한다 (Researcher 3-tier 모델 — (a) physical CI/git hook / (b) startup-time hook / (c) runtime text directive).

**Mechanism**: consumer `.claude/settings.json` `hooks.SessionStart[]` 에 `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` 을 등록함으로써, Claude Code harness 가 세션 부팅 시점에 helper script `scripts/check-codeforge-prereq.sh` 의 stdout 을 Orchestrator 첫 turn context 에 prompt-injection 형태로 inject. helper script 본문 = 다음 instruction 의 static heredoc echo:

```
You MUST call the following as your first tool action in this session, before
responding to any user message:

  ToolSearch(query="select:TodoWrite,EnterWorktree,ExitWorktree,SendMessage", max_results=5)

This loads schemas for 4 deferred tools required by codeforge orchestration
(ADR-038 §결정 9 + CFP-463 extension):
  - TodoWrite — progress visualization
  - EnterWorktree / ExitWorktree — worktree-first workflow (ADR-040)
  - SendMessage — agent teammate communication (ADR-044)

If ToolSearch fails: retry once. If retry fails: warn user, continue
(ADR-038 §결정 7 fallback).
```

> **CFP-463 extension (2026-05-12)**: 초기 preload list (TodoWrite 단독) 를 4 tool 로 확장. cost-benefit 평가 — codeforge orchestrator Story 작업 시 4 tool 모두 high-frequency 사용 → 4x token cost 가 첫 사용 latency 4회 제거 와 trade-off positive. measurable 도입 의도 evidence = 본 retro session 의 EnterWorktree/SendMessage 첫 사용 시 ToolSearch latency 4회 발생.

**본 hook 의 책임 경계 (한계 명시 — Researcher 3-tier 중 (b) layer 한정)**:

- 책임: schema/state 가용성 보장 layer — Orchestrator turn 진입 시점에 deferred tool schema 가 prompt cache 에 fresh 한 상태로 가용함을 hook stdout prompt-injection 으로 강하게 advise.
- **비책임**: behavioral attempt 의무 자체는 §결정 8 그대로 retain — hook 도 prompt-level advisory 이며 mechanical function-call 강제가 아님. behavioral compliance 자체는 여전히 Orchestrator 책임.

**Extensibility — `prereq_tools[]` + `prereq_checks[]` array schema**:

본 hook sample 은 향후 추가 deferred tool (Monitor / WebFetch / 자주 쓰이는 mcp__github__\*) 또는 prereq check (ADR-053 structural-change verify / settings.json sanity) 가 필요할 경우 schema-only 갱신으로 list 확장 가능. **초기 preload list = TodoWrite 단독** (보수적 minimum, 향후 별도 CFP 가 measurable 도입 의도 후 확장). **현재 list = TodoWrite + EnterWorktree + ExitWorktree + SendMessage 4종 (CFP-463 extension, 2026-05-12)**.

**Layered defense (fallback retain)**:

| Tier | Mechanism | 본 §결정 9 적용 후 status |
|------|-----------|------------------------|
| (b) SessionStart hook | harness 가 첫 turn 에 prompt-injection | **PRIMARY (본 §결정 9 신설)** |
| (c) Runtime ToolSearch attempt | Orchestrator §결정 8 호출 의무 | RETAIN — hook 미등록 / 실행 실패 시 fallback |
| Failure handling | §결정 7 (warning only, lane 비차단) | RETAIN unchanged |

hook 등록 누락 / hook 실행 실패 → §결정 8 의 runtime ToolSearch 시도가 자동 fallback. 두 tier 가 layered defense 로 작동. §결정 7·8 폐기·축소 0건 — Amendment 2 는 §결정 8 의 "전제 조건" 부분 의 enforcement layer 만 격상.

**관련 파일** (Phase 2 PR scope):

- `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` (신규)
- `scripts/check-codeforge-prereq.sh` (신규)
- `docs/domain-knowledge/domain/runtime/deferred-tool-and-session-start-hook.md` (신규 — ADR-056 §결정 1 path)
- `docs/orchestrator-playbook.md` §1.1 0i (supersede)
- `CLAUDE.md` "세션 개시 의무" (supersede)
- `.claude/settings.json` (wrapper dogfooding 등록)
- `docs/consumer-guide.md` (등록 절차 명문화)
- `.claude-plugin/plugin.json` (MINOR bump 5.16.0 → 5.17.0, ADR-037 §결정 1(c))

carrier_story: CFP-500
Amendment 날짜: 2026-05-12

amendment_log:
  - by: "CFP-500"
    date: "2026-05-12"
    scope: "§결정 9 신설 — deferred tool 스키마 선제 로드 enforcement layer 를 runtime advisory (c) 에서 SessionStart hook tier (b) 로 격상. §결정 7·8 retain (layered defense)."
    sunset_justification: |
      본 amendment 는 ADR 본체 frontmatter `is_transitional: false` (progress visualization layer 자체는 영구 정책) 변경 안 함 — Amendment 2 는 §결정 9 **신설** (기존 결정 폐기/축소 아님).
      단 (b) hook tier 자체의 measurable performance 는 별도 metric/who/how 3-tuple 로 추적:
        - **metric**: 신규 세션 100개 중 TodoWrite InputValidationError 발생률. 5건 이상 → revert 검토 trigger.
        - **who**: PMOAgent (Story 완료 회고에서 mctrader debut audit 결과 집계).
        - **how**: CFP-500 merge 후 3개월 + mctrader debut audit 1 cycle 완료 시점에 retrospective 평가. PASS 시 §결정 9 retain. FAIL 시 (a) tier 격상 (CI / git hook physical enforcement) 검토 CFP 발의. **Automation candidate** — CFP-389 / ADR-060 evidence-enforceable framework 후속 evaluation (manual sampling → grep-based auto count) 으로 격상 가능성 별도 CFP 평가.
      Measurement mechanism 한계 — consumer telemetry 부재로 manual sampling (automation candidate 위 참조). ADR-058 §결정 3 정량 명시 + 모달 어휘 부재 정합. 측정 정확도는 retrospective evaluation 까지 미해소 (Story §6 위험 #1 acknowledged).
  - by: "CFP-707"
    date: "2026-05-15"
    scope: |
      Amendment 4 — 4-marker vocabulary swap (§결정 2) + FIX 검출 lane semantic 정정 (§결정 3) + 재진입 row marker swap (§결정 6). 변경 vocab 3건:
        - `⏳ pending` → `⬜` (TodoWrite checkbox 패러다임 정합 — "시작 안 됨" empty checkbox 직관)
        - `🔄 in_progress` → `⏳` (모래시계 = "시간 흐름 = 진행 중" 자연 인지 모델 align)
        - `❌ FIX 원인` → `🔄 FIX 검출 lane` (검출 lane 부여 + 회전 = "다시 시작 / retry trigger" semantic align, §결정 3 위치 swap 동반)
      `✅ completed` 변경 0건. 책임 추적 (FIX-N 원인 판정) 의미 영역 변경 0건 — §결정 3 정정 후 원인 lane content suffix `FIX-N 원인 · <판정>` 로 보존.
      §결정 1·4·5·7·8·9·10·11·12·13·14 retain unchanged. §결정 2/3/6 표기 swap + semantic 정정 (cosmetic + 직관성 evidence-driven).
    sunset_justification: |
      본 amendment 는 ADR 본체 frontmatter `is_transitional: false` (permanent governance mandate) 변경 안 함 — Amendment 4 = §결정 2/3/6 vocabulary + semantic 정정 (책임 추적 의미 보존 + 표기 직관성만 강화).

      **Amendment 4 정당화 근거 — 사용자 dialog 5 turn 누적 evidence (2026-05-15 KST)**:
        - `⏳ pending` 모래시계 글리프가 in_progress 마커 (`🔄` 회전) 와 시각 모호 (CFP-274 deploy 후 5 day 누적 사용 evidence)
        - `❌ FIX 원인 lane` 부여 = "검출한 lane 이 잘못한 거 아닌가" 직관과 충돌 (lane row 만 훑어보면 ✅ 검출 lane PASS 와 ❌ 원인 lane FAIL 의미 분리 인지 부담)
        - `⬜` empty checkbox = TodoWrite checkbox 패러다임 자연 align (universal pending convention)
        - `🔄` 회전 + 검출 lane 부여 = retry trigger 의미 직관 (검출한 쪽이 retry 발화)

      **Measurement mechanism (sunset_justification 의무 정합 — ADR-058 §결정 5 + Amendment 1 metric/who/how 3-tuple)**:
        - **metric**: TodoWrite render 직관성 confusion 발생률 (Story §10 retro 안 "TodoWrite vocab 모호 발화 횟수" + Story §11 retro 안 "marker 의미 confused" 사용자 발화 횟수). Story 100 cycle 누적 후 ≥ 5건 → revert 검토 trigger.
        - **who**: PMOAgent (Story 완료 retro mctrader debut audit 결과 집계).
        - **how**: CFP-707 merge 후 3개월 retrospective + mctrader debut audit 1 cycle 완료 시점 동시 평가. PASS 시 §결정 2/3/6 Amendment 4 retain. FAIL 시 별도 CFP 가 vocab 재정의 또는 revert 평가.
        - **Automation candidate**: Story §10/§11 retro markdown grep — "vocab 모호" / "marker 의미 confused" / "직관성 약함" / "지표 헷갈림" 키워드 grep count → manual sampling 단계 (consumer telemetry 부재). ADR-058 §결정 3 정량 명시 + 모달 어휘 부재 정합.

      Amendment 0 / 1 / 2 / 3 의 sunset_justification cycle (3개월 + mctrader debut 1 cycle) 와 동일 동기화. 측정 정확도 한계 = retrospective evaluation 까지 미해소 (consumer telemetry 부재 영향, Story §10/§11 grep manual sampling 단계).

  - by: "CFP-475"
    date: "2026-05-12"
    scope: |
      §결정 10·11·12·13·14 신설 (5건 — implementation correction of CFP-500 path mismatch root cause).
      §결정 9 retain unchanged (hook tier 격상 정책 자체 보존, 본 Amendment 3 는 **등록 위치** + **polyglot pattern** + **one-channel rule** + **env contract** + **self-application** 만 신설).
      §결정 1-8 retain unchanged.
    sunset_justification: |
      본 amendment 는 ADR 본체 frontmatter `is_transitional: false` (permanent governance mandate) 변경 안 함 — Amendment 3 = implementation correction (path mismatch root cause 해소) + ADR-040 Amendment 3 §결정 7.D self-application 두 번째 사례. 기존 결정 폐기/축소 0건.

      §결정 9 의 metric/who/how 3-tuple (TodoWrite InputValidationError 발생률 < 5건/100세션) 은 Amendment 3 에 의해 강화 — hook 발화 channel 정합성 확보 (path mismatch 해소) 가 metric 측정 정확도의 prerequisite. Amendment 3 후 3개월 retrospective 시점 (Amendment 2 sunset_justification 와 동일 cycle) 에 동시 평가:
        - **§결정 10·12 measurable validation**: Phase 2 PR merge 후 100개 cold start sample 안 (a) hook 발화 channel 정합성 (`additionalContext` 안 `ToolSearch select:TodoWrite` substring 발화 비율 ≥ 95%) + (b) within-block / cross-block duplication 0건 검증 — `scripts/check-no-duplicate-session-start-hook.sh` warning detect 빈도 = 0.
          - **4th attempt PASS evidence (2026-05-14 KST)**: 첫 measurable validation sample — fresh Opus 세션 cold start `additionalContext` 안 (a) `[codeforge prereq-check]` substring 발화 + (b) `ToolSearch("select:TodoWrite,EnterWorktree,ExitWorktree,SendMessage")` directive 발화 + (c) `hooks/session-start` line 44-57 byte-identical verbatim emit + (d) Orchestrator ToolSearch auto-call 성공 + (e) TodoWrite schema 로드 후 InputValidationError 0건 + (f) within-block duplication 0건 + (g) JSON wrapping 부재 + (h) #471 FAIL 해소 — 8/8 PASS. 1차 measurable validation sentinel — 100 sample cycle 진행 의무 보존 (3개월 retrospective evaluation 시점). 선행 1-3 attempt (CFP-375 / CFP-385 / CFP-475 3rd) FAIL 누적 후 첫 성공 사례 = `hooks/hooks.json` plugin-root SSOT (§결정 10) + polyglot pattern (§결정 11) + one-channel rule (§결정 12) 조합 효과 prima facie 입증. Evidence artifact = `<internal-docs>/wrapper/retros/2026-05-13-cfp-475-retro.md` PASS section.
        - **§결정 11 polyglot pattern stability**: superpowers 5.1.0 verbatim copy-adapt — 5.1.0 GA 6개월 무사고 evidence preserve + 본 Story Phase 2 merge 후 3개월 cycle 안 polyglot wrapper regression 0건 (`tests/unit/test-session-start-hook.sh` PASS 100%).
        - **§결정 13 BYPASS env contract**: `BYPASS_CODEFORGE_PREREQ` 사용 빈도 measurable (stderr audit echo grep — manual sampling 단계). `BYPASS_PREREQ_CHECK` deprecated grace = 1 release (별도 CFP carrier).
        - **§결정 14 self-application**: ADR-040 Amendment 3 §결정 7.D 패턴 두 번째 사례. ADR-060 evidence-enforceable framework `duplicate-session-start-hook-check` entry warning tier — promotion criteria (PR 누적 ≥ 20 + failure 0) 충족 시 blocking-on-pr 격상 가능성 별도 CFP 평가.
        - **Story §3.4.0 결정 1 T5 imperative directive measurable revisit** (DesignReview synth cfp-475-dr-synth-003 권고 정합): hook stdout 의 "You MUST call..." imperative wording 보존 결정 (factual reframing 미적용). prompt-injection defense surface 발화 frequency manual sampling — stderr / GitHub issue search "prompt injection defense" / Claude session warning 발화 grep. **100세션 sample 중 ≥ 5건 → factual reframing ("The codeforge orchestrator workflow requires...") 격상 별도 CFP carrier**. Amendment 2 sunset_justification cycle (3개월 + mctrader debut 1 cycle) 와 동일 동기화. fail-safe monitoring 채널 = Story §8.1-T4 indirect detect (cold start `additionalContext` 안 directive 발화 metric 동반 측정).

      Measurement mechanism 한계 = §결정 9 sunset_justification verbatim (consumer telemetry 부재 → manual sampling, automation candidate). ADR-058 §결정 3 정량 명시 + 모달 어휘 부재 정합.

### 결정 10 — Hook 등록 위치 SSOT 정정 (plugin-root `hooks/hooks.json` first-class, Amendment 3)

§결정 9 의 Mechanism 부분은 consumer `.claude/settings.json` `hooks.SessionStart[]` 에 sample 등록을 명시했다. **이 명시가 CFP-500 in-vivo verify #471 FAIL 의 implementation bug root cause** — `${CLAUDE_PLUGIN_ROOT}` interpolation 이 plugin context 에서만 resolve 되는데, settings.json 안 `command` 가 `${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-prereq.sh` 잉여 `codeforge/` segment 를 포함 → bash 실행 실패 → stdout empty → harness capture 0 → injection 0. 본 §결정 10 가 등록 위치 SSOT 를 **plugin-root `hooks/hooks.json` first-class** 로 정정.

**SSOT (plugin-root)**:
- 위치: `<plugin-cache>/hooks/hooks.json` (plugin root, **`.claude-plugin/` 하위 금지** — Claude Code Plugins 공식 spec verbatim 정합)
- Schema: superpowers 5.1.0 `hooks/hooks.json` verbatim copy-adapt (line 1-16 — `matcher: "startup|clear|compact"` + `type: "command"` + `command: "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd session-start"` + `async: false`)
- `${CLAUDE_PLUGIN_ROOT}` resolve scope = plugin context 한정 (잉여 path segment 0 보장)
- Consumer activation = `/plugins install codeforge@mclayer` 단독으로 자동 활성 (CFP-475 §4.2 G2 PoC PASS evidence — `/plugin enable` 별도 명령 불필요)

**Fallback (deprecated, 1 release grace)**:
- `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` = consumer 등록 sample. **CFP-475 부터 deprecated** (`_deprecated_since: 5.22.0` metadata 부착).
- 1 release grace 후 별도 CFP 가 sample file 삭제 + 등록 잔존 cleanup 권고.

**§결정 9 Mechanism 정정**: "consumer `.claude/settings.json` `hooks.SessionStart[]` 에 sample 등록" → "plugin-root `hooks/hooks.json` 자동 활성 (consumer 등록 절차 불필요)".

carrier_story: CFP-475
Amendment 날짜: 2026-05-12

### 결정 11 — Polyglot wrapper pattern (Windows `.cmd` + Unix `.sh`, superpowers 5.1.0 verbatim copy-adapt + MIT attribution)

§결정 9 의 helper script `scripts/check-codeforge-prereq.sh` = bash 단일 환경. Windows consumer (cmd.exe / PowerShell / Git Bash / WSL) 에서 hook 발화 시점에 어떤 shell 이 invoke 되는지 Claude Code 공식 spec 모호. CFP-475 §4.2 G1 PoC 가 superpowers 5.1.0 `run-hook.cmd` 의 polyglot 패턴 (3 환경 실측) 검증 — 본 §결정 11 가 패턴을 ADR-038 SSOT 로 채택.

**Polyglot dispatcher (`hooks/run-hook.cmd`)**:
- superpowers 5.1.0 `hooks/run-hook.cmd` (line 1-47) **verbatim copy-adapt** (변경 0건).
- Polyglot mechanism: line 1 `: << 'CMDBLOCK'` = bash 의 no-op heredoc + cmd.exe 의 라벨 (parse 안 됨) → cmd.exe 는 line 2-39 batch 실행, bash 는 line 42-46 만 실행.
- Windows bash detect 4-tier (line 21-35): `C:\Program Files\Git\bin\bash.exe` → `C:\Program Files (x86)\Git\bin\bash.exe` → `where bash` (PATH) → silent `exit /b 0` (4번째 = no bash 환경 fail-safe).
- Unix dispatch (line 42-46): `exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"` — extensionless script 호출.

**Extensionless script naming (`hooks/session-start`)**:
- superpowers run-hook.cmd line 6-8 주석 verbatim — "Hook scripts use extensionless filenames (e.g. "session-start" not "session-start.sh") so Claude Code's Windows auto-detection — which prepends "bash" to any command containing .sh — doesn't interfere."
- Windows harness auto-detect 우회 = race condition 회피.

**MIT attribution**:
- `hooks/run-hook.cmd` line 1-3 주석 안 SPDX-License-Identifier + 출처 (https://github.com/obra/superpowers v5.1.0) + carrier_story (CFP-475) 명시 의무.
- superpowers 의 MIT 라이센스 = 본 ADR sample / 본 plugin Phase 2 PR 차용 안전.

**Overhead (G1 PoC 실측)**:
- Git Bash 단독 ~50ms / Win11 cmd.exe → bash dispatch ~150ms / WSL bash ~50ms / macOS bash ~50ms.
- Hook timeout 15s 대비 **< 1%** = §결정 9 layered defense 영향 0.

**Variants 미채택**:
- 환경별 별도 hook entry (`.cmd` only / `.sh` only) 분리: 채택 X — schema 복잡도 증가 + cross-platform 일관성 약화. polyglot single file 가 우월.
- `plugin.json.hooks` inline: 채택 X — Claude Code spec 안 inline schema 모호 + `${CLAUDE_PLUGIN_ROOT}` resolve scope 불확실. plugin-root `hooks/hooks.json` 단독 SSOT.

carrier_story: CFP-475
Amendment 날짜: 2026-05-12

### 결정 12 — One-channel rule (plain stdout SSOT + JSON form 은 `suppressOutput` 동반 시에만)

§결정 9 Mechanism = helper script stdout 의 prompt-injection inject. CFP-475 Researcher Round 4 re-verify 가 **paradigm shift** 발견 — Claude Code Hooks 공식 spec (https://code.claude.com/docs/en/hooks) verbatim: "Any text your hook script prints to stdout is added as context for Claude" + "Since plain stdout already reaches Claude for this event, a hook that only loads context can print to stdout directly without building JSON. Use the JSON form when you need to combine context with other fields such as `suppressOutput`." 본 §결정 12 가 plain stdout 을 SSOT 로 채택.

**One-channel rule (plain stdout SSOT)**:
- `hooks/session-start` 본문 = `cat <<'EOF' ... EOF` heredoc plain stdout echo + exit 0.
- JSON wrap layer (`additional_context` / `hookSpecificOutput.additionalContext` / `additionalContext` 3-platform dispatch) **부재** — superpowers session-start 의 `escape_for_json` + 3-platform JSON dispatch 패턴 미차용.
- JSON form 은 `suppressOutput` / `systemMessage` 등 다른 field 동반 필요 시에만 사용 (공식 spec verbatim 정합) — 본 Story scope = single advisory directive, JSON 비필수.

**Double-injection 회귀 회피 (mechanical lint enforcement)**:
- `.claude/settings.json` `hooks.SessionStart[]` + plugin-root `hooks/hooks.json` 양 channel 안 prereq-check entry 동시 존재 시 → `scripts/check-no-duplicate-session-start-hook.sh` warning tier (exit 2) 발화 + `templates/github-workflows/duplicate-session-start-hook-check.yml` PR-time audit comment auto-post.
- `hotfix-bypass:duplicate-session-start-hook` label 부착 시 lint skip + audit comment 만 발화 (ADR-060 §결정 7 audit-trailed exception 패턴 정합).
- Evidence base: anthropics/claude-code Issue #14281 (within-block / cross-block duplication) + superpowers Issue #648 (2-field JSON 출력 → dedup 부재 → 2x inject 회귀).

**Within-block duplication 잔존 위험 처리**:
- plain stdout 도 #14281 within-block 위험 잔존 가능 — §결정 12 가 mechanical lint 로 차단 (`hooks/hooks.json` schema 안 prereq-check entry 1 회만 정의 의무).
- §8.5.6 paradigm shift verify 8-step (Story CFP-475) = substring count = 1 verify 의무 (cold start manual transcript export).

carrier_story: CFP-475
Amendment 날짜: 2026-05-12

### 결정 13 — `BYPASS_CODEFORGE_PREREQ` env contract + namespace migration + audit trail 의무

§결정 9 Mechanism = "If ToolSearch fails: retry once. If retry fails: warn user, continue (ADR-038 §결정 7 fallback)" — runtime fallback. 본 §결정 13 = 사용자 ad-hoc bypass channel SSOT 명시.

**Env contract (`BYPASS_CODEFORGE_PREREQ=1`)**:
- 사용자 advisory bypass — debug / 환경별 사유로 hook 발화 제어 시.
- 설정 시 hook short-circuit (stdout empty + harness injection 0 + 세션 정상 진행).
- **Audit trail 의무 (mandatory)**: stderr 로 1-line audit echo — `>&2 printf '[codeforge-prereq] BYPASS_CODEFORGE_PREREQ=1 — TodoWrite preload directive suppressed at %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"`. timestamp UTC ISO 8601 = single canonical reference.
- 근거: ADR-058 §결정 5 audit trail visibility + ADR-060 §결정 7 hotfix-bypass:* audit-trailed exception 패턴 (env bypass 도 동등 audit channel 의무).

**Namespace migration (`BYPASS_PREREQ_CHECK` → `BYPASS_CODEFORGE_PREREQ`)**:
- 기존 `BYPASS_PREREQ_CHECK=1` env (CFP-500 산출물) = codeforge 식별 prefix 부재 — namespace 불명확.
- `BYPASS_CODEFORGE_PREREQ` = codeforge prefix 명료 (다른 plugin / tool 의 BYPASS env 와 collision 회피).
- **1 release deprecation grace**: `BYPASS_PREREQ_CHECK=1` 도 1 release 동안 호환 — stderr 로 deprecation warning + exit 0. 별도 CFP 가 후속 제거.

**Bypass scope 한계**:
- 본 env = advisory bypass only — TodoWrite preload directive 발화 제어만 영향 (다른 hook entry / workflow / lint 비영향).
- Multi-instance race condition 영향 0 (hook stateless I2 정합).
- ratchet anti-pattern 차단 = audit echo 가 silent bypass 방지 (ADR-058 §결정 5 정합).

carrier_story: CFP-475
Amendment 날짜: 2026-05-12

### 결정 14 — `mechanical_enforcement_actions[]` self-application (ADR-040 Amendment 3 §결정 7.D 패턴 두 번째 사례)

ADR-040 Amendment 3 §결정 7 (CFP-426) = 모든 normative ADR amendment 의 frontmatter `mechanical_enforcement_actions[]` 의무 신설. §결정 7.D self-application 첫 사례 = ADR-040 자체. 본 §결정 14 = ADR-038 Amendment 3 가 self-application 두 번째 사례.

**Frontmatter `mechanical_enforcement_actions[]` 부착 (본 ADR file 자체)**:
```yaml
mechanical_enforcement_actions:
  - action: duplicate-session-start-hook-check
    status: warning
    target_section: §결정 12 (one-channel rule + plain stdout SSOT)
    progress_note: "actual wire CFP-475 (scripts/check-no-duplicate-session-start-hook.sh + templates/github-workflows/duplicate-session-start-hook-check.yml)"
```

**Entry binding**:
- `action: duplicate-session-start-hook-check` = `docs/evidence-checks-registry.yaml` entry name verbatim.
- `target_section: §결정 12` = 본 ADR 안 binding 지점 (one-channel rule mechanical enforcement 의 normative source).
- `progress_note` = actual wire CFP-475 (script + workflow) — CFP-426 worktree-first 4 entry skeleton 동등 패턴.

**evidence-checks-registry.yaml entry append (별도 file)**:
- 위치: `docs/evidence-checks-registry.yaml` `entries[]` 마지막 row append (worktree-first-spawn-evidence-cwd 다음).
- Schema v1.1 정합 (CFP-455 Amendment 2 §결정 17 retroactive reclassification immediate fail) — `current_tier: warning` (required) + `bypass_label: hotfix-bypass:duplicate-session-start-hook` + `bypass_audit_lint: bash scripts/check-bypass-audit-comment.sh` (CFP-389 prior art reuse).
- promotion criteria: `pr_cumulative_min: 20` + `failure_threshold: 0` + `sibling_dependencies: []` (본 entry 단독, Story 4 진입 시 평가 sibling 부재).
- `introduced_by: CFP-475` / `owner_adr: ADR-038` / `carrier_adr: ADR-038` / `status: Active`.

**Promotion 평가 (별도 CFP)**:
- 본 entry = warning tier (Phase 2 PR scope = actual wire 첫 사례). CFP-426 worktree-first 4 entry skeleton 동등 패턴.
- ADR-060 §결정 6 promotion gate AND condition (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 충족 시 blocking-on-pr 격상 가능 — 별도 CFP 평가.

carrier_story: CFP-475
Amendment 날짜: 2026-05-12

## 대안 검토

### 대안 A — TodoWrite 를 canonical state cache 로 승격

§0 file 격하. 거부 이유: TodoWrite ephemeral → CFP-20 §14.8 resume 깨짐. CFP-20 §14.2 invariant 위반.

### 대안 B — Multi-channel dashboard (TodoWrite + statusline + Mermaid Gantt)

거부 이유: scope creep, 사용자 우선순위 미선택. statusline / Mermaid Gantt 는 별도 CFP.

채택 = 본 ADR §결정 1-7 (Approach 1 minimal extension).

## 결과

### 영향 file (wrapper repo)

- `docs/adr/ADR-038-progress-visualization-todowrite.md` (본 file)
- `docs/orchestrator-playbook.md` §14.4 (status enum 4 marker simplify)
- `docs/orchestrator-playbook.md` §14.5 (Trigger 표 + best-effort + collision rule)
- `docs/orchestrator-playbook.md` §14.7 (Render flow step 5)
- `docs/orchestrator-playbook.md` §14.8 (Resume step 4)
- `CLAUDE.md` (ADR-038 reference 1 paragraph)

### 비-영향

- 6 lane plugin (codeforge-{requirements,design,develop,test,review,pmo}) 변경 없음 (ADR-029 §결정 5 와 동일 정책 — Writer 단독 invariant)
- §0 Live Progress file (CFP-20) 동작 무변화 — render flow step 5 만 추가
- Stop discipline (ADR-022 / ADR-025) 정책 무변화
- Inter-plugin contract 영향 없음

### Reversibility

- Yes — TodoWrite update step 미사용 시 CFP-20 + ADR-029 기존 동작 복원
- ADR revert 시 TodoWrite update 제거 → file + stderr only 로 복원

## Out-of-scope

- Multi-Story 동시 active TodoWrite 표현 (별도 CFP)
- Statusline / Mermaid Gantt / Hook context inject 등 추가 channel
- CFP-20 §0 file 폐기
- stderr narration 폐기
- Lane plugin agent 변경
- ANSI color stderr (cross-platform 안전성)
- Per-lane signature emoji (사용자 거부)
- Real-time progress bar (사용자 거부)
- TodoWrite cross-plugin generalization (별도 ADR — 본 ADR 는 wrapper-specific)

## 관련 ADR

- **ADR-029** (Phase execution visibility expansion) — sibling, sub-step stderr narration. ADR-029 §결정 5 와 동일 정책 (Lane plugin 변경 불요).
- **CFP-20** (§0 Live Progress) — derivative cache file. 본 ADR 가 §14 amendment.
- **ADR-013** (codeforge family dogfood-out policy) — spec / plan 위치 internal-docs override.
- **ADR-022** (Sonnet decider) — CFP-134 에 의해 deprecate 예정. 본 ADR sample / vocabulary 는 Sonnet decider 자동 dispatch 가정 안 함 (사용자 directive).
- **ADR-024** (Story-scoped branch policy) — 본 Story branch 명명.
- **ADR-031** (Lane spawn evidence trail) — Story §14 7 row populated 의무.
- **ADR-005** (Plugin meta exempt) — N/A lane 사유 reference.

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/orchestrator-playbook.md` §14.4 / §14.5 / §14.7 / §14.8
- `CLAUDE.md` Orchestration 규칙 §
- `wrapper/specs/2026-05-08-cfp-274-progress-visualization-todowrite-design.md` (internal-docs SSOT)
- `wrapper/change-plans/cfp-274-progress-visualization-todowrite.md` (internal-docs)
- `wrapper/stories/CFP-274.md` (internal-docs)
- `wrapper/decisions/CFP-274-001-codex-spec-review.yaml` (internal-docs)
