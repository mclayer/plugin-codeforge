---
adr_number: 27
title: Consumer Adoption Protocol — bootstrap + 3-trigger enforcement
status: Proposed
category: Plugin Distribution & Consumer Onboarding
date: 2026-05-05
carrier_story: CFP-96
related_files:
  - overlay/hooks/check-bootstrap.sh
  - overlay/hooks/regen-agents.sh
  - overlay/_overlay/project.yaml.example
  - templates/github-workflows/phase-gate-mergeable.yml
  - docs/consumer-guide.md
  - CHANGELOG.md
related_stories:
  - CFP-96
  - CFP-103
  - CFP-104
  - CFP-105
  - CFP-106
  - CFP-107
  - CFP-108
  - CFP-127
amendments:
  - ADR-032
  - ADR-027-Amendment-2-CFP-658  # CFP-658 Wave 1 of Epic CFP-431 — Action-blocked manual fallback path normative SSOT
  - ADR-027-Amendment-3-CFP-702  # CFP-699 Wave 1 Story-2 — D4 customization marker 의무 추가 (# BEGIN/END wrapper-managed block)
  - ADR-027-Amendment-4-CFP-820  # CFP-699 Wave 3 Story-6 — consumer adoption 시 codeforge.version_pin schema detection 의무 (3-way version atomic invariant consumer layer, ADR-063 Amendment 5 §결정 15 동반). §결정 8 신설
  - ADR-027-Amendment-5-CFP-821  # CFP-699 Wave 3 Story-7 — consumer adoption 시 Issue Forms enumeration 정정 (3종 → audit+bug+story+discussion+codeforge-improvement 5 forms + config.yml) + D4 marker form-level wrap cross-ref (D1 coverage fan-out, ADR-076 §결정 2 표 PR template row 동반). §결정 9 신설
mechanical_enforcement_actions:
  - action_name: section-1-verbatim-postmerge
    decision_binding: "Amendment 2 §결정 6.A — manual fallback path 의 §1 verbatim invariant post-merge lint (warning tier)"
    evidence_registry_entry: section-1-verbatim-postmerge  # docs/evidence-checks-registry.yaml row
    bypass_label: hotfix-bypass:section-1-verbatim-postmerge
    carrier_cfp: CFP-658  # Phase 1 = SSOT 등재, Phase 2 = workflow + script 신설
    introduced_by_amendment: 2
  - action_name: wrapper-managed-block
    decision_binding: "Amendment 3 §결정 7 — consumer customization 영역의 # BEGIN/END wrapper-managed marker block 정합성 lint (blocking-on-pr tier). marker block 안 = wrapper SSOT desired state, 밖 = consumer customization preserve invariant 의 mechanical enforcement"
    evidence_registry_entry: wrapper-managed-block  # docs/evidence-checks-registry.yaml row (Phase 2 PR append, blocking-on-pr tier)
    bypass_label: hotfix-bypass:wrapper-managed-block
    carrier_cfp: CFP-702  # Phase 1 = ADR Amendment 3 + change-plan SSOT, Phase 2 = lint + workflow + migration script 신설
    introduced_by_amendment: 3
supersedes: null
superseded_by: null
is_transitional: false
---

# ADR-027: Consumer Adoption Protocol — bootstrap + 3-trigger enforcement

## 상태

Proposed (2026-05-05). CFP-96 Epic carrier ADR. Phase 2 (CFP-103 + CFP-104) implementation 완료 시 Accepted.

## 컨텍스트

mctrader 데뷔 audit (2026-05-02 ~ 2026-05-05) 7 Epic (MCT-12, MCT-18, MCT-25, MCT-32, MCT-37, MCT-48, MCT-63) 모두 main merge — 그러나 **6 lane plugin 0개 spawn**, manual Codex 7-area + Sonnet decider 패턴으로 우회. 검증된 사실 (2026-05-05):

- `~/.claude/plugins/installed_plugins.json` 등록 plugin = 4개 (`github` / `superpowers` / `claude-md-management` / `codex`). codeforge family **0개**.
- `mclayer/marketplace` repo 부재 (`gh api repos/mclayer/marketplace` → 404)
- 6 lane plugin GitHub repo 모두 존재 (`mclayer/plugin-codeforge-{requirements,design,develop,test,review,pmo}`) + 로컬 working dir clone 도 존재
- mctrader-hub `.claude/settings.json` SessionStart hook 이 `${CLAUDE_PLUGIN_ROOT}/codeforge/...` 참조하지만 wrapper 미설치로 silently dropped (#169 와 일치)

사용자 명시 (2026-05-05):

> codeforge는 무조건 사용해야 한다. 사용이 어렵다면 시간이 오래 걸리더라도 issue escalation 해서 개선하는 방식으로 가야 한다. 지금까지 사용하지 못했던 원인도 찾아 모두 제거하고 변경 착수시마다 codeforge를 사용하도록 해야 한다.
> 처음 시작시 codeforge 사용 선언시 의존 관계 플러그인 설치 등 이번 epic은 codeforge 반영 자체에 필요할 것이다.

본 ADR 은 consumer 가 처음 plugin 사용 선언 시점부터 변경 착수 시점까지 codeforge 사용을 enforce 하는 protocol 표준화.

## 결정

### 결정 1 — bootstrap 검증 책임 = wrapper plugin overlay/hooks/

Consumer 측 책임은 `.claude/settings.json` 에 hook 등록 + `.claude/_overlay/project.yaml` 작성만. 검증 로직 자체는 wrapper plugin `overlay/hooks/check-bootstrap.{sh,ps1}` 가 SSOT.

검증 항목 (`installed_plugins.json` 검사):

- codeforge wrapper + 6 lane plugin (`codeforge-{requirements,design,develop,test,review,pmo}`)
- 4 dependency: `github`, `codex`, `superpowers`, `claude-md-management`
- **9 plugin total**

추가 검증:

- consumer `.github/workflows/` 11종 (CFP-105 close 후 14종) sync
- consumer `.github/ISSUE_TEMPLATE/` 5 forms (audit + bug + story + discussion + codeforge-improvement) + `config.yml` sync (Amendment 5 §결정 9 정정 — 旧 stale "3종 (audit + bug + story)" = enumeration gap, reality audit + bug 2종 only / D1 fan-out 후 5 forms + config.yml SSOT. ADR-068 I-4 wording SSOT 정합)
- `CODEOWNERS` + branch protection 정합
- `.claude/_overlay/project.yaml` schema validation (per `docs/project-config-schema.md`)

### 결정 2 — 3-trigger enforcement model invariant

**Primary — Story phase 진입**: 기존 `phase-gate-mergeable.yml` + `phase-label-invariant.yml` workflow. CFP-96 Phase 4 (CFP-106) 에서 #143 fix (doc-only PR fast-pass) + #144 fix (CI terminal state classification) 적용.

**Secondary — UserPromptSubmit hook (NEW, CFP-104)**: consumer `.claude/settings.json` 에 등록, wrapper `overlay/hooks/userprompt-reminder.{sh,ps1}` 호출. 검출 패턴 regex `(구현|만들|수정|짜|fix|implement|refactor|create|add)` 매치 + 활성 Story 미특정 ∨ phase label 부재 시 stdout 으로 reminder 출력 → Claude Code 가 LLM context 에 inject. **Block 아님 — warning inject only.**

**Tertiary — SessionStart hook (강화, CFP-103 + CFP-104)**: 기존 `regen-agents.sh` 호출 + 신규 `check-bootstrap.{sh,ps1}` 강화. 부재/불일치 시 stdout 으로 안내 + LLM context inject. **Claude Code hook 자체는 session 차단 권한 없음** — LLM 이 첫 reasoning turn 에 reminder 받아 사용자에게 dependency 미충족 surface + 후속 작업 이전에 install 안내 (enforcement = LLM 측 책임).

### 결정 3 — Bypass 메커니즘

긴급 hotfix 등에서 enforcement 우회 필요 시:

```
HOTFIX_BYPASS_CODEFORGE=1
HOTFIX_BYPASS_REASON="<사유 텍스트>"
```

두 env flag 동시 설정 의무. bypass 사용 시:

- hook 의 reminder/warning 출력 skip
- `docs/hotfix-playbook.md` 에 사유 등재 의무
- bypass 후 후속 audit issue 자동 생성 (post-bypass audit, CFP-106 Phase 4 에서 detail)

### 결정 4 — Cross-platform 의무 (POSIX + Windows)

Hook 구현은 양 OS 모두 검증:

- POSIX: bash 5.x+ (Linux, macOS)
- Windows: PowerShell 5.1+ (mctrader-hub Windows 환경 정합)

consumer `.claude/settings.json` 에 OS 분기 등록 (또는 wrapper 가 `$OSTYPE` / `$env:OS` 분기). 단위 테스트 양 platform CI 의무 (CFP-103 task).

### 결정 5 — consumer-guide.md 가 SSOT

Consumer 절차 SSOT = `docs/consumer-guide.md`. 본 ADR 은 결정만 freeze, 절차/명령어 SSOT 는 consumer-guide. CFP-106 Phase 4 에서 consumer-guide §X "CI terminal state classification" + §Y "bootstrap protocol" 추가.

## 결과

- mctrader-hub Phase 6 verify (CFP-108, #204) 후 protocol 정합 확인
- 향후 mclayer org 의 모든 신규 consumer (mctrader-market 외 5개 포함) 가 본 protocol 채택
- mctrader 의 7 기 완료 Epic 은 retroactive 처리 안 함 (manual artifact 유지)

## Out-of-scope

- IDE plugin / browser companion / WebSocket reload — 현 hook 메커니즘 한정
- CFP-50 marketplace parity CI 자동화 — Phase 5 manual sync 후 follow-up
- 6 lane plugin 의 internal redesign — 발견 시 별도 CFP-N

## 해소 기준

N/A — permanent policy

## 관련 파일

- `overlay/hooks/check-bootstrap.sh` (Phase 2 강화)
- `overlay/hooks/regen-agents.sh` (Phase 2 또는 4 #169 docstring fix)
- `overlay/hooks/userprompt-reminder.{sh,ps1}` (Phase 2 NEW)
- `overlay/_overlay/project.yaml.example` (Phase 2 schema 보강)
- `templates/github-workflows/phase-gate-mergeable.yml` (Phase 4 #143 fix)
- `templates/github-workflows/story-init.yml` 등 4종 (Phase 3 NEW, CFP-45 close)
- `docs/consumer-guide.md` (Phase 4 §X 추가)
- spec: `codeforge-internal-docs/wrapper/specs/2026-05-05-cfp-96-first-consumer-adoption-bootstrap-design.md`
- plan: `codeforge-internal-docs/wrapper/plans/2026-05-05-cfp-96-first-consumer-adoption-bootstrap-plan.md`

## Amendment 1 — Strict mode opt-in (ADR-032, CFP-127)

**Effective**: 2026-05-06 (CFP-127 Phase 1 PR #60 + Phase 2 PR #233 merged).

본 ADR §결정 2 (3-trigger enforcement model) Tertiary trigger (`check-bootstrap` SessionStart hook) 의 `LLM-trust default` 는 유지 (warning-only, exit 0). [ADR-032](ADR-032-adr-027-amendment-1-hard-enforcement.md) 가 **additive opt-in strict mode** 추가 — supersede 아님.

**Strict mode 활성 조건** (CLI > env > yaml priority):
1. `--strict` flag (`bash overlay/hooks/check-bootstrap.sh --strict`)
2. `CODEFORGE_STRICT_BOOTSTRAP=1` env
3. `bootstrap.strict_mode: true` in `.claude/_overlay/project.yaml`

**Strict 활성 + 4종 strict-eligible drift 발견 → exit 1** (Sonnet decider CFP-127-001 pick alpha):
- (a) `project.yaml` 부재
- (b) plugin 8 critical (wrapper + 6 lane + superpowers) 미설치
- (c) `settings.json` 3 hook (SessionStart × 2 + UserPromptSubmit × 1) 미등록
- (d) 18 label 중 phase:* (7) + gate:* (3) = 10 critical 부재

**Bypass priority HIGHEST**: §결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip. Bypass mechanism (§결정 3) 와 Strict mode (Amendment 1) 동시 작동, 별도 mechanism.

**Default 미변경** = warning-only. mctrader 6-repo 점진 도입 가능. 본 amendment = additive 만 (default behavior 변경 없음).

상세: [ADR-032](ADR-032-adr-027-amendment-1-hard-enforcement.md) §결정 1-5.

## Amendment 2 — Action 차단 시 agent direct write fallback path (CFP-658)

**Effective**: 2026-05-14 (CFP-658 Wave 1 of Epic CFP-431 Phase 1 PR merged).

**Carrier**: CFP-658 (`carrier_story`). Parent Epic CFP-431 (audit:from-mctrader-debut). Sibling Waves: CFP-660 (consumer workflow drift detection) / CFP-661 (enterprise prerequisite + graceful degradation).

본 ADR §결정 2 (3-trigger enforcement model) Primary trigger (`story-init.yml` 등 workflow) 가 enterprise GitHub Actions `default_workflow_permissions: read` 차단 환경 또는 일반 Action failure 시 silent skip 되는 single-point-of-failure 해소 + ADR-039 inline whitelist 외 영역 modification 금지 와 의무 충돌 해소.

본 amendment = ADR-027 §결정 2 Primary trigger 의 **fallback path** 추가 (additive, supersede 아님). §결정 6 신설.

### 결정 6 — Action 차단 시 agent direct write fallback path (normative SSOT)

#### §결정 6.A — Fallback trigger 정의 + 우선순위

2 trigger hybrid:

| Option | 정의 | 적용 영역 |
|---|---|---|
| **(A) Declarative** | `.claude/_overlay/project.yaml` 의 `bootstrap.fallback_mode: action_blocked` enable | 영구 차단 환경 (enterprise admin policy disable) default |
| **(C) Explicit ad-hoc** | Issue 발의자 또는 Orchestrator 가 `fallback:manual` label 부착 | per-Issue override (일시 outage / 사용자 explicit 선택) |

**우선순위 (C) > (A)** — per-Issue override > environment default.

**Option (B) Outage detection (workflow run conclusion + N분 timeout) 폐기** — Researcher 위험 1 (workflow self-fail detection 불가, silent failure) 차단.

#### §결정 6.B — 활성 agent + 책임 분배

| Agent | 역할 | 사유 |
|---|---|---|
| RequirementsPLAgent | §1-§7 직접 생성 (Issue body §1 verbatim copy) — **skip 가능** | mctrader-hub MCT-135 evidence 패턴 (brainstorm Phase 0 4-agent burst 합성 spec 이 §3-6 SSOT 대체 시 RequirementsPL 의 4 mandate verbatim 수행 = redundant spawn 회피, ADR-064 §결정 3 룰 1 derived default) |
| ArchitectPLAgent | Phase 1 PR manual `gh pr create` 책임 + Codex Touchpoint #2 dispatch | ADR-052 Amendment 4 mandatory 영역 |
| Orchestrator | phase label 수동 부착 + §14 Lane Evidence row append | ADR-031 / lane-self-write-boundary skill 정합 |

#### §결정 6.C — Governance ratchet 약화 mitigation 3종 (SecurityArch T1/T2/T3)

| Invariant | Mitigation | Tier |
|---|---|---|
| §1 verbatim immutable | post-merge lint `section-1-verbatim-postmerge.yml` (Phase 2 carrier) — Story §1 ↔ Issue body §1 byte-identical, drift 시 `hotfix-bypass:section-1-verbatim-postmerge` audit comment 자동 발의 | warning (ADR-060 framework) |
| phase-label transition | Orchestrator 수동 의무 (`codeforge:lane-self-write-boundary` skill 정합) | governance |
| 4 required check | manual PR 도 phase-gate-mergeable + doc frontmatter + doc section + invariant-check 통과 의무 (`enforce_admins:true` ratchet 유지, CFP-70) | blocking |

#### §결정 6.D — PAT scope 최소권한 표 (SecurityArch 조건 2)

| Scope | 필요 여부 | 사유 |
|---|---|---|
| `repo` | required | Issue read / branch create / PR open |
| `read:org` | required | org membership 검증 |
| `write:packages` | forbidden | 본 fallback 범위 외 |
| `admin:*` | forbidden | governance ratchet 약화 vector |

GitHub App 권장 (ADR-066 90 days rotation 정합).

#### §결정 6.E — Shell injection 차단 (SecurityArch 조건 3)

Issue body parse 시 shell injection 위험 영역. `manual-story-init-fallback.sh` (Phase 2 carrier) 안 `printf '%s'` + heredoc single-quoted 의무 (ADR-061 bash 인접 변형):

```bash
ISSUE_BODY=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body')
SECTION_1=$(printf '%s' "$ISSUE_BODY" | awk '/^## 1\./,/^## 2\./' | head -n -1)
cat > "docs/stories/${KEY}.md" <<'STORY_EOF'
${SECTION_1}
STORY_EOF
```

#### §결정 6.F — 2-PAT namespace 분리 (OpRiskArch 조건 2)

| PAT name | Scope | 용도 |
|---|---|---|
| `CODEFORGE_CROSS_REPO_PAT` (기존) | repo + read:org | phase-gate-mergeable.yml + rate-limit-fallback-kpi.yml (ADR-066) |
| `CODEFORGE_FALLBACK_PAT` (신설) | repo only | manual fallback path 전용 — write:packages / admin:* 금지 |

namespace 분리 = fallback path 침해 시 blast radius 최소화.

#### §결정 6.G — Burst control + rate-limit (OpRiskArch 조건 3-4)

`manual-story-init-fallback.sh` 안 exponential backoff:
- 1차 retry: 1s wait — `[empirical-source: AWS SDK Builders' Library 'Timeouts, retries, and backoff with jitter' base * 2^attempt formula]`
- 2차 retry: 2s wait — `[empirical-source: 동상]`
- 3차 retry: 4s wait — `[empirical-source: 동상]`
- 초과: silent skip + `fallback:rate-limited` label 부착 — max 3 retry `[empirical-source: GitHub Actions secondary rate-limit conservative bound — 4xx burst 5+ retry 시 blocklist 진입 위험]`

#### §결정 6.H — Existence check verbatim port (DataMigrationArch 조건)

`templates/github-workflows/story-init.yml` L107-124 의 `existence_check` step (CFP-280 Iter 1 FIX, `gh api repos/<owner>/<repo>/branches/<branch>` atomic) 을 `manual-story-init-fallback.sh` 에 verbatim port — race fix manual fallback 영역으로 propagate 의무.

#### §결정 6.I — Trigger (C) ad-hoc PR description checklist mirror (OpRiskArch 조건 1)

`fallback:manual` label 부착 PR description 의무 영역:

```markdown
## Manual fallback checklist
- [ ] Issue body §1 verbatim copy (byte-identical 검증)
- [ ] KEY = PREFIX-${ISSUE_NUMBER} (ADR-036 atomic)
- [ ] Branch existence_check (`gh api repos/<owner>/<repo>/branches/<branch>`)
- [ ] PR opened via `gh pr create`
- [ ] phase:요구사항 label 부착
- [ ] `fallback:manual` label 부착
```

silent failure detection forcing function.

### Bypass 정합

§결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip. Amendment 2 fallback path 활성 시에도 §결정 3 bypass mechanism 그대로 작동 — 별도 mechanism.

### Default 미변경 = additive only

본 amendment = additive 만 (default behavior 변경 없음). consumer overlay 의 `bootstrap.fallback_mode` 부재 = default `auto` = 기존 동작 보존 (backward-compat).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-658-action-blocked-fallback.md`.

Cross-ref:
- [ADR-032](ADR-032-adr-027-amendment-1-hard-enforcement.md) — Amendment 1 strict-eligible 4종
- [ADR-036](ADR-036-project-key-atomic-reservation.md) — KEY atomic invariant 보존
- `docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md` — recovery runbook
- `docs/consumer-guide.md` §"Action 차단 환경 fallback" — consumer runbook
- `docs/orchestrator-playbook.md` §"fallback decision tree" — Orchestrator detection 절차
- `docs/project-config-schema.md` `bootstrap.fallback_mode` — schema

## Amendment 3 — D4 customization marker 의무화 (CFP-702)

**Effective**: 2026-05-15 (CFP-699 Wave 1 Story-2 Phase 1 PR merged 시점).

**Carrier**: CFP-702 (`carrier_story`). Parent Epic CFP-699 (선언적 reconciliation 기반 codeforge upgrade flow). Sibling Wave 1 Story-1: CFP-701 (reconciliation contract + ADR-076 + reconcile-protocol-v1, **MERGED prerequisite**).

본 ADR §결정 1 (bootstrap 검증 책임 = wrapper plugin overlay/hooks/) + §결정 5 (consumer-guide.md SSOT) 정합. ADR-076 (Story-1 carrier) 의 reconcile-protocol-v1 contract 가 `customization_preservation_entry: "marker_block"` + `marker_block_syntax_carrier: "CFP-702"` 로 본 Amendment 3 에 syntax 영역을 명시적 위임. 본 amendment = ADR-027 §결정 추가 (additive, supersede 아님). §결정 7 신설.

### 결정 7 — D4 customization marker block 의무 (normative SSOT)

#### §결정 7.A — marker block syntax 정식 정의

Consumer customization 영역과 wrapper SSOT desired state 영역을 명문화·구분하는 marker block:

```
# BEGIN wrapper-managed
<wrapper SSOT desired state mirror 영역 — upgrade 시 wrapper 최신 버전 기준 mirror>
# END wrapper-managed
```

**Comment prefix per-filetype** (§결정 7.A.1 — Axis 1 결정):

| File type | BEGIN marker | END marker | 적용 영역 |
|---|---|---|---|
| `.yml` / `.yaml` (project.yaml, workflow) | `# BEGIN wrapper-managed` | `# END wrapper-managed` | overlay project.yaml / consumer-local workflow |
| `.sh` / shell hook | `# BEGIN wrapper-managed` | `# END wrapper-managed` | `.claude/hooks/` fragment |
| `.md` (CLAUDE.md overlay) | `<!-- BEGIN wrapper-managed -->` | `<!-- END wrapper-managed -->` | `.claude/_overlay/CLAUDE.md` |
| `.json` (settings.json) — **marker-incapable** | (sidecar manifest) | (sidecar manifest) | `.claude/_overlay/.wrapper-managed-manifest.json` sidecar — JSON 은 주석 불가, key-path allowlist 방식 (실 구현 = Wave 2 Story-5 carrier, 본 Amendment 3 = sidecar 영역 declare only) |

**결정 근거** (Axis 1): file-type 별 native comment prefix variant 채택 — 단일 `#` 강제는 `.md` (markdown 은 `#` 가 heading) 충돌, JSON 은 주석 자체 불가. comment-syntax-bearing 영역 (`.yml`/`.sh`)은 `#`, markdown 은 HTML comment, JSON 은 sidecar manifest. 외부 prior art = Ansible blockinfile `marker` 파라미터 (file-type 별 comment prefix 주입 패턴, Story §6.2 표 정합도 "가장 높음").

#### §결정 7.B — marker block 안 = wrapper SSOT, 밖 = consumer customization preserve invariant

- **marker block 안 영역** = wrapper SSOT desired state target. upgrade 시 wrapper 최신 버전 기준 **wholesale mirror** (consumer 변경 무시 — wrapper wins inside block).
- **marker block 밖 영역** = consumer customization = **preserve** (upgrade 시 wrapper 가 절대 침범 0 — consumer wins outside block).

이는 reconcile-protocol-v1 §3.2 Rule 3.2.1 의 verbatim cross-ref. codeforge 모델 = "wrapper SSOT wins inside marker block, consumer wins outside" — npm / Helm 의 'consumer wins' default 와 **reverse** (SSOT-driven 모델, Story §6.1 Unknown unknowns 정합). 외부 prior art 동형 = Kustomize base(wrapper SSOT) + overlay(consumer customization) 분리.

#### §결정 7.C — marker 부재 fallback = wholesale_mirror_with_user_visible_loss_report

Consumer 가 marker block 도입 전 customization 영역 보유 시 (mctrader 5 repo 등 기존 adopter):

- snapshot 안 해당 file 전체 보존 (full backup — reconcile-protocol-v1 Rule 3.2.2 cross-ref)
- wholesale mirror 후 **user-visible loss report 생성** (`docs/upgrade-events/<date>-<version>.md` 안 `## Wholesale mirror losses` § 명시)
- **silent overwrite 0** invariant (EPIC-AC-4 "충돌 시 명시적 보고 (silent overwrite 0)" verbatim 정합)

reconcile-protocol-v1 `marker_block_absent_behavior: "wholesale_mirror_with_user_visible_loss_report"` field 의 verbatim cross-ref. 본 fallback = graceful degradation (marker 부재 = breaking 아님, additive governance — backward-compat).

#### §결정 7.D — lint mechanical enforcement (blocking-on-pr tier)

`scripts/check-wrapper-managed-block.sh` (Phase 2 carrier) — marker block 정합성 검증:

- **BEGIN/END pairing**: 모든 BEGIN 은 대응 END 보유 (orphan BEGIN / orphan END = malformed → exit ≠ 0)
- **순서 invariant**: BEGIN 이 END 보다 앞 (역전 = malformed)
- **nesting 정책** (§결정 7.D.1 — Axis 2 결정): **flat only — nesting 금지** (BEGIN ... BEGIN ... END ... END = lint reject). 결정 근거: nested marker 는 wrapper SSOT 영역 안에 consumer customization 을 중첩 = "marker 안 = 100% wrapper, 밖 = 100% consumer" invariant (§결정 7.B) 와 모순. depth tracking 복잡도 회피 + Ansible blockinfile flat-only 패턴 동형.
- **evidence-checks-registry tier**: `current_tier: blocking-on-pr` (Story §5.2 AC-3 + Spec §7 Story-2 row verbatim). bypass channel = `hotfix-bypass:wrapper-managed-block` label (ADR-024 §결정 6.A per-entry namespace).
- **workflow self-app**: `templates/github-workflows/wrapper-managed-block.yml` ↔ `.github/workflows/wrapper-managed-block.yml` byte-identical (ADR-065 §결정 1 정합).

##### §결정 7.D.2 — lint file-scope = consumer customization 영역 한정 (self-referential skip-list, Axis 5 결정 / CFP-702 FIX iter 2 설계 회귀)

wrapper-managed-block lint 의 검사 대상 file-scope = **consumer customization 영역 한정**. wrapper plugin 자기 meta 파일은 **skip-list 제외** — marker 문자열을 데이터 / 로직 / 문서 / fixture 로 보유하는 self-referential 파일이 actual marker block 으로 오탐되는 것 차단.

**Skip-list (dogfooding self-detection 회피 invariant)** — 다음 generalized 패턴:

1. **lint 구현 자체**: `scripts/check-wrapper-managed-block.sh` (marker 문자열 = grep 패턴 데이터)
2. **lint test fixture**: `scripts/test-check-wrapper-managed-block.sh` (marker 문자열 = malformed/정상 fixture)
3. **migration 구현**: `scripts/migrate-existing-customization.sh` (marker 문자열 = wrap 삽입 데이터)
4. **lint 을 설명하는 SSOT 문서**: `docs/inter-plugin-contracts/reconcile-protocol-v1.md` + `docs/evidence-checks-registry.yaml` + `docs/adr/ADR-027-consumer-adoption-protocol.md` (본 ADR 자신 — marker syntax 문서화 영역)
5. **lint workflow YAML**: `.github/workflows/wrapper-managed-block.yml` + `templates/github-workflows/wrapper-managed-block.yml` (marker 문자열 = workflow step 데이터)

**generalized rule** (enumeration 외 future-proof): "wrapper-managed-block lint 자신 + 그 lint 를 설명·테스트·구현하는 wrapper plugin SSOT 파일" = self-referential → skip. consumer customization 영역 (overlay 4-layer + consumer-local workflow) 만 actual 검사 대상. 결정 근거: D4 marker 의 의미적 scope (§결정 7.B) = **consumer 측 customization 영역의 wrapper SSOT ↔ consumer 경계 명문화** — wrapper plugin 자기 meta 파일은 애초에 marker block 의미 적용 영역 자체가 아님 (consumer 가 customize 하는 파일 아님). under-specified 설계 (FIX iter 2 이전 §결정 7.D 가 file-scope 미명세) 가 Phase 2 dogfooding 에서 7-file false positive 노출 → 본 §결정 7.D.2 가 의미적 scope 를 mechanical scope 로 확정·명문화.

##### §결정 7.D.3 — marker 매칭 = whole-line anchored (substring 매칭 금지, Axis 5 결정 / CFP-702 FIX iter 2 설계 회귀)

lint 의 marker detection = **whole-line anchored 매칭** 의무:

- shell 구현: `grep -xF "<marker>"` (full-line fixed-string) 또는 `grep -E '^# BEGIN wrapper-managed$'` (anchored 정규식)
- **substring 매칭 금지**: `grep -F` (substring) 은 `# BEGIN wrapper-managed-other` / 주석 안 `# ... # BEGIN wrapper-managed ...` / 문서 inline reference 같은 prefix-collision 및 부분문자열 false positive 유발 — FIX iter 2 root cause (현 Phase 2 구현 L96-97 `grep -cF` substring 매칭).
- comment prefix per-filetype (§결정 7.A.1) 별 anchored 패턴: `.yml`/`.sh` = `^# BEGIN wrapper-managed$` / `.md` = `^<!-- BEGIN wrapper-managed -->$` (선/후행 whitespace tolerance 는 구현 spec — change-plan §3, leading whitespace trim 후 anchor).

결정 근거: marker block = **줄 단위 boundary 선언** (§결정 7.A syntax — marker 는 자체 라인 점유). substring 매칭은 marker 의 줄 단위 의미를 위반 → whole-line anchor 가 marker syntax 의 의미적 정합. Ansible blockinfile 의 marker 도 전용 라인 점유 (동형 prior art).

**additive 정합**: §결정 7.D.2 / §결정 7.D.3 = additive (supersede 0). §결정 7.D.1 flat-only nesting + §결정 7.D evidence-tier / workflow self-app 모두 무손상 유지. governance 강화 방향 ratchet (false positive 차단 = lint 정밀도 강화) — ADR-058 §결정 5 sunset_justification 불요 (강화 방향).

#### §결정 7.E — retroactive migration (idempotent)

`scripts/migrate-existing-customization.sh` (Phase 2 carrier) — 기존 marker-부재 consumer (mctrader 5 repo, Tier B-extended) retroactive auto-wrap:

- **idempotency invariant**: N회 실행 = 1회 effect (이미 wrap 된 영역 재wrap 0). 2차 실행 = file hash 동일 (Story §5.2 AC-4 testable predicate). 외부 prior art = Ansible blockinfile marker-pair replace idempotency 동형.
- **false-positive boundary** (§결정 7.E.1 — Axis 3 결정): **wrapper SSOT template 과 byte-diff 가 0 인 영역 + `consumer-scripts.manifest` 등재 영역만 wrap** (conservative — consumer customize 영역은 marker 밖 보존). 결정 근거: byte-diff 0 = consumer 가 손대지 않은 순수 wrapper SSOT mirror 영역임이 mechanical 확정 → false-positive 0. manifest 등재 = wrapper 가 consumer 에 배포하는 영역의 explicit SSOT (Story §2 Refactor perspective — `consumer-scripts.manifest` 가 wrapper SSOT mirror 영역 anchor).
- **사용자 결정 분기 0 invariant**: false-positive boundary 가 사용자 prompt 없이 mechanical 판정 (byte-diff + manifest = 결정론적). dry-run preview 는 정보 제공만 = 결정 분기 아님 (reconcile-protocol-v1 `dry_run_classified_as_decision_branch: false` verbatim 정합, CFP-699 Epic §1 WHY "0 자리" directive 정합).

#### §결정 7.F — lint promotion_criteria (Axis 4 결정)

`wrapper-managed-block` evidence-checks-registry entry 의 promotion_criteria (blocking-on-pr 첫 도입이므로 Story-1 `worktree-first-pre-checkout` entry 패턴 reference):

| Field | 값 | 근거 |
|---|---|---|
| `pr_cumulative_min` | 20 | ADR-060 §결정 6 (a) 표준값 — `worktree-first-pre-checkout` L634 verbatim 동형 |
| `failure_threshold` | 0 | ADR-060 §결정 6 (b) — bypass 외 failure 0 |
| `current_tier` | `blocking-on-pr` | Spec §7 Story-2 row verbatim ("blocking-on-pr"). ADR-060 4-tier enum 의 2번째 tier — D4 marker 위반 = customization wholesale loss 직결 (HIGH risk) → warning tier 시작점 아닌 blocking-on-pr 직접 도입 정당 (Story §5.3 AC-3 edge 정합) |

#### §결정 7.G — reconcile-protocol-v1 4.3 (b) trigger 발동

Story-1 contract `reconcile-protocol-v1.md` §4.3 (b): "Wave 1 Story-2 (CFP-702) merge — marker block syntax 확정 시 `customization_preservation_entry` 영역 확장". 본 Amendment 3 에서 marker syntax 정식 확정 (§결정 7.A) → contract 4.3 (b) trigger 발동. **단 contract 갱신 = Phase 2 PR scope** (kind:registry MINOR sibling sync 면제, ADR-008 §결정 2 + ADR-010 §결정 2). Phase 1 (본 ADR Amendment 3) = syntax SSOT 확정만, contract `customization_preservation_entry` 영역 확장 반영 = Phase 2 PR 에서 동반 (Story §4.0.1 "reconcile-protocol-v1.md 수정 = Phase 1 또는 Phase 2 (ArchitectAgent 결정)" → **Phase 2 결정** — marker syntax 가 lint script 와 atomic 하게 검증되어야 contract 영역 확장이 mechanical 유효).

### Bypass 정합

§결정 3 `HOTFIX_BYPASS_CODEFORGE=1 + REASON` 양 env set → strict 무관 hook self skip. Amendment 3 marker lint 활성 시에도 §결정 3 bypass mechanism 그대로 작동. 추가로 marker lint per-entry bypass = `hotfix-bypass:wrapper-managed-block` label (ADR-024 §결정 6.A per-entry namespace, ADR-060 framework 정합) — 별도 mechanism.

### Default 미변경 = additive only

본 amendment = additive 만. marker 부재 consumer = §결정 7.C wholesale_mirror_with_user_visible_loss_report fallback (graceful degradation, backward-compat). 기존 consumer 동작 즉시 변경 0 — migration script (§결정 7.E) 가 retroactive opt-in 보장.

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy, 기존 §"해소 기준" = "N/A — permanent policy" verbatim). Amendment 3 = D4 marker 의무 추가 = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-702-d4-customization-marker.md`.

Cross-ref:
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — Story-1 carrier, reconcile semantic SSOT (boundary disjoint — ADR-076 = upgrade transaction layer / 본 Amendment 3 = consumer customization marker enforcement layer)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` §3.2 Rule 3.2.1/3.2.2 + §4.3 (b) — customization preservation entry SSOT
- [ADR-053](ADR-053-structural-change-restart-prerequisite.md) §D2 — 본 Story 구조적 변경 (scripts/+workflow 신규) → Wave 2 Story-5 진입 prerequisite (dogfood-out 면제 분기)
- [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) — blocking-on-pr tier 첫 도입 (`wrapper-managed-block` registry entry)
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) §결정 1 — workflow templates/ ↔ .github/ byte-identical self-app
- [ADR-040](ADR-040-worktree-convention.md) §결정 7.A — `mechanical_enforcement_actions[]` frontmatter 의무 (본 Amendment 3 = `wrapper-managed-block` entry append)
- `docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` — Customization layer marker syntax detail (RequirementsPL 본 lane 보강)
- `docs/consumer-guide.md` §"D4 customization marker" — consumer runbook (Phase 2 carrier)

## Amendment 4 — consumer adoption 시 codeforge.version_pin schema detection 의무 (CFP-820)

**Effective**: 2026-05-17 (CFP-699 Wave 3 Story-6 Phase 1 PR merged 시점).

**Carrier**: CFP-820 (Wave 3 Story-6). Parent Epic CFP-699 (선언적 reconciliation 기반 codeforge upgrade flow). Sibling carrier: ADR-063 Amendment 5 §결정 15 (marketplace ↔ plugin.json atomic invariant 의 consumer-side 3-way 확장 — 본 Amendment 4 = ADR-027 consumer adoption protocol 측 schema detection 영역, ADR-063 = 3-way invariant 영역. 두 ADR boundary disjoint, cross-ref 정합).

본 ADR §결정 1 (bootstrap 검증 책임 = wrapper plugin overlay/hooks/) + §결정 5 (consumer-guide.md SSOT) 정합. ADR-063 Amendment 5 §결정 15 (3-way version atomic invariant) 가 consumer pin SSOT location 으로 `.claude/_overlay/project.yaml codeforge.version_pin` (FORM (b), 사용자 confirm 2026-05-17 KST) 를 확정 → 본 Amendment 4 = consumer adoption protocol 의 bootstrap/reconcile detection 영역에 `codeforge.version_pin` schema detection 의무를 codify. 본 amendment = ADR-027 §결정 추가 (additive, supersede 아님). §결정 8 신설.

**ADR collision 회피 (신규 ADR 아닌 Amendment — CFP-820 Story §3.1.5 판정 정합)**: ADR-027 = consumer adoption protocol SSOT — `bootstrap.fallback_mode` (Amendment 2) + `bootstrap.strict_mode` (Amendment 1) 패턴이 이미 consumer-side detection + fallback semantic 의 carrier. `codeforge.version_pin` warning-first → blocking fallback = ADR-027 Amendment 2 `bootstrap.fallback_mode` 의 동형 패턴 → 신규 ADR 신설 시 consumer adoption 영역 2 ADR 분산 (SSOT drift). Amendment = ADR-064 top-down ratchet 강화 방향 only (consumer adoption scope 확장 — version pin detection 추가).

### 결정 8 — consumer adoption 시 codeforge.version_pin schema detection (normative SSOT)

#### §결정 8.A — version_pin schema detection 의무

Consumer adoption 시 (bootstrap / reconcile) wrapper plugin overlay/hooks/ (`validate_config.py` — §결정 1 책임 영역) 가 `.claude/_overlay/project.yaml` 의 `codeforge.version_pin` block 등록 여부 detect:

| State | Detection 결과 | 동작 |
|---|---|---|
| `codeforge.version_pin` block 부재 | pin 미등록 (신규 consumer / 미설정) | **warning-first** — 3-way version parity lint skip + warn message "consumer pin SSOT 미등록 — codeforge.version_pin 등록 후 3-way enforce 활성" (exit 0). onboarding 마찰 0 |
| `codeforge.version_pin.version` 등록 (semver string) | pin 등록 | 3-way version parity enforce 활성 (publisher↔registry↔consumer pin byte-identical, mismatch = blocking-on-pr exit 1) |
| `codeforge.version_pin` 존재하나 `version` field 부재 / 비-semver | pin malformed | `validate_config.py` exit 4 (required field 누락/타입 위반 정합 — project-config-schema §6 verbatim) + actionable message. silent skip 금지 |

**결정 근거 (Axis — orthogonality invariant)**: `pin 가용성` (block 등록 여부 = enforce 가능 여부) 과 `version 정합성` (값 일치 여부 = drift 존재 여부) 은 ORTHOGONAL 2 조건 — 동일 fallback 에 conflate 금지 (CFP-745 FIX Iter 2 base-absent≠marker-absent verified-true precedent 답습. conflate 시 결함: pin 미등록 신규 consumer 즉시 blocking = onboarding 마찰 false-positive / pin 등록 consumer 실 drift 가 warning 약화 false-negative). 외부 prior art = ADR-027 Amendment 2 `bootstrap.fallback_mode: auto | action_blocked` 의 동형 패턴 (consumer onboarding 마찰 회피 → 등록 후 enforce).

#### §결정 8.B — warning-first → 등록 후 blocking fallback semantic (사용자 confirm 2026-05-17 KST)

- **pin 미등록** = warning-only (lint skip + warn, exit 0). pin 부재 = mismatch 판정 불성립 (비교 대상 없음 — false-positive 차단). onboarding 마찰 0 (ADR-027 Amendment 2 `bootstrap.fallback_mode` 패턴 답습)
- **pin 등록 후 mismatch** = blocking-on-pr (exit 1, PR 차단). drift 0 strict enforce (등록 영역)

이는 ADR-063 Amendment 5 §결정 15 `version_handshake_3way_binding.fallback_semantic` (reconcile-protocol-v1 v1.5 §4.8) 의 verbatim cross-ref. codeforge 모델 = "pin 미등록 = graceful skip (additive governance — backward-compat), pin 등록 = strict enforce". consumer-authored invariant 보존 — 모든 codeforge agent 는 `codeforge.version_pin` field write 금지 (project-config-schema §4b verbatim). 3-way lint = read-only compare-only (write surface 0).

#### §결정 8.C — schema location SSOT = project.yaml codeforge.version_pin (FORM (b))

consumer pin location = `.claude/_overlay/project.yaml` `codeforge.version_pin` block (기존 `codeforge:` block sibling sub-key — 기존 SSOT 확장, 신규 file 0, consumer 1-file 정책 정합). 별도 file (`.wrapper-plugin-pin.yaml`) / runtime artifact (`installed_plugins.json`) / hidden config root (`.codeforge/version-pin.yaml`) = 기각 (consumer 1-file 정책 위배 / 의도 declare semantic mismatch — CFP-820 Story §3.1.3 ALTERNATIVE 표 SSOT). schema 정의 = `docs/project-config-schema.md` `codeforge.version_pin` block (본 Amendment 4 동반 MINOR — `updated: 2026-05-17`).

#### §결정 8.D — mechanical enforcement = ADR-063 §결정 15 version-3way-atomic cross-ref (중복 codification 회피)

본 §결정 8 = consumer adoption protocol detection mandate (declarative SSOT). 실 mechanical lint = ADR-063 Amendment 5 §결정 15 의 `version-3way-atomic` evidence-check entry (blocking-on-pr tier, ADR-063 frontmatter `mechanical_enforcement_actions[]` 등재) 가 cover — `scripts/check-3way-version-parity.sh` (Phase 2 carrier) 가 3-way byte-identical version parity 검증. 본 Amendment 4 측 별도 mechanical action 신설은 **중복 codification 회피** (ADR-065 §결정 5 "cross-ref only — 중복 codification 회피" 정합) — ADR-063 marketplace 영역 ↔ ADR-027 consumer adoption 영역 boundary 정합. ADR-027 frontmatter `mechanical_enforcement_actions[]` = Amendment 2/3 entry 보존, Amendment 4 별도 entry 미추가 (ADR-063 §결정 15 entry 가 SSOT).

#### §결정 8.E — validate_config.py validator (Phase 2 carrier)

`overlay/hooks/validate_config.py` `SCHEMA_RULES` 에 `codeforge.version_pin` validator 추가 (Phase 2 carrier — PyYAML only, jsonschema 의존 회피, 기존 SCHEMA_RULES 패턴 정합 — project-config-schema §6 verbatim). Phase 1 (CFP-820) = declarative SSOT mandate (본 §결정 8). Phase 2 = validate_config.py validator 실 구현 + `overlay/_overlay/project.yaml.example` `codeforge.version_pin` 예시 row + `docs/consumer-guide.md` §2g.N consumer runbook.

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy, 기존 §"해소 기준" = "N/A — permanent policy" verbatim). Amendment 4 = consumer adoption 시 version_pin schema detection 의무 추가 = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합 — consumer adoption scope 확장 only, weakening 0).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-820-3way-version-atomic.md`.

Cross-ref:
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) Amendment 5 §결정 15 — 3-way version atomic invariant (본 Amendment 4 sibling carrier, boundary disjoint: ADR-063 = 3-way invariant 영역 / 본 Amendment 4 = consumer adoption protocol schema detection 영역)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` v1.5 §4.8 `version_handshake_3way_binding` — fallback semantic + orthogonality invariant SSOT (§결정 8.B verbatim cross-ref)
- `docs/project-config-schema.md` `codeforge.version_pin` block — schema 정의 SSOT (본 Amendment 4 동반 MINOR — `updated: 2026-05-17`)
- [ADR-066](ADR-066-pat-rotation-policy.md) §결정 2 — `marketplace contents:read` reuse (3-way lint read-only, Amendment 3 write scope 미사용 — 추가 PAT grant 0)
- [ADR-064](ADR-064-decision-principle-mandate.md) §self-application — Amendment 4 = consumer adoption scope 확장 강화 방향 only (weakening 0)
- `docs/consumer-guide.md` §2g.N — consumer pin setup runbook (Phase 2 carrier)

## Amendment 5 — consumer adoption 시 Issue Forms enumeration 정정 + D4 marker form-level wrap cross-ref (CFP-821)

**Effective**: 2026-05-17 (CFP-699 Wave 3 Story-7 Phase 1 PR merged 시점).

**Carrier**: CFP-821 (Wave 3 Story-7 — coverage fan-out D1+D2+D3). Parent Epic CFP-699 (선언적 reconciliation 기반 codeforge upgrade flow). Sibling carrier: ADR-076 §결정 2 표 PR template row append (Amendment 아닌 표 1행 additive — Issue templates row 동형) + reconcile-protocol-v1 v1.6 §4.3 (h) trigger + §4.9 `coverage_fan_out_implementation_binding` block.

**번호 정정 (설계 lane strict-verify)**: 본 Amendment = **Amendment 5 §결정 9** (Story §1-§6 RequirementsPL synthesis 1차 view 의 'Amendment 4' = frontmatter 미검증 hypothesis — 설계 lane strict-verify origin/main direct Read 결과 **CFP-820 (Wave 3 Story-6) 이 Amendment 4 / §결정 8 점유** → 본 Story-7 = Amendment 5 §결정 9 정정. 동반 reconcile-protocol-v1 version = **v1.6 §4.3 (h)** (Story-7 §3.5 1차 view 'v1.5 §4.3 (h)' = CFP-820 이 v1.5 §4.3 (e) 점유 collision → v1.6 §4.3 (h) 정정). Codex TP#2 verify-before-trust 8-mirror 교훈 + CFP-820 §4.3 (e) "Amendment 번호 정정" 패턴 verbatim 답습 — fact 영향 0, 추적성/번호 정정만 (ADR-068 I-4 wording SSOT 정합).

본 ADR §결정 1 (bootstrap 검증 책임 = wrapper plugin overlay/hooks/) + §결정 5 (consumer-guide.md SSOT) + §결정 7 (Amendment 3 D4 marker syntax) 정합. ADR-076 §결정 2 9 영역 enumeration 표가 wrapper SSOT desired state 단위를 정의 → 본 Story-7 D1 = Issue/PR template fan-out 으로 §결정 1 line 84 의 systemic enumeration gap (`3종 (audit + bug + story)` ↔ reality audit + bug 2종 only, story 부재) 를 정정 + D4 marker (Amendment 3 §결정 7.A.1) 의 신설 form 적용 cross-ref. 본 amendment = ADR-027 §결정 추가 (additive, supersede 아님). §결정 9 신설.

**ADR collision 회피 (신규 ADR 아닌 Amendment — CFP-821 Story §3.1.2 판정 정합)**: ADR-027 = consumer adoption protocol SSOT — `.github/ISSUE_TEMPLATE/` sync enumeration (§결정 1) + D4 marker syntax (Amendment 3 §결정 7) 이 이미 consumer-side template adoption 의 carrier. Issue Forms enumeration 정정 + D4 marker form-level wrap = ADR-027 §결정 1 + Amendment 3 §결정 7.A.1 의 동형 영역 확장 → 신규 ADR 신설 시 consumer adoption 영역 SSOT 분산. Amendment = ADR-064 top-down ratchet 강화 방향 only (consumer adoption scope 확장 — Issue Forms 3종 → 5 forms + config.yml + D4 marker 신설 form 적용).

### 결정 9 — consumer adoption 시 Issue Forms enumeration 정정 + D4 marker form-level wrap (normative SSOT)

#### §결정 9.A — Issue Forms enumeration 정정 (§결정 1 line 84 systemic gap 해소)

§결정 1 line 84 의 `consumer .github/ISSUE_TEMPLATE/ 3종 (audit + bug + story) sync` = systemic enumeration gap (실제 origin/main `.github/ISSUE_TEMPLATE/` = audit.yml + bug.yml 2종 only, story 부재). D1 fan-out 후 정식 enumeration:

| Form | 역할 | SSOT location (Phase 2 carrier) |
|---|---|---|
| `audit.yml` | audit Issue Form (기존 — SSOT 승격) | `templates/.github/ISSUE_TEMPLATE/audit.yml` |
| `bug.yml` | bug Issue Form (기존 — SSOT 승격) | `templates/.github/ISSUE_TEMPLATE/bug.yml` |
| `story.yml` | Story Issue Form (신설) | `templates/.github/ISSUE_TEMPLATE/story.yml` |
| `discussion.yml` | Discussion Issue Form (신설) | `templates/.github/ISSUE_TEMPLATE/discussion.yml` |
| `codeforge-improvement.yml` | codeforge-improvement Issue Form (신설) | `templates/.github/ISSUE_TEMPLATE/codeforge-improvement.yml` |
| `config.yml` | Issue selector controller (`blank_issues_enabled` + `contact_links[]`, form 아님) | `templates/.github/ISSUE_TEMPLATE/config.yml` |
| `PULL_REQUEST_TEMPLATE.md` | PR template (현 `.github/` byte-identical mirror — consumer-distributable SSOT) | `templates/.github/PULL_REQUEST_TEMPLATE.md` |

prior art = microsoft/TypeScript 5 forms + config.yml 패턴 (정합도 최고). `templates/.github/` = consumer-distributable SSOT 신설 영역 (현 `.github/` = wrapper self-app, ADR-005 byte-identical). **본 §결정 9.A = declarative enumeration 정정 (normative SSOT)** — 실 file 신설 = Phase 2 carrier (구현 lane, §결정 9.E).

#### §결정 9.B — D4 marker form-level wrap (Amendment 3 §결정 7.A.1 신설 form 적용)

신설 `templates/.github/ISSUE_TEMPLATE/*.yml` + `PULL_REQUEST_TEMPLATE.md` 의 D4 customization marker 적용 = **form 전체 wrap** (Amendment 3 §결정 7.A.1 comment prefix per-filetype + §결정 7.D.3 whole-line anchored + §결정 7.D.1 flat-only 정합):

- `.yml` Issue Form / config.yml = `# BEGIN wrapper-managed` / `# END wrapper-managed` (form 전체를 marker block 으로 wrap — body[] sub-block partial marker 금지)
- `.md` PR template = `<!-- BEGIN wrapper-managed -->` / `<!-- END wrapper-managed -->`
- marker 안 = wrapper SSOT desired state / 밖 = consumer customization preserve (Amendment 3 §결정 7.B verbatim)

**결정 근거 (Axis — form-level wrap vs body[] partial)**: Issue Form yaml = structured spec — body[] sub-block 안 partial marker 는 yaml structure 파편화 risk + GitHub Issue Form parser 가 `#` 주석 무시 → form 전체 wrap 이 의미 정합 (Amendment 3 §결정 7.D.1 nesting 금지 flat-only + Ansible blockinfile flat 패턴 동형). consumer customization = D4 marker 밖 별도 form 추가 또는 marker 부재 form (Amendment 3 §결정 7.C `wholesale_mirror_with_user_visible_loss_report` 재사용 — D1 first-reconcile silent overwrite 0, EPIC-AC-4 보존).

#### §결정 9.C — D1 reconcile = reconcile-protocol-v1 §4.7 SSOT 재사용 (재구현 0)

D1 `.github/` 영역 consumer reconcile = reconcile-protocol-v1 v1.4 §4.7 `overlay_reconcile_implementation_binding` (marker-aware 2-way / `wholesale_mirror_with_user_visible_loss_report`) SSOT 재사용 — `.github/` 영역 area handler 추가 (algorithm 재구현 0, path 매핑만 신규). reconcile-protocol-v1 v1.6 §4.9 `coverage_fan_out_implementation_binding.d1_issue_pr_template_fan_out.reconcile_reuse` verbatim cross-ref. consumer (예: mctrader 5 repo) `.github/ISSUE_TEMPLATE/` marker 부재 시 first-reconcile = wholesale mirror + loss report (silent overwrite 0).

#### §결정 9.D — D2 branch protection FORM (b) + ADR-066 무변경 (F-P1-A 해소, cross-ref)

D2 = `templates/scripts/setup-branch-protection.sh` FORM (b) (manifest 합성 + dry-run preview only, gh api PUT = 0 — 실 등록 = consumer admin operator manual OOS). GitHub API write 자체 0 → fine-grained PAT `Administration:write` 불요 → **ADR-066 §결정 2 scope 5종 무변경 (ADR-066 무접촉)**. Codex TP#4 F-P1-A (D2 credential gap, P1 hidden-assumption) 해소 = scope-down OOS = least-privilege ratchet-safe (ADR-064 minimal-change). 본 §결정 9 = D1 Issue Forms enumeration carrier 가 primary — D2 FORM (b) ADR-066 무변경 = cross-ref only (reconcile-protocol-v1 v1.6 §4.9 `d2_branch_protection_setup_helper` SSOT, ADR-066 별도 entry 미추가).

#### §결정 9.E — Phase split (Phase 1 = declarative SSOT / Phase 2 = 구현 lane)

Phase 1 (CFP-821 본 PR) = declarative SSOT mandate (본 §결정 9 + ADR-076 §결정 2 표 PR template row + reconcile-protocol-v1 v1.6 §4.3 (h)/§4.9 + MANIFEST.yaml row + change-plan + Story §3.1/§7/§11 미러링 — pure design-SSOT, template/script/doc 실 file 0건, CFP-743/744/745/820 선례 정합). Phase 2 (별 PR, 구현 lane) = `templates/.github/ISSUE_TEMPLATE/*.yml` 5종 + `config.yml` + `templates/.github/PULL_REQUEST_TEMPLATE.md` 실 file + `.github/` byte-identical self-app + `templates/scripts/setup-branch-protection.sh` (FORM (b)) + `docs/script-boundary.md` + `docs/consumer-guide.md` §2 line 472/814 enumeration 정정 + §N D2 operator manual 절차 + reconcile-overlay.sh `.github/` area handler 실 연계.

#### §결정 9.F — mechanical enforcement (중복 codification 회피)

본 §결정 9 = consumer adoption protocol enumeration 정정 + D4 marker form-level wrap declarative mandate. D4 marker mechanical lint = Amendment 3 §결정 7.D `wrapper-managed-block` evidence-check entry (blocking-on-pr tier, frontmatter `mechanical_enforcement_actions[]` 이미 등재) 가 cover (신설 form 도 동일 lint 적용). 본 Amendment 5 측 별도 mechanical action 신설은 **중복 codification 회피** (ADR-065 §결정 5 "cross-ref only" 정합) — ADR-027 frontmatter `mechanical_enforcement_actions[]` = Amendment 2/3 entry 보존, Amendment 5 별도 entry 미추가 (Amendment 3 §결정 7.D `wrapper-managed-block` entry 가 D4 marker SSOT). D3 script boundary mechanical lint = §3.3 OOS 별도 follow-up Issue (codeforge-improvement (k) bash top-level local lint — ADR-064 minimal-change, Story scope creep 회피).

### 해소 기준 정합

ADR-027 frontmatter `is_transitional: false` (permanent policy, 기존 §"해소 기준" = "N/A — permanent policy" verbatim). Amendment 5 = consumer adoption 시 Issue Forms enumeration 정정 (3종 → 5 forms + config.yml) + D4 marker form-level wrap cross-ref = governance 강화 방향 ratchet — ADR-058 §결정 5 sunset_justification 불요 (강화 방향, ADR-064 top-down self-application 정합 — consumer adoption scope 확장 only, weakening 0).

상세 Change Plan: `codeforge-internal-docs/wrapper/change-plans/cfp-821-coverage-fan-out.md`.

Cross-ref:
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) §결정 2 — Wrapper SSOT 영역 enumeration scheme (본 Amendment 5 sibling carrier: ADR-076 §결정 2 표 PR template row append 동반 — Issue templates row 동형 `template export — consumer overlay 시점 byte-identical mirror`)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` v1.6 §4.9 `coverage_fan_out_implementation_binding` — D1/D2/D3 fan-out binding SSOT (§결정 9.A-9.D verbatim cross-ref)
- ADR-027 Amendment 3 §결정 7.A.1 / 7.B / 7.C / 7.D.1 / 7.D.3 — D4 marker syntax (본 Amendment 5 §결정 9.B 가 신설 form 에 적용 — comment prefix per-filetype + whole-line anchored + flat-only)
- [ADR-066](ADR-066-pat-rotation-policy.md) §결정 2 — scope 5종 무변경 (D2 FORM (b) — Administration:write grant 0, F-P1-A 해소 = scope-down OOS, 본 Amendment 5 = ADR-066 무접촉 cross-ref only)
- [ADR-024](ADR-024-story-scoped-branch-policy.md) Amendment 2 §결정 A·C — branch-protection-manifest SSOT (D2 setup-branch-protection.sh = §결정 C 운영 규칙 mechanical helper, ADR-024 Amendment 6 회피 — 본문 무변경)
- [ADR-005](ADR-005-plugin-self-application-na-standardization.md) — `templates/.github/*` ↔ `.github/*` byte-identical self-app (D1 Phase 2)
- [ADR-064](ADR-064-decision-principle-mandate.md) §self-application — Amendment 5 = consumer adoption scope 확장 강화 방향 only (신규 ADR 회피 + D2 scope-down least-privilege ratchet-safe, weakening 0)
- `docs/consumer-guide.md` §2 line 472/814 enumeration 정정 + §N D2 operator manual — consumer runbook (Phase 2 carrier)
