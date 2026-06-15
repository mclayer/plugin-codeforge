---
adr_number: 123
title: 문서 가독성·커뮤니케이션 표준 — git 작성 + Confluence 미러 공통 규범
status: Accepted
category: Team & Process
date: 2026-06-16
carrier_story: CFP-2284
is_transitional: false
related_stories:
  - CFP-2284
related_adrs:
  - ADR-012 (확장 — wrapper CLAUDE.md SSOT 경계, "언어 정책"·"결정·대화 원칙"의 문서 작성 일반화)
  - ADR-079 (정합 — KST +09:00 ISO 8601 시각 표기 mandate, 본 표준 §구체 사실 항목이 인용)
  - ADR-064 (정합 — wording 표준 / decision-principle mandate, filler 금지 규칙 cross-ref)
  - ADR-100 (정합 — Confluence doc SSOT 인정, git=정본·Confluence=읽기 미러 단방향)
  - ADR-101 (정합 — verify-before-trust Confluence REST, 미러 무결성 layer)
  - ADR-103 (정합 — git→Confluence sync mechanism, 단방향 push·직접 편집 금지의 mechanism 원천)
  - ADR-111 (정합 — Confluence-mirror classification policy, 미러 대상 closed-enum)
  - ADR-119 (정합 — research-before-claims, 본 표준 §구체 사실 항목과 동축)
related_files:
  - docs/doc-readability-standard.md
  - CLAUDE.md
  - docs/wording-dictionary.md
---

# ADR-123: 문서 가독성·커뮤니케이션 표준

## 상태

Accepted (2026-06-16) — CFP-2284 carrier. ADR-012(wrapper CLAUDE.md SSOT 경계)의 "언어 정책"·"결정·대화 원칙"을 문서 작성 일반 규범으로 확장한다. 기존 정책을 축소하지 않으며(확장만), ADR-079(KST 시각 표기)·ADR-064(wording)·ADR-119(research-before-claims)·ADR-100/101/103/111(Confluence 미러)과 정합한다.

## 컨텍스트

사용자는 Confluence 문서 이관을 진행하며 "내부 전문용어와 구어체를 빼고, 격식 있는 문서체에 쉬운 말·구조·시각요소를 갖춰 작성하라"고 반복 지시했고, 이를 앞으로 모든 문서 작성에 적용되는 표준으로 git 에 고정(codify)하라고 요구했다.

이 표준이 메우는 공백은 두 가지다.

1. **분산된 단편 규칙** — CLAUDE.md "언어 정책"(한글 주 언어)과 "결정·대화 원칙"(표·개조식, 평문 풀이)은 존재하나 대상이 **사용자 대화** 위주이고, 에이전트가 git 에 쓰는 **문서 본문** 전반에 대한 통합 가독성 규범은 단일 SSOT 가 없었다.
2. **미러 렌더 규칙 부재** — git 문서를 Confluence 로 단방향 미러링할 때(ADR-100/103) 출처 표기·직접 편집 금지·시각요소 활용 같은 렌더 규범이 명문화되지 않았다.

본 표준의 적용 면은 두 곳이다.

| 적용 면 | 설명 |
|---|---|
| (A) git 작성 | codeforge 에이전트가 ADR·도메인 지식·가이드·아키텍처 등 사람이 읽는 문서를 git 에 쓸 때 |
| (B) Confluence 미러 | git 정본을 Confluence 로 단방향 미러링해 읽기용으로 렌더링할 때 |

용어 풀이(독자 대면 문맥 기준):

- **dogfood** — 플러그인 제작자가 자기 플러그인을 자기 개발에 직접 사용하는 것.
- **wrapper** — codeforge 모노레포의 최상위 패키지(루트). 8개 lane 플러그인을 묶는 상위 레이어.
- **미러(mirror)** — 원본(git)을 다른 시스템(Confluence)에 한 방향으로 복제해 보여주는 사본.

## 결정

### 결정 1 — 쉬운 말 우선

- 내부 식별자·전문용어(예: dogfood, wrapper, carrier story, lane, ratchet, sunset, fragment, referent, grep-gate)를 독자 대면 문맥에서 쓸 때는 **평문 1줄 풀이를 동반한다**.
- 약어·내부 코드명은 첫 등장 시 괄호로 풀이한다(예: SSOT(단일 원본)).
- 의미 없는 filler 단어("영역" 등)는 사용하지 않는다(ADR-064 / wording-dictionary 정합).

### 결정 2 — 격식 문서체

- 문어체("~한다 / ~이다 / ~된다")로 작성한다.
- 구어체("~한테 영향 있나", "빌려 쓰던", "빈 껍데기" 등)는 사용하지 않는다.

### 결정 3 — 구조

- 표준 섹션 순서를 권장한다: **개요 → 배경 → 결정(또는 핵심 내용) → 영향 → 관련**.
- 핵심을 문서 앞에 배치한다(결론 우선).
- 표·개조식을 우선하고, 긴 평서문 덩어리를 피한다.

### 결정 4 — 한글 주 언어

- 한글을 주 언어로 한다(CLAUDE.md "언어 정책" 정합).
- 한자(일·중 포함)는 사용하지 않는다.
- 영어는 기술용어·고유명사·코드에 한정한다.

### 결정 5 — 구체 사실

- 버전·수치·날짜는 구체적으로 명시한다(추상 레이블 금지).
- 사실 단정 전 검증을 선행한다(ADR-119 research-before-claims 정합).
- 시각 표기는 KST `+09:00` ISO 8601 형식을 사용한다(ADR-079 정합). 외부 timestamp(GitHub / git)는 원본을 보존한다.

### 결정 6 — 시각요소 적극 활용

- 가능한 곳에 상태 뱃지·색 패널(info / note / warning / success / error)·2~3단 비교·정렬표·접기를 사용한다.
- 흐름도(다이어그램)는 현재 자동 렌더 제약(외부 이미지 차단 + 앱 매크로 API 삽입 불가)으로 **필요한 소수 페이지에만 수동 삽입**하며, 자동 파이프라인 대상에서 제외한다.

### 결정 7 — Confluence 렌더 한정 규칙

(B) Confluence 미러에만 적용한다.

- 페이지 상단에 출처(원문 git 경로)와 "정본 = git, 단방향 미러, 직접 편집 금지" 표기를 둔다(ADR-100 / ADR-103 정합).
- 밀도 높은 거버넌스 세부는 접기 처리한다.
- 미러 대상은 사람이 읽는 문서(ADR·도메인 지식·계약·가이드·아키텍처)로 한정한다(ADR-111 closed-enum 정합).

## 근거

- **분산 규칙 통합**: CLAUDE.md 의 대화 위주 규범을 문서 본문 전반으로 확장해 단일 SSOT 를 둔다. 기존 정책을 축소하지 않고 확장만 한다(ADR-012 경계 보존).
- **이관 일관성**: Confluence 이관 시 페이지마다 출처·편집 금지·시각요소 규칙이 달라지는 불일치를 차단한다.
- **자동/수동 분리**: 다이어그램은 현 렌더 제약상 자동화 대상에서 제외하되 표준에서 배제하지 않고 "수동 소수 페이지" 경로로 보존해 정보 손실 0 을 유지한다.
- **기성 표준 재사용**: 시각 표기는 ADR-079, wording 금지는 ADR-064, 사실 검증은 ADR-119 를 인용해 중복 규범을 만들지 않는다.

## 결과

- 실무 체크리스트와 Confluence 렌더 규칙의 빠른 참조 SSOT = `docs/doc-readability-standard.md`(본 ADR 을 SSOT 로 cross-ref).
- 에이전트가 사람이 읽는 문서를 git 에 쓸 때, 그리고 그 문서를 Confluence 로 미러링할 때 본 7 결정을 준수한다.
- 기존 문서의 일괄 소급 개정은 본 ADR 의 강제 대상이 아니다(신규·개정 작성분부터 적용, 점진 정합).
- mechanical_enforcement_actions: [] — Wave 1 declarative-only. 가독성 규범은 대부분 behavioral(리뷰 판단)이며, 일부(filler 금지·KST 시각 표기·한자 금지)는 기존 lint(wording-dictionary / KST mandate)가 이미 부분 커버한다. 재발 패턴 누적 시 후속 CFP 가 mechanical lint 승격을 평가한다(ADR-084 precedent).

## sunset_justification (ADR-058 §결정 5 — 약화 차단)

본 표준은 기존 정책의 확장이며 약화 0 건이다. CLAUDE.md "언어 정책"·"결정·대화 원칙"은 무손상 존속하고, 본 ADR 은 그 적용 범위를 문서 본문·미러 렌더로 넓힌다. is_transitional: false (permanent governance anchor).

## 관련 파일

- `docs/doc-readability-standard.md` — 빠른 참조 체크리스트 + Confluence 렌더 규칙(본 ADR 을 SSOT 로 참조).
- `CLAUDE.md` — "언어 정책" / "결정·대화 원칙" / "시각 표기"(본 ADR 이 확장하는 상위 정책).
- `docs/wording-dictionary.md` — filler 금지 등 wording lint SSOT(결정 1 cross-ref).
