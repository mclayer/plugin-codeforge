# Changelog

`codeforge` 플러그인 릴리스 이력. 각 엔트리는 버전 bump 단위.
Breaking change 있는 버전은 [`docs/migration-guide.md`](docs/migration-guide.md) 해당 섹션 변경.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능. plugin SemVer rule SSOT: [ADR-037](docs/adr/ADR-037-plugin-version-bump-rule.md).

## [Unreleased]

## [5.58.0] - 2026-05-14 — CFP-658 Phase 2 of Epic CFP-431 (audit:from-mctrader-debut) — Action 차단 환경 mechanical implementation

### Added

- **`templates/scripts/manual-story-init-fallback.sh`** (bash, POSIX): ADR-027 Amendment 2 §결정 6.H+6.E+6.G+6.I 정합 manual Story init fallback 스크립트. Issue 번호 인자 → existence_check → §1-§11 Story file write + branch + Phase 1 PR open. SecurityArch 조건 3 (shell injection 차단 — printf '%s' + heredoc single-quoted + 숫자 전용 검증) + OpRiskArch 조건 2/4 (exponential backoff 1s/2s/4s + fallback:rate-limited auto-label) + DataMigrationArch 조건 1 (existence_check verbatim port) + PR description checklist mirror (6 체크 항목) 모두 포함.
- **`templates/scripts/manual-story-init-fallback.ps1`** (Windows PowerShell parity): Bash 동일 logic, PowerShell 5.1 semantics. `pre-push.sh.example` precedent 정합.
- **`templates/github-workflows/section-1-verbatim-postmerge.yml`** (warning tier): ADR-027 Amendment 2 §결정 6.C + ADR-060 evidence-enforceable framework. `pull_request_target` closed+merged trigger → Story §1 ↔ Issue body §1 byte-identical 검증 → drift 시 warning audit comment 자동 발의. 4-step Python extract (ADR-061 heredoc single-quoted <<'EOF') + diff -q compare + hotfix-bypass label channel.
- **`.github/workflows/section-1-verbatim-postmerge.yml`**: `templates/github-workflows/section-1-verbatim-postmerge.yml` 와 byte-identical (ADR-005 self-application invariant — diff -q exit 0 verified).
- **`overlay/hooks/validate_config.py` 확장** (`bootstrap.fallback_mode` enum): `auto` | `action_blocked` enum 검증 추가. field 부재 = default `auto` (no error). 허용 외 값 = exit 4 (schema violation). ADR-027 Amendment 2 §결정 6.A SSOT 정합.
- **`overlay/hooks/tests/test_validate_config.py` 확장** (TDD red→green): `TestBootstrapFallbackMode` class 7 TC 추가 — absent/auto/action_blocked/invalid/strict_mode_coexist/uppercase/empty_string. 32/32 PASS.
- **`.claude/_overlay/project.yaml.example` 갱신**: `bootstrap.fallback_mode` commented 예시 추가 (Trigger (A)/(C) 설명 + 우선순위 CLI > env > yaml 명시).
- **`docs/evidence-checks-registry.yaml` 갱신**: `section-1-verbatim-postmerge` entry `status: deferred-followup` → `Active` 전환 + `detect_command` + `workflow` 필드 채움 (Phase 2 carrier 신설 완료).

### Sibling sync (별 PR — Orchestrator monopoly)

- `mclayer/marketplace` plugins[name=codeforge].version 5.57.0 → 5.58.0 (ADR-063 §결정 5 atomic invariant — MINOR bump 동반 marketplace sync required).

## [5.57.0] - 2026-05-14 — CFP-658 Wave 1 of Epic CFP-431 (audit:from-mctrader-debut) — Action 차단 환경 agent direct write fallback path 표준화

### Added

- **ADR-027 Amendment 2 §결정 6 신설**: Action 차단 시 agent direct write fallback path (normative SSOT 단일 위치). 9 §결정 (6.A trigger (A)+(C) hybrid + 6.B agent + 6.C governance ratchet mitigation 3종 + 6.D PAT scope 표 + 6.E shell injection 차단 + 6.F 2-PAT namespace 분리 + 6.G burst control + 6.H existence_check verbatim port + 6.I PR description checklist mirror). frontmatter `amendments[]` append + `mechanical_enforcement_actions[]` 신설 (section-1-verbatim-postmerge action_name, ADR-040 Amendment 3 §결정 7.A 정합).
- **ADR-032 + ADR-036 cross-ref**: Amendment 2 와 strict-eligible 4종 disjoint + KEY atomic invariant manual write 영역 보존.
- **신규 label** (label-registry-v2 v2.11 → v2.13 MINOR — 신규 `fallback` category enum, post-CFP-627 v2.12 atomic rebase):
  - `fallback:manual` (color `c5def5`, audit-trailed) — per-Issue ad-hoc override marker. 우선순위 (C) > (A) > env default.
  - `fallback:rate-limited` (color `c5def5`, audit-trailed) — manual-story-init-fallback.sh exponential backoff max 3 retry 초과 시 자동 부착.
- **`scripts/bootstrap-labels.sh` 갱신**: fallback:* 2 entry hardcoded append (35 base label, 직전 33 base + 2). canonical-only (kind:registry — sibling sync scope 외, ADR-010 §결정 2).
- **`docs/evidence-checks-registry.yaml` 45번째 entry**: `section-1-verbatim-postmerge` (warning tier, deferred-followup status — Phase 2 carrier 신설 후 Active 전환). owner_adr: ADR-027 Amendment 2 §결정 6.C / carrier_adr: ADR-060.
- **`docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md` 신설**: recovery runbook SSOT — enterprise org-cap evidence + Researcher 위험 2종 + Trigger (A)/(C) detection + 7-step procedure + governance ratchet mitigation 3종 + shell injection 차단 + 2-PAT namespace + burst control + Edge case 4종 + sunset criteria.
- **`docs/consumer-guide.md` §1h "Action 차단 환경 fallback" 신설**: consumer runbook — bootstrap.fallback_mode 설정 + manual-story-init-fallback.sh 호출 + 4 required check 통과 의무 + PR description checklist + 2-PAT 모델.
- **`docs/orchestrator-playbook.md` §3.15 "Action-blocked fallback decision tree" 신설**: Orchestrator detection 절차 (lane spawn 직전 의무) + Trigger (C) > (A) 우선순위 + Codex Touchpoint #2 mandatory + env=0 / env=1 동작 동일.
- **`docs/project-config-schema.md` `bootstrap.fallback_mode` enum 등재**: `auto` (default) / `action_blocked`. 우선순위 CLI > env > yaml (ADR-032 정합 일관성).
- **`CLAUDE.md` §"오케스트레이션 규칙" 1-line normative pointer**: Action-blocked fallback path SSOT cross-ref (line cap 330 — `hotfix-bypass:claude-md-line-cap` label 동반 의무, audit-trailed exception channel).
- **3 deputy 산출물 통합**: SecurityArch 4 조건 (post-merge lint + PAT scope + shell injection + audit-trailed channel) + OpRiskArch 4 조건 (PR description checklist + 2-PAT namespace + fallback:rate-limited label + burst control) + DataMigrationArch 1 조건 (existence_check verbatim port) — 모두 addressed.

### Internal-docs (ADR-013 dogfood-out)

- `<internal-docs>/wrapper/specs/2026-05-14-cfp-658-action-blocked-fallback.md` (Phase 0 burst evidence)
- `<internal-docs>/wrapper/stories/CFP-658.md` (Story file §1-§7)
- `<internal-docs>/wrapper/change-plans/cfp-658-action-blocked-fallback.md` (Change Plan §1-§13)

### Sibling sync (separate PR, 선행 merge 의무)

- `mclayer/marketplace` `.claude-plugin/marketplace.json` plugins[name=codeforge].version 5.56.0 → 5.57.0 + description CFP-658 entry append (ADR-063 §결정 5 + §결정 9 atomic invariant — plugin.json MINOR bump 동반 marketplace sync required).

### Deferred (Phase 2 PR scope)

- `templates/scripts/manual-story-init-fallback.sh` (bash, POSIX) + `manual-story-init-fallback.ps1` (Windows parity)
- `templates/github-workflows/section-1-verbatim-postmerge.yml` + `.github/workflows/section-1-verbatim-postmerge.yml` (byte-identical mirror, ADR-005)
- `overlay/hooks/validate_config.py` enum validator (`bootstrap.fallback_mode`)
- `overlay/hooks/tests/test_validate_config.py` TDD red phase
- `.claude/_overlay/project.yaml.example` 갱신
- sibling plugin agent file 갱신 (plugin-codeforge-requirements RequirementsPLAgent.md + plugin-codeforge-design ArchitectPLAgent.md)

## [5.56.1] - 2026-05-14 — CFP-633 Story-2 sibling sync (Epic CFP-620 — mctrader 3-cycle post-mortem)

### Added

- ADR-014 Amendment 3 — ProductionEvidenceDeputy boundary axis 명시 (`policy SSOT vs evidence SSOT` 목적축 분리)
  - §결정 6.1: Boundary axis 1줄 (Story-1 OpRiskArch deputy 산출 verbatim reuse)
  - §결정 6.2: `findings[].owner_axis_kind` enum 신설 (별 CFP-Z carrier reservation, review-verdict-v4 v4.5 → v4.6 MINOR bump 영역)
  - §결정 6.3: Amendment 2 §결정 3 ↔ ADR-72 §결정 2 5번째 cell 3-way 충돌 처리 단락 (chief author 자율 신설, AC-5 carrier 의무 충족)
- Story-1 anchor (ADR-72) sibling sync 완료 (Epic CFP-620 sequential first sibling)

### Notes

- Codex TP#2 3 dispatch converge (1st FIX iter 1 + 2nd FIX iter 2 + 3rd false positive ack)
- ADR-067 cap 2/3 보존 (escalation 회피)
- ADR-064 §결정 8 forbid-list 카테고리 (a) 4 어휘 0 violations (3 file)
- §10 FIX Ledger 8 row 명시 (Orchestrator monopoly, fix-event-v1 v1.2 schema 정합)

## [5.56.0] - 2026-05-14 — CFP-651 marketplace drift fast-forward + ADR-72 bypass_label 단축 정정 (doc-only fast-path, ADR-054)

### Fixed

- ADR-72 frontmatter `mechanical_enforcement_actions[]` 2 entry에 `bypass_label` 필드 신설 + GitHub 50자 제한 정합 단축 값 적용:
  - `hotfix-bypass:production-cutover-deputy-spawn-evidence` (54자) → `hotfix-bypass:prod-cutover-deputy-evidence` (41자)
  - `hotfix-bypass:epic-cutover-gate-evidence-quad-check` (51자) → `hotfix-bypass:epic-cutover-quad-check` (36자)
  - action name 자체 (`production-cutover-deputy-spawn-evidence` / `epic-cutover-gate-evidence-quad-check`) 은 unchanged (evidence-checks-registry entry name = SSOT, ADR-060 §결정 20 정합).
- `docs/evidence-checks-registry.yaml` 2 entry `bypass_label` 필드 동 단축 (action name 영역 외 bypass_label field only).

### Sibling sync (separate PR)

- `mclayer/marketplace` `.claude-plugin/marketplace.json` plugins[name=codeforge].version 5.55.0 → 5.56.0 + description CFP-651 entry append (ADR-063 §결정 5 선행 merge 의무).

## [5.55.0] - 2026-05-14 — CFP-632 Story-1 anchor (Epic CFP-620 — mctrader 3-cycle post-mortem)

### Added

- ADR-72 신설: ProductionEvidenceDeputyAgent (3rd CONDITIONAL deputy, 9th overall) + EPIC CLOSED gate evidence quad. 8 §결정 + frontmatter `mechanical_enforcement_actions[]` 2 entry (production-cutover-deputy-spawn-evidence + epic-cutover-gate-evidence-quad-check, deferred-followup status, warning tier).
- CLAUDE.md "Deputy mandate 매트릭스" 6+2 → 6+3 CONDITIONAL (ProductionEvidence 9th deputy row + ADR-72 cross-ref).
- `docs/evidence-checks-registry.yaml` +2 entry (production-cutover-deputy-spawn-evidence + epic-cutover-gate-evidence-quad-check, deferred-followup status, warning tier).
- `docs/parallel-work/section-ownership.yaml` +1 row (production-evidence-deputy section, owner_adr=ADR-72).
- 3 hotfix-bypass label: `hotfix-bypass:claude-md-line-cap` (기존) + `hotfix-bypass:prod-cutover-deputy-evidence` (NEW) + `hotfix-bypass:epic-cutover-quad-check` (NEW). (주: GitHub 50자 제한으로 원 지시명 단쳙)

### Modified

- `docs/orchestrator-playbook.md` — DesignLane spawn 시 ProductionEvidence trigger 조건 row 추가 (Gap 3 보강).

### Deferred (Phase 1 PR open 후 후속 carrier 영역)

- CFP-Z: review-verdict-v4 v4.5 → v4.6 MINOR bump, owner_deputy_kind enum `production_evidence` 신설.
- CFP-Z’: PMOAgent retro epic_close_gate evidence quad workflow 통합 — Sibling Story-4 plugin-codeforge-pmo#18 prerequisite.

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.54.0 → 5.55.0 mirrored (ADR-063 atomic invariant).

## [5.54.0] - 2026-05-14 — CFP-631 Phase 2 (marketplace-description-verbatim lint script + workflow + bats 13 TC)

CFP-631 Phase 2 실제 구현: `scripts/check-marketplace-description-verbatim.sh` (byte-identical lint, exit 0/1/2 ADR-060 §결정 15 3-tier) + `templates/github-workflows/marketplace-description-verbatim.yml` + `.github/workflows/marketplace-description-verbatim.yml` (ADR-005 self-app byte-identical mirror) + `tests/scripts/test_check_marketplace_description_verbatim.bats` (13 TC all PASS). Phase 1 선언 (§결정 11/12 + evidence-checks-registry entry) 의 mechanical enforce 체인 완성. 7th rebase race sentinel sample (cumulative 7 — CFP-619 + CFP-628 + CFP-631 FIX-1 + CFP-631 Phase 1 + CFP-631 Phase 2 + 2 more).

ADR-037 MINOR bump: script/workflow 신규 추가 (behavior change). plugin.json 5.53.0 → 5.54.0.

### Added

- `scripts/check-marketplace-description-verbatim.sh` — NEW bash lint script. byte-identical compare (trailing newline normalize). Exit 0=PASS / 1=DRIFT / 2=SETUP-error (ADR-060 §결정 15 3-tier). Test override: `CFP631_MARKETPLACE_PATH` / `CFP631_PLUGIN_JSON` env. DRIFT report: first-diff position + 200-char excerpt.
- `templates/github-workflows/marketplace-description-verbatim.yml` — NEW workflow. Trigger: pull_request to main (opened/synchronize/reopened/labeled). blocking-on-pr tier. hotfix-bypass:marketplace-description-verbatim conditional skip + audit comment. permissions: `{}` top-level + job override `contents:read / pull-requests:write` (ADR-060 Amendment 8 정합).
- `.github/workflows/marketplace-description-verbatim.yml` — ADR-005 self-app byte-identical mirror. SHA256: `681dff2222cf5f0327bb29a1b89d1e0f12a9b3341e68169783267002e6895c11` (FIX iter 1 후 갱신).
- `tests/scripts/test_check_marketplace_description_verbatim.bats` — 13 test cases (7 unit + 3 integration + 2 meta SETUP error). All 13 PASS (bats 1.13.0).

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.53.0 → 5.54.0 description mirrored (ADR-063 atomic invariant, Amendment 2 §결정 12 self-application 2nd PR).

## [5.53.0] - 2026-05-14 — CFP-622 (ADR-073 Orchestrator verify-before-assert — Sentinel #4 strike #2 carrier)

### Added

- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` 신설 — Sentinel #4 strike #2 carrier. ADR-070 자매 ADR (external worker output verify ↔ Orchestrator self-assertion verify). cross-repo state + assumption 기술 verify-before-assert 의무. 8 결정 + 3-layer coherence (ADR-070/071/073) + super-class anchor + 2 mechanism enumeration (M1 working tree mutation lag + M2 cross-repo origin lag) + future strike #N append schema.
- `docs/adr/ADR-RESERVATION.md` row 73 (CFP-622).
- `CLAUDE.md` ADR section ADR-073 cross-ref 추가 + L160 ADR-039 단락 압축 (cap residual 회피).
- `skills/codeforge-brainstorm/SKILL.md` Phase 0 자기 적용 의무 sub-section 추가 (verify-before-assert ADR-073 §결정 1 → §결정 6 carrier).

### Cross-ref

- Issue #607 (Sentinel #4 carrier) — strike #2 evidence comment trigger 충족
- Issue #622 (ADR-NNN carrier 예약) — 본 ADR codify
- Sister Epic #635 (CFP-635 over-questioning) — super-class 공유, scope disjoint (cognitive layer)
- ADR-071 (sister governance — dialog convergence) — 사용자 대화 표현 layer 와 분리

### 본 carrier 처리 외 영역

- E-1 hook automation (mechanical enforcement layer) = 별 follow-up CFP
- GitHub API eventual consistency = 별 CFP
- superpowers:writing-plans cross-plugin amend = upstream PR

### Strike #3 — self-application paradox (rebase 정정)

- **상황**: cfp-622 worktree base = 5.48.0 결정 시점에 origin/main 이 이미 5.49.0 (CFP-628) 으로 진행 중. Tasks 3-6 commit `983cf6d` 가 stale base 위 결정 → ADR-073 §결정 1 (verify-before-assert) 의무 위반 사례 (recursive self-application paradox).
- **해소**: cfp-622 를 origin/main `fa69a40` (CFP-628 5.49.0 head) 위로 rebase + version 5.48.0 → 5.50.0 정정 (5.49.0 위 MINOR bump). plugin.json description = CFP-628 sentence (origin/main append) + CFP-622 sentence (cfp-622 append) 둘 다 preserve. CHANGELOG top order = 5.50.0 (CFP-622) > 5.49.0 (CFP-628) > 5.47.0 (older).
- **Verify-before-assert evidence**: 매 step 시작 전 `git fetch origin` + plugin.json description verbatim mirror = `git show origin/main:.claude-plugin/plugin.json` direct verify (PowerShell native execution to avoid PS shell ref-mangling).
- **Story §10 추가 의무**: 본 fix 가 Strike #3 evidence — Story §10 + retro 안 명시 의무 (Task 12 retro 영역 후속 task).

### Strike #4 — continuous self-application paradox (2nd rebase 정정)

- **상황**: PR #109 (marketplace cfp-622 → main) merge attempt 가 두 번째로 origin/main advance 발견. Strike #3 정정 (5.48.0 → 5.50.0) 후 PR open 사이 origin/main 이 또 3 commit advance — `ce3aaee CFP-631 5.50.0 sync` + `e08ce48 CFP-637 5.51.0 sync` + `6eb5890 CFP-638 5.52.0 sync`. wrapper plugin도 동일 stale (cfp-622 5.50.0 vs origin/main 5.52.0).
- **해소**: 양 worktree (wrapper + marketplace) origin/main rebase + version 5.50.0 → **5.53.0** MINOR bump (5.52.0 위) + plugin.json description = origin/main 의 CFP-631+637+638 sentences preserve + CFP-622 sentence append. force-push (--force-with-lease) + PR #109 merge 재시도.
- **Verify-before-assert evidence (Strike #3 보다 강화)**: 매 rebase + push 사이 origin advance 가능 성 명시 — 1 trip 안 (rebase → push → merge attempt) 즉시 진행 의무. Maximum 5 attempts. 5 회 fail 시 사용자 escalation.
- **Recursive self-application paradox 시연**: 본 carrier 가 ADR-073 codify 카리어 인데 codify 전 진행 중 ADR-073 의 정확한 anti-pattern 을 자기 자신이 시연 (Strike #3 + Strike #4 누적). ADR-073 future amendment trigger evidence — N+1 mechanism (continuous race condition during rebase race) 후속 강화 candidate.
- **Story §10 추가 의무**: 본 fix 가 Strike #4 evidence — Story §10 + retro 안 명시 의무 (Task 12 retro 영역 후속 task, Strike #3 와 동일 row group).

## [5.52.0] - 2026-05-14 — CFP-638 (Continuous "진행해" 패턴 mechanical detect — Epic CFP-635 Story D)

Epic [CFP-635](https://github.com/mclayer/plugin-codeforge/issues/635) Story D sister carrier. doc-only fast-path (ADR-054). CFP-637 (Story A+B+C combined) merged 후 base (5.51.0 → 5.52.0 post-CFP-637 atomic realignment).

ADR-064 Amendment 3 §결정 9 sister — Continuous "진행해" 패턴 mechanical detect 영역. Orchestrator 가 직전 N (≥3) user turn 안 "진행해" / "그대로" / "계속" / "ok" / "yes" / "go" / "맞아" pattern 누적 시 후속 turn 의 dialog format (numbered list / decision option) 발화 자동 차단.

ADR-037 MINOR bump: registry entry runtime 활성화 (evidence-checks-registry 44번째 warning-tier entry — advisory only, turn-final hook 부재 platform 한계).

### Added

- `docs/evidence-checks-registry.yaml` 44번째 entry `stop-time-continuous-confirm-detect` (CFP-638, warning tier, advisory only). owner_adr: ADR-064 Amendment 3, carrier_adr: ADR-060, sibling_dependencies: [CFP-637], recurrence count=1 (Epic CFP-635 trigger evidence, 2026-05-14). post-CFP-631 atomic realignment.
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.11 hotfix-bypass:stop-time-continuous-confirm 18번째 family member append. ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합.

### Changed

- `docs/orchestrator-playbook.md` §3.0.14 Question quality 3-check 본문에 Continuous "진행해" 패턴 detect subsection 추가 — pattern 8종 + 3+ 누적 trigger + 5+ strong brevity signal + mechanical layer SSOT cross-ref + 미래 hook 도입 별 CFP follow-up 명시.

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.51.0 → 5.52.0 mirrored (ADR-063 atomic invariant). CFP-637 marketplace sync (#111 merged) 후 base.

### Coordination with sibling Stories

- CFP-637 (Story A+B+C combined, PR #640 MERGED) — 본 PR base.
- CFP-639 (Story E cross-plugin, PR #642) — 본 Story merge 와 독립 진행 가능 (cross-plugin upstream PR 영역).

## [5.51.0] - 2026-05-14 — CFP-637 (ADR-064 Amendment 3 — Over-questioning anti-pattern 차단)

Epic [CFP-635](https://github.com/mclayer/plugin-codeforge/issues/635) Story A+B+C combined carrier. doc-only fast-path (ADR-054). post-CFP-631 atomic realignment (5.50.0 → 5.51.0, rebase race 5th sample).

사용자 directive 2026-05-14 KST (verbatim, Epic body §사용자 directive): "이렇게 물을 필요 없는 질문 방금 왜한거야? 이렇게 된 원인을 심층적으로 파악하고 이 외에도 의미없는질문으로 user stop 걸지 않아야한다. 반드시" — 4-layer root cause + 7 anti-pattern (P1-P7) enumeration carrier.

ADR-037 MINOR bump: CLAUDE.md 의미 변경 (§결정 9 강화 + §결정 10 신설 mirror) + ADR-064 본문 amendment + skill body amend.

### Added

- ADR-064 Amendment 3 frontmatter + amendment_log entry (carrier_story: CFP-637, direction: strengthen, sunset_justification: null — ratchet 강화 방향)
- ADR-064 §결정 9 amendment — Stop-time pre-flight Question quality 3-check (가치 판단 영역 / derived default 자명 / 1-option 자기 검증) + 7 anti-pattern P1-P7 enumeration body
- ADR-064 §결정 10 신설 — Skill body ↔ CLAUDE.md normative priority precedence (CLAUDE.md > ADR > skill body > external skill body). CFP-358 / CFP-374 (Subagent-Driven 자동 선택) generalized normative SSOT.
- ADR-064 Amendment 3 section (Amendment 결정 1-7) — Story A 결정 (§결정 9 amend) / Story B 결정 (skill body amend) / Story C 결정 (§결정 10 신설) / Memory normative 승격 mapping (3 entry) / Self-application + ratchet / review-verdict-v4 영향 0건 / sister Story CFP-638·CFP-639 cross-ref.
- `skills/codeforge-brainstorm/SKILL.md` Phase 1 priority precedence note — dialog format / AskUserQuestion / "사용자 confirm" 지시가 derived default 자명 영역에서 무효 명시.

### Changed

- `CLAUDE.md` `## 결정 원칙` 단락 Trace 5 (Stop-time 평문 정리) → Trace 5/6 통합 + Question quality 3-check + Skill body ↔ normative precedence 본문 추가
- `docs/orchestrator-playbook.md` §3.0.14 — §결정 9 Question quality 3-check + §결정 10 Skill body precedence 본문 추가
- `docs/orchestrator-playbook.md` §3.0.5 — Generalized normative SSOT cross-ref (§결정 10) 추가
- `docs/orchestrator-playbook.md` §3.0.14 duplicate numbering 수정 → §3.0.15 Parallel Dispatch Protocol

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.50.0 → 5.51.0 mirrored (ADR-063 atomic invariant — marketplace 선행 merge → wrapper PR merge, post-CFP-631 realignment)

### Memory normative 승격 (post-merge cleanup)

본 PR merge 후 다음 3 memory entry 삭제 (single-source-of-truth, CLAUDE.md "behavioral directive → memory 금지" normative 정합):

- `feedback_question_quality` → §결정 9 Question quality 3-check
- `feedback_explain_before_ask` → §결정 3 룰 3 + 룰 6 (Amendment 2 carry, 본 amendment 검증 통과)
- `feedback_subagent_driven_auto_select` → §결정 10 generalized precedent

### CLAUDE.md line cap

CLAUDE.md = 327 lines (ADR-012 Amendment 1 ≤320 cap 7 초과). `hotfix-bypass:claude-md-line-cap` label 부착 (CFP-628 / CFP-506 precedent 정합). compression scope = Trace 5 + Trace 6 통합 (Amendment 3 본문 압축 — ADR-064 본문 / playbook 가 detailed SSOT, CLAUDE.md 는 summary mirror).

## [5.50.0] - 2026-05-14 — CFP-631 (ADR-063 Amendment 2 — marketplace description verbatim PR-time proactive lint mandate)

CFP-619 retro §5.2 carry-over — 6 sample 누적 description drift evidence (CFP-387 / CFP-393 / CFP-423 / CFP-597 / CFP-612 / CFP-619). ADR-063 §결정 1 mirrored field invariant 안 `description` field 만 PR-time enforce 부재 (version = `version-bump-atomic-check.yml` blocking-on-pr cover, name/author = `check-marketplace-parity.sh` warning sufficient) → mechanical proactive lint mandate (Amendment 2 §결정 11). Amendment 1 (design-time self-check, CFP-597) 와 layered 2-layer proactive forcing function.

ADR-037 MINOR bump: governance behavior change (Amendment 2 mandate 신설 — blocking-on-pr tier 직접 시작, Phase 2 PR 부터 active enforce). rebase race 4th sample (CFP-619+CFP-628+CFP-631 FIX-1+CFP-631 PR sequence) — base 5.49.0 (CFP-628 Story 2 merge 후 재산정).

### Added

- ADR-063 Amendment 2 본문 — `docs/adr/ADR-063-marketplace-atomic-invariant.md` frontmatter `amendments[1]` row append + §결정 11 (description proactive lint mandate) + §결정 12 (self-application ratchet + 본 carrier 첫 사례 시연 의무).
- `docs/evidence-checks-registry.yaml` — 42번째 entry `marketplace-description-verbatim` append (CFP-628 `retro-alert-pickup-rate` 42번째 entry 위 재편입 → CFP-631 이 43번째로 재배치). owner_adr: ADR-063, carrier_adr: ADR-060, current_tier: blocking-on-pr (ADR-060 §결정 5 default warning explicit exception + §결정 19 Amendment 6 CFP-509 auto_blocking manual gate path — 6 sample 누적 evidence base + 사용자 directive Story §1), bypass_label: `hotfix-bypass:marketplace-description-verbatim` (per-entry namespace, ADR-024 Amendment 3 §결정 6.A 정합, 17번째 hotfix-bypass family member). recurrence: count=6 / threshold=6 / promotion_trigger=auto_blocking / last_occurrence=2026-05-14.
- `docs/inter-plugin-contracts/label-registry-v2.md` — v2.9 → v2.10 PATCH (schema 무변경 — §3 yaml `hotfix-bypass:marketplace-description-verbatim` 17번째 family member append). bootstrap-labels.sh dynamic read 분기 자동 sync (CFP-598).

### Scope split (Phase 1 vs Phase 2)

- **Phase 1 (본 PR)**: ADR-063 Amendment 2 + plugin.json + CHANGELOG + evidence-checks-registry + label-registry-v2 (doc/registry/version bump only).
- **Phase 2 (별도 PR)**: `scripts/check-marketplace-description-verbatim.sh` (bash lint script) + `templates/github-workflows/marketplace-description-verbatim.yml` canonical SSOT + `.github/workflows/marketplace-description-verbatim.yml` byte-identical mirror (ADR-005). Phase 2 PR merge 후 future PR 부터 본 lint 활성 (chicken-and-egg 회피).

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.49.0 → 5.50.0 + description tail 갱신 (CFP-631 carrier note byte-identical) — ADR-063 §결정 1 atomic invariant + Amendment 2 §결정 12 self-application 첫 사례. ordering: marketplace 선행 merge → wrapper Phase 1 PR merge.

### Lane boundary stretch declare

ArchitectPLAgent boundary-stretched §2-§6 (codeforge-requirements@mclayer v0.6.0 plugin available but mechanical scope — §1 사용자 verbatim 6 sample 표 + 변경 영역 7-file delta + Test plan + Related ADR 완결 specify). CFP-619 precedent (Wave 5 동일 cycle) 정합.

### Codex Touchpoint #2 inline FIX

- P1 #1 (citation drift) FIX: ADR-060 "Amendment 4 §결정 16" false citation → "ADR-060 §결정 5 default warning explicit exception + §결정 19 Amendment 6 (CFP-509) auto_blocking manual gate path" 정정 (실제 §결정 16 = warning-tier bypass_label policy, §결정 19 = recurrence-based advisory promotion signal).
- P1 #2 (Phase 1 artifacts missing) FIX: plugin.json 5.49.0 → 5.50.0 + CHANGELOG [5.50.0] + evidence-checks-registry entry + label-registry-v2 entry 본 PR 안 동반 commit (Phase 1 self-application 완료).
- P2 #1 (rate-limit wording) FIX: "single PR 1 call → 영향 0" → "per workflow run 1 call + repeated synchronize events possible; authenticated 5000req/h 한도 안 실질 영향 낮음" 정정.
- P2 #2 (empirical-source rationale-only) FIX: NFR 4행 안 `[empirical-source: ...]` annotation 정밀 — Lint runtime + Workflow trigger latency 2 행 `[empirical-source: TBD]` marker 전환 (ADR-068 Amendment 1 line 94 allowed format), Phase 2 PR 첫 실행 시 actual benchmark 의무.

## [5.49.0] - 2026-05-14 — CFP-628 Story 2 (ADR-045 §D-5 retro alert pickup KPI sentinel)

ADR-045 §D-5 신설 (CFP-628 Story 1, doc-only) 의 Layer (c) 구현 — retro alert pickup rate KPI sentinel script + SessionStart hook sample + monthly cron workflow + evidence-checks-registry entry + KPI seed + label-registry v2.9. ADR-037 MINOR bump: script behavior change (check-retro-alerts.sh SessionStart hook 신규 활성화).

### Added

- **`scripts/check-retro-alerts.sh`** (NEW, bash) — ADR-045 §D-5 retro alert pre-screen script. open `phase:완료` issue 안 `[PMO] retro alert` prefix comment scan. 35min filter (2100초 — retry 4회 완료 latency). exit 0 = no alert, exit 1 = alert detected + stdout prompt-injection (Orchestrator PMOAgent spawn 의무 알림). TDD 4 TC bats PASS (TC-1 no issue / TC-2 alert >35min / TC-3 alert <35min filter / TC-4 ESCALATE prefix skip). ADR-061 정합 (bash + jq, Python heredoc 금지).
- **`tests/scripts/test_check_retro_alerts.bats`** (NEW) — TDD unit test (4 TC PASS). bats framework. gh stub (GH_STUB_RESPONSE_FILE env) 메커니즘. FAIL 먼저 확인 후 script 구현 (TDD 순서 정합).
- **`templates/.claude/hooks/SessionStart-check-retro-alerts.json.sample`** (NEW) — SessionStart hook sample. command: `bash scripts/check-retro-alerts.sh`, blocking: false (non-blocking advisory). ADR-038 Amendment 2 §결정 9 hook tier 패턴 정합.
- **`templates/github-workflows/retro-alert-pickup-kpi.yml`** (NEW) — ADR-060 warning-tier monthly cron KPI workflow. schedule `0 0 1 * *`. 분모 (지난 30일 `[PMO] retro alert` comment 수) / 분자 (30일 retro file 생성 수). `docs/kpi/retro-alert-pickup-rate.json` auto-PR. permissions T1 base (CFP-530 정합).
- **`.github/workflows/retro-alert-pickup-kpi.yml`** (NEW, byte-identical) — self-app. diff 0 lines PASS (AC-6 evidence).
- **`docs/evidence-checks-registry.yaml`** — 42번째 entry `retro-alert-pickup-rate` append. owner_adr: ADR-045, introduced_by: CFP-628, current_tier: warning, bypass_label: `hotfix-bypass:retro-alert-pickup`, sunset_gate: ≥90% 3 month rolling (ADR-058 3-tuple: metric/who/how). schema v1.2 recurrence field 정합 (CFP-509).
- **`docs/kpi/retro-alert-pickup-rate.json`** (NEW, seed) — `{"value": null, "history": [], "schema_version": "1.1", "introduced_by": "CFP-628"}`.
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.9 sub-entry `hotfix-bypass:retro-alert-pickup` (16번째 hotfix-bypass:* family member, ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합).

### Changed

- **`docs/inter-plugin-contracts/label-registry-v2.md`** — version v2.8 → v2.9 (PATCH bump, schema 무변경, §3 yaml row append).
- bootstrap-labels.sh 3-way self-check PASS (58 dry-run lines / 58 invocations / 16 yaml hotfix-bypass rows — 자동 반영, script 직접 수정 불필요).

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.49.0 (marketplace 이미 5.49.0, description에 CFP-628 content append sync — ADR-063 atomic invariant, separate PR #106)

## [5.47.0] - 2026-05-14 — CFP-619 (retro-mandatory.yml workflow deploy — ADR-045 mandate restoration)

CFP-612 retro carrier #1 — `retro-mandatory.yml` workflow 가 `.github/workflows/` 에 미배포 상태 → ADR-045 mandate (PMOAgent retro auto-trigger 5min grace + retry state machine + close-blocking) 의 mechanical enforcement 미작동. CFP-612 Phase 2 PR #618 merge (2026-05-14) 시점 첫 manual fallback observed → 본 carrier 가 sentinel #1 회복.

ADR-037 MINOR bump: script behavior change (신규 workflow runtime 활성화 — 차 Phase 2 PR merge 부터 retro-check job 발화).

### Added

- `.github/workflows/retro-mandatory.yml` (NEW, byte-identical mirror of `templates/github-workflows/retro-mandatory.yml` per ADR-005 self-application invariant — SHA256 `d01bf23f4503049a5afa4336b575e357002467a3b0b5551ccc9b26927f142fd6`). Phase 1 + Phase 2 통합 form (CFP-138 + CFP-290 carrier prior art, FIX iter 1-3 PASS). 3 trigger (pull_request closed / issues closed / schedule cron `*/5 * * * *`) + 3 jobs (retro-check / close-blocking / retry-state-machine).
- `docs/evidence-checks-registry.yaml` — 41번째 entry `retro-mandatory-deployed` append (CFP-610 wording-dictionary 40번째 entry 직후). owner_adr: ADR-045, introduced_by: CFP-619, current_tier: warning, bypass_label: `hotfix-bypass:retro-mandatory-deployed` (per-entry namespace, ADR-024 Amendment 3 §결정 6.A 정합).

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.46.0 → 5.47.0 mirrored (ADR-063 atomic invariant — marketplace 선행 merge → wrapper PR merge)

### Lane boundary stretch declare

본 Story = codeforge-requirements plugin 미로드 영역 (session-level constraint, Story scope 결정 아님) → ArchitectPLAgent 가 §2-§6 (Requirements lane) + §7 (Design lane) 통합 author. ADR-054-grade trivial mechanical scope + retro carrier compressed lifecycle 정합. Story §10.5 Git Ops Log gitops-cfp619-004 row 기록.

## [5.46.0] - 2026-05-14 — CFP-610 Story 2 Phase 2 FIX iter 1 (ADR-064 Amendment 2 mechanical enforcement + marketplace atomic sync)

### Added (CFP-610 Story 2 — wording-dictionary lint)

- **`scripts/check-wording-dictionary.sh`** (NEW) — ADR-064 Amendment 2 wording-dictionary lint script. 카테고리 (a) forbid 어휘 발견 시 exit 1 warning (박제 / 못 박기 / pin / freezing). 카테고리 (b) 어휘 평문 정의 누락 시 exit 0 advisory (normative / sibling sync / kind:contract / ratchet / mirrored field). SSOT: docs/wording-dictionary.md. 5 scope: docs/adr/** / docs/change-plans/** / CLAUDE.md / docs/orchestrator-playbook.md / templates/**. blockquote + fenced code block exempt. docs/wording-dictionary.md 자체 EXEMPT.
- **`tests/scripts/test_check_wording_dictionary.bats`** (NEW) — TDD unit test (17 TC PASS: TC-1~4 + IT-1~3 + CI-1). bats framework. 카테고리 (a) forbid 4 TC + 카테고리 (b) advisory 2 TC + 정의 동반 5 TC + 일반 어휘 2 TC + blockquote/fenced exempt 2 TC + self-app baseline 1 TC.
- **`templates/github-workflows/wording-dictionary.yml`** + **`.github/workflows/wording-dictionary.yml`** (NEW, byte-identical) — ADR-060 warning-tier workflow. continue-on-error: true. hotfix-bypass:wording-dictionary label bypass + audit comment.
- **`docs/evidence-checks-registry.yaml`** — 39번째 entry `wording-dictionary` append. owner_adr: ADR-064, introduced_by: CFP-610, current_tier: warning.
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.6 sub-entry `hotfix-bypass:wording-dictionary` (13번째 hotfix-bypass:* family member). frontmatter version `2.5` 미변경 (same-MINOR additive).
- **`scripts/bootstrap-labels.sh`** — `hotfix-bypass:wording-dictionary` label entry append (label-registry-v2 sync).
- **CLAUDE.md** — Evidence-enforceable 단락 5→6 warning entry / GitHub Workflow 단락 fixture 22→23종.

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.45.0 → 5.46.0 mirrored (ADR-063 atomic invariant)

## [5.45.0] - 2026-05-14 — CFP-612 Wave 5 (ADR-071 Orchestrator-user dialog convergence)

### Closed (CFP-612 Phase 2 — full-lane closure, src/tests = 0, all code-lane N/A)

full-lane Story convention 준수 Phase 2 closure. src/tests 변경 0 — 모든 effective 변경은 Phase 1 (#617) 에 포함. code-lane (Develop/CodeReview/SecurityTest) 모두 N/A 선언. ADR-045 mandate PMOAgent retro auto-trigger 발화 시점 (Phase 2 PR merge 후 5분 grace). Change Plan §10.1 declare: Phase 2 0 commit.

### Added (CFP-612 Phase 1 — Design lane, ADR-071 + playbook §3.14 + skill + Layer 4 file)

CFP-525 Epic ancestor follow-up — Orchestrator-user dialog convergence (Wave 5). Phase 1 PR scope = §1-§7 (ADR + Change Plan + playbook §3.14 + skill SKILL.md + Layer 4 incidents file + CLAUDE.md cross-ref + plugin.json MINOR bump + CHANGELOG + ADR-064 related_adrs append + section-ownership.yaml 2 row append + ADR-RESERVATION row 71 active). 신규 ADR 동반 → ADR-054 §결정 1 full-lane Story 분류 (doc-only fast-path 미적용). src/tests 변경 0.

- `docs/adr/ADR-071-orchestrator-user-dialog-convergence.md` (NEW) — governance permanent (`is_transitional: false`). 본질 anchor (mechanical rule 추종 회피 + 진짜 수렴 dialog) + §결정 1-11 (frame mode 4 step + frame mode 세부 룰 3 종 + 4 layer 검증 + sub-mechanism 2 종 + 사실/가치 결정 트리 + Layer 4 영속 file schema + "추상" keyword semantics + 3 memory entry normative 승격 mapping + CFP-582 conceptual cross-ref schema fit 부적합 declare + scope out + ADR-039 inline whitelist 1번 entry cognitive 강화 declare). `mechanical_enforcement_actions: []` (Wave 5 = cognitive + persistence layer only, Layer 1 mechanical lint 별 follow-up CFP). carrier_story = CFP-612.
- `docs/orchestrator-communication-incidents.md` (NEW) — Layer 4 누적 detection file (cross-Story append-only, Orchestrator monopoly). 8-column schema (iter / timestamp / story_key / pattern_dimension / pattern_summary / trigger / different_dimension_after_halt / escalation_outcome). M=5 lifetime counter, manual reset only. wrapper repo 4번째 cross-Story append-only file 패턴 (FIX Ledger / Git Ops Log / ADR-RESERVATION 정합).
- `skills/user-dialog-mode/SKILL.md` (NEW) — `codeforge:user-dialog-mode` skill. 매 user-facing turn 직전 호출. frame mode 4 step + 4 layer + sub-mechanism 2 종 lookup-table.
- `docs/orchestrator-playbook.md` (UPDATE) — §3.14 Orchestrator-user dialog convergence 신설 (§3.13 debate-protocol-v1 직후). frame mode + 4 layer + sub-mechanism + Layer 4 file + 결정 트리 + memory entry mapping + CFP-582 schema fit 부적합 declare 본문 SSOT. logical position = agent ↔ agent debate (§3.13) ↔ Orchestrator ↔ user dialog (§3.14) 인접 짝.
- `CLAUDE.md` (UPDATE) — Adversarial Debate Protocol 단락에 Wave 5 inline cross-ref 추가 (Wave 4 단락 안 same-paragraph append) + "Lane 진입 시 skill 호출 의무" 표 1 row 추가 (`매 user-facing turn 직전 (사용자 dialog turn)` → `codeforge:user-dialog-mode`). 320 cap compression 동반 — "Deferred tool 선제 로드 (0i)" + "SessionStart hook — worktree-gc (0a-prime)" 두 단락 1 단락으로 merge (net -2 lines, 신규 row 1 line 흡수 후 319/320).
- `docs/adr/ADR-064-decision-principle-mandate.md` (UPDATE) — `related_adrs` field 에 ADR-071 append (본문 변경 0, backward compat). ADR-064 §결정 7 top-down ratchet 정합 — 강화 방향 only.
- `docs/adr/ADR-RESERVATION.md` (UPDATE) — row 71 `reserved → active` 전환. ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent.
- `docs/parallel-work/section-ownership.yaml` (UPDATE) — 2 row append: (1) `docs/orchestrator-playbook.md §3.14` (owner_adr ADR-071, append-only) (2) `docs/orchestrator-communication-incidents.md Incidents` (owner_adr ADR-071, append-only, arbitrator = orchestrator-self-write monopoly).
- `.claude-plugin/plugin.json` (UPDATE) — version 5.44.0 → 5.45.0 MINOR + description CFP-612 Wave 5 entry (3rd rebase — CFP-598 P2 version collision resolved).

### Codex Proactive Check #2 + #6 (CFP-612 carry-over to DesignReview lane)

- **Touchpoint #2** (ArchitectAgent §3 / Change Plan §3 완료 직후) — DIVERGENCE_DETECTED 1 P1 finding (anchor `CFP-612-W5-S2-E9-E11-TURN-SHAPE` semantic-2 category): Story §5.3 Edge Case E9 streaming token / E10 tool-call-only / E11 AskUserQuestion popup turn-shape default 가 ADR-071 + playbook §3.14 + skill 모두 미명시 (E12 trivial answer 만 cover). **Inline FIX applied (ADR-052 Amendment 4 §결정 10 mandatory)** — playbook §3.14 "Turn-shape derived defaults" 표 3 row append (E9/E10/E11) + ADR-071 §결정 3 4 layer 표 turn-shape edge cross-ref + skill SKILL.md "Turn-shape edge 분기" 4 row table append. 모든 RequirementsPL §5.3 `[fact-check-pending]` marker resolved. verify-before-trust (ADR-070) Orchestrator 측 direct file Read 로 finding ground truth 확인 완료.
- **Touchpoint #6** (ArchitectAgent ADR 초안 완료 직후) — ADR-071 draft 완료 직후 single-shot Codex check (FIX-1 적용 후 ADR-071 자체 = 330 lines, 신규 inline FIX 영역 reflect). 추가 divergence 미발견 expected.

### 3 memory entry normative 승격 (Phase 2 PR merge 시점 effective)

- `feedback_explain_before_ask` → playbook §3.14 (frame mode 본문 SSOT) + ADR-071 §결정 1 step 4 + §결정 4 sub-mechanism 1
- `feedback_question_quality` → playbook §3.14 (frame mode 본문 SSOT) + ADR-071 §결정 2 (b) + §결정 5 결정 트리
- `feedback_subagent_driven_auto_select` → **변경 없음** (playbook §3.0.5 기존 정책 유지, codeforge wrapper side SSOT 변경 0)

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.44.0 → 5.45.0 mirrored (ADR-063 atomic invariant, marketplace_sync_required: true — 3rd rebase sync PR cfp-612-codeforge-5.45.0-sync)

## [5.44.0] - 2026-05-14 — CFP-598 Phase 2 (bootstrap-labels.sh hotfix-bypass:* dynamic sync)

CFP-530 retro carrier #2 (Phase 2) — `bootstrap-labels.sh` hotfix-bypass:* family dynamic sync + label-registry-v2 §3 yaml first-class backfill (pre-existing leak 해소). ADR-037 MINOR bump: script behavior change (13 hotfix-bypass:* label 동적 생성 신규).

### Added

- `docs/inter-plugin-contracts/label-registry-v2.md` v2.5 → v2.7 PATCH bump:
  §3 yaml block 안 hotfix-bypass:* 13 row first-class 추가 (category: hotfix-bypass,
  color: fef2c0, 기존 §변경 이력 prose-only → yaml 정규화). ADR-008 §결정 3 PATCH 정합.
- `scripts/parse-hotfix-bypass-labels.py` 신설 (ADR-061 외부 .py 의무):
  label-registry-v2.md §3 yaml block parse → stdout name\tcolor\tdescription.
  yaml.safe_load 의무 / isinstance guard / Path.is_file() / exit 4-tier (0/1/2/3).
- `scripts/bootstrap-labels.sh` hotfix-bypass:* dynamic read 분기 신설:
  component:* 직전 삽입. REGISTRY_MD env override + SCRIPT_DIR 절대 경로.
  process substitution `< <(...)` — subshell 회피로 LABEL_COUNT 부모 증분 보장.
  DRY_RUN + actual 양 모드 모두 처리 (canonical-only).
- `scripts/check-bootstrap-labels-count.sh` 3-way parity 확장 (CFP-598):
  기존 2-way (dry-run lines == invocations) +
  3rd: §3 yaml hotfix-bypass:* row count == dry-run hotfix-bypass lines.
  exit 0 PASS / exit 1 drift / exit 2 meta-error.
  sanity check: 55 lines == 55 invocations, yaml 13 rows == dry-run 13 lines.

### Phase 1 산출물 (CFP-598 Phase 1 PR #602, merged main)

- `wrapper/change-plans/2026-05-13-cfp-598-bootstrap-labels-hotfix-bypass-sync.md` (internal-docs)
- `wrapper/stories/CFP-598.md` §1-§9 (internal-docs)

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.43.0 → 5.44.0 mirrored + description CFP-598 entry append (ADR-063 atomic invariant, sibling PR #98 MERGED 선행 2026-05-14T00:02:42Z)

## [5.43.0] - 2026-05-14 — CFP-609 (ADR-064 Amendment 1 + parallel-dispatch-protocol-v1)

### Added (CFP-609 — parallel-dispatch-protocol-v1 신설 + ADR-064 Amendment 1 mechanical enforcement Phase 1)

- **`docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md`** 신설 (kind:registry, wrapper canonical, sibling sync 면제) — ADR-064 §결정 4 Trace 4 "Orchestrator multi-task spawn default = parallel" normative declaration 의 execution-time enforcement contract. 4 의무 항목 (plan DAG verbatim 박제 / PL 자율 병렬 권한 명시 / sequential mandate enum 명시 / file-level conflict resolution 패턴) + 6 sequential mandate enum (close-set) + PL 자율 병렬 결정 tree 4-분기 + env=0/1 동등성 + consumer overlay defaults.
- **`docs/inter-plugin-contracts/MANIFEST.yaml`** `registries:` 행 `parallel-dispatch-protocol-v1` append.
- **`docs/evidence-checks-registry.yaml`** entry `parallel-dispatch-prompt-check` append — ADR-060 evidence-enforceable framework warning tier (ADR-064 Amendment 1 §결정 4 carrier).
- **`scripts/check-parallel-dispatch-prompt.sh`** + **`scripts/check_parallel_dispatch_prompt.py`** — Orchestrator → PL spawn prompt 내 `[Parallel Dispatch Hint]` block 유무 + sequential 의무 영역 명시 여부 검증 lint (exit-code 0/1/2 tri-tier, ADR-060 Amendment 2 §결정 15 정합).
- **`templates/github-workflows/parallel-dispatch-prompt-check.yml`** (warning tier, `continue-on-error: true`, bypass label `hotfix-bypass:parallel-dispatch-prompt`).
- **`templates/team-spec-requirements.yaml`** 6-way teammates 정합 (ADR-056 gap absorb — CFP-609 absorb).
- **ADR-064 Amendment 1** frontmatter `amendment_log` + `mechanical_enforcement_actions[]` 갱신 — parallel-dispatch-prompt-check binding.
- **`docs/orchestrator-playbook.md`** §3.0.14 신설 — Parallel Dispatch Protocol 운영 매뉴얼 (registry §4 full schema 요약 + 4 의무 항목 + 6 enum + 4-분기 cross-ref, DRY 구조).
- **`overlay/_overlay/project.yaml.example`** consumer overlay `parallel_dispatch` defaults 섹션 추가.

**trigger**: consumer mctrader MCT-159 Phase 2 55min wall-clock sequential bias 실측 (mctrader-data#49).

### Added (CFP-598 Phase 1 — Design lane, plumbing only)

CFP-530 retro carrier #2 — `bootstrap-labels.sh` hotfix-bypass:* family dynamic sync + §3 yaml backfill (pre-existing leak). Phase 1 PR scope = Change Plan + Story §1-§9 only (no src/scripts/registry edit). Phase 2 PR (별 carrier) 가 6 file 변경 + marketplace 5.42.0 → 5.43.0 sibling PR.

- `wrapper/change-plans/2026-05-13-cfp-598-bootstrap-labels-hotfix-bypass-sync.md` (internal-docs) — Change Plan §1-§14 author by ArchitectAgent chief (5 deputy synthesis: CodebaseMapper + DataMigrationArch + SecurityArch + TestContractArch + Refactor). ADR audit: 신규 0건, 기존 9 ADR 정합 (ADR-024 A3 §6.A + A4 §6.A.1 / ADR-063 §2 / ADR-061 §1·§3 / ADR-064 §1 / ADR-065 §1 #1 / ADR-008 §3 / ADR-037 / ADR-010 §2 / ADR-013).
- `wrapper/stories/CFP-598.md` §1-§9 (internal-docs) — RequirementsPL §1-§6 + ArchitectPL §3·§7·§11 + Orchestrator §9.1 DesignReview PASS + §9.2 Codex proactive check #2 FIX-1 record.
- **Codex proactive check #2** (ADR-052 Amendment 4 / CFP-532 mandatory) — P0:0 / P1:3 inline FIX-1 (F-3 base count / F-5 exit-code semantic / F-6 §8 test intent anchor) / P2:3 skip rationale.
- **DesignReviewPL iter 1 = PASS** (review-verdict-v4 v4.4, 3 self-check 모두 verified true).

## [5.42.0] - 2026-05-13 — CFP-582 Phase 2 (ADR-059 Amendment 2 enforcement)

### Changed (CFP-582 Phase 2 — debate convergence quality lint)

- **CFP-582 Phase 2 / ADR-059 Amendment 2 §결정 8 enforcement**: `scripts/check_debate_convergence_quality.py` 신설 (3 marker regex pattern lint — `[COUNTERARGUMENT]` / `[ALTERNATIVE_PROPOSED]` / `[DEBATE_PURPOSE_STATEMENT]`). Story §9 debate transcript section 탐지 후 marker presence 검증. exit-code 0/1/2 tri-tier (ADR-060 Amendment 2 §결정 15 정합).
- **`templates/github-workflows/debate-convergence-quality.yml`** + **`.github/workflows/debate-convergence-quality.yml`** (byte-identical self-app) — warning tier workflow (continue-on-error: true). Story 파일 변경 PR 시 trigger.
- **`docs/evidence-checks-registry.yaml`** entry `debate-convergence-quality-marker-presence` append — ADR-060 evidence-enforceable framework warning tier 첫 debate 영역 entry. owner_adr: ADR-059, carrier_adr: ADR-059.
- **ADR-061 Python script-writing convention 정합** — heredoc 금지 + Write tool 외부 .py 파일 작성.

### Sibling sync (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.41.0 → 5.42.0 mirrored (ADR-063 atomic invariant)

## [5.41.0] - 2026-05-13 — CFP-582 Wave 4 (ADR-059 Amendment 2)

### Added (CFP-582 Wave 4 — DesignLane blanket adversarial debate + convergence_quality_invariant, ADR-059 Amendment 2)

Wave 4 of Epic-FIX-ESCALATION-prevention (#525) — ADR-059 Amendment 2 carrier. 사용자 directive "반론 수용 + 대안 발의 + 토론 목적 = 최적 구조" 의 mechanical enforceable invariant 명문화. doc-only fast-path (ADR-054) — src/tests 무변경.

- `docs/adr/ADR-059-debate-protocol-v1.md` — Amendment 2 append (§결정 7: DesignLane blanket trigger + cross-module Story 정의 heuristic inline / §결정 8: convergence_quality_invariant 3 marker pattern / §결정 9: Touchpoint #2 carry-over 의무 / §결정 10: lane-agnostic registry 정합).
- `docs/inter-plugin-contracts/debate-protocol-v1.md` — v1.1 → v1.2 MINOR bump. `blanket_cross_module_designlane` dispatch_mode 4번째 enum value + `convergence_quality_invariant` block schema (counterargument_present / alternative_proposed_count / debate_purpose_statement_present) + Touchpoint #2 carry-over field + version_history row.
- `docs/inter-plugin-contracts/MANIFEST.yaml` — debate-protocol-v1 version row 1.1 → 1.2 갱신.
- `CLAUDE.md` — Adversarial Debate Protocol 단락 갱신 (blanket dispatch 4번째 enum value + 3 marker pattern + convergence_quality_invariant 3-tuple AND + Touchpoint #2 carry-over 절차).
- `docs/orchestrator-playbook.md` — DesignLane blanket trigger 진입 절차 (§3 blanket invocation flow + convergence_quality_invariant gate + Touchpoint #2 forward).
- `docs/domain-knowledge/domain/agent-teams/convergence-quality-invariant.md` (NEW) — 3-tuple 정의 + measurable signal + ADR-059 Amendment 2 carrier link.
- `docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md` — 변경 이력 row append (blanket dispatch_mode + convergence_quality_invariant 추가).
- `.claude-plugin/plugin.json` — version 5.40.0 → 5.41.0 MINOR + description CFP-582 Wave 4 entry append.

### Sibling sync (separate PRs)

- mclayer/marketplace#85: plugins[codeforge].version 5.40.0 → 5.41.0 mirrored (ADR-063 atomic invariant)
- mclayer/plugin-codeforge-design#40: ArchitectPLAgent Phase 0.5 Blanket Adversarial Debate Trigger (cross-module Story 자동 발동 + Touchpoint #2 carry-over + convergence_quality_invariant gate)
- mclayer/plugin-codeforge-review#32: review-pl-base §11.5 debate-protocol-v1 v1.2 cross-ref + 3 marker pattern verification 책무
- mclayer/marketplace#87: codeforge-design 0.11.0 + codeforge-review 1.6.0 sibling sync mirror

## [5.40.0] - 2026-05-13 — CFP-507 DeveloperPLAgent Phase 2 PR body composition convention codification

### Added (CFP-507 — Lane evidence heading 1회 inject convention, ADR-031 §결정 3 정합)

CFP-490 (#490, merged) §7.5 origin investigation 의 carrier — `## Lane evidence` first heading auto-include 의 actual origin 정정. 가설 (wrapper PR template 부재 → DeveloperPL spawn template) 은 **verified false**, 실제 origin = codeforge-develop DeveloperPLAgent body composition convention 부재 + wrapper Orchestrator manual append 정책 부재 결합.

- `docs/orchestrator-playbook.md` (UPDATE) — §3.0.13 신설 "PR description `## Lane evidence` manual append 정책 (CFP-507)". 3-step 절차 (heading 존재 check → row append only / heading 재추가 금지 → 부재 시 heading + 7-row template inject) + Story §14 Lane Evidence row append 동시 turn 처리 의무 (ADR-031 정합) + 위반 시 `lane-evidence-check.yml` 5a duplicate guard 발화 (CFP-490 §결정 1 정합). codeforge-develop sibling plugin `agents/DeveloperPLAgent.md` "Phase 2 PR body composition convention" section 와 짝 (sibling 0.5.2 → 0.6.0 MINOR bump).
- `.claude-plugin/plugin.json` — version 5.39.0 → 5.40.0 MINOR + description CFP-507 entry append.

### Doc-only fast-path (ADR-054 §결정 1) — src/tests 0건 + 신규 ADR 0건 + ADR Amendment 0건

본 Story = doc-only fast-path 분류. 설계 lane 진입 후 ArchitectPLAgent chief author self-execute (6 permanent deputy + 2 CONDITIONAL deputy spawn 0 — mandate 정합 0). Self-check verdict packet: `mechanical_self_check_passed: true` (ADR-065 vacuous truth) + `boundary_completeness_self_check_passed: true` (ADR-068 wording SSOT cross-ref) + `dimensional_empirical_self_check_passed: true` (ADR-068 Amendment 1 count dim empirical-source annotated). 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 lane SKIPPED.

### Sibling sync (separate PRs)

- mclayer/plugin-codeforge-develop — `agents/DeveloperPLAgent.md` "Phase 2 PR body composition convention" section 신설 + `.claude-plugin/plugin.json` 0.5.2 → 0.6.0 MINOR
- mclayer/marketplace — `.claude-plugin/marketplace.json` `plugins[name=codeforge]` version 5.39.0 → 5.40.0 mirror + `plugins[name=codeforge-develop]` version 0.5.2 → 0.6.0 mirror (ADR-063 §결정 5 atomic invariant — concurrent merge gate)

## [5.39.0] - 2026-05-13

> Note: Version 5.38.0 reserved by CFP-582 (marketplace PR #85 open). CFP-585 jumps to 5.39.0 to avoid concurrent reservation collision (ADR-037 sequential bump rule).

### Fixed (CFP-585 — version-bump-atomic-check workflow Bypass audit comment permission)

본 세션 4 Stories (CFP-491/509/508/492) 모두 hit한 `atomic-check` workflow "Bypass audit comment" step 실패의 root cause 정정. `permissions:` block 가 `contents: read` only — `gh pr comment` 호출 시 `pull-requests: write` 누락으로 GraphQL "Resource not accessible by integration (addComment)" 실패. 정정 후 admin merge 불필요화.

- `templates/github-workflows/version-bump-atomic-check.yml` (UPDATE) — `permissions:` 에 `pull-requests: write` 추가
- `.github/workflows/version-bump-atomic-check.yml` (UPDATE, ADR-005 self-application byte-identical)
- `.claude-plugin/plugin.json` — version 5.37.0 → 5.39.0 MINOR (5.38.0 reserved by CFP-582)

## [5.37.0] - 2026-05-13 — CFP-529 Wave 3 Phase 2

### Added (CFP-529 Wave 3 Phase 2 — handoff wording linter, ADR-068 §결정 5 / ADR-060)

Wave 3 Phase 2 mechanical impl carrier — handoff wording drift detector. ADR-068 §결정 5 `wording-ssot-grep-lint` evidence-enforceable framework warning-tier 8번째 entry mechanical impl. Phase 1 (PR #579 stack base) = declarative SSOT (severity-propagation-v1 contract + MANIFEST + registry row). 본 Phase 2 PR = mechanical script + tests + workflow + self-app + plugin.json 5.36.0 → 5.37.0 MINOR + CHANGELOG.

- `scripts/check_handoff_wording.py` (NEW, ~600 LOC, ADR-061 정합 외부 `.py`) — handoff wording drift mechanical detection. Scope 5 영역 (`scripts/**` / `templates/**` / `tests/**` / `docs/**` / `CLAUDE.md`). Direction enum 3-way: forward (ADR 식별자 verbatim 매칭 → impl 부재 시 info) / backward (impl 식별자 reverse-lookup → ADR/contract 부재 시 warning, Amendment trigger SSOT) / lateral (Story §3 ↔ §7 ↔ §8.5 cross-section diff). Drift 패턴 8종 — mechanical 5 (synonym_substitution / unit_drift / modal_downgrade / boundary_inversion / scope_widening) + AI escalate stub 3 (precision_loss / conditional_erasure / actor_drift). Exempt regions 3종 (dictionary body marker / verbatim quote `>` lines / consumer overlay `.claude/_overlay/`). Exit code tri-tier (ADR-060 Amendment 2 §결정 15): 0 (PASS or warning tier with findings) / 1 (strict mode with findings) / 2 (root path absent).
- `tests/scripts/test_check_handoff_wording.py` (NEW, ~370 LOC unittest) — 26 test cases: mechanical patterns (5) + AI escalate stubs (4) + direction enum (3) + exit code (4) + exempt regions (3) + arg parse (4) + formatters (3). Tempdir fixture isolation. All 26 PASS.
- `templates/github-workflows/handoff-wording-check.yml` (NEW) + `.github/workflows/handoff-wording-check.yml` (NEW self-app byte-identical mirror). `continue-on-error: true` warning tier. Bypass channel `hotfix-bypass:boundary-wording` label (ADR-024 Amendment 3 정합) + audit comment 자동 발의 + bypass audit assertion.
- `.claude-plugin/plugin.json` — version 5.36.0 → 5.37.0 MINOR + description CFP-529 Wave 3 Phase 2 entry append.

### Sibling sync (separate PRs)

- mclayer/marketplace: marketplace.json plugins[codeforge].version 5.36.0 → 5.37.0 mirrored (ADR-063 atomic invariant — 본 PR merge 전 선행 merge)

## [5.36.0] - 2026-05-13

### Added (CFP-530 — workflow yml permissions hardening, ADR-060 Amendment 8)

Workflow yml `permissions:` block 일괄 hardening (`.github/workflows/` 6 + `templates/github-workflows/` 8 = 16 file). GitHub Actions least-privilege standard 정합 — GITHUB_TOKEN 명시적 scope 제어. 14 MISSING + 2 job-level upgrade 대상 모두 T1 base (`contents: read`), `superpowers-schema-drift.yml` pair 는 TH-7 sealed (top-level deny + schedule job override `issues: write` event-conditioned). `scripts/check-workflow-permissions-presence.sh` mechanical lint + `templates/github-workflows/workflow-permissions-check.yml` warning-tier workflow + self-app byte-identical mirror (`workflow-permissions-check.yml` `.github/workflows/` 동시 신설). evidence-check-registry-v1 row append `workflow-permissions-block-presence` (9번째 entry), label-registry-v2 v2.5 same-MINOR sub-entry append (`hotfix-bypass:workflow-permissions` 10번째 family member). ADR-024 Amendment 정합, ADR-063 atomic invariant 발효 (plugin.json 5.35.0 → 5.36.0 + CHANGELOG + marketplace.json 3-file atomic sync).

- `.github/workflows/` 6 file `permissions: contents: read` top-level prepend
- `templates/github-workflows/` 8 file `permissions: contents: read` top-level prepend + 2 pair byte-identical mirror
- `templates/github-workflows/superpowers-schema-drift.yml` + `.github/workflows/superpowers-schema-drift.yml` job-level `issues: write` override (TH-7 sealed)
- `scripts/check-workflow-permissions-presence.sh` (NEW) + exec bit
- `templates/github-workflows/workflow-permissions-check.yml` (NEW) warning-tier workflow
- `.github/workflows/workflow-permissions-check.yml` (NEW self-app mirror)
- `docs/evidence-checks-registry.yaml` row append `workflow-permissions-block-presence` (9번째 entry, ADR-060 Amendment 8 §결정 21)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.5 same-MINOR sub-entry append (`hotfix-bypass:workflow-permissions` 10번째 family, ADR-024 Amendment 정합)
- `.claude-plugin/plugin.json` — version 5.35.0 → 5.36.0 + description CFP-530 row append

## [5.35.0] - 2026-05-13 — CFP-528 Wave 2B

### Added

- **ADR-068 Amendment 1** — I-5 dimensional empirical grounding invariant 신설 (4 → 5 invariants, ratchet 강화). 10 dimension enum (latency/scale/cardinality/throughput/cost/accuracy/lifecycle/volume/rate/count) 의 quantitative parameter 마다 `[empirical-source: <ref>]` 또는 `[empirical-source: TBD]` annotation 의무. empirical-absent default lock-in 차단 (#319 RETRO-MCT-104 carrier).
- **review-verdict-v4 v4.3 → v4.4 MINOR bump** — `dimensional_empirical_self_check_passed: bool` optional field + `findings[].type: "dimensional-empirical-gap"` literal. ArchitectAgent verdict packet 셋 별도 boolean field (mechanical + boundary_completeness + dimensional_empirical) 동시 PASS 의무.
- **mechanical_enforcement_actions[] 3번째 entry** — `dimensional-empirical-grounding` (status: deferred-followup, target_section: §결정 1).

### Closed

- **#319 (RETRO-MCT-104)** — keep-linked + close as absorbed. distinct failure-class but systemic super-class (empirical-grounded design discipline). ADR-052 Amendment 3 (touchpoint #4 fact-check) cover specific case + CFP-528 dimensional sensitivity discipline 일반화.

### Sibling sync (separate PRs)

- mclayer/marketplace: marketplace.json plugins[codeforge].version 5.34.0 → 5.35.0 mirrored (ADR-063 atomic invariant)
- mclayer/plugin-codeforge-design: ArchitectAgent.md / ArchitectPLAgent.md I-5 self-check step (parallel sibling PR)
- mclayer/plugin-codeforge-review: review-pl-base.md §3 I-5 mechanical detection rule + review-verdict-v4 canonical v4.4 (parallel sibling PR)
- mclayer/codeforge-internal-docs: wrapper/stories/CFP-528.md 신설

## [5.34.0] - 2026-05-13

### Added
- **[ESC#525 CFP-527]** Boundary completeness 4-invariant governance ADR-068 신설 (Wave 2A of Epic-FIX-ESCALATION-prevention). ADR-068 governance permanent (`is_transitional: false`) — 4 invariants (API contract semantic / cross-module propagation / guard placement intent / wording SSOT) + dual-binding (design author + code-review cross-validate) + review-verdict-v4 v4.3 MINOR bump (`boundary_completeness_self_check_passed` + `findings[].type: "boundary-completeness"`) + wording-ssot-grep-lint warning-tier evidence-enforceable (8번째 entry). #438 absorption — ADR-065 (mechanical syntactic) 와 ADR-068 (semantic) 분리 운영 (verdict packet 양 별도 boolean field).

## [5.33.0] - 2026-05-13

### Changed
- **[ESC#525 CFP-526]** fix-ledger RESET 정책 + implementability reassessment + reasoning carryover (Wave 1 of Epic-FIX-ESCALATION-prevention). ADR-067 신설 (fix-ledger implementability escalation, governance category) + fix-event-v1 v1.1 → v1.2 MINOR bump (reasoning_carryover optional field, 3-part structured YAML) + skill `codeforge:fix-ledger-schema` 4 bullet 본문 확장 + orchestrator-playbook §6.4/§6.5/§6.6 신설 + CLAUDE.md FIX 루프 cross-ref. 사용자 directive 2026-05-13 carrier — FIX 3회 초과 시 ArchitectPL 재량 implementability 평가 + 사용자 escalation 의무 trigger 3종 (ESCALATE root cause / cross-module invariant / N+1 round divergence). Case study source = mctrader-hub MCT-150 §10 4 FIX cycle.

## [5.32.0] - 2026-05-13

### Added (CFP-492 — lint hardening: bootstrap-labels self-check + measure exit 4 context-aware)

CFP-451 P2 advisory 2건 통합 (PMOAgent 발의 #5). bootstrap-labels.sh 에 `LABEL_COUNT` counter + DRY_RUN 모드 stderr report 추가, `scripts/check-bootstrap-labels-count.sh` 신설하여 dry-run output line count ↔ counter 2-way verify (drift detection 자동화). measure-rate-limit-fallback.sh exit 4 SONNET_AGENTS enum drift 검출을 ADR 본문 `## 결정` / `### 결정 N:` block scope 안으로 한정 (awk state machine — false-positive 회피, deprecated section / 거절 대안 영역 무시).

- `scripts/bootstrap-labels.sh` (UPDATE) — LABEL_COUNT counter + DRY_RUN stderr report
- `scripts/check-bootstrap-labels-count.sh` (NEW) — 2-way verify lint
- `scripts/measure-rate-limit-fallback.sh` (UPDATE) — exit 4 section-aware awk parsing
- `tests/scripts/test_bootstrap_labels_count.sh` (NEW, 3 case)
- `tests/scripts/test_measure_rate_limit_fallback_section_aware.sh` (NEW, 2 case)
- `.claude-plugin/plugin.json` — 5.31.0 → 5.32.0 MINOR

## [5.31.0] - 2026-05-13

### Added (CFP-508 — evidence-registry-naming convention lint, ADR-060 Amendment 7)

evidence-checks-registry 32 entry name ↔ workflow file naming convention 검증 (Conservative no-rename policy). `scripts/check-evidence-registry-naming.sh` (file existence + allowlist DRIFT advisory). multi-job workflow pattern 정식 인정 (contract-lint.yml + lint.yml). §결정 20 신설. 7번째 warning-tier evidence-enforceable entry.

- `scripts/check-evidence-registry-naming.sh` (NEW)
- `tests/scripts/test_check_evidence_registry_naming.sh` (NEW, 3 case)
- `templates/github-workflows/evidence-registry-naming-check.yml` (NEW, warning mode)
- `.github/workflows/evidence-registry-naming-check.yml` (NEW, self-app byte-identical)
- `docs/evidence-checks-registry.yaml` — evidence-registry-naming entry append (7번째 warning-tier)
- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — Amendment 7 + §결정 20 신설
- `.claude-plugin/plugin.json` — version 5.30.0 → 5.31.0 MINOR

## [5.30.0] - 2026-05-13

### Changed (CFP-509 — evidence-check-registry schema v1.1 → v1.2 MINOR bump)

ADR-060 Amendment 6 carrier — `recurrence:` field 정식 도입 (optional object: count / last_occurrence / threshold / promotion_trigger) + §결정 19 신설 (recurrence-based advisory promotion signal) + 32 entry retroactive migration (lane-evidence-trail count=2 historical evidence 흡수, 31 entry count=0 default). schema validation lint 확장. backward-compat 100% (recurrence 미정의 entry 모두 정상 PASS).

- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` (UPDATE) — schema v1.1 → v1.2 MINOR (recurrence field schema + v1.2 historical row)
- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` (UPDATE) — Amendment 6 + §결정 19 신설
- `docs/evidence-checks-registry.yaml` (UPDATE) — 32 entry recurrence field migration
- `scripts/check-evidence-registry.sh` (UPDATE) — recurrence field validation
- `.claude-plugin/plugin.json` — version 5.29.0 → 5.30.0 MINOR

## [5.29.0] - 2026-05-13

> Note: Rebased twice onto main HEAD due to concurrent CFP-521 merges (#523 sibling-pr lint = 5.27.0; #524 PAT rotation = 5.28.0; CFP-462-followup marketplace batch #70). CFP-491 jumps to 5.29.0 to maintain ADR-037 sequential bump invariant.

### Added (CFP-491 — AC mapping cross-ref lint — F-001 Option C systematization)

`scripts/check-impl-manifest-ac-mapping.sh` + `tests/scripts/test_check_impl_manifest_ac_mapping.sh` + `templates/github-workflows/ac-mapping-cross-ref-check.yml` + `.github/workflows/` self-app (ADR-005) + `docs/evidence-checks-registry.yaml` ac-mapping-cross-ref entry (ADR-060 Amendment 6 6번째 warning-tier entry). Story §8.5 Impl Manifest 의 AC id 인용 ↔ §5.1 AC 정의 cross-reference 검증 (1차 단순화 = 2-way only). 기본 mode = LLM trust (exit 0 + stderr advisory), --strict mode + workflow continue-on-error:true defense in depth.

- `scripts/check-impl-manifest-ac-mapping.sh` (NEW)
- `tests/scripts/test_check_impl_manifest_ac_mapping.sh` (NEW)
- `templates/github-workflows/ac-mapping-cross-ref-check.yml` (NEW)
- `.github/workflows/ac-mapping-cross-ref-check.yml` (NEW, self-app)
- `docs/evidence-checks-registry.yaml` (UPDATE) — ac-mapping-cross-ref entry append (6번째 warning-tier entry)
- `.claude-plugin/plugin.json` — version 5.28.0 → 5.29.0 MINOR

## [5.28.0] - 2026-05-13

### Added (CFP-521 — CODEFORGE_CROSS_REPO_PAT rotation policy + ADR-066)

EPIC-RESULTS CFP-462 §6 carrier #3. CFP-450 (ADR-013 Amendment 4) PAT consolidation 후속 — 단일 `CODEFORGE_CROSS_REPO_PAT` (cross-repo Story binding + KPI internal-docs clone) 의 lifetime / rotation / compromise response / audit log SSOT 신설. 권장 rotation 90 days / 최대 lifetime 180 days. Scope minimum 3종 (`repo:read` + `repo:write` + `metadata:read`). 5-step rotation 절차 + 4-step compromise response 명문화. Audit log SSOT 신설 (`docs/security/pat-rotation-log.md`, 사용자 manual entry 의무). 자동 만료 reminder workflow + audit log schema lint 는 Phase 2 carrier (별도 CFP — ADR-066 `mechanical_enforcement_actions: []`). Consumer overlay `security.pat_rotation_cadence_days` 강화 방향 override 허용 (weaken 금지). `is_transitional: false` (security default presumption, ADR-058 정합).

- `docs/adr/ADR-066-pat-rotation-policy.md` (NEW) — 7 결정 (cadence / scope / 절차 / compromise / audit / 자동화 carrier / consumer overlay)
- `docs/adr/ADR-RESERVATION.md` (UPDATE) — ADR-066 row append
- `docs/security/pat-rotation-log.md` (NEW) — Audit log SSOT (rotation history 표 + schema + compromise response cross-ref)
- `docs/consumer-guide.md` (UPDATE) — §1g 신설 (rotation cadence / scope / 절차 / compromise / audit / consumer overlay)
- `CLAUDE.md` (UPDATE) — GitHub Workflow 단락 blockquote cross-ref 1줄 추가 (cap ≤320 정합)
- `.claude-plugin/plugin.json` — version 5.27.0 → 5.28.0 MINOR (sibling-pr lint 5.27.0 merge 후 rebase)

## [5.27.0] - 2026-05-13

### Added (CFP-521 — sibling-pr label anti-misuse lint, EPIC-RESULTS-CFP-462 §6 carrier #2)

ADR-010 Amendment 4 §결정 5 anti-misuse 안전망 mechanical enforcement. `sibling-pr` label 부착 PR 의 paired wrapper PR link (`mclayer/plugin-codeforge#NNN` 패턴 — short form + URL form 양쪽) 검증. 부재 시 audit comment 부착 + workflow failure (warning tier, advisory only — PR merge 미차단). Guard 3종 (sibling-pr label 미부착 skip / hotfix-bypass label 부착 skip / wrapper repo self-PR skip) + audit comment dedup (`[sibling-pr-anti-misuse]` marker). ADR-060 evidence-enforceable framework **5th warning-tier entry** (1st = adr-sunset-criteria / 2nd = decision-principle-vocab / 3rd = auto-phase-label / 4th = claude-md-line-cap). `hotfix-bypass:sibling-pr-author-check` **9번째 hotfix-bypass:* family member** (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합). CFP-499 sibling-pr fast-pass mechanism 의 anti-misuse 안전망 forcing function — Orchestrator self-write 영역 (CFP-61 / ADR-035) enforce.

> **CFP # 정정 (2026-05-13)**: 본 entry 의 "CFP-521" 은 sibling-pr lint Story 의 wrong-CFP anomaly (실제 Issue # = 522, 정정된 CFP # = CFP-522, Story file 은 cleanup PR #285 으로 rename 완료). 본 description 의 텍스트 reference 는 descriptive only 로 보존 — functional 영향 0건.

- `templates/github-workflows/sibling-pr-label-author-check.yml` (NEW) — wrapper SSOT fixture, actions/github-script-based 2-step workflow (paired link 검증 + audit comment 부착)
- `.github/workflows/sibling-pr-label-author-check.yml` (NEW, self-app byte-identical, ADR-005 self-application 정합)
- `docs/evidence-checks-registry.yaml` (UPDATE) — `sibling-pr-label-author-check` entry append (5th warning-tier, status=Active)
- `docs/inter-plugin-contracts/label-registry-v2.md` (UPDATE) — v2.4 sub-entry append + frontmatter `related_adrs` ADR-010 추가 + `hotfix-bypass:sibling-pr-author-check` 9번째 family member 문서화
- `CLAUDE.md` (UPDATE L291) — workflow 갯수 22 → 23 / 4 evidence-enforceable warning → 5 / 새 entry 1줄 inline 추가
- `.claude-plugin/plugin.json` — version 5.26.0 → 5.27.0 MINOR (workflow 변경, ADR-037 plugin SemVer rule)

#### Why

axis-A (governance — ADR-010 Amendment 4 §결정 5 anti-misuse 후행 carrier 의무): CFP-499 (ADR-010 Amendment 4) 가 `sibling-pr` label fast-pass mechanism 도입 시 §결정 5 (anti-misuse 안전망) 가 후행 CFP carrier 의무 명문화. EPIC-RESULTS-CFP-462 §6 후행 carrier #2 로 식별. axis-B (mechanical enforcement — Orchestrator self-write 영역 정합): label 자체에 author check 없음 → human user 부착 시 phase-gate bypass 악용 가능. PR body grep `mclayer/plugin-codeforge#NNN` 패턴 검증으로 paired wrapper PR link evidence enforce. axis-C (warning tier conservatism — ADR-060 §결정 5 첫 도입 = warning): advisory only, PR merge 미차단. 승격 path = pr_cumulative_min 20 + failure_threshold 0 도달 시 별도 carrier 가 blocking-on-pr 평가.

## [5.26.0] - 2026-05-13

### Added (CFP-506 — CLAUDE.md skill 추출 + cap ratchet ≤320 + mechanical lint forcing function)

4 신규 skill 추출 (lane-self-write-boundary / story-cutoff-classification / inter-plugin-contract-registry / story-epic-flow-preflight) + CLAUDE.md 434줄 → 309줄 압축 (cap 320 대비 11줄 headroom) + `scripts/check-claude-md-line-cap.sh` lint script + `templates/github-workflows/claude-md-line-cap.yml` warning-tier workflow (ADR-060 Amendment 5 4번째 warning-tier entry). ADR-012 Amendment 1 cap ≤380 → ≤320 ratchet 강화. ADR-051 Amendment 1 Draft → Accepted + anchor vs reference 판정자 §결정 신설.

- `skills/lane-self-write-boundary/SKILL.md` (NEW)
- `skills/story-cutoff-classification/SKILL.md` (NEW)
- `skills/inter-plugin-contract-registry/SKILL.md` (NEW)
- `skills/story-epic-flow-preflight/SKILL.md` (NEW)
- `CLAUDE.md` (UPDATE) — 434줄 → 309줄 압축
- `scripts/check-claude-md-line-cap.sh` (NEW)
- `templates/github-workflows/claude-md-line-cap.yml` (NEW)
- `.github/workflows/claude-md-line-cap.yml` (NEW, self-app)
- `docs/evidence-checks-registry.yaml` (UPDATE) — claude-md-line-cap entry append
- `docs/orchestrator-playbook.md` (UPDATE) — §1.1 0a-prime 신설
- `.claude-plugin/plugin.json` — version 5.25.0 → 5.26.0 MINOR

## [5.25.0] - 2026-05-13

### Changed (CFP-510 — ADR-052 Amendment 3 touchpoint #4 divergence detection 영역 확장)

CFP-451 (#451) + CFP-490 (#490) 0-FIX chain 7-8번째 retro PMOAgent FU-4 (low severity) carrier. ADR-052 Amendment 1 (CFP-411) 의 touchpoint #4 divergence detection 3 semantic criteria 에 **4번째 영역 = fact-check** 추가. 사실 영역 (registry-execution drift / pre-existing leak / file path verification / cross-repo state verification) 의 implicit 발화를 explicit normative anchor 로 승격. PL self-evaluation 의무 = synthesis fact claim 영역 marker 5종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]` / `[verification-out-of-scope: <사유>]`) — fact-check 영역 divergence detection false negative 차단 forcing function. debate-protocol-v1 dispatch 흐름 변경 없음 (divergence_type enum 확장은 별도 carrier CFP). MINOR bump (CLAUDE.md SSOT mirror 영향 + ADR amendment).

- `docs/adr/ADR-052-codex-proactive-check-touchpoints.md` (UPDATE) — Amendment 3 본문 append (A1~A8 결정 + 거절된 대안 H~K). amendments[] frontmatter row 추가.
- `CLAUDE.md` (UPDATE L188) — Codex Proactive Check blockquote 갱신: divergence 영역 = 3 semantic + 1 factual = 4 영역 명시 + marker 5종 의무 inline.
- `.claude-plugin/plugin.json` — version 5.24.0 → 5.25.0 MINOR (rebased onto main HEAD post-CFP-453 merge). description CFP-510 entry append.
- Sibling sync: `mclayer/plugin-codeforge-requirements` 0.5.1 → 0.6.0 MINOR (RequirementsPLAgent.md "Divergence detection 4 영역" + "PL self-evaluation 의무" 단락 + codex-proactive-check.md "Fact-check 영역" 단락).
- Marketplace sync (`mclayer/marketplace` `marketplace.json` `plugins[name=codeforge]` + `plugins[name=codeforge-requirements]` mirrored field — name/version/description/author atomic, ADR-063 §결정 5).

#### Why

axis-A (governance — fact-check 영역 explicit normative anchor): 양 retro evidence 2회 누적으로 implicit 발화 영역 normative 승격 timing 도달. axis-B (PL synthesis quality — marker 5종 forcing function): "가설" vs "verified" 영역 구분 의무 부재 → Codex fact 발견 시 PL LLM 판정 false negative 위험 차단. axis-C (lane-agnostic protocol 확장 보존): debate-protocol-v1 dispatch 흐름 변경 없음 — divergence_type 영역만 확장 (separate carrier CFP 가 enum MINOR bump 처리).

### Added (CFP-462 Epic close + CFP-438)

- **CFP-438** ADR-065 — ArchitectAgent Phase 1 mechanical sync self-check 7-item checklist (non-marketplace 영역). change-plan template §13 self-check 결과 섹션. ArchitectPLAgent verdict packet `mechanical_self_check_passed: bool` schema forward.
- **CFP-462** Epic close — 5 child Story 통합 처리 완료 (CFP-448 / 451 / 450 / 453 / 438).

### Changed (CFP-462)

- `docs/inter-plugin-contracts/review-verdict-v4.md` — v4.1 → v4.2 MINOR (`mechanical_self_check_passed` optional bool field 추가, ADR-008 §결정 2 정합). wrapper sibling sync.

### Sibling sync (Epic CFP-462 close)

- `codeforge-design` 0.7.0 → 0.9.0 — ArchitectAgent §5.5 self-check + ArchitectPLAgent verdict forward + change-plan §13.
- `codeforge-review` 1.3.0 → 1.4.0 — review-verdict-v4 canonical v4.2 MINOR.
- `marketplace.json` — 3 plugin atomic sync (codeforge / codeforge-design / codeforge-review).

## [5.24.0] - 2026-05-13

### Changed (CFP-453 Phase 2 — KPI history.jsonl 누적 정책)

CFP-393 (ADR-057 Amendment 2 / fallback rate KPI dashboard, merged #398) 의 best-effort 확장. latest snapshot only 한계 4종 (trend 분석 / sunset gate 시점 추적 / sample size 누적 / regression detection) broad coverage 해소. JSONL 1 line per monthly cron 누적 + idempotency rule (동일 month 재실행 = 마지막 줄 교체) + KPI JSON schema 1.0 → 1.1 MINOR bump. MINOR plugin version bump (ADR-037 정합 — `templates/github-workflows/**` + `scripts/` + schema 변경).

- `docs/kpi/rate-limit-fallback-history.jsonl` (NEW, 0 byte git-tracked) — append-only JSONL, 1 entry per monthly cron. Schema: `{measured_at, month, sonnet_spawn_total, fallback_count, rate, gate_status, sample_size_sufficient, partial_data}`.
- `scripts/measure-rate-limit-fallback.sh` (UPDATE) — `--history-out <jsonl-path>` option 추가. 미지정 시 backward-compat (history 무영향). 지정 시 window 마지막 month bucket 의 1 entry append. Idempotency: last entry month 가 새 entry 와 동일 = 마지막 줄 교체 (atomic via `head -n -1 + tmp + mv`). file 부재 시 graceful create (`mkdir -p` 동반).
- `docs/kpi/rate-limit-fallback.json` (UPDATE) — `schema_version: "1.1"` + `history_file: "docs/kpi/rate-limit-fallback-history.jsonl"` 필드 추가. backward-compat (history field 도입 X 시 ignore).
- `templates/github-workflows/rate-limit-fallback-kpi.yml` (UPDATE) — aggregate step `args+=(--history-out docs/kpi/rate-limit-fallback-history.jsonl)` 추가 + auto-PR step `git add docs/kpi/rate-limit-fallback-history.jsonl` 추가. 단일 PR 통합 (KPI JSON + history.jsonl 동일 PR, auto-PR noise 회피).
- `.github/workflows/rate-limit-fallback-kpi.yml` (UPDATE) — byte-identical self-app copy (ADR-005 정합).
- `docs/parallel-work/section-ownership.yaml` (UPDATE) — history.jsonl append-only row 추가. owner_adr = ADR-057. NOTE: workflow-only-write semantic (사용자 manual edit 금지, CFP-393 KPI JSON row 와 동일 NOTE 패턴).
- `tests/scripts/measure-rate-limit-fallback/test_aggregator.sh` (UPDATE) — T-11 (idempotency, 4 assertion) / T-12 (graceful create, 3 assertion) / T-13 (multi-month accumulation, 4 assertion) 신규 + `assert_line_count` helper. 총 19 → 30 assertion (CFP-393 baseline 보존).
- `.claude-plugin/plugin.json` — version 5.23.0 → 5.24.0 MINOR (ADR-037 정합 — `templates/github-workflows/**` + `scripts/` 변경, ADR Amendment 본문 변경 0건). description CFP-453 Phase 2 entry append.

### Sibling sync (ADR-016 + ADR-063 atomic invariant)

- `marketplace.json` 4 mirrored field sync — **본 PR scope 외**, Epic CFP-462 close 시 single marketplace sync PR 일괄 처리 전략. `hotfix-bypass:marketplace-atomic` label 부착 (24h drift window 발생 → audit comment 자동 발의 인지, ADR-063 §결정 5 정합).
- 6 lane plugin sibling — 영향 0건 (contract schema 변경 0, agent file 변경 0).

### Why

CFP-393 (ADR-057 Amendment 2) KPI dashboard 가 latest snapshot only — trend / sunset gate 시점 / sample size 추이 / regression detection 4 한계 보유. ADR-057 §결정 2 sunset gate "3개월 연속 < 1%" 충족 시점이 historical evidence 부재. 본 Story = history.jsonl 누적으로 4 한계 동시 해소. visualization tool / retention policy / sunset gate 자동 발화 = 별도 carrier (Story §1 본문 명시 — future CFPs).

### Compatibility

- **Wire**: 영향 0건 — `--history-out` 미지정 시 기존 동작 보존 (backward-compat).
- **KPI JSON schema**: 1.0 → 1.1 MINOR (`schema_version` + `history_file` 필드 추가). 기존 consumer (visualization tool 부재) 무영향. forward-compat verified.
- **Test contract**: T-11/T-12/T-13 신규 — 기존 T-1~T-10 regression 0건.
- **Sibling plugins**: 영향 0건 (contract schema 변경 0).

## [5.23.0] - 2026-05-12

### Changed (CFP-490 Phase 2 — lane-evidence-check duplicate heading collision auto-detection 강화)

ADR-031 §결정 3 (lint cross-validate) 의 enforcement layer logic refinement. CFP-465 (#482, cc5d7c3) 가 도입한 5a duplicate guard (line 113-128) 의 잔여 gap 4종 해소 — (a) summary 메시지 단순 count → tie-break case A/B/C 식별 + valid heading 명시 + 삭제 target 권고, (b) tie-break decision 부재 → Case A (1 valid) / Case B (0 valid) / Case C (2+ valid) 분기, (c) recurrence count documentation 부재 → registry description 본문 명시, (d) origin 식별 부재 → first-match capture boundary + DeveloperPL spawn template 가설 documentation. Option A strict 채택 (CFP-465 invariant 보존, lenient fallback 폐기 — ADR-031 §결정 2 "1회 heading 의무" 정합). `.mjs` extraction 채택 (testability rationale — bash heredoc `node -e` simulate 한계 초과, 6 test_function 29 assertion path coverage 측정). MINOR bump (workflow yml 변경 + .github script 신설).

- `templates/github-workflows/lane-evidence-check.yml` (UPDATE line 112-143) — 5a guard 강화: `analyzeDuplicateHeadings()` import + tie-break case A/B/C summary + ADR-031 §결정 2 정책 인용 + DeveloperPL spawn template 가설 documentation comment.
- `.github/workflows/lane-evidence-check.yml` (UPDATE) — ADR-005 byte-identical self-app mirror.
- `.github/scripts/check-lane-evidence-block.mjs` (NEW, 116 line) — `analyzeDuplicateHeadings(body)` 함수 export. Case A/B/C tie-break + valid_heading_idx + invalid_idx_list 식별. `actions/github-script@v7.1.0` 안 dynamic import (ESM/CJS 호환).
- `tests/workflows/test_lane-evidence-check-yml.sh` (NEW, 252 line, 6 test_function 29 assertion) — Case A/B/C path coverage + strict mode + fast-pass invariants + BYPASS honor + cross-cutting (byte-identical + .mjs presence + dynamic import) 검증. base64 body encoding 으로 cross-platform 안전 (Git Bash MSYS2 path translation 회피).
- `docs/evidence-checks-registry.yaml` (UPDATE) — `lane-evidence-trail` entry description 본문에 actual recurrence (CFP-500 FIX-5 1차 + CFP-451 본 세션 2차) + logic refinement (CFP-490 Phase 2) 명시. schema 무영향 — machine-usable promotion signal 아님 (ADR-060 4-tier 무관).
- `.claude-plugin/plugin.json` — version 5.22.1 → 5.23.0 MINOR (workflow yml + .github script 신설, ADR-037 정합).

### Sibling sync (ADR-016 + ADR-063 atomic invariant)

- `marketplace.json` 4 mirrored field sync 의무 — name/version/description/author. **본 PR scope 외, Orchestrator escalation 영역** (DeveloperPL 책임 외). marketplace sync PR open 후 atomic check PASS 의무.

### Why

CFP-500 FIX-5 (#456, merge 직전 1차 actual collision) + CFP-451 본 세션 transient (#486 step 3 2차 actual) 의 2회 actual recurrence — 단일 defense (5a heading-count guard) 가 작동하나 valid heading 식별 부재 + tie-break decision 부재 + fix-guide weak (수동 삭제 안내만, 어느 heading 인지 명시 안 함). 본 Story = 잔여 gap 해소. 신규 ADR 0건 — ADR-031 §결정 3 의 enforcement layer 내부 logic refinement.

### Compatibility

- **Wire**: 영향 0건 — ADR-031 effective date 보존 (retroactive 미처리, §결정 5 정합).
- **Existing valid PR**: 영향 0건 (5 capture + 6 step 동작 변경 0, 5a 만 강화).
- **In-flight Phase 2 PR with duplicate heading**: 본 Story merge 후 첫 push 부터 강화된 summary 발화 — fix 부담 줄어듦 (어느 heading 이 valid 인지 명시).
- **codeforge-develop sibling**: AC-9 origin investigation 결론 — DeveloperPL agent body composition 영역의 first heading auto-inject 정정은 별도 carrier CFP (sibling lane plugin scope).

## [5.22.1] - 2026-05-12

### Changed (CFP-448 Phase 2 — Sonnet selective rollback 구현)

ADR-057 Amendment 3 + ADR-042 Amendment 5 (Phase 1 PR #488 merged) 의 Phase 2 구현. 6 agent decision matrix 정합 — N=3 Sonnet rollback (CodebaseMapper / Refactor / DeveloperPL) + 3 Opus 유지 (Feasibility / Continuity / ChangeImpact). mandate text 재정의 N'=2 (CodebaseMapper / Refactor — ChangeImpact exclusion criterion 정합). PATCH bump (CLAUDE.md mirror + script 배열 변경, 정책 본문 변경 0건).

- `CLAUDE.md` (UPDATE L164 cross-ref note) — "ADR-057 §결정 3 표 = SSOT, CLAUDE.md L127 = mirror reference" 1줄 명시 (CL-6 사용자 확정 / drift forcing function).
- `scripts/measure-rate-limit-fallback.sh` (UPDATE) — SONNET_AGENTS 배열 5종 → 8종 (3 entry append: CodebaseMapperAgent / RefactorAgent / DeveloperPLAgent). header 주석 + drift detection 코멘트 cross-ref Amendment 3 갱신.
- `.claude-plugin/plugin.json` — version 5.22.0 → 5.22.1 PATCH (ADR-037 정합 — CLAUDE.md mirror + script 배열 변경, ADR Amendment 본문 변경 0건). description CFP-448 Phase 2 entry append.

### Sibling sync (ADR-016 + ADR-063 atomic invariant — Phase 2 PR pair)

- `plugin-codeforge-develop` 0.5.0 → 0.5.1 PATCH — DeveloperPLAgent model field Opus → Sonnet (사용자 framing 직접 적용 — ADR-042 §결정 1 (b) verbatim 회귀, mandate text 0건 — 이미 implementation work 정의 명확).
- `plugin-codeforge-design` 0.6.0 → 0.7.0 MINOR — CodebaseMapperAgent / RefactorAgent model field Opus → Sonnet **+ mandate text 재정의** (description frontmatter + 본문 mandate boundary section).
- `plugin-codeforge-requirements` 영향 0 (ChangeImpactAgent Opus 유지).
- `marketplace.json` 3 entry sync — **본 PR scope 외**, Epic CFP-462 close 시 일괄 처리 (24h drift window 발생 → audit comment 자동 발의 인지, ADR-063 §결정 5 hotfix-bypass:marketplace-atomic 채널 외 normal merge).

### Why

CFP-393 회고에서 발견된 3-way drift (CLAUDE.md L127 8종 / ADR-057 §결정 3 5종 / agent file 실측 4종) 의 reverse direction 해소. CLAUDE.md L127 8종이 정합인 상태로 회복 — 3 agent (CodebaseMapper / Refactor / DeveloperPL) Opus → Sonnet 복귀. 사용자 framing 진화 — 초기 결정 (ChangeImpact + Mapper + Refactor) 에서 새 framing ("코드 작성 agent = Sonnet, 고도 추론 불필요" + "ChangeImpact 는 Opus 가 괜찮음") 적용 후 swap. ADR-042 §결정 1 (b) "Implementation work" verbatim 정합. mandate text 재정의로 ADR-042 §결정 2 invariant ("Sonnet 으로 fully cover 가능 = role 재정의 시그널") 정합 강제.

### Compatibility

- **Wire**: codeforge-{requirements,design} >= 0.5.0 (sibling sync 의무).
- **Contract version**: 본 PR 의 contract schema 변경 0건 (review-verdict-v4 / develop-output-v1 / requirements-output-v1 / design-output-v2 / fix-event-v1 모두 unchanged).
- **Marketplace**: 3-file atomic invariant (ADR-063) — 본 PR 은 24h drift window scope (Epic CFP-462 close 시 sync). 별도 PR 으로 marketplace.json 3 entry version sync 의무.
- **ADR-053 재구동 의무**: agent definition 변경 = 구조적 변경. Phase 2 merge 후 consumer 측 marketplace install + plugin version drift check 의무.

## [5.22.0] - 2026-05-12

### Added (CFP-475 — ADR-038 Amendment 3 hooks/hooks.json plugin-root SSOT + polyglot wrapper + plain stdout SSOT)

CFP-500 (#417 CLOSED) Phase 2 in-vivo verify (#471) FAIL implementation bug fix. **Root cause** (G3 PoC SMOKING GUN): `.claude/settings.json` line 78-87 command 안 잉여 `codeforge/` segment. **Paradigm shift** (Researcher Round 4 evidence triple-anchor: code.claude.com/docs/en/hooks + anthropics/claude-code#14281 + obra/superpowers#648): JSON output 의무 → **plain stdout SSOT** (JSON form 은 `suppressOutput` 동반 시에만).

- `docs/adr/ADR-038-progress-visualization-todowrite.md` (UPDATE — Phase 1 PR #493) — Amendment 3 §결정 10·11·12·13·14 신설:
  - §결정 10: Hook 등록 위치 SSOT = plugin-root `hooks/hooks.json` (first-class). settings.json fallback deprecated.
  - §결정 11: Polyglot wrapper pattern (superpowers 5.1.0 verbatim copy-adapt + MIT attribution).
  - §결정 12: One-channel rule + plain stdout SSOT (double-injection 회귀 회피).
  - §결정 13: `BYPASS_CODEFORGE_PREREQ` env contract + stderr 1-line audit echo + `BYPASS_PREREQ_CHECK` deprecation grace.
  - §결정 14: frontmatter `mechanical_enforcement_actions[]` self-application (ADR-040 Amendment 3 §결정 7.D 두 번째 사례).
- `hooks/hooks.json` (NEW) — plugin-root SSOT (superpowers 5.1.0 schema verbatim, matcher `startup|clear|compact`).
- `hooks/run-hook.cmd` (NEW) — Windows CMD polyglot dispatcher (superpowers 5.1.0 verbatim copy-adapt + MIT attribution 5-line header).
- `hooks/session-start` (NEW, executable) — extensionless naming, plain stdout SSOT body + 2 BYPASS env handling + stderr audit echo.
- `scripts/check-no-duplicate-session-start-hook.sh` (NEW, executable) — 회귀 lint, exit code 3-tier (0/1/2), bash + jq fallback, `hotfix-bypass:duplicate-session-start-hook` label conditional skip.
- `templates/github-workflows/duplicate-session-start-hook-check.yml` (NEW) — CI gate warning mode (`continue-on-error: true`), bypass label audit comment auto-post.
- `tests/unit/test-session-start-hook.sh` (NEW) — §8.1-T2 + T6 control char grep verbatim assertion (Story §3.4.0 결정 3) + BYPASS env verify (12/12 test PASS).
- `tests/unit/test-no-duplicate-session-start-hook.sh` (NEW) — §8.1-T3 5 fixture matrix F1-F5 + exit code 3-tier verify (5/5 fixture PASS).
- `.claude/settings.json` (UPDATE) — prereq-check entry 제거 (line 71-80 splice, worktree-stale entry 무손상).
- `CLAUDE.md` (UPDATE) — "세션 개시 의무 (필수 의존성 SSOT)" 0i 영역 갱신 (plugin-root SSOT, settings.json fallback deprecated).
- `docs/consumer-guide.md` (UPDATE) — §2h.1 갱신 (plugin discovery 자동 활성, sample deprecation 안내).
- `docs/evidence-checks-registry.yaml` (UPDATE) — `duplicate-session-start-hook-check` entry append (warning tier, schema v1.1, ADR-038 owner).
- `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` (DEPRECATION HEADER) — `_deprecated_since: 5.22.0` + `_migration` + `_scheduled_removal: 5.23.0` 3 field prepend.
- `scripts/check-codeforge-prereq.sh` + `tests/scripts/test_check_codeforge_prereq.sh` (REMOVED) — logic inline 통합 (hooks/session-start), test 동반 폐기.
- **plugin.json description retain** (CFP-451/448/481 entries 잔존) — ADR-063 atomic invariant 면제 (mirrored field 변경 0). version 5.22.0 (CFP-451/448/481 concurrent merge window 정합).
- **marketplace.json sibling sync 면제** — mirrored field 변경 0 (description retain), 별도 sync PR 불요.

### Why (CFP-475)

CFP-500 forcing function 효과 0건 측정 — path mismatch root cause 해소 + 공식 SSOT 정합 (plugin-root `hooks/hooks.json` first-class) + consumer scope 확장 (`/plugins install` 단독 자동 활성). debate-protocol-v1 4 round (Codex divergence → Researcher Round 4 evidence preserved + paradigm shift 발견).

### Compatibility (CFP-475)

backward-compatible — consumer `/plugins install` 자동 활성 (G2 PoC PASS evidence), manual action 0. `BYPASS_PREREQ_CHECK` env 1 release deprecation grace (5.23.0 제거 예정).

### Related Issues (CFP-475)

CFP-475 (#475) / CFP-500 (#417 CLOSED, in-vivo verify #471 carrier) / Phase 1 PR mclayer/plugin-codeforge#493 + mclayer/codeforge-internal-docs#251.

---

### Added (CFP-451 — codeforge-kpi-infra-error label + sub-axis 다축 완결 + KPI workflow infra error 분기)

CFP-393 ADR-057 fallback rate KPI dashboard 의 후속 — workflow 가 두 가지 다른 종류의 실패 (measurement alert vs infra error) 를 단일 label channel 로 발화하던 한계 해소. monitoring tier sub-axis 다축 완결 (info / warn / error). 추가로 Codex F-451-001 (a) 사전 leak 정정: `codeforge-kpi-update` label 이 workflow line 237 에서 사용 중이었으나 label-registry-v2 + bootstrap-labels.sh 부재 — registry-execution drift 정정.

- `docs/inter-plugin-contracts/label-registry-v2.md` (UPDATE) — v2.2 → v2.3 MINOR bump. **2 entry append**:
  - `codeforge-kpi-infra-error` (color `d73a4a` red — severity / oncall) — KPI workflow infrastructure failure marker
  - `codeforge-kpi-update` (color `0e8a16` green — info / data refresh) — pre-existing CFP-393 leak 정정
  - monitoring tier sub-axis 다축 완결: info (update) / warn (alert) / error (infra-error). count 33+ → 35+.
- `scripts/bootstrap-labels.sh` (UPDATE) — monitoring 영역 1 → 3 entry. count echo "31 base label" → "33 base label" (component:* 동적 별도).
- `templates/github-workflows/rate-limit-fallback-kpi.yml` (UPDATE) — infra error 분기 추가:
  - aggregate step `set -uo pipefail` 전환 (errexit 분리) + `exit_code=$?` capture + `GITHUB_OUTPUT` export
  - `Create or update auto-PR` step `id: auto_pr` 부여 (detect_infra outcome 캡처 가능)
  - 신규 step `Detect infra error` (id: detect_infra, if: always()) — clone fail / aggregate exit code 1/2/3/4/* / auto_pr failure 분기, case `*)` fallback default
  - 신규 step `Open infra error issue` — `gh issue create --label codeforge-kpi-infra-error` 발화 (dedup: window 단위)
  - Summary step `infra_error` + `infra_error_reasons` 출력 추가
  - 기존 `Open KPI alert issue` step `if:` 조건 **변경 0** — dual-open semantics 보존 (Story §5.5 결정 3 verbatim)
- `.github/workflows/rate-limit-fallback-kpi.yml` (UPDATE) — templates 와 byte-identical self-app copy (ADR-005)
- `scripts/measure-rate-limit-fallback.sh` (UPDATE) — exit code 3 (internal-docs scan failure) + exit code 4 (SONNET_AGENTS enum drift) 추가. 0/1/2 기존 시맨틱 유지. header 주석 multi-line block.
- `tests/workflows/test_rate-limit-fallback-kpi-yml.sh` (UPDATE) — 4 신규 test_function:
  - `test_aggregate_exit_code_capture` (AC-12 — PL 신규, Story §5.1 row 부재 / CP §1.3 + §3.5 + §8.1 단일 source / DesignReview F-001 Option C 안전망)
  - `test_detect_infra_step_exists` — case 분기 + `*)` fallback + exit 3/4 sub-reason
  - `test_open_infra_issue_step_exists` — `--label codeforge-kpi-infra-error` 부착
  - `test_alert_dual_open_with_infra_error` — alert step `if:` 조건이 detect_infra 미참조 verify
  - main() 14 test 등록 (10 기존 + 4 신규)
- `.claude-plugin/plugin.json` — version 5.21.0 → 5.22.0 MINOR (workflow 변경 동반 ADR-037). description CFP-451 entry append.
- `marketplace.json` (sibling) — plugins[name=codeforge] version + description sync (ADR-063 atomic invariant — 3-file coordination 의무).

---

## [5.21.0] - 2026-05-12

### Added (CFP-449 — forbid-list 어휘 mechanical lint + evidence-enforceable 2nd warning-tier entry)

CFP-445 ADR-064 §결정 2 forbid-list 8 어휘 dictionary 의 mechanical enforcement carrier. CFP-388 evidence-enforceable framework (ADR-060) 의 2nd warning-tier entry — 1st entry `adr-sunset-criteria` 와 schema 정합 cross-validation 신호.

- `scripts/check-decision-principle-vocabulary.sh` (NEW) — Python heredoc lint script. 8 forbid 어휘 (임시 / 단계적 / 일단 / 우선 / 잠정 / 가벼운 / minimal viable / quick win) detection in 5 scope 영역 (`docs/adr/**` / `docs/change-plans/**` / `CLAUDE.md` / `docs/orchestrator-playbook.md` / `templates/**`). Exempt = markdown blockquote + fenced code + EXEMPT_PATHS (ADR-064 self / ADR-RESERVATION / registry yaml / script self / bats fixture self). Exit code 3-tier (0=PASS / 1=violation / 2=meta-error — ADR-060 Amendment 2 §결정 15).
- `templates/github-workflows/decision-principle-vocabulary.yml` (NEW) — warning mode (`continue-on-error: true`). PR trigger + 5 scope paths filter. `hotfix-bypass:decision-principle-vocab` label conditional skip + audit comment 자동 발의 (ADR-060 §결정 8 schema). bypass audit assertion lint (`check-bypass-audit-comment.sh` reuse).
- `docs/evidence-checks-registry.yaml` row append (`decision-principle-vocab` entry, 23rd entry). 본 framework 2nd warning-tier entry — `owner_adr: ADR-064` + `carrier_adr: ADR-060` + `sibling_dependencies: []` (독립 entry).
- `tests/scripts/test-check-decision-principle-vocabulary.bats` (NEW, 15 test case) — Happy path 1 + Forbid detection 3 + Scope filtering 3 + Exempt 영역 5 + Edge case 3. `tests/scripts/` 디렉터리 신설 (bats 첫 진입 사례).
- `CLAUDE.md` "GitHub Workflow" 단락 — 19종 → 20종 fixture, 1 evidence-enforceable warning → 2 evidence-enforceable warning 갱신.
- `.claude-plugin/plugin.json` description append CFP-449 entry (mirrored field — marketplace sibling sync 의무).

### Why

ADR-064 §결정 8 declaration only — mechanical enforcement 는 CFP-449 별도 carrier 분리. ADR-060 evidence-enforceable framework 가 2nd entry 도입을 통해 multi-entry 운영 검증 + 점진 승격 patterns 의 cross-validation 신호 확보. 작성자 자발 준수 + DesignReview 1차 안전망 의존의 한계 (forbid 어휘 reflex 사용 시 detection 부재) 해소.

### Compatibility

- consumer overlay 영향 = 정책 축소 불허 (lint script + workflow + registry entry 신설). `.claude/_overlay/project.yaml` extension 만 허용.
- lint = warning tier (ADR-060 §결정 5), PR merge 미차단. blocking 승격은 framework gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 통과 후 별도 CFP carrier.
- bypass channel = `hotfix-bypass:decision-principle-vocab` label + PR description `### Bypass reason` (ADR-024 Amendment 3 §결정 6.A). audit comment 자동 발의 — 정책 회피 등록 차단 (ADR-064 §결정 5 정합).
- 6 lane plugin 영향 = 0 (wrapper level lint, lane plugin self-write boundary 무변경).
- ADR-060 Amendment 3 (Phase 1 PR #470 merged 2026-05-12) — `hotfix-bypass` 채널 의미 sharpening 1줄 + amendment_log row 3 추가. 강화 방향 amendment (ratchet 위반 0건).
- Marketplace sibling sync 의무 = `version` 5.20.0 → 5.21.0 + `description` mirrored field. ADR-063 §결정 2 atomic invariant — marketplace sync PR 선행 merge → plugin PR merge.

### Related

- [CFP-449](https://github.com/mclayer/plugin-codeforge/issues/449) — 본 carrier Story (Phase 2 PR)
- [CFP-445](https://github.com/mclayer/plugin-codeforge/issues/445) — ADR-064 declaration carrier (Phase 1 prerequisite)
- [CFP-388](https://github.com/mclayer/plugin-codeforge/issues/388) — evidence-enforceable framework Epic
- [ADR-064](docs/adr/ADR-064-decision-principle-mandate.md) §결정 2 — forbid-list dictionary SSOT
- [ADR-060](docs/adr/ADR-060-evidence-enforceable-promotion-framework.md) §결정 5 — warning mode
- [ADR-024](docs/adr/ADR-024-story-scoped-branch-policy.md) Amendment 3 — `hotfix-bypass:*` per-entry namespace
- [ADR-061](docs/adr/ADR-061-python-script-writing-convention.md) §결정 1 — Python heredoc convention
- [ADR-063](docs/adr/ADR-063-marketplace-atomic-invariant.md) §결정 2 — marketplace sync ordering

## [5.20.0] - 2026-05-12

### Added (CFP-445 — 결정 원칙 mandate carrier)

사용자 directive 4 회 누적 (2026-05-11 ~ 2026-05-12, KST) 의 normative SSOT 승격. memory ephemeral 영역의 cross-session enforcement 부재 해소.

- `docs/adr/ADR-064-decision-principle-mandate.md` (NEW) — 8 결정 본문
  1. 4 어휘 운영적 정의 (Trace 1) — best-effort / broad coverage / full-scope / active amendment
  2. forbid-list 8 어휘 dictionary — CFP-449 mechanical lint SSOT (warning tier)
  3. 결정 제시 5 룰 (Trace 2) — derived default / 옵션 dump 금지 / 식별자 사전 요약 / 질문 brevity / AskUserQuestion 범위
  4. multi-task spawn parallel default + sequential 강제 3 사유 dictionary (Trace 4)
  5. CFP scope unitary 룰
  6. 결정 제시 시점 (proposing-time) 영역 정의
  7. Self-application top-down ratchet
  8. Declaration only (CFP-446 / CFP-449 mechanical enforcement 별도 carrier)
- `CLAUDE.md` "결정 원칙" 신규 단락 ("오케스트레이션 규칙" 직전, append-only)
- `docs/orchestrator-playbook.md` §4.1.1 신규 — parallel default + sequential 강제 3 사유 운영 + 결정 제안 시점 self-check 5 항목 checklist
- `docs/domain-knowledge/domain/governance-principle/decision-style.md` (NEW) — 행동 패턴 + 적용 사례 SSOT (governance-principle 카테고리 신규 진입)
- `templates/github-issue-forms/story.yml` `decision_principle_compliance` advisory 체크박스 추가 (forcing function)
- `docs/adr/ADR-RESERVATION.md` — `| 64 | CFP-445 | active | 2026-05-12 |` row append

### Why

사용자 directive 4 회 누적 (2026-05-11 발화 1 회 + 2026-05-12 발화 2 회 + Codex pre-review iterative directive 1 회) 에도 normative SSOT 부재 = cross-session enforcement 결손. memory ephemeral 영역 한계가 결정 품질의 forbid-list 영역 침식 위험 + 옵션 dump UX + sequential bias 3 갈래 root cause. 본 carrier 가 그 SSOT 정립.

### Compatibility

- consumer overlay 영향 = 정책 축소 불허 (CLAUDE.md normative 단락 신설). `.claude/_overlay/project.yaml` extension 만 허용.
- mechanical lint (CFP-449) = warning tier 진입 (ADR-060 §결정 5), advisory only. blocking 승격은 evidence-enforceable framework gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 통과 후 별도 CFP carrier.
- iterative reformulation (CFP-446) = ADR-052 Amendment 2 별도 carrier (touchpoint #1 single-shot → max 3 rounds).
- 6 lane plugin 영향 = 0 (wrapper level normative SSOT, lane plugin self-write boundary 무변경).
- Marketplace sibling sync 의무 = `name` / `description` mirrored field 갱신 (description 변경 — `+ CFP-445 ...` append). 본 PR merge 직후 `mclayer/marketplace` sync PR 즉시 open · merge (ADR-016 + ADR-063 atomic invariant 정합).

### Related

- [CFP-445](https://github.com/mclayer/plugin-codeforge/issues/445) — 본 carrier Story
- [CFP-446](https://github.com/mclayer/plugin-codeforge/issues/446) — Codex pre-review iterative reformulation (ADR-052 Amendment 2 별도 carrier)
- [CFP-449](https://github.com/mclayer/plugin-codeforge/issues/449) — forbid-list mechanical lint (ADR-060 warning tier 신규 entry `decision-principle-vocab` — 기존 entry `adr-sunset-criteria` 와 병렬)
- [ADR-064](docs/adr/ADR-064-decision-principle-mandate.md) — normative 결정 SSOT
- [ADR-058](docs/adr/ADR-058-adr-sunset-criteria-mandate.md) — sunset criteria mandate (ratchet 차단 forcing function)
- [ADR-060](docs/adr/ADR-060-evidence-enforceable-promotion-framework.md) — evidence-enforceable framework
- [ADR-063](docs/adr/ADR-063-marketplace-atomic-invariant.md) — 3-file atomic invariant

## [5.19.0] - 2026-05-12

### Changed (CFP-455 — Evidence registry schema v1.0 → v1.1 (4-tier enforcement 정식 amendment))

CFP-391 (Issue #396, closed without delivery 2026-05-11) / CFP-412 (Issue #412, post-merge-followup workflow false-positive close 2026-05-11) 의 재재예약 carrier. ADR-060 Amendment 2 deliver — 4-tier enforcement 정식 분류 정식화.

- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — Amendment 2 append (frontmatter `amendment_log[]` row 2 + 본문 `## Amendment 2` § 신설 8 결정 — §결정 3 required 전환 / §결정 6 (c) `sibling_dependencies` append CFP-455 / §결정 14 메타 anomaly vs schema validation lint 분리 / §결정 15 exit-code 3-tier semantics / §결정 16 warning-tier bypass_label optional / §결정 17 retroactive reclassification immediate fail / §결정 18 marketplace sync 의무 명시 / Mermaid diagram 동기화)
- `docs/evidence-checks-registry.yaml` — header `schema_version: "1.0"` → `"1.1"` + `last_updated: 2026-05-12` + `entries[name=adr-sunset-criteria].promotion_criteria.sibling_dependencies` append `CFP-455`
- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — frontmatter `version: "1.0"` → `"1.1"` + §3 표 `current_tier` row required marker + §3 표 `bypass_label` row tier 별 의무 분리 + §4 본문 4-tier enum 강조 + §7 v1.1 row 완료된 변경 historical 분리
- `docs/inter-plugin-contracts/MANIFEST.yaml` — `registries.evidence_check_registry.files[0].version: "1.0"` → `"1.1"`
- `CLAUDE.md` — Inter-plugin Contract 단락 `evidence-check-registry-v1.md` v1.1 표기 + Amendment 2 narrative + ADR 단락 Amendment 2 narrative append

### Why

ADR-060 §결정 12 후속 carrier 의무가 2 carrier (CFP-391 / CFP-412) 모두 closed without delivery 로 2차 orphan. 4-tier enforcement 정식 분류 deliver = framework SSOT 의 mechanical enforcement 첫 단계 확정. schema v1.1 MINOR bump 가 `current_tier` 필드 mechanical 강제 (Phase 2 PR scope 의 메타 lint).

### Compatibility

- backward compatible — 기존 22 entry 모두 현행 `current_tier` 보유 verified (CodebaseMapper deputy 정밀 verify, 2026-05-12), mechanical regression 0건
- schema MINOR bump = ADR-008 §kind:registry 정합 (field required 전환 = MINOR)
- `is_transitional: false` (permanent — ADR-060 §결정 11 framework SSOT self-defeat 회피 정합)

### Phase 2 (별도 PR 권고)

본 5.19.0 = Phase 1 (docs/* SSOT 만) — Phase 2 PR scope = `scripts/check-evidence-registry.sh` 신설 + `templates/github-workflows/evidence-registry-check.yml` 신설 + 메타 lint self-application registry entry (`evidence-registry-schema`). Phase 2 시점 ADR-037 적용 — plugin.json 5.19.0 → 5.20.0 MINOR bump 권고 (별도 carrier 판단).

### Marketplace sync (의무, ADR-063 §결정 2 — 별도 PR)

본 PR merge 직후 즉시 marketplace sync PR open·merge (codeforge plugin family 의 wrapper plugin version mirrored field — `mclayer/marketplace` `marketplace.json` `plugins[name=codeforge]` version `5.18.0` → `5.19.0`).

## [5.18.0] - 2026-05-12

### Added (CFP-500 — SessionStart prereq-check hook tier 격상)

ADR-038 Amendment 1 §결정 8 (CFP-375) + CFP-385 의 (c) runtime advisory tier 가 매 세션 무시 → 본 Story 가 (b) startup hook tier 로 enforcement 격상. consumer `.claude/settings.json` `hooks.SessionStart[]` 에 `SessionStart-codeforge-prereq-check.json.sample` 등록 시 harness 가 세션 부팅 시점에 Orchestrator 에게 prompt-injection 으로 `ToolSearch("select:TodoWrite")` 호출 지시.

- `templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample` (NEW) — 3번째 SessionStart hook sample (drift / worktree-gc 패턴 정합, 7 top-level field schema)
- `scripts/check-codeforge-prereq.sh` (NEW) — bash helper, single-quoted heredoc static stdout (set -euo pipefail + filesystem touch 0 + network call 0 + AC-11 정적 검증 cover)
- `tests/scripts/test_check_codeforge_prereq.sh` (NEW) — bash smoke test, 16 assertion (정적 10 + runtime 5 + exit code 1 bonus)
- `docs/domain-knowledge/domain/runtime/deferred-tool-and-session-start-hook.md` (NEW, ADR-056 §결정 1 `domain/<area>/<topic>.md` 정합)
- `docs/orchestrator-playbook.md` §1.1 0i 항목 supersede + hook tier 위임 + §결정 7·8 retain 폴백
- `CLAUDE.md` "세션 개시 의무" 단락 supersede
- `.claude-plugin/plugin.json` description 끝 CFP-500 entry append + version 5.17.0 → 5.18.0
- `.claude/settings.json` wrapper dogfooding (`hooks.SessionStart[]` 에 prereq-check 추가)
- `docs/consumer-guide.md` §2h.1 SessionStart prereq-check hook subsection 신설

### Why

`선언적 규칙 = 신뢰 불가` 가 CFP-375 + CFP-385 두 차례 검증됨. 본 Story = (c) → (b) tier escalation (3rd attempt). ADR-038 Amendment 2 §결정 9 신설 — `prereq_tools[]` + `prereq_checks[]` declarative array schema 로 extensibility 보존 (초기 preload = TodoWrite 단독, 보수적). ADR-058 §결정 5 정합 — amendment_log `sunset_justification` 3-tuple (metric `TodoWrite InputValidationError <5/100세션` / who PMOAgent / how manual sampling + CFP-389 / ADR-060 automation candidate).

### Compatibility

Non-breaking. Hook 등록은 consumer opt-in (CONDITIONAL). 기존 ADR-038 §결정 7 (실패 non-blocking) + §결정 8 (호출 시도 non-skippable) retain — layered defense.

## [5.17.0] - 2026-05-12

### Added (CFP-436 — Marketplace ↔ plugin.json atomic invariant)

CFP-387 / CFP-393 / CFP-423 retro 의 3-Wave marketplace drift 누적 → ADR carrier 격상 timing 도달. mirrored field bump 시 3 file atomic coordination 의무 명시화.

- `docs/adr/ADR-063-marketplace-atomic-invariant.md` (NEW, 200L) — 8 결정 정책 본문
  1. 3-file atomic invariant 명시 (plugin.json + CHANGELOG.md + marketplace.json 동시 처리)
  2. PR ordering — marketplace sync PR 선행 merge 권장 (chicken-and-egg 회피)
  3. 작성 단계 sanity check — pre-commit 권장
  4. bypass channel — `hotfix-bypass:marketplace-atomic` label (ADR-024 Amendment 3 정합)
  5. 기존 CI lint 보존 + 신규 lint follow-up (별도 CFP carrier)
  6. ADR-016 vs ADR-063 분리 — sync 무엇 vs sync 어떻게
  7. ADR-061 §결정 5 정합 — sanity check 3종 적용
  8. Self-application — `is_transitional: false` (permanent)
- `CLAUDE.md` "ADR" 섹션 — ADR-063 cross-ref 1 단락 (ADR-061 직후)
- `docs/adr/ADR-RESERVATION.md` — `| 63 | CFP-436 | active | 2026-05-12 |` row append

### Why

3-Wave drift evidence (CFP-387 chicken-and-egg + CFP-393 catch-up + CFP-423 합쳐 처리) — mirrored field bump 시 atomic coordination invariant 부재. 기존 `check-marketplace-parity.sh` / `check-marketplace-sync.sh` 는 사후 감지만 가능, 작성 시점 강제 mechanism 없음.

### Compatibility

- `is_transitional: false` (permanent policy carrier — ADR-058 self-application 정합)
- ADR-016 sibling sync 와 별도 정책 (amendment 아님)
- ADR-037 version bump rule 정합
- backward compatible — 기존 PR 영향 없음

### Self-application

본 PR 자체가 ADR-063 §결정 1 self-application 첫 사례 — plugin.json 5.16.0 → 5.17.0 + CHANGELOG 5.17.0 entry + marketplace.json sync PR 병행 open (선행 merge).

## [5.16.0] - 2026-05-12

### Added (CFP-423 — Python script-writing convention)

bash heredoc 안 Python script 작성의 escape trap 차단. CFP-418 FIX iter 1 root cause (43 file regression) carrier.

- `docs/adr/ADR-061-python-script-writing-convention.md` (NEW, 260L) — 8 결정 정책 본문
  1. 외부 `.py` 파일 의무 (`Write` tool → `python file.py`, > 5줄 또는 backslash escape 포함 시)
  2. 짧은 `python -c` 허용 범위 (5줄 이내 + backslash 무관)
  3. heredoc 금지 영역 (regex backref / byte escape / multiline string with backslash)
  4. `<<'EOF'` single-quoted 한계 명시 (Windows Git Bash / MSYS2 / WSL 환경 backslash escape inconsistency)
  5. Sanity check 3종 의무 (diff inspection / lint re-run / sample file Read)
  6. Reusable backfill helper 권장 (장기 follow-up, `scripts/lib/`)
  7. ADR-039 정합 — script work 도 subagent default
  8. Self-application — `is_transitional: false` (permanent policy)
- `CLAUDE.md` "ADR" 섹션 — ADR-061 cross-ref 1 단락 추가 (ADR-058 sunset criteria 직후, ADR-060 evidence-enforceable framework 직전)
- `docs/adr/ADR-RESERVATION.md` — `| 61 | CFP-423 | active | 2026-05-12 |` row append

### Why

CFP-418 Phase 2 FIX iter 1: bash heredoc `<<'PYEOF'` (single-quoted) 가 Python `\\1\\2` 를 `\1\2` (octal escape, SOH+STX 제어문자) 로 변환하여 43 ADR file 의 `## 관련 파일` heading 손실. 동일 trap이 향후 backfill/migration script에서 재발화 위험. evidence-enforceable framework (ADR-060) 의 doc section schema lint 가 trap 감지 — CFP-389 framework 효과 confirmed.

### Compatibility

- `is_transitional: false` (permanent policy carrier — ADR-058 self-application 정합)
- ADR-039 정합 — script work도 subagent default
- ADR-054 §결정 4 (신규 ADR 도입 = full-lane) 정합
- backward compatible — 기존 script 영향 없음 (신규 작성 가이드 only)

## [5.15.0] - 2026-05-11

### Added (CFP-393 — Story 1 of CFP-388 Epic, retroactive catch-up)

evidence-enforceable framework 첫 non-sunset application — ADR-057 (Orchestrator Opus mandate + Sonnet→Opus fallback) Amendment 2 + fallback rate KPI dashboard registry entry.

- `docs/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md` — Amendment 2: sunset criteria 본문 강화 (CFP-388 framework 첫 적용 사례)
- `docs/evidence-checks-registry.yaml` — 두 번째 entry (fallback rate KPI, ADR-057 sunset criteria measurement)
- marketplace.json 5.15.0 sync 완료 (이전 PR에서)

### Why

ADR-058 (CFP-387) sunset criteria 정책의 첫 non-sunset framework application. ADR-057 Sonnet→Opus fallback rate 의 정량 측정 infra 도입 — `[rate-limit-fallback:sonnet→opus]` 태그 grep + 월간 집계.

### Compatibility

본 entry 는 plugin.json 5.15.0 catch-up — 본 PR 이전에 marketplace 가 5.15.0 으로 sync 되었으나 plugin.json + CHANGELOG.md 가 미반영되었던 drift 정정.

## [5.14.0] - 2026-05-11

### Added (CFP-411 — Story 2 of Epic CFP-390)

Multi-round Adversarial Debate Protocol 의 Requirements lane 확장. Story 1 (CFP-391) 에서 도입한 `debate-protocol-v1` registry + ADR-059 + ADR-044 Amendment 1 `auto_on_divergence` 를 Requirements lane 에 적용. doc-only fast-path applied (ADR-054) — Phase 1+2 단일 PR.

- `docs/adr/ADR-052-codex-proactive-check-touchpoints.md` — Amendment 1: touchpoint #4 (RequirementsPLAgent §1~§6 완료 직후 Codex proactive check) single-shot 검토 → multi-round adversarial debate 격상
- `docs/inter-plugin-contracts/debate-protocol-v1.md` (Story 1 산출) — `trigger.lane: requirements` + `divergence_type: semantic` enum 재사용
- `docs/orchestrator-playbook.md` §3.10 — touchpoint #4 divergence detection + debate dispatch 흐름 추가
- codeforge-requirements 0.5.0 sibling sync (mclayer/plugin-codeforge-requirements#19):
  - `agents/RequirementsPLAgent.md` — semantic divergence detection 3 criteria (AC 의미 차이 / Edge Case 누락 / Why 해석 mismatch)
  - `agents/codex-proactive-check.md` (NEW) — Codex worker entry, `dispatch_mode: auto_on_divergence`

### Why

- ADR-052 touchpoint #4 의 single-shot 검토가 AC 의미 차이·Edge Case 누락·Why 해석 mismatch 같은 의미적 divergence 를 해소하지 못함 → multi-round debate 로 격상
- ADR-059 lane-agnostic 설계 활용 → 신규 contract 신설 없이 trigger 조건만 추가
- Requirements lane 은 review-verdict-v4 미적용 (verdict packet producer 아님) → divergence 판정자 = RequirementsPL LLM (semantic only, structured surface 없음)

### Compatibility

- **Wire**: codeforge-requirements >= 0.5.0 의무 — version drift check `bash scripts/check-codeforge-version-drift.sh` 가 강제
- **Backward compat**: divergence 미검출 시 기존 ADR-052 single-shot 흐름 유지 — 새 동작은 superset
- **Sibling**: marketplace.json `plugins[name=codeforge]` version 5.13.0 → 5.14.0 sync 의무 (ADR-016)

### Related

- Story: [CFP-411](https://github.com/mclayer/plugin-codeforge/issues/392) — doc-only fast-path
- Wrapper PR: [#411](https://github.com/mclayer/plugin-codeforge/pull/411) merged 2026-05-11
- Sibling: [codeforge-requirements#19](https://github.com/mclayer/plugin-codeforge-requirements/pull/19) merged 2026-05-11
- Story 1: CFP-391 (Protocol + DesignReview lane) — full-lane

## [5.13.0] - 2026-05-11

### Added
- CFP-389 — Evidence-enforceable promotion framework SSOT (ADR-060 신규)
  - `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — framework SSOT (12 §결정, is_transitional=false, ## 해소 기준 N/A — permanent policy)
  - `docs/adr/ADR-024-story-scoped-branch-policy.md` — Amendment 3: `hotfix-bypass:*` label family = audit-trailed exception channel (사용자 ESCALATE Option A)
  - `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — kind:registry schema doc (4th wrapper-owned registry)
  - `docs/inter-plugin-contracts/MANIFEST.yaml` — `registries:` entry (`evidence_check_registry`)
  - `docs/evidence-checks-registry.yaml` — data SSOT 첫 entry (`adr-sunset-criteria`, tier=warning, bypass=hotfix-bypass:adr-sunset, pr_cumulative_min=20)
  - `scripts/check-adr-sunset-criteria.sh` + `scripts/check-bypass-audit-comment.sh` — Python lint
  - `templates/github-workflows/adr-sunset-criteria.yml` + `.github/workflows/` self-app copy (warning mode, `continue-on-error: true`)
  - `docs/doc-locations.yaml` + `docs/parallel-work/section-ownership.yaml` row 추가
  - `CLAUDE.md` 3 섹션 갱신 (ADR / GitHub Workflow 14종 / Inter-plugin Contract kind:registry 5 file)

### Changed
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — lint regex 정합 ("N/A — permanent policy" 문구)
- `docs/adr/ADR-RESERVATION.md` — row 60 추가 (CFP-389)
- `docs/doc-location-registry.md` — regen

### Why
- CFP-388 Epic의 첫 vertical slice (Phase 1+2 단일 PR — ADR-060 §결정 12 declaration + first check 일체화)
- ADR-058 declaration only → mechanical enforcement 점진 적용 framework SSOT 도입
- 사용자 ESCALATE Option A: `hotfix-bypass:adr-sunset` label로 ADR-024 `enforce_admins: true` 호환

## [5.12.1] - 2026-05-11

### Added
- CFP-391 Phase 2 — debate-protocol-v1 검증 인프라
  - `templates/team-spec-design-review.yaml` Codex worker `dispatch_mode: [user_request_only, auto_on_divergence]` 배열 + `divergence_detection` block (surface/criteria/anchor_field) + `dispatch_pattern` `adversarial-debate` entry (rounds min 3 max 5 soft 4 + protocol debate-protocol-v1 + transcript Story §9 영속화) — ADR-044 Amendment 1 정합
  - `scripts/check-doc-frontmatter.sh` — registry kind 필수 필드 보강 (`canonical_repo` + `canonical_path` + `date`); 기존 8 registry frontmatter backfill 동행
  - `scripts/check-doc-section-schema.sh` — Story §9 `### Debate transcript: <anchor_id>` sub-section schema 검증 (anchor_id non-empty + `#### trigger` / `#### rounds` (최소 1 `- index: N` entry) / `#### termination` block 의무)
  - `tests/debate-protocol/test_divergence_detection.sh` + `test_anchor_recurrence.sh` — bash + jq 시뮬레이션 (divergence union/severity/recommendation 분류 + recurrence count >= 2 escalation) + fixtures 4종
  - `tests/fixtures/debate-protocol/{invalid,valid}-frontmatter.md` + `tests/fixtures/debate-transcript/{invalid-missing-anchor,invalid-empty-rounds,valid-minimal}.md` — schema lint negative/positive case

### Changed
- 8 registry frontmatter backfill — `canonical_repo` / `canonical_path` / `date` 필드 추가 (comment-prefix / debut-audit-triage / decision-packet v1/v2 / fix-event / label-registry v1/v2 / stop-event)

### Why
- Phase 2 PR scope — Phase 1 PR (ADR-059 + protocol 정의) merge 후 implementation: lint enforcement + team-spec yaml dispatch_mode array + simulation test

## [5.12.0] - 2026-05-11

### Added
- CFP-391 / ADR-059: debate-protocol-v1 registry + DesignReview lane 적용 (Phase 1)
  - `docs/inter-plugin-contracts/debate-protocol-v1.md` (NEW, `kind: registry`) — lane-agnostic adversarial debate protocol SSOT
    - Trigger / Round / Termination 3-block schema + Round 0~N 입력 형식
    - Anti-sycophancy 메커니즘 (role_lock / position_change / remaining_disagreements / force_continue)
    - Anchor recurrence escalation (>= 2 시 즉시 사용자 escalation)
    - FIX 통합 (reasoning carryover, ArchitectAgent re-run prompt 에 transcript 명시 주입)
  - `docs/adr/ADR-059-debate-protocol-v1.md` (NEW, Accepted) — 5 결정 carrier
  - `docs/adr/ADR-044-phase-scoped-sequential-team.md` Amendment 1 — `dispatch_mode` enum 에 `auto_on_divergence` 추가 + 우선순위 룰 (`default > auto_on_divergence > user_request_only`)
  - `docs/inter-plugin-contracts/fix-event-v1.md` 1.0 → 1.1 MINOR bump — `debate_artifact_ref` optional 필드
  - `docs/inter-plugin-contracts/review-verdict-v4.md` — `findings[].anchor_id` optional 필드 추가 (debate-protocol-v1 stable identifier 의존, FIX-1)
  - `docs/inter-plugin-contracts/MANIFEST.yaml` debate_protocol entry 추가

### Changed
- `CLAUDE.md` 4 섹션 추가 — kind:registry 3→4 / Adversarial Debate sub-section / FIX 루프 debate_artifact_ref / 레인 진입 트리거 주석
- `docs/orchestrator-playbook.md` §3.13 신설 — Multi-round Adversarial Debate dispatch 흐름
- `docs/consumer-guide.md` §1f 확장 — auto_on_divergence + Token 비용 의식 + anchor 재발 escalation
- `docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md` Adversarial 패턴 확장
- `templates/team-spec-design-review.yaml` Codex worker `dispatch_mode: [user_request_only, auto_on_divergence]` (Phase 2 PR scope)

### Why

5 권장 패턴 중 Adversarial debate 영역 measurable verification 부족 — `worker_dialog_rounds >= 2` 시 review-verdict packet 의 finding evidence 에 round-by-round narrative 포함 강제 필요. PL LLM judgment 단독 (외부 algorithm 없음) + anti-sycophancy 메커니즘 (role_lock / remaining_disagreements) + anchor 재발 escalation 으로 AI 합의 불가능 신호 명시화.

### Compatibility

- ADR-037 §3.1 (h) 신규 ADR (ADR-059) + (g) additive CLAUDE.md guidance + (f) inter-plugin contract MINOR (fix-event-v1) + (h) Amendment (ADR-044) → MINOR. 5.11.0 → 5.12.0.
- Story 2 (Requirements lane 확장) deferred → CFP-392 stub.

## [5.11.0] - 2026-05-11

### Added
- CFP-387 / ADR-058: ADR template 해소 기준 섹션 의무화 + `is_transitional` 분류 frontmatter
  - `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` (NEW, Accepted) — declaration only policy carrier
    - §결정 1: frontmatter `is_transitional: true | false` 의무화 (boolean only)
    - §결정 2: `## 해소 기준` 섹션 의무 (`is_transitional: true` 시) — `## 결과` 직후 / "다이어그램 (선택)" 직전 / false 시 "N/A — permanent policy" 1줄
    - §결정 3: 측정성 3-tuple (metric / who / how) 정량 명시 의무 — 모달 어휘 ("충분히 안정화되면", "임시로", "한시적", "until further notice") 금지
    - §결정 4: 미선언 default = `is_transitional: true` (안전망 추정, safe direction, CL-1 옵션 A 채택)
    - §결정 5: Amendment 시 `sunset_justification` 의무 (ratchet 차단, CL-2 옵션 B 채택, count cap 거부)
    - §결정 6: 본 ADR 자기 분류 = `is_transitional: false` (self-defeat 회피 — permanent policy carrier)
    - §결정 7: 보안 ADR default classification presumption = `is_transitional: false` (Codex proactive check #1 권고 반영)
    - §결정 8: Declaration only — CFP-B (CI lint) / CFP-C (ADR-057 amendment + KPI) / CFP-D (retroactive backfill) 별도 carrier 분리

### Changed
- `CLAUDE.md` "ADR (`docs/adr/` SSOT)" 섹션 — ADR-058 안전망 분류 + 해소 기준 의무 cross-ref 추가 (1 단락)
  - frontmatter `is_transitional` 분류 정책 명시
  - `## 해소 기준` 섹션 의무 + 측정성 3-tuple 정량 요구 명시
  - 보안 ADR default presumption 명시
  - DesignReview lane manual gate (CFP-B merge 까지 임시 운영 문구)

### Phase 2 (plugin-codeforge-design v0.7.0)
- `templates/adr.md` frontmatter `is_transitional` 필드 + `amendments[].sunset_justification` schema 추가
- `templates/adr.md` body `## 해소 기준` 섹션 신설 + 예시 3종 inline (rate-limit / platform SLA / full-rollout)
- 모달 어휘 금지 명시 + 보안 ADR default presumption 명시

### Why

ADR-057 (Orchestrator Opus 필수화 + Sonnet→Opus fallback) 가 측정 기준 없는 영구 안전망으로 굳어지는 위험이 brainstorming (Opus×Codex 3라운드, 2026-05-11) 에서 식별 → 합의 원칙 5 "안전망 측정가능 종료" forcing function. technical debt ratchet effect (Cunningham 1992 / Fowler 2003) + 입법 sunset clause 패턴 + feature flag sunset 운영 가이드 선행 연구 기반.

### Compatibility

- ADR-037 §3.1 (h) 신규 ADR + (g) additive CLAUDE.md guidance → MINOR. 5.10.0 → 5.11.0.
- backward compatible — 기존 ADR 39종 frontmatter 미선언 = default `is_transitional: true` 안전망 추정 (declaration only, mechanical enforcement = CFP-B 잠정 carrier)
- **Sibling sync**: codeforge-design 0.6.0 → 0.7.0 (`templates/adr.md` canonical SSOT 갱신) — Phase 2 PR pair 동시 merge 의무
- **Marketplace sync**: wrapper + codeforge-design 양쪽 mirrored field 변경 (`version` + `description`) → marketplace sync PR 의무 (Phase 2 PR merge 직후, ADR-016)
- Mode B hub-centralized (ADR-020 Amendment 1) — wrapper hub, codeforge-design worker plugin

## [5.10.0] - 2026-05-11

### Changed
- CFP-378 / ADR-014 Amendment 2: `skills/deputy-mandate/SKILL.md` §7.4/§7.5/§11 소유권 annotation 갱신
  - SecurityArch: credential threat owner (§7.5) 명시
  - OpRiskArch: environment containment owner (§7.4.5) 명시
  - DataMigrationArch: §11.6 idempotency cell primary author 명시
- `docs/adr/ADR-014-operational-risk-ssot-distribution.md` Amendment 2 추가
  - LiveOps = external venue source-of-truth owner / LiveOrdering = internal state machine convergence owner (reconciliation 영역)
  - DataMigrationArch §11.6 primary author / OpRiskArch memo input 분리
  - SecurityArch credential threat owner / OpRiskArch environment containment 경계 확정

### Phase 2 (plugin-codeforge-design v0.6.0)
- ArchitectAgent: Phase 3.5 self-lint 단계 추가 (mechanical pre-check, author≠judge 원칙 보존)
- ArchitectPLAgent: Phase 1.0 §8.5 조건 평가 신설 + `§8.5_active` spawn parameter 하위 전달
- TestContractArchitectAgent: `§8.5_active` spawn parameter 수신 + dissent format 표준화
- LiveOpsDeputyAgent: reconciliation 소유 경계 (외부 venue 진실 owner) 명시
- LiveOrderingDeputyAgent: reconciliation 소유 경계 (내부 상태머신 수렴 owner) 명시
- `.github/workflows/phase-gate-mergeable.yml`: CFP-342/317/123/133 갱신 동기화

## [5.9.0] - 2026-05-10

### Changed
- ADR-042 Amendment 2: Haiku 3번째 카테고리(mechanical pattern execution) 추가
- InfraEngineerAgent·QADeveloperAgent·DataEngineerAgent Haiku 4.5 pilot 전환 결정
- rollback 트리거 기준 및 governance 재-audit 트리거 규정 (ADR-042 결정 5·6)

### Phase 2 (plugin-codeforge-develop v0.3.0)
- InfraEngineerAgent·QADeveloperAgent·DataEngineerAgent `model:` 필드 `claude-sonnet-4-6` → `claude-haiku-4-5` 실제 전환 완료 (`plugin-codeforge-develop` PR #14)

## [5.8.0] - 2026-05-10

### Added
- CFP-343 / ADR-051: 4개 SSOT 예외 테이블 → plugin skill 분리 (`codeforge:review-responsibility`, `codeforge:root-cause-decision`, `codeforge:fix-ledger-schema`, `codeforge:deputy-mandate`)
- CLAUDE.md 오케스트레이션 규칙: Lane 진입 시 skill 호출 의무 trigger 테이블 신설

### Changed
- CLAUDE.md: 454줄 → 320줄 (ADR-012 ≤380줄 cap 재충족, -29.5%)
- `skills/codeforge-brainstorm.md` flat 파일 → `skills/codeforge-brainstorm/SKILL.md` subdirectory 형식 정정 (system-reminder 노출 버그 해소)

## [5.7.0] - 2026-05-09

### Added
- ADR-046: ResearcherAgent 역할 재정립 — Concept Formulation + Deep Exploration + Requirement Reshape mandate (3 mandate boundary, Light structured 6-section output schema, mode policy, Opus tier rationale)

### Changed
- ADR-042 amendment_log[1]: ResearcherAgent deferred fence resolved — §결정 2 RESOLVED annotation + §결정 1 (g) cleanup (Risk R3 mitigation, ref ADR-046)
- CLAUDE.md: Agent model tier 정책 단락에 ADR-046 cross-ref 추가
## [5.6.0] - 2026-05-09

### Agent model selection policy — ADR-042 (ADR-013 dogfood-out waiver)

- `docs/adr/ADR-042-agent-model-selection-policy.md` (NEW, Accepted) — codeforge agent `model:` field 의 Opus / Sonnet / Haiku tier 선정 SSOT. 4 결정: 3-tier role-pattern 매트릭스 / sibling PR scope (CodebaseMapper + Refactor → Sonnet, ResearcherAgent 재정의 deferred) / 신규 agent 도입 ADR-amendment 의무 / `model:` 필드 부재 = 명시적 Opus 결정. Core principle: "Sonnet 으로 fully cover 가능 = role 재정의 시그널".
- `CLAUDE.md` (Modify) — Development Agent Team 섹션 직후 ADR-042 1줄 cross-ref.

ADR-037 §3.1 (h) 새 ADR + (g) additive CLAUDE.md guidance → MINOR. 5.5.0 → 5.6.0.

ADR-013 dogfood-out explicit waiver: full Story flow 우회 (3 사유 — KEY collision codeforge-internal-docs#99 / Action permission codeforge-internal-docs#98 / cost asymmetry).

Sibling: [mclayer/plugin-codeforge-design#24](https://github.com/mclayer/plugin-codeforge-design/pull/24) (Mapper + Refactor model field edit + 0.4.0 → 0.4.1 PATCH).

Marketplace mirror sync: 후속 sibling PR (codeforge 5.6.0 + codeforge-design 0.4.1).

## [5.5.0] - 2026-05-08

### CFP-273 — SessionStart-codeforge-drift.json.sample consumer overlay (CFP-262 spillover)

- `templates/.claude/hooks/SessionStart-codeforge-drift.json.sample` (NEW) — drift check hook 의 ready-to-cp sample. consumer 가 `.claude/_overlay/.claude/hooks/SessionStart-codeforge-drift.json` 으로 복사하면 overlay/hooks/merge.py 가 `.claude/settings.json.hooks.SessionStart[]` 에 자동 merge.
- `docs/consumer-guide.md` (Modify) — Version drift 검사 섹션 갱신: "Activate (cp 방식)" 단계 추가, severity → action mapping 명시, manual 실행 + bypass env 안내.

ADR-037 §3.1 (c) 선택 hook 추가 + (d) 선택 template 추가 → MINOR. 5.4.0 → 5.5.0.

Marketplace mirror sync: mclayer/marketplace#21 (선행 merge for drift CI pass).

## [5.4.0] - 2026-05-08

### CFP-259 Epic — Plugin version governance + project key atomic reservation (3 child Stories)

#### CFP-260 (PR #266 + PR #269) — Project key atomic reservation (Option B)

- `docs/adr/ADR-036-project-key-atomic-reservation.md` (NEW, Accepted) — KEY = `<PREFIX>-<Issue#>` (GitHub atomic Issue numbering 위임). 6 결정: KEY 형식 / cfp-reserve.yml Form / phase:reservation label / reservation-cleanup.yml workflow / story-init.yml concurrency 안전망 / Migration (기존 KEY rename 금지).
- `templates/github-issue-forms/cfp-reserve.yml` (NEW) — 1-line title reservation Form, brainstorming 시점 KEY 사전 확보.
- `templates/github-workflows/story-init.yml` (Modify) — KEY 계산 line 70-81 단순화 (find/sort/max+1 4 lines 제거 → `${PREFIX}-${ISSUE_NUMBER}` 1 line) + per-Issue concurrency group.
- `templates/github-workflows/reservation-cleanup.yml` (NEW) — daily cron, 30-day TTL stale reservation auto-close.
- `docs/inter-plugin-contracts/label-registry-v1.md` (v1.3 → v1.4) — `phase:reservation` 신설.
- `scripts/bootstrap-labels.sh` (28 → 29 labels).
- `docs/orchestrator-playbook.md` §1.2.0 + `docs/consumer-guide.md` 갱신.

#### CFP-261 (PR #267 + PR #270) — Plugin version bump rule SSOT (Option β + α)

- `docs/adr/ADR-037-plugin-version-bump-rule.md` (NEW, Accepted) — Option β core (12 surface category) + Wrapper-coupling trigger 3종 (T1 contract MAJOR / T2 agent topology / T3 family invariant ADR supersede) + Option α (Conventional Commits CI enforcement).
- `templates/github-workflows/check-plugin-version-bump.yml` (NEW) — Phase 2 v1: Conventional Commits + plugin.json version bump consistency 검사. β surface table + T1/T2/T3 mapping = follow-up CFP.
- `CONTRIBUTING.md` (NEW) — 7 plugin family overview + Branch policy + Conventional Commits + bump rule β + Wrapper-coupling triggers + Marketplace mirror + CI required checks + Story discipline + Internal-docs.

#### CFP-262 (PR #271) — Session-start codeforge plugin version drift check (Wave 2)

- `scripts/check-codeforge-version-drift.sh` (NEW, executable) — 9 plugin (codeforge family 7 + codex + superpowers) installed vs marketplace 비교, semver compare, severity 분류 (MAJOR=hard-stop / MINOR=warn / PATCH=info), bypass env (`BYPASS_VERSION_DRIFT`).
- `docs/orchestrator-playbook.md` §1.1 sub-step 0f 추가 (drift 검사 의무).
- `docs/consumer-guide.md` (drift 검사 안내 + SessionStart hook JSON 예시).
- `CLAUDE.md` "세션 개시 의무" 갱신 (link + bash 명령 inline).

#### Epic close (PR #272 — 본 PR)

- ADR-036 status: Proposed → Accepted
- ADR-037 status: Proposed → Accepted (self-application 첫 사례 = wrapper plugin 5.3.0 → 5.4.0 MINOR bump)
- `.claude-plugin/plugin.json` version + description 갱신
- Marketplace mirror sync = mclayer/marketplace#20 (먼저 merged, drift CI pass)

#### CI enhancement

- `.github/workflows/invariant-check.yml` — `reservation-cleanup.yml` + `check-plugin-version-bump.yml` 을 CONSUMER_ONLY_WORKFLOWS 에 추가
- `.github/workflows/phase-gate-mergeable.yml` + `templates/github-workflows/phase-gate-mergeable.yml` — 도c-only fast-pass 에 `scripts/` + `CONTRIBUTING.md` 추가

#### Internal-docs (mclayer/codeforge-internal-docs#74 merged)

- Stage 0 spec (CFP-259 Epic design)
- 3 Change Plans (CFP-260 / CFP-261 / CFP-262)
- 4 Story files (CFP-259 Epic + 3 children) in `wrapper/stories/`

### ADR-037 self-application (CFP-259 Epic 누적 변경 → 5.4.0 MINOR)

| Surface | 변경 | Bump |
|---|---|---|
| (h) ADR new | ADR-036 / ADR-037 신설 | MINOR |
| (d) Template workflow 추가 | cfp-reserve.yml / reservation-cleanup.yml / check-plugin-version-bump.yml | MINOR |
| (i) Bootstrap script | phase:reservation entry / check-codeforge-version-drift.sh | MINOR |
| (l) Marketplace mirrored field | description 갱신 | MINOR |

Wrapper-coupling trigger T1/T2/T3: 모두 미발동 (contract 변경 없음 / agent 0 invariant 유지 / ADR new 는 supersede 아님).

→ aggregate MINOR signal → 5.3.0 → 5.4.0 정합 ✅

## [5.3.0] - 2026-05-07

### CFP-128 — Docker-first Infra Engineering (Phase 1 + Phase 2)

#### Phase 1 (PR #240, merged 2026-05-07T04:56:20Z)

- `docs/adr/ADR-033-docker-first-infra-engineering.md` (NEW) — CFP-128 carrier. 7 결정: (1) InfraEngineerAgent default 출력 = Dockerfile + compose.yml + .dockerignore (1st-class). (2) K8s manifests = `presets/k8s/` (codeforge-develop) opt-in. (3) systemd / launchd / PaaS = legacy (consumer overlay opt-in only). (4) SecurityTest 1st-layer = trivy + hadolint 추가. (5) CONDITIONAL deputy 매트릭스 — Docker 관련 cell annotation update. (6) Migration = ADR Accepted 후 신규 Story 만 의무, 기존 in-flight grandfathered (ADR-031 §14 freeze pattern). (7) Consumer 측 follow-on Epic = mctrader 등 컨테이너화 코드 작업 별도 Epic 의무 (consumer 워크스페이스 수행).
- `docs/adr/ADR-014-operational-risk-ssot-distribution.md` (Modify) — frontmatter `amendments: [ADR-033]` + 본문 "Amended by" section (§7.4 OpRiskArch mandate 4 항목 확장 — container restart policy / volume DR / health check tuning / network mode boundary).
- 5 substantive decision (D1-D6, brainstorming 5 turn).
- Codex 7-area review CFP-128-001 verdict CONDITIONAL_PASS (P0:0, P1:3, all resolved).
- Spec / plan / Change Plan / Story §1-§7 / Codex review archive: codeforge-internal-docs `wrapper/{specs,plans,change-plans,stories,decisions}/CFP-128*` (PR #67 merged 2026-05-07T04:46:52Z).

#### Phase 2 (this PR)

- `docs/adr/ADR-033` (Modify) — Status `Proposed` → `Accepted`. effective date = Phase 2 PR merge timestamp.
- `CLAUDE.md` (Modify) — 4 SSOT 매트릭스 cell update:
  - 책임 매트릭스 +7 row (image base / Dockerfile lint / image CVE / compose definition / network mode / secret mount / restart policy)
  - 원인 판정 decision table +7 row (Dockerfile build FAIL / image CVE P0 / hadolint P1 / health check FAIL / secret 누설 / network 위반 / restart loop)
  - 6 deputy mandate 매트릭스 5 cell parenthetical annotation (§7.1 / §7.4 / §7.5 / §11 + §3 chief author footer note)
  - FIX Ledger §10 schema 무변화
- `templates/impl-manifest.md` (Modify) — 예시 row 교체 (`deploy/systemd/<service>.service` → `Dockerfile` + `compose.yml` + `.dockerignore`)
- `docs/project-config-schema.md` (Modify) — `infra_strategy` enum field (docker_first | legacy_systemd | none) + `infra_strategy_extras.k8s_preset_enabled` 추가
- `docs/consumer-guide.md` (Modify) — §3z "Docker-first 채택" subsection 신설 (4 sub: default contract / project.yaml override / K8s preset opt-in / container-image-scan workflow 호출 / 기존 consumer follow-on Epic 패턴). §4-§8 numbering 보존.
- `scripts/check-container-strategy.sh` (NEW) — `infra_strategy: docker_first` consumer 의 Dockerfile + compose.yml 존재 검증 lint.
- `scripts/test-check-container-strategy.sh` (NEW) — TDD wrapper 5 시나리오 PASS (docker_first / docker_first_old_compose_name (duality) / legacy_systemd / none / 2 negative — Codex P1-3 fix).
- `scripts/fixtures/check-container-strategy/{docker_first,docker_first_old_compose_name,legacy_systemd,none}/` (NEW) — TDD fixtures.
- `templates/github-workflows/container-image-scan.yml` (NEW) — reusable workflow (hadolint + trivy + SARIF upload, severity threshold CRITICAL,HIGH default + ignore-unfixed mitigation).
- `examples/webapp-minimal/Dockerfile` + `compose.yml` + `.dockerignore` (NEW) — multi-stage Node webapp + db + redis + healthcheck + restart policy 시범. project.yaml `infra_strategy: docker_first`.
- `examples/cli-tool-minimal/Dockerfile` + `.dockerignore` (NEW) — distroless single-stage Go binary 시범. project.yaml `infra_strategy: docker_first`.
- `examples/library-minimal/.claude/_overlay/project.yaml` (Modify) — `infra_strategy: none` 명시 (library Docker artifact 미적용).

#### Sibling sync (Phase 2 merge 후 — D step ★ Agent tool 3 parallel dispatch)

- mclayer/plugin-codeforge-develop: InfraEngineer mandate + presets/k8s/ + develop-output-v1
- mclayer/plugin-codeforge-design: OpRiskArch §7.4 Container considerations + design-output-v2
- mclayer/plugin-codeforge-review: SecurityTestPL trivy + hadolint 1st-layer + review-pl-base

#### Marketplace mirror (F step)

- mclayer/marketplace marketplace.json 4 plugin version bump (codeforge + 3 lane).

### CFP-126 — ADR-031 amend (Proposed → Accepted, §결정 1 (a) §14 freeze)

- `docs/adr/ADR-031-lane-spawn-evidence-trail.md` (Modify) — frontmatter `status: Proposed → Accepted`, `related_files` 갱신 (`phase-gate-mergeable.yml` → `lane-evidence-check.yml`). §상태 갱신 (CFP-126 Phase 1 PR #59 + Phase 2 PR #232 merged). §결정 1 storage location 4 candidate → (a) §14 freeze (12 field YAML schema explicit). 다른 3 candidate 명시적 superseded.
- Sonnet decider CFP-126-001 pick (high confidence) freeze. 본 amend = no-impl (도큐먼트 status 전환 + canonical schema reference).
- Parent Epic: CFP-124 (#230 + #57). carrier_story = CFP-126 (#59 + #232).

### CFP-127 — ADR-032 amend (Proposed → Accepted) + ADR-027 Amendment 1 in-doc

- `docs/adr/ADR-032-adr-027-amendment-1-hard-enforcement.md` (Modify) — frontmatter `status: Proposed → Accepted`. §상태 갱신 (CFP-127 Phase 1 PR #60 + Phase 2 PR #233 merged 명시).
- `docs/adr/ADR-027-consumer-adoption-protocol.md` (Modify) — frontmatter `amendments: [ADR-032]` field 추가, `related_stories[]` 에 CFP-127 추가. 본문 끝에 "Amendment 1 — Strict mode opt-in (ADR-032, CFP-127)" section 신설 (effective date / 활성 조건 3 mechanism / 4종 strict-eligible drift / Bypass priority HIGHEST / default 미변경 명시 + ADR-032 cross-ref).
- Sonnet decider CFP-127-001 (strict-eligible 4-type pick alpha high confidence) freeze. 본 amend = no-impl (도큐먼트 status 전환 + cross-reference).
- Parent Epic: CFP-124 (#230 + #57). carrier_story = CFP-127 (#60 + #233).

### CFP-124 — Consumer adoption hardening Phase 1 (Epic doc-only)

- `docs/adr/ADR-031-lane-spawn-evidence-trail.md` (NEW, status: Proposed) — CFP-126 carrier. 5 결정: Wrapper Orchestrator self-write committed lane evidence (storage location 4 candidate 중 CFP-126 Phase 1 Sonnet decider pick — Story 새 §section / §8.5 sub-block / frontmatter / PR description-only. 명시적 제외: `.claude-work/progress/` CFP-20 NG6 cache invariant) / Phase 2 PR description `## Lane evidence` 의무 블록 (regex 검증) / `phase-gate-mergeable.yml` evidence 부재 시 action_required block / `BYPASS_LANE_EVIDENCE` env (REASON 의무 동반) / effective date = ADR-031 Accepted PR merge 직후 Phase 2 PR (retroactive 안 함). 6 lane plugin 영향 매트릭스: 모두 변경 없음 (wrapper Orchestrator self-write 영역 한정).
- `docs/adr/ADR-032-adr-027-amendment-1-hard-enforcement.md` (NEW, status: Proposed) — CFP-127 carrier. ADR-027 **§결정 2 (3-trigger enforcement model) Tertiary trigger** amendment 1 (additive opt-in, supersede 아님). §결정 3 (Bypass) 와 별도 mechanism — 동시 작동. 5 결정: LLM-trust default 유지 / strict-eligible drift 4종 (project.yaml 부재 / plugin 미설치 / hook 미등록 / phase·gate label 부재) / opt-in 3 mechanism (`--strict` flag > env > yaml `bootstrap.strict_mode`) / strict exit 1 → Claude Code session 차단 안 함 (stderr + Orchestrator escalation) / 점진 도입 (mctrader 6-repo first opt-in) + revert procedure (CLI 미사용 / env unset / yaml false). Risk 5종 (false-positive / telemetry volume / schema drift / cold-start / in-flight 작업 차단) + mitigation 명시.
- Epic decomposition: 3 child Story (CFP-125 consumer-guide §2b sync + single-entry script / CFP-126 lane-spawn evidence trail / CFP-127 ADR-027 §결정 2 amendment 1).
- Phase 1 = doc-only Epic carrier PR. 각 child Story 가 독자 Phase 1+2 dogfood iteration.
- Spec / plan / Epic Story / 3 child Story stub: codeforge-internal-docs `wrapper/{specs,plans,stories}/CFP-124*` (ADR-013 dogfood-out).
- 사용자 directive (2026-05-06): "codeforge가 consumer에서 제대로 쓰이고 있지 않다 — 적극적으로 사용할 수 있도록 개정해야 한다" + Codex deep diagnosis 결과 + Claude verification + 사용자 explicit pick = option α.
- 진단 데이터 (verified): 28 `audit:from-mctrader-debut` 모두 closed / ADR-027 §결정 2 Tertiary trigger LLM-trust 의도된 design / `consumer-guide.md §2b` FLAT schema drift / `check_bootstrap.py:17` warning-only / mctrader 7 Epic 모두 main merge but 6 lane plugin 0개 spawn (manual workaround 회귀).
- Codex 7-area review (gpt-5.5 high, 본 Phase 1 spec/plan): P0=0 / P1=4 (lane evidence storage 충돌 → 4 candidate Sonnet pick / 6 lane plugin 영향 매트릭스 / ADR-027 §결정 ref 정정 / risk + revert procedure) / P2=2 (measurable acceptance / cross-plugin 제외 근거) — pre-merge 모두 fixed.
- Sonnet decider 본 옵션-formulation 미발화 (사용자 explicit pick). 각 child Story sub-decision 발화 가능 — 특히 CFP-126 Phase 1 PR 의 lane evidence storage 4 candidate (trigger a) 가 명시 의무.

### CFP-125 — Phase 2: consumer-guide §2 invert + bootstrap-consumer + check-debut-readiness

- `docs/consumer-guide.md` (Modify):
  - §2.0 신설 "5분 quickstart (RECOMMENDED — single-command setup)" — `bash scripts/bootstrap-consumer.sh` + `bash scripts/check-debut-readiness.sh` first-class. Windows variant 명시. Recovery (--resume default / --force / --reset) + plugin install reminder (platform-level).
  - §2a → §2.1 rename + framing "manual / advanced fallback (script 미작동 시)" + anchor 보존
  - §2b → §2.2 — FLAT schema → NESTED schema (`templates/settings.json.example` 정합) + 3 hook 등록 의무 (SessionStart × 2: regen-agents + check-bootstrap / UserPromptSubmit × 1: userprompt-reminder). Windows variant inline + hook 역할 enumerate.
- `scripts/bootstrap-consumer.sh` + `.ps1` (NEW) — 8 단계 idempotent setup (pre-check / plugin install reminder / overlay scaffold / settings.json bootstrap / GitHub workflows+forms+CODEOWNERS / labels delegate / consumer-scripts.manifest / summary). State marker `.claude/_overlay/.bootstrap-state.json` + `--dry-run` / `--force` / `--reset` / `--family-skip` / `--org` / `--repo` flag. Default `--resume` semantic. settings.json 자동 backup `.bak.<ts>` 보호.
- `scripts/check-debut-readiness.sh` + `.ps1` (NEW) — 4 verification (check_bootstrap.py 8 sub-check / plugin 11종 presence / project.yaml schema / settings.json 3 hook 정합). Default exit 0 advisory (ADR-027 §결정 2 LLM-trust 정합). `--strict` flag 인식 + 현 release 무 동작 (CFP-127 ADR-032 후 활성).
- `scripts/test-bootstrap-consumer.sh` (NEW) — 6 smoke test (--dry-run / --help / unknown arg / check-debut default / check-debut --strict pre-CFP-127 / PowerShell syntax). 향후 follow-up CFP 에서 3 fixture end-to-end TDD 확장.
- `templates/consumer-scripts.manifest` (Modify) — 2 신규 entry (`bootstrap-consumer.sh` + `check-debut-readiness.sh`, workflow dependency 없음).
- 3 substantive sub-decision Codex CONFIRM (CFP-125-001): bootstrap-consumer α (별도 신규 + reuse) / check-debut-readiness α (thin orchestrator) / consumer-guide §2b fix γ (invert priority).
- Codex 7-area review Phase 1 pre-merge: CONDITIONAL_PASS / P0=0 / P1=4 모두 fixed (plan/Change Plan/Story §3 작성 / exit code semantics 명확 표 / 6 lane plugin no-impact + mctrader 6-repo migration path 매트릭스 / partial-bootstrap failure recovery contract).
- Sonnet decider 발화 없음 (Phase 1 = 사용자 picked option / sub-decision Codex CONFIRM).
- Story SSOT: codeforge-internal-docs `wrapper/stories/CFP-125.md` (Phase 1 PR #58, Phase 2 sibling PR).
- Resolves CFP-124 Gap #2 (consumer-guide §2b FLAT schema drift) + Gap #3 (단일 진입점 부재).

### CFP-126 — Phase 2: Story §14 Lane Evidence schema + workflow + lint

- `templates/story-page-structure.md` (Modify) — §14 Lane Evidence section 신설 (additive, 기존 §1-§13 무영향). 12 field YAML schema (lane / iteration / agent / spawned_at / returned_at / output_status / outcome / pr_ref / decision_packet_ref / transcript / spawn_id / fix_iteration). Effective date = ADR-031 Accepted 후 신규 Phase 2 PR (retroactive 미처리). `.claude-work/progress/<KEY>.md` (CFP-20 NG6 cache) 와 분리 명시 — §14 SSOT priority.
- `templates/github-workflows/lane-evidence-check.yml` (NEW) + `.github/workflows/` self-apply — Phase 2 PR description `## Lane evidence` 블록 + 7-row valid format 검증. Fast-pass (type:epic / doc-only PR / non-Phase-2 PR), bypass (PR description `BYPASS: <reason>`), 부재/invalid → action_required.
- `scripts/check-lane-evidence.sh` + `.ps1` (NEW) — Story §14 ↔ PR description cross-validate (lane name set 일치 + bypass reason 명시). Auto-detect Story path from branch + PR number from gh CLI. Default exit 0 advisory (ADR-027 §결정 2 정합), `--strict` flag → exit 1.
- `scripts/test-check-lane-evidence.sh` (NEW) — 5 smoke test (single-pass fixture / missing story default / missing story strict / --help / unknown arg). 5/5 PASS local.
- `scripts/fixtures/check-lane-evidence/single-pass-story.md` (NEW) — fixture story 7-lane PASS 모두 §14 row carry. 향후 follow-up 에서 multi-iteration FIX / bypass fixture 확장.
- `templates/github-pr-template.md` (Modify) — Phase 2 PR template 에 `## Lane evidence` placeholder 7-row 추가 + `bash scripts/check-lane-evidence.sh` 검증 task 추가.
- `templates/consumer-scripts.manifest` (Modify) — `scripts/check-lane-evidence.sh:templates/github-workflows/lane-evidence-check.yml` entry 추가 (CFP-109 schema 정합).
- `CLAUDE.md` (Modify) — §"오케스트레이션 규칙" 의 "Wrapper 위임 패턴" 에 lane evidence invariant 1 line 추가 (ADR-031 cross-ref + bypass + effective date + .claude-work 분리).
- Sonnet decider CFP-126-001 storage location pick (a) §14 (high confidence) — Phase 1 PR #59 archived. Codex 7-area review CFP-126-002 = HOLD → CONDITIONAL_PASS, P1=7 모두 pre-merge fixed (file missing 해소 + spawn_id + fix_iteration cross-ref + output_status partial-row + §13 vs §14 verification + ADR-031 transition + .claude-work non-authoritative).
- Story SSOT: codeforge-internal-docs PR #59 (Phase 1).
- Parent Epic: CFP-124 (#230 + #57).
- Resolves CFP-124 Gap #1 (Lane plugin 실제 spawn 흔적 invariant 부재) + root cause A1.
- ADR-031 status (Proposed → Accepted) + §결정 1 (a) §14 pick freeze = 별도 small wrapper amend PR (CFP-124 #230 merge 후 즉시).

### CFP-127 — Phase 2: bootstrap strict mode opt-in (ADR-032 amendment 1)

- `overlay/hooks/check_bootstrap.py` (Modify) — `argparse` 추가 (`--strict` / `--quiet` flag), `_check_bypass_active()` + `_check_strict_mode_active()` + `_classify_strict_eligible()` helper 신설. NEW check 9 (`check_settings_hooks` — SessionStart × 2 + UserPromptSubmit × 1 hook 등록 검증). Strict mode 활성 조건 (CLI > env > yaml): `--strict` flag / `CODEFORGE_STRICT_BOOTSTRAP=1` / `bootstrap.strict_mode: true` (project.yaml). Strict-eligible drift 4종 (Sonnet pick alpha CFP-127-001): (a) project.yaml 부재 (b) plugin 8 critical (wrapper + 6 lane + superpowers) 미설치 (c) settings.json 3 hook 미등록 (d) 10 critical label (phase:* 7 + gate:* 3) 부재. Strict 활성 + drift 발견 → exit 1. Bypass priority HIGHEST: `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip (ADR-027 §결정 3 정합).
- `overlay/hooks/check-bootstrap.sh` + `.ps1` (Modify) — `--strict` / `--quiet` flag passthrough (`-Strict` / `-Quiet` for PowerShell). Exit code passthrough from Python core (default 0, strict + drift 1).
- `docs/project-config-schema.md` (Modify) — `bootstrap.strict_mode` field 명세 (boolean, default false). Priority + Bypass precedence + Revert procedure 명시.
- `overlay/hooks/validate_config.py` (Modify) — SCHEMA_RULES 에 `bootstrap.strict_mode` boolean validator 추가.
- `overlay/_overlay/project.yaml.example` (Modify) — `bootstrap.strict_mode` commented field 예시 + 점진 도입 + revert + Bypass 정합 안내.
- `docs/consumer-guide.md` (Modify) — §2i 신설 "Strict mode opt-in" — 점진 도입 4 단계 절차 + 3 mechanism 우선순위 표 + strict-eligible 4종 detection + revert procedure + ADR-027 §결정 3 Bypass 동시 작동.
- `scripts/test-check-bootstrap-strict.sh` (NEW) — 6 smoke test (--help / default silent skip / --strict no yaml / bypass priority HIGHEST / env-priority / yaml fixture). 6/6 PASS local.
- `scripts/fixtures/check-bootstrap-strict/clean/.claude/_overlay/project.yaml` (NEW) — fixture with `bootstrap.strict_mode: true`.
- Sonnet decider CFP-127-001 (Phase 1 PR #60) strict-eligible 4-type pick alpha (high confidence) — 본 Phase 2 = implement.
- Codex 7-area review CFP-127-002 (Phase 1) — CONDITIONAL_PASS, 6 P1 fixed.
- ADR-032 status (Proposed → Accepted) finalize = 별도 small wrapper amend PR (CFP-124 #230 merge 후).
- Story SSOT: codeforge-internal-docs PR #60 (Phase 1).
- Parent Epic: CFP-124 (#230 + #57).
- Resolves CFP-124 Gap #4 (`check_bootstrap` warning-only) + root cause A0 (LLM-trust enforcement architectural 한계).

### CFP-74 — Post-merge follow-up automation (ADR-026)

- `docs/adr/ADR-026-post-merge-automation.md` (NEW) — 4 결정 (Wrapper Orchestrator post-merge automation 의무 / Cross-repo PAT / Telemetry only / Disable-by-flag + main 직접 push 금지). Sonnet decider (CFP-74-001) pick=alpha, Codex round 2 audit (gpt-5.5 high, ADR conflict 0/7).
- `templates/github-workflows/post-merge-followup.yml` (NEW) + `.github/workflows/` self-apply — 4 sequential actions (phase label transition / cross-repo Story §9 writer / carrier Issue close / sibling PR auto-close) + telemetry counter + disable-by-flag + per-action outcome tracking.
- `scripts/{next-phase,post-merge-story-writer,post-merge-sibling-close,post-merge-telemetry}.sh` (NEW, 4 scripts) — workflow action implementations. Cross-repo write via CODEFORGE_CROSS_REPO_PAT (CFP-71 precedent), main 직접 push 금지 (branch + PR pattern).
- `<internal-docs>/wrapper/post-merge-counters.jsonl` (NEW telemetry, on first run) — JSONL append-only, contract_version 1.0. Long-lived `telemetry-counters` rolling branch (auto-PR), accumulates outcome events across runs. PMOAgent retro 30+ run 후 ROI 평가.
- `docs/orchestrator-playbook.md` (Modify) — §15 reserved (CFP-73 Phase 2 stop-event-v1 deferred placeholder) + §16 신설 (post-merge automation flow narrative SSOT).
- `CLAUDE.md` (Modify) — workflow list 10 → 11 fixture (`post-merge-followup.yml` 추가).
- Codex audit P0 (telemetry main push violation) + 4 P1 (phase transition source / outcome aggregation / JSONL newline / rerun idempotency) + P2 (story_uri marker) — pre-merge 모두 fixed.
- Story SSOT: internal-docs `wrapper/stories/CFP-74.md` (PR #31 merged 2ce571b).

CFP-74 Phase 1 dogfood 4 followup PR (5 iteration 통과 후 production-ready):
- **Followup #1** (PR #225): exec bit (100644 → 100755) 누락 fix + chore PR detection (`^chore[:(]`+ multi-CFP regex `grep -oiE | sort -u | wc -l > 1`).
- **Followup #2** (PR #226): case-insensitive CFP regex (`grep -oE` → `grep -oiE` + `tr '[:lower:]' '[:upper:]'` normalize) — lowercase PR convention `feat(cfp-N):` extraction silent no-op fix.
- **Followup #3** (PR #227): §9 row insertion logic — awk state machine `in_table` mode 추가, table header 자동 삽입, append-only chronological ordering. Codex P1 (existing_table flag-only) FIXED.
- **Followup #4** (PR #228): CI invariant `script-exec-bit (CFP-74 invariant)` (`scripts/check-script-exec-bit.sh` + `.github/workflows/lint.yml`) — 미래 `Permission denied` drift 사전 차단. Codex P2 #2 (bash prefix false positive) FIXED.

Lesson: 신규 cross-repo workflow 배포 = 3-5 dogfood iteration 일반적 패턴 입증.

### CFP-123 — Live Epic lane-entry policy (ADR-030)

- `docs/adr/ADR-030-live-entry-gate-policy.md` (NEW) — 5 결정 (gate:live-entry-pass label 정의 / Live touching Story 식별 mechanism / phase-gate-mergeable.yml validation / 3-condition AND consumer-side SSOT / fast-pass 영향 차단). mctrader debut audit P0 (Codex gpt-5.5 high 2026-05-04) 해소.
- `docs/inter-plugin-contracts/label-registry-v1.md` (Modify, v1.2 → v1.3 minor bump) — gate:* 카테고리 2종 → 3종 (`gate:live-entry-pass` 추가). Color 0e8a16, single_active false.
- `scripts/bootstrap-labels.sh` (Modify) — `gate:live-entry-pass` 1 line idempotent create.
- `templates/github-workflows/phase-gate-mergeable.yml` (Modify) + `.github/workflows/` self-apply — Live touching Story (Story frontmatter `live_touching:true` OR PR body marker) + phase:보안-테스트 시 본 gate 추가 검증. Membership-style gate check (PR carries multiple gate:* labels simultaneously).
- `CLAUDE.md` (Modify) — 보안 테스트 row gate list 갱신 (조건부 gate:live-entry-pass 추가, ADR-030).
- Codex audit P1 (gate label first-only bug) + 2 P2 (ADR phase reference / registry purpose text) — pre-merge fixed.
- Story SSOT: internal-docs `wrapper/stories/CFP-123.md` (PR #52 merged e1296ff).
- Resolves issue #156.

### CFP-114 — Phase execution visibility expansion (ADR-029)

- `docs/adr/ADR-029-phase-execution-visibility-expansion.md` (NEW) — 5 결정 (sub-step event narration 의무 / format 표준 + sanitize policy / stop discipline cross-reference / verbosity opt-out / Lane plugin 변경 불요). 사용자 directive (2026-05-05) "phase 와 내부 진행단계를 완료 시마다 출력해주어야 한다" 해소.
- `docs/orchestrator-playbook.md` (Modify, §14.5 갱신) — Trigger SSOT 표 4 sub-step event (Deputy spawn / Deputy return / 병렬 dispatch R3·R4·R7·R9 / R9 subset 완료) terminal narration ❌ → ✅ 전환. R10 prefetch skip 유지.
- `docs/project-config-schema.md` (Modify) — `progress_narration_verbosity: full | lane_only` field 명세 (default `full`).
- `overlay/_overlay/project.yaml.example` (Modify) — 신규 field 예시 (commented).
- `overlay/hooks/validate_config.py` (Modify) — `_is_progress_narration_verbosity` enum validator + SCHEMA_RULES 추가.
- `docs/consumer-guide.md` (Modify) — verbosity 사용법 subsection.
- `CLAUDE.md` (Modify) — ADR-029 reference (Orchestration 규칙 §).
- Stop discipline 정책 변경 없음 — ADR-022 + ADR-025 + Amendment 1 SSOT 그대로 cross-reference.

### CFP-122 — ADR-020 Amendment 2 — Mechanical Epic mode

- `docs/adr/ADR-020-cross-repo-epic-pattern.md` (Modify) — Amendment 2 신설:
  - **Mode C: Mechanical Epic** — Mode B special case. wrapper-driven Epic 의 Phase 2-N 가 동일 mechanical apply 시 child Story Issue / per-lane spec/plan 생략 허용.
  - 4 조건 AND (file content 동일 / acceptance criteria 동일 / Sonnet trigger 무발화 / parent Epic §5 표 enumerate).
  - PR body / Story frontmatter `mode: mechanical` marker 의무.
  - CFP-120 + CFP-121 Phase 2 post-hoc ratification.

### CFP-121 — Superpowers schema drift quarterly review (wrapper Phase 1)

- `templates/superpowers-skill-snapshot.txt` (NEW) — pinned snapshot of 14 superpowers v5.1.0 skills.
- `scripts/check-superpowers-schema-drift.sh` (NEW) — 2-check lint: SSOT-referenced skills ⊆ snapshot (broken reference detection) + (optional) snapshot vs local install diff (advisory).
- `scripts/test-check-superpowers-schema-drift.sh` + `scripts/fixtures/superpowers-schema-drift/` (NEW, 3 fixture TDD).
- `templates/github-workflows/superpowers-schema-drift.yml` (NEW) — quarterly cron + manual dispatch + PR trigger. Auto-creates Issue if scheduled drift detected.
- `docs/superpowers-integration.md` §2 + §3 fix (DOGFOOD test caught existing CFP-113 bug):
  - SSOT row 22 `review/ClaudeReviewAgent`: `superpowers:code-reviewer` → `superpowers:requesting-code-review` (실제 superpowers v5.1.0 에 `code-reviewer` 는 standalone skill 아님, `requesting-code-review` skill 의 dispatch subagent).
  - §3 row 7 변환 표 동일 수정.
- Phase 2 follow-up: codeforge-review ClaudeReviewAgent.md 의 동일 typo 수정 (별도 lane PR).

### CFP-120 — Lane plugin parity gap fix-back (Phase 1 wrapper)

- `.gitattributes` (NEW, all 7 codeforge family repos via Phase 2-7 batch) — `*.sh text eol=lf executable` + line ending normalization. Windows clones default `core.autocrlf` 가 LF→CRLF + exec bit 손실 → CI permission denied 사고 영구 fix (CFP-113 Phase 1 발견).
- `scripts/bootstrap-codeforge-family.sh` (NEW) — 7 codeforge family repo (wrapper + 6 lane) label set 일괄 부트스트랩. CFP-113 Phase 2-7 시 manual `gh label create` workaround 영구 fix.
- `docs/consumer-guide.md` §2d (Modify) — codeforge family setup 시 `bootstrap-codeforge-family.sh` 사용법 추가.
- Phase 2-7 lane plugin (6 repos) — `.gitattributes` 동일 standard 적용.

### CFP-113 — Superpowers integration wrapping (Phase 1 wrapper SSOT)

- `docs/superpowers-integration.md` (NEW) — codeforge ↔ superpowers 통합 SSOT (6 sub-section, 23 호출 지점 / 7 skill / 15 agent file enumerate).
- `docs/adr/ADR-028-superpowers-integration-policy.md` (NEW) — 6 결정 (SSOT 위치 / contract / path override / 변환 표 / helpers 소유권 / Phase 2-7 batch open). Sonnet decider Option B + Codex 3 mod + Sonnet 2 mitigation 통합.
- `docs/adr/ADR-017-skill-override-path-enforcement.md` (Modify) — Amendment 1: agent md `Edit/Write(docs/superpowers/**)` 권한 표기 lint 추가. effective date = Phase 1 PR merge 직후.
- `templates/skill-prompt-helpers/{brainstorming-path-override,writing-plans-path-override,tdd-discipline,verification-before-completion}.md` (NEW, 4 fragment) — wrapper-owned, lane import-only.
- `scripts/check-superpowers-integration.sh` + `scripts/test-check-superpowers-integration.sh` + `scripts/fixtures/superpowers-integration/` (NEW) — 3 check lint (SSOT row drift / stale path / inline copy) + 4 fixture test runner.
- `templates/github-workflows/superpowers-integration.yml` (NEW) — PR check (fail-closed self-test + real wrapper state lint).
- `CLAUDE.md` (Modify) — "필수 플러그인 9종" 의 superpowers 표기 명확화 + integration SSOT link.
- `overlay/hooks/check_bootstrap.py` (Modify) — REQUIRED_PLUGINS comment + WARN 메시지 보강 (non-blocking 유지).
- `docs/orchestrator-playbook.md` (Modify) — §1.1 checklist 0번 superpowers ✅ line 에 integration SSOT link.
- `docs/consumer-guide.md` (Modify) — §1b 플러그인 4종 의 superpowers 표기 link.
- Story / spec / plan / change-plan / decision archive — internal-docs `wrapper/{stories,specs,plans,change-plans,decisions}/` (ADR-013 dogfood-out).
- Phase 2-7 lane plugin batch open at Phase 1 merge — agent prose 정합 + 4 stale path 정리 (3 ReviewPL + PMOAgent) acceptance criteria.

### CFP-96 — Phase 7: Epic close

- `wrapper/retros/EPIC-RESULTS-CFP-96.md` (NEW, codeforge-internal-docs) — Epic close artifact.
- Spec verbiage fix-back — `consumer-shared 11종 + Story-flow 4종 = 14종` → 실제 EXPECTED_WORKFLOWS_FULL 7종 (Phase 6/6b finding).
- 9 Decision YAML 일관성 검증 (CFP-96-001 + CFP-96-002 + CFP-103~108 + CFP-111).
- 7 child Story (CFP-103~108 + CFP-111) 모두 close.
- 3 finding (#143 / #144 / #169) + CFP-45 4건 모두 close.
- mctrader 6-repo (1 hub + 5 sister) full codeforge adoption — 매 변경 시 codeforge protocol 의무 자동 enforcement.
- 76 pytest (Phase 2a 22 + Phase 2b 54) Windows native pass.

### CFP-96 — First-Consumer Adoption Bootstrap Phase 1 (doc-only)

- `docs/adr/ADR-027-consumer-adoption-protocol.md` (NEW) — 5 결정 freeze: bootstrap 검증 책임 = wrapper overlay/hooks/, 3-trigger enforcement (Story phase / UserPromptSubmit / SessionStart), bypass = HOTFIX_BYPASS_CODEFORGE env, cross-platform (POSIX + Windows), consumer-guide.md = 절차 SSOT.
- 6 child Story registered (CFP-103~108, #199~#204) for Phase 2~6 implementation. Phase 7 = Epic close.
- Spec/plan/change-plan/decisions: codeforge-internal-docs/wrapper/ (ADR-013 dogfood-out).
- Phase 2 (CFP-103+CFP-104) version bump: 5.2.0 → 5.3.0 (예상).

### CFP-106 — Phase 4: #143 + #144 + #169 close

- `templates/github-workflows/phase-gate-mergeable.yml` (Modify) — doc-only / `type:epic` fast-pass step 추가 (#143 fix). PR labels 에 `type:epic` 있거나 모든 변경 file 이 `docs/`/`wrapper/`/`.github/`/`*.md`/`CHANGELOG.md`/`README.md` 인 경우 자동 `success` conclude — phase + gate 라벨 검증 우회.
- `docs/consumer-guide.md` §7.5 (NEW) — CI Terminal State Classification (#144 fix): 8-state 표 (SUCCESS / FAILURE / ACTION_REQUIRED known/unknown / NEUTRAL / SKIPPED / BLOCKED MERGEABLE / UNKNOWN) + watch 명령 패턴 + enforce_admins toggle 기법.
- `overlay/hooks/regen-agents.sh` (Modify) — docstring 예시 schema-correct fix (#169). Flat `{"command": "..."}` → nested 3-level `{"hooks": [{"type": "command", "command": "..."}]}`. `${CLAUDE_PLUGIN_ROOT}` 치환 한계 안내 추가.
- ADR-027 §결정-2 Tertiary trigger (SessionStart 강화) + §결정-5 (consumer-guide SSOT) implementation.

### CFP-104 — Phase 2b: UserPromptSubmit hook (변경 착수 reminder inject)

- `overlay/hooks/userprompt_reminder.py` (NEW) — Python core (regex change-intent + branch parse + bypass env).
- `overlay/hooks/userprompt-reminder.sh` (NEW) — POSIX thin wrapper (CFP-103 패턴 reuse).
- `overlay/hooks/userprompt-reminder.ps1` (NEW) — Windows PowerShell thin wrapper.
- `overlay/hooks/tests/test_userprompt_reminder.py` (NEW) — 54 pytest 단위 테스트 (cross-platform CI matrix).
- `templates/settings.json.example` (NEW) — consumer 측 hook 등록 템플릿 (SessionStart + UserPromptSubmit).
- ADR-027 §결정-2 Secondary trigger (UserPromptSubmit) implementation.
- bypass: `HOTFIX_BYPASS_CODEFORGE=1` + `HOTFIX_BYPASS_REASON='<사유>'` 양 env 의무 (사유 추적). flag 만 set 시 bypass NOT honored + reminder 에 WARN 포함.
- 활성 Story 검출: git branch 명 `cfp-N/...` / `mct-N/...` parse → reminder 에 Story key + phase 노출.

### CFP-103 — Phase 2a: bootstrap protocol Python core + cross-platform wrapper

- `overlay/hooks/check_bootstrap.py` (NEW) — Python core for cross-platform check (validate_config.py 패턴).
- `overlay/hooks/check-bootstrap.sh` (Modify) — thin POSIX wrapper, calls check_bootstrap.py.
- `overlay/hooks/check-bootstrap.ps1` (NEW) — Windows PowerShell wrapper.
- `overlay/hooks/tests/test_check_bootstrap.py` (NEW) — 22 pytest 단위 테스트 (cross-platform CI matrix 권장).
- `overlay/hooks/tests/fixtures/installed_plugins_{full,partial,empty}.json` (NEW) — fixture (mctrader-hub 검증 데이터 포함).
- 4 NEW check (CFP-103): 11 plugin install (`installed_plugins.json`) + consumer `.github/workflows/` file 존재 + `.github/ISSUE_TEMPLATE/` 3종 sync + `CODEOWNERS` 정합.
- 4 보존 (CFP-11/86/89/97): workflow permissions / 18 plugin labels / workflow_distribution.mode / consumer-scripts manifest drift.
- Non-blocking exit 0 invariant 보존.
- `overlay/_overlay/project.yaml.example` — `bootstrap.expected_workflows` override field 추가.
- ADR-027 결정 1 (bootstrap 검증 책임 = wrapper overlay/hooks/) + 4 (cross-platform) implementation.
- Codex Phase 2 entry review (agent a394d669843f0a58b) Sonnet decider pick=split (CFP-103 선행, CFP-104 후행) HIGH confidence.

## [5.2.0] - 2026-04-30

### CFP-47 — Stateful / restart invariant test category (ADR-015)

CFP-46 (Operational Risk Architect 6th deputy) 의 검증-side 짝. §8 Test Contract 에 §8.5 CONDITIONAL sub-section 신설 + codeforge-test lane 1→2 agent split + 양 contract additive minor in-place bump.

### Added

- `docs/adr/ADR-015-stateful-test-category.md` — carrier ADR (5 결정 + 거부된 대안)
- 책임 매트릭스 §8.5 row (TestContractArch primary + DesignReview 감사 P0 차단 + StatefulTestAgent 검증)
- 원인 판정 decision table 4 row (cache drift / queue accumulation / restart loss / replay failure)
- 6 deputy mandate matrix §8.5 row (TestContractArch primary)
- `scripts/check-doc-section-schema.sh` §8.5 applicability 표 강제 (4 Y/N + substantive reason 30자 minimum, vague 차단) [후속 PR-G]
- 4 lint fixture (passing-y-applies / passing-n-substantive / failing-y-no-section / failing-n-vague) [후속 PR-G]
- `agents/StatefulTestAgent.md` (codeforge-test) — long-running + restart invariant 전담 [후속 PR-F]

### Changed

- `.claude-plugin/plugin.json`: 5.1.0 → 5.2.0 + description CFP-47 / ADR-015 + `stateful-testing` keyword
- `templates/change-plan.md` (codeforge-design): §8.4 직후 §8.5 신설 (체크표 + §8.5.1-§8.5.4) [후속 PR-C]
- `agents/TestContractArchitectAgent.md` (codeforge-design): mandate.primary 에 §8.5 추가 [후속 PR-B]
- `docs/inter-plugin-contracts/design-output-v2.md`: contract_version 2.0 → 2.1 (additive minor — sections_authored 에 §8.5 추가) [후속 PR-D]
- `docs/inter-plugin-contracts/test-verdict-v1.md`: contract_version 1.0 → 1.1 (additive minor — stateful_invariant_results optional 필드) [후속 PR-E]
- `docs/inter-plugin-contracts/MANIFEST.yaml`: design_output / test_verdict version 갱신 [후속 PR-D / PR-E]
- `agents/TestAgent.md` (codeforge-test): functional/integration/infra/perf 영역 명시 (StatefulTestAgent 와 boundary clarity) [후속 PR-F]
- `CLAUDE.md` (codeforge-test): self-write 책임 표 갱신 + failure ownership 매트릭스 추가 [후속 PR-F]

### Migration

- consumer 무영향 — 모든 bump minor (additive)
- 기존 §8 N/A Story 에 §8.5 자동 N/A (포함 관계)
- in-flight Story 는 transition period (1 sprint) 동안 §8.5.0 체크표 추가 작성 의무
- marketplace sync 는 CFP-49 sweep 에 포함 (별도 진행)

## [5.1.0] - 2026-04-30

### CFP-46 — Operational Risk Architect 6th deputy + §7.4 운영리스크 + §11.6 idempotency CONDITIONAL (ADR-014 신설)

ζ arc (CFP-31~40) 후 첫 minor bump. 암호화폐 트레이딩 시스템 대비 production-readiness invariant 통합 — 외부 의존 disconnect / clock drift / rate limit / env isolation / DR / idempotency.

### Added

- `docs/adr/ADR-014-operational-risk-ssot-distribution.md` — carrier ADR (OperationalRiskArchitectAgent SSOT 분배 + §7.4 5 sub-item + §11.6 CONDITIONAL + design-output v1→v2 BREAKING 결정 5종)
- `docs/inter-plugin-contracts/design-output-v2.md` — sibling. 6 deputy schema (op_risk_arch + idempotency_applicable) + sections_authored §7.4/§7.5/§7.6/§7.7 + §11.6/§11.7 mirror
- 6 deputy mandate 매트릭스 — wrapper CLAUDE.md 4번째 SSOT 예외 (ADR-012 §3 amendment)
- 책임 매트릭스 §7.4 운영리스크 8 행 + §11 Idempotency CONDITIONAL 행 추가
- 원인 판정 decision table §7.4 5 행 + §11 Idempotency 1 행 추가
- `scripts/check-doc-section-schema.sh` — §7.4 schema (5 sub-item) + CONDITIONAL N/A justification 10-char minimum 검증
- `scripts/test-check-doc-section-schema.sh` + 4 fixture (passing / failing-no-na / failing-empty-na / failing-short-na)

### Changed

- `.claude-plugin/plugin.json`: 5.0.1 → 5.1.0 + description (CFP-46 / ADR-014 / 6 deputy / §7.4 / §11.6 반영)
- `docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md` §3: "3 named SSOT exceptions" → "4 named SSOT exceptions" (carrier ADR pattern)
- `docs/orchestrator-playbook.md`: 13 location 5 deputy → 6 deputy + token budget 200k→225k / 320k→345k 재조정 (CFP-21 precedent)
- `docs/inter-plugin-contracts/design-output-v2.md` §4 6 deputy 통합 표 DataMigrationArchitectAgent consult 행 §11.6 OpRiskArch consult 추가 (CFP-46 cleanup C4)

### BREAKING (lane plugin internal — wrapper consumer 영향 없음)

- `design_output` contract v1 → v2 BREAKING (ADR-008 룰): deputies_results.op_risk_arch 신규 + sections_authored §7 sub-numbering shift (§7.4 운영리스크 신규, 기존 §7.4 민감→§7.5 / §7.5 위협매핑→§7.6 / §7.6 N/A→§7.7)

### Migration

- consumer 무영향 — wrapper plugin level 은 minor bump
- lane plugin (codeforge-design) 측 0.1.0 → 0.2.0 BREAKING (consumer 영향 없음 — overlay 기반 사용자에게는 transparent)
- marketplace.json sync (ζ arc + CFP-46 누적 drift) 는 별도 CFP-49 sweep 예정

## [Unreleased] - CFP-E (2026-04-30)

### CFP-E — Inter-plugin Contract Drift Detection (ADR-011 신설)

ADR-010 §5 후속 ADR 직접 충족. wrapper PR/push 시 canonical (lane plugin repo) ↔ wrapper sibling 본문 verbatim drift 자동 검증.

### Added

- `docs/adr/ADR-011-inter-plugin-contract-drift-detection.md` — drift detection 정책 동결 (live fetch + 정규화 5단계 + Archived skip + PR/push trigger only)
- `scripts/check-inter-plugin-drift.sh` — canonical live fetch (GitHub REST API) + 정규화 + byte-verbatim 비교 lint
- `scripts/test-check-inter-plugin-drift.sh` — 회귀 테스트 harness (T-1 ~ T-8: 정합 / sibling drift / canonical drift / meta heading 변형 / line ending / Archived skip / Active 404 / trailing whitespace)
- `.github/workflows/contract-lint.yml` 신규 job `inter-plugin-drift (CFP-E)` + `workflow_dispatch:` trigger

### Fixed

- 5 lane output sibling (requirements/design/develop/test/pmo output v1) 의 inherited drift 제거 — CFP-42 sibling backfill 시 author 가 의도치 않게 prepend 한 short intro 1 줄 제거. drift detection lint dogfood 결과로 발견한 사후 fix.

### Migration

- consumer 무영향 — 신규 lint 추가만
- 첫 PR/push merge 후 1일 dogfood 후 main branch protection 의 required-status-check 에 `inter-plugin-drift (CFP-E)` 수동 등록 권장

## [Unreleased] - CFP-D (2026-04-30)

### CFP-D — review_verdict v1 Deprecated → Archived

consumer 부재 확신 (사용자 명시 2026-04-30) 으로 v1 grace period 불필요. 실행 시점 canonical (codeforge-review) repo 의 `docs/inter-plugin-contracts/` 에 v1 file 부재 확인 — wrapper 가 v1 단독 SSOT (option α 채택, canonical PR drop).

### Changed

- `docs/inter-plugin-contracts/review-verdict-v1.md` frontmatter `status: Deprecated → Archived`. body header `(DEPRECATED) → (ARCHIVED)`. warning paragraph 갱신 (CFP-D 전환 시점 + ADR-008 §5 historical record 보존 명시)
- `docs/inter-plugin-contracts/MANIFEST.yaml` v1 entry status `Deprecated → Archived`
- `CLAUDE.md` "Inter-plugin Contract" 표 review_verdict v1 컬럼: `(Deprecated) → (Archived)`
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md` §5.1 신규 단락 — Deprecated → Archived 전환 트리거 3 조건 정의 (consumer 부재 + 후속 MAJOR 1+ release + canonical/sibling sync 또는 wrapper 단독)
- `docs/orchestrator-playbook.md` line 26 narrative: `review_verdict v1 → v2` (v1 Archived 명시)
- `docs/migration-guide.md` line 98/109/112 narrative: 현재 active schema v2 + v1 Archived 명시
- 5 history file (`cfp-31` spec, `cfp-42` spec+plan, `zeta-arc` retro, `ADR-009`) v1 status reference 갱신

### Migration

- consumer 부재 — 액션 불필요
- v1 file 자체는 historical record 로 영구 보존 (ADR-008 §5 룰 — 삭제 금지)
- 향후 v1 schema 참조하던 코드 (없음 — v2 active 부터 v1 사용 0) 는 v2 로 migrate 필요

## [5.0.1] - 2026-04-29

### CFP-41 (ζ arc retro) — 종합 회고 + ADR-009 Adopted (Patch)

ζ arc parent spec (CFP-31) §5.10 마지막 deliverable. lane plugin 6개 추출 + DocsAgent 해체 완료 후 종합 검증.

### Added

- `docs/adr/ADR-009-wrapper-only-decomposition.md` — 신규 ADR (status: Adopted). ζ arc 결정 영속 기록
- `docs/retros/2026-04-29-zeta-arc-completion.md` — ζ arc 종합 회고 (Codex round 2 5 조건 검증 + 사용자 진단 통증 해소 검증)

### Changed

- `.claude-plugin/plugin.json` v5.0.0 → v5.0.1 (patch — retro/ADR doc only)

### Why

ζ arc 6 lane plugin 추출 (CFP-32 ~ CFP-40) 완료 후 결정 영속 + 사용자 진단 통증 해소 검증 필요. ADR-009 가 wrapper-only 결정의 SSOT.

### Validation 검증 시나리오 (retro 본문)

- "새 architect deputy 추가" 시 wrapper 무손상 ✓
- "새 role:dev (예: ML Engineer)" 시 wrapper 무관 ✓
- ζ arc 진행 중 6+ silent drift 자동 catch (lint harness 가치 입증) ✓

## [5.0.0] - 2026-04-29

### CFP-40 (ζ arc LAST) — codeforge-design plugin extraction + DocsAgent final delete (BREAKING)

ζ arc 마지막 lane plugin 추출 (parent §5.10). 7 design agents + 2 templates 이전. **DocsAgent agent file 최종 삭제** — wrapper-only end-state 도달.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.10. Codex round 2 sequencing 권고: design 가장 마지막 (가장 큰 표면 — split-brain 위험 회피).

### Removed (BREAKING)
- `agents/{ArchitectPL,Architect,CodebaseMapper,Refactor,SecurityArchitect,TestContractArchitect,DataMigrationArchitect}Agent.md` → mclayer/plugin-codeforge-design (7 agent)
- `agents/DocsAgent.md` — **최종 삭제** (CFP-32부터 단계적 권한 회수 끝)
- `templates/change-plan.md` → mclayer/plugin-codeforge-design
- `templates/adr.md` → mclayer/plugin-codeforge-design

### Changed
- `CLAUDE.md` 9 → 10 plugin (codeforge-design 추가). agent count 8 → 0 (wrapper-only)
- `CLAUDE.md` description: "19 core 에이전트" 패턴 → "0 core 에이전트 (wrapper-only)"
- `.claude-plugin/plugin.json` description: 완전 재작성 — wrapper-only end-state 반영
- 다수 file 의 broken link → external URL (ArchitectAgent, ArchitectPLAgent, deputies, change-plan/adr templates, DocsAgent)
- `scripts/check-write-permission-redistribution.sh` — ArchitectAgent / DocsAgent 부재 시 skip
- `.claude-plugin/plugin.json` v4.0.0 → v5.0.0 BREAKING

### Why
ζ arc parent spec §2.1 end-state 도달: codeforge wrapper agent 0개. Orchestrator (top-level Claude 세션) + playbook + CI workflows + cross-plugin schema templates + inter-plugin contracts SSOT location 만 wrapper에 잔류.

DocsAgent 최종 삭제 정당화:
- §10 owner = Orchestrator (CFP-32)
- §9 owner = codeforge-review (CFP-35)
- §11 owner = codeforge-pmo (CFP-36)
- §2/§5/§6 owner = codeforge-requirements (CFP-37)
- §10 trigger reporter = codeforge-test (CFP-38)
- §8/§8.5 owner = codeforge-develop (CFP-39)
- §3/§7/§11 mirror owner = codeforge-design (본 CFP)
- §1 owner = story-init.yml CI Action (plugin 무관)
- 일반 docs/** writes (orchestrator-playbook, consumer-guide 등) = Orchestrator 직접 (top-level 세션 path-scoped 권한 무관)

### Followups (CFP-41 retro)
- ζ arc 종합 검증 + ADR-009 status Accepted → Adopted
- 가상 시나리오 검증 (새 deputy 추가 시 wrapper 무손상)
- core agent 수 19 → 0 도달 audit

## [4.0.0] - 2026-04-29

### CFP-39 (ζ arc) — codeforge-develop plugin extraction (BREAKING)

ζ arc 다섯 번째 lane plugin (parent §5.9). 5 agent + presets/webapp 이전.

### Removed (BREAKING)
- `agents/{Developer,DataEngineer,InfraEngineer,DeveloperPL,QADeveloper}Agent.md` → mclayer/plugin-codeforge-develop
- `presets/` 전체 → mclayer/plugin-codeforge-develop

### Changed
- `CLAUDE.md` 8 → 9 plugin, agent count 13 → 8
- `CLAUDE.md` write-queue 표 + 외부 plugin listing 갱신
- 7 broken link → external URL (DeveloperPLAgent, presets/)
- `.claude-plugin/plugin.json` v3.0.0 → v4.0.0 BREAKING

### Why
ζ arc §5.9: DeveloperPL의 role:dev roster 동적 discovery + 5 agent + presets 가 응집된 단위. CFP-31 §3.5 거부 (Codex round 2 권고 "overlay 충분")는 wrapper-only end-state 와 충돌이라 폐기 — 본 CFP에서 명시적 이전.

### Followups
- CFP-40: codeforge-design (last — 가장 큰 표면 7 agent + change-plan/adr templates)
- CFP-41: ζ arc retro

## [3.0.0] - 2026-04-29

### CFP-38 (ζ arc) — codeforge-test plugin extraction (BREAKING)

ζ arc 네 번째 lane plugin 추출 (parent §5.8). TestAgent 단독 + owner doc 부재 — 가장 단순한 lane.

### Removed (BREAKING)
- `agents/TestAgent.md` → mclayer/plugin-codeforge-test

### Changed
- `CLAUDE.md` 필수 플러그인 7 → 8종 (codeforge-test 추가). agent count 14 → 13
- `CLAUDE.md` write-queue 표 — TestAgent 제거
- `docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md` 2건 broken link → external URL
- `.claude-plugin/plugin.json` v2.0.0 → v3.0.0 BREAKING

### Why
ζ arc §5.8: 가장 단순한 lane (1 agent + owner doc 부재) — Codex sequencing 권고대로 review/pmo/requirements 검증 후 진입.

### Followups
- CFP-39: codeforge-develop (5 agent + presets, role:dev 동적 roster)
- CFP-40: codeforge-design (7 agent + change-plan/adr templates — 가장 큰 표면, last)
- CFP-41: ζ arc retro

## [2.0.0] - 2026-04-29

### CFP-37 (ζ arc) — codeforge-requirements plugin extraction (BREAKING)

ζ arc 세 번째 lane plugin 추출 (parent §5.7). 4 sub-agent (RequirementsPL + Domain + Analyst + Researcher) + 도메인 KB owner write + Story §2/§5/§6 self-write 를 별도 plugin `codeforge-requirements` 으로 이전.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.7.

### Removed (BREAKING for consumer)
- `agents/RequirementsPLAgent.md` → mclayer/plugin-codeforge-requirements
- `agents/DomainAgent.md` → mclayer/plugin-codeforge-requirements
- `agents/RequirementsAnalystAgent.md` → mclayer/plugin-codeforge-requirements
- `agents/ResearcherAgent.md` → mclayer/plugin-codeforge-requirements
- `templates/domain-knowledge.md` → mclayer/plugin-codeforge-requirements

### Changed
- `CLAUDE.md` 필수 플러그인 6종 → 7종 (`codeforge-requirements@mclayer` 추가). agent count 18 → 14
- `CLAUDE.md` Write queue 의뢰 권한 표 — 4 agent 제거 + 외부 plugin listing 갱신
- `CLAUDE.md` 외부 도구 wrapper 표 — RequirementsAnalyst codex CLI 의존성 codeforge-requirements 로 이전 표시
- 3 file 의 DomainAgent / domain-knowledge 링크 → mclayer/plugin-codeforge-requirements external URL
- `.claude-plugin/plugin.json` v1.0.0 → v2.0.0 BREAKING

### Why
ζ arc §5.7: 4 sub-agent 병렬 패턴이 본 plugin 의 응집성 핵심. 도메인 KB owner write 이전이 "writer-distributed + path-scoped permission travels with agent" 모델 검증 두 번째 사례 (CFP-36 PMOAgent retro 이전 다음).

### Migration (BREAKING)
- consumer install: `/plugins install codeforge-requirements@mclayer`
- 기존 docs/domain-knowledge/* 그대로 유지 (codeforge-requirements 의 DomainAgent 가 동일 path 직접 write)
- codex CLI 의존성: codeforge-requirements 측 SessionStart hook 이 검증 (codeforge wrapper 측 부담 해소)

### Followups (CFP-38+)
- CFP-38: codeforge-test (TestAgent 단독 — 가장 단순)
- CFP-39: codeforge-develop (5 agent + presets)
- CFP-40: codeforge-design (7 agent + change-plan/adr templates — 가장 큰 표면, last per Codex)

## [1.0.0] - 2026-04-29

### CFP-36 (ζ arc) — codeforge-pmo plugin extraction (BREAKING)

ζ arc 두 번째 lane plugin 추출 (parent §5.6). PMOAgent + retro template + retros owner write 를 별도 plugin `codeforge-pmo` 으로 이전. wrapper agent 수 감소 (writer-distributed 모델 본격 진행).

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.6.

### Removed (BREAKING for consumer)
- `agents/PMOAgent.md` — codeforge-pmo plugin 으로 이전
- `templates/retro.md` — codeforge-pmo plugin 으로 이전

### Changed
- `CLAUDE.md` 필수 플러그인 5종 → 6종 (`codeforge-pmo@mclayer` 추가). codeforge-review 항목 v1.0.0 retrofit 사실 반영
- `scripts/check-write-permission-redistribution.sh` — PMOAgent.md 부재 시 skip (extraction 후 wrapper 영역 외 invariant)
- `.claude-plugin/plugin.json` v0.22.0 → v1.0.0 BREAKING (consumer 신규 plugin install 의무)

### Why
ζ arc 로드맵 §5.6: PMOAgent 가 가장 작은 lane (1 agent) + 가장 약한 결합 (Cross-cutting, lane gate 무관) → writer-distributed 패턴의 두 번째 검증 단계로 적합. CFP-35 review v2 retrofit (코드 이동 0) 검증 후 코드 이전 첫 사례.

거부된 대안: PMOAgent를 wrapper 잔류 (overlay 충분 — Codex round 2 표면적 권고이지만 wrapper-only end-state 와 충돌), retro template 도 wrapper 잔류 (cross-plugin schema 인지 lane-owned 인지 모호 — codeforge-pmo 단일 owner 가 명료).

### Migration (BREAKING)
- consumer 측 install 추가 필수: `/plugins install codeforge-pmo@mclayer`
- 기존 docs/retros/* 그대로 유지 (codeforge-pmo의 PMOAgent 가 동일 path 직접 write — schema 변화 없음)
- CFP-26 Phase 0a single-owner write 모델 유지 (단 owner 가 wrapper 의 PMOAgent → codeforge-pmo 의 PMOAgent 로 이동)

### Validation
- 5 신규 lint 모두 PASS (PMOAgent.md 삭제 후에도 invariant 통과 — CFP-26 invariant 가 부재 시 skip 처리)
- codeforge-pmo plugin v0.1.0 정상 install 가능 (자체 SessionStart hook + regen-agents.sh)
- marketplace sync 동시 진행 (codeforge v1.0.0 + codeforge-pmo v0.1.0 신규 등록)

### Followups (CFP-37+)
- CFP-37: codeforge-requirements (RequirementsPL + Domain + Analyst + Researcher 추출)
- CFP-38: codeforge-test (TestAgent 추출)
- CFP-39: codeforge-develop (DeveloperPL + role:dev 추출)
- CFP-40: codeforge-design (가장 마지막 — 가장 큰 표면)

## [0.22.0] - 2026-04-29

### CFP-35 (ζ arc) — review_verdict v2 retrofit (Non-BREAKING for wrapper · BREAKING for codeforge-review)

ζ arc 첫 lane plugin self-write 검증 단계 (parent spec §5.5). codeforge-review v1.0.0 BREAKING + codeforge wrapper sibling sync.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.5. Codex round 2 sequencing 권고 (review v2 retrofit이 코드 이동 0의 첫 self-write 검증으로 적합).

### Added
- `docs/inter-plugin-contracts/review-verdict-v2.md` — sibling reference (canonical은 mclayer/plugin-codeforge-review repo)

### Changed
- `docs/inter-plugin-contracts/review-verdict-v1.md` status: Active → Deprecated. 본문 상단 deprecation 안내 추가 (6 CFP 무사고 후 archive 예정)
- `.claude-plugin/plugin.json` version 0.21.0 → 0.22.0

### Why
codeforge-review v1.0.0 BREAKING (Self-write 도입) 시 wire compatibility 위해 wrapper 도 동시 bump. wrapper 자체 코드 변경 없음 (Orchestrator는 verdict status·findings만 소비, write 책임은 codeforge-review로 이전).

거부된 대안: v1 + v2 동시 지원 (write 책임 분기 → DocsAgent 절반만 해체 = ζ arc 모호. v1 deprecate가 명료), wrapper BREAKING bump (실제 wrapper API/runtime 변화 없음 — minor 가 정확).

### Migration
**Non-BREAKING for wrapper consumer** — wrapper 자체 동작 변화 없음. 단 codeforge-review v1.0.0 동시 install 의무 (CFP-29 BREAKING 정책 동일).

- consumer: `gh plugins update codeforge-review` 후 `gh plugins update codeforge` (또는 동시 install)
- v1 contract reference (codeforge core CLAUDE.md "Inter-plugin Contract" 섹션) — Deprecated 표기 후 본문 변경 없음 (audit 보존)

### Validation
- All 10 lint scripts PASS (review-verdict-v2.md 신설로 inter-plugin-contracts 2 contract 검증)
- 1-2 dogfood Story (다음 real Story)에서 codeforge-review v1.0.0 self-write 정상 동작 확인 — 본 PR scope 외

### Followups (CFP-36+)
- CFP-36: codeforge-pmo 신설 (PMOAgent 이전 + retro template + pmo writer + pmo-output-v1 contract). v2 self-write 패턴 두 번째 검증

## [0.21.0] - 2026-04-29

### CFP-34 (ζ arc F3) — Workflow yaml syntax tests + marketplace sync drift detection (Non-BREAKING)

ζ arc 세번째 foundation step. 3 핵심 workflow yaml 의 regex 패턴 fixture 검증 + mclayer/marketplace mirrored 필드 drift CI 자동 감지. CFP-35+ lane plugin 추출 진입 전 Codex round 2 5조건 충족 마무리 단계.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.4. Codex round 2 조건 #3(workflow regex CI 사전 lint) + 조건 #4(marketplace 4-plugin 임계점 전 sync 자동화) 직접 대응.

### Added
- `scripts/check-workflow-yaml.sh` — 3 workflow (fix-ledger-sync · subissue-from-impl-manifest · phase-gate-mergeable) yaml syntax + 핵심 regex 패턴 존재 + Python re-impl fixture 검증
- `scripts/check-marketplace-sync.sh` — `.claude-plugin/plugin.json` mirrored 필드 (name/version/description/author) ↔ mclayer/marketplace marketplace.json plugins[name=local] entry 양방향 비교. drift 시 CI fail + sync 안내
- `.github/workflows/contract-lint.yml` — `workflow-yaml` + `marketplace-sync` job 2종 추가

### Changed
- `.claude-plugin/plugin.json` version 0.20.0 → 0.21.0

### Why
CFP-32 (SSOT 도입) + CFP-33 (lint harness)에 이은 ζ arc foundation 마무리. 본 CFP 후 Codex round 2 5조건 모두 충족 → CFP-35 review v2 retrofit 부터 lane plugin 추출 본격 진입 가능.

거부된 대안: marketplace 자동 PR 생성까지 단일 CFP 포함 (cross-repo PAT 설정 + secret 관리 추가 → 본 CFP scope 초과. drift 감지만 우선 도입, 자동 sync PR open 은 token 인프라 후속 CFP), workflow yaml regex 추출 + 직접 실행 (Node.js 설치 + js engine 통합 → 복잡도 대비 가치 낮음).

### Migration
**Non-BREAKING** — 본 CFP는 lint 추가 + version bump 만. consumer 영향 없음.

- 기존 9 lint job 그대로 + 신규 2 lint job (`workflow-yaml`, `marketplace-sync`)
- workflow yaml 변경 시 fixture와 drift 시 lint catch — yaml 의 핵심 regex 보호
- marketplace 동기 의무 자동 enforcement (CFP-24 정책 manual → automated)

### Validation
- 5 신규 lint 모두 정상 상태 PASS (workflow-yaml 3 fixture, marketplace-sync 양방향 비교)
- 기존 8 lint 회기 없음
- 의도적 yaml regex break 도입 → fixture fail 검증
- 의도적 plugin.json mirrored 필드 변경 (sync 누락) → CI fail 검증

### Followups (CFP-35+)
- CFP-35: codeforge-review v2 retrofit (review-verdict-v2 신설, 첫 lane self-write 검증)
- 향후 (별도): marketplace sync 자동 PR 생성 (cross-repo PAT secret 인프라 + auto-PR workflow)
- 본 CFP 머지 직후: mclayer/marketplace 에 codeforge entry sync (v0.18.0 stale → v0.21.0)

## [0.20.0] - 2026-04-29

### CFP-33 (ζ arc F2) — Contract Lint Harness (Non-BREAKING)

ζ arc 두번째 foundation step. Inter-plugin contract + cross-system registry 검증을 자동화하는 lint harness 3종 신설. CFP-32에서 도입한 invariant SSOT 3종을 CI에서 일관 강제 + 기존 review-verdict-v1.md frontmatter 백필로 legacy allowlist 제거.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.3. Codex round 2 조건 #2 후속(machine-readable shared contract) + 조건 #3(workflow regex 사전 lint).

### Added
- `scripts/check-inter-plugin-contracts.sh` — `kind: contract` 파일 frontmatter (kind, contract_version, status, related_plugins, related_adrs, authors) + 본문 sanity (≥3 ## 섹션) 검증
- `scripts/check-comment-prefix.sh` — `comment-prefix-registry-v1.md` ## 3. 항목 yaml self-validation (11 prefix · 필수 field · auto_mirror bool · 중복 검출)
- `scripts/check-label-registry.sh` — `label-registry-v1.md` ↔ `bootstrap-labels.sh --dry-run` 양방향 sync (name set + color drift + single_active invariant)
- `.github/workflows/contract-lint.yml` — 위 3 lint job CI 통합

### Changed
- `docs/inter-plugin-contracts/review-verdict-v1.md` — frontmatter 백필 (kind: contract, contract_version: 1.0, status: Active, related_plugins, related_adrs, authors)
- `scripts/bootstrap-labels.sh` — `--dry-run` 플래그 추가 (gh 미호출, name|color|desc tab-separated stdout 출력 → check-label-registry.sh 가 parse)
- `scripts/check-doc-frontmatter.sh` — kind:contract dispatch (kind:registry 만 본 lint 적용, kind:contract 는 check-inter-plugin-contracts.sh 가 별도)
- `scripts/check-doc-section-schema.sh` — 동일 dispatch
- `.claude-plugin/plugin.json` version 0.19.0 → 0.20.0

### Why
CFP-32 가 SSOT를 도입했지만 CI 강제는 일부만 (frontmatter + section 만). CFP-33 은 내용물(`## 3. 항목`) 자체 + script ↔ registry sync 까지 자동 검증. CFP-35 review v2 retrofit 진입 전 contract 변경 안전성 보장.

거부된 대안: 모든 lint 를 `check-doc-frontmatter.sh` 안에 inline (단일 스크립트가 너무 많은 역할), `bootstrap-labels.sh` 자체를 registry 에서 자동 생성 (CFP-33 scope 초과 — 이전은 후속 CFP).

### Migration
**Non-BREAKING** — 본 CFP는 추가 lint 만. consumer 영향 없음. 기존 동작 변화 없음.

- review-verdict-v1.md 의 frontmatter 백필은 narrative 영향 없음 (본문 그대로)
- bootstrap-labels.sh 정상 호출 시 동작 동일 (--dry-run 추가만)
- consumer overlay 영향 없음

### Validation
- 3 신규 lint 모두 정상 상태 PASS (review-verdict-v1.md 1건 contract 검증, registry 11+20 entry sync)
- 의도적 break (frontmatter 누락 / yaml schema mismatch / bootstrap-labels.sh 라벨 추가 누락) 시 CI fail 검증
- 기존 5 lint (frontmatter / section-schema / write-permission / no-atlassian / doc-links) 회기 없음

### Followups (CFP-34+)
- CFP-34: workflow yaml syntax test + marketplace sync auto + story-section-write-guard.yml
- CFP-35: codeforge-review v2 retrofit (review-verdict-v2 신설 + v1 deprecate)

## [0.19.0] - 2026-04-29

### CFP-32 (ζ arc F1) — Foundation: Invariant SSOT 3종 + §10 Orchestrator 단독 owner (Non-BREAKING)

ζ arc 첫 foundation step. 3 invariant SSOT(`comment-prefix-registry-v1` · `label-registry-v1` · `fix-event-v1`)을 `docs/inter-plugin-contracts/`에 신설하고 lint로 강제. §10 FIX Ledger 갱신 권한을 DocsAgent → Orchestrator 단독으로 이관. 후속 CFP-35~40 lane plugin 추출의 contract surface 준비 완료.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.2. Codex round 2 조건 #2(machine-readable shared contract 사전 구축) 직접 대응.

### Added
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` — 11종 phase prefix machine-readable SSOT (kind: registry)
- `docs/inter-plugin-contracts/label-registry-v1.md` — 20종 GitHub label machine-readable SSOT
- `docs/inter-plugin-contracts/fix-event-v1.md` — §10 FIX Ledger row schema + append 규칙 + RESET 시맨틱스
- `docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md` — 본 implementation plan

### Changed
- `scripts/check-doc-frontmatter.sh` — `docs/inter-plugin-contracts/**` path 규칙 추가 (필수: kind/registry/version/status/authors). `review-verdict-v1.md` legacy allowlist
- `scripts/check-doc-section-schema.sh` — `docs/inter-plugin-contracts/**` 본문 섹션 규칙 추가 (## 1-4. 목적/Schema/항목/변경 규칙). 같은 legacy allowlist
- `docs/orchestrator-playbook.md` §6.4 — DocsAgent → Orchestrator §10 단독 갱신자 이관 명시 + 3 SSOT cross-ref. §6.6 parallel diagnosis narrative 정정 (DeveloperPL typed return)
- `agents/DocsAgent.md` — ζ arc 단계적 해체 진행 표시 + §10 권한 회수 + 11 phase prefix narrative → registry SSOT cross-ref
- `.claude-plugin/plugin.json` version 0.18.0 → 0.19.0

### Why
ζ arc parent spec(CFP-31)이 정의한 9 CFP 로드맵의 첫 단계. Codex round 2 명시: lane plugin 추출 시작 전 phase prefix · label · FIX event 필드 contract를 machine-readable로 fix해야 split-brain 위험 회피. 본 CFP는 "추출"이 아닌 "추출 전 invariant 동결" — 추출 자체는 CFP-35부터.

거부된 대안: F1+F2+F3 압축 1 CFP (Codex 명시 거부 — 검증 신호 분리 불가), F1을 review-verdict-v1.md 백필 포함 확장 (scope creep — CFP-33 contract harness 영역).

### Migration
**Non-BREAKING** — 본 CFP는 schema 도입 + 권한 narrative 갱신만. 기존 Story file·GitHub Issue·CI Action 동작 변화 없음.

- consumer overlay 영향 없음
- agent permission frontmatter 변화 없음 (DocsAgent narrative만 갱신)
- §10 갱신 주체가 Orchestrator로 명시되었으나 실제 mechanics는 동일 (Orchestrator → DocsAgent 의뢰 → §10 Edit이 → Orchestrator 직접 Edit으로 변경 — Orchestrator는 top-level 세션이라 path-scoped 권한 무관)

### Validation
- `scripts/check-doc-frontmatter.sh` (strict) — 5 owner path 통과
- `scripts/check-doc-section-schema.sh` (strict) — 5 owner path 통과
- `scripts/check-doc-links.sh` — 신규 cross-ref 무결
- `scripts/check-agent-frontmatter.sh` — DocsAgent 변경분 통과
- 1-2 dogfood Story (CFP-33 또는 다음 real Story)에서 Orchestrator §10 직접 Edit 동작 확인 (본 CFP scope 외 — 다음 PR 검증)

### Followups (CFP-33+)
- CFP-33: contract lint harness 신설 — `docs/inter-plugin-contracts/**` 의 cross-contract 의존성 + example 유효성 검증. `review-verdict-v1.md` frontmatter 백필 (allowlist 제거)
- CFP-34: workflow yaml syntax test + marketplace sync auto + `story-section-write-guard.yml`
- CFP-35: codeforge-review v2 retrofit (verdict 반환 → self-write)

## [0.18.0] - 2026-04-28

### CFP-28 — Phase 0c · Lint strict 전환 + retro frontmatter backfill (Non-BREAKING)

CFP-27 Phase 0b에서 도입된 4 owner doc path schema lint(`scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh`) 을 warning 모드 → strict 모드 전환. retro 3 file frontmatter backfill + 회고 §1 regex 완화 + legacy change-plan allowlist 도입.

설계 SSOT: [`docs/stories/CFP-28.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-28.md) (plugin-meta-na 1-PR 패턴, ADR-005). Phase 0a (CFP-26) → Phase 0b (CFP-27) → 본 Phase 0c (CFP-28) 의 staged ε path 마지막 단계.

### Changed
- `scripts/check-doc-frontmatter.sh` — strict 전환 (`exit 0` → `sys.exit(1)` on warns), 헤더 주석 갱신
- `scripts/check-doc-section-schema.sh` — strict 전환 + 회고 §1 regex 완화 (`^## §1 결과` → `^## §1\s+\S` — 회고 종류별 §1 명칭 자유) + legacy change-plan allowlist (CFP-1 ~ CFP-18 중 docs/change-plans/ 존재분 16건 면제)
- `.github/workflows/lint.yml` — `doc-frontmatter` / `doc-section-schema` job name `(CFP-27 — warning)` → `(CFP-28 — strict)`
- `.claude-plugin/plugin.json` version 0.17.0 → 0.18.0

### Added
- `docs/retros/2026-04-27-v0.11.0-sprint-close.md` frontmatter (title/date/sprint_period/cfp_keys/authors/related_stories/sentinel_refs)
- `docs/retros/2026-04-28-codex-audit-closure-sprint.md` frontmatter
- `docs/retros/2026-04-28-marketplace-bootstrap-sprint.md` frontmatter
- `docs/stories/CFP-28.md` — Story file
- `docs/migration-guide.md` `## v0.17 → v0.18` 섹션 (Non-BREAKING 안내)

### Why
CFP-27 도입 시점에 명시적으로 "CFP-28 strict 전환" 약속. drift 위험을 silent에서 PR 차단으로 격상. legacy 16 change-plan은 backfill 비용 회피하고 신규 작성에 대해서만 strict 적용 (CFP-19+ 부터 docs/superpowers/{specs,plans}/* 패턴 전환으로 docs/change-plans/ 디렉토리는 사실상 freeze — 미래 backfill 부담 없음).

거부된 대안: legacy 16 change-plan 전부 backfill (busywork, 결정은 commit 이력 + ADR에 이미 보존), 별도 디렉토리 이동 (URL/링크 영향, 보존 가치 낮음), schema 자체 폐기 (consumer 프로젝트 규약은 유지 필요).

### Migration
**Non-BREAKING for plugin runtime — schema 위반 시 lint.yml CI에서 PR 차단**:

- 신규 `docs/{change-plans,adr,domain-knowledge,retros}/**` 작성 시 [`templates/<doc-type>.md`](templates/) frontmatter + 본문 섹션 schema 준수 필수
- 회고 §1 명칭 자유 — 첫 메이저 섹션이 `## §1 ...`로 시작하면 통과
- pre-CFP-27 legacy change-plan(`cfp-1` ~ `cfp-18`)은 자동 면제 — 추가 작업 불필요
- consumer overlay (`.claude/_overlay/**`) 영향 없음

상세는 [`docs/migration-guide.md`](docs/migration-guide.md) `## v0.17 → v0.18` 섹션 참조.

## [0.17.0] - 2026-04-28

### CFP-29 — Phase 1 · codeforge-review plugin 추출 (BREAKING — staged ε strategic payoff)

**BREAKING (v1.0 이전 minor 표기)**. 5 review agent (Design/Code/SecurityTest PL + Claude/Codex worker) + `templates/review-pl-base.md` + 3 lane checklist을 별도 plugin [`codeforge-review`](https://github.com/mclayer/plugin-codeforge-review) v0.1.0 으로 추출. Inter-plugin Contract `review_verdict v1` 동결.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md) (CFP-29 — 본 구현 Story, parent CFP-25 staged ε design).

### Removed
- `agents/DesignReviewPLAgent.md` (codeforge-review로 이동)
- `agents/CodeReviewPLAgent.md` (이동)
- `agents/SecurityTestPLAgent.md` (이동)
- `agents/ClaudeReviewAgent.md` (이동)
- `agents/CodexReviewAgent.md` (이동)
- `templates/review-pl-base.md` (이동)
- `templates/review-checklists/{design,code,security}.md` (이동)
- `templates/review-checklists/` 디렉토리 (자동 정리)

### Added
- `docs/inter-plugin-contracts/review-verdict-v1.md` — review_packet (core → review) + review_verdict (review → core) v1 contract 상세 schema
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md` — SemVer-style versioning 룰 (v1.x compat / v2.0 BREAKING)
- `CLAUDE.md` "## Inter-plugin Contract" 신규 섹션 — review_verdict v1 요약 + 향후 plugin 추출 시 동일 패턴 안내
- 필수 플러그인 목록에 `codeforge-review@mclayer` (4종 → 5종)

### Changed
- `.claude-plugin/plugin.json` version 0.16.0 → 0.17.0 + description 갱신 (24 → 19 + codeforge-review 추출 명시)
- `CLAUDE.md` 9 곳: agent count 24 → 19, ASCII 다이어그램의 review 5 agent에 `[codeforge-review]` marker, 리뷰 워커 통합 paragraph + Never-skippable + 판정 SSOT 등 cross-ref 갱신
- `docs/orchestrator-playbook.md` 5 곳: frontmatter related_files / 첫 paragraph / review-pl-base path 참조 / 에이전트 표 / dry-run 예시
- `docs/plugin-design.md` 5 곳: §1 §2a §5 §6 헤딩 + Group A 분류 (codeforge core vs codeforge-review plugin 분리)

### Why
CFP-25 ([staged ε design — Claude Opus 4.7 + Codex GPT-5.4 4 라운드 협업](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md))의 strategic payoff. CFP-21 (DataMigrationArchitectAgent 6th deputy 추가)이 9+ file 동시 갱신 + BREAKING bump을 일으킨 사례에서 monolithic plugin의 revision 비용 高를 진단. Phase 0a (CFP-26 DocsAgent scope 축소) + Phase 0b (CFP-27 lint 강화) 가 inter-plugin extraction의 prerequisite 정착 — Phase 1이 이 구조 위에서 review subsystem 분리 실현. ADR-001 lane-agnostic worker 통합 결정을 plugin 경계로 보존.

거부된 대안: soft transition (deprecation 기간 — drift 위험), subdirectory plugin (단일 repo 2 plugin — marketplace 단위와 mismatch), dual install (두 곳에 같은 agent — overlay merge 우선순위 모호), manifest dependency field (Claude Code schema 부재).

### Migration
**BREAKING — consumer 영향**:

기존 codeforge consumer는 다음과 같이 두 plugin 모두 등록 의무:

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-review@mclayer": true   // 추가
  }
}
```

또는 CLI: `/plugins install codeforge-review@mclayer`.

codeforge-review의 SessionStart hook이 codeforge core 설치 여부 verify — codeforge만 설치하고 review 미설치 시 review lane 진입 시 fail-fast + install 안내. codeforge core의 SessionStart hook도 codeforge-review 설치 여부 감지해 안내.

자세한 사항: `docs/migration-guide.md` v0.16 → v0.17 섹션 참조.

## [0.16.0] - 2026-04-28

### CFP-27 — Phase 0b · Lint 강화 + CI Integration

**Non-BREAKING** — 신규 lint 2종 (doc-frontmatter / doc-section-schema)은 **warning 모드** 시작. 기존 docs 파일 fail 없음. CFP-28 dogfood 검증 통과 후 strict 전환 예정.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 — 설계 spec, CFP-27 — 본 구현 Story).

### Added
- `templates/domain-knowledge.md` — DomainAgent owner doc schema SSOT (CFP-26 Phase 0a부터 owner direct write이나 schema 부재였음)
- `templates/retro.md` — PMOAgent owner doc schema SSOT (동일)
- `scripts/check-doc-frontmatter.sh` — 4 owner doc path frontmatter 필수 필드 검증 (warning 모드)
- `scripts/check-doc-section-schema.sh` — 4 owner doc path 본문 필수 섹션 헤딩 검증 (warning 모드)
- `.github/workflows/lint.yml` 3 신규 job: `write-permission-redistribution` (strict, CFP-26 invariant CI 통합) + `doc-frontmatter` + `doc-section-schema` (warning 모드)

### Changed
- `scripts/check-write-permission-redistribution.sh` — `allow_block` / `deny_block` 두 함수를 단일 `extract_block(file, key)` 파라미터화 (CFP-26 code review minor follow-up)
- `CLAUDE.md` "## ADR" + "## Domain Knowledge" + "## docs/stories markdown 규약" 섹션 — CFP-27 lint enforcement 안내 추가

### Why
CFP-26 Phase 0a가 4 owner agent direct write를 도입했으나 **schema enforcement는 manual convention**에 그침. CFP-27이 schema를 lint로 자동 강제 시작 (warning 모드 → CFP-28 dogfood → CFP-28+ strict). 또한 부재했던 owner doc 템플릿 2건(domain-knowledge / retro) 신설로 SSOT 완결성 회복.

추가로 CFP-26에서 식별된 follow-up 2건 처리: redistribution lint CI integration (이전 manual call only) + awk 코드 정리.

### Migration
**Non-BREAKING — consumer 영향 미미**:
- 신규 lint 2종은 warning 모드라 기존 consumer docs 파일 호환
- consumer가 `templates/domain-knowledge.md` / `templates/retro.md` 를 schema source로 사용 가능 — 강제 아님 (CFP-28에서 strict 전환 시 backfill 필요)
- CI workflow 6 jobs 운영 — consumer가 `.github/workflows/lint.yml` 복사한 경우 새 job 3개 동기화 권장

자세한 사항: `docs/migration-guide.md` v0.15 → v0.16 섹션 참조.

## [0.15.0] - 2026-04-28

### CFP-26 — Phase 0a · Single-owner write 권한 재분배 (BREAKING — DocsAgent scope 축소)

**BREAKING (v1.0 이전 minor 표기)**. DocsAgent 단독 writer 모델을 "DocsAgent + 3 owner agent 분담"으로 변경.
4 single-owner 문서 경로(`docs/{change-plans,adr,domain-knowledge,retros}/**`)가 owner agent direct write로 이관.
DocsAgent는 Story file (multi-writer 직렬화) + GitHub Issue/PR/comment·label·body·milestone 책임 유지.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 — 설계 spec, CFP-26 — 본 구현 Story).

### Changed
- `agents/ArchitectAgent.md` frontmatter — `docs/change-plans/**` + `docs/adr/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/DomainAgent.md` frontmatter — `docs/domain-knowledge/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/PMOAgent.md` frontmatter — `docs/retros/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/DocsAgent.md` frontmatter — 4 owner-path deny 추가, "소유 영역" 표 갱신 (취소선으로 이관 audit trail 보존)
- `CLAUDE.md` "Write 권한 (path-scoped)" + "문서 write 책임 분담" 섹션 (이전 "단독 writer 원칙") 갱신
- `docs/orchestrator-playbook.md` §5.1 + §5.2 + §11.2/§11.4 + §13.4 — 단계 종료 시 DocsAgent 스폰 체크리스트의 4 single-owner trigger를 owner direct로 변경, write queue type enum에서 4 deprecated type 제거

### Added
- `scripts/check-write-permission-redistribution.sh` — Phase 0a invariant lint (4 owner-path direct write + DocsAgent deny 16 assertion)

### Why
CFP-21 (DataMigrationArchitectAgent — 6th deputy) 추가가 9+ 파일 동시 갱신 + BREAKING bump을 일으킨 사례에서, codeforge 본체 revision 비용이 monolithic single-writer 모델 때문에 과도하게 상승함이 명확. DocsAgent의 funnel 가치(multi-writer 직렬화·GitHub lifecycle 일관성·comment phase prefix)는 보존하되, single-author 산출물은 owner agent direct write로 이관해 funnel 부담을 줄이고, 향후 plugin 추출(CFP-29 codeforge-review)의 cross-plugin 결합점을 narrow하게 한다.

설계 협업: Claude Opus 4.7 + Codex GPT-5.4 (4 라운드, 라운드 4에서 Path A 합의). 거부된 대안: Path B (DocsAgent 완전 제거 — multi-writer 직렬화 깨짐), Path C (skill 다운그레이드 — knowledge 보존하지만 enforcement 잃음).

### Migration
**BREAKING — consumer 영향**:
- consumer overlay에서 ArchitectAgent · DomainAgent · PMOAgent 권한을 추가로 확장하던 경우, frontmatter `permissions.allow` 항목이 **core와 concat+dedup** 되므로 변경 없음 (overlay 메커니즘이 새 항목 자동 흡수)
- consumer overlay가 DocsAgent 권한을 명시 override 하던 경우(드뭄), `docs/{change-plans,adr,domain-knowledge,retros}/**` 4 path deny가 추가됨에 유의 — overlay에서 다시 allow를 명시하면 path-scoped allow가 우선
- 자동화: `scripts/check-write-permission-redistribution.sh`가 invariant 강제. CI에서 호출 권장

자세한 사항: 본 spec (CFP-25) §1·§5 참조.

## [0.14.3] - 2026-04-28

### CFP-24 — Marketplace cross-repo 동기화 의무 정식 잠금

**Non-BREAKING**. 사용자 명시 규칙을 CLAUDE.md에 SSOT로 명문화. plugin.json의 mirrored 필드(`name` · `version` · `description` · `author`) 변경 시 `mclayer/marketplace`의 marketplace.json `plugins[name=codeforge]` 동일 필드도 같은 Story 범위 내 sync PR 의무.

### Added
- CLAUDE.md `## Plugin` 섹션 하위 `### Marketplace cross-repo 동기화 의무` 신규 — mirrored 필드 정의 + 의무 절차 + 면제 조건 + 향후 자동화 후보

### Why
CFP-23(2026-04-28)에서 `mclayer/marketplace` 단일 진입점 노출 시작. 두 리포가 plugin.json·marketplace.json 양쪽에 같은 필드를 가져 drift surface 신규 발생. 사용자 입장에서 단일 좌표(`codeforge@mclayer`)로 보이는데 실제는 두 리포 분리 → drift 시 stale version 또는 어긋난 description 노출. 본 규칙으로 author·Orchestrator 의무화. 자동화는 cross-repo parity CI 후속 CFP에서 처리.

### Migration
Non-BREAKING — 기존 사용자 영향 없음. 향후 codeforge plugin.json 변경 PR 작성 시 mirrored 필드 점검 + marketplace sync PR 후속 의무가 author/Orchestrator 절차에 추가됨.

자세한 사항: CLAUDE.md `Marketplace cross-repo 동기화 의무` 섹션 참조.

## [0.14.2] - 2026-04-28

### CFP-23 — `mclayer` marketplace 노출

**Non-BREAKING**. 본 플러그인이 [`mclayer/marketplace`](https://github.com/mclayer/marketplace) 단일 진입점으로 노출됨. 사용자는 `/plugins install codeforge@mclayer`로 설치 가능. 기존 GitHub 좌표 직접 등록 사용자에 영향 없음.

### Added
- README.md `설치 · 사용` 섹션: `mclayer` marketplace 등록 명령 + `~/.claude/settings.json` 영구 등록 예시

### Why
v0.14.1까지 marketplace 노출 부재 — 사용자가 GitHub 원본 좌표를 직접 등록해야 했음. `mclayer/marketplace` 별도 wrapper 리포 신설(2026-04-28)로 단일 진입점 확보. 향후 `mclayer/plugin-<X>` 시리즈 추가 시에도 동일 marketplace에서 일괄 설치 가능.

### Migration
Non-BREAKING — 기존 사용자(직접 GitHub 좌표 등록)는 그대로 유지 가능. 신규/이주 권장 경로:

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": { "codeforge@mclayer": true }
}
```

자세한 사항: `mclayer/marketplace` README 참조.

## [0.14.1] - 2026-04-28

### CFP-22 — DesignReview checklist 확장 (Codex audit #4·#5·#6)

**Non-BREAKING**. ADR-004 §"후속 조치" #4·#5·#6 직접 적용. 새 deputy 없음, 새 §섹션 없음 — 기존 design.md에 3 audit 섹션만 추가.

### Added
- design.md: §4 API 호환 감사 (Codex #5)
- design.md: §3·§4 관측성 감사 (Codex #4)
- design.md: §3 SLO 감사 (Codex #6)
- lane=design category enum: api-compatibility / observability / slo-missing (3개 추가, 8 → 11)
- DesignReviewPL severity_overrides: P0 3건 추가 (조건부 — 공개 API·SLA·boundary만)
- CodexReviewAgent lane=design prompt: auto-P0 3건 추가

### Why
Codex audit #4 (관측성) / #5 (API 호환) / #6 (SLO) 모두 설계 시점 누락 위험 — 운영 단계에서 발견 시 비싼 회귀. shift-left 정합성 (ADR-004 / ADR-006 / ADR-007 동일 trade-off, 단 새 deputy 불필요).

### Migration
Non-BREAKING — 기존 Story 진행 중인 경우 새 audit 룰은 다음 DesignReview 진입 시 자동 적용. P0 룰은 조건부 (공개 API·SLA·boundary 컴포넌트만) — 내부 도구·docs-only는 P1 또는 N/A 사유 1줄로 처리.

자세한 사항: [docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-cfp-22-design-checklist-expansion.md)

## [0.14.0] - 2026-04-28 (BREAKING)

### CFP-21 — DataMigrationArchitectAgent (Codex audit #2)

**BREAKING**. ADR-004 §"후속 조치" #2 직접 적용. ADR-006 (TestContractArch precedent) 패턴 그대로 차용 — shift-left 데이터 무결성 advocate. 본 plugin은 자기 적용 안 함 (paradox 처리, ADR-005 plugin-meta-na).

### Added
- `agents/DataMigrationArchitectAgent.md` (신설, 6번째 deputy)
- ADR-007 (Accepted) — DataMigrationArchitectAgent 도입 결정
- `templates/change-plan.md` §11 데이터 마이그레이션 (§11.1 Schema 영향 / §11.2 Migration 전략 / §11.3 Rollback 경로 / §11.4 Data integrity invariant / §11.5 Backfill / §11.6 N/A)
- `templates/review-checklists/design.md` §11 audit 절 + 3 P0 차단 룰 (누락 / N/A 사유 부재 / DataMigrationArch 매핑 미반영)
- lane=design category enum: `data-migration` (7 → 8 카테고리)

### Changed
- agent count: 23 → 24
- ArchitectPLAgent: deputy 4 → 5 (Phase 1.5 sanity check 1 항목 + 메타-규칙 1번 §11 매핑 1행 추가)
- ArchitectAgent: deputy 5인 산출물 통합 + Change Plan §1-§10 → §1-§11 + §11 author input 절차
- 4 deputy md (Mapper / Refactor / SecurityArch / TestContractArch): cross-ref 1줄 (DataMigrationArch §11 author input + 4-way 대립 참여)
- CLAUDE.md: 24 core, 다이어그램, Never-skippable, 책임 매트릭스 6행 (§11 5 항목 + 누락/N/A 1행), FIX decision table 1행 추가, 3-way → 4-way 대립 재명명, ArchitectAgent 재스폰 §1-§11
- orchestrator-playbook.md: 24 core, deputy 5인 일괄, 토큰 budget 175k → 200k peak, §3.1 스폰 시퀀스, §3.2 PL 표 DataMigrationArch 행, §14 progress dashboard 5/5 deputies

### Migration
- BREAKING: agent count 23 → 24 (DataMigrationArchitectAgent 추가)
- BREAKING: Change Plan template §1-§10 → §1-§11 (신규 §11 데이터 마이그레이션)
- BREAKING: DesignReview checklist §11 누락 차단 룰 추가
- Consumer 액션: 진행 중 Story (phase: 설계 / 설계 리뷰)는 §11 추가 후 ArchitectPLAgent 검수 재실행. Plugin meta / docs-only / pure UI Story는 §11.6 N/A 사유 1줄 명시
- 자세한 사항: [docs/migration-guide.md](docs/migration-guide.md) v0.13.0 → v0.14.0 절

## [0.13.0] - 2026-04-28

### CFP-19 — 오케스트레이션 병렬화 (R1-R11 Tier 1+2)

**Non-BREAKING**. 사용자 critical feedback ("전체적으로 너무 느리다") 대응. Codex(GPT-5) + general-purpose 두 독립 감사 합의 11개 직렬 병목 제거. 본 plugin은 자기 적용 안 함 (paradox 처리, ADR-005 plugin-meta-na).

**Tier 1 (R1-R8)**:
- R1: DocsAgent dual-mode (blocking/background) write queue drain — `mode` 필드 필수, blocking 7종 / background 4종 분류
- R2: ReviewPL verdict-return-first protocol — DocsAgent save 대기 안 함, 다음 lane spawn 트리거 후 background drain
- R3: Orchestrator-direct dual review worker spawn — PL이 packet return → Orchestrator 한 메시지에 (Claude ∥ Codex) dispatch
- R4: FIX speculative pipelining — DeveloperPL 1차 진단 ∥ ArchitectPL 최종 판정 병렬, 불일치 시 ArchitectPL 우선
- R5: §8.5 Impl Manifest 자동 생성 — DocsAgent kind=impl-manifest helper, DeveloperPL은 review-edit only
- R6: Lane Context Packet warm cache — `.claude-work/cache/<KEY>-sections.json` git commit hash invalidation
- R7: Phase 1 merge ↔ Phase 2 prep parallel — 설계 리뷰 PASS 즉시 Track A(merge) ∥ Track B(prep) 병렬
- R8: ArchitectPL fail-fast pre-synthesis — Phase 1.5 sanity check, 결격 deputy clarification 재spawn

**Tier 2 (R9-R11)**:
- R9: TestAgent subset 병렬 — `subset: functional` ∥ `subset: performance`
- R10: SecurityTestPL 1차 layer pre-fetch — `.claude-work/cache/<KEY>-sec1.json` background prefetch
- R11: FIX mechanical fast-path — typo/broken-link/minor-naming/comment-only 자격 시 ArchitectPL 판정 skip + §10 row 안 매김

**예상 효과**: Story 1건당 평균 20-32분 단축 (60-90분 → 40-60분 예상, 30-40% reduction).

**변경 파일**: `templates/review-pl-base.md`, `agents/{DocsAgent,ArchitectPLAgent,DeveloperPLAgent,DesignReviewPLAgent,CodeReviewPLAgent,SecurityTestPLAgent,TestAgent}.md`, `docs/orchestrator-playbook.md`, `CLAUDE.md`. ADR 변경 0건.

**Spec/Plan**: [docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md), [docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/plans/2026-04-27-cfp-19-orchestration-parallelization.md).

### Migration
- Non-BREAKING — 모든 변경은 SSOT 문서·agent md·playbook 추가 절. consumer 액션 없음.
- 본 plugin은 자기 적용 안 함 (paradox 처리). 다음 Story부터 발효.

## [0.12.0] - 2026-04-27

### Added
- **TestContractArchitectAgent** 신설 — 설계 lane 5번째 deputy (§8 Test Contract author input contributor, QA perspective)
- **ADR-006** — TestContractArch 도입 결정 기록 (status=Accepted)
- **ArchitectPL 검수 메타-규칙 압축** — 4 항목 enumerate -> 2 항목 메타-규칙 (§섹션별 deputy author input 통합 + §섹션 누락 차단)

### Changed
- **ArchitectAgent**: deputy 3인 -> 4인 (TestContractArch 추가) + §8 Test Contract author 라인 §7 동형 보강
  > Note: "deputy" 카운트는 perspective 차이 — ArchitectAgent peer view = 4 (Mapper/Refactor/SecurityArch/TestContractArch), ArchitectPL chief-inclusive view = 5 (+chief author).
- **ArchitectPLAgent**: deputy 4인 -> 5인 + 검수 4 항목 -> 메타-규칙 2 항목 압축
- **CodebaseMapper / RefactorAgent / SecurityArchitectAgent**: "Mapper/Refactor와의 관계" 절 끝에 "TestContractArch는 §3·§7 도형 대립 비참여" 1줄 cross-reference 추가
- **QADeveloperAgent**: 계약 소유자 라인 보강 ("TestContractArch input 통합 후 §8 확정")
- **CLAUDE.md / orchestrator-playbook.md / plugin-design.md**: 22 core -> 23 core, deputy 4 -> 5 일괄, 검수 메타-규칙 압축 반영
- **ADR-005**: status Proposed -> **Accepted (결정 1·2·3 한정)** — N/A 표기 형식·면제 분류·N/A inheritance 차단. 결정 4 (invariant-check Step 신설)는 follow-up CFP

### Migration
- BREAKING: agent count 22 -> 23 (TestContractArchitectAgent 추가)
- BREAKING: 책임 매트릭스에 TestContractArch perspective 추가 (§8 author input contributor)
- Consumer 액션: 없음 (Orchestrator 경유 호출). SessionStart hook 재실행 권장
- 자세한 사항: [docs/migration-guide.md](docs/migration-guide.md) v0.11.0 -> v0.12.0 절

## [0.11.0] - 2026-04-27

### Added
- **ArchitectPLAgent** 신설 — 설계 레인 PL (supervisor + FIX 루프 최종 판정자)
- **SecurityArchitectAgent** 신설 — 설계 레인 deputy (trust boundary / threat model / auth / data)
- **Change Plan §7 보안 설계** 섹션 신설 (templates/change-plan.md)
- **ADR-004** — 설계 lane 재구조화 결정 기록

### Changed
- **ArchitectAgent** 책임 분리: PL → chief author. FIX 최종 판정·deputy 스폰·Impl Manifest 감사 책임을 ArchitectPLAgent로 이관. 신규 ADR draft 작성 책임 명문화 (Codex #7)
- **CodebaseMapperAgent / RefactorAgent**: 상위 ArchitectAgent → ArchitectPLAgent. 2-way → 3-way 대립 (+ SecurityArch)
- **CLAUDE.md**: 다이어그램·Never-skippable·스폰 시퀀스·책임 매트릭스·FIX decision table·병렬 스폰·Write 권한 모두 갱신
- **DesignReviewPL**: review packet에 §7 보안 설계 차단 룰 추가
- **DeveloperPL**: FIX 1차 진단 → ArchitectPLAgent 최종 판정 (3 lane 갱신)

### Migration
- Consumer 액션 필요 없음 (Orchestrator 경유 호출이라 직접 영향 없음)
- 기존 docs/change-plans/* 회귀 갱신 불필요 (신규 Story부터 §7 적용)
- 자세한 사항: [docs/migration-guide.md](docs/migration-guide.md) v0.10.0 → v0.11.0 절

## [0.10.0] — 2026-04-27 (Self-application 6 layer 완성 — CFP-1~16)

### Architecture
- **Plugin self-application 정합화 sprint** — 16 CFP Story로 6 layer 완성:
  1. **정책** (CFP-1): `story_cutoff` policy + dogfooding rule (CLAUDE.md "Story 작성 의무" 섹션)
  2. **인프라** (CFP-2): GitHub Issue Forms 3종 + 6 workflows + CODEOWNERS + PR template
  3. **메타 정합** (CFP-4): story-init.yml drift sync + CLAUDE.md self-application stage 정정 + plugin.json 메타
  4. **CI invariant** (CFP-5/6/7/8/9/10/13/16): `invariant-check.yml` 8 step (workflow parity / version match / agent count / write queue 권한 / ADR-002 footer / 3-lane category enum / migration-guide BREAKING / severity overrides count+breakdown)
  5. **SessionStart 부트스트랩** (CFP-12): `overlay/hooks/check-bootstrap.sh` (org permission + 18 label 자동 검출, non-blocking) + `scripts/bootstrap-labels.sh` (idempotent 부트스트랩)
  6. **end-to-end 실측** (CFP-11): Issue Form → workflow chain 첫 실증 + 3 drift 발견·정합 회복
- **ADR-003 도입**: SSOT drift 검출·회복 책임을 3 layer로 분리 (CI invariant / SessionStart 부트스트랩 / 사용자 가이드) — 향후 새 drift 검출 추가 시 layer 결정 기준 (Q1-Q3 tree)
- **CFP-15 폴리시**: story-init workflow의 docs h1·PR title에서 `[STORY]` prefix strip (cosmetic 정합)

### Added
- `.github/workflows/invariant-check.yml` (CI level layer)
- `overlay/hooks/check-bootstrap.sh` (SessionStart non-blocking 진단)
- `scripts/bootstrap-labels.sh` (consumer 1회 부트스트랩)
- `docs/adr/ADR-003-three-layer-drift-responsibility.md`
- `docs/stories/CFP-1.md` ~ `CFP-16.md` (15 Story files; CFP-3 deferred)
- `docs/change-plans/cfp-*.md` (대응 Change Plan 14건)

### Changed
- `overlay/hooks/regen-agents.sh` — SessionStart에 `check-bootstrap.sh` 호출 wiring (`|| true` 비차단)
- `overlay/hooks/validate_config.py` — `story_cutoff.additional_exempt_categories` schema + unknown key reject (CFP-1 invariant 영구 보존, CFP-6)
- `.github/workflows/story-init.yml` — sed Korean range bug fix (Python re.UNICODE 교체) + `[STORY]` prefix strip
- `docs/adr/ADR-002-docsagent-inherit-footer-pattern.md` — §3.2 path example 오타 정정
- `docs/consumer-guide.md` — §2d label bootstrap script 자동화 참조 + §2g org permission 부트스트랩 단계 신설
- `CLAUDE.md` — "Story 작성 의무 (모든 변경 적용)" 섹션 추가 (cutoff 정책 + dogfood 단계)
- `docs/project-config-schema.md` — `story_cutoff.additional_exempt_categories` schema 추가

### Migration

v0.9 → v0.10은 **non-BREAKING** (모든 추가는 opt-in 또는 자동 적용). consumer 마이그레이션 절차 없음.

다만 **권장**:
- 신규 invariant-check.yml은 plugin maintainer 전용 — consumer는 복사 불필요
- consumer는 `bash scripts/bootstrap-labels.sh` 1회 실행으로 18 plugin label 일괄 부트스트랩
- consumer-guide §2g 따라 org-level "Workflow permissions" 활성화 (story-init.yml의 PR auto-create 정상 동작 조건)

## [0.9.0] — 2026-04-26 (BREAKING — Review/Test 워커 통합)

### Breaking
- **3 lane × 2 vendor = 6 워커 → 2 워커로 통합** ([ADR-001](docs/adr/ADR-001-review-agent-unification.md)). consumer overlay에 `agents/Claude{Design,Code,SecurityTest}ReviewAgent.md` 또는 `Codex...` 파일이 있다면 마이그레이션 필요
- 24 core agents → **20 core agents** (워커 6 삭제, 워커 2 신규)
- Codex 플러그인 단일 의존성: 미설치 시 3 리뷰 lane 모두 진입 불가 (이전: 각 lane별 개별 차단)

### Architecture
- **워커 통합**: `ClaudeReviewAgent` + `CodexReviewAgent` 2종이 lane=design/code/security 3 lane 공통 처리. 도메인은 호출 PL이 review packet으로 주입 (체크리스트·스코프·category enum·severity 자동 룰)
- **공통 base SSOT**: `templates/review-pl-base.md` — severity 종합·dedup·noise 분류·보고 형식·escalation 절차. 3 PL이 9번 복제하던 표가 1군데로
- **체크리스트 SSOT**: `templates/review-checklists/{design,code,security}.md` — consumer overlay가 도메인 특화 체크 추가 가능
- **Packet 누락 invariant**: 워커는 packet 필수 필드 누락 시 즉시 `ESCALATE_PACKET_INCOMPLETE` 반환 — generic fallback 금지
- 3 PL md 슬림화 (~120줄 → ~60줄): base 템플릿 참조 + lane-specific 4가지(체크리스트 packet·FIX 카운터 정책·검증 스코프·다음 게이트 라벨)만 본문에 명시
- SecurityTestPL에 `Bash(gh api repos/*)` 권한 부여 — 1차 layer (Dependabot/CodeQL/Secret Scanning) 결과 fetch 후 packet inline 첨부
- 레인 명칭·라벨·워크플로우 invariant 그대로 유지 (`phase:보안-테스트`·`gate:security-test-pass`·`fix:보안-테스트-retry`)

### Added
- `docs/adr/ADR-001-review-agent-unification.md` (첫 ADR)
- `templates/review-pl-base.md` (3 PL 공통 base SSOT)
- `templates/review-checklists/design.md` · `code.md` · `security.md`
- `agents/ClaudeReviewAgent.md` · `agents/CodexReviewAgent.md` (lane-agnostic 워커)

### Changed
- `agents/DesignReviewPLAgent.md` · `agents/CodeReviewPLAgent.md` · `agents/SecurityTestPLAgent.md` 슬림화 (base + lane-specific만)
- `CLAUDE.md` (agent tree·never-skippable·write 권한 표·외부 도구 wrapper·Codex 의존성)
- `docs/orchestrator-playbook.md` (스폰 시퀀스 다이어그램·핵심 의무 표·외부 의존성 표·세션 회고 테이블)
- `docs/plugin-design.md` (agent enumeration)
- `agents/DocsAgent.md` (phase prefix 매핑·Codex 보고 기록 형식)

### Removed
- `agents/ClaudeDesignReviewAgent.md`
- `agents/CodexDesignReviewAgent.md`
- `agents/ClaudeCodeReviewAgent.md`
- `agents/CodexCodeReviewAgent.md`
- `agents/ClaudeSecurityTestAgent.md`
- `agents/CodexSecurityTestAgent.md`

### Migration
v0.8 → v0.9 마이그레이션:
1. consumer overlay에 6 워커 오버라이드가 있다면 → `ClaudeReviewAgent.md` / `CodexReviewAgent.md` 1쌍으로 통합 + lane-specific 부분은 `templates/review-checklists/<lane>.md`로 이동
2. SecurityTestPL이 `gh api repos/*` 호출하므로 GitHub 인증 (Dependabot/CodeQL/Secret Scanning alerts read 권한) 확인
3. CHANGELOG 기록·코멘트의 `Codex<Domain>ReviewAgent` 인용은 historical로 유지

## [0.8.0] — 2026-04-26 (BREAKING — Atlassian 제거 + GitHub 전환)

### Breaking
- **Atlassian backend 완전 제거** (Confluence/Jira). consumer는 GitHub-only로만 사용 가능
- `atlassian.*` project.yaml 스키마 → `github.*`로 교체 (org / repo / default_branch / pr_title_prefix_template / story_key_prefix / codeowners / discussions / milestone)
- 24 agents의 atlassian MCP 권한 제거. DocsAgent는 `mcp__github__*` write + gh CLI Bash fallback
- 필수 의존성: MCP `github` (`atlassian` 대체), 플러그인 4종 (`github@claude-plugins-official` 격상), CLI 2종 (`gh` 추가)
- 권장 플러그인 5종 → 4종 (`atlassian@claude-plugins-official` 제거, `github@claude-plugins-official`은 격상)

### Architecture
- **Story 페이지 → `docs/stories/<KEY>.md`** (single-file SSOT, §1-11)
- **ADR → `docs/adr/ADR-NNN-<slug>.md`** (flat, frontmatter `category:`)
- **Domain KB → `docs/domain-knowledge/<area>/<topic>.md`** (계층)
- **Story 1건 = PR 2건** (Phase 1 docs / Phase 2 code+docs append)
- **GitHub Workflow 자동화 6종**: story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync
- **보안 테스트 1차 layer**: Dependabot + CodeQL + Secret Scanning + Push Protection (GitHub native)
- **Phase 라벨 single-active invariant**: phase-label-invariant.yml Action이 강제
- **§1 변조 금지 invariant**: story-section-1-immutable.yml Action이 강제
- **CODEOWNERS**: `docs/adr/**`·`docs/change-plans/**`·`docs/stories/**` → architect team / `docs/domain-knowledge/**` → domain expert team
- **Branch protection**: phase-gate-mergeable required status check + CODEOWNERS review

### Added
- `templates/github-workflows/*.yml` 6개 (Action SSOT)
- `templates/github-issue-forms/*.yml` 3개 (story / bug / audit)
- `templates/github-pr-template.md` (Phase 1 / Phase 2 양식 분리)
- `templates/CODEOWNERS.template`
- `scripts/check-no-atlassian.sh`, `scripts/check-agent-frontmatter.sh`, `scripts/check-doc-links.sh`

### Changed
- `CLAUDE.md` major rewrite (atlassian 제거 + GitHub-native 워크플로우 + 세션 개시 의무 갱신)
- `docs/orchestrator-playbook.md` major rewrite (§1.1 / §3B / §11 / §12 / §12.5 갱신)
- `docs/project-config-schema.md` (atlassian.* 제거, github.* 신설)
- `docs/consumer-guide.md` (GitHub-native 셋업 절차)
- `agents/DocsAgent.md` major rewrite (권한 + GitHub primitive 매핑)
- 23 agents (frontmatter MCP + 본문 prose 일괄 변환)
- `templates/story-page-structure.md`, `adr.md`, `impl-manifest.md`, `change-plan.md`
- `presets/webapp/agents/*` (Jira/Confluence → GitHub Issue/PR)
- `.claude/settings.json`, `.claude/settings.local.json` (atlassian MCP 제거, github MCP + gh CLI 추가)
- `overlay/_overlay/project.yaml.example`, `overlay/_overlay/README.md`, `overlay/hooks/validate_config.py`, `overlay/hooks/tests/test_validate_config.py`
- `examples/*/.claude/_overlay/project.yaml` (3개 fixture)

### Migration
v0.7.x 이하에서 v0.8로 in-place 업그레이드 불가. 기존 consumer는 fresh GitHub-based setup 필요. [migration-guide.md](docs/migration-guide.md#v07--v08-atlassian-제거--github-전환) 참조.

### Affected — 32+ files
- Core: `CLAUDE.md`, `docs/orchestrator-playbook.md`, `docs/project-config-schema.md`, `docs/consumer-guide.md`, `docs/migration-guide.md`, `docs/plugin-design.md`, `docs/README.md`, `README.md`
- Agents: 24 agent .md 전부
- Templates: 4 templates 전부 + 신규 11개 (workflows · forms · CODEOWNERS · PR template)
- Settings: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/_overlay/project.yaml`
- Overlay/Hook: `overlay/_overlay/*`, `overlay/hooks/validate_config.py`
- Scripts: 신규 3개 검증 스크립트
- Examples: 3개 project.yaml fixture
- Presets: webapp agents 2개

## [0.7.1] — 2026-04-24

### Fixed (v0.7.0 병렬 모델 정합성 결함 보정)

- **§2 Story 페이지 섹션 타이밍 drift**: v0.7.0에서 Analyst·Researcher가 §2(DomainAgent 해석)를 입력 참조한다는 서술이 남아있었음. 병렬 모델에서 §2는 Domain 자신의 output destination이며 페이지 생성 시엔 placeholder → Analyst·Researcher 프롬프트에서 §2 참조 제거, templates/story-page-structure.md에 타이밍 주석 추가
- **섹션별 atomic 갱신 규정 누락**: Domain/Analyst/Researcher 결과를 배치로 기록하면 resume 시 부분 완료 감지 불가. DocsAgent가 §2·§5·§6 각각 **atomic 갱신** 의무 명시 (배치 금지)
- **Clarification 재스폰 로그 위치 불명**: §10 FIX Ledger와 구분이 모호 → **§9.0 "Clarification 재스폰 이력"** 섹션 신설, Jira `fix:*` 라벨 미추가 (게이트 실패 아님)
- **DesignReview 감사 항목 표류**: 병렬 모델에서 Mapper·Refactor 상호 대응이 없는데 "Mapper 변호 근거 일축 여부"를 두 에이전트 산출물에 묻는 서술이 남아있었음 → "**Architect 통합 판정**이 Mapper 변호를 근거 있게 일축·수용했는가"로 리프레이밍 (CLAUDE.md, ArchitectAgent, CodebaseMapper, Refactor 4곳)

### Added

- **§8.2 토큰 예산 peak/total 구분** (playbook): 병렬화로 peak concurrent context 증가 반영. 요구사항 peak 3× (~60k), 설계 peak 2× (~50k+Architect). "Peak 접근 시 순차 fallback 검토" 지침
- **§3B.3 Preflight 공통 입력 준비 체크**: 요구사항·설계 레인 진입 전 Orchestrator가 ADR 목록·코드 경로·Project Config Packet·Change Plan 초안 등 공통 입력 패키지 완비 확인 의무
- **§7.3 Resume 부분 완료 매핑**: §2·§5·§6 중 일부만 채워진 상태에서 중단됐을 때 비어있는 섹션의 에이전트만 선택 재스폰 (이미 채워진 섹션 재활용). 설계 레인도 동일 규칙
- **DocsAgent §2·§5·§6 null 결과 템플릿**: "공백 없음"·"추가 해석 불필요"·"외부 지식 보강 불필요" 판정 시 섹션 생략 금지 — 독립 관점 결과 보존을 위해 사유 기록 템플릿 명시

### Affected
- `CLAUDE.md`, `docs/orchestrator-playbook.md`, `templates/story-page-structure.md`
- `agents/DocsAgent.md`, `agents/DomainAgent.md`, `agents/RequirementsAnalystAgent.md`, `agents/ResearcherAgent.md`
- `agents/ArchitectAgent.md`, `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md`

### Migration
- Non-breaking (v0.7.0 semantic 유지, 정합성만 보정)
- Consumer overlay override가 §2를 입력으로 참조하던 경우 제거 필요

## [0.7.0] — 2026-04-24

### Changed
- **BREAKING (오케스트레이션 semantics)**: 요구사항·설계 레인 서브 에이전트 **sequential → parallel** 전환
  - 요구사항 레인: `DomainAgent → Analyst → Researcher` 순차 (조건부 생략 포함) → `DomainAgent ∥ Analyst ∥ Researcher 병렬` (셋 다 non-skippable)
  - 설계 레인: `CodebaseMapper → Refactor` 순차 (Refactor가 Mapper 요약 입력 수신) → `CodebaseMapper ∥ Refactor 병렬` (둘 다 원 소스 직접 독해, 산출물 교차 참조 없음)
  - 이유: 순차 모델에서 후속 에이전트가 선행 결과에 오염되어 **독립 관점** 소실. 병렬 모델에서 PL/Architect가 진정한 synthesizer 역할
- **Clarification 재스폰 프로토콜 신설**: 서브 에이전트는 one-shot 실행이므로 PL↔서브 continuous dialog 불가. PL이 통합 중 추가 질의 필요 시 Orchestrator 경유 재스폰 요청 (이전 출력 pointer + clarification context + 범위 제한). 동일 에이전트 2회 재스폰 이후 미해소면 사용자 ESCALATE

### Affected
- `CLAUDE.md` — 스폰 시퀀스·Never-skippable·병렬 스폰 권장·CodebaseMapper↔Refactor 대립 섹션 전면 개편
- `agents/RequirementsPLAgent.md` — 병렬 스폰 원칙·dedup·상충 조정 프로토콜·clarification 재스폰 절차 신설
- `agents/DomainAgent.md`, `agents/RequirementsAnalystAgent.md`, `agents/ResearcherAgent.md` — 타 에이전트 산출물 수신 제거, 각자 공통 입력에서 관점 자체 도출. Researcher·DomainAgent는 **non-skippable**로 승격 (null 결과도 명시 반환)
- `agents/ArchitectAgent.md` — 설계 레인 실행 흐름 8단계 재구성 (공통 입력 패키지 → 병렬 스폰 → 대립 조정 → clarification 재스폰)
- `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md` — 상호 산출물 미참조, 원 소스 직접 독해 의무. RefactorAgent에 "잠재 변호 논리 예상" 섹션 신설 (self-identify)
- `docs/orchestrator-playbook.md` — §3.2 스폰 템플릿 특이 블록, §4.2 표준 병렬 패턴 표에 요구사항·설계 레인 추가, §4.4 Clarification 재스폰 절차 신설, §7.3 resume 매핑 수정
- `templates/story-page-structure.md` — §6 "(Researcher, 조건부)" → "(Researcher)" + null 결과 보존 규정

### Migration
- Consumer overlay가 RequirementsPLAgent/ArchitectAgent 행동을 override하지 않는다면 영향 없음
- Override 중이면 `docs/migration-guide.md` §v0.6→v0.7 섹션 참조 — 병렬 스폰 지시 블록 추가 필요

## [0.6.0] — 2026-04-24

### Changed
- **BREAKING**: Plugin name rename `dev-orchestrator` → `codeforge`. `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/*` 경로 references 전부 `${CLAUDE_PLUGIN_ROOT}/codeforge/*` 로 교체
- Repo 예정 rename: `mctrader/plugin-codeforge` → `mctrader/plugin-codeforge` (PLG-19, admin UI)
- Atlassian workspace 이관: 플러그인 dev를 `mctrader.atlassian.net` PLG space + PLG project (component=codeforge)로 운영

### Added
- `.claude/_overlay/project.yaml` — 플러그인 자체의 dog-food config (PLG 좌표)
- Confluence PLG tree: CodeForge top + Stories/Domain Knowledge/ADR/Retrospective/Architecture Overview + 6 retroactive ADRs + 5 per-version retrospectives
- Jira retroactive: 6 Epics (v0.1~v0.5.x) + 11 Stories (PR 1:1)

### Migration
- v0.5.x 사용자: `docs/migration-guide.md` §v0.5→v0.6 섹션 참조 — consumer `.claude/settings.json` hook 커맨드 `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh` → `${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh` 교체 필수

## [0.5.1] — 2026-04-24

### Added
- **Project Config Packet** (playbook §12.5): Orchestrator가 `.claude/_overlay/project.yaml`을 세션 개시 시 1회 로드하고 Atlassian/GitHub 호출이 필요한 에이전트 (DocsAgent·RequirementsPL·DomainAgent·PMO) 프롬프트에 slice를 자동 주입 → 반복 `Read` 회피
- CLAUDE.md에 Project Config Packet 간단 언급 추가

### Changed
- `agents/DocsAgent.md` — Packet SSOT 우선, fallback으로 `Read` 명시

## [0.5.0] — 2026-04-24

### Added
- `overlay/hooks/validate_config.py` — `project.yaml` schema 검증기 (hand-rolled, PyYAML만 의존). Missing file=WARN, malformed YAML=exit 3, schema 위반=exit 4
- `regen-agents.sh`에 validator 통합 — SessionStart 시 자동 검증, 위반 시 abort
- `overlay/hooks/tests/test_validate_config.py` — 22 테스트 (unit + E2E + bundled examples 검증)
- `.github/workflows/test.yml` — GitHub Actions CI (PR/push to main): pytest + yaml 파싱 + example 스모크 + frontmatter 유효성
- `CHANGELOG.md` — SemVer 형식 릴리스 이력

### Changed
- `docs/project-config-schema.md` §6 신설 (Hook 통합 Schema 검증), §7 장래 확장 축소
- README.md "연혁" → CHANGELOG 링크로 축약

## [0.4.0] — 2026-04-24

### Added
- `.claude/_overlay/project.yaml` — consumer SSOT 상수 (Atlassian·GitHub·labels) 구조화 주입
- `docs/project-config-schema.md` — `project.yaml` schema SSOT (경계·필드·접근 규칙·missing 동작)
- `overlay/_overlay/project.yaml.example` — consumer 복사용 스켈레톤
- `examples/library-minimal/` — 라이브러리 shape consumer 예시 (preset 미사용, 공개 API 경로 scoping)
- `docs/migration-guide.md` — 버전업 절차 가이드 (v0.1 → v0.4)

### Changed
- `DocsAgent`·`DomainAgent` 등 Atlassian 호출 에이전트가 `project.yaml`을 `Read`하는 것 의무화
- `.claude/_overlay/CLAUDE.md` 역할 변경 — SSOT 상수 제거, narrative 컨텍스트 (도메인 해설·기술 스택 근거) 전담
- `examples/webapp-minimal/`·`examples/cli-tool-minimal/` overlay 재구성 (`project.yaml` 분리)
- `docs/plugin-design.md` Stage 2 partial 완료 표기

### Migration
- v0.3 사용자: `docs/migration-guide.md` v0.3→v0.4 섹션 참조 (CLAUDE.md overlay의 SSOT 상수를 project.yaml로 이동)

## [0.3.0] — 2026-04-24

### Added
- `agents/DeveloperAgent.md` — generic 구현 담당 (core, `role: dev`)
- `agents/InfraEngineerAgent.md` — 인프라·배포·패키징 전반 (ServerEng 리네임, 범위 확장)
- `presets/webapp/agents/` — 웹앱 preset (BackendDev·FrontendDev 이동)
- `presets/README.md`, `presets/webapp/README.md` — preset 개념·사용법 가이드
- `examples/webapp-minimal/`, `examples/cli-tool-minimal/` — consumer overlay 예시 2종
- `overlay/hooks/merge.py --overlay-only` — core 없는 consumer-defined agent 지원
- `overlay/hooks/tests/test_merge.py` — merge.py 계약 유닛·E2E 테스트 42건

### Changed
- **BREAKING**: `BackendDeveloperAgent`·`FrontendDeveloperAgent` → `presets/webapp/agents/`로 이동 (core에서 제거)
- **BREAKING**: `ServerEngineerAgent` → `InfraEngineerAgent`로 리네임 (범위 확장: systemd/Docker/K8s → 전 플랫폼 배포·패키징)
- **BREAKING**: `DeveloperPLAgent`가 하드코딩된 "4 Dev" 대신 `role: dev` frontmatter 태그로 런타임 roster discovery
- `merge.py` §4d 변경 — "core 없음 + overlay 있음"이 이전엔 abort였으나 이제 overlay-only 렌더
- Core agent 수: 25 → 24 (Backend/Frontend 제거 + DeveloperAgent 추가, ServerEng → InfraEng 리네임)

### Migration
- v0.2 사용자: `docs/migration-guide.md` v0.2→v0.3 섹션 참조 (preset 복사 또는 generic Dev로 전환, ServerEng→InfraEng 리네임)

## [0.2.0] — 2026-04-24

### Added
- **보안 테스트 레인** (7번째 레인) — `SecurityTestPLAgent` + `ClaudeSecurityTestAgent` + `CodexSecurityTestAgent`
- `templates/` 디렉토리 SSOT — `change-plan.md`, `adr.md`, `story-page-structure.md`, `impl-manifest.md`
- Claude + Codex peer 리뷰 3중 (설계·코드·보안)

### Changed
- 기존 "테스트" 레인 → "구현 테스트" + "보안 테스트" 2단계 분리
- FIX 루프: 보안 테스트 FAIL 시 Architect 원인 판정 (구현/설계) — 무제한 FIX

### Migration
- Non-breaking. Jira 대시보드 JQL에 `phase:보안-테스트` 라벨 추가 권장

## [0.1.0] — 2026-04-24

### Added
- 플러그인 pivot — 기존 crypto FW repo(`mctrader`)에서 범용 SW 개발 플러그인 `dev-orchestrator`로 재편 (v0.6.0에서 `codeforge`로 최종 rename)
- 22 에이전트 · 6 레인 오케스트레이션 구조
- Overlay 메커니즘 (β) — consumer 측 `.claude/_overlay/` + SessionStart merge hook
- `overlay/hooks/merge.py` + `regen-agents.sh` — core+overlay 병합 tooling
- Archive tag `archive/pre-plugin-pivot-20260424` — pivot 직전 상태 보존

### Breaking
- 기존 crypto FW 코드 전부 삭제 (`src/mctrader/**`, `tests/**`)
- `.claude/agents/` → `agents/` 경로 이동 (plugin core SSOT)
