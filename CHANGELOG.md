# Changelog

`codeforge` 플러그인 릴리스 이력. 각 엔트리는 버전 bump 단위.
Breaking change 있는 버전은 [`docs/migration-guide.md`](docs/migration-guide.md) 해당 섹션 변경.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능. plugin SemVer rule SSOT: [ADR-037](docs/adr/ADR-037-plugin-version-bump-rule.md).

## [Unreleased]

### Added

- [CFP-1612] **ADR-082 Amendment 25 — §결정 1 layer 1 sub-scope (1-N) 신설 numeric claim write-time verify Wave 2 mechanical enforcement wire** (doc-only fast-path per ADR-054 Cat 1, Issue #1612 HIGH FU-A from CFP-1601 retro carrier — sub-scope 1-K Amd 22 CFP-1601 Wave 1 declaration-only behavioral mandate 의 Wave 2 mechanical lint enforcement wire (declaration → mechanical enforce promotion path), mid-flight CFP-1589 collision recovery — initial Amd 24+1-M → renumber Amd 25+1-N on rebase to origin/main `5b5c9f7b`)
  - **4-tuple primitive (Wave 2 mechanical wire scope)**: (a) lint script SSOT (Python `scripts/lib/check_numeric_claim_write_time.py` per ADR-061 multi-line Python convention + bash thin wrapper `scripts/check-numeric-claim-write-time-verify.sh`) / (b) 6 dimension detection logic (line/file/API/pattern/commit/row count) Python dict SSOT regex+source command pattern map / (c) FP guard 4종 (code-span EXEMPT + quoted-text EXEMPT + templates/** EXEMPT + docs/stories/§9 transcript EXEMPT) + PER_BLOCK_SCAN_CAP=50 CodeQL ReDoS guard / (d) workflow yml + .github/workflows/ byte-identical mirror per ADR-005 + `continue-on-error: true` warning tier + `hotfix-bypass:numeric-claim-write-time-verify` bypass label + evidence-checks-registry warning-tier initial registration
  - **axis disjoint codify**: 1-K (Amd 22 mandate 자체, 4-step verify-before-write + 6 numeric closed-set dimension declaration) ↔ 본 1-N (1-K Wave 2 mechanical enforcement scope, declaration → mechanical lint enforce per ADR-060 §결정 5). axis 인접하나 verify 대상 disjoint (behavioral mandate axis ↔ mechanical enforcement wire axis — declaration → enforce promotion path layered). axis 분리 vs Amd 17 1-G (amendment-slot reservation lifecycle, status enum 4-value reserved|active|abandoned|superseded) + Amd 20 §결정 15 (Issue body 4 sub-pattern stale claim) + Amd 23 1-L (upstream-inherited fact verify, 4 sub-source) + Amd 24 1-M (own-author synthesis 보고 vs actual git commit gap, artifact identity)
  - **pattern_count 2 reach evidence (1-K + 1-N 동일 base inherit)**: (1) CFP-1571 §3.2 line count drift '+93→+101' 3 location 정정 / (2) CFP-1581 §3.2 file count drift '10→14' actual = pattern_count 2 reach Mandatory ADR-045 §D-9 escalation 산물
  - **Option B (super-class scope expansion) 채택** (vs Option A new ADR fragmentation 회피): ArchitectAgent chief author 자율 결정. axis 정합 영역 — super-class 안 sub-scope 1-N (1-A ~ 1-M 와 disjoint axis Wave 2 mechanical enforcement wire SSOT). ratchet 강화 방향 (12 → 13 sub-scope, axis disjoint 영역 누적). Wave 1 → Wave 2 split precedent CFP-1437/1436/1435/1559/1578/1601/1590/1589 11번째 instance 답습 — declaration mandate ↔ mechanical enforcement scope = 동일 axis 안 layered ratchet
  - **Mid-flight CFP-1589 collision recovery (META-self-applied recursive dogfooding 3rd applied case after CFP-FU-A Amd 19 + CFP-1590 Amd 23)**: timeline = ArchitectAgent spawn pinned `f2e78b16` (amendments[] max=23, spawn packet claim 'Amendment 24 + sub-scope 1-M') → fetch reveals CFP-1589 PR #1622 merged (`5b5c9f7b`, Amd 24+1-M 점유 'synthesis vs commit gap verify mandate F-DR-003') → race-winner-takes-it convention 정합 → renumber Amd 24→25 + sub-scope 1-M→1-N on hard-reset to origin/main `5b5c9f7b` + atomic re-apply. ADR-082 §결정 1-L spawn packet fact verify-before-trust 1st applied case (input-axis upstream-inherited fact verify + numeric claim 1-K output-axis source command verify 동시 적용 recursive dogfooding)
  - **Wave 1 declarative SSOT (본 Amendment 25 Phase 1 PR)** = ADR-082 §결정 1 layer 1 sub-scope 1-N append + `mechanical_enforcement_actions[]` entry `numeric-claim-write-time-verify` status `deferred-followup` → `warning-tier wire complete (CFP-1612 Wave 2 carrier)` 갱신 + ADR-RESERVATION amendments_reserved[] row 25 pre-append + evidence-checks-registry warning-tier initial registration entry append (ADR-060 §결정 5 'first introduction = warning mode' default) + label-registry-v2 MINOR bump v2.75 → v2.76 + `hotfix-bypass:numeric-claim-write-time-verify` 101st family member append + MANIFEST.yaml label_registry version 갱신 + 본 CHANGELOG entry append. **Wave 2 = actual mechanical wire (Phase 2 PR 별 sub-carrier — DeveloperPL + QADev spawn)**: `scripts/lib/check_numeric_claim_write_time.py` Python SSOT (ADR-061) + `scripts/check-numeric-claim-write-time-verify.sh` bash thin wrapper + `templates/github-workflows/numeric-claim-write-time-verify.yml` workflow + `.github/workflows/numeric-claim-write-time-verify.yml` byte-identical mirror per ADR-005 + `tests/scripts/check-numeric-claim-write-time-verify/test_*.bats` fixture (5 markers + 6 dimension TCs RED→GREEN stash proof per §결정 11.A). pattern_count ≥ N 추가 reach 시 warning → blocking-on-pr 승격 = Wave 3 별 carrier 분리 (ADR-060 §결정 6 promotion gate AND 3/3 — PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged)
  - **META-self-applied** (§결정 10.D 20th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 6th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590 + Amd 24 CFP-1589 + Amendment 22 §결정 1-K numeric claim verify-before-write 1st applied for Wave 2 wire carrier — recursive dogfooding spawn packet 안 'Amendment 24 + sub-scope 1-M' claim ↔ actual ADR-082 frontmatter post-CFP-1589-merge Read verify divergence direct catch, 정확 next-slot = 25 + 1-N 정정 = numeric-claim 1-K + spawn-packet-fact 1-L paired META first applied case)
  - **Files**: `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` (frontmatter amendments[] Amendment 25 entry + amendment_log[] entry + related_stories[] + mechanical_enforcement_actions[] entry `numeric-claim-write-time-verify` status 갱신 + §결정 1 본문 sub-scope 1-N section append) / `docs/adr/ADR-RESERVATION.md` (amendments_reserved[] row append — adr_number 82 amendment_id 25 reserved_by_cfp CFP-1612) / `docs/evidence-checks-registry.yaml` (numeric-claim-write-time-verify warning-tier initial registration entry append, ADR-060 §결정 5 정합) / `docs/inter-plugin-contracts/label-registry-v2.md` (MINOR bump v2.75 → v2.76 + hotfix-bypass:numeric-claim-write-time-verify 101st family member append) / `docs/inter-plugin-contracts/MANIFEST.yaml` (label_registry version `2.75` → `2.76` 갱신) / `CHANGELOG.md` (본 entry append)
  - **Cross-ref**: Issue #1612 HIGH FU-A / CFP-1601 retro (sub-scope 1-K Amd 22 Wave 1 declaration-only mandate origin) / sister carrier CFP-1571 (line count drift evidence #1) / sister carrier CFP-1581 (file count drift evidence #2) / CFP-1437/1436/1435/1559/1578/1601/1590/1589 (Wave 1→Wave 2 split precedent 11번째 instance)

- [CFP-1589] **ADR-082 Amendment 24 — §결정 1 layer 1 sub-scope (1-M) 신설 own-author synthesis 보고 vs actual git commit gap verify mandate (F-DR-003 carrier)** (doc-only fast-path per ADR-054 Cat 1, CFP-1523 retro carry-over — F-DR-002 P0 finding ArchitectPL verdict packet 'Artifacts written: ...' 보고 ≠ actual git commit DesignReviewPL audit FIX iter 1 dispatch)
  - **4-tuple primitive**: (a) synthesis 보고 시점 actual git commit verify 의무 — `git -C <worktree> log --oneline origin/main..HEAD` direct execute + actual commit list 확인 (worktree modified/untracked 영역 commit 0건 미포함, claim 'Artifacts written' = actual commit hash 매핑 의무) / (b) review-verdict-v4 packet 안 optional `artifact_commits[]` field 영역 (40-char hex commit hash array, future MINOR bump v4.9 → v4.10 carrier 별 sub-CFP) / (c) Story §14 Lane Evidence row append 시 actual commit verify (ADR-073 verify-before-assert + ADR-082 §결정 1 sub-scope 1-M dual binding) / (d) `synthesis_vs_commit_gap_verified: <bool>` field annotation 의무
  - **axis disjoint codify**: 1-L (Amd 23 upstream-inherited input verify, synthesis input 측 4 sub-source 사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file) ↔ 본 1-M (own-author synthesis 결과 vs actual artifact gap, synthesis output ↔ git commit downstream own-author self-verify) = input-output paired complement axis. axis 분리 vs Amd 22 1-K (own author write-time numeric claim source/value strict 6-dimension) — 1-M = numeric 영역 외 artifact identity claim 영역. axis 분리 vs Amd 18 1-H (Orchestrator monopoly §10 FIX Ledger source/evidence, fix-event-v1 contract) ↔ 본 1-M (lane agent self-write own-author axis, lane plugin 영역)
  - **pattern_count 1 reach evidence**: CFP-1523 carrier F-DR-002 P0 finding (Phase 1 ArchitectPL verdict packet 'Artifacts written: ...' 보고 ≠ actual git commit, DesignReviewPL audit verify-before-trust direct git status verify 후 detect, FIX iter 1 dispatch, memory `project_cfp_1523_complete.md` 안 finding 3 박제). deferred-followup carrier (Wave 1 declaration-only mandate, pattern_count 누적 시 Wave 2 mechanical wire 별 carrier 발의 — ADR-082 §결정 6 retain pattern 답습)
  - **Option B (super-class scope expansion) 채택** (vs Option A new ADR fragmentation 회피): ArchitectAgent chief author 자율 결정. axis 정합 영역 — super-class 안 sub-scope axis disjoint 누적 1-M (1-A ~ 1-L 와 disjoint axis own-author synthesis 보고 vs actual artifact gap verify) = governance hygiene + ratchet 강화 방향. Amd 23 Option B precedent 답습
  - **Wave 1 declaration-only behavioral mandate** (`mechanical_enforcement_actions[]` 신규 entry `synthesis-vs-commit-gap-check` warning-tier deferred-followup append). Wave 2 mechanical wire (Python SSOT lint per ADR-061 + bash wrapper + workflow + bats RED→GREEN stash proof per §결정 11.A + label-registry MINOR `hotfix-bypass:synthesis-vs-commit-gap-check` + evidence-checks-registry warning-tier initial registration ADR-060 §결정 5 정합 + review-verdict-v4 v4.9 → v4.10 MINOR carrier `artifact_commits[]` optional field schema 신설) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435/1559/1578/1601/1590 Wave 1→Wave 2 split 답습)
  - **META-self-applied** (§결정 10.D 19th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 5th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + Amd 23 CFP-1590): ADR-RESERVATION amendments_reserved[] row pre-claim commit `98ebb8c` + push (Amd 17 1-G precedent 답습)
  - **Files**: `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` (frontmatter amendments[] Amendment 24 entry + amendment_log[] entry + related_stories[] + related_files[] + mechanical_enforcement_actions[] append + §결정 1 본문 sub-scope 1-M section append) / `docs/adr/ADR-RESERVATION.md` (amendments_reserved[] row append — adr_number 82 amendment_id 24 reserved_by_cfp CFP-1589) / `CLAUDE.md` (verify-before-trust 4-layer 단락 Amendment 24 cross-ref append, 320/320 line cap invariant 보존) / `docs/evidence-checks-registry.yaml` (synthesis-vs-commit-gap-check warning-tier deferred-followup entry append)
  - **Cross-ref**: CFP-1523 retro `project_cfp_1523_complete.md` memory anchor (F-DR-002 origin finding) / Issue #1589 / sister carrier CFP-1590 (Amd 23 1-L upstream-inherited input verify, 본 1-M output verify = input-output paired complement) / sister carrier CFP-1601 (Amd 22 1-K own author numeric strict, 본 1-M = artifact identity verify disjoint complement) / sister carrier CFP-1342 (Amd 18 1-H Orchestrator §10 monopoly, 본 1-M = lane agent self-write disjoint complement)

- [CFP-1590] **ADR-082 Amendment 23 — §결정 1 layer 1 sub-scope (1-L) 신설 spawn prompt fact verify-before-trust mandate (upstream-inherited stale fact carrier super-class)** (doc-only fast-path per ADR-054 Cat 1, PMOAgent CFP-1523 retro §5 inline ADR draft Orchestrator → ArchitectAgent spawn carry-over carrier, ADR-045 §D-9 Mandatory escalation pattern_count 3 reach, mid-flight CFP-1601 collision recovery — initial Amd 22+1-K → renumber Amd 23+1-L on rebase to origin/main `4c668913`)
  - **4-tuple primitive**: (a) upstream-inherited fact 식별 의무 — 4 sub-source (사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file) / (b) direct source verify 의무 — `verified-via:` annotation 의무 (cached/synthesized 금지) / (c) stale 검출 시 `[fact-correction: <claim> stale, verified <correct-value>, source: <verify-source>]` marker 의무 / (d) `spawn_prompt_fact_verified: <bool>` field 명시
  - **axis disjoint codify**: 4-layer temporal defense (Amd 15 pre-spawn-fetch + Amd 19 pre-spawn-prompt-finalize + Amd 16 mid-spawn-periodic + Amd 18 Orchestrator §10 source-claim) 의 content fact axis 5th layer 신설 (when verify vs what verify disjoint). axis 분리 vs Amd 5 1-C (content 전달 형식 axis) + Amd 20 §결정 15 (self-write content stale super-class) + Amd 22 1-K (own author write-time numeric claim strict CFP-1601)
  - **pattern_count 3 reach evidence**: (1) CFP-1493 S2.3 PR #1520 commit message defer 사유 inheritance "284 MCP call" 실 6 atomic 47x over-estimate Confluence REST cascade primitive 미선재 / (2) CFP-1523 사용자 spawn prompt 4 fact 모두 stale (ADR lane field 1/117 실 0/117 + binding 53 실 59 + 142 page 실 corpus 148 + 284 MCP call 실 6) / (3) CFP-1591 Issue body canonical/sibling 역할 반전 ("canonical (codeforge-review) v4.11 vs sibling (wrapper) v4.9" 단언 실 reverse direction ADR-010 §결정 1 canonical-first invariant 위배)
  - **Option B (super-class scope expansion) 채택** (vs Option A new ADR fragmentation 회피): ArchitectAgent chief author 자율 결정. axis 정합 영역 — super-class 안 sub-scope axis disjoint 누적 1-L (1-A ~ 1-K 와 disjoint) = governance hygiene + ratchet 강화 방향. ADR-082 already permanent governance anchor verify-before-trust 4-layer 의 internal lane agent self-write super-class SSOT 영역
  - **Mid-flight CFP-1601 collision recovery (META 2nd applied case after CFP-FU-A Amd 19)**: timeline = ArchitectAgent spawn pinned `ec2fc349` (max=21) → ADR-RESERVATION row pre-claim (d3d307f) → ADR-082 Amd 22+1-K body write (7a48a08) → PR #1615 open → fetch reveals CFP-1601 PR #1611 merged (`4c668913`, Amd 22+1-K 점유 "numeric claim write-time strict claim mandate") → race-winner-takes-it convention 정합 → renumber Amd 22→23 + sub-scope 1-K→1-L on hard-reset + re-apply
  - **Wave 1 declaration-only behavioral mandate** (`mechanical_enforcement_actions[]` 신규 entry `spawn-prompt-fact-verify` warning-tier deferred-followup append). Wave 2 mechanical wire (Python SSOT lint per ADR-061 + bash wrapper + workflow + bats RED→GREEN stash proof per §결정 11.A + label-registry MINOR + evidence-checks-registry warning-tier initial registration) = 별 sub-CFP carrier 분리 (precedent CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 1→Wave 2 split 답습)
  - **META-self-applied** (§결정 10.D 18th applied case + Amendment 17 §결정 1-G strict pre-reservation claim mandate 4th applied case after Amd 18 CFP-1342 + Amd 21 CFP-1578 + Amd 22 CFP-1601 + mid-flight collision recovery 2nd applied case after CFP-FU-A Amd 19): ADR-RESERVATION amendments_reserved[] row pre-claim preserved + post-CFP-1601-merge atomic renumber
  - **Files**: `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` (frontmatter amendments[] Amendment 23 entry + amendment_log[] entry + related_stories[] + related_files[] + mechanical_enforcement_actions[] append + §결정 1 본문 sub-scope 1-L section append) / `docs/adr/ADR-RESERVATION.md` (amendments_reserved[] row append — adr_number 82 amendment_id 23 reserved_by_cfp CFP-1590) / `CLAUDE.md` (verify-before-trust 4-layer 단락 Amendment 22 + Amendment 23 cross-ref append) / `docs/evidence-checks-registry.yaml` (spawn-prompt-fact-verify warning-tier deferred-followup entry append)
  - **Cross-ref**: PMOAgent retro `<internal-docs>/plugin-codeforge/retros/2026-05-25-cfp-1523-confluence-ia-real-backfill.md` §5 inline ADR draft anchor (Orchestrator → ArchitectAgent spawn carry-over source) / Issue #1590 / sister carrier CFP-1559 (Amd 20 self-write Issue body stale-claim super-class) / sister carrier CFP-1601 (Amd 22 numeric claim write-time strict, axis disjoint complement) / sister carrier CFP-FU-A Amd 19 (1st mid-flight collision recovery META precedent)

- [CFP-1603] **playbook §3.5.3 신설 — Version race coordination sequential merge orchestration** (doc-only fast-path per ADR-054, ADR-045 §D-9 pattern_count 2 reach escalation_resolved_carrier — Wave 2 + Wave 3 batch sentinel evidence)
  - **race detection criteria**: same-base-SHA + same-mirrored-field primitive — `pr_open` / `lane_spawn` transition trigger 직전 sentinel polling §3.5.1 HEAD compare step 에서 detect (별 detection mechanism 신설 0, 기존 §3.5.1 답습)
  - **4-step (full path)**: 선행 marketplace sibling PR merge → 선행 plugin PR merge → 후행 plugin PR rebase + version bump 재계산 (SemVer monotonic invariant 보장: PATCH 6.7.3 < MINOR 6.8.0 < PATCH rebased 6.8.1) + CHANGELOG.md chronological append → 후행 marketplace sibling PR merge → 후행 plugin PR merge
  - **2-step (marketplace 부재 축소)**: 선행 plugin PR merge → 후행 plugin PR rebase + merge (mirrored field 변경 0 시, doc-only fast-path Story batch 영역)
  - **ordering invariant**: MAJOR > MINOR > PATCH per ADR-037 §결정 1 정합. 동일 surface category race 시 lower CFP 번호 선행 merge (ADR-050 §3.4.2 답습)
  - **race resolution example (Wave 3 evidence verbatim, 2026-05-25 KST)**: CFP-1580 MINOR 6.8.0 선행 merge + CFP-1559 PATCH 6.7.3 → 6.8.1 rebase resolution 7-step worked example
  - **ADR-045 §D-9 escalation_resolved_carrier declare**: pattern_count 2 reach (Wave 2 + Wave 3 batches) → escalation_action `escalate_user` resolution = 본 carrier declarative codify
  - **mid-spawn drift detection (ADR-073 Amendment 12)**: §3.5.2 slot 점유 (CFP-1578 Amendment 21 cross-repo worktree target authority verify) 발견 → §3.5.3 sibling slot 정정 채택 (§3.5.1 sentinel polling + §3.5.2 cross-repo worktree + §3.5.3 version race = §3.5.x family axis disjoint trio)
  - **mechanical_enforcement_actions: []** declaration-only Wave 1 (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습). Wave 2 mechanical wire (workflow lint `version-race-coordination-ordering` + bats fixture 4 case: MINOR+PATCH / PATCH+PATCH / MAJOR+MINOR / marketplace 부재 축소) = 별 sub-CFP carrier
  - **ADR Amendment 0건 / 신규 ADR 0건** — P2 severity 영역 대비 over-codify risk 회피 (RequirementsPL `scope_verdict: PASS` + 3-agent 수렴 derived default 정합)
  - **Codex TP#2 skip** per ADR-052 Amendment 11 (wrapper-self conditional skip, ADR-082 §결정 2 scope a-d write-time verify cover)
  - Change Plan SSOT: `<internal-docs>/plugin-codeforge/change-plans/cfp-1603-version-race-coordination.md`
  - Story SSOT: `<internal-docs>/plugin-codeforge/stories/cfp-1603.md` §3·§7·§11 append
  - Cross-ref carrier: CFP-1540 (Wave 2 first occurrence, sentinel script cp949 fix sibling axis disjoint), CFP-1559 (Wave 3 PATCH 6.7.3 → 6.8.1 rebase evidence), CFP-1580 (Wave 3 MINOR 6.8.0 선행 merge evidence), CFP-1578 (paired sibling §3.5.2 cross-repo worktree target authority axis disjoint), ADR-037 §결정 1 / ADR-063 §결정 1·2 / ADR-045 §D-9 / ADR-050 §3.4.2 / ADR-024 §3 cross-ref

- [CFP-1607] **ADR-024 Amendment 15 — `per-plugin-cumulative-counter` warning → blocking-on-pr tier ratchet (ADR-060 framework first-use blocking-on-pr promotion, 2026-05-25 KST)** (Wave 4 batch sequential last carrier — PIVOT trend 4/4 break 후 PROCEED_WITH_SCOPE_EXPANSION)
  - **사용자 directive**: `사용자 confirmed blocking-on-pr 승격` (Issue #1607 user-utterance 2026-05-25 KST 18:00, Wave 3 retro §4.2 C `escalate_user` enum resolved)
  - **ADR-060 §결정 6 promotion gate AND 3/3 PASS evidence**: (a) PR cumulative since 2026-05-17 = **200 PRs** ≥ 20 (10x threshold, `gh pr list --search "merged:>=2026-05-17" --limit 200`) / (b) bypass label外 failure count = **0** (`recurrence.count: 0` registry yaml verified + `gh pr list --label hotfix-bypass:per-plugin-cumulative-counter` returned 0 PRs) / (c) sibling Stories CFP-390 PR #415/#420 + CFP-455 PR #460/#461 (CFP-412 substitution per ADR-060 Amendment 1+2 chain) **ALL MERGED**
  - **본 Amendment 15 = ADR-060 framework 첫 actual blocking-on-pr 승격 carrier** — multi-entry registry 운영 검증 첫 사례 (template precedent emission, 향후 21+ warning-tier entry 의 blocking-on-pr 승격 path = 본 Amendment 답습 base)
  - **Wave 1 (declarative — 본 Phase 1 PR scope)**: `docs/evidence-checks-registry.yaml` entry `per-plugin-cumulative-counter` 4 field transition (`current_tier: warning → blocking-on-pr` + `status: warning → blocking-on-pr` + `recurrence.last_occurrence: null → 2026-05-25T18:00:00+09:00` + `recurrence.promotion_trigger: none → warning_to_blocking_on_pr`) + 2 신규 optional field (`promoted_by: CFP-1607` + `promoted_date: 2026-05-25`) + `sibling_dependencies: [] → [CFP-390, CFP-412, CFP-455]` + `evidence_artifacts` 확장 2 entry (audit_comment_author_verification_lint + sticky_comment_pattern_implementation)
  - **Wave 2 (mechanical wire — 별 sub-CFP carrier)**: workflow `templates/github-workflows/per-plugin-cumulative-counter.yml` + `.github/workflows/` self-app `continue-on-error: true` → `false` ratchet + ADR-060 §결정 6 evidence_artifact (v) `scripts/check-audit-comment-author.{sh,py}` + workflow + bats fixture pair + (vi) `bypass-audit.yml` sticky comment pattern wire (marker `[hotfix-bypass-audit] PR=N` dedup)
  - **label-registry-v2 v2.75 retain** (family member 신설 0, `hotfix-bypass:per-plugin-cumulative-counter` 45번째 family member 보존). `docs/inter-plugin-contracts/MANIFEST.yaml` v2.75 retain
  - **plugin.json bump 0 = `marketplace_sync_declared: false`** (mirrored field 변경 0, kind:registry sibling sync 면제 영역, ADR-063 atomic invariant 발효 조건 미충족)
  - **mid-spawn drift detection (ADR-073 Amendment 12) 적용**: 본 worktree base advance evidence — 0a19e6a → 4c66891 rebase clean (4 commits behind origin/main detected: CFP-1601 + CFP-1586 + CFP-1585 + CFP-1584 cascade integrate)
  - **ADR-RESERVATION strict pre-claim (ADR-082 §결정 1 sub-scope 1-G) 4th applied case**: ADR-024 amendment_id=15 for CFP-1607 row append + commit + push DONE (race window 차단, Amendment 18 CFP-1342 1st + Amendment 21 CFP-1578 2nd + Amendment 22 CFP-1601 3rd precedent 답습) + sub-scope 1-K numeric claim write-time strict claim 2nd applied case (Amendment 22 1st META carrier 답습)
  - **deputy spawn 0** — pure declarative governance ratchet (Wave 2 mechanical wire 별 sub-CFP scope), `mechanical_fast_path_inline` precedent 답습 (chief author single-source author)
  - **CLAUDE.md L302 영역 prose 갱신**: warning tier 23종 → 22종 + blocking-on-pr 3종 → 4종 (CFP-1607 carrier 반영)
  - **6 self-check ALL PASS** (mechanical / boundary completeness / dimensional empirical / marketplace_sync_declared=false / architecture_doc=false with none_rationale / kst-timestamp=true)
  - Change Plan SSOT: `docs/change-plans/cfp-1607-per-plugin-cumulative-counter-promotion.md`
  - Story SSOT: `<internal-docs>/plugin-codeforge/stories/cfp-1607.md` §3·§7·§8·§11·§14 append
  - Cross-ref carriers: ADR-024 §결정 6.A.3 + Amendment 15 (본 carrier) / ADR-060 §결정 6 framework first-use precedent / ADR-045 §D-9 forcing function 작동 사례 첫 carrier (escalate_user enum resolved) / ADR-058 §결정 5 ratchet 강화 (sunset_justification N/A) / ADR-064 §결정 5 CFP scope unitary (sibling 6.A.4/6.A.5 별 CFP) / ADR-082 §결정 1 sub-scope (1-G) + (1-K) META self-applied / ADR-073 Amendment 12 mid-spawn drift detection / CFP-845 본체 ship precedent (PR #886 + #891 MERGED 2026-05-17)

- [CFP-1577] **playbook §9.7.1 신설 — Phase label transition timing forcing function** (doc-only fast-path per ADR-054, CFP-1539+CFP-1540 batch retro §4.1 #1 mandatory follow-up carrier)
  - **axis disjoint codify**: §9.7 = static snapshot mapping (PR open 시 mergeable 판정 기준) ↔ §9.7.1 = dynamic transition timing forcing function (Orchestrator 가 *언제 무엇을* attach/remove 의무 codify). workflow ↔ Orchestrator handshake codification gap 해소
  - **11-row transition timing 표** (column schema: `Phase / Add label / Remove label / Add gate / Timing signal / Source`) — 8 lane phase taxonomy (CFP-1059 후) + Issue Forms entry + terminal `phase:완료` 전부 coverage
  - **`phase:완료` precondition AND mandate** (CFP-1539+CFP-1540 incident 차단): (a) 활성 lane terminal gate (`gate:design-review-pass` default / `gate:deploy-review-pass` deploy lane 활성 시) + (b) `gate:retro-complete` (label-registry-v2 line 558, ADR-045 v1.5 실재 confirmed). 위반 정정 pattern (incident verbatim 답습) = `phase:구현-리뷰` + gate 재부착 → workflow PASS
  - **`skills/story-epic-flow-preflight/SKILL.md` preflight check #1 cross-ref 1-row append** — skill body 의 phase 라벨 정합 check 가 §9.7.1 SSOT 참조 의무 (AC-3 carrier)
  - **workflow yml 변경 0건** (Issue Out of scope §3 retain — `phase-gate-mergeable.yml` 본문 무수정, documentation layer only)
  - **ADR Amendment 0건 / 신규 ADR 0건** — playbook documentation 강화 only, ADR governance 영역 무관 (RequirementsPL `scope_verdict: AGREED` + `0 ADR Amendment` 정합)
  - **A3 pivot resolved**: `gate:retro-complete` label-registry-v2 line 558 실재 [verified] (ADR-045 v1.5 entry). A4 pivot retained — skill path `skills/story-epic-flow-preflight/SKILL.md` (Issue body stale path `codeforge-` prefix 제거)
  - Change Plan SSOT: `<internal-docs>/plugin-codeforge/change-plans/cfp-1577-phase-label-transition-timing.md`
  - Story SSOT: `<internal-docs>/plugin-codeforge/stories/cfp-1577.md` §3·§7·§11 append
  - Cross-ref carrier: codeforge-internal-docs PR #904 (CFP-1539+CFP-1540 batch retro §4.1 #1), CFP-342 / CFP-479 (playbook §9.7 source), ADR-026 Amendment 4 (CFP-795 post-merge fix exemption axis disjoint)


### Changed

- [CFP-1541] **`scripts/check-3way-version-parity.sh` Sanity guard (1) size threshold lowering — 40000B → 1024B (Axis D minimum floor lowering, CFP-FU-B cleanup paradox 차단)** (CFP-FU-B retro mandatory follow-up #3 carrier — `lint_paradox_cleanup_trips_stale_heuristic` pattern 1st occurrence 차단)
  - **4 places threshold value + wording 갱신** (L16/L135/L138/L139 — uniform unconditional, ADR-068 I-3 + I-4 정합): `if [[ "$MARKETPLACE_SIZE" -le 40000 ]]` → `if [[ "$MARKETPLACE_SIZE" -le 1024 ]]` + comment / echo wording 동시 sync
  - **empty-blob / truncated fetch 방어 intent preserve**: 1024B floor = `{}` empty JSON (2B) 의 ~512x + `{"plugins":[]}` (15B) 의 ~68x + single minimal plugin entry (~200B) 의 ~5x safety margin. 기존 Sanity guard 2-6 multi-layer defense (JSON parse / 4-field parity / sister entry mutation / git diff single-line / version pattern unique) 가 truncated semantic 영역 already cover — guard 1 unique value = "fetch 0-byte 또는 garbage binary fail-fast" only → 1024B sufficient
  - **CFP-820 시점 stale assumption 영역 갱신**: CFP-820 (2026-05-17) marketplace.json 실 size = ~64KB (description 60KB + 4KB skeleton) 기반 40000B threshold = "절반 이하 = 비정상" heuristic reasonable. CFP-FU-B (2026-05-25) cleanup 후 실 size = 21,696B → 40000B 가 normal state trip → `exit 2` false-positive. cleanup carrier 자체가 lint 의 stale assumption 영역을 trip 하는 paradox 영역 1회성 차단
  - **bypass overhead 감소** (positive direction): 본 fix 후 cleanup carrier PR 영역 `hotfix-bypass:version-3way-atomic` label 사용 빈도 0 목표 → bypass-as-norm-mutation (ADR-024 Amendment 8 §결정 6.A.3) escalation 위험 영역 회피
  - **bats fixture TC-20 / TC-21 추가** (Phase 2 carrier): TC-20 (cleanup_carrier scenario size 21696B → exit 0 + 3-way match) + TC-21 (cleanup_carrier_below_floor size 100B → exit 2 empty-blob defense preserve) — 기존 19 TC regression 0 (특히 TC-8 size=100 trip path 1024B floor 정합 invariant)
  - **RED→GREEN stash proof** (CFP-1334 §8.4 mandate): `git stash push -- scripts/check-3way-version-parity.sh` → bats TC-20 RED (40000 threshold 영역 → cleanup_carrier mode size 21696 ≤ 40000 → exit 2 trip) → `git stash pop` → bats 21/21 GREEN. `tests/scripts/MANIFEST.yaml` `check-3way-version-parity` entry `red_green_proof:` block (Phase 2 DeveloperPL self-write)
  - **ADR Amendment 신설 0건**: ADR-063 §결정 15 (3-way version atomic invariant policy) 변경 0 (Issue body Out of scope verbatim) / ADR-070 verify-before-trust 표준 변경 0 (empty-blob detection intent preserve) — 본 fix = lint script heuristic layer (policy layer 영역 외)
  - **plugin.json bump 0건**: marketplace_sync_required: false (mirrored field 변경 0)
  - **sister carrier 부재 verified** (Story §2.1 row 5): `Grep "size.*40000|truncated|content-checksum"` = `scripts/check-3way-version-parity.sh` 단독 hit, 다른 size-threshold lint 0건. `lint_paradox_cleanup_trips_stale_heuristic` pattern_count: 1 (threshold < 2, informational only)
  - Change Plan SSOT: `<internal-docs>/plugin-codeforge/change-plans/cfp-1541-check-3way-version-parity-threshold.md`

### Fixed
## [6.8.1] - 2026-05-25

### Added

- [CFP-1559] **ADR-082 Amendment 20 — §결정 15 신설 Issue body stale-claim super-class verify-before-trust write-time pre-screen mandate (declarative-only Wave 1)**

### Bump rationale

- ADR-037 §결정 1(a) PATCH — additive governance behavior mandate (declarative Wave 1 only, src/tests 변경 0)

## [6.8.0] - 2026-05-25

### Added

- [CFP-1580] **ADR-068 Amendment 4 + ADR-045 §D-9 Amendment 7 paired sibling — Wave 2 mechanical wire 영역 design review skip 정합 invariant codify (pattern_count 5 evidence-base)** (PMOAgent CFP-1539+1540 batch retro §6 escalation_action escalate_user → 사용자 Option A confirmed compress normative codify 2026-05-25 KST)
  - `docs/adr/ADR-068-boundary-completeness-invariants.md` — **Amendment 4 (§결정 7 신설)**: Wave 2 mechanical wire 영역 (Wave 1 declarative anchor active 후 scripts/workflow/bats implementation only) DesignReviewPL spawn = optional (skip default) + Wave 1 declarative or 신규 ADR/governance 영역 = mandatory retain. ArchitectAgent §13 4-tuple self-check (ADR-068 I-1~I-6 + ADR-065 10-item + ADR-082 §결정 11.A bats RED→GREEN stash proof + chief tie-break ladder Amd 2) + CodeReviewPL mechanical correctness review retain = DesignReviewPL semantic review 대체 sufficient. DeveloperPL spawn prompt 안 `wave2_mechanical_wire_dr_skip_applicable: bool` declarative anchor field codify (declarative anchor only, 실 wire = 별 sub-CFP carrier Wave 2 mechanical enforcement). orthogonal axis with §결정 1 invariants (spawn-time orchestration governance ↔ write-time verification semantic). I-1~I-6 본문 의미 변경 0건, invariants count 6 retain. review-verdict-v4 schema 변경 0건 (declarative anchor only, sibling sync 면제).
  - `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — **Amendment 7 (evidence-only)**: §D-9 forcing function 산물 기록 6번째 (Amendment 6 CFP-776 ADR-082 carrier 5번째 / 본 = 6번째). pattern `wave2-mechanical-wire-design-review-skip` pattern_count 5 ≥ threshold 2 reach Mandatory (CFP-1489 / CFP-1497 / CFP-1500 / CFP-1502 / CFP-1539 5 precedent linear chain, all Wave 1 anchor active 후 Wave 2 wire 영역 DesignReviewPL spawn 0 + 0 design FIX + admin squash merge) → escalate_user → 사용자 Option A → ADR-068 Amendment 4 산물. §D-9 결정 본문 / threshold N=2 / hybrid 검출 전략 / escalation_action enum 2-value 의미 변경 0건.
  - `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 2-row pre-claim append (ADR-068 Amd 4 + ADR-045 Amd 7 paired sibling, ADR-082 Amendment 17 §결정 1-G strict pre-claim mandate 정합, status active)
  - `CLAUDE.md` — ADR-068 Amendment 4 inline cross-ref 1-line append (verify-before-trust 4-layer 단락 영역 외, ADR-068 description line 영역 — boundary completeness invariants 단락 6 invariants 본문 정합)
  - `(cross-repo)` `mclayer/marketplace/.claude-plugin/marketplace.json` — `plugins[name=codeforge]` block `version` 6.7.2 → 6.8.0 sibling sync (ADR-063 §결정 1 3-file atomic invariant + §결정 2 ordering: marketplace 선행 merge → wrapper merge). description / name / author 변경 0 (mirrored field 4종 중 version 1개만 변경).
  - `docs/cross-repo-patches/cfp-1580-marketplace-sync.patch.txt` (신규) — marketplace.json patch content draft worktree-saved evidence (Orchestrator cross-repo PR open 시 verbatim 사용)

### Scope (doc-only fast-path ADR-054)

- src/tests 무변경 — ADR Amendment 2종 + CLAUDE.md + plugin.json MINOR bump + CHANGELOG + marketplace.json sibling sync atomic (ADR-063 §결정 1 5-file scope)
- declarative anchor only — Wave 2 mechanical enforcement (DeveloperPL spawn prompt 실 wire / workflow lint `wave2-mechanical-wire` label PR 영역 DesignReviewPL spawn 0 warning tier 검출) = 별 sub-CFP carrier
- ADR-082 §결정 6 + ADR-070 §D5 + CFP-898/899/900 + ADR-085/097 precedent declaration-only Wave 1 retain pattern 답습

### Bump rationale

- ADR-037 §결정 1(h) MINOR — governance behavior change (chief author Wave 2 mechanical wire 영역 DesignReviewPL skip 정합 mechanism codify + Wave 1 영역 mandatory retain invariant 명확화)
- ADR-063 §결정 1 atomic invariant 정합 (plugin.json mirrored field `version` 변경 → marketplace.json sync 동반 의무)
- review-verdict-v4 schema bump 0건 (declarative anchor only, sibling sync 면제)

### Cross-ref

- Sibling carriers: CFP-1539 (Wave 2 mechanical wire 5번째 + 본 carrier 발의 origin) / CFP-FU-C #1577 + CFP-FU-D #1578 (process learnings)
- Retro carrier: codeforge-internal-docs PR #904 (CFP-1539 + CFP-1540 batch retro §6 escalation)
- ADR-068 (boundary completeness 6 invariants — extending mechanism)
- ADR-065 (mechanical self-check 10-item Amd 4 + Amd 5 — ArchitectAgent §13 4-tuple self-check 1/4 layer)
- ADR-082 §결정 11.A (bats RED→GREEN stash proof — ArchitectAgent §13 4-tuple self-check 1/4 layer)
- ADR-045 §D-9 (pattern escalation forcing function — paired sibling Amendment 7)
- ADR-024 Amendment 8 (bypass-as-norm-mutation 위험 cross-ref)
- 5 precedent CFP linear chain: CFP-1489 / CFP-1497 / CFP-1500 / CFP-1502 / CFP-1539

### Fixed (CFP-1540/CFP-1539 carry-over from prior session — rolled into 6.8.0 release)

- [CFP-1540] **Sentinel script `scripts/lib/check_parallel_work_sentinel.py` — 6 subprocess.run() call sites cp949 encoding fix** (CFP-967 mechanical wire invocation reliability layer 회복, CFP-FU-A retro mandatory follow-up #2 carrier)
  - 6 call sites (line 95/114/128/327/344/380) 의 `subprocess.run(..., text=True)` 에 `encoding="utf-8", errors="replace"` 명시 추가. line 113 `git fetch origin` = binary discard (skip, disjoint scope)
  - Windows Git Bash 환경 cp949 default platform encoding 으로 인한 `UnicodeDecodeError` 차단 → race window catch 실패 silent failure state 해소
  - 3-kwarg combo rationale (DomainAgent + Researcher convergent): `text=True` (mode flag) + `encoding="utf-8"` (codec spec, PEP 540 env dependency 회피) + `errors="replace"` (`U+FFFD` visible marker, silent corruption 차단 + crash 차단 양립)
  - sibling-scope continuation of CFP-1393 F8-FU (PR #1395, `sys.stdout.reconfigure` 37 file bulk sweep print() scope) — 본 fix = subprocess() scope second-half
  - bats TC-9 추가 (Korean Issue title fixture mock, `tests/scripts/check-parallel-work-sentinel/fixtures/non-ascii-title.json` 신규) — 16/16 GREEN gate (기존 8 TC + TC-9)
  - Wave 2 mechanical wire (sibling paired) = CFP-1539 (sentinel reliable invocation 후속 carrier — 본 #1540 이 prerequisite)
  - Change Plan SSOT: `<internal-docs>/plugin-codeforge/change-plans/cfp-1540-sentinel-cp949-encoding-fix.md`

### Added

- [CFP-1578] **ADR-082 Amendment 21 — §결정 1 layer 1 sub-scope (1-J) 신설 cross-repo worktree target authority verify mandate** (worktree mis-target 첫 catch carrier, CFP-1539+CFP-1540 batch retro §4.1 #2 mandatory follow-up, paired sibling CFP-1559 Amendment 20 Issue body stale claim pre-screen super-class axis disjoint)
  - **ADR-082 Amendment 21** (frontmatter amendments[] entry + amendment_log[] entry + 본문 §결정 1 sub-scope 1-J body 신설): 4-tuple primitive — (a) `git -C <worktree_abs_path> remote -v` expected repo vs actual remote URL 일치 verify / (b) spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field 의무 명시 (write-target authority anchor block, sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` + 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습) / (c) cross-repo 작업 sequence 시 명시적 worktree switch (각 repo 별 worktree 분리, ADR-040 worktree convention 정합) / (d) verified-via annotation `worktree_target_authority_verified: <bool>` field 의무 명시
  - **ADR-RESERVATION amendments_reserved[] row pre-append + commit + push 완료** (adr_number 82 amendment_id 21 reserved_by_cfp CFP-1578 reservation_date 2026-05-25 KST status active, PRE-eee3ec6 commit on cfp-1578-wave3) — Amendment 17 sub-scope 1-G strict claim mandate META 2nd applied case (Amendment 18 CFP-1342 1st applied case precedent 답습)
  - **CLAUDE.md L282 verify-before-trust 4-layer 단락 Amendment 21 cross-ref append** (CFP-506 line cap 정합, 본문 wording mirror)
  - **docs/orchestrator-playbook.md §3.5.2 sub-section 신설** — Cross-repo worktree target authority verify (CFP-1578 / ADR-082 Amendment 21 §결정 1 sub-scope 1-J) declarative anchor + 4-tuple primitive 표 + verify pattern bash skeleton + cold start sentinel + cross-ref
  - **skills/lane-self-write-boundary/SKILL.md cross-cutting rule append** — Cross-repo worktree target authority verify-before-write matrix 4 target repo (wrapper / internal-docs / marketplace / consumer-<name>) × expected remote URL pattern × owner content + disjoint axis vs cross-repo `gh` rule 명시 (API-level vs filesystem-level boundary)
  - **Wave 1 declaration-only behavioral mandate**: mechanical_enforcement_actions[] 신규 entry `worktree-target-authority-verify` warning-tier deferred-followup (ADR-082 §결정 6 retain pattern 답습). Wave 2 mechanical wire (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry) = 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 Wave 1→Wave 2 split precedent 답습)
  - **RequirementsPL verdict Alternative C 채택**: Issue #1578 out-of-scope `ADR 신설` = new ADR file scope, ADR-082 sub-scope Amendment 영역과 disjoint axis — sub-scope 신설 (1-J) 로 ADR Amendment 영역 적합
  - **META-self-applied (§결정 10.D 16th applied case)**: 본 Amendment 21 자체가 ADR-082 frontmatter `amendments:` Read verify (worktree HEAD 4000440 origin/main amendments[] max=19 — CFP-FU-A Amd 19 merge 후 base + paired sibling CFP-1559 Amd 20 pre-claim gating → 정확 next-slot for CFP-1578 = 21) 후 결정
  - **plugin.json bump 0건**: marketplace_sync_required: false (mirrored field 변경 0)
  - **Change Plan SSOT**: `<internal-docs>/plugin-codeforge/change-plans/cfp-1578-worktree-target-authority-verify.md` + Story file `<internal-docs>/plugin-codeforge/stories/cfp-1578.md` §3·§7·§11

- [CFP-1539] **CFP-FU-A Wave 2 mechanical wire — pre-spawn-prompt-finalize-verify (ADR-082 Amd 19 sub-scope 1-I)** (4-layer temporal defense forcing function 의 마지막 mechanical layer, Layer 4 preventive pre-spawn-prompt-finalize verify enforcement)
  - **Phase 1 design artifacts** (본 PR 산출물): Change Plan (`<internal-docs>/plugin-codeforge/change-plans/cfp-1539-fu-a-wave2-pre-spawn-prompt-finalize-verify.md`) + Story §3·§7·§11 append (`<internal-docs>/plugin-codeforge/stories/CFP-FU-A-W2.md`) + `CLAUDE.md` L282 Wave 2 wire activation 1-line marker + 본 CHANGELOG `[Unreleased]` entry
  - **Phase 2 actual implementation** (declarative, DeveloperAgent carrier 분리 또는 동일 PR atomic): 5-piece atomic wire bundle (`scripts/lib/check_pre_spawn_prompt_finalize_verify.py` Python SSOT + `scripts/check-pre-spawn-prompt-finalize-verify.sh` bash thin wrapper + `templates/github-workflows/pre-spawn-prompt-finalize-verify.yml` workflow + `.github/workflows/` byte-identical mirror + `tests/scripts/cfp-1539/cfp-1539-pre-spawn-prompt-finalize-verify.bats` 9 TC + 2 PREREQ = 11/11 GREEN target RED→GREEN stash proof per ADR-082 §결정 11.A) + 3 registry sync (`docs/inter-plugin-contracts/label-registry-v2.md` v2.71 → v2.72 MINOR + 97번째 hotfix-bypass:* family member raw active concrete grep count post-append 96 + 1 = 97 정합 per ADR-108 §결정 3 / `docs/inter-plugin-contracts/MANIFEST.yaml` label_registry row "2.71" → "2.72" / `docs/evidence-checks-registry.yaml` 신규 entry `pre-spawn-prompt-finalize-verify` warning Active owner_adr ADR-082 + paired_owner_adr ADR-073) + 1 bats MANIFEST entry (`tests/scripts/MANIFEST.yaml`)
  - **`scripts/bootstrap-labels.sh` body 변경 0** (CFP-598 dynamic registry-driven pattern via `parse-hotfix-bypass-labels.py` — registry yaml entry append 시 자동 pick-up)
  - **META self-application 5th applied case**: 본 Story ArchitectAgent spawn 자체가 `[PRE-SPAWN-ORIGIN-MAIN-SHA: 2e2c53a3970c67c3f0961d94b5ed8fd8e3cf2cd0]` block + `[USER-UTTERANCE-VERBATIM]` block + (장차 Phase 2) `pre_spawn_prompt_finalize_verified: true` annotation 3-block 동시 사용 = mechanism 5th applied case (CFP-1489 1st + CFP-1497 2nd + CFP-1500 3rd + CFP-1502 4th 답습)
  - **ADR Amendment 신설 0건**: ADR-082 Amd 19 본문 line 1675 declarative split 이미 codify, ADR 본문 수정 불필요
  - **plugin.json bump 0건**: marketplace_sync_required: false (mirrored field 변경 0)
  - **sister Issue #1540 cp949 fix paired carrier**: Python subprocess UTF-8 강제 + cp949 fallback 차단 pattern cross-ref (CFP-1489 line 50-55 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` verbatim 답습)
- [CFP-FU-A] **Parallel session race 11th occurrence 3-Amendment paired carrier + 12th meta-occurrence collision recovery** (escalate_user pattern_count 11 reach Mandatory ADR-045 §D-9 — sub-decisions 1+2+3 통합 + recursive dogfooding evidence for #1476)
  - `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 13 (transition trigger enum 12+13번째 entries `pre_git_operation` + `pre_push`, polling cadence 1 → 3) + Amendment 14 (§결정 1-P primitive AND aggregate composition layer, OR semantics → 3-mode AND aggregate `scripts/lib/check_parallel_work_sentinel.py:437` Wave 2 mechanical wire 별 sub-CFP carrier)
  - `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — Amendment 19 sub-scope (1-I) (§결정 1 layer 1 sub-scope (1-I) 신설 pre-spawn-prompt-finalize verify layer, worktree create 후 ~30-60s window 안 1회 추가 polling 의무 + 3-source AND aggregate verify + verified-via `pre_spawn_prompt_finalize_verified` annotation, **renumbered from Amd 18 sub-scope 1-H post CFP-1342 mid-flight collision recovery** — CFP-1342 ADR-082 Amd 18 + 1-H collision detected post-PR-#1527-open during pre-merge window, recovery via rebase on origin/main ca1c20e + renumber + 4-file cross-ref update. 4-layer temporal defense forcing function 완결 = Amd 15 pre-spawn pin + Amd 16 mid-spawn drift + Amd 18 Orchestrator §10 source-claim + Amd 19 pre-spawn-prompt-finalize)
  - `docs/adr/ADR-RESERVATION.md` — `amendments_reserved[]` 3-row pre-claim append (ADR-073 Amd 13 + Amd 14 + ADR-082 Amd 19, CFP-FU-A carrier active status, ADR-082 Amd 17 §결정 1-G strict pre-claim mandate 정합; CFP-1342 Amd 18 row preserved upstream of our Amd 19 row post-collision-recovery)
  - `CLAUDE.md` — verify-before-trust 4-layer 단락 (line 282) 1-line cross-ref append (CFP-FU-A 3-Amendment paired carrier + axis disjoint complement 3-set + 4-layer temporal defense forcing function 완결 + 12th meta-occurrence collision recovery, CFP-506 line cap 정합)

### Sentinel evidence (CFP-FU-A escalate_user 11 reach)

| # | Story | 발생 | Resolution |
|---|---|---|---|
| 1 | CFP-953 | label-based search miss → memory rule 6 신설 (title-based search 의무) | reactive |
| 2 | CFP-946 | Epic close miss → memory rule 7 신설 (Epic state polling 의무) | reactive |
| 3 | CFP-949 | sub-issue scope polling gap → rule 7 refinement | reactive |
| 4-10 | (다수) | various race window incidents | partial preventive (Amd 2/3/4/5) |
| 11 | CFP-1420 Sub-A S1.2 | PR #1442 STAND_DOWN_DUPLICATE per #1441 prior merge | escalate_user mandate (본 CFP-FU-A carrier) |
| 12 META | CFP-FU-A self | CFP-1342 ADR-082 Amd 18+1-H collision detected post-PR-#1527-open during pre-merge window (recursive dogfooding evidence for #1476 sub-decisions 1+2+3 race window 영역 직접 reproduce: T0 worktree create → T1 spawn prompt finalize → T2 ArchitectAgent commit → ~30-60s gap → T3 CFP-1342 merge → T4 PR #1527 open → T5 collision → T6 recovery) | recovery via rebase on ca1c20e + renumber Amd 18→19 + 1-H→1-I + 4-file cross-ref update |

11 occurrences + 12th meta-occurrence (in-flight collision recovery) ≫ threshold 2 = ADR-045 §D-9 Mandatory escalation. 본 carrier = preventive + reactive 4-layer 완결.

### Out of scope (별 follow-up CFP carrier)

- **Wave 2 mechanical wire** (lint script + workflow yml hydrate + bats fixture + label-registry MINOR + evidence-checks-registry entry) — 별 sub-CFP carrier 분리 (CFP-1437/1436/1435 → CFP-1489/1500/1497/1502 Wave 2 precedent 답습):
  - `pre-git-operation-sentinel-pickup` lint + workflow + bats
  - `pre-push-sentinel-pickup` lint + workflow + bats
  - `parallel-work-sentinel-and-aggregate` (`scripts/lib/check_parallel_work_sentinel.py` 신규 `--mode all-and` choice 추가 + 3-mode invoke + AND aggregate logic)
  - `pre-spawn-prompt-finalize-verify` lint + workflow + bats (sub-scope 1-I, renumbered from 1-H post CFP-1342 mid-flight collision recovery)
- **lane plugin agent md cross-ref** (codeforge-pmo GitOpsAgent.md / codeforge-design ArchitectAgent.md / 8 lane plugin PL agent file) — follow-up defer (wrapper-only ADR-010 sibling sync 면제)
- **plugin.json version bump** — 본 PR = doc-only fast-path (ADR-054), additive governance behavior ratchet 강화. marketplace_sync_required: false (mirrored field 변경 0건)
- **marketplace.json sibling sync** — N/A (plugin.json 변경 0건)

### Bump rationale

- doc-only fast-path (ADR-054) — Wave 1 declaration-only behavioral mandate, src/tests 변경 0건
- plugin.json bump 0 = MINOR ratchet 강화 governance behavior 영역 (Amd 13/14/18 모두 closed_enum ratchet 강화 + sub-scope 신설, additive only)
- next release tag = 별 carrier 결정 (본 PR = [Unreleased] entry only)

## [6.7.2] - 2026-05-25

### Changed

- [CFP-1477-FU-B] **wrapper plugin.json description — short-form re-write (60KB → 217 bytes, 99.6% reduction)** (pre-existing main drift 2-defect atomic cleanup: defect 2 description-verbatim + defect 3 marketplace-parity, scope narrowed from CFP-1477 5-defect to 2-defect per RequirementsPL synthesis + 사용자 Option A 채택)
  - `.claude-plugin/plugin.json` — `description` 60KB changelog accumulation 폐기 → canonical short-form 217 bytes (UTF-8, 128 chars). wording SSOT = CLAUDE.md L9 본질 정의 (CFP/ADR cross-ref 제거 — description field 안 governance internal reference noise leak 회피, JSON string convention 정합). npm convention ≤200 char near-aligned. CHANGELOG.md SSOT 정합 (changelog history = CHANGELOG.md monopoly, description field duplication 제거)
  - `.claude-plugin/plugin.json` — `version` 6.7.1 → 6.7.2 PATCH (ADR-037 §결정 1(a) additive only, no API/contract surface change, mirrored field cleanup governance 영역)
  - `(cross-repo)` `mclayer/marketplace/.claude-plugin/marketplace.json` — `plugins[name=codeforge]` block `description` byte-identical mirror + `version` 6.7.1 → 6.7.2 sibling sync (ADR-063 §결정 1 3-file atomic invariant + §결정 2 ordering: marketplace 선행 merge → wrapper merge)
  - `docs/cross-repo-patches/cfp-1477-fu-b-marketplace-sync.patch.txt` (신규) — marketplace.json patch content draft worktree-saved evidence (Orchestrator cross-repo PR open 시 verbatim 사용)

### Scope narrowed (RequirementsPL synthesis + 사용자 Option A 채택)

- Issue #1477 의 5 defect 중 2 defect (defect 2 description-verbatim + defect 3 marketplace-parity) 만 본 PATCH bump scope. 나머지 3 defect (sister carrier overlap or stale origin):
  - defect 1 (wording-dictionary CLAUDE.md L276 `pin`) → #1061 ADR escalation (Mandatory, pattern_count 21+) + CFP-1510 macro label Wave 2 hydrate
  - defect 4 (evidence-registry-naming) → CFP-1336 sister CLOSED + 별 carrier candidate (workflow file create scope, 1 VIOLATION + 25 advisory = ADR-060 §결정 20 explicit allowlist Conservative no-rename)
  - defect 5 (inter-plugin-drift) → #815 LOW + 별 carrier for v4.10/v4.11 canonical sibling sync gap
- pattern_count escalation marker (Story §10 + ADR-045 §D-9 cross-ref): partial 2/5 cleanup, 3/5 sister-deferred

### Out of scope (별 follow-up CFP carrier)

- 5 sibling plugin (codeforge-develop / -design / -test / -pmo / -requirements) review-verdict-v4 v4.9 → v4.11 sibling sync sweep (defect 5 sub-domain)
- ADR-064 Amendment 6 wording-dictionary lint inline-detect refinement (defect 1 root cause potential, #1061 owner)
- macro label CFP-1510 Wave 2 hydrate (`if: false` 제거 + event trigger wire)
- description field 60KB accumulation pattern 자체 refactor (예: `description.short` + `description.long` split) — 별 governance Story

### Bump rationale

- description short-form cleanup (60KB → 217 bytes) + marketplace sibling sync (cross-repo PR pair) atomic
- ADR-037 §결정 1(a) — additive only, no API/contract surface change, no agent behavior change, no script logic change
- PATCH bump 6.7.1 → 6.7.2 (mirrored field cleanup governance 영역 = PATCH, MINOR/MAJOR 영역 외)

## [6.7.1] - 2026-05-24

### Added

- [CFP-1353-FU] **mega-sweep — 11 FU-CFP batch** (Epic CFP-1353 follow-up backlog closure, security hardening + collector cleanup + agent guardrail codify)
  - **Story A — collector/script cleanup (4 items)**
    - [#1458] A1 — `scripts/lib/measure_429_incident.py` `_coerce_int` / `_coerce_str_safe` defense-in-depth guards on regex-captured scalars (numeric range + whitelist string), `[A1-guard]` stderr message on malformed marker rejection. Current `\d+` regex pre-filters, but guards future-proof marker schema widening.
    - [#1459] A2 — `scripts/lib/measure_429_incident.py` cross-platform exclusive file lock (`fcntl.flock`/`msvcrt.locking` via `_ExclusiveFileLock` ctx mgr) + `_atomic_write_text` (tmp + `os.replace`) for JSONL append race / TOCTOU; `templates/github-workflows/429-incident-telemetry.yml` auto-PR branch uniqueness (PID suffix + remote pre-check + `--force-with-lease` push)
    - [#1460] A3 — `datetime.utcnow()` deprecation sweep verify: 0 occurrence across entire worktree (`scripts/`, `templates/`); collector already uses `datetime.now(timezone.utc)`
    - [#1461] A4 — `templates/github-workflows/429-incident-telemetry.yml` heredoc interpolation defensive guards: sanitize-then-interpolate pattern (3 heredocs at L144/L200/L281), strip backticks (`) and `$` from all interpolated variables (`WINDOW_KEY_SAFE`/`CASCADE_COUNT_SAFE`/`KPI_JSON`/`KPI_SUMMARY`/`REASONS_SAFE`/`RUN_URL_SAFE`) before unquoted `<<EOF` blocks. Cannot use `<<'EOF'` because body needs variable expansion.
  - **Story B — Windows wrapper hardening (6 items)**
    - [#1463] B1 — XML XmlReaderSettings DtdProcessing.Prohibit sweep verify: `scripts/install-codeforge-resume.ps1` already applied (CFP-1355 FIX iter 2); `scripts/codeforge-session-resume.ps1` Toast XML uses `Windows.Data.Xml.Dom.XmlDocument` (WinRT type, inherently XXE-safe by API design, no DTD/entity resolution) + `[int]` coerce defense-in-depth on `$MaxRetryCount`. Sweep audit conclusive: 0 XmlReader-replaceable sites remain.
    - [#1464] B2 — `scripts/codeforge-session-resume.ps1` File ACL inclusive: user + Administrators + SYSTEM `:F` grant (preserves SCCM/AV scanning + Admin recovery + service-account writes) with `.acl-set` marker idempotency guard (avoids re-ACL on every 10-min Task Scheduler poll)
    - [#1465] B3 — `scripts/codeforge-session-resume.ps1` TOCTOU symlink reject: `Get-Item -LiteralPath` + `LinkType` check rejects SymbolicLink/Junction/HardLink reparse points before UUID file read; `System.IO.File::ReadAllText` for atomic read (avoids `Get-Content` cmdlet pipeline race window between Test-Path and Get-Content)
    - [#1466] B4 — `scripts/codeforge-session-resume.ps1` `Write-Log` control char strip: CR/LF/TAB replaced with space, all C0 (0x00-0x1F) + DEL (0x7F) replaced with `?` (prevents log forging via embedded newlines)
    - [#1468] B5 — `scripts/codeforge-session-resume.ps1` `Write-Log` secret redaction regex array: extends sk-ant-* coverage to ghp_*, github_pat_*, `Bearer <token>`, `Authorization:` / `x-api-key:` headers, AWS access key ID prefix (AKIA...). Array-driven (`$secretPatterns`) for future extensibility.
    - [#1469] B6 — `scripts/codeforge-session-resume.ps1` Mutex namespace `Global\` opt-in via `$env:CODEFORGE_MULTI_USER=1` (multi-user host / Citrix / RDS protection). Default `Local\` (current per-session behavior preserved).
  - **Cross-Story B7**
    - [#1470] B7 — `docs/agent-prompt-guardrails.md` (new SSOT) — agent spawn prompt FIX-only directive codify: `[USER-UTTERANCE-VERBATIM]` block 4-invariant (opening/closing marker pair + trailing `DO NOT re-interpret` directive + `EXECUTE ONLY` token) + agent self-guard 4-step (carrier source recognition, scope confinement, no self-escalation, conflict escalate) + FIX-only directive 3 token vocabulary. Declaration-only Wave 1 (mechanical lint =별 sub-CFP carrier). cross-ref ADR-082 §결정 1 layer 1 sub-scope (1-C) + ADR-071 §결정 17 + ADR-039 + ADR-064 §결정 9/10.

### Out of scope (별 follow-up CFP carrier)

- **mechanical lint for USER-UTTERANCE-VERBATIM block** (`scripts/check-user-utterance-verbatim-block.sh` opening/closing marker pair + scope-redirect 어휘 ban heuristic) = 별 sub-CFP carrier, declaration-only Wave 1.
- **agent file template 갱신** (각 lane plugin PL agent file self-guard 본문 추가) = cross-plugin `sibling sync` carrier (ADR-010 §결정 1 정합).
- **review-verdict-v4 schema field** (`user_utterance_verbatim_block_present: bool`) = CFP scope 외 (Wave 1 declaration-only).
- **ADR-065 mechanical lint** (`scripts/check-mechanical-self-check-evidence.sh` + evidence-checks-registry entry + workflow yml) = 별 sub-CFP carrier (ADR-082 §결정 6 retain pattern, declaration-only Wave 1 from CFP-1462 Amendment 5).
- **marketplace.json `sibling sync`** (mclayer/marketplace repo PR, ADR-063 §결정 5 atomic invariant) = wrapper PR merge 직후 자동 trigger.

### Bump rationale

- 11 FU-CFP atomic batch: security hardening (B1-B6 6 items) + collector defense-in-depth (A1-A4 4 items) + agent guardrail codify (B7 doc-only)
- ADR-037 §결정 1(g) — additive behavior + Added section only, no Breaking change
- PATCH bump 6.7.0 → 6.7.1 (security fixes typically MINOR but no API/contract surface change, declaration-only doc + script internal hardening)

## [6.7.0] - 2026-05-24

### Added

- [CFP-1462] **ADR-065 Amendment 5 — 11th item post-write actual-run verify mandate** (Pattern A "chief author self-attest false claim" pattern_count 3 reach Mandatory escalation, ADR-045 §D-9 / CFP-1353 retro)
  - `docs/adr/ADR-065-architect-phase1-mechanical-self-check.md` — frontmatter `amendments[]` entry 5 + `mechanical_enforcement_actions[]` `mechanical-self-check-evidence-presence` entry append (deferred-followup, declaration-only Wave 1) + `related_stories` CFP-1462 + `related_adrs` ADR-067 cross-ref + 본문 §결정 1 표 row 11 + §결정 10 narrative section (10 sub-section: 동기 / row 11 schema / verify_method enum 4종+확장 / claim mismatch verdict reject / mechanical 자동 검출 deferred / ADR-082 §결정 1 layer 1 sister carrier / row 1-10 본문 변경 0 invariant / META self-application first applied case / sunset_justification family 정합)
  - `CLAUDE.md` — ADR-065 inline description 에 Amendment 5 clause 추가 (11th item post-write actual-run verify mandate, Pattern A pattern_count 3 reach Mandatory escalation)
  - `.claude-plugin/plugin.json` — version 6.6.2 → 6.7.0 MINOR (ADR-037 §결정 1(h) — additive amendment + chief author 검증 의무 `ratchet` 10→11 = governance behavior change)

### Pattern A lineage evidence (CFP-1353 retro)

- (a) ArchitectAgent chief Phase 1 self-attest divergence (Phase 1 first occurrence): 6 self-check `true` self-attest vs worker re-verify 3 field (`mechanical_self_check_passed` / `dimensional_empirical_self_check_passed` / `audit_gate_pointer_self_check_passed`) partial/false
- (b) InfraEng Phase 2 FIX iter 1 false self-attest (second occurrence): `tests_passed: "19/19 bats GREEN"` vs actual run `10/27 (17 FAIL)` 17-test divergence
- (c) PMOAgent retro file Write claim vs Windows filesystem persistence 0 (third occurrence): "347 lines written" claim vs filesystem actual file 부재 → Orchestrator inline write fallback

3 lineage = `chief_author_self_attest_false_claim` pattern_count 3 reach Mandatory escalation (ADR-045 §D-9).

### Out of scope (별 follow-up CFP carrier)

- **mechanical lint 자동 검출** (`scripts/check-mechanical-self-check-evidence.sh` + evidence-checks-registry entry append + warning tier workflow yml) — declaration-only Wave 1 (ADR-082 §결정 6 retain pattern). status 승격 trigger = 별 sub-CFP merge 시점 (`deferred-followup` → `warning` → `blocking-on-pr`).
- **marketplace.json `sibling sync`** (mclayer/marketplace repo PR, ADR-063 §결정 5 atomic invariant) — wrapper PR merge 직후 자동 trigger.
- **review-verdict-v4 schema MINOR bump** — `actual_run_output` / `verify_method` / `count_summary` optional field 신설 별 carrier (cross-plugin `sibling sync` 필요, 본 Amendment scope 외).

## [6.6.2] - 2026-05-24

### Added

- [CFP-1355-Phase2] **Windows external session auto-resume wrapper** (OS-level rate-limit recovery post-session-dead)
  - `scripts/codeforge-session-resume.ps1` — PowerShell wrapper SSOT (ADR-110 §결정 1-10 `normative` codify): UUID abstraction (`%LOCALAPPDATA%/codeforge/last-session.txt` read), rate-limit detection (`claude --print "noop"` + `anthropic-ratelimit-unified-5h-reset` epoch parse), Task Scheduler trigger mutation (`schtasks /Change`), session resume invoke, ghost-session prevention (mutex Local\CodeforgeResumeWrapper), retry counter + Windows Toast fallback (ADR-110 §결정 9), log rotation (90-day retention + secret redaction `sk-ant-***`), platform explicit abort (Linux/macOS non-support + non-zero exit)
  - `scripts/install-codeforge-resume.ps1` — consumer install script (idempotent): wrapper copy to `%ProgramFiles%/codeforge/`, ACL enforcement, Task Scheduler XML template import via `Register-ScheduledTask`
  - `templates/scheduler/codeforge-auto-resume.xml` — Task Scheduler job XML template (schema 1.2, Windows 10 1809+ baseline): 10-minute polling interval, 30s execution timeout, 3-retry RestartOnFailure, InteractiveToken LogonType (no stored credential), task path `\codeforge\`
  - `docs/consumer-guide.md §1j` (신설) — Windows-specific auto-resume install + activation + fidelity test 4-source measurement (ADR-110 §결정 7 empirical gate)
  - `CLAUDE.md` — OS-level external session auto-resume cross-ref (1 줄) + line-cap ≤ 320 유지
  - `docs/orchestrator-playbook.md §1.1 0ii` — Windows auto-resume wrapper SessionStart hook context append (1 줄)
  - `.claude-plugin/plugin.json` — version 6.6.1 → 6.6.2 PATCH (ADR-110 external wrapper governance layer codify + consumer adoption protocol ADR-027 extension)

### Out of scope (별 follow-up CFP carrier)

- **Phase 2 empirical fidelity test** (CFP-1355 Change Plan §3 gate): M-1 conversation context fidelity % + M-2 in-process state /4 + M-3 VS Code ↔ CLI asymmetry + M-4 UUID file path verify. gate result = pass → sub-area b/c/d 병렬 진입 / partial → Partial wrapper scope / fail → sub-area b/c/d ABORT + sub-area e (ADR negative) carry-over
- **Linux/macOS bash equivalent** (ADR-110 §결정 5 Phase 2 sub-CFP carrier): systemd timer (Linux) / launchd (macOS) wrapper
- **Multi-user developer machine** (ADR-110 §결정 6 Phase 2 carrier): `project.yaml runtime.multi_user: bool` opt-in 활성, Global namespace mutex 수정
- **CFP-FU-1**: external-wrapper-ssot-boundary mechanical lint (`scripts/check-external-wrapper-ssot-boundary.sh` + evidence-checks-registry entry) — declaration-only Wave 1 (ADR-082 §결정 6 retain pattern)
- **resume-fidelity-test-evidence artifact** (`docs/kpi/resume-fidelity-history.jsonl` append-only event log) — declaration-only Wave 1, mechanical wire Phase 2 sub-CFP carrier (CFP-FU-2)
- **CFP-FU-3**: marketplace.json `sibling sync` (mclayer/marketplace repo PR, ADR-063 §결정 5 atomic invariant) — Orchestrator decision lane (Marketplace sync lane) 영역, wrapper PR merge 직후 자동 trigger

## [6.6.1] - 2026-05-24

### Added
  - [CFP-1354-Phase2] **in-process Anthropic infra 429 surgical mitigation framework Phase 2 implementation**
    - `docs/kpi/429-incident.json` — 주간 집계 KPI artifact (schema_version 1.0, weekly_incident_count / cascade_incidents / gate_status)
    - `docs/kpi/429-incident-history.jsonl` — append-only event log (ADR-109 §결정 10 secret redaction matrix)
    - `templates/github-workflows/429-incident-telemetry.yml` — weekly cron telemetry (cascade alert + infra error Issue auto-open)
    - `scripts/check-429-retry-evidence-presence.sh` — lint §14 Lane Evidence marker (warning-tier deferred-followup)
    - `scripts/check-debate-parallel-cap-check.sh` — lint team-spec parallel_spawn_cap field
    - `scripts/check-deputy-stagger-check.sh` — lint team-spec spawn_stagger_ms field
    - `templates/team-spec-*.yaml` 7 files — 3 신규 필드 (parallel_spawn_cap / spawn_stagger_ms / cascade_circuit_breaker, default values)
    - `docs/inter-plugin-contracts/label-registry-v2.md` — v2.54 → v2.55 MINOR (3 entries: severity:429-cascade + hotfix-bypass:429-retry-evidence-presence **76번째** + hotfix-bypass:debate-parallel-cap-check **77번째**)
    - `docs/evidence-checks-registry.yaml` — 3 신규 entry (429-retry-evidence-presence / debate-parallel-cap-check / deputy-stagger-check)
    - `docs/inter-plugin-contracts/MANIFEST.yaml` — label-registry-v2 version 2.54 → 2.55


- [CFP-1334-Phase2] **bats fixture RED→GREEN proof presence lint mechanical wire** (Phase 1 #1374 declaration-only Wave 1 → Phase 2 active warning-tier 전환)
  - `scripts/lib/check_bats_red_green_proof.py` — Python lint SSOT, 5-marker grep-presence heuristic (pre_impl_sha / git_stash_sequence / role_vocabulary / red_green_anchor / platform_verified) ≥3/5 PASS threshold (ADR-061 §결정 1 + Amendment 1 §결정 6.A external .py split)
  - `scripts/check-bats-red-green-proof.sh` — 8-line bash thin wrapper
  - `templates/github-workflows/bats-red-green-proof.yml` + `.github/workflows/bats-red-green-proof.yml` — sibling parity byte-identical (ADR-005), PR trigger on tests/**/*.bats + lint script + registry paths, hotfix-bypass:bats-red-green-proof label early exit
  - `tests/scripts/check-bats-red-green-proof/test_check_bats_red_green_proof.bats` — **META self-app dogfood closing-the-loop** (memory `feedback_meta_self_application_pattern` 정합). 5 TC: TC-1 discriminating (high-marker fixture PASS) + TC-2 regression_guard (zero-marker fixture WARN) + TC-3 bootstrap (empty argv no-files exit 0) + TC-4 META self-app (lint applied to THIS fixture = PASS 5/5 markers) + TC-5 bypass-env (skip placeholder). pre_impl_sha = 7afcebb (Phase 1 merge commit, pre-Phase-2 HEAD). RED→GREEN stash proof manual reproduction sequence 명시 (git stash push --include-untracked → bats run → expect TC-1+TC-4 FAIL → git stash pop → 5/5 PASS).
  - `docs/evidence-checks-registry.yaml` — entry `bats-red-green-proof-presence` status `deferred-followup` → `warning` direct 전환 + detect_command + workflow populated (Phase 1 squash merge entry append loss 흡수, Phase 2 active state 직접 declare)
  - `CHANGELOG.md` — 본 entry [6.6.1]
  - `.claude-plugin/plugin.json` — version 6.6.0 → 6.6.1 PATCH (ADR-037 (a) — mechanical lint coverage 확장 = plugin behavior 변경)

### Out of scope (별 follow-up CFP carrier)

- **CFP-FU-1**: CFP-1302 retroactive 33 TC RED→GREEN proof 부착 (test_phase_gate_mergeable_yml.bats 13 + test_phase_gate_auto_cleanup_yml.bats 20)
- **CFP-FU-2**: ADR-061 Amendment 3 bats 영역 확장 검토 (axis 정합, pattern_count ≥ 2 reach 시)
- **CFP-FU-3**: ADR-068 Amendment 4 (I-7) 또는 ADR-082 Amendment N (Phase 2 evidence 누적 후)
- **CFP-FU-4**: marketplace_sync strict invariant (ADR-063 §결정 21 Amendment carrier, version-only bump 시 마켓플레이스 동시 sync 결정 룰 명문화)

## [6.6.0] - 2026-05-24

### Added

- [CFP-1334] **bats fixture RED→GREEN stash proof pattern + TestContract deputy mandate codification** (CFP-1302 retro F4 deferred carrier, CodeReviewPL F-CR-1302-2 P2 follow-up)
  - chief tie-break ladder 3 단계 적용 (Step 1 RACI lookup `skills/deputy-mandate/SKILL.md` L80 TestContractArchitectAgent §8 → Step 2 ADR-068 6/6 invariant axis mismatch (design-level vs test-authoring scope) → Step 3 chief judgement + ADR-086 5-checklist self-app 5/5 PASS) → **Option C convergence** (declaration-only Wave 1, ADR 신설 0건)
  - 3-packet deputy advocacy convergent: TestContractArch (Option D primary = Option C 의미적 alias) + ArchitectAnalyst (Option C primary + F-AA-1334-01 ADR-082 §결정 7 per-area 분할 거부 invariant Option B 직접 차단) + CodebaseMapper (0 finding, fact enumeration — 67 bats files / 103 evidence-checks-registry entries / ADR-068 amendment_max 3 / ADR-082 amendment_max 7 / ADR-061 amendment_log max 2)
  - `templates/impl-manifest.md` — `bats_fixtures[]` field + `red_green_proof_evidence_artifact` nested object schema (method 3-enum + pre_impl_sha + assertion_classification[] role 3-enum + platform_verified 5-enum + null_reason 4-enum, ADR-068 I-2 cross-module propagation completeness directly-analogous + I-3 unconditional vs conditional guard placement intent pattern verbatim 답습)
  - `skills/deputy-mandate/SKILL.md` — TestContractArchitectAgent mandate body 갱신 (L80 row + RACI matrix L115 §8.5 discriminating fixture mandate row append, append-only — ModuleArch/DataArch/APIContractArch/SecurityArch/InfraOperationalArch row 변경 0)
  - `docs/domain-knowledge/domain/test-discipline/red-green-stash-proof-pattern.md` — narrative SSOT first entry (codeforge governance 어휘 promotion 첫 사례, memory `feedback_tdd_red_proof_via_stash` 일반화)
  - `docs/evidence-checks-registry.yaml` — `bats-red-green-proof-presence` warning-tier deferred-followup entry append (owner_adr=ADR-060 / carrier_adr=ADR-060, declaration-only Wave 1 → Phase 2 mechanical wire 후 warning 전환)
  - `docs/parallel-work/section-ownership.yaml` — 4 row append-only (templates/impl-manifest.md + skills/deputy-mandate/SKILL.md + docs/evidence-checks-registry.yaml + docs/domain-knowledge/domain/test-discipline/), CFP-1085 sibling collision 회피 (ADR-068 amendments[] touch 0건 — Option C convergence 정합)
  - `.claude-plugin/plugin.json` — version 6.5.2 → 6.6.0 MINOR + description CFP-1334 entry prepend (ADR-037 (b) governance behavior 확장 — TestContract deputy mandate scope expansion)
  - `CHANGELOG.md` — 본 entry

### Out of scope (별 follow-up CFP carrier)

- **Phase 2 mechanical wire** (CFP-1334 self-carrier 별 PR): `scripts/check-bats-red-green-proof.sh` + `scripts/lib/check_bats_red_green_proof.py` (ADR-061 Amendment 1 §결정 6 thin wrapper) + `templates/github-workflows/bats-red-green-proof.yml` + `.github/workflows/bats-red-green-proof.yml` (sibling-parity byte-identical) + `tests/scripts/check-bats-red-green-proof/test_check_bats_red_green_proof.bats` (META self-app closing-the-loop)
- **CFP-FU-1**: CFP-1302 retroactive 33 TC RED→GREEN proof 부착 (test_phase_gate_mergeable_yml.bats 13 TC + test_phase_gate_auto_cleanup_yml.bats 20 TC, Priority HIGH/MID)
- **CFP-FU-2**: ADR-061 Amendment 3 bats 영역 확장 검토 (axis 정합 영역 재검토, pattern_count ≥ 2 reach 시)
- **CFP-FU-3**: ADR-068 Amendment 4 (I-7 discriminating-fixture invariant 신설) 또는 ADR-082 Amendment N (sub-scope-e), Phase 2 evidence 누적 + pattern_count ≥ 2 reach 후
- **CFP-FU-4**: marketplace_sync strict invariant — version-only bump 시 marketplace_sync_required 결정 룰 명문화 (ADR-063 §결정 21 Amendment carrier, F-PL-1334-02 P2 + F-DR-1334-03 P2 advisory source)
- Python pytest / Node jest 영역 RED→GREEN proof (language-agnostic pattern, cross-platform stash 검증 별 axis)

## [6.5.2] - 2026-05-23

### Changed

- [CFP-1312] **ADR-082 Amendment 7 — §결정 9 verify-before-cite scope 양방향 확장 + CFP-1216 lint Check (b) backward-staleness wire** (dual-carrier, ADR-045 §D-9 pattern_count 3 reach Mandatory escalation 산물)
  - `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` Amendment 7 신설: frontmatter amendments[] / amendment_log[] entry 7 append + §결정 9 wording 양방향 확장 (forward only → forward + backward, `M = max+1` 정확 next-slot 외 모두 stale) + Amendment 7 본문 section append + related_stories CFP-1312/CFP-1293/CFP-1216 append
  - `scripts/lib/check_amendment_number_stale.py` Check (b) `cited_m != max_id + 1` 양방향 비교 확장 + `[FORWARD-STALE]` / `[BACKWARD-STALE]` label format 분리 + `_is_template_path()` FP-완화 guard 2 (templates/** path filter — canonical example 면제)
  - `tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats` 양방향 staleness TC 6 신설 (TC-B-BWD-EXACT / TC-B-BWD-DEEP / TC-B-FWD-EXACT-NEXT / TC-B-FWD-LABEL / TC-B-TEMPLATE-EXEMPT / TC-B-SELF-REF-EXEMPT) + 기존 TC-B2 expected output 정정 (Amendment 7 wording 정합 — M=2, max=3 → BACKWARD-STALE)
  - `docs/evidence-checks-registry.yaml` `amendment-number-frontmatter-verify` entry description Check (b) 양방향 staleness codify + sibling_dependencies CFP-1312 append + extended_by CFP-1312 + last_extended_date 2026-05-23 + last_updated header CFP-1312 prepend (status warning retain, scope expand only)
  - `docs/adr/ADR-RESERVATION.md` amendments_reserved[] row append (ADR-082 Amendment 7 reserved → active 직접 전환, ArchitectPL chief author precedent — sibling pattern ADR-083 Amendment 3 CFP-1293)
  - `docs/parallel-work/section-ownership.yaml` 7 entry append (ADR-082 Amendment 7 + scripts/lib/check_amendment_number_stale.py + bats fixture + evidence-checks-registry + ADR-RESERVATION + plugin.json + CHANGELOG)
  - pattern_count 3 reach (CFP-1177 forward + CFP-1179 forward + **CFP-1293 backward** ADR-083 Amendment 2 with max=2) ≥ ADR-045 §D-9 threshold 2 Mandatory escalation
  - root cause = Wave 1 behavioral 단독 불충분 아닌 Wave 2 mechanical lint Check (b) `M > max+1` forward-only coverage gap 으로 backward-staleness escape — Amendment 7 = 양방향 wire 보강
  - is_transitional: false retain (permanent governance policy, `ratchet` 강화 방향: forbid scope 확장 `M = max+1` 외 모두 stale, ADR-058 §결정 5 sunset_justification "N/A — `ratchet` 강화 방향")
  - dual-carrier (axis 동일, ADR-064 §결정 1 CFP scope unitary 정합): wording 보강 + lint coverage gap 보강
  - PATCH bump 6.5.1 → 6.5.2 (ADR-037 (a) — mechanical lint coverage 확장 = plugin behavior 변경, ADR-063 §결정 1 marketplace `sibling sync` 의무 동반)

## [6.5.1] - 2026-05-23

### Changed

- [CFP-1293] **walker apply Stage D ADR-083 consumer-applicability filter wire 실 구현** (Phase 2, FIX iter 1+2 통합)
  - `scripts/lib/walk_plan.py` section (h) +121 LOC: `FilterDecision` frozen dataclass + `apply_consumer_applicability_filter()` + `invoke_detect_repo_kind()` 3 신설
  - `scripts/lib/walk_plan.py` section (i) +149 LOC (FIX iter 2 — CodeReviewPL F-CR-001 P1 해소): `WalkStageAbortError` + `ApplyChangelogEntryResult` + `apply_changelog_entry()` caller (Step D.1 filter → Step D.2 apply_overlay_file 실 wire)
  - ADR-083 §결정 5 4-way truth-table 실 wire: plugin/mixed → proceed (wrapper self-app exemption), consumer → positive whitelist filter, unknown → fail-closed abort
  - `tests/scripts/cfp-1293/test_walker_filter.py` 신설 (TDD Python, 15 TC GREEN)
  - `tests/scripts/cfp-1293/walker-filter.bats` 신설 (bats integration, 23 TC GREEN — TC-INT-WIRE-CONSUMER + TC-INT-WIRE-WRAPPER 2 신규)
  - ADR-083 Amendment 3 §결정 5 wire location expand 3 영역 atomic codify (reconcile-overlay.sh 기존 + walk_plan.py 신규 + UpgradeAgent.md R-3) realization
  - β2 audit (#1113 Anchor 2) declared LOSSLESS ↔ walk_plan.py 안 wire 0 match drift catch evidence-based — sunset_justification 강화 (carrier-preserved sunset ADR-097 §결정 3 정합, `ratchet` 강화 방향 evidence ADR-058 §결정 5 CFP-1149 symmetric evidence-gate 정합)
  - #1268 결함 2 paradigm-aware 정정 carrier (defect 1 = #1294 reservation, paradigm migration super-class)
  - PATCH bump 6.5.0 → 6.5.1 (CFP-1303 6.5.0 위 catch-up rebase, ADR-037 (a) Phase 2 code-only)

## [6.5.0] - 2026-05-23

### Changed

- [CFP-1303] **review-verdict-v4 `sibling sync` v4.8 → v4.9 MINOR** — CFP-604 retro F7 Wave 2 carrier (Wave 1 [CFP-1291](https://github.com/mclayer/plugin-codeforge/issues/1291) prose-only anchor 위 schema layer codify).
  - `findings[].parallel_anchors_checked` optional array field 신설 (additive backward-compat — `findings[].anchor_id` v4.1 pattern 답습)
  - 각 entry = `{file_line: string, pattern_type: enum 5종 closed-set, matched: bool}`
  - `pattern_type` 5종 enum closed-set: `local_remote` (LOCAL_X ↔ REMOTE_X — CFP-604 evidence) / `client_server` (RPC 양방향) / `read_write` (file I/O 대칭) / `forward_reverse` (encode↔decode) / `enum_closure` (enum value 전수 coverage)
  - `matched: bool` = 검색 evidence 명시 (true = parallel anchor 발견, false = clean enumeration, field absent = 검색 미수행 — Wave 3 lint heuristic 영역)
  - **ADR-068 I-2 cross-module propagation completeness 의 review-verdict layer realization** (micro-scale parallel form, semantic anchor — propagation matrix module-level vs `parallel_anchors_checked` finding-level disjoint axis)
  - **Trigger evidence**: CFP-604 F-CR-604-2 (LOCAL_AUTHOR `check-version-bump-atomic.sh:76` jq fallback unreachable) catch 후 후속 CI 에서 REMOTE_AUTHOR `check-version-bump-atomic.sh:213` (동일 root cause jq object/scalar handling) 미catch 발견 → continuation commit `85b6042` 필요. pattern_count 2 evidence.
  - **Wave 1 → Wave 2 → Wave 3 layered architecture**: Wave 1 prose anchor (CFP-1291 MERGED 2026-05-23 09:23 KST codeforge-review #42) / Wave 2 schema codify (본 CFP-1303) / Wave 3 mechanical lint presence-grep heuristic (deferred-followup, 별 carrier)
  - 적용 lane: **CodeReviewPL** (primary) — Wave 1 CFP-1291 본문 정합 / **DesignReviewPL** + **SecurityTestPL** (optional)
  - verdict-level boolean field 신설 0건 — `mechanical_self_check_passed` / `boundary_completeness_self_check_passed` / `dimensional_empirical_self_check_passed` / `audit_gate_pointer_self_check_passed` / `deputy_axis_restructure_self_check_passed` 5 verdict-level boolean 과 disjoint axis (anchor_id pattern 답습 finding-level array)
  - ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합. Runtime impact 없음 (기존 v4.8 consumer 가 본 신규 field 무시 가능 = backward-compat invariant)
  - CFP-1117-S4 wrapper `sibling sync` precedent 답습 (canonical + wrapper atomic, 5 other lane plugin sweep [requirements / design / develop / test / pmo] = 별 follow-up CFP — CFP-1167 precedent)
  - `mirrored field`: 6.4.6 → 6.5.0 MINOR (additive contract field per ADR-037 — governance behavior 확장). Marketplace `sibling sync`.

### Files touched
- `docs/inter-plugin-contracts/review-verdict-v4.md` (wrapper sibling) — v4.8 → v4.9 MINOR (frontmatter version + related_adrs ADR-068 cross-ref append + authors CFP-1303 entry + amendment_log v4.9 entry + findings[] schema block parallel_anchors_checked field + §16 신설 cross-anchor parity check enumeration section)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — review-verdict-v4.md contract_version 4.8 → 4.9 + CFP-1303 row comment append
- `.claude-plugin/plugin.json` — version 6.4.6 → 6.5.0 + description CFP-1303 entry prepend
- `CHANGELOG.md` — 본 entry

### Out of scope (별 follow-up CFP carrier)
- **Wave 3 mechanical lint**: `parallel_anchors_checked` field presence-grep heuristic on finding emit (deferred-followup, ADR-064 §결정 1 scope unitary)
- **5 other lane plugin sibling sweep** (requirements / design / develop / test / pmo v4.8 → v4.9 mirror): CFP-1167 precedent 답습 — 별 follow-up CFP

## [6.4.6] - 2026-05-23

### Changed

- [CFP-1289] **MANIFEST.yaml deploy_output / deploy_review_output entries status Draft → Active** (CFP-604 retro F5 follow-up realized, minimum-viable scope).
  - declarative-only Phase 1 placeholder alignment: MANIFEST.yaml entry status (Draft) ↔ contract file frontmatter status (Active) 간 drift 해소
  - `deploy-output-v1.md` (CFP-1059 / ADR-087) line 5 `status: Active` 와 MANIFEST entry status 정합
  - `deploy-review-output-v1.md` (CFP-1059 / ADR-088) 동일
  - `inter-plugin-drift` lint (CFP-E) Active|Archived membership 충족 → CFP-1059 family scope future PR 의 baseline drift 부담 해소
  - actual schema body wire = **multi-session Epic deferred** — CFP-1059 S2 (codeforge-deploy plugin seed) + S3 (codeforge-deploy-review plugin seed) sub-Story carrier 영역
  - `mirrored field`: 6.4.5 → 6.4.6 PATCH. Marketplace `sibling sync`.

## [6.4.5] - 2026-05-23

### Changed

- [CFP-1290] **phase-gate-mergeable workflow summary multi-gate display 개선** (CFP-604 retro F6 follow-up realized, minimum-viable). CFP-604 incident: PR phase 전환 후 prior gate label (예: `gate:design-review-pass`) 잔존 + new gate (예: `gate:security-test-pass`) 미부착 시, singular `gateLabel` 가 prior 표시 → "current=gate:design-review-pass" misleading 메시지.
  - fix: `prGateLabels.join(", ")` 으로 전체 gate label 표시 + "required gate=X MISSING" 명시 형식 변경
  - self-app mirror: templates/ + .github/ byte-identical
  - **deferred-followup**: 본 변경은 display 개선 only — workflow 의 auto-cleanup-stale-gate-label-on-phase-transition (Issue label 자동 cleanup) 또는 phase-gate-mergeable.yml 의 multi-gate matching logic strengthening 은 별 Story carrier (Wave 2 mechanical lint pattern)
  - bats fixture: deferred-followup (workflow runtime test gap, ADR-076/082/086 precedent 답습 — Wave 2 별 carrier)
  - `mirrored field`: 6.4.4 → 6.4.5 PATCH. Marketplace `sibling sync` (ADR-063 §결정 2).

## [6.4.4] - 2026-05-23

### Changed

- [CFP-1288] **wording-dictionary 카테고리 (b) baseline backfill — templates 2 file 인라인 평문 정의** (CFP-604 retro F4 follow-up realized, partial). doc-only fast-path (ADR-054 Cat 1).
  - templates/story-page-structure.md line 54 — `ratchet` 인라인 평문 정의 추가
  - templates/architecture-doc.md line 34 — `kind:contract` 인라인 평문 정의 추가
  - CHANGELOG.md historical entries: **history preservation invariant** (frozen records 수정 금지, ADR-079 forward-only 정합)
  - `mirrored field`: prev → 6.4.4 PATCH. Marketplace `sibling sync`.

## [6.4.3] - 2026-05-23

### Changed

- [CFP-1287] **CLAUDE.md diet 348 → 319 lines** (cap 320 회복, CFP-604 retro F3 follow-up realized). doc-only fast-path (ADR-054 Cat 1). 압축 5건 (semantic 손실 0 — 모든 cross-ref / ADR / CFP / SSOT reference 보존):
  - (a) CFP-1111 Wave 1 Story-2 6 ADR bundle 9-line block → 2-line inline list
  - (b) Deploy lane workflow 7 numbered list 10-line block → 1-line inline
  - (c) Sonnet rate-limit fallback 9-line section → 4-line consolidated
  - (d) phase-gate-mergeable label + CODEFORGE_CROSS_REPO_PAT 4-line dual blockquote → 1-line combined
  - (e) Branch governance + Brainstorming skill 4-line dual paragraph → 1-line combined
  - line-cap baseline drift resolution (`hotfix-bypass:claude-md-line-cap` 부담 해소). 매 PR 의 line-cap bypass 부담 제거.
  - `mirrored field`: 6.4.2 → 6.4.3 PATCH + description CFP-1287 entry append. Marketplace `sibling sync` (ADR-063 §결정 2).

## [6.4.2] - 2026-05-23

### Added

- [CFP-1286] **Codex worker fail-mode enum 8 → 9 확장 — `codex_truncated_no_verdict` 9번째 value** (CFP-604 retro F2 follow-up realized, single sample escalate_user 사용자 직접 채택). doc-only fast-path (ADR-054 Cat 2). 3-ADR trio Amendment:
  - **ADR-070 Amendment 8** (SSOT): §결정 D1 expansion fail-mode 8-set → 9-set 확장.
  - **ADR-052 Amendment 13** (cross-ref): §A3 `fallback_skip_with_marker` 표 8 → 9 enum 동기 정정.
  - **ADR-081 Amendment 7** (cross-ref): fail-mode reference 표기 9-enum 전수 정정. file-redirect ↔ stream-stall ↔ reasoning-exhausted 3 disjoint failure mode.
  - 적용 영역 = file-redirect dispatch (ADR-081 §결정 D8) 정상 invocation 후 sandbox + Windows encoding + 대용량 artifact reasoning budget 소진 → verdict 미생산.
  - `ratchet` ↑ direction (closed-enum expansion additive). `mechanical_enforcement_actions[]=[]` retain. pattern_count=1 (single sample), Wave 2 mechanical detection lint = 별 carrier.
  - `mirrored field`: 6.4.1 → 6.4.2 + description CFP-1286 entry. Marketplace `sibling sync` (ADR-063 §결정 2).

## [6.4.1] - 2026-05-23

### Added

- [CFP-1292] **ADR-061 Amendment 2 — production-scale invariant verify for bash scripts** (CFP-604 retro Mandatory F1 carrier — ADR-045 §D-9 / pattern_count 2: SIGPIPE bug + production-scale fixture gap, sibling CFP-583). doc-only fast-path (ADR-054 Cat 2 — 기존 ADR Amendment, src/tests 무변경).
  - **§결정 9 신설**: bash script 가 3-조건 AND (`set -uo pipefail` + pipe operator + 가변 size input source) 충족 시 production-scale discriminating fixture mandatory (≥ 10× isolated env size) **또는** 대안 패턴 채택 (here-string `<<<`, process substitution `< <(...)`, 명시적 pipefail 해제 구간) — `ratchet` equivalent.
  - **§결정 10 self-app**: `ratchet` ↑ direction 검증 — strengthen direction, `is_transitional: false` 보존, CFP scope unitary 정합. mechanical_enforcement_actions: [] declarative-only (Wave 1, Wave 2 mechanical lint 별 sub-Story carrier — ADR-076/082/086 precedent).
  - 적용 영역: `scripts/*.sh` + `templates/github-workflows/*.yml` step `run:` block. ADR-061 외부 `.py` split mandate (§결정 1 / Amendment 1 §결정 6.A) 와 disjoint axis (Python sys.stdin SIGPIPE 무위험).
  - 위반 처리: Phase 2 PR open 시 CodeReviewPL audit anchor (3-조건 AND grep + fixture TC enumeration verify, 미충족 시 severity P1 권장 finding).
  - `mirrored field`: version 6.4.0 → 6.4.1 + description CFP-1292 entry append. Marketplace `sibling sync` 의무 (ADR-063 §결정 2).

## [6.4.0] - 2026-05-23

### Added

- [CFP-604] ADR-063 Amendment 9 marketplace atomic-sync mechanical enforcement (Gap A + Gap B).
  - **Gap A lint** (`scripts/check-architect-marketplace-self-check.sh` + workflow 신설): plugin.json `mirrored field` 변경 PR 의 Change Plan §13 `marketplace_sync_required:` presence/completeness 검증 (ADR-063 §결정 21 / warning tier). doc-only fast-path / cross-repo dogfood-out false-positive 차단. bypass: `hotfix-bypass:architect-marketplace-self-check`.
  - **Gap B `check-version-bump-atomic.sh` 강화** (ADR-063 §결정 22): (a) gh-skip silent hole 제거 — CI 환경(`$CI=true AND $GITHUB_ACTIONS=true`) `exit 2` fail-loud 전환, non-CI `exit 0` graceful skip + stderr warning emit (조용 skip 금지). (b) Step 4 `mirrored field` 4종 확장 — name/author parity mismatch 시 `exit 1` blocking-on-pr (기존 description only → 4종 전스 coverage 완결).
  - `docs/evidence-checks-registry.yaml` `architect-marketplace-self-check` entry 신규 (warning tier, ADR-060 §결정 5). `marketplace-description-verbatim` entry description Gap B SSOT 명문화.
  - `tests/scripts/cfp-604/` bats fixture 2종 신규: `check-architect-marketplace-self-check.bats` (Gap A 5 TC) + `check-version-bump-atomic.bats` (Gap B regression 5 TC).

## [6.3.0] - 2026-05-22

### Added

- [CFP-1244] Codex worker dispatch file-redirect mandate — ADR-081 Amendment 6 (신규 §결정 D8) + ADR-070 Amendment 7 + ADR-052 Amendment 12. Codex CLI (v0.125.0) `codex exec` stdin-pipe invocation 이 TTY 부재 sandbox 안 0-byte stall (>5min) systemic 원인 — file-redirect invocation `codex exec --sandbox read-only < <promptfile>` 가 stall 회피 + genuine dual-perspective review 산출 (CFP-1187 운영 phase Epic S4/S5 early stall → substitution / S5/S6/S7 file-redirect 성공 / S7 ArchitectPL stream idle-timeout after 40 tool_uses → redo evidence).
  - `docs/adr/ADR-081-codex-worker-prompt-boilerplate.md`: Amendment 6 (6번째 amendments[] entry) — 신규 §결정 D8 Codex worker dispatch file-redirect mandate. file-redirect invocation 의무 (composed worker prompt file write 후 stdin redirect, direct stdin-pipe / inline-arg 금지) + result-via-file 수신 + Orchestrator synchronous block-wait 금지 (bounded window 초과 시 다음 step 진행 후 result file pickup). D1.A-D 4 mandatory boilerplate field 무변경 (dispatch invocation 영역, prompt field 신설 0). is_transitional false 유지, sunset_justification = additive `ratchet` 강화 (dispatch reliability hardening).
  - `docs/adr/ADR-070-codex-verify-before-trust.md`: Amendment 7 (7번째 amendments[] entry) — §결정 D1 fail-mode enum SSOT 7-set → 8-set 확장 (`dispatch_stall_or_stream_timeout` 8번째 value, Codex `codex exec` invocation stall OR Orchestrator stream idle-timeout → `fallback_skip_with_marker` path). closed-enum expansion = `ratchet` 강화 (additive, 정보 손실 0). is_transitional false 유지.
  - `docs/adr/ADR-052-codex-proactive-check-touchpoints.md`: Amendment 12 (12번째 amendments[] entry) — ADR-081 Amendment 6 file-redirect dispatch mandate cross-ref (본문 SSOT 위임) + ADR-070 Amendment 7 fail-mode enum 7 → 8 확장 cross-ref. §A3 cross-ref 표 가 Amendment 10 (`subagent_recursion_blocked` 추가) 시점 갱신 누락으로 6-stale 였던 mechanical self-check escape 도 본 carrier 에서 full 8-enum 으로 정정 (ADR-065 Amendment 4 / CFP-1242 와 동일 class). is_transitional false 유지.

### Changed

- [CFP-1244] `docs/orchestrator-playbook.md` §3.10 — Codex CLI worker check file-redirect dispatch mandate 본문 추가 (`codex exec --sandbox read-only < <promptfile>` invocation + result-via-file + synchronous block-wait 금지 + stall/stream idle-timeout 시 `fallback_skip_with_marker` substitution). Substitution scope 3-path enum 표 의 `[codex-sandbox-fallback]` fail-mode enum 7 → 8 갱신 + §3.10 step marker 영역 6-stale enum → 8 정정.
- [CFP-1244] `CLAUDE.md` — Codex Proactive Check 블록쿼트 fail-mode enum `6 종` → `8 종` (pre-existing 6-stale count 정정 — Amendment 10 `subagent_recursion_blocked` 미반영분 포함) + ADR-081 Amendment 6 file-redirect dispatch mandate cross-ref (기존 line 확장, 신규 line 0건 — line cap 정합).
- plugin.json 6.2.1 → 6.3.0 MINOR (ADR-037 §결정 1(h) — three additive ADR amendment = governance behavior change). marketplace atomic sync 별도 sibling PR 의무 (ADR-063 §결정 5, `mirrored field` version 변경).

### Cross-ref

- Issue: #1244
- ADR: ADR-081 (Amendment 6), ADR-052 (Amendment 12)

## [6.2.1] - 2026-05-22

### Fixed

- [CFP-1243] S4 producer (`scripts/check_rollback_signal.py`) enum literal conformance — `operational-signal-v1` closed `signal_type` enum drift 해소 (Option B: contract = SSOT, producer 가 conform).
  - `scripts/check_rollback_signal.py`: burn-rate 임계 초과 시 emit 하던 비정규 literal `burn_rate` → §결정 3 / `operational-signal-v1` 정규 enum value `latency_burn_rate` 로 conform (`check_safety_1` L142 string literal 1건 + docstring 출력 포맷 L30 1건, surgical). burn-rate 입력 metric 명칭 (변수 `burn_rate` / `--burn-rate` CLI flag / prose) 은 무변경 — 비정규였던 것은 emit signal_type literal 뿐.
  - `tests/scripts/cfp-1193/check-rollback-signal.bats`: TC-2 assertion 을 `signal_type=latency_burn_rate` 정확 비교 + 비정규 `signal_type=burn_rate` 출현 금지 guard 로 강화 + TC-15 contract-binding guard 신설 (producer emit non-none signal_type ∈ closed enum {error_rate, latency_burn_rate, regression, smoke_health} membership 보증 — future drift 차단). TDD RED (line 142 비정규 상태에서 TC-2/TC-15 FAIL) → GREEN (conform 후 20/20 PASS).
  - `docs/inter-plugin-contracts/operational-signal-v1.md`: `signal_type` row note 를 deferred follow-up CFP 기록 → RESOLUTION 으로 갱신 (producer 가 정규 `latency_burn_rate` emit, alias 없음). enum value / `version` frontmatter 무변경 (editorial note correction — schema/enum 변경 0, MANIFEST registries sync 불요).
  - `docs/adr/ADR-106-operational-signal-pmo-input-circuit.md`: Amendment 3 추가 (S4 producer emit literal `burn_rate` → `latency_burn_rate` conformance 기록). §결정 3 closed enum 4-value 자체는 무변경 (이미 정규). is_transitional false 유지 (corrective conformance — additive trail, strengthening, sunset_justification null).
  - plugin.json 6.2.0 → 6.2.1 PATCH (ADR-037 — enum drift 버그 fix, `fix:` commit signal; ADR-106 Amendment 3 = corrective trail, 신규 capability 0). marketplace atomic sync 별도 sibling PR 의무 (ADR-063 §결정 5, `mirrored field` version 변경).

### Cross-ref

- Issue: #1243
- ADR: ADR-106 (Amendment 3)

## [6.2.0] - 2026-05-22

### Added

- [CFP-1242] INV-1 parity lint scope 의 kind:registry 확장 + ADR-065 Amendment 4 (chief author mechanical self-check 10th item 선제-lint mandate). ADR-045 §D-9 escalate_user (pattern_count 3 — kind:registry version parity unguarded → S4 drift human review 도달).
  - `scripts/lib/check_inter_plugin_contracts_parity.py`: INV-1 parity lint 이 그동안 `manifest["contracts"]` 만 iterate (kind:registry version parity 무방비 iteration gap). 정정된 진단 — "MANIFEST 가 kind:registry 제외" 정책 exclusion 이 아니라 lint iteration gap (sibling-sync 면제 ADR-010 §결정 2 와 MANIFEST↔frontmatter parity 가 conflate). 두 섹션 (contracts: `contract_version` / registries: `version`) 모두 parity-check 하도록 확장 — Active row membership semantic (parallel-append 다중 Active row tolerant), 비-Active(Archived/Sunsetted) skip, self-ref graceful + exit code (0/1/2) 보존, 기존 7 contract check 무회귀. docstring 정정.
  - `scripts/lib/test_check_inter_plugin_contracts_parity.py`: TC-8..TC-13 registries parity 테스트 추가 (TDD RED: TC-9 live label_registry drift 재현 + TC-12 missing version field — lint 확장 전 FAIL / 후 PASS 확인, 기존 9 test 무회귀, total 15 GREEN).

### Fixed

- [CFP-1242] `docs/inter-plugin-contracts/MANIFEST.yaml` `registries.label_registry` live drift fix — frontmatter `version: "2.50"` 인데 MANIFEST 가 7개 mis-ordered "Active" row (2.43, 2.44, 2.45, 2.49, 2.48, 2.47, 2.46 = parallel-session append drift) 를 나열 (2.50 부재). 7 Active rows → single Active 2.50 row collapse (label-registry-v1 Archived row 보존, 다른 8 registry 무변경). 확장된 lint 가 BEFORE 적발 (RED) / AFTER PASS (GREEN) — 7 contracts + 8 registries 15 Active file 검증.

### Changed

- [CFP-1242] ADR-065 Amendment 4 — §결정 1 표 row 10 append (Phase 1 산출물 commit 직전 touched ADR/doc 에 `check-doc-section-schema.sh` + `check-adr-sunset-criteria.sh` 로컬 선제 실행 PASS, behavioral mandate, 운영 phase S3+ FIX 0 효과 입증) + §결정 9 narrative (corrected diagnosis + INV-1 parity kind:registry scope 확장). `mechanical_enforcement_actions[]` = 기존 `inter-plugin-contracts-parity` entry scope 확장 cross-ref only (신규 evidence-checks-registry entry 0건). is_transitional false 유지 (additive `ratchet`, ADR-058 §결정 5 sunset_justification quoted-string). CLAUDE.md ADR-065 inline description Amendment 4 clause 동반.
  - plugin.json 6.1.1 → 6.2.0 MINOR (ADR-037 §결정 1(h) — additive amendment + lint behavior change = governance behavior change). marketplace atomic sync 별도 sibling PR 의무 (ADR-063 §결정 5, `mirrored field` version 변경).

### Cross-ref

- Issue: #1242
- ADR: ADR-065 (Amendment 4)

## [6.1.1] - 2026-05-22

### Fixed

- [CFP-1241] `cross-layer-impact-check.yml` (CFP-1059 배포 lane Epic 산출) — "Enumerate touched layers" step 의 `grep | wc -l` pipefail 버그 fix. `set -euo pipefail` 하에서 grep 0-match → exit 1 → command-substitution abort → migrations/schema/src/frontend/backend 을 안 건드리는 모든 PR (대부분 docs/governance) 마다 advisory step FAILURE (warning tier, CI noise). 4 `grep | wc -l` 파이프에 `|| true` 추가 (template + `.github/workflows/` self-app byte-identical, ADR-005). 자매 워크플로 `dependency-order-check.yml` 는 이미 `|| echo ""` safe 패턴 사용 — disjoint, 무변경.
  - TDD: `tests/workflows/test_cross-layer-impact-check-yml.sh` 신설 (TC-1 regression guard — workflow 에서 4 grep line 런타임 추출 후 non-matching 입력으로 exit 0 검증 / TC-2 positive case / TC-3 ADR-005 parity / 4 structural `|| true` presence). `|| true` strip 시 TC-1·TC-2 genuine FAIL 확인 (RED 진정성).
  - plugin.json 6.1.0 → 6.1.1 PATCH (ADR-037 §결정 1(d) — 기존 optional workflow 버그 fix, `fix:` commit signal). marketplace atomic sync 별도 sibling PR (ADR-063 §결정 5).

## [6.1.0] - 2026-05-22

### Added

- [CFP-1187] 운영 phase Epic close — 배포 후 ongoing 신호 회수 + 자동 rollback 의 운영 phase mechanism layer 신설 (CFP-1059 6→8 lane 위, lane 아님 / lane count 변경 0). 운영 phase 8 Story 누적 1회 MINOR bump (multi-Story Epic, S8 close 결정).
  - S1 운영 phase 1st-class 정의 (ADR-104: lifecycle 배포→배포검토→운영 / mechanism layer / 0 API call constraint / wrapper-self-app N/A / self-improving loop) + domain-knowledge 4 파일
  - S2 자동 rollback 재정의 (ADR-105: 안전장치 4 AND [숫자 임계 / 보존 3h / 사후 알림 / kill-switch] + user-decision↔auto-rollback 2-layer disjoint + §self-application 2-layer) + rollback-protocol.md 2-layer amend
  - S3 운영 metric→PMOAgent input 회로 (ADR-106: 회로 4단계 + ADR-045 §D-9 disjoint 답습 + closure 3원칙 + KPI append-only + self-improving≠self-executing)
  - S4 rollback signal monitor (check_rollback_signal.py + workflow, CFP-1059 auto-rollback-hook 연계 중복0, 단계 2-a) + ADR-106 Amendment 1 (단계 2 two-part split)
  - S5 regression/smoke·health monitor (check_operational_regression.py, flap 3-layer for-clause+hysteresis+dedup, 0 API call filesystem) + ADR-106 Amendment 2 (단계 2-a monitor-originated notification generalize)
  - S6 self-improving loop closure (loop_closure_gate.py + operational-signal-to-issue.sh + check-ops-signal-alerts.sh, 단계 2-b/3/4 + KPI SHA-CAS append-only + 사용자 게이트) + operational-signal-v1 contract (kind:registry)
  - S7 canary auto-promote (canary_auto_promote.py, 3-layer L1 CFP-991 criteria 재사용 / L2 CFP-1059 deploy 호출 / L3 신규 오케스트레이션, S4 mirror 안전장치 4)
  - S8 통합 검증 (bats 83/83 GREEN + ADR-106 회로 coherence + 흡수 2 channel-drift/production-cutover cross-ref + CFP-1079 axis disjoint)
  - label-registry-v2 v2.45/v2.46/v2.47/v2.49 (ops-signal + hotfix-bypass:rollback-signal-monitor/operational-monitor/self-improving-loop/canary-auto-promote)
  - plugin.json 6.0.5 → 6.1.0 MINOR (운영 phase 신규 capability set). marketplace atomic sync 별도 sibling PR 의무 (ADR-063 §결정 5, 선행 merge 의무)

### Cross-ref

- Epic: #1187
- Stories: CFP-1190~1196 (S1~S8)
- ADR: ADR-104 / ADR-105 / ADR-106 (+ Amendment 1·2)

## [6.0.5] - 2026-05-21

### Changed

- [CFP-1168] deputy-mandate SKILL.md RACI matrix 전면 재편 (CFP-1126 follow-up deferred carrier realized — ADR-042 Amendment 10 + ADR-091 Amendment 1 정합): AggregateArch deprecated + ModuleArch boundary axis unified (7+3+1 → 6+3+1). PATCH bump (ADR-037 (b) Skill file minor edit — CFP-1126 governance 의미 확정 후 matrix body catch-up, agent 신설/제거 0건 = T2 미발동)
  - frontmatter description 7+3+1 → 6+3+1 + 호출 시점 5→6 deputy 표기 + 매트릭스 header + BackendArchEpic roster section CFP-1126 layer
  - CFP-1086 7+3+1 primary axis matrix → 6+3+1 (§3 aggregate / §11.1-§11.6 RDB OLTP / Alembic 7 원칙 owner = AggregateArch → ModuleArch boundary axis unified)
  - axis disjoint 검증 4 영역 정정 (ModuleArch↔AggregateArch 자기 통합 제거 + AggregateArch↔DataArch → ModuleArch↔DataArch + SecurityArch↔AggregateArch → SecurityArch↔ModuleArch)
  - footnote deferred → realized (CFP-1168 명시)
  - RACI 4-way 12-cell → 3-way 9-cell body 전면 재편 (AggregateArch cross-axis column 제거, Cell 1.1/2.1/3.1 의 C=AggregateArch → ModuleArch aggregate-level 흡수, Cell 1.2/1.3 + 2.2/2.3 + 3.2/3.3 재번호)
  - CONDITIONAL applicability key `aggregate_arch.applicable` 보존 (ModuleArch carry-over, consumer overlay backward-compat)
  - codeforge-design CLAUDE.md RACI 4-column → 3-column (9 cells) cross-repo `sibling sync` (design 0.19.0 → 0.19.1 PATCH)
  - doc-only fast-path ADR-054. marketplace atomic sync 별도 sibling PR 의무 (ADR-063 §결정 5, `mirrored field` version 변경)

## [6.0.4] - 2026-05-21

### Changed

- [CFP-1059-S6] 배포 매커니즘 실 구현 MINOR — 5 신규 deployment script + 7 workflow placeholder→실 job body (ADR-037 behavior change MINOR)
  - templates/deployment/: deploy-blue-green.sh + auto-version-bump.sh + auto-rollback-hook.sh + big-change-manual-trigger.sh + expand-migration-apply.sh (5 script 신설)
  - scripts/: deploy_blue_green.py + auto_version_bump.py (ADR-061 외부 .py, multi-line Python 의무)
  - .github/workflows/: 7 workflow placeholder → 실 job body (blue-green/auto-version-bump/auto-rollback/big-change/expand-migration/deploy-review/post-deploy-hook)
  - bats 34 TC GREEN (TDD RED→GREEN) — §8.5 restart invariant / §11.6 idempotency / ADR-087 §결정 5 healthcheck/swap 검증
  - S5 (6.0.3) 선행 merge → S6 rebase 후 6.0.4 sequential merge-order 의무 (ADR-064 ordering invariant)
- 구현리뷰 FIX iter 1: bats TC-3b/TC-4/TC-7 + TC-5c/TC-5d/TC-6b fallback assertion 강화 (regression 검출력 ↑, De Morgan 오류 수정, 정확값 단독 매칭)

### Cross-ref

- Epic: #1059
- Story-6: 배포 매커니즘 실 implementation (ADR-087 §결정 5)
- S5 sequential prerequisite: 6.0.3 (consumer overlay deploy.* schema validation)
## [6.0.3] - 2026-05-21

### Added

- [CFP-1059-S5] consumer overlay deploy.* schema 실 validation wire (declarative seed -> mechanical lint, ADR-054 Amendment 1 full-lane)
  - `scripts/check_deployment_schema.py` (yaml.safe_load 기반, exit 3-tier, 5 sub-field validation, ADR-061 외부 .py)
  - `scripts/check-deployment-schema.sh` (ADR-061 thin bash wrapper)
  - `templates/github-workflows/deployment-schema-check.yml` + `.github/workflows/` byte-identical self-app (warning tier)
  - `tests/scripts/cfp-1059-s5/check-deployment-schema.bats` (8 TC TDD) + 5 fixture YAML
  - `docs/evidence-checks-registry.yaml` deployment-schema-check 91번째 entry (warning tier)
  - label-registry-v2 v2.42 -> v2.43 (hotfix-bypass:deployment-schema 61번째 family member)
  - §7 SecurityArch: secret env-name only, value dereference 0

## [6.0.2] - 2026-05-21

### Changed

- [CFP-1059 Story-2/S3] codeforge family 7 → 9 plugin 실재화 — 신규 2 lane plugin seed 노출 (PATCH)
  - "필수 플러그인 (8종 active + 2 신설 예정)" → "(10종)" + codeforge-deploy + codeforge-deploy-review 실 plugin URL 정정 (Story-1 declarative 의 후속 wire)
  - "Development Agent Team" 표 배포 / 배포 리뷰 row SSOT = `TBD (S2/S3 sub-Story carrier)` → 실 plugin CLAUDE.md URL (배포 2 agent / 배포 리뷰 3 agent — ProductionEvidenceDeputy 이관 포함)
  - 신규 plugin seed = `mclayer/plugin-codeforge-deploy` (1.0.0) + `mclayer/plugin-codeforge-deploy-review` (1.0.0)
  - marketplace.json 2 신규 entry `sibling sync` (ADR-016 / ADR-063) — wrapper entry version 6.0.2 mirror 동반
- doc-only fast-path (ADR-054 Category 2) — src/tests 무변경. CFP-1059 / ADR-087 / ADR-088 정합

### Cross-ref

- Epic: #1059
- Story-2: codeforge-deploy plugin seed (ADR-087)
- Story-3: codeforge-deploy-review plugin seed + ProductionEvidenceDeputy 이관 (ADR-088)

## [6.0.1] - 2026-05-21

### Changed

- [CFP-1125 (Wave 1 Story-1)] 9 ADR/contract sunset_justification declarative `박제` (Imperative changelog walk paradigm 도입 carrier — CFP-1111 Epic)
  - 6 ADR sunset declarative: ADR-076 / ADR-083 / ADR-026 Amendment 5 (sibling carrier role 만) / ADR-027 Amendment 6 / ADR-067 (disjoint invariant declare, 본체 sunset 아님) / ADR-053 D2 영역 (D1 영구)
  - reconcile-protocol-v1 §4.3 (k)/(l)/(m) + §4.13 + §4.14 + §4.8 sunset declarative
  - reconcile-protocol-v1 v1.13 status `Active → Deprecated`
  - ADR-RESERVATION 7 slot append ADR-92 ~ ADR-98 (Wave 1 Story-2 carry)
- doc-only fast-path (ADR-054 Category 2) — src/tests 무변경
- β2 audit (CFP-1113) input — 9/9 anchor LOSSLESS 판정 + 3 carry-over 설계 주의 사항

### Cross-ref

- Epic: #1111
- Story-1 sub-issue: #1125
- Sister CFP: #1112 (β1 P0) / #1113 (β2 closed) / #1114 (β3 P1) / #1115 (β5 P1)
- spec: codeforge-internal-docs/wrapper/specs/CFP-1111.md (PR #732 merged 4cdd3019)
- plan: codeforge-internal-docs/wrapper/plans/CFP-1111-W1-S1.md (PR #733 merged)

### marketplace `sibling sync` (declared, 실 PR 발의 = Task 14 후)

- ADR-063 atomic invariant 정합 의무 — wrapper PR open 후 marketplace.json mirror `sibling sync` PR 발의

## [6.0.0] - 2026-05-20

### BREAKING CHANGES (CFP-1059 Story-1 — Deploy + DeployReview lane 신설 카리어 Phase 1 SSOT)

본 release = **MAJOR bump** — codeforge family lane 구조 정식 확장 (6 → 8 lane). Phase 1 = ADR / spec / governance SSOT layer (Phase 2 PR 직후 mechanical enforcement은 별 sub-Story carrier 분할).

- **Lane 구조 6 → 8 단계 확장** — 배포 (Deploy) + 배포 검토 (Deploy Review) 정식 lane 신설 (요구사항 / 설계 / 설계리뷰 / 구현 / 구현리뷰 / 통합테스트 / 보안테스트 / **배포** / **배포-리뷰** 9 단계 lifecycle)
- **Plugin family 확장** — codeforge-deploy + codeforge-deploy-review plugin family member 신설 (Story-2 + Story-3 carrier — 본 Story-1 = wrapper SSOT 만)
- **Consumer overlay schema 확장** — `project.yaml` `deploy.*` 5 sub-field 신설 (host_mapping / docker_hub / traefik / 1password / ssh_targets)
- **Label taxonomy 확장** — phase:배포 / phase:배포-리뷰 + 5 gate:* + 7 hotfix-bypass:* + category:deployment 신설 (label-registry v2.42 MINOR)

### Migration guide

자세한 마이그레이션 단계 = `docs/consumer-guide.md` §1m 참조 (Story-2 carrier 신설 예정).

### Added

- **ADR-087** (Deploy lane 신설 — single deploy_strategy enum + rollback policy + 배포 후 health check)
- **ADR-088** (Deploy Review lane 신설 + ProductionEvidenceDeputy ownership 이관 wrapper → codeforge-deploy-review)
- **ADR-089** (Schema 변경 7 원칙 — additive only / closed enum / default value / deprecation marker / migration guide / version bump / `sibling sync`)
- **ADR-090** (Cross-layer 참조 정책 — 8 lane 간 cross-ref 의무 + circular dependency 차단)
- 7 신규 workflow template (`templates/github-workflows/deploy-*.yml` — Story-2 carrier)
- 2 신규 inter-plugin contract placeholder (`deploy-output-v1` / `deploy-review-output-v1`, Story-2/Story-3 wire)

### Changed

- **ADR-023 Amendment 1** (lane plugin lifecycle 8 lane 확장 — 6 → 8 enum)
- **ADR-042 Amendment 9** (DeployPL Sonnet + DeployReviewPL Opus 4 신설 agent tier)
- **ADR-014 Amendment 5** (InfraOperationalArch ↔ DeployPL boundary 정합)
- **ADR-026 Amendment 6** (post-merge automation — Epic close → Deploy trigger)
- **ADR-027 Amendment 7** (consumer adoption protocol — `deploy.*` schema 5 sub-field)
- **ADR-063 Amendment 7** (marketplace atomic invariant — family scope 7 → 9 plugin 확장)
- **ADR-072 Amendment 4** (ProductionEvidenceDeputy ownership wrapper → codeforge-deploy-review 이관)
- 8 lane CLAUDE.md / playbook / skill 6종 갱신 (Story-2 carrier 분할)

### Sibling plugin atomic (옵션 A — wrapper-only MAJOR, 사용자 결정 2026-05-20 KST)

본 release 의 6 lane plugin (codeforge-{requirements,design,develop,test,review,pmo}) = **자체 변경 0** → version retain (**ADR-063/016 strict 해석** — per-plugin SSOT, 자체 코드 변경 0 = version 불변, history 보존). codeforge-deploy + codeforge-deploy-review = 1.0.0 baseline (Story-2 + Story-3 carrier 영역, 본 Story-1 = wrapper SSOT 만).

### Baseline 정정

본 Story-1 진입 시 spec/plan 안 stale 영역 검출:

- baseline version: 5.92.0 (stale) → **5.99.0 (실제)** — parallel session 7 MINOR 누적 (CFP-689 / 967 / 900 / 967 Phase 2 / 1086 Stories 등)
- marketplace.json path: top-level (stale) → **`.claude-plugin/marketplace.json` (실제)**
- atomic file 수: 7 plugin atomic (stale) → **wrapper-only MAJOR + 6 sibling retain (옵션 A 정합)**

## [5.103.0] - 2026-05-20

## [5.99.0] - 2026-05-20

### Added (CFP-1088 — Wave 2-2 of CFP-698 retro carrier)

본 release = IntegrationTest §7.4 측정 evidence path codify Wave 2 mechanical wire (codeforge-test plugin `sibling sync`, 1.2.0 → 1.3.0).

#### codeforge-test plugin changes

- **`mclayer/plugin-codeforge-test/agents/IntegrationTestAgent.md`** — §7.4 row append: per-Story `tests/integration/baseline/<STORY-KEY>/§7.4-measurement-evidence.md` self-write path codify + 7-column Axis 2 schema (measurement_id | pointer | measured_value | unit | method | timestamp | empirical_source) + 6-column Axis 3 schema (policy_id | pointer | measured_value M-row ref | proposed_policy_value | rationale_ref | follow_up_carrier)
- **`mclayer/plugin-codeforge-test/tests/integration/baseline/example-story/§7.4-measurement-evidence.md`** — template file (CFP-1088 codify)
- **`mclayer/plugin-codeforge-test/tests/integration/baseline/example-story/test_§7.4-axis-2-measurement.bats`** — 5 TC PASS (schema invariant)
- **`mclayer/plugin-codeforge-test/tests/integration/baseline/example-story/test_§7.4-axis-3-policy.bats`** — 5 TC PASS (Axis 3 pointer schema)
- **`mclayer/plugin-codeforge-test/.claude-plugin/plugin.json`** — 1.2.0 → 1.3.0 MINOR

#### Cross-ref

- ADR-014 Amendment 4 §결정 2 evidence-driven 3-axis (Axis 1 측정 대상 정의 DesignLane / Axis 2 실측 IntegrationTestLane / Axis 3 policy 결정 ArchitectLane post-measurement)
- ADR-068 Amendment 3 §결정 1 I-6 audit-gate-pointer-existence (CFP-1087, 4-form pointer scope)
- review-verdict-v4 v4.7 `audit_gate_pointer_self_check_passed` + `findings[].type: "audit-gate-pointer-missing"` (CFP-1087)
- CFP-1089 DesignReviewPL §8.6 pointer-presence-check mechanical workflow (sibling carrier merged)

### Marketplace dual sync

- **`mclayer/marketplace`** sync PR — codeforge 5.102.0 → 5.103.0 + codeforge-test 1.2.0 → 1.3.0 dual `sibling sync` (ADR-063 §결정 5)

## [5.102.0] - 2026-05-20

### Added (CFP-1089 — Wave 2-3 of CFP-698 retro carrier)

본 release = DesignReviewPL §8.6 pointer-presence-check mechanical workflow Phase 2 (ADR-068 Amendment 3 + review-verdict-v4 v4.7 declaration prerequisite 영역 CFP-1087 이미 merged 영역 정합).

#### Lint script + workflow

- **`scripts/check-design-review-pl-8-6-pointer.sh`** + **`scripts/lib/check_design_review_pl_8_6_pointer.py`** (ADR-061 thin bash wrapper + Python SSOT) — 3-check warning tier lint:
  - Check 1: findings[].type "audit-gate-pointer-missing" literal review-verdict-v4 v4.7+ enum 정합
  - Check 2: audit_gate_pointer_self_check_passed verdict-level boolean field schema 정합
  - Check 3: ADR-068 frontmatter amendments[3] + I-6 invariant declaration cross-ref 정합
- **`templates/github-workflows/design-review-pl-8-6-pointer.yml`** + **`.github/workflows/design-review-pl-8-6-pointer.yml`** (byte-identical self-app, ADR-005)
- **`tests/scripts/check-design-review-pl-8-6-pointer.bats`** — 5 TC PASS

#### Registry entries

- **`docs/evidence-checks-registry.yaml`** — design-review-pl-8-6-pointer entry append (warning tier, owner_adr ADR-068, carrier_adr ADR-060, sibling_dependencies CFP-1087)
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — hotfix-bypass:design-review-pl-8-6-pointer entry append

### Marketplace sync

- **`mclayer/marketplace`** sync PR — plugins[name=codeforge] version 5.101.0 → 5.102.0 + description verbatim mirror (ADR-063 §결정 5)

## [5.101.0] - 2026-05-20

### Added (CFP-1102 — ADR-073 Amendment 5 carrier)

본 release = ADR-073 Amendment 5 (§결정 1 transition trigger enum 5번째 entry `fix_iter_start` 추가) doc-only fast-path ADR-054 Category 2 carrier.

#### ADR Amendment 1종

- **`docs/adr/ADR-073-orchestrator-verify-before-assert.md`** — Amendment 5 append (CFP-1102). §결정 1 transition trigger enum 4 → 5 entry `ratchet` (`fix_iter_start` 5번째). §결정 1-E main HEAD `pin` verify primitive 3-step (fetch + remote HEAD `pin` gh api + local cache cross-check). §결정 1-F Amendment 2 §결정 1-A 3-step 재실행 정합. CFP-1087 cascade race evidence + pattern_count 2 reach HIGH escalation.

#### Cross-ref

- **`CLAUDE.md`** — Verify-before-trust 4-layer governance ADR-073 단락 Amendment 5 mention 추가 (별 PR 또는 본 PR 동반)

### Marketplace sync

- **`mclayer/marketplace`** sync PR — plugins[name=codeforge] version 5.100.0 → 5.101.0 + description verbatim mirror (ADR-063 §결정 5 atomic invariant, separate sibling PR 선행 merge)

## [5.100.0] - 2026-05-20

### Added (CFP-1087 — Wave 2-1 of CFP-698 retro carrier)

본 release = ADR-068 Amendment 3 + review-verdict-v4 v4.7 MINOR atomic carrier (doc-only fast-path ADR-054 Category 2 — 4-repo atomic: marketplace + codeforge-review + wrapper + internal-docs). **collision resolution** — CFP-1086 main cascade S1/S3/S4/S5 (Amendment 2 + v4.6 + 5.99.0) sequential precedence acquire → 본 carrier renumber Amendment 3 + v4.7 + 5.100.0.

#### ADR Amendment 1종

- **`docs/adr/ADR-068-boundary-completeness-invariants.md`** — Amendment 3 append (CFP-1087, I-6 audit-gate-pointer-existence invariant 신설). §8.6 audit gate finding 영역 4-form pointer scope (link target / section anchor / file path reference / ADR §결정 N reference) mechanical existence verify 의무. 5 → 6 invariants `ratchet` 강화 (ADR-058 §결정 5 정합). CFP-528 Amendment 1 (I-5) precedent verbatim 답습. ADR-073 cross-ref backref (I-6 verification primitive ↔ §결정 1 verify-before-assert primitive directly-analogous).

#### Inter-plugin contract bumps

- **`docs/inter-plugin-contracts/review-verdict-v4.md`** — v4.6 → v4.7 MINOR (wrapper sibling + codeforge-review canonical 양 file verbatim mirror). `audit_gate_pointer_self_check_passed` 5번째 verdict-level boolean field 신설 + `findings[].type` enum 5번째 literal `"audit-gate-pointer-missing"` 추가 (additive only, backward-compat invariant 보존).
- **`docs/inter-plugin-contracts/MANIFEST.yaml`** — review-verdict-v4 version row 4.6 → 4.7 갱신 + CFP-1087 entry note append.

#### `Sibling sync` — codeforge-review canonical

- **`mclayer/plugin-codeforge-review`** sibling PR #40 (canonical-first invariant, ADR-010 §단계 절차): `docs/inter-plugin-contracts/review-verdict-v4.md` v4.7 verbatim mirror + `templates/review-pl-base.md` §8.6 wording rename (boundary-completeness flag → audit-gate-pointer-missing flag, alias 패턴 disjoint axis 명문화 + 4-form pointer scope cite).

#### Cross-ref

- **`docs/adr/ADR-068-boundary-completeness-invariants.md`** — `related_adrs[]` ADR-073 append + `## 관련 ADR` 표 ADR-073 row 신설 (cross-ref only, ADR-073 본문 0건 변경).
- **`CLAUDE.md`** — ADR-068 cross-ref 갱신 (Amendment 2 → Amendment 3 mention 추가, I-6 audit-gate-pointer-existence invariant 1-line note).

### Marketplace sync

- **`mclayer/marketplace`** sync PR #177 — plugins[name=codeforge] version 5.99.0 → 5.100.0 + description verbatim mirror sync (ADR-063 §결정 5 atomic invariant, separate sibling PR 선행 merge 의무). main 영역 5.99.0 (CFP-1086-S5 sync 완료) 동시 catch-up.

## [5.98.0] - 2026-05-20

### Changed (CFP-1086 Story-4 — ADR-068 Amendment 2 implementation note + chief author body cross-ref binding)

본 release = CFP-1086 BackendArchEpic Phase 2 Story-4 carrier. Story-1 (Amendment 2 declare 본문) 의 **chief author implementation cross-ref** + **mctrader 5 repo cross-layer evidence (P4)** + ADR-068 implementation note subsection. doc-only fast-path (ADR-054 Category 2 — ADR cross-ref subsection 추가, src/tests 변경 0). **5.97.0 skip** — S3 (parallel sibling Story-3 RACI matrix codify) 점유. S4 preemptive bump to 5.98.0 (S3 merge 후 본 PR rebase 시 conflict-free).

#### Changed

- **`docs/adr/ADR-068-boundary-completeness-invariants.md`** — Amendment 2 body section 끝 §"Implementation note (CFP-1086 Story-4 — chief author body cross-ref)" subsection 추가. 4-layer 분리 명시 (declaration layer = 본 ADR / implementation layer = chief author prompt body / architecture doc layer = lane internal SSOT / skill layer = RACI matrix host). Carrier 분리 표 (Story-1 declaration / Story-3 RACI matrix / Story-4 implementation body). Body 정합성 invariant (I-4 wording SSOT 자기 적용). Mechanical enforcement 영역 unchanged (verdict field-only enforcement 유지 — 신규 lint script / workflow yml / registry entry 0건). frontmatter `amendments[]` Amendment 2 row `ref` field 갱신 (implementation note 동반 명시). 변경이력 row 추가 (`2026-05-20 Implementation note (CFP-1086 / Story-4 — ADR-068 본문 정책 0건 변경)`).

#### Invariant declare

- **본문 정책 / I-1~I-5 invariant body / verdict field / 10 dimension enum / mitigation 0건 변경 invariant** — Amendment 아님, implementation surface 분포 declaration only
- `ratchet` 강화 방향 (약화 0건) — Amendment 2 declare layer 와 implementation layer 분리 명시 = sunset_justification 불필요 (declaration-only cross-ref)

#### Related ADRs

- ADR-068 (본 ADR — Amendment 2 implementation note subsection 추가)
- ADR-068 Amendment 2 (CFP-1086 Story-1 carrier — declaration layer SSOT)
- ADR-086 (CFP-1086 Story-1 신설 — Deputy 신설 결정 framework P7, ladder 3단계 호출 영역)
- ADR-042 Amendment 8 (CFP-1086 Story-1 carrier — 7+3+1 roster, ladder 1단계 RACI lookup 입력)
- ADR-054 (doc-only fast-path Category 2 — ADR cross-ref subsection 추가)

#### `Sibling sync` (Orchestrator 영역, 별도 cross-repo PR)

- `mclayer/plugin-codeforge-design` plugin.json 0.15.0 → 0.17.0 + ArchitectAgent.md §"Chief 통합 mechanism" + §"Chief tie-break ladder" + §"Wording SSOT advocate" body + docs/architecture/codeforge-design.md §"mctrader 5 repo cross-layer evidence" section
- `mclayer/marketplace` `marketplace.json` `plugins[name=codeforge]` `mirrored field` 4종 sync (ADR-063 atomic invariant)

## [5.97.0] - 2026-05-20

### Changed (CFP-1086 Story-3 (Wave 2) — deputy-mandate skill RACI 표준 body 4-way overlap zone codify)

본 release = CFP-1086 Wave 2 Story-3 carrier (W1 Story-1+S2 merged baseline 위 body 채움). doc-only fast-path (ADR-054 Category 2 — skill body 확장, ADR / src / tests 변경 0). Story-1 = skeleton + cross-ref. Story-3 (본 release) = 12-cell matrix R/A/C/I 4-column body 채움.

#### Changed

- **`skills/deputy-mandate/SKILL.md`** — `## RACI 표준 row 형식 (Story-3 — 4-way overlap zone body)` 단락 (skeleton → body 전환):
  - **4-column 열 정의** — R (primary 결정권자) / A (모든 row = ArchitectAgent chief tie-break ladder 3단계, ADR-068 Amd 2) / C (co-author + 양방향 dialog) / I (일방향 통지).
  - **4-way 12-cell matrix** — 3 sub-axis (Security / InfraOp / TestContract) × 4 cross-axis (Aggregate / Data OLAP / Module / APIContract) = 12 Cell × R/A/C/I 4-column row. CFP-1086 §7+3+1 primary axis matrix 의 cross-axis 영역 보강.
  - **Cell 1.1 ~ 3.4 each row body** — 12 Cell 각 R deputy primary author + C deputy co-author + I deputy 통지 영역 + 책임 1-line description:
    - Cell 1.1 Security × Aggregate (PII column type / encryption-at-rest / RDB audit log schema)
    - Cell 1.2 Security × Data (OLAP PII 익명화 / Parquet column 마스킹)
    - Cell 1.3 Security × Module (trust boundary module 배치 / dependency direction)
    - Cell 1.4 Security × APIContract (auth / authz / rate limit / input validation)
    - Cell 2.1 InfraOp × Aggregate (connection pool / replica / advisory lock)
    - Cell 2.2 InfraOp × Data (OLAP scan / streaming throttle / batch window)
    - Cell 2.3 InfraOp × Module (runtime module 분리 / hot reload)
    - Cell 2.4 InfraOp × APIContract (transport-level retry / circuit breaker / timeout / cancel-on-disconnect)
    - Cell 3.1 TestContract × Aggregate (migration forward/backward + idempotency test)
    - Cell 3.2 TestContract × Data (OLAP fixture / streaming replay / lineage test)
    - Cell 3.3 TestContract × Module (module boundary test / dependency test)
    - Cell 3.4 TestContract × APIContract (contract testing — Pact / OpenAPI / GraphQL schema validate) — **예외 R=APIContractArch** primary (§8.6 contract testing primary axis 정합, CFP-1086 primary axis matrix row 정합) + C=TestContractArch (CI placement + orchestration disjoint axis).
  - **Cell selection heuristic 4-step** — (1) single-axis 결정 → primary axis matrix 직접 lookup, RACI 미적용 / (2) 2-axis 이상 overlap → 본 RACI 12-cell row 활성 (R+C dialog, A sign-off, I 통지) / (3) R+C 합의 부재 → ladder 2단계 (ADR-068 invariant) / (4) invariant 적용 후 미해소 → ladder 3단계 (chief judgement + ADR Amendment 발의).
  - **Cross-ref 강화** — ADR-068 Amendment 2 ladder 3단계 wording SSOT + ADR-086 axis 분석 + 5-checklist + review-verdict-v4 v4.6 `boundary_completeness_self_check_passed` scope expansion + CFP-1086 Story-2 (Cell 1.4 / 2.4 / 3.4 의 C/R 영역 detail SSOT) + codeforge-design CLAUDE.md RACI section mirror (wrapper SSOT 참조).
- **`.claude-plugin/plugin.json`**: 5.96.0 → **5.97.0** MINOR (ADR-037 — skill body 확장 + cross-repo sibling carrier governance behavior change). description 갱신 (CFP-1086 Story-3 RACI body 12-cell codify entry 추가).

#### Related ADRs

- ADR-042 Amendment 8 (CFP-1086 Story-1 carrier — 7+3+1 deputy roster, 본 RACI matrix 의 axis 정의 입력)
- ADR-068 Amendment 2 (CFP-1086 Story-1 sibling carrier — chief tie-break ladder 3 단계 1단계 RACI lookup SSOT)
- ADR-086 (CFP-1086 Story-1 sibling 신설 carrier — Deputy 신설 결정 framework, RACI codify = mechanism gap 해소 `ratchet`)
- ADR-058 §결정 5 (ADR sunset criteria mandate — top-down `ratchet` 정합, additive only)
- ADR-064 §결정 7 (decision principle mandate — top-down `ratchet`, 강화 방향만 허용)
- ADR-054 (doc-only fast-path Category 2 — skill body 확장)

#### Marketplace `sibling sync` (Orchestrator 영역, 별도 cross-repo PR)

- `mclayer/marketplace` `marketplace.json` `plugins[name=codeforge]` `mirrored field` 4종 (name / version / description / author) sync. ADR-063 atomic invariant. Sibling repos cross-repo sync (wrapper + codeforge-design = 2 plugin repos this Story; internal-docs Story file + marketplace sync = Orchestrator scope).

## [5.96.0] - 2026-05-20

### Added (CFP-1086 Story-1 — BackendArchEpic Phase 2 design lane 7+3+1 roster 재편)

본 release = ADR-042 Amendment 8 + ADR-068 Amendment 2 + ADR-086 신설 atomic carrier (doc-only fast-path ADR-054 5-repo atomic).

#### ADR 3종 (Amendment 2 + 신설 1)

- **`docs/adr/ADR-042-agent-model-selection-policy.md`** — Amendment 8 append (5+3 → 7+3+1 permanent+CONDITIONAL roster 재편). AggregateArchitectAgent + APIContractArchitectAgent 신설 (Sonnet single-mandate advocacy). CodeArchitectAgent → ModuleArchitectAgent rename + mandate 정정 (도메인 모델 invariant 영역 = AggregateArch 분리). DataArchitectAgent mandate 축소 (RDB OLTP 영역 제거 → 빅데이터 OLAP only). AggregateArch CONDITIONAL applicability (`project.yaml aggregate_arch.applicable: bool` — P2). DDDArchitectAgent 신설 reject 명문화 (axis 미정합).
- **`docs/adr/ADR-068-boundary-completeness-invariants.md`** — Amendment 2 append (wording SSOT 충돌 시 chief tie-break ladder 3 단계: RACI lookup → ADR-068 invariant → chief judgement + ADR Amendment 발의). `boundary_completeness_self_check_passed` scope expansion (I-4 mechanism boost).
- **`docs/adr/ADR-086-deputy-creation-decision-framework.md`** (신설) — Deputy 신설 결정 framework P7. axis 분석 의무 + 5-checklist self-application (axis disjoint / cost-token budget / consumer carrier / sibling Epic align / deferred trigger) + deferred carrier path codify. 본 Amendment 8 = self-application 첫 사례. `mechanical_enforcement_actions: []` declaration-only Wave 1 retain (ADR-076 / ADR-070 / ADR-082 precedent 답습, 5 instance 누적).

#### Inter-plugin contract bumps

- **`docs/inter-plugin-contracts/review-verdict-v4.md`** — v4.5 → v4.6 MINOR (`deputy_axis_restructure_self_check_passed` optional bool field 신설 + `boundary_completeness_self_check_passed` scope expansion). 적용 lane = design lane only.
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.40 → v2.41 MINOR (5 신규 entry: 4 axis:* + hotfix-bypass:deputy-axis-restructure 53번째 family member + 신규 category enum `axis`).
- **`docs/inter-plugin-contracts/MANIFEST.yaml`** — review-verdict-v4 + label-registry-v2 version row 갱신.

### Changed

- **`CLAUDE.md`** — L131 Development Agent Team 표 row + Deputy mandate 매트릭스 단락 (5+3 → 7+3+1).
- **`docs/orchestrator-playbook.md`** — Lane spawn 표 + token budget (평균 22 → 28 / full 34 → 40, 1.27배) + 설계 lane packet recipient 7 permanent + 3 sub-tuple.
- **`docs/project-config-schema.md`** + **`docs/consumer-guide.md`** — `aggregate_arch.{applicable, migration_tool}` schema 신설 (Tool scope B — 9-enum override default alembic). §1l consumer-guide 신설.
- **`skills/deputy-mandate/SKILL.md`** — 7+3+1 roster + CFP-1086 primary axis matrix canonical SSOT + RACI 표준 row 형식 skeleton (Story-3 carrier).
- **`docs/parallel-work/section-ownership.yaml`** — Deputy mandate 매트릭스 section append-only ownership (ADR-042 Amd 8 carrier).
- **`docs/evidence-checks-registry.yaml`** — `deputy-spawn-count-empirical-grounding` deferred-followup entry append (ADR-068 I-5 backref).
- **`docs/adr/ADR-RESERVATION.md`** — Row 86 `reserved` → `active` 전환 (ADR-086 신설 점유 확정).
- **`.claude-plugin/plugin.json`** — 5.95.0 → **5.96.0** MINOR (ADR-037 — ADR Amendment carrier 묶음 + label-registry-v2 MINOR + review-verdict-v4 MINOR governance behavior change).

### Marketplace sync

plugin.json 5.95.0 → 5.96.0 MINOR + marketplace.json `sibling sync` PR after wrapper merge (ADR-063 atomic invariant, `mirrored field` 4종). Sibling Stories 5-repo atomic (wrapper + codeforge-design + internal-docs + marketplace, codeforge-pmo 변경 0건).

### Related ADRs

- ADR-042 Amendment 8 (본 carrier — design lane 7+3+1 roster 재편)
- ADR-068 Amendment 2 (sibling carrier — chief tie-break ladder)
- ADR-086 (sibling 신설 carrier — Deputy 신설 결정 framework P7)
- ADR-054 (doc-only fast-path — 5-repo atomic 단일 PR family)
- ADR-063 (marketplace atomic invariant — Phase 6 sync)
- ADR-016 (marketplace registration policy — `sibling sync` 의무)

## [5.95.0] - 2026-05-20

### Added (CFP-1057 — ADR-085 Wave 2 mechanical wire, CFP-1041 follow-up (b))

- **`scripts/check-active-sessions-presence.sh`** + **`scripts/lib/check_active_sessions_presence.py`** — Story Issue body `<!-- active_sessions -->` HTML comment block OR Story file frontmatter `active_sessions:` array presence-grep + 5-tuple schema validation (git_identity / worktree_path / entry_phase / entered_at_kst / last_heartbeat_kst, ADR-079 KST `+09:00` strict)
- **`scripts/check-lane-entry-ownership.sh`** + **`scripts/lib/check_lane_entry_ownership.py`** — `gh pr list --search "head:<branch>" --state open` ownership verify primitive (ADR-073 Amendment 2 polling enum 4번째 source `active_sessions_check`)
- **`templates/github-workflows/active-sessions-presence.yml`** + **`templates/github-workflows/lane-entry-ownership-verify.yml`** (continue-on-error: true, warning tier ADR-060 §결정 5)
- **`.github/workflows/active-sessions-presence.yml`** + **`.github/workflows/lane-entry-ownership-verify.yml`** byte-identical self-app
- **`tests/scripts/check-active-sessions-presence/test_active_sessions_presence.bats`** (9 TC) + **`tests/scripts/check-lane-entry-ownership/test_lane_entry_ownership.bats`** (4 TC)
- `docs/evidence-checks-registry.yaml` 2 entry `status: deferred-followup → warning` 전환 (ADR-085 mechanical_enforcement_actions Wave 1 → Wave 2 promotion)

### Marketplace sync

plugin.json 5.94.0 → 5.95.0 MINOR + marketplace.json `sibling sync` PR after wrapper merge (ADR-063 atomic invariant, `mirrored field` 4종).

CFP-967 parallel-work-sentinel-pickup chain precedent verbatim 답습 (Wave 1 declarative anchor CFP-966 → Wave 2 mechanical wire CFP-967 → Wave 1 declarative anchor CFP-1041 → Wave 2 mechanical wire CFP-1057).

## [5.94.0] - 2026-05-20

### Added (CFP-1041 — ADR-085 Multi-session collaboration protocol SSOT, declarative anchor Wave 1)

- **`docs/adr/ADR-085-multi-session-collaboration-protocol.md`** NEW — 본질 선언 + 8 §결정 + 5-layer disjoint 표 (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row Multi-session coordination 신설) + `mechanical_enforcement_actions: [active-sessions-presence, lane-entry-ownership-verify]` declaration-only-Wave-1 (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습)
- `docs/adr/ADR-RESERVATION.md` row 85 = CFP-1041 active
- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` **Amendment 4** cross-ref (post-rebase amendments[] sequence [1, 2, 3 (CFP-689 worktree-first self-ownership), 4 (본 CFP-1041 ADR-085 coordination)] consecutive)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` **Amendment 3** cross-ref (dual amendments[]+amendment_log[] block 정합)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.39 → v2.40 (+ 2 hotfix-bypass family member: `active-sessions-presence` + `lane-entry-ownership-verify`)
- `docs/inter-plugin-contracts/MANIFEST.yaml` label-registry-v2 version sync
- `docs/evidence-checks-registry.yaml` + 2 entry warning tier deferred-followup (active-sessions-presence + lane-entry-ownership-verify, recurrence {count: 0, threshold: 3, promotion_trigger: none})
- `templates/story-page-structure.md` frontmatter `active_sessions[]` field 5-tuple schema (git_identity / worktree_path / entry_phase / entered_at_kst / last_heartbeat_kst, ADR-079 KST `+09:00` strict, optional backward-compat default `[]`)
- `CLAUDE.md` 신규 "Multi-session collaboration protocol" 단락 + verify-before-trust 4-layer 단락 Amendment 4 cross-ref
- `docs/orchestrator-playbook.md` §3.18 신설 (lane-entry sentinel 4-step polling + rebase merge 우선 + handoff baton transfer)

### Cross-Issue absorption

- `#983` super-class SSOT (`parallel_session_shared_workdir_collision` 8+ occurrence) — close declare (absorbed into ADR-085)
- `#870` multi-session FIX-handoff contract (P:medium, from-cfp-699-retro) — inline absorb §결정 5 (handoff baton transfer)
- `#1038` ADR-073 Amendment 3 escalation carrier — resolved by sibling CFP-689 PR #1043 merged `18236621` 2026-05-20 (parallel session race during 본 carrier Phase 1, dogfooding ADR-085 코드ify pattern)

### Carrier evidence

- ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach (CFP-953/946/949/932/954/991/967/1014 + CFP-689 9th in-flight race)
- ADR-082 precedent 동형 (pattern_count → 신규 ADR carrier, NOT Amendment overload)
- Branch A user-confirmed (Codex high-confidence + Orchestrator 종합 over ArchitectAgent Branch C)
- CFP-681 retroactive evidence (collaboration success variant 첫 case — rebase merge 우선, force-push 회피)

### Marketplace sync mandate (ADR-063 §결정 5)

plugin.json 5.93.0 → 5.94.0 MINOR bump → marketplace.json `sibling sync` PR after wrapper merge (`mirrored field` 4종 atomic). `marketplace_sync_declared: true`.

## [5.93.0] - 2026-05-20

### Added (CFP-689 — ADR-073 Amendment 3 worktree-first self-ownership verify 3-tuple, declarative anchor Wave 1)

- **`docs/adr/ADR-073-orchestrator-verify-before-assert.md`** — Amendment 3 sub-section append (107 lines: §결정 1-A 추가 transition trigger enum 4번째 entry `worktree_lane_spawn` + §결정 1-D path-based self-ownership verify 3-tuple primitive (a) cwd↔worktree path / (b) HEAD↔reflog membership / (c) `git worktree list --porcelain`+reflog 2-source AND + §결정 1-E subagent verdict re-verify mandate (ADR-082 cross-ref, multi-worktree self-confusion 영역 agent 도 보임 입증) + §결정 1-F disjoint axis with #983 reflog membership 1 bit signal + Wave 1 declaration / Wave 2 mechanical wire 분리 — CFP-966/967 chain precedent 답습). frontmatter `amendments[]` row 신설 (`amendment_id: 3`, `cfp: CFP-689`, `date: 2026-05-20`, `status: applied`, `sunset_justification: null` `ratchet` 강화 only) + `mechanical_enforcement_actions[]` 1 → 2 entry (`parallel-work-sentinel-pickup` 보존 + `worktree-self-ownership-verify` 신규) + `related_stories[]` CFP-689 + CFP-1038 + CFP-983 append. ADR-058 §결정 5 / ADR-064 §self-application top-down `ratchet` 강화 방향 only.
- **`docs/evidence-checks-registry.yaml`** — `worktree-self-ownership-verify` 신규 entry append (warning tier, `status: deferred-followup` declaration-only-Wave-1, recurrence count 3 / threshold 3 / promotion_trigger auto_blocking — pattern_count 3 already reached 2026-05-19~20 sentinel evidence, owner_adr ADR-073-Amendment-3 / carrier_adr ADR-060 dual-binding codex-network-scope-presence precedent 답습, sibling_dependencies: [CFP-689, TBD-Wave-2-sub-CFP]).
- **`docs/parallel-work/section-ownership.yaml`** — ADR-073 file lock row append (`carrier_story: CFP-689`, `amendment_id: 3`, Amendment 2 CFP-966 row 와 section disjoint 보장).
- **`docs/domain-knowledge/domain/orchestrator-discipline/worktree-self-ownership-verify.md`** — 신규 narrative SSOT (164 lines, DomainAgent 지식 공백 해소): 1. 5th layer staleness (spatial dimension, Bazel hermeticity 동형 + codeforge 5th layer 확장) + 2. 3 occurrences sentinel evidence (CFP-1026 STAND-DOWN + CFP-681 cfp-1014 dup worktree `f39b221` + CFP-681 ArchitectPL `00b7d8a` mis-flag) + 3. Path-based 3-tuple verify primitive (사용자 prompt identity-based → path-based 대안 채택 — Solo-dev 환경 식별력 0 회피) + 4. Edge case (detached HEAD / anonymous worktree / signed commit GPG / reflog GC 90d / Windows path normalize) + 5. Subagent verdict re-verify mandate (multi-worktree self-confusion 영역 agent 도 보임, ADR-082 §결정 1 4-layer disjoint 표 cross-ref) + 6. Disjoint scope with #983 (reflog membership 1 bit) + 7. mechanical_enforcement chain (Wave 1/2/3 progression) + 8. 외부 fact 인용 (`git worktree list --porcelain` 산업 표준 — Linux kernel / Chromium primary cite).

### Changed

- **`CLAUDE.md`** — "Verify-before-trust 4-layer governance" 단락 안 ADR-073 Amendment 3 (CFP-689, 2026-05-20) 1-문장 inline append (worktree-first 환경 self-confusion sub-domain 5th layer staleness + 4번째 transition trigger enum + path-based 3-tuple verify + subagent verdict re-verify mandate + `mechanical_enforcement_actions: [parallel-work-sentinel-pickup, worktree-self-ownership-verify]` 2 entry + disjoint axis with #983 = reflog membership 1 bit + Wave 2 별 sub-CFP carrier + `feedback_worktree_first_not_parallel_session` memory 승격 carrier). line count 315 lines invariant 유지 (cap ≤ 320, ADR-012 Amendment 1, +5 budget 안 wrapped inside existing paragraph).
- **`.claude-plugin/plugin.json`** — version `5.92.0` → `5.93.0` MINOR (ADR-037 — ADR-073 Amendment 3 신설 발의 = governance behavior change MINOR).
- **marketplace atomic sync (ADR-063 §결정 5, separate sibling PR — 본 wrapper PR 선행/직후 marketplace sync PR open + merge 의무)**: `mclayer/marketplace/marketplace.json` plugins[name=codeforge] `mirrored field` `version` `5.92.0` → `5.93.0` + `description` 동기화 (별 PR scope, 본 ArchitectAgent spawn scope 외 — Orchestrator inline scope).

### Cross-references

- **Carrier ESC**: plugin-codeforge#1038 PMO escalation P1 (worktree_first_self_confusion_within_single_session pattern_count 3 reach) — 본 PR merge 시 close 의무.
- **#983 후보 (c) 정식 carrier**: plugin-codeforge#983 P1 ESC body 안 후보 (c) "ADR-073 Amendment 3 — shared workdir collision worktree-first invariant 강화" 의 정식 carrier (disjoint axis = reflog membership 1 bit).
- **Wave 2 별 sub-CFP reservation** (sequential next, 본 Wave 1 merge 후): mechanical wire — `scripts/check-worktree-self-ownership.sh` (thin bash wrapper, ADR-061) + `scripts/lib/check_worktree_self_ownership.py` (Python SSOT, 3-tuple verify primitive 구현) + `templates/github-workflows/worktree-self-ownership-verify.yml` + `.github/workflows/` byte-identical self-app (ADR-005) + `templates/.claude/hooks/PreToolUse-worktree-self-ownership.json.sample` (consumer opt-in cold start sample) + `tests/scripts/check-worktree-self-ownership/test_worktree_self_ownership.bats` + label-registry-v2 신규 entry `hotfix-bypass:worktree-self-ownership-verify`.
- **ContinuityAgent CRITICAL** (post-merge follow-up): plugin-codeforge#729 (title "ADR-073 Amendment 1" 슬롯 충돌 — Amendment 1 = CFP-776 / Amendment 2 = CFP-966 / Amendment 3 = CFP-689 점유 verified) → Amendment 4 로 재배정 의무. 본 Amendment 3 = self-ownership verify 3-tuple + transition trigger enum 4번째 entry 영역 / Amendment 4 (#729 재배정) = Glob false negative 별 §결정 영역 — section disjoint 보장.

## [5.92.0] - 2026-05-19

### Added (CFP-967 — parallel work sentinel mechanical wire, ADR-073 Amendment 2 §결정 1-A/1-B/1-C)

- **`scripts/check-parallel-work-sentinel.sh`** — ADR-061 thin bash wrapper dispatching Python SSOT. 3 모드 (`--mode=title-search` / `--mode=epic-state-poll` / `--mode=head-compare-sibling-commits`). `BYPASS_PARALLEL_WORK_SENTINEL=1` audit-trailed bypass (43번째 family member).
- **`scripts/lib/check_parallel_work_sentinel.py`** — Python SSOT 3 polling mode 구현: (A) title-search = CFP-NNN pattern GitHub search + 요청 CFP title 교집합, (B) epic-state-poll = Epic Issue `scope_manifest` block parse + open/closed state, (C) head-compare-sibling-commits = git log 기반 sibling commit delta. graceful degradation 3 fail-mode (`api_quota_exceeded` / `hook_self_fail` / `stale_label_grace`). exit-code 3-tier (ADR-060 §결정 15: 0=PASS / 1=reserved / 2=SETUP error).
- **`templates/github-workflows/parallel-work-sentinel-check.yml`** + **`.github/workflows/parallel-work-sentinel-check.yml`** — byte-identical self-app (ADR-005). warning-tier (continue-on-error: true). PR open/sync + daily cron + workflow_dispatch trigger. permissions top-level deny-all + job-level minimal (contents:read / issues:write).
- **`templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample`** — consumer opt-in cold start 등록 sample (deprecated channel 명시).
- **`tests/scripts/check-parallel-work-sentinel/test_parallel_work_sentinel.bats`** — bats 8 TC (TC-1 title-search hit / TC-2 miss / TC-3 epic OPEN / TC-4 head-compare delta / TC-5 graceful 403 / TC-6 hook_self_fail / TC-7 idempotent / TC-8 BYPASS).
- **`scripts/lib/test_check_parallel_work_sentinel.py`** — pytest 13 TC (TestTitleSearchHit 3 + TestEpicStatePoll 3 + TestHeadCompare 3 + TestArgparse 2 + TestExitCodes 2).
- **`tests/scripts/check-parallel-work-sentinel/fixtures/`** — 6 JSON/text fixtures (CFP-953 evidence: title-search-hit.json / title-search-miss.json / epic-state-open.json / head-compare-delta.txt / compare-api.json / api-403.json).

### Changed

- **`hooks/session-start`** — `[codeforge parallel-work-poll advisory — CFP-967 / ADR-073 Amendment 2 §결정 1-B cold start]` block 추가. lane spawn / PR open / merge transition 직전 3-mode poll 실행 지시.
- **`docs/evidence-checks-registry.yaml`** — `parallel-work-sentinel-pickup` entry `status: deferred-followup` → `warning` + `detect_command` + `workflow` path 채움 (ADR-073 Amendment 2 §결정 1-A mechanical enforcement 첫 wire).
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.34 → v2.35: `hotfix-bypass:parallel-work-sentinel-pickup` 43번째 family member 신설.
- **`docs/inter-plugin-contracts/MANIFEST.yaml`** — label_registry version v2.34 → v2.35 + CFP-967 changelog 1-line prepend.
- **`CLAUDE.md`** — GitHub Workflow 섹션 `33종` → `34종` fixture + `15 evidence-enforceable warning` → `16 evidence-enforceable warning` + `parallel-work-sentinel-check.yml — CFP-967 / ADR-073 Amendment 2` 1-line 신설.
- **`.claude-plugin/plugin.json`** — version `5.91.1` → `5.92.0` MINOR (ADR-037 — 신규 lint script + workflow runtime 활성화 = governance behavior change MINOR).

ADR-073 Amendment 2 carrier: §결정 1-A (script wire) / §결정 1-B (hooks/session-start cold start) / §결정 1-C (workflow warning tier). CFP-953 (title-based search miss evidence) + CFP-946 (Epic close 11분 gap evidence) 동일 세션 same-day 2-occurrence sentinel = escalation evidence threshold.

## [5.91.1] - 2026-05-18

### Fixed (CFP-986 post-merge — S3 result-fidelity classification↔severity disjoint, Epic CFP-858)

- **`scripts/reconcile-overlay.sh`** — `detect-repo-kind.py` 의 **classification** exit code (`0=plugin / 1=consumer / 2=mixed / 3=unknown`) 를 **severity** 채널 `_S2_MAX_EXIT` 에 무조건 전파하던 line 490-491 (`if [[ "${_ec}" -gt "${_S2_MAX_EXIT}" ]]; then _S2_MAX_EXIT="${_ec}"; fi`) 삭제. 정상 consumer repo (`detect-repo-kind` exit 1 = consumer, NORMAL) reconcile 이 `result-fidelity-aggregator.py s2_exit_to_result(1)=FAILED` 로 false `result: FAILED` 기록하던 결함 해소 (codeforge PRIMARY use case; Epic CFP-858 honest-reporting mandate 의 inverse 위반 — false SUCCESS 의 inverse = false FAILED). genuine abort case (unknown=3 / crash / enum-pollution) 의 severity signal 은 per-branch handler 가 독립 보존 (fail-closed 무약화). Epic CFP-858 IntegrationTest gate 검출 + ADR-070 verify-before-trust 직접 재현.
- **`docs/inter-plugin-contracts/reconcile-protocol-v1.md`** — §4.12 `classification_severity_disjoint_invariant` + §4.13 `classification_not_severity_clause` 명세 명확성 보강 (classification exit ≠ severity signal — `ratchet`-strengthening only, 의미 invariant 무변경, ADR-064 §self-application). reconcile-protocol-v1 version 무변경 (v1.10 유지, body 정확화).
- **`tests/integration/test_reconcile_overlay_consumer_filter.bats`** — discriminating end-to-end TC 4종 추가 (TC-INT-RF-CONSUMER → SUCCESS / TC-INT-RF-UNKNOWN → FAILED 보존 / TC-INT-RF-PLUGIN → SUCCESS / TC-INT-RF-MIXED → SUCCESS). `tests/test_result_fidelity_aggregator.py` TC-RF-3 (aggregator severity contract `s2_exit=1→FAILED`) 무변경 (aggregator 가 결함 아님).
- ADR-026 isPostMergeFix fast-pass 경로. Issue #986 (parent Epic CFP-858, relates CFP-900). ArchitectPL root-cause ADR-035 = impl + 명세 명확성 보강 (NOT design defect — §4.13 degradation_propagation semantic 자체는 sound).

## [5.91.0] - 2026-05-18

### Added (CFP-900 Phase 2 — §4.13 result_fidelity_binding runtime, Epic CFP-858 S3 마지막 Story)

- **`templates/scripts/result-fidelity-aggregator.py`** — 신설. §4.13 result enum 집계 CLI (Python stdlib only, ADR-061 외부 .py). 입력: S1 exit code (§4.11 closure resolver) + S2 exit code (§4.12 consumer-applicability filter) + post-mirror sanity check. 출력: `SUCCESS` / `SUCCESS_WITH_DEGRADATION` / `PARTIAL_FAILURE` / `FAILED` 4-value closed-set. exit code contract: 0=SUCCESS / 1=PARTIAL_FAILURE·FAILED / 2=SUCCESS_WITH_DEGRADATION / 3=internal error. `--dry-run` EC-2 (result field 미적용) 지원. `--output-file` artifact 파일 출력. filesystem-only invariant (network call 0 / gh api 0).
- **`scripts/reconcile-overlay.sh`** — §4.13 post-mirror sanity stage 삽입 (wholesale_mirror cp 후 step_4). `_S1_MAX_EXIT` / `_S2_MAX_EXIT` explicit capture (F-CR-899-10 bash subshell `||` fallback 패턴 방지). `RESULT_FIDELITY_AGGREGATOR_PY` + `CONSUMER_APPLICABLE_WHITELIST` + `RESULT_FIDELITY_OUTPUT_FILE` env seam. upgrade_event_honest_record: `result: SUCCESS` hardcode forbidden invariant 적용.
- **`templates/github-workflows/phase-gate-mergeable.yml`** — §4.13 `fast_pass_content_sanity` warning layer 추가. `.github/workflows/*.yml` 변경 시 의존 script reference mismatch detect (warning emit + PR comment). fast-pass OR-gate (`isEpicLabel || isSiblingPr || isDocOnly || isPostMergeFix`) 무변경 — orthogonal warning layer (ADR-026 Amendment 5 §결정 7, EC-5 fast-pass PASS 보존).
- **`.github/workflows/phase-gate-mergeable.yml`** — byte-identical mirror (ADR-005).
- **`docs/upgrade-events/README.md`** — upgrade event log artifact schema (result enum 4-value + EC 규칙 + 관련 SSOT).
- **`tests/test_result_fidelity_aggregator.py`** — 신설. 25 TC TDD. 8 RF (degradation_propagation matrix) + 5 SAN (post-mirror sanity) + 7 EC (edge cases EC-1~7) + 4 EXIT (exit code contract) + 4 PAT (F-CR-899 pattern avoidance). pytest framework.
- **`tests/integration/test_reconcile_overlay_result_fidelity.bats`** — 신설. 7 bats TC. TC-INT-RF-1~7. reconcile-overlay.sh 실 실행 검증 (F-CR-899-6 교훈 proxy-only 회피) + post-mirror stage 도달 verify + S1/S2 fail-closed/abort → FAILED 정직 기록 + dry-run EC-2 + ADR-061 invariant.
- **`tests/workflows/test_phase-gate-mergeable-yml.sh`** — §4.13 content sanity 7 assertion 추가 (TC-CS-1~7). byte-identical self-app verify 포함.

### Scope (CFP-900 Phase 2 invariants)

- **ADR-076 Amendment 3 §결정 3 sub-clause carrier** — transaction 사후 sanity check + result fidelity false SUCCESS 차단 clause runtime 활성화.
- **ADR-026 Amendment 5 §결정 7 carrier** — `.github/` fast-pass content sanity 1차 신호 orthogonal warning layer.
- **degradation_propagation deterministic mapping** — exit code → result enum pure function (side-effect 0). silent false SUCCESS 차단 core invariant.
- **hook_integration 순서** — S1 closure resolver → S2 consumer-applicability filter → cp → §4.13 post-mirror sanity check + result enum 집계 (mirror-전 S1/S2 vs mirror-후 layer 분리).
- **F-CR-899 패턴 방지** — F-CR-899-1(exit code spec verbatim) / F-CR-899-2(wrapper self-app honest) / F-CR-899-4(env var binding spec 정합) / F-CR-899-10(bash subshell || fallback 회피) / F-CR-899-6(bats 실 실행 검증).
- **Epic CFP-858 3-layer composite 완결**: S1 vertical closure resolver (mirror-전) + S2 horizontal consumer-applicability filter (mirror-전) + S3 temporal-post result fidelity (mirror-후).
- **marketplace atomic sync (ADR-063 §결정 5)** — 별도 sibling PR 의무 (Orchestrator 책임 영역).

## [5.90.0] - 2026-05-18

### Added (CFP-899 Phase 2 — Consumer-applicability filter runtime)

- **`templates/scripts/detect-repo-kind.py`** — 신설. §4.12 truth-table 4-way repo-kind 분류 CLI (Python stdlib only, ADR-061 외부 .py). 출력: `plugin`/`consumer`/`mixed`/`unknown`. exit code 0/1/2/3 매핑. Primary signal 3종 (`.claude-plugin/plugin.json` + `.claude/_overlay/project.yaml` + marketplace membership). `--skip-marketplace-check` offline fallback. `--check-signal` 단일 신호 probe. self_app_exemption invariant (§4.12, ADR-040 Amendment 3 §결정 7.D).
- **`templates/scripts/consumer_applicable_workflows.txt`** — 신설. consumer-applicable workflow positive whitelist manifest (per-line yml basename, `#` comment 허용). 30 consumer-applicable entries + plugin-only omit 목록 주석. §4.12 whitelist_file_format 정합.
- **`scripts/reconcile-overlay.sh`** — §4.12 consumer-applicability filter hook 삽입 (MARKER_NONE branch, §4.11 dep closure hook 직후 sibling line). `detect-repo-kind.py` 호출 → `plugin`: 전체 mirror / `consumer|mixed`: whitelist filter → plugin-only workflow skip / `unknown`: fail-closed return 2. `DETECT_REPO_KIND_PY` + `CONSUMER_APPLICABLE_LIST` env seam (test-injectable). dry-run propagation 보존 (CFP-898 FIX iter 1 lesson).
- **`tests/test_detect_repo_kind.py`** — 신설. 20 TC TDD (RED→GREEN). 4 MATRIX + 6 EC + 5 WHITELIST + 3 INTEGRATION + 1 MIXED + 1 SELFLOOP. pytest framework.
- **`tests/integration/test_reconcile_overlay_consumer_filter.bats`** — 신설. 5 bats TC (TC-INT-1~5): consumer/plugin/unknown/mixed/dry-run propagation. §4.12 hook 통합 검증.
- **`.claude-plugin/plugin.json`** — version `5.89.0` → `5.90.0` MINOR (ADR-037 정합 — runtime script 신설 + workflow hook 삽입 = behavior change MINOR). `description` 안 CFP-899 Phase 2 entry 선행 삽입.
- **`CHANGELOG.md`** — [5.90.0] entry 신설.

### Scope (CFP-899 Phase 2 invariants)

- **ADR-061 정합** — detect-repo-kind.py: 외부 .py 파일, shebang `#!/usr/bin/env python3`, UTF-8, stdlib only.
- **ADR-040 Amendment 3 §결정 7.D self-app verify** — detect-repo-kind.py 를 wrapper repo root 에서 실행 시 plugin 판정 (exit 0/2 = plugin/mixed). self_app_exemption invariant 20 TC SELFLOOP 검증.
- **reconcile-protocol-v1 v1.9 §4.12 hook_integration 정합** — sequential composition: §4.11 closure → §4.12 filter → cp.
- **ADR-083 Wave-1 declaration → Wave-2 runtime** — consumer_applicability_filter_detection action runtime 활성화.
- **fail_closed_unknown** — 신호 없는 repo = unknown → §4.12 abort (return 2), 안전 방향.
- **dry-run propagation** — MARKER_NONE branch dry_run=true 시 filter 판정 출력만, 실 abort 0 (ADR-076 §결정 3 정합).
- **marketplace atomic sync (ADR-063 §결정 5)** — 별도 sibling PR 의무 (Orchestrator 책임 영역).
- **tests 무변경 범위** — 기존 test_mirror_dependency_closure.py / test_reconcile_overlay_dep_closure.bats 변경 0.

## [5.89.0] - 2026-05-18

### Changed (CFP-946 option 1 — ADR-081 Amendment 3 §D1.D sandbox_network_required toggle)

- **`docs/adr/ADR-081-codex-worker-prompt-boilerplate.md`** — Amendment 3 신설. frontmatter `amendments[]` `amendment_id: 3` entry append. 본문 §결정 D1 표(D1.A/B/C 3-row) 에 §D1.D append (sandbox_network_required toggle codification). 4 mandatory boilerplate field: D1.A (dogfood-out path) + D1.B (current lane/phase) + D1.C (sandbox_outside_paths) + D1.D (sandbox_network_required). D1.A-C 본문 의미 변경 0건. cross-ref: ADR-052 Amendment 8 + ADR-070 Amendment 3 (CFP-946-A merged earlier — substitution-side mechanism). 본 D1.D = spawn-prompt-side declaration. 양면 chain 완결 (option 1 + option 2 + option 3 통합).
- **`.claude-plugin/plugin.json`** — version `5.88.0` → `5.89.0` MINOR.
- **`CHANGELOG.md`** — [5.89.0] entry 신설.

### Scope (CFP-946 option 1 invariants)

- **declaration-only retain** — mechanical injection layer 부재. Codex CLI runtime 자체 sandbox toggle 가능성은 codex@openai-codex plugin runtime 영역 (codeforge 측 declaration 만). Amendment 1/2 family pattern 정합 (§D5 precedent).
- **additive `ratchet` only** (ADR-058 §결정 5 + ADR-064 §결정 7) — D1.A-C 본문 의미 변경 0, scope 축소 0, Amendment 1/2 D6/D7 영향 0.
- **marketplace atomic sync (ADR-063 §결정 5)** — 별도 sibling PR 의무.



## [5.88.0] - 2026-05-18

### Changed (CFP-930 ADR-065 Amendment 3 — 9th item Story self-declared correction commit application verify)

- **`docs/adr/ADR-065-architect-phase1-mechanical-self-check.md`** — Amendment 3 신설. frontmatter `amendments[]` `amendment: 3` entry append (`date: 2026-05-18` + `cfp: CFP-930` + `summary` 안 §결정 1 표 row 9 `ratchet` 확장 + §결정 8 narrative + cross-Story pattern threshold reach (CFP-795 + CFP-906 evidence, ADR-045 §D-9) + ADR-082 Amendment 1 scope b sister + `is_transitional: false` + `sunset_justification: "N/A — permanent policy 의 ratchet 강화 (Amendment 1/2 family pattern 정합). 약화 방향(9th item 제거 / verify 의무 해제) 발의 차단."` quoted string form). `mechanical_enforcement_actions[]` `story-self-declared-correction-verify` entry append (status: `deferred-followup` — mechanical lint 자동 검출 별도 follow-up CFP scope, manual self-check tier). `related_stories[]` `CFP-930` append. 본문 §결정 1 표 row 9 append (`Story 본문 self-declared correction (~~old~~ → new / <del> HTML / 'previously: X' 패턴) chief author commit 실제 적용 verify` 항목 + 검증 방법: enumerate + `git diff` cross-check + repo-wide grep stale carry-over 0 verify). 본문 §결정 8 narrative section 신설 — 6 sub-section: §8.1 동기 (CFP-795 + CFP-906 occurrence evidence) / §8.2 신규 row 9 schema (검증 대상 + 검증 방법 3 step + RETURN 조건) / §8.3 mechanical 자동 검출 deferred / §8.4 ADR-082 Amendment 1 scope b sister / §8.5 row 1-8 본문 변경 0 invariant / §8.6 sunset_justification null quoted-string-form 의무.
- **`.claude-plugin/plugin.json`** — version `5.87.0` → `5.88.0` MINOR (ADR-037 정합 — ADR Amendment 발의 = governance behavior change MINOR, chief author 검증 의무 `ratchet` 8→9 item). `description` 안 CFP-930 entry append.
- **`CHANGELOG.md`** — [5.88.0] entry 신설.

### Scope (CFP-930 invariants)

- **doc-only fast-path (ADR-054)** — src/tests 무변경, ADR-065 Amendment 3 (본 ADR 본문) + plugin.json + CHANGELOG + marketplace sibling = 4 file 만 (marketplace 는 별도 sibling PR). 신규 ADR / 신규 lint script / 신규 workflow yml / 신규 evidence-checks-registry entry / `story-self-declared-correction-verify` action `deferred-followup` (mechanical lint 신설 별 carrier scope) / 6 lane sibling PR 0 / review-verdict-v4 schema bump 0 (cross-plugin `sibling sync` 필요 영역 = 별 carrier).
- **additive `ratchet` only** (ADR-058 §결정 5 / ADR-064 §self-application top-down `ratchet` 정합) — §결정 1 row 1-8 본문 변경 0, §결정 2-7 변경 0, Amendment 1/2 family pattern 보존, `is_transitional: false` 보존, `sunset_justification` quoted string form 의무. 약화 방향 enum 차단: 9th item 제거 / verify 의무 해제 / sunset_justification 다운그레이드 / row 1-8 본문 약화 / Amendment 1/2 family pattern revoke.
- **Cross-Story pattern threshold reach evidence** — CFP-795 (first occurrence, `feedback_codex_tp2_verify_before_trust` 8-mirror checklist) + CFP-906 (second occurrence, `~~ADR-072~~ → ADR-72` 18 occurrence 미적용 → DesignReviewPL Iter 1 P0+P1 적발). ADR-045 §D-9 정량 threshold (≥ 2) 도달.
- **marketplace atomic sync (ADR-063 §결정 5)** — 별도 sibling PR 의무 (Orchestrator 책임 영역, codeforge PR merge 직후 즉시 open · merge). `mirrored field` 4종 (`name`/`version`/`description`/`author`) verbatim parity.



## [5.87.0] - 2026-05-18

### Added (CFP-898 Phase 2 — dependency bundle integrity closure resolver runtime)

- **`templates/scripts/mirror-dependency-closure.py`** — 신규 Python stdlib 전용 closure resolver.
  AM-1 (regex_primary, PyYAML 의존 0) / AM-2 (transitive_depth_limit=1) /
  AM-3 (shell_script_only_v1: `scripts/check-[a-z0-9-]+\\.sh` + `templates/scripts/[a-z0-9-]+\\.py`) /
  AM-4 (self_app_exemption: 자체 self-loop 0 invariant). CLI: `--yml <path>` / `--all` / `--dry-run`.
  exit code 0/1/2. perf baseline: avg 0.42ms/file × 74 workflow yml (max 2.39ms, budget < 50ms).
- **`scripts/reconcile-overlay.sh` §4.11 hook** — MARKER_NONE branch 첫 라인에 dep-closure hook
  삽입 (MARKER_LINT return 2 abort pattern 답습). wrapper yml dep missing 시 reconcile abort.
- **`tests/test_mirror_dependency_closure.py`** — 15 TC unit tests (TC-DEP-1~15),
  pytest framework (ADR-005 정합). TDD RED→GREEN cycle 완료. 14 PASS + 1 SKIP (Windows symlink).
- **`tests/integration/test_reconcile_overlay_dep_closure.bats`** — 통합 테스트
  (TC-INT-1: dep-closure missing → exit 1, TC-INT-2: self-app no self-loop, TC-INT-3: syntax check).
- **`docs/evidence-checks-registry.yaml` `dependency-closure-self-test` entry** — warning-tier
  신규 entry (75번째). ADR-060 framework 정합. script: `python3 templates/scripts/mirror-dependency-closure.py --all --dry-run`.

### Changed

- **`scripts/reconcile-overlay.sh`** — MARKER_NONE 분기에 §4.11 dependency closure hook 추가
  (기존 로직 무변경, hook 삽입만). `MIRROR_DEP_PY` env var injectable (test seam 보존).
- **`.claude-plugin/plugin.json`** — version `5.86.0` → `5.87.0` MINOR
  (ADR-037 §결정 1 (c) — runtime behavior 추가 = MINOR). marketplace `mirrored field` 4종 sync 의무
  (ADR-063 atomic invariant — marketplace sibling PR 별도 open, CFP-898 Epic close 전 완료).

### Scope

- reconcile-protocol-v1 §4.11 binding block Phase 2 runtime landing. Phase 1 = ADR-076 Amendment 2 + §4.11 schema declare (wrapper PR #925).
- Story drift cleanup (Amendment 1 → 2, §4.10 → §4.11 stale refs) — sibling internal-docs PR 동반.
- ADR-068 I-1~I-5 self-check PASS (API contract / cross-module propagation / guard placement / wording SSOT / dimensional empirical).

## [5.86.0] - 2026-05-18

### Added (INCIDENT-2026-05-17 — cross-repo gh CLI safety net)

- **`hooks/cross-repo-gh-safety`** — 신규 PreToolUse hook (extensionless bash, polyglot wrapper 패턴 정합 — `run-hook.cmd` dispatch). `gh pr|issue <write-verb>` (create/edit/comment/close/reopen/merge/review/ready/lock/unlock/delete/transfer/develop/`pin`/unpin) 명령에 `--repo`/`-R` flag 또는 `GH_REPO` env (inline prefix 포함) 부재 시 `exit 2` 차단 + 한글 차단 메시지. read-only verb (view/list/checks/status/diff) = scope 외 (정보 조회, write 사고 영향 0). 비-Bash tool / command 추출 실패 = fail-open (best-effort 1차 안전망). `BYPASS_CROSS_REPO_GH_SAFETY=1` escape (scope disjoint — `BYPASS_CODEFORGE_PREREQ` / `BYPASS_WORKTREE_FIRST` 와 별도 env). 정적 properties = session-start hook 패턴 정합 (set -euo pipefail / filesystem touch 0 / network call 0 / jq 비의존 POSIX grep·sed 파싱).
- **`hooks/hooks.json`** — `PreToolUse` matcher `Bash` entry 신설 (`run-hook.cmd cross-repo-gh-safety`).
- **`skills/lane-self-write-boundary/SKILL.md`** — Cross-cutting rule cross-ref 신설: 모든 lane plugin + Orchestrator 의 GitHub self-write 시 `--repo` 명시 의무 + 물리 안전망(hook) / 가이드 차원(skill) 2중 안전망 + bypass env 명시.

### Trigger

- INCIDENT-2026-05-17 disk-pressure incident retro (`mctrader-data#94` §6 carry-over Action Item) + cross-repo PMO audit (`mctrader-hub#394`). self-incident 1건 기재: 2026-05-17 cross-repo 세션에서 `gh pr edit 94` 가 mctrader-hub cwd 에서 실행되어 의도된 mctrader-data#94 가 아닌 mctrader-hub#94 (다른 merged PR) description 을 silent overwrite, GitHub API 미노출로 원 description 복원 불가.

### Changed

- **`.claude-plugin/plugin.json`** — version `5.85.0` → `5.86.0` MINOR (ADR-037 §결정 1 (c) — 선택 hook 추가 = governance behavior change MINOR). `description` 안 INCIDENT-2026-05-17 carrier entry append. marketplace `mirrored field` 4종 (`name`/`version`/`description`/`author`) verbatim parity (별도 sibling PR, ADR-063 §결정 5).

### Scope

- src 무변경 (hook script + skill + plugin.json + CHANGELOG + marketplace sibling). 신규 ADR / lint workflow yml / evidence-checks-registry entry / 6 lane sibling PR = 0건. ADR 본문 publish (codeforge governance ADR 후보) = 별도 codeforge governance 세션 scope (retro #94 §6 + hub#394 가 trigger SSOT, mandate Out-of-scope 정합).

## [5.85.0] - 2026-05-17

### Changed (CFP-911 ADR-065 Amendment 2 — 8th item frontmatter YAML parse self-validate)

- **`docs/adr/ADR-065-architect-phase1-mechanical-self-check.md`** — Amendment 2 신설. frontmatter `amendments[]` `amendment: 2` entry append (`date: 2026-05-17` + `cfp: CFP-911` + `summary` 안 §결정 1 표 row 8 `ratchet` 확장 + §결정 7 narrative + cascade obligation invariant + CFP-851 incident commit SHA `79a4fdda0c9b4ee249edfcdb3769ef95b8113628` reference + family pattern 정합 + `mechanical_enforcement_actions[]` cross-ref 명시 + `is_transitional: false` + `sunset_justification: "N/A — permanent policy 의 ratchet 강화 (Amendment 1 family pattern 정합). ADR-064 §self-application top-down ratchet 정합. 약화 방향(8th item 제거 / check-doc-frontmatter.sh cross-ref 해제) 발의 차단."` quoted string form). `mechanical_enforcement_actions[]` `doc-frontmatter-yaml-parse` entry append (`status: existing-warning-cross-ref` + `target_section: §결정 1 row 8 (Amendment 2 CFP-911) / §결정 7 (신설)` + `progress_note` 안 신규 lint script 0건 + 기존 CFP-28 `check-doc-frontmatter.sh` PR-time strict check 의 commit-time forcing function cross-ref only 명시). `related_stories[]` `CFP-911` append. 본문 §결정 1 표 row 8 append (`Phase 1 산출물 commit 직전 chief author 가 변경한 frontmatter 보유 .md file 의 YAML parse self-validate` 항목 + `bash scripts/check-doc-frontmatter.sh <path>` PASS 검증 방법, CFP-28 strict mode cross-ref). 본문 row 8 직후 **Row 8 cascade obligation (Amendment 2 / CFP-911)** 1줄 신설 — `check-doc-frontmatter.sh` thin wrapper + `scripts/lib/check_doc_frontmatter.py` Python SSOT 두 file 의 strict mode contract (exit code semantic / strict-mode 분기 / target path coverage) 변경 시 row 8 wording 갱신 cascade 의무, manual review 의존, cascade 자동 검출 lint = 별도 follow-up CFP carrier. §결정 7 narrative section 신설 — 6 sub-section: §7.1 Incident reference (CFP-851 PR #885 amendment_log `is_transitional: false` colon-space plain scalar nested mapping ScannerError + FIX iter 1 equals form 정정 commit SHA + 현재 file state HEAD 재현 불가 + git history SSOT) / §7.2 Family pattern 정합 (Amendment 1 verbatim mirror — additive·strengthen, `sunset_justification: null` 금지 quoted string form 의무, ADR-071 family cross-pollination 차단, row 1-7 본문 변경 0, §결정 2-6 변경 0, mechanical_enforcement_actions[] 기존 cross-ref) / §7.3 Cascade obligation invariant (thin wrapper + Python SSOT 두 file dependency + cascade 의무 + manual review 의존 + 별도 follow-up CFP carrier) / §7.4 Doc-only fast-path 정합 (ADR-054 — 단일 PR, src/tests 무변경, 신규 ADR / lint / workflow yml / actions entry name = 0건) / §7.5 무약화 invariant (Self-application top-down `ratchet`, ADR-064 — 강화 방향만 허용 / 약화 방향 차단 enum: 8th item 제거 / cross-ref 해제 / `sunset_justification` 다운그레이드 / row 1-7 본문 약화 / Amendment 1 family pattern revoke / ADR-058 §결정 5 sunset_justification 의무) / §7.6 Schema invariant (review-verdict-v4 v4.2 `mechanical_self_check_passed: bool` semantic 무변경, 검증 항목 양적 7→8 확장만, schema MINOR bump 0건, 6 lane sibling PR 동반 의무 0건). `## 관련 파일` Amendment 2 sub-section 신설 — 본 ADR 본문 + `scripts/check-doc-frontmatter.sh` 무수정 cross-ref target + `scripts/lib/check_doc_frontmatter.py` 무수정 cross-ref target + plugin.json 5.84.0 → 5.85.0 MINOR + CHANGELOG.md [5.85.0] entry + `mclayer/marketplace:marketplace.json` `mirrored field` Phase 2 atomic `sibling sync`. **신규 lint script / workflow yml / 신규 ADR / evidence-checks-registry entry / mechanical_enforcement_actions[] action name (`doc-frontmatter-yaml-parse` = existing `check-doc-frontmatter.sh` cross-ref only, 신규 registry row 0건) / 6 lane sibling PR / review-verdict-v4 schema bump / cascade 자동 검출 lint = 0건** (Story §5.4 Out-of-Scope 7 항목 정합).
- **`.claude-plugin/plugin.json`** — version `5.84.0` → `5.85.0` MINOR (ADR-037 정합 — ADR Amendment 발의 = governance behavior change MINOR, chief author 검증 의무 `ratchet` 7→8 item). `description` 안 CFP-911 entry append — Amendment 2 narrative 압축 (8th item `ratchet` + §결정 7 신설 + cascade obligation + family pattern + Out-of-Scope 7 항목 + doc-only fast-path + marketplace atomic sync). marketplace `mirrored field` 4종 (`name`/`version`/`description`/`author`) verbatim parity.

### Scope (CFP-911 invariants)

- **doc-only fast-path (ADR-054)** — src/tests 무변경, ADR-065 Amendment 2 (본 ADR 본문) + plugin.json + CHANGELOG + marketplace sibling = 4 file 만 (marketplace 는 별도 sibling PR). 신규 ADR / 신규 lint script / 신규 workflow yml / 신규 evidence-checks-registry entry / 신규 mechanical_enforcement_actions[] action name (`doc-frontmatter-yaml-parse` = existing `check-doc-frontmatter.sh` cross-ref alias, 신규 registry row 부재) / 6 lane sibling PR open / review-verdict-v4 schema bump / cascade 자동 검출 lint 신설 = 0건 (Story §5.4 Out-of-Scope 7 항목 정합).
- **additive `ratchet` only** (ADR-058 §결정 5 정합 / ADR-064 §self-application top-down `ratchet` 정합) — §결정 1 row 1-7 본문 변경 0, §결정 2-6 변경 0, Amendment 1 family pattern 보존, `is_transitional: false` 보존, `sunset_justification` quoted string form 의무 (ADR-071 family `sunset_justification: null` 패밀리 cross-pollination 차단 — Codex TP#4 P0 finding 흡수 결과). 약화 방향 enum 차단: 8th item 제거 / `check-doc-frontmatter.sh` cross-ref 해제 / `sunset_justification` 다운그레이드 / row 1-7 본문 약화 / Amendment 1 family pattern revoke.
- **CFP-851 incident reference** — PR #885 ADR-071 amendment_log entry `is_transitional: false` colon-space plain scalar nested mapping ScannerError → FIX iter 1 commit SHA `79a4fdda0c9b4ee249edfcdb3769ef95b8113628` (2026-05-17 KST, equals form 정정으로 해소). 현재 file state HEAD 재현 불가 — incident SSOT = git history (`git log --grep=CFP-851`, PR #885 commit chain `1c15e79 → 79a4fdd → 0fdfe6d`). chief author **commit-time** forcing function 부재 gap → row 8 신설로 보완.
- **Cascade obligation invariant** — row 8 검증 방법 `bash scripts/check-doc-frontmatter.sh <path>` 가 thin wrapper + Python SSOT 두 file 의 strict mode contract 의존. 두 file 의 contract 변경 PR 시 row 8 wording 갱신 cascade 의무 (manual review 의존). cascade 자동 검출 lint 신설은 별도 follow-up CFP carrier (Story §5.4 row 7 정합 — scope expansion 시 brainstorm + 별도 Story).
- **Schema invariant** — review-verdict-v4 `mechanical_self_check_passed: bool` field semantic 무변경. 검증 항목 7→8 양적 확장만. schema MINOR bump 0건, 6 lane plugin sibling PR 동반 의무 0건 (`sibling sync` 면제, Story §5.3 Non-Goals 정합).
- **plugin.json 5.84.0 → 5.85.0 MINOR** (ADR-037 정합 — ADR Amendment 발의 = governance behavior change MINOR, chief author 검증 의무 `ratchet` 7→8).
- **marketplace atomic sync** (ADR-063 §결정 5) — 별도 sibling PR 의무 (Orchestrator 책임 영역, codeforge PR merge 직후 즉시 open·merge). `mirrored field` 4종 (`name`/`version`/`description`/`author`) 의 verbatim parity.

## [5.84.0] - 2026-05-17

### Changed (CFP-851 ADR-071 Amendment 4 — Conversational reporting frequency suppression contract)

- **`docs/adr/ADR-071-orchestrator-user-dialog-convergence.md`** — Amendment 4 신설 (`amendment_log` entry `amendment_id: 4` + `carrier_story: CFP-851` + `sunset_justification: null` + family pattern 정합, related_stories CFP-851 append). 본문 §결정 15 신설 — Orchestrator ↔ user dialog 의 발화 허용 touchpoint 3종 closed enumeration 명문화 + frequency vs richness 분리 invariant codify. 7 sub-section: §15.1 본질 anchor (frequency vs richness 분리 + verifiable outcome surface 경계) / §15.2 3 touchpoint closed enumeration ((a) 결과-명세 확인 / (b) 사용자만 풀 수 있는 차단 / (c) 최종 완료 보고 1회) + 산출물 channel enumeration (Story / change-plan / ADR / PR / TodoWrite panel) / §15.3 무약화 invariant — §결정 2(c) richness 보존 + Layer 1-4 + DialogFidelityAgent auxiliary + Sub-mechanism 1/2 + §결정 14 measurement 모두 보존 + 5번째 cognitive layer 신설 금지 invariant 정합 / §15.4 ADR-039 inline whitelist 1번·4번 entry scope 안 작동 declare (closed 4-entry 보존, 신규 entry 신설 0) / §15.5 closed-enum 확장 패턴 (4번째 touchpoint 신설 시 별도 CFP 의무 — §결정 13.6 정합, 본 ADR 안 3번째 closed enumeration 인스턴스) / §15.6 measurement gap declare — behavioral directive only (mechanical lint = 별도 follow-up CFP) / §15.7 sunset_justification: null 적격 (Amendment 1/2/3/4 family pattern). self-application top-down `ratchet` 단락 약화 방향 enum 확장 (3 touchpoint enum 축소 + §결정 2(c) richness 약화 차단 명시).
- **`docs/orchestrator-playbook.md` §3.14**: `Conversational reporting frequency suppression (ADR-071 §결정 15 / CFP-851 / Amendment 4)` sub-section 신설 (closed enum 확장 단락 다음, §3.15 fallback decision tree 직전). 본질 anchor + 3 touchpoint 표 + 산출물 channel enumeration + 무약화 invariant + closed enum 확장 패턴 + mechanical lint 별도 follow-up CFP 단락.
- **`CLAUDE.md` L199 (오케스트레이션 규칙 / Adversarial Debate Protocol Wave 5 단락)**: Wave 5 single-line inline 안에 `Amendment 4 (CFP-851 / §결정 15)` sentence append — 3 touchpoint closed enumeration + 무약화 invariant + ADR-039 inline whitelist 1번·4번 entry scope + 4번째 touchpoint 확장 별도 CFP 의무. line cap 320 invariant 보존 (inline 확장만, 별도 줄 추가 0).
- **`skills/user-dialog-mode/SKILL.md`**: `Conversational reporting frequency suppression (ADR-071 §결정 15 / CFP-851 / Amendment 4)` lookup mirror sub-section 신설 — playbook §3.14 + ADR-071 §결정 15 SSOT, skill body = mirror only (ADR-064 §결정 10 `normative` > skill body 우선 정합). 본질 anchor + 3 touchpoint 표 + 무약화 invariant + closed enum 확장 + mechanical lint 별도 CFP.

### Scope (CFP-851 invariants)

- **doc-only fast-path (ADR-054)** — src/tests 무변경, ADR-071 Amendment + SSOT 문서 4종만 갱신, 단일 PR, Story §1·§2·§11 필수 + §3-§10 = `N/A — doc-only fast-path (ADR-054)` 선언.
- **additive `ratchet` only** (ADR-058 §결정 5 정합) — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 2(c) richness / 3-anchor enum / 4 차원 enum / Inline whitelist 4-entry 모두 보존. `is_transitional: false` 유지, `sunset_justification: null` 적격.
- **frequency vs richness 분리 invariant** — 본 Amendment 가 좁히는 것은 발화 횟수·시점 만, 발화 시 풍부함 (3 줄 제약 거부 / 배경 포함 / Layer 1·2 preamble·declare) 모두 보존. 약화 방향 다운그레이드 (3 touchpoint enum 축소 / §결정 2(c) richness 약화) = ADR-058 §결정 5 `sunset_justification` 의무로 차단.
- **behavioral directive only** — mechanical lint (3 touchpoint 외 발화 자동 감지 / 억제-induced rework 측정) = 별도 follow-up CFP scope (§결정 10 패턴 정합, dialog-fidelity-effect precedent runtime cron measurement 동형 advisory warning tier).
- **plugin.json 5.83.0 → 5.84.0 MINOR** (ADR-037 정합 — ADR Amendment 발의 = governance behavior change MINOR).
- **marketplace atomic sync** (ADR-063 §결정 5) — 별도 sibling PR 의무 (Orchestrator 책임 영역, codeforge PR merge 직후 즉시 open·merge). `mirrored field` 4종 (`name`/`version`/`description`/`author`) 의 verbatim parity.

## [5.83.0] - 2026-05-17

### Added (CFP-821 Epic CFP-699 Wave 3 Story-7 Phase 2 — D1+D2+D3 coverage fan-out)

- **`templates/.github/ISSUE_TEMPLATE/story.yml`** (NEW) — Story 제출 Issue Form (phase:요구사항 label 자동 부착). D4 marker form-level wrap (ADR-027 Amendment 5 §결정 9 / §결정 7.A.1).
- **`templates/.github/ISSUE_TEMPLATE/discussion.yml`** (NEW) — Q&A·토론·제안 Issue Form (type:discussion label).
- **`templates/.github/ISSUE_TEMPLATE/codeforge-improvement.yml`** (NEW) — codeforge 개선 제안 Form (codeforge-improvement label, mctrader-debut lineage).
- **`templates/.github/ISSUE_TEMPLATE/config.yml`** (NEW) — Issue selector controller (`blank_issues_enabled: false` + contact_links).
- **`templates/.github/ISSUE_TEMPLATE/audit.yml`** (UPGRADED) — 기존 `.github/` SSOT 승격 + D4 marker form-level wrap 추가.
- **`templates/.github/ISSUE_TEMPLATE/bug.yml`** (UPGRADED) — 기존 `.github/` SSOT 승격 + D4 marker form-level wrap 추가.
- **`templates/.github/PULL_REQUEST_TEMPLATE.md`** (NEW) — 기존 `.github/PULL_REQUEST_TEMPLATE.md` byte-identical mirror (consumer-distributable SSOT, ADR-005).
- **`.github/ISSUE_TEMPLATE/story.yml`** (NEW, ADR-005 self-app) — byte-identical mirror of templates/.
- **`.github/ISSUE_TEMPLATE/discussion.yml`** (NEW, ADR-005 self-app) — byte-identical mirror.
- **`.github/ISSUE_TEMPLATE/codeforge-improvement.yml`** (NEW, ADR-005 self-app) — byte-identical mirror.
- **`.github/ISSUE_TEMPLATE/config.yml`** (NEW, ADR-005 self-app) — byte-identical mirror.
- **`templates/scripts/setup-branch-protection.sh`** (NEW) — D2 FORM (b) branch protection manifest 합성 + dry-run preview helper. **API write 0건** (no `gh api -X PUT/POST/PATCH/DELETE`). Administration:write 불요. ADR-066 §결정 2 scope 5종 무변경. exit 0 (no drift) / 2 (drift, informational) / 1 (error). ADR-024 Amendment 2 §결정 C step 1 자동화.
- **`docs/script-boundary.md`** (NEW) — D3 script ownership boundary taxonomy 3 분류 declarative SSOT: (1) Wrapper SSOT / (2) Consumer overlay / (3) Mixed-zone distributed templates. ADR-039/ADR-061 cross-ref.
- **`docs/evidence-checks-registry.yaml`** — `branch-protection-sync` warning-tier entry append (ADR-024 §결정 A/B/C owner, ADR-060 carrier).

### Changed (CFP-821 Phase 2)

- **`.github/ISSUE_TEMPLATE/audit.yml`** — D4 marker form-level wrap 추가 (templates/ SSOT 승격 후 byte-identical).
- **`.github/ISSUE_TEMPLATE/bug.yml`** — D4 marker form-level wrap 추가.
- **`docs/consumer-guide.md`** — §2 Issue template enumeration 3종 → 5종 + config.yml 정정 (ADR-027 Amendment 5 §결정 9 정합). §2e branch protection D2 operator manual 절차 신설 (FORM (b) drift 확인 + `setup-branch-protection.sh` 사용법).
- **`.claude-plugin/plugin.json`** — 5.82.0 → 5.83.0 MINOR.

### Tests

- **`tests/scripts/cfp-821/cfp-821-coverage-fanout.bats`** (NEW, 12 TC TDD RED→GREEN) — TC-D1-1~TC-D1-4 / TC-D2-1~TC-D2-4 / TC-D3-1~TC-D3-2 / TC-INT-1 / TC-AC11-1.

## [5.82.0] - 2026-05-17

### Added (CFP-820 Epic CFP-699 Wave 3 Story-6 Phase 2 — ADR-063 Amendment 5 §결정 15/16 3-way version atomic invariant enforcement)

- **`scripts/check-3way-version-parity.sh`** (NEW) — publisher (`.claude-plugin/plugin.json`) ↔ registry (`marketplace.json`) ↔ consumer (`project.yaml` `codeforge.version_pin.version`) 3-way byte-identical version compare. PIN_ABSENT = warning-first exit 0 (orthogonality invariant — `pin` 미선언 ≠ 버전 불일치). PIN_MALFORMED = exit 2. 3-way mismatch = blocking exit 1. ADR-063 Amendment 5 §결정 15 AC-1~AC-13 전 항목 커버. 14/14 BATS TC PASS (TDD RED→GREEN — 3 FIX iterations).
- **`scripts/read_version_pin.py`** (NEW, ADR-061 외부 .py) — `project.yaml` `codeforge.version_pin.version` YAML 파싱 helper. Stdout protocol: PIN_ABSENT / PIN_MALFORMED:<reason> / PIN_VERSION:<version>. Exit codes: 0/10(no PyYAML)/11(parse error).
- **`templates/github-workflows/version-3way-atomic.yml`** (NEW) — PR-time 3-way version atomic invariant check workflow. blocking-on-pr tier. Triggers on plugin.json / CHANGELOG.md / project.yaml / scripts 변경. `hotfix-bypass:version-3way-atomic` label bypass channel.
- **`.github/workflows/version-3way-atomic.yml`** (NEW, byte-identical self-app ADR-005).
- **`tests/scripts/check-3way-version-parity/check-3way-version-parity.bats`** (NEW, 14 TC) — TC-1~TC-14 discriminating fixture.

### Changed (CFP-820 Phase 2)

- **`docs/evidence-checks-registry.yaml`** — `version-3way-atomic` entry append (blocking-on-pr tier, owner_adr ADR-063, carrier_adr ADR-060, bypass_label hotfix-bypass:version-3way-atomic, CFP-820).
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.23 → v2.24 PATCH (hotfix-bypass:version-3way-atomic 33번째 family member, §3 yaml entry append, ADR-063 Amendment 5 §결정 16 carrier).
- **`overlay/hooks/validate_config.py`** — `codeforge.version_pin` (optional dict) + `codeforge.version_pin.version` (optional str) SCHEMA_RULES 추가 (CFP-820 / ADR-063 Amendment 5).
- **`overlay/_overlay/project.yaml.example`** — `codeforge.version_pin` commented 예시 블록 추가.
- **`docs/consumer-guide.md`** — §2i 신설 (3-way version atomic `pin` 설정 가이드, CFP-820 / ADR-063 Amendment 5 §결정 15).
- **`CLAUDE.md`** — GitHub Workflow 27종 → 28종 (`version-3way-atomic.yml` blocking-on-pr 3번째 entry 추가). blocking-on-pr 2 → 3.
- **`.claude-plugin/plugin.json`** — 5.81.0 → 5.82.0 MINOR (신규 lint script + workflow blocking-on-pr 활성화 — ADR-037). marketplace 별도 sibling PR sync 의무 (ADR-063 §결정 5).

## [5.81.0] - 2026-05-17

### Added (CFP-745 Wave 2 Story-5 Phase 2 — overlay 영역 3-way merge reconcile runtime, CFP-810/795/801/777/751 collision rebase)

- **`scripts/reconcile-overlay.sh`** (NEW, 746L) — overlay 영역 3-way merge reconcile runtime. base×marker 2×2 dispatch: BASE_OK+MARKER_VALID=3-way / BASE_ABSENT+MARKER_VALID=marker-aware first-reconcile / MARKER_NONE=wholesale_mirror / BASE_CORRUPT=abort-before-touch. EPIC-AC-4 silent overwrite 0. AC-9(a) idempotency. orphan marker abort. 4 test seam env vars. ADR-061 heredoc-python 0 (validate_sidecar.py 위임). 20/20 BATS TC PASS (TDD: RED→GREEN→REFACTOR).
- **`scripts/lib/validate_sidecar.py`** (NEW, 48L) — ADR-061 external .py. sidecar manifest schema validation.
- **`scripts/lib/reconcile_json_sidecar.py`** (NEW, 153L) — JSON sidecar RFC 6901 key-path merge helper.
- **`.claude/_overlay/.wrapper-managed-manifest.json`** (NEW) — sidecar manifest template.
- **`scripts/check-wrapper-template-managed-coverage.sh`** (NEW, 175L) — authoring-guard lint warning tier.
- **`templates/github-workflows/wrapper-template-managed-coverage.yml`** + **`.github/workflows/wrapper-template-managed-coverage.yml`** (NEW, byte-identical self-app ADR-005).
- **`tests/scripts/cfp-745/reconcile-overlay.bats`** (NEW, 645L, 20 TC) — AC-9 a/b/c + base×marker 2×2 + §7.4.1 8 failure mode TC, FIX Iter 4 TC-19 discriminating 강화.

### Changed (CFP-745 Wave 2 Story-5 Phase 2)

- **`docs/evidence-checks-registry.yaml`** — 60번째 entry `wrapper-template-managed-coverage` append (warning tier, owner_adr ADR-027, carrier_adr ADR-060). CFP-722 57th + CFP-771 58th + CFP-745 59th 정합.
- **`docs/consumer-guide.md`** — §1k 신설 overlay reconcile 가이드.
- **`.claude-plugin/plugin.json`** — 5.80.0 → 5.81.0 MINOR (신규 runtime script + workflow 활성화 — ADR-037). marketplace 별도 sibling PR sync 의무 (ADR-063 §결정 5, codeforge-improvement (i) sanity guard 적용).

### Fixed (CFP-745 Phase 2 FIX Iter 4 — CodeReviewPL findings, 구현 원인)

- **F-CR-745-1 (P1 runtime-error)**: `scripts/reconcile-overlay.sh` L133/L135 `local` keyword removed (top-level if 블록 안 함수 외부 사용 fatal). `local_overlay_parent`/`local_overlay_base` variable name prefix 컨벤션 (L122 동형). `--rollback` snapshot restore 정상화.
- **F-CR-745-2 (P1 test-quality)**: `tests/scripts/cfp-745/reconcile-overlay.bats` TC-19 강화 (exit 0 단일 + prior-state positive assert + current-state negative assert). RED proof: F-CR-745-1 미수정 시 `not ok 19: line 632 [ status -eq 0 ] failed` (genuine discriminating).
- **F-CR-745-3 (P2)**: `wrapper/stories/CFP-745.md` §8 TC 매핑 표 20 row 실제 .bats layout 정정 (§8.5 Impl Manifest 12/12 preserve).

### Incident & Lessons

- **P0 marketplace.json 0-byte 파괴 (Iter 3)**: PR #152 (`15fdca4 +0/-97`) 가 marketplace.json 전체 파괴 (git empty-blob `e69de29b`). Orchestrator strict-verify-gate 가 plugin-codeforge #798 OPEN 시점 적발 → fix-forward PR #153 (`a3dfd42`) merge → marketplace.json 복구 + ADR-063 4-field parity ALL TRUE 독립 재verify.
- **codeforge-improvement 후보 신규 (Epic close batch)**: (i) marketplace 3-file atomic write 후 git diff stat sanity check + 0-byte abort guard / (j) cross-repo state false-claim verify = gh api blob sha empty-detection 표준 / (k) bash top-level vs function-scope keyword (local/declare/typeset) lint warning-tier.

## [5.80.0] - 2026-05-17

### Changed (CFP-795 Phase 2 — post-merge-fix phase-gate fast-pass 4번째 source)

- [CFP-795] phase-gate-mergeable.yml 4번째 fast-pass source `isPostMergeFix` (3-조건 AND: ① post-merge-fix label ② hub Story §10 FIX Ledger row binding + ALLOWED_HUB_REPOS strict match (zero-trust, Codex TP#2 P1 FIX) ③ 원 MERGED PR §7 보안 non-touch 양면 SECURITY_PATHS). ADR-026 Amendment 4 §결정 6 mechanical 이행.
- [CFP-795] label-registry-v2 v2.21 — post-merge-fix entry 신설 (category: fast-pass 신규, kind:registry MINOR). cross-repo land_order 후 safe defect 정정 hotfix 경로.
- [CFP-795] hotfix-playbook cross-repo land_order post-merge 경로 신설 (§6).
- [CFP-795] consumer-guide post-merge-fix exemption 사용법 + CI terminal state classification 확장.
- [CFP-795] CLAUDE.md "GitHub Workflow" fast-pass 3→4 source + "Inter-plugin Contract" label-registry v2.21 반영.
- [CFP-795] tests/workflows/test_phase-gate-mergeable-yml.sh 신규 fixture (28 TC TDD RED→GREEN).
- [CFP-795] byte-identical self-app: templates/ ↔ .github/ phase-gate-mergeable.yml (ADR-005).

## [5.79.0] - 2026-05-16

### Changed (CFP-777 Phase 2 — DialogFidelityAgent wrapper 반영)

- CFP-777 (Epic #761 Story-1) Phase 2 — DialogFidelityAgent sibling codeforge-pmo 0.2.0 신설 + wrapper CLAUDE.md Development Agent Team 표 codeforge-pmo 2→3 + playbook §3.14 verifier auxiliary 단락 (ADR-071 Amendment 1 / ADR-042 Amendment 6 carrier, ADR-063 6-file atomic).

## [5.78.0] - 2026-05-16

### Changed (CFP-751 Phase 2 — deputy 일반 명사 → SubAgent 전수 sweep, ADR-080 `normative` 적용)

- **51 file / 282 mechanical replacements** (wrapper repo) — `docs/**` + `CLAUDE.md` + `skills/**` 영역의 lowercase 일반 명사 `deputy` → `SubAgent` (Class-A 치환). 의미 보존 (역할 / 위계 0 변경).
- **Class-B 보존 verified** — 15 `*DeputyAgent` (agent identifiers) / 41 `Deputy` (capitalized concept) / 11 `codeforge:deputy-mandate` (skill name) / 3 `skills/deputy-mandate/` (path). Phase 1 ADR-080 §결정 1-2 정합.
- **Sweep script** `.tmp/sweep_deputy_subagent.py` (ADR-061 외부 `.py`, heredoc 금지) — regex `(?<![/"'\w-])deputy(?!-)(?![A-Za-z0-9_])` (hyphen+quote lookbehind + ASCII lookahead Korean rescue), fenced code block toggle preservation. 3-iter regex refinement (Korean follow / SKILL.md basename collision / path-slug+quoted-verbatim breakage). 21 residual lowercase `deputy` 잔존 — 모두 Class-B 정당 보존 (fenced yaml schema / inline-code field names / `.yaml` files out of script scope).
- **ADR-RESERVATION row 80 verbatim user directive 보존** — `"deputy라는 표현을 쓰는데"` + `"deputy" 일반 명사` quoted text intact (Iter 3 regex fix evidence).
- **`.claude-plugin/plugin.json`** — 5.77.0 → 5.78.0 MINOR (ADR-080 `normative` 적용 carrier — Phase 2 deploying canonical SubAgent terminology). version + description `mirrored field` bump → marketplace atomic sync (ADR-063 §결정 2 선행 ordering).
- **ADR-010 §결정 2 cross-plugin `sibling sync`** — `mclayer/plugin-codeforge-design` 동형 paired PR (13 file / 142 replacement, 0.12.0 → 0.12.1 PATCH).

## [5.77.0] - 2026-05-16

### Changed (CFP-750 Phase 2 — `박제` enforcement 강화: lint scope 확장 + per-word decoupling + 전수 sweep + R9 perf fix)

- **`scripts/check-wording-dictionary.sh`** — ADR-064 Amendment 5 (CFP-750) 구현:
  - `FORBID_DICTIONARY` array → `declare -A WORD_TARGETS` per-word map (`박제`/`못 박기`/`pin`/`freezing` = expanded `docs CLAUDE.md CHANGELOG.md templates` / 별도 = 5-scope 유지). per-word scope decoupling = scope axis 정밀화 (어휘 추가 시 scope 자동 확장 차단). R2 mitigation (`별` standalone fp collateral 차단, #718 F4 disjoint carrier).
  - Bash 4+ guard (`((BASH_VERSINFO[0] < 4)) && exit 1`) + 4 precedent script consistency anchor (`check-codeforge-version-drift.sh:45` / `measure-rate-limit-fallback.sh:312-313` / `migrate-label-to-issue-type.sh:44+143`).
  - inline code-span (`` `...` ``) strip 로직 추가 (single-backtick, blockquote/fenced 분기 보존). 메타-언급 정밀 EXEMPT (file 전체 EXEMPT 차단).
  - **R9 perf algorithmic mitigation 달성 (>30x)** — `strip_exempt` per-line `printf|sed` subshell loop O(lines×fork) → 단일 awk 1-pass + filesystem memo (mktemp -d cache, strip 결과 tmp file 1회 + path 반환, grep file 직접 read). CLAUDE.md 단일 원래 >수분 → 4.5s. Windows Git Bash residual = MSYS fork-emulation-bound (algorithmic 회귀 아님). CI ubuntu-latest authoritative per R9 §4.2 (P2 advisory continue-on-error).
- **`docs/wording-dictionary.md`** — 카테고리 (a) lint scope 문구 갱신 (per-word decoupling) + frontmatter `amendments` row append (amendment 2, carrier_cfp CFP-750). Phase 1 scope gap catch-up (Phase 1 lane 실행 누락 catch-up via Phase 2).
- **`docs/evidence-checks-registry.yaml`** — `wording-dictionary` entry `detect_command` (no-arg per-word lookup mode) + `description` scope 갱신 (current_tier: warning 유지).
- **`CLAUDE.md`** — 결정원칙 forbid-list lint scope mirror 갱신 (per-word decoupling — `박제`/못박기/`pin`/`freezing` expanded / 별도 5-scope, CFP-750 cross-ref).
- **`templates/github-workflows/wording-dictionary.yml`** + **`.github/workflows/wording-dictionary.yml`** (byte-identical excl `name:`) — `on.pull_request.paths` 에 `CHANGELOG.md` 명시 + lint invocation step `run:` no-arg 전환 (per-word lookup mode default).
- **`tests/scripts/test_check_wording_dictionary.bats`** (+241) — INV-T1~T5 bats fixture (TDD): IT-4/IT-4a~d/IT-5/IT-self-app/IT-treaty-invariance + edge case (adjacent/unbalanced/double backtick/multiline) + 기존 `박제` fixture 4건 (TC-1~4 + IT-1/2 + F-3) 보존. 합성 repo tree + no-arg per-word lookup mode 정합. **40/40 GREEN PASS**.
- **`tests/contracts/test_cfp750_treaty_invariance.sh`** (+103, NEW) — INV-T2 treaty invariance helper (TestContractArchitect §8.1 #6). first-cell-identifier semantic — 표 row 변경은 field/enum/invariant 명 집합 변경 시만 flag, description cell 내부 prose 어휘 치환 허용. Change Plan §6.4 정합 (§8.0 literal vs §6.4 semantic 모순 후속 carrier).
- **`박제` 전수 sweep (12 file)** — Class-Q (blockquote `>` 사용자 verbatim) 절대 보존 + Class-B (non-quote body) `명시`/`확정`/`기재`/`포함` 문맥별도 치환 + 메타-언급 inline code-span 화. parallel-dispatch-protocol-v1.md 10회 / CLAUDE.md / CHANGELOG.md / ADR-027/037/076 / domain-knowledge×2 / contracts×4 sweep. 의미 보존 (schema 층 무변경, contract version bump 0, `sibling sync` 면제 ADR-008/010). pre-existing baseline debt (ADR-027/076/CLAUDE.md L290 + **ADR-037 `pin` baseline option A catch-up**, §6.2 item6 list 확장) 동반 정리.
- **`.claude-plugin/plugin.json`** — 5.76.0 → 5.77.0 MINOR (lint script behavior change + CLAUDE.md 의미 변경 — ADR-037 base 결정 1). version + description `mirrored field` bump → marketplace atomic sync MERGED `mclayer/marketplace#150` (ADR-063 §결정 2 선행 ordering).
- **Phase 1 wording-dictionary.md scope gap catch-up (§10 Iter 3)** — Phase 1 lane 실행 gap (Change Plan §6.1 정확 명시, Phase 1 PR 작성 시 wording-dictionary.md 미포함) Phase 2 흡수. retroactive 불가, 추가 PR 0. ADR-068 I-4 wording SSOT lockstep + INV-1 (CFP-610 mirror) = Phase 2 종료 시점 충족.

## [5.76.0] - 2026-05-16

### Added (CFP-744 Wave 2 Story-4 Phase 2 — 7-plugin family atomic upgrade (A2) + #752 consumer-distribution)

- **`scripts/atomic-upgrade-7-plugins.sh`** (NEW) — per-family transaction orchestration shell. codeforge family 7 plugin (codeforge + codeforge-{requirements,design,review,develop,test,pmo}) atomic upgrade. §4.1 CLI: `--apply` / `--dry-run` / `--rollback` / `--repo <path>` / `--help`. §4.2 algorithm: idempotency pre-check (ALL none → no-op 정상 종료, AC-9 (a)) → per-family pre-atomic snapshot → 7 plugin per-plugin reconcile (Story-3 `codeforge-upgrade.sh` 위임, semantic 분산 0 §4.4) → 사후 7-plugin 0-drift 검증 (`check-codeforge-version-drift.sh --plugin <codeforge-N>` 7회, F-002 옵션 A — codex/superpowers 구조적 배제) → drift 0 commit / drift > 0 또는 부분 실패 = 전체 7 plugin atomic rollback. §7.4.1 (a)-(i) 9 failure mode DR. ADR-037 Amendment 1 0-drift invariant. ADR-061 정합 (heredoc-python 0). user_decision_branches: 0.

### Changed (CFP-744 Wave 2 Story-4 Phase 2)

- **`scripts/codeforge-upgrade.sh` / `scripts/codeforge-upgrade.ps1`** — AC-11 parser refactor: single-positional `case "${1}"` → `while [[ $# -gt 0 ]]` loop parser. **§3.7.2-parser 7-invariant byte-level binding** 보존 (기존 `--dry-run`/`--apply`/`--rollback <version>` 동작·exit code·error 문구 byte-identical / `--repo <path>` orthogonal / mode 정확히 1개 강제 / unknown arg enum whitelist reject / downstream `_to_canonical()`→`CANONICAL_REPO_ROOT`→`input_repo_root` pipeline 무변경 / fallback byte-identical). `--repo <path>`/`CODEFORGE_REPO_ROOT` env/fallback resolve chain (AC-11 consumer_repo_root parameterization). §4.5/§7.4.1 (i) wrong-target abort-before-touch (실재 디렉터리 AND `.git` 보유 검증). Story-3 per-plugin runtime SSOT semantic 재작업 0 (additive backward-compat, AC-6 정합 — 기존 invocation 동작 byte 불변).
- **`templates/consumer-scripts.manifest`** — AC-10: 4 entry append (`scripts/codeforge-upgrade.sh` / `scripts/codeforge-upgrade.ps1` / `scripts/lib/path_normalize.py` / `scripts/atomic-upgrade-7-plugins.sh`, workflow-invoked 아님 = dependent-workflow 미부착) + 4 script `chmod +x` (git mode 100755, Check 4 executable-bit — Linux CI PASS). `bootstrap-consumer.sh` Stage 7 가 consumer repo 에 mirror.
- **`docs/consumer-guide.md`** — AC-12: §2g.2 신설 (consumer 자기 repo 7-plugin atomic upgrade end-to-end flow — 배포 경로 + `--repo` + dry-run/apply/rollback + 사후 0-drift, #752 consumer-distribution 완전 해소).
- **`docs/evidence-checks-registry.yaml`** — `atomic-upgrade-zero-drift` entry status `deferred-followup` → `Active` (Phase 2 workflow self-app land 완료).
- **`templates/github-workflows/atomic-upgrade-zero-drift.yml`** + **`.github/workflows/atomic-upgrade-zero-drift.yml`** (NEW) — byte-identical self-app (ADR-005). warning tier (ADR-060 §결정 5), `hotfix-bypass:atomic-upgrade-zero-drift` bypass channel. evidence-registry-naming-check PASS (ad-hoc `hotfix-bypass:evidence-naming` 무효화).
- **`.claude-plugin/plugin.json`** — 5.75.0 → 5.76.0 MINOR (선택 setup script 추가 — ADR-037 base 결정 1 (i)). version + description `mirrored field` bump → marketplace atomic sync 별도 sibling PR 의무 (ADR-063 §결정 5).

## [5.75.0] - 2026-05-16

### Added (CFP-743 Wave 2 Story-3 Phase 2 — upgrade CLI + UpgradeAgent (C1+C2+C3))

- **`scripts/codeforge-upgrade.sh`** (NEW) — POSIX bash thin dispatcher. 3 mode CLI: `--dry-run` / `--apply` / `--rollback <version>`. enum whitelist reject (unknown arg exit 1). user_decision_branches: 0 (no prompt). §4.4 drift-check 직접 호출 금지 (UpgradeAgent Plan stage 귀속). §4.5 path normalization via `scripts/lib/path_normalize.py`.
- **`scripts/codeforge-upgrade.ps1`** (NEW) — PowerShell thin dispatcher. sh 와 동일 reconcile semantic (9 영역 / 3 mode / user_decision_branches: 0). cross-platform parity 의무 (§4.5 path_normalize.py 공유 단일 소스).
- **`scripts/lib/path_normalize.py`** (NEW) — §4.5 6 입력 형태 path 정규화 헬퍼 (ADR-061 외부 .py 의무). 수용 형태: MSYS2/Git-Bash POSIX / Windows backslash / Windows forward-slash / 상대 / 공백 / non-ASCII UTF-8. canonical output: repo_root 절대 + forward-slash + UTF-8. 정규화 불가 = SystemExit 2 + abort-before-touch 보장. CFP-702 `_to_canonical()` precedent 동형.
- **`templates/agents/UpgradeAgent.md`** (NEW) — Orchestrator default subagent one-shot (ADR-039 §결정 1). Plan+Apply 책임 (ADR-076 §결정 5 — SessionStart hook detect 침범 0). 9 영역 reconcile + snapshot lifecycle + 사후 sanity check 3종 + event log. §7.4.1 DR 6종 (a-f) 처리 (prompt 0 보장). §11.6 idempotency.
- **`templates/upgrade-event.md`** (NEW) — C2 event log schema (doc type `upgrade_events`, ADR-041 doc-locations.yaml Phase 1 등록 완료). snapshot mirror + reconcile 결과 + (marker block 부재 시) `## Wholesale mirror losses` § 포함.
- **`scripts/tests/test_path_normalize.py`** (NEW) — §8 Test Contract impl: 18 pytest TC all PASS. 6 입력 형태 × canonical output / abort-before-touch 경계 / sh↔ps1 parity (TC-9 parity matrix).
- **`scripts/tests/test-codeforge-upgrade.sh`** (NEW) — CLI argument parser 단위 테스트: 17 bash TC all PASS. AC-1~AC-4 / §8.2 경계 조건 (unknown arg / 추가 인자 / --rollback 미제공) / TC-9 thin dispatcher drift-check 미직접 호출 / TC-10 no prompt invariant / TC-12 reconcile_protocol_version: 1.2.

## [5.74.0] - 2026-05-15

### Added (CFP-702 Wave 1 Story-2 Phase 2 — ADR-027 Amendment 3 §결정 7 D4 customization marker)

- **`scripts/check-wrapper-managed-block.sh`** (NEW) — D4 `# BEGIN/END wrapper-managed` marker pair 정합성 lint. blocking-on-pr tier. 3 checks: orphan detection (count mismatch) / nesting detect (nested BEGIN/BEGIN reject — flat-only policy) / ordering validate (END ≤ BEGIN → reject). exit 0=PASS / 1=malformed / 2=setup error. `.yml/.yaml/.sh` = `#` prefix, `.md` = HTML comment `<!-- -->` variant.
- **`scripts/migrate-existing-customization.sh`** (NEW) — retroactive idempotent marker wrap migration. `--dry-run` / `--repo-root` / `--plugin-root` args. `templates/consumer-scripts.manifest` driven. false-positive boundary: byte-diff-0 (템플릿과 동일 파일은 wrap 대상 제외). atomic wrap via `mktemp` + `mv`. mctrader 5 repo idempotent 대상.
- **`templates/github-workflows/wrapper-managed-block.yml`** (NEW) — blocking-on-pr CI workflow. jobs: bypass-check / changed-file-detection / lint-run / audit-comment / bypass-audit-comment. `hotfix-bypass:wrapper-managed-block` bypass channel (ADR-024 Amendment 3 §결정 6.A).
- **`.github/workflows/wrapper-managed-block.yml`** (NEW) — byte-identical self-app (ADR-065 §결정 1 정합).
- **`scripts/test-check-wrapper-managed-block.sh`** (NEW) — QA test suite 11 TC all PASS (TC-1a~e / TC-2 역전 / TC-3 nesting / TC-4 idempotency / TC-5 false-positive-0 / TC-6 byte-identical / TC-7 dry-run).
- **`docs/evidence-checks-registry.yaml`** — 56번째 entry `wrapper-managed-block` append (blocking-on-pr tier, owner_adr ADR-027, introduced_by CFP-702).
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.18 MINOR: `hotfix-bypass:wrapper-managed-block` 26번째 family member (N-1 anomaly 정정 — Phase 1 §결정 7.D claim 23번째 → actual 26번째, parallel session CFP-685/688 반영).
- **`docs/inter-plugin-contracts/reconcile-protocol-v1.md`** — v1.1 MINOR: `customization_preservation_entry.marker_block_syntax` 확장 — file-type별도 comment prefix / flat-only nesting policy / lint/migration script / false-positive boundary / lint_tier SSOT.
- **`CLAUDE.md`** — GitHub Workflow 섹션 26종 → 27종: `wrapper-managed-block.yml` blocking-on-pr entry 추가. `version-bump-atomic-check.yml` 단독 → `version-bump-atomic-check.yml` + `wrapper-managed-block.yml` 2개 blocking-on-pr 기재.

### Why

D4 customization marker 의무화 (ADR-027 Amendment 3 §결정 7): consumer `# BEGIN wrapper-managed` / `# END wrapper-managed` block 경계 lint로 plugin update 시 consumer customization wholesale loss 방지 (blocking-on-pr = HIGH risk). CFP-699 Wave 1 Story-2. Story-1 (CFP-701) reconcile-protocol-v1 §4.3(b) trigger prerequisite 충족.

### Compatibility

- 신규 blocking-on-pr CI: `wrapper-managed-block.yml` — marker 부재 기존 consumer는 `scripts/migrate-existing-customization.sh` retroactive wrap (idempotent, dry-run 지원)
- label-registry-v2 v2.18 (MINOR) — 기존 hotfix-bypass label 경로 무변경

## [5.73.0] - 2026-05-15

### Added (CFP-688 Phase 2 sub-PR (c) — ADR-026 Amendment 3 §결정 5.G.b actionlint + §결정 5.G.d KPI sentinel + TC-4/TC-7 extract-security-ai)

- **`scripts/extract-security-ai.sh`** (NEW) — ADR-061 §결정 1 외부 script. lanes.security_ai 3-state extraction (true / false / missing). yq primary → python3 fallback. TC-4 carrier. Inv-2 fail-closed strict: missing → caller treats as phase:보안-테스트.
- **`.github/workflows/actionlint-check.yml`** (NEW) — PR-time actionlint v1.7.12 syntax validation warning-tier CI step. `hotfix-bypass:actionlint` bypass channel. ADR-026 §5.G.b prevention layer.
- **`templates/github-workflows/actionlint-check.yml`** (NEW) — byte-identical mirror (ADR-005 §결정 2 정합).
- **`templates/.git-hooks/pre-commit.sample`** (NEW) — opt-in actionlint pre-commit hook. binary 부재 시 warning emit + bypass (T-NEW-1 forced install 차단). scripts/install-git-hooks.sh 자동 디스커버리 대상.
- **`.github/workflows/post-merge-followup-success-rate-kpi.yml`** (NEW) — rolling 14-day success rate sentinel (sentinel ≥ 90%). cron weekly Monday 09:00 UTC + workflow_dispatch. breach 시 Issue 자동 생성. ADR-026 §5.G.d KPI detection layer.
- **`templates/github-workflows/post-merge-followup-success-rate-kpi.yml`** (NEW) — byte-identical mirror (ADR-005 §결정 2 정합).
- **`scripts/check-post-merge-followup-success-rate.sh`** (NEW) — thin bash wrapper. gh run list 14-day aggregation. exit 0/1/2 (ADR-060 §결정 15 3-tier). SENTINEL_PCT/WINDOW_DAYS env override 지원.
- **`docs/evidence-checks-registry.yaml`** — 54번째 entry `workflow-actionlint-precommit` + 55번째 entry `post-merge-followup-workflow-success-rate-kpi` append (각 warning tier, owner_adr ADR-026, introduced_by CFP-688).
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.17 PATCH: `hotfix-bypass:actionlint` 24번째 + `hotfix-bypass:post-merge-followup-success-rate` 25번째 family member (combined single bump). (label-registry-v2 frontmatter CFP-708 Phase 2 v2.17 bump 선행 정정 동반 — CFP-708이 CHANGELOG에 v2.17 기록 후 frontmatter 미갱신, 본 sub-PR에서 PATCH 추가).

### Changed (CFP-688 Phase 2 sub-PR (c))

- **`.github/workflows/post-merge-followup.yml`** — Step 2 TC-7 semantic fix: lanes.security_ai 3-state unified (explicit false → phase:구현-테스트 / missing|true → phase:보안-테스트 fail-closed). inline _read_security_ai() heredoc → `scripts/extract-security-ai.sh` external call (ADR-061 §결정 1 + ADR-026 §결정 5.G.b). dead-code TERMINAL_PHASE pre-set 수정.
- **`templates/github-workflows/post-merge-followup.yml`** — byte-identical mirror (ADR-005 §결정 2 정합).
- **`docs/adr/ADR-026-post-merge-automation.md`** — frontmatter mechanical_enforcement_actions[] 2 entry `status: deferred-followup` → `active` + progress_note 갱신.

## [5.72.0] - 2026-05-15

### Added (CFP-708 Phase 2 — ADR-074 CLAUDE.md Amendment ref drift detection lint)

- **`scripts/check-claude-md-amendment-ref.sh`** — bash wrapper (ADR-061 §결정 1 정합, 25+ lines = Python 위임). `scripts/lib/check_claude_md_amendment_ref.py` 경유 실행.
- **`scripts/lib/check_claude_md_amendment_ref.py`** — Python 구현 (~270 lines). CLAUDE.md 안 `[ADR-NNN](...)` 링크 + 인접 `Amendment N (CFP-NNN)` 패턴 detect + ADR frontmatter `amendment_log[]`/`amendments[]` 배열 길이 비교. exit code 3-tier (0=PASS/1=drift/2=setup error). `amendment_log` + `amendments` 두 형식 모두 지원.
- **`templates/github-workflows/claude-md-amendment-ref-drift.yml`** — PR-time warning tier lint workflow (paths: CLAUDE.md + docs/adr/**). `hotfix-bypass:claude-md-amendment-ref` label bypass + audit comment 자동 발의 (ADR-024 Amendment 3 §결정 6.A).
- **`.github/workflows/claude-md-amendment-ref-drift.yml`** — byte-identical self-app (ADR-005 §결정 2 정합).
- **`tests/scripts/check-claude-md-amendment-ref.bats`** — 5 TC TDD Red-Green PASS: TC-1 stale / TC-2 latest / TC-3 no-amendment-log / TC-4 multi-Amendment / TC-5 setup-error.
- **`docs/evidence-checks-registry.yaml`** — 53번째 entry `claude-md-amendment-ref-drift-check` append (warning tier, owner_adr ADR-074, recurrence count=2 threshold=2, promotion_trigger adr_draft_emitted).
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.17 MINOR: `hotfix-bypass:claude-md-amendment-ref` 23번째 family member.

Cross-ref: ADR-074 / ADR-060 / ADR-024 Amendment 3 / CFP-477 retro 후보 3 carrier / 2 drift evidence (CFP-627 + CFP-477 F-DR-001 P1). 5.69.0/5.70.0/5.71.0 skip: CFP-707/CFP-688 main forward 경쟁 (rebase friction 7th wave — CFP-477 hook 직접 적용 영역).

## [5.71.0] - 2026-05-15

### Fixed (CFP-688 Phase 2 sub-PR (b) — ADR-026 Amendment 2 §결정 5.E + §결정 5.F drift fix, 5.70.0 skip: CFP-708 marketplace pre-sync collision)

- **F6.1 — Action 1 §결정 5.E strict regex matching** (`post-merge-followup.yml` Action 1 ISSUE_NUM 해석 블록):
  - `in:title` qualifier 추가: `--search "in:title ${STORY_KEY}"` (기존 bare search → GitHub tokenizer prefix collision 차단)
  - env indirection 추가: `STORY_KEY: ${{ steps.meta.outputs.story_key }}` (T2 HIGH shell expansion 완화, CFP-545 §결정 5.E)
  - jq post-filter word boundary: `select(.title | test("^${STORY_KEY}\\b"))` (CFP-545 vs CFP-5451 exact match 보장)
  - null jq 결과 방어: `[ -z "$ISSUE_NUM" ] || [ "$ISSUE_NUM" = "null" ]`
- **F6.2 — concurrency.group §결정 5.F namespace prefix** (`concurrency.group`):
  - `${{ github.repository }}-` prefix 추가 → `post-merge-followup-mclayer/plugin-codeforge-<PR#>` (namespace clarity + forward-compat)
  - `cancel-in-progress: false` 보존 (§결정 5.D partial Issue close state 차단 invariant)
- **byte-identical mirror**: `templates/github-workflows/post-merge-followup.yml` + `.github/workflows/post-merge-followup.yml` 동기화 (AC-4)

## [5.69.0] - 2026-05-15

### Changed (CFP-707 — ADR-038 Amendment 4 TodoWrite 4-marker vocabulary swap, doc-only fast-path ADR-054)

- **ADR-038 §결정 2 — 4-marker vocabulary swap (직관성 정정)**:
  - `⏳ pending` → `⬜` (TodoWrite checkbox 패러다임 정합 — 시작 안 됨 empty checkbox 직관)
  - `🔄 in_progress` → `⏳` (모래시계 = 시간 흐름 = 진행 중 자연 인지 모델 align)
  - `❌ FIX 원인 lane` → `🔄 FIX 검출 lane` (회전 = retry trigger semantic align, §결정 3 위치 swap 동반)
  - `✅ completed` 변경 0건
- **ADR-038 §결정 3 — FIX 마커 부여 위치 정정**: 원인 lane → **검출 lane** 부여 (직관 align — "검출한 쪽이 retry 를 trigger"). 책임 추적 (FIX-N 원인 판정) 의미 영역 변경 0건 — 원인 lane content suffix `FIX-N 원인 · <판정>` 으로 보존 (lane PASS evidence + FIX trigger origin 양 보존).
- **ADR-038 §결정 6 — 재진입 row marker swap**: 기존 `❌` 표기 → 검출 lane `🔄` 마커 (§결정 3 정합).
- **ADR-038 frontmatter `amendments[]` Amendment 4 entry append** + **`amendment_log` entry append** (sunset_justification metric/who/how 3-tuple — Story 100 cycle retro grep).
- **playbook §14.3** sample swap + `⏸` deprecated → `⬜` 통일 (Story 시작 시 init marker).
- **playbook §14.4** Status enum 표 4 row swap + blocked / waiting 정정 + 활성 lane row 예시 swap.
- **playbook §14.5** Trigger 표 14 row swap (Story 개시 / Lane 진입 / Deputy spawn-return / 병렬 dispatch / CI gate / R11 fast-path / Lane PASS / Lane FIX / Lane 재진입 / RESET / Lane N/A).
- **playbook §14.7** Render flow step 5 detail swap (Lane 진입 / Agent return / Lane PASS / Lane FIX 4 sub-bullet — semantic 정정 동반).
- **playbook §14.8** Resume re-build 4-marker 변환 swap.
- **CLAUDE.md L202** mirror reference 정정 (`(⏳ 🔄 ✅ ❌)` → `(⬜ ⏳ ✅ 🔄)` + 검출 lane / 원인 lane 의미 정정).

### Rationale

사용자 dialog 5 turn 합의 (2026-05-15 KST):
- `⏳` (모래시계 글리프) 의 pending semantic 이 "시간 흐름 = 진행 중" 직관과 충돌
- `❌` 가 root cause lane (= 잘못한 쪽) 에 부여되는 §결정 3 의 책임 추적 semantic 이 "검출한 쪽" 직관과 충돌
- swap 후 시각 모델: `⬜` (시작 안 됨) / `⏳` (진행 중) / `✅` (완료) / `🔄` (FIX 검출, retry trigger 회전)

### Cascade resolution

- 5.67.0 skip: CFP-442 marketplace pre-sync drift (Phase 2 wrapper PR pending 시점 marketplace 만 사전 sync, 2026-05-14)
- 5.68.0 skip: CFP-685 sub-PR (c) PR #714 merge 2026-05-15T05:37:02Z (CFP-707 worktree base 이후 발생)
- 5.69.0 atomic align: ADR-063 §결정 5 marketplace sibling PR 동시 open + 선행 merge 의무

Cross-ref: ADR-038 / ADR-054 / ADR-063 / ADR-067 §결정 3 (Pause-and-resume) / ADR-073 (verify-before-assert).

## [5.68.0] - 2026-05-15

### Added (CFP-685 — ADR-065 Amendment 1 §결정 6 family scope self-app invariant + sibling-workflow-parity enforcement)

- **CFP-685 sub-PR (a)** — ADR-065 Amendment 1 §결정 6 신설: family scope self-app invariant (templates/github-workflows/*.yml ↔ .github/workflows/*.yml byte-identical parity 의무 포함 전체 family scope 확장) + ADR-005 §결정 2 cross-ref 강화 + MANIFEST.yaml 갱신 (PR #694, 2026-05-15).
- **CFP-685 sub-PR (b)** — `scripts/check-sibling-workflow-parity.sh` 신설 (sha256sum/shasum 2-tier hash + exit 0/1/2 ADR-060 §결정 15 정합) + `templates/github-workflows/sibling-workflow-parity.yml` + `.github/workflows/sibling-workflow-parity.yml` (byte-identical self-app, ADR-005) + `docs/evidence-checks-registry.yaml` 51번째 entry `auto-phase-label-sibling-parity` (warning tier, owner_adr ADR-065) + `docs/inter-plugin-contracts/label-registry-v2.md` v2.16 MINOR (`hotfix-bypass:auto-phase-label-sibling-parity` 21번째 family member) (PR #705, 2026-05-15).
- **CFP-685 sub-PR (c)** — `CLAUDE.md` GitHub Workflow 단락 갱신 (`templates/github-workflows/` 26종 → 27종 / 8 → 9 evidence-enforceable warning, `sibling-workflow-parity.yml` entry 추가) + `plugin.json` 5.66.0 → 5.68.0 MINOR (ADR-037 — 신규 workflow + script + evidence-registry entry 신설 runtime 활성화) + `CHANGELOG.md` [5.68.0] entry + marketplace atomic sync (ADR-063 §결정 5 — separate sibling PR, 2026-05-15).

Cross-ref: ADR-065 / ADR-060 / ADR-005 / ADR-066 / label-registry-v2 v2.16.

## [5.67.0] - 2026-05-14

### Added (CFP-442 Phase 2 — evidence-registry anomaly lint carrier)

- **`scripts/check-evidence-registry-anomaly.sh`** — thin bash wrapper (8-10 lines, ADR-061 §결정 1 정합). `scripts/lib/check_evidence_registry_anomaly.py` 경유 실행.
- **`scripts/lib/check_evidence_registry_anomaly.py`** — Python helper (~300 lines). 2 sub-check:
  - sub-check 1: `docs/evidence-checks-registry.yaml` entries ↔ ADR-060 §결정 13 표 Group A 18 entry 1:1 inventory parity. status=Retired skip (EC-6, marketplace-sync 예외).
  - sub-check 2: `scripts/check-*.sh` + `.github/workflows/*.yml` + `templates/github-workflows/*.yml` 4-criteria AND (detect_command / workflow trigger / owner_adr ADR-NNN / continue-on-error) 후보 식별도 + registry 미등록 감지.
  - ALLOWLIST 4-path self-exempt (purpose a: candidate exclude 3 paths) + start-up assertion (purpose b: 4 paths 전체 EC-9 drift guard). ADR-068 I-3 guard placement intent 정합.
  - Exit code 3-tier (Amendment 2 §결정 15): 0=PASS / 1=anomaly DETECTED / 2=META-ERROR (EC-7/EC-8/EC-9).
- **`templates/github-workflows/evidence-registry-anomaly-check.yml`** — warning mode workflow (continue-on-error: true). PR trigger: scripts/check-*.sh + .github/workflows/*.yml + templates/github-workflows/*.yml + docs/evidence-checks-registry.yaml + docs/adr/ADR-060-*.md.
- **`.github/workflows/evidence-registry-anomaly-check.yml`** — byte-identical self-app mirror (ADR-005 정합).
- **`docs/evidence-checks-registry.yaml` 51번째 entry** — `evidence-registry-anomaly` (warning tier, ADR-060 Amendment 11 §결정 25, self-carrier CFP-442 제외 convention, sibling_dependencies 11 entry chain).
- **`tests/scripts/check-evidence-registry-anomaly/`** — pytest suite: TC-1 (positive current-state, mandatory) + TC-2 (negative missing lane-evidence-trail, mandatory) + TC-3 (ALLOWLIST self-exempt in-place, mandatory) + TC-4 (sub-check 2 fake lint, optional) + TC-5 (META-ERROR broken yaml, optional).
- **ADR-060 Amendment 11 framework self-application 5-piece chain 완성**: CFP-389 → CFP-390 → CFP-455 → CFP-508 → **CFP-442** = framework self-aware governance 도달.

## [5.66.0] - 2026-05-15

### Added (CFP-477 Phase 2 — pre-push auto-rebase hook sample carrier)

- **`templates/.claude/hooks/pre-push-auto-rebase.sh.sample`** — opt-in pre-push hook (env `PRE_PUSH_AUTO_REBASE=1`) advisory abort + 4-line guidance when branch behind origin/main. hook 안 직접 `git pull --rebase` 실행 금지 (git-scm hook semantics 정합 — advisory abort only). CFP-447 `pre-push.sh.sample` sibling pattern 차용. ADR-063 §결정 5 sublayer (pre-push auto-rebase guidance) carrier.
- **`tests/scripts/pre-push-auto-rebase.bats`** — 5 TC bats (TC-1 env unset no-op / TC-2 up-to-date no-op / TC-3 behind abort+guidance / TC-4 fetch failure graceful exit 0 / TC-5 detached HEAD skip).
- **`docs/consumer-guide.md` §1j** — consumer-facing opt-in usage instruction (4-line guidance 해석 포함).
- **rebase friction relief** — 4-Story evidence (CFP-423 / CFP-436 / CFP-441 / CFP-455) + CFP-627 pause-and-resume (baseline drift cadence ~30분/commit) carrier resolution.

## [5.65.0] - 2026-05-15

### Added (Story flow + lane orchestration)

- **CFP-673 marketplace-drift-detection artifact Phase 2 sub-PR (c) — verification + version bump (ADR-063 Amendment 3 §결정 13 Phase 2 carrier complete)**: bats TC-6~10 5 TCs append (E-4a 401 Issue create + E-4b 429 fail-open + E-4c 5xx fail-closed-with-retry + E-2 registration leak + TC-10 KPI seed gate_status warming verify) + `docs/kpi/marketplace-drift-rate.json` seed (gate_status: warming, owner_adr: ADR-063, carrier_story: CFP-673) + `docs/security/pat-rotation-log.md` PENDING placeholder → actual grant row (ADR-066 Amendment 2 §결정 3 + CFP-673 prerequisite resolved) + plugin.json 5.64.0 → 5.65.0 MINOR (ADR-037) + marketplace atomic sync (ADR-063 §결정 5 — separate sibling PR 선행 merge 의무).

## [5.64.0] - 2026-05-15 — CFP-671 [RETRO-CFP-662] story-init.yml workflow 2 bug regression fix (combined single PR)

### Fixed

- **Bug 1 — KEY 추출 regex bug** (ADR-036 Amendment 1 carrier):
  - 현재 `Compute story key` step 가 title 의 `[CFP-NNN]` reservation pattern 인식 못 함 → Issue # fallback only
  - **Fix**: Python inline heredoc 안 `re.search(r'\[?([A-Z]+-\d+)\]?', title_clean)` pattern 추출 + prefix guard (`key_from_title.startswith(prefix + "-")`) + title pattern matched + prefix matched 시 title KEY 우선 + 부재 OR mismatch 시 `f"{prefix}-{issue_number}"` fallback (ADR-036 결정 1 race-free guarantee 보존)
  - **Cross-project KEY injection 차단**: title `[ABC-123]` + PREFIX=CFP 시 prefix guard 가 Issue # fallback 으로 강등 (security guard)
- **Bug 2 — CFP-596 cross-repo write code phantom changelog** (ADR-013 Amendment 5 + Amendment 6 carrier):
  - CFP-596 의 두 commit (Phase 1 `150aac0` ADR-013 Amendment 5 + Phase 2 `b8dfddb` workflow yml cross-repo write code) 가 main branch 에 통합되지 않은 상태로 잔존 (verify-before-trust evidence: `git branch --all --contains 150aac0` = `CFP-596` branch 단독)
  - CHANGELOG.md `[5.43.0]` / `[5.44.0]` entry 만 main 진입 — phantom changelog 영역 (declared ↔ actual 미반영 drift)
  - **Fix**: CFP-596 의 ADR-013 Amendment 5 본문 + story-init.yml workflow body (6 step: project_config family detect + key + existence_check two-stage + parse + render + create-branch-codeforge + create-branch-consumer + cross-repo PR + Issue body cross-repo link) 전체 verbatim port via `git show b8dfddb:templates/github-workflows/story-init.yml > templates/github-workflows/story-init.yml`
  - CFP-661 의 intended addition (PR create step `continue-on-error: true` + post-fail Issue comment) 동시 cherry-pick port (consumer branch 영역에만 적용)
- **story-init.yml restoration scope**:
  - 364 lines → 624 lines (CFP-596 base 610 + CFP-671 Bug 1 patch ~10 + CFP-661 graceful degradation 보존 ~50, net +260)
  - `.github/workflows/story-init.yml` byte-identical mirror (ADR-005)

### Added

- **`docs/adr/ADR-036-project-key-atomic-reservation.md` Amendment 1**: Title regex precedence 명시.
  - 결정 1: Title pattern matched + prefix matched → title KEY 우선
  - 결정 1 fallback: pattern absent OR prefix mismatch → Issue # fallback (race-free guarantee 보존)
  - 결정 2: Cross-project KEY injection 차단 (security guard)
  - frontmatter `amendment_log[]` row 1 + `related_stories[]` CFP-671 append
- **`docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md` Amendment 5 (CFP-596 verbatim port via CFP-671 actual integration)**: Story-init workflow cross-repo write 의무 codification.
  - 결정 1-7 (location semantics 재정의 / cross-repo write 패턴 / PAT 재사용 / 거부된 대안 / 잔여 Issue 처리 / 6 lane sibling no-op / two-stage existence_check)
- **`docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md` Amendment 6 (CFP-671 신설)**: CFP-596 phantom changelog incident retrospective.
  - 결정 1: CFP-596 본문 actual integration via CFP-671
  - 결정 2: phantom changelog detection lint carrier follow-up (별도 CFP-NNN)
  - 결정 3: CFP-661 PR description vs actual diff parity (별도 retro carrier)
- **`tests/workflows/test_story-init-yml.sh` (신설 — CFP-596 base T-1~T-10 restoration + T-11~T-14 CFP-671 신규)**:
  - T-1~T-10: CFP-596 base (codeforge family / consumer / fail-closed / idempotency / commit message / byte-identical / slug normalize — 39 assertions)
  - T-11~T-13: Bug 1 KEY title regex precedence + prefix guard + cross-project KEY injection 차단 (10 assertions)
  - T-14: CFP-661 graceful degradation (pr_create_consumer + continue-on-error + post-fail fallback comment — 4 assertions)
  - Total: **52 TC PASS**
- **`tests/workflows/test_story-init-key-logic.py` (신설 — ADR-061 정합 외부 .py)**: 5 semantic TC PASS (T-11.S~T-15.S):
  - T-11.S: title pattern matched → title KEY 우선
  - T-12.S: no title pattern → Issue # fallback
  - T-13.S: prefix mismatch → Issue # fallback (cross-project KEY injection 차단)
  - T-14.S: title pattern without [STORY] prefix → title KEY 우선
  - T-15.S: title pattern unbracketed → title KEY 우선

### Changed

- **`.claude-plugin/plugin.json` 5.63.0 → 5.64.0 MINOR bump**: ADR-037 — workflow behavior change carrier (KEY 추출 logic + cross-repo write 분기 + CFP-661 graceful degradation 통합).

### Notes

- **CFP-596 regression analysis (PMO retro carrier)**: 본 영역 진행 중 CFP-596 의 두 commit 이 main 미통합 + CFP-661 의 PR description (additions=191 / deletions=2) ↔ actual diff (454 lines, 242+/212-) mismatch 발견. ADR-013 Amendment 6 에 incident 명시 + 별도 CFP-NNN 후속 carrier 의무 (PR description vs actual diff parity lint + phantom changelog detection lint).
- **verify-before-trust evidence (ADR-070 / ADR-073)**:
  - `git log -- templates/github-workflows/story-init.yml` 출력 = CFP-596 commit 부재
  - `git branch --all --contains 150aac0` 결과 = `CFP-596` branch 단독 (main / origin/main 미포함)
  - CFP-596 본문 b8dfddb verbatim port via `git show b8dfddb:templates/github-workflows/story-init.yml`
  - 52 + 5 = 57 TC PASS evidence (RED→GREEN cycle 진행)
- **doc-only fast-path 영역 외 (ADR-054)**: src 변경 (workflow yml 364 → 624 lines) + tests 신설 (52 + 5 TC) → regular Story scope. Combined single PR scope (Phase 1 + Phase 2) 정합 (작은 영역 — 1 workflow + 2 tests + 2 ADR Amendment + 1 plugin.json + 1 CHANGELOG entry).
- **ADR-063 §결정 5 marketplace atomic sync 의무**: plugin.json 5.63.0 → 5.64.0 MINOR + marketplace.json `mirrored field` 4종 (`name`/`version`/`description`/`author`) sync. marketplace sibling PR 선행 merge 의무 (ordering invariant).
- **ADR-061 정합**: `tests/workflows/test_story-init-key-logic.py` 외부 .py file 작성 (workflow yml 안 heredoc 와 verbatim 동일 logic mirror — testable). multi-line Python heredoc escape 영역 회피.
- **Internal-docs cross-repo write**: `mclayer/codeforge-internal-docs/wrapper/stories/CFP-671.md` + `mclayer/codeforge-internal-docs/wrapper/change-plans/cfp-671-story-init-regression-fix.md` 작성 (ADR-013 dogfood-out 정합, manual fallback path — 본 carrier 가 story-init.yml 영역 정정 자체이므로 dogfood-out workflow 자동 미동작).
## [5.63.0] - 2026-05-14 — CFP-662 Phase 2 — bootstrap-labels.yml workflow body + self-app + Test Contract (8 test)

### Added

- **`templates/github-workflows/bootstrap-labels.yml` 신설** (26번째 fixture, CFP-662 Phase 2): consumer repo PR open 시 codeforge 필수 label set 자동 bootstrap. `on.pull_request.types: [opened]` only (synchronize 제외 — chicken-and-egg + 무한 루프 회피). `concurrency.group: bootstrap-labels-${PR_NUMBER}`. `continue-on-error: true` (ADR-060 §결정 5 warning tier). `hotfix-bypass:bootstrap-labels` conditional skip + audit comment 자동 발의. token: `CODEFORGE_CROSS_REPO_PAT` fallback `GITHUB_TOKEN`. `bash scripts/bootstrap-labels.sh` (idempotent 3-fallback chain 활용, ADR-061 외부 script convention). `timeout-minutes: 5`. RETRO-MCT-104 carrier (mctrader-data MCT-104 Phase 2 PR #14 recurrence 방지).
- **`.github/workflows/bootstrap-labels.yml` byte-identical mirror** (ADR-005 self-application invariant). diff 0 byte 확인.
- **`tests/workflows/test_bootstrap_labels_workflow.bats`** 10 TC (T-1~T-8 + T-meta-1/2) — TDD RED(9f1bcd5) → GREEN(dd56276) 전환 완료.

### Changed

- **`.claude-plugin/plugin.json` 5.62.0 → 5.63.0 MINOR bump**: ADR-037 — workflow 신설 (consumer-impact, runtime 활성화 = behavior change).

### Notes

- **ADR-060 Amendment 10 §결정 24 정합**: warning tier 10번째 entry `bootstrap-labels-precondition` — Phase 1 PR에서 declarative SSOT 선확립, Phase 2 PR에서 workflow body 본 구현.
- **ADR-005 self-application**: `templates/github-workflows/bootstrap-labels.yml` ↔ `.github/workflows/bootstrap-labels.yml` byte-identical diff 0 verified.
- **mctrader-data PR replay sentinel (AC-4)**: bootstrap-labels.sh 이미 존재 + workflow 호출 경로 확립 → MCT-104 recurrence 방지 구조 완성.
- **marketplace sync**: plugin.json 5.62.0 → 5.63.0 MINOR (ADR-037). marketplace.json 동반 sync 의무 (ADR-063 §결정 5 atomic invariant — 별도 sibling PR, 선행 merge 의무).

## [5.63.0] - 2026-05-14 — CFP-662 sibling (Issue #669) Phase 1 — wrapper `sibling sync` design-output-v2 v2.3 (canonical codeforge-design PR #42 SHA a6aa5502 verbatim mirror)

### Added

- **`docs/inter-plugin-contracts/design-output-v2.md` v2.2 → v2.3 verbatim mirror** (canonical codeforge-design PR #42 SHA `a6aa5502404ab5a9e7f81b865af62889466e829a`): `chief_author_artifact.spec_invariant_measurement_required: bool` optional field 신설 (default `false`). chief author artifact 가 spec invariant measurement 의무를 명시했는지 audit marker. additive minor — deputies_results / writes_completed 변경 없음. v2.2 consumer backward-compat 보장. ADR-010 `sibling sync` + ADR-008 §결정 2 MINOR bump 정합.
- **frontmatter `mirrored_from_canonical` block** (`sibling sync` annotation — ADR-010 §결정 3): `repo: mclayer/plugin-codeforge-design`, `sha: a6aa5502404ab5a9e7f81b865af62889466e829a`, `pr: 42`.
- **§6 Changelog `v2.3 (CFP-662)` sub-section** 신설: additive minor 상세 (trigger / purpose / schema enumeration).

### Changed

- **`docs/inter-plugin-contracts/MANIFEST.yaml` design_output entry**: `contract_version: "2.1"` → `"2.3"` 2-minor jump (Option A — SSOT alignment: 파일 자체 "2.3" 기준 / audit trail: skip v2.2 explicit 기록 / atomic: drift 0 해소 / rollback simplicity). Note: MANIFEST 은 "2.1" 상태였으나 파일은 "2.2" 였던 pre-existing drift 동시 해소.
- **`.claude-plugin/plugin.json` 5.62.0 → 5.63.0 MINOR bump**: ADR-037 — inter-plugin contract version bump + new contract field 도입 (governance behavior change carrier).

### Notes

- **doc-only fast-path (ADR-054) 정합**: Phase 1 PR 단독. src/tests 무변경. Phase 2 PR 부재.
- **ADR-010 §결정 3 `sibling sync` ordering 정합**: canonical codeforge-design PR #42 MERGED (2026-05-14T13:17:49Z, SHA `a6aa5502404ab5a9e7f81b865af62889466e829a`) → wrapper `sibling sync` PR 후속.
- **ADR-008 §결정 2 MINOR 정합**: `chief_author_artifact.spec_invariant_measurement_required` optional field 추가 = additive minor = MINOR bump (MAJOR 미해당 — no mandatory field, no removal, no rename).
- **2-minor jump justification (ADR-008 §결정 2 audit trail)**: "2.1" → "2.3" skip (MANIFEST pre-existing drift "2.1" vs file "2.2" 동시 정렬). 4 근거: (1) SSOT = 파일 자체가 "2.3" — MANIFEST 이 실제 상태 반영; (2) audit trail = skip 명시적 기록으로 오히려 명확; (3) atomic = single commit 에 drift = 0 도달; (4) rollback simplicity = 단일 version string 으로 rollback 가능.
- **verify-before-trust evidence**: canonical SHA `a6aa5502404ab5a9e7f81b865af62889466e829a` `gh pr view 42 --repo mclayer/plugin-codeforge-design` mergeCommit.oid = MERGED (2026-05-14T13:17:49Z) verified. design-output-v2.md 본문 verbatim fetch (gh api raw content) + spec_invariant_measurement_required field 확인.
- **marketplace sync**: plugin.json 5.62.0 → 5.63.0 MINOR (ADR-037). marketplace.json 동반 sync 의무 (ADR-063 §결정 5 atomic invariant — 별도 sibling PR, wrapper PR merge 선행 의무).

## [5.62.0] - 2026-05-14 — CFP-665 sibling (Issue #668) Phase 1 — wrapper `sibling sync` pmo-output-v1 v1.2 + ADR-045 Amendment 5 §D-9

### Added

- **`docs/inter-plugin-contracts/pmo-output-v1.md` v1.1 → v1.2 verbatim mirror** (canonical codeforge-pmo PR #19 SHA `5fdaf895c70e140c1ac9001114c01504f3b0a2a0`): `cross_story_pattern_adr_trigger` optional field 추가 (Cross-Story pattern 누적 ≥ 2 검출 시 ADR escalation trigger schema, additive). 5 sub-field (`pattern_count_threshold` / `detected_anchor_id` / `fallback_root_cause_class` / `occurrences[]` / `escalation_action`). ADR-010 `sibling sync` 정합.
- **`docs/adr/ADR-045-story-retro-mandatory-trigger.md` Amendment 5 §D-9 신설**: Cross-Story pattern threshold N=2 도달 시 ADR escalation 의무 (Mandatory framing). PMOAgent self-decide 영역 제거. hybrid 검출 전략 (primary anchor_id strict / secondary root_cause_class fallback). `amendment_log[]` amendment_id 5 row append (frontmatter sync).

### Changed

- **`docs/inter-plugin-contracts/MANIFEST.yaml` pmo_output entry**: `contract_version: "1.1"` → `"1.2"` 갱신. ADR-010 `sibling sync` parity 정합.
- **`.claude-plugin/plugin.json` 5.61.0 → 5.62.0 MINOR bump**: ADR-037 — inter-plugin contract version bump + ADR Amendment (governance behavior change carrier).

### Notes

- **doc-only fast-path (ADR-054) 정합**: Phase 1 PR 단독. src/tests 무변경. Phase 2 PR 부재.
- **ADR-010 §결정 3 `sibling sync` ordering 정합**: canonical codeforge-pmo PR #19 MERGED (2026-05-14T12:34:03Z) → wrapper `sibling sync` PR 후속 (Story-1 패턴 reuse).
- **verify-before-trust evidence**: canonical SHA `5fdaf895c70e140c1ac9001114c01504f3b0a2a0` `gh pr view 19 --repo mclayer/plugin-codeforge-pmo` mergeCommit.oid verified. pmo-output-v1.md 본문 verbatim fetch + diff 0 mirror.
- **marketplace sync**: plugin.json 5.61.0 → 5.62.0 MINOR (ADR-037). marketplace.json 동반 sync 의무 (ADR-063 §결정 5 atomic invariant — 별도 sibling PR, 선행 merge 의무).

## [5.61.0] - 2026-05-14 — CFP-672 ADR-064 Amendment 4 — wording-dictionary 카테고리 (a) 4 → 5 어휘 (`별` standalone)

### Added

- **ADR-064 Amendment 4 §결정 1-6 신설**: wording-dictionary 카테고리 (a) 4 어휘 → 5 어휘 확장 (Amendment 2 cap 4 → 5 `ratchet`). 5번째 어휘 = standalone `별` — native Korean reader 의미 confusion ("star" 天文 / 별자리 vs 한자어 `別` "separate" / "another" — codeforge family doc 안 의도된 의미). 두 의미 가 동일 character form 으로 collision — cold reader 가독성 영역 mitigation. CFP-620 Epic 진행 세션 (Issue #620) live evidence. self-application top-down `ratchet` 두 번째 사례 (첫 사례 = Amendment 2 forbid-list 8 → 12 어휘, 2026-05-13 — 본 = 카테고리 (a) 4 → 5 어휘, 2026-05-14). 6 sub-decisions (배경 / §결정 1 어휘 추가 + 권장 대체 7 form / §결정 2 Hangul-boundary regex 처리 / §결정 3 self-application + `ratchet` 정합 / §결정 4 review-verdict-v4 schema 영향 0 / §결정 5 marketplace atomic invariant ADR-063 / §결정 6 evidence track + sweep CFP 분리).
- **`scripts/check-wording-dictionary.sh` FORBID_DICTIONARY array 4 → 5 entry**: `별` (standalone) 추가. 한국어 단일 character 어휘 dispatch branch 신설 — PCRE Hangul-boundary lookahead/lookbehind regex `(?<![가-힣])별(?![가-힣])` 적용 (LC_ALL=en_US.UTF-8 강제, Windows Git Bash / WSL / Linux 환경 공통). 한자어 compound (`별도` / `별개` / `특별` / `구별` / `차별`) false-positive 차단 + standalone (`별 도리` / `별도 carrier` / `별도 PR`) 만 detect. ad-hoc self-test 5 case PASS (compound 차단 + standalone detect 정합).
- **`docs/wording-dictionary.md` 카테고리 (a) row append**: 5번째 어휘 `별` (standalone) entry 추가 + frontmatter `amendments[]` Amendment 1 row append (CFP-672, 2026-05-14) + 시점 1 cap 4 어휘 → 시점 2 cap 5 어휘 갱신. EXEMPT_FILES (본 file + ADR-064) framework 그대로 재사용 — self-detection 회피.

### Changed

- **`CLAUDE.md` 결정 원칙 단락 (§결정 내용 Trace 1)**: "Forbid-list dictionary 12 어휘" → "Forbid-list dictionary 13 어휘" (Amendment 2 — 8 → 12, CFP-610 / Amendment 4 — 12 → 13, CFP-672). lint reference Amendment 4 CFP-672 추가. wording dictionary 카테고리 (a) 4 → 5 어휘 mirror. 결정 menu 자체에서 제거 의무 wording 유지.
- **`.claude-plugin/plugin.json` 5.60.0 → 5.61.0 MINOR bump**: ADR-037 — lint script FORBID_DICTIONARY array entry append (governance behavior change, runtime forbid 어휘 lint detection 확장).

### Notes

- **doc-only fast-path (ADR-054) 정합**: Phase 1 PR 단독 + marketplace `sibling sync` PR (ADR-063 §결정 5 atomic invariant). src/tests 무변경. Phase 2 PR 부재.
- **lint baseline**: 본 PR merge 시점 기존 32 file 안 `별` standalone 사용 검출 (warning tier, continue-on-error: true — PR merge 미차단). sweep batch 일괄 정리 = 새 CFP carrier 분리 (ADR-064 §결정 5 CFP scope unitary 정합 시연 — 본 Amendment 4 자체가 그 패턴).
- **EXEMPT_FILES 자기 시연**: 본 PR 내 ADR-064 + wording-dictionary.md 안 의미 정의 표기 영역에서 `별` 어휘 의도된 등장 — EXEMPT_FILES 가 차단 → self-detection 회피.
- **carrier framework 재사용**: Amendment 2 carrier (CFP-610 Story 2) 의 `scripts/check-wording-dictionary.sh` + `templates/github-workflows/wording-dictionary.yml` workflow + `hotfix-bypass:wording-dictionary` label + ADR-060 warning-tier registry entry 그대로 재사용 — entry 1 추가만, framework 신설 0건 / 새 workflow 0건 / 새 label 0건. mechanical enforcement 비용 0.
- **marketplace sync**: plugin.json 5.60.0 → 5.61.0 MINOR (ADR-037 — Amendment 4 governance behavior change / lint script FORBID_DICTIONARY array entry runtime 활성화). marketplace.json 동반 sync 의무 (ADR-063 §결정 1 atomic invariant — sibling PR).

## [5.60.0] - 2026-05-14 — CFP-660 Wave 2 of Epic CFP-431 (audit:from-mctrader-debut) — Consumer workflow version drift detection + CFP-662 Phase 1 RETRO-MCT-104 carrier

### Added (CFP-660)

- **ADR-032 Amendment 2 §결정 6 신설**: Consumer workflow version drift = 5번째 strict-eligible drift (ADR-032 §결정 2 strict-eligible 4 → 5 종 확장). consumer `.github/workflows/<name>.yml` 가 wrapper `templates/github-workflows/<name>.yml` 와 SHA-256 / 핵심 line (concurrency / on / permissions) 불일치 시 drift 감지. lane orchestration semantics divergence (race condition / counter collision / silent skip) vector 차단 forcing function. 6 sub-decisions (6.A 5번째 drift 정의 + 6.B Tier 1 SHA + Tier 2 core marker 알고리즘 + 6.C strict mode integration + 6.D bypass channel + 6.E consumer recovery procedure + 6.F out-of-scope). frontmatter `amendments[]` append + `mechanical_enforcement_actions[]` (workflow-version-drift action_name, ADR-040 Amendment 3 §결정 7.A 정합).
- **`overlay/hooks/check_bootstrap.py` check 10 NEW**: `check_workflow_version_drift()` function + `STRICT_ELIGIBLE_WORKFLOWS` set (7 file — phase-gate-mergeable / phase-label-invariant / story-init / story-section-1-immutable / subissue-from-impl-manifest / fix-ledger-sync / story-section-schema) + `WORKFLOW_CORE_MARKERS` regex tuple + `_normalized_core_markers()` helper + `_sha256_of_file()` helper + `_classify_strict_eligible()` 의 (e) 분기 + `main()` 의 `drift_warnings` wire. 9 check → 10 check.
- **`overlay/hooks/tests/test_check_bootstrap.py` TDD test 8건 신설**: clean baseline / strict-eligible drift detection / whitespace-only superficial diff suppress / plugin_root missing / wrapper templates missing / consumer workflows dir missing / non-strict-eligible warning-only / strict mode main exit 1.
- **`docs/evidence-checks-registry.yaml` 45번째 entry**: `workflow-version-drift` (warning tier, status `active` — check_bootstrap.py runtime ready). owner_adr: ADR-032 Amendment 2 §결정 6 / carrier_adr: ADR-060 evidence-enforceable framework.
- **신규 label** (label-registry-v2 v2.13 → v2.14 MINOR — schema 무변경, §3 yaml hotfix-bypass:* 20번째 family member append):
  - `hotfix-bypass:workflow-version-drift` (color `fef2c0`, audit-trailed) — check 10 conditional skip + audit comment 자동 발의 channel.
- **`docs/consumer-guide.md` §2i-3 갱신**: Strict-eligible drift 4 → 5종 표 확장 + (e) drift 복구 절차 sweep 안내 + per-Issue bypass label.
- **`docs/project-config-schema.md` `bootstrap.strict_mode` 주석 갱신**: 5번째 strict-eligible drift (e) consumer workflow version drift 명시 + STRICT_ELIGIBLE_WORKFLOWS 7 file enumeration.

### Added (CFP-662)

- **`docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` Amendment 10 §결정 24 신설**: 10번째 warning-tier entry `bootstrap-labels-precondition` — consumer repo PR open 시 codeforge 필수 label set (`phase:*` / `gate:*` / `type:*` / `hotfix-bypass:*` / `severity:*` / `audit:*` / `component:*`) 부재 자동 감지 + `scripts/bootstrap-labels.sh` idempotent 호출. PR-time precondition check pattern 의 첫 baseline (RETRO-MCT-104 carrier, mctrader-data MCT-104 Phase 2 PR #14 2026-05-09 replay sentinel). amendment_log + related_stories: CFP-662 row append + sibling_dependencies append `[..., CFP-662]` (Amendment 2 §결정 6 (c) chain 정합 — 11 carrier 누적).
- **`docs/inter-plugin-contracts/label-registry-v2.md` v2.14 → v2.15 PATCH**: `hotfix-bypass:bootstrap-labels` 21번째 hotfix-bypass:* family member 신설 + §3 yaml first-class entry append + §변경 이력 v2.15 prose entry. canonical-only (kind:registry — `sibling sync` scope 외, ADR-010 §결정 2). ADR-008 §결정 3 schema 무변경 row append = PATCH bump.
- **`docs/evidence-checks-registry.yaml` 46번째 entry `bootstrap-labels-precondition` append**: warning tier, deferred-followup status (Phase 2 carrier 신설 후 Active 전환). recurrence count=1 / threshold=3 / promotion_trigger=advisory / last_occurrence=2026-05-09 [empirical-source: mctrader-data PR #14 RETRO-MCT-104]. ADR-068 Amendment 1 I-5 dimensional empirical grounding 정합.
- **`docs/consumer-guide.md` §2h.2 신설**: `bootstrap-labels.yml` 자동 install 절차 (CFP-475 SessionStart hook `regen-agents.sh` no-clobber copy + §2c `*.yml` glob 자동 포함) + Workflow 동작 spec 표 + Edge Cases 4종 + Bypass channel (`hotfix-bypass:bootstrap-labels`) + 책임 경계 명시. Edge Case #1 CRITICAL (consumer copy 미수행) 해소 carrier.

### Changed (CFP-662)

- **`CLAUDE.md` §GitHub Workflow fixture count 25 → 26**: bootstrap-labels.yml entry append (8번째 evidence-enforceable warning, RETRO-MCT-104 carrier). 기존 7개 warning entry description 압축 (line cap 332 — `hotfix-bypass:claude-md-line-cap` label 동반 의무, audit-trailed exception channel CFP-506 ADR-012 Amendment 1 정합).
- **`.claude-plugin/plugin.json` `version: 5.59.0` → `5.60.0`**: MINOR bump (workflow 신설 = consumer-impact, ADR-037 정합) + description CFP-662 carrier entry append.

### Phase 2 PR scope (CFP-662 deferred)

- `templates/github-workflows/bootstrap-labels.yml` 신설 (26번째 fixture) — `on.pull_request.types: [opened]` only + `concurrency.group: bootstrap-labels-${{ github.event.pull_request.number }}` + `continue-on-error: true` + `bash ${{ github.workspace }}/scripts/bootstrap-labels.sh` 단일 호출 + `${{ secrets.CODEFORGE_CROSS_REPO_PAT }}` primary token + `${{ secrets.GITHUB_TOKEN }}` fallback + top-level `permissions: { issues: write, pull-requests: write }` (least privilege, ADR-060 Amendment 8 정합).
- `.github/workflows/bootstrap-labels.yml` byte-identical mirror (ADR-005 self-application).
- Story §8 Test Contract write + Story §8.5 Performance Baseline N/A declare (§8.5_active = false, 4 conditions all N).
- mctrader-data PR replay sentinel verify (AC-4).

### Notes

- **TDD discipline (CFP-660)**: 35/35 pytest PASS (CFP-103 27 기존 + CFP-660 8 신설).
- **Out-of-scope (CFP-660)** (별도 CFP carrier 후보): `scripts/sync-consumer-workflows.sh` sweep helper / `templates/github-workflows/workflow-drift-detection.yml` cron-based reactive workflow / per-marker custom drift threshold.
- **marketplace sync**: plugin.json 5.59.0 → 5.60.0 MINOR (ADR-037 — workflow-version-drift entry runtime 활성화 / CFP-662 bootstrap-labels-precondition entry + consumer-guide 신설). marketplace.json 동반 sync 의무 (ADR-063 §결정 1 atomic invariant — 별도 sibling PR, 선행 merge 완료).
- **ADR-027 Amendment 1 (ADR-032) `ratchet`**: strict-eligible 4 → 5 = additive only / supersede 아님. opt-in default-off 보존.
- **ADR-054 doc-only fast-path 부적격 (CFP-662)**: Phase 2 PR 가 `templates/github-workflows/bootstrap-labels.yml` + `.github/workflows/bootstrap-labels.yml` workflow 신설 (runtime behavior change) 동반 → Phase 1 = SSOT only + Phase 2 = workflow self-app 분리 (ADR-024 Phase 1/2 split 표준).
- **bootstrap-labels.sh 무변경 (CFP-662)**: workflow body 가 외부 script 호출 (ADR-061 §결정 1 외부 script convention reuse — multi-line shell embed 회피, CFP-583 BODY heredoc anti-pattern 차단). `hotfix-bypass:bootstrap-labels` row 는 CFP-598 dynamic read 분기 (`parse-hotfix-bypass-labels.py`) 가 자동 흡수.
## [5.59.0] - 2026-05-14 — CFP-661 Wave 3 of Epic CFP-431 (audit:from-mctrader-debut) — Enterprise prerequisite docs + graceful degradation (doc-only fast-path ADR-054)

### Added

- **`README.md` §2a "Enterprise environment prerequisite" 신설**: GitHub Enterprise `default_workflow_permissions: write` + `Allow GitHub Actions to create and approve pull requests` 활성 의무 (권한 보유 환경) — repo Settings UI step + CLI 등가 명령 (`gh api --method PUT repos/<owner>/<repo>/actions/permissions/workflow`). 차단 환경 = graceful degradation 자동 활성 안내.
- **`docs/consumer-guide.md` §1i "Enterprise environment setup" 신설**: enterprise admin 권한 보유 환경 prerequisite 활성 runbook (4 단계: UI step + CLI 명령 + 확인 명령 + 결정 매트릭스) + graceful degradation 자동 활성 안내 (CFP-658 Wave 1 fallback path 대체 진입점) + Enterprise admin 결정 매트릭스 4 행 (권한/cap 정책 조합) + sunset criteria (90% 신규 consumer install prerequisite default 활성 metric).
- **`CLAUDE.md` §"세션 개시 의무" 1-line `normative` pointer**: Enterprise prerequisite SSOT cross-ref (`docs/consumer-guide.md §1i`) + graceful degradation step pair (continue-on-error + Issue comment fallback) 자동 활성 안내. line cap 330 — `hotfix-bypass:claude-md-line-cap` label 동반 의무 (audit-trailed exception channel, CFP-506 ADR-012 Amendment 1 정합).

### Changed

- **`templates/github-workflows/story-init.yml` `Create Phase 1 PR` step**: `id: pr_create` 부여 + `continue-on-error: true` 추가 — enterprise `default_workflow_permissions: read` 차단 시 graceful degradation. Story init silent skip 회피.
- **`templates/github-workflows/story-init.yml` 신설 `Post manual PR fallback comment` step**: `pr_create.outcome == 'failure'` 조건 발화 — Issue comment 로 CFP-658 Wave 1 fallback path 안내 자동 게시 (4-step manual fallback runbook + `fallback:manual` label 부착 안내 + enterprise admin prerequisite gh api 등가 명령 + cross-ref §1h/§1i/ADR-027). Branch `feat/${KEY}-${SLUG}` push 완료 후 manual PR open 만 필요 — Story init 진행 무중단.
- **`.github/workflows/story-init.yml`** — `templates/github-workflows/story-init.yml` byte-identical mirror (ADR-005 self-application).

### `Sibling sync` (separate PR, 선행 merge 의무)

- `mclayer/marketplace` `.claude-plugin/marketplace.json` plugins[name=codeforge].version 5.58.0 → 5.59.0 + description CFP-661 entry append (ADR-063 §결정 5 + §결정 9 atomic invariant — plugin.json MINOR bump 동반 marketplace sync required).

### Notes

- **ADR-054 doc-only fast-path scope justification**: 7 file 중 6 file = docs (README / consumer-guide / CLAUDE.md / CHANGELOG / plugin.json / marketplace sibling), 1 file = workflow yml `continue-on-error: true` 추가 + new step (declarative, runtime logic change 없음 — silent skip 회피 graceful degradation). `src/` + `tests/` 변경 0건. Phase 1 PR 1개 scope.
- Wave 1 (CFP-658, 7 PR merged) 의 fallback path `normative` SSOT 와 Wave 3 의 enterprise prerequisite docs + graceful degradation 이 disjoint scope — Wave 1 = "차단 환경 대응 path" / Wave 3 = "권한 환경 prerequisite + 차단 환경 graceful degradation auto-trigger" (paired complement).
- Wave 2 (CFP-660) 병렬 진행 — baseline drift 인지 (origin/main 5.58.0).
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

### `Sibling sync` (별도 PR — Orchestrator monopoly)

- `mclayer/marketplace` plugins[name=codeforge].version 5.57.0 → 5.58.0 (ADR-063 §결정 5 atomic invariant — MINOR bump 동반 marketplace sync required).

## [5.57.0] - 2026-05-14 — CFP-658 Wave 1 of Epic CFP-431 (audit:from-mctrader-debut) — Action 차단 환경 agent direct write fallback path 표준화

### Added

- **ADR-027 Amendment 2 §결정 6 신설**: Action 차단 시 agent direct write fallback path (`normative` SSOT 단일 위치). 9 §결정 (6.A trigger (A)+(C) hybrid + 6.B agent + 6.C governance `ratchet` mitigation 3종 + 6.D PAT scope 표 + 6.E shell injection 차단 + 6.F 2-PAT namespace 분리 + 6.G burst control + 6.H existence_check verbatim port + 6.I PR description checklist mirror). frontmatter `amendments[]` append + `mechanical_enforcement_actions[]` 신설 (section-1-verbatim-postmerge action_name, ADR-040 Amendment 3 §결정 7.A 정합).
- **ADR-032 + ADR-036 cross-ref**: Amendment 2 와 strict-eligible 4종 disjoint + KEY atomic invariant manual write 영역 보존.
- **신규 label** (label-registry-v2 v2.11 → v2.13 MINOR — 신규 `fallback` category enum, post-CFP-627 v2.12 atomic rebase):
  - `fallback:manual` (color `c5def5`, audit-trailed) — per-Issue ad-hoc override marker. 우선순위 (C) > (A) > env default.
  - `fallback:rate-limited` (color `c5def5`, audit-trailed) — manual-story-init-fallback.sh exponential backoff max 3 retry 초과 시 자동 부착.
- **`scripts/bootstrap-labels.sh` 갱신**: fallback:* 2 entry hardcoded append (35 base label, 직전 33 base + 2). canonical-only (kind:registry — `sibling sync` scope 외, ADR-010 §결정 2).
- **`docs/evidence-checks-registry.yaml` 45번째 entry**: `section-1-verbatim-postmerge` (warning tier, deferred-followup status — Phase 2 carrier 신설 후 Active 전환). owner_adr: ADR-027 Amendment 2 §결정 6.C / carrier_adr: ADR-060.
- **`docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md` 신설**: recovery runbook SSOT — enterprise org-cap evidence + Researcher 위험 2종 + Trigger (A)/(C) detection + 7-step procedure + governance `ratchet` mitigation 3종 + shell injection 차단 + 2-PAT namespace + burst control + Edge case 4종 + sunset criteria.
- **`docs/consumer-guide.md` §1h "Action 차단 환경 fallback" 신설**: consumer runbook — bootstrap.fallback_mode 설정 + manual-story-init-fallback.sh 호출 + 4 required check 통과 의무 + PR description checklist + 2-PAT 모델.
- **`docs/orchestrator-playbook.md` §3.15 "Action-blocked fallback decision tree" 신설**: Orchestrator detection 절차 (lane spawn 직전 의무) + Trigger (C) > (A) 우선순위 + Codex Touchpoint #2 mandatory + env=0 / env=1 동작 동일.
- **`docs/project-config-schema.md` `bootstrap.fallback_mode` enum 등재**: `auto` (default) / `action_blocked`. 우선순위 CLI > env > yaml (ADR-032 정합 일관성).
- **`CLAUDE.md` §"오케스트레이션 규칙" 1-line `normative` pointer**: Action-blocked fallback path SSOT cross-ref (line cap 330 — `hotfix-bypass:claude-md-line-cap` label 동반 의무, audit-trailed exception channel).
- **3 deputy 산출물 통합**: SecurityArch 4 조건 (post-merge lint + PAT scope + shell injection + audit-trailed channel) + OpRiskArch 4 조건 (PR description checklist + 2-PAT namespace + fallback:rate-limited label + burst control) + DataMigrationArch 1 조건 (existence_check verbatim port) — 모두 addressed.

### Internal-docs (ADR-013 dogfood-out)

- `<internal-docs>/wrapper/specs/2026-05-14-cfp-658-action-blocked-fallback.md` (Phase 0 burst evidence)
- `<internal-docs>/wrapper/stories/CFP-658.md` (Story file §1-§7)
- `<internal-docs>/wrapper/change-plans/cfp-658-action-blocked-fallback.md` (Change Plan §1-§13)

### `Sibling sync` (separate PR, 선행 merge 의무)

- `mclayer/marketplace` `.claude-plugin/marketplace.json` plugins[name=codeforge].version 5.56.0 → 5.57.0 + description CFP-658 entry append (ADR-063 §결정 5 + §결정 9 atomic invariant — plugin.json MINOR bump 동반 marketplace sync required).

### Deferred (Phase 2 PR scope)

- `templates/scripts/manual-story-init-fallback.sh` (bash, POSIX) + `manual-story-init-fallback.ps1` (Windows parity)
- `templates/github-workflows/section-1-verbatim-postmerge.yml` + `.github/workflows/section-1-verbatim-postmerge.yml` (byte-identical mirror, ADR-005)
- `overlay/hooks/validate_config.py` enum validator (`bootstrap.fallback_mode`)
- `overlay/hooks/tests/test_validate_config.py` TDD red phase
- `.claude/_overlay/project.yaml.example` 갱신
- sibling plugin agent file 갱신 (plugin-codeforge-requirements RequirementsPLAgent.md + plugin-codeforge-design ArchitectPLAgent.md)

## [5.56.1] - 2026-05-14 — CFP-633 Story-2 `sibling sync` (Epic CFP-620 — mctrader 3-cycle post-mortem)

### Added

- ADR-014 Amendment 3 — ProductionEvidenceDeputy boundary axis 명시 (`policy SSOT vs evidence SSOT` 목적축 분리)
  - §결정 6.1: Boundary axis 1줄 (Story-1 OpRiskArch deputy 산출 verbatim reuse)
  - §결정 6.2: `findings[].owner_axis_kind` enum 신설 (별도 CFP-Z carrier reservation, review-verdict-v4 v4.5 → v4.6 MINOR bump 영역)
  - §결정 6.3: Amendment 2 §결정 3 ↔ ADR-72 §결정 2 5번째 cell 3-way 충돌 처리 단락 (chief author 자율 신설, AC-5 carrier 의무 충족)
- Story-1 anchor (ADR-72) `sibling sync` 완료 (Epic CFP-620 sequential first sibling)

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

### `Sibling sync` (separate PR)

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

### `Sibling sync` (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.54.0 → 5.55.0 mirrored (ADR-063 atomic invariant).

## [5.54.0] - 2026-05-14 — CFP-631 Phase 2 (marketplace-description-verbatim lint script + workflow + bats 13 TC)

CFP-631 Phase 2 실제 구현: `scripts/check-marketplace-description-verbatim.sh` (byte-identical lint, exit 0/1/2 ADR-060 §결정 15 3-tier) + `templates/github-workflows/marketplace-description-verbatim.yml` + `.github/workflows/marketplace-description-verbatim.yml` (ADR-005 self-app byte-identical mirror) + `tests/scripts/test_check_marketplace_description_verbatim.bats` (13 TC all PASS). Phase 1 선언 (§결정 11/12 + evidence-checks-registry entry) 의 mechanical enforce 체인 완성. 7th rebase race sentinel sample (cumulative 7 — CFP-619 + CFP-628 + CFP-631 FIX-1 + CFP-631 Phase 1 + CFP-631 Phase 2 + 2 more).

ADR-037 MINOR bump: script/workflow 신규 추가 (behavior change). plugin.json 5.53.0 → 5.54.0.

### Added

- `scripts/check-marketplace-description-verbatim.sh` — NEW bash lint script. byte-identical compare (trailing newline normalize). Exit 0=PASS / 1=DRIFT / 2=SETUP-error (ADR-060 §결정 15 3-tier). Test override: `CFP631_MARKETPLACE_PATH` / `CFP631_PLUGIN_JSON` env. DRIFT report: first-diff position + 200-char excerpt.
- `templates/github-workflows/marketplace-description-verbatim.yml` — NEW workflow. Trigger: pull_request to main (opened/synchronize/reopened/labeled). blocking-on-pr tier. hotfix-bypass:marketplace-description-verbatim conditional skip + audit comment. permissions: `{}` top-level + job override `contents:read / pull-requests:write` (ADR-060 Amendment 8 정합).
- `.github/workflows/marketplace-description-verbatim.yml` — ADR-005 self-app byte-identical mirror. SHA256: `681dff2222cf5f0327bb29a1b89d1e0f12a9b3341e68169783267002e6895c11` (FIX iter 1 후 갱신).
- `tests/scripts/test_check_marketplace_description_verbatim.bats` — 13 test cases (7 unit + 3 integration + 2 meta SETUP error). All 13 PASS (bats 1.13.0).

### `Sibling sync` (separate PR)

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

- E-1 hook automation (mechanical enforcement layer) = 별도 follow-up CFP
- GitHub API eventual consistency = 별도 CFP
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

- `docs/orchestrator-playbook.md` §3.0.14 Question quality 3-check 본문에 Continuous "진행해" 패턴 detect subsection 추가 — pattern 8종 + 3+ 누적 trigger + 5+ strong brevity signal + mechanical layer SSOT cross-ref + 미래 hook 도입 별도 CFP follow-up 명시.

### `Sibling sync` (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.51.0 → 5.52.0 mirrored (ADR-063 atomic invariant). CFP-637 marketplace sync (#111 merged) 후 base.

### Coordination with sibling Stories

- CFP-637 (Story A+B+C combined, PR #640 MERGED) — 본 PR base.
- CFP-639 (Story E cross-plugin, PR #642) — 본 Story merge 와 독립 진행 가능 (cross-plugin upstream PR 영역).

## [5.51.0] - 2026-05-14 — CFP-637 (ADR-064 Amendment 3 — Over-questioning anti-pattern 차단)

Epic [CFP-635](https://github.com/mclayer/plugin-codeforge/issues/635) Story A+B+C combined carrier. doc-only fast-path (ADR-054). post-CFP-631 atomic realignment (5.50.0 → 5.51.0, rebase race 5th sample).

사용자 directive 2026-05-14 KST (verbatim, Epic body §사용자 directive): "이렇게 물을 필요 없는 질문 방금 왜한거야? 이렇게 된 원인을 심층적으로 파악하고 이 외에도 의미없는질문으로 user stop 걸지 않아야한다. 반드시" — 4-layer root cause + 7 anti-pattern (P1-P7) enumeration carrier.

ADR-037 MINOR bump: CLAUDE.md 의미 변경 (§결정 9 강화 + §결정 10 신설 mirror) + ADR-064 본문 amendment + skill body amend.

### Added

- ADR-064 Amendment 3 frontmatter + amendment_log entry (carrier_story: CFP-637, direction: strengthen, sunset_justification: null — `ratchet` 강화 방향)
- ADR-064 §결정 9 amendment — Stop-time pre-flight Question quality 3-check (가치 판단 영역 / derived default 자명 / 1-option 자기 검증) + 7 anti-pattern P1-P7 enumeration body
- ADR-064 §결정 10 신설 — Skill body ↔ CLAUDE.md `normative` priority precedence (CLAUDE.md > ADR > skill body > external skill body). CFP-358 / CFP-374 (Subagent-Driven 자동 선택) generalized `normative` SSOT.
- ADR-064 Amendment 3 section (Amendment 결정 1-7) — Story A 결정 (§결정 9 amend) / Story B 결정 (skill body amend) / Story C 결정 (§결정 10 신설) / Memory `normative` 승격 mapping (3 entry) / Self-application + `ratchet` / review-verdict-v4 영향 0건 / sister Story CFP-638·CFP-639 cross-ref.
- `skills/codeforge-brainstorm/SKILL.md` Phase 1 priority precedence note — dialog format / AskUserQuestion / "사용자 confirm" 지시가 derived default 자명 영역에서 무효 명시.

### Changed

- `CLAUDE.md` `## 결정 원칙` 단락 Trace 5 (Stop-time 평문 정리) → Trace 5/6 통합 + Question quality 3-check + Skill body ↔ `normative` precedence 본문 추가
- `docs/orchestrator-playbook.md` §3.0.14 — §결정 9 Question quality 3-check + §결정 10 Skill body precedence 본문 추가
- `docs/orchestrator-playbook.md` §3.0.5 — Generalized `normative` SSOT cross-ref (§결정 10) 추가
- `docs/orchestrator-playbook.md` §3.0.14 duplicate numbering 수정 → §3.0.15 Parallel Dispatch Protocol

### `Sibling sync` (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.50.0 → 5.51.0 mirrored (ADR-063 atomic invariant — marketplace 선행 merge → wrapper PR merge, post-CFP-631 realignment)

### Memory `normative` 승격 (post-merge cleanup)

본 PR merge 후 다음 3 memory entry 삭제 (single-source-of-truth, CLAUDE.md "behavioral directive → memory 금지" `normative` 정합):

- `feedback_question_quality` → §결정 9 Question quality 3-check
- `feedback_explain_before_ask` → §결정 3 룰 3 + 룰 6 (Amendment 2 carry, 본 amendment 검증 통과)
- `feedback_subagent_driven_auto_select` → §결정 10 generalized precedent

### CLAUDE.md line cap

CLAUDE.md = 327 lines (ADR-012 Amendment 1 ≤320 cap 7 초과). `hotfix-bypass:claude-md-line-cap` label 부착 (CFP-628 / CFP-506 precedent 정합). compression scope = Trace 5 + Trace 6 통합 (Amendment 3 본문 압축 — ADR-064 본문 / playbook 가 detailed SSOT, CLAUDE.md 는 summary mirror).

## [5.50.0] - 2026-05-14 — CFP-631 (ADR-063 Amendment 2 — marketplace description verbatim PR-time proactive lint mandate)

CFP-619 retro §5.2 carry-over — 6 sample 누적 description drift evidence (CFP-387 / CFP-393 / CFP-423 / CFP-597 / CFP-612 / CFP-619). ADR-063 §결정 1 `mirrored field` invariant 안 `description` field 만 PR-time enforce 부재 (version = `version-bump-atomic-check.yml` blocking-on-pr cover, name/author = `check-marketplace-parity.sh` warning sufficient) → mechanical proactive lint mandate (Amendment 2 §결정 11). Amendment 1 (design-time self-check, CFP-597) 와 layered 2-layer proactive forcing function.

ADR-037 MINOR bump: governance behavior change (Amendment 2 mandate 신설 — blocking-on-pr tier 직접 시작, Phase 2 PR 부터 active enforce). rebase race 4th sample (CFP-619+CFP-628+CFP-631 FIX-1+CFP-631 PR sequence) — base 5.49.0 (CFP-628 Story 2 merge 후 재산정).

### Added

- ADR-063 Amendment 2 본문 — `docs/adr/ADR-063-marketplace-atomic-invariant.md` frontmatter `amendments[1]` row append + §결정 11 (description proactive lint mandate) + §결정 12 (self-application `ratchet` + 본 carrier 첫 사례 시연 의무).
- `docs/evidence-checks-registry.yaml` — 42번째 entry `marketplace-description-verbatim` append (CFP-628 `retro-alert-pickup-rate` 42번째 entry 위 재편입 → CFP-631 이 43번째로 재배치). owner_adr: ADR-063, carrier_adr: ADR-060, current_tier: blocking-on-pr (ADR-060 §결정 5 default warning explicit exception + §결정 19 Amendment 6 CFP-509 auto_blocking manual gate path — 6 sample 누적 evidence base + 사용자 directive Story §1), bypass_label: `hotfix-bypass:marketplace-description-verbatim` (per-entry namespace, ADR-024 Amendment 3 §결정 6.A 정합, 17번째 hotfix-bypass family member). recurrence: count=6 / threshold=6 / promotion_trigger=auto_blocking / last_occurrence=2026-05-14.
- `docs/inter-plugin-contracts/label-registry-v2.md` — v2.9 → v2.10 PATCH (schema 무변경 — §3 yaml `hotfix-bypass:marketplace-description-verbatim` 17번째 family member append). bootstrap-labels.sh dynamic read 분기 자동 sync (CFP-598).

### Scope split (Phase 1 vs Phase 2)

- **Phase 1 (본 PR)**: ADR-063 Amendment 2 + plugin.json + CHANGELOG + evidence-checks-registry + label-registry-v2 (doc/registry/version bump only).
- **Phase 2 (별도 PR)**: `scripts/check-marketplace-description-verbatim.sh` (bash lint script) + `templates/github-workflows/marketplace-description-verbatim.yml` canonical SSOT + `.github/workflows/marketplace-description-verbatim.yml` byte-identical mirror (ADR-005). Phase 2 PR merge 후 future PR 부터 본 lint 활성 (chicken-and-egg 회피).

### `Sibling sync` (separate PR)

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

### `Sibling sync` (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.49.0 (marketplace 이미 5.49.0, description에 CFP-628 content append sync — ADR-063 atomic invariant, separate PR #106)

## [5.47.0] - 2026-05-14 — CFP-619 (retro-mandatory.yml workflow deploy — ADR-045 mandate restoration)

CFP-612 retro carrier #1 — `retro-mandatory.yml` workflow 가 `.github/workflows/` 에 미배포 상태 → ADR-045 mandate (PMOAgent retro auto-trigger 5min grace + retry state machine + close-blocking) 의 mechanical enforcement 미작동. CFP-612 Phase 2 PR #618 merge (2026-05-14) 시점 첫 manual fallback observed → 본 carrier 가 sentinel #1 회복.

ADR-037 MINOR bump: script behavior change (신규 workflow runtime 활성화 — 차 Phase 2 PR merge 부터 retro-check job 발화).

### Added

- `.github/workflows/retro-mandatory.yml` (NEW, byte-identical mirror of `templates/github-workflows/retro-mandatory.yml` per ADR-005 self-application invariant — SHA256 `d01bf23f4503049a5afa4336b575e357002467a3b0b5551ccc9b26927f142fd6`). Phase 1 + Phase 2 통합 form (CFP-138 + CFP-290 carrier prior art, FIX iter 1-3 PASS). 3 trigger (pull_request closed / issues closed / schedule cron `*/5 * * * *`) + 3 jobs (retro-check / close-blocking / retry-state-machine).
- `docs/evidence-checks-registry.yaml` — 41번째 entry `retro-mandatory-deployed` append (CFP-610 wording-dictionary 40번째 entry 직후). owner_adr: ADR-045, introduced_by: CFP-619, current_tier: warning, bypass_label: `hotfix-bypass:retro-mandatory-deployed` (per-entry namespace, ADR-024 Amendment 3 §결정 6.A 정합).

### `Sibling sync` (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.46.0 → 5.47.0 mirrored (ADR-063 atomic invariant — marketplace 선행 merge → wrapper PR merge)

### Lane boundary stretch declare

본 Story = codeforge-requirements plugin 미로드 영역 (session-level constraint, Story scope 결정 아님) → ArchitectPLAgent 가 §2-§6 (Requirements lane) + §7 (Design lane) 통합 author. ADR-054-grade trivial mechanical scope + retro carrier compressed lifecycle 정합. Story §10.5 Git Ops Log gitops-cfp619-004 row 기록.

## [5.46.0] - 2026-05-14 — CFP-610 Story 2 Phase 2 FIX iter 1 (ADR-064 Amendment 2 mechanical enforcement + marketplace atomic sync)

### Added (CFP-610 Story 2 — wording-dictionary lint)

- **`scripts/check-wording-dictionary.sh`** (NEW) — ADR-064 Amendment 2 wording-dictionary lint script. 카테고리 (a) forbid 어휘 발견 시 exit 1 warning (`박제` / `못 박기` / `pin` / `freezing`). 카테고리 (b) 어휘 평문 정의 누락 시 exit 0 advisory (`normative` / `sibling sync` / `kind:contract` / `ratchet` / `mirrored field`). SSOT: docs/wording-dictionary.md. 5 scope: docs/adr/** / docs/change-plans/** / CLAUDE.md / docs/orchestrator-playbook.md / templates/**. blockquote + fenced code block exempt. docs/wording-dictionary.md 자체 EXEMPT.
- **`tests/scripts/test_check_wording_dictionary.bats`** (NEW) — TDD unit test (17 TC PASS: TC-1~4 + IT-1~3 + CI-1). bats framework. 카테고리 (a) forbid 4 TC + 카테고리 (b) advisory 2 TC + 정의 동반 5 TC + 일반 어휘 2 TC + blockquote/fenced exempt 2 TC + self-app baseline 1 TC.
- **`templates/github-workflows/wording-dictionary.yml`** + **`.github/workflows/wording-dictionary.yml`** (NEW, byte-identical) — ADR-060 warning-tier workflow. continue-on-error: true. hotfix-bypass:wording-dictionary label bypass + audit comment.
- **`docs/evidence-checks-registry.yaml`** — 39번째 entry `wording-dictionary` append. owner_adr: ADR-064, introduced_by: CFP-610, current_tier: warning.
- **`docs/inter-plugin-contracts/label-registry-v2.md`** — v2.6 sub-entry `hotfix-bypass:wording-dictionary` (13번째 hotfix-bypass:* family member). frontmatter version `2.5` 미변경 (same-MINOR additive).
- **`scripts/bootstrap-labels.sh`** — `hotfix-bypass:wording-dictionary` label entry append (label-registry-v2 sync).
- **CLAUDE.md** — Evidence-enforceable 단락 5→6 warning entry / GitHub Workflow 단락 fixture 22→23종.

### `Sibling sync` (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.45.0 → 5.46.0 mirrored (ADR-063 atomic invariant)

## [5.45.0] - 2026-05-14 — CFP-612 Wave 5 (ADR-071 Orchestrator-user dialog convergence)

### Closed (CFP-612 Phase 2 — full-lane closure, src/tests = 0, all code-lane N/A)

full-lane Story convention 준수 Phase 2 closure. src/tests 변경 0 — 모든 effective 변경은 Phase 1 (#617) 에 포함. code-lane (Develop/CodeReview/SecurityTest) 모두 N/A 선언. ADR-045 mandate PMOAgent retro auto-trigger 발화 시점 (Phase 2 PR merge 후 5분 grace). Change Plan §10.1 declare: Phase 2 0 commit.

### Added (CFP-612 Phase 1 — Design lane, ADR-071 + playbook §3.14 + skill + Layer 4 file)

CFP-525 Epic ancestor follow-up — Orchestrator-user dialog convergence (Wave 5). Phase 1 PR scope = §1-§7 (ADR + Change Plan + playbook §3.14 + skill SKILL.md + Layer 4 incidents file + CLAUDE.md cross-ref + plugin.json MINOR bump + CHANGELOG + ADR-064 related_adrs append + section-ownership.yaml 2 row append + ADR-RESERVATION row 71 active). 신규 ADR 동반 → ADR-054 §결정 1 full-lane Story 분류 (doc-only fast-path 미적용). src/tests 변경 0.

- `docs/adr/ADR-071-orchestrator-user-dialog-convergence.md` (NEW) — governance permanent (`is_transitional: false`). 본질 anchor (mechanical rule 추종 회피 + 진짜 수렴 dialog) + §결정 1-11 (frame mode 4 step + frame mode 세부 룰 3 종 + 4 layer 검증 + sub-mechanism 2 종 + 사실/가치 결정 트리 + Layer 4 영속 file schema + "추상" keyword semantics + 3 memory entry `normative` 승격 mapping + CFP-582 conceptual cross-ref schema fit 부적합 declare + scope out + ADR-039 inline whitelist 1번 entry cognitive 강화 declare). `mechanical_enforcement_actions: []` (Wave 5 = cognitive + persistence layer only, Layer 1 mechanical lint 별도 follow-up CFP). carrier_story = CFP-612.
- `docs/orchestrator-communication-incidents.md` (NEW) — Layer 4 누적 detection file (cross-Story append-only, Orchestrator monopoly). 8-column schema (iter / timestamp / story_key / pattern_dimension / pattern_summary / trigger / different_dimension_after_halt / escalation_outcome). M=5 lifetime counter, manual reset only. wrapper repo 4번째 cross-Story append-only file 패턴 (FIX Ledger / Git Ops Log / ADR-RESERVATION 정합).
- `skills/user-dialog-mode/SKILL.md` (NEW) — `codeforge:user-dialog-mode` skill. 매 user-facing turn 직전 호출. frame mode 4 step + 4 layer + sub-mechanism 2 종 lookup-table.
- `docs/orchestrator-playbook.md` (UPDATE) — §3.14 Orchestrator-user dialog convergence 신설 (§3.13 debate-protocol-v1 직후). frame mode + 4 layer + sub-mechanism + Layer 4 file + 결정 트리 + memory entry mapping + CFP-582 schema fit 부적합 declare 본문 SSOT. logical position = agent ↔ agent debate (§3.13) ↔ Orchestrator ↔ user dialog (§3.14) 인접 짝.
- `CLAUDE.md` (UPDATE) — Adversarial Debate Protocol 단락에 Wave 5 inline cross-ref 추가 (Wave 4 단락 안 same-paragraph append) + "Lane 진입 시 skill 호출 의무" 표 1 row 추가 (`매 user-facing turn 직전 (사용자 dialog turn)` → `codeforge:user-dialog-mode`). 320 cap compression 동반 — "Deferred tool 선제 로드 (0i)" + "SessionStart hook — worktree-gc (0a-prime)" 두 단락 1 단락으로 merge (net -2 lines, 신규 row 1 line 흡수 후 319/320).
- `docs/adr/ADR-064-decision-principle-mandate.md` (UPDATE) — `related_adrs` field 에 ADR-071 append (본문 변경 0, backward compat). ADR-064 §결정 7 top-down `ratchet` 정합 — 강화 방향 only.
- `docs/adr/ADR-RESERVATION.md` (UPDATE) — row 71 `reserved → active` 전환. ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent.
- `docs/parallel-work/section-ownership.yaml` (UPDATE) — 2 row append: (1) `docs/orchestrator-playbook.md §3.14` (owner_adr ADR-071, append-only) (2) `docs/orchestrator-communication-incidents.md Incidents` (owner_adr ADR-071, append-only, arbitrator = orchestrator-self-write monopoly).
- `.claude-plugin/plugin.json` (UPDATE) — version 5.44.0 → 5.45.0 MINOR + description CFP-612 Wave 5 entry (3rd rebase — CFP-598 P2 version collision resolved).

### Codex Proactive Check #2 + #6 (CFP-612 carry-over to DesignReview lane)

- **Touchpoint #2** (ArchitectAgent §3 / Change Plan §3 완료 직후) — DIVERGENCE_DETECTED 1 P1 finding (anchor `CFP-612-W5-S2-E9-E11-TURN-SHAPE` semantic-2 category): Story §5.3 Edge Case E9 streaming token / E10 tool-call-only / E11 AskUserQuestion popup turn-shape default 가 ADR-071 + playbook §3.14 + skill 모두 미명시 (E12 trivial answer 만 cover). **Inline FIX applied (ADR-052 Amendment 4 §결정 10 mandatory)** — playbook §3.14 "Turn-shape derived defaults" 표 3 row append (E9/E10/E11) + ADR-071 §결정 3 4 layer 표 turn-shape edge cross-ref + skill SKILL.md "Turn-shape edge 분기" 4 row table append. 모든 RequirementsPL §5.3 `[fact-check-pending]` marker resolved. verify-before-trust (ADR-070) Orchestrator 측 direct file Read 로 finding ground truth 확인 완료.
- **Touchpoint #6** (ArchitectAgent ADR 초안 완료 직후) — ADR-071 draft 완료 직후 single-shot Codex check (FIX-1 적용 후 ADR-071 자체 = 330 lines, 신규 inline FIX 영역 reflect). 추가 divergence 미발견 expected.

### 3 memory entry `normative` 승격 (Phase 2 PR merge 시점 effective)

- `feedback_explain_before_ask` → playbook §3.14 (frame mode 본문 SSOT) + ADR-071 §결정 1 step 4 + §결정 4 sub-mechanism 1
- `feedback_question_quality` → playbook §3.14 (frame mode 본문 SSOT) + ADR-071 §결정 2 (b) + §결정 5 결정 트리
- `feedback_subagent_driven_auto_select` → **변경 없음** (playbook §3.0.5 기존 정책 유지, codeforge wrapper side SSOT 변경 0)

### `Sibling sync` (separate PR)

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

### `Sibling sync` (separate PR)

- mclayer/marketplace: plugins[codeforge].version 5.43.0 → 5.44.0 mirrored + description CFP-598 entry append (ADR-063 atomic invariant, sibling PR #98 MERGED 선행 2026-05-14T00:02:42Z)

## [5.43.0] - 2026-05-14 — CFP-609 (ADR-064 Amendment 1 + parallel-dispatch-protocol-v1)

### Added (CFP-609 — parallel-dispatch-protocol-v1 신설 + ADR-064 Amendment 1 mechanical enforcement Phase 1)

- **`docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md`** 신설 (kind:registry, wrapper canonical, `sibling sync` 면제) — ADR-064 §결정 4 Trace 4 "Orchestrator multi-task spawn default = parallel" `normative` declaration 의 execution-time enforcement contract. 4 의무 항목 (plan DAG verbatim 기재 / PL 자율 병렬 권한 명시 / sequential mandate enum 명시 / file-level conflict resolution 패턴) + 6 sequential mandate enum (close-set) + PL 자율 병렬 결정 tree 4-분기 + env=0/1 동등성 + consumer overlay defaults.
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

CFP-530 retro carrier #2 — `bootstrap-labels.sh` hotfix-bypass:* family dynamic sync + §3 yaml backfill (pre-existing leak). Phase 1 PR scope = Change Plan + Story §1-§9 only (no src/scripts/registry edit). Phase 2 PR (별도 carrier) 가 6 file 변경 + marketplace 5.42.0 → 5.43.0 sibling PR.

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

### `Sibling sync` (separate PR)

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

### `Sibling sync` (separate PRs)

- mclayer/marketplace#85: plugins[codeforge].version 5.40.0 → 5.41.0 mirrored (ADR-063 atomic invariant)
- mclayer/plugin-codeforge-design#40: ArchitectPLAgent Phase 0.5 Blanket Adversarial Debate Trigger (cross-module Story 자동 발동 + Touchpoint #2 carry-over + convergence_quality_invariant gate)
- mclayer/plugin-codeforge-review#32: review-pl-base §11.5 debate-protocol-v1 v1.2 cross-ref + 3 marker pattern verification 책무
- mclayer/marketplace#87: codeforge-design 0.11.0 + codeforge-review 1.6.0 `sibling sync` mirror

## [5.40.0] - 2026-05-13 — CFP-507 DeveloperPLAgent Phase 2 PR body composition convention codification

### Added (CFP-507 — Lane evidence heading 1회 inject convention, ADR-031 §결정 3 정합)

CFP-490 (#490, merged) §7.5 origin investigation 의 carrier — `## Lane evidence` first heading auto-include 의 actual origin 정정. 가설 (wrapper PR template 부재 → DeveloperPL spawn template) 은 **verified false**, 실제 origin = codeforge-develop DeveloperPLAgent body composition convention 부재 + wrapper Orchestrator manual append 정책 부재 결합.

- `docs/orchestrator-playbook.md` (UPDATE) — §3.0.13 신설 "PR description `## Lane evidence` manual append 정책 (CFP-507)". 3-step 절차 (heading 존재 check → row append only / heading 재추가 금지 → 부재 시 heading + 7-row template inject) + Story §14 Lane Evidence row append 동시 turn 처리 의무 (ADR-031 정합) + 위반 시 `lane-evidence-check.yml` 5a duplicate guard 발화 (CFP-490 §결정 1 정합). codeforge-develop sibling plugin `agents/DeveloperPLAgent.md` "Phase 2 PR body composition convention" section 와 짝 (sibling 0.5.2 → 0.6.0 MINOR bump).
- `.claude-plugin/plugin.json` — version 5.39.0 → 5.40.0 MINOR + description CFP-507 entry append.

### Doc-only fast-path (ADR-054 §결정 1) — src/tests 0건 + 신규 ADR 0건 + ADR Amendment 0건

본 Story = doc-only fast-path 분류. 설계 lane 진입 후 ArchitectPLAgent chief author self-execute (6 permanent deputy + 2 CONDITIONAL deputy spawn 0 — mandate 정합 0). Self-check verdict packet: `mechanical_self_check_passed: true` (ADR-065 vacuous truth) + `boundary_completeness_self_check_passed: true` (ADR-068 wording SSOT cross-ref) + `dimensional_empirical_self_check_passed: true` (ADR-068 Amendment 1 count dim empirical-source annotated). 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 lane SKIPPED.

### `Sibling sync` (separate PRs)

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

### `Sibling sync` (separate PRs)

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

- **ADR-068 Amendment 1** — I-5 dimensional empirical grounding invariant 신설 (4 → 5 invariants, `ratchet` 강화). 10 dimension enum (latency/scale/cardinality/throughput/cost/accuracy/lifecycle/volume/rate/count) 의 quantitative parameter 마다 `[empirical-source: <ref>]` 또는 `[empirical-source: TBD]` annotation 의무. empirical-absent default lock-in 차단 (#319 RETRO-MCT-104 carrier).
- **review-verdict-v4 v4.3 → v4.4 MINOR bump** — `dimensional_empirical_self_check_passed: bool` optional field + `findings[].type: "dimensional-empirical-gap"` literal. ArchitectAgent verdict packet 셋 별도 boolean field (mechanical + boundary_completeness + dimensional_empirical) 동시 PASS 의무.
- **mechanical_enforcement_actions[] 3번째 entry** — `dimensional-empirical-grounding` (status: deferred-followup, target_section: §결정 1).

### Closed

- **#319 (RETRO-MCT-104)** — keep-linked + close as absorbed. distinct failure-class but systemic super-class (empirical-grounded design discipline). ADR-052 Amendment 3 (touchpoint #4 fact-check) cover specific case + CFP-528 dimensional sensitivity discipline 일반화.

### `Sibling sync` (separate PRs)

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

### Added (CFP-506 — CLAUDE.md skill 추출 + cap `ratchet` ≤320 + mechanical lint forcing function)

4 신규 skill 추출 (lane-self-write-boundary / story-cutoff-classification / inter-plugin-contract-registry / story-epic-flow-preflight) + CLAUDE.md 434줄 → 309줄 압축 (cap 320 대비 11줄 headroom) + `scripts/check-claude-md-line-cap.sh` lint script + `templates/github-workflows/claude-md-line-cap.yml` warning-tier workflow (ADR-060 Amendment 5 4번째 warning-tier entry). ADR-012 Amendment 1 cap ≤380 → ≤320 `ratchet` 강화. ADR-051 Amendment 1 Draft → Accepted + anchor vs reference 판정자 §결정 신설.

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

CFP-451 (#451) + CFP-490 (#490) 0-FIX chain 7-8번째 retro PMOAgent FU-4 (low severity) carrier. ADR-052 Amendment 1 (CFP-411) 의 touchpoint #4 divergence detection 3 semantic criteria 에 **4번째 영역 = fact-check** 추가. 사실 영역 (registry-execution drift / pre-existing leak / file path verification / cross-repo state verification) 의 implicit 발화를 explicit `normative` anchor 로 승격. PL self-evaluation 의무 = synthesis fact claim 영역 marker 5종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]` / `[verification-out-of-scope: <사유>]`) — fact-check 영역 divergence detection false negative 차단 forcing function. debate-protocol-v1 dispatch 흐름 변경 없음 (divergence_type enum 확장은 별도 carrier CFP). MINOR bump (CLAUDE.md SSOT mirror 영향 + ADR amendment).

- `docs/adr/ADR-052-codex-proactive-check-touchpoints.md` (UPDATE) — Amendment 3 본문 append (A1~A8 결정 + 거절된 대안 H~K). amendments[] frontmatter row 추가.
- `CLAUDE.md` (UPDATE L188) — Codex Proactive Check blockquote 갱신: divergence 영역 = 3 semantic + 1 factual = 4 영역 명시 + marker 5종 의무 inline.
- `.claude-plugin/plugin.json` — version 5.24.0 → 5.25.0 MINOR (rebased onto main HEAD post-CFP-453 merge). description CFP-510 entry append.
- `Sibling sync`: `mclayer/plugin-codeforge-requirements` 0.5.1 → 0.6.0 MINOR (RequirementsPLAgent.md "Divergence detection 4 영역" + "PL self-evaluation 의무" 단락 + codex-proactive-check.md "Fact-check 영역" 단락).
- Marketplace sync (`mclayer/marketplace` `marketplace.json` `plugins[name=codeforge]` + `plugins[name=codeforge-requirements]` `mirrored field` — name/version/description/author atomic, ADR-063 §결정 5).

#### Why

axis-A (governance — fact-check 영역 explicit `normative` anchor): 양 retro evidence 2회 누적으로 implicit 발화 영역 `normative` 승격 timing 도달. axis-B (PL synthesis quality — marker 5종 forcing function): "가설" vs "verified" 영역 구분 의무 부재 → Codex fact 발견 시 PL LLM 판정 false negative 위험 차단. axis-C (lane-agnostic protocol 확장 보존): debate-protocol-v1 dispatch 흐름 변경 없음 — divergence_type 영역만 확장 (separate carrier CFP 가 enum MINOR bump 처리).

### Added (CFP-462 Epic close + CFP-438)

- **CFP-438** ADR-065 — ArchitectAgent Phase 1 mechanical sync self-check 7-item checklist (non-marketplace 영역). change-plan template §13 self-check 결과 섹션. ArchitectPLAgent verdict packet `mechanical_self_check_passed: bool` schema forward.
- **CFP-462** Epic close — 5 child Story 통합 처리 완료 (CFP-448 / 451 / 450 / 453 / 438).

### Changed (CFP-462)

- `docs/inter-plugin-contracts/review-verdict-v4.md` — v4.1 → v4.2 MINOR (`mechanical_self_check_passed` optional bool field 추가, ADR-008 §결정 2 정합). wrapper `sibling sync`.

### `Sibling sync` (Epic CFP-462 close)

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

### `Sibling sync` (ADR-016 + ADR-063 atomic invariant)

- `marketplace.json` 4 `mirrored field` sync — **본 PR scope 외**, Epic CFP-462 close 시 single marketplace sync PR 일괄 처리 전략. `hotfix-bypass:marketplace-atomic` label 부착 (24h drift window 발생 → audit comment 자동 발의 인지, ADR-063 §결정 5 정합).
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

ADR-031 §결정 3 (lint cross-validate) 의 enforcement layer logic refinement. CFP-465 (#482, cc5d7c3) 가 도입한 5a duplicate guard (line 113-128) 의 잔여 gap 4종 해소 — (a) summary 메시지 단순 count → tie-break case A/B/C 식별도 + valid heading 명시 + 삭제 target 권고, (b) tie-break decision 부재 → Case A (1 valid) / Case B (0 valid) / Case C (2+ valid) 분기, (c) recurrence count documentation 부재 → registry description 본문 명시, (d) origin 식별도 부재 → first-match capture boundary + DeveloperPL spawn template 가설 documentation. Option A strict 채택 (CFP-465 invariant 보존, lenient fallback 폐기 — ADR-031 §결정 2 "1회 heading 의무" 정합). `.mjs` extraction 채택 (testability rationale — bash heredoc `node -e` simulate 한계 초과, 6 test_function 29 assertion path coverage 측정). MINOR bump (workflow yml 변경 + .github script 신설).

- `templates/github-workflows/lane-evidence-check.yml` (UPDATE line 112-143) — 5a guard 강화: `analyzeDuplicateHeadings()` import + tie-break case A/B/C summary + ADR-031 §결정 2 정책 인용 + DeveloperPL spawn template 가설 documentation comment.
- `.github/workflows/lane-evidence-check.yml` (UPDATE) — ADR-005 byte-identical self-app mirror.
- `.github/scripts/check-lane-evidence-block.mjs` (NEW, 116 line) — `analyzeDuplicateHeadings(body)` 함수 export. Case A/B/C tie-break + valid_heading_idx + invalid_idx_list 식별. `actions/github-script@v7.1.0` 안 dynamic import (ESM/CJS 호환).
- `tests/workflows/test_lane-evidence-check-yml.sh` (NEW, 252 line, 6 test_function 29 assertion) — Case A/B/C path coverage + strict mode + fast-pass invariants + BYPASS honor + cross-cutting (byte-identical + .mjs presence + dynamic import) 검증. base64 body encoding 으로 cross-platform 안전 (Git Bash MSYS2 path translation 회피).
- `docs/evidence-checks-registry.yaml` (UPDATE) — `lane-evidence-trail` entry description 본문에 actual recurrence (CFP-500 FIX-5 1차 + CFP-451 본 세션 2차) + logic refinement (CFP-490 Phase 2) 명시. schema 무영향 — machine-usable promotion signal 아님 (ADR-060 4-tier 무관).
- `.claude-plugin/plugin.json` — version 5.22.1 → 5.23.0 MINOR (workflow yml + .github script 신설, ADR-037 정합).

### `Sibling sync` (ADR-016 + ADR-063 atomic invariant)

- `marketplace.json` 4 `mirrored field` sync 의무 — name/version/description/author. **본 PR scope 외, Orchestrator escalation 영역** (DeveloperPL 책임 외). marketplace sync PR open 후 atomic check PASS 의무.

### Why

CFP-500 FIX-5 (#456, merge 직전 1차 actual collision) + CFP-451 본 세션 transient (#486 step 3 2차 actual) 의 2회 actual recurrence — 단일 defense (5a heading-count guard) 가 작동하나 valid heading 식별도 부재 + tie-break decision 부재 + fix-guide weak (수동 삭제 안내만, 어느 heading 인지 명시 안 함). 본 Story = 잔여 gap 해소. 신규 ADR 0건 — ADR-031 §결정 3 의 enforcement layer 내부 logic refinement.

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

### `Sibling sync` (ADR-016 + ADR-063 atomic invariant — Phase 2 PR pair)

- `plugin-codeforge-develop` 0.5.0 → 0.5.1 PATCH — DeveloperPLAgent model field Opus → Sonnet (사용자 framing 직접 적용 — ADR-042 §결정 1 (b) verbatim 회귀, mandate text 0건 — 이미 implementation work 정의 명확).
- `plugin-codeforge-design` 0.6.0 → 0.7.0 MINOR — CodebaseMapperAgent / RefactorAgent model field Opus → Sonnet **+ mandate text 재정의** (description frontmatter + 본문 mandate boundary section).
- `plugin-codeforge-requirements` 영향 0 (ChangeImpactAgent Opus 유지).
- `marketplace.json` 3 entry sync — **본 PR scope 외**, Epic CFP-462 close 시 일괄 처리 (24h drift window 발생 → audit comment 자동 발의 인지, ADR-063 §결정 5 hotfix-bypass:marketplace-atomic 채널 외 normal merge).

### Why

CFP-393 회고에서 발견된 3-way drift (CLAUDE.md L127 8종 / ADR-057 §결정 3 5종 / agent file 실측 4종) 의 reverse direction 해소. CLAUDE.md L127 8종이 정합인 상태로 회복 — 3 agent (CodebaseMapper / Refactor / DeveloperPL) Opus → Sonnet 복귀. 사용자 framing 진화 — 초기 결정 (ChangeImpact + Mapper + Refactor) 에서 새 framing ("코드 작성 agent = Sonnet, 고도 추론 불필요" + "ChangeImpact 는 Opus 가 괜찮음") 적용 후 swap. ADR-042 §결정 1 (b) "Implementation work" verbatim 정합. mandate text 재정의로 ADR-042 §결정 2 invariant ("Sonnet 으로 fully cover 가능 = role 재정의 시그널") 정합 강제.

### Compatibility

- **Wire**: codeforge-{requirements,design} >= 0.5.0 (`sibling sync` 의무).
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
- **plugin.json description retain** (CFP-451/448/481 entries 잔존) — ADR-063 atomic invariant 면제 (`mirrored field` 변경 0). version 5.22.0 (CFP-451/448/481 concurrent merge window 정합).
- **marketplace.json `sibling sync` 면제** — `mirrored field` 변경 0 (description retain), 별도 sync PR 불요.

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
- `.claude-plugin/plugin.json` description append CFP-449 entry (`mirrored field` — marketplace `sibling sync` 의무).

### Why

ADR-064 §결정 8 declaration only — mechanical enforcement 는 CFP-449 별도 carrier 분리. ADR-060 evidence-enforceable framework 가 2nd entry 도입을 통해 multi-entry 운영 검증 + 점진 승격 patterns 의 cross-validation 신호 확보. 작성자 자발 준수 + DesignReview 1차 안전망 의존의 한계 (forbid 어휘 reflex 사용 시 detection 부재) 해소.

### Compatibility

- consumer overlay 영향 = 정책 축소 불허 (lint script + workflow + registry entry 신설). `.claude/_overlay/project.yaml` extension 만 허용.
- lint = warning tier (ADR-060 §결정 5), PR merge 미차단. blocking 승격은 framework gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 통과 후 별도 CFP carrier.
- bypass channel = `hotfix-bypass:decision-principle-vocab` label + PR description `### Bypass reason` (ADR-024 Amendment 3 §결정 6.A). audit comment 자동 발의 — 정책 회피 등록 차단 (ADR-064 §결정 5 정합).
- 6 lane plugin 영향 = 0 (wrapper level lint, lane plugin self-write boundary 무변경).
- ADR-060 Amendment 3 (Phase 1 PR #470 merged 2026-05-12) — `hotfix-bypass` 채널 의미 sharpening 1줄 + amendment_log row 3 추가. 강화 방향 amendment (`ratchet` 위반 0건).
- Marketplace `sibling sync` 의무 = `version` 5.20.0 → 5.21.0 + `description` `mirrored field`. ADR-063 §결정 2 atomic invariant — marketplace sync PR 선행 merge → plugin PR merge.

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

사용자 directive 4 회 누적 (2026-05-11 ~ 2026-05-12, KST) 의 `normative` SSOT 승격. memory ephemeral 영역의 cross-session enforcement 부재 해소.

- `docs/adr/ADR-064-decision-principle-mandate.md` (NEW) — 8 결정 본문
  1. 4 어휘 운영적 정의 (Trace 1) — best-effort / broad coverage / full-scope / active amendment
  2. forbid-list 8 어휘 dictionary — CFP-449 mechanical lint SSOT (warning tier)
  3. 결정 제시 5 룰 (Trace 2) — derived default / 옵션 dump 금지 / 식별자 사전 요약 / 질문 brevity / AskUserQuestion 범위
  4. multi-task spawn parallel default + sequential 강제 3 사유 dictionary (Trace 4)
  5. CFP scope unitary 룰
  6. 결정 제시 시점 (proposing-time) 영역 정의
  7. Self-application top-down `ratchet`
  8. Declaration only (CFP-446 / CFP-449 mechanical enforcement 별도 carrier)
- `CLAUDE.md` "결정 원칙" 신규 단락 ("오케스트레이션 규칙" 직전, append-only)
- `docs/orchestrator-playbook.md` §4.1.1 신규 — parallel default + sequential 강제 3 사유 운영 + 결정 제안 시점 self-check 5 항목 checklist
- `docs/domain-knowledge/domain/governance-principle/decision-style.md` (NEW) — 행동 패턴 + 적용 사례 SSOT (governance-principle 카테고리 신규 진입)
- `templates/github-issue-forms/story.yml` `decision_principle_compliance` advisory 체크박스 추가 (forcing function)
- `docs/adr/ADR-RESERVATION.md` — `| 64 | CFP-445 | active | 2026-05-12 |` row append

### Why

사용자 directive 4 회 누적 (2026-05-11 발화 1 회 + 2026-05-12 발화 2 회 + Codex pre-review iterative directive 1 회) 에도 `normative` SSOT 부재 = cross-session enforcement 결손. memory ephemeral 영역 한계가 결정 품질의 forbid-list 영역 침식 위험 + 옵션 dump UX + sequential bias 3 갈래 root cause. 본 carrier 가 그 SSOT 정립.

### Compatibility

- consumer overlay 영향 = 정책 축소 불허 (CLAUDE.md `normative` 단락 신설). `.claude/_overlay/project.yaml` extension 만 허용.
- mechanical lint (CFP-449) = warning tier 진입 (ADR-060 §결정 5), advisory only. blocking 승격은 evidence-enforceable framework gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 통과 후 별도 CFP carrier.
- iterative reformulation (CFP-446) = ADR-052 Amendment 2 별도 carrier (touchpoint #1 single-shot → max 3 rounds).
- 6 lane plugin 영향 = 0 (wrapper level `normative` SSOT, lane plugin self-write boundary 무변경).
- Marketplace `sibling sync` 의무 = `name` / `description` `mirrored field` 갱신 (description 변경 — `+ CFP-445 ...` append). 본 PR merge 직후 `mclayer/marketplace` sync PR 즉시 open · merge (ADR-016 + ADR-063 atomic invariant 정합).

### Related

- [CFP-445](https://github.com/mclayer/plugin-codeforge/issues/445) — 본 carrier Story
- [CFP-446](https://github.com/mclayer/plugin-codeforge/issues/446) — Codex pre-review iterative reformulation (ADR-052 Amendment 2 별도 carrier)
- [CFP-449](https://github.com/mclayer/plugin-codeforge/issues/449) — forbid-list mechanical lint (ADR-060 warning tier 신규 entry `decision-principle-vocab` — 기존 entry `adr-sunset-criteria` 와 병렬)
- [ADR-064](docs/adr/ADR-064-decision-principle-mandate.md) — `normative` 결정 SSOT
- [ADR-058](docs/adr/ADR-058-adr-sunset-criteria-mandate.md) — sunset criteria mandate (`ratchet` 차단 forcing function)
- [ADR-060](docs/adr/ADR-060-evidence-enforceable-promotion-framework.md) — evidence-enforceable framework
- [ADR-063](docs/adr/ADR-063-marketplace-atomic-invariant.md) — 3-file atomic invariant

## [5.19.0] - 2026-05-12

### Changed (CFP-455 — Evidence registry schema v1.0 → v1.1 (4-tier enforcement 정식 amendment))

CFP-391 (Issue #396, closed without delivery 2026-05-11) / CFP-412 (Issue #412, post-merge-followup workflow false-positive close 2026-05-11) 의 재재예약 carrier. ADR-060 Amendment 2 deliver — 4-tier enforcement 정식 분류 정식화.

- `docs/adr/ADR-060-evidence-enforceable-promotion-framework.md` — Amendment 2 append (frontmatter `amendment_log[]` row 2 + 본문 `## Amendment 2` § 신설 8 결정 — §결정 3 required 전환 / §결정 6 (c) `sibling_dependencies` append CFP-455 / §결정 14 메타 anomaly vs schema validation lint 분리 / §결정 15 exit-code 3-tier semantics / §결정 16 warning-tier bypass_label optional / §결정 17 retroactive reclassification immediate fail / §결정 18 marketplace sync 의무 명시 / Mermaid diagram 동기화)
- `docs/evidence-checks-registry.yaml` — header `schema_version: "1.0"` → `"1.1"` + `last_updated: 2026-05-12` + `entries[name=adr-sunset-criteria].promotion_criteria.sibling_dependencies` append `CFP-455`
- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — frontmatter `version: "1.0"` → `"1.1"` + §3 표 `current_tier` row required marker + §3 표 `bypass_label` row tier 별도 의무 분리 + §4 본문 4-tier enum 강조 + §7 v1.1 row 완료된 변경 historical 분리
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

본 PR merge 직후 즉시 marketplace sync PR open·merge (codeforge plugin family 의 wrapper plugin version `mirrored field` — `mclayer/marketplace` `marketplace.json` `plugins[name=codeforge]` version `5.18.0` → `5.19.0`).

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

CFP-387 / CFP-393 / CFP-423 retro 의 3-Wave marketplace drift 누적 → ADR carrier 격상 timing 도달. `mirrored field` bump 시 3 file atomic coordination 의무 명시화.

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

3-Wave drift evidence (CFP-387 chicken-and-egg + CFP-393 catch-up + CFP-423 합쳐 처리) — `mirrored field` bump 시 atomic coordination invariant 부재. 기존 `check-marketplace-parity.sh` / `check-marketplace-sync.sh` 는 사후 감지만 가능, 작성 시점 강제 mechanism 없음.

### Compatibility

- `is_transitional: false` (permanent policy carrier — ADR-058 self-application 정합)
- ADR-016 `sibling sync` 와 별도 정책 (amendment 아님)
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
- codeforge-requirements 0.5.0 `sibling sync` (mclayer/plugin-codeforge-requirements#19):
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
    - §결정 5: Amendment 시 `sunset_justification` 의무 (`ratchet` 차단, CL-2 옵션 B 채택, count cap 거부)
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

ADR-057 (Orchestrator Opus 필수화 + Sonnet→Opus fallback) 가 측정 기준 없는 영구 안전망으로 굳어지는 위험이 brainstorming (Opus×Codex 3라운드, 2026-05-11) 에서 식별도 → 합의 원칙 5 "안전망 측정가능 종료" forcing function. technical debt `ratchet` effect (Cunningham 1992 / Fowler 2003) + 입법 sunset clause 패턴 + feature flag sunset 운영 가이드 선행 연구 기반.

### Compatibility

- ADR-037 §3.1 (h) 신규 ADR + (g) additive CLAUDE.md guidance → MINOR. 5.10.0 → 5.11.0.
- backward compatible — 기존 ADR 39종 frontmatter 미선언 = default `is_transitional: true` 안전망 추정 (declaration only, mechanical enforcement = CFP-B 잠정 carrier)
- **`Sibling sync`**: codeforge-design 0.6.0 → 0.7.0 (`templates/adr.md` canonical SSOT 갱신) — Phase 2 PR pair 동시 merge 의무
- **Marketplace sync**: wrapper + codeforge-design 양쪽 `mirrored field` 변경 (`version` + `description`) → marketplace sync PR 의무 (Phase 2 PR merge 직후, ADR-016)
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
| (l) Marketplace `mirrored field` | description 갱신 | MINOR |

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

#### `Sibling sync` (Phase 2 merge 후 — D step ★ Agent tool 3 parallel dispatch)

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

- `docs/adr/ADR-030-live-entry-gate-policy.md` (NEW) — 5 결정 (gate:live-entry-pass label 정의 / Live touching Story 식별도 mechanism / phase-gate-mergeable.yml validation / 3-condition AND consumer-side SSOT / fast-pass 영향 차단). mctrader debut audit P0 (Codex gpt-5.5 high 2026-05-04) 해소.
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
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md` §5.1 신규 단락 — Deprecated → Archived 전환 트리거 3 조건 정의 (consumer 부재 + 후속 MAJOR 1+ release + canonical/`sibling sync` 또는 wrapper 단독)
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

ζ arc 첫 lane plugin self-write 검증 단계 (parent spec §5.5). codeforge-review v1.0.0 BREAKING + codeforge wrapper `sibling sync`.

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
- `scripts/check-doc-frontmatter.sh` — `kind:contract` dispatch (kind:registry 만 본 lint 적용, `kind:contract` 는 check-inter-plugin-contracts.sh 가 별도)
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
- `scripts/check-doc-section-schema.sh` — strict 전환 + 회고 §1 regex 완화 (`^## §1 결과` → `^## §1\s+\S` — 회고 종류별도 §1 명칭 자유) + legacy change-plan allowlist (CFP-1 ~ CFP-18 중 docs/change-plans/ 존재분 16건 면제)
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
- **ArchitectPL 검수 메타-규칙 압축** — 4 항목 enumerate -> 2 항목 메타-규칙 (§섹션별도 deputy author input 통합 + §섹션 누락 차단)

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
- Codex 플러그인 단일 의존성: 미설치 시 3 리뷰 lane 모두 진입 불가 (이전: 각 lane별도 개별도 차단)

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
- **섹션별도 atomic 갱신 규정 누락**: Domain/Analyst/Researcher 결과를 배치로 기록하면 resume 시 부분 완료 감지 불가. DocsAgent가 §2·§5·§6 각각 **atomic 갱신** 의무 명시 (배치 금지)
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
