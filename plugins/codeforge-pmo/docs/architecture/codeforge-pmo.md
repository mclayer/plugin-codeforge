---
title: codeforge-pmo lane 구조 (Cross-cutting — Epic 창설 / Story 회고 / Git ops)
last_captured: 2026-07-24
captured_at_sha: 14ac6b9b3  # D7 provenance — 검증 시점 코드 commit anchor (CFP-2813 §3.4)
last_update_cfp: CFP-2813  # stale 해소 실갱신 — model tier 실측(ADR-141: PMOAgent fable Amd4 / GitOpsAgent sonnet) + 계약 wrapper 단일 원본(ADR-118 D5 — 구 ADR-010 canonical/mirror supersede) + 본 doc write = ArchitectAgent monopoly 정정(INV-3, doc-locations owner_agent) + per-PR 현행화 게이트(ADR-078 Amd3/ADR-112 Amd1) + ADR-166 read protocol G4 관점(PMOAgent = write 주체, mandatory read 대상 아님)
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = lane plugin self-owned seed (CFP-973 / Sub-Epic CFP-949 Wave 2, parent Epic CFP-756 / ADR-078).
     누적 현재 상태 SSOT — Story key 독립, 고정 경로. 델타는 Change Plan SSOT (disjoint, ADR-078 §결정 3).
     family-level structure = family_ref (wrapper repo seed) 참조. 본 doc 은 lane internal 구조만 채운다. -->

## 모듈

codeforge-pmo = **Cross-cutting** lane plugin. 단일 Story lane 게이트에 비개입하면서 Epic 분해 보조 / Story 완료 회고 감사 / Cross-Story 패턴 분석 / git operations orchestration 책임을 가로지른다. `[verified: lane plugin CLAUDE.md @ cfp-2236 GitOpsAgent 단락 + agents/ tree direct enumeration: PMOAgent.md + GitOpsAgent.md]` — 2 sibling agent (책임 영역 disjoint):

| 모듈 (agent) | 라이프사이클 (model — frontmatter 실측 @ 14ac6b9b3, ADR-141) | 입장 / 책임 |
|---|---|---|
| **PMOAgent** | one-shot trigger-driven (Epic 창설 / Story 완료 회고 자동 trigger / retro batch closure — follow-up 3+ / 사용자 ad-hoc) — **fable** (ADR-141 Amd4 apex) | Epic 분해 보조 + Story 완료 회고 감사 + Cross-Story 패턴 분석 + 게이트 준수 감사 + ESCALATE 트렌드 축적 → ADR 후보 발의 (`pmo_output v1.adr_proposal` field) + retro batch closure (ADR-045 §D-11) |
| **GitOpsAgent** | long-running teammate (Story 전 기간 active) — **sonnet** (ADR-141 Amd2 carve-out) | Hierarchical branch tree + Worktree lifecycle (`.claude-work/worktree-manifest.yaml`) + Sequential merge orchestration + FIX iteration 재구성 + Stale worktree cleanup + Cross-platform path handling. Orchestrator + 모든 lane PL 의 git 작업 단일 위임 대상 |

> 2 agent 간 직접 sub-agent spawn 불가 — Orchestrator 경유 (codeforge family ADR-009 invariant). GitOpsAgent ↔ PMOAgent 는 sibling (책임 disjoint, 회고 영역 vs git 영역).
>
> **DialogFidelityAgent sunset (CFP-2236, 2026-06-14)**: 구 3번째 sibling (one-shot read-only dialog fidelity verifier, 3-anchor: `post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause`) 는 전면 폐지. agent count 3→2. dialog turn 검증 ground = 동일 anchor 의 Codex TP#2/TP#3 (mandatory P0/P1 inline FIX) + ADR-064 §결정 9 Q-3check (Orchestrator self-check) 가 보존. 폐지 박제 = ADR-071 Amendment 9 (carrier-preserved).

## 경계

**Lane self-write boundary** `[verified: CLAUDE.md @ c0f26435 Self-write 책임 표]`:

| 경계 영역 | owner agent |
|---|---|
| `docs/retros/<sprint>.md` (story_completion 자동 + cross_story_audit_request) | PMOAgent (direct write, CFP-26 Phase 0a) |
| Story `<KEY>.md §11` (회고 블록 4 field schema: retro_file / retro_summary / learnings_count / feedback_back_to_codeforge — CFP-138 / ADR-045 D-5) | PMOAgent |
| `gate:retro-complete` label add (retro write 완료 후 forcing function) | PMOAgent (`mcp__github__issue_write`) |
| Epic GitHub milestone description 갱신 | PMOAgent (`gh api repos/*/milestones*`) |
| GitHub comment `[PMO]` prefix | PMOAgent (`mcp__github__add_issue_comment`) |
| `.claude-work/worktree-manifest.yaml` (TeamCreate / TeamDelete / FIX iteration / stale cleanup) | GitOpsAgent (direct write) |
| Story `<KEY>.md §10.5 Git Ops Log` (매 git ops event, append-only) | GitOpsAgent |
| GitHub comment `[GitOps]` prefix (conflict / escalation) | GitOpsAgent |
| `docs/architecture/<path>.md` (본 doc 영역) | **ArchitectAgent write monopoly** (INV-3 — doc-locations `owner_agent: codeforge-design:ArchitectAgent` + parallel-edit locked. per-PR 현행화: `plugins/codeforge-pmo/**` 변경 PR = 본 doc 본문 갱신 OR `[living-arch-no-impact]` declare closed-binary — ADR-078 Amd3 / ADR-112 Amd1 / CFP-2813. PMOAgent = F8 divergence 수신·retro 감사 축이지 arch doc write 주체 아님) |

**Cross-cutting boundary (Story lane 게이트 비개입)**:
- 단일 Story lane gate (Phase 1/2 PR merge-mergeable / FIX root cause / 설계 결정 / 구현 / 보안 테스트) 영역 deny — PMOAgent / GitOpsAgent 어떤 agent 도 lane 진행 결정 비참여
- ESCALATE 트렌드 축적 → ADR 후보 발의 (`pmo_output v1.cross_story_pattern_adr_trigger` + `adr_proposal` field 동시 채움, status: Proposed inline ADR draft) — **Mandatory framing** (CFP-665 / ADR-045 Amendment 5 §D-9, pattern_count ≥ 2 forcing function, PMOAgent self-decide 영역 제거)

**Parallel epic coordination boundary** (ADR-050):
- `docs/parallel-work/section-ownership.yaml` = 동시 수정 시 `merge-order` 의무 정책 SSOT (PMOAgent / GitOpsAgent 가 cross-Epic scope_manifest intersection 검사 시 참조)
- Epic Issue body `<!-- scope_manifest -->` 블록 = PMOAgent self-write 영역 (Phase 1 시작 시) — `planned_adrs` / `planned_files` / `planned_claude_md_sections` / `planned_inter_plugin_contracts[]` / `planned_label_registry_bumps[]` / `cross_section_conflict_detection: true`

**Disjoint scope** (ADR-078 §결정 3):
- 본 doc (architecture_doc) = lane internal 누적 현재 상태, Story key 독립
- Change Plan = Story별 변경 델타, Story key 종속, 1회 작성
- ADR = 단일 결정 단위 (결정 시점 고정 — 개정=supersede / 의미보존 위생편집 채널; ADR-058 §결정10)
- 본 doc ↔ Change Plan = 상보 disjoint (구조 vs 델타)

**verify-before-trust 4-layer 안전망 안의 본 lane 위치** (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D-9):
- ADR-045 §D-9 (PMOAgent retro corpus enumeration cross-Story pattern_count ≥ threshold 2 검출 시 ADR escalation **forcing function**) = 본 lane 의 4-layer 마지막 layer 주관
- 다른 3 layer (ADR-073 Orchestrator verify-before-assert / ADR-070 Codex verify-before-trust / ADR-082 write-time self-write verification) = 본 lane 의 owner 아님 (Orchestrator / 외부 worker / internal lane agent 각각 disjoint)

## 인터페이스 계약

본 lane 의 인터페이스 surface = `docs/inter-plugin-contracts/` (**wrapper 단일 원본 — ADR-118 D5, sibling sync 폐지**. 구 ADR-010 canonical/mirror 체계 supersede):

**설계 정보 소비 (ADR-166 design-info read protocol, CFP-2813)**: PMOAgent = **G4 (write 주체 — mandatory read 대상 아님)**: 회고·패턴 분석 입력 = retro corpus + Story file 이지 설계 현재상태 재구성 아님 (F8 divergence 수신 mandate 는 별개 채널). GitOpsAgent = 대상 아님 (git 기계 작업).

**Producer 계약 (kind:contract)** — 본 lane 이 생성:

| contract | producer agent | 용도 | SSOT pointer |
|---|---|---|---|
| `pmo_output` | PMOAgent | Cross-cutting 산출물 핸드오프 (retro_summary / learnings / cross_story_pattern_adr_trigger / adr_proposal) | `docs/inter-plugin-contracts/pmo-output-v1.md` (**wrapper 단일 원본 — ADR-118 D5**) |
| `git_ops_event` | GitOpsAgent | git operations event log (TeamCreate / TeamDelete / merge / cleanup / FIX iteration 재구성). fix-event-v1 chain 연동 | `docs/inter-plugin-contracts/` (MANIFEST.yaml SSOT) |

**Host 계약 (kind:registry — wrapper 단일 원본, ADR-118 D5)** — 본 lane 이 발동 / 참여:

| contract | 본 lane 역할 |
|---|---|
| `fix-event-v1` | `git_ops_event` chain 연동 carrier — FIX iteration 재구성 시 GitOpsAgent 가 `git_ops_event` row append, Orchestrator §10 FIX Ledger append 와 chain join |
| `evidence-check-registry-v1` | `retro-mandatory.yml` workflow / `retro-alert-pickup-kpi.yml` warning-tier lint entry host (CFP-628 / ADR-045 §D-5) — PMOAgent 의 forcing function mechanical layer |
| `label-registry-v2` | `gate:retro-complete` label + `hotfix-bypass:retro-*` label family host. PMOAgent self-write 의 forcing function carrier |

**Workflow 계약 (mechanical enforcement)** — 본 lane 활성화 trigger:

| workflow | trigger | 본 lane 호출 |
|---|---|---|
| `retro-mandatory.yml` (wrapper template) | Phase 2 PR merge 후 5분 grace + 4 attempt retry policy (1 initial + 3 retries, total max latency = 35min) | PMOAgent 자동 spawn (CFP-138 / ADR-045 forcing function). retro write + Story §11 fill + `gate:retro-complete` label + `[PMO]` comment |
| `parallel-epic-conflict-check.yml` | Epic body scope_manifest 변경 시 | PMOAgent (Open epic 교집합 + cross-section 검사) → `conflict:{contract-overlap,registry-bump-overlap}` 라벨 + `merge-order` 자동 부여 |
| `retro-alert-pickup-kpi.yml` (CFP-628 / ADR-045 §D-5) | SessionStart hook scan + cron pickup | Orchestrator 가 미해소 `[PMO] retro alert` comment 감지 시 PMOAgent 자동 spawn |

> 계약 schema field-level 상세 + version 값 = 각 contract file SSOT + MANIFEST.yaml. 본 섹션 = surface enumeration (계약 이름 + producer agent + SSOT pointer, version literal 미박제 — version drift 회피).
>
> **DialogFidelityAgent verifier surface sunset (CFP-2236, 2026-06-14)**: 구 DialogFidelityAgent 3-anchor read-only verifier surface (declaration-only, contract field 신설 0) 는 agent 폐지와 함께 제거. dialog turn 검증 ground = Codex TP#2/TP#3 + ADR-064 Q-3check 보존. 폐지 박제 = ADR-071 Amendment 9.

## 데이터 흐름

**Cross-cutting trigger → 산출물 flow** (Orchestrator 가 트리거별로 본 lane agent 1개 spawn — Story lane 게이트 비개입):

```
[trigger 1: Epic 창설] 사용자 요구 (Issue Form / 직접 발화)
  ↓
PMOAgent spawn (Orchestrator)
  ├─ Epic body + scope_manifest 작성 (planned_adrs / planned_files / planned_claude_md_sections / planned_inter_plugin_contracts[] / planned_label_registry_bumps[] / cross_section_conflict_detection: true)
  ├─ Epic GitHub milestone create
  ├─ Story 분해 자문 (단, lane 결정 비개입)
  └─ `[PMO]` prefix comment
  ↓
GitOpsAgent (long-running teammate, 활성 진입)
  ├─ Hierarchical branch tree 설계
  ├─ Worktree 생성 (`.claude-work/worktree-manifest.yaml` row append)
  ├─ `git_ops_event` row append (Story §10.5)
  └─ Story / Sub-Epic lane spawn 흐름 시작

[trigger 2: Phase 2 PR merge 자동] retro-mandatory.yml workflow (CFP-138 / ADR-045)
  · cumulative offset from PR merge timestamp:
  · First attempt = +5min (grace period)
  · Retry 1 = +10min / Retry 2 = +20min / Retry 3 = +35min (final)
  · ESCALATE = +35min 후 (4 attempts 모두 fail)
  ↓
PMOAgent spawn (Orchestrator)
  ├─ `docs/retros/<sprint>-cfp-NNN-<slug>.md` 신규 생성 (templates/retro.md schema 정합)
  ├─ Story §11 회고 블록 4 field schema fill (retro_file / retro_summary / learnings_count / feedback_back_to_codeforge)
  ├─ Epic milestone description 갱신
  ├─ `gate:retro-complete` label add (forcing function 핵심 단계)
  └─ `[PMO]` prefix comment
  ↓
[cross-Story pattern 분석 — 매 retro write 시점]
  · patterns_observed[] enumeration (FIX 반복 / ESCALATE 트렌드 / 성능 회귀 / 코드 핫스팟)
  · ADR-082 scope (a) corpus-claim-verify 의무 (write-time source direct verify)
  ↓ pattern_count ≥ 2 reach
[trigger 3: cross_story_pattern_adr_trigger forcing function] ADR-045 Amendment 5 §D-9 (Mandatory framing)
  ↓
PMOAgent `pmo_output v1` return:
  ├─ cross_story_pattern_adr_trigger field 채움
  └─ adr_proposal field 동시 채움 (status: Proposed inline ADR draft)
  ↓
Orchestrator forward → codeforge-design lane (ArchitectAgent) spawn → 정식 ADR file write
  · 본 lane 은 ADR file 직접 write 안 함 — 발의만 (CLAUDE.md `Self-write 책임` 표 boundary)

[trigger 4: parallel epic conflict] parallel-epic-conflict-check.yml (Epic body 변경 시)
  ↓
PMOAgent (Open epic 교집합 + cross-section 검사)
  ├─ `conflict:{contract-overlap,registry-bump-overlap}` 라벨 부여
  ├─ `merge-order` 자동 부여
  └─ `[PMO]` prefix comment

[trigger 5: SessionStart hook] retro-alert-pickup-kpi.yml (CFP-628 / ADR-045 §D-5)
  ↓
Orchestrator scan: 미해소 `[PMO] retro alert` comment
  ↓
PMOAgent 자동 spawn (forcing function 안전망)

[downstream]
  · pmo_output → Orchestrator (retro_summary / adr_proposal forward to ArchitectAgent)
  · git_ops_event → Story §10.5 + fix-event-v1 chain (FIX iteration 재구성 시)
  · Sub-Epic / Epic close → milestone close (PMOAgent self-write)
```

**FIX iteration 재구성 데이터 흐름** (GitOpsAgent 영역):
- DeveloperPL / 각 lane PL 의 FIX verdict → Orchestrator §10 FIX Ledger append → GitOpsAgent `git_ops_event` row append (Story §10.5) → fix-event-v1 chain join (debate_artifact_ref 보유 시 transcript 연동)
- branch / worktree / merge / cleanup 실패 시 conflict escalation → `[GitOps]` prefix comment + lane PL sibling SendMessage

**Artifact propagation**:
- Story file (`internal-docs/codeforge-pmo/stories/<KEY>.md`) = lane 컨텍스트 SSOT (PMOAgent / GitOpsAgent self-fetch)
- Retro file (`docs/retros/<sprint>-cfp-NNN-<slug>.md`) = retro_summary SSOT (영속, Story key 독립 sprint 단위)
- Worktree manifest (`.claude-work/worktree-manifest.yaml`) = GitOpsAgent state (long-running teammate active state)
- 본 doc (architecture_doc) = 누적 현재 상태 (영속, Story key 독립) — 매 Cross-cutting 책임 변경 시 4 H2 영역 갱신 의무 (CLAUDE.md `Self-write 책임` 표)

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### ADR-076 declarative reconciliation 3-layer cross-ref

본 lane 의 architecture_doc 운용은 [ADR-076](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-076-declarative-reconciliation-upgrade.md) declarative reconciliation 3-layer 패턴을 도메인 disjoint 로 답습 (ADR-078 §결정 4 명시):

- **desired state** = 본 doc 의 4 H2 closed-enum (모듈 + 경계 + 인터페이스 계약 + 데이터 흐름) 누적 현재 상태 SSOT
- **current state** = lane plugin agent file (`agents/PMOAgent.md` + `agents/GitOpsAgent.md`) + `CLAUDE.md` 의 실제 정의 상태
- **converge** = PMOAgent self-write (매 Cross-cutting 책임 변경 시 4 H2 갱신, CLAUDE.md `Self-write 책임` 표) + design lane verdict gate (DesignReviewPL 가 본 doc drift 검증 — CFP-923 detection class d, architecture-drift lint 후속 carrier)

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `agents/` 또는 `src/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
