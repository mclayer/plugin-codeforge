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
mechanical_enforcement_actions:
  - action_name: section-1-verbatim-postmerge
    decision_binding: "Amendment 2 §결정 6.A — manual fallback path 의 §1 verbatim invariant post-merge lint (warning tier)"
    evidence_registry_entry: section-1-verbatim-postmerge  # docs/evidence-checks-registry.yaml row
    bypass_label: hotfix-bypass:section-1-verbatim-postmerge
    carrier_cfp: CFP-658  # Phase 1 = SSOT 등재, Phase 2 = workflow + script 신설
    introduced_by_amendment: 2
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
- consumer `.github/ISSUE_TEMPLATE/` 3종 (audit + bug + story) sync
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
- 1차 retry: 1s 대기
- 2차 retry: 2s 대기
- 3차 retry: 4s 대기
- 초과: silent skip + `fallback:rate-limited` label 부착

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
