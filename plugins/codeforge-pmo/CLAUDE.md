# CLAUDE.md (codeforge-pmo)

codeforge ζ arc PMO lane plugin. PMOAgent 가 codeforge core 의 Orchestrator 에 의해 스폰되어 Cross-cutting 책임 수행 — 단일 lane gate 에 무관.

## Plugin position

본 plugin 은 codeforge wrapper 의 dependency. 단독 동작 불가 — codeforge core (>= 1.0.0) 가 Orchestrator + Story file lifecycle + GitHub workflow CI 보유.

설치 + 의존성 + architecture 는 [`README.md`](README.md) 참조.

## Inter-plugin contracts

- `pmo_output v1` — wrapper repo 루트 `docs/inter-plugin-contracts/pmo-output-v1.md` (canonical SSOT — 설치 캐시 기준 plugin 디렉터리 외부, 링크 비제공)
- codeforge wrapper 측 sibling reference: `mclayer/plugin-codeforge/docs/inter-plugin-contracts/pmo-output-v1.md`

## Self-write 책임 (CFP-36 ζ arc 패턴 + CFP-139 GitOps)

PMOAgent 가 다음을 직접 write:

| Path | 트리거 | Mechanism |
|---|---|---|
| `docs/retros/<sprint>.md` | **story_completion (Phase 2 PR merge 자동, CFP-138 / [ADR-045](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-045-story-retro-mandatory-trigger.md) mandate)** / cross_story_audit_request (사용자 요청) | `Edit(docs/retros/**)` |
| `docs/stories/<KEY>.md §11` | story_completion (4 field schema: retro_file / retro_summary / learnings_count / feedback_back_to_codeforge — CFP-138 / ADR-045 D-5) | `Edit(docs/stories/**)` |
| `gate:retro-complete` label add | story_completion (retro write 완료 후 — CFP-138 / ADR-045 forcing function) | `mcp__github__issue_write` |
| Epic GitHub milestone | epic_creation / story_completion | `gh api repos/*/milestones*` |
| GitHub comment `[PMO]` prefix | 모든 trigger | `mcp__github__add_issue_comment` |
| `pmo_output v1.2.cross_story_pattern_adr_trigger` field 채움 + `adr_proposal` field 동시 채움 (status: Proposed inline ADR draft) | **Cross-Story pattern threshold reach (≥ 2)** — retro write 시점 patterns_observed[] 검출 직후 (CFP-665 / ADR-045 Amendment 5 §D-9, Mandatory framing — PMOAgent self-decide 영역 제거) | inline pmo_output return → Orchestrator forward to ArchitectAgent (codeforge-design lane spawn) |

**Epic-close 구현-리팩터링 triage (ADR-137, §D-11 sibling·axis-disjoint)**: PMOAgent 는 Epic-close 시점에 구현-리팩터링 triage 의 **verdict judge** 로도 발동 — 3분기 verdict(now/defer/drop) 판정 + drop-ledger(`docs/refactor-triage/drop-ledger.md`) read/count(≥2 escalation) + defer verdict → `EPIC-RESULTS-<EPIC_KEY>.md` `## §deferred` 5-column row(source=`triage-defer`) 변환 append. **dispatch 주체 아님**: 실 debate dispatch = Orchestrator inline(ADR-039 §결정18 재귀 가드, self-spawn 불가). §D-11(retro follow-up Issue batch closure)과 대상 모집단·enum axis-disjoint (동일시 금지). 상세 = [`agents/PMOAgent.md §4.3`](agents/PMOAgent.md).

GitOpsAgent (CFP-139 신설 long-running teammate) 가 다음을 직접 write:

| Path | 트리거 | Mechanism |
|---|---|---|
| `.claude-work/worktree-manifest.yaml` | TeamCreate / TeamDelete / FIX iteration / stale cleanup | `Edit/Write(.claude-work/worktree-manifest.yaml)` |
| `docs/stories/<KEY>.md §10.5 Git Ops Log` | 매 git ops event (append-only) | `Edit(docs/stories/**)` |
| GitHub comment `[GitOps]` prefix | conflict / escalation | `mcp__github__add_issue_comment` |

DocsAgent 경유 안 함 ([CFP-31 parent spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md)).

### Retro 자동 trigger flow (CFP-138 / ADR-045)

Phase 2 PR merge 후 자동 trigger 의무 — 사용자 요청 불필요. FIX iter 1 F-1 verbatim 6-source sync (cumulative offset from PR merge timestamp):

1. wrapper repo 의 `templates/github-workflows/retro-mandatory.yml` workflow 발화 (PR closed + merged=true)
2. **First attempt at PR merge + 5min** (5min grace period) — PMOAgent retro write 시간 부여
3. PMOAgent self-write (5 sub-steps):
   - `docs/retros/<sprint>-cfp-NNN-<slug>.md` 신규 생성 (`templates/retro.md` schema 정합)
   - Story file §11 회고 블록 4 field schema update
   - Epic milestone description 갱신
   - `gate:retro-complete` label add (forcing function 의 핵심 단계)
   - `[PMO]` prefix comment
4. First attempt 후에도 `gate:retro-complete` label 부재 시 retry policy:
   - **Retry 1 at PR merge + 10min** (5min wait after first attempt fail)
   - **Retry 2 at PR merge + 20min** (10min wait after retry 1 fail)
   - **Retry 3 at PR merge + 35min** (15min wait after retry 2 fail, final attempt)
   - **ESCALATE at PR merge + 35min 후** (4 attempts 모두 fail 시 사용자 ESCALATE)
   - **Total attempts = 4** (1 initial + 3 retries). **Total max latency = 35min** (5min grace + 5+10+15 retry waits)
   - Phase 2 PR scope retry state machine (jsonl-state-store + cron re-trigger) — Phase 1 PR scope = first attempt 만 implement
5. Story Issue close 차단 (auto-reopen) — retro 작성 후에만 close 가능

**§6 ADR 후보 발의 pre-publish 8-tuple verify gate (CFP-1623 / CFP-1632, [ADR-045 Amendment 9 §D-10](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-045-story-retro-mandatory-trigger.md) — Wave 2 mechanical wire active)**:

retro file `§6 ADR 후보 발의` 안 ADR draft candidate 작성 직전 — 8 independent source AND gate 통과 의무 (Mandatory framing, PMOAgent self-decide 영역 제거). 1+ source disagree 시 `downgrade_action` 2-value enum 자동 적용 (`to_section_4_informational` | `pivot_mark`). pmo-output-v1 v1.3 `retro_section_6_pre_publish_verify` optional field (3 sub-field: `verify_sources_attempted[]` / `verify_sources_blocked[]` / `downgrade_action`) 채움 의무. 상세는 [`agents/PMOAgent.md §4.1`](agents/PMOAgent.md) — 8-tuple source enum + platform exemption marker + mechanical enforcement (132nd evidence-checks-registry entry `retro-batch-adr-draft-pre-publish` warning tier + `hotfix-bypass:retro-batch-adr-draft-pre-publish` 102nd family member).

상세 정책 SSOT: [ADR-045](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-045-story-retro-mandatory-trigger.md) D-1 ~ D-10.

## GitOpsAgent (CFP-139)

본 plugin 은 PMOAgent (one-shot trigger-driven, Cross-cutting 회고·감사) + GitOpsAgent (long-running teammate, git operations orchestrator) 2 sibling agent 로 구성.

| 영역 | PMOAgent | GitOpsAgent |
|------|:--------:|:-----------:|
| 회고 / Cross-Story 패턴 / ADR 발의 / Epic 분해 자문 | ✅ | — |
| Hierarchical branch tree / Worktree lifecycle / Sequential merge / FIX iteration 재구성 / Stale cleanup | — | ✅ |

GitOpsAgent 는 Orchestrator + 모든 lane PL agent 의 git 작업 (branch / worktree / merge / cleanup) 단일 위임 대상. PMOAgent 와 병렬로 작동 — Story 도메인 결정 영역 무관 (코드 / 회고 영역 deny).

**SendMessage peer protocol**: GitOpsAgent ↔ Orchestrator (lead) / PMOAgent (sibling, hotspot 패턴 보고) / 각 lane PL agent (sibling, conflict escalation + TeamCreate/Delete request). 직접 sub-agent spawn 불가 — Orchestrator 경유 (codeforge family ADR-009 invariant).

Agent 상세 SSOT: [`agents/GitOpsAgent.md`](agents/GitOpsAgent.md).

> **DialogFidelityAgent sunset (CFP-2236, 2026-06-14)**: 구 3번째 sibling DialogFidelityAgent (one-shot read-only dialog fidelity verifier) 는 전면 폐지. agent count 3→2. 근거 = 3-anchor spawn 의무 런타임 미준수 (죽은 의무) + 동일 anchor Codex TP#2/TP#3 + ADR-064 Q-3check 검증 ground 중복 + Opus verifier spawn 비용 대비 측정 효과 0. 폐지 결정 박제 = ADR-071 Amendment 9 (carrier-preserved). ADR-071 본체 (frame mode + 4 layer + 3 touchpoint) 는 무손상 보존.

## Cross-Story patterns 입력 → ADR 발의 hand-off

PMOAgent 가 cross_story_audit_request 트리거에서 cross-Story 패턴 (FIX 반복·ESCALATE 트렌드·성능 회귀·코드 핫스팟) 발견 시:
- `pmo_output v1.adr_proposal` 필드에 ADR 후보 (status: Proposed) 발의
- Orchestrator 가 codeforge-design plugin (CFP-40 후) 또는 codeforge wrapper 의 ArchitectAgent 에 hand-off
- 본 plugin 은 ADR file 직접 write 안 함 — 발의만

## Dogfood policy (CFP-45)

본 plugin repo 는 runtime SSOT 만 보유. dogfood artifacts (specs/plans/retros/stories/change-plans) 는 [`mclayer/codeforge-internal-docs`](https://github.com/mclayer/codeforge-internal-docs) 단일 monorepo SSOT. 본 plugin 폴더는 `codeforge-internal-docs/pmo/`. 상세 정책 + Story workflow 흐름은 wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) canonical SSOT 참조 + [ADR-013](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (PR-I 머지 후 Adopted).

Plugin repo 측 GitHub Issue 와 internal-docs 측 Story file 의 binding:
- Issue body frontmatter: `story_uri: <internal-docs URL>`
- Story file frontmatter: `story_issues: [{repo: "mclayer/plugin-codeforge", number: <N>}]`
- `.github/workflows/phase-gate-mergeable.yml` (본 repo) 가 cross-repo Story fetch via GitHub App
