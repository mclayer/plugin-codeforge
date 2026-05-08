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
- **플러그인 4종**: `codex@openai-codex`, `superpowers@claude-plugins-official` ([integration SSOT](superpowers-integration.md)), `claude-md-management@claude-plugins-official`, `github@claude-plugins-official`
- **CLI 2종**: `codex`, `gh` (`gh auth login` 인증)

### 1c. 권장 플러그인 (선택)
- `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

### 1d. Plugin install 의무 — `enabledPlugins` ↔ `installed_plugins.json` (CFP-132 / Issue #238)

**중요**: `~/.claude/settings.json` 의 `enabledPlugins[<id>] = true` 만으로는 agent / skill 노출 불충분합니다. Claude Code 는 세션 시작 시 `~/.claude/plugins/installed_plugins.json` 을 읽어 plugin 을 discovery — `installed_plugins.json` 에 entry 가 없으면 `enabledPlugins=true` 라도 agent 미노출.

**증상**: 설치 후 `subagent_type` 리스트에 `codeforge-design:*` / `codeforge-review:*` 등 미노출 → "왜 ArchitectPL agent 가 없지?".

**올바른 절차**:

```bash
# enabledPlugins=true 만 토글 — 부족
# (settings.json 수동 편집 OR /config 토글)

# /plugin install 명시 실행 — installed_plugins.json entry 추가
/plugin install codeforge@<marketplace>
/plugin install codeforge-requirements@<marketplace>
/plugin install codeforge-design@<marketplace>
/plugin install codeforge-review@<marketplace>
/plugin install codeforge-develop@<marketplace>
/plugin install codeforge-test@<marketplace>
/plugin install codeforge-pmo@<marketplace>
/plugin install codex@openai-codex
/plugin install superpowers@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install github@claude-plugins-official
```

새 세션 시작 시 11 plugin agent 모두 노출 확인 — 미노출 시 `~/.claude/plugins/installed_plugins.json` entry 부재 점검.

**자동 검증**: SessionStart hook (`overlay/hooks/check_bootstrap.py`) 가 `REQUIRED_PLUGINS` 11종 verify, 누락 시 stderr WARN 출력 (CFP-103). 본 WARN 메시지를 보면 `/plugin install` 누락이 원인 — 위 명령 실행으로 해결.

### 1e. Pre-push lint hook (선택, 권장 — CFP-132 / Issue #236)

**문제**: 매 phase production push 후 CI 의 ruff/pyright fail → fix → push 사이클 반복 (4-round 평균) → GitHub Actions 비용 폭증.

**해결**: pre-push hook 으로 push 전 lint 자동 실행 — fail 시 push 차단 + 로컬 fix 유도.

**Install (수동)**:

```bash
# Option A: .git/hooks/pre-push 직접 cp
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/pre-push.sh.example .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# Option B: core.hooksPath 사용 (.githooks/ 디렉터리 commit 가능)
mkdir -p .githooks
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/pre-push.sh.example .githooks/pre-push
chmod +x .githooks/pre-push
git config core.hooksPath .githooks
```

**Manual 실행 (hook 미사용 시)**:

```bash
# PR open 전 의무
bash scripts/check-lint.sh           # 검사
bash scripts/check-lint.sh --fix     # ruff auto-fix 적용
```

`scripts/check-lint.sh` 는 pyproject.toml (ruff + pyright) / package.json (eslint + tsc) 자동 detect, 없으면 silent skip.

**Bypass (긴급 push)**: `git push --no-verify`

**Rollback**: `rm .git/hooks/pre-push` 또는 `git config --unset core.hooksPath`

**Windows 환경 caveat**: `.venv/Scripts/Activate.ps1` 경로 권한 / WSL bash 호출 issue 시 manual 실행 fallback. 자세한 워크어라운드는 별도 follow-up CFP.

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

### 2.0. 5분 quickstart (RECOMMENDED — single-command setup, CFP-125)

새 consumer project 에서 처음 codeforge 적용 시 단일 명령 setup + 검증:

```bash
# Setup (idempotent, --dry-run 으로 사전 검증 가능)
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/bootstrap-consumer.sh
  # 8 단계: pre-check / plugin install reminder / overlay scaffold / settings.json /
  #         workflows+forms+CODEOWNERS / labels / consumer-scripts.manifest / summary

# Verify
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
  # 4 verification: check_bootstrap.py (8 sub-check) / plugin 11종 / project.yaml schema / settings.json 3 hook
```

Windows:

```powershell
pwsh -File ${env:CLAUDE_PLUGIN_ROOT}/codeforge/scripts/bootstrap-consumer.ps1
pwsh -File ${env:CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.ps1
```

**PASS 시**: 첫 Story Issue Form 제출 가능. `gh issue create --template story.yml` (또는 GitHub UI 의 New Issue → Story).

**KEY 사전 확보 (선택, ADR-036 / CFP-260 — Option B)**: brainstorming 시점에 KEY 미리 확보가 필요하면 `gh issue create --template cfp-reserve.yml` (또는 GitHub UI New Issue → "CFP key reservation"). 받은 Issue # 가 KEY 가 됨 (`<PREFIX>-<#>`, 예: TM-247). spec 작성 후 label `phase:reservation` → `phase:요구사항` + `type:story` 로 promote 시 story-init.yml 자동 트리거. 30 일 미진행 시 `reservation-cleanup.yml` 가 자동 close.

**Version drift 검사 (선택, ADR-037 / CFP-262 / CFP-273 — 권장)**: consumer 가 stale codeforge plugin 으로 작업 진입 시 silent corruption 위험. SessionStart hook 으로 자동 검사 권장.

**Activate (cp 방식, CFP-273)**:

```bash
# Sample hook config 복사 (overlay/hooks/merge.py 가 settings.json 에 자동 merge)
mkdir -p .claude/_overlay/.claude/hooks/
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/.claude/hooks/SessionStart-codeforge-drift.json.sample \
   .claude/_overlay/.claude/hooks/SessionStart-codeforge-drift.json
```

**Manual 실행 (hook 미사용 시)**:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-version-drift.sh
# Exit 0 = no drift / MINOR / PATCH (작업 진행)
# Exit 1 = MAJOR drift (hard-stop, /plugins update <name> 의무)
# Exit 2 = prerequisite missing (gh CLI / jq / awk / gh auth status)
```

**Severity → action (ADR-037 cross-ref)**:
- **MAJOR** = hard-stop blocking → `/plugins update <name>` 의무 + Orchestrator 재 spawn
- **MINOR** = warning + auto-proceed → 작업 진행, 사용자에게 update 권유
- **PATCH** = info only → 작업 진행, log 만

**Bypass (긴급 / network 부재 시)**: `BYPASS_VERSION_DRIFT=1 BYPASS_VERSION_DRIFT_REASON='<text>'`. reason field non-empty 의무 (audit trail).

**FAIL 시**: stderr 의 안내 따라 manual fix 또는 §2a-§2h manual fallback 절차 활용. `--dry-run` 으로 변경 미적용 사전 진단, `--reset` 으로 state marker 삭제 + clean 재시도.

**Recovery**:
- Default semantic = `--resume` (`.claude/_overlay/.bootstrap-state.json` marker 인식 + 재개점부터)
- `--force` — marker 무시 모든 단계 재시도 (cp -n 안전망 보존)
- `--reset` — marker 삭제 + clean state from scratch (사용자 확인 prompt 의무)
- 기존 `.claude/settings.json` 는 자동 backup `.claude/settings.json.bak.<ts>` (단계 4 시)

**Plugin install 안내**: `bootstrap-consumer.sh` 가 누락 plugin 11종 listing stdout 출력 — 실 install 은 platform-level (Claude Code `/plugins install` 명령 사용자 직접 실행 의무).

§2.1 ~ §2.7 = manual / advanced fallback (script 미작동 시 / 부분 customize 필요 시).

---

### 2.0a Optional Stage 0 — pre-Issue brainstorming (recommended for non-trivial Story)

복잡한 요구사항 (cross-cutting / 새 도메인 / 모호한 scope) 인 경우, Issue Form 제출 전 `superpowers:brainstorming` skill 로 scope 를 먼저 정리할 수 있습니다 ([ADR-034](adr/ADR-034-pre-issue-brainstorming-stage.md), [orchestrator-playbook §1.2.0](orchestrator-playbook.md)). 산출 spec 의 결론 요약을 Issue Form `user-original` 필드에, spec path 를 `spec_link` 필드에 입력하면 codeforge requirements lane 이 그 텍스트를 입력으로 받아 분석을 시작합니다. 작은 chore / 명료한 요구사항이면 생략 가능 — Stage 0 는 옵션입니다 (CI 강제 없음).

Spec 저장 위치:
- **Consumer project**: `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md` (skill default)
- **Plugin repo dogfood (codeforge family)**: `<internal-docs>/<plugin-folder>/specs/YYYY-MM-DD-cfp-NNN-<slug>-design.md` ([ADR-013](adr/ADR-013-codeforge-family-dogfood-out-policy.md) / [ADR-017](adr/ADR-017-skill-override-path-enforcement.md) enforced)

In-lane brainstorming (DomainAgent / RequirementsPL 가 lane 내부에서 호출) 과는 다른 단계 — [superpowers-integration.md §2](superpowers-integration.md) 참조.

---

### 2.1 (manual fallback) 초기 복사

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

(§2a anchor 보존 — 외부 link 호환)

### 2.2 (manual fallback) `.claude/settings.json` 설정 — 3 hook 등록 (CFP-103 + CFP-104 + CFP-106 정합)

`templates/settings.json.example` 정합 NESTED schema. 3 hook 등록 의무 — SessionStart × 2 (regen-agents + check-bootstrap) + UserPromptSubmit × 1 (userprompt-reminder). FLAT schema (기존 §2b 잔존, CFP-125 fix 전) 는 invalid — Claude Code parser silent skip 가능성.

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh" }
        ]
      },
      {
        "hooks": [
          { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/check-bootstrap.sh" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/userprompt-reminder.sh" }
        ]
      }
    ]
  }
}
```

**Windows variant** (PowerShell wrapper, `templates/settings.json.example` `_windows_note` 정합):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "pwsh -File ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.ps1" }] },
      { "hooks": [{ "type": "command", "command": "pwsh -File ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/check-bootstrap.ps1" }] }
    ],
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "pwsh -File ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/userprompt-reminder.ps1" }] }
    ]
  }
}
```

**Hook 역할**:
- SessionStart `regen-agents.sh` (CFP-65) — overlay agents 자동 merge
- SessionStart `check-bootstrap.sh` (CFP-103) — 8 sub-check (workflow 권한 / label / plugin / consumer workflows / forms / CODEOWNERS)
- UserPromptSubmit `userprompt-reminder.sh` (CFP-104) — 변경 착수 prompt 검출 시 reminder inject

(§2b anchor 보존 — 외부 link 호환. CFP-125 Phase 2 PR 가 §2b FLAT → NESTED schema fix.)

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

> **CFP-12 자동화** (권장 — consumer 1 repo): `bash scripts/bootstrap-labels.sh [<org>/<repo>]` — 아래 18 label을 idempotent로 일괄 생성. SessionStart hook의 `check-bootstrap.sh`가 부재 시 자동 안내.

> **CFP-120 (codeforge family setup)**: codeforge family 7 repo (wrapper + 6 lane) 모두 label 부트스트랩 = `bash scripts/bootstrap-codeforge-family.sh [--org <org>]` (default org: `mclayer`). lane plugin contributor 가 처음 setup 할 때 의무. label 부재 시 cross-repo Story binding PR 의 phase + gate label apply 가 `'phase:설계-리뷰' not found` 로 실패.

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

### 2i. Strict mode opt-in (CFP-127 / ADR-032 amendment 1) — RECOMMENDED for mctrader 6-repo

기본 동작 (default): `check_bootstrap.py` 가 drift 발견 시 stderr 경고만 출력, exit 0 (ADR-027 §결정 2 Tertiary trigger LLM-trust 정합). 신규 consumer 가 lane orchestration 진입 가능하지만 enforcement layer 가 silent 로 누락될 위험.

**Strict mode opt-in**: `bootstrap.strict_mode: true` (project.yaml) 활성 시 adoption-critical drift 4종 발견 → exit 1 + Orchestrator 사용자 escalation. mctrader 6-repo first opt-in target 권장.

#### 2i-1. 점진 도입 4 단계 (Cold-start 회피)

신규 strict opt-in 시 4종 drift 동시 발견 시 escalation flood 회피하기 위한 **점진 단계** (각 단계별 PASS 확인 후 다음 진행):

```bash
# 단계 1: Plugin install (8 critical = wrapper + 6 lane + superpowers)
/plugins install codeforge@<marketplace>
/plugins install codeforge-requirements@<marketplace>
# ... 6 lane plugin 모두
/plugins install superpowers@claude-plugins-official

# 단계 1 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# Check 2 PASS 확인

# 단계 2: settings.json hook 등록 (3 hook = SessionStart × 2 + UserPromptSubmit × 1)
# §2.2 (또는 §2b legacy) 의 NESTED schema 정합 cp:
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/settings.json.example .claude/settings.json
# 단계 2 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# Check 4 PASS 확인

# 단계 3: project.yaml 작성 + validation
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example .claude/_overlay/project.yaml
# editor 에서 <REPLACE> 값 치환
python3 ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/validate_config.py .claude/_overlay/project.yaml
# 단계 3 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# Check 1 + 3 PASS 확인

# 단계 4: labels bootstrap (10 critical = phase:* 7 + gate:* 3)
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/bootstrap-labels.sh <org>/<repo>
# 단계 4 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# 모든 4 check PASS 확인

# 단계 5: strict_mode opt-in 활성
# .claude/_overlay/project.yaml 에 추가:
#   bootstrap:
#     strict_mode: true
git add .claude/_overlay/project.yaml
git commit -m "chore: opt-in bootstrap.strict_mode (CFP-127 / ADR-032)"
```

#### 2i-2. 3 mechanism + 우선순위 (CLI > env > yaml)

| Priority | Mechanism | 명령 | 적용 범위 |
|---|---|---|---|
| 1 (highest) | CLI flag | `bash check-bootstrap.sh --strict` / `python check_bootstrap.py --strict` | per-invocation |
| 2 | Env | `CODEFORGE_STRICT_BOOTSTRAP=1` | shell session |
| 3 (lowest) | YAML | `bootstrap.strict_mode: true` (project.yaml) | persistent project-level |

"Most explicit wins" — CLI flag set 시 env / yaml 무시.

#### 2i-3. Strict-eligible drift 4종

| # | Drift | Detection |
|---|---|---|
| (a) | `.claude/_overlay/project.yaml` 부재 | file presence |
| (b) | plugin 8 critical (wrapper + 6 lane + superpowers) 미설치 | `~/.claude/plugins/installed_plugins.json` parse |
| (c) | `.claude/settings.json` 의 SessionStart × 2 + UserPromptSubmit × 1 hook 미등록 | json hooks parse + command grep |
| (d) | phase:* (7) + gate:* (3) = 10 critical label 부재 | `gh label list` |

Non-eligible (warning-only 유지): workflow permissions / consumer-scripts manifest drift / consumer .github/workflows/ file (Path B degraded 정합) / Issue forms / CODEOWNERS / 기타 advisory.

#### 2i-4. Revert procedure

False-positive 발생 또는 strict mode 비활성 필요 시:

| Mechanism | Disable 명령 |
|---|---|
| CLI flag | flag 미사용 (next invocation) |
| Env | `unset CODEFORGE_STRICT_BOOTSTRAP` |
| YAML | `bootstrap.strict_mode: false` 또는 field 삭제 + commit |

#### 2i-5. ADR-027 §결정 3 Bypass 와 동시 작동

`HOTFIX_BYPASS_CODEFORGE=1 + HOTFIX_BYPASS_REASON="<reason>"` 양 env set → strict mode 활성 무관 hook self skip. Bypass priority HIGHEST.

emergency hotfix / lane invariant override 시 사용. `docs/hotfix-playbook.md` 사유 등재 의무 + post-bypass audit Issue 자동 생성.

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

progress_narration_verbosity: full  # full | lane_only
```

`progress_narration_verbosity` 는 phase 진행 narration 출력량을 조절한다. 기본값 `full` 은 ADR-029 기준 sub-step narration 까지 출력하는 opt-in 기본 동작이고, consumer 가 더 조용한 CFP-20 기존 동작을 원하면 `lane_only` 로 opt-out 하여 lane boundary event 만 출력한다.

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

### 3z. Docker-first Infra 채택 (CFP-128 / ADR-033)

framework default = Docker-first ([ADR-033](adr/ADR-033-docker-first-infra-engineering.md)). InfraEngineerAgent 가 Story 의 §5 변경 계획 에 따라 다음 산출물 생성:

- `Dockerfile` (multi-stage build — deps / builder / runner 분리)
- `compose.yml` (service definition + healthcheck + volume + network)
- `.dockerignore` (build context 축소)

#### 3z.1 `infra_strategy` override (project.yaml)

3 enum value 중 1개 선택 (default = `docker_first`):

```yaml
# .claude/_overlay/project.yaml
infra_strategy: docker_first  # default — Dockerfile + compose + .dockerignore
# infra_strategy: legacy_systemd  # legacy systemd unit / launchd plist (deprecated, opt-in only)
# infra_strategy: none            # library / config-only repo (Docker artifact 미적용)

infra_strategy_extras:
  k8s_preset_enabled: false     # presets/k8s/ activate 여부 (codeforge-develop)
```

scripts/check-container-strategy.sh 가 lint:
- `docker_first` 채택 + Dockerfile / compose.yml 부재 → exit 1
- `legacy_systemd` / `none` → skip

#### 3z.2 K8s preset opt-in

production K8s 환경 사용 시 `k8s_preset_enabled: true` + 다음 절차:

```bash
# K8s manifest skeleton 적용 (codeforge-develop presets/k8s/ 에서 templates 참조)
cp ${CLAUDE_PLUGIN_ROOT}/codeforge-develop/presets/k8s/*.yaml.template k8s/
# 각 template 의 placeholder ({app_name} / {namespace} / {image_ref}) 치환
```

Single-host docker compose 환경 = K8s preset 비활성 (`false`, default). 90% consumer 에 적합.

#### 3z.3 container-image-scan workflow 호출

본 plugin 의 `templates/github-workflows/container-image-scan.yml` reusable workflow 를 consumer build pipeline 에서 호출:

```yaml
# .github/workflows/build.yml (consumer 측)
jobs:
  build-image:
    # ... build + push to registry ...
    outputs:
      image-ref: ${{ steps.push.outputs.image-ref }}
  scan:
    needs: build-image
    uses: ./.github/workflows/container-image-scan.yml
    with:
      image-ref: ${{ needs.build-image.outputs.image-ref }}
      severity: "CRITICAL,HIGH"
      ignore-unfixed: true
```

trivy + hadolint 자동 실행. SecurityTestPL 1st-layer 의 일부 (CFP-128 / ADR-033 §결정 4).

#### 3z.4 기존 consumer follow-on Epic 패턴

ADR-033 effective date (Phase 2 wrapper PR merge) 이전 Phase 1 PR open 된 Story = grandfather (legacy 산출물 유지). retroactive 강제 없음. 컨테이너화 코드 작업 = **별도 Epic** (consumer 워크스페이스에서 수행, ADR-020 Mode B hub-centralized 권장 — mctrader 패턴):

1. Epic Issue (consumer hub repo) — 컨테이너화 scope + child Story decomposition (per repo)
2. 각 child Story 가 자체 Phase 1 + Phase 2 PR 시퀀스
3. Epic close PR (`EPIC-RESULTS-<KEY>.md` artifact)

mctrader 5 repo (Tier B-extended) = 첫 follow-on Epic 후보 (CFP-128 spec §3.4.1 / Story §11 회고 pointer).

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

## 7.5. CI Terminal State Classification (CFP-106 fix #144)

PR / GitHub Actions 결과 처리 가이드. fresh consumer (mctrader debut 등) 가 `SUCCESS` 만 wait 하는 naive polling 으로 사용자 stop 발생하던 패턴 해결.

### Terminal state 분류 + 자동 action

| state | conclusion / mergeable | 자동 action | 사용자 보고 |
|---|---|---|---|
| **SUCCESS** | conclusion=success | admin merge (또는 normal merge) | 1줄 또는 통합 보고 |
| **FAILURE** | conclusion=failure | `gh run view --log-failed` → fix → push → re-watch | root cause 1줄 |
| **ACTION_REQUIRED (known)** | conclusion=action_required + known list 등재 | admin merge (#143 fast-pass 후 무관) | 보고 X |
| **ACTION_REQUIRED (unknown)** | conclusion=action_required + 미등재 | 사용자 보고 + 진단 | 의무 |
| **NEUTRAL / SKIPPED** | conclusion=neutral/skipped | 무시 | 보고 X |
| **BLOCKED + MERGEABLE=true** | mergeStateStatus=BLOCKED + mergeable=MERGEABLE | admin merge (enforce_admins toggle 기법) | 보고 X |
| **BLOCKED + MERGEABLE=false** | mergeStateStatus=BLOCKED + mergeable!=MERGEABLE | rebase 시도 → fail 시 보고 | 시도 후 fail 보고 |
| **UNKNOWN** | 기타 | 사용자 보고 | 의무 |

### CI watch 명령 패턴 (POSIX bash)

```bash
# 모든 terminal state 자동 분류 (SUCCESS / FAILURE / ACTION_REQUIRED / BLOCKED).
# `gh pr checks --watch` 가 8 = ACTION_REQUIRED, 0 = success.
until gh pr checks "$PR" --repo "$REPO" --watch --interval 10 >/dev/null 2>&1 || ec=$? \
      && { [ "$ec" -eq 0 ] || [ "$ec" -eq 8 ]; }; do sleep 5; done
echo "[ci-watch] terminal state reached, exit=$ec"
```

### Known ACTION_REQUIRED 패턴

| 패턴 | 원인 | 자동 action |
|---|---|---|
| `phase-gate-mergeable` on type:epic 라벨 PR | (resolved CFP-106 #143 fast-pass) → 자동 success | (의도 fast-pass — admin merge 불필요) |
| `phase-gate-mergeable` on doc-only PR (`docs/`/`wrapper/`/`*.md`) | (resolved CFP-106 #143 fast-pass) → 자동 success | (의도 fast-pass) |
| 기타 ACTION_REQUIRED | 사전 등재 X | 사용자 보고 + 진단 |

### enforce_admins toggle 기법 (BLOCKED + MERGEABLE 케이스)

```bash
gh api "repos/$REPO/branches/main/protection/enforce_admins" -X DELETE
gh pr merge "$PR" --repo "$REPO" --admin --squash --delete-branch
gh api "repos/$REPO/branches/main/protection/enforce_admins" -X POST
```

> **Note**: enforce_admins toggle 은 admin 권한 + branch protection 보존 의무. PR merge 직후 즉시 복원 (window <1초).

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
