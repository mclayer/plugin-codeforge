---
adr_number: 73
title: Orchestrator verify-before-assert — cross-repo ground truth + assumption verify mandate
status: Accepted
category: governance
date: 2026-05-14
carrier_story: CFP-622
parent_epic: null
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    cfp: CFP-776
    date: 2026-05-17
    scope: "ADR-082 cross-ref 보완 관계 명시 (disjoint 보완) — ADR-073 = Orchestrator 행위(cross-repo state + assumption) 한정 ↔ ADR-082 = internal lane agent self-write(§9 evidence / Phase 0 mapping / corpus enumeration) write-time semantic truth verify. 두 layer disjoint, scope 침범 0. ADR-082 §결정 1 layer disjoint 4-layer 표가 공통 anchor (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D). 본문 §결정 / mechanism 의미 변경 없음 — cross-ref-only Amendment."
    status: applied
    ref: "## Amendments / Amendment 1 + ADR-082 §결정 1"
    sunset_justification: null
  - amendment_id: 2
    cfp: CFP-966
    date: 2026-05-18
    scope: "§결정 1 expansion — transition trigger enum 3종 (lane_spawn / pr_open / merge_transition) + cold start session_start 보강 + sustained in-session polling 의무 (turn-0-only SessionStart hook 한계 해소). 본 Amendment 는 §결정 1-8 본문 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 0건. evidence-checks-registry warning-tier entry parallel-work-sentinel-pickup (recurrence count 2 / threshold 3 / promotion_trigger auto_blocking, schema v1.2 정합) 가 measurement carrier. memory rule 6 (title-based search) + rule 7 (Epic state poll) = declarative cross-ref normative anchor (mechanical enforcement = sibling Story-2 CFP-967 carrier). Sentinel: 2026-05-18 KST same-day 2/2 parallel race incidents (CFP-953 first label-based search miss + CFP-946 second 11분 gap Epic close miss)."
    status: applied
    ref: "## Amendments / Amendment 2 + CFP-966 carrier"
    sunset_justification: null
  - amendment_id: 3
    cfp: CFP-689
    date: 2026-05-20
    scope: "§결정 1 expansion — transition trigger enum 4번째 entry `worktree_lane_spawn` 추가 (closed-set ratchet 강화, Amendment 2 §결정 1-A precedent 답습) + worktree-first 환경 self-ownership verify 3-tuple path-based normative (a) cwd ↔ worktree path 일치 (`git rev-parse --show-toplevel` vs `git worktree list --porcelain`, path normalize forward-slash + lowercase drive-letter) (b) HEAD lineage ↔ session reflog membership (long-Phase-gap reflog 90d GC 시 (a)+(c) 2-source AND fallback) (c) `git worktree list --porcelain | grep <branch>` + reflog 2-source AND ownership verify + subagent verdict `parallel_session_conflict` 발화 시 Orchestrator re-verify mandate (ADR-082 verify-before-trust 자기 산출물 영역 확장 cross-ref — agent 도 multi-worktree self-confusion 보임). 본 Amendment 는 §결정 1-8 본문 + Amendment 1+2 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 0건. evidence-checks-registry warning-tier entry `worktree-self-ownership-verify` (recurrence count 3 / threshold 3 / promotion_trigger auto_blocking, declaration-only-Wave-1) 가 measurement carrier. memory `feedback_worktree_first_not_parallel_session` = normative 승격 carrier. Sentinel: 2026-05-19~20 KST single session 3 occurrences (CFP-1026 STAND-DOWN false-positive + CFP-681 cfp-1014 dup worktree RequirementsPL `f39b221` self-misflag + CFP-681 ArchitectPL Phase 3 자기 ArchitectAgent commit `00b7d8a` parallel_session_conflict mis-flag)."
    status: applied
    ref: "## Amendments / Amendment 3 + CFP-689 carrier"
    sunset_justification: null
  - amendment_id: 4
    cfp: CFP-1041
    date: 2026-05-20
    scope: "ADR-085 cross-ref 보완 관계 명시 (disjoint complement — verify axis ↔ coordination axis). ADR-073 = Orchestrator 행위(cross-repo state + assumption) verify 한정 (verify axis) ↔ ADR-085 = 복수 Claude Code session ownership / 분담 / handoff coordination (coordination axis, pre-hoc cross-session). 두 layer axis disjoint — verify 가 충족되어도 ownership 미결정 시 parallel race 발생, ownership 결정 후에도 verify 미수행 시 false claim. ADR-085 §결정 1 5-layer disjoint 표가 공통 anchor (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row Multi-session coordination 신설). 본 Amendment 는 §결정 1 lane-entry sentinel 4-step polling 의 4번째 source (active_sessions_check) cross-ref-only append — 본문 §결정 1-8 + Amendment 1-3 mechanism 의미 변경 0 (ADR-085 §결정 3 cross-ref-only Amendment, ADR-082 Amendment 1 ADR-073 cross-ref pattern verbatim 답습). post-rebase sequence [1, 2, 3 (CFP-689 worktree-first self-ownership), 4 (본 CFP-1041 ADR-085 coordination)] consecutive — sibling escalation #1038 의 actual carrier = CFP-689 (PR #1043 merged 18236621 2026-05-20, 본 CFP-1041 Phase 1 PR open 도중 origin/main 으로 advance), dogfooding ADR-085 본 carrier 가 codify 하는 `parallel_session_shared_workdir_collision` pattern (9th+ parallel race lineage single session evidence)."
    status: applied
    ref: "## Amendments / Amendment 4 + ADR-085 §결정 3"
    sunset_justification: null
  - amendment_id: 5
    cfp: CFP-1102
    date: 2026-05-20
    scope: "§결정 1 expansion — transition trigger enum 5번째 entry `fix_iter_start` 추가 (closed-set ratchet 강화, Amendment 2/3 §결정 1-A precedent 답습). FIX iter trigger 시점 main HEAD pin verify mandate — §10 FIX Ledger row append 시점 + FIX iter N > 0 영역에서 `git fetch origin main` + `gh api repos/<owner>/<repo>/git/refs/heads/main --jq '.object.sha'` direct pin + cached SHA cross-check 의무 + `verified-via` annotation. CFP-1087 cascade race evidence (CFP-1086 main S1/S3/S4/S5 1시간 안 5 commits advance during FIX iter 1, force-push 후 또 CONFLICTING) — pattern_count 2 reach (CFP-953 pre-flight verify stale + CFP-1087 cascade race) HIGH escalation per ADR-045 §D-9 Mandatory framing. 본 Amendment 는 §결정 1-8 본문 + Amendment 1+2+3+4 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 0건. evidence-checks-registry warning-tier entry `parallel-work-sentinel-pickup` (Amendment 2 carrier) 의 fix_iter_start trigger 영역 확장 = mechanical wire Wave 2 별 carrier (sibling: force-push pre-flight gate CFP-1103). memory rule 7 (pin HEAD SHA first, feedback-verify-pin-head-sha) declarative cross-ref normative anchor."
    status: applied
    ref: "## Amendments / Amendment 5 + §결정 1-A transition trigger 표 5번째 row"
    sunset_justification: null
  - amendment_id: 6
    cfp: CFP-1318
    date: 2026-05-23
    scope: "§결정 1 expansion — transition trigger enum 6번째 entry `sibling_story_handoff` 추가 (closed-set ratchet 강화, Amendment 2/3/5 §결정 1-A precedent 답습). Epic 안 복수 Story 가 sequential 또는 parallel 진행 시, agent / subagent (chief author / Analyst / Researcher / PL deputy) 가 sibling Story 의 진행 상태 / scope / artifact ownership 을 단정 발화하는 시점 의무. Orchestrator 단독 행위 영역 (base + Amendment 1-5) 을 agent / subagent 행위 영역 (sibling Story state polling) 으로 확장한다 — verify subject = agent / subagent, verify object = sibling Story state, verify direction = bidirectional (chief↔Orchestrator 양방향 catch). 본 Amendment 는 §결정 1-8 본문 + Amendment 1+2+3+4+5 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 / 면제 영역 0건. Pattern_count 3 reach Mandatory escalation (PMOAgent W5 retros 누적 corpus enumeration sentinels CFP-1226 + CFP-1269 + CFP-1273, Epic-A #1146 close retro internal-docs#797 carrier — 3 occurrences of `sibling_story_stale_claim_at_handoff` super-class), ADR-045 §D-9 Mandatory framing 정합. evidence-checks-registry warning-tier entry `subagent-sibling-story-polling-evidence` 신설 = mechanical wire Wave 2 별 sub-CFP (declaration-only-Wave-1 retain, parallel-work-sentinel-pickup precedent 답습). memory rule 6 (title-based search) + rule 7 (Epic state poll) declarative cross-ref normative anchor — 본 Amendment 6 가 detection layer (Orchestrator-side) 의 sibling-edge complement (agent/subagent-side) 확장한다."
    status: applied
    ref: "## Amendments / Amendment 6 + §결정 1-A transition trigger 표 6번째 row"
    sunset_justification: null
  - amendment_id: 7
    cfp: CFP-1319
    date: 2026-05-24
    scope: "§결정 1 expansion — transition trigger enum 7번째 entry `stale_local_main_checkout` 추가 (closed-set ratchet 강화, Amendment 2/3/5/6 §결정 1-A precedent 답습). Orchestrator 가 main worktree (또는 본 session 시작 시점 checkout) 에서 src/* / docs/* / inter-plugin-contracts/* / ADR / Change Plan / Story 본문 file Read 시 working tree HEAD 가 origin/main 보다 stale (≥ N commits behind 또는 sibling session merge 후 미반영) 인 영역에서 chief / Analyst / Researcher 의 claim 을 ground truth 와 대조해 hallucination 으로 오분류 anti-pattern. 본 Amendment 7 = Orchestrator session-start cold start + pre-Read pre-flight `git fetch origin && git rev-parse origin/main vs HEAD` divergence detection mandate + divergence ≥ threshold 시 fresh worktree (EnterWorktree) 재진입 의무 + Read 의 ground truth = `git show origin/main:<path>` direct fetch (working tree file 우회). 본 Amendment 는 §결정 1-8 본문 + Amendment 1+2+3+4+5+6 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 / 면제 영역 0건. Pattern_count 3+ reach (Epic-A W5-S14 init + W5-S16 init + CFP-1318 본 session 다회 reproduction — Orchestrator 자가 catch 사례 포함 super-class `stale_local_main_checkout`), ADR-045 §D-9 Mandatory framing 정합. evidence-checks-registry warning-tier entry `stale-local-main-checkout-divergence-check` 신설 = mechanical wire Wave 2 별 sub-CFP (declaration-only-Wave-1 retain, parallel-work-sentinel-pickup + subagent-sibling-story-polling-evidence precedent 답습). memory `feedback_worktree_first_not_parallel_session` declarative cross-ref normative anchor — 본 Amendment 7 = Orchestrator self-Read 영역 (worktree-first 환경 안 stale local checkout 사용 anti-pattern) 차단 mandate."
    status: applied
    ref: "## Amendments / Amendment 7 + §결정 1-A transition trigger 표 7번째 row"
    sunset_justification: null
  - amendment_id: 8
    cfp: CFP-1348
    date: 2026-05-24
    scope: "§결정 1 expansion — transition trigger enum 8번째 entry `mcp_token_expired_mid_flight` 추가 (closed-set ratchet 강화, Amendment 2/3/5/6/7 §결정 1-A precedent 답습). MCP server (`mcp__plugin_atlassian_atlassian__*` / `mcp__github__*` / 등) 인증 token TTL (OAuth ~1hr 기준) expiry mid-flight 영역 — Orchestrator 가 6 parallel agent dispatch 후 ~3-5분 안 token 전부 expired sentinel reproduction (CFP-1146 Epic-A W5 다회 발생). 본 Amendment 8 = lane-spawn / MCP-direct work 시작 직전 token freshness pre-flight verify mandate + token TTL threshold (default 15분 잔여) 미만 시 사용자 /mcp 재인증 요청 의무 + agent spawn prompt 안 `mcp_token_freshness_verified: bool` field (verdict packet 자체 검증). 본 Amendment 는 §결정 1-8 본문 + Amendment 1+2+3+4+5+6+7 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 / 면제 영역 0건. Pattern_count 2 reach (CFP-1146 W5-S15+S16+S17 6 parallel dispatch token expiry, 본 session evidence base, 외부 session evidence 부재 → pattern_count 2 conservative). evidence-checks-registry warning-tier entry `mcp-token-freshness-precheck` 신설 = mechanical wire Wave 2 별 sub-CFP (declaration-only-Wave-1 retain, parallel-work-sentinel-pickup + subagent-sibling-story-polling-evidence + stale-local-main-checkout-divergence-check precedent 답습). 본 Amendment 8 = MCP-direct work 영역 (auth layer staleness) — Amendment 7 의 git layer staleness 와 axis disjoint (auth ↔ git layer disjoint, 양 staleness sub-domain)."
    status: applied
    ref: "## Amendments / Amendment 8 + §결정 1-A transition trigger 표 8번째 row"
    sunset_justification: null
  - amendment_id: 9
    cfp: CFP-1384
    date: 2026-05-24
    scope: "Wave 2 mechanical wire activation — Amd 7 (CFP-1319) `stale_local_main_checkout` declaration→mechanical wire. `mechanical_enforcement_actions[]` 5번째 entry `stale-local-main-checkout-divergence-check` + evidence-checks-registry warning-tier (status Active) + SessionStart hook (polyglot extensionless + hooks.json matcher) + script chain (bash thin + Python SSOT per ADR-061 + check-baseline-pin-verify lane spawn lint) + workflow dual trigger pull_request + workflow_dispatch + .github/workflows self-app per ADR-005 + bats fixture pair RED→GREEN stash proof + label-registry v2.53→v2.54 MINOR (`hotfix-bypass:stale-local-main-checkout-divergence-check` 75번째 family member). Pattern_count 10+ reach Mandatory (CFP-1146 W5-S14/S16 + CFP-1318 + CFP-1333 3-occurrence + CFP-1384 + ArchitectPL iter 1+2 META in-flight). recursive dogfooding self-evidence — retain pattern (behavioral directive 만으로 forcing function 달성) 가정 systemic falsified."
    status: applied
    ref: "## Amendments / Amendment 9 + §결정 1-I main checkout divergence detection primitive mechanical activation"
    sunset_justification: null
  - amendment_id: 10
    cfp: CFP-1336
    date: 2026-05-24
    scope: "§결정 1 expansion — transition trigger enum 9번째 entry `label_change`. cross-repo label change event (wrapper Story Issue phase:*/gate:* mutation + impl repo PR label mutation + `cross-repo-label-sync.yml` workflow + `gh api .../labels` direct call 직전·직후) verify-before-assert 4-step (git fetch + gh api direct + Story §14 + active_sessions[] dual-source AND + verified-via) + T-2 self-trigger 4-pattern AND guard (sender.type early-exit / actor-allowlist / `[skip-cross-repo-sync]` marker / idempotent diff). paired sibling ADR-082 Amd 14 (1-D cross-repo label-write authority) + ADR-066 Amd 4 (PAT scope issues:write) = 3 ADR 동시 발의 axis disjoint (verify subject ↔ write authority ↔ PAT scope). axis disjoint vs Amd 7 git layer + Amd 8 auth layer (label state layer). evidence-checks-registry `cross-repo-label-sync` Wave 2 별 sub-CFP. CFP-1302 D-4 chief dissent carry-over. slot history: 9→10 (CFP-1384 mid-session collision)."
    status: applied
    ref: "## Amendments / Amendment 10 + §결정 1-A transition trigger 표 9번째 row"
    sunset_justification: null
  - amendment_id: 11
    cfp: CFP-1437
    date: 2026-05-24
    scope: "§결정 1 expansion — transition trigger enum 10번째 entry `spawn_prompt_emit` 추가 (closed-set ratchet 강화, Amendment 2/3/5/6/7/8/10 §결정 1-A precedent 답습). Orchestrator (또는 PL agent / chief author) 가 lane PL / chief author / deputy / 4-tuple sub-tuple subagent 를 spawn 하는 시점 영역 — spawn prompt emit 직전 `git rev-parse origin/main` direct fetch + spawn prompt 첫 줄 `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block 의무 + verified-via annotation. ADR-082 Amendment 5 §결정 1 sub-scope (1-C) `[USER-UTTERANCE-VERBATIM]` precedent 답습 (spawn-time anchor block pattern). 본 Amendment 는 §결정 1-10 본문 + Amendment 1+2+3+4+5+6+7+8+9+10 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 / 면제 영역 0건. closed_enum: open_extension:false — 11번째 trigger 추가 시 Amendment 강화 방향만. evidence-checks-registry warning-tier entry `spawn-prompt-head-pin-presence` 신설 = mechanical wire Wave 2 별 sub-CFP (declaration-only-Wave-1 retain, parallel-work-sentinel-pickup + worktree-self-ownership-verify + subagent-sibling-story-polling-evidence + mcp-token-freshness-precheck + stale-local-main-checkout-divergence-check + cross-repo-label-sync precedent 답습). paired sibling ADR-082 Amendment 15 §결정 1 layer 1 sub-scope (1-E) spawn prompt SHA-anchor write-time verify mandate (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier). 본 Amendment 11 = spawn-time layer 영역 (Orchestrator/PL/chief author self-assertion verify, transition trigger `spawn_prompt_emit`) — Amendment 7 git layer staleness + Amendment 8 auth layer staleness + Amendment 10 label state layer 와 axis disjoint (spawn-time SHA-anchor layer, 별 sub-domain). 동인: CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach single Story 4 reach lineage + 5th collision (Amd 8 → 10 → 12 → 13 → 14 history) system-level evidence — 본 Amendment 11 = preventive solution carrier (spawn-time origin/main SHA pin 으로 chief author / deputy stale-at-planning 차단 forcing function). cascade SHA propagation 의무 (parent → child spawn 시 fresh pin re-fetch, parent SHA verbatim carry 금지)."
    status: applied
    ref: "## Amendments / Amendment 11 + §결정 1-A transition trigger 표 10번째 row"
    sunset_justification: null
  - amendment_id: 12
    cfp: CFP-1436
    date: 2026-05-24
    scope: "§결정 1 expansion — transition trigger enum 11번째 entry `mid_spawn_origin_drift_detected` 추가 (closed-set ratchet 강화, Amendment 2/3/5/6/7/8/10/11 §결정 1-A precedent 답습). Sub-CFP B of CFP-1389 — paired sibling CFP-1437 (Sub-CFP A) 의 **reactive complement** (Sub-CFP A = preventive pre-spawn time / Sub-CFP B = reactive mid-spawn time). chief author / deputy / 4-tuple sub-tuple spawn-internal periodic check 영역 — 작업 중간 (예: 매 N file edit 또는 매 Edit/Write tool 호출 후) `git fetch origin main --quiet` + `git rev-parse origin/main` 으로 spawn 시점 PRE-SPAWN-ORIGIN-MAIN-SHA 와 비교 drift 감지 의무. drift threshold (≥ N commits behind) 도달 시 `drift_detected: true` flag 와 함께 Orchestrator 에 RETURN — Orchestrator 가 (a) fresh pin 으로 re-spawn / (b) fast-fail / (c) escalate 결정. CFP-1336 9+ collisions evidence preventive (Sub-CFP A) + reactive (Sub-CFP B) 2-layer defense forcing function 완결. 본 Amendment 는 §결정 1-11 본문 + Amendment 1+2+3+4+5+6+7+8+9+10+11 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 / 면제 영역 0건. closed_enum: open_extension:false — 12번째 trigger 추가 시 Amendment 강화 방향만. evidence-checks-registry warning-tier entry `mid-spawn-drift-detection` 신설 = mechanical wire Wave 2 별 sub-CFP (declaration-only-Wave-1 retain, parallel-work-sentinel-pickup + worktree-self-ownership-verify + subagent-sibling-story-polling-evidence + mcp-token-freshness-precheck + stale-local-main-checkout-divergence-check + cross-repo-label-sync + spawn-prompt-head-pin-presence precedent 답습). paired sibling ADR-082 Amendment 16 §결정 1 layer 1 sub-scope (1-F) spawn-internal periodic origin/main fetch + return early protocol (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier). 본 Amendment 12 = mid-spawn time layer 영역 (chief author / deputy / sub-tuple self-detection + return early, transition trigger `mid_spawn_origin_drift_detected`) — Amendment 11 spawn-time SHA-anchor layer (pre-spawn time) 와 axis disjoint (mid-spawn time reactive drift detection layer, 별 sub-domain)."
    status: applied
    ref: "## Amendments / Amendment 12 + §결정 1-A transition trigger 표 11번째 row"
    sunset_justification: null
  - amendment_id: 13
    cfp: CFP-FU-A
    date: 2026-05-25
    scope: "§결정 1 expansion — transition trigger enum 12+13번째 entry `pre_git_operation` + `pre_push`. polling cadence 1→3 확장 (lane-entry + git operation 직전 + push 직전). sub-decision 1 (polling threshold tighten) within CFP-FU-A. paired sibling Amd 14 (OR→AND composition) + ADR-082 Amd 19 (1-I pre-spawn-prompt-finalize) = 3 ADR 동시 발의 axis disjoint 3-set. evidence-checks-registry `pre-git-operation-sentinel-pickup` + `pre-push-sentinel-pickup` Wave 2 별 sub-CFP. 동인 = pattern_count 11 (CFP-1420). pre-git-state-mutation layer (`git add/commit/merge/rebase` 직전) + pre-network-publish layer (`git push` 직전). axis disjoint vs Amd 5 fix_iter + Amd 11 spawn-time + Amd 12 mid-spawn (event timing layer)."
    status: applied
    ref: "## Amendments / Amendment 13 + §결정 1-A transition trigger 표 12+13번째 row"
    sunset_justification: null
  - amendment_id: 14
    cfp: CFP-FU-A
    date: 2026-05-25
    scope: "§결정 1-P primitive 신설 — AND aggregate composition layer. `scripts/lib/check_parallel_work_sentinel.py:437` argparse `--mode` choices = `[\"title-search\", \"epic-state-poll\", \"head-compare-sibling-commits\"]` mutually exclusive dispatcher 영역 (single-mode invocation, caller discretion only) → 3-mode 동시 실행 + 모두 AND aggregate 의무 composition layer 신설 mandate. lane-entry sentinel polling 시 3 mode 모두 invoke + AND aggregate verify (single-mode invocation 차단). caller discretion 금지 — race window 차단 능력 1/3 → 3/3 보장 ratchet. sub-decision 2 (Heuristic precision triple-source AND) carrier within CFP-FU-A. axis disjoint with Amd 11/12/13 (Amd 11/12/13 = single source per spawn or single trigger per cadence, 본 Amd 14 = multi-source AND composition per polling event). paired sibling Amd 13 (sub-decision 1 polling cadence 1→3) + ADR-082 Amendment 19 sub-scope (1-I) (sub-decision 3 pre-spawn-prompt-finalize verify layer, renumbered from Amd 18 sub-scope 1-H post CFP-1342 mid-flight collision recovery) = 3 ADR Amendment 동시 발의 axis disjoint complement 3-set ADR-064 §결정 1 CFP scope unitary 정합. 본 Amendment 는 §결정 1-11 + 1-P primitive 신설 + Amendment 1-13 scope 강화 only (ADR-058 §결정 5 ratchet 정합) — 약화 / scope 축소 / 면제 영역 0건. evidence-checks-registry warning-tier entry `parallel-work-sentinel-and-aggregate` 신설 = mechanical wire Wave 2 별 sub-CFP carrier (declaration-only-Wave-1 retain — `scripts/lib/check_parallel_work_sentinel.py` 신규 `--mode all-and` choice 추가 + 3 sub-mode invoke + 결과 AND aggregate logic Wave 2 carrier). parallel session race 11th occurrence (CFP-1420 Sub-A S1.2 STAND_DOWN_DUPLICATE per PR #1441 prior merge) — OR semantics structural weakness root cause carrier (현재 lib code = single-mode dispatcher caller discretion 으로 race window 차단 능력 1/3 수준, AND composition 으로 race window 차단 능력 3/3 ratchet)."
    status: applied
    ref: "## Amendments / Amendment 14 + §결정 1-P primitive AND composition layer"
    sunset_justification: null
  - amendment_id: 15
    cfp: CFP-1571
    date: 2026-05-25
    scope: "§결정 1 expansion — transition trigger enum 14번째 entry `architect_agent_chief_author_lane_spawn` (ArchitectPL → ArchitectAgent chief author handoff specific cadence, Amd 11 generic spawn 의 chief-author specialization). 동인 = `parallel-session-merge-stream-main-advance-during-lane-flow` pattern_count 5 reach (CFP-1334 §3.1 4건 + CFP-1403 §3.1 1건 stale-base regression cascade). Verify mandate 4-step: (a) `git -C <worktree> fetch origin` / (b) `git diff origin/main..HEAD --stat` base drift detection / (c) drift 시 `git rebase origin/main` mechanical (no semantic conflict) / (d) expected diff narrowed verify. Root cause = ArchitectAgent commit on stale base → HEAD diff REVERSE direction downgrade. META self-application 1st (recursive dogfooding triggered AND RESOLVED in carrier PR): Phase 0 worktree HEAD `4a1f0be` drift 0 → CFP-1523 #1560 merged 5 commits drift → §결정 1-Q step 3 rebase (disjoint) + step 4 narrowed (1 file +101). closed_enum: open_extension:false. evidence-checks-registry warning-tier entry `architect-chief-author-base-sha-freeze-verify` = Wave 2 별 sub-CFP. doc-only fast-path Wave 1 declaration-only."
    status: applied
    ref: "## Amendments / Amendment 15 + §결정 1-A transition trigger 표 14번째 row"
    sunset_justification: null
  - amendment_id: 16
    cfp: CFP-1581
    date: 2026-05-25
    scope: "Wave 2 mechanical wire activation — Amd 15 (CFP-1571) `architect_agent_chief_author_lane_spawn` declaration→mechanical wire. `mechanical_enforcement_actions[]` 12번째 entry `architect-chief-author-base-sha-freeze-verify` status 갱신 + evidence-checks-registry warning-tier entry + script chain (bash thin + Python SSOT per ADR-061) + workflow dual trigger pull_request + workflow_dispatch + .github/workflows/ self-app per ADR-005 + bats fixture cohort RED→GREEN stash proof + label-registry v2.73→v2.74 MINOR (`hotfix-bypass:architect-chief-author-base-sha-freeze-verify` 99번째 family member). Pattern_count 5 reach Mandatory (CFP-1334 §3.1 4건 + CFP-1403 §3.1 1건 stale-base regression cascade). Wave 1→Wave 2 split precedent 7-instance (CFP-967/1437/1497/1436/1435/1539/1368). META anti-self-application: Phase 0 worktree HEAD `4000440` drift 0 → mid-flight CFP-1588 FU bundle 4 commits drift → §결정 1-Q step 3 mechanical rebase (drift 영역 disjoint) + step 4 expected diff narrowed (5 files / 129 insertions / 3 deletions). marketplace_sync_required: false."
    status: applied
    ref: "## Amendments / Amendment 16 + §결정 1-A transition trigger 표 14번째 row mechanical wire activation"
    sunset_justification: null
related_stories:
  - CFP-622  # carrier
  - CFP-776  # Amendment 1 — ADR-082 cross-ref (disjoint 보완)
  - CFP-966  # Amendment 2 — transition trigger enum + sustained polling (declarative anchor)
  - CFP-967  # Amendment 2 sibling — mechanical wire (script + hook + workflow + bats)
  - CFP-953  # Amendment 2 sentinel evidence (first parallel race — label-based search miss)
  - CFP-946  # Amendment 2 sentinel evidence (second parallel race — 11분 gap Epic close miss)
  - CFP-689  # Amendment 3 — worktree-first self-ownership verify 3-tuple (declarative anchor, plugin-codeforge#1038 carrier)
  - CFP-1038 # Amendment 3 carrier ESC — PMO P1 escalation (worktree_first_self_confusion_within_single_session pattern_count 3 reach, plugin-codeforge#1038)
  - CFP-983  # Amendment 3 candidate (c) 정식 carrier — #983 P1 ESC body shared workdir collision worktree-first invariant 강화 영역
  - CFP-1041 # Amendment 4 — ADR-085 disjoint complement (verify axis ↔ coordination axis), §결정 1 lane-entry sentinel 4-step polling 의 4번째 source `active_sessions_check` cross-ref-only append
  - CFP-1102 # Amendment 5 — transition trigger enum 5번째 entry `fix_iter_start` 추가 (FIX iter 시점 main HEAD pin verify mandate), CFP-1087 cascade race evidence
  - CFP-1318 # Amendment 6 — transition trigger enum 6번째 entry `sibling_story_handoff` (bidirectional verify-before-trust, agent/subagent sibling Story state polling 영역 확장), CFP-1226+CFP-1269+CFP-1273 sentinel pattern_count 3 Mandatory
  - CFP-1319 # Amendment 7 — transition trigger enum 7번째 entry `stale_local_main_checkout` (Orchestrator pre-Read divergence detection mandate, working tree HEAD vs origin/main staleness), Epic-A W5-S14/S16 + CFP-1318 다회 reproduction sentinel pattern_count 3+ Mandatory
  - CFP-1347 # Amendment 6 Wave 1 sibling carrier — evidence-checks-registry `subagent-sibling-story-polling-evidence` entry append (deferred-followup status, ADR-073 frontmatter mechanical_enforcement_actions[] 3rd entry activation)
  - CFP-1348 # Amendment 8 — transition trigger enum 8번째 entry `mcp_token_expired_mid_flight` (MCP server auth token TTL freshness pre-flight verify mandate), CFP-1146 Epic-A W5 6 parallel dispatch token expiry sentinel pattern_count 2 reach
  - CFP-1384 # Amendment 9 — Wave 2 mechanical wire activation (declaration → mechanical wire active 전환, Amendment 7 TBD-Wave-2 placeholder 채우기). 5번째 mechanical_enforcement_actions[] entry stale-local-main-checkout-divergence-check + evidence-checks-registry warning-tier entry (status: Active) + SessionStart hook + script chain + PR-time workflow + bats fixture pair + label-registry-v2 v2.54 MINOR. pattern_count 8+ reach Mandatory (CFP-1333 3-occurrence + CFP-1384 iter 1 7번째 + ArchitectPL spawn 8번째 recursive dogfooding self-evidence)
  - CFP-1336 # Amendment 10 — transition trigger enum 9번째 entry `label_change` (cross-repo bidirectional label sync verify-before-assert mandate, paired ADR-082 Amendment 14 sub-scope 1-D cross-repo label-write authority + ADR-066 Amendment 4 §결정 2 6번째 entry cross-repo-target-repos issues:write), CFP-1302 D-4 chief tie-break dissent carry-over F2 carrier. Amendment slot 9 → 10 renumber (CFP-1384 mid-session collision, 6th collision in CFP-1336 lineage, pattern_count 11+)
  - CFP-1302 # Amendment 10 parent — D-4 chief tie-break dissent (within-repo GITHUB_TOKEN 결정 시 cross-repo path 별 carrier 분리, axis disjoint follow-up F2 carrier scope split)
  - CFP-1437 # Amendment 11 — transition trigger enum 10번째 entry `spawn_prompt_emit` (Orchestrator / PL / chief author spawn 시점 origin/main SHA pin verify mandate + spawn prompt 첫 줄 [PRE-SPAWN-ORIGIN-MAIN-SHA] block 의무, paired ADR-082 Amendment 15 sub-scope 1-E spawn prompt SHA-anchor write-time verify). CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence preventive solution carrier — chief author / deputy stale-at-planning 차단 forcing function. cascade SHA propagation (parent → child fresh re-fetch). Sub-CFP A Wave 1 declarative-only carrier (mechanical lint wire = Wave 2 별 sub-CFP)
  - CFP-1389 # Amendment 11 origin — CFP-1336 retro follow-up Sub-CFP A (Pre-spawn HEAD-pin protocol mechanical lint Epic carrier)
  - CFP-1436 # Amendment 12 — transition trigger enum 11번째 entry `mid_spawn_origin_drift_detected` (chief author / deputy / sub-tuple spawn-internal periodic origin/main fetch drift detection + return early protocol, paired ADR-082 Amendment 16 sub-scope 1-F spawn-internal periodic origin re-pin). Sub-CFP B Wave 1 declarative-only — reactive complement to Sub-CFP A CFP-1437 (preventive pre-spawn pin) / Sub-CFP B 가 mid-spawn drift detection 영역 codify. CFP-1336 9+ collisions evidence reactive carrier — 2-layer defense (preventive + reactive) forcing function 완결. mechanical lint wire = Wave 2 별 sub-CFP
  - CFP-FU-A # Amendment 13 + 14 paired carriers — transition trigger enum 12+13번째 entry `pre_git_operation` + `pre_push` (Amd 13 sub-decision 1 polling cadence 1→3) + §결정 1-P primitive AND aggregate composition layer (Amd 14 sub-decision 2 OR→AND triple-source). paired sibling ADR-082 Amendment 19 sub-scope (1-I) pre-spawn-prompt-finalize verify layer (sub-decision 3 race window 단축, renumbered from Amd 18 sub-scope 1-H post CFP-1342 mid-flight collision recovery + 12th meta-occurrence). 3 ADR Amendment 동시 발의 axis disjoint complement 3-set ADR-064 §결정 1 CFP scope unitary 정합. parallel session race 11th occurrence (CFP-1420 Sub-A S1.2 STAND_DOWN_DUPLICATE per PR #1441 prior merge) escalate_user pattern_count 11 ≫ ADR-045 §D-9 threshold 2 = Mandatory escalation 산물. doc-only fast-path (ADR-054) Wave 1 declaration-only — mechanical wire (lint script + workflow + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 Wave 1→Wave 2 split precedent 답습)
  - CFP-1420 # Amendment 13+14 sentinel — parallel session race 11th occurrence (Mega-Epic CFP-1415 Sub-A S1.2, branch `cfp-1420-doc-locations-schema-1-2-confluence-variant` PR #1441 prior merge 2026-05-24T03:07:53Z → 본 session PR #1442 STAND_DOWN_DUPLICATE per DesignReviewPL verdict ESCALATE_PACKET_INCOMPLETE parallel_session_conflict_post_merge_duplicate)
  - CFP-1571 # Amendment 15 — transition trigger enum 14번째 entry `architect_agent_chief_author_lane_spawn` (ArchitectPL → ArchitectAgent chief author specific cadence base SHA freeze mandate, Amd 11 generic spawn 의 chief-author-specific specialization). Mandatory escalation #1571 (PMO 권장 Option A 채택) — `parallel-session-merge-stream-main-advance-during-lane-flow` pattern_count 5 reach (CFP-1334 §3.1 4건 + CFP-1403 §3.1 1건 stale-base regression cascade). escalate_user (PMO trivial 판정) per ADR-045 §D-9 Mandatory framing. Sibling CFP-1334 retro §5.2 escalate_user Optional 연속 lineage. doc-only fast-path (ADR-054) Wave 1 declaration-only — mechanical wire = 별 sub-CFP carrier.
  - CFP-1334 # Amendment 15 sentinel sibling — retro §5.2 4건 stale-base regression cascade lineage (escalate_user Optional, 본 CFP-1571 Mandatory escalation source 1/2)
  - CFP-1403 # Amendment 15 sentinel sibling — retro §3.1 1건 stale-base regression cascade lineage (escalate_user, 본 CFP-1571 Mandatory escalation source 2/2 + PMO 권장 Option A 채택 carrier)
  - CFP-1581 # Amendment 16 — Wave 2 mechanical wire activation (declaration → mechanical wire active 전환, Amendment 15 (CFP-1571) Wave 1 declarative-only carrier 의 mechanical wire activation). 12번째 mechanical_enforcement_actions[] entry `architect-chief-author-base-sha-freeze-verify` inline comment status 갱신 (deferred-followup → warning-tier wire complete) + evidence-checks-registry warning-tier entry 신규 등록 (NOT promotion per ADR-060 §결정 5 'first introduction = warning mode' default) + script chain (`scripts/check-architect-chief-author-base-sha-freeze.{sh,py}`) + PR-time workflow (`templates/github-workflows/architect-chief-author-base-sha-freeze.yml` + `.github/workflows/` self-app per ADR-005) + bats fixture cohort (`tests/scripts/check-architect-chief-author-base-sha-freeze/test_*.bats` RED→GREEN stash proof pattern per CFP-1334 §8.4) + label-registry-v2 v2.73 → v2.74 MINOR bump (`hotfix-bypass:architect-chief-author-base-sha-freeze-verify` 99번째 family member). pattern_count 6 reach Mandatory (CFP-1334 §3.1 4건 + CFP-1403 §3.1 1건 + 본 Story 6번째 META self-evidence). CFP-967 / CFP-1437 / CFP-1497 / CFP-1436 / CFP-1435 / CFP-1539 / CFP-1368 Wave 1 → Wave 2 split precedent 답습 chain 7-instance established pattern.
  - CFP-597  # sentinel #4 strike #1 origin (CLAUDE.md cap + playbook §3.6 false alarm)
  - CFP-578  # ADR-070 verify-before-trust 자매 (external worker output)
  - CFP-612  # ADR-071 dialog convergence 자매 governance
  - CFP-635  # sister Epic over-questioning (super-class shared, scope disjoint)
related_adrs:
  - ADR-070  # 자매 ADR (external worker output verify ↔ self-assertion verify)
  - ADR-071  # sister governance (dialog convergence layer)
  - ADR-082  # disjoint super-class (internal lane agent self-write verify — Orchestrator 행위 ↔ lane agent self-write)
  - ADR-039  # Inline whitelist boundary (verify 액션 분류 추가 row)
  - ADR-058  # sunset_justification (false 정합)
  - ADR-064  # decision principle mandate (self-application top-down ratchet)
  - ADR-012  # CLAUDE.md cap (cross-ref 추가 시 압축 plan 동반)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무 (governance category)
  - ADR-085  # Amendment 4 — disjoint complement (verify axis ↔ coordination axis, ADR-085 §결정 1 5-layer 표 anchor)
  - ADR-045  # §D-9 Mandatory framing — pattern_count ≥ threshold 2 escalation forcing function (본 Amendment 6 = pattern_count 3 reach Mandatory, 본 Amendment 7 = pattern_count 3+ reach Mandatory)
  - ADR-040  # Amendment 3 §결정 7.D self-application precedent (Wave 1 declaration-only / Wave 2 mechanical wire 분리)
related_files:
  - CLAUDE.md  # 결정 원칙 section + ADR list 영역 cross-ref
  - skills/codeforge-brainstorm/SKILL.md  # verify 의무 amend
  - <internal-docs>/wrapper/templates/spec.md  # pre_lookup_evidence[] field 신설
  - <internal-docs>/wrapper/templates/plan.md  # pre_lookup_evidence[] field 신설
is_transitional: false
mechanical_enforcement_actions:
  - parallel-work-sentinel-pickup     # CFP-966 Amendment 2 — declarative anchor (warning tier, sibling Story-2 CFP-967 mechanical wire merged 2026-05-19, status: warning per ADR-040 Amendment 3 §결정 7.D self-application 정합)
  - worktree-self-ownership-verify    # CFP-689 Amendment 3 — declarative anchor (warning tier, declaration-only-Wave-1, recurrence count 3 / threshold 3 / promotion_trigger auto_blocking, actual lint script + workflow + hook = sibling Story-2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — parallel-work-sentinel-pickup precedent 답습)
  - subagent-sibling-story-polling-evidence  # CFP-1347 Wave 1 (sibling carrier of Amendment 6 CFP-1318) — declarative anchor (warning tier, deferred-followup status, recurrence count 3 / threshold 3 / promotion_trigger auto_blocking, actual lint script + workflow + bats + label-registry MINOR bump = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — parallel-work-sentinel-pickup + worktree-self-ownership-verify precedent 답습. Amendment 6 §결정 1-A 6번째 entry sibling_story_handoff + §결정 1-G primitive + §결정 1-H subject scope 확장 carrier)
  - mcp-token-freshness-precheck  # CFP-1348 Wave 1 (sibling carrier of Amendment 8) — declarative anchor (warning tier, deferred-followup status, recurrence count 2 / threshold 3 / promotion_trigger auto_blocking pending 3 reach, actual SessionStart hook + script + workflow + bats + label-registry MINOR bump = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — parallel-work-sentinel-pickup + worktree-self-ownership-verify + subagent-sibling-story-polling-evidence precedent 답습. Amendment 8 §결정 1-A 8번째 entry mcp_token_expired_mid_flight + §결정 1-K primitive + §결정 1-L spawn prompt field carrier)
  - stale-local-main-checkout-divergence-check  # CFP-1384 Amendment 9 — Wave 2 mechanical wire activation (Wave 1 declaration anchor = CFP-1319 Amendment 7, TBD-Wave-2 placeholder 채우기). actual SessionStart hook (hooks/stale-local-main-checkout polyglot extensionless + hooks.json matcher 2nd command append, async: false sequential) + script chain (scripts/check-stale-local-main-checkout.sh thin wrapper + scripts/lib/check_stale_local_main_checkout.py Python SSOT per ADR-061 + scripts/check-baseline-pin-verify.sh lane spawn lint) + PR-time workflow (templates/github-workflows/stale-local-main-checkout-divergence-check.yml dual trigger pull_request + workflow_dispatch + .github/workflows self-app per ADR-005) + bats fixture pair (tests/scripts/test_check-stale-local-main-checkout.sh ≥ 6 assertion T-1~T-6 + tests/scripts/test_check-baseline-pin-verify.sh ≥ 4 assertion T-7~T-8, RED→GREEN stash proof pattern per CFP-1334 §8.4) + label-registry-v2 v2.54 MINOR (hotfix-bypass:stale-local-main-checkout-divergence-check 75번째 family member per ADR-108 §결정 3 META self-application 2nd applied case) = Wave 2 mechanical wire active (declaration-only-Wave-1 단계 도입 0 per CFP scope unitary ADR-064 §결정 1 — Phase 1 declarative + Phase 2 file impl atomic carrier). recurrence count 8 / threshold 3 / promotion_trigger auto_blocking (count > threshold 발화 active, promotion criteria pr_cumulative_min 20 + failure_threshold 0 충족 시 즉시 blocking-on-pr 승격). Amendment 7 §결정 1-I 3-step primitive mechanical 실 enforcement carrier (Step 1 git fetch + Step 2 rev-list count + Step 3 plain stdout warning + EnterWorktree guidance + ground truth direct fetch `git show origin/main:<path>`).
  - cross-repo-label-sync  # CFP-1336 Amendment 10 (renumber from 9, CFP-1384 mid-session collision) — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 0 — sentinel-driven 아닌 ratchet 확장 carrier (CFP-1302 D-4 chief tie-break dissent carry-over F2 carrier), threshold 3 / promotion_trigger none, actual workflow yml hydrate + script + bats fixture pair + impl repo listener seed + PAT scope grant actual = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합. Amendment 10 §결정 1-A 9번째 entry label_change + §결정 1-M primitive (verify-before-assert 4-step) carrier. paired sibling ADR-082 Amendment 14 sub-scope 1-D cross-repo label-write authority + ADR-066 Amendment 4 §결정 2 6번째 entry cross-repo-target-repos issues:write)
  - spawn-prompt-head-pin-presence  # CFP-1437 Amendment 11 — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 0 — sentinel-driven (CFP-1336 amendment_number_stale_at_planning pattern_count 9+ reach system-level evidence preventive solution carrier), threshold 3 / promotion_trigger none, actual lint script + workflow yml hydrate + bats fixture pair + label-registry MINOR bump + evidence-checks-registry entry = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — parallel-work-sentinel-pickup + worktree-self-ownership-verify + subagent-sibling-story-polling-evidence + mcp-token-freshness-precheck + stale-local-main-checkout-divergence-check + cross-repo-label-sync precedent 답습. Amendment 11 §결정 1-A 10번째 entry `spawn_prompt_emit` + §결정 1-N primitive (spawn-time `git rev-parse origin/main` direct fetch + spawn prompt 첫 줄 `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block + verified-via annotation + cascade SHA propagation parent → child fresh re-fetch) carrier. paired sibling ADR-082 Amendment 15 sub-scope 1-E spawn prompt SHA-anchor write-time verify (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier)
  - mid-spawn-drift-detection  # CFP-1436 Amendment 12 — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 0 — sentinel-driven reactive complement (CFP-1336 9+ collisions evidence, Sub-CFP A CFP-1437 preventive + Sub-CFP B CFP-1436 reactive 2-layer defense forcing function 완결), threshold 3 / promotion_trigger none, actual lint script + workflow yml hydrate + bats fixture pair + label-registry MINOR bump + evidence-checks-registry entry = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — parallel-work-sentinel-pickup + worktree-self-ownership-verify + subagent-sibling-story-polling-evidence + mcp-token-freshness-precheck + stale-local-main-checkout-divergence-check + cross-repo-label-sync + spawn-prompt-head-pin-presence precedent 답습. Amendment 12 §결정 1-A 11번째 entry `mid_spawn_origin_drift_detected` + §결정 1-O primitive (spawn-internal periodic `git fetch origin main --quiet` + `git rev-parse origin/main` compare with PRE-SPAWN-ORIGIN-MAIN-SHA + drift ≥ N threshold detection + return early protocol `drift_detected: true` flag) carrier. paired sibling ADR-082 Amendment 16 sub-scope 1-F spawn-internal periodic origin re-pin (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier)
  - pre-git-operation-sentinel-pickup  # CFP-FU-A Amendment 13 (1/2) — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 0 — sentinel-driven (CFP-1420 Sub-A S1.2 parallel session race 11th occurrence, escalate_user pattern_count 11 reach Mandatory ADR-045 §D-9), threshold 3 / promotion_trigger none, actual lint script + workflow yml hydrate + bats fixture pair + label-registry MINOR bump + evidence-checks-registry entry = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — parallel-work-sentinel-pickup + worktree-self-ownership-verify + subagent-sibling-story-polling-evidence + mcp-token-freshness-precheck + stale-local-main-checkout-divergence-check + cross-repo-label-sync + spawn-prompt-head-pin-presence + mid-spawn-drift-detection precedent 답습. Amendment 13 §결정 1-A 12번째 entry `pre_git_operation` carrier — git state mutation 직전 (예: `git add` / `git commit` / `git merge` / `git rebase` direct state mutation 직전) sentinel pickup 의무. paired sibling Amendment 14 (1-P AND composition layer) + ADR-082 Amendment 19 sub-scope (1-I) pre-spawn-prompt-finalize verify layer (renumbered from Amd 18 sub-scope 1-H post CFP-1342 collision recovery))
  - pre-push-sentinel-pickup  # CFP-FU-A Amendment 13 (2/2) — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 0 — sentinel-driven (CFP-1420 Sub-A S1.2), threshold 3 / promotion_trigger none, actual lint script + workflow yml hydrate + bats fixture pair + label-registry MINOR bump + evidence-checks-registry entry = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — pre-git-operation-sentinel-pickup precedent 답습. Amendment 13 §결정 1-A 13번째 entry `pre_push` carrier — `git push` direct cross-repo state propagation 직전 sentinel pickup 의무 (network publish 영역 — Amd 13 1/2 pre_git_operation 의 local-only mutation 영역과 axis disjoint complement). paired sibling Amendment 13 (1/2) + Amendment 14 + ADR-082 Amendment 19 sub-scope (1-I) (renumbered from Amd 18 sub-scope 1-H post CFP-1342 collision recovery))
  - parallel-work-sentinel-and-aggregate  # CFP-FU-A Amendment 14 — Wave 1 declarative anchor (warning tier, deferred-followup status, recurrence count 0 — sentinel-driven OR semantics structural weakness (CFP-1420 Sub-A S1.2 evidence root cause = `scripts/lib/check_parallel_work_sentinel.py:437` single-mode dispatcher, caller discretion only), threshold 3 / promotion_trigger none, actual `scripts/lib/check_parallel_work_sentinel.py` 신규 `--mode all-and` choice 추가 + 3 sub-mode invoke + 결과 AND aggregate logic + workflow yml hydrate + bats fixture pair + label-registry MINOR bump + evidence-checks-registry entry = Wave 2 별 sub-CFP carrier per ADR-040 Amendment 3 §결정 7.D self-application 정합 — pre-git-operation-sentinel-pickup + pre-push-sentinel-pickup precedent 답습. Amendment 14 §결정 1-P primitive AND aggregate composition layer carrier (3-mode 모두 invoke + 결과 AND aggregate verify, single-mode invocation 차단). paired sibling Amendment 13 (1/2 + 2/2) + ADR-082 Amendment 19 sub-scope (1-I) (renumbered from Amd 18 sub-scope 1-H post CFP-1342 collision recovery))
  - architect-chief-author-base-sha-freeze-verify  # CFP-1571 Amd 15 (Wave 1 declarative) → CFP-1581 Amd 16 (Wave 2 mechanical wire active). recurrence count 6 / threshold 3 / auto_blocking active. Mandatory escalation `parallel-session-merge-stream-main-advance-during-lane-flow` pattern_count 6 (CFP-1334 §3.1 4건 + CFP-1403 §3.1 1건 + CFP-1581 6th). Wave 2 wire: bash thin + Python SSOT (ADR-061) + workflow dual trigger + bats fixture RED→GREEN + label-registry v2.73→v2.74 (`hotfix-bypass:architect-chief-author-base-sha-freeze-verify` 99번째 family member) + evidence-checks-registry warning-tier. Wave 1→Wave 2 split chain 11-instance. Amd 15 §결정 1-A 14번째 entry `architect_agent_chief_author_lane_spawn` + §결정 1-Q primitive (4-step verify-before-assert: git fetch + git diff base drift + mechanical rebase + expected diff narrowed). Amd 16 = mechanical wire activation (artifact verification 2-mode lint: spawn-prompt-grep + lane-evidence-marker-grep).
# Wave 1 = behavioral directive only (Orchestrator self-discipline forcing function) — Amendment 2 (CFP-966)
# 가 첫 mechanical_enforcement_actions[] row entry append (declarative anchor only — script + workflow
# 실 binding 은 sibling Story-2 CFP-967 carrier).
# Layer 2 mechanical lint (pre-tool-use hook 또는 evidence-checks-registry warning-tier) = 별도 follow-up CFP 분리.
# 본 ADR effective 후 신설 evidence-enforceable entry 가 follow-up CFP carrier 에서 추가될 때
# mechanical_enforcement_actions[] 갱신 + Amendment 발의 (강화 방향만 — ADR-058 §결정 5 / ADR-064 §결정 7
# top-down ratchet 정합).
sunset_justification: "N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — verify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책)."
pre_lookup_evidence:
  verified_files:
    - { path: "docs/adr/ADR-070-codex-verify-before-trust.md", verified-via: "git show origin/main", note: "자매 ADR — 본질 선언 패턴 + 결정 구조 reference" }
    - { path: "docs/adr/ADR-071-orchestrator-user-dialog-convergence.md", verified-via: "git show origin/main", note: "anchor-first 패턴 차용 (mechanism 우선 reading risk 회피)" }
    - { path: "docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md", verified-via: "git show origin/main", note: "Inline whitelist 4-entry boundary" }
    - { path: "docs/adr/ADR-058-adr-sunset-criteria-mandate.md", verified-via: "git show origin/main", note: "is_transitional: false 정합 + sunset_justification ratchet 차단" }
    - { path: "docs/adr/ADR-064-decision-principle-mandate.md", verified-via: "git show origin/main", note: "self-application top-down ratchet (강화 방향 only)" }
    - { path: "docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md", verified-via: "git show origin/main", note: "Amendment 1 §결정 6 cap 320 (현 CLAUDE.md = 321줄, +1 over)" }
    - { path: "docs/adr/ADR-040-worktree-convention.md", verified-via: "git show origin/main", note: "Amendment 3 governance category mechanical_enforcement_actions[] 의무 (Wave 1 = []  empty + retroactive 면제 표시)" }
  origin_main_sha: "e5c5c64e64b28a83f312210a2a9c71e177738fb3"  # git rev-parse origin/main 결과 (PL self-application 첫 적용)
  last_git_fetch_timestamp: "2026-05-14T18:30+09:00"  # KST per memory feedback_time_display
---

# ADR-073: Orchestrator verify-before-assert — cross-repo ground truth + assumption verify mandate

## 상태

Accepted (2026-05-14 KST, CFP-622 carrier). `is_transitional: false` — 영구 정책 (governance carrier, ADR-064 / ADR-058 self carrier 패턴 정합).

## 본질 선언

> **Orchestrator 가 cross-repo state 또는 assumption 을 단정할 때, ground truth 를 verify-before-assert 의무.**

위 본질 선언이 본 ADR 의 **anchor**. 본 ADR 의 모든 §결정 (mandate / mechanism enumeration / 3-layer coherence / subagent context packet / spec template field / skill body amend / scope 외 분리) 은 본질을 보조하는 **scaffolding** — mechanism 만 codify 하고 본질 (verify discipline) 을 놓치면 ADR-071 가설 E (mechanical 규칙 자체 한계) 의 self-defeating trap 으로 떨어진다. 본 anchor 가 §결정 1 보다 먼저 배치된 이유 = mechanism 우선 reading risk 회피 forcing function (ADR-071 anchor-first 패턴 차용).

본 ADR 은 ADR-070 / ADR-071 와 함께 super-class "Orchestrator self-discipline ratchet" 의 3 children 중 1 children:

| Layer | ADR | Producer | Verify 영역 |
|---|---|---|---|
| External worker output | ADR-070 | Codex (외부 worker) | review-verdict-v4 finding evidence |
| Orchestrator self-assertion | **ADR-073 (본 ADR)** | Orchestrator (자기) | cross-repo state + file path 단정 |
| User dialog convergence | ADR-071 | Orchestrator (사용자 대화) | 4 vulnerability 차단 + 4 layer 검증 |

mechanism 만 codify 하고 본질을 놓치면 self-defeating trap. 3 layer cross-ref 의무 (§결정 3 표 verbatim).

## 컨텍스트

본 ADR 의 동인은 sentinel #4 strike 누적 evidence — Orchestrator 가 cross-repo file / state 인용 시 working tree 또는 stale local state 를 ground truth 로 신뢰하는 anti-pattern.

### Strike 누적 evidence 표

| Strike | Story | 일자 | 발견 영역 | 결과 |
|---|---|---|---|---|
| #1 | CFP-597 retro §6 sentinel #4 | 2026-05-13 | playbook §3.6 false alarm + CLAUDE.md 320 cap 위협 | 1 sample sentinel — 다음 carrier 동일 anti-pattern 재현 시 ADR 발의 임계 도달 declare |
| #2 | CFP-622 본 carrier (2026-05-14 KST) | 2026-05-14 | `grep -c §3.6\|§5.7 c:/workspace/mclayer/plugin-codeforge-{design,pmo}/agents/...` → 0 hits (false-negative). 실제 origin/main = CFP-597 PR #41 (f608838 design) + #17 (f77766d pmo) 으로 sibling backfill 완료 상태 | Root cause: `git fetch origin` 누락. Cascade: spec/plan/4 worktree 가짜 작업 ~30분 + 사용자 cognitive load 3회 confirm + 4 worktree setup→prune |

→ Issue #607 sentinel "2번째 sample 발견 시 ADR 발의 임계 도달" 충족. 본 ADR-073 발의 carrier.

### Systemic 4-layer staleness hierarchy (Bazel hermeticity 동형)

ground truth 의 staleness 계층:

```
working tree mutable        ← 가장 stale (uncommitted edits)
< local main push-lag       ← local commit 후 push 전
< origin/main canonical     ← canonical (GitHub remote)
< GitHub API eventual       ← API cache (eventual consistency)
```

Orchestrator 가 단정 발화 시 사용해야 하는 ground truth = **origin/main canonical** (working tree 와 local main 은 staleness 영역). GitHub API staleness 는 별도 영역 (§결정 7 scope 외 분리).

### 현 SSOT 결격 영역

- ADR-070 (Codex external worker verify) = external worker output scope. Orchestrator self-assertion 영역 normative anchor 부재.
- ADR-071 (사용자 dialog convergence) = dialog 표현 / 사실 vs 가치 분리 영역. cross-repo state factual verify 영역 부재.
- ADR-039 §결정 2 (Inline whitelist 4-entry) = inline 액션 분류 영역. file path / cross-repo state 인용 시 verify 의무 boundary 모호.
- ADR-064 §결정 7 (self-application top-down ratchet) = 결정 원칙 ratchet 영역. file Read 액션 verify 의무 영역 부재.

기존 SSOT 들이 super-class "Orchestrator self-discipline ratchet" 의 일부만 커버 — Orchestrator self-assertion verify 영역은 normative anchor 신설 영역 (본 ADR-073).

## 결정

### §결정 1 — Verify-before-assert mandate

Orchestrator (또는 subagent) 가 sibling plugin / cross-repo file path / state 에 대해 **단정 발화** 시 (예: "X file 안 §N section 부재", "Y issue closed 상태", "Z PR merged"), 다음 4 의무:

1. `cd <repo> && git fetch origin` 선행 (working tree stale 우려)
2. `git show origin/main:<path>` 또는 `gh issue/pr view --json state` direct verify
3. 인용 옆 `verified-via: <method>` annotation
4. spec/plan frontmatter 안 `pre_lookup_evidence[]` PL 수동 declaration (mechanical layer 부재 시)

**적용 영역**: cross-repo state + assumption 기술 한정. Inline whitelist (ADR-039 §결정 2 4-entry) 영역 안 단순 file stat (line count / section exist) 는 inline 허용 — **단정 발화 시만 verify 의무**.

**Inline whitelist boundary 표** (ADR-039 §결정 2 4-entry 영역 cross-ref):

| 액션 | 분류 | Verify 의무 | 근거 |
|---|---|---|---|
| 사용자 dialog 중 file Read | inline (ADR-039 1번 entry) | 인용 시만 (단순 stat 면제) | ADR-071 §결정 11 cognitive 보강 영역 |
| TodoWrite scratchpad | inline (ADR-039 2번 entry) | 면제 | non-assertion |
| Read-only Q&A 답변 | inline (ADR-039 3번 entry) | 인용 시만 (단순 stat 면제) | answer-only scope |
| Status report | inline (ADR-039 4번 entry) | 인용 시 의무 | factual claim 영역 |
| 사용자/subagent 단정 발화 | non-inline (subagent spawn 영역) | **의무** | 본 §결정 1 |

**거절된 대안 D1**:
- (D1-A) 모든 file Read 시 verify 의무 강제 — Inline whitelist 영역 침범 + ADR-039 default subagent context 정합 위반
- (D1-B) Codex worker 영역만 verify (ADR-070 흡수) — Orchestrator self-assertion 영역 systemic 원인 미해소 (strike #2 evidence 자체가 Orchestrator 자기 단정 영역)
- (D1-C) verify 의무를 사용자 dialog turn 한정 — ADR-071 dialog convergence 영역 침범 + subagent spawn prompt staleness 영역 미해소 (§결정 4 영역)

### §결정 2 — Mechanism enumeration (super-class anchor + extensible)

super-class = "stale source 인용 anti-pattern". 현재 mechanism 2 종, future strike #3+ append 가능 (ADR-058 §결정 5 ratchet 강화 방향 only).

| ID | Mechanism | Strike origin | 차단 mechanism |
|---|---|---|---|
| M1 | same-repo working tree mutation lag | CFP-597 retro §6 strike #1 (CLAUDE.md 320 cap stale read — working tree 미반영) | `wc -l <file>` 사전 측정 + 압축 plan 동반 (ADR-012 Amendment 1 정합) |
| M2 | cross-repo origin lag | 본 carrier strike #2 (git fetch 누락 → sibling backfill 인지 실패 → CFP-597 PR #41/#17 누락 인지 가짜 작업 ~30분) | `git fetch origin` 선행 + `git show origin/main:<path>` direct verify |
| M3+ | future strike (TBD) | TBD (다음 carrier sentinel) | TBD |

future strike #3+ 발견 시 row append 의무 — Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). M1 + M2 row 삭제 / 약화 변경 = sunset_justification 의무 (ratchet 차단 logic 통과 의무).

**Future append schema**:
```
| ID | Mechanism | Strike origin | 차단 mechanism |
|----|-----------|---------------|----------------|
| M3 | <신규 staleness 영역> | <Story ref + sentinel> | <차단 cmd / annotation> |
```

### §결정 3 — 3-layer coherence

verify-before-trust 원칙 3 layer cross-ref 의무. layer 침범 금지 (각 layer scope 분리 — 흡수 / 통합 시 dispatch_mode scope 침범 risk):

| Layer | ADR | Producer | 적용 영역 | scope 분리 사유 |
|---|---|---|---|---|
| External worker output | ADR-070 | Codex (외부 worker) | review-verdict-v4 finding evidence + verbatim attach | sandbox boundary cross-cutting (file Read 실패 silent fallback) |
| Orchestrator self-assertion | **ADR-073 (본 ADR)** | Orchestrator (자기) | cross-repo state + file path 단정 | working tree mutable < origin/main canonical staleness 영역 (ADR-070 sandbox 영역 외) |
| User dialog convergence | ADR-071 | Orchestrator (사용자 대화) | 4 vulnerability 차단 + 4 layer 검증 + cognitive convergence | dialog 표현 layer (ADR-073 factual verify 와 disjoint) |

**3 ADR 동시 진행 가능** (file-level conflict 0): super-class "Orchestrator self-discipline ratchet" children 이지만 producer / scope / verify 영역 모두 disjoint.

**거절된 대안 D3**:
- (D3-A) ADR-073 을 ADR-070 Amendment 로 통합 — Codex external worker scope ↔ Orchestrator self scope type mismatch (producer 영역 침범 risk + dispatch_mode confusion)
- (D3-B) ADR-073 을 ADR-071 Amendment 로 통합 — dialog convergence cognitive layer ↔ factual verify layer scope mismatch (가설 E mechanical 규칙 자체 한계 영역 vs 사실 verify 영역 disjoint)
- (D3-C) 3 ADR 통합 super ADR 신설 — super-class anchor 가 codified 되면 children 의 mechanism enumeration 자유도 손실 + future strike append 시 Amendment 영역 침범

### §결정 4 — Subagent context packet staleness annotation

Orchestrator 가 subagent spawn 시 prompt 안 file path / cross-repo state 인용 영역에 metadata 첨부 의무. subagent 가 Orchestrator 의 "지금" 가정 회피 — subagent context packet 자체가 staleness 영역.

**Context packet schema**:

```yaml
context_packet:
  cited_files:
    - path: "<absolute path or repo:relative>"
      verified_at: "<ISO-8601 KST>"
      git_fetch_sha: "<origin/main SHA at verify>"
      verified_via: "<method — git show origin/main | gh api | wc -l 등>"
  cited_state:
    - resource: "<issue#NNN | PR#NNN | branch:<name>>"
      verified_at: "<ISO-8601 KST>"
      api_response_sha: "<gh api ETag or query timestamp>"
      verified_via: "<gh issue view | gh pr view | git ls-tree>"
```

**적용 영역**: subagent spawn prompt 안 file path / cross-repo state 인용 시 의무. 단순 dialog turn (사용자 ↔ Orchestrator) 영역은 ADR-071 영역 (본 §결정 4 scope 외).

**거절된 대안 D4**:
- (D4-A) annotation 면제 (Orchestrator 신뢰) — strike #2 evidence (Orchestrator 자기 단정 영역) 가 mitigation 부재 영역
- (D4-B) verbatim file content 첨부 의무 (ADR-070 D2 패턴 차용) — Orchestrator subagent 영역은 own working directory 일치 영역 (sandbox boundary cross-cutting 부재) — verbatim 첨부 token 비용 과다 + ADR-070 영역 침범

### §결정 5 — spec/plan template `pre_lookup_evidence[]` field 신설

spec template + plan template (codeforge-internal-docs SSOT — ADR-013 dogfood-out 정합) 에 frontmatter field 신설.

**Schema**:

```yaml
pre_lookup_evidence:
  verified_files:
    - { path, repo, verified-via, sha }  # 또는 commit SHA
  cross_section_conflict_check:
    - { issue, scope, merge_order, conflict }
  last_git_fetch_timestamp: "<ISO-8601 KST>"  # ADR-073 §결정 1 의무
  origin_main_sha: "<git rev-parse origin/main 결과>"  # PL self-application 적용 시 권장
```

**적용 영역**:
- 모든 spec/plan 신설 시 frontmatter `pre_lookup_evidence` block 의무
- 본 ADR-073 spec (`<internal-docs>/wrapper/specs/2026-05-14-cfp-622-orchestrator-verify-before-assert.md`) frontmatter 가 첫 적용 사례 (recursive bootstrap mitigation — PL 수동 declare)
- 본 ADR-073 frontmatter `pre_lookup_evidence:` block 자체가 self-application 두 번째 사례

**target file** (codeforge-internal-docs PR3 carrier):
- `<internal-docs>/wrapper/templates/spec.md`
- `<internal-docs>/wrapper/templates/plan.md`

**거절된 대안 D5**:
- (D5-A) field 명 = `evidence[]` (단순) — 의미 모호 + 기존 evidence-checks-registry 와 충돌 risk
- (D5-B) field 명 = `verified_sources[]` — verified 라는 표현 redundancy (frontmatter 자체가 PL declare 영역)
- (D5-C) field optional — spec/plan 신설 forcing function 부재 (recursive bootstrap mitigation 효력 약화)

### §결정 6 — Skill body amend (codeforge:brainstorm only)

`skills/codeforge-brainstorm/SKILL.md` 본문 안 다음 section 추가 의무:

> **자기 적용 의무 (ADR-073 §결정 1)**: Phase 0 4 agent prompt 안 file path / cross-repo state 인용 시 `git fetch origin` 선행 + `git show origin/main:<path>` direct verify + `verified-via` annotation 의무. agent prompt template 의 default behavior — 4 agent 산출물 모두 `verified-via` annotation 준수.

**적용 영역 한정** (cross-plugin amend 분리):
- `skills/codeforge-brainstorm/SKILL.md` (codeforge wrapper plugin own skill) — **본 ADR scope**
- `superpowers:writing-plans` (claude-plugins-official upstream plugin) — **본 ADR scope 외** (별도 carrier 분리, CFP-622 §10 후속 carrier 영역 declare)

**거절된 대안 D6**:
- (D6-A) `superpowers:writing-plans` skill body 도 동시 amend — cross-plugin 영역 (claude-plugins-official upstream 협의 의무 발화) — Story scope 침범 + ADR-013 dogfood-out 영역 외
- (D6-B) `codeforge:brainstorm` Phase 0 mandatory 면제 (optional 명시) — 첫 적용 사례 effort 부족 + Phase 0 4 agent prompt staleness 영역 미커버

### §결정 7 — GitHub API staleness 분리 (scope 외)

`gh issue / pr list / view` 결과도 GitHub API eventual consistency 영역 — local git state staleness 와 별도 영역 (4-layer staleness hierarchy 의 4번째 layer).

**본 ADR scope = local git state 한정** (working tree / local main / origin/main 3-layer 영역).

GitHub API staleness 영역 = 별도 CFP carrier 분리:
- cross-repo state SSOT 영역 (issue / PR / branch 단정 verify 영역)
- API ETag / cache invalidation pattern 영역
- gh CLI vs MCP github tool selection 영역

**Cross-ref**: ADR-073 본문에 GitHub API staleness 영역은 "scope 외 declare" 만 하고 mechanism / mitigation 영역은 별도 CFP carrier 위임 (super-class 동일 children 으로 분리 가능).

**거절된 대안 D7**:
- (D7-A) GitHub API staleness 도 본 ADR 흡수 — scope 비대화 + 4-layer hierarchy mechanism 영역 침범 (gh CLI / MCP github tool 영역 = wrapper repo wrapper-only ζ arc 영역)
- (D7-B) GitHub API staleness 면제 declare 부재 — scope 모호성 향후 strike #3+ 인용 시 잘못된 영역 분류 risk

### §결정 8 — hook automation 분리 (scope 외)

`pre-tool-use` hook 으로 file Read 직전 git fetch trigger = mechanical enforcement layer.

**본 ADR scope = behavioral directive layer only** (Wave 1 = []  empty mechanical_enforcement_actions[]).

**별도 follow-up CFP 분리 영역**:
- pre-tool-use hook 도입 (file Read 액션 hook)
- evidence-checks-registry warning-tier entry (`orchestrator-verify-before-assert-declared`) 등록
- ADR-040 Amendment 3 §결정 7.A schema 정합 mechanical_enforcement_actions[] 갱신
- ADR-073 Amendment 1 carrier 발의 (강화 방향 only — ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합)

**Wave 1 → Wave 2 progression chain** (ADR-040 Amendment 3 self-application 패턴 차용):
```
Wave 1 (declaration mandate)         ← 본 ADR-073 (CFP-622, 2026-05-14)
  ↓
Wave 2 (mechanical lint actual wire) ← follow-up CFP (TBD)
  ↓
Wave 3 (warning → blocking-on-pr)    ← ADR-073 Amendment 2 (TBD, ratchet 강화)
```

**거절된 대안 D8**:
- (D8-A) Wave 1 동시 mechanical_enforcement_actions[] 신설 — hook automation 영역 (pre-tool-use hook) 가 ADR-073 declaration 동시 영역에 codify 시 Wave 1 → Wave 2 progression chain 손실 (ADR-040 Amendment 3 self-application 패턴 위반)
- (D8-B) hook automation 영구 면제 — verify-before-assert 의무가 behavioral directive layer 만 codified 시 strike #3+ 재발 risk + ratchet 강화 방향 차단 (ADR-058 §결정 5 정합 손실)

## 결과

본 ADR codify 결과:
- Sentinel #4 strike #2 trigger 충족 (Issue #607 — 2번째 sample 발견 시 ADR 발의 임계 도달)
- ADR-070 자매 layer 신설 (Codex external worker output verify ↔ Orchestrator self-assertion verify)
- 3-layer coherence (ADR-070 + ADR-071 + ADR-073) cross-ref 확립
- super-class anchor + 2 mechanism enumeration (M1 working tree mutation lag + M2 cross-repo origin lag) + future strike #N append schema
- skill body amend (codeforge:brainstorm Phase 0 verify 의무)
- spec/plan template `pre_lookup_evidence[]` field 신설
- 본 carrier 자체 self-application paradox 시연 (Strike #3 + Strike #4) → mechanism 확장 후보 evidence (M3 Windows shell ref-mangling, M4 continuous race condition during rebase)
- CFP-635 sister Epic (over-questioning) 와 super-class shared, scope disjoint

## Amendments

### Amendment 1 — ADR-082 cross-ref (disjoint 보완 관계, CFP-776)

**문제**: ADR-073 = Orchestrator 가 cross-repo state / assumption 단정 시 verify 의무 (Orchestrator 행위 한정). 그러나 lane agent 가 §9 evidence 작성 / Phase 0 mapping / corpus enumeration 시 write-time semantic truth 를 verify 없이 단언하는 영역 (pattern_count 3 누적, CFP-746/CFP-770) 은 ADR-073 scope 외 — internal lane self-write 미포함.

**결정**: ADR-082 (Write-time self-write verification mandate) 신설로 해당 gap 을 disjoint super-class layer 로 codify. ADR-073 ↔ ADR-082 = **disjoint 보완 관계**:

- **ADR-073** = Orchestrator 행위 한정 (cross-repo state + assumption 기술 시 `git fetch` + `git show origin/main:<path>` direct verify + `verified-via` annotation)
- **ADR-082** = internal lane agent self-write 한정 (§9 evidence / Phase 0 mapping / corpus enumeration write-time 에 작성 값 자체의 사실성 source direct verify)

두 layer 는 verify 대상 / 행위 주체가 disjoint — scope 침범 0. ADR-082 §결정 1 layer disjoint 4-layer 표 (ADR-073 / ADR-070 / ADR-082 / ADR-045 §D) 가 공통 anchor. 본 Amendment 는 cross-ref-only — ADR-073 §결정 1-8 / mechanism enumeration 의 의미 변경 없음.

### Amendment 2 — Transition trigger enum + sustained polling expansion (CFP-966)

**문제**: ADR-073 base §결정 1 (CFP-622) + Amendment 1 (CFP-776 ADR-082 cross-ref) 은 Orchestrator 가 cross-repo state / assumption 을 **단정 발화** 하는 순간 (한 turn 내 1회 event) 의 verify 의무를 codify. 그러나 long-running Orchestrator session 안에서 발생하는 **mid-flight parallel race incidence** 영역은 base + Amendment 1 scope 외 — session 시작 시점 (turn 0) state snapshot 이 stale 화 하면서 동일 session 안 후속 turn 의 단정 발화 도 동시 정합 invariant 가 깨진다.

Sentinel evidence (2026-05-18 KST same-day 2/2 occurrence):
- **CFP-953** (first incident): Epic CFP-882 Wave 4 Story-2 진행 시 label-based search (`gh issue list --label parent:CFP-882`) 만 수행 → CFP-932 (실제 Wave 4 Story-2 carrier, label `parent:CFP-699` 만 부착) miss → #953 brainstorm Phase 0/2 + spec PR #624 진행 후 발견 → #953 closed not_planned + spec deprecation PR #625. memory rule 6 신설 carrier (title-based search 의무).
- **CFP-946** (second incident, same day, 11분 gap): Epic CFP-946 brainstorm + Story-A (#957) PR #961 merged `06:42:12Z` → 11분 후 parallel session PR #962 `[CFP-946 option 1]` merged `06:53:30Z` "Closes #946" → Epic #946 CLOSED. Story-B (#958) ArchitectPL spawn 직전 HEAD re-pin 시 #962 검출. Story-B scope 분할 (declaration absorbed by #962 + mechanical layer carry-forward = #963 P2). memory rule 7 신설 carrier (Epic 진행 중 polling 의무).

**결정**: §결정 1 의 verify-before-assert mandate 를 **mid-flight transition state** 영역까지 expansion. 다음 3 요소 신설:

#### Amendment 2 §결정 1-A — Transition trigger enum 3종 (closed set)

Orchestrator (또는 subagent) 가 다음 transition 직전 시점에 추가 verify 의무 발화:

| ID | Transition trigger | 발화 시점 | Verify 의무 |
|----|---|---|---|
| `lane_spawn` | lane 진입 직전 (Requirements / Design / DesignReview / Develop / CodeReview / SecurityTest / IntegrationTest / PMO retro lane spawn) | Agent tool spawn 직전 | Issue body / current CFP context title-based search + Epic state poll + HEAD re-pin (`git ls-remote origin <branch>`) + HEAD compare (`gh api repos/.../compare/<prior>...<current>`) |
| `pr_open` | PR open 직전 (Phase 1 / Phase 2 / retro PR) | `gh pr create` 직전 | 동일 3-step (title-based search + Epic poll + HEAD compare) + sibling Story PR list cross-ref |
| `merge_transition` | PR merge 직전 (`gh pr merge` 직전) + merge 직후 (gate label / phase label transition 직전) | merge command 직전 + 직후 transition action 직전 | 동일 3-step + Epic state final poll (close eligibility check, ADR-077 §결정 4 정합) |

closed enum — 4번째 trigger 추가 시 Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합).

#### Amendment 2 §결정 1-B — Cold start session_start 보강

기존 SessionStart hook tier (`templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` + ADR-038 Amendment 2 §결정 9 TodoWrite preload pattern) 는 **turn 0 prompt-injection 단독 layer** — additionalContext 가 first user turn 직전 1회 발화. mid-flight parallel race (CFP-953 / CFP-946 evidence) 차단 영역은 cover 부족.

본 Amendment 2 는 cold start session_start 도 transition trigger 4번째 가상 entry 로 amplify:
- session 첫 turn additionalContext 안 **active CFP context list** + **open Epic state list** + **current branch HEAD vs origin/main delta** 3-item preload 의무 (SessionStart hook tier 위임 — Story-2 carrier `templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample` mechanical wire)
- additionalContext 안 layer 1 fallback 만 — actual sustained polling = §결정 1-C 영역

#### Amendment 2 §결정 1-C — Sustained in-session polling 의무 mandate (turn-0-only 한계 해소)

base §결정 1 (Orchestrator 단정 발화 시점 verify) + 본 Amendment §결정 1-A (transition trigger 3종) 의 **sustained polling** discipline normative anchor:

- Long-running session 안 **매 transition trigger 직전 HEAD SHA re-pin** 의무 — TodoWrite scratchpad / Story §0 Live Progress / `.claude-work/progress/<KEY>.md` 등 session state cache 가 stale (이미 polling 후 5+ min 경과) 일 가능성 무조건 가정
- mechanical polling source (parallel branch HEAD list + open Epic list + recent merged PR list) = sibling Story-2 CFP-967 mechanical wire (`scripts/check-parallel-work-sentinel.{sh,py}` + workflow event dispatch) 영역
- 본 ADR scope = behavioral directive + declarative anchor (§결정 1-A enum + §결정 1-B cold start ratchet + §결정 1-C polling mandate). actual lint script + workflow yaml + hook json sample = Story-2 carrier 위임 (declaration-only-Wave-1 patterns, ADR-082 §결정 6 + ADR-060 Amendment 10 §결정 24 precedent 답습)

#### Amendment 2 — mechanical_enforcement_actions[] 첫 entry append

본 Amendment 2 가 ADR-073 frontmatter `mechanical_enforcement_actions[]` 의 첫 row entry (`parallel-work-sentinel-pickup`) append 발의 — base + Amendment 1 의 `[]` empty Wave 1 → Amendment 2 의 1-entry warning-tier Wave 1 ratchet (ADR-040 Amendment 3 §결정 7.D self-application 정합).

| Wave | Status | Carrier |
|---|---|---|
| Wave 1 base (declaration mandate) | `mechanical_enforcement_actions: []` | CFP-622 (ADR-073 base, 2026-05-14) |
| Wave 1 + Amendment 1 (ADR-082 cross-ref) | `mechanical_enforcement_actions: []` (unchanged) | CFP-776 (Amendment 1, 2026-05-17) |
| **Wave 1.5 + Amendment 2 (declarative anchor entry)** | `mechanical_enforcement_actions: [parallel-work-sentinel-pickup]` (warning tier) | **CFP-966 (본 Amendment 2, 2026-05-18) — declarative anchor only** |
| Wave 1.6 + Story-2 mechanical wire | (entry unchanged, status warning → blocking-on-pr 자동 승격 trigger 활성) | CFP-967 (Story-2 mechanical wire, sequential — Story-1 merge 후) |
| Wave 2 (recurrence count ≥ 3 자동 승격) | (entry current_tier: blocking-on-pr 전환) | post-CFP-967 follow-up CFP (recurrence.threshold=3 auto-firing) |

#### Amendment 2 — Disjoint scope cross-ref (Edge 3 정합)

본 Amendment 2 는 ADR-082 Amendment 1 (CFP-841 Phase 1 declare — write-time self-write verification scope 2(a) corpus-claim-verify + scope 2(d) cross-plugin-ownership-verify deferred-followup) 과 **disjoint scope**:

- **ADR-082 Amendment 1** = internal lane agent self-write **write-time** semantic truth verify (corpus annotation + cross-plugin ownership) — 작성 값 자체의 사실성 source verify
- **ADR-073 Amendment 2** (본) = Orchestrator **transition state** verify (lane spawn / PR open / merge transition 직전 mid-flight parallel race state poll) — write-time 영역 외, session state cache staleness 영역

ADR-082 §결정 1 layer disjoint 4-layer 표 anchor 정합 — 두 Amendment 가 별 layer 안 ratchet 강화 진행, scope 침범 0건. 본 Amendment 2 본문 자체 안 ADR-082 cross-ref 영역 변조 0 (Amendment 1 disjoint 보완 관계 그대로 보존).

#### Amendment 2 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 2 scope = §결정 1-A/1-B/1-C 강화 방향 only (transition trigger enum 추가 + cold start 보강 + sustained polling mandate). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1 동형 precedent).

### Amendment 3 — worktree-first self-ownership verify 3-tuple (CFP-689)

**문제**: ADR-040 worktree-first normative (Amendment 3·5·6 §결정 7.D 4 evidence-check entry blocking-on-pr) 가 만든 토폴로지 = **multi-worktree distributed local state** (동일 lane branch 가 N 개 isolated worktree `${HOME}/.claude/worktrees/<repo>/cfp-NNN[-suffix]` 에 분산). 산업 표준 4-layer staleness hierarchy (Bazel hermeticity: source tree / network / clock / process) 와 동형이되 **5th layer "spatial dimension (multi-worktree distributed local state)"** 로 확장된 codeforge-specific 도메인. 단일-worktree 멘탈모델 (`C:/workspace/mclayer/<repo>/`) 로는 자기 세션이 dedicated worktree 에서 만든 commit 도 외부 commit 처럼 보인다 — **자기 세션 자체 산출물을 외부 parallel session 으로 오인하는 self-confusion**.

memory rule 6 (title-based search) + rule 7 (Epic state poll) + Amendment 2 transition trigger enum 3종 + cold start session_start 은 **detection layer** only — worktree-first 환경 안 detection 양성 직전 self-ownership verify 선행 layer 가 governance 안 부재. 이 verification layer 부재가 false-positive 의 force-push war / 잘못된 stand-down / 중복 spawn 을 만드는 systemic root.

**Sentinel evidence** (2026-05-19~20 KST single session 3 occurrences, pattern_count 3 reach):

- **Occurrence #1 — CFP-1026 brainstorm STAND-DOWN false-positive** (2026-05-19): Phase 0 4-agent parallel context fetch 직후 본 session 자기 산출물을 외부 work 으로 오인 → STAND-DOWN 발화 → 검증 후 false-positive 확인 → resume.
- **Occurrence #2 — CFP-681 cfp-1014 dup worktree** (2026-05-19~20): RequirementsPL 중복 spawn — authoritative `cfp-681-s2` worktree 의 자기 work commit `f39b221` 을 parallel session 산출물로 mis-flag → dup worktree setup → 검증 후 self-confusion 확인 → dup prune.
- **Occurrence #3 — CFP-681 ArchitectPL Phase 3 자기 commit mis-flag** (2026-05-20): ArchitectPL verdict packet 안 자기 ArchitectAgent commit `00b7d8a` 를 `parallel_session_conflict` 로 mis-flag — **subagent 도 multi-worktree self-confusion 영역에서 보이는 패턴 입증**. Orchestrator 가 subagent verdict 를 final source of truth 로 취급 시 self-confusion contagion (Orchestrator → subagent → Orchestrator 재반영 cycle).

#### Amendment 3 §결정 1-A 추가 — Transition trigger enum 4번째 entry (closed-set ratchet)

Amendment 2 §결정 1-A 의 transition trigger enum 3종 (`lane_spawn` / `pr_open` / `merge_transition`) + cold start `session_start` (Amendment 2 §결정 1-B) 에 **4번째 entry `worktree_lane_spawn`** 추가 (closed-set ratchet 강화, Amendment 2 §결정 1-A precedent 답습):

| ID | Transition trigger | 발화 시점 | Verify 의무 |
|----|---|---|---|
| `lane_spawn` (Amendment 2) | lane 진입 직전 (Requirements / Design / DesignReview / Develop / CodeReview / SecurityTest / IntegrationTest / PMO retro lane spawn) | Agent tool spawn 직전 | Amendment 2 §결정 1-A 3-step (title-based search + Epic poll + HEAD compare) |
| `pr_open` (Amendment 2) | PR open 직전 (Phase 1 / Phase 2 / retro PR) | `gh pr create` 직전 | 동일 3-step + sibling Story PR list cross-ref |
| `merge_transition` (Amendment 2) | PR merge 직전 + merge 직후 gate label / phase label transition | merge command 직전 + 직후 transition action 직전 | 동일 3-step + Epic state final poll |
| **`worktree_lane_spawn` (Amendment 3, 신규)** | **worktree-first lane spawn 직전 (`Agent` tool 호출 prompt 안 worktree path 주입 직전)** | **lane spawn 직전 + subagent verdict `parallel_session_conflict` 발화 직후** | **§결정 1-D self-ownership verify 3-tuple (path-based, 아래)** |
| **`fix_iter_start` (Amendment 5, 신규)** | **§10 FIX Ledger row append 직전 (FIX iter N > 0, 즉 N=1 첫 FIX iter 부터)** | **§10 row write + lane re-spawn 직전** | **§결정 1-E main HEAD pin verify (아래) + Amendment 2 §결정 1-A 3-step 재실행** |
| **`sibling_story_handoff` (Amendment 6, 신규)** | **agent / subagent 가 sibling Story (동일 Epic 안 sequential / parallel Story) 의 진행 상태 / scope / artifact ownership 을 단정 발화 직전** | **chief author / Analyst / Researcher / PL deputy spawn prompt 안 sibling Story 인용 직전 + verdict packet sibling Story state claim 직전** | **§결정 1-G sibling Story state polling primitive (아래) — 3-step `gh issue view <sibling> --json state,labels,closedAt` + `gh pr list --search "head:cfp-<sibling>"` + Epic parent `gh issue view <epic> --json subIssues` cross-check** |
| **`stale_local_main_checkout` (Amendment 7, 신규)** | **Orchestrator 가 main worktree (또는 본 session 시작 시점 checkout) 에서 src/* / docs/* / inter-plugin-contracts/* / ADR / Change Plan / Story 본문 file Read 시 working tree HEAD 가 origin/main 보다 stale (≥ N commits behind 또는 sibling session merge 후 미반영) 영역** | **session-start cold start + 매 lane spawn 직전 pre-Read pre-flight + chief / Analyst / Researcher claim 을 working tree file 과 대조 직전** | **§결정 1-I main checkout divergence detection primitive (아래) — `git fetch origin && git rev-parse origin/main vs HEAD` divergence ≥ threshold (default 1) 시 fresh worktree (EnterWorktree) 재진입 의무 + Read ground truth = `git show origin/main:<path>` direct fetch (working tree file 우회)** |
| **`mcp_token_expired_mid_flight` (Amendment 8, 신규)** | **MCP server (`mcp__plugin_*`, `mcp__github__*`) 인증 token TTL (OAuth ~1hr) expiry mid-flight 영역 — 6 parallel agent dispatch 후 token 전부 expired sentinel reproduction (CFP-1146 Epic-A W5)** | **lane-spawn / MCP-direct work 시작 직전 token freshness pre-flight + 다회 parallel dispatch 직전 + long-running session 안 매 lane re-spawn 직전** | **§결정 1-K MCP token freshness verify primitive (아래) — token TTL threshold (default 15분 잔여) 미만 시 사용자 `/mcp` 재인증 요청 의무 + agent spawn prompt 안 `mcp_token_freshness_verified: bool` field 검증** |
| **`label_change` (Amendment 9, 신규)** | **cross-repo label state mutation event 영역 — wrapper repo Story Issue `phase:*` / `gate:*` / `hotfix-bypass:*` label change ↔ impl repo Phase 2 PR label change 의 bidirectional sync (CFP-1302 D-4 chief tie-break dissent carry-over F2 carrier, sentinel-driven 아닌 ratchet 확장 carrier)** | **(a) wrapper repo Story Issue label change event (`issues.labeled` / `issues.unlabeled`) 직전 + 직후 (b) impl repo Phase 2 PR label change event (`pull_request.labeled` / `pull_request.unlabeled`) 직전 + 직후 (c) `cross-repo-label-sync.yml` workflow self-application 직전 (d) `gh api repos/<org>/<repo>/issues/<N>/labels` direct call 직전** | **§결정 1-M cross-repo label state verify-before-assert primitive (아래) — 4-step: `git fetch origin main` + `gh api` direct verify (sender + receiver 양 verify) + Story §14 + active_sessions[] dual-source AND + `verified-via` annotation 의무 + §결정 1-N T-2 self-trigger 4-pattern AND guard invariant (sender.type early-exit / actor-allowlist / `[skip-cross-repo-sync]` marker / idempotent diff)** |

closed enum — **10번째 trigger 추가 시** Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). open_extension: false.

#### Amendment 3 §결정 1-D — Self-ownership verify 3-tuple (path-based, 사용자 prompt identity-based 대안 채택)

`worktree_lane_spawn` transition 직전 + subagent verdict `parallel_session_conflict` 발화 시점에 다음 3-tuple verify 의무 (path-based, ResearcherAgent + FeasibilityAgent 통합 권장 채택 — Solo-dev 환경 identity-based 식별력 0 회피):

**3-tuple verify primitive** (atomic group — 3-step 동시 수행, 부분 PASS 허용 fallback rule 동반):

| ID | Verify check | 실행 cmd | PASS 조건 | Fallback rule |
|----|---|---|---|---|
| **(a) cwd ↔ worktree path 일치** | 현재 작업 worktree path 가 git worktree list 안 등록 entry 와 정확 일치 | `git rev-parse --show-toplevel` vs `git worktree list --porcelain` | string equality (path normalize: forward-slash `/` + lowercase drive-letter `c:` `c:/users/...`) | normalize 후 mismatch 시 (a) FAIL → (c) backstop |
| **(b) HEAD lineage ↔ session reflog membership** | HEAD commit lineage 가 본 session reflog 안 단일 선형 (자기 산출물 입증) | `git reflog show <branch> --all` + `git log <commit> --oneline` cross-check | reflog membership = true (본 session 안 commit chain 추적 가능) | long-Phase-gap reflog 90d GC (git default `gc.reflogExpire=90 days`) 시 (b) FAIL → **(a)+(c) 2-source AND fallback** |
| **(c) worktree list + reflog 2-source AND** | `git worktree list --porcelain | grep <branch>` 출력 + reflog 양 source AND 정합 | `git worktree list --porcelain` parse `branch` field + reflog entry exists | 양 source PASS = self-ownership verify TRUE | (a) FAIL OR (b) FAIL OR (c) FAIL 시 → parallel session verdict (memory rule 6/7 detection layer 인계) |

**Edge case handling**:
- **detached HEAD** (branch reflog 없음): `branch` field 부재 → (b) 자동 skip → **(a)+(c) 2-source AND fallback** (PASS 조건 = (a) PASS AND (c) PASS — branch field 없을 시 detached HEAD log line `(detached HEAD ...)` 검증).
- **anonymous worktree** (`branch` field 부재 — `git worktree add --detach` path): self-ownership verify 불가능 영역 → **forcing function**: "anonymous worktree 안 lane spawn 금지" (codeforge worktree convention violation — ADR-040 §결정 1 named worktree mandate 정합). detection 시 즉시 ABORT + named branch worktree 재생성 의무.
- **path normalization**: Windows drive-letter case 변동 (`C:/` vs `c:/`) + slash direction (`/` vs `\`) → canonical form = **lowercase drive + forward-slash** (`c:/users/...`). MSYS2 / Git Bash / WSL / native cmd.exe 전 환경 동형 보장.
- **signed commit GPG** + **CODEFORGE_SESSION_ID env 부재**: 사용자 prompt identity-based 3-tuple (cwd ↔ git config user.email / HEAD author ↔ session identity / `gh pr list head:<branch>`) 영역의 edge — 본 Amendment 3 path-based 채택으로 회피 (identity-based scope OUT, ResearcherAgent + FeasibilityAgent 통합 권장).

#### Amendment 3 §결정 1-E — Subagent verdict re-verify mandate (ADR-082 cross-ref)

Orchestrator 가 subagent verdict 안 `parallel_session_conflict` (또는 동형 발화 — `external_work_detected` / `cross_session_collision` / `stand_down_recommended` 등) 수신 시:

1. **즉시 ground-truth re-verify 의무** — `git worktree list --porcelain` + `git reflog show <branch>` direct execution (subagent 가 이미 수행했더라도 Orchestrator 자기 검증).
2. **subagent verdict ≠ final source of truth** — multi-worktree self-confusion 영역에서는 agent 도 mis-flag 패턴 입증 (Occurrence #3 sentinel evidence — ArchitectPL Phase 3 ArchitectAgent commit `00b7d8a` mis-flag). Subagent verdict 는 advisory annotation 만 — Orchestrator 가 self-ownership verify 3-tuple 결과를 ground truth 채택.
3. **3-tuple PASS (self-ownership TRUE) 시**: subagent verdict 의 `parallel_session_conflict` REJECT + continue (자기 산출물 정상 진행). FIX Ledger row append (`subagent_misflag_self_confusion` reason code) — Orchestrator 단독 §10 append 독점 (fix-event-v1 contract).
4. **3-tuple FAIL (self-ownership FALSE) 시**: subagent verdict 의 `parallel_session_conflict` 채택 + memory rule 6/7 detection layer 절차 진행 (title-based search + Epic state poll + HEAD compare).

**ADR-082 §결정 1 layer disjoint 4-layer 표 cross-ref 의무**:

- **ADR-082** = internal lane agent self-write **write-time** semantic truth verify (corpus annotation + cross-plugin ownership) — 작성 값 자체의 사실성 source verify
- **ADR-073 Amendment 3** (본) = Orchestrator **worktree-first self-confusion** verify (worktree_lane_spawn transition 직전 + subagent verdict re-verify) — 자기 산출물 영역의 verify 확장 (lane agent self-write 가 만든 commit 의 self-ownership verify 영역)

두 layer 는 verify 대상이 disjoint — ADR-082 = 작성 값의 source verify / 본 Amendment 3 = commit ownership 의 worktree topology verify. scope 침범 0. agent verdict packet `parallel_session_conflict` mis-flag 영역은 본 Amendment 3 의 §결정 1-E re-verify mandate 가 직접 cover (ADR-082 §결정 1 layer disjoint anchor 와 양립).

#### Amendment 3 §결정 1-F — Disjoint axis with #983 (reflog membership 1 bit)

본 Amendment 3 의 self-confusion sub-domain 은 #983 후보 (a)/(b) 의 real parallel cross-session collision sub-domain 과 **disjoint axis** (reflog membership 1 bit signal):

| 차원 | 진짜 parallel (cross-session conflict, #983 후보 (a)/(b) 영역) | self-confusion (within single session, **본 Amendment 3 영역**) |
|---|---|---|
| reflog membership | **본 세션 reflog 에 없는 commit** + 다른 worktree lineage 가 origin 에 독립 존재 | **본 세션 skeleton → lane commit 단일 선형** 이 multi-worktree 로 흩어진 산출물 |
| 1-bit signal | reflog membership = **false** | reflog membership = **true** |
| 적용 governance | memory rule 6/7 + ADR-073 Amendment 2 (detection layer) | **본 Amendment 3 (verification layer — detection 직전 self-ownership verify 선행)** |
| 처리 액션 | stand-down / re-spawn / merge-order 의뢰 | continue (자기 산출물 정상 진행) + subagent verdict reject |
| Carrier ESC | #983 (별 Story carrier, real parallel cross-session collision 영역) | CFP-689 (본 Story, plugin-codeforge#1038 carrier) |

본 Amendment 3 = #983 P1 ESC body 안 후보 (c) "ADR-073 Amendment 3 — shared workdir collision worktree-first invariant 강화" 의 정식 carrier. #983 후보 (a)/(b) (real parallel cross-session collision sub-domain) 는 별 Story carrier 영역 — 본 Amendment 3 scope 외, disjoint axis 명시 invariant.

#### Amendment 3 — Wave 1 declaration / Wave 2 mechanical wire 분리 (CFP-966/967 precedent 답습)

본 Amendment 3 = **declarative anchor only** (Wave 1, declaration-only, ADR-064 §결정 1 CFP scope unitary 정합). CFP-966 (declarative anchor) → CFP-967 (mechanical wire merged 2026-05-19) chain 완결 precedent 답습:

| Wave | Status | Carrier |
|---|---|---|
| Wave 1 Amendment 3 (declarative anchor) | `mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify]` (2 entry, warning tier, status: deferred-followup) | **CFP-689 (본 Amendment 3, 2026-05-20) — declarative anchor only** |
| Wave 2 sibling Story-2 mechanical wire | (entry status: deferred-followup → warning 전환) | **TBD 별 sub-CFP carrier** (`scripts/check-worktree-self-ownership.sh` + `scripts/lib/check_worktree_self_ownership.py` Python SSOT + `templates/github-workflows/worktree-self-ownership-verify.yml` + `.github/workflows/` byte-identical self-app + `templates/.claude/hooks/PreToolUse-worktree-self-ownership.json.sample` + `tests/scripts/check-worktree-self-ownership/test_worktree_self_ownership.bats` + label-registry-v2 신규 entry `hotfix-bypass:worktree-self-ownership-verify`) |
| Wave 3 (recurrence count ≥ 3 자동 승격) | (entry current_tier: warning → blocking-on-pr 전환) | post-Wave-2 follow-up CFP (recurrence.threshold=3 auto-firing — pattern_count 3 already reached 2026-05-19~20 sentinel evidence) |

#### Amendment 3 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 3 scope = §결정 1 본문 + Amendment 1+2 강화 방향 only (transition trigger enum 4번째 entry append + self-ownership verify 3-tuple 신설 + subagent verdict re-verify mandate). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2 동형 precedent). ADR-064 §self-application top-down ratchet 정합 (강화 방향 only — verify scope 확장).

### Amendment 4 — ADR-085 cross-ref disjoint complement (verify axis ↔ coordination axis, CFP-1041)

**문제**: ADR-073 (base + Amendment 1+2+3) 은 Orchestrator 행위 영역에서 cross-repo state / assumption verify (verify axis) 의무를 codify. 그러나 복수 Claude Code session 이 동일 repository / Story / branch 에서 동시 작업할 때 ownership 결정 / 분담 / handoff coordination (coordination axis) 영역은 ADR-073 scope 외 — verify 가 모두 충족되어도 ownership 미결정 시 parallel race 발생, ownership 결정 후에도 verify 미수행 시 false claim 가능 (둘 다 필요한 orthogonal layer).

**결정**: ADR-085 (Multi-session collaboration protocol — `active_sessions[]` + lane-entry sentinel + rebase merge 우선 + handoff baton transfer) 신설로 coordination axis layer 추가. ADR-073 ↔ ADR-085 = **disjoint complement** 관계:

- **ADR-073** = Orchestrator cross-repo state / assumption verify 한정 (verify axis, post-hoc verify)
- **ADR-085** = 복수 session ownership / 분담 / handoff coordination 한정 (coordination axis, pre-hoc cross-session)

ADR-085 §결정 1 5-layer disjoint 표가 공통 anchor (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row Multi-session coordination 신설). 본 Amendment 4 는 §결정 1 lane-entry sentinel 4-step polling 의 **4번째 source** (`active_sessions_check`) cross-ref-only append — 본문 §결정 1-8 + Amendment 1-3 mechanism 의미 변경 0 (ADR-085 §결정 3 cross-ref-only Amendment, ADR-082 Amendment 1 ADR-073 cross-ref pattern verbatim 답습).

post-rebase amendments[] sequence = [1, 2, 3 (CFP-689 worktree-first self-ownership), 4 (본 CFP-1041 ADR-085 coordination)] consecutive. 본 carrier 진행 중 origin/main 으로 CFP-689 (PR #1043, sibling escalation #1038 actual carrier) advance — dogfooding ADR-085 본 carrier 가 codify 하는 `parallel_session_shared_workdir_collision` pattern (9th+ parallel race lineage single session evidence: CFP-953/946/949/932/954/991/967/1014 + 본 CFP-1041 진행 중 CFP-689 race) verbatim 시연.

#### Amendment 4 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 4 scope = cross-ref-only append (mechanism 의미 변경 0, scope 확장 / 강화 0). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2+3 동형 precedent). ADR-064 §self-application top-down ratchet 정합.

### Amendment 5 — `fix_iter_start` transition trigger 5번째 entry (FIX iter 시점 main HEAD pin verify, CFP-1102)

**날짜**: 2026-05-20

#### 동기

CFP-1087 FIX iter 1 진행 중 CFP-1086 main이 1시간 안 5번 cascade advance (S1 06:46Z → S3 07:37Z → S4 07:41Z → S5 07:49Z, plugin.json 5.96 → 5.97 → 5.98 → 5.99 점진 ratchet). 본 carrier force-push (`60cdaa5`, 5.99.0) 직후 main S5 cascade → 5.99.0 main 점유 → 본 carrier CONFLICTING. FIX iter 2 cherry-pick + 5.99 → 5.100 ratchet 의무.

**Pattern_count 2 reach** (PMOAgent retro corpus enumeration):
- Pre-flight verify working tree stale — CFP-953 + CFP-1087 (working tree cache 영역 origin/main HEAD vs gh api ?ref=main divergence)
- main cascade race during FIX iter — CFP-1087 sentinel (1 sample 신규, 영역 super-class shared with working tree stale)

ADR-045 §D-9 Mandatory framing 정합 — HIGH escalation `adr_draft_emitted` (본 Amendment 5 carrier).

#### §결정 1 expansion — `fix_iter_start` transition trigger 5번째 entry (closed-set ratchet)

Amendment 2/3 §결정 1-A precedent 답습 (transition trigger enum closed-set ratchet 강화). 본 Amendment 5 = 5번째 entry append.

**5번째 trigger 정의**:

| Field | Value |
|---|---|
| ID | `fix_iter_start` |
| Transition trigger | §10 FIX Ledger row append 시점 + FIX iter N > 0 (즉 N=1 첫 FIX iter 부터 적용) |
| 발화 시점 | §10 row write 직전 + 후속 lane re-spawn 직전 (양 시점 모두 verify 의무) |
| Verify 의무 | §결정 1-E main HEAD pin verify (아래) + Amendment 2 §결정 1-A 3-step (title-based search + Epic poll + HEAD compare) 재실행 |

closed enum — 9번째 trigger 추가 시 Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). open_extension: false.

#### §결정 1-E — Main HEAD pin verify (FIX iter trigger 영역)

`fix_iter_start` transition 시점에 다음 verify 의무 (memory rule 7 `feedback-verify-pin-head-sha` declarative cross-ref normative anchor):

**Pin verify primitive** (3-step atomic group):

| Step | Verify command | PASS 조건 | Fallback rule |
|---|---|---|---|
| 1. fetch | `git -C <worktree> fetch origin <base-branch> --quiet` | exit 0 | fetch 실패 시 advisory warning + cached HEAD 사용 (graceful degradation) |
| 2. remote HEAD pin | `gh api repos/<owner>/<repo>/git/refs/heads/<base> --jq '.object.sha'` | SHA returned, 7+ chars | API 실패 시 `git rev-parse origin/<base>` fallback |
| 3. local cache cross-check | `git -C <worktree> rev-parse origin/<base>` vs step 2 output | byte-identical | divergence detect 시 fetch 재실행 + step 2/3 재verify |

3-step PASS 조건 모두 충족 시 — pinned HEAD SHA 영역 §10 FIX Ledger row `verified-via` annotation 의무. 미충족 시 — FIX iter 진행 중단 + advisory escalate (사용자 / Orchestrator 결정 영역).

#### §결정 1-F — FIX iter trigger 영역 § Amendment 2 §결정 1-A 3-step 재실행 정합

Amendment 2 §결정 1-A 3-step (title-based search + Epic state poll + HEAD compare-sibling-commits) 영역 = `lane_spawn` / `pr_open` / `merge_transition` trigger 동일. `fix_iter_start` trigger 영역 동일 3-step 재실행 의무 — sustained in-session polling discipline (Amendment 2 §결정 1-B normative anchor) 정합. 본 §결정 1-F = 5번째 trigger 영역 본 3-step coverage 명시 only (3-step mechanism 의미 변경 0).

#### Amendment 5 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 5 scope = §결정 1 본문 + Amendment 1+2+3+4 강화 방향 only (transition trigger enum 5번째 entry append + main HEAD pin verify primitive 신설). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2+3+4 동형 precedent). ADR-064 §self-application top-down ratchet 정합 (강화 방향 only — verify scope FIX iter trigger 영역 확장).

## 관련 파일

- `docs/adr/ADR-RESERVATION.md` — row 73 (CFP-622)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — disjoint super-class (Amendment 1 cross-ref, CFP-776)
- `CLAUDE.md` — "결정 원칙" section + "Verify-before-trust 4-layer governance" 단락 ADR-073 cross-ref
- `skills/codeforge-brainstorm/SKILL.md` — Phase 0 자기 적용 의무 sub-section
- `.claude-plugin/plugin.json` — version bump (CFP-622 carrier MINOR)
- `CHANGELOG.md` — 5.53.0 entry + Strike #3 + Strike #4 sub-sections
- `mclayer/marketplace/.claude-plugin/marketplace.json` — codeforge entry mirrored field sync (PR1 #109 merged)
- `mclayer/codeforge-internal-docs/wrapper/{specs,plans,stories,change-plans}/CFP-622-*.md` — Story carrier (PR3 TBD)
- `mclayer/codeforge-internal-docs/wrapper/templates/{spec,plan}.md` — pre_lookup_evidence[] field 신설
- **Amendment 2 (CFP-966, 2026-05-18) 관련**:
  - `docs/evidence-checks-registry.yaml` — `parallel-work-sentinel-pickup` 신규 entry (warning tier, declaration-only-Wave-1, recurrence count 2 / threshold 3 / promotion_trigger auto_blocking)
  - `docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md` — narrative SSOT (sentinel batch + escalation matrix)
  - `docs/orchestrator-playbook.md` §3.5 — lane spawn 직전 polling 의무 enum + HEAD compare pattern
  - `docs/parallel-work/section-ownership.yaml` — ADR-073 file lock row append (Amendment 2 신설 carrier)
  - `mclayer/codeforge-internal-docs/wrapper/stories/CFP-966.md` — Story-1 declarative anchor (본 Amendment 2 carrier)
  - `mclayer/codeforge-internal-docs/wrapper/change-plans/CFP-966.md` — Change Plan (declarative)
  - **sibling Story-2**: CFP-967 mechanical wire (`scripts/check-parallel-work-sentinel.{sh,py}` + `templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample` + `templates/github-workflows/parallel-work-sentinel-check.yml` + `tests/bats/test_parallel_work_sentinel.bats`)
- **Amendment 3 (CFP-689, 2026-05-20) 관련**:
  - `docs/evidence-checks-registry.yaml` — `worktree-self-ownership-verify` 신규 entry (warning tier, declaration-only-Wave-1, recurrence count 3 / threshold 3 / promotion_trigger auto_blocking, sibling_dependencies: [CFP-689, TBD-Wave-2-sub-CFP])
  - `docs/domain-knowledge/domain/orchestrator-discipline/worktree-self-ownership-verify.md` — narrative SSOT 신설 (DomainAgent 지식 공백 해소 — Multi-worktree distributed local state 5th layer staleness + disjoint axis + 3 occurrences sentinel evidence + path-based 3-tuple verify primitive + edge case + subagent verdict re-verify mandate)
  - `docs/parallel-work/section-ownership.yaml` — ADR-073 file lock row append (Amendment 3 신설 carrier, Amendment 2 row CFP-966 와 section disjoint)
  - `CLAUDE.md` "Verify-before-trust 4-layer governance" 단락 — Amendment 3 (CFP-689) 1문장 inline append + `mechanical_enforcement_actions[]` 2 entry mention (ADR-012 cap 320 line budget verified — 315 → ~318 lines 예상)
  - `mclayer/codeforge-internal-docs/wrapper/stories/CFP-689.md` — Story-1 declarative anchor (본 Amendment 3 carrier — RequirementsPL 7-agent synthesis §2-6 + ArchitectAgent §3/§7/§11 final write)
  - `mclayer/codeforge-internal-docs/wrapper/change-plans/CFP-689.md` — Change Plan (declarative)
  - **sibling Story-2 (TBD 별 sub-CFP)**: mechanical wire (`scripts/check-worktree-self-ownership.{sh,py}` + `templates/.claude/hooks/PreToolUse-worktree-self-ownership.json.sample` + `templates/github-workflows/worktree-self-ownership-verify.yml` + `tests/scripts/check-worktree-self-ownership/test_worktree_self_ownership.bats` + label-registry-v2 신규 entry `hotfix-bypass:worktree-self-ownership-verify`)
  - **#729 future Amendment 4 disjoint 영역**: plugin-codeforge#729 (ADR-073 "Amendment 1" title 표기 — 슬롯 충돌, Amendment 4 로 재배정 의무, ContinuityAgent CRITICAL 발견). Glob false negative P1 영역 — 본 Amendment 3 self-ownership verify 3-tuple 영역과 section disjoint 보장 (Amendment 4 = `Glob false negative` 별 §결정 영역).

## 해소 기준

N/A — permanent policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — verify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. is_transitional: false (영구 정책).

### Amendment 6 — `sibling_story_handoff` transition trigger 6번째 entry (bidirectional verify-before-trust, CFP-1318)

**날짜**: 2026-05-23

#### 동기

Epic 안 복수 Story 가 sequential 또는 parallel 진행 시, agent / subagent (chief author / Analyst / Researcher / PL deputy) 가 sibling Story 상태 / scope / artifact ownership 단정 발화 영역이 base §결정 1 + Amendment 2/3/5 scope 외 — agent / subagent 가 spawn 직전 stale sibling state 를 ground truth 로 단정하는 anti-pattern.

**Sentinel evidence** (pattern_count 3 reach Mandatory per ADR-045 §D-9):
- **CFP-1226**: chief author (ArchitectAgent) 가 sibling Story ADR 결정 wording 을 stale 채로 carrier 본문 cite → DesignReviewPL 미catch (sibling = 다른 lane review scope) → merged 후 wording drift.
- **CFP-1269**: Analyst subagent prior art 인용 시 sibling Story 결정 사항 (이미 amended) 을 amend 직전 snapshot 으로 cite → chief synthesis stale.
- **CFP-1273**: Researcher subagent brainstorm Phase 0 context fetch 시 sibling Story scope (partial close / sub-Story 분기) 단정 → spec/plan stale assumption 박제 → Phase 1 ArchitectAgent 재cite contagion.

super-class = `sibling_story_stale_claim_at_handoff`. **bidirectional verify-before-trust** — Orchestrator 만 verify 시 chief stale 차단 불가, chief 만 verify 시 Orchestrator handoff stale 차단 불가.

#### §결정 1 expansion — `sibling_story_handoff` transition trigger 6번째 entry

Amendment 2/3/5 precedent 답습 (closed-set ratchet 강화). 본 Amendment 6 = 6번째 entry append.

| Field | Value |
|---|---|
| ID | `sibling_story_handoff` |
| Transition trigger | agent / subagent (chief / Analyst / Researcher / PL deputy) 가 sibling Story 진행 상태 / scope / artifact ownership 단정 발화 직전 |
| 발화 시점 | (a) chief / Analyst / Researcher spawn prompt 안 sibling Story 인용 직전 (b) PL verdict packet sibling Story state claim 직전 (c) brainstorm Phase 0 context fetch 시 sibling Story scope 단정 직전 |
| Verify 의무 | §결정 1-G primitive 3-step + Amendment 2 §결정 1-A 3-step 재실행 |
| Verify subject | **agent / subagent (확장 영역)** — Orchestrator 단독 영역 (base + Amd 1-5) 에서 확장. subject 확장 시 동등 mandate |
| Verify direction | **bidirectional** — Orchestrator → chief handoff direction + chief → Orchestrator verdict direction 양방향 |

closed enum — **9번째 trigger 추가 시** Amendment 강화 방향만. open_extension: false.

#### §결정 1-G — Sibling Story state polling primitive

`sibling_story_handoff` transition 시점 verify 의무 (memory rule 6 + rule 7 declarative cross-ref):

| Step | Verify command | PASS 조건 | Fallback |
|---|---|---|---|
| 1. sibling state pin | `gh issue view <sibling> --json state,labels,closedAt,updatedAt` | state field returned, updatedAt within session window (5+ min old → re-poll) | API 실패 시 advisory + cached state (graceful degradation) |
| 2. sibling PR head compare | `gh pr list --search "head:cfp-<sibling>" --state all --json number,state,mergedAt,headRefOid` | PR list returned (empty OK — sibling 미진입), merged 시 mergedAt vs session start 비교 | `gh pr list --label parent:CFP-<epic>` (memory rule 6) |
| 3. Epic parent sub-issue | `gh issue view <epic> --json subIssues` parse | sibling Story membership + state 일치 | `gh issue list --search "parent-issue:<epic>"` (memory rule 7) |

3-step PASS 시 — `verified-via: gh issue view <sibling> + gh pr list head + gh issue view <epic> subIssues` annotation 의무. 미충족 시 spawn 중단 + advisory escalate.

**Bidirectional catch protocol**:
- **Orchestrator → chief** (handoff): Orchestrator 가 chief spawn prompt 작성 직전 verify (sentinel #1 차단).
- **chief → Orchestrator** (verdict): chief / Analyst / Researcher / PL deputy 가 verdict packet sibling state claim 작성 직전 verify (sentinel #2/#3 차단).

양방향 모두 mandate — 단방향 catch 시 contagion 재발 risk.

#### §결정 1-H — agent vs subagent actor scope (ADR-039 inline whitelist boundary cross-ref)

base §결정 1 (Orchestrator subject 한정) → Amendment 6 (Orchestrator ∪ agent ∪ subagent). subject 확장 = verify mandate 동등 적용 (약화 0건, ADR-058 §결정 5 ratchet 정합).

신규 의무 영역:
- agent / subagent → Orchestrator verdict 안 sibling Story state claim = 의무 (본 Amendment 6 §결정 1-G, chief→Orchestrator direction).
- Orchestrator → chief spawn prompt 안 sibling Story 인용 = 의무 (본 Amendment 6 §결정 1-G, Orchestrator→chief direction).

#### Amendment 6 — Wave 1 declaration / Wave 2 mechanical wire 분리

`mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify]` (2 entry unchanged — Wave 1 retain, 3rd entry append 보류). Wave 2 별 sub-CFP carrier = `subagent-sibling-story-polling-evidence` warning-tier entry 신설 (recurrence count 3 / threshold 3 already reached / auto_blocking, sibling_dependencies: [CFP-1318, TBD-Wave-2]).

Wave 1 retain rationale: Researcher 권고 (spawn prompt grep heuristic false-negative risk, CFP-963 codex-network-scope-presence precedent). Amendment 5 (CFP-1102 fix_iter_start) 동일 Wave 1 declarative anchor only 답습 (precedent consistency).

#### Amendment 6 — Disjoint axis cross-ref

- **ADR-082**: write-time semantic truth verify (corpus / cross-plugin). 본 Amd 6 = sibling Story state verify. write-time input value ≠ sibling state handoff, axis disjoint.
- **ADR-085**: multi-session collaboration coordination (pre-hoc cross-session). 본 Amd 6 = single session 안 agent/subagent sibling Story polling (verify axis, post-hoc cross-Story). ownership coordination ≠ sibling state polling, axis disjoint.
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 6 = pattern_count 3 reach Mandatory carrier (CFP-1226+1269+1273), 첫 적용 사례 of family.

#### Amendment 6 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 6 scope = 본문 + Amendment 1+2+3+4+5 강화 방향 only (enum 6번째 entry append + sibling state polling primitive 신설 + subject scope 확장 Orchestrator → Orchestrator ∪ agent ∪ subagent + bidirectional catch protocol 신설). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2+3+4+5 동형 precedent). ADR-064 §self-application top-down ratchet 정합.

### Amendment 7 — `stale_local_main_checkout` transition trigger 7번째 entry (Orchestrator pre-Read divergence detection mandate, CFP-1319)

**날짜**: 2026-05-24

#### 동기

Orchestrator 가 main worktree (또는 본 session 시작 시점 checkout) 에서 src/* / docs/* / inter-plugin-contracts/* / ADR / Change Plan / Story 본문 file Read 시 working tree HEAD 가 origin/main 보다 stale 인 영역 — sibling session merge 후 미반영 또는 cold session 진입 시점 cached snapshot — 안에서 chief / Analyst / Researcher claim 을 working tree file 과 대조 시, 정합 claim 을 hallucination 으로 오분류하는 anti-pattern. Orchestrator 자가 catch 시 false-positive `chief_hallucination` 진단 발화 + 정정 비용.

**Sentinel evidence** (pattern_count 3+ reach Mandatory per ADR-045 §D-9, super-class `stale_local_main_checkout`):
- **Epic-A CFP-1146 W5-S14 init**: Orchestrator main checkout stale HEAD (session-start snapshot, sibling session merge 후 미반영) → chief ADR §결정 wording claim 을 working tree file 과 대조 → 정합인데 hallucination 으로 오분류 → fresh worktree EnterWorktree 재verify 후 catch.
- **Epic-A CFP-1146 W5-S16 init**: 동일 패턴 (W5-S15 sibling merge 후 main HEAD 미반영 영역 안 Analyst claim hallucination 오분류) → fresh worktree 재verify 후 catch.
- **CFP-1318 본 session 다회**: brainstorm Phase 0 / Phase 2 packet 작성 시 main HEAD stale (Orchestrator 자가 catch — fresh worktree 재verify 메커니즘 작동 결과, 사용자 catch 0회).

super-class = `stale_local_main_checkout`. **Orchestrator self-Read direction** — base + Amendment 1-6 의 verify subject scope (Orchestrator + agent + subagent) 안 누락된 channel = Orchestrator self-Read (working tree file 직접 Read 시 stale snapshot anti-pattern).

#### §결정 1 expansion — `stale_local_main_checkout` transition trigger 7번째 entry

Amendment 2/3/5/6 precedent 답습 (closed-set ratchet 강화). 본 Amendment 7 = 7번째 entry append.

| Field | Value |
|---|---|
| ID | `stale_local_main_checkout` |
| Transition trigger | Orchestrator 가 main worktree (또는 본 session 시작 시점 checkout) 안 working tree file 을 ground truth 로 Read 직전 (chief / Analyst / Researcher claim 대조 + ADR / Change Plan / Story / contract file Read 영역 포함) |
| 발화 시점 | (a) session-start cold start 직후 첫 Read 직전 (b) 매 lane spawn 직전 working tree file Read pre-flight (c) chief / Analyst / Researcher verdict 안 claim 을 working tree file 과 대조 직전 (d) sibling session merge 가능성 영역 (Epic in-flight + 동시 session activity 감지) Read 직전 |
| Verify 의무 | §결정 1-I main checkout divergence detection primitive (아래) + Amendment 2 §결정 1-A 3-step 재실행 (sibling session activity 감지 시) |
| Verify subject | **Orchestrator** (base + Amendment 1-5 + 본 Amendment 7) + agent / subagent (Amendment 6 + 본 Amendment 7 — working tree file Read 시 동등 mandate) |
| Verify direction | **self-Read direction** (Orchestrator/agent/subagent → working tree file Read) — base direction (Orchestrator → cross-repo state) + Amendment 6 bidirectional (chief↔Orchestrator) 보완 |

closed enum — **9번째 trigger 추가 시** Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). open_extension: false.

#### §결정 1-I — Main checkout divergence detection primitive

`stale_local_main_checkout` transition 시점 verify 의무 (memory `feedback_worktree_first_not_parallel_session` declarative cross-ref):

| Step | Verify command | PASS 조건 | Fallback |
|---|---|---|---|
| 1. origin fetch | `git fetch origin --quiet` | exit 0 | network 실패 시 advisory + cached state (graceful degradation) |
| 2. HEAD vs origin/main divergence | `git rev-list --count HEAD..origin/main` | count `≤` divergence_threshold (default 1) | count `>` threshold 시 (3) escalate |
| 3. fresh worktree mandate | EnterWorktree (fresh-from-origin) 재진입 의무 OR Read ground truth = `git show origin/main:<path>` direct fetch (working tree file 우회) | 새 worktree HEAD `==` origin/main 또는 direct fetch ground truth 채택 | 양 path 모두 실패 시 ABORT + 사용자 escalate |

3-step PASS 시 — `verified-via: git fetch + git rev-list HEAD..origin/main count=N + EnterWorktree / git show origin/main:<path>` annotation 의무. 미충족 시 Read 단정 발화 차단 + advisory escalate.

**Divergence threshold rationale**: default `1` commit behind (보수적) — sibling session merge 직후 catch. consumer overlay 안 `project.yaml verify.local_main_divergence_threshold: <int>` 확장 허용 (축소 불가, ADR-027 Amendment 5 consumer overlay scope 정합).

**Working tree file Read 우회 path (ground truth direct fetch)**:
- `git show origin/main:<path>` = origin/main snapshot 의 file content stdout fetch. cached working tree 와 disjoint, network round-trip 없음 (object pool 안 fetch 완료 후 local).
- 우회 path 선호 = fresh worktree EnterWorktree 비용 회피 시 1 회 Read 영역 단발성 verify.
- 다회 Read / 편집 / Phase 1 PR 작업 영역 = EnterWorktree fresh-from-origin 정합 (worktree-first invariant ADR-040 §결정 1).

#### §결정 1-J — Inline whitelist boundary cross-ref (ADR-039)

ADR-039 Inline whitelist 4-entry (사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report) 안 **Read-only Q&A 답변** entry 의 Read 영역이 본 Amendment 7 의무 영역과 교집합 — Orchestrator 가 사용자 질문 답변 시 working tree file inline Read = self-Read direction 정합. 본 Amendment 7 의무 적용 = ADR-039 inline whitelist scope 안 Read action 도 §결정 1-I primitive 의무 (whitelist = "agent spawn 회피" 만, "verify 회피" 아님 — disjoint axis).

#### Amendment 7 — Wave 1 declaration / Wave 2 mechanical wire 분리

`mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify]` (2 entry unchanged — Wave 1 retain, 3rd / 4th entry append 보류). Wave 2 별 sub-CFP carrier = `stale-local-main-checkout-divergence-check` warning-tier entry 신설 (recurrence count 3+ already reached / auto_blocking, sibling_dependencies: [CFP-1319, CFP-1384]).

Wave 1 retain rationale: Amendment 5/6 (CFP-1102 fix_iter_start + CFP-1318 sibling_story_handoff) 동일 Wave 1 declarative anchor only 답습 (precedent consistency). spawn prompt grep heuristic / hook PreToolUse Read intercept 영역 false-negative risk (CFP-963 codex-network-scope-presence precedent 답습).

#### Amendment 7 — Disjoint axis cross-ref

- **ADR-082**: write-time semantic truth verify (corpus / cross-plugin). 본 Amd 7 = Read-time working tree file ground truth verify. write-time input value ≠ Read-time working tree snapshot, axis disjoint.
- **ADR-085**: multi-session collaboration coordination (pre-hoc cross-session ownership). 본 Amd 7 = single session 안 working tree divergence detection (verify axis, post-hoc local state). ownership coordination ≠ working tree divergence, axis disjoint.
- **Amendment 3** (`worktree_lane_spawn`): worktree-first self-ownership verify 3-tuple (path-based, cwd ↔ worktree path). 본 Amd 7 = working tree HEAD vs origin/main divergence (temporal axis). path-based topology ≠ temporal divergence, axis disjoint.
- **Amendment 6** (`sibling_story_handoff`): bidirectional sibling Story state polling (chief↔Orchestrator). 본 Amd 7 = Orchestrator self-Read working tree file (single direction). sibling state polling ≠ self-Read divergence, axis disjoint.
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 7 = pattern_count 3+ reach Mandatory carrier (Epic-A W5-S14 + W5-S16 + CFP-1318 다회), 2번째 적용 사례 of family (Amendment 6 첫 사례 후).

#### Amendment 7 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 7 scope = 본문 + Amendment 1+2+3+4+5+6 강화 방향 only (enum 7번째 entry append + main checkout divergence detection primitive 신설 + ADR-039 inline whitelist boundary cross-ref). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2+3+4+5+6 동형 precedent). ADR-064 §self-application top-down ratchet 정합.

### Amendment 8 — `mcp_token_expired_mid_flight` transition trigger 8번째 entry (MCP server auth token TTL freshness pre-flight verify, CFP-1348)

**날짜**: 2026-05-24

#### 동기

MCP server (`mcp__plugin_atlassian_atlassian__*` / `mcp__github__*` / 등) 인증 token TTL (OAuth ~1hr 기준) expiry mid-flight 영역 — Orchestrator 가 다회 parallel agent dispatch 후 ~3-5분 안 token 전부 expired sentinel reproduction (CFP-1146 Epic-A W5 다회 발생). 본 anti-pattern 차단:
- 6 parallel `Agent` tool dispatch (MCP server 활용) → ~3-5분 후 전부 fail (token expired)
- 사용자 catch + `/mcp` 재인증 의무 → 다회 round-trip 비용
- agent spawn 시 token freshness assumption 단정 발화 (verify 부재)

**Sentinel evidence** (pattern_count 2 reach, conservative — 본 session evidence base, 외부 session evidence 부재):
- **CFP-1146 W5-S15/S16/S17** 6 parallel dispatch token expiry — 전부 ~3-5분 안 fail, 사용자 /mcp 재인증 후 follow-up dispatch 정상 (~53min 추가 비용).
- (외부 session reproduction = TBD, pattern_count 3 reach 시 본 Amendment ratchet 추가 강화 평가).

super-class = `mcp_session_auth_layer_staleness`. **auth layer staleness** — Amendment 7 의 git layer staleness (working tree HEAD vs origin/main divergence) 와 axis disjoint (auth ↔ git layer disjoint, 양 staleness sub-domain).

#### §결정 1 expansion — `mcp_token_expired_mid_flight` transition trigger 8번째 entry

Amendment 2/3/5/6/7 precedent 답습 (closed-set ratchet 강화). 본 Amendment 8 = 8번째 entry append.

| Field | Value |
|---|---|
| ID | `mcp_token_expired_mid_flight` |
| Transition trigger | MCP server (`mcp__plugin_*`, `mcp__github__*`) 인증 token TTL expiry mid-flight 영역 — 6 parallel agent dispatch 후 token 전부 expired sentinel |
| 발화 시점 | (a) lane-spawn 직전 (MCP-direct work 활용 agent) (b) MCP-direct work 시작 직전 (`mcp__plugin_*` tool 호출 직전) (c) 다회 parallel dispatch 직전 (5+ agent batch spawn) (d) long-running session 안 매 lane re-spawn 직전 (cumulative session age threshold > 45분) |
| Verify 의무 | §결정 1-K MCP token freshness verify primitive (아래) |
| Verify subject | **Orchestrator** (base + Amendment 1-5 + Amendment 7 + 본 Amendment 8) + agent / subagent (Amendment 6 + 본 Amendment 8 — MCP-direct work 활용 영역 동등 mandate) |
| Verify direction | **pre-flight direction** (Orchestrator/agent/subagent → MCP server auth state verify) — base direction + Amendment 6 bidirectional + Amendment 7 self-Read 보완 |

closed enum — **9번째 trigger 추가 시** Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). open_extension: false.

#### §결정 1-K — MCP token freshness verify primitive

`mcp_token_expired_mid_flight` transition 시점 verify 의무:

| Step | Verify primitive | PASS 조건 | Fallback |
|---|---|---|---|
| 1. session age estimate | session 시작 시점 + 누적 elapsed time (rough estimate, OAuth TTL ~1hr 기준) | elapsed < 45분 (token TTL 15분 잔여 default threshold) | elapsed ≥ 45분 시 (3) 강제 진입 |
| 2. last MCP call success | 직전 MCP tool 호출 timestamp (5분 이내 success) | 5분 이내 success = freshness 유효 | 5분 초과 OR last call fail 시 (3) |
| 3. user re-auth request | 사용자 `/mcp` 재인증 요청 + verify | 사용자 confirm 후 follow-up MCP call success | 재인증 미실행 시 ABORT + advisory |

3-step PASS 시 — `verified-via: session age <X분 + last_mcp_call_success <Y분 ago` annotation 의무. 미충족 시 MCP-direct work 차단 + 사용자 escalate.

**Token TTL threshold rationale**: OAuth standard ~1hr TTL — 15분 잔여 default threshold (보수적, 다회 parallel dispatch 영역 safety margin). consumer overlay 안 `project.yaml verify.mcp_token_freshness_threshold_min: <int>` 확장 허용 (축소 불가, ADR-027 Amendment 5 consumer overlay scope 정합).

**6 parallel dispatch heuristic** (CFP-1146 Epic-A W5 sentinel reproduction 정합):
- 5+ agent batch spawn = high-risk mid-flight token expiry 영역 → 사전 token freshness verify 의무 강화 (default 15분 → 30분 잔여 threshold).
- 1-2 agent spawn = standard threshold 적용.

#### §결정 1-L — Agent spawn prompt `mcp_token_freshness_verified` field

agent / subagent spawn prompt 안 verify directive insertion:

```
[MCP TOKEN FRESHNESS]
mcp_token_freshness_verified: <bool>  # Orchestrator 가 §결정 1-K 3-step verify 수행 결과
mcp_session_age_estimate_min: <int>   # session 시작 후 누적 분
last_mcp_call_success_ago_min: <int>  # 직전 MCP tool 호출 success 후 경과 분
```

verdict packet 자체 검증 — false 시 spawn 중단 + 사용자 /mcp 재인증 요청 의무.

#### Amendment 8 — Wave 1 declaration / Wave 2 mechanical wire 분리

`mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify, subagent-sibling-story-polling-evidence]` (3 entry unchanged — Wave 1 retain, 4th entry append 보류). Wave 2 별 sub-CFP carrier = `mcp-token-freshness-precheck` warning-tier entry 신설 (recurrence count 2 / threshold 3 / promotion_trigger auto_blocking pending more sentinel evidence, sibling_dependencies: [CFP-1348, TBD-Wave-2]).

Wave 1 retain rationale: Amendment 5/6/7 (CFP-1102 fix_iter_start + CFP-1318 sibling_story_handoff + CFP-1319 stale_local_main_checkout) 동일 Wave 1 declarative anchor only 답습 (precedent consistency). SessionStart hook + script + bats fixture 영역 false-negative risk (token TTL heuristic estimate inherent, MCP server side TTL extension 외부 영역).

#### Amendment 8 — Disjoint axis cross-ref

- **ADR-082**: write-time semantic truth verify (corpus / cross-plugin). 본 Amd 8 = pre-flight MCP auth state verify. write-time input value ≠ MCP token TTL, axis disjoint.
- **ADR-085**: multi-session collaboration coordination (pre-hoc cross-session ownership). 본 Amd 8 = single session 안 MCP token TTL pre-flight (verify axis, pre-hoc auth state). ownership coordination ≠ MCP auth, axis disjoint.
- **Amendment 7** (`stale_local_main_checkout`): git layer staleness (working tree HEAD vs origin/main divergence). 본 Amd 8 = auth layer staleness (MCP token TTL). git ↔ auth layer disjoint, 양 staleness sub-domain (both addressed by separate triggers).
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 8 = pattern_count 2 reach (conservative, sentinel reproduction 본 session base), 3번째 적용 사례 of family (Amendment 6 첫 + Amendment 7 둘째 + 본 Amendment 8 셋째).

#### Amendment 8 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 8 scope = 본문 + Amendment 1+2+3+4+5+6+7 강화 방향 only (enum 8번째 entry append + MCP token freshness verify primitive 신설 + agent spawn prompt `mcp_token_freshness_verified` field 신설). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2+3+4+5+6+7 동형 precedent). ADR-064 §self-application top-down ratchet 정합.

### Amendment 9 — `stale-local-main-checkout-divergence-check` Wave 2 mechanical wire activation (5번째 mechanical_enforcement_actions[] entry, CFP-1384)

**날짜**: 2026-05-24

#### 동기

Amendment 7 (CFP-1319, 2026-05-23 merged) 가 `stale_local_main_checkout` transition trigger 7번째 entry 를 declaration-only-Wave-1 retain 상태로 도입. retain pattern 가정 (behavioral directive ADR-073 §결정 6 만으로 unconditional forcing function 달성) 이 **recursive dogfooding loop 안 systemic 으로 falsified**:

- **CFP-1333 single Story session 3-occurrence sentinel** (Amendment 7 sentinel 본문 cited): F-001 Phase 0 cold start (Orchestrator session-start cold start 시 fetch + divergence detection 누락, 6 commits behind 영역 안 RequirementsPL spawn → §2.1 verified_state_table GAP claim 잘못된 결론) + F-002 3-step same-session drift (`a1fb06b → c951199 → d24ab28` baseline pin 직후에도 stale, evidence_pre-trust 가 spawn 외 turn 사이에서 stale) + §9.1 DesignReview Codex 5/5 FP (external verifier own stale local checkout `bfc4806` 5 commits behind, 3rd-order reproduction)
- **CFP-1384 iter 1 RequirementsPL 7번째 reproduction**: packet baseline `6eb8112` 8 commits behind actual origin/main `bfa62f8` (CFP-1346 retro merge advance), RequirementsPL §2.1 verified_state_table 본인 검증 단계에서 catch
- **CFP-1384 ArchitectPL spawn 8번째 reproduction in-flight**: wrapper worktree HEAD `aacce0f` 4 commits behind actual origin/main `bb6f7d0` (CFP-1392 + CFP-1334 + CFP-1346 Phase 2 + CFP-1333 Phase 2 merged in-flight), ArchitectPL Phase 0 re-verify catch

**Pattern_count 8+ reach Mandatory** (ADR-045 §D-9 정합) — Issue body claim 5+ reach 이미 Mandatory framing, 본 ArchitectPL spawn 시점 8+ accumulate. retain pattern 의 "behavioral directive 만으로 충분" 가정 systemic 으로 wrong 입증 — mechanical wire (SessionStart hook + script chain + PR-time workflow + bats fixture + label-registry bypass channel) 활성 evidence-grounded essential.

#### §결정 — Wave 2 mechanical wire activation

본 Amendment 9 = Amendment 7 line 770 `TBD-Wave-2` placeholder 채우기 — declaration → mechanical wire active 전환의 atomic component file 집합. ADR-064 §결정 1 CFP scope unitary 정합 — Phase 1 declarative anchor + Phase 2 file impl 모두 단일 wire 의 구성 요소 (split 0). mcp-token-freshness-precheck Wave 1 declarative-only retain (CFP-1348) precedent 와 차이점: 본 carrier = Wave 2 자체이므로 declaration-only-Wave-1 stage 추가 도입 0, evidence-checks-registry entry `status: Active` 직접 도입 (deferred-followup 단계 미경유).

| 영역 | 활성 carrier | Phase |
|---|---|---|
| frontmatter `mechanical_enforcement_actions[]` 5번째 entry append (`stale-local-main-checkout-divergence-check`, closed-set ratchet 강화 4→5) | 본 Amendment 9 | Phase 1 |
| evidence-checks-registry warning-tier entry 신설 (17 field schema verbatim 답습, status: Active, recurrence count 8 / threshold 3 / promotion_trigger auto_blocking) | 본 Amendment 9 | Phase 1 |
| label-registry-v2 v2.53 → v2.54 MINOR bump (`hotfix-bypass:stale-local-main-checkout-divergence-check` 75번째 family member, ADR-108 §결정 3 description text count parity META self-application 2nd applied case) | 본 Amendment 9 | Phase 1 |
| evidence-check-registry-v1.md 변경 0 (이미 v1.3 CFP-963 / ADR-060 Amendment 14 merged 2026-05-19, 본 carrier schema field 추가 0 → version bump 불필요 — iter 2 F-003 absorb stale design assumption 정정) | N/A | N/A |
| SessionStart hook (`hooks/stale-local-main-checkout` polyglot extensionless + `hooks/hooks.json` matcher 2nd command append, async: false sequential 정합) | CFP-1384 Phase 2 | Phase 2 |
| script chain (`scripts/check-stale-local-main-checkout.sh` thin wrapper + `scripts/lib/check_stale_local_main_checkout.py` Python SSOT per ADR-061 + `scripts/check-baseline-pin-verify.sh` lane spawn lint) | CFP-1384 Phase 2 | Phase 2 |
| PR-time workflow (`templates/github-workflows/stale-local-main-checkout-divergence-check.yml` dual trigger pull_request + workflow_dispatch per production-cutover-evidence.yml D2 consensus 답습 + `.github/workflows/...yml` self-app byte-identical per ADR-005) | CFP-1384 Phase 2 | Phase 2 |
| bats fixture pair (`tests/scripts/test_check-stale-local-main-checkout.sh` ≥ 6 assertion T-1~T-6 + `tests/scripts/test_check-baseline-pin-verify.sh` ≥ 4 assertion T-7~T-8, RED→GREEN stash proof pattern per CFP-1334 §8.4) | CFP-1384 Phase 2 | Phase 2 |

#### Amendment 9 — Amendment 7 §결정 1-I primitive mechanical 실 enforcement

본 Amendment 9 = Amendment 7 §결정 1-I main checkout divergence detection primitive (3-step) 의 **mechanical 실 enforcement carrier**:

| Step | Verify command | mechanical wire 영역 |
|---|---|---|
| 1. origin fetch | `git fetch origin --quiet` | `scripts/lib/check_stale_local_main_checkout.py` subprocess.run (timeout 10s per EC-3, env override `CODEFORGE_STALE_FETCH_TIMEOUT_SEC`) |
| 2. HEAD vs origin/main divergence | `git rev-list --count HEAD..origin/main` | `scripts/lib/check_stale_local_main_checkout.py` divergence count integer parse (threshold default 1, env override `CODEFORGE_STALE_THRESHOLD`) |
| 3. fresh worktree mandate | plain stdout warning + EnterWorktree guidance + `git show origin/main:<path>` direct fetch fallback | `scripts/lib/check_stale_local_main_checkout.py` stdout emit (ADR-038 Amendment 3 §결정 11 plain stdout SSOT) + SessionStart hook (`hooks/stale-local-main-checkout`) 매 session start + /clear + /compact 직후 자동 발화 |

#### Amendment 9 — Disjoint axis cross-ref

- **ADR-082**: write-time semantic truth verify (corpus / cross-plugin). 본 Amd 9 = Read-time working tree file ground truth mechanical verify. write-time input value ≠ Read-time working tree snapshot, axis disjoint.
- **ADR-085**: multi-session collaboration coordination (pre-hoc cross-session). 본 Amd 9 = single session 안 working tree divergence mechanical detection (verify axis). ownership coordination ≠ working tree divergence, axis disjoint.
- **Amendment 3** (`worktree_lane_spawn`): worktree-first self-ownership verify 3-tuple (path-based). 본 Amd 9 = working tree HEAD vs origin/main divergence (temporal axis). path-based topology ≠ temporal divergence, axis disjoint.
- **Amendment 6** (`sibling_story_handoff`): bidirectional sibling Story state polling. 본 Amd 9 = single session self-Read working tree file. sibling state polling ≠ self-Read divergence, axis disjoint.
- **Amendment 7** (`stale_local_main_checkout` Wave 1 declarative): 본 Amd 9 = Wave 2 mechanical wire active 직접 후속 carrier (declaration → activation 정상 lifecycle).
- **Amendment 8** (`mcp_token_expired_mid_flight`): auth layer staleness. 본 Amd 9 = git layer staleness. git ↔ auth layer disjoint, 양 staleness sub-domain.
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 9 = pattern_count 8+ reach Mandatory carrier, 4번째 적용 사례 of family (Amendment 6 첫 + Amendment 7 둘째 + Amendment 8 셋째 + 본 Amendment 9 넷째).

#### Amendment 9 — META self-application 2nd applied case

ADR-108 §결정 3 `label-registry-frozen-baseline-count-parity` lint = description text count = raw active grep count post-append parity forcing function (CFP-1346 1st applied case). 본 carrier label-registry-v2 v2.54 신규 entry description text 안 "75번째 hotfix-bypass:* family member" wording 의무 — **META self-application 2nd applied case** (post-CFP-1346 v2.53 baseline raw active 74 + new = 75 정합, ADR-108 §결정 6 dogfood loop close).

#### Amendment 9 — Wave 2 mechanical wire status decision (Active vs deferred-followup)

본 carrier evidence-checks-registry entry `status: Active` 직접 도입 (deferred-followup 단계 미경유). **rationale**:
- mcp-token-freshness-precheck precedent (CFP-1348 Wave 1) = declaration-only-Wave-1 retain, Wave 2 별 carrier 미존재 시점 → `status: deferred-followup` 정합
- 본 carrier (CFP-1384) = Wave 2 mechanical wire 자체 (Amendment 9 + frontmatter + registry entry + label-registry + Phase 2 file impl atomic) → CFP scope unitary (ADR-064 §결정 1) 정합 — Wave 1 추가 stage 도입 0, Phase 2 = file impl 만 (declarative layer 무변경) → `Active` 직접 도입 정합

Active 진입 후 PR 누적 ≥ 20 + bypass 외 failure = 0 reach 시 (ADR-060 §결정 6 promotion criteria) 별 carrier 가 warning → blocking-on-pr tier 승격 평가 (본 carrier scope 외).

#### Amendment 9 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 9 scope = 본문 + Amendment 1+2+3+4+5+6+7+8 강화 방향 only (5번째 mechanical_enforcement_actions[] entry append + evidence-checks-registry warning-tier entry 신설 status: Active + label-registry-v2 v2.54 MINOR + SessionStart hook + script chain + PR-time workflow + bats fixture pair 전체 atomic mechanical wire activation). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1+2+3+4+5+6+7+8 동형 precedent). ADR-064 §self-application top-down ratchet 정합.

---

### Amendment 10 — `label_change` transition trigger 9번째 entry (cross-repo bidirectional label sync verify-before-assert, CFP-1336)

**날짜**: 2026-05-24

#### 동기

cross-repo 영역의 label state mutation event — wrapper repo Story Issue `phase:*` / `gate:*` label change ↔ impl repo Phase 2 PR label change 의 bidirectional sync 가 base + Amendment 1-8 의 verify subject scope (Orchestrator + agent + subagent) 안 codify 부재. label state 가 lane workflow 자동 진행의 핵심 driver (phase 전환 = lane spawn trigger, gate 전환 = phase-gate-mergeable.yml unblock signal)인데 cross-repo 영역 안 wrapper Story Issue label ↔ impl repo PR label drift 발생 시 verify 의무 영역 미codify.

**Carrier driver** = CFP-1302 D-4 chief tie-break dissent carry-over (within-repo GITHUB_TOKEN 결정 시 cross-repo path 별 carrier 분리, axis disjoint follow-up F2 carrier scope split — within-repo synchronous ↔ cross-repo asynchronous + PAT-mediated 영역 분리). 본 Amendment 9 = sentinel-driven 아닌 ratchet 확장 carrier (CFP-1302 D-4 dissent 정합).

**예상 anti-pattern** (Wave 2 mechanical wire 활성 후 sentinel 영역 후보):
- wrapper repo Story Issue 가 `phase:구현` 부착인데 impl repo Phase 2 PR 은 `phase:설계` 잔존 → lane workflow 자동 진행 신뢰성 손실
- cross-repo PAT (CODEFORGE_CROSS_REPO_PAT) write 후 wrapper-side workflow 가 또 다시 `label_change` event 발화 → 무한 self-trigger loop (T-2 invariant 위반)
- impl repo PR label change event 가 verified-via annotation 부재 상태로 wrapper Issue label write 발화 → cross-repo state ground truth verify 미수행 false claim

super-class = `cross_repo_label_state_drift_unverified`. **cross-repo state layer** — Amendment 7 의 git layer staleness (working tree HEAD vs origin/main divergence) + Amendment 8 의 auth layer staleness (MCP token TTL) 와 axis disjoint (label state ↔ git ↔ auth 3 layer disjoint, 별 staleness sub-domain).

#### §결정 1 expansion — `label_change` transition trigger 9번째 entry

Amendment 2/3/5/6/7/8 precedent 답습 (closed-set ratchet 강화). 본 Amendment 9 = 9번째 entry append.

| Field | Value |
|---|---|
| ID | `label_change` |
| Transition trigger | cross-repo label state mutation event — wrapper repo Story Issue `phase:*` / `gate:*` / `hotfix-bypass:*` label change ↔ impl repo Phase 2 PR label change 의 bidirectional sync 직전·직후 |
| 발화 시점 | (a) wrapper repo Story Issue label change event (`issues.labeled` / `issues.unlabeled`) 직전 + 직후 (b) impl repo Phase 2 PR label change event (`pull_request.labeled` / `pull_request.unlabeled`) 직전 + 직후 (c) `cross-repo-label-sync.yml` workflow self-application 직전 (Orchestrator 가 workflow 발화 직전 active_sessions[] dual-source verify) (d) `gh api repos/<org>/<repo>/issues/<N>/labels` direct call 직전 (label state ground truth verify) |
| Verify 의무 | §결정 1-M cross-repo label state verify-before-assert primitive (아래) + T-2 self-trigger 4-pattern AND guard invariant (sender.type / actor-allowlist / `[skip-cross-repo-sync]` marker / idempotent diff) |
| Verify subject | **Orchestrator** (base + Amendment 1-5 + Amendment 7 + Amendment 8 + 본 Amendment 9) + agent / subagent (Amendment 6 + Amendment 8 + 본 Amendment 9 — cross-repo workflow self-application + label state assertion 영역 동등 mandate) |
| Verify direction | **bidirectional cross-repo direction** (wrapper Issue label ↔ impl PR label, wrapper-primary tie-break — conflict 시 wrapper Story Issue = source of truth) — base direction (Orchestrator self-assertion) + Amendment 6 sibling Story bidirectional + Amendment 7 self-Read + Amendment 8 pre-flight 보완 |

closed enum — **10번째 trigger 추가 시** Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합). open_extension: false.

#### §결정 1-M — Cross-repo label state verify-before-assert primitive

`label_change` transition 시점 verify 의무 (Amendment 9 신설):

| Step | Verify command | PASS 조건 | Fallback |
|---|---|---|---|
| 1. wrapper main pin | `git fetch origin main` (working tree stale 우려, Amendment 7 §결정 1-I 정합) | exit 0 | network 실패 시 advisory + cached state (graceful degradation) |
| 2. cross-repo state direct verify | `gh api /repos/<org>/<repo>/issues/<N>/labels --jq '.[].name'` direct fetch (sender 측 wrapper + receiver 측 impl repo 양 verify) | API 200 + label list returned | API 실패 시 advisory + `[CROSS-REPO-SYNC: <repo> unreachable]` audit comment + circuit breaker (5 fail → 1h pause) |
| 3. dual-source AND verify | Story §14 Lane Evidence + Story Issue body `active_sessions[]` (ADR-085 §결정 2 dual carrier) 두 source 일치 검증 | dual-source AND PASS | 1+ source mismatch 시 stale_session_state 의심 → memory rule 6/7 detection layer 진입 (title-based search + Epic state poll) |
| 4. verified-via annotation | 모든 cross-repo label state 인용 옆 `verified-via: gh api repos/.../issues/<N>/labels --jq '.[].name'` annotation 부착 | annotation 부재 시 lint warning (Wave 2 carrier) | Wave 1 = behavioral mandate, Wave 2 = mechanical lint binding |

4-step PASS 시 — `verified-via: git fetch + gh api repos/.../issues/<N>/labels direct + active_sessions[] dual-source AND` annotation 의무. 미충족 시 cross-repo label state 단정 발화 차단 + advisory escalate (audit comment `[CROSS-REPO-SYNC: skip — verify-before-assert 4-step FAIL]`).

**Wrapper-primary tie-break rationale**: conflict 시 wrapper Story Issue = source of truth — wrapper Issue 가 governance SSOT, impl repo PR 은 implementation artifact (Concept 3, Researcher synthesis §6 정합). consumer overlay 안 `project.yaml verify.cross_repo_label_tie_break: <wrapper-primary | impl-primary>` 확장 허용 (강화 방향 only, ADR-027 Amendment 5 consumer overlay scope 정합).

#### §결정 1-N — T-2 self-trigger 4-pattern AND guard invariant

`cross-repo-label-sync.yml` workflow (CFP-1336 Wave 2 carrier) 의 self-trigger loop 차단 invariant. cross-repo PAT (CODEFORGE_CROSS_REPO_PAT) write 후 workflow 가 또 다시 `label_change` event 발화 → 무한 recursion risk → 4-pattern AND defense in depth 의무 (Researcher Concept 2 정합):

| Pattern | Guard mechanism | Verify command |
|---|---|---|
| (a) sender.type early-exit | `github.event.sender.type == 'Bot'` AND sender login == PAT actor 시 즉시 exit 0 | `if [[ "${{ github.event.sender.type }}" == "Bot" ]] && [[ "${{ github.event.sender.login }}" == "${{ vars.CROSS_REPO_PAT_ACTOR }}" ]]; then exit 0; fi` |
| (b) actor-allowlist | `github.actor` ∈ known-bot allowlist (e.g., `CODEFORGE_CROSS_REPO_PAT` owner login `mccho` / `dependabot[bot]` 등) | `if ! grep -q "^${{ github.actor }}$" <(yq '.cross_repo_label_sync.actor_allowlist[]' .claude/_overlay/project.yaml); then exit 0; fi` |
| (c) `[skip-cross-repo-sync]` marker grep | Issue / PR body 안 marker 부재 verify (opt-out channel) | `if echo "${{ github.event.issue.body || github.event.pull_request.body }}" \| grep -q '\[skip-cross-repo-sync\]'; then exit 0; fi` |
| (d) idempotent diff | 동기화 대상 label set 이 현 state 와 byte-identical 시 no-op (write 자체 발화 차단) | `if [[ "$WRAPPER_LABELS" == "$IMPL_LABELS" ]]; then exit 0; fi` |

4-pattern AND PASS 시에만 cross-repo label write 발화. 1+ FAIL 시 exit 0 graceful skip + audit comment `[CROSS-REPO-SYNC: skip — <pattern> guard fail]` (comment-prefix-registry-v1 v1.4 `[CROSS-REPO-SYNC]` 15번째 prefix 정합).

#### §결정 1-O — Inline whitelist boundary cross-ref (ADR-039)

ADR-039 Inline whitelist 4-entry (사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report) 안 **Status report** entry 의 Issue / PR label state 인용 영역이 본 Amendment 9 의무 영역과 교집합 — Orchestrator 가 사용자 status report 발화 시 wrapper Issue / impl PR label state 인용 = cross-repo state assertion 정합. 본 Amendment 9 의무 적용 = ADR-039 inline whitelist scope 안 Status report entry 도 §결정 1-M primitive 의무 (whitelist = "agent spawn 회피" 만, "verify 회피" 아님 — Amendment 7 §결정 1-J disjoint axis 패턴 답습).

#### Amendment 9 — Wave 1 declaration / Wave 2 mechanical wire 분리

`mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify, subagent-sibling-story-polling-evidence, mcp-token-freshness-precheck, cross-repo-label-sync]` (5 entry — Wave 1 retain, 6th entry append 보류). Wave 2 별 sub-CFP carrier = `cross-repo-label-sync` warning-tier entry (frontmatter 갱신 완료, 본 Change Plan §3.6 자체 carrier — declaration-only-Wave-1 retain, recurrence count 0 — sentinel-driven 아닌 ratchet 확장 carrier (CFP-1302 D-4 chief tie-break dissent carry-over), threshold 3 / promotion_trigger none, sibling_dependencies: [CFP-1336, TBD-Wave-2]).

Wave 1 retain rationale: Amendment 5/6/7/8 (CFP-1102 fix_iter_start + CFP-1318 sibling_story_handoff + CFP-1319 stale_local_main_checkout + CFP-1348 mcp_token_expired_mid_flight) 동일 Wave 1 declarative anchor only 답습 (precedent consistency). workflow yml hydration + script + bats fixture pair + impl repo listener seed 영역 false-negative risk + cross-repo PAT scope grant actual = Phase 2 PR 사용자 manual blocker (ADR-066 Amendment 4 §결정 2 6번째 entry pre-clear).

#### Amendment 9 — Paired sibling Amendment cross-ref (3 ADR Amendment 동시 발의)

본 Amendment 9 = **paired sibling** with 2 ADR Amendment (동일 CFP-1336 carrier, axis disjoint complement 3-set):

- **ADR-082 Amendment 14** §결정 1 layer 1 sub-scope (1-D) `cross-repo label-write authority` 신설 — internal lane agent 의 cross-repo label state mutation 직전 write authority 4-tuple verify (wrapper→impl write 권한 / impl→wrapper write 권한 sender.type + actor allowlist / cross-org sync 차단 mclayer org only / verified-via annotation 의무).
- **ADR-066 Amendment 4** §결정 2 scope minimum 6번째 entry `cross-repo-target-repos issues:write (label endpoint)` — CODEFORGE_CROSS_REPO_PAT scope grant (least-privilege invariant — target = wrapper-self ↔ impl repo 한정, action = `issues:write` (label endpoint) 1종만, escalation scope 금지).

**axis disjoint complement 3-set** (ADR-064 §결정 1 CFP scope unitary 정합, ADR-082 §결정 8 per-area 분할 거부 pattern 답습):
- 본 Amendment 9 = **verify subject layer** (Orchestrator self-assertion verify, transition trigger `label_change`)
- ADR-082 Amendment 14 sub-scope 1-D = **write authority layer** (internal lane agent self-write authority 4-tuple verify)
- ADR-066 Amendment 4 §결정 2 6번째 entry = **PAT scope grant layer** (least-privilege scope minimum)

3 layer disjoint codify — 단일 super-class "cross-repo bidirectional label sync" 의 3 layer 분리 (chief tie-break ladder ADR-068 Amendment 2 단계 2 ADR-068 invariant I-4 wording SSOT 정합).

#### Amendment 9 — Disjoint axis cross-ref

- **ADR-082**: write-time semantic truth verify (corpus / cross-plugin / cross-repo label-write authority sub-scope 1-D). 본 Amd 9 = transition state verify (label_change event 직전·직후 transition layer). write-time input value vs cross-repo state assertion, sub-scope 1-D ↔ Amendment 9 = paired axis (verify subject ↔ write authority disjoint complement).
- **ADR-085**: multi-session collaboration coordination (pre-hoc cross-session ownership). 본 Amd 9 = single session 안 cross-repo label state verify (verify axis, post-hoc cross-repo state). ownership coordination ≠ cross-repo label state verify, axis disjoint.
- **Amendment 7** (`stale_local_main_checkout`): git layer staleness (working tree HEAD vs origin/main divergence). 본 Amd 9 = label state layer (wrapper Issue label ↔ impl PR label drift). git ↔ label state layer disjoint, 양 staleness sub-domain.
- **Amendment 8** (`mcp_token_expired_mid_flight`): auth layer staleness (MCP token TTL). 본 Amd 9 = label state layer. auth ↔ label state layer disjoint, 양 staleness sub-domain.
- **Amendment 6** (`sibling_story_handoff`): bidirectional sibling Story state polling (chief↔Orchestrator). 본 Amd 9 = bidirectional cross-repo label state (wrapper↔impl, wrapper-primary tie-break). sibling Story state ≠ cross-repo label state, axis disjoint — 단 양쪽 모두 bidirectional pattern 답습.
- **ADR-066 Amendment 4** (§결정 2 6번째 entry cross-repo-target-repos issues:write): PAT scope grant layer. 본 Amd 9 = verify subject layer. PAT grant ≠ verify, paired axis disjoint complement (3-set 정합).
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 9 = pattern_count 0 (sentinel-driven 아닌 ratchet 확장 carrier — CFP-1302 D-4 chief tie-break dissent carry-over F2 carrier 정합). ADR-045 §D-9 적용 사례 외 영역 (Amendment family 4번째 ratchet 확장 사례 — Amendment 6/7/8 sentinel-driven 후 9 non-sentinel ratchet).
- **CFP-1302**: parent — within-repo phase-gate-auto-cleanup.yml (GITHUB_TOKEN only) + D-4 chief tie-break dissent (cross-repo path 별 carrier 분리). 본 Amd 9 = D-4 dissent F2 carry-over scope split carrier.

#### Amendment 9 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 10 scope = 본문 + Amendment 1+2+3+4+5+6+7+8+9 강화 방향 only (enum 9번째 entry append + cross-repo label state verify-before-assert primitive 신설 + T-2 self-trigger 4-pattern AND guard invariant codify + ADR-039 inline whitelist Status report scope 적용). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1-9 동형 precedent). ADR-064 §self-application top-down ratchet 정합. paired sibling ADR-082 Amendment 14 + ADR-066 Amendment 4 동일 carrier — 3 ADR Amendment 동시 발의 (axis disjoint complement 3-set, ADR-064 §결정 1 CFP scope unitary 정합). **Amendment slot history**: Amd 9 → 10 (CFP-1384 mid-session collision, 6th collision in CFP-1336 lineage pattern_count 11+).

### Amendment 11 — `spawn_prompt_emit` transition trigger 10번째 entry (Pre-spawn HEAD-pin protocol, CFP-1437)

**날짜**: 2026-05-24 KST

**carrier**: CFP-1437 (Sub-CFP A of CFP-1389 / CFP-1336 retro follow-up — Pre-spawn HEAD-pin protocol mechanical lint Epic)

**paired sibling**: ADR-082 Amendment 15 §결정 1 layer 1 sub-scope (1-E) spawn prompt SHA-anchor write-time verify mandate (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier)

#### 동기

CFP-1336 Phase 1 single Story 안 amendment_number_stale_at_planning collision 4 reach (Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions) + cross-Story pattern_count 누적 9+ reach (CFP-1293 / CFP-1303 / CFP-1318 / CFP-1336-iter1~iter4 / CFP-1390 mid-DesignReview) → system-level pattern continued evidence. ADR-045 §D-9 Mandatory escalation 정합 — preventive solution carrier 의무.

근본 원인 = Orchestrator (또는 PL agent / chief author) 가 lane PL / chief author / deputy / 4-tuple sub-tuple subagent 를 spawn 할 때 spawn prompt 안 baseline origin/main SHA reference 부재 (또는 stale SHA 추정 사용). spawn 직후 mid-flight 다른 Story / Amendment merge 발생 시 spawn 받은 agent / subagent 는 stale baseline 가정 위에 planning → write 시점 amendment_id collision FIX iter 진입.

Amendment 7 (`stale_local_main_checkout`) + Amendment 5 (`fix_iter_start`) 가 git-layer staleness sub-domain 을 codify 하지만 **spawn-time anchor** 영역은 누락 (read-time / FIX iter trigger time 만 coverage). 본 Amendment 11 = spawn-time SHA-anchor preventive layer 신설.

#### Sentinel evidence (pattern_count 9+ reach Mandatory per ADR-045 §D-9, super-class `amendment_number_stale_at_planning`)

| # | Story | 발현 | Amd slot drift |
|---|---|---|---|
| 1 | CFP-1293 | ADR-083 Amd cite stale (backward-staleness) | 2 → 3 |
| 2 | CFP-1303 | review-verdict-v4 v4.8→v4.9 schema sibling sync | (Story scope drift) |
| 3 | CFP-1318 | ADR-073 Amd 6 sibling_story_handoff trigger collision | 6 collision |
| 4-7 | CFP-1336 iter1-iter4 | single Story 4 reach (Amd 8 → 10 → 12 → 13 → 14) | 5 collisions |
| 8 | CFP-1390 mid-DesignReview spawn | spawn collision (CFP-1336 lineage 5th) | Amd 13 → 14 |
| 9 | (forward-prevention sentinel) | CFP-1336 retro identification | 본 Sub-CFP A carrier |

> ratchet ≥ threshold 2 reach Mandatory + 본 Amendment 11 = preventive solution carrier (sentinel-driven + ratchet 확장 hybrid).

#### §결정 1 expansion — `spawn_prompt_emit` transition trigger 10번째 entry

Amendment 2/3/5/6/7/8/10 precedent 답습 (closed-set ratchet 강화). 본 Amendment 11 = 10번째 entry append.

> closed_enum: open_extension:false — 11번째 trigger 추가 시 Amendment 강화 방향만 허용 (ADR-058 §결정 5 정합).

#### §결정 1-N primitive — Pre-spawn HEAD-pin protocol (4-step verify-before-assert mandate)

Orchestrator (또는 PL agent / chief author) 가 spawn prompt emit 시 다음 4 의무:

1. **`git rev-parse origin/main` direct fetch** — spawn prompt 작성 직전 `git fetch origin main --quiet` + `git rev-parse origin/main` 으로 ground truth SHA 획득 (working tree HEAD 또는 cached SHA 사용 금지).
2. **spawn prompt 첫 줄 anchor block 의무** — spawn prompt body 첫 줄 (또는 `[USER-UTTERANCE-VERBATIM]` block 다음 줄, ADR-082 sub-scope 1-C precedent 답습) `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block 부착. 형식 = literal block, regex `^\[PRE-SPAWN-ORIGIN-MAIN-SHA: [0-9a-f]{40}\]$`.
3. **verified-via annotation** — spawn prompt 안 annotated section `verified-via: git rev-parse origin/main at <timestamp KST>` 또는 동등 형식. cached SHA 인용 금지 (matches ADR-073 §결정 1 base form).
4. **cascade SHA propagation** — parent agent (Orchestrator / PL) 가 child agent (chief author / deputy / sub-tuple) spawn 시, 본 spawn 시점 `git rev-parse origin/main` 재실행 후 fresh SHA pin 의무. parent SHA verbatim carry 금지 (parent SHA → spawn 시점 사이 mid-flight merge 가능, fresh re-fetch 의무).

> ADR-082 §결정 1 sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` block precedent 동형 — spawn-time anchor block pattern. block 형식 변경 시 Amendment 강화 방향만.

#### §결정 1-A transition trigger 표 10번째 row

| # | Trigger | Verify subject | Verify object | Timing |
|---|---|---|---|---|
| 10 | `spawn_prompt_emit` | Orchestrator / PL / chief author | origin/main SHA (spawn 시점 fresh) | spawn prompt body 작성 직전 |

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `spawn-prompt-head-pin-presence` warning-tier deferred-followup append. Wave 2 mechanical wire (lint script + workflow + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (ADR-082 Wave 1 declaration-only precedent 답습 — Amendment 6/8/10 패턴 verbatim 답습).

Wave 1 retain rationale: Researcher 권고 fail-pattern (mechanical lint 의 grep heuristic false-positive — spawn prompt 안 anchor block 부재 vs 단순 형식 변경 disambiguate 영역) — sentinel forward-prevention 후 Wave 2 mechanical wire 결정 (precedent CFP-963 codex-network-scope-presence + CFP-1336 Amendment 10 cross-repo-label-sync 답습).

#### ADR-082 Amendment 15 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair)

ADR-073 Amendment 11 = transition 시점 spawn prompt SHA pin verify (when + how — Orchestrator / PL emit-time discipline). ADR-082 Amendment 15 §결정 1 layer 1 sub-scope 1-E = spawn prompt SHA-anchor write-time verify (what + who-can-write — internal lane agent self-write semantic truth verify). 두 ADR 가 같은 CFP-1437 Story 안 paired carrier 로 사용자 D-4 chief tie-break dissent carry F2 carrier 영역 (spawn-time SHA-anchor drift 차단) 의 두 disjoint axis 동시 codify.

#### Disjoint axis cross-ref

- **Amendment 5** (`fix_iter_start`): FIX iter N > 0 시점 main HEAD pin verify. 본 Amd 11 = spawn-time SHA pin verify (FIX iter 이전 spawn-time discipline). FIX iter ↔ spawn-time disjoint, 양 staleness sub-domain.
- **Amendment 7** (`stale_local_main_checkout`): Orchestrator self-Read working tree HEAD vs origin/main divergence. 본 Amd 11 = spawn prompt anchor SHA pin (spawn-time write 시점, not Read 시점). Read ↔ spawn-time write disjoint, 양 git layer staleness sub-domain.
- **Amendment 8** (`mcp_token_expired_mid_flight`): MCP server auth token TTL. 본 Amd 11 = spawn prompt body anchor (git ground truth layer, not auth layer). auth ↔ git layer disjoint, 양 staleness sub-domain.
- **Amendment 10** (`label_change`): cross-repo label state mutation. 본 Amd 11 = spawn-time SHA-anchor (intra-repo git layer, not cross-repo label state). label state ↔ SHA pin disjoint, 양 layer 별 sub-domain.
- **ADR-082 sub-scope 1-C** (`[USER-UTTERANCE-VERBATIM]`): spawn prompt user-utterance verbatim anchor (user input fidelity). 본 Amd 11 = spawn prompt SHA-anchor (ground truth fidelity, git layer). user input ↔ git ground truth disjoint, 양 spawn-time anchor sub-domain — precedent pattern 답습 (block 형식 verbatim 답습).
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 11 = pattern_count 9+ reach Mandatory carrier (CFP-1293/1303/1318/1336-iter1~iter4/1390 + forward-prevention) — preventive solution carrier (sentinel-driven + ratchet 확장 hybrid).

#### Amendment 11 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 11 scope = 본문 + Amendment 1+2+3+4+5+6+7+8+9+10 강화 방향 only (enum 10번째 entry append + spawn-time SHA-anchor primitive 신설 + cascade SHA propagation invariant codify). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1-10 동형 precedent). ADR-064 §self-application top-down ratchet 정합. paired sibling ADR-082 Amendment 15 동일 carrier — 2 ADR Amendment 동시 발의 (axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합).

#### Related (Amendment 11 동반)

- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — Amendment 15 paired (sub-scope 1-E spawn prompt SHA-anchor write-time verify, verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1437 carrier)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 2-row append (ADR-073 Amd 11 / ADR-082 Amd 15, CFP-1437 paired carrier active 동시 점유)
- `templates/github-workflows/spawn-prompt-head-pin-check.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1437-pre-spawn-head-pin-protocol.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy + `docs/change-plans/` gitignored)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-073 Amendment 11 + ADR-082 Amendment 15 sub-scope 1-E cross-ref 1 line append (CFP-506 line cap 정합)
- `<internal-docs>/plugin-codeforge/stories/CFP-1437.md` — Story file (Sub-CFP A carrier, Phase 1 declarative)

### Amendment 12 — `mid_spawn_origin_drift_detected` transition trigger 11번째 entry (Mid-spawn rebase auto-detection, CFP-1436)

**날짜**: 2026-05-24 KST

**carrier**: CFP-1436 (Sub-CFP B of CFP-1389 / CFP-1336 retro follow-up — Mid-flight rebase auto-detection mechanical lint Epic). paired sibling of CFP-1437 (Sub-CFP A) — Sub-CFP A = preventive (pre-spawn time) / Sub-CFP B = reactive (mid-spawn time).

**paired sibling**: ADR-082 Amendment 16 §결정 1 layer 1 sub-scope (1-F) spawn-internal periodic origin re-pin protocol (verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier)

#### 동기

Sub-CFP A (CFP-1437 / ADR-073 Amendment 11 + ADR-082 Amendment 15) 가 spawn 직전 PRE-SPAWN-ORIGIN-MAIN-SHA block 의무로 baseline origin/main SHA 를 lock 한다. 그러나 spawn 직후 ~ 작업 완료 사이 mid-flight 다른 Story / Amendment merge 가 발생하면 spawn 받은 agent 의 baseline 이 stale 가 된다 (preventive layer 만으로 미흡 — drift 가 spawn-internal time 에 발생).

Sub-CFP B 의 동인 = preventive layer 보강 — chief author / deputy / 4-tuple sub-tuple 작업 중간 (예: 매 N file edit 또는 매 Edit/Write tool 호출 후) periodic check 의무 + drift 감지 시 fast-fail (`drift_detected: true` flag RETURN to Orchestrator) + Orchestrator 가 fresh pin 으로 re-spawn / fast-fail / escalate 결정.

CFP-1336 9+ collisions evidence 의 reactive complement (preventive + reactive 2-layer defense forcing function 완결) — Sub-CFP A 단독으로 catch 못 하는 spawn-internal mid-flight drift 영역 codify.

#### Sentinel evidence (sentinel-driven 아닌 ratchet 확장 carrier)

본 Amendment 12 = preventive layer (Sub-CFP A) 의 reactive complement carrier. sentinel evidence 별도 누적 없음 — CFP-1336 evidence 공유 (preventive + reactive 2-layer defense 결정). Sub-CFP A 와 같은 CFP-1336 evidence base 위 다른 layer 신설.

#### §결정 1 expansion — `mid_spawn_origin_drift_detected` transition trigger 11번째 entry

Amendment 2/3/5/6/7/8/10/11 precedent 답습 (closed-set ratchet 강화). 본 Amendment 12 = 11번째 entry append.

> closed_enum: open_extension:false — 12번째 trigger 추가 시 Amendment 강화 방향만 허용 (ADR-058 §결정 5 정합).

#### §결정 1-O primitive — Mid-spawn rebase auto-detection protocol (3-step reactive verify-before-assert mandate)

chief author / deputy / 4-tuple sub-tuple subagent 가 작업 중간 다음 3 의무:

1. **periodic check trigger** — 매 N file edit 또는 매 Edit/Write tool 호출 후 (또는 timer-based 일정 interval, e.g. 5분) `git fetch origin main --quiet` + `git rev-parse origin/main` 실행. Wave 1 = behavioral mandate (frequency = subagent 자체 판단), Wave 2 mechanical wire = trigger heuristic 별 sub-CFP carrier 결정 (file edit count / time interval / hybrid).
2. **drift comparison** — spawn prompt 안 PRE-SPAWN-ORIGIN-MAIN-SHA block 값과 current origin/main SHA 비교. 일치 = 정상 (continue). 불일치 = drift 감지 (다음 step).
3. **drift detected return early protocol** — drift threshold (≥ N commits behind, default N=1 즉 any merge) 초과 시 subagent 가 RETURN early with `drift_detected: true` flag + `pre_spawn_sha: <hex>` + `current_origin_main_sha: <hex>` + `commits_drift: <N>` + `drift_detected_at_step: <description>` payload. Orchestrator 가 RETURN 수신 시 (a) fresh pin 으로 re-spawn / (b) fast-fail abort / (c) 사용자 escalate 3-way 결정.

> ADR-073 Amendment 11 §결정 1-N (Pre-spawn HEAD-pin protocol) 와 paired — Amendment 11 = pre-spawn time / Amendment 12 = mid-spawn time. 같은 ground truth (origin/main SHA) 이지만 2-layer defense.

#### §결정 1-A transition trigger 표 11번째 row

| # | Trigger | Verify subject | Verify object | Timing |
|---|---|---|---|---|
| 11 | `mid_spawn_origin_drift_detected` | chief author / deputy / sub-tuple subagent | origin/main SHA (mid-spawn time fresh, compared with PRE-SPAWN block) | spawn-internal periodic (매 N file edit / 매 Edit/Write tool 호출 후 / 일정 interval) |

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `mid-spawn-drift-detection` warning-tier deferred-followup append. Wave 2 mechanical wire (subagent runtime hook + lint script + workflow + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (ADR-082 Wave 1 declaration-only precedent 답습 — Amendment 6/8/10/14 + ADR-073 Amendment 11 (Sub-CFP A CFP-1437) 패턴 verbatim 답습).

Wave 1 retain rationale: mechanical wire 의 detection logic (subagent runtime 안 어떻게 periodic check 발화할지 / file edit count vs time interval vs hybrid / return early protocol payload schema) = sentinel forward-prevention 후 Wave 2 mechanical wire 결정 (precedent CFP-963 codex-network-scope-presence + CFP-1336 Amendment 10 cross-repo-label-sync + CFP-1437 Amendment 11 spawn-prompt-head-pin-presence 답습).

#### ADR-082 Amendment 16 dual-binding (verify 의무 ↔ write authority 의무 disjoint axis pair)

ADR-073 Amendment 12 = mid-spawn 시점 origin/main SHA drift 감지 의무 (when + how — chief author / deputy / sub-tuple detection time discipline). ADR-082 Amendment 16 §결정 1 layer 1 sub-scope 1-F = spawn-internal periodic origin re-pin protocol (what + who-can-write — internal lane agent self-write 시 RETURN early authority + payload write-time semantic truth verify). 두 ADR 가 같은 CFP-1436 Story 안 paired carrier 로 mid-flight drift 차단 의 두 disjoint axis 동시 codify.

#### Disjoint axis cross-ref

- **Amendment 11** (`spawn_prompt_emit`): pre-spawn time SHA pin verify (Sub-CFP A CFP-1437, preventive layer). 본 Amd 12 = mid-spawn time drift detection (Sub-CFP B CFP-1436, reactive layer). pre-spawn ↔ mid-spawn disjoint, 양 spawn-time staleness sub-domain — preventive + reactive 2-layer defense.
- **Amendment 5** (`fix_iter_start`): FIX iter N > 0 시점 main HEAD pin verify. 본 Amd 12 = spawn-internal mid-time periodic check (FIX iter 진입 이전 / 진입과 무관). FIX iter ↔ spawn-internal time disjoint.
- **Amendment 7** (`stale_local_main_checkout`): Orchestrator self-Read working tree HEAD vs origin/main divergence. 본 Amd 12 = subagent self-detect mid-spawn-time drift (subagent layer, Orchestrator layer 분리). Read divergence ↔ spawn-internal write-time drift disjoint.
- **Amendment 8** (`mcp_token_expired_mid_flight`): MCP server auth token TTL. 본 Amd 12 = origin/main SHA git layer (not auth layer). auth ↔ git layer disjoint.
- **Amendment 10** (`label_change`): cross-repo label state mutation. 본 Amd 12 = intra-repo git ground truth (not cross-repo label state). label ↔ git disjoint.
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 12 = pattern_count 공유 (CFP-1336 9+ reach, Sub-CFP A preventive + Sub-CFP B reactive 2-layer defense — 동일 evidence base).

#### Amendment 12 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 12 scope = 본문 + Amendment 1+2+3+4+5+6+7+8+9+10+11 강화 방향 only (enum 11번째 entry append + mid-spawn-time drift detection primitive 신설 + return early protocol invariant codify). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1-11 동형 precedent). ADR-064 §self-application top-down ratchet 정합. paired sibling ADR-082 Amendment 16 동일 carrier — 2 ADR Amendment 동시 발의 (axis disjoint complement 2-set, ADR-064 §결정 1 CFP scope unitary 정합).

#### Related (Amendment 12 동반)

- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — Amendment 16 paired (sub-scope 1-F spawn-internal periodic origin re-pin protocol, verify 의무 ↔ write authority 의무 disjoint axis pair, 같은 CFP-1436 carrier)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 2-row append (ADR-073 Amd 12 / ADR-082 Amd 16, CFP-1436 paired carrier active 동시 점유)
- `templates/github-workflows/mid-spawn-drift-detection-check.yml` — workflow stub (declaration-only Wave 1 / Wave 2 mechanical wire 별 sub-CFP carrier)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1436-mid-flight-rebase-detection.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy + `docs/change-plans/` gitignored)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-073 Amendment 12 + ADR-082 Amendment 16 sub-scope 1-F cross-ref 1 line append (CFP-506 line cap 정합)
- `<internal-docs>/plugin-codeforge/stories/CFP-1436.md` — Story file (Sub-CFP B carrier, Phase 1 declarative)

### Amendment 13 — `pre_git_operation` + `pre_push` transition trigger 12+13번째 entries (Polling cadence 1→3, CFP-FU-A sub-decision 1)

**날짜**: 2026-05-25 KST

**carrier**: CFP-FU-A (Parallel session race 11th occurrence 3-decision sub-CFP — sub-decision 1 carrier within CFP-FU-A).

**paired sibling**: Amendment 14 (sub-decision 2 OR→AND composition layer §결정 1-P primitive) + ADR-082 Amendment 19 sub-scope (1-I) (sub-decision 3 pre-spawn-prompt-finalize verify layer, renumbered from Amd 18 sub-scope 1-H post CFP-1342 mid-flight collision recovery). 3 ADR Amendment 동시 발의 = axis disjoint complement 3-set (event timing cadence + composition layer + window narrowing), ADR-064 §결정 1 CFP scope unitary 정합.

#### 동기

CFP-1420 Sub-A S1.2 parallel session race 11th occurrence (Mega-Epic CFP-1415, branch `cfp-1420-doc-locations-schema-1-2-confluence-variant`, PR #1441 prior merge 2026-05-24T03:07:53Z → 본 session PR #1442 STAND_DOWN_DUPLICATE per DesignReviewPL verdict ESCALATE_PACKET_INCOMPLETE `parallel_session_conflict_post_merge_duplicate`) sentinel.

근본 원인 분석 (Story §2.2):
- (a) lane-entry polling은 발생했으나 timing이 race window 안 — polling 시점에는 별 session의 PR #1441이 아직 open 상태가 아니었거나, polling이 부분 source만 사용
- (b) **OR semantics structural weakness** — `scripts/lib/check_parallel_work_sentinel.py:437` single-mode dispatcher (caller discretion only). caller가 1 mode만 호출하면 다른 2 source 정보 누락 — race window 차단 능력 1/3 수준
- (c) race window pre-spawn-prompt phase (Amd 14 + ADR-082 Amd 19 sub-scope 1-I 영역, renumbered from Amd 18/1-H post CFP-1342 collision recovery)

본 Amendment 13 동인 = (a) polling cadence 자체 부족 — 현 ADR-073 Amd 2 transition trigger enum 4 source (`lane_spawn` / `pr_open` / `merge_transition` / `active_sessions_check`) + Amd 5 (`fix_iter_start`) + Amd 11 (`spawn_prompt_emit`) + Amd 12 (`mid_spawn_origin_drift_detected`) covers spawn/fix-iter-time + pr/merge/label/session_start state-mutation. 단 "git operation 직전" (`git add` / `git commit` / `git merge` / `git rebase`) + "push 직전" (`git push` direct cross-repo state propagation) specific cadence binding 미codify — race window 위주 cadence gap.

#### Sentinel evidence (pattern_count 11 reach Mandatory ADR-045 §D-9)

| # | Story | 발생 | Resolution |
|---|---|---|---|
| 1 | CFP-953 | label-based search miss → memory rule 6 신설 (title-based search 의무) | reactive |
| 2 | CFP-946 | Epic close miss → memory rule 7 신설 (Epic state polling 의무) | reactive |
| 3 | CFP-949 | sub-issue scope polling gap → rule 7 refinement | reactive |
| 4-10 | (다수) | various race window incidents | partial preventive (Amd 2/3/4/5) |
| 11 | CFP-1420 Sub-A S1.2 | PR #1442 STAND_DOWN_DUPLICATE per #1441 prior merge | escalate_user mandate (본 carrier) |

11 occurrences ≫ threshold 2 = ADR-045 §D-9 Mandatory escalation + 12th meta-occurrence (CFP-1342 collision recovery in-flight). 본 Amendment 13 + 14 + ADR-082 Amendment 19 sub-scope (1-I) (renumbered from Amd 18/1-H post CFP-1342 mid-flight collision recovery) = preventive + reactive 3-layer 완결 carrier.

#### §결정 1 expansion — `pre_git_operation` + `pre_push` transition trigger 12+13번째 entries

Amendment 2/3/5/6/7/8/10/11/12 precedent 답습 (closed-set ratchet 강화). 본 Amendment 13 = 12+13번째 entries append.

> closed_enum: open_extension:false — 14번째 trigger 추가 시 Amendment 강화 방향만 허용 (ADR-058 §결정 5 정합).

#### §결정 1-A transition trigger 표 12+13번째 row

| # | Trigger | Verify subject | Verify object | Timing |
|---|---|---|---|---|
| 12 | `pre_git_operation` | Orchestrator / PL / chief author / subagent | origin/main SHA fresh + sibling Story/PR state (3-mode AND per Amd 14) | git state mutation 직전 (예: `git add` / `git commit` / `git merge` / `git rebase` direct mutation 직전, local-only) |
| 13 | `pre_push` | Orchestrator / PL / chief author / subagent | origin/main SHA fresh + sibling Story/PR state (3-mode AND per Amd 14) | `git push` direct cross-repo state propagation 직전 (network publish 영역, axis disjoint with 12 — local mutation vs network publish) |

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 2 entry `pre-git-operation-sentinel-pickup` + `pre-push-sentinel-pickup` warning-tier deferred-followup append. Wave 2 mechanical wire (`pre-commit` / `pre-push` git hook 통합 + lint script + workflow + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습).

#### Disjoint axis cross-ref

- **Amendment 5** (`fix_iter_start`): FIX iter N > 0 시점 main HEAD pin verify. 본 Amd 13 = pre-git-operation / pre-push timing (FIX iter 진입과 무관). FIX iter ↔ git-op/push disjoint.
- **Amendment 11** (`spawn_prompt_emit`): pre-spawn time SHA pin verify (Sub-CFP A CFP-1437, preventive). 본 Amd 13 = pre-git-operation/pre-push (spawn 후 working time). spawn-time ↔ working-time disjoint.
- **Amendment 12** (`mid_spawn_origin_drift_detected`): spawn-internal periodic drift detection (Sub-CFP B CFP-1436, reactive). 본 Amd 13 = pre-git-operation/pre-push (specific git event trigger). periodic time ↔ event time disjoint.
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 13 = pattern_count 공유 (parallel_session_race 11+ reach, escalate_user mandate 산물).

#### Amendment 13 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 13 scope = 본문 + Amendment 1-12 강화 방향 only (enum 12+13번째 entries append + pre-git-operation/pre-push specific cadence codify). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합.

#### Related (Amendment 13 동반)

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 14 paired (1-P AND composition layer, same CFP-FU-A carrier)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — Amendment 18 paired (1-H pre-spawn-prompt-finalize verify layer, same CFP-FU-A carrier)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 3-row pre-claim append (ADR-073 Amd 13 + Amd 14 + ADR-082 Amd 19, CFP-FU-A paired carrier active 동시 점유; renumbered from Amd 18 post CFP-1342 collision recovery, CFP-1342 Amd 18 row preserved upstream)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-fu-a-parallel-race-3-decisions.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy)
- `<internal-docs>/plugin-codeforge/stories/CFP-FU-A.md` — Story file (CFP-FU-A carrier, Phase 1 declarative)
- `CLAUDE.md` — verify-before-trust 4-layer 단락 ADR-073 Amendment 13/14 + ADR-082 Amendment 19 sub-scope (1-I) (renumbered from Amd 18/1-H post CFP-1342 collision recovery) cross-ref 1 line append (CFP-506 line cap 정합)

### Amendment 14 — §결정 1-P primitive AND aggregate composition layer (CFP-FU-A sub-decision 2)

**날짜**: 2026-05-25 KST

**carrier**: CFP-FU-A (Parallel session race 11th occurrence 3-decision sub-CFP — sub-decision 2 carrier within CFP-FU-A).

**paired sibling**: Amendment 13 (sub-decision 1 polling cadence 1→3, 12+13번째 transition trigger entries) + ADR-082 Amendment 19 sub-scope (1-I) (sub-decision 3 pre-spawn-prompt-finalize verify layer, renumbered from Amd 18 sub-scope 1-H post CFP-1342 mid-flight collision recovery). 3 ADR Amendment 동시 발의 = axis disjoint complement 3-set (event timing cadence + composition layer + window narrowing), ADR-064 §결정 1 CFP scope unitary 정합.

#### 동기

Story §2.0 verify-before-trust 7th pivot — Issue body assumption "scripts/check-parallel-work-sentinel.sh 3 polling mode = OR semantics" verified-pivot. 실제 `scripts/lib/check_parallel_work_sentinel.py:437` argparse `--mode` choices = `["title-search", "epic-state-poll", "head-compare-sibling-commits"]` = **mutually exclusive dispatcher** (single mode per invocation), NOT composed OR. caller가 mode 선택 — no AND/OR composition layer codified.

CFP-1420 Sub-A S1.2 11th occurrence root cause analysis (Story §2.2(b)): caller discretion 으로 single-mode invocation 시 다른 2 source 정보 누락 — race window 차단 능력 1/3 수준. AND composition layer 신설 시 race window 차단 능력 3/3 보장 ratchet.

#### §결정 1-P primitive — AND aggregate composition layer mandate

lane-entry sentinel polling 시 다음 3 의무:

1. **3-mode 동시 invoke 의무** — `title-search` + `epic-state-poll` + `head-compare-sibling-commits` 3 sub-mode 모두 invoke (caller가 single-mode만 invoke 금지). Wave 1 = behavioral mandate (caller가 자체 sequential invoke 가능), Wave 2 mechanical wire = `scripts/lib/check_parallel_work_sentinel.py` 신규 `--mode all-and` choice 추가 + 3 sub-mode invoke + 결과 AND aggregate logic 별 sub-CFP carrier.
2. **AND aggregate verify 의무** — 3-mode 결과 모두 PASS (race detected = false) 시에만 sentinel PASS. 1개라도 positive (race detected = true) 시 race detected verdict.
3. **single-mode invocation 차단 binding** — caller discretion 금지 (race window 차단 능력 보장 ratchet). `--mode <single>` invocation 시 deprecation warning 발화 의무 (Wave 2 mechanical wire).

> Amendment 14 sub-decision 2 carrier — race window 차단 능력 1/3 → 3/3 ratchet 강화.

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `parallel-work-sentinel-and-aggregate` warning-tier deferred-followup append. Wave 2 mechanical wire (`scripts/lib/check_parallel_work_sentinel.py` 신규 `--mode all-and` choice + 3 sub-mode invoke + 결과 AND aggregate logic + workflow yml hydrate + bats fixture pair + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435 Wave 1→Wave 2 split 답습).

#### Disjoint axis cross-ref

- **Amendment 11** (`spawn_prompt_emit`): pre-spawn time SHA pin verify (single source per spawn — origin/main SHA fetch 시점). 본 Amd 14 = multi-source AND per polling event (composition layer). single source per spawn ↔ multi-source AND composition disjoint.
- **Amendment 12** (`mid_spawn_origin_drift_detected`): spawn-internal periodic drift detection (single source per check — origin/main SHA compare). 본 Amd 14 = multi-source AND per polling event. single source per check ↔ multi-source AND composition disjoint.
- **Amendment 13** (`pre_git_operation` + `pre_push`): event timing cadence (when polling 발화). 본 Amd 14 = composition layer (how polling source 묶기). cadence ↔ composition disjoint complement (cadence 발화 후 composition layer 적용 = sequential composition).
- **Amendment 5 + ADR-085 lane-entry sentinel 4-step polling**: 4-step polling 의 source 추가 (active_sessions[] field check + gh issue list search + git pull rebase + active_sessions[] append). 본 Amd 14 = polling 안 3-mode 동시 AND aggregate (sub-source composition). 4-step polling ↔ 3-mode AND aggregate disjoint (4-step = lane-entry sequence, 3-mode = source aggregation per polling event).
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 14 = pattern_count 공유 (parallel_session_race 11+ reach, OR semantics structural weakness root cause carrier).

#### Amendment 14 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 14 scope = 본문 + Amendment 1-13 + 1-P primitive 신설 강화 방향 only (composition layer 신설 + caller discretion 차단 invariant codify). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과. ADR-064 §self-application top-down ratchet 정합.

#### Related (Amendment 14 동반)

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 13 paired (1-A 12+13번째 entries, same CFP-FU-A carrier)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — Amendment 18 paired (1-H pre-spawn-prompt-finalize verify layer, same CFP-FU-A carrier)
- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 3-row pre-claim append (ADR-073 Amd 13 + Amd 14 + ADR-082 Amd 19, CFP-FU-A paired carrier active 동시 점유; renumbered from Amd 18 post CFP-1342 collision recovery, CFP-1342 Amd 18 row preserved upstream)
- `scripts/lib/check_parallel_work_sentinel.py` — line 437 argparse `--mode` choices 영역 (Wave 2 mechanical wire 대상, `--mode all-and` choice 신규 추가)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-fu-a-parallel-race-3-decisions.md` — Change Plan SSOT
- `<internal-docs>/plugin-codeforge/stories/CFP-FU-A.md` — Story file

### Amendment 15 — `architect_agent_chief_author_lane_spawn` transition trigger 14번째 entry (ArchitectPL → ArchitectAgent chief author specific cadence base SHA freeze mandate, CFP-1571)

**날짜**: 2026-05-25 KST

**carrier**: CFP-1571 (Mandatory escalation #1571 — `parallel-session-merge-stream-main-advance-during-lane-flow` pattern_count 5 reach 산물, PMO 권장 Option A 채택 사용자 직권 derived default)

**paired sibling**: 없음 (single-axis carrier — chief author handoff specific cadence specialization, Amd 11 `spawn_prompt_emit` generic spawn 의 chief-author-specific specialization axis disjoint complement)

#### 동기

CFP-1334 retro §5.2 + CFP-1403 retro §3.1 sentinel evidence — `parallel-session-merge-stream-main-advance-during-lane-flow` pattern_count 5 reach:
- **CFP-1334 §3.1 4건 lineage** — ArchitectAgent spawn 후 mid-flight parallel session merge stream main advance 영역 안 chief author commit base stale 화 (sibling Story / Amendment merge 가 lane flow 진행 중 main 으로 advance). 4건 lineage = single Story 안 multi-occurrence (escalate_user Optional carrier 첫 reproduction).
- **CFP-1403 §3.1 1건 추가** — base regression cascade (ArchitectAgent commit on stale base `ca1c20e`, 그 사이 `99fb31f` CFP-FU-B plugin.json version bump + CHANGELOG entry + cross-repo-patch merged → HEAD diff REVERSE direction downgrade). escalate_user mandate (PMO trivial 판정).

본 pattern = Amd 11 (`spawn_prompt_emit` generic spawn) 의 chief-author-specific subset — **ArchitectPL → ArchitectAgent chief author handoff specific cadence**. Amd 11 = generic any-actor spawn (Orchestrator / PL / chief 모두 적용) / 본 Amd 15 = ArchitectPL → ArchitectAgent chief author specific handoff (deputy spawn 영역 외 단일 subordinate 영역). axis disjoint complement — Amd 11 generic cadence 가 chief-author-specific binding 영역 충분히 cover 못 함 (chief author spawn = lane flow 안 most token-intensive + most parallel-race-prone operation, specific cadence specialization 의무).

#### Sentinel evidence (pattern_count 5 reach Mandatory ADR-045 §D-9)

| # | Story | 발생 | Resolution |
|---|---|---|---|
| 1-4 | CFP-1334 §3.1 | 4건 stale-base regression cascade — single Story 안 multi-occurrence | escalate_user Optional (first lineage reproduction) |
| 5 | CFP-1403 §3.1 | 1건 추가 — base regression cascade (ArchitectAgent commit on stale base, HEAD diff REVERSE direction downgrade) | escalate_user mandate per PMO (본 CFP-1571 Mandatory escalation source) |

5 occurrences ≫ threshold 2 = ADR-045 §D-9 Mandatory escalation + Option A 채택 (사용자 직권 derived default per PMO 권장).

#### §결정 1 expansion — `architect_agent_chief_author_lane_spawn` transition trigger 14번째 entry

Amendment 2/3/5/6/7/8/10/11/12/13 precedent 답습 (closed-set ratchet 강화). 본 Amendment 15 = 14번째 entry append.

> closed_enum: open_extension:false — 15번째 trigger 추가 시 Amendment 강화 방향만 허용 (ADR-058 §결정 5 정합).

#### §결정 1-A transition trigger 표 14번째 row

| # | Trigger | Verify subject | Verify object | Timing |
|---|---|---|---|---|
| 14 | `architect_agent_chief_author_lane_spawn` | Orchestrator + ArchitectPL (handoff sender) | origin/main SHA (chief author spawn 시점 fresh) + base drift (working tree HEAD vs origin/main) | ArchitectAgent chief author Agent tool dispatch 직전 (ArchitectPL deputy spawn request packet 수령 후) |

#### §결정 1-Q primitive — ArchitectPL → ArchitectAgent chief author handoff specific cadence (4-step verify-before-assert mandate)

ArchitectAgent chief author spawn 직전 다음 4 의무 (Orchestrator + ArchitectPL handoff sender 양 의무):

1. **`git -C <worktree_abs_path> fetch origin`** — cross-repo state freshness 의무 (working tree HEAD 또는 cached SHA 사용 금지). worktree_abs_path = spawn prompt 안 `<worktree_path>` placeholder 의무 명시 (ADR-040 §결정 1 worktree convention 정합).
2. **`git -C <worktree_abs_path> diff origin/main..HEAD --stat`** — base drift detection (HEAD vs origin/main delta 측정). expected diff = 본 Story scope 영역 (예: ADR Amendment 단독 +N lines for doc-only fast-path). drift 감지 = unexpected file additions / unrelated modifications / reverse-direction commits (downgrade 영역).
3. **drift 감지 시 `git -C <worktree_abs_path> rebase origin/main`** — mechanical resolution (no semantic conflict 시 만). semantic conflict (자동 merge 불가 영역) 시 ABORT + chief author re-spawn 의무 (rebase 시도 후 conflict marker 잔존 시).
4. **rebase 후 expected diff narrowed verify** — `git diff origin/main..HEAD --stat` 재실행 + expected scope (Story §3 도입할 설계 영역) 정합 확인. unexpected mid-flight merge 영역 cover 시 chief author re-spawn 의무.

3-step PASS 조건: (a) `git fetch origin` exit 0 + (b) drift 0건 OR drift 감지 후 mechanical rebase PASS + (c) rebase 후 expected diff narrowed verified. 4-step PASS 시 chief author spawn proceed. 미충족 시 spawn 중단 + advisory escalate (사용자 / Orchestrator 결정 영역).

> 본 4-step = Amd 11 §결정 1-N (Pre-spawn HEAD-pin protocol) 의 chief-author-specific specialization — Amd 11 generic spawn anchor block (PRE-SPAWN-ORIGIN-MAIN-SHA literal block) 위에 chief author handoff specific cadence (rebase 의무 + expected diff narrowed verify) 추가 mandate.

#### Wave 1 = declaration-only behavioral mandate

`mechanical_enforcement_actions[]` 신규 entry `architect-chief-author-base-sha-freeze-verify` warning-tier deferred-followup append. Wave 2 mechanical wire (pre-spawn hook + lint script `scripts/lib/check_architect_chief_author_base_sha_freeze.py` Python SSOT per ADR-061 + workflow yml hydrate + bats fixture pair RED→GREEN stash proof per CFP-1334 §8.4 + label-registry MINOR bump `hotfix-bypass:architect-chief-author-base-sha-freeze-verify` family member + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (precedent ADR-082 §결정 6 + ADR-070 §D5 + ADR-077 + ADR-078 + ADR-097 + Amd 11/12/13/14 Wave 1→Wave 2 split 답습).

Wave 1 retain rationale: Amd 11/12/13/14 (CFP-1437 spawn_prompt_emit + CFP-1436 mid_spawn_origin_drift_detected + CFP-FU-A pre_git_operation/pre_push + parallel-work-sentinel-and-aggregate) 동일 Wave 1 declarative anchor only 답습 (precedent consistency). pre-spawn hook + mechanical rebase logic + expected diff narrowed verify primitive false-negative risk + chief author re-spawn ABORT path 영역 = sentinel forward-prevention 후 Wave 2 mechanical wire 결정.

#### Disjoint axis cross-ref

- **Amendment 5** (`fix_iter_start`): FIX iter N > 0 시점 main HEAD pin verify (FIX iter trigger). 본 Amd 15 = ArchitectPL → chief author handoff (FIX iter 진입 이전). FIX iter ↔ chief handoff disjoint.
- **Amendment 7** (`stale_local_main_checkout`): Orchestrator self-Read working tree HEAD vs origin/main divergence (Orchestrator self-Read). 본 Amd 15 = ArchitectPL handoff sender → ArchitectAgent chief author (subagent spawn). self-Read ↔ subagent spawn disjoint.
- **Amendment 8** (`mcp_token_expired_mid_flight`): MCP server auth token TTL (auth layer). 본 Amd 15 = origin/main SHA git layer (not auth). auth ↔ git disjoint.
- **Amendment 10** (`label_change`): cross-repo label state mutation. 본 Amd 15 = intra-repo git ground truth (not cross-repo label state). label ↔ git disjoint.
- **Amendment 11** (`spawn_prompt_emit` generic spawn): generic any-actor spawn-time SHA pin verify (Orchestrator / PL / chief 모두 적용). 본 Amd 15 = **ArchitectPL → ArchitectAgent chief author specific cadence** (chief-author-specific specialization, axis disjoint complement) — Amd 11 generic cadence 가 chief-author-specific binding 영역 충분히 cover 못 함 (chief author spawn = lane flow 안 most token-intensive + most parallel-race-prone operation, specific cadence specialization 의무).
- **Amendment 12** (`mid_spawn_origin_drift_detected`): spawn-internal periodic drift detection (subagent self-detect mid-spawn time). 본 Amd 15 = pre-spawn handoff (ArchitectPL → chief author handoff sender side). pre-spawn ↔ mid-spawn disjoint.
- **Amendment 13** (`pre_git_operation` + `pre_push`): specific git event trigger cadence (git operation 직전). 본 Amd 15 = ArchitectAgent chief author spawn 직전 (specific actor + specific lane). git event ↔ chief handoff disjoint.
- **Amendment 14** (`parallel-work-sentinel-and-aggregate` 3-mode AND composition): polling source aggregation layer. 본 Amd 15 = chief author handoff base SHA freeze (specific verify primitive). composition layer ↔ specific primitive disjoint.
- **ADR-045 §D-9**: PMOAgent retro corpus pattern_count threshold escalation. 본 Amd 15 = pattern_count 5 reach Mandatory carrier (CFP-1334 §3.1 4건 + CFP-1403 §3.1 1건 stale-base regression cascade), 5번째 적용 사례 of family (Amd 6/7/8/9 + 본 Amd 15).

#### Amendment 15 — META anti-self-application 첫 적용 사례 (triggered + RESOLVED in carrier PR itself)

본 Amendment 15 (Story CFP-1571) 의 deterministic mandate 가 carrier PR 자체에서 violation 잠재 (recursive dogfooding self-evidence) — 본 ArchitectAgent chief author spawn 자체가 §결정 1-Q primitive 의무 영역. 본 carrier 안 actual sequence:

1. **Phase 0 verify-before-cite snapshot** (chief author spawn 시점): `git -C <worktree> rev-parse origin/main` = `4a1f0be` (CFP-1539, 2026-05-25 KST) + worktree HEAD = `4a1f0be` 동일 → drift 0건 (verify PASS).
2. **Amendment 15 author 진행 중 mid-flight drift**: CFP-1523 cfp-1523-confluence-ia-real-backfill (#1560 + 4 follow-up commits) merged → origin/main `4a1f0be` → `49d6f6c` advance (5 commits drift, ~10-15분 author elapsed time 안 발생).
3. **§결정 1-Q step 2 base drift detection**: `git -C <worktree> diff origin/main --stat` 실행 시 unexpected 3-file diff 감지 (`docs/adr/ADR-073-...md` +101 expected + `docs/confluence-ia-tree.yaml` -128 unexpected + `docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md` -256 unexpected = file delete).
4. **§결정 1-Q step 3 mechanical rebase**: drift commits 5건 verify (CFP-1523 lineage, ADR-073.md 미touch — disjoint file set, no semantic conflict). `git stash push` → `git rebase origin/main` → `git stash pop` 실행 PASS.
5. **§결정 1-Q step 4 expected diff narrowed verify**: 재실행 `git diff origin/main --stat` = 1 file +101 lines only (ADR-073 Amendment 15 본문 만, expected scope 정합). PASS.

본 META self-application 첫 적용 사례 = recursive dogfooding self-evidence triggered AND RESOLVED in carrier PR itself. 본 Amendment 가 codify 하는 §결정 1-Q primitive 가 carrier PR 자체에서 실 발동 + 4-step protocol PASS — Wave 1 declaration-only behavioral mandate effectiveness self-empirical evidence (mechanical wire 도입 이전 단계 behavioral self-discipline 가 PASS path 달성 가능 입증, ratchet evidence base 강화). post-Amd 9 META self-application 2nd ADR-108 §결정 3 precedent (label-registry-frozen-baseline-count-parity) + 본 Amd 15 = ADR-073 META self-application family 첫 적용 사례 (chief author spawn discipline 자체가 본 Amendment codify 영역).

#### Amendment 15 — sunset_justification N/A 정당

`is_transitional: false` (영구 governance policy) 보존 — Amendment 15 scope = 본문 + Amendment 1-14 강화 방향 only (enum 14번째 entry append + ArchitectPL → ArchitectAgent chief author handoff specific cadence 4-step primitive 신설 + META anti-self-application invariant codify). 약화 / scope 축소 / 면제 영역 0건. ADR-058 §결정 5 sunset_justification ratchet 차단 logic 통과 (Amendment 1-14 동형 precedent). ADR-064 §self-application top-down ratchet 정합. single-axis carrier (paired sibling 없음 — chief-author-specific specialization axis 자체가 단일 axis carrier).

#### Related (Amendment 15 동반)

- `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` row append (ADR-073 Amd 15, CFP-1571 carrier active 점유 — retrospective baseline, CFP-1497 amendment-slot reservation optional 정합)
- `<internal-docs>/plugin-codeforge/change-plans/cfp-1571-adr073-amd-15.md` — Change Plan SSOT (Phase 1 carrier, internal-docs SSOT per ADR-013 dogfood-out policy)
- `<internal-docs>/plugin-codeforge/stories/CFP-1571.md` — Story file (CFP-1571 carrier, Phase 1 declarative)
