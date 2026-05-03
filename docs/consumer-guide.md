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
│   ├── workflows/                      # Plugin 워크플로우 5종 consumer-distributable (수동 cp)
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
# Workflow 5개 복사 (consumer-distributable: phase-gate-mergeable + phase-label-invariant + story-init + story-section-1-immutable + fix-ledger-sync)
mkdir -p .github/workflows
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/

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

세션 개시 즉시 Orchestrator가 의존성 체크 결과 출력. 5개 워크플로우·3개 Forms·CODEOWNERS 부재 시 알림.

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

> **F2 Phase 2 split 잔존**: §1 변경 차단 자동 (`story-section-1-immutable.yml` — CFP-67) ✅ + FIX Ledger label sync 자동 (`fix-ledger-sync.yml` — CFP-67) ✅. **Impl Manifest 자동 sub-issue** (`subissue-from-impl-manifest.yml`) 만 CFP-68 까지 manual sub-issue create.

## 5. Workflow

Consumer 프로젝트에서 요구사항을 GitHub Issue Form으로 입력하면 플러그인이 0 core (wrapper-only) + 23 distributed agent (6 lane plugin) + `role: dev` 동적 roster · 7 레인 구조로 자율 실행:

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트
```

**1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항+설계+설계리뷰): docs only
- **Phase 2 PR** (구현+구현리뷰+구현테스트+보안테스트): code + docs append

상세 오케스트레이션 규칙은 [`orchestrator-playbook.md`](orchestrator-playbook.md).

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
| Phase-gate-mergeable check 통과 안 됨 | phase + gate 라벨 미부착 | lane plugin (DesignReviewPL·SecurityTestPL)이 라벨 부착했는지 확인. phase-label-invariant.yml가 자동 single-active 강제하므로 새 phase 라벨만 추가하면 됨 |
| §1 변경 PR이 reject됨 | story-section-1-immutable.yml | Q7 참조 |
| sub-issue 자동 생성 안 됨 | §8.5 매핑표 형식 오류 또는 `addSubIssue` GraphQL beta 변경 | Action 로그 확인. fallback으로 DeveloperPL이 `mcp__github__sub_issue_write` 수동 호출 |
