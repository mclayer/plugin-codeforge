---
kind: registry
registry: fix-event
version: "1.1"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/fix-event-v1.md
date: 2026-05-11
authors:
  - Claude (CFP-32 codification — playbook §6.4 추출 + Orchestrator monopoly enforcement)
  - ArchitectAgent (CFP-391 — v1.1 MINOR bump, debate_artifact_ref optional field)
related_adrs:
  - ADR-008
  - ADR-009 (CFP-31 — §10 Orchestrator 단독 owner 결정)
  - ADR-039 (CFP-275 Amendment — Orchestrator-owned delegate subagent inclusion)
  - ADR-059 (CFP-391 — debate-protocol-v1 reasoning carryover, debate_artifact_ref 필드 도입)
related_files:
  - docs/orchestrator-playbook.md (§6.4 narrative SSOT — 본 registry와 cross-ref)
  - .github/workflows/fix-ledger-sync.yml (§10 행 commit 감지 → label/comment mirror)
  - templates/story-page-structure.md (Story §10 표 schema)
  - docs/inter-plugin-contracts/debate-protocol-v1.md (debate_artifact_ref consumer)
amendment_log:
  - date: 2026-05-11
    version: "1.1"
    cfp: CFP-391
    summary: "debate_artifact_ref optional 필드 추가 — ADR-059 reasoning carryover (Story §9 debate transcript section anchor link). 8 번째 column 으로 §10 표 확장."
    breaking: false
    backward_compat: true  # 기존 7-column row valid (debate_artifact_ref 누락 = null 처리)
---

# fix-event v1

## 1. 목적

`docs/stories/<KEY>.md` §10 "FIX Ledger" 표의 row schema machine-readable SSOT. ζ arc CFP-32부터 §10 갱신 권한이 **Orchestrator 단독**으로 이관 — lane plugin은 FIX event를 보고할 뿐 §10에 직접 append 금지. 본 registry는 row 필드 + append 규칙 + RESET 시맨틱스를 명시.

**Amendment (2026-05-08, CFP-275)** — "Orchestrator 단독" 의 **Orchestrator 정의 확장**: top-level Claude 세션 + **Orchestrator 가 §10 row append 전용으로 spawn 한 delegate subagent** 모두 포함. mechanism level subagent 경유여도 ownership identity = Orchestrator 유지. lane plugin agent 가 자체 임의 §10 직접 append 는 여전히 금지 (lane plugin spawn ≠ Orchestrator-owned delegate spawn). Cross-ref: ADR-039 §결정 3 + §결정 12.

## 2. Schema

각 §10 row entry:

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| Iter | int (1-indexed) | required | iteration 누적 카운터. 같은 Story 안에서 단조 증가 (RESET 무관) |
| 시각 | ISO8601 string | required | UTC strict — Z suffix 필수. `2026-04-29T12:34:56Z` 형식 (CFP-295 / Issue #302 — +00:00 / bare datetime 불허) |
| 레인 | enum | required | 요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 |
| 트리거 | string | required | 실패 원문 요약 (예: "DesignReviewPL P0 × 2", "성능 mean +15%", "SecurityTestPL P0 × 1 (SQL injection)") |
| 원인 판정 | enum | required | 설계 / 구현 (ArchitectPL 최종 판정. CLAUDE.md "원인 판정 decision table" SSOT) |
| 재실행 범위 | string | required | 어떤 산출물·step부터 다시 진행하는지 (예: "Change Plan §3 재작성", "DeveloperAgent 재스폰") |
| RESET? | string | required | "—" (RESET 없음) 또는 "RESET <레인>" (해당 lane 카운터 리셋) |
| debate_artifact_ref | string \| null | **optional (v1.1, CFP-391)** | debate-protocol-v1 발동된 FIX event 시 Story §9 debate transcript section anchor link (예: `#debate-transcript-DR-001`). 미발동 FIX 시 `null` 또는 column 자체 생략 (backward-compat — 기존 7-column row valid) |

§10 행 markdown 형식 예시 (v1.1 — 8 column):

```markdown
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? | debate_artifact_ref |
|------|------|------|--------|-----------|-------------|--------|---------------------|
| 1    | 2026-04-29T10:15:00Z | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — | null |
| 2    | 2026-04-29T14:22:00Z | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | RESET 구현-리뷰 | null |
| 3    | 2026-04-30T09:00:00Z | 보안-테스트 | SecurityTestPL P0 × 1 (SQL injection) | 구현 | DeveloperAgent 재스폰 | — | null |
| 4    | 2026-05-11T11:00:00Z | 설계-리뷰   | debate-protocol-v1 FIX (anchor F-001 severity divergence) | 설계 | ArchitectAgent re-run with transcript | — | #debate-transcript-F-001 |
```

§10 행 markdown 형식 — backward-compat (v1.0 7-column 유지 가능, debate 미발동 시):

```markdown
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | 2026-04-29T10:15:00Z | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
```

기존 `fix-ledger-sync.yml` Action 의 regex 는 7-column 기준 — v1.1 8 번째 column 추가는 regex non-blocking (extra trailing column 허용). v1.x 동안 두 형식 공존 가능.

## 3. 항목

```yaml
fix_event_schema:
  Iter:
    type: int
    constraints:
      - "monotonically increasing within a single Story file"
      - "1-indexed"
      - "RESET 마커는 카운터 자체에 영향 없음 — RESET 행 자체도 Iter+1"

  "시각":
    type: ISO8601
    constraints:
      - "UTC strict — Z suffix 필수 (예: 2026-04-29T12:34:56Z). +00:00 / bare datetime 불허 (CFP-295 / Issue #302)"
      - "millisecond precision optional (e.g. 2026-04-29T12:34:56.789Z 허용)"

  "레인":
    type: enum
    values:
      - 요구사항    # 발생 드묾 — clarification 재스폰은 §10 미사용 (§9.0 별도)
      - 설계
      - 설계-리뷰
      - 구현
      - 구현-리뷰
      - 구현-테스트
      - 보안-테스트

  "트리거":
    type: string
    constraints:
      - "review verdict findings 요약 또는 test failure 원문 요약"
      - "free-form, but ≤120자 권장"

  "원인 판정":
    type: enum
    values:
      - 설계      # → Change Plan 갱신, 설계 리뷰부터 재실행
      - 구현      # → Change Plan 유지, 구현 commit append
    decision_rule_ssot: CLAUDE.md "원인 판정 decision table" 섹션
    decided_by: ArchitectPLAgent (chief judge — DeveloperPL 1차 진단과 병렬)

  "재실행 범위":
    type: string
    constraints:
      - "구체 산출물·step 명시 (Change Plan §N 재작성 / agent 재스폰 / commit append 등)"

  "RESET?":
    type: string
    values:
      - "—"                        # 평소
      - "RESET 구현-리뷰"           # 구현-테스트/보안-테스트 FAIL 시 구현 복귀 → 구현-리뷰 카운터 리셋
    rule: "구현-테스트 또는 보안-테스트 FAIL → 구현 복귀 시 마지막 행에 RESET 기입. 설계-리뷰·구현-리뷰 내부 루프는 RESET 없음"

  "debate_artifact_ref":
    type: "string | null"
    required: optional        # v1.1 신규, backward-compat 보장 (CFP-391 / ADR-059)
    introduced_in: "1.1"
    values:
      - "null"                                    # debate 미발동 FIX
      - "#debate-transcript-<anchor_id>"          # debate-protocol-v1 발동 FIX — Story §9 section anchor link
    rule: |
      debate-protocol-v1 발동된 debate verdict = FIX 인 경우에만 채움. Story §9 의
      `### Debate transcript: <anchor_id>` section anchor link 형식 (`#debate-transcript-<anchor_id>`).
      미debate FIX = null 또는 column 생략 (backward-compat).
      Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32).
    cross_ref:
      - docs/adr/ADR-059-debate-protocol-v1.md (§결정 3 reasoning carryover)
      - docs/inter-plugin-contracts/debate-protocol-v1.md (Termination schema + FIX 통합)

append_rules:
  writer:
    - "Orchestrator 단독 (CFP-32 ζ arc F1부터)"
    - "DocsAgent §10 write 권한 회수 — fallback 없음"
    - "ADR-039 Amendment (CFP-275, 2026-05-08): Orchestrator 정의 = top-level Claude 세션 + Orchestrator 가 §10 row append 전용으로 spawn 한 delegate subagent. lane plugin agent 직접 append 는 여전히 금지."
  ordering:
    - "append-only — 행 삭제·수정·재정렬 금지"
    - "stale-read 체크: Edit 직전 git pull --rebase 또는 file mtime 비교"
  trigger_sources:
    - "lane plugin이 FIX event 보고 (verdict.status == FIX 또는 test FAIL)"
    - "Orchestrator가 보고 수령 → 원인 판정 (ArchitectPL 최종) → §10 행 작성"
  fix-ledger-sync.yml_action:
    - "§10 commit 감지 → Story Issue에 [FIX #N] 코멘트 mirror + fix:<레인>-retry 라벨 자동 부착"
    - "단방향 (§10 → label/comment). 라벨 변경에서 §10 자동 생성 안 함 (Codex 권고)"

counter_semantics:
  current_cycle:
    rule: "마지막 RESET <레인> 행 이후 같은 lane row count"
    pseudo_code: |
      rows = parse_section10(story_file)
      for lane in [설계-리뷰, 구현-리뷰, 구현-테스트, 보안-테스트]:
          last_reset_idx = max(i for i,r in enumerate(rows) if r.reset == lane, default=-1)
          current_count = sum(1 for r in rows[last_reset_idx+1:] if r.lane == lane)

  max_fix_per_cycle:
    설계-리뷰: 3       # 초과 시 ESCALATE
    구현-리뷰: 3       # 초과 시 ESCALATE
    구현-테스트: ∞      # 무제한 (테스트 family)
    보안-테스트: ∞      # 무제한
```

## 4. 변경 규칙

- **`시각` 필드 UTC strict (CFP-295 / Issue #302, 2026-05-09)**: `시각` 값 Z suffix 강제 (ISO8601 UTC). +00:00 표기 및 timezone 없는 bare datetime 불허. 기존 legacy entry (Z suffix 미적용) 는 표시 전용 — 신규 append 시 반드시 Z suffix. 이 정책 변경 = schema clarification (v1.0 minor commentary) — BREAKING 아님 (append-only 필드 의미 동일).
- **Append-only for v1.x**: 새 필드 추가는 minor (v1.0 → v1.1). 기존 필드 삭제 또는 enum 값 제거는 v2.0 BREAKING (ADR-008)
- **§10 마크다운 표 형식 변경 금지 (v1.x)**: `fix-ledger-sync.yml` Action regex가 현 표 형식에 의존 — 기존 7 column 순서·헤더 텍스트 변경 시 BREAKING. v1.1 의 `debate_artifact_ref` 8 번째 column 은 trailing optional column 추가 (기존 regex 비충돌). CFP-34에서 workflow yaml regex test 추가 후에야 column 순서 변경 안전
- **Writer monopoly v1**: Orchestrator 단독. lane plugin이 §10 직접 Edit 시 CI Action `story-section-write-guard.yml` (CFP-34 deliverable)이 catch. **CFP-275 Amendment**: "Orchestrator 단독" = top-level Claude 세션 + Orchestrator-owned delegate subagent (§10 row append 전용 spawn) 동등 — ADR-039 §결정 12 normative 정합 anchor.
- **RESET 시맨틱스 변경**: lane scope 또는 시점 변경은 minor (v1.1) — `current_cycle` 알고리즘 영향. ESCALATE 임계값 변경은 minor (v1.1)
- **§10 schema 검증**: CFP-33 contract harness가 본 registry → Story file §10 매칭 lint 추가
- **v1.0 → v1.1 (CFP-391 / ADR-059)**: `debate_artifact_ref` optional 필드 추가. SemVer MINOR — backward-compat 보장 (기존 7-column row valid, column 자체 생략 가능). `fix-ledger-sync.yml` regex 호환성 검증 필요 — Phase 2 PR scope (`scripts/check-doc-section-schema.sh` 보강).
