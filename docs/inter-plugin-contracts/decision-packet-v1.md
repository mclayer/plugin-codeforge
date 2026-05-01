---
kind: registry
registry: decision-packet
version: "1.0"
status: Active
authors:
  - Claude (CFP-57 author — spec § 2.6 codification)
  - Codex (gpt-5.5 high) — Round 1+2 brainstorming + spec audit Round 1+2
related_adrs:
  - ADR-018 (carrier)
  - ADR-008 (parent — versioning rule)
  - ADR-001 (sibling — review verdict 는 본 registry 적용 대상 아님)
related_files:
  - CLAUDE.md (오케스트레이션 규칙 — Gemini Decider subsection)
  - templates/story-page-structure.md (§12 Gemini Decision Log)
---

# decision-packet v1

## 1. 목적

CFP-57 (ADR-018) Gemini decider auto-proceed system 의 decision packet schema. Claude+Codex 가 생성한 옵션 set + cross-review + 사용자 context 를 Gemini 에 전달할 때의 정형 format. Gemini 응답·sanity audit·retry/fallback 결과 까지 누적 기록.

본 registry 는 wrapper-owned (registry kind, lint scope 밖). MANIFEST.yaml 의 contracts list 에 등록하지 않음.

## 2. Schema

```yaml
packet_id: <KEY>-<seq>           # globally unique, format: CFP-NN-NNN
content_hash: <sha256>           # normalized options + context hash
trigger: option-formulation | fix-root-cause | codex-ambiguity | brainstorming-constraint
story_key: CFP-NN
seq: 1                            # Story 내 순번
context:
  background: <verbatim user request + 직전 분기 history>
  constraints: <repo SSOT / ADR refs / domain context>
options:                          # 3+ 옵션 가능
  - id: <option id e.g. A, B, ..., Y_prime>
    source: claude | codex | both
    rationale: <generator analysis, multi-paragraph>
    cross_review: <other LLM view, agree/disagree + reasoning>
recommendations:
  claude: <option id>
  codex: <option id>
  divergence: <if claude != codex, why; null if agree>
gemini_decision:                  # filled in step 5 of decision flow
  pick: <option id>
  ranking: [<id>, <id>, ...]      # 모든 옵션 순위
  reasoning: <multi-paragraph>
  confidence: high | medium | low
  override_required: bool         # true if pick rejected by both Claude+Codex
sanity_audit:                     # filled in step 6b only (override case)
  result: PASS | FAIL
  notes: <Codex sanity audit reasoning>
attempts:                         # retry / resume 시 append
  - n: 1
    timestamp: <ISO8601>
    outcome: success | parse_failure | timeout | quota_exhausted | malformed
              | invalid_packet | unauthorized | repeated_identical | dual_failure
              | schema_terminal_failure | parse_terminal_failure | user_override
              | gemini_suspended
authority_transfer:               # quota/auth 실패 시
  occurred: bool
  final_decider: gemini | codex_legacy | user
fallback_unavailable: bool        # Gemini + Codex 동시 차단 시
```

## 3. 항목 정의

### 3.1 packet identity

- `packet_id`: Story KEY + 3-digit zero-padded seq (예: CFP-57-001). 같은 Story 내 단조 증가.
- `content_hash`: options + context 정규화 후 sha256. "같은 packet" 정의 = packet_id + content_hash 동시 일치. content 변경 시 새 packet 발급.

### 3.2 trigger enum

- `option-formulation`: substantive 다중 선택지 (stop point a)
- `fix-root-cause`: FIX Ledger 원인 판정 Claude vs Codex 불일치 (stop point b)
- `codex-ambiguity`: Codex 가 결론 회피 (stop point c)
- `brainstorming-constraint`: brainstorming clarifying Q 의 d-constraint sub-class (stop point d-constraint)

### 3.3 options

- `source`: 옵션 작성자 (`claude` / `codex` / `both` — 양 LLM 가 동일 옵션 생성 시).
- `rationale`: 옵션 생성자 분석 multi-paragraph.
- `cross_review`: 상대 LLM 의 평가 (agree/disagree + 근거).

### 3.4 gemini_decision

- `pick`: options[].id 중 하나.
- `ranking`: 모든 옵션 순위 (pick 포함).
- `confidence`: enum {high, medium, low}. Phase 1 audit trail 보강.
- `override_required`: pick 이 Claude+Codex 둘 다 reject 한 옵션이면 true → step 6b sanity audit 진입.

### 3.5 attempts

- 매 retry / resume / fallback 시 append.
- `outcome` enum 13 값:
  - `success` — Gemini 정상 응답 + schema 정합
  - `parse_failure` — 응답 parse 실패 (1 회 retry 대상)
  - `timeout` / `quota_exhausted` / `unauthorized` / `malformed` / `invalid_packet` — fallback matrix row 트리거
  - `repeated_identical` — ≥2 회 동일 pick 반복 실패
  - `dual_failure` — Gemini + Codex 동시 차단
  - `schema_terminal_failure` / `parse_terminal_failure` — retry 후에도 실패 → user escalation
  - `user_override` — 사용자 mid-flow 직접 결정
  - `gemini_suspended` — suspend 중 발생, Claude·Codex 합의 임시 proceed

### 3.6 authority_transfer

- Gemini quota/auth 실패 시 `occurred: true` + `final_decider` 변경.
- `codex_legacy` = quota exhausted 시 Codex audit gate 임시 권한.
- `user` = unauthorized / repeated / dual_failure 시 사용자 escalation.

### 3.7 fallback_unavailable

- Gemini + Codex 동시 차단 시 true. 사용자 escalation + packet draft 첨부.

## 4. 변경 규칙

### 4.1 라이프사이클

- 생성: Claude 본세션이 trigger 발화 시 schema 따라 수동 작성 (Phase 1 doc-only).
- 저장: `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` (full schema), Story §12 (요약 1 row).
- Retention: Story closure 까지. closure 후 archive 정책 후속 (CFP-57 §4.1 Open Item).
- Audit: 첫 5 packet scheduled self-audit, 그 후 failure-driven.

### 4.2 Versioning (ADR-008 정합)

- Breaking change 시 v2 발급 + 본 v1 status=Archived.
- Phase 1 운영 후 schema deviation 다수 발견 시 v2 검토 (CFP-57 §4.1 Open Item).
- Schema 추가 (필드 신설) = minor (v1 → v1.1, MANIFEST.yaml 변경 없음, kind:registry 라 lint scope 밖).
- 필드 삭제 / enum 축소 / 의미 재정의 = major (v2 신규 file).

### 4.3 검증

본 registry 는 lint scope 밖 (kind:registry). 운영 검증 = CFP-57 Phase 1 acceptance target (N≥30, zero whitelist-out, 100% schema 준수).
