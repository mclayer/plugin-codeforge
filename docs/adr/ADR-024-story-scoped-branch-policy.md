---
adr_number: 24
title: Story-scoped branch policy — main 직접 수정 금지 + Phase 2 enforcement deferred
status: Accepted
category: governance
date: 2026-05-03
is_transitional: false
amended_by: CFP-1025
amended_date: 2026-05-19
amendments:
  - by: "CFP-134"
    date: "2026-05-08"
    scope: "hierarchical branch convention 추가 — flat cfp-NNN 에서 cfp-NNN[/<lane>[/<sub>]] 계층까지 분기 가능"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hierarchical branch convention 은 영구 SSOT 확장."
  - by: "CFP-280"
    date: "2026-05-11"
    scope: "required_status_checks.contexts drift invariant + branch-protection-manifest.yaml SSOT + branch-protection-drift-check.yml 자동화"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). drift invariant 는 영구 enforcement."
  - by: "CFP-389"
    date: "2026-05-11"
    scope: "audit-trailed exception channel = hotfix-bypass:* label family (carrier ADR-060) — §결정 6 의 evidence-enforceable mechanical check 호환"
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hotfix-bypass label family 자체는 ADR-060 framework 와 연동된 영구 channel — 개별 evidence check entry 의 enforce 승격 시점에만 활성."
  - by: "CFP-426"
    date: "2026-05-12"
    scope: "§결정 6.A per-entry namespace 의 4 신규 `hotfix-bypass:worktree-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}` label entry 추가 (ADR-040 Amendment 3 동반 / CFP-425 Epic Story 1) — `hotfix-bypass:adr-sunset` 패턴 직접 mirror, 단일 audit lint `scripts/check-bypass-audit-comment.sh` reuse."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 4 worktree-first label = §결정 6.A per-entry namespace 의무의 영구 확장."
  - by: "CFP-481"
    date: "2026-05-12"
    scope: "Amendment 4 — §결정 6.A per-entry namespace 의 7번째 신규 `hotfix-bypass:auto-phase-label` label entry 추가 (ADR-060 Amendment 4 동반 — 3rd warning-tier entry `auto-phase-label`) + §결정 6.A.1 (신설) branch → phase mapping 표 SSOT (cfp-NNN[/<lane>[/<sub>]] hierarchical → phase:* 8 label mapping verbatim, ADR-024 Amendment 1 hierarchical convention 의 직접 확장)."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hotfix-bypass:auto-phase-label = §결정 6.A per-entry namespace 의무의 영구 확장. branch → phase mapping 표 = ADR-024 Amendment 1 hierarchical convention 의 영구 SSOT 명세화."
  - by: "CFP-582"
    date: "2026-05-13"
    scope: "Amendment 5 — §결정 6.A per-entry namespace 의 12번째 신규 `hotfix-bypass:debate-convergence-quality` label entry 추가 (ADR-059 Amendment 2 §결정 8 동반 — convergence_quality_invariant 첫 debate 영역 warning-tier entry `debate-convergence-quality-marker-presence`, ADR-060 framework 정합). prior art `hotfix-bypass:adr-sunset` (CFP-389) + 4 `hotfix-bypass:worktree-*` (CFP-426) + `hotfix-bypass:auto-phase-label` (CFP-481) + `hotfix-bypass:claude-md-line-cap` (CFP-506) + `hotfix-bypass:sibling-pr-author-check` (CFP-521) + `hotfix-bypass:workflow-permissions` (CFP-530) + `hotfix-bypass:workflow-yaml-parse` (CFP-583) 직접 mirror, 단일 audit lint `scripts/check-bypass-audit-comment.sh` reuse."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). hotfix-bypass:debate-convergence-quality = §결정 6.A per-entry namespace 의무의 영구 확장 (debate 영역 첫 family member)."
  - by: "CFP-825"
    date: "2026-05-17"
    scope: "Amendment 6 — §결정 6.A per-entry namespace 누적 사용 카운터 lint (bypass-label-counter, 63번째 evidence-checks-registry entry, warning tier first iteration) + 31번째 family member `hotfix-bypass:bypass-label-counter` (self-meta loop 회피) + 32번째 family member `hotfix-bypass:exempt:<entry>` template (rare 정당 declare 채널, narrative audit trail mechanical enforce = 후속 carrier). ratchet 룰: per-(plugin, label) signature ≥3 reach-merged PR 누적 시 carrier Issue 자동 발의 + dedup (window=all-time / dedup_unit=PR number / exempt 2종). CFP-771 retro §8 제안 1 carrier — exception → norm mutation 위험 누적 monitoring 부재 차단."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). bypass-label-counter = forbid scope 확장 (ratchet-up 강화 방향, ADR-058 §결정 5 정합). 2 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장 (self-meta + rare 정당 declare 2종 channel)."
  - by: "CFP-841"
    date: "2026-05-17"
    scope: "Amendment 7 — §결정 6.A per-entry namespace 의 34번째 신규 `hotfix-bypass:corpus-claim-verify` + 35번째 신규 `hotfix-bypass:cross-plugin-ownership-verify` family member 추가 (ADR-082 Amendment 1 carrier — §결정 6 behavioral→mechanical 전환, ADR-060 framework 2 신규 warning-tier evidence-checks-registry entry `corpus-claim-verify` + `cross-plugin-ownership-verify`). write-time semantic truth verify 영역 첫 family member."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 2 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장 (write-time semantic truth verify 영역 첫 진입)."
  - by: "CFP-845"
    date: "2026-05-17"
    scope: "Amendment 8 — bypass-as-norm-mutation 후속 escalation 3 sub-decision 통합 (CFP-825 Amendment 6 §scope_boundary 의 4 out-of-scope 후속 carrier 영역 중 3 즉시 통합, 4번째 `blocking-on-merge tier 격상` = Story-2 #861 RESERVED 별 carrier evidence-gated 분리). §결정 6.A.3 (신설) per-plugin 전체 누적 카운터 ratchet — 단일 plugin 의 모든 hotfix-bypass:* family entry 누적 ≥5 reach-merged PR (signature = plugin-only, dedup_unit = PR number, window = all-time) 시 carrier Issue 자동 발의. §결정 6.A.4 (신설) `[bypass-justification]` PR comment marker mechanical enforce — hotfix-bypass:* label 부착 PR 의 marker presence grep-only lint (semantic adequacy 불가 = false-positive risk 명시, reviewer responsibility). §결정 6.A.5 (신설) cross-repo bypass counter extension — wrapper (plugin-codeforge) 단일 → internal-docs / marketplace sibling repo 3-repo 동시 cover, signature = (repo, plugin, label) 3-tuple, 단일 PAT (CODEFORGE_CROSS_REPO_PAT) reuse. §결정 6.A (확장) `hotfix-bypass:per-plugin-cumulative-counter` 37번째 + `hotfix-bypass:bypass-justification-marker` 38번째 + `hotfix-bypass:cross-repo-bypass-counter` 39번째 family member."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 3 신규 sub-decision = bypass-as-norm mutation 누적 monitoring 의 ratchet-up 강화 방향 (per-entry → per-plugin / narrative audit / cross-repo 확장). ADR-058 §결정 5 정합. 3 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장."
  - by: "CFP-963"
    date: "2026-05-19"
    scope: "Amendment 9 — §결정 6.A per-entry namespace 의 44번째 신규 `hotfix-bypass:codex-sandbox-substitution` family member 추가 (ADR-060 Amendment 14 §결정 28 carrier — 12번째 warning-tier evidence-checks-registry entry `codex-network-scope-presence` bypass channel + ADR-081 Amendment 4 §결정 D1.D 본문 확장 mechanical enforcement layer). historical-with-template-count convention citation (Codex TP#2 F-CX-963-A P2 calibration verdict 정합) — `^  - name: hotfix-bypass:` direct grep count = 42 active concrete entry + CFP-825 Amendment 6 §결정 6.A.2 `hotfix-bypass:exempt:<entry>` 32번째 template (rare 정당 declare 채널, template-not-concretely-instantiated 영역 — historical Nth count 1 포함) + 직전 family member `hotfix-bypass:architecture-drift` 43번째 (CFP-923 self-describe L1011 정합) → 신규 = 44번째 historical Nth count convention. label-registry-v2 v2.34 → v2.35 MINOR bump 동반 (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 3 row append). prior art `hotfix-bypass:adr-sunset` (CFP-389) + `hotfix-bypass:worktree-*` 4 (CFP-426) + `hotfix-bypass:auto-phase-label` (CFP-481) + `hotfix-bypass:claude-md-line-cap` (CFP-506) + `hotfix-bypass:sibling-pr-author-check` (CFP-521) + `hotfix-bypass:workflow-permissions` (CFP-530) + `hotfix-bypass:workflow-yaml-parse` (CFP-583) + `hotfix-bypass:debate-convergence-quality` (CFP-582) + `hotfix-bypass:wording-dictionary` (CFP-610) + `hotfix-bypass:retro-mandatory-deployed` (CFP-619) + `hotfix-bypass:retro-alert-pickup` (CFP-628) + `hotfix-bypass:marketplace-description-verbatim` (CFP-631) + `hotfix-bypass:stop-time-continuous-confirm` (CFP-638) + `hotfix-bypass:marketplace-drift-detection` (CFP-627) + `hotfix-bypass:workflow-version-drift` (CFP-660) + `hotfix-bypass:bootstrap-labels` (CFP-662) + `hotfix-bypass:auto-phase-label-sibling-parity` (CFP-685) + `hotfix-bypass:claude-md-amendment-ref` (CFP-708) + `hotfix-bypass:actionlint` + `hotfix-bypass:post-merge-followup-success-rate` (CFP-688) + `hotfix-bypass:wrapper-managed-block` (CFP-702) + `hotfix-bypass:kst-timestamp-display` (CFP-771) + `hotfix-bypass:story-section-ownership` (CFP-722) + `hotfix-bypass:adr-077-ratchet` + `hotfix-bypass:adr-077-design-reading` (CFP-785) + `hotfix-bypass:bypass-label-counter` + `hotfix-bypass:exempt:<entry>` template (CFP-825) + `hotfix-bypass:version-3way-atomic` (CFP-820) + `hotfix-bypass:corpus-claim-verify` + `hotfix-bypass:cross-plugin-ownership-verify` (CFP-841) + `hotfix-bypass:branch-protection-sync` (CFP-821) + `hotfix-bypass:per-plugin-cumulative-counter` + `hotfix-bypass:bypass-justification-marker` + `hotfix-bypass:cross-repo-bypass-counter` (CFP-845) + `hotfix-bypass:fix-event-depth-scope` (CFP-842) + `hotfix-bypass:inter-plugin-contracts-parity` (CFP-894) + `hotfix-bypass:channel-drift-detection` (CFP-932) + `hotfix-bypass:architecture-drift` (CFP-923) 직접 mirror, 단일 audit lint `scripts/check-bypass-audit-comment.sh` reuse."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 1 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장 (codex worker collaboration mechanical layer bypass channel 영역 첫 family member). ratchet-UP 강화 방향 (active concrete grep count 42 → 43 정합 + historical Nth 43 → 44 convention 정합 ADR-058 §결정 5 정합)."
  - by: "CFP-1000"
    date: "2026-05-19"
    scope: "Amendment 10 — §결정 6.A per-entry namespace 의 45번째 (raw) 신규 `hotfix-bypass:prod-cutover-deputy-evidence` family member registry-side late codify (CFP-954 carrier originally registered in gh repo at PR-time but missed registry §3 declaration — bidirectional drift Tier-A closure, CFP-963 retro 식별 + CFP-1000 Tier-A carrier). gh-side 1 hit verified 2026-05-19 KST, registry §3 yaml append 누락 sync gap closure. ADR-72 §결정 5 evidence-checks-registry 2 entry (production-cutover-deputy-spawn-evidence + epic-cutover-gate-evidence-quad-check) warning-tier bypass channel — Wave 4 sub-Epic #882 Story-3 ProductionEvidenceDeputy mandate first activation declare layer + Epic close-time quad-check. label-registry-v2 v2.36 → v2.37 MINOR bump 동반 (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 3 row append). `hotfix-bypass:inter-plugin-contracts-parity` (CFP-894 v2.29 L994 이미 declared, gh-side 0 hits) 는 bootstrap-labels.yml workflow PR open 시 auto-run 의무 발효 영역 — registry §3 변경 0건, gh CLI 실행만 추가 (CFP-598 dynamic registry-driven pattern 자동, scripts/parse-hotfix-bypass-labels.py가 §3 yaml read auto-emit). 카운트 convention: raw active concrete grep (Amendment 9 historical-with-template-count convention 과 disjoint — template-vs-concrete 모호성 영역 외, entry-specific calibration). CFP-967 v2.36 self-describe \"45번째 (historical-with-template-count)\" 와 본 Amendment 10 raw count 45번째 는 동일 숫자 우연 — CFP-967 = pre-edit raw 44 + historical adjustment 1 = 45 historical / 본 Amendment 10 = post-edit raw 45 (pre-edit 44 + 1 new). 동일 숫자 occurrence 는 convention divergence calibration artifact. CLAUDE.md L295 prose `hotfix-bypass:prod-cutover-deputy-evidence 44번째` 인용 = CFP-954 PR-time historical-with-template-count attribution 보존 (본 Story OOS — Tier-B CFP #1004 영역). Tier-B (bidirectional drift 잔여 34 entries reconcile sweep) = 별 CFP #1004 (post-merge open) 영역 (ADR-064 §결정 1 CFP scope unitary 정합 — 한 CFP 안 Tier-A → Tier-B 단계 채택 금지). prior art Amendment 9 (CFP-963) 직전 carrier 정합."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 1 신규 family member = §결정 6.A per-entry namespace 의무의 영구 확장 (production-cutover evidence 영역 first registry-side codify). ratchet-UP 강화 방향 (active concrete grep count 44 → 45 정합 raw active concrete, registry-gh 4-way sync gap 부분 closure, 약화 영역 0건 ADR-058 §결정 5 정합)."
  - by: "CFP-1006"
    date: "2026-05-19"
    scope: "Amendment 11 — Tier-B 4-way sync bidirectional drift sweep (Wave 1): §결정 6.A per-entry namespace 의 47/48/49/50번째 (raw) 4 신규 family member registry-side late codify (gh→registry missing direction): `hotfix-bypass:comment-prefix-registry` (12+ PR audit-trail Issue #1011 bypass-counter signature reach, CFP-845 historical carrier — comment-prefix-registry-v1 contract bump governance ceremony skip) + `hotfix-bypass:epic-cutover-quad-check` (ADR-72 §결정 1/§결정 5 production-cutover-evidence.yml workflow + evidence-checks-registry epic-cutover-gate-evidence-quad-check entry backing, CFP-954 carrier) + `hotfix-bypass:evidence-naming` (ADR-060 framework + scripts/lib/check_evidence_registry_naming.py + templates/github-workflows/evidence-registry-naming-check.yml backing) + `hotfix-bypass:markdown-internal-links` (11+ PR audit-trail Issue #1013 bypass-counter signature reach, general doc maintenance lint forward reference scope). 1 naming mismatch resolution: registry §3 entry rename `hotfix-bypass:claude-md-amendment-ref` → `hotfix-bypass:claude-md-amendment-ref-drift` (conservative direction matches gh repo label + workflow filename claude-md-amendment-ref-drift.yml + 5+ PR audit history; rename target never-instantiated in gh = registry-side 0 effect on gh consumers, §4 변경 규칙 v2.x append-only exception 영역). label-registry-v2 v2.38 → v2.39 MINOR bump 동반 (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 3 row append + rename). MANIFEST.yaml row \"2.38\" → \"2.39\". 35 of 36 registry→gh missing 자동 해소 expected via bootstrap-labels.yml workflow PR open auto-fire (CFP-598 dynamic registry-driven pattern via parse-hotfix-bypass-labels.py — §3 yaml read auto-emit, registry append + rename 만으로 5 entry 자동 처리). 카운트 convention: raw active concrete grep (CFP-1000 Amendment 10 답습 — historical-with-template-count convention 미답습, Amendment 9 CFP-963 disjoint). pre-edit raw count 47 (46 active + 1 exempt template) → post-edit raw count 51 (50 active + 1 exempt template). issue_origin: orchestrator_authored_followup (ADR-082 Amendment 2 §2.1 carrier — CFP-1000 retro PMOAgent-authored Tier-B carry-forward, §3.17 4-step procedure 적용). pivot finding (write-time): 1 entry shifted between morning verification (Issue body 35+6=41) ↔ pre-spawn verify-before-trust (36+5=41 raw drift, 41 total invariant). 5 of 5 gh→registry missing 모두 legitimate operational provenance (3 with backing CFP/workflow + 2 with 11-12+ PR bypass-counter audit-trail). Tier-B Wave 2 (registry→gh sync verify) + Wave 3 (sync drift lint) = 별 CFP carrier 분리 (ADR-064 §결정 1 CFP scope unitary 정합). prior art Amendment 10 (CFP-1000) 직전 carrier 정합."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 4 신규 family member + 1 rename = §결정 6.A per-entry namespace 의무의 영구 확장 (Tier-B bidirectional drift sweep Wave 1 영역, gh→registry missing direction first closure). ratchet-UP 강화 방향 (active concrete grep count 46 → 50 정합 raw active concrete, registry-gh 4-way sync gap 부분 closure, 약화 영역 0건 ADR-058 §결정 5 정합)."
  - by: "CFP-1025"
    date: "2026-05-19"
    scope: "Amendment 12 — Tier-B Wave 2 registry→gh backfill + CFP-1006 Wave-1 auto-resolve FALSIFICATION record + bootstrap-labels token-permission(CODEFORGE_CROSS_REPO_PAT label-write gap ROOT) / scripts/bootstrap-labels.sh:53 2>/dev/null error-mask(META-ROOT) 2-layer root cause codify + Wave 2 closure + Wave 3 sync-drift-lint OOS (별 CFP) + PAT user-domain residual flag (ADR-066). CFP-1006 Amendment 11 scope 의 '35 of 36 registry→gh missing 자동 해소 expected via bootstrap-labels.yml workflow PR open auto-fire' assumption 은 실측 거짓 입증 (run 26080174058 success but gh hotfix-bypass count 15 unchanged, NO PyYAML SKIP, 115 blanket label-write failure incl base labels — Orchestrator pre-spawn PyYAML hypothesis REFUTED, runner ubuntu-24.04 PyYAML present). 진짜 root cause = (ROOT) workflow token = secrets.CODEFORGE_CROSS_REPO_PAT || secrets.GITHUB_TOKEN → PAT in effect (secret set 2026-05-14) but ADR-066/CFP-450 provisioned scope (phase-gate-mergeable + rate-limit-fallback-kpi) 가 label-write (Issues:write on mclayer/plugin-codeforge) 미포함 / (META-ROOT) scripts/bootstrap-labels.sh:53-55 create_label() 의 2>/dev/null 가 실제 HTTP 403/404 삼킴 → generic 메시지 + 오인성 'Bootstrap completed successfully' (CFP-1006 mis-diagnosis 직접 원인). 본 Amendment 12 = root-cause/process codification only (신규 family member append 0, 신규 ordinal 0, registry §3 content 변경 0건 v2.39 retain). Phase 2 src: scripts/bootstrap-labels.sh:53-70 error-unmask (captured stderr verbatim echo, --dry-run path 무영향 LABEL_COUNT parity 108==108 보존) + .github/workflows/bootstrap-labels.yml + templates/ byte-identical false-success visibility step (fail_count >= 10 시 ::warning::, continue-on-error/warning tier 보존, ADR-005 diff empty). 35 registry→gh missing = owner-context one-time idempotent backfill (NOT CI re-trigger — token-blocked, 재-fire 는 동일 실패 = falsified Wave-defer 반복 차단). residual: CODEFORGE_CROSS_REPO_PAT Issues:write 미획득 시 CI self-heal 불가 = user secret-domain accepted (ADR-066, AC-5). issue_origin: orchestrator_authored_followup (ADR-082 Amendment 2 §2.1 — CFP-1006 retro PMOAgent-authored Tier-B carry-forward, §3.17 4-step procedure 적용). src 변경 동반으로 doc-only fast-path (ADR-054) 미적용 = full-lane. memory feedback_wave_defer_empirical_verify (deferred Wave auto-resolve assumption empirical-verify 의무) + feedback_architect_script_behavior_claim_verify (script-behavior claim 실측 의무) lineage 교훈. prior art Amendment 11 (CFP-1006) 직전 carrier 정합."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). ratchet 강화 방향 (Wave-defer empirical-verify discipline + error-mask remediation 추가, forbid scope 축소 0, 약화 영역 0건). ADR-058 §결정 5 + ADR-064 §self-application top-down ratchet 정합."
  - by: "CFP-1306"
    date: "2026-05-25"
    scope: "Amendment 14 — §결정 6.A.7 신설 (92번째 hotfix-bypass:* family member append — raw active concrete grep count post-append 91 + 1 = 92) `hotfix-bypass:parallel-anchors-checked-presence` per-entry namespace. review-verdict-v4 findings[].parallel_anchors_checked[] field presence-grep heuristic mechanical lint (CFP-1306 / ADR-060 Amendment 15 §결정 29 / ADR-068 I-2 cross-module propagation completeness Wave 3 enforcement layer) 의 bypass channel codify. ADR-108 §결정 3 META self-app 9th applied case (raw active concrete grep count post-append 91 + 1 = 92 정합). ADR-082 §결정 9 verify-at-write-time — rebase 후 base v2.66 / 91 raw active concrete grep (CFP-1367 90+91번째 먼저 머지됨). label-registry-v2 v2.66 → v2.67 MINOR bump 동반 (kind:registry sibling sync 면제 ADR-010 §결정 2 + ADR-008 §결정 3 row append). MANIFEST.yaml row '2.66' → '2.67' ratchet 동반. plugin.json bump 0 = marketplace_sync_declared: false (lint+workflow 신설 = governance behavior 변경이나 plugin.json mirrored field 무변경, ADR-063 atomic invariant 발효 조건 미충족). **late-comer rebase invariant 완료 (ADR-050 §결정 1)**: CFP-1367 PR #1517 먼저 머지됨 (90번째+91번째) → CFP-1306 = 92번째 (v2.67) rebase 완료."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 1 신규 family member + §결정 6.A.7 신설 = §결정 6.A per-entry namespace 의무의 영구 확장 (parallel_anchors_checked field presence-grep enforcement layer bypass channel). forbid scope 축소 0건. ratchet-UP 강화 방향 (active concrete grep count 91 → 92, 약화 영역 0건). ADR-058 §결정 5 + ADR-064 §self-application top-down ratchet 정합."
  - by: "CFP-1510"
    date: "2026-05-25"
    scope: "Amendment 13 — §결정 6.A.6 신설 (macro label batch attachment audit-trailed exception channel) + §결정 6.A per-entry namespace 의 89번째 (raw active concrete grep count post-append) family member `hotfix-bypass:pre-existing-main-drift-bundle` macro label 추가. CFP-1389 lineage 마지막 follow-up (FU-Wave3-C). pre-existing-main-drift super-class 8 sentinel labels closed-set (bootstrap-labels / actionlint / claude-md-amendment-ref-drift / markdown-internal-links / inter-plugin-contracts-parity / fix-event-depth-scope / sibling-pr-author-check / wording-dictionary) 의 unified channel codify. Macro label semantics: single `hotfix-bypass:pre-existing-main-drift-bundle` attach → 8 underlying hotfix-bypass labels auto-fan-out attach via `macro-label-expander.yml` workflow (Wave 1 declarative stub `if: false` disabled, Wave 2 hydrate carrier 별 sub-CFP — pull_request.labeled / issues.labeled event triggers wire). Efficiency target: 64 manual attachments (8 PR × 8 label) → 8x reduction (1 macro attach = 8 label auto-fan-out + single audit comment 1개로 8 underlying labels rationale 통합 가능). §결정 6.A.6 audit pattern: single audit comment block (예: `[bypass-audit] pre-existing-main-drift-bundle: <rationale>`) 가 8 underlying labels 모두에 대해 audit-trail rationale 충족. 기존 single audit lint `scripts/check-bypass-audit-comment.sh` reuse (신규 lint 도입 0건, CFP-389 prior art). Audit invariant 보존: macro = batch-attach mechanism only / 8 underlying labels 의 individual lint enforce 영역 무변경. label-registry-v2 v2.64 → v2.65 MINOR bump 동반 (kind:registry sibling sync 면제 ADR-010 §결정 2 + ADR-008 §결정 3 row append). MANIFEST.yaml row '2.64' → '2.65' ratchet 동반. plugin.json bump 0 = marketplace_sync_declared: false (lint+workflow 신설 = governance behavior 변경이나 plugin.json mirrored field 무변경 — kind:registry sibling sync 면제 영역, ADR-063 atomic invariant 발효 조건 미충족). Wave 1 산출: (a) label-registry-v2 §3 macro label entry append (b) `templates/github-workflows/macro-label-expander.yml` Wave 1 declarative stub (`if: false` disabled, Wave 2 hydrate carrier 별 sub-CFP) (c) `.github/workflows/macro-label-expander.yml` self-app byte-identical (ADR-005 invariant). Wave 2 carrier 영역 (별 sub-CFP): workflow `if: false` 제거 + pull_request.labeled / issues.labeled event trigger wire + 8 underlying labels mechanical attach script + audit comment fan-out logic + bats fixture pair. raw count convention 답습 (CFP-1000 Amendment 10 + CFP-1346 ADR-108 forcing function parity mandate META self-application — raw active concrete grep count post-append 88 + 1 = 89). ADR-108 §결정 3 META self-app 7th applied case. ADR-082 §결정 9 verify-at-write-time (worktree base v2.64 / 88 raw active concrete grep) verified — main repo divergent state ignored (worktree-base SSOT, ADR-070 verify-before-trust). prior art Amendment 12 (CFP-1025) 직전 carrier 정합."
    sunset_justification: "N/A — is_transitional: false (permanent governance policy). 1 신규 family member + §결정 6.A.6 신설 = §결정 6.A per-entry namespace 의무의 영구 확장 (macro label batch attachment audit-trailed exception channel — bypass-as-norm-mutation 누적 monitoring 의 efficiency-preserving 강화 방향, 64 manual attach overhead → 1 macro attach reduction). forbid scope 축소 0건 (8 underlying labels 의 individual lint enforce 영역 무변경, macro = batch-attach mechanism only — audit trail invariant 보존). ratchet-UP 강화 방향 (active concrete grep count 88 → 89 정합 raw active concrete + audit pattern 확장, 약화 영역 0건). ADR-058 §결정 5 + ADR-064 §self-application top-down ratchet 정합."
related_files:
  - CLAUDE.md
  - docs/consumer-guide.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/adr/ADR-040-worktree-convention.md
  - docs/adr/ADR-059-debate-protocol-v1.md
  - docs/adr/ADR-060-evidence-enforceable-promotion-framework.md
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md
  - docs/inter-plugin-contracts/label-registry-v2.md
  - templates/branch-protection-manifest.yaml
  - templates/github-workflows/branch-protection-drift-check.yml
  - templates/github-workflows/debate-convergence-quality.yml
  - templates/github-workflows/bypass-label-counter.yml
  - templates/github-workflows/per-plugin-cumulative-counter.yml
  - templates/github-workflows/bypass-justification-marker.yml
  - templates/github-workflows/cross-repo-bypass-counter.yml
  - scripts/check-bypass-label-counter.py
  - scripts/check-bypass-label-counter.sh
  - scripts/check-per-plugin-cumulative-counter.py
  - scripts/check-per-plugin-cumulative-counter.sh
  - scripts/check-bypass-justification-marker.py
  - scripts/check-bypass-justification-marker.sh
  - scripts/check-cross-repo-bypass-counter.py
  - scripts/check-cross-repo-bypass-counter.sh
  - templates/github-workflows/macro-label-expander.yml
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.A 의무 — 본 ADR-024 Amendment 4 (CFP-481, 2026-05-12)
  # 가 ADR-040 Amendment 3 발효 (CFP-426 Phase 1 PR merge) 이후 작성된 normative
  # ADR amendment 이므로 §결정 7.C retroactive 면제 외 — Amendment 4 부터 mandate 적용.
  # 기존 ADR-024 Amendment 1·2·3 = retroactive 면제 (§결정 7.C 정합).
  - action: auto-phase-label
    status: deferred-followup     # registry yaml row append = CFP-481 Phase 2 PR scope
    target_section: §결정 6.A.1   # branch → phase mapping 표 SSOT (1순위 inference 로직)
  # Amendment 6 (CFP-825, 2026-05-17) — 본 Amendment 의 mechanical enforcement self-application
  - action: bypass-label-counter
    status: deferred-followup     # registry yaml row append = CFP-825 Phase 2 PR scope
    target_section: §결정 6.A.2   # per-entry namespace 누적 사용 카운터 lint ratchet 룰 (3-tuple: threshold / dedup / window)
  # Amendment 8 (CFP-845, 2026-05-17) — bypass-as-norm-mutation 후속 escalation 3 sub-decision self-application
  - action: per-plugin-cumulative-counter
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint+workflow wire = Phase 2 PR scope
    target_section: §결정 6.A.3   # per-plugin 전체 누적 카운터 ratchet (단일 plugin scope 분산 bypass 탐지)
  - action: bypass-justification-marker
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint+workflow wire = Phase 2 PR scope
    target_section: §결정 6.A.4   # PR comment marker grep-presence lint (false-positive risk 명시, reviewer responsibility)
  - action: cross-repo-bypass-counter
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint+workflow wire = Phase 2 PR scope
    target_section: §결정 6.A.5   # cross-repo extension (wrapper + internal-docs + marketplace 3-repo signature)
  # Amendment 9 (CFP-963, 2026-05-19) — 44번째 family member `hotfix-bypass:codex-sandbox-substitution`
  # ADR-060 Amendment 14 §결정 28 carrier + ADR-081 Amendment 4 §결정 D1.D body 확장 mechanical
  # enforcement layer (warning-tier evidence-checks-registry entry `codex-network-scope-presence` bypass channel).
  # historical-with-template-count convention citation (active concrete 42 + CFP-825 template 43 = 44 new).
  - action: codex-network-scope-presence
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint script + workflow + bats fixture pair wire = Phase 2 PR scope
    target_section: §결정 6.A     # 44th family member append — codex worker collaboration mechanical layer bypass channel 영역 첫 family member
  # Amendment 10 (CFP-1000, 2026-05-19 KST) — 45번째 (raw) family member `hotfix-bypass:prod-cutover-deputy-evidence`
  # registry-side late codify carrier — gh-side 는 CFP-954 PR-time 이미 등록 (1 hit verified). 신규 lint 도입 0건 —
  # 본 entry 의 mechanical enforcement = (가) `bootstrap-labels.yml` workflow auto-run PR open 시 자동 sync gap closure
  # (CFP-598 dynamic registry-driven pattern: scripts/parse-hotfix-bypass-labels.py 가 §3 yaml read auto-emit) +
  # (나) existing audit-comment lint (`scripts/check-bypass-audit-comment.sh`, CFP-389 prior art reuse — 모든 family entry detect).
  # ADR-72 §결정 5 의 2 evidence-checks-registry entry (production-cutover-deputy-spawn-evidence +
  # epic-cutover-gate-evidence-quad-check) bypass channel — registry §3 yaml append 만으로 자동 발효.
  - action: bootstrap-labels
    status: existing-reuse        # 신규 lint 도입 0건 — registry §3 append 만으로 `bootstrap-labels.yml` workflow auto-run (CFP-662 baseline) 가 gh-side sync gap 자동 closure
    target_section: §결정 6.A     # 46th family member append — production-cutover evidence 영역 first registry-side codify
  - action: check-bypass-audit-comment
    status: existing-reuse        # 신규 lint 도입 0건 — existing single audit-comment lint (CFP-389 prior art) 가 모든 family entry detect, 본 entry 부착 PR 도 자동 cover
    target_section: §결정 6.A     # audit comment 의무 검증 + audit log 집계 (Amendment 3 §결정 6.A audit-trailed exception channel)
  # Amendment 13 (CFP-1510, 2026-05-25) — 89번째 (raw active concrete grep count post-append) family member
  # `hotfix-bypass:pre-existing-main-drift-bundle` macro label + §결정 6.A.6 신설 (macro label batch attachment audit-trailed exception channel)
  # Wave 1 declarative — `templates/github-workflows/macro-label-expander.yml` Wave 1 stub (`if: false` disabled)
  # Wave 2 hydrate carrier 별 sub-CFP (pull_request.labeled / issues.labeled event triggers wire + 8 underlying labels mechanical attach + audit comment fan-out logic)
  # CFP-1389 lineage 마지막 follow-up FU-Wave3-C — pre-existing-main-drift super-class 8 sentinel closed-set unified channel
  # Closed-set 8 underlying labels: bootstrap-labels / actionlint / claude-md-amendment-ref-drift / markdown-internal-links / inter-plugin-contracts-parity / fix-event-depth-scope / sibling-pr-author-check / wording-dictionary
  - action: macro-label-expander
    status: deferred-followup     # registry §3 append + workflow stub = Phase 1 PR; actual workflow `if:false` 제거 + 8 underlying labels mechanical fan-out wire = Wave 2 별 sub-CFP scope
    target_section: §결정 6.A.6   # 89번째 family member append — macro label batch attachment audit-trailed exception channel 영역 첫 family member (single attach = 8 label auto-fan-out + single audit comment 1개 통합)
  # Amendment 14 (CFP-1306, 2026-05-25) — 92번째 (raw active concrete grep count post-append, v2.67) family member
  # `hotfix-bypass:parallel-anchors-checked-presence` per-entry namespace
  # review-verdict-v4 findings[].parallel_anchors_checked[] field presence-grep heuristic mechanical lint bypass channel
  # CFP-1306 / ADR-060 Amendment 15 §결정 29 / ADR-068 I-2 cross-module propagation completeness Wave 3 enforcement layer
  # late-comer rebase invariant: CFP-1367 PR #1517 먼저 머지됨 (90+91번째) → CFP-1306 = 92번째 v2.67 rebase 완료
  - action: parallel-anchors-checked-presence
    status: warning               # Phase 1+2 동시 wire (CFP-1334 deferred-followup → warning 직접 전환 precedent)
    target_section: §결정 6.A.7   # 92번째 family member append — review-verdict-v4 parallel anchor parity enforcement bypass channel
---

# ADR-024: Story-scoped branch policy — main 직접 수정 금지 + Phase 2 enforcement deferred

## 상태

Accepted (2026-05-03 — CFP-66 carrier)

## 컨텍스트

User directive 2026-05-03 (CFP-65 작업 중간):

> "codeforge로 작업하는 모든 변경사항은 story 단위 이하에서 브랜치를 분리하여 작업 수행해 main 브랜치에 머지할 수 있도록 한다 main브랜치에 직접 수정하는 것을 금지한다. 이유는 스토리 단위 별로 병렬 수정이 가능하도록 하기 위함이다."

현재 practice (2026-05-02 ~ 03 dogfood 운영):
- CFP-63 / CFP-64 / CFP-65 모두 feature branch + PR 경유 — 행동상 직접 push 사례 없음
- main branch protection 설정: `enforce_admins: false`, `restrictions: null` — admin (mccho8865) 가 main 직접 push 가능, 단 운영 중 직접 push 미사용

Gap: 행동상 충족 / policy enforcement 미완. solo-dev 가 우연히 main commit 하거나 emergency hotfix 명목으로 직접 push 시 governance 부재.

추가 제약 (Sonnet decider CFP-66-001 검토):
- 6+ pre-existing CI fail 존재 (inter-plugin-drift / workflow yaml regex 등) — `enforce_admins:true` 즉시 적용 시 ANY PR merge 차단 (deadlock).
- consumer 측 branch policy 권장 (consumer-guide.md §2e) 와 wrapper repo 자체 policy 분리 필요 — 두 scope 가 혼재 시 governance 모호.

## 결정

### 결정 1: Story-scoped feature branch + PR 경유 의무

모든 wrapper 변경 (codeforge family 자체 dogfood 작업 포함) = Story-scoped feature branch + PR 경유. main 직접 push 금지 — 정책 + 물리 강제.

권장 branch naming (강제는 Phase 2):
- `cfp-NNN[-<slug>]` (가장 일반적)
- `cfp-NNN-<phase>` (multi-phase Story 의 Phase 분리 시 — 예: `cfp-65-story-flow-phase1`)
- 동등 naming 도 허용 — Phase 2 에서 enforcement (Option G) 결정.

### 결정 2: main branch protection `restrictions:{users:[],teams:[],apps:[]}` 강제 (Phase 1)

`gh api -X PUT repos/mclayer/plugin-codeforge/branches/main/protection` 의 `restrictions` field 를 `null` → `{users:[],teams:[],apps:[]}` 로 변경. 결과: main 에 직접 push 권한이 누구에게도 없음 — PR 경유 merge 만 허용.

### 결정 3: `enforce_admins: false` Phase 1 유지 (deadlock 회피)

`enforce_admins: true` 적용 시 admin 도 required status check fail bypass 불가. 현재 6+ pre-existing CI fail 환경에서 ANY PR merge 차단 = 즉시 deadlock. Phase 2 (CI green 100% 달성 후 별도 CFP) 까지 `enforce_admins: false` 유지 — admin (mccho8865) 가 PR-based admin merge 로 deferred CI fail bypass 가능.

### 결정 4: Phase 2 enforcement 후속 CFP — CI green 전제

Phase 2 transition 조건 = 6+ pre-existing CI fail 전부 해소. 별도 CFP 로 다음 항목 평가:
- `enforce_admins: true` 전환
- GitHub Rulesets (legacy branch protection 대체)
- Story branch naming enforcement (e.g. `^cfp-\d+(-.*)?$` regex)
- PR source-branch non-main enforcement (자동화 추가)

Phase 2 도입 순서: Rulesets 검증 → naming rule 정착 → enforcement 자동화 → enforce_admins:true 최종 전환.

### 결정 5: Consumer policy 분리 + cross-reference

Wrapper repo (mclayer/plugin-codeforge) governance vs consumer-guide.md §2e (다운스트림 consumer 권장 settings) 분리. consumer 는 자기 repo 의 branch protection 을 자기 환경 (solo-dev / 1-2인 팀 / 다인 contributor) 에 맞게 설정 — wrapper governance 와 별도.

CLAUDE.md 에 본 ADR-024 cross-ref 1줄 + consumer-guide.md §2e cross-ref. 두 SSOT 의 분리 명시.

### 결정 6: Emergency hotfix 도 PR 경유 의무 (no exception)

운영 장애 hotfix 도 본 정책 예외 없음. hotfix branch (e.g. `hotfix-<id>`) + PR 경유 — admin merge via PR API 로 신속 merge 가능. 직접 push 우회 금지.

## 결과

- 직접 push 물리 차단 → governance 강화, solo-dev 우연 commit 차단
- PR-based admin merge 패턴 무영향 (`enforce_admins:false` 유지로 deferred CI fail bypass 가능)
- 병렬 modification 지원: 여러 Story-scoped branch 동시 작업 + 독립 PR 가능 (개별 PR 의 CI 검증 / merge 순서 자유)
- ADR governance trail — Phase 2 transition 의 명확한 trigger / 조건 추적 가능
- consumer 측은 자기 환경에 맞는 별도 protection — wrapper 정책 강요 X

## 해소 기준

N/A — permanent policy. 본 ADR 은 `is_transitional: false` (permanent governance carrier — Story-scoped branch policy 자체 가 codeforge 의 영구 결제 룰). ADR-058 §결정 7 보안 ADR default presumption = `false` 정합 (security & governance carrier).

## 관련 파일

- `CLAUDE.md` — Story 작성 의무 섹션에 ADR-024 cross-ref 추가
- `docs/consumer-guide.md` — §2e 와 cross-ref 분리 명시
- GitHub branch protection (api operation, file 외부) — `restrictions:{users:[],teams:[],apps:[]}` (Phase 1) + **`enforce_admins: true` (Phase 2 / CFP-70)** 적용
- ADR-013 (dogfood-out policy) — Story 작성 의무 root principle
- ADR-022 (Sonnet Decider) — 본 ADR 의 결정 protocol
- ADR-058 (sunset criteria mandate) — `is_transitional: false` classification 적용
- ADR-060 (evidence-enforceable framework) — Amendment 3 의 `hotfix-bypass:*` label family carrier

## Phase 2 partial impl (CFP-70 — 2026-05-03)

CFP-70 (Sonnet decider CFP-70-001 pick=A + CFP-70-002 sub-pick=B minimal) 가 Phase 2 의 부분 적용:

- ✅ **`enforce_admins: true`** — 적용. admin (mccho8865) 도 4 required check (phase-gate-mergeable / doc frontmatter / doc section / invariant-check) 모두 통과 의무.
- ⏸️ **GitHub Rulesets** — solo-dev 가정 하 ROI 낮음. defer.
- ⏸️ **Branch naming auto enforcement** — 정책 도덕적 의무 (본 ADR §결정 1) 충분. defer.
- ⏸️ **PR source-branch non-main enforcement** — `restrictions:{users:[],teams:[],apps:[]}` 가 이미 covered. 추가 enforcement 불필요.

Phase 2 sequence 해석 ("Rulesets 검증 → naming → enforcement 자동화 → enforce_admins:true"): 결정 4 의 "검증" = "evaluate + skip-if-not-needed". Solo-dev evaluation 결과 = skip — sequence 위반 아님.

**가정 변경 시 재검토 의무**: contributor 추가 (외부 PR 가능성 발생) 시점에 Rulesets shadow + branch naming auto enforcement 별도 CFP 추진 의무. 본 ADR Phase 2 partial 명시 = 재검토 trigger.

Rollback runbook (emergency only):

```bash
# enforce_admins:false 재전환 (admin bypass 복원)
gh api -X PUT repos/mclayer/plugin-codeforge/branches/main/protection \
  --input <(현재 protection JSON 단 enforce_admins:false)
```

bypass 가능 admin = mccho8865 (mclayer org owner).

## solo-dev governance gap 영구 해결 (CFP-72 — 2026-05-04)

CFP-71 (PR #149) merge 시 발견 — solo-dev 환경 + `enforce_admins:true` + `require_code_owner_reviews:true` + `required_approving_review_count:1` = **본인 PR 본인 approve 불가** (GitHub policy: `Can not approve your own pull request`). CFP-66/70 검토 시 누락된 edge case. 매 PR 마다 `enforce_admins:false` + review requirement off 임시 bypass + 즉시 복원 = 1-2분 governance gap 누적.

CFP-72 (CFP-72-001 옵션 A 사용자 결단) 가 영구 해결:

- ✅ `required_approving_review_count: 0` — review 강제 해제
- ✅ `require_code_owner_reviews: false` — CODEOWNERS 강제 해제
- ✅ `enforce_admins: true` — 유지 (admin 도 4 required check 통과 의무)
- ✅ `restrictions: {users:[], teams:[], apps:[]}` — 유지 (direct push 차단)
- ✅ 4 required status check — 유지 (phase-gate-mergeable / doc frontmatter / doc section / invariant-check)

CODEOWNERS file 자체는 **유지** — auto review request 발생 = 도덕적 governance (PR open 시 architects team 자동 통보, merge 강제 요건 없음).

**가정 변경 시 재검토 의무**: contributor 추가 (외부 PR 가능성 발생) 시점에 `require_code_owner_reviews:true` + `required_approving_review_count:1` 복원 의무. 본 § = 재검토 trigger.

CFP-72 본 PR 자체가 governance gap **마지막** 임시 bypass 사용 사례 — merge 후 영구 해결 적용 → 재발 0.

## Amendment 1 — Hierarchical branch convention (CFP-134, 2026-05-08)

### 컨텍스트

Agent teams 적극 도입 (CFP-137) + worktree infrastructure (CFP-136) 도입 시 1 Story = N teammate 가 자기 sub-branch 위에서 병렬 작업. flat naming (`cfp-NNN[-slug]`) 으로는 lane / sub-task 분기 표현 불가. 사용자 directive (CFP-134 Epic, 2026-05-08): "Epic > Story > sub... 이렇게 있는 경우 branch 를 하위 생성하여 agent 내에서 적극적으로 병렬 작업".

### Amendment

기존 §결정 1 의 branch naming 확장:

```yaml
naming_convention:
  story_root: cfp-NNN[-slug]              # 기존 — 변경 없음
  lane: cfp-NNN/<lane-name>               # 신규 — lane 단위 sub-branch
  sub_task: cfp-NNN/<lane-name>/<sub-name>  # 신규 — deputy / role:dev 등 sub-task
  fix_iter: cfp-NNN/fix-iter-<N>          # 신규 — FIX iteration 임시 branch
  retro: cfp-NNN/retro                    # 신규 — retro 작업 임시 branch

example_paths:
  - cfp-135                               # Story root
  - cfp-135-foundation                    # Story root with slug
  - cfp-NNN/design                        # design lane sub-branch
  - cfp-NNN/design/chief                  # design lane chief author sub-branch
  - cfp-NNN/design/mapper                 # design lane CodebaseMapper deputy sub-branch
  - cfp-NNN/code-review/codex-worker      # code review lane Codex worker sub-branch
```

### 적용 규칙

- 모든 sub-branch 는 자기 worktree (CFP-136 infrastructure) 에서 작업 — file 충돌 0
- Lane 완료 시 sub-branch → lane branch sequential merge → Story root branch merge → main PR
- GitOpsAgent (CFP-139) 가 worktree lifecycle + sequential merge 담당
- Phase 2 enforcement (branch naming auto enforcement) 는 별도 CFP — solo-dev 환경 deferred (현재 ADR-024 결정 4)

### Compatibility

기존 flat naming `cfp-NNN[-slug]` 그대로 유효 — story root branch 로 사용. 신규 hierarchical 은 sub-branch 영역 추가만.

### Related

- CFP-134 Epic spec: `<internal-docs>/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md` §3.4
- CFP-136 (worktree infrastructure) — 본 amendment 의 prerequisite
- CFP-137 (agent teams 적극 도입) — 본 amendment 의 use case
- CFP-139 (GitOpsAgent) — 본 amendment 의 enforcement

## Amendment 2 — required_status_checks.contexts drift invariant (CFP-280, 2026-05-11)

### 컨텍스트

CFP-136 (worktree infrastructure) 도입 후 `gh api` 로 branch protection 을 직접 조회했을 때, `required_status_checks.contexts` 에 3개 stale context 가 잔존함을 확인:

| stale context | 원인 |
|---|---|
| `doc frontmatter schema (CFP–28 — strict)` | 하이픈 문자 em-dash(`–`, U+2013) vs workflow job name의 hyphen(`-`, U+002D) 불일치 |
| `doc section schema (CFP–28 — strict)` | 동일 em-dash 문자 불일치 |
| `doc-locations-check / validate` | CFP-276 이후 해당 workflow job 삭제됨 — orphan |

실제 workflow job name (2개) 은 `doc frontmatter schema (CFP-28 — strict)` / `doc section schema (CFP-28 — strict)` (ASCII hyphen) 이므로, branch protection 에 등록된 em-dash 변형은 영구 mismatch → 해당 check 가 GitHub 에서 "expected" 상태로 표시되지 않아 PR merge 가 잠재적으로 차단될 수 있음.

CFP-136 align fix 시 3개 stale 제거 + 올바른 2개 추가 완료. 그러나 이 drift 재발 방지를 위한 **자동화 invariant 부재** — 본 Amendment 2 가 gap 해소.

현재 확정 4 required context:

```
phase-gate-mergeable        # phase-gate-mergeable.yml checks.create (동적 생성)
invariant-check             # invariant-check.yml job id (explicit name: 없음)
doc frontmatter schema (CFP-28 — strict)  # check-doc-frontmatter.yml job name
doc section schema (CFP-28 — strict)      # check-doc-section-schema.yml job name
```

### Amendment

#### §결정 A: `templates/branch-protection-manifest.yaml` SSOT 신설

branch protection 에 등록 필요한 `required_status_checks.contexts` 를 SSOT 파일로 관리. consumer 가 overlay 로 자기 context 추가 가능 (확장 only — 기본 4개 삭제 불허).

```yaml
# templates/branch-protection-manifest.yaml
# consumer overlay: .claude/_overlay/branch-protection-manifest.yaml 로 확장 가능
required_status_checks:
  contexts:
    - name: "phase-gate-mergeable"
      type: dynamic          # checks.create API (phase-gate-mergeable.yml)
      source_workflow: templates/github-workflows/phase-gate-mergeable.yml
    - name: "invariant-check"
      type: workflow-job-id  # job id (explicit name: 없음)
      source_workflow: templates/github-workflows/invariant-check.yml
    - name: "doc frontmatter schema (CFP-28 — strict)"
      type: workflow-job-name
      source_workflow: templates/github-workflows/check-doc-frontmatter.yml
    - name: "doc section schema (CFP-28 — strict)"
      type: workflow-job-name
      source_workflow: templates/github-workflows/check-doc-section-schema.yml
```

#### §결정 B: `templates/github-workflows/branch-protection-drift-check.yml` 신설

자동화 drift 감지. 트리거: `.github/workflows/**` 또는 `templates/branch-protection-manifest.yaml` 변경 push to main + 주 1회 schedule (`cron: '0 9 * * 1'`) + `workflow_dispatch`.

동작:
1. `gh api` 로 `repos/{owner}/{repo}/branches/main/protection/required_status_checks` 조회 → 실제 contexts 목록 추출 + sort
2. manifest yaml 에서 기대 contexts 추출 + sort
3. `comm -23` (stale: 실제에 있으나 manifest에 없는 것) + `comm -13` (missing: manifest에 있으나 실제에 없는 것) 비교
4. stale 또는 missing 존재 시 → `exit 1` (CI fail)

#### §결정 C: drift 발견 시 수정 절차 (운영 규칙)

1. manifest yaml 에 기대 contexts 반영 (정책 반영)
2. `gh api -X PUT repos/.../branches/main/protection` 로 실제 branch protection 동기
3. drift-check workflow 재실행 PASS 확인
4. 두 변경이 동일 PR 에 포함 의무 (SSOT 와 실제 동기 원자적 보장)

### Compatibility

- 기존 4 required check 변경 없음 — 단 SSOT 위치가 implicit → `templates/branch-protection-manifest.yaml` explicit 으로 전환
- 기존 `required-workflow-drift-check.yml` (enterprise required workflow drift) · `rulesets-drift-check.yml` (GitHub Rulesets drift) 와 별도 목적 — 중복 없음
- consumer overlay 확장 방식 → consumer 는 자기 context 추가만 가능 (core 4개 삭제 불허)

### Related

- CFP-280 carrier story
- `templates/branch-protection-manifest.yaml` — §결정 A SSOT
- `templates/github-workflows/branch-protection-drift-check.yml` — §결정 B 자동화
- CFP-136 (worktree infrastructure) — 3 stale context 최초 발견 trigger

## Amendment 3 — Audit-trailed exception channel via `hotfix-bypass:*` label family (CFP-389, 2026-05-11)

### 컨텍스트

ADR-024 §결정 6 ("emergency hotfix 도 PR 경유 의무, no exception") + `enforce_admins: true` (CFP-70, Phase 2 partial) + `restrictions: {users:[], teams:[], apps:[]}` (CFP-66) 조합 결과: enforce mode 진입한 required check 가 운영 장애 hotfix PR 을 차단 시 admin override 우회 채널 부재 → deadlock 위험.

CFP-389 (ADR-060 carrier — evidence-enforceable promotion framework) 가 첫 evidence check (`scripts/check-adr-sunset-criteria.sh`) 도입 시 동일 deadlock pattern 재발 차단을 위해 audit-trailed exception channel 정식 도입 결정 (사용자 ESCALATE Option A).

### Amendment

본 Amendment 3 은 §결정 6 보완 — emergency hotfix PR 경유 의무 유지하면서 evidence-enforceable check 한정 audit-trailed bypass channel 도입:

#### §결정 6.A: `hotfix-bypass:*` label family = audit-trailed exception channel

evidence-enforceable framework (ADR-060) 의 개별 evidence check 가 enforce mode 진입한 후, 운영 장애 hotfix 가 정책 위반을 강제하는 경우 → `hotfix-bypass:<entry-name>` label 부착으로 해당 check skip + audit trail 자동 발의:

- **label naming**: `hotfix-bypass:<entry-name>` family. 첫 entry = `hotfix-bypass:adr-sunset` (ADR-060 §결정 7).
- **권한자**: repo admin only. solo-dev 환경 = 사용자 본인 (mccho8865). contributor 추가 시 재논의 (별도 carrier).
- **scope 통제**: per-entry namespace 분리 (registry entry `bypass_label` 필드 per-entry). 단일 global bypass label 도입 금지 (ADR-060 §대안 E 거부 사유 정합).
- **enforce mode 진입 전 (warning mode)**: bypass label 부착 시 lint workflow conditional skip — required check 부착 아님 (continue-on-error). 본 Amendment 의 protection 강화 효과는 enforce mode 진입 후 발현.
- **확장 사례 (CFP-426 / Epic CFP-425)**: 4 신규 label entry 동시 도입 — `hotfix-bypass:worktree-session-start-wire` / `hotfix-bypass:worktree-pre-checkout` / `hotfix-bypass:worktree-pre-commit-main-block` / `hotfix-bypass:worktree-spawn-evidence-cwd`. 모두 §결정 6.A per-entry namespace 정합 + ADR-040 Amendment 3 §결정 7.D self-application 의 4 evidence check entry 와 1:1 mapping. audit lint = `scripts/check-bypass-audit-comment.sh` (CFP-389 prior art 단일 reuse — `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect).

#### §결정 6.B: PR 경유 의무 유지 (no push/merge path override)

bypass label = lint skip only. 다음 항목 미변경 (§결정 6 + CFP-66 + CFP-70 정합):

- main 직접 push 금지 (restrictions:{users:[],teams:[],apps:[]} 유지)
- 모든 변경 = feature branch + PR 경유 의무
- enforce_admins:true (admin 도 4 required check 통과 의무 — bypass label 외 check 들에는 영향 X)

bypass label 은 evidence-enforceable check 한 가지의 skip 만 제공 — branch protection의 4 core required check (phase-gate-mergeable / doc frontmatter / doc section / invariant-check) 는 우회 불가.

#### §결정 6.C: Audit trail 3중 안전망

bypass label 적용 시 다음 3중 안전망 자동 활성:

1. **Audit comment 자동 발의** (workflow level): GitHub Actions bot 이 PR comment 1개 append (schema: ADR-060 §결정 8).
   ```
   [hotfix-bypass-audit] PR=<number> label_applied_by=<user> reason=<bypass_reason_textbox> ADR_files=<paths> timestamp=<ISO8601>
   ```
2. **Audit assertion lint**: `scripts/check-bypass-audit-comment.sh` 가 audit comment 1개 이상 존재 검증 → 부재 시 PR block.
3. **Audit log 집계**: bypass label 적용 PR list quarterly merge 시 `docs/audit/hotfix-bypass-log.md` 자동 append (별도 carrier scope — CFP-390 인벤토리 backfill 또는 신규 carrier).

#### §결정 6.D: Re-entry 안전망 (bypass PR 자체 정책 위반)

bypass label PR 안 변경 자체가 정책 위반 (예: bypass PR 의 변경 ADR 가 sunset criteria 누락) 인 재귀 시나리오 — audit comment 에 `[sunset-criteria-deferred]` 태그 자동 추가 + 후속 보완 의무 자동 Issue 발의 (CFP-390 인벤토리 backfill scope 또는 별도 carrier).

본 재귀 시나리오 미해소 상태로 다음 bypass label 적용 시 escalation 경고 (별도 lint 또는 manual review — 별도 carrier).

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) 전부 유지 — 본 Amendment 3 은 §결정 6 의 호환 channel 확장만.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check 외 lint) 에는 영향 X.
- contributor 추가 시 권한자 재논의 의무 (별도 carrier).

### Related

- ADR-060 (carrier — evidence-enforceable promotion framework SSOT) §결정 7
- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — `bypass_label` per-entry 필드 정의
- `docs/evidence-checks-registry.yaml` — `hotfix-bypass:adr-sunset` 첫 사용 entry
- `scripts/check-bypass-audit-comment.sh` — audit assertion lint
- `templates/github-workflows/adr-sunset-criteria.yml` — bypass label conditional skip workflow
- label-registry-v2 entry 추가 의무 — `hotfix-bypass:adr-sunset` label = label-registry-v2 의 신규 `bypass` tier entry (MINOR bump v2.0 → v2.1 — 별도 follow-up PR 또는 Phase 1 PR 동반, ArchitectAgent 판단)

## Amendment 4 — `hotfix-bypass:auto-phase-label` 7번째 family member + branch → phase mapping 표 SSOT (CFP-481, 2026-05-12)

### 컨텍스트

CFP-455 + CFP-449 retro 식별 sentinel 2 (Codex review verdict EVIDENCE_FRAMEWORK_ENTRY P2) — PR open 후 phase label 누락이 2회 재현되어 mechanical enforcement 도입 timing 도달. CFP-481 (carrier) 가 ADR-060 Amendment 4 (3rd warning-tier entry `auto-phase-label` 등록) 동반으로 본 Amendment 4 도입.

본 Amendment 4 의 두 결정:

1. **`hotfix-bypass:auto-phase-label` 7번째 family member 추가** — Amendment 3 §결정 6.A per-entry namespace 정합 (CFP-389 prior art `hotfix-bypass:adr-sunset` + CFP-426 prior art 4 `hotfix-bypass:worktree-*` 직접 mirror).
2. **branch → phase mapping 표 SSOT 신설** — ADR-024 Amendment 1 hierarchical convention (`cfp-NNN[/<lane>[/<sub>]]`) 의 phase:* label 매핑이 codeforge 안에서 SSOT 부재. CFP-481 의 `auto-phase-label.yml` workflow 가 1순위 inference 로직으로 본 mapping 직접 사용 — 본 Amendment 4 가 mapping SSOT 명세화.

### Amendment

#### §결정 6.A.1 (신설) — branch → phase mapping 표 SSOT

ADR-024 Amendment 1 hierarchical convention `cfp-NNN[/<lane>[/<sub>]]` 의 lane 별도 phase:* label 매핑:

| branch pattern | phase:* label | 비고 |
|---|---|---|
| `cfp-NNN/requirements` | `phase:요구사항` | 요구사항 lane sub-branch (codeforge-requirements) |
| `cfp-NNN/design` | `phase:설계` | 설계 lane sub-branch (codeforge-design) |
| `cfp-NNN/design-review` | `phase:설계-리뷰` | 설계리뷰 lane sub-branch (codeforge-review) |
| `cfp-NNN/develop` | `phase:구현` | 구현 lane sub-branch (codeforge-develop) |
| `cfp-NNN/code-review` | `phase:구현-리뷰` | 구현리뷰 lane sub-branch (codeforge-review) |
| `cfp-NNN/security-test` | `phase:보안-테스트` | 보안테스트 lane sub-branch (codeforge-review) |
| `cfp-NNN[-<slug>]` (lane 표기 없음) | (mapping 없음 — 2순위 fallback) | story root branch — Issue Form 부착 phase:* label inheritance 또는 PR body `Related: #N` linked Issue label 복사 |
| `cfp-NNN-docs-*` 또는 body marker `<!-- doc-only -->` | `phase:설계-리뷰` (terminal default) | doc-only fast-path Story (ADR-054 §결정 4) |
| `cfp-NNN-close` 또는 Epic Phase N+1 close 시그널 | `phase:reservation` (terminal default) | Epic close PR (ADR-020 Amendment 1 §결정 9) |

**SSOT 발효**: 본 §결정 6.A.1 = mapping 표의 wrapper-owned SSOT. CFP-481 의 `auto-phase-label.yml` workflow 가 1순위 inference 로직으로 본 표 verbatim 사용. 신규 lane / sub-branch 추가 시 본 표 row 동시 갱신 의무.

**Sub-task branch (`cfp-NNN/<lane>/<sub-name>`)**: lane prefix 만 매칭 — 예: `cfp-481/design/security-arch` → `phase:설계` (lane prefix `cfp-481/design` 매칭).

**Fix iter / retro branch**: `cfp-NNN/fix-iter-<N>` / `cfp-NNN/retro` → mapping 없음 (2순위 fallback 의존).

**Mechanical enforcement** (ADR-040 Amendment 3 §결정 7.B Pattern I): `auto-phase-label` (status: deferred-followup — CFP-481 Phase 2 PR scope `docs/evidence-checks-registry.yaml` row append + `templates/github-workflows/auto-phase-label.yml` self-app workflow 도입) — 본 §결정 6.A.1 mapping 표를 1순위 inference 로직 SSOT 로 verbatim 사용. registry yaml entry name = `auto-phase-label`. tier 도입 시점 = warning (ADR-060 §결정 5 — 모든 신규 entry 는 warning 시작 강제). bypass label = `hotfix-bypass:auto-phase-label` (§결정 6.A 7번째 family member 정합).

#### §결정 6.A (확장) — `hotfix-bypass:auto-phase-label` 7번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합):

1. `hotfix-bypass:adr-sunset` (CFP-389)
2. `hotfix-bypass:worktree-session-start-wire` (CFP-426)
3. `hotfix-bypass:worktree-pre-checkout` (CFP-426)
4. `hotfix-bypass:worktree-pre-commit-main-block` (CFP-426)
5. `hotfix-bypass:worktree-spawn-evidence-cwd` (CFP-426)
6. (decision-principle-vocab — CFP-449 Amendment 3, ADR-060 entry — bypass_label optional warning tier)
7. **`hotfix-bypass:auto-phase-label` (CFP-481, 본 Amendment 4)** — 신규

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 별도 lint 신설 0건).

**bypass scope**: `auto-phase-label.yml` workflow 의 phase label 부착 step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) 전부 유지 — 본 Amendment 4 는 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 7번째 family member) + branch → phase mapping 표 SSOT 신설 only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~3 entry) 에는 영향 X.
- `auto-phase-label.yml` workflow 가 1순위 inference 로직으로 본 mapping 표 verbatim 사용 — workflow 변경 시 mapping 표와 동기 의무 (ADR-029 self-app byte-identity invariant 정합).

### Related

- ADR-060 Amendment 4 (carrier — 3rd warning-tier entry `auto-phase-label` 등록)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.3 MINOR (phase:* 8 label entry attach_owner_plugin field 갱신 — `auto-phase-label.yml` 명시)
- `templates/github-workflows/auto-phase-label.yml` (Phase 2 PR scope) — 본 mapping 표 verbatim 사용
- `.github/workflows/auto-phase-label.yml` (Phase 2 PR scope) — self-app mirror byte-identical (ADR-029)
- `docs/evidence-checks-registry.yaml` (Phase 2 PR scope) — `auto-phase-label` row append (warning tier, bypass_label `hotfix-bypass:auto-phase-label`)
- `scripts/check-bypass-audit-comment.sh` (CFP-389 prior art) — audit lint reuse

## Amendment 5 — `hotfix-bypass:debate-convergence-quality` 12번째 family member (CFP-582, 2026-05-13)

### 컨텍스트

CFP-582 Wave 4 (ADR-059 Amendment 2 carrier — debate-protocol-v1 v1.2 convergence_quality_invariant) 가 ADR-060 framework 의 첫 debate 영역 warning-tier evidence check entry `debate-convergence-quality-marker-presence` 신설. 본 entry 는 Story §9 debate transcript 안 3 marker (`[COUNTERARGUMENT]` / `[ALTERNATIVE_PROPOSED]` / `[DEBATE_PURPOSE_STATEMENT]`) section header 존재 여부를 mechanical lint 로 검증 — `scripts/check_debate_convergence_quality.py` + `templates/github-workflows/debate-convergence-quality.yml`.

ADR-060 framework 정합 의무: 모든 warning-tier evidence check entry 는 ADR-024 Amendment 3 §결정 6.A per-entry namespace `hotfix-bypass:*` family member 와 1:1 mapping 의무 (audit-trailed exception channel SSOT). 12번째 family member 등록이 본 Amendment 5 의 의무.

### Amendment

#### §결정 6.A (확장) — `hotfix-bypass:debate-convergence-quality` 12번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4 확장 정합):

1. `hotfix-bypass:adr-sunset` (CFP-389)
2. `hotfix-bypass:worktree-session-start-wire` (CFP-426)
3. `hotfix-bypass:worktree-pre-checkout` (CFP-426)
4. `hotfix-bypass:worktree-pre-commit-main-block` (CFP-426)
5. `hotfix-bypass:worktree-spawn-evidence-cwd` (CFP-426)
6. `hotfix-bypass:decision-principle-vocab` (CFP-449 — ADR-060 entry, bypass_label optional warning tier)
7. `hotfix-bypass:auto-phase-label` (CFP-481, Amendment 4)
8. `hotfix-bypass:marketplace-atomic` (ADR-063 carrier)
9. `hotfix-bypass:claude-md-line-cap` (CFP-506)
10. `hotfix-bypass:sibling-pr-author-check` (CFP-521)
11. `hotfix-bypass:workflow-permissions` (CFP-530)
12. `hotfix-bypass:workflow-yaml-parse` (CFP-583)
13. **`hotfix-bypass:debate-convergence-quality` (CFP-582, 본 Amendment 5)** — 신규

(family member 카운트 = 12 — 위 prior list 의 entry 중 ADR-060 entry 와 wrapper-internal entry 혼합 sequence. 본 Amendment 5 시점 family 총원 = 12 active entry. label-registry-v2 v2.6 sub-entry append 동반.)

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 별도 lint 신설 0건).

**bypass scope**: `debate-convergence-quality.yml` workflow 의 3 marker presence lint step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**debate 영역 첫 family member**: 기존 11 family member 는 모두 syntactic / structural mechanical lint 대응. 본 Amendment 5 의 12번째 family member 는 debate transcript 의 convergence_quality_invariant (semantic anti-sycophancy 검증) 영역 첫 진입 — debate-protocol-v1 v1.2 schema 와 inter-plugin-contracts 의 cross-validation channel 활성.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) 전부 유지 — 본 Amendment 5 는 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 12번째 family member) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~4 entry) 에는 영향 X.
- ADR-059 Amendment 2 §결정 8 convergence_quality_invariant carrier 동반 — debate-protocol-v1 v1.2 schema 의 `convergence_quality_invariant` block 과 cross-validate 의무.

### Related

- ADR-059 Amendment 2 (carrier — convergence_quality_invariant 3 marker mechanical enforcement + first debate-domain warning-tier entry)
- ADR-060 (framework — 7th warning-tier entry `debate-convergence-quality-marker-presence` 등록)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.6 sub-entry (CFP-582 — 12번째 hotfix-bypass:* family member entry)
- `docs/inter-plugin-contracts/debate-protocol-v1.md` v1.2 (convergence_quality_invariant schema block)
- `docs/evidence-checks-registry.yaml` (CFP-582 Phase 2 — `debate-convergence-quality-marker-presence` row append, warning tier, bypass_label `hotfix-bypass:debate-convergence-quality`)
- `templates/github-workflows/debate-convergence-quality.yml` — 3 marker mechanical lint workflow
- `scripts/check_debate_convergence_quality.py` — 3 marker regex lint (CFP-582 Phase 2 산출물)
- `scripts/check-bypass-audit-comment.sh` (CFP-389 prior art) — audit lint reuse

## Amendment 6 — `hotfix-bypass:*` per-entry namespace 누적 사용 카운터 lint + 31/32번째 family member (CFP-825, 2026-05-17)

### 컨텍스트

ADR-024 Amendment 3 §결정 6.A `hotfix-bypass:<entry>` per-entry namespace 가 audit-trailed exception channel 의도로 도입된 후 30 entry 누적 (label-registry-v2 v2.22 / CFP-785 `adr-077-design-reading` 30번째 family member 시점, post-CFP-825 carrier base; CFP-771 retro §8 발의 시점 = 17 entry era). CFP-771 (2026-05-16) retro §8 제안 1 이 evidence cluster 5+ 사용 발견 carrier:

- CFP-770/771 PR #788 admin merge — `hotfix-bypass:claude-md-line-cap` + `hotfix-bypass:wording-dictionary` 2 label 동시 부착
- CFP-819 PR #823 — `hotfix-bypass:wording-dictionary` cosmetic 7 occurrences
- CFP-786/801/795 carrier — `hotfix-bypass:unit-tests` pre-existing pytest 부재 사유 누적

정당 예외 채널이 누적되며 정상 경로화하는 거버넌스 erosion (bypass-as-norm mutation) — 사용 빈도 monitoring 부재 시 잠재. ADR-024 Amendment 3 §결정 6.C audit trail 3중 안전망 (PR comment 자동 발의 + audit assertion lint + audit log 집계) 가 개별 PR scope cover 하나, **per-(plugin, label) signature 단위의 시계열 누적 패턴 감지 channel 부재** — 본 Amendment 6 이 그 gap 해소.

### Amendment

#### §결정 6.A.2 (신설) — per-entry namespace 누적 사용 카운터 lint ratchet 룰

`hotfix-bypass:*` family member 의 per-(plugin, label) signature 단위 누적 사용 횟수가 threshold reach 시 carrier Issue 자동 발의 의무. ratchet 3-tuple:

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **threshold** | per-(plugin, label) signature 누적 ≥3 reach-merged PR | CFP-770/771/819 corpus 5+ 사용 evidence cluster (verified-via: gh pr view #788 #823 --json labels, Phase 2 PR open 시 재 verify-before-trust 의무). dimension category = `count` (PR 누적 횟수). units = `merged PR count per (plugin, label) signature`. |
| **dedup unit** | PR number (merged PR 고유 idempotent) | docs/domain-knowledge/domain/github-actions/workflow-idempotency-patterns.md §schedule trigger 정합 (cron 반복 → concurrency group 부족 → file-marker 부적합 → signature dedup 의무, L174 verbatim) |
| **measurement window** | all-time | rolling window (30d/90d) 도입 시 dedup signature 가 stale signature pollution 영구 carry-forward 차단 못함 — 전체 history 누적 행위 패턴 감지 의무. |
| **exempt channels (2종)** | (1) `hotfix-bypass:bypass-label-counter` (self-meta loop 회피) / (2) `hotfix-bypass:exempt:<entry>` template (rare 정당 declare, narrative audit trail mechanical enforce = 후속 carrier 영역) | self-meta loop 차단 절대 invariant + rare 정당 declare 채널 보존 |

**자동 발의 carrier Issue 본문 의무 (Phase 2 PR scope)**: signature `<plugin>::<label>` + PR 누적 list + ADR-024 Amendment 6 cross-ref + 후속 평가 영역 (threshold 재calibration vs blocking-on-merge 격상 vs 정당 사용 영역 declare).

**self-meta loop 회피 invariant**: 본 lint workflow 자체의 PR (예: `bypass-label-counter.yml` 수정 PR) 에 `hotfix-bypass:bypass-label-counter` 부착 시 해당 PR signature 누적 count 제외. lint 가 자기 자신을 trigger 하는 재귀 차단.

**multi-signature 동시 reach 처리**: 단일 cron 실행에서 다중 (plugin, label) signature 가 동시에 threshold reach 시 각 signature 별 독립 carrier Issue 발의 (signature aggregation 금지 — 후속 evaluation 의 dedup 영역 별도).

#### §결정 6.A (확장) — `hotfix-bypass:bypass-label-counter` 31번째 + `hotfix-bypass:exempt:<entry>` 32번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4/5 확장 정합 + CFP-426~CFP-722 추가 entry 누적):

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:bypass-label-counter` | **31번째** | 본 lint workflow self-meta loop 회피 — 본 entry 부착 PR 은 누적 count 제외 |
| `hotfix-bypass:exempt:<entry>` | **32번째** (template) | rare 정당 declare 채널 — `<entry>` 부분 가 specific entry name (예: `hotfix-bypass:exempt:wording-dictionary`). narrative audit trail mechanical enforce 는 후속 carrier 영역 (본 Amendment 6 = label 등록만) |

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 별도 lint 신설 0건).

**bypass scope**: `bypass-label-counter.yml` workflow 의 per-signature tally + Issue auto-create step 만 skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**bypass-as-norm mutation 영역 첫 family member**: 기존 30 family member 는 개별 evidence check 의 1회 hotfix bypass 영역. 본 Amendment 6 의 31번째/32번째 family member 는 family 자체의 누적 사용 패턴 monitoring 영역 — 첫 진입.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) + Amendment 5 (CFP-582) 전부 유지 — 본 Amendment 6 은 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 31/32번째 family member + §결정 6.A.2 ratchet 룰 신설) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~5 entry) 에는 영향 X.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 6 = forbid scope 확장 (per-entry → 누적 카운터 monitoring 추가) = ratchet-up 강화 방향, sunset_justification_required: false.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). blocking-on-merge 격상 = empirical evidence 누적 후 별 CFP carrier 영역 (ADR-060 승격 gate AND condition 통과 의무).

### scope_boundary (CFP scope unitary, ADR-064 §결정 1 정합)

본 Amendment 6 **포함** 영역:

- per-(plugin, label) signature 단위 카운터 lint (warning tier only)
- bypass-as-norm mutation 누적 monitoring (Issue auto-create + dedup)
- 2 신규 family member (self-meta exempt + rare 정당 declare template)

본 Amendment 6 **out-of-scope** (후속 carrier 영역):

- **per-plugin scope 누적 카운터** (단일 plugin 5 entry 각 1회 = 5회 분산이지만 근본은 동일 plugin 의 체계적 회피) — 별 CFP carrier
- **blocking-on-merge tier escalation** — 별 CFP, ADR-060 승격 gate AND condition 통과 후
- **bypass narrative audit trail mechanical enforce** (`[bypass-justification]` PR 코멘트 marker) — 별 CFP
- **cross-repo bypass counter extension** (codeforge-internal-docs / marketplace) — 별 CFP, EC-1 정합
- **carrier Issue 코멘트 append** (이미 발의된 Issue 에 추가 PR 정보 append) — 별 CFP

### Related

- ADR-024 Amendment 3 §결정 6.A (prior art — per-entry namespace audit-trail SSOT)
- ADR-024 Amendment 3 §결정 6.C (prior art — audit trail 3중 안전망: PR comment + audit assertion lint + audit log 집계)
- ADR-060 (framework — 63번째 evidence-checks-registry entry `bypass-label-counter` warning tier 등록)
- ADR-058 §결정 5 (ratchet-up 강화 방향 정합 — sunset_justification_required: false)
- ADR-061 (Python script convention — 본 신설 script = `.py` file + thin bash wrapper)
- ADR-040 Amendment 3 §결정 7.D (mechanical_enforcement_actions[] self-application — `bypass-label-counter` entry 추가)
- ADR-068 Amendment 1 I-5 (dimensional empirical grounding — threshold ≥3 의 `count` dimension + empirical-source annotation 의무)
- ADR-005 (workflow self-app byte-identical mirror)
- ADR-010 §결정 2 (label-registry-v2 v2.22 → v2.23 MINOR bump = wrapper-local, sibling sync 면제)
- ADR-063 (marketplace ↔ plugin.json atomic invariant — 본 carrier 적용 제외, plugin.json MINOR bump 미동반)
- ADR-066 (CODEFORGE_CROSS_REPO_PAT rotation policy — 본 workflow `permissions: issues: write` 단일 PAT consolidation)
- ADR-008 (contract versioning — v2.22 → v2.23 MINOR bump 룰)
- ADR-027 Amendment 2 §결정 6.C (manual fallback path 정합 — workflow trigger 시 PAT 환경 검증 의무)
- CFP-627 (precedent — marketplace-drift-detection 24h cron + workflow_dispatch + Issue auto-create + per-(plugin, field) signature dedup 동일 구조 reuse)
- CFP-771 retro §8 제안 1 (carrier — bypass-label-namespace 카운터 lint 제안)
- CFP-389 prior art (`scripts/check-bypass-audit-comment.sh` audit lint reuse)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.22 → v2.23 MINOR (CFP-825 — 31번째 `hotfix-bypass:bypass-label-counter` + 32번째 `hotfix-bypass:exempt:<entry>` template)
- `docs/evidence-checks-registry.yaml` (CFP-825 Phase 2 — `bypass-label-counter` 63번째 entry append, warning tier, bypass_label `hotfix-bypass:bypass-label-counter`)
- `templates/github-workflows/bypass-label-counter.yml` (CFP-825 Phase 2 — 24h cron + workflow_dispatch + Issue auto-create)
- `scripts/check-bypass-label-counter.py` (CFP-825 Phase 2 — gh api query + signature tally + threshold check + Issue auto-create)
- `scripts/check-bypass-label-counter.sh` (CFP-825 Phase 2 — thin bash wrapper, ADR-061 정합)
- `tests/scripts/test-check-bypass-label-counter.bats` (CFP-825 Phase 2 — TC 5+ baseline)

## Amendment 7 — `hotfix-bypass:corpus-claim-verify` 34번째 + `hotfix-bypass:cross-plugin-ownership-verify` 35번째 family member (CFP-841, 2026-05-17)

### 컨텍스트

CFP-841 (ADR-082 Amendment 1 carrier — §결정 6 behavioral→mechanical 전환) 가 ADR-060 framework 의 2 신규 warning-tier evidence check entry 를 신설한다:

- `corpus-claim-verify` (ADR-082 §결정 2(a)) — Story/Change-Plan/ADR 본문 corpus/fixture enumeration ("예시 N건 / 전무 / 부재 / 다수" + file-path 인용 co-occurrence) 의 `[verified: git show <ref>:<path>]` annotation 부재 검출 (ADR-068 I-5 directly-analogous pattern 재사용). `scripts/check-corpus-claim-verify.{py,sh}` + `templates/github-workflows/corpus-claim-verify.yml` (CFP-841 Phase 2 carrier).
- `cross-plugin-ownership-verify` (ADR-082 §결정 2(d)) — ChangeImpactAgent Phase 0 mapping `templates/*` wrapper-local 단정 전 `lane-self-write-ownership-matrix.yaml` cross_plugin_doc_ownership sub-tree query 1-step annotation 부재 검출 + §13.B 4-way drift-sync invariant. `scripts/check-cross-plugin-ownership-verify.{py,sh}` + workflow (CFP-841 Phase 2 carrier).

ADR-060 framework 정합 의무: 모든 warning-tier evidence check entry 는 ADR-024 Amendment 3 §결정 6.A per-entry namespace `hotfix-bypass:*` family member 와 1:1 mapping 의무 (audit-trailed exception channel SSOT). 34번째 + 35번째 family member 등록이 본 Amendment 7 의 의무 (verified-via: `git show origin/main:docs/inter-plugin-contracts/label-registry-v2.md` — v2.24 CFP-820 `hotfix-bypass:version-3way-atomic` 33번째 family member 가 현 최신, 본 Amendment 7 = 34/35번째).

### Amendment

#### §결정 6.A (확장) — `hotfix-bypass:corpus-claim-verify` 34번째 + `hotfix-bypass:cross-plugin-ownership-verify` 35번째 family member

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4/5/6 확장 정합 + CFP-426~CFP-820 추가 entry 누적, 33 active member):

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:corpus-claim-verify` | **34번째** | ADR-082 §결정 2(a) corpus annotation lint conditional skip — Story/Change-Plan/ADR corpus enumeration `[verified]` annotation lint (warning tier, CFP-841 Phase 2 carrier) |
| `hotfix-bypass:cross-plugin-ownership-verify` | **35번째** | ADR-082 §결정 2(d) cross-plugin ownership queryable lint conditional skip — `lane-self-write-ownership-matrix.yaml` cross_plugin_doc_ownership sub-tree query + §13.B 4-way drift-sync invariant lint (warning tier, CFP-841 Phase 2 carrier) |

(family member 카운트 = 33 active member (v2.24 CFP-820 33번째 `version-3way-atomic` 시점) + 본 Amendment 7 = 34/35번째 → 35 total. label-registry-v2 v2.24 → v2.25 MINOR bump 동반 — 2 신규 family member 동시 추가.)

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 독립 lint 신설 0건).

**bypass scope**: `corpus-claim-verify.yml` / `cross-plugin-ownership-verify.yml` workflow 의 annotation presence lint step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**write-time semantic truth verify 영역 첫 family member**: 기존 33 family member 는 syntactic / structural / debate / governance mechanical lint 대응. 본 Amendment 7 의 34/35번째 family member 는 ADR-082 write-time self-write semantic truth verify (corpus 단정 / cross-plugin ownership) 영역 첫 진입 — ADR-082 §결정 1 layer disjoint 표의 internal lane agent self-write layer 의 mechanical enforcement 활성.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) + Amendment 5 (CFP-582) + Amendment 6 (CFP-825) 전부 유지 — 본 Amendment 7 은 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 34/35번째 family member) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~6 entry) 에는 영향 X.
- ADR-082 Amendment 1 carrier 동반 — ADR-082 §결정 2(a)/2(d) mechanical_enforcement_actions[] deferred-followup 2 entry 와 1:1 mapping.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 7 = forbid scope 확장 (per-entry namespace 2 추가) = ratchet-up 강화 방향, `sunset_justification_required: false`.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). blocking-on-pr 격상 = empirical evidence 누적 후 별 CFP carrier 영역.

### Related

- ADR-082 Amendment 1 (carrier — §결정 6 behavioral→mechanical 전환, scope 2(a) corpus-claim-verify + scope 2(d) cross-plugin-ownership-verify)
- ADR-068 I-5 (scope 2(a) lint = I-5 `[empirical-source]` annotation directly-analogous pattern 재사용, cross-ref only)
- ADR-060 (framework — 2 신규 warning-tier evidence-checks-registry entry `corpus-claim-verify` + `cross-plugin-ownership-verify` 등록)
- ADR-024 Amendment 3 §결정 6.A (prior art — per-entry namespace audit-trail SSOT) + §결정 6.C (audit trail 3중 안전망)
- ADR-058 §결정 5 (ratchet-up 강화 방향 정합 — sunset_justification_required: false)
- ADR-010 §결정 2 (label-registry-v2 v2.24 → v2.25 MINOR = wrapper-canonical kind:registry, sibling sync 면제)
- ADR-008 (contract versioning — v2.24 → v2.25 MINOR bump 룰, 신규 label entry append = minor)
- ADR-063 (marketplace ↔ plugin.json atomic invariant — 본 carrier plugin.json MINOR bump 미동반 → atomic invariant 비발효)
- CFP-841 retro/Change Plan §3 (Phase 2 carrier — lint script + workflow + bats + yaml cross-plugin sub-tree 확장 + §13.B 4-way sync)
- CFP-389 prior art (`scripts/check-bypass-audit-comment.sh` audit lint reuse)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` Amendment 1 (carrier)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.24 → v2.25 MINOR (CFP-841 — 34번째 `hotfix-bypass:corpus-claim-verify` + 35번째 `hotfix-bypass:cross-plugin-ownership-verify`)
- `docs/evidence-checks-registry.yaml` (CFP-841 — `corpus-claim-verify` + `cross-plugin-ownership-verify` 2 entry append, warning tier, deferred-followup status, Phase 2 actual wire)
- `templates/github-workflows/corpus-claim-verify.yml` / `cross-plugin-ownership-verify.yml` (CFP-841 Phase 2 — annotation presence lint workflow)
- `scripts/check-corpus-claim-verify.{py,sh}` / `scripts/check-cross-plugin-ownership-verify.{py,sh}` (CFP-841 Phase 2 — ADR-061 정합 외부 .py + thin bash wrapper)
- `tests/scripts/test-check-corpus-claim-verify.bats` / `test-check-cross-plugin-ownership-verify.bats` (CFP-841 Phase 2 — TC 5+ baseline 각)

## Amendment 8 — bypass-as-norm-mutation 후속 escalation 3 sub-decision 통합 + 37/38/39번째 family member (CFP-845, 2026-05-17)

### 컨텍스트

CFP-825 Amendment 6 §결정 6.A.2 가 `bypass-label-counter` warning-tier lint 로 per-(plugin, label) signature 누적 모니터링 channel 을 도입했으나 **§scope_boundary 가 명시한 4 out-of-scope 후속 carrier 영역** (per-plugin scope 누적 / blocking-on-merge tier 격상 / `[bypass-justification]` narrative audit / cross-repo extension) 의 후속 carrier 영역 미해소. CFP-845 (carrier) brainstorm Phase 0 4-agent 수렴 결과 = "옵션 B 2-Story 분할 권장" — 본 Amendment 8 (Story-1) = 4 영역 중 3 즉시 통합 (per-plugin / `[bypass-justification]` marker / cross-repo), 4번째 (blocking-on-merge tier 격상) = Story-2 (#861 RESERVED) evidence-gated 분리. ADR-064 §결정 1 (CFP scope unitary) 정합 — Story-2 분리 사유 = ADR-060 promotion gate AND-condition (PR≥20 + bypass외 failure=0 + sibling merged) 가 외부 시간 의존 gate, "경량→full" 단계 한 CFP 묶임 차단.

본 Amendment 8 적용 영역 = 3 신규 sub-decision (§결정 6.A.3 / §결정 6.A.4 / §결정 6.A.5) + §결정 6.A 확장 (3 신규 family member: 37/38/39번째). bypass-as-norm mutation governance erosion 영역의 **multi-axis monitoring 확장** (entry-axis → plugin-axis → cross-repo-axis + narrative audit axis).

### Amendment

#### §결정 6.A.3 (신설) — per-plugin 전체 누적 카운터 ratchet 룰

`hotfix-bypass:*` family member 의 per-(plugin) signature 단위 (label entry 무관 cross-entry 집계) 누적 사용 횟수가 threshold reach 시 carrier Issue 자동 발의 의무. §결정 6.A.2 (per-entry namespace) 의 **상위 layer 집계 channel** — 단일 plugin 이 5 entry 각 1회 = 5회 분산 사용 시 §결정 6.A.2 미발의 (각 entry 1회 < threshold 3) but **근본은 동일 plugin 의 체계적 회피** (per-plugin scope norm mutation). 본 §결정 6.A.3 이 그 gap 해소.

ratchet 3-tuple:

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **threshold** | per-(plugin) signature 누적 ≥5 reach-merged PR | per-entry threshold 3 (§결정 6.A.2) 보다 보수적 (5) — entry 다양성 cover 의 noise floor. dimension category = `count` (PR 누적 횟수). units = `merged PR count per plugin signature (cross-entry aggregate)`. empirical-source = CFP-825 evidence cluster (single plugin 5+ entry 사용 corpus) + CFP-845 Research §unknown unknown 1 (per-plugin threshold calibration evidence 부족 → 보수적 시작, Phase 2 actual wire 후 별 calibration carrier) |
| **dedup unit** | PR number (merged PR 고유 idempotent) | §결정 6.A.2 와 동일 — docs/domain-knowledge/domain/github-actions/workflow-idempotency-patterns.md §schedule trigger 정합 |
| **measurement window** | all-time | §결정 6.A.2 와 동일 — rolling window 의 stale signature pollution 차단 |
| **exempt channels (3종)** | (1) `hotfix-bypass:per-plugin-cumulative-counter` (self-meta loop 회피) / (2) `hotfix-bypass:exempt:<entry>` template (rare 정당 declare, CFP-825 prior art) / (3) `hotfix-bypass:exempt:per-plugin` template (per-plugin scope 정당 declare, 본 §결정 6.A.3 신규) | self-meta loop 차단 + per-entry/per-plugin scope 양 declare 채널 보존 |

**자동 발의 carrier Issue 본문 의무 (Phase 2 PR scope)**: signature `<plugin>` + entry breakdown (entry 별 PR list) + PR 누적 list + ADR-024 Amendment 8 cross-ref + 후속 평가 영역 (threshold 재calibration vs blocking-on-merge 격상 vs 정당 사용 영역 declare).

**self-meta loop 회피 invariant**: 본 lint workflow 자체의 PR (예: `per-plugin-cumulative-counter.yml` 수정 PR) 에 `hotfix-bypass:per-plugin-cumulative-counter` 부착 시 해당 PR signature 누적 count 제외.

**§결정 6.A.2 와 disjoint invariant**: 동일 PR 가 §결정 6.A.2 (per-entry) + §결정 6.A.3 (per-plugin) 양 trigger 시 양 carrier Issue 각 발의 (signature aggregation 금지, 각 carrier 가 별 evaluation 영역).

#### §결정 6.A.4 (신설) — `[bypass-justification]` PR comment marker mechanical enforce

`hotfix-bypass:*` label 부착 PR 의 `[bypass-justification]` prefix PR comment 존재 의무 — narrative audit trail mechanical enforce. `scripts/check-bypass-justification-marker.sh` lint = grep-presence only (semantic adequacy 검증 불가):

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **lint scope** | hotfix-bypass:* label 부착 PR 의 PR comment (review comment 제외 — top-level only) | comment-prefix-registry-v1 v1.3 신규 `[bypass-justification]` prefix (CFP-845 carrier) — 14번째 phase prefix. dimension category = `count` (PR per-presence boolean) |
| **grep pattern** | `^\[bypass-justification\]` (line start anchor, case-sensitive) | comment-prefix-registry-v1 §3 entry 표준 형식 정합 (Bracket prefix + 빈칸 + 본문) |
| **semantic adequacy** | grep-only — **semantic 진위 검증 불가** | false-positive risk 명시 (CFP-845 Research §unknown unknown 2) — reviewer responsibility, lint 가 narrative 정당성 평가 X |
| **false-positive policy** | grep PASS but body 부적합 (예: 빈 marker, 단순 "ok") = lint PASS but reviewer reject 영역 | Phase 2 workflow PR comment 안 reminder 자동 발의 (사용자 가이드 + warning marker) — 별 carrier |

**bypass scope**: `bypass-justification-marker.yml` workflow 의 grep-presence lint step skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**self-meta loop 회피 invariant**: 본 lint workflow 자체의 PR 에 `hotfix-bypass:bypass-justification-marker` 부착 시 marker presence check skip.

**marker 의무 scope**: hotfix-bypass:* label 부착 PR only — label 부착 없는 PR 은 marker 의무 X.

**audit trail 영구화**: PR comment 는 GitHub-side state (영구 보존, PR close 후도 유지) — file marker 와 disjoint, dedup 불요 (PR 별 1회 발화).

#### §결정 6.A.5 (신설) — cross-repo bypass counter extension

현 wrapper (`mclayer/plugin-codeforge`) 단일 cover → **3-repo 동시 cover** 확장: `mclayer/plugin-codeforge` + `mclayer/codeforge-internal-docs` + `mclayer/marketplace`. signature = (repo, plugin, label) 3-tuple, threshold 별 calibration:

| 항목 | 값 | 근거 (empirical-source) |
|---|---|---|
| **scope repos (3종)** | wrapper plugin-codeforge / internal-docs / marketplace | ADR-013 §결정 family scope 7 plugin (wrapper + 6 lane plugin, 단 lane plugin 의 hotfix-bypass 사용은 wrapper-only governance — sibling sync 면제 정합, ADR-010 §결정 2). 본 §결정 6.A.5 cover = 3 cross-repo 중 hotfix-bypass label 사용 영역 (wrapper governance / internal-docs dogfood artifact / marketplace publication) |
| **threshold** | per-(repo, plugin, label) signature 누적 ≥3 reach-merged PR | §결정 6.A.2 와 동일 (3) — repo namespace 분리 시 per-repo 독립 trigger. dimension category = `count`. units = `merged PR count per (repo, plugin, label) signature` |
| **aggregate trigger** | 3 repo 동일 (plugin, label) signature 동시 reach 시 단일 aggregate carrier Issue 발의 (multi-repo signature) | per-repo 단독 trigger + aggregate trigger 양 channel disjoint — aggregate = 3-repo systemic mutation 신호, per-repo = 단일 repo local mutation 신호 |
| **dedup unit** | (repo, PR number) 2-tuple (cross-repo PR number 충돌 회피) | 3 repo 동일 PR number 가능 — repo namespace 의무 |
| **PAT scope** | 단일 PAT (CODEFORGE_CROSS_REPO_PAT, ADR-066) reuse — 3 repo `issues:read` + `repo:read` 권한 | 신규 secret 0건, ADR-066 rotation policy 적용 (90 day rotation / 180 day max lifetime) |
| **exempt channels** | `hotfix-bypass:cross-repo-bypass-counter` (self-meta loop 회피) + §결정 6.A.2/6.A.3 의 exempt 채널 carry-over | 3 axis lint self-meta loop 차단 |

**자동 발의 carrier Issue 본문 의무 (Phase 2 PR scope)**: signature `(repo)::<plugin>::<label>` 또는 aggregate `<plugin>::<label>` (3-repo) + repo breakdown (repo 별 PR list) + ADR-024 Amendment 8 cross-ref + 후속 평가 영역 + ADR-066 PAT audit trail.

**carrier Issue repository**: aggregate carrier = `mclayer/plugin-codeforge` (wrapper governance owner SSOT, ADR-013 정합). per-repo carrier = 해당 repo (각 repo 의 local governance).

**ADR-066 PAT 의존 invariant**: 본 §결정 6.A.5 작동 의무 = CODEFORGE_CROSS_REPO_PAT secret 활성 + 3 repo `issues:read` + `repo:read` 권한 보유 — PAT 만료 시 workflow 실패 (warning tier 정합, blocking 미발효).

#### §결정 6.A (확장) — 3 신규 family member (37/38/39번째)

기존 `hotfix-bypass:*` family (Amendment 3 §결정 6.A 정합 + Amendment 4/5/6/7 확장 정합 + CFP-426~CFP-841 추가 entry 누적, 36 active member — v2.26 CFP-821 `branch-protection-sync` 36번째):

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:per-plugin-cumulative-counter` | **37번째** | §결정 6.A.3 per-plugin scope 누적 카운터 self-meta loop 회피 — 본 entry 부착 PR 은 per-plugin 누적 count 제외 |
| `hotfix-bypass:bypass-justification-marker` | **38번째** | §결정 6.A.4 PR comment marker presence lint conditional skip — narrative audit 영역 첫 family member |
| `hotfix-bypass:cross-repo-bypass-counter` | **39번째** | §결정 6.A.5 cross-repo 3-tuple signature 누적 카운터 self-meta loop 회피 — cross-repo 영역 첫 family member |

(family member 카운트 = 36 active member (v2.26 CFP-821 36번째 `branch-protection-sync` 시점) + 본 Amendment 8 = 37/38/39번째 → 39 total. label-registry-v2 v2.26 → v2.27 MINOR bump 동반 — 3 신규 family member 동시 추가.)

**audit lint**: `scripts/check-bypass-audit-comment.sh` reuse (CFP-389 prior art 단일 lint, `BYPASS_LABEL_PREFIX=hotfix-bypass:` env scan 으로 all-family detect — 신규 audit lint 0건).

**bypass scope**: `per-plugin-cumulative-counter.yml` / `bypass-justification-marker.yml` / `cross-repo-bypass-counter.yml` workflow 의 각 lint step 만 skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**bypass-as-norm mutation 다차 axis monitoring 영역 진입**: 기존 36 family member 는 단일 axis (per-entry signature) cover. 본 Amendment 8 의 37/38/39번째 family member 는 **3 신규 axis** (per-plugin scope / narrative audit / cross-repo extension) 동시 진입 — bypass-as-norm mutation governance erosion 의 multi-axis monitoring 완비.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1 (CFP-134) + Amendment 2 (CFP-280) + Amendment 3 (CFP-389) + Amendment 4 (CFP-481) + Amendment 5 (CFP-582) + Amendment 6 (CFP-825) + Amendment 7 (CFP-841) 전부 유지 — 본 Amendment 8 은 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 37/38/39번째 family member + §결정 6.A.3/6.A.4/6.A.5 ratchet 룰 신설) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~7 entry) 에는 영향 X.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 8 = forbid scope 확장 (per-entry → per-plugin scope 추가 + narrative audit 추가 + cross-repo 추가) = ratchet-up 강화 방향, sunset_justification_required: false.
- ADR-024 Amendment 6 §scope_boundary 4 out-of-scope 영역 중 3 영역 흡수 (per-plugin / `[bypass-justification]` marker / cross-repo) — 4번째 (blocking-on-merge tier 격상) = Story-2 #861 RESERVED 별 carrier evidence-gated 분리, ADR-064 §결정 1 CFP scope unitary 정합.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). blocking-on-merge 격상 = empirical evidence 누적 후 별 CFP carrier 영역 (ADR-060 승격 gate AND condition 통과 의무, Story-2 #861).
- comment-prefix-registry-v1 v1.2 → v1.3 MINOR bump 동반 (§결정 6.A.4 `[bypass-justification]` 14번째 prefix 신설) — ADR-008 MINOR (entry 추가 = append-only for v1.x rule 정합), kind:registry sibling sync 면제 (ADR-010 §결정 2).
- ADR-066 단일 PAT (CODEFORGE_CROSS_REPO_PAT) reuse — 신규 secret 0건, rotation policy 영향 0.

### scope_boundary (CFP scope unitary, ADR-064 §결정 1 정합)

본 Amendment 8 **포함** 영역 (Story-1 = 본 #845 ACTIVE):

- §결정 6.A.3 per-plugin scope 누적 카운터 ratchet (warning tier only)
- §결정 6.A.4 `[bypass-justification]` PR comment marker presence lint (grep-only, false-positive risk 명시)
- §결정 6.A.5 cross-repo bypass counter extension (wrapper + internal-docs + marketplace 3-repo)
- 3 신규 family member (37/38/39번째)
- comment-prefix-registry-v1 v1.3 MINOR bump (`[bypass-justification]` 14번째 prefix)

본 Amendment 8 **out-of-scope** (Story-2 #861 RESERVED 별 carrier 영역):

- **blocking-on-merge tier escalation** — ADR-060 승격 gate AND condition (PR 누적 ≥20 + bypass 외 failure=0 + sibling Story merged) 통과 후 별 carrier (#861 evidence-gated). 본 Amendment 8 = 3 신규 entry warning tier first iteration only.

본 Amendment 8 **후속 carrier 영역** (Phase 2 actual wire 후 별 carrier):

- per-plugin threshold 재calibration (현 5 = 보수적 시작, Phase 2 evidence 누적 후 재평가)
- cross-repo aggregate threshold 재calibration (현 3 = per-entry 동일, multi-repo systemic 신호 noise floor 평가)
- `[bypass-justification]` marker semantic adequacy 자동 평가 (현 grep-only, NLP 평가는 별 carrier — Research §unknown unknown 2 deferred)
- per-plugin 외 추가 axis (예: per-author cumulative — Phase 2 actual wire 후 evidence 누적 시 별 carrier)

### Related

- ADR-024 Amendment 3 §결정 6.A (prior art — per-entry namespace audit-trail SSOT)
- ADR-024 Amendment 3 §결정 6.C (prior art — audit trail 3중 안전망: PR comment + audit assertion lint + audit log 집계)
- ADR-024 Amendment 6 §결정 6.A.2 (prior art — per-entry namespace 누적 사용 카운터 ratchet 룰)
- ADR-024 Amendment 6 §scope_boundary (본 Amendment 8 의 4 out-of-scope 영역 중 3 영역 흡수, 4번째 = Story-2 #861 RESERVED)
- ADR-060 (framework — 3 신규 warning-tier evidence-checks-registry entry `per-plugin-cumulative-counter` + `bypass-justification-marker` + `cross-repo-bypass-counter` 등록, Phase 1 entry append + Phase 2 actual wire)
- ADR-058 §결정 5 (ratchet-up 강화 방향 정합 — sunset_justification_required: false)
- ADR-061 (Python script convention — 본 신설 3 lint script = `.py` file + thin bash wrapper 각)
- ADR-040 Amendment 3 §결정 7.D (mechanical_enforcement_actions[] self-application — `per-plugin-cumulative-counter` + `bypass-justification-marker` + `cross-repo-bypass-counter` 3 entry 추가)
- ADR-068 Amendment 1 I-5 (dimensional empirical grounding — threshold ≥5 `count` dimension + threshold ≥3 `count` dimension 각 empirical-source annotation 의무)
- ADR-005 (workflow self-app byte-identical mirror — 3 신규 workflow yml templates/ ↔ .github/workflows/ 동기)
- ADR-010 §결정 2 (label-registry-v2 v2.26 → v2.27 MINOR + comment-prefix-registry-v1 v1.2 → v1.3 MINOR = wrapper-canonical kind:registry, sibling sync 면제)
- ADR-008 (contract versioning — 2 kind:registry MINOR bump 룰, 신규 entry append = minor)
- ADR-063 (marketplace ↔ plugin.json atomic invariant — 본 carrier plugin.json MINOR bump 미동반 → atomic invariant 비발효)
- ADR-066 (CODEFORGE_CROSS_REPO_PAT rotation policy — 본 §결정 6.A.5 cross-repo workflow `permissions: issues: write` + `repo: read` 단일 PAT reuse, rotation 90 day 정합)
- ADR-027 Amendment 2 §결정 6.C (manual fallback path 정합 — workflow trigger 시 PAT 환경 검증 의무)
- ADR-013 (family scope SSOT — 3 cross-repo = wrapper + internal-docs + marketplace)
- ADR-064 §결정 1 (CFP scope unitary — Story-1 (본 #845) 3 즉시 통합 + Story-2 (#861 RESERVED) 1 deferred 분리 정합)
- CFP-825 retro §6 후보 3 (carrier — bypass-as-norm mutation 후속 escalation 4 영역 발의)
- CFP-825 Amendment 6 §scope_boundary (out-of-scope 4 영역 verbatim 인용 → 본 Amendment 8 = 3 영역 흡수)
- CFP-845 Issue body + scope-split comment (2026-05-17 KST) — 옵션 B 2-Story 분할 권장 (Researcher / PMO / Analyst 3-agent 합치)
- CFP-861 RESERVED (Story-2 — blocking-on-merge tier 격상 carrier, evidence-gated)
- CFP-771 retro §8 제안 1 (prior art lineage — bypass-label-namespace 카운터 lint 제안, CFP-825 Amendment 6 첫 carrier)
- CFP-627 (precedent — marketplace-drift-detection 24h cron + workflow_dispatch + Issue auto-create + per-(plugin, field) signature dedup 동일 구조 cross-repo reuse)
- CFP-389 prior art (`scripts/check-bypass-audit-comment.sh` audit lint reuse)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.26 → v2.27 MINOR (CFP-845 — 37번째 `hotfix-bypass:per-plugin-cumulative-counter` + 38번째 `hotfix-bypass:bypass-justification-marker` + 39번째 `hotfix-bypass:cross-repo-bypass-counter`)
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` v1.2 → v1.3 MINOR (CFP-845 — 14번째 `[bypass-justification]` prefix 신설)
- `docs/evidence-checks-registry.yaml` (CFP-845 Phase 1 — `per-plugin-cumulative-counter` + `bypass-justification-marker` + `cross-repo-bypass-counter` 3 entry append, warning tier, deferred-followup status, Phase 2 actual wire)
- `templates/github-workflows/per-plugin-cumulative-counter.yml` / `bypass-justification-marker.yml` / `cross-repo-bypass-counter.yml` (CFP-845 Phase 2 — 24h cron + PR-time lint 각)
- `scripts/check-per-plugin-cumulative-counter.{py,sh}` / `check-bypass-justification-marker.{py,sh}` / `check-cross-repo-bypass-counter.{py,sh}` (CFP-845 Phase 2 — ADR-061 정합 외부 .py + thin bash wrapper 각)
- `tests/scripts/test-check-per-plugin-cumulative-counter.bats` / `test-check-bypass-justification-marker.bats` / `test-check-cross-repo-bypass-counter.bats` (CFP-845 Phase 2 — TC 5+ baseline 각)

## Amendment 9 — `hotfix-bypass:codex-sandbox-substitution` 44번째 family member (CFP-963, 2026-05-19 KST)

### 컨텍스트

CFP-963 = CFP-946 Epic (Codex worker network_scope mechanical layer) Story-B carry-forward. ADR-081 Amendment 4 §결정 D1.D body 확장 (boolean `sandbox_network_required: <bool>` → 4-tier `network_scope: <enum>` strict ratchet-up) + ADR-060 Amendment 14 §결정 28 신설 (12번째 warning-tier evidence-checks-registry entry `codex-network-scope-presence`) 동반.

ADR-060 framework 의 신규 warning-tier entry 도입 시 ADR-024 §결정 6.A per-entry namespace bypass channel 의무 동반 (Amendment 3 §결정 6.A 정합). 본 Amendment 9 = 44번째 family member `hotfix-bypass:codex-sandbox-substitution` 추가.

### Amendment

#### §결정 6.A (확장) — 44번째 신규 family member

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:codex-sandbox-substitution` | **44번째** (historical-with-template-count convention) | ADR-060 Amendment 14 §결정 28 `codex-network-scope-presence` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel. ADR-081 Amendment 4 §결정 D1.D body 확장 (4-tier `network_scope` enum) 의 mechanical enforcement layer 의 bypass channel. codex worker collaboration mechanical layer 영역 첫 family member. |

**카운트 convention (Codex TP#2 F-CX-963-A P2 calibration 정합)**:

active concrete entry direct grep count (`^  - name: hotfix-bypass:` line-anchor):
- v2.34 시점 grep count = 42 entries (직접 verified — label-registry-v2.md §3 active hotfix-bypass entries)
- CFP-825 Amendment 6 §결정 6.A.2 historical Nth count = 32 `hotfix-bypass:exempt:<entry>` template (rare 정당 declare 채널, template not concretely instantiated — historical Nth count 1 포함)
- 직전 family member 43번째 = `hotfix-bypass:architecture-drift` (CFP-923 self-describe L1011 "43번째 family member" 정합 — `42 active concrete + 1 template historical = 43 historical Nth`)
- 신규 = **44번째 historical Nth** (`43 historical Nth + 1 = 44 new`)

historical-with-template-count convention 채택 사유:
- ADR-024 Amendment 6 §결정 6.A.2 (CFP-825) 가 31번째 + 32번째 family member 동시 추가 시 32번째 = `hotfix-bypass:exempt:<entry>` template (rare 정당 declare 채널) → 본 convention 의 first precedent
- Amendment 7 (CFP-841) / Amendment 8 (CFP-845) 모두 직전 family member 의 historical Nth + N convention 답습 (raw grep count divergence 영역 의식적 보존)
- 본 Amendment 9 = convention 답습 (raw grep 42 + 1 = 43 vs historical Nth 43 + 1 = 44, **historical convention 채택**)

label-registry-v2 v2.34 → v2.35 MINOR bump 동반 (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 3 row append).

**자동 발의 carrier Issue 본문**: bypass label 부착 PR 마다 `scripts/check-bypass-audit-comment.sh` audit lint (CFP-389 prior art reuse, 단일 lint 모든 family entry detect) 가 audit comment 의무 검증 + audit log 집계.

#### Bypass scope

`codex-network-scope-presence.yml` workflow 의 lint step (`scripts/check-codex-network-scope.sh` Python SSOT invocation) 의 conditional skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**self-meta loop 회피**: 본 lint workflow / script 자체의 PR 에 `hotfix-bypass:codex-sandbox-substitution` 부착 시 본 lint step skip. **carrier_story self-exempt**: 본 entry 도입 carrier (CFP-963) Story file 자체의 Phase 1+2 PR 은 carrier 영역 bootstrap-exempt 정합 (ADR-062 §결정 8 self-application precedent / CFP-722 §결정 27 carrier-Story exemption 동형).

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1~8 전부 유지 — 본 Amendment 9 은 Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 44번째 family member append) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~13 entry) 에는 영향 X.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 9 = forbid scope 확장 (44th family member append) = ratchet-up 강화 방향, sunset_justification_required: false.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). blocking-on-pr 격상 = empirical evidence 누적 후 별 CFP carrier 영역 (ADR-060 승격 gate AND condition 통과 의무).
- label-registry-v2 v2.34 → v2.35 MINOR bump 동반 (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 3 — 신규 entry append = MINOR).
- ADR-008 §결정 3 정합 (kind:registry MINOR rule). plugin.json bump 0 → ADR-063 marketplace atomic invariant 미발효 (mirrored field 무변경, marketplace_sync_declared:false).

### Related

- ADR-060 Amendment 14 §결정 28 (CFP-963 carrier — 12번째 warning-tier entry `codex-network-scope-presence`)
- ADR-081 Amendment 4 §결정 D1.D body 확장 (boolean → 4-tier `network_scope` enum strict ratchet-up)
- ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합 (44번째 family member)
- ADR-024 Amendment 6 §결정 6.A.2 historical-with-template-count convention first precedent (`hotfix-bypass:exempt:<entry>` 32번째 template)
- ADR-010 §결정 2 + ADR-008 §결정 3 (kind:registry sibling sync 면제 + MINOR append rule)
- ADR-040 Amendment 3 §결정 7.A self-application — 본 Amendment 9 mechanical_enforcement_actions entry binding (action: `codex-network-scope-presence`, target_section: §결정 6.A)
- ADR-058 §결정 5 정합 (is_transitional:false 영구 governance, ratchet-up 강화 방향, sunset_justification_required:false)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.34 → v2.35 MINOR (CFP-963 — 44번째 `hotfix-bypass:codex-sandbox-substitution`)
- `docs/evidence-checks-registry.yaml` (CFP-963 Phase 1 — `codex-network-scope-presence` entry append, warning tier, deferred-followup status, Phase 2 actual wire)
- `templates/github-workflows/codex-network-scope-presence.yml` + `.github/workflows/` self-app (CFP-963 Phase 2 — byte-identical ADR-005)
- `scripts/check-codex-network-scope.{sh,py}` (CFP-963 Phase 2 — ADR-061 정합 외부 .py + thin bash wrapper)
- `tests/bats/test_codex_network_scope.bats` + `tests/fixtures/codex_spawn_prompt_{with,without}_network_scope.txt` (CFP-963 Phase 2 — CX-963-3 P2 boundary fixture pair mandate)
- Codex TP#2 F-CX-963-A P2 calibration verdict (`[codex-severity-inflation: F-CX-963-A P1→P2]` Story §10 marker per ADR-081 §결정 D6.e tracking convention)

## Amendment 10 — `hotfix-bypass:prod-cutover-deputy-evidence` 45번째 (raw) family member registry-side late codify (CFP-1000, 2026-05-19 KST)

### 컨텍스트

CFP-1000 = CFP-963 retro 직후 발견된 bidirectional drift 36 entries 의 Tier-A closure carrier. RequirementsPL verify-before-trust direct probe (ADR-082 §결정 1) 가 두 incident 식별:

1. **`hotfix-bypass:prod-cutover-deputy-evidence`** (registered-but-not-declared): gh repo 1 hit (CFP-954 PR-time 부착 이력) but registry §3 yaml 미선언. **본 Amendment 10 = registry §3 late codify carrier**.
2. **`hotfix-bypass:inter-plugin-contracts-parity`** (declared-but-not-registered): registry §3 L994 declared (CFP-894 v2.29) but gh repo 0 hits. **본 Story Phase 1 PR open 시 `bootstrap-labels.yml` workflow auto-run 의무 발효 영역** — registry §3 변경 0건, gh CLI 실행만 추가 (CFP-598 dynamic registry-driven pattern 자동 — `scripts/parse-hotfix-bypass-labels.py` 가 §3 yaml read auto-emit).

Orchestrator 가 ADR-064 §결정 1 (CFP scope unitary) 정합 Tier-A (Issue body 명시 2 entries) 만 본 Story 범위 ratify, Tier-B (잔여 34 entries reconcile sweep — gh→registry 5 + registry→gh 29) 는 별도 CFP #1004 (post-merge open) 이관.

### Amendment

#### §결정 6.A (확장) — 45번째 (raw) 신규 family member

| 신규 entry | family position | 의미 |
|---|---|---|
| `hotfix-bypass:prod-cutover-deputy-evidence` | **45번째 (raw)** (raw active concrete grep count: 44 + 1 new = 45) | ADR-72 §결정 5 evidence-checks-registry 2 entry (`production-cutover-deputy-spawn-evidence` + `epic-cutover-gate-evidence-quad-check`) warning-tier bypass channel. Wave 4 sub-Epic #882 Story-3 ProductionEvidenceDeputy mandate first activation declare layer 의 mechanical lint conditional skip 채널. registry-side late codify — gh-side 는 CFP-954 PR-time 이미 등록 (1 hit verified 2026-05-19 KST). |

**카운트 convention 정합 (raw active concrete grep, NOT historical-with-template-count)**:

본 Amendment 10 = **raw active concrete grep count convention** 채택. Amendment 9 (CFP-963) 의 historical-with-template-count convention 과 disjoint scope.

- Pre-CFP-1000 시점 active concrete grep count (`^  - name: hotfix-bypass:` line-anchor) = **44** (직접 verified `git show 506bb20:docs/inter-plugin-contracts/label-registry-v2.md | grep -c "^  - name: hotfix-bypass:"` = 44, 2026-05-19 KST)
- 직전 raw family member (44th raw) = `hotfix-bypass:parallel-work-sentinel-pickup` (CFP-967 self-describe L1028 "45번째 family member" — historical-with-template-count convention, raw count 44 + template adjustment 1 = 45 historical)
- 신규 (CFP-1000 post-edit) = **45번째 raw active concrete grep** (`44 + 1 new = 45`)

**Convention re-anchor notice**: CFP-967 self-described "45번째" while actual pre-edit raw count was 44 — CFP-967 internally used historical-with-template-count convention (Amendment 9 precedent 답습) but labeled the result as raw "45". 본 Amendment 10 = explicit raw active concrete grep count convention 채택 — 45번째 = post-edit grep count (44 + 1 = 45). 동일 숫자 "45" 의 occurrence 는 우연 (CFP-967 historical 45 ↔ CFP-1000 raw 45) but 의미 disjoint (semantically 다른 convention). 후속 amendment 는 본 convention re-anchor 답습 의무.

Convention 채택 사유:

- Amendment 9 historical-with-template-count convention 은 CFP-963 carrier 영역 specific (`codex-sandbox-substitution` 의 template-vs-concrete 모호성 영역 정합 — `hotfix-bypass:exempt:<entry>` template 의 active vs concrete instantiated 모호성 처리 영역). 본 Amendment 10 carrier (`prod-cutover-deputy-evidence`) 는 template-vs-concrete 모호성 영역 외 — raw count 우선 정합.
- CFP-967 (Amendment 직접 없이 §3 yaml self-describe "45번째" 인용) 가 raw grep count convention 답습 사례 — 본 Amendment 10 동일 노선.
- Multi-convention coexistence 정합 (Amendment 9 historical / 본 Amendment 10 raw — convention divergence ↔ entry-specific calibration). 후속 amendment 시 entry-specific convention 명시 의무.

**CLAUDE.md L295 historical attribution invariant**: CLAUDE.md L295 prose `hotfix-bypass:prod-cutover-deputy-evidence 44번째 family member` 인용은 CFP-954 PR-time historical attribution (당시 raw count = 43 + template 1 = 44 historical-with-template-count). 본 Amendment 10 = registry §3 late codify carrier 영역, CLAUDE.md L295 인용 갱신은 본 Story OOS (ADR-064 §결정 1 scope unitary 정합). Tier-B reconcile sweep CFP #1004 영역 — historical numbering reconciliation 별도 carrier.

label-registry-v2 v2.36 → v2.37 MINOR bump 동반 (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 3 row append).

**자동 발의 carrier Issue 본문**: bypass label 부착 PR 마다 `scripts/check-bypass-audit-comment.sh` audit lint (CFP-389 prior art reuse, 단일 lint 모든 family entry detect) 가 audit comment 의무 검증 + audit log 집계.

#### Bypass scope

`production-cutover-evidence.yml` workflow 의 lint step (`scripts/check-production-cutover-evidence.sh` SSOT invocation) 의 conditional skip — phase-gate-mergeable.yml / phase-label-invariant.yml / 기타 4 core required check 영향 0건 (Amendment 3 §결정 6.B 정합).

**self-meta loop 회피**: 본 lint workflow / script 자체의 PR 에 `hotfix-bypass:prod-cutover-deputy-evidence` 부착 시 본 lint step skip. **carrier_story self-exempt**: 본 entry 도입 carrier (CFP-1000) Story file 자체의 Phase 1 PR 은 carrier 영역 bootstrap-exempt 정합 (ADR-062 §결정 8 self-application precedent / CFP-722 §결정 27 carrier-Story exemption 동형). ADR-72 §결정 3 D3 consensus wrapper-self-app exemption 2-tier (Tier-1 declare-time + Tier-2 runtime) 와 disjoint scope — exemption ≠ bypass channel (exemption 외 영역에서만 bypass 발효).

#### inter-plugin-contracts-parity 등록 mechanism (registry §3 변경 0건)

`hotfix-bypass:inter-plugin-contracts-parity` (CFP-894 v2.29 L994 이미 declared) 는 본 Amendment 10 영역 외 — registry §3 변경 0건 invariant. gh-side 0 hits 의 해소 mechanism = bootstrap-labels.yml workflow PR open 시 auto-run (CFP-598 dynamic registry-driven pattern). 본 Story Phase 1 PR open 시 workflow 가 §3 yaml read → 두 labels 모두 emit (idempotent invariant: `prod-cutover-deputy-evidence` = gh API 422 already-exists swallow / `inter-plugin-contracts-parity` = gh API 201 created).

#### Tier-B handoff (CFP #1004)

bidirectional drift 잔여 34 entries (gh→registry 5 + registry→gh 29) reconcile sweep = 별도 CFP #1004 (post-merge open) 이관. ADR-064 §결정 1 (CFP scope unitary) 정합 — 한 CFP 안 "Tier-A 경량 → Tier-B full" 단계 채택 금지. 별 CFP 분리 (CFP-1000 Tier-A + CFP-1004 Tier-B) 가 independent brainstorm + independent Story + independent PR invariant 보존.

추가 OOS 영역 (CFP #1004 또는 별 CFP carrier):
- `claude-md-amendment-ref-drift` (gh) vs `claude-md-amendment-ref` (registry) naming mismatch rename direction
- CLAUDE.md L295 historical-Nth attribution reconciliation
- pattern_count tracking ADR 후보 (RequirementsPL §2.2 OOS noted)
- inter-plugin-contracts-parity check design-output-v2 marker fix (RequirementsPL §2.2 OOS noted)

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1~9 전부 유지 — 본 Amendment 10 = Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 45번째 (raw) family member append) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~13 entry) 에는 영향 X.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 10 = forbid scope 확장 (46th family member append) = ratchet-up 강화 방향, sunset_justification_required: false.
- warning tier 첫 도입 (ADR-060 §결정 5 정합 — 모든 신규 entry 는 warning 시작 강제). 본 entry = ADR-72 §결정 5 `production-cutover-deputy-spawn-evidence` + `epic-cutover-gate-evidence-quad-check` 2 entry warning-tier 동반. blocking-on-pr 격상 = empirical evidence 누적 후 별 CFP carrier 영역 (ADR-060 승격 gate AND condition 통과 의무).
- label-registry-v2 v2.36 → v2.37 MINOR bump 동반 (kind:registry sibling sync 면제, ADR-010 §결정 2 + ADR-008 §결정 3 — 신규 entry append = MINOR).
- ADR-008 §결정 3 정합 (kind:registry MINOR rule). plugin.json bump 0 → ADR-063 marketplace atomic invariant 미발효 (mirrored field 무변경, `marketplace_sync_declared: false`).
- `bootstrap-labels.sh` 변경 0건 (CFP-598 dynamic registry-driven pattern — L165-191 `parse-hotfix-bypass-labels.py` 가 §3 yaml read auto-emit, registry append 만으로 양 entry 자동 처리).

### Related

- ADR-72 §결정 1 + §결정 5 (CFP-954 carrier — ProductionEvidenceDeputy mandate first activation declare layer + Epic close-time quad-check evidence aggregation)
- ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합 (45번째 (raw) family member)
- ADR-024 Amendment 6 §결정 6.A.2 historical-with-template-count convention first precedent (`hotfix-bypass:exempt:<entry>` 32번째 template) — 본 Amendment 10 convention divergence 영역 (raw 채택, historical 미답습)
- ADR-024 Amendment 9 (CFP-963 — codex-sandbox-substitution 44번째 historical convention) — convention scope disjoint 영역
- ADR-010 §결정 2 + ADR-008 §결정 3 (kind:registry sibling sync 면제 + MINOR append rule)
- ADR-082 §결정 1 (write-time verify-before-trust 4-layer disjoint) — 본 Story Tier-A 확정의 anchor (RequirementsPL §2 verified state synthesis 영역)
- ADR-064 §결정 1 (CFP scope unitary) — Tier-B CFP #1004 분리 결정 anchor
- ADR-054 (doc-only fast-path — 1 PR + Phase split 없음 + 구현 lane skip)
- ADR-058 §결정 5 정합 (is_transitional:false 영구 governance, ratchet-up 강화 방향, sunset_justification_required:false)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.36 → v2.37 MINOR (CFP-1000 — 45번째 (raw) `hotfix-bypass:prod-cutover-deputy-evidence`)
- `docs/inter-plugin-contracts/MANIFEST.yaml` label-registry-v2 row "2.36" → "2.37"
- `scripts/bootstrap-labels.sh` 변경 0건 (CFP-598 dynamic registry-driven pattern — L165-191 `parse-hotfix-bypass-labels.py` 가 §3 yaml read auto-emit)
- `templates/github-workflows/bootstrap-labels.yml` (CFP-662 baseline — PR open 시 auto-run 의무 발효 영역, `hotfix-bypass:inter-plugin-contracts-parity` gh-side 등록 mechanism)
- CLAUDE.md L295 prose "44번째 = `hotfix-bypass:prod-cutover-deputy-evidence` (CFP-954)" 인용 = 본 Story OOS (CFP-954 PR-time historical attribution invariant 보존, Tier-B CFP #1004 reconciliation 영역)

## Amendment 11 — Tier-B 4-way sync bidirectional drift sweep (Wave 1): 47-50번째 (raw) family member + 1 naming mismatch resolution (CFP-1006, 2026-05-19 KST)

### 결정 6.A 호환 확장 — Tier-B 4-way sync bidirectional drift sweep (Wave 1)

CFP-1000 (Tier-A) 가 1 registered-but-not-declared entry (`prod-cutover-deputy-evidence`) registry-side late codify 으로 Tier-A 영역 close — Tier-B 영역 (35 registry→gh missing + 5 gh→registry missing + 1 naming mismatch = 41 raw drift, Issue body CFP-1000 retro 2026-05-19 morning verification 값) 은 별 CFP carrier 분리 (ADR-064 §결정 1 CFP scope unitary 정합 + CFP-963 retro escalation candidate). 본 Amendment 11 = CFP-1006 carrier 영역 Tier-B Wave 1 (gh→registry missing 5 entries + 1 naming mismatch).

**Pivot finding (write-time)**: pre-spawn verify-before-trust 시점 (`84ed75b2` HEAD pinned) verified state:
- 1 entry shifted between morning verification (Issue body 35 registry→gh + 6 gh→registry = 41) ↔ pre-spawn verify (36 registry→gh + 5 gh→registry = 41 raw drift, 41 total invariant)
- 5 of 5 gh→registry missing 모두 legitimate operational provenance 보유 (3 with backing CFP carrier / 2 with 11-12+ PR audit-trail evidence)

**4 신규 entry registry-side late codify** (gh→registry missing direction):

1. **`hotfix-bypass:comment-prefix-registry`** (registered-but-not-declared): gh repo ≥ 12 PR audit-trail (Issue #1011 bypass-counter signature reach 12+ evidence). registry §3 yaml 미선언. Operational scope = comment-prefix-registry-v1 contract version bump governance ceremony (ADR-008 contract MINOR/PATCH) conditional skip. Backing CFP carrier = CFP-845 Amendment 8 §결정 6.A.4 historical (v1.3 `[bypass-justification]` 14번째 prefix 신설 시 사용). No dedicated workflow file (pure governance audit-trail channel).
2. **`hotfix-bypass:epic-cutover-quad-check`** (registered-but-not-declared): gh repo pre-existing + `docs/evidence-checks-registry.yaml:1441` + `ADR-72:36` provenance. registry §3 yaml 미선언. Operational scope = production-touching Epic-cutover PR 4-tuple evidence quad (live_touching / production_cutover_touching / marketplace_publish_touching / consumer_impact_blast_radius) check skip. Backing carrier = ADR-72 §결정 1/§결정 5 (Wave 4 sub-Epic #882 Story-3, CFP-954). Workflow = `production-cutover-evidence.yml`. wrapper-self-app Tier-1 declare-time 면제 invariant 보존.
3. **`hotfix-bypass:evidence-naming`** (registered-but-not-declared): gh repo pre-existing + `docs/evidence-checks-registry.yaml:1053` + `scripts/lib/check_evidence_registry_naming.py:160` + `templates/github-workflows/evidence-registry-naming-check.yml:30` provenance. registry §3 yaml 미선언. Operational scope = evidence-checks-registry.yaml row name convention warning-tier lint skip. Backing = ADR-060 framework.
4. **`hotfix-bypass:markdown-internal-links`** (registered-but-not-declared): gh repo ≥ 11 PR audit-trail (Issue #1013 bypass-counter signature reach 11+ evidence). registry §3 yaml 미선언. Operational scope = doc-only fast-path PR forward reference 영역 / planned-but-deferred docs 미실재 ADR placeholder 인용 시 broken-link detection lint skip. No dedicated workflow file (general doc maintenance lint scope).

**1 naming mismatch resolution** (conservative direction — registry §3 entry rename to match gh repo + workflow filename + 12+ PR audit history):

- **PREVIOUS** registry §3 entry name: `hotfix-bypass:claude-md-amendment-ref` (CFP-708 originally / never registered in gh repo with this name)
- **NEW** registry §3 entry name: `hotfix-bypass:claude-md-amendment-ref-drift`
- **Conservative direction rationale**:
  1. gh repo label is `claude-md-amendment-ref-drift` (with `-drift` suffix) — actively used in 5+ PR bypass annotations
  2. Workflow file is `templates/github-workflows/claude-md-amendment-ref-drift.yml` (with `-drift` suffix) — matches gh repo label naming
  3. Workflow lint detection scope = "CLAUDE.md Amendment ref drift" — semantic of `-drift` suffix preserved
  4. registry §3 entry name `claude-md-amendment-ref` (no suffix) was never instantiated in gh — rename = registry-side 0 effect on gh repo (no `gh label delete` + `gh label create` required, no PR audit-trail invalidation)
- **Convention compatibility**: `§4 변경 규칙` "v2.x append-only" + "기존 label 삭제 또는 이름 변경은 v3.0 BREAKING" rule 호환 → 본 rename = exception 영역 (rename target never-instantiated, gh-side 0 effect, no contract consumer impact). v2.39 MINOR 정합 (append-only invariant 보존, rename-of-never-instantiated-entry = effective no-op for gh consumers).

**Family member ordinal positions (raw active concrete grep count convention 답습 = CFP-1000 Amendment 10 precedent)**:

- Pre-edit raw count (84ed75b2): 47 unique `hotfix-bypass:*` entries in §3 yaml (46 active + 1 `exempt:<entry>` template)
- Post-edit (CFP-1006 v2.39):
  - 23번째 family member position preserved → renamed `hotfix-bypass:claude-md-amendment-ref-drift` (historical attribution invariant)
  - 47번째 = `hotfix-bypass:comment-prefix-registry` (new)
  - 48번째 = `hotfix-bypass:epic-cutover-quad-check` (new)
  - 49번째 = `hotfix-bypass:evidence-naming` (new)
  - 50번째 = `hotfix-bypass:markdown-internal-links` (new)
- Post-edit raw count: 51 unique entries (50 active + 1 `exempt:<entry>` template)

### 결정 6.A.2 호환 — bypass-as-norm-mutation 누적 카운터 (per-entry namespace)

`scripts/check-bypass-label-counter.py` (CFP-825 / Amendment 6 §결정 6.A.2) lint 가 본 Amendment 11 4 신규 entry 부착 PR 누적 시 자동 escalation Issue 생성 (warning-tier). 본 Amendment 11 = `comment-prefix-registry` (12+ reach 기존 Issue #1011) + `markdown-internal-links` (11+ reach 기존 Issue #1013) 영역 이미 escalated — 본 registry §3 late codify 가 escalation Issue history invalidate 아니라 codification carrier 영역 (ADR-024 Amendment 6 §결정 6.A.2 ratchet rule audit-trail 정합).

### 결정 6.A.3 호환 — per-plugin scope 누적 카운터 (CFP-845 Amendment 8 §결정 6.A.3)

본 Amendment 11 = `mclayer/plugin-codeforge` plugin scope 단독 — `scripts/check-per-plugin-cumulative-counter.py` 누적 4 신규 entry 부착 시 자동 escalation Issue 생성 영역 (warning-tier).

### Convention re-anchor — raw active concrete grep count 답습

CFP-1000 Amendment 10 = raw active concrete grep count convention 채택 (Amendment 9 CFP-963 historical-with-template-count convention 과 disjoint). 본 Amendment 11 = CFP-1000 Amendment 10 답습 — 47/48/49/50번째 = post-edit grep count - 1 (50 active 신규 끝 = 50번째). Convention divergence 영역 없음 (Amendment 10 노선 단일 유지).

### Effective behavior

- v2.39 MINOR bump 후 hotfix-bypass:* 가족 50 활성 entry (51 raw, 1 `exempt:<entry>` template). 본 Amendment 11 = 23 entry rename + 47-50번째 (raw) 4 신규 entry append.
- `templates/github-workflows/bootstrap-labels.yml` PR open 시 auto-run — 4 신규 labels gh-side idempotent invariant (gh API 422 already-exists swallow / 201 created — depend on per-label, 4 of 4 entries 이미 gh-side active 따라서 모두 422 already-exists swallow).
- `scripts/bootstrap-labels.sh` 변경 0건 (CFP-598 dynamic registry-driven pattern — L165-191 `parse-hotfix-bypass-labels.py` 가 §3 yaml read auto-emit, registry append + rename 만으로 5 entry 자동 처리).
- `claude-md-amendment-ref` 23번째 family member rename → `claude-md-amendment-ref-drift` 효과 = `parse-hotfix-bypass-labels.py` 출력 name field 갱신 (rename 적용). bootstrap-labels.yml auto-run 시 gh repo 에서 `claude-md-amendment-ref-drift` label 이미 존재 (5+ PR 부착 이력) → 422 already-exists swallow. **registry-side rename 효과 = gh-side 0 effect (rename target never-instantiated in gh)**.
- **35 of 36 registry→gh missing 자동 해소 expected** — bootstrap-labels.yml workflow PR open 시 fire → `parse-hotfix-bypass-labels.py` § yaml read → **51 entries emit** (50 active + 1 `exempt:<entry>` template; parser filter is ONLY `category == 'hotfix-bypass'` per L92-121, NO template-name skip logic — F-DR-1006-1 mechanistic correction) → `create_label` 호출 → 36 entries 중 35 entries 가 gh repo `gh api 201 created` 발효 (1 entry = `exempt:<entry>` template 가 gh API 에서 literal `<entry>` placeholder 로 인해 silently rejected at create-label time). 4 신규 entry (47-50번째) = 4 of 4 이미 gh-side active 따라서 422 already-exists swallow.
- 1 of 36 registry→gh missing 자동 해소 미지 영역: `exempt:<entry>` template = **gh API silent rejection at `gh label create` time** (NOT parser-side skip; parser emits all 51 entries — F-DR-1006-1 mechanistic correction. gh API silently rejects literal `<entry>` placeholder during create-label invocation, effective gh-side outcome = template never persisted in gh repo).

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1~10 전부 유지 — 본 Amendment 11 = Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 47-50번째 (raw) family member append + 23번째 rename) only.
- ADR-060 framework 외 영역 (4 core required check + 기존 evidence check + Amendment 1~10 entry) 에는 영향 X.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 11 = forbid scope 확장 (4 신규 family member append) = ratchet-up 강화 방향, sunset_justification_required: false.
- `§4 변경 규칙` v2.x append-only invariant 호환 (rename target never-instantiated in gh, exception 영역). MAJOR v3.0 BREAKING 회피 (ADR-008 §결정 3 정합).

### Related

- ADR-024 Amendment 10 (CFP-1000 — Tier-A 1 entry registry-side late codify, 45번째 (raw)) — 본 Amendment 11 = Tier-B Wave 1 carrier (35 + 5 = 41 raw drift 영역 sweep)
- ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합 (47-50번째 (raw) family member)
- ADR-024 Amendment 6 §결정 6.A.2 (bypass-as-norm mutation 누적 카운터 — Issue #1011 + Issue #1013 evidence)
- ADR-024 Amendment 8 §결정 6.A.3/6.A.4 (per-plugin scope + bypass-justification marker 정합)
- ADR-008 §결정 3 정합 (kind:registry MINOR rule). plugin.json bump 0 → ADR-063 marketplace atomic invariant 미발효 (mirrored field 무변경, `marketplace_sync_declared: false`).
- ADR-010 §결정 2 (kind:registry sibling sync 면제)
- ADR-082 Amendment 2 §2.1 (`issue_origin: orchestrator_authored_followup` — CFP-1000 retro PMOAgent-authored Tier-B carry-forward, §3.17 4-step procedure 적용)
- ADR-064 §결정 1 (CFP scope unitary) — Tier-B Wave 2/Wave 3 (registry→gh sync verify + sync drift lint) 분리 결정 anchor
- ADR-054 (doc-only fast-path — 1 PR + Phase split 없음 + 구현 lane skip)
- ADR-058 §결정 5 정합 (is_transitional:false 영구 governance, ratchet-up 강화 방향, sunset_justification_required:false)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.38 → v2.39 MINOR
- `docs/inter-plugin-contracts/MANIFEST.yaml` label-registry-v2 row "2.38" → "2.39"
- `scripts/bootstrap-labels.sh` 변경 0건 (CFP-598 dynamic registry-driven pattern)
- `templates/github-workflows/bootstrap-labels.yml` (CFP-662 baseline — PR open 시 auto-run 의무 발효 영역, 35 registry→gh missing 자동 해소 expected)
- ADR-077 §결정 5 reinvestigation_tracking 정합 (본 Story §1 verbatim claim 검증 → §2.1 verified state table 10 row mandatory)
- Issue #1011 (`comment-prefix-registry` 12+ reach bypass-counter) + Issue #1013 (`markdown-internal-links` 11+ reach bypass-counter) — bypass-as-norm mutation evidence anchors
- CLAUDE.md L295 prose 인용 = 본 Story OOS (Tier-B CFP #1004 reconciliation 영역)

## Amendment 12 — Tier-B Wave 2: registry→gh backfill + Wave-1 auto-resolve assumption FALSIFICATION + bootstrap token-permission/error-mask root cause codify (CFP-1025, 2026-05-19 KST)

### 결정 6.A 호환 확장 — Tier-B 4-way sync bidirectional drift sweep (Wave 2: registry→gh direction closure)

CFP-1006 Amendment 11 = Tier-B Wave 1 (gh→registry 5 entries + 1 rename, registry §3 late codify). Amendment 11 §"Effective behavior" L1071-1072 asserted: "35 of 36 registry→gh missing 자동 해소 expected — bootstrap-labels.yml workflow PR open 시 fire → 35 entries 가 gh repo `gh api 201 created` 발효". 본 Amendment 12 = **해당 assumption 의 empirical FALSIFICATION 기록 + 진짜 root cause codify + registry→gh direction (35 missing) 의 owner-context backfill 으로 Tier-B Wave 2 영역 close**. registry §3 content 변경 0건 (label-registry-v2 v2.39 retain — 본 Amendment 12 = 신규 family member append 아님, root-cause/process codification only → 신규 ordinal 없음).

### Pivot finding (write-time, ADR-070/ADR-082 §결정 1 verify-before-trust) — Wave 1 auto-resolve FALSIFIED

CFP-1006 Wave 1 의 "bootstrap-labels.yml CFP-598 dynamic pattern 이 PR open 시 35 registry→gh missing 자동 해소" assumption 은 **실측으로 거짓 입증** (memory `feedback_wave_defer_empirical_verify` — deferred Wave 의 auto-resolve assumption 은 predecessor close 전 empirical verify 의무):

- bootstrap-labels.yml DID fire on CFP-1006 PR (run `26080174058`, 2026-05-19T06:23:45Z, conclusion=success)
- gh `hotfix-bypass:*` count = **15 — UNCHANGED** (auto-resolve 0 effect)
- run log: NO `PyYAML 미설치 SKIPPED` line (Orchestrator pre-spawn PyYAML hypothesis **REFUTED** — runner=`ubuntu-24.04`, PyYAML present, parse succeeded, all 50+ entries enumerated)
- 모든 `gh label create` (hotfix-bypass:* AND base labels `audit:spec-amendment`/`channel:beta` 포함) = `! <name>: create/edit 실패 (권한 문제 가능)`

### Root cause (CONFIRMED) — token-permission gap + `2>/dev/null` error-mask

1. **Token gap (ROOT)**: `bootstrap-labels.yml` token = `secrets.CODEFORGE_CROSS_REPO_PAT || secrets.GITHUB_TOKEN`. `CODEFORGE_CROSS_REPO_PAT` IS set (secret updated 2026-05-14) → PAT in effect. 해당 PAT 는 ADR-066/CFP-450 에서 phase-gate-mergeable + rate-limit-fallback-kpi 용도로 provisioned — **label-write (Issues: write on `mclayer/plugin-codeforge`) 미포함** (fine-grained PAT repo-allowlist / permission-set 영역 외). 대조: 사용자 admin `gh` (admin:true) probe `gh label create` + `gh label delete` SUCCEEDED → backfill feasible via owner context.
2. **Error-mask (META-ROOT)**: `scripts/bootstrap-labels.sh:53-55` `create_label()` 의 `2>/dev/null` 가 실제 HTTP 403/404 error 를 삼킴 → generic `권한 문제 가능` + 오인성 `Bootstrap completed successfully` (script `exit 0` + workflow `continue-on-error: true`). **이 masking 이 CFP-1006 mis-diagnosis + Wave-defer false-confidence 의 직접 원인.**
3. Issue #1025 candidate causes (a) PR-diff-scoped loop / (b) conditional `gh label create` loop / (c) bulk-vs-incremental logic gap — **3 전부 REFUTED** (parse emits all 51, loop full-registry-scoped, all attempted).

### Effective behavior (Wave 2 closure)

- **`scripts/bootstrap-labels.sh` `create_label()` error-unmask** (production script — Phase 2): `2>/dev/null` → captured-stderr; terminal failure 시 captured `gh` error verbatim echo. control flow (`create || edit || fail-echo`) + exit semantics 불변. `--dry-run` branch (L48-51) untouched → `LABEL_COUNT` 2-way self-check parity 보존 (`check-bootstrap-labels-count.sh` 영향 0).
- **bootstrap-labels.yml false-success visibility step** (byte-identical pair, ADR-005): post-Bootstrap non-fatal step 가 stdout 의 `^  ! .*: ` 실패 line count → 임계 초과 시 `::warning::bootstrap-labels: N label create/edit FAILED — token may lack Issues:write (ADR-066 / CFP-1025)`. `continue-on-error: true` + warning tier 보존 (chicken-and-egg / required-check regression 0).
- **35 registry→gh missing owner-context backfill** (operational, idempotent, one-time): 사용자 admin `gh` context (probe-proven). NOT via CI (token-blocked — 재-fire 는 동일 실패; 이 반복이 정확히 falsified Wave-defer). `gh label create` 멱등 (already-exists → `gh label edit` no-op/benign). `hotfix-bypass:exempt:<entry>` template 제외 (gh API 가 literal `<entry>` placeholder reject — gh-side never persisted; 50 active = 51 raw − 1 template).
- registry §3 content / label-registry-v2 version 변경 0건 (v2.39 retain). plugin.json bump 0 → ADR-063 marketplace atomic invariant 미발효, `marketplace_sync_declared: false`.

### Residual (user-domain, accepted — AC-5)

`CODEFORGE_CROSS_REPO_PAT` 가 `Issues: write` on `mclayer/plugin-codeforge` 획득하기 전까지 (ADR-066, 사용자 secret-domain) CI mechanism 은 future registry→gh drift self-heal 불가. 본 Amendment 12 backfill = one-time manual reconcile. Wave 3 sync-drift lint (별 CFP, ADR-064 §결정 1 unitary) 는 PAT remediate 전까지 detection-only. 문서화된 accepted residual — 본 Story blocker 아님.

### Compatibility

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1~11 전부 유지 — 본 Amendment 12 = root-cause/process codification (신규 family member append 0, 신규 ordinal 0).
- ADR-058 §결정 5 sunset_justification — 본 Amendment 12 = process visibility 강화 (error-unmask = ratchet-up 방향, scope 약화 0), `is_transitional: false` 영구 governance, `sunset_justification_required: false`.
- ADR-005 byte-identical workflow pair invariant 호환 (post-edit `diff templates/github-workflows/bootstrap-labels.yml .github/workflows/bootstrap-labels.yml` = empty 의무).
- 본 Amendment 12 = src 변경 동반 (production `scripts/bootstrap-labels.sh`) → doc-only fast-path (ADR-054) **미적용** → full-lane (Phase 1 design + Phase 2 impl).

### Related

- ADR-024 Amendment 11 (CFP-1006 — Tier-B Wave 1, gh→registry 5 + rename) — 본 Amendment 12 = Tier-B Wave 2 (registry→gh 35 + root cause)
- ADR-005 (templates/ ↔ .github/ byte-identical workflow invariant)
- ADR-066 / CFP-450 (`CODEFORGE_CROSS_REPO_PAT` rotation/scope — label-write 미포함 = 본 Story 의 underlying gap, user secret-domain follow-up)
- ADR-070 (verify-before-trust — post-merge verify 가 falsification surface + write-time PyYAML hypothesis refute)
- ADR-082 Amendment 2 §2.1 / §3.17 (`issue_origin: orchestrator_authored_followup` — CFP-1006 retro PMOAgent-authored, 4-step procedure)
- ADR-064 §결정 1 (CFP scope unitary — Wave 3 sync-drift lint 별 CFP)
- ADR-054 (doc-only fast-path — src 변경 동반으로 미적용, full-lane)
- CFP-598 / CFP-662 (dynamic registry-driven bootstrap pattern — 구조적으로 sound, token-blocked)
- memory `feedback_wave_defer_empirical_verify` (deferred Wave auto-resolve assumption empirical-verify 의무 — 본 Story 의 lineage 교훈) + `feedback_architect_script_behavior_claim_verify` (script-behavior claim 실측 의무 — root cause = script behavior)
- `scripts/bootstrap-labels.sh` `create_label()` L53-55 (Phase 2 error-unmask target)
- `templates/github-workflows/bootstrap-labels.yml` + `.github/workflows/bootstrap-labels.yml` (Phase 2 byte-identical visibility-step pair)

## Amendment 14 — `hotfix-bypass:parallel-anchors-checked-presence` 92번째 (raw active concrete grep count post-append, v2.67 late-comer rebase) family member + §결정 6.A.7 신설 (CFP-1306, 2026-05-25)

### Context

CFP-1306 Wave 3 mechanical lint enforcement — review-verdict-v4 v4.9 (CFP-1303) 에서 신설된 `findings[].parallel_anchors_checked[]` optional array field 의 presence-grep heuristic lint (`scripts/check-parallel-anchors-checked-presence.sh` + Python SSOT). ADR-060 Amendment 15 §결정 29 13번째 warning-tier entry 의 bypass channel 신설 의무. late-comer rebase invariant (ADR-050 §결정 1): CFP-1367 PR #1517 먼저 머지됨 (90번째+91번째 family member) → CFP-1306 = 92번째 (v2.67) rebase 완료.

### Amendment

**92번째 (raw active concrete grep count post-append, rebase base v2.66 = 91 → 91 + 1 = 92) hotfix-bypass:* family member `hotfix-bypass:parallel-anchors-checked-presence` per-entry namespace 신설 + §결정 6.A.7 (신설)**.

#### §결정 6.A.7 (신설) — `hotfix-bypass:parallel-anchors-checked-presence` per-entry namespace

`hotfix-bypass:parallel-anchors-checked-presence` label 는 PR 에 attach 시 `parallel-anchors-checked-presence` warning-tier lint 를 bypass. audit comment `[bypass-audit] parallel-anchors-checked-presence: <rationale>` 의무 (§결정 6.A audit-trailed exception channel).

- color `fef2c0` (warning tier, audit channel)
- description = "hotfix-bypass: parallel-anchors-checked-presence — bypass review-verdict-v4 findings[].parallel_anchors_checked[] field presence-grep heuristic lint (CFP-1306 / ADR-060 Amendment 15 §결정 29 / ADR-068 I-2 Wave 3 enforcement). Attach [bypass-audit] comment with rationale. **92번째 hotfix-bypass:* family member (ADR-108 forcing function parity mandate — raw active concrete grep count post-append = 91 + 1 = 92 정합, late-comer rebase: CFP-1367 90+91번째 선점 → CFP-1306 = 92번째 v2.67). CFP-1306 Bundle A.A1 carrier.**"

### Count convention 답습

본 Amendment 14 = raw active concrete grep count convention 답습 (CFP-1000 Amendment 10 precedent + CFP-1346 ADR-108 §결정 3 forcing function parity mandate).

- **Raw active concrete grep count**: `^  - name: hotfix-bypass:` direct grep pre-edit (v2.66 rebase base, CFP-1367 merged) = 91 → post-edit (v2.67) = 92 (post-append parity).
- **ADR-108 §결정 3 META self-app 9th applied case** (이전: CFP-1346 1st + CFP-1384 2nd + CFP-1429 3rd + CFP-1489 4th + CFP-1497 5th + CFP-1500 6th + CFP-1502 7th + CFP-1510 8th + 본 CFP-1306 = 9th applied case).

**late-comer rebase invariant 완료 (ADR-050 §결정 1)**: CFP-1367 PR #1517 먼저 머지됨 (90번째+91번째) → CFP-1306 = v2.67 (92번째 family member) rebase 완료.

### ADR-082 §결정 9 verify-at-write-time 적용 evidence

rebase 후 origin/main `HEAD 8b50316` 안 `docs/inter-plugin-contracts/label-registry-v2.md` frontmatter `version: "2.66"` + `^  - name: hotfix-bypass:` raw grep count `91` 직접 verify (ADR-070 verify-before-trust, CFP-1367 PR #1517 merge 반영).

### 영향

- ADR-024 §결정 1~6 + Amendment 1~13 전부 유지 — 본 Amendment 14 = Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 92번째 family member append + §결정 6.A.7 신설).
- label-registry-v2 v2.66 → v2.67 MINOR bump 동반 (1 신규 entry append + frontmatter `version: "2.67"` ratchet, kind:registry sibling sync 면제 ADR-010 §결정 2 + ADR-008 §결정 3 row append).
- MANIFEST.yaml row `"2.66"` → `"2.67"` ratchet 동반 (INV-1 parity).
- plugin.json bump 0 = `marketplace_sync_declared: false`.
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 14 = forbid scope 확장 (92nd family member append) = ratchet-up 강화 방향.

### 관련 파일

- ADR-060 Amendment 15 §결정 29 — enforcement source (dual-binding)
- ADR-068 I-2 — declaration source (cross-module propagation completeness)
- review-verdict-v4 v4.9 — schema carrier (CFP-1303)
- CFP-1306 Bundle A.A1 — carrier Story
- ADR-108 §결정 3 forcing function parity mandate (raw active concrete grep count post-append parity)

## Amendment 13 — `hotfix-bypass:pre-existing-main-drift-bundle` macro label 89번째 (raw active concrete grep count post-append) family member + §결정 6.A.6 신설 (CFP-1510, 2026-05-25)

### Context

CFP-1389 lineage 마지막 follow-up (FU-Wave3-C). pre-existing main drift 영역 8 sentinel hotfix-bypass labels (closed-set: bootstrap-labels / actionlint / claude-md-amendment-ref-drift / markdown-internal-links / inter-plugin-contracts-parity / fix-event-depth-scope / sibling-pr-author-check / wording-dictionary) 가 동일 root cause (pre-existing main drift) 영역 closed-set 임에도 batch attach mechanism 부재 → 매 PR 마다 8 individual hotfix-bypass labels 를 manual attach 의무 (PR 8개 가정 시 64 manual attachments 누적). audit overhead 비대.

**Efficiency target**: 64 manual attachments (8 PR × 8 label) → 8x reduction (1 macro attach = 8 label auto-fan-out via macro-label-expander workflow).

### Amendment

**89번째 (raw active concrete grep count post-append, base v2.64 = 88 → 88 + 1 = 89) hotfix-bypass:* family member `hotfix-bypass:pre-existing-main-drift-bundle` macro label 신설 + §결정 6.A.6 (신설) macro label batch attachment audit-trailed exception channel codify**.

#### §결정 6.A.6 (신설) — Macro label batch attachment audit-trailed exception channel

**Macro label semantics**: 단일 `hotfix-bypass:pre-existing-main-drift-bundle` label attach 시 macro-label-expander workflow 가 8 underlying labels (closed-set) 를 auto-fan-out attach.

**Closed-set 8 underlying labels** (pre-existing main drift super-class sentinel):

| # | Underlying label | Root carrier |
|---|---|---|
| 1 | `hotfix-bypass:bootstrap-labels` | CFP-662 / ADR-060 Amendment 10 §결정 24 |
| 2 | `hotfix-bypass:actionlint` | CFP-688 / ADR-026 Amendment 3 §결정 5.G.b |
| 3 | `hotfix-bypass:claude-md-amendment-ref-drift` | CFP-708 / ADR-074 (CFP-1006 v2.39 rename precedent) |
| 4 | `hotfix-bypass:markdown-internal-links` | CFP-1006 v2.39 §결정 6.A 50번째 family member |
| 5 | `hotfix-bypass:inter-plugin-contracts-parity` | CFP-894 / ADR-010 INV-1 parity warning-tier lint |
| 6 | `hotfix-bypass:fix-event-depth-scope` | CFP-842 / ADR-067 Amendment 1 §결정 4 |
| 7 | `hotfix-bypass:sibling-pr-author-check` | CFP-521 / ADR-066 sibling PR author check |
| 8 | `hotfix-bypass:wording-dictionary` | CFP-610 / ADR-064 Amendment 2 |

**Audit pattern**: single audit comment block (예: `[bypass-audit] pre-existing-main-drift-bundle: <rationale>`) 가 8 underlying labels 모두에 대해 audit-trail rationale 충족 — 기존 single audit lint `scripts/check-bypass-audit-comment.sh` (CFP-389 prior art) reuse, 신규 lint 도입 0건.

**Wave 1 / Wave 2 분리** (ADR-064 §결정 1 CFP scope unitary 정합):

- **Wave 1 (본 Amendment 13)** = declarative codify — (a) label-registry-v2 §3 macro label entry append + (b) `templates/github-workflows/macro-label-expander.yml` Wave 1 stub (`if: false` disabled) + (c) `.github/workflows/macro-label-expander.yml` self-app byte-identical (ADR-005 invariant).
- **Wave 2 (별 sub-CFP carrier)** = mechanical hydrate — workflow `if: false` 제거 + `pull_request.labeled` / `issues.labeled` event trigger wire + 8 underlying labels mechanical attach script + audit comment fan-out logic + bats fixture pair.

**Audit invariant 보존**: macro = batch-attach mechanism only. 8 underlying labels 의 individual lint enforce 영역 무변경 (각 lint workflow 가 자기 lint scope 안에서 attached underlying label presence detect → workflow conditional skip → audit comment 자동 발의). macro attach 가 enforce 약화 0건 — audit trail invariant 보존.

#### `hotfix-bypass:pre-existing-main-drift-bundle` Macro Label

- color `fef2c0` (warning tier, audit channel)
- description = "hotfix-bypass: pre-existing-main-drift-bundle macro label — single attach expands to 8 individual hotfix-bypass labels via macro-label-expander workflow (CFP-1510 / ADR-024 Amendment 13 §결정 6.A.6). Closed-set 8 underlying labels: bootstrap-labels / actionlint / claude-md-amendment-ref-drift / markdown-internal-links / inter-plugin-contracts-parity / fix-event-depth-scope / sibling-pr-author-check / wording-dictionary. Efficiency target: 64 manual attachments (8 PR × 8 label) → 8x reduction. Wave 1 declarative — workflow stub `if: false`, Wave 2 hydrate carrier 별 sub-CFP. **89번째 hotfix-bypass:* family member (ADR-108 forcing function parity mandate — raw active concrete grep count post-append = 88 + 1 = 89 정합). CFP-1389 lineage 마지막 follow-up FU-Wave3-C**."
- single_active: false
- attach_owner_plugin: "Orchestrator (CFP-1510 macro label batch attachment — pre-existing main drift unified channel, 사용자 직접 / Orchestrator 직접 attach 시 Wave 2 expander workflow 가 8 underlying labels auto-fan-out)"

### Count convention 답습

본 Amendment 13 = **raw active concrete grep count convention** 답습 (CFP-1000 Amendment 10 precedent + CFP-1346 ADR-108 §결정 3 forcing function parity mandate META self-application).

- **Raw active concrete grep count**: `^  - name: hotfix-bypass:` direct grep pre-edit (v2.64 baseline) = 88 → post-edit (v2.65) = 89 (post-append parity).
- **ADR-108 §결정 3 META self-app 7th applied case**: CFP-1346 1st + CFP-1384 2nd + CFP-1429 3rd + CFP-1489 4th + CFP-1497 5th + CFP-1500 6th + CFP-1502 7th + 본 CFP-1510 = 8th applied case (raw active grep count 88 + 1 = 89 정합).

### ADR-082 §결정 9 verify-at-write-time 적용 evidence

본 Amendment 13 write-time 에 ADR-082 §결정 9 verify-at-write-time mandate 적용 — task prompt 의 `post-CFP-1502 Wave 2-D = v2.64` 주장을 worktree base (HEAD pin `6515df1eae5299255d30ef689105b7902eb07653`) 안 `docs/inter-plugin-contracts/label-registry-v2.md` frontmatter `version: "2.64"` + `^  - name: hotfix-bypass:` raw grep count `88` direct read 로 verify (ADR-070 verify-before-trust). main repo divergent state (v2.51, raw 72) ignored — worktree-base SSOT 정합.

### 영향

- ADR-024 §결정 1~6 + Phase 2 partial (CFP-70) + CFP-72 + Amendment 1~12 전부 유지 — 본 Amendment 13 = Amendment 3 §결정 6.A 의 호환 확장 (per-entry namespace 89번째 family member append + §결정 6.A.6 신설 audit pattern 확장).
- label-registry-v2 v2.64 → v2.65 MINOR bump 동반 (1 신규 entry append + frontmatter `version: "2.65"` ratchet, kind:registry sibling sync 면제 ADR-010 §결정 2 + ADR-008 §결정 3 row append).
- MANIFEST.yaml row `"2.64"` → `"2.65"` ratchet 동반 (INV-1 parity).
- plugin.json bump 0 = `marketplace_sync_declared: false` (lint+workflow 신설 = governance behavior 변경이나 plugin.json mirrored field 무변경, ADR-063 atomic invariant 발효 조건 미충족).
- ADR-058 §결정 5 sunset_justification ratchet — 본 Amendment 13 = forbid scope 확장 (89th family member append + §결정 6.A.6 신설) = ratchet-up 강화 방향, `sunset_justification_required: false`.

### 산출물 (Wave 1 declarative)

- `docs/inter-plugin-contracts/label-registry-v2.md` — frontmatter `version: "2.65"` + §3 macro label entry append
- `docs/inter-plugin-contracts/MANIFEST.yaml` — `registries[label_registry][file:label-registry-v2.md].version` `"2.64"` → `"2.65"`
- `docs/adr/ADR-024-story-scoped-branch-policy.md` — 본 Amendment 13 + frontmatter `amendment_log` row + `mechanical_enforcement_actions` row + `related_files` row (macro-label-expander.yml)
- `docs/adr/ADR-RESERVATION.md` — Amendment id slot reservation row (Amendment 13)
- `templates/github-workflows/macro-label-expander.yml` — Wave 1 stub (`if: false` disabled)
- `.github/workflows/macro-label-expander.yml` — self-app byte-identical (ADR-005 invariant)
- `CLAUDE.md` — 본 Amendment 13 cross-ref 1줄
- internal-docs Story (`plugin-codeforge/stories/CFP-1510.md`) + Change Plan (`plugin-codeforge/change-plans/cfp-1510-fu-c-macro-label.md`)

### 관련 파일

- ADR-024 §결정 6.A (CFP-389 Amendment 3 — audit-trailed exception channel SSOT)
- ADR-024 §결정 6.A.2 ~ 6.A.5 (CFP-825 / CFP-845 sub-decision precedents — per-entry / per-plugin / narrative / cross-repo escalation)
- ADR-024 Amendment 10 (CFP-1000 — registry-side late codify pattern + raw count convention)
- ADR-024 Amendment 9 (CFP-963 — historical-with-template-count convention precedent)
- ADR-108 §결정 3 forcing function parity mandate (raw active concrete grep count post-append parity — META self-app 7th applied case)
- CFP-389 prior art `scripts/check-bypass-audit-comment.sh` (audit comment lint reuse)
- CFP-1389 lineage retro (pre-existing main drift super-class identification + FU-Wave3-C 마지막 follow-up)
- ADR-005 templates/ ↔ .github/ byte-identical workflow invariant
- ADR-010 §결정 2 kind:registry sibling sync 면제
- ADR-008 §결정 3 row append (kind:registry 영역)
- ADR-058 §결정 5 sunset_justification (ratchet-up 강화 방향)
- ADR-064 §결정 1 CFP scope unitary (Wave 1 / Wave 2 분리 정합)
- ADR-070 verify-before-trust (worktree base v2.64 / 88 raw verify-at-write-time)
- ADR-082 §결정 9 verify-at-write-time (frontmatter version + raw grep count direct read evidence)

