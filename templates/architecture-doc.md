---
title: <대상 영역 한 줄 — 예: codeforge family 전체 구조>
last_captured: <YYYY-MM-DD>   # KST 일자 의미 (ADR-079 display layer 정합) — 마지막 구조 캡처 시점
kind: architecture_doc
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

> **시각 diagram 허용 (CFP-951)**: 위 4 H2 안에 `mermaid` / `plantuml` fenced code block embed 허용. 4 H2 closed-enum invariant + anti-scope guard 4종("코드 mirror") 보존 (diagram = abstraction layer, 코드 line mirror 아님). fenced code block 은 architecture-drift lint(CFP-923 detection class d) 의 exempt 영역이므로 별도 governance 변경 없이 사용 가능.

<!--
  architecture_doc = docs/architecture/ 경로 하 영속 markdown SSOT.
  Story key 독립 (고정 경로) + 누적 *현재 상태* 영역 only (델타 X — 델타는 change_plan SSOT).
  ADR-078 §결정 1 closed-enum: 정확히 아래 4 H2 heading 만. heading 문자열 변경 금지
  (S4 #923 drift lint 가 grep 할 고정 문자열 — EC-1 정합).
-->

## 모듈

<!-- plugin / package / module-level structural unit. 라인 수준 금지 (anti-scope guard 참조). -->
<!-- placeholder 가이드: 구성 단위(plugin/package/module)와 각 단위의 책임 1줄 요약을 채운다.
     클래스 list / 함수 enumeration / 변수 목록 / import graph 금지 — 모듈 단위 책임 서술만. -->

<여기에 모듈 구조를 채운다>

## 경계

<!-- plugin 간 boundary + scope partition + responsibility partition. -->
<!-- placeholder 가이드: 모듈/plugin 간 책임 경계 + write boundary + scope 분할 정책을 채운다.
     함수 signature / parameter list 금지 — 경계 정책 서술만. -->

<여기에 경계 구조를 채운다>

## 인터페이스 계약

<!-- inter-plugin contract surface (kind:contract = contract schema 영역 / kind:registry = lookup/표 영역, MANIFEST.yaml SSOT cross-ref). -->
<!-- placeholder 가이드: 모듈 간 계약 surface 를 SSOT cross-ref 로 채운다 (MANIFEST.yaml 등 참조).
     계약 schema 의 field-level / type-level 상세 금지 — contract 이름 + SSOT pointer 만. -->

<여기에 인터페이스 계약을 채운다>

## 데이터 흐름

<!-- input → transform → output dataflow (lane spawn / event / artifact propagation level). -->
<!-- placeholder 가이드: 입력 → 변환 → 출력 흐름을 lane/event/artifact propagation 수준으로 채운다.
     함수 호출 trace / 변수 전달 라인 금지 — 흐름 단계 서술만. -->

<여기에 데이터 흐름을 채운다>

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `src/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
