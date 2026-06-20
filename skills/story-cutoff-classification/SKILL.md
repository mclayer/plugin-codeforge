---
name: story-cutoff-classification
description: 모든 변경 Story 작성 의무 분류 (사용자 요구사항 접수 직후). 면제·단축 0 — 모든 변경이 정식 풀 플로우 + Story file 작성 대상 (ADR-127).
tools: Read
---

# Story 작성 의무 분류 기준 (CFP-45 / ADR-127)

> 참조 테이블 skill — 요구사항 접수 직후 Story 작성 의무를 확인하세요. **면제·단축경로 0 — 모든 변경이 Story 작성 대상**(ADR-127 §결정 1).

매 변경 시작 시 Orchestrator 가 cutoff 분류 → **모든 변경 = Story 작성 의무**(chore 면제 / doc-only fast-path 폐지 — ADR-127). 오타·lint·버전범프·링크수정 같은 순수 기계적 변경도 정식 풀 플로우 + Story file 작성 대상. Plugin 자체 + consumer 프로젝트 모두 적용. 정책 SSOT: [ADR-013](../../archive/adr/ADR-013-codeforge-family-dogfood-out-policy.md) (+ Amendment 8) + [ADR-127](../../archive/adr/ADR-127-mandatory-full-flow-no-exemption.md). Story file 위치 = `mclayer/codeforge-internal-docs/<plugin-folder>/stories/<KEY>.md` (Plugin repo Issue body 와 bidirectional `story_uri`/`story_issues` binding). 새 Story = internal-docs `story.yml` Issue Form → `story-init.yml` Action 자동 생성 + Phase 1 PR open.

## 모든 변경 = Story 작성 의무 (강제 단일 분류 — ADR-127 §결정 1)

아래는 **예시 enumeration** 일 뿐, 분류 분기가 아니다 — 모든 변경이 Story 작성 + 정식 풀 플로우 대상이다.

- 신규 ADR 결정 / 기존 ADR 변경
- 아키텍처·도메인 모델 추가·삭제·재정의
- 에이전트 추가·삭제·역할 재정의
- Workflow 정의(`templates/github-workflows/**`) 변경
- SSOT 문서(`templates/`·`presets/`·`CLAUDE.md`·`docs/orchestrator-playbook.md`) 의미 변경
- Breaking change · consumer migration 영향
- 오타·문법·줄바꿈·마크다운 형식·링크수정·lint 자동fix·dependency lock·버전범프·README 단순 문구 (종전 chore 면제 대상 — ADR-127 §결정 1 로 Story 작성 의무 승격)

**chore 면제 폐지 (ADR-127 §결정 1)**: `Story 면제 사유:` commit body marker 채널 폐지. doc-only fast-path(단일 PR, 구현 lane skip) 폐지 — 모든 Story = full 10 lane + Phase 1 PR(§1-7) + Phase 2 PR(§8-11) 분리 무조건(ADR-127 §결정 2). "lane 의 노력 절감 skip" 만 폐지 — lane 이 검사할 산출물 target 이 부재한 자연 N/A 는 정식 분류의 정상 결과(ADR-005 / ADR-127 §결정 5 3축 AND).

## Brainstorming/writing-plans skill default override

Plugin repo (codeforge family) 작업 시:
- `codeforge:brainstorm` skill spec 저장 위치 = `<internal-docs-clone>/<plugin-folder>/specs/` (default `docs/superpowers/specs/` 아님)
- `codeforge:writing-plans` skill plan 저장 위치 = `<internal-docs-clone>/<plugin-folder>/plans/` (default 아님)
- Controller (Orchestrator) 가 path 명시 의무, Skill prompt 에 explicit override
- Plugin repo CI (`dogfood-artifact-paths`) 가 PR 단계에서 fail-closed (ADR-017). Skill prompt 정책 인지는 1차 안전망, CI 가 authoritative
- `codeforge:brainstorm` skill = codeforge 프로젝트 전용 강화 brainstorming (ADR-034 Amendment 1·2). Phase 0 자동 실행 (CFP-386, Amendment 2). 외부 plugin 없이 자립 (ADR-122 §결정2).

Consumer overlay: **면제 추가 불가** — `story_cutoff.additional_exempt_categories[]` 면제 확장채널 폐지(ADR-127 §결정 6). overlay 는 정책을 **확장(더 엄격하게 — 강제 추가)** 만 가능하고 면제 추가(강제 축소)는 애초에 invariant 위반이었다. consumer 는 강제 정책을 더할 수만 있다. Schema [`docs/project-config-schema.md`](../../docs/project-config-schema.md) §2.

본 plugin repo dogfooding: KEY prefix `CFP`. Plugin meta 변경 시 무의미한 lane 은 `N/A — <사유>` 명시 (ADR-005 standardization).

**Branch governance** (CFP-66 / ADR-024): 모든 wrapper 변경 = Story-scoped feature branch (`cfp-NNN[-<slug>]`) + PR 경유 의무. main 직접 push 금지 — branch protection `restrictions:{users:[],teams:[],apps:[]}` 물리 차단. emergency hotfix 도 PR 경유 (no exception). 병렬 modification 지원 = Story 단위 독립 branch + 독립 PR. 정책 SSOT: [ADR-024](../../archive/adr/ADR-024-story-scoped-branch-policy.md).
