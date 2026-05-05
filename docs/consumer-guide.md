# Consumer Guide — 플러그인 적용 가이드

이 플러그인(`codeforge`)을 consumer 프로젝트에서 사용하는 방법.

## 0. 사전 요구사항

- **GitHub Team plan** (Sub-issues, Projects v2, CODEOWNERS, Branch protection 사용)
- 권한: GitHub repo admin (Branch protection·CODEOWNERS·Actions 설정)
- gh CLI 설치 + 인증 (`gh auth login`)

## 1. 설치

### 1a. 플러그인 설치 (marketplace 경유)

```bash
/plugins install codeforge@<marketplace>
/plugins install github@claude-plugins-official
/plugins install codex@openai-codex
/plugins install superpowers@claude-plugins-official
/plugins install claude-md-management@claude-plugins-official
```

또는 로컬 경로 설치(개발 중인 플러그인 테스트 시):

```bash
/plugins install /path/to/codeforge-repo
```

설치 확인:

```bash
ls ~/.claude/plugins/cache/<marketplace>/codeforge/<version>/agents/
# ArchitectAgent.md  DeveloperAgent.md  ...
```

### 1b. 필수 의존성

`CLAUDE.md` §"세션 개시 의무"에 명시. 미설치 시 플러그인 동작 불가:

- **MCP**: `github` 인증 완료 (`/mcp` 인증)
- **플러그인 4종**: `codex@openai-codex`, `superpowers@claude-plugins-official`, `claude-md-management@claude-plugins-official`, `github@claude-plugins-official`
- **CLI 2종**: `codex`, `gh` (`gh auth login` 인증)

### 1c. 권장 플러그인 (선택)
- `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

## 2. Consumer 프로젝트 구조 초기화

```
<consumer-project>/
├── .claude/
│   ├── _overlay/                       # 프로젝트 특화 overlay (편집 대상)
│   │   ├── project.yaml                # GitHub·labels structured 상수
│   │   ├── CLAUDE.md                   # 프로젝트 narrative
│   │   └── agents/
│   │       ├── DomainAgent.md          # 도메인 전문가 특화
│   │       ├── DataEngineerAgent.md    # 데이터 계층 특화
│   │       └── ...                     # 필요한 에이전트만
│   ├── agents/                         # GENERATED (hook 산출물, gitignore)
│   ├── settings.json                   # SessionStart hook 등록
│   └── settings.local.json             # (선택) 로컬 오버라이드
├── .github/
│   ├── workflows/                      # Plugin 워크플로우 7종 consumer-distributable (수동 cp, CFP-94)
│   ├── ISSUE_TEMPLATE/                 # Plugin Issue Forms 3종 (audit + bug + story) + config.yml
│   ├── PULL_REQUEST_TEMPLATE.md        # Plugin PR template
│   └── CODEOWNERS                      # architect/domain-expert team 매핑
├── docs/
│   ├── stories/                        # GENERATED (story-init.yml Action 산출 — CFP-65 F2 Phase 1 복원)
│   ├── adr/                            # ADR markdown (ArchitectAgent direct write)
│   ├── change-plans/                   # Architect Change Plan (ArchitectAgent direct write)
│   └── domain-knowledge/               # Domain KB (계층, DomainAgent direct write)
├── CLAUDE.md                           # GENERATED (hook 산출물, gitignore 또는 commit)
├── .claude-work/                       # consumer overlay scratch (gitignore)
└── ...
```

### 2a. 초기 복사

```bash
# consumer project root에서
mkdir -p .claude/_overlay/agents
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/README.md .claude/_overlay/
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example .claude/_overlay/project.yaml

# TestAgent가 호출할 wrapper 2종 (consumer가 러너 명령 결정)
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/run-tests.sh.example .claude/_overlay/run-tests.sh
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/run-perf.sh.example .claude/_overlay/run-perf.sh
chmod +x .claude/_overlay/run-tests.sh .claude/_overlay/run-perf.sh
# editor에서 pytest 부분을 프로젝트 러너로 교체 (vitest / go test / cargo test / jest / k6 등)
```

### 2b. `.claude/settings.json` 설정 (SessionStart hook 등록)

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

### 2c. GitHub repo 셋업 (Plugin 권장 워크플로우 + Forms + CODEOWNERS)

```bash
# Workflow 7개 복사 (consumer-distributable):
#   phase-gate-mergeable + phase-label-invariant + story-init + story-section-1-immutable
#   + fix-ledger-sync + subissue-from-impl-manifest + story-section-schema (CFP-94)
mkdir -p .github/workflows
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/

# CFP-97 + CFP-109 + CFP-110: consumer-distributable scripts manifest-driven copy.
# Manifest format: <script-path>[:<dependent-workflow-path>]
# (CFP-109 — workflow path optional, used by SessionStart Check 4 for degraded suppression).
#
# CFP-110: SessionStart hook (regen-agents.sh) 가 매 세션 시 자동 install (cp -n no-clobber)
# — 본 manual loop 는 fallback (hook 미작동 / 첫 install 전 / opt-out 시).
# Plugin update 시 신규 manifest entry 는 자동 propagate.
while IFS= read -r line; do
    # trim leading/trailing whitespace
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    case "$line" in '#'*|'') continue ;; esac
    # CFP-109: parse script-path before optional `:<workflow>` suffix
    script_path="${line%%:*}"
    # path traversal guard (CFP-97 P1 + CFP-112 leading-dash) — applied to script_path only
    case "$script_path" in
        /*) echo "manifest absolute-path entry rejected: $line" >&2; continue ;;
        *..*) echo "manifest traversal entry rejected: $line" >&2; continue ;;
        -*) echo "manifest leading-dash entry rejected: $line" >&2; continue ;;
    esac
    mkdir -p "$(dirname "$script_path")"
    cp "${CLAUDE_PLUGIN_ROOT}/codeforge/${script_path}" "${script_path}"
    chmod +x "${script_path}"
done < "${CLAUDE_PLUGIN_ROOT}/codeforge/templates/consumer-scripts.manifest"

# Issue Forms 3개 복사 (audit + bug + story)
mkdir -p .github/ISSUE_TEMPLATE
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-issue-forms/*.yml .github/ISSUE_TEMPLATE/

# blank issue 비활성화 (Forms만 강제)
cat > .github/ISSUE_TEMPLATE/config.yml <<EOF
blank_issues_enabled: false
EOF

# PR template 복사
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-pr-template.md .github/PULL_REQUEST_TEMPLATE.md

# CODEOWNERS 복사 + team placeholder 치환
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/CODEOWNERS.template .github/CODEOWNERS
# editor에서 @ORG/ARCHITECT_TEAM, @ORG/DOMAIN_EXPERT_TEAM을 자기 organization team으로 치환
```

#### Path A (default — full distribution) vs Path B (degraded distribution) (CFP-86)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-6 finding: 위 7 workflow (CFP-94 후 — 6 → 7) 모두 복사가 default 이나 (Path A), 실제 mctrader-hub 는 **2 workflow 만 보유 (Path B)**. SSOT 미문서화 → invariant 보장 기대치 mismatch.

**Path A (full)**: 7 workflow 모두 보유 — 모든 invariant 자동 enforce.
**Path B (degraded)**: 일부 workflow 부재 — manual compensating check 의무.

##### Workflow 별 invariant 영향

| Workflow | 부재 시 lost invariant | Manual compensating check (Path B) |
|---|---|---|
| `story-init.yml` | Issue Form → Story file + Phase 1 PR 자동 생성 | `gh issue create` 수동 + `docs/stories/<KEY>.md` 수동 작성 + Phase 1 PR 수동 open |
| `phase-label-invariant.yml` | single-active phase label enforce | PR review 시 phase label 1개만 boolean check (script 또는 manual) |
| `phase-gate-mergeable.yml` | phase gate ↔ PR mergeable status | PR merge 직전 phase 라벨 + gate 라벨 manual verify |
| `story-section-1-immutable.yml` | §1 변조 금지 | PR diff 의 `## §1` line range manual review |
| `fix-ledger-sync.yml` | §10 row append → Issue label mirror + comment | §10 row 추가 commit 시 수동 `[FIX #N]` Issue comment + `fix:<lane>-retry` label 부착 |
| `subissue-from-impl-manifest.yml` | §8.5 Impl Manifest → file-level sub-issue 자동 생성 | §8.5 commit 후 수동 `gh sub-issue create` per file |
| `story-section-schema.yml` (CFP-94) | Story file §1-§13 schema lint (Implementation strict + Epic condensed) | PR review 시 수동 section schema 검증 또는 `bash scripts/check-story-section-schema.sh` 로컬 실행 (CFP-97 manifest 경유 copy) |

**mctrader-hub 현재 상태 (2026-05-04 audit)**:
- ✅ `phase-gate-mergeable.yml`
- ✅ `phase-label-invariant.yml`
- ❌ 4 workflow 부재 (Path B 운영 중) — 수동 compensating check 가 자율적

##### Path A ↔ Path B cutover 절차

**Path A → Path B (degrade)**:
1. 부재할 workflow yml 명시 (PR description 에 reason)
2. 본 §2c 표 의 manual compensating check 활성화
3. consumer overlay `.claude/_overlay/project.yaml` 의 `workflow_distribution: full | degraded` field 갱신 (CFP-86 Phase 2 — 별도 follow-up CFP)

**Path B → Path A (upgrade)**:
1. `cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<missing>.yml .github/workflows/`
2. (CFP-97) `<missing>.yml` 가 의존 script 보유 시 (예: `story-section-schema.yml` ↔ `scripts/check-story-section-schema.sh`) §2c manifest-driven loop 동시 실행
3. CI 가 신규 invariant 발견 시 backlog Story 로 변환 (예: 누락된 §10 row → Story 작성)
4. `workflow_distribution` field = `full`

##### git history audit signal

mctrader-hub git log 에 `chore: codeforge consumer setup (Path B — degraded distribution)` commit 존재 (2026-04-25 시점). 본 CFP-86 = ex post SSOT 화 — 이미 emerge 한 패턴 명시.

### 2d. GitHub Labels 생성 (gh CLI 일괄)

> **CFP-12 자동화** (권장): `bash scripts/bootstrap-labels.sh [<org>/<repo>]` — 아래 18 label을 idempotent로 일괄 생성. SessionStart hook의 `check-bootstrap.sh`가 부재 시 자동 안내.

수동 명령으로 진행하려면:

```bash
ORG_REPO="<your-org>/<your-repo>"

# Type labels
gh label create "type:epic" --color "3E4B9E" --repo "$ORG_REPO"
gh label create "type:story" --color "0E8A16" --repo "$ORG_REPO"
gh label create "type:bug" --color "D73A4A" --repo "$ORG_REPO"
gh label create "type:audit" --color "FBCA04" --repo "$ORG_REPO"
gh label create "impl-manifest" --color "C2E0C6" --repo "$ORG_REPO"

# Phase labels (single-active, phase-label-invariant.yml Action이 강제)
for phase in "요구사항" "설계" "설계-리뷰" "구현" "구현-리뷰" "구현-테스트" "보안-테스트"; do
  gh label create "phase:$phase" --color "FEF2C0" --repo "$ORG_REPO"
done

# Gate labels (review pass)
gh label create "gate:design-review-pass" --color "C2E0C6" --repo "$ORG_REPO"
gh label create "gate:security-test-pass" --color "C2E0C6" --repo "$ORG_REPO"

# Fix labels (cumulative)
for lane in "설계-리뷰" "구현-리뷰" "구현-테스트" "보안-테스트"; do
  gh label create "fix:${lane}-retry" --color "F9D0C4" --repo "$ORG_REPO"
done

# Hotfix / audit
gh label create "hotfix:minimal" --color "FF5722" --repo "$ORG_REPO"
gh label create "hotfix:critical" --color "B71C1C" --repo "$ORG_REPO"
gh label create "audit:post-hotfix" --color "FBCA04" --repo "$ORG_REPO"
```

### 2e. Branch protection (main)

#### 다인 contributor 팀 (default — review gate 강제)

```bash
gh api -X PUT repos/$ORG_REPO/branches/main/protection \
  -F required_status_checks='{"strict":true,"contexts":["phase-gate-mergeable"]}' \
  -F required_pull_request_reviews='{"required_approving_review_count":1,"require_code_owner_reviews":true}' \
  -F enforce_admins=false \
  -F restrictions=null
```

#### 단일 author / 1-2인 팀 (solo-dev 권장)

단일 author 가 sole CODEOWNER 이면 GitHub 정책 (`Cannot approve your own pull request`) 으로 self-approve 불가능 → 모든 PR 영구 deadlock. 다음 완화 분기 권장:

```bash
gh api -X PUT repos/$ORG_REPO/branches/main/protection \
  -F required_status_checks='{"strict":true,"contexts":["phase-gate-mergeable"]}' \
  -F required_pull_request_reviews='{"required_approving_review_count":0,"require_code_owner_reviews":false}' \
  -F enforce_admins=false \
  -F restrictions=null
```

`phase-gate-mergeable` status check 는 그대로 강제 — review-gate 만 완화. 팀 합류 시 위 다인 모드로 전환.

#### 이미 deadlock 상태인 경우 (workaround — standard flow 아님)

`enforce_admins=false` + repo admin 권한 보유자가 admin override:

```bash
gh pr merge --admin --squash <PR-number>
```

본 명령은 **escape-hatch** 이며 정상 flow 가 아님. solo-dev 모드 시 위 권장 분기 적용 후 일반 `gh pr merge --squash` 사용.

### 2f. 보안 보강 활성화 (consumer settings)

GitHub repo settings 또는 gh api로:
- **Dependabot alerts** + **Dependabot security updates** (자동 PR)
- **CodeQL** (default setup 권장)
- **Secret Scanning** + **Push Protection**

이는 SecurityTestPL의 1차 layer로 활용된다.

### 2g. Workflow permissions (org-level) — **반드시 설정**

**`story-init.yml` workflow 가 Phase 1 PR 을 자동 open 하므로 GitHub Actions 에 PR 생성 권한 필요**. CFP-11 end-to-end 실증에서 발견된 bootstrap drift — org admin 권한 필요 (1회 설정).

> **CFP-65 F2 Phase 1 복원**: CFP-45 가 `story-init.yml` 을 internal-docs 로 이동한 후 CFP-65 가 single-repo flavor 로 plugin templates 에 복귀. consumer 첫 사용 시 본 설정 1회 활성화 필수.

**Web UI**:
1. https://github.com/organizations/`<your-org>`/settings/actions
2. **Workflow permissions** → "Read and write permissions" 선택
3. **"Allow GitHub Actions to create and approve pull requests"** 체크
4. Save

**CLI** (admin:org scope 필요, `gh auth refresh -h github.com -s admin:org` 후):

```bash
gh api -X PUT orgs/<your-org>/actions/permissions/workflow \
  -f default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true
```

미설정 시: `story-init.yml` 의 `Create Phase 1 PR` step 이 다음 에러로 fail:
```
GitHub Actions is not permitted to create or approve pull requests (createPullRequest)
```
(branch + docs file 은 commit·push 되지만 PR auto-open 실패. 수동 `gh pr create` 로 복구 가능하나 자동화 가치 손실)

> **§1 invariant 자동 강제**: CFP-67 (F2 Phase 2 split 1/2) 후 `story-section-1-immutable.yml` 자동 강제. §1 변경 PR 시 자동 reject — 정당한 정정은 PR 제목 `[bypass-section-1]` + CODEOWNERS architect team approval 절차 (§7 Q7 참조).

### 2h. `.gitignore`에 추가

```gitignore
# codeforge plugin — generated files
.claude/agents/
.claude-work/
CLAUDE.md    # core+overlay merge 결과면 gitignore. 수동 커밋 원하면 제외.
```

## 3. Overlay 작성

### 3a. `.claude/_overlay/project.yaml` — objective SSOT 상수

GitHub 좌표·CODEOWNERS·Discussions·Milestone·labels 등 structured 상수를 작성. Schema 전체 명세: [`project-config-schema.md`](project-config-schema.md).

```yaml
project:
  name: <your-project>

github:
  org: <your-org>
  repo: <your-repo>
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: <PREFIX>      # e.g. TM
  codeowners:
    architect_team: "@<your-org>/architects"
    domain_expert_team: "@<your-org>/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"

labels:
  components:
    - <component-1>   # e.g. api
    - <component-2>   # e.g. ui
```

주 소비자: RequirementsPLAgent · DomainAgent · PMOAgent · ArchitectPLAgent 및 각 lane plugin. 에이전트는 이 파일을 `Read`로 직접 참조.

SessionStart hook이 자동으로 `validate_config.py`를 실행해 schema 준수를 검증. 위반 시 hook abort. 수동 검증:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/validate_config.py \
    .claude/_overlay/project.yaml
```

### 3b. `.claude/_overlay/CLAUDE.md` 예시 (narrative 컨텍스트)

CLAUDE.md overlay에는 **서술 컨텍스트만** (도메인 소개·기술 스택 선택 근거·경로 관습 설명). Objective 상수는 project.yaml에 있음.

```markdown
## Project

`<your-project>` — <한 줄 프로젝트 설명>. <기술 스택> 기반.

SSOT 상수는 `.claude/_overlay/project.yaml` 참조.

## Domain

<프로젝트 도메인 한 줄 서술>

## 기술 스택 (선택 근거)

- 언어: <선택 이유 포함>
- 저장소: <선택 이유>
- 배포: <선택 이유>

## 경로 관습

- `src/<your-domain>/...` — 도메인 로직
- `src/adapters/...` — 외부 시스템 어댑터
- 기타 프로젝트 관습
```

### 3c. Preset 임포트 (선택)

프로젝트 shape이 플러그인 preset과 맞으면 preset agents를 overlay로 복사.

```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

상세는 [`../presets/README.md`](https://github.com/mclayer/plugin-codeforge-develop/blob/main/presets/README.md) 참조.

### 3d. `.claude/_overlay/agents/<Name>.md` 예시

프로젝트 특화 정보가 필요한 에이전트만 overlay 작성. 대부분 에이전트는 core만으로 충분.

#### `.claude/_overlay/agents/DomainAgent.md`

```markdown
### 도메인 소스

- Domain Knowledge: `docs/domain-knowledge/<your-area>/...`
- ADR 카테고리 (frontmatter `category:`): `<project-domain-category>`
- 도메인 코드 경로: `src/<your-project>/domain/**`
- 도메인 용어: <용어1>, <용어2>, <용어3>

### 우선순위 원칙
- <예: 지연 민감 / 데이터 일관성 / 보안 / 장애 복구 등>
```

## 4. 첫 실행 검증

### 4a. Claude Code 세션 시작

프로젝트 디렉토리에서 `claude` 실행. SessionStart hook이 자동으로 `.claude/agents/*.md`와 `CLAUDE.md` 생성.

### 4b. 의존성 점검

세션 개시 즉시 Orchestrator가 의존성 체크 결과 출력. 6개 워크플로우·3개 Forms·CODEOWNERS 부재 시 알림.

### 4c. 첫 Story 생성

GitHub UI 에서 Issue 생성 → "Story" 템플릿 선택 → 사용자 요구사항 입력 → 제출.

`story-init.yml` Action 이 자동 (CFP-65 F2 Phase 1 — single-repo flavor):

1. project.yaml `github.story_key_prefix` fetch
2. 다음 KEY 번호 계산 (`docs/stories/<PREFIX>-N.md` 스캔)
3. `docs/stories/<KEY>.md` 생성 (§1=verbatim 입력, §2-11=placeholder)
4. Phase 1 PR 자동 open (architect team CODEOWNERS auto-review)
5. Issue body 를 docs file 링크로 갱신
6. (optional) Epic Milestone / Component label 부착

이후 Claude Code 세션을 재시작하거나 prompt 에 "Story `<KEY>` 진행" 이라고 입력하면 Orchestrator 가 활성 Story 를 감지해 RequirementsPLAgent 스폰.

> **F2 Phase 2 split 종료** (CFP-68): §1 변경 차단 (`story-section-1-immutable.yml` — CFP-67) ✅ + FIX Ledger label sync (`fix-ledger-sync.yml` — CFP-67) ✅ + Impl Manifest 자동 sub-issue + GraphQL addSubIssue (`subissue-from-impl-manifest.yml` — CFP-68) ✅. F2 (#116) Phase 2 모든 caveat 해소.

## 5. Workflow

Consumer 프로젝트에서 요구사항을 GitHub Issue Form으로 입력하면 플러그인이 0 core (wrapper-only) + 23 distributed agent (6 lane plugin) + `role: dev` 동적 roster · 7 레인 구조로 자율 실행:

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트
```

**Story flow (default — single-repo Story 또는 Epic 외 1 child Story)** — **1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항+설계+설계리뷰): docs only
- **Phase 2 PR** (구현+구현리뷰+구현테스트+보안테스트): code + docs append

**Epic flow (cross-repo 또는 multi-Story Epic, CFP-82)** — **1 Epic = Phase 1 doc PR + N implementation PRs + close PR**:
- **Phase 1 PR** (hub / owner repo): Epic doc + child Story stubs + Codex 7-area review aggregate
- **Phase 2 ~ Phase N PR**: 각 child Story implementation. Joint-phase narrow form 허용 (1 Story 가 1 phase 안 multi-repo joint PR 보유 가능, ADR-020 Amendment 1)
- **Phase N+1 close PR** (hub / owner repo): `EPIC-RESULTS-<KEY>.md` Epic close artifact
- Mid-Phase **spec amendment PR** 가능 (Codex push-back 발견 시)

mctrader 진행 중 Epic 예시:

| Epic | Phase 1 (hub) | Phase 2~N (impl) | close PR | total PR |
|---|---|---|---|---|
| MCT-25 RiskGate full | hub#41 | data#1 + engine#1/#2/#3 | hub#42 | 6 |
| MCT-32 Order rate limit | hub#48 | engine#4/#5/#6 + market-bithumb#1 | hub#49 | 6 |
| MCT-48 Paper Runtime | hub#64 | engine#10/#11/#12 + web#1/#2 + spec amend hub#72 | (in flight) | 7+ |

상세 오케스트레이션 규칙은 [`orchestrator-playbook.md`](orchestrator-playbook.md).

### 5.1 Cross-repo Epic — Centralization mode 선택 (multi-repo consumer)

multi-repo consumer (예: mctrader 의 6 repo) 의 cross-repo Epic 진행 시 [ADR-020 Amendment 1](adr/ADR-020-cross-repo-epic-pattern.md) (CFP-81) 의 mode 결정 의무:

| Mode | child Story 위치 | 채택 조건 |
|---|---|---|
| **A: Repo-local** (ADR-020 v1 default) | 각 작업 repo 의 `docs/stories/<KEY>.md` | Implementation repo 가 자체 storyboard 운영 / repo 별 자율 lifecycle |
| **B: Hub-centralized** | 1 hub repo 가 모든 child Story 보유, implementation repo 는 code PR 만 | Doc-only hub repo 존재 + 도메인 ADR collocate (mctrader 패턴) |

**Mixed-mode 금지** — 단일 Epic 내 mode 일관 유지. 다른 Epic 은 다른 mode 가능.

**Joint-phase narrow form 허용** (ADR-020 Amendment 1 §결정 9): 단일 child Story 가 1 phase 안에서 multi-repo joint PR 보유 가능 (예: foundation Story 의 data + engine 동시 변경). 모든 PR 가 동일 Story key + 동일 phase label + topological merge order. mctrader MCT-26 = 사용 사례.

**Mid-Epic 신규 repo 추가**: 기존 mode 유지 default. Mode 전환 필요 시 Epic 분할 또는 재시작 (consumer 명시 ESCALATE). 상세 = playbook §3.4 + ADR-020 Amendment 1 §결정 8.

## 6. FAQ

### Q1. Overlay에 스칼라 필드(name, description, model)가 들어가면?

**merge.py가 abort**한다. 스칼라는 core-only.

### Q2. `.claude/agents/*.md`를 직접 편집하면?

SessionStart hook이 다음 실행 시 덮어쓴다. 편집하려면 `.claude/_overlay/agents/` 또는 플러그인 core agents/를 수정.

### Q3. Core 에이전트 자체를 바꾸고 싶다 (버그 수정·새 규칙 추가)

**플러그인 repo에 PR**. Core는 모든 consumer의 SSOT.

### Q4. 플러그인 업그레이드 시 overlay 호환성

core의 에이전트 섹션 구조·frontmatter 키가 바뀌면 overlay가 깨질 수 있다. 플러그인 버전 변경 시 [`migration-guide.md`](migration-guide.md) 참조.

### Q5. `codex` / `gh` 미설치 상태에서 시작하면?

세션 시작 시 의존성 체크가 blocking wait 상태로 전환되며 설치 요청. 설치 전까지 어떤 작업도 진행 안 함.

### Q6. GitHub Workflow 파일이 plugin과 drift된 경우?

SessionStart hook이 plugin templates SHA와 consumer `.github/workflows/` 사본 SHA 비교 후 알림. 자동 덮어쓰기 안 함. consumer가 검토 후 갱신:

```bash
diff -u ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<file>.yml \
        .github/workflows/<file>.yml
# 차이 검토 후
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<file>.yml .github/workflows/
```

### Q7. §1 변조 금지 invariant를 정당하게 위반해야 할 때 (예: 오타 수정)

`story-section-1-immutable.yml` Action이 자동 reject한다. 정당한 정정을 위한 bypass:

1. 별도 PR을 docs only로 open
2. **PR 제목**에 `[bypass-section-1]` 추가 (대소문자 무관, 정규식 매칭)
3. **architect team CODEOWNERS** 멤버 1명 이상 GitHub PR APPROVED review
4. Action이 두 조건 충족 시 자동 PASS, 부족 시 명확한 사유 코멘트 + status fail로 안내

요건:
- `.github/CODEOWNERS`에 `docs/stories/** @<org>/<architect-team>` 매핑 존재 (없으면 bypass 작동 불가)
- architect team에 GitHub repo `read` 이상 권한

운영 빈도 0에 가까워야 함 (주로 사용자 원문 명백한 오타 정정).

## 7. Sonnet Decider 정책 (CFP-61 / ADR-022)

본 plugin install 한 consumer 프로젝트의 Orchestrator 도 Sonnet decider 적용 대상. 단 Phase 1 = trust model — plugin CLAUDE.md doc 만 정책 source, 강제 instrumentation 없음.

### Phase 1 활성 절차

consumer 측 사용자 가 다음 directive 발화 시 활성:

> "이 프로젝트에서도 codeforge plugin Sonnet decider 정책 (CFP-61 / ADR-022) 적용해서 정지 없이 진행해라."

또는 동등 wording. directive 없으면 default = user-approval gates 운영.

### 적용 trigger 5 종 (ADR-022 §결정 2)

- (a) substantive 다중 선택지
- (b) FIX root-cause 불일치
- (c) Codex ambiguity (option-formulation 한정)
- (d-constraint) 제약 surfacing Q
- (e) review-verdict — 매 review iteration 종료 후 Sonnet final pick (PASS|FIX)

### 운영 의존성

- `Agent` tool with `model: sonnet` (Anthropic billing 내, 외부 auth 무관)
- 외부 API key / Plus subscription / Vertex AI / GCA — 의무 prerequisite 아님 (CFP-58 axis 모두 제거)

### Phase 2 enforcement (후속)

30+ packet 운영 후 ROI 평가 + instrumentation hook / refusal logic / runtime validation 도입 여부 결정 — 별도 CFP.

### 사용자 explicit suspension

"잠깐 끄자" / "Sonnet decider 정지" → session/Story 단위 일시 중단 — review-verdict trigger 발화 시 PL 1차 판단 (pl_recommendation) 으로 임시 proceed (ADR-022 §결정 9).

## 7.1 Stop discipline + Epic-level continuity (ADR-025 + Amendment 1)

Sonnet decider 정책 (§7) 의 **trust model invariant** 와 **Epic-level continuity** 직접 적용:

### "Sonnet decides ⇒ Orchestrator proceeds without user confirmation" (ADR-025 §결정 1)

Sonnet decider 가 PASS / FIX / pick 응답 후 Orchestrator 가 사용자에게 "진행할까요?" / "이대로 가도 됩니까?" 묻는 것은 **whitelist 외 stop = `policy_violation` (defect)** 분류.

### Epic-level continuity (CFP-80 / ADR-025 Amendment 1, 2026-05-04)

**사용자 메시지 받은 시점 = 작업 단위 식별**:

| 사용자 메시지 패턴 | 작업 단위 | Continuity 의무 |
|---|---|---|
| "다음 작업 있나" + 1+ 후보 존재 | 모든 후보 / backlog 처리 단위 | backlog 모든 issue / Story 자동 통과 + 1번 final report |
| "X 진행" (X = Epic 명시) | Epic 의 7 phase + 모든 child Story | child Story 모두 Phase 1 + Phase 2 PR cycle 자동 통과 + 1번 final report |
| "X 진행" (X = Story 명시) | Story 의 Phase 1 + Phase 2 PR cycle | 양 PR cycle 자동 통과 + 1번 final report |
| 명시 선택 ("a" / "C" / "ok" / "진행하자") | 직전 메시지의 후보 또는 진행 path | path 끝까지 자동 진행 |
| 정보 요청 ("X 보여달라") | 정보 답변 단위 | 답변 + stop 없음 |

### 합법 stop whitelist (5종 strict — 본 외 모든 stop = defect)

1. **User environment 변경 의무** (PAT 발급 / API key / 외부 서비스 가입 / 자금 입금 / 1Password setup 등)
2. **Destructive action 직전** (force push / DB drop / 설정 영구 변경 / production first 동작)
3. **진정 unprecedented / unscoped 영역** (새 organizational decision)
4. **Codex+Sonnet decider 의 escalation 결정** (`decider_decision.escalation_required=true`)
5. **작업 단위 완료 후 final report** (1번)

### 불법 stop 패턴 (반드시 회피)

| Pattern | Defect 사유 |
|---|---|
| "후보 A/B/C/D 중 어떤거?" | Codex+Sonnet 자동 처리 의무 (sub-decision) |
| "큰 작업이라 확인 받겠습니다" | token cost 추정 = 사용자 의도 아님 |
| "Phase 1 완료, Phase 2 시작할까요?" | 1 Story / Epic 안의 sub-step (decision unit 분리 violation) |
| "5 sub-CFP 중 첫 번째 완료, 다음 진행할까요?" | backlog 단위면 5 모두 처리 |
| "final report 후 다음 작업 후보 결정 받음" | backlog 안 끝났으면 자동 발굴 + 진행 |

### Result 보고 형식 (1번)

작업 단위 전체 완료 후 1번 final report — sub-step 별 완료 시각 / 소요 시간 / Sonnet pick / override marker 포함. 사용자 redirect 가능성 명시 (단 본인이 stop 안 함).

### Consumer 측 활성 directive

consumer 측 사용자 발화 의무 (Phase 1 trust model — enforcement hook 없음):

> "이 프로젝트에서도 codeforge plugin Stop discipline + Epic-level continuity (ADR-025 / CFP-80) 적용해서 작업 단위 끝까지 자동 진행 + 1번 final report 해라."

또는 동등 wording. directive 없으면 default = user-approval gates 운영 + 매 phase stop.

### Phase 2 instrumentation (후속)

30+ stop event 누적 후 stop-event-v1 ledger ROI 평가 + 도입 시:
- `reason_class` enum: `policy_violation` / `policy_violation_subdecision` / `policy_violation_phase_split` 분류
- consumer + wrapper 양쪽 행동 데이터 누적
- hook / refusal logic / runtime validation 도입 여부 결정 — 별도 CFP

## 8. 트러블슈팅

| 증상 | 원인 | 대응 |
|------|------|------|
| `regen-agents.sh: merge.py not found` | PLUGIN_ROOT 해석 실패 | `CLAUDE_PLUGIN_ROOT` 환경변수 확인 |
| `ERROR: overlay scalar mismatch at '.name'` | overlay frontmatter에 core와 다른 name 지정 | overlay의 name 필드 제거 |
| `ERROR: PyYAML required` | python3 환경에 PyYAML 없음 | `pip install pyyaml` 또는 venv 설정 |
| Agent가 overlay 내용을 따르지 않음 | 생성된 `.claude/agents/<Name>.md` 확인 | `cat .claude/agents/<Name>.md` → overlay body 실제 존재하는지 점검 |
| `gh: command not found` | gh CLI 미설치 | https://cli.github.com/ 참고해 설치 |
| GitHub MCP 미인증 | OAuth 만료 | `/mcp` 재인증 |
| story-init.yml Action 실패 | yq 미설치 또는 project.yaml 누락 / `github.story_key_prefix` 부재 | Action 로그 확인. yq 는 ubuntu-latest 표준 미보장 — Python fallback parser 가 두 번째 단계로 작동. project.yaml `github.story_key_prefix` 필수 |
| story-section-1-immutable.yml fail | §1 변경 + bypass marker 부재 | PR 제목 `[bypass-section-1]` 추가 + CODEOWNERS architect team APPROVED review (§7 Q7 절차) |
| fix-ledger-sync.yml mirror 안 됨 | §10 표 형식 위반 | `fix-event-v1` schema 준수 — 7 column (Iter / 시각 / 레인 / 트리거 / 원인 판정 / 재실행 범위 / RESET?). Iter = 1-indexed integer |
| subissue-from-impl-manifest.yml fail | §8.5 표 형식 위반 또는 `addSubIssue` GraphQL 권한 부재 | §8.5 첫 column = file path (각 row 1 sub-issue). GitHub Sub-issue 기능은 GraphQL beta — `issues:write` 권한 + repo 가 sub-issue feature flag 활성화 필요. 미작동 시 fallback = `core.warning` 만 — sub-issue 자체는 생성됨 (parent link 만 누락) |
| Phase-gate-mergeable check 통과 안 됨 | phase + gate 라벨 미부착 | lane plugin (DesignReviewPL·SecurityTestPL)이 라벨 부착했는지 확인. phase-label-invariant.yml가 자동 single-active 강제하므로 새 phase 라벨만 추가하면 됨 |
| §1 변경 PR이 reject됨 | story-section-1-immutable.yml | Q7 참조 |
| sub-issue 자동 생성 안 됨 | §8.5 매핑표 형식 오류 또는 `addSubIssue` GraphQL beta 변경 | Action 로그 확인. fallback으로 DeveloperPL이 `mcp__github__sub_issue_write` 수동 호출 |
