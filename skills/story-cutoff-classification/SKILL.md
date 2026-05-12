---
name: story-cutoff-classification
description: Story 작성 의무 vs chore commit 면제 분류 시 (사용자 요구사항 접수 직후). 강제 대상 / doc-only fast-path / 면제 대상 3종 분류 기준을 정의한다.
tools: Read
---

# Story 작성 의무 분류 기준 (CFP-45)

> 참조 테이블 skill — 요구사항 접수 직후 Story 작성 의무 vs chore commit 면제를 판정하세요.

매 변경 시작 시 Orchestrator 가 cutoff 분류 → 강제/면제 결정. **모호 시 강제 측 분류**. Plugin 자체 + consumer 프로젝트 모두 적용. 정책 SSOT: [ADR-013](../../docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md). Story file 위치 = `mclayer/codeforge-internal-docs/<plugin-folder>/stories/<KEY>.md` (Plugin repo Issue body 와 bidirectional `story_uri`/`story_issues` binding). 새 Story = internal-docs `story.yml` Issue Form → `story-init.yml` Action 자동 생성 + Phase 1 PR open.

## 강제 대상 (Story file 작성 의무)

- 신규 ADR 결정 / 기존 ADR 변경
- 아키텍처·도메인 모델 추가·삭제·재정의
- 에이전트 추가·삭제·역할 재정의
- Workflow 정의(`templates/github-workflows/**`) 변경
- SSOT 문서(`templates/`·`presets/`·`CLAUDE.md`·`docs/orchestrator-playbook.md`) 의미 변경
- Breaking change · consumer migration 영향

## doc-only fast-path 대상 (ADR-054)

SSOT 문서 변경 + 기존 ADR Amendment 또는 ADR 없음 + src/tests 무변경인 Story.
lane: 요구사항 → 설계 → 경량 설계리뷰 → 단일 PR close (구현 lane skip).
신규 ADR 도입 Story = full-lane 강제. 모호 시 full-lane 강제 (안전 방향).
판정 표 SSOT: [ADR-054](../../docs/adr/ADR-054-doc-only-story-fast-path.md).

## 면제 대상 (chore commit OK)

- Typo · 문법 · 줄바꿈 · 마크다운 형식 정리
- 링크 깨짐 수정 / 죽은 링크 제거
- Lint 자동 fix · dependency lock · version bump (security 영향 없는 경우)
- README 단순 문구 수정

면제 시 commit body 에 `Story 면제 사유: <이유>` 1줄 명시. 판단 시점: cutoff 분류 선언 (변경 시작 시) + commit 직전 재확인.

## Brainstorming/writing-plans skill default override

Plugin repo (codeforge family) 작업 시:
- `superpowers:brainstorming` skill spec 저장 위치 = `<internal-docs-clone>/<plugin-folder>/specs/` (default `docs/superpowers/specs/` 아님)
- `superpowers:writing-plans` skill plan 저장 위치 = `<internal-docs-clone>/<plugin-folder>/plans/` (default 아님)
- Controller (Orchestrator) 가 path 명시 의무, Skill prompt 에 explicit override
- Plugin repo CI (`dogfood-artifact-paths`) 가 PR 단계에서 fail-closed (ADR-017). Skill prompt 정책 인지는 1차 안전망, CI 가 authoritative
- `codeforge:brainstorm` skill = codeforge 프로젝트 전용 강화 brainstorming (ADR-034 Amendment 1·2). Phase 0 자동 실행 (CFP-386, Amendment 2). `superpowers:brainstorming` 상위호환.

Consumer overlay: `.claude/_overlay/project.yaml` `story_cutoff.additional_exempt_categories[]` 로 도메인 특화 면제 추가 가능 (**강제 항목 축소 불허** — 안전 방향만). Schema [`docs/project-config-schema.md`](../../docs/project-config-schema.md) §2.

본 plugin repo dogfooding: KEY prefix `CFP`. Plugin meta 변경 시 무의미한 lane 은 `N/A — <사유>` 명시 (ADR-005 standardization).

**Branch governance** (CFP-66 / ADR-024): 모든 wrapper 변경 = Story-scoped feature branch (`cfp-NNN[-<slug>]`) + PR 경유 의무. main 직접 push 금지 — branch protection `restrictions:{users:[],teams:[],apps:[]}` 물리 차단. emergency hotfix 도 PR 경유 (no exception). 병렬 modification 지원 = Story 단위 독립 branch + 독립 PR. 정책 SSOT: [ADR-024](../../docs/adr/ADR-024-story-scoped-branch-policy.md).
