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
  - tests/workflows/test_post-merge-followup-yml.sh                            # Amendment 1 — Phase 2 PR scope
  - tests/fixtures/post-merge-followup/                                        # Amendment 1 — 12 fixture
  - docs/orchestrator-playbook.md
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md
  - docs/adr/ADR-011-inter-plugin-contract-drift-detection.md
related_stories:
  - CFP-74
  - CFP-476   # Amendment 1 carrier — PR-Issue close trigger algorithm + line 47 stale 정정 + byte-identity invariant §결정 5.B
amendment_log:
  - date: 2026-05-12
    carrier: CFP-476
    section: "§결정 5 (신설) + §결정 1 (line 47 inline 정정)"
    summary: "PR-Issue close trigger algorithm 정식화 — dual-source AND (PR body close keyword regex ∩ Issue closedByPullRequestsReferences) + terminal-phase gate (phase:보안-테스트 / phase:구현-테스트 consumer config 분기) + multi-issue audit (single carrier + skip + [multi-match-skip] marker) + cross-repo qualified syntax skip + security T1/T2 env indirection + byte-identity invariant (§결정 5.B). 결정 1 line 47 stale terminal phase (phase:완료) → phase:보안-테스트 default / phase:구현-테스트 (lanes.security_ai: false) 정정. CFP-391 / CFP-412 / CFP-455 false-positive close 3-Story 누적 패턴 차단."
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
- I.a / I.b / I.c / I.d 각각 별 PR 분리
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

추가 보안 발견 (SecurityArch deputy, CFP-476): line 41 `PR_TITLE='${{ github.event.pull_request.title }}'` 및 Action 3 본체 inline `${{ ... }}` shell 삽입 — **T1 CRITICAL** PR body shell injection + **T2 HIGH** PR_TITLE single-quote escape 가능. env indirection (`env: PR_BODY: ${{ ... }}` + `"$PR_BODY"`) 마이그레이션 의무.

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

### 결정 1 (line 47 inline 정정)

본 Amendment 1 §결정 5.A terminal-phase gate 와 정합. 본문 결정 1 step 3 `phase:완료` stale → `terminal phase 도달 시` 정정 (playbook line 228 SSOT 정합). frontmatter `amendment_log[]` row 1 verbatim cross-ref.

## 관련 ADR

- **ADR-022** §결정 1 User Override hierarchy: workflow 가 merge 결정 안 함, follow-up 만 (사용자 admin merge 결정 보존)
- **ADR-022** §결정 11 Phase 1 trust model: telemetry only, no enforcement hook
- **ADR-024** story-scoped branch policy: cfp-74 branch + Phase 1 PR 분리 정합. internal-docs 측 cross-repo write 도 branch + PR (1 PR 통합 거부 정합)
- **ADR-025** §결정 1: Sonnet pick=alpha 자동 진행 정합
- **ADR-001** review-agent-unification: review separation 변경 없음
- **ADR-008** SemVer: post-merge-counters.jsonl v1.0 = additive minor 가능
- **ADR-011** cross-repo PAT: CFP-71 precedent 정합
- **ADR-045 / CFP-138 Phase 1 follow-up** (2026-05-09): post-merge-telemetry.sh 의 Contents API SHA-based optimistic concurrency pattern 이 [`docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md`](../domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md) Pattern A 로 SSOT 화. retro-attempts.jsonl (ADR-045) 도 동일 Pattern A 의무. 본 ADR-026 implementation (post-merge-telemetry.sh) 는 이미 Pattern A 정합 — 본문 변경 0 (cross-ref only).
