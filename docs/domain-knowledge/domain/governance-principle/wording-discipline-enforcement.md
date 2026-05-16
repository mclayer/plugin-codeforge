---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: wording-discipline-enforcement
title: codeforge wording-discipline — registration ↔ enforcement 2-layer 분리 + lint scope 확장의 강화 방향 판정 SSOT
status: Active
tags:
  - wording-discipline
  - forbid-list
  - lint-scope
  - top-down-ratchet
  - evidence-enforceable
  - adr-064
  - adr-058
  - adr-060
related_adrs:
  - ADR-064  # forbid-list dictionary normative carrier (§결정 2 + Amendment 2/4)
  - ADR-058  # sunset criteria mandate — ratchet 차단 (§결정 5 sunset_justification)
  - ADR-060  # evidence-enforceable promotion framework (warning → blocking tier)
  - ADR-024  # hotfix-bypass:* per-entry namespace exempt channel
related_stories:
  - CFP-610  # wording-dictionary 신설 + `박제` 등 4 어휘 등록 (Amendment 2)
  - CFP-672  # 별 standalone 추가 (Amendment 4 — entry 추가 = ratchet 첫 패턴군)
  - CFP-750  # lint scope 확장 + 기존 전수 sweep (Amendment 5 — scope 확장 = ratchet 두 번째 축)
created: 2026-05-16
updated: 2026-05-16
---

# codeforge wording-discipline — registration ↔ enforcement 2-layer 분리 SSOT

## 정의

**wording-discipline enforcement** 는 codeforge 의 어휘 규율 (`docs/wording-dictionary.md` 카테고리 (a) forbid-list) 이 **실제 문서에서 사용 불가가 되도록 강제하는 메커니즘 layer** 다. [decision-style](decision-style.md) 가 결정 *내용/제시/속도* 의 행동 패턴 SSOT 라면, 본 페이지는 그 결정 원칙이 산출한 forbid-list 어휘가 **어떻게 실효성을 갖는가** (등록 ↔ 강제의 분리, scope 확장이 ratchet 인지의 판정) 의 행동 패턴 SSOT 다.

핵심 명제: **어휘를 forbid-list 에 등록하는 것 (registration)** 과 **그 어휘가 실제로 사용 불가가 되는 것 (enforcement)** 은 별개 layer 다. 등록만으로는 실사용이 지속될 수 있고, 두 enforcement 변수 — (1) tier (warning vs blocking) (2) lint scope coverage — 가 동시에 충족되어야 실효성이 생긴다.

## 컨텍스트

본 SSOT 정립 동인은 CFP-750 (사용자 directive verbatim: `박제라는 단어 쓰지 못하게 하라`, 2026-05-16 KST) 이다. `박제` 는 CFP-610 / ADR-064 Amendment 2 로 이미 wording-dictionary 카테고리 (a) 에 등록돼 있었으나, 거버넌스 문서 전반에서 실사용이 지속되고 있었다. 원인은 enforcement layer 의 2 공백:

1. **tier 공백** — `scripts/check-wording-dictionary.sh` 가 ADR-060 warning tier (exit 1 경고만, PR 머지 미차단). 작성자가 경고를 무시하면 그대로 merge.
2. **scope 공백** — lint 적용 영역이 5-scope (`docs/adr/**` / `docs/change-plans/**` / `CLAUDE.md` / `docs/orchestrator-playbook.md` / `templates/**`) 한정. `docs/inter-plugin-contracts/**` / `CHANGELOG.md` 등 미커버 영역에서 `박제` 잔존 (예: `parallel-dispatch-protocol-v1.md` 의 `의무 박제` 등 핵심 용어 ~10회 — CFP-750 Amendment 5 전수 sweep 으로 해소).

이 패턴은 codeforge governance 의 일반 현상이다 — ADR-064 §결정 8 (Declaration only) 이 명문화하듯, codeforge 는 normative declaration 과 mechanical enforcement 를 의도적으로 분리해 evidence-enforceable 점진 적용 (ADR-060) 한다. 그 결과 "등록됐으나 강제되지 않는" 중간 상태가 구조적으로 발생하며, 본 SSOT 는 그 상태의 해소 행동 패턴을 정립한다.

## 핵심 규칙

### 규칙 1 — Registration ↔ Enforcement 2-layer 분리

| Layer | 정의 | 산출물 | SSOT |
|---|---|---|---|
| **Registration** | 어휘를 forbid-list 에 등록 (의미 정의 + 권장 대체 명시) | `docs/wording-dictionary.md` 카테고리 (a) row + ADR-064 §결정 2 표 + lint script `FORBID_DICTIONARY` array (lockstep 3-point) | ADR-064 §결정 2 |
| **Enforcement** | 등록 어휘가 실제 사용 불가가 되도록 강제 | (a) tier (ADR-060 4-tier) + (b) lint scope coverage + (c) 기존 occurrence 전수 sweep | ADR-060 §결정 3·5 + 본 페이지 |

Registration 완료 ≠ 실효성 확보. Enforcement layer 의 3 변수 (tier / scope / sweep) 가 미충족이면 등록 어휘는 "선언적 금지" 상태로 잔존한다. 사용자가 "이미 금지인데 안 지켜진다" 라고 발화하면 = registration 은 완료, enforcement layer 공백 신호. → 신규 등록(Amendment 추가)이 아닌 enforcement 강화 Story 로 해석 (CFP-750 derived interpretation 패턴).

### 규칙 2 — Enforcement 강화 3-축

등록 어휘의 실효성을 높이는 3 독립 축. 각 축 강화는 모두 ratchet 강화 방향 (규칙 3 참조):

| 축 | 강화 방향 | ADR-060 / ADR-064 정합 |
|---|---|---|
| **tier 승격** | warning → blocking-on-pr → blocking-on-merge | ADR-060 §결정 5 4-tier. 승격 게이트 = 누적 PR ≥ 20 + bypass 외 failure = 0 + sibling Story merged (AND condition) |
| **scope 확장** | 5-scope → 거버넌스 문서 전체 (+`docs/inter-plugin-contracts/**` + `CHANGELOG.md` 등) | lint script 기본 TARGETS 확장 + workflow self-app scope 동기화 + EXEMPT_FILES 정합 |
| **기존 전수 sweep** | 잔존 occurrence 0 달성 (의미 보존 치환) | `명시` / `확정` / `기재` 등 권장 대체로 치환 — 계약 의미 불변 보존 의무 (inter-plugin-contract 영역 특히) |

3 축은 독립이지만 상호 보강한다. 특히 **tier 승격이 별도 트랙(누적 PR 게이트)으로 지연되더라도, scope 확장 + 전수 sweep 만으로 "실사용 0" 을 달성하면 사실상 사용 불가**가 된다 (CFP-750 도출 scope 패턴 — blocking 격상 없이 실효성 확보).

### 규칙 3 — Lint scope 확장 = 강화 방향 (sunset_justification 불요) 판정

ADR-064 §결정 7 self-application top-down ratchet 은 amendment 를 강화 방향만 허용하고, 약화 방향은 ADR-058 §결정 5 sunset_justification 의무로 차단한다. **lint scope 확장이 강화 방향인지의 판정 기준**:

| Amendment 변경 | 방향 | sunset_justification | 근거 |
|---|---|---|---|
| forbid-list 어휘 추가 (8→12, 4→5) | **강화** | 불요 | ADR-064 Amendment 2/4 self-application 시연 (entry 추가 = scope 확장) |
| **lint scope 영역 확장 (5→전체)** | **강화** | **불요** | 동일 ratchet 축의 두 번째 instantiation — 검사 *대상* 확대 = 강제 *범위* 확대. forbid-list 어휘 추가와 동형 (등록 어휘가 더 많은 문서에서 실효) |
| tier 승격 (warning→blocking) | **강화** | 불요 | ADR-060 §결정 5 4-tier 승격 = 강도 강화 |
| forbid-list 어휘 축소 | 약화 | **의무** | ADR-064 §결정 7 forbid-list dictionary 축소 명시 차단 |
| lint scope 축소 | 약화 | **의무** | scope 확장의 역방향 = framework 축소 (대칭 추론) |
| tier 강등 (blocking→warning) | 약화 | **의무** | ADR-060 §결정 5 강도 약화 |

**판정 원리**: ratchet 의 "강화" 는 *"등록 어휘가 실제로 사용 불가가 되는 정도가 단조 증가하는가"* 로 판정한다. forbid-list 어휘 추가 / lint scope 확장 / tier 승격 / 기존 전수 sweep 은 모두 이 정도를 증가시키므로 강화 방향 → ADR-058 §결정 5 sunset_justification 불요. Amendment 2 (forbid-list 8→12) 가 첫 self-application 사례, Amendment 4 (4→5 카테고리 a) 가 두 번째, CFP-750 의 Amendment 5 (lint scope 5→전체) 가 **scope 축 첫 ratchet 사례** — 어휘 축 ratchet 과 동형 판정.

### 규칙 4 — EXEMPT 영역 보존 의무 (false-positive 완화 framework 불변)

scope 확장 시에도 false-positive 완화 framework 는 보존한다 (framework 축소 0건 — ratchet 강화 정합):

- **EXEMPT_FILES**: `docs/wording-dictionary.md` (사전 파일 — 어휘 정의 목적) + `docs/adr/ADR-064-decision-principle-mandate.md` (§결정 2 forbid-list 정의 표). scope 확장으로 신규 검사 대상에 사전 성격 파일 추가 시 EXEMPT_FILES row append 의무.
- **blockquote (`>` prefix) exempt**: 외부 인용 / 사용자 발화 verbatim 영역. ADR-064 §결정 2 "dictionary 본문 자체 또는 외부 인용 영역 등장은 외연 허용" 정합.
- **fenced code block exempt**: 코드 블록 내부.
- **한국어 substring vs 영어 word-boundary**: `박제` / `못 박기` = substring match (POSIX `\b` 한국어 의미 부재). `별` standalone = Hangul-boundary lookahead/lookbehind PCRE. `pin` / `freezing` = word-boundary + case-insensitive (일반 영어 false-positive 차단).

scope 확장이 EXEMPT framework 를 *축소* 하면 (예: blockquote exempt 제거) = 강화 아닌 별개 약화 변경 → 별도 sunset_justification 판정 필요. CFP-750 도출 scope 는 EXEMPT framework 불변 명시 (Amendment 2 framework 재사용).

### 규칙 5 — 의미 보존 sweep 의무 (계약 영역 특히)

기존 occurrence 전수 sweep 시 권장 대체는 **의미 보존 치환**이어야 한다. `박제` 의 권장 대체 = 맥락에 따라 `명시` / `확정` / `기재` 선택 (ADR-064 §결정 2 표). `docs/inter-plugin-contracts/**` 영역 sweep 시 **계약 의미 불변** 이 최우선 invariant — contract semantic 이 어휘 치환으로 변하면 sibling sync drift (ADR-010) / contract version bump 오발 위험. inter-plugin-contract 영역 sweep 은 치환 전후 contract 의미 동일성을 별도 검증해야 한다 (DesignReview lane 영역).

## 경계

### In-scope (본 SSOT 적용 영역)

- **wording-dictionary 카테고리 (a) forbid-list enforcement** — 등록 어휘의 tier / scope / sweep 3-축 강화 행동.
- **lint scope 확장의 ratchet 방향 판정** — ADR-064 §결정 7 + ADR-058 §결정 5 정합 판정 (강화 = sunset_justification 불요).
- **registration ↔ enforcement 분리 진단** — "이미 금지인데 안 지켜진다" 신호의 derived interpretation (신규 등록 아닌 enforcement 강화 Story).

### Out-of-scope (본 SSOT 적용 외 영역)

- **카테고리 (b) 평문 정의 동반 의무 어휘** — advisory-only (exit 0), baseline 폭증 risk 완화 영역. 본 SSOT 의 tier/scope ratchet 판정은 카테고리 (a) forbid 한정.
- **behavioral directive 영역** (Orchestrator user-facing dialog text turn) — mechanical enforce 미시도, retro audit signal 만 (PMOAgent retro file §wording-discipline 표). ADR-064 §결정 9 stop-time wording 영역.
- **신규 어휘 등록 절차** — `docs/wording-dictionary.md` §신규 entry 추가 절차 (별 CFP brainstorm + ADR-064 Amendment N) 가 owner. 본 SSOT 는 *등록 후 enforcement* 영역.
- **`hotfix-bypass:wording-dictionary` label 부착 PR** — audit-trailed exception channel (ADR-024 Amendment 3 per-entry namespace). 정책 회피 등록 channel 아님 (ADR-060 Amendment 3 의미 sharpening 정합).
- **tier 승격 게이트 평가 자체** — ADR-060 §결정 5 AND condition (누적 PR ≥ 20 + bypass 외 failure = 0 + sibling merged) 측정은 별도 트랙. 본 SSOT 는 tier 가 enforcement 3-축의 하나임을 정립할 뿐, 게이트 측정 절차는 ADR-060 owner.

## 관련 ADR

- [ADR-064](../../../adr/ADR-064-decision-principle-mandate.md) — forbid-list dictionary normative carrier. §결정 2 (forbid-list + Amendment 2/4 어휘 추가) + §결정 7 (self-application top-down ratchet — 본 SSOT 규칙 3 의 판정 근거) + §결정 8 (Declaration only — registration ↔ enforcement 분리의 구조적 동인).
- [ADR-058](../../../adr/ADR-058-adr-sunset-criteria-mandate.md) — sunset criteria mandate. §결정 5 sunset_justification 의무 = 약화 방향 amendment 차단. 본 SSOT 규칙 3 의 "강화 = sunset_justification 불요" 판정의 대칭 anchor.
- [ADR-060](../../../adr/ADR-060-evidence-enforceable-promotion-framework.md) — evidence-enforceable promotion framework. 4-tier (warning → blocking-on-pr → blocking-on-merge → hotfix-bypass) + 승격 게이트 AND condition. 본 SSOT 규칙 2 tier 축의 SSOT.
- [ADR-024](../../../adr/ADR-024-story-scoped-branch-policy.md) — Amendment 3 per-entry `hotfix-bypass:*` namespace. enforcement 의 audit-trailed exception channel (정책 회피 등록 아님).
- [decision-style](decision-style.md) — sibling domain knowledge. 결정 *내용/제시/속도* 행동 패턴 (Trace 1/2/4). 본 페이지는 그 결정 원칙이 산출한 forbid-list 의 *enforcement layer* 행동 패턴 — disjoint scope (decision-style = 결정 발생, 본 페이지 = 결정 산출물의 실효성).

## 변경 이력

- **2026-05-16** — 신설 (CFP-750 carrier). registration ↔ enforcement 2-layer 분리 + lint scope 확장의 강화 방향 판정 SSOT 정립. 지식 공백 동인: `governance-principle` 영역에 decision-style.md (결정 발생 행동) 만 존재, forbid-list 어휘의 *enforcement layer* (tier/scope/sweep 3-축 + scope 확장 ratchet 판정) SSOT 부재 — CFP-750 "이미 금지인데 안 지켜진다" derived interpretation 의 도메인 근거 부재 공백 해소.
