---
adr_number: 102
title: Ratchet 약화 evidence-gate governance anchor — formal-ADR-없는 spec-level predecessor reversal 의 sunset_justification mechanism (extend)
status: Accepted
category: governance
date: 2026-05-22
carrier_story: CFP-1228
parent_epic: CFP-1146
related_stories:
  - CFP-1228     # 본 carrier (Epic-A Wave 1 Story-4 — W1 마지막 governance ADR)
  - CFP-1146     # umbrella Epic-A (Atlassian suite 재결합 governance reversal)
related_adrs:
  - ADR-099      # Wave 1 Story-1 (hard prerequisite, MERGED) — §결정 4/4-A 가 본 ADR-102 에 약화 정당화 위임. lint 역전 (Layer 2 평문 allowlist 확장) = ratchet 약화 방향, 본 ADR 이 evidence-gate 통과 anchor
  - ADR-058      # ADR sunset criteria mandate — §결정 5 (CFP-1149 Amendment 1 재정의: 약화 차단 logic → 약화 evidence requirement, evidence-gate). 본 ADR = 일반 evidence-gate 경로 적용 (ADR-097 면제 channel 비대상)
  - ADR-064      # decision principle mandate — §결정 7 (CFP-1149 Amendment 8 재정의: top-down ratchet → evidence-gated symmetric ratchet). 본 ADR = 약화 방향 evidence-gate 통과 사례
  - ADR-095      # 9 ADR sunset metric 표준화 — sunset_justification metric 영역 형식 reuse (changelog mining + cron 2-source closed-set / K8s GA 12개월 baseline)
  - ADR-097      # paradigm replacement governance anchor — 면제 channel 비대상 (§결정 1 closed-set AND 조건 a 9+ ADR sunset 미충족, predecessor formal ADR 0건). carrier-preserved sunset 개념(§결정 3)만 cross-ref (개념 reuse, 면제 channel 발동 안 함)
  - ADR-100      # Wave 1 Story-2 (sister, MERGED) — §해소 기준 "약화 정당화 layer 분리" 에서 Layer 1/데이터 흐름 영역은 약화 정당화 비대상, Layer 2 lint 한정 위임 명시. 본 ADR = 그 Layer 2 한정 약화 정당화 owner
  - ADR-101      # Wave 1 Story-3 (sister, MERGED) — 순수 security 강화 (약화 0건) → 본 ADR 약화 정당화 비대상. cross-ref only
  - ADR-103      # Wave 4 git↔Confluence sync mechanism — 본 commit 시점 reserved (미작성). forward cross-ref (Layer 1 narrow allow wire owner)
  - ADR-013      # codeforge family dogfood-out — predecessor reversal source (spec/plan = internal-docs dogfood, formal ADR 0건)
related_files:
  - docs/adr/ADR-099-atlassian-allow-redefinition.md          # §결정 4/4-A 약화 정당화 위임 source (본 ADR 이 그 위임 받음)
  - docs/adr/ADR-058-adr-sunset-criteria-mandate.md           # §결정 5 evidence-gate (CFP-1149 Amendment 1) 일반 경로
  - docs/adr/ADR-064-decision-principle-mandate.md            # §결정 7 evidence-gated symmetric (CFP-1149 Amendment 8)
  - docs/adr/ADR-095-sunset-metric-standardization.md         # sunset metric 형식 reuse source
  - docs/adr/ADR-097-paradigm-replacement-governance-anchor.md # 면제 channel 비대상 + carrier-preserved 개념 cross-ref
  - scripts/check-no-atlassian.sh                             # ADR-099 §결정 1 Layer 2 lint — 본 ADR 약화 정당화 대상 (Layer 2 한정)
  - .claude/settings.json                                     # Layer 1 mcp__atlassian deny carrier-preserved (약화 대상 아님 — §결정 3 명시)
  - CHANGELOG.md                                              # changelog mining metric source (ADR-092 SSOT) — Atlassian 재결합 reversal 완료 marker
  - docs/adr/ADR-RESERVATION.md                               # row 102 reserved → active 전환
mechanical_enforcement_actions: []   # declaration-only Wave 1 — §결정 3 sunset metric 의 실 cron kpi (docs/kpi/atlassian-allow-incident.json) + 집계 측정 wire = 후속 carrier. ADR-082 §결정 6 / ADR-070 §D5 / ADR-095 §결정 2 retain pattern 답습 (behavioral declaration, pattern_count >= 2 재발 시 follow-up CFP MUST promote to mechanical lint)
is_transitional: false   # permanent governance anchor — spec-level reversal sunset mechanism (§결정 4) 은 영구 거버넌스 정책 (future formal-ADR-없는 reversal 재사용). 본 ADR 이 codify 하는 mechanism = 강화 방향 (governance 표현력 확장). 단 본 ADR 이 정당화하는 Atlassian-allow ratchet 약화 evidence (3-tuple) 는 §결정 3 본문 명시 (ADR-058 §결정 5 evidence-gate 통과)
sunset_justification: null   # is_transitional false — 본 ADR mechanism (spec-level reversal sunset 형식) 자체는 강화 방향 (신설 = governance 표현력 확장, 약화 아님) → mechanism 자체의 sunset_justification 불요. 본 ADR 이 정당화하는 Atlassian-allow ratchet 약화 evidence 는 §결정 3 본문 (frontmatter sunset_justification 과 별개 layer — 본 ADR = 약화 정당화 anchor 이지 본 ADR 자체가 약화되는 것 아님)
amendment_log: []
---

# ADR-102 — Ratchet 약화 evidence-gate governance anchor (spec-level predecessor reversal sunset mechanism)

## 상태

`Accepted` (2026-05-22 KST) — CFP-1228 carrier (Epic-A Wave 1 Story-4, W1 마지막 governance ADR). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 / ADR-099 row 99 / ADR-100 row 100 / ADR-101 row 101 chief author precedent 정합). 별도 Story file 없음 (Wave 1 Story-1/2/3 ADR-099/100/101 답습 — ADR 가 §3 설계 SSOT). dogfood-out (ADR-013): change-plan 은 wrapper repo 에 commit 안 함, ADR 만 wrapper commit.

## 컨텍스트

### 동인

ADR-099 (Wave 1 Story-1, MERGED) 가 `check-no-atlassian.sh` lint 를 역전했다 — "Atlassian 잔재 0" 에서 "Atlassian-allow (Layer 2 평문 참조 화이트리스트 확장)" 으로. ADR-099 §결정 4-A 가 이 lint 역전을 **ratchet 약화 방향** 으로 판정하고, 그 약화의 정당화를 본 ADR-102 (Wave 1 Story-4) 에 위임했다.

핵심 긴장은 predecessor 의 성격이다. v0.7→v0.8 의 Atlassian 완전 제거 (hard remove, breaking change) 는 **formal ADR carrier 가 0건** — spec/plan/agents/settings/schema/docs 레벨 결정만 존재한다 (predecessor spec = `docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md`, internal-docs dogfood). ADR-058 §결정 5 와 ADR-097 §결정 3 어느 쪽도 "formal ADR 없는 spec/plan-레벨 predecessor 의 reversal 을 어떻게 sunset_justification 처리하는가" 를 다루지 않는다.

본 ADR 은 이 case 의 sunset_justification mechanism 을 codify 한다 — **formal ADR 없는 predecessor 를 spec/plan 참조로 대체하는 형식** (extend). 동시에 ADR-099 가 위임한 Atlassian-allow ratchet 약화의 evidence (3-tuple) 를 §결정 3 본문에 명시해 ADR-058 §결정 5 evidence-gate 를 통과시킨다.

### evidence-gate framing — 약화 차단 극복이 아니라 evidence-gate 통과 (post-CFP-1149 정정)

본 ADR 의 framing 은 **"ratchet 약화 차단을 극복한다" 가 아니라 "약화 evidence-gate 를 통과한다"** 다. 두 의존 ADR 이 CFP-1149 로 재정의됐기 때문이다 (verified):

- **ADR-058 §결정 5 (CFP-1149 Amendment 1)**: sunset_justification 의미가 **"약화 차단 logic (ratchet 차단)" 에서 "약화 방향 evidence requirement (강화 방향 evidence 와 동등 1급 절차)" 로 재정의**됐다. 차단(block) 이 아니라 **evidence-gate** — 약화 evidence 가 있으면 약화는 1급으로 허용된다.
- **ADR-064 §결정 7 (CFP-1149 Amendment 8)**: top-down ratchet (강화 방향만 허용, 약화 차단) 이 **evidence-gated symmetric ratchet (강화/약화 양방향 허용, 양방향 evidence-grounded justification 의무)** 로 재정의됐다. §결정 7 본문은 약화 방향 evidence 를 "metric 측정 결과 / 평가 / 환경 변화 / pattern obsolescence" 로 명시한다.

따라서 본 ADR 은 약화를 막는 벽을 깨는 anchor 가 아니라, **Atlassian-allow ratchet 약화의 evidence (3-tuple) 를 제시해 ADR-058 §결정 5 evidence-gate 를 통과시키는** anchor 다. ADR file 명 `ADR-102-ratchet-weakening-governance-anchor.md` 는 reservation 확정값으로 유지하되, 본문 framing 은 "evidence-gate 통과 / 약화 정당화" 를 사용한다 ("차단 극복" 어휘 회피 — 차단이 아니므로).

### verified-via — 본 ADR 의 모든 사실 인용 검증

본 ADR 의 모든 §결정 / line / §N 인용은 ground truth direct Read / git verify 위에서 작성됐다 (ADR-082 §결정 2 write-time self-write verification 정합). spawn prompt 의 ArchitectAnalyst prior-art [hypothesis] 항목은 본 chief author 가 ground truth 위에서 정량 확정했다.

> verified-via: Read docs/adr/ADR-058-adr-sunset-criteria-mandate.md (worktree HEAD `fee741e`) L11-21 amendment_log Amendment 1 (CFP-1149) + L90-94 §결정 5 본문 — sunset_justification = "약화 차단 logic → 약화 방향 evidence requirement" 재정의, "차단(block)이 아니라 evidence-gate: evidence 있으면 약화 1급 허용" verbatim. count cap 미적용.
> verified-via: Read docs/adr/ADR-064-decision-principle-mandate.md (worktree) L301-316 §결정 7 — "top-down ratchet → evidence-gated symmetric ratchet" 재정의 (CFP-1149 Amendment 8). L308 약화 방향 evidence = "metric 측정 결과 / 평가 / 환경 변화 / pattern obsolescence" verbatim. ADR-058 §결정 5 의 sunset_justification = 약화 방향 evidence requirement (강화 방향 evidence 와 동등 1급 절차).
> verified-via: Read docs/adr/ADR-099-atlassian-allow-redefinition.md (worktree) L142-183 §결정 4/4-A — ADR-102 = extend (a) ADR-097 면제 channel 비대상 (조건 a 9+ ADR sunset 미충족, predecessor formal ADR 0건, closed-set AND 위반) / (b) ADR-058 §결정 5 일반 경로 / (c) ADR-095 metric reuse / (d) spec-level reversal mechanism 신설 = extend. Layer 1 (permission deny) = carrier-preserved, 약화 대상 아님 (Layer 2 lint allowlist 한정).
> verified-via: Read docs/adr/ADR-095-sunset-metric-standardization.md (worktree) L75-86 §결정 1 — metric source closed-set 2-source (changelog mining + cron 자동 측정, AND/OR composable) + baseline = K8s deprecation policy (GA 12개월 / Beta 9개월). docs/kpi/rate-limit-fallback.json 집계 dashboard 형식 답습.
> verified-via: Read docs/adr/ADR-097-paradigm-replacement-governance-anchor.md (worktree) L67-110 §결정 1-3 — 면제 channel closed-set AND 3 조건 (a 9+ ADR 동시 sunset / b 단일 atomic Epic / c ratchet 강화 lossless). §결정 3 carrier-preserved sunset 개념 (효용 lossless carry = carrier shift ≠ 약화).
> verified-via: `git -C <worktree> log --all --oneline -- 'docs/adr/ADR-*.md' | grep -i atlassian` (worktree HEAD `fee741e`) — exit 1 (매치 0건 beyond ADR-099 신설 + ADR-RESERVATION 예약). predecessor v0.7→v0.8 Atlassian 제거의 formal ADR carrier 0건 재확인 (ADR-099 §결정 4-A 결론 정합).
> verified-via: Read docs/adr/ADR-100-confluence-doc-ssot-recognition.md (worktree, MERGED) L220-228 §해소 기준 — "S4 ADR-102 sunset_justification (ratchet 약화 정당화) 는 Layer 2 lint (Atlassian-allow grep allowlist) 영역 한정 (ADR-099 §결정 4-A). 본 ADR-100 의 Layer 1 / 데이터 흐름 영역은 ADR-102 약화 정당화 경로 비대상" verbatim — 본 ADR 의 Layer 2 한정 scope 를 sister ADR-100 이 cross-ref 로 확정.
> verified-via: `ls docs/adr/ADR-101*` (worktree) — file 존재 (ADR-101 MERGED, verified 인용 가능). `ls docs/adr/ADR-103*` — file 부재 (reserved, forward cross-ref only). `ls docs/adr/ADR-102*` — file 부재 (신규 작성).
> verified-via: Read docs/adr/ADR-RESERVATION.md (worktree) L145 — row 102 = CFP-1146, status `reserved`, ADR file = `ADR-102-ratchet-weakening-governance-anchor.md` (reservation 확정 파일명 정합). row 103 (ADR-103) = `reserved` (미작성 — forward cross-ref).

### forward cross-ref reserved 명시 (ADR-082)

본 ADR 은 **ADR-103 (W4 git↔Confluence sync mechanism)** 를 cross-ref 하나, ADR-103 은 **본 commit 시점 미작성 (reserved)** 이다 (ADR-RESERVATION row 103 status `reserved` verified). 따라서 본 ADR 의 ADR-103 인용은 "owner 위임 + reserved" 로만 기술하며, 그 §결정 N 내용을 존재하듯 단언하지 않는다. sister ADR-099 / ADR-100 / ADR-101 = **MERGED** (file 존재 verified) → §결정 N 인용 가능.

## 결정

### §결정 1 — ADR-097 paradigm replacement 면제 channel 비대상 (closed-set AND 조건 a 미충족, carrier-preserved 개념만 cross-ref)

**판정 = ADR-097 면제 channel 비대상.** Atlassian-allow ratchet 약화 (ADR-099 lint 역전) 는 ADR-097 §결정 1 paradigm replacement 면제 channel 의 **발동 자격을 충족하지 못한다**. ADR-097 §결정 1 면제 channel = closed-set AND 3 조건 — 그 중 조건 (a) 가 미충족이므로 closed-set AND 위반이다.

| ADR-097 §결정 1 조건 | Atlassian reversal 평가 | 충족 |
|---|---|---|
| **(a) 9+ ADR/contract 동시 sunset 동반** | predecessor v0.7→v0.8 Atlassian 제거의 **formal carrier ADR 가 0건** (git verified). sunset 대상 ADR/contract enumeration 자체가 불가 — sunset 할 ADR 객체 부재 | **미충족** |
| **(b) 단일 atomic Epic** | Epic-A (CFP-1146) 5-slot bundle (ADR-099~103), sub-Story sibling sequential | 충족 |
| **(c) ratchet 강화 방향 lossless** | mcp__atlassian deny 가 Layer 1 permission layer 로 효용 이전 (carrier-preserved) — lossless carry 가능 | 충족 가능 |

(a) 미충족 → closed-set AND 위반 → ADR-097 면제 channel **발동 안 함**.

**carrier-preserved sunset 개념만 cross-ref (개념 reuse, 면제 channel 발동 아님)**: ADR-097 §결정 3 의 "효용 lossless carry = carrier shift (효용 소멸 아님) ≠ ratchet 약화" 개념 자체는 본 ADR 이 cross-ref 로 차용한다. v0.8 lint + 차단 효용 (무단 MCP 호출 0) 이 ADR-099 §결정 1 Layer 1 (permission deny) 로 lossless 이전됐다 — 효용 carrier 가 grep 에서 permission layer 로 shift 됐을 뿐 소멸하지 않았다. 단 이 개념 차용은 ADR-097 §결정 1/2 면제 channel 의 발동이 **아니다** (조건 a 미충족) — ADR-097 의 개념(§결정 3) 만 reuse 하고, 면제 channel 자격(§결정 1) 은 비대상이다.

### §결정 2 — ADR-058 §결정 5 evidence-gate 경로 (post-CFP-1149) + ADR-064 §결정 7 symmetric — Atlassian-allow 약화 = 약화 evidence 제시 시 1급 허용

**판정 = ADR-058 §결정 5 일반 evidence-gate 경로.** §결정 1 에서 ADR-097 면제 channel 비대상이 확정됐으므로, Atlassian-allow ratchet 약화의 정당화는 ADR-058 §결정 5 **일반** sunset_justification 3-tuple (metric/who/how) 경로를 탄다.

**evidence-gate framing (차단 아님)**: CFP-1149 재정의 후, ADR-058 §결정 5 의 sunset_justification 은 약화를 **막는 logic 이 아니라 약화 방향 evidence requirement** 다 — 강화 방향이 pattern_count / incident evidence 를 요구하듯, 약화 방향은 metric / 평가 / 환경 변화 / pattern obsolescence evidence 를 요구한다 (강화와 동등 1급 절차). ADR-064 §결정 7 (CFP-1149 Amendment 8) 의 evidence-gated symmetric ratchet 가 이를 `is_transitional: false` governance ADR 의 약화 방향에도 동일 evidence-gate 로 적용한다 (symmetric scope).

따라서 Atlassian-allow ratchet 약화 (ADR-099 lint 역전, Layer 2 평문 allowlist 확장) 는 **약화 evidence (§결정 3 의 3-tuple) 를 제시하면 1급으로 허용**된다. 막혀 있던 결정을 우회하는 것이 아니라, evidence-gate 의 입력(evidence) 을 충족시켜 정상 통과시키는 것이다. 본 ADR 은 그 evidence 를 §결정 3 에 명시 제출하는 anchor 다.

**약화 방향 evidence-grounded justification 의무 (ADR-064 §결정 7)**: 본 약화는 symmetric ratchet 의 약화 방향 사례이므로, evidence-grounded justification 의무가 강화 방향과 동등하게 적용된다. §결정 3 의 3-tuple 이 그 의무 충족이다.

### §결정 3 — sunset_justification 3-tuple (metric/who/how, ADR-095 형식 reuse, 정량) + Layer 2 한정 (Layer 1 carrier-preserved, 약화 대상 아님)

ADR-099 가 위임한 Atlassian-allow ratchet 약화의 정당화 evidence 를 ADR-058 §결정 3 의무 (3-tuple 모두 정량 명시, 모달 어휘 금지) 에 따라 명시한다. metric 영역 형식은 ADR-095 §결정 1 (changelog mining + cron 2-source closed-set / K8s GA 12개월 baseline) 을 reuse 한다.

#### 약화 범위 = Layer 2 lint allowlist 확장 한정 (이의 2 보존 — Layer 1 carrier-preserved)

본 §결정 3 의 약화 정당화 범위는 **ADR-099 §결정 1 Layer 2 (lint grep 평문 allowlist 확장) 한정**이다. ADR-099 §결정 1 의 2-layer 분리 정합:

| Layer | 약화 대상 여부 | 근거 |
|---|---|---|
| **Layer 1** — `mcp__atlassian__*` permission deny (settings.json + agent preset narrow allow) | **약화 대상 아님 (carrier-preserved)** | ADR-099 §결정 1 / 4-A — v0.8 security guard 효용 (무단 MCP 호출 0) 의 실 carrier 가 permission layer 로 lossless 이전됨. Layer 1 을 약화 대상에 포함 = ADR-099 §결정 1 위반. 순수 강화 방향 (grep → permission 격상) → 약화 정당화 비대상 |
| **Layer 2** — lint grep 평문 `atlassian\|Confluence\|Jira` allowlist 확장 | **약화 대상 (본 ADR 정당화 owner)** | "Atlassian 잔재 0" → "Atlassian-allow" detection 완화 = ratchet 약화 방향. 본 §결정 3 의 3-tuple 이 evidence-gate 통과 evidence |

이 Layer 분리는 sister ADR-100 §해소 기준 ("S4 ADR-102 약화 정당화는 Layer 2 lint 영역 한정, Layer 1/데이터 흐름 영역은 비대상", verified) 과 정합한다.

#### sunset_justification 3-tuple (정량)

ADR-099 가 약화하는 것은 "predecessor v0.8 Atlassian 제거 결정의 lint Layer 2 detection 효력" 이다. 그 약화가 정당한 evidence (도입 사유 = Atlassian 잔재 차단 의 해소 신호 + Layer 1 carrier 효용 lossless 유지) 를 다음 3-tuple 로 명시한다:

- **metric** (ADR-095 §결정 1 형식 reuse — closed-set 2-source AND, 정량):
  - **(source 1) changelog mining** (ADR-092 SSOT) — `CHANGELOG.md` 의 Atlassian 재결합 reversal entry 등장 = reversal 완료 marker. 약화 정당화 신호 = Atlassian-allow lint 의 도입 사유 (v0.8 Atlassian 잔재 차단) 가 Epic-A reversal 로 의도적으로 무효화됐음이 changelog entry pattern 으로 mining 됨.
  - **(source 2) cron monthly 자동 측정** (ADR-095 §결정 2 / ADR-057 `rate-limit-fallback.json` precedent 형식) — 2 지표 동시 0건 invariant: (i) **Layer 1 incident_count = 0** — 무단 `mcp__atlassian__*` 호출 incident 0건 (permission deny carrier 효용 유지 입증) / (ii) **Layer 2 lint warning = 0** — `check-no-atlassian.sh` Layer 2 warning 0건 (allowlist 확장 후 정상 detection 상태).
  - **baseline (K8s deprecation policy 차용, ADR-095 §결정 1)**: **GA (stable) 12개월** — Layer 1 permission deny 가 12개월 무위반 (incident_count 0 유지) 시 v0.8 security 효용이 carrier shift 후에도 lossless 임이 정식 확인된다. 시간 threshold (12개월) AND metric threshold (incident_count 0 AND warning 0) 동시 충족이 약화 정당화 완성 신호.
- **who** (검증 주체 — 정량 식별):
  - **GitOpsAgent** — changelog mining (source 1) + Layer 2 lint warning 상태 (source 2-ii) 측정 책임.
  - **SecurityArchitectAgent (SecurityArch)** — Layer 1 deny 설정 유효성 + incident_count (source 2-i) 측정 책임 (permission deny carrier 효용 유지 검증).
- **how** (구체 검증 방법 — 정량 path):
  - **source 1 (changelog mining)**: `CHANGELOG.md` (ADR-092 SSOT) 의 Atlassian 재결합 reversal entry grep — reversal 완료 marker pattern 매치.
  - **source 2-i (Layer 1 incident)**: `.claude/settings.json` Read — `permissions.deny` 안 `mcp__atlassian` / `mcp__atlassian__*` 존재 확인 (Layer 1 carrier 효용 carry 입증) + cron kpi `docs/kpi/atlassian-allow-incident.json` (ADR-057 `rate-limit-fallback.json` 형식 precedent) `incident_count: 0` 측정.
  - **source 2-ii (Layer 2 warning)**: `scripts/check-no-atlassian.sh` 실행 — Layer 2 grep warning 0건 확인.

3-tuple 모두 정량 명시 (ADR-058 §결정 3 의무 정합) — "충분히 안정화되면" / "임시" / "한시적" 등 모달 어휘 0건. metric source 는 ADR-095 §결정 1 closed-set 2-source (changelog mining + cron) 안에서만 표현 (자유 산문 metric 비대상).

**cron kpi 실 wire = 후속 carrier**: `docs/kpi/atlassian-allow-incident.json` 실 생성 + monthly cron workflow + 측정 script 는 본 ADR Wave 1 scope 외 (`mechanical_enforcement_actions: []` declaration-only). ADR-095 §결정 2 (sunset metric dashboard Wave 1 = declaration-only) + ADR-082 §결정 6 retain pattern 답습 — cron 도입 전까지 3-tuple 형식 declare 가 manual 1차 안전망 + DesignReview lane MUST flag (behavioral directive).

### §결정 4 — spec-level reversal mechanism 신설 (extend) — formal-ADR-없는 predecessor 의 spec/plan 참조 sunset_justification 형식

**판정 = extend (reuse 만으로 불충분, 완전 신설도 아님).** ADR-058 §결정 5 / ADR-097 어느 쪽도 "formal ADR 없는 spec/plan-레벨 predecessor 의 reversal 을 어떻게 sunset_justification 처리하는가" 를 다루지 않는다. 본 §결정 4 가 이 case 의 mechanism 을 ADR-058 §결정 5 **일반 evidence-gate 경로 위에 specialize** 하여 신설한다 (extend). future formal-ADR-없는 reversal 재사용 anchor.

#### 문제 — ADR-097 §결정 3 의 "sunset 대상 ADR enumeration" 전제 부재

ADR-097 §결정 3 carrier-preserved sunset 은 "sunset 되는 각 ADR 의 효용 carry 경로 enumeration" 을 전제한다 — sunset 대상이 **formal ADR 객체** 임을 가정한다. 그러나 Atlassian 제거 predecessor 는 formal ADR carrier 가 0건 (git verified) 이므로, "sunset 할 ADR 객체" 자체가 부재하다. ADR-097 §결정 3 의 enumeration 전제를 그대로 적용할 수 없다.

#### 신설 mechanism — predecessor 식별을 spec/plan 참조로 대체

formal-ADR-없는 spec/plan-레벨 predecessor 의 reversal sunset_justification 은 다음 형식으로 처리한다 (extend):

1. **predecessor 식별 = spec/plan 참조** — formal ADR 번호 enumeration 대신, predecessor 결정을 담은 spec/plan 문서를 SSOT 참조로 명시한다. 본 case 의 predecessor = `docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md` (internal-docs dogfood, ADR-013 정합) — "atlassian MCP 의존 완전 제거 (hard remove), breaking change v0.x.0" 결정. formal ADR carrier 0건이 git verified 임을 sunset_justification 본문에 명시 (`git log --all -- 'docs/adr/ADR-*.md' | grep -i atlassian` = 0건).
2. **효용 carry 경로 = 평문 enumeration** — sunset 대상이 formal ADR 이 아니므로, "각 ADR 의 효용 carry" 대신 predecessor 결정의 **효용을 평문으로 enumeration + 각 효용의 carry 경로** 를 명시한다. 본 case: predecessor 효용 = "무단 Atlassian MCP 호출 0" → carrier shift = ADR-099 §결정 1 Layer 1 permission deny (grep → permission 격상, lossless). ADR-097 §결정 3 carrier-preserved 개념을 formal-ADR-free 영역에 적용.
3. **evidence-gate 통과 = ADR-058 §결정 5 일반 3-tuple** — §결정 3 의 metric/who/how 3-tuple 이 evidence-gate 입력. spec-level predecessor 도 일반 evidence-gate 경로 (면제 channel 비대상) 를 탄다.

**extend 경계 명시 (reuse ↔ 신설 disjoint)**:

| 구분 | 내용 | source |
|---|---|---|
| **reuse** | metric 형식 (changelog mining + cron / GA 12개월 baseline) | ADR-095 §결정 1/2 |
| **reuse** | carrier-preserved sunset 개념 (효용 lossless carry = carrier shift ≠ 약화) | ADR-097 §결정 3 (개념만, 면제 channel 발동 안 함) |
| **reuse** | sunset_justification 3-tuple schema + evidence-gate 원칙 | ADR-058 §결정 5 / ADR-064 §결정 7 |
| **신설 (extend)** | formal-ADR-없는 spec/plan-레벨 predecessor reversal 의 sunset_justification 처리 mechanism (predecessor 식별을 spec/plan 참조로 대체, 효용 carry 를 평문 enumeration 으로) | 본 §결정 4 |

본 mechanism 신설 자체는 **강화 방향** (governance 표현력 확장 — 기존에 다루지 못하던 case 의 1st-class 표현 획득) 이다 (ADR-064 §결정 7 evidence-gated symmetric — 강화 방향). 따라서 mechanism 자체의 sunset_justification 은 불요 (frontmatter `sunset_justification: null` 정당). 본 ADR 이 **정당화하는 약화** (Atlassian-allow Layer 2 lint) 의 evidence 는 §결정 3 에 별도 명시 — mechanism 신설(강화) ↔ 정당화 대상 약화(Layer 2 lint) 는 disjoint layer.

## 결과

### 긍정

- ADR-099 가 위임한 Atlassian-allow ratchet 약화 (Layer 2 lint) 의 evidence-gate 통과 anchor 확립 — §결정 3 의 정량 3-tuple 이 ADR-058 §결정 5 (post-CFP-1149 evidence-gate) 입력 충족.
- formal-ADR-없는 spec/plan-레벨 predecessor reversal 의 sunset_justification mechanism 1st-class 표현 획득 (§결정 4 extend) — future 동형 case 재사용 permanent anchor (강화 방향, governance 표현력 확장).
- Layer 1 (permission deny) carrier-preserved 보존 명시 — v0.8 security 효용이 grep → permission layer 로 lossless 격상됐음을 약화 정당화 범위에서 명시 제외 (Layer 2 lint 한정). ADR-099 §결정 1 / ADR-100 §해소 기준 정합.
- ADR-097 면제 channel 비대상 결정의 일반 evidence-gate 경로 확정 — closed-set AND 조건 a 미충족 case 의 sunset_justification 경로를 명시 (면제 channel 오용 차단).
- Epic-A Wave 1 (S1 lint 역전 + S2 Confluence SSOT + S3 verify-before-trust + S4 약화 정당화) governance foundation 완결 — S1 이 위임한 약화 정당화를 S4 가 닫음.

### 부정 / trade-off

- spec-level reversal mechanism (§결정 4) 의 실 적용 빈도 낮음 (formal-ADR-없는 reversal = 저빈도 governance event). 그러나 anchor 부재 시 매 formal-ADR-free reversal 마다 ad-hoc paradox 재논쟁 = governance 비용. anchor 도입이 1회성 비용으로 future 재논쟁 차단 (trade-off 정당, ADR-097 §결과 동형 rationale).
- cron kpi (`docs/kpi/atlassian-allow-incident.json`) Wave 1 부재 (`mechanical_enforcement_actions: []`) — §결정 3 의 metric source 2 (cron 자동 측정) 는 형식 declare 만, 실 dashboard json + cron workflow 는 후속 carrier. cron 도입 전까지 changelog mining (source 1) + manual incident/warning 확인이 1차 안전망 + DesignReview lane MUST flag. pattern_count >= 2 재발 시 follow-up CFP MUST promote to mechanical (ADR-082 §결정 6 / ADR-095 §결정 2 retain rationale 답습).
- baseline GA 12개월 grace (K8s deprecation policy 차용) — Layer 1 deny 무위반 12개월 확인까지 약화 정당화가 metric 차원에서 완성 안 됨. 단 본 ADR 의 약화 정당화 (evidence-gate 통과) 는 changelog mining (reversal 완료 marker) 으로 즉시 성립 (Epic-A 의도적 reversal 결정 자체가 도입 사유 무효화 evidence) — 12개월 baseline 은 carrier 효용 lossless 의 **사후 정식 확인** 차원 (약화 발동 차단이 아니라 carrier shift 검증).
- evidence-gate framing 의 cognitive 부하 — "약화 차단 극복" 이 아니라 "약화 evidence-gate 통과" 라는 post-CFP-1149 재정의를 reader 가 이해해야 함. 완화 = §컨텍스트 evidence-gate framing 단락 + §결정 2 명시 (차단 아님, evidence 입력 충족).
- ADR file 명 (`ratchet-weakening-governance-anchor`) ↔ 본문 framing (evidence-gate 통과) 표면 불일치 — file 명은 reservation 확정값 유지. 완화 = §상태 / §컨텍스트 에서 file 명 vs framing 분리 명시.

## 해소 기준

N/A — permanent policy (`is_transitional: false`). spec-level reversal sunset mechanism (§결정 4) 은 영구 거버넌스 anchor — future formal-ADR-없는 predecessor reversal 재사용. 본 ADR 이 codify 하는 mechanism 자체는 강화 방향 (governance 표현력 확장, 약화 아님) → mechanism 자체의 sunset_justification 불요.

**약화 정당화 layer 분리 명시**: 본 ADR 의 **mechanism 신설** (§결정 4 spec-level reversal 형식) 은 강화 방향 (frontmatter `sunset_justification: null` 정당). 본 ADR 이 **정당화하는 약화** = ADR-099 §결정 1 Layer 2 lint allowlist 확장 (Atlassian-allow) — 그 약화의 evidence 는 §결정 3 의 3-tuple 에 명시 (frontmatter sunset_justification 과 별개 layer). 본 ADR = 약화 정당화 anchor 이지, 본 ADR 자체가 약화되는 것이 아니다. Layer 1 (permission deny) + ADR-100 데이터 흐름 (Confluence readable) 영역은 약화 정당화 비대상 (carrier-preserved + 순수 강화).

amendment 시 evidence-grounded justification 의무 (ADR-064 §결정 7 evidence-gated symmetric, post-CFP-1149) — 강화 방향 (예: spec-level reversal mechanism scope 정밀화 / 3-tuple metric source 강화 / cron kpi mechanical 승격) 은 pattern_count / incident evidence. 약화 방향 (예: spec-level reversal mechanism 무자격 영역 확장 / 3-tuple 정량 의무 완화 / Layer 1 을 약화 대상에 포함) 은 ADR-058 §결정 5 (post-CFP-1149 evidence-gate) 의 약화 방향 evidence (metric / 평가 / 환경 변화 / pattern obsolescence) 의무. 양방향 evidence-gate 동등 적용 (비대칭 제거).

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 인접 (Layer 1 permission deny carrier-preserved + Atlassian token secret boundary = security guard, ADR-099/100/101 cross-ref). 단 category = governance (ratchet 약화 evidence-gate + spec-level reversal mechanism 거버넌스 결정 본체) — security 차단 패턴은 ADR-099 Layer 1 permission carrier + ADR-101 trust boundary 로 보존.

## 관련 파일

- `docs/adr/ADR-099-atlassian-allow-redefinition.md` — §결정 4/4-A 약화 정당화 위임 source (본 ADR 이 위임 받음). Layer 1/2 분리 + ADR-097 면제 channel 비대상 + extend 판정 SSOT
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — §결정 5 (CFP-1149 Amendment 1 evidence-gate 재정의) 일반 sunset_justification 3-tuple 경로 + §결정 3 정량 의무
- `docs/adr/ADR-064-decision-principle-mandate.md` — §결정 7 (CFP-1149 Amendment 8 evidence-gated symmetric ratchet) — 약화 방향 evidence-gate 동등 적용
- `docs/adr/ADR-095-sunset-metric-standardization.md` — sunset metric 형식 reuse (changelog mining + cron 2-source closed-set / K8s GA 12개월 baseline)
- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — 면제 channel 비대상 (§결정 1 조건 a 미충족). carrier-preserved sunset 개념(§결정 3)만 cross-ref (개념 reuse, 면제 channel 발동 안 함)
- `docs/adr/ADR-100-confluence-doc-ssot-recognition.md` — sister W1 S2 (MERGED). §해소 기준 "ADR-102 약화 정당화 = Layer 2 lint 한정" cross-ref 확정 (Layer 1/데이터 흐름 비대상)
- `docs/adr/ADR-101-verify-before-trust-confluence-rest.md` — sister W1 S3 (MERGED). 순수 security 강화 (약화 0건) → 본 ADR 약화 정당화 비대상. cross-ref only
- `docs/adr/ADR-103-git-confluence-sync-mechanism.md` — W4 Layer 1 narrow allow wire owner (**reserved — 본 commit 시점 미작성**, forward cross-ref)
- `scripts/check-no-atlassian.sh` — ADR-099 §결정 1 Layer 2 lint (본 ADR 약화 정당화 대상, Layer 2 한정). source 2-ii 측정 대상
- `.claude/settings.json` — Layer 1 `permissions.deny: ["mcp__atlassian", "mcp__atlassian__*"]` carrier-preserved (약화 대상 아님). source 2-i 측정 대상
- `CHANGELOG.md` — changelog mining metric source (ADR-092 SSOT) — Atlassian 재결합 reversal 완료 marker (source 1)
- `docs/kpi/atlassian-allow-incident.json` — cron kpi (ADR-057 `rate-limit-fallback.json` 형식 precedent, 실 wire = 후속 carrier). source 2 dashboard
- `docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md` — predecessor (v0.7→v0.8 Atlassian 완전 제거, spec/plan 레벨, formal ADR carrier 0건 — §결정 4 spec/plan 참조 식별 대상)
- `docs/adr/ADR-RESERVATION.md` — row 102 reserved → active 전환
