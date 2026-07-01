---
title: 구현-리팩터링 drop-ledger (cross-Epic append-only)
kind: operational_ledger
status: Active
created: 2026-07-01
carrier_story: CFP-2541
related_adrs:
  - ADR-137  # Epic-close 구현-리팩터링 triage governance — 본 ledger 의 drop verdict substrate + anchor-recurrence(≥2) escalation source
  - ADR-059  # debate-protocol-v1 §3.4 anchor-recurrence(≥2 escalation) — 본 ledger 가 cross-Epic 로 키잉 scope 확장
  - ADR-119  # §결정9 발견≠필요 3문 게이트 — drop verdict rationale 축
---

# 구현-리팩터링 drop-ledger (cross-Epic append-only)

## 목적

Epic-close 구현-리팩터링 triage(ADR-137 §결정2)의 **drop verdict** anchor 를 **cross-Epic** 로 영속화하는 append-only ledger. debate-protocol-v1 §3.4 anchor-recurrence(같은 anchor ≥2 → escalation)의 키잉 scope 를 per-Story §9 transcript → cross-Epic 로 확장하는 substrate (§3.4 원본은 "drop 후 다음 Epic 재발"을 못 봄).

`EPIC-RESULTS-<EPIC_KEY>.md` 는 per-Epic artifact 라 cross-Epic 재발 state 를 담을 수 없어 본 전용 파일이 필수다.

## 스캔·count 주체

- **PMOAgent verdict judge** 가 매 Epic-close triage 시 본 ledger 를 **read → 신규 drop anchor 의 `anchor_stable` 이 기존 row 와 매치되는 count** 산출 → `count(rows WHERE anchor_stable = X) >= 2` 시 사용자 escalation(AskUserQuestion). 상세 = `plugins/codeforge-pmo/agents/PMOAgent.md §4.3 (b)`.
- 본 ledger 는 `check-deferred-item-recovery.sh` **스캔 대상 아님** (§deferred 섹션이 아니라 별 cross-Epic 파일) — PMOAgent 직접 read/count.
- semantic-equivalence 판단 = PL judgment (debate-protocol EC-7 상속 — 명확히 다른 쟁점이면 카운트 안 함, 모호 시 escalation 우선).

## anchor_stable 식별자

`anchor_stable` = `<file>::<Sym>.<method>` (symbol-qualified) OR duplication content-hash. line-independent — `<file>:<line>` 은 리팩터 후 line 이동으로 cross-Epic 붕괴하므로 사용 금지.

## Schema (5-column, append-only)

| anchor_stable | epic_key | disposition | rationale | timestamp |
|---|---|---|---|---|
| <file::Sym.method \| content-hash> | <CFP-NNNN> | drop | <ADR-119 §결정9 3문 결과 — 어느 문이 NO 였는지 (깨졌나·강제요인 / 이득>비용·리스크 / 관찰자 없어도 할 일)> | <YYYY-MM-DD KST> |

- **`rationale` column (Change Plan §3.6 정합)**: drop verdict 근거 = ADR-119 §결정9 3문(깨졌나·강제요인 / 이득>비용·리스크 / 관찰자 없어도 할 일) 중 어느 문이 NO 였는지 audit trail. drop = "발견≠필요 기각"의 검증 가능한 근거 보존 (연극화 방지).
- **append-only**: 기존 row 수정·삭제 금지 (cross-Epic 재발 추적 무결성).
- **dedup key**: `anchor_stable` (append 재실행 중복 방지 — 문서 레벨, DB migration 아님). recurrence count 로직(`count(rows WHERE anchor_stable = X) >= 2`)은 `rationale` column 추가와 무관 (anchor_stable keying 무변경).

## Ledger rows

<!-- Epic-close triage drop verdict 발생 시 PMOAgent 가 append. 최초 baseline = 0 row. -->

(no drop entries yet)
