---
spec_id: cfp-20
title: Live Progress Dashboard — Orchestrator-owned ephemeral §0 + 7-lane × phase 가시화
status: Approved
date: 2026-04-28
authors:
  - Orchestrator (brainstorming synthesizer)
  - CodexReviewAgent (independent audit, GPT-5)
related_adrs:
  - ADR-001 (review agent unification)
  - ADR-004 (ArchitectPL + SecurityArch)
  - ADR-006 (TestContractArch)
related_files:
  - docs/orchestrator-playbook.md (§14 신설)
  - agents/PMOAgent.md
  - CLAUDE.md
  - templates/progress-examples/ (신설)
---

## 0. 사용자 원문 (Verbatim)

> 이 codeforge를 통해서 진행되는 레인과 phase가 있는데 이것도 todolist 처럼 만들어서 진행상황과 완료되었다면 결과를 매 진행 때마다 수시로 보여줄 수 있나?

## 1. 컨텍스트 — 진행 가시성 부재

CodeForge v0.13.0 (CFP-19 머지 직후) 기준, Story 진행 상태는 다음 분산 source에서만 추적 가능:

- GitHub Issue `phase:*` 라벨 (현재 lane 1개만, 누적 진행 추적 불가)
- `docs/stories/<KEY>.md` §10 FIX Ledger (FIX 이벤트만)
- `docs/stories/<KEY>.md` §-fill 상태 (각 섹션 채워짐 여부 = 완료 lane 추론)
- 코멘트 phase prefix (10 lane prefix · DocsAgent 단독 기록)

이 구조는 **합산된 live dashboard 가 없어** 사용자가 "지금 어디까지 진행됐고 deputy 단위로 무엇이 돌아가는가"를 한 화면에서 볼 수 없다. 특히 CFP-19 도입 병렬 이벤트(R3 review parallel, R4 진단 parallel, R7 2-track, R9 test subset, R10 prefetch, R11 fast-path) 이후 **lane 내부 동시 진행** 까지 늘어 가시성 격차가 더 커졌다.

### 1.1 todolist UX 직관

사용자 원문 "todolist 처럼"은 다음 3 요건을 함의:
- (a) **상태 마커** — 각 항목이 pending / in-progress / done 명확히 구분
- (b) **수시 업데이트** — 진행 변경 시마다 즉시 반영 (이벤트 기반)
- (c) **완료 결과 표기** — done 항목에 결과 한 줄 (todolist의 "취소선" + 완료 메모 패턴)

## 2. 목표 + Non-goals

### 2.1 Goals

1. **G1**: 7 lane (요구사항·설계·설계리뷰·구현·구현리뷰·구현테스트·보안테스트) 진행 상태를 1 화면 markdown으로 가시화
2. **G2**: 활성 lane은 deputy sub-tree expand, 나머지는 collapsed (M3 hierarchical)
3. **G3**: 완료 lane은 1줄 결과 snippet (S3 — Change Plan 버전·ADR·PR 번호 등 lane별 산출물 요약)
4. **G4**: 매 lane 경계 이벤트(진입·PASS·FAIL·FIX·RESET·N/A) 시 사용자 terminal narration
5. **G5**: 활성 lane deputy 진행은 file에만 갱신 (terminal noise 방지, 필요 시 사용자 명시 요청으로 노출)
6. **G6**: 세션 재개 시 자동 복원 (state source에서 derive)
7. **G7**: PMOAgent 회고/Cross-Story 분석 input 으로 활용

### 2.2 Non-goals

- **NG1**: GitHub Issue body 안에 progress 미러링 (DocsAgent single-writer 영역 침범)
- **NG2**: PR diff에 §0 commit 노출 (commit churn 방지)
- **NG3**: 자동 progress notification (Slack/email 등 외부 알림)
- **NG4**: Multi-Story 동시 진행 시 합쳐진 dashboard (각 KEY별 separate file 유지, pointer만 index)
- **NG5**: Cache-hit / R10 prefetch 같은 사용자 무관 메타 이벤트 표기 (의도적 skip)
- **NG6**: §0 file이 commit되거나 deliverable이 되는 모델 (cache로 유지)

## 3. Architecture (Ownership + State source)

### 3.1 핵심 invariant

```
State source (committed, durable):
  - docs/stories/<KEY>.md §10 FIX Ledger    → FIX 카운터 + RESET 마커
  - docs/stories/<KEY>.md §-fill state      → 완료 lane 추론
  - GitHub Issue phase label                → 현재 lane

Derivative cache (ephemeral, gitignored):
  - .claude-work/progress/<KEY>.md          → rendered §0 (M3 + S3)
  - .claude-work/progress/index.md          → multi-Story pointer
  - .claude-work/progress/_archive/<KEY>.md → Story 완료 후 PMO 회고용

Orchestrator role:
  - 정상 흐름: 매 이벤트마다 cache 직접 patch (read-patch-write, 저비용)
  - 세션 재개 / 손상 / 모순 감지 시: state source에서 재 derive 후 cache 재기록
  - cache는 항상 source로부터 재구성 가능 (idempotent — cache 손실은 데이터 손실이 아님)
  - lane boundary 이벤트만 terminal narration

DocsAgent / doc-queue / Story file: 무관여
```

### 3.2 권한·소유

| 컴포넌트 | Writer | Reader |
|---|---|---|
| `.claude-work/progress/<KEY>.md` | **Orchestrator 단독** | Orchestrator (resume), PMOAgent (회고), 사용자 (수동) |
| `.claude-work/progress/index.md` | Orchestrator 단독 | Orchestrator (multi-Story 분기) |
| `.claude-work/progress/_archive/**` | Orchestrator (Story 완료 시 mv) | PMOAgent (Cross-Story 패턴) |
| Terminal narration | Orchestrator (lane boundary 시) | 사용자 |

DocsAgent는 본 spec 범위 밖. doc-queue·docs/stories/<KEY>.md·GitHub Issue body 모두 변경 없음.

### 3.3 race·corruption 처리

- **Race**: §0 갱신 이벤트(lane PASS / FIX / deputy spawn-return / RESET)는 모두 Orchestrator의 Agent tool 결과 수신 시점에 발생. Agent tool returns는 Orchestrator session 내 sequential하므로 file write race는 없음
- **Corruption**: file 헤더에 `last_processed_seq: <N>` (monotonic counter). resume 시 source에서 항상 재 derive 가능하므로 corruption은 sanity check 수준 — 손상돼도 다음 이벤트에서 자동 회복

## 4. Components

### 4.1 §0 file 포맷

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

- frontmatter 없이 plain markdown (yaml-style 메타 4줄)
- Story 시작 시 모든 lane `⏸` 으로 init
- Story 완료 시 `_archive/<KEY>.md` 로 mv (PMOAgent Cross-Story 분석 input 보존)

### 4.2 Status enum

| 마커 | 의미 | 사용 위치 |
|---|---|---|
| `⏸` | pending | Lane top, deputy slot |
| `🔄` | in-progress | Lane top, deputy slot |
| `✅` | PASS / done | Lane top (S3 snippet 동반), deputy slot |
| `❌ FIX-N` | FIX 진행 중 | Lane top (evidence 1줄 동반) |
| `❌ FIX-N (fast-path)` | R11 mechanical fast-path | Lane top (typo·broken-link·minor-naming·comment-only 카테고리) |
| `⏳` | blocked | Lane top (사용자 응답·외부 의존성 대기) |
| `⊘ N/A` | skip (plugin meta lane 등) | Lane top (사유 동반) |
| `🔁 RESET-N` | 구현 리뷰 RESET | 구현테스트·보안테스트 → 구현 회귀 시 |

### 4.3 Active lane inline qualifier

활성 lane top 라인에 deputy 진행률 inline 표기:

- `🔄 설계 — 진행 중 (3/4 deputies)` — deputy 4인 중 3 done
- `🔄 구현 테스트 — 진행 중 (functional ✅ / performance 🔄)` — R9 subset 병렬
- `🔄 보안 테스트 — 진행 중 (1차 layer ✅ / 2차 layer 🔄)` — 1·2차 layer 분리

### 4.4 S3 snippet 7-lane 표 (Lane PASS 시 1줄)

| Lane | snippet 템플릿 | source |
|---|---|---|
| 요구사항 | `통합 명세 §3-6 + 도메인 공백 <N>건` | RequirementsPL 통합 + DomainAgent 결과 |
| 설계 | `Change Plan v<N> + ADR-<NNN> <신규\|변경> (deputy <M>인)` | ArchitectPL + ADR file mtime |
| 설계 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | DesignReviewPL packet |
| 구현 | `Phase 2 PR #<num> · <commit>건 · §8.5 manifest <file>건` | DeveloperPL 보고 + git log |
| 구현 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | CodeReviewPL packet |
| 구현 테스트 | `functional <PASS\|FAIL>, performance Δ <±N%>` | TestAgent subset 보고 |
| 보안 테스트 | `1차 alerts <N> / 2차 P0:<N> P1:<N>` | SecurityTestPL packet |

미정 데이터는 `?` placeholder (예: `Change Plan v? + ADR-? 신규 (deputy 4인)` — render 시점 source 미가용 시).

### 4.5 Multi-Story index 파일

```markdown
# Active Stories Index

last_updated: <ISO8601>

- CFP-20 (phase: 설계, fix_cycle: 0)
- CFP-21 (phase: 구현 리뷰, fix_cycle: 1)
```

- Orchestrator가 모든 active Story KEY + 현재 phase 만 기록
- "always latest" pointer로 사용 (Orchestrator가 다음 작업 분기 시 어떤 Story가 진행 중인지 파악)
- SSOT 아님 — 각 KEY의 진실은 `<KEY>.md` 와 state source

## 5. Data Flow (트리거 → 갱신 → narration)

### 5.1 갱신 흐름

```
[Lane/Deputy event 발생]
  └→ Orchestrator 1차 수신
       ├→ 1) Read(.claude-work/progress/<KEY>.md)  (cache)
       ├→ 2) parse → 해당 lane sub-tree patch
       ├→ 3) Write(.claude-work/progress/<KEY>.md) — full rewrite, last_processed_seq 증가
       ├→ 4) lane boundary 이벤트일 때만 → terminal narration emit
       │       (deputy spawn/return 은 file만, terminal noise 방지)
       └→ 5) Story 완료 시 _archive/<KEY>.md 로 mv + index.md 갱신
```

### 5.2 트리거 SSOT 표

| 이벤트 | 영향 라인 | 갱신 동작 | terminal narration |
|---|---|---|---|
| Story 개시 | 전체 | file create, 7 lane `⏸` | ✅ |
| Lane 진입 | top | `⏸` → `🔄 진행 중`, current_lane 갱신 | ✅ |
| Deputy spawn | active sub-tree | `🔄 <Deputy>` 추가, qualifier 갱신 | ❌ (file only) |
| Deputy return | active sub-tree | `🔄` → `✅`, qualifier 갱신 | ❌ (file only) |
| 병렬 dispatch (R3·R4·R7·R9) | active sub-tree | 두 deputy 동시에 `🔄` 라인 추가 | ❌ (file only) |
| R9 subset 시작 | 구현 테스트 | inline qualifier `(functional 🔄 / performance ⏸)` | ✅ |
| R9 subset 완료 | 구현 테스트 | qualifier 갱신 (둘 다 결과 반영) | ❌ (lane PASS/FIX 시 별도 narration) |
| R11 fast-path | 해당 lane | `❌ FIX-N (fast-path)` 마커 | ✅ |
| Lane PASS | top | `🔄` → `✅ — <S3 snippet>`, sub-tree 접음 | ✅ |
| Lane FIX | top | `🔄` → `❌ FIX-N — <evidence 1줄>`, fix_cycle 갱신 | ✅ |
| Lane 재진입 (FIX 후) | top | `❌ FIX-N` → `🔄 진행 중 (FIX-N)` | ✅ |
| RESET 마커 | 구현 리뷰 | `✅` → `🔁 RESET-N` | ✅ |
| Lane N/A (plugin meta) | top | `⏸` → `⊘ N/A — <사유>` | ✅ |
| 사용자 "진행상황 보여줘" | — | file 변경 없이 현재 §0 전체 emit | ✅ (deputy 포함 full) |
| Story 완료 | 전체 | 모두 `✅`, archive 이동, index 갱신 | ✅ |

## 6. Error Handling / Edge Cases

| 시나리오 | 처리 |
|---|---|
| 세션 재개 시 file 부재 | Orchestrator가 **state source** (Story §10 + phase label + §-fill) 에서 derive → file 재생성. deputy sub-tree는 비워둠 (활성 deputy 정보 손실 허용 — 다음 deputy 이벤트에서 자동 충족) |
| 세션 재개 시 file 존재 | **state source에서 항상 재 derive** 후 file 갱신 (cache는 신뢰하지 않음). last_processed_seq 만 보존 |
| `.claude-work/progress/` 디렉토리 부재 | Orchestrator가 `mkdir -p` 후 file create |
| `.claude-work/progress/_archive/` 부재 | Story 완료 시 Orchestrator가 `mkdir -p` 후 mv |
| 병렬 deputy 동시 return (R3·R4·R7·R9) | Agent tool returns는 Orchestrator session 내 sequential — race 없음. 두 deputy 모두 같은 ms에 return 해도 read-patch-write가 직렬로 완료된 뒤 다음 처리 |
| Story 중도 폐기 | Orchestrator가 `_archive/<KEY>-aborted.md` 로 mv, narration "Story 폐기" |
| Plugin meta lane skip (CFP-N/A 보안테스트) | `⊘ N/A — plugin meta` 마커, snippet 자리에 사유 |
| 파일 손상 (수동 편집 등) | Orchestrator가 parse 실패 시 backup(`<KEY>.md.bak`) → state source에서 재 derive |
| Multi-Story 2+ 진행 중 | 각 KEY별 separate `<KEY>.md` 유지. index.md가 active 목록 보유. Orchestrator가 사용자 입력으로 KEY 분기 결정 (playbook §7.1 기존 multi-Story 핸들링 재사용) |

## 7. Testing / Verification

CFP-20은 UX·rendering 변경이므로 단위 테스트보다 **golden example 비교 + invariant grep** 위주.

### 7.1 Golden examples (`templates/progress-examples/` 신설)

| 파일 | 검증 시나리오 |
|---|---|
| `01-simple-pass.md` | 7 lane 모두 ✅ — 기본 happy path |
| `02-na-lane.md` | 보안 테스트 `⊘ N/A — plugin meta` (CFP-NN 자가적용 시) |
| `03-multi-fix.md` | 설계 리뷰 FIX-1 → FIX-2 → PASS, 구현 리뷰 FIX-1 → PASS, 구현 테스트 RESET-1 |
| `04-reset-marker.md` | 보안 테스트 FAIL → 설계 회귀 → 구현 리뷰 `🔁 RESET-1` 마커 |
| `05-active-deputy.md` | 설계 lane 활성, 4 deputy 중 3 완료, qualifier `(3/4 deputies)` |
| `06-r9-subset.md` | 구현 테스트 lane qualifier `(functional ✅ / performance 🔄)` |
| `07-r11-fastpath.md` | 구현 리뷰 `❌ FIX-1 (fast-path)` 마커 |

### 7.2 Invariant 검증

| 항목 | 방식 |
|---|---|
| `.claude-work/` gitignore | `grep -q '^\.claude-work/$' .gitignore` (이미 만족 — 확인 완료) |
| §14 신설 위치 | playbook 부록 A·B 앞에 §14 존재 (manual review) |
| Render 멱등성 | golden example 1 → 같은 이벤트 시퀀스 → 같은 §0 출력 (manual diff) |

### 7.3 Plugin self-application

CFP-21 이후 Story 첫 실행에서 `.claude-work/progress/CFP-21.md` 가 모든 lane을 `⏸ → 🔄 → ✅` 순으로 진행하는지 1회 trace (dogfooding).

자동화된 테스트는 본 Story 범위 외 — golden example + plugin self-dogfooding이 가장 강한 검증.

## 8. 변경 영향 (수정 대상 파일)

| 파일 | 변경 유형 | 분량 |
|---|---|---|
| `docs/orchestrator-playbook.md` | 신규 §14 "§0 Live Progress" — 부록 A·B 앞 | ~150 줄 |
| `agents/PMOAgent.md` | 회고/Cross-Story input source에 `.claude-work/progress/<KEY>.md` 추가 | 1 줄 |
| `CLAUDE.md` | 컨텍스트 전달 단락에 "§0 progress는 .claude-work/progress/<KEY>.md (Orchestrator owner)" 1줄 | 1 줄 |
| `templates/progress-examples/` | 신설 디렉토리 + golden 7 파일 | ~150 줄 (7 파일 합계) |
| `docs/superpowers/specs/2026-04-28-cfp-20-live-progress-design.md` | 본 spec 신규 | ~400 줄 |
| `.gitignore` | **무변경** (`.claude-work/` 이미 ignore) | 0 줄 |
| `agents/DocsAgent.md` | **무변경** | 0 줄 |
| `templates/story-page-structure.md` | **무변경** | 0 줄 |
| 모든 PL agent md / 워크플로우 yml | **무변경** | 0 줄 |

## 9. Out of Scope

- 별도 GitHub Action 으로 progress 자동 commit (commit churn 방지 의도와 정면 충돌)
- VS Code extension / TUI 등 별도 viewer (markdown file 으로 충분 — 사용자가 IDE에서 직접 열기 가능)
- progress → external notification (Slack·email)
- §0 → GitHub Issue body sync (DocsAgent 영역 침범)
- automated render unit test (over-engineering — golden example diff로 충분)
- `last_processed_seq` 기반 event sourcing 풀 도입 (Codex C5 검토 결과 over-engineering 판정)

## 10. 결정 history (Brainstorming → Codex 감사 → 최종)

### 10.1 Brainstorming 7개 결정

| Q | 결정 | 추천 이유 |
|---|---|---|
| Q1 frequency | F3 hybrid | lane events auto + explicit 사용자 요청 + always-latest §0 file |
| Q2 data model | M3 hierarchical | "todolist 처럼" 직관 부합, collapsed/expanded 자연 |
| Q3 trigger | T3 hybrid threshold | top-level은 lane 경계만, active lane만 deputy 단위, FIX evidence freeze |
| Q4 status enum | S3 (S2 + completion snippet) | "결과를 보여줄 수 있나" 의도 직접 충족, PASS 시 1회 set이라 churn 0 |
| Q5 location | (revoked) | 초안 L1 (Story file §0) → 사용자 push back 후 revoked |
| Q6 ownership | P1 (Orchestrator + .claude-work/) | DocsAgent 책임 분리, ephemeral 명확화 |
| Q7 render rules | playbook §14 신설 | 7-lane snippet 표 + 트리거 SSOT |

### 10.2 Codex 감사 반영 (5 concerns + 3 missing)

- **C1**: §13 collision (이미 PMOAgent) → §14로 변경
- **C2**: R9/R10/R11 가시성 — R9·R11 추가, R10 의도적 skip 유지
- **C3**: parallel inline qualifier (`3/4 deputies`) 추가
- **C4**: resume derive logic — Codex 정정 반영 (Story §10 + phase label + §-fill)
- **C5**: corruption — last_processed_seq sanity check만 (event sourcing 풀 도입 X)
- **M1**: multi-Story index.md 신설
- **M2**: golden examples 7종 (`templates/progress-examples/`)
- **M3**: state source vs cache 재기술 — invariant section 추가 (file은 derivative cache, source는 §10 + phase label + §-fill)

## 11. References

- CLAUDE.md (DocsAgent single-writer 원칙, story-init.yml workflow, §10 FIX Ledger SSOT)
- docs/orchestrator-playbook.md §7 (resume), §11 (DocsAgent doc-queue), §13 (PMOAgent)
- agents/DocsAgent.md (commit deliverable writer scope)
- agents/PMOAgent.md (Cross-cutting 회고/패턴 분석 책임)
- docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md (R3·R4·R7·R9·R10·R11 정의)
- docs/adr/ADR-001-review-agent-unification.md
- docs/adr/ADR-004-architectpl-securityarch.md
- docs/adr/ADR-006-testcontractarch.md (CFP-18)
