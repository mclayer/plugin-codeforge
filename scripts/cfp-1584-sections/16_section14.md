## 14. §0 Live Progress (CFP-20)

`.claude-work/progress/<KEY>.md` 파일에 Orchestrator가 7-lane × phase 진행 상황을 M3 hierarchical + S3 completion snippet 형식으로 기록한다. PR diff에 노출 X (gitignored), GitHub Issue body 미러링 X (lane plugin self-write 영역과 분리). 사용자 원문 "todolist 처럼 매 진행 때마다 수시로 보여" 의도 충족.

### 14.1 권한·소유

| 컴포넌트 | Writer | Reader |
|---|---|---|
| `.claude-work/progress/<KEY>.md` | **Orchestrator 단독** | Orchestrator (resume), PMOAgent (회고), 사용자 (수동) |
| `.claude-work/progress/index.md` | Orchestrator 단독 | Orchestrator (multi-Story 분기) |
| `.claude-work/progress/_archive/<KEY>.md` | Orchestrator (Story 완료 시 mv) | PMOAgent (Cross-Story 패턴) |

doc-queue (사용 안 함 — ζ arc 완료) / docs/stories/<KEY>.md 직접 write (lane plugin self-write) / GitHub Issue body: **progress file 과 무관**.

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
⏳ 설계 — 진행 중 (6/6 deputies, chief author 통합 중)
   ├─ ✅ CodebaseMapperAgent
   ├─ ✅ RefactorAgent
   ├─ ✅ SecurityArchitectAgent
   ├─ ✅ OperationalRiskArchitectAgent
   ├─ ✅ TestContractArchitectAgent
   ├─ ✅ DataMigrationArchitectAgent
   └─ ⏳ ArchitectAgent (chief author) — Change Plan §3 author 중
⬜ 설계 리뷰
⬜ 구현
⬜ 구현 리뷰
⬜ 구현 테스트
⬜ 보안 테스트
```

- frontmatter 없이 plain markdown + yaml-style 메타 4줄
- Story 시작 시 모든 lane `⬜` init (CFP-707 Amendment 4 — `⏸` deprecated, `⬜` empty checkbox 통일)
- Story 완료 시 `_archive/<KEY>.md` 로 mv (PMO Cross-Story 분석 input 보존)

### 14.4 Status enum (ADR-041, 4 marker — CFP-707 Amendment 4 vocabulary swap)

| 마커 | 의미 | TodoWrite native state | 사용 위치 |
|---|---|---|---|
| `⬜` | pending — 시작 안 됨 (empty checkbox) | `pending` | Lane row, agent sub-row |
| `⏳` | in_progress — 진행 중 (모래시계 시간 흐름) | `in_progress` | Lane row, agent sub-row |
| `✅` | completed — PASS / N/A / 검출 성공 / FIX 원인 lane (content suffix `FIX-N 원인 · <판정>`) | `completed` | Lane row, agent sub-row |
| `🔄` | FIX 검출 lane — retry trigger (회전 = 다시 시작) | `in_progress` (content `FIX-N detected (cause: <원인 lane>)`) | Lane row only |

**검출 label 정규화**: review/test lane 의 terminal detection 이 FAIL 인 경우에도 TodoWrite content label 은 `FAIL detected` 를 쓰지 않고 `FIX-N detected` 로 정규화한다. RESET 이 필요한 경우에도 `FIX-N detected (cause: <원인 lane>, RESET-N)` 형식. `FAIL` 은 review/test 판정 흐름의 terminal outcome vocabulary 로만 남고, TodoWrite row label 은 `FIX-N detected` 가 canonical.

**N/A**: ✅ marker + content prefix `N/A · <사유>`. PASS 와 시각 차별 (텍스트 차이).
**RESET**: ✅ marker (원인 lane content suffix `FIX-N 원인 · <판정>` 보존) + 새 lane row append (`(재진입 RESET-N)` suffix).
**blocked / waiting**: 4-marker vocabulary 범위 밖. 대기 상태는 ⬜ pending 으로 표현, 진행 중 차단성 작업은 ⏳ in_progress row 의 content 1줄 설명으로 표현.

기존 8 marker (⏸ ⏳-blocked 🔄 ✅ ❌ FIX-N ❌ FIX-N(fast-path) ⊘ 🔁) 폐기. **CFP-707 Amendment 4 vocab swap**: `⏳ pending` → `⬜` / `🔄 in_progress` → `⏳` / `❌ FIX 원인 lane` → `🔄 FIX 검출 lane` (semantic 정정 동반 — §결정 3). file / TodoWrite 두 channel 동일 어휘.

활성 lane row 라인에 inline qualifier (예: `⏳ 설계` content 미동반, sub-row 가 detail 표현. PASS 시 `✅ 설계 - PASS · Change Plan v1 + ADR-NNN`).

### 14.5 트리거 SSOT

**Verbosity policy (CFP-114 / ADR-029)** — `terminal narration` 컬럼은 `progress_narration_verbosity` 값 기반 적용:
- `full` (default, ADR-029 §결정 1+4) — 모든 ✅ 표기 항목 narrate (sub-step 포함)
- `lane_only` — lane-level event 만 narrate (CFP-20 기존 동작, sub-step 표기는 file-only 로 fallback)

| 이벤트 | 영향 라인 | 갱신 동작 | terminal narration | TodoWrite 갱신 (ADR-041 — CFP-707 Amendment 4) | full/lane_only |
|---|---|---|---|---|---|
| Story 개시 | 전체 | file create, 7 lane `⬜` | ✅ | 7 lane row ⬜ seed | both |
| Lane 진입 | top | `⬜` → `⏳ 진행 중`, current_lane 갱신 | ✅ | lane row ⬜ → ⏳ + agent sub-row 펼침 | both |
| Deputy spawn | active sub-tree | `⏳ <Deputy>` 추가, qualifier 갱신 | ✅ | agent sub-row 추가 (status=in_progress) | full only |
| Deputy return | active sub-tree | `⏳` → `✅`, qualifier 갱신 | ✅ | agent sub-row status=completed | full only |
| 병렬 dispatch (R3·R4·R7·R9) | active sub-tree | 두 SubAgent 동시 `⏳` 라인 추가 | ✅ | agent sub-row 다수 동시 in_progress (multi-row deviation) | full only |
| CI gate 시작 | 구현 테스트 | inline qualifier `(gh pr checks ⏳)` | ✅ | CI gate sub-row inline qualifier | both |
| CI gate 완료 | 구현 테스트 | qualifier 갱신 | ✅ | CI gate sub-row 갱신 | full only |
| R11 fast-path | 해당 lane | `🔄 FIX-N (fast-path)` 마커 | ✅ | lane row → ✅ collapsed, content "PASS · R11 mechanical fast-path" | both |
| Lane PASS | top | `⏳` → `✅ — <S3 snippet>`, sub-tree 접음 | ✅ | lane row → ✅ + S3 snippet, agent sub-row 제거 | both |
| Lane FIX | top | 검출 lane `⏳` → `🔄 FIX-N — <evidence 1줄>`, fix_cycle 갱신 | ✅ | 검출 lane → 🔄 + content "FIX-N detected (cause: X, retry trigger)" + 원인 lane → ✅ 유지 + content suffix "FIX-N 원인 · <판정>" + 재진입 lane row append | both |
| Lane 재진입 (FIX 후) | top | 재진입 lane row append `⏳ 진행 중 (FIX-N 재진입)` | ✅ | 재진입 lane row → ⏳ + agent sub-row 펼침 | both |
| RESET 마커 | 구현 리뷰 | `✅` → `🔁 RESET-N` | ✅ | 재진입 lane row append (suffix "(재진입 RESET-N)") | both |
| Lane N/A (plugin meta) | top | `⬜` → `⊘ N/A — <사유>` | ✅ | lane row → ✅ + content "N/A · <사유>" | both |
| 사용자 "진행상황 보여줘" | — | file 변경 없이 현재 §0 전체 emit | ✅ (SubAgent 포함 full) | TodoWrite 도 emit (file + TodoWrite 동시) | both |
| Story 완료 | 전체 | 모두 `✅`, archive mv, index 갱신 | ✅ | 7 lane row 모두 ✅, 최종 state | both |

R10 prefetch (security 1차 layer cache) 같은 사용자 무관 메타 이벤트는 **의도적 skip** (verbosity 무관).

**TodoWrite 시도 의무 + 실패 non-blocking 원칙 (ADR-041 + ADR-038 Amendment 1 §결정 8)**: 두 속성을 명확히 분리한다.

- **시도 의무 (non-skippable)**: 위 표의 TodoWrite 갱신 컬럼에 표시된 이벤트 각각에서 Orchestrator 는 TodoWrite 갱신을 **반드시 시도**해야 한다. 시도 자체를 건너뛰는 것은 ADR-038 §결정 8 위반이다.
- **실패 처리 (non-blocking)**: 시도 후 갱신 실패 시 — lane primary work 미차단. lane 은 계속 진행하고, TodoWrite discrepancy 는 warning 으로 surface 한다. 사용자 confirmation / polling / acknowledgment wait 도입 없음 (ADR-029 stop discipline 정책 무영향).

"시도를 건너뛰는 것" 과 "시도했으나 실패한 것" 은 별개의 위반이다.

**Single-Story collision rule (ADR-041)**: single-Story 모드에서도 두 concurrent lane spawn 이 같은 Story 의 TodoWrite 를 동시에 write 할 수 있다. collision 발생 시:
1. canonical §14 Lane Evidence table state 에서 todo list 전체를 재구성
2. TodoWrite hard-reset 수행: 기존 todo list 를 부분 수정하지 않고 full rewrite
3. rewrite 후 active lane / agent sub-row 는 canonical state 에 남아 있는 evidence 만 반영
4. hard-reset 결과와 collision warning 을 terminal narration / wrapper warning 으로 surface
5. lane primary work 는 중단하지 않고 계속 진행

incremental patch 금지 — collision 의심 시 항상 full rewrite.

**Narration format (ADR-029 §결정 2)** — `[<lane-한국어>] <event>: <detail>` 1 sentence stderr line. 예시:

```
[설계] Deputy spawn 6/6 병렬 (CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch)
[설계] DataMigrationArchitectAgent return — §11 Migration 전략 + Rollback 경로 author 완료
[설계 리뷰] R7 병렬 dispatch — DesignReviewPL ∥ DeveloperPL Phase 2 PR 준비
[구현 테스트] CI gate 실행 중 — `gh pr checks` watching (timeout 30분)
```

세부 rule: 한국어 lane 이름, 멀티라인 금지, stderr only (file-write 와 격리). Stop discipline 정책은 ADR-022 §결정 2 + ADR-025 SSOT (본 §14.5 는 visibility 만 다룸).

### 14.6 S3 snippet 7-lane 표 (Lane PASS 시 1줄)

| Lane | snippet 템플릿 | source |
|---|---|---|
| 요구사항 | `통합 명세 §3-6 + 도메인 공백 <N>건` | RequirementsPL 통합 + DomainAgent |
| 설계 | `Change Plan v<N> + ADR-<NNN> <신규\|변경> (SubAgent <M>인)` | ArchitectPL + ADR file mtime |
| 설계 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | DesignReviewPL packet |
| 구현 | `Phase 2 PR #<num> · <commit>건 · §8.5 manifest <file>건` | DeveloperPL + git log |
| 구현 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | CodeReviewPL packet |
| 구현 테스트 | `CI gate <PASS\|FAIL> — checks <N>건` | `gh pr checks` 출력 |
| 보안 테스트 | `1차 alerts <N> / 2차 P0:<N> P1:<N>` | SecurityTestPL packet |

미정 데이터는 `?` placeholder (예: `Change Plan v? + ADR-? 신규 (SubAgent 6인)`).

### 14.7 Render flow

```
[Lane/Deputy event 발생]
  └→ Orchestrator 1차 수신
       ├→ 1) Read(.claude-work/progress/<KEY>.md)  (cache)
       ├→ 2) parse → 해당 lane sub-tree patch
       ├→ 3) Write(.claude-work/progress/<KEY>.md) — full rewrite, last_processed_seq 증가
       ├→ 4) terminal narration emit (ADR-029)
       ├→ 5) ★ TodoWrite update — non-skippable 시도 (ADR-038 §결정 8) / failure non-blocking (ADR-038 §결정 7)
       └→ 6) Story 완료 시 _archive/<KEY>.md 로 mv + index.md 갱신
```

**TodoWrite update (step 5) detail (ADR-041 — CFP-707 Amendment 4)**:
- Lane 진입: lane row → ⏳ + agent sub-row 펼침 (PL → workers/deputies → chief 순)
- Agent return: 해당 agent sub-row 의 status=completed + content 갱신 (1-line 활동 결과)
- Lane PASS: agent sub-row 제거, lane row content = `PASS · <S3 snippet>`
- Lane FIX (검출 후): 검출 lane → 🔄 + content `FIX-N detected (cause: <원인 lane>, retry trigger)`, 원인 lane → ✅ 유지 + content suffix `FIX-N 원인 · <원인 판정 1줄>` (lane PASS evidence 보존, FIX trigger origin 은 content text 로 책임 추적), 재진입 lane row append (⏳ 시작)
- Multi-row in_progress 의도적 허용 (TodoWrite "ONE in_progress" 가이드 deviation, codeforge 병렬 agent 모델)
- Single-Story 모드 — `[KEY]` prefix drop (모든 row 에서)
- 시도 의무: step 5 건너뛰기는 ADR-038 §결정 8 위반 (시도 후 실패는 §결정 7 — non-blocking)
- 실패 처리: TodoWrite update 실패 시 warning, lane primary work 미차단 (§14.5 원칙)

### 14.8 Resume / corruption 처리

세션 재개 / 압축 재개 시:

1. `.claude-work/progress/<KEY>.md` 존재 여부 확인
2. **존재해도 신뢰하지 않음** — state source(Story §10 + GitHub Issue phase label + Story §-fill state)에서 재 derive
3. 재 derive 결과를 cache 재기록, last_processed_seq 갱신
4. **★ TodoWrite re-build (ADR-041 NEW — CFP-707 Amendment 4 vocab)**: §0 file 의 lane 별도 status 로 TodoWrite full rewrite
   - active lane 의 agent sub-row 는 빈 상태 (SubAgent 활성 정보 손실 허용 — 다음 SubAgent 이벤트에서 자동 충족)
   - 4 marker (⬜ ⏳ ✅ 🔄) 어휘로 변환
   - Single-Story 모드 — `[KEY]` prefix drop
   - best-effort — TodoWrite re-build 실패 시 아래 경고 출력 후 file-only 상태로 lane work 진행 (ADR-038 §결정 7):
     `⚠️ TodoWrite 재빌드 실패 — 진행상황 표시가 부정확할 수 있습니다. 현재 상태: <§14 Lane Evidence 최신 row>`
5. SubAgent sub-tree 는 비워둠 (file + TodoWrite 동일 — 다음 SubAgent 이벤트에서 자동 충족)

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

### 14.11 Spawn ID 대장 mini-table (Issue #312)

Orchestrator 는 매 agent spawn 시 **Spawn ID 대장**을 `.claude-work/progress/<KEY>.md` 에 실시간 갱신한다. 목적: SendMessage target 모호성 해소 + 병렬 spawn 추적.

**포맷**:

```markdown
## Spawn ID 대장

| spawn_id | agent_type | lane | spawn_at |
|---|---|---|---|
| spawn-001 | RequirementsPLAgent | 요구사항 | 2026-05-09T10:00:00Z |
| spawn-002 | DomainAgent | 요구사항 | 2026-05-09T10:00:05Z |
| spawn-003 | ArchitectPLAgent | 설계 | 2026-05-09T10:15:00Z |
```

**갱신 의무**:
- spawn 직전 (spawn_at 기록 시점) 에 row 추가 — return 대기 없이 즉시 기록.
- spawn_id 형식: `spawn-NNN` (전역 단조 증가, Story 전체 통합 카운터).
- `agent_type` = agent file 식별자 (예: `ArchitectAgent`, `role:dev:SoftwareDeveloperAgent`).
- `lane` = 해당 spawn 의 진입 레인 (예: 설계, 구현, 구현-리뷰).
- `spawn_at` = ISO 8601 UTC. **§14 본문 markdown 표 Start/End column = KST `+09:00` (display layer — ADR-079 §결정 9 dual-layer co-existence)**. schema field `spawned_at`/`returned_at` = UTC strict 보존 (contract field layer).

**팀 컨텍스트 (env=1)**:
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 시 SendMessage 대상 지정에 spawn_id 를 사용 (teammate 이름 중복 시 spawn_id 로 disambiguate).
- TeamCreate 전·후로 스폰된 PL / teammate 모두 동일 대장에 기록.

**위치**: `.claude-work/progress/<KEY>.md` 의 `## Spawn ID 대장` 섹션 (14.3 §0 file 포맷 뒤에 append). gitignored — ephemeral cache.

### 14.12 Spawn-level token telemetry mini-table (Issue #300)

Orchestrator 는 매 spawn 결과 수령 후 **Spawn token telemetry 대장**을 `.claude-work/progress/<KEY>.md` 에 갱신한다. 목적: 레인별·에이전트별 token quota 분석 + §8.2 예산 대비 실적 추적.

**포맷**:

```markdown
## Spawn Token Telemetry

| spawn_id | agent_type | lane | spawn_at | input_tokens | output_tokens |
|---|---|---|---|---|---|
| spawn-001 | RequirementsPLAgent | 요구사항 | 2026-05-09T10:00:00Z | 12340 | 3210 |
| spawn-002 | DomainAgent | 요구사항 | 2026-05-09T10:00:05Z | 8900 | 1540 |
| spawn-003 | ArchitectPLAgent | 설계 | 2026-05-09T10:15:00Z | 21000 | 7800 |
```

**기록 규칙**:
- `input_tokens` / `output_tokens` = spawn return 시 플랫폼이 노출하는 값. 미노출 시 `?` placeholder.
- §8.3 세션 회고 보고 "토큰 사용량" 표 는 본 대장의 집계값으로 채움 (에이전트별 행 일치).
- 레인 합계 = 해당 레인 spawn row 의 `input_tokens + output_tokens` 합산 → §8.2 Total 사전 예산 비교 input.

**관계 (§15 4-channel observability)**:
- 본 대장은 Tier 1 ephemeral 채널 (`.claude-work/progress/<KEY>.md` cache 와 동일 파일). gitignored.
- stop-event-v1 (Tier 3) 과 이중 기록 금지 — quota 분석용 로컬 계산 전용.
- spawn-event-v1 (§15.2 boundary note, ADR-042 §결정 3 보류) 신설 전까지 본 대장이 spawn 단위 token 추적 유일 source.

---

### 14.11 완료 시각 + 소요 시간 reporting (normative — wrapper + all consumers)

Orchestrator 는 substantive milestone 마다 완료 시각 + 소요 시간을 final report 또는 단계 마무리 메시지에 명시한다.

**Reporting 의무 트리거**:
- Phase 1 PR open / merge
- Phase 2 PR open / merge
- Story close (Phase 2 PR merge + Issue auto-close)
- Lane gate transition (설계 리뷰 PASS / 구현 리뷰 PASS / CI PASS)
- 사용자 가시 milestone (ad-hoc 요청 완료 / FIX loop 완료)

**형식**:
```
Phase 2 PR merged (14:23, 이 단계 37분 / 세션 시작부터 1h 12m)
```
- 시각: `HH:MM`
- 소요 시간: incremental (해당 단계 시작부터) + cumulative (세션 시작부터) 모두 명시
- Trivial 작업 (1 commit, 1 file edit) = skip OK. Substantive milestone = 의무.

**TodoWrite 연동**: §14.7 render flow step 5 의 lane row content 에 완료 시각 suffix 포함 권장 (`✅ 구현 레인 PASS · 14:23`). TodoWrite update best-effort 정책(ADR-038 §결정 7) 유지 — TodoWrite 실패 시에도 메시지 내 시간 명시는 이 §14.11 normative 규칙으로 유지.

---

