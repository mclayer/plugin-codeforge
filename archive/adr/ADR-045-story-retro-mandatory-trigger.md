---
adr_number: 43
title: Story 완료 회고 의무화 — Phase 2 PR merge 후 PMOAgent 자동 trigger + gate:retro-complete close-blocking
status: Proposed
category: Team & Process
date: 2026-05-09
carrier_story: CFP-138
parent_epic: CFP-134
related_files:
  - templates/github-workflows/retro-mandatory.yml
  - templates/github-workflows/post-merge-followup.yml
  - templates/github-workflows/phase-label-invariant.yml
  - templates/story-page-structure.md
  - docs/inter-plugin-contracts/label-registry-v1.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - scripts/bootstrap-labels.sh
  - CLAUDE.md
related_stories:
  - CFP-134
  - CFP-135
  - CFP-138
  - CFP-1580  # Amendment 7 carrier — pattern_count 5 escalation_resolved_carrier (Wave 2 mechanical wire DR-skip pattern, paired sibling ADR-068 Amendment 4)
  - CFP-1592  # Amendment 8 carrier — §D-9 sub-decision (b) 3-source AND verify declarative anchor (sequential first, paired sibling)
  - CFP-1623  # Amendment 9 carrier — §D-10 신설 8-tuple pre-publish preflight forcing function (paired sibling sequential second after #1592, retro-batch-origin discriminator confirmed 5/5 PIVOT rate)
  - CFP-1632  # Amendment 10 carrier — §D-10 Wave 2 mechanical wire activation evidence (CFP-1623 Wave 1 declarative anchor 발효 후 mechanical layer activation: scripts/lib/check_retro_batch_adr_draft_pre_publish.py + thin bash wrapper + canonical workflow + self-app mirror + bats fixture cohort + evidence-checks-registry 132nd entry + label-registry-v2 v2.76→v2.77 102nd hotfix-bypass:* family member + pmo-output-v1 v1.2→v1.3 retro_section_6_pre_publish_verify optional field codify, evidence-only Amendment ADR-045 §결정 본문 변경 0건, 13-instance Wave 1→Wave 2 established pattern 13번째 instance)
  - CFP-1680  # Amendment 11 carrier — §D-11 신설 (PMOAgent retro batch closure pattern normative codify, HIGH normative consolidation doc-only fast-path ADR-054 Cat 1, 4-option decision enum CLOSE_AS_OBVIATED/CLOSE_AS_SENTINEL/PROMOTE/DEFER + 5 sub-scope verify-before-trust mandate + closure summary table SSOT 5-column + 3 step closure forcing function, paired sibling carrier playbook §18, 6 applied case evidence chain CFP-963/1339/1612/1637/1648/1680 pattern_count 6 reach threshold 2 = 3.0x, META 24th applied case)
  - CFP-2330  # Amendment 12 carrier — §D-9 sub-decision (c) 신설 (Pattern A 반응형→예방형 merge-time gate-provenance self-attest, warning-first → ratchet posture, Epic CFP-2324 S6, #2322 흡수). gate verdict 의 lane-produced machine-checkable artifact (review-verdict-v4 packet 형식·필수필드) ∧ Story §14 lane-evidence binding multi-anchor AND (wrapper-self `mixed` repo = ADR-031 §14 면제라 PR body/코멘트 병행 anchor). 위협모델 = honest-but-careless (연극 게이트). 악의 단일계정 위조 = out-of-scope accepted risk 명시 박제. 모든 게이트 (요구사항리뷰/설계리뷰/보안테스트/배포리뷰) 적용. multi-anchor AND 3-source 패턴 = ADR-026 §결정 6 isPostMergeFix 답습.
  - CFP-2377  # Amendment 13 carrier — §D-12 신설 (phase:완료 precondition worktree-clean self-check 추가, ADR-128 완료 단계 정식화 묶음, paired sibling ADR-040 Amendment 9)
  - CFP-2392  # Amendment 14 carrier — §D-13 신설 (phase:완료 precondition capture self-check 추가, ADR-129 OMC-adopt 지식캡처 묶음, paired sibling ADR-071 Amendment 12)
related_adrs:
  - ADR-009
  - ADR-137  # Epic-close 구현-리팩터링 triage (CFP-2541 Story C) — §D-11 Epic-close sibling, 모집단·enum axis-disjoint (retro follow-up Issue ↔ 실코드 duplication anchor / CLOSE_AS_* ↔ now/defer/drop)
  - ADR-013
  - ADR-022
  - ADR-024
  - ADR-025
  - ADR-026
  - ADR-031
  - ADR-035
  - ADR-039
  - ADR-082  # Amendment 6 — §D-9 cross_story_pattern_adr_trigger 적용 evidence (ADR-082 = pattern_count 3 산물)
  - ADR-128  # Amendment 13 — 완료 단계 정식화 umbrella (본 §D-12 = phase:완료 worktree-clean precondition carrier)
  - ADR-040  # Amendment 13 — paired sibling Amendment 9 (§결정 7.K worktree-clean cleanup invariant + backstop SessionEnd 트리거)
  - ADR-129  # Amendment 14 — OMC-adopt 지식캡처+메모리다이어트 umbrella (본 §D-13 = phase:완료 capture self-check precondition carrier)
  - ADR-071  # Amendment 14 — paired sibling Amendment 12 (§18.7 MEMORY.md 슬림화 mechanism deferred 해제)
supersedes: null
superseded_by: null
amends:
  - ADR-035 (Wave 2 amendment_id 추가 — D5 Story 완료 회고 의무화 implementation level)
amendment_log:
  - amendment_id: 1
    cfp: CFP-138
    date: 2026-05-09
    scope: "Phase 1 follow-up (FIX iter 2 boundary resolution from CodeReviewPL Iter 1 P0 A-2 + P0 C-1) — §D-4 Phase 2 implementation spec 명확화: 'workflow_run **또는** scheduled cron' disjunction → 'scheduled cron `*/5 * * * *` 단독 사용 (workflow_run trigger 제거)'. workflow_run self re-trigger 의 GitHub Actions infinite loop risk + quota exhaustion risk 회피. boundary issue resolution = 신규 cross-cutting design pattern doc `docs/domain-knowledge/jsonl-write/race-condition-handling-pattern.md` 도입 — Pattern A (Contents API SHA-based optimistic concurrency, default), Pattern B (Long-lived branch + rolling PR, high-volume), Pattern C (File lock + retry, low-volume + simple). 모든 cross-repo jsonl write workflow = Pattern A 의무 (post-merge-telemetry.sh + retro-mandatory.yml + 미래 신설). git clone + bare push 패턴 금지 (lost-update risk)."
    status: applied
    ref: §D-4 + docs/domain-knowledge/jsonl-write/race-condition-handling-pattern.md
  - amendment_id: 2
    cfp: CFP-290
    date: 2026-05-09
    scope: "retro-attempts-state branch retention policy 추가 (Issue #295) — `retro-attempts-state/<KEY>` long-lived branch 의 보존 기간을 Story close 후 90일로 정의. cleanup trigger = `gate:retro-complete` label 부착 확인 + Story Issue close 확인 + 90일 경과. cleanup command = `git push origin --delete retro-attempts-state/<KEY>`. worktree GC hook (CFP-136 / ADR-040) cross-ref 의무 — `templates/scripts/check-worktree-stale.sh` 가 stale 판정 시 함께 prune. Pattern B (Long-lived branch) 채택 Story 에 적용."
    status: applied
    ref: §D-4 + §Amendments-2 (branch-retention)
  - amendment_id: 3
    cfp: CFP-290
    date: 2026-05-09
    scope: "§11.6 multi-runner race scenario informational mitigation enumeration (Issue #297) — Pattern A (Contents API SHA-based optimistic concurrency) 가 multi-runner concurrent write 를 처리함을 검증·문서화. CFP-138 security test 통과 근거: (1) SHA mismatch 시 409 Conflict 반환 → caller retry, (2) SHA collision 확률 무시 가능 (Git SHA-1 2^80 preimage resistance), (3) retro-attempts.jsonl write 경합 = last-writer-wins 없음 (모든 writer 가 최신 SHA fetch 후 CAS write). 코드 변경 불필요 — Pattern A 구현이 이미 이 보장을 내포. 검증된 동작을 ADR 에 informational note 로 기록."
    status: applied
    ref: §D-4 + §Amendments-3 (multi-runner-mitigation) + docs/domain-knowledge/jsonl-write/race-condition-handling-pattern.md
  - amendment_id: 4
    cfp: CFP-628
    date: 2026-05-14
    scope: "§D-5 신설 — Orchestrator 가 새 session 개시 시 mechanical scan 의무 (gh issue list + comment poll + created_at filter 35min) → 미해소 alert 발견 시 PMOAgent 자동 spawn. manual fallback retro 3 sample (CFP-609 + CFP-612 + CFP-610) 누적 evidence 해소."
    status: applied
    ref: §D-5 + CLAUDE.md SessionStart retro alert scan
    sunset_justification: null
  - amendment_id: 5
    cfp: CFP-665
    date: 2026-05-14
    scope: "§D-9 신설 — PMOAgent 가 retro write 시점 Cross-Story pattern 누적 ≥ 2 검출 시 ADR escalation trigger 의무화 (Mandatory framing). N=2 fixed threshold (industry lower bound: Google SRE / ITIL / NASA ASRS). hybrid 검출 전략 (primary = anchor_id strict / secondary = root_cause_class fallback). PMOAgent self-decide 영역 제거 — pmo-output-v1 v1.2 cross_story_pattern_adr_trigger field mandatory 채움 의무 (회피 불가). False positive 안전망 = escalation_action enum 2-value (adr_draft_emitted | escalate_user)."
    status: applied
    ref: §D-9 + pmo-output-v1 v1.2 + CLAUDE.md PMOAgent Cross-cutting
    sunset_justification: null
  - amendment_id: 6
    cfp: CFP-776
    date: 2026-05-17
    scope: "§D-9 cross_story_pattern_adr_trigger 적용 evidence (Amendment 5 forcing function 산물 기록) — CFP-746 retro §6 후보 1 (corpus-claim write-time verification) + CFP-770 retro §6 후보 1 (self-write artifact source/value/ownership claim write-time verification) = pattern_count 3 ≥ threshold 2 → Mandatory framing + escalation_action escalate_user → 사용자 단일 super-class ADR 통합 결정 (2026-05-16 KST) → ADR-082 (Write-time self-write verification mandate) 산출. §D-9 forcing function 이 'pattern 누적 → ADR escalation' 으로 실제 동작한 첫 cross-Story 산물 evidence. §D-9 결정 본문 / threshold / hybrid 검출 전략 의미 변경 없음 — evidence-only Amendment."
    status: applied
    ref: §D-9 + ADR-082 (산물) + Issue #776 pattern corpus 3건
    sunset_justification: null
  - amendment_id: 7
    cfp: CFP-1580
    date: 2026-05-25
    scope: "§D-9 cross_story_pattern_adr_trigger 적용 evidence (Amendment 5 forcing function 산물 기록 6번째) — pattern `wave2-mechanical-wire-design-review-skip` pattern_count 5 ≥ threshold 2 reach Mandatory (CFP-1489 / CFP-1497 / CFP-1500 / CFP-1502 / CFP-1539 5 precedent linear chain, all Wave 1 declarative anchor active 후 Wave 2 mechanical wire 영역에서 DesignReviewPL spawn 0 + 0 design FIX + 0 design review divergence detection + wrapper-self CodeReviewPL PASS + admin squash merge) → PMOAgent CFP-1539+1540 batch retro §6 escalation_action escalate_user → 사용자 결정 (2026-05-25 KST): Option A — Compress normative codify → ADR-068 Amendment 4 산물 (§결정 7 신설: Wave 2 mechanical wire 영역 design review skip 정합 invariant codify + Wave 1 declarative or 신규 ADR/governance 영역 mandatory retain). §D-9 forcing function 이 'pattern 누적 → ADR escalation' 으로 실제 동작한 6번째 cross-Story 산물 evidence (Amendment 6 CFP-776 ADR-082 carrier = 5번째 / 본 Amendment 7 = 6번째). §D-9 결정 본문 / threshold N=2 / hybrid 검출 전략 / escalation_action enum 2-value 의미 변경 없음 — evidence-only Amendment. paired sibling ADR-068 Amendment 4 (CFP-1580 §결정 7 신설 Wave 2 mechanical wire 영역 design review skip 정합 invariant declarative anchor)."
    status: applied
    ref: §D-9 + ADR-068 Amendment 4 (산물) + 5 precedent CFP linear chain (CFP-1489 / CFP-1497 / CFP-1500 / CFP-1502 / CFP-1539)
    sunset_justification: null
  - amendment_id: 9
    cfp: CFP-1623
    date: 2026-05-25
    scope: "§D-10 신설 — PMOAgent retro batch §6 ADR draft pre-publish 8-tuple verify-before-trust forcing function (paired sibling axis with §D-9 + Amendment 8 §D-9 sub-decision (b) 3-source AND verify). axis 분리 codify: §D-9 (Amendment 5 CFP-665) = post-hoc cross-Story pattern threshold 도달 시 ADR escalation forcing function (retro write 시점 pattern_count ≥ 2 → escalation_action enum mandatory) ↔ §D-9 sub-decision (b) (Amendment 8 CFP-1592 paired sibling) = 동일 axis 안 3-source AND verify-before-trust (retro batch §6 ADR draft 후보 작성 pre-publish 검증) ↔ 본 §D-10 (Amendment 9 CFP-1623) = pre-publish preflight 8-tuple expansion forcing function (PMOAgent retro file authoring path 안 §6 ADR draft section authoring 직전 8 independent verify sources AND gate, 1+ disagree → downgrade enum 2-value `downgrade_to_section_4_informational_only` 또는 `pivot_mark`). 8-tuple verify sources AND gate: (1) `git show origin/main:<ADR-path>` frontmatter amendment_log direct read (target ADR 영역 이미 amendment 추가 여부) / (2) `grep <feature-name> docs/evidence-checks-registry.yaml` (mechanical lint 이미 등록 여부) / (3) `Glob scripts/check-<feature-pattern>*` (실 script 이미 존재 여부) / (4) `gh pr list --search '<feature-name> in:title' --state merged` (sibling carrier merge status) / (5) `gh issue list --search '<feature-name> in:title' --state all` (existing CFP carrier 검색) / (6) `git log --all --oneline -- <path>` (file-level historical change presence) / (7) `Glob docs/adr/ADR-*.md` + frontmatter `amendment_log` cross-Story scan (recent amendment chain) / (8) retro §5 cross-Story pattern table 안 anchor_id ↔ existing implementation 매핑. Platform 한계 영역 처리 = `[verification-out-of-scope: <사유>]` marker (ADR-052 Amendment 3 marker 5종 정합 — gh CLI rate-limit / shallow clone). pmo-output-v1 v1.3 optional field 신설 `retro_section_6_pre_publish_verify` (3 sub-field: `verify_sources_attempted[]` enum / `verify_sources_blocked[]` 사유 / `downgrade_action` enum 2-value `null|to_section_4_informational|pivot_mark`) — Wave 1 declarative anchor scope, Wave 2 mechanical wire (scripts/check-retro-batch-adr-draft-pre-publish.py + workflow + evidence-checks-registry + label-registry MINOR + codeforge-pmo sibling sync) = 별 sub-CFP carrier defer. 동인 = ADR-045 §D-9 Mandatory escalation pattern_count 6 cumulative reach (Wave 1 CFP-1006 1 + Wave 3 batches CFP-1542/CFP-1558 2 + Wave 4 batches CFP-1604/CFP-1605/CFP-1606 3 = 6 ≫ threshold 2 = 3.0x) 100% retro-batch-origin PIVOT rate (5/5 batches stale catch, Wave 1 1/1 + Wave 3 2/2 + Wave 4 3/3). retro-batch-origin discriminator confirmed evidence (Wave 4 5/5 PIVOT rate retro-batch-origin Stories vs non-retro-batch 0/2 rate CFP-1603 / CFP-1607). §D-9 결정 본문 / threshold N=2 / hybrid 검출 전략 / escalation_action enum 2-value 의미 변경 0 — additive ratchet (sub-decision §D-10 신설). paired sibling carrier Amendment 8 CFP-1592 (§D-9 sub-decision (b) 3-source AND declarative anchor) → 본 Amendment 9 CFP-1623 (§D-10 신설 8-tuple expansion, sub-domain prerequisite mechanical layer). sequential dispatch convention 정합 (#1592 먼저 land → #1623 §D-10 sibling 후속, Story §7 권장)."
    status: applied
    ref: §D-10 + paired sibling Amendment 8 CFP-1592 (§D-9 sub-decision (b) 3-source AND) + Wave 4 pattern_count 6 cumulative evidence + retro-batch-origin discriminator
    sunset_justification: null
  - amendment_id: 10
    cfp: CFP-1632
    date: 2026-05-25
    scope: "§D-10 Wave 2 mechanical wire activation evidence (Amendment 9 CFP-1623 Wave 1 declarative anchor 발효 후 mechanical layer carrier) — evidence-only Amendment, ADR-045 §D-10 본문 wording 변경 0건 (Amendment 9 declaration source verbatim retain → Amendment 10 mechanical wire activation source split, CFP-1612 ADR-082 Amd 22→25 split precedent 답습 13-instance established pattern 13번째 instance). Wave 2 mechanical wire activation 구성 6 산출물: (a) `scripts/lib/check_retro_batch_adr_draft_pre_publish.py` Python SSOT (ADR-061 — retro file §6 ADR draft section auto-detect + 8-tuple verify source presence-grep + downgrade marker emission + PER_LANE_EVIDENCE_SCAN_CAP=30 line CodeQL ReDoS guard ADR-061 Amendment 3 §결정 11 정합 + FP guard 4종 templates/** + tests/** + retro path scope + §6 부재 silent skip + BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH=1 env unconditional skip) (b) `scripts/check-retro-batch-adr-draft-pre-publish.sh` bash thin wrapper (ADR-061 — POSIX dispatch only, exec Python SSOT) (c) `templates/github-workflows/retro-batch-adr-draft-pre-publish-check.yml` canonical workflow + `.github/workflows/retro-batch-adr-draft-pre-publish-check.yml` self-app mirror (ADR-005 byte-identical parity, warning tier continue-on-error + 3-trigger D2-extended split per spawn prompt AC #3 `pull_request: opened/synchronize/reopened` + `workflow_dispatch` + `schedule: cron '0 0 * * *'` 24h cron + permissions deny-all top-level ADR-060 Amendment 8 + concurrency group + bypass label check + bypass audit comment) (d) `tests/scripts/check-retro-batch-adr-draft-pre-publish/test_retro_batch_adr_draft_pre_publish.bats` + `fixtures/*.md` fixture cohort (8-tuple verify TC coverage TC-1~TC-8 + TC-9 8-tuple AND all PASS + TC-10 1+ disagree downgrade emission + TC-11 [verification-out-of-scope:] exemption + RED→GREEN stash proof per ADR-082 §결정 11.A + CFP-1334 §8.4 + 5 markers pre_impl_sha + git_stash_sequence + role_vocabulary + red_green_anchor + platform_verified) (e) `docs/evidence-checks-registry.yaml` entry append 132번째 sequential entry post-CFP-1612 (warning tier initial registration, owner_adr ADR-045-Amendment-9 declaration source + carrier_adr ADR-045-Amendment-10 Wave 2 mechanical wire activation source split, introduced_by CFP-1632, recurrence {count: 6, threshold: 2, promotion_trigger: warning}, sibling_dependencies [CFP-1592, CFP-1623, CFP-1632], status Active) (f) `docs/inter-plugin-contracts/label-registry-v2.md` MINOR bump v2.76 → v2.77 (`hotfix-bypass:retro-batch-adr-draft-pre-publish` 102번째 family member append, post-append raw active concrete grep count 101 + 1 = 102 정합 per ADR-108 §결정 3 forcing function parity META self-application) + `docs/inter-plugin-contracts/pmo-output-v1.md` MINOR bump v1.2 → v1.3 (`retro_section_6_pre_publish_verify` optional field codify 3 sub-field — `verify_sources_attempted[]` 8-enum + `verify_sources_blocked[]` platform exemption 사유 + `downgrade_action` enum 2-value `null|to_section_4_informational|pivot_mark`, additive v1.0/v1.1/v1.2 consumer 호환 ADR-008 §결정 2 backward-compat invariant 정합) + `docs/inter-plugin-contracts/MANIFEST.yaml` 2 row version field bump (label-registry-v2 + pmo-output-v1). Wave 1 (Amendment 9 CFP-1623) declaration-only Wave 2 (본 Amendment 10 CFP-1632) mechanical enforcement wire activation 분리 (CFP-967 / CFP-1437 / CFP-1436 / CFP-1435 / CFP-1539 / CFP-1559 / CFP-1578 / CFP-1581 / CFP-1590 / CFP-1589 / CFP-1612 → 본 CFP-1632 = 13번째 instance, established pattern). 강화 방향 only (Wave 1 declarative → Wave 2 mechanical wire activation, 약화 영역 0건 — forbid scope 확장 / threshold 약화 0 / sunset 0). META 21st applied case (ADR-082 §결정 1-K 4-step numeric claim write-time verify-before-write mandate self-execute, CFP-1612 post-rebase = 20th, 본 CFP-1632 = 21st recursive dogfooding self-evidence — §결정 1-K 4-step strict claim mandate META 21번째 적용). pattern_count ≥ N 추가 reach 시 warning → blocking-on-pr 승격 = Wave 3 별 carrier 분리 (ADR-060 §결정 6 promotion gate AND 3/3). evidence-only Amendment — ADR-045 §결정 본문 / §D-10 본문 / threshold / 8-tuple enum / downgrade_action enum 의미 변경 0건. paired sibling Amendment 9 CFP-1623 (Wave 1 declaration source retain invariant)."
    status: applied
    ref: §D-10 Wave 2 mechanical wire activation evidence (CFP-1632 carrier) + paired sibling Amendment 9 CFP-1623 Wave 1 declarative anchor retain invariant + 13-instance Wave 1→Wave 2 established pattern
    sunset_justification: null
    direction: strengthening
    nature: ratchet-up
  - amendment_id: 11
    cfp: CFP-1680
    date: 2026-05-26
    scope: "§D-11 신설 — PMOAgent retro batch closure pattern normative codify (HIGH normative consolidation carrier, doc-only fast-path ADR-054 Cat 1). 6 applied case evidence base (pattern_count 6 reach, threshold 2 = 3.0x): (1) CFP-963 retro 4-batch (Codex worker network_scope 영역) / (2) CFP-1339 retro 5-batch (6-CFP codify batch closure 정합) / (3) CFP-1612 retro 3-batch (Wave 2 mechanical wire activation paired sibling) / (4) CFP-1637 retro 3-batch (sub-domain followup closure) / (5) CFP-1648 retro deferred (pre-merge ABORT precedent — DEFER decision evidence) / (6) batch-close 2026-05-26 (6 follow-up closure, 본 Amendment 11 carrier 자체 retro). 4-option decision enum closed-set codify: `CLOSE_AS_OBVIATED` (recent carrier resolution direct merge link verify) / `CLOSE_AS_SENTINEL` (declarative monitor only, pattern_count not reached) / `PROMOTE` (pattern_count reached, active Story 발의 + label `priority:P1`) / `DEFER` (keep open, future carrier 대기, rationale 명시). 의무 영역 4 closed-set: (a) per-Issue body verbatim cite (재합성 0 — ADR-082 §결정 1 layer 1 sub-scope (1-C) USER-UTTERANCE-VERBATIM block 패턴 답습 PMOAgent retro batch closure 영역 sub-domain) (b) recent merge state direct verify (`gh api` + `git log` — ADR-073 verify-before-assert primitive 답습 PMOAgent batch closure 영역) (c) axis disjoint discrimination false-positive obviation 차단 (ADR-082 §결정 12 retro-time verify-before-trust 정합 batch closure 영역) (d) sibling carrier cross-link via PR number (ADR-082 §결정 9 verify-before-cite 양방향 답습 batch closure 영역) (e) sub-scope alphabet sequential verify (pre-write 위치 확인 — ADR-082 §결정 1 sub-scope codify 패턴 답습). Closure summary table format SSOT 5-column (`Issue / Tier / Decision / Final state / Comment URL`) — ADR-068 I-4 wording SSOT invariant 정합 batch closure 영역. Cross-Story pattern_count progression table (pre-batch / post-batch / threshold / status) + Net escalation 0 시 `cross_story_pattern_adr_trigger` field empty — ADR-045 §D-9 escalation 영역 disjoint axis (pre-publish vs post-batch closure 명확 분리). Closure forcing function 3 step: (1) 각 Issue 별 `[PMO]` prefix comment + state transition (2) Retro PR open + auto-merge closure evidence trail (ADR-045 §결정 4 retro PR 자동 merge 정합) (3) `gate:retro-complete` label add OR `not_planned` reason close (ADR-045 §결정 5 close-blocking 정합). META 24th applied case (ADR-082 §결정 1-K 4-step numeric claim write-time verify-before-write mandate self-execute, CFP-1632 = 21st / CFP-1648 = 22nd / CFP-1637 = 23rd / 본 CFP-1680 = 24th — pattern_count 6 reach 자체 verify-before-write self-execute recursive dogfooding self-evidence). Wave 1 → Wave 2 split precedent 적용 영역 외 (batch close = governance status update, mechanical wire 영역 disjoint — declarative anchor only). META forward-prevention via verify-before-trust 5 sub-scope mandate (a~e 위 enumerate). ratchet ↑ direction — ADR-058 §결정 5 면제 (강화 방향 only, forbid scope 확장 / threshold 약화 0 / sunset 0). paired sibling carrier = playbook §18 (batch close operating sequence 5 sub-section codify). doc-only fast-path ADR-054 Cat 1 — 1 PR per repo, src/tests 무변경. 본 Amendment 11 = normative consolidation Story 자체가 batch close pattern 7th applied (self-reference recursive dogfooding META invariant 보존)."
    status: applied
    ref: §D-11 + playbook §18 (paired sibling) + 6 applied case evidence chain (CFP-963 / CFP-1339 / CFP-1612 / CFP-1637 / CFP-1648 / CFP-1680 batch-close 2026-05-26)
    sunset_justification: null
    direction: strengthening
    nature: ratchet-up
  - amendment_id: 12
    cfp: CFP-2330
    date: 2026-06-18
    scope: "§D-9 sub-decision (c) 신설 — Pattern A (chief-author self-attest false claim) 반응형(reactive)→예방형(preventive) merge-time gate-provenance self-attest forcing function (additive ratchet, sub-decision (a)/(b) RETAIN, §D-9 본문 의미 변경 0건). Epic CFP-2324 S6 carrier (escalation #2322 흡수). 기존 §D-9 (a) post-detection escalation + (b) pre-publish 3-source AND verify 는 PMOAgent retro-time 영역. 본 (c) = gate verdict write-time 영역 (Orchestrator self-write gate-pass label/comment 직전 self-attest preventive gate). axis 분리: (a)/(b) = retro corpus / ADR draft 영역 ↔ (c) = gate verdict provenance 영역 (disjoint). carrier source = CFP-1353 Pattern A 'chief author self-attest false claim' pattern (명칭 SSOT = docs/agent-prompt-guardrails.md:26, Pattern A-2 = InfraEng FIX iter 1 false self-attest tests_passed 19/19 vs actual 10/27). 기존 ADR-082 §결정 1 (write-time self-write verify) + ADR-073 (verify-before-assert) 는 author 가 자기 claim 을 스스로 verify 하는 self-discipline layer = 반응형 (위반해도 검출 시점 = downstream review/retro). 본 (c) = merge-time mechanical preventive gate — gate verdict 가 (1) lane-produced machine-checkable artifact (review-verdict-v4 packet 형식 준수 + 필수필드 contract_version/lane/story_key/iteration/pl_recommendation 존재) ∧ (2) Story §14 lane-evidence binding (해당 lane row 존재 + output_status/outcome 정합) multi-anchor AND 충족 시에만 정당. wrapper-self `mixed` repo = ADR-031 §결정 (Amendment, mixed repo §14 면제) 라 §14 anchor 대신 PR body/코멘트 review-verdict packet 병행 anchor 로 충당. multi-anchor AND 3-source 패턴 = ADR-026 §결정 6 isPostMergeFix (label ∧ Story §10 binding ∧ §7 보안 non-touch) 답습 — single point of forgery 제거 mechanism. 위협모델 = honest-but-careless (연극 게이트 / 실수로 빈 verdict 부착 / artifact 부재인데 gate-pass label 부착). 악의 단일계정 위조 (single-session·single-account = git author 기반 implementer≠certifier separation 불가) = out-of-scope accepted risk 명시 박제 (mitigation 비용 > 이득, dogfood wrapper-self 환경 single-operator). 적용 = 모든 게이트 (요구사항리뷰 [ADR-125 신규 lane, S2 self-attest 구멍 공동 차단] / 설계리뷰 / 보안테스트 / 배포리뷰). posture = warning-first → ratchet — Phase 1 = declarative anchor (본 sub-decision 신설 + multi-anchor AND schema codify), Phase 2 = advisory CI 경고 (mechanical wire, gate-pass label 부착 PR 에서 multi-anchor 부재 시 warning emit + PR comment, merge 미차단). hard-block 승격 = 별 follow-up Story (ADR-060 §결정 6 promotion gate AND 3/3 충족 후, ratchet 강화 방향). gate label authority SSOT = 기존 (ADR-022 §결정 4 review-verdict gate outcome contract + base-labels.tsv gate:* registry) — 신규 gate-provenance ADR 발의 안 함 (3문 게이트: 신규 ADR 비용 > 이득, ADR-045 §D-9 sub-decision 확장으로 충분). ratchet ↑ direction (강화 방향 only, sub-decision (a)/(b) 의미 변경 0 / threshold 약화 0 / sunset 0) — ADR-058 §결정 5 면제. Wave 2 mechanical wire (advisory CI warning) = 별 sub-CFP / S6 Phase 2 carrier defer. paired sibling = S7 (CFP-2331, ADR-014 Amendment 6) 동일 Epic gate-model 일관 설계 묶음 (phase-gate-mergeable.yml 게이트 매핑 공유)."
    status: applied
    ref: §D-9 sub-decision (c) + carrier source CFP-1353 Pattern A (docs/agent-prompt-guardrails.md:26) + ADR-026 §결정 6 multi-anchor AND 답습 + ADR-031 §14 lane-evidence binding + ADR-022 §결정 4 gate authority cross-ref
    sunset_justification: null
    direction: strengthening
    nature: ratchet-up
  - amendment_id: 13
    cfp: CFP-2377
    date: 2026-06-20
    scope: "§D-12 신설 — phase:완료 transition precondition 에 worktree-clean self-check 추가 (gate:retro-complete close-blocking 골격 확장, ADR-128 완료 단계 정식화 묶음 carrier, additive ratchet). 기존 phase:완료 precondition = 2-gate AND (활성 lane terminal gate `gate:design-review-pass`/`gate:deploy-review-pass` + `gate:retro-complete`, playbook §9.7.1 line 2858 SSOT). 본 Amendment 13 = precondition 에 worktree-clean self-check 1항 추가 → 2-gate AND + worktree-clean self-check. worktree-clean = '완료 Story 의 worktree 가 eager 정리됐는가' (eager 미실행 검출 게이트, 정리 실행 owner=GitOpsAgent eager 불변 — 본 게이트는 검증만). tier = Orchestrator behavioral precondition (로컬 self-write) — phase:완료 transition = Orchestrator self-write + worktree 클라우드 러너 미접근이라 required CI check 불가 (AC-2/AC-12). 3-조합 기계화 = (a) playbook §9.7.1 precondition 행 + (b) 로컬 check 스크립트 scripts/check-worktree-completion-clean.sh (Phase 2) + (c) evidence-checks-registry warning-tier `workflow: null` (ADR-099/ADR-122 local-only 선례). data-loss hard-block 금지 (fail-safe 4종 상속 — ADR-040 Amendment 9 §결정 7.K). close lifecycle 무영향 = worktree-clean self-check 는 transition precondition (label attach 직전)이지 Issue close 차단(reopen)이 아님 → retro-mandatory.yml gate:retro-complete close-blocking auto-reopen 과 axis disjoint (#772 EC-5 정합, 중복 reopen 0). branch protection 6-tuple 무변경 (신규 required check 0 → ADR-024 Amendment 19 §B bypass 신설 금지 invariant 원천 정합). ADR-045 §결정 5 close-blocking + §D-6 gate:retro-complete entry 의미 변경 0건 (precondition 1항 추가만). paired sibling carrier = ADR-040 Amendment 9 (backstop SessionEnd async 트리거 복원 + §결정 7.K worktree-clean cleanup invariant) + ADR-128 (완료 단계 정식화 umbrella). gate label authority SSOT = 기존 (ADR-022 §결정 4 gate outcome contract) — 신규 gate:worktree-clean label 신설 안 함 (사용자 방향 '기존 게이트 확장', label 없이 Orchestrator self-check). ratchet ↑ direction (강화 방향 only, §결정 1-8 + §D-9~D-11 의미 변경 0 / threshold 약화 0 / sunset 0) — ADR-058 §결정 5 면제. Wave 2 mechanical wire (로컬 check 스크립트 + evidence-registry entry) = Phase 2 carrier."
    status: applied
    ref: §D-12 + paired sibling ADR-040 Amendment 9 (§결정 7.K worktree-clean cleanup invariant) + ADR-128 (완료 단계 정식화 umbrella) + playbook §9.7.1 line 2858 precondition + ADR-099 workflow:null local-only 선례
    sunset_justification: null
    direction: strengthening
    nature: ratchet-up
  - amendment_id: 14
    cfp: CFP-2392
    date: 2026-06-24
    scope: "§D-13 신설 — phase:완료 transition precondition 에 capture self-check 추가 (완료시점 재사용지식 외부화 게이트, ADR-129 OMC-adopt 지식캡처 묶음 carrier, additive ratchet). ADR-128 Amendment 13 §D-12 worktree-clean self-check 와 동형 구조 (둘 다 phase:완료 local-only warning-tier self-check). 기존 phase:완료 precondition = 2-gate AND + worktree-clean self-check (§D-12) → 본 Amendment 14 = capture self-check 1항 추가. capture self-check = '이번 Story 에서 재사용 가능한 지식이 외부화됐는가' — capture artifact (신규 skills/<slug>/SKILL.md 또는 docs/domain-knowledge/.../*.md) OR 명시적 no-capture note('캡처 대상 검토 완료 — 외부화 불요(사유)' 1줄) 흔적 검사. 둘 다 부재 = WARN (silent skip 금지, forced-no-silent-skip). 3문 admission(구글5분/코드베이스특정/실제노력) 자체 판정 = semantic(behavioral, Orchestrator self-eval), lint 은 '흔적 존재'만 presence 검사. tier = Orchestrator behavioral precondition (로컬 self-write) — phase:완료 transition = Orchestrator self-write + 완료 marker working-tree 검출이라 required CI check 불가. 3-조합 기계화 = (a) playbook §9.7.2 완료 단계 수렴 SSOT capture self-check pointer + (b) 로컬 check 스크립트 scripts/check-capture-gate-completion.sh (Phase 2) + (c) evidence-checks-registry warning-tier knowledge-capture-completion-gate workflow:null (ADR-099/ADR-122/ADR-128 local-only 선례). data-loss hard-block 금지 (git/gh 미인증 시 exit 0 보존). close lifecycle 무영향 (worktree-clean §D-12 동형 — transition precondition 이지 Issue close 차단 아님). branch protection 6-tuple 무변경 (신규 required check 0 → ADR-024 Amendment 19 §B bypass 신설 금지 invariant 원천 정합). ADR-045 §결정 5 close-blocking + §D-6/§D-12 entry 의미 변경 0건 (precondition 1항 추가만). paired sibling carrier = ADR-071 Amendment 12 (§18.7 MEMORY.md 슬림화 mechanism deferred 해제) + ADR-129 (OMC-adopt 지식캡처+메모리다이어트 umbrella). gate label authority SSOT = 기존 (ADR-022 §결정 4) — 신규 gate:capture label 신설 안 함 (ADR-128 §D-12 worktree-clean label 미신설 패턴 답습). axis-disjoint vs §D-9 retro: TIMING(pre-completion vs post-hoc) / UNIT(single-task vs multi-Story) / OUTPUT(skill·domain-knowledge artifact vs ADR escalation) 3축 disjoint → §D-9 흡수 불가, ADR-129 NEW umbrella (ADR-128 archetype 답습). ratchet ↑ direction (강화 방향 only, §결정 1-8 + §D-9~D-12 의미 변경 0 / threshold 약화 0 / sunset 0) — ADR-058 §결정 5 면제. Wave 2 mechanical wire = Phase 2 carrier."
    status: applied
    ref: §D-13 + paired sibling ADR-071 Amendment 12 (§18.7 MEMORY.md 슬림화 deferred 해제) + ADR-129 (OMC-adopt 지식캡처+메모리다이어트 umbrella) + ADR-128 §D-12 worktree-clean self-check 동형 + playbook §9.7.2 완료 단계 수렴 SSOT + ADR-099/ADR-122/ADR-128 workflow:null local-only 선례
    sunset_justification: null
    direction: strengthening
    nature: ratchet-up
is_transitional: false
---

# ADR-045: Story 완료 회고 의무화 — Phase 2 PR merge 후 PMOAgent 자동 trigger

## 상태

**Proposed (2026-05-09)** — CFP-138 carrier. CFP-134 Epic 의 Wave 2 child Story (D5 Foundation 결정 implementation). Phase 1 PR merge 시 `Accepted` 전환.

본 ADR 의 spec SSOT = [`mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md) §4.3 (CFP-138 부분).

## 컨텍스트

사용자 directive 2026-05-08 (CFP-134 brainstorming spec turn 9, verbatim):

> "story 완료 회고는 사용자 요청이 없어도 의무로 수행한다."

추가 framing (turn 7-8 정합):

> "codex review와 sonnet decider를 codeforge의 일환으로 보는 것 같은데 그건 아니다. 사용자 stop이 너무 많아 내가 필요할 때마다만 요청하는 것이지 codeforge가 이를 반영해서 임의로 수행해서는 안된다."

### 현재 상태

- ADR-035 D5 (Foundation 결정) — "PMOAgent 가 Phase 2 PR merge 후 retro 자동 trigger (사용자 요청 불필요). `gate:retro-complete` label 신설 — 미작성 시 Story close 차단" 명시. Implementation = CFP-138 carrier (본 ADR).
- ADR-026 post-merge-followup.yml = 4-action workflow + telemetry-only mode + idempotent + disable-by-flag (`/.codeforge/post-merge-automation.disabled`). 본 ADR 가 5번째 action 추가 또는 **별도 workflow 분리** 결정.
- codeforge-pmo PMOAgent.md = `Edit(docs/retros/**)` + `Edit(docs/stories/**)` + `mcp__github__issue_write` 권한 보유. 새 권한 추가 불필요.
- Story file template `templates/story-page-structure.md` §11 = `- 회고 (PMOAgent 작성)` vague placeholder line 157. schema 갱신 필요.
- `templates/github-workflows/phase-label-invariant.yml` `enforce-terminal-on-close` job = closed event terminal phase 검증 + comment alert (auto-reopen 안 함). retro 의무 별도 workflow 분리 정합.

### Gap

1. **retro automation timing 미정의** — Story close 시점 vs Phase 2 PR merge 시점. ADR-026 post-merge-followup.yml Action 3 (Issue close) 와 race condition 우려.
2. **doc-only Story 의 retro 의무** — Phase 2 PR 부재 시 trigger window 미정의.
3. **partial-write protocol 부재** — PMOAgent retro write 일부 실패 (Epic milestone API fail / network) 시 처리.
4. **Story §11 schema vague** — 현재 `- 회고 (PMOAgent 작성)` = 비-structured. machine-readable 검증 불가.
5. **PMOAgent mandate amendment 부재** — codeforge-pmo CLAUDE.md "Story 완료 시 → 회고 감사" trigger 가 ad-hoc 또는 자동 명시 부재.

## 결정 (D-1 ~ D-8)

### D-1 — Trigger timing = Phase 2 PR merge 직후 + 5분 grace

**결정**: retro-mandatory.yml workflow trigger = `pull_request closed event` (merged=true) + Phase 2 marker (PR title regex `Phase 2` OR `phase:보안-테스트` PR label). 5분 grace period 내 PMOAgent retro write 시간 부여.

5분 grace 후 `gate:retro-complete` label 부재 검출 시 close-blocking 동작 (Issue close 시도 시 자동 reopen + `[PMO]` prefix comment).

**거절된 대안**:
- (b) Story Issue close 시점 trigger — race condition (post-merge-followup.yml Action 3 도 Issue close 시점에 trigger, 동시 발화 시 sequence 불명확)
- (c) `gate:security-test-pass` label 부착 시점 trigger — Phase 1 PR merge 후 phase:설계-리뷰 → phase:구현 transition 영역과 분리 안 됨

**근거**: Issue body §1.3 verbatim "Phase 2 PR merge 완료 → 자동으로 TEAM-RETRO spawn" 정합. 5분 grace = workflow 단일 실행 안 sleep step 또는 scheduled cron retry 영역 (D-4 partial-write protocol 정합).

**Implementation**: retro-mandatory.yml workflow `on: pull_request: types: [closed]` + `if: github.event.pull_request.merged == true` + Phase 2 marker check + `sleep 300` step 또는 별도 scheduled trigger.

### D-2 — Workflow 분리 = 별도 retro-mandatory.yml 신설 (post-merge-followup.yml 미터치)

**결정**: ADR-026 의 post-merge-followup.yml Action 5 추가 안 함. **별도 `templates/github-workflows/retro-mandatory.yml` 신설**.

**거절된 대안**:
- (b) post-merge-followup.yml 안 Action 5 추가 — single-responsibility 위반. 4 action 모두 PR merge 시점 즉시 발화 (continue-on-error + outcome aggregation), retro 는 5분 grace + 2 retry max — trigger window 다름.
- (c) post-merge-followup.yml 안 별도 job 추가 — workflow 안 multi-job 시 disable-by-flag check + telemetry 정합 복잡화.

**근거**:
- single-responsibility — post-merge-followup = 4 즉시 action, retro-mandatory = 5분 grace + retry + close-blocking
- ADR-026 §결정 4 disable-by-flag invariant 보존 — 두 workflow 모두 같은 flag (`.codeforge/post-merge-automation.disabled`) 검사 가능 (D-7 정합)
- retry 시 4 action 동시 재실행 = idempotent invariant 위반 risk (post-merge-followup 의 phase label transition + Issue close 등은 1-shot 의도)
- ADR-026 patterns mirror 가능 (workflow concurrency / continue-on-error / cross-repo PAT / outcome aggregation) — 재발명 회피

**Implementation**: 신규 `templates/github-workflows/retro-mandatory.yml` 작성 + self-app `.github/workflows/retro-mandatory.yml` parity (`scripts/check-workflow-parity.sh` 정합).

### D-3 — Doc-only Story retro 의무 = 모든 Story 적용

**결정**: Phase 1 PR + Phase 2 PR 일반 패턴 + ADR-027 Amendment 1 doc-only Story (Phase 1 단독) 모두 retro 의무. 단 doc-only Story 의 trigger window 는 **Phase 1 PR merge 시점** (Phase 2 부재 시).

**거절된 대안**:
- (b) doc-only Story 면제 — Story-level 일관성 약화. 미래 doc 변경 retroactive audit 시 retro 부재로 학습 누적 부족.

**근거**: Story-level 일관성 우선. doc-only Story 도 retro write 의무 (간단 retro 라도). retro file = `<sprint>-cfp-NNN-<slug>.md` naming — Phase 1 PR merge 시점에 작성 가능.

**Implementation**: retro-mandatory.yml workflow 가 Phase 2 marker 부재 시 fallback = Phase 1 PR merge + Story Issue close 시점 trigger. 또는 doc-only Story = `phase:보안-테스트` 도달 시점 (Phase 1 PR merge 후 phase progression 가능). 본 ADR 결정 = doc-only Story 도 retro 의무.

### D-4 — Partial-write protocol = 4 attempts (1 initial + 3 retries) + ESCALATE + close-blocking 유지

**결정**: PMOAgent retro write 시 partial failure (예: retro file write 성공 + Story §11 update 성공 — Epic milestone API 호출 fail) 발생 시 retry policy.

**Cumulative offset spec from PR merge timestamp** (verbatim — 6 source sync SSOT, FIX iter 1 F-1 fix):

| Attempt | Wait from previous | Cumulative offset from PR merge | Action |
|---|---|---|---|
| **First attempt** (initial) | — (5min grace) | **+5min** | PMOAgent retro write 시도 |
| **Retry 1** | +5min wait | **+10min** | gate:retro-complete 부재 검출 시 PMOAgent re-spawn |
| **Retry 2** | +10min wait | **+20min** | gate:retro-complete 부재 검출 시 PMOAgent re-spawn |
| **Retry 3** | +15min wait | **+35min** | gate:retro-complete 부재 검출 시 PMOAgent re-spawn (final attempt) |
| **ESCALATE** | — | **+35min** 후 | retry 3 fail 시 `[PMO] Retro automation failed after 3 retries — 사용자 ESCALATE` comment + `gate:retro-complete` 미부착 (Story close 차단 유지) |

**Total attempts = 4** (1 initial + 3 retries).
**Total max latency from PR merge to ESCALATE = 35min** (5min grace + 5+10+15 retry waits).

35min 후 Story close 차단 유지 + 사용자 manual 복구 후 PMOAgent re-spawn → 정상 경로 복귀.

**거절된 대안**:
- (b) retry 1회 + ESCALATE — transient failure (network blip / GitHub API 5xx) 자동 복구 부족
- (c) infinite retry — DoS risk (PR 다수 merge 시 worker thread 누적)
- (d) close-blocking 해제 — silent failure 차단 무력화 (mandate forcing function 의미 상실)

**근거**: 5min grace = first attempt budget. 5/10/15 wait = 점진 증가 (exponential backoff lite). 35min max latency 후 사용자 ESCALATE = silent failure 차단 정합.

**Idempotency invariant** (§11.6 cross-ref): 매 attempt 가 idempotent — retro file 존재 검사 (PMOAgent re-spawn 시 existing file 검출 + abort 또는 append) + `gh label add` no-op (이미 부착 시) + Issue close-blocking auto-reopen idempotent comment (EXISTING_ALERT check, retro-mandatory.yml workflow 안).

**Phase 2 implementation spec** (F-5 fix — DesignReview iter 1 P1, Phase 2 PR scope):
- **State management mechanism**: `<internal-docs>/wrapper/retro-attempts.jsonl` (Phase 2 신설, ADR-026 post-merge-counters.jsonl 와 별도 channel). per-Story attempt counter 누적 — schema = `{story_key, pr_ref, attempt_n: 1|2|3|4, last_attempted_at: ISO8601, status: in_flight|success|failed|escalated}`.
- **Re-trigger mechanism (Phase 1 follow-up amendment_id=1, FIX iter 2 boundary resolution)**: **scheduled cron `*/5 * * * *` 단독 사용** (workflow_run trigger 제거 — workflow_run self re-trigger 의 GitHub Actions infinite loop risk + quota exhaustion risk 회피). cron + retry-state-machine job 가 retro-attempts.jsonl state 검사 후 due retry dispatch. 거절된 alternative: "workflow_run + cron both enabled with infinite loop guard" (`if: github.event.workflow_run.name != 'self'` 등) — complexity 증가 + edge case 다수 (workflow_run.conclusion 다양 + race condition retry 발화 + GitHub Actions runtime quota burn) → cron 단독 = 단순성 + safety + 5min latency overhead 무시 가능 채택. Phase 1 PR scope 에서는 first attempt (5min grace) 만 implement — retry 영역 = Phase 2 PR scope.
- **Concurrent jsonl write race handling** (boundary issue resolution, FIX iter 2 amendment_id=1): retro-attempts.jsonl 의 모든 cross-repo write (4 git push points = first attempt write + retry-state-machine 의 success/failed/escalated status update) = **Pattern A (Contents API SHA-based optimistic concurrency) 의무** — 신규 cross-cutting design pattern doc `docs/domain-knowledge/jsonl-write/race-condition-handling-pattern.md` SSOT. ADR-026 post-merge-counters.jsonl 도 동일 Pattern A mirror (post-merge-telemetry.sh 가 이미 implementation 정합). git clone + bare push pattern 금지 (lost-update risk — concurrent push 시 second push fail without recovery, silent telemetry loss).
- **Max attempts state machine**: 4번째 attempt fail 시 `escalated` state 진입 + ESCALATE comment + close-blocking 유지.

Phase 1 PR scope (본 ADR carrier) = first attempt 5min grace + close-blocking action 만. retry state machine = Phase 2 PR scope deferred.

### D-5 — Story §11 schema migration = 신규 Story 부터 적용 (backward compat)

**결정**: `templates/story-page-structure.md` §11 schema 갱신 — 현재 `- 회고 (PMOAgent 작성)` line 157 vague placeholder → 4 field structured:

```markdown
- 회고 (PMOAgent 작성):
    retro_file: <relative-path-or-cross-repo-url>
    retro_summary: <one-paragraph-summary, max 500자>
    learnings_count: <integer >= 0>
    feedback_back_to_codeforge: <Issue link list or empty []>
```

**Migration**: 신규 Story (CFP-138 merge 이후 close) 부터 신규 schema 적용. 기존 close Story file 100+ 의 §11 영역 = `- 회고 (...)` 불완전 string 유지 (retroactive 미처리).

**Backward compat 검증**: `scripts/check-doc-section-schema.sh` 가 PMOAgent owner section 검증 — Story frontmatter `created_at >= CFP-138 merge date` 또는 status:open at CFP-138 merge time 검출 시 strict mode. 그 외 lenient mode (vague placeholder OK).

**거절된 대안**:
- (b) 모든 close Story retroactive backfill — 100+ Story 변조 risk + Story §1 verbatim invariant 위반 risk
- (c) schema 미터치 (vague placeholder 유지) — machine-readable 검증 불가

**근거**: Issue body §1.3 verbatim "retroactive 미처리" 정합 + ADR-013 dogfood-out / append-only invariant 정합.

### D-6 — label-registry MINOR bump = v1.4 → v1.5 (gate:retro-complete entry)

**결정**: `docs/inter-plugin-contracts/label-registry-v1.md` v1.4 → v1.5 (additive minor, ADR-008 SemVer 정합). `gate:retro-complete` entry 추가:

```yaml
- name: gate:retro-complete
  category: gate
  color: "0e8a16"
  description: "Story 완료 회고 작성됨 (PMOAgent self-write — CFP-138 / ADR-045 mandate)"
  single_active: false
  attach_owner_plugin: "codeforge-pmo (PMOAgent self-write)"
```

`scripts/bootstrap-labels.sh` 에 `create_label "gate:retro-complete" "0e8a16" "..."` 1줄 append + line 51 echo "29종" → "30종" 갱신.

**Idempotency invariant**: `gh label create ... 2>/dev/null || gh label edit ... 2>/dev/null` 패턴 유지 — 기존 30+ label 무수정.

**MANIFEST.yaml** entry version update (label-registry-v1: "1.4" → "1.5").

**거절된 대안**:
- (b) MAJOR bump v2.0 — 기존 label 삭제 / rename 없음 (additive minor 충분)

**근거**: ADR-008 SemVer (additive minor). consumer breaking 없음 — 기존 label 유지.

### D-7 — Disable-by-flag safety = `.codeforge/post-merge-automation.disabled` 단일 flag 공유

**결정**: retro-mandatory.yml workflow 도 ADR-026 와 동일한 `.codeforge/post-merge-automation.disabled` flag 검사. 두 workflow 모두 같은 flag 단일 disable.

**거절된 대안**:
- (b) 별도 flag `.codeforge/retro-mandatory.disabled` — 운영 복잡성 증가, ADR-026 §결정 4 invariant 의 simplicity 정합 약화

**근거**: ADR-026 §결정 4 invariant (운영 emergency 안전망) 정합. 단일 flag = post-merge automation 전체 disable (4 action + retro mandate 양쪽). 부분 disable 필요 시 workflow yaml 직접 수정 (별도 PR).

### D-8 — Sibling sync 의무 = codeforge-pmo plugin Phase 1 PR pair

**결정**: ADR-010 sibling sync — wrapper Phase 1 PR 와 codeforge-pmo plugin Phase 1 PR 같은 Story 안 같이 merge 의무.

**Sibling 영역**:
- codeforge-pmo `CLAUDE.md` "Self-write 책임" 표 — `docs/retros/<sprint>.md` row trigger 컬럼 amendment (`story_completion (Phase 2 PR merge 자동, CFP-138) / cross_story_audit_request`)
- codeforge-pmo `agents/PMOAgent.md` 호출 시점 표 amendment (line 56-60 — `Story 완료 시 (Phase 2 PR merge 후 5분 grace, CFP-138 자동 trigger)`)
- codeforge-pmo `agents/PMOAgent.md` 책임 상세 §2 Story 완료 회고 감사 영역 → mandate 자동 trigger 명시

**거절된 대안**:
- (b) wrapper-only PR — codeforge-pmo plugin 정합 부재 시 PMOAgent agent file invalid (mandate amendment 미반영, agent 가 자기 역할 trigger 모름)

**근거**: ADR-010 cross-plugin sibling sync 정합. Phase 1 PR pair = same Story 안 ATOMIC merge.

## 대안 검토

### 대안 A — Workflow 통합 (post-merge-followup Action 5 추가, β)

- post-merge-followup.yml 의 4 action 후 Action 5 (gate:retro-complete check + close-blocking) 추가
- 거부 사유:
  - single-responsibility 위반
  - retry 시 4 action 동시 재실행 = idempotent 위반 risk
  - 5분 grace + 2 retry max trigger window 가 즉시-실행 4 action 와 다름
  - D-2 결정 정합

### 대안 B — Story Issue close 시점 trigger (γ)

- post-merge-followup.yml Action 3 가 Issue close 후 retro 검증
- 거부 사유: race condition (Action 3 와 retro 검증 동시 발화 시 sequence 불명확). D-1 결정 정합.

### 대안 C — Retroactive backfill (δ)

- 본 ADR merge 후 기존 close Story 100+ 에 retro 작성
- 거부 사유:
  - Story §1 verbatim invariant 위반 risk (PMOAgent edit 시 §1 line range 변조 우려)
  - 100+ Story 변조 risk
  - Issue body §1.3 verbatim "retroactive 미처리" 정합
  - 별도 backfill CFP 가능 (선택 — out-of-scope)

### 대안 D — Doc-only Story 면제 (ε)

- doc-only Story (Phase 2 부재) retro 의무 면제
- 거부 사유: Story-level 일관성 약화. D-3 결정 정합.

## 결과

긍정:
- ADR-035 D5 Foundation 결정 implementation 충족
- 사용자 directive (turn 9) verbatim 정합
- ADR-022 Deprecated (Sonnet decider 자동 발동 무효) framing 와 같은 Wave 2 진행
- ADR-026 post-merge-followup.yml 미터치 (single-responsibility 보존)
- bootstrap-labels.sh idempotency 보존 (기존 30+ label 무수정)
- backward compat (기존 Story file retroactive 미처리)
- forcing function 동작 (close-blocking + 4 attempts (1 initial + 3 retries) + 35min max latency + ESCALATE)

부정:
- 5min grace + 4 attempts (1 initial + 3 retries) cumulative = 35min max latency — 정상 경로에서 retro write 첫 attempt 성공 시 0-5min (acceptable)
- Story close 시점 다소 지연 (5분 grace + PMOAgent spawn time)
- Cross-repo PAT (CODEFORGE_CROSS_REPO_PAT) expiration 의존 — ADR-026 §결정 2 90d runbook 정합
- Doc-only Story trigger window 정의 복잡 (Phase 2 marker fallback) — D-3 implementation 정밀화 의무

### Reversibility

Yes. Rollback 경로:

1. **즉시 disable**: `.codeforge/post-merge-automation.disabled` flag 활성 → 양 workflow no-op
2. **단계적 revert**:
   - retro-mandatory.yml 삭제 (workflow disable)
   - label-registry-v1 v1.5 → v1.4 revert (gate:retro-complete entry 삭제)
   - bootstrap-labels.sh `gate:retro-complete` 1줄 revert
   - story-page-structure.md §11 schema revert (`- 회고 (PMOAgent 작성)` line 복구)
   - codeforge-pmo CLAUDE.md + agents/PMOAgent.md amendment revert
   - ADR-045 status: Accepted → Deprecated
3. **이미 운영 중인 retro file 보존** (audit trail 유지) — append-only invariant 정합
4. **이미 부착된 `gate:retro-complete` label** = leave as-is (label 자체 GitHub 측 잔존, registry revert 후 무영향)

## Out-of-scope

- retro file schema 강화 / quality lint (현재 `templates/retro.md` schema 그대로 사용) — 별도 follow-up CFP
- Consumer-side retro mandate 도입 가이드 — `docs/consumer-guide.md` 후속 안내 (별도 CFP, debut audit 후)
- Retroactive backfill — 본 ADR 도입 이전 close 된 Story 100+ 의 retro 작성 (D-5 정합)
- Hotfix 경로 retro 의무 — `docs/hotfix-playbook.md` amendment 별도 CFP
- TEAM-RETRO 의 agent teams 활성 (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) 의존성 — 본 ADR 는 default subagent context 에서도 동작 (Orchestrator → PMOAgent subagent spawn one-shot 패턴)
- EC-5 사용자 manual edit policy (retro file append-only / immutable) — KB 신설 후보 (`docs/domain-knowledge/retro-flow/manual-override-policy.md`), 별도 CFP

## Amendments

### Amendment 2 — `retro-attempts-state` branch retention policy (CFP-290 / Issue #295)

**문제**: ADR-045 D-4 §Phase 2 implementation spec 에서 Pattern B (Long-lived branch + rolling PR) 를 선택한 Story 의 경우 `retro-attempts-state/<KEY>` long-lived branch 가 생성된다. 그러나 해당 branch 의 보존 기간·삭제 트리거·삭제 명령이 어디에도 정의되지 않아 브랜치가 무기한 잔존하는 리포지터리 오염이 발생할 수 있다.

**결정**: `retro-attempts-state/<KEY>` branch 보존 기간 = **Story close 후 90일**. 아래 조건 모두 충족 시 삭제 의무:

1. `gate:retro-complete` label 부착 확인 (retro 정상 완료 증거)
2. Story Issue close 확인
3. Story close timestamp 로부터 90일 경과

**Cleanup command**:

```bash
git push origin --delete retro-attempts-state/<KEY>
```

**Worktree GC hook cross-ref (ADR-040 / CFP-136)**: `templates/scripts/check-worktree-stale.sh` 가 stale worktree 판정 기준 (7 days + origin absent) 에 따라 prune 할 때, 동일 `<KEY>` 의 `retro-attempts-state/<KEY>` remote branch 도 함께 정리 대상으로 포함. 단 worktree GC = 7 day stale 기준, branch cleanup = 90 day — 두 기준은 독립 (worktree GC 가 branch cleanup 을 강제하지 않음, 편의 참고만).

**Pattern A 해당 Story**: Pattern A (Contents API SHA-based optimistic concurrency) 를 사용하는 경우 `retro-attempts-state/<KEY>` long-lived branch 생성 없음 — 본 retention policy 적용 범위 외. Pattern A 기본 채택 (amendment_id=1 정합).

**근거**: 90일 = ADR-026 §결정 2 CODEFORGE_CROSS_REPO_PAT 90d rotation runbook 과 alignment. story close 후 90일 = audit trail 충분 보존 + 브랜치 누적 방지 균형.

---

### Amendment 3 — §11.6 multi-runner race scenario informational mitigation (CFP-290 / Issue #297)

**문제**: retro-attempts.jsonl 의 concurrent write 시나리오 (GitHub Actions matrix strategy 또는 병렬 workflow runner 가 동시에 jsonl append 시도) 에 대한 mitigation 이 ADR-045 내에 문서화되지 않아 "race 발생 시 어떻게 되는가" 가 불명확했다.

**결정**: Pattern A (Contents API SHA-based optimistic concurrency, `docs/domain-knowledge/jsonl-write/race-condition-handling-pattern.md`) 가 multi-runner concurrent write 를 올바르게 처리함을 CFP-138 security test 를 통해 검증했다. **코드 변경 불필요** — 검증된 동작을 informational note 로 기록.

**검증된 mitigation enumeration**:

| 시나리오 | Pattern A 처리 방식 | 결과 |
|---|---|---|
| Runner A + Runner B 동시 append 시도 | A 가 먼저 write 완료 → B 의 PUT 요청 SHA mismatch → GitHub Contents API 409 Conflict 반환 | B 가 최신 SHA re-fetch 후 CAS retry → eventual consistency 보장 |
| 3+ runner 동시 경합 | 동일 CAS 메커니즘, 순차 직렬화 | 모든 write 가 commit history 에 기록됨 |
| SHA collision 위험 | Git SHA-1 2^80 preimage resistance (NIST SP 800-131A 기준) | collision 확률 무시 가능 (negligible) |
| 네트워크 지연 / 부분 실패 | 409 이후 caller retry + exponential backoff (Pattern A spec 정합) | no silent data loss |

**보장**: git clone + bare push pattern (lost-update risk, D-4 금지) 과 달리 Pattern A 는 last-writer-wins 없음 — 모든 concurrent writer 가 CAS 로 직렬화되어 retro-attempts.jsonl 의 data integrity invariant (D-4 Idempotency invariant) 충족.

**Scope**: 본 informational note 는 Pattern A 구현 코드의 동작을 ADR 레벨에서 확인·기록한 것. Pattern A 코드 자체는 `docs/domain-knowledge/jsonl-write/race-condition-handling-pattern.md` SSOT — 본 ADR 는 cross-reference 만.

---

### Amendment 4 — §D-5 신설: Orchestrator session 개시 retro alert scan 의무 (CFP-628)

**문제**: CFP-609 + CFP-612 + CFP-610 3 Story 연속으로 retro-mandatory.yml workflow 발화에도 불구하고 Orchestrator 가 새 session 개시 시 미해소 `[PMO] retro alert` comment 를 인지하지 못해 manual fallback 이 반복됐다. behavioral scan 의무 부재가 원인.

**결정**: §D-5 신설 — Orchestrator 가 새 session 개시 시 다음 mechanical scan 의무.

#### §D-5 — Orchestrator session 개시 retro alert scan 의무

1. `gh issue list --state open --label "phase:완료" --json number,labels` 조회
2. 각 Issue 의 comment 안 `[PMO] retro alert` prefix comment 존재 + `created_at` filter (PR merge + 35min 경과 — retry 4회 완료 후)
3. 미해소 alert 발견 시 PMOAgent 자동 spawn 의무

**강제 강도**: behavioral directive — SessionStart hook (`scripts/check-retro-alerts.sh`, Layer c) 가 mechanical pre-screen.

**ADR-039 §결정 7 cross-ref**: Orchestrator self-discipline 영역 확장 — `policy_violation_subdecision` 발화 차단.

**Sunset metric**: retro-alert-pickup-rate ≥ 90% (분모 = 발화 alert comment 수, 분자 = Orchestrator 5 turn 내 PMOAgent spawn 한 비율, monthly cron `retro-alert-pickup-kpi.yml` 자동 측정).

**근거**: CFP-609 + CFP-612 + CFP-610 3 Story 연속 manual fallback evidence — behavioral directive 신설 없이는 silent miss 반복 예상. session 개시 = 자연 scan 시점.

---

### Amendment 5 — §D-9 신설: Cross-Story pattern threshold 도달 시 ADR escalation 의무 (CFP-665)

**문제**: PMOAgent 가 Cross-Story pattern 을 발견하더라도 ADR 발의 여부를 자체 판단(self-decide)에 맡겨 발의 누락 또는 지연이 발생할 수 있었다. N=2 이상 반복은 PMOAgent 가 "우연이 아님" 을 판단해야 하는 영역이며 self-decide = 회피 가능한 회색지대였다.

**결정**: §D-9 신설 — PMOAgent 가 retro write 시점 Cross-Story pattern 검출 직후 threshold check. 누적 ≥ 2 도달 시 ADR escalation 의무 (Mandatory framing).

#### §D-9 — Cross-Story pattern threshold 도달 시 ADR escalation 의무

**Threshold**: N = 2 (fixed, industry lower bound — Google SRE Workbook Chapter 15 "If you see the same issue twice, it is no longer a coincidence" + ITIL v4 Foundation Problem Management "Recurring incidents ≥ 2 → Problem Record" + NASA ASRS Significant Event Reporting "≥ 2 similar events"). consumer overlay 가변 = out-of-scope (별도 follow-up CFP 분리).

**검출 전략 = hybrid** (Sun et al. 2011 ASE best F1 score 정합):

1. **(Primary) 동일 anchor_id ≥ 2 Story 재발**: review-verdict-v4 stable identifier strict matching — false positive 차단 우선.
2. **(Secondary fallback) root_cause_taxonomy class 내 anchor_id ≥ 2**: anchor_id naming inconsistency 시 catch — false negative 보완.

**Mandatory framing**: threshold 도달 시 PMOAgent self-decide 영역 제거 — `pmo_output v1.2.cross_story_pattern_adr_trigger` field mandatory 채움 의무 (회피 불가). False positive 안전망 = `escalation_action` enum 2-value:
- `adr_draft_emitted` (정식 ADR draft 작성, default) — ArchitectAgent spawn
- `escalate_user` (PMOAgent 가 trivial 판정 시 사용자 manual decide 의뢰)

두 enum value 모두 `cross_story_pattern_adr_trigger` field mandatory 채움 의무 (forcing function 보존). 후속 처리 분기만 다름.

**pmo-output-v1 v1.2 연동**: `cross_story_pattern_adr_trigger` optional field 신설 (additive, v1.0/v1.1 consumer 호환). schema 5 sub-field: `pattern_count_threshold` / `detected_anchor_id` / `fallback_root_cause_class` / `occurrences[]` / `escalation_action`. SSOT = [pmo-output-v1 §3](https://github.com/mclayer/plugin-codeforge/blob/main/docs/inter-plugin-contracts/pmo-output-v1.md).

**강제 강도**: PMOAgent agent file mandate (codeforge-pmo CLAUDE.md §3 Cross-Story 패턴 분석 §4 ADR 후보 발의 — Mandatory 표기) + pmo-output-v1 v1.2 contract schema (threshold 도달 시 field 채움 의무).

**근거**: ADR-045 D-8 D-2 framing 정합 — retro 의무화가 "발견 → 행동" forcing function 이듯이 본 §D-9 는 "pattern 누적 → ADR escalation" forcing function. CFP-665 Story DesignReview lane evidence = FIX iter 1 ADR ref 갱신 inline FIX 1건 외 정상 PASS.

### Amendment 6 — §D-9 cross_story_pattern_adr_trigger 적용 evidence: ADR-082 산물 (CFP-776)

**문제 (해당 없음 — evidence-only)**: 본 Amendment 는 §D-9 결정 본문을 변경하지 않는다. Amendment 5 §D-9 가 신설한 "pattern 누적 → ADR escalation" forcing function 이 cross-Story 에서 실제로 작동한 첫 산물을 evidence 로 기록한다 (Amendment 5 self-application paradox 시연 — forcing function 이 명목상 존재만 하는지 실제 동작하는지의 evidence).

**적용 evidence**:

| 항목 | 값 |
|---|---|
| pattern_count | 3 (≥ threshold 2 = Mandatory framing 발동) |
| occurrences | CFP-746 D-7 corpus slip (#1a) / CFP-746 CFP-531 정정-2nd-slip (#1b) / CFP-770 CR-004 §9 evidence stale (#2) / CFP-770 §결정 8 Phase 0 cross-plugin 추정 (#3) |
| detected pattern | self-write artifact 의 source/value/ownership claim 을 write-time verification 없이 단언 (super-class) |
| trigger source | CFP-746 retro §6 후보 1 (corpus-claim write-time verification lint) + CFP-770 retro §6 후보 1 (self-write artifact source/value/ownership claim write-time verification 의무) |
| escalation_action | `escalate_user` (PMOAgent → 사용자 manual decide 의뢰 — 단일 super-class ADR 통합 vs per-area 분할) |
| 사용자 결정 | 2026-05-16 KST — 단일 super-class ADR 통합 (ADR-064 §결정 1 unitary scope 정합) |
| 산물 | ADR-082 (Write-time self-write verification mandate) — CFP-776 carrier, doc-only fast-path |

**결정**: §D-9 forcing function 이 "pattern 누적 → ADR escalation" 으로 실제 작동했음을 ADR-082 산출로 확인. §D-9 결정 본문 / threshold N=2 / hybrid 검출 전략 / Mandatory framing 의미 변경 없음 — evidence-only Amendment. ADR-082 §결정 1 layer disjoint 표가 ADR-045 §D 를 4-layer 중 "retro corpus enumeration (PMOAgent §5 pattern_count)" layer 로 명시 (verify-before-trust governance 의 retro pattern aggregation layer).

### Amendment 8 — §D-9 sub-decision (b) 신설: PMOAgent retro batch §6 ADR draft pre-publish verify-before-trust 3-source AND mandate (CFP-1592)

**문제**: ADR-045 Amendment 5 §D-9 forcing function (pattern_count ≥ 2 → escalation_action enum 2-value) 이 도입된 이후, PMOAgent retro batch (§5 cross-Story pattern aggregation 직후) §6 ADR draft 후보 발의 sub-section 안에서 **이미 shipped 영역과 collision** 하는 stale-premise ADR draft 후보가 반복 발의되었다. §D-9 의 기존 sub-decision (a) (pattern_count threshold 도달 시 escalation_action enum 채움 의무) 는 post-detection escalation enforce mechanism — 그러나 ADR draft 후보 작성 시점 자체에 stale-premise prevention 의 pre-publish quality gate 가 부재했다.

**증거 (pattern_count 6 reach Mandatory)**:

| # | CFP | 발의 origin | Stale premise | Already-shipped carrier |
|---|---|---|---|---|
| 1 | CFP-1006 | Tier-B Wave 1 (2026-05-19) | auto-resolve assumption | CFP-1025 root cause codify (post-merge) |
| 2 | CFP-1542 | CFP-FU-A/B retro batch (2026-05-25) | bypass-cumulative-counter mechanical wire 신규 | CFP-845 (ADR-024 Amd 8) MERGED 2026-05-17 — full per-plugin-cumulative-counter shipped |
| 3 | CFP-1558 | CFP-FU-A/B retro batch (2026-05-25) | amendment-number-frontmatter-verify lint 신규 | CFP-1198/1216/1312 MERGED 2026-05-21~23 — Wave 1+2+bidirectional extension shipped |
| 4 | CFP-1604 | Wave 4 batch (2026-05-25) | (Wave 4 batch stale catch) | (별 carrier already shipped) |
| 5 | CFP-1605 | Wave 4 batch (2026-05-25) | (Wave 4 batch stale catch) | (별 carrier already shipped) |
| 6 | CFP-1606 | Wave 4 batch (2026-05-25) | (Wave 4 batch stale catch) | (별 carrier already shipped) |

pattern_count 6 ≫ threshold 2 = **Mandatory** (Amendment 5 §D-9 forcing function 정합). 100% retro-batch-origin rate + 60% PIVOT rate (Wave 4 batch 3/5).

**결정**: §D-9 본문 **sub-decision (b) 신설 (additive ratchet 강화 방향, 본문 변경 0건 — sub-decision (a) RETAIN)**. PMOAgent retro file write 시점 §6 ADR 후보 발의 sub-section 안 매 ADR draft 후보 (escalation_action: adr_draft_emitted 또는 escalate_user **모두**) 작성 직전 3-source AND verify gate 통과 의무.

#### §D-9 sub-decision (b) — Retro batch §6 ADR draft pre-publish 3-source AND verify gate

**Pre-publish gate trigger**: PMOAgent 가 retro file `<sprint>-cfp-NNN-<slug>.md` §6 sub-section 안 ADR draft 후보 (escalation_action enum value 무관 — adr_draft_emitted / escalate_user **모두**) 발의 시점.

**3-source AND verify (모두 PASS 의무)**:

1. **`git show origin/main:<ADR-path>` direct frontmatter amendment count verify** — target ADR 가 이미 존재한다면 amendment_log[] max 직접 read. 발의 premise 가 "기존 ADR 의 신규 Amendment 가 필요" 일 때 — 해당 영역이 이미 max-1 amendment 까지 codified 되어 있는지 확인.
2. **`grep <feature-name> docs/evidence-checks-registry.yaml`** — 발의 premise feature 가 이미 evidence-checks-registry mechanical lint entry 로 wire 되어 있는지 직접 grep. 발의 premise 가 "mechanical lint 신규 wire" 일 때 — 동일 lint 가 이미 warning/blocking tier 로 wire 되어 있는지 확인.
3. **`Glob scripts/check-<feature-pattern>*`** — 발의 premise script 가 이미 wrapper repo 안 wire 되어 있는지 직접 Glob. 발의 premise 가 "lint script 신규 작성" 일 때 — 동일 script 가 이미 존재하는지 확인.

**Gate fail behavior** (1+ source 부재 = stale-premise 확률 높음):
- `[fact-check-pending]` annotation 의무 (PMOAgent retro file §6 후보 row 안 marker append)
- §6 후보 **downgrade to §4 informational only** (정식 ADR draft 발의 차단)
- **OR PIVOT mark** (`pmo_output v1.cross_story_pattern_adr_trigger.escalation_action: escalate_user` enum retain — false positive 안전망)

**Gate PASS (3 source AND 모두 PASS) behavior**:
- §6 후보 정식 발의 (`escalation_action: adr_draft_emitted`)
- ArchitectAgent spawn → 신규 ADR 또는 Amendment carrier 작성

**False positive 안전망 (sub-decision (a) RETAIN)**: `escalation_action: escalate_user` enum value 보존 — gate fail 시 PMOAgent self-decide 영역 0, 사용자 manual decide 의뢰 path 보존. forcing function 약화 0건 — pre-publish gate 는 post-detection escalation 의 quality 강화 layer, original (a) mechanism 보존 (additive).

**Strict mode invariant**: 3-source AND 가 OR 가 아닌 AND 임 — 1 source 라도 부재 시 gate fail. 이유: stale-premise 발생 root cause = "정보 일부 missing 으로 인한 incomplete check" — 1 source PASS 만으로 premise validity 결론 금지.

**근거**: ADR-045 §D-9 Amendment 5 forcing function 의 **self-strengthening** — sub-decision (b) 신설 = forcing function 의 pre-publish quality gate axis 강화 (기존 sub-decision (a) = post-detection escalation enforce mechanism, 본 sub-decision (b) = pre-publish stale-premise prevention mechanism). 두 sub-decision = disjoint axis temporal split (pre vs post detection).

paired sibling **CFP-1623** = Wave 2 mechanical wire prerequisite carrier (sequential after #1592 merge — declarative anchor 발효 후 mechanical wire activation, CFP-825 → CFP-845 → CFP-1198~1216~1312 → CFP-1580 → CFP-1592 5-Story Wave 1 → Wave 2 split precedent 답습). pmo-output-v1 schema 확장 (3-source verify field) 영역 = #1623 carrier.

**axis disjoint preservation**: ADR-082 sub-scope 1-A~1-M 13 chain = artifact content write-time semantic truth verify axis. 본 Amendment 8 = retro corpus enumeration §6 ADR draft authoring path pre-publish gate axis (ADR-045 §D layer 정합). 두 ADR 가 retro-time verify 영역에서 axis 분리되어 disjoint complement 관계.

**ADR-097 paradigm scope boundary 정합**: sub-decision 확장 = ratchet 강화 carve-out (≠ paradigm replacement). ADR-097 §결정 1 closed-set 3 조건 (9+ ADR 동시 sunset / 단일 atomic Epic / ratchet 강화 carve-out) 중 본 Amendment 8 은 단일 ADR 단일 sub-decision 확장 = paradigm replacement 영역 외.

**escalation_resolved_carrier**: CFP-1592 (본 carrier).

### Amendment 8 적용 evidence (§D-9 forcing function 산물 7번째)

| 항목 | 값 |
|---|---|
| pattern_count | 6 (≫ threshold 2 = Mandatory framing 발동) |
| occurrences | CFP-1006 (Tier-B Wave 1 stale auto-resolve) / CFP-1542 (CFP-FU-A/B retro batch bypass-cumulative-counter stale) / CFP-1558 (CFP-FU-A/B retro batch amendment-number-frontmatter-verify stale) / CFP-1604/1605/1606 (Wave 4 batch 3 stale catches) |
| detected pattern | `retro_batch_adr_draft_stale_premise` — PMOAgent retro batch §6 ADR draft 후보 발의 시 이미 shipped 영역과 collision (super-class) |
| trigger source | CFP-1592 Issue body §"Why" (orchestrator_authored_followup 2026-05-25 KST) |
| escalation_action | `adr_draft_emitted` (CFP-1592 carrier 산물) |
| 사용자 결정 | 2026-05-25 KST — ADR-045 §D-9 sub-decision (b) 신설 (additive ratchet 강화 방향, ADR-082 axis disjoint preservation) |
| 산물 | ADR-045 Amendment 8 (CFP-1592 carrier, doc-only fast-path Cat 1 단일 PR) + paired sibling #1623 Wave 2 mechanical wire carrier (sequential) |

§D-9 forcing function 이 'pattern 누적 → ADR escalation' 으로 실제 동작한 7번째 cross-Story 산물 evidence (Amendment 6 CFP-776 ADR-082 carrier = 5번째 / Amendment 7 CFP-1580 ADR-068 Amd 4 carrier = 6번째 / 본 Amendment 8 = 7번째). 본 Amendment 8 는 **evidence + sub-decision (b) 신설** dual carrier — Amendment 6/7 (evidence-only) 대비 §D-9 본문 자체 (sub-decision layer) 강화 ratchet 동반.

### Amendment 9 — §D-10 신설: Retro batch §6 ADR draft pre-publish 8-tuple verify-before-trust forcing function (CFP-1623)

**문제**: PMOAgent retro batch §6 ADR draft authoring 시점 verify-before-trust 부재 → retro-batch-origin Stories 100% PIVOT rate (Wave 3+4 batches 5/5 stale catch). pattern_count 6 cumulative ≫ threshold 2 (3.0x), retro-batch-origin discriminator confirmed (5/5 vs non-retro-batch 0/2 rate).

본 Amendment 는 §D-9 forcing function 의 axis 보완 — §D-9 (post-hoc threshold escalation) ↔ Amendment 8 §D-9 sub-decision (b) (3-source AND verify) ↔ 본 §D-10 (pre-publish preflight 8-tuple expansion). 세 forcing function 이 retro lifecycle 의 세 시점 cover:

- §D-9 (Amendment 5) = retro write 완료 후 cross-Story pattern_count 누적 → ADR escalation (post-hoc aggregation)
- §D-9 sub-decision (b) (Amendment 8 CFP-1592, paired sibling) = retro batch §6 ADR draft 후보 작성 직전 3-source AND verify (declarative anchor)
- 본 §D-10 (Amendment 9) = §6 ADR draft section authoring 직전 8-tuple AND gate (preflight expansion forcing function)

**결정**: §D-10 신설 — PMOAgent retro write 시점 §6 ADR draft section authoring 직전 8-tuple verify-before-trust gate 통과 의무.

#### §D-10 — Retro batch §6 ADR draft pre-publish 8-tuple verify forcing function

**Mandatory framing**: gate fail (8 source 중 1+ disagree) 시 PMOAgent self-decide 영역 제거 — §6 candidate 자동 downgrade 의무 (`downgrade_action` enum 2-value):

- `downgrade_to_section_4_informational_only` — carrier 발의 회피, 기존 §4 informational 으로 강등
- `pivot_mark` — carrier 발의 보존 but PIVOT preflight marker 부착, retro file 안 명시 mark

두 enum value 모두 §6 candidate scope re-decide 의무 (forcing function 보존). 후속 처리 분기만 다름.

**8-tuple verify sources** (AND gate, 1+ disagree → downgrade):

1. `git show origin/main:<ADR-path>` — frontmatter `amendment_log` direct read (target ADR 영역에 이미 amendment 추가됨 여부)
2. `grep <feature-name> docs/evidence-checks-registry.yaml` — mechanical lint 이미 등록됨 여부
3. `Glob scripts/check-<feature-pattern>*` — 실 script 이미 존재 여부
4. `gh pr list --search "<feature-name> in:title" --state merged` — sibling carrier merge status
5. `gh issue list --search "<feature-name> in:title" --state all` — existing CFP carrier 검색
6. `git log --all --oneline -- <path>` — file-level historical change presence
7. `Glob docs/adr/ADR-*.md` + frontmatter `amendment_log` cross-Story scan — recent amendment chain
8. retro §5 cross-Story pattern table 안 `anchor_id` ↔ existing implementation 매핑 — pattern_count → existing carrier mapping verify

**Platform 한계 영역 처리** (`[verification-out-of-scope: <사유>]` marker, ADR-052 Amendment 3 marker 5종 정합):

- gh CLI search rate-limit 환경 = source 4 + 5 skip → 6-tuple AND
- git shallow clone 환경 = source 6 skip → 7-tuple AND
- 단일 source 미충족 ≠ gate fail — 사유 marker 의무 (reverse-explicit annotation)

**pmo-output-v1 v1.3 연동**: `retro_section_6_pre_publish_verify` optional field 신설 (additive, v1.0/v1.1/v1.2 consumer 호환). schema 3 sub-field:

- `verify_sources_attempted[]` — 8 source enum
- `verify_sources_blocked[]` — platform exemption 사유
- `downgrade_action` — enum 2-value (`null` if pass / `to_section_4_informational` / `pivot_mark`)

SSOT = [pmo-output-v1 §3](https://github.com/mclayer/plugin-codeforge/blob/main/docs/inter-plugin-contracts/pmo-output-v1.md). Wave 1 = schema declarative codify, Wave 2 mechanical wire = 별 sub-CFP carrier defer.

**강제 강도**: PMOAgent agent file mandate (codeforge-pmo `templates/retro.md` §6 pre-publish gate cross-ref + PMOAgent.md self-write 표 — Wave 2 sibling sync 시점) + pmo-output-v1 v1.3 contract schema (`retro_section_6_pre_publish_verify` optional field, Wave 2 sibling sync 시점 mandatory transition).

**Wave 1 declarative anchor scope** (본 Amendment 본문):

- §D-10 forcing function 신설 (8-tuple AND gate + `downgrade_action` enum 2-value)
- 8 verify sources schema codify
- platform exemption `[verification-out-of-scope:]` marker channel codify
- pmo-output-v1 v1.3 `retro_section_6_pre_publish_verify` optional field 신설 선언

**Wave 2 mechanical wire** (별 sub-CFP carrier defer, declarative-only Wave 1 enforce):

- `scripts/check-retro-batch-adr-draft-pre-publish.py` — PMOAgent retro file §6 ADR draft section auto-detect + 8-tuple verify automation
- `templates/github-workflows/retro-batch-adr-draft-pre-publish.yml` — warning tier workflow (cron 또는 retro PR open trigger)
- `docs/evidence-checks-registry.yaml` entry append — `retro-batch-adr-draft-pre-publish`, owner_adr ADR-045 / carrier_adr ADR-060, warning tier deferred-followup
- `docs/inter-plugin-contracts/label-registry-v2.md` MINOR — `hotfix-bypass:retro-batch-adr-draft-pre-publish` family member
- codeforge-pmo plugin sibling sync — PMOAgent.md self-write 표 + `templates/retro.md` §6 pre-publish gate cross-ref (별 PR carrier)

**근거**: ADR-045 §D-9 post-hoc threshold escalation 의 pre-publish preflight 보완 axis. Wave 3+4 batches 100% retro-batch-origin PIVOT rate (5/5) evidence 정합. CFP-1623 carrier = META #1592 (Amendment 8 §D-9 sub-decision (b) 3-source AND) 의 sub-domain prerequisite (8-tuple expansion). retro-batch-origin discriminator 확정 = retro lifecycle 안 §6 ADR draft authoring path 영역 forcing function 강화 정합 (Industry pre-publish gate pattern — K8s admission webhook / GitHub branch protection required checks / Hashicorp Terraform plan/apply split analog).

**paired sibling cross-ref**:

- Amendment 8 (CFP-1592, paired sibling) = §D-9 sub-decision (b) 3-source AND verify declarative anchor — sequential dispatch convention (#1592 먼저 land → 본 §D-10 후속, Story §7 권장 정합)
- Amendment 5 (CFP-665) §D-9 retain invariant 보존 — Amendment 9 = §D-10 sub-decision append only, §D-9 본문 의미 변경 0
- Amendment 6 (CFP-776) §D-9 evidence Amendment precedent 답습 — forcing function 이 명목상 존재만 하는지 실제 동작하는지의 evidence Amendment pattern (본 §D-10 = preflight 측 forcing function expansion)
- Amendment 7 (CFP-1580) §D-9 evidence Amendment 6번째 precedent — pattern_count 5 → §D-9 forcing function 실 작동 → ADR-068 Amendment 4 산물 (axis 분리: 본 §D-10 = pattern_count 6 reach 후 preflight 보완, ADR-068 Amendment 4 = mechanical wire DR-skip 영역 disjoint axis)
- ADR-082 §결정 12 (RequirementsPL + retro-time verify-before-trust) = adjacent disjoint axis (write-time vs pre-publish discipline 명확 분리, RequirementsPL vs PMOAgent agent boundary 명확)

#### §D-11 — PMOAgent retro batch closure pattern normative codify (Amendment 11 / CFP-1680)

**Mandatory framing**: PMOAgent 가 누적 LOW/MEDIUM follow-up Issue (≥ 3) 의 batch closure 진행 시 본 §D-11 4-option decision enum + 4 의무 영역 + closure summary table SSOT format + closure forcing function 3 step 적용 의무.

axis 분리 (paired sibling §D-9 / §D-10 / §D-11 closed-set):
- **§D-9** (Amendment 5 CFP-665) = post-hoc cross-Story pattern threshold 도달 시 ADR escalation forcing function (retro write 시점)
- **§D-9 sub-decision (b)** (Amendment 8 CFP-1592) = retro batch §6 ADR draft 후보 작성 pre-publish 3-source AND verify gate
- **§D-10** (Amendment 9 CFP-1623 + Wave 2 mechanical wire Amendment 10 CFP-1632) = retro batch §6 ADR draft pre-publish 8-tuple verify forcing function
- **§D-11** (Amendment 11 CFP-1680, 본 sub-decision) = retro batch **closure** lifecycle 영역 (post-batch governance status update, pre-publish §D-9/§D-10 forcing function 영역과 disjoint axis)

**ADR-137 cross-ref (Epic-close 구현-리팩터링 triage, CFP-2541 Story C)**: ADR-137 = §D-11 Epic-close **sibling** (같은 발동 시점 Epic-close + 같은 owner PMOAgent). 단 **모집단·enum axis-disjoint (동일시 금지)**: §D-11 = retro follow-up **Issue**(≥3) / enum `CLOSE_AS_OBVIATED·SENTINEL·PROMOTE·DEFER` ↔ ADR-137 = 실코드 **duplication anchor** / enum `now·defer·drop`. §D-11 5-column structured-row 는 ADR-137 이 **패턴 참조 선례로만** 인용(closure enum 값 비재사용). 상세 = ADR-137.

##### §D-11 (1) Decision enum (closed-set 4-option)

PMOAgent 가 batch closure 안 각 Issue 에 대해 다음 4-option 중 1 값 결정 의무:

- **`CLOSE_AS_OBVIATED`** — recent carrier 가 이미 cover (verify via direct merge link 의무, Issue body verbatim ↔ carrier PR merge state mapping)
- **`CLOSE_AS_SENTINEL`** — declarative monitor only (pattern_count not reached, ADR-060 promotion gate AND 3/3 미충족, deferred future carrier candidate)
- **`PROMOTE`** — pattern_count reached, active Story 발의 의무 (label `priority:P1` 부착, ADR-045 §D-9 escalation 정합)
- **`DEFER`** — keep open, future carrier 대기 (rationale 명시 의무, sunset gate metric 부재 영역 보존)

##### §D-11 (2) Verify-before-trust 5 sub-scope mandate

PMOAgent batch closure write-time 다음 5 sub-scope 의무 (각 Issue 별):

- **(a) per-Issue body verbatim cite** — 재합성 0 (ADR-082 §결정 1 layer 1 sub-scope (1-C) USER-UTTERANCE-VERBATIM block 패턴 답습 batch closure 영역 sub-domain, Issue body wording 직접 인용 의무)
- **(b) recent merge state direct verify** — `gh api repos/<owner>/<repo>/pulls/<N>` + `git log --oneline <SHA>` (ADR-073 verify-before-assert primitive 답습 batch closure 영역)
- **(c) axis disjoint discrimination** — false-positive obviation 차단 (ADR-082 §결정 12 retro-time verify-before-trust 정합 batch closure 영역, "비슷한 carrier 가 cover 한다" 추론 금지 — verify 의무)
- **(d) sibling carrier cross-link via PR number** — ADR-082 §결정 9 verify-before-cite 양방향 답습 batch closure 영역 (closure rationale 안 PR/Issue 번호 explicit cite)
- **(e) sub-scope alphabet sequential verify** — pre-write 위치 확인 (ADR-082 §결정 1 sub-scope codify 패턴 답습, 본 §D-11 sub-scope 1-K, 1-L 등 amendment 진입 시 pre-claim 의무)

##### §D-11 (3) Closure summary table format (SSOT)

PMOAgent batch closure 산출 retro file §X (close lane sub-section) 안 다음 5-column table 의무 (ADR-068 I-4 wording SSOT invariant 정합 batch closure 영역):

| # | Issue | Tier | Decision | Final state | Comment URL |
|---|---|---|---|---|---|
| 1 | #NNN | priority:low \| priority:medium | CLOSE_AS_OBVIATED \| CLOSE_AS_SENTINEL \| PROMOTE \| DEFER | closed (not_planned) \| closed (completed) \| open (deferred) | https://github.com/.../issues/NNN#issuecomment-... |

##### §D-11 (4) Cross-Story pattern_count progression

batch closure 안 §D-9 cross_story_pattern_adr_trigger field 충돌 회피 의무 — pre-batch / post-batch / threshold / status 명시:

```
cross_story_pattern_progression:
  pattern_anchor: <anchor_id>
  pre_batch_count: N
  post_batch_count: N (closure 가 pattern_count 변화 0 — closure 자체는 pattern 자체 변경 아님)
  threshold: 2
  status: not_reached | reached_and_carrier_filed | reached_and_deferred
  cross_story_pattern_adr_trigger: null (closure 자체는 §D-9 escalation 비대상)
```

Net escalation 0 시 `cross_story_pattern_adr_trigger` field empty 유지 (closure ≠ pattern increment).

##### §D-11 (5) Closure forcing function 3 step

PMOAgent batch closure 진행 시 다음 3 step 의무 (각 Issue 별):

1. **`[PMO]` prefix comment + state transition** — Issue 별 closure decision rationale comment 작성 + state 전환 (`closed` `not_planned` reason OR `completed` reason). 상세 PMOAgent.md §"closure rationale comment" (현 `plugins/codeforge-pmo/agents/PMOAgent.md`, 구 lane repo 삭제됨 2026-06-12) (Wave 2 sibling sync 시점).
2. **Retro PR open + auto-merge** — closure evidence trail 의 영속화 (ADR-045 §결정 4 retro PR 자동 merge 정합, batch closure retro file §X close lane sub-section 안 closure summary table embed).
3. **`gate:retro-complete` label add OR `not_planned` reason close** — ADR-045 §결정 5 close-blocking 정합 (Issue close 의무 evidence trail).

##### §D-11 (6) Wave lineage — 6 applied case evidence base

본 §D-11 normative consolidation 동인 = pattern_count 6 reach (threshold 2 = 3.0x):

1. **CFP-963 retro 4-batch** (Codex worker network_scope 영역, 2026-05-22 KST) — 4 follow-up CFP filed batch closure 첫 evidence
2. **CFP-1339 retro 5-batch** (6-CFP codify batch closure 정합, 2026-05-23 KST) — META self-application 6th applied case
3. **CFP-1612 retro 3-batch** (Wave 2 mechanical wire activation paired sibling, 2026-05-25 KST) — 13-instance established pattern reach
4. **CFP-1637 retro 3-batch** (sub-domain followup closure, 2026-05-25 KST) — established pattern carrier
5. **CFP-1648 retro deferred** (pre-merge ABORT precedent, 2026-05-26 KST) — DEFER decision evidence (4-option enum DEFER value 첫 evidence)
6. **batch-close 2026-05-26** (본 Amendment 11 carrier 자체 retro, 6 follow-up closure) — normative consolidation Story 자체가 batch close pattern 7th applied (self-reference recursive dogfooding)

##### §D-11 (7) Wave 1 → Wave 2 split 적용 영역 외 (declarative anchor only)

batch close = governance status update (closure decision + comment + label 영역) — mechanical wire 영역 disjoint:

- Wave 2 mechanical wire 보류 — ADR-076 declarative reconciliation pattern (closure decision 자체는 사용자 영역 + agent judgment 영역, mechanical lint 무관)
- 향후 Wave 2 carrier 발생 시 별 sub-CFP carrier (ADR-076 mechanical wire 패턴 답습 보류, ADR-064 §결정 5 CFP scope unitary 정합)
- pattern_count ≥ 9 reach 시 warning → blocking-on-pr 승격 = Wave 3 별 carrier 분리 (ADR-060 §결정 6 promotion gate AND 3/3)

##### §D-11 (8) META forward-prevention

본 Amendment 11 = META 24th applied case (ADR-082 §결정 1-K 4-step numeric claim write-time verify-before-write mandate self-execute):

- CFP-1632 = 21st applied (Wave 2 mechanical wire activation)
- CFP-1648 = 22nd applied (pre-merge ABORT precedent)
- CFP-1637 = 23rd applied (sub-domain followup closure)
- **본 CFP-1680 = 24th applied** (PMOAgent retro batch closure pattern normative consolidation, pattern_count 6 reach 자체 verify-before-write self-execute recursive dogfooding self-evidence)

**paired sibling cross-ref**:

- playbook §18 (PMOAgent retro batch closure operating sequence) = 동일 Story CFP-1680 paired sibling carrier, 5 sub-section codify (§18.1 trigger / §18.2 decision tree / §18.3 verify mandate workflow / §18.4 table SSOT / §18.5 retro PR auto-merge)
- ADR-045 §D-9 (Amendment 5 CFP-665) = post-hoc threshold escalation forcing function (batch closure 영역과 disjoint axis — escalation vs closure 명확 분리)
- ADR-045 §D-10 (Amendment 9 CFP-1623 + Wave 2 Amendment 10 CFP-1632) = pre-publish 8-tuple verify forcing function (batch closure 영역과 disjoint axis — pre-publish vs post-batch 명확 분리)
- ADR-082 §결정 12 (retro-time verify-before-trust) = adjacent axis (PMOAgent retro write-time vs PMOAgent batch closure-time 분리)
- ADR-082 §결정 9 (verify-before-cite 양방향) = §D-11 (2)(d) sibling carrier cross-link via PR number 정합

### Amendment 12 — §D-9 sub-decision (c) 신설: Pattern A 반응형→예방형 merge-time gate-provenance self-attest (warning-first → ratchet, CFP-2330)

**문제**: ADR-045 §D-9 의 기존 두 sub-decision — (a) (Amendment 5 CFP-665) post-detection cross-Story pattern threshold escalation + (b) (Amendment 8 CFP-1592) PMOAgent retro batch §6 ADR draft pre-publish 3-source AND verify — 는 모두 **PMOAgent retro-time** 영역의 forcing function 이다. 그러나 `docs/agent-prompt-guardrails.md:26` 가 박제한 **Pattern A "chief author self-attest false claim"** (pattern_count 3 reach Mandatory, Pattern A-2 = InfraEng FIX iter 1 false self-attest `tests_passed: 19/19` vs actual `10/27 (17 FAIL)`) 는 **gate verdict write-time** 영역에 위치한다 — agent 가 자기 산출물의 PASS 를 거짓 단언하고 그 verdict 가 그대로 gate-pass label/comment 로 승격되는 경로. 기존 self-discipline layer (ADR-082 §결정 1 write-time self-write verify + ADR-073 verify-before-assert) 는 **반응형(reactive)** — author 가 스스로 verify 하지 않으면 위반이 downstream review/retro 시점에야 검출된다. gate verdict 가 lane 의 실제 machine-checkable 산출물에 묶여 있는지 **merge-time 에 mechanical 로 예방(preventive)** 하는 layer 가 부재했다.

**증거 (Pattern A lineage)**:

| # | Pattern A occurrence | self-attest false claim | ground truth |
|---|---|---|---|
| A-2 | InfraEng FIX iter 1 (docs/agent-prompt-guardrails.md:26-28) | `tests_passed: 19/19 bats GREEN` | actual `10/27 (17 FAIL)` — gate verdict 가 검증 없이 PASS 승격 |
| — | (retro 미관찰 다중 occurrence 추정 — guardrails.md:34) | gate verdict ↔ 실 artifact 괴리 | mechanical preventive gate 부재 |

Pattern A pattern_count 3 ≥ threshold 2 = Mandatory escalation (§D-9 forcing function 정합). carrier source 명칭 SSOT = `docs/agent-prompt-guardrails.md:26` (이슈 #1353 직접 링크 금지 — "ADR-045 §D-9 Pattern A(carrier CFP-1353, 명칭 SSOT=agent-prompt-guardrails.md:26)" 로 ref).

**결정**: §D-9 본문 **sub-decision (c) 신설 (additive ratchet 강화 방향, 본문 변경 0건 — sub-decision (a)/(b) RETAIN)**. Orchestrator 가 gate verdict 를 self-write (gate-pass label 부착 / `[<lane>-리뷰]` PASS comment) 하기 직전, 해당 verdict 가 lane 의 실제 machine-checkable 산출물에 묶여 있는지 **merge-time multi-anchor AND preventive gate** 통과 의무.

#### §D-9 sub-decision (c) — Merge-time gate-provenance multi-anchor AND self-attest

**axis 분리 (paired sibling §D-9 (a)/(b)/(c) closed-set)**:
- **(a)** (Amendment 5 CFP-665) = post-hoc cross-Story pattern threshold escalation (PMOAgent retro write 시점)
- **(b)** (Amendment 8 CFP-1592) = retro batch §6 ADR draft 후보 pre-publish 3-source AND verify (PMOAgent retro write 시점)
- **(c)** (본 Amendment 12 CFP-2330) = gate verdict provenance multi-anchor AND (Orchestrator gate self-write 시점) — **(a)/(b) retro-time 영역과 disjoint axis** (gate verdict provenance vs retro corpus/ADR draft)

**Multi-anchor AND (2 anchor 모두 충족 의무)** — ADR-026 §결정 6 isPostMergeFix 3-조건 AND (label ∧ Story §10 binding ∧ §7 보안 non-touch) single-point-of-forgery 제거 mechanism 답습:

| # | anchor | mechanical 판정 | trust anchor |
|---|---|---|---|
| 1 | lane-produced machine-checkable artifact | 해당 lane 의 review-verdict-v4 packet 이 형식 준수 + 필수필드 (`contract_version` / `lane` / `story_key` / `iteration` / `pl_recommendation`) 존재 + `pl_recommendation` ∈ {PASS, FIX, FIX_DISCRETIONARY} (gate-pass label 시 = PASS) | ReviewPL synthesis 산출 (review-verdict-v4 contract, ADR-022 §결정 4 gate outcome SSOT) |
| 2 | Story §14 lane-evidence binding | Story §14 Lane Evidence 에 해당 lane row 존재 + `output_status: completed` + `outcome: PASS` 정합 (ADR-031 §결정 1 committed evidence) | Orchestrator self-write committed audit trail (위조 시 PR diff 노출) |

**wrapper-self `mixed` repo 면제 처리** (ADR-031 §14 `mixed` repo-kind 면제 정합): wrapper-self dogfood repo (`mixed` repo-kind — Story SSOT = codeforge-internal-docs binding, §14 advisory-red 면제 영역) 는 anchor 2 의 §14 binding 대신 **Phase 1/2 PR body 또는 gate-pass comment 안 review-verdict-v4 packet block embed** 를 병행 anchor 로 충당. 면제는 `mixed` 한정 — consumer / plugin / unknown repo-kind 의 §14 binding 은 면제 대상 아님 (ADR-031 §14 회귀 보존 invariant 정합).

**위협모델 = honest-but-careless (연극 게이트 차단)**:
- 본 sub-decision (c) 이 차단하는 표면 = **실수/부주의** 영역 — (1) 빈 verdict 또는 artifact 부재인데 gate-pass label 부착 (2) review-verdict packet 형식 위반인데 PASS 승격 (3) §14 row 부재인데 lane PASS 단언 (Pattern A-2 형 false self-attest 의 mechanical 표면).
- **악의 단일계정 위조 = out-of-scope (accepted risk, 명시 박제)**: single-session·single-account 환경 (dogfood wrapper-self) 에서는 git author 기반 implementer≠certifier separation 이 구조적으로 불가 — 동일 operator 가 artifact 와 verdict 를 모두 위조하면 multi-anchor AND 도 우회 가능. 이 영역 mitigation (별도 attestation 서명 / 외부 certifier) 비용 > 이득 (single-operator dogfood). **accepted risk 로 수용** — 본 gate 는 honest-but-careless 만 차단, malicious forgery 는 차단 못 함을 명시 declare (검사 연극 회피 — 막지 못하는 것을 막는 척 금지).

**적용 범위 = 모든 게이트**: 요구사항리뷰 (ADR-125 신규 9번째 lane — S2 carrier CFP-2326 의 self-attest 구멍 공동 차단) / 설계리뷰 / 보안테스트 / 배포리뷰 (`phase:배포-리뷰` 시 이미 required, phase-gate-mergeable.yml:488-490 — provenance anchor 추가). gate verdict self-write 가 발생하는 모든 lane 의 gate-pass label/comment 에 적용.

**posture = warning-first → ratchet**:
- **Phase 1 (본 Amendment, declarative anchor)**: sub-decision (c) 신설 + multi-anchor AND schema codify + `mixed` 면제 병행 anchor 규칙 codify. mechanical enforce 부재 (declaration-only).
- **Phase 2 (advisory CI 경고, mechanical wire — 별 sub-CFP / S6 Phase 2 carrier defer)**: gate-pass label 부착 PR 에서 multi-anchor 부재 detect 시 **warning tier emit + PR comment advisory** (merge 미차단 — ADR-026 Amendment 5 §결정 7 content-sanity warning tier 패턴 동형). fast-pass OR-gate 무변경 invariant 보존.
- **hard-block 승격 = 별 follow-up Story** (ADR-060 §결정 6 promotion gate AND 3/3 충족 후 — ratchet 강화 방향만, 약화 0).

**gate label authority SSOT 무변경 (신규 ADR 발의 안 함)**: gate label registry authority = 기존 SSOT 유지 (ADR-022 §결정 4 review-verdict gate outcome contract-fixed `PASS|FIX` + `templates/labels/base-labels.tsv` gate:* registry). 본 sub-decision (c) = provenance 예방형 layer 추가일 뿐 gate label 정의 SSOT 신설 아님. **신규 gate-provenance ADR 발의 안 함** — 3문 게이트 (① 깨졌나: Pattern A reactive-only 갭 존재 ② 이득>비용: 신규 ADR governance surface 추가 비용 > §D-9 sub-decision 확장 이득 ③ 관찰자 없어도 할 일: yes) 적용 결과 = ADR-045 §D-9 sub-decision 확장으로 충분.

**근거**: ADR-045 §D-9 forcing function 의 **temporal axis 확장** — 기존 (a)/(b) retro-time post/pre-publish 영역에 (c) gate-write-time preventive 영역 추가. Pattern A reactive self-discipline (ADR-082 / ADR-073) 의 merge-time mechanical preventive 보완. Industry analog = K8s admission webhook (write-time validation) / GitHub branch protection required status checks (merge-time gate) / supply-chain provenance attestation (SLSA build provenance, source: https://slsa.dev/spec/v1.0/provenance — artifact ↔ verdict binding 원리). multi-anchor AND single-point-of-forgery 제거 = ADR-026 §결정 6 답습.

**paired sibling cross-ref**:
- S7 (CFP-2331, ADR-014 Amendment 6) = 동일 Epic CFP-2324 gate-model 일관 설계 묶음 (phase-gate-mergeable.yml 게이트 매핑·검증 로직 공유 — 단일 설계로 처리)
- ADR-026 §결정 6 (isPostMergeFix 3-조건 AND) = multi-anchor AND single-point-of-forgery 제거 mechanism 답습
- ADR-031 §결정 1 + §14 (committed lane evidence + `mixed` repo 면제) = anchor 2 trust source
- ADR-022 §결정 4 (review-verdict gate outcome contract-fixed) = anchor 1 gate label authority SSOT (무변경)
- ADR-082 §결정 1 (write-time self-write verify) + ADR-073 (verify-before-assert) = reactive self-discipline layer (본 (c) preventive 와 disjoint axis — self-discipline vs mechanical gate)
- docs/agent-prompt-guardrails.md:26 (Pattern A 명칭 SSOT, carrier CFP-1353) = carrier source citation

## D-12 — phase:완료 transition precondition 에 worktree-clean self-check 추가 (Amendment 13, CFP-2377, 2026-06-20)

ADR-128(완료 단계 정식화) 의 갭 A 해소 carrier 의 ADR-045 측 amendment. ADR-040 Amendment 9(backstop SessionEnd 트리거 + §결정 7.K worktree-clean cleanup invariant) 와 paired sibling.

### §13.A — precondition 확장 (2-gate AND → 2-gate + worktree-clean self-check)

`phase:완료` transition 의 기존 precondition (playbook §9.7.1 line 2858 SSOT):

> **precondition AND**: 활성 lane 의 terminal gate (`gate:design-review-pass` default, deploy lane 활성 시 `gate:deploy-review-pass`) + `gate:retro-complete`

본 Amendment 13 이 worktree-clean self-check 1항을 추가한다:

> **precondition AND**: 활성 lane terminal gate + `gate:retro-complete` + **worktree-clean self-check** (완료 Story 의 worktree 가 eager 정리됐는가)

- worktree-clean self-check = **eager 미실행 검출 게이트** (정리 실행 owner = GitOpsAgent eager 불변, 본 게이트는 검증만 — ADR-040 가정 1).
- backstop(check-worktree-stale.sh, age 7d+)과 **다른 검사** — 완료 worktree 는 0일령이라 age 7d 조건과 충돌하지 않는다 (AC-3, 2-layer 책임 분리 = ADR-040 Amendment 9 §결정 7.K 표).

### §13.B — tier = Orchestrator behavioral precondition (required CI 불가)

`phase:완료` transition = Orchestrator self-write(로컬) + worktree 클라우드 러너 미접근 → **required CI check 불가** (AC-2/AC-12). 3-조합 기계화:

1. **(a) Orchestrator behavioral precondition** — playbook §9.7.1 `phase:완료` precondition 행에 worktree-clean self-check 1항 추가 (본 §13.A).
2. **(b) 로컬 check 스크립트** — `scripts/check-worktree-completion-clean.sh` (Phase 2). fail-safe 4종 상속 (ADR-040 Amendment 9 §결정 7.K — gh 미인증 보존 / dirty 보존 / data-loss 가드 / always exit 0).
3. **(c) evidence-checks-registry 등록** — warning-tier + `workflow: null` (ADR-099/ADR-122 local-only 선례 동형, `# CI 미wire — standalone manual / 세션-개시 호출` marker).

**branch protection 6-tuple 무변경** — 신규 required check 0 → ADR-024 Amendment 19 §B "required check bypass escape valve 신설 금지" invariant 원천 정합. **`gate:worktree-clean` label 신설 안 함** — 사용자 방향 "기존 게이트 확장", label 없이 Orchestrator self-check (가벼운 forcing function).

### §13.C — close lifecycle 무영향 (#772 EC-5 정합)

worktree-clean self-check 는 `phase:완료` **transition precondition** (label attach 직전)이지 Issue **close 차단(reopen)** 이 아니다. `retro-mandatory.yml` 의 `gate:retro-complete` close-blocking auto-reopen(§결정 5, line 376-456) 과 **axis disjoint** — worktree-clean 은 reopen trigger 가 아니다.

- #772(OPEN, close-event auto-reopen 일반화 forcing function) 와 정합 — 본 게이트가 close lifecycle 에 **새 reopen 경로를 추가하지 않음** (중복 reopen / reopen 충돌 0).
- ADR-045 §결정 5 close-blocking + §D-6 `gate:retro-complete` entry **의미 변경 0** — precondition 에 self-check 1항 추가만.

### 정합성 검증

- **ADR-128 정합**: 본 Amendment 13 = ADR-128 §결정 2(완료-게이트) 의 ADR-045 측 carrier. ADR-040 Amendment 9 와 paired sibling.
- **ADR-040 Amendment 9 정합**: §결정 7.K(worktree-clean cleanup invariant 2-layer) 와 동일 검사를 phase:완료 precondition 으로 wire — fail-safe / 순서 invariant(EC-3) / sub-worktree vs Story root 구분(EC-2) 상속.
- **ADR-058 §결정 5 정합**: precondition 1항 추가 = strengthening direction (ratchet) — `is_transitional: false` permanent. amendment_log id:13 `sunset_justification: null` + `direction: strengthening`.
- **ADR-024 Amendment 19 §B 정합**: required 6-tuple 신설 0 → bypass 신설 금지 invariant 원천 정합.
- **ADR-099 / ADR-122 정합**: `workflow: null` local-only check 선례 동형.
- **ADR-127 정합**: forcing function 추가 방향 (process-skip 채널 0). worktree-clean self-check 미통과 = 정리 후 재확인이지 "생략 후 진행" 아님.
- **ADR-009 invariant 무손상**: precondition 추가 + 로컬 check + registry entry — wrapper agent 신설 0.
- **ADR-045 §결정 1-8 + §D-9~D-11 무손상**: §D-12 sub-section 추가만, 기존 결정 변경 없음.

## D-13 — phase:완료 transition precondition 에 capture self-check 추가 (Amendment 14, CFP-2392, 2026-06-24)

ADR-129(OMC-adopt 지식캡처 + 메모리 다이어트) 의 갭 A(capture timing 공백) 해소 carrier 의 ADR-045 측 amendment. ADR-071 Amendment 12(§18.7 MEMORY.md 슬림화 mechanism deferred 해제) 와 paired sibling. ADR-128 Amendment 13 §D-12(worktree-clean self-check) 와 **동형 구조** — 둘 다 phase:완료 local-only warning-tier self-check.

### §14.A — precondition 확장 (§D-12 worktree-clean + capture self-check)

`phase:완료` transition 의 precondition (§D-12 이후 SSOT):

> **precondition AND**: 활성 lane terminal gate + `gate:retro-complete` + worktree-clean self-check (§D-12)

본 Amendment 14 가 capture self-check 1항을 추가한다:

> **precondition AND**: 활성 lane terminal gate + `gate:retro-complete` + worktree-clean self-check + **capture self-check** (이번 Story 에서 재사용 가능한 지식이 외부화됐는가)

- capture self-check = **완료시점 재사용지식 외부화 검출 게이트** — capture artifact (신규 `skills/<slug>/SKILL.md` 또는 `docs/domain-knowledge/.../*.md`) **OR** 명시적 no-capture note(`"캡처 대상 검토 완료 — 외부화 불요(사유)"` 1줄) 흔적을 검사. 둘 다 부재 = WARN (silent skip 금지 = forced-no-silent-skip, ADR-129 §결정 1(4)).
- 3문 admission(구글5분 / 코드베이스특정 / 실제노력 — OMC skillify(MIT) 차용)은 **semantic judgment** → behavioral (Orchestrator self-eval). lint 은 "흔적 존재"만 presence 검사 (Story §8.3 anti-theater 분류).

### §14.B — tier = Orchestrator behavioral precondition (required CI 불가)

`phase:완료` transition = Orchestrator self-write(로컬) + 완료 marker = working-tree 검출 → **required CI check 불가**. 3-조합 기계화 (§D-12 / ADR-128 §결정 2 답습):

1. **(a) Orchestrator behavioral precondition** — playbook §9.7.2 완료 단계 수렴 SSOT 에 capture self-check pointer 1줄 + 본 §14.A.
2. **(b) 로컬 check 스크립트** — `scripts/check-capture-gate-completion.sh` (Phase 2). fail-safe = git/gh 미인증 시 exit 0 보존 (data-loss 가드, hard-block 금지) / 완료 marker 부재 시 exit 0 no-op.
3. **(c) evidence-checks-registry 등록** — warning-tier + `workflow: null` (`knowledge-capture-completion-gate`, ADR-099/ADR-122/ADR-128 local-only 선례 동형).

**branch protection 6-tuple 무변경** — 신규 required check 0 → ADR-024 Amendment 19 §B "required check bypass escape valve 신설 금지" invariant 원천 정합. **`gate:capture` label 신설 안 함** — ADR-128 §D-12 worktree-clean label 미신설 패턴 답습 (label 없이 Orchestrator self-check).

### §14.C — axis-disjoint vs §D-9 retro (흡수 거부, ADR-129 NEW umbrella 정당)

본 capture self-check 는 §D-9 retro 와 **3축 disjoint** 라 §D-9 로 흡수 불가:

| 축 | capture self-check (본 §D-13) | §D-9 retro |
|---|---|---|
| TIMING | pre-completion forcing (완료 직전) | post-hoc (Phase 2 PR merge 후) |
| UNIT | single-task (이번 작업) | multi-Story (cross-Story pattern) |
| OUTPUT | skill / domain-knowledge artifact | ADR escalation |

→ ADR-129 NEW umbrella (ADR-128 archetype 답습 — 흡수 거부 + paired Amendments). ADR-045 §결정 5 close-blocking + §D-6/§D-12 entry **의미 변경 0** (precondition 1항 추가만).

### 정합성 검증 (§D-13)

- **ADR-129 정합**: 본 Amendment 14 = ADR-129 §결정 1(완료시점 capture 게이트) 의 ADR-045 측 carrier. ADR-071 Amendment 12 와 paired sibling.
- **ADR-128 §D-12 동형**: worktree-clean self-check 와 동일 구조(phase:완료 local-only warning-tier self-check + fail-safe + required CI 불가) — 3-조합 기계화·tier·label 미신설 상속.
- **ADR-058 §결정 5 정합**: precondition 1항 추가 = strengthening direction (ratchet) — amendment_log id:14 `sunset_justification: null` + `direction: strengthening`.
- **ADR-024 Amendment 19 §B 정합**: required 6-tuple 신설 0 → bypass 신설 금지 invariant 원천 정합.
- **ADR-099 / ADR-122 / ADR-128 정합**: `workflow: null` local-only check 선례 동형.
- **ADR-127 정합**: forcing function 추가 방향 (process-skip 채널 0). capture self-check 미통과 = 외부화(또는 no-capture note) 후 재확인이지 "생략 후 진행" 아님.
- **ADR-119 정합 (통합 금지)**: 3문 admission 과 ADR-119 §결정 9 제안 필요성 3문 게이트는 동형이나 도메인 disjoint(지식 캡처 ↔ 작업 제안) → 통합 금지, cross-ref 만.
- **ADR-045 §결정 1-8 + §D-9~D-12 무손상**: §D-13 sub-section 추가만, 기존 결정 변경 없음.

## 해소 기준

N/A — permanent policy

## 관련 파일

- `templates/github-workflows/retro-mandatory.yml` (신규)
- `templates/github-workflows/post-merge-followup.yml` (미터치, ADR-026 보존)
- `templates/github-workflows/phase-label-invariant.yml` (`enforce-terminal-on-close` job 동시 동작)
- `templates/story-page-structure.md` §11 schema 갱신
- `docs/inter-plugin-contracts/label-registry-v1.md` v1.4 → v1.5
- `docs/inter-plugin-contracts/MANIFEST.yaml` label-registry-v1 entry update
- `scripts/bootstrap-labels.sh` 1줄 추가 + echo string 갱신
- `CLAUDE.md` "Story 작성 의무" + "Lane plugin self-write boundary" cross-ref minimal 추가
- `<internal-docs>/wrapper/change-plans/2026-05-09-cfp-138-retro-mandatory.md` (Change Plan)
- `<internal-docs>/wrapper/stories/CFP-138.md` §3·§7·§11 채움

## 관련 ADR

- **ADR-009** wrapper-only decomposition: 본 ADR 는 PMOAgent (codeforge-pmo lane plugin) mandate amendment + workflow 추가. wrapper agent 0개 invariant 무손상.
- **ADR-013** codeforge family dogfood-out policy: retro file write target = `<internal-docs>/<plugin-folder>/retros/`. wrapper repo `docs/retros/` 부재 정합.
- **ADR-022** Sonnet decider Comprehensive Policy (**Deprecated 2026-05-08**, CFP-134): 본 ADR 의 retro 자동 trigger 의무화 = ADR-022 deprecate framing (사용자 turn 9 directive) 의 일부.
- **ADR-024 + Amendment 1** Story-scoped branch policy: retro-mandatory.yml = PR merge event trigger only. main 직접 push 차단 invariant 무손상.
- **ADR-025 Amendment 1** Stop discipline + Epic-level continuity: 본 ADR 의 retro 자동 trigger = stop discipline 의무화 (사용자 매번 stop 발화 불필요). §결정 7 `policy_violation_subdecision` 차단 정합.
- **ADR-026** Post-merge follow-up automation: retro-mandatory.yml = 별도 workflow 분리 (D-2). disable-by-flag invariant 공유 (D-7). PAT scope 정합 (D-1).
- **ADR-031** Lane evidence: retro = lane 외 phase. §14 lane enum 미수정 (영향 없음).
- **ADR-035** codeforge agent teams Epic SSOT: 본 ADR = D5 Foundation 결정 implementation. amendment_log[] 에 `amendment_id: 2 (CFP-138)` 추가 의무 (CFP-137 first merge 시 본 lane rebase + amendment_id 다음 값으로 갱신).
- **ADR-039** Orchestrator subagent default: retro 자동 trigger 동작 = Orchestrator → PMOAgent subagent spawn (inline write 금지). 본 ADR 정합.
- **ADR-082** Write-time self-write verification mandate: Amendment 6 — §D-9 cross_story_pattern_adr_trigger forcing function 이 cross-Story pattern_count 3 ≥ threshold 2 → escalation_action escalate_user → ADR-082 산출. §D-9 가 명목상 존재가 아니라 실제 동작한 첫 cross-Story 산물 evidence. ADR-082 §결정 1 layer disjoint 표가 ADR-045 §D 를 "retro corpus enumeration" layer 로 명시. 충돌 0 (evidence-only Amendment).
