---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: knowledge-capture-and-memory-governance
title: 지식 캡처 + 메모리 거버넌스 원리 — 휘발성 운영지식 영속화의 두 면 (capture / slimming)
status: Active
tags:
  - knowledge-capture
  - memory-governance
  - completion-self-check
  - warning-tier
  - char-budget
  - semantic-vs-mechanical
related_adrs:
  - ADR-129  # 본 페이지의 정책 SSOT (지식 캡처 + 메모리 거버넌스)
  - ADR-045  # PMOAgent retro batch closure (지식 보존 인접)
  - ADR-071  # MEMORY.md cap + 슬림화 normative (§18.2-18.7)
  - ADR-051  # (지식/노트 거버넌스 인접)
  - ADR-119  # 제안 필요성 3문 게이트 (capture 3문 게이트 동형 cross-ref)
related_stories:
  - CFP-2392
created: 2026-06-24
updated: 2026-06-24
---

# 지식 캡처 + 메모리 거버넌스 원리 (CFP-2392 / ADR-129)

## 정의

**지식 캡처 + 메모리 거버넌스 (knowledge-capture-and-memory-governance)** 는 codeforge self-governance 의 "학습/지식 보존" 축이다. 휘발성 운영지식(작업 중 디버깅·설계·운영 노력으로 발견한 것)을 디스크에 영속화하는 거버넌스로, **두 면**으로 이루어진다:

| 면 | 질문 | mechanism |
|---|---|---|
| **capture (들어오는 흐름)** | "이번 작업에서 재사용 가능한 지식이 나왔는가 — 외부화했는가?" | 완료시점 capture 게이트 (ADR-129 §결정 1) |
| **slimming (쌓인 것의 관리)** | "축적된 MEMORY.md 가 용량을 넘었는가 — 무손실로 슬림화했는가?" | MEMORY.md 용량관리 규약 (ADR-129 §결정 2) |

두 면은 한 skill(`knowledge-capture-gate`) + 한 ADR umbrella 로 묶이되, 두 개의 독립 게이트로 운영된다.

본 note 는 *원리* 를 기록한다. 정책 SSOT = [ADR-129](../../../../archive/adr/ADR-129-omc-knowledge-capture-memory-governance.md), 절차 SSOT = `codeforge:knowledge-capture-gate` skill (절차는 skill, 결정은 ADR — ADR-120 §결정 3 split).

## 컨텍스트

본 원리는 codeforge self-governance 의 지식 보존 축으로, 한 도메인 문제의 두 면(capture / slimming)을 단일 ADR umbrella 와 단일 skill 로 묶되 두 독립 게이트로 분리 운영하는 설계 동인에서 나온다.

- **capture 면 동인**: 작업 중 발견한 재사용 가능 지식이 세션 종료와 함께 휘발 → 완료시점 capture 게이트로 외부화 흔적을 강제(forced-no-silent-skip).
- **slimming 면 동인**: 축적된 MEMORY.md 가 harness session-reminder 한도(per-entry one-line ~200자) 및 총량 cap(24.4KB, ADR-071 §18.2)을 초과 → 무손실 슬림화 규약.
- **차용 vs internal 도출 경계**: oh-my-claudecode(OMC, MIT) skillify 의 3문 admission 휴리스틱 1건만 차용, 나머지 거버넌스(경로 규약·char-budget·용량 cap·슬림화 전략)는 internal 도출 (firsthand — OMC skillify 에는 char-cap·descriptor-only split 부재).
- **로컬-only 제약**: `phase:완료` transition·완료 marker·MEMORY.md 가 전부 working-tree 또는 `~/.claude` 외부 파일 → 클라우드 러너 미접근 → required CI 구조적 불가, warning-tier 가 정답.

## 핵심 규칙

### 원리 1 — capture admission 은 semantic, 흔적은 mechanical

- 캡처 여부 판정(3문 게이트: 5분 구글 불가 ∧ 코드베이스 특정 ∧ 실제 노력)은 **semantic judgment** — mechanical lint 불가, Orchestrator self-eval (behavioral).
- 그러나 "흔적 존재"(capture artifact OR no-capture note)는 **mechanical-checkable** — presence lint 가능.
- → 게이트는 흔적만 강제하고 품질은 self-eval. 이로써 "캡처할 게 없다" 도 명시적 흔적을 남겨야 한다(forced-no-silent-skip) — 게이트가 항상 통과하는 검사연극이 되지 않는다.

### 원리 2 — char-budget 은 OMC 차용이 아니라 internal 도출

- 차용: oh-my-claudecode(MIT) skillify 의 3문 admission 휴리스틱 1건뿐.
- internal 도출: 경로 규약(in-repo `skills/`·`docs/domain-knowledge/`), char-budget(2-layer), 용량 cap(24.4KB), 슬림화 전략. OMC skillify 에는 char-cap·descriptor-only split 이 없다(firsthand).
- 2-layer budget: (a) per-entry one-line ~200자 = harness session-reminder 도출 / (b) total 24.4KB = ADR-071 §18.2 도출. (a) 위반(긴 한 줄)이 (b) 위반(총량)을 견인하므로 둘 다 필요.

### 원리 3 — 로컬-only 게이트는 required CI 불가, warning-tier 가 정답

- `phase:완료` transition = Orchestrator self-write(로컬), 완료 marker = working-tree, MEMORY.md = `~/.claude` 외부 파일 → 클라우드 러너 미접근.
- → required CI check **구조적 불가**. warning-tier + `workflow: null` local-only self-check 가 정답 (ADR-099/ADR-122/ADR-128 선례). required check 신설 0 → branch protection 6-tuple 무변경.
- 비용 정직 고지: 자율준수 의존이 0 으로 떨어지지 않는다. CI hard-block 으로 만들 수 없는 한계를 받아들이고 local check + evidence-registry 로 behavioral compliance 를 보조한다.

### 원리 4 — 완료-self-check family (관찰, 강제 추상화 보류)

- worktree-clean(ADR-128) + capture(ADR-129) = `phase:완료` local-only warning-tier self-check family 가 emerging.
- 지금 공통 프레임워크로 강제 추상화하지 않는다 — 검증 대상(worktree 잔존 vs 지식 흔적)이 disjoint 라 공통화 이득 < 비용 (ADR-119 §결정 9 3문 게이트). family 가 3+ 면 escalation.

## 경계

- **cross-ref 동형이나 통합 금지**: capture 3문 게이트 ↔ ADR-119 §결정 9 제안 필요성 3문 게이트 = **동형**(noise 억제 3문 게이트)이나 **도메인 disjoint**(지식 캡처 ↔ 작업 제안) → 통합 금지, cross-ref 만.
- **family 강제 추상화 out-of-scope**: 완료-self-check family(worktree-clean + capture)는 현재 관찰 단계 — 공통 프레임워크 추상화는 family 가 3+ 일 때까지 보류 (원리 4).
- **절차·결정 영역 분리**: 본 note 는 *원리* 만 owner. 절차는 `knowledge-capture-gate` skill, 결정(normative)은 ADR-129 가 SSOT (ADR-120 §결정 3 split — 본 note 에 절차·결정 중복 작성 금지).

## 관련 ADR

- [ADR-129](../../../../archive/adr/ADR-129-omc-knowledge-capture-memory-governance.md) — 지식 캡처 + 메모리 거버넌스 정책 SSOT (본 페이지의 normative carrier — §결정 1 capture 게이트 + §결정 2 MEMORY.md 용량관리).
- [ADR-071 §18.2-18.3/18.7](../../../../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) — MEMORY.md cap(24.4KB) + 슬림화 normative + deferred mechanism (Amendment 12 해제). 원리 2 의 (b) total budget 도출 근거.
- [ADR-128](../../../../archive/adr/ADR-128-completion-stage-formalization.md) — 완료 단계 정식화 archetype. 원리 3 의 local-only warning-tier self-check 선례 + 원리 4 완료-self-check family 의 worktree-clean 멤버.
- [ADR-119](../../../../archive/adr/ADR-119-research-before-claims.md) — 제안 필요성 3문 게이트 (§결정 9). capture 3문 게이트와 동형이나 도메인 disjoint — 통합 금지 cross-ref (경계 참조) + 원리 4 family 추상화 보류 판단의 3문 게이트 근거.
- [ADR-045](../../../../archive/adr/ADR-045-story-retro-mandatory-trigger.md) — Story retro mandatory trigger. 지식 보존 인접 영역(회고 산출물 영속화).
- [ADR-051](../../../../archive/adr/ADR-051-ssot-skill-extraction-pattern.md) — SSOT skill extraction pattern. 본 note(원리) ↔ skill(절차) ↔ ADR(결정) 3-way split 의 패턴 근거.
- `skills/knowledge-capture-gate/SKILL.md` — 절차 SSOT (본 note 와 disjoint — 절차 owner).

## 변경 이력

- **2026-06-24** — 신설 (CFP-2392 carrier, ADR-129). 휘발성 운영지식 영속화 거버넌스의 두 면(capture / slimming) 원리 4종 + cross-ref SSOT 정립. capture admission semantic vs 흔적 mechanical(원리 1) / char-budget internal 도출(원리 2) / 로컬-only warning-tier(원리 3) / 완료-self-check family 강제 추상화 보류(원리 4). doc-frontmatter + doc-section-schema 6 필수 섹션 (정의 / 컨텍스트 / 핵심 규칙 / 경계 / 관련 ADR / 변경 이력) 정합 — content 손실 0, re-structure only.
