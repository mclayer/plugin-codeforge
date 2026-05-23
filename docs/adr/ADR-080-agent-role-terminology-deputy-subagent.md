---
title: "ADR-080: Agent role terminology — deputy → SubAgent canonical form + identifier preservation"
adr_number: 80
status: Active
category: governance
date: 2026-05-16
carrier_story: CFP-751
related_adrs:
  - ADR-005  # plugin self-application / N/A standardization — terminology standardization family
  - ADR-010  # inter-plugin contract sibling sync — cross-plugin propagation
  - ADR-039  # Orchestrator subagent default policy — "subagent" 어휘 정합
  - ADR-044  # agent teams enabled context — deputy 역할 시연 영역
  - ADR-064  # decision principle mandate (wording-dictionary) — forbid-list 등록 영역 아님 (terminology 표준화)
  - ADR-014  # operational risk SSOT — "6 deputy mandate 매트릭스" 개념명 발생 원천
  - ADR-072  # production evidence deputy — *DeputyAgent 식별자 발생 원천
schema_version: "1.0"
amendments: []
is_transitional: false
related_stories:
  - CFP-751
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - skills/deputy-mandate/SKILL.md
  - docs/inter-plugin-contracts/  # cross-plugin sibling sync 영역
  - mclayer/plugin-codeforge-design  # cross-plugin (ADR-010 sibling sync 대상)
---

# ADR-080: Agent role terminology — deputy → SubAgent canonical form + identifier preservation

## 상태

Active. CFP-751 carrier (Phase 1 신설).

## 컨텍스트

codeforge family 안 "deputy" 표현이 두 가지 의미로 혼용된다:

1. **일반 명사 (general noun)** — ArchitectPLAgent 가 spawn 하는 하위 전문 에이전트들의 역할 호칭. 예: "6 deputy", "ArchitectPLAgent 직속 deputy", "deputy spawn".
2. **고유 식별자 (identifier)** — `*DeputyAgent` agent type names (LiveOpsDeputyAgent / LiveOrderingDeputyAgent / ProductionEvidenceDeputy 등), skill name `codeforge:deputy-mandate`, 개념명 "Deputy mandate 매트릭스".

사용자 directive (Issue #751, 2026-05-16 KST) verbatim:
> 그리고 deputy라는 표현을 쓰는데 이건 Agent인가? 그렇다면 agent로 못박아라

후속 clarification verbatim:
> 남발하지만 않으면 된다. 기존에 Deputy로 명명한 Agent 명은 두고 SubAgent로 치환 가능한 경우 그렇게 표현하라

**의도**: 영어 jargon "deputy" 가 한국어 native 사용자에게 불투명 + codeforge 전체가 agent 라 식별력 약함 → 고유 식별자/개념명은 보존, 일반 명사 사용은 `SubAgent` 로 표준화.

## 결정

### 결정 1 — Canonical role terminology = "SubAgent"

ArchitectPLAgent 직속 하위 전문 에이전트들의 일반 명사 호칭 = **`SubAgent`** (CamelCase, 영문 그대로). 한국어 prose 안 사용 시 그대로 "SubAgent" 형태. ADR-039 `subagent` 어휘 (lowercase, "Orchestrator subagent default" 맥락) 와 호환 — 본 ADR 의 `SubAgent` 는 design lane 의 specialist 역할 호칭, ADR-039 의 `subagent` 는 Agent tool spawn 모델 일반어. 양자 별도 의미 layer (역할 vs 실행 모델), 충돌 없음.

### 결정 2 — Class-A (치환 대상, 일반 명사) vs Class-B (보존 대상, 식별자/개념명) 분류

**Class-A (치환 — `deputy` → `SubAgent`)** — 일반 명사 사용:
- 수량 + 명사 패턴 (예: "6 deputy", "6 permanent + 3 CONDITIONAL deputy", "8 (PL + chief + 6 deputy)")
- 소유 + 명사 패턴 (예: "ArchitectPLAgent 직속 deputy", "내 deputy")
- 행위 + 명사 패턴 (예: "deputy spawn", "deputy 산출물", "deputy fan-out")
- 정의·서술 prose 안 deputy 사용 일반

**Class-B (보존 — 변경 금지)** — 식별자/고착 개념명:
- **Agent type names**: `LiveOpsDeputyAgent` / `LiveOrderingDeputyAgent` / `ProductionEvidenceDeputy` 등 `*Deputy*Agent` 패턴 (codeforge-design plugin 정의)
- **Skill name**: `codeforge:deputy-mandate` (skill identifier 변경 시 CLAUDE.md / playbook / lane-entry 표 / agent prompt 등 전반 재명명 cascade)
- **Concept names**: "Deputy mandate 매트릭스" (capitalized 첫 글자 + 고착 용어로 architecturally established), "deputy-mandate skill"
- **File names**: `skills/deputy-mandate/` (skill 디렉토리 이름)
- **Code identifiers**: Bash/Python/YAML 안 `deputy` 가 변수명·키·label 일부인 경우 (rename = code change scope)

**경계 ambiguity 처리**: 둘 다 해석 가능한 경우 Class-B 측 분류 (safe direction — 식별자/개념 보존 우선, 의미 손실 방지).

### 결정 3 — forbid-list 아님 (ADR-064 카테고리 a 미등록)

본 표준화 = 용어 가이드라인 (terminology guidance), **NOT** wording-dictionary 카테고리 (a) forbid-list 등록. 근거:
- 사용자 directive "남발하지만 않으면 된다" = 과용 방지 수준 (lint warning 강제 아님)
- Class-B 보존 영역 다수 (식별자 / 개념명 / 코드 영역) → forbid-list 등록 시 lint false-positive 폭증
- 표준화 의도는 신규 작성 시 SubAgent 우선 사용 권장 + 기존 일반 명사 일괄 sweep 으로 충분

mechanical enforcement = Class-A sweep 의 1회성 적용 + 신규 작성 시 SubAgent 사용 자기 검열 (lint 미강제). 약화 = ADR-058 §결정 5 sunset_justification 의무 (현재 `is_transitional: false`).

### 결정 4 — Cross-plugin sibling sync (ADR-010 정합)

CFP-751 적용 영역:
- **wrapper repo `mclayer/plugin-codeforge`** — CLAUDE.md / docs/ / skills/ 안 deputy 일반 명사 sweep. Phase 2 PR carrier.
- **cross-plugin `mclayer/plugin-codeforge-design`** — codeforge-design plugin = "Deputy mandate 매트릭스" 의 진짜 SSOT 위치 (deputy 정의 원천). CLAUDE.md / agent files (LiveOpsDeputyAgent.md 등 Class-B 보존) / skill files / templates 안 deputy 일반 명사 sweep. **ADR-010 §sibling sync PR 의무** — wrapper PR merge 와 paired sibling repo PR.
- **기타 lane plugin** (codeforge-{requirements, develop, review, test, pmo}) = deputy 일반 명사 미사용 추정 (verify 의무). 사용 발견 시 sibling sync 확장.

### 결정 5 — Phase 1 (Story+ADR+Change Plan doc) + Phase 2 (sweep + sibling sync) 2-PR

- **Phase 1**: 본 ADR + CFP-751 Story §1-§7 + Change Plan (wrapper repo + internal-docs paired PR). 신규 ADR 도입이므로 doc-only fast-path 비적용 (ADR-054 정합) — 단 Phase 1 = doc-only commit (실 sweep 미수행).
- **Phase 2**: wrapper deputy sweep (Class-A 일반 명사 ≈335 line / 60 file → SubAgent 치환) + Class-B 보존 검증 + plugin.json bump (terminology change = PATCH per ADR-037? — 설계리뷰 lane 영역, 분류 검토). cross-plugin codeforge-design sibling PR pair (ADR-010 §결정 2 ordering). ADR-063 marketplace atomic = wrapper plugin.json bump 시 적용.

### 결정 6 — 표준화 시점 (forward + retroactive)

- **Forward (신규 작성)**: 본 ADR Accepted 후 새 doc / agent prompt / skill / PR 작성 시 "SubAgent" 사용 의무. 기존 "deputy" 사용 시 reviewer flag 권장 (mechanical lint 미강제).
- **Retroactive (sweep)**: Phase 2 sweep 으로 기존 Class-A occurrence 일괄 치환. Class-B 보존. 의미 보존 (역할 / 위계 / 책임 매트릭스 의미 0 변경).


## 해소 기준

N/A — permanent policy

## 결과

### 긍정 효과

- codeforge family 내 영어 jargon "deputy" 일반 명사 사용 정리 — 한국어 native 사용자 가독성 + 식별력 증가.
- SubAgent 라는 명확 canonical form 도입 — 새 contributor onboarding 명료성.
- Class-A/B 분류 규칙 정립 — 향후 재발 방지 (애매한 사용 시 반복 의문 제거).
- cross-plugin sibling sync 로 codeforge family 전체 표준 일관성.

### 부정 효과 / risk

- **Class-A/B 경계 ambiguity**: 일부 prose 표현 (예: "deputy mandate" 안 deputy 가 일반 명사 vs 고착 개념 시작 어휘) 판정 모호 — Class-B 측 분류 (safe direction) 로 완화.
- **cross-plugin propagation 지연**: codeforge-design plugin PR + wrapper PR sibling sync ordering 의무 (ADR-010 §결정 2). 미정합 시 일시 drift.
- **`codeforge:deputy-mandate` skill 이름 잔존**: Class-B 보존 결정 (skill rename cascade 비용 > 가치 평가). 사용자 directive "기존 Deputy 명명 Agent 명은 두고" 정합 — skill 도 동일 원칙 (codeforge:* skill 식별자 보존).

### Sunset criteria

N/A — permanent governance terminology policy. `is_transitional: false` (ADR-058 §결정 5 정합).

향후 약화 방향 amendment (예: Class-B 영역 축소 / forbid-list 등록 추가 / `SubAgent` canonical form 변경) = ADR-058 §결정 5 `sunset_justification` 의무 (top-down ratchet, ADR-064 §결정 7 정합).

## 관련 파일

- [`docs/wording-dictionary.md`](../wording-dictionary.md) — 카테고리 (b) entry 후보 검토 (SubAgent / deputy 등 inline 평문 정의 동반 의무)? — 설계리뷰 lane 결정 (본 ADR scope 내 미확정, Story §3 참조)
- [`skills/deputy-mandate/SKILL.md`](../../skills/deputy-mandate/SKILL.md) — Class-B 보존 (skill name 불변)
- [CLAUDE.md](../../CLAUDE.md) — Class-A sweep 대상 (다수 일반 명사 사용)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — Class-A sweep 대상
