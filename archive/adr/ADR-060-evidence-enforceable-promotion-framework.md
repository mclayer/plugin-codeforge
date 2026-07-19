---
adr_number: 60
title: Evidence-enforceable promotion framework — declaration → warning → enforce 점진 적용 SSOT
status: Accepted
category: governance
date: 2026-05-11
is_transitional: false
carrier_story: CFP-389
supersedes: []
amends: []
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.A (A안 list[object]) — Amendment 13 (CFP-722) 신규 mechanical action 도입.
  # ADR-060 본문 §결정 1-25 = framework 자체 (개별 entry 의 mechanical action 은 registry yaml SSOT).
  # 본 field = Amendment 가 신규 lint carrier 일 때 §결정 N ↔ entry binding 명시 (Amendment 12 doc-only 면제와 상이).
  - action: story-section-ownership          # docs/evidence-checks-registry.yaml entries[].name verbatim (Phase 2 row append)
    status: warning                          # ADR-060 §결정 5 첫 도입 = warning (continue-on-error, never block)
    progress_note: "CFP-722 Amendment 13 carrier — Phase 1 = ADR/Story §3·§7/Change Plan, Phase 2 = script/lib/2 workflow/registry row/fixture. blocking-on-pr 승격 target = §결정 27.E (data-loss expedited-gate = FUTURE labeled option, STANDARD §결정 6 threshold ship)"
    target_section: §결정 27                  # 본 Amendment 13 의 mechanical action ↔ §결정 binding
  # Amendment 14 (CFP-963, 2026-05-19 KST) — 12번째 warning-tier entry 도입 (codex-network-scope-presence,
  # ADR-081 Amendment 4 §결정 D1.D body 확장의 mechanical enforcement layer).
  - action: codex-network-scope-presence
    status: deferred-followup     # registry yaml row append = Phase 1 PR; actual lint script + workflow + bats fixture pair wire = Phase 2 PR scope
    progress_note: "CFP-963 Amendment 14 carrier — Phase 1 = ADR-081/060/024 Amendments + 2 contract MINOR + SSOT doc + Story §3·§7·§11 + Change Plan, Phase 2 = scripts/check-codex-network-scope.{sh,py} + templates/github-workflows/codex-network-scope-presence.yml + .github/workflows/ self-app + tests/bats + tests/fixtures pair (CX-963-3 P2 boundary mandate per Codex TP#4). warning tier first per §결정 5"
    target_section: §결정 28      # 본 Amendment 14 의 mechanical action ↔ §결정 binding (신규 §결정 28 entry scope + false-positive risk + self-meta loop avoidance)
  # Amendment 15 (CFP-1306, 2026-05-25) — 13번째 warning-tier entry 도입 (parallel-anchors-checked-presence,
  # ADR-068 I-2 cross-module propagation completeness Wave 3 enforcement layer, review-verdict-v4 v4.9 carrier).
  - action: parallel-anchors-checked-presence
    status: warning               # Phase 1+2 동시 wire (CFP-1334 precedent — deferred-followup → warning 직접 전환)
    progress_note: "CFP-1306 Amendment 15 carrier — review-verdict-v4 findings[].parallel_anchors_checked[] presence-grep heuristic lint. ADR-068 I-2 declaration source + ADR-060 Amendment 15 enforcement source dual-binding. 3-state semantic (absent→WARNING/clean→PASS/matched→PASS). 5 pattern_type enum closed-set. bats 12 TC RED→GREEN stash proof (CFP-1334 mandate). warning tier first per §결정 5"
    target_section: §결정 29      # 본 Amendment 15 의 mechanical action ↔ §결정 binding
  # Amendment 16 (CFP-2061-S1, 2026-06-08) — 14번째 warning-tier entry 도입 (increment-justification-presence,
  # 검사/ADR/스크립트 순증 PR 정당화 게이트 enforcement layer, de-bloat 거버넌스 영속화 carrier).
  - action: increment-justification-presence
    status: warning               # Phase 1+2 분리 wire (Phase 1 = ADR Amendment + frontmatter entry, Phase 2 = registry row + script/workflow/bats). warning tier first per §결정 5
    progress_note: "CFP-2061-S1 Amendment 16 carrier — 검사(scripts/check-*, (templates|.github)/workflows/*)·ADR(신규 adr_number)·스크립트 신규 추가 PR 의 PR body 정당화 marker (`[increment-justification] why=<...> blocks-or-replaces=<...>`) presence-grep heuristic lint. check-tier-downgrade-guard.sh 순증 방향 대칭 + check-bypass-justification-marker presence-grep/exempt/3-tier exit 구조 차용. ADR-058/064 약화 정당화 순증 제약 reference-only 연결. Phase 1 = ADR Amd16 + frontmatter entry + Story §3·§7 + Change Plan, Phase 2 = scripts/lib/check_increment_justification.py + scripts/check-increment-justification.sh + templates/github-workflows/increment-justification.yml + .github/workflows/ self-app + tests/bats + tests/fixtures + registry row. warning tier first per §결정 5"
    target_section: §결정 30      # 본 Amendment 16 의 mechanical action ↔ §결정 binding
  # Amendment 17 (CFP-2061-S4, 2026-06-09) — 15번째 warning-tier entry 도입 (governance-drift-detection,
  # 거버넌스 지표 7종 주기 측정 + drift 이슈 자동 발행 cron, de-bloat 재증식 감시 경보 채널).
  - action: governance-drift-detection
    status: warning               # Phase 2 full-lane wire (Python SSOT + bash wrapper + cron workflow + baseline JSON + bats + registry row). warning tier first per §결정 5
    progress_note: "CFP-2061-S4 Amendment 17 carrier — 거버넌스 지표 7종(검사수/워크플로수/매-PR워크플로/셸수/셸LOC/ADR수/ADR바이트) baseline JSON 대비 drift 상대 증가율 임계 초과 시 이슈 자동 발행(dedup). dedup signature = sha256(governance-drift|metric|increase|bucket) — current_val 절대 제외(폭주 함정 회피). advisory exit 0 (warning tier). Phase 2 = scripts/lib/check_governance_drift.py + scripts/check-governance-drift.sh + templates+.github/workflows/governance-remeasure-cron.yml (ADR-005 byte-parity) + docs/kpi/governance-bloat-baseline.json (provisional) + tests/bats 19 TC RED->GREEN. prior art 답습: check-marketplace-drift.sh + bypass-label-counter.py (신규 발명 0). warning tier first per §결정 5"
    target_section: §결정 31      # 본 Amendment 17 의 mechanical action ↔ §결정 binding
  # Amendment 18 (CFP-2381, 2026-06-20 KST) — 16번째 warning-tier entry 도입 (deferred-followup-reconcile,
  # §결정 19 auto_blocking 라벨의 mechanical forcing function carrier — carrier-부재 reconciliation 게이트).
  - action: deferred-followup-reconcile
    status: warning               # Phase 2 full-lane wire (Python SSOT + bash wrapper + warning workflow + self-validation test job + registry self-entry + STALE 2 flip). warning tier first per §결정 5. self-entry 는 §32.E self-application 자연 회피 정합 — 게이트 자체 script/workflow 실존 예정이라 self-flag 안 됨 (carrier_absent == false)
    progress_note: "CFP-2381 Amendment 18 carrier — §결정 19 (Amendment 6) auto_blocking 라벨이 '별도 carrier 가 평가 의무' 선언만 하고 carrier 발의 강제 forcing function 부재 → '임계 초과 + auto_blocking + 전용 carrier 부재' entry 자동 검출 + 강제 action 3택 (배선/강등/폐기). carrier-부재 검출 = detect_command/workflow 경로 파일 실존 (OR 결합 — 하나라도 ABSENT 면 carrier-incomplete, deterministic + 외부의존 0 + backfill 0). 검출 status-agnostic broad criterion (stale-local-main status:Active 도 포착). Phase 2 = scripts/lib/check_deferred_followup_reconcile.py + scripts/check-deferred-followup-reconcile.sh + templates+.github/workflows/deferred-followup-reconcile.yml (test-job byte-parity = §32.E Phase 2 결정) + scripts/test-check-deferred-followup-reconcile.sh (self-validation, exit-1 회귀 차단) + registry self-entry append + STALE 2 status flip (bootstrap-labels-precondition + schema-change-7-principles-self-check) + TBD 주석 제거. prior art 답습: check_governance_drift.py (registry-class lint) + check-increment-justification.sh (trigger-path 감지 presence-grep) + operational-outcome-signal-lint.yml (self-validation test job). warning tier first per §결정 5"
    target_section: §결정 32      # 본 Amendment 18 의 mechanical action ↔ §결정 binding
  # Amendment 19 (CFP-2426, 2026-06-26 KST) — 17번째 warning-tier entry 도입 (lane-count-ssot-consistency,
  # canonical 작업레인 수(10, ADR-125 Amd1) SSOT mechanical consistency enforcement carrier).
  - action: lane-count-ssot-consistency
    status: warning               # Phase 2 full-lane wire (Python SSOT + bash wrapper + warning workflow + self-contained discriminating test + registry self-entry + plugin.json tagline STALE 정정). warning tier first per §결정 5. self-entry 는 §33.D self-application — 게이트 자체 script/workflow 실파일 동반 신설 + self description 에 count 토큰(N≠10) 미포함 → self-flag 안 됨
    progress_note: "CFP-2426 Amendment 19 carrier — ADR-125 Amd1 이 canonical lane 수=10 을 정본 SSOT 로 박았으나(registration) 분산 governance 문서 사본이 단조 유지되도록 강제하는 mechanical enforcement 부재 → stale N 레인/N번째 lane(N≠10) drift 가 2 Story 연속(CFP-2341 → CFP-2376) leak. 'registration 완료 ≠ enforcement 실효' 전형. 검출 1급 firing = stale_token_match(line) AND NOT allowlist_match(line). 5축 allowlist(within-line 이중토큰 / negation / history / path / counterfactual) channel(line-prefix key) 단위 면제. same-file channel-split: live description:/section: 값=검출 vs date:/source_section:/amendment_log span=면제. amendment_log span = line-local boolean toggle(enter=헤더 key / exit=dedent·sibling list·다음 top-level key), multi-line backtracking regex 0(ReDoS-safe). N-range={5,6,7,8,9} = canonical-10 특정값 detection (미래 lane 증감 ADR-125 Amendment 가 N-range 갱신을 REQUIRED mechanical-sync 항으로 포함). Phase 2 = scripts/lib/check_lane_count_ssot.py + scripts/check-lane-count-ssot.sh + .github/workflows/lane-count-ssot.yml(.github single-root, deferred-followup-reconcile 동형) + scripts/test-check-lane-count-ssot.sh(22 fixture + 4 mutation 생존 0) + registry self-entry append + plugin.json tagline lane-count 8→10 STALE 정정(marketplace-atomic sync ADR-063). prior art 답습: check_issue_body_claim_pre_screen.py(line-by-line in_fence boolean toggle) + check_governance_drift.py(git ls-files path walk + ::warning:: advisory exit) + check-deferred-followup-reconcile.sh(ADR-061 thin wrapper). warning tier first per §결정 5"
    target_section: §결정 33      # 본 Amendment 19 의 mechanical action ↔ §결정 binding
  # Amendment 20 (CFP-2591, 2026-07-10 KST) — deferred-followup forcing-function 봉합 Stage 1+2
  #   (baseline + new-only shadow). §결정32.D surfacing tier 도입 + grandfather baseline 메커니즘 신규 §결정
  #   + (b) carrier-mandate no-TBD lint entry (18번째 warning-tier entry, deferral-carrier-declared).
  - action: deferral-carrier-declared
    status: warning               # ★ Stage 1+2 (baseline + new-only shadow) — warning-tier wired, blocking 아님. 실제 continue-on-error 제거(flip → blocking-on-pr surfacing)는 baseline main 착지 후 별 후속 PR (§7.2.2 self-deadlock 회피). self-entry deferred-followup-reconcile current_tier:warning 불변 (NO-FLIP invariant). warning tier first per §결정 5
    progress_note: "CFP-2591 Amendment 20 carrier — deferred-followup 을 미해결 placeholder(TBD 마커 / 미발급 CFP 번호 / 미배선 FU 마커)로 남기면 forcing function 대상 자체가 소멸(silent debt) → (b) carrier-mandate no-TBD lint 이 registry 밖 declaration surface 전반에서 placeholder 검출 + registry cross-check(named carrier level-1 membership) + baseline grandfather(new-only). (a) registry FLAG 는 sibling deferred-followup-reconcile 소관(두 축 disjoint). grandfather baseline 메커니즘(docs/deferred-followup-baseline.yaml — enumerated-freeze / 2-owner section / single-writer gen tool / content_digest tamper-evident / monotonic shrink) = framework-wide 신규 §결정(new-only SonarQube Clean-as-You-Code + betterer ratchet). §결정32.D surfacing tier(Tier 1 = continue-on-error 제거 + red-X/sticky 표면화, required 6-tuple 미편입) 도입 + §결정3 reconciliation(surfacing qualifier — current_tier:blocking-on-pr 자체가 contexts membership 함의 안 함). self-entry §결정6 carrier 3종(outage runbook / author-verify lint / sticky at-most-once) evidence_artifacts 배선. Stage 1+2 = continue-on-error 유지(flip 미포함) — Tier 2(hard-required) = FUTURE/OOS. honest forcing ceiling: hard block 미주장(admin 우회 구조적 가능, AC-20 count #4 관측만). Phase 2 = scripts/lib/check_deferral_carrier_declared.py + scripts/check-deferral-carrier-declared.sh + .github/workflows/deferral-carrier-declared.yml + docs/deferred-followup-baseline.yaml + docs/runbooks/deferred-followup-reconcile-enforce-outage.md + registry (b) entry + self-entry evidence_artifacts 3종. prior art 답습: check_lane_count_ssot.py(line-by-line scan + 5축 allowlist) + check_deferred_followup_reconcile.py(baseline loader/digest). ADR-127/ADR-024 amendment 불요(Tier 1 surfacing 이 6-tuple 회피 → §9.1 SSOT 무변경 + §9.4 bypass invariant 미발화). warning tier first per §결정 5"
    target_section: §결정 32      # 본 Amendment 20 의 mechanical action ↔ §결정 binding (§32.D surfacing tier 개정 + §7.9 carrier trio + no-TBD (b) lint)
  # Amendment 21 (CFP-2597, 2026-07-10 KST) — 19번째 warning-tier entry 등록 (peer-completion-falsifiability,
  #   ADR-044 Amendment 6 §결정 12 verification-floor 축③ carrier). 신규 §결정 0 — §결정 5 warning-tier 등록 절차 상속.
  - action: peer-completion-falsifiability
    status: warning               # ADR-060 §결정 5 첫 도입 = warning mode (continue-on-error). ADR-044 §3.4 정직 상한 (full falsifiability 불가 → blocking 승격 = false assurance). warning tier first per §결정 5
    progress_note: "CFP-2597 Amendment 21 carrier — ADR-044 Amendment 6 §결정 12 (check-verification-floor.sh 축③ peer-completion falsifiability) 의 warning-tier check 등록. owner_adr = ADR-044 (축③ 결정 SSOT), carrier_adr = ADR-060 (framework host). evidence-checks-registry.yaml peer-completion-falsifiability entry mirror. PASS verdict 이 review-verdict-v4 §19 peer_verdicts[] artifact-backed 완료 증거를 동반하도록 강제 (target FS 실재+non-empty 독립 stat, 자기단언 verify_status 불신). ★ check-lane-evidence.sh 축③ (deputy/role:dev fan-out, ADR-044 §결정 10 (d)) 와 별개 (이름만 동일, script·axis disjoint). 신규 §결정 0 — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate (pr_cumulative_min 20 / failure 0 / sibling merged) 상속. non-version-gated (anti-evasion). 실 script (scripts/check-verification-floor.sh 축③ logic) + workflow + discriminating test = sibling worker Phase 2 deliverable. Phase 1 governance-doc = ADR-044 Amendment 6 + review-verdict-v4 v4.16 + MANIFEST mirror + review-pl-base §3/§10 + orchestrator-playbook §3.10.1 + evidence-checks-registry entry. warning tier first per §결정 5"
    target_section: §결정 5       # 본 Amendment 21 = 신규 §결정 0 (framework 자연스러운 사용 사례 entry 추가 only) — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate 상속, owner_adr = ADR-044 Amendment 6
  # Amendment 22 (CFP-2635, 2026-07-12 KST) — 20번째 warning-tier entry 등록 (shell-test-exit-masking-detect,
  #   codeforge shell self-test 코퍼스의 `|| true` exit-masking + mock-seam-무assert false-coverage 정적 검출).
  #   신규 §결정 0 — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate 상속 (framework 자연 사용 사례, 신규 mechanism 0).
  - action: shell-test-exit-masking-detect
    status: warning               # ADR-060 §결정 5 첫 도입 = warning mode (continue-on-error). ADR-151 honesty ceiling 상속 (naive-masking 패턴 presence/형식 까지만 — 검출력 미강제, blocking 승격 = false assurance). warning tier first per §결정 5
    progress_note: "CFP-2635 Amendment 22 carrier (원천 backlog #960) — codeforge 거버넌스 shell self-test 코퍼스(scripts/test-*.sh 33 + tests/scripts/*.sh 37 = 70 file [verified])의 (a) raw `cmd || true` exit-masking(cmd exit 이 유일 pass/fail 신호이고 하류 FAIL 카운터/assertion 부재 = 항상 PASS) + (b) mock-seam env export 후 동반 assertion 부재 = false-coverage 를 정적 lint 로 검출. ★ 정당 3종(§2.4)은 오탐 0 제외: (i) counter-backup `assert_* || true`(assert helper 가 FAIL 카운터 증가, set -e 중도종료 가드) / (ii) `((c++)) || true` 산술 idiom / (iii) production `cmd 2>/dev/null || true` best-effort 캡처. 핵심 정밀도 keystone = **logical-line 재구성**(backslash-continuation join) 후 leading-command-token 분류 — 다중행 `assert_grep_all ... \\ \"p1\" \\ \"p2\" || true`(test-cfp-2521-presence.sh:92-95 [verified])의 `|| true` 가 continuation 행에 위치해도 logical head token=`assert_grep_all` 로 정당 판정(naive line-grep 오탐 폭발 회피, ADR-119 자기모순 차단). bats 아님 — 원 #960 의 bats 프레이밍은 codeforge 오칭, 대상 재지정(shell 코퍼스). scope 밖: plugins/codeforge-test/**/*.bats 2 fixture(통합테스트 example-story, 거버넌스 코퍼스와 disjoint — RR-2635-1) + tests/scripts/ Python/JS. Phase 2 = scripts/lib/check_shell_test_masking.py (Python SSOT, ADR-061 §결정 1 offline/read-only/argparse/pathlib, ReDoS-safe anchored 리터럴+\\d+ line-by-line) + scripts/check-shell-test-masking.sh (thin wrapper) + .github+templates/github-workflows/shell-test-exit-masking-detect.yml (byte-identical pair ADR-005, pull_request NOT pull_request_target + permissions contents:read) + tests/scripts/test_check-shell-test-masking.sh (discriminating fixture — masking TC RED→검출 / 정당 3종 GREEN→미검출, mutation-kill: 제외 로직 제거 시 정당 RED / 검출 로직 제거 시 masking RED) + docs/selftest-execution-liveness-inventory.yaml 레코드 append(ADR-151 AC-1a bijection 강제, discriminating_fixture:present) + registry row append + hotfix-bypass:shell-test-exit-masking-detect label(label-registry-v2). owner_adr = ADR-060 (framework host = enforcement source) / honesty ceiling source = ADR-151 §결정7. prior art 답습: check_selftest_execution_liveness.py(house style + helper decomposition) + check_spawn_prompt_fact_verify.py(ReDoS-safe line-by-line) + subagent-wait-liveness-presence(byte-identical workflow + execution-backed self-test + spec_invariant_measurement_required:false). 신규 발명 0. removed orphan bats-red-green-proof-presence(2026-06-10 de-bloat, workflow 부재 dead gate) 재발 차단 = 대상 실코퍼스 + live workflow pair + inventory enroll + self-test 발화 실증. warning tier first per §결정 5"
    target_section: §결정 5       # 본 Amendment 22 = 신규 §결정 0 (framework 자연 사용 사례 entry 추가 only) — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate 상속, owner_adr = ADR-060, honesty-ceiling source = ADR-151 §결정7
  # Amendment 23 (CFP-2700, 2026-07-16 KST) — 21+22번째 warning-tier entry 등록 (infra-resource-undeclared-surface + infra-resource-orphan-reconcile,
  #   인프라 자원 선언 manifest(project.yaml infra_resources) vs 코드/compose/env 템플릿 스캔 CI drift 게이트 — CFP-2700 D3). 2 entry 분리 근거 = §결정 3 current_tier per-entry(entry 당 1개) → D3 2축(미선언 표면명 surfacing-bound / orphan warning→승격) 비대칭 표현 불가라 분리.
  #   신규 §결정 0 — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate + Amendment 20 grandfather baseline(new-only) + §결정 32.D surfacing 상속 (신규 승격/baseline mechanism 발명 0, CFP-2700 AC-16). owner_adr = ADR-157 (D1~D5 결정 SSOT), carrier_adr = ADR-060 (framework host).
  - action: infra-resource-undeclared-surface
    status: warning               # ★ Phase 2 = warning + baseline 동시 착지, blocking 아님. 미선언축(코드/compose/env 스캔 표면명이 manifest 미선언·미분류) = new-only ratchet(Amd20 grandfather baseline) + §결정 32.D surfacing. 실제 continue-on-error 제거(flip → blocking-on-pr surfacing)는 baseline main 착지 후 별 후속 PR (§7.2.2 NO-FLIP self-deadlock 회피 — baseline 도입 PR 자신이 surfacing 이면 baseline 부재 상태 전 PR self-block). warning tier first per §결정 5
    progress_note: "CFP-2700 Amendment 23 carrier (미선언축) — 인프라 자원 manifest(consumer/wrapper-self .claude/_overlay/project.yaml infra_resources) vs 코드·compose·env 템플릿 스캔 표면명 대조. alias→canonical 정규화 적용 후에도 미분류 표면명 = drift(env 키 난립 차단). Phase 2 = scripts/lib/check_infra_resource_drift.py(Python SSOT, ADR-061 offline/read-only/argparse/pathlib, ReDoS-safe line-by-line) + scripts/check-infra-resource-drift.sh(thin wrapper) + .github+templates/github-workflows/infra-resource-manifest-drift.yml(byte-identical pair ADR-005, pull_request + permissions contents:read, always-run job + repo-guard if: — on.paths 필터 day-1 금지=vacuous-pass 규범⑤) + docs/infra-resource-baseline.yaml(Amd20 grandfather baseline 재사용 — enumerated-freeze/2-owner/single-writer gen/content_digest/monotonic shrink) + discriminating self-test dual(.sh ADR-151 inventory enroll + .py ac-traceability Hop3 AST) + census fail-closed(candidates==0∧inert==0 → born-hollow exit 3, examples/**+presets/** scan scope 포함 필수 — inert>0 성립) + registry row + hotfix-bypass:infra-resource-undeclared-surface label. cross-repo 축(CODEFORGE_CROSS_REPO_PAT fetch + <ns>/<id> 네임스페이스 + failure-mode 분리[content-mismatch=fail-closed / token부재=degraded-FAIL / foreign transient=fail-open+Issue] + ref-pin) = ADR-157 §결정 4 SSOT. §32.D surfacing(required 7→8 미편입, DEC-5 정합 — narrowing override 불요, ADR-060 이 fail-closed 비호환 아님). 死因 3-mode 봉인: FM1-false-positive=surgical scope+allowlist+SELF_EXCLUDE / FM2=Phase1+2 동시착지 / FM3=cross-repo subject durability(live consumer 자원선언). prior art 답습: check_path_relocation_consistency.py(원장 yaml + 로컬 코퍼스 census + active_when self-report selector) + check_deferral_carrier_declared.py(baseline loader/digest). owner_adr = ADR-157. warning tier first per §결정 5"
    target_section: §결정 5       # 본 Amendment 23(미선언축) = 신규 §결정 0 (framework 자연 사용 사례 entry 추가 only) — §결정 5 warning-tier 등록 절차 + §결정 32.D surfacing(NO-FLIP) 상속, owner_adr = ADR-157
  - action: infra-resource-orphan-reconcile
    status: warning               # orphan축(manifest 선언됐으나 어떤 참조면에서도 미참조 = dead declaration) = §결정 5 warning first → §결정 6 3-AND(PR 누적≥20 ∧ bypass 외 failure=0 ∧ sibling merged) + evidence 6 산출물로 승격. born-red 비대칭 보존(orphan day-1=0 이라 warning 시작 안전). warning tier first per §결정 5
    progress_note: "CFP-2700 Amendment 23 carrier (orphan축) — manifest 에 선언됐으나 코드/compose/env 어떤 참조면에서도 미참조인 자원 = orphan(stale declaration, I-2 dead declaration = 결함). §1 D3 정의('orphan = warning → 안정화 후 fail')가 정확히 ADR-060 §결정 5(첫 도입 warning) → §결정 6(3-AND 승격) 모델이라 승격 로직 발명 없이 상속(AC-16). 미선언축(sibling entry infra-resource-undeclared-surface)과 §결정 3 current_tier per-entry 분리. Phase 2 = 동일 scanner(check_infra_resource_drift.py) 의 orphan 판정 분기 + registry row + hotfix-bypass:infra-resource-orphan-reconcile label. 역색인(D4) = 비커밋 ephemeral CI artifact(ADR-157 §결정 6, ADR-107 Path B 정합 — mirror-SSOT 아님 / CFP-2673 tautology 소멸). 승격 sibling merged 조건 = 미선언축 entry. owner_adr = ADR-157. warning tier first per §결정 5"
    target_section: §결정 5       # 본 Amendment 23(orphan축) = 신규 §결정 0 (framework 자연 사용 사례 entry 추가 only) — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate(3-AND) 상속, owner_adr = ADR-157
amendment_log:
  - amendment: 1
    carrier_story: CFP-390
    date: 2026-05-11
    summary: |
      4 정정 + Codex Proactive Check #2/#6 FIX iter 1 4 P1 해소 —
      §결정 6 (c) `sibling_dependencies` CFP-391 → CFP-412 verbatim 정정 (원본 inline strikethrough + Mermaid 동기) +
      §결정 12 후속 carrier 목록 CFP-391 폐기 + CFP-412 재예약 정정 +
      신설 §결정 13 인벤토리 backfill SSOT — Phase 1 (SSOT only) / Phase 2 (row append) scope split + 그룹 A final 18 entry (owner_adr 정합 ADR 명확 entry 만, 8 entry 그룹 B 강등) + tier 재계산 (manifest 부착 2 entry 만 blocking, 나머지 warning) +
      신설 §결정 14 메타 anomaly lint 후속 carrier 의무 명시 (Codex P2-B 정합)
  - amendment: 2
    carrier_story: CFP-455
    date: 2026-05-12
    summary: |
      4-tier enforcement 정식 amendment + schema MINOR bump (v1.0 → v1.1) —
      §결정 3 `current_tier` 필드 optional → required 전환 명시 + retroactive 분류 검증 의무 표기 (22/22 entry 모두 현행 `current_tier` 보유 verified, mechanical regression 0건) +
      §결정 6 (c) `sibling_dependencies` field back-substitution 결정 (append `[CFP-390, CFP-412, CFP-455]` — CFP-412 폐기 history 보존 + sibling 의도 보존) +
      §결정 14 메타 anomaly lint 와 본 Story 의 메타 schema validation lint 분리 결정 (별도 entry 2종, scope 차이 — anomaly = inventory detection / schema validation = field schema 정합) +
      신설 §결정 15 메타 lint exit-code 3-tier semantics (0=PASS / 1=validation FAIL / 2=meta-error) — Codex AREA 1 정합 +
      신설 §결정 16 warning-tier bypass_label policy (warning = non-blocking, bypass 의미 부적용 → optional + 본 메타 lint entry 자체 omit) — Codex AREA 2 (a) 정합 +
      신설 §결정 17 retroactive reclassification failure handling (immediate fail exit 1 + PR block) — Codex AREA 2 (b) 정합 +
      신설 §결정 18 marketplace/sibling sync necessity 명시 (registry yaml = wrapper-owned, ADR-010 scope 외, marketplace sync 불필요) — Codex AREA 2 (c) 정합 +
      Mermaid 다이어그램 sibling_dependencies 표기 갱신 (CFP-455 carrier 반영) — Codex AREA 4 정합
  - amendment: 3
    carrier_story: CFP-449
    date: 2026-05-12
    summary: |
      `hotfix-bypass:*` channel 의미 sharpening — §결정 7 본문에 "audit 전용 채널 — 정책 회피 등록 차단 (ADR-064 §결정 5 ratchet 정합)" 한 줄 명시 (운영 안전망 통로, 정책 회피 등록 channel 아님) +
      ADR-064 §결정 2 forbid-list 8 어휘 mechanical lint entry (`decision-principle-vocab`) 신설 cross-ref +
      evidence-checks-registry.yaml 2nd warning-tier entry 도입 = framework multi-entry 운영 검증 cross-validation 신호 (1st entry `adr-sunset-criteria` 와 schema 정합 검증) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, 의미 sharpening only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment).
  - amendment: 4
    carrier_story: CFP-481
    date: 2026-05-12
    summary: |
      3rd warning-tier entry `auto-phase-label` 등록 carrier amendment — PR open 시 phase label 자동 부착 workflow (CFP-455 + CFP-449 retro sentinel 2 재현 → mechanical enforcement 도입 timing 도달) +
      registry yaml row append (Phase 2 PR scope) — schema 변경 0건 (Amendment 2 schema v1.1 정합, `current_tier: warning` + `bypass_label: hotfix-bypass:auto-phase-label` per-entry namespace) +
      ADR-024 Amendment 4 동반 (`hotfix-bypass:auto-phase-label` 7번째 family member + branch → phase mapping 표 SSOT 신설) +
      label-registry-v2 v2.3 MINOR 동반 (phase:* 8 label entry attach_owner_plugin field 갱신 — `auto-phase-label.yml` 명시) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT permanent governance) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481]` (Amendment 2 §결정 6 (c) chain 정합 — CFP-449 / CFP-481 모두 framework 운영 검증 entry).
  - amendment: 5
    carrier_story: CFP-506
    date: 2026-05-13
    summary: |
      4th warning-tier entry `claude-md-line-cap` 등록 carrier amendment — CLAUDE.md 본문 줄수가 ADR-012 cap (≤320, CFP-506 Amendment 1 후) 초과 시 사후 감지 → 작성 시점 enforce 전환 (declaration-only ADR mechanical enforcement 확장 첫 ADR-012 cap 영역 application) +
      registry yaml row append (Phase 2 PR scope) — schema 변경 0건 (Amendment 2 schema v1.1 정합, `current_tier: warning` + `bypass_label: hotfix-bypass:claude-md-line-cap` per-entry namespace 정합) +
      label-registry-v2 v2.4 same-MINOR sub-entry append 동반 (`hotfix-bypass:claude-md-line-cap` 8번째 family member, v2.4 frontmatter `version` 미변경 — CFP-481 v2.3 → v2.4 carrier 후 본 CFP-506 = same MINOR 안 hotfix-bypass family entry append) +
      ADR-012 Amendment 1 동반 (cap ≤380 → ≤320 ratchet + §3 scope 4-층 재해석 + §결정 5/6 신설) +
      ADR-051 Amendment 1 동반 (status Draft → Accepted + §결정 7/8/9 신설 — anchor vs reference 판정자 / 5~9 skill pattern reuse / silent dead code 3-층 안전망) +
      ADR-040 Amendment 3 §결정 7.D self-application 패턴 reuse (warning tier + bypass label + audit_lint 동반, 1st/2nd/3rd entry 패턴 동일) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506]` (Amendment 2 §결정 6 (c) chain 정합).
  - amendment: 6
    carrier_story: CFP-509
    date: 2026-05-13
    summary: |
      evidence-check-registry schema v1.1 → v1.2 MINOR bump — `recurrence:` field 정식 도입
      (optional object: count / last_occurrence / threshold / promotion_trigger) +
      신설 §결정 19 — recurrence-based advisory promotion signal (recurrence.count ≥
      recurrence.threshold 시 PR comment advisory + 별도 carrier 가 actual blocking-on-pr
      승격 평가, CFP-490 lane-evidence-trail description-only recurrence_count 의 schema 흡수) +
      22 entry retroactive recurrence 검증 (lane-evidence-trail count=2 — CFP-500 FIX-5 +
      CFP-451 transient 2회 historical evidence 정합, 나머지 31 entry count=0 default) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, schema MINOR bump only
      (backward-compat — recurrence 미정의 entry 모두 정상 lint pass, ADR-058 §결정 5 sunset_justification
      의무 통과 — 강화 방향 amendment, framework SSOT permanent governance) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506, CFP-509]`
      (Amendment 2 §결정 6 (c) chain 정합).
  - amendment: 7
    carrier_story: CFP-508
    date: 2026-05-13
    summary: |
      evidence-checks-registry 32 entry name ↔ workflow file drift sweep — multi-job workflow
      pattern 정식 인정 (contract-lint.yml + lint.yml = 5+ entry 공유 jobs, registry entry
      name 과 workflow basename 자연스러운 divergence 허용) + `scripts/check-evidence-registry-naming.sh`
      신설 (workflow file 존재 검증 only, naming drift 는 allowlist hardcode warning) +
      신설 §결정 20 (entry name convention — kebab-case + workflow file name 자유 + multi-job
      pattern 허용 + Conservative no-rename policy + workflow file existence lint 의무) +
      ratchet 위반 0건 — lint scope 확장 + framework 의 자연스러운 사용 사례 정식 인정 only
      (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT
      permanent governance) + sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449,
      CFP-481, CFP-506, CFP-509, CFP-508]` (Amendment 2 §결정 6 (c) chain 정합).
  - amendment: 8
    carrier_story: CFP-530
    date: 2026-05-13
    summary: |
      N번째 warning-tier entry `workflow-permissions-block-presence` 등록 carrier amendment —
      workflow yml top-level `permissions:` block 부재 mechanical lint (warning tier first,
      hotfix-bypass:workflow-permissions per-entry namespace) carrier 직접 이행. CFP-506
      Phase 2 PR #519 CodeQL 권고 (claude-md-line-cap.yml:34 workflow permissions hardening
      unresolved review thread) + CFP-506 §11.1 entry 5 carrier 의무 + CFP-520 retro carrier
      reference 종합 해소 — wrapper repo 79 file (.github 38 + templates 41) audit 후 16 file
      remediation surface (14 MISSING + 2 JOB-LEVEL upgrade) top-level `permissions:` block
      일괄 prepend (T1 base = `contents: read` / T3 conditional override = schedule job 만
      `issues: write`, TH-7 sealed verdict 정합 — SecurityArch finalize) +
      registry yaml row append (Phase 2 PR scope) — schema 변경 0건 (Amendment 2 schema v1.1
      정합, `current_tier: warning` + `bypass_label: hotfix-bypass:workflow-permissions`
      per-entry namespace) +
      label-registry-v2 v2.5 same-MINOR sub-entry append 동반
      (`hotfix-bypass:workflow-permissions` 10번째 family member, v2.5 frontmatter `version`
      미변경 — CFP-429 v2.4 → v2.5 carrier 후 본 CFP-530 = same MINOR 안 hotfix-bypass family
      entry append, ADR-008 §결정 SemVer rule 안 same MINOR sub-entry 허용 정합) +
      ADR-063 atomic invariant 발효 (plugin.json MINOR bump 5.34.0 → 5.35.0 + CHANGELOG +
      marketplace.json sync) — Phase 2 PR scope, 3-file atomic coordination 의무 +
      CFP-300 (third-party action SHA-pinning) 직교 정책 결합 — supply chain security family
      AND 결합 (token scope 최소화 + action 신뢰성 immutable pinning) 완성 +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의
      자연스러운 사용 사례 entry 추가 only (ADR-058 §결정 5 sunset_justification 의무 통과 —
      강화 방향 amendment, framework SSOT permanent governance) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506,
      CFP-509, CFP-508, CFP-530]` (Amendment 2 §결정 6 (c) chain 정합).
  - amendment: 10
    carrier_story: CFP-662
    date: 2026-05-14
    summary: |
      10번째 warning-tier entry `bootstrap-labels-precondition` 등록 carrier amendment —
      consumer repo PR open 시점에 codeforge 필수 label set (phase:* / gate:* / type:* /
      hotfix-bypass:* / severity:* / audit:* / component:*) 부재 자동 감지 + bootstrap-labels.sh
      idempotent 호출 (RETRO-MCT-104 carrier, mctrader-data MCT-104 Phase 2 PR #14
      2026-05-09 replay sentinel). PR-time precondition check pattern 의 첫 baseline
      (CFP-583 retro 후 framework legitimacy 회복 직후 신규 entry 도입) +
      registry yaml row append (Phase 2 PR scope) — schema 변경 0건 (Amendment 6 schema v1.2 정합,
      `current_tier: warning` + `bypass_label: hotfix-bypass:bootstrap-labels` per-entry namespace) +
      label-registry-v2 v2.13 → v2.14 PATCH 동반 (`hotfix-bypass:bootstrap-labels` 20번째 family member +
      §3 yaml first-class entry, ADR-008 §결정 3 schema 무변경 row append) +
      ADR-024 Amendment 3 §결정 6.A per-entry namespace pre-existing pattern reuse (별도 Amendment 불필요) +
      `bash scripts/bootstrap-labels.sh` reuse pattern (ADR-061 §결정 1 외부 script convention 정합,
      workflow yml 본문에서 multi-line shell embed 회피 — CFP-583 BODY heredoc anti-pattern 차단) +
      consumer-guide §2h.X 자동 install 절차 명시 (Edge Case #1 CRITICAL 해소 — `regen-agents.sh`
      no-clobber copy + 신규 consumer onboarding 의무 step + §2c `*.yml` glob workflow file copy
      자동 포함) +
      chicken-and-egg deadlock 회피 (`continue-on-error: true` warning tier first entry default,
      first-PR-ever 보호 + branch protection `required_status_checks.contexts` 미부착) +
      PAT-loop prevention (`on.pull_request.types: [opened]` only filter +
      `concurrency.group: bootstrap-labels-${{ github.event.pull_request.number }}` per-PR dedup) +
      ADR-066 CODEFORGE_CROSS_REPO_PAT 90 day rotation lifetime 정합 (primary token) +
      GITHUB_TOKEN fallback (silent advisory degradation) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운
      사용 사례 entry 추가 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment,
      framework SSOT permanent governance) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506,
      CFP-509, CFP-508, CFP-530, CFP-583, CFP-662]` (Amendment 2 §결정 6 (c) chain 정합).
  - amendment: 11
    carrier_story: CFP-442
    date: 2026-05-14
    summary: |
      5번째 warning-tier entry `evidence-registry-anomaly` 등록 carrier amendment —
      Amendment 1 §결정 14 (인벤토리 anomaly lint 후속 carrier 의무) + Amendment 2 §결정 14
      (anomaly vs schema validation 분리 결정) 의 actual 이행. framework self-application
      inventory axis 의 mechanical enforcement layer 완성 (CFP-389 declaration + CFP-390
      inventory backfill + CFP-455 schema axis + CFP-508 naming convention + CFP-442 inventory
      anomaly = 5-piece self-aware governance chain). 신설 §결정 25 — 메타 anomaly lint scope
      SSOT (sub-check 1 registry yaml entries ↔ ADR-060 §결정 13 표 Group A 18 entry 1:1
      inventory parity + sub-check 2 scripts/check-*.sh + .github/workflows/*.yml +
      templates/github-workflows/*.yml 4-criteria static analysis 후보 식별 + registry 미등록
      감지 + ALLOWLIST 4-path self-exempt + start-up time assertion (EC-9 정합) + Exit code
      3-tier Amendment 2 §결정 15 정합) +
      registry yaml row append (Phase 2 PR scope) — schema 변경 0건 (Amendment 6 schema v1.2
      정합, `current_tier: warning` + bypass_label omit Amendment 2 §결정 16 warning tier
      optional 정합) +
      ADR-061 §결정 1 외부 .py split 정합 (thin bash wrapper `scripts/check-evidence-registry-anomaly.sh`
      8-10 lines + Python helper `scripts/lib/check_evidence_registry_anomaly.py` ~280-380 lines —
      CFP-455 prior art mirror) +
      ADR-063 §결정 1 atomic invariant 발효 (plugin.json MINOR bump 5.65.0 → 5.66.0 + CHANGELOG +
      marketplace.json sync) — ADR-037 신규 lint script + workflow runtime 활성화 = governance
      behavior change MINOR 분류. Phase 2 PR scope, 3-file atomic coordination 의무 + Amendment 1
      §결정 9 ArchitectAgent §3.6 proactive self-check declare (review-verdict-v4 v4.5
      `marketplace_sync_declared: true`) +
      DRIFT allowlist (CFP-508 §결정 20 partial match — `evidence-registry-anomaly` ↔
      `evidence-registry-anomaly-check.yml` substring 정합) 자동 흡수 (별도 hardcode 불필요) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의
      자연스러운 사용 사례 entry 추가 + self-application 의무 deliver (ADR-058 §결정 5
      sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT permanent governance) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506,
      CFP-509, CFP-508, CFP-530, CFP-583, CFP-662]` (Amendment 2 §결정 6 (c) chain length 11,
      self-carrier CFP-442 제외 — `adr-sunset-criteria` (carrier CFP-389) self CFP-389 미포함 +
      `evidence-registry-schema-validation` (carrier CFP-455) self `sibling_dependencies: []`
      empty prior art 정합. self promotion gate 평가 trigger = 자기 PR merge tautology 회피
      convention — F-CL-01 FIX iter 2 정정).
  - amendment: 9
    carrier_story: CFP-583
    date: 2026-05-13
    summary: |
      7th warning-tier entry `workflow-yaml-parse` 등록 carrier amendment — 6 workflow file
      (decision-principle-vocabulary / adr-sunset-criteria / auto-phase-label / worktree-first-pre-checkout /
      carrier-bootstrap-check / handoff-wording-check) 가 multi-line bash `BODY="${HEADER}\n\n\`\`\`\n${VAR}..."`
      heredoc 패턴 (block scalar 안 0-indent backtick fence + variable interpolation) 으로 인해
      yaml ScannerError 유발 → `pull_request` listener 미등록 → workflow startup_failure +
      jobs:[] empty + PR statusCheckRollup 0 attach (zero-coverage operation since carrier merge).
      framework legitimacy 훼손 sentinel — Amendment 3/4/5/6/7 의 warning-tier entry 도입 시점부터
      mechanical enforcement 가 false-PASS 운영 (작성 carrier PR merge 이후 모든 PR-time enforce 0건).
      ADR-060 framework promotion gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged)
      의 measurement 자체가 무의미 (broken workflow = absent 와 동치, sample size = 0).
      해소 + recurrence prevention validation gate 도입:
        - 6 workflow yml + 6 template self-app 정정 (BODY heredoc 정상 패턴 = printf interpolation form
          또는 ANSI-C bash `$'...'` quoting, parallel-epic-conflict-check.yml healthy reference) +
        - `scripts/check-workflow-yaml-parse.sh` 신설 (PyYAML safe_load + actionlint dual validation,
          ADR-061 §결정 1 Python script convention 정합 — multi-line Python > 5줄 외부 .py 의무 동인
          + 이번 carrier 가 yaml-shell heredoc 영역 extension 확장 첫 사례) +
        - `templates/github-workflows/workflow-yaml-parse.yml` + self-app `.github/workflows/`
          (warning tier first, `hotfix-bypass:workflow-yaml-parse` 11th hotfix-bypass family member,
          per-entry namespace ADR-024 Amendment 3 §결정 6.A 정합) +
        - registry yaml row append (Phase 2 PR scope, schema v1.2 정합 — `recurrence: count=6
          / threshold=3 / promotion_trigger=advisory` schema v1.2 Amendment 6 정합 — 6 file 동시
          actual failure 가 threshold 초과 → advisory comment trigger) +
      신설 §결정 23 (workflow yml BODY heredoc anti-pattern + 정상 패턴 정의):
        - **금지**: `run: |` block scalar 안 `BODY="${VAR}\n\n\`\`\`\n${OTHER}..."` 패턴 —
          0-indent backtick fence + 0-indent `${...}` interpolation 가 yaml scanner 의
          block scalar 종료 모호성 유발 (PyYAML strict ScannerError / GitHub Actions Go parser
          jobs:[] silent fail) +
        - **권장**: `BODY=$(printf '%s\n\n\`\`\`\n%s\n\`\`\`\n\n%s' "$HEADER" "$LINT_OUT" "$FOOTER")`
          (printf format string + variable arg = yaml scanner 영역 무관) 또는 ANSI-C bash
          `BODY=$'${HEADER}\n\n```...'` (single-quoted dollar prefix, fence 가 ANSI escape 안
          포함되어 yaml scanner 미접근) +
        - **참조 healthy pattern**: parallel-epic-conflict-check.yml line 146-152 +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 zero-coverage
      sentinel 회복 + recurrence prevention validation gate 도입 (ADR-058 §결정 5 sunset_justification
      의무 통과 — 강화 방향 amendment, framework legitimacy 회복 의무) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506,
      CFP-509, CFP-508, CFP-530, CFP-583]` (Amendment 2 §결정 6 (c) chain 정합).
  - amendment: 12
    carrier_story: CFP-734
    date: 2026-05-15
    direction: strengthen
    sunset_justification: null  # 강화 방향 amendment (신규 §결정 26 — KPI history governance scope 확장) — sunset_justification 무관 영역 (ADR-058 §결정 5 / §결정 11 framework permanent SSOT 정합)
    summary: |
      신설 §결정 26 — KPI history accumulation 메커니즘 선택 결정 규칙 SSOT.
      codeforge 의 3 KPI snapshot (rate-limit-fallback / retro-alert-pickup-rate /
      marketplace-drift-rate) 가 history 누적을 3 상이 메커니즘 (별도 *-history.jsonl /
      embedded "history" 배열 / embedded "gate_status_history" 배열) 으로 처리 — 결정 규칙
      SSOT 부재가 진짜 결함 (3 메커니즘 자체 아님). framework 의 sunset gate 측정
      (§결정 6 N consecutive months / rolling window) 이 history 누적을 암묵 전제하므로
      KPI history 메커니즘 = ADR-060 framework 의 data-substrate 하위 영역 — 신규 ADR 아닌
      Amendment host 가 구조적으로 정합 (§결정 11 framework permanent SSOT 정합).
      §결정 26 = (a) 결정 규칙 (scope boundary = metric-sample-history 만 규율,
      gate-transition/lifecycle-status log 는 scope 외 — category error 방지 +
      decidable 입력 window_shape + entry_cardinality → pattern 출력, source-of-truth
      deterministic priority = registry sunset_gate window > JSON window_months) +
      tie-break (E-1: 모호 시 jsonl / E-2: dual-window = registry gate window 우선 /
      E-2.1: governing-window 자체 미해소 시 분류 보류 + 잠정 jsonl) +
      (b) 통일 history key 명 = "history" (신규 KPI 강제, 기존 entry grandfather) +
      (c) 3-KPI 분류표 (rate-limit 정합 무변경 / retro-alert = 분류 보류 (deferred,
      dual-window 미해소 → OOS-D1 선결) / marketplace = 26.A scope 외
      (gate_status_history = transition-log ≠ metric-history) → OOS-D2) + (d) 각 패턴
      rationale (G-1 지식 공백 retroactive 해소) + (e) 본 Amendment 미해소 영역
      follow-up CFP 경계 (ADR-064 §결정 5 CFP-scope-unitary — 실제 jsonl 마이그레이션 /
      marketplace gate_status_history semantic 처리 (D-2 data-bearing + ADR-063 결합 +
      scope-out semantic) / D-1 registry-json window 불일치 정정 (retro-alert 최종
      분류 선결) = 각 독립 CFP). 모든 26.D verdict 는 26.A scope + 26.A 규칙 + 26.B
      에서 기계적으로 도출 가능 (SSOT 존재 이유 — 임의 단정 0건). lane 분류 = doc-only fast-path (ADR-054 §결정 1 — Amendment +
      src/tests/`templates/github-workflows/**` 무변경 / §결정 4 신규 ADR 회피).
      mechanical enforcement 0건 (declarative 규칙 — 분류표 검증은 향후 별 evidence-check
      entry 후보로 §결정 26 경계에 명시, 본 Amendment scope 외).
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework
      governance scope 확장 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화
      방향 amendment, framework SSOT permanent governance).
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506,
      CFP-509, CFP-508, CFP-530, CFP-583, CFP-662]` (Amendment 2 §결정 6 (c) chain 정합,
      self-carrier CFP-734 제외).
  - amendment: 13
    carrier_story: CFP-722
    date: 2026-05-16
    direction: strengthen
    sunset_justification: null  # ADR-058 §결정 5 trigger = `is_transitional: true` ADR 의 amendment. ADR-060 = `is_transitional: false` 영구 framework (§결정 11 permanent SSOT host) → trigger 자체 미해당 (약화/강화 방향 무관 — trigger 는 is_transitional 값 기준). 강화 방향 amendment (behavioral-directive-only → +mechanical-enforcement-layer 추가 = ratchet-UP) — 선행 사례 (Amendment 3/4/5/10/11) 정합. ADR-064 약화-차단 self-application 과 별개 개념.
    summary: |
      신설 §결정 27 — 11번째 warning-tier evidence-checks-registry entry
      `story-section-ownership` 등록 carrier amendment. cross-repo
      internal-docs Story PR 의 per-section diff 를 append-only
      (additions-dominant) vs destructive (high-delete-ratio, incident
      PR #441 = +216/-850 signature) 분류 + monopoly section
      (§10 CFP-32 fix-event-v1 / §13 ArchitectPL verdict / §14 ADR-031
      lane-evidence / §10.5 GitOps) author-identity attribution.
      `codeforge:lane-self-write-boundary` skill (normative behavioral
      directive SSOT) 의 mechanical-enforcement layer 추가 — ownership
      semantic 신설/재정의 0건 (ADR-031 §결정 1 FROZEN / CFP-32
      fix-event-v1 / ADR-013 dogfood-out = cross-ref only, 검증 강화).
      구조 = story-section-9-typed (CFP-410) precedent verbatim 차용
      (thin-wrapper bash + scripts/lib python SSOT ADR-061 §결정 1 +
      template/self-app byte-identical ADR-005 + continue-on-error
      warning-tier + tests/fixtures + registry row). git-ref
      failure-handling layer = NEW combination (story-section-1-immutable
      try/catch/skip MECHANICS + story-section-9-typed exit-0 VERDICT —
      어느 선례도 verbatim base 아님, 명시 설계). dual-deployment =
      wrapper template (consumer docs/stories/*.md) + wrapper self-app
      (byte-identical, sibling-workflow-parity 자동) + internal-docs
      adapted self-app (*/stories/*.md, SHA-pin 양 deployment 동일 —
      story-section-1-immutable.yml dual-deployment 선례 답습; SEC-F1
      trust-minimal = ZERO cross-repo gh api/git fetch + 신규 PAT 0건,
      3 독립 per-repo self-app, wrapper-fetches-internal-docs = net trust
      expansion = DesignReview blocker). registry yaml row append
      (Phase 2 PR scope) — schema_version 1.2 무변경 (Amendment 2 schema
      v1.1 → v1.2 Amendment 6 정합, current_tier: warning + bypass_label:
      hotfix-bypass:story-section-ownership per-entry namespace
      ADR-024 Amd3). ADR-040 Amendment 3 §결정 7.A frontmatter
      mechanical_enforcement_actions[] 신규 추가 (Amendment 12 doc-only
      action 0건 면제와 상이 — 본 Amd13 = 신규 lint carrier) + §결정 27
      ↔ story-section-ownership entry binding (§결정 7.B Pattern I).
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경
      없음, framework 의 자연스러운 사용 사례 entry 추가 + behavioral
      directive 의 mechanical layer 강화 only (ADR-058 §결정 5
      sunset_justification 의무 = is_transitional:false 영구 framework
      이므로 trigger 자체 미해당 — 강화 방향 amendment). lane 분류 =
      full-lane (신규 script/workflow 동반 → ADR-054 §결정 5 doc-only
      부적격). Phase 1 = ADR Amd13 + Story §3·§7 + Change Plan,
      Phase 2 = script/lib/2 workflow/registry row/skill cross-ref/
      ownership-yaml/regression entry/fixture.
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449,
      CFP-481, CFP-506, CFP-509, CFP-508, CFP-530, CFP-583, CFP-662,
      CFP-734]` (Amendment 2 §결정 6 (c) chain 정합, self-carrier
      CFP-722 제외).
  - amendment: 14
    carrier_story: CFP-963
    date: 2026-05-19
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 자체 미해당 (강화/약화 방향 무관 — trigger 는 is_transitional 값 기준). 본 Amendment 14 = 강화 방향 (12번째 warning-tier entry codex-network-scope-presence 등록 = framework entry count 11 → 12 ratchet-UP). ADR-064 §결정 7 top-down ratchet self-application 정합 (약화 영역 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 only + ADR-081 Amendment 4 §결정 D1.D 확장의 mechanical enforcement layer carrier).
    summary: |
      신설 §결정 28 — 12번째 warning-tier evidence-checks-registry entry
      `codex-network-scope-presence` 등록 carrier amendment. ADR-081
      Amendment 4 §결정 D1.D 본문 확장 (`sandbox_network_required: <bool>`
      → `network_scope: <4-tier enum>` strict ratchet-up) 의
      mechanical enforcement layer. ADR-040 Amendment 3 §결정 7.A
      self-application 정합 (ADR-081 frontmatter `mechanical_enforcement_actions[]`
      `[]` → list[object] entry `codex-network-scope-presence` 전환,
      declaration-only retain 본문 유지 + presence-grep warning lint
      = 보완 관계 = 상충 0).

      `codex-network-scope-presence` 영역 = Codex worker spawn-prompt 본문
      안 `network_scope` field presence-grep heuristic (4-tier enum
      value OR boolean legacy `sandbox_network_required: <bool>`
      advisory grace) + Story §10 `[codex-substitution-scope-declared: *]`
      / `[codex-sandbox-fallback: *]` marker 의 enum 정합 (membership
      check 만, semantic adequacy 검증 불가 — reviewer responsibility).
      false-positive risk 명시 — 어휘 grep heuristic 한정 (D7.a
      digest-parse 동형).

      self-meta loop 회피: 본 entry 부착 PR (Phase 1+2) 은
      `hotfix-bypass:codex-sandbox-substitution` label 또는 carrier_story
      self-exempt 채널 — ADR-024 Amendment 9 §결정 6.A 정합 (44번째
      family member).

      구조 = parallel-work-sentinel-pickup (CFP-966) / channel-drift-detection
      (CFP-932) / story-section-ownership (CFP-722) / corpus-claim-verify
      (CFP-841) precedent verbatim 차용 (thin-wrapper bash + scripts/lib
      python SSOT ADR-061 §결정 1 + template/self-app byte-identical
      ADR-005 + continue-on-error warning-tier + tests/fixtures + registry
      row). dual-deployment = wrapper template + wrapper self-app
      byte-identical mirror (ADR-005 sibling-workflow-parity 자동 강제).
      CX-963-3 P2 boundary fixture pair mandate (`tests/fixtures/
      codex_spawn_prompt_{with,without}_network_scope.txt`) carrier
      (Codex TP#4 P2 finding integration).

      registry yaml row append (Phase 2 PR scope) — schema_version
      `1.2` → `1.3` MINOR bump 동반 (evidence-check-registry-v1
      신규 optional schema field `network_scope_actual` codify, §14
      Lane Evidence 13번째 optional field carrier, CX-963-4 P3 finding
      integration). ADR-060 framework 의 schema bump 와 별 surface
      (kind:registry sibling sync 면제, ADR-010 §결정 2). evidence-check-registry-v1
      v1.2→v1.3 + MANIFEST.yaml row stale "1.1" → "1.3" atomic catch-up
      (CFP-509 v1.1→v1.2 sibling MANIFEST sync miss 영역의 INV-1
      parity ratchet — 본 CFP-963 이 silent stale 영역 catch-up + 신규
      MINOR 동반, 단일 PR 안 row write).

      label-registry-v2 v2.34 → v2.35 MINOR bump 동반 (ADR-024 Amendment 9
      §결정 6.A 의 44번째 family member `hotfix-bypass:codex-sandbox-substitution`
      append, kind:registry sibling sync 면제).

      ADR-024 Amendment 9 동반 (§결정 6.A per-entry namespace 44번째
      family member 추가 + historical-with-template-count convention
      citation per Codex TP#2 F-CX-963-A P2 calibration — active concrete
      grep count = 42 + CFP-825 template `hotfix-bypass:exempt:<entry>`
      = 43 historical Nth = 44th new, internally consistent with
      Amendment 6 §결정 6.A.2 prior art).

      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경
      없음, framework 의 자연스러운 사용 사례 entry 추가 only (ADR-058
      §결정 5 sunset_justification 의무 = is_transitional:false 영구
      framework 이므로 trigger 자체 미해당 — 강화 방향 amendment, framework
      permanent SSOT). lane 분류 = full-lane (신규 script/workflow 동반
      → ADR-054 §결정 5 doc-only 부적격). Phase 1 = 3 ADR Amendments
      (081 Amd4 + 060 Amd14 + 024 Amd9) + 2 contract MINOR
      (evidence-check-registry-v1 v1.3 + label-registry-v2 v2.35) +
      MANIFEST.yaml row catch-up + Story §3·§7·§11 + Change Plan +
      SSOT doc updates (CLAUDE.md + playbook §3.10). Phase 2 = scripts/
      check-codex-network-scope.{sh,py} + templates/github-workflows/
      codex-network-scope-presence.yml + .github/workflows/ self-app +
      tests/bats + tests/fixtures pair + .claude-work/label-registry-bootstrap.json
      + scripts/bootstrap-labels.sh 44th family member parity +
      evidence-checks-registry.yaml row append.

      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449,
      CFP-481, CFP-506, CFP-509, CFP-508, CFP-530, CFP-583, CFP-662,
      CFP-734]` (Amendment 2 §결정 6 (c) chain 정합, self-carrier
      CFP-963 제외 + CFP-722 chain 동일 — self promotion gate 평가
      trigger = 자기 PR merge tautology 회피).
  - amendment: 15
    carrier_story: CFP-1306
    date: 2026-05-25
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework → ADR-058 §결정 5 trigger 미해당. 본 Amendment 15 = 강화 방향 (13번째 warning-tier entry parallel-anchors-checked-presence 등록 = framework entry count 12 → 13 ratchet-UP). 약화 영역 0건.
    summary: |
      신설 §결정 29 — 13번째 warning-tier evidence-checks-registry entry
      `parallel-anchors-checked-presence` 등록 carrier amendment.
      review-verdict-v4 v4.9 (CFP-1303) 에서 신설된
      findings[].parallel_anchors_checked[] optional array field 의
      presence-grep heuristic mechanical lint. ADR-068 I-2 cross-module
      propagation completeness 의 review-verdict layer realization
      (Wave 1=CFP-1291 prose → Wave 2=CFP-1303 schema → Wave 3=본 carrier
      mechanical lint ADR-060 3-tier promotion canonical 사례).

      3-state semantic: absent→WARNING / present+clean→PASS /
      present+matched→PASS (clean enumeration evidence).
      5 pattern_type enum closed-set: local_remote / client_server /
      read_write / forward_reverse / enum_closure.

      dual-binding: ADR-068 I-2 = declaration source /
      ADR-060 Amendment 15 = enforcement source.
      ADR-061 Amendment 3 (CFP-1497 CodeQL ReDoS guard) 정합 —
      literal string containment only, no backtracking regex.
      bats 12 TC RED→GREEN stash proof (CFP-1334 mandate ADR-082
      §결정 11.A). Phase 1+2 동시 wire (CFP-1334 precedent —
      deferred-followup → warning 직접 전환).

      ADR-024 Amendment 14 동반 (§결정 6.A.7 per-entry namespace
      90번째 family member `hotfix-bypass:parallel-anchors-checked-presence`
      추가). label-registry-v2 v2.65 → v2.66 MINOR bump 동반.
  - amendment: 16
    carrier_story: CFP-2061-S1
    date: 2026-06-08
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 자체 미해당 (강화/약화 방향 무관 — trigger 는 is_transitional 값 기준). 본 Amendment 16 = 강화 방향 (14번째 warning-tier entry increment-justification-presence 등록 = framework entry count 13 → 14 ratchet-UP). 약화 영역 0건 (enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 only). ADR-064 §결정 7 top-down ratchet self-application 정합 (본 게이트 PR 자체가 정당화 marker 자가적용).
    summary: |
      신설 §결정 30 — 14번째 warning-tier evidence-checks-registry entry
      `increment-justification-presence` 등록 carrier amendment.
      검사(`scripts/check-*` / `(templates|.github)/workflows/*`)·ADR
      (신규 adr_number)·스크립트 신규 추가 PR 에 PR body 정당화 marker
      (`[increment-justification] why=<...> blocks-or-replaces=<...>`)
      presence-grep 강제. de-bloat 거버넌스 영속화 (CLAUDE.md
      1.8K→7.2K 재증식 = ratchet 부재 아닌 "추가마다 실효 입증 의무
      부재"의 측정 공백) 의 예방 구조 — 순증(추가) 방향 정당화 게이트.

      구조 = 두 prior art 결합 (신규 로직 표면 최소화):
      `check-tier-downgrade-guard.sh` (약화 방향 base-ref diff 가드)
      의 **순증 방향 대칭** + `check-bypass-justification-marker`
      (presence-grep / exempt 채널 / 3-tier exit / mock env bats /
      thin-wrapper bash) **구조 차용**. 신규 순수 로직 ≈ "trigger-path
      감지 ∧ marker 부재 → WARNING" 결합부 한 함수.

      trigger-path G1 closed-set (4-path, false-positive 차단):
      (a) `docs/evidence-checks-registry.yaml` entries[] row 신규
      append / (b) `scripts/check-*.{sh,py}` 신규 파일 / (c)
      `(templates|.github)/workflows/*.yml` 신규 파일 / (d)
      `archive/adr/ADR-*.md` 신규 adr_number (Amendment append 제외 —
      base-ref 에 adr_number 부재 판정). 신규 도메인 지식 doc 등 무관
      파일 미포함.

      G2 marker 형식 = PR body presence-grep (registry field schema
      아님): `^\[increment-justification\]` line-start anchor +
      `why=` substring + `blocks-or-replaces=` substring (3 AND).
      근거 = prior art bypass-justification-marker 동형 + 145 entry
      schema 확장 surface 회피 + PR = 거버넌스 변경 자연 경계.
      semantic adequacy = reviewer responsibility (presence-grep
      공통 한계).

      ADR-058/064 reference-only 연결: ADR-058 (능동 일몰 시점
      정당화) 의 방향 대칭 (추가 시점 정당화) — 능동 일몰 절차
      SSOT 는 S3 별 Story scope. ADR-064 §결정 7 evidence-gated
      symmetric ratchet 의 강화 방향 self-application 인용 (본 게이트
      PR 자체가 정당화 marker 자가적용 = top-down ratchet).

      self-meta loop 회피: 본 entry 부착 PR (Phase 2 자기 carrier) 은
      `hotfix-bypass:increment-justification` self-exempt label
      (admin-only, ADR-024 §결정 7) 또는 carrier_story self-exempt
      채널 + 자가적용 marker 이중 부착 (AC-6 dogfood, EC-5) —
      Amendment 14 `codex-network-scope-presence` self-meta loop
      회피 선례 답습.

      AC-4 exempt 잠정 경계: 보안/consumer-whitelist 영역 게이트
      예외/완화 = exempt path/tag 잠정 list (security tag entry +
      consumer-whitelist tag) 만 정의, per-path 판정 (EC-4 — 일반
      검사 부분 marker 의무 / 보안 부분만 exempt). **S2 (검사 dead
      판정 가드 + security/whitelist tag SSOT) 머지 후 정합 재확인
      의무** (OOS1 cross-ref) — S2 가 tag SSOT 확정 전이므로 본
      게이트 exempt 판정은 잠정 경계.

      ADR-040 Amendment 3 §결정 7.A frontmatter
      `mechanical_enforcement_actions[]` 신규 추가 (§결정 30 ↔
      increment-justification-presence entry binding, §결정 7.B
      Pattern I) — Amendment 12 doc-only action 0건 면제와 상이
      (본 Amd16 = 신규 lint carrier). registry yaml row append =
      Phase 2 PR scope (schema_version 무변경 — Amendment 6 schema
      v1.2 정합, `current_tier: warning` + `bypass_label:
      hotfix-bypass:increment-justification` per-entry namespace
      ADR-024). label-registry-v2 family member append
      (`hotfix-bypass:increment-justification`) = Phase 2 scope,
      kind:registry sibling sync 면제 (ADR-010 §결정 2).

      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작
      변경 없음, framework 의 자연스러운 사용 사례 entry 추가 +
      behavioral directive 의 mechanical layer 강화 only (ADR-058
      §결정 5 sunset_justification 의무 = is_transitional:false 영구
      framework 이므로 trigger 자체 미해당 — 강화 방향 amendment).
      lane 분류 = full-lane (신규 script/workflow 동반 → ADR-054
      §결정 5 doc-only 부적격). Phase 1 = ADR Amd16 + frontmatter
      entry + Story §3·§7 + Change Plan + correction-lane cross-ref,
      Phase 2 = scripts/lib/check_increment_justification.py +
      scripts/check-increment-justification.sh + templates/
      github-workflows/increment-justification.yml + .github/
      workflows/ self-app + tests/bats + tests/fixtures + registry
      row + label-registry family member.

      sibling_dependencies append `[CFP-390, CFP-412, CFP-455,
      CFP-449, CFP-481, CFP-506, CFP-509, CFP-508, CFP-530, CFP-583,
      CFP-662, CFP-734]` (Amendment 2 §결정 6 (c) chain 정합,
      self-carrier CFP-2061-S1 제외 — self promotion gate 평가
      trigger = 자기 PR merge tautology 회피 convention).
  - amendment: 17
    carrier_story: CFP-2061-S4
    date: 2026-06-09
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework → ADR-058 §결정 5 trigger 미해당. 본 Amendment 17 = 강화 방향 (15번째 warning-tier entry governance-drift-detection 등록 = framework entry count 14 → 15 ratchet-UP). 약화 영역 0건.
    summary: |
      신설 §결정 31 — 15번째 warning-tier evidence-checks-registry entry
      `governance-drift-detection` 등록 carrier amendment.
      거버넌스 지표 7종(검사수/워크플로수/매-PR워크플로/셸수/셸LOC/ADR수/ADR바이트)
      baseline JSON 대비 drift 상대 증가율 임계 초과 시 이슈 자동 발행 (dedup).

      dedup signature = sha256("governance-drift|<metric>|increase|<bucket>") — current_val 절대 제외.
      포함 시 매일 signature 변동 → dedup 무력화 → 이슈 폭주 (D4 함정 회피).
      advisory exit 0 (warning tier — PR 게이트 아님).

      구조 = prior art 답습 (신규 발명 0):
        check-marketplace-drift.sh (cron+drift+sha256 dedup+이슈자동+warning+401/429/5xx)
        bypass-label-counter.py (dedup signature count 제외 + dry-run + _SKIP_ISSUE_CREATE)

      Phase 2 산출물: scripts/lib/check_governance_drift.py (SSOT) +
      scripts/check-governance-drift.sh (ADR-061 thin wrapper) +
      templates+.github/workflows/governance-remeasure-cron.yml (ADR-005 byte-parity) +
      docs/kpi/governance-bloat-baseline.json (provisional, D5) +
      docs/kpi/governance-bloat-history.jsonl + tests/bats 19 TC RED->GREEN +
      registry entry + label-registry-v2 v2.91 (hotfix-bypass:governance-drift).

      ratchet 위반 0건 (enum/tier/bypass channel 동작 변경 없음,
      framework 자연 사용 사례 entry 추가 only. ADR-064 §결정 7 정합).
      ADR-058 §결정 5 sunset_justification 의무 = is_transitional:false 영구
      framework trigger 자체 미해당.
  - amendment: 18
    carrier_story: CFP-2381
    date: 2026-06-20
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 자체 미해당 (강화/약화 방향 무관 — trigger 는 is_transitional 값 기준). 본 Amendment 18 = 강화 방향 (16번째 warning-tier entry deferred-followup-reconcile 등록 = framework entry count 15 → 16 ratchet-UP + §결정 19 auto_blocking 라벨에 mechanical forcing function 결합). 약화 영역 0건 (enum 값 / tier 추가 / bypass channel 동작 변경 없음).
    summary: |
      신설 §결정 32 — 16번째 warning-tier evidence-checks-registry entry
      `deferred-followup-reconcile` 등록 carrier amendment + §결정 19
      auto_blocking 라벨의 mechanical forcing function 결합.

      직접 동인 (Story §2 carrier-부재 검출): §결정 19 (Amendment 6)
      이 `recurrence.promotion_trigger: auto_blocking` 을 "별도 carrier
      Story 가 actual 승격 평가 의무" 로 선언했으나 (§결정 19 L1143
      "자동 transition 아님 — governance 보존" + §결정 6 승격 gate 는
      *더 나중* 단계), **carrier 발의 자체를 강제하는 mechanical
      forcing function 이 framework 어디에도 부재**. 결과 = "임계
      초과 + auto_blocking 선언 + 전용 carrier 부재" entry 가 적체
      (issue-body-claim-pre-screen count 7/3 + spawn-prompt-fact-verify
      count 3/3 + stale-local-main-checkout-divergence-check count 8/3
      등) 되어도 무경보. worktree 정리(CFP-2377) / de-bloat 재증식
      (CFP-2061-S4) 와 동일 병 — 규정 있고 강제 없음.

      carrier-부재 검출 방식 = **detect_command/workflow 가 가리키는
      파일의 실존 여부** (deterministic + 외부의존 0 + CI offline 가능
      + backfill 0). registry 데이터에 이미 박혀 있는 신호 — 2026-06-10
      de-bloat 가 "detect_command·workflow 가 가리키는 워크플로 부재 =
      실행경로 0 거짓 inventory" 로 3 entry 제거한 선례 (registry
      last_updated log) 와 동형. carrier-부재 = (detect_command 경로
      ABSENT) OR (workflow 경로 ABSENT) — 둘 중 하나라도 부재면
      carrier-incomplete (stale-local-main = script EXISTS but workflow
      ABSENT 사례가 OR 의 근거).

      검출 status 필터 경계 (Story 결정점 2) = **status-agnostic broad
      criterion 채택** (chief author 판정). 1급 firing 조건 =
      (count >= threshold) AND (promotion_trigger == auto_blocking) AND
      (carrier 부재). status 무관 — `status: deferred-followup` 뿐 아니라
      `status: Active` 로 의도 등록된 stale-local-main (Wave 2 mechanical
      wire 자체이나 workflow 미배선) 도 포착. forcing function 의 실제
      의도 = "강제됐어야 하는데 안 된 것" 전부 (status 라벨 아닌 실제
      배선 결손). warning-tier 이므로 broad-scope noise 비차단 (false
      positive 비용 = advisory only). promotion_trigger == advisory +
      over-threshold = secondary informational tier (강제 아님 — §결정 19
      advisory 의미 보존). warning_tier_initial entry (fix-loop-reverify
      / retro-fact-verify) 는 firing scope 외 (auto_blocking/advisory
      아님 — "should-be-blocking" 신호 아님), §32.B 에 명시.

      강제 action 3택 (검출 시 warning emit): ① 배선 carrier
      (script+workflow) 발의 (#1602 5-element 템플릿 자원) / ②
      `tier-downgrade-justification:` 근거 강등 (선례
      check-tier-downgrade-guard.sh 마커 패턴) / ③ 폐기 (entry 제거).

      STALE 2건 status flip (Story 결정점 4, Phase 2 impl 대상):
      bootstrap-labels-precondition (registry L965) + schema-change-
      7-principles-self-check (registry L1590) 둘 다 `status:
      deferred-followup` → flip. firsthand 실측 — bootstrap-labels:
      scripts/bootstrap-labels.sh + templates/+.github/workflows/
      bootstrap-labels.yml 3 file EXISTS / schema-7: scripts/check-
      schema-7-principles.sh (Python delegate 실구현) + templates/+
      .github/workflows/schema-7-principles-check.yml 3 file EXISTS.
      schema-7 L1591/L1592 `# TBD — S2 carrier wire` 주석은 stale
      (파일 실재) → status flip + TBD 주석 2건 제거 동반. flip 방향 =
      deferred-followup → Active = 강화 방향 (검사 실작동 상태). 강등
      아님 → tier-downgrade-justification 마커 불요. (Architect §3 에서
      check-tier-downgrade-guard.sh 가 flip 을 무단하향 오탐하는지 확인
      의무.)

      self-application 무한루프 회피 (Story 결정점 3): 본 게이트
      self-entry `deferred-followup-reconcile` 는 처음부터 `status:
      Active` (current_tier: warning) 등록 + detect_command/workflow
      실파일을 동일 Phase 2 PR 에 동반 신설 → 자기 검출 시 carrier
      실존으로 자연 PASS (별도 self-skip 분기 불요). 선례 =
      adr-citation-slug entry (registry "자기 진원 RED 0 → status:
      warning 직접") + Amendment 11 evidence-registry-anomaly ALLOWLIST
      self-exempt.

      schema doc drift catch-up (권고, Architect 재량): docs/inter-
      plugin-contracts/evidence-check-registry-v1.md `status` field enum
      = `Active / Deprecated / Archived` (L70) 인데 registry 에
      `deferred-followup` 20건 사용 중 (schema-lint 미검출 drift). 본
      게이트 carrier 가 부수 해소 여부 = Architect 판단 (scope cohesion
      vs CFP-scope-unitary ADR-064 §결정 5 — Phase 1 schema doc enum
      append 1줄 = 본 게이트 status-scan 의 데이터 정합 기반이므로
      cohesive 추정).

      중복 0 (Story §8 disjoint 입증): #1600/#1687 (current_tier 축
      warning→blocking 승격, 더 나중 단계) + #2166 (신규 entry 도입
      carrier) 와 disjoint — 본 게이트 = status 축 (선언만 ∧ 미배선 ∧
      임계초과 carrier-부재 검출). #1602 = 자원-사용 (① 배선 강제 시
      5-element 템플릿 소비).

      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작
      변경 없음, framework 의 자연스러운 사용 사례 entry 추가 +
      §결정 19 auto_blocking 라벨의 mechanical layer 강화 only (ADR-058
      §결정 5 sunset_justification 의무 = is_transitional:false 영구
      framework 이므로 trigger 자체 미해당 — 강화 방향 amendment).
      lane 분류 = full-lane (신규 script/workflow 동반 → ADR-054
      §결정 5 doc-only 부적격). branch protection 6-tuple 무변경
      (ADR-127 ratchet — required 신설 0). change-plan 면제 = ADR-carrier
      (본 Amendment 가 설계 서사 host, ADR-054 §결정 4 신규 ADR 회피 +
      framework self-application sub-decision 은 Amendment host 구조적
      정합 §결정 11). Phase 1 = ADR Amd18 + frontmatter entry + Story
      §3·§7 + (schema doc enum drift catch-up 권고) + STALE 2 flip
      준비, Phase 2 = scripts/lib/check_deferred_followup_reconcile.py +
      scripts/check-deferred-followup-reconcile.sh + templates/
      github-workflows/deferred-followup-reconcile.yml + .github/
      workflows/ self-app byte-identical + self-validation test job +
      registry self-entry append + STALE 2 status flip + TBD 주석 제거 +
      plugin.json MINOR bump (marketplace sync).

      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449,
      CFP-481, CFP-506, CFP-509, CFP-508, CFP-530, CFP-583, CFP-662,
      CFP-734]` (Amendment 2 §결정 6 (c) chain 정합, self-carrier
      CFP-2381 제외 — self promotion gate 평가 trigger = 자기 PR merge
      tautology 회피 convention).
  - amendment: 19
    carrier_story: CFP-2426
    date: 2026-06-26
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 자체 미해당 (강화/약화 방향 무관 — trigger 는 is_transitional 값 기준). 본 Amendment 19 = 강화 방향 (17번째 warning-tier entry lane-count-ssot-consistency 등록 = framework entry count 16 → 17 ratchet-UP). 약화 영역 0건 (enum 값 / tier 추가 / bypass channel 동작 변경 없음).
    summary: |
      신설 §결정 33 — 17번째 warning-tier evidence-checks-registry entry
      `lane-count-ssot-consistency` 등록 carrier amendment + canonical
      작업레인 수(10, ADR-125 Amendment 1) SSOT mechanical consistency
      enforcement.

      직접 동인 (33.A 메우는 갭): ADR-125 Amendment 1 (CFP-2341) 이
      canonical lane 수=10 을 정본 SSOT 로 박았으나(registration),
      분산 governance 문서 사본이 그 사실에 단조 유지되도록 강제하는
      mechanical enforcement 가 부재. 그 결과 stale `N 레인`/`N번째 lane`
      (N≠10) drift 가 **2 Story 연속(CFP-2341 → CFP-2376) leak**. 두
      선행 Story 모두 manual text-fix 만 수행(lint 0). "registration
      완료 ≠ enforcement 실효" 전형 (story-section-ownership /
      governance-drift 와 동일 병 — 규정 있고 강제 없음).

      검출 1급 firing 조건 (33.B): flag(line) := stale_token_match(line)
      AND NOT allowlist_match(line). detect 정규식 = `([6-9])\s*레인` /
      `레인\s*([5-9])개` / `([6-9])번째\s*lane` (N≠10). exit 3-tier
      (§결정 15): 0=PASS(FLAG 0) / 1=FLAG 1+(::warning:: emit,
      continue-on-error 비차단) / 2=SETUP. ReDoS-safe = line-by-line
      scan (multi-line backtracking regex 0) + anchored bounded
      quantifier.

      allowlist 5축 (33.C, load-bearing): ①within-line 이중토큰
      (`N lane plugin` — plugin-count 별 축 ADR-023) / ②negation
      (`N번째 lane 이 아니다`) / ③history(date행·amendment_log span·
      source_section·버전이력표·토큰-인접 이벤트동사) / ④path 제외
      (archive/adr/·docs/cross-repo-patches/) / ⑤counterfactual
      (`만약 ... N번째 lane 으로 신설하면 ... 충돌` 가정 조건절). 면제
      단위 = syntactic channel(line-prefix key) 또는 counterfactual
      마커, 토큰 자체 아님. same-file channel-split: live
      `description:`/`section:` 값=검출 vs `date:`/`source_section:`/
      amendment_log span=면제. amendment_log span = line-local boolean
      toggle(enter=헤더 key / exit=dedent·sibling list·다음 top-level
      key), multi-line regex 0(ReDoS-safe). over-broad 금지 = span
      무한확장 시 sibling live `description:` STALE 까지 silent 면제
      (AC-8 false-negative) — F-CHANNEL-1 multi-line block fixture +
      Mutation-3 kill 로 구조적 보장.

      N-range = canonical-10 특정값 detection (33.B / §7.B9 D4
      documented-limitation): 현 정규식 N∈{5,6,7,8,9} 하드코딩은
      canonical=10 기준 검출이다. 미래 lane 증감(canonical→11) 시
      `11 레인` 류를 silent 미검출(false-negative)하며 self-test
      ({5..9} fixture)도 이 갭 미검출 → lane count canonical 값을
      바꾸는 미래 ADR-125 Amendment 는 본 lint 정규식의 N-range 갱신
      (+ self-test fixture range 확장)을 그 Amendment 의 REQUIRED
      mechanical-sync carrier 항으로 포함해야 한다 (구조 재설계 불요).

      self-application (33.D): self-entry `lane-count-ssot-consistency`
      는 처음부터 `status: Active` (current_tier: warning) 등록 +
      detect_command(scripts/check-lane-count-ssot.sh) / workflow
      (.github/workflows/lane-count-ssot.yml) 실파일을 동일 Phase 2 PR
      에 동반 신설 → 자기 검출 시 carrier 실존 자연 PASS. self-entry
      description 자체에 count 토큰(N≠10) 미포함 의무 (자기 검출 회피
      — `9번째 lane 이 아니다` 류 예시 인용 시 negation/history 채널만).
      선례 = Amendment 18 §32.E (deferred-followup-reconcile self-entry).

      pattern_count=2 정당화 (33.E / §3.4): 2 Story 연속 leak = manual
      정정의 구조적 한계 입증. ADR-060 승급 임계치(재발 ≥3)는 advisory
      (hard-invariant 아님) — PMO authority 재평가로 pattern_count=2
      에서 warning-tier *도입* 정당 (§결정 5 첫 도입 = warning;
      §결정 19 promotion gate 는 warning→blocking 승격용이지 warning
      도입 임계치 아님).

      anti-theater test (33.F / AC-7 / CFP-1334): self-test job
      (scripts/test-check-lane-count-ssot.sh) — 22 fixture(F-DET ×4 /
      F-HIST ×5 / F-DUAL ×2 / F-NEG / F-COUNTERFACTUAL ×2 / F-TRANS ×2 /
      F-CHANNEL ×2 / F-BORDER / F-EXIT ×3) + 4 mutation(detect 정규식
      제거 / allowlist OR false / amendment_log span exit 미감지
      over-broaden / counterfactual over-broaden) 양방향 mutation 생존 0.
      content-anchor fixture (line# 하드코딩 0 — 요구사항리뷰 R1 교훈).

      lane 분류 = full-lane (신규 script/workflow 동반 → ADR-054 §결정 5
      doc-only 부적격). branch protection 6-tuple 무변경 (ADR-127 ratchet
      — required 신설 0 / process-skip 채널 0). change-plan 면제 =
      ADR-carrier (본 Amendment 가 설계 서사 host, ADR-054 §결정 4 신규
      ADR 회피 — standalone ADR-132 기각, ADR-060 framework 의 자연스러운
      17번째 entry). Phase 1 = ADR Amd19 + frontmatter entry + Story
      §3·§7·§8, Phase 2 = scripts/lib/check_lane_count_ssot.py +
      scripts/check-lane-count-ssot.sh + .github/workflows/
      lane-count-ssot.yml (.github single-root, deferred-followup-
      reconcile 동형) + scripts/test-check-lane-count-ssot.sh + registry
      self-entry append + plugin.json tagline lane-count 8→10 STALE 정정
      + plugin.json 6.38.0 → 6.40.0 MINOR bump (marketplace-atomic sync
      ADR-063 — 6.39.0 = CFP-2428 #2430 병렬 세션 선점, 6.40.0 회피).

      genuine STALE sweep 정정 = OOS 분리 (§1.4 / §7.0): 현 main
      genuine current-state STALE = label-registry-v2 live `description:`
      `9번째 lane` ×3 / base-labels.tsv `9번째 lane` ×1 / section-
      ownership.yaml `section:` 값 `레인 5개`·`레인 8개` ×2 — 본 lint
      신설 직후 self-run 이 RED 검출(의도된 warning, 비차단). 실 정정 =
      registry version bump carrier / section-ownership owner carrier
      별 분리(OOS). plugin.json tagline 만 본 Story 정정 (marketplace-
      touching). LANES 8→10 배열 확장 (check-lane-evidence.sh, 배포·
      배포-리뷰 누락) = name-array 불일치 (count 토큰 정규식 비매칭,
      lint scope 외) → 별 carrier tracked follow-up (§5.5-4 / §7.B5 D5).

      중복 0 (disjoint): #1600/#1687 (current_tier 축 승격) + #2166
      (신규 entry 도입) 와 disjoint — 본 게이트 = governance 문서
      자기일관성 grep 검출 축 (lane-count drift). ADR-023 = lane
      *plugin* count(8) 별 축 (cross-ref, 충돌 아님 — allowlist 축①
      도메인 근거). ADR-125 Amd1 = enforce 대상 ground-truth (충돌 아님).

      ratchet 위반 0건 — framework 의 자연스러운 사용 사례 entry 추가
      only (ADR-058 §결정 5 sunset_justification 의무 = is_transitional:
      false 영구 framework 이므로 trigger 자체 미해당 — 강화 방향
      amendment).
  - amendment: 20
    carrier_story: CFP-2591
    date: 2026-07-10
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 자체 미해당. 본 Amendment 20 = 강화 방향 (18번째 warning-tier entry deferral-carrier-declared 등록 + grandfather baseline 메커니즘 신규 §결정 + §결정32.D surfacing tier 도입 = framework entry count 17 → 18 ratchet-UP). 약화 영역 0건 (enum 값/tier 제거 없음, surfacing = 신규 sub-mode append).
    summary: |
      §결정 32.D 개정 (surfacing tier 도입) + grandfather baseline 메커니즘
      framework-wide 신규 §결정 + (b) carrier-mandate no-TBD lint entry
      (18번째 warning-tier entry `deferral-carrier-declared`) 등록 carrier
      amendment. deferred-followup forcing-function 봉합 Stage 1+2
      (baseline + new-only shadow).

      ★ NO-FLIP: 본 CFP-2591 PR 은 Stage 1+2 (baseline + new-only shadow)
      까지만 ship — 실제 continue-on-error 제거(flip → blocking-on-pr
      surfacing) 및 self-entry tier 승격은 baseline main 착지 후 별 후속
      PR (§7.2.2 self-deadlock 회피). Tier 2 (hard-required, 6-tuple 편입)
      = FUTURE/OOS.

      (a) §결정32.D 개정: "warning emit, blocking 아님" → `blocking-on-pr
      (surfacing)` tier(Tier 1) 도입 — continue-on-error 제거로 red-X +
      sticky 표면화, required 6-tuple 미편입. 단 본 PR 은 flip 미포함
      (shadow 까지만).

      §결정3 reconciliation (F-3): §결정3 tier-table 이 `blocking-on-pr`
      을 "required check·contexts 부착"으로 정의 → surfacing(비-required)
      의미와 상충. Amendment 20 이 `surfacing` qualifier 도입 —
      `current_tier: blocking-on-pr` 자체가 6-tuple/contexts membership 을
      함의하지 않음 (surfacing sub-mode = continue-on-error 제거만·contexts
      무변경). 실측 drift(worktree-first 3 entry blocking-on-pr ∧ contexts
      미부착) + Amendment 1 FIND-4 정합.

      §결정6 harmonization: `failure=0` 을 baseline-relative(new-debt
      failure=0)로 재해석 — Clean-as-You-Code ↔ §결정5 warning-first 조화.

      grandfather baseline 메커니즘 (framework-wide 신규 §결정):
      `docs/deferred-followup-baseline.yaml` (enumerated-freeze / 2-owner
      section / single-writer gen tool / content_digest tamper-evident /
      monotonic shrink). new-only (SonarQube Clean-as-You-Code) + betterer
      ratchet.

      (b) carrier-mandate entry: deferral 선언 시 carrier CFP + registry
      등재 필수화, 미해결 placeholder(TBD 마커/미명명 FU 마커) 금지
      (no-TBD lint). declared→registered 강제 결합 (§2.3). (a) registry
      FLAG 는 sibling deferred-followup-reconcile 소관 — 두 축 disjoint.

      §결정6 carrier trio (self-entry evidence_artifacts 3종 배선):
      outage runbook(iv) + author-verify lint(v) + sticky at-most-once(vi).

      ADR-127/ADR-024 amendment 불요: Tier 1 surfacing 이 6-tuple 회피 →
      §9.1 SSOT 무변경 + §9.4 bypass invariant 미발화. honest forcing
      ceiling: 게이트는 hard block 미주장 — admin 우회 구조적 가능, AC-20
      count #4 로 관측만.

      ratchet 위반 0건 — framework 자연스러운 사용 사례 entry 추가 +
      surfacing sub-mode append (ADR-058 §결정 5 sunset_justification
      의무 = is_transitional:false 영구 framework trigger 미해당 — 강화
      방향 amendment).
  - amendment: 21
    carrier_story: CFP-2597
    date: 2026-07-10
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 미해당. 본 Amendment 21 = 강화 방향 (19번째 warning-tier entry peer-completion-falsifiability 등록, framework entry count 18 → 19 ratchet-UP). 약화 영역 0건 (enum 값/tier 제거 없음, 신규 §결정 0 = §결정 5/6 절차 상속).
    summary: |
      19번째 warning-tier entry `peer-completion-falsifiability` 등록 carrier
      amendment — ADR-044 Amendment 6 §결정 12 (check-verification-floor.sh
      축③ peer-completion falsifiability) 의 warning-tier check 등록. 신규
      §결정 0 — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate
      (pr_cumulative_min 20 / failure_threshold 0 / sibling merged) 상속.

      owner_adr = ADR-044 (축③ 결정 SSOT), carrier_adr = ADR-060 (framework
      host). evidence-checks-registry.yaml `peer-completion-falsifiability`
      entry mirror (registry yaml row append, Phase 2 PR scope — schema 변경
      0건, current_tier: warning + bypass_label omit 선례 tier-honesty /
      spawn-description-prefix-detect / deferral-carrier-declared 답습).

      게이트 의미: PASS verdict 이 review-verdict-v4 §19 peer_verdicts[]
      artifact-backed 완료 증거를 동반하도록 강제 — 각 target(dirname(verdict_path)
      기준 상대) FS 실재+non-empty 를 게이트가 독립 stat (자기단언 verify_status
      불신, ADR-119 §결정 10 outcome-honesty). peer_count:0+PASS = 축① 선차단 /
      honest-single-peer-degrade = 축② 위임 (축③ stand-down, AC-A3 무회귀).
      non-version-gated (anti-evasion). ★ check-lane-evidence.sh 축③
      (deputy/role:dev fan-out, ADR-044 §결정 10 (d)) 와 별개 — 이름만 동일,
      script·axis disjoint.

      정직 상한 (ADR-044 §3.4): 축③ = 위조비용 상향 + audit trail 이지
      위조방지 게이트 아님 (PL claim+proof 동시저작 → full falsifiability 불가).
      warning-tier = 정직 상한, blocking 승격 = false assurance. full
      falsifiability = Epic trapdoor (stop-event 강화 / spawn-event-v1 선행).
      Phase 1 governance-doc = ADR-044 Amendment 6 + review-verdict-v4 v4.16
      (peer_verdicts[] additive MINOR) + MANIFEST mirror + review-pl-base §3/§10
      + orchestrator-playbook §3.10.1 active-resume/I-6.6 이식 + evidence-checks-registry
      entry. 실 script + workflow + discriminating test = sibling worker Phase 2
      deliverable. plugin.json 6.73.1 → 6.74.0 MINOR + codeforge-review 1.21.0 →
      1.22.0 MINOR + marketplace sync.

      ratchet 위반 0건 — framework 자연스러운 사용 사례 entry 추가 only
      (ADR-058 §결정 5 sunset_justification 의무 = is_transitional:false 영구
      framework trigger 미해당 — 강화 방향 amendment). 기존 §결정 5/6 본문
      의미 변경 0건.
  - amendment: 22
    carrier_story: CFP-2635
    date: 2026-07-12
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 미해당. 본 Amendment 22 = 강화 방향 (20번째 warning-tier entry shell-test-exit-masking-detect 등록, framework entry count 19 → 20 ratchet-UP). 약화 영역 0건 (enum 값/tier 제거 없음, 신규 §결정 0 = §결정 5/6 절차 상속, 기존 본문 의미 변경 0).
    summary: |
      20번째 warning-tier entry `shell-test-exit-masking-detect` 등록 carrier
      amendment (원천 backlog #960) — codeforge 거버넌스 shell self-test 코퍼스
      (`scripts/test-*.sh` 33 + `tests/scripts/*.sh` 37 = 70 file [verified])의
      false-coverage 2종을 정적 lint 로 검출: (a) raw `cmd || true` exit-masking
      (cmd exit 이 유일 pass/fail 신호이고 하류 FAIL 카운터/assertion 부재 = 항상
      PASS) + (b) mock-seam env export 후 동반 assertion 부재. 신규 §결정 0 —
      §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate (pr_cumulative_min 20
      / failure_threshold 0 / sibling merged) 상속. 신규 mechanism 0 (기존 5-piece
      chain 재사용) → A2-5 판정: Amendment prong 채택 / 신규-ADR prong 기각
      (ADR-151 §결정1 verbatim 구조 역적용 — 신규 ADR 은 corpus-wide 인벤토리
      메타-게이트라는 신규 mechanism 도입 시, 본 건은 framework 자연 사용 사례
      entry 추가라 신규 mechanism 0 → Amendment). ADR 번호 충돌 회피
      (병렬 세션 CFP-2602/2628 ADR 활발 신설, max=152) 부수 효과.

      owner_adr = ADR-060 (framework host = enforcement source). honesty-ceiling
      source = ADR-151 §결정7 상속 — 본 게이트는 **naive/구조적 masking 패턴만**
      검출 (bare `|| true` on raw command + mock-seam-export-무-in-scope-companion-assert).
      검출력(surviving test 가 실제 mutation 을 죽이는가)은 **미강제**(G3/review/QADev
      discriminating-case 소관). "false-coverage 완전 봉인" hard-claim 금지 — presence/형식
      천장. ADR-151 selftest-execution-liveness 인벤토리 등재(discriminating_fixture:
      present / blocking_tier: warning_tier 정직 기록).

      ★ 1급 정밀도 요건 (anti-hollow-gate) — 정당 `|| true` 3종(§2.4) 오탐 0 제외:
      (i) counter-backup `assert_* || true`(assert helper 가 `FAIL=$((FAIL+1))` 증가,
      `set -euo pipefail` 중도종료 가드, 종료 `[ $FAIL -eq 0 ]`) / (ii) `((c++)) || true`
      산술 idiom / (iii) production `cmd 2>/dev/null || true` best-effort 값 캡처
      (enforcement 신호 아님). 정밀도 keystone = **logical-line 재구성**(backslash
      continuation join) 후 leading-command-token 분류 — 다중행
      `assert_grep_all "$F" "name" \ "p1" \ "p2" || true`
      (test-cfp-2521-presence.sh:92-95 [verified])의 `|| true` 가 continuation 행에
      있어도 logical head token=`assert_grep_all`(assert-family) 로 정당 판정.
      naive line-grep 은 `"direction: strengthening" || true` 를 masking 오탐 →
      코퍼스 149행 `|| true` 대부분 오탐 폭발 → lint 자체가 hollow/noisy gate
      (자기모순, ADR-119 위반). 재구성이 이를 원천 차단. + branch-guard
      (`if cmd || true; then`) / heredoc·comment literal 제외.

      대상 재지정 (원 #960 오칭 정정): codeforge 는 bats 미사용 — 원 제안의
      "bats masking lint"를 문자대로 구현 시 대상 프레임워크 부재 dead gate
      (removed orphan `bats-red-green-proof-presence` 2026-06-10 de-bloat 재발).
      대상 = codeforge 실 shell 코퍼스. scope 밖: `plugins/codeforge-test/**/*.bats`
      2 fixture(통합테스트 example-story baseline, 거버넌스 코퍼스와 disjoint —
      RR-2635-1) + tests/scripts/ Python/JS.

      Phase 1 (본 PR) = ADR-060 Amendment 22 + Change Plan
      (internal-docs `wrapper/change-plans/cfp-2635-shell-test-exit-masking-detect.md`)
      + Story §3/§7. Phase 2 = scripts/lib/check_shell_test_masking.py (Python SSOT,
      ADR-061 §결정 1 offline/read-only/argparse/pathlib, ReDoS-safe anchored
      리터럴+\d+ line-by-line) + scripts/check-shell-test-masking.sh (thin wrapper)
      + .github+templates/github-workflows/shell-test-exit-masking-detect.yml
      (byte-identical pair ADR-005, injection-safe pull_request + permissions
      contents:read) + tests/scripts/test_check-shell-test-masking.sh (discriminating
      fixture RED→GREEN — masking TC 검출 / 정당 3종 미검출 / mutation-kill) +
      docs/selftest-execution-liveness-inventory.yaml 레코드 append(ADR-151 AC-1a
      bijection) + registry row append + hotfix-bypass:shell-test-exit-masking-detect
      label(label-registry-v2 MINOR). Layer 1(thin) = DeveloperPLAgent packet mandate
      (raw `|| true` 금지 + mock-seam export 시 동반 assertion 의무). Layer 3 =
      QADeveloperAgent discriminating-case 이미 존재(obviated).

      prior art 답습: check_selftest_execution_liveness.py(house style + helper
      decomposition) + check_spawn_prompt_fact_verify.py(ReDoS-safe
      line-by-line scan) + subagent-wait-liveness-presence(byte-identical workflow
      + execution-backed self-test + spec_invariant_measurement_required:false).
      신규 발명 0.

      ratchet 위반 0건 — framework 자연스러운 사용 사례 entry 추가 only
      (ADR-058 §결정 5 sunset_justification 의무 = is_transitional:false 영구
      framework trigger 미해당 — 강화 방향 amendment). 기존 §결정 5/6 본문
      의미 변경 0건. plugin.json bump + marketplace sync = Phase 2 PR scope
      (ArchitectAgent Phase 2 판단, ADR-063).
  - amendment: 23
    carrier_story: CFP-2700
    date: 2026-07-16
    direction: strengthen
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 미해당. 본 Amendment 23 = 강화 방향 (21+22번째 warning-tier entry infra-resource-undeclared-surface + infra-resource-orphan-reconcile 등록, framework entry count 20 → 22 ratchet-UP 2건). 약화 영역 0건 (enum 값/tier 제거 없음, 신규 §결정 0 = §결정 5/6/32.D/Amd20 절차·기제 상속, 기존 본문 의미 변경 0).
    summary: |
      21+22번째 warning-tier entry `infra-resource-undeclared-surface` +
      `infra-resource-orphan-reconcile` 등록 carrier amendment (CFP-2700 D3) —
      인프라 자원 선언 manifest(consumer/wrapper-self `.claude/_overlay/project.yaml`
      `infra_resources:` block) vs 코드·compose·env 템플릿 스캔 표면명 대조 CI
      drift 게이트. owner_adr = ADR-157 (D1~D5 결정 SSOT — 인프라 자원 manifest +
      startup fail-closed + drift scan), carrier_adr = ADR-060 (framework host).

      **2 entry 분리 근거** (§결정 3 current_tier = entry 당 1개): D3 는 2축이
      비대칭 tier 라 단일 entry 로 표현 불가 →
      (1) `infra-resource-undeclared-surface`(미선언 표면명 = 코드/compose/env
      스캔 표면이 alias→canonical 정규화 후에도 manifest 미선언·미분류, env 키
      난립 차단) = new-only ratchet(Amendment 20 grandfather baseline 재사용) +
      §결정 32.D surfacing tier. NO-FLIP(§7.2.2): Phase 2 = warning + baseline
      동시 착지, 실제 continue-on-error 제거(flip → blocking-on-pr surfacing)는
      baseline main 착지 후 별 후속 PR (baseline 도입 PR 자신이 surfacing 이면
      self-deadlock). required 7→8 미편입(§결정 32.D surfacing = contexts membership
      미함의) → ADR-145 §결정 3 narrowing override 불요 (ADR-060 이 fail-closed
      비호환 아님, 반대로 native 지원).
      (2) `infra-resource-orphan-reconcile`(선언됐으나 어떤 참조면에서도 미참조
      = dead declaration, I-2) = §결정 5 warning first → §결정 6 3-AND
      (pr_cumulative_min 20 / failure_threshold 0 / sibling merged[=미선언축
      entry]) 승격. born-red 비대칭 보존(orphan day-1=0 이라 warning 시작 안전).

      신규 §결정 0 — §결정 5 warning-tier 등록 절차 + §결정 6 promotion gate +
      Amendment 20 grandfather baseline(new-only) + §결정 32.D surfacing 상속.
      신규 승격/baseline mechanism 발명 0 (CFP-2700 AC-16 — 기존 기제 재사용).

      **死因 3-mode 봉인** (이 repo 에서 drift 게이트가 죽는 패턴 — ADR-011
      Proposed 영구 미배선 / ADR-107 Active 선언 wire 죽음 / ADR-096 Wave 2
      미도달): FM1-false-positive = surgical scope + inline allowlist(사유·만료
      필수) + SELF_EXCLUDE(스캐너 자기 코드/fixture/생성 역색인 제외) / FM2 =
      Phase 1(ADR) + Phase 2(script/workflow/registry/self-test) 동시 착지 +
      ADR-151 inventory enroll / FM3(최중요) = cross-repo subject durability —
      D3 subject = live consumer 자원선언(durable), 모노레포 consolidatable mirror
      아님 (ADR-011/107 死因 직접 반박).

      census fail-closed(candidates==0 ∧ inert==0 → born-hollow exit 3,
      check_path_relocation_consistency.py:752 동형): scan corpus 에 examples/** +
      presets/** 포함 필수(inert>0 성립 — inert 는 construct 가 자원명 텍스트 지목
      시에만 증가, :576 verified). anti-hollow self-test dual: .sh(ADR-151 enroll)
      + .py(ac-traceability Hop3 AST).

      Phase 2 = scripts/lib/check_infra_resource_drift.py (Python SSOT, ADR-061
      §결정 1 offline/read-only/argparse/pathlib, ReDoS-safe line-by-line) +
      scripts/check-infra-resource-drift.sh (thin wrapper) +
      .github+templates/github-workflows/infra-resource-manifest-drift.yml
      (byte-identical pair ADR-005, always-run job + repo-guard if: — on.paths
      필터 day-1 금지=vacuous-pass 규범⑤) + docs/infra-resource-baseline.yaml
      (Amendment 20 grandfather baseline 재사용) + discriminating self-test dual +
      docs/selftest-execution-liveness-inventory.yaml 레코드 + registry 2 row +
      hotfix-bypass:{infra-resource-undeclared-surface,infra-resource-orphan-reconcile}
      label. cross-repo 축(CODEFORGE_CROSS_REPO_PAT fetch + <ns>/<id> 네임스페이스
      + failure-mode 분리 + ref-pin) = ADR-157 §결정 4 SSOT.

      prior art 답습: check_path_relocation_consistency.py(원장 yaml + 로컬 코퍼스
      census + active_when self-report selector, 최근접 구조 선례 CFP-2661) +
      check_deferral_carrier_declared.py(baseline loader/digest, Amd20). 신규
      발명 0 아님(정직) — fail class 의 no-optout 자세는 5-piece 가 안 주므로
      "구조 5/5 답습 + 비대칭 1건 신규(§32.D surfacing 채택)".

      ratchet 위반 0건 — framework 자연스러운 사용 사례 entry 추가 only. 기존
      §결정 5/6/32.D 본문 의미 변경 0건. plugin.json bump(6.94.0 tentative,
      origin fetch 후 확정) + marketplace sync = Phase 2 PR scope (ADR-063).
  - amendment: 24
    carrier_story: CFP-2719
    date: 2026-07-17
    direction: clarify
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework (§결정 11 permanent SSOT host) → ADR-058 §결정 5 trigger 미해당. 본 Amendment 24 = fact-correction(clarify) — 결정 내용 무변경(tier·승격 gate·surfacing 경계·registry 절차 전부 불변), Amendment 23 carrier prose 의 정정된 facts 만 SSOT-정합. 약화 0건 (인용처/구현 유무/증거 의무 = 사실 축 정정이며 invariant 강도 무변경) → ADR-058 §결정 5 약화 방향 발의 차단 logic 비대상. 선례 = ADR-037 Amendment 3 (fact-correction, "결정 내용 무변경 ... carrier prose 의 정정된 facts 만 SSOT-정합").
    summary: |
      Amendment 23 (CFP-2700 D3, 2 warning-tier entry 등록) carrier prose 의
      **사실 3건 정정** — fact-correction(clarify), 결정 내용 무변경.
      G2 실배선(CFP-2719) 설계 lane 이 Amd23 prose 를 firsthand 재검증하는
      과정에서 검출. 세 진술 모두 Amd23 `infra-resource-undeclared-surface`
      entry `progress_note` 에 verbatim 실재 (phantom fact-correction 0 —
      Amd23 에 없는 주장을 정정하지 않는다). 정정 없이 배선하면 hollow
      claim 이 코드로 상속된다 (실증 — 아래 (2)).

      (1) **prior art 오인용**: Amd23 이 baseline digest 선례로 인용한
      `check_deferral_carrier_declared.py(baseline loader/digest, Amd20)` 는
      digest 구현이 **0** 이다 (해당 파일 :47 은 타 파일을 지목하는 주석일 뿐).
      정정 → 실 Amd20 준수 구현 = **`check_deferred_followup_reconcile.py`**
      (compute_content_digest :356 / sha256 :362,:381 / stored↔recomputed
      불일치 :395-399 / grandfathered_ok NOT-worse 술어 :404) +
      **`gen_deferred_followup_baseline.py`** (single-writer gen, cmd_prune
      :187 = monotonic shrink only). 참고: Amendment 20 본문(:60)은 이미
      `check_deferred_followup_reconcile.py(baseline loader/digest)` 로 정확히
      인용 → 오인용은 Amd23 국소 결함이며 framework 기제 자체는 무결.

      (2) **"Amd20 grandfather baseline 재사용" = hollow**: 재사용할 구현이
      존재하지 않는다. Amd23 이 나란히 인용한
      `check_path_relocation_consistency.py` 는 hashlib|sha256|digest|
      monotonic|shrink hit **0** = Amd20 **비준수 인스턴스**(모범 아님).
      정정 → D3 baseline = **implemented-new Amd20-compliant**
      (**코드 상속-재사용 아님** — 단 Epic AC-16 "기존 기제 재사용"은 무손상:
      "재사용" = 기제/패턴 축[Amd20 5요소 형판 + check_deferred_followup_
      reconcile.py prior-art]에서 참 ⊥ 본 정정 = 코드 상속 축[path-relocation
      digest 0 → 상속할 구현 없음], 두 축 disjoint). Amd20 이 framework-wide
      로 규정한 5요소(enumerated-freeze / 2-owner section / single-writer gen
      tool / content_digest tamper-evident / monotonic shrink) **형판이 기준**
      이며, as-built 처분(digest+shrink 실배선 / gen tool·2-owner 미채택·이연)
      = change-plan §9.2 SSOT.
      ★ 실증: 선행 구현 초기 커밋(cfp-2700-g2 `7715657e`)의 scanner 는
      sha256|hashlib|content_digest **0** 이면서 주석은 "monotonic shrink" 를
      주장하고, write_baseline() 은 전량 재작성이라 재생성이 baseline 을
      조용히 **키울 수** 있었다(ratchet 무력화). = hollow claim 이 코드로
      상속된 실증. 이후 merge-전 FIX 가 digest(set-결박, 손상 = exit 3
      substrate-failure) + shrink-only(`--allow-baseline-growth --reason`
      명시 escape) 실배선으로 정정해 main 착지(PR #2720 `8e60a53d`).
      본 정정이 문서 위생이 아니라 **결함 예방**인 근거.

      (3) **"ReDoS-safe" claim 의 증거 의무**: Amd23 prose 의 "(Python SSOT …
      ReDoS-safe line-by-line)" 는 ADR-082 Amendment 38 §결정 16(21번째
      warning-tier entry `resource-safety-claim-proof-presence`) 의 대상
      closed-set 에 속하는 **resource-safety claim** 이다 → **paired
      proof-reference 또는 honest-ceiling 동반 의무**(file-scoped presence).
      정정 → D3 는 claim 유지 시 DoS-bound 회귀 fixture(wall-clock 실측)를
      proof-ref 로 동반하고 honest-ceiling 을 함께 싣거나, claim 자체를
      제거한다. 자기 게이트에 born-red 로 태어나지 않기 위한 의무.

      **범위·비대상**: 신규 §결정 0 / 신규 entry 0 / tier·bypass·승격 gate
      무변경 / Amendment 23 의 2 mechanical action(infra-resource-
      undeclared-surface + infra-resource-orphan-reconcile) 존치.
      required contexts 7-tuple 무변경 (surfacing ≠ membership,
      §결정 32.D — ADR-145 §결정 3 override 비적용). ADR-157 §결정 6(D4
      비커밋 ephemeral) 정합 유지. doc-only — plugin.json bump 0
      (`archive/**` = ADR-037 결정 A2-3 비귀속 + A2-6 no-surface-touch 면제,
      게이트 실측 check-plugin-version-bump-self.sh:145 `archive/*` → exempt)
      → marketplace sync 불요 (ADR-063 §결정 1 mirrored field 변경 0).
  - amendment: 25
    carrier_story: CFP-2650
    date: 2026-07-19
    direction: clarify
    sunset_justification: null  # ADR-060 = is_transitional:false 영구 framework → ADR-058 §결정 5 trigger 미해당. Amendment 25 = clarify/promotion-provenance — tier flip 은 additive ratchet↑(warning → blocking-on-pr surfacing), invariant 강도 상향이며 약화 0건. required contexts 7-tuple 무변경 (surfacing ≠ membership, ADR-145 §결정3 override 비적용). 선례 = Amendment 20 (CFP-2594 flip provenance) + Amendment 24 (clarify).
    summary: |
      resource-safety-claim-proof-presence 게이트 warning → blocking-on-pr 승격
      provenance (CFP-2650, CFP-2646 Wave 2 named carrier). CFP-2594 flip model
      동형 — surfacing ≠ required-context 편입. 신규 §결정 0 · 신규 entry 0 ·
      tier flip 만 (게이트 semantic 무변경, ADR-082 §결정16 owner Amendment 불요).
      (1) 승격 provenance: promoted_by CFP-2650 / evidence-gate 3/3 MET
      (pr_cumulative 56≥20 / failure_threshold 0 / sibling CFP-2646 #2651 MERGED).
      (2) CFP-2594 "surfacing ≠ required-context 편입" model 을 본 게이트에 재확인 —
      workflow header 승격노트의 stale 2-정의(surfacing = required 편입) 봉합.
      (3) branch-protection 7-tuple 무변경 (required contexts 신설 0, ADR-125 선호).
      honesty-ceiling(ADR-151 §결정7) 불변 — blocking 게이트도 presence 만 검사,
      truth 미강제. scope = 양 workflow continue-on-error 제거(byte-identical pair) +
      registry current_tier flip + lint docstring granularity-carrier pointer 정정 +
      정책문서 file-scoped over-claim sweep(ADR-045/ADR-061 3-line) + plugin.json MINOR.
related_stories:
  - CFP-389
  - CFP-390  # Amendment 1 carrier — 인벤토리 backfill (CFP-388 Epic Story-2)
  - CFP-388  # parent Epic
  - CFP-449  # Amendment 3 carrier — 2nd warning-tier entry `decision-principle-vocab` + bypass channel 의미 sharpening
  - CFP-481  # Amendment 4 carrier — 3rd warning-tier entry `auto-phase-label` + ADR-024 Amendment 4 동반 + label-registry-v2 v2.3 MINOR 동반
  - CFP-506  # Amendment 5 carrier — 4th warning-tier entry `claude-md-line-cap` + ADR-012 Amendment 1 + ADR-051 Amendment 1 + label-registry-v2 v2.4 same-MINOR sub-entry 동반
  - CFP-509  # Amendment 6 carrier — evidence-check-registry schema v1.1 → v1.2 MINOR bump + §결정 19 신설 (recurrence-based advisory promotion signal)
  - CFP-508  # Amendment 7 carrier — evidence-registry-naming convention lint + §결정 20 신설 (entry name ↔ workflow file naming convention + Conservative no-rename policy + multi-job pattern 정식 인정)
  - CFP-530  # Amendment 8 carrier — N번째 warning-tier entry `workflow-permissions-block-presence` 등록 + 16 file remediation surface T1/T3 tier 매핑 + hotfix-bypass:workflow-permissions 10번째 family member + ADR-063 atomic invariant 발효
  - CFP-583  # Amendment 9 carrier — 7th warning-tier entry `workflow-yaml-parse` 등록 + 6 workflow yml BODY heredoc anti-pattern 정정 + framework zero-coverage sentinel 회복 (ADR-064 §결정 2 forbid-list mechanical lint + ADR-058 sunset criteria mandate + ADR-040 worktree-first 4 entry + ADR-024 Amendment 4 auto-phase-label + ADR-068 wording SSOT 등 framework SSOT 운영 정당성 회복) + §결정 23 BODY heredoc 정상 패턴 SSOT
  - CFP-662  # Amendment 10 carrier — 10번째 warning-tier entry `bootstrap-labels-precondition` 등록 + RETRO-MCT-104 carrier (mctrader-data MCT-104 Phase 2 PR #14 2026-05-09 replay sentinel) + PR-time precondition check pattern 의 첫 baseline + label-registry-v2 v2.13 → v2.14 PATCH (`hotfix-bypass:bootstrap-labels` 20번째 family member) + ADR-061 §결정 1 외부 script convention pattern reuse (CFP-583 BODY heredoc anti-pattern 차단) + ADR-066 CODEFORGE_CROSS_REPO_PAT primary token 정합 + consumer-guide §2h.X 자동 install 절차 명시 (Edge Case #1 CRITICAL 해소)
  - CFP-734  # Amendment 12 carrier — 신설 §결정 26 KPI history accumulation 메커니즘 선택 결정 규칙 SSOT + 3-KPI 분류표 + 통일 "history" key 명 grandfather 정책 + follow-up CFP 경계 (ADR-064 §결정 5). lane 분류 = doc-only fast-path (ADR-054 §결정 1). G-1 지식 공백 (패턴 rationale 부재) retroactive 해소
  - CFP-722  # Amendment 13 carrier — 신설 §결정 27 11번째 warning-tier entry story-section-ownership + lane-self-write-boundary mechanical-enforcement layer (CFP-688 Phase 2 PR #441 destructive rewrite incident 차단 forcing function, ADR-031 §14 monopoly + CFP-32 fix-event-v1 §10 monopoly cross-ref only — ownership semantic 재정의 0건). full-lane (script + workflow + bats + dual-deployment per-repo self-app).
  - CFP-963  # Amendment 14 carrier — 신설 §결정 28 12번째 warning-tier entry codex-network-scope-presence + ADR-081 Amendment 4 §결정 D1.D 본문 확장 (boolean → 4-tier enum strict ratchet-up) mechanical enforcement layer. ADR-040 Amendment 3 §결정 7.A self-application (ADR-081 mechanical_enforcement_actions[]=[] → list[object] 전환). full-lane (Phase 1 = 3 ADR Amd + 2 contract MINOR + SSOT doc + Story + Change Plan, Phase 2 = scripts/lib/2 workflow/bats/fixture pair CX-963-3 P2 boundary mandate). CFP-509 v1.1→v1.2 sibling MANIFEST sync miss INV-1 parity 영역의 evidence-check-registry-v1 MANIFEST row stale "1.1" → "1.3" atomic catch-up (CFP-963 silent stale 영역 catch-up + 신규 v1.3 MINOR network_scope_actual optional schema field codify, 단일 PR row write).
  - CFP-2061-S4  # Amendment 17 carrier — 신설 §결정 31 15번째 warning-tier entry governance-drift-detection + 거버넌스 지표 7종 주기 측정 + drift 이슈 자동 발행 (advisory, cron). full-lane (Python SSOT + bash wrapper + cron workflow + baseline JSON + bats 19 TC). prior art 답습: check-marketplace-drift.sh + bypass-label-counter.py (신규 발명 0). de-bloat 재증식 감시 경보 채널.
  - CFP-2381  # Amendment 18 carrier — 신설 §결정 32 16번째 warning-tier entry deferred-followup-reconcile + §결정 19 auto_blocking 강제력 0 라벨 → mechanical forcing function 연결 (carrier-부재 검출 = detect_command/workflow 경로 파일 실존, deterministic + 외부의존 0 + backfill 0). STALE 2건 (bootstrap-labels-precondition + schema-change-7-principles-self-check) status flip + stale TBD 주석 제거. full-lane (Python SSOT + bash wrapper + warning workflow + self-validation test job + registry self-entry). prior art 답습: check_governance_drift.py + increment-justification + operational-outcome-signal-lint test-job (신규 발명 최소).
  - CFP-2426  # Amendment 19 carrier — 신설 §결정 33 17번째 warning-tier entry lane-count-ssot-consistency + canonical 작업레인 수(10, ADR-125 Amd1) SSOT mechanical consistency enforcement. grep-기반 검출(N 레인/N번째 lane/레인 N개, N≠10) + 5축 allowlist(within-line 이중토큰/negation/history/path/counterfactual) channel-split false-positive 차단. 2 Story 연속(CFP-2341→CFP-2376) leak = manual 정정 구조적 한계 입증(pattern_count=2 정당). full-lane (Python SSOT + thin wrapper + .github single-root warning workflow + self-contained discriminating test 22 fixture/4 mutation 생존 0 + registry self-entry + plugin.json tagline 8→10 STALE 정정 + 6.40.0 MINOR marketplace sync). standalone ADR-132 기각(ADR-060 framework 자연스러운 17번째 entry). prior art 답습: check_issue_body_claim_pre_screen.py(in_fence toggle) + check_governance_drift.py(path walk + ::warning::) + check-deferred-followup-reconcile.sh(thin wrapper).
  - CFP-2597  # Amendment 21 carrier — 19번째 warning-tier entry peer-completion-falsifiability 등록 (ADR-044 Amendment 6 §결정 12 verification-floor 축③ carrier). 신규 §결정 0 — §결정 5 등록 절차 + §결정 6 promotion gate 상속. owner_adr ADR-044 / carrier_adr ADR-060. evidence-checks-registry entry mirror + review-verdict-v4 v4.16 (peer_verdicts[] additive). ★ check-lane-evidence.sh 축③(fan-out) 와 별개 (이름만 동일). 실 script+workflow+test = sibling worker Phase 2 deliverable.
  - CFP-2591  # Amendment 20 carrier — §결정 32.D 개정(surfacing tier 도입) + grandfather baseline 메커니즘 framework-wide 신설 + 18번째 warning-tier entry deferral-carrier-declared(carrier-mandate no-TBD lint). deferred-followup forcing-function 봉합 Stage 1+2(baseline + new-only shadow) — NO-FLIP: continue-on-error 유지 + self-entry current_tier:warning 불변, 실 flip=별 후속 PR(baseline main 착지 후). §결정3 reconciliation(surfacing qualifier — blocking-on-pr 자체가 contexts membership 미함의) + §결정6 harmonization(baseline-relative new-debt failure=0). self-entry deferred-followup-reconcile §결정6 carrier trio(outage runbook/author-verify/sticky at-most-once) evidence_artifacts 배선. ADR-127/ADR-024 amendment 불요(Tier 1 surfacing 6-tuple 회피). full-lane (baseline yaml + check new-only subtract + (b) Python SSOT/thin wrapper/.github workflow + runbook + registry (b) entry + self-entry evidence_artifacts + plugin.json 6.72.0 MINOR + registry-v1 v1.6). honest ceiling: hard block 미주장(admin 우회 구조적 가능, AC-20 count 관측만). prior art 답습: check_lane_count_ssot.py(5축 allowlist) + check_deferred_followup_reconcile.py(baseline loader/digest).
  - CFP-2700  # Amendment 23 carrier — 21+22번째 warning-tier entry infra-resource-undeclared-surface + infra-resource-orphan-reconcile (D3 인프라 자원 manifest drift 게이트). owner_adr ADR-157 / carrier_adr ADR-060. 2 entry 분리(§결정3 current_tier per-entry, 미선언축 surfacing-bound / orphan축 warning→§결정6 승격 비대칭). Amd20 grandfather baseline + §32.D surfacing(NO-FLIP) 상속, 신규 mechanism 0(AC-16). 死因 3-mode 봉인(FM1/FM2/FM3). 실 script+workflow+dual self-test = Phase 2 deliverable.
related_adrs:
  - ADR-008   # versioning (kind:registry 도 minor/major SemVer 정합)
  - ADR-010   # contract sibling sync (kind:registry scope 외 명시)
  - ADR-013   # dogfood-out (Story file path internal-docs)
  - ADR-016   # marketplace registration
  - ADR-024   # branch policy (Amendment 3 의 audit-trailed exception channel 도입)
  - ADR-037   # plugin version bump (MINOR)
  - ADR-041   # doc-locations
  - ADR-050   # parallel epic + warning mode prior art
  - ADR-053   # structural change restart
  - ADR-054   # doc-only fast-path (본 Story 는 full-lane)
  - ADR-057   # 첫 amendment 후보 (별도 carrier)
  - ADR-058   # 직접 동인 — sunset criteria mandate
  - ADR-044   # Amendment 21 — 축③ (peer-completion falsifiability) 결정 SSOT (owner_adr), ADR-060 = warning-tier check 등록 framework host (carrier_adr)
related_files:
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - docs/evidence-checks-registry.yaml
  - docs/doc-locations.yaml
  - docs/parallel-work/section-ownership.yaml
  - scripts/check-adr-sunset-criteria.sh
  - scripts/check-bypass-audit-comment.sh
  - templates/github-workflows/adr-sunset-criteria.yml
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - CLAUDE.md
---

# ADR-060: Evidence-enforceable promotion framework — declaration → warning → enforce 점진 적용 SSOT

## 상태

Accepted (2026-05-11). carrier_story = CFP-389. parent Epic = CFP-388.

## 컨텍스트

ADR-058 (CFP-387, merged 2026-05-11 — internal-docs main `a59fc8a`) 가 ADR `## 해소 기준` 섹션과 `is_transitional` frontmatter 를 의무화했으나 **declaration only** 단계에 머물렀다. §결정 8 명시:

> 본 ADR 은 정책 declaration only. 기계적 강제 (CI lint) 는 CFP-B (잠정) / 정책 첫 적용 사례 (ADR-057 amendment + KPI) 는 CFP-C (잠정) / 기존 안전망 ADR retroactive backfill 은 CFP-D (잠정) 별도 carrier 분리.

본 ADR (ADR-060) 가 **CFP-B 잠정의 carrier** — declaration 의 첫 evidence-enforceable mechanical check 도입 + 모든 후속 evidence check 가 따를 **점진 적용 framework SSOT**.

### 직접 동인

1. **ADR-058 declaration 의 moral governance 한계**: 정책 선언 → 작성자 자발 준수 + DesignReview 1차 안전망 의존. CI mechanical enforcement 부재 시 ADR-057 같은 직접 동인 ADR 의 측정 기준 부재 위험이 재발.

2. **codeforge wrapper repo 의 governance 진화 패턴**: ADR-050 (parallel-epic-conflict-check.yml = warning mode prior art) / ADR-024 Amendment 2 (CFP-280 — branch protection drift detection) / ADR-041 (doc-locations.yaml SSOT) 가 모두 "선언 → 점진 enforce" 패턴 채택. 본 framework 가 패턴을 정형화.

3. **사용자 brainstorming 합의** (Opus×Codex 3-round, 2026-05-11): "안전망 측정가능 종료" 원칙 5 + "evidence-enforceable 점진 적용" 원칙 + "velocity-normalized metric" (throughput 가변 환경에서 sprint-주기 metric 회피).

4. **CFP-388 Epic 3 child Story 의 framework 정합 요구**: CFP-389 (본 framework SSOT) → CFP-390 (인벤토리 backfill = registry yaml row append) → CFP-391 (4-tier 정식 분류 amendment) 의 순차 의존. 3 Story 모두 본 framework registry 위에서 동작.

5. **Hotfix bypass channel 의 필요성**: enforce mode 진입 후 운영 장애 hotfix 가 정책 위반을 강제하는 경우, ADR-024 §결정 6 ("emergency hotfix 도 PR 경유 의무, no exception") + `enforce_admins: true` (CFP-70) 와 호환되는 **audit-trailed exception channel** 부재. 사용자 ESCALATE 결정 (CFP-389 iteration 2) = Option A — `hotfix-bypass:*` label family 도입 + ADR-024 Amendment 3 동반.

### 선행 연구 / prior art

- **Feature flag sunset (LaunchDarkly / Optimizely 운영 가이드)**: 도입 시 sunset criteria + owner + date 의무화. 측정성 3-tuple 패턴 차용.
- **입법 sunset clause 패턴**: 명시적 종료 조건 미충족 시 자동 expire. warning → enforce mode 전환 (=evidence check 의 sunset transition) 으로 변형.
- **CI/CD progressive enforcement (Spotify / Shopify code health migration 가이드)**: 신규 lint 도입 시 advisory → blocking on changed lines → blocking on full repo 3 단계 점진. 본 framework 의 4-tier 분류 (warning / blocking-on-PR / blocking-on-merge / hotfix-bypass) 의 직접 모델.
- **codeforge 내부 prior art**: ADR-050 parallel-epic-conflict-check.yml (non-blocking warning + PR comment + label) / ADR-024 Amendment 2 branch-protection-drift-check.yml (drift detection schedule + workflow_dispatch) 모두 본 framework workflow 양식의 1차 reference.

## 결정

### 결정 1 — Framework SSOT 위치 = `docs/inter-plugin-contracts/evidence-check-registry-v1.md`

evidence-enforceable framework 의 schema doc + 운영 룰 = **kind:registry** entry. 위치 = `docs/inter-plugin-contracts/evidence-check-registry-v1.md`. 분류 근거:

- ADR-058 §결정 8 의 framework declaration 을 mechanical 검증 가능한 **cross-cutting protocol** 로 변환 → kind:contract (lane plugin 간 typed schema) 아닌 kind:registry (wrapper-owned cross-cutting protocol) 정합.
- 기존 3 kind:registry (`comment-prefix-registry-v1` / `fix-event-v1` / `label-registry-v2`) 와 동일 위치 + 동일 lint chain (`check-doc-frontmatter.sh` + `check-doc-section-schema.sh`).
- `inter-plugin-contracts/MANIFEST.yaml` 의 `registries:` 블록에 entry 추가 (label_registry 패턴) — kind:contract `check-inter-plugin-contracts.sh` scope 외 (MANIFEST header `kind:contract files only` 명시 정합).

(§5.5 CL-1 — 권고 채택)

### 결정 2 — Registry data = `docs/evidence-checks-registry.yaml` (single SSOT)

본 framework 의 모든 evidence check entry 는 단일 yaml file `docs/evidence-checks-registry.yaml` 에 정의. schema 는 `evidence-check-registry-v1.md` SSOT. MANIFEST.yaml `registries:` 블록은 **versioning 추적 only** (label-registry-v1 → v2 패턴 reference, version bump 시 row append). data 자체는 yaml.

(§5.5 CL-1 추가 명시 — MANIFEST = versioning, yaml = data)

### 결정 3 — 4-tier enforcement enum (정식 도입)

evidence-checks-registry.yaml 의 각 entry 는 `current_tier` 필드 보유. enum:

| tier | 동작 | branch protection 영향 |
|---|---|---|
| `warning` | continue-on-error 또는 non-required check. PR comment / job summary 경고만. | required_status_checks.contexts 미부착 |
| `blocking-on-pr` | required check. PR merge 차단. | required_status_checks.contexts 부착 |
| `blocking-on-merge` | post-merge guard (예: phase-gate-mergeable). PR open 단계는 통과, merge 시점 차단. | required_status_checks.contexts 부착 |
| `hotfix-bypass` | bypass label 적용 PR 만 skip + audit comment 의무. label 부재 시 blocking-on-pr 등가. | required_status_checks.contexts 부착 (+ bypass workflow) |

본 ADR (CFP-389) 의 첫 entry = `warning` tier. 후속 Story (CFP-391) 가 본 enum 을 정식 명시 + 기존 entry retroactive 분류. 본 ADR 시점에서는 enum 정의만 제공, registry yaml 의 `current_tier` 필드는 optional (CFP-391 시점 required 전환 = MINOR bump).

### 결정 4 — 첫 entry = ADR sunset criteria lint (`scripts/check-adr-sunset-criteria.sh`)

evidence-checks-registry.yaml 의 첫 entry:

```yaml
- name: adr-sunset-criteria
  description: ADR-058 §결정 1-3 mechanical verification (is_transitional frontmatter + ## 해소 기준 섹션 + 측정성 3-tuple + 모달 어휘 1차 사전)
  detect_command: bash scripts/check-adr-sunset-criteria.sh
  workflow: templates/github-workflows/adr-sunset-criteria.yml
  current_tier: warning
  bypass_label: hotfix-bypass:adr-sunset
  bypass_audit_lint: bash scripts/check-bypass-audit-comment.sh
  promotion_criteria:
    pr_cumulative_min: 20
    failure_threshold: 0
    sibling_dependencies:
      - CFP-390
      - CFP-391
    evidence_artifacts:
      - github_actions_run_history_url
      - lint_failure_count_zero_proof
      - pr_cumulative_count_proof
  modal_anti_pattern_dictionary:
    version: "1.0"
    dictionary:
      - "안정화되면"
      - "임시"
      - "한시적"
      - "until further notice"
  introduced_by: CFP-389
  owner_adr: ADR-058
  carrier_adr: ADR-060
```

lint script 책임 4건 (Story §5.1 AC-4 정합):
- (a) ADR file 의 `is_transitional: true|false` frontmatter 필드 존재 검증
- (b) `## 해소 기준` 섹션 존재 검증
- (c) is_transitional=false 시 "N/A — permanent policy" 1줄 또는 동등 형식 허용
- (d) is_transitional=true 시 측정성 3-tuple (metric / who / how) 존재 검증 + 모달 어휘 1차 사전 4 표현 매치 검사

본 lint exit code = 0 (PASS) / 1 (FAIL — violation 1건 이상). bypass label 적용 PR 의 경우 workflow 가 lint 실행 자체를 skip (continue-on-error 무관, label 기반 conditional skip).

### 결정 5 — 첫 적용 = warning mode (continue-on-error)

`templates/github-workflows/adr-sunset-criteria.yml` 는 다음 양식:

- trigger: `pull_request` (opened / synchronize / reopened) — paths filter `docs/adr/**.md`
- 실행: `bash scripts/check-adr-sunset-criteria.sh <changed-ADR-files>`
- step: `pip install --user pyyaml` (default ubuntu-latest runner = python3 + pip 사전 설치, pyyaml 별도 install 의무 — lint script python yaml 의존성)
- `continue-on-error: true` 적용 → lint fail 이 PR merge 차단하지 않음
- branch protection `required_status_checks.contexts` 미부착 (ADR-024 Amendment 2 manifest 갱신 불필요)
- PR comment 자동 게시 — violation 발견 시 job summary + sticky comment 형태 (parallel-epic-conflict-check.yml 패턴 차용)
- `hotfix-bypass:adr-sunset` label 적용 PR = lint skip + audit comment 자동 발의 (별도 step)

운영 가이드 (§6.1.2 EC-B 정합):
- 첫 warning 출현 ≤ 14 days 동안 false positive ≥ 5건 발생 시 → workflow 일시 정지 (admin only) + ADR-060 §결정 보완 carrier 발의.
- solo-dev 환경 (CFP-72 reviewer count=0) → 사용자 본인 적극 체크 의무 (PR review 단계 GitHub Actions warning manual 확인).

### 결정 6 — 승격 gate (binary, AND condition)

warning → blocking-on-pr (또는 blocking-on-merge) 승격 조건 = **3 condition AND** (§5.1 AC-6 정합):

- **(a) PR 누적 ≥ 20**: ADR-060 merge 후 첫 main PR merge 일자부터 카운트 시작. `hotfix-bypass:adr-sunset` label 적용 PR 도 throughput metric 에 포함 (EC-C 정합).
- **(b) bypass label 외 failure count = 0**: warning mode 운영 기간 동안 `scripts/check-adr-sunset-criteria.sh` violation 카운트 = 0. bypass label 적용 PR 의 lint 결과 skip (failure 미카운트). 시뮬레이션 실패와 enforce failure 는 동일 의미로 통합 (별도 카운터 없음).
  - **measurement 방식**: failure count = **각 PR 의 final commit (= PR branch 의 최종 commit, merge 전략 squash/rebase/merge-commit 무관) 의 lint 결과** 기준 (PR 전체 commit history 또는 individual workflow run 누적 아님). PR 작성자가 warning manual 확인 → 다음 commit append 로 warning 해소 → PR merge 시점 final state = PASS = failure 미카운트. 정합: 운영 가이드 §결정 5 "사용자 본인 적극 체크 의무". P1-A `continue-on-error: true` × `failure_threshold=0` 잠재 deadlock 해소 — final commit 기준이면 warning mode 의 의도 (PR 진행 차단 X + final 정합 측정) 양립.
    - **final commit 정의 (merge 전략별 정합)**: GitHub PR UI 기준 PR branch 의 최종 commit (≈ `gh pr view --json commits | jq '.commits[-1].oid'` 결과). squash merge = 압축 전 PR head 기준 / rebase merge = PR head 기준 / merge-commit = PR head 기준 (생성된 merge commit 아님). main branch 의 post-merge commit 과 무관.
    - **workflow trigger 시점**: `pull_request` (synchronize / opened / reopened / labeled / unlabeled) — PR approval phase 에서만 실행. merge 후 재실행 X. 별도 post-merge lint 는 본 Story scope 외 (enforce 승격 carrier 또는 별도 carrier).
- **(c) sibling Story merged**: CFP-390 (인벤토리 backfill) + ~~CFP-391 (4-tier 정식 amendment)~~ → **CFP-412 (4-tier amendment 재예약 carrier, Amendment 1, 2026-05-11)** 모두 main merge 완료. 본 framework 가 multi-entry registry 로 운영되는 시점 정합. (see Amendment 1 — CFP-391 Issue #396 closed without delivery 2026-05-11, CFP-412 Issue #412 substitution)

승격 carrier (별도 CFP-NNN, 본 Story scope 외) 의 evidence 4 산출물 의무:
- (i) GitHub Actions 누적 run 결과 page URL (warning workflow 실행 이력)
- (ii) bypass label 외 failure count = 0 lint 출력 (gh CLI / API 결과 첨부)
- (iii) PR 누적 ≥ 20 카운트 (gh CLI / API 결과 첨부)
- (iv) **GitHub Actions outage runbook**: warning mode = `continue-on-error: true` 덕에 outage 시 PR 차단 X. enforce mode 진입 시점 = outage 발생 시 PR block / hotfix-bypass label 활용 / workflow manual disable 등 대응 절차 산출물 의무. 외부 의존 (GitHub Actions 가용성) 의 enforce mode 영향 분석 + manual fallback path 명시. (§7.4.1 DR 분석의 enforce 진입 시 후속 carrier scope.)
- (v) **Audit comment author 검증 lint 증거** (§결정 8 cross-ref): enforce 승격 carrier 가 `audit_comment_author_verification_lint` 의 실행 결과 (gh CLI / API 출력) 첨부 의무. comment author = `github-actions[bot]` 검증 lint 가 bypass label 적용 PR 의 audit comment spoofing 차단 — §7.2 STRIDE-LITE S1 강화 enforce 의무.
- (vi) **Sticky comment pattern 구현 증거** (§결정 8 cross-ref): enforce 승격 carrier 가 audit comment workflow 의 sticky pattern (기존 `[hotfix-bypass-audit]` comment update 또는 marker 기반 dedup) 도입 + 단일 PR 동일 workflow run 다회 시 at-most-once 보장 증거 (workflow yaml diff + test 출력) 첨부 의무.

본 6 산출물 부재 시 승격 carrier PR block. **자동화 카운터 인프라는 후속 carrier 책임** — 본 ADR 는 gate 정의만 제공.

### 결정 7 — Hotfix bypass channel = `hotfix-bypass:*` label family (audit-trailed exception)

운영 장애 hotfix 가 정책 위반을 강제하는 경우의 **audit-trailed exception channel**:

- **label naming**: `hotfix-bypass:<entry-name>` family. 첫 entry = `hotfix-bypass:adr-sunset` (본 Story).
- **권한자**: repo admin only. solo-dev 환경 = 사용자 본인 (mccho8865). contributor 추가 시 재논의.
- **PR 경유 의무 유지**: bypass label = lint skip only. push/merge 경로는 PR 경유 유지 — ADR-024 §결정 6 (`emergency hotfix 도 PR 경유, no exception`) + `restrictions: {users:[], teams:[], apps:[]}` (CFP-66) + `enforce_admins: true` (CFP-70) 와 호환.
- **label scope**: per-entry 한정. 본 entry (`adr-sunset`) bypass label 은 sunset criteria 관련 긴급 hotfix only. 다른 evidence check (CFP-390 인벤토리 추가) 는 자체 bypass label 정의 (registry entry `bypass_label` 필드 per-entry).
- **ADR-024 Amendment 3 동반 의무**: 본 ADR-060 §결정 7 = ADR-024 Amendment 3 (`hotfix-bypass:*` label family 가 ADR-024 §결정 6 의 audit-trailed exception channel 임을 명시) 의 carrier. Phase 1 PR 동반 (scope cohesion).
- **label-registry-v2 entry 추가**: `hotfix-bypass:adr-sunset` label = label-registry-v2 의 신규 entry. taxonomy = `bypass` tier (신규 tier 도입). label-registry MINOR bump (v2.0 → v2.1) — 별도 PR 또는 본 Phase 1 PR 동반 (ArchitectAgent 판단 — 본 Story scope 동반 권고). **본 결정은 label-registry-v2 의 `bypass` tier 신설 결정 carrier 역할 — label-registry sibling sync (ADR-010) 별도 follow-up 가능**.
- **(Amendment 3, CFP-449)** **audit 전용 채널 — 정책 회피 등록 차단 (ADR-064 §결정 5 ratchet 정합)**: `hotfix-bypass:*` label 은 운영 장애 hotfix 의 일회성 exception 통로이며, 정책 위반을 회피하는 영구 등록 채널이 아님. label 부착 PR 마다 audit comment 자동 발의 + quarterly merge audit log 집계 의무 (§결정 8 schema 정합). 사용한 entry 가 enforce 승격 carrier (별도 CFP-NNN) 진입 시 bypass label 적용 PR 누적 회수가 evidence 산출물 (`bypass_pr_count`) 검토 영역. dictionary 회피 의도 등록 시 sunset_justification 의무 (ADR-058 §결정 5 정합) — bypass channel = 운영 안전망, 정책 회피 통로 아님.

(§5.5 CL-4 RESOLVED — 사용자 Option A 채택 verbatim 반영)

### 결정 8 — Audit trail schema (P0-1 정합)

bypass label 적용 PR 마다 GitHub Actions bot 가 PR comment 1개 자동 append. comment body schema (단일 textual form, CI-parsable):

```
[hotfix-bypass-audit] PR=<number> label_applied_by=<user> reason=<bypass_reason_textbox> ADR_files=<comma-separated-paths> timestamp=<ISO8601>
```

- `PR` = PR number (정수)
- `label_applied_by` = label 적용한 GitHub user login (admin only — solo-dev = 사용자 본인)
- `reason` = PR description 내 `### Bypass reason` 섹션 textbox 본문 (workflow 가 추출, 부재 시 PR block 의무 — workflow level 검증)
- `ADR_files` = 본 PR 에서 변경된 `docs/adr/*.md` 경로 list (comma-separated)
- `timestamp` = ISO8601 UTC (Z suffix 의무 — fix-event-v1 schema clarification 정합)

**Re-entry 안전망 (EC-D 정합)**: bypass PR 의 변경 ADR 가 sunset criteria 누락 상태 (재귀 시나리오) 일 시 audit comment 에 `[sunset-criteria-deferred]` 태그 자동 추가 + 후속 보완 의무 자동 Issue 발의 (CFP-390 인벤토리 backfill scope 또는 별도 carrier).

**Audit log 집계**: bypass label 적용 PR list 가 `docs/audit/hotfix-bypass-log.md` (quarterly merge 시 자동 append) — 별도 carrier scope (CFP-390 인벤토리 또는 신규 carrier). 본 ADR 는 schema + bot comment 양식만.

**Audit assertion lint**: `scripts/check-bypass-audit-comment.sh` (본 Story Phase 2 PR 범위 내 신설 — §5.5 CL-A 권고 채택). bypass label 부착 PR 의 audit comment 1개 이상 존재 검증. 부재 시 PR block (workflow level conditional).

**Audit comment author 검증 (enforce 승격 carrier 의무)**: warning mode 단계 = 본 lint 가 comment 존재만 검증 (author = `github-actions[bot]` 검증 미수행 — advisory). enforce mode 승격 carrier (별도 CFP-NNN) 의 `evidence_artifacts` 에 `audit_comment_author_verification_lint` 항목 추가 의무 — author = `github-actions[bot]` 강화 검증 lint 신설. 수동 audit comment 위조 (PR submitter spoofing) 차단을 위한 enforce 진입 전 mandatory 조건.

**Sticky comment pattern (enforce 승격 carrier 의무)**: warning mode 단계 = audit comment automation 가 동일 PR 의 multiple workflow run 시 multiple comment 발의 가능 (at-least-once). enforce mode 승격 carrier 의 의무: sticky comment pattern 도입 (workflow 가 기존 `[hotfix-bypass-audit]` comment 1개 update 또는 marker 기반 dedup) — at-least-once → at-most-once 보장. warning mode 단계는 advisory only 정합 (Change Plan §11.6 / OpRiskArch consult 결과 acceptable).

### 결정 9 — 모달 어휘 1차 사전 = ADR-058 §결정 8 의 4 표현 only

evidence-checks-registry.yaml 의 `modal_anti_pattern_dictionary.version: "1.0"` 의 4 표현 verbatim:

- "안정화되면"
- "임시"
- "한시적"
- "until further notice"

확장 어휘 ("충분히" / "조만간" / "soon" / "TBD" 등) 는 본 Story scope 외. 별도 carrier (CFP-391 4-tier amendment 또는 신규 carrier) 가 `dictionary_version: "1.1"` 으로 MINOR bump 시 확장.

**Amendment chain SSOT 위치 (v1.1 carrier 의무)**: dictionary 확장 carrier (CFP-391 등) 가 어느 ADR 를 amendment 할지 분기:
- **추천 (default)**: **ADR-058 amendment** — ADR-058 §결정 8 이 declaration SSOT 의 owner. 4 표현 dictionary 자체는 ADR-058 원본. ADR-060 는 mechanical carrier (사전 verbatim 재인용 — 본 §결정 9 본문). v1.1 확장 = ADR-058 §결정 8 amendment N.
- **선택 (대안)**: **ADR-060 amendment** — framework SSOT (4-tier / 승격 gate / bypass channel) 자체 변경 동반 시 일체화. 단일 ADR amendment 로 처리.
- **registry yaml = version 추적 only**: `evidence-checks-registry.yaml` 의 `modal_anti_pattern_dictionary.version` field 는 추적 만 — 언어 정의 SSOT 아님. amendment chain 의 단일 진실 = ADR-058 (default) 또는 ADR-060 (대안 — framework 변경 동반 시).

**Substring → word boundary 전환 의무 (v1.1 도입 carrier)**: v1.0 시점 = substring match (예: `임시` 가 `임시저장` 부분 일치 → FAIL = false positive). 의도된 conservative direction (anti-pattern bias). v1.1 확장 어휘 도입 시점 = substring → word boundary regex 전환 의무 (한국어 morpheme-aware tokenizer 또는 `\b modal \b` ASCII fallback). false positive 누적 시 운영 가이드 (§결정 5 EC-B 14d/5건 trigger) 통한 manual disable 가능.

(§5.5 CL-5 ARCHITECT-RESOLVABLE — 4 표현 only 확정. EC-2 P0-3 ADR-058 모순 해소 verbatim.)

### 결정 10 — velocity-normalized metric (throughput 독립)

승격 gate 의 metric = "20+ PR 누적 무사고" — Story 수 / 일자 / sprint 의존 X.

근거:
- codeforge wrapper repo throughput 가변 (solo-dev, dogfood + consumer 작업 혼재).
- sprint-주기 metric (예: "2 sprint 안정 후 enforce") 은 throughput 변동 시 의도와 어긋남.
- PR 누적 = 변경 누적의 직접 신호 — false positive 검증 표본 수 보장.
- bypass label PR 도 throughput 카운트 (EC-C 정합) → bypass 빈도 자체가 throughput 의 일부, 별도 metric 분리 불필요.

### 결정 11 — Framework SSOT 자체는 영구 정책 (sunset 불가)

본 ADR (ADR-060) 자체 분류 = `is_transitional: false` (permanent policy carrier). ADR-058 §결정 6 self-defeat 회피 패턴 정합. 

본 ADR 의 효력 종료 조건 = 본 ADR 의 supersede 또는 codeforge 의 evidence-enforceable governance 자체 폐지. recursive sunset 의 무한 후행 회피.

단 본 framework 의 **개별 evidence check entry** (registry yaml row) 는 individual 하게 sunset 가능:
- warning tier 운영 중 lint script 자체가 deprecate 결정 → registry yaml row `status: deprecated` 또는 row 삭제.
- enforce mode 진입 후 framework 가 영구 운영 상태 진입 (= individual entry 의 mode transition, framework SSOT 자체 sunset 아님).

### 결정 12 — Declaration + first mechanical check 일체화 (CFP-B carrier)

본 ADR 는 ADR-058 §결정 8 의 CFP-B (잠정) carrier 역할:
- declaration (framework SSOT) + first mechanical check (ADR sunset lint) 일체 도입.
- 후속 carrier 분리:
  - **CFP-390 (인벤토리 backfill)** = registry yaml 의 추가 entry 도입 (도메인 추가).
  - **CFP-391 (4-tier 정식 amendment)** = `current_tier` 필드 required 전환 + tier enum 정식 분류 (schema MINOR bump).
  - **CFP-C 잠정 (ADR-057 amendment)** = ADR-057 sunset criteria 본문 backfill + KPI dashboard. 본 framework 위에서 운영 — 첫 적용 사례.
  - **CFP-D 잠정 (retroactive backfill)** = 기존 Active 잠재 안전망 ADR sunset criteria 본문 추가.

## 결과

### 긍정

- ADR-058 declaration 의 moral governance 단계 → mechanical enforcement 점진 진입 — framework SSOT 가 forcing function 제공.
- velocity-normalized metric 로 throughput 가변 환경 (solo-dev) 친화 + sprint-주기 회피.
- 4-tier enum 으로 향후 evidence check 도입 시 mode 표현력 확보 (warning → blocking-on-pr → blocking-on-merge → hotfix-bypass).
- hotfix bypass label 채널이 ADR-024 §결정 6 + `enforce_admins: true` 와 호환 — audit-trailed exception channel 정식 도입.
- audit trail 3중 안전망 (audit comment + audit log + audit lint assertion) 이 bypass 악용 차단 (EC-A 정합).
- kind:registry SSOT 분류로 wrapper-owned cross-cutting protocol 패턴 정합 — 기존 3 entry (`comment-prefix-registry-v1` / `fix-event-v1` / `label-registry-v2`) 와 일관성.

### 부정

- registry yaml 의 첫 entry 만 보유 (sunset criteria lint) — multi-entry 운영 시 schema 유효성은 CFP-390 / CFP-391 이후 확정.
- velocity-normalized metric "20+ PR 누적 무사고" 의 측정 자동화 인프라 미도입 — 승격 carrier 가 evidence 3 산출물 manual 제출 의무 (자동화는 별도 carrier).
- warning mode false positive 폭증 시 운영 가이드 (EC-B) 가 manual disable 의존 — admin 적극 개입 필요.
- solo-dev 환경 (CFP-72 reviewer count=0) 에서 warning mode 시각적 표시만 의존 (EC-F) — 사용자 본인 적극 체크 의무.
- audit log quarterly merge 자동화 부재 (별도 carrier) — 본 Story 는 schema + bot comment 양식만.
- ADR-024 Amendment 3 동반으로 governance ADR 변경 surface 확대 (label-registry MINOR bump 동반 시).

### Trade-off

- **declaration vs enforcement 단계 분리 (ADR-058 §결정 8 패턴)**: 한 Story 에서 declaration + enforcement + retroactive backfill 일체 도입 시 risk 분산 부족 + review burden 폭증. 본 ADR 는 declaration + first mechanical check 일체화, 후속 (CFP-390 / CFP-391) 가 incremental 확장 — 단계 분리의 cost (multi-Story 의존) vs visibility (각 Story 의 결정 surface 명확화) trade-off 에서 visibility 우선.
- **warning vs blocking 첫 도입 mode**: blocking 즉시 도입 시 mechanical enforcement 효과 즉시 발현 / false positive 영향 즉시 발현. warning 시작 + 승격 gate (= ADR-050 prior art 패턴) 채택 — 효과 지연 vs false positive risk mitigation 의 trade-off 에서 위험 회피 우선.
- **bypass label per-entry vs global**: 단일 global bypass label (e.g., `evidence-bypass:*`) 도입 시 사용 단순 / 악용 위험 확대. per-entry (`hotfix-bypass:adr-sunset` 등) → namespace 분리 + 권한 분리 가능 — 사용 복잡도 vs scope 통제 trade-off 에서 통제 우선.

## 대안

### 대안 B (거부) — bypass label 미도입

bypass 채널 부재 → 운영 장애 hotfix 시 ADR-024 `enforce_admins: true` + required check 통과 의무 = deadlock. 직접 push 금지 + bypass 부재 = hotfix 불가능. **거부 사유**: 실운영 시 deadlock 위험 + ADR-024 §결정 6 (emergency hotfix 도 PR 경유 의무) 가 hotfix 채널 자체 부정 아님 — bypass channel 정식 도입 = §결정 6 정합 + audit-trailed 보장.

### 대안 C (거부) — warning mode 영구 (enforce 미승격)

declaration → warning 까지만 도입, enforce mode 영구 미도입. **거부 사유**: warning mode = continue-on-error → mechanical enforcement 실효성 부재. ADR-058 declaration 의 moral governance 단계와 본질적으로 동일 — 점진 적용 의도 미충족. 승격 gate 정의 + 자동 승격 carrier path 가 framework 의 핵심.

### 대안 D (거부) — sprint-주기 metric (예: "2 sprint 안정")

sprint 주기 기반 promotion gate. **거부 사유**: codeforge wrapper repo throughput 가변 (solo-dev). sprint 정의 자체 모호 (별도 governance 부재). PR 누적 = 변경 누적의 직접 신호 + throughput 독립 — velocity-normalized 우위.

### 대안 E (거부) — 단일 global bypass label

`evidence-bypass:*` 단일 label 모든 evidence check skip 가능. **거부 사유**: scope 통제 부재 → 한 entry hotfix 가 모든 entry bypass 우회 위험. per-entry namespace 분리 + 권한 분리 (registry entry `bypass_label` 필드) 우위.

## 다이어그램

```mermaid
graph TD
    A[ADR-058 declaration] -->|CFP-B carrier| B[ADR-060 framework SSOT]
    B --> C[evidence-check-registry-v1.md schema]
    B --> D[evidence-checks-registry.yaml data]
    D --> E[entry 1: adr-sunset-criteria<br/>tier=warning]
    E --> F[scripts/check-adr-sunset-criteria.sh]
    E --> G[adr-sunset-criteria.yml workflow<br/>continue-on-error: true]
    E --> H[hotfix-bypass:adr-sunset label]
    H --> I[scripts/check-bypass-audit-comment.sh]
    H --> J[ADR-024 Amendment 3]
    
    K[승격 gate AND] -->|PR 누적 ≥ 20| L[promote]
    K -->|failure = 0| L
    K -->|"CFP-390 + CFP-412 + CFP-455 merged<br/>(Amendment 2: CFP-412 폐기 → CFP-455 carrier)"| L
    L --> M[blocking-on-pr / blocking-on-merge]
    M --> N[required_status_checks.contexts 부착]
    N --> O[ADR-024 Amendment 2 manifest 갱신]
```

## 해소 기준

N/A — permanent policy. 본 ADR 은 `is_transitional: false` (permanent policy carrier — framework SSOT). §결정 11 self-defeat 회피.

단 본 framework 의 **개별 evidence check entry** 는 individual sunset 가능 — entry level 의 mode transition (warning → enforce) 은 framework 운영의 정상 동작이며 framework SSOT 자체 sunset 이 아님.

## 관련 파일

- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — framework SSOT (kind:registry schema doc, 결정 1)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — `registries:` 블록 entry 추가 (결정 1)
- `docs/evidence-checks-registry.yaml` — registry data, 첫 entry = adr-sunset-criteria (결정 2 + 결정 4)
- `docs/doc-locations.yaml` — 신규 doc type `evidence_check_registry` row 추가 (ADR-041 §결정 정합, §5.5 CL-2)
- `docs/parallel-work/section-ownership.yaml` — 신규 entry: `evidence-checks-registry.yaml` parallel_edit=append-only (ADR-050 정합)
- `scripts/check-adr-sunset-criteria.sh` — lint 첫 구체 (결정 4)
- `scripts/check-bypass-audit-comment.sh` — audit assertion lint (결정 8)
- `templates/github-workflows/adr-sunset-criteria.yml` — warning mode workflow (결정 5)
- `docs/adr/ADR-024-story-scoped-branch-policy.md` — Amendment 3 동반 (결정 7)
- `CLAUDE.md` — 3 섹션 갱신 (ADR / GitHub Workflow / Inter-plugin Contract)
- `docs/adr/ADR-RESERVATION.md` — ADR-060 row reserved (CFP-389, 2026-05-11)
- 후속 carrier:
  - CFP-390 (인벤토리 backfill — registry yaml row append, ADR-060 **Amendment 1 carrier — 이미 발효**)
  - **CFP-391 (Issue #396, 2026-05-11 closed without delivery — 폐기 처리)** → **CFP-412 (Issue #412, 재예약 carrier)** 가 4-tier 정식 amendment 책임 (ADR-060 Amendment 2 + schema v1.0 → v1.1 MINOR bump)
  - **CFP-TBD (메타 anomaly lint carrier — Amendment 1 §결정 14 명시 의무, Codex P2-B 정합)**: 인벤토리 누락 시 anomaly 감지 메타 lint (`scripts/check-evidence-registry.sh` 또는 동등) 발의. CFP-390 Phase 1 PR merge 후 별도 CFP/Issue 발의.
  - CFP-C 잠정 (ADR-057 amendment + KPI dashboard — 첫 적용 사례)
  - CFP-D 잠정 (retroactive backfill — 기존 안전망 ADR sunset criteria 본문 추가)

## Amendment 1 (CFP-390, 2026-05-11)

본 Amendment 는 CFP-390 (인벤토리 backfill, Issue #395) 의 Phase 1 carrier 산출물.

ADR-060 framework SSOT 의 4 정정:

### Amendment 1-결정 6 (c) 정정 — `sibling_dependencies` CFP-391 → CFP-412 verbatim 정정

본 ADR §결정 6 (c) `sibling_dependencies` 의 의미 = warning → enforce 승격 전 main merge 의무 sibling Story. 원본 항목 `CFP-391` (Issue #396, 4-tier 정식 amendment 예상 carrier) 는 2026-05-11 시점 **closed without delivery** (Issue #396 close, 4-tier amendment 작업 미실행). 후속 carrier 재예약 = **CFP-412** (Issue #412 — 4-tier amendment 재예약 carrier).

따라서 `docs/evidence-checks-registry.yaml` 의 `entries[name=adr-sunset-criteria].promotion_criteria.sibling_dependencies` 다음과 같이 정정 의무 (본 Amendment 1 carrier PR 동반):

```yaml
sibling_dependencies:            # ADR-060 §결정 6 (c) — Amendment 1 정정
  - CFP-390  # 인벤토리 backfill — 본 Amendment 1 carrier (이미 발효)
  - CFP-412  # 4-tier amendment 재예약 carrier (CFP-391 #396 폐기 처리)
```

### Amendment 1-결정 12 정정 — 후속 carrier 목록 정정

본 ADR §결정 12 의 후속 carrier 목록 4 항목 중 CFP-391 항목 정정:

- **CFP-391 (4-tier 정식 amendment)** (원본 표기) →
- **CFP-391 (Issue #396 closed without delivery, 2026-05-11) → CFP-412 (Issue #412) 가 4-tier 정식 amendment carrier 재예약** (`current_tier` required 전환 + tier enum 정식 분류 + schema v1.0 → v1.1 MINOR bump)

본 정정은 ADR-058 §결정 9 amendment chain 정책 (framework SSOT 변경 동반 시 framework ADR amendment 정합) 정합. 4-tier amendment 자체는 framework SSOT 의 schema field semantic 변경 (`current_tier` optional → required) 동반 → ADR-060 amendment 가 정합 carrier.

### Amendment 1-결정 13 (신설) — 인벤토리 backfill SSOT (18 entry 그룹 A 등록 — FIX iter 1 정정 후)

> **Scope 한정**: 본 표는 CFP-389 / CFP-390 작업 시점 "기존 ad-hoc evidence check" 인벤토리만 포함. 후속 framework entry (예: CFP-393 가 추가한 `rate-limit-fallback-rate`) 는 표 scope 외 — 각 carrier ADR / Story 가 자체 registry row 등록을 책임진다.

본 CFP-390 = ADR-060 framework 의 첫 multi-entry registry 운영 진입. CodebaseMapper SubAgent perspective 통합 정밀 verify (scripts/check-*.sh 33개 + .github/workflows/ 20개 + templates/github-workflows/ 24개 전수 inspect) 결과 4-criteria (detect_command + workflow + owner_adr/contract + tier signal) PASS entry 18개 그룹 A 등록 (Codex Proactive Check #2/#6 FIND-3 정정 후 — owner_adr 정합 ADR/contract 명확 entry 만).

**Scope split 명시 (FIND-2 정정)**:
- **Phase 1 PR (본 carrier) = SSOT 만**: 본 §결정 13 표 + 그룹 B/C 분류 + sibling_dependencies field substitution (CFP-391 → CFP-412) + CLAUDE.md cross-ref. registry yaml 의 실제 row append 는 **수행하지 않음**.
- **Phase 2 PR scope = 본 §결정 13 표의 18 entry 실제 row append**: `docs/evidence-checks-registry.yaml` 의 schema v1.0 정합 row 작성. doc-only fast-path 적용 가능성 ArchitectAgent / DeveloperPL 후속 판단 (ADR-054 정합, 모호 시 full-lane).
- **tier 재계산 (FIND-4 정정)**: 실제 `templates/branch-protection-manifest.yaml` 부착 entry 만 `blocking-on-pr` / `blocking-on-merge` 분류. 미부착 entry = `warning` 일괄 하향. manifest 부착 = 2 entry (invariant-check / phase-gate-mergeable). doc-frontmatter-schema / doc-section-schema 는 manifest 부착 (row 3/4) 이나 owner_adr 모호로 FIND-3 그룹 B 강등.

**그룹 A — 18 entry SSOT (Phase 2 PR row append target)**:

| # | name | detect_command | workflow | owner_adr/contract | tier (final) |
|---|---|---|---|---|---|
| 1 | `lane-evidence-trail` | `bash scripts/check-lane-evidence.sh` | `.github/workflows/lane-evidence-check.yml` | ADR-031 §결정 3 + fix-event-v1 | `warning` (manifest 미부착) |
| 2 | `doc-locations-registry` | `bash scripts/check-doc-locations.sh --full` | `.github/workflows/doc-locations-check.yml` | ADR-041 | `warning` (manifest 미부착 — CLAUDE.md "5번째" narrative 와 drift, 별도 Issue 권고) |
| 3 | `marketplace-parity` | `bash scripts/check-marketplace-parity.sh` | `.github/workflows/marketplace-parity.yml` | ADR-016 / ADR-023 §결정 5 | `warning` |
| 4 | `invariant-check` | (workflow inline — 5 invariant 직접) | `.github/workflows/invariant-check.yml` | ADR-002 (footer pattern) + 다중 CFP (5/7/8/10) | `blocking-on-pr` (branch-protection-manifest row 2) |
| 5 | `phase-gate-mergeable` | (workflow inline — cross-repo Story fetch) | `.github/workflows/phase-gate-mergeable.yml` | ADR-031 §결정 3 + label-registry-v2 | `blocking-on-merge` (branch-protection-manifest row 1, dynamic checks.create) |
| 6 | `inter-plugin-contracts` | `bash scripts/check-inter-plugin-contracts.sh` | `.github/workflows/contract-lint.yml` job:`inter-plugin-contracts` | ADR-008 / ADR-010 / MANIFEST.yaml | `warning` |
| 7 | `inter-plugin-drift` | `bash scripts/check-inter-plugin-drift.sh` | `.github/workflows/contract-lint.yml` job:`inter-plugin-drift` | ADR-011 | `warning` |
| 8 | `comment-prefix-registry` | `bash scripts/check-comment-prefix.sh` | `.github/workflows/contract-lint.yml` job:`comment-prefix-registry` | comment-prefix-registry-v1 (kind:registry) | `warning` |
| 9 | `label-registry-sync` | `bash scripts/check-label-registry.sh` | `.github/workflows/contract-lint.yml` job:`label-registry-sync` | label-registry-v2 (kind:registry) | `warning` |
| 10 | ~~`marketplace-sync`~~ (retired CFP-457) | ~~`bash scripts/check-marketplace-sync.sh`~~ | ~~`.github/workflows/contract-lint.yml` job:`marketplace-sync`~~ | ~~ADR-016~~ | ~~`warning`~~ — see entry #5 `marketplace-parity` (CFP-50 / ADR-023) for SSOT |
| 11 | `dogfood-artifact-paths` | `bash scripts/check-dogfood-artifact-paths.sh` | `.github/workflows/dogfood-artifact-paths.yml` | ADR-013 / ADR-017 | `warning` |
| 12 | ~~`superpowers-integration`~~ (retired — dead file, ADR-122) | ~~`bash scripts/check-superpowers-integration.sh`~~ | ~~`.github/workflows/superpowers-integration.yml`~~ | ~~ADR-028 / CFP-113~~ | ~~`warning`~~ |
| 13 | ~~`superpowers-schema-drift`~~ (retired — dead file, ADR-122) | ~~`bash scripts/check-superpowers-schema-drift.sh`~~ | ~~`.github/workflows/superpowers-schema-drift.yml`~~ | ~~ADR-028 / CFP-121~~ | ~~`warning` (scheduled quarterly + PR:paths)~~ |
| 14 | `parallel-epic-conflict` | (workflow inline — PR file 교집합) | `.github/workflows/parallel-epic-conflict-check.yml` | ADR-050 | `warning` (continue-on-error prior art) |
| 15 | `branch-protection-drift` | (workflow inline — gh api + manifest diff) | `.github/workflows/branch-protection-drift-check.yml` | ADR-024 Amendment 2 | `warning` (weekly Mon 09:00 UTC cron) |
| 16 | `required-workflow-drift` | (workflow inline + `check-enterprise-admin.sh`) | `.github/workflows/required-workflow-drift-check.yml` | ADR-162 §결정 3 | `warning` (weekly Mon 10:00 UTC cron) |
| 17 | `rulesets-drift` | (workflow inline + `check-enterprise-admin.sh`) | `.github/workflows/rulesets-drift-check.yml` | ADR-162 §결정 1 | `warning` (daily 09:00 UTC cron) |
| 18 | `write-permission-redistribution` | `bash scripts/check-write-permission-redistribution.sh` | `.github/workflows/lint.yml` job:`write-permission-redistribution` | CFP-26 / ADR-009 (write 권한 invariant) | `warning` |

**tier 최종 분포**: `blocking-on-merge` 1 (phase-gate-mergeable) + `blocking-on-pr` 1 (invariant-check) + `warning` 16. manifest 부착 entry 만 blocking 분류.

**그룹 B — 보류 (별도 carrier 책임, 14 entry — FIND-3 강등 8 + 기존 6)**:

| name | 미충족 / 모호 | 처리 |
|---|---|---|
| `story-section-schema` | (c) **owner_adr 정합 ADR 미존재** — CFP-91 / CFP-94 비-ADR (FIND-3 강등) | 등록 보류 — CFP-412 schema v1.1 또는 별도 carrier 가 `owner_adr=null` 또는 `owner_contract` enum 도입 후 등록 |
| `doc-frontmatter-schema` | (c) **owner_adr 정합 ADR 미존재** — CFP-28 비-ADR (FIND-3 강등, manifest row 3 부착이나 owner_adr governance integrity 약함) | 동일 — schema v1.1 owner_adr=null 도입 후 등록 + 부착된 manifest row 와 tier 정합 별도 검토 |
| `doc-section-schema` | (c) **owner_adr 정합 ADR 미존재** — CFP-28 비-ADR (FIND-3 강등, manifest row 4 부착이나 owner_adr governance integrity 약함) | 동일 |
| `workflow-yaml-syntax` | (c) **owner_adr 정합 ADR 미존재** — CFP-34 비-ADR (FIND-3 강등) | 동일 |
| `consumer-scripts-manifest` | (c) **owner_adr 정합 ADR 미존재** — CFP-109 비-ADR (FIND-3 강등) | 동일 |
| `script-exec-bit` | (c) **owner_adr 정합 ADR 미존재** — CFP-74 invariant 비-ADR (FIND-3 강등) | 동일 |
| `markdown-internal-links` | (c) **owner_adr 정합 ADR 미존재** — CFP 미명시 (FIND-3 강등) | 동일 |
| `agent-frontmatter` | (c) ADR-042 = agent **model selection** policy 이지 agent frontmatter contract 의 owner 아님 — owner_adr 정합 ADR 미존재 (FIND-3 강등) | 동일 |
| `check-fix-evidence` | (b) workflow trigger 부재 (CFP-298 carrier 책임 — wrapper repo 미배치 가능성) | 등록 보류 — Phase 2 또는 별도 carrier 에서 workflow 도입 후 등록 |
| `check-no-atlassian` | (c) owner_adr 부재 (meta-governance) BUT detect_command 보유. workflow trigger 명확치 않음 | 등록 보류 — owner_adr 도입 후속 carrier 발의 권고 |
| `check-container-strategy` | (c) ADR-033 명확 BUT (b) workflow trigger 부재 — `container-image-scan.yml` consumer-only | 등록 보류 — consumer-only entry 분류 정책 명확화 후 |
| `check-domain-knowledge-schema` | (b) workflow trigger 명확치 않음 | 등록 보류 — workflow trigger 검증 후 |
| `check-review-verdict-v4` | (b) workflow trigger 명확치 않음 | 등록 보류 — workflow trigger 추가 도입 후 (CFP-137 후속) |
| `check-team-spec-schema` | (b) workflow trigger 명확치 않음 | 등록 보류 — workflow trigger 추가 도입 후 (CFP-137 후속) |

**그룹 C — 등록 제외 (4-criteria 미충족 / consumer-only / sub-utility)**:

- `check-codeforge-version-drift` — workflow 부재 (session-start CLI script, CLAUDE.md 세션 개시 의무 0번)
- `check-enterprise-admin` — sub-utility (rulesets-drift-check + required-workflow-drift-check 의 step, 단독 workflow 없음)
- `check-debut-audit-signals` / `check-debut-readiness` — consumer-specific (ADR-021 mctrader debut audit, wrapper governance scope 외)
- `check-doc-links` — `markdown-internal-links` (lint.yml inline) 와 중복
- bootstrap-*.sh / test-*.sh (30+) / audit-trail-fetch.sh / next-phase.sh / migrate-*.sh / post-merge-*.sh / sync-*.sh / retro-retry-helper.sh / check-lint.sh — not lint / helper / migration
- consumer-only workflow (self-app parity 제외): 전체 목록의 authoritative SSOT = `.github/workflows/invariant-check.yml` 의 `CONSUMER_ONLY_WORKFLOWS` bash 배열. 본 ADR 은 dual-maintenance drift 원천 제거(CFP-2678 / Amendment 21 §결정 34)를 위해 사본 enumeration 을 두지 않고 SSOT 를 참조한다 — 이 bullet 에 개별 workflow 명 목록을 재추가하지 말 것(재추가 = drift 재유입).

본 그룹 A **18 entry** (FIX iter 1 정정 후 — owner_adr 정합 ADR/contract 명확 entry 만, 8 entry 그룹 B 강등) 의 registry yaml row append 는 **CFP-390 Phase 2 PR scope** (본 Amendment 1 = Phase 1 ADR 갱신 + 후속 carrier 정정 + 인벤토리 SSOT 확정). Phase 2 PR 진행 여부 = doc-only fast-path 가능성 ArchitectAgent / DeveloperPL 판단 (ADR-054 모호 시 full-lane).

### Amendment 1-결정 14 (신설) — 메타 anomaly lint 후속 carrier 의무 명시 (Codex P2-B 정합)

본 CFP-390 인벤토리 backfill = manual sweep. 후속 신규 evidence-enforceable 패턴 (script + workflow) 도입 시 registry 등록 누락 = governance drift 위험. Codex Proactive Check #4 P2-B (사전 수렴 시점 raised) finding 정합 — 본 Amendment 1 가 메타 anomaly lint 후속 carrier 의무 명시:

- **carrier 발의 의무**: CFP-390 Phase 1 PR merge 후 별도 CFP/Issue 발의. 본 Story scope 외.
- **carrier scope**: `scripts/check-evidence-registry.sh` (또는 동등) 신설 — registry yaml 미등록 신규 evidence-enforceable 패턴 (예: 신규 `.github/workflows/*.yml` + `scripts/check-*.sh` 동반 도입 PR) 자동 발견 lint.
- **trigger 추정**: `.github/workflows/evidence-registry-anomaly.yml` (pull_request:paths) — script/workflow file 변경 시 registry yaml 등록 누락 lint.
- **tier 추정**: `warning` (false positive 위험 — 새 lint script 가 production 정합 의제로 즉시 인식 부담).
- **owner_adr 후보**: ADR-060 (본 framework SSOT — meta lint 가 framework 의 안전망 강화 측면).

본 carrier 부재 시 = manual inventory sweep 정합 유지 (반복 CFP 비용). 본 Amendment 14 명시 = CFP-390 retro (§11) 의 reminder 1 항목 + 후속 발의 의무 SSOT 화.

## Amendment 2 (CFP-455, 2026-05-12)

본 Amendment 는 CFP-455 (4-tier enforcement 분류 정식화, Issue #455) 의 Phase 1 carrier 산출물. CFP-391 (Issue #396, closed without delivery 2026-05-11) / CFP-412 (Issue #412, post-merge-followup workflow false-positive close 2026-05-11) 의 재재예약 carrier — 4-tier amendment 정식 deliver.

### Amendment 2-결정 3 (변경) — `current_tier` 필드 optional → required 전환 명시

본 ADR §결정 3 의 4-tier enum 본문 "본 ADR (CFP-389) 의 첫 entry = `warning` tier. 후속 Story (CFP-391) 가 본 enum 을 정식 명시 + 기존 entry retroactive 분류. 본 ADR 시점에서는 enum 정의만 제공, registry yaml 의 `current_tier` 필드는 optional (CFP-391 시점 required 전환 = MINOR bump)." → **본 CFP-455 (4-tier 정식 amendment carrier, CFP-391 #396 / CFP-412 #412 폐기 후 재예약) 가 `current_tier` 필드 optional → required 전환을 정식 deliver**. schema doc `docs/inter-plugin-contracts/evidence-check-registry-v1.md` v1.0 → v1.1 MINOR bump 동반 + registry yaml `schema_version: "1.0"` → `"1.1"` header 갱신 동반.

**retroactive 분류 검증 의무**: 본 Amendment 2 시점 = 22/22 entry 모두 현행 `current_tier` 보유 verified (CodebaseMapper SubAgent perspective 정밀 verify, 2026-05-12). mechanical regression 0건 — 신규 메타 lint (`scripts/check-evidence-registry.sh`, Phase 2 PR scope) 가 schema 정합 mechanical 강제.

### Amendment 2-결정 6 (c) 정정 — `sibling_dependencies` field back-substitution (append)

본 ADR §결정 6 (c) 의 `sibling_dependencies` 의미 = warning → enforce 승격 전 main merge 의무 sibling Story. Amendment 1 시점 = `[CFP-390, CFP-412]` (CFP-391 → CFP-412 정정). CFP-412 Issue #412 도 closed without delivery (2026-05-11T15:41:42Z, post-merge-followup workflow false-positive close — PR #421 = CFP-393 rate-limit-fallback 작업, "Closes #412" reference 없음) — 4-tier amendment 0 commits. 본 Amendment 2 의 결정:

```yaml
sibling_dependencies:            # ADR-060 §결정 6 (c) — Amendment 2 정정 (CFP-455)
  - CFP-390  # 인벤토리 backfill — 본 Amendment 1 carrier (이미 발효)
  - CFP-412  # 4-tier amendment 재예약 carrier (CFP-391 #396 폐기 처리) — Amendment 1 정정 / CFP-412 자체도 #412 closed without delivery
  - CFP-455  # 4-tier 정식 amendment carrier (재재예약) — 본 Amendment 2 deliver
```

**append 결정 근거** (DataMigrationArch SubAgent + RequirementsPL Q2 권고 verbatim 채택):
- CFP-412 의 폐기 history 가 registry yaml 에서 visible 보존 (replace 시 invisible 위험).
- sibling 의도 ("4-tier amendment 가 main merge 의무") 보존 — append 로 chain 가시화.
- 폐기 carrier 의 trail 이 framework SSOT 의 governance integrity 강화.

### Amendment 2-결정 14 (정정) — 메타 anomaly lint 와 메타 schema validation lint 분리 (별도 entry 2종)

Amendment 1 §결정 14 의 메타 anomaly lint (인벤토리 누락 감지) 와 본 Amendment 2 가 도입 명시하는 메타 schema validation lint (`scripts/check-evidence-registry.sh`, 본 Story Phase 2 PR scope) 는 **scope 가 다른 별도 lint 2종**:

| lint | scope | trigger | tier |
|---|---|---|---|
| **메타 schema validation** (본 Story 도입) | registry yaml 자체 schema/일관성 검증 — 6 검증 (schema_version / entry required field / current_tier enum / bypass pair / name uniq / owner_adr+carrier_adr ADR file cross-ref) | `pull_request:paths` (registry yaml + contract md + lint script 변경 시) | `warning` (continue-on-error) |
| **메타 anomaly detection** (§결정 14 후속 carrier, 본 Story scope 외) | registry yaml 미등록 신규 evidence-enforceable 패턴 자동 발견 (신규 `.github/workflows/*.yml` + `scripts/check-*.sh` 동반 도입 PR) | `pull_request:paths` (workflows + scripts 변경 시) | `warning` (false positive 위험) |

**분리 근거** (RequirementsPL Q6 권고 verbatim 채택): 통합 시 lint script 복잡도 증가 + trigger paths 모호. 분리 시 각자 carrier 별도 (메타 schema validation = 본 Story CFP-455 / 메타 anomaly = §결정 14 후속 carrier).

### Amendment 2-결정 15 (신설) — 메타 lint exit-code 3-tier semantics (Codex AREA 1 정합)

`scripts/check-evidence-registry.sh` (Phase 2 PR scope) 의 exit code 의미:

| exit code | 의미 | 처리 |
|---|---|---|
| **0** | PASS — 모든 검증 통과 | normal continuation |
| **1** | validation FAIL — 1+ entry 가 schema 위반 (current_tier 부재 / enum 외 값 / bypass pair 위반 / name 중복 / owner_adr+carrier_adr ADR file 부재 등) | warning mode = continue-on-error (PR merge 가능) / blocking mode 승격 시 PR block |
| **2** | meta-error — tooling 오류 (yaml 파싱 실패 / pyyaml 미설치 / registry yaml 자체 file 부재 / ADR file glob unreadable 등) | warning / blocking 무관 = 명확한 error message 출력 + workflow job step fail (lint logic 실행 불가 상황 분리 명시) |

**근거**: validation FAIL 과 meta-error 의 semantic 분리 — meta-error 가 false-positive validation FAIL 로 위장되면 운영 신뢰도 추적 (ADR-060 §결정 5 EC-B 14d/5건 trigger) 가 왜곡. 3-tier semantics 도입 = false positive rate 측정의 무결성 보장.

### Amendment 2-결정 16 (신설) — warning-tier bypass_label policy (Codex AREA 2 (a) 정합)

본 ADR §결정 7 의 `bypass_label` 정책 명세화:

- **warning tier** = continue-on-error / non-blocking. bypass_label 적용은 의미 부적용 (skip 의미 없음 — 이미 PR block X). → `bypass_label` field = **optional** (omit 권고).
- **blocking-on-pr / blocking-on-merge / hotfix-bypass tier** = required check. bypass_label 의무 분리:
  - `blocking-on-pr` / `blocking-on-merge` = bypass_label optional (운영 장애 hotfix 시 도입 가능, 미도입 시 emergency-channel 부재 risk 분리 평가).
  - `hotfix-bypass` = bypass_label **required** (정의상 bypass channel SSOT).

**본 Story 의 메타 lint self-application entry** (Phase 2 PR scope) = warning tier → bypass_label omit. 정합: SecurityArch SubAgent spoofing 차단 invariant 강화 (bypass field 의 잘못된 의미 부여 회피).

### Amendment 2-결정 17 (신설) — Retroactive reclassification failure handling (Codex AREA 2 (b) 정합)

본 Amendment 2 의 `current_tier` required 전환 시점 = 22/22 entry 모두 현행 `current_tier` 보유 verified (CodebaseMapper SubAgent 정밀 verify). 단 future drift / human error 로 enum membership 위반 발견 시 (예: 신규 entry 가 `current_tier: hard_block` 사용자 alias 주입, registry yaml 의 retroactive corruption):

- **처리**: `scripts/check-evidence-registry.sh` exit 1 (validation FAIL) + PR block (blocking mode 승격 시) — **immediate fail**.
- **근거**: required tier 도입 의의 정합 — schema 정합 mechanical 강제가 framework SSOT 의 핵심. tolerant mode (warning continuation) 도입 시 required 의 mechanical 효력 무력화.
- **본 Story 단계 (warning mode)** = continue-on-error → PR merge 가능 but lint output 의 violation 명확 표시 + 운영 가이드 ADR-060 §결정 5 EC-B 14d/5건 trigger 적용. 실제 PR block 효과는 promotion carrier 시점 (별도 CFP-NNN, evidence 6 산출물 제출 시).

### Amendment 2-결정 18 (신설) — Marketplace/sibling sync necessity 명시 (Codex AREA 2 (c) 정합)

본 Amendment 2 의 schema v1.0 → v1.1 MINOR bump 시 sibling sync 의무 분석:

- **registry yaml** (`docs/evidence-checks-registry.yaml`) = wrapper-owned cross-cutting protocol (kind:registry, ADR-010 scope 외 = sibling sync 불필요).
- **schema doc** (`docs/inter-plugin-contracts/evidence-check-registry-v1.md`) = wrapper-owned canonical (ADR-010 scope 외 = sibling sync 불필요).
- **MANIFEST.yaml** = wrapper-owned cross-cutting registry list (sibling sync 불필요).
- **marketplace.json mirrored field sync**: schema v1.1 bump 동반 plugin.json MINOR bump (5.18.0 → 5.19.0, ADR-037 정합 — CFP-500 이 main 에서 5.18.0 차지 후 rebase 시 5.19.0 으로 re-bump) → ADR-063 §결정 1 atomic invariant (plugin.json + CHANGELOG.md + marketplace.json 동시 처리) 발효 → marketplace sync PR **의무** (별도 PR, codeforge PR merge 후 즉시 open·merge — ADR-063 §결정 2 chicken-and-egg 회피).

**정리**: kind:registry schema 변경 자체는 sibling sync 불필요 (Codex AREA 2 (c) 권고 정합). 단 plugin version MINOR bump 동반 시 marketplace.json mirrored field sync 가 ADR-063 invariant 로 의무. 본 Story Phase 2 PR (또는 Phase 1 PR) 의 plugin.json MINOR bump 와 같은 PR 안 처리.

### §결정 19 (Amendment 6, CFP-509 — 2026-05-13)

**Recurrence-based advisory promotion signal**: evidence-check-registry schema v1.2 의 `recurrence:` field 가 machine-usable recurrence metric 제공. `recurrence.count ≥ recurrence.threshold` 도달 시:

- **advisory mode** (기본): `recurrence.promotion_trigger: advisory` — PR comment 만 (warning tier 유지, blocking transition 없음). `[recurrence-threshold-reached]` marker 자동 발화.
- **auto_blocking mode**: `recurrence.promotion_trigger: auto_blocking` — 별도 carrier Story 가 actual `current_tier: warning → blocking-on-pr` 승격 평가 의무 (자동 transition 아님 — governance 보존).
- **none mode** (default): `recurrence.count` 누적만, advisory / blocking 모두 미발화.

본 §결정 = §결정 6 (warning → blocking 승격 gate) 의 supplementary signal — 기존 3 condition (pr_cumulative_min / failure_threshold / sibling_dependencies) 와 OR 관계 아님 (additional advisory). actual transition 은 여전히 별도 carrier 의무.

**CFP-490 lane-evidence-trail entry description-only `recurrence_count` 의 schema 흡수**: CFP-500 FIX-5 + CFP-451 transient 2회 historical evidence (description body 영역) → `recurrence.count: 2` schema-level 정식 표기. machine-usable 전환.

### Mermaid 다이어그램 동기화 (Amendment 2 — Codex AREA 4 정합)

본 ADR `## 다이어그램` Mermaid 의 `K -->|"CFP-390 + CFP-412 merged<br/>(Amendment 1: CFP-391 폐기 → CFP-412)"|` row 갱신 의무 (Amendment 2 시점 CFP-412 도 폐기 → CFP-455 carrier append):

본 Amendment 2 carrier PR 안에서 `## 다이어그램` 본문의 해당 row 를 `K -->|"CFP-390 + CFP-412 + CFP-455 merged<br/>(Amendment 2: CFP-412 폐기 → CFP-455 carrier)"|` 으로 갱신 (carrier PR 본 §결정 동반 직접 edit). Mermaid stale 차단 — diagram 이 §결정 6 (c) sibling_dependencies 의 SSOT 와 verbatim 정합.

## Amendment 7 (CFP-508, 2026-05-13)

본 Amendment 는 CFP-508 (evidence-registry-naming convention lint, Issue #508) 의 Phase 1 carrier 산출물. CFP-490 FU-2 carrier.

### §결정 20 (Amendment 7, CFP-508 — 2026-05-13)

**Entry name ↔ workflow file naming convention**: evidence-checks-registry entry 의 `name` field 와 `workflow:` field 의 file basename 자연스러운 divergence 허용 — multi-job workflow pattern 인정:

- **EXACT match (default)**: entry name = workflow basename (`.yml` 제외). 권장 패턴.
- **partial match**: entry name 이 workflow basename 의 substring 또는 vice versa. 자연스러운 변형 (e.g., `carrier-bootstrap` ↔ `carrier-bootstrap-check`). 허용.
- **multi-job pattern**: 단일 workflow file 안 여러 job 이 별개 evidence-check entry 로 등록 (e.g., `contract-lint.yml` 안 `inter-plugin-contracts` / `inter-plugin-drift` / `comment-prefix-registry` / `label-registry-sync` jobs). registry entry name = workflow job name (workflow file basename 과 무관). 허용.
- **Conservative no-rename policy**: 기존 entry 에 대한 workflow rename 금지 — CI history + branch protection `required_status_checks.contexts` 영향 회피. 신규 entry 도입 시만 EXACT match 권장.

**Lint enforcement** (`scripts/check-evidence-registry-naming.sh`):
- workflow file 존재 검증 의무 (templates/ 기준 file path 실제 존재).
- DRIFT (no match) entry = allowlist hardcode 의무 (별도 file rename 필요 시 후속 carrier Story).
- `github-actions-runtime` detect_command entry 는 workflow file 존재만 검증 (job name 무관).
- `Retired` status entry skip.
- Exit code 3-tier (ADR-060 Amendment 2 §결정 15): 0 PASS / 1 violation (workflow file 부재 OR allowlist 밖 DRIFT) / 2 meta-error (yaml parse 실패 / python3 미설치 등).

**DRIFT allowlist 10건** (CFP-508 audit 결과 — Conservative no-rename policy 첫 적용):

| entry name | workflow basename | pattern |
|---|---|---|
| `rate-limit-fallback-rate` | `rate-limit-fallback-kpi.yml` | basename divergence (rate vs kpi) |
| `lane-evidence-trail` | `lane-evidence-check.yml` | basename divergence (trail vs check) |
| `doc-locations-registry` | `doc-locations-check.yml` | basename divergence (registry vs check) |
| `inter-plugin-contracts` | `contract-lint.yml` | multi-job pattern (ADR-008/010) |
| `inter-plugin-drift` | `contract-lint.yml` | multi-job pattern (ADR-011) |
| `comment-prefix-registry` | `contract-lint.yml` | multi-job pattern (comment-prefix-registry-v1) |
| `label-registry-sync` | `contract-lint.yml` | multi-job pattern (label-registry-v2) |
| `marketplace-sync` | `contract-lint.yml` | Retired entry / multi-job pattern (CFP-457) |
| `write-permission-redistribution` | `lint.yml` | multi-job pattern (lint.yml shared job) |
| `evidence-registry-schema-validation` | `evidence-registry-check.yml` | basename divergence (schema-validation vs check) |

**ratchet 위반 0건** — lint scope 확장 (workflow file existence lint 의무 + DRIFT allowlist hardcode 10건) + framework 의 자연스러운 사용 사례 정식 인정 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT permanent governance).

**sibling_dependencies append**: `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506, CFP-509, CFP-508]` (Amendment 2 §결정 6 (c) chain 정합).

## Amendment 8 (CFP-530, 2026-05-13)

본 Amendment 는 CFP-530 (Workflow yml `permissions:` block 일괄 hardening, Issue #530) 의 Phase 1 carrier 산출물. CFP-506 §11.1 entry 5 (workflow yml permissions block 일괄 hardening follow-up CFP) + CFP-520 retro carrier reference 종합 해소.

### §결정 21 (Amendment 8, CFP-530 — 2026-05-13)

**N번째 warning-tier entry 등록** — `workflow-permissions-block-presence`:

evidence-checks-registry.yaml 에 신규 row append (Phase 2 PR scope). framework 의 자연스러운 사용 사례 entry 추가 — schema 변경 0건 (Amendment 2 schema v1.1 정합 유지).

**Entry 필드 SSOT** (registry yaml row 형식):

```yaml
  - name: workflow-permissions-block-presence
    description: |
      Workflow yml top-level `permissions:` block 부재 mechanical lint.
      GitHub Actions least-privilege standard 정합 (Secure use reference) —
      `permissions:` 부재 시 GITHUB_TOKEN 의 모든 scope 자동 grant (over-privileged) →
      top-level block 명시 후 per-job override (granular least privilege) 패턴 강제.
      CFP-506 PR #519 CodeQL `actions/missing-workflow-permissions` query 권고 해소 carrier.
      Glob scope: `.github/workflows/*.yml` + `templates/github-workflows/*.yml`
      (`*.yaml` 확장자 제외 — fixture file 면제).
    detect_command: bash scripts/check-workflow-permissions-presence.sh
    workflow: templates/github-workflows/workflow-permissions-check.yml
    current_tier: warning  # ADR-060 §결정 5 — 첫 도입 = warning mode (continue-on-error: true)
    bypass_label: hotfix-bypass:workflow-permissions
    bypass_audit_lint: bash scripts/check-bypass-audit-comment.sh
    promotion_criteria:
      pr_cumulative_min: 20            # ADR-060 §결정 6 (a)
      failure_threshold: 0             # ADR-060 §결정 6 (b)
      sibling_dependencies: []         # 신규 entry — sibling 없음 (CFP-530 carrier self)
      evidence_artifacts:
        - github_actions_run_history_url
        - lint_failure_count_zero_proof
        - pr_cumulative_count_proof
    modal_anti_pattern_dictionary: {}  # 본 lint = schema 검증, modal phrase 검사 미포함
    introduced_by: CFP-530
    owner_adr: ADR-060                  # framework SSOT 직접 carrier
    carrier_adr: ADR-060                # self-carrier (Amendment 8)
    recurrence:
      count: 0
      promotion_trigger: none      # ADR-060 §결정 19 (Amendment 6) — schema v1.2 default
    status: Active
```

**Tier 매핑 SSOT — 16 file remediation surface** (Phase 2 PR scope, SecurityArch finalize T0-T7 framework 정합):

| File 그룹 | 개수 | 적용 tier | scope |
|---|---|---|---|
| 14 MISSING (read-only lint) | 14 | **T1 base** | `permissions: contents: read` |
| 2 JOB-LEVEL upgrade (`wording-ssot-check.yml` x2) | 2 | **T1 base** | `permissions: contents: read` (job-level → top-level move) |
| ~~2 `superpowers-schema-drift.yml` (.github + templates)~~ (retired — file 부재, ADR-122) | ~~(이미 14 MISSING 안 포함)~~ | ~~**T1 top-level + T3 schedule job override**~~ | ~~top-level `contents: read` + schedule job `issues: write` (TH-7 sealed verdict 정합 — EC-4 job-level escalation 채택)~~ |
| 1 pair `test.yml` (.github vs templates) | 2 file (의도적 divergence) | **T1 base** each | 양쪽 독립 hardening, mirror invariant 비대상 (Story §2.4) |

**TH-7 sealed verdict** (SecurityArch finalize): scheduled conditional issue create job 만 `issues: write` 권한 escalate — top-level `issues: write` 가 PR 경로까지 권한 확대 = least privilege 위반 회피 (Story §5.3 EC-4 정합).

**Hotfix-bypass label 명명**: `hotfix-bypass:workflow-permissions` — ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **10번째 hotfix-bypass:* family member** (기존 9: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check). label-registry-v2 v2.5 same-MINOR sub-entry append 동반 (frontmatter `version` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).

**Promotion criteria** (warning → blocking-on-pr, ADR-060 §결정 6 AND condition):
- (a) pr_cumulative_min: 20 PR 누적 (velocity-normalized — §결정 10)
- (b) failure_threshold: 0 bypass 외 failure
- (c) sibling_dependencies: [] (신규 entry — sibling 없음, 본 carrier self-application)

승격 평가 책임 = 별도 carrier Story (warning → blocking-on-pr transition 자동 아님, governance 보존 — Amendment 6 §결정 19 정합).

**ratchet 위반 0건** — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT permanent governance).

**sibling_dependencies append**: `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506, CFP-509, CFP-508, CFP-530]` (Amendment 2 §결정 6 (c) chain 정합).

**CFP-300 cross-ref** (third-party action SHA-pinning policy) — 직교 정책 결합: token scope 최소화 (본 Amendment 8) + action 신뢰성 immutable pinning (CFP-300) = supply chain security family AND 결합 완성. 두 정책 independent invariant 유지.

**Mermaid 다이어그램 동기화** (Amendment 2 §결정 6 (c) chain 정합): 본 ADR `## 다이어그램` Mermaid 의 carrier chain row 갱신은 추후 다이어그램 갱신 carrier 가 통합 처리 (현재 chain length 9 — CFP-530 까지 보존 의무).

### §결정 22 (Amendment 9, CFP-583 — 2026-05-13)

**7th warning-tier entry 등록** — `workflow-yaml-parse`:

CFP-578 retro 후속 audit 결과 6 workflow file (decision-principle-vocabulary / adr-sunset-criteria / auto-phase-label / worktree-first-pre-checkout / carrier-bootstrap-check / handoff-wording-check) 가 multi-line bash `BODY="${HEADER}\n\n` + 3-backtick fence + `${VAR}` interpolation 패턴으로 인해 yaml ScannerError 유발 → `pull_request` listener 미등록 → workflow startup_failure + jobs:[] empty + PR statusCheckRollup 0 attach. carrier merge 시점부터 zero-coverage 운영 sentinel — Amendment 3/4/5/6/7 framework SSOT 의 mechanical enforcement 가 false-PASS.

PR #581 evidence chain (3 runs, cfp-578 branch, event=push, conclusion=failure, jobs:[]): adb15b4 / 6c084d8 / dbd556f — workflow `name:` field path fallback (yml top parse 실패) + `pull_request` event 0건. RequirementsPL §1 진술의 H1/H2/H3 가설 모두 reject — root cause = yaml scanner block scalar 종료 모호성 (path filter / cache / dispatch race 영역 도달 전 단계 fail).

**Entry 필드 SSOT** (registry yaml row 형식, Phase 2 PR append target):

```yaml
  - name: workflow-yaml-parse
    description: |
      ADR-060 §결정 23 — workflow yml YAML scanner ambiguity 감지 carrier (CFP-583 sentinel).
      Multi-line bash `BODY="${HEADER}\n\n` + 3-backtick fence + `${VAR}` interpolation 패턴이
      PyYAML strict ScannerError + GitHub Actions Go parser jobs:[] silent fail 유발. 6 file
      재현 evidence (decision-principle-vocabulary / adr-sunset-criteria / auto-phase-label /
      worktree-first-pre-checkout / carrier-bootstrap-check / handoff-wording-check).
      validation: `python -c "import yaml; yaml.safe_load(open('<file>'))"` (PyYAML safe_load)
      + actionlint binary (Go 기반 GitHub Actions parser semantics 정합).
    detect_command: bash scripts/check-workflow-yaml-parse.sh
    workflow: templates/github-workflows/workflow-yaml-parse.yml
    current_tier: warning            # ADR-060 §결정 5 — 첫 도입 = warning mode
    bypass_label: hotfix-bypass:workflow-yaml-parse
    bypass_audit_lint: bash scripts/check-bypass-audit-comment.sh   # CFP-389 prior art reuse
    promotion_criteria:
      pr_cumulative_min: 20          # ADR-060 §결정 6 (a) / §결정 10 velocity-normalized
      failure_threshold: 0           # ADR-060 §결정 6 (b)
      sibling_dependencies: []       # 독립 entry — workflow self-app + 6 file 정정 외 의존 없음
      evidence_artifacts:
        - github_actions_run_history_url
        - lint_failure_count_zero_proof
        - pr_cumulative_count_proof
    introduced_by: CFP-583
    introduced_date: 2026-05-13
    owner_adr: ADR-060               # framework SSOT — workflow yml parse 정합의 정책 owner
    carrier_adr: ADR-060             # self-carrier (Amendment 9)
    recurrence:
      count: 6                       # 6 file 동시 actual broken (CFP-583 evidence)
      last_occurrence: "2026-05-13T00:00:00Z"
      threshold: 3                   # ADR-060 §결정 19 (Amendment 6) — advisory promotion signal
      promotion_trigger: advisory    # 6 >= 3 threshold 도달 → PR advisory comment
    status: Active
```

**Hotfix-bypass label 명명**: `hotfix-bypass:workflow-yaml-parse` — ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **11번째 hotfix-bypass:* family member** (기존 10: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions). label-registry-v2 v2.6 same-MINOR sub-entry append 동반 (frontmatter `version` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).

**Promotion criteria** (warning → blocking-on-pr, ADR-060 §결정 6 AND condition):
- (a) pr_cumulative_min: 20 PR 누적 (velocity-normalized — §결정 10)
- (b) failure_threshold: 0 bypass 외 failure (본 carrier PR merge 시점 = 0 발효 시작)
- (c) sibling_dependencies: [] (독립 entry — 6 file 정정 atomic Phase 2 PR scope 안 완결, 외부 carrier 미의존)

승격 평가 책임 = 별도 carrier Story (warning → blocking-on-pr transition 자동 아님, governance 보존 — Amendment 6 §결정 19 정합).

**framework legitimacy 회복**: 본 carrier 가 ADR-060 framework promotion gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 의 measurement 정당성 회복 — 6 affected entry (decision-principle-vocab / adr-sunset-criteria / auto-phase-label / worktree-first-pre-checkout / carrier-bootstrap / handoff-wording) 가 본 PR merge 후 actual PR-time enforce 발효 시작. 회복 전 시점의 measurement (PR 누적 / failure count) 는 broken-baseline 으로 retroactive 분리 (별도 carrier scope, Story §3.4 명시).

### §결정 23 (Amendment 9, CFP-583 — 2026-05-13)

**workflow yml BODY heredoc anti-pattern + 정상 패턴 SSOT** (forcing function for future workflow author + DesignReview lint reference):

GitHub Actions workflow yml 안 `run: |` block scalar 내부에서 multi-line bash `BODY="..."` 변수 assignment 작성 시 다음 패턴이 yaml scanner 의 block scalar 종료 모호성 유발 → ScannerError / jobs:[] silent fail.

#### 금지 (anti-pattern)

```yaml
run: |
  BODY="${HEADER}

  ```                  # ← yaml scanner 가 fence-start line 으로 오해
  ${LINT_OUT}          # ← yaml 가 새 key 시작으로 분류 시도 → ':' 부재 → ScannerError
  ```
  ..."
```

**금지 사유**: yaml block scalar (`|`) 안 모든 line 은 nominal "indented continuation". 그러나 0-indent backtick fence + 0-indent `${...}` 가 continuation interpretation 와 충돌 — PyYAML strict 는 `ScannerError: while scanning a simple key, could not find expected ':'`. GitHub Actions Go parser 는 lenient 하나 `jobs:` block 평가 시점에 silent fail (workflow startup_failure 패턴, jobs:[] empty + run status=failure).

#### 권장 (정상 패턴 2종)

**(A) printf format string + variable arg** (parallel-epic-conflict-check.yml healthy reference line 146-152):

```yaml
run: |
  BODY=$(printf '%s\n\n```\n%s\n```\n\n%s' \
    "$HEADER" "$LINT_OUT" "$FOOTER")
  gh pr comment "$PR_NUMBER" --body "$BODY"
```

**정당화**: printf format string 은 single-quoted (yaml scanner 가 단일 quoted scalar 로 인식, 내부 backtick / `${...}` 가 escape 영역 외). variable arg `"$HEADER"` 는 bash interpolation 영역 (yaml 미접근).

**(B) ANSI-C bash quoting `$'...'` + escape literal newline**:

```yaml
run: |
  BODY=$'## Header\n\n```\n'"$LINT_OUT"$'\n```\n\n'"$FOOTER"
  gh pr comment "$PR_NUMBER" --body "$BODY"
```

**정당화**: `$'...'` 는 ANSI-C quoted string (bash builtin). 내부 `\n` 가 literal newline 으로 escape. yaml scanner 영역에서는 single-quoted scalar 로 인식 — backtick fence 가 quoted scalar 안 포함되어 block scalar 종료 boundary 미접근.

**(C) external script call** (ADR-061 §결정 1 영역 적용 — multi-line > 5줄 시):

```yaml
run: |
  bash scripts/emit-comment-body.sh "$HEADER" "$LINT_OUT" "$FOOTER" > /tmp/body.md
  gh pr comment "$PR_NUMBER" --body-file /tmp/body.md
```

**정당화**: yaml 안에 multi-line bash 자체 부재. external `.sh` 또는 `.py` script 가 모든 escape 책임 흡수. ADR-061 §결정 1 의 yaml-shell 영역 extension (Python script convention 의 self-citation).

#### Lint enforcement

`scripts/check-workflow-yaml-parse.sh` (Phase 2 PR scope) 가 PyYAML safe_load + actionlint dual validation 으로 mechanical enforcement. warning tier 첫 도입 — `continue-on-error: true`. 4-tier promotion path (warning → blocking-on-pr) 는 별도 carrier (ADR-060 §결정 6 AND condition + §결정 19 advisory promotion signal).

#### ADR-061 cross-ref

ADR-061 §결정 1 (Python script-writing convention) 는 multi-line Python > 5줄 외부 .py 의무 + bash heredoc 금지. 본 §결정 23 = 동일 root cause family 의 yaml-shell heredoc 영역 extension (multi-line quoted string 안 backtick / `$` / `\` 가 transmission boundary 마다 다른 escape semantics 적용). ADR-061 신규 Amendment 영역은 별도 carrier — 본 ADR-060 §결정 23 가 워킹플로우 yml 영역 mechanical enforcement carrier (registry entry + script + workflow self-app).

## Amendment 10 (CFP-662, 2026-05-14)

### Amendment 10-결정 24 (신설) — 10번째 warning-tier entry `bootstrap-labels-precondition` 등록

**Carrier**: CFP-662 / Issue #670 / Story file `wrapper/stories/CFP-662.md` (codeforge-internal-docs SSOT).

**Direct trigger**: [RETRO-MCT-104] (#318, 2026-05-09 발생) — mctrader-data PR #14 의 `phase-gate-mergeable` CI check 초회 실행 FAIL. 원인 = mctrader-data repo 에 `phase:보안-테스트` / `gate:security-test-pass` label 부재. SecurityTestPLAgent 가 수동으로 `scripts/bootstrap-labels.sh` 실행 후 통과. PR merge ~20분 지연. 사용자 directive (2026-05-14): "워크플로우 레벨 fix (권장)" 명시.

**Background root cause**: CI gate 자체가 label set 부재를 사전 감지 못함 = root cause. consumer repo 가 codeforge plugin install 후 첫 PR open 시점에 codeforge 필수 label set (`phase:*` / `gate:*` / `type:*` / `hotfix-bypass:*` / `severity:*` / `audit:*` / `component:*`) 가 자동으로 보장되지 않음 — PR-time precondition check pattern 부재 (`templates/github-workflows/*.yml` 52 entry 중 `gh label create` 호출 workflow = `check-plugin-version-bump.yml` 1건만, 별도 axis).

**Entry 필드 SSOT** (registry yaml row 형식, Phase 2 PR append target):

```yaml
  - name: bootstrap-labels-precondition
    description: |
      ADR-060 Amendment 10 mechanical verification — consumer repo PR open 시 codeforge
      필수 label set (phase:* / gate:* / type:* / hotfix-bypass:* / severity:* / audit:* /
      component:*) 부재 자동 감지 + bootstrap-labels.sh idempotent 호출 (RETRO-MCT-104
      carrier, mctrader-data MCT-104 Phase 2 PR #14 2026-05-09 replay sentinel).
      PR-time precondition check pattern 의 첫 baseline (CFP-583 retro 후 framework
      legitimacy 회복 후 신규 entry 도입).
    detect_command: bash scripts/bootstrap-labels.sh   # CFP-662 Phase 2 — workflow body 본문 호출 대상
    workflow: templates/github-workflows/bootstrap-labels.yml   # CFP-662 Phase 2 신설
    current_tier: warning            # ADR-060 §결정 5 — 첫 도입 = warning mode
    bypass_label: hotfix-bypass:bootstrap-labels
    bypass_audit_lint: bash scripts/check-bypass-audit-comment.sh   # 1st-19th entry 동일 패턴
    promotion_criteria:
      pr_cumulative_min: 20          # ADR-060 §결정 6 (a) / §결정 10 velocity-normalized
      failure_threshold: 0           # ADR-060 §결정 6 (b)
      sibling_dependencies: []       # 독립 entry — bootstrap-labels.sh reuse + workflow self-app 외 의존 없음
      evidence_artifacts:
        - github_actions_run_history_url
        - lint_failure_count_zero_proof
        - pr_cumulative_count_proof
    modal_anti_pattern_dictionary: {}  # 본 lint = precondition check, modal phrase 검사 미포함
    introduced_by: CFP-662
    introduced_date: 2026-05-14
    owner_adr: ADR-060               # framework SSOT — PR-time precondition check pattern 의 정책 owner
    carrier_adr: ADR-060             # self-carrier (Amendment 10)
    recurrence:
      count: 1                       # MCT-104 Phase 2 mctrader-data PR #14 (2026-05-09) [empirical-source: spec PR #393 §"동인" + Issue #318]
      threshold: 3                   # ADR-060 §결정 19 (Amendment 6) — advisory promotion signal
      last_occurrence: 2026-05-09    # [empirical-source: mctrader-data PR #14 timestamp]
      promotion_trigger: advisory    # count=1 < threshold=3 → 발화 없음
    status: Active                   # Phase 2 PR carrier merge 후 Active 전환 (workflow self-app 시점)
```

**Hotfix-bypass label 명명**: `hotfix-bypass:bootstrap-labels` — ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **20번째 hotfix-bypass:* family member** (기존 19: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection). label-registry-v2 v2.13 → v2.14 PATCH 동반 (frontmatter `version` bump — schema 무변경 yaml row append, ADR-008 §결정 3 정합).

**Promotion criteria** (warning → blocking-on-pr, ADR-060 §결정 6 AND condition):
- (a) pr_cumulative_min: 20 PR 누적 (velocity-normalized — §결정 10)
- (b) failure_threshold: 0 bypass 외 failure (본 carrier PR merge 시점 = 0 발효 시작)
- (c) sibling_dependencies: [] (독립 entry — bootstrap-labels.sh reuse + workflow self-app + consumer-guide §2h.X 외 의존 없음)

승격 평가 책임 = 별도 carrier Story (warning → blocking-on-pr transition 자동 아님, governance 보존 — Amendment 6 §결정 19 정합).

**PR-time precondition check pattern 의 첫 baseline**: CFP-583 retro 후 framework legitimacy 회복 (workflow yml ScannerError 6 file 정정 완료) 직후 신규 entry 도입. 본 entry 는 기존 warning-tier 9개 entry (adr-sunset / decision-principle-vocab / auto-phase-label / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary) 와 패턴 정합 — `continue-on-error: true` + `hotfix-bypass:*` per-entry namespace + `check-bypass-audit-comment.sh` reuse + ADR-060 §결정 5 default tier.

**ADR-061 §결정 1 외부 script convention pattern reuse**: workflow yml 본문 = `bash ${{ github.workspace }}/scripts/bootstrap-labels.sh` 단일 호출 (CFP-583 BODY heredoc anti-pattern 차단 — multi-line shell embed 회피, yaml scanner 영역 무관). script 자체는 209 line idempotent 3-fallback chain (`gh label create` → `gh label edit` → silent fail) 이미 보유 — workflow 신설 시 script 변경 0건.

**ADR-066 CODEFORGE_CROSS_REPO_PAT primary token 정합**: 90 day rotation lifetime / 최대 180 day. PAT scope min = `public_repo` (public consumer repo) 또는 `repo` (private consumer repo). Fallback = `GITHUB_TOKEN` (silent advisory degradation, PAT 부재 / scope 부족 시).

**Consumer-guide §2h.X 자동 install 절차 명시**: Edge Case #1 (consumer copy 미수행, CRITICAL) 해소 — `regen-agents.sh` no-clobber copy 자동 propagate + 신규 consumer onboarding 시 의무 step + §2c `cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/` glob 보존 (workflow file copy 자동 포함).

**ratchet 위반 0건** — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT permanent governance).

**sibling_dependencies append**: `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506, CFP-509, CFP-508, CFP-530, CFP-583, CFP-662]` (Amendment 2 §결정 6 (c) chain 정합).

**Mermaid 다이어그램 동기화** (Amendment 2 §결정 6 (c) chain 정합): 본 ADR `## 다이어그램` Mermaid 의 carrier chain row 갱신은 추후 다이어그램 갱신 carrier 가 통합 처리 (현재 chain length 11 — CFP-662 까지 보존 의무).

#### Cross-ref

- **RETRO-MCT-104**: #318 (2026-05-09 발생, priority:P2) — 본 Amendment 10 carrier 가 RETRO 해소 (Phase 1 PR open 후 #318 cross-ref comment + close, deduplication).
- **CFP-598**: bootstrap-labels.sh hotfix-bypass:* dynamic read 분기 (label-registry-v2 §3 yaml first-class backfill v2.7) — 본 entry 의 `hotfix-bypass:bootstrap-labels` 20번째 family member 가 dynamic read 분기 자동 흡수 (script 변경 0건, registry yaml row append 만).
- **CFP-474**: 6 mctrader repo prereq-check sweep (CLOSED, 2026-05-09) — 본 Story sentinel test 대상 (mctrader-data PR replay sentinel).
- **CFP-583**: workflow-yaml-parse warning tier 7번째 entry — 본 Amendment 10 이 framework legitimacy 회복 직후 신규 entry 도입 timing 정합 (broken workflow 영역 차단 완료 후 신규 entry 도입).

## Amendment 11 (CFP-442, 2026-05-14)

### Amendment 11-결정 25 (신설) — 5번째 warning-tier entry `evidence-registry-anomaly` 등록 + 메타 anomaly lint scope SSOT

**Carrier**: CFP-442 / Issue #442 / Story file `wrapper/stories/CFP-442.md` (codeforge-internal-docs SSOT, ADR-013 dogfood-out 정합).

**Direct trigger**: Amendment 1 §결정 14 (CFP-390, 2026-05-11) + Amendment 2 §결정 14 (CFP-455, 2026-05-12) 의 후속 carrier 의무 명시 — 메타 anomaly lint (inventory drift detection) 첫 deliver. 본 amendment 가 framework self-application 5-piece chain (CFP-389 declaration + CFP-390 inventory backfill + CFP-455 schema axis + CFP-508 naming convention + **CFP-442 inventory anomaly**) 완성.

**Background root cause**: ADR-060 framework 가 self-evolving SSOT — 신규 evidence-enforceable 패턴 (script + workflow + ADR carrier) 도입 시 registry yaml 등록 누락 = governance drift 위험. Amendment 1 §결정 13 의 manual inventory backfill (CFP-390) 정합 유지 = 반복 CFP 비용 (사용자 §1 verbatim 위험 인식). 본 lint = manual sweep 의 mechanical 대체 (Amendment 1 §결정 14 carrier 의무 deliver).

### 메타 anomaly lint scope SSOT (CFP-442 carrier — Story §1 + Change Plan §3 verbatim)

**sub-check 1** (registry yaml ↔ ADR-060 §결정 13 표 inventory parity):
- 입력: `docs/evidence-checks-registry.yaml` entries[] + `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` Amendment 1 §결정 13 표 Group A 18 entry SSOT
- 검증: 1:1 매핑 (registry 에 표 entry 누락 OR 표 에 registry entry 누락 시 anomaly)
- 예외: `status: Retired` entry skip (EC-6 — `marketplace-sync` retired entry inventory match 면제)
- 출력: violation list (missing entry name + 양방향 분류)

**sub-check 2** (4-criteria static analysis 후보 식별):
- 입력: `scripts/check-*.sh` glob (56 file [verified — CFP-442 §2 CodebaseMapper]) + `.github/workflows/*.yml` glob (51 file) + `templates/github-workflows/*.yml` glob (53 file)
- 4-criteria AND condition (Amendment 1 §결정 13 본문 verbatim):
  - (a) `detect_command` (script 또는 workflow inline)
  - (b) `workflow` GitHub Actions trigger 존재
  - (c) `owner_adr` (proper ADR-NNN) script header 또는 workflow comment 매칭
  - (d) `current_tier` signal (PR/merge 차단/경고 의지 — `continue-on-error` field 추출)
- 4 모두 True 시만 candidate 분류 (LLM judgment 미사용, deterministic — 사용자 §1 verbatim)
- 제외 prefix: bootstrap-/test-/audit-trail-/migrate-/post-merge-/sync-/helper- (Group C — 4-criteria 미충족 ad-hoc utility)
- 제외 path: ALLOWLIST 4-path (self-referential 회피)
- 출력: confirmed candidates (registry 미등록) list

**ALLOWLIST 4-path hardcode — 2-purpose serving** (F-CL-03 FIX iter 2 정정, EC-9 §결정 25 invariant):

ALLOWLIST 4-path 은 **두 목적** serving (multi-purpose semantic 명시 — ADR-068 I-3 guard placement intent 정합):

**(a) candidate 식별 false positive 회피** (3 paths — `collect_script_candidates()` + `collect_workflow_candidates()` exclude 대상):
- `scripts/check-evidence-registry-anomaly.sh` (sub-check 2 `scripts/check-*.sh` glob 매칭 — exclude 의무)
- `templates/github-workflows/evidence-registry-anomaly-check.yml` (sub-check 2 `templates/github-workflows/*.yml` glob 매칭 — exclude 의무)
- `.github/workflows/evidence-registry-anomaly-check.yml` (sub-check 2 `.github/workflows/*.yml` glob 매칭 — exclude 의무)
- ※ `scripts/lib/check_evidence_registry_anomaly.py` = **부적용** (sub-check 2 glob `scripts/check-*.sh` pattern 외 — `scripts/lib/*.py` 미매칭, candidate 후보 아님)

**(b) start-up time existence assertion** (4 paths 전체 — `assert_allowlist_files()` Python helper invoke 직후 검증 대상):
- 위 3 path + `scripts/lib/check_evidence_registry_anomaly.py` (Python helper 본체)
- 4 paths 모두 file 존재 의무 — 1+ 부재 시 exit 2 META-ERROR (drift detection forcing function, EC-9 정합)
- `scripts/lib/*.py` 는 candidate 후보 아니나 deployment 무결성 (Python helper 가 실제 file 로 존재) 검증 의무
- CFP-508 §결정 20 DRIFT allowlist hardcode 패턴 정합

**guard placement intent** (ADR-068 I-3 정합):
- `assert_allowlist_files()` = **unconditional** start-up time guard (Python helper invoke 시점 무조건 실행, sub-check 1/2 진입 전)
- (a) candidate exclude = **conditional** on sub-check 2 진입 path (sub-check 1 inventory parity 영역 외)
- (b) start-up assertion = **unconditional** + 4-path 전체 적용 (candidate exclude 의 3-path 와 별 axis)

**Exit code 3-tier** (Amendment 2 §결정 15 정합):
- `exit 0` = PASS (sub-check 1 mismatch 0 AND sub-check 2 candidate 0)
- `exit 1` = anomaly DETECTED (sub-check 1 OR sub-check 2 violation 1+)
- `exit 2` = META-ERROR — 3 분기:
  - (a) pyyaml 미설치 / Python lib import 실패
  - (b) registry yaml 파싱 실패 (yaml.YAMLError) — 메시지 = `META-ERROR: registry yaml parse failed — <file>:<line>:<col> <msg>`
  - (c) ADR-060 §결정 13 표 parse 실패 — 메시지 = `META-ERROR: ADR-060 §결정 13 inventory table unparseable — <reason: heading-mismatch | table-row-malformed | table-missing> at <anchor>`
  - (d) ALLOWLIST 4-path 부재 (EC-9 drift) — 메시지 = `META-ERROR: ALLOWLIST file 부재 — <path>`

**Entry 필드 SSOT** (registry yaml row 형식, Phase 2 PR append target):

```yaml
  - name: evidence-registry-anomaly
    description: |
      ADR-060 Amendment 11 §결정 25 — 메타 anomaly (inventory) lint.
      sub-check 1: registry yaml entries ↔ ADR-060 §결정 13 표 Group A 18 entry 1:1 inventory parity.
      sub-check 2: scripts/check-*.sh + .github/workflows/*.yml + templates/github-workflows/*.yml
                   4-criteria static analysis 후보 식별 + registry 미등록 감지.
      ALLOWLIST 4-path self-exempt + start-up time assertion (EC-9 정합).
      Exit code 3-tier (Amendment 2 §결정 15 정합).
    detect_command: bash scripts/check-evidence-registry-anomaly.sh
    workflow: templates/github-workflows/evidence-registry-anomaly-check.yml
    current_tier: warning            # ADR-060 §결정 5 — 첫 도입 = warning mode
    # bypass_label: omit             # Amendment 2 §결정 16 — warning tier optional
    promotion_criteria:
      pr_cumulative_min: 20          # ADR-060 §결정 6 (a) / §결정 10 velocity-normalized
      failure_threshold: 0           # ADR-060 §결정 6 (b)
      sibling_dependencies:                  # F-CL-01 FIX iter 2 — self-carrier CFP-442 제외 convention (prior art `evidence-registry-schema-validation` self CFP-455 미포함 + `adr-sunset-criteria` self CFP-389 미포함)
        - CFP-390
        - CFP-412
        - CFP-455
        - CFP-449
        - CFP-481
        - CFP-506
        - CFP-509
        - CFP-508
        - CFP-530
        - CFP-583
        - CFP-662
      evidence_artifacts:
        - github_actions_run_history_url
        - lint_failure_count_zero_proof
        - pr_cumulative_count_proof
    modal_anti_pattern_dictionary: {}  # 본 lint = inventory anomaly, modal phrase 검사 미포함
    introduced_by: CFP-442
    introduced_date: 2026-05-14
    owner_adr: ADR-060               # framework SSOT — inventory anomaly axis 의 정책 owner
    carrier_adr: ADR-060             # self-carrier (Amendment 11)
    recurrence:
      count: 0                       # CFP-442 첫 도입 — historical evidence 0건 (DataMigrationArch F-DM-004 Option A 권장)
      threshold: 3                   # ADR-060 §결정 19 (Amendment 6) — advisory promotion signal
      promotion_trigger: none        # count=0 < threshold=3 → 발화 없음 (Option A)
    status: Active                   # Phase 2 PR carrier merge 후 Active 전환 (workflow self-app 시점)
```

**Hotfix-bypass label 명명**: omit — Amendment 2 §결정 16 (warning tier = bypass_label optional, non-blocking 의미상 bypass 불필요).

**Promotion criteria** (warning → blocking-on-pr, ADR-060 §결정 6 AND condition):
- (a) `pr_cumulative_min: 20` PR 누적 (velocity-normalized — §결정 10)
- (b) `failure_threshold: 0` bypass 외 failure (본 carrier PR merge 시점 = 0 발효 시작)
- (c) `sibling_dependencies: [CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506, CFP-509, CFP-508, CFP-530, CFP-583, CFP-662]` (chain length **11** — Amendment 2 §결정 6 (c) chain 정합, self-carrier CFP-442 제외 — F-CL-01 FIX iter 2)

**sibling_dependencies self-exclusion convention** (F-CL-01 FIX iter 2 명시): self-carrier CFP (본 entry 의 경우 CFP-442) 는 `sibling_dependencies` 에서 제외 — 자기 promotion gate 평가 trigger 가 자기 PR merge tautology 회피. CFP-455 prior art 정합 verified:
- `evidence-registry-schema-validation` (carrier CFP-455) → `sibling_dependencies: []` (empty, self CFP-455 미포함, 주석 "독립 entry — schema validation, 외부 의존 없음")
- `adr-sunset-criteria` (carrier CFP-389) → `sibling_dependencies: [CFP-390, CFP-412, CFP-455]` (self CFP-389 미포함)

승격 평가 책임 = 별도 carrier Story (warning → blocking-on-pr transition 자동 아님, governance 보존 — Amendment 6 §결정 19 정합).

**framework self-application 5-piece chain 완성**: CFP-389 (framework declaration) → CFP-390 (인벤토리 backfill — §결정 13 표 SSOT) → CFP-455 (schema axis self-protection — `evidence-registry-schema-validation` entry) → CFP-508 (entry name ↔ workflow naming convention SSOT — §결정 20) → **CFP-442 (inventory axis self-evolution — 본 amendment)** = framework 가 **self-aware governance** 도달 (Story §6 ResearcherAgent verbatim). 이후 carrier = promotion gate 자동화 / advisory comment 자동 발화 등 별도 영역.

**ADR-061 §결정 1 외부 .py split 정합**: thin bash wrapper (8-10 lines) `scripts/check-evidence-registry-anomaly.sh` + Python helper (~280-380 lines) `scripts/lib/check_evidence_registry_anomaly.py`. CFP-455 prior art (`scripts/check-evidence-registry.sh` 9 lines + `scripts/lib/check_evidence_registry.py` 315 lines) verbatim mirror. heredoc multi-line Python inline anti-pattern 차단 (Windows Git Bash / MSYS2 / WSL 환경 backslash escape inconsistency 회피 — CFP-418 FIX iter 1 evidence).

**ADR-063 §결정 1 atomic invariant 발효**: plugin.json MINOR bump (5.65.0 → 5.66.0) + CHANGELOG.md `## [5.66.0]` entry append + marketplace.json `plugins[name=codeforge]` version + description mirror = 3-file atomic coordination 의무 (ADR-037 — 신규 lint script + workflow runtime 활성화 = governance behavior change MINOR 분류). marketplace sibling PR 선행 merge → wrapper Phase 2 PR merge (ADR-063 §결정 5 ordering). Amendment 1 §결정 9 ArchitectAgent §3.6 proactive self-check declare (review-verdict-v4 v4.5 `marketplace_sync_declared: true`) — 본 Change Plan §3.6 단락이 SSOT.

**DRIFT allowlist 자동 흡수**: CFP-508 §결정 20 entry name ↔ workflow basename naming convention partial match 허용 (Conservative no-rename policy). 본 entry `evidence-registry-anomaly` ↔ workflow basename `evidence-registry-anomaly-check.yml` substring "evidence-registry-anomaly" partial match — 별도 DRIFT allowlist hardcode 불필요 (자연 흡수).

**ratchet 위반 0건** — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 + self-application 의무 deliver (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT permanent governance).

**sibling_dependencies append**: `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481, CFP-506, CFP-509, CFP-508, CFP-530, CFP-583, CFP-662]` (chain length **11**, Amendment 2 §결정 6 (c) chain 정합, self-carrier CFP-442 제외 — F-CL-01 FIX iter 2 정정).

**Mermaid 다이어그램 동기화** (Amendment 2 §결정 6 (c) chain 정합): 본 ADR `## 다이어그램` Mermaid 의 carrier chain row 갱신은 추후 다이어그램 갱신 carrier 가 통합 처리 (현재 chain length **11** — CFP-662 까지 보존 의무, CFP-442 self-exclusion 정합).

#### Cross-ref

- **Amendment 1 §결정 14** (CFP-390 / 2026-05-11): 메타 anomaly lint 후속 carrier 의무 명시 — 본 Amendment 11 이 deliver.
- **Amendment 2 §결정 14** (CFP-455 / 2026-05-12): anomaly vs schema validation 분리 결정 — 본 Amendment 11 = anomaly axis deliver (schema validation = CFP-455 separate).
- **CFP-508 §결정 20** (Amendment 7 / 2026-05-13): entry name ↔ workflow basename partial match 정합. 본 entry 자동 흡수 (별도 hardcode 불필요).
- **CFP-509 Amendment 6 §결정 19**: schema v1.2 recurrence field — 본 entry recurrence `{count: 0, threshold: 3, promotion_trigger: none}` Option A.

## Amendment 12 (CFP-734, 2026-05-15)

### Amendment 12-결정 26 (신설) — KPI history accumulation 메커니즘 선택 결정 규칙 SSOT

**Carrier**: CFP-734 / Issue [mclayer/plugin-codeforge#734](https://github.com/mclayer/plugin-codeforge/issues/734) / Story file `wrapper/stories/CFP-734.md` (codeforge-internal-docs SSOT, ADR-013 dogfood-out 정합).

**Direct trigger**: codeforge 의 KPI snapshot JSON 들이 historical metric 누적을 3 상이 메커니즘으로 처리 중 (origin/main `git show` verify) — (a) `rate-limit-fallback` (CFP-453) = 별도 append-only `docs/kpi/rate-limit-fallback-history.jsonl` + `*.json` 안 `history_file` pointer + `scripts/measure-rate-limit-fallback.sh --history-out` (idempotent month-keyed), (b) `retro-alert-pickup-rate` (CFP-628) = embedded `"history": []` 배열 (`docs/kpi/retro-alert-pickup-rate.json` 내부) + `retro-alert-pickup-kpi.yml` 인라인 jq, (c) `marketplace-drift-rate` (CFP-673) = embedded `"gate_status_history"` 배열 (key 명 상이, `docs/kpi/marketplace-drift-rate.json` 내부). trend tooling 입력 계약이 KPI 마다 달라 일관성·테스트 격리·diff-noise 측면에서 비결정적.

**Background root cause**: 3 메커니즘 자체가 결함이 아니라, "어떤 KPI 가 어떤 패턴을 써야 하는가" 의 **결정 규칙 SSOT 부재** 가 결함이다 (Story §2 C-1). 새 KPI 작성자가 매번 ad-hoc 판단 → drift 영구 누적. 또한 3 메커니즘 중 어느 것도 "왜 이 패턴인가" 의 rationale 이 SSOT 에 명시돼 있지 않음 (Story §2.5 G-1 지식 공백). KPI history 누적은 ADR-060 framework 의 sunset gate 측정 (§결정 6 `N consecutive months` / rolling window 판정) 을 위한 **data-substrate 하위 영역** — 독립 설계 도메인이 아니므로 신규 ADR 가 아닌 본 framework 의 Amendment host 가 구조적으로 정합 (§결정 11 framework permanent SSOT 정합 — KPI history governance = framework 운영의 자연스러운 sub-decision).

#### 26.A — 결정 규칙 (decidable 입력 → pattern 출력)

**규칙 적용 범위 (scope boundary — 본 §결정 26 이 governance 하는 데이터 종류)**:

본 §결정 26 은 **metric-sample history** 만 규율한다 — 즉 *window 단위로 누적되는 KPI metric 측정값* (예: 월별 fallback rate / pickup rate / drift count 의 시계열 누적). 다음 두 데이터 종류는 **명시적으로 scope 외** (별개 semantic, 본 규칙 미적용):

- **gate-transition / lifecycle-status log** — gate 의 상태 전이 기록 (예: `marketplace-drift-rate.json` 의 `gate_status_history` = `{status, transitioned_at, reason, transitioned_by}` 형태의 warming→ready→sunset 상태 전이 audit log). metric 측정값의 시계열 누적이 *아님* (값이 아닌 상태 변화 사건 기록). `last_measured_value` 가 존재하지 않거나 history array 의 entry 가 metric 값이 아닌 상태 전이 record 이면 본 범위 외로 판정한다.
- **이미 별 ADR/contract 가 owner 인 비-KPI 시계열** (예: ADR-RESERVATION append, FIX Ledger row) — 본 framework KPI 도메인 외.

scope 외 데이터에 26.A~26.D 를 적용하지 않는다 (category error 방지 — state-transition-log 에 metric-history 패턴 규칙을 강제하면 잘못된 jsonl-migration verdict 발생). 해당 KPI 에 *metric-sample history* 가 신설되면 그 시점에 26.A 를 새로 적용한다 (26.D marketplace 행 참조).

KPI 의 metric-sample history 누적 패턴 선택은 다음 **결정 가능한 입력 2 변수** 로 deterministic 결정한다 (LLM judgment 미사용 — 두 입력 모두 관측 가능한 SSOT field 에서 기계적으로 도출):

| 입력 변수 | 정의 | 값 | **산정 source-of-truth (deterministic priority)** |
|---|---|---|---|
| `window_shape` | gate 판정에 쓰이는 history window 의 형태 | `rolling-multi-month` (예: 3-month rolling) / `single-fixed-window` (예: 1-month flat) | **(1) `docs/evidence-checks-registry.yaml` 해당 entry `sunset_gate` window 표현** (gate 판정의 실제 SSOT) → (2) 없으면 KPI JSON `window_months` → (3) 그래도 모호하면 26.B E-1. registry window 와 JSON `window_months` 가 불일치 (dual-window) 하면 **registry `sunset_gate` window 가 우선** (E-2) |
| `entry_cardinality` | metric history entry 1건의 구조 + 누적 성장 특성 | `multi-field-or-unbounded` (entry 가 다중 metric field 보유 OR 무한 누적 성장) / `flat-bounded` (단일/소수 field + 유한 소규모) | KPI JSON / jsonl 의 **선언·관측 가능한 entry field** 로 산정 — entry 최대 field 개수 + bounded/unbounded 누적 선언 (registry/json 의 declared schema). 주관적 "성장 가능성" 추정 금지 — 선언된 schema field 와 window 형태에서만 도출 |

**패턴 출력 규칙**:

| `window_shape` | `entry_cardinality` | 선택 패턴 |
|---|---|---|
| `rolling-multi-month` | `multi-field-or-unbounded` | **별도 append-only `docs/kpi/<kpi>-history.jsonl`** (+ snapshot `*.json` 안 `history_file` pointer + measure script `--history-out` idempotent month/window-keyed replace) |
| `rolling-multi-month` | `flat-bounded` | **별도 jsonl** (window_shape 가 rolling = 무한 누적 본질 — jsonl 우선, 26.B tie-break 정합) |
| `single-fixed-window` | `flat-bounded` | **embedded `"history"` 배열** (snapshot `*.json` 내부, 단일 file atomic read, pointer 불요) |
| `single-fixed-window` | `multi-field-or-unbounded` | **별도 jsonl** (entry_cardinality 가 확장/성장 본질 — jsonl 우선, 26.B tie-break 정합) |

규칙 1줄 요약: **`window_shape == rolling-multi-month` OR `entry_cardinality == multi-field-or-unbounded` 이면 별도 jsonl, 둘 다 아니면 (`single-fixed-window` AND `flat-bounded`) embedded `"history"` 배열.**

#### 26.B — Tie-break / fallback (E-1)

규칙 입력만으로 패턴이 자명하지 않은 KPI (예: window 은 1-month 선언이나 entry 가 multi-field rolling 의도 / 두 window 동시 보유) → **모호 시 별도 jsonl 채택**. 근거: jsonl 이 테스트 격리 (snapshot json 과 history file 분리 → 측정 로직 단위 테스트가 history 오염 없음) · 무한 확장성 · diff-noise 최소 (append-only) 측면에서 안전 방향 (ADR-064 §결정 1 best-effort / broad-coverage 정합 — fail-safe 가 격리·확장 우위 패턴).

**E-2 (dual-window KPI — mechanical priority)**: KPI 가 두 window 를 동시에 가지면 (예: JSON `window_months` 와 registry `sunset_gate` window 가 불일치) → 26.A source-of-truth priority 표 verbatim 적용 = **registry `sunset_gate` window 가 deterministic 우선** (display/JSON window 가 아닌 *gate 판정에 실제로 쓰이는 window*). registry `sunset_gate` window 가 rolling-multi-month 이면 `window_shape == rolling-multi-month` → 26.A → jsonl. 이 priority 가 부재하면 D-1 같은 registry/json window 불일치에서 작성자가 임의로 어느 window 를 쓸지 선택 (subjective drift) → 분류표 verdict 가 규칙에서 도출 불가능해진다.

**E-2.1 (dual-window 의 governing-window 자체가 미해소일 때 — 분류 보류 규칙)**: dual-window KPI 인데 registry window ↔ JSON window 불일치가 *아직 정정되지 않은 상태* (즉 어느 표현이 정정 후 최종 governing window 가 될지 별 follow-up CFP 로 위임된 상태) 라면 → 분류표 (26.D) 는 해당 KPI 를 **"분류 보류 (deferred)"** 로 기록하고, **26.B tie-break 의 안전 방향 = 잠정 jsonl** 을 적용하며, **최종 분류는 해당 window-불일치 정정 follow-up CFP (예: OOS-D1) 해소 후 26.A 로 재산정** 한다. 이 경우 분류표가 "정합 무변경" 같은 단정을 절대 발화하지 않는다 (window 불일치가 미해소인데 embedded 정합을 단정하면 곧 E-2 와 모순 + 정정 CFP 를 사실상 pre-judge — 26.E follow-up 경계 위반). 잠정 jsonl 은 *방향 권고* 일 뿐 즉시 마이그레이션 강제가 아니다 (실행은 OOS-migration / 해당 OOS follow-up CFP, data 0건이면 E-4 trivially 정합).

#### 26.C — 통일 history key 명 + grandfather 정책 (AC-2 / E-5)

- **신규 KPI**: embedded 패턴 채택 시 history 배열 key 명 = **`"history"`** 로 강제한다. `gate_status_history` 같은 변종 key 명 신규 도입 금지.
- **기존 entry grandfather**: 본 Amendment 발효 시점 기존 3 KPI 의 현행 key 명은 **grandfather** (즉시 rename 강제 아님). 규칙은 "신규 KPI 부터 적용 + 기존 KPI 는 분류표가 정렬 필요로 판정 시 별 follow-up CFP" 의 적용 시점을 명시한다 (E-5 — 기존 embedded 를 전부 jsonl 강제하면 ADR-064 §결정 5 폭발 → backward-compat 보장).
- **data 0건 trivially 정합 (E-4)**: 규칙 적용 결과가 패턴 변경을 요구해도 history data 가 0건이면 (`history: []` / 0-byte jsonl) "정렬 trivially 정합" 으로 분류 — 불필요한 follow-up CFP 양산 방지.

#### 26.D — 3-KPI 분류표 (AC-3)

> 표의 모든 verdict 는 26.A scope boundary + 26.A 패턴 규칙 + 26.B (E-2 / E-2.1) 에서 *기계적으로 도출* 가능해야 한다 (= 본 SSOT 의 존재 이유). 도출 과정을 verdict 칸에 명시한다.

| KPI | 도입 CFP | 현행 패턴 | 26.A scope | `window_shape` (source-of-truth) | `entry_cardinality` | 규칙 산정 패턴 | 규칙 적용 결과 (도출 경로 명시) |
|---|---|---|---|---|---|---|---|
| `rate-limit-fallback` | CFP-453 | 별도 `*-history.jsonl` + `history_file` pointer (`window_months: 3`) `[verified origin/main]` | **in-scope** (metric-sample history — sonnet_spawn/fallback rate 시계열) | `rolling-multi-month` (registry `rate-limit-fallback-rate` "3 month rolling window" = JSON `window_months: 3` 와 일치, dual-window 아님) | `multi-field-or-unbounded` (sonnet_spawn_total / fallback_count / fallback_rate_percent 등 multi-field, 월 누적 무한) | 별도 jsonl (26.A: rolling-multi-month → jsonl) | **정합 — 무변경**. 도출: in-scope ∧ window_shape=rolling-multi-month → 26.A 1줄규칙 = jsonl = 현행. jsonl precedent 자체 (ADR-057 Amendment 2 owner) |
| `retro-alert-pickup-rate` | CFP-628 | embedded `"history": []` (JSON `window_months: 1`) `[verified origin/main]` | **in-scope** (metric-sample history — pickup rate 시계열, value/numerator/denominator) | **dual-window 미해소** — registry `retro-alert-pickup-rate` `sunset_gate.metric` = "≥ 90% (**3 month rolling window**)" / `description` "3 month window" / `how` "gate_status 3 consecutive months → sunset" `[verified origin/main]` ↔ JSON `window_months: 1`. E-2 priority → governing = registry **rolling-multi-month**. 단 정정 미실행 (OOS-D1 위임) → **E-2.1 발동** | `flat-bounded` (value / numerator / denominator flat) | E-2 엄격 적용 시 rolling-multi-month → jsonl. **단 E-2.1 (governing-window 자체 미해소)** | **분류 보류 (deferred)**. 도출: dual-window ∧ window 불일치 미정정 → E-2.1 → 26.B tie-break **잠정 jsonl** (안전 방향 권고, 즉시 마이그레이션 강제 아님 — 현재 `history: []` 0건 = E-4 trivially 정합). **최종 분류는 OOS-D1 (registry↔JSON window 정정) 해소 후 26.A 재산정**. "정합 무변경" 단정 *불가* (E-2 와 모순 + OOS-D1 pre-judge 회피). key 명은 이미 `"history"` (26.C grandfather 무관) |
| `marketplace-drift-rate` | CFP-673 | embedded `"gate_status_history"` (1 entry: `{status: warming, transitioned_at: 2026-05-15, reason, transitioned_by}`) `[verified origin/main]` | **out-of-scope** — 유일 history array = `gate_status_history` = **gate-transition / lifecycle-status log** semantic (warming→ready→sunset 상태 전이 audit), metric-sample history *아님*; `last_measured_value: null` (누적 metric 측정값 0건) `[verified origin/main]` | N/A (scope 외 — 26.A 미적용) | N/A (scope 외) | **26.A 미적용** (scope boundary) | **26.A scope 외 — 본 규칙 미적용**. `gate_status_history` = gate-transition-log (≠ metric-sample-history). 향후 marketplace-drift 에 *metric-sample history* (예: 월별 `drift_issue_auto_create_count` 시계열) 가 신설되면 그 시점에 26.A 재적용. 현행 `gate_status_history` 의 key 명·표현 semantic 처리 (통일 여부/별 어휘) = **OOS-D2 별 follow-up CFP** (data-bearing 1 entry + ADR-063 atomic invariant + state-transition-log ↔ metric-history semantic 분리 결정 필요). 본 규칙은 marketplace 마이그레이션을 *함의하지 않음* (R-1 — scope 외이므로 jsonl 정렬 verdict 발화 자체가 category error) |

#### 26.E — 본 Amendment 미해소 영역 follow-up CFP 경계 (AC-5 / R-1 / ADR-064 §결정 5)

본 Amendment 는 **결정 규칙 SSOT + 분류표 + 통일 key 정책** 까지만 정의한다. 규칙이 정렬을 요구하는 항목의 **실제 실행은 각 독립 follow-up CFP** (독립 brainstorm + 독립 Story + 독립 PR — ADR-064 §결정 5 CFP-scope-unitary verbatim: "한 CFP 안에서 '경량 → full' 단계 채택 금지. 별개 CFP 분리는 허용"):

- **OOS-D2 (marketplace `gate_status_history` semantic 처리)** = 별 follow-up CFP. **본 §결정 26 scope 외 항목** (26.D marketplace 행 = "26.A 미적용"). OOS-D2 의 역할 = scope 외 데이터를 *어떻게 다룰지* 결정 (본 규칙이 결정하지 않음). 사유 3중 (각 독립적으로 별-CFP 강제): (1) **scope-out semantic** — `gate_status_history` = gate-transition / lifecycle-status log (≠ metric-sample-history); OOS-D2 가 "state-transition-log 를 별 어휘로 둘지 / metric-history 와 통일할지" 를 결정해야 함 (본 규칙은 이 결정을 하지 않음 — 26.A scope boundary), (2) **data-bearing** — origin/main 실측 `gate_status_history` 1 entry 보유 (status `warming`, transitioned 2026-05-15), 0-entry 아님 → 어떤 변경이든 데이터 변환 동반, (3) **ADR-063 atomic invariant 결합** — marketplace-drift 는 ADR-063 owner, schema bump 시 plugin.json/CHANGELOG.md/marketplace.json 3-file atomic coordination 의무. **본 규칙은 marketplace jsonl 마이그레이션을 함의하지 않는다** (scope 외 → R-1: THIS rule ⇒ no marketplace migration). 향후 marketplace-drift 에 metric-sample history 가 신설되면 그때 26.A 가 그 신규 history 에 새로 적용된다 (현행 `gate_status_history` 와 무관).
- **OOS-D1 (retro-alert registry/JSON window 불일치 정정)** = 별 follow-up CFP. **26.D retro-alert 행의 "분류 보류 (deferred)" 를 해소하는 선결 follow-up** — 본 §결정 26 의 분류 자체가 OOS-D1 미해소를 전제로 잠정 verdict (E-2.1) 만 발화하므로, OOS-D1 = 26.D retro-alert 최종 분류의 prerequisite. `docs/evidence-checks-registry.yaml` `retro-alert-pickup-rate` entry `sunset_gate.metric` = "retro-alert-pickup-rate ≥ 90% (3 month rolling window)" + `description` "3 month window" + `how` "gate_status 3 consecutive months = ok → sunset 판정" 인데 `docs/kpi/retro-alert-pickup-rate.json` + `retro-alert-pickup-kpi.yml` 은 `window_months: 1` 하드코딩 `[verified origin/main]`. 26.B E-2 (registry `sunset_gate` window deterministic 우선) 적용 시 governing window = registry **rolling-multi-month** → 26.A = jsonl 방향. 그러나 *어느 표현이 정정 후 SSOT 가 될지* (registry 를 1-month 로 정정 vs JSON/workflow 를 3-month 로 정정) 자체가 미결정 → 26.D 는 E-2.1 로 분류 보류 + 잠정 jsonl 만 기록. 정정 실행이 별 CFP 인 사유: registry `sunset_gate.metric`/`description`/`how` 는 `evidence-check-registry-v1` schema-lint 및 ADR-045 §D-5 owner semantics 와 결합 → gate 판정 window 의미 변경 = owner-ADR-coupled 변경, ADR-064 §결정 5 번들 금지 대상. OOS-D1 해소 후 26.A 로 retro-alert 최종 분류 재산정 (정정 결과가 1-month 로 수렴하면 single-fixed-window×flat-bounded → embedded `"history"` 정합 무변경; 3-month 로 수렴하면 rolling-multi-month → jsonl 정렬 필요 — *둘 다 26.A 에서 도출 가능*).
- **OOS-migration (실제 jsonl 마이그레이션 일반)** = 별 follow-up CFP. 규칙이 어떤 KPI 를 "jsonl 로 가야 한다" 분류해도 그 마이그레이션 실행 (schema bump + measure script + workflow rewrite) 은 본 Amendment scope 외.

**적용 시점**: 본 §결정 26 은 **Amendment 발효 후 신규/변경 KPI 부터 binding** (retroactive 강제 아님). 기존 3 KPI 의 분류표 (26.D) 상태: `rate-limit-fallback` = 현행 추인 (in-scope, 규칙 = 현행 jsonl), `retro-alert-pickup-rate` = **분류 보류** (dual-window 미해소 → E-2.1, 최종 분류는 OOS-D1 선결), `marketplace-drift-rate` = **26.A scope 외** (gate-transition-log, metric-sample-history 아님 → 본 규칙 미적용; semantic 처리 = OOS-D2). 어떤 기존 KPI 도 즉시 마이그레이션을 강제하지 않는다 (jsonl 방향 권고는 실행 follow-up CFP 위임 + data 0건 E-4 trivially 정합).

#### 26.F — 각 패턴 rationale (AC-4 — G-1 지식 공백 retroactive 해소)

| 패턴 | rationale (왜 이 패턴인가) |
|---|---|
| 별도 append-only jsonl | (1) **diff-noise 최소** — 한 줄=한 entry, append 만 → versioned JSON 의 전체 array 재작성 diff 회피. (2) **테스트 격리** — snapshot json (측정 로직 단위 테스트 대상) 과 history file 물리 분리 → 측정 테스트가 history 오염 없음. (3) **무한 확장성** — rolling multi-month 누적이 json 비대화 없이 file rotation/분리 용이. (4) grep/tail/jq stream 친화. 비용: 별도 file·`history_file` pointer·schema_version 동기화. ⇒ rolling/multi-field/unbounded 에서 우월. |
| embedded `"history"` 배열 | (1) **단일 file atomic read** — pointer 불요, snapshot 1회 read 로 history 동시 획득. (2) **단순성** — measure script 가 별도 file lifecycle 관리 불요. 비용: entry 추가마다 전체 json 재작성 → array diff-noise, 무한 누적 시 json 비대화, 측정 로직 테스트가 history array 와 결합. ⇒ single fixed-window·flat·소규모 유한에서 단순성 우월. |

#### 26.G — lane 분류 결과 (W-1 / AC-7 — ADR-054 §결정 1/4 근거)

- **형식 결정**: 신규 ADR 아닌 **ADR-060 Amendment 12** (KPI history 누적 = framework data-substrate 하위, 구조적 종속 — §결정 11 framework permanent SSOT host 정합).
- **lane 분류**: **doc-only fast-path** (ADR-054 §결정 1 표 verbatim — "SSOT 문서 변경 + 기존 ADR Amendment + src/tests 무변경"). 근거: (a) 신규 ADR 미도입 → ADR-054 §결정 4 (신규 ADR = full-lane 강제) **트리거 회피**, (b) src/tests 변경 0건 — 본 Amendment 는 declarative 규칙만 (measure script / workflow / KPI json 무변경), (c) `templates/github-workflows/**` 변경 0건 → ADR-054 §결정 5 (workflow 변경 = full-lane) 트리거 회피.
- **모호성 평가**: ADR-054 §결정 2 (모호 시 full-lane 강제) **미발동** — host 결정이 결정적 (framework 구조적 종속 + Story §6.3 ADR 정합성 점검 + Requirements §4.2 framing 이 ADR-060 Amendment 로 수렴). 신규 standalone ADR 채택은 framework SSOT 파편화 + full-lane 무익 강제로 *덜* 방어 가능한 선택.
- **ADR-RESERVATION**: 신규 ADR 미도입 → ADR-RESERVATION row 신규 append **불요** (Amendment 는 번호 예약 대상 아님). 신규 §결정 번호 = 26 (ADR-060 본문 §결정 1-12 + Amendment §결정 13-25 다음 sequential).

#### 26.H — mechanical enforcement 경계 (ADR-040 Amendment 3 §결정 7.C 정합)

본 §결정 26 = **declarative governance 규칙** (분류 판정·key 명·rationale). 즉시 mechanical enforcement 0건 (lint script / workflow 신설 없음 — doc-only fast-path 정합). 분류표 (26.D) 정합성을 신규/변경 KPI 에 대해 자동 검증하는 evidence-check entry (`kpi-history-pattern-conformance` 후보) 는 **별 follow-up CFP** 의 ADR-060 framework 자연스러운 entry 추가 영역 (본 Amendment scope 외 — ADR-040 Amendment 3 §결정 7.C retroactive 면제 / ADR-060 §결정 5 첫 도입 = warning). 본 Amendment 는 normative ADR-060 의 amendment 이나 신규 mechanical action 무도입 → `mechanical_enforcement_actions[]` 신규 entry append 불요 (기존 framework entry 변경 0건).

#### Cross-ref

- **ADR-054 §결정 1/2/4/5** (CFP-363 / 2026-05-10): doc-only fast-path 분류 — 본 Amendment = Amendment + src/tests/workflow 무변경 → doc-only fast-path. 신규 ADR 회피로 §결정 4 트리거 회피.
- **ADR-064 §결정 5** (CFP-445 / 2026-05-12): CFP-scope-unitary — 26.E follow-up CFP 경계가 verbatim 정합 (마이그레이션 번들 0건).
- **ADR-057 Amendment 2**: rate-limit jsonl extension owner — 26.D rate-limit 행이 jsonl precedent 으로 추인 (무충돌, registry "3 month rolling window" = JSON `window_months: 3` 일치 = dual-window 아님).
- **ADR-045 §D-5** (CFP-628): retro-alert KPI owner — 26.D retro-alert 행은 **추인이 아니라 "분류 보류 (deferred)"**. registry `sunset_gate` window (3-month rolling) ↔ JSON `window_months: 1` 불일치가 dual-window 이므로 E-2.1 발동 → 잠정 jsonl 권고 + 최종 분류는 OOS-D1 (window 불일치 정정, ADR-045 owner 영역 결합) 선결. 본 §결정 26 은 retro-alert 의 embedded 패턴을 추인하지 *않는다* (단정 시 E-2 와 모순).
- **ADR-063** (marketplace atomic invariant): marketplace-drift 결합 — 26.E OOS-D2 별 CFP 권고의 atomic invariant 결합 근거.
- **ADR-013** (dogfood-out): Story file = `mclayer/codeforge-internal-docs:wrapper/stories/CFP-734.md`. 정책 SSOT = `mclayer/plugin-codeforge` 본 ADR.
- **§결정 6 / §결정 11** (본 ADR 본문): sunset gate 측정이 history 누적을 암묵 전제 → KPI history governance = framework 하위 (Amendment host 구조적 정합 / framework permanent SSOT 정합).

## Amendment 13 (CFP-722, 2026-05-16)

### Amendment 13-결정 27 (신설) — 11번째 warning-tier entry `story-section-ownership` 등록 + lane-self-write-boundary mechanical-enforcement layer

**Carrier**: CFP-722 / Issue [mclayer/plugin-codeforge#722](https://github.com/mclayer/plugin-codeforge/issues/722) / Story file `wrapper/stories/CFP-722.md` (codeforge-internal-docs SSOT, ADR-013 dogfood-out 정합) / Change Plan `wrapper/change-plans/CFP-722.md`.

**Direct trigger**: CFP-688 Phase 2 sub-PR (b) 진행 중 (2026-05-15 KST) DeveloperPLAgent 가 Story §8 self-write 시 **destructive rewrite** — PR [mclayer/codeforge-internal-docs#441](https://github.com/mclayer/codeforge-internal-docs/pull/441) (closed-no-merge, additions:216 / deletions:850 / changes:1066). DeveloperPL owner boundary = §8/§8.5 only ([`codeforge:lane-self-write-boundary`](https://github.com/mclayer/plugin-codeforge/blob/main/skills/lane-self-write-boundary/SKILL.md) SSOT) 이나 §1.1/§2/§3/§4/§5/§6/§7/§9/§10 (Orchestrator fix-event-v1 monopoly CFP-32)/§13 (ArchitectPL verdict)/§14 (Orchestrator monopoly ADR-031) destructive 다수 침범. §1 verbatim invariant 만 우연히 보존 (`story-section-1-immutable.yml` 가 §1 만 cover). PR #441 close 후 Orchestrator inline append-only redo (PR #442, MERGED `5940799`)로 복구.

**Background root cause**: `story-section-1-immutable.yml` = §1 verbatim 영역만 mechanical guard. §2-§14 per-lane ownership matrix 위반 = mechanical detection 영역 외. `codeforge:lane-self-write-boundary` skill = normative SSOT (behavioral directive) — **mechanical enforcement layer 부재** 가 진짜 결함이다 (skill 자체 아님). cross-repo internal-docs Story PR 의 per-section diff ownership cross-validate 책임 lane 미지정 (CodeReview lane = plugin-codeforge code PR 영역). per-section ownership governance = evidence-enforceable framework 의 자연스러운 신규 warning-tier entry — 신규 standalone ADR 아닌 ADR-060 Amendment host 가 구조적으로 정합 (§결정 11 framework permanent SSOT 정합 — Amendment 3/4/5/10/11 선례 동형, 모두 신규 warning-tier entry = Amendment 형식).

#### 27.A — 결정 (신규 entry `story-section-ownership` + warning-tier)

`docs/evidence-checks-registry.yaml` 에 신규 entry `story-section-ownership` append (Phase 2 PR scope — schema_version `1.2` 무변경, row-append only). entry schema = 기존 `story-section-9-typed` entry 17-field verbatim 차용 (name / description / detect_command `bash scripts/check-story-section-ownership.sh` / workflow `templates/github-workflows/story-section-ownership-check.yml` / `current_tier: warning` / `bypass_label: hotfix-bypass:story-section-ownership` / `bypass_audit_lint` / `promotion_criteria{pr_cumulative_min:20, failure_threshold:0, sibling_dependencies:[], evidence_artifacts}` / `introduced_by: CFP-722` / `owner_adr: ADR-031` (lane-self-write-boundary ownership semantic source) / `carrier_adr: ADR-060` / `recurrence{count:0, promotion_trigger:none}` / `status`).

**tier = warning (ADR-060 §결정 5 첫 도입)**: `continue-on-error: true` workflow + script `sys.exit(0)` always. 모든 fixture (destructive PR #441 +216/-850 reproduction 포함) exit-code 0 — violations stdout-report only, never block PR.

#### 27.B — mechanical action ↔ §결정 binding (ADR-040 Amendment 3 §결정 7.B Pattern I)

**Mechanical enforcement**: `story-section-ownership` (status: warning) — 본 §결정 27 의 mechanical lint 는 `docs/evidence-checks-registry.yaml` 의 동명 entry SSOT. frontmatter `mechanical_enforcement_actions[]` (ADR-040 Amendment 3 §결정 7.A A안 list[object]) 의 단일 entry 와 binding. Amendment 12 (§결정 26 doc-only, mechanical action 0건) 와 상이 — 본 Amd13 = 신규 lint carrier 이므로 §결정 7.A mandate 적용 (ADR-060 frontmatter 에 `mechanical_enforcement_actions[]` field 신규 추가). detect/workflow/tier 의 entry-level SSOT = registry yaml (frontmatter 중복 보유 금지, ADR-040 §결정 7.A B안 거부 사유 정합).

#### 27.C — ratchet 방향 + sunset_justification (ADR-058 §결정 5)

ADR-058 §결정 5 의 trigger = **`is_transitional: true` ADR 의 amendment** 시 amendment_log `sunset_justification` 명시 의무. ADR-060 = `is_transitional: false` 영구 framework (frontmatter line 7 + §결정 11 permanent SSOT host) → §결정 5 trigger **자체 미해당** (약화/강화 방향 무관 — trigger 는 `is_transitional` 값 기준). 본 Amendment 13 = 강화 방향 (behavioral-directive-only `lane-self-write-boundary` skill → **+mechanical-enforcement-layer** 추가 = detection coverage 확대 ratchet-UP, 약화 0). amendment_log `sunset_justification: null` = 선행 강화-방향 amendment (Amendment 3/4/5/10/11, ADR-040 Amd) 와 정합. **별개 개념 주의**: ADR-064 의 "약화 방향 차단" self-application narrative 은 ADR-064-specific ratchet concept 이며 ADR-058 §결정 5 의 `is_transitional`-based trigger 정의와 분리 (혼합 금지).

#### 27.D — ADR-031 / CFP-32 / ADR-013 cross-ref only (재정의 0건)

본 §결정 27 = 기존 ownership 정책의 mechanical-enforcement layer 추가. 다음은 cross-ref only — ownership semantic 신설/재정의 0건:

- **ADR-031 §결정 1 FROZEN + Amendment 1 (CFP-275)**: §14 Lane Evidence = Orchestrator self-write monopoly. Amendment 1 = Orchestrator-owned delegate subagent 의 §14 write 도 "Orchestrator self-write" 정의 포함 (mechanism-level subagent 경유여도 ownership identity = Orchestrator; lane plugin agent 자체 임의 §14 직접 append 만 금지 — lane plugin spawn ≠ Orchestrator-owned delegate spawn). 본 lint 의 monopoly attribution = 이 정의 검증 (lane-plugin-direct = FAIL / Orchestrator + Orchestrator-owned delegate subagent = PASS).
- **CFP-32 fix-event-v1 Amendment (CFP-275)**: §10 FIX Ledger Orchestrator monopoly (행 삭제·수정·재정렬 금지) — §14 와 동형 delegate-subagent 정의. monopoly INV-DI-2 (ANY base-row mutation = candidate violation) 의 근거.
- **ADR-013 dogfood-out**: codeforge family Story file = `mclayer/codeforge-internal-docs:<plugin>/stories/` — cross-repo 경계 (충돌 아님, dual-deployment scope 정의). SEC-F1 trust-minimal (per-repo self-app, ZERO cross-repo fetch/PAT) 가 이 경계의 보안 invariant.

#### 27.E — blocking-on-pr 승격 target (FUTURE labeled option — STANDARD ship)

본 Amendment = warning-tier 만 ship (ADR-060 §결정 5 framework warning-first 준수). promotion_criteria = ADR-060 §결정 6 **STANDARD threshold** (`pr_cumulative_min: 20` / `failure_threshold: 0`). data-loss severity (PR #441 미검출 merge 시 ~700 LOC upstream lane work 영구 손실 risk) 가 expedited promotion gate 를 정성적으로 정당화하나 — 본 Amendment 는 expedited gate 를 **encode 하지 않는다**. ADR-064 §결정 1 CFP-scope-unitary ("한 CFP 안 '경량 → full' 단계 채택 금지") 정합 — expedited-gate 는 prose/registry comment 의 **FUTURE labeled option** 으로만 기록, 별 follow-up CFP 의 독립 brainstorm + Story + PR 영역. blocking-on-pr 승격 precondition 1 항목: internal-docs CODEOWNERS 부재 (cross-repo bypass-authz path 가 incident-carrier repo 에서 inoperative — warning-tier 동안은 무의미하나 blocking 승격 시 해소 필요).

#### 27.F — lane 분류 (ADR-054 §결정 5)

**full-lane** (doc-only fast-path **부적격**). 근거: 신규 `scripts/check-story-section-ownership.sh` + `scripts/lib/check_story_section_ownership.py` + `templates/github-workflows/story-section-ownership-check.yml` + `.github/workflows/` self-app + `tests/fixtures/` 동반 → ADR-054 §결정 5 (workflow/script 변경 = full-lane) 트리거. Phase 1 PR (doc §1-§7 + Change Plan + 본 ADR Amd13) + Phase 2 PR (script/lib/2 workflow/registry row/skill cross-ref/ownership-yaml/regression entry/fixture). 신규 standalone ADR 미도입 → ADR-RESERVATION row append 불요 (Amendment = 번호 예약 대상 아님, Amendment 12 §26.G 선례 동형). 신규 §결정 번호 = 27 (본문 §결정 1-12 + Amendment §결정 13-26 다음 sequential).

#### Cross-ref

- **ADR-031 §결정 1 + Amendment 1 (CFP-275)** / **CFP-32 fix-event-v1 Amendment (CFP-275)**: §14/§10 monopoly + delegate-subagent ownership 정의 — 본 lint attribution 규칙의 ground truth (cross-ref only, 재정의 0건).
- **ADR-013 (dogfood-out)**: cross-repo Story file 경계 — SEC-F1 trust-minimal per-repo self-app.
- **ADR-005 (byte-identical mirror)**: wrapper template ↔ self-app byte-identity = `sibling-workflow-parity` 자동 강제 (신규 parity check 불요). internal-docs adapted self-app = 의도적 path divergence (`*/stories/*.md`) 만, SHA-pin 양 deployment 동일 (internal-docs 의 unpinned actions = 선재 incidental defect, 답습 금지).
- **ADR-061 §결정 1**: thin-wrapper bash + scripts/lib python SSOT (NO heredoc) — story-section-9-typed precedent 동형.
- **ADR-040 Amendment 3 §결정 7.A/7.B**: frontmatter `mechanical_enforcement_actions[]` + 본문 §결정 27 reference (Pattern I) — Amendment 12 doc-only 면제와 상이 (신규 lint carrier).
- **ADR-058 §결정 5**: `is_transitional` 기준 trigger — `is_transitional: false` 영구 framework 이므로 미해당 + 강화 방향 (ADR-064 self-application 과 별개).
- **ADR-064 §결정 1**: CFP-scope-unitary — 27.E expedited-gate = FUTURE option 만 (경량→full 번들 금지).
- **§결정 5 / §결정 6 / §결정 11** (본 ADR 본문): warning-first / standard promotion threshold / framework permanent SSOT host — 본 Amendment 정합.

## Amendment 14 (CFP-963, 2026-05-19 KST)

### Amendment 14-결정 28 (신설) — 12번째 warning-tier entry `codex-network-scope-presence` 등록 + ADR-081 Amendment 4 §결정 D1.D 본문 확장의 mechanical enforcement layer

**Carrier**: CFP-963 / Issue [mclayer/plugin-codeforge#963](https://github.com/mclayer/plugin-codeforge/issues/963) / Story file `wrapper/stories/CFP-963.md` (codeforge-internal-docs SSOT, ADR-013 dogfood-out 정합) / Change Plan `wrapper/change-plans/cfp-963-codex-network-scope.md`.

**Direct trigger**: ADR-081 Amendment 4 (CFP-963) 가 §결정 D1.D 본문 `sandbox_network_required: <bool>` boolean toggle → `network_scope: <4-tier enum>` strict ratchet-up codify (4-tier: `offline` / `repo-fetch-only` / `web-fetch` / `offline_substitution_declared`). ADR-040 Amendment 3 §결정 7.A self-application 정합 — ADR-081 frontmatter `mechanical_enforcement_actions[]=[]` → list[object] entry `codex-network-scope-presence` 전환 (declaration-only retain 본문 유지 + presence-grep warning lint = 보완 관계 = 상충 0, CFP-722 story-section-ownership / CFP-841 corpus-claim-verify 선례 동형).

**Background root cause**: ADR-081 §D5 declaration-only retain invariant (Amendment 1/2/3 `mechanical_enforcement_actions[]=[]` precedent) 는 boilerplate composition 본문 변경 (mechanical injection layer) 의 robustness risk 회피 목적 — 본문은 declaration-only 유지. 그러나 spawn-prompt 본문 안 `network_scope` field **presence-grep heuristic** 자체 = static doc analysis 영역 (CFP-722 §10 ownership lint / CFP-841 corpus annotation 동형 — declaration ≠ presence verification axis, 보완 관계). framework warning-tier entry `codex-network-scope-presence` 도입 = ADR-081 본문 변경 0건 (D5 SSOT 보존 invariant 정합) + spawn-prompt 작성 시 `network_scope` field 누락 grep-detect = warning advisory (false-positive risk 명시, reviewer responsibility — semantic adequacy 검증 불가).

#### 28.A — 결정 (신규 entry `codex-network-scope-presence` + warning-tier)

`docs/evidence-checks-registry.yaml` 에 신규 entry `codex-network-scope-presence` append (Phase 2 PR scope — schema_version `1.2` → `1.3` MINOR bump 동반, 신규 optional schema field `network_scope_actual` codify §14 Lane Evidence 13번째 optional field carrier). entry schema = 기존 `parallel-work-sentinel-pickup` (CFP-966) / `channel-drift-detection` (CFP-932) / `story-section-ownership` (CFP-722) entry verbatim 차용 (name / description / detect_command `bash scripts/check-codex-network-scope.sh` / workflow `templates/github-workflows/codex-network-scope-presence.yml` / `current_tier: warning` / `bypass_label: hotfix-bypass:codex-sandbox-substitution` / `bypass_audit_lint` / `promotion_criteria{pr_cumulative_min:20, failure_threshold:0, sibling_dependencies:[], evidence_artifacts}` / `introduced_by: CFP-963` / `owner_adr: ADR-081-Amendment-4` (D1.D body 확장 source) / `carrier_adr: ADR-060` / `recurrence{count:0, threshold:3, promotion_trigger:none}` / `status: deferred-followup` (Phase 2 actual lint script + workflow + bats fixture wire 후 `Active`)).

**tier = warning (ADR-060 §결정 5 첫 도입)**: `continue-on-error: true` workflow + script `sys.exit(0)` always. 모든 fixture (CX-963-3 P2 boundary mandate fixture pair `tests/fixtures/codex_spawn_prompt_{with,without}_network_scope.txt` 포함) exit-code 0 — violations stdout-report only, never block PR.

**ADR-068 I-3 unconditional guard placement 정합**: boolean grace 영역 (`sandbox_network_required: <bool>` legacy) = **unconditional advisory** — lint flag gating 없이 무조건 `[legacy-boolean-detected]` PR comment + exit 0. ADR-081 Amendment 4 D1.D.legacy_grace_window 본문 정합.

#### 28.B — mechanical action ↔ §결정 binding (ADR-040 Amendment 3 §결정 7.B Pattern I)

**Mechanical enforcement**: `codex-network-scope-presence` (status: deferred-followup) — 본 §결정 28 의 mechanical lint 는 `docs/evidence-checks-registry.yaml` 의 동명 entry SSOT. ADR-060 frontmatter `mechanical_enforcement_actions[]` (Amendment 13 carrier 동형 — Amendment 14 entry append) + ADR-081 frontmatter `mechanical_enforcement_actions[]` list[object] 양 binding. detect/workflow/tier 의 entry-level SSOT = registry yaml (frontmatter 중복 보유 금지, ADR-040 §결정 7.A B안 거부 사유 정합).

**dual-binding rationale**: ADR-081 Amendment 4 = declaration source (spawn-prompt boilerplate body) / ADR-060 Amendment 14 = enforcement source (framework warning-tier entry). 양 ADR `mechanical_enforcement_actions[]` 안 동일 `action: codex-network-scope-presence` entry 보유 — entry name verbatim binding (ADR-040 §결정 7.A 정합). 동일 mechanical action 이 두 normative ADR 의 declaration source ↔ enforcement source axis 양 면 binding 영역 첫 사례 (parallel-work-sentinel-pickup = ADR-073 single-binding / story-section-ownership = ADR-031 single-binding / channel-drift-detection = ADR-063 + reconcile-protocol-v1 binding precedent).

#### 28.C — entry scope + false-positive risk + self-meta loop avoidance

**Lint scope**:
- Codex worker spawn-prompt 본문 안 `network_scope:` field presence-grep heuristic (4-tier enum value `offline` / `repo-fetch-only` / `web-fetch` / `offline_substitution_declared` membership check OR boolean legacy `sandbox_network_required: <bool>` advisory grace)
- Story §10 `[codex-substitution-scope-declared: <scope-enum>]` / `[codex-sandbox-fallback: <fail-mode>]` marker 의 enum 정합 (membership check 만 — 6-enum fail-mode = `api_missing` / `version_skew` / `enterprise_blocked` / `gh_api_network_blocked` / `manual_substitution_declared` / `inline_orchestrator_verify_only` playbook L1349 정합)
- §14 Lane Evidence row 의 optional `network_scope_actual` field 의 4-tier enum 정합 (field present 시만 검증, omit-on-N/A pattern backward-compat default)

**False-positive risk 명시**:
- 어휘 grep heuristic 한정 (`network_scope:` / `sandbox_network_required:` / `[codex-*]` marker prefix line-anchor)
- **semantic adequacy 검증 불가** — `network_scope: web-fetch` declare 와 실제 spawn-prompt 본문 안 actual `gh api` / cross-repo `git fetch` 호출 사이 의미 정합 검증은 lint 영역 외 (reviewer responsibility)
- 4-tier enum value 의 의미 분류 (예: `offline` 영역에서 spawn-prompt 본문에 실제 web-fetch 호출 명시) = lint 검증 영역 외 (D7.a digest-parse 동형 — semantic precision 불가, FP risk acknowledged)
- boolean legacy ↔ 4-tier enum mapping ambiguity (예: `sandbox_network_required: true` ↔ {repo-fetch-only, web-fetch} 양 mapping 가능) = advisory only (warning tier 정합)

**self-meta loop 회피**: 본 lint workflow 자체의 PR (예: `codex-network-scope-presence.yml` 수정 PR / Phase 2 scripts/check-codex-network-scope.{sh,py} 수정 PR) 에 `hotfix-bypass:codex-sandbox-substitution` 부착 시 본 lint step skip — `scripts/check-bypass-audit-comment.sh` audit lint 의무 (CFP-389 prior art 단일 lint reuse). **carrier_story self-exempt**: 본 entry 도입 carrier (CFP-963) Story file 자체의 Phase 1+2 PR 은 carrier 영역 bootstrap-exempt 정합 (ADR-062 §결정 8 self-application precedent / CFP-722 §결정 27 carrier-Story exemption 동형).

#### 28.D — ADR-081 / ADR-052 / ADR-070 cross-ref only (재정의 0건)

본 §결정 28 = 기존 정책의 mechanical enforcement layer 추가. 다음은 cross-ref only — semantic 신설/재정의 0건:

- **ADR-081 Amendment 4 §결정 D1.D**: `network_scope: <4-tier enum>` body 확장 SSOT. 본 lint 의 검증 대상 declaration source. D5 declaration-only retain invariant + 본 §결정 28 enforcement = 보완 관계 (declaration ≠ presence verification axis, 상충 0).
- **ADR-052 Amendment 8**: substitution path 3-enum cross-matrix SSOT. 본 lint 의 Story §10 `[codex-substitution-scope-declared: *]` marker 검증 = Amendment 8 substitution-scope-declared marker (1회/spawn) 의 presence-grep 측면.
- **ADR-070 Amendment 3 §결정 1 expansion**: substitution scope codify SSOT. 본 lint 의 Story §10 `[codex-sandbox-fallback: <fail-mode>]` marker 검증 = Amendment 3 fail-mode 6-enum membership 측면.
- **playbook §3.10 (CFP-963 graceful degradation step pair sub-section 신설)**: step (a) detect → step (b) declare + verify-before-trust 5 sub-scope full apply → step (c) Story §10 marker + §14 `network_scope_actual` field. 본 lint 의 step (c) Story §10 marker 검증 + §14 field 검증 binding.

#### 28.E — blocking-on-pr 승격 target (FUTURE labeled option — STANDARD ship)

본 Amendment = warning-tier 만 ship (ADR-060 §결정 5 framework warning-first 준수). promotion_criteria = ADR-060 §결정 6 **STANDARD threshold** (`pr_cumulative_min: 20` / `failure_threshold: 0`). codex worker spawn-prompt declaration 부재 → Codex finding evidence ground-truth verify 실패 risk (CFP-946 8-occurrence sentinel re-entry) — 본 entry 가 그 risk 의 mechanical detection layer. 그러나 본 Amendment 는 expedited gate 를 **encode 하지 않는다**. ADR-064 §결정 1 CFP-scope-unitary ("한 CFP 안 '경량 → full' 단계 채택 금지") 정합 — expedited-gate 는 prose/registry comment 의 **FUTURE labeled option** 으로만 기록, 별 follow-up CFP 의 독립 brainstorm + Story + PR 영역.

#### 28.F — lane 분류 (ADR-054 §결정 5)

**full-lane** (doc-only fast-path **부적격**). 근거: 신규 `scripts/check-codex-network-scope.sh` + `scripts/lib/check_codex_network_scope.py` + `templates/github-workflows/codex-network-scope-presence.yml` + `.github/workflows/` self-app + `tests/bats/test_codex_network_scope.bats` + `tests/fixtures/codex_spawn_prompt_{with,without}_network_scope.txt` (CX-963-3 P2 boundary fixture pair mandate) 동반 → ADR-054 §결정 5 (workflow/script 변경 = full-lane) 트리거. Phase 1 PR (3 ADR Amendments + 2 contract MINOR + MANIFEST row catch-up + SSOT doc + Story §1-§7 + Change Plan) + Phase 2 PR (script/lib/2 workflow/registry row/bats/fixture pair/bootstrap parity). 신규 standalone ADR 미도입 → ADR-RESERVATION row append 불요 (Amendment = 번호 예약 대상 아님, Amendment 13 §27.F 선례 동형). 신규 §결정 번호 = 28 (본문 §결정 1-12 + Amendment §결정 13-27 다음 sequential).

#### Cross-ref

- **ADR-081 Amendment 4 §결정 D1.D** + **ADR-081 §D5 declaration-only retain** — 본 entry 의 declaration source + enforcement axis 보완 관계 (상충 0). carrier Amendment 4 frontmatter `mechanical_enforcement_actions[]` list[object] 동일 entry binding (dual-binding pattern 첫 사례).
- **ADR-052 Amendment 8** + **ADR-070 Amendment 3 §결정 1 expansion** — substitution path 3-enum cross-matrix + fail-mode 6-enum playbook L1349 정합 (cross-ref only, 재정의 0건 — CFP-966 lesson "신규 unique drift value 회피" 정합).
- **ADR-024 Amendment 9** (CFP-963 동반) — §결정 6.A per-entry namespace 44번째 family member `hotfix-bypass:codex-sandbox-substitution` (historical-with-template-count convention citation per Codex TP#2 F-CX-963-A P2 calibration — active concrete 42 + CFP-825 template 43 historical = 44 new, Amendment 6 §결정 6.A.2 prior art 정합).
- **ADR-005 (byte-identical mirror)**: wrapper template ↔ self-app byte-identity = `sibling-workflow-parity` 자동 강제 (신규 parity check 불요).
- **ADR-061 §결정 1**: thin-wrapper bash + scripts/lib python SSOT (NO heredoc) — parallel-work-sentinel-pickup / channel-drift-detection / story-section-ownership precedent 동형.
- **ADR-040 Amendment 3 §결정 7.A/7.B**: frontmatter `mechanical_enforcement_actions[]` + 본문 §결정 28 reference (Pattern I) — Amendment 12 doc-only 면제와 상이 (신규 lint carrier).
- **ADR-058 §결정 5**: `is_transitional` 기준 trigger — `is_transitional: false` 영구 framework 이므로 미해당 + 강화 방향 (ADR-064 self-application 과 별개).
- **ADR-064 §결정 1**: CFP-scope-unitary — 28.E expedited-gate = FUTURE option 만 (경량→full 번들 금지).
- **ADR-068 I-3** (unconditional vs conditional guard placement): boolean grace = unconditional advisory (lint flag gating 부재, `[legacy-boolean-detected]` warn + exit 0 무조건) — ADR-081 Amendment 4 D1.D.legacy_grace_window 정합.
- **ADR-068 I-5** (dimensional empirical grounding, Amendment 1): D1.D.legacy_grace_window 의 `pr_cumulative_min: 20` ratchet trigger = ADR-060 §결정 6(b) default precedent-aligned (dimension category: count, units: merged-PR-count-with-enum-only-network-scope-usage, empirical-source: ADR-060 22 entry retroactive verified prior art, conservative ratchet).
- **§결정 5 / §결정 6 / §결정 11** (본 ADR 본문): warning-first / standard promotion threshold / framework permanent SSOT host — 본 Amendment 정합.
- **§결정 19** (Amendment 6 recurrence schema v1.2): 본 entry `recurrence{count:0, threshold:3, promotion_trigger:none}` default — sentinel-driven 도입 아닌 ratchet 확장 carrier (CFP-722 §결정 27 → CFP-966 parallel-work-sentinel-pickup recurrence count=2 sentinel 영역 vs 본 entry count=0 default 영역 분리, parallel-work-sentinel-pickup precedent verbatim 차용 = schema shape 정합).

## Amendment 15 (CFP-1306, 2026-05-25 KST)

### Amendment 15-결정 29 (신설) — 13번째 warning-tier entry `parallel-anchors-checked-presence` 등록 + ADR-068 I-2 review-verdict layer realization Wave 3 mechanical enforcement

**Carrier**: CFP-1306 / Issue [mclayer/plugin-codeforge#1306](https://github.com/mclayer/plugin-codeforge/issues/1306) / Bundle A.A1.

**Direct trigger**: ADR-068 I-2 cross-module propagation completeness 의 review-verdict layer realization — Wave 1 (CFP-1291, CodeReviewPLAgent.md prose anchor) → Wave 2 (CFP-1303, review-verdict-v4 v4.9 `findings[].parallel_anchors_checked[]` optional array field schema codify) → Wave 3 = 본 carrier mechanical lint enforcement. ADR-060 3-tier promotion canonical 사례 (declaration → warning → enforce).

#### 29.A — 결정 (신규 entry `parallel-anchors-checked-presence` + warning-tier)

`docs/evidence-checks-registry.yaml` 에 신규 entry `parallel-anchors-checked-presence` append.

**3-state semantic** (ADR-068 I-2 review-verdict layer realization):
- `absent` → exit 1 (WARNING) — candidate finding (category in 5 pattern_type closed-set) 에 `parallel_anchors_checked` field 누락
- `present + clean` → exit 0 (PASS) — 모든 entry `matched: false` (clean enumeration evidence)
- `present + matched` → exit 0 (PASS) — 1+ entry `matched: true` (parallel anchor found, advisory)

**5 pattern_type enum closed-set** (review-verdict-v4 v4.9 SSOT L55):
`local_remote` / `client_server` / `read_write` / `forward_reverse` / `enum_closure`

**tier = warning (ADR-060 §결정 5 첫 도입)**: `continue-on-error: true` workflow. violations = stdout-report only, PR merge 영향 0.

**AC-13** (DR iter 1): Markdown fenced ` ```yaml ` block extraction before `yaml.safe_load`.
**AC-14** (DR iter 1): non-array `parallel_anchors_checked` (dict/string/null) → WARNING advisory + skip.
**AC-15** (DR iter 1): `pattern_type` lives inside `parallel_anchors_checked[]` items, NOT `findings[].type`.

#### 29.B — mechanical action ↔ §결정 binding

**Mechanical enforcement**: `parallel-anchors-checked-presence` (status: warning, Phase 1+2 동시 wire per CFP-1334 precedent) — `docs/evidence-checks-registry.yaml` 동명 entry SSOT.

**dual-binding**: ADR-068 I-2 = declaration source / ADR-060 Amendment 15 = enforcement source. CFP-963 Amendment 14 dual-binding pattern 답습.

**ADR-061 Amendment 3 (CFP-1497 CodeQL ReDoS guard) 정합**: literal string containment only — no backtracking regex on multi-line content. Line-by-line parse (split on newline, ops on single line).

#### 29.C — TDD stash proof (ADR-082 §결정 11.A, CFP-1334 mandate)

12 TC bats RED→GREEN stash proof:
- RED: `git stash push -- tests/fixtures/cfp-1306/` → bats = 12/12 FAIL (fixture absence)
- GREEN: `git stash pop` → bats = 12/12 PASS

#### 29.D — Cross-ref

- **ADR-068 I-2** — cross-module propagation completeness declaration source. Wave 3 review-verdict layer realization.
- **review-verdict-v4 v4.9** (CFP-1303) — `findings[].parallel_anchors_checked[]` schema carrier.
- **ADR-024 Amendment 14** — §결정 6.A.7 per-entry namespace 90번째 family member `hotfix-bypass:parallel-anchors-checked-presence`.
- **ADR-061 §결정 1** — thin bash wrapper + scripts/lib Python SSOT (NO heredoc). Amendment 3 (CFP-1497 ReDoS guard) 정합.
- **ADR-040 Amendment 3 §결정 7.A/7.B** — frontmatter `mechanical_enforcement_actions[]` + 본문 §결정 29 reference.
- **ADR-058 §결정 5** — `is_transitional: false` 영구 framework trigger 미해당 + 강화 방향.
- **ADR-064 §결정 1** — CFP-scope-unitary (Wave 3 enforcement 단독 carrier).
- **CFP-1291** (Wave 1 prose) + **CFP-1303** (Wave 2 schema) — Wave lineage.

## Amendment 16 (CFP-2061-S1, 2026-06-08 KST)

### Amendment 16-결정 30 (신설) — 14번째 warning-tier entry `increment-justification-presence` 등록 + 검사·ADR·스크립트 순증 PR 정당화 게이트 mechanical enforcement

**Carrier**: CFP-2061-S1 / Issue [mclayer/plugin-codeforge#2062](https://github.com/mclayer/plugin-codeforge/issues/2062) / parent Epic [#2061](https://github.com/mclayer/plugin-codeforge/issues/2061) (de-bloat 거버넌스 영속화) / Phase A.

**Direct trigger**: CLAUDE.md 1.8KB→7.2KB 재증식의 진짜 원인 = ratchet 부재 아닌 "추가마다 실효를 입증할 의무가 없음" (측정 공백). 약화(축소) 방향은 `check-tier-downgrade-guard.sh` 가 `tier-downgrade-justification:` 마커 강제로 차단하나, **순증(추가) 방향은 어떤 게이트도 "실효 정당화"를 강제하지 않음** — `docs/correction-lane.md §범위/비범위` 가 "신규 검사 도입은 promotion 경로를 따른다"고 명시적 공백 선언. ADR-060 promotion_criteria 는 warning→blocking *승격* 시점 절차일 뿐 **검사/ADR/스크립트가 처음 추가되는 시점**의 정당화 의무는 부재. 본 게이트가 그 경계를 메운다.

#### 30.A — 결정 (신규 entry `increment-justification-presence` + warning-tier)

`docs/evidence-checks-registry.yaml` 에 신규 entry `increment-justification-presence` append (Phase 2 PR scope). 검사·ADR·스크립트 신규 추가 PR 의 PR body 정당화 marker 강제.

**trigger-path G1 closed-set** (4-path — false-positive 차단, 신규 도메인 지식 doc 등 무관 파일 미포함):
- (a) `docs/evidence-checks-registry.yaml` entries[] row 신규 append (diff hunk 에 `- name:` 추가)
- (b) `scripts/check-*.{sh,py}` 신규 파일 (diff status=added)
- (c) `(templates|.github)/workflows/*.yml` 신규 파일 (diff status=added)
- (d) `archive/adr/ADR-*.md` 신규 adr_number (Amendment append 제외 — base-ref 에 adr_number 부재 판정)

**G2 marker 형식** (PR body presence-grep — registry field schema 아님):
```
[increment-justification] why=<왜 필요한가> blocks-or-replaces=<무엇을 차단/대체>
```
grep = `^\[increment-justification\]` line-start anchor + `why=` substring + `blocks-or-replaces=` substring (3 AND).

**3-state semantic**:
- trigger-path 0건 → exit 0 (PASS — 게이트 비대상, chore fast-path 자동 충족 / doc-only PR)
- trigger-path 감지 + marker 양 요소 존재 → exit 0 (PASS)
- trigger-path 감지 + marker 부재 또는 요소 누락 → exit 1 (WARNING)
- setup error (gh api auth 실패 등) → exit 2

**tier = warning (ADR-060 §결정 5 첫 도입)**: `continue-on-error: true` workflow. violations = stdout-report only, PR merge 영향 0. branch protection required_status_checks.contexts 미부착. blocking 격상은 ADR-060 §결정 6 승격 gate 별도 트랙 (warning 운영 ≥ 20 PR 후).

#### 30.B — mechanical action ↔ §결정 binding

**Mechanical enforcement**: `increment-justification-presence` (status: warning) — `docs/evidence-checks-registry.yaml` 동명 entry SSOT. Phase 1 = ADR Amd16 frontmatter `mechanical_enforcement_actions[]` entry + 본문 §결정 30, Phase 2 = registry row + script/workflow/bats wire.

**구조 = 두 prior art 결합** (신규 로직 표면 최소화):
- `check-tier-downgrade-guard.sh` — 약화 방향 base-ref(`origin/main`) diff 가드의 **순증 방향 대칭** (base 부재 시 통과 / changed-file 추출 차용)
- `check-bypass-justification-marker` — presence-grep 함수 / exempt 채널 / 3-tier exit / mock env var bats / thin-wrapper bash 구조 차용

신규 순수 로직 ≈ "trigger-path 감지 ∧ marker 부재 → WARNING" 결합부 한 함수.

**핵심 차이점 (우회 시점 vs 추가 시점)**:
| | check-bypass-justification-marker (prior art) | 본 게이트 (신규) |
|---|---|---|
| trigger 시점 | merged PR comment 사후 스캔 | 현재 PR diff trigger-path 감지 후 open-time |
| marker 위치 | top-level PR comment | PR body |
| marker 요소 | 1 (`[bypass-justification]`) | 2 (`why` + `blocks-or-replaces`) |
| 차단 대상 | hotfix-bypass label PR 의 정당화 누락 | 거버넌스 순증 PR 의 정당화 누락 |

**ADR-061 Amendment 3 (CFP-1497 CodeQL ReDoS guard) 정합**: literal string containment only — no backtracking regex. line-by-line parse.

#### 30.C — exempt / self-meta loop 회피

**AC-4 exempt 잠정 경계**: 보안/consumer-whitelist 영역 게이트 예외/완화 = exempt path/tag 잠정 list (security tag entry + consumer-whitelist tag) 만 정의, per-path 판정 (EC-4 — 일반 검사 부분 marker 의무 / 보안 부분만 exempt). **S2 (검사 dead 판정 가드 + security/whitelist tag SSOT) 머지 후 정합 재확인 의무** (OOS1 cross-ref). S2 가 tag SSOT 확정 전이므로 본 게이트 exempt 판정은 잠정 경계 — Story §11 hand-off follow-up row 추적.

**self-meta loop 회피**: 본 entry 부착 PR (Phase 2 자기 carrier) 은 `hotfix-bypass:increment-justification` self-exempt label (admin-only, ADR-024 §결정 7) 또는 carrier_story self-exempt 채널 + 자가적용 marker 이중 부착 (AC-6 dogfood, EC-5). Amendment 14 `codex-network-scope-presence` self-meta loop 회피 선례 답습.

#### 30.D — TDD stash proof (ADR-082 §결정 11.A, CFP-1334 mandate)

10 TC bats RED→GREEN stash proof (Phase 2 scope):
- RED: lint 미구현 (또는 `git stash push -- tests/fixtures/cfp-2061-s1/`) → TC-2 (신규 검사 + marker 부재) = FAIL
- GREEN: 구현 후 (또는 `git stash pop`) → 10/10 PASS
- discriminating core = TC-2 (marker 부재 = WARNING) + TC-6 (Amendment ≠ 신규 adr_number, EC-2)

#### 30.E — Cross-ref

- **§결정 5 / §결정 6 / §결정 11** (본 ADR 본문) — warning-first / standard promotion threshold / framework permanent SSOT host — 본 Amendment 정합 (개별 evidence check entry individual 추가 가능, framework data-substrate 하위 영역).
- **§결정 19** (Amendment 6 recurrence schema v1.2) — 본 entry `recurrence{count:0, threshold:3, promotion_trigger:none}` default (sentinel-driven 도입 아닌 ratchet 확장 carrier).
- **§결정 27** (Amendment 13 story-section-ownership) — behavioral directive (`correction-lane.md` / `lane-self-write-boundary` skill) 의 mechanical-enforcement layer 추가 패턴 동형.
- **ADR-058** — 능동 일몰 시점 정당화의 방향 대칭 (추가 시점 정당화). 능동 일몰 절차 SSOT = S3 별 Story scope. reference-only.
- **ADR-064 §결정 7** — evidence-gated symmetric ratchet 의 강화 방향 self-application 인용 (본 게이트 PR 자체가 정당화 marker 자가적용 = top-down ratchet). reference-only.
- **ADR-024 §결정 7** — `hotfix-bypass:increment-justification` self-exempt label (admin-only) + audit comment 의무. label-registry-v2 family member (Phase 2).
- **ADR-061 §결정 1** — thin bash wrapper + scripts/lib Python SSOT (NO heredoc). Amendment 3 (CFP-1497 ReDoS guard) 정합.
- **ADR-040 Amendment 3 §결정 7.A/7.B** — frontmatter `mechanical_enforcement_actions[]` (Pattern I) + 본문 §결정 30 reference.
- **ADR-005** — sibling-workflow-parity (template ↔ self-app byte-identical, Phase 2).
- **ADR-058 §결정 5** — `is_transitional: false` 영구 framework trigger 미해당 + 강화 방향 amendment.
- **prior art** — `scripts/check-tier-downgrade-guard.sh` (약화 방향 대칭) / `scripts/check-bypass-justification-marker.{py,sh}` (presence-grep/exempt/3-tier) / `templates/github-workflows/bypass-justification-marker.yml` (workflow 양식).

## Amendment 17 (CFP-2061-S4, 2026-06-09 KST)

### Amendment 17-결정 31 (신설) — 15번째 warning-tier entry `governance-drift-detection` 등록 + 거버넌스 지표 주기 재계측 + drift 이슈 자동 발행 cron

#### 31.A — 결정 (신규 entry `governance-drift-detection` + warning-tier)

`docs/evidence-checks-registry.yaml` 에 신규 entry `governance-drift-detection` append (Phase 2 PR scope). 거버넌스 지표 7종 baseline 대비 drift 상대 증가율 임계 초과 시 advisory 이슈 자동 발행.

**7지표 측정 대상**:

| metric | 단위 | 측정 명령 | 임계 |
|---|---|---|---|
| evidence_checks_registry_entries | count | registry yaml entries[] len | +20% |
| workflows_total | count | git ls-files '.github/workflows/*.yml' | +20% |
| workflows_pr_triggered | count | 위 중 pull_request 트리거 | +20% |
| shell_scripts | count | git ls-files 'scripts/' \| grep '.sh$' | +25% |
| shell_loc | lines | shell_scripts 합산 LOC | +25% |
| adr_count | count | git ls-files 'archive/adr/ADR-*.md' | +15% |
| adr_total_bytes | bytes | adr_count 합산 byte | +15% |

**shell_scripts glob 정정 (§4.1)**: `git ls-files 'scripts/' | grep '.sh$'` (top-level + nested 전부). NOT `scripts/**/*.sh` (top-level 누락 — 18배 과소측정).

#### 31.B — dedup signature (D4 — 최대 함정 회피)

```
SIG = sha256("governance-drift|<metric>|increase|<threshold_bucket>") | first 16 chars
```

**current_val 절대 제외** — 포함 시 매일 측정값이 변하면 signature 변동 → dedup 무력화 → 이슈 폭주 (D4 핵심 함정).

답습 원천: `bypass-label-counter.py` L169 `signature = f"{repo}::{label}"` (count 제외) 패턴 직접 답습.

#### 31.C — advisory + prior art 답습

- **advisory exit 0** — drift 감지 + 이슈 발행 후에도 exit 0 (warning tier). setup error 만 exit 2.
- **prior art 답습**: `scripts/check-marketplace-drift.sh` (cron+drift+sha256 dedup+이슈자동+401/429/5xx) + `scripts/check-bypass-label-counter.py` (dedup signature + dry-run + _SKIP_ISSUE_CREATE). 신규 발명 0.
- **cron 시각**: `30 1 * * *` (01:30 UTC = 10:30 KST) — bypass-label-counter(00:00) 시각 분산 (ADR-109).
- **baseline provisional**: `provisional:true` + `rebaseline_owner:CFP-2061-S7` + `captured_at_sha` (D5 — S5/S6 청소 전 잠정).

#### 31.D — TDD bats 19 TC RED->GREEN proof

TC-1 측정 정확성 (discriminating — glob 결함 RED verify) + TC-2 dedup signature (discriminating 핵심 — current_val 포함 naive 시 RED) + TC-3 drift 임계 경계 + TC-4 advisory exit 0 + TC-5 401/429/5xx. hermetic mock.

#### 31.E — Cross-ref

- **§결정 5 / §결정 6 / §결정 11** — warning-first / standard promotion threshold / framework permanent SSOT host.
- **ADR-061** — thin wrapper + scripts/lib Python SSOT (NO heredoc). ADR-005 = template ↔ self-app byte-identical.
- **ADR-066** — CODEFORGE_CROSS_REPO_PAT (issues:write + contents:read).
- **ADR-083** — consumer-applicability: wrapper-self 전용 (self-repo 측정 + self-repo issue create).
- **ADR-109** — rate-limit-429-mitigation: cron 시각 분산 정합.
- **ADR-058 §결정 5** — `is_transitional: false` 영구 framework trigger 미해당 + 강화 방향 (15번째 entry ratchet-UP).
- **prior art** — `scripts/check-marketplace-drift.sh` + `scripts/check-bypass-label-counter.py` + `scripts/lib/gh-api-helpers.sh`.

## Amendment 18 (CFP-2381, 2026-06-20)

### Amendment 18-결정 32 (신설) — 16번째 warning-tier entry `deferred-followup-reconcile` + §결정 19 auto_blocking 라벨의 mechanical forcing function 결합

**Carrier**: CFP-2381 (Epic CFP-2380 S1) / Issue [mclayer/plugin-codeforge#2381](https://github.com/mclayer/plugin-codeforge/issues/2381). Story file = GitHub Issue (wrapper-self Story, ADR-013 dogfood-out 정합).

#### 32.A — 메우는 갭 (forcing function 부재)

§결정 19 (Amendment 6, CFP-509) 가 `recurrence.promotion_trigger: auto_blocking` 을 "별도 carrier Story 가 actual `current_tier: warning → blocking-on-pr` 승격 평가 의무 (자동 transition 아님 — governance 보존)" 로 선언했다 (L1143). 그러나 **그 carrier 발의 자체를 강제하는 mechanical forcing function 이 framework 어디에도 없다.**

- §결정 19 = "auto_blocking 이면 carrier 가 평가해야 한다" 라는 *라벨* 만 부여 — 강제력 0.
- §결정 6 승격 gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling merged) 는 *더 나중* 단계 (carrier 가 이미 존재한다는 전제).
- 결과: "임계 초과 + auto_blocking 선언 + 전용 carrier 부재" entry 가 무경보 적체. 실측 (Story §4):

| entry | count/thr | promotion_trigger | detect_command/workflow 실파일 |
|---|---|---|---|
| `issue-body-claim-pre-screen` | 7/3 | auto_blocking | 둘 다 ABSENT |
| `spawn-prompt-fact-verify` | 3/3 | auto_blocking | 둘 다 ABSENT |
| `stale-local-main-checkout-divergence-check` | 8/3 | auto_blocking | script EXISTS / **workflow ABSENT** (status=Active) |

worktree 정리(CFP-2377) / de-bloat 재증식(CFP-2061-S4) 와 동일 병 — **규정 있고 강제 없음**.

#### 32.B — 검출 기준 결정 (Story 결정점 2 — chief author 판정 = status-agnostic broad criterion)

검출 1급 firing 조건 = **3-AND, status-agnostic**:

```
flag(entry) := (recurrence.count >= recurrence.threshold)
             AND (recurrence.promotion_trigger == "auto_blocking")
             AND (carrier_absent(entry))
```

- **status 필드 무관** — `status: deferred-followup` 뿐 아니라 `status: Active` 로 의도 등록된 `stale-local-main-checkout-divergence-check` (Wave 2 mechanical wire 자체이나 workflow 미배선) 도 포착. forcing function 의 실제 의도 = "강제됐어야 하는데 안 된 것" 전부 (status 라벨이 아닌 *실제 배선 결손* 기준).
- **broad 채택 근거**: narrow (`status == deferred-followup`) 기준이면 stale-local-main (의미상 동일 결함) 을 누락 — `status: Active` 가 "deferred-followup [아님]" 으로 의도 등록됐기 때문 (registry L1973-1974). 그러나 carrier 부재라는 결함은 동일. status 는 "선언만 됐나" lifecycle 라벨일 뿐 carrier 실존을 보장하지 않음.
- **noise 비용 = 0 차단**: warning-tier (continue-on-error) 이므로 broad-scope false positive 가 PR merge 를 차단하지 않음 (advisory only). 강제 신설 0 (ADR-127 ratchet, branch protection 6-tuple 무변경).

**`carrier_absent` 정의** (Story 결정점 1 — detect_command/workflow 파일 실존 변형):

```
carrier_absent(entry) := NOT exists(resolve_path(entry.detect_command))
                      OR NOT exists(resolve_path(entry.workflow))
```

**`detect_command` 경로 추출 spec — 닫힌집합 + fail-loud** (F2 robustness, firsthand registry 다형 실측 반영): registry 의 `detect_command` 는 단일 `bash <path>` 외에도 다형 형태가 실재한다 (firsthand: `bash -c '...diff...yml'` L702 / `A.sh && B.sh` L414 / env-prefix `bash x.sh --repo "${VAR}"` L1850 / `github-actions-runtime` L501 / `workflow inline — ...` prose L183/206/274 / `null` L734/779). 추정 분해는 false-positive/negative 를 유발하므로 **지원 command 형태를 닫힌집합으로 한정 + 닫힌집합 외는 fail-loud (검사 보류, 추정 금지)**:

| 형태 | 처리 |
|---|---|
| `bash <path.sh>` / `python3 <path.py>` / `python <path.py>` (단일 interpreter + 단일 파일 token, optional flag/env-prefix 뒤따름) | 첫 `*.sh`/`*.py` token = resolve 대상 (env-prefix `${VAR}` 인자는 무시 — 경로 token 만) |
| `null` / prose 마커 (`workflow inline — ...` / `github-actions-runtime` 등 파일 경로 아님) | detect_command 축 **검사 제외** (경로 미보유 = carrier_absent 판정 입력 아님 — false-positive 차단) |
| **복합·모호** (`bash -c '...'` / `A && B` 다중 파일 / 위 닫힌집합 미매칭) | **fail-loud** — 해당 entry 를 `UNRESOLVED` 로 분류 + warning 출력 (carrier_absent True/False 단정 금지, 추정 회피). reviewer 가 수동 판정 / 향후 spec 확장 carrier. exit code 는 FLAG 와 동급 warning (continue-on-error 무차단) |

**`workflow` field resolve 규칙 (2-root parity)**: `workflow` 값은 prose 아닌 **verbatim 파일 경로** 로 해석. 값이 `templates/github-workflows/<f>.yml` 이면 ADR-005 byte-parity 의무상 self-app `.github/workflows/<f>.yml` 도 동반 실존해야 하므로 **2-root 둘 다 확인** (둘 중 하나라도 ABSENT = carrier-incomplete). 값이 `.github/workflows/<f>.yml` single-root 이면 그 경로만 확인 (단 §32.E self-entry 는 template-mirror 채택 권고 — Phase 2 결정 §32.E).

- **OR 결합** (AND 아님): detect_command 경로 OR workflow 경로 중 하나라도 ABSENT 면 carrier-incomplete. 근거 = `stale-local-main` 실측 — script EXISTS but workflow ABSENT 인데도 carrier 미완 (검사가 CI 에서 돌지 않음). 둘 다 실존해야 carrier 완결. (현 firing 3건 = 단일-token detect_command 라 UNRESOLVED 미발생 — 닫힌집합 spec 은 향후 다형 entry 대비 + Phase 2 fixture 커버 의무 §8.)
- **deterministic + 외부의존 0 + backfill 0**: GitHub API / PAT / 검색 무의존, CI offline 실행 가능, registry 20+ entry 전수 schema backfill 불요 (데이터에 이미 경로 존재). 2026-06-10 de-bloat (registry `last_updated` log) 가 "detect_command·workflow 가 가리키는 워크플로 부재 = 실행경로 0 거짓 inventory" 로 3 entry 제거한 선례와 동형 신호.

**대안 기각** (Story 결정점 1):
- (a) `wire_carrier:` 필드 신설 = schema 확장 + 기존 20+ entry 전수 backfill 비용 → 기각.
- (b) GitHub Issue 검색 = PAT/API/auth 의존 + 검색어 false-positive → fragile, 기각.

#### 32.C — secondary tier + firing scope 외 (firing 경계 명시)

- **advisory + over-threshold (secondary, informational)**: `promotion_trigger == advisory` AND over-threshold AND carrier-absent = secondary tier 로 별도 보고 (강제 action 3택 미요구 — §결정 19 advisory 의미 "PR comment 만, blocking transition 없음" 보존). 1급 firing (강제) 아님.
- **firing scope 외 (검출 제외)**:
  - `promotion_trigger == warning_tier_initial` (예: `fix-loop-reverify-mandate` count 3/2, `retro-fact-verify-mandate` count 2/2) — auto_blocking / advisory 어느 것도 아님 = "should-be-blocking" 신호 아님 → 검출 대상 아님. (Story §4 표는 이 2건을 "현재 carrier 부재" 사실로 열거하나, *본 게이트의 강제 firing 모집단* 은 auto_blocking 한정 — 이들의 직접 배선은 Epic CFP-2380 S2/S3 담당, §결정 19 의미 정합.)
  - `recurrence.threshold` 미정의 entry — count 비교 불가 → 검출 제외 (false-positive 차단).
  - 본 게이트 self-entry (carrier 실존) — §32.E 자연 PASS.

#### 32.D — 강제 action 3택 (검출 시 warning emit)

flag 된 entry 마다 PR 작성자에게 다음 중 **택일** 강제 (warning emit, blocking 아님):

- **① 배선 carrier (script + workflow) 발의** — `#1602` 5-element 템플릿 자원 사용 (자원-사용 관계, disjoint 아님).
- **② `tier-downgrade-justification:` 근거 강등** — 선례 `scripts/check-tier-downgrade-guard.sh` 마커 패턴 (auto_blocking → none/advisory 로 의도적 강등 + 근거 명시).
- **③ 폐기** — entry 제거 (de-bloat).

출력 형식 = 각 flag entry 의 `(name / count-threshold / promotion_trigger / absent-path[detect_command|workflow])` + 3택 안내 + 본 게이트 = warning mode 1줄 (decision-principle-vocabulary.yml sticky comment 패턴 답습).

#### 32.E — self-application 무한루프 회피 (Story 결정점 3)

본 게이트 self-entry `deferred-followup-reconcile` 는 **처음부터 `status: Active` (current_tier: warning)** 로 등록 + `detect_command` (scripts/check-deferred-followup-reconcile.sh) / `workflow` (deferred-followup-reconcile.yml — root 선택 = §32.H F4 Phase 2 결정에 종속) 실파일을 **동일 Phase 2 PR 에 동반 신설**. 자기 검출 시 `carrier_absent == false` (실파일 실존) → 자연 PASS. 별도 self-skip 분기 불요. (self-entry `workflow` field 값이 어느 root 인지는 §32.B 2-root parity resolve 규칙과 일관돼야 함 — F4 결정 후 확정.)

- 선례: `adr-citation-slug` entry ("자기 진원 RED 0 → status: warning 직접") + Amendment 11 `evidence-registry-anomaly` ALLOWLIST self-exempt.
- recurrence 미부여 (count/threshold 미정의) — self-entry 는 sentinel-driven 아닌 forcing-function carrier 이므로 promotion_trigger 무관 (검출 모집단 제외 이중 안전).

#### 32.F — STALE 2건 status flip (Story 결정점 4 — Phase 2 impl)

firsthand 실측 (file 실존 검증) 기반 2건 `status: deferred-followup` → `Active` flip:

| entry | registry 라인 | detect_command 실파일 | workflow 실파일 | 동반 정리 |
|---|---|---|---|---|
| `bootstrap-labels-precondition` | L965 | `scripts/bootstrap-labels.sh` EXISTS | `templates/+.github/workflows/bootstrap-labels.yml` EXISTS | status 라인만 변경 |
| `schema-change-7-principles-self-check` | L1590 | `scripts/check-schema-7-principles.sh` EXISTS (Python delegate 실구현) | `templates/+.github/workflows/schema-7-principles-check.yml` EXISTS | status flip + **L1591/L1592 `# TBD — S2 carrier wire` stale 주석 2건 제거** |

- flip 방향 = deferred-followup → Active = **강화 방향** (검사가 실제로 도는 상태로). 강등 아님 → `tier-downgrade-justification:` 마커 불요. (Architect §3 = `check-tier-downgrade-guard.sh` 가 flip 을 무단하향으로 오탐하는지 git diff 기준 확인 의무 — Story 결정점 3.)
- schema-7 TBD 주석은 파일 실재이므로 stale → status flip 과 동반 제거 (firsthand 우선 — 파일 실측 > registry 주석).

#### 32.G — schema doc enum drift catch-up (권고)

`docs/inter-plugin-contracts/evidence-check-registry-v1.md` §status field enum (L70) = `Active / Deprecated / Archived` — `deferred-followup` 미등재인데 registry 20건 사용 중 (schema-lint 미검출 drift). 본 게이트의 status-scan 데이터 정합 기반이므로 Phase 1 에서 enum 에 `deferred-followup` 1줄 append 권고 (scope cohesion vs ADR-064 §결정 5 — cohesive 추정, Architect 재량 + DesignReview 확인).

#### 32.H — TDD anti-theater test (self-validation test job — AC-6)

- **discriminating test** = registry fixture (over-threshold-uncarried entry 1+ 포함) → 검출돼야 할 entry 가 검출 안 되면 RED (missing-case) + exit code assert.
- **CI 실행 배선 동반 필수** (AC-6 — 과거 test 스위트 dead PR #2103 재발 차단): bats 별도 러너 신규 배선이 wrapper-self 에 부재하므로, **`operational-outcome-signal-lint.yml` (CFP-2361 PS4) 패턴 답습** — 동일 workflow file 안 2번째 job (`deferred-followup-reconcile-test`) 이 `bash scripts/test-check-deferred-followup-reconcile.sh` 실행 + 회귀 시 exit 1 (continue-on-error 미적용, lint 결함 차단). mutation 생존 0 (검출 로직 1줄 깨뜨리면 RED).
- **[Phase 2 결정 필요] self-validation test-job byte-parity 충돌 해소** (F4): §32.E/I 는 ADR-005 `templates/github-workflows/` ↔ `.github/workflows/` byte-identical mirror 를 요구하나, 답습 대상 `operational-outcome-signal-lint.yml` 은 firsthand 실측상 **`.github/` single-root (template 부재)**. 두 선택지 중 Phase 2 구현 lane 이 택일 — **(택1) wrapper-self test job = `.github/` single-root** (operational-outcome-signal-lint 답습 그대로, ADR-005 byte-parity scope 외 처리 = `invariant-check.yml` `CONSUMER_ONLY_WORKFLOWS` 배열에 `deferred-followup-reconcile.yml` 등록 필요 — firsthand: 동 배열 실재 L47) / **(택2) template mirror 채택 = templates/+.github/ 2-root byte-identical** (ADR-005 정합, consumer 도 게이트 상속 — 단 consumer 의 registry 가 wrapper 형식과 동형이어야 의미, 검토 필요). 본 ADR 은 결정 미선점 (구현 lane scope) — **"Phase 2 결정 필요" 박제** 만 의무. lint 본체 workflow (게이트 자체) 의 root 선택도 동일 결정에 종속 (§32.E self-entry `workflow` 값이 어느 root 인지가 §32.B 2-root parity resolve 와 일관돼야 함).
- 추가 bats (tests/scripts/) 는 보조 — CI 진실 source = self-validation test job.

#### 32.I — Cross-ref

- **§결정 19 (Amendment 6)** — 본 게이트가 mechanical forcing function 을 결합하는 직접 대상 (auto_blocking 라벨 강제력 0 → warning emit 연결).
- **§결정 5 / §결정 6 / §결정 11** — warning-first / standard promotion threshold (carrier 가 평가) / framework permanent SSOT host (self-application sub-decision = Amendment host 구조 정합).
- **ADR-061** — thin wrapper bash + `scripts/lib/check_deferred_followup_reconcile.py` Python SSOT (multi-line Python 외부 .py, NO heredoc). **ADR-005** — `templates/github-workflows/` ↔ `.github/workflows/` byte-identical mirror.
- **ADR-127** — required 신설 0 ratchet (warning-tier, branch protection 6-tuple 무변경). **ADR-054 §결정 4** — 신규 ADR 회피 (Amendment host) = change-plan 면제 (ADR-carrier).
- **ADR-058 §결정 5** — `is_transitional: false` 영구 framework trigger 미해당 + 강화 방향 (16번째 entry ratchet-UP).
- **disjoint** (Story §8 중복 0): #1600/#1687 (current_tier 축 승격) + #2166 (신규 entry 도입) 와 disjoint — 본 게이트 = status 축 (carrier-부재 검출). #1602 = 자원-사용 (① 배선 강제 시 5-element 템플릿).
- **prior art** (worktree 실존 확인 — ADR-119): `scripts/lib/check_governance_drift.py` (registry/거버넌스 지표 PyYAML 파싱 + dedup signature + advisory exit + bash thin wrapper) = registry-class lint 살아있는 등가물 (구 `check_evidence_registry_anomaly.py` 는 2026-06-10 de-bloat 제거됨 — 인용 금지) + `scripts/check-increment-justification.sh` (trigger-path 감지 ∧ marker 부재 → WARNING presence-grep) + `operational-outcome-signal-lint.yml` (self-validation test job in-workflow).

## Amendment 19 (CFP-2426, 2026-06-26 KST)

### Amendment 19-결정 33 (신설) — 17번째 warning-tier entry `lane-count-ssot-consistency` 등록 + canonical lane 수(10) SSOT mechanical consistency enforcement

**Carrier**: CFP-2426 (CFP-2376 retro follow-up) / Issue [mclayer/plugin-codeforge#2426](https://github.com/mclayer/plugin-codeforge/issues/2426). Story file = `mclayer/codeforge-internal-docs` `wrapper/stories/CFP-2426.md` (wrapper-self Story, ADR-013 dogfood-out 정합).

#### 33.A — 메우는 갭 (registration 완료 ≠ enforcement 실효)

ADR-125 Amendment 1 (CFP-2341) 이 canonical lane 수=10 을 정본 SSOT 로 박았으나(registration), 분산 governance 문서 사본이 그 사실에 단조 유지되도록 강제하는 **mechanical enforcement 가 부재**했다. 그 결과 stale `N 레인`/`N번째 lane`(N≠10) drift 가 **2 Story 연속(CFP-2341 → CFP-2376) leak**. 두 선행 Story 모두 manual text-fix 만 수행(lint 0) → enforcement layer 부재가 leak 의 구조적 원인.

- "registration 완료 ≠ enforcement 실효" 전형 — story-section-ownership (§결정 27) / governance-drift (§결정 31) 와 동일 병 (규정 있고 강제 없음).
- canonical=10 invariant SSOT = ADR-125 Amendment 1 (lint 의 ground-truth). lane count(10) ≠ lane *plugin* count(8, ADR-023) — disjoint 축.

#### 33.B — 검출 1급 firing 조건 + exit semantics

```
flag(line) := stale_token_match(line) AND NOT allowlist_match(line)
```

- **detect 정규식** (§7.B2): `(?<![0-9])([6-9])\s*레인` / `레인\s*([5-9])개` / `([6-9])번째\s*lane`. N 범위 = **{5,6,7,8,9}** (canonical=10 외 현 surface 실측 등장 정수).
- **검사 경로**: `docs/**` · `CLAUDE.md` · `plugins/**` · `scripts/**` · `templates/**` · `.claude-plugin/plugin.json`. **제외**(축④): `archive/adr/**` · `docs/cross-repo-patches/**`.
- **필터 순서**: stale 매칭 **이후** allowlist 필터 (역전 시 부정문 STALE 오검출).
- **exit 3-tier** (§결정 15): 0=PASS(FLAG 0) / 1=FLAG 1+(`::warning::check-lane-count-ssot: FLAG ...` emit, continue-on-error 비차단) / 2=SETUP(검사 경로 부재 / python3 미설치 / read 실패).
- **ReDoS-safe** (ADR-061 Amd3): line-by-line scan (multi-line backtracking regex **0**) + anchored bounded-quantifier (nested quantifier 0).
- **N-range = canonical-10 특정값 detection** (documented-limitation): 미래 lane 증감 ADR-125 Amendment 가 N-range 정규식 갱신(+ self-test fixture range 확장)을 그 Amendment 의 **REQUIRED mechanical-sync 항**으로 포함해야 한다 (`11 레인` 류 silent 미검출 방지). 구조 재설계 불요 — 범위 갱신만.

#### 33.C — allowlist 5축 (load-bearing — channel-split)

면제 단위 = **syntactic channel(line-prefix key)** 또는 **counterfactual 마커**, 토큰 자체 아님.

| 축 | 면제 대상 | over-broad 금지 |
|---|---|---|
| **①within-line 이중토큰** | `N lane plugin` (plugin-count 별 축, ADR-023) | 라인 전체 면제 금지 — 같은 라인 `plugin` 미인접 잔여 stale 은 RED (dual-token masking 후 잔여 재검사) |
| **②negation** | `N번째 lane 이 아니다` (부정 토큰 인접) | 부정 토큰 동일 라인 인접 — multi-line 부정 한계 |
| **③history** | date행(③-a) / amendment_log span(③-b) / source_section·주석 인용(③-c) / 버전이력 표 ·숫자전이 N→M(③-d) / 토큰-인접 이벤트동사(§7.B5) | span 무한확장 금지 — sibling live `description:` 까지 silent 면제 = AC-8 false-negative |
| **④path** | `archive/adr/**` · `docs/cross-repo-patches/**` | — |
| **⑤counterfactual** | `만약 ... N번째 lane 으로 신설하면 ... 충돌` 가정 조건절 | `만약` 마커 부재 단독 `N 레인`/`N번째 lane` = RED 유지 (가정 마커 없는 현재-상태 단언은 면제 아님) |

**same-file channel-split (AC-8 핵심 hazard)**: 동일 파일 안 live `description:`/`section:` 값 = **검출** vs `date:`/`source_section:`/amendment_log span = **면제**. amendment_log span = **line-local boolean toggle**(enter=`amendment_log:`/`changelog:` 헤더 key 또는 `- amendment:` 선두 / exit=dedent·sibling 비-amendment list item(`- name:`)·다음 top-level key), multi-line backtracking regex 0 (ReDoS-safe). span 무한확장 시 sibling live `description:` STALE 까지 silent 면제 = false-negative → F-CHANNEL-1 multi-line block fixture + Mutation-3 kill 로 구조적 보장.

#### 33.D — self-application (무한루프 회피)

본 게이트 self-entry `lane-count-ssot-consistency` 는 처음부터 `status: Active` (current_tier: warning) 등록 + `detect_command`(scripts/check-lane-count-ssot.sh) / `workflow`(.github/workflows/lane-count-ssot.yml) 실파일을 **동일 Phase 2 PR 에 동반 신설** → 자기 검출 시 carrier 실존 자연 PASS. self-entry description 자체에 count 토큰(N≠10) 미포함 의무 (자기 검출 회피 — count 토큰 인용 시 `N`(letter) placeholder 또는 negation/history 채널만). 선례 = Amendment 18 §32.E (deferred-followup-reconcile self-entry) / Amendment 11 evidence-registry-anomaly ALLOWLIST self-exempt. self-source 파일(`scripts/lib/check_lane_count_ssot.py` 등)은 SELF_EXCLUDE_PATHS 로 scan 제외 (검출 토큰 예시 보유 — 자기 검출 회피).

#### 33.E — pattern_count=2 정당화

2 Story 연속(CFP-2341 → CFP-2376) leak = manual 정정의 구조적 한계 입증. ADR-060 승급 임계치(재발 ≥3)는 **advisory**(hard-invariant 아님)이므로 PMO authority 재평가로 pattern_count=2 에서 warning-tier *도입* 정당 (충돌 아님 — §결정 19 promotion gate 는 warning→blocking 승격용이지 warning *도입* 임계치 아님; warning 첫 도입은 §결정 5).

#### 33.F — TDD anti-theater test (AC-7 / CFP-1334)

self-test job(`scripts/test-check-lane-count-ssot.sh`) — 22 fixture(F-DET ×4 / F-HIST ×5 / F-DUAL ×2 / F-NEG / F-COUNTERFACTUAL ×2 / F-TRANS ×2 / F-CHANNEL ×2 / F-BORDER / F-EXIT ×3) + 4 mutation 양방향 생존 0:
- **Mutation-1**: detect 정규식 제거 → F-DET RED (stale 미검출).
- **Mutation-2**: allowlist OR → false 상수화 → F-HIST/NEG/COUNTERFACTUAL/DUAL RED (과검출).
- **Mutation-3**: amendment_log span exit 미감지(무한확장) → F-CHANNEL-1 RED (sibling live `description:` STALE silent 면제 = false-negative).
- **Mutation-4**: 축⑤ counterfactual over-broaden(`만약` anchor 제거 → 일반 lane-count 면제) → F-COUNTERFACTUAL-NEG RED (단독 `9 레인` silent 면제).

content-anchor fixture (line# 하드코딩 0 — 요구사항리뷰 R1 교훈). CI 실행 = `.github/workflows/lane-count-ssot.yml` job 2 (`lane-count-ssot-test`, continue-on-error 없음 — 회귀 차단).

#### 33.G — standalone ADR-132 기각 + Cross-ref

- **standalone ADR-132 기각** (비용>이득): warning-tier lint entry 17종 전부 standalone ADR 0, 전부 ADR-060 Amendment. ADR-132 번호 free(ADR-130·ADR-131 실재)이나 신규 ADR = framework 재발명 비용 + 선례 일관성 파괴. focused warning-tier lint = ADR-060 framework 의 자연스러운 17번째 entry. ADR-127 ratchet 정합 (required 신설 0 / branch protection 6-tuple 무변경 / process-skip 채널 0).
- **ADR-125 Amendment 1** — enforce 대상 ground-truth (canonical lane 수=10 정본 SSOT). 충돌 아님.
- **ADR-061** — thin wrapper bash + `scripts/lib/check_lane_count_ssot.py` Python SSOT (NO heredoc). ReDoS-safe(Amd3 line-by-line). **ADR-104** — negation(축②) + counterfactual(축⑤) carrier (operational-phase). **ADR-023** — lane *plugin* count(8) disjoint 축 (allowlist 축① 도메인 근거).
- **ADR-037 (d)** — 신규 governance lint runtime 활성화 = governance behavior → MINOR (6.38.0 → 6.40.0; 6.39.0 = CFP-2428 #2430 병렬 세션 선점 → skip). **ADR-063** — plugin.json `description` tagline `8 레인`→`10 레인` = description-touching → marketplace sync PR 선행 merge.
- **ADR-054 §결정 4** — 신규 ADR 회피 (Amendment host) = change-plan 면제 (ADR-carrier). **ADR-130 §결정 158** — path-filter `on.paths` skip 금지 (선례 일관성, deferred-followup-reconcile 동형 .github single-root).
- **prior art** (worktree 실존 확인 — ADR-119): `scripts/lib/check_issue_body_claim_pre_screen.py` (line-by-line in_fence boolean toggle masking — span toggle 선례) + `scripts/lib/check_governance_drift.py` (git ls-files path walk + `::warning::` advisory exit) + `scripts/check-deferred-followup-reconcile.sh` (ADR-061 thin wrapper).

## Amendment 20 (CFP-2591, 2026-07-10 KST)

**Carrier**: CFP-2591 (Epic — deferred-followup forcing-function 봉합) / Story file = `mclayer/codeforge-internal-docs` `wrapper/stories/CFP-2591.md` (wrapper-self Story, ADR-013 dogfood-out 정합).

deferred-followup forcing function 의 최종 봉합. §결정 32 (Amendment 18) 가 registry entry 의 carrier-부재를 검출하나, (a) enforce 실효(surfacing) + (b) registry **밖** declaration surface 의 미해결 placeholder carrier(no-TBD) + (iv)~(vi) carrier trio 3 갭이 잔존했다. 본 Amendment 20 이 이를 §7.9 로 봉합한다.

### ★ NO-FLIP 불변식 (Stage 경계 명시)

본 CFP-2591 PR = **Stage 1+2 (baseline + new-only shadow)** 이지 Stage 3(flip) 아님.

- `.github/workflows/deferred-followup-reconcile.yml` 의 lint step `continue-on-error: true` **유지** (제거 = flip 금지).
- self-entry `deferred-followup-reconcile` + (b) entry `deferral-carrier-declared` 의 `current_tier: warning` **유지** (blocking-on-pr 승격 금지).
- 실제 continue-on-error 제거(flip → blocking-on-pr surfacing) + tier 승격 = **baseline main 착지 후 별 후속 PR** (§7.2.2 self-deadlock 회피). Tier 2(hard-required, 6-tuple 편입) = FUTURE/OOS.

### §7.9.A — (a) §결정 32.D 개정 (surfacing tier 도입)

§결정 32.D 의 강제 action 은 종전 "warning emit, blocking 아님" 이었다. Amendment 20 이 `blocking-on-pr (surfacing)` tier(**Tier 1**)를 도입 — continue-on-error 제거로 red-X + sticky comment 표면화, 단 required 6-tuple 미편입. **단 본 CFP-2591 PR 은 Stage 1+2 까지만 ship — 실제 continue-on-error 제거(flip)는 baseline main 착지 후 별 후속 PR** (§7.2.2 self-deadlock 회피: baseline 을 도입하는 PR 자신이 blocking 이면 baseline 부재 상태에서 전 PR self-block). Tier 2(hard-required) = FUTURE/OOS.

### §7.9.B — §결정 3 reconciliation (F-3, 필수)

§결정 3 tier-table 이 `blocking-on-pr` 을 "required check·`required_status_checks.contexts` 부착"으로 정의 → surfacing(비-required) 의미와 상충. Amendment 20 이 **`surfacing` qualifier 도입**:

- `current_tier: blocking-on-pr` 자체는 6-tuple/contexts membership 을 **함의하지 않는다**. surfacing sub-mode = **continue-on-error 제거만 · contexts 무변경**.
- 실측 drift 정합: `worktree-first-pre-checkout` 계열 3 entry 가 `blocking-on-pr` ∧ `required_status_checks.contexts` 미부착 상태로 이미 실재 → surfacing qualifier 가 이 실측을 소급 정합화 (Amendment 1 FIND-4 "manifest 부착 entry 만 blocking 분류" 와 정합 — 부착 없이 blocking-on-pr 표기 가능한 surfacing sub-mode).

### §7.9.C — §결정 6 harmonization (baseline-relative failure=0)

§결정 6 (b) `failure_threshold = 0` 을 **baseline-relative(new-debt failure=0)** 로 재해석 — baseline 에 grandfather 된 pre-existing debt 는 failure 미카운트, baseline 이후 신규 유입만 failure 로 집계. Clean-as-You-Code ↔ §결정 5 warning-first 조화 (기존 debt 로 인한 전면 red 회피 + 신규 debt 즉시 표면화).

### §7.9.D — grandfather baseline 메커니즘 (framework-wide 신규 §결정)

`docs/deferred-followup-baseline.yaml` = enumerated-freeze baseline. 속성:

- **enumerated-freeze**: gate_flags + declaration_surfaces 를 승격 시점 snapshot 으로 열거 동결 (locator + token + reason).
- **2-owner section**: gate_flags(registry gate 축) + declaration_surfaces((b) lint 축) 두 소유 섹션 분리.
- **single-writer gen tool**: `scripts/gen-deferred-followup-baseline.sh` 만 write (손 편집 금지 — DO NOT EDIT BY HAND). CI 는 gen 미호출(regen-and-diff-zero 게이트 신설 금지 — provenance drift 회피).
- **content_digest tamper-evident**: sha256 over canonical `{gate_flags, declaration_surfaces}` (provenance/generated_at 제외) — 손 편집 tamper 검출.
- **monotonic shrink**: baseline 은 축소만(정리 시 subtract) — 증식 금지 ratchet.

이론적 근거 = SonarQube **Clean-as-You-Code**(new-only) + betterer ratchet. 신규 debt 만 gate, legacy debt 는 별 backward-triage carrier(예: confluence-ia-tree TBD 2건 → #2097).

### §7.9.E — (b) carrier-mandate entry (no-TBD lint)

deferral 선언 시 carrier CFP + registry 등재를 **필수화**. registry **밖** declaration surface(문서/워크플로/스킬 안 placeholder carrier)에서 미해결 placeholder(미확정 TBD 마커 / 미발급 CFP 번호 / 미배선 FU 마커)를 grep-기반 mechanical 검출 + registry cross-check(named carrier level-1 membership) + 5축 allowlist false-positive 차단 + baseline grandfather(new-only). **declared→registered 강제 결합**(§2.3 forced-coupling) — 선언만 하고 미등재/미명명인 silent debt 차단.

- (a) registry FLAG 는 sibling `deferred-followup-reconcile` 소관, (b) 는 registry 밖 surface 소관 — 두 축 **disjoint**.
- entry = `deferral-carrier-declared` (18번째 warning-tier entry). detect = `scripts/lib/check_deferral_carrier_declared.py` + thin wrapper + `.github/workflows/deferral-carrier-declared.yml` + QADev discriminating test.
- bypass_label **미신설**(D9 — attack surface 최소화, advisory 게이트라 escape valve 불요).

### §7.9.F — §결정 6 carrier trio (self-entry evidence_artifacts 3종)

self-entry `deferred-followup-reconcile` 에 §결정 6 carrier 3종 evidence_artifacts 배선:

- **(iv) outage runbook**: `docs/runbooks/deferred-followup-reconcile-enforce-outage.md` (외부의존 열거 + surfacing outage 처리 + manual fallback 3-step + self-block 회복 sequence + honest ceiling).
- **(v) author-verify lint**: hotfix-bypass audit comment 이 `github-actions[bot]` authored 인지 검증(`scripts/check-audit-comment-author.sh`) — presence-only spoof gap 봉합. 워크플로 배선 = warning mode(검증 FAIL → echo 경고만·비차단, Stage 1+2).
- **(vi) sticky comment at-most-once**: hidden marker find-then-upsert(plain append 금지) — ID-2 idempotency.

### §7.9.G — ADR-127/ADR-024 amendment 불요 + honest ceiling

- **ADR-127/ADR-024 amendment 불요**: Tier 1 surfacing 이 required 6-tuple 을 회피 → ADR-127 §9.1 required-check SSOT 무변경 + ADR-024 §9.4 bypass invariant 미발화 (surfacing = required 아님이라 bypass channel 의무 미발동).
- **honest forcing ceiling**: 게이트는 hard block 을 **미주장**한다 — admin 우회는 구조적으로 가능(surfacing 은 required 아님, admin merge 경로 open). 우회는 감사(audit comment) + AC-20 count(#4)로 **관측만** (mechanical 차단 아님).

### §7.9.H — Cross-ref

- **§결정 32 (Amendment 18)** — 본 Amendment 20 이 개정하는 forcing function 원 정의(§32.D surfacing tier 개정 대상).
- **§결정 3 / §결정 5 / §결정 6** — surfacing qualifier reconciliation / warning-first / promotion gate(baseline-relative harmonization).
- **ADR-061** — thin wrapper bash + `scripts/lib/check_deferral_carrier_declared.py` Python SSOT (ReDoS-safe line-by-line). **ADR-127** — required 신설 0 ratchet (Tier 1 surfacing = branch protection 6-tuple 무변경). **ADR-024** — bypass channel(surfacing 미발동).
- **ADR-063** — plugin.json 6.71.0 → 6.72.0 MINOR (governance behavior — 신규 warning-tier lint runtime 활성화). marketplace.json cross-repo sync = 별 follow-up declare.
- **ADR-058 §결정 5** — is_transitional:false 영구 framework trigger 미해당 + 강화 방향(18번째 entry ratchet-UP + surfacing sub-mode append).
- **prior art** (worktree 실존 확인 — ADR-119): `scripts/lib/check_lane_count_ssot.py` (line-by-line scan + git ls-files walk + 5축 allowlist + SELF_EXCLUDE + ReDoS-safe + exit 3-tier — verbatim copy-inherit) + `scripts/lib/check_deferred_followup_reconcile.py` (carrier-resolution triplet + baseline loader/digest) + `worktree-first-pre-checkout.yml` (audit comment scaffold + sticky comment 패턴 — blocking mode 를 surfacing/warning non-blocking 으로 적용).

## Amendment 21 (CFP-2678, 2026-07-14 KST)

**Carrier**: CFP-2678 (wrapper-self Story) / Story file = `mclayer/codeforge-internal-docs` `wrapper/stories/CFP-2678.md`.

### §결정 34 (신설) — 그룹 C consumer-only bullet: 사본 enumeration → SSOT 참조 단일화 (dual-maintenance drift 원천 제거)

**배경**: 그룹 C(§Amendment 1-결정 13, L1473~) 의 `consumer-only workflow:` bullet 은 `CONSUMER_ONLY_WORKFLOWS`(SSOT, `.github/workflows/invariant-check.yml`)의 **사본 산문 enumeration** 을 보유했다. 이 산문 mirror 는 **CFP-390 Amendment 1 시점의 point-in-time snapshot(13-entry)** 이라 이후 SSOT 확장분을 미반영한 채 historical(고정 snapshot)↔live(SSOT) lag 를 축적했다 — SSOT 확장 4회(CFP-2227 consumer-deploy-seed/post-deploy-smoke · CFP-2360 post-deploy-benchmark · CFP-2369 duplication-check · CFP-2521 pl-delegation-ratio-check)마다 이 산문 mirror 가 미동기화 → drift 4회 반복 (SSOT 18 vs mirror 13, 누락 5).

**결정**: 그룹 C 의 consumer-only bullet 에서 **사본 enumeration 을 제거**하고 SSOT 를 **참조**로 대체한다. 둘째 사본이 없으면 drift 가 구조적으로 불가능 (prevention-by-design).
- authoritative 목록 = `.github/workflows/invariant-check.yml` 의 `CONSUMER_ONLY_WORKFLOWS` bash 배열 (안정 심볼 참조 — brittle 한 line-number 하드코딩 금지).
- ADR 본문은 개별 workflow 명 목록을 **재보유하지 않는다**. 재추가 = drift 재유입 → 금지 (self-defending 명시).

**재발방지 parity lint 미채택 근거 (ADR-119 §결정9)**: 사본 제거(§결정 34) 후 "SSOT↔산문 사본 parity 강제 lint"는 지킬 대상이 소멸해 vacuous. 산문 파싱 lint 는 fragile(CFP-2653) → 이득 0 · 비용 高 로 3문 게이트 FAIL. detection(lint) 대신 elimination(참조 단일화)이 근본책.

**scope**: doc-only. 신규 게이트/required-context/evidence-registry entry 0. branch protection 7-tuple 무변경 (ADR-127 required 신설 0 ratchet 정합).

## Amendment 24 (CFP-2719, 2026-07-17 KST) — Amendment 23 carrier prose fact-correction

**Carrier**: CFP-2719 (Epic CFP-2700 G2 — D3 drift scan + D4 ephemeral 역색인 실배선) / Story file = `mclayer/codeforge-internal-docs` `wrapper/stories/CFP-2719.md`.

**class**: **fact-correction (clarify)** — **결정 내용 무변경, 약화 0**. 선례 = **ADR-037 Amendment 3** ("결정 내용 무변경 … carrier prose 의 정정된 facts 만 SSOT-정합"). 신규 §결정 0 · 신규 entry 0 · tier/bypass/승격 gate 무변경 · Amendment 23 의 2 mechanical action 존치.

**배경**: G2 실배선 설계 lane(CFP-2719)이 Amendment 23 의 carrier prose 를 firsthand 재검증한 결과 **사실 3건** 이 실제와 어긋남을 확인했다. 세 진술 모두 Amd23 `infra-resource-undeclared-surface` entry `progress_note` 에 **verbatim 실재**한다 — Amd23 에 없는 주장은 정정하지 않는다(phantom fact-correction 0). 이 정정은 문서 위생이 아니라 **결함 예방**이다 — 정정 전 상태에서 만들어진 선행 구현 초기 커밋(`cfp-2700-g2` `7715657e`)이 아래 (2)의 hollow claim 을 **코드로 그대로 상속**한 것이 실증이다(주석은 monotonic shrink 를 주장하고 구현은 부재; 이후 merge-전 FIX 로 실배선 정정 → PR #2720 `8e60a53d` main 착지).

### 정정 3건 (Amendment 23 prose ↔ 실측)

| # | Amd23 진술 | 실측 정정 (firsthand) |
|---|---|---|
| **1** | prior art = `check_deferral_carrier_declared.py`(baseline loader/digest, Amd20) | **오인용** — 해당 파일 digest 구현 **0**(`:47` = 타 파일 지목 주석). 실 구현 = **`check_deferred_followup_reconcile.py`**(`compute_content_digest:356` / `sha256:362,381` / stored↔recomputed 불일치 `:395-399` / `grandfathered_ok:404`) + **`gen_deferred_followup_baseline.py`**(single-writer gen, `cmd_prune:187` monotonic shrink only). Amendment 20 본문(`:60`)은 이미 정확히 인용 → **Amd23 국소 결함**, framework 기제는 무결 |
| **2** | baseline = "Amd20 grandfather baseline **재사용**" | **hollow (코드 상속 축)** — 상속-재사용할 구현 부재. 나란히 인용된 `check_path_relocation_consistency.py` = `hashlib\|sha256\|digest\|monotonic\|shrink` hit **0** = Amd20 **비준수 인스턴스**. 정정 → **implemented-new Amd20-compliant**. ★ Epic AC-16 "기존 기제 재사용"은 **무손상** — "재사용" = 기제/패턴 축(Amd20 5요소 형판 + `check_deferred_followup_reconcile.py` prior-art)에서 참 ⊥ 본 정정 = 코드 상속 축, 두 축 disjoint |
| **3** | "(Python SSOT … **ReDoS-safe** line-by-line)" | ADR-082 Amd38 §결정 16 대상 closed-set 의 safety-claim → **paired proof-reference 또는 honest-ceiling 동반 의무**. claim 유지 시 DoS-bound 회귀 fixture(wall-clock)를 proof-ref 로 동반, 아니면 claim 제거 |

### 약화 0 논증 (ADR-058 §결정 5 비대상)

정정 3건 전부 **사실 축**(인용처 · 구현 유무 · 증거 의무)이며, tier · 승격 gate(§결정 6 3-AND) · surfacing 경계(§결정 32.D) · registry 등록 절차(§결정 5) 등 **결정 내용은 무변경**이다. invariant 강도 불변 → ADR-058 §결정 5 약화 방향 발의 차단 logic **비대상**. required contexts 7-tuple 무변경 (**surfacing ≠ membership** — ADR-145 §결정 3 override 비적용).

### 인접 SSOT 정정 (cross-ref, 본 ADR 결정 무영향)

- **tier 권한 귀속**: "ADR-157 §결정 9(tier)" = **오귀속**. §결정 9 = *census born-red 해소 + D3 base scan corpus 완전 열거*. tier·승격 권한 = **본 ADR Amendment 23** 이며 ADR-157 `:52` 이 자기 위임한다 — "tier·승격은 ADR-060 Amendment 소관, 본 ADR 은 승격 로직을 발명하지 않는다."
- **label registry 실경로** = **`docs/inter-plugin-contracts/label-registry-v2.md`**(v2.107). Epic change-plan 의 `docs/label-registry-v2.md` = **dead path**(파일 부재).

**scope**: doc-only (`archive/adr/**` 단일). 신규 게이트/required-context/evidence-registry entry 0. branch protection 7-tuple 무변경. plugin.json bump **0** — `archive/**` = ADR-037 결정 A2-3 **비귀속** + A2-6 **no-surface-touch 면제**(게이트 실측: `scripts/check-plugin-version-bump-self.sh:145` `archive/*` → `exempt`; ADR-037 `:432` 가 자기 Amendment PR 로 동일 경로 시연) → **marketplace sync 불요**(ADR-063 §결정 1 mirrored field 변경 0). D3 실배선 본체(5-piece + registry row + label + 6.97.0 MINOR + marketplace sync #364)는 **PR #2720 으로 이미 main 착지**(`8e60a53d`) — 잔여 갭 작업(per-class census floor + ADR-154 enrollment)은 CFP-2719 **Phase 2 PR scope**(6.98.0 MINOR + marketplace sync, change-plan §5.2/§5.3 SSOT).

## Amendment 25 (CFP-2650, 2026-07-19 KST) — resource-safety-claim-proof-presence warning→blocking-on-pr 승격 provenance

**Carrier**: CFP-2650 (CFP-2646 Wave 2 — resource-safety-claim-proof-presence 게이트 승격 + 정책문서 over-claim sweep + consumer 전파) / Story file = `mclayer/codeforge-internal-docs` `wrapper/stories/CFP-2650.md`.

**class**: **clarify / promotion-provenance** — 결정 내용 무변경, 약화 0. 신규 §결정 0 · 신규 entry 0 · 게이트 semantic 불변(tier flip 만). 선례 = Amendment 20(CFP-2594 flip provenance) + Amendment 24(clarify). ADR-082 §결정16(게이트 owner) semantic 불변 → ADR-082 Amendment 불요.

**배경**: CFP-2646 이 warning-tier(continue-on-error, merge 무차단)로 착지시킨 `resource-safety-claim-proof-presence` 게이트를, ADR-060 §결정 6 evidence-gate 실측 통과 후 blocking-on-pr 로 승격한다. registry `named_promotion_carrier: CFP-2650` 의 실집행.

### 승격 provenance (evidence-gate 3/3 MET, firsthand)

| 조건 | 기준 | 실측치 | 판정 |
|---|---|---|---|
| pr_cumulative_min | ≥ 20 | 56 merged PR (introduced_date 2026-07-13 이후) | MET |
| failure_threshold | = 0 | warning comment 0건 + 현 main HEAD lint PASS(0 new over-claim) + baseline 1회 생성 후 미변경 삼각검증 | MET |
| sibling_dependencies | CFP-2646 merged | PR #2651 MERGED 2026-07-12 | MET |

### 승격 mechanism (CFP-2594 flip model 동형)

- 양 workflow(`.github/workflows/` + `templates/github-workflows/` byte-identical pair, ADR-005) job+step `continue-on-error` 제거 = blocking-on-pr surfacing (lint 실패 = job 실패 = 체크 red).
- registry `current_tier: warning → blocking-on-pr` + `promoted_by: CFP-2650` + `promoted_date: 2026-07-19` provenance.
- **branch-protection 7-tuple 무변경** — surfacing ≠ required-context 편입 (ADR-125 required contexts 무변경 선호 + CFP-2594 "surfacing ≠ required" 선례). required 편입(7→8 fail-closed narrowing)은 §1 미요청 별개 escalation(ADR-145 선례), 본 Story 미채택. workflow header 승격노트의 stale 2-정의(surfacing = required 편입) 봉합.

### honesty-ceiling 불변 (ADR-151 §결정7 상속)

승격은 게이트의 강제 속성을 presence → truth 로 올리지 않는다. blocking-on-pr 은 좌향 노출의 가시성만 warning → PR-red 로 상향하고, presence ≠ truth 상한은 tier 와 독립적으로 불변이다. detection(보안테스트 lane) 존치. 본 Amendment 및 산출물에 "완전 봉인"·"완전 방지"·"truth 강제" 류 hard-claim 부재.

### 약화 0 논증 (ADR-058 §결정 5 비대상)

tier flip = additive ratchet↑ (warning → blocking-on-pr surfacing). invariant 강도 상향, 약화 방향 0건 → ADR-058 §결정 5 약화 방향 발의 차단 logic 비대상. required contexts 7-tuple 무변경 (surfacing ≠ membership — ADR-145 §결정 3 override 비적용). sunset_justification = N/A.

**scope**: workflow pair(continue-on-error 제거) + registry(current_tier flip + provenance) + lint docstring(granularity-carrier pointer 정정) + 정책문서 sweep(ADR-045:107 · ADR-061:454-455 3-line) + 신규 flip self-test(`tests/scripts/test_resource_safety_flip.py`) + plugin.json 6.108.0 MINOR + marketplace sync. 본 ADR 변경(`archive/**`)은 그 자체로 plugin.json bump 비귀속(ADR-037 A2-3/A2-6 면제); bump 는 workflow/registry/script 변경이 driver.
