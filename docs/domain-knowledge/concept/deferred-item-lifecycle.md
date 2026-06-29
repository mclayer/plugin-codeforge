---
kind: concept_definition
type: domain-knowledge
slug: deferred-item-lifecycle
title: Deferred item lifecycle (narrative deferred → tracking-externalized | observe-only, no-silent-drop)
status: Active
updated: 2026-06-29
carrier_story: CFP-2470
related_adrs:
  - ADR-119  # research-before-claims §결정 9 발견≠필요 3문 게이트 — 본 lifecycle 의 filter 단계 근거
  - ADR-045  # retro mandatory + §D-11 batch closure 4-option enum (CLOSE_AS_OBVIATED/SENTINEL/PROMOTE/DEFER) — structured DEFER row 재사용
  - ADR-128  # 완료 단계 정식화 (phase:완료 worktree-clean self-check) — warning-tier + workflow:null + behavioral precondition 구조 동형 archetype
  - ADR-127  # 정식 풀 플로우 비협상 / skip-offer 금지 — narrative deferred 의 silent drop 금지 정신 정합
related_files:
  - plugins/codeforge-pmo/templates/retro.md          # retro §4 try / §8 개선 제안 — narrative deferred 의 발생지
  - .github/workflows/retro-mandatory.yml             # cross-repo Contents API + PAT graceful skip 패턴 SSOT (L195-205, 287-295)
  - docs/evidence-checks-registry.yaml                # warning-tier + workflow:null entry 등록처 (worktree-clean-completion-gate L2796 archetype)
  - hooks/skip-offer-reminder.py                       # consumer 전파 채널 (UserPromptSubmit hook) 선례 — CFP-2456
related_concepts:
  - policy-propagation-channel        # consumer 도달 채널 (hooks.json UserPromptSubmit) — 자매 concept
tags:
  - codeforge
  - governance
  - deferred-followup
  - retro
  - no-silent-drop
sources:
  - https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-119-research-before-claims.md  # 발견≠필요 3문 게이트
  - https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-045-story-retro-mandatory-trigger.md  # §D-11 batch closure 4-option enum
---

## 정의

**Deferred item lifecycle** = codeforge 의 retro·Story 서사(narrative)에 "한계·미해결·다음에 할 일"로 기록된 deferred 항목이 **완료 시점(phase:완료)에 silent 하게 사라지지 않도록** 강제하는 상태 모델. 핵심 명제는 "deferred 전부를 추적 Issue 로 강제 전환"이 **아니라** — 각 deferred 항목이 완료 시점에 둘 중 하나로 **명시 판정**되게 강제하는 것이다:

1. **tracking-externalized** — 추적 Issue 로 전환 (3문 게이트 통과 actionable).
2. **observe-only + 사유 명시** — 추적하지 않되 "왜 추적 안 하는가" 사유 기록 (3문 게이트 미통과 = 관찰만).

silent drop (둘 중 어느 것도 아닌 채로 서사에만 남고 누락) **만** 차단한다.

## 컨텍스트

mctrader(첫 비-dogfood consumer) 데뷔 감사에서 드러난 갭: retro 가 한계·미해결을 정직히 기록(검출 OK)하나, 그 항목이 추적 Issue 전환·회수 매커니즘 부재로 "deferred = narrative만" 누적. "발견했으나 조치 매커니즘 부재" = leak. CFP-2470/W2 가 이 leak 을 막는 **no-silent-drop 게이트**의 도메인 모델 carrier.

## 핵심 규칙

### 4-state 모델

```
discovered            → 작업 중 한계·미해결·후속 후보를 발견 (아직 미기록)
  ↓ (retro/Story 서사 기록)
narrative-recorded    → retro §4 try / §8 개선 제안 / Story 서사에 텍스트로 기록됨
  ↓ (완료 시점 판정 — 본 게이트가 강제)
  ├─ tracking-externalized  → 추적 Issue 전환 (3문 게이트 통과 actionable)
  │     ↓
  │   resolved | deferred(Issue 안에서 재-deferred, ADR-045 §D-11 DEFER row)
  └─ observe-only           → 추적 안 함 + 사유 명시 ("관찰됨·미조치" + 사유 1줄)

금지 전이: narrative-recorded → (판정 없이 소멸)   ← 이것이 silent drop, 본 게이트가 차단
```

### 필터 vs 회수 — 발견≠필요(filter) ↔ 발견≠조치(recover) 순차직렬

본 lifecycle 은 ADR-119 §결정 9 와 **충돌이 아니라 순차직렬**이다:

- **ADR-119 §결정 9 (발견≠필요, filter)**: 작업 제안·follow-up 발의 *전* 3문 게이트(① 깨졌나·강제요인 ② 이득>비용·리스크 ③ 관찰자 없어도 할 일)로 noise 를 **억제**. 셋 다 YES 아니면 발의 금지("관찰됨·미조치" 1줄만).
- **본 lifecycle (발견≠조치, recover)**: 이미 retro 서사에 **기록된** deferred (= 필요성 필터를 거쳐 narrative-recorded 단계에 도달한 것)가 완료 시점에 silent 하게 누락되는 leak 을 **억제**.

순서: discovered → (ADR-119 filter) → narrative-recorded → (본 게이트 recover 판정). 즉 filter 가 먼저 noise 를 깎고, 그 통과분(서사에 남은 것)에만 recover 게이트가 작동한다. "관찰됨·미조치"로 정당하게 처리된 항목도 observe-only state 로 명시 판정되면 게이트 통과 — 3문 게이트 미통과가 곧 silent drop 이 아니다 (사유 명시가 판정).

### theater 방지 — dual-source AND

판정의 진정성은 **dual-source AND** 로 검증한다: (선언된 DEFER/tracking row) ∧ (실제 tracking Issue 존재 OR 사유 텍스트 존재). 선언만 있고 실 backing 이 없으면 theater (연극 게이트). structured row (ADR-045 §D-11 batch-closure enum 4-value 재사용) 를 anchor 로 써 자유텍스트 파싱을 회피한다.

## 경계

### CFP-2380 (evidence-checks-registry reconciliation) 과의 disjoint

| 축 | CFP-2380 (carrier 게이트) | 본 lifecycle (CFP-2470/W2, 서사 게이트) |
|---|---|---|
| 검사 모집단 | `docs/evidence-checks-registry.yaml` 의 status:deferred-followup **carrier entry** (lint/workflow 파일 실존) | retro/Story **markdown 서사** deferred 항목 (텍스트) |
| 검출 신호 | `count ≥ threshold ∧ 전용 carrier 부재` (registry 필드 스캔) | narrative-recorded 항목의 완료-시점 판정 부재 (서사 누락) |
| 메커니즘 | reconciliation 게이트 → 배선/근거강등/폐기 택일 | no-silent-drop 게이트 → tracking-externalized / observe-only 택일 |
| 흡수 관계 | **disjoint** — 모집단·신호·메커니즘 완전 분리. 이름("deferred-followup") 충돌만 존재 | 신규 축. CFP-2380 entry 가 본 게이트 대상 아님, 역도 성립 |

이름 충돌만 존재하므로 carrier Story 의 §3 에서 명시적으로 분리 선언 의무.

### #2390 항목1 (retro-fact-verify cross-repo) 과의 disjoint

#2390 항목1 = retro 서사의 **사실 claim 을 cross-repo 로 verify** 하는 축. 본 lifecycle = retro 서사의 **deferred 항목 판정 누락** 을 막는 축. cross-repo Contents API 인프라(retro-mandatory.yml 패턴)만 공유하고 검사 대상은 disjoint — 흡수 불가.

## 관련 ADR

- **ADR-119** §결정 9 — 발견≠필요 3문 게이트. 본 lifecycle 의 filter 단계 근거 (recover 와 순차직렬).
- **ADR-045** §D-11 — retro batch closure 4-option enum (CLOSE_AS_OBVIATED / CLOSE_AS_SENTINEL / PROMOTE / DEFER). structured DEFER row schema 재사용 source.
- **ADR-128** — 완료 단계 정식화 (phase:완료 worktree-clean self-check). warning-tier + workflow:null + behavioral precondition 3-조합 archetype — 본 게이트가 동형 구조로 land.
- **ADR-127** §결정 4 — 정식 풀 플로우 비협상 / skip-offer 금지. narrative deferred 의 silent drop 금지 정신 정합.

## 변경 이력

- 2026-06-29 (CFP-2470/W2): 신규 작성. mctrader 데뷔 감사 "deferred follow-up 회수 실패" 갭 carrier. 4-state 모델 + ADR-119 filter↔recover 순차직렬 + CFP-2380/#2390 disjoint 명시.
