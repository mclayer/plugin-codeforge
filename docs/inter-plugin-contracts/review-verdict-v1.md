---
kind: contract
contract_version: "1.0"
status: Deprecated
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-review (lane plugin, producer)
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker)
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
authors:
  - CFP-29 동결 (2026-04-28)
  - CFP-33 frontmatter backfill (2026-04-29)
  - CFP-35 status Active → Deprecated (v2 신설, 2026-04-29)
---

# review_verdict v1 — Inter-plugin Contract (DEPRECATED)

> **CFP-35 (2026-04-29) 이후 Deprecated**: codeforge-review plugin v1.0.0+ 부터 [`review-verdict-v2.md`](review-verdict-v2.md) self-write contract 사용. v1 contract surface (DocsAgent 경유 write 위임)는 codeforge v0.22.0 + codeforge-review v1.0.0 짝 부터 더 이상 호환 처리 안 함. 본 file은 audit·archive 목적으로 유지 (6 CFP 무사고 후 별도 cleanup CFP에서 file 삭제 예정).

`codeforge` core ↔ `codeforge-review` plugin 사이의 양방향 schema. CFP-29 Phase 1에서 동결.

**상위 SSOT 위치**:
- 본 file: 상세 schema + example + ESCALATE 처리
- [`CLAUDE.md`](../../CLAUDE.md) "## Inter-plugin Contract" 섹션: 요약 + cross-ref to 본 file
- [`docs/adr/ADR-008-inter-plugin-contract-versioning.md`](../adr/ADR-008-inter-plugin-contract-versioning.md): versioning 룰

## 1. 흐름 개요

```
codeforge core (Orchestrator)
        │
        │ ① review_packet 작성 (lane-specific)
        ▼
codeforge-review plugin
  └─ <Lane>ReviewPLAgent (Design / Code / Security)
        │
        │ ② Orchestrator가 한 메시지에 두 워커 dispatch
        ▼
  ├─ ClaudeReviewAgent (worker, lane-agnostic)
  └─ CodexReviewAgent  (worker, lane-agnostic)
        │
        │ ③ 워커 결과 PL에 return
        ▼
  └─ <Lane>ReviewPLAgent dedup + severity 종합
        │
        │ ④ review_verdict v1 typed output
        ▼
codeforge core (Orchestrator)
        │
        │ ⑤ verdict 처리:
        │    - status=PASS → DocsAgent에 gate 라벨 부착 의뢰
        │    - findings → DocsAgent에 Story §9 append 의뢰
        │    - summary_for_pr_comment → DocsAgent에 PR comment 의뢰 (phase prefix 적용)
        │    - status=FIX → FIX 루프 진입 (Story §10 FIX Ledger sync)
        ▼
codeforge core (DocsAgent)
        write Story §9 + GitHub PR comment + gate label
```

## 2. review_packet (codeforge core → codeforge-review)

PL spawn 시 Orchestrator가 packet을 PL 프롬프트에 주입.

```yaml
review_packet:
  contract_version: "1.0"           # required
  lane: design | code | security    # required
  checklist_path: <relative path within codeforge-review repo>  # required
  scope_globs:                       # required
    - <file glob list>               # 예: ["docs/change-plans/**", "docs/stories/<KEY>.md"]
  category_enum:                     # required — lane-specific category 목록
    - <category list>                # 예: ["adr-mismatch", "design-quality", ...]
  severity_overrides:                # optional — lane별 자동 P0 룰
    - rule: "ADR violation"          # → P0
    - rule: "credential hardcode"    # → P0
  story_key: <STORY_KEY>             # required — Story file 참조
  related_adrs:                      # optional — 정합성 교차 입력
    - docs/adr/ADR-NNN-<slug>.md

  # security lane only
  first_layer_findings:
    dependabot:    [<Dependabot alerts>]
    codeql:        [<CodeQL findings>]
    secret_scan:   [<Secret Scanning alerts>]
    push_protection: [<Push Protection bypassed events>]
```

**필수 필드 누락 시**: 워커가 `ESCALATE_PACKET_INCOMPLETE` 신호 반환 (generic fallback 금지). PL은 정정 후 재 dispatch.

상세 lane별 packet schema는 codeforge-review repo의 `templates/review-pl-base.md` §2 SSOT 참조.

## 3. review_verdict (codeforge-review → codeforge core)

PL이 워커 결과 종합 후 Orchestrator return.

```yaml
review_verdict:
  contract_version: "1.0"           # required — version mismatch 시 core가 ESCALATE
  lane: design | code | security    # required (packet과 일치)
  story_key: <STORY_KEY>            # required (packet과 일치)
  iteration: <int>                  # required — FIX 카운터, core가 §10 FIX Ledger sync에 사용

  status: PASS | FIX | FIX_DISCRETIONARY  # required — review-pl-base.md §3 SSOT 룰 적용
                                          # PASS: 모든 P0/P1 finding 0건 (또는 P0 0 + P1 1 + 재량)
                                          # FIX: P0 ≥ 1 또는 P0 0 + P1 ≥ 2
                                          # FIX_DISCRETIONARY: P0 0 + P1 = 1, PL 재량

  findings:                          # array — 모든 발견 (severity 무관)
    - severity: P0 | P1 | P2          # required
      category: <enum from packet.category_enum>  # required
      file: <path>                    # required
      line: <int>                     # optional (비-file finding 시 0)
      evidence: <markdown>            # required — 해당 위치 인용 + 위반 근거
      suggestion: <markdown>          # required — 수정 방향 (코드 patch 아님, 가이드)

  summary_for_story_section_9: <markdown>
                                     # required — core(DocsAgent)가 Story §9 append
                                     # 포맷: PL 종합 보고 + finding count + 결정 근거

  summary_for_pr_comment: <markdown>
                                     # required — core(DocsAgent)가 phase prefix 적용해 PR comment 게시
                                     # 짧은 형태 (≤30 줄). 상세는 §9 참조 링크

  next_gate_label: gate:design-review-pass | gate:security-test-pass | null
                                     # required — PASS 시 core가 부착할 라벨
                                     # status=FIX/FIX_DISCRETIONARY 시 null
                                     # status=PASS + lane=code 시 null (구현 리뷰 PASS 라벨 부재 — 다음 lane 트리거만)
```

## 4. ESCALATE 처리

### 4.1 contract_version mismatch

core가 verdict.contract_version을 모르는 값으로 받으면:

```
[Orchestrator → user]
✗ Inter-plugin contract version mismatch:
  codeforge core 가 인식하는 review_verdict version: v1.0 (...)
  codeforge-review 가 반환한 version: <unknown>
  
호환성 매트릭스 부재 — fallback 시도하지 않음.
조치: codeforge core 또는 codeforge-review 중 한쪽 update 후 재시도.
```

### 4.2 status 룰 위반

PL이 P0 ≥ 1인데 status=PASS 반환 시 → core가 verdict 거부 + ESCALATE. PL의 dedup·severity 종합 로직 검증 필요.

### 4.3 next_gate_label 부재 (PASS인데)

status=PASS인데 next_gate_label이 null 또는 unknown enum → core ESCALATE. lane별 gate label은 codeforge core가 owner.

## 5. v1 → v2 변경 시 (예측 가능한 향후)

ADR-008 룰 적용:
- v1.x backward-compat (선택 필드 추가만): 양쪽 plugin 무관, contract version `"1.X"`
- v2.0 BREAKING: 양쪽 plugin 동시 bump, 새 ADR 필수

예시 — 향후 v1.1 후보:
- `findings[].suggested_fix_diff: <patch>` (선택, ClaudeReview가 채우면 좋음)
- `cost_token_estimate: <int>` (선택, 보고용)

## 6. 본 contract 시점 동결 ATTRIBUTION

- 본 v1 동결 시점: 2026-04-28 CFP-29 머지 시점
- codeforge core SHA: feat/cfp-29-phase-1 브랜치 머지 commit (PR #XX)
- codeforge-review SHA: initial commit on main (mclayer/plugin-codeforge-review)
- 이전 review packet schema source: codeforge core (pre-CFP-29) `templates/review-pl-base.md` §2 — 본 file로 이전 + version 부여
