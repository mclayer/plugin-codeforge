---
adr_number: "005"
title: "ADR-005: Plugin Self-Application N/A 표준화"
status: Accepted
category: Team & Process
date: "2026-04-27"
related_files:
  - "docs/stories/CFP-1.md"
  - "docs/stories/CFP-2.md"
  - "docs/stories/CFP-13.md"
  - "docs/stories/CFP-14.md"
  - "docs/stories/CFP-15.md"
  - "docs/stories/CFP-16.md"
  - "docs/stories/CFP-17.md"
  - "templates/story-page-structure.md"
  - "templates/change-plan.md"
  - "CLAUDE.md"
  - "agents/PMOAgent.md"
is_transitional: false
---

## 상태

Accepted (2026-04-27) — 결정 1·2·3 CFP-18 Phase 2 완료 시 확정.
결정 4 (invariant-check workflow N/A prefix detect step)는 후속 CFP 분리.

## 컨텍스트

CFP-1 (Plugin Self-Application 정책 도입) 이후 v0.11.0까지 plugin 자체를 변경하는 Story들이 누적됐다. 이들의 공통 특성:

- 실행 가능 코드 0줄 (agent md / template / docs / workflow yaml만 수정)
- 외부 입력·인증·민감데이터 흐름 변경 0건
- 단위/통합/성능 테스트 inert (테스트할 runtime behavior 부재)
- 1차 보안 layer (Dependabot/CodeQL/Secret Scanning) 영향 부재 또는 자동 통과

7-lane 흐름 자체는 Plugin meta change Story도 통과해야 하지만, 다수 lane이 자연스럽게 N/A가 됨. 각 Story 작성자가 N/A 표기 방식을 즉석에서 결정해 표현이 비일관:

- CFP-2: §5.5 사용자 확인 항목을 "[✓] ... 본 세션에서 확인 완료" 형식
- CFP-13~16: §9 "구현 테스트 = invariant-check workflow 자동 검증" 형식
- CFP-17: §7 보안 설계를 "N/A — agent md / template / docs 변경. 외부 입력·인증·민감데이터 흐름 변경 0개. trust boundary 변경 없음" + 괄호로 사유 패턴 시연
- CFP-1·14·15: §10 FIX Ledger를 "비어있음 — FIX 루프 미발생" 자유 텍스트

이 7건이 같은 추론 ("plugin meta는 X lane이 N/A인 이유 = Y")을 매번 재발명. 일반 consumer가 plugin meta change 시도할 때 같은 추론 비용 반복.

## 결정

### 결정 1 — N/A 표준 표기 형식

Plugin meta change Story (또는 lane이 자연스럽게 N/A인 일반 Story)의 §X 본문에 다음 1-line 또는 multi-line 표기 사용:

**1-line (lane 전체 N/A)**:
```
N/A — <사유 한 줄>. (Plugin self-application 패턴 / 또는 도메인 사유)
```

**multi-line (부분 N/A 또는 audit trail 강조)**:
```
N/A — <사유 한 줄>.
- 검증 채널: <대체 검증 — 예: invariant-check workflow / consumer overlay 시뮬레이션 / 1차 보안 layer 자동 통과>
- 면제 분류: <plugin-meta-na | runtime-inert | external-dep-none>
```

### 결정 2 — 면제 분류 (3종)

- `plugin-meta-na`: agent md / template / docs / yaml만 수정, 실행 가능 코드 0줄
- `runtime-inert`: 코드는 있으나 외부 입력·인증·민감데이터 흐름 무관 (예: build script 정합성 fix)
- `external-dep-none`: 외부 라이브러리·표준 의존 없음 (Researcher §6 N/A 사유)

### 결정 3 — Story §11 회고에 N/A lane 명시 의무

Story가 lane을 N/A 처리한 경우 §11 회고에 "이번 Story는 lane {X·Y·Z}를 N/A 처리. 다음 Story 작성자는 같은 lane 무자동 N/A 가정 금지 — 매 Story 분류 재실시" 1줄 명시. **N/A의 자동 inheritance 차단**.

### 결정 4 — invariant-check workflow가 §X "N/A — " prefix를 detect

`invariant-check.yml` 신규 Step 추가: Story file의 §X (X ∈ {7,8,9}) 본문이 빈 placeholder인지 vs `N/A — <사유>` 형식인지 검사. 빈 placeholder 또는 사유 없는 N/A는 reject.

(이 결정 4는 후속 Story로 분리 — 본 ADR은 결정 1·2·3 `Accepted` 상태로 정책 명문화, Step 신설은 follow-up Story. 결정 4 invariant-check Step 신설은 후속 CFP에서 `Accepted`로 전환)

## 결과

### 긍정적

- 일관된 N/A 표기로 audit trail 강화
- 일반 consumer가 plugin meta change 흉내 낼 때 reference 가능한 표준
- N/A inheritance 차단으로 lane skip의 silent 누적 방지
- 결정 4 후속 Story가 본 sprint의 **"invariant ratchet 패턴"** 7번째 적용

### 부정적

- 작성 부담 미세 증가 (§X 본문 1-3줄 추가)
- 면제 분류 enum이 plugin meta change 외 일반 Story에는 적용 모호 (per-lane decision tree 필요할 수 있음)

### Trade-off

본 ADR은 **Proposed** 상태로 우선 발행. 결정 4 (invariant-check Step 신설)는 1-2 Story 누적 후 패턴이 충분히 안정화되면 follow-up CFP로 정식 implement. PMOAgent.md §4 ADR 후보 발의 절차를 따름.

## 해소 기준

N/A — permanent policy



(N/A — 정책 ADR이라 다이어그램 불필요)

## 관련 파일

- `docs/stories/CFP-1.md` ~ `CFP-17.md` (사례 7건)
- `templates/story-page-structure.md` (Story §X placeholder 형식 SSOT)
- `templates/change-plan.md` (§7 보안 설계 N/A 사유 슬롯)
- `CLAUDE.md` "Plugin 자체 적용 (dogfooding)" 섹션 — 본 ADR과 cross-link
- `agents/PMOAgent.md` §4 ADR 후보 발의 절차

---

**발의자**: PMOAgent (Cross-cutting), v0.11.0 sprint close retro 직후 (2026-04-27)
**Status**: Accepted (2026-04-27) — 결정 1·2·3 확정. 결정 4 후속 CFP 분리.
