---
name: research-request-gate
description: lane 이 작업 *중* 외부사실 의존으로 막혔을 때(known-unknown 깊은 질문) Orchestrator 가 따르는 on-demand 깊은 조사 보충 절차. lane 이 scope-clear 조사 요청을 올림 → Orchestrator 가 문지기로 게이트 심사(scope 명확성 / shallow-vs-deep 문턱 / 흐린 요청 반려) → harness-native deep-research 실행(Orchestrator 전용) → cited 결과를 요청 lane 재spawn packet 으로 주입. 외부지식 충당 3-단계(ADR-124) 중 단계③ 의 on-demand 경로(review-time 게이트 S2/S3 와 disjoint). caller scope = Orchestrator preset 한정. ADR-126 SSOT / ADR-124 §결정 1·2·6 / ADR-039 §결정 1·2 정합.
tools: Read
---

# codeforge:research-request-gate (CFP-2329 / Epic CFP-2324 S5 — 단계③ on-demand pull)

> lane 이 작업 *중* 외부사실 의존 known-unknown 으로 막혔을 때(예: 설계 결론이 어떤 외부 프로토콜·표준의 진위에 좌우되는데 얕은 자가조사(단계②)로는 닫히지 않을 때), Orchestrator 가 깊은 다출처 검증(deep-research)을 보충해 주는 절차. lane 은 **요청만 올리고**, 실행(deep-research 호출)은 Orchestrator 가 한다.
>
> 정책 SSOT = [ADR-126](../../archive/adr/ADR-126-on-demand-research-request-gate.md). 본 skill 은 그 정책의 **운영 절차 carrier**. 외부지식 충당 3-단계 모델 = [ADR-124](../../archive/adr/ADR-124-external-knowledge-provisioning-model.md) §결정 1, 깊은 검증 발동 게이트 = ADR-124 §결정 2, 외부사실 의존 휴리스틱 = ADR-124 §결정 6.
>
> **caller scope (ADR-039 §결정 1/2 경계 정합)**: 본 절차는 **Orchestrator preset 한정**. 임의 SubAgent 는 본 절차의 게이트 심사·deep-research 호출 비대상(deny) — lane(subagent)이 스스로 deep-research 를 호출(=spawn)하면 재귀-spawn limit 와 충돌하므로([ADR-039](../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) 회피 대안 C "subagent → Agent tool 호출 금지"), lane 은 **요청만** 올린다. deep-research 실행은 spawn 독점 주체인 Orchestrator 의 행위 (jira-decision-channel "Orchestrator preset 한정, 임의 SubAgent deny" 선례 동형).

---

## 단계③ 의 두 경로 (review-time ↔ on-demand)

깊은 다출처 검증(ADR-124 §결정 1 단계③)은 두 경로로 진입한다. 본 skill 은 그 중 **on-demand** 경로 전담이다.

| 경로 | trigger | 주체 | 시점 | carrier |
|---|---|---|---|---|
| review-time(자동 게이트) | 요구사항리뷰 lane 진입 (자동) | RequirementsReviewPL → Claude/Codex dual-peer | 설계 진입 *전* | S2 (ADR-125) + S3 차등 (ADR-124 Amendment 1) |
| **on-demand(pull)** | lane 이 작업 *중* 외부사실 의존으로 막힘 | 임의 lane(요청) + Orchestrator(문지기·실행) | 작업 *중* | **본 skill (S5 / ADR-126)** |

> 두 경로는 trigger·주체·시점이 갈리는 **disjoint** 관계 (SSOT = [ADR-125](../../archive/adr/ADR-125-requirements-review-lane.md) §결정 6 "on-demand 경로(S5) 와 disjoint … 깊이의 차등 메커니즘 실구현은 S3 로 보존"). 같은 deep-research skill body 를 trigger·주체·시점만 달리 진입한다.

---

## 절차 추상 단계 (channel-agnostic)

on-demand 보충은 아래 **추상 단계**로 정의한다. 절차 본체는 mechanism 비의존이고, env=1 team-mode SendMessage / env=0 round-trip 의 mechanism 바인딩은 "mechanism 이중 경로" 절에만 둔다.

| 추상 단계 | 의미 | 책임 |
|---|---|---|
| `request` | lane 이 scope-clear 조사 요청을 올림 | lane (요청 형식) |
| `gate` | Orchestrator 가 문지기로 요청 심사 (3-규칙) | Orchestrator |
| `theater_check` | 외부사실 의존 게이트 + 검사연극 차단 (ADR-124 §결정 2/6 상속) | Orchestrator |
| `execute` | harness-native deep-research skill 호출 (Orchestrator 전용) | Orchestrator |
| `inject` | cited 결과를 요청 lane 재spawn packet 으로 주입 | Orchestrator |

---

## 1. lane 조사 요청 형식 (`request`)

lane 은 작업 중 외부사실 의존 known-unknown 으로 막혔을 때, 아래 형식으로 조사 요청을 올린다 (lane 은 요청만 — 실행 금지).

```
조사 요청: <lane>/<작업-anchor>          # 예: 설계/CFP-NNNN-§3
질문: <단일·평문 질문 1개>               # 다중 질문 금지 — scope 명확성 (게이트 규칙 ①)
얕은조사 불가 사유: <왜 단계②(얕은 자가조사)로 안 되는지 1~2줄>
외부사실 의존 지점: <결론이 어떤 외부지식의 진위에 좌우되는지>
```

- **단일 질문 의무** — 한 요청 = 한 질문. 묶음 질문은 scope 가 흐려져 게이트 ① 에서 반려된다.
- **얕은조사 불가 사유 의무** — 단계②(그 lane 의 자기 도구로 결정-범위 얕게 확인)로 닫히지 않는 이유를 명시. 이 사유가 부실하면 게이트 ② shallow-vs-deep 문턱에서 반려된다.
- **외부사실 의존 게이트 상속 (ADR-124 §결정 2)**: 질문이 외부지식(산업 표준·RFC·벤더 동작·CVE 등)의 진위에 의존해야 한다. 내부 코드·내부 규칙·팀 암묵지식만으로 닫히는 결론(ADR-124 §결정 6 "의존 X" row)에 deep-research 를 요청하면 **검사연극** → 반려 (theater_check 절).

---

## 2. Orchestrator 게이트 3-규칙 (`gate`)

Orchestrator = **문지기**(scope 심사 + 반려 판정)다. **조사 주제 기획자가 아니다** — demand 출처는 lane 이고, Orchestrator 는 요청의 적격성만 심사한다.

| 규칙 | 심사 | 반려 조건 |
|---|---|---|
| ① scope 명확성 | 단일·평문 질문인가, anchor·외부사실 의존 지점이 특정되는가 | 묶음 질문 / 모호한 범위 / anchor 부재 → 반려 |
| ② shallow-vs-deep 문턱 | 얕은 자가조사(단계②)로 처리될 일이 아닌가 | "얕은 셀프서비스로 충분" → 반려 |
| ③ 흐린 요청 반려 | ①② 충족하나 질문 자체가 흐린가 | 구체화 요구 후 재요청 |

**반려 사유 형식** (lane 에 되돌려보낼 때):

```
반려: <lane>/<작업-anchor> 조사 요청
사유: <규칙 ①|②|③ 중 위반 규칙 + 1줄 설명>
재요청 안내: <단일 질문으로 좁히기 | 얕은 자가조사(단계②)로 처리 | 외부사실 의존 지점 명시>
```

- 게이트 ② 반려 = "얕은 셀프서비스로 처리하라" 통보 (단계② 로 routing). 게이트 ①③ 반려 = lane 이 요청을 재구성해 다시 올림.
- 반려는 거버넌스 결손이 아니라 게이트의 정상 동작이다 — on-demand 게이트 자체가 검사연극 차단 장치다(theater_check 절).

---

## 3. 외부사실 의존 게이트 + 검사연극 금지 (`theater_check`)

게이트 3-규칙 통과 후에도, **결론이 외부사실에 의존하는 지점인지** 를 최종 확인한다 (ADR-124 §결정 2 외부사실 의존 게이트를 본 on-demand 경로에 상속).

- **외부사실 의존 판정 휴리스틱** (ADR-124 §결정 6, 인용 — 복붙 금지):
  - 의존 O (단계③ 적용): 팩트체크 / 벤더 동작 / 표준(RFC 등) / CVE·취약점 사실.
  - 의존 X (단계③ 미적용): 팀 암묵지식 / 내부 코드·규칙 사실 (repo·내부 축).
  - 경계(?): 시장정보 / 벤치마크 / StackOverflow 등 준-외부 출처 → ADR-125 §결정 6 운영 판정(단계② 우선, 리뷰어 재량 escalation)을 따른다.
- **검사연극(verification theater) 금지** — 내부근거-only 결론에 deep-research 를 강제하면 검사연극이다. SSOT = ADR-124 §결정 2 + ADR-119 §결정 6 "'조사했으므로 옳다' 단정 금지" (조사 = traceability + 정직성 수단이지 결론의 정당성 보증 아님). 본 절은 그 두 SSOT 를 **cross-ref** 하며 문구를 복붙하지 않는다(drift 회피).
- **code lane 웹금지 우회 차단 (ADR-124 Amendment 1 A1-3, [P0])** — 요청 lane 이 code(구현리뷰)면, deep 조사 결과를 주입해도 **code 리뷰 결론은 내부 코드 사실 축으로 닫힌다**. on-demand 가 code lane 의 web 전면금지(web 허용 lane = security + requirements-review + design 좁은 예외 3 종)를 깨는 우회로가 되어서는 안 된다 — code lane 의 작업중 막힘이 외부지식 의존이 아닌데 deep 조사를 끼워 넣으면 검사연극 + 대칭 붕괴다. (S3 차등 ↔ S5 on-demand 는 axis 가 다르다: S3 = 적용 깊이 차등 / S5 = 호출 경로 pull.)
- **abstention escape** — deep-research 가 출처를 확보하지 못하면 ADR-119 §결정 3.2 "확인 불가 / 추정" 명시 후 진행 (데드락 회피, ADR-124 §결정 6 상속).

---

## 4. deep-research 실행 (`execute`)

게이트 통과 시, Orchestrator 가 harness-native **deep-research** skill 을 호출한다 (Orchestrator 전용).

- **방법론 = harness 제공** — deep-research(다출처 web 조사 + adversarial 검증 + 출처 인용)는 Claude Code harness 가 제공하는 system skill 이다. 본 skill 은 방법론을 **재정의하지 않는다** — 호출 경로·게이트만 신설한다. lane별 차등 instantiate(보안테스트 web 단계 심화 / 설계리뷰 좁은 예외 / code lane web 금지 보존)는 S3(ADR-124 Amendment 1)가 이미 완료했다 (cross-ref only).
- **S3 차등 방법론과 정합** — 외부사실 의존 + 다출처 교차 + adversarial verify + 시의성(recency). on-demand 도 이 4 요소를 따른다 (ADR-124 Amendment 1 A1-1).
- **ADR-039 §결정 2 정합 (1줄 명문, AC-7)**: deep-research Skill 호출은 ADR-039 §결정 2 closed 4-entry inline whitelist 의 **5번째 entry 를 신설하지 않는다.** rate-limit-429-mitigation skill 선례(ADR-039 Amendment 4)와 동형 — **skill body 가 operational primitive 를 보유하되 closed 4-entry whitelist 는 무손상.** Skill 호출 자체는 file/GitHub mutation 미발화 → §결정 1 "수정 작업" closed enum 비해당 → whitelist axis 와 disjoint. 상세 SSOT = ADR-126 §결정 2/3.

---

## 5. cited 결과 주입 (`inject`)

deep-research 의 cited 결과를 **요청 lane 의 재spawn prompt packet block** 으로 주입한다 (요청 lane 이 막힌 지점에서 결과를 받아 작업 재개).

```
[research-injection] 요청=<lane>/<작업-anchor>
  질문: <원 질문 1줄>
  결과(요약): <cited 결론 — 각 단정에 출처 병기>
  출처: <URL | 표준 번호 | 벤더 문서명 ...>
  abstention: <출처 확보 불가 시 "확인 불가/추정" 명시 — 없으면 생략>
```

- **재주입 = 기존 packet-injection 동형** — cited 결과 packet 은 기존 FIX 재spawn + `pr_phase` packet 주입과 **동형**이다 (신규 주입 채널 발명 금지). 요청 lane 을 재spawn 하며 prompt packet 에 위 block 을 확장 주입한다.
- **각 단정에 출처 병기 (ADR-119)** — 주입되는 결과의 substantive 단정에는 `source: <URL|표준 번호|문서명>` 병기 의무. 출처 부재 시 "확인 불가 / 추정" 명시 (abstention escape).

### mechanism 이중 경로 (env=1 / env=0 동등)

요청·주입 mechanism 은 team-mode 활성 여부에 따라 두 경로가 **동등 보장**된다 (playbook env=0/env=1 동등성 — registry §6.4 / playbook §3.6 답습, 신규 분기 발명 금지).

| env | `request` | `inject` |
|---|---|---|
| env=1 (team-mode, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | lane teammate → Orchestrator(Lead) **SendMessage** 로 조사 요청 | Orchestrator → lane teammate SendMessage 또는 재spawn packet 주입 |
| env=0 (default subagent context, ADR-039) | lane subagent **return verdict** 에 조사 요청 표기 → Orchestrator 게이트 심사 (round-trip) | 게이트 통과 → deep-research 실행 → 요청 lane **재spawn** with packet 주입 (round-trip polyfill) |

- 두 경로는 **동등** — env=0 round-trip 은 env=1 SendMessage 의 polyfill 이며, 신규 분기를 발명하지 않는다. env=0 는 lane 막힘당 최소 1 추가 round-trip(latency/token 정성 trade-off — 토큰 효율보다 정확성 우선, ADR-035 §컨텍스트 정합).

---

## Cross-references

- [ADR-126](../../archive/adr/ADR-126-on-demand-research-request-gate.md) — 본 skill body 정책 SSOT (§결정 1-6: on-demand mechanism + ADR-039 정합 자체 재논증 + whitelist 무신설 + code lane web 금지 보존 + review-time disjoint + 검사연극 금지 상속)
- [ADR-124](../../archive/adr/ADR-124-external-knowledge-provisioning-model.md) — 외부지식 충당 3-단계 모델 (§결정 1 단계③ "리뷰 게이트(주) + on-demand(후순위)" / §결정 2 외부사실 의존 게이트 + 검사연극 금지 / §결정 6 외부사실 의존 휴리스틱 / Amendment 1 A1-3 code lane web 금지 [P0])
- [ADR-125](../../archive/adr/ADR-125-requirements-review-lane.md) — 요구사항리뷰 lane (§결정 6 on-demand(S5) ↔ review-time disjoint SSOT)
- [ADR-039](../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — spawn = Orchestrator 전용(§결정 1) + closed 4-entry inline whitelist(§결정 2, L145) + 회피 대안 C(lane 자가-spawn 불가) + Amendment 4(skill body primitive ↔ whitelist 무손상 선례)
- [ADR-119](../../archive/adr/ADR-119-research-before-claims.md) — §결정 6 검사연극 금지 SSOT / §결정 3.2 abstention escape
- [ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) / `skills/rate-limit-429-mitigation/SKILL.md` — skill body 가 primitive 보유하되 whitelist 무손상 binding precedent (Amendment 4 경유)
- `skills/jira-decision-channel/SKILL.md` / `skills/review-responsibility/SKILL.md` — 추상 단계 표 + caller scope Orchestrator 한정 / 참조 테이블 형식 선례
