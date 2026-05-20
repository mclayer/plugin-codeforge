---
adr_number: null
title: ADR 번호 예약 레지스트리 (GitOpsAgent 전용 운영 레지스트리)
status: Active
category: governance
date: 2026-05-09
carrier_story: CFP-344
related_adrs:
  - ADR-050
related_files:
  - docs/parallel-work/section-ownership.yaml
  - templates/github-workflows/parallel-epic-conflict-check.yml
is_transitional: false
---

# ADR 번호 예약 레지스트리

## 상태

Active (2026-05-09) — ADR-050 §결정 1 구현. GitOpsAgent 전용 sequential append 레지스트리.

## 컨텍스트

복수 Orchestrator 세션이 동시에 서로 다른 에픽을 진행할 때 두 세션이 같은 ADR 번호로 파일을 생성하는 충돌이 발생한다 (ADR-048 중복 사례 실증). ADR-050 §결정 1에서 이 문제를 해결하기 위해 본 레지스트리를 신설했다.

**Write 주체**: GitOpsAgent 전용 (sequential append).
**충돌 해소**: 두 세션 동시 append → git merge positional conflict → GitOpsAgent가 adr_number 오름차순 re-sort.

## 결정

GitOpsAgent가 본 레지스트리를 통해 ADR 번호를 원자적으로 예약한다.

### 예약 절차

1. ArchitectAgent가 ADR 필요 신호 발신
2. GitOpsAgent가 마지막 `adr_number` + 1을 append → commit
3. ArchitectAgent가 예약된 번호로 `ADR-NNN-*.md` 생성
4. ADR merge 완료 후 `status: reserved → active`로 갱신

### 레지스트리 YAML 스키마

```yaml
reservations: []
# 형식:
# - adr_number: NNN
#   epic: CFP-XXX
#   status: reserved   # reserved | active | archived
#   reserved_at: ISO8601
```

### Amendment id slot reservation (CFP-1058 신설)

ADR 본문 안 `amendments[]` array 의 `amendment_id` slot 도 multi-session race 영역 — 본 레지스트리 안 `amendments_reserved[]` sub-tree 신설:

```yaml
amendments_reserved:
# 형식:
# - adr_number: NNN              # 기존 ADR number (active)
#   amendment_id: M              # 예약 Amendment id slot (sequential within ADR)
#   reserved_by_cfp: CFP-XXX     # carrier Story
#   reservation_date: YYYY-MM-DD KST
#   status: reserved | active | superseded
```

사용 사례 evidence (CFP-1041 vs CFP-689 race precedent): CFP-689 PR #1043 (ADR-073 Amendment 3 worktree-first self-ownership) 와 CFP-1041 (ADR-073 Amendment cross-ref) 가 동시 in-flight 시 — body intent `#1038 = Amendment 3 carrier` 가 ADR-RESERVATION 미codify 영역 → race-winner-takes-it convention (informal). 본 schema 도입으로 reservation intent 형식 codify 가능.

**Optional field — backward-compat**: `amendments_reserved[]` 신설 0 entry baseline (기존 ADR Amendment id slot retrospective reservation 면제). 신규 reservation 만 사용. CFP-1041 race precedent retrospective entry 1건 sample 가능 (CFP-1038 → ADR-073 Amendment 3 reserved 의도 evidence).

## 결과

### 현재 예약 목록

| adr_number | epic | status | reserved_at |
|---|---|---|---|
| 50 | CFP-344 | active | 2026-05-09 |
| 51 | CFP-343 | active | 2026-05-09 |
| 54 | CFP-363 | active | 2026-05-10 |
| 55 | CFP-367 | reserved | 2026-05-10 |
| 56 | CFP-374 | active | 2026-05-11 |
| 57 | CFP-379 | reserved | 2026-05-11 |
| 58 | CFP-387 | active | 2026-05-11 |
| 59 | CFP-391 | reserved | 2026-05-11 |
| 60 | CFP-389 | active | 2026-05-11 |
| 61 | CFP-423 | active | 2026-05-12 |
| 62 | CFP-407 | active | 2026-05-12 |
| 63 | CFP-436 | active | 2026-05-12 |
| 64 | CFP-445 | active | 2026-05-12 |
| 65 | CFP-438 | active | 2026-05-13 |
| 66 | CFP-521 | active | 2026-05-13 |
| 67 | CFP-526 | active | 2026-05-13 |
| 68 | CFP-527 | active | 2026-05-13 |
| 69 | CFP-342 | active | 2026-05-13 (retroactive — CFP-570 renumber from collided ADR-050; ADR file = `ADR-069-multi-repo-story-key-system.md`) |
| 70 | CFP-578 | active | 2026-05-13 (ArchitectAgent inline append per CFP-578 chief author scope — GitOpsAgent self-write 영역 inline carrier 정합. ADR file = `ADR-070-codex-verify-before-trust.md`) |
| 71 | CFP-612 | active | 2026-05-13 (ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent. ADR file = `ADR-071-orchestrator-user-dialog-convergence.md`, status `reserved → active` 전환 2026-05-14 Phase 1) |
| 72 | CFP-620 | active | 2026-05-14 (mctrader 3-cycle post-mortem Epic — Story-1 anchor ADR. ADR file = `ADR-72-production-evidence-deputy-and-epic-cutover-gate.md`. status `reserved → active` 전환 2026-05-14 Phase 1 PR #651 merged) |
| 73 | CFP-622 | active | 2026-05-14 (Sentinel #4 strike #2 carrier — Orchestrator verify-before-assert. ADR-070 자매 ADR. ADR file = `ADR-073-orchestrator-verify-before-assert.md`) |
| 74 | CFP-708 | active | 2026-05-14 (ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent. CFP-477 retro §6 후보 3 `escalation_action: adr_draft_emitted` carrier — CLAUDE.md Amendment ref drift detection lint. ADR file = `ADR-074-claude-md-amendment-ref-drift-lint.md`, status `reserved → active` 전환 2026-05-15 Phase 1 PR #711 merged) |
| 75 | CFP-709 | active | 2026-05-14 (Defense-in-depth sublayer registry — ADR-063 §결정 5 본문 표 sublayer enumeration 영역 의 kind:registry 분리. 3 carrier 누적 마찰 evidence: CFP-441/447/477. ADR file = `ADR-075-defense-in-depth-sublayer-registry.md`) |
| 76 | CFP-701 | active | 2026-05-15 (CFP-699 Epic Wave 1 Story-1 carrier — declarative reconciliation upgrade flow SSOT. ADR-074 / ADR-075 (CFP-708 / CFP-709 chronological precedence resolution per PR #712 verbatim, 2026-05-15) 점유 결과 CFP-701 = ADR-076 swap. User-confirmed Branch A (2026-05-15 KST, codeforge:user-dialog-mode skill 경유). ArchitectAgent inline append per ADR-070 / CFP-578 chief author precedent. ADR file = `ADR-076-declarative-reconciliation-upgrade.md`. Note: ADR-74/75 row append 는 CFP-708/709 carrier 책임 — 본 row 는 CFP-701 단독 self-write.) |
| 77 | CFP-759 | active | 2026-05-16 KST (GitOpsAgent sequential append — 요구사항 레인 clarification 강제 재조사 전파 정책 SSOT. RequirementsPL clarification 답변 수신 시 전 에이전트 재조사 강제 + 조건부 PMO 합류 + design-reading fan-out + stale 게이트 + 안전 envelope 정책 anchor ADR. status `reserved → active` 전환 2026-05-16 KST Story-1 Phase 1 — ADR file = `ADR-077-clarification-forced-reinvestigation-propagation.md`. ArchitectAgent direct write per CFP-759 chief author scope — ADR-070 / CFP-578 precedent.) |
| 78 | CFP-919 | active | 2026-05-18 KST (ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent — 살아있는 구조 설계 문서 (living architecture doc) 유지 정책 SSOT. 설계 레인이 Story key 독립 살아있는 구조 설계 문서를 매 실행 갱신 + 게이트 + 드리프트 체크 정책 anchor (mechanism = S2/S3/S4 위임). Change Plan 델타와 상보적 누적 현재 상태 SSOT anchor ADR. status `reserved → active` 전환 2026-05-18 KST Story-1 Phase 1 (ADR-077 row 77 precedent 정합). ADR file = `ADR-078-living-architecture-doc.md`. parent_epic CFP-756.) |
| 79 | CFP-770 | active | 2026-05-16 KST (ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent — KST timestamp display mandate (Layer-bounded) SSOT. governance display layer 영속 artifact 시각 = KST `+09:00` ISO 8601 zoned 강제 / contract field layer (7 contract + Story §14 schema field) = UTC strict 0건 변경 invariant. status `reserved` 미경유 직접 `active` (Epic 비소속 단일 Story carrier, ADR-077 row 77 precedent 정합). ADR file = `ADR-079-kst-timestamp-display-mandate.md`. Phase 2 mechanical lint = CFP-771 (blocks-on CFP-770) Amendment 1 carrier.) |
| 80 | CFP-751 | active | 2026-05-16 KST (Orchestrator Lead-conducted per ADR-070 / CFP-578 precedent — Agent role terminology canonical standardization SSOT: "deputy" 일반 명사 → "SubAgent" canonical form, `*DeputyAgent` 고유 식별자 + `codeforge:deputy-mandate` skill name + "Deputy mandate 매트릭스" 개념명 보존. Class-A (general noun, 치환) vs Class-B (identifier/concept, 보존) 분류 규칙. cross-plugin sibling sync 적용 (ADR-010, codeforge-design plugin). 사용자 directive: "deputy라는 표현을 쓰는데... agent로 못박아라" + "남발하지만 않으면 된다. 기존 Deputy로 명명한 Agent 명은 두고 SubAgent로 치환 가능한 경우". forbid-list 아님 (ADR-064 카테고리 a 미등록 — 용어 표준화 가이드라인). status `reserved` 미경유 직접 `active` (ADR-079 row 79 precedent 정합). ADR file = `ADR-080-agent-role-terminology-deputy-subagent.md`.) |
| 81 | CFP-819 | active | 2026-05-17 KST (ArchitectPL direct write per ADR-070 / CFP-578 chief author precedent — Codex worker prompt boilerplate composition SSOT: 3 mandatory section (dogfood-out Story path / lane stage / sandbox boundary) + verify-before-trust scope 5 sub-scope 분리 (file / dir / cross-repo / grep count active vs historical / ADR §결정 번호 정확성) + 3-lane partition (Codex factual citation / DesignReview boundary completeness / CodeReview style + history disjoint). ADR-052 Amendment 6 cross-ref sibling. ADR-070 §D5 declaration-only retain precedent verbatim 정합 (`mechanical_enforcement_actions: []` + registry yaml 무변경). 6-Story carry-over fp 0 evidence sentinel (CFP-770/771 fp 8 baseline → CFP-786/801/792/795/810 fp 0 5 consecutive) + ADR-045 Amendment 5 §D-9 cross_story_pattern_adr_trigger forcing function (pattern_count 5 reach YES, escalation_action: adr_draft_emitted) carrier. status `reserved` 미경유 직접 `active` (ADR-079/080 row precedent 정합). ADR file = `ADR-081-codex-worker-prompt-boilerplate.md`.) |
| 82 | CFP-776 | active | 2026-05-17 KST (ArchitectPL direct write per ADR-070 / CFP-578 chief author precedent — write-time self-write verification mandate super-class SSOT: lane agent §9 evidence 작성 / Phase 0 ChangeImpactAgent mapping / Story corpus enumeration write-time 에 source/value/ownership 을 verify 없이 단언하는 super-class 결함 차단. ADR-073 (Orchestrator cross-repo state / assumption) + ADR-070 (Codex external worker output) disjoint super-class — ADR-082 = internal lane agent self-write verify layer. §결정 1 layer disjoint 4-layer 표 (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D) + §결정 2 scope (a-d) write-time verify 의무 + §결정 3 정정 재귀 ADR-067 max FIX 3/3 RESET cap cross-ref + §결정 4 citation≠assertion + §결정 5 provisional defer + §결정 6 `mechanical_enforcement_actions: []` known-limitation rationale binding (ADR-040 Amendment 3 missing flag 회피, ADR-070 §D5 declaration-only retain 선례 + ADR-RESERVATION row 81 CFP-819 동일 패턴) + self-referential trap 회피 (EC-3 self-protection). 본 carrier = ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count 3 ≥ threshold 2 산물 (CFP-746 §6후보1 + CFP-770 §6후보1, escalation_action escalate_user → 사용자 단일 super-class 통합 결정 2026-05-16 KST). ADR-073/070 Amendment 1 + ADR-045 Amendment 6 cross-ref. doc-only fast-path (ADR-054 단일 PR). status `reserved` 미경유 직접 `active` (ADR-079/080/081 row precedent 정합). ADR file = `ADR-082-write-time-self-write-verification-mandate.md`.) |

| 83 | CFP-899 | active | 2026-05-18 KST (ArchitectPLAgent Phase 1 design lane direct write per ADR-070 / CFP-578 chief author precedent — Consumer-applicability filter policy SSOT, CFP-858 Wave 4 sub-Epic S2 carrier. reconcile-protocol-v1 v1.9 §4.12 `consumer_applicability_filter_binding` block carrier — 4-way enum closed-set `plugin`/`consumer`/`mixed`/`unknown` + positive whitelist `consumer_applicable_workflows.txt` + mixed repo full workflow set exemption + fail-closed unknown semantic + filesystem-only signal invariant (network call 0 / gh api 0 / marketplace.json membership check 0 — offline-first + trust boundary 명확 + < 1ms primary signal cost, SecurityArch + OpRiskArch deputy primary recommendation). ADR-027 Amendment 6 §결정 10 sibling carrier (consumer-side signal SSOT — filesystem-only 2-signal cross-product `.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` 4-way truth-table + boundary disjoint invariant 보존). CFP-898 §4.11 vertical closure resolver 와 sequential composition (filter 먼저 → closure 다음 = hook order: closure resolver → consumer-applicability filter → cp). mctrader-data#81 14 failing checks horizontal filter layer evidence (Epic CFP-858 결함 2 root cause — wrapper-only workflow 무차별 유입 silent harm super-class, CFP-898 closure missing 차단의 dual axis). is_transitional: false (permanent architecture invariant — 약화 방향 차단). mechanical_enforcement_actions[] = `consumer-applicability-filter-detection` (status: `declaration-only-Wave-1`, ADR-082 §결정 6 retain pattern 답습 — Phase 2 carrier deferred: `templates/scripts/detect-repo-kind.py` 실 구현 + `templates/consumer_applicable_workflows.txt` populate + reconcile-overlay.sh hook insertion + test suite + evidence-checks-registry warning tier wire). status `reserved → active` 전환 = S2 Phase 1 PR ArchitectPLAgent commit time 점유 확정 (정상 transition path — ADR-079/080/081/082 direct `active` 진입 row 와 분리 invariant). ADR file = `ADR-083-consumer-applicability-filter.md`.) |

| 84 | CFP-989 | active | 2026-05-19 KST (ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent — numeric-space-sharing channel disjointness invariant codification SSOT. CFP-986 §4.12 classification_severity_disjoint_invariant + §4.13 classification_not_severity_clause (commit `b6d7eb5`) first applied case 의 일반화: inter-plugin contract 에서 numeric exit code / enum cross-channel propagate 시 channel 간 numeric-space 가 share 되면 explicit disjointness invariant 를 contract 본문 + ADR 본문 + domain-knowledge entry 3 곳 모두 명시 declare 의무 (implicit 금지). DesignReview lane MUST flag = behavioral directive. ADR-082 §결정 1 disjoint 4-layer 표 안 governance pattern 의 inter-plugin contract level codification 동형 layer. precedent chain 5번째 declaration-only retain instance (ADR-070 §D5 → ADR-082 §결정 6 → ADR-081 §결정 D6.e → ADR-070 Amendment 4 D6.4 → 본 ADR-084). is_transitional: false (permanent — 약화 차단 ratchet). mechanical_enforcement_actions: [] retain + clause "if pattern_count ≥ 2 recurrence, follow-up CFP MUST promote to mechanical lint" 명시 의무 (ADR-082 §결정 6 rationale 답습). status `reserved` 미경유 직접 `active` (ADR-079/080/081/082/083 row precedent 정합). ADR file = `ADR-084-numeric-space-sharing-channel-disjointness.md`. carrier 본 Story = doc-only fast-path 1-PR (ADR-054 정합). parent_epic null — Epic CFP-858 retro emission 후속 독립 Story (ADR-064 §결정 5 CFP scope unitary). E-3 carrier from EPIC-RESULTS-CFP-858.md §6.3.) |

| 85 | CFP-1041 | active | 2026-05-20 KST (ArchitectPLAgent Phase 1 design lane direct write per ADR-070 / CFP-578 chief author precedent — Multi-session collaboration protocol SSOT. 복수 Claude Code session 이 동일 repository / Story / branch 동시 작업 시 ownership 결정 / 분담 / handoff 의 normative SSOT codify. 3-pillar anchor: (a) `active_sessions[]` field (Story Issue body + Story file frontmatter dual carrier, 5-tuple git_identity / worktree_path / entry_phase / entered_at_kst / last_heartbeat_kst) (b) lane-entry sentinel `gh pr list --search "head:<branch>"` ownership verify (ADR-073 Amd 2 polling enum 4번째 source append cross-ref) (c) rebase merge 우선 normative (force-push 회피, CFP-681 success variant). super-class anchor §결정 1 5-layer disjoint 표 (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row "Multi-session collaboration" 추가, anchor-first pattern). axis disjoint: verify-before-trust 4-layer (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D) 와 verify axis / parallel epic conflict (ADR-050 PR-level vs ADR-085 session-level pre-hoc) / worktree-first single-session (ADR-040 namespace surface) 모두 disjoint. is_transitional: false (permanent — 약화 차단 ratchet). mechanical_enforcement_actions = [`active-sessions-presence`, `lane-entry-ownership-verify`] declaration-only-Wave-1 (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습, Wave 2 mechanical wire 별 sub-CFP carrier). 본 carrier = ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach (8+ parallel race incidents single session evidence CFP-953/946/949/932/954/991/967/1014 lineage) escalation_action: adr_draft_emitted 산물. retroactive evidence anchor = CFP-681 (rebase merge first success variant). status `reserved` 미경유 직접 `active` (ADR-079/080/081/082/084 row precedent 정합). ADR file = `ADR-085-multi-session-collaboration-protocol.md`. carrier 본 Story = Phase 1+2 분리 (ADR-054 doc-only fast-path 비대상 — 신규 ADR 도입 governance behavior 변경 영역 ADR-013 dogfood-out 정합). parent_epic null — independent Story (ADR-064 §결정 5 CFP scope unitary).) |

| 86 | CFP-1086 | active | 2026-05-20 KST (ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent — Deputy 신설 결정 framework SSOT, BackendArchEpic CFP-1086 Story-1 carrier (메타 산출물). P7 framework: axis 분석 (orthogonal axis 검증) + 5-checklist (axis disjoint / cost-token budget / consumer carrier / sibling Epic align / deferred trigger 명시) + deferred carrier path codify. ADR-042 Amendment 8 (7+3+1 roster — AggregateArchitect 신설 / APIContractArchitect 신설 / ModuleArchitect rename / DataArchitect 축소 / AggregateArch CONDITIONAL applicability P2) + ADR-068 Amendment 2 (wording SSOT chief tie-break ladder P1) sibling carriers within Story-1. brainstorm Phase 0+1+2 완결 (2026-05-20 KST — 4 agent burst Domain/Researcher/Analyst/PMO + why-first dialog 4 turn Q1 WHY → Q2 명칭 → Q2-prime ModuleArch → Q3 Tool=B → Q4 AggregateArch → Q4-prime DDDArch reject → Q5 ACK all + PMO 2nd pass 6 Story / 3 Wave + scope_manifest YAML + 5-checklist self-application 6 Story 전건 READY). is_transitional: false (permanent — 약화 방향 차단 ratchet). status `reserved → active` 전환 2026-05-20 KST Story-1 Phase 1 PR ArchitectAgent commit time 점유 확정 (정상 transition path — ADR-083 row 83 CFP-899 precedent 정합). ADR file = `ADR-086-deputy-creation-decision-framework.md`. parent_epic CFP-1086. Sequential prerequisite 충족: CFP-1026 W3 close (S4 #1031 / S5 #1032 / S6 #1033 / follow-up #1037 ALL CLOSED, milestone #6 CLOSED, Epic #1026 CLOSED, 2026-05-20 KST). Follow-up CFP carriers: #1079 (OpsExecutionArch, sequential ADR-042 Amendment coordinator) + #1081 (Cross-Story rename sweep + α escalation 흡수) + #1082 (empirical evidence audit, ADR-068 I-5 self-app baseline) + #1084 (decision_carrier_pattern ADR draft) + #1085 (ADR-068 Amd N I-5 mechanical wire draft) + #1059 (배포 lane sibling Epic cross-ref).) |

| 87 | CFP-1059 | active | 2026-05-20 KST (GitOpsAgent sequential append per ADR-RESERVATION write boundary — Deploy lane 신설 SSOT carrier. codeforge 7 lane → 8 lane 확장 시 deploy lane 의 plugin lifecycle / lane spawn order / worktree branch naming / preflight 체크 / phase label 매핑 normative SSOT. ADR-023 Amendment / ADR-026 Amendment / ADR-027 Amendment 3 carrier sibling within CFP-1059. status `reserved` 미경유 직접 `active` (ADR-079/080/081/082/083/084/085/086 row precedent 정합 — chief author scope). ADR file = `ADR-087-deploy-lane-and-lifecycle-extension.md`. parent_epic CFP-1059.) |

| 88 | CFP-1059 | active | 2026-05-20 KST (GitOpsAgent sequential append per ADR-RESERVATION write boundary — Deploy Review lane 신설 + ProductionEvidenceDeputy 이관 SSOT carrier. deploy review lane 의 agent roster / ProductionEvidenceDeputy 이관 경계 / review verdict contract / preflight 체크 normative SSOT. ADR-072 Amendment carrier sibling within CFP-1059. status `reserved` 미경유 직접 `active` (row 87 동일 precedent 정합). ADR file = `ADR-088-deploy-review-lane-and-production-evidence-transfer.md`. parent_epic CFP-1059.) |

| 89 | CFP-1059 | active | 2026-05-20 KST (GitOpsAgent sequential append per ADR-RESERVATION write boundary — Schema 변경 7 원칙 SSOT carrier. 양방향 호환 / expand-contract / reverse / smoke / cross-repo / backup / hard limit 7 원칙 normative SSOT. ADR-089 Schema 7 principles anchor. status `reserved` 미경유 직접 `active` (row 87/88 동일 precedent 정합). ADR file = `ADR-089-schema-change-7-principles.md`. parent_epic CFP-1059.) |

| 90 | CFP-1059 | active | 2026-05-20 KST (GitOpsAgent sequential append per ADR-RESERVATION write boundary — Cross-layer 참조 정책 + 양 layer 동시 변경 순서 SSOT carrier. source-first expand / leaf-first contract ordering invariant normative SSOT. ADR-090 cross-layer reference policy anchor. status `reserved` 미경유 직접 `active` (row 87/88/89 동일 precedent 정합). ADR file = `ADR-090-cross-layer-reference-policy.md`. parent_epic CFP-1059.) |

### 번호 해제 (archived)

ADR deprecated/superseded 시 해당 row `status: archived`. 번호 재사용 금지.

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-050](ADR-050-parallel-epic-conflict-coordination.md) — 본 레지스트리 결정의 carrier ADR
- `docs/parallel-work/section-ownership.yaml` — ADR-050 §결정 4 (locked 섹션 선언)
- `templates/github-workflows/parallel-epic-conflict-check.yml` — ADR-050 §결정 3 (자동 충돌 감지)
