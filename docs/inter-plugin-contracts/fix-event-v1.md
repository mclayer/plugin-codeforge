---
kind: registry
registry: fix-event
version: "1.4"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/fix-event-v1.md
date: 2026-05-17
authors:
  - Claude (CFP-32 codification — playbook §6.4 추출 + Orchestrator monopoly enforcement)
  - ArchitectAgent (CFP-391 — v1.1 MINOR bump, debate_artifact_ref optional field)
  - ArchitectAgent (CFP-526 — v1.2 MINOR bump, reasoning_carryover optional field)
  - ArchitectAgent (CFP-842 — v1.3 MINOR bump, depth-aware scope optional fields)
  - ArchitectAgent (CFP-2480 — v1.4 MINOR bump, FIX ground-truth replay optional fields: reproducer_command + replay_verdict)
related_adrs:
  - ADR-008
  - ADR-009 (CFP-31 — §10 Orchestrator 단독 owner 결정)
  - ADR-039 (CFP-275 Amendment — Orchestrator-owned delegate subagent inclusion)
  - ADR-059 (CFP-391 — debate-protocol-v1 reasoning carryover, debate_artifact_ref 필드 도입)
  - ADR-067 (CFP-526 — fix-ledger implementability escalation, reasoning_carryover 필드 도입; CFP-842 Amendment 1 — depth-aware scope cross-ref, RESET mechanical 정확도; CFP-2480 Amendment 3 — FIX replay ↔ max-FIX disjoint, reproducer_command/replay_verdict carrier)
  - ADR-070 (CFP-2480 — verify-before-trust FIX-close 시점 적용, replay_verdict = §결정 D9 3-상태 disposition 정합 매핑, reproducer = [hypothesis] → PL falsify → [verified] close)
  - ADR-119 (CFP-2480 — §결정 10② close-time wire 실현, "수정됨=반증 후 단언" mechanical carrier)
related_files:
  - docs/orchestrator-playbook.md (§6.4 / §6.7 narrative SSOT — 본 registry와 cross-ref)
  - .github/workflows/fix-ledger-sync.yml (§10 행 commit 감지 → label/comment mirror)
  - templates/story-page-structure.md (Story §10 표 schema)
  - docs/inter-plugin-contracts/debate-protocol-v1.md (debate_artifact_ref consumer)
  - docs/evidence-checks-registry.yaml (CFP-842 — fix-event-depth-scope-presence warning-tier entry)
amendment_log:
  - date: 2026-05-11
    version: "1.1"
    cfp: CFP-391
    summary: "debate_artifact_ref optional 필드 추가 — ADR-059 reasoning carryover (Story §9 debate transcript section anchor link). 8 번째 column 으로 §10 표 확장."
    breaking: false
    backward_compat: true  # 기존 7-column row valid (debate_artifact_ref 누락 = null 처리)
  - date: 2026-05-13
    version: "1.2"
    cfp: CFP-526
    summary: "reasoning_carryover optional 필드 추가 — ADR-067 §결정 5 architectural amnesia 차단 (3-part structured YAML: invariant_summary + disputed_claims + transcript_ref). 9 번째 column 으로 §10 표 확장."
    breaking: false
    backward_compat: true  # 기존 8-column row valid (reasoning_carryover 누락 = null 처리)
  - date: 2026-05-17
    version: "1.3"
    cfp: CFP-842
    summary: "depth-aware scope 2 optional 필드 추가 — affected_scope (enum: single-file / cross-module / cross-repo / cross-plugin) + affected_paths_with_depth (array of {path, depth}). RESET 범위·재스폰 lane 결정 mechanical 정확도 확보 + broken-link/path 정정 FIX 시 over-correction regression chain 직접 차단 (CFP-770 §8 CR-005→CR-006→CR-007 carry-over). 10/11 번째 column 으로 §10 표 확장. broken-link/path 정정 FIX 영역 한정 affected_paths_with_depth 의무 (그 외 optional)."
    breaking: false
    backward_compat: true  # 기존 9-column row valid (affected_scope / affected_paths_with_depth 누락 = null 처리)
  - date: 2026-06-30
    version: "1.4"
    cfp: CFP-2480
    summary: "FIX ground-truth replay 2 optional 필드 추가 — reproducer_command (finding 정당화한 실패 명령 verbatim + base SHA 동반, 생성 시점 저장; schema 제약 = repo-relative 게이트/테스트 호출 형태만, raw shell free-string 금지 = stored-command injection vector 차단; INV-SEC-1 PII/secret/credential/private-path 금지) + replay_verdict (닫기 시점 enum: PASS / falsified / replay-impossible / undetermined; ADR-070 §결정 D9 3-상태 disposition 정합 매핑; INV-SEC-2 stdout 최소 발췌). FIX '수정됨' close = 원 reproducer 재실행 GREEN(외부 Retest) 반증 후에만 성립 (ADR-119 §결정 10② close-time wire 실현). 12/13 번째 column 으로 §10 표 확장. replay FAIL = 닫기 게이트(close 거부)지 max-FIX 카운터 소비 아님 (ADR-067 Amendment 3 disjoint). replay-impossible = 실행 가능 명령 환원 불가 finding 의 사유 동반 disposition (silent 면제 금지)."
    breaking: false
    backward_compat: true  # 기존 11-column row valid (reproducer_command / replay_verdict 누락 = null 처리)
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
| reasoning_carryover | object \| null | **optional (v1.2, CFP-526)** | ArchitectPL re-spawn 시 architectural amnesia 차단 — 직전 finding + reasoning 전달 (ADR-067 §결정 5). 3-part structured YAML: `invariant_summary` (50자 이내, immutable boundary 요약) / `disputed_claims` (100자 이내, unresolved 영역) / `transcript_ref` (Story §9 anchor link). 미사용 시 `null` 또는 column 생략 (backward-compat — 기존 8-column row valid) |
| affected_scope | enum \| null | **optional (v1.3, CFP-842)** | 결함의 affected layer depth — enum `single-file` (1 file 안 isolated) / `cross-module` (동일 repo 안 2+ top-level dir) / `cross-repo` (2+ repo, 단일 plugin family) / `cross-plugin` (2+ plugin family 또는 marketplace mirror 영역). RESET 범위·재스폰 lane 결정 mechanical 정확도 확보 (ADR-067 §결정 4 cross-lane RESET 정합). 미사용 시 `null` 또는 column 생략 (backward-compat — 기존 9-column row valid) |
| affected_paths_with_depth | array of object \| null | **optional (v1.3, CFP-842)** | broken-link / path 정정 FIX 시 의무 — 영향 file 별 `{path: string, depth: integer}` array. `depth` = file 의 root 로부터 dir depth (e.g. `docs/adr/ADR-067.md` = 2, `templates/github-workflows/fix-ledger-sync.yml` = 2, `CLAUDE.md` = 0). 정정 규칙 적용 범위 (예: `depth >= 2 then path adjust = '../../'`) 의 mechanical reasoning trace 보존 + over-correction regression chain (CFP-770 §8 CR-005→CR-006→CR-007 lesson) 직접 차단. broken-link / path 정정 외 FIX = `null` 또는 column 생략 (backward-compat 9-column row valid). broken-link/path FIX 인데 본 필드 누락 = `fix-event-depth-scope-presence` warning-tier lint 적발 |
| reproducer_command | object \| null | **optional (v1.4, CFP-2480)** | FIX ground-truth replay 의 원 reproducer — finding 을 정당화한 실패 명령 verbatim + base SHA. 2-part: `command` (string, **schema 제약 = repo-relative 게이트/테스트 호출 형태만** — 예: `bash scripts/check-plugin-version-bump-self.sh --self-test` 또는 `pytest tests/foo::test_bar`; raw shell free-string 금지 = stored-command injection vector 차단, SecurityArch THR-E3-2) + `base_sha` (string, finding 정당화 시점 base SHA — reproduce-before-fix 결정론 기준, InfraOp SHA-pin). finding 생성 시점 저장 (닫기 시점 재실행 가능하도록). **INV-SEC-1 (의무)**: PII / secret / credential / API key / private absolute-path 금지 (public PR mirror surface — ADR-067 §결정 7 동형). FIX replay 대상 finding 한정 의무 (환원불가 finding = `null`). 누락 = backward-compat (기존 11-column row valid, null 처리) |
| replay_verdict | enum \| null | **optional (v1.4, CFP-2480)** | FIX "수정됨" 닫기 시점 replay disposition. enum = `PASS` (원 reproducer 결정론적 GREEN 재현 + PL falsify 통과 → close 허용, 외부 Retest) / `falsified` (여전히 RED → close 거부, (A)축 fail-closed) / `replay-impossible` (실행 가능 명령 환원 불가 finding — 사유 동반 의무, silent 면제 금지) / `undetermined` (flaky 다회 미충족 또는 mixed → 보류 quarantine, false-GREEN+false-RED 양방향 차단). ADR-070 §결정 D9 3-상태 disposition 정합 매핑. 결정 SSOT = `scripts/lib/fix_replay_disposition.py` (pure function + provenance 동반, artifact 없이 close 경로 0 — Story A INV-G4 동형). **INV-SEC-2 (의무)**: verdict 동반 stdout 발췌는 exit + 모순 라인만 최소 (전체 dump 금지). replay FAIL(`falsified`) = 닫기 게이트지 max-FIX 카운터 소비 아님 (ADR-067 Amendment 3 disjoint). 누락 = backward-compat (기존 12-column row valid, null 처리) |

§10 행 markdown 형식 예시 (v1.4 — 13 column):

```markdown
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? | debate_artifact_ref | reasoning_carryover | affected_scope | affected_paths_with_depth | reproducer_command | replay_verdict |
|------|------|------|--------|-----------|-------------|--------|---------------------|---------------------|----------------|---------------------------|--------------------|----------------|
| 1    | 2026-04-29T10:15:00Z | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — | null | null | single-file | null | null | null |
| 2    | 2026-04-29T14:22:00Z | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | RESET 구현-리뷰 | null | null | cross-module | null | null | null |
| 3    | 2026-04-30T09:00:00Z | 보안-테스트 | SecurityTestPL P0 × 1 (SQL injection) | 구현 | DeveloperAgent 재스폰 | — | null | null | single-file | null | null | null |
| 4    | 2026-05-11T11:00:00Z | 설계-리뷰   | debate-protocol-v1 FIX (anchor F-001 severity divergence) | 설계 | ArchitectAgent re-run with transcript | — | #debate-transcript-F-001 | {invariant_summary: "API contract immutable", disputed_claims: "rate-limit scope", transcript_ref: "#debate-transcript-F-001"} | cross-plugin | null | null | null |
| 5    | 2026-05-17T11:00:00Z | 구현-리뷰   | CodeReviewPL P1 broken-link x 3 (CR-005 over-correction) | 구현 | DeveloperAgent 재스폰 (path adjust) | — | null | null | cross-module | [{path: "docs/adr/ADR-067.md", depth: 2}, {path: "templates/github-workflows/fix-ledger-sync.yml", depth: 2}, {path: "CLAUDE.md", depth: 0}] | null | null |
| 6    | 2026-06-30T11:00:00Z | 구현-리뷰   | CodeReviewPL P0 × 1 (version-bump under-bump, 정책팩 실행 포착) | 구현 | DeveloperAgent 재스폰 (MINOR→bump) — close 시 replay | — | null | null | single-file | null | {command: "bash scripts/check-plugin-version-bump-self.sh --self-test", base_sha: "50b333b5"} | PASS |
| 7    | 2026-06-30T12:30:00Z | 구현-리뷰   | CodeReviewPL P1 naming 가독성 (환원불가) | 구현 | DeveloperAgent 재스폰 | — | null | null | single-file | null | null | replay-impossible |
```

> v1.4 row 6 = 게이트 출처 finding → reproducer 환원 가능 → close 시 원 reproducer 재실행 GREEN(`replay_verdict: PASS`, 외부 Retest) 후 close. row 7 = 코드 P1 의미 판정 finding → 실행 가능 명령 환원 불가 → `replay_verdict: replay-impossible` + reproducer_command=null (사유는 §10 row 트리거 또는 별도 disposition 기록 — silent 면제 금지).

§10 행 markdown 형식 — backward-compat (v1.0 7-column 유지 가능, debate / carryover / scope 미사용 시):

```markdown
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | 2026-04-29T10:15:00Z | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
```

기존 `fix-ledger-sync.yml` Action 의 regex 는 7-column 기준 — v1.1 8 번째 column 추가는 regex non-blocking (extra trailing column 허용). v1.2 9 번째 column / v1.3 10·11 번째 column / v1.4 12·13 번째 column (reproducer_command / replay_verdict) 도 동일하게 trailing optional column 추가로 regex 비충돌 (v1.1~v1.3 선례 4회 정합). v1.x 동안 모든 형식 공존 가능.

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

  "reasoning_carryover":
    type: object
    optional: true            # v1.2 신규, backward-compat 보장 (CFP-526 / ADR-067)
    introduced_in: "1.2"
    description: §10 row 의 architectural amnesia 차단 — ArchitectPL re-spawn 시 직전 finding + reasoning 전달
    properties:
      invariant_summary:
        type: string
        max_length: 50
        description: immutable boundary 요약 (변경 차단 영역)
      disputed_claims:
        type: string
        max_length: 100
        description: FIX iter 내 unresolved 영역 (다음 cycle input)
      transcript_ref:
        type: string
        description: Story §9 anchor link (예 "#debate-transcript-F-001")
    rule: |
      ArchitectPL re-spawn 시 직전 §10 row 의 reasoning_carryover full-text를 입력으로 전달 의무.
      debate_artifact_ref 와 직교 — debate 발동 여부와 무관하게 reasoning 보존 가능.
      미사용 FIX = null 또는 column 생략 (backward-compat — 기존 8-column row valid).
      Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32).
    cross_ref:
      - docs/adr/ADR-067-fix-ledger-implementability-escalation.md (§결정 5 reasoning carryover)
      - docs/orchestrator-playbook.md (§6.6 — re-spawn 시 carryover 전달 절차)

  "affected_scope":
    type: enum
    optional: true            # v1.3 신규, backward-compat 보장 (CFP-842 / ADR-067 Amendment 1)
    introduced_in: "1.3"
    description: "결함의 affected layer depth — RESET 범위·재스폰 lane 결정 mechanical 정확도 input"
    values:
      - single-file       # 1 file 안 isolated (typo, comment-only, 단일 함수 logic)
      - cross-module      # 동일 repo 안 2+ top-level dir (예: docs/ + templates/ + scripts/)
      - cross-repo        # 2+ repo, 단일 plugin family (예: wrapper + internal-docs sibling sync)
      - cross-plugin      # 2+ plugin family 또는 marketplace mirror 영역 (ADR-063 atomic invariant scope)
    rule: |
      Orchestrator 가 FIX root cause 판정 직후 affected_scope 결정. ArchitectPL chief judge 의 evidence pack 참조.
      RESET 결정 영향: cross-module / cross-repo / cross-plugin scope = ArchitectPL 가 cross-lane RESET 적극 검토
      (ADR-067 §결정 4 Pause-and-resume 패턴). single-file scope = 동일 lane FIX iter 유지 (RESET 회피).
      미사용 시 null 또는 column 생략 (backward-compat — 기존 9-column row valid).
      Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32).
    cross_ref:
      - docs/adr/ADR-067-fix-ledger-implementability-escalation.md (Amendment 1 §결정 4 cross-lane RESET scope 정합)
      - docs/orchestrator-playbook.md (§6.5 cross-lane RESET 정책 — scope-aware 결정)

  "affected_paths_with_depth":
    type: array
    optional: true            # v1.3 신규, broken-link/path 정정 FIX 영역 한정 의무
    introduced_in: "1.3"
    description: "broken-link / path 정정 FIX 영역 한정 — 영향 file 별 path + dir depth tuple"
    items:
      type: object
      properties:
        path:
          type: string
          description: "repo root 기준 relative path (예: docs/adr/ADR-067.md, CLAUDE.md, templates/github-workflows/fix-ledger-sync.yml)"
        depth:
          type: integer
          minimum: 0
          description: "path 의 dir depth (root level file = 0, depth 1 dir 안 file = 1, ...)"
    rule: |
      broken-link / path 정정 FIX (예: cross-module relative path adjust, doc-location-registry move) 시 의무.
      그 외 FIX (logic bug, API change, perf regression 등) = null 또는 column 생략 허용.
      각 row 의 path 가 depth 별로 정정 규칙이 달라지는 영역 (예: depth >= 2 인 file 은 `../../` 추가 의무) 의 mechanical reasoning trace 보존.
      CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson — depth 정보 부재가 directly carrier.
      broken-link/path FIX 인데 본 필드 누락 = `fix-event-depth-scope-presence` warning-tier lint 적발 (advisory only, blocking-on-pr 미승격).
      Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32).
    cross_ref:
      - docs/adr/ADR-067-fix-ledger-implementability-escalation.md (Amendment 1 §결정 4 cross-lane RESET scope 정합)
      - docs/evidence-checks-registry.yaml (fix-event-depth-scope-presence — warning-tier broken-link/path FIX lint)
      - docs/orchestrator-playbook.md (§6.7 §10 관리 세부 — broken-link/path FIX 시 depth annotation 의무)

  "reproducer_command":
    type: object
    optional: true            # v1.4 신규, FIX ground-truth replay 영역 한정 의무 (CFP-2480 / ADR-067 Amendment 3)
    introduced_in: "1.4"
    description: "FIX finding 을 정당화한 원 reproducer (실패 명령 verbatim + base SHA) — reproduce-before-fix 기록"
    properties:
      command:
        type: string
        description: |
          repo-relative 게이트/테스트 호출 형태만 (schema 제약 — raw shell free-string 금지).
          예: "bash scripts/check-plugin-version-bump-self.sh --self-test" / "pytest tests/foo.py::test_bar".
          SecurityArch THR-E3-2 — stored-command injection vector 차단 (Codex worker 발화 reproducer 더 위험,
          Evgrafov inter-agent 82.4% > direct 41.2%). 발화자(Codex) ≠ 기록자(Orchestrator).
      base_sha:
        type: string
        description: "finding 정당화 시점 base SHA (reproduce-before-fix 결정론 기준, InfraOp SHA-pin). 명령·입력 결정론 고정 (과거 시간여행 아님)"
    rule: |
      FIX replay 대상 finding (게이트/테스트 출처 = 환원 가능) 한정 의무. 환원불가 finding (코드 P1 가독성 등) = null.
      finding 생성 시점 저장 (닫기 시점 재실행 가능하도록 — F-2 reproduce-before-fix).
      INV-SEC-1 (의무): PII / secret / credential / API key / private absolute-path 금지 (public PR mirror surface,
        ADR-067 §결정 7 동형). repo-relative·환경독립 명령만. Orchestrator append 전 SCAN-A + 위반 시 fail-fast (자동 redact 금지, audit 가능성).
      미사용 FIX = null 또는 column 생략 (backward-compat — 기존 11-column row valid).
      Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32). replay 실행 = Codex worker / replay verdict 기록·close = Orchestrator (실행자≠판정자).
    cross_ref:
      - docs/adr/ADR-067-fix-ledger-implementability-escalation.md (Amendment 3 — FIX replay ↔ max-FIX disjoint + reproducer schema 제약 carrier)
      - docs/adr/ADR-070-codex-verify-before-trust.md (Amendment 12 — reproducer = [hypothesis] → PL falsify → [verified] close)
      - docs/domain-knowledge/concept/fix-ground-truth-replay.md (F-2 reproduce-before-fix / F-4 신호원 분리)

  "replay_verdict":
    type: enum
    optional: true            # v1.4 신규, FIX "수정됨" close 시점 disposition (CFP-2480 / ADR-070 Amendment 12)
    introduced_in: "1.4"
    description: "FIX '수정됨' 닫기 시점 replay disposition — 원 reproducer 재실행 결과 (ADR-070 §결정 D9 3-상태 정합)"
    values:
      - PASS                # 원 reproducer 결정론적 GREEN 재현 + PL falsify 통과 → close 허용 (외부 Retest, F-1)
      - falsified           # 여전히 RED → close 거부 ((A)축 fail-closed, degrade 없음 — 수정이 실제로 안 됨)
      - replay-impossible   # 실행 가능 명령 환원 불가 finding → 사유 동반 의무 (silent 면제 금지, INV-FR2)
      - undetermined        # flaky 다회 미충족 또는 mixed → 보류 quarantine (false-GREEN+false-RED 양방향 차단, FLAKY)
    rule: |
      FIX "수정됨" close = replay_verdict == PASS 시만 성립 (F-1 — 원 reproducer 재실행 GREEN = 외부 Retest).
      falsified = close 거부 ((A)축 replay-verdict fail-closed — degrade 없음, fail-open reject).
      replay-impossible = 환원불가 finding 의 disposition + 사유 명시 의무 (INV-FR2 silent 면제 차단).
      undetermined = flaky (다회 결정론 미충족 또는 mixed) → quarantine 보류 (1회 GREEN close 금지 = false-GREEN 차단,
        §1 목적 정면 훼손 방지; mixed quarantine = false-RED max-FIX 부당소진 차단).
      결정 SSOT = scripts/lib/fix_replay_disposition.py (pure function decide_replay_disposition + provenance 동반,
        artifact 없이 close 경로 0 — Story A INV-G4 동형 / discriminating test tests/scripts/test-check-fix-replay-disposition.sh).
      INV-SEC-2 (의무): verdict 동반 stdout 발췌는 exit + 모순 라인만 최소 (전체 dump 금지).
      replay FAIL(falsified) = 닫기 게이트지 max-FIX 카운터 소비 아님 (ADR-067 Amendment 3 disjoint — 무한거부 backstop = fix-attempt 카운터).
      Codex 미가용 (replay 실행 자체 불가, fail-mode (B)축) = lane-time fail-open + marker [fix-replay-fallback: fail-mode=codex_unavailable, disposition=open] ((A)축 falsified 와 disjoint).
      미사용 FIX = null 또는 column 생략 (backward-compat — 기존 12-column row valid).
      Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32).
    cross_ref:
      - docs/adr/ADR-070-codex-verify-before-trust.md (Amendment 12 §결정 D9 3-상태 disposition 정합 매핑)
      - docs/adr/ADR-119-research-before-claims.md (§결정 10② close-time wire 실현 — "수정됨=반증 후 단언")
      - scripts/lib/fix_replay_disposition.py (decide_replay_disposition SSOT)
      - docs/domain-knowledge/concept/fix-ground-truth-replay.md (F-1 close=Retest / F-3 false-close 양방향 차단)

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
- **v1.1 → v1.2 (CFP-526 / ADR-067)**: `reasoning_carryover` optional 필드 추가 (3-part structured YAML: invariant_summary + disputed_claims + transcript_ref). SemVer MINOR — backward-compat 100% 보장 (기존 8-column row valid, column 자체 생략 = null 처리). `debate_artifact_ref` (v1.1) 와 직교하는 독립 필드. ESCALATE root cause = "design granularity inadequate" 또는 N+1 round divergence 유지 케이스에서 ArchitectPL re-spawn 시 reasoning continuity 확보.
- **v1.2 → v1.3 (CFP-842 / ADR-067 Amendment 1)**: `affected_scope` + `affected_paths_with_depth` 2 optional 필드 추가. SemVer MINOR — backward-compat 100% 보장 (기존 9-column row valid, column 자체 생략 = null 처리). RESET 범위·재스폰 lane 결정 mechanical 정확도 input + broken-link/path 정정 FIX 시 over-correction regression chain (CFP-770 §8 lesson) 직접 차단. `affected_paths_with_depth` 는 broken-link / path 정정 FIX 영역 한정 의무 (그 외 optional). `fix-event-depth-scope-presence` warning-tier lint (advisory only, blocking-on-pr 미승격) 가 Phase 2 carrier — broken-link/path FIX 인데 depth 누락 시 적발.
- **v1.3 → v1.4 (CFP-2480 / ADR-067 Amendment 3 + ADR-070 Amendment 12 + ADR-119 §결정 10②)**: `reproducer_command` (object: command + base_sha) + `replay_verdict` (enum) 2 optional 필드 추가. SemVer MINOR — backward-compat 100% 보장 (기존 11-column row valid, column 자체 생략 = null 처리). FIX ground-truth replay close-gate carrier — "수정됨" close = 원 reproducer 재실행 GREEN(외부 Retest, ADR-119 §결정 10② close-time wire) 반증 후에만 성립. `reproducer_command.command` schema 제약 = repo-relative 게이트/테스트 호출 형태만 (raw shell free-string 금지 = stored-command injection vector 차단, SecurityArch THR-E3-2) + INV-SEC-1 (PII/secret/credential/private-path 금지, ADR-067 §결정 7 동형). `replay_verdict` = ADR-070 §결정 D9 3-상태 disposition 정합 매핑 + INV-SEC-2 (stdout 최소 발췌). replay FAIL(falsified) = max-FIX 카운터 disjoint (닫기 게이트, ADR-067 Amendment 3). 결정 SSOT = `scripts/lib/fix_replay_disposition.py` (pure function + provenance + discriminating test). `fix-ledger-sync.yml` regex = trailing optional column 비충돌 (v1.1~v1.3 선례 4회 정합). FIX replay mechanical wire (close-time replay 자동화) = Phase 2 / 후속 carrier.

## v1.4 (2026-06-30, CFP-2480)

- reproducer_command optional object 신설 (command: repo-relative 게이트/테스트 호출만 + base_sha: reproduce-before-fix 결정론 기준)
- replay_verdict optional enum 신설 (PASS / falsified / replay-impossible / undetermined — ADR-070 §결정 D9 3-상태 정합)
- ADR-067 Amendment 3 (replay ↔ max-FIX disjoint) + ADR-070 Amendment 12 (verify-before-trust FIX-close 적용) + ADR-119 §결정 10② (close-time wire 실현) binding
- INV-SEC-1 (reproducer PII/secret/credential/private-path 금지) + INV-SEC-2 (verdict stdout 최소 발췌) — public PR mirror surface (ADR-067 §결정 7 동형)
- 결정 SSOT = scripts/lib/fix_replay_disposition.py (decide_replay_disposition pure function + INV-FR1~5/FLAKY-1~3 + provenance 동반 + 3-tier exit + discriminating test)
- Backward compat: 100% (2 optional field, 기존 row null 또는 column 생략 모두 valid — 12·13번째 trailing column, regex 비충돌)

## v1.3 (2026-05-17, CFP-842)

- affected_scope optional enum 신설 (single-file / cross-module / cross-repo / cross-plugin)
- affected_paths_with_depth optional array 신설 ({path, depth} per file)
- ADR-067 Amendment 1 §결정 4 binding — cross-lane RESET scope-aware mechanical 정확도 확보
- broken-link/path 정정 FIX 영역 한정 affected_paths_with_depth 의무 (lint warning-tier `fix-event-depth-scope-presence`)
- CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson directly 차단
- Backward compat: 100% (2 optional field, 기존 row null 또는 column 생략 모두 valid)

## v1.2 (2026-05-13, CFP-526)

- reasoning_carryover optional field 신설 (3-part structured: invariant_summary + disputed_claims + transcript_ref)
- ADR-067 §결정 5 binding — architectural amnesia 차단
- debate-protocol-v1 v1.1 patterns (debate_artifact_ref) 정합
- Backward compat: 100% (optional field, 기존 row null 또는 column 생략 모두 valid)
