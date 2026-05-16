---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: timestamp-display-policy
title: codeforge KST timestamp display 정책 — Layer-bounded authority + 5 governance 원칙
status: Active
updated: 2026-05-16
carrier_story: CFP-770
related_adrs:
  - ADR-079  # KST timestamp display mandate (Layer-bounded) — 본 정책 normative SSOT
  - ADR-057  # Orchestrator Opus mandate — consumer overlay 축소 불가 패턴 정합
  - ADR-073  # verify-before-assert — external timestamp 무변조 invariant
  - ADR-058  # ADR sunset criteria — is_transitional:false governance presumption 정합
tags:
  - kst
  - timestamp
  - governance
  - layer-bounded
  - display-policy
  - consumer-overlay
---

# KST timestamp display 정책

## 정의

codeforge 모든 governance self-write 에서 시각을 표기할 때 **KST `+09:00` ISO 8601 zoned 형식**을 사용한다. contract field layer (7 inter-plugin contract + Story §14 schema field) 의 timestamp 정의는 **0건 변경** (Layer-bounded — ADR-079 §결정 1 first historical decision, 2026-05-16 KST).

## 컨텍스트

codeforge 시스템에서 display layer 와 contract field layer 의 시각 표기 권한이 명문화되지 않은 상태였다. UTC 강제 정책 (CFP-295 / Issue #302 sealed) 은 contract field layer 한정이었으나 display layer 적용 영역이 미분리 상태여서 두 layer 가 한 정책 안에서 충돌. memory `feedback_time_display` 가 유일한 KST display 근거였으나 ephemeral·non-authoritative 상태. 본 정책이 ADR-079 §결정 1 first historical decision 으로 display layer KST 강제를 SSOT 영구 layer 에 확립 (ADR-079 §배경 root cause 인용).

## 핵심 규칙

### 원칙 1 — Layer-bounded authority

시각 표기 권한은 **두 disjoint layer** 로 분리된다:

| Layer | 권한 | SSOT |
|---|---|---|
| display layer (governance self-write) | KST `+09:00` 강제 | ADR-079 §결정 1·2 |
| contract field layer (machine-readable) | UTC strict 0건 변경 (CFP-295 / Issue #302 sealed 보존) | ADR-079 §결정 3 |

두 layer 는 변환 관계가 아니다 — notation rule only, value transform 없음.

### 원칙 2 — scope-bounded-tz-authority

**governance self-write 영역만** KST 직접 표기. external timestamp (GitHub API / git commit) 는:

- UTC verbatim 보존 의무 (변조 금지 — ADR-073 verify-before-assert 정합)
- KST parenthetical 부기 허용: `2026-05-16T10:30:00Z (19:30 KST)`

이 경계가 audit trail 오염 없는 KST display 를 가능하게 한다.

### 원칙 3 — audit-trail-coherence

KST display 가 audit trail 을 깨지 않는 이유:

1. display layer 와 contract field layer 가 disjoint — 두 layer 모두 독립적으로 올바름
2. external timestamp 변조 금지 — 원본 UTC verbatim 보존으로 재현 가능
3. consumer cross-Story 시각 비교 = KST 단일 기준으로 일관성 보장 (wrapper-canonical)

multi-consumer 환경에서 각 consumer 가 다른 timezone 을 쓰면 cross-Story 시각 비교가 불가능해짐 → wrapper-canonical KST 단일 기준 의무.

### 원칙 4 — forward-only

**2026-05-16 KST 이후 신규 작성분만 적용** (ADR-079 §결정 6). legacy retroactive backfill 미수행. 이유:

- 레거시 timestamp 는 형식이 이미 확정된 sealed state — 수정 시 audit trail 변조 위험
- 점진 적용 = Phase 2 CFP-771 `hotfix-bypass:kst-timestamp-display` 점진 정리 (별도 carrier)
- DataMigrationArch "retroactive backfill 부적합" 경고 정합

### 원칙 5 — consumer overlay tz override 불가

wrapper-canonical KST 강제. consumer overlay (`.claude/_overlay/`) 는 **이 정책을 축소할 수 없고 확장만 가능** (CLAUDE.md normative + ADR-057 정합).

미국/유럽 consumer 도입 시 별도 CFP (현 scope 외). 단일 tz 기준 의무 이유:

- cross-consumer Story 시각 비교 일관성 (audit-trail-coherence 원칙 3)
- codeforge 플러그인은 한국 ops context 기반 — KST = 1st-class timezone

## 경계

### 적용 영역 (display layer)

| # | 영역 | 형식 |
|---|---|---|
| D-1 | Orchestrator ↔ 사용자 dialog | `2026-05-16 19:30 KST` (prose 허용) |
| D-2 | CLAUDE.md 정책 효력 시점 표기 | `2026-05-16T19:30:00+09:00` |
| D-3 | playbook 섹션 정책 효력 시점 | 동 D-2 |
| D-4 | ADR amendment_log `date:` | date-only KST 일자 의미 (`2026-05-16`) |
| D-5 | retro 작성 시각 + auto-trigger 시각 | `2026-05-16T19:30:00+09:00` |
| D-6 | EPIC-RESULTS `opened_at` / `closed_at` | ISO 8601 zoned |
| D-7 | Story §10 FIX Ledger 시각 | Orchestrator local KST clock |
| D-8 | Story §14 본문 markdown 표 Start/End column | KST `+09:00` (schema field 와 disjoint co-exist) |
| D-9 | `[PAUSE]` / `[RESUME]` checkpoint | `[PAUSE] 2026-05-16T19:30:00+09:00 — <사유>` |
| D-10 | `[RETRO TRIGGER]` comment prefix | `[RETRO TRIGGER] 2026-05-16T19:30:00+09:00 — ...` |

### 비적용 영역 (contract field layer — 0건 변경)

| 영역 | 형식 | 근거 |
|---|---|---|
| fix-event-v1 `시각` | UTC strict Z suffix | CFP-295 / Issue #302 sealed |
| git-ops-event-v1 `timestamp` | UTC strict Z suffix | 동 |
| debate-protocol-v1 `detected_at`·`emitted_at`·`terminated_at` | UTC strict Z suffix | 동 |
| stop-event-v1 `timestamp` | UTC strict Z suffix | 동 |
| evidence-check-registry-v1 `recurrence.last_occurrence` | UTC strict Z suffix | 동 |
| test-verdict-v2 `executed_at` | ISO8601 bare | sealed pre-decision 보존 |
| pmo-output-v1 `worktree_manifest.events[].timestamp` | ISO8601 bare | 동 |
| Story §14 schema field `spawned_at`/`returned_at` | ISO8601 UTC | ADR-031 §결정 3, `check-lane-evidence.sh` lint 대상 |

### 가시성 4 영역 (ADR-079 §결정 5)

사용자 directive 실제 동기 = "Orchestrator holding/지연 상태 가시성 부재". 단순 KST 숫자 표기를 넘어:

1. **V-1 (PRIMARY)** — `[PAUSE]` / `[RESUME]` checkpoint (사용자 directive 직접 지목)
2. **V-2 (secondary)** — `[RETRO TRIGGER]` comment prefix (ADR-045 / CFP-138 정합)
3. **V-3 (secondary)** — §10 FIX Ledger dual-clock (Orchestrator KST vs GitHub UTC mirror)
4. **V-4 (secondary)** — ADR amendment_log `date:` date-only KST 일자 의미 normative

## 관련 ADR

- [ADR-079: KST timestamp display mandate](../../../adr/ADR-079-kst-timestamp-display-mandate.md) — normative SSOT
- [kst-display-invariant](../../concept/kst-display-invariant.md) — 개념 SSOT
- [CLAUDE.md §시각 표시 정책](../../../../CLAUDE.md) — cross-cutting 요약

## 변경 이력

| 일자 | 변경 내용 | carrier |
|---|---|---|
| 2026-05-16 | 초기 신설 — codeforge KST timestamp display 정책 narrative SSOT | CFP-770 |
