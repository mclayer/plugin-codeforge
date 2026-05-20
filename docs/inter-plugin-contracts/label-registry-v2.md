---
kind: registry
registry: label
version: "2.40"
status: Active
supersedes: label-registry-v1.md
created_by: CFP-140
created_date: 2026-05-09
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/label-registry-v2.md
date: 2026-05-20  # CFP-1041 v2.40 — Multi-session collaboration protocol carrier (ADR-085 §결정 8 deferred-followup mechanical_enforcement_actions[] 2-entry sibling labels): hotfix-bypass:active-sessions-presence 51번째 + hotfix-bypass:lane-entry-ownership-verify 52번째 family member (raw active concrete grep count convention 답습, v2.39 baseline 50 → +2 → 52 / parallel session bump 시 ratchet). MINOR bump: 2 신규 entry, kind:registry sibling sync 면제 (ADR-010 §결정 2 + ADR-008 §결정 3 row append). plugin.json MINOR bump 동반 (governance behavior 변경 ADR-037 정합, marketplace_sync_declared: true ADR-063 atomic invariant). MANIFEST.yaml row "2.39" → "2.40" ratchet 동반. ADR-024 Amendment N §결정 6.A per-entry namespace 정합 carrier (CFP-1041 신규 family member 2 row). 8 parallel race incidents single session lineage (CFP-953/946/949/932/954/991/967/1014, 2026-05-18 ~ 2026-05-19 KST) 산물 ADR-045 §D-9 cross_story_pattern_adr_trigger escalation. | CFP-1006 v2.39 — Tier-B 4-way sync bidirectional drift sweep (Wave 1): 4 신규 entry registry-side late codify (gh→registry missing: hotfix-bypass:comment-prefix-registry 47번째 + hotfix-bypass:epic-cutover-quad-check 48번째 + hotfix-bypass:evidence-naming 49번째 + hotfix-bypass:markdown-internal-links 50번째 family member, raw active concrete grep count convention 답습 = CFP-1000 Amendment 10 precedent) + 1 naming mismatch resolution (registry §3 entry rename hotfix-bypass:claude-md-amendment-ref → hotfix-bypass:claude-md-amendment-ref-drift, conservative direction matches gh repo label + workflow filename claude-md-amendment-ref-drift.yml + 12+ PR audit history). 35 of 36 registry→gh missing 자동 해소 expected via bootstrap-labels.yml workflow PR open auto-fire (CFP-598 dynamic registry-driven pattern via parse-hotfix-bypass-labels.py). Pivot finding (write-time): registry-only 36 (Issue body said 35) + gh-only 5 (Issue body match) + 1 naming mismatch = 42 raw drift (Issue body 41 — 1 entry shift between morning verification ↔ pre-spawn verify-before-trust). MINOR bump: 4 신규 entry + 1 rename (net 5 §3 changes, raw count 47→51 — exempt:<entry> template 1 + active 46 in CFP-1000 stale → 51 post-rename + 4 new active). kind:registry sibling sync 면제 (ADR-010 §결정 2 + ADR-008 §결정 3 row append). plugin.json bump 0 = marketplace_sync_declared: false. MANIFEST.yaml row "2.38" → "2.39" ratchet 동반. ADR-024 Amendment 11 §결정 6.A per-entry namespace 정합 carrier. issue_origin: orchestrator_authored_followup (ADR-082 Amendment 2 §2.1 carrier — CFP-1000 retro PMOAgent-authored). | CFP-1000 v2.38 — hotfix-bypass:prod-cutover-deputy-evidence 45번째 (raw) family member registry-side late codify (CFP-954 carrier originally registered in gh repo at PR-time but missed registry §3 declaration — bidirectional drift Tier-A closure, CFP-963 retro 식별 + CFP-1000 Tier-A carrier). collision rebase ratchet: CFP-991 parallel session main 점유 v2.35 → CFP-1000 = v2.38 (CFP-967 v2.36 + CFP-991 v2.37 absorbed). MINOR bump: 1 신규 entry, kind:registry sibling sync 면제 (ADR-010 §결정 2 + ADR-008 §결정 3 row append), plugin.json bump 0. MANIFEST.yaml row "2.37" → "2.38" ratchet 동반. | CFP-967 v2.36 — hotfix-bypass:parallel-work-sentinel-pickup 45번째 family member (ADR-073 Amendment 2 §결정 1 mechanical enforcement parallel work sentinel warning-tier bypass channel, CFP-967 Phase 2 carrier, MINOR bump: 1 신규 entry, kind:registry sibling sync 면제, plugin.json MINOR bump 동반). parallel race absorbed into CFP-1000 v2.38 rebase ratchet. | CFP-991 v2.37 — Wave 4 sub-Epic #1 Story-4 carrier (4 신규 entry: 1 hotfix-bypass:canary-promotion-criteria 46번째 family member + 3 gate:channel-canary-promotion + gate:channel-beta-promotion + gate:channel-stable-promotion, MINOR bump, kind:registry sibling sync 면제 ADR-010 §결정 2, plugin.json bump 0). MANIFEST.yaml row "2.34" → "2.35" ratchet 동반. canary promotion criteria enforcement layer (reconcile-protocol-v1 v1.10 → v1.11 §4.14 canary_compatibility_check_binding block 신설 sibling carrier). | CFP-954 v2.34 — Wave 4 sub-Epic #882 Story-3 carrier (1 신규 entry: production-touching + 신규 category enum: production-impact, MINOR bump, kind:registry sibling sync 면제, plugin.json bump 0). CFP-949 v2.33 collision rebase ratchet (parallel session #975 main 점유 → CFP-954 = 다음 MINOR v2.34, dual-carrier 보존). MANIFEST.yaml row "2.33" → "2.34" ratchet 동반. | CFP-949 v2.33 — Sub-Epic 6 lane plugin self-owned architecture doc seed 신설 5 label family member (parent:CFP-949 + plugin:codeforge-{requirements,design,develop,test} 4 lane plugin namespace) (MINOR bump: 5 신규 entry, plugin.json bump 0 = kind:registry sibling sync 면제, ADR-010 §결정 2) | CFP-923 v2.32 — hotfix-bypass:architecture-drift 43번째 family member (Epic B Story-4 ADR-078 P-S4 mechanism — docs/architecture/**/*.md 4 H2 closed-enum + 3 detection class lint warning-tier, MINOR bump: 1 신규 family member, plugin.json bump 0 = kind:registry sibling sync 면제) | CFP-932 v2.31 — hotfix-bypass:channel-drift-detection 42번째 family member (Wave 4 sub-Epic #1 Story-2 — channel-drift-detection.yml workflow + check-channel-drift.sh warning-tier bypass channel, ADR-063 Amendment 3 §결정 13 marketplace-drift-detection precedent 답습, MINOR bump: 1 신규 family member 추가, plugin.json bump 0 = kind:registry sibling sync 면제) | CFP-906 v2.30 — channel:* 3 신규 family (stable/beta/canary) + 신규 category enum `channel` (Wave 4 sub-Epic #1 Story-1 multi-version channel pin declare layer, Epic CFP-882 / ADR-076 §결정 9 + ADR-016 Amendment 3 + ADR-063 Amendment 6 §결정 17 carrier, MINOR bump: 3 신규 entry + 신규 category enum) | CFP-894 v2.29 — hotfix-bypass:inter-plugin-contracts-parity 41번째 family member (ADR-010 / CFP-894 carrier — MANIFEST↔frontmatter INV-1 parity warning-tier lint bypass channel, MINOR bump: 1 신규 family member 추가) | CFP-842 v2.28 — hotfix-bypass:fix-event-depth-scope 40번째 family member (ADR-067 Amendment 1 §결정 4 carrier — fix-event-v1 v1.3 depth-aware scope presence warning-tier lint bypass channel, MINOR bump: 1 신규 family member 추가) | CFP-845 v2.27 — hotfix-bypass:per-plugin-cumulative-counter 37번째 + hotfix-bypass:bypass-justification-marker 38번째 + hotfix-bypass:cross-repo-bypass-counter 39번째 family member (ADR-024 Amendment 8 §결정 6.A.3/6.A.4/6.A.5 carrier — bypass-as-norm-mutation 후속 escalation 3 sub-decision 통합 Phase 1, MINOR bump: 3 신규 family member 동시 추가) | CFP-821 v2.26 — hotfix-bypass:branch-protection-sync 36번째 family member (CFP-821 D2 evidence-check bypass channel, MINOR bump — CFP-841 v2.25 선점으로 충돌 해소 rebase, 34→36번째 재번호) | CFP-841 v2.25 — hotfix-bypass:corpus-claim-verify 34번째 + hotfix-bypass:cross-plugin-ownership-verify 35번째 family member (ADR-024 Amendment 7 / ADR-082 Amendment 1 §결정 6 behavioral→mechanical 전환 carrier — corpus annotation lint scope 2(a) + cross-plugin ownership queryable scope 2(d), MINOR bump: 2 신규 family member 동시 추가) | CFP-820 v2.24 — hotfix-bypass:version-3way-atomic 33번째 family member (ADR-063 Amendment 5 §결정 16 carrier — 3-way version atomic invariant blocking-on-pr bypass channel, MINOR bump) | CFP-825 v2.23 — hotfix-bypass:bypass-label-counter 31번째 + hotfix-bypass:exempt:<entry> 32번째 family member (ADR-024 Amendment 6 §결정 6.A.2 carrier — per-entry namespace 누적 사용 카운터 lint ratchet 룰 + bypass-as-norm mutation 누적 monitoring 첫 진입, MINOR bump: 2 신규 family member 동시 추가) | CFP-785 v2.22 — hotfix-bypass:adr-077-ratchet 29번째 + hotfix-bypass:adr-077-design-reading 30번째 family member (v2.21 CFP-795 collision rebase: PATCH re-index v2.22) | CFP-795 v2.21 — post-merge-fix fast-pass source label 신설 (ADR-026 Amendment 4 §결정 6 carrier — cross-repo post-merge hotfix 3-조건 AND fast-pass gate 조건 1, MINOR bump: 신규 fast-pass category 신설) | CFP-722 v2.20 — hotfix-bypass:story-section-ownership 28번째 family member (ADR-060 Amendment 13 §결정 27 carrier — Story per-section ownership mechanical lint warning-tier, CFP-722 Phase 2 rebase post-CFP-771) | CFP-771 v2.19 — hotfix-bypass:kst-timestamp-display 27번째 family member (ADR-079 Amendment 1 carrier — KST timestamp display mechanical lint warning-tier, CFP-771) | CFP-702 v2.18 — hotfix-bypass:wrapper-managed-block 26번째 family member (ADR-027 Amendment 3 §결정 7.D carrier — D4 customization marker block lint blocking-on-pr, CFP-699 Wave 1 Story-2) | CFP-688 v2.17 — hotfix-bypass:actionlint 24번째 + hotfix-bypass:post-merge-followup-success-rate 25번째 family member (ADR-026 Amendment 3 §결정 5.G.b + §결정 5.G.d carriers — actionlint prevention layer + KPI detection sentinel, CFP-688 Phase 2 sub-PR (c)) | CFP-708 Phase 2 v2.16 back-ref: hotfix-bypass:claude-md-amendment-ref 23번째 family member (see below) | CFP-685 v2.16 — hotfix-bypass:auto-phase-label-sibling-parity 22번째 family member (ADR-065 §결정 1 row 3 carrier — templates ↔ self-app byte-identical parity warning-tier entry, CFP-609 retro Finding D carrier) | CFP-662 v2.15 — hotfix-bypass:bootstrap-labels 21번째 family member (ADR-060 Amendment 10 §결정 24 carrier — PR-time precondition check pattern 의 첫 baseline, RETRO-MCT-104 carrier 정합) | CFP-660 v2.14 — hotfix-bypass:workflow-version-drift 20번째 family member (ADR-032 Amendment 2 §결정 6 carrier — strict-eligible 5번째 drift consumer workflow version drift, CFP-660 Wave 2 of Epic CFP-431) | CFP-658 v2.13 — fallback:* family 신설 (fallback:manual + fallback:rate-limited, ADR-027 Amendment 2 §결정 6 carrier — Action-blocked agent direct write fallback path normative SSOT, post-CFP-627 v2.12 atomic rebase) | CFP-627 v2.12 — hotfix-bypass:marketplace-drift-detection 19번째 family member (ADR-063 Amendment 3 §결정 13 carrier — marketplace reactive scheduled drift detection 4th defense layer, post-CFP-638 base) | CFP-638 v2.11 — hotfix-bypass:stop-time-continuous-confirm 18번째 family member (ADR-064 Amendment 3 §결정 9 sister carrier — Continuous '진행해' 패턴 mechanical detect advisory channel) | CFP-631 v2.10 — hotfix-bypass:marketplace-description-verbatim 17번째 family member (ADR-063 Amendment 2 carrier — description proactive PR-time lint blocking-on-pr 직접 시작) | CFP-628 v2.9 — hotfix-bypass:retro-alert-pickup 16번째 family member (ADR-045 §D-5 retro alert pickup KPI warning-tier sentinel) | CFP-619 v2.8 — hotfix-bypass:retro-mandatory-deployed 15번째 family member (ADR-045 mandate restoration carrier) | CFP-610 v2.6 sub-entry — hotfix-bypass:wording-dictionary 13번째 (ADR-064 Amendment 2) | CFP-582 v2.6 sub-entry — hotfix-bypass:debate-convergence-quality 12번째 (ADR-059 Amendment 2 §결정 8) | CFP-583 v2.6 sub-entry — hotfix-bypass:workflow-yaml-parse 11번째 | CFP-530 v2.5 sub-entry — hotfix-bypass:workflow-permissions 10번째 | CFP-429 v2.5 — from-cfp-425-followup provenance label | CFP-521 v2.4 sub-entry — hotfix-bypass:sibling-pr-author-check 9번째 | CFP-506 v2.4 sub-entry — hotfix-bypass:claude-md-line-cap 8번째 | CFP-481 v2.4 — phase:* attach_owner_plugin field 갱신
authors:
  - Claude (CFP-140 — ADR-049 type:* → native Issue Types cutover)
related_adrs:
  - ADR-008 (contract versioning — MAJOR bump = label hack removal)
  - ADR-049 (CFP-140 — Issue Types native migration)
  - ADR-009 (CFP-31 — wrapper agent 0 invariant)
  - ADR-030 (CFP-123 — gate:live-entry-pass v1.3)
  - ADR-036 (CFP-260 — phase:reservation v1.4)
  - ADR-045 (CFP-138 — gate:retro-complete v1.5)
  - ADR-050 (CFP-344 — conflict:* + merge-order:* labels v2.1)
  - ADR-057 (CFP-393 — codeforge-kpi-alert + monitoring tier v2.2)
  - ADR-060 (CFP-393 — framework first non-sunset application + CFP-481 Amendment 4 — 3rd warning-tier entry auto-phase-label carrier)
  - ADR-005 (CFP-451 — self-application byte-identical .github/workflows copy)
  - ADR-024 (CFP-481 Amendment 4 — branch → phase mapping 표 SSOT + hotfix-bypass:auto-phase-label 7번째 family member)
  - ADR-012 (CFP-506 Amendment 1 — cap ratchet ≤320 + §3 scope 4-층 재해석)
  - ADR-051 (CFP-506 Amendment 1 — Draft → Accepted + anchor vs reference 판정자)
  - ADR-060 Amendment 5 (CFP-506 — 4th warning-tier entry claude-md-line-cap + hotfix-bypass:claude-md-line-cap 8번째 family member)
  - ADR-010 (CFP-521 Amendment 4 §결정 5 anti-misuse 안전망 — 5th warning-tier entry sibling-pr-label-author-check + hotfix-bypass:sibling-pr-author-check 9번째 family member)
  - ADR-040 Amendment 4 (CFP-429 — worktree-first enforcement closing the loop declaration carrier, gate FAIL 분기 후속 carrier `from-cfp-425-followup` provenance label 신설)
  - ADR-060 §결정 6 (CFP-429 — promotion gate 평가 FAIL = warning tier 유지 + actual 승격 follow-up CFP open mandate)
  - ADR-060 Amendment 8 (CFP-530 — N번째 warning-tier entry workflow-permissions-block-presence + hotfix-bypass:workflow-permissions 10번째 family member)
  - ADR-060 Amendment 9 (CFP-583 — 7th warning-tier entry workflow-yaml-parse + hotfix-bypass:workflow-yaml-parse 11번째 family member + 6 workflow yml BODY heredoc anti-pattern 정정 + framework zero-coverage sentinel 회복)
  - ADR-059 Amendment 2 (CFP-582 — convergence_quality_invariant 3 marker mechanical enforcement + debate-convergence-quality-marker-presence warning-tier entry + hotfix-bypass:debate-convergence-quality 12번째 family member)
  - ADR-024 Amendment 5 (CFP-582 — §결정 6.A per-entry namespace 의 12번째 family member hotfix-bypass:debate-convergence-quality 추가)
  - ADR-064 Amendment 2 (CFP-610 — wording-dictionary lint warning-tier entry + hotfix-bypass:wording-dictionary 13번째 family member)
  - ADR-045 §D-5 (CFP-628 Story 2 — retro alert pickup KPI warning-tier entry + hotfix-bypass:retro-alert-pickup 16번째 family member, ADR-060 framework 42번째 entry)
  - ADR-045 (CFP-619 — retro-mandatory.yml workflow byte-identical mirror deployment mandate restoration carrier + hotfix-bypass:retro-mandatory-deployed 15번째 family member, ADR-060 framework 41번째 entry)
  - ADR-005 (CFP-619 — templates/** ↔ .github/workflows/** byte-identical self-application invariant SSOT, retro-mandatory.yml mirror anchor)
  - ADR-063 Amendment 2 (CFP-631 — marketplace description verbatim PR-time proactive lint blocking-on-pr 직접 시작 carrier + hotfix-bypass:marketplace-description-verbatim 16번째 family member)
  - ADR-032 Amendment 2 (CFP-660 — strict-eligible 5번째 drift consumer workflow version drift, check 10 NEW carrier + hotfix-bypass:workflow-version-drift 20번째 family member, Wave 2 of Epic CFP-431)
  - ADR-060 Amendment 10 (CFP-662 — 10번째 warning-tier entry bootstrap-labels-precondition + hotfix-bypass:bootstrap-labels 21번째 family member + PR-time precondition check pattern 의 첫 baseline + RETRO-MCT-104 carrier)
  - ADR-065 §결정 1 row 3 (CFP-685 — templates ↔ self-app byte-identical parity warning-tier entry auto-phase-label-sibling-parity + hotfix-bypass:auto-phase-label-sibling-parity 22번째 family member, CFP-609 retro Finding D carrier)
  - ADR-024 Amendment 6 (CFP-825 — §결정 6.A.2 per-entry namespace 누적 사용 카운터 lint ratchet 룰 + hotfix-bypass:bypass-label-counter 31번째 + hotfix-bypass:exempt:<entry> 32번째 family member + ADR-060 framework 63번째 evidence-checks-registry entry, CFP-771 retro §8 제안 1 carrier — bypass-as-norm mutation 누적 monitoring 첫 진입)
  - ADR-063 Amendment 5 (CFP-820 — §결정 16 carrier — 3-way version atomic invariant blocking-on-pr bypass channel + hotfix-bypass:version-3way-atomic 33번째 family member, §결정 15 version-3way-atomic evidence-checks-registry entry)
  - ADR-024 Amendment 7 (CFP-841 — §결정 6.A per-entry namespace 확장 — hotfix-bypass:corpus-claim-verify 34번째 + hotfix-bypass:cross-plugin-ownership-verify 35번째 family member, ADR-082 Amendment 1 carrier — §결정 6 behavioral→mechanical 전환, ADR-060 framework 2 신규 warning-tier entry)
  - ADR-082 Amendment 1 (CFP-841 — §결정 6 behavioral→mechanical 전환 carrier — corpus-claim-verify scope 2(a) + cross-plugin-ownership-verify scope 2(d))
  - CFP-821 (D2 branch-protection-sync evidence-check bypass channel + hotfix-bypass:branch-protection-sync 36번째 family member, v2.26 MINOR bump — CFP-841 v2.25 선점으로 충돌 해소 rebase)
  - ADR-024 Amendment 8 (CFP-845 — §결정 6.A.3/6.A.4/6.A.5 신설 — per-plugin scope 누적 카운터 + `[bypass-justification]` PR comment marker mechanical enforce + cross-repo extension (wrapper + internal-docs + marketplace 3-repo) — hotfix-bypass:per-plugin-cumulative-counter 37번째 + hotfix-bypass:bypass-justification-marker 38번째 + hotfix-bypass:cross-repo-bypass-counter 39번째 family member + ADR-060 framework 3 신규 warning-tier evidence-checks-registry entry, CFP-825 Amendment 6 §scope_boundary 4 out-of-scope 중 3 영역 흡수 — 4번째 (blocking-on-merge tier 격상) = Story-2 #861 RESERVED 별 carrier evidence-gated 분리)
  - ADR-064 §결정 1 (CFP-845 — CFP scope unitary 정합, Story-1 (본 #845) 3 즉시 통합 + Story-2 (#861 RESERVED) 1 deferred 분리)
  - ADR-067 Amendment 1 (CFP-842 — §결정 4 cross-lane RESET 정책 의 mechanical 정확도 carrier — fix-event-v1 v1.2 → v1.3 MINOR bump + fix-event-depth-scope-presence warning-tier entry + hotfix-bypass:fix-event-depth-scope 40번째 family member, broken-link/path 정정 FIX 시 affected_paths_with_depth presence advisory)
  - ADR-078 (CFP-949 v2.33 — Sub-Epic 6 lane plugin self-owned architecture doc seed completion carrier: 5 신규 label family member append — parent:CFP-949 child Story sub-issue marker + plugin:codeforge-{requirements,design,develop,test} 4 lane plugin namespace, closing-the-loop 7 seed completion wrapper governance update)
  - ADR-72 Amendment 3 (CFP-991 v2.37 — Wave 4 sub-Epic #1 Story-4 canary promotion criteria enforcement layer carrier: 4 신규 label family member append — hotfix-bypass:canary-promotion-criteria 46번째 family member (warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel, ADR-060 evidence-enforceable framework cross-ref) + gate:channel-canary-promotion / gate:channel-beta-promotion / gate:channel-stable-promotion 3 entry (category `gate`, color `0e8a16`, attach_owner_plugin `codeforge-design`, consumer canary→beta promotion gate evaluation marker — Tier-2 admin tier 권장 영역). reconcile-protocol-v1 v1.10 → v1.11 §4.14 canary_compatibility_check_binding sibling carrier. MINOR bump (4 신규 entry append, kind:registry sibling sync 면제 ADR-010 §결정 2, plugin.json bump 0). 5 threat × mitigation matrix carrier (T-3.1 gate:channel-*-promotion label mis-attach mitigation core field — attach_owner_plugin: consumer_repo_only invariant + workflow `if: github.repository != 'mclayer/plugin-codeforge'` mechanical guard))
  - ADR-076 §결정 9.6 (CFP-991 v2.37 — promotion criteria 4-tuple SSOT 4 industry exemplar anchor: Chrome 3-channel Stable/Beta/Canary primary + npm dist-tag + Rust 3-channel + K8s 3-stage 보조 reference. gate:channel-{canary,beta,stable}-promotion 3 entry 의 semantic anchor source)
  - ADR-070 §결정 D6 (CFP-988 Amendment 4 carrier — mandatory-real-execution-evidence STANDING 4-tuple cross-ref §결정 1 expansion: external worker output → DevPL self-claim + IntegrationTestAgent flagged observation 영역 일반화. CFP-991 §4.14 T-4.1 4-tuple measurement spoofing mitigation 영역 cross-ref)
related_files:
  - scripts/bootstrap-labels.sh (type:* 3 entry removed — CFP-140)
  - templates/issue-types.yaml (native Issue Types SSOT — CFP-140)
  - scripts/migrate-label-to-issue-type.sh (migration tool — CFP-140)
  - .github/workflows/phase-label-invariant.yml
  - .github/workflows/phase-gate-mergeable.yml
  - .github/workflows/fix-ledger-sync.yml
  - .github/workflows/subissue-from-impl-manifest.yml
  - .github/workflows/story-init.yml
---

# label-registry v2

## 변경 이력

**v2.35 (CFP-991 / ADR-72 Amendment 3 + ADR-076 §결정 9.6 + reconcile-protocol-v1 v1.11 §4.14, 2026-05-19)**: MINOR bump (4 신규 label entry append — Wave 4 sub-Epic #1 Story-4 canary promotion criteria enforcement layer carrier).

- **추가**: `hotfix-bypass:canary-promotion-criteria` (color `fef2c0`, category `hotfix-bypass`) — `templates/github-workflows/canary-promotion-criteria.yml` (CFP-991 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **43번째 hotfix-bypass:* family member**). ADR-60 evidence-enforceable promotion framework cross-ref — `canary-compatibility-check` evidence-checks-registry entry warning-tier 활성 시 bypass 영역 (reconcile-protocol-v1 §4.14 `promotion_gate_failure_mode.bypass_label` 정합).
- **추가**: `gate:channel-canary-promotion` (color `0e8a16`, category `gate`, attach_owner_plugin `codeforge-design`) — consumer canary tier 활성 PR 안 4-tuple evidence quad 충족 marker (functional + security + monitoring + testing all 'pass' OR 'n_a'). Tier-2 admin tier 권장 영역 (consumer-side 책임 advisory). T-3.1 mitigation core field — `attach_owner_plugin: consumer_repo_only` invariant + workflow `if: github.repository != 'mclayer/plugin-codeforge'` mechanical guard.
- **추가**: `gate:channel-beta-promotion` (color `0e8a16`, category `gate`, attach_owner_plugin `codeforge-design`) — beta tier promotion gate marker (canary → beta transition). 동일 4-tuple gate evaluation 적용.
- **추가**: `gate:channel-stable-promotion` (color `0e8a16`, category `gate`, attach_owner_plugin `codeforge-design`) — stable tier promotion gate marker (beta → stable transition). 동일 4-tuple gate evaluation 적용.
- 3 gate:channel-*-promotion entry 모두 category `gate` (기존 channel category `channel:*` axis 와 disjoint — channel = release lifecycle / gate = promotion transition gate marker, semantic axis 2-way split).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json bump 0).
- ADR-008 §결정 3 SSOT: 신규 label entry append = MINOR bump (v2.34 → v2.35 MINOR increment, 4 family member 동시 추가).
- **MANIFEST.yaml ratchet**: row label-registry-v2 `"2.34"` → `"2.35"` 동반. reconcile-protocol-v1 v1.10 → v1.11 sibling MINOR bump 동반 (§4.14 `canary_compatibility_check_binding.promotion_gate_failure_mode.bypass_label: hotfix-bypass:canary-promotion-criteria` field cross-ref).
- `scripts/bootstrap-labels.sh` 4 신규 entry 동기화 추가 (hardcoded base entry — hotfix-bypass + gate category 양 영역, `parse-hotfix-bypass-labels.py` dynamic read 분기 자동 흡수).
- ratchet 강화 방향 — ADR-058 §결정 5 sunset_justification 영역 외 (`is_transitional: false` invariant, scope 확장 only).
- 8-mirror checklist self-application — ADR-72 (2-digit form) / ADR-076 (3-digit form) 정식 form 정확 사용 invariant. variant form 도입 0건 의무 (CFP-906 + CFP-932 + CFP-954 lineage pattern_count 3 reach, 본 Story-4 = 4 reach 차단 carrier, memory `feedback_codex_tp2_verify_before_trust_pattern`).

**v2.34 (CFP-954 / ADR-72 §결정 1 + §결정 5, 2026-05-18)**: MINOR bump (1 신규 label entry append + 신규 category enum `production-impact` 신설 — Wave 4 sub-Epic #882 Story-3 production cutover layer mandate activation declare scope). CFP-949 v2.33 collision rebase ratchet (parallel session #975 main 점유 → CFP-954 = 다음 MINOR v2.34, dual-carrier 보존).

- **추가**: `production-touching` (color `b60205`, category `production-impact`, severity_binding `severity:high`) — Story touches production cutover surface marker. Issue/PR open 시 사용자 explicit go-ahead 의무 진입 forcing function (ADR-72 §결정 3 trigger axis 정합). Wave 4 sub-Epic #882 Story-3 carrier 영역. 이미 GitHub label list 존재 (registry drift 정정 carrier — DataMigrationArch §G.2 정합, bootstrap-labels.sh count comment 갱신 동반).
- **신규 category enum `production-impact`**: 기존 axis (`channel` — release lifecycle / `phase` / `gate` / `fix` / `hotfix` / `audit` / `hotfix-bypass` / `monitoring` / `conflict` / `fallback` / `fast-pass` / `parent` / `plugin`) 와 별도 axis (production risk axis). canary tier (CFP-906 channel:canary, channel category) ↔ production-touching (production-impact category) 2-axis disjoint (DataMigrationArch §G.3 정합 — channel = release lifecycle / production-impact = production risk). canary tier + production-touching 양 label 동시 부착 가능 (semantic axis 2-way split).
- severity_binding `severity:high` (severity-propagation-v1 v1.0 cross-ref only — kind:registry sibling sync 면제, 본 contract 본문 변경 0). production-touching label 부착 PR/Issue = HIGH severity invariant (review-verdict-v4 findings[].severity binding).
- `scripts/bootstrap-labels.sh` 정식 entry 추가 (base hardcoded entry, hotfix-bypass:* dynamic read 영역 외 — production-touching 은 base label scope) + LABEL_COUNT comment 갱신 동반 (CFP-492 2-way self-check 정합, DataMigrationArch §G.2). CFP-949 v2.33 의 5 신규 entry (parent:CFP-949 + plugin:codeforge-{requirements,design,develop,test}) 와 누적 (dual-carrier — CFP-949 entry 보존 + CFP-954 production-touching append).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json bump 0).
- ADR-008 §결정 3 SSOT: 신규 label entry append + 신규 category 신설 = MINOR bump (v2.33 → v2.34 MINOR increment, CFP-949 v2.33 점유로 collision rebase ratchet).
- **MANIFEST.yaml ratchet**: row label-registry-v2 `"2.33"` (CFP-949 #975 main 반영 baseline) → `"2.34"` (CFP-954 carrier ratchet). 직전 stale drift (`"2.31"` CFP-923 sync miss) 는 CFP-949 v2.33 carrier 가 main 에서 이미 정정 — 본 rebase 는 v2.33 → v2.34 단일 MINOR ratchet. DataMigrationArch §G.1 critical pre-existing drift evidence (`scripts/check-inter-plugin-contracts.sh` INV-1 parity lint warn 차단).
- ratchet 강화 방향 — ADR-058 §결정 5 sunset_justification 영역 외 (`is_transitional: false` invariant, scope 확장 only).
- 8-mirror checklist self-application — ADR-72 / ADR-076 정식 form 정확 사용 invariant. variant form 도입 0건 의무 (memory `feedback_codex_tp2_verify_before_trust_pattern` lineage — CFP-906 + CFP-932 lessons 에서 pattern_count 2 reach, 본 Story-3 = 3 reach 차단 carrier). 변종 literal string 직접 인용은 registry SSOT 영역 (kind:registry actual usage context) 에서 회피 — anti-pattern enumeration 은 bats TC-16 self-documenting test (`tests/scripts/cfp-954/cfp-954-production-cutover.bats` line 509-549) + ADR-065 amendment_log historical context + ADR-080 corpus list (식별자 발생 원천 history) 영역 위임.

**v2.33 (CFP-949 / Sub-Epic 6 lane plugin self-owned architecture doc seed completion, 2026-05-18)**: MINOR bump (5 신규 label entry append — Sub-Epic CFP-949 child Story sub-issue marker + 4 lane plugin namespace marker, parent Epic CFP-756 / ADR-078 closing-the-loop 7 seed completion).

- **추가**: `parent:CFP-949` (color `ededed`, category `parent`) — Sub-Epic CFP-949 child Story sub-issue marker (Wave 1 CFP-968/969/970 + Wave 2 CFP-971/972/973 6 child Story). 기존 `parent:CFP-541` / `parent:CFP-425` / `parent:CFP-525` / `parent:CFP-548` family pattern 답습.
- **추가**: `plugin:codeforge-requirements` (color `ededed`, category `plugin`) — Plugin namespace marker (요구사항 lane). Wave 1 CFP-968 carrier.
- **추가**: `plugin:codeforge-design` (color `ededed`, category `plugin`) — Plugin namespace marker (설계 lane). Wave 1 CFP-969 carrier.
- **추가**: `plugin:codeforge-develop` (color `ededed`, category `plugin`) — Plugin namespace marker (구현 lane). Wave 1 CFP-970 carrier.
- **추가**: `plugin:codeforge-test` (color `ededed`, category `plugin`) — Plugin namespace marker (통합테스트 lane). Wave 2 CFP-972 carrier. (Note: `plugin:codeforge-review` + `plugin:codeforge-pmo` 는 사전 wrapper repo 환경에서 부트스트랩 형태로 이미 존재 — 본 v2.33 = registry SSOT 보강 차원에서 4 신규 lane plugin namespace 형식화 첫 회차.)
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반).
- ADR-008 §결정 3 SSOT: 신규 label entry append = MINOR bump (v2.32 → v2.33 MINOR increment).
- `scripts/bootstrap-labels.sh` 5 신규 entry 동기화 추가 (parent:CFP-949 + plugin:codeforge-{requirements,design,develop,test} 5 row hardcoded).
- ADR-078 (Living architecture doc SSOT) carrier — Sub-Epic CFP-949 6 lane plugin self-owned architecture_doc seed Wave 1+2 completion 후 wrapper governance update (CLAUDE.md cross-ref + doc-locations.yaml examples expand).

**v2.30 (CFP-906 / ADR-076 §결정 9 + ADR-016 Amendment 3 + ADR-063 Amendment 6 §결정 17, 2026-05-17)**: MINOR bump (3 신규 label entry append + 신규 category enum `channel` 신설 — Wave 4 sub-Epic #1 Story-1 multi-version channel pin declare layer, Epic CFP-882).

- **추가**: `channel:stable` (color `0e8a16`, category `channel`) — consumer `.claude/_overlay/project.yaml codeforge.channel.tier: stable` 선언 시 GitHub Issue/PR channel-aware annotation marker. ADR-076 §결정 9.1 3-tier taxonomy 의 default tier (LOW risk class). Wave 4 sub-Epic #1 Story-1 (CFP-906) carrier.
- **추가**: `channel:beta` (color `d4c5f9`, category `channel`) — beta tier marker (MEDIUM risk class, opt-in incremental track).
- **추가**: `channel:canary` (color `f9d0c4`, category `channel`) — canary tier marker (HIGH risk class, production-impact awareness — ADR-076 §결정 9.4 channel selection authority asymmetry + ADR-72 §결정 1 ProductionEvidenceDeputy spawn trigger semantic anchor, Story-3 carrier 영역).
- **신규 category enum**: `channel` — 기존 axis (type/phase/gate/fix/hotfix/audit/hotfix-bypass/monitoring/conflict/fallback/fast-pass) 와 별 axis. CFP-658 v2.13 `fallback:` 신설 / CFP-795 v2.21 `fast-pass` 신설 선례 정합. ADR-008 §결정 1 BREAKING enum 추가 아님 (label name self-distinguishing).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반 — declare layer SSOT only).
- ADR-008 §결정 3 SSOT: 신규 label entry append + 신규 category 신설 = MINOR bump (v2.29 → v2.30 MINOR increment).
- Wave 4 sub-Epic #1 carrier (Epic CFP-882) — 후속 Wave 4 sub-Epic #1 Story-2/3/4/5 sequential 진행 시 channel:* family 의 mechanical lint (channel-drift-detection / channel promotion gate / channel demotion warning) 활성 영역.

**v2.28 (CFP-842 / ADR-067 Amendment 1 §결정 4, 2026-05-17)**: MINOR bump (§3 yaml hotfix-bypass:* 40번째 family member append — fix-event-v1 v1.3 depth-aware scope presence warning-tier lint bypass channel).
- **추가**: `hotfix-bypass:fix-event-depth-scope` (color `fef2c0` audit tier) — `templates/github-workflows/fix-event-depth-scope-presence.yml` (CFP-842 Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **40번째 hotfix-bypass:* family member** — 기존 39 entry 전체 list 는 v2.27 changelog 참조). ADR-067 Amendment 1 §결정 4 carrier — fix-event-v1 v1.3 의 `affected_paths_with_depth` 필드 broken-link/path 정정 FIX 시 presence advisory (false-positive risk 명시, 어휘 grep heuristic, semantic precision 불가 — reviewer responsibility). CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson directly 차단 forcing function.
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 자동 발의 (reuse 패턴, 기존 entry 동일).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반).
- label-registry §4 변경 규칙 SSOT: 신규 label entry append = **minor** (v2.27 → v2.28 MINOR increment, 1 family member 추가).

**v2.27 (CFP-845 / ADR-024 Amendment 8 §결정 6.A.3/6.A.4/6.A.5, 2026-05-17)**: MINOR bump (§3 yaml hotfix-bypass:* 37번째 + 38번째 + 39번째 family member 3 동시 추가 — bypass-as-norm-mutation 후속 escalation 3 sub-decision 통합 Phase 1).
- **추가**: `hotfix-bypass:per-plugin-cumulative-counter` (color `fef2c0` audit tier) — `templates/github-workflows/per-plugin-cumulative-counter.yml` (CFP-845 Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **37번째 hotfix-bypass:* family member** — 기존 36 entry 전체 list 는 v2.26 changelog 참조). ADR-024 Amendment 8 §결정 6.A.3 carrier — per-(plugin) signature 단위 cross-entry aggregate 누적 카운터 lint (threshold ≥5 reach-merged PR, dedup_unit = PR number, window = all-time). self-meta loop 회피 = 본 entry 부착 PR 은 per-plugin 누적 count 제외.
- **추가**: `hotfix-bypass:bypass-justification-marker` (color `fef2c0` audit tier) — `templates/github-workflows/bypass-justification-marker.yml` (CFP-845 Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **38번째 hotfix-bypass:* family member**). ADR-024 Amendment 8 §결정 6.A.4 carrier — `^\[bypass-justification\]` PR comment grep-presence lint (hotfix-bypass:* label 부착 PR scope, semantic adequacy 불가 — false-positive risk 명시, reviewer responsibility). narrative audit 영역 첫 family member. comment-prefix-registry-v1 v1.2 → v1.3 MINOR bump 동반 (14번째 `[bypass-justification]` prefix 신설).
- **추가**: `hotfix-bypass:cross-repo-bypass-counter` (color `fef2c0` audit tier) — `templates/github-workflows/cross-repo-bypass-counter.yml` (CFP-845 Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **39번째 hotfix-bypass:* family member**). ADR-024 Amendment 8 §결정 6.A.5 carrier — 3-repo (wrapper plugin-codeforge + internal-docs + marketplace) cross-repo per-(repo, plugin, label) signature 누적 카운터 lint (threshold ≥3 reach-merged PR, aggregate trigger = 3 repo 동시 reach, single PAT CODEFORGE_CROSS_REPO_PAT reuse — ADR-066 정합). cross-repo 영역 첫 family member.
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 자동 발의 (reuse 패턴, 기존 entry 동일).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반).
- label-registry §4 변경 규칙 SSOT: 신규 label entry append = **minor** (v2.26 → v2.27 MINOR increment, 3 family member 동시 추가).
- CFP-825 Amendment 6 §scope_boundary 4 out-of-scope 중 3 영역 흡수 (per-plugin / `[bypass-justification]` marker / cross-repo) — 4번째 (blocking-on-merge tier 격상) = Story-2 #861 RESERVED 별 carrier evidence-gated 분리 (ADR-064 §결정 1 CFP scope unitary 정합).

**v2.26 (CFP-821 / D2 branch-protection-sync evidence-check, 2026-05-17)**: MINOR bump (§3 yaml hotfix-bypass:* 36번째 family member append — CFP-841 v2.25 선점으로 충돌 해소 rebase, 34→36번째 재번호).
- **추가**: `hotfix-bypass:branch-protection-sync` (color `fef2c0` audit tier) — `templates/github-workflows/branch-protection-drift-check.yml` + `setup-branch-protection.sh` warning-tier drift check conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **36번째 hotfix-bypass:* family member** — 기존 35: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels / auto-phase-label-sibling-parity / claude-md-amendment-ref / actionlint / post-merge-followup-success-rate / wrapper-managed-block / kst-timestamp-display / story-section-ownership / adr-077-ratchet / adr-077-design-reading / bypass-label-counter / exempt:<entry> / version-3way-atomic / corpus-claim-verify / cross-plugin-ownership-verify). CFP-821 D2 `docs/evidence-checks-registry.yaml` `branch-protection-sync` entry 신설 동반 (warning-tier, ADR-060 framework).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 자동 발의 (reuse 패턴, 기존 entry 동일).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반).
- label-registry §4 변경 규칙 SSOT: 신규 label entry append = **minor** (v2.25 → v2.26 MINOR increment).

**v2.25 (CFP-841 / ADR-024 Amendment 7 + ADR-082 Amendment 1, 2026-05-17)**: MINOR bump (§3 yaml hotfix-bypass:* 34번째 + 35번째 family member 2 동시 추가 — `hotfix-bypass:corpus-claim-verify` (ADR-082 §결정 2(a) corpus annotation lint) + `hotfix-bypass:cross-plugin-ownership-verify` (ADR-082 §결정 2(d) cross-plugin ownership queryable lint)).
- **추가**: `hotfix-bypass:corpus-claim-verify` (color `fef2c0` audit tier) — `templates/github-workflows/corpus-claim-verify.yml` (CFP-841 Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **34번째 hotfix-bypass:* family member** — 기존 33: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels / auto-phase-label-sibling-parity / claude-md-amendment-ref / actionlint / post-merge-followup-success-rate / wrapper-managed-block / kst-timestamp-display / story-section-ownership / adr-077-ratchet / adr-077-design-reading / bypass-label-counter / exempt:<entry> / version-3way-atomic). ADR-082 Amendment 1 §결정 2(a) carrier — Story/Change-Plan/ADR corpus enumeration `[verified: git show <ref>:<path>]` annotation lint (ADR-068 I-5 directly-analogous pattern 재사용).
- **추가**: `hotfix-bypass:cross-plugin-ownership-verify` (color `fef2c0` audit tier) — `templates/github-workflows/cross-plugin-ownership-verify.yml` (CFP-841 Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **35번째 hotfix-bypass:* family member**). ADR-082 Amendment 1 §결정 2(d) carrier — `lane-self-write-ownership-matrix.yaml` cross_plugin_doc_ownership sub-tree query 1-step lint + §13.B 4-way drift-sync invariant.
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 자동 발의 (reuse 패턴, 기존 entry 동일).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반).
- label-registry §4 변경 규칙 SSOT: 신규 label entry append = **minor** (v2.24 → v2.25 MINOR increment, 2 family member 동시 추가).

**v2.24 (CFP-820 / ADR-063 Amendment 5 §결정 16, 2026-05-17)**: MINOR bump (§3 yaml hotfix-bypass:* 33번째 family member append).
- **추가**: `hotfix-bypass:version-3way-atomic` (color `fef2c0` audit tier) — `templates/github-workflows/version-3way-atomic.yml` blocking-on-pr 3-way version atomic invariant check conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **33번째 hotfix-bypass:* family member** — 기존 32: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels / auto-phase-label-sibling-parity / claude-md-amendment-ref / actionlint / post-merge-followup-success-rate / wrapper-managed-block / kst-timestamp-display / story-section-ownership / adr-077-ratchet / adr-077-design-reading / bypass-label-counter / exempt:<entry>). ADR-063 Amendment 5 §결정 16 carrier — `hotfix-bypass:version-3way-atomic` label 부착 PR 은 3-way atomic invariant check skip (24시간 이내 sync 의무, ADR-024 Amendment 3 hotfix-bypass family 정합).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 자동 발의 (reuse 패턴, 기존 entry 동일).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반).
- label-registry §4 변경 규칙 SSOT: 신규 label entry append = **minor** (v2.23 → v2.24 MINOR increment).

**v2.23 (CFP-825 / ADR-024 Amendment 6 §결정 6.A.2, 2026-05-17)**: MINOR bump (§3 yaml hotfix-bypass:* 31번째 + 32번째 family member 2 동시 추가 — `hotfix-bypass:bypass-label-counter` (self-meta loop 회피) + `hotfix-bypass:exempt:<entry>` template (rare 정당 declare 채널)).
- **추가**: `hotfix-bypass:bypass-label-counter` (color `fef2c0` audit tier) — `templates/github-workflows/bypass-label-counter.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 6 §결정 6.A.2 ratchet 룰 / ADR-060 framework 63번째 entry). bypass-as-norm mutation 누적 monitoring 첫 family member. 본 entry 부착 PR 은 누적 count 제외 (self-meta loop invariant). **31번째 hotfix-bypass:* family member**.
- **추가**: `hotfix-bypass:exempt:<entry>` template (color `fef2c0` audit tier) — rare 정당 declare 채널, `<entry>` 부분 가 specific entry name (예: `hotfix-bypass:exempt:wording-dictionary`). bypass-label-counter signature 누적 count 제외 영역. narrative audit trail mechanical enforce 는 후속 carrier 영역 (본 carrier = label 등록만). **32번째 hotfix-bypass:* family member template**.
- ADR-008 §결정 3 SSOT: 신규 label entry 2 동시 추가 = MINOR bump.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2, marketplace.json sync 면제 — plugin.json MINOR bump 미동반).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).

**v2.22 (CFP-785 / ADR-077 §결정 3 + §결정 9, 2026-05-17)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 29번째 + 30번째 family member append, v2.21 CFP-795 collision rebase 재인덱스).

`hotfix-bypass:adr-077-ratchet` (29번째) + `hotfix-bypass:adr-077-design-reading` (30번째) 2 family member append. ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

Story-3 Phase 1 carrier — evidence-checks-registry `adr-077-ratchet-declared` / `adr-077-design-reading-mandate-declared` 2 warning-tier row 의 bypass label per-entry namespace. ADR-077 §결정 9 ratchet 선언 + §결정 3 design-reading mandate lint skip (deferred-followup → Phase 2 land 시 Active).

**v2.21 (CFP-795 / ADR-026 Amendment 4 §결정 6, 2026-05-17)**: MINOR bump (신규 label entry + 신규 category `fast-pass` 신설).
- **추가**: `post-merge-fix` (color `0e8a16`, category `fast-pass`) — `phase-gate-mergeable.yml` 4번째 fast-pass source `isPostMergeFix` 의 조건 1 (3-조건 AND 중 label). 단독 부착 ≠ fast-pass (조건 2 hub Story §10 binding + 조건 3 원 PR §7 보안 non-touch 양면 AND 필수). ADR-026 Amendment 4 §결정 6 carrier — cross-repo land_order 후 발견된 safe defect 정정 경로. Orchestrator 수동 부착 의무 (fix-event-v1 §10 row 작성과 동시).
- **신규 category `fast-pass`**: 기존 axis (type/phase/gate/fix/hotfix/audit/hotfix-bypass/monitoring/conflict/fallback) 와 별 axis. sibling-pr 의미 동류, fallback:* v2.13 CFP-658 신설 선례 정합. ADR-008 §결정 1 BREAKING enum 추가 아님 (label name self-distinguishing).
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: 신규 label entry append + 신규 category 신설 = MINOR bump.
- plugin.json MINOR 동반 (5.78.0 → 5.79.0) — marketplace.json sync required (ADR-063 atomic invariant §결정 18).

**v2.20 (CFP-722 / ADR-060 Amendment 13 §결정 27, 2026-05-16)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 28번째 family member append, post-CFP-771 v2.19 rebase).
- **추가**: `hotfix-bypass:story-section-ownership` (color `fef2c0` audit tier) — `templates/github-workflows/story-section-ownership-check.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **28번째 hotfix-bypass:* family member**). ADR-060 Amendment 13 §결정 27 carrier — heading-anchored per-section INV-DI-1 destructive-non-owner + INV-DI-2 monopoly-unauthorized 검출 (PR #441 +216/-850 destructive rewrite incident prevention).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 기존 entry 동일).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.19 (CFP-771 / ADR-079 Amendment 1, 2026-05-16)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 27번째 family member append).
- **추가**: `hotfix-bypass:kst-timestamp-display` (color `fef2c0` audit tier) — `templates/github-workflows/kst-timestamp-display.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **27번째 hotfix-bypass:* family member** — 기존 26: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels / auto-phase-label-sibling-parity / claude-md-amendment-ref / actionlint / post-merge-followup-success-rate / wrapper-managed-block). ADR-079 Amendment 1 carrier — ADR-079 §결정 1 display layer 5 scope KST +09:00 colon-offset form 강제 lint.
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 기존 entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.18 (CFP-702 / ADR-027 Amendment 3 §결정 7.D, 2026-05-15)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 26번째 family member append).
- **추가**: `hotfix-bypass:wrapper-managed-block` (color `fef2c0` audit tier) — `templates/github-workflows/wrapper-managed-block.yml` blocking-on-pr marker block lint skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **26번째 hotfix-bypass:* family member** — 기존 25: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels / auto-phase-label-sibling-parity / claude-md-amendment-ref / actionlint / post-merge-followup-success-rate). ADR-027 Amendment 3 §결정 7.D carrier — D4 customization marker block lint blocking-on-pr (CFP-699 Wave 1 Story-2). D4 marker 위반 = Wave 2 Story-5 reconcile 시 consumer customization wholesale loss 직결 → HIGH risk → blocking-on-pr 직접 시작 (warning 시작점 아님, ADR-027 §결정 7.F 근거).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의. PR description `### Bypass reason` 섹션 기재 필수.
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.17 (CFP-688 / ADR-026 Amendment 3 §결정 5.G.b + §결정 5.G.d, 2026-05-15)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 24번째 + 25번째 family member append, combined single version bump per Change Plan §2.3 coordination directive).
- **추가**: `hotfix-bypass:actionlint` (color `fef2c0` audit tier) — `templates/github-workflows/actionlint-check.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **24번째 hotfix-bypass:* family member** — 기존 23: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels / auto-phase-label-sibling-parity / claude-md-amendment-ref). ADR-026 Amendment 3 §결정 5.G.b carrier — actionlint prevention layer (born-broken 재발 차단 forcing function, CFP-688 P0 incident evidence).
- **추가**: `hotfix-bypass:post-merge-followup-success-rate` (color `fef2c0` audit tier) — `templates/github-workflows/post-merge-followup-success-rate-kpi.yml` KPI sentinel breach Issue auto-create conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **25번째 hotfix-bypass:* family member**). ADR-026 Amendment 3 §결정 5.G.d carrier — rolling 14-day success rate ≥ 90% sentinel, 9번째 warning-tier entry (ADR-026 §5.G.d 명시).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-23rd entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.16 (CFP-685 / ADR-065 §결정 1 row 3, 2026-05-15)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 22번째 family member append).
- **추가**: `hotfix-bypass:auto-phase-label-sibling-parity` (color `fef2c0` audit tier) — `templates/github-workflows/sibling-workflow-parity.yml` (Phase 1 sub-PR (b) carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **22번째 hotfix-bypass:* family member** — 기존 21: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-21st entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- ADR-065 §결정 1 row 3 carrier — templates/github-workflows/*.yml ↔ .github/workflows/*.yml SHA-256 byte-identical parity 검증 (warning tier, weekly cron + workflow_dispatch). CFP-609 retro Finding D (sibling workflow parity enforcement gap) 의 mechanical enforcement.
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.15 (CFP-662 / ADR-060 Amendment 10, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 21번째 family member append).
- **추가**: `hotfix-bypass:bootstrap-labels` (color `fef2c0` audit tier) — `templates/github-workflows/bootstrap-labels.yml` (Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **21번째 hotfix-bypass:* family member** — 기존 20: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-20th entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- ADR-060 Amendment 10 §결정 24 evidence-enforceable warning-tier entry `bootstrap-labels-precondition` carrier 동반 — consumer repo PR open 시 codeforge 필수 label set 부재 자동 감지 + bootstrap-labels.sh idempotent 호출 (RETRO-MCT-104 carrier, mctrader-data MCT-104 Phase 2 PR #14 2026-05-09 replay sentinel). PR-time precondition check pattern 의 첫 baseline (CFP-583 retro 후 framework legitimacy 회복 후 신규 entry 도입).
- `scripts/bootstrap-labels.sh` 무변경 (workflow body 가 본 script 외부 호출, ADR-061 §결정 1 외부 script convention reuse — multi-line shell embed 회피, CFP-583 BODY heredoc anti-pattern 차단). `hotfix-bypass:bootstrap-labels` row 는 CFP-598 dynamic read 분기 (parse-hotfix-bypass-labels.py) 가 자동 흡수 — script 변경 0건.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.14 (CFP-660 / ADR-032 Amendment 2, 2026-05-14)**: MINOR bump (schema 무변경 — §3 yaml hotfix-bypass:* 20번째 family member append).
- **추가**: `hotfix-bypass:workflow-version-drift` (color `fef2c0` audit tier) — `overlay/hooks/check_bootstrap.py` check 10 runtime detection conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **20번째 hotfix-bypass:* family member** — 기존 19: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection).
- ADR-032 Amendment 2 §결정 6 carrier — strict-eligible drift 4 → 5종 확장 (consumer `.github/workflows/<name>.yml` SHA / 핵심 line drift vs wrapper templates). lane orchestration semantics divergence vector 차단 forcing function.
- evidence-checks-registry 45번째 entry `workflow-version-drift` (warning tier, owner_adr ADR-032 / carrier_adr ADR-060, status active).
- plugin.json MINOR bump 동반 (5.57.0 → 5.58.0) — marketplace.json sync required (ADR-063 §결정 1 atomic invariant, 별 sibling PR).

**v2.13 (CFP-658 / ADR-027 Amendment 2, 2026-05-14)**: MINOR bump (신규 `fallback` category enum + 2 entry first-class).
- **추가**: `fallback:manual` (color `c5def5` audit-trailed) — per-Issue ad-hoc override marker. Orchestrator 가 부착 시 `bootstrap.fallback_mode: action_blocked` (declarative trigger A) 와 무관 fallback path 활성. 우선순위 (C) > (A). ADR-027 Amendment 2 §결정 6.A carrier — Action 차단 환경 또는 일반 Action failure 시 manual agent direct write path 진입 의무.
- **추가**: `fallback:rate-limited` (color `c5def5` audit-trailed) — `manual-story-init-fallback.sh` (Phase 2 carrier) 의 exponential backoff (1s/2s/4s) max 3 retry 초과 시 silent skip + 자동 부착 label. OpRiskArch 조건 4 carrier (rate-limit detection + audit-trailed channel).
- **신규 category enum**: `fallback` — 기존 7 category (type / phase / gate / fix / hotfix / audit / hotfix-bypass / monitoring / conflict) 와 별 axis. ADR-008 §결정 1 BREAKING enum 추가 아님 — namespace 정합 (label name `fallback:` prefix 가 self-distinguishing). consumer overlay 영역 외, canonical-only.
- `comment-prefix-registry-v1` `[SECURITY-FALLBACK]` prefix 신설 (SecurityArch 조건 4 carrier) — 본 entry 와 동행, separate PR.
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 1 PR scope — fallback:* 2 entry 직접 hardcoded append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-063 §결정 18 정합: plugin.json MINOR bump 동반 (5.56.0 → 5.57.0) → marketplace.json sync required (별 PR, mclayer/marketplace repo, 선행 merge 의무).

**v2.10 (CFP-631 / ADR-063 Amendment 2, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 17번째 family member append). rebase race 4th sample 반영 (버전 재산정: 5.48.0 → 5.50.0).
- **추가**: `hotfix-bypass:marketplace-description-verbatim` (color `fef2c0` audit tier) — `templates/github-workflows/marketplace-description-verbatim.yml` (Phase 2 carrier) blocking-on-pr lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **17번째 hotfix-bypass:* family member** — CFP-598 backfill 12 entry + CFP-610 wording-dictionary 14th + CFP-619 retro-mandatory-deployed 15th + CFP-628 retro-alert-pickup 16th + 본 entry 17th. ADR-063 Amendment 2 §결정 11 mandate carrier — description PR-time mechanical proactive lint, blocking-on-pr 직접 시작 근거 = ADR-060 §결정 5 default warning explicit exception + §결정 19 Amendment 6 (CFP-509) auto_blocking manual gate path + 사용자 directive Story §1 verbatim).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.9 (CFP-628 / ADR-045 §D-5 + ADR-060 framework, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 16번째 family member append).
- **추가**: `hotfix-bypass:retro-alert-pickup` (color `fef2c0` audit tier) — retro-alert-pickup-rate KPI warning-tier entry 조건부 skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **16번째 hotfix-bypass:* family member** — 기존 15: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed).
- evidence-checks-registry.yaml entry `retro-alert-pickup-rate` (ADR-060 framework 42번째 entry, owner_adr: ADR-045, introduced_by: CFP-628, current_tier: warning) bypass_label 필드 정합.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.8 (CFP-619 / ADR-045 + ADR-060 framework, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 15번째 family member append).
- **추가**: `hotfix-bypass:retro-mandatory-deployed` (color `fef2c0` audit tier) — `templates/github-workflows/retro-mandatory.yml` ↔ `.github/workflows/retro-mandatory.yml` byte-identical mirror deployment lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **15번째 hotfix-bypass:* family member** — CFP-598 backfill 12 entry + CFP-610 wording-dictionary 14th + 본 entry 15th. 기존 14: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary).
- evidence-checks-registry.yaml entry `retro-mandatory-deployed` (ADR-060 framework 41번째 entry, owner_adr: ADR-045, introduced_by: CFP-619, current_tier: warning) 의 `bypass_label` field 와 SSOT 양방향 정합 회복 (pre-existing CFP-619 Phase 1 leak — ArchitectAgent §5.5 self-check item #1 N/A 표기, 실제 FAIL. DesignReview F-3 P1 boundary-completeness finding 가 검출, FIX-1 resolution carrier).
- ADR-065 §결정 1 #1 self-check (label-registry sync) PASS gate 충족 — ArchitectPL verdict packet `mechanical_self_check_passed: true` 재발화 가능.
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-14th entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.7 (CFP-598 / ADR-024 Amendment 3/5 §결정 6.A, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 12 row first-class backfill, 기존 prose-only entry 의 yaml 정규화).
- **추가**: `hotfix-bypass:*` 12종 §3 yaml first-class entry — adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality. pre-existing state: 12개 모두 §변경 이력 prose 에만 기록, §3 yaml row 부재 (bootstrap-labels.sh --dry-run 에서 hotfix-bypass:* 생성 불가 = pre-existing leak). backfill 로 DRY status 해소.
- `scripts/parse-hotfix-bypass-labels.py` 신설 — label-registry-v2.md §3 yaml block 안 `category: hotfix-bypass` row 동적 parse (ADR-061 외부 .py 정합).
- `scripts/bootstrap-labels.sh` hotfix-bypass:* dynamic read 분기 신설 (라인 125 component:* 직전 삽입).
- `scripts/check-bootstrap-labels-count.sh` 3-way parity 확장 (기존 2-way + §3 yaml hotfix-bypass:* row count 추가).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row backfill = PATCH bump.

**v2.6 추가 entry (CFP-610 / ADR-064 Amendment 2, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:wording-dictionary` (color `fef2c0` audit) — `templates/github-workflows/wording-dictionary.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **13번째 hotfix-bypass:* family member** — 기존 12: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-12th entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- ADR-064 Amendment 2 + Amendment 5 (CFP-750) wording-dictionary lint carrier 동반 — 카테고리 (a) forbid 어휘 (`박제` / `못 박기` / `pin` / `freezing` / `별` standalone) grep + 카테고리 (b) 어휘 (normative / sibling sync / kind:contract / ratchet / mirrored field) 평문 정의 동반 의무 advisory (ADR-060 framework warning-tier entry, per-word scope decoupling: `박제`/`못 박기`/`pin`/`freezing` = docs/** + CLAUDE.md + CHANGELOG.md + templates/** / `별` = docs/adr/** + docs/change-plans/** + CLAUDE.md + docs/orchestrator-playbook.md + templates/**).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.6 추가 entry (CFP-582 / ADR-059 Amendment 2 §결정 8 / ADR-024 Amendment 5, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:debate-convergence-quality` (color `fef2c0` audit) — `templates/github-workflows/debate-convergence-quality.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 5 §결정 6.A per-entry namespace 정합, **12번째 hotfix-bypass:* family member** — 기존 11: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-11th entry 동일).
- ADR-059 Amendment 2 §결정 8 convergence_quality_invariant carrier 동반 — Story §9 debate transcript 내 3 marker (`[COUNTERARGUMENT]` / `[ALTERNATIVE_PROPOSED]` / `[DEBATE_PURPOSE_STATEMENT]`) section header 존재 여부 mechanical lint (debate-protocol-v1 v1.2 convergence_quality_invariant block 과 cross-validate, ADR-060 framework 첫 debate 영역 warning-tier entry).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.6 추가 entry (CFP-583 / ADR-060 Amendment 9 §결정 22, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용. v2.5 → v2.6 marker 는 본 sub-entry append carrier 의 chronological provenance, frontmatter version bump 아님).
- **추가**: `hotfix-bypass:workflow-yaml-parse` (color `fef2c0` audit) — `templates/github-workflows/workflow-yaml-parse.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **11번째 hotfix-bypass:* family member** — 기존 10: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-10th entry 동일).
- ADR-060 Amendment 9 §결정 22 evidence-enforceable warning-tier entry `workflow-yaml-parse` carrier 동반 — workflow yml PyYAML safe_load + actionlint dual validation mechanical lint (CFP-578 retro 후속 audit 결과 6 broken workflow file 의 yaml ScannerError sentinel 회복 + framework legitimacy 회복 carrier).
- §결정 23 (BODY heredoc anti-pattern + 정상 패턴 SSOT) 신설 cross-ref — printf format / ANSI-C bash quoting / external script 3 정상 패턴.
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.5 추가 entry (CFP-530 / ADR-060 Amendment 8 §결정 21, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:workflow-permissions` (color `fef2c0` audit) — `templates/github-workflows/workflow-permissions-check.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **10번째 hotfix-bypass:* family member** — 기존 9: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-9th entry 동일).
- ADR-060 Amendment 8 §결정 21 evidence-enforceable warning-tier entry `workflow-permissions-block-presence` carrier 동반 — workflow yml top-level `permissions:` block 부재 mechanical lint (CFP-506 PR #519 CodeQL 권고 + CFP-506 §11.1 entry 5 carrier 의무 + CFP-520 retro carrier reference 종합 해소).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.5 (CFP-429 / ADR-040 Amendment 4 / ADR-060 §결정 6, 2026-05-13)**: MINOR bump.
- **추가**: `from-cfp-425-followup` (color `fbca04` yellow provenance) — Epic CFP-425 (worktree-first mechanical enforcement 영구화) gate FAIL 분기 후속 carrier marker. ADR-060 §결정 6 promotion gate (b) bypass 외 failure > 0 FAIL → 4 entry `current_tier: warning` 유지 + actual `warning → blocking-on-pr` 승격 follow-up Story open carrier 표식.
- ADR-040 Amendment 4 §결정 7.H (CFP-429 Phase 1) self-application closing the loop declaration 의 evidence row.
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — provenance category data row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.4 추가 entry (CFP-521 / ADR-010 Amendment 4 §결정 5 / ADR-060, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.4"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:sibling-pr-author-check` (color `fef2c0` audit) — `templates/github-workflows/sibling-pr-label-author-check.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **9번째 hotfix-bypass:* family member** — 기존 8: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-8th entry 동일).
- ADR-010 Amendment 4 §결정 5 anti-misuse 안전망 mechanical enforcement — EPIC-RESULTS-CFP-462 §6 carrier #2.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.4 (CFP-481 / ADR-060 Amendment 4 / ADR-024 Amendment 4, 2026-05-12)**: MINOR bump.
- **갱신**: phase:* 8 label entry 의 `attach_owner_plugin` field — `auto-phase-label.yml` Action 자동 부착 owner 추가 (PR open 시 1순위 inference fallback chain 으로 부착, ADR-024 Amendment 4 §결정 6.A.1 branch → phase mapping 표 verbatim 사용).
- 기존 lane plugin self-write 영역 invariant 보전 — `auto-phase-label.yml` 가 `if: !contains(...labels.*.name, 'phase:')` 가드로 story-init.yml 가 만든 PR (이미 phase label 부착) skip → 책임 분리.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.4 추가 entry (CFP-506 / ADR-012 Amendment 1 / ADR-060 Amendment 5, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.4"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:claude-md-line-cap` (color `fef2c0` audit) — `templates/github-workflows/claude-md-line-cap.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **8번째 hotfix-bypass:* family member** — 기존 7: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st/2nd/3rd entry 동일).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 1 PR scope, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.3 (CFP-451 / ADR-057 Amendment 2 / ADR-060 / ADR-005, 2026-05-12)**: MINOR bump.
- **추가**: `codeforge-kpi-infra-error` (color `d73a4a` red — severity / oncall) — rate-limit-fallback-kpi.yml workflow infrastructure failure (clone fail / aggregator script error / auto-PR fail). measurement alert (`codeforge-kpi-alert`) 와 분리된 channel — audience-based routing (oncall vs 정책 의사결정자).
- **추가**: `codeforge-kpi-update` (color `0e8a16` green — info / data refresh marker) — rate-limit-fallback-kpi.yml workflow 가 monthly cron 으로 발의하는 data-only refresh PR. **pre-existing leak 정정** (Codex F-451-001 (a)) — CFP-393 workflow line 237 에서 `gh pr create --label codeforge-kpi-update` 사용 중이었으나 registry / bootstrap 부재 (sub-issue carrier 미발의 leak).
- **monitoring tier sub-axis 다축 완결** (v2.2 의 "sub-axis 확장 자연" 선언 첫 다축 사례):
  - `codeforge-kpi-alert` (orange `f29513`) = severity:warn — measurement threshold violation
  - `codeforge-kpi-infra-error` (red `d73a4a`) = severity:error — infrastructure failure
  - `codeforge-kpi-update` (green `0e8a16`) = severity:info — data-only refresh marker
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.2 (CFP-393 / ADR-057 Amendment 2 / ADR-060, 2026-05-11)**: MINOR bump.
- **추가**: `codeforge-kpi-alert` — codeforge KPI threshold violation alert (CFP-393 ADR-057 fallback rate KPI dashboard, rate-limit-fallback-kpi.yml CI Action 자동 부착)
- **신규 tier**: `monitoring` — KPI / metric / dashboard / alert 영역. 기존 `audit` (후처리 분류) 와 분리. 향후 sub-axis (info / warn / error) 확장 자연.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.1 (CFP-344 / ADR-050, 2026-05-09)**: MINOR bump.
- **추가**: `conflict:file-overlap`, `conflict:adr-number`, `conflict:section-locked` — 병렬 에픽 충돌 감지 레이블 (parallel-epic-conflict-check.yml Actions 부착)
- **추가**: `merge-order:1`, `merge-order:2` — 충돌 시 merge 순서 프로토콜 (GitOpsAgent 부착)

**v2.0 (CFP-140 / ADR-049, 2026-05-09)**: MAJOR bump.
- **제거**: `type:epic`, `type:story`, `type:bug` — native GitHub Issue Types 로 대체
  - See: `templates/issue-types.yaml`, `scripts/migrate-label-to-issue-type.sh`
- **유지**: `impl-manifest` (별도 axis — sub-issue visual marker, non-breaking)
- **유지**: phase:* / gate:* / fix:* / hotfix:* / audit:* / category:* (전부 유지)

## 1. 목적

`bootstrap-labels.sh`가 생성하는 GitHub label SSOT (v2.3 시점 35+ 종 — type 1 / phase 8 / gate 4 / fix 4 / hotfix 2 / audit 12+ / category 7 / conflict 5 / monitoring 3).
`type:epic` / `type:story` / `type:bug` 는 native Issue Types 로 대체 (ADR-049).

## 2. Schema

각 label entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| name | string | label 이름 (예: `phase:설계`) |
| category | enum | type / phase / gate / fix / hotfix / audit / hotfix-bypass / monitoring / conflict / fallback / fast-pass / channel (channel = CFP-906 v2.30 신설) |
| color | string | 6자리 hex (gh label spec) |
| description | string | label 설명 |
| single_active | bool | 같은 category에서 1개만 active 가능 (phase만 true) |
| attach_owner_plugin | string | 부착 권한 plugin / Action |

## 3. 항목

```yaml
labels:
  # type:* — v2.0 변경사항
  # type:epic / type:story / type:bug = REMOVED (native Issue Types — ADR-049)
  # impl-manifest = RETAINED (sub-issue axis, non-breaking)

  - name: impl-manifest
    category: type
    color: "fbca04"
    description: "Sub-issue (Impl Manifest 파일 단위)"
    single_active: false
    attach_owner_plugin: "subissue-from-impl-manifest.yml CI Action (자동)"

  # phase:* (8종 — phase:reservation 포함, single-active enforced by phase-label-invariant.yml)
  - name: phase:요구사항
    category: phase
    color: "1d76db"
    description: "Phase: 요구사항"
    single_active: true
    attach_owner_plugin: "codeforge-requirements (CFP-37 후) / DocsAgent (CFP-32 시점) / story-init.yml (초기 부착) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/requirements 1순위 inference)"

  - name: phase:설계
    category: phase
    color: "1d76db"
    description: "Phase: 설계"
    single_active: true
    attach_owner_plugin: "codeforge-design (CFP-40 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/design 1순위 inference)"

  - name: phase:설계-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 설계-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/design-review 1순위 inference + doc-only fast-path 3순위 terminal default)"

  - name: phase:구현
    category: phase
    color: "1d76db"
    description: "Phase: 구현"
    single_active: true
    attach_owner_plugin: "codeforge-develop (CFP-39 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/develop 1순위 inference)"

  - name: phase:구현-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 구현-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/code-review 1순위 inference)"

  - name: phase:구현-테스트
    category: phase
    color: "1d76db"
    description: "Phase: 구현-테스트"
    single_active: true
    attach_owner_plugin: "codeforge-test (CFP-38 후) / DocsAgent (CFP-32 시점)"

  - name: phase:보안-테스트
    category: phase
    color: "1d76db"
    description: "Phase: 보안-테스트"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/security-test 1순위 inference)"

  - name: phase:reservation
    category: phase
    color: "ededed"
    description: "Phase: reservation (CFP-260 / ADR-036 — brainstorming 시점 KEY 사전 확보, 30 일 미진행 시 reservation-cleanup.yml 자동 close. promote 시 phase:요구사항 으로 변경)"
    single_active: true
    attach_owner_plugin: "cfp-reserve.yml Issue Form (자동 첨부) / Orchestrator (수동 promote 시 detach) / auto-phase-label.yml (CFP-481 — Epic Phase N+1 close PR 3순위 terminal default)"

  # gate:* (4종) — gate:live-entry-pass added v1.3 (CFP-123 / ADR-030)
  - name: gate:design-review-pass
    category: gate
    color: "0e8a16"
    description: "Design review PASS"
    single_active: false
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: gate:security-test-pass
    category: gate
    color: "0e8a16"
    description: "Security test PASS"
    single_active: false
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: gate:live-entry-pass
    category: gate
    color: "0e8a16"
    description: "Live Epic lane-entry pass — 3-condition AND (mode==live + --confirm-live + isolated runtime) 충족"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (post-review-verdict step 4) / consumer CI 부착 (3-condition 검증 통과 시)"

  - name: gate:retro-complete
    category: gate
    color: "0e8a16"
    description: "Story 완료 회고 작성됨 (PMOAgent self-write — CFP-138 / ADR-045). 미부착 시 retro-mandatory.yml 가 Story Issue close 차단 (auto-reopen)."
    single_active: false
    attach_owner_plugin: "codeforge-pmo (PMOAgent self-write) — Phase 2 PR merge 후 retro write 완료 시 부착"

  # fix:* (4종, 누적 가능)
  - name: fix:설계-리뷰-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 설계-리뷰"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:구현-리뷰-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 구현-리뷰"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:구현-테스트-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 구현-테스트"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:보안-테스트-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 보안-테스트"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  # hotfix:* (2종)
  - name: hotfix:minimal
    category: hotfix
    color: "ff9999"
    description: "Hotfix minimal"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix 경로)"

  - name: hotfix:critical
    category: hotfix
    color: "ff0000"
    description: "Hotfix critical"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix 경로)"

  - name: audit:post-hotfix
    category: audit
    color: "fef2c0"
    description: "Post-hotfix audit Story"
    single_active: false
    attach_owner_plugin: "Orchestrator (hotfix merge 다음 세션 자동 부착)"

  # audit:debut-* (2종)
  - name: audit:debut-eval
    category: audit
    color: "fbca04"
    description: "데뷔 평가 (consumer 첫 사용 사례) 발견 사항"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-60 ADR-021 detection)"

  - name: audit:from-mctrader-debut
    category: audit
    color: "fef2c0"
    description: "mctrader 데뷔 평가에서 발견된 codeforge gap (첫 사례)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-60 mctrader 데뷔 평가)"

  - name: from-cfp-425-followup
    category: audit
    color: "fbca04"
    description: "Epic CFP-425 (worktree-first mechanical enforcement 영구화) gate FAIL 분기 후속 carrier marker. ADR-060 §결정 6 promotion gate (b) bypass 외 failure > 0 FAIL → 4 entry current_tier: warning 유지 + actual warning → blocking-on-pr 승격 follow-up Story open. 본 label 부착 Story = CFP-429 Amendment 4 declaration 후속 carrier 책임 (4 entry tier 승격 + 4 workflow continue-on-error: false + required_status_checks.contexts 부착 + plugin.json MINOR bump 등 evidence 6 산출물 i~vi 충족)."
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-429 Phase 2 PR description 안 conditional step gate FAIL 분기 자동 trigger) / GitOpsAgent (Issue create 위임)"

  - name: audit:spec-amendment
    category: audit
    color: "fbca04"
    description: "Mid-implementation spec doc 수정 PR (Codex push-back / 사용자 mid-impl clarification / spec drift 발견 시)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (playbook §6.8 spec amendment loop)"

  # early-close:* (3종 권장)
  - name: early-close:duplicate
    category: audit
    color: "d4c5f9"
    description: "다른 Story 와 중복 — early-close 정당화"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-90 phase invariant)"

  - name: early-close:reclassified
    category: audit
    color: "d4c5f9"
    description: "Out-of-scope 재분류 — 다른 Epic / 별도 Story 로 이전"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-90 phase invariant)"

  - name: early-close:epic-rolled-up
    category: audit
    color: "d4c5f9"
    description: "Epic 종료 시 child Story 일괄 close — Epic close PR 가 absorbing"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-90 phase invariant)"

  # category:* (7종) — CFP-60 debut-audit-triage-v1
  - name: category:lane-progression
    category: audit
    color: "0e8a16"
    description: "#1 — 7 lane 통과 / 막힘 (owner: PMOAgent)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (debut-audit-triage)"

  - name: category:agent-gap
    category: audit
    color: "d93f0b"
    description: "#2 — phase 별 gap + 과부하 (owner: ArchitectPL, ADR-021 R1-R4)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (scripts/check-debut-audit-signals.sh detection)"

  - name: category:decision-table
    category: audit
    color: "1d76db"
    description: "#3 — 원인 판정 row 모호 / 신규 (owner: wrapper Orchestrator)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:deputy-mandate
    category: audit
    color: "5319e7"
    description: "#4 — 6 deputy mandate 부족 (owner: ArchitectPL)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:workflow-invariant
    category: audit
    color: "bfd4f2"
    description: "#5 — GitHub Actions 강제 누락 (owner: wrapper Orchestrator)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:template
    category: audit
    color: "c5def5"
    description: "#6 — Story / Change Plan / ADR 필드 부족 (owner: per-template)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:contract-schema
    category: audit
    color: "bfdadc"
    description: "#7 — inter-plugin contract schema 부족 (owner: producer lane plugin)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  # conflict:* (3종 — 병렬 에픽 충돌 감지, ADR-050)
  - name: conflict:file-overlap
    category: conflict
    color: "e4e669"
    description: "다른 open PR과 변경 파일 중복 (parallel-epic-conflict-check.yml 자동 감지)"
    single_active: false
    attach_owner_plugin: "parallel-epic-conflict-check.yml CI Action (자동)"

  - name: conflict:adr-number
    category: conflict
    color: "e4e669"
    description: "ADR-RESERVATION.md 동시 수정 감지 — ADR 번호 충돌 위험"
    single_active: false
    attach_owner_plugin: "parallel-epic-conflict-check.yml CI Action (자동)"

  - name: conflict:section-locked
    category: conflict
    color: "d93f0b"
    description: "section-ownership.yaml locked 섹션 동시 수정 감지 — merge 순서 조율 필요"
    single_active: false
    attach_owner_plugin: "parallel-epic-conflict-check.yml CI Action (자동)"

  # merge-order:* (2종 — 충돌 시 merge 순서 프로토콜, ADR-050)
  - name: merge-order:1
    category: conflict
    color: "0075ca"
    description: "병렬 에픽 충돌 시 먼저 merge해야 하는 PR (낮은 CFP 번호)"
    single_active: false
    attach_owner_plugin: "GitOpsAgent"

  - name: merge-order:2
    category: conflict
    color: "e4e669"
    description: "병렬 에픽 충돌 시 merge-order:1 완료 후 git rebase main 의무"
    single_active: false
    attach_owner_plugin: "GitOpsAgent"

  # monitoring:* (3종 — CFP-451 v2.3 sub-axis 다축 완결 / CFP-393 v2.2 신설 tier)
  # KPI / metric / dashboard / alert 영역. 기존 `audit` (후처리 분류) 와 분리.
  # sub-axis: info (data refresh) / warn (measurement alert) / error (infra failure).
  - name: codeforge-kpi-alert
    category: monitoring
    color: "f29513"
    description: "codeforge KPI threshold violation alert (CFP-393 ADR-057 fallback rate KPI dashboard). rate-limit-fallback-kpi.yml workflow 가 sample_size_sufficient=true AND fallback_rate_percent >= 1.0% 시 Issue auto-open. ADR-060 evidence-enforceable framework 첫 non-sunset application."
    single_active: false
    attach_owner_plugin: "rate-limit-fallback-kpi.yml CI Action (자동)"

  - name: codeforge-kpi-infra-error
    category: monitoring
    color: "d73a4a"
    description: "KPI workflow infrastructure failure — oncall investigation required. rate-limit-fallback-kpi.yml workflow 가 clone fail / aggregator script error / auto-PR fail detect 시 Issue auto-open. measurement alert (`codeforge-kpi-alert`) 와 분리된 channel — audience routing (oncall vs 정책 의사결정자). CFP-451 v2.3 sub-axis 다축 완결."
    single_active: false
    attach_owner_plugin: "rate-limit-fallback-kpi.yml CI Action (자동)"

  - name: codeforge-kpi-update
    category: monitoring
    color: "0e8a16"
    description: "KPI workflow data refresh PR — auto-merge eligible. rate-limit-fallback-kpi.yml workflow 가 monthly cron 으로 발의하는 docs/kpi/rate-limit-fallback.json 데이터 갱신 PR marker. CFP-451 v2.3 sub-axis 다축 완결 (pre-existing CFP-393 leak 정정 — Codex F-451-001 (a))."
    single_active: false
    attach_owner_plugin: "rate-limit-fallback-kpi.yml CI Action (자동)"

  # hotfix-bypass:* (16종 — ADR-024 Amendment 3/5 §결정 6.A per-entry namespace)
  # CFP-598 v2.7 PATCH backfill — §변경 이력 prose-only 상태에서 §3 yaml first-class 정규화.
  # color: fef2c0 (audit tier 동일 — bypass channel 은 audit 계열 색상 공유)
  # single_active: false (누적 가능 — 여러 entry bypass 동시 활성)
  # category: hotfix-bypass (별도 category enum — ADR-024 Amendment 3 §결정 6.A namespace)
  - name: hotfix-bypass:adr-sunset
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: adr-sunset-criteria lint 조건부 skip + audit comment 자동 발의 (CFP-389 / ADR-024 Amendment 3 §결정 6.A / ADR-060 §결정 7 — templates/github-workflows/adr-sunset-criteria.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:decision-principle-vocab
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: decision-principle-vocabulary lint 조건부 skip + audit comment 자동 발의 (CFP-449 / ADR-024 Amendment 3 §결정 6.A / ADR-060 §결정 5 — templates/github-workflows/decision-principle-vocabulary.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:auto-phase-label
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: auto-phase-label 조건부 skip + audit comment 자동 발의 (CFP-481 / ADR-024 Amendment 4 §결정 6.A.1 / ADR-060 Amendment 4 — templates/github-workflows/auto-phase-label.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:marketplace-atomic
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: marketplace ↔ plugin.json atomic invariant check 조건부 skip + audit comment 자동 발의 (CFP-441 / ADR-063 §결정 4 — templates/github-workflows/version-bump-atomic-check.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-session-start-wire
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-session-start-wire blocking-on-pr check 조건부 skip (CFP-427 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-session-start-wire.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-pre-checkout
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-pre-checkout blocking-on-pr check 조건부 skip (CFP-428 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-pre-checkout.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-pre-commit-main-block
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-pre-commit-main-block blocking-on-pr check 조건부 skip (CFP-428 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-pre-commit-main-block.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-spawn-evidence-cwd
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-spawn-evidence-cwd blocking-on-pr check 조건부 skip (CFP-427 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-spawn-evidence-cwd.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:claude-md-line-cap
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: CLAUDE.md ≤320줄 cap lint 조건부 skip + audit comment 자동 발의 (CFP-506 / ADR-012 Amendment 1 / ADR-060 Amendment 5 — templates/github-workflows/claude-md-line-cap.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:sibling-pr-author-check
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: sibling-pr-label-author-check lint 조건부 skip + audit comment 자동 발의 (CFP-521 / ADR-010 Amendment 4 §결정 5 — templates/github-workflows/sibling-pr-label-author-check.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:workflow-permissions
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: workflow permissions block presence lint 조건부 skip + audit comment 자동 발의 (CFP-530 / ADR-060 Amendment 8 §결정 21 — templates/github-workflows/workflow-permissions-check.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:workflow-yaml-parse
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: workflow yaml parse lint 조건부 skip + audit comment 자동 발의 (CFP-583 / ADR-060 Amendment 9 §결정 22 — templates/github-workflows/workflow-yaml-parse.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:debate-convergence-quality
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: debate convergence_quality_invariant 3 marker lint 조건부 skip + audit comment 자동 발의 (CFP-582 / ADR-059 Amendment 2 §결정 8 / ADR-024 Amendment 5 — templates/github-workflows/debate-convergence-quality.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:wording-dictionary
    category: hotfix-bypass
    color: "fef2c0"
    description: "wording-dictionary lint warning 예외 채널 (ADR-064 Amendment 2 / CFP-610). PR description ### Bypass reason 섹션 기재 필수."
    single_active: false
    attach_owner_plugin: "wording-dictionary.yml CI Action (조건부 skip + audit comment 자동)"

  - name: hotfix-bypass:retro-mandatory-deployed
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: retro-mandatory.yml workflow byte-identical mirror deployment lint 조건부 skip + audit comment 자동 발의 (CFP-619 / ADR-045 mandate restoration / ADR-060 framework 41번째 entry / ADR-005 self-application invariant — templates/github-workflows/retro-mandatory.yml ↔ .github/workflows/retro-mandatory.yml diff sentinel)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:retro-alert-pickup
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: retro-alert-pickup-rate KPI sentinel 조건부 skip + audit comment 자동 발의 (CFP-628 Story 2 / ADR-045 §D-5 / ADR-060 framework 42번째 entry — retro alert pickup KPI warning-tier entry 예외 채널). PR description ### Bypass reason 섹션 기재 필수."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:marketplace-description-verbatim
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: marketplace description verbatim PR-time proactive lint 조건부 skip + audit comment 자동 발의 (CFP-631 / ADR-063 Amendment 2 §결정 11 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/marketplace-description-verbatim.yml Phase 2 carrier — blocking-on-pr tier 직접 시작 근거 = ADR-060 §결정 5 default warning explicit exception + §결정 19 Amendment 6 CFP-509 auto_blocking manual gate + 사용자 directive Story §1)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:stop-time-continuous-confirm
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: Continuous '진행해' 패턴 mechanical detect advisory channel skip + audit comment 자동 발의 (CFP-638 / ADR-064 Amendment 3 §결정 9 sister carrier / ADR-060 framework 44번째 entry — Orchestrator self-check behavioral directive advisory only, turn-final hook 부재 platform 한계 + PMOAgent retro file §over-questioning 표 audit signal SSOT). 18번째 hotfix-bypass:* family member (post-CFP-631 atomic realignment)."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:marketplace-drift-detection
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: marketplace ↔ wrapper plugin.json reactive scheduled drift detection workflow skip + audit comment 자동 발의 (CFP-627 / ADR-063 Amendment 3 §결정 13 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/marketplace-drift-detection.yml Phase 2 carrier — warning tier 신규 entry, 4th defense layer reactive scheduled cron channel). 19번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:workflow-version-drift
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: consumer .github/workflows/<name>.yml ↔ wrapper templates/github-workflows/<name>.yml SHA / 핵심 line drift detection skip + audit comment 자동 발의 (CFP-660 / ADR-032 Amendment 2 §결정 6 / ADR-024 Amendment 3 §결정 6.A — overlay/hooks/check_bootstrap.py check 10 runtime detection, warning tier 신규 entry, lane orchestration semantics divergence vector 차단). strict-eligible 5번째 drift (ADR-032 §결정 2 4 → 5 확장). 20번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:bootstrap-labels
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: bootstrap-labels precondition workflow skip + audit comment 자동 발의 (CFP-662 / ADR-060 Amendment 10 §결정 24 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/bootstrap-labels.yml Phase 2 carrier — warning tier 신규 entry, PR-time precondition check pattern 의 첫 baseline, RETRO-MCT-104 carrier). 21번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:auto-phase-label-sibling-parity
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: templates/github-workflows/*.yml ↔ .github/workflows/*.yml SHA-256 byte-identical parity warning-tier lint skip + audit comment 자동 발의 (CFP-685 / ADR-065 §결정 1 row 3 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/sibling-workflow-parity.yml carrier — weekly cron + workflow_dispatch 검증 채널, CFP-609 retro Finding D enforcement). 22번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # CFP-1006 v2.39 naming mismatch resolution — registry §3 entry rename to match gh repo label + workflow filename:
  # PREVIOUS name: hotfix-bypass:claude-md-amendment-ref (CFP-708 originally / never registered in gh repo)
  # NEW name: hotfix-bypass:claude-md-amendment-ref-drift (matches gh repo label + workflow file claude-md-amendment-ref-drift.yml + 12+ PR audit history)
  # Conservative direction: align registry → gh + workflow (registry was never active in gh, gh side widely used → preserve audit history).
  # Convention compatibility: append-only v2.x append (no v3.0 BREAKING required — §4 변경 규칙 정합, since the original "claude-md-amendment-ref" name was never instantiated in gh; this is registry-side rename only, gh-side 0 effect).
  - name: hotfix-bypass:claude-md-amendment-ref-drift
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: CLAUDE.md Amendment ref drift detection lint skip + audit comment 자동 발의 (CFP-708 / ADR-074 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/claude-md-amendment-ref-drift.yml carrier — CLAUDE.md 안 Amendment N (CFP-NNN) 참조 + ADR frontmatter amendment_log/amendments 길이 비교, warning tier 신규 entry, cross-section coherence lint CFP-263 lineage 답습). 23번째 hotfix-bypass:* family member (historical attribution preserved — rename does not change family ordinal position). CFP-1006 v2.39 naming mismatch resolution: registry §3 entry name aligned to gh repo label + workflow filename (-drift suffix retained, conservative direction)."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:actionlint + hotfix-bypass:post-merge-followup-success-rate (2종 — CFP-688 / ADR-026 Amendment 3 §결정 5.G.b + §결정 5.G.d carrier)
  # actionlint prevention layer + KPI detection layer. canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
  # plugin.json PATCH bump 동반 (5.72.0 → 5.73.0) — marketplace.json sync required (ADR-063 §결정 18).
  - name: hotfix-bypass:actionlint
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: actionlint workflow syntax validation lint skip + audit comment 자동 발의 (CFP-688 / ADR-026 Amendment 3 §결정 5.G.b / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/actionlint-check.yml carrier — .github/workflows/*.yml YAML parse + syntax validation, actionlint v1.7.12, warning tier 신규 entry, born-broken 재발 차단 forcing function). ADR-026 §5.G.b 승격 target = blocking-on-pr (tier reconciliation: 첫 도입 warning, ADR-060 §결정 5). 24번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:post-merge-followup-success-rate
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: post-merge-followup.yml rolling 14-day success rate KPI sentinel breach Issue auto-create skip + audit comment 자동 발의 (CFP-688 / ADR-026 Amendment 3 §결정 5.G.d / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/post-merge-followup-success-rate-kpi.yml carrier — weekly cron + workflow_dispatch 측정, sentinel ≥ 90%, 9번째 warning-tier entry ADR-026 §5.G.d 명시). 25번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # fallback:* (2종 — CFP-658 / ADR-027 Amendment 2 §결정 6.A carrier — Action 차단 환경 manual agent direct write path)
  # 신규 category enum: fallback (별 axis). canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
  # plugin.json MINOR bump 동반 (5.56.0 → 5.57.0) — marketplace.json sync required (ADR-063 §결정 18).
  - name: fallback:manual
    category: fallback
    color: "c5def5"
    description: "fallback: per-Issue ad-hoc override marker (CFP-658 / ADR-027 Amendment 2 §결정 6.A). Orchestrator 가 부착 시 bootstrap.fallback_mode: action_blocked (declarative Trigger A) 와 무관 manual agent direct write path 활성. 우선순위 (C) > (A) — Issue 발의자 또는 Orchestrator 의 일시 outage / 사용자 explicit 선택 영역. RequirementsPL / ArchitectPL 의 manual `bash templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>` 호출 의무 (Phase 2 carrier 신설 후 활성). 4 required check + enforce_admins:true ratchet 유지."
    single_active: false
    attach_owner_plugin: "Orchestrator / 사용자 직접 (Issue 발의 시 또는 fallback path 진입 시점)"

  - name: fallback:rate-limited
    category: fallback
    color: "c5def5"
    description: "fallback: rate-limited skip audit marker (CFP-658 / ADR-027 Amendment 2 §결정 6.G). manual-story-init-fallback.sh (Phase 2 carrier) 의 exponential backoff (1s/2s/4s) max 3 retry 초과 시 silent skip + 자동 부착. OpRiskArch 조건 4 carrier — GitHub secondary content-creation rate-limit (503/429) 영역 audit-trailed channel."
    single_active: false
    attach_owner_plugin: "manual-story-init-fallback.sh (자동) / Orchestrator (수동 audit 시)"

  # hotfix-bypass:wrapper-managed-block (CFP-702 / ADR-027 Amendment 3 §결정 7.D carrier — D4 customization marker lint blocking-on-pr)
  # 26번째 hotfix-bypass:* family member (v2.18 PATCH).
  - name: hotfix-bypass:wrapper-managed-block
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: wrapper-managed marker block lint skip + audit comment 자동 발의 (CFP-702 / ADR-027 Amendment 3 §결정 7.D / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/wrapper-managed-block.yml blocking-on-pr carrier — # BEGIN / # END wrapper-managed pair + 순서 + flat-only nesting 검증, D4 marker 위반 = customization wholesale loss 직결 HIGH risk). 26번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:kst-timestamp-display (CFP-771 / ADR-079 Amendment 1 carrier — KST timestamp display mechanical lint warning-tier)
  # 27번째 hotfix-bypass:* family member (v2.19 PATCH).
  - name: hotfix-bypass:kst-timestamp-display
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: KST timestamp display mechanical lint skip + audit comment 자동 발의 (CFP-771 / ADR-079 Amendment 1 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/kst-timestamp-display.yml warning-tier carrier — display layer 5 scope (CLAUDE.md / orchestrator-playbook / ADR / retros) 의 ISO 8601 dateTime +09:00 colon-offset form 강제 lint, RFC 3339 §5.6 KST_TS_RE regex). 27번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:story-section-ownership (CFP-722 / ADR-060 Amendment 13 §결정 27 carrier — per-section ownership mechanical lint warning-tier)
  # 28번째 hotfix-bypass:* family member (v2.19 sub-entry append — MINOR bump 불요, same-MINOR additive sub-entry ADR-008 §결정 SemVer rule).
  - name: hotfix-bypass:story-section-ownership
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: Story per-section ownership lint skip + audit comment 자동 발의 (CFP-722 / ADR-060 Amendment 13 §결정 27 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/story-section-ownership-check.yml warning-tier carrier — heading-anchored content slice per-section INV-DI-1 destructive-non-owner + INV-DI-2 monopoly-unauthorized 검출. PR #441 +216/-850 destructive rewrite incident prevention. §14 ADR-031 + §10 CFP-32 monopoly 보호). 28번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # post-merge-fix (CFP-795 / ADR-026 Amendment 4 §결정 6 carrier — cross-repo land_order post-merge hotfix 3-조건 AND fast-pass gate 조건 1)
  # 신규 category enum: fast-pass (별 axis — sibling-pr 의미 동류, fallback:* v2.13 CFP-658 신설 선례 정합).
  # plugin.json MINOR bump 동반 (5.78.0 → 5.79.0) — marketplace.json sync required (ADR-063 atomic invariant).
  - name: post-merge-fix
    category: fast-pass
    color: "0e8a16"
    description: "cross-repo Story land_order 후 발견된 safe defect 의 post-merge hotfix PR — phase-gate-mergeable.yml 4번째 fast-pass source (3-조건 AND 중 조건 1). 단독 부착 ≠ fast-pass (조건 2 hub Story §10 FIX Ledger row binding + 조건 3 원 MERGED PR §7 보안 non-touch 양면 AND 필수). ADR-026 Amendment 4 §결정 6 carrier. 사용법: Orchestrator 가 post-merge hotfix PR open 시 수동 부착 — fix-event-v1 §10 row 작성 (Orchestrator monopoly, CFP-32) + corrects_pr: marker PR body 기재 + story_uri: marker 병기 의무."
    single_active: false
    attach_owner_plugin: "Orchestrator (post-merge hotfix PR open 시 수동 부착 — fix-event-v1 §10 row 작성과 동시)"

  # hotfix-bypass:adr-077-ratchet (CFP-785 / ADR-077 §결정 9 ratchet 선언 mechanical lint warning-tier)
  # 29번째 hotfix-bypass:* family member (v2.22 PATCH bump, v2.21 CFP-795 collision rebase 재인덱스).
  - name: hotfix-bypass:adr-077-ratchet
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: ADR-077 §결정 9 ratchet lint (`adr-077-ratchet-declared`) skip — Story-3 carrier (CFP-785), Phase 2 wire 후 enforce. lint script: scripts/check-adr-077-ratchet.sh. Phase 1 status: deferred-followup → Phase 2 land 시 Active. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:adr-077-design-reading (CFP-785 / ADR-077 §결정 3 design-reading mandate lint warning-tier)
  # 30번째 hotfix-bypass:* family member (v2.22 PATCH bump, v2.21 CFP-795 collision rebase 재인덱스).
  - name: hotfix-bypass:adr-077-design-reading
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: ADR-077 §결정 3 design-reading mandate lint (`adr-077-design-reading-mandate-declared`) skip — Story-3 carrier (CFP-785), Phase 2 wire 후 enforce. lint script: scripts/check-adr-077-design-reading-mandate.sh. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:bypass-label-counter (CFP-825 / ADR-024 Amendment 6 §결정 6.A.2 carrier — per-entry namespace 누적 사용 카운터 lint, self-meta loop 회피 invariant)
  # 31번째 hotfix-bypass:* family member (v2.23 MINOR bump — 2 신규 family member 동시 추가, 본 entry + exempt:<entry> template).
  - name: hotfix-bypass:bypass-label-counter
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: bypass-label-counter per-entry namespace 누적 사용 카운터 lint 조건부 skip + audit comment 자동 발의 (CFP-825 / ADR-024 Amendment 6 §결정 6.A.2 / ADR-060 framework 63번째 entry — templates/github-workflows/bypass-label-counter.yml Phase 2 carrier — 24h cron + workflow_dispatch + Issue auto-create, per-(plugin, label) signature ≥3 reach-merged PR 누적 시 carrier Issue 자동 발의, window=all-time / dedup_unit=PR number / self-meta loop 회피 절대 invariant). bypass-as-norm mutation 누적 monitoring 첫 family member. CFP-771 retro §8 제안 1 carrier. 31번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:exempt:<entry> (CFP-825 / ADR-024 Amendment 6 §결정 6.A.2 carrier — template entry, rare 정당 declare 채널)
  # 32번째 hotfix-bypass:* family member (template — <entry> 부분 가 specific entry name).
  - name: "hotfix-bypass:exempt:<entry>"
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass:exempt:<entry> template — rare 정당 declare 채널 (CFP-825 / ADR-024 Amendment 6 §결정 6.A.2 carrier — bypass-label-counter signature 누적 count 제외 영역, 정당 사용으로 평가된 PR 에 부착 시 해당 PR signature 누적 count 제외). <entry> 부분 가 specific entry name (예: hotfix-bypass:exempt:wording-dictionary). narrative audit trail mechanical enforce 는 후속 carrier 영역 (본 carrier = label 등록만). 32번째 hotfix-bypass:* family member template."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로) — <entry> 부분 specific entry name 명시 의무"

  # hotfix-bypass:version-3way-atomic (CFP-820 / ADR-063 Amendment 5 §결정 16 carrier — 3-way version atomic invariant blocking-on-pr bypass channel)
  # 33번째 hotfix-bypass:* family member (v2.24 MINOR bump).
  - name: hotfix-bypass:version-3way-atomic
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: version-3way-atomic blocking-on-pr 3-way version atomic invariant check 조건부 skip + audit comment 자동 발의 (CFP-820 / ADR-063 Amendment 5 §결정 16 — templates/github-workflows/version-3way-atomic.yml, publisher plugin.json ↔ registry marketplace.json ↔ consumer project.yaml 3-way byte-identical version check skip. 24시간 이내 3-way sync 의무. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 33번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:corpus-claim-verify (CFP-841 / ADR-082 Amendment 1 §결정 2(a) carrier — corpus annotation lint warning-tier, ADR-068 I-5 directly-analogous pattern 재사용)
  # 34번째 hotfix-bypass:* family member (v2.25 MINOR bump — 2 신규 family member 동시 추가).
  - name: hotfix-bypass:corpus-claim-verify
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: corpus-claim-verify warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-841 / ADR-082 Amendment 1 §결정 2(a) / ADR-024 Amendment 7 — templates/github-workflows/corpus-claim-verify.yml Phase 2 carrier — Story/Change-Plan/ADR 본문 corpus/fixture enumeration ('예시 N건 / 전무 / 부재 / 다수' + file-path 인용 co-occurrence) 의 [verified: git show <ref>:<path>] annotation 부재 검출. 4-guard FP 완화 (file-path co-occurrence / citation≠assertion 면제 / forward-only / self-referential exemption — ADR-068 I-5 + ADR-082 §결정 4/6 EC-3 prior art 재사용). ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). write-time semantic truth verify 영역 첫 family member. 34번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:cross-plugin-ownership-verify (CFP-841 / ADR-082 Amendment 1 §결정 2(d) carrier — cross-plugin ownership queryable lint warning-tier + §13.B 4-way drift-sync invariant)
  # 35번째 hotfix-bypass:* family member (v2.25 MINOR bump — 2 신규 family member 동시 추가).
  - name: hotfix-bypass:cross-plugin-ownership-verify
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: cross-plugin-ownership-verify warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-841 / ADR-082 Amendment 1 §결정 2(d) / ADR-024 Amendment 7 — templates/github-workflows/cross-plugin-ownership-verify.yml Phase 2 carrier — ChangeImpactAgent Phase 0 mapping templates/* wrapper-local 단정 전 lane-self-write-ownership-matrix.yaml cross_plugin_doc_ownership sub-tree query 1-step annotation 미보유 검출 [verified: git show origin/main:templates/github-workflows/cross-plugin-ownership-verify.yml] + §13.B 4-way drift-sync invariant (yaml ↔ SKILL.md ↔ story-page-structure.md ↔ lint regex, yaml-as-canonical single-direction). CFP-722 §13.A machine_readable_ssot 실재 기반 cross-plugin 영역 확장 (신규 registry 창설 아님). ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 35번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:branch-protection-sync (CFP-821 D2 — branch protection manifest drift check bypass channel)
  # 36번째 hotfix-bypass:* family member (v2.26 MINOR bump — CFP-841 v2.25 선점으로 충돌 해소 rebase, 34→36번째 재번호).
  - name: hotfix-bypass:branch-protection-sync
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: branch-protection-sync warning-tier drift check 조건부 skip + audit comment 자동 발의 (CFP-821 D2 — templates/github-workflows/branch-protection-drift-check.yml + templates/scripts/setup-branch-protection.sh, templates/branch-protection-manifest.yaml SSOT ↔ 실 GitHub API state drift 경고 skip. ADR-024 Amendment 2 §결정 A core 4 contexts 삭제 불허 invariant 보존 의무. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 36번째 hotfix-bypass:* family member (CFP-841 v2.25 선점으로 충돌 해소 rebase — 34→36번째 재번호)."

  # hotfix-bypass:per-plugin-cumulative-counter (CFP-845 — ADR-024 Amendment 8 §결정 6.A.3 bypass-as-norm-mutation per-plugin scope 누적 카운터 lint bypass channel)
  # 37번째 hotfix-bypass:* family member (v2.27 MINOR bump — bypass-as-norm-mutation 후속 escalation 3 sub-decision 통합 Phase 1).
  - name: hotfix-bypass:per-plugin-cumulative-counter
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: per-plugin-cumulative-counter warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-845 Phase 2 carrier — templates/github-workflows/per-plugin-cumulative-counter.yml + scripts/check-per-plugin-cumulative-counter.{py,sh}, ADR-024 Amendment 8 §결정 6.A.3 — per-(plugin) signature 단위 cross-entry aggregate 누적 카운터 lint skip. self-meta loop 회피: 본 entry 부착 PR 은 per-plugin 누적 count 제외. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 37번째 hotfix-bypass:* family member. threshold ≥5 reach-merged PR (single plugin cross-entry aggregate), dedup_unit = PR number, window = all-time."

  # hotfix-bypass:bypass-justification-marker (CFP-845 — ADR-024 Amendment 8 §결정 6.A.4 `[bypass-justification]` PR comment marker presence lint bypass channel)
  # 38번째 hotfix-bypass:* family member — narrative audit 영역 첫 family member.
  - name: hotfix-bypass:bypass-justification-marker
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: bypass-justification-marker warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-845 Phase 2 carrier — templates/github-workflows/bypass-justification-marker.yml + scripts/check-bypass-justification-marker.{py,sh}, ADR-024 Amendment 8 §결정 6.A.4 — hotfix-bypass:* label 부착 PR 의 `^\\[bypass-justification\\]` top-level PR comment grep-presence lint skip. semantic adequacy 불가 (grep-only) — false-positive risk 명시, reviewer responsibility. comment-prefix-registry-v1 v1.3 14번째 `[bypass-justification]` prefix 정합. self-meta loop 회피: 본 entry 부착 PR 은 marker presence check skip. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 38번째 hotfix-bypass:* family member. narrative audit 영역 첫 family member."

  # hotfix-bypass:cross-repo-bypass-counter (CFP-845 — ADR-024 Amendment 8 §결정 6.A.5 cross-repo 3-repo signature 누적 카운터 lint bypass channel)
  # 39번째 hotfix-bypass:* family member — cross-repo 영역 첫 family member.
  - name: hotfix-bypass:cross-repo-bypass-counter
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: cross-repo-bypass-counter warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-845 Phase 2 carrier — templates/github-workflows/cross-repo-bypass-counter.yml + scripts/check-cross-repo-bypass-counter.{py,sh}, ADR-024 Amendment 8 §결정 6.A.5 — 3-repo (mclayer/plugin-codeforge + mclayer/codeforge-internal-docs + mclayer/marketplace) cross-repo per-(repo, plugin, label) signature 누적 카운터 lint skip. threshold ≥3 reach-merged PR per signature, aggregate trigger = 3 repo 동시 reach 시 단일 aggregate carrier Issue 발의 (mclayer/plugin-codeforge wrapper governance owner SSOT, ADR-013 정합). dedup_unit = (repo, PR number) 2-tuple. single PAT CODEFORGE_CROSS_REPO_PAT reuse — ADR-066 rotation policy 정합 (`issues:read` + `repo:read` 3-repo 동시 권한). self-meta loop 회피: 본 entry 부착 PR 은 cross-repo 누적 count 제외. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 39번째 hotfix-bypass:* family member. cross-repo 영역 첫 family member."

  # hotfix-bypass:fix-event-depth-scope (CFP-842 — ADR-067 Amendment 1 §결정 4 fix-event-v1 v1.3 depth-aware scope presence lint bypass channel)
  # 40번째 hotfix-bypass:* family member — broken-link/path FIX over-correction regression chain 차단 forcing function.
  - name: hotfix-bypass:fix-event-depth-scope
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: fix-event-depth-scope-presence warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-842 Phase 2 carrier — templates/github-workflows/fix-event-depth-scope-presence.yml + scripts/check-fix-event-depth-scope-presence.sh, ADR-067 Amendment 1 §결정 4 — fix-event-v1 v1.3 의 affected_paths_with_depth 필드 broken-link/path 정정 FIX 시 presence advisory skip. 어휘 grep heuristic (broken-link / path 정정 / relative path / doc-location-registry move / link target / href / cross-module path / over-correction) — semantic precision 불가, reviewer responsibility. CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson directly 차단 forcing function. self-meta loop 회피: 본 entry 부착 PR 은 depth-scope presence check skip. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 40번째 hotfix-bypass:* family member."

  # hotfix-bypass:inter-plugin-contracts-parity (CFP-894 — ADR-010 INV-1 MANIFEST↔frontmatter parity lint bypass channel)
  # 41번째 hotfix-bypass:* family member — CFP-834 silent drift 류 재발 차단 forcing function.
  - name: hotfix-bypass:inter-plugin-contracts-parity
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: inter-plugin-contracts-parity warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-894 / ADR-010 — templates/github-workflows/inter-plugin-contracts-parity.yml + scripts/check-inter-plugin-contracts-parity.{sh,py}, INV-1 wrapper-local MANIFEST.yaml contract_version row ↔ wrapper sibling .md frontmatter contract_version 2-touchpoint byte-identical parity skip. CFP-834 silent drift (wrapper sibling 1.1↔body 1.0) 류 재발 차단. Phase 2 carrier (별 CFP): body `## N.` payload + cross-repo canonical frontmatter parity (CODEFORGE_CROSS_REPO_PAT 의존, ADR-066). Archived 면제 (historical record). Missing file = separation of concerns (CFP-42 check_inter_plugin_contracts.py 영역, parity 영역 외 silent skip). ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 41번째 hotfix-bypass:* family member."

  # hotfix-bypass:channel-drift-detection (CFP-932 — Wave 4 sub-Epic #1 Story-2 channel-drift-detection warning-tier bypass channel)
  # 42번째 hotfix-bypass:* family member — ADR-063 Amendment 3 §결정 13 marketplace-drift-detection precedent 답습 (3-tuple channel drift 4th defense layer).
  - name: hotfix-bypass:channel-drift-detection
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: channel-drift-detection warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-932 / ADR-063 Amendment 3 §결정 13 + reconcile-protocol-v1 §4.10 — templates/github-workflows/channel-drift-detection.yml + scripts/check-channel-drift.sh, 3-tuple channel drift (consumer codeforge.channel.tier ↔ install plugin.json .version ↔ registry marketplace.json channels[*].versions[] membership) 24h cron + workflow_dispatch reactive scheduled detection. marketplace-drift-detection.yml byte-pattern 답습 — signature dedup + E-4 3-branch (401 fail-closed / 429 fail-open / 5xx 3-retry) + warning-first (drift 감지해도 exit 0, Issue auto-create 통보 channel). (c) registry leg 미populate (Story-4 전) = warning-first graceful (blocking 0, transitional valid). evidence-checks-registry.yaml channel-drift-detection entry warning-tier 동반 (ADR-060 framework). Wave 4 sub-Epic #1 Story-2 carrier, Epic CFP-882. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). 42번째 hotfix-bypass:* family member."

  # hotfix-bypass:architecture-drift (CFP-923 — Epic B Story-4 ADR-078 P-S4 architecture-drift warning-tier bypass channel)
  # 43번째 hotfix-bypass:* family member — ADR-078 §결정 1 4 H2 closed-enum + 3 detection class lint (CFP-771 kst-timestamp-display precedent 동형).
  - name: hotfix-bypass:architecture-drift
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: architecture-drift warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-923 / ADR-078 §결정 4 P-S4 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/architecture-drift.yml + scripts/check-architecture-drift.sh, docs/architecture/**/*.md scope 의 4 H2 closed-enum (모듈/경계/인터페이스 계약/데이터 흐름) + 3 detection class (a 모듈 enumeration parity / b inter-plugin-contracts enumeration parity / d anti-scope guard violation — class/def/import/signature line + H2 closed-enum 외 H2) 정합 lint. 4-guard FP 완화 (CFP-841 corpus-claim-verify §결정 4/6 EC-3 prior art 재사용 — scope guard / citation≠assertion 면제 / forward-only / self-referential exemption). Epic B Story-4 single-Phase land — CFP-771 kst-timestamp-display 동형. evidence-checks-registry.yaml architecture-drift entry warning-tier 동반 (ADR-060 framework). 43번째 hotfix-bypass:* family member."

  # hotfix-bypass:codex-sandbox-substitution (CFP-963 — ADR-024 Amendment 9 + ADR-060 Amendment 14 §결정 28 + ADR-081 Amendment 4 §결정 D1.D body 확장 carrier)
  # 44번째 hotfix-bypass:* family member — historical-with-template-count convention citation (Codex TP#2 F-CX-963-A P2 calibration verdict 정합):
  # active concrete `^  - name: hotfix-bypass:` direct grep count = 42 + CFP-825 Amendment 6 §결정 6.A.2 `hotfix-bypass:exempt:<entry>` 32번째 template (rare 정당 declare 채널, template not concretely instantiated — historical Nth count 1 포함) +
  # 직전 family member 43번째 `hotfix-bypass:architecture-drift` (CFP-923 self-describe L1011 정합) → 신규 = 44번째 historical Nth count convention.
  # Amendment 6 §결정 6.A.2 prior art = first precedent of historical-with-template-count convention.
  - name: hotfix-bypass:codex-sandbox-substitution
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: codex-network-scope-presence warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-963 / ADR-081 Amendment 4 §결정 D1.D body 확장 (boolean `sandbox_network_required: <bool>` → 4-tier `network_scope: <enum>` strict ratchet-up: `offline` / `repo-fetch-only` / `web-fetch` / `offline_substitution_declared`) + ADR-060 Amendment 14 §결정 28 (12번째 warning-tier evidence-checks-registry entry `codex-network-scope-presence`) + ADR-024 Amendment 9 §결정 6.A — templates/github-workflows/codex-network-scope-presence.yml + scripts/check-codex-network-scope.{sh,py}, Codex worker spawn-prompt 본문 안 `network_scope` field presence-grep heuristic (4-tier enum value membership check OR boolean legacy `sandbox_network_required: <bool>` advisory grace) + Story §10 `[codex-substitution-scope-declared: *]` / `[codex-sandbox-fallback: *]` marker 의 enum 정합 + §14 Lane Evidence row 안 `network_scope_actual` 13번째 optional field (evidence-check-registry-v1 v1.3 신규 schema field, ADR-031 §14 12 field 영향 0 backward-compat) 4-tier enum membership check. semantic adequacy 검증 불가 — false-positive risk 명시 (어휘 grep heuristic, reviewer responsibility). self-meta loop 회피: 본 lint workflow / script 자체의 PR 부착 시 본 lint step skip + carrier_story self-exempt (CFP-963 Phase 1+2 PR bootstrap-exempt, ADR-062 §결정 8 precedent 정합). dual-binding pattern 첫 사례 — ADR-081 Amendment 4 (declaration source) + ADR-060 Amendment 14 (enforcement source) 양 ADR frontmatter `mechanical_enforcement_actions[]` 안 동일 `action: codex-network-scope-presence` entry 보유. CFP-722 story-section-ownership / CFP-841 corpus-claim-verify / CFP-966 parallel-work-sentinel-pickup precedent 동형 (declaration-only normative + presence-grep warning lint 보완 관계). evidence-checks-registry.yaml codex-network-scope-presence entry warning-tier 동반 (ADR-060 framework, deferred-followup status — Phase 2 actual lint + workflow + bats fixture pair CX-963-3 P2 boundary mandate wire 후 Active 전환). ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합. 44번째 hotfix-bypass:* family member (historical-with-template-count convention: 42 active concrete + CFP-825 32번째 template = 43 historical + 1 = 44 new). CFP-946 8-occurrence sentinel closing-the-loop carrier (Story-B carry-forward — option 1 codex CLI flag wire + option 2 graceful degradation + option 3 substitution-side mechanism = 양 면 chain 완결)."

  # hotfix-bypass:parallel-work-sentinel-pickup (CFP-967 — ADR-073 Amendment 2 §결정 1 mechanical enforcement parallel work sentinel warning-tier bypass channel)
  # 45번째 hotfix-bypass:* family member — ADR-073 Amendment 2 declarative anchor CFP-966 의 mechanical wire carrier (CFP-967 Phase 2). collision rebase ratchet: CFP-963 v2.35 44번째 병렬 merge 선점 → CFP-967 = 45번째 v2.36 (dual-carrier 보존).
  - name: hotfix-bypass:parallel-work-sentinel-pickup
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: parallel-work-sentinel-pickup warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-967 / ADR-073 Amendment 2 §결정 1-A/1-B/1-C — scripts/check-parallel-work-sentinel.sh + templates/github-workflows/parallel-work-sentinel-check.yml, memory rule 6 title-based search + rule 7 Epic state poll + HEAD compare 3 polling mode. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합. 45번째 hotfix-bypass:* family member (collision rebase ratchet: CFP-963 v2.35 44번째 병렬 merge 선점 → CFP-967 = 45번째 v2.36)). sentinel evidence: CFP-953 + CFP-946 same-day 2-occurrence 2026-05-18 KST."

  # channel:* (3종 — CFP-906 / ADR-076 §결정 9 + ADR-016 Amendment 3 + ADR-063 Amendment 6 §결정 17 carrier — Wave 4 sub-Epic #1 Story-1 multi-version channel pin declare layer, Epic CFP-882)
  # 신규 category enum: channel (별도 axis — release tier selector, version specifier 와 disjoint).
  # 3-tier closed-enum (stable | beta | canary) — consumer `.claude/_overlay/project.yaml codeforge.channel.tier` 선언 시 family 7 plugin channel-aware annotation marker.
  # canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2). marketplace.json sync 면제 (declare layer SSOT only, plugin.json bump 0).
  # ADR-008 §결정 3 SSOT: 신규 label entry append + 신규 category 신설 = MINOR bump (v2.29 → v2.30, CFP-894 v2.29 hotfix-bypass:inter-plugin-contracts-parity 직후 sequential).
  - name: channel:stable
    category: channel
    color: "0e8a16"
    description: "channel: stable tier marker (CFP-906 / ADR-076 §결정 9.1 — codeforge family plugin distribution 의 default release tier). consumer `codeforge.channel.tier: stable` 선언 PR/Issue channel-aware annotation. LOW risk class (production impact: none — developer self-service OK). Wave 4 sub-Epic #1 Story-1 carrier, Epic CFP-882."
    single_active: false
    attach_owner_plugin: "Orchestrator (consumer codeforge.channel.tier 선언 PR/Issue open 시 부착) / 사용자 직접 / channel-drift-detection.yml (Wave 4 sub-Epic #1 Story-2 carrier 시점 자동 부착 영역)"

  - name: channel:beta
    category: channel
    color: "d4c5f9"
    description: "channel: beta tier marker (CFP-906 / ADR-076 §결정 9.1 — opt-in incremental track). consumer `codeforge.channel.tier: beta` 선언 PR/Issue channel-aware annotation. MEDIUM risk class (production impact: observable but reversible — developer + reviewer awareness 충분). Wave 4 sub-Epic #1 Story-1 carrier."
    single_active: false
    attach_owner_plugin: "Orchestrator (consumer codeforge.channel.tier 선언 PR/Issue open 시 부착) / 사용자 직접 / channel-drift-detection.yml (Wave 4 sub-Epic #1 Story-2 carrier 시점 자동 부착 영역)"

  - name: channel:canary
    category: channel
    color: "f9d0c4"
    description: "channel: canary tier marker (CFP-906 / ADR-076 §결정 9.1 + §결정 9.4 — preview + production-impact tier). consumer `codeforge.channel.tier: canary` 선언 PR/Issue channel-aware annotation. HIGH risk class (production cutover semantic — admin tier 권장, consumer-side 책임 + CODEOWNERS auto-review path 권장 advisory). canary tier 선언 시 Wave 4 sub-Epic #1 Story-3 ProductionEvidenceDeputy spawn trigger 영역 (ADR-72 §결정 1 정합 — Story-1 declare layer 영역 외). Wave 4 sub-Epic #1 Story-1 carrier."
    single_active: false
    attach_owner_plugin: "Orchestrator (consumer codeforge.channel.tier 선언 PR/Issue open 시 부착) / 사용자 직접 / channel-drift-detection.yml (Wave 4 sub-Epic #1 Story-2 carrier 시점 자동 부착 영역)"

  # parent:* (CFP-949 추가 — Sub-Epic 6 lane plugin self-owned architecture doc seed)
  # 기존 parent:CFP-* family pattern 답습 (parent:CFP-541 / parent:CFP-425 / parent:CFP-525 / parent:CFP-548 선례).
  # bootstrap-labels.sh L112 ↔ registry 양방향 sync (CFP-33 STRICT lint).
  - name: parent:CFP-949
    category: parent
    color: "ededed"
    description: "Child Story of Sub-Epic CFP-949 (6 lane plugin self-owned architecture doc seed)"
    single_active: false
    attach_owner_plugin: "Orchestrator (Sub-Epic CFP-949 child Story Issue open 시 부착) / GitOpsAgent (sub-issue 생성 시 자동 부착)"

  # plugin:* (CFP-949 추가 — 4 lane plugin namespace marker)
  # Wave 1 CFP-968/969/970 + Wave 2 CFP-972 carrier. plugin:codeforge-{review,pmo} 는 사전 wrapper repo 환경에서 부트스트랩 형태로 이미 존재.
  # bootstrap-labels.sh L116-119 ↔ registry 양방향 sync (CFP-33 STRICT lint).
  - name: plugin:codeforge-requirements
    category: plugin
    color: "ededed"
    description: "Plugin namespace: codeforge-requirements (요구사항 lane)"
    single_active: false
    attach_owner_plugin: "Orchestrator (plugin scope PR/Issue open 시 부착) / GitOpsAgent (lane-targeted sub-issue 생성 시 자동 부착)"

  - name: plugin:codeforge-design
    category: plugin
    color: "ededed"
    description: "Plugin namespace: codeforge-design (설계 lane)"
    single_active: false
    attach_owner_plugin: "Orchestrator (plugin scope PR/Issue open 시 부착) / GitOpsAgent (lane-targeted sub-issue 생성 시 자동 부착)"

  - name: plugin:codeforge-develop
    category: plugin
    color: "ededed"
    description: "Plugin namespace: codeforge-develop (구현 lane)"
    single_active: false
    attach_owner_plugin: "Orchestrator (plugin scope PR/Issue open 시 부착) / GitOpsAgent (lane-targeted sub-issue 생성 시 자동 부착)"

  - name: plugin:codeforge-test
    category: plugin
    color: "ededed"
    description: "Plugin namespace: codeforge-test (통합테스트 lane)"
    single_active: false
    attach_owner_plugin: "Orchestrator (plugin scope PR/Issue open 시 부착) / GitOpsAgent (lane-targeted sub-issue 생성 시 자동 부착)"

  # production-impact:* (1 entry — CFP-954 / ADR-72 §결정 1 + §결정 5 carrier, Wave 4 sub-Epic #882 Story-3 production cutover layer mandate activation declare scope)
  # 신규 category enum: production-impact (별도 axis from channel — release lifecycle vs production risk).
  # production-touching = HIGH severity invariant (severity-propagation-v1 v1.0 binding cross-ref only).
  # canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2). marketplace.json sync 면제.
  # ADR-008 §결정 3 SSOT: 신규 label entry append + 신규 category 신설 = MINOR bump (v2.33 → v2.34, CFP-949 v2.33 collision rebase ratchet).
  # MANIFEST.yaml ratchet 동반 ("2.33" CFP-949 → "2.34" CFP-954 carrier).
  - name: production-touching
    category: production-impact
    color: "b60205"
    severity_binding: "severity:high"
    description: "Story touches production cutover surface — explicit user go-ahead required before lane entry (ADR-72 §결정 3 trigger axis 정합 — Live touching + production cutover both = ProductionEvidence + LiveOps + LiveOrdering 9 SubAgent both spawn 의무). CFP-954 Story-3 carrier — production cutover layer mandate **activation declare** scope (실 first spawn = consumer Story 영역, wrapper-self-app N/A ADR-72 §결정 6 정합). 본 label 부착 PR/Issue = HIGH severity invariant (severity-propagation-v1 v1.0 cross-ref). production-cutover-evidence.yml workflow PR-open trigger 영역. canary tier (channel:canary) 와 2-axis disjoint — channel = release lifecycle / production-impact = production risk (DataMigrationArch §G.3 정합, 양 label 동시 부착 가능 semantic axis 2-way split)."
    single_active: false
    attach_owner_plugin: "사용자 직접 (Phase 1 PR open 전 explicit go-ahead 의무 진입) / Orchestrator (Story §1 frontmatter `production_cutover_touching: true` 선언 PR/Issue open 시 부착)"

  # canary promotion criteria (4 entries — CFP-991 / ADR-72 Amendment 3 + ADR-076 §결정 9.6 + reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding carrier, Wave 4 sub-Epic #1 Story-4 enforcement layer)
  # hotfix-bypass:canary-promotion-criteria = 46번째 family member (warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel).
  # gate:channel-{canary,beta,stable}-promotion = 3 entry (canary→beta→stable transition gate marker, attach_owner_plugin: codeforge-design / 사용자 직접).
  # canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2). marketplace.json sync 면제, plugin.json bump 0.
  # ADR-008 §결정 3 SSOT: 신규 label entry append = MINOR bump (v2.34 → v2.35, 4 family member 동시 추가).
  # MANIFEST.yaml ratchet 동반 ("2.34" CFP-954 → "2.35" CFP-991 carrier).
  - name: hotfix-bypass:canary-promotion-criteria
    category: hotfix-bypass
    color: "fef2c0"
    description: "templates/github-workflows/canary-promotion-criteria.yml (CFP-991 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, 43번째 hotfix-bypass:* family member). reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding.promotion_gate_failure_mode.bypass_label field 정합 — consumer canary→beta promotion gate 4-tuple evidence quad 일시 부재 시 bypass 영역 (ADR-060 evidence-enforceable promotion framework `canary-compatibility-check` evidence-checks-registry entry warning-tier cross-ref). bypass 사용 시 check-bypass-audit-comment.sh 가 audit comment 자동 발의."
    single_active: false
    attach_owner_plugin: "사용자 직접 (PR open 시 부착 — bypass 사용 시점 audit comment 자동 발의 후 reviewer approval)"
  - name: gate:channel-canary-promotion
    category: gate
    color: "0e8a16"
    description: "consumer canary tier 활성 PR 안 4-tuple evidence quad 충족 marker (functional + security + monitoring + testing all 'pass' OR 'n_a'). reconcile-protocol-v1 v1.11 §4.14 canary_compatibility_check_binding.promotion_criteria_4tuple cross-ref (ADR-076 §결정 9.6 4 industry exemplar Chrome 3-channel SSOT verbatim cite). Tier-2 admin tier 권장 영역 (consumer-side 책임 advisory). T-3.1 mitigation core field — attach_owner_plugin: consumer_repo_only invariant + workflow `if: github.repository != 'mclayer/plugin-codeforge'` mechanical guard (wrapper-self-app trigger 차단)."
    single_active: false
    attach_owner_plugin: "codeforge-design (consumer Story carrier 영역 — Orchestrator 가 promotion_criteria_4tuple 4-tuple all 'pass' OR 'n_a' verify 후 부착)"
  - name: gate:channel-beta-promotion
    category: gate
    color: "0e8a16"
    description: "consumer beta tier promotion gate marker (canary → beta transition). 동일 4-tuple evidence quad gate evaluation 적용 (reconcile-protocol-v1 v1.11 §4.14 cross-ref). Tier-2 admin tier 권장 영역."
    single_active: false
    attach_owner_plugin: "codeforge-design (consumer Story carrier 영역 — Orchestrator 가 promotion_criteria_4tuple 4-tuple all 'pass' OR 'n_a' verify 후 부착)"
  - name: gate:channel-stable-promotion
    category: gate
    color: "0e8a16"
    description: "consumer stable tier promotion gate marker (beta → stable transition). 동일 4-tuple evidence quad gate evaluation 적용 (reconcile-protocol-v1 v1.11 §4.14 cross-ref). Tier-2 admin tier 권장 영역."
    single_active: false
    attach_owner_plugin: "codeforge-design (consumer Story carrier 영역 — Orchestrator 가 promotion_criteria_4tuple 4-tuple all 'pass' OR 'n_a' verify 후 부착)"
  # hotfix-bypass:prod-cutover-deputy-evidence = 45번째 (raw) family member registry-side late codify.
  # CFP-954 carrier 당시 gh-side 등록은 완료됐으나 registry §3 declaration 누락 (bidirectional drift Tier-A 식별 — CFP-963 retro).
  # CFP-1000 Tier-A closure carrier: registry §3 declare → gh-side / §3 양방향 정합 완료.
  # canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2). marketplace.json sync 면제, plugin.json bump 0.
  # ADR-008 §결정 3 SSOT: 신규 label entry append = MINOR bump (v2.37 → v2.38, collision rebase ratchet).
  # MANIFEST.yaml ratchet 동반 ("2.37" CFP-1000 → "2.38" CFP-1000 carrier).
  - name: hotfix-bypass:prod-cutover-deputy-evidence
    category: hotfix-bypass
    color: "ededed"
    description: "ADR-72 §결정 3 production-cutover-deputy-spawn-evidence bypass — deferred (CFP-954 carrier: Wave 4 sub-Epic #882 Story-3 ProductionEvidenceDeputy mandate activation declare scope. wrapper-self-app Tier-1 exemption invariant 보존 — wrapper PR = declare-time 면제 triple-AND fast-PASS. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). registry §3 late codify: gh-side 등록 CFP-954 PR-time / §3 선언 누락 → CFP-1000 Tier-A 정합 carrier."
    single_active: false
    attach_owner_plugin: "사용자 직접 (wrapper-self-app Tier-1 declare-time 면제 / consumer Tier-2 admin-tier 권장)"

  # CFP-1006 v2.39 Tier-B 4-way sync bidirectional drift sweep (Wave 1) — 4 신규 entry registry-side late codify (gh→registry missing).
  # All 4 entries gh-side actively used pre-existing — registry §3 declaration absent at codify time.
  # ADR-024 Amendment 11 §결정 6.A per-entry namespace 정합 (47-50번째 family member, raw active concrete grep count convention 답습 = CFP-1000 Amendment 10 precedent).
  # canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2). marketplace.json sync 면제, plugin.json bump 0.
  # ADR-008 §결정 3 SSOT: 신규 label entry append = MINOR bump (v2.38 → v2.39).
  # MANIFEST.yaml ratchet 동반 ("2.38" CFP-1000 → "2.39" CFP-1006 carrier).
  # bootstrap-labels.yml workflow PR open 시 auto-fire — 4 entries gh-side idempotent invariant (gh API 422 already-exists swallow / 201 created — depend on per-label).

  # 47번째 family member — comment-prefix-registry contract version bump (v1.x append-only governance) 영역 bypass.
  # Provenance: 12+ merged PRs (Issue #1011 bypass-counter signature reach evidence). Operational scope = doc-only fast-path PRs that touch comment-prefix-registry-v1.md frontmatter version field without full ADR-008 contract-bump ceremony (e.g., CFP-845 Phase 2 [bypass-justification] 14th prefix introduction sibling sync).
  # Backing CFP carrier = CFP-845 (historical, Amendment 8 §결정 6.A.4). No dedicated workflow file (no auto-lint backing — pure governance audit-trail channel).
  - name: hotfix-bypass:comment-prefix-registry
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: comment-prefix-registry-v1 contract version bump governance ceremony (ADR-008 contract MINOR/PATCH) conditional skip + audit comment 자동 발의 (CFP-845 Amendment 8 §결정 6.A.4 historical carrier — comment-prefix-registry-v1 v1.3 14번째 [bypass-justification] prefix 신설 시 사용 / 후속 CFP-NNN doc-only fast-path PR 의 contract bump ceremony skip 영역. ADR-024 Amendment 11 §결정 6.A per-entry namespace 정합). 47번째 hotfix-bypass:* family member (raw active concrete grep count convention 답습). CFP-1006 v2.39 registry §3 late codify (gh-side 등록 ≥ 12 PR pre-existing / §3 선언 누락 → Tier-B 4-way sync Wave 1 carrier)."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로 — doc-only fast-path PR governance audit-trail)"

  # 48번째 family member — Epic-cutover quad-check evidence presence governance bypass.
  # Provenance: docs/evidence-checks-registry.yaml line 1441 + ADR-72 line 36. Operational scope = production-touching Epic-cutover PR 가 4-tuple evidence quad (live_touching / production_cutover_touching / marketplace_publish_touching / consumer_impact_blast_radius) check skip 영역 (wrapper-self-app Tier-1 exemption / consumer Tier-2 admin tier).
  # Backing carrier = ADR-72 §결정 1 + §결정 5 (Wave 4 sub-Epic #882 Story-3, CFP-954). Workflow file = production-cutover-evidence.yml (CFP-954 / ADR-72 §결정 1).
  - name: hotfix-bypass:epic-cutover-quad-check
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: Epic-cutover quad-check 4-tuple evidence presence lint conditional skip + audit comment 자동 발의 (ADR-72 §결정 1/§결정 5 carrier — Wave 4 sub-Epic #882 Story-3 ProductionEvidenceDeputy mandate activation declare scope, CFP-954 / templates/github-workflows/production-cutover-evidence.yml + docs/evidence-checks-registry.yaml `epic-cutover-gate-evidence-quad-check` entry. ADR-024 Amendment 11 §결정 6.A per-entry namespace 정합). 48번째 hotfix-bypass:* family member (raw active concrete grep count convention 답습). CFP-1006 v2.39 registry §3 late codify (gh-side 등록 CFP-954 PR-time / §3 선언 누락 → Tier-B 4-way sync Wave 1 carrier). 단, ADR-72 §결정 6 wrapper-self-app Tier-1 declare-time 면제 invariant 보존 — wrapper PR scope 영역 외."
    single_active: false
    attach_owner_plugin: "사용자 직접 (wrapper-self-app Tier-1 declare-time 면제 / consumer Tier-2 admin-tier 권장)"

  # 49번째 family member — evidence-checks-registry entry naming convention lint bypass.
  # Provenance: docs/evidence-checks-registry.yaml line 1053 + scripts/lib/check_evidence_registry_naming.py line 160 + templates/github-workflows/evidence-registry-naming-check.yml line 30. Operational scope = evidence-checks-registry.yaml row name convention check warning-tier skip (when legitimate naming exception arises, e.g., backward-compat alias).
  # Backing carrier = ADR-060 framework (evidence-checks-registry-v1 naming convention guardrail).
  - name: hotfix-bypass:evidence-naming
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: evidence-checks-registry.yaml entry name convention warning-tier lint conditional skip + audit comment 자동 발의 (ADR-060 framework / scripts/lib/check_evidence_registry_naming.py SSOT — templates/github-workflows/evidence-registry-naming-check.yml carrier — name field kebab-case + reserved prefix invariant check, warning tier. ADR-024 Amendment 11 §결정 6.A per-entry namespace 정합). 49번째 hotfix-bypass:* family member (raw active concrete grep count convention 답습). CFP-1006 v2.39 registry §3 late codify (gh-side 등록 pre-existing / §3 선언 누락 → Tier-B 4-way sync Wave 1 carrier)."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # 50번째 family member — Markdown internal-links broken-link warning-tier lint bypass.
  # Provenance: 11+ merged PRs (Issue #1013 bypass-counter signature reach evidence). Operational scope = doc-only fast-path PRs that introduce intentional non-existent internal links (e.g., forward references to future Story files, ADR placeholders, planned-but-deferred docs).
  # Backing carrier: general doc maintenance lint (broken markdown links detection) — used extensively across CFP-NNN doc PRs. No dedicated workflow file (general lint scope).
  - name: hotfix-bypass:markdown-internal-links
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: Markdown internal-links broken-link detection lint conditional skip + audit comment 자동 발의 (general doc maintenance lint scope — forward reference 영역 / planned-but-deferred docs / 미실재 ADR placeholder 인용 시 warning-tier skip, false-positive 영역. ADR-024 Amendment 11 §결정 6.A per-entry namespace 정합). 50번째 hotfix-bypass:* family member (raw active concrete grep count convention 답습). CFP-1006 v2.39 registry §3 late codify (gh-side 등록 ≥ 11 PR pre-existing / §3 선언 누락 → Tier-B 4-way sync Wave 1 carrier)."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로 — doc-only fast-path PR forward reference 영역)"

  # 51번째 family member — Multi-session collaboration protocol Wave 2 mechanical wire bypass channel (ADR-085 §결정 2 active_sessions[] field presence-grep lint, Story Issue body + Story file frontmatter dual carrier).
  # Provenance: 8 parallel race incidents single session lineage (CFP-953/946/949/932/954/991/967/1014 lineage, 2026-05-18 ~ 2026-05-19 KST) — ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach escalation_action adr_draft_emitted 산물.
  # Backing carrier: ADR-085 §결정 8 mechanical_enforcement_actions[] 2-entry deferred-followup (declaration-only-Wave-1, Phase 2 별 sub-CFP carrier — workflow + script + bats 실 wire).
  - name: hotfix-bypass:active-sessions-presence
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: ADR-085 §결정 2 active_sessions[] field presence-grep lint conditional skip + audit comment 자동 발의 (Wave 2 mechanical wire 별 sub-CFP carrier — templates/scripts/check-active-sessions-presence.{sh,py} + templates/github-workflows/active-sessions-presence.yml warning-tier. Story Issue body `<!-- active_sessions -->` HTML comment block + Story file frontmatter `active_sessions:` array 5-tuple field (git_identity / worktree_path / entry_phase / entered_at_kst / last_heartbeat_kst) dual carrier presence check. backward-compat: 기존 미명시 Story default `[]` (Wave 1 declarative — Wave 2 mechanical lint promotion 시 점진 ratchet). ADR-024 Amendment N §결정 6.A per-entry namespace 정합). 51번째 hotfix-bypass:* family member (raw active concrete grep count convention 답습, v2.39 baseline 50 → +2 → 52 / parallel session bump 시 ratchet)."
    single_active: false
    attach_owner_plugin: "Orchestrator (hotfix-bypass 경로 — multi-session ownership declaration 영역 Wave 2 mechanical wire 도입 전 declarative-only Story PR bypass)"

  # 52번째 family member — Multi-session collaboration protocol Wave 2 mechanical wire bypass channel (ADR-085 §결정 3 lane-entry sentinel 4-step polling subprocess invoke, ADR-073 Amendment 2 polling enum 4번째 source `active_sessions_check` cross-ref wire).
  # Provenance: 8 parallel race incidents single session lineage (CFP-953/946/949/932/954/991/967/1014 lineage, 2026-05-18 ~ 2026-05-19 KST) — ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach escalation_action adr_draft_emitted 산물.
  # Backing carrier: ADR-085 §결정 8 mechanical_enforcement_actions[] 2-entry deferred-followup (declaration-only-Wave-1, Phase 2 별 sub-CFP carrier — workflow + script + hook + bats 실 wire).
  - name: hotfix-bypass:lane-entry-ownership-verify
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: ADR-085 §결정 3 lane-entry sentinel 4-step polling subprocess invoke lint conditional skip + audit comment 자동 발의 (Wave 2 mechanical wire 별 sub-CFP carrier — templates/scripts/check-lane-entry-ownership.{sh,py} + templates/github-workflows/lane-entry-ownership-verify.yml warning-tier. ADR-073 Amendment 2 polling enum 4번째 source `active_sessions_check` cross-ref wire — lane 진입 직전 4-step polling: memory rule 6 title-based search + memory rule 7 Epic state poll + active_sessions[] field check + lane-entry sentinel `gh pr list --search head:<branch>` PR existence check. 1+ failure 시 Orchestrator 가 사용자 dialog 발화 (Inline whitelist 1번 entry, codeforge:user-dialog-mode skill 경유) — parallel session defer / takeover / abandon 결정. ADR-024 Amendment N §결정 6.A per-entry namespace 정합). 52번째 hotfix-bypass:* family member (raw active concrete grep count convention 답습, v2.39 baseline 50 → +2 → 52 / parallel session bump 시 ratchet)."
    single_active: false
    attach_owner_plugin: "Orchestrator (hotfix-bypass 경로 — lane spawn 직전 4-step polling subprocess Wave 2 mechanical wire 도입 전 declarative-only Story PR bypass)"
```

## 4. 변경 규칙

- **v2.x append-only**: 새 label 추가는 minor (v2.1). 기존 label 삭제 또는 이름 변경은 v3.0 BREAKING (ADR-008)
- **`single_active: true` invariant**: phase:* 카테고리만 single-active
- **`bootstrap-labels.sh` SSOT 역전 (CFP-33 contract harness 후)**: 현재 script 가 hardcoded source. CFP-33 에서 본 registry → script 자동 생성으로 전환
### v2.27 변경 이력 (CFP-848)

- 신규 `hotfix-bypass:adr-077-integration` family member 추가 — ADR-077 stale 게이트·envelope·4-layer disjoint runtime mechanical lint (evidence-checks-registry `adr-077-integration` entry 의 bypass channel). ADR-024 Amendment 3 hotfix-bypass:* family pattern 정합 (audit-trailed exception, warning tier).
- introduced_by: CFP-848 (Epic A Story-5 Phase 2 carrier)
- carrier_adr: ADR-060 (evidence-enforceable warning-tier framework)
- date: 2026-05-17
