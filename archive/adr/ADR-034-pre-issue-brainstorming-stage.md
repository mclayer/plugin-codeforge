---
adr_number: 34
title: Pre-Issue Brainstorming as Optional Stage 0 — orchestrator-playbook §1.2.0 + story.yml spec_link
date: 2026-05-07
status: Accepted
category: workflow-policy
carrier_story: CFP-129
parent_epic: null
supersedes: null
amends: null
amendments:
  - id: 1
    carrier_story: CFP-345
    date: 2026-05-09
    title: "codeforge:brainstorm 통합 — Stage 0 Requirements 에이전트 참여"
  - id: 2
    carrier_story: CFP-386
    date: 2026-05-11
    title: "Phase 0 자동 실행 — opt-in AskUserQuestion 폐지"
  - id: 3
    carrier_story: CFP-2249
    date: 2026-06-15
    title: "superpowers fallback 문구 제거 — codeforge:brainstorm 자립 (ADR-122 §결정 7)"
related_stories:
  - CFP-129
  - CFP-2249   # Amendment 3 — superpowers fallback 제거
related_adrs:
  - ADR-013
  - ADR-017
  - ADR-027
  - ADR-028
  - ADR-031
  - ADR-032
  - ADR-122   # Amendment 3 — superpowers 의존 완전 제거 (fallback 대상 소멸)
related_files:
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/superpowers-integration.md
  - templates/skill-prompt-helpers/brainstorming-path-override.md
  - templates/github-issue-forms/story.yml
  - CLAUDE.md
is_transitional: false
---

# ADR-034: Pre-Issue Brainstorming as Optional Stage 0

## 상태

**Accepted (2026-05-07)** — CFP-129 Phase 1 wrapper PR mclayer/plugin-codeforge#245 (merged 2026-05-07T14:41:16Z) + Phase 2 wrapper PR (본 PR, merge 시점에 effective). carrier_story = CFP-129 (single Story, single-repo, not part of Epic). Effective date = Phase 2 wrapper PR merge timestamp (ADR-031 §14 freeze pattern 재사용 — 본 effective date 이전 Phase 1 PR open 된 모든 Story = grandfather, retroactive 강제 없음).

Phase 1 internal-docs PR (mclayer/codeforge-internal-docs#70, merged 2026-05-07T14:42:32Z) — spec / plan / Change Plan / Story §1-§7 / Codex 7-area review CONDITIONAL_PASS archive.

ADR-027 Amendment 1 / CFP-127 정합 — Proposed → Accepted 2-stage 패턴.

## 컨텍스트

사용자 directive (2026-05-07 conversation, claude-opus-4-7 wrapper session):

> consumer project에서 brainstorming으로 요구사항을 확장한 다음 codeforge를 통할 수 있도록 할 수 있는가?
>
> 그렇게 할 수 있도록 하자.

### 현재 상태

`docs/orchestrator-playbook.md` §1.2 신규 세션 플로우 = 사용자 요구사항 접수 후 Issue Forms 또는 Orchestrator 직접 분해 2 가지 옵션만 명시. Issue Form **제출 전** 사용자 / consumer Orchestrator 가 brainstorming 으로 scope 정리하는 절차 = 미문서화.

`docs/superpowers-integration.md` §2 SSOT 의 brainstorming 호출 2 행 (`requirements / DomainAgent / 요구사항 대안 탐색` + `requirements / RequirementsPLAgent / 요구사항 대안 탐색`) 은 모두 **lane 내부** 호출 — 사용자 입력이 이미 Issue Form 으로 들어온 후 lane plugin agent 가 호출. Pre-Issue scoping (사용자 발화 → Issue Form 제출 전) 은 다른 단계.

`templates/skill-prompt-helpers/brainstorming-path-override.md` fragment 는 ADR-013 / ADR-017 enforce path override 안내 — 단 in-lane 시나리오만 다룸.

### Gap
- Pre-Issue 시나리오 = 미문서화 (사용자 / consumer Orchestrator 가 임의로 호출 가능하나 호출점 / spec 위치 / Issue Form 연결 mechanism SSOT 부재)
- story.yml Issue Form 에 brainstorming spec 보존 필드 부재 → 사용자 가 Issue body 자유 형식에 적어 두면 traceability 약함

## 결정

### D1. Pre-Issue brainstorming = optional Stage 0

**순수 옵션** — CI 강제 없음, 권장만. 비-trivial Story (cross-cutting / 새 도메인 / 모호한 scope) 에 권장. 작은 chore Story / 명료한 요구사항이면 생략 가능.

> **cross-ref (ADR-027 Amendment 10 / §결정 13, CFP-2243)**: 미초기화 greenfield consumer 에서 codeforge 의도 선언 시 발동하는 bootstrap-first entry-gate (UserPromptSubmit 훅 + skill 게이트 절차) 의 대상 = **bootstrap 미초기화 감지·제안** — brainstorm 진입 자체 차단 아님. warning inject only (exit 0), 사용자 거부 시 진행. 본 D1 (brainstorm = 순수 옵션, CI 강제 없음) 보존 — 게이트는 초기화 우선 "유도(권고)" 만 수행하며 hard-block 미사용. (D1 자기모순 회피 — "진입 시 상태 확인 의무" 를 본 ADR 에 넣지 않고 ADR-027 §결정 13 에 위임.)

**거절된 대안**:
- (B) 복잡도 임계 위 mandatory: 임계 정의 모호. CI 강제 = 옵션 정책 위배.
- (C) 모든 Story mandatory: 작은 chore (typo fix / link repair) 도 Stage 0 강제 → 과도. in-lane brainstorming (DomainAgent / RequirementsPL) 으로 lane 내부 보호 이미 존재.

### D2. Spec ↔ Issue Form 연결 = Both

**Both** — 신규 optional `spec_link` 필드 (path/URL) + 기존 `user-original` 필드 (결론 요약 paste, §1 verbatim source).

근거: spec 본문은 길어서 §1 verbatim 으로 부적합. 결론 요약을 user-original 에 paste, 원문은 path link 로 보존 (장기 archive).

### D3. story.yml fixture = additive only

신규 textarea field `spec_link`, `validations.required: false`, free-form (URL 또는 relative path). 기존 `user-requirement-verbatim` / `epic-milestone` / `component` field 변경 없음. SemVer minor (additive optional field). 기존 Story / Issue 영향 없음 (미입력 valid).

### D4. Skill prompt helper = sub-section append

기존 [`templates/skill-prompt-helpers/brainstorming-path-override.md`](../../templates/skill-prompt-helpers/brainstorming-path-override.md) 에 "Pre-Issue scenario" sub-section append. 별도 fragment 신설 안 함.

근거: [ADR-028](ADR-028-superpowers-integration-policy.md) §결정 5 — wrapper-owned fragment 4 개 고정. 1 fragment 안에 in-lane / pre-Issue 2 시나리오 분리가 더 간결.

### D5. superpowers-integration.md §2 표 = 1 row + footnote

기존 23 호출 지점 → 24 호출 지점. 신규 row = `wrapper / Orchestrator (or human) / pre-Issue scoping (Stage 0) / 외부 plugin brainstorming skill / YES / §3 row 2 / wrapper Phase 1 (post-merge: Issue Form 제출)`. (Amendment 3 / ADR-122: superpowers-integration.md 자체가 sunset 제거됨 — 본 row 는 당시 통합 표 이력 기록.)

§2 직후 footnote 추가 — Pre-Issue 시나리오의 I/O = spec → Issue Form `user-original` (§1 verbatim source) + `spec_link` 필드 (path/URL traceability). §3 row 2 의 in-lane I/O 와 다름.

### D6. Effective date = Phase 2 wrapper PR merge timestamp

[ADR-031](ADR-031-lane-spawn-evidence-trail.md) §14 freeze 패턴 재사용. Effective date 이전 Phase 1 PR open 된 모든 Story = grandfather (retroactive 미적용).

## 결과

- 9 file 변경 (3 신규 + 6 수정), wrapper-only (lane plugin sibling sync 없음).
- Phase 1 PR (this PR): ADR-034 Proposed + 4 doc edits (orchestrator-playbook §1.2.0 INSERT + consumer-guide §2.0a APPEND + superpowers-integration §2 row + brainstorming-path-override sub-section).
- Phase 2 PR: ADR-034 Accepted + story.yml `spec_link` field + CLAUDE.md 1 line annotation + Story §8-§11 internal-docs append.
- Risk-low: additive only, regression 0.
- Migration: 없음.

## 거절된 대안

- D1 (B) 복잡도 임계 위 mandatory: 임계 정의 모호 (cross-cutting / 새 도메인 / 모호한 scope = RequirementsPL 가 lane 내부에서 판단 가능, pre-Issue 강제 ROI 낮음). CI 강제 = 옵션 정책 위배.
- D1 (C) 모든 Story mandatory: 작은 chore (typo fix / link repair) 도 Stage 0 강제 → 과도. in-lane brainstorming 으로 충분.
- D4 (별도 fragment 신설): ADR-028 §결정 5 의 wrapper-owned fragment 4 개 고정 정책 위배. 1 fragment 안 sub-section 분리가 더 간결.
- spec_link auto-fetch (RequirementsPL 가 link fetch): SSRF 위험 — 단순 traceability metadata 유지.

## 관련 ADR

- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — codeforge family dogfood-out policy. spec / plan / change-plan / story / retro 위치 internal-docs override.
- [ADR-017](ADR-017-skill-override-path-enforcement.md) — skill override path enforcement. `docs/superpowers/{specs,plans}/**` plugin repo 금지 + CI fail-closed.
- [ADR-027](ADR-027-consumer-adoption-protocol.md) + [ADR-032 Amendment 1](ADR-032-adr-027-amendment-1-hard-enforcement.md) — consumer adoption + ADR Proposed → Accepted 2-stage 패턴.
- [ADR-028](ADR-028-superpowers-integration-policy.md) — superpowers integration SSOT, wrapper-owned fragment 4 개 고정. (ADR-122 로 Superseded — superpowers 의존 제거)
- [ADR-031](ADR-031-lane-spawn-evidence-trail.md) — lane spawn evidence trail + effective date freeze 패턴.
- [ADR-122](ADR-122-superpowers-dependency-removal.md) — superpowers 의존 완전 제거 (§결정 7: 본 ADR-034 fallback 문구 제거 — Amendment 3). Stage 0 brainstorming 핵심 정책은 보존, superpowers 매개체만 `codeforge:brainstorm` 자립으로 치환.

## 해소 기준

N/A — permanent policy

## 관련 파일

Phase 1 wrapper PR (이 PR):
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §1.2.0 Stage 0 블록 INSERT
- [`docs/consumer-guide.md`](../consumer-guide.md) — §2.0a "Optional Stage 0" APPEND
- [`docs/superpowers-integration.md`](../superpowers-integration.md) — §2 표 1 row + footnote (24 호출 지점)
- [`templates/skill-prompt-helpers/brainstorming-path-override.md`](../../templates/skill-prompt-helpers/brainstorming-path-override.md) — "Pre-Issue scenario" sub-section APPEND

Phase 2 wrapper PR (후속):
- [`templates/github-issue-forms/story.yml`](../../templates/github-issue-forms/story.yml) — optional `spec_link` textarea field 추가
- [`CLAUDE.md`](../../CLAUDE.md) — Stage 0 1 line annotation
- 본 ADR-034 — status Proposed → Accepted

internal-docs (별도 repo, mclayer/codeforge-internal-docs):
- `wrapper/specs/2026-05-07-cfp-129-pre-issue-brainstorming-design.md` — brainstorming spec
- `wrapper/plans/2026-05-07-cfp-129-pre-issue-brainstorming-plan.md` — implementation plan
- `wrapper/change-plans/cfp-129-pre-issue-brainstorming.md` — Change Plan §1-§11
- `wrapper/stories/CFP-129.md` — Story §1-§7 (Phase 1) + §8-§11 (Phase 2 append)
- `wrapper/decisions/CFP-129-001-codex-spec-review.yaml` — Codex 7-area review verdict archive

## Amendment 1 — codeforge:brainstorm 통합 (CFP-345, 2026-05-09)

### 컨텍스트

기존 Stage 0는 외부 plugin brainstorming skill 단독 호출 (Orchestrator 단일 에이전트).
Requirements 에이전트(DomainAgent, ResearcherAgent, RequirementsAnalystAgent, PMOAgent)의
전문성이 brainstorming 단계에 투입되지 않아 scope 정의 품질이 낮고 downstream 충돌 확률이 높다.

또한 brainstorming 결과가 scope_manifest(ADR-050 §결정 2)로 연결되지 않아
병렬 에픽 충돌 조율 정보가 누락된다.

### 변경

| 항목 | 기존 (ADR-034 v1) | Amendment 1 이후 |
|---|---|---|
| Stage 0 스킬 | 외부 plugin brainstorming skill | codeforge 프로젝트 = `codeforge:brainstorm` (권장) |
| 하위호환 | — | (Amendment 3 / ADR-122: 외부 plugin 없이 `codeforge:brainstorm` 자립 — superpowers fallback 대상 소멸) |
| 에이전트 참여 | Orchestrator 단독 | Phase 0: 4 에이전트 병렬 컨텍스트 제공 (opt-in) |
| 출력 | spec 파일 | spec 파일 + scope_manifest 초안 |

### 적용 조건

- codeforge 프로젝트 (`.claude/_overlay/project.yaml` 존재) 또는 dogfood (`docs/adr/` 디렉터리 존재)
- Orchestrator가 brainstorming을 시작할 때 `codeforge:brainstorm` 스킬 호출
- Phase 0는 사용자 opt-in (ResearcherAgent Opus 비용 제어)

### 만료 / supersede

Amendment 2 (CFP-386) 가 Phase 0 opt-in 결정을 자동 실행으로 변경 — Amendment 1 의 "Phase 0 는 사용자 opt-in" 항목은 Amendment 2 발효일 (2026-05-11) 이후 invalid.

## Amendment 2 — Phase 0 자동 실행 (CFP-386, 2026-05-11)

### 컨텍스트

Amendment 1 (CFP-345) 는 ResearcherAgent Opus tier 비용 제어를 위해 Phase 0 opt-in 확인 절차를 `skills/codeforge-brainstorm/SKILL.md` 17-25 줄에 명시 — 매 brainstorm 호출 시 "Phase 0 을 실행할까요?" `AskUserQuestion` 발생.

사용자 directive (2026-05-11 KST conversation, claude-opus-4-7 wrapper session):

> 이러한 입력을 포함한 쓸모없는 userstopp 이 없어야 한다. 플러그인의 생산성을 극도로 저하시킨다.

### 문제

1. **반복 비용 경고 = 학습된 reflex**: 매 호출마다 동일 질문 반복 → 의미 있는 결정 없이 클릭만 수행. AskUserQuestion 의 신호 가치 소실.
2. **호출 시점에 이미 비용 의사 표명됨**: brainstorming 자체가 비-trivial Story 권장 절차. `codeforge:brainstorm` skill 호출 = 비용 발생 동의 = 추가 확인 불필요.
3. **cost-out 경로 이미 존재**: 비용 절감을 원하는 사용자는 `codeforge:brainstorm` 의 Phase 0 (4 에이전트 병렬 spawn) 를 skip 가능. 자동 실행해도 사용자 제어 보존. (Amendment 3 / ADR-122: 구 superpowers fallback 경로는 의존 제거로 소멸 — cost-out 은 Phase 0 skip 으로만 제공.)
4. **CFP-358 / CFP-374 패턴 정합**: Subagent-Driven 자동 선택 (구현 실행 방식 프롬프트 skip) 과 동일 원칙 — "비용 경고가 생산성을 저하시키는 경우 사용자 선택이 아닌 정책으로 처리".

### 변경

| 항목 | Amendment 1 (기존) | Amendment 2 이후 |
|---|---|---|
| Phase 0 진입 | opt-in 확인 후 진입 | 자동 진입 (별도 사용자 확인 없음) |
| AskUserQuestion | 매 호출당 1회 | 0회 |
| 사용자 cost-out 경로 | Phase 0 거절 → 외부 plugin brainstorming fallback | `codeforge:brainstorm` Phase 0 skip (Amendment 3 / ADR-122: 외부 plugin fallback 대상 소멸 — cost-out = Phase 0 skip only) |
| 비용 통지 | 매 호출 inline 경고 | SKILL.md 본문 + ADR-042 의 model tier 정책 SSOT 참조 |

### 적용 조건

- `codeforge:brainstorm` skill 발동 시 즉시 Phase 0 (4 에이전트 병렬 spawn) 진행
- Phase 0 결과를 Phase 1 (강화된 brainstorming 대화) 초기 컨텍스트로 주입
- Phase 0 의 4 에이전트 결과 합성 후 `codeforge:brainstorm` 의 내재 brainstorming checklist 로 진행 (Amendment 3 / ADR-122: 구 superpowers checklist 는 codeforge:brainstorm 본문으로 내재화)

### 사용자 제어 보존

비용 절감을 원하는 사용자는:
- `codeforge:brainstorm` 의 Phase 0 (4 에이전트 병렬 spawn) 를 skip → 강화된 brainstorming 대화만 진행
- 이 cost-out 경로는 SKILL.md 본문에서 명시 (Amendment 3 / ADR-122: 구 superpowers fallback 광고는 의존 제거로 폐기 — Phase 0 skip 이 유일 cost-out)

### 변경 파일

- `skills/codeforge-brainstorm/SKILL.md` — "Phase 0 opt-in 확인" 섹션 (17-25 줄) 제거 + 자동 실행 명시
- `docs/adr/ADR-034-pre-issue-brainstorming-stage.md` — 본 Amendment 2 (frontmatter `amendments[]` + 본문 추가)
- `CLAUDE.md` — Stage 0 annotation 정합 갱신 (`(opt-in Phase 0)` → `(자동 Phase 0)`)

### 만료 / supersede

별도 superseding amendment 없는 한 영구.

## Amendment 3 — superpowers fallback 문구 제거 (CFP-2249 / ADR-122, 2026-06-15)

### 컨텍스트

[ADR-122](ADR-122-superpowers-dependency-removal.md) 가 codeforge family 의 superpowers 의존을 완전 제거했다 (brainstorming/writing-plans 를 `codeforge:brainstorm` / `codeforge:writing-plans` 자립 skill 로 내재화). 본 ADR-034 의 Stage 0 정책은 Amendment 1·2 를 거치며 `codeforge:brainstorm` 을 권장 경로로 채택했으나, **하위호환 / cost-out 경로로 외부 plugin brainstorming skill 직접 호출을 fallback 으로 광고**하는 문구가 본문 9 지점에 잔존했다 (line 99/158/169/170/198/207/214/219/220). superpowers 의존이 제거된 상태에서 이 fallback 광고는 존재하지 않는 외부 경로를 활성 경로로 안내 → ADR-122 §결정 2 (codeforge 자립) 직접 모순.

### 결정

ADR-122 §결정 7 에 따라 본 ADR-034 의 superpowers fallback 문구를 제거한다.

- **하위호환 / cost-out 경로** (line 170/198/207/219/220): 외부 plugin brainstorming skill 직접 호출 fallback 광고 제거 → cost-out = `codeforge:brainstorm` 의 Phase 0 (4 에이전트 병렬 spawn) skip 으로만 기술. 외부 plugin fallback 대상 소멸.
- **checklist 참조** (line 214): 구 superpowers checklist 참조 → `codeforge:brainstorm` 내재 brainstorming checklist 로 치환 (ADR-122 가 brainstorming 을 SKILL.md 본문에 내재화).
- **이력 서술** (line 99/158/169): Amendment 1 변천 이력 / §컨텍스트 평문의 superpowers 어구 → "외부 plugin (일반)" 으로 wording 정규화 (ADR-064 §결정 10 cleanup 동형 — referent 소멸).

### 보존 (무손상)

Stage 0 (pre-Issue brainstorming) 핵심 정책 본체 — 옵션 정책 / Phase 0 자동 실행 (Amendment 2) / spec → Issue Form `user-original` + `spec_link` I/O / effective date freeze (D6) — 전부 무손상. superpowers 라는 **매개체**만 codeforge 자립 skill 로 치환했을 뿐 brainstorming Stage 0 결정 자체는 불변.

### 만료 / supersede

별도 superseding amendment 없는 한 영구.
