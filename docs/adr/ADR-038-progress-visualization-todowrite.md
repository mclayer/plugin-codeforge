---
adr_number: 38
title: Progress visualization via TodoWrite (single-Story, hierarchical 4-marker)
date: 2026-05-08
status: Accepted
category: orchestration
carrier_story: CFP-274
supersedes: null
is_transitional: false
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

⏳ pending (모래시계) / 🔄 in_progress / ✅ completed (PASS / N/A) / ❌ FIX 원인. 기존 CFP-20 8 marker (⏸ ⏳ 🔄 ✅ ❌ 🔁 ⊘ N/A) 단순화. ⏳ semantic 변경 (blocked → pending). file / TodoWrite 두 channel 동일 어휘.

검출 label 정규화: review/test lane 의 terminal detection FAIL 인 경우에도 TodoWrite content label 은 `FIX-N detected` 정규화 (RESET 시 `FIX-N detected (cause: <원인 lane>, RESET-N)`). `FAIL` 은 review/test 판정 흐름의 terminal outcome vocabulary 로만 남음.

blocked / waiting 처리: 4-marker vocabulary 범위 밖. ⏳ pending 으로 표현, 진행 중 차단성 작업은 🔄 in_progress row 의 content 1줄 설명으로 표현.

### 결정 3 — ❌ semantic 정정

검출 lane (review/test 자체) 이 아닌 **원인 lane** 에 표시. 검출 lane 은 ✅ + content `FIX-N detected (cause: <원인 lane>)`. 원인 lane 은 기존 ✅ 가 ❌ 로 flip + content `FIX-N 원인 · <원인 판정 1줄>`. 재진입 lane 은 새 row append (⏳ 시작, content suffix `(재진입)` 또는 `(재진입 RESET-N)`).

### 결정 4 — Single-Story 모드

1 세션 = 1 active Story. TodoWrite row 의 `[KEY]` prefix drop. multi-Story TodoWrite 지원은 후속 CFP. single-Story collision (두 concurrent lane spawn 이 같은 Story TodoWrite write) 발생 시 hard-reset (canonical state 에서 full rewrite).

### 결정 5 — Hierarchical 2-level

lane row (0-indent) + agent sub-row (2-space indent). active lane 만 펼침. 다중 in_progress (TodoWrite "ONE in_progress" 가이드 deviation) 의도적 허용 — codeforge 의 병렬 agent 모델 (deputy 6/8 / workers parallel / parallel diagnosis) 본질상 불가피. 본 ADR 가 wrapper-specific deviation 명시.

cross-plugin generalization (lane plugins 에 동일 protocol 적용) 은 별도 CFP — 본 ADR scope 외부.

### 결정 6 — 재진입 = 새 row 추가

`(재진입)` 또는 `(재진입 RESET-N)` suffix. 기존 ❌ row 는 retrospective 기록으로 보존 (immutable). 다중 FIX (FIX-1 → FIX-2 동일 lane) 도 새 row append: 이전 ❌ row patch 안 함, 새 ❌ row append + 새 재진입 row append.

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

**Mechanism**: consumer `.claude/settings.json` `hooks.SessionStart[]` 에 `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` 을 등록함으로써, Claude Code harness 가 세션 부팅 시점에 helper script `templates/scripts/check-codeforge-prereq.sh` 의 stdout 을 Orchestrator 첫 turn context 에 prompt-injection 형태로 inject. helper script 본문 = 다음 instruction 의 static heredoc echo:

```
You MUST call the following as your first tool actions in this session, before
responding to any user message:

  ToolSearch(query="select:TodoWrite", max_results=1)

This loads schemas for deferred tools required by codeforge orchestration
(ADR-038 §결정 9). If ToolSearch fails: retry once. If retry fails: warn user,
continue without progress visualization (ADR-038 §결정 7 fallback).
```

**본 hook 의 책임 경계 (한계 명시 — Researcher 3-tier 중 (b) layer 한정)**:

- 책임: schema/state 가용성 보장 layer — Orchestrator turn 진입 시점에 deferred tool schema 가 prompt cache 에 fresh 한 상태로 가용함을 hook stdout prompt-injection 으로 강하게 advise.
- **비책임**: behavioral attempt 의무 자체는 §결정 8 그대로 retain — hook 도 prompt-level advisory 이며 mechanical function-call 강제가 아님. behavioral compliance 자체는 여전히 Orchestrator 책임.

**Extensibility — `prereq_tools[]` + `prereq_checks[]` array schema**:

본 hook sample 은 향후 추가 deferred tool (Monitor / WebFetch / 자주 쓰이는 mcp__github__\*) 또는 prereq check (ADR-053 structural-change verify / settings.json sanity) 가 필요할 경우 schema-only 갱신으로 list 확장 가능. **초기 preload list = TodoWrite 단독** (보수적 minimum, 향후 별도 CFP 가 measurable 도입 의도 후 확장).

**Layered defense (fallback retain)**:

| Tier | Mechanism | 본 §결정 9 적용 후 status |
|------|-----------|------------------------|
| (b) SessionStart hook | harness 가 첫 turn 에 prompt-injection | **PRIMARY (본 §결정 9 신설)** |
| (c) Runtime ToolSearch attempt | Orchestrator §결정 8 호출 의무 | RETAIN — hook 미등록 / 실행 실패 시 fallback |
| Failure handling | §결정 7 (warning only, lane 비차단) | RETAIN unchanged |

hook 등록 누락 / hook 실행 실패 → §결정 8 의 runtime ToolSearch 시도가 자동 fallback. 두 tier 가 layered defense 로 작동. §결정 7·8 폐기·축소 0건 — Amendment 2 는 §결정 8 의 "전제 조건" 부분 의 enforcement layer 만 격상.

**관련 파일** (Phase 2 PR scope):

- `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` (신규)
- `templates/scripts/check-codeforge-prereq.sh` (신규)
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
