---
kind: concept_definition
type: domain-knowledge
slug: instruction-data-language-partition
title: Instruction-data language partition — 지시문 언어 통일 + 데이터 원어 verbatim 보존 + delimited untrusted block 결합 + 상향 보고 병기(additive) 원칙
status: Active
updated: 2026-08-03
carrier_story: CFP-2884
related_adrs:
  - ADR-119  # research-before-claims — "영어 프롬프트 성능" 주장의 출처 검증 규율
  - ADR-081  # Codex dispatch — 본 partition 의 적용 지점
related_files:
  - docs/domain-knowledge/concept/text-encoding-layer-model.md  # 짝 개념 (축 A)
  - docs/domain-knowledge/concept/ubiquitous-language.md  # 프로젝트 확정 한글 표기 SSOT 계보
  - docs/domain-knowledge/concept/additive-merge-pattern.md  # additive > destructive 동형 원리
tags:
  - prompt-language
  - instruction-data-separation
  - spotlighting
  - delimited-untrusted-block
  - bilingual-side-by-side
  - translation-fidelity
---

# Instruction-data language partition (지시문-데이터 언어 구획)

## 정의

`instruction-data language partition` = **LLM 워커 dispatch 프롬프트를 3 구획으로 나누고 구획별 언어 정책을 달리하는 패턴**: (A) 지시문 = 단일 언어(영어) 강제, (B) 인용 데이터 = 원어 verbatim 보존 + delimited untrusted block 격리(번역 금지), (C) 상향 보고 = 원문 verbatim + 요약 번역 **병기** (교체 금지).

## 컨텍스트

본 개념은 CFP-2884 요구사항 lane 탐구 산출이다 (변경 이력 참조). 인코딩 방어 계층(축 A)을 다루는 짝 개념 `text-encoding-layer-model` 과 짝을 이루며, 본 문서는 언어 정책 구획을 담당한다 (경계 절 참조).

## 핵심 규칙

구획별 언어 정책(정의 절의 A/B/C 3 구획)이 본 개념의 핵심 규칙이며, 그 타당성은 아래 외부 근거 3축이 지지한다.

### 외부 근거 3축

#### 축 1 — 지시문·데이터 분리는 확립된 관행 (구획 A/B 구조)

Microsoft **Spotlighting** (Hines et al. 2024, arXiv:2403.14720): 지시문과 비신뢰 데이터의 경계를 delimiting / datamarking / encoding 3 방식으로 명시 — GPT 계열에서 indirect prompt injection 성공률 >50% → <2%. delimited untrusted block 안 내용은 "지시가 아니라 데이터"로 취급 = **번역·재해석 없이 원형 보존이 전제**. 언어 분리와의 결합을 명명한 선행사례는 미발견이나, "데이터 구획 원형 보존" 원칙에서 "원어 보존"은 직접 도출된다 (결합 자체는 본 프로젝트의 합성 — 출처 없음 정직 표시).

#### 축 2 — "영어 지시문 성능" 주장은 출처 실재, 단 효과 크기는 조건부

| 방향 | 근거 | 출처 품질 |
|---|---|---|
| 지지 | Etxaniz et al., "Do Multilingual Language Models Think Better in English?" (NAACL 2024) — self-translate 가 비영어 직접 추론을 일관 상회 | 1차 연구 (단 구세대 오픈 모델 대상) |
| 지지 | Shi et al., MGSM (ICLR 2023) — EN-CoT/translate-EN 전략 유효 | 1차 연구 |
| 지지 | OpenAI Help Center — "models are optimized for English" | 벤더 문서 |
| 조건부 | Anthropic Multilingual support 문서 — 한국어 = 영어 대비 96.6~96.7% (translated-MMLU, 격차 ~3.3%p 소폭) | 벤더 문서 (task 언어 측정, 지시문 언어 단독 아님) |
| 조건부 | Mondshine et al., "Beyond English" (NAACL 2025 Findings) — pre-translation 이득은 언어 자원·영어 유사도·번역 품질 의존, 선택적 적용 권고 | 1차 연구 |
| 반례 | CulturALL 벤치마크 — 문화 맥락 task 는 영어 프롬프트가 원어 대비 8.08%p **하락** | 1차 연구 |

**정직 결론**: 고자원 언어(한국어) + 문화 맥락 무관 기술 task(코드 리뷰)에서는 "영어 지시문 소폭 유리 또는 동등" — 성능은 **2차 보강 논거**이며, 1차 논거는 인코딩 구조 불변(ASCII 면역, 짝 개념 참조)이다. "영어가 무조건 좋다"는 over-claim.

#### 축 3 — 병기(additive) > 교체: 번역 검증 가능성 원칙 (구획 C)

법률 공인번역 관행: 번역본은 **원본 첨부 시에만** 법적 효력 — 판정자가 번역을 원문 대조 검증할 수 있어야 한다 (bilingual side-by-side 제출이 표준 관행). 번역만 상향하면 번역 오류가 **검증 불가능한 단일 장애점**이 된다. 원문 verbatim + 요약 번역 병기 = 검증 가능성 보존 + 하류 소비성 확보 양립. 프로젝트 내부 동형: fact-check marker verbatim 보존 규율, additive-merge pattern (additive > destructive).

## 경계

- 구획 A 의 "프로젝트 확정 한글 표기"(예: 고유 codename)는 예외 허용 — SSOT = `docs/wording-dictionary.md`/`docs/glossary.md` 계보.
- 구획 B 번역 금지는 dispatch 방향(하향) — 상향 보고의 요약 번역(구획 C)과 disjoint.
- 본 개념 = 언어 정책 구획. 인코딩 방어 계층 = 짝 개념 `text-encoding-layer-model` 소관.

## 관련 ADR

- **ADR-119 (research-before-claims)** — "영어 프롬프트 성능" 주장의 출처 검증 규율.
- **ADR-081 (Codex dispatch)** — 본 partition 의 적용 지점.

## 변경 이력

| 일자 | 변경 | carrier |
|---|---|---|
| 2026-08-03 | 신규 작성 — CFP-2884 요구사항 lane 탐구 산출 | CFP-2884 |
| 2026-08-04 | 헤딩 구조 재배치 — concept doc-section-schema 필수 헤딩(컨텍스트·핵심 규칙·관련 ADR) 정합. 내용 무손실 (외부 근거 3축을 핵심 규칙 하위로 강등: `###`→`####` + 컨텍스트는 문서 내 기존 사실 재기술 + frontmatter 인용 ADR 2건 목록화) | CFP-2884 |
