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
amendments:
  - amendment_id: 1
    date: "2026-05-16"
    carrier_story: CFP-777
    issue: https://github.com/mclayer/plugin-codeforge/issues/777
    summary: DialogFidelityAgent external verifier auxiliary layer additive (Layer 1-4 보존, sunset_justification null 강화 ratchet)
    sunset_justification: null
  - amendment_id: 2
    date: "2026-05-17"
    carrier_story: CFP-818
    issue: https://github.com/mclayer/plugin-codeforge/issues/818
    summary: DialogFidelityAgent 3-anchor 운영 정의 + turn-shape edge × 3-anchor 12 cell 활성 표 신설 + ADR-039 inline whitelist 1번 entry 정합 명문화 + ADR-064 §결정 9 Q-3check disjoint scope cross-ref (additive, Layer 1-4 보존 + 5번째 cognitive layer 신설 금지 invariant 보존, sunset_justification null 강화 ratchet)
    sunset_justification: null
  - amendment_id: 3
    date: "2026-05-17"
    carrier_story: CFP-833
    issue: https://github.com/mclayer/plugin-codeforge/issues/833
    summary: DialogFidelityAgent effectiveness measurement wiring (Epic CFP-761 Story-3 closing-the-loop) — Layer 4 incident realtime detect incident append-rate delta (proxy signal — not causal effectiveness measure) metric + evidence-checks-registry.yaml dialog-fidelity-effect warning-tier entry (owner_adr ADR-071 / carrier_adr ADR-060, precedent rate-limit-fallback-rate 동형) + mechanical_enforcement_actions[] 갱신 (ADR-040 §결정 7.A governance 의무) + 본문 §결정 14 신설. additive — Layer 1-4 + DialogFidelityAgent auxiliary layer 보존, ## 해소 기준 무변경 (permanent governance recursive sunset 회피), ADR-058 §결정 3 측정성 self-application 강화 ratchet. Epic plan Task 4 invariant 5 (label-registry MINOR) deviation = precedent override (OQ-3 사용자 확정 2026-05-17 KST, ADR-064 §결정 10 precedence)
    sunset_justification: null
  - amendment_id: 4
    date: "2026-05-17"
    carrier_story: CFP-851
    issue: https://github.com/mclayer/plugin-codeforge/issues/851
    summary: Conversational reporting frequency suppression contract — Orchestrator ↔ user dialog 의 발화 허용 touchpoint 3종 closed enumeration codify (§결정 15 신설). (a) 결과-명세 확인 (사용자 선언 결과 자체 모호 + rollback 비싼 경우, verifiable outcome surface 안전판) / (b) 사용자만 풀 수 있는 차단 (인증·권한 등 codeforge 자체 해소 불가) / (c) 최종 완료 보고 1회 (요청 작업 단위 전체 완료). 그 외 진행·중간 결정·근거·중간 결과 = 산출물 (Story / change-plan / ADR / PR / TodoWrite panel) 전용 기록. 무약화 invariant — frequency 축소 ≠ richness 축소, §결정 2(c) "3 줄 제약 거부 · 길이 자유 · 배경 포함" 보존 + Layer 1/2 preamble·declare 의무 turn 발생 시 그대로 적용. ADR-039 inline whitelist 1번·4번 entry scope 안 작동 (closed 4-entry 보존, 신규 entry 신설 0). 4번째 touchpoint 확장 시 별도 CFP 의무 (§결정 13.6 closed-enum 확장 패턴 정합). mechanical lint = behavioral directive only, 별도 follow-up CFP (§결정 10 패턴 정합). additive — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 2(c) 무약화, is_transitional=false 보존, ADR-058 §결정 5 약화 차단 영역 미적용
    sunset_justification: null
  - amendment_id: 5
    date: "2026-05-20"
    carrier_story: CFP-1104
    issue: https://github.com/mclayer/plugin-codeforge/issues/1106
    summary: Natural-language action trigger lookup table codify (§결정 16 신설) — consumer 가 자연어 token "codeforge upgrade" (또는 한글 변형) 발화 시 orchestrator 가 dialog reflex (AskUserQuestion 모드/채널 재질의) 차단 + 7 차원 derived default (trigger phrase regex / repo cwd 자동 주입 / mode dry-run → apply 자동 / channel overlay resolve fallback stable / scope 단일 plugin default / dirty tree abort / 실패 시 자동 rollback) 결정론적 mapping closed enumeration 1 entry. ADR-076 invariant `user_decision_branches=0` 를 dialog 진입 단계로 확장 carrier — 본 ADR-071 §결정 5 사실/가치 분리의 dialog reflex 차단 first applied case. closed enumeration 보존 invariant — 본 lookup table 이 ADR-071 내 4번째 closed enumeration 인스턴스 (3-anchor enum §13.6 / 4 차원 enum §4 / 3 touchpoint enum §15.5 / **trigger table §16**) 신설, 2번째 trigger token 확장 시 별도 CFP 의무 (§결정 13.6 closed-enum 확장 패턴 정합 — ADR-064 §결정 7 top-down ratchet 강화 방향 + ADR-058 §결정 5 sunset_justification null 보존). ADR-039 inline whitelist 1번 entry scope 안 작동 (사용자 dialog 허용 영역, 5번째 entry 신설 0). doc-only fast-path Story (src/tests touch 0). additive — Layer 1-4 / DialogFidelityAgent auxiliary / §결정 2(c) richness / 3 touchpoint enum (§15) 모두 보존, dialog reflex 차단 layer 추가만. is_transitional=false 보존, ADR-058 §결정 5 약화 차단 영역 미적용
    sunset_justification: null
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
  - CFP-777  # Amendment 1 carrier (DialogFidelityAgent additive auxiliary)
  - CFP-761  # parent Epic (DialogFidelityAgent 도입)
  - CFP-818  # Amendment 2 carrier (spawn trigger 운영 정의)
  - CFP-833  # Amendment 3 carrier (effectiveness measurement wiring — closing-the-loop)
  - CFP-851  # Amendment 4 carrier (conversational reporting frequency suppression contract)
  - CFP-1104  # Amendment 5 carrier (natural-language action trigger lookup table — "codeforge upgrade" mapping)
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
  - ADR-060  # evidence-enforceable framework (Amendment 3 dialog-fidelity-effect entry carrier — CFP-833)
  - ADR-076  # declarative-reconciliation-upgrade (Amendment 5 — invariant `user_decision_branches: 0` dialog 단계 enforcement carrier)
  - ADR-054  # doc-only fast-path (Amendment 5 — Story 분류 정합)
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/orchestrator-communication-incidents.md
  - skills/user-dialog-mode/SKILL.md
  - docs/parallel-work/section-ownership.yaml
is_transitional: false
mechanical_enforcement_actions:
  - action: dialog-fidelity-effect
    status: deferred-followup
    progress_note: "Phase 1 (CFP-833) = registry entry skeleton (non-null detect_command, #827 회피) + ADR-071 Amendment 3 + 본문 §결정 14. Phase 2 carrier (동일 Story CFP-833 후속 PR) = dialog-fidelity-measurement.yml workflow 2종 byte-identical + check-dialog-fidelity-effect.sh thin wrapper + lib .py. warning tier advisory (no PR block) — runtime cron metric, blocking 승격 의미 부적용 (precedent rate-limit-fallback-rate 동형)"
    target_section: §결정 14
# Wave 5 = cognitive + persistence layer. Amendment 3 (CFP-833) = effectiveness measurement layer (additive — Layer 1-4 + auxiliary 보존).
# Layer 1 mechanical lint (preamble presence check) = 별도 follow-up CFP 분리 (Story §1 verbatim).
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
- [ADR-040 Amendment 3](ADR-040-worktree-convention.md) — governance category ADR 의 `mechanical_enforcement_actions[]` frontmatter 의무. Wave 5 = cognitive + persistence layer only, Layer 1 mechanical lint 별도 follow-up CFP — actions list `[]` empty + retroactive 면제 표시 (§결정 7.C 정합).

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
| **Layer 1 — 가시적 preamble** | 메시지 맨 위 "지금 답해주실 것" 1 문장 가시 | 매 user-facing turn 의 메시지 맨 윗줄. trivial turn (E12) 면제 + turn-shape edge 분기 (E9 streaming / E10 tool-call-only / E11 AskUserQuestion popup) 적용. 분기 derived default = playbook §3.14 본문 "Turn-shape derived defaults" 표 결정 영역. **mechanical lint 별도 follow-up CFP** — 본 Wave 5 scope 외 |
| **Layer 2 — 자기 declare** | turn 끝 "주의한 가설" 1 줄 declare (보조 신호) | 매 user-facing turn 의 메시지 맨 아랫줄. trivial turn (E12) + E10 tool-call-only + E11 popup turn 면제. E9 streaming = final flush 시 적용. derived default = playbook §3.14 |
| **Layer 3 — keyword "추상" 즉시 halt** | 사용자 메시지 본문 안 "추상" 한글 token 등장 시 즉시 halt + 재작성 의무 | 사용자 발화 token detection 시점. Hanja form ("抽象") 면제 (CLAUDE.md §1 한자 금지 정책 정합). stem match (예: "추상적" / "추상화") = 적용. **모든 turn-shape edge (E9-E12) 에서 active** — popup option_text 안 "추상" 등장 가능. playbook §3.14 본문이 stem vs exact match 결정 영역 |
| **Layer 4 — 누적 detection** | N=1 즉시 halt (같은 양상 다음 turn 재발 시) + M=5 max threshold 사용자 escalation (`AskUserQuestion` 발화) + 누적 file 영속 | `docs/orchestrator-communication-incidents.md` (cross-Story append-only). **모든 turn-shape edge (E9-E12) 에서 active** — 단 E10 tool-call-only turn 자체는 incident 분류 외 (no user-facing prose = pattern detection 영역 외). §결정 6 참조 |

**Turn-shape edge derived default (E9 / E10 / E11) cross-ref**: 본 ADR §결정 10 (scope out) 정합 — 4 layer × 4 turn-shape edge 의 정량 default matrix 는 **playbook §3.14 "Turn-shape derived defaults" 표 결정 영역**. 본 ADR §결정 3 안 mapping 만 명시 (cross-ref boundary 보존). E10 tool-call-only 정량 정의 (prose 0 줄 + cosmetic 1-줄 미만) + E11 popup turn Layer 2 면제 사유 (popup 본문 자체 declare semantic 충당) 도 playbook 결정 영역. RequirementsPL §5.3 E9-E12 의 `[fact-check-pending]` marker 가 본 FIX-1 으로 모두 resolved.

### §결정 4 — Sub-mechanism 2 종 (수렴 보장)

CFP-612 §1 verbatim "Sub-mechanism" 정합. 4 layer 가 detect 만 하고 수렴 보장 못함 → 본 sub-mechanism 이 수렴 forcing function.

**Sub-mechanism 1 — 매 halt 후 재작성 시 "이전과 다르게 한 점" 1 줄 명시 의무**: Layer 3 또는 Layer 4 N=1 halt 후 재작성 메시지의 맨 아랫줄 (Layer 2 declare 와 별도 줄) 에 "이전과 다르게 한 점:" prefix + 1 줄 본문. 단순 표현 다듬기 (예: 어휘 변경 / 문장 길이 압축) 이 아닌 **차원 전환** 의무.

**Sub-mechanism 2 — 같은 양상 재발 시 다른 차원 전환 의무**: Layer 4 누적 file 에 동일 양상 row count ≥ 2 시점 (즉 같은 양상이 한 번 재발 시점) 부터 단순 표현 다듬기 금지. **4 차원 enum** 중 다른 차원으로 강제 전환:

| 차원 | 의미 | 전환 예시 |
|---|---|---|
| **표현** | 어휘 / 문장 길이 / 구조 변경 | "ADR-064 §결정 3" → "결정 제시 5 룰" |
| **결정 구조** | 옵션 제시 방식 / derived default 적용 / AskUserQuestion 형식 | numbered list → 권장 1 + 대안 1 (ADR-064 §결정 3 룰 4 정합) |
| **보고 형식** | sub-agent 결과 packet 표시 / 평이 번역 / 길이 | raw JSON → 평이 한글 (3 줄 제약 거부) |
| **질문 자체** | 어떤 결정을 사용자에게 묻는지 자체 변경 | "방향 X / Y 중 어느 것" → "본 결정의 user value 우선순위는?" |

차원 전환 의무 = 같은 양상 재발 사이클을 break 하는 forcing function. memory `feedback_explain_before_ask` 의 normative 승격 carrier (§결정 8 mapping 표 참조).

**4 차원 enum exhaustiveness declare**: 본 4 차원 (표현 / 결정 구조 / 보고 형식 / 질문 자체) 은 **closed enum**. 5번째 차원 추가는 별도 ADR Amendment 의무 (강화 방향 ratchet 정합 단 사용자 burden 변화 영역 — pattern_dimension column 분류 schema 변경). Layer 4 영속 file `pattern_dimension` column 의 valid value enum 도 본 4 종으로 한정 (schema 안정성 보장).

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

**file path**: `docs/orchestrator-communication-incidents.md` (wrapper repo). consumer 측은 자기 repo 의 `docs/orchestrator-communication-incidents.md` (별도 lifecycle, consumer-guide §1 cross-ref 의무).

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
- **keyword 확장 ratchet 의무** — Layer 3 trigger keyword 영역 확장 (예: "두루뭉술" / "막연히" 추가) 시 별도 ADR Amendment 의무 (사용자 burden 변화 영역 — Layer 3 가 사용자 발화 token detection 기반이므로 keyword 추가 = 사용자 표현 자유도 축소). ADR-058 §결정 5 sunset_justification 불요 (강화 방향 ratchet 정합) 단 별도 CFP carrier + Story §1 사용자 explicit 승인 의무.

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

ADR-059 = lane-agnostic protocol contract — lane 정보를 인자로 받는 일반 schema. 본 ADR-071 = lane 분기 영역 아님 (Orchestrator-user turn 자체는 모든 lane 진입 직전·직후·중간에 발생 — lane-agnostic 도 아니고 single-lane 도 아닌 별도 layer). 본 declare 가 미래 CodeReview / SecurityTest lane 의 debate 확장 (deferred CFP-C scope) 와 본 ADR 의 sibling 발의 가능성을 분리.

### §결정 10 — Scope out (별도 follow-up CFP)

CFP-612 §1 verbatim "Scope 가 아닌 것" + RequirementsPL §5.4 정합:

- **Layer 1 preamble mechanical lint** — 별도 follow-up CFP 분리 (본 Wave 5 = cognitive + persistence layer 만). 본 ADR effective 후 evidence-enforceable warning-tier entry 신설 carrier 가 follow-up CFP.
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

- **Layer 1 preamble mechanical lint** = 별도 follow-up CFP (Wave 5 §결정 10 scope out)
- **frame mode marker 형식** = playbook §3.14 본문 결정 영역
- **Layer 3 stem vs exact match** = playbook §3.14 본문 결정 영역
- **Layer 4 file rotate / archive** = playbook §3.14 본문 결정 영역

## §결정 12. DialogFidelityAgent external verifier auxiliary layer (Amendment 1, CFP-777)

### 12.1 결정 요약

Layer 1-4 = ADR-071 **§결정 3** 의 4-layer cognitive enum (preamble 의무 / declare 의무 / "추상" halt / N=1+M=5 incidents append) 골격 **보존 invariant**.

별개 §결정 family 분리 (5-element squash 회피):
- frame mode 4 step = ADR-071 **§결정 1** (4-step protocol — 사용자 요건 파악 / mental model 추정 / 1-sentence frame / forcing-function declare)
- sub-mechanism 2 종 = ADR-071 **§결정 4** (turn-final hook 부재 → cognitive substitute)
- Layer 4 영속 file = ADR-071 **§결정 6** (cross-Story incidents.md ledger Orchestrator monopoly)

DialogFidelityAgent = **additive auxiliary layer**, 신규 **5번째 cognitive layer 신설 금지** (§결정 3 의 4-layer cognitive enum scope 만, 다른 §결정 family 와 무관).

발화 entity (Orchestrator) 와 검증 entity (DialogFidelityAgent) **분리** — ADR-071 anchor 단락 (line 57) 가설 E (mechanism 만 codify, 본질 미codify 한계 — self-defeating trap) 다층 방어 채널 (mechanism scaffolding 강화 + 본질 anchor 동시 보존).

### 12.2 Mandate scope (read-only inspection only)

verifier-narrower-than-generator 패턴 강제:

| 항목 | scope |
|---|---|
| input | (a) 세션 개시 요건 (Story §1 immutable verbatim) + (b) 누적 결정/제약 ledger (Layer 4 incidents file verbatim row) + (c) 현 Orchestrator turn 출력 (SHA-256 hash-pinned verbatim) |
| output | `verify_result: enum<fidelity_ok \| drift_detected \| ledger_gap>` + `evidence_path[]` (non-empty when != ledger_gap) + `incident_row_match: {row_id, layer, criterion}` + `correction_action_hint: enum<rescan_ledger \| escalate_user \| self_correct \| no_action> \| null` |
| 추론 재실행 | **금지** (검증자 역설 회피, generator 역할 침범 금지) |

### 12.3 Layer 1-4 보존 invariant (ADR-071 §결정 3 의 4-layer cognitive enum scope)

| Layer (§결정 3 cognitive enum) | AS-IS | 본 Amendment 후 |
|---|---|---|
| Layer 1 (preamble 의무) | mechanical lint deferred (§결정 10 정합) | 보존, 무변경 |
| Layer 2 (declare 의무) | behavioral directive | 보존, 무변경 |
| Layer 3 ("추상" halt) | behavioral directive | 보존, 무변경 |
| Layer 4 (N=1 + M=5 incidents append) | Orchestrator monopoly write (§결정 6) | 보존, 무변경. DialogFidelityAgent read-only inspection only |

**신규 5번째 cognitive layer 신설 금지 invariant** (§결정 3 enum scope 만, 다른 §결정 family 와 무관): pattern_dimension 4 차원 enum closed (보고 형식 / 질문 자체 / sub-mechanism 2종 — §결정 4 carrier) 보존. verifier 도입 = mechanism (verification entity) 추가, §결정 3 cognitive layer count 변경 아님.

### 12.4 ADR-071 anchor 단락 line 57 가설 E 다층 방어 채널

`[verified — git show origin/main:docs/adr/ADR-071-orchestrator-user-dialog-convergence.md line 57 anchor 단락 verbatim]` ADR-071 anchor 단락 본문:
> "본 ADR 의 모든 §결정 ... 은 본질을 보조하는 scaffolding — mechanism 만 codify 하고 본질을 놓치면 가설 E (mechanical 규칙 자체 한계) 의 self-defeating trap"

본질 anchor = 발화 entity ≠ 검증 entity 분리 (Orchestrator self-check 만으로는 mechanical 규칙이 본질을 놓침). 가설 E location = **§결정 11 본문이 아닌 anchor 단락 line 57** (§결정 family 보다 상위 framing context).

**다층 방어 메커니즘**: 발화 entity (Orchestrator) ≠ 검증 entity (DialogFidelityAgent codeforge-pmo agent). mechanism scaffolding 강화 + 본질 anchor (entity 분리) 동시 보존. 4-layer mechanical defense (Change Plan CFP-777 §7.3):

| Layer | mitigation |
|---|---|
| M1 | `tools:` field read-only subset only `[Read, Grep, Glob, ToolSearch]` — Write/Edit/Bash/SendMessage/Agent 차단 (input integrity input scope 제한) |
| M2 | output schema closed enum (verify_result 3-value `fidelity_ok \| drift_detected \| ledger_gap` + correction_action_hint 4-value `rescan_ledger \| escalate_user \| self_correct \| no_action` + `null`) — narrative free-form 차단 (generator 영역 reasoning 재실행 차단 = M1 + M2 combined forcing function) |
| M3 | input contract SHA-256 hash-pinned (current_output_hash) — Orchestrator turn output verbatim 이 spawn 시점과 동일한지 확인 (input integrity verification only, reasoning re-execution 차단은 M1+M2 combined 위임) |
| ADR-070 §B final safety net | Orchestrator post-verify ground truth direct Read: evidence_path[] direct Read verify 의무, mismatch 시 verdict reject + tally |

### 12.5 Spawn anchor 3종 (ADR-039 §결정 2 inline whitelist 보존)

ADR-039 **§결정 2** Inline whitelist 4-entry (사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report) **보존 invariant**. 매 user-facing turn spawn 금지. (note: base ADR-071 §결정 11 본문이 ADR-039 §결정 7 을 인용한 self-error — 본 Amendment 는 §결정 2 정확 cite 채택.)

선별 anchor 3종:

| anchor | 발동 시점 |
|---|---|
| `post_user_turn` | 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / AskUserQuestion 직전) |
| `pre_architectpl_synthesis` | ArchitectPL synthesis 완료 직전 (Codex TP#2 augment) |
| `pre_fix_rootcause` | FIX 루프 root cause 판정 직전 (Codex TP#3 augment) |

자동 발동 hook 부재 (turn-final hook unavailable, ADR-039 §결정 9 deferred 영역 정합). Orchestrator 자율 채택 layer (behavioral directive).

### 12.6 Cross-ref (deputy 산출물 통합 anchor)

- **SecurityArch §7.1-§7.6** (Change Plan CFP-777 §7): trust boundary / threat (T1 tampering, T2 silent drift) / mitigation M1/M2/M3 / auth / audit
- **TestContractArch §8** (Change Plan CFP-777 §8): unit AC-U1/U2/U3 / integration 5 baseline incident catch / boundary AC-B1-B4 / stateful §8.5
- **DataMigrationArch §11** (Change Plan CFP-777 §11): 분기 A schema 무변경 / 5 baseline integrity invariants / ADR-079 KST timestamp display 정합
- **OpRiskArch §7.4** (Change Plan CFP-777 §7.4): DR (non-blocking + Story §14 outcome marker) / rate-limit (3-anchor only) / env (env=0 default) / sibling cross-repo (ADR-063 6-file atomic)

### 12.7 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment = **additive ratchet** (Layer 1-4 골격 보존, 검증 mechanism 만 추가). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격.

## §결정 13. DialogFidelityAgent spawn trigger 운영 정의 (Amendment 2, CFP-818)

### 13.1 결정 요약

Amendment 1 (§결정 12) 가 도입한 DialogFidelityAgent (cross-cutting read-only verifier, codeforge-pmo) 의 **spawn trigger 운영 정의** + ADR-039 inline whitelist 1번 entry **정합 명문화** + turn-shape edge × 3-anchor **12 cell 활성 표** 신설 + ADR-064 §결정 9 Q-3check **disjoint scope cross-ref**.

Story-2 (CFP-818) 채택 = **spawn-on-marker (closed 3-anchor)** — Anthropic Constitutional AI critique pattern (Bai et al. 2022) selective spawn 패턴 정합 + ADR-052 6 touchpoint precedent (codeforge 내부 precedent — 전수 아닌 6 touchpoint 만 활성) + verifier-narrower-than-generator forcing function (Epic CFP-761 spec § "근거 1" verbatim).

회피 대안:
- **spawn-everywhere** (전수 spawn, 매 user-facing turn) — cover 100% 단 30x overhead + verifier-narrower-than-generator 위반 (검증 범위 ≥ 생성 범위 시 검증자 역설). 회피.
- **gradient spawn** (사용자 turn 형태별 활성 비율) — 비율 정의 자체 추가 결정 영역 + 12 cell discrete 표 보다 mental model 복잡 + Story-3 effectiveness metric carrier 가 closed enum baseline 측정 후 확장 영역. 회피 (closed 3-enum + 별도 CFP 의무 — §13.6).

본 §결정 13 = additive 강화 (Layer 1-4 보존 + 5번째 cognitive layer 신설 금지 invariant 보존 + Inline whitelist 4-entry 보존 + Q-3check 7 anti-pattern 보존). §결정 12 family 정합 — 새 §결정 family 분리 (5-element squash 회피 패턴 정합).

### 13.2 3-anchor 발화 형태 매핑 표

§결정 12.5 의 3-anchor enum 의 운영 정의 (각 anchor 가 어떤 turn shape 직전 활성):

| anchor | 발동 시점 | 발화 형태 매핑 (UC) | Codex touchpoint dedup |
|---|---|---|---|
| `post_user_turn` | 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / `AskUserQuestion` 직전) | UC-1 (`AskUserQuestion` 발화 직전) / UC-2 (numbered list 또는 dialog format 발화 직전) / Layer 3 "추상" stem detect 직후 | 없음 (Codex 6 touchpoint 와 disjoint) |
| `pre_architectpl_synthesis` | ArchitectPL synthesis 완료 직전 (사용자 보고 발화 직전) | UC-3 (Orchestrator 가 ArchitectPL synthesis 결과 사용자 보고 발화 직전) | **Codex TP#2 (mandatory, [ADR-052](ADR-052-codex-proactive-check-touchpoints.md) Amendment 4) 와 동일 위치** — 양 verifier 활성 (EC-6 dedup) |
| `pre_fix_rootcause` | FIX 루프 root cause 판정 직전 (ArchitectPL 1차 진단 후 최종 판정 직전) | UC-4 (Orchestrator 가 FIX 루프 root cause 판정 직전) | **Codex TP#3 (FIX 2+ 감지 시) 와 동일 위치** — 양 verifier 활성 (EC-5 dedup) |

dedup 패턴 (EC-5/EC-6): 동일 위치 활성 시 — Codex = P0/P1 inline FIX mandatory (TP#2) / single-shot 검토 (TP#3) / DialogFidelityAgent = correction_action_hint 5-enum 권고. Orchestrator 가 양 verdict 통합 (verify-before-trust ADR-070 의무).

### 13.3 turn-shape edge × 3-anchor 12 cell 활성 표

[playbook §3.14 "Turn-shape derived defaults" 표](../orchestrator-playbook.md) 의 E9/E10/E11/E12 edge × 3-anchor cross-product 활성 매핑:

| anchor \ edge | E9 streaming token | E10 tool-call-only | E11 AskUserQuestion popup | E12 trivial answer |
|---|---|---|---|---|
| `post_user_turn` | **final flush 시 활성** (mid-stream spawn 금지 — idempotency) | **면제** (사용자 발화 직접 미발생) | **active** (popup 본문 자체가 dialog convergence anchor — popup option_text/body Layer 3 "추상" detect 영역) | **면제** (cost > benefit, trivial turn 3-criteria AND 충족 시 cognitive overhead 정당화 불가) |
| `pre_architectpl_synthesis` | active (edge-independent — Story 1회 발동, ArchitectPL synthesis 완료 직전 fixed timepoint) | active | active | active |
| `pre_fix_rootcause` | active (edge-independent — FIX 발동 시점 fixed, ADR-067 FIX 3 카운터 범위 안 ≤ 3/Story) | active | active | active |

cell 값 enum: `active` (spawn 의무) / `면제` (spawn 금지) / `final flush 시 활성` (E9 streaming 의 final flush 단계 1회만 spawn — mid-stream 금지).

12 cell 모두 derived default 값 (Story §5.5 OQ-3 채택, 사실 측 분류 — 본 §결정 3 (4 layer) + playbook §3.14 SSOT 정합).

**E11 popup × `post_user_turn` 결정 근거**: popup 본문 자체가 dialog convergence anchor — Layer 1 가시적 preamble (= "AskUserQuestion 으로 답해주실 것: ..." 1 문장, playbook §3.14 E11 derived default) 의 발화가 곧 dialog turn, popup option_text 안 Layer 3 "추상" stem detect 영역 = active 의무.

empirical-source annotation (ADR-068 Amendment 1 I-5 dimensional empirical grounding):
- **latency**: `[hypothesis]` subagent one-shot ~ 2-10 sec (codeforge telemetry 부재 — Story-3 effectiveness metric carrier 영역)
- **cost**: `[hypothesis]` read-only inspection ~ 5-15k input + 0.5-2k output (model tier `inherit` Story-1 [ADR-042 Amendment 6](ADR-042-agent-model-selection-policy.md))
- **count**: `[verified]` max upper bound ≤ 34/Story (`post_user_turn` ≤ 30 — `AskUserQuestion` / numbered list / 추상-detect trigger subset / `pre_architectpl_synthesis` 1 + `pre_fix_rootcause` ≤ 3 — [ADR-067 §결정 3](ADR-067-fix-ledger-implementability-escalation.md) FIX 3 카운터 정합)

### 13.4 ADR-039 Inline whitelist 1번 entry 정합 명문화

[ADR-039 §결정 2](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Inline whitelist 4-entry **closed enumeration** 보존 (5번째 entry 신설 금지 invariant).

DialogFidelityAgent verifier subagent spawn = 1번 entry (사용자 dialog) **scope 안** cognitive 보강:
- 사용자 dialog **본 발화** = inline 유지 (Inline whitelist 1번 entry 원래 mandate)
- 본 발화 **직전/직후** verifier subagent spawn = ADR-039 §결정 1 default subagent spawn 정합 (subagent 형태 자체는 inline 영역 외 — 정상 default 적용)

5번째 entry 신설 X — 새 카테고리 enumeration 추가 아님, 기존 1번 entry 의 "cognitive 보강 채널" 1 문장 명문화. closed enumeration 보존 invariant + 5번째 entry 신설 시 Amendment 의무 invariant 양 보존.

ADR-039 §결정 2 표 row 1 Mechanism rationale 컬럼이 본 정합 1 문장 verbatim 명시 (CFP-818 Phase 1 PR Edit).

### 13.5 ADR-064 §결정 9 Q-3check disjoint scope cross-ref

[ADR-064 §결정 9](ADR-064-decision-principle-mandate.md) Question quality 3-check = **Orchestrator self-check** (proposing-time + stop-time).

DialogFidelityAgent = **외부 verifier** (발화 entity ≠ 검증 entity 분리, self-referential trap 회피 — 본 §결정 12 anchor 단락 가설 E 다층 방어 메커니즘 정합).

disjoint scope — 양자 cross-cutting 보강:

| 영역 | 3-check cover | DialogFidelityAgent cover |
|---|---|---|
| turn-internal cognitive frame (1-option 묻기 / Implementation detail 묻기 / Confirm-of-confirm 등 7 anti-pattern P1-P7) | ✅ | — |
| 누적 결정 ledger drift (Layer 4 영속 file `docs/orchestrator-communication-incidents.md` row 일관성) | — | ✅ |
| 세션 개시 요건 일관성 (Story §1 immutable verbatim vs 현 turn 출력) | — | ✅ |
| 가치 판단 vs 사실 판단 분류 self-check (§결정 9 Question quality 3-check 1번 항목) | ✅ | — |
| derived default 자명성 self-check (§결정 9 Question quality 3-check 2번 항목) | ✅ | — |

양자 동시 활성 (3-check 의 anti-pattern 7종 + DialogFidelityAgent output 4-enum) 이 dialog fidelity 보장 강화 forcing function. ADR-064 §결정 9 단락 말미가 본 disjoint scope 1 단락 verbatim 명시 (CFP-818 Phase 1 PR Edit).

### 13.6 closed enum 확장 시 별도 CFP 의무 codification

3-anchor enum (`post_user_turn` / `pre_architectpl_synthesis` / `pre_fix_rootcause`) = **closed enumeration**. 확장 후보 3종 발생 시 (Story §5.4 IA-4 정합):

- `pre_lane_spawn`: 매 lane spawn 직전 verifier dispatch
- `pre_phase_transition`: phase label transition 직전 (요구사항 → 설계 / 설계 → 설계-리뷰 등)
- `pre_pause_decision`: ADR-067 §결정 3 Pause/Resume 결정 직전

→ **별도 CFP 신설 의무** (사용자 burden 변화 영역 — spawn frequency 증가 + ROI 측정 baseline 갱신 의무). ADR-064 §결정 7 top-down ratchet 정합 (강화 방향 only) + ADR-058 §결정 5 sunset_justification 의무 (anchor 축소 시).

본 §13.6 codification = scope creep 차단 forcing function (Story §5.4 IA-4 + §결정 12 5번째 cognitive layer 신설 금지 invariant pattern 정합).

### 13.7 sunset_justification: null (additive ratchet, §결정 12 family 정합)

본 Amendment 2 = **additive 강화** (Layer 1-4 보존 + Inline whitelist 4-entry 보존 + Q-3check 7 anti-pattern 보존 + closed 3-anchor 보존). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§결정 12 family pattern 정합).

## §결정 14. DialogFidelityAgent effectiveness measurement wiring (Amendment 3, CFP-833)

> Epic CFP-761 Story-3 (마지막 Story — closing-the-loop). carrier: CFP-833, issue https://github.com/mclayer/plugin-codeforge/issues/833. additive 강화 — Layer 1-4 + DialogFidelityAgent auxiliary layer 보존, measurement layer 추가만.

### 14.1 WHY (ADR-058 §결정 3 측정성 self-application)

Story-1 (CFP-777) 이 DialogFidelityAgent 를 신설하고 Story-2 (CFP-818) 가 spawn trigger 를 운영 정의했다. 그러나 **그 verifier 가 실제로 맥락 fidelity 손실을 줄였는지 정량 측정하지 않으면 ADR-071 이 측정 기준 없는 영구 안전망으로 굳는다** (ADR-058 §결정 3 측정성 forcing function 미적용 상태). 본 §결정 14 = ADR-058 의 측정성 mandate 를 DialogFidelityAgent 효과에 wiring 하는 self-application — verifier 자신이 ADR-058 §결정 3 forcing function 의 적용 대상이 된다 (verifier 도 측정 없이 영구화되면 안 됨).

### 14.2 measurement SSOT 분리 (`## 해소 기준` 무변경 invariant)

ADR-071 = `is_transitional: false` permanent governance → `## 해소 기준` = "N/A — permanent policy" **무변경** (permanent governance recursive sunset 회피 invariant — 측정 metric 을 `## 해소 기준` 섹션 자체에 적지 않는다). measurement 실체 = 분리된 2 SSOT:

1. **본 amendment_log Amendment 3** (`sunset_justification: null` 강화 ratchet — Amendment 1/2 family pattern)
2. **`docs/evidence-checks-registry.yaml` `dialog-fidelity-effect` warning-tier entry** (`owner_adr: ADR-071` / `carrier_adr: ADR-060`) = metric 의 mechanical SSOT

ADR 본문 = cross-ref only (precedent `rate-limit-fallback-rate` ↔ ADR-057 §결정 2 sunset gate wiring 동형 — registry entry 가 measurement SSOT, ADR 본문은 reference).

### 14.3 metric 정의 + proxy signal qualification (Codex TP#2 P1 정합)

metric = **incident append-rate delta (proxy signal — not causal effectiveness measure)**. DialogFidelityAgent 도입 (Story-1 merge `577f96f`, 2026-05-17 KST) 전후 Layer 4 incident realtime detect row append rate A-B baseline delta. 정량 3-tuple (metric/who/how) + sample insufficient sentinel + baseline normalization 의 SSOT = `dialog-fidelity-effect` registry entry `description` (Change Plan CFP-833 §3.1 cross-ref).

**proxy 한계 명시 (over-claim 차단 — ADR-058 §결정 3 metric 정직성 정합)**: `before` = Story-0 retroactive backfill marker row / `after` = Story-1 merge 이후 realtime detect row → 두 collection mode 가 상이하므로 delta 는 DialogFidelityAgent 효과뿐 아니라 instrumentation mode change / backfill completeness / reviewer detection behavior 변화도 반영할 수 있다. 따라서 본 metric 은 **advisory operational signal only — 효과 "판정" 이 아니라 측정 "신호"** (Story §5.4 가정 2 + EC-3 정합). sunset 판정 자체 (DialogFidelityAgent archive / 강화 amendment) 는 별도 후속 carrier (precedent `rate-limit-fallback-rate` 의 `kpi_dashboard_3month_window_evidence` 도 독립 carrier).

### 14.4 strengthening ratchet 정합 (sunset_justification: null 근거)

measurement wiring = **강화 방향** (측정성 forcing function 도입 = ADR-058 carrier WHY 동형). ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification ratchet 차단 정합 — `sunset_justification: null` 적격 (Amendment 1 §12.7 / Amendment 2 §13.7 family pattern). additive 강화: Layer 1-4 + DialogFidelityAgent auxiliary 보존, measurement layer 추가만. `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

### 14.5 Epic plan Task 4 invariant 5 deviation (precedent override)

Epic plan (`mclayer/codeforge-internal-docs:wrapper/plans/2026-05-16-dialog-fidelity-agent-epic.md` Task 4 invariant 5) = "label-registry MINOR — `hotfix-bypass:dialog-fidelity` 1 entry + frontmatter version MINOR bump". **본 Story-3 는 이 invariant 5 를 deviation 한다**:

- **deviation 사유**: Epic plan invariant 5 는 evidence-check entry 가 static-lint (PR block) 임을 가정한 산물. 본 metric pattern = runtime cron measurement (precedent `rate-limit-fallback-rate` 동형 — advisory warning tier, PR block 안 함) → bypass label 의 의미 (PR block conditional skip) 부적용. label 신설 시 dead label 발생.
- **precedence**: ADR-064 §결정 10 = normative 우선순위 ADR > planning doc. Epic plan = planning artifact (normative SSOT 아님). precedent (`rate-limit-fallback-rate`) + ADR-060 §결정 3 (warning tier bypass 의미) 가 Epic plan invariant 5 보다 우선.
- **사용자 확정**: 2026-05-17 KST AskUserQuestion — OQ-3 = precedent 우선, label-registry MINOR 면제 명시 결정.
- **EPIC-RESULTS cross-ref 의무**: Epic close 시 `EPIC-RESULTS-CFP-761` 에 본 deviation 기록 의무 (PMOAgent Epic close 영역, Story §11 회고 cross-ref). 본 §14.5 + Change Plan CFP-833 §3.7 = SSOT 이중 anchor.

## §결정 15. Conversational reporting frequency suppression contract (Amendment 4, CFP-851)

> Story-1 (CFP-777) DialogFidelityAgent 도입 + Story-2 (CFP-818) spawn trigger 운영 정의 + Story-3 (CFP-833) effectiveness measurement wiring 이후 **누적 governance gap** — Orchestrator ↔ user dialog 의 **말 거는 시점·빈도** (frequency / timing) 가 SSOT 미codified 상태. carrier: CFP-851, issue https://github.com/mclayer/plugin-codeforge/issues/851. additive 강화 — Layer 1-4 + DialogFidelityAgent auxiliary + §결정 2(c) richness 보존, frequency 축소 layer 추가만.

### 15.1 본질 anchor — frequency vs richness 분리 (가장 중요한 invariant)

본 Amendment 4 가 좁히는 것은 Orchestrator 가 사용자에게 **말 거는 횟수·시점** (frequency / timing) 만이다. **말할 때의 풍부함은 보존된다.** 두 축 분리 invariant:

| 축 | 본 Amendment 4 의 작용 | SSOT |
|---|---|---|
| **frequency / timing** (말 거는 횟수·시점) | 좁힘 — 3 touchpoint closed enumeration (§15.2) | 본 §결정 15 신설 |
| **richness** (말할 때의 풍부함 — 길이 / 배경 / 평이 번역) | 보존 — 무약화 | §결정 2(c) verbatim 유지 (3 줄 제약 거부 · 길이 자유 · 배경 포함) |

이 분리가 본 Amendment 의 핵심 invariant 이며 ADR-058 §결정 5 약화 차단 (`sunset_justification: null`) 의 근거다. 3 touchpoint 발화 시 Layer 1 가시적 preamble + Layer 2 자기 declare + §결정 2(c) richness 그대로 적용 — turn-shape edge (E9/E10/E11/E12) derived default 도 무변경 (playbook §3.14 본문 결정 영역).

**Verifiable outcome surface 경계** (RE 안전판): 본 Amendment 가 억제하는 것은 **"how" (구현 과정)** 의 중간 보고이고, 억제하지 않는 것은 **"what" (요구 명세)** 의 disambiguation. 사용자가 선언한 결과가 모호하여 잘못 추측 시 rollback 비용이 큰 경우, 그 명세를 확인하는 것은 **요구사항 disambiguation** 이며 억제 대상이 아니다 (touchpoint (a)). 전면 보고 / 질문 억제 = 검증되지 않은 한쪽 극단 (wrong-dataset risk — requirements ambiguity 미해소 → 끝까지 wrong deliverable → rollback 비용 ≫ 보고 비용). SI 아웃소싱 / SQL 개발자 비유 (Story §1 사용자 directive verbatim) 도 동일 구조 — 고객은 "어떻게 뽑았는지" 의 중간 보고 불요지만 "무엇을 뽑을지" 의 명세는 ambiguous 시 SI 가 확인한다.

### 15.2 3 touchpoint closed enumeration

Orchestrator 의 사용자 발화 허용 시점 = closed enumeration 3 종. 그 외 진행·중간 결정·근거·중간 결과는 **산출물** (Story / change-plan / ADR / PR / TodoWrite panel) 전용 기록.

| touchpoint | 발화 사유 | 분류 |
|---|---|---|
| **(a) 결과-명세 확인** | 사용자가 선언한 결과 자체가 모호 + 잘못 추측 시 rollback 비싼 경우 | 가치 / 명세 판단 (§결정 5 결정 트리 — 모호 → 가치 측 분류, `AskUserQuestion` 의무) |
| **(b) 사용자만 풀 수 있는 차단** | 인증·권한 등 codeforge 자체 해소 불가, 사용자 행동 필요 | 차단 해소 (ADR-039 inline whitelist 1번 entry scope 안 — 사용자 dialog) |
| **(c) 최종 완료 보고 1회** | 요청한 작업 단위 전체 완료 | 산출물 = 최종 결과 자체 (ADR-039 inline whitelist 4번 entry scope 안 — Status report) |

**산출물 channel enumeration** (대화 turn 아닌 정상 기록 경로):
- `docs/stories/<KEY>.md` (Story file — §0 Live Progress / §9 / §10 FIX Ledger / §14 Lane Evidence)
- `docs/change-plans/<slug>.md` (Change Plan)
- `docs/adr/ADR-NNN-<slug>.md` (ADR)
- PR description / GitHub Issue comment
- TodoWrite panel (ADR-038 progress visualization — 산출물 channel, 대화 turn 아님)

### 15.3 무약화 invariant — §결정 2(c) 와의 정합

`[verified — Read ADR-071 §결정 2(c) lines 142-147]` 기존 §결정 2(c) "sub-agent 결과의 사용자용 평이 번역" = `3 줄 제약 명시적 거부 — 길이 자유` + `"왜 / trade-off / 걸려있는 것" 배경 포함`. 본 Amendment 4 는 이 정책을 **무약화** — 3 touchpoint 발화 시 Layer 1/2 preamble·declare + §결정 2(c) 풍부함 그대로 적용된다.

| Layer / 정책 | 본 Amendment 4 후 |
|---|---|
| Layer 1 가시적 preamble (§결정 3) | 보존 — 3 touchpoint 발화 시 매 turn 맨 윗줄 "지금 답해주실 것" 1 문장 (turn-shape edge derived default 무변경) |
| Layer 2 자기 declare (§결정 3) | 보존 — 3 touchpoint 발화 시 매 turn 맨 아랫줄 "주의한 가설" 1 줄 (E11 popup 면제 derived default 무변경) |
| Layer 3 "추상" halt (§결정 3) | 보존 — 모든 user-facing turn 에서 active |
| Layer 4 누적 detection (§결정 3 / §결정 6) | 보존 — cross-Story 영속 file append-only Orchestrator monopoly |
| §결정 2(c) richness (3 줄 제약 거부 + 배경 포함) | 보존 — 3 touchpoint 발화 시 그대로 적용 |
| Sub-mechanism 1/2 (§결정 4) | 보존 — halt 후 재작성 시 "이전과 다르게 한 점" + 4 차원 enum 강제 전환 |
| DialogFidelityAgent auxiliary (§결정 12) | 보존 — read-only inspection only, generator 역할 침범 금지 |
| DialogFidelityAgent 3-anchor spawn (§결정 13) | 보존 — closed 3-anchor enum 무변경 |
| §결정 14 measurement (CFP-833) | 보존 — incident append-rate delta proxy signal |

**5번째 cognitive layer 신설 금지 invariant (§결정 12 carrier) 와의 정합**: 본 §결정 15 = mechanism (말 거는 시점 closed enumeration) 추가, §결정 3 cognitive layer count 변경 아님 (§결정 12 §12.3 family pattern 정합 — verifier 도입 = mechanism 추가, cognitive layer 신설 아님 동형).

### 15.4 ADR-039 inline whitelist 정합 — closed 4-entry 보존

[ADR-039 §결정 2](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Inline whitelist 4-entry **closed enumeration** 보존 invariant. 3 touchpoint 는 기존 entry scope 안에서 작동 — 신규 entry 신설 0.

| touchpoint | ADR-039 inline whitelist entry |
|---|---|
| (a) 결과-명세 확인 | 1번 entry (사용자 dialog) — `AskUserQuestion` 발화 |
| (b) 사용자만 풀 수 있는 차단 | 1번 entry (사용자 dialog) — 사용자 행동 요청 발화 |
| (c) 최종 완료 보고 1회 | 4번 entry (Status report) — 작업 완료 통지 |

**5번째 entry 신설 X** — 새 카테고리 enumeration 추가 아님, 기존 1번·4번 entry 의 frequency 영역 명문화. closed enumeration 보존 invariant + 5번째 entry 신설 시 Amendment 의무 invariant 양 보존 (§결정 13.4 ADR-039 정합 명문화 family pattern 정합).

### 15.5 closed-enum 확장 패턴 (§결정 13.6 정합)

3 touchpoint enum = **closed enumeration**. 확장 후보 발생 시 (예: "사용자 explicit 과정 설명 요청" / "FIX 3 회 escalation 시점" / "보안 incident detect 시점") → **별도 CFP 신설 의무** (사용자 burden 변화 영역 — 발화 frequency 증가).

| 룰 | 적용 |
|---|---|
| ADR-064 §결정 7 top-down ratchet | 강화 방향 only (touchpoint 추가 = 발화 빈도 증가 강화 ratchet) |
| ADR-058 §결정 5 sunset_justification | touchpoint 축소 시 의무 (frequency 축소 = 사용자 burden 추가 변화 영역) |
| Story §1 사용자 explicit 승인 | 별도 CFP 의 Story §1 verbatim 명시 의무 (CFP-851 §1 declared outcome 1번 항목 verbatim pattern 정합) |

본 §15.5 codification = scope creep 차단 forcing function (§결정 13.6 closed-enum 확장 패턴 verbatim 적용 — 본 ADR 안 3번째 closed enumeration 인스턴스: 3-anchor enum (§13.6) / 4 차원 enum (§4) / 3 touchpoint enum (§15.5)).

### 15.6 measurement gap declare — behavioral directive only

본 §결정 15 = **behavioral directive only** (mechanical lint 부재). 3 touchpoint 외 발화 자동 감지 / 억제-induced rework 측정 채널 = 별도 follow-up CFP scope (ADR-071 §결정 10 "Layer 1 preamble mechanical lint = 별도 follow-up CFP" 패턴 정합 + §결정 14 measurement wiring precedent — advisory operational signal, blocking 승격 의미 부적용).

| 측정 axis | 본 Amendment 4 scope | 별도 follow-up CFP scope |
|---|---|---|
| 3 touchpoint 외 발화 detect | — | mechanical lint (별도 CFP, advisory warning tier 첫 도입 시 evidence-checks-registry entry 추가) |
| 억제-induced rework 빈도 | — | runtime cron metric (precedent `dialog-fidelity-effect` / `rate-limit-fallback-rate` 동형) |
| 사용자 explicit 과정 설명 요청 후 발화 frequency | — | 별도 CFP scope (확장 candidate, §15.5 정합) |

**ADR-058 §결정 3 측정성 self-application 정합**: 본 Amendment 가 measurement wiring 없이 영구화되면 안 됨을 인지. 단 measurement 자체 = behavioral baseline 누적 후 별도 CFP carrier 영역 — Amendment 4 effective 후 incident pattern (Layer 4 file row pattern_dimension="보고 형식") + PMOAgent retro user feedback 누적 가 baseline. §결정 14 measurement (CFP-833) precedent 동형 — measurement entry 가 ADR 본문 외부 (registry yaml) 에서 wiring.

### 15.7 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 4 = **additive 강화** (Layer 1-4 + DialogFidelityAgent auxiliary + §결정 2(c) richness + Inline whitelist 4-entry + 3-anchor enum + 4 차원 enum 모두 보존, frequency 축소 layer 추가만). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§12.7 / §13.7 / §14.4 family pattern 정합 — Amendment 1/2/3/4 모두 동일).

## §결정 16. Natural-language action trigger lookup table (Amendment 5, CFP-1104)

> CFP-1104 carrier 사용자 directive verbatim: Turn 1 "codeforge upgrade" / Turn 2 "항상 모호하다고 그러는데 codeforge를 통해 upgrade 절차에 대해 정립해둔게 있을거다. codeforge plugin에 반영해라" / Turn 3 "mctrader-hub와 mctrader-data에서 codeforge upgrade를 요구하면 애매하네요? 이런 소리 말고 바로 수행할 수 있도록". 본 §결정 16 = ADR-076 invariant `user_decision_branches: 0` 을 dialog 진입 단계로 확장 carrier — base ADR-071 §결정 5 사실/가치 분리 원칙의 dialog reflex (AskUserQuestion "어떤 upgrade?" "어느 채널?") 차단 first applied case.

### 16.1 본질 anchor

사용자가 IDE 에서 wrapper-managed-manifest.json 을 열어 둔 상태에서 단어 `codeforge upgrade` 하나만 발화 시 orchestrator 는 즉시 cwd + consumer overlay project.yaml + ADR-076 derived default 로 추론·실행한다. derived default 자명 (ADR-076 invariant + cwd 자동 / overlay channel resolve / dry-run → apply 자동 reflex) 이므로 발화 금지 — ADR-064 §결정 7 + ADR-071 §결정 5 가치/사실 분리 + ADR-039 inline whitelist 1번 entry "사용자 dialog 허용 영역이지만 derived default 자명 시 발화 금지" cognitive 강화 carrier.

### 16.2 Closed enumeration — 1 entry

| Trigger token (regex, case-insensitive) | Action |
|---|---|
| `\b(codeforge\s+upgrade\|codeforge\s+업그레이드)\b` | `scripts/codeforge-upgrade.sh` invocation per ADR-076 §결정 5 (§16.3 7 차원 derived default 자동 적용) |

본 lookup table = **closed enumeration**. 2번째 trigger token 확장 후보 (예: `codeforge rollback` / `codeforge family upgrade` / `codeforge plan` 등) 발생 시:

| 룰 | 적용 |
|---|---|
| ADR-064 §결정 7 top-down ratchet | 강화 방향 only (trigger token 추가 = 자율 reflex 영역 확장 강화 ratchet) |
| ADR-058 §결정 5 sunset_justification | trigger token 회수 시 의무 (사용자 burden 영역 — automatic reflex 가 dialog reflex 로 후퇴) |
| Story §1 사용자 explicit 승인 | 별도 CFP 의 Story §1 verbatim 명시 의무 (CFP-1104 §1 declared outcome verbatim pattern 정합) |
| SecurityArch consult | trust boundary 영역 — closed enum 확장 시 security review 의무 (ADR-039 entry 1 derived default 자명성 검토 의무, 의도 외 명령 실행 위험 평가) |

본 §16.2 codification = ADR 안 4번째 closed enumeration 인스턴스: 3-anchor enum (§13.6) / 4 차원 enum (§4) / 3 touchpoint enum (§15.5) / **trigger table (§16.2)**. §15.5 codify pattern verbatim 적용 — scope creep 차단 forcing function.

### 16.3 Derived default 7 차원 (CFP-1104 §5 verbatim)

orchestrator 가 사용자 발화 token detect 시 다음 7 차원 default 자동 적용. 사용자 정정 의무 (dialog reflex 차단 — Layer 1 preamble "발화하신 'codeforge upgrade' → 다음 default 로 즉시 수행" 1 문장 자기 발화만 의무, AskUserQuestion 0):

| 차원 | derived default | 근거 |
|---|---|---|
| trigger phrase | regex `\b(codeforge\s+upgrade\|codeforge\s+업그레이드)\b` (case-insensitive, 한글 변형 포함) | RequirementsAnalyst Edge Case + lint pattern 정합 (CFP-1104 §5) |
| repo | cwd 자동 주입 (`--repo $(pwd)`) | Researcher Unknown #3 해소 (CFP-1104 §5) |
| mode | dry-run 자동 → evidence 자동 verify → apply 자동 (사용자 확인 분기 0) | ADR-076 invariant + MCT-202 자율 full-run |
| channel | consumer overlay `.claude/_overlay/project.yaml::codeforge.channel.tier` resolve → fallback `"stable"` | ADR-076 v1.7 (CFP-906) |
| scope | 단일 codeforge plugin (default). 사용자가 "family" / "7-plugin" / "전체" 명시 시만 `atomic-upgrade-7-plugins.sh` | Researcher Unknown #2 — 단어 그대로 해석 |
| dirty tree | abort + 사용자 보고 (safe direction). `--force-dirty` opt-in flag 별 follow-up | Researcher Unknown #3 + InfraOperationalArch §7.4.5 env containment consult |
| 실패 처리 | dry-run 실패 → abort + 사실 보고 / apply 실패 → 자동 rollback + 사실 보고 + 사용자 정정 의무 | ADR-076 §결정 3 snapshot/rollback |

### 16.4 ADR-076 invariant carrier 명문화

ADR-076 invariant `user_decision_branches: 0` (Epic CFP-699 §1 WHY "0 자리" verbatim, ADR-076 line 177/200 명시) = **CLI argument fix 단계** scope 명시. 본 §결정 16 = 동일 invariant 를 **dialog 진입 단계** 로 확장 carrier — 사용자 발화 → orchestrator 추론 → CLI invocation 사이 dialog reflex (AskUserQuestion / "어떤 ~?" / "어느 ~?") 차단.

- 두 단계 disjoint scope: ADR-076 = CLI argument 결정 분기 / 본 §결정 16 = 자연어 발화 → CLI mapping 결정 분기
- 동일 invariant 표현 ("결정 분기 0") 이지만 layer 다름 (CLI vs dialog) — 두 ADR carrier 의 합집합 = end-to-end "결정 분기 0"

### 16.5 ADR-039 inline whitelist 1번 entry 정합 명문화

[ADR-039 §결정 2](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Inline whitelist 4-entry **closed enumeration** 보존 invariant. 본 §결정 16 의 dialog reflex 차단은 기존 1번 entry "사용자 dialog 허용 영역" scope 안에서 작동 — 신규 entry 신설 0.

**구체 적용**: 사용자 token detect 시 Orchestrator inline 발화 = 1번 entry scope 안. 단 발화 내용 = derived default declare 1 문장 (Layer 1 preamble) + `scripts/codeforge-upgrade.sh` 즉시 실행 (E10 tool-call-only edge, AskUserQuestion 0). 발화 자체 차단 아님 — **dialog reflex (AskUserQuestion / 모호함 호소 / 옵션 dump) 차단** 만.

**5번째 entry 신설 X** — 새 카테고리 enumeration 추가 아님, 기존 1번 entry 의 "derived default 자명 시 발화 금지" 1 문장 명문화 (§결정 11 family pattern 정합).

### 16.6 closed-enum 확장 패턴 (§결정 13.6 + §15.5 정합)

본 §16.2 trigger table = **closed enumeration** (1 entry). 확장 후보 발생 시:

| 룰 | 적용 |
|---|---|
| ADR-064 §결정 7 top-down ratchet | 강화 방향 only (trigger token 추가 = 자율 reflex 영역 확장) |
| ADR-058 §결정 5 sunset_justification | trigger token 회수 시 의무 (사용자 burden 영역) |
| Story §1 사용자 explicit 승인 | 별도 CFP 의 Story §1 verbatim 명시 의무 |
| SecurityArch consult | trust boundary 영역 — 의도 외 명령 실행 위험 평가 의무 |

본 §16.6 codification = §결정 13.6 + §15.5 closed-enum 확장 패턴 family pattern 정합 — 본 ADR 안 4번째 closed enumeration 인스턴스 (3-anchor enum (§13.6) / 4 차원 enum (§4) / 3 touchpoint enum (§15.5) / **trigger table (§16.2)**).

### 16.7 measurement gap declare — behavioral directive only

본 §결정 16 = **behavioral directive only** (mechanical lint 부재). orchestrator 자연어 token detect 자체의 false negative (token detect 실패 → AskUserQuestion 발화) / false positive (의도 외 token match → 잘못된 upgrade 실행) 자동 감지 채널 = 별도 follow-up CFP scope (ADR-071 §결정 10 "Layer 1 preamble mechanical lint = 별도 follow-up CFP" + §결정 14 measurement wiring precedent + §결정 15.6 measurement gap declare 패턴 정합 — advisory operational signal, blocking 승격 의미 부적용).

| 측정 axis | 본 Amendment 5 scope | 별도 follow-up CFP scope |
|---|---|---|
| token detect false negative (AskUserQuestion 발화 회귀) | — | runtime cron metric (precedent `dialog-fidelity-effect` 동형) |
| token detect false positive (의도 외 명령 실행) | — | SecurityArch consult mandate + audit log (precedent `rate-limit-fallback-rate` 동형) |
| dirty tree abort 정확성 | — | regression test (별 CFP scope) |

**ADR-058 §결정 3 측정성 self-application 정합**: 본 Amendment 5 가 measurement wiring 없이 영구화되면 안 됨을 인지. 단 measurement 자체 = behavioral baseline 누적 후 별도 CFP carrier 영역 — Amendment 5 effective 후 PMOAgent retro user feedback (token detect 회귀 incident) 누적 가 baseline. §결정 14 measurement (CFP-833) precedent 동형 — measurement entry 가 ADR 본문 외부 (registry yaml) 에서 wiring.

### 16.8 sunset_justification: null (ADR-058 §결정 5 정합)

본 Amendment 5 = **additive 강화** (Layer 1-4 + DialogFidelityAgent auxiliary + §결정 2(c) richness + Inline whitelist 4-entry + 3-anchor enum + 4 차원 enum + 3 touchpoint enum 모두 보존, dialog reflex 차단 layer 추가만). 강화 방향 only — `is_transitional: false` 보존, ADR-058 §결정 5 약화 차단 영역 미적용.

`sunset_justification: null` 적격 (§12.7 / §13.7 / §14.4 / §15.7 family pattern 정합 — Amendment 1/2/3/4/5 모두 동일).

## self-application top-down ratchet

본 ADR amendment 는 [ADR-064 §결정 7](ADR-064-decision-principle-mandate.md) top-down ratchet 정합 — 강화 방향만 허용 (scope 확장 / 강도 강화). 약화 방향 (`is_transitional: false → true` 다운그레이드 / 4 layer 축소 / 3 memory entry mapping 회수 / Sub-mechanism 2 차원 enum 축소 / **3 touchpoint enum 축소 — §결정 15 Amendment 4** / **trigger table 회수 — §결정 16 Amendment 5** / **§결정 2(c) richness 약화 — frequency 축소 ≠ richness 축소 invariant 위반**) 은 [ADR-058 §결정 5](ADR-058-adr-sunset-criteria-mandate.md) `sunset_justification` 의무로 차단. 본 ADR-071 = ADR-064 ratchet 의 직접 carrier (mechanical version 승격 + scope 확장 = strict superset). Amendment 1/2/3/4/5 = `sunset_justification: null` family pattern.

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
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — declarative reconciliation upgrade (Amendment 5 — invariant `user_decision_branches: 0` dialog 단계 enforcement carrier)
- [ADR-045](ADR-054-doc-only-story-fast-path.md) — doc-only fast-path (Amendment 5 — Story 분류 정합)
- [CLAUDE.md](../../CLAUDE.md) — cross-ref 1-2 줄 (320 cap compression 정합)
- [docs/orchestrator-playbook.md](../orchestrator-playbook.md) — §3.14 frame + 4 layer + sub-mechanism 본문 SSOT
- [docs/orchestrator-communication-incidents.md](../orchestrator-communication-incidents.md) — Layer 4 영속 file
- [skills/user-dialog-mode/SKILL.md](../../skills/user-dialog-mode/SKILL.md) — frame mode + 4 layer lookup table skill
- [CFP-612](https://github.com/mclayer/plugin-codeforge/issues/612) — carrier Issue
- [CFP-525](https://github.com/mclayer/plugin-codeforge/issues/525) — ancestor Epic (closed)
- [CFP-1104](https://github.com/mclayer/plugin-codeforge/issues/1104) — Amendment 5 carrier Issue (natural-language action trigger lookup table)
- [CFP-582](https://github.com/mclayer/plugin-codeforge/issues/589) — sibling (agent ↔ agent domain, conceptual cross-ref)
