# CFP-29 Phase 1 — codeforge-review Plugin 추출 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** codeforge core에서 5 review agent + base + 3 checklist을 신규 `mclayer/plugin-codeforge-review` repo로 추출하고, core는 v0.17.0 BREAKING bump + Inter-plugin Contract SSOT 신설.

**Architecture:** β sequencing — codeforge-review repo 신설 → marketplace 신규 entry → codeforge core PR (cleanup + SSOT 갱신 + v0.17.0) → marketplace version sync. 두 plugin 각자 SessionStart hook + regen-agents.sh 보유, codeforge-review는 codeforge core의 merge.py 재사용.

**Tech Stack:** GitHub repo + plugin manifest + bash hooks + markdown SSOT + GitHub Actions YAML.

---

## Spec 참조

본 plan은 [`docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md`](../specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md) (CFP-29 spec) §5 sequencing 구현. parent: [CFP-25](../specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) §4.2 Phase 1.

## File Structure

| 파일 | 책임 | 변경 종류 |
|---|---|---|
| `agents/{Design,Code,Security}TestPLAgent.md` + ClaudeReviewAgent.md + CodexReviewAgent.md | 5 review agents (codeforge-review로 이동) | **삭제** |
| `templates/review-pl-base.md` | review PL 공통 base | **삭제** |
| `templates/review-checklists/{design,code,security}.md` | 3 lane checklist | **삭제** |
| `docs/inter-plugin-contracts/review-verdict-v1.md` | review_verdict v1 schema 상세 | **신규** |
| `docs/adr/ADR-008-inter-plugin-contract-versioning.md` | versioning 룰 ADR | **신규** |
| `CLAUDE.md` | "## Inter-plugin Contract" 섹션 신설 + 의존성 목록 + 다이어그램 + 책임 매트릭스 | 정비 |
| `docs/orchestrator-playbook.md` | review reference → "codeforge-review plugin" | 정비 |
| `docs/plugin-design.md` | Stage 1 history + agent count 24 → 19 | 정비 |
| `.claude-plugin/plugin.json` | version 0.16.0 → 0.17.0 | 정비 |
| `CHANGELOG.md` | [0.17.0] BREAKING entry | 정비 |
| `docs/migration-guide.md` | v0.16 → v0.17 섹션 (consumer 두 plugin 설치) | 정비 |
| `scripts/check-no-atlassian.sh` | allowlist에 CFP-29 spec/plan 추가 | 정비 |
| `mclayer/plugin-codeforge-review/**` (외부 repo) | 신규 plugin (8 file 이동 + 자체 hook + manifest + README) | 외부 신규 |
| `mclayer/marketplace/.claude-plugin/marketplace.json` | codeforge-review 신규 entry + codeforge version sync | 외부 정비 |

---

## Task 1: docs/inter-plugin-contracts/review-verdict-v1.md 신설

**Files:**
- Create: `docs/inter-plugin-contracts/review-verdict-v1.md`

상세 schema 본문. CLAUDE.md "## Inter-plugin Contract" 섹션이 본 file에 cross-ref.

- [ ] **Step 1: Write file**

내용 ~120 lines. review_packet (core → review plugin) + review_verdict (review plugin → core) 두 schema 명시 + versioning 룰 + ESCALATE 처리 + example.

- [ ] **Step 2: Commit**

```
git add docs/inter-plugin-contracts/review-verdict-v1.md
git commit -m "feat(cfp-29): docs/inter-plugin-contracts/review-verdict-v1.md 신설"
```

---

## Task 2: docs/adr/ADR-008-inter-plugin-contract-versioning.md 신설

ADR-008. v1.x backward-compat / v2.0 BREAKING 룰 동결.

- [ ] **Step 1: Write ADR**
- [ ] **Step 2: Commit** `feat(cfp-29): ADR-008 — Inter-plugin Contract Versioning`

---

## Task 3: 5 review agent + base + 3 checklist 삭제 (codeforge core)

가장 무거운 단일 step. 8 file rm.

- [ ] **Step 1: Verify pre-state** (file 존재 확인)
- [ ] **Step 2: Delete 8 files**
```bash
git rm agents/DesignReviewPLAgent.md \
       agents/CodeReviewPLAgent.md \
       agents/SecurityTestPLAgent.md \
       agents/ClaudeReviewAgent.md \
       agents/CodexReviewAgent.md \
       templates/review-pl-base.md \
       templates/review-checklists/design.md \
       templates/review-checklists/code.md \
       templates/review-checklists/security.md
rmdir templates/review-checklists/
```
- [ ] **Step 3: Verify** (`ls agents/ | grep -i review` → empty)
- [ ] **Step 4: Run lints** — invariant-check 일부 fail 예상 (CFP-7 Write queue parity가 ClaudeReview/CodexReview 등 5 agent를 listed인데 frontmatter 부재로 detect할 수 있음). 즉시 다음 task에서 CLAUDE.md 갱신 시 해소
- [ ] **Step 5: Commit**

---

## Task 4: CLAUDE.md 갱신 — 4 sub-section

- [ ] **Step 1: "## Development Agent Team" 다이어그램** — 5 review agent 노드를 "codeforge-review plugin (별도)" 외부 box로
- [ ] **Step 2: "## 세션 개시 의무" 필수 플러그인 목록** — codeforge-review 추가 (4 → 5종)
- [ ] **Step 3: "## Inter-plugin Contract" 섹션 신설** — review_verdict v1 schema 인용 + cross-ref to docs/inter-plugin-contracts/
- [ ] **Step 4: "## 오케스트레이션 규칙" / Never-skippable 등 review 5 agent 참조** — "codeforge-review의 ClaudeReviewAgent" 식으로 plugin 명시
- [ ] **Step 5: "## Write 권한" / "Codex CLI 필수" / "병렬 스폰 권장"** — review references 갱신
- [ ] **Step 6: "## 디자인 vs Code vs Security 책임 매트릭스"** — 변경 없음 (lane 자체는 유지, 단지 워커가 외부 plugin)
- [ ] **Step 7: Run lints + commit**

---

## Task 5: orchestrator-playbook.md 갱신

review references → "codeforge-review plugin"의 ClaudeReview/CodexReview/3 PL.

- [ ] **Step 1: grep 모든 review reference**
- [ ] **Step 2: Edit** — Phase 1·2 lane spawn 흐름의 dispatch line 표현 갱신
- [ ] **Step 3: §11.4 write queue type enum / §13.4 등** — 영향 점검 (large 변경 안 예상)
- [ ] **Step 4: Run lints + commit**

---

## Task 6: plugin-design.md 갱신

- [ ] **Step 1: Stage 1 history line append** — v0.17 milestone (codeforge-review 추출)
- [ ] **Step 2: Agent count 24 → 19** (5 review agent 제거)
- [ ] **Step 3: §1·§2a·§5·§6 등 모든 24 → 19**
- [ ] **Step 4: Group A 분류 갱신** (5 review가 Group A에 있었음)
- [ ] **Step 5: commit**

---

## Task 7: v0.17.0 release artifacts

- [ ] **Step 1: plugin.json** version 0.16.0 → 0.17.0
- [ ] **Step 2: CHANGELOG [0.17.0] entry** — Removed/Added/Changed/Why/Migration 5 sections
- [ ] **Step 3: docs/migration-guide.md v0.16 → v0.17 섹션** — consumer 두 plugin 설치 가이드
- [ ] **Step 4: commit**

---

## Task 8: Final verification + check-no-atlassian allowlist

- [ ] **Step 1: allowlist에 CFP-29 spec + plan 추가**
- [ ] **Step 2: Run all 6 lints — 모두 PASS**
- [ ] **Step 3: Verify commit log + diff stat**
- [ ] **Step 4: commit**

---

## Task 9: Bootstrap mclayer/plugin-codeforge-review repo (외부 작업)

본 task는 **외부 GitHub repo create + initial commit**. codeforge feature branch와 별도 워크스페이스.

- [ ] **Step 1: GitHub repo create** — `mclayer/plugin-codeforge-review` (public, no template)
- [ ] **Step 2: Local clone**
- [ ] **Step 3: Copy 8 files from codeforge main (pre-deletion SHA)** to codeforge-review:
```
agents/{DesignReviewPL,CodeReviewPL,SecurityTestPL,ClaudeReview,CodexReview}Agent.md
templates/review-pl-base.md
templates/review-checklists/{design,code,security}.md
```
- [ ] **Step 4: Create plugin manifest**
```json
.claude-plugin/plugin.json
{
  "name": "codeforge-review",
  "version": "0.1.0",
  "description": "codeforge core 의 lane-agnostic review subsystem (3 PL + 2 worker + base + 3 checklist). codeforge core 의존 — 단독 동작 불가.",
  "author": { "name": "Josh" },
  "keywords": ["review", "code-review", "security-review", "design-review", "codeforge-extension"]
}
```
- [ ] **Step 5: Create overlay/hooks/session-start-deps-check.sh** + chmod +x
- [ ] **Step 6: Create overlay/hooks/regen-agents.sh** (codeforge core merge.py 재사용 패턴) + chmod +x
- [ ] **Step 7: Create README.md** — install + dep + verdict v1 contract 인용
- [ ] **Step 8: Create CHANGELOG.md** — [0.1.0] initial extract entry
- [ ] **Step 9: Create docs/adr/ADR-001-extracted-from-codeforge.md** — codeforge SHA + verdict v1 동결 시점 기록
- [ ] **Step 10: Initial commit + push to main** (no PR — bootstrap commit)

---

## Task 10: marketplace 신규 entry + codeforge version sync (외부 작업)

본 task는 **mclayer/marketplace** 측 작업. codeforge core PR merge 전후 두 단계.

### Phase A — codeforge-review entry 추가 (codeforge PR open 직후)

- [ ] **Step 1: Branch in marketplace repo** `add/codeforge-review-0.1.0`
- [ ] **Step 2: marketplace.json plugins[]에 codeforge-review entry 추가** (codeforge entry version은 그대로 0.16.0 유지)
- [ ] **Step 3: commit + PR open**
- [ ] **Step 4: PR merge** (consumer가 codeforge-review install 가능 상태)

### Phase B — codeforge entry version sync (codeforge core PR merge 직후)

- [ ] **Step 5: Branch** `sync/codeforge-0.17.0`
- [ ] **Step 6: marketplace.json plugins[name=codeforge].version = 0.17.0**
- [ ] **Step 7: commit + PR open + merge**

---

## Task 11: codeforge core PR open + CI + merge

- [ ] **Step 1: Push feature branch**
- [ ] **Step 2: gh pr create** with comprehensive body
- [ ] **Step 3: Add labels** (phase:설계-리뷰 + gate:design-review-pass)
- [ ] **Step 4: Wait for CI** — all 9+ checks PASS
- [ ] **Step 5: gh pr merge --merge**

---

## 자체 점검 (Self-Review)

**1. Spec coverage**: CFP-29 spec §5 sequencing의 4 step 매핑:
- spec Step 1 (codeforge-review repo 신설) → plan Task 9
- spec Step 2 (marketplace add) → plan Task 10 Phase A
- spec Step 3 (codeforge cleanup PR) → plan Tasks 1-8 + 11
- spec Step 4 (marketplace sync) → plan Task 10 Phase B

**2. Order**: spec 권고 β order는 review-first → core-cleanup-second. plan order는 core changes (1-8) → review repo bootstrap (9) → marketplace add (10A) → core PR merge (11) → marketplace sync (10B). 약간 다른 흐름 (실제 행위 시점 기준):

- codeforge core 변경은 feature branch에 commit (실제 main 영향 없음, PR merge까지)
- review repo bootstrap은 별도 repo 신설 — 즉시 main에 commit (별도 PR 없이)
- marketplace add Phase A는 PR merge 후에야 consumer 영향 — codeforge core PR open 시점에 marketplace PR open + merge 가능
- codeforge core PR merge가 가장 큰 이벤트
- marketplace Phase B는 core merge 직후 즉시 sync (CFP-24 정책)

따라서 실제 main 진입 순서:
1. codeforge-review repo main 진입 (Task 9 push 시점)
2. marketplace codeforge-review entry main 진입 (Task 10 Phase A merge)
3. codeforge core v0.17.0 main 진입 (Task 11 merge)
4. marketplace codeforge version sync main 진입 (Task 10 Phase B merge)

이 순서가 spec β order와 일치 (consumer가 codeforge-review를 install할 수 있는 시점이 codeforge core BREAKING 전에 옴).

**3. Placeholder scan**: 본 plan은 Tasks 1-8 step 본문은 high-level 만 적음 (concrete code는 spec과 implementer에게 위임). 통상 plan보다 가벼움 — 실행 단계에서 구체화. 명시 placeholder ("TODO" 등) 없음.

**4. Type consistency**: review_verdict v1 contract version "1.0", `next_gate_label` enum, `status` enum 등 spec과 plan/Task 4 일관 인용.

**5. Risk coverage**: spec §8 모든 risk 항목 (codeforge-review 단독 사용 / sequencing window / contract drift / cross-plugin lint coverage 등)이 plan task에 mitigation 매핑.

---

## 다음 plan (참조)

- **CFP-29.5 (조건부)**: codeforge-review 자체 lint workflow 추가
- **CFP-30+ (조건부)**: contract validation lint (v1 schema 위반 자동 detect)
- **CFP-28 (deferred)**: lint strict 전환 + 기존 retro 3건 frontmatter backfill + real Story 검증
- **misc cleanup**: PMOAgent §4 line 152 / Cross-Story routing / ADR-002 context note
