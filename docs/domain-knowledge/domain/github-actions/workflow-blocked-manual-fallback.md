---
kind: domain-knowledge
domain: github-actions
title: Workflow Action 차단 환경 manual fallback path — recovery runbook
introduced_by: CFP-658
related_adrs:
  - ADR-027  # Amendment 2 carrier
  - ADR-032  # Amendment 1 strict-eligible 4종
  - ADR-036  # KEY atomic invariant
  - ADR-039  # subagent default
  - ADR-061  # Python script writing convention (bash 인접 변형)
  - ADR-066  # PAT rotation policy
related_files:
  - templates/scripts/manual-story-init-fallback.sh  # Phase 2 carrier
  - templates/scripts/manual-story-init-fallback.ps1  # Phase 2 carrier
  - templates/github-workflows/story-init.yml  # L107-124 existence_check verbatim port source
  - templates/github-workflows/section-1-verbatim-postmerge.yml  # Phase 2 carrier
  - docs/consumer-guide.md  # consumer runbook
  - docs/orchestrator-playbook.md  # Orchestrator detection 절차
date: 2026-05-14
---

# Workflow Action 차단 환경 manual fallback path — recovery runbook

본 페이지 = `default_workflow_permissions: read` 차단 환경 또는 일반 Action failure 시 codeforge 의무 사용을 위한 manual fallback path SSOT. ADR-027 Amendment 2 §결정 6 의 implementation guide.

## 컨텍스트

### Enterprise org-level workflow permission cap

GitHub Enterprise org 의 admin policy 가 `default_workflow_permissions: read` 로 cap 설정 시 — workflow `GITHUB_TOKEN` 이 `contents:write` / `issues:write` / `pull-requests:write` 권한을 갖지 못한다. job-level `permissions:` 명시도 org cap 초과 불가.

이 환경에서는 codeforge 의 6 핵심 workflow (`story-init.yml` / `phase-label-invariant.yml` / `subissue-from-impl-manifest.yml` / `phase-gate-mergeable.yml` / `fix-ledger-sync.yml` / `post-merge-followup.yml`) 전체가 silent skip — codeforge 의무 사용 (ADR-027) 과 consumer workaround 금지 (ADR-039 inline whitelist) 사이 의무 충돌 발생.

### Researcher 위험 1 — Trigger detection asymmetry (silent failure)

workflow 의 comment 작성 자체가 fail = silent failure. Action tab 의 conclusion 만으로 fallback 진입 trigger 를 자동 감지 불가 — 사용자 / Orchestrator 의 수동 확인 의존 = unreliable trigger.

→ **Outage detection (workflow conclusion + N분 timeout) 폐기 사유**. ADR-027 Amendment 2 §결정 6.A 는 (B) Outage detection 후보 폐기 후 (A) Declarative + (C) Explicit ad-hoc hybrid 채택.

### Researcher 위험 2 — Manual write 가 governance ratchet 약화 vector

manual write 영역 ↔ governance ratchet 충돌 영역:
- §1 immutable invariant (`story-section-1-immutable.yml`) — manual fallback 시 §1 변조 가능
- `phase-label-invariant.yml` — phase 전이 자동 검증 우회 가능
- 4 required check (branch protection) — admin override 가능성

ADR-073 verify-before-assert + Codex Touchpoint #2 mandatory (ADR-052 Amendment 4) + post-merge lint `section-1-verbatim-postmerge.yml` (Phase 2 carrier) 3 layer 로 보강.

## Fallback trigger 정의 — (A) + (C) hybrid

### Option (A) Declarative — environment default

`.claude/_overlay/project.yaml` 에 `bootstrap.fallback_mode: action_blocked` enable:

```yaml
bootstrap:
  fallback_mode: action_blocked  # default: auto
```

영구 차단 환경 (enterprise admin policy disable) default. Orchestrator 가 매 Story spawn 시 본 flag 검증 — true 시 자동 manual fallback path 활성.

### Option (C) Explicit ad-hoc — per-Issue override

Issue 발의자 또는 Orchestrator 가 `fallback:manual` label 부착. environment default 와 무관 fallback path 활성.

per-Issue override (일시 outage / 사용자 explicit 선택).

### 우선순위 (C) > (A)

per-Issue 명시 의지 > environment default. (A) 활성 환경에서도 (C) label 없는 Issue 는 정상 workflow 시도 후 fail 시 사용자 escalate.

### Option (B) Outage detection 폐기

workflow run conclusion + N분 timeout 후보 = **폐기**. Researcher 위험 1 (silent failure) 차단 — workflow comment 작성 자체 fail 시 detection 불가.

## Manual fallback path 절차

### Step 1 — Trigger 감지

| Trigger | 감지 방법 |
|---|---|
| (A) Declarative | Orchestrator 가 `.claude/_overlay/project.yaml` Read 시 `bootstrap.fallback_mode == "action_blocked"` 확인 |
| (C) Explicit | Issue 에 `fallback:manual` label 부착 |

### Step 2 — RequirementsPLAgent spawn (skip 가능 영역)

mctrader-hub MCT-135 evidence 패턴 (brainstorm Phase 0 4-agent burst 합성 spec 이 §3-6 SSOT 대체) 시 RequirementsPL skip 가능. ADR-064 §결정 3 룰 1 (derived default) 정합.

spawn 시 Issue body §1 verbatim copy + §2-§7 author.

### Step 3 — `manual-story-init-fallback.sh` 호출

`templates/scripts/manual-story-init-fallback.sh` (Phase 2 carrier) — bash one-liner 로 §1 verbatim copy + §2-§11 placeholder + branch create + PR open 자동 수행:

```bash
bash templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>
```

내부 step:
1. Issue body fetch (`gh issue view <ISSUE_NUMBER> --json body`)
2. §1 verbatim extract (shell injection 차단 — `printf '%s'` + heredoc single-quoted, ADR-061 정합)
3. `KEY = PREFIX-${ISSUE_NUMBER}` 발급 (ADR-036)
4. Existence check (story-init.yml L107-124 verbatim port)
5. Story file write (§1 verbatim + §2-§11 placeholder)
6. Branch create + commit + push
7. PR open (`gh pr create`)

Windows 환경은 `.ps1` parity (Phase 2 carrier).

### Step 4 — ArchitectPLAgent Phase 1 PR manual open

ArchitectPLAgent 가 Phase 1 PR manual `gh pr create` 책임. Codex Touchpoint #2 dispatch (ADR-052 Amendment 4 mandatory) — `artifacts` 필드 verbatim attach (ADR-070).

### Step 5 — Orchestrator phase label 수동 부착

`codeforge:lane-self-write-boundary` skill 정합 — manual fallback path 에서도 lane plugin owner path 준수. phase label 수동 전이 + Story §14 Lane Evidence row append (ADR-031).

### Step 6 — Trigger (C) ad-hoc PR description checklist mirror

`fallback:manual` label 부착 PR description 에 checklist 의무 (silent failure detection):

```markdown
## Manual fallback checklist
- [ ] Issue body §1 verbatim copy (byte-identical 검증)
- [ ] KEY = PREFIX-${ISSUE_NUMBER} (ADR-036 atomic)
- [ ] Branch existence_check (`gh api repos/<owner>/<repo>/branches/<branch>`)
- [ ] PR opened via `gh pr create`
- [ ] phase:요구사항 label 부착
- [ ] `fallback:manual` label 부착
```

### Step 7 — 4 required check 통과 의무

manual PR 도 phase-gate-mergeable + doc frontmatter + doc section + invariant-check 통과 의무. `enforce_admins: true` ratchet 유지 (CFP-70) — admin override 차단.

## 보안 + 운영 리스크 mitigation 통합

### Governance ratchet 약화 mitigation 3종 (SecurityArch T1/T2/T3)

| Invariant | Mitigation | Tier |
|---|---|---|
| §1 verbatim immutable | `section-1-verbatim-postmerge.yml` (Phase 2) warning tier | ADR-060 framework |
| phase-label transition | Orchestrator 수동 의무 | governance |
| 4 required check | manual PR 도 통과 의무 (enforce_admins:true) | blocking |

### Shell injection 차단 (SecurityArch 조건 3)

Issue body parse 시 shell injection 차단 — `manual-story-init-fallback.sh` 안 `printf '%s'` + heredoc single-quoted 의무 (ADR-061 정합):

```bash
ISSUE_BODY=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body')
SECTION_1=$(printf '%s' "$ISSUE_BODY" | awk '/^## 1\./,/^## 2\./' | head -n -1)
cat > "docs/stories/${KEY}.md" <<'STORY_EOF'
${SECTION_1}
STORY_EOF
```

### 2-PAT namespace 분리 (OpRiskArch 조건 2)

| PAT name | Scope | 용도 |
|---|---|---|
| `CODEFORGE_CROSS_REPO_PAT` (기존) | repo + read:org | phase-gate-mergeable.yml + rate-limit-fallback-kpi.yml |
| `CODEFORGE_FALLBACK_PAT` (신설) | repo only | manual fallback path 전용 |

`write:packages` / `admin:*` 금지. ADR-066 90 days rotation 정합 — `docs/security/pat-rotation-log.md` audit entry 의무.

### Burst control + rate-limit (OpRiskArch 조건 4)

- Primary rate limit: 5000 req/hr (`[empirical-source: GitHub REST API documentation — vendor doc explicit guarantee]`)
- Secondary rate limit: content-creation per minute (burst 시 503/429, `[empirical-source: GitHub REST API documentation — vendor doc]`)

`manual-story-init-fallback.sh` 안 exponential backoff:
- 1차 retry: 1s 대기
- 2차 retry: 2s 대기
- 3차 retry: 4s 대기
- 초과: silent skip + `fallback:rate-limited` label 부착

## 멱등성 (DataMigrationArch 조건 — story-init.yml L107-124 verbatim port)

`templates/github-workflows/story-init.yml` L107-124 의 `existence_check` step (CFP-280 Iter 1 FIX, `gh api repos/<owner>/<repo>/branches/<branch>` atomic) 을 `manual-story-init-fallback.sh` 에 verbatim port.

### Edge case 4종

- **Edge-1 (멱등성)**: branch + PR existence check (`git ls-remote --heads origin feat/<KEY>-<SLUG>` + `gh pr list --head feat/<KEY>-<SLUG>`)
- **Edge-2 (병렬 fallback)**: 동시 동일 Issue manual fallback 시 원격 branch 존재 검사 (story-init.yml 의 `Skip if first firing already published` step verbatim port)
- **Edge-3 (governance ratchet 우회 시도)**: §1 변조 → `section-1-verbatim-postmerge.yml` warning lint audit comment 자동 발의 (hard block 아님)
- **Edge-4 (KEY 미확정 시도)**: brainstorming 시점 KEY 사전 추측 → ADR-036 위반 차단. 반드시 `cfp-reserve.yml` Issue 발의 후 발급된 Issue # 사용 의무

## consumer-guide ↔ playbook 분리

- **consumer-guide** (`docs/consumer-guide.md` §"Action 차단 환경 fallback"): consumer 가 따라할 runbook (project.yaml 설정 + manual-story-init-fallback.sh 호출 + 4 required check 통과)
- **playbook** (`docs/orchestrator-playbook.md` §"fallback decision tree"): Orchestrator 가 매 lane spawn 직전 따르는 detection + phase 수동 transition 절차

본 페이지 = 양쪽의 evidence + recovery runbook SSOT.

## Sunset criteria (ADR-058 §결정 5)

본 fallback path 는 **permanent policy** — ADR-027 Amendment 2 자체는 `is_transitional: false` (안전망 ADR 아님, normative SSOT 단일 위치 영구).

단 `section-1-verbatim-postmerge.yml` warning tier entry 는 `is_transitional: true` (ADR-060 framework 정합):
- **metric**: warning 발화 0회 누적 + manual fallback PR 누적 ≥ 20 + bypass 외 failure = 0 → `blocking-on-pr` 승격 검토 별 CFP
- **who**: PMOAgent retro audit
- **how**: monthly KPI dashboard (rate-limit-fallback.json 패턴 precedent)
