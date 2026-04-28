---
adr_number: 008
title: Inter-plugin Contract Versioning — review_verdict v1.x compat / v2.0 BREAKING
status: Accepted
category: Architecture
date: 2026-04-28
related_files:
  - docs/inter-plugin-contracts/review-verdict-v1.md
  - CLAUDE.md
  - docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md
related_stories:
  - CFP-29 (본 ADR 신설 시점)
  - CFP-25 (parent design — staged ε)
---

# ADR-008: Inter-plugin Contract Versioning — review_verdict v1.x compat / v2.0 BREAKING

## 상태

`Accepted` (2026-04-28)

## 컨텍스트

CFP-29 Phase 1에서 codeforge core 의 review subsystem이 별도 plugin (`codeforge-review`)으로 추출. 두 plugin이 양방향 schema(`review_packet` core→review, `review_verdict` review→core)로 통신. CFP-25 design spec §10.5 risk: contract drift — codeforge-review 단독 변경이 contract을 깨면 silent corruption 발생 위험.

CFP-29 spec §4.3 동결: contract_version 필드 + versioning 룰 명시. 본 ADR이 그 룰을 정식 결정.

## 결정

### 1. SemVer-style versioning

`review_packet.contract_version` 과 `review_verdict.contract_version` 필드는 SemVer 2.0.0 형태 (`MAJOR.MINOR`). MAJOR=1로 시작 (CFP-29 v1.0).

### 2. v1.x backward-compatible 변경 룰

다음 변경은 v1.x minor bump (예: v1.0 → v1.1) — 양쪽 plugin 양방향 호환:

- 새 **선택 필드** 추가 (필수 필드 추가 금지)
- 기존 필드의 **enum 값 추가** (제거 금지)
- 기존 필드의 description / 주석 / SSOT 위치 변경

위 변경은 한쪽 plugin만 단독 bump 가능 — 다른 쪽이 v1.0 인 채로도 정상 동작 (선택 필드 못 보냄/못 받음 = no-op).

### 3. v2.0 BREAKING 변경 룰

다음 변경은 MAJOR bump (v1.x → v2.0):

- **필수 필드** 추가 / 제거 / rename
- 기존 필드의 **type 변경** (예: string → array)
- 기존 enum 값 **제거** 또는 의미 변경
- 흐름 자체 변경 (예: 양방향 → 단방향)

v2.0 변경은:
1. **양쪽 plugin 동시 bump 의무** — codeforge core + codeforge-review 동시 release
2. **새 ADR 신설 의무** — 본 ADR-008을 supersede
3. **migration-guide v2 섹션 의무** — consumer 조치 명시
4. **이전 v1.x 와 backward-compat 부재** — codeforge core가 v1 verdict 받으면 ESCALATE (warning fallback 금지)

### 4. version mismatch 런타임 처리

codeforge core 가 verdict.contract_version 을 모르는 값으로 받으면:
- v1.0 expected, v2.0 received → ESCALATE_VERSION_MISMATCH (양쪽 plugin update 필요)
- v1.0 expected, v1.5 received → 정상 동작 (v1.x compat 룰)
- v1.0 expected, "unknown" 또는 missing → ESCALATE (corruption 의심)

### 5. SSOT 위치 룰

- `docs/inter-plugin-contracts/review-verdict-v<MAJOR>.md` — 상세 schema 본문 (현재 v1)
- `CLAUDE.md` "## Inter-plugin Contract" 섹션 — 요약 + cross-ref
- 새 MAJOR 시점에 `review-verdict-v<NEW>.md` 신설, 이전 file은 historical record로 유지 (삭제 금지)

### 6. enforcement (현재 상태 + 향후)

- **CFP-29 시점 (현재)**: enforcement는 manual convention. ADR-008이 룰 동결, 실제 위반 catch는 dogfood + code review
- **향후 (CFP-30+ 조건부)**: contract validation lint 추가 가능. v2.0 발의 시점에서 결정. 현재 plan 범위 밖

## 결과

### 긍정

- contract drift 위험 → 명시적 룰로 통제
- consumer가 contract version 문법으로 호환성 확인 가능
- v1.x bump가 자유로워짐 → review plugin이 자체 cadence로 발전 가능
- v2.0 bump 부담을 명시 → 양쪽 plugin 동시 release를 미리 인지

### 부정 / Trade-off

- 룰 위반 자동 catch 부재 (manual convention) — CFP-29 시점 한계
- 향후 v2.0 BREAKING 시 양쪽 plugin 동시 release coordination 부담
- consumer가 두 plugin 의 version 호환성 매트릭스를 별도로 추적해야 함 (codeforge core CHANGELOG가 codeforge-review compat 명시 의무)

### 영향

- codeforge core: 본 ADR + `docs/inter-plugin-contracts/review-verdict-v1.md` SSOT 보유 + 향후 v2.0 발의 시 새 ADR 의무
- codeforge-review: README + CHANGELOG에 contract version compat 명시
- 향후 plugin 추출 (CFP-25 §10.2 Phase 2 — arch-deputies / req-deputies 등): 동일 룰 적용 (각 plugin 추출 시 own contract + ADR)

## 다이어그램

```
v1.0 (CFP-29 동결)
   │
   ├── v1.1 (예: findings[].suggested_fix_diff 추가) — 한쪽 단독 bump 가능
   ├── v1.2 (예: cost_token_estimate 추가)         — 한쪽 단독 bump 가능
   │
   ▼ (BREAKING 결정 시)
v2.0 — 양쪽 동시 bump + 새 ADR
   │
   └── (이전 ADR-008은 v1 historical record로 유지)
```

## 관련 파일

- [`docs/inter-plugin-contracts/review-verdict-v1.md`](../inter-plugin-contracts/review-verdict-v1.md) — v1 상세 schema (본 ADR이 versioning 룰 동결)
- [`CLAUDE.md`](../../CLAUDE.md) "## Inter-plugin Contract" 섹션
- [CFP-29 design spec](../superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md) §4.3 — 본 ADR의 motivation
- [`mclayer/plugin-codeforge-review`](https://github.com/mclayer/plugin-codeforge-review) — v1 contract 준수 plugin
