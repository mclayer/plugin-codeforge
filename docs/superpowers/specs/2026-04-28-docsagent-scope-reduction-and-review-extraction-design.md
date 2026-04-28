---
spec_id: cfp-25
title: DocsAgent scope reduction + codeforge-review plugin extraction (Path A · staged ε)
status: Draft
date: 2026-04-28
authors:
  - User (motivation + reframing)
  - Claude (Opus 4.7) — synthesis
  - Codex (GPT-5.4 via codex-rescue) — independent architecture review (4 rounds)
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker 통합 결정. 본 spec이 그 결정을 plugin 경계로 보존)
  - ADR-007 (DataMigrationArchitect — 6th deputy 추가가 일으킨 cross-file SSOT churn은 본 spec의 동기 evidence)
related_files:
  - agents/DocsAgent.md (scope 축소)
  - agents/ArchitectAgent.md (Change Plan + ADR direct write 권한 추가)
  - agents/DomainAgent.md (Domain Knowledge direct write 권한 추가)
  - agents/PMOAgent.md (Retro direct write 권한 추가)
  - agents/{DesignReviewPL,CodeReviewPL,SecurityTestPL,ClaudeReview,CodexReview}.md (Phase 1에서 별도 plugin 이동)
  - templates/review-pl-base.md (Phase 1에서 별도 plugin 이동)
  - templates/review-checklists/{design,code,security}.md (Phase 1에서 별도 plugin 이동)
  - scripts/check-doc-links.sh (lint 확장)
  - scripts/check-agent-frontmatter.sh (lint 확장)
  - CLAUDE.md (책임 매트릭스 갱신)
  - docs/orchestrator-playbook.md (write 흐름 갱신)
  - docs/plugin-design.md (plugin 분리 정책 갱신)
---

## 0. 사용자 원문 (verbatim)

> codeforge에서 분리가 가능한 플러그인을 설계하고자 한다. codex와 함께 아키텍트해서 나에게 알려달라.

이후 4 라운드 대화로 reframing:

1. 분리 동기 → 재사용(1) + 독립 cadence(3) + 계층 강제(4)
2. 분리 단위 후보 → β-full(layer-split) 검토 → role-family axis(ε)로 reframing
3. ε 평가 → review-only-first staged 합의
4. DocsAgent 본질 필요성 검토 → "scope만 축소, 존재는 유지" (Path A) 합의

본 spec은 4번 reframing의 결론을 design doc으로 고정.

## 1. 동기 (Why)

### 1.1 사용자가 표명한 문제

> "codeforge 개정할 때 비용이 너무 크다. 유사하거나 중복되는 역할의 agent를 plugin으로 분리하면 본체가 안 흔들리지 않겠나"

구체 evidence: CFP-21 (DataMigrationArchitectAgent — 6th deputy 추가)이 v0.14.0 BREAKING bump을 일으키며 동시 갱신:

- `agents/DataMigrationArchitectAgent.md` (신규)
- `agents/{ArchitectPLAgent,ArchitectAgent,CodebaseMapper,Refactor,SecurityArchitect,TestContractArchitect}.md`
- `templates/change-plan.md` §11
- `templates/review-checklists/design.md`
- `agents/{ClaudeReview,CodexReview}.md` (P0 룰)
- `docs/{orchestrator-playbook.md,plugin-design.md}` + `CLAUDE.md` + `CHANGELOG.md` + ADR-007

= **하나의 deputy 추가에 9+ 파일 동시 갱신 + BREAKING bump**. role-family 한 가족의 변화가 monolith 본체를 흔든다.

### 1.2 Codex의 추가 진단 (라운드 4 회신)

DocsAgent가 **모든 plugin 추출 시도의 가장 큰 결합점**으로 지목됨. git log evidence:

- `b56a9a4` queue/manifest/cache disciplines 추가
- `781abec` permission redefinition + GitHub primitive mapping 재작성
- `0fd48db` R1-R11 parallelization 추가

회고 evidence: `docs/retros/2026-04-27-v0.11.0-sprint-close.md`이 CLAUDE.md를 top drift surface로 명시, DocsAgent를 그 SSOT writer로 명명. **DocsAgent는 convention이 아니라 관찰된 chaos에 대한 응답으로 탄생** — 따라서 functional necessity가 있다.

### 1.3 본 spec이 푸는 결합

DocsAgent의 책임 중 일부는 **funnel(직렬화 enforcement) 가치**가 있고, 일부는 **단순 convention**이다. 후자만 분리하면:

- single-author 문서(Change Plan / ADR / Domain Knowledge / Retro)는 owner agent 직접 write
- multi-writer Story file + GitHub lifecycle은 DocsAgent 유지 (직렬화 필요)
- 결과: codeforge-review 추출이 가능해짐 (review plugin이 자기 verdict를 typed output으로 반환, core가 lifecycle 라벨/Story §9 반영)

## 2. 합의된 strategy

**Path A + staged ε**:

- **Path A** = DocsAgent 존재 유지, scope만 축소 (single-author 4종을 owner direct write로 이관)
- **Staged ε** = role-family 추출 중 review만 먼저, 나머지 deferred (contract 안정성 측정 후)

## 3. 거부된 대안 (Considered Alternatives)

### 3.1 Path B — DocsAgent 완전 제거

거부 사유 (Codex 라운드 4):

- Story §9 동시 write (4 PL 병렬) 직렬화 못 풂 — git는 같은 섹션 동시 edit 해결 안 함
- Phase prefix가 8+ agent 사이 drift 위험
- `phase-label-invariant.yml` · `fix-ledger-sync.yml` · `phase-gate-mergeable.yml`이 coherent label/story state 가정. 분산 시 duplicate-label·duplicate-comment·MCP rate-limit failure mode 곱셈
- shared idempotency wrapper가 DocsAgent 외에 없음

### 3.2 Path C — DocsAgent를 skill로 다운그레이드

거부 사유 (Codex 라운드 4):

- Claude Code skill은 **guidance** 이지 mandatory enforcement가 아님 — malformed write 거부 불가
- cross-plugin skill sync = 새로운 비싼 문제. codeforge-review와 core가 독립 버전이면 §10 schema·11 phase prefix가 drift
- **knowledge는 보존하지만 enforcement를 deletes — failure history가 필요로 한 것의 정반대**

### 3.3 β-full — 4-5 plugin layer split (foundation/orchestration/delivery)

거부 사유 (Codex 라운드 1):

- DocsAgent가 모든 layer 가로지름
- CLAUDE.md + playbook이 phase 라벨·FIX 라우팅을 hardcode (얇은 shell 아님)
- `regen-agents.sh`가 single plugin root 가정
- ADR-001 lane-agnostic 통합 결정 역전 위험

### 3.4 γ — 5+ plugin aggressive split

거부 사유 (Codex 라운드 1·2): marketplace sync tax 5x, contract churn 동반, 결정 역전 가능성 높음.

### 3.5 codeforge-dev-roster 추출

거부 사유 (Codex 라운드 2): overlay `role: dev` + preset이 이미 plugin 분리 효과를 모두 줌. 별도 plugin은 packaging noise.

## 4. Architecture

### 4.1 Phase 0 — DocsAgent scope reduction (현 monolith 안)

**범위**: 3 CFP, no plugin 추출, no queue 메커니즘 변경.

**책임 재분배표**:

| 경로 / 책임 | Before | After (Phase 0 후) |
|---|---|---|
| `docs/change-plans/<slug>.md` | queue → DocsAgent | **ArchitectAgent** (chief author) direct write |
| `docs/adr/ADR-NNN-<slug>.md` | queue → DocsAgent | **ArchitectAgent** direct write |
| `docs/domain-knowledge/<area>/<topic>.md` | queue → DocsAgent | **DomainAgent** direct write |
| `docs/retros/<sprint>.md` | queue → DocsAgent | **PMOAgent** direct write |
| `docs/stories/<KEY>.md` §1 | story-init.yml Action | story-init.yml Action (변경 없음) |
| `docs/stories/<KEY>.md` §§2-11 multi-writer | DocsAgent | **DocsAgent (유지)** |
| §10 FIX Ledger | DocsAgent | **DocsAgent (유지)** |
| §8.5 Impl Manifest | DocsAgent | **DocsAgent (유지)** |
| §9 Review summary (4 PL append) | DocsAgent | **DocsAgent (유지)** |
| GitHub Issue/PR comment phase prefix (11종) | DocsAgent | **DocsAgent (유지)** |
| GitHub PR/Issue body create/update | DocsAgent | **DocsAgent (유지)** |
| GitHub label attach (`gate:*`, `phase:*`, `fix:*`) | DocsAgent | **DocsAgent (유지)** |
| `gh api` fallback (milestones, discussions, GraphQL) | DocsAgent | **DocsAgent (유지)** |

**원칙**: single-owner는 빠지고, multi-writer + GitHub lifecycle은 남는다.

### 4.2 Phase 1 — codeforge-review plugin 추출 (Phase 0 검증 후)

**범위**: 1 CFP, plugin 추출 첫 사례.

**추출 대상**:

```
codeforge-review/  (신규 plugin)
├── .claude-plugin/plugin.json
├── agents/
│   ├── DesignReviewPLAgent.md
│   ├── CodeReviewPLAgent.md
│   ├── SecurityTestPLAgent.md
│   ├── ClaudeReviewAgent.md
│   └── CodexReviewAgent.md
├── templates/
│   ├── review-pl-base.md
│   └── review-checklists/
│       ├── design.md
│       ├── code.md
│       └── security.md
└── README.md
```

**core(codeforge)에 남는 것**:

- Orchestrator playbook · CLAUDE.md
- DocsAgent · PMOAgent · TestAgent · QADeveloperAgent
- RequirementsPLAgent · ArchitectPLAgent · ArchitectAgent (chief author) · DeveloperPLAgent
- 5 architect deputies (CodebaseMapper · Refactor · SecurityArch · TestContractArch · DataMigrationArch — Phase 2 deferred)
- 3 requirements deputies (Domain · RequirementsAnalyst · Researcher — Phase 2 deferred)
- DeveloperAgent · DataEngineerAgent · InfraEngineerAgent (Phase 2에서도 분리 안 함 — overlay/preset이 이미 충분, Codex 라운드 2 권고)
- GitHub workflow templates · overlay framework
- `templates/{change-plan,adr,story-page-structure,impl-manifest}.md`

**marketplace 등록**: `mclayer/marketplace`의 `marketplace.json`에 `codeforge-review` 추가. mirrored 필드(name·version·description·author) cross-repo sync 의무 발생 (CFP-24 정책).

### 4.3 Phase 2 — 조건부 추가 추출 (deferred)

**조건**:
- `codeforge-arch-deputies` 추출 조건 = `templates/change-plan.md` §11 schema가 2 CFP 연속 변경 없음
- `codeforge-req-deputies` 추출 조건 = Story §2·§5·§6 destination schema가 2 CFP 연속 변경 없음

조건 미충족 시 **그냥 core에 둔다**. 강제 분리는 매번 BREAKING bump → 추출 효과 역전.

## 5. Components

### 5.1 Phase 0: 권한 frontmatter 변경

**ArchitectAgent.md** frontmatter:
```yaml
tools:
  - Read
  - Glob
  - Grep
  - Edit("docs/change-plans/**")    # 추가
  - Write("docs/change-plans/**")   # 추가
  - Edit("docs/adr/**")             # 추가
  - Write("docs/adr/**")            # 추가
  - Edit(".claude-work/doc-queue/**")
  - Write(".claude-work/doc-queue/**")
```

**DomainAgent.md** frontmatter:
```yaml
tools:
  - Read
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - Edit("docs/domain-knowledge/**")  # 추가
  - Write("docs/domain-knowledge/**") # 추가
  - Edit(".claude-work/doc-queue/**")
  - Write(".claude-work/doc-queue/**")
```

**PMOAgent.md** frontmatter:
```yaml
tools:
  - Read
  - Glob
  - Grep
  - Edit("docs/retros/**")    # 추가
  - Write("docs/retros/**")   # 추가
  - Edit(".claude-work/doc-queue/**")
  - Write(".claude-work/doc-queue/**")
```

**DocsAgent.md** frontmatter — 4 path deny 추가:
```yaml
tools:
  - Read
  - Glob
  - Grep
  - Edit("docs/**")
  - Write("docs/**")
  # 단, 다음은 deny (owner agent로 이관)
  - "deny: Edit(docs/change-plans/**)"
  - "deny: Edit(docs/adr/**)"
  - "deny: Edit(docs/domain-knowledge/**)"
  - "deny: Edit(docs/retros/**)"
  - mcp__github__*
  - Bash(gh api repos/*/milestones*)
  - ...
```

(정확한 deny 표기 형식은 Claude Code permission schema 확인 후 확정)

### 5.2 Phase 0: Lint 강화

**`scripts/check-agent-frontmatter.sh`** — 기존 agent md frontmatter 검증을 확장해 docs frontmatter 검증 추가:

- `docs/adr/ADR-*.md` → `templates/adr.md` schema 기준 (adr_number / title / status / category / date / related_files)
- `docs/change-plans/*.md` → `templates/change-plan.md` 기준 (§1-§11 heading 존재, frontmatter 필드)
- `docs/domain-knowledge/**/*.md` → 도메인 KB schema (title / area / sources / updated)
- `docs/retros/*.md` → retro schema (sprint / date / cfp_keys / authors)

**`scripts/check-doc-links.sh`** — 기존 link 검증을 확장해 cross-doc 참조 무결성 확인 (ADR ↔ Change Plan ↔ Story file).

CI에서 `.github/workflows/`에 새 lint workflow 추가하거나 기존 workflow에 step 추가.

### 5.3 Phase 1: codeforge-review plugin 구조

**`.claude-plugin/plugin.json`**:
```json
{
  "name": "codeforge-review",
  "version": "0.1.0",
  "description": "Lane-agnostic review subsystem extracted from codeforge — 3 PLs (design/code/security) + 2 workers (Claude/Codex) + base SSOT + 3 checklists. Depends on codeforge core.",
  "author": { "name": "Josh" },
  "keywords": ["review", "code-review", "security-review", "design-review", "lane-agnostic"]
}
```

**dependency 선언**: codeforge-review는 codeforge core에 의존. Claude Code plugin 생태계에서 plugin-to-plugin dependency 표현 방법 확인 필요 (현재 codeforge가 `codex@openai-codex`, `superpowers@claude-plugins-official`, `claude-md-management@claude-plugins-official`, `github@claude-plugins-official` 의존하는 방식 참조). 만약 manifest 차원에서 dep 표현 못 하면 README + SessionStart hook 검증으로 fallback.

### 5.4 Phase 1: Inter-plugin contract — review packet ABI

**core → review plugin 호출 시 contract**:

```yaml
# core(Orchestrator)가 review PL 스폰 시 packet 형태
review_packet:
  lane: design | code | security        # enum 고정
  story_key: <KEY>                       # docs/stories/<KEY>.md 경로 도출용
  change_plan_path: docs/change-plans/<slug>.md  # design lane만
  pr_number: <int>                       # code/security lane만
  category_enum: [...]                   # lane별 카테고리 — review-pl-base.md §X SSOT
  severity_overrides: {...}              # lane별 자동 룰
  story_sections_to_fetch:               # Context Packet
    - "§1 사용자 원문"
    - "§3 관련 ADR"
    - "§7 보안 설계"  # design lane
    - "§8 Test Contract"
```

**review plugin → core 반환 시 contract**:

```yaml
review_verdict:
  lane: design | code | security
  iteration: <int>                       # FIX 카운터, §10 sync에 사용
  status: PASS | FIX | FIX_DISCRETIONARY
  findings:
    - severity: P0 | P1 | P2
      category: <enum>
      file: <path>
      line: <int>
      evidence: <text>
      suggestion: <text>
  summary_for_story_section_9: <markdown> # core(DocsAgent)가 §9에 append
  summary_for_pr_comment: <markdown>      # core(DocsAgent)가 phase comment로 게시
```

**누가 무엇을 하나**:

- review plugin: verdict 생성·반환만 (write 안 함)
- core(DocsAgent): verdict 받아 Story §9 append + GitHub PR comment 게시 + PASS 시 `gate:*-pass` 라벨 부착

**Codex 명시 (라운드 3)**: review plugin은 라벨 부착·Story §9 직접 write 안 함. lifecycle transition은 core 책임 — `phase-gate-mergeable.yml` · `phase-label-invariant.yml`이 단일 actor 가정.

## 6. Data flow

### 6.1 현재 (As-is, queue → DocsAgent drain)

```
ArchitectAgent → write queue file → Orchestrator → DocsAgent spawn → drain → docs/change-plans/*.md write
DomainAgent    → write queue file → Orchestrator → DocsAgent spawn → drain → docs/domain-knowledge/**/*.md write
DesignReviewPL → write queue file → Orchestrator → DocsAgent spawn → drain → docs/stories/<KEY>.md §9 + PR comment + label
```

### 6.2 Phase 0 후 (single-owner direct, multi-owner queue 유지)

```
ArchitectAgent → docs/change-plans/*.md direct write   (no queue)
ArchitectAgent → docs/adr/*.md direct write            (no queue)
DomainAgent    → docs/domain-knowledge/**/*.md direct  (no queue)
PMOAgent       → docs/retros/*.md direct               (no queue)
DesignReviewPL → write queue → DocsAgent drain → §9 + PR comment + label    (변화 없음)
```

### 6.3 Phase 1 후 (review plugin verdict → core 적용)

```
codeforge-review.DesignReviewPL → typed verdict (return value, not write)
                ↓
codeforge.Orchestrator (verdict 수령)
                ↓
codeforge.DocsAgent → §9 append + PR comment (phase prefix 적용) + PASS 시 gate label
```

## 7. Error handling / Edge cases

### 7.1 Phase 0: 4 single-owner 문서 format drift

**위험**: ArchitectAgent의 ADR style과 DomainAgent의 도메인 KB style이 따로 drift.

**완화**:
- `templates/adr.md` · `templates/change-plan.md` (이미 SSOT)
- `scripts/check-agent-frontmatter.sh` 확장으로 frontmatter·필수 섹션 lint
- CI 강제

**잔여 위험** (Codex 라운드 3 인정): lint는 schema 검증만, **policy 검증은 못함** (e.g., "이 ADR이 prior ADR을 올바르게 supersede 하는가"). 이건 ArchitectAgent의 self-discipline + review lane이 catch.

### 7.2 Phase 0: 동시 single-owner write 충돌

**위험**: 한 Story 안에서 ArchitectAgent가 ADR 2개를 동시에 write 하려 시도.

**완화**: 단일 author 단일 epoch — 한 ArchitectAgent 인스턴스가 sequential write. 병렬 deputy는 read-only.

### 7.3 Phase 1: codeforge-review와 core 사이 contract drift

**위험**: review plugin이 `review_verdict` schema를 v0.2.0에서 변경, core는 v0.1.0 기대.

**완화**:
- `templates/review-pl-base.md`을 codeforge-review에 이동시키되, **core가 contract version을 명시** (CLAUDE.md에 "review_verdict v1 contract" 섹션)
- codeforge-review README에 "core compat: codeforge >= 0.15.0" 명시
- marketplace.json mirrored 필드 동기화 의무 (CFP-24 정책) 그대로 적용

### 7.4 Phase 1: gate label 부착 책임 경계 leakage

**위험**: review plugin이 자기 verdict를 PASS라 판정하고 직접 `gate:design-review-pass` 부착.

**완화**: 권한 차단 — codeforge-review의 어떤 agent도 `mcp__github__*` 라벨 도구 권한 없음. core(DocsAgent)만 가짐.

## 8. Testing / Validation

### 8.1 Phase 0 검증 (CFP-X+2)

**기준**: 1-2개 real Story를 Phase 0 후 모델로 실행. 합격 조건:

- `docs/change-plans/<slug>.md` · `docs/adr/ADR-*.md` · `docs/domain-knowledge/**` · `docs/retros/*.md` schema lint pass
- `docs/stories/<KEY>.md` §10 FIX Ledger schema 그대로 유지 (DocsAgent 미손상)
- `fix-ledger-sync.yml` · `phase-gate-mergeable.yml` action clean
- 4 owner agent 직접 write가 git author로 명시적 (audit trail 보존 검증)

실패 시: 해당 owner agent의 권한 회수, DocsAgent로 환원.

### 8.2 Phase 1 검증 (CFP-X+3 이후 2-3 CFP)

**측정 항목**:

- codeforge core 본체 bump 빈도 (Phase 0 → Phase 1 비교)
- codeforge-review plugin 자체 bump 빈도 (independent cadence 검증)
- review_verdict contract 위반 발생 0건
- gate label 부착 실패 0건

**합격 조건**: 2 CFP 연속 core bump 없이 codeforge-review만 bump 된 경우 → Phase 1 성공.

### 8.3 Phase 2 진입 조건 (deferred)

- `codeforge-arch-deputies` 진입: `templates/change-plan.md` §11 schema 2 CFP 안정 + arch-deputy 추가 0건 또는 추가가 있어도 interface 변화 없음
- `codeforge-req-deputies` 진입: Story §2·§5·§6 schema 2 CFP 안정

## 9. Migration / CFP sequencing

```
CFP-25 (본 spec)  : 본 design doc commit (no code change)
CFP-26 (Phase 0a) : Single-owner 4종 권한 이관
                    - ArchitectAgent: docs/change-plans/** + docs/adr/** Write
                    - DomainAgent: docs/domain-knowledge/** Write
                    - PMOAgent: docs/retros/** Write
                    - DocsAgent: 위 4 path deny 추가
                    - CLAUDE.md "Write 권한" 매트릭스 갱신
                    - docs/orchestrator-playbook.md 갱신
                    - CHANGELOG (minor — v0.15.0)
CFP-27 (Phase 0b) : Lint 강화
                    - scripts/check-agent-frontmatter.sh 확장
                    - scripts/check-doc-links.sh 확장
                    - .github/workflows/에 lint step 추가
                    - 기존 docs 4종 backfill (frontmatter 누락 보강)
CFP-28 (Phase 0c) : 1-2 real Story 실행 검증
                    - dogfooded CFP를 Phase 0 후 모델로 시도
                    - 4 single-owner 문서 직접 write 검증
                    - lint clean 확인
                    - 결과 회고 (docs/retros/2026-MM-DD-phase0-validation.md)
CFP-29 (Phase 1)  : codeforge-review plugin 추출
                    - 신규 repo 생성 (mclayer/codeforge-review — codeforge plugin 1개 = 1 repo 관례 유지)
                    - .claude-plugin/plugin.json 작성
                    - 5 agent + base + 3 checklist 이동
                    - codeforge core CLAUDE.md에 "review_verdict v1 contract" 명시
                    - codeforge core dependency 추가 (codeforge-review)
                    - mclayer/marketplace cross-repo sync (codeforge-review 신규 등록 + codeforge dependency 갱신)
                    - codeforge core CHANGELOG (BREAKING — v0.16.0)
CFP-30~31         : Phase 1 검증 기간 (core bump 빈도 측정)
CFP-32 (조건부)   : Phase 2 진입 또는 deferred 유지 결정
```

## 10. Risks / Open issues

### 10.1 DocsAgent가 영구 fixture로 남음 (Codex 라운드 4 명시)

DocsAgent는 본 plan 후에도:
- Story §§2-11 multi-writer 직렬화
- GitHub Issue/PR comment 11 phase prefix
- GitHub PR/Issue body create/update
- GitHub label attach
- `gh api` fallback

— 의 전담자로 남는다. 이는 lifecycle transition·schema 직렬화의 단일 enforcement point가 필요하다는 Codex 평가에 동의한 결과. **future replacement는 typed·idempotent story-update API를 만들어야 가능** (현 plan 범위 밖).

### 10.2 Phase 2가 영원히 안 올 가능성

`templates/change-plan.md` §11 schema는 CFP-21에서 막 추가됐고 향후 churn 가능. Phase 2 진입 조건(2 CFP 안정)이 영원히 충족 안 될 수도 있다. 그 경우 codeforge-arch-deputies는 **영구히 core에 머문다** — 이게 Codex 권고이며 받아들인다.

### 10.3 marketplace sync tax (CFP-24 정책)

Phase 1 추출 후 plugin 2개 (codeforge + codeforge-review) — 매 mirrored 필드 변경 시 cross-repo sync 2회. CFP-24 정책 상수배 적용. tolerable한지는 Phase 1 검증 기간(2-3 CFP) 동안 측정.

### 10.4 review plugin이 codeforge core에 강하게 의존

Codex 라운드 2 진단: review plugin은 Story §9·§10·gate label·phase 라벨·Change Plan schema 등 core SSOT를 reference. **물리적 분리는 했지만 의존은 단방향(review → core)으로 강하게 남는다**. independent cadence 효과는 review plugin의 *내부 변경*(예: 새 카테고리 추가, 새 finding format)에만 한정.

### 10.5 plugin-to-plugin dependency 표현 메커니즘 미확정

`.claude-plugin/plugin.json` schema가 plugin 간 dependency를 manifest 차원에서 표현하는지 확인 필요. 현재 codeforge가 4개 plugin에 의존하지만 manifest에는 명시 안 됨 (CLAUDE.md "세션 개시 의무"에서 SessionStart hook이 검증). codeforge-review도 같은 패턴 따를 가능성 — 검증 로직을 codeforge core SessionStart hook이 수행.

### 10.6 Open decisions (implementation plan에서 해소)

본 design에서 의도적으로 미확정으로 둔 항목:

- **Phase 0a 권한 syntax**: Claude Code permission schema의 path-scoped deny 정확 표기 (§5.1) — 현 codeforge agent md frontmatter 문법 검증 후 확정
- **Phase 1 plugin manifest dependency 필드**: codeforge-review가 codeforge에 의존함을 manifest로 표현할 수 있는지 (§5.3, §10.5) — Claude Code plugin schema 문서 확인 후 확정
- **Phase 1 marketplace 등록 시점**: codeforge-review가 mclayer/marketplace에 1차 등록되는 PR과 codeforge core CHANGELOG BREAKING bump이 같은 sprint 안에 묶여야 함 (CFP-24 cross-repo sync 정책) — 정확 순서는 implementation plan에서 단계화

## 11. References

### 협업 history
- 2026-04-28 brainstorming session (Claude Opus 4.7 + Codex GPT-5.4 via codex-rescue, 4 라운드)
- 라운드 1: α/β/γ layer-split 분석 → β-full 거부, α + presets 권고
- 라운드 2: ε(role-family axis) 평가 → review-only-first staged 권고, dev-roster drop
- 라운드 3: 재분배 평가 → multi-writer 유지·single-owner 이관 boundary 확정
- 라운드 4: A/B/C 평결 → Path A 결정, B(완전제거)·C(skill 다운그레이드) 거부

### 관련 SSOT
- [`CLAUDE.md`](../../../CLAUDE.md) — 본 spec 적용 후 갱신 필요
- [`docs/orchestrator-playbook.md`](../../orchestrator-playbook.md) — write 흐름 §11 갱신 필요
- [`docs/plugin-design.md`](../../plugin-design.md) — plugin 분리 정책 갱신 필요
- [`agents/DocsAgent.md`](../../../agents/DocsAgent.md) — scope 축소 대상
- [`agents/ArchitectAgent.md`](../../../agents/ArchitectAgent.md) · [`agents/DomainAgent.md`](../../../agents/DomainAgent.md) · [`agents/PMOAgent.md`](../../../agents/PMOAgent.md) — 권한 추가 대상
- [`templates/review-pl-base.md`](../../../templates/review-pl-base.md) · [`templates/review-checklists/`](../../../templates/review-checklists/) — Phase 1 추출 대상

### 관련 ADR
- [ADR-001](../../adr/ADR-001-review-agent-unification.md) — lane-agnostic 통합. 본 spec이 plugin 경계로 보존
- [ADR-007](../../adr/ADR-007-datamigration-architect.md) — 6th deputy 추가 사례. 본 spec의 동기 evidence
