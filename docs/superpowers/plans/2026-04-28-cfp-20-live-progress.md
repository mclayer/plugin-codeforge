# CFP-20 Live Progress Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Orchestrator-owned ephemeral §0 Live Progress dashboard rendered as M3 hierarchical view with S3 completion snippets, documented as playbook §14 SSOT + 7 golden render examples.

**Architecture:** Document Orchestrator runtime behavior in playbook §14 (operational SSOT — trigger table, render rules, S3 snippet table, resume logic, state source vs cache invariant). Provide 7 golden examples in `templates/progress-examples/` to validate render correctness across edge cases. Cross-reference from PMOAgent (회고 input) and CLAUDE.md (컨텍스트 전달). No new code, no new workflows, no new dependencies — Orchestrator runtime behavior emerges from documented rules.

**Tech Stack:** Markdown documentation, plain-text golden examples. Validation via grep + manual diff against goldens. Plugin self-application (next CFP-21+ Story) is the strongest end-to-end test.

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `templates/progress-examples/` | Create directory | Container for 7 golden render examples |
| `templates/progress-examples/01-simple-pass.md` | Create | 7 lanes all ✅ happy path golden |
| `templates/progress-examples/02-na-lane.md` | Create | Plugin meta `⊘ N/A` lane skip golden |
| `templates/progress-examples/03-multi-fix.md` | Create | Multi-FIX cycle 진행 중 snapshot |
| `templates/progress-examples/04-reset-marker.md` | Create | `🔁 RESET-N` 보안→설계 회귀 marker |
| `templates/progress-examples/05-active-deputy.md` | Create | 활성 lane deputy expand + qualifier `(3/4 deputies)` |
| `templates/progress-examples/06-r9-subset.md` | Create | R9 functional ∥ performance subset 병렬 qualifier |
| `templates/progress-examples/07-r11-fastpath.md` | Create | R11 mechanical `❌ FIX-N (fast-path)` marker |
| `docs/orchestrator-playbook.md` | Modify (insert) | §14 신규 — §0 Live Progress operational SSOT (between §13.6 and 부록 A) |
| `agents/PMOAgent.md` | Modify | 2 곳 — Story 완료 회고 입력 source + Cross-Story 분석 input에 progress file 추가 |
| `CLAUDE.md` | Modify | "컨텍스트 전달" 섹션 (line 142 다음)에 §0 progress 위치 1줄 추가 |

---

## Task 1: Create progress-examples directory + 7 golden render examples

**Files:**
- Create: `templates/progress-examples/01-simple-pass.md`
- Create: `templates/progress-examples/02-na-lane.md`
- Create: `templates/progress-examples/03-multi-fix.md`
- Create: `templates/progress-examples/04-reset-marker.md`
- Create: `templates/progress-examples/05-active-deputy.md`
- Create: `templates/progress-examples/06-r9-subset.md`
- Create: `templates/progress-examples/07-r11-fastpath.md`

- [ ] **Step 1.1: Create directory**

```bash
mkdir -p templates/progress-examples
```

- [ ] **Step 1.2: Write `01-simple-pass.md` (7 lanes ✅ happy path)**

Content of `templates/progress-examples/01-simple-pass.md`:

```markdown
# Live Progress — CFP-EXAMPLE-01

last_updated: 2026-04-28T12:00:00Z
last_processed_seq: 42
current_lane: (완료)
fix_cycle: 0

✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 0건
✅ 설계 — Change Plan v1 + ADR-007 신규 (deputy 4인)
✅ 설계 리뷰 — PASS — Claude/Codex 종합, 코멘트 #234
✅ 구현 — Phase 2 PR #235 · 12건 · §8.5 manifest 8건
✅ 구현 리뷰 — PASS — Claude/Codex 종합, 코멘트 #236
✅ 구현 테스트 — functional PASS, performance Δ -2%
✅ 보안 테스트 — 1차 alerts 0 / 2차 P0:0 P1:0
```

- [ ] **Step 1.3: Write `02-na-lane.md` (plugin meta N/A skip)**

Content of `templates/progress-examples/02-na-lane.md`:

```markdown
# Live Progress — CFP-EXAMPLE-02

last_updated: 2026-04-28T12:00:00Z
last_processed_seq: 38
current_lane: (완료)
fix_cycle: 0

✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 0건
✅ 설계 — Change Plan v1 + ADR-008 신규 (deputy 4인)
✅ 설계 리뷰 — PASS — Claude/Codex 종합, 코멘트 #237
✅ 구현 — Phase 2 PR #238 · 5건 · §8.5 manifest 3건
✅ 구현 리뷰 — PASS — Claude/Codex 종합, 코멘트 #239
✅ 구현 테스트 — functional PASS, performance Δ -1%
⊘ 보안 테스트 — N/A — plugin meta (코드 변경 없음)
```

- [ ] **Step 1.4: Write `03-multi-fix.md` (multi-FIX cycle snapshot)**

Content of `templates/progress-examples/03-multi-fix.md`:

```markdown
# Live Progress — CFP-EXAMPLE-03

last_updated: 2026-04-28T15:30:00Z
last_processed_seq: 76
current_lane: 구현 리뷰
fix_cycle: 1

✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 1건
✅ 설계 — Change Plan v3 + ADR-009 변경 (deputy 4인)
✅ 설계 리뷰 — PASS — Claude/Codex 종합, 코멘트 #240
✅ 구현 — Phase 2 PR #241 · 18건 · §8.5 manifest 12건
🔄 구현 리뷰 — 진행 중 (FIX-1)
⏸ 구현 테스트
⏸ 보안 테스트

# Note: 본 snapshot은 구현 리뷰 FIX-1 cycle 진행 중. 과거 FIX 이력은 §0 아닌 docs/stories/<KEY>.md §10 FIX Ledger SSOT 참조.
```

- [ ] **Step 1.5: Write `04-reset-marker.md` (RESET marker after security→design regression)**

Content of `templates/progress-examples/04-reset-marker.md`:

```markdown
# Live Progress — CFP-EXAMPLE-04

last_updated: 2026-04-28T16:45:00Z
last_processed_seq: 91
current_lane: 구현 리뷰
fix_cycle: 0

✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 0건
✅ 설계 — Change Plan v2 + ADR-010 변경 (deputy 4인)
✅ 설계 리뷰 — PASS — Claude/Codex 종합, 코멘트 #243
✅ 구현 — Phase 2 PR #244 · 22건 · §8.5 manifest 14건
🔁 구현 리뷰 — RESET-1
⏸ 구현 테스트
⏸ 보안 테스트

# Note: 보안 테스트 FAIL → 설계 회귀 → 구현 재실행 후 구현 리뷰 재진입 직전 RESET 마커 freeze. 다음 이벤트(lane 재진입)에서 `🔄 진행 중 (RESET-1)` 로 전이.
```

- [ ] **Step 1.6: Write `05-active-deputy.md` (active lane deputy expand)**

Content of `templates/progress-examples/05-active-deputy.md`:

```markdown
# Live Progress — CFP-EXAMPLE-05

last_updated: 2026-04-28T13:15:00Z
last_processed_seq: 28
current_lane: 설계
fix_cycle: 0

✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 0건
🔄 설계 — 진행 중 (3/4 deputies)
   ├─ ✅ CodebaseMapperAgent
   ├─ ✅ RefactorAgent
   ├─ ✅ SecurityArchitectAgent
   ├─ ✅ TestContractArchitectAgent
   └─ 🔄 ArchitectAgent (chief author) — Change Plan §3 author 중
⏸ 설계 리뷰
⏸ 구현
⏸ 구현 리뷰
⏸ 구현 테스트
⏸ 보안 테스트

# Note: 4 deputy 모두 PASS, ArchitectAgent (chief author) 통합 author 진행 중. qualifier "(3/4 deputies)" 는 sub-tree 내 done deputy 수 / 전체 deputy 수.
```

- [ ] **Step 1.7: Write `06-r9-subset.md` (R9 functional ∥ performance subset)**

Content of `templates/progress-examples/06-r9-subset.md`:

```markdown
# Live Progress — CFP-EXAMPLE-06

last_updated: 2026-04-28T17:00:00Z
last_processed_seq: 64
current_lane: 구현 테스트
fix_cycle: 0

✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 0건
✅ 설계 — Change Plan v1 + ADR-011 신규 (deputy 4인)
✅ 설계 리뷰 — PASS — Claude/Codex 종합, 코멘트 #246
✅ 구현 — Phase 2 PR #247 · 9건 · §8.5 manifest 6건
✅ 구현 리뷰 — PASS — Claude/Codex 종합, 코멘트 #248
🔄 구현 테스트 — 진행 중 (functional ✅ / performance 🔄)
⏸ 보안 테스트

# Note: R9 subset 병렬 — TestAgent functional 완료 후 performance baseline 비교 진행 중. inline qualifier 가 두 subset 진행 상태 동시 표기.
```

- [ ] **Step 1.8: Write `07-r11-fastpath.md` (R11 mechanical fast-path marker)**

Content of `templates/progress-examples/07-r11-fastpath.md`:

```markdown
# Live Progress — CFP-EXAMPLE-07

last_updated: 2026-04-28T18:20:00Z
last_processed_seq: 53
current_lane: 구현 리뷰
fix_cycle: 1

✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 0건
✅ 설계 — Change Plan v1 + ADR-012 신규 (deputy 4인)
✅ 설계 리뷰 — PASS — Claude/Codex 종합, 코멘트 #250
✅ 구현 — Phase 2 PR #251 · 15건 · §8.5 manifest 9건
❌ FIX-1 (fast-path) — 구현 리뷰 — typo · broken-link · minor-naming · comment-only 카테고리
⏸ 구현 테스트
⏸ 보안 테스트

# Note: R11 mechanical fast-path. 일반 FIX와 달리 DeveloperPL 진단 cycle 우회 — DocsAgent 또는 자동화로 즉시 fix 가능한 mechanical 카테고리만 적용. severity 항상 P2 이하.
```

- [ ] **Step 1.9: Verify all 7 files created**

Run:
```bash
ls templates/progress-examples/ | sort
```

Expected output:
```
01-simple-pass.md
02-na-lane.md
03-multi-fix.md
04-reset-marker.md
05-active-deputy.md
06-r9-subset.md
07-r11-fastpath.md
```

- [ ] **Step 1.10: Verify each file contains canonical 7 lanes (or N/A skip)**

Run:
```bash
for f in templates/progress-examples/*.md; do
  echo "=== $f ==="
  grep -cE "^(✅|🔄|⏸|❌|⏳|⊘|🔁)" "$f"
done
```

Expected: each file has ≥7 lane lines (some may have additional sub-tree lines).

- [ ] **Step 1.11: Commit**

```bash
git add templates/progress-examples/
git commit -m "$(cat <<'EOF'
feat(cfp-20): templates/progress-examples/ 7 golden render examples

CFP-20 Live Progress dashboard render 정합성 검증용 golden 7종:
- 01: 7 lanes 모두 ✅ happy path
- 02: ⊘ N/A 보안 테스트 (plugin meta skip)
- 03: 🔄 구현 리뷰 (FIX-1) cycle snapshot
- 04: 🔁 RESET-1 (보안→설계 회귀)
- 05: 활성 설계 lane deputy expand + (3/4 deputies) qualifier
- 06: R9 functional ∥ performance subset qualifier
- 07: R11 mechanical fast-path FIX-1 마커

Spec: docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md §7.1
EOF
)"
```

---

## Task 2: Add playbook §14 — §0 Live Progress operational SSOT

**Files:**
- Modify: `docs/orchestrator-playbook.md` (insert §14 between line 1078 and line 1080, before `## 부록 A`)

- [ ] **Step 2.1: Verify insertion point**

Run:
```bash
sed -n '1077,1083p' docs/orchestrator-playbook.md
```

Expected output:
```
- 사용자 직접 상호작용 (Orchestrator 경유 보고만)

---

## 부록 A. 관련 문서

- `CLAUDE.md` — 에이전트 목록·레인·권한·GitHub Workflow·ADR 규약 ("무엇")
```

- [ ] **Step 2.2: Insert §14 content using Edit tool**

Use Edit on `docs/orchestrator-playbook.md`. Replace:

```
- 사용자 직접 상호작용 (Orchestrator 경유 보고만)

---

## 부록 A. 관련 문서
```

with:

```
- 사용자 직접 상호작용 (Orchestrator 경유 보고만)

---

## 14. §0 Live Progress (CFP-20)

`.claude-work/progress/<KEY>.md` 파일에 Orchestrator가 7-lane × phase 진행 상황을 M3 hierarchical + S3 completion snippet 형식으로 기록한다. PR diff에 노출 X (gitignored), GitHub Issue body 미러링 X (DocsAgent 영역 침범 회피). 사용자 원문 "todolist 처럼 매 진행 때마다 수시로 보여" 의도 충족.

### 14.1 권한·소유

| 컴포넌트 | Writer | Reader |
|---|---|---|
| `.claude-work/progress/<KEY>.md` | **Orchestrator 단독** | Orchestrator (resume), PMOAgent (회고), 사용자 (수동) |
| `.claude-work/progress/index.md` | Orchestrator 단독 | Orchestrator (multi-Story 분기) |
| `.claude-work/progress/_archive/<KEY>.md` | Orchestrator (Story 완료 시 mv) | PMOAgent (Cross-Story 패턴) |

DocsAgent / doc-queue / docs/stories/<KEY>.md / GitHub Issue body: **무관여**.

### 14.2 State source vs Derivative cache (핵심 invariant)

```
State source (committed, durable):
  - docs/stories/<KEY>.md §10 FIX Ledger    → FIX 카운터 + RESET 마커
  - docs/stories/<KEY>.md §-fill state      → 완료 lane 추론
  - GitHub Issue phase label                → 현재 lane

Derivative cache (ephemeral, gitignored):
  - .claude-work/progress/<KEY>.md          → rendered §0
```

- 정상 흐름: 매 이벤트마다 cache 직접 patch (read-patch-write, 저비용)
- 세션 재개 / 손상 / 모순 감지 시: state source에서 재 derive 후 cache 재기록
- cache는 항상 source로부터 재구성 가능 → 손실/손상이 데이터 손실이 아님

### 14.3 §0 file 포맷

```markdown
# Live Progress — <KEY>

last_updated: <ISO8601>
last_processed_seq: <N>
current_lane: <한국어 lane 이름>
fix_cycle: <N>

✅ 요구사항 — <S3 snippet>
🔄 설계 — 진행 중 (3/4 deputies)
   ├─ ✅ CodebaseMapperAgent
   ├─ ✅ RefactorAgent
   ├─ ✅ SecurityArchitectAgent
   ├─ ✅ TestContractArchitectAgent
   └─ 🔄 ArchitectAgent (chief author) — Change Plan §3 author 중
⏸ 설계 리뷰
⏸ 구현
⏸ 구현 리뷰
⏸ 구현 테스트
⏸ 보안 테스트
```

- frontmatter 없이 plain markdown + yaml-style 메타 4줄
- Story 시작 시 모든 lane `⏸` init
- Story 완료 시 `_archive/<KEY>.md` 로 mv (PMO Cross-Story 분석 input 보존)

### 14.4 Status enum

| 마커 | 의미 | 사용 위치 |
|---|---|---|
| `⏸` | pending | Lane top, deputy slot |
| `🔄` | in-progress | Lane top, deputy slot |
| `✅` | PASS / done | Lane top (S3 snippet 동반), deputy slot |
| `❌ FIX-N` | FIX 진행 중 | Lane top (evidence 1줄 동반) |
| `❌ FIX-N (fast-path)` | R11 mechanical | Lane top (typo·broken-link·minor-naming·comment-only) |
| `⏳` | blocked | Lane top (사용자/외부 의존성 대기) |
| `⊘ N/A` | skip | Lane top (사유 동반, 주로 plugin meta) |
| `🔁 RESET-N` | 구현 리뷰 RESET | 구현 테스트·보안 테스트 → 구현 회귀 시 |

활성 lane top 라인에 inline qualifier (예: `🔄 설계 — 진행 중 (3/4 deputies)` / `🔄 구현 테스트 — 진행 중 (functional ✅ / performance 🔄)`).

### 14.5 트리거 SSOT

| 이벤트 | 영향 라인 | 갱신 동작 | terminal narration |
|---|---|---|---|
| Story 개시 | 전체 | file create, 7 lane `⏸` | ✅ |
| Lane 진입 | top | `⏸` → `🔄 진행 중`, current_lane 갱신 | ✅ |
| Deputy spawn | active sub-tree | `🔄 <Deputy>` 추가, qualifier 갱신 | ❌ (file only) |
| Deputy return | active sub-tree | `🔄` → `✅`, qualifier 갱신 | ❌ (file only) |
| 병렬 dispatch (R3·R4·R7·R9) | active sub-tree | 두 deputy 동시 `🔄` 라인 추가 | ❌ (file only) |
| R9 subset 시작 | 구현 테스트 | inline qualifier `(functional 🔄 / performance ⏸)` | ✅ |
| R9 subset 완료 | 구현 테스트 | qualifier 갱신 | ❌ (lane PASS/FIX 시 별도) |
| R11 fast-path | 해당 lane | `❌ FIX-N (fast-path)` 마커 | ✅ |
| Lane PASS | top | `🔄` → `✅ — <S3 snippet>`, sub-tree 접음 | ✅ |
| Lane FIX | top | `🔄` → `❌ FIX-N — <evidence 1줄>`, fix_cycle 갱신 | ✅ |
| Lane 재진입 (FIX 후) | top | `❌ FIX-N` → `🔄 진행 중 (FIX-N)` | ✅ |
| RESET 마커 | 구현 리뷰 | `✅` → `🔁 RESET-N` | ✅ |
| Lane N/A (plugin meta) | top | `⏸` → `⊘ N/A — <사유>` | ✅ |
| 사용자 "진행상황 보여줘" | — | file 변경 없이 현재 §0 전체 emit | ✅ (deputy 포함 full) |
| Story 완료 | 전체 | 모두 `✅`, archive mv, index 갱신 | ✅ |

R10 prefetch (security 1차 layer cache) 같은 사용자 무관 메타 이벤트는 **의도적 skip**.

### 14.6 S3 snippet 7-lane 표 (Lane PASS 시 1줄)

| Lane | snippet 템플릿 | source |
|---|---|---|
| 요구사항 | `통합 명세 §3-6 + 도메인 공백 <N>건` | RequirementsPL 통합 + DomainAgent |
| 설계 | `Change Plan v<N> + ADR-<NNN> <신규\|변경> (deputy <M>인)` | ArchitectPL + ADR file mtime |
| 설계 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | DesignReviewPL packet |
| 구현 | `Phase 2 PR #<num> · <commit>건 · §8.5 manifest <file>건` | DeveloperPL + git log |
| 구현 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | CodeReviewPL packet |
| 구현 테스트 | `functional <PASS\|FAIL>, performance Δ <±N%>` | TestAgent subset |
| 보안 테스트 | `1차 alerts <N> / 2차 P0:<N> P1:<N>` | SecurityTestPL packet |

미정 데이터는 `?` placeholder (예: `Change Plan v? + ADR-? 신규 (deputy 4인)`).

### 14.7 Render flow

```
[Lane/Deputy event 발생]
  └→ Orchestrator 1차 수신
       ├→ 1) Read(.claude-work/progress/<KEY>.md)  (cache)
       ├→ 2) parse → 해당 lane sub-tree patch
       ├→ 3) Write(.claude-work/progress/<KEY>.md) — full rewrite, last_processed_seq 증가
       ├→ 4) lane boundary 이벤트일 때만 → terminal narration emit
       └→ 5) Story 완료 시 _archive/<KEY>.md 로 mv + index.md 갱신
```

### 14.8 Resume / corruption 처리

세션 재개 / 압축 재개 시:

1. `.claude-work/progress/<KEY>.md` 존재 여부 확인
2. **존재해도 신뢰하지 않음** — state source(Story §10 + GitHub Issue phase label + Story §-fill state)에서 재 derive
3. 재 derive 결과를 cache 재기록, last_processed_seq 갱신
4. deputy sub-tree는 비워둠 (활성 deputy 정보 손실 허용 — 다음 deputy 이벤트에서 자동 충족)

손상 시: parse 실패 → backup(`<KEY>.md.bak`) → state source에서 재 derive.

### 14.9 Multi-Story index

`.claude-work/progress/index.md`:

```markdown
# Active Stories Index

last_updated: <ISO8601>

- CFP-20 (phase: 설계, fix_cycle: 0)
- CFP-21 (phase: 구현 리뷰, fix_cycle: 1)
```

- Orchestrator가 모든 active Story KEY + 현재 phase만 기록
- "always latest" pointer로 사용 (다음 작업 분기 시 어느 Story가 활성인지 파악)
- SSOT 아님 — 진실은 각 `<KEY>.md` 와 state source

### 14.10 Story 완료 archive

Story Phase 2 PR merge 후:

```bash
mv .claude-work/progress/<KEY>.md .claude-work/progress/_archive/<KEY>.md
```

Orchestrator는 `_archive/` 디렉토리 부재 시 `mkdir -p` 후 mv. PMOAgent Cross-Story 분석은 `_archive/**` glob 으로 누적 progress 참조.

Story 중도 폐기 시: `_archive/<KEY>-aborted.md` 로 mv, 사용자 narration "Story 폐기".

---

## 부록 A. 관련 문서
```

- [ ] **Step 2.3: Verify §14 inserted correctly**

Run:
```bash
grep -n "^## 14\.\|^### 14\." docs/orchestrator-playbook.md
```

Expected: 11 lines matching §14, §14.1, §14.2, ..., §14.10.

- [ ] **Step 2.4: Verify §14 placement (between §13.6 and 부록 A)**

Run:
```bash
grep -n "^## 1[34]\.\|^## 부록" docs/orchestrator-playbook.md
```

Expected output (line numbers):
- §13 PMOAgent (existing)
- §14 §0 Live Progress (newly added)
- 부록 A 관련 문서
- 부록 B 개정 이력

§14 must be between §13 and 부록 A.

- [ ] **Step 2.5: Commit**

```bash
git add docs/orchestrator-playbook.md
git commit -m "$(cat <<'EOF'
feat(cfp-20): playbook §14 신설 — §0 Live Progress operational SSOT

§14.1-14.10 — Orchestrator-owned ephemeral progress dashboard:
- 14.1 권한·소유 (Orchestrator 단독 writer, .claude-work/progress/)
- 14.2 State source vs Cache invariant
- 14.3 §0 file 포맷
- 14.4 Status enum (7 markers + inline qualifier)
- 14.5 트리거 SSOT 표 (13 이벤트)
- 14.6 S3 snippet 7-lane 표
- 14.7 Render flow
- 14.8 Resume / corruption 처리
- 14.9 Multi-Story index
- 14.10 Story 완료 archive

Spec: docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md
EOF
)"
```

---

## Task 3: Update PMOAgent.md — input source 2 곳 추가

**Files:**
- Modify: `agents/PMOAgent.md` (line 104 area + line 115 area)

- [ ] **Step 3.1: Read PMO Story 완료 회고 input section**

Run:
```bash
sed -n '102,108p' agents/PMOAgent.md
```

Expected (current state):
```
### 2. Story 완료 회고 감사

Story 완료 직후 Orchestrator가 스폰. 입력: 해당 Story file §1-11 + FIX Ledger + GitHub Issue 코멘트 이력.

감사 항목:
```

- [ ] **Step 3.2: Modify Story 완료 회고 input source**

Use Edit on `agents/PMOAgent.md`. Replace:

```
Story 완료 직후 Orchestrator가 스폰. 입력: 해당 Story file §1-11 + FIX Ledger + GitHub Issue 코멘트 이력.
```

with:

```
Story 완료 직후 Orchestrator가 스폰. 입력: 해당 Story file §1-11 + FIX Ledger + GitHub Issue 코멘트 이력 + `.claude-work/progress/<KEY>.md` (Orchestrator-owned live progress trace).
```

- [ ] **Step 3.3: Read PMO Cross-Story 패턴 분석 section**

Run:
```bash
sed -n '115,127p' agents/PMOAgent.md
```

Expected (current state):
```
### 3. Cross-Story 패턴 분석 (다중 Story)

사용자 요청 시 또는 Epic 완료 시.

패턴 검출 대상:
- 반복되는 FIX 원인 유형 (예: "최근 5 Story 중 3건이 같은 Adapter 레이어 경계에서 P1 boundary 발생")
- ESCALATE 반복 위치 (어느 레인·어느 단계에서 자주 막히는가)
- 성능 게이트 실패 트렌드
- 같은 파일이 여러 Story에 걸쳐 수정되는 핫스팟

산출물: `[PMOAgent Cross-Story 감사]` 보고서. 패턴이 "설계 지침 부재"로 해석되면 **ADR 후보 발의**.
```

- [ ] **Step 3.4: Add Cross-Story input source line**

Use Edit on `agents/PMOAgent.md`. Replace:

```
### 3. Cross-Story 패턴 분석 (다중 Story)

사용자 요청 시 또는 Epic 완료 시.

패턴 검출 대상:
```

with:

```
### 3. Cross-Story 패턴 분석 (다중 Story)

사용자 요청 시 또는 Epic 완료 시. 입력: 다수 Story file §1-11 + 다수 FIX Ledger + `.claude-work/progress/_archive/**` (완료 Story 누적 progress trace).

패턴 검출 대상:
```

- [ ] **Step 3.5: Verify both PMO modifications**

Run:
```bash
grep -n "claude-work/progress" agents/PMOAgent.md
```

Expected: 2 lines matching (Story 완료 회고 + Cross-Story 패턴 분석).

- [ ] **Step 3.6: Commit**

```bash
git add agents/PMOAgent.md
git commit -m "$(cat <<'EOF'
feat(cfp-20): PMOAgent input source — .claude-work/progress/ 추가

- Story 완료 회고 입력에 .claude-work/progress/<KEY>.md 추가
- Cross-Story 패턴 분석 입력에 .claude-work/progress/_archive/** 추가

PMO 가 Orchestrator-owned live progress trace를 회고/패턴 분석 시 참조.

Spec: docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md §4.5
EOF
)"
```

---

## Task 4: Update CLAUDE.md — 컨텍스트 전달 섹션에 §0 progress 1줄 추가

**Files:**
- Modify: `CLAUDE.md` (line 142 다음)

- [ ] **Step 4.1: Read insertion point**

Run:
```bash
sed -n '138,148p' CLAUDE.md
```

Expected (current state):
```
### 컨텍스트 전달 (docs file SSOT + Context Packet)

각 Story마다 **`docs/stories/<KEY>.md`** 파일이 컨텍스트 단일 출처(SSOT). 에이전트 프롬프트에는 기본적으로 **docs file 경로만 주입**하고, 필요한 내용은 에이전트가 직접 `Read(docs/stories/<KEY>.md)`로 fetch.

**Context Packet 주입** (설계·구현·리뷰 레인): Orchestrator가 섹션 캐시를 유지해 에이전트 프롬프트에 packet 형태로 필요 섹션을 직접 삽입 → 반복 fetch 회피. 상세는 playbook §12.

**Project Config Packet** (DocsAgent·RequirementsPL·DomainAgent·PMO·ArchitectPLAgent): `.claude/_overlay/project.yaml` slice도 packet으로 주입 → GitHub 호출 에이전트의 반복 `Read` 회피. 상세는 playbook §12.5.
```

- [ ] **Step 4.2: Insert §0 progress reference**

Use Edit on `CLAUDE.md`. Replace:

```
**Context Packet 주입** (설계·구현·리뷰 레인): Orchestrator가 섹션 캐시를 유지해 에이전트 프롬프트에 packet 형태로 필요 섹션을 직접 삽입 → 반복 fetch 회피. 상세는 playbook §12.

**Project Config Packet** (DocsAgent·RequirementsPL·DomainAgent·PMO·ArchitectPLAgent): `.claude/_overlay/project.yaml` slice도 packet으로 주입 → GitHub 호출 에이전트의 반복 `Read` 회피. 상세는 playbook §12.5.
```

with:

```
**Context Packet 주입** (설계·구현·리뷰 레인): Orchestrator가 섹션 캐시를 유지해 에이전트 프롬프트에 packet 형태로 필요 섹션을 직접 삽입 → 반복 fetch 회피. 상세는 playbook §12.

**§0 Live Progress** (ephemeral derivative cache): `.claude-work/progress/<KEY>.md` (Orchestrator owner, gitignored). M3 hierarchical + S3 completion snippet 형식. 정상 흐름은 Orchestrator가 cache patch, 재개·손상 시 state source(Story §10 + phase label + §-fill)에서 재 derive. 상세는 playbook §14.

**Project Config Packet** (DocsAgent·RequirementsPL·DomainAgent·PMO·ArchitectPLAgent): `.claude/_overlay/project.yaml` slice도 packet으로 주입 → GitHub 호출 에이전트의 반복 `Read` 회피. 상세는 playbook §12.5.
```

- [ ] **Step 4.3: Verify CLAUDE.md modification**

Run:
```bash
grep -n "§0 Live Progress\|claude-work/progress" CLAUDE.md
```

Expected: 1 line matching (the new §0 reference paragraph).

- [ ] **Step 4.4: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
feat(cfp-20): CLAUDE.md 컨텍스트 전달 섹션에 §0 progress 1줄 추가

.claude-work/progress/<KEY>.md (Orchestrator owner, gitignored) 위치·소유·resume 정책 1줄 cross-reference. 상세는 playbook §14.

Spec: docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md §3
EOF
)"
```

---

## Task 5: Validate invariants + cross-references

**Files:** (검증만, 수정 없음 — 결과 따라 후속 fix 발생 가능)

- [ ] **Step 5.1: Verify .gitignore already covers .claude-work/**

Run:
```bash
grep -E '^\.claude-work/?$' .gitignore
```

Expected: 1 match (line 3 currently).

If no match: ADD `.claude-work/` to `.gitignore`. (Currently confirmed exists, no action needed.)

- [ ] **Step 5.2: Verify spec §8 변경 영향 표 ↔ 실제 변경 파일 정합**

Run:
```bash
git diff --name-only main..HEAD | sort
```

Expected output (5 paths):
```
CLAUDE.md
agents/PMOAgent.md
docs/orchestrator-playbook.md
docs/superpowers/plans/2026-04-28-cfp-20-live-progress.md
docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md
templates/progress-examples/01-simple-pass.md
templates/progress-examples/02-na-lane.md
templates/progress-examples/03-multi-fix.md
templates/progress-examples/04-reset-marker.md
templates/progress-examples/05-active-deputy.md
templates/progress-examples/06-r9-subset.md
templates/progress-examples/07-r11-fastpath.md
```

Spec §8 declares 5 modified files (playbook + PMO + CLAUDE + spec + templates dir). Plan file is additional (writing-plans output). 7 golden files per spec §7.1. Total 12 paths. ✅

- [ ] **Step 5.3: Verify §14 cross-reference from CLAUDE.md works**

Run:
```bash
grep -n "playbook §14" CLAUDE.md docs/orchestrator-playbook.md
```

Expected:
- `CLAUDE.md`: 1 reference (the new line added in Task 4)
- `docs/orchestrator-playbook.md`: 1 self-reference is OK (the §14 header itself, may not match pattern)

If no §14 reference in CLAUDE.md: re-check Task 4 step 4.2.

- [ ] **Step 5.4: Verify spec ↔ playbook §14 table parity**

Run:
```bash
grep -cE "^\| (Story 개시|Lane 진입|Deputy spawn|Deputy return|Lane PASS|Lane FIX|Lane 재진입|RESET 마커|Lane N/A|R9 subset|R11 fast-path)" docs/orchestrator-playbook.md docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md
```

Expected: Both files have same set of trigger event rows (count varies by formatting but row content identical for 11 base events).

- [ ] **Step 5.5: Verify all golden examples use canonical 7-lane order**

Run:
```bash
for f in templates/progress-examples/*.md; do
  echo "=== $f ==="
  grep -n "^[✅🔄⏸❌⏳⊘🔁]" "$f" | head -10
done
```

Expected: each file shows lanes in this order: 요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트.

- [ ] **Step 5.6: Verify no broken references in spec/plan**

Run:
```bash
grep -E "ADR-(00[1-6])" docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md docs/superpowers/plans/2026-04-28-cfp-20-live-progress.md
```

Expected: ADR-001 / ADR-004 / ADR-006 references only (existing ADRs at time of writing). ADR-007+ in golden examples are illustrative placeholders.

- [ ] **Step 5.7: No commit needed for Task 5 unless fixes required**

If steps 5.1-5.6 reveal any fix needed, commit with message:

```bash
git commit -m "fix(cfp-20): validation fix-up — <issue>"
```

If no fixes: skip this step. Proceed to Task 6.

---

## Task 6: Open Phase 1 PR (CFP-20 plugin meta change)

**Files:** (PR open만)

CFP-20은 plugin meta 변경 (templates/ + playbook §14 + cross-references). CLAUDE.md "강제 대상" 정책상 Story file 필요. 다만 단일 PR 으로 처리 (CFP-19 pattern). 구현 테스트·보안 테스트 lane은 N/A — plugin meta 코드 변경 없음.

- [ ] **Step 6.1: Verify branch name**

Run:
```bash
git branch --show-current
```

If on `main`: create branch first.
```bash
git checkout -b impl/cfp-20-live-progress
```

If already on `impl/cfp-20-live-progress`: continue.

- [ ] **Step 6.2: Push branch**

```bash
git push -u origin impl/cfp-20-live-progress
```

- [ ] **Step 6.3: Open PR**

```bash
gh pr create --title "feat(cfp-20): §0 Live Progress dashboard — playbook §14 + 7 golden examples" --body "$(cat <<'EOF'
## Summary

- CFP-20 Live Progress dashboard 도입 — Orchestrator-owned ephemeral §0
- Spec: \`docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md\`
- Plan: \`docs/superpowers/plans/2026-04-28-cfp-20-live-progress.md\`
- M3 hierarchical + S3 completion snippet, T3 hybrid trigger threshold
- Codex 독립 감사 반영 (5 concerns + 3 missing → 모두 design에 통합)

## Changes

- **playbook §14 신설** (10 sub-sections, ~150 줄) — Orchestrator §0 behavior SSOT
- **\`templates/progress-examples/\` 신설** — 7 golden render examples
- **PMOAgent.md** — input source에 \`.claude-work/progress/\` 2 곳 추가
- **CLAUDE.md** — 컨텍스트 전달 섹션에 §0 progress 1줄 추가

## Lane Status

- ✅ 요구사항 + 설계 — brainstorming + spec + plan 완료
- ⏸ 설계 리뷰 — 본 PR review가 lane 역할
- ⏸ 구현 — 본 PR commit 6건이 구현
- ⏸ 구현 리뷰 — 본 PR review가 lane 역할
- ⊘ 구현 테스트 — N/A (plugin meta, 코드 변경 없음. golden example diff 가 검증)
- ⊘ 보안 테스트 — N/A (plugin meta, 보안 영향 없음)

## Test plan

- [x] 7 golden examples 캐노니컬 7-lane 순서 + status enum 정합
- [x] playbook §14 ↔ spec 트리거 표 row 정합 (11 이벤트)
- [x] CLAUDE.md §0 cross-reference → playbook §14 도달
- [x] PMOAgent input source 2 곳 (Story 완료 + Cross-Story) 정합
- [x] .gitignore .claude-work/ 이미 ignore (line 3)
- [ ] Plugin self-application: CFP-21 first execution 시 §0 file 생성·갱신·archive 정상 동작 trace (별도 Story)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 6.4: Capture PR URL**

PR URL printed by previous step. Save for tracking. PR number will be referenced in Story file §11 참조.

---

## Manual Verification (post-merge)

CFP-20은 자동화 단위 테스트 없음 — golden examples + plugin self-application이 검증.

### V1: Plugin self-dogfooding (next CFP-21+ Story)

다음 Story 첫 실행 시 Orchestrator가:

1. `.claude-work/progress/CFP-21.md` 자동 생성 (모든 lane `⏸`)
2. 요구사항 lane 진입 시 → `🔄 요구사항 — 진행 중`
3. Deputy spawn (DomainAgent / Analyst / Researcher) → sub-tree에 `🔄 <Deputy>` 추가
4. Deputy 모두 return → `✅ <Deputy>` 전이
5. Lane PASS → `✅ 요구사항 — 통합 명세 §3-6 + 도메인 공백 N건` (S3 snippet)
6. 다음 lane 진입 → 같은 패턴 반복
7. Story 완료 → `_archive/CFP-21.md` 로 mv

trace 1회 manual review로 §14 SSOT 동작 검증.

### V2: Resume scenario

세션 압축 후 재개 시:

1. `.claude-work/progress/<KEY>.md` 존재 확인
2. Orchestrator가 Story §10 + phase label + §-fill 에서 재 derive
3. cache 재기록, last_processed_seq 갱신
4. 재 derive 결과가 phase label과 일치하는지 manual review

### V3: Multi-Story scenario

2 Story 동시 진행 (CFP-21 + CFP-22):

1. `.claude-work/progress/CFP-21.md` + `CFP-22.md` 둘 다 존재
2. `.claude-work/progress/index.md` 에 두 KEY + 현재 phase 기록
3. Orchestrator가 다음 작업 분기 시 index에서 활성 KEY 정확히 식별

---

## Self-Review (writing-plans 단계 inline 점검)

### 1. Spec coverage check

| Spec section | Plan task |
|---|---|
| §1 컨텍스트 (가시성 부재 분석) | 변경 없음 — context 기록만 |
| §2 Goals G1-G7 + Non-goals NG1-NG6 | Task 1 (G1-G3, M3+S3 골든) + Task 2 §14 (G4-G7 행동 정의) |
| §3 Architecture (state source vs cache) | Task 2 §14.1-§14.2 |
| §4 Components (file 포맷, status enum, qualifier, S3 표, index) | Task 1 (golden) + Task 2 §14.3-§14.6, §14.9 |
| §5 Data flow (트리거·갱신·narration) | Task 2 §14.5 트리거 SSOT 표 + §14.7 render flow |
| §6 Error handling (9 시나리오) | Task 2 §14.8 resume / corruption + §14.10 archive |
| §7 Testing (7 golden + invariant) | Task 1 (golden) + Task 5 (invariant) |
| §8 변경 영향 (5 파일) | Task 5.2 (변경 파일 정합 grep) |
| §9 Out of scope | 변경 없음 — 명시만 |
| §10 결정 history | 변경 없음 — 명시만 |
| §11 References | Task 4 (CLAUDE.md cross-reference) + Task 5.3 (검증) |

✅ 모든 spec section이 plan task로 mapping.

### 2. Placeholder scan

Plan 내 TBD/TODO/placeholder 검색 — `?` placeholder는 S3 snippet 패턴 정의의 일부 (의도적). 다른 placeholder 0건.

### 3. Type consistency

- "deputy", "qualifier", "snippet", "trigger" 용어 일관성: ✅ (spec과 plan 동일)
- 파일 경로 정합: ✅ (`.claude-work/progress/<KEY>.md` 일관)
- §섹션 번호 정합: ✅ (§14 = playbook 신설, §10 = Story file FIX Ledger)
- 마커 정합: ✅ (✅/🔄/⏸/❌/⏳/⊘/🔁 7종 동일)

✅ 일관성 검증 통과.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-28-cfp-20-live-progress.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Fresh subagent per task, review between tasks. Best for plugin meta change with multiple SSOT files.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch with checkpoints.

**Which approach?**
