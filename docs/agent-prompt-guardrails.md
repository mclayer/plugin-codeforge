---
title: Agent prompt guardrails SSOT
status: Active
owner: codeforge-wrapper
related_cfp:
  - CFP-1470  # B7 carrier of Epic CFP-1353 FU sweep
related_adrs:
  - ADR-082   # write-time self-write verification mandate (carrier-source citation invariant)
  - ADR-039   # Orchestrator subagent default for modification work
  - ADR-071   # Orchestrator user-dialog convergence (USER-UTTERANCE-VERBATIM block lineage)
last_updated_kst: "2026-05-24"
---

# Agent prompt guardrails SSOT

본 문서 = Orchestrator 가 codeforge family agent (PL / Worker / Deputy / SubAgent / Cross-cutting)
spawn 시 prompt 안에 carrier source citation 으로 사용자 발화를 첨부할 때 적용하는
**FIX-only directive** + **re-interpretation 차단** invariant SSOT.

Wave 1 = **declaration-only** (mechanical enforce 부재, agent file 변경 0). mechanical wire =
별 sub-CFP carrier (예: spawn prompt lint heuristic — `[USER-UTTERANCE-VERBATIM]` block
존재 시 closing marker `[END USER-UTTERANCE]` 필수 + scope-redirect 어휘 grep ban).

## 결정 0 (배경 / 동기)

CFP-1353 Pattern A "chief author self-attest false claim" pattern_count 3 reach Mandatory
escalation (ADR-045 §D-9) lineage 중 Pattern A-2 = **InfraEng FIX iter 1 false self-attest**
`tests_passed: "19/19 bats GREEN"` vs actual `10/27 (17 FAIL)`. 근본 원인 분석 중 발견:

- Orchestrator 가 agent 를 spawn 할 때 사용자 발화를 prompt 본문에 carrier source 로 첨부.
- agent (특히 PL tier) 가 이를 "신규 요구사항" 으로 **re-interpret** 하여 scope 를 자체 확장.
- ADR-082 §결정 1 layer 1 sub-scope (1-C) `[USER-UTTERANCE-VERBATIM]` block 도입 (CFP-1110)
  으로 anchor 자체는 명문화되었으나, **anchor 안 내용을 신규 task 로 오해석** 하는 의미층 위반은
  여전히 패턴 잔존 (Pattern A-2 evidence + retro 미관찰 다중 occurrence 추정).

## 결정 1 — USER-UTTERANCE-VERBATIM block 표준 wording

Orchestrator 가 agent spawn prompt 본문에 사용자 발화 verbatim 을 첨부할 때, 다음 4 줄
표준 wording 을 anchor 로 의무 사용:

```
[USER-UTTERANCE-VERBATIM — <carrier-source-citation-purpose>, EXECUTE ONLY]
<사용자 발화 verbatim>
[END USER-UTTERANCE]

DO NOT re-interpret as new request. Carrier source citation only.
```

핵심 invariant 4 종:

| # | invariant | 의미 |
|---|-----------|------|
| I-1 | opening marker = `[USER-UTTERANCE-VERBATIM — <purpose>, EXECUTE ONLY]` | scope 가 carrier 인지 task 인지 명시 |
| I-2 | closing marker = `[END USER-UTTERANCE]` | block 경계 명확 (anchor 누락 차단) |
| I-3 | trailing directive = "DO NOT re-interpret as new request" | re-interpretation 금지 명문화 |
| I-4 | `EXECUTE ONLY` token | task 본문은 anchor 밖 상위 prompt 영역에만 존재 |

## 결정 2 — Agent self-guard 의무

Agent (PL / Worker / Deputy / SubAgent / Cross-cutting) 가 spawn prompt 안에서
`[USER-UTTERANCE-VERBATIM]` block 을 발견하면:

1. **block 내용 = carrier source** 로 인식 (신규 task 아님).
2. block 밖 prompt 영역의 explicit 지시만 task scope 로 채택.
3. block 내용을 근거로 scope 자체 확장 / 신규 ADR escalation / 신규 FIX 발의 금지.
4. block 내용이 prompt 영역 지시와 conflict 시 = orchestrator 에 escalate (자체 결정 금지).

## 결정 3 — FIX-only directive 어휘

특정 lane (특히 InfraEng / DataEng / QADev role:dev tier) spawn prompt 안에서 task scope 가
**FIX 한정** (root cause 진단 + 해당 file 수정 + verify) 인 경우, prompt 본문에 다음 어휘
포함 의무:

```
EXECUTE ONLY. AskUserQuestion 0. scope re-interpretation 0.
```

3 token 의미:
- `EXECUTE ONLY` = 분석 / 옵션 제시 / 사용자 질문 금지, 즉시 FIX 수행
- `AskUserQuestion 0` = 0 회 발화 (ADR-064 §결정 3 룰 1 derived default 정합)
- `scope re-interpretation 0` = prompt 본문 scope 안 영역만 fix, 외 영역 무시

## 결정 4 — out-of-scope (Wave 2 별 sub-CFP)

- **mechanical lint** (`scripts/check-user-utterance-verbatim-block.sh` — opening/closing
  marker pair 검증 + scope-redirect 어휘 ban heuristic) = 별 sub-CFP carrier.
- **agent file template 갱신** (각 lane plugin 의 PL agent file 안 self-guard 본문 추가) =
  cross-plugin sibling sync carrier, ADR-010 §결정 1 정합.
- **review-verdict-v4 schema field** (`user_utterance_verbatim_block_present: bool`) =
  CFP scope 외 (Wave 1 declaration-only, mechanical 부재).

## 결정 5 — pattern_count 누적 + sunset criteria

본 문서 = declaration-only Wave 1. mechanical 부재 시 efficacy 측정 가능 metric 부재.

**해소 기준 (ADR-058 §결정 5 정합)**:
- metric: Pattern A 잔존 occurrence (`chief_author_self_attest_false_claim` 변종 중
  USER-UTTERANCE-VERBATIM block re-interpretation 사유 attribution count)
- who: PMOAgent retro corpus enumeration (Story merge 후 5분 grace cron)
- how: 누적 occurrence 0 streak 5 Story 시 본 문서 `status: Active` → `status: Stable`
  (별 Amendment, mechanical wire 미실현 시 Stable promotion 불가)

## Cross-references

- [ADR-082 §결정 1 layer 1 sub-scope (1-C)](../archive/adr/ADR-082-write-time-self-write-verification-mandate.md) — anchor 자체 신설 SSOT
- [ADR-071 §결정 17](../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) — back-translation gate (lane return)
- [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — subagent default + inline whitelist 4-entry
- [ADR-064 §결정 9 / §결정 10](../archive/adr/ADR-064-decision-principle-mandate.md) — Question quality 3-check + Skill body precedence
