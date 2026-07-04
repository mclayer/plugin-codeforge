---
kind: contract
contract_version: "1.0"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/return-envelope-v1.md
related_plugins:
  - codeforge (wrapper, consumer) — Orchestrator + 전 lane PL/worker 반환
related_adrs:
  - ADR-142 (Orchestrator-self context discipline — §결정 3 return-envelope-v1 carrier)
  - ADR-039 (subagent default — §결정 2 inline-whitelist disjoint axis)
  - ADR-044 (Phase-scoped Sequential Team — worker 반환 경계)
  - ADR-119 (research-before-claims — high-signal / proxy 정직 표기 + hollow-gate 차단)
  - ADR-008 (Inter-plugin Contract Versioning)
authors:
  - CFP-2572 (2026-07-05) — return-envelope-v1 신설 (Orchestrator context discipline Phase 2, ADR-142 §결정 3 carrier)
---

# return-envelope v1 — Inter-plugin Contract

전 codeforge worker / lane PL / Orchestrator 반환을 **감싸는(wrap) 범용 return-envelope**. 기존 `*_output-v1` / `review-verdict-v4` / `fix-event-v1` per-task payload 을 **대체하지 않고 그 위에 합성(compose over)** 한다 — per-task payload schema 는 무변경. envelope 는 return 크기 · raw 제외 · high-signal-only 3 불변식의 **DRY 단일 소유자(single owner)** 다 (개별 payload 계약이 이 3 불변식을 중복 정의하지 않는다).

**상위 SSOT 위치**: 본 파일이 단일 원본(canonical) — ADR-142 §결정 3 (CFP-2158 / [ADR-118](../../archive/adr/ADR-118-monorepo-consolidation.md) D5 wrapper 단일 원본). versioning 룰 = ADR-008.

## 1. 목적 + Tier 선언 (사활 — capability-claim honesty)

본 contract 는 **[measurement] (schema 파일-lint) + [advisory] (prompt-mandate tight-return)** 두 tier 로만 작동한다. **runtime hard-cap 아님** — agent-return runtime hard-cap 은 플랫폼에 **미문서화**(P3, code.claude.com/docs)이며 substrate 가 미검증이라 ADR-142 §결정 3 에서 **REJECTED** 됐다. 따라서 본 문서 어디에도 반환을 런타임에서 물리적으로 막는(block/deny) 표현을 두지 않는다. 3 불변식은 (1) 문서 수준 schema-lint 로 **측정**되고 (2) worker spawn prompt 에 tight-return **권고**로 실린다 — 그 둘이 전부다.

배경 근거 (ADR-119 인용):
- context = "Context must be treated as a finite resource with diminishing marginal returns" + context rot ("as tokens increase, the model's ability to accurately recall decreases") — source: anthropic.com/engineering/effective-context-engineering-for-ai-agents.
- subagent 반환 = "only a condensed summary (often 1,000-2,000 tokens)" — source: effective-context-engineering.

## 2. envelope 구조 (wrap contract)

envelope = 2-part composition. per-task payload 은 그대로 `envelope.payload` 에 들어가고(schema 무변경), `envelope.meta` 가 크기 · 신호 밀도 회계(accounting)만 얹는다.

```yaml
return_envelope:
  contract_version: "1.0"
  envelope:
    meta:
      verdict: <string>          # per-task 결론 (PASS/FAIL/PARTIAL/ESCALATE 등 — payload 계약별 enum 재사용)
      size_bytes: <int>          # 본 envelope 직렬화 크기 (측정값)
      cap_bytes: <int>           # 권고 상한 (advisory soft cap — 런타임 강제 아님)
      over_cap: <bool>           # size_bytes > cap_bytes 관측 flag (block 아님, 측정 결과만)
      mode: concise | detailed   # concise = verdict + evidence_ref 만 / detailed = 확장 (response_format 대응)
      evidence_ref:              # path:line 포인터 배열 (raw 원문 미포함)
        - "<path>:<line>"
    payload: <existing per-task contract object>   # *_output-v1 / review-verdict-v4 / fix-event-v1 그대로
```

- `envelope.payload` = **기존 per-task 계약 객체 그대로** (wrap 관계 — 본 envelope 는 payload 의 내부 schema 를 변경/재정의하지 않는다).
- raw diff / 원문은 payload/meta 어디에도 **inline 으로 싣지 않는다** — `evidence_ref` path:line 포인터만 (§4 예외 3종 포함 전부 포인터화).

## 3. envelope 소유 불변식 (DRY single owner)

아래 3 불변식은 **모든 return 계약을 가로질러 envelope 단 한 곳이 소유**한다 (개별 payload 계약이 중복 정의 금지 — DRY). 각 불변식의 실 작동 tier = 문서-lint 측정 + prompt 권고 (런타임 강제 아님).

| 불변식 | 내용 | 작동 tier |
|---|---|---|
| size cap | `size_bytes` 를 `cap_bytes` 권고 상한과 대조, 초과 시 `over_cap=true` 관측 flag | [measurement] flag + [advisory] 권고 |
| raw-exclusion | raw diff / 원문 미포함 — `evidence_ref` path:line 포인터만 | [measurement] doc-lint (clause 존재 검증) + [advisory] |
| high-signal-only | verdict + evidence_ref 중심, 저수준 식별자(low-level identifier) 배제 | [advisory] prompt-mandate |

high-signal-only 근거 (ADR-119 인용):
- "return only high signal information … eschew low-level identifiers" — source: writing-tools-for-agents.
- Claude Code 는 tool 응답을 "restrict tool responses to 25,000 tokens by default" 하며 `response_format` concise/detailed 를 제공 — source: writing-tools-for-agents. 본 envelope 의 `mode: concise|detailed` 가 이 response_format 에 대응.

## 4. 필수 raw 예외 (CLOSED enumeration — 정확히 3종)

raw 원문이 불가피한 경우는 **닫힌 3종뿐**이며, 이 셋조차 envelope 에 **inline raw 로 넣지 않고** `evidence_ref` 포인터 + on-demand refetch 로 표현한다:

1. **FIX diff** — fix-event-v1 의 변경 diff 원문
2. **review verdict 원문** — review-verdict-v4 finding 의 원 근거 텍스트
3. **research 인용 원천** — 외부 조사 인용 source 원문 (ADR-119 / ADR-126)

이 3종은 **CLOSED set** 이다 (추가/제거 = 본 contract §8 version bump 대상). 표현 규칙 = `envelope.meta.evidence_ref` 에 **path:line 포인터**로 남기고 필요 시점에 소비자가 **on-demand refetch** — envelope 에 raw 를 실어 보내지 않는다 (inline 금지, 포인터화 유지).

## 5. disjoint-axis 선언 (MANDATORY — ADR-039 §결정 2 무침범)

본 return-size 계약은 ADR-039 §결정 2 의 inline-whitelist 와 **disjoint axis** 다. inline-whitelist 는 **inline-vs-spawn 메커니즘 축**(현재 유효 6-entry closed enumeration)이고, return-envelope-v1 은 **return 크기 · 신호 밀도 축**이다. return-envelope-v1 은 **ADR-039 §결정 2 의 7번째 whitelist entry 가 아니며**, 그 closed enumeration 을 **건드리지 않는다** (별개 축 — mechanism 축 무변경, 6-entry closed 유지).

## 6. [measurement] scoping (hollow-gate 차단)

동반 schema-lint 는 **오직 본 문서(return-envelope-v1.md)가 well-formed 인지만** 검증한다 — cap field 존재 + raw-exclusion clause 존재 + MANIFEST 등록. 그것은 **런타임 return 준수를 강제하지 않는다** (It does NOT enforce runtime return compliance). 이는 fix-event-v1 이 **문서 schema(파일)** 이지 **inter-agent return-channel enforcement 가 아닌 것과 동일 관계**다. lint GREEN = "문서가 계약 형식을 갖췄다"이지 "런타임 반환이 cap 을 지켰다"가 **아니다** (hollow-gate 위장 금지 — ADR-119 검증-후-단언).

## 7. [advisory] prompt-mandate (tight-return)

worker spawn prompt 는 tight-return 계약을 **실어야 한다(SHOULD)** — verdict / evidence-ref 만, raw 제외, concise|detailed mode. 이는 **advisory prompt-mandate 이지 enforced 아님** (lane PL 이 spawn packet 에 얹는 권고 문구). 미준수는 관측 대상이지 런타임 차단 사유가 아니다.

플랫폼 사실 (요구사항리뷰 PASS): live per-turn self-context surface 부재(P1), agent-return runtime hard-cap 미문서화(P3) — source: code.claude.com/docs. → 본 계약은 어디에서도 runtime hard-cap 을 주장하지 않는다.

## 8. 변경 규칙 (ADR-008)

- `envelope.meta` 선택 field 추가 = **MINOR** (backward-compat, v1.0 reader skip 가능).
- §4 CLOSED raw 예외 3종 **확장 = MINOR** (additive) / **제거 = MAJOR** (BREAKING).
- tier 승격 ([measurement]/[advisory] → 물리 강제 runtime cap) = **MAJOR/BREAKING** — 별 ADR + substrate 검증 선행 필수 (ADR-142 §결정 3 REJECT 재검토 대상).
- wrapped payload 계약(`*_output-v1` / `review-verdict-v4` / `fix-event-v1`)은 본 envelope 와 **독립 versioning** (wrap 관계 — 각자 bump, 상호 무결합).

## 9. Cross-references

- **ADR-142** §결정 3 (return-envelope carrier) / §결정 4 (self-context proxy sibling — spawn-event-v1 §2.1)
- **ADR-039** §결정 2 — inline-whitelist (disjoint axis, §5)
- **fix-event-v1** / **review-verdict-v4** / **`*_output-v1`** — wrapped payload 계약 (schema 무변경)
- **ADR-119** — high-signal / proxy 정직 표기 + hollow-gate 차단 근거
- **ADR-008** — inter-plugin contract versioning (§8)
