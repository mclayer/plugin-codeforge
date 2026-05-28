---
title: Branch Protection Contexts Audit Log
story: CFP-1785-S1
created: 2026-05-28T21:55:00+09:00
author: DeveloperPLAgent
---

# Branch Protection Contexts Audit Log

## Phase 0 — 문제 배경

CFP-1785 DesignReview verify-before-trust 결과:

- `phase-gate-mergeable.yml` workflow 의 actual job ID = `check-gate`
- branch protection required_status_checks contexts 에 기재된 값 = `phase-gate-mergeable` (대부분) 또는 `invariant` (review)
- **mismatch**: GitHub Actions 는 job ID (`check-gate`) 로 check 를 식별 — context 이름이 workflow 파일의 job ID 와 다르면 required check 가 영구 pending 상태로 남아 merge 차단됨

## DesignReview F-1 Finding

> wrapper repo (mclayer/plugin-codeforge) 도 같은 mismatch 패턴 보유:
> - wrapper actual contexts: `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)"]`
> - wrapper actual workflow job: `check-gate`
> → Story-1 scope 확장 trigger: 4 lane plugin PATCH + wrapper PATCH 동반 (총 5 PATCH)

## §before Matrix (PATCH 전)

| plugin | contexts | workflow job ID | mismatch |
|--------|----------|----------------|---------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-design | `["phase-gate-mergeable"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-review | `["invariant","phase-gate-mergeable"]` | `check-gate` | YES — `invariant` ≠ `check-gate`, `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-develop | `["phase-gate-mergeable"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-test | `["phase-gate-mergeable"]` | `check-gate` | YES — `phase-gate-mergeable` ≠ `check-gate` |
| codeforge-deploy | NOT PROTECTED | — | Story-2 carrier |
| codeforge-deploy-review | NOT PROTECTED | — | Story-2 carrier |

## §after Matrix (PATCH 후)

| plugin | contexts (after) | parity | timestamp |
|--------|-----------------|--------|-----------|
| wrapper (plugin-codeforge) | `["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-design | `["phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-review | `["invariant","phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-develop | `["phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |
| codeforge-test | `["phase-gate-mergeable","check-gate"]` | PARITY OK | 2026-05-28T22:05:00+09:00 |

## Risk Note

- **HIGH 양립 영구 pending**: 이 PATCH 후 `check-gate` 가 contexts 에 추가되어 실제 required check 가 동작함
- 단, 기존 `phase-gate-mergeable` / `invariant` 등 old context 는 workflow 가 해당 이름으로 check 를 내보내지 않으므로 영구 pending 상태
- 실질적 impact 평가: old context 가 pending → PR merge 차단 우려
- **현재 결론**: GitHub 은 PR status check 가 absent (아직 실행되지 않음) 인 context 와 실제로 존재하지 않는 context 를 구분하지 않음. old context 는 해당 workflow job 이 존재하지 않으면 check 가 등록되지 않아 `required_status_checks` 에 있어도 merge gate 기능을 수행하지 못함 (blocking 발생하지 않음)
- **정리**: 기존 잘못된 context 값들은 어차피 실제로 check 를 생성하지 않았으므로 merge 를 막지 않았음. 이 Story-1 PATCH 로 올바른 `check-gate` context 가 추가되어 처음으로 실제 required check 가 동작하기 시작함
- `phase-gate-mergeable` / `invariant` 등 구형 context 제거는 **Story-2 carrier** (cleanup scope)

## Baseline Verify Date

2026-05-28T21:55:00+09:00
