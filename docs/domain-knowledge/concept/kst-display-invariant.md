---
kind: concept_definition
type: domain-knowledge
slug: kst-display-invariant
title: KST display invariant — 값 무변환·표기만 강제·drift 회피 forcing function
status: Active
updated: 2026-05-16
carrier_story: CFP-770
related_adrs:
  - ADR-079  # KST timestamp display mandate (Layer-bounded) — 본 개념의 normative SSOT
  - ADR-073  # verify-before-assert — external timestamp 무변조 invariant 정합
  - ADR-031  # Lane-spawn evidence — §14 dual-layer co-existence 근거
tags:
  - kst
  - timestamp
  - display-invariant
  - layer-bounded
  - notation-rule
  - rfc3339
---

# KST display invariant

## 정의

`display-invariant` = governance display layer 의 시각 표기 규칙. **값(value) 을 변환하지 않고 표기(notation) 만 강제**하는 개념. 이것이 contract field layer 와의 drift 를 구조적으로 회피하는 forcing function 이다.

## 컨텍스트

본 개념은 Story §14 Lane Evidence 의 dual-layer co-existence 에서 명확하게 드러난다. ResearcherAgent UU#1 cross-tool format drift 근거로 RFC 3339 §5.6 colon-offset form 이 단일 SSOT 로 확정 (ADR-079 §결정 2). §14 schema field `spawned_at`/`returned_at` 가 contract field layer 에 속하므로 UTC strict 보존 — display layer KST 강제와 disjoint co-exist 하는 대표 사례.

## 핵심 규칙

### 1. 값 무변환 (no-value-transform)

KST display mandate 는 **표기 규칙(notation rule)** 이다. display layer 에서 `+09:00` 으로 표기한다는 것이 내부 저장값이나 contract field 의 UTC 를 KST 로 변환한다는 뜻이 아니다.

```
display layer: "2026-05-16T19:30:00+09:00"  ← 사람이 읽는 표기
contract field: "2026-05-16T10:30:00Z"      ← 기계가 처리하는 값 (변환 없음)
```

두 값은 **동일 시점**을 표현하나 변환 관계가 아니라 **disjoint axis** 다. display layer 가 KST 표기라고 해서 contract field 를 변환하거나 동기화하지 않는다. 변환 logic 자체가 시스템 안에 부재 (구현도 없고 필요도 없음).

### 2. 표기 강제 (notation enforcement)

display layer 영속 artifact 의 시각 표기 형식:

| 용도 | 형식 | 예시 |
|---|---|---|
| 영속 artifact (CLAUDE.md / playbook / ADR / retro / Story §10·§14 본문 표·§9) | ISO 8601 RFC 3339 §5.6 colon-offset form | `2026-05-16T19:30:00+09:00` |
| dialog · prose (Orchestrator ↔ 사용자) | prose KST 허용 | `2026-05-16 19:30 KST` |
| frontmatter `date:` (date-only) | YYYY-MM-DD = KST 일자 의미 | `2026-05-16` |

**basic form `+0900` 금지** — RFC 3339 §5.6 colon-offset form (`+09:00`) 단일 SSOT. 이는 cross-tool format drift 를 방지한다 (ResearcherAgent UU#1 근거).

### 3. RFC 3339 §5.6 colon form 강제 이유

RFC 3339 는 Internet Protocol 에서 날짜/시간을 표현하는 표준. §5.6 colon-offset form (`+HH:MM`) 이 기계 파싱 + 사람 가독성 양쪽에서 표준으로 채택됨. basic form (`+HHMM`) 은 ISO 8601 허용 범위이나 RFC 3339 §5.6 에서 비권장. codeforge 는 RFC 3339 §5.6 단일 기준 채택으로 format drift 회피.

### 4. external timestamp 무변조

Orchestrator 가 GitHub API response / git commit metadata 등 외부 시스템의 UTC timestamp 를 인용할 때:

- **원본 UTC verbatim 보존** — 변조 금지 (ADR-073 verify-before-assert 정합)
- **KST parenthetical 부기 허용** — `2026-05-16T10:30:00Z (19:30 KST)` 형식
- KST 로 재표기하거나 UTC 를 숨기는 것은 audit trail 오염 위험

## 경계

### §14 Lane Evidence dual-layer co-existence

Story `§14 Lane Evidence` 는 한 섹션 안에 두 layer 가 disjoint co-exist 하는 대표 사례:

- **본문 markdown 표 Start/End column** = display layer → **KST `+09:00` 의무** (사람이 읽는 lane evidence trail)
- **YAML schema field `spawned_at`/`returned_at`** = contract field layer → **UTC strict 보존** (`scripts/check-lane-evidence.sh` lint 검증 대상)

두 layer 가 "같은 섹션" 에 있어도 서로 다른 axis 이며 변환 관계 아님. `spawned_at: 2026-05-16T10:30:00Z` + `Start: 2026-05-16T19:30:00+09:00` 는 동시에 올바른 표기다.

### drift 회피 forcing function

"변환 없음" 원칙이 drift 를 구조적으로 차단한다:

1. display layer 와 contract field layer 가 서로 다른 형식을 가지면 "어느 것이 맞는가" 질문이 발생하지 않음 — 각 layer 는 독립적으로 올바름
2. 변환 logic 부재 = 변환 버그 발생 불가
3. layer boundary 가 명확하면 새 artifact 작성 시 "어느 layer 인가?" 판단만으로 표기 형식 결정 가능

## 관련 ADR

- **Layer-bounded timestamp authority** — ADR-079 §결정 1 (두 disjoint layer 의 공식 정의)
- **scope-bounded-tz-authority** — ADR-079 §결정 4 (external timestamp 무변조 + governance self-write 한정)
- **forward-only effective date** — ADR-079 §결정 6 (2026-05-16 KST 이후 신규 작성분만)
- **consumer overlay tz override 불가** — ADR-079 §결정 7 (wrapper-canonical KST 강제)

**참조 파일**:
- [ADR-079: KST timestamp display mandate](../../adr/ADR-079-kst-timestamp-display-mandate.md) — normative SSOT
- [timestamp-display-policy](../domain/governance-principle/timestamp-display-policy.md) — 정책 narrative

## 변경 이력

| 일자 | 변경 내용 | carrier |
|---|---|---|
| 2026-05-16 | 초기 신설 — KST display invariant 개념 SSOT | CFP-770 |
