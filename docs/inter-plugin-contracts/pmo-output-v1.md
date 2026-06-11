---
kind: contract
contract_version: "1.3"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-pmo (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only core + writer-distributed lane plugins, codeforge wrapper CFP-31)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
  - ADR-045 (Story retro mandatory trigger — Amendment 5 §D-9 Cross-Story pattern ≥ 2 ADR escalation trigger, CFP-665; Amendment 9 §D-10 retro §6 8-tuple verify-before-trust AND gate, CFP-1632)
authors:
  - CFP-36 ζ arc — second lane self-write pattern validation (2026-04-29)
  - CFP-139 — GitOpsAgent worktree_manifest MINOR bump (2026-05-08)
  - CFP-665 — cross_story_pattern_adr_trigger field MINOR bump (2026-05-14)
  - CFP-1632 — retro_section_6_pre_publish_verify field MINOR bump (2026-05-25)
---

# pmo_output v1 — Inter-plugin Contract

`codeforge-pmo` plugin → `codeforge` core (Orchestrator) 단방향 schema. PMOAgent 가 self-write 후 typed output 으로 결과 audit 보고.

**상위 SSOT 위치**: 본 파일이 단일 원본 (canonical) — CFP-2158 / [ADR-118](../../archive/adr/ADR-118-monorepo-consolidation.md) D5 가 lane canonical ↔ wrapper mirror 이중체계를 폐지 (monorepo 통합 S1 후속). frontmatter 의 ADR-010 인용은 historical (sibling sync 정책 Superseded — ADR-010 Amendment 5). versioning 룰 = ADR-008 불변.

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① pmo_packet 작성 (trigger-specific)
        ▼
codeforge-pmo plugin
  └─ PMOAgent
        │
        │ ② Self-write 단계:
        │    - Edit(docs/retros/<sprint>.md) [회고 감사 / Cross-Story 패턴 보고서]
        │    - Edit(docs/stories/<KEY>.md §11) [Story 완료 회고 mirror]
        │    - mcp__github__add_issue_comment ([PMO] prefix)
        │    - gh api repos/*/milestones (Epic milestone 갱신)
        │    - ADR 후보 발의 시: codeforge-design 에 hand-off (verdict.adr_proposal)
        ▼
        │ ③ pmo_output v1 typed output (writes_completed audit + ADR proposal)
        ▼
codeforge core (Orchestrator)
        │
        │ ④ output 처리:
        │    - adr_proposal 존재 → codeforge-design 에 발의 hand-off
        │    - patterns_for_cross_story_audit → 향후 PMO trigger 데이터로 보존
```

## 2. pmo_packet (Orchestrator → PMOAgent)

```yaml
pmo_packet:
  contract_version: "1.0"        # 필수
  trigger:                       # 필수 — enum
    - epic_creation              # Epic 창설 시 1회 (scope 분해 자문)
    - story_completion           # Story 완료 시 (회고 감사)
    - cross_story_audit_request  # 사용자 주기적 요청 (Cross-Story 패턴)
  story_key: <STORY_KEY>         # 선택 — story_completion 시 필수
  epic_milestone: <int>          # 선택 — epic_creation / cross_story_audit 시 필수
  scope_for_audit:               # 선택 — cross_story_audit_request 시
    sprint_period: <str>
    story_keys: [<list>]
```

## 3. pmo_output (PMOAgent → Orchestrator)

```yaml
pmo_output:
  contract_version: "1.3"
  trigger: <packet 동일 enum>
  story_key: <STORY_KEY>          # 필수 (해당 시) — packet과 일치
  epic_milestone: <int>           # 필수 (해당 시) — packet과 일치

  status: COMPLETED | PARTIAL | ESCALATED   # 필수

  # PMOAgent self-write 결과 audit
  writes_completed:
    retro_doc: <bool>             # 필수 — docs/retros/<sprint>.md write 완료
    story_section_11: <bool>      # 필수 — Story §11 retro pointer (story_completion only)
    epic_milestone_progress: <bool>  # 필수 — milestone progress 갱신 (epic 관련 trigger)
    pmo_comment: <bool>           # 필수 — [PMO] prefix GitHub comment 게시

  # ADR 후보 발의 (선택 — 패턴 발견 시)
  adr_proposal:                   # 선택 — null 허용
    title: <string>               # ADR 제목 안
    context: <markdown>           # 발의 근거 (관찰된 cross-Story 패턴)
    status: Proposed              # 항상 Proposed (codeforge-design 에서 Accepted/Rejected 결정)
    target_plugin: codeforge-design (CFP-40 후) | wrapper

  # Cross-Story 감사 결과 (선택)
  patterns_observed:              # 선택 — null 또는 array
    - category: <enum>            # fix-loop-pattern / escalate-trend / performance-regression / hotspot
      summary: <markdown>
      affected_stories: [<list>]
      severity: P0 | P1 | P2

  # GitOpsAgent worktree manifest reference (CFP-139, v1.1 신설 — optional)
  # PMOAgent 가 retro 작성 시 GitOpsAgent 산출물 (.claude-work/worktree-manifest.yaml) 의
  # worktree create / delete / merge / conflict event 를 reference. v1.0 consumer 호환 — 필드 부재 = 미사용.
  worktree_manifest:              # 선택 — null 허용 (v1.1 NEW, additive)
    schema: git-ops-event-v1      # 향후 inter-plugin contract 신설 예정 (CFP-139 follow-up)
    manifest_path: <path>         # 보통 .claude-work/worktree-manifest.yaml
    events:                       # array of git ops events
      - event_type: <enum>        # team-create / team-delete / sequential-merge / conflict-detected / fix-iteration-rebuild / stale-cleanup
        timestamp: ISO8601
        lane: <string>            # 8 lane slug (requirements / design / review / develop / test / deploy / deploy-review / pmo) 또는 cross-cutting
        actor: GitOpsAgent
        worktree_count: <int>     # team-create 시 N
        outcome: success | conflict | aborted
        detail: <markdown>        # short narrative

  # Cross-Story pattern ADR escalation trigger (CFP-665, v1.2 신설 — optional)
  # PMOAgent 가 retro write 시점 patterns_observed[] 검출 직후 threshold check.
  # 누적 ≥ 2 도달 시 본 field mandatory 채움 (Mandatory framing, ADR-045 Amendment 5 §D-9).
  # v1.0 / v1.1 consumer 호환 — 필드 부재 = 미사용 (이전 동작 유지).
  cross_story_pattern_adr_trigger:        # 선택 — null 허용 (v1.2 NEW, additive)
    pattern_count_threshold: 2            # 정수 — fixed (industry lower bound: Google SRE / ITIL / NASA ASRS)
    detected_anchor_id: <string>          # review-verdict-v4 anchor_id stable identifier (primary detection key, strict matching)
    fallback_root_cause_class: <string>   # root_cause_taxonomy class (secondary detection key, loose matching fallback)
    occurrences:                          # array — pattern 검출된 Story 목록 (≥ 2 entry)
      - story_key: <KEY>                  # Story 식별자 (예: CFP-NNN, MCT-NNN)
        finding_ref: <string>             # Story §X.Y 인용 (예: "§10 FIX-2", "§9 Codex P1 F-003")
    escalation_action: adr_draft_emitted  # enum — adr_draft_emitted (정식 ADR draft 작성, default) | escalate_user (PMOAgent trivial 판정 시 사용자 manual decide)

  # Retro §6 ADR draft pre-publish verify (CFP-1632, v1.3 신설 — optional)
  # PMOAgent 가 retro §6 (ADR 후보 발의) 섹션 작성 후 publish 전 8-tuple verify-before-trust AND gate 실행 결과 기록.
  # ADR-045 Amendment 9 §D-10 + Amendment 10 Wave 2 mechanical lint wire 정합.
  # v1.0 / v1.1 / v1.2 consumer 호환 — 필드 부재 = 미사용 (이전 동작 유지).
  retro_section_6_pre_publish_verify:        # 선택 — null 허용 (v1.3 NEW, additive)
    verify_sources_attempted:               # 8 source enum closed-set (ADR-045 Amendment 9 §D-10 정합)
      - source_1_git_show_amendment_log     # git show origin/main 로 amendment_log 존재 verify
      - source_2_grep_evidence_registry     # grep evidence-checks-registry.yaml 로 entry 존재 verify
      - source_3_glob_scripts_check         # Glob scripts/check-*.sh 로 script 존재 verify
      - source_4_gh_pr_list_search          # gh pr list --search 로 관련 PR 존재 verify
      - source_5_gh_issue_list_search       # gh issue list --search 로 관련 Issue 존재 verify
      - source_6_git_log_path               # git log -- <path> 로 커밋 존재 verify
      - source_7_glob_adr_amendment_scan    # Glob docs/adr/ 로 ADR amendment 존재 verify
      - source_8_retro_section_5_pattern_table  # retro §5 Cross-Story 패턴 테이블 확인
    verify_sources_blocked:                 # 선택 — platform exemption 사유 (ADR-052 Amendment 3 정합)
      - gh_cli_rate_limit                   # gh CLI rate-limit 으로 source_4 / source_5 skip
      - git_shallow_clone                   # shallow clone 으로 source_1 / source_6 skip
    downgrade_action:                       # 선택 — AND gate 결과 downgrade 시 취한 action
      enum: [null, to_section_4_informational, pivot_mark]
      # null = 8-tuple AND gate PASS (downgrade 없음)
      # to_section_4_informational = §6 → §4 이동 (ADR candidate 수준 미달 판정)
      # pivot_mark = §6 내용 보존 + [pivot: <사유>] 마커 추가 (ADR-045 Amendment 9 §D-10 정합)
```

## 4. ESCALATE 처리

PMOAgent self-write 단계 실패 (예: GitHub milestone API rate limit, retro file write 실패) 시:
- `status: ESCALATED`
- `writes_completed` 모든 필드 false
- Orchestrator 가 사용자 ESCALATE 후 수동 복구 의뢰

## 5. v1 → v2 변경 가능성

다음 조건에서 v2 BREAKING 가능:
- `adr_proposal` schema 확장 (예: 결정 우선순위 추가)
- 새 trigger enum 추가 (backward-compat 시 minor)
- `patterns_observed` category enum 변경 (drop 시 v2)
- `worktree_manifest` 필드 required 화 (v1.1 = optional, BREAKING 시 v2)
- `cross_story_pattern_adr_trigger` 필드 required 화 (v1.2 = optional, BREAKING 시 v2) 또는 `pattern_count_threshold` 변경 (가변 채택 시 v2 — 본 v1.2 = N=2 fixed)
- `retro_section_6_pre_publish_verify` 필드 required 화 (v1.3 = optional, BREAKING 시 v2) 또는 `verify_sources_attempted` enum closed-set 변경 (원소 추가 = additive MINOR, 원소 제거 = BREAKING v2)

## 6. Changelog

- **v1.3** (2026-05-25, CFP-1632): `retro_section_6_pre_publish_verify` optional field 추가 (PMOAgent retro §6 ADR draft 작성 후 publish 전 8-tuple verify-before-trust AND gate 실행 결과 기록 schema, additive — v1.0 / v1.1 / v1.2 consumer 호환). 3 sub-field (`verify_sources_attempted` / `verify_sources_blocked` / `downgrade_action`). MINOR per [ADR-008](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-008-inter-plugin-contract-versioning.md) (additive optional field). [ADR-045 Amendment 9 §D-10](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-045-story-retro-mandatory-trigger.md) + Amendment 10 Wave 2 mechanical lint enforcement wire 정합 — 8 source enum closed-set (source_1 ~ source_8) AND gate forcing function mechanical activation carrier.
- **v1.2** (2026-05-14, CFP-665): `cross_story_pattern_adr_trigger` optional field 추가 (Cross-Story pattern 누적 ≥ 2 검출 시 ADR escalation trigger schema, additive — v1.0 / v1.1 consumer 호환). 5 sub-field (`pattern_count_threshold` / `detected_anchor_id` / `fallback_root_cause_class` / `occurrences[]` / `escalation_action`). MINOR per [ADR-008](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-008-inter-plugin-contract-versioning.md) (additive optional field). [ADR-045 Amendment 5 §D-9](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-045-story-retro-mandatory-trigger.md) Mandatory framing 정합 — PMOAgent self-decide 영역 제거, threshold ≥ 2 도달 시 본 field mandatory 채움 의무.
- **v1.1** (2026-05-08, CFP-139): `worktree_manifest` optional 필드 추가 (GitOpsAgent 산출물 reference, additive — v1.0 consumer 호환). MINOR per [ADR-008](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-008-inter-plugin-contract-versioning.md) (additive optional field).
- **v1.0** (2026-04-29, CFP-36): 초기 동결.

## 7. 본 contract 시점 동결 ATTRIBUTION

- 동결 일시: 2026-04-29 (CFP-36) → v1.1 amendment 2026-05-08 (CFP-139) → v1.2 amendment 2026-05-14 (CFP-665) → v1.3 amendment 2026-05-25 (CFP-1632)
- 협업: Claude (codification) · CFP-31 parent spec §5.6 · CFP-139 GitOpsAgent agent file · CFP-665 ArchitectAgent (chief author) · CFP-1632 DeveloperPLAgent (Wave 2 mechanical wire)
- Source: `mclayer/plugin-codeforge-pmo/agents/PMOAgent.md` + `agents/GitOpsAgent.md` 책임 정의 + ADR-045 Amendment 5 §D-9 + ADR-045 Amendment 9 §D-10
