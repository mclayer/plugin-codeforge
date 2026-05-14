---
adr_number: 71
title: Orchestrator-user dialog convergence — frame mode + 4 layer 검증 + cross-Story 영속 incidents file
status: Accepted
category: governance
date: 2026-05-14
carrier_story: CFP-612
parent_epic: CFP-525  # ancestor
supersedes: null
amends: null
amendments: []
related_stories:
  - CFP-612  # carrier
  - CFP-525  # ancestor Epic (closed 2026-05-13)
  - CFP-582  # conceptual pair (agent ↔ agent debate domain)
  - CFP-445  # ADR-064 carrier (proposing-time 5 룰 mother policy)
  - CFP-387  # ADR-058 sunset criteria carrier
  - CFP-436  # ADR-063 atomic invariant carrier
  - CFP-438  # ADR-065 mechanical self-check carrier
  - CFP-411  # ADR-052 Amendment 1 (touchpoint #4) carrier
  - CFP-578  # ADR-070 verify-before-trust carrier
related_adrs:
  - ADR-064  # 결정 원칙 mandate — proposing-time 5 룰 mother policy (mechanical version 승격 source)
  - ADR-058  # sunset criteria mandate (is_transitional: false 정합)
  - ADR-052  # Codex Proactive Check 6 touchpoint (Amendment 1 multi-round debate + Amendment 3 fact-check marker)
  - ADR-059  # debate-protocol-v1 (conceptual cross-ref only — schema fit 부적합)
  - ADR-063  # marketplace atomic invariant (plugin.json MINOR bump 발화)
  - ADR-065  # ArchitectAgent Phase 1 mechanical self-check 7-item
  - ADR-070  # Codex verify-before-trust (fact-check marker source)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무 (governance category)
  - ADR-039  # inline whitelist 1번 entry (사용자 dialog) cognitive layer 강화
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/orchestrator-communication-incidents.md
  - skills/user-dialog-mode/SKILL.md
  - docs/parallel-work/section-ownership.yaml
is_transitional: false
mechanical_enforcement_actions: []
# Wave 5 = cognitive + persistence layer only.
# Layer 1 mechanical lint (preamble presence check) = 별 follow-up CFP 분리 (Story §1 verbatim).
# 본 ADR effective 후 신설 evidence-enforceable entry 가 follow-up CFP carrier 에서 추가될 때
# mechanical_enforcement_actions[] 갱신 + Amendment 발의 (강화 방향만 — ADR-058 §결정 5 / ADR-064 §결정 7
# top-down ratchet 정합).
---

# ADR-071: Orchestrator-user dialog convergence — frame mode + 4 layer 검증 + cross-Story 영속 incidents file

## 상태

Accepted (2026-05-14 KST, CFP-612 carrier). `is_transitional: false` — 영구 정책 (governance carrier, ADR-064 / ADR-058 self carrier 패턴 정합).

## 본질 선언 (Wave 5 핵심)

> **Orchestrator 가 사용자와 대화할 때, mechanical rule 추종이 아니라 진짜 수렴 대화에 참여하도록 codeforge SSOT 를 영구적으로 바꾸는 변화.**

위 본질 선언 (CFP-612 사용자 directive verbatim) 이 본 ADR 의 **anchor**. 본 ADR 의 모든 §결정 (frame mode / 4 layer / sub-mechanism / Layer 4 영속 file) 은 본질을 보조하는 **scaffolding** — mechanism 만 codify 하고 본질을 놓치면 가설 E (mechanical 규칙 자체 한계) 의 self-defeating trap. 본 anchor 가 §결정 1 보다 먼저 배치된 이유 = mechanism 우선 reading risk 회피 forcing function (CFP-612 RequirementsPL §4.2.3 경고 힌트 1번 정합).

## 컨텍스트

본 ADR 의 동인은 CFP-612 §1 verbatim "관찰된 vulnerability 4 종 + 심층 원인 가설 5 종" — 기존 soft 안전망 (memory entry / ADR-064 § "결정 제시" 5 룰) 의 mechanical enforcement 부재. 4 vulnerability:

1. 식별자 (ADR / CFP / 영문 약어) 사전 요약 없이 사용자에게 던지는 패턴
2. subagent 결과를 abstract packet 형태로 보고 → 사용자가 큰 그림 잡기 어려움
3. 가치 판단 영역에서 derived default 단독 선언하고 진행
4. 한 번 지적 받은 패턴이 다음 turn 에 반복되는 경향

5 심층 원인 가설 (서로 겹침): (A) 입력 context 의 중력 — codeforge 내부 vocabulary 비중 / (B) 두 역할 (codeforge 운영 + 사용자 대화) 미분리 / (C) 사용자 지식 경계 모델 부재 / (D) 진행감의 비용 인식 / (E) **Mechanical 규칙 자체 한계** — 외형 검사 규칙이 본래 의도와 반대로 작동 가능 (메타 경고).

선행 SSOT 정합:

- [ADR-064](ADR-064-decision-principle-mandate.md) — `결정 제시` 5 룰 (derived default / 옵션 dump 금지 / 식별자 사전 요약 / brevity / AskUserQuestion 범위) 의 **mechanical version 승격 + scope 확장** carrier. proposing-time 만 → 전 turn 적용. ADR-064 §결정 7 top-down ratchet 정합 (강화 방향 only).
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — `is_transitional: false` 영구 정책 + `## 해소 기준` "N/A — permanent policy" 1줄 패턴 정합.
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) — 본 ADR 신설 = CLAUDE.md 의미 변경 = plugin.json MINOR bump = 3-file atomic invariant 발화.
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) — Phase 1 산출물 7-item mechanical sync self-check 적용 (link target Phase 분배 / MANIFEST.yaml 갱신 NA declare / section-ownership row append).
- [ADR-052 Amendment 1](ADR-052-codex-proactive-check-touchpoints.md) — touchpoint #4 (RequirementsPL §1-§6 완료 직후) multi-round debate 격상. 본 Story §2-§6 가 첫 사례.
- [ADR-070](ADR-070-codex-verify-before-trust.md) — fact-check marker 4 + reverse-explicit `[verification-out-of-scope]` 1 종 verify-before-trust source.
- [ADR-059](ADR-059-debate-protocol-v1.md) — agent ↔ agent debate domain. 본 ADR 은 Orchestrator ↔ user domain — **direct schema mapping 부적합** (CFP-582 의 3 marker pattern 은 debate transcript verification schema, turn-by-turn user dialog 에 fit 안 함). Conceptual cross-ref only — schema 재사용 절대 금지.
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — inline whitelist 4-entry 의 1번 entry (사용자 dialog) 안 cognitive layer 강화. ADR-039 위반 아님 (inline whitelist scope 안 cognitive 보강).
- [ADR-040 Amendment 3](ADR-040-worktree-convention.md) — governance category ADR 의 `mechanical_enforcement_actions[]` frontmatter 의무. Wave 5 = cognitive + persistence layer only, Layer 1 mechanical lint 별 follow-up CFP — actions list `[]` empty + retroactive 면제 표시 (§결정 7.C 정합).

## 결정

### §결정 1 — 사용자 대화 모드 frame (frame mode 의무)

Orchestrator 가 사용자에게 메시지를 발화하는 turn (= ADR-039 inline whitelist 1번 entry = 사용자 dialog turn) 시 **다른 사고 모드 진입 의식**. 본 frame mode 진입은 매 user-facing turn 의 의무. mechanism 만 적용하고 frame mode 진입 의식을 놓치면 본 ADR 본질 anchor 가 충족되지 못함.

**thinking 절차 4 step** (CFP-612 §1 verbatim "후보 4 — 사용자 대화 모드 진입 의식 (frame, 후보 1·2·3 위에)" 4 sub-bullet 정합):

1. **codeforge 내부 어휘 "내부 메모" 분류 격리** — Orchestrator 입력 context 의 codeforge vocabulary (ADR-NNN / CFP-NNN / lane plugin name / hook name / inter-plugin contract name 등) 를 "내부 메모" 영역으로 분류. 사용자 발화 본문에 직접 등장 금지 (식별자 인용 시 사전 요약 의무 — ADR-064 §결정 3 룰 3 정합).
2. **사용자 지금까지 무엇 알고 있는지 정리** — 사용자 mental model 추정. 사용자가 이미 알고 있는 사항 (이전 turn 발화 기준) 과 미공개 컨텍스트 분리.
3. **사용자 이 turn 무엇 답·결정해야 하는지 한 문장** — 본 turn 의 사용자 입장 action item 1 문장 정리. 사용자가 답해야 할 것이 한 문장으로 명확하지 않으면 본 step 미완.
4. **위 셋 바탕으로 메시지 작성** — step 1 (격리) + step 2 (사용자 지식) + step 3 (turn 결정) 의 통합 위에 메시지 본문 작성.

frame mode 진입 marker 형식 (visible vs hidden cognitive layer) = playbook §3.14 본문 결정 영역 (본 ADR scope = 의무 declare 까지).

### §결정 2 — frame mode 안 세부 규칙 3 종 (후보 1·2·3 흡수)

frame mode 진입 후 적용되는 세부 룰. CFP-612 §1 verbatim "후보 1·2·3" 흡수.

**(a) 후보 1 — 메시지 보내기 직전 self-check 3 문항**:
1. 사용자가 답해야 할 것이 한 문장으로 명확한가
2. 비-codeforge 맥락 사람이 이해 가능한가
3. 답하는 데 필요한 배경 (왜 / trade-off / 걸려있는 것) 충분한가

길이 제약 없음 (3 문항 모두 PASS 후 메시지 발화 의무).

**(b) 후보 2 — 사실/가치 분리, 모호 시 가치 측 분류**:
- 사실 판단 → derived default 적용 (ADR-064 §결정 3 룰 1 정합)
- 가치 판단 → 무조건 explicit 사용자 확인 (`AskUserQuestion` 발화 의무, ADR-064 §결정 3 룰 5 정합)
- 모호 시 → 가치 측 분류 (safe direction)

memory entry `feedback_question_quality` 의 normative 승격 carrier (§결정 8 mapping 표 참조).

**(c) 후보 3 — sub-agent 결과의 사용자용 평이 번역**:
- raw packet 그대로 노출 금지
- codeforge 내부 용어 평이한 한글로 번역
- **3 줄 제약 명시적 거부** — 길이 자유
- "왜 / trade-off / 걸려있는 것" 배경 포함
- 원본 packet 은 사용자 요청 시 별도 제공

### §결정 3 — 4 layer 검증 (모두 도입)

frame mode + §결정 2 세부 룰을 보조하는 4 검증 layer. CFP-612 §1 verbatim "Layer 1 / 2 / 3 / 4" 정합.

| Layer | 동작 | 발화 위치 |
|---|---|---|
| **Layer 1 — 가시적 preamble** | 메시지 맨 위 "지금 답해주실 것" 1 문장 가시 | 매 user-facing turn 의 메시지 맨 윗줄. trivial turn (E12) 면제 + turn-shape edge 분기 (E9 streaming / E10 tool-call-only / E11 AskUserQuestion popup) 적용. 분기 derived default = playbook §3.14 본문 "Turn-shape derived defaults" 표 결정 영역. **mechanical lint 별 follow-up CFP** — 본 Wave 5 scope 외 |
| **Layer 2 — 자기 declare** | turn 끝 "주의한 가설" 1 줄 declare (보조 신호) | 매 user-facing turn 의 메시지 맨 아랫줄. trivial turn (E12) + E10 tool-call-only + E11 popup turn 면제. E9 streaming = final flush 시 적용. derived default = playbook §3.14 |
| **Layer 3 — keyword "추상" 즉시 halt** | 사용자 메시지 본문 안 "추상" 한글 token 등장 시 즉시 halt + 재작성 의무 | 사용자 발화 token detection 시점. Hanja form ("抽象") 면제 (CLAUDE.md §1 한자 금지 정책 정합). stem match (예: "추상적" / "추상화") = 적용. **모든 turn-shape edge (E9-E12) 에서 active** — popup option_text 안 "추상" 등장 가능. playbook §3.14 본문이 stem vs exact match 결정 영역 |
| **Layer 4 — 누적 detection** | N=1 즉시 halt (같은 양상 다음 turn 재발 시) + M=5 max threshold 사용자 escalation (`AskUserQuestion` 발화) + 누적 file 영속 | `docs/orchestrator-communication-incidents.md` (cross-Story append-only). **모든 turn-shape edge (E9-E12) 에서 active** — 단 E10 tool-call-only turn 자체는 incident 분류 외 (no user-facing prose = pattern detection 영역 외). §결정 6 참조 |

**Turn-shape edge derived default (E9 / E10 / E11) cross-ref**: 본 ADR §결정 10 (scope out) 정합 — 4 layer × 4 turn-shape edge 의 정량 default matrix 는 **playbook §3.14 "Turn-shape derived defaults" 표 결정 영역**. 본 ADR §결정 3 안 mapping 만 명시 (cross-ref boundary 보존). E10 tool-call-only 정량 정의 (prose 0 줄 + cosmetic 1-줄 미만) + E11 popup turn Layer 2 면제 사유 (popup 본문 자체 declare semantic 충당) 도 playbook 결정 영역. RequirementsPL §5.3 E9-E12 의 `[fact-check-pending]` marker 가 본 FIX-1 으로 모두 resolved.

### §결정 4 — Sub-mechanism 2 종 (수렴 보장)

CFP-612 §1 verbatim "Sub-mechanism" 정합. 4 layer 가 detect 만 하고 수렴 보장 못함 → 본 sub-mechanism 이 수렴 forcing function.

**Sub-mechanism 1 — 매 halt 후 재작성 시 "이전과 다르게 한 점" 1 줄 명시 의무**: Layer 3 또는 Layer 4 N=1 halt 후 재작성 메시지의 맨 아랫줄 (Layer 2 declare 와 별 줄) 에 "이전과 다르게 한 점:" prefix + 1 줄 본문. 단순 표현 다듬기 (예: 어휘 변경 / 문장 길이 압축) 이 아닌 **차원 전환** 의무.

**Sub-mechanism 2 — 같은 양상 재발 시 다른 차원 전환 의무**: Layer 4 누적 file 에 동일 양상 row count ≥ 2 시점 (즉 같은 양상이 한 번 재발 시점) 부터 단순 표현 다듬기 금지. **4 차원 enum** 중 다른 차원으로 강제 전환:

| 차원 | 의미 | 전환 예시 |
|---|---|---|
| **표현** | 어휘 / 문장 길이 / 구조 변경 | "ADR-064 §결정 3" → "결정 제시 5 룰" |
| **결정 구조** | 옵션 제시 방식 / derived default 적용 / AskUserQuestion 형식 | numbered list → 권장 1 + 대안 1 (ADR-064 §결정 3 룰 4 정합) |
| **보고 형식** | sub-agent 결과 packet 표시 / 평이 번역 / 길이 | raw JSON → 평이 한글 (3 줄 제약 거부) |
| **질문 자체** | 어떤 결정을 사용자에게 묻는지 자체 변경 | "방향 X / Y 중 어느 것" → "본 결정의 user value 우선순위는?" |

차원 전환 의무 = 같은 양상 재발 사이클을 break 하는 forcing function. memory `feedback_explain_before_ask` 의 normative 승격 carrier (§결정 8 mapping 표 참조).

**4 차원 enum exhaustiveness declare**: 본 4 차원 (표현 / 결정 구조 / 보고 형식 / 질문 자체) 은 **closed enum**. 5번째 차원 추가는 별 ADR Amendment 의무 (강화 방향 ratchet 정합 단 사용자 burden 변화 영역 — pattern_dimension column 분류 schema 변경). Layer 4 영속 file `pattern_dimension` column 의 valid value enum 도 본 4 종으로 한정 (schema 안정성 보장).

### §결정 5 — 사실/가치 판단 분류 결정 트리 (§결정 2 (b) 확장)

§결정 2 (b) 의 mechanical 분류 절차. Orchestrator 매 turn 의 결정 후보에 적용:

```
결정 후보 발화 직전:
  is_factual?
    YES → derived default 적용 (단 derived default 가 추론 가능한 컨텍스트 보유 시)
                   ↓
                  declare default + 결과 보고 + 사용자 정정 의무
    NO (가치 판단 영역) → AskUserQuestion 발화 의무 (ADR-064 §결정 3 룰 5 정합)
    AMBIGUOUS → 가치 측 분류 (safe direction)
                   ↓
                  AskUserQuestion 발화 의무
```

**사실 판단 예시**: 파일 존재 확인 / `wc -l` 결과 / `git log` 출력 / SHA 식별자 / `grep` 결과 (모두 derived default 적용 가능 영역).

**가치 판단 예시**: 사용자 선호 (UX / 보고 길이 / 식별자 인용 빈도) / 정책 강화 방향 (warning → blocking) / scope 결정 (1 CFP 안 vs 분리) / brainstorm 후 채택안 결정 (모두 AskUserQuestion 의무 영역).

**모호 영역 예시**: derived default 가 컨텍스트로 추론 가능 but 사용자 explicit 발화 없음 + 결과가 future 작업에 영향 큼 — 가치 측 분류 (사용자 확인 후 진행).

### §결정 6 — Layer 4 영속 file 영역 + schema

cross-Story append-only file (wrapper repo 레벨 단일 file). owner = Orchestrator 단독 monopoly (FIX Ledger / Git Ops Log 패턴 유사).

**file path**: `docs/orchestrator-communication-incidents.md` (wrapper repo). consumer 측은 자기 repo 의 `docs/orchestrator-communication-incidents.md` (별 lifecycle, consumer-guide §1 cross-ref 의무).

**initial content** (CL-3 derived default — Phase 1 commit 시 본 ADR 동반 신설):

```markdown
---
title: Orchestrator Communication Incidents (Layer 4 누적 file)
status: Active
category: governance
date: 2026-05-14
carrier_story: CFP-612
related_adrs:
  - ADR-071
schema_version: "1.0"
---

# Orchestrator Communication Incidents

> Layer 4 누적 detection file (ADR-071 §결정 6).
> owner = Orchestrator 단독 monopoly. append-only. cross-Story 영속 (Story 종료 시 reset 없음).
> M=5 max threshold 누적 시 사용자 escalation (`AskUserQuestion` 발화).
> reset 정책: manual archive only (yearly file rotate 또는 별 row delineator marker).

## Schema

| Column | 의미 |
|---|---|
| iter | 누적 incident sequential id (전체 file 기준) |
| timestamp | KST ISO8601 |
| story_key | 발생 시점 active Story KEY (cross-Story 추적) |
| pattern_dimension | 4 차원 enum (표현 / 결정 구조 / 보고 형식 / 질문 자체) |
| pattern_summary | 어떤 양상이 detect 됐는지 1 줄 |
| trigger | Layer 3 (사용자 "추상" keyword) / Layer 4 N=1 (같은 양상 재발) / Layer 4 M=5 (escalation) |
| different_dimension_after_halt | Sub-mechanism 1 — "이전과 다르게 한 점" 1 줄 |
| escalation_outcome | M=5 escalation 시 사용자 답변 요약 (`AskUserQuestion` outcome) — N=1 / Layer 3 시 비어있음 |

## Incidents

| iter | timestamp | story_key | pattern_dimension | pattern_summary | trigger | different_dimension_after_halt | escalation_outcome |
|------|-----------|-----------|-------------------|-----------------|---------|-------------------------------|--------------------|

<!-- 비어있는 table — Orchestrator 가 incident detect 시 row append -->
```

**lifecycle 룰**:
- append-only (Orchestrator 단독)
- Story 종료 시 reset 없음 (cross-Story 영속)
- M=5 카운터 = lifetime 영속 (manual reset 만 허용 — 사용자 explicit reset request 시)
- pattern_dimension 분류는 §결정 4 4 차원 enum 만 허용
- 사용자 escalation 후 다음 incident = pattern_dimension 강제 전환 (§결정 4 sub-mechanism 2 정합)

### §결정 7 — Layer 3 keyword "추상" semantics

CFP-612 §1 verbatim "Layer 3 — keyword '추상'" + RequirementsPL §5.3 E1·E2 derived default 정합.

- **한글 token "추상"** 등장 시 trigger (substring stem match — "추상" / "추상적" / "추상화" 등 모두 trigger)
- **Hanja form "抽象"** 면제 (CLAUDE.md §1 한자 금지 정책 정합 — 한자 형태 자체는 codeforge 안에서 발화되지 않음)
- **영문 alias** ("abstract" / "abstraction") = trigger 아님 (한글 token 만 anchor)
- **false positive 양 증가 risk** 인지 — stem match 가 false positive 발생 가능 영역 (예: "추상 미술" 같은 도메인 어휘) — playbook §3.14 본문이 false positive 처리 결정 영역
- **keyword 확장 ratchet 의무** — Layer 3 trigger keyword 영역 확장 (예: "두루뭉술" / "막연히" 추가) 시 별 ADR Amendment 의무 (사용자 burden 변화 영역 — Layer 3 가 사용자 발화 token detection 기반이므로 keyword 추가 = 사용자 표현 자유도 축소). ADR-058 §결정 5 sunset_justification 불요 (강화 방향 ratchet 정합) 단 별 CFP carrier + Story §1 사용자 explicit 승인 의무.

### §결정 8 — 3 memory entry normative 승격 mapping 표

CFP-612 §1 verbatim "기존 memory entry normative 승격" + AC-12 measurement column 정합:

| memory entry | 정책 위치 SSOT 이전 | unchanged scope |
|---|---|---|
| `feedback_explain_before_ask` | **playbook §3.14** (frame mode 본문 SSOT) + 본 ADR §결정 1 step 4 (메시지 작성 시 식별자 사전 요약 의무) + §결정 4 sub-mechanism 1 (이전과 다르게 한 점) | — |
| `feedback_question_quality` | **playbook §3.14** (frame mode 본문 SSOT) + 본 ADR §결정 2 (b) (사실/가치 분리) + §결정 5 (분류 결정 트리) | — |
| `feedback_subagent_driven_auto_select` | **변경 없음** — playbook §3.0.5 기존 정책 유지 (Subagent-Driven 자동 선택) | codeforge wrapper side SSOT 변경 0 (사용자 personal memory side 의 entry 자체는 영향 받지 않음 — 사용자 영역, codeforge wrapper scope 외) |

**승격 시점**: 본 Story Phase 2 PR merge 시점 (effective 단계 완료 — CLAUDE.md cross-ref + playbook §3.14 + Layer 4 file 동반 반영). ADR-071 Accepted 직후는 effective 단계 미완. Phase 2 PR retro (PMOAgent ADR-045 mandate) 의제로 사용자 personal memory entry 삭제 제안 — 사용자 결정 영역 (codeforge wrapper scope 외).

### §결정 9 — CFP-582 conceptual cross-ref + schema fit 부적합 declare

[ADR-059 Amendment 2](ADR-059-debate-protocol-v1.md) + CFP-582 = **agent ↔ agent debate domain**. 본 ADR-071 = **Orchestrator ↔ user dialog domain**. 두 도메인 의 conceptual common ground = "수렴 dialog 가 본질" 1 점. 단:

- CFP-582 의 3 marker pattern (`counterargument_present` / `alternative_proposed` / `debate_purpose_statement_present`) = **debate transcript verification schema** — multi-round adversarial debate 의 convergence_quality_invariant 검증용.
- 본 ADR-071 = **turn-by-turn Orchestrator-user dialog** — single-turn cognitive frame + cross-Story 누적 detection.

**Schema fit**: CFP-582 의 3 marker = 라운드 단위 transcript 검증, 본 ADR-071 = turn 단위 메시지 검증. **직접 schema mapping 부적합**. ADR-071 §결정 1-7 의 frame mode + 4 layer + sub-mechanism 어느 항목도 CFP-582 의 3 marker schema 를 import 하지 않는다. CFP-582 의 본질 (수렴 dialog) 만 conceptual cross-ref. **schema 재사용 절대 금지**.

**`anchor_recurrence_count` reset 의미 (Wave 5 scope)**: ADR-059 Amendment 1 의 `anchor_recurrence_count` 는 debate 라운드 영역 카운터 — Wave 5 영역에서는 항상 0 (debate 미발동 = 본 Story 의 첫 review = 누적 영역 외). Layer 4 영속 file (`docs/orchestrator-communication-incidents.md`) 의 M=5 lifetime counter 는 `anchor_recurrence_count` 와 다른 차원 (cross-Story 영속 vs single-debate 라운드). 두 카운터 간 mapping 절대 금지.

ADR-059 = lane-agnostic protocol contract — lane 정보를 인자로 받는 일반 schema. 본 ADR-071 = lane 분기 영역 아님 (Orchestrator-user turn 자체는 모든 lane 진입 직전·직후·중간에 발생 — lane-agnostic 도 아니고 single-lane 도 아닌 별 layer). 본 declare 가 미래 CodeReview / SecurityTest lane 의 debate 확장 (deferred CFP-C scope) 와 본 ADR 의 sibling 발의 가능성을 분리.

### §결정 10 — Scope out (별 follow-up CFP)

CFP-612 §1 verbatim "Scope 가 아닌 것" + RequirementsPL §5.4 정합:

- **Layer 1 preamble mechanical lint** — 별 follow-up CFP 분리 (본 Wave 5 = cognitive + persistence layer 만). 본 ADR effective 후 evidence-enforceable warning-tier entry 신설 carrier 가 follow-up CFP.
- **agent ↔ agent debate domain** — CFP-582 cover 완료, 본 ADR scope 외.
- **코드 품질 / 보안 / 성능** — 본 Wave 5 = cognitive + persistence layer SSOT only.
- **사용자 personal memory entry 자체 삭제** — 사용자 영역, codeforge wrapper scope 외. PMOAgent retro 의제로 제안만.
- **consumer overlay 영역 customization** — consumer overlay 가 정책 축소 불허 (CLAUDE.md L155-156 정합) — Wave 5 정책 자체는 wrapper-level normative.
- **debate-protocol-v1 의 3 marker import** — §결정 9 verbatim "직접 mapping 부적합", schema 직접 채택 절대 금지.
- **frame mode 진입 marker 의 visible vs hidden 형식 결정** — playbook §3.14 본문 결정 영역.
- **Layer 3 stem match vs exact match 결정** — playbook §3.14 본문 결정 영역.
- **Layer 4 file rotate / archive 정책** — playbook §3.14 본문 결정 영역.

### §결정 11 — ADR-039 inline whitelist 1번 entry cognitive 강화 declare

[ADR-039 §결정 7](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) inline whitelist 4-entry 의 1번 entry (사용자 dialog) 에 frame mode + 4 layer 의 추가 cognitive layer 부착 = **ADR-039 위반 아님**. inline whitelist scope 안 cognitive 보강 (file write / Bash 실행 / Agent spawn 분류 영역 외).

본 declare = ArchitectAgent over-engineer 회피 forcing function (RequirementsPL §4.2.4 ADR-039 충돌 후보 → 해소 경로 명시).

## 결과

### Phase 1 산출물

본 ADR effective 후 매 codeforge session 의 Orchestrator 가 user-facing turn 시 frame mode 진입 의무. Phase 1 산출물 (본 ADR + playbook §3.14 + 신규 skill `codeforge:user-dialog-mode` + Layer 4 file 신설 + CLAUDE.md cross-ref + plugin.json MINOR bump + marketplace sync) 동시 발효.

### measurable signal

본 ADR `is_transitional: false` 영구 정책 + ADR-058 `## 해소 기준` "N/A — permanent policy". 본 ADR 의 effective signal:

- Layer 4 file (`docs/orchestrator-communication-incidents.md`) row count
- M=5 escalation 발생 빈도 (`AskUserQuestion` 발화 count)
- §결정 4 sub-mechanism 2 차원 전환 횟수 (pattern_dimension column distinct count)
- PMOAgent retro 의 user feedback (수렴 dialog 체감 / 식별자 사전 요약 누락 빈도)

### Follow-up scope

- **Layer 1 preamble mechanical lint** = 별 follow-up CFP (Wave 5 §결정 10 scope out)
- **frame mode marker 형식** = playbook §3.14 본문 결정 영역
- **Layer 3 stem vs exact match** = playbook §3.14 본문 결정 영역
- **Layer 4 file rotate / archive** = playbook §3.14 본문 결정 영역

## self-application top-down ratchet

본 ADR amendment 는 [ADR-064 §결정 7](ADR-064-decision-principle-mandate.md) top-down ratchet 정합 — 강화 방향만 허용 (scope 확장 / 강도 강화). 약화 방향 (`is_transitional: false → true` 다운그레이드 / 4 layer 축소 / 3 memory entry mapping 회수 / Sub-mechanism 2 차원 enum 축소) 은 [ADR-058 §결정 5](ADR-058-adr-sunset-criteria-mandate.md) `sunset_justification` 의무로 차단. 본 ADR-071 = ADR-064 ratchet 의 직접 carrier (mechanical version 승격 + scope 확장 = strict superset).

## 해소 기준

N/A — permanent policy.

본 ADR 의 sunset 은 codeforge dialog governance 자체 폐지 (예: codeforge plugin family 전체 deprecate) 또는 본 ADR supersede (예: ADR-071 의 강화 amendment 발의) 시점에만 가능. ADR-064 / ADR-058 / ADR-063 / ADR-065 / ADR-039 governance carrier 의 `is_transitional: false` 패턴 정합 (recursive sunset 회피).

## 관련 파일

- [ADR-064](ADR-064-decision-principle-mandate.md) — 결정 원칙 mandate (proposing-time 5 룰, 본 ADR mechanical 승격 source)
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — sunset criteria mandate (`is_transitional: false` 정합 anchor)
- [ADR-052](ADR-052-codex-proactive-check-touchpoints.md) — Codex Proactive Check 6 touchpoint (Amendment 1 multi-round debate + Amendment 3 fact-check marker)
- [ADR-059](ADR-059-debate-protocol-v1.md) — debate-protocol-v1 (conceptual cross-ref only, §결정 9)
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) — plugin.json MINOR bump atomic invariant
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) — Phase 1 mechanical sync self-check 7-item
- [ADR-070](ADR-070-codex-verify-before-trust.md) — fact-check marker source
- [ADR-040](ADR-040-worktree-convention.md) — `mechanical_enforcement_actions[]` frontmatter 의무
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — inline whitelist 1번 entry cognitive 강화 (§결정 11)
- [CLAUDE.md](../../CLAUDE.md) — cross-ref 1-2 줄 (320 cap compression 정합)
- [docs/orchestrator-playbook.md](../orchestrator-playbook.md) — §3.14 frame + 4 layer + sub-mechanism 본문 SSOT
- [docs/orchestrator-communication-incidents.md](../orchestrator-communication-incidents.md) — Layer 4 영속 file
- [skills/user-dialog-mode/SKILL.md](../../skills/user-dialog-mode/SKILL.md) — frame mode + 4 layer lookup table skill
- [CFP-612](https://github.com/mclayer/plugin-codeforge/issues/612) — carrier Issue
- [CFP-525](https://github.com/mclayer/plugin-codeforge/issues/525) — ancestor Epic (closed)
- [CFP-582](https://github.com/mclayer/plugin-codeforge/issues/589) — sibling (agent ↔ agent domain, conceptual cross-ref)
