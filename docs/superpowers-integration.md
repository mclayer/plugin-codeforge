---
doc_type: integration-policy
title: codeforge ↔ superpowers integration SSOT
status: Active
date: 2026-05-05
related_adrs:
  - ADR-013 (codeforge-family-dogfood-out-policy)
  - ADR-017 (skill override path enforcement)
  - ADR-028 (superpowers integration policy)
related_files:
  - CLAUDE.md
  - templates/skill-prompt-helpers/
  - scripts/check-superpowers-integration.sh
  - templates/github-workflows/superpowers-integration.yml
---

# codeforge ↔ superpowers Integration SSOT

본 문서는 codeforge family (wrapper + 6 lane plugin) 가 `superpowers@claude-plugins-official` 을 사용하는 단일 진실원. 모든 lane CLAUDE.md / agent md 는 본 문서를 link 로 참조 — 정책 재정의 금지 ([ADR-028](adr/ADR-028-superpowers-integration-policy.md) §결정 1).

## §1 현 상태 사실

superpowers 의존이 codeforge family 에 존재하는 4 표면 위치:

1. **[CLAUDE.md](../CLAUDE.md)** "필수 플러그인 9종" — `superpowers@claude-plugins-official` 표기 + 본 문서 link
2. **[overlay/hooks/check_bootstrap.py](../overlay/hooks/check_bootstrap.py)** `REQUIRED_PLUGINS` set — non-blocking WARN
3. **[docs/orchestrator-playbook.md §1.1](orchestrator-playbook.md)** checklist 0번 — 미설치 시 `/plugins install` 안내
4. **[docs/consumer-guide.md §0b](consumer-guide.md)** — 필수 4종 advertisement (consumer 측)

CI 안전망: [ADR-017](adr/ADR-017-skill-override-path-enforcement.md) + Amendment 1 (`docs/superpowers/{specs,plans}/**` plugin repo 금지 + agent md `Edit/Write(docs/superpowers/**)` 권한 표기 금지). [scripts/check-superpowers-integration.sh](../scripts/check-superpowers-integration.sh) lint script 가 PR check 로 fail-closed.

## §2 호출 지점 enumerate (SSOT 표)

본 표가 17 agent × 7 skill 호출 매핑 SSOT. 변경 시 본 표 + lane plugin agent md 동시 갱신 (CI lint 가 drift 자동 detect).

총 23 호출 지점 / 7 skill / 15 agent file (3 ReviewPL agent 는 skill 호출 없음 — stale path 정리 대상만, §5 참조).

| Lane | Agent | codeforge Phase trigger | Skill | Path override | I/O 계약 | Phase target |
|---|---|---|---|:-:|---|---|
| design | ArchitectAgent | 설계 lane R3 (Change Plan §3) | superpowers:writing-plans | YES | §3 row 1 | plugin-codeforge-design Phase 2 |
| design | ArchitectAgent | 설계 lane R2 (대안 탐색) | superpowers:brainstorming | YES | §3 row 2 | plugin-codeforge-design Phase 2 |
| design | ArchitectAgent | FIX 수령 (root cause) | superpowers:systematic-debugging | NO | §3 row 4 | plugin-codeforge-design Phase 2 |
| design | ArchitectPLAgent | 설계 lane synthesis | superpowers:writing-plans | YES | §3 row 1 | plugin-codeforge-design Phase 2 |
| design | ArchitectPLAgent | 6 deputy 병렬 spawn | superpowers:dispatching-parallel-agents | NO | §3 row 6 | plugin-codeforge-design Phase 2 |
| design | ArchitectPLAgent | FIX 수령 | superpowers:systematic-debugging | NO | §3 row 4 | plugin-codeforge-design Phase 2 |
| design | DataMigrationArchitectAgent | §11 author input | superpowers:writing-plans | YES | §3 row 1 | plugin-codeforge-design Phase 2 |
| design | RefactorAgent | §6 author input | superpowers:writing-plans | YES | §3 row 1 | plugin-codeforge-design Phase 2 |
| design | SecurityArchitectAgent | §7 author input | superpowers:writing-plans | YES | §3 row 1 | plugin-codeforge-design Phase 2 |
| design | TestContractArchitectAgent | §8 author input | superpowers:writing-plans | YES | §3 row 1 | plugin-codeforge-design Phase 2 |
| develop | DataEngineerAgent | 파이프라인 장애 진단 | superpowers:systematic-debugging | NO | §3 row 4 | plugin-codeforge-develop Phase 2 |
| develop | DeveloperAgent | 구현 (TDD) | superpowers:test-driven-development | NO | §3 row 3 | plugin-codeforge-develop Phase 2 |
| develop | DeveloperAgent | 구현 장애 진단 | superpowers:systematic-debugging | NO | §3 row 4 | plugin-codeforge-develop Phase 2 |
| develop | QADeveloperAgent | tests/** 작성 (TDD) | superpowers:test-driven-development | NO | §3 row 3 | plugin-codeforge-develop Phase 2 |
| requirements | DomainAgent | 요구사항 대안 탐색 | superpowers:brainstorming | YES | §3 row 2 | plugin-codeforge-requirements Phase 2 |
| requirements | DomainAgent | 지식 공백 점검 | superpowers:verification-before-completion | NO | §3 row 5 | plugin-codeforge-requirements Phase 2 |
| requirements | RequirementsAnalystAgent | 사용자 확인 점검 | superpowers:verification-before-completion | NO | §3 row 5 | plugin-codeforge-requirements Phase 2 |
| requirements | RequirementsPLAgent | 요구사항 대안 탐색 | superpowers:brainstorming | YES | §3 row 2 | plugin-codeforge-requirements Phase 2 |
| requirements | RequirementsPLAgent | 통합 명세 점검 | superpowers:verification-before-completion | NO | §3 row 5 | plugin-codeforge-requirements Phase 2 |
| requirements | ResearcherAgent | 출처 URL 점검 | superpowers:verification-before-completion | NO | §3 row 5 | plugin-codeforge-requirements Phase 2 |
| review | ClaudeReviewAgent | 표준 체크리스트 | superpowers:code-reviewer | NO | §3 row 7 | plugin-codeforge-review Phase 2 |
| review | ClaudeReviewAgent | PASS evidence 점검 | superpowers:verification-before-completion | NO | §3 row 5 | plugin-codeforge-review Phase 2 |
| pmo | PMOAgent | Story 완료 감사 | superpowers:verification-before-completion | NO | §3 row 5 | plugin-codeforge-pmo Phase 2 |

## §3 I/O 변환 표 (skill → codeforge artifact)

| skill | codeforge artifact target | 변환 룰 |
|---|---|---|
| 1. brainstorming | `<internal-docs>/<lane>/specs/` (canonical) + `docs/stories/<KEY>.md §6` (Acceptance Criteria) | spec 본문 → §6 측정 가능 기준; 대안 탐색 → §3 도입할 설계 candidate |
| 2. writing-plans | `<internal-docs>/<lane>/plans/` (canonical) + `docs/change-plans/<slug>.md §3 도입할 설계` | plan step 1-N → Change Plan §3 절차; 0-context 개발자 전제 → §6 리팩터링 선행 |
| 3. test-driven-development | `docs/change-plans/<slug>.md §8 Test Contract` + `tests/**` | TDD red-green-refactor → §8 unit/integration/infra/perf 분류; §8.5 Stateful invariant 별도 |
| 4. systematic-debugging | `docs/stories/<KEY>.md §10 FIX Ledger` (column 원인 판정 / 재실행 범위) | 매 iteration 다른 가설 → §10 row append; root cause → 설계 vs 구현 dichotomy |
| 5. verification-before-completion | gate label (gate:design-review-pass / gate:security-test-pass) + Story §9 evidence | 체크리스트 빠짐 방지 → review-verdict-v3 packet evidence column |
| 6. dispatching-parallel-agents | playbook §3 parallel spawn 판단 (track A ∥ track B) | 병렬 fan-out 근거 → spawn 시점 + sub-agent 수 + non-skippable 매트릭스 |
| 7. code-reviewer | review-verdict-v3 finding format + lane-specific 체크리스트 | 표준 체크리스트 + lane 책임 매트릭스 dedup |

## §4 Path override 강제 메커니즘

**계층**:
1. **선제 (prompt-time)**: [`templates/skill-prompt-helpers/`](../templates/skill-prompt-helpers/) fragment — agent md / Orchestrator prompt 가 `Read(${CLAUDE_PLUGIN_ROOT}/codeforge/templates/skill-prompt-helpers/<fragment>.md)` 패턴으로 inline reference. fragment 안에 explicit path override 안내.
2. **사후 (PR-time)**: [ADR-017](adr/ADR-017-skill-override-path-enforcement.md) + Amendment 1 CI lint — `docs/superpowers/{specs,plans}/**` 경로 file 생성 + agent md `Edit/Write(docs/superpowers/**)` 권한 표기 금지. fail-closed.

**4 fragment** (wrapper-owned, lane import-only — [ADR-028](adr/ADR-028-superpowers-integration-policy.md) §결정 5):
- `templates/skill-prompt-helpers/brainstorming-path-override.md`
- `templates/skill-prompt-helpers/writing-plans-path-override.md`
- `templates/skill-prompt-helpers/tdd-discipline.md`
- `templates/skill-prompt-helpers/verification-before-completion.md`

## §5 Stale legacy path 정리 protocol

**Target (lint check 2 에서 자동 detection 됨, 4 file)**: 3 ReviewPL agent (DesignReviewPL / CodeReviewPL / SecurityTestPL) + PMOAgent 권한 의 `Edit(docs/superpowers/**)` + `Write(docs/superpowers/**)`.

**정리 룰**: ADR-013 후 spec/plan SSOT = `<internal-docs>/<lane>/specs/` + `/plans/`. ReviewPL 의 self-write owner = Story §9 + GitHub PR comment 만 (CFP-61 ADR-022 후 review-verdict v3 final write 는 Orchestrator). PMOAgent 의 self-write owner = `<internal-docs>/<plugin-folder>/retros/` + Epic Issue body. `docs/superpowers/**` 권한 = stale, 제거.

**Acceptance criteria** (Phase 2-7 lane plugin PR): 각 lane plugin Phase PR 마다 본 protocol 준수 검증. CI lint check 2 가 자동 fail-closed. 정리 대상 분포: codeforge-review (3 ReviewPL) + codeforge-pmo (PMOAgent 1).

## §6 Lane plugin 후속 CFP 가이드

Phase 1 wrapper PR merge 직후 6 lane CFP batch open. 각 lane CFP scope:

| Phase | Lane plugin | Target file 수 | Acceptance criteria |
|---|---|---|---|
| 2 | codeforge-requirements | 4 agent md | superpowers reference SSOT §2 link only, stale path 0 |
| 3 | codeforge-design | 8 agent md | (동일) |
| 4 | codeforge-review | 5 agent md (3 PL stale + 2 worker prose) | stale `docs/superpowers/**` 권한 제거 의무 |
| 5 | codeforge-develop | 5 agent md | (동일) |
| 6 | codeforge-test | 2 agent md | (동일) |
| 7 | codeforge-pmo | 1 agent md | (동일) |

각 lane CFP = 별도 child Story (Mode B hub-centralized — wrapper repo = Epic owner, [ADR-020](adr/ADR-020-cross-repo-epic-pattern.md)).
