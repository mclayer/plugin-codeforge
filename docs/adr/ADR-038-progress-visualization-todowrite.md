---
adr_number: 38
title: Progress visualization via TodoWrite (single-Story, hierarchical 4-marker)
date: 2026-05-08
status: Accepted
category: orchestration
carrier_story: CFP-274
supersedes: null
---

# ADR-038: Progress visualization via TodoWrite (single-Story, hierarchical 4-marker)

## 상태

Accepted (2026-05-08). carrier_story = CFP-274. Effective = Phase 2 wrapper PR merge timestamp (retroactive 미적용).

## 컨텍스트

CFP-20 (`docs/orchestrator-playbook.md` §14, `.claude-work/progress/<KEY>.md` derivative cache file) + ADR-029 (sub-step stderr narration) 가 진행상황 가시화 2 channel 제공. 사용자 directive (2026-05-08, 11 turn) — TodoWrite 가 CC 네이티브 sticky UI 로 가장 시각적인 channel 인데 codeforge 가 미사용. 본 ADR 가 3번째 channel 로 추가.

추가 사용자 directive (2026-05-08) — Sonnet decider 는 codeforge 가 자동 dispatch 하는 도구가 아닌, 사용자 임의 호출 전용 도구. ADR-022 deprecate 예정 (CFP-134 carrier). 본 ADR 는 codeforge 자동 dispatch 가정하지 않음.

## 결정 요약 (7 결정)

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

## 관련 파일

- `docs/orchestrator-playbook.md` §14.4 / §14.5 / §14.7 / §14.8
- `CLAUDE.md` Orchestration 규칙 §
- `wrapper/specs/2026-05-08-cfp-274-progress-visualization-todowrite-design.md` (internal-docs SSOT)
- `wrapper/change-plans/cfp-274-progress-visualization-todowrite.md` (internal-docs)
- `wrapper/stories/CFP-274.md` (internal-docs)
- `wrapper/decisions/CFP-274-001-codex-spec-review.yaml` (internal-docs)
