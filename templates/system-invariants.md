---
title: <대상 시스템 한 줄 — 예: mctrader-data collector standing invariant-surface>
last_captured: <YYYY-MM-DD>   # KST 일자 의미 (ADR-079 display layer 정합) — 마지막 surface 갱신 시점
kind: system_invariants
---

<!--
  목적 (ADR-068 I-8 — Amendment 6 / CFP-2351):
  시스템의 long-lived mutable structure (프로세스 수명 동안 상태를 누적·유지하는 구조 —
  in-process WAL / 버퍼 / 큐 / 캐시 / 카운터 / ledger 등) 의 bound / lifetime / ordering invariant 를
  상시 색인하는 standing 문서. runtime-failure 진단의 falsifier (ADR-119 §결정 10 ② generative invariant sweep —
  "실패 경로의 long-lived mutable 구조 열거 + bound/lifetime/ordering invariant 명시 + 코드 보존 여부 실측") 가
  본 surface 를 cross-ref 해 invariant sweep 의 enumeration 완전성 (구조 누락 0) 을 보강한다.

  유지 의무 (ADR-068 I-8):
  - impl PR 이 새 long-lived mutable structure 를 추가 (또는 기존 구조의 bound/lifetime/ordering invariant 를 변경) 하면
    그 PR 이 본 표의 row 를 append (또는 갱신) 할 의무. 색인 부재/미갱신 = I-8 위반.
  - 진단 시 이 표를 재도출하지 말고 먼저 읽는다 (상시 구조적 속성은 코드를 바꾸지 않는 한 불변).

  cross-ref:
  - ADR-068 I-8 (standing invariant-surface invariant) = 본 문서 정의 SSOT
  - ADR-119 §결정 10 ② (진단면 generative invariant sweep) = 본 surface 의 사용처 (falsifier 입력)
  - ADR-015 Amendment 1 §결정 1 (accumulation/lifetime-class soak) = accumulation/lifetime-class flag 의 테스트 측 정보원
  - ADR-014 Amendment 7 §7.4.7 outcome-signal ③ (발현조건 임계) = accumulation/lifetime-class flag 의 운영 AC 측 정보원
  - consumer-guide §7.x (standing invariant-surface 유지 조항) — Phase 2 consumer-guide 본문 cross-ref 예정

  적용 경계:
  - short-lived (단일 요청/트랜잭션 수명, 프로세스 수명 누적 0) 구조 = scope 외 (long-lived 아님).
  - immutable (불변) 구조 = scope 외 (mutable 아님).
  - wrapper-self (codeforge dogfood) = runtime 0 (governance Story, in-process long-lived structure 부재) → 면제 (ADR-005 plugin-meta-na).
    본 template 은 consumer 가 자기 시스템에 두는 standing surface 용.
-->

# 시스템 standing invariant-surface

> long-lived mutable structure 의 bound / lifetime / ordering invariant 색인. ADR-068 I-8 SSOT.
> impl PR 이 새 구조 추가 시 본 표 확장 의무. runtime-failure 진단 falsifier (ADR-119 §결정 10 ②) 의 cross-ref surface.

## bound / lifetime 구분 (작성 시 필수)

- **bound = backlog cap** — 처리 대기 큐의 순간 상한 (소비되면 줄어듦). backlog 초과 = 처리 지연 신호.
- **bound = lifetime cap** — 프로세스 수명 동안 누적되는 총량의 상한 (소비/회수 없이 monotone 증가). lifetime cap 미설정 = 무한 누적 = OOM/고갈 위험.
- **혼동 주의**: monotone 누적 구조를 backlog cap 으로 오인하면 "회수되니 괜찮다" 는 거짓 안심이 된다 (incident 의 근본 패턴). 누적·미회수 구조는 반드시 `accumulation/lifetime-class? = Y`.

## 표

| 구조명 | 위치(file) | 종류 | bound invariant | lifetime invariant (회수 여부) | ordering invariant | 코드 보존 지점 | accumulation/lifetime-class? |
|---|---|---|---|---|---|---|---|
| `<예시>` WAL accumulator | `src/<...>/wal.py` | WAL | flush 전 누적 상한 = **backlog cap 이어야** 하나 현재 monotone lifetime cap (위반 — flush 후 회수 미수행) `[empirical-source: <wiretap ref> \| TBD]` | **미회수 (monotone)** — flush 후에도 누적 buffer 해제 안 됨 → 무한 성장 | shard 순서 보존 (watermark = 마지막 flush offset) | `wal.py:append()` 가 cap 검사 없이 누적 (위반 지점) / `wal.py:flush()` 가 buffer.clear() 미호출 | **Y** (accumulation-class — capacity 회계가 backlog 이 아닌 lifetime monotone) |
| `<구조명>` | `<file>` | buffer / queue / cache / counter / ledger / WAL | `<상한값 + backlog vs lifetime 명시>` `[empirical-source: <ref> \| TBD]` | `<회수됨 / 미회수(monotone)>` | `<순서 보장 / watermark 정의 / N/A>` | `<invariant enforce 또는 위반 file:line>` | `<Y / N>` |

<!--
  작성 가이드:
  - 한 row = 하나의 long-lived mutable structure. 7-key (구조명+위치 / 종류 / bound / lifetime / ordering / 코드 보존 지점 / accumulation flag) 전부 채운다.
  - bound 의 수치는 I-5 dimensional empirical 정합 — 모든 정량 parameter 에 `[empirical-source: <ref> | TBD]` annotation (추정값 lock-in 금지).
  - accumulation/lifetime-class? = Y 인 구조는 ADR-015 soak 지속 시간 도출 + ADR-014 §7.4.7 발현조건 임계 선언의 정보원이 된다 (단일 출처화).
  - 위반(invariant 가 코드에서 보존되지 않음) 도 명시한다 — 위반 row 가 곧 진단 falsifier 의 1순위 후보.
  - ordering 이 무관한 구조 (순서 비의존 cache 등) 는 `N/A` 명시.
-->

## 진단 사용법 (ADR-119 §결정 10 ②)

runtime-failure 진단 시:
1. 실패 경로에 관여하는 long-lived mutable structure 를 본 표에서 **열거** (재도출 금지 — 이미 색인됨).
2. 각 구조의 bound / lifetime / ordering invariant 가 **코드에서 실제 보존되는지 실측** (코드 보존 지점 file:line direct Read).
3. 위반 invariant 1개 (file:line 으로 짚힘) > "확인함 OK" N개 (비대칭 규칙 — ADR-119 §결정 10 ②).
4. 표에 없는 구조를 새로 발견하면 진단 종료 후 본 표에 row append (surface 확장 — 다음 진단의 enumeration 완전성 보강).
