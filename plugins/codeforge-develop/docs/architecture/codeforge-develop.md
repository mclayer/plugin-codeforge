---
title: codeforge-develop lane 구조 (구현 레인 — TDD 구현 + QA)
last_captured: 2026-07-24
captured_at_sha: 14ac6b9b3  # D7 provenance — 검증 시점 코드 commit anchor (CFP-2813 §3.4)
last_update_cfp: CFP-2813  # stale 해소 실갱신 — model tier 실측 반영(ADR-141: DeveloperPL fable / Developer opus / QADev·DataEng·InfraEng haiku Amd1) + doc-only fast-path(ADR-054) 폐지 정정(ADR-127 §결정 1/2 — 모든 변경 full 8 lane + 2 PR) + develop_output wrapper 단일 원본(ADR-118 D5) + ADR-166 read protocol G3 관점 + 본 doc = living-architecture-update per-PR 게이트 대상(ADR-078 Amd3/ADR-112 Amd1)
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = codeforge-develop lane plugin self-owned seed (CFP-970 / Sub-Epic CFP-949 / Epic CFP-756 / ADR-078).
     누적 현재 상태 SSOT. Story key 독립 (고정 경로). 델타 = Change Plan SSOT.
     family 전체 구조 = wrapper repo 의 codeforge-family.md SSOT (family_ref 참조). -->

## 모듈

`[verified: lane plugin CLAUDE.md @ 37350384 "Role:dev roster 동적 discovery" + "Self-write 책임"]` — codeforge-develop = 구현 레인 plugin. **5 core agent + preset/overlay 동적 `role:dev` roster** 로 구성.

| 모듈 (agent) | tier (model — agents/*.md frontmatter 실측 @ 14ac6b9b3, ADR-141) | 책임 |
|---|---|---|
| **DeveloperPLAgent** | PL — fable (ADR-141 Amd4 apex) | 구현 레인 통솔 — `role:dev` 매칭 worker 병렬 spawn / FIX 1차 진단 / Story §8 self-write / Phase 2 PR 발의 |
| **QADeveloperAgent** | Worker — haiku (ADR-141 Amd1 기계 워커) | 테스트 코드 author + CI 워크플로 author/갱신 (CFP-317 / ADR-048) — `.github/workflows/test.yml` + performance baseline |
| **DeveloperAgent** | Worker (role:dev) — opus | 일반 구현 worker — TDD red→green 수행 |
| **DataEngineerAgent** | Worker (role:dev) — haiku | 데이터 계층 worker — schema / migration / pipeline 구현 |
| **InfraEngineerAgent** | Worker (role:dev) — haiku | 인프라 계층 worker — IaC / CI / container 구현 |

**preset/overlay 동적 roster** (consumer overlay 영역) — DeveloperPLAgent 가 spawn 시점에 frontmatter `role: dev` 매칭으로 discovery:

- 본 plugin `agents/*` (3 core + QADev — 위 표)
- `presets/<active>/agents/*` (preset 활성 시 확장 worker)
- consumer overlay `.claude/_overlay/agents/*` (consumer project 자체 worker 정의)

> roster source 3종 = lane plugin CLAUDE.md "Role:dev roster 동적 discovery" SSOT. 본 표 = composition map 수준 (라인 수준 0건). agent 별 모델 tier / 상세 동작은 lane plugin `agents/*.md` SSOT.

## 경계

**Self-write 영역** (`[verified: lane plugin CLAUDE.md @ 37350384 "Self-write 책임" 표]` — `codeforge:lane-self-write-boundary` SSOT 정합):

| Path | 책임 agent |
|---|---|
| Story `§8` (구현 commit log) | DeveloperPLAgent |
| Story `§8.5` (QA / 통합 검증 evidence) | DeveloperPLAgent |
| Phase 2 PR (구현 산출물 PR) | DeveloperPLAgent |
| GitHub comment `[구현]` prefix | DeveloperPLAgent |
| phase label transition (`phase:구현` → `phase:구현-리뷰`) | DeveloperPLAgent |

**Phase 2 PR producer 패턴** (ADR-024 Story-scoped branch):

- 1 Story = 2 PRs (Phase 1 = 요구/설계 doc, Phase 2 = 구현 commit). 본 lane = **Phase 2 producer** (선행 Phase 1 merge 의무).
- branch convention `cfp-NNN[-<slug>]` (main 직접 push 금지, ADR-024 §결정 1).
- ~~doc-only fast-path (ADR-054) 1 PR~~ — **폐지** (ADR-127 §결정 1/2: 문서-only 단일 PR·chore 면제 폐지, 모든 변경 = 정식 full 8 lane + Phase 1/2 PR 분리 무조건).

**worktree-first normative** (ADR-040 Amendment 6, 4 blocking-on-pr evidence-check):

- lane spawn / ad-hoc 구분 없이 모든 coding work = isolated worktree (`${HOME}/.claude/worktrees/<repo>/<branch-flat>`) 안에서 수행.
- `git -C <worktree_abs_path>` 강제 directive — harness cwd reset gap 차단.
- `BYPASS_WORKTREE_FIRST=1` 외 main 직접 편집 금지.

**`role:dev` 동적 roster boundary** — consumer preset/overlay 확장 영역. wrapper / lane plugin 정책은 축소 불가 (`.claude/_overlay/` = 확장만 허용).

**FIX 루프 경계** (ADR-035 정합):

- 구현 리뷰 / 구현 테스트 / 보안 테스트 FAIL 시 — **DeveloperPL 1차 진단** (failure local? boundary?) → **ArchitectPLAgent 최종 판정** (설계 원인 vs 구현 원인).
- 구현 원인 = Phase 2 PR commit append. 설계 원인 = Change Plan 갱신 + Phase 1 follow-up PR (ArchitectAgent re-spawn).
- decision table SSOT = `codeforge:root-cause-decision` skill.

**Scope partition**:

- dogfood artifacts (specs/plans/retros/stories/change-plans) = `mclayer/codeforge-internal-docs` monorepo SSOT (ADR-013). 본 plugin 폴더 = `codeforge-internal-docs/codeforge-develop/`.
- 본 plugin repo = runtime SSOT 만 (agents/* + presets/* + scripts/ + workflows/).

## 인터페이스 계약

`[verified: lane plugin CLAUDE.md @ 37350384 "Inter-plugin contracts" 단락]` — 본 lane = 1 producer + N consumer.

**producer**:

| contract | 위치 | 용도 |
|---|---|---|
| `develop_output` | `docs/inter-plugin-contracts/develop-output-v1.md` (**wrapper 단일 원본 — ADR-118 D5**, sibling sync 폐지) | 구현 산출물 핸드오프 packet (Phase 2 PR ↔ CodeReview lane) |

**consumer** (lane 외 contract 수신):

| contract | producer plugin | 용도 |
|---|---|---|
| `design_output` | codeforge-design | Change Plan + §8 Test Contract 입력 |
| `review_verdict` | codeforge-review | CodeReview / SecurityTest lane verdict (FIX 트리거) |
| `fix-event-v1` (chain) | wrapper (Orchestrator monopoly) | §10 FIX Ledger append event |

**skill anchor** (lane 진입 / FIX 루프 진입 시 호출):

- `codeforge:fix-ledger-schema` — §10 FIX Ledger 스키마 + RESET 룰 + max FIX 카운터 SSOT (FIX 루프 진입 시).
- `codeforge:root-cause-decision` — failure 유형별 1차 가정 + escalate 조건 SSOT (DeveloperPL 진단 전).

**설계 정보 소비 (ADR-166 design-info read protocol, CFP-2813)**: 본 lane 구성원 (Developer/QADev 계열) = **G3 (델타·근거 소비자)** — change_plan/§8 Test Contract 가 1차 입력, Living Architecture 는 on-demand 보조 (mandatory 선행 read 대상 아님). 본 doc 자신 = `living-architecture-update` per-PR 게이트 대상 (`plugins/codeforge-develop/**` 변경 PR = 본 doc 갱신 OR `[living-arch-no-impact]` declare — ADR-078 Amd3/ADR-112 Amd1).

**Phase 2 PR (artifact 계약)**:

- branch convention `cfp-NNN[-<slug>]` (ADR-024).
- description block 의무: `## Lane evidence` (Story §14 mirror, ADR-031 / CFP-126).
- `phase:구현-리뷰` 라벨 + Related Issue `#<KEY>` cross-ref.

> 계약 schema field-level 상세 = 각 contract file SSOT + wrapper repo `MANIFEST.yaml`. version 값은 MANIFEST.yaml SSOT 가 권위 (본 doc version literal 미박제 — drift 회피).

## 데이터 흐름

**Story-level lane spawn 흐름** (본 lane 의 input → transform → output):

```
[설계 lane 완료]
  → design_output 수신 (Change Plan §3-§7 + §8 Test Contract)
  → Orchestrator 가 DeveloperPLAgent spawn (lane plugin PL 1개, non-skippable)
    → DeveloperPL = role:dev worker discovery (본 plugin agents/* + presets/* + consumer overlay)
    → DeveloperPL = parallel role:dev spawn (의존성 없는 한 모두 한 메시지)
      → role:dev worker = TDD red 우선 (test fixture author) → green (implementation author)
      → QADeveloperAgent = 테스트 코드 + CI 워크플로 (test.yml + perf baseline) author
    → DeveloperPL = Phase 2 PR 발의 (Story §8 self-write commit append)
  → CodeReview lane 핸드오프 (review_verdict consumer)
  → [FIX 트리거 시] DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (ADR-035)
    → 구현 원인 = Phase 2 PR commit append
    → 설계 원인 = ArchitectAgent re-spawn (Change Plan 갱신)
```

**artifact propagation**:

- Story file (`internal-docs/codeforge-develop/stories/<KEY>.md`) = lane 컨텍스트 SSOT (Orchestrator fetch + lane self-fetch). 본 lane self-write = §8 / §8.5.
- Phase 2 PR = 구현 commit append target (Story-scoped branch, ADR-024).
- `develop_output` packet = CodeReview lane 핸드오프 carrier (review-verdict 매칭).
- `fix-event-v1` chain = Orchestrator §10 FIX Ledger monopoly append (FIX 루프 진입 시).

**FIX 루프 데이터 흐름** (max FIX 3/3, ADR-067):

- review_verdict `pl_recommendation: FIX` 수신 → Orchestrator §10 FIX Ledger row append → DeveloperPL re-spawn (1차 진단).
- DeveloperPL 진단 packet → ArchitectPLAgent 최종 판정 (cross-lane).
- max 3 도달 시 = ArchitectPL implementability reassessment (ADR-067 §결정 3) — RESET / escalate / Pause 분기.

> 본 흐름 = lane spawn / event / artifact propagation 수준 (anti-scope guard 준수). 함수 호출 trace / 변수 전달 라인 0건.

### ADR-076 declarative reconciliation 3-layer cross-ref

ADR-076 (declarative reconciliation upgrade flow) 의 3-layer 패턴 (desired state / current state / preserved customization marker) 답습 — 본 lane 의 self-write 영역 (§8 / §8.5 / Phase 2 PR) 은 **current state layer** 에 해당 (Story 진행 시점의 누적 commit log + QA evidence). desired state = Change Plan §3-§7 (설계 lane 산출물). preserved customization = consumer overlay `role:dev` roster (축소 불가, 확장만 허용). 본 architecture_doc = 누적 현재 상태 SSOT (델타 = Change Plan SSOT — disjoint 상보, ADR-078 §결정 3).

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `src/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
