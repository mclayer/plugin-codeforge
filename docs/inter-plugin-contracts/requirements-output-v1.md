---
kind: contract
contract_version: "1.3"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-requirements (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
  - "ADR-077 (Clarification 강제 재조사 정책 — §결정 5 carrier: recheck_counter typed surface = 4-layer disjoint 3번째 cross-declare 위치 / Amendment 1 carrier: why_roundtrip_counter typed surface = 5번째 disjoint measurement channel, CFP-2725)"
  - ADR-145 (요건 traceability zero-drop 게이트 — §결정 6 v1.2 acceptance_criteria[] additive MINOR carrier)
  - ADR-159 (요구사항 lane enrichment + design-entry 사용자 확정 gate SSOT — 결정 4 terminal event·확정 발화 verbatim primary Story §5.5, CFP-2725 v1.3 why_roundtrip counter 짝)
authors:
  - CFP-42 sibling backfill (2026-04-29) — wrapper sibling 첫 작성, canonical 본문 verbatim mirror
  - CFP-2603 (2026-07-11) — v1.1 → v1.2 MINOR: acceptance_criteria[] top-level optional 추가 (AC-ID zero-drop, ADR-145 §결정 6 / ADR-008 §결정 2 backward-compat)
  - CFP-2725 (2026-07-18) — v1.2 → v1.3 MINOR: why_roundtrip_tracking top-level optional block 추가 (why-왕복 counter = ADR-077 Amendment 1 §2 5번째 disjoint measurement channel, reinvestigation_tracking 과 peer / ADR-008 §결정 2 backward-compat) + phase_label_transitioned 주석 drift 정정 (요구사항리뷰 lane 경유)
---

# requirements_output v1 — Inter-plugin Contract

**상위 SSOT 위치**: 본 파일이 단일 원본 (canonical) — CFP-2158 / [ADR-118](../../archive/adr/ADR-118-monorepo-consolidation.md) D5 가 lane canonical ↔ wrapper mirror 이중체계를 폐지 (monorepo 통합 S1 후속). frontmatter 의 ADR-010 인용은 historical (sibling sync 정책 Superseded — ADR-010 Amendment 5). versioning 룰 = ADR-008 불변.

`codeforge-requirements` plugin → `codeforge` core (Orchestrator) 단방향 schema. 4 sub-agent (Domain · Analyst · Researcher) 병렬 스폰 후 RequirementsPLAgent 가 통합·자체 write 후 typed output 으로 결과 audit.

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① requirements_packet 작성 (Story §1 + §3 ADR list + §4 코드 경로 + Project Config)
        ▼
codeforge-requirements plugin
  └─ RequirementsPLAgent
        │
        │ ② Orchestrator가 한 메시지에 3 sub-agent 병렬 dispatch
        ▼
  ├─ DomainAgent       (도메인 지식 공백 분석)
  ├─ RequirementsAnalystAgent (Codex 호출 — ambiguity / 가정 / AC)
  └─ ResearcherAgent   (외부 기술·표준·선행사례)
        │
        │ ③ 3 결과 PL에 return
        ▼
  └─ RequirementsPLAgent dedup + 상충 조정 통합
        │
        │ ④ Self-write 단계:
        │    - Edit(docs/stories/<KEY>.md §2/§5/§6 동시 채움)
        │    - DomainAgent 의 KB 공백 해소 시: Edit(docs/domain-knowledge/**/*.md)
        │    - mcp__github__add_issue_comment ([요구사항] prefix)
        │    - phase 라벨 transition: phase:요구사항 → phase:요구사항-리뷰 (ADR-125 10-lane — 요구사항리뷰 lane 경유 후 phase:설계)
        ▼
        │ ⑤ requirements_output v1 typed output
        ▼
codeforge core (Orchestrator)
        │
        │ ⑥ Output 처리:
        │    - PASS → 다음 lane (설계) 진입
        │    - ESCALATE → 사용자 인터랙션 (Story §1 ambiguity 해결 필요)
```

## 2. requirements_packet (Orchestrator → RequirementsPLAgent)

```yaml
requirements_packet:
  contract_version: "1.0"           # 필수
  story_key: <STORY_KEY>             # 필수
  story_section_1: <markdown>        # Story §1 verbatim
  related_adr_paths:                 # 선택 — Story §3 fetch 결과
    - docs/adr/ADR-NNN-<slug>.md
  related_code_paths:                # 선택 — Story §4 fetch 결과
    - <path glob>
  project_config:                    # 필수 — overlay project.yaml slice
    domain: <domain identifier>
    discussions_kb_category: <gh discussions category id, optional>
```

## 3. requirements_output (PL → Orchestrator)

```yaml
requirements_output:
  contract_version: "1.3"           # CFP-2725: 1.2 → 1.3 MINOR (why_roundtrip_tracking top-level 추가). CFP-2603: 1.1 → 1.2 (acceptance_criteria[] top-level). CFP-834: 1.0 → 1.1 (reinvestigation_tracking)
  story_key: <STORY_KEY>

  status: PASS | ESCALATE_USER_CLARIFICATION | ESCALATE_PACKET_INCOMPLETE  # 필수

  sub_agent_results:                # 필수 — 3 sub-agent 결과 audit
    domain:
      kb_gaps_filled: <int>          # 새로 KB 작성 페이지 수
      kb_paths: [<list>]
      null_result: <bool>            # 도메인 공백 없음
    analyst:
      ambiguities_found: <int>
      assumptions_listed: <int>
      acceptance_criteria_count: <int>
      null_result: <bool>            # 사용자 원문 완전 명확
    researcher:
      external_refs_count: <int>     # 인용 외부 자료 수
      libraries_evaluated: [<list>]
      null_result: <bool>            # 조사 불필요

  # AC-ID 항목화 목록 (CFP-2603 / ADR-145 §결정 6 — v1.2 additive MINOR)
  acceptance_criteria:              # OPTIONAL top-level — sub_agent_results / writes_completed 와 peer (.analyst 하위 아님).
                                    #   부재 시 게이트가 list 실재 강제(ADR-145 AC-3). 계약 field 는 영구 optional (v1.1 consumer 무영향).
                                    #   analyst.acceptance_criteria_count 는 보존(제거 = MAJOR) — 정수 요약 ↔ 항목 identity 병존.
                                    #   §5.2 스키마 2-등급 (ADR-145 §결정1(i)/§결정6):
                                    #     REQUIRED (machine-enforced — Hop1 validate_ac_record fail-closed) = id / statement / source / tier
                                    #     DERIVED  (파생 — present 시 format-only, 완결성=계약/Hop2/review 층, 게이트 §5-parse 미재검증)
                                    #              = verification / coverage_required / phase
                                    #              (coverage_required←tier+Hop2 / phase←run-phase+tier / verification←tier+Hop2·review)
    - id: AC-1a                     # [required] ^AC-(\d+)([a-z])?$ (sub-letter 수용 — AC_ID_RE SSOT, naive AC-\d+ drop 금지)
      statement: <given-when-then>  # [required] 검증 가능한 분기 행동 (non-empty)
      source: user | derived        # [required] enum
      verification: <테스트 종류·관측점>   # [derived] 파생 (present 시 format-only)
      coverage_required: [design, §8_test]  # [derived] 파생
      phase: 1 | 2                  # [derived] 파생 (1=문서·명명 / 2=실 테스트파일)
      tier: normative | declared | advisory   # [required] enum — normative=fail-closed 기계 / declared=review-verified / advisory=경보만

  # PL self-write 결과 audit
  writes_completed:
    story_section_2: <bool>           # 도메인 분석 (§2)
    story_section_5: <bool>           # 요구사항 확장 해석 (§5)
    story_section_6: <bool>           # 외부 지식 배경 (§6)
    domain_kb_files: <int>            # 신규 또는 갱신된 docs/domain-knowledge/* 파일 수
    phase_comment: <bool>             # [요구사항] prefix GitHub comment
    phase_label_transitioned: <bool>  # phase:요구사항 → phase:요구사항-리뷰 (ADR-125 10-lane — 요구사항리뷰 lane 경유 후 phase:설계; 구 coarse phase:요구사항→phase:설계 stale 정정 CFP-2725)

  # ESCALATE 시 추가 (사용자 clarification 요청 항목)
  user_clarification_needed:        # 선택 — null 또는 array
    - question: <text>
      context: <text>
      blocking: <bool>
```

## 3.1 Story §1 frontmatter schema (cross-repo Epic 지원, v1.1)

CFP-60 / [ADR-020](../../archive/adr/ADR-020-cross-repo-epic-pattern.md) 신설. Story `§1 메타` 의 YAML frontmatter 에 cross-repo Epic 정보 추가 (optional, backward compatible).

```yaml
---
key: <KEY>           # required (예: CFP-60)
title: <string>      # required
status: <phase:*>    # required
date: <ISO8601>      # required
type: story          # required
github_issue: <owner/repo#N>  # required

# Cross-repo Epic 지원 (v1.1, ADR-020 / CFP-60)
epic_owner_repo: <owner/repo> | null  # OPTIONAL — null if single-repo Story
epic_dependencies:                    # OPTIONAL — empty list if independent
  - type: hard_block | design_parallel | impl_parallel
    target: <KEY>
    repo: <owner/repo>
---
```

**Type 정의**:
- `hard_block`: blocking dependency — target merge 전 본 Story 작업 불가
- `design_parallel`: 설계 동시 진행 가능 (구현은 target 후)
- `impl_parallel`: 구현 동시 진행 가능 (target merge 와 무관)

**Backward compatibility**:
- Pre-v1.1 Story (CFP-1 ~ CFP-59) 는 `epic_dependencies` / `epic_owner_repo` field 없이 작성됨
- v1.1 consumer 가 default `[]` / `null` 로 처리
- 기존 Story 영향 X — 신규 Story 만 optional 사용

## 3.2 재조사 카운터 typed surface (recheck_counter, v1.1)

# CFP-834 / ADR-077 §결정 5 carrier. requirements_output 본문에 reinvestigation_tracking
# top-level block 추가 (optional, backward compatible — ADR-008 §결정 2 MINOR).
#
# 4-layer disjoint cross-declare 위치 (cross-ref only — 본문 재선언 금지):
#   본 surface = 4-layer disjoint counter 의 3번째 cross-declare 위치
#   (1 = ADR-077 §결정 5 + §결과 절 / 2 = playbook §4.4.0 표 / 3 = 본 schema).
#   cross-pollinate 금지 (ADR-077 §결정 5 normative). 1·2번째 본문 재선언 금지.

```yaml
requirements_output:
  contract_version: "1.3"           # CFP-2725: 1.2 → 1.3 MINOR (why_roundtrip_tracking top-level 추가). CFP-2603: 1.1 → 1.2 (acceptance_criteria[] top-level). CFP-834: 1.0 → 1.1 (reinvestigation_tracking)
  # ... (기존 §3 필드 불변: status / sub_agent_results / acceptance_criteria / writes_completed / user_clarification_needed)

  reinvestigation_tracking:         # OPTIONAL — clarification-driven 재조사 누적 forward 신호
    optional: true                  # ADR-008 §결정 2 MINOR — consumer v1.0 채 못 받아도 no-op
    recheck_counter: <int>          # cross-cycle 누적. default 0 (absent ≡ 0)
                                    # cap SSOT = ADR-077 §결정 4 표 P-2 recheck_counter_cap
                                    # (평문 박제 금지 — cross-ref only, DC-3)
    recheck_status: accumulating | cap_reached   # enum (D6)
                                    # accumulating: 0 <= recheck_counter < cap
                                    # cap_reached:  recheck_counter == cap → ESCALATE
                                    #   escalation_class: scope_redefinition_required
                                    #   (ADR-077 §결정 6 cross-ref — NOT failure/abort)
                                    #   ESCALATE 후 recheck_counter RESET to 0 (새 baseline)
    owner: RequirementsPL           # Story §9.0 self-write (fix:* 라벨 미부착)

  # disjoint invariant (cross-ref only — ADR-077 §결정 5):
  #   - recheck_counter ≠ §10 FIX Ledger row (fix-event-v1 미공유 구조)
  #   - §10 합산 금지 (ADR-067 cross-lane 합산 금지) — cap_reached → ESCALATE 도
  #     §10 FIX Ledger 미기록 (ADR-077 §결정 6 §10 무기록 정합)
  #   - 정보 무결성 (ADR-077 §결정 7 cross-ref): 재조사가 직전 cycle
  #     [hypothesis]/[fact-check-pending] marker 를 무검증 [verified] 승격 금지
```

**계약 불변식 요약**:
- `reinvestigation_tracking` block 부재 = `recheck_counter` 암묵 `0` + `recheck_status: accumulating` (backward-compat default, DataMigrationArch INV-4).
- `recheck_status: cap_reached` ⟺ `recheck_counter == cap` (ADR-077 §결정 4 P-2 SSOT) → consumer 는 contract 해석으로 ESCALATE 인지 (AC-8.2).
- `cap` 정량값 = schema 본문 평문 금지 — `ADR-077 §결정 4 표 P-2 recheck_counter_cap` cross-ref only (DC-3).

## 3.3 why-왕복 counter typed surface (why_roundtrip_counter, v1.3)

# CFP-2725 / ADR-077 Amendment 1 §2 carrier. requirements_output 본문에 why_roundtrip_tracking
# top-level block 추가 (optional, backward compatible — ADR-008 §결정 2 '새 선택 필드 추가' MINOR).
#
# §3.2 reinvestigation_tracking 과 PEER (형제) top-level block — 혼입 금지 (disjoint 불변식):
#   why-왕복 counter = ADR-077 §결정 5 disjoint counter 의 5번째 measurement channel
#   (5th = 요구사항 lane intake 왕복 layer, Amendment 1 §2). recheck_counter(§3.2)와 별 block.
#   cross-pollinate 금지 (ADR-077 §결정 5 normative 상속). §3.2 block 안 nesting 금지.

```yaml
requirements_output:
  contract_version: "1.3"           # CFP-2725: 1.2 → 1.3 MINOR (why_roundtrip_tracking top-level 추가)
  # ... (기존 §3 / §3.2 필드 불변: status / sub_agent_results / acceptance_criteria / writes_completed / user_clarification_needed / reinvestigation_tracking)

  why_roundtrip_tracking:           # OPTIONAL — 사용자 최종 확정 why-왕복 measurement channel (design-entry sign-off, ADR-159 결정 4)
    optional: true                  # ADR-008 §결정 2 MINOR — consumer v1.2 채 못 받아도 no-op
    why_roundtrip_counter: <int>    # 요구사항 lane intake why-왕복 누적. default 0 (absent ≡ 0)
                                    # cap SSOT = ADR-077 §결정 4 정량 표 (평문 박제 금지 — cross-ref only, 실측 전 `[empirical-source: TBD]` 상속)
    confirmation_status: unconfirmed | roundtrip_active | confirmed   # enum — 미확정 / 왕복중 / 확정됨
                                    # confirmed: 사용자 최종 확정 발화 존재 (terminal event `user-final-confirmation-driven`, ADR-159 결정 4)
                                    #   순수 확정(내용 무변경) = terminal event → 재조사 fan-out 미발동
                                    #   내용 수정 동반 확정 = clarification origin 재조사 후 재확정 (§3.2 recheck 경로)
    owner: RequirementsPL           # Story §5.5 self-write (확정 발화 verbatim primary SSOT — ADR-159 결정 4)

  # disjoint invariant (cross-ref only — ADR-077 Amendment 1 §2):
  #   - why_roundtrip_counter ≠ recheck_counter (§3.2) — recheck_counter_cap 비소모 (cross-pollinate 금지 상속)
  #   - terminal event(순수 확정) 비소모 / §10 FIX Ledger 합산 금지 (ADR-067 cross-lane 합산 금지)
  #   - measurement channel ≠ cognitive layer — ADR-071 §결정 3 cognitive Layer 1-4 와 무관 (cross-namespace disambiguation)
```

**계약 불변식 요약**:
- `why_roundtrip_tracking` block 부재 = `why_roundtrip_counter` 암묵 `0` + `confirmation_status: unconfirmed` (backward-compat default).
- `why_roundtrip_tracking` 과 `reinvestigation_tracking`(§3.2) 는 **disjoint peer block** — 상호 nesting·counter 합산 금지 (ADR-077 §결정 5 / Amendment 1 §2 normative).
- `cap` 정량값 = schema 본문 평문 금지 — `ADR-077 §결정 4 표` cross-ref only (recheck cap 과 동거, 재선언 금지).
- advisory ceiling (ADR-159 결정 6): 본 counter surface = presence 기록 typed field — 신규 기계 강제 게이트 0.

## 4. ESCALATE 처리

- **ESCALATE_USER_CLARIFICATION**: Analyst 가 user 원문 ambiguity 해결 불가. PL 이 specific 질문 list 반환 → Orchestrator 가 user 에게 전달
- **ESCALATE_PACKET_INCOMPLETE**: 필수 packet 필드 누락 (story_section_1 부재 등) — 즉시 Orchestrator 수동 복구

## 5. v1 → v2 변경 가능성

- 새 sub-agent 추가 (예: ComplianceAnalyst) — sub_agent_results schema 확장 minor (v1.1)
- 새 ESCALATE enum 추가 — minor
- writes_completed 필드 schema 확장 — minor
- reinvestigation_tracking 확장 (recheck_counter 파생 필드 추가) — minor (CFP-834: v1.0 → v1.1 기존 진화 경로 정합)
- acceptance_criteria[] top-level 항목화 목록 추가 — additive MINOR (CFP-2603 / ADR-145 §결정 6: v1.1 → v1.2, acceptance_criteria_count 보존 = MAJOR 회피, ADR-008 §결정 2 backward-compat)

## 6. 본 contract 시점 동결 ATTRIBUTION

- 동결 일시: 2026-04-29 (CFP-37)
- 협업: Claude (codification) · CFP-31 parent spec §5.7
- Source: `plugins/codeforge-requirements` 4 agent 책임 정의
