# CFP-26 Phase 0a — Single-owner Write 권한 재분배 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ArchitectAgent · DomainAgent · PMOAgent에게 자기 owner 경로의 직접 write 권한을 부여하고, DocsAgent의 docs/** 독점을 4개 owner-path에서 해제. write queue drain 메커니즘은 보존.

**Architecture:** path-scoped permission frontmatter 4개 agent 갱신 + DocsAgent deny 4건 추가 + 정합성을 강제할 lint 1건 신설. 코드/runtime 변경 없음 — agent 권한 spec만 변경.

**Tech Stack:** YAML frontmatter (agent md), Bash (lint script), markdown (CLAUDE.md / playbook 갱신).

---

## Spec 참조

본 plan은 [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](../specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) **Phase 0a (CFP-26)** 만 구현. Phase 0b (CFP-27 lint 강화) · Phase 0c (CFP-28 검증) · Phase 1 (CFP-29 review extract) 는 별도 plan.

## File Structure (변경되는 파일과 책임)

| 파일 | 책임 | 변경 종류 |
|---|---|---|
| `agents/ArchitectAgent.md` | chief author — Change Plan + ADR direct write | frontmatter `permissions.allow` 추가, `deny` 일부 제거 |
| `agents/DomainAgent.md` | 도메인 KB direct write | frontmatter `permissions.allow` 추가, `deny` 일부 제거 |
| `agents/PMOAgent.md` | retro direct write | frontmatter `permissions.allow` 추가, `deny` 일부 제거 |
| `agents/DocsAgent.md` | Story file + GitHub lifecycle만 owner | frontmatter `permissions.deny` 4건 추가, 본문 owner 영역 표 갱신 |
| `scripts/check-write-permission-redistribution.sh` | 권한 재분배 invariant lint (NEW) | 신규 파일 |
| `CLAUDE.md` | "Write 권한" 매트릭스 + "단독 writer 원칙" 갱신 | 기존 두 섹션 갱신 |
| `docs/orchestrator-playbook.md` | DocsAgent 스폰 체크리스트 §5.1 갱신 | 4 single-owner 경로를 owner agent로 위임 명시 |
| `CHANGELOG.md` | v0.15.0 entry | 신규 entry append |
| `.claude-plugin/plugin.json` | version 0.14.3 → 0.15.0 | version 필드 |
| `docs/plugin-design.md` | "Write 권한" 섹션 갱신 (있으면) | 정합 갱신 |

---

## Task 1: Lint script 신설 — TDD foundation

invariant: "ArchitectAgent has Write/Edit on docs/change-plans/** + docs/adr/**, DomainAgent has on docs/domain-knowledge/**, PMOAgent has on docs/retros/**, DocsAgent has DENY on these 4 paths."

이 lint가 변경 후 PASS 해야 한다. 변경 전엔 FAIL.

**Files:**
- Create: `scripts/check-write-permission-redistribution.sh`

- [ ] **Step 1: Write the lint script (will fail before changes)**

Create file `scripts/check-write-permission-redistribution.sh`:

```bash
#!/usr/bin/env bash
# CFP-26 Phase 0a invariant
# 검사: single-owner 4종 docs path가 owner agent로 이관되었는가
#   - ArchitectAgent: docs/change-plans/** + docs/adr/** Edit/Write 보유
#   - DomainAgent:    docs/domain-knowledge/** Edit/Write 보유
#   - PMOAgent:       docs/retros/** Edit/Write 보유
#   - DocsAgent:      위 4 경로 Edit/Write deny 보유
set -euo pipefail
cd "$(dirname "$0")/.."

FAIL=0

# helper: extract permissions allow block from agent md
allow_block() {
  local f="$1"
  awk '
    /^---$/{c++; next}
    c==1 && /^permissions:/{in_perm=1; next}
    c==1 && in_perm && /^  allow:/{in_allow=1; next}
    c==1 && in_perm && /^  [a-z]+:/{in_allow=0}
    c==1 && in_allow{print}
    c>=2{exit}
  ' "$f"
}

deny_block() {
  local f="$1"
  awk '
    /^---$/{c++; next}
    c==1 && /^permissions:/{in_perm=1; next}
    c==1 && in_perm && /^  deny:/{in_deny=1; next}
    c==1 && in_perm && /^  [a-z]+:/{in_deny=0}
    c==1 && in_deny{print}
    c>=2{exit}
  ' "$f"
}

assert_allow() {
  local f="$1" pat="$2"
  if ! allow_block "$f" | grep -qF -- "$pat"; then
    echo "✗ $f frontmatter permissions.allow에 '$pat' 없음"
    FAIL=1
  fi
}

assert_deny() {
  local f="$1" pat="$2"
  if ! deny_block "$f" | grep -qF -- "$pat"; then
    echo "✗ $f frontmatter permissions.deny에 '$pat' 없음"
    FAIL=1
  fi
}

# ArchitectAgent
assert_allow agents/ArchitectAgent.md "Edit(docs/change-plans/**)"
assert_allow agents/ArchitectAgent.md "Write(docs/change-plans/**)"
assert_allow agents/ArchitectAgent.md "Edit(docs/adr/**)"
assert_allow agents/ArchitectAgent.md "Write(docs/adr/**)"

# DomainAgent
assert_allow agents/DomainAgent.md "Edit(docs/domain-knowledge/**)"
assert_allow agents/DomainAgent.md "Write(docs/domain-knowledge/**)"

# PMOAgent
assert_allow agents/PMOAgent.md "Edit(docs/retros/**)"
assert_allow agents/PMOAgent.md "Write(docs/retros/**)"

# DocsAgent — 4 path deny
assert_deny agents/DocsAgent.md "Edit(docs/change-plans/**)"
assert_deny agents/DocsAgent.md "Write(docs/change-plans/**)"
assert_deny agents/DocsAgent.md "Edit(docs/adr/**)"
assert_deny agents/DocsAgent.md "Write(docs/adr/**)"
assert_deny agents/DocsAgent.md "Edit(docs/domain-knowledge/**)"
assert_deny agents/DocsAgent.md "Write(docs/domain-knowledge/**)"
assert_deny agents/DocsAgent.md "Edit(docs/retros/**)"
assert_deny agents/DocsAgent.md "Write(docs/retros/**)"

if [[ $FAIL -eq 0 ]]; then
  echo "✓ CFP-26 Phase 0a — single-owner 4종 권한 재분배 invariant OK"
fi
exit $FAIL
```

- [ ] **Step 2: Make it executable and run to verify it fails**

```bash
chmod +x scripts/check-write-permission-redistribution.sh
./scripts/check-write-permission-redistribution.sh
```

Expected: FAIL with multiple "✗ ... 없음" lines (current state lacks all of these).

- [ ] **Step 3: Commit (do NOT yet apply changes)**

```bash
git add scripts/check-write-permission-redistribution.sh
git commit -m "chore(cfp-26): add write-permission-redistribution invariant lint (failing pre-state)

CFP-26 Phase 0a TDD foundation. Lint asserts ArchitectAgent/DomainAgent/PMOAgent
have direct write permissions on their owner paths and DocsAgent has deny.
Currently failing — assertions encode target state; subsequent commits in this
CFP will make the lint pass.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: ArchitectAgent — docs/change-plans + docs/adr 권한 추가

**Files:**
- Modify: `agents/ArchitectAgent.md` (frontmatter `permissions` block)

- [ ] **Step 1: Edit ArchitectAgent.md frontmatter**

현재 (lines 5-21):

```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(docs/**)
    - Write(docs/**)
```

변경 후:

```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
    - Edit(docs/change-plans/**)
    - Write(docs/change-plans/**)
    - Edit(docs/adr/**)
    - Write(docs/adr/**)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    # 주의: docs/change-plans/** + docs/adr/**는 allow에서 명시 허용 — blanket deny 제거
    # 그 외 docs/** 는 묵시 deny (allow 없음)
```

블랭킷 `Edit(docs/**)` + `Write(docs/**)` deny 라인을 **삭제**한다 (path-scoped allow와 충돌). docs/** 다른 경로는 allow 부재로 묵시 차단.

- [ ] **Step 2: Run lint — partial pass expected (4/14)**

```bash
./scripts/check-write-permission-redistribution.sh
```

Expected: 4건 PASS (ArchitectAgent allow 4종) + 10건 FAIL (나머지). 진행 OK.

- [ ] **Step 3: Update ArchitectAgent body — direct write 흐름 명시**

`agents/ArchitectAgent.md` 본문 중 "DocsAgent 이중 저장 의뢰" 언급 부분을 찾아 갱신:

```bash
grep -n "DocsAgent" agents/ArchitectAgent.md
```

각 hit에 대해:
- Change Plan 저장 책임: "DocsAgent 의뢰" → "본 에이전트가 `docs/change-plans/<slug>.md` 직접 write (CFP-26 Phase 0a)"
- ADR draft 저장 책임: "DocsAgent 의뢰" → "본 에이전트가 `docs/adr/ADR-NNN-<slug>.md` 직접 write"
- Story file §7 미러링: DocsAgent 유지 (Story file은 multi-writer)

본문 수정은 의미 보존 위주, 1-2줄 변경만. 전체 책임 흐름은 `docs/orchestrator-playbook.md` 갱신 (Task 7)에서 처리.

- [ ] **Step 4: Commit**

```bash
git add agents/ArchitectAgent.md
git commit -m "feat(cfp-26): ArchitectAgent — docs/change-plans + docs/adr direct write

Phase 0a 권한 재분배 (1/4). Change Plan + ADR이 chief author의 단일 author
산출물이므로 DocsAgent funnel 제거하고 owner direct write로 이관.
Story file §7 미러링은 DocsAgent 유지 (multi-writer).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: DomainAgent — docs/domain-knowledge 권한 추가

**Files:**
- Modify: `agents/DomainAgent.md` (frontmatter `permissions` block)

- [ ] **Step 1: Edit DomainAgent.md frontmatter**

현재 (lines 5-23):

```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(docs/**)
    - Write(docs/**)
    - WebSearch
    - WebFetch
```

변경 후:

```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
    - Edit(docs/domain-knowledge/**)
    - Write(docs/domain-knowledge/**)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - WebSearch
    - WebFetch
```

블랭킷 `Edit(docs/**)` + `Write(docs/**)` 제거. WebSearch·WebFetch는 deny 유지 (DomainAgent는 known knowns만 다루며 외부 fetch는 ResearcherAgent 책임).

- [ ] **Step 2: Run lint — partial pass expected (6/14)**

```bash
./scripts/check-write-permission-redistribution.sh
```

Expected: 6건 PASS (Architect 4 + Domain 2) + 8건 FAIL.

- [ ] **Step 3: Update DomainAgent body — direct write 명시**

본문 중 "지식 공백 해소 시 write queue에 Domain Knowledge draft 제출 → DocsAgent가 docs/domain-knowledge/<area>/<topic>.md 신규/갱신" 같은 문구 검색:

```bash
grep -n "domain-knowledge\|DocsAgent" agents/DomainAgent.md
```

각 hit를 갱신:
- "write queue에 ... draft 제출 → DocsAgent" → "`docs/domain-knowledge/<area>/<topic>.md` 직접 write (CFP-26 Phase 0a)"

- [ ] **Step 4: Commit**

```bash
git add agents/DomainAgent.md
git commit -m "feat(cfp-26): DomainAgent — docs/domain-knowledge direct write

Phase 0a 권한 재분배 (2/4). 도메인 지식 공백 해소 산출물이 단일 author이므로
DocsAgent funnel 제거하고 owner direct write로 이관.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: PMOAgent — docs/retros 권한 추가

**Files:**
- Modify: `agents/PMOAgent.md` (frontmatter `permissions` block)

- [ ] **Step 1: Edit PMOAgent.md frontmatter**

현재 (lines 5-21):

```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(docs/**)
    - Write(docs/**)
```

변경 후:

```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
    - Edit(docs/retros/**)
    - Write(docs/retros/**)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
```

- [ ] **Step 2: Run lint — partial pass expected (8/14)**

```bash
./scripts/check-write-permission-redistribution.sh
```

Expected: 8건 PASS + 6건 FAIL (DocsAgent deny 6건만 남음).

- [ ] **Step 3: Update PMOAgent body — direct write 명시**

본문 중 retro 작성 흐름 검색:

```bash
grep -n "retro\|회고\|DocsAgent" agents/PMOAgent.md
```

retro 작성 부분에서 DocsAgent 의뢰 문구를 "본 에이전트가 `docs/retros/<sprint>.md` 직접 write" 로 갱신.

- [ ] **Step 4: Commit**

```bash
git add agents/PMOAgent.md
git commit -m "feat(cfp-26): PMOAgent — docs/retros direct write

Phase 0a 권한 재분배 (3/4). 회고 산출물이 단일 author이므로 DocsAgent funnel
제거하고 owner direct write로 이관.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: DocsAgent — 4 owner-path Edit/Write deny

**Files:**
- Modify: `agents/DocsAgent.md` (frontmatter `permissions.deny` block + 본문 "소유 영역" 표)

- [ ] **Step 1: Edit DocsAgent.md frontmatter — deny 4종 추가**

현재 deny block (lines 37-49):

```yaml
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(.claude/**)
    - Write(.claude/**)
    - Edit(config/**)
    - Write(config/**)
    - Edit(deploy/**)
    - Write(deploy/**)
    - Edit(scripts/**)
    - Write(scripts/**)
```

변경 후:

```yaml
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(.claude/**)
    - Write(.claude/**)
    - Edit(config/**)
    - Write(config/**)
    - Edit(deploy/**)
    - Write(deploy/**)
    - Edit(scripts/**)
    - Write(scripts/**)
    # CFP-26 Phase 0a — single-owner path는 owner agent로 이관
    - Edit(docs/change-plans/**)
    - Write(docs/change-plans/**)
    - Edit(docs/adr/**)
    - Write(docs/adr/**)
    - Edit(docs/domain-knowledge/**)
    - Write(docs/domain-knowledge/**)
    - Edit(docs/retros/**)
    - Write(docs/retros/**)
```

- [ ] **Step 2: Run lint — full pass expected (14/14)**

```bash
./scripts/check-write-permission-redistribution.sh
```

Expected: `✓ CFP-26 Phase 0a — single-owner 4종 권한 재분배 invariant OK`

- [ ] **Step 3: Update DocsAgent body — "소유 영역" 표 갱신**

`agents/DocsAgent.md` lines 56-64 "소유 영역:" 섹션 갱신:

```markdown
소유 영역:
1. **GitHub Issue 코멘트** — 모든 에이전트의 단계별 기록 (phase prefix 10종 + Orchestrator Preflight 1종 = 총 11종)
2. **`docs/stories/<KEY>.md`** (GitHub Issue 1건당 1파일) — 컨텍스트·설계·개발 서사 SSOT (single-file, multi-writer 직렬화 owner)
3. ~~**`docs/adr/ADR-NNN-<slug>.md`** — 설계 결정 아카이브~~ → **CFP-26 Phase 0a부터 ArchitectAgent direct write**. DocsAgent는 Story §3 ADR 참조 mirroring만 책임
4. ~~**`docs/domain-knowledge/<area>/<topic>.md`** 트리~~ → **CFP-26 Phase 0a부터 DomainAgent direct write**. GitHub Discussions Q&A는 DocsAgent 유지
5. ~~**Git `docs/change-plans/<slug>.md`**~~ → **CFP-26 Phase 0a부터 ArchitectAgent direct write**. DocsAgent는 Story §7 미러링만 책임. **`docs/**` 일반 문서**(stories·migration-guide·plugin-design·orchestrator-playbook 등) write는 DocsAgent 유지
6. **`docs/retros/<sprint>.md`** ~~DocsAgent write~~ → **CFP-26 Phase 0a부터 PMOAgent direct write**
7. **GitHub Sub-issue** — Impl Manifest 파일 단위 추적 (subissue-from-impl-manifest.yml Action이 자동 생성, DocsAgent는 수동 fallback만)
8. **GitHub Milestone** — Epic 관리 (`gh api repos/*/milestones*`)
9. **GitHub Label** — phase·gate·fix·type·component·adr·hotfix·audit·impl-manifest 부착·제거
```

(취소선 사용 — 정확히 무엇이 이관됐는지 audit trail 보존)

- [ ] **Step 4: Commit**

```bash
git add agents/DocsAgent.md
git commit -m "feat(cfp-26): DocsAgent — 4 owner-path deny + 소유 영역 표 갱신

Phase 0a 권한 재분배 (4/4 — DocsAgent scope 축소 완료).
- frontmatter permissions.deny에 docs/{change-plans,adr,domain-knowledge,retros}/** 추가
- 본문 '소유 영역' 표에 이관 사실 명시 (취소선 + CFP-26 ref)
- Story file (multi-writer) · GitHub Issue/PR/comment · label · milestone은 DocsAgent 유지

invariant lint check-write-permission-redistribution.sh 14/14 PASS.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: CLAUDE.md — Write 권한 매트릭스 + 단독 writer 원칙 갱신

**Files:**
- Modify: `CLAUDE.md` (lines ~440-456 — "Write 권한 (path-scoped)" + "문서 write 단독 writer 원칙" 두 섹션)

- [ ] **Step 1: 위치 확인**

```bash
grep -n "### Write 권한\|### 문서 write 단독 writer" CLAUDE.md
```

- [ ] **Step 2: "Write 권한 (path-scoped)" 섹션 갱신**

현재:

```markdown
### Write 권한 (path-scoped — 각 agent md frontmatter가 SSOT)

**Core 기본 경로** (consumer overlay가 확장):
- **Write 권한 있음**:
  - `role: dev` 에이전트별 개별 scoping (core: DeveloperAgent `src/**` 기본 + `tests/**`·`docs/**` deny, ...)
  - QADev `role: qa` (`tests/**` allow + `src/**` deny — production 코드 직접 수정 금지)
  - **DocsAgent(`docs/**` + `.claude-work/doc-queue/**` + GitHub MCP write 도구 전용, ...)**
- **Write queue 의뢰 권한** (`.claude-work/doc-queue/**`만): RequirementsPLAgent, DomainAgent, PMOAgent, ArchitectPLAgent, ArchitectAgent, ...
```

변경 후:

```markdown
### Write 권한 (path-scoped — 각 agent md frontmatter가 SSOT)

**Core 기본 경로** (consumer overlay가 확장):
- **Write 권한 있음**:
  - `role: dev` 에이전트별 개별 scoping (core: DeveloperAgent `src/**` 기본 + `tests/**`·`docs/**` deny, DataEng 프로젝트별 데이터 계층 경로, InfraEngineer `deploy/**`·`config/**`·`scripts/**`; preset·overlay가 경로 재정의 — preset 예: `presets/webapp/agents/{Backend,Frontend}DeveloperAgent`)
  - QADev `role: qa` (`tests/**` allow + `src/**` deny — production 코드 직접 수정 금지)
  - **DocsAgent**: `docs/**` (단, `docs/{change-plans,adr,domain-knowledge,retros}/**` 4종은 deny — CFP-26 Phase 0a부터 owner agent로 이관) + `.claude-work/doc-queue/**` + GitHub MCP write 도구 전용 + `src`·`tests`·`.claude`·`config`·`deploy`·`scripts` 명시 deny
  - **ArchitectAgent**: `docs/change-plans/**` + `docs/adr/**` (CFP-26 Phase 0a — chief author direct write)
  - **DomainAgent**: `docs/domain-knowledge/**` (CFP-26 Phase 0a — 도메인 KB direct write)
  - **PMOAgent**: `docs/retros/**` (CFP-26 Phase 0a — retro direct write)
- **Write queue 의뢰 권한만** (`.claude-work/doc-queue/**`): RequirementsPLAgent, ArchitectPLAgent, SecurityArchitectAgent, TestContractArchitectAgent, DataMigrationArchitectAgent, CodebaseMapper, Refactor, DesignReviewPL, CodeReviewPL, SecurityTestPL, ClaudeReviewAgent, CodexReviewAgent, DeveloperPLAgent, RequirementsAnalyst, Researcher, TestAgent — Story file·GitHub comment 등 multi-writer / lifecycle 책임은 여전히 DocsAgent 경유
- **외부 도구 wrapper**: RequirementsAnalyst(`Bash(codex exec *)`), CodexReviewAgent(`Bash(node *)` codex-companion 실행 + `WebSearch`·`WebFetch` CVE/OWASP 조회), ClaudeReviewAgent(`WebSearch`·`WebFetch` 보안 lane CVE 조회), SecurityTestPL(`Bash(gh api repos/*)` 1차 layer alerts fetch), DocsAgent(`Bash(gh api repos/*/milestones*)`, `Bash(gh api repos/*/discussions*)`, `Bash(gh api graphql*)`, `Bash(mkdir/ls/rm .claude-work/doc-queue*)`)
```

(주: ArchitectAgent · DomainAgent · PMOAgent를 "Write queue 의뢰 권한만" 리스트에서 제거 — 이들은 이제 직접 write 권한 보유)

- [ ] **Step 3: "문서 write 단독 writer 원칙" 섹션 갱신**

현재:

```markdown
### 문서 write 단독 writer 원칙

**DocsAgent만이 GitHub Issue/PR/comment·repo file `docs/**` write 가능**. 나머지 에이전트는 모두 문서 write 권한 없음. 문서 작업은 전원 **file-based write queue**(`.claude-work/doc-queue/<story>/`)에 의뢰 파일을 append → Orchestrator가 DocsAgent 스폰 시 drain. 상세는 playbook §11.

- DocsAgent 권한은 path-scoped: `Edit(docs/**)`, `Write(docs/**)`, `Edit(.claude-work/doc-queue/**)`, `Write(.claude-work/doc-queue/**)` + GitHub MCP write 도구 + gh CLI Bash fallback
- 문서화 표준(GitHub Issue 코멘트 phase prefix, Story file 섹션 규격, Change Plan 템플릿, ADR 템플릿, FIX Ledger 스키마, Impl Manifest 스키마)은 [`agents/DocsAgent.md`](agents/DocsAgent.md) SSOT
- 다른 에이전트 md에는 "문서화 표준은 DocsAgent.md 참조" 1줄만
```

변경 후:

```markdown
### 문서 write 책임 분담 (CFP-26 Phase 0a 후)

**DocsAgent + 3 owner agent 분담 모델**. `docs/**` 영역은 둘로 나뉜다:

1. **Single-owner 직접 write** (CFP-26 Phase 0a부터):
   - **ArchitectAgent**: `docs/change-plans/**` + `docs/adr/**` (chief author 산출물)
   - **DomainAgent**: `docs/domain-knowledge/**` (도메인 KB)
   - **PMOAgent**: `docs/retros/**` (회고)
   - 이 4 path는 DocsAgent deny — owner agent가 직접 write
2. **DocsAgent 단독 owner** (multi-writer 직렬화 + GitHub lifecycle):
   - `docs/stories/<KEY>.md` (multi-writer 직렬화 — RequirementsPL §2-6, ArchitectAgent §7 미러링, DeveloperPL §8/§8.5, ReviewPLs §9, TestAgent §10 결과, FIX Ledger §10 schema, PMO §11 회고 pointer)
   - `docs/**` 그 외 일반 문서 (orchestrator-playbook, plugin-design, migration-guide, consumer-guide 등)
   - GitHub Issue/PR/comment (phase prefix 11종) · PR/Issue body create/update (`Closes #N` keyword) · label 부착(gate/phase/fix) · sub-issue 수동 fallback · milestone · gh api fallback
3. **나머지 에이전트** (Write queue 의뢰만): Story file 섹션 갱신·GitHub comment 게시 등 multi-writer/lifecycle 영역은 `.claude-work/doc-queue/<story>/`에 의뢰 → Orchestrator가 DocsAgent 스폰 시 drain. 상세는 playbook §11

문서화 표준(GitHub Issue 코멘트 phase prefix, Story file 섹션 규격, Change Plan 템플릿, ADR 템플릿, FIX Ledger 스키마, Impl Manifest 스키마)은 [`agents/DocsAgent.md`](agents/DocsAgent.md) SSOT. 4 single-owner doc 템플릿은 [`templates/`](templates/) (change-plan / adr / domain-knowledge schema / retro schema). owner agent는 본인 owner path write 시 해당 템플릿 schema 준수 필수 — `scripts/check-write-permission-redistribution.sh` (CFP-26) + 향후 frontmatter/section schema lint (CFP-27)에서 강제.
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(cfp-26): CLAUDE.md Write 권한 매트릭스 + 단독 writer 원칙 갱신

Phase 0a 권한 재분배 SSOT 갱신.
- '단독 writer 원칙' → '책임 분담' 으로 prose 변경
- 4 single-owner doc은 owner direct write, multi-writer + GitHub lifecycle은
  DocsAgent 유지 — 두 모델 명시
- ArchitectAgent · DomainAgent · PMOAgent를 'write queue 의뢰만' 리스트에서 제거

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: orchestrator-playbook.md — DocsAgent 스폰 체크리스트 갱신

**Files:**
- Modify: `docs/orchestrator-playbook.md` (§5.1 단계 종료 시 DocsAgent 스폰 체크리스트 + DocsAgent 관련 흐름 라인)

- [ ] **Step 1: 위치 확인**

```bash
grep -n "### 5.1 단계 종료 시 DocsAgent\|file 변경은 \*\*DocsAgent 독점\|domain-knowledge\|change-plans\|retros" docs/orchestrator-playbook.md
```

- [ ] **Step 2: §5.1 체크리스트 표 갱신**

현재 표는 "트리거 / 갱신 섹션 / Orchestrator가 DocsAgent에 전달할 내용" 컬럼. CFP-26 후 갱신 대상:

- **DomainAgent 지식 공백 발견 시** trigger row → "DocsAgent 의뢰" → "DomainAgent 직접 write (owner)" 로 변경
- **ArchitectAgent Change Plan 확정 시** trigger row → "DocsAgent 이중 저장" → "ArchitectAgent가 `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` 직접 write, Story §7 미러링만 DocsAgent 의뢰" 로 변경
- **PMOAgent 회고 시** trigger row → "DocsAgent 의뢰" → "PMOAgent 직접 write" 로 변경

표의 정확한 위치는 §5.1 section 안. trigger 컬럼 키워드로 식별.

- [ ] **Step 3: §5.1 직후 prose "file 변경은 DocsAgent 독점" 갱신**

해당 라인을 다음으로 변경:

```markdown
- file 변경 권한 분담 (CFP-26 Phase 0a 이후):
  - `docs/change-plans/**` + `docs/adr/**` → **ArchitectAgent direct**
  - `docs/domain-knowledge/**` → **DomainAgent direct**
  - `docs/retros/**` → **PMOAgent direct**
  - `docs/stories/**` (multi-writer) + `docs/**` 그 외 + GitHub Issue/PR/comment + label → **DocsAgent 단독**
  - 그 외 모든 에이전트는 write queue 의뢰만
```

- [ ] **Step 4: Commit**

```bash
git add docs/orchestrator-playbook.md
git commit -m "docs(cfp-26): orchestrator-playbook §5.1 — DocsAgent 스폰 체크리스트 갱신

Phase 0a 권한 재분배 행동 SSOT 갱신.
- §5.1 trigger 표에서 4 single-owner trigger를 owner agent direct로 명시
- 'file 변경은 DocsAgent 독점' prose를 분담 모델로 갱신

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: plugin.json version bump + CHANGELOG entry + plugin-design.md 갱신

**Files:**
- Modify: `.claude-plugin/plugin.json` (version 0.14.3 → 0.15.0)
- Modify: `CHANGELOG.md` (신규 [0.15.0] entry append at top)
- Modify: `docs/plugin-design.md` (Write 권한 관련 섹션 정합 갱신)

- [ ] **Step 1: plugin.json version bump**

현재:

```json
{
  "name": "codeforge",
  "version": "0.14.3",
  ...
}
```

변경:

```json
{
  "name": "codeforge",
  "version": "0.15.0",
  ...
}
```

(BREAKING — minor 0.14 → 0.15. v1.0 이전이므로 minor bump가 breaking 표현 — codeforge convention)

- [ ] **Step 2: CHANGELOG.md — [0.15.0] entry append at top**

현재 맨 위 [0.14.3] 엔트리 위에 다음 entry 추가:

```markdown
## [0.15.0] - 2026-04-28

### CFP-26 — Phase 0a · Single-owner write 권한 재분배 (BREAKING — DocsAgent scope 축소)

**BREAKING (v1.0 이전 minor 표기)**. DocsAgent 단독 writer 모델을 "DocsAgent + 3 owner agent 분담"으로 변경.
4 single-owner 문서 경로(`docs/{change-plans,adr,domain-knowledge,retros}/**`)가 owner agent direct write로 이관.
DocsAgent는 Story file (multi-writer 직렬화) + GitHub Issue/PR/comment·label·body·milestone 책임 유지.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25).

### Changed
- `agents/ArchitectAgent.md` frontmatter — `docs/change-plans/**` + `docs/adr/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/DomainAgent.md` frontmatter — `docs/domain-knowledge/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/PMOAgent.md` frontmatter — `docs/retros/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/DocsAgent.md` frontmatter — 4 owner-path deny 추가, "소유 영역" 표 갱신 (취소선으로 이관 audit trail 보존)
- `CLAUDE.md` "Write 권한 (path-scoped)" + "문서 write 책임 분담" 섹션 (이전 "단독 writer 원칙") 갱신
- `docs/orchestrator-playbook.md` §5.1 — 단계 종료 시 DocsAgent 스폰 체크리스트의 4 single-owner trigger를 owner direct로 변경

### Added
- `scripts/check-write-permission-redistribution.sh` — Phase 0a invariant lint (4 owner-path direct write + DocsAgent deny 14 assertion)

### Why
CFP-21 (DataMigrationArchitectAgent — 6th deputy) 추가가 9+ 파일 동시 갱신 + BREAKING bump을 일으킨 사례에서, codeforge 본체 revision 비용이 monolith 모놀리식 single-writer 모델 때문에 과도하게 상승함이 명확. DocsAgent의 funnel 가치(multi-writer 직렬화·GitHub lifecycle 일관성·comment phase prefix)는 보존하되, single-author 산출물은 owner agent direct write로 이관해 funnel 부담을 줄이고, 향후 plugin 추출(CFP-29 codeforge-review)의 cross-plugin 결합점을 narrow하게 한다.

설계 협업: Claude Opus 4.7 + Codex GPT-5.4 (4 라운드, 라운드 4에서 Path A 합의). 거부된 대안: Path B (DocsAgent 완전 제거 — multi-writer 직렬화 깨짐), Path C (skill 다운그레이드 — knowledge 보존하지만 enforcement 잃음).

### Migration
**BREAKING — consumer 영향**:
- consumer overlay에서 ArchitectAgent · DomainAgent · PMOAgent 권한을 추가로 확장하던 경우, frontmatter `permissions.allow` 항목이 **core와 concat+dedup** 되므로 변경 없음 (overlay 메커니즘이 새 항목 자동 흡수)
- consumer overlay가 DocsAgent 권한을 명시 override 하던 경우(드뭄), `docs/{change-plans,adr,domain-knowledge,retros}/**` 4 path deny가 추가됨에 유의 — overlay에서 다시 allow를 명시하면 path-scoped allow가 우선
- 자동화: `scripts/check-write-permission-redistribution.sh`가 invariant 강제. CI에서 호출 권장

자세한 사항: 본 spec (CFP-25) §1·§5 참조.
```

- [ ] **Step 3: docs/plugin-design.md 정합 갱신**

`docs/plugin-design.md`에 Write 권한 관련 섹션이 있으면 갱신:

```bash
grep -n "DocsAgent\|단독 writer\|write queue\|docs/\*\*" docs/plugin-design.md
```

발견 hit가 "DocsAgent 단독 writer" 또는 "docs/** 단독 write" 표현이면 다음으로 갱신:

```markdown
- **문서 write 책임 분담** (CFP-26 Phase 0a 이후): DocsAgent + 3 owner agent (ArchitectAgent / DomainAgent / PMOAgent). 상세는 [CLAUDE.md](../CLAUDE.md) "문서 write 책임 분담" 섹션 + [agents/DocsAgent.md](../agents/DocsAgent.md) "소유 영역" 표 SSOT
```

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/plugin.json CHANGELOG.md docs/plugin-design.md
git commit -m "chore(cfp-26): v0.15.0 release — Phase 0a write 권한 재분배 BREAKING

- plugin.json version 0.14.3 → 0.15.0 (BREAKING under v1.0 minor convention)
- CHANGELOG [0.15.0] entry — Changed/Added/Why/Migration 4 sections
- docs/plugin-design.md 정합 갱신 (single writer → 분담 모델)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Final verification + marketplace cross-repo sync 준비

**Files:**
- (No new file changes) Run lint + verify state

- [ ] **Step 1: invariant lint 최종 확인**

```bash
./scripts/check-write-permission-redistribution.sh
./scripts/check-agent-frontmatter.sh
./scripts/check-doc-links.sh
./scripts/check-no-atlassian.sh
```

Expected: 모두 PASS.

- [ ] **Step 2: git log 검증**

```bash
git log --oneline -10
```

Expected: 본 CFP의 commit 8건 (Task 1~8)이 main 위에 순서대로 쌓여있어야 함.

- [ ] **Step 3: cross-repo sync 의무 확인 (CFP-24 정책)**

`.claude-plugin/plugin.json`의 mirrored 필드(`name` · `version` · `description` · `author`) 변경 확인:

- `name`: codeforge (변경 없음)
- `version`: 0.14.3 → 0.15.0 (변경됨)
- `description`: (변경 없음 — 본 CFP는 description touch 안 함)
- `author`: (변경 없음)

→ `version` 변경이 mirrored 필드 → **mclayer/marketplace 동기화 PR 필요**.

다음 단계 (별도 PR, 본 CFP 머지 직후):

```bash
# mclayer/marketplace 리포 clone (별도 워크스페이스)
gh repo clone mclayer/marketplace
# .claude-plugin/marketplace.json의 plugins[name=codeforge].version을 0.15.0으로 갱신
# sync PR open
```

본 plan 범위에선 codeforge 측 PR commit까지만 포함. marketplace sync PR은 PR review·merge 직후 별도 처리 (본 plan §10.6 open decisions 참조).

- [ ] **Step 4: 본 CFP 통합 commit log 요약 (no commit, 검증만)**

기대 commit 순서:
1. `chore(cfp-26): add write-permission-redistribution invariant lint (failing pre-state)`
2. `feat(cfp-26): ArchitectAgent — docs/change-plans + docs/adr direct write`
3. `feat(cfp-26): DomainAgent — docs/domain-knowledge direct write`
4. `feat(cfp-26): PMOAgent — docs/retros direct write`
5. `feat(cfp-26): DocsAgent — 4 owner-path deny + 소유 영역 표 갱신`
6. `docs(cfp-26): CLAUDE.md Write 권한 매트릭스 + 단독 writer 원칙 갱신`
7. `docs(cfp-26): orchestrator-playbook §5.1 — DocsAgent 스폰 체크리스트 갱신`
8. `chore(cfp-26): v0.15.0 release — Phase 0a write 권한 재분배 BREAKING`

- [ ] **Step 5: PR open (사용자 권한, 본 plan 범위 밖 안내만)**

본 plan은 commit까지. PR 생성·marketplace sync PR open은 사용자 또는 후속 단계.

PR title 권장: `feat(cfp-26): Phase 0a · single-owner write 권한 재분배 (BREAKING v0.15.0)`

PR body에 다음 포함:
- 본 plan 링크 (`docs/superpowers/plans/2026-04-28-cfp-26-phase-0a-write-permission-redistribution.md`)
- 본 spec 링크 (`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`)
- "marketplace sync PR 후속 의무" 명시 (CFP-24 정책)
- BREAKING note (consumer migration)

---

## 자체 점검 (Self-Review)

본 plan을 spec과 대조해 누락·placeholder·일관성 이슈 검토:

**1. Spec coverage** — spec §9 "Migration / CFP sequencing"의 CFP-26 항목:

> CFP-26 (Phase 0a) : Single-owner 4종 권한 이관
>   - ArchitectAgent: docs/change-plans/** + docs/adr/** Write    ✓ Task 2
>   - DomainAgent: docs/domain-knowledge/** Write                  ✓ Task 3
>   - PMOAgent: docs/retros/** Write                               ✓ Task 4
>   - DocsAgent: 위 4 path deny 추가                                ✓ Task 5
>   - CLAUDE.md "Write 권한" 매트릭스 갱신                          ✓ Task 6
>   - docs/orchestrator-playbook.md 갱신                            ✓ Task 7
>   - CHANGELOG (minor — v0.15.0)                                  ✓ Task 8

전 항목 cover. Task 1(lint)과 Task 9(verification)은 spec에 명시 안 됐지만 TDD discipline + invariant 강제 위해 추가 (정당화).

**2. Placeholder scan** — "TODO"·"TBD"·"이 부분은 채울 것" 등 placeholder 0건. 모든 step에 concrete 실행 명령 + 예상 결과 명시. ✓

**3. Type consistency** — agent 권한 항목 표기가 모든 task에서 `Edit(docs/<path>/**)` + `Write(docs/<path>/**)` pair로 일관. ✓

**4. Open issue**: spec §10.6에 명시한 "Claude Code permission schema의 path-scoped deny 정확 표기" — 본 plan은 기존 DocsAgent.md의 `Edit(.claude/**)` deny 패턴을 그대로 따라 `Edit(docs/<path>/**)` 표기 사용. 검증은 invariant lint(Task 1)가 string match로 강제 — schema 정확성은 별도 (Claude Code가 권한 거부 정상 동작 여부는 CFP-28 검증 단계에서 dogfood로 확인).

**5. Risk fix**: Phase 0a 변경이 기존 multi-writer Story file 갱신 흐름을 깨뜨리지 않는지 — DocsAgent의 `Edit(docs/**)` + `Write(docs/**)` 블랭킷 allow는 유지되며 `docs/stories/**` · `docs/**` 일반 문서 write는 정상 동작. 4 owner-path만 deny. ✓

---

## 다음 plan (참조)

- **CFP-27 Phase 0b**: lint 강화 (`scripts/check-agent-frontmatter.sh` + `check-doc-links.sh` 확장 — 4 owner doc 종 frontmatter·섹션 schema 검증). 별도 plan으로 작성 예정
- **CFP-28 Phase 0c**: 1-2 real Story 실행 검증. 별도 plan
- **CFP-29 Phase 1**: codeforge-review plugin 추출. 별도 plan
