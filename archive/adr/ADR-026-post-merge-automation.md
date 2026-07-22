---
adr_number: 26
title: Post-merge follow-up automation — wrapper Orchestrator workflow + cross-repo Story writer (telemetry only)
status: Accepted
category: Team & Process
date: 2026-05-04
carrier_story: CFP-74
related_files:
  - templates/github-workflows/post-merge-followup.yml
  - .github/workflows/post-merge-followup.yml                                  # Amendment 1 — byte-identity invariant §결정 5.B mirror
  - scripts/post-merge-story-writer.sh
  - scripts/post-merge-sibling-close.sh
  - scripts/post-merge-telemetry.sh
  - scripts/next-phase.sh
  - tests/workflows/test_post-merge-followup-yml.sh                            # Amendment 1 — Phase 2 PR scope (CFP-545: Block A 4 assertion 추가, 39 → 43 PASS)
  - tests/fixtures/post-merge-followup/                                        # Amendment 1 — 12 fixture / Amendment 1 §결정 5.E — fixture 16 추가 (CFP-545: 4 scenario + EC-1/2/3)
  - docs/orchestrator-playbook.md
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md
  - docs/adr/ADR-011-inter-plugin-contract-drift-detection.md
related_stories:
  - CFP-74
  - CFP-476   # Amendment 1 carrier — PR-Issue close trigger algorithm + line 47 stale 정정 + byte-identity invariant §결정 5.B
  - CFP-545   # Amendment 2 §결정 5.E + §결정 5.F unified carrier — Action 1 strict regex + concurrency.group namespace prefix
  - CFP-546   # §결정 5.F absorbed (concurrency.group namespace, framing errata) — standalone PR 폐기, CFP-545 안 통합 (Codex 종합 리뷰 2026-05-13)
  - CFP-688   # Amendment 3 §결정 5.G carrier — workflow file integrity safeguards (actionlint pre-commit hook + CI step + canary deploy mandate + KPI registry warning-tier sentinel)
  - CFP-795   # Amendment 4 §결정 6 carrier — post-merge-fix phase-gate fast-pass exemption (3-조건 AND: post-merge-fix label + hub Story §10 binding + 원 MERGED PR §7 보안 non-touch 역참조)
  - CFP-900   # Amendment 5 §결정 7 carrier — `.github/` fast-pass content sanity 1차 신호 orthogonal warning layer (Wave 4 sub-Epic CFP-858 S3, Epic 마지막 Story. fast-pass OR-gate 무변경 + content mismatch warning emit 1단 추가. ADR-076 Amendment 3 §결정 3 sub-clause sibling)
  - CFP-1059  # Amendment 6 §결정 8 carrier — Epic close → Deploy trigger hook (codeforge-deploy lane 신설 정합, ADR-087 §결정 6 sibling carrier). post-merge automation 영역 확장 (PR merge / Issue close transition 외 Epic close transition trigger 추가, declaration-only Wave 1)
amendment_log:
  - date: 2026-05-12
    carrier: CFP-476
    section: "§결정 5 (신설) + §결정 1 (line 47 inline 정정)"
    summary: "PR-Issue close trigger algorithm 정식화 — dual-source AND (PR body close keyword regex ∩ Issue closedByPullRequestsReferences) + terminal-phase gate (phase:보안-테스트 / phase:구현-테스트 consumer config 분기) + multi-issue audit (single carrier + skip + [multi-match-skip] marker) + cross-repo qualified syntax skip + security T1/T2 env indirection + byte-identity invariant (§결정 5.B). 결정 1 line 47 stale terminal phase (phase:완료) → phase:보안-테스트 default / phase:구현-테스트 (lanes.security_ai: false) 정정. CFP-391 / CFP-412 / CFP-455 false-positive close 3-Story 누적 패턴 차단."
  - date: 2026-05-13
    carrier: CFP-545
    section: "Amendment 2 — §결정 5.E (신설) + §결정 5.F (신설, CFP-546 absorbed)"
    summary: "Amendment 2 = 2 sub-decision unified — (5.E) Action 1 (Phase label transition) Issue resolution 영역의 strict regex matching 의무화 — CFP-476 hotfix scope 외 잔존 결함 (line 96 bare search + inline `${{ ... }}` shell expansion) closure. `in:title` qualifier + jq post-filter `^${STORY_KEY}\\\\b` word boundary + env indirection (`env: STORY_KEY`) 의무. prior art SSOT = `retro-mandatory.yml` lines 162-166 verbatim mirror. semantic 분리 — 5.E 는 Issue title regex (5.A 는 PR body regex, 별개). T2 HIGH 잔존 영역 (Action 1 inline shell expansion) 동시 해소 — §결정 5.D 정합 강화. CFP-541 Epic A 1주 SLA emergency hotfix child #2. (5.F) concurrency.group key namespace clarity 강화 — `${{ github.repository }}` prefix 의무 (CFP-546 worktree content absorbed). CFP-476 retro §4.1 carrier #8 원문 'cross-repo number collision' framing 부정확 — GitHub Actions concurrency scope = repository-level verified (Discussion #78332). 진짜 사유 = namespace clarity / sibling consistency / forward-compat. 6 sibling sweep cross-ref = CFP-569 carrier (별도). retro errata = CFP-568 carrier (별도). Codex 종합 리뷰 (2026-05-13) 권고 정합 — CFP-546 standalone PR 폐기, ADR 내용만 본 Amendment 2 안 통합."
  - date: 2026-05-15
    carrier: CFP-688
    section: "Amendment 3 — §결정 5.G (신설)"
    summary: "Amendment 3 = workflow file integrity safeguards SSOT — CFP-688 carrier (post-merge-followup.yml 100% FAILURE born-broken state, 17h 18min, 100/100 FAILURE, P0 hotfix). 4 sub-결정 통합: (5.G.a) inline Python heredoc grace policy explicit — ADR-061 §결정 1 strict default 유지 + workflow yml 안 inline ≤ 25 lines + `bash -n` PASS + `actionlint` PASS 3-key 정합 시 grace (본 fix 가 외부 `scripts/extract-security-ai.sh` 분리 path 채택, ADR-061 strict 적용으로 grace clause 미발효 — declarative path 만 명시). (5.G.b) actionlint pre-commit hook 도입 + CI step (prevention layer) — `templates/.git-hooks/pre-commit.sample` 안 actionlint step opt-in + `.github/workflows/actionlint-check.yml` + `templates/github-workflows/actionlint-check.yml` byte-identical mirror 신설 (ADR-005 정합). born-broken 재발 차단의 mechanical forcing function. (5.G.c) canary deploy mandate — post-merge 첫 sister PR merge wait + 5 action outcome telemetry live verify (workflow run conclusion success/no_op enum verify, AC-9 deliverable). (5.G.d) KPI registry warning-tier 9번째 entry `post-merge-followup-workflow-success-rate` — sentinel rolling 14-day window, success rate ≥ 90%, ADR-060 framework 정합 + hotfix-bypass channel `hotfix-bypass:post-merge-followup-success-rate` (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). sunset_justification 면제 — ratchet 강화 방향 (Amendment 1 algorithmic invariant + Amendment 2 strict regex / namespace 보존 + §결정 5.G integrity safeguards 추가, ADR-058 §결정 5 정합). 본 Amendment 3 = fail-to-run defect fix only 아닌 새 design layer 도입 (workflow file integrity governance = 3-layer chain — silent dead detection + prevention layer + canary detection layer)."
  - date: 2026-05-16
    carrier: CFP-795
    section: "Amendment 4 — §결정 6 (신설) + §결정 2 (cross-repo PAT scope read 정합 cross-ref)"
    summary: "Amendment 4 = post-merge-fix phase-gate fast-pass exemption SSOT — CFP-795 carrier (mctrader consumer MCT-183 Phase 2 PR1 post-merge hotfix mctrader-data#71 trigger, cross-repo Story land_order 후 발견된 safe defect 의 정정 PR 이 phase-gate-mergeable.yml 의 PR-label-only fallback 추론으로 구조적 무한 BLOCK = consumer admin override / 불필요한 보안테스트 lane 재실행 강요 = escalate-and-fix 철학 / enforce_admins:true invariant 위배). §결정 6 (신설) = phase-gate-mergeable.yml 의 기존 3-source fast-pass OR-gate (isEpicLabel || isSiblingPr || isDocOnly) 에 4번째 source isPostMergeFix 추가 — 단순 라벨 단독 통과 금지, 3-조건 AND gate: (조건 1) post-merge-fix label 존재 (조건 2) hub Story §10 FIX Ledger 에 해당 hotfix PR 을 가리키는 row binding 존재 (cross-repo audit trail, Orchestrator monopoly fix-event-v1 contract CFP-32) (조건 3) 정정 대상 원(MERGED) PR 이 §7 보안 영역 non-touch (3a 원 PR 변경 파일 보안경로 non-match ∧ 3b hotfix PR 자체 변경 파일 보안경로 non-match — SecurityArch 양면 강화, revert 가 보안 패치 무력화 차단 = 역참조). 옵션 1 단독 (단순 라벨 exemption) 거부 = self-declare 위조 → 보안테스트 우회 attack surface (4 에이전트 독립 수렴). 옵션 3 단독 (admin-override 정책화) 거부 = enforce_admins:true invariant 정면 충돌 + escalate-and-fix 위배 — 단 consumer 즉시 unblock 의 interim-only 경로 (hotfix-playbook §3 사후 감사 trail + admin-override-with-justification) 는 정책 아닌 운영 fallback 으로 유효. 조건 2 cross-repo read 는 phase-gate-mergeable.yml 의 기존 story_uri PR-body marker + CODEFORGE_CROSS_REPO_PAT contents fetch 메커니즘 (L31-90) 재사용 — internal-docs hub Story §10 read 는 기존 PAT contents:write scope 가 read 포함하므로 충족 (§결정 2 cross-ref, scope 확장 불요). fail-closed default (판정 불가 = BLOCK 유지, false-negative 보안우회 < false-positive 불필요BLOCK). label-registry-v2 post-merge-fix entry MINOR + plugin.json MINOR (ADR-063 atomic 3-file + marketplace.json sync). is_transitional: false 유지 — sunset_justification 면제 = ratchet 강화 방향 (fast-pass 3-source → 4-source 는 gate 강화이며 약화 아님; 조건 2/3 AND 가 옵션 1 단순 라벨보다 엄격, ADR-058 §결정 5 정합). 본 Amendment 4 = ADR-024 enforce_admins:true invariant 보호 (admin override 정상화 거부) + escalate-and-fix 철학 실행 (consumer workaround 금지, 정책 기반 자동 gate pass). **Codex TP#2 inline FIX (2026-05-17, verified-true P1)**: §3.2 (hub Story §10 read) 에 hub repo 화이트리스트 (`ALLOWED_HUB_REPOS` workflow env / plugin config 주입, PR body derive 금지) 의무 추가 — story_uri spoofing forged §10 row attack 차단. zero-trust anchor. consumer overlay `phase_gate.allowed_hub_repos[]` 확장 가능 (ADR-026 Amd 4 §결정 6 (화이트리스트) + ADR-024 Amendment 2 §결정 A (확장-only 패턴) + ADR-116 (주입 mechanism) 축소 불가). ADR-052 Amendment 4 P1 mandatory inline FIX 이행."
  - date: 2026-05-20
    carrier: CFP-1059
    section: "Amendment 6 — §결정 8 (신설)"
    summary: "Amendment 6 = Epic close → Deploy trigger hook 신설 (codeforge-deploy lane 신설 정합 carrier — ADR-023 Amendment 1 + ADR-087 신설 sibling). post-merge automation 영역 확장 — 기존 post-merge follow-up trigger (PR merge transition + Issue close keyword transition Amendment 1 dual-source AND + post-merge-fix phase-gate fast-pass Amendment 4 §결정 6 + `.github/` fast-pass content sanity Amendment 5 §결정 7) 위에 Epic close transition trigger 1단 추가 — Epic Issue closed + `gate:retro-complete` label 동시 활성 시 DeployPL spawn hook fire (production cutover-touching Epic 한정, wrapper-self-app N/A). declaration-only Wave 1 — Phase 2 PR scope (`templates/github-workflows/epic-close-deploy-trigger.yml` + `scripts/check-epic-close-deploy-trigger.sh` + evidence-checks-registry row append). consumer-side gating layer = ADR-083 §결정 1 4-way enum closed-set (consumer 영역만 hook fire, wrapper-self-app `mixed`/`plugin` repo skip). ratchet 강화 방향 — post-merge automation trigger 4-source → 5-source 확장 + Epic close transition trigger 신규 channel 추가 (약화 0건). is_transitional: false 보존."
  - date: 2026-05-18
    carrier: CFP-900
    section: "Amendment 5 — §결정 7 (신설)"
    summary: "Amendment 5 = `.github/` fast-pass content sanity 1차 신호 orthogonal warning layer SSOT — CFP-900 carrier (Wave 4 sub-Epic CFP-858 S3, Epic 마지막 Story. ADR-076 Amendment 3 §결정 3 result fidelity sub-clause sibling carrier). Epic CFP-858 §1 부가 결함 verbatim: phase-gate-mergeable.yml 의 `.github/` 경로 fast-pass (isDocOnly line 180 `f.filename.startsWith('.github/')` + isSiblingPr line 173) 가 file path prefix match 만 수행 → workflow yml 안 의존 script reference (`run: bash scripts/check-*.sh` / `python3 templates/scripts/*.py`) content 비정합 silent pass → consumer 가 'fast-pass PASS = 안전' 오인 후 머지 → 전체 CI 마비 P0급 피해 (현재는 close 로 회피). §결정 7 (신설) = fast-pass OR-gate (isEpicLabel || isSiblingPr || isDocOnly || isPostMergeFix) 위 orthogonal content sanity warning layer 1단 추가 — 변경된 `.github/workflows/*.yml` 안 의존 script reference 가 동일 PR diff 안 OR repo 안 존재하는지 mismatch detect (S1 closure resolver CFP-898 §4.11 의 phase-gate-mergeable layer mirror — mirror-time vertical vs gate-time signal, layer 분리 invariant). severity = warning tier (AM-1 derived default — fast-pass PASS 자체 보존, fast-pass 정책 약화 = ADR-064 ratchet 위배 회피, content mismatch 시 1차 warning emit + PR comment). fast-pass OR-gate 자체 변경 0 invariant (orthogonal warning layer = gate 강화 방향, ADR-026 Amendment 4 §결정 6 3-source → 4-source ratchet 강화 패턴 답습 — gate 약화 0). blocking 승격 = evidence-checks-registry tier 승격 gate AND condition 충족 후 future CFP separate (CFP scope unitary ADR-064 §결정 1.3). is_transitional: false 유지 — sunset_justification 면제 = ratchet 강화 방향 (orthogonal warning layer 1단 추가 = gate 강화이며 약화 아님, ADR-058 §결정 5 정합, CFP-795 Amendment 4 동형). mechanical_enforcement_actions[] entry `post-merge-fix-fast-pass-content-sanity-signal` append (status: declaration-only-Wave-1, ADR-082 §결정 6 + ADR-070 §D5 패턴 답습 — Phase 2 PR 시점 phase-gate-mergeable.yml content sanity assertion + tests/workflows/ fixture 가 mechanical detection 책임). reconcile-protocol-v1 v1.9 → v1.10 §4.13 `result_fidelity_binding.fast_pass_content_sanity` field = mechanical declare / 본 ADR §결정 7 = semantic declare 분리 (CFP-743/744/745/820/821/898/899 §결정 본문 vs binding block 분리 패턴 답습). 신규 ADR 미신설 — S3 = ADR-026 Amendment 5 + ADR-076 Amendment 3 ratchet 강화로 충분 (S1 ADR-076 Amendment 2 / S2 ADR-083 신규 와 비대칭, Architect lane minimal-change 결정, ADR-RESERVATION row 84 reserve 불요)."
  - date: 2026-05-21
    carrier: CFP-1125
    section: "Amendment 7 — Amendment 5 sibling carrier role 만 sunset (declarative boundary, β2 audit Anchor 3 carry-over)"
    summary: "Amendment 7 = Amendment 5 sibling carrier role 만 sunset boundary declarative SSOT — CFP-1125 carrier (β2 audit #1113 Anchor 3 LOSSLESS 판정 carry-over). 본체 §결정 1-6 (post-merge automation SSOT — PR merge transition / Issue close keyword transition / Cross-repo PAT / Telemetry only / Disable-by-flag safety + PR-Issue close algorithm Amendment 1 / Action 1 strict regex + concurrency namespace Amendment 2 / Workflow file integrity Amendment 3 / Post-merge-fix phase-gate fast-pass Amendment 4 §결정 6 / Epic close → Deploy trigger Amendment 6 §결정 8) = sunset 대상 아님 (PR-merge gate 로직 자체 별 lifecycle 작동). 본 Amendment 7 = Amendment 5 §결정 7 의 sibling carrier role 만 sunset boundary 명시 — reconcile-protocol-v1 §4.13 result_fidelity_binding 의 declarative carrier_story CFP-900 sibling 역할이 CFP-1111 walker paradigm 전환 후 walker walk_result 4-value enum (SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED) 으로 carry. PR-gate layer 독립 보존 invariant — phase-gate-mergeable.yml `.github/` content sanity warning layer 는 walker paradigm 과 disjoint 별 lifecycle. is_transitional: false 보존 (본체 sunset 아님 + sibling carrier role 만 sunset 영역 분리 — 부분 sunset declarative, ADR-058 §결정 5 정합). frontmatter 값 변경 0 (carrier_story / related_stories / supersedes / superseded_by / is_transitional). 해소 기준 3-tuple (metric / who / how) = walker schema field walk_result + exit_code_to_walk_result_mapping rule + walker integration test 4-value enum honest record verify + PR-gate layer 독립 작동 확인. β2 audit Anchor 3 carry-over 3 설계 주의 #2 정합 (sunset 영역 = sibling carrier role 만, 본체 §결정 1-6 sunset 아님)."
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.A schema 정합 — list[object] verbatim entry name + status + progress_note + target_section
  # 본 mechanical_enforcement_actions[] field 도입 = CFP-688 Amendment 3 §결정 5.G binding (ADR-040 Amendment 3 §결정 7.A 정합)
  - action: workflow-actionlint-precommit
    status: active
    progress_note: "Phase 2 sub-PR (c) 완료 — actionlint-check.yml + templates mirror (byte-identical, ADR-005) + templates/.git-hooks/pre-commit.sample opt-in hook + evidence-checks-registry 54번째 entry (warning tier, 2026-05-15). hotfix-bypass channel = `hotfix-bypass:actionlint` (label-registry-v2 v2.17 24번째 family member). ADR-026 §5.G.b 승격 target = blocking-on-pr (별도 CFP carrier 의무)."
    target_section: §결정 5.G.b
  - action: post-merge-followup-workflow-success-rate-kpi
    status: active
    progress_note: "Phase 2 sub-PR (c) 완료 — post-merge-followup-success-rate-kpi.yml + templates mirror (byte-identical, ADR-005) + scripts/check-post-merge-followup-success-rate.sh + evidence-checks-registry 55번째 entry (warning tier, 9번째 warning-tier entry, 2026-05-15). hotfix-bypass channel = `hotfix-bypass:post-merge-followup-success-rate` (label-registry-v2 v2.17 25번째 family member). 14-day measurement window 진입 중."
    target_section: §결정 5.G.d
  - action: post-merge-fix-fast-pass-3-condition-gate
    status: deferred-followup
    progress_note: "CFP-795 Amendment 4 §결정 6 carrier. mechanical enforce = phase-gate-mergeable.yml + .github/workflows/phase-gate-mergeable.yml (byte-identical, ADR-005) 의 4번째 fast-pass source isPostMergeFix (3-조건 AND: post-merge-fix label ∧ hub Story §10 row binding ∧ 원 MERGED PR §7 보안 non-touch 양면). Phase 2 PR (구현 lane) 가 workflow Actions script 구현 + tests/workflows/ fixture (8-조합 truth table + fail-closed + self-application 회귀) carrier. evidence-checks-registry entry 신설 불요 — phase-gate-mergeable.yml 자체가 required status check (branch protection 1번째) 로 이미 mechanical gate, 본 4번째 source 는 그 gate 의 fast-pass 분기 확장 (별도 lint/sentinel 영역 아님). 본 entry 는 ADR-040 Amendment 3 §결정 7.A schema 정합용 declarative binding (Phase 2 구현 완료 시 status: active 전환)."
    target_section: §결정 6
  - action: post-merge-fix-fast-pass-content-sanity-signal
    status: declaration-only-Wave-1
    progress_note: "CFP-900 Amendment 5 §결정 7 carrier (Wave 4 sub-Epic CFP-858 S3, Epic 마지막 Story). mechanical enforce = phase-gate-mergeable.yml + .github/workflows/phase-gate-mergeable.yml (byte-identical, ADR-005) 의 `.github/` fast-pass (isDocOnly line 180 / isSiblingPr line 173) 위 orthogonal content sanity warning layer — 변경 `.github/workflows/*.yml` 안 의존 script reference (`run: bash scripts/check-*.sh` / `python3 templates/scripts/*.py`) 가 동일 PR diff 안 OR repo 안 존재 mismatch detect, warning tier (fast-pass OR-gate 무변경). Phase 2 PR (구현 lane) 가 phase-gate-mergeable.yml content sanity assertion 구현 + tests/workflows/test_phase-gate-mergeable-yml.sh content sanity 1차 신호 assertion + self-application 회귀 fixture carrier. evidence-checks-registry entry 신설 불요 — fast-pass content sanity = orthogonal warning emit (fast-pass OR-gate 자체는 이미 required status check, 본 layer 는 그 위 advisory warning 1단). 본 entry 는 ADR-040 Amendment 3 §결정 7.A schema 정합용 declarative binding (declaration-only-Wave-1 — ADR-082 §결정 6 + ADR-070 §D5 declaration-only retain 패턴 답습, CFP-898/CFP-899 precedent 정합. Phase 2 구현 완료 시 status: active 전환). reconcile-protocol-v1 v1.10 §4.13 result_fidelity_binding.fast_pass_content_sanity field = mechanical declare cross-ref."
    target_section: §결정 7
supersedes: null
superseded_by: null
is_transitional: false
---

# ADR-026: Post-merge follow-up automation

## 상태

Accepted (2026-05-04). carrier_story = CFP-74. codeforge productivity round 2.

## 컨텍스트

CFP-73 (round 1) Phase 1 (ADR-025 정책 명확화) land 후 사용자 동일 호소 verbatim 재발 (2026-05-04). ADR-025 §결정 1 invariant ("Sonnet decides → automatic proceed") 가 land 됐음에도 stop 빈도 감소 미실현.

Codex+Claude+Sonnet round 2 진단 = primary root cause = **(a) Post-merge manual actions**. 사용자 admin merge 후 Story §9 PASS write + phase label transition + Issue close + sibling PR close 4-5 manual stops per merge. CFP-73 4 PR × 4 actions ≈ 16+ stops 누적 직접 evidence.

Sonnet decider (CFP-74-001) pick=`alpha` (Candidate I single PR + Candidate III telemetry bundling).

## 결정 요약

### 결정 1 — Wrapper Orchestrator post-merge follow-up automation 의무

PR merge event 시 4 action 순차 자동 처리:
1. **Phase label transition** — carrier Issue 의 `phase:*` label 다음 phase 로 transition
2. **Story §9 writer** — internal-docs `wrapper/stories/<KEY>.md` §9 row append (decider:user_admin marker)
3. **Issue close** — terminal phase 도달 시 carrier Issue 자동 close (terminal phase = `phase:보안-테스트` default / `phase:구현-테스트` if `lanes.security_ai: false`. 본 ADR Amendment 1 §결정 5.A — CFP-476 정정. **이전 본문 `phase:완료` 는 stale — playbook line 228 SSOT 와 부정합, CFP-455 retro 발견**)
4. **Sibling PR auto-close** — archive marker (`Closed (deferral)` 등) sibling PR 자동 close

각 action 은 idempotent (workflow 재실행 시 중복 처리 안 함).

### 결정 2 — Cross-repo PAT (CFP-71 precedent + ADR-011 정합)

internal-docs 측 cross-repo write 는 organization secret `CODEFORGE_CROSS_REPO_PAT` 사용:
- scope = `contents:write` only on `mclayer/codeforge-internal-docs`
- 90 day expiration + 사용자 수동 갱신 (CFP-71 §7.3 정합)
- workflow log 자동 mask (gh CLI)

### 결정 3 — Telemetry only (no enforcement)

ADR-022 §결정 11 Phase 1 trust model 정합. workflow 는 follow-up 자동 처리만, **사용자 stop 발화 자체를 차단 / refuse 하지 않음**. 측정 채널 = `<internal-docs>/wrapper/post-merge-counters.jsonl` (JSONL append-only, contract_version 1.0). 30+ run 누적 후 PMOAgent retro 분석 → Phase 2 enforcement 도입 여부 별도 CFP.

stop-event-v1 (CFP-73 deferred) 와의 관계: 본 ADR 의 telemetry counter = lite version (post-merge specific). stop-event-v1 full schema 는 CFP-73 deferral 그대로 잔존. 30+ run 후 통합 평가.

### 결정 4 — Disable-by-flag safety + main 직접 push 금지 invariant

- `.codeforge/post-merge-automation.disabled` file 추가 시 workflow 즉시 정지 (운영 emergency 안전망)
- internal-docs 측 cross-repo write 는 **branch 생성 + PR open** 패턴 — main 직접 push 금지 (사용자 admin merge 패턴 유지)
- 본 invariant 위반 시 ADR-024 story-scoped branch policy 위반 = policy_violation defect

## 대안 검토

### 대안 A — 4 sub-decomposition (β)
- I.a / I.b / I.c / I.d 각각 별도 PR 분리
- 거부 사유: delivery 시간 4배 증가 (각 sub × Phase 1+2 dogfood). root cause 명확하니 incremental 의미 marginal. Sonnet pick reasoning 정합 (CFP-74-001).

### 대안 B — Enforcement 즉시 도입 (γ)
- workflow 가 사용자 stop 발화 자체 차단 / refuse
- 거부 사유: ADR-022 §결정 8 Phase 2 ROI 평가 SSOT 위반. measurement 없이 enforcement 도입 시 over-correction 위험. 사용자 통제 상실 가능성.

### 대안 C — Story file 단순화 (δ)
- §1-12 sections 축소
- 거부 사유: SSOT 파급 범위 부적합. root cause = post-merge manual actions 와 무관.

## 결과

긍정:
- 사용자 admin merge 후 manual 4-5 stops 자동 처리 → 직접 stop 빈도 감소
- ADR-022 §결정 11 Phase 1 trust model 정합 (telemetry only)
- CFP-73 deferral 의도 보존 (stop-event-v1 full schema 미land)
- disable-by-flag + main 직접 push 금지 invariant 로 운영 위험 mitigation

부정:
- workflow 잘못 처리 시 conflict (사용자 manual write 와 동시 발생) — 단 idempotent dedup + branch 명 unique 로 mitigation
- Cross-repo PAT expiration 의무 (90d) — CFP-71 §3.3 runbook 적용

### Reversibility

Yes. `.codeforge/post-merge-automation.disabled` flag 또는 workflow yaml 삭제 시 즉시 기존 manual 동작 복원.

## Out-of-scope

- Enforcement (whitelist 외 stop refusal) — Phase 2 ROI 평가 후 별도 CFP
- stop-event-v1 full schema (CFP-73 deferral 잔존)
- Consumer overlay path support (PMOAgent retro 후)
- Lane plugin self-emit (S3, 후속 CFP)

## 해소 기준

N/A — permanent policy

## 관련 파일

- `templates/github-workflows/post-merge-followup.yml` (workflow)
- `scripts/post-merge-{story-writer,sibling-close,telemetry,next-phase}.sh` (4 scripts)
- `docs/orchestrator-playbook.md` §16 (narrative SSOT)
- `CLAUDE.md` (workflow list 6 → 7)
- `<internal-docs>/wrapper/post-merge-counters.jsonl` (telemetry, first run 후 신설)

## Amendment 1 (CFP-476, 2026-05-12)

### 컨텍스트

CFP-455 retro action_item #1 (severity: blocking, 2026-05-12) — `templates/github-workflows/post-merge-followup.yml` Action 3 (Carrier Issue close, Phase 2 final merge only) PR-Issue matching algorithm 결함이 systemic 으로 발견됨. **3-Story 누적 false-positive close 패턴** (직접 evidence):

| Story | Closed at (UTC) | `closedByPullRequestsReferences` | 분석 |
|---|---|---|---|
| CFP-391 #396 | 2026-05-11 12:32:08Z | `[]` (empty) | PR #400/#403 (debate-protocol-v1 작업) trigger close — GitHub native cross-link 부재, workflow 강제 close |
| CFP-412 #412 | 2026-05-11 15:41:42Z | `[]` (empty) | PR #421 (CFP-393 rate-limit-fallback 작업) trigger close — 동일 패턴 |
| CFP-455 #455 | 2026-05-12 04:25:42Z | `[#460, #461]` | Phase 1 PR #460 merge 시점 (03:06 UTC) 1차 잘못 close → re-open → Phase 2 #461 merge 후 (04:25 UTC) 정상 close |

3 결함 결합: (a) `gh issue list --search "$STORY_KEY"` fuzzy match + `head -1` 비결정적 선택 → false target Issue close. (b) PR title 기반 phase gate (`grep "Phase 2"`) — PR title 안 "Phase 2" 문자열 우연 일치 시 false-positive (Phase 1 PR cross-reference / retro doc / EPIC plan). (c) `phase:완료` (결정 1 본문) stale — playbook line 228 SSOT 와 부정합 (terminal phase = `phase:보안-테스트` default / `phase:구현-테스트` if `lanes.security_ai: false`).

추가 보안 발견 (SecurityArch SubAgent, CFP-476): line 41 `PR_TITLE='${{ github.event.pull_request.title }}'` 및 Action 3 본체 inline `${{ ... }}` shell 삽입 — **T1 CRITICAL** PR body shell injection + **T2 HIGH** PR_TITLE single-quote escape 가능. env indirection (`env: PR_BODY: ${{ ... }}` + `"$PR_BODY"`) 마이그레이션 의무.

본 Amendment 1 = 4 결함 + 2 위협 + 1 stale doc 통합 정정 carrier.

### 결정 5 (신설) — PR-Issue close trigger algorithm 정식화

Action 3 (Carrier Issue close) 알고리즘이 다음 4 sub-결정 (5.A ~ 5.D) 의무.

#### 5.A — dual-source AND semantic + terminal-phase gate

**Source A (PR body close keyword regex)**: GitHub native 9 variant (`close` / `closes` / `closed` / `fix` / `fixes` / `fixed` / `resolve` / `resolves` / `resolved`, case-insensitive) + bare `#N` 또는 qualified `owner/repo#N` 참조.

**Regex notation SSOT — ERE 단일화** (DesignReview FIX iter 1 / F-P1-01 mitigation, 2026-05-12 18:30 KST): 본 ADR-026 §결정 5.A 가 정식 SSOT. POSIX ERE (GNU grep 3.7 `-oE`, ubuntu-latest 검증) — PCRE / Python re / JavaScript notation 금지. 모든 doc surface (Story §2.3/§4.1/§5.2 AC-1/§5.3 EC-9, Change Plan §7.2, fixture yml) 가 본 ERE notation verbatim mirror 의무.

```
(close[sd]?|fix(es|ed)?|resolve[sd]?)[[:space:]]*:?[[:space:]]*(([[:alnum:]_-]+/[[:alnum:]_.-]+)?#[0-9]+)
```

**Source B (Issue closedByPullRequestsReferences API)**: `gh issue view <N> --json closedByPullRequestsReferences` 또는 PR side `closingIssuesReferences` (REST/GraphQL 양쪽 노출).

**판정**: Source A 결과 set X ∩ Source B 결과 set Y. **X ∩ Y 비어있지 않을 때에만 close trigger 발화** (AND). X 또는 Y 부재 / 교집합 비어있음 = `::warning::` + audit comment `[dual-source-mismatch]` + skip (UC-4 / EC-5 fallback). bash 구현 = `comm -12 + process substitution`.

**Terminal-phase gate**: PR label = **terminal phase only**. Consumer config (`.codeforge/project.yaml` 또는 `.claude/_overlay/project.yaml`) `lanes.security_ai` field read (yq → python3 fallback, `templates/github-workflows/story-init.yml` line 37-68 verbatim mirror) — `true` = `phase:보안-테스트` / `false` = `phase:구현-테스트`. **Fail-closed default** = `phase:보안-테스트` (option B, 더 엄격 — consumer config read fail / ambiguous 시 close trigger 차단). 중간 phase (`phase:설계` / `phase:설계-리뷰` / `phase:구현` / `phase:구현-리뷰`) = 차단.

**PR title 기반 phase gate (`grep "Phase 2"`) 폐지** — Issue label re-fetch (PR label 신뢰 X, Action 1 의 `ISSUE_LANE` 패턴 mirror). phase label race condition (Action 1 fail → Action 3 stale label) 시 `[stale-phase-label]` audit + close skip.

#### 5.B — Byte-identity invariant (workflow yml + test harness 양쪽)

`templates/github-workflows/post-merge-followup.yml` 와 `.github/workflows/post-merge-followup.yml` 는 **byte-identical** (mechanical mirror). 신규 test harness `tests/workflows/test_post-merge-followup-yml.sh` 가 `diff -q` 양쪽 assertion 의무. 비교 대상 무한 확장 금지 — Repo-level scope: 2 workflow + 1 test harness만.

**Rationale**: codeforge wrapper 의 self-application 패턴 (post-merge-followup 자체가 wrapper repo 의 Required workflow `target: all` enterprise scope — `templates/required-workflows-spec.yaml` 정합). canonical (`templates/`) ↔ deployed (`.github/`) drift 시 production behavior 가 doc 와 달라지는 결함 차단.

**stale attribution 정정**: 이전 CFP-455 (`tests/CFP-455-TEST-MAPPING.md` line 20 / line 67) 가 본 invariant 의 source 를 ADR-029 ("Phase execution visibility expansion") 로 잘못 attribution. **ADR-029 ≠ byte-identity** (실제 = orchestration narration). 본 §결정 5.B 가 byte-identity 의 정식 SSOT. 신규 reference (CFP-476 이후) = `ADR-026 Amendment 1 §결정 5.B` 사용 의무. 기존 CFP-455 reference 는 prior art chain history 보존 (정정 불요).

**Generalization principle** (DesignReview FIX iter 1 / F-P2-05 채택, 2026-05-12 18:30 KST): 본 byte-identity invariant 패턴은 **canonical SSOT ↔ deployed copy 가 동일 mechanical surface 인 모든 file pair** 에 일반화 적용 가능 — workflow yml 외 script (`scripts/*.sh`) / config (`*.yaml`) / template (`templates/**`) 등. 본 ADR-026 §결정 5.B 의 Repo-level scope (post-merge-followup workflow 2 file + 1 test harness) 가 첫 instantiation. 미래 신규 mirror pair 도입 시 동일 패턴 (test harness `diff -q` assertion + scope-limited 비교 대상) 적용 — 별도 ADR 격리 불필요 (본 §결정 5.B 가 SSOT).

#### 5.C — Multi-match audit + cross-repo skip (single carrier 원칙)

**Multi-issue close detect** (Source A set X 크기 > 1): single carrier + multi-match audit + skip. audit comment 본문 schema:

```
[multi-match-skip] detected_issues=[#N1, #N2, ...] pr=<owner/repo#PR> carrier=#<PR title 첫 CFP key Issue> action=workflow_skip_native_close_delegated manual_follow_up=<true|false>
```

- `carrier` = PR title 안 첫 `[CFP-NNN]` reference 의 Issue (chronological 첫 매칭 아닌 PR title CFP key 기반 — narrative drift 차단)
- `manual_follow_up` = detected_issues 모두 `closedByPullRequestsReferences` 존재 시 `false`, 1+ 누락 시 `true`
- `::warning::` log: `multi-issue close detected — workflow skipping carrier-only close; GitHub native handles all matched issues; manual follow-up may be required for non-native-closed issues.`

**Cross-repo qualified syntax skip**: regex `(?:[\w-]+/[\w.-]+)?#(\d+)` 가 `other-org/other-repo#N` 형식 매칭 → **same-repo limit** (`repo` field 부재 OR `${{ github.repository }}` 일치 시에만 close trigger). cross-repo 감지 시 `::warning::` + audit `[cross-repo-skip] reference=<owner/repo#N> pr=<...> action=skip_cross_repo_unsupported follow_up_carrier=CFP-TBD`. 

본 Story scope 정당화: cross-repo close = `CODEFORGE_CROSS_REPO_PAT` 의존 + workflow `issues: write` same-repo scope only + 사용자 directive "재작성 최소화" 정합. **PMOAgent retro action item 의무**: post-CFP-476 cross-repo follow-up carrier 발의.

**4-marker namespace** (audit comment 본문 prefix): `[close-success]` (정상 close) / `[multi-match-skip]` / `[cross-repo-skip]` / `[dual-source-mismatch]`. 기존 close-success comment 도 marker prefix 보유 의무 (AC-2 grep 통일).

#### 5.D — Security T1/T2 mitigation + concurrency lock + permissions 정정

**T1 PR body shell injection (CRITICAL)** + **T2 PR_TITLE single-quote escape (HIGH)** mitigation: `env:` indirection 의무. `env: PR_BODY: ${{ github.event.pull_request.body }}` + `env: PR_TITLE: ${{ github.event.pull_request.title }}` → shell 안 `"$PR_BODY"` / `"$PR_TITLE"` 참조. inline `${{ ... }}` shell expansion **금지**. Action 3 본체 + 기존 line 41 (Extract PR metadata) 양쪽 동시 마이그레이션 의무 (T2 회귀 차단).

**Shell expansion deeper mitigation** (DesignReview FIX iter 1 / F-P1-05 mitigation, 2026-05-12 18:30 KST): `"$PR_BODY"` / `"$PR_TITLE"` 사용 시 추가 invariant:
- **금지 패턴**: 백틱 `` `$PR_BODY` `` / command substitution `$(...)` 안 PR_BODY 내장 / `eval "$PR_BODY"` / `bash -c "$PR_BODY"`
- **권고 패턴**: `printf '%s' "$PR_BODY"` (raw output, escape interpretation 차단) 또는 awk `BEGIN { line = ENVIRON["PR_BODY"] }` (env 격리 read) — regex 추출 시 `printf '%s' "$PR_BODY" | grep -oE '...'` 패턴 의무
- **rationale**: env indirection 만으로는 shell metachar (`` ` `` / `$()`) escape 미보장 — printf/awk 가 raw byte-level 처리

**AC-16 verify regex 강화** (F-P1-05 mitigation): test harness `tests/workflows/test_post-merge-followup-yml.sh` 가 yq AST query 의무:
- env block 안 `PR_BODY` + `PR_TITLE` 정의 존재 검증 (`yq '.jobs.followup.steps[].env.PR_BODY'`)
- run block 안 inline `${{ github.event.pull_request.body }}` / `${{ github.event.pull_request.title }}` 0회 검증 (grep `'\${{ github.event.pull_request.\(body\|title\) }}'` in run blocks → 0 expected)
- 백틱 / `$()` 안 PR_BODY|PR_TITLE 0회 검증 (정적 grep)

**Concurrency lock — idempotent serialization** (DesignReview FIX iter 1 / F-P1-02 mitigation, 2026-05-12 18:30 KST): workflow yml 안 job-level `concurrency` block 의무:

```yaml
concurrency:
  group: post-merge-followup-${{ github.event.pull_request.number }}
  cancel-in-progress: false
```

**Rationale**: AC-17 `skip_already_audited` idempotency probe 가 audit comment pre-grep 으로 dedupe 보장하지만, GitHub Actions runner 가 동일 PR merge 이벤트로 concurrent workflow run 발생 시 (rare but possible — webhook retry / manual re-trigger) audit comment grep ↔ post 사이 race window 발생 가능. concurrency group = PR number 기반 serialization + `cancel-in-progress: false` = 진행 중 run 보존 (cancel 시 partial state — Issue close 절반 진행 risk). AC-17 verify 항목에 concurrency block 존재 grep 추가.

**Permissions 정정 + 정당화** (DesignReview FIX iter 1 / F-P2-02 채택, 2026-05-12 18:30 KST): job `permissions:`:

| permission | scope | 정당화 |
|---|---|---|
| `issues: write` | Issue close + label transition + audit comment post | Action 1 phase label edit + Action 3 close + 4-marker audit (§5.C) — least-privilege scope 정합 |
| `pull-requests: write` | Action 3 audit comment + Action 4 sibling PR close | audit comment = workflow bot post 채널 (§5.C marker namespace 정합). `read` 만으로는 comment post 불가 — `write` 의무. sibling PR close (Action 4) 도 동일 |
| `contents: read` | `.codeforge/post-merge-automation.disabled` flag + consumer config (`.codeforge/project.yaml` / `.claude/_overlay/project.yaml`) read | terminal-phase gate `lanes.security_ai` field read 필요. write 미필요 (workflow stateless) |
| ❌ `actions: write` | 미부여 | workflow re-trigger 불가 (cascading run 방지) |
| ❌ `id-token: write` | 미부여 | OIDC 미사용 |

`CODEFORGE_CROSS_REPO_PAT` Action 3 미주입 (defense-in-depth — 2-단 cross-repo 차단: app-layer same-repo limit + token-layer 403 fallback).

회귀 fixture 의무: `tests/fixtures/post-merge-followup/pr-title-with-singlequote.yml` (T1+T2 회귀) + `tests/fixtures/post-merge-followup/source-b-lazy-sync.yml` (Source B lazy update retry — F-P1-06).

## Amendment 2 (CFP-545 + CFP-546 absorbed, 2026-05-13)

### 컨텍스트

CFP-541 Epic A (1주 SLA emergency hotfix) 안 child Story 2종 (CFP-545 Action 1 strict + CFP-546 concurrency namespace) 의 ADR scope 가 동일 `ADR-026-post-merge-automation.md` 의 별개 sub-decision 영역으로 분리됨. Codex 종합 리뷰 (2026-05-13) 권고 정합 — CFP-546 standalone PR 가치 평가 결과 ADR namespace 1-line workflow 변경 + framing errata 영역만 보유하므로 별도 Story / PR 분리 불요, CFP-545 의 unified Amendment 2 안에 §결정 5.F 로 통합. CFP-546 Issue 자체는 sibling sweep (CFP-569) 와 grouped open 상태 유지 (audit-trail 보존).

본 Amendment 2 = 2 sub-decision unified:
- **§결정 5.E** (CFP-545 origin) — Action 1 (Phase label transition) Issue resolution 영역의 strict regex matching 의무
- **§결정 5.F** (CFP-546 origin, absorbed) — concurrency.group key namespace clarity (repository prefix)

#### 5.E — Action 1 (Phase label transition) Issue resolution strict regex matching

**Carrier**: CFP-545 (CFP-541 Epic A 1주 SLA emergency hotfix child #2, 2026-05-13)

**컨텍스트**: CFP-476 Amendment 1 §결정 5.A-5.D 는 **Action 3** (Carrier Issue close) 영역의 PR body Source A regex + Issue API Source B dual-source AND 정식화. **Action 1** (line 87-119, Phase label transition) 의 Issue resolution 영역은 hotfix scope 외 — line 96 안 잔존 결함 (CFP-476 retro §3 line 162 CodebaseMapper 발견):

```yaml
# AS-IS (CFP-476 hotfix 외 잔존)
ISSUE_NUM=$(gh issue list --label "type:story" --search "${{ steps.meta.outputs.story_key }}" --json number -q '.[0].number')
```

3 결함:
1. **bare search (no `in:title` qualifier)** — GitHub tokenizer substring match → `CFP-1` query 가 `CFP-506` hit (실측 evidence). false-positive Issue 선택 시 무관한 Story 의 phase label transition.
2. **inline `${{ steps.meta.outputs.story_key }}` shell expansion** — §결정 5.D T2 HIGH mitigation 정합 위반 (env indirection 의무).
3. **no post-filter** — `--search "in:title CFP-545"` 도 tokenization 동작 자체는 동일 (`CFP-545` 가 `CFP-5451` hit) — title regex anchored match (word boundary) 의무.

**결정**: Action 1 (line 87-119) 의 Issue resolution 호출 안 다음 4 요건 의무:

1. **`in:title` qualifier** — search scope 를 title 로 한정 (body / comments 제외)
2. **jq post-filter `^${STORY_KEY}\\\\b`** — word boundary regex 안 정확 prefix-anchored match (CFP-545 vs CFP-5451 collision 차단)
3. **env indirection** — Action 1 env block 안 `STORY_KEY: ${{ steps.meta.outputs.story_key }}` 정의 + run block 안 `"$STORY_KEY"` / `${STORY_KEY}` 참조 (T2 HIGH 해소, §결정 5.D 정합)
4. **null jq 결과 방어** — `[ -z "$ISSUE_NUM" ] || [ "$ISSUE_NUM" = "null" ]` 조건 (jq null literal 방어)

**TO-BE 패턴** (verbatim mirror prior art `templates/github-workflows/retro-mandatory.yml` lines 162-166 — FIX iter 1 F-2 검증 패턴, 운영 중 PASS):

```yaml
- name: Action 1 — Phase label transition
  if: steps.enabled.outputs.disabled != 'true' && steps.meta.outputs.story_key != ''
  id: action1
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    STORY_KEY: ${{ steps.meta.outputs.story_key }}  # T2 mitigation: env indirection (CFP-545 / §결정 5.E)
  continue-on-error: true
  run: |
    # CFP-545: Strict regex matching — prior art retro-mandatory.yml lines 162-166 mirror.
    # Before: gh issue list --search "$STORY_KEY" → CFP-545 vs CFP-5451 prefix collision (GitHub tokenizer)
    # After: in:title qualifier + title regex post-filter (^STORY_KEY\b word boundary) → exact match only
    ISSUE_NUM=$(gh issue list \
      --label "type:story" \
      --search "in:title ${STORY_KEY}" \
      --json number,title \
      --jq "[.[] | select(.title | test(\"^${STORY_KEY}\\\\b\"))] | .[0].number")
    if [ -z "$ISSUE_NUM" ] || [ "$ISSUE_NUM" = "null" ]; then
      echo "::warning::No Issue found for ${STORY_KEY} (in:title exact match)"
      echo "outcome=skip_no_issue" >> $GITHUB_OUTPUT
      exit 0
    fi
    # ... (기존 line 102-119 본문 무변경 — ISSUE_LANE re-fetch + next-phase.sh + transition)
```

**Semantic 분리 (§결정 5.A vs §결정 5.E)**:

| 항목 | §결정 5.A (Action 3 영역) | §결정 5.E (Action 1 영역) |
|---|---|---|
| **Source** | PR body close keyword regex (Source A) ∩ Issue API closedByPullRequestsReferences (Source B) | Issue title regex (single source) |
| **Pattern** | `(close[sd]?|fix(es|ed)?|resolve[sd]?)[[:space:]]*:?[[:space:]]*(([[:alnum:]_-]+/[[:alnum:]_.-]+)?#[0-9]+)` (POSIX ERE) | `^${STORY_KEY}\\\\b` (jq PCRE2 test() — word boundary) |
| **목적** | dual-source AND verify — false-positive Issue close 차단 | Issue resolution strict — fuzzy match / substring collision 차단 |
| **Action** | Carrier Issue close trigger gate | Phase label transition target selection |

두 §결정 모두 동일 root cause 도메인 (GitHub search tokenization fuzzy match) 의 별개 영역 — 5.A 는 close trigger gate, 5.E 는 resolution selection. 분리 SSOT 가 cleaner semantic.

**Byte-identity invariant** (§결정 5.B 적용): `templates/github-workflows/post-merge-followup.yml` 와 `.github/workflows/post-merge-followup.yml` Action 1 변경 시 단일 commit 안 양쪽 동시 갱신 의무. `diff -q` CI assertion (test harness Block A 기존 보유).

**T2 마이그레이션 동반** (§결정 5.D 강화): Action 1 inline `${{ steps.meta.outputs.story_key }}` 잔존 1건 해소 → env indirection 마이그레이션. 본 §결정 5.E carrier (CFP-545) 의 free benefit.

**회귀 fixture 의무**: `tests/fixtures/post-merge-followup/16-action1-fuzzy-substring-collision.yml` (4 scenario):
- SC-1 CFP-545 정상 match (issue_num=545 expected)
- SC-2 CFP-5451 substring collision 차단 (issue_num=skip_no_issue expected)
- SC-3 CFP-54 prefix-only 차단 (issue_num=skip_no_issue expected)
- SC-4 CFP-9999 Issue 부재 skip (issue_num=skip_no_issue expected)
- 추가 Edge case: EC-1 (lowercase `cfp-545` UPPERCASE 정규화 정합) + EC-2 (한글 인접 jq `\b` Unicode boundary empirical verify) + EC-3 (`CFP-05` vs `CFP-5` leading-zero — zero-trimming 없음 verify)

**테스트 harness Block A assertion 4 추가**: env block 안 STORY_KEY 정의 / inline `${{ ... }}` run block 0회 / `in:title ${STORY_KEY}` 패턴 / jq post-filter `^${STORY_KEY}\\\\b` 패턴. 결과: Block A 32 → 36 PASS / 전체 39 → 43 PASS.

**Rollback path**: Phase 2 PR revert 시 Action 1 = 기존 bare search 복원 (Action 3 = 무영향, 분리 design 정합). `.codeforge/post-merge-automation.disabled` flag (§결정 4) 동일 적용.

#### 5.F — concurrency.group key namespace clarity (repository prefix) — CFP-546 absorbed

**Carrier**: CFP-546 origin (Codex 종합 리뷰 2026-05-13 권고 정합 — standalone PR 폐기, CFP-545 의 unified Amendment 2 안에 absorbed)

**Framing errata (verified)**: CFP-476 retro §4.1 carrier #8 (2026-05-13, Codex Touchpoint #4 요구사항 lane anchor2) 가 본 ADR §결정 5.D 의 concurrency.group key (`post-merge-followup-${{ github.event.pull_request.number }}`) 를 **fork PR / cross-repo origin / re-trigger 시 PR number 충돌 risk** 로 분류하며 mitigation 으로 `${{ github.repository }}` prefix 추가 권고. 그러나 CFP-476 retro 원문 "cross-repo number collision" 분석은 부정확. GitHub Actions concurrency.group **scope = repository-level** ([verified] — [GitHub Discussion #78332](https://github.com/orgs/community/discussions/78332): "Concurrency doesn't work for different repos. If you define the same concurrency group key in two different repositories, they will not affect each other — both can run simultaneously without any queueing or cancellation occurring between them."). 다른 repo 에서 같은 group key 사용해도 영향 없음 — cross-repo collision 자체가 발생하지 않음. fork PR 도 base repo context 에서 실행 (`github.event.pull_request.number` = base repo PR number) — same-repo same-PR 케이스로 환원. 본 §결정 5.F 본문 안 errata 영역 보유 (별도 retro errata carrier = CFP-568, retro doc 자체는 history record 보존).

**진짜 정당화** (active amendment 방향, 본 Amendment 2 §결정 5.F 채택):

1. **Namespace clarity** — group key 안 repository identifier 명시 = audit trail debug 친화 (GitHub Actions UI 안 group key 표시 `post-merge-followup-mclayer/plugin-codeforge-501` vs 이전 `post-merge-followup-501`)
2. **Sibling consistency** — codeforge family 6 sibling workflow (auto-phase-label / post-merge-followup / sibling-pr-label-author-check / story-init / retro-mandatory / rate-limit-fallback-kpi) 안 4 deployed + 1 template-only + 1 static 분류 — 동일 패턴 audit-wide expansion 후보 (별도 sibling sweep carrier = CFP-569). 본 §결정 5.F 가 첫 instance, CFP scope unitary 정합 (ADR-064 §결정 1).
3. **Forward-compat** — 미래 `workflow_run` cross-repo trigger / reusable workflow / composite action 통합 패턴 도입 시 group key naming convention 통일성. base repo identifier 명시화가 forward-compat.

**결정**: §결정 5.D concurrency lock 도입 (CFP-476 Amendment 1) 위에 다음 invariant 추가:

`concurrency.group` key 안 **`${{ github.repository }}` prefix 필수** — namespace clarity / sibling consistency / forward-compat 정합.

Before (CFP-476 Amendment 1 §결정 5.D, namespace 모호):
```yaml
concurrency:
  group: post-merge-followup-${{ github.event.pull_request.number }}
  cancel-in-progress: false
```

After (CFP-545 Amendment 2 §결정 5.F, namespace 명시화):
```yaml
concurrency:
  group: post-merge-followup-${{ github.repository }}-${{ github.event.pull_request.number }}
  cancel-in-progress: false
```

**Invariant**:
- `${{ github.repository }}` context variable = owner/repo 형식 (예: `mclayer/plugin-codeforge`) — workflow runtime 에서 항상 base repo 이름 반환 ([verified] — [GitHub Docs Events](https://docs.github.com/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#pull_request) fork PR base repo context)
- group key 안 slash (`/`) 문자 허용 — GitHub Actions concurrency group key string 제약 없음
- `cancel-in-progress: false` 유지 의무 (§결정 5.D invariant 보존 — partial Issue close state 차단)

**대안 거부**:
- 대안 B (`${{ github.repository_id }}` numeric) — debug 친화성 손실, sibling consistency 영역 외. 거부
- 대안 C (`${{ github.event.pull_request.base.repo.full_name }}`) — `github.repository` 와 동일 결과 (workflow 실행 context = base repo) + 더 verbose. 거부

**Queue overflow 동작 명시**: `cancel-in-progress: false` GitHub Actions default 동작 = 진행 중 1 run + pending 1 run max. 3번째 동일 group key run 발화 시 pending 안 기존 대기 run 이 **새 run 으로 대체** ([verified] — [GitHub Docs Control concurrency](https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs) lines 287-292 verbatim: "Note that in the default behavior, if a new run is queued ... and another run is already queued (but not started), the queued run is replaced."). 의미: 마지막 2 run (진행 중 + 가장 최신 pending) 만 실제 실행 + 중간 retry 는 silently dropped. **Action 3 (Carrier Issue close) Step 4 idempotency probe (audit comment grep) 가 dropped run 무영향 보장** — close + audit comment 1번만 실제 post. group key 강화 (repository prefix 추가) 후에도 본 동작 동일 적용 — 변경 전후 same default behavior.

**Byte-identity invariant 보존** (§결정 5.B): `templates/github-workflows/post-merge-followup.yml` ↔ `.github/workflows/post-merge-followup.yml` 양쪽 동시 변경 (`diff -q` exit 0 의무). 기존 test harness `tests/workflows/test_post-merge-followup-yml.sh` Block A-E 32/32 + Block F 15/15 = 39/39 PASS regression 없음 의무 (byte-identity Block A 가 cross-validate). 본 §결정 5.E + §결정 5.F 동시 carrier (CFP-545 Phase 2 PR) 적용 시 Block A assertion 추가 (5.E 4 + 5.F 1 ≥ 5 assertion 추가).

**Mechanical enforcement actions**: 본 §결정 5.F 가 도입하는 mechanical enforcement action 신설 없음 (group key namespace 강화 = workflow internal change, evidence-check entry 영역 외). ADR-040 Amendment 3 §결정 7.C 정합 — 본 §결정 5.F 는 group key 1-line 변경 + ADR doc-only 변경 영역, mechanical enforcement framework 적용 영역 외.

**Retro errata + 6 sibling sweep cross-ref**:
- **CFP-568 (retro errata carrier)**: CFP-476 retro §4.1 carrier #8 원문 "cross-repo number collision" framing 부정확 사실 — 별도 follow-up carrier. retro doc 자체는 history record 보존 (정정 불요), 본 §결정 5.F 본문 안 정정 분석 보유.
- **CFP-569 (6 sibling sweep carrier)**: 6 sibling workflow audit-wide expansion = 별도 sweep carrier. 분류 (4 deployed + 1 template-only + 1 static):
  - 4 deployed (byte-identical mirror 적용): `auto-phase-label.yml` / `post-merge-followup.yml` (본 §결정 5.F carrier) / `sibling-pr-label-author-check.yml` / `story-init.yml`
  - 1 template-only (mirror MISSING — CFP-545 동일 발견): `retro-mandatory.yml` — sibling sweep 진입 전 mirror 신설 선행 의무 (2-step sequence)
  - 1 static key (risk=NO): `rate-limit-fallback-kpi.yml` — single-instance enforced

### 결정 1 (line 47 inline 정정)

본 Amendment 1 §결정 5.A terminal-phase gate 와 정합. 본문 결정 1 step 3 `phase:완료` stale → `terminal phase 도달 시` 정정 (playbook line 228 SSOT 정합). frontmatter `amendment_log[]` row 1 verbatim cross-ref.

## Amendment 3 (CFP-688, 2026-05-15) — workflow file integrity safeguards

### 컨텍스트

`post-merge-followup.yml` workflow 가 CFP-476 Phase 2 merge (commit `5b8e5dc`, 2026-05-13) 이래 **17시간 18분 100/100 FAILURE born-broken state** 발생. `event: push` fallback signature (정상 `event: pull_request` 대신) + `gh run view --log-failed` "log not found" + jobs[] empty = silent dead 의 전형적 fingerprint. CFP-688 (P0 hotfix, sister carrier #689 P1 retro-mandatory.yml L6 mapping regression).

5 critical action (Phase label transition + Story §9 writer + Carrier Issue close + Sibling PR auto-close + Telemetry counter) 모두 silent dead — manual cleanup mandate 가 사람 행동 의존 = ADR-026 mandate 의 design intent (mechanical enforce) 가 normative directive 로 격하 = systemic regression.

Amendment 1 (§결정 5.A-5.D) = algorithmic invariant 정식화 (PR-Issue close trigger) + Amendment 2 (§결정 5.E-5.F) = Action 1 strict regex + concurrency.group namespace prefix. 두 Amendment 모두 **algorithmic / semantic invariant layer**. 본 Amendment 3 = **workflow file integrity governance layer** = 새 design dimension 도입:

1. **silent dead detection layer** — 100/100 FAILURE + `event: push` fallback 의 3-signature fingerprint 검출
2. **prevention layer** — actionlint pre-commit hook + CI step (born-broken 재발 차단 mechanical forcing function)
3. **canary detection layer** — Phase 2 PR merge 직후 첫 sister PR live verify + KPI registry warning-tier sentinel (사후 detection)

본 Amendment 3 = fail-to-run defect fix only 가 아닌 새 design layer (workflow file integrity governance) 의 SSOT.

### 결정 5.G (신설) — Workflow file integrity safeguards

Workflow file (`post-merge-followup.yml` + sibling 5 workflow) 의 YAML parse-time integrity governance — 4 sub-결정 (5.G.a ~ 5.G.d) 의무.

#### 5.G.a — Inline Python heredoc grace policy explicit (ADR-061 §결정 1 localization)

**Default**: ADR-061 §결정 1 strict — multi-line Python (> 5줄 또는 backslash escape 포함) 작성 시 외부 `.py` 또는 `.sh` 파일 분리 의무.

**Grace clause (localized to workflow yml inline scope)**: 본 ADR-026 §결정 5.G.a 안 workflow yml 안 inline Python heredoc (`<<'PY' ... PY` 패턴) 의 grace 영역 = 다음 3-key AND 정합 시:

1. inline ≤ 25 lines (workflow yml self-contained convention 보존)
2. `bash -n .github/workflows/<name>.yml` syntax check PASS
3. `actionlint .github/workflows/<name>.yml` YAML + bash + shellcheck integrate PASS

3-key 모두 PASS 시 inline retain 허용 (ADR-061 strict 면제). 한 key 라도 FAIL 시 외부 분리 의무 (ADR-061 §결정 1 default 환원).

**Rationale**:
- workflow yml 안 inline = self-contained convention (cross-file dependency 차단) 의 value 가 있음 (debug audit trail 친화)
- but actionlint PASS 가 prevention layer (5.G.b) 의 forcing function — grace clause 가 actionlint 의 PASS 의무 binding
- Story §3 / Change Plan §3.3 ADR-061 Amendment 후보 분기에서 inline retain 선택 시 본 grace 영역 적용

**본 Story (CFP-688) 적용**: Phase 2 sub-PR (b) 가 외부 `scripts/extract-security-ai.sh` 분리 path 채택 (ADR-061 strict default + ADR-064 §결정 4 broad coverage 정합). 따라서 본 5.G.a grace clause 미발효 — declarative path 만 명시 (future workflow yml inline 도입 시 grace 영역 reference SSOT).

#### 5.G.b — actionlint pre-commit hook + CI step (prevention layer)

Workflow file YAML parse-time defect 사전 차단 = born-broken 재발 차단 mechanical forcing function.

**1. CI step** (deployed):

`.github/workflows/actionlint-check.yml` + `templates/github-workflows/actionlint-check.yml` 신규 (byte-identical, ADR-005 정합):

- trigger: `pull_request: [opened, synchronize]` with `paths: ['.github/workflows/**', 'templates/github-workflows/**']`
- step: `pip install actionlint==<pinned-version>` → `actionlint .github/workflows/*.yml`
- exit non-zero = fail-closed default (PR merge 차단)

**2. Pre-commit hook** (opt-in):

`templates/.git-hooks/pre-commit.sample` 안 actionlint step 신설:

```bash
# templates/.git-hooks/pre-commit.sample
# actionlint pre-commit hook (CFP-688 Amendment 3 §결정 5.G.b)
if command -v actionlint >/dev/null 2>&1; then
  actionlint .github/workflows/*.yml || exit 1
else
  echo "::warning::actionlint not installed — skipping workflow lint (opt-in install: pip install actionlint)"
  # binary 부재 시 warning emit + bypass (local DX 보존, hotfix-bypass channel)
fi
```

- binary 부재 시 warning emit + bypass (local DX 보존)
- opt-in install (CFP-428 pattern 동등 — wrapper opt-in installer + sample)

**3. Hotfix-bypass channel**: `hotfix-bypass:actionlint` label (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). false positive 또는 emergency hotfix 시 CI step bypass channel.

**Sibling workflow scope**: 본 5.G.b 의 actionlint CI step 은 `.github/workflows/**` 전체 sweep — 6 sibling workflow (auto-phase-label / post-merge-followup / sibling-pr-label-author-check / story-init / retro-mandatory / rate-limit-fallback-kpi) + 신규 actionlint-check.yml + KPI workflow 등 모두 coverage.

**mechanical_enforcement_actions[] binding**: frontmatter `mechanical_enforcement_actions[]` 안 `workflow-actionlint-precommit` entry (status: deferred-followup, target_section: §결정 5.G.b, carrier: CFP-688 Phase 2 sub-PR (b)).

#### 5.G.c — Canary deploy mandate (live verify)

Workflow yml fix 후 즉시 production verify 의무. 본 5.G.c 는 ADR-026 본문 결정 4 (Disable-by-flag safety + main 직접 push 금지) 의 extension.

**Sequence**:

1. Phase 2 sub-PR (b) (workflow yml + hook + tests) merge
2. **첫 sister PR merge wait** (canary trigger) — 본 ADR-026 5 action 발화 trigger 발생
3. workflow run live verify:
   - `gh run list --workflow=post-merge-followup.yml --limit=1 --json conclusion,event,headSha` → `conclusion: success` + `event: pull_request` 의무
   - jobs[] = 1 (followup job)
   - 5 action outcome 각각 명시 (`success` / `no_op` / `skip_*` enum) — log 안 grep 의무
   - aggregate outcome = `auto_completed` / `manual_only` / `partial` 정확 분류
4. Story §9.4 Gate evidence row append (canary verify timestamp + outcome verbatim)

**Fail-closed default**: 첫 sister PR canary 가 FAILURE 시 즉시 Phase 2 sub-PR (b) revert + root cause 재분석 (born-broken 재현 차단).

**AC-9 deliverable mapping**: Story §5.2 AC-9 정합 — canary deploy verification 가 Story §9.4 evidence collection 영역.

#### 5.G.d — KPI registry warning-tier sentinel (post-detection layer)

사후 detection layer — silent dead 재발 시 사용자 visibility 0 차단의 mechanical forcing function.

**Entry**: `post-merge-followup-workflow-success-rate` (warning-tier 9번째 entry, `docs/evidence-checks-registry.yaml`)

**Metric**:

```bash
gh run list \
  --workflow=post-merge-followup.yml \
  --created=>=$(date -u -d '14 days ago' +%Y-%m-%d) \
  --json conclusion \
  --jq '[.[] | select(.conclusion=="success")] | length / (length)' # success ratio
```

**Sentinel**: ≥ 90% rolling 14-day window.

**Sentinel breach 시 action**:
- Issue auto-create (label `hotfix-bypass:post-merge-followup-success-rate` + audit comment)
- KPI workflow cron weekly 발화 (`templates/github-workflows/post-merge-followup-success-rate-kpi.yml`)
- workflow_dispatch ad-hoc trigger 허용

**4-tier framework 정합**: ADR-060 §결정 3 4-tier enum (`warning` / `blocking-on-pr` / `blocking-on-merge` / `hotfix-bypass`) — 본 entry 첫 도입 default = `warning`. 14-day window 누적 + sample sentinel collect 후 별도 CFP (Phase 3 review-promotion) 가 `blocking-on-pr` 승격 결정.

**Hotfix-bypass channel**: `hotfix-bypass:post-merge-followup-success-rate` (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). emergency bypass channel.

**mechanical_enforcement_actions[] binding**: frontmatter `mechanical_enforcement_actions[]` 안 `post-merge-followup-workflow-success-rate-kpi` entry (status: deferred-followup, target_section: §결정 5.G.d, carrier: CFP-688 Phase 2 sub-PR (c)).

### Reversibility (Amendment 3 scope)

- §결정 5.G.b (actionlint hook + CI step): Phase 2 sub-PR (b) revert 시 `actionlint-check.yml` 삭제 + `pre-commit.sample` 안 step revert. CI step 부재 시 born-broken 재발 risk 복원 (ADR-026 Amendment 3 pre-state) — but workflow yml 본체 fix 는 그대로 유지.
- §결정 5.G.c (canary deploy mandate): declarative SSOT만, ADR file revert 가능. 실제 canary deploy 자체는 Phase 2 sub-PR (b) merge 시점에 이미 실행됨 — reversibility 없음.
- §결정 5.G.d (KPI registry warning-tier entry): Phase 2 sub-PR (c) revert 시 registry yaml row 삭제 + workflow + label-registry-v2 row 동시 rollback. workflow 본체 무영향.
- ADR-026 Amendment 3 자체 revert: ADR file revert (workflow / hook 본체 무영향, declarative SSOT 만 revert) — but Amendment 3 의 design intent (workflow file integrity governance layer) 이 normative directive 로 격하.

### Out-of-scope (Amendment 3 scope)

- Sister carrier #689 (`retro-mandatory.yml` L6 mapping regression) — 분리 결정 (RequirementsPL synthesis CL-1 = SEPARATE, Codex R1 concur). 본 Amendment 3 scope 외, distinct root cause.
- Sibling sweep CFP-569 (6 sibling workflow audit-wide expansion of namespace clarity §결정 5.F) — 별 carrier, 본 Amendment 3 scope 외.
- ADR-061 Amendment (workflow yml inline Python heredoc grace period explicit) — 본 §결정 5.G.a 가 localized grace clause 명시, ADR-061 본문 Amendment 불필요 (broad coverage default 정합).
- Wrapper repo Python project 도입 (`unit-tests` / `integration-tests` 활성화) — 분리 Story 후보.

### 해소 기준 (Amendment 3 scope)

N/A — `is_transitional: false` (permanent governance mandate). 본 Amendment 3 = ratchet 강화 방향 (Amendment 1 algorithmic invariant + Amendment 2 strict regex / namespace 보존 + §결정 5.G integrity safeguards 추가) — ADR-058 §결정 5 정합. sunset_justification 면제.

## Amendment 4 (CFP-795, 2026-05-16) — post-merge-fix phase-gate fast-pass exemption (cross-repo land_order 4번째 fast-pass source)

### 컨텍스트

mctrader consumer (mclayer/mctrader-hub governance hub) EPIC-data-domain-decoupling Story-2 (MCT-183 — Layer2 io/ relocation) Phase 2 PR1 진행 중 발견. cross-repo Story (1 Story = N PR, mctrader Mode B hub-centralized) 의 land_order 시퀀스:

- land_order 1: `mctrader-data#70` (io/ 6 module + tests/io/ 수령) MERGED — 정상 phase flow
- land_order 2: `mctrader-engine#58` (io/ + tests/io/ 삭제) MERGED — INV-3 정합
- post-merge: data#70 의 initial relocate commit 에 `ruff --fix F401,SIM105` lint auto-fix 가 의도치 않게 적용 → INV-1 byte-equivalence (Change Plan §3.5/§8.1, "relocate ≠ 재구현, byte-for-byte 동등") 위반 발견 → hotfix PR `mctrader-data#71` (byte-equiv revert + `[tool.ruff.lint.per-file-ignores]`, **신규 코드/로직 0**)

`Phase Gate Mergeable (cross-repo)` workflow (`phase-gate-mergeable.yml`) 가 hotfix PR#71 을 구조적 무한 BLOCK:

> Awaiting: phase=phase:보안-테스트 (current=phase:구현), gate=gate:security-test-pass (current=none) (source: PR labels (no Story binding))

sibling repo Story binding 부재 → `phase-gate-mergeable.yml` L132 `PR labels (no Story binding)` fallback 으로 원 Story terminal phase(보안-테스트)를 추론 → 구조적 무한 BLOCK. consumer 가 (a) admin override governance bypass 또는 (b) 불필요한 보안테스트 lane 재실행을 강요 — 둘 다 codeforge escalate-and-fix 철학 / `enforce_admins:true` invariant (ADR-024 / CFP-70 — admin 도 required check 통과 의무) 위배.

**근본 문제** = "정상 phase flow 로 이미 land 된 PR 의 safe defect 정정"이라는 새로운 작업 클래스에 대한 거버넌스 부재. cross-repo Story 가 보편화될수록 post-merge hotfix 빈도 증가 예상.

Amendment 1 (§결정 5.A-5.D) = PR-Issue close trigger algorithm + Amendment 2 (§결정 5.E-5.F) = Action 1 strict regex / concurrency namespace + Amendment 3 (§결정 5.G) = workflow file integrity governance. 본 Amendment 4 = **phase-gate fast-pass source 거버넌스 layer** = 새 design dimension (이미 정상 land 된 PR 의 safe defect 정정 경로 정식화).

### 거부된 옵션 + 사유 (4 에이전트 독립 수렴)

- **옵션 1 단독 (단순 `post-merge-fix` 라벨 exemption)**: **거부.** label 부착 권한이 곧 fast-pass 권한 → PR author (또는 label 부착 권한자) 가 신규 보안-민감 로직을 `post-merge-fix` 라벨로 위장해 보안테스트를 우회 = self-declare 위조 attack surface (PMO "옵션 1 단독 채택 금지" / Researcher "self-declare 자동통과 보안 우회" / Analyst "자동 신뢰 금지" 독립 수렴). brainstorm Phase 0 incident — Phase 0 agent 1종이 옵션 1 형태 (`isPostMergeFix` 단순 라벨) 를 main 에 직접 박음 → Orchestrator 가 `git stash` (stash@{0}) 격리. 채택 설계는 그 unsafe 형태를 명시적으로 거부, 3-조건 AND 를 처음부터 정식 설계.
- **옵션 3 단독 (admin-override 가이드 명문 = 정책화)**: **거부 (정책으로).** admin override 정상화 = `enforce_admins:true` invariant (ADR-024 / CFP-70) 정면 충돌 + escalate-and-fix 철학 위배. **단** consumer 즉시 unblock 의 **interim-only 운영 fallback** 으로는 유효 — `docs/hotfix-playbook.md §3 사후 감사` trail + admin-override-with-justification 경로 (정책 아님, ADR-027 Amendment 2 §결정 6 action-blocked fallback path 와 동류의 사후감사 운영 채널). 본 Amendment 4 는 정책 채택이 아닌 운영 fallback 으로만 옵션 3 을 허용 — `phase-gate-mergeable.yml` mechanical gate 의 정상 통과 경로는 어디까지나 §결정 6 의 3-조건 AND.

### 결정 6 (신설) — post-merge-fix phase-gate fast-pass exemption (3-조건 AND)

`templates/github-workflows/phase-gate-mergeable.yml` (+ `.github/workflows/phase-gate-mergeable.yml` byte-identical self-app mirror, ADR-005) 의 기존 3-source fast-pass OR-gate (현 `if (isEpicLabel || isSiblingPr || isDocOnly)`) 에 **4번째 source `isPostMergeFix` 추가**. 단순 `post-merge-fix` 라벨 부착만으로 통과 금지 — **3-조건 AND gate**:

| # | 조건 | mechanical 판정 | trust anchor |
|---|---|---|---|
| 1 | `post-merge-fix` label 존재 | `allLabels.includes('post-merge-fix')` (기존 isEpicLabel/isSiblingPr 동형) | PR author / label 부착 권한자 영역 |
| 2 | hub Story §10 FIX Ledger 에 해당 hotfix PR 을 가리키는 row binding 존재 | hotfix PR body `story_uri:` marker (기존 L31-90 cross-repo fetch 메커니즘 재사용) → Story file content fetch → §10 FIX Ledger 표 안 현재 hotfix PR 번호 (`<owner>/<repo>#<N>`) substring match + story_uri host + `<owner>/<repo>` 가 `ALLOWED_HUB_REPOS` (workflow env / plugin config 주입, PR body derive 금지) strict match — 미일치 시 fail-closed (Codex TP#2 P1 inline FIX, ADR-052 Amendment 4) | Orchestrator monopoly (fix-event-v1 contract, CFP-32) — PR author 위조 불가 audit trail |
| 3 | 정정 대상 원(MERGED) PR 이 §7 보안 영역 non-touch (양면) | (3a) hotfix PR body `corrects_pr: <owner>/<repo>#<N>` marker → 원 PR `pulls.listFiles` → `SECURITY_PATHS` 패턴 non-match ∧ (3b) 현재 hotfix PR 변경 파일도 `SECURITY_PATHS` 패턴 non-match | revert 가 보안 패치 무력화하는 것 차단 = 역참조 (SecurityArch 양면 강화 — Story §5 A3 가정 빈틈 보완) |

**audit trail 양면 필수**: 조건 1 (label, PR author 영역) ∧ 조건 2 (Story §10 binding, Orchestrator 영역) AND = single point of forgery 제거. 한쪽만으로는 orphan hotfix (Story 미연결 임의 fast-pass) 또는 self-declare 위조 가능 → 양면 AND 가 trust boundary mechanical anchor.

**`SECURITY_PATHS` 정의** (조건 3 보안 경로 패턴 집합, workflow 내 const): codeforge 도메인 보안 영역 = (a) `docs/adr/**` 중 보안 분류 ADR (frontmatter `category: security` 또는 title `security` 매칭) (b) `docs/security/**` (c) 정정 대상 원 PR 의 hub Story Change Plan §7 (보안 설계) 가 명시한 touched 파일 (Story §10 row 의 원 PR Change Plan link 역추적, best-effort — link 부재 시 (a)+(b) 패턴 + label heuristic fallback). consumer 도메인은 consumer overlay 가 `SECURITY_PATHS` 확장 가능 (축소 불가 — ADR-026 Amd 4 §결정 6 (화이트리스트) + ADR-024 Amendment 2 §결정 A (확장-only 패턴)).

**fail-closed default**: 판정 불가 시 (원 PR fetch 실패 / `corrects_pr:` marker 부재 / `story_uri:` marker 부재 / Story §10 fetch 실패 / 패턴 모호) = **BLOCK 유지 (exemption 미적용)**. false-negative (보안 우회 허용) 보다 false-positive (불필요 BLOCK → 정상 escalation 경로) 우선. 3-조건 중 1개라도 미충족 = 기존 phase gate 동작 그대로 (BLOCK).

**조건 2 cross-repo read PAT scope 판정** (§결정 2 cross-ref): 조건 2 는 `phase-gate-mergeable.yml` 의 **기존** `story_uri:` PR-body marker + `CODEFORGE_CROSS_REPO_PAT` contents fetch 메커니즘 (L19-90, `/repos/.../contents/<path>` REST endpoint + `Authorization: token` header + base64 decode) 을 **재사용**. 기존 메커니즘은 현재 frontmatter (phase/gate) 만 regex parse 하나, content 전체가 이미 base64 decode 되므로 §10 본문 표 파싱은 별도 API call 불요 (동일 fetch content 재사용). §결정 2 의 `CODEFORGE_CROSS_REPO_PAT` scope = `contents:write only on mclayer/codeforge-internal-docs` — **write scope 가 read 를 포함** (GitHub fine-grained PAT `contents:write` ⊇ `contents:read`). 따라서 dogfood Story 의 hub 가 internal-docs 인 경우 §10 read 는 기존 PAT scope 로 충족, **scope 확장 불요**. consumer repo 가 hub Story 인 경우 (mctrader hub 등) 는 해당 consumer 측 PAT 가 hub repo `contents:read` 보유 의무 — 본 dogfood Story 즉시 영역 아님 (consumer 일반화 = `docs/consumer-guide.md` Phase 2 명문화 + ADR-066 PAT rotation policy cross-ref). GITHUB_TOKEN 은 cross-repo 권한 없음 → PAT 미설정 시 degraded (조건 2 판정 불가 → fail-closed BLOCK). trust boundary 보완: 화이트리스트가 zero-trust anchor (PAT scope 만으론 fetch 성공이 hub trust 입증 안 함). 상세 = Change Plan §3.2 step 2.5

**EC-1 재귀 hotfix depth 제어**: hotfix-1 merge 후 발견된 bug → hotfix-2. Story §10 FIX Ledger row chain depth (또는 PR body `corrects_pr:` reference chain) > 2 시 escalate 강제 (BLOCK + escalate marker). audit trail 누적 depth mechanical 추적.

**EC-2 hotfix:minimal 경계**: `post-merge-fix` ≠ `hotfix:minimal` (별개 메커니즘). `hotfix:minimal` = 설계리뷰 생략만, 보안테스트 필수 (`docs/hotfix-playbook.md §1`). `post-merge-fix` = cross-repo land_order 정정 전용 (조건 3 보안 non-touch 역참조 시 보안테스트 실질 N/A). 두 경로 혼동 금지 — `docs/consumer-guide.md` Phase 2 명문화 의무. `post-merge-fix` 는 `hotfix-bypass:*` per-entry namespace 와도 별도 axis (hotfix-bypass = warning-tier lint conditional skip, post-merge-fix = phase-gate fast-pass source).

**구조 정합 (Refactor 검토)**: 4번째 source append 는 순수 additive — boolean OR 의 monotonic 특성상 기존 3 source (isEpicLabel/isSiblingPr/isDocOnly) 의 evaluation/short-circuit 동작 무변경 (각 source 독립 boolean, 상호 미참조). 조건 2/3 은 비동기 fetch 동반 → `isPostMergeFix` 를 OR-gate 직전 별도 async 평가 후 boolean 으로 진입 (기존 "boolean 사전 계산" 패턴 동형 유지). API 절약: `isPostMergeFix` 평가는 조건 1 (`post-merge-fix` label 존재) 시에만 short-circuit 진입 (라벨 부재 시 조건 2/3 fetch skip). 조건 2 cross-repo fetch 는 기존 L48-90 fetch content 재사용 권고 (별도 helper function 추출 — frontmatter parse 전용 기존 로직과 §10 row 전용 신규 로직 분리, PAT/URL parse 공유 DRY).

**self-application 회귀 invariant**: 본 Amendment 4 의 Phase 2 PR 자체가 `phase-gate-mergeable.yml` 변경 → Phase 2 PR 의 gate 가 변경된 workflow 자신으로 평가. Phase 2 PR 은 `phase:구현` → 기존 L210-213 `gate:design-review-pass` 경로 사용 (post-merge-fix 라벨 미부착 = 4번째 source 미발동 = 기존 3-source 동작으로 평가). "신규 source 가 기존 path 를 오염시키지 않음" 입증 = Phase 2 PR gate 통과 + `tests/workflows/` self-application 회귀 fixture.

### Reversibility (Amendment 4 scope)

- §결정 6 (4번째 fast-pass source): Phase 2 PR 의 `phase-gate-mergeable.yml` 변경에서 `|| isPostMergeFix` disjunct + `isPostMergeFix` 평가 블록 제거 = 기존 3-source 복원 (additive 특성상 clean rollback, 기존 source 무영향). `.github/workflows/` mirror 동시 revert (ADR-005).
- label-registry-v2 `post-merge-fix` entry: Phase 2 PR revert 시 §3 yaml row + frontmatter version + §변경 이력 prose 동시 rollback.
- plugin.json/CHANGELOG/marketplace.json MINOR bump: 별도 revert (ADR-063 atomic 3-file — marketplace sync PR 도 동반 revert).
- ADR-026 Amendment 4 자체 revert: ADR file revert (workflow 본체 무영향, declarative SSOT 만 revert) — but Amendment 4 design intent (post-merge-fix fast-pass source governance) 가 normative directive 로 격하.
- ADR-026 §결정 4 `.codeforge/post-merge-automation.disabled` flag 는 `post-merge-followup.yml` 용 — 본 §결정 6 fast-pass 와 별개 (rollback = code revert, flag 무관).

### Out-of-scope (Amendment 4 scope)

- 옵션 1 단독 / 옵션 3 단독 정책 채택 — 명시적 거부 (위 "거부된 옵션").
- `phase-gate-mergeable.yml` / `label-registry-v2.md` / `plugin.json` mechanical 구현 — Phase 2 구현 lane (Change Plan §3/§7/§8 SSOT 이행).
- consumer repo hub Story §10 read 의 consumer 측 PAT scope 일반화 — `docs/consumer-guide.md` Phase 2 명문화 + ADR-066 cross-ref (본 dogfood Story 즉시 영역은 internal-docs hub 으로 기존 PAT 충족).
- brainstorm Phase 0 agent read-only mandate enforcement gap (incident note) — 별도 codeforge-improvement 발의 영역 (spec §9 기록 보존). 본 Amendment 4 scope 외.
- PAT 만료 임박 사전 경고 KPI — ADR-066 PAT rotation policy 영역, 별도 follow-up note (조건 2 fail-closed 의 운영 부담 완화).

### 해소 기준 (Amendment 4 scope)

N/A — `is_transitional: false` (permanent governance mandate). 본 Amendment 4 = ratchet **강화** 방향: fast-pass 3-source → 4-source 는 gate **강화** 이며 약화 아님 (4번째 source 의 3-조건 AND 가 옵션 1 단순 라벨보다 엄격 — label 단독 거부 + Story §10 binding + 원 PR §7 보안 양면 non-touch). escalate-and-fix 철학 실행 (consumer workaround 금지, 정책 기반 자동 gate pass) + `enforce_admins:true` invariant 보호 (admin override 정상화 거부). ADR-058 §결정 5 정합 — sunset_justification 면제.

## Amendment 5 (CFP-900, 2026-05-18) — `.github/` fast-pass content sanity 1차 신호 (Wave 4 sub-Epic CFP-858 S3, Epic 마지막 Story)

### 컨텍스트

Epic CFP-858 (reconcile wholesale-mirror fallback 부가 결함 해소) 의 S3 (마지막 Story). S1 (CFP-898 dependency bundle integrity, vertical closure resolver mirror-전) + S2 (CFP-899 consumer-applicability filter, horizontal gating mirror-전) 위 honest reporting layer (mirror-후 temporal-post, 3-layer composite 완결). 본 Amendment 5 = ADR-076 Amendment 3 §결정 3 result fidelity sub-clause 의 sibling carrier (ADR-076 = upgrade-event log result enum 정직 반영 + post-mirror sanity check / 본 ADR-026 Amendment 5 = phase-gate-mergeable `.github/` fast-pass content sanity 1차 신호 — gate-time signal layer, mirror-time 집계 layer 와 분리).

**Epic CFP-858 §1 부가 결함 verbatim**: `phase-gate-mergeable.yml` 의 `.github/` 경로 fast-pass (현 `isDocOnly` line 180 `f.filename.startsWith('.github/')` + `isSiblingPr` line 173) 는 file path **prefix match 만** 수행 — workflow yml 안 의존 script reference (`run: bash scripts/check-*.sh` / `python3 templates/scripts/*.py`) 의 content 정합성 검사 부재. consumer 가 fast-pass PASS 만 보고 머지 시, mirror 된 workflow yml 의 의존 script 가 부재하면 전체 CI 마비 (P0급 피해). 현재는 close 로 회피 (구조적 거버넌스 부재). mctrader-data#81 14 failing checks class 가 evidence (S1 closure missing 차단의 gate-time dual axis).

Amendment 1 (§결정 5.A-5.D PR-Issue close algorithm) + Amendment 2 (§결정 5.E-5.F Action 1 strict regex / namespace) + Amendment 3 (§결정 5.G workflow file integrity governance) + Amendment 4 (§결정 6 post-merge-fix fast-pass 4번째 source). 본 Amendment 5 = **fast-pass content sanity advisory layer** = 새 design dimension (`.github/` fast-pass 의 path prefix match 만으론 탐지 못하는 content 비정합 1차 신호).

### 거부된 옵션 + 사유 (6 SubAgent 독립 수렴)

- **옵션 A 단독 (fast-pass OR-gate 에서 `.github/` 제거 / blocking 승격)**: **거부.** fast-pass 정책 약화 = ADR-064 §self-application top-down ratchet 위배 (fast-pass = operational tooling 자율성 보존 의도, CFP-260/261/262 SSOT). `.github/` fast-pass 제거 = 모든 workflow yml 변경이 full lane 강요 → escalate-and-fix 철학 위배 (불필요 BLOCK). content sanity 는 fast-pass 정책과 **orthogonal** — fast-pass PASS 보존 + content mismatch warning 별도 emit (SecurityArch + Refactor + OpRiskArch 독립 수렴: orthogonal warning layer ≠ gate 약화).
- **옵션 C 단독 (semantic-level content equivalence diff)**: **거부 (본 Story scope).** workflow logic equivalence diff = parser dependency + false-positive 폭증 (CFP-898 §4.11 AM-1 stdlib only 패턴 동형 reasoning). 본 Amendment 5 = syntax-level 1차 신호 (의존 script reference 존재성 mismatch) — semantic depth = future CFP separate (CFP scope unitary ADR-064 §결정 1.3, TestContractArch + DataMigrationArch 독립 수렴).

### 결정 7 (신설) — `.github/` fast-pass content sanity 1차 신호 (orthogonal warning layer)

`templates/github-workflows/phase-gate-mergeable.yml` (+ `.github/workflows/phase-gate-mergeable.yml` byte-identical self-app mirror, ADR-005) 의 기존 4-source fast-pass OR-gate (`isEpicLabel || isSiblingPr || isDocOnly || isPostMergeFix`) **위** orthogonal content sanity warning layer 1단 추가. **fast-pass OR-gate 자체 변경 0** — gate 통과 보존 + content mismatch warning 별도 emit.

| # | 항목 | 정의 | trust anchor |
|---|---|---|---|
| 1 | trigger 영역 | PR 변경 file 이 `.github/workflows/*.yml` 포함 ∧ fast-pass (isDocOnly OR isSiblingPr) 적용 시 | 객관 file path + diff (PR author 위조 불가) |
| 2 | content sanity signal | 변경된 `.github/workflows/*.yml` 안 의존 script reference (`run: bash scripts/check-*.sh` / `python3 templates/scripts/*.py`) 가 동일 PR diff 안 존재 OR repo 안 존재하는지 mismatch detect (S1 closure resolver CFP-898 §4.11 의 phase-gate-mergeable layer mirror — mirror-time vertical vs gate-time signal, layer 분리 invariant) | 객관 grep + diff (S1 closure resolver algorithm 재사용) |
| 3 | severity | **warning tier** (AM-1 derived default) — fast-pass PASS 자체 보존, content mismatch 시 1차 warning emit + PR comment | fast-pass 정책 무변경 invariant |

**fast-pass OR-gate 무변경 invariant**: 본 §결정 7 = fast-pass OR-gate (`isEpicLabel || isSiblingPr || isDocOnly || isPostMergeFix`) 자체 변경 0 — content sanity = orthogonal warning layer 1단 추가 (Amendment 4 §결정 6 3-source → 4-source ratchet 강화 패턴 답습 = gate 강화 방향, gate 약화 0). content mismatch 발견 시에도 fast-pass PASS 는 보존 (warning emit 만).

**warning tier rationale (AM-1 derived default, ADR-064 §결정 3 룰 1)**: fast-pass 정책 약화 (blocking 승격) = ADR-064 §self-application top-down ratchet 위배. content mismatch = 1차 warning + PR comment advisory (GitHub required vs optional check pattern 동형 — optional = warning emit but merge 미차단). blocking 승격 = evidence-checks-registry tier 승격 gate AND condition 충족 후 future CFP separate (CFP scope unitary ADR-064 §결정 1.3).

**S1 closure resolver algorithm 재사용 (Refactor 검토)**: 의존 script reference detect = CFP-898 §4.11 `dependency_bundle_integrity_binding.closure_resolve_algorithm: regex_primary` (stdlib only, transitive_depth_limit=1) 동형 — algorithm 재구현 0 (mirror-time closure resolver 의 gate-time signal mirror). 본 §결정 7 = phase-gate-mergeable.yml workflow Actions script 의 fast-pass 분기 안 content sanity 평가 (조건 1 trigger 시에만 short-circuit 진입 — `.github/workflows/*.yml` 미포함 시 skip).

**self-application 회귀 invariant**: 본 Amendment 5 의 Phase 2 PR 자체가 `phase-gate-mergeable.yml` 변경 → Phase 2 PR 의 gate 가 변경된 workflow 자신으로 평가. content sanity = orthogonal warning layer (fast-pass OR-gate 무변경 → Phase 2 PR gate 통과 무영향). "신규 warning layer 가 기존 fast-pass path 를 오염시키지 않음" 입증 = Phase 2 PR gate 통과 + `tests/workflows/test_phase-gate-mergeable-yml.sh` self-application 회귀 fixture.

### Reversibility (Amendment 5 scope)

- §결정 7 (content sanity warning layer): Phase 2 PR 의 `phase-gate-mergeable.yml` 변경에서 content sanity 평가 블록 제거 = 기존 4-source fast-pass 동작 복원 (orthogonal 특성상 clean rollback, fast-pass OR-gate 무영향). `.github/workflows/` mirror 동시 revert (ADR-005).
- ADR-026 Amendment 5 자체 revert: ADR file revert (workflow 본체 무영향, declarative SSOT 만 revert) — but Amendment 5 design intent (`.github/` fast-pass content sanity governance) 가 normative directive 로 격하.
- reconcile-protocol-v1 v1.10 §4.13 `result_fidelity_binding.fast_pass_content_sanity` field: 별도 revert (kind:registry, sibling sync 면제).

### Out-of-scope (Amendment 5 scope)

- 옵션 A 단독 (fast-pass `.github/` 제거 / blocking 승격) / 옵션 C 단독 (semantic-level content equivalence) — 명시적 거부 (위 "거부된 옵션").
- `phase-gate-mergeable.yml` content sanity mechanical 구현 — Phase 2 구현 lane (Change Plan §3/§7/§8 SSOT 이행, declaration-only-Wave-1).
- content sanity blocking tier 승격 — evidence-checks-registry tier 승격 gate AND condition 충족 후 future CFP separate.
- semantic-level workflow logic equivalence diff — AM-3 derived default 외, future CFP separate (CFP scope unitary).
- mctrader-data#81 14 failing checks backfill remediate — cross-repo, Epic CFP-858 close 후 별도 work (Epic §위험 신호 verbatim).

### 해소 기준 (Amendment 5 scope)

N/A — `is_transitional: false` (permanent governance mandate). 본 Amendment 5 = ratchet **강화** 방향: orthogonal content sanity warning layer 1단 추가 = gate **강화** 이며 약화 아님 (fast-pass OR-gate 무변경 + content mismatch 1차 warning emit — fast-pass PASS 보존하면서 silent content 비정합 가시화). escalate-and-fix 철학 실행 (consumer 가 fast-pass PASS = 안전 오인 → 전체 CI 마비 P0 차단). ADR-058 §결정 5 정합 — sunset_justification 면제 (CFP-795 Amendment 4 동형).

### Amendment 5 sunset boundary (CFP-1111 carrier — sibling carrier role 만)

본 Amendment 5 의 효용 carrier = **PR-gate layer 독립 보존** (phase-gate-mergeable.yml 의 `.github/` content sanity warning) — upgrade flow 영역 와 disjoint. CFP-1111 walker paradigm 전환 후에도 PR-merge gate 로직 자체는 별도 lifecycle 로 작동 (sunset 대상 아님).

다만 reconcile-protocol-v1 §4.13 result_fidelity_binding 의 sibling carrier 역할 (declarative carrier_story CFP-900) = walker walk_result 4-value enum 으로 carry — 그 영역의 sibling carrier role 만 sunset.

- **metric (sibling carrier role 만)**: walker 완료 보고 4-field (`walk_result: SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED`) 가 reconcile-protocol §4.13 result enum 4-value closed-set semantic equivalent + silent false SUCCESS 차단 0건 / N walk
- **who**: imperative-walker-protocol-v1 walker schema field `walk_result` + `exit_code_to_walk_result_mapping` rule
- **how**: walker integration test 안 4-value enum honest record verify + PR-gate layer 독립 작동 확인 (phase-gate-mergeable.yml `.github/` content sanity warning 존속)

**cross-ref**: [β2 audit (#1113)](https://github.com/mclayer/plugin-codeforge/issues/1113) Anchor 3 LOSSLESS 판정. PR-gate layer 독립 보존 — ADR-026 본체 (§결정 1-6 post-merge automation SSOT) 는 sunset 대상 아님.

#### sunset_executed (CFP-1186, 2026-05-22) — Amendment 5 sibling carrier role 영역 한정

**상태**: Amendment 5 sibling carrier role 영역 Sunsetted — reconcile-protocol-v1 §4.13 result_fidelity_binding 의 sibling carrier 역할 효용이 imperative walker 로 lossless carry 완료됨.

carry 증거 (β2 audit Anchor 3 LOSSLESS 확인):
- walker `walk_result` 4-value enum (SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED) = reconcile-protocol §4.13 result enum 4-value closed-set semantic equivalent
- silent false SUCCESS 차단 0건 / N walk 보존 (imperative-walker-protocol-v1 §2 walk_result honest record 의무)
- PR-gate layer (`phase-gate-mergeable.yml` `.github/` content sanity warning) = walker paradigm 과 **disjoint** 별도 lifecycle — 본체 §결정 1-6 sunset 아님, 계속 유효

**is_transitional 무변경**: `false` 유지 (본체 §결정 1-6 + Amendment 5 §결정 7 PR-gate layer 영구 불변). 본 sunset = Amendment 5 sibling carrier role 만 (reconcile-protocol §4.13 result_fidelity_binding 의 ADR-026 선언 역할 해소).

**본 ADR 본문 삭제 금지**: Sunsetted = 해당 영역의 carry 완료 선언. 본문은 historical record 로 영구 보존.

## 관련 ADR

- **ADR-022** §결정 1 User Override hierarchy: workflow 가 merge 결정 안 함, follow-up 만 (사용자 admin merge 결정 보존)
- **ADR-022** §결정 11 Phase 1 trust model: telemetry only, no enforcement hook
- **ADR-024** story-scoped branch policy: cfp-74 branch + Phase 1 PR 분리 정합. internal-docs 측 cross-repo write 도 branch + PR (1 PR 통합 거부 정합)
- **ADR-025** §결정 1: Sonnet pick=alpha 자동 진행 정합
- **ADR-001** review-agent-unification: review separation 변경 없음
- **ADR-008** SemVer: post-merge-counters.jsonl v1.0 = additive minor 가능
- **ADR-011** cross-repo PAT: CFP-71 precedent 정합
- **ADR-045 / CFP-138 Phase 1 follow-up** (2026-05-09): post-merge-telemetry.sh 의 Contents API SHA-based optimistic concurrency pattern 이 [`docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md`](../domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md) Pattern A 로 SSOT 화. retro-attempts.jsonl (ADR-045) 도 동일 Pattern A 의무. 본 ADR-026 implementation (post-merge-telemetry.sh) 는 이미 Pattern A 정합 — 본문 변경 0 (cross-ref only).
- **ADR-024 / CFP-70** (Amendment 4): `enforce_admins:true` invariant — admin 도 required status check 통과 의무. 본 Amendment 4 §결정 6 = 본 invariant 보호 (옵션 3 admin override 정상화 거부 = invariant 정면 충돌 회피, gate 강화 방향).
- **ADR-063** (Amendment 4): marketplace ↔ plugin.json atomic invariant — label-registry-v2 `post-merge-fix` entry MINOR → plugin.json MINOR (5.78.0 → 5.79.0) → CHANGELOG.md → marketplace.json 3-file atomic + sync PR 선행 merge.
- **ADR-005** (Amendment 4): self-application byte-identical mirror — `templates/github-workflows/phase-gate-mergeable.yml` ↔ `.github/workflows/phase-gate-mergeable.yml` 동시 갱신 의무 (4번째 source append).
- **ADR-066** (Amendment 4): CODEFORGE_CROSS_REPO_PAT rotation policy — 조건 2 cross-repo §10 read 가 기존 PAT (`contents:write on internal-docs` ⊇ read) 재사용. consumer hub repo 일반화 시 consumer PAT `contents:read` scope cross-ref.
- **ADR-013 / ADR-017** (Amendment 4): codeforge family dogfood-out — 본 Amendment 4 의 Change Plan / Story file = internal-docs `wrapper/`, ADR home = 본 plugin-codeforge `docs/adr/`.
- **ADR-076** (Amendment 5): declarative reconciliation upgrade flow — 본 Amendment 5 §결정 7 (`.github/` fast-pass content sanity 1차 신호 gate-time signal) = ADR-076 Amendment 3 §결정 3 result fidelity sub-clause (upgrade-event log result enum 정직 반영 + post-mirror sanity check mirror-time 집계) 의 sibling carrier (Wave 4 sub-Epic CFP-858 S3, Epic 마지막 Story). gate-time signal layer ↔ mirror-time 집계 layer 분리 invariant.
- **ADR-064** (Amendment 5): §self-application top-down ratchet — 본 Amendment 5 = orthogonal content sanity warning layer 1단 추가 (gate 강화 방향, fast-pass OR-gate 무변경 = 약화 0). 옵션 A 단독 (fast-pass `.github/` 제거) 거부 = fast-pass 정책 약화 ratchet 위배 회피. semantic-level depth = future CFP separate (CFP scope unitary §결정 1.3).
- **ADR-058** (Amendment 5): §결정 5 sunset_justification — Amendment 5 = ratchet 강화 방향 (orthogonal warning layer 1단 추가는 gate 강화), `is_transitional: false` 유지, sunset_justification 면제 (CFP-795 Amendment 4 동형).
- **ADR-082 / ADR-070** (Amendment 5): write-time self-write verification mandate / Codex verify-before-trust — 본 Amendment 5 `mechanical_enforcement_actions[]` entry `post-merge-fix-fast-pass-content-sanity-signal` = declaration-only-Wave-1 (Phase 2 PR content sanity assertion 가 mechanical detection 책임, ADR-082 §결정 6 + ADR-070 §D5 declaration-only retain 패턴 답습, CFP-898/CFP-899 precedent 정합).
- **ADR-005** (Amendment 5): self-application byte-identical mirror — `templates/github-workflows/phase-gate-mergeable.yml` ↔ `.github/workflows/phase-gate-mergeable.yml` 동시 갱신 의무 (content sanity warning layer Phase 2 추가).
- **ADR-083 / CFP-898 / CFP-899** (Amendment 5): Wave 4 sub-Epic CFP-858 3-layer composite — S1 (CFP-898 ADR-076 Amendment 2 vertical dependency closure) + S2 (CFP-899 ADR-083 horizontal consumer-applicability filter) 위 S3 (CFP-900 본 Amendment 5 + ADR-076 Amendment 3 honest reporting layer, mirror-후 temporal-post). content sanity signal = S1 closure resolver (CFP-898 §4.11) 의 phase-gate-mergeable layer mirror (algorithm 재사용, gate-time signal).
- **ADR-013 / ADR-017** (Amendment 5): codeforge family dogfood-out — 본 Amendment 5 의 Change Plan / Story file = internal-docs `wrapper/`, ADR home = 본 plugin-codeforge `docs/adr/`.
- **ADR-058** (Amendment 4): §결정 5 sunset_justification — Amendment 4 = ratchet 강화 방향 (fast-pass 3→4 source 는 gate 강화), `is_transitional: false` 유지, sunset_justification 면제.

## Amendment 6 (CFP-1059, 2026-05-20) — Epic close → Deploy trigger hook (codeforge-deploy lane 신설 정합)

### 결정 8 (신설) — Epic close transition trigger 추가

CFP-1059 Story-1 sibling carrier (ADR-023 Amendment 1 + ADR-087 Deploy lane + ADR-088 Deploy Review lane 신설 atomic). 본 Amendment 6 = post-merge automation 영역 확장 — Epic close transition trigger 신규 채널 추가.

#### 기존 post-merge automation trigger (Amendment 1-5 누적)

| Source | Trigger | Owner |
|---|---|---|
| 1 | PR merge transition (`pull_request: closed + merged`) | Action 1 (Phase label transition) — Amendment 1 §결정 5 |
| 2 | Issue close keyword regex transition (PR body `Closes #` + Issue closedByPullRequestsReferences dual-source AND) | Action 1 §결정 5 |
| 3 | post-merge-fix phase-gate fast-pass (3-조건 AND: post-merge-fix label + hub Story §10 binding + 원 MERGED PR §7 보안 non-touch) | Amendment 4 §결정 6 |
| 4 | `.github/` fast-pass content sanity 1차 신호 (orthogonal warning layer) | Amendment 5 §결정 7 |

#### 5번째 source (신설) — Epic close transition trigger

```yaml
trigger:
  issues:
    types: [closed]

source_5_epic_close:
  condition:
    - issue.labels contains "type:epic"
    - issue.labels contains "gate:retro-complete"
    - issue.closedAt - issue.openedAt >= 1h  # 즉시 close 차단 (parent Epic 정합 invariant)
  action: spawn DeployPL (codeforge-deploy lane)
  scope: production cutover-touching Epic 한정 (consumer-side, wrapper-self-app N/A)
  consumer_applicability_filter: ADR-083 §결정 1 4-way enum (`consumer` only, `mixed`/`plugin`/`unknown` repo skip)
```

#### Consumer-side gating layer (ADR-083 정합)

- **wrapper-self-app exemption** — wrapper repo (`mclayer/plugin-codeforge`) = mixed repo 분류 → DeployPL spawn skip (self-loop bug 차단, ADR-083 §결정 4 정합)
- **consumer repo only** — `.claude-plugin/plugin.json` 부재 + `.claude/_overlay/project.yaml` 존재 시 (consumer repo) DeployPL spawn fire
- **production cutover-touching Epic 한정** — Epic Issue body 안 `<!-- scope_manifest -->` block `production_cutover_touching: true` 명시 시만 trigger (ADR-072 §결정 5 epic-cutover-gate-evidence-quad-check 정합)

### 결정 9 (신설) — declaration-only Wave 1 mechanical_enforcement_actions[] entry

```yaml
mechanical_enforcement_actions:
  - action: epic-close-deploy-trigger
    status: declaration-only-Wave-1
    progress_note: "CFP-1059 Story-1 Amendment 6 §결정 8 carrier (codeforge-deploy lane 신설 정합). mechanical enforce = `templates/github-workflows/epic-close-deploy-trigger.yml` + `.github/workflows/epic-close-deploy-trigger.yml` (byte-identical, ADR-005) + `scripts/check-epic-close-deploy-trigger.sh` + evidence-checks-registry row append. Phase 2 PR (구현 lane) scope. declaration-only Wave 1 retain (ADR-082 §결정 6 + ADR-070 §D5 precedent 답습, CFP-898 / CFP-899 / CFP-900 precedent 정합)."
    target_section: §결정 8
```

### 기존 정책 변경 0건 (ADR-026 본문)

본 Amendment 6 = ADR-026 결정 1~7 본문 변경 0건. 변경 = (a) 본 `## Amendment 6` body section (b) frontmatter `amendment_log` entry append (Amendment 6 row) + `related_stories` CFP-1059 row append. ratchet 강화 방향 (post-merge automation trigger 4-source → 5-source 확장 — scope 확장, ADR-058 §결정 5 정합) → sunset_justification 불필요 (강화 방향 only).

### Cross-references

- ADR-023 Amendment 1 (CFP-1059 / Story-1 sibling carrier — lane plugin 6 → 8 확장)
- ADR-087 (CFP-1059 / Story-1 신설 — Deploy lane as 7th lane plugin, §결정 6 sibling cross-ref — Epic close trigger 정합)
- ADR-088 (CFP-1059 / Story-1 신설 — Deploy Review lane + ProductionEvidence transfer)
- ADR-042 Amendment 9 (CFP-1059 / Story-1 sibling — 4 신설 agent tier DeployPL / DeployWorker / DeployReviewPL / DeployReviewWorker)
- ADR-083 §결정 1 (consumer-applicability filter 4-way enum, consumer-self-app gating layer)
- ADR-072 §결정 5 (epic-cutover-gate-evidence-quad-check — production cutover-touching Epic 한정 trigger scope 정합)
- ADR-082 §결정 6 + ADR-070 §D5 (declaration-only Wave 1 retain pattern)
- ADR-005 (self-application byte-identical mirror — `templates/github-workflows/epic-close-deploy-trigger.yml` ↔ `.github/workflows/` Phase 2 PR 의무)
- ADR-064 §self-application top-down ratchet (강화 방향 only, 약화 0)
- ADR-058 §결정 5 sunset_justification (ratchet 강화 방향 = sunset 면제, is_transitional: false 보존)
