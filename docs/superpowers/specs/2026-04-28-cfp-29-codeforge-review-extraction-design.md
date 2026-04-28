---
spec_id: cfp-29
title: codeforge-review plugin 추출 (Phase 1 — staged ε strategic payoff)
status: Draft
date: 2026-04-28
authors:
  - User (Q4 hard cut 결정)
  - Claude (Opus 4.7) — synthesis
  - CFP-25 spec (parent design — Phase 1 outline)
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker 통합. 본 추출이 그 결정을 plugin 경계로 보존)
  - ADR-008 (NEW — Inter-plugin Contract Versioning)
related_files:
  - .claude-plugin/plugin.json (codeforge core — version bump 0.16.0 → 0.17.0 BREAKING)
  - agents/{DesignReviewPL,CodeReviewPL,SecurityTestPL,ClaudeReview,CodexReview}Agent.md (5 file 삭제 — codeforge-review repo로 이동)
  - templates/review-pl-base.md (삭제)
  - templates/review-checklists/{design,code,security}.md (3 file 삭제)
  - CLAUDE.md (Inter-plugin Contract 섹션 신규 + 의존성 목록 갱신 + ASCII 다이어그램 갱신)
  - docs/orchestrator-playbook.md (review references → "codeforge-review plugin")
  - docs/plugin-design.md (Stage 1 history + agent count)
  - docs/inter-plugin-contracts/review-verdict-v1.md (NEW)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md (NEW)
  - mclayer/plugin-codeforge-review/* (NEW repo — 외부 GitHub 리포)
  - mclayer/marketplace/.claude-plugin/marketplace.json (codeforge-review 신규 entry + codeforge version sync)
---

## 0. 사용자 원문 (verbatim)

> 그냥 묻지말고 쭉 진행해

CFP-25 spec Phase 1 + Q4 hard cut(2026-04-28) 결정 이후 명시 confirm. 본 spec은 Phase 1을 끝까지 자율 실행하기 위한 design freeze.

## 1. 컨텍스트

### 1.1 parent spec (CFP-25)

[CFP-25 design spec](2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) §4.2 "Phase 1 — codeforge-review plugin 추출" 가 high-level outline 정의. Phase 0a (CFP-26) + Phase 0b (CFP-27) 는 이미 완료 + dogfooded · 머지됨. 본 spec은 CFP-25 deferred specifics 5건을 결정한다:

| Deferred item | 결정 |
|---|---|
| Plugin manifest dependency 메커니즘 | **SessionStart hook check** (codeforge가 4 plugin에 의존하는 기존 패턴 답습 — 이미 dogfooded) |
| regen-agents.sh multi-plugin awareness | **각 plugin이 자체 hook 보유** — 자기 plugin root에서만 자기 agent 처리. sibling discovery 메커니즘 불필요 |
| review_verdict v1 contract 위치 | **codeforge core CLAUDE.md "Inter-plugin Contract" 신규 섹션** + `docs/inter-plugin-contracts/review-verdict-v1.md` 상세 schema |
| Consumer migration 강도 | **Hard cut** (Q4 결정) — codeforge v0.17.0이 5 agent + base + 3 checklist 즉시 삭제. consumer는 두 plugin 모두 등록 의무 |
| codeforge core version 정책 | **0.17.0** (minor BREAKING). 1.0.0은 staged ε 완료 milestone (Phase 2 deferred 결정 후) |

### 1.2 staged ε strategic payoff

CFP-25 §1 동기 인용:

> "codeforge 개정할 때 비용이 너무 크다. 유사하거나 중복되는 역할의 agent를 plugin으로 분리하면 본체가 안 흔들리지 않겠나"

본 CFP가 staged ε의 **첫 plugin 추출**. 이후 추가 추출 (arch-deputies / req-deputies)은 contract 안정성 측정 후 조건부 (CFP-25 §10.2 — "Phase 2가 영원히 안 올 가능성").

본 추출의 검증 목표 (Phase 1 측정 기준):
- 2-3 CFP 사이클 동안 codeforge core bump 빈도 측정
- codeforge-review 자체 bump 빈도 측정 (independent cadence 검증)
- review_verdict v1 contract 위반 발생 0건
- gate label 부착 실패 0건

## 2. 합의된 strategy: Hard cut + per-plugin hook + SessionStart dependency check

세 결정이 design 전반을 좌우한다:

1. **Hard cut**: codeforge v0.17.0 머지 직후 5 agent + base + 3 checklist 즉시 삭제. 점진 deprecation 없음
2. **Per-plugin hook**: codeforge-review가 자체 `overlay/hooks/regen-agents.sh` 보유 (codeforge core의 hook 패턴 복제). consumer 측 SessionStart에서 두 hook이 각자 자기 plugin root만 처리 — 충돌 없음
3. **SessionStart dependency check**: codeforge-review의 SessionStart hook이 codeforge core 설치 여부를 verify. 미설치 시 install 안내 + fail-fast

## 3. 거부된 대안

### 3.1 Soft transition (deprecation 기간)

거부 사유: hard cut이 staged ε 모델 변화의 명료한 cut 표시. soft transition은 일정 기간 양쪽 install 가능 → drift 위험 + consumer 혼동.

### 3.2 Subdirectory plugin (단일 repo, 2 plugin)

거부 사유: CFP-25 §4.2 "1 plugin = 1 repo 관례 유지" + Codex 라운드 1 verdict ("monorepo workspace는 더 복잡한 문제"). marketplace.json은 plugin 단위 entry — repo 단위가 자연스러움.

### 3.3 codeforge core가 5 agent fallback 유지 + codeforge-review가 우선순위 override

거부 사유: overlay merge 우선순위 정책이 새로 필요 + 두 곳 동기화 부담 + dogfooding 가치 약화 (어느 쪽이 SSOT인지 모호).

### 3.4 Manifest field로 plugin dependency 표현

거부 사유: Claude Code plugin schema가 dependency field 표준 부재. SessionStart hook 패턴은 codeforge가 codex/superpowers/claude-md-management/github 4 plugin 의존을 이미 dogfood — extension는 same pattern.

## 4. Architecture

### 4.1 Repo 구조

```
mclayer/
├── plugin-codeforge/              # existing — v0.17.0 BREAKING (5 agent 삭제)
│   ├── agents/                    # 19 agent (24 - 5 review)
│   ├── templates/                 # change-plan / adr / story-page-structure /
│   │                              # impl-manifest / domain-knowledge / retro /
│   │                              # github-* (review-pl-base + review-checklists 삭제)
│   ├── docs/inter-plugin-contracts/  # NEW
│   │   └── review-verdict-v1.md   # NEW
│   ├── docs/adr/
│   │   └── ADR-008-inter-plugin-contract-versioning.md  # NEW
│   ├── CLAUDE.md                  # § "Inter-plugin Contract" 추가 + 의존성 목록 + 다이어그램
│   └── ...
│
├── plugin-codeforge-review/       # NEW repo — v0.1.0 (initial)
│   ├── .claude-plugin/plugin.json # name=codeforge-review, version=0.1.0
│   ├── agents/                    # 5 review agent (이동)
│   ├── templates/
│   │   ├── review-pl-base.md      # 이동
│   │   └── review-checklists/     # 이동 (3 checklists)
│   ├── overlay/hooks/
│   │   ├── regen-agents.sh        # 자체 hook (codeforge core 패턴 복제)
│   │   └── session-start-deps-check.sh  # codeforge core 설치 verify
│   ├── README.md                  # consumer install + codeforge core dep
│   ├── CHANGELOG.md               # v0.1.0 initial
│   └── docs/
│       └── adr/
│           └── ADR-001-extracted-from-codeforge.md  # 추출 사실 + verdict v1 contract 동결 시점
│
└── marketplace/                   # existing
    └── .claude-plugin/marketplace.json
        # plugins[]:
        #   - codeforge (version 0.16.0 → 0.17.0)
        #   - codeforge-review (NEW, version 0.1.0)
```

### 4.2 추출 대상 정확 매핑

**codeforge core에서 삭제** (8 files):

```
agents/DesignReviewPLAgent.md
agents/CodeReviewPLAgent.md
agents/SecurityTestPLAgent.md
agents/ClaudeReviewAgent.md
agents/CodexReviewAgent.md
templates/review-pl-base.md
templates/review-checklists/design.md
templates/review-checklists/code.md
templates/review-checklists/security.md
```

**codeforge-review로 이동** (동일 8 files, 같은 path 구조):

```
agents/DesignReviewPLAgent.md
agents/CodeReviewPLAgent.md
agents/SecurityTestPLAgent.md
agents/ClaudeReviewAgent.md
agents/CodexReviewAgent.md
templates/review-pl-base.md
templates/review-checklists/design.md
templates/review-checklists/code.md
templates/review-checklists/security.md
```

**codeforge core에 새로 생기는 file** (3 files):

```
docs/inter-plugin-contracts/review-verdict-v1.md  # 상세 schema
docs/adr/ADR-008-inter-plugin-contract-versioning.md
docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md  # 본 spec
docs/superpowers/plans/2026-04-28-cfp-29-phase-1-codeforge-review-extract.md     # plan
```

**codeforge core에서 갱신되는 file** (4 files):

```
.claude-plugin/plugin.json   # version 0.16.0 → 0.17.0
CLAUDE.md                    # Inter-plugin Contract 섹션 + 의존성 목록 + 다이어그램
docs/orchestrator-playbook.md  # review reference → "codeforge-review plugin"
docs/plugin-design.md        # Stage 1 history + agent count 24 → 19
CHANGELOG.md                 # [0.17.0] BREAKING entry
docs/migration-guide.md      # v0.16 → v0.17 섹션
```

**codeforge-review 신규 file**:

```
.claude-plugin/plugin.json   # name=codeforge-review, version=0.1.0
overlay/hooks/regen-agents.sh
overlay/hooks/session-start-deps-check.sh
README.md
CHANGELOG.md  (v0.1.0 initial)
docs/adr/ADR-001-extracted-from-codeforge.md
```

### 4.3 Inter-plugin Contract — review_verdict v1

본 contract는 codeforge core가 codeforge-review의 PL agents에 review packet을 주입하고, PL이 normalized verdict를 반환할 때의 양방향 schema. CLAUDE.md "## Inter-plugin Contract" 섹션 + `docs/inter-plugin-contracts/review-verdict-v1.md` 양쪽에 명시.

#### 3.1 review_packet (core → review plugin)

기존 `templates/review-pl-base.md` §2 schema 그대로 (codeforge-review로 이동). 필수/선택 필드 매트릭스도 동일.

```yaml
review_packet:
  contract_version: "1.0"
  lane: design | code | security
  checklist_path: <path within codeforge-review>
  scope_globs: [...]
  category_enum: [...]
  severity_overrides: [...]
  story_key: <STORY_KEY>
  related_adrs: [...]
  # security lane only:
  first_layer_findings: { dependabot, codeql, secret_scan, push_protection }
```

#### 3.2 review_verdict (review plugin → core)

신규 — 본 CFP에서 v1 동결. PL이 워커 결과 종합 후 Orchestrator에 return:

```yaml
review_verdict:
  contract_version: "1.0"          # 향후 변경 시 v2 신설 + ADR
  lane: design | code | security
  story_key: <STORY_KEY>
  iteration: <int>                 # FIX 카운터 — core가 §10 FIX Ledger sync에 사용
  status: PASS | FIX | FIX_DISCRETIONARY  # review-pl-base.md §3 SSOT 준수
  findings:
    - severity: P0 | P1 | P2
      category: <enum from review_packet.category_enum>
      file: <path>
      line: <int>
      evidence: <markdown>
      suggestion: <markdown>
  summary_for_story_section_9: <markdown>  # core(DocsAgent)가 Story §9 append
  summary_for_pr_comment: <markdown>       # core(DocsAgent)가 phase prefix 적용해 PR comment 게시
  next_gate_label: gate:design-review-pass | gate:security-test-pass | null
                                   # PASS 시 core가 부착. null이면 gate 부착 안 함 (FIX 케이스)
```

#### 3.3 contract versioning 룰 (ADR-008)

- v1.x backward-compat 변경: 새 선택 필드 추가만 가능 (review plugin과 core 양쪽 무관). 예: `findings[].suggested_fix_diff` 추가
- v2.0 BREAKING 변경: 필수 필드 변경·제거·rename. 양쪽 plugin 동시 bump 필수 + ADR 신설
- contract_version mismatch 처리: review plugin의 verdict가 core가 모르는 version 반환 시 → core가 ESCALATE + 사용자 안내 (compat 매트릭스 부재 fallback 금지)

### 4.4 SessionStart dependency check

codeforge-review의 `overlay/hooks/session-start-deps-check.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# codeforge-review는 codeforge core 의존
# core 미설치 시 본 plugin은 동작 불가 — fail-fast + install 안내

CORE_PLUGIN_PATH="${CLAUDE_PLUGIN_DIR:-$HOME/.claude/plugins/cache}/mclayer/codeforge"

if [[ ! -d "$CORE_PLUGIN_PATH" ]]; then
  cat >&2 <<EOF
✗ codeforge-review plugin 의존성 누락

본 plugin은 codeforge core plugin이 설치되어 있어야 동작합니다.

설치 방법:
  /plugins install codeforge@mclayer

또는 ~/.claude/settings.json에서 enabledPlugins.codeforge@mclayer = true

자세한 사항: https://github.com/mclayer/plugin-codeforge-review#dependencies
EOF
  exit 1
fi

# core 설치는 OK — 이제 자체 regen-agents.sh 실행 (체인)
exec "$(dirname "$0")/regen-agents.sh"
```

### 4.5 codeforge-review의 자체 regen-agents.sh

```bash
#!/usr/bin/env bash
# codeforge-review plugin 자체 agent regen
# codeforge core의 overlay/hooks/regen-agents.sh 패턴 복제 (자기 root만 iterate)

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONSUMER_AGENTS_DIR=".claude/agents"

mkdir -p "$CONSUMER_AGENTS_DIR"

for core_agent in "$PLUGIN_ROOT/agents/"*.md; do
  basename=$(basename "$core_agent")
  overlay_agent=".claude/_overlay/agents/$basename"
  output="$CONSUMER_AGENTS_DIR/$basename"

  # codeforge core merge.py 재사용 (consumer가 codeforge core 설치 의무이므로 가용)
  CORE_MERGE_PY="${CLAUDE_PLUGIN_DIR:-$HOME/.claude/plugins/cache}/mclayer/codeforge/overlay/hooks/merge.py"

  if [[ -f "$overlay_agent" ]]; then
    python3 "$CORE_MERGE_PY" "$core_agent" "$overlay_agent" > "$output"
  else
    python3 "$CORE_MERGE_PY" "$core_agent" > "$output"
  fi
done
```

핵심: codeforge-review가 **codeforge core의 merge.py를 재사용**. 자체 merge.py 복제 X — DRY. consumer가 core 설치 의무라는 dependency check가 이를 보장.

## 5. Migration sequencing (β 안 — review-first, core-cleanup-second)

```
Step 1 — mclayer/plugin-codeforge-review repo 신설
  - GitHub repo create (mclayer/plugin-codeforge-review, public)
  - 5 agent + base + 3 checklist을 codeforge에서 단순 copy (git history 보존 안 함 —
    "initial extract from mclayer/plugin-codeforge@<sha>" 첫 commit으로 attribution)
  - .claude-plugin/plugin.json (v0.1.0)
  - SessionStart hook (deps check) + regen-agents.sh
  - README + CHANGELOG (v0.1.0 initial) + ADR-001-extracted-from-codeforge.md
  - main 브랜치에 commit + push (별도 PR 없이 single initial commit)

Step 2 — mclayer/marketplace 신규 entry (codeforge-review)
  - marketplace.json plugins[]에 codeforge-review entry 추가
  - codeforge entry version 0.16.0 그대로 (Step 4까지)
  - sync PR + merge → consumer가 즉시 install 가능

Step 3 — mclayer/plugin-codeforge cleanup PR
  - 5 agent + base + 3 checklist 삭제
  - CLAUDE.md "## Inter-plugin Contract" 섹션 신설 (review_verdict v1 schema)
  - CLAUDE.md "## 세션 개시 의무" 필수 플러그인 목록에 codeforge-review 추가
  - CLAUDE.md "## Development Agent Team" 다이어그램에서 review 5 → "codeforge-review plugin (별도)"
  - docs/inter-plugin-contracts/review-verdict-v1.md 신규
  - docs/adr/ADR-008 신규
  - docs/orchestrator-playbook.md 갱신 (review references)
  - docs/plugin-design.md 갱신 (history + count)
  - CHANGELOG v0.17.0 BREAKING entry
  - docs/migration-guide.md v0.16 → v0.17 섹션 (consumer 두 plugin 설치 절차)
  - PR open + CI + merge

Step 4 — marketplace codeforge entry version sync (CFP-24 정책)
  - marketplace.json plugins[name=codeforge].version = 0.17.0
  - sync PR + merge
```

## 6. Consumer migration guide (v0.16 → v0.17)

**BREAKING**. 기존 consumer 조치:

### 6.1 plugin install 추가

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

### 6.2 자동 감지

codeforge-review의 SessionStart hook이 codeforge core 설치 여부를 verify — codeforge만 설치하고 review 미설치 시 review lane 진입 시 ESCALATE (orchestration 흐름 깨짐). codeforge core의 SessionStart hook도 codeforge-review 설치 여부 감지해 안내.

### 6.3 consumer overlay 영향

- consumer overlay에 5 agent 중 어느 것이라도 override 하던 경우 (드뭄): overlay 파일을 codeforge 디렉토리에서 codeforge-review 디렉토리로 이동
- review packet schema는 변동 없음 — overlay 호환

## 7. Testing / Validation

### 7.1 Step 1 검증 (codeforge-review repo 초기 상태)

- `.claude-plugin/plugin.json` valid JSON
- 5 agent + base + 3 checklist 파일 정확 존재 (codeforge에서 사라진 것과 1:1 대응)
- SessionStart hook 구문 valid (`bash -n` syntax check)
- regen-agents.sh 실행 가능 (chmod +x)
- README가 codeforge core dep 명시

### 7.2 Step 3 검증 (codeforge core PR)

- 8 file 삭제 완료 (`ls agents/{Design,Code,Security,Claude,Codex}*.md` → no match)
- CLAUDE.md "## Inter-plugin Contract" 섹션 존재 + review_verdict v1 schema 인용
- 모든 lint PASS (CFP-26/27 invariants 유지)
- 다이어그램이 review 5 agent 외부 plugin 표시
- migration-guide v0.16→v0.17 섹션 self-contained

### 7.3 통합 검증 (Step 4 후)

- consumer test: 가상 consumer 환경에서 두 plugin install → SessionStart hook 정상 → review lane spawn → verdict 반환 → core가 Story §9 + gate label 처리
- 본 검증은 CFP-29 머지 후 첫 real Story (별도 CFP)에서 dogfood

## 8. Risks / Open issues

### 8.1 codeforge core가 review agents 없이 일시적으로 동작 불가

Step 3 머지 후 Step 4 sync 전에 marketplace에 codeforge 0.17.0 = stale entry 존재 (still 0.16.0). consumer가 codeforge update 받지만 marketplace는 옛 entry — consumer가 0.16.0을 보게 됨. 단, codeforge 0.17.0이 marketplace에 노출되는 건 Step 4 sync 후 — Step 3-4 사이 brief 윈도우.

**완화**: Step 3 머지 직후 (분 단위) Step 4 sync. 본 CFP autonomous 진행에서 sequential 자동 처리.

### 8.2 codeforge-review의 SessionStart hook이 core 미설치 시 무한 fail-fast

consumer가 codeforge-review만 install (core 없이) 하면 SessionStart마다 fail. consumer가 core 설치하면 자동 해결. fail 시 install 안내 메시지가 명확해야 함.

### 8.3 review_verdict v1 contract drift

codeforge-review 단독 변경이 contract 깨면 → ADR-008이 versioning enforce. v1.x backward-compat 보존 / v2.0 BREAKING 양쪽 plugin 동시 bump.

**잔여 위험**: ADR-008은 룰만 정의 — 실제 enforcement는 lint 또는 dogfood. CFP-30+에서 contract validation lint 후속 가능 (v2.0 발의 시점에서 결정).

### 8.4 marketplace.json plugins[] 순서

codeforge-review entry를 codeforge 다음에 추가. plugins[] 순서가 install priority에 영향 주지 않음 (Claude Code가 enabledPlugins map으로 lookup) — 안전.

### 8.5 git history 분리

codeforge-review repo는 codeforge git history와 분리됨. 5 agent의 historical commit (CFP-1, CFP-17, ADR-001 등)이 보존 안 됨 — initial commit message에 attribution + ADR-001-extracted-from-codeforge.md에 codeforge SHA 인용으로 audit trail 보존. 완전한 history 보전을 원하면 git filter-branch 등 더 복잡한 절차 가능하나 본 CFP scope 밖.

### 8.6 cross-plugin lint coverage

codeforge core의 lint workflow (6 jobs)가 codeforge-review 파일은 점검 안 함. codeforge-review repo가 자체 lint workflow를 가질지 본 CFP에서는 deferred — initial 0.1.0은 lint 없음. 향후 v0.2.0+에서 추가 (CFP-29.5 또는 등).

## 9. References

### 협업 history
- [CFP-25 design spec](2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) — parent (Phase 1 outline)
- [CFP-25 brainstorm 4 라운드 (Codex)](2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md#11-references) — staged ε strategy 합의

### 관련 SSOT
- [ADR-001](../adr/ADR-001-review-agent-unification.md) — review worker 통합 결정. 본 추출이 plugin 경계로 보존
- [ADR-008](../adr/ADR-008-inter-plugin-contract-versioning.md) — NEW, 본 CFP에서 신설
- [CLAUDE.md](../../../CLAUDE.md) "## Inter-plugin Contract" — review_verdict v1 schema + versioning 룰 SSOT
- [docs/inter-plugin-contracts/review-verdict-v1.md](../../inter-plugin-contracts/review-verdict-v1.md) — 상세 schema
- [docs/migration-guide.md](../../migration-guide.md) v0.16 → v0.17 섹션 — consumer 조치
