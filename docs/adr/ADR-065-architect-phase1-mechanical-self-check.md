---
adr_number: 65
title: ArchitectAgent Phase 1 산출물 mechanical sync self-check 의무 (non-marketplace 영역)
status: Accepted
category: Team & Process
date: 2026-05-13
is_transitional: false
related_files:
  - CLAUDE.md
  - docs/inter-plugin-contracts/review-verdict-v4.md
related_stories:
  - CFP-393
  - CFP-411
  - CFP-438
  - CFP-685   # Amendment 1 carrier — family scope 확장 (wrapper-only → 7-repo)
  - CFP-911   # Amendment 2 carrier — 8th item frontmatter YAML parse self-validate (CFP-851 incident gap 보완)
  - CFP-930   # Amendment 3 carrier — 9th item Story self-declared correction commit application verify
  - CFP-1242  # Amendment 4 carrier — 10th item 선제-lint mandate + INV-1 parity kind:registry scope 확장 (ADR-045 §D-9 escalate_user)
related_adrs:
  - ADR-005   # CFP-685 정정 audit trail — ADR-005 (lane N/A 표준화) ≠ self-app convention SSOT
  - ADR-010   # CFP-685 cross-ref — kind:workflow sibling sync 면제 vs family scope self-app 분리
  - ADR-013   # CFP-685 cross-ref — dogfood-out family 7-repo SSOT
  - ADR-016   # family scope 정의 source (marketplace registration 7-repo)
  - ADR-031
  - ADR-039
  - ADR-041
  - ADR-049
  - ADR-050
  - ADR-060   # CFP-685 carrier — sibling-parity entry warning tier (Amendment 11)
  - ADR-063
  - ADR-066   # CFP-685 cross-ref — Phase 2 sibling sync PR open 시 CODEFORGE_CROSS_REPO_PAT 의무 영역
  - ADR-073   # CFP-685 cross-ref — Orchestrator verify-before-assert (cross-repo state 단정 의무)
  - ADR-008   # CFP-1242 cross-ref — inter-plugin contract/registry versioning (INV-1 parity field semantic)
  - ADR-045   # CFP-1242 cross-ref — §D-9 cross-Story pattern_count 3 escalate_user (Amendment 4 동기)
  - ADR-064   # CFP-1242 cross-ref — §self-application top-down ratchet (Amendment 4 강화 방향만)
  - ADR-082   # CFP-1242 cross-ref — write-time self-write verification (선제-lint mandate 인접 layer)
amendments:
  - amendment: 1
    date: 2026-05-15
    cfp: CFP-685
    summary: "§결정 1 row 3 family scope 확장 — wrapper-only self-app convention 의 7-repo (wrapper + 6 lane plugin sibling) byte-identical mandate. §결정 6 신설 (family scope self-app invariant — Anchor Issue #626 / CFP-609 retro Finding D 영역). §결정 1 본문 변경 0 (row 3 wording 유지 — wrapper Phase 1 commit-time self-check). 본 Amendment 가 row 3 의 sibling-family scope 확장 + drift detection mechanism (scripts/check-sibling-workflow-parity.sh + templates/github-workflows/sibling-workflow-parity.yml warning tier) 도입. mechanical_enforcement_actions[] append — `sibling-workflow-parity` entry status: deferred-followup → warning (Phase 1 PR merge 후). ratchet 강화 방향만 (wrapper-only scope 축소 금지 — ADR-064 top-down ratchet 정합)."
    is_transitional: false
    sunset_justification: "N/A — permanent policy 의 ratchet 강화. ADR-058 §결정 7 governance default presumption 정합 (is_transitional: false). ADR-064 §self-application top-down ratchet 정합 (Amendment 1 = scope 확장 강화 방향 only). 약화 방향 (family scope → wrapper-only / sibling drift detection 면제 / Conservative no-rename policy revoke) 발의 차단."
  - amendment: 2
    date: 2026-05-17
    cfp: CFP-911
    summary: "§결정 1 표(7-row) 에 row 8 append — Phase 1 산출물 commit 직전 chief author 가 변경한 frontmatter 보유 .md file 의 YAML parse self-validate (검증 방법: `bash scripts/check-doc-frontmatter.sh <path>` PASS, CFP-28 strict mode cross-ref). §결정 7 신설 — Amendment 2 narrative (incident reference + family pattern 정합 + cascade obligation invariant + sunset_justification quoted-string-form 보존). §결정 1 row 1-7 본문 변경 0 (row 8 append 만), §결정 2-6 변경 0. mechanical_enforcement_actions[] append — `doc-frontmatter-yaml-parse` entry status: existing-warning-cross-ref (신규 lint script 신설 0건, 기존 CFP-28 `check-doc-frontmatter.sh` PR-time strict check 의 commit-time forcing function cross-ref only). Story §5.4 Out-of-Scope 7 항목 정합 — 신규 ADR 0건, 신규 lint script 0건, 신규 workflow yml 0건, 신규 mechanical_enforcement_actions[] action name 0건(기존 안전망 cross-ref only — `doc-frontmatter-yaml-parse` 가 `check-doc-frontmatter.sh` existing entry alias), 6 lane sibling PR 0건, review-verdict-v4 schema bump 0건, cascade lint 신설 0건(별도 CFP carrier). CFP-851 incident evidence (Phase 2 PR #885 ADR-071 amendment_log entry `is_transitional: false` colon-space plain scalar nested mapping ScannerError, FIX iter 1 commit `79a4fdda0c9b4ee249edfcdb3769ef95b8113628` equals form 정정으로 해소, 현재 file state HEAD 재현 불가 — git history SSOT) 가 chief author commit-time forcing function 부재 gap 입증. ratchet 강화 방향만 (7→8 ratchet 확장 only — 8th item 제거 / `check-doc-frontmatter.sh` cross-ref 해제 발의 차단)."
    is_transitional: false
    sunset_justification: "N/A — permanent policy 의 ratchet 강화 (Amendment 1 family pattern 정합). ADR-064 §self-application top-down ratchet 정합. 약화 방향(8th item 제거 / check-doc-frontmatter.sh cross-ref 해제) 발의 차단."
  - amendment: 3
    date: 2026-05-18
    cfp: CFP-930
    summary: "§결정 1 표(8-row) 에 row 9 append — Story 본문 self-declared correction(strike-through `~~old~~ → new` / `<del>` HTML / 'previously: X' 류 패턴) 의 chief author commit 실제 적용 verify. 검증 방법: Story §2/§6 등 declared correction enumerate → `git diff` / repo-wide grep 로 실제 적용 cross-check, 누락 검출 시 RETURN to ArchitectPLAgent (chief author 재호출, ADR-004 author ≠ judge 보존). §결정 1 row 1-8 본문 변경 0 (row 9 append 만), §결정 2-7 변경 0. mechanical_enforcement_actions[] append `story-self-declared-correction-verify` entry status: deferred-followup (mechanical lint 자동 검출 별 carrier). cross-Story pattern threshold reach (≥ 2, ADR-045 §D-9): CFP-795 first occurrence (Architect §3 mandatory P1 finding inline FIX 시 8 anchor 동시 갱신 누락, F-1 lesson) + CFP-906 second occurrence (Story §2.2 `~~ADR-072~~ → ADR-72` 18 occurrence 미적용, F-DR-906-1 P0 broken-link + F-DR-906-2 P1 wording-SSOT). chief author mechanical self-check 신뢰도 저하 + DesignReviewPL 사후 catch FIX iter 추가 evidence. ADR-082 Amendment 1 scope b (design-lane self-check + 정정 재귀) 직접 인접 — sister carrier. review-verdict-v4 schema 영향 별 carrier (cross-plugin sibling sync 필요, 본 Amendment scope 외). ratchet 강화 방향만 (8→9 ratchet 확장 only)."
    is_transitional: false
    sunset_justification: "N/A — permanent policy 의 ratchet 강화 (Amendment 1/2 family pattern 정합). ADR-064 §self-application top-down ratchet 정합. 약화 방향(9th item 제거 / verify 의무 해제) 발의 차단."
  - amendment: 4
    date: 2026-05-22
    cfp: CFP-1242
    summary: "(a) §결정 1 표(9-row) 에 row 10 append — Phase 1 산출물 commit 직전 touched ADR/doc 에 대해 `bash scripts/check-doc-section-schema.sh <path>` + `bash scripts/check-adr-sunset-criteria.sh <path>` 로컬 선제 실행 (PASS 확인) behavioral mandate (운영 phase S3+ FIX 0 효과 입증). (b) INV-1 parity lint (scripts/lib/check_inter_plugin_contracts_parity.py) scope 의 kind:registry 확장 (mechanical) — MANIFEST `registries` 섹션 (`version` field) 이 그동안 lint iteration gap 으로 무방비였음 (정정된 진단: 'MANIFEST 가 kind:registry 를 제외' 라는 정책 exclusion 이 아니라, lint 가 manifest['contracts'] 만 iterate 하던 iteration gap — sibling-sync 면제 ADR-010 §결정 2 와 MANIFEST↔frontmatter parity 가 conflate 됨). 본 Amendment 가 두 영역 (contracts: contract_version / registries: version) 모두 parity-check 하도록 확장 — S4 drift class 차단. live label_registry drift (frontmatter v2.50 ∉ MANIFEST 7 mis-ordered Active rows 2.43-2.49) 를 lint 가 실제 적발 + 동반 MANIFEST collapse fix. §결정 1 row 1-9 본문 변경 0 (row 10 append 만), §결정 2-8 변경 0. mechanical_enforcement_actions[] = 기존 `inter-plugin-contracts-parity` entry (CFP-894 / ADR-060 §결정 6) 의 scope 확장 cross-ref only — 신규 evidence-checks-registry entry 0건 (기존 parity check 가 cover). cross-Story pattern threshold reach (pattern_count 3, ADR-045 §D-9 escalate_user): S1/S2/S4 evidence (kind:registry version parity unguarded → S4 drift human review 도달). ratchet 강화 방향만 (9→10 ratchet 확장 + parity scope 확장 only — ADR-064 §self-application top-down ratchet 정합)."
    is_transitional: false
    sunset_justification: "N/A — permanent policy 의 ratchet 강화 (Amendment 1/2/3 family pattern 정합). ADR-064 §self-application top-down ratchet 정합. 약화 방향(10th item 제거 / 선제 lint mandate 해제 / INV-1 parity kind:registry 재제외) 발의 차단."
mechanical_enforcement_actions:
  - action: sibling-workflow-parity
    status: deferred-followup
    progress_note: "ADR-065 Amendment 1 (CFP-685) 신설 시점 — verdict field-only enforcement (workflow self-fire weekly cron). evidence-checks-registry entry `auto-phase-label-sibling-parity` warning tier 도입. blocking-on-pr 승격 후보 — 별도 CFP 가 첫 20 PR sample 누적 + failure_threshold 0 + sibling Story merged 도달 시 status 갱신 (deferred-followup → warning → blocking-on-pr)."
    target_section: §결정 1 row 3 (family scope 확장) / §결정 6 (신설)
  - action: doc-frontmatter-yaml-parse
    status: existing-warning-cross-ref
    progress_note: "ADR-065 Amendment 2 (CFP-911) 신설 시점 — 신규 lint script 신설 0건. 기존 CFP-28 `scripts/check-doc-frontmatter.sh` (thin wrapper, `scripts/lib/check_doc_frontmatter.py` SSOT, ADR-061 §결정 1 정합) PR-time strict check 의 commit-time forcing function cross-ref only. row 8 의 검증 방법 wording 은 thin wrapper + Python SSOT 두 file 의 strict mode contract 의존 — cascade obligation invariant (§결정 7 §7.3 본문 cascade 1줄 신설로 codify, manual review 의존, cascade 자동 검출 lint 별도 follow-up CFP carrier — Story §5.4 row 7 정합). evidence-checks-registry 신규 entry 0건 (기존 안전망 cross-ref only). status 승격 trigger 없음 — `existing-warning-cross-ref` 영구 (별도 CFP 가 신규 lint script 발의 시에만 status 갱신)."
    target_section: §결정 1 row 8 (Amendment 2 CFP-911) / §결정 7 (신설)
  - action: story-self-declared-correction-verify
    status: deferred-followup
    progress_note: "ADR-065 Amendment 3 (CFP-930) 신설 시점 — chief author 의 commit-time manual self-check (Story declared correction enumerate + `git diff` cross-check). mechanical lint 자동 검출 = 별도 follow-up CFP scope (Story body 의 strike-through 패턴 자동 enumerate + commit diff 비교). evidence-checks-registry 신규 entry 0건 (manual self-check tier). 본 status 승격 trigger = mechanical lint 신설 별 CFP merge 시점. ADR-082 Amendment 1 scope b (design-lane self-check + 정정 재귀) sister carrier — review-verdict-v4 schema 영향 (cross-plugin sibling sync 필요) 별 carrier 분리."
    target_section: §결정 1 row 9 (Amendment 3 CFP-930) / §결정 8 (신설)
  - action: inter-plugin-contracts-parity
    status: existing-warning-cross-ref
    progress_note: "ADR-065 Amendment 4 (CFP-1242) 신설 시점 — 신규 evidence-checks-registry entry 0건. 기존 `inter-plugin-contracts-parity` check (CFP-894 / ADR-060 §결정 6, `scripts/lib/check_inter_plugin_contracts_parity.py` SSOT + thin wrapper `scripts/check-inter-plugin-contracts-parity.sh`, warning tier) 의 SCOPE 확장 cross-ref only. 본 Amendment 4 (b) 가 lint 의 iteration scope 를 manifest['contracts'] 단독 → contracts + registries 양 섹션으로 확장 (contracts field=contract_version / registries field=version). 신규 lint script / 신규 workflow yml / 신규 evidence-checks-registry entry / 신규 mechanical_enforcement_actions[] action name 0건 — 기존 parity check 가 kind:registry 영역까지 cover 하도록 확장만. status 승격 trigger 없음 — `existing-warning-cross-ref` (별도 CFP 가 parity check tier 승격 발의 시에만 status 갱신). row 10 (a) 선제-lint behavioral mandate 는 mechanical action 아님 (chief author commit-time manual 선제 실행) — evidence-checks-registry entry 0건."
    target_section: §결정 1 row 10 (Amendment 4 CFP-1242) / §결정 9 (신설)
---

# ADR-065: ArchitectAgent Phase 1 산출물 mechanical sync self-check 의무 (non-marketplace 영역)

## 상태

`Accepted` (2026-05-13). ADR-063 (marketplace atomic invariant) 의 non-marketplace 영역 보완.

## 컨텍스트

codeforge-design lane 의 ArchitectAgent (chief author) 가 Phase 1 산출물을 commit 직전, 사전 정의된 checklist 부재로 인해 매 Story 반복 결함이 발생했다. 이 결함들은 모두 chief author 가 "산출물 commit 직전 self-check" 로 잡을 수 있는 mechanical sync 누락이다.

### 결함 evidence (3 Story 누적)

**CFP-393 (#398) iter 1 FIX (설계-리뷰 CI lint, 3건)**:

- `scripts/bootstrap-labels.sh` ↔ `docs/inter-plugin-contracts/label-registry-v2.md` sync 누락 (CFP-33 strict check FAIL)
- CLAUDE.md L129 `docs/kpi/rate-limit-fallback.json` Phase 1 link → Phase 2 target dangling (markdown internal links FAIL)
- `docs/doc-locations.yaml` 갱신 후 `docs/doc-location-registry.md` mirror regenerate 누락 (validate FAIL)

**CFP-393 (#398) iter 3 FIX (구현 Phase 2 PR CI, 1건 — marketplace 2건은 CFP-436 분리)**:

- `templates/github-workflows/rate-limit-fallback-kpi.yml` 신규했으나 `.github/workflows/` self-app copy 누락 (invariant-check FAIL)

**CFP-411 (#411) phase-gate path 누락**:

- phase 라벨 전환 시점 / gate label attach 미흡 → phase-gate-mergeable FAIL

### 공통 root cause

- chief author 가 6 SubAgent 산출물 통합 후 Change Plan + ADR draft 만 write, 주변 mechanical sync 파일을 별도 checklist 로 확인하지 않음
- 매 Story 에서 동일 결함 type 재발 (label-registry / doc-locations / workflow self-app / link target / MANIFEST.yaml)
- CI lint 가 사후 감지 channel 로 동작 — Phase 1 PR commit 시점 forcing function 부재

### 기존 SSOT 의 한계

- ArchitectAgent.md 본문 §3.5 self-lint (CFP-378) = 6 SubAgent 산출물 input 표면 형식 / Story §1 cross-ref / 외부 입력 무결성 — **design decision input 표면 check 만**. mechanical sync (label-registry / doc-locations / workflow self-app) 영역 미포함
- ADR-063 marketplace atomic invariant = `plugin.json` / `CHANGELOG.md` / `marketplace.json` 3-file atomic — **marketplace 영역만**. label-registry / doc-locations / workflow self-app 등 non-marketplace 영역 미포함
- review-verdict-v4 schema = `pl_recommendation` 단일 final verdict — chief author self-check pass 여부 explicit marker 부재

## 결정

### 결정 1: 7-item mechanical sync self-check 의무 (non-marketplace 영역)

ArchitectAgent chief author 는 Phase 1 산출물 commit 직전 다음 7 항목 mechanical sync 검증 의무:

| # | 항목 | 검증 방법 |
|---|---|---|
| 1 | `label-registry-v2.md` 변경 시 `scripts/bootstrap-labels.sh` sync 동반 | `bash scripts/check-labels-bootstrap-strict.sh` PASS |
| 2 | `doc-locations.yaml` 변경 시 `bash scripts/check-doc-locations.sh --regen` 실행 | regenerate 후 `doc-location-registry.md` mirror diff 0 |
| 3 | 신규 `templates/github-workflows/*.yml` 시 `.github/workflows/` self-app copy 동반 | `diff -q templates/github-workflows/X.yml .github/workflows/X.yml` exit 0 (byte-identical) (see §결정 6 for family scope, Amendment 1 CFP-685) |
| 4 | CLAUDE.md / docs/** 내 link target 이 Phase 1 분배인지 확인 | Phase 2 file 참조 시 dangling — markdown internal link lint PASS |
| 5 | `docs/inter-plugin-contracts/MANIFEST.yaml` registries 블록 갱신 필요성 확인 | 신규 registry 도입 시 row append, MANIFEST `check-inter-plugin-contracts.sh` PASS |
| 6 | `docs/parallel-work/section-ownership.yaml` 정책 필요 시 row append | 동시 편집 영향 받는 신규 section 도입 시 row append |
| 7 | `docs/doc-locations.yaml` 신규 doc type row 필요성 확인 | 신규 doc type 도입 시 row append, `check-doc-locations.sh` PASS |
| 8 | Phase 1 산출물 commit 직전 chief author 가 변경한 frontmatter 보유 `.md` file 의 YAML parse self-validate (Amendment 2 CFP-911) | `bash scripts/check-doc-frontmatter.sh <path>` PASS 확인 (CFP-28 strict mode cross-ref) |
| 9 | Story 본문 self-declared correction (`~~old~~ → new` strike-through / `<del>` HTML / "previously: X" 류 패턴) 의 chief author commit 실제 적용 verify (Amendment 3 CFP-930) | Story §2/§6 등 declared correction 패턴 enumerate → 각 패턴이 본 PR commit 안 actual diff 로 적용되었는지 `git diff` / repo-wide grep cross-check. 누락 검출 시 RETURN to ArchitectPLAgent (chief author 재호출) |
| 10 | Phase 1 산출물 commit 직전 touched ADR/doc 에 대해 `bash scripts/check-doc-section-schema.sh <path>` + `bash scripts/check-adr-sunset-criteria.sh <path>` 로컬 선제 실행 (PASS 확인) — (a) behavioral mandate, 운영 phase S3+ FIX 0 효과 입증 (Amendment 4 CFP-1242) | touched ADR / doc 각 path 에 두 lint 로컬 선제 실행 → PASS 확인 후 commit. 사후 CI 도달 전 chief author 가 self-detect (운영 phase Epic S3+ Story 가 본 선제-lint 프로세스로 FIX iter 0 달성 — pre-lint 효과 입증) |

**Row 8 cascade obligation (Amendment 2 / CFP-911)**: 본 row 8 의 검증 방법 wording 은 `scripts/check-doc-frontmatter.sh` (thin wrapper) / `scripts/lib/check_doc_frontmatter.py` (Python SSOT, ADR-061 §결정 1 정합) 의 strict mode contract 의존. 두 file 의 contract (exit code semantic / strict-mode 분기 / target path coverage) 가 변경되는 PR (예: CFP-NNN script behavior change) 는 ADR-065 §결정 1 row 8 wording 갱신 cascade 의무 — 갱신 누락 시 row 8 forcing function silently drift. cascade 검출은 manual review 의존 (별도 follow-up CFP carrier — cascade 자동 검출 lint 신설 검토, Story §5.4 row 7 정합).

각 항목 = chief author 가 본인 Phase 1 산출물 commit 직전 self-check. NA (해당 영역 변경 없음) = 명시적 PASS 로 분류.

### 결정 2: change-plan template "Phase 1 self-check 결과" 섹션 의무화

[codeforge-design `templates/change-plan.md`](https://github.com/mclayer/plugin-codeforge-design/blob/main/templates/change-plan.md) 에 `§13. Phase 1 산출물 self-check 결과 (ADR-065 / CFP-438)` 섹션 추가. chief author 가 7 항목 결과 (PASS / NA / FIX) 를 명시 의무.

### 결정 3: review-verdict-v4 v4.1 → v4.2 MINOR bump — `mechanical_self_check_passed: bool` 필드 추가

review-verdict-v4 schema 에 다음 optional 필드 추가:

```yaml
mechanical_self_check_passed: <bool>   # NEW (ADR-065 / CFP-438, v4.2 MINOR)
                                        # ArchitectAgent Phase 1 7-item mechanical sync self-check 결과
                                        # true = 모두 PASS 또는 NA, false = FIX 의무
                                        # 적용 lane: design lane 만 (code/security lane = optional, omit 가능)
```

ADR-008 §결정 2 "새 선택 필드 추가" = MINOR bump 정합. Runtime impact 없음 (기존 v4.1 consumer 가 본 필드 무시 가능).

### 결정 4: false 시 FIX 의무 — ArchitectPLAgent 가 ArchitectAgent re-spawn 명령

`mechanical_self_check_passed: false` 수신 시:

- ArchitectPLAgent verdict packet 의 `pl_recommendation` 을 `FIX` 로 설정
- review-verdict-v4 `findings[]` 에 mechanical 누락 항목 each row 추가 (severity P1 — `mechanical_sync_required`)
- ArchitectAgent re-spawn — 누락 항목 only 보완 후 self-check 재실행
- Story §10 FIX Ledger row append (Orchestrator monopoly, fix-event-v1 contract)

### 결정 5: marketplace 영역 self-check 는 ADR-063 SSOT — 본 ADR scope 외

marketplace mirrored field (`name` / `version` / `description` / `author`) 변경 관련 3-file atomic invariant (`plugin.json` / `CHANGELOG.md` / `marketplace.json`) = ADR-063 SSOT. 본 ADR-065 = non-marketplace 영역 7 항목 한정.

cross-ref only — 중복 codification 회피.

**marketplace 영역 ArchitectAgent Phase 1 self-check trigger = [ADR-063 §결정 9](ADR-063-marketplace-atomic-invariant.md) (CFP-597 Amendment 1) 참조.**

### 결정 6 — Family scope self-app invariant (Amendment 1, CFP-685)

§결정 1 row 3 (wrapper repo `templates/github-workflows/X.yml ↔ .github/workflows/X.yml` byte-identical) 의 **family scope 확장**. wrapper repo 자체 self-app 외에 codeforge family 7-repo (wrapper + 6 lane plugin sibling: codeforge-{requirements,design,develop,test,review,pmo}) 의 `.github/workflows/<X>.yml` 도 wrapper `templates/github-workflows/<X>.yml` 와 byte-identical 의무 영역.

**적용 scope (whitelist — 확장 시 별도 CFP 의무)**:

| 영역 | 적용 여부 | 근거 |
|---|---|---|
| `auto-phase-label.yml` | **YES** (Amendment 1 첫 entry) | CFP-685 carrier — Anchor #626 evidence (develop#23 stuck) |
| `phase-label-invariant.yml` | NO (Amendment 1 시점) | 별 Epic carrier 후보 (§결정 6 whitelist 확장 시) |
| `claude-md-line-cap.yml` | NO (Amendment 1 시점) | 별 Epic carrier 후보 |
| `wording-dictionary.yml` | NO (Amendment 1 시점) | 별 Epic carrier 후보 |
| `bootstrap-labels.yml` | NO | CFP-662 prior-art (label registration parity 영역, workflow file parity 와 분리) |
| 기타 wrapper workflow | NO | 별 CFP 의무 |

**검증 mode (E-5 mode-mixing 회피, CFP-685 §5.3 E-5 정합)**:
- **raw-byte equality + enforced LF** (1 mode 단독): `.gitattributes` 강제 LF (`<file>.yml text eol=lf` 의무) + `cmp -s` byte-level diff exit 0
- normalized semantic equality (whitespace / comment 차이 무시) 금지 — drift hiding risk 차단

**drift detection mechanism (CFP-685 Phase 1 carrier)**:
- `scripts/check-sibling-workflow-parity.sh` (신설, exit 0=PASS / exit 1=drift / exit 2=SETUP error — `check-marketplace-parity.sh:13-15` 패턴 verbatim 차용)
- `templates/github-workflows/sibling-workflow-parity.yml` (신설, warning tier, cron weekly Monday 10:00 UTC + `workflow_dispatch` manual trigger — `required-workflow-drift-check.yml:9` 패턴 차용)
- evidence-checks-registry entry `auto-phase-label-sibling-parity` (warning tier, `bypass_label: hotfix-bypass:auto-phase-label-sibling-parity` 22번째 family member — label-registry-v2 v2.16)

**Phase 2 sibling sync mechanism (cross-repo file write)**:
- 6 sibling repo `.github/workflows/auto-phase-label.yml` 신규 생성 PR 6건 (parallel open — parallel-dispatch-protocol-v1 정합, state-independent)
- PAT = `CODEFORGE_CROSS_REPO_PAT` (ADR-066 §결정 2 Amendment 2 정합, `repo:write` cover, 추가 secret 신설 0건)
- `GITHUB_TOKEN` 미사용 (same-repo scope 만, cross-repo write 불가 — CFP-685 §5.3 E-7 verified)

**ADR-005 cross-ref (audit trail)**:
- ADR-005 = "Plugin Self-Application N/A 표준화" (lane N/A handling 정책) — **본 ADR-065 §결정 6 family scope self-app convention 과 무관**
- CFP-685 FIX iter 1 정정 (Codex TP#4 F-5 finding `[verified]`) — ADR-005 ≠ workflow self-app convention SSOT
- 본 ADR-065 §결정 1 row 3 (Amendment 1 family scope 확장 포함) 이 actual self-app convention SSOT

**ratchet direction (top-down, ADR-064 §self-application top-down ratchet 정합)**:
- 강화 방향만 허용: family scope 확장 / 검증 mode 강화 / drift detection cadence 증가
- 약화 방향 차단: family scope → wrapper-only / sibling drift detection 면제 / Conservative no-rename policy (ADR-060 Amendment 7) revoke
- ADR-058 §결정 5 sunset_justification 의무 적용 — Amendment 차수 추가 시 강화 방향 evidence 의무

### 결정 7 — 8th item frontmatter YAML parse self-validate (Amendment 2, CFP-911)

§결정 1 표(원 7-row) 에 row 8 append 로 chief author self-check 항목을 8개로 확장. 신규 8번째 항목 = **"Phase 1 산출물 commit 직전 chief author 가 변경한 frontmatter 보유 `.md` file 의 YAML parse self-validate"** — 검증 방법 `bash scripts/check-doc-frontmatter.sh <path>` PASS (CFP-28 strict mode cross-ref).

**7.1 Incident reference (CFP-851)**:

CFP-851 Phase 2 PR (#885) 의 `docs/adr/ADR-071-orchestrator-user-dialog-convergence.md` amendment_log entry summary 안 `is_transitional: false` 의 콜론-공백 패턴이 YAML plain scalar 내부에서 nested mapping 으로 오해석돼 ScannerError 발생. CI (`scripts/check-doc-frontmatter.sh` strict mode — CFP-28 PR-time check) 가 사후 감지하여 FIX iter 1 로 해소 (commit `79a4fdda0c9b4ee249edfcdb3769ef95b8113628`, 2026-05-17 KST — `is_transitional: false` → `is_transitional=false` equals form, semantic 동일하지만 YAML scanner parse safe). 현재 file state HEAD 기준 재현 불가 — incident SSOT = git history (`git log --grep=CFP-851`, PR #885 commit chain `1c15e79 → 79a4fdd → 0fdfe6d`).

**핵심 gap**: PR-time CI 가 사후 감지 channel 로 작동 — chief author 의 **commit-time** forcing function 부재. row 8 신설이 이 gap 보완.

**7.2 Family pattern 정합 (Amendment 1 verbatim mirror)**:

- additive·strengthen 방향 only (7→8 항목 ratchet 확장)
- `sunset_justification: null` 금지 (quoted string form 의무) — ADR-071 family 의 `amendment_id` / `carrier_story` / `sunset_justification: null` 패밀리 schema 와 cross-pollination 차단 (Codex TP#4 P0 finding 흡수 결과)
- `is_transitional: false` 보존 (governance permanent, ADR-058 §결정 7 default presumption 정합)
- 기존 §결정 1 row 1-7 본문 변경 0
- §결정 2-6 변경 0
- `mechanical_enforcement_actions[]` = 기존 `check-doc-frontmatter.sh` cross-ref (신규 lint script 0건, `existing-warning-cross-ref` status)

**7.3 Cascade obligation invariant**:

§결정 1 row 8 의 검증 방법 wording 안 `bash scripts/check-doc-frontmatter.sh <path>` dependency 는 **두 file** 의 strict mode contract 의존:

- `scripts/check-doc-frontmatter.sh` (thin wrapper, ADR-061 §결정 1 정합)
- `scripts/lib/check_doc_frontmatter.py` (Python SSOT, exec target)

두 file 의 contract (exit code semantic / strict-mode 분기 / target path coverage) 가 변경되는 PR (예: 별도 CFP 가 script behavior change 발의 시) 는 ADR-065 §결정 1 row 8 wording 갱신 cascade 의무. 갱신 누락 시 row 8 forcing function silently drift — 사전 codified invariant 가 안전망. **cascade 검출 = manual review 의존** (별도 follow-up CFP carrier — cascade 자동 검출 lint 신설 검토, Story §5.4 row 7 정합).

**7.4 Doc-only fast-path 정합 (ADR-054)**:

본 Amendment 2 = 기존 ADR-065 본문 Amendment 만 (신규 ADR 0건). 단일 PR 안 deliverable:
- ADR-065 본문 Amendment 2 (frontmatter `amendments[]` row append + `mechanical_enforcement_actions[]` entry append + 본문 §결정 1 표 row 8 append + cascade obligation 1줄 + §결정 7 narrative + `## 관련 파일` Amendment 2 sub-section)
- `plugin.json` MINOR bump (ADR-037 governance behavior change — chief author 검증 의무 ratchet)
- `CHANGELOG.md` entry append (ADR-063 atomic)
- `marketplace.json` sibling sync (ADR-063 §결정 5 — 별도 sibling PR, codeforge PR merge 직후 즉시 open·merge)

src/tests 무변경, 신규 ADR / 신규 lint script / 신규 workflow yml / mechanical_enforcement_actions[] 신규 action name 0건 (Story §5.4 Out-of-Scope 7 항목 정합).

**7.5 무약화 invariant (Self-application top-down ratchet, ADR-064 §결정 정합)**:

- 강화 방향만 허용: 8th item 보존 / `check-doc-frontmatter.sh` cross-ref 강화 / 9th item ratchet 확장 (별도 CFP 발의 시)
- **약화 방향 차단**: 8th item 제거 / `check-doc-frontmatter.sh` cross-ref 해제 / `sunset_justification` quoted string → null 다운그레이드 / row 1-7 본문 약화 / Amendment 1 family pattern revoke
- ADR-058 §결정 5 sunset_justification 의무 적용 — `sunset_justification` 본문 안 약화 방향 발의 차단 명문화 ("약화 방향(8th item 제거 / check-doc-frontmatter.sh cross-ref 해제) 발의 차단" verbatim)

**7.6 Schema invariant (review-verdict-v4 v4.2 무변경)**:

review-verdict-v4 schema `mechanical_self_check_passed: bool` field semantic 무변경. 검증 항목 7→8 양적 확장만 — schema MINOR bump 0건. 6 lane plugin sibling PR 동반 의무 0건 (sibling sync 면제, Story §5.3 Non-Goals 정합).

## 결과

### 긍정적 결과

- chief author 의 산출물 commit 직전 mechanical sync 의무 인지 강화
- 매 Story 반복 결함 (CFP-393 3건 + 1건 + CFP-411) 사전 차단
- Phase 1 PR CI lint 에 도달하기 전 chief author 가 self-detect 가능
- review-verdict-v4 v4.2 packet 에 explicit marker — Orchestrator 가 FIX routing 결정 시 명시적 signal

### 부정적 결과

- chief author overhead 증가 (산출물 commit 직전 7 항목 검증 단계)
- 7 항목 detail noise → review-pl-base.md §3 P2 finding 증가 위험 — mitigation: 7 항목 한정, mechanical fast-path 정합 (Change Plan 본문 변경 0건 항목만)
- review-verdict-v4 schema MINOR bump → sibling sync PR 의무 (canonical = `plugin-codeforge-review`, wrapper sibling)

### Trade-off

- chief author 가 한 번 더 mechanical check 수행 → 5-10 min overhead vs Phase 1 PR FIX iteration 1회 (30+ min) 차단

### 결정 8 — 9th item Story self-declared correction commit application verify (Amendment 3, CFP-930)

§결정 1 표(8-row, post-Amendment-2) 에 row 9 append 로 chief author self-check 항목을 9개로 확장. 신규 9번째 항목 = **"Story 본문 self-declared correction (`~~old~~ → new` strike-through / `<del>` HTML / 'previously: X' 류 패턴) 의 chief author commit 실제 적용 verify"** — 검증 방법: Story §2/§6 등 declared correction 패턴 enumerate → 각 패턴이 본 PR commit 안 actual diff 로 적용되었는지 `git diff` / repo-wide grep cross-check. 누락 검출 시 RETURN to ArchitectPLAgent (chief author 재호출, ADR-004 author ≠ judge 보존).

#### 8.1 동기 (cross-Story pattern threshold reach, ADR-045 §D-9)

`chief_author_mechanical_sync_gap` 누적 2 occurrence — threshold reach (≥ 2):

- **CFP-795 first occurrence**: Architect §3 mandatory P1 finding inline FIX 시 ADR 본문 표·단락 8 anchor 동시 갱신 누락 (`feedback_codex_tp2_verify_before_trust` 8-mirror checklist lesson, retro F-1)
- **CFP-906 second occurrence**: Story §2.2 self-declared correction (`~~ADR-072~~ → ADR-72`) 18 occurrence 미적용 → DesignReviewPL Iter 1 P0 broken-link (F-DR-906-1) + P1 wording-SSOT (F-DR-906-2) 적발. ArchitectAgent §13.A row 4 "link target Phase 1 분배 PASS" mechanically false self-claim.

기존 7-item (§결정 1) + 8-item (Amendment 2 row 8 frontmatter YAML parse) 은 label-registry / doc-locations / workflow self-app / link target / MANIFEST / section-ownership / doc-locations / frontmatter YAML 영역 cover. **Story 본문에 self-declared 된 정정 지침이 commit 작성 step 에서 mechanical sync 누락**되어도 self-check 가 PASS self-claim 하는 gap 부재.

#### 8.2 신규 row 9 schema

- **검증 대상**: Story 본문 (§2 / §5 / §6 / §11.3 / 기타 author-editable section) 의 correction 패턴 — `~~text~~` strike-through, `<del>text</del>` HTML, "previously: X / now: Y" 류 prose, "before: X → after: Y" 류 prose
- **검증 방법**: Phase 1 산출물 commit 직전 chief author 가:
  1. Story 본문 안 correction 패턴 grep enumerate (예: `grep -E "(~~|<del>|previously:|before:.*→.*after:)" docs/stories/<KEY>.md`)
  2. 각 enumerate 된 패턴마다 `git diff <pre-commit>..<HEAD>` cross-check — actual diff 안 적용 verify
  3. repo-wide grep (`git grep "old token"`) — stale carry-over 0 verify
- **누락 검출 시**: ArchitectPLAgent 에 RETURN (mechanical_self_check_passed=false). PL 이 chief author 재호출 (ADR-004 author ≠ judge 보존)

#### 8.3 mechanical 자동 검출 deferred

본 §결정 8 = chief author **manual self-check** 만 codify. mechanical lint (Story body strike-through 패턴 자동 enumerate + commit diff 비교) = 별 follow-up CFP scope. `mechanical_enforcement_actions[]` `story-self-declared-correction-verify` entry status: `deferred-followup` — mechanical lint 신설 별 CFP merge 시점 status 승격.

#### 8.4 ADR-082 Amendment 1 scope b sister

[ADR-082 Amendment 1](ADR-082-write-time-self-write-verification-mandate.md) scope b (design-lane self-check + 정정 재귀) 와 직접 인접 sister carrier. ADR-082 = write-time verification SSOT, 본 ADR-065 §결정 8 = chief author commit-time self-check 의 sub-scope. boundary preserved — review-verdict-v4 carrier field 영향 (cross-plugin sibling sync 필요) 별 carrier 분리.

#### 8.5 row 1-8 본문 변경 0 invariant

§결정 1 row 1-8 본문 변경 0 (row 9 append 만). §결정 2-7 변경 0. Amendment 1 (family scope) + Amendment 2 (frontmatter YAML parse) family pattern 정합 — additive ratchet only (9th item 제거 / verify 의무 해제 발의 차단, ADR-058 §결정 5).

#### 8.6 sunset_justification: null (Amendment 1/2 family 정합)

`is_transitional: false` 보존 + `sunset_justification: "N/A — permanent policy 의 ratchet 강화..."` quoted-string-form 의무 (Amendment 2 §7.2 cross-pollination 차단 invariant 정합).

### 결정 9 — 10th item 선제-lint behavioral mandate + INV-1 parity kind:registry scope 확장 (Amendment 4, CFP-1242)

§결정 1 표(9-row, post-Amendment-3) 에 row 10 append 로 chief author self-check 항목을 10개로 확장 (behavioral mandate, (a)). 동반하여 기존 INV-1 parity lint 의 mechanical scope 를 kind:registry 영역으로 확장 ((b)). 두 영역은 동일 결함 class (kind:registry version parity unguarded) 의 behavioral + mechanical 양면 closure.

#### 9.1 (a) 선제-lint behavioral mandate (row 10)

신규 10번째 항목 = **"Phase 1 산출물 commit 직전 touched ADR/doc 에 대해 `bash scripts/check-doc-section-schema.sh <path>` + `bash scripts/check-adr-sunset-criteria.sh <path>` 로컬 선제 실행 (PASS 확인)"**.

- chief author 가 touched ADR / doc path 각각에 두 lint 를 commit 직전 로컬 선제 실행 → PASS 확인 후 commit.
- 사후 CI 도달 전 self-detect — 운영 phase Epic (project_cfp_1187_operational_phase_epic) 의 S3+ Story 가 본 선제-lint 프로세스로 FIX iter 0 을 달성한 효과 입증 (선제-lint 프로세스 효과: S3+ FIX 0).
- behavioral mandate only — mechanical action 아님 (chief author commit-time manual 선제 실행). `mechanical_enforcement_actions[]` 신규 entry 0건.

#### 9.2 (b) INV-1 parity mechanical scope 확장 — kind:registry (corrected diagnosis)

**정정된 진단 (CFP-1242 verify-before-trust catch)**: Issue 의 framing ("label-registry-v2 ↔ MANIFEST.yaml kind:registry parity") 은 imprecise 했음. 검증된 reality:

- `docs/inter-plugin-contracts/MANIFEST.yaml` 은 두 top-level 키 — `contracts` (9 kind:contract entry) + `registries` (9 kind:registry entry) — 를 가진다.
- INV-1 parity lint (`scripts/lib/check_inter_plugin_contracts_parity.py`, CFP-894 / ADR-060 §결정 6) 은 그동안 `manifest["contracts"]` 만 iterate — `manifest["registries"]` 를 **결코 검사하지 않았다**. 즉 kind:registry version parity 가 무방비였다 (S4 가 human review 까지 도달하게 한 정확한 gap).
- 이는 **"MANIFEST 가 kind:registry 를 제외한다"는 정책 exclusion 이 아니라 lint iteration gap** 이다. 기존 docstring 의 "kind:registry entries = ADR-010 §결정 2 sibling sync 면제 → parity 대상 외" 표현이 두 개념을 conflate 했다: sibling-sync 면제 (cross-repo, ADR-010 §결정 2) 는 MANIFEST↔frontmatter parity (wrapper-local invariant) 와 **orthogonal**. registry 는 cross-repo sibling sync 만 면제될 뿐, MANIFEST row ↔ wrapper-local frontmatter parity 는 여전히 invariant.

**Live drift 적발 (lint genuinely catches the live defect)**: `registries.label_registry` 가 `label-registry-v2.md` 에 대해 7개의 mis-ordered "Active" row (2.43, 2.44, 2.45, 2.49, 2.48, 2.47, 2.46 — out of order = parallel-session append drift) 를 나열한 반면, file frontmatter 는 `version: "2.50"`. 즉 2.50 이 MANIFEST 에 부재 → drift. 확장된 lint 가 이 live label_registry drift 를 실제 적발 (RED proof) → 동반 MANIFEST collapse (7 Active rows → single Active 2.50 row, v1 Archived row 보존) 후 PASS (GREEN proof). 나머지 8 registry 는 clean (frontmatter == single MANIFEST Active row), Archived (label-registry-v1) / Sunsetted (reconcile-protocol-v1) row 는 올바르게 non-Active 로 skip.

**확장 내용**: lint 가 두 섹션 모두 iterate — contracts (field=`contract_version`) + registries (field=`version`). Membership semantic: 한 file 의 frontmatter version 이 그 file 의 Active MANIFEST row version(s) 중 하나로 **나타나야** 함 (parallel-append 다중 Active row tolerant). 비-Active row (Archived / Sunsetted / Deprecated) 는 contracts 와 동일하게 skip. self-ref graceful (MANIFEST 부재 → exit 0) + exit code (0 PASS / 1 drift / 2 config error) 보존. 기존 7 contract check 100% 무회귀.

#### 9.3 동기 (cross-Story pattern threshold reach, ADR-045 §D-9 escalate_user)

`chief_author_mechanical_sync_gap` super-class 의 kind:registry parity unguarded 변종 — pattern_count 3 reach (ADR-045 §D-9 escalate_user):

- **S1 / S2 evidence**: kind:registry version parity 가 INV-1 lint scope 밖이라 MANIFEST row ↔ frontmatter drift 가 detect 되지 않음 (registry append-heavy 영역의 silent drift).
- **S4 evidence**: label_registry 7-row 누적 parallel-session append drift 가 human review 까지 도달 (mechanical (b) closure 부재의 직접 증상).

본 Amendment 가 behavioral (a) + mechanical (b) 양면으로 이 drift class 차단.

#### 9.4 mechanical_enforcement_actions[] = 기존 parity check scope 확장 cross-ref

신규 evidence-checks-registry entry 0건. 기존 `inter-plugin-contracts-parity` check (CFP-894 / ADR-060 §결정 6, warning tier) 의 scope 확장 cross-ref only (Amendment 2 의 `existing-warning-cross-ref` 패턴 정합). 신규 lint script / 신규 workflow yml / 신규 mechanical action name 0건 — 기존 parity check 가 kind:registry 영역까지 cover 하도록 확장만.

#### 9.5 row 1-9 본문 변경 0 invariant

§결정 1 row 1-9 본문 변경 0 (row 10 append 만). §결정 2-8 변경 0. Amendment 1/2/3 family pattern 정합 — additive ratchet only.

#### 9.6 sunset_justification (Amendment 1/2/3 family 정합)

`is_transitional: false` 보존 + `sunset_justification: "N/A — permanent policy 의 ratchet 강화..."` quoted-string-form 의무. 약화 방향(10th item 제거 / 선제-lint mandate 해제 / INV-1 parity kind:registry 재제외) 발의 차단 (ADR-058 §결정 5 / ADR-064 §self-application top-down ratchet).

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) — cross-ref 추가
- [`docs/inter-plugin-contracts/review-verdict-v4.md`](../inter-plugin-contracts/review-verdict-v4.md) — v4.1 → v4.2 MINOR bump
- `plugin-codeforge-design/agents/ArchitectAgent.md` — 7-item self-check 섹션 신설
- `plugin-codeforge-design/agents/ArchitectPLAgent.md` — verdict packet `mechanical_self_check_passed` 필드
- `plugin-codeforge-design/templates/change-plan.md` — §13 Phase 1 self-check 결과 섹션
- `plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v4.md` — canonical v4.2 MINOR bump

### Amendment 1 (CFP-685) 신설 파일

- [`scripts/check-sibling-workflow-parity.sh`](../../scripts/check-sibling-workflow-parity.sh) — Phase 2 carrier (drift detection lint, exit 0/1/2 3-tier)
- [`templates/github-workflows/sibling-workflow-parity.yml`](../../templates/github-workflows/sibling-workflow-parity.yml) — Phase 2 carrier (warning tier workflow, cron + dispatch + Issue auto-create)
- [`.github/workflows/sibling-workflow-parity.yml`](../../.github/workflows/sibling-workflow-parity.yml) — Phase 2 byte-identical self-app
- [`docs/evidence-checks-registry.yaml`](../evidence-checks-registry.yaml) — `auto-phase-label-sibling-parity` entry append (warning tier, Phase 1)
- [`docs/inter-plugin-contracts/label-registry-v2.md`](../inter-plugin-contracts/label-registry-v2.md) — v2.15 → v2.16 MINOR (hotfix-bypass:auto-phase-label-sibling-parity 22번째 family member, Phase 1)
- 6 sibling repo `.github/workflows/auto-phase-label.yml` — Phase 2 byte-identical deploy (6 cross-repo PR)

### Amendment 2 (CFP-911) 신설 파일

- **이 ADR 본문** (`docs/adr/ADR-065-architect-phase1-mechanical-self-check.md`) — frontmatter `amendments[]` amendment 2 entry + `mechanical_enforcement_actions[]` `doc-frontmatter-yaml-parse` entry + `related_stories` CFP-911 + 본문 §결정 1 표 row 8 + §7.3 cascade obligation 1줄 + §결정 7 narrative section + 본 `### Amendment 2 (CFP-911) 신설 파일` sub-section
- [`scripts/check-doc-frontmatter.sh`](../../scripts/check-doc-frontmatter.sh) — **무수정** (기존 CFP-28 thin wrapper, row 8 cross-ref target)
- [`scripts/lib/check_doc_frontmatter.py`](../../scripts/lib/check_doc_frontmatter.py) — **무수정** (Python SSOT, ADR-061 §결정 1 정합, row 8 cross-ref target)
- [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) — version 5.84.0 → 5.85.0 MINOR (ADR-037 governance behavior change — chief author 검증 의무 ratchet 7→8)
- [`CHANGELOG.md`](../../CHANGELOG.md) — `[5.85.0] - 2026-05-17` entry append (ADR-063 atomic)
- `mclayer/marketplace:marketplace.json` `plugins[name=codeforge]` mirrored field (`name`/`version`/`description`/`author`) — Phase 2 atomic sibling sync (ADR-063 §결정 5, 별도 sibling PR, codeforge PR merge 직후 즉시 open·merge)

**신규 lint script / 신규 workflow yml / 신규 ADR / 신규 evidence-checks-registry entry / 신규 mechanical_enforcement_actions[] action name / 6 lane sibling PR / review-verdict-v4 schema bump / cascade 자동 검출 lint = 0건** (Story §5.4 Out-of-Scope 7 항목 정합).

### Amendment 4 (CFP-1242) 신설/변경 파일

- **이 ADR 본문** (`docs/adr/ADR-065-architect-phase1-mechanical-self-check.md`) — frontmatter `amendments[]` amendment 4 entry + `mechanical_enforcement_actions[]` `inter-plugin-contracts-parity` entry (scope 확장 cross-ref) + `related_stories` CFP-930·CFP-1242 + `related_adrs` ADR-008·ADR-045·ADR-064·ADR-082 + 본문 §결정 1 표 row 10 + §결정 9 narrative section + 본 sub-section
- [`scripts/lib/check_inter_plugin_contracts_parity.py`](../../scripts/lib/check_inter_plugin_contracts_parity.py) — INV-1 parity lint **scope 확장** (manifest['contracts'] 단독 → contracts + registries 양 섹션, field 분기 contract_version / version) + docstring 정정 (kind:registry 무방비 iteration gap, sibling-sync 면제 orthogonal)
- [`scripts/lib/test_check_inter_plugin_contracts_parity.py`](../../scripts/lib/test_check_inter_plugin_contracts_parity.py) — TC-8..TC-13 registries parity 테스트 추가 (TDD RED: TC-9 live label_registry drift 재현 + TC-12 missing version field)
- [`docs/inter-plugin-contracts/MANIFEST.yaml`](../inter-plugin-contracts/MANIFEST.yaml) — `registries.label_registry` 7 mis-ordered Active rows (2.43-2.49) → single Active 2.50 row collapse (label-registry-v1 Archived row 보존)
- [`scripts/check-doc-section-schema.sh`](../../scripts/check-doc-section-schema.sh) — **무수정** (row 10 (a) 선제-lint cross-ref target)
- [`scripts/check-adr-sunset-criteria.sh`](../../scripts/check-adr-sunset-criteria.sh) — **무수정** (row 10 (a) 선제-lint cross-ref target)
- [`CLAUDE.md`](../../CLAUDE.md) — ADR-065 inline description 에 Amendment 4 clause 추가
- [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) — version 6.1.1 → 6.2.0 MINOR (ADR-037 §결정 1(h) — additive amendment + lint behavior change = governance behavior change)
- [`CHANGELOG.md`](../../CHANGELOG.md) — `[6.2.0] - 2026-05-22` entry append (ADR-063 atomic)
- `mclayer/marketplace:marketplace.json` `plugins[name=codeforge]` mirrored field (`name`/`version`/`description`/`author`) — Phase 2 atomic sibling sync (ADR-063 §결정 5, 별도 sibling PR, codeforge PR merge 직후 즉시 open·merge)

**신규 lint script / 신규 workflow yml / 신규 ADR / 신규 evidence-checks-registry entry / 신규 mechanical_enforcement_actions[] action name = 0건** (기존 `inter-plugin-contracts-parity` parity check scope 확장 cross-ref only — 기존 안전망이 kind:registry 영역까지 cover).
