---
adr_number: 101
title: verify-before-trust Confluence REST ground-truth — Confluence 응답 무결성 검증 (SSRF / 응답 변조 boundary, ADR-070 sub-domain 확장)
status: Accepted
category: security
date: 2026-05-22
carrier_story: CFP-1226
parent_epic: CFP-1146
related_stories:
  - CFP-1226     # 본 carrier (Epic-A Wave 1 Story-3)
  - CFP-1146     # umbrella Epic-A (Atlassian suite 재결합 governance reversal)
related_adrs:
  - ADR-070      # verify-before-trust (외부 worker output) — 본 ADR = ADR-070 D1/D3 의 Confluence REST output sub-domain instantiate (Codex output → Confluence REST output, 동일 axis = 외부 source output verify). D5 declaration-only retain pattern 답습
  - ADR-100      # Confluence doc SSOT 인정 (sister, W1 S2 MERGED) — §결정 5 가 본 ADR-101 을 trust boundary 무결성 owner 로 forward cross-ref. ADR-100 §결정 1 Confluence = SoR-docs authoritative (응답 변조 → governance state poisoning 비대칭 근거) + §결정 4 Layer 1 settings.json deny (SSRF Layer 1 방벽)
  - ADR-099      # Wave 1 Story-1 (sister) — §결정 5 trust boundary (MCP endpoint SSRF / 응답 변조 surface) 가 ADR-101 ground-truth verify 로 위임. §결정 1 Layer 1 permission deny = SSRF 1차 방벽 (본 ADR Layer 2 = 정식 채널 응답 무결성)
  - ADR-103      # git↔Confluence sync mechanism — 본 ADR policy / ADR-103 mechanism 분리. 실 hash 알고리즘 / Confluence property schema / base_url 도메인 allowlist (SSRF Layer 3) 실 wire owner. 본 commit 시점 reserved (W4 carrier, 미작성 — forward cross-ref)
  - ADR-082      # write-time self-write verification — forward cross-ref (ADR-103/102) reserved 명시 (미작성 anchor 단언 금지) + §결정 6 declaration-only retain pattern (Wave 1 declare / Wave 2 wire)
  - ADR-064      # decision principle mandate — §self-application top-down ratchet (순수 security 강화 = 약화 아님, sunset_justification null 정당) + §결정 3 룰 2 (권장 1 + 대안 1)
  - ADR-058      # ADR sunset criteria mandate — §결정 7 보안 ADR presumption false 강화 (category security) + §결정 5 ratchet (강화 방향만 허용)
  - ADR-068      # boundary completeness invariants — I-1 (verify API contract semantic) / I-2 (3-layer SSRF chain cross-module propagation) / I-3 (dual-layer verify 무조건 적용 guard placement) / I-4 (wording SSOT)
related_files:
  - docs/adr/ADR-100-confluence-doc-ssot-recognition.md                           # §결정 5 가 본 ADR 을 trust boundary 무결성 owner 로 forward cross-ref (검증 완료)
  - docs/adr/ADR-099-atlassian-allow-redefinition.md                              # §결정 5 MCP endpoint SSRF / 응답 변조 boundary 위임 + §결정 1 Layer 1 permission deny (SSRF 1차 방벽)
  - docs/adr/ADR-070-codex-verify-before-trust.md                                 # 본 ADR = D1/D3 Confluence REST output sub-domain instantiate
  - docs/adr/ADR-103-git-confluence-sync-mechanism.md                            # policy / mechanism 분리 — 실 hash 알고리즘 / property schema / base_url allowlist 실 wire owner (reserved — W4 carrier, 본 commit 시점 미작성)
  - .claude/settings.json                                                        # §결정 3 SSRF Layer 1 (ADR-100 §결정 4 mcp__atlassian deny baseline) cross-ref — 실 wire = Phase 2 S2/S3 carrier
  - docs/adr/ADR-RESERVATION.md                                                  # row 101 reserved → active 전환
mechanical_enforcement_actions: []   # declaration-only Wave 1 — §결정 1 3-anchor cross-check + dual-layer verify + §결정 2 read/write disjoint narrow-allow + §결정 3 SSRF Layer 3 base_url allowlist 실 wire = ADR-103 (W4 carrier). 실 hash 알고리즘 / Confluence property schema = ADR-103 owner. ADR-082 §결정 6 / ADR-070 §D5 / ADR-100 retain pattern (Wave 1 declare / Wave 2 wire). pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier
is_transitional: false   # permanent security — Confluence REST 응답 무결성 verify (SSRF / 응답 변조 boundary) 는 Atlassian 재결합 후 영구 security 정책 방향. 3-anchor AND cross-check + dual-layer verify + governance state poisoning 차단 = 순수 security 강화 (약화 아님). ADR-058 §결정 7 보안 ADR presumption false 강화
sunset_justification: null   # is_transitional false — 본 ADR 의 verify-before-trust Confluence REST 결정은 영구 + 순수 security 강화 (governance state poisoning 차단). ADR-070 D1/D3 외부 source output verify axis 의 Confluence sub-domain 확장 = 강화 방향. 약화 (3→single anchor / Orchestrator 2차 verify 면제 / git→Confluence SoR 역전) = ADR-058 §결정 5 sunset_justification 의무로 차단
amendment_log: []
---

# ADR-101 — verify-before-trust Confluence REST ground-truth (SSRF / 응답 변조 boundary)

## 상태

`Accepted` (2026-05-22 KST) — CFP-1226 carrier (Epic-A Wave 1 Story-3). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 / ADR-100 row 100 / ADR-099 row 99 chief author precedent 정합). 별도 Story file 없음 (Wave 1 Story-1 ADR-099 / Story-2 ADR-100 답습 — ADR 가 §3 설계 SSOT). dogfood-out (ADR-013): change-plan 은 wrapper repo 에 commit 안 함, ADR 만 wrapper commit.

## 컨텍스트

### 동인

ADR-100 (W1 S2, MERGED) 가 Confluence 를 wrapper governance docs 의 **authoritative readable source** 로 인정했다 (SoR-docs). ADR-100 §결정 5 는 그 응답을 신뢰하기 전 무결성 검증 책임을 **ADR-101 ground-truth verify owner** 로 forward cross-ref 했다. 본 ADR-101 = 그 owner — Confluence REST 응답을 wrapper governance state 에 반영하기 전 git-side ground truth 와 cross-check 하는 **정책 layer** 다.

핵심 비대칭 (가장 심각): ADR-100 §결정 1 이 Confluence 를 SoR-docs authoritative 로 격상했으므로, Confluence 응답이 변조되면 변조된 doc 이 권위 readable source 로 wrapper governance state 에 반영된다 — **governance state poisoning**. 단순 stale read 보다 심각하다 (authoritative source 의 무결성 자체가 무너짐). 따라서 본 ADR 은 응답 무결성 verify 를 outbound REST 채널의 normative invariant 로 codify 한다.

본 ADR 의 placement = **ADR-070 sub-domain 확장** (ArchitectAnalyst prior-art verify 완료): ADR-070 D1/D3 는 외부 worker(Codex) output 의 ground truth 를 Orchestrator direct file Read 로 verify 하고 mismatch 시 reject 한다. 본 ADR-101 은 동일 axis (외부 source output verify) 를 **Confluence REST output** 으로 instantiate 한다 (Codex output → Confluence REST output). ADR-073 (Orchestrator assumption verify) / ADR-082 (internal lane agent self-write verify) 와는 **disjoint** (verify 주체 / 대상 상이). 따라서 신규 verify layer 가 아니라 ADR-070 의 sub-domain 이며, CLAUDE.md 4-layer governance 표에 5번째 row 를 신설하지 않고 ADR-070 (2) entry 안 1줄 cross-ref 로 fold 한다 (ADR-082 §결정 1 layer disjoint anchor 보존).

### verified-via — 본 ADR 의 모든 사실 인용 검증

본 ADR 의 모든 §결정 / line / §N 인용은 ground truth direct Read 위에서 작성됐다 (ADR-082 §결정 2 write-time self-write verification 정합).

> verified-via: Read docs/adr/ADR-100 (worktree HEAD `c306127`) L177-199 §결정 5 — Confluence REST = outbound-only + read 우선 / write 는 ADR-103 단일 진입점 / `mcp__atlassian__*` endpoint = SSRF + 응답 변조 surface, boundary 검증 책임 = ADR-101 ground-truth verify (ADR-070 verify-before-trust 외부 worker output 정합). Layer 1 permission deny (§결정 4) = SSRF 1차 방벽, ADR-101 = 정식 채널 응답 무결성 (2차 layer). L80 §결정 1 — Confluence = SoR-docs authoritative readable (응답 변조 → governance state poisoning 비대칭 근거). L17 frontmatter related_adrs — ADR-101 = "trust boundary (SSRF / 응답 변조 무결성 검증 owner). 본 commit 시점 reserved (S3 carrier, 미작성)".
> verified-via: Read docs/adr/ADR-070 (worktree) L118-156 §결정 D1 + D1 expansion / L181-208 §결정 D3 — D1 = Orchestrator 가 외부 worker 발화 evidence 를 own working directory file Read 로 verify, 외부 fetch 결과 자체는 trust 대상 아님. D3 = evidence mismatch 시 verdict reject (false positive) + override rationale 4종 (finding verbatim / direct Read verify 결과 / mismatch 영역 / 후속 동작). L234-248 §결정 D5 — declaration-only retain (mechanical lint 부재, 본문 SSOT, evidence-checks-registry append 면제). `mechanical_enforcement_actions: []`.
> verified-via: Read docs/adr/ADR-099 (worktree) L202-210 §결정 5 — MCP endpoint = SSRF + 응답 변조 surface, boundary 검증 책임 = ADR-101 ground-truth verify. §결정 1 Layer 1 permission deny = SSRF 1차 방벽 (무단 endpoint 호출 차단), ADR-101 = 정식 채널 응답 무결성 (2차 layer). frontmatter (L4-30) category: governance / is_transitional: false / sunset_justification: null format precedent.
> verified-via: Read docs/adr/ADR-RESERVATION.md (worktree) L143 — row 101 = CFP-1146, status `reserved`, ADR file = `ADR-101-verify-before-trust-confluence-rest.md` (reservation 확정 파일명 정합). row 102 (ADR-102 ratchet 약화 governance anchor, S4) / row 103 (ADR-103 git↔Confluence sync mechanism, W4) = 모두 `reserved` (미작성 — forward cross-ref).
> verified-via: Bash `grep CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS .claude/settings.json` (worktree) L3 = `"1"` — agent-teams enabled 활성 (§결정 1 dual-layer verify 의 Orchestrator 2차 verify 가 sibling teammate 전파 영역과 disjoint, ADR-100 §결정 5 SendMessage leak surface 실재 정합).
> verified-via: Bash `ls docs/adr/ADR-101*` (worktree) — file 부재 확인 (신규 작성).

### forward cross-ref reserved 명시 (ADR-082)

본 ADR 은 **ADR-103 (W4 git↔Confluence sync mechanism)** 와 **ADR-102 (S4 ratchet 약화 governance anchor)** 를 cross-ref 하나, 두 ADR 은 **본 commit 시점 미작성 (reserved)** 이다 (ADR-RESERVATION row 102/103 status `reserved` verified). 따라서:

- **ADR-103** = 본 ADR §0 verify 결과 미작성 영역 — 실 hash 알고리즘 / Confluence property schema / base_url 도메인 allowlist (SSRF Layer 3) 의 empirical 결정은 "(W4 ADR-103 carrier — 본 commit 시점 미작성, reserved)" 로만 기술하며 그 §결정 N 내용을 존재하듯 단언하지 않는다.
- **ADR-102** = S4 ratchet 약화 정당화 anchor (Layer 2 lint 영역 한정, ADR-099 §결정 4-A) — 본 ADR-101 은 **순수 security 강화** (약화 0건) 이므로 ADR-102 약화 정당화 경로의 **비대상** 이다. ADR-102 cross-ref 는 "약화 정당화 경로 비대상 명시" 로만 기술.

ADR-100 (sister, MERGED) 는 본 commit 시점 작성 완료 (reserved 아님) — §결정 5 의 ADR-101 owner 위임은 verified 인용.

## 결정

### §결정 1 — verify-before-trust Confluence REST (ADR-070 D1/D3 instantiate — dual-layer verify 주체 + 3-anchor AND + mismatch reject)

Confluence REST 응답을 wrapper governance state 에 반영하기 전 git-side ground truth 와 cross-check 한다 (ADR-070 D1 외부 source output verify 의 Confluence sub-domain instantiate). 외부 fetch 결과 자체는 trust 대상 아니다 — git source 가 SoR-work invariant 이며, Confluence 응답은 ground truth 확정 후에만 governance state 에 반영한다.

#### governance state poisoning 비대칭 (verify 정당성)

ADR-100 §결정 1 이 Confluence 를 SoR-docs authoritative readable 로 격상했으므로 (verified L80), 응답 변조 시 변조된 doc 이 권위 readable source 로 governance state 에 반영된다 = **governance state poisoning** (가장 심각). 단순 read staleness 보다 심각하다 — authoritative source 무결성 자체가 무너지므로 verify-before-trust 가 normative invariant 로 codify 될 정당성 충족 (ADR-070 systemic 원인 sentinel 패턴 정합 — 외부 source 무신뢰 boundary).

#### dual-layer verify (single-layer collapse 금지 — SecurityArch mandate)

verify 주체는 **2 layer 다** (ADR-070 D1 verify 주체 invariant 보존):

| Layer | verify 주체 | 책임 | reserved 상태 |
|---|---|---|---|
| **1차** | sync agent | Confluence REST 응답 수신 시점 1차 무결성 verify | wire owner = ADR-103 (W4, 본 commit 시점 미작성) |
| **2차** | Orchestrator | governance state 반영 전 ground truth 확정 (ADR-070 D1 verify 주체 invariant — 외부 worker output 의 ground truth 는 Orchestrator 가 own working directory 안에서 확정) | 본 ADR-101 policy SSOT |

**single-layer collapse 금지 invariant**: sync agent 1차 verify 만으로 governance state 반영 PASS 금지. Orchestrator 2차 verify 가 무조건 (unconditional) 적용된다 (ADR-068 I-3 — guard placement intent = "governance state 반영 진입 시점 무조건", 특정 path 한정 아님). agent-teams `AGENT_TEAMS=1` 활성 하 (verified) sync agent 응답이 SendMessage 로 sibling 에 전파되더라도 (ADR-100 §결정 5 leak surface) Orchestrator 2차 verify 는 그 전파 채널과 disjoint — Orchestrator 가 own working directory git source 로 직접 확정한다.

#### 3-anchor AND cross-check (single-anchor 신뢰 금지 — SecurityArch mandate)

응답 무결성은 다음 **3 anchor 의 AND** 로 cross-check 한다 (defense-in-depth, single-anchor 신뢰 금지):

| Anchor | 비교 대상 | 탐지 영역 |
|---|---|---|
| **(A) content hash** | 응답 doc body 정규화 hash ↔ 마지막 sync commit 의 git source hash | doc body 변조 |
| **(B) version 메타** | Confluence page version ↔ git 기록의 sync version | replay (구 버전 응답 재사용) 탐지 |
| **(C) sync commit SHA 표식** | Confluence property 의 SHA 표식 ↔ git log SHA | lineage 무결성 (응답이 어느 git commit 에서 sync 됐는가) |

3 anchor 가 모두 (AND) match 할 때만 응답 무결. 1+ anchor mismatch = 무결성 위반 (§아래 reject). 실 hash 알고리즘 (정규화 방식) / Confluence property schema (SHA 표식 저장 형식) 는 **[hypothesis] Atlassian REST page schema 미verify** — ADR-103 owner (empirical verify 후 결정, 본 commit 시점 reserved).

#### mismatch 행동 (ADR-070 D3 instantiate)

1+ anchor mismatch 검출 시 (ADR-070 D3 verdict reject 흐름의 Confluence sub-domain instantiate):

1. 응답을 governance state 에 **반영 안 함 (reject)** — 변조 가능성 있는 응답으로 authoritative readable source 를 오염시키지 않음.
2. **mismatch audit log** — 어느 anchor (A/B/C) 가 mismatch 인지 + 응답 verbatim + git source verbatim 기록.
3. **git source 우선 정정** — git = SoR-work invariant (ADR-100 disjoint axis). Confluence readable 이 stale / 변조 시 git source 가 우선, Confluence 측 재sync 는 ADR-103 mechanism 위임.
4. **override rationale 4종** (ADR-070 D3 형식): (a) Confluence 응답 evidence verbatim / (b) Orchestrator direct git source verify 결과 verbatim / (c) mismatch anchor 영역 명시 / (d) reject 후속 동작 (재sync 요청 / 사용자 escalation).

**거절된 대안 §결정 1 (ADR-064 §결정 3 룰 2 — 권장 + 대안)**: 권장 = dual-layer + 3-anchor AND (defense-in-depth). 대안 = single-anchor (content hash 만) + sync agent 1차 verify 만 (Orchestrator 2차 면제) — replay / lineage 위조 탐지 부재 + ADR-070 D1 verify 주체 invariant 위배 (외부 worker 자체 verify 신뢰) → reject (governance state poisoning 비대칭상 부족).

### §결정 2 — outbound-only + read/write narrow-allow disjoint

Confluence REST 채널은 **outbound-only** 다 — Confluence → wrapper inbound webhook 0 (listening endpoint 부재 → inbound 공격 surface 0). 호출 방향은 wrapper → Confluence 단방향.

#### read/write tool set disjoint narrow-allow

- **read 우선** (빈번 — governance docs readable 참조) — read tool set 에 §결정 1 3-anchor verify 적용.
- **write** = ADR-103 (sync mechanism) **단일 진입점** narrow allow (W4 defer — 사용처 0 시점 선제 부여 reject, 최소권한).
- **read tool set ↔ write tool set disjoint narrow-allow** (ADR-068 I-1 — API contract semantic completeness): read 권한이 write 권한을 **상속 금지**. read-only 채널이 write 권한을 갖지 않도록 tool set 을 분리 정의 (실 분리 mechanism = ADR-103 owner — Claude Code permissions deny precedence 우회 / scope 분리는 ADR-100 §결정 4 deny precedence 충돌 경고 정합, ADR-103 empirical verify).

#### 약화 차단

역방향 push (Confluence → wrapper inbound) 도입 = inbound 공격 surface 신설 = 약화 (ADR-058 §결정 5 sunset_justification 의무). read 가 write 권한 상속 = 최소권한 약화 (동일 차단).

### §결정 3 — SSRF 3-layer chain (Layer 1 ADR-100 / Layer 2 ADR-101 / Layer 3 ADR-103 reserved)

`mcp__atlassian__*` endpoint 의 SSRF (내부 자원 도달) surface 는 **3-layer chain** 으로 방어한다 (ADR-068 I-2 — cross-module propagation completeness, 각 layer owner 명시):

| Layer | 방벽 | owner | 상태 |
|---|---|---|---|
| **Layer 1** | settings.json `mcp__atlassian` deny baseline (무단 endpoint 호출 자체 차단) | ADR-100 §결정 4 | 실 wire = Phase 2 S2/S3 carrier |
| **Layer 2** | **본 ADR-101 — 정식 채널 응답 무결성 verify** (§결정 1 3-anchor AND + dual-layer) | **ADR-101 (본 ADR) policy SSOT** | 본 commit |
| **Layer 3** | base_url 도메인 allowlist (sandbox `allowedDomains`, network egress 제한 — 정식 채널이라도 허용 도메인 외 호출 차단) | ADR-103 | reserved (W4 carrier, 본 commit 시점 미작성) |

본 ADR-101 = **Layer 2 owner**. Layer 1 (무단 호출 차단) 와 Layer 3 (도메인 egress 제한) 은 각각 ADR-100 / ADR-103 owner — propagation chain 의 본 ADR 책임은 Layer 2 (정식 채널 응답 무결성) 한정. Layer 3 base_url 도메인 allowlist 실 값 / sandbox config 는 ADR-103 empirical verify (본 commit 시점 reserved).

### §결정 4 — ADR-101 policy / ADR-103 mechanism 분리 (declaration-only Wave 1)

본 ADR-101 = **"신뢰 전 무엇을 verify"** (정책 / 의무):

- verify anchor 종류 (§결정 1 A/B/C 3-anchor 의미)
- dual-layer verify 주체 (1차 sync agent / 2차 Orchestrator)
- 3-layer SSRF chain 구조 (Layer 1/2/3 owner)
- mismatch reject 흐름 + override rationale 4종

ADR-103 = **"verify 를 코드가 어떻게"** (mechanism):

- REST client 구현 + 실 hash 알고리즘 (정규화 방식) + Confluence property schema (SHA 표식 저장 형식)
- sandbox config (base_url 도메인 allowlist 실 값, SSRF Layer 3)
- sync agent narrow allow wire (deny precedence 충돌 우회 / scope 분리)

**`mechanical_enforcement_actions: []` declaration-only Wave 1** (ADR-082 §결정 6 / ADR-070 §D5 / ADR-100 retain pattern): 본 ADR 의 verify 의무는 정책 layer normative anchor 만 — 실 mechanical wire (hash 비교 코드 / property schema validator / base_url allowlist) 는 ADR-103 (W4 carrier). **pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier** (ADR-070 §D5 declaration-only retain precedent chain — runtime probe 영역은 static doc lint 영역과 type mismatch, sentinel 누적 시 carrier 발의).

## 결과

### 긍정

- Confluence REST 응답 무결성 verify normative anchor 확립 — ADR-100 SoR-docs authoritative 격상이 도입한 governance state poisoning surface 를 dual-layer + 3-anchor AND 로 차단.
- ADR-070 sub-domain 확장 — 외부 source output verify axis 의 Confluence instantiate. 신규 verify layer 신설 0건 (CLAUDE.md 4-layer 표 5번째 row 불요, ADR-070 (2) entry fold) → layer disjoint anchor 무손상 (ADR-082 §결정 1).
- 3-layer SSRF chain 명시 — Layer 1 (ADR-100 deny) / Layer 2 (본 ADR 응답 verify) / Layer 3 (ADR-103 도메인 allowlist) 의 owner / 책임 / reserved 상태 cross-module propagation 명시 (ADR-068 I-2).
- 순수 security 강화 — dual-layer (single-layer collapse 금지) + 3-anchor AND (single-anchor 신뢰 금지) + read/write disjoint narrow-allow + outbound-only (inbound surface 0) = 약화 0건 (ADR-064 top-down ratchet).
- policy / mechanism 분리 — ADR-101 (무엇을 verify) / ADR-103 (어떻게) 명확 boundary, double-amendment 회피 (실 hash 알고리즘 / property schema 미정 영역을 ADR-103 위임).

### 부정 / trade-off

- **dual-layer verify 비용** — sync agent 1차 + Orchestrator 2차 = verify 2회 (governance state 반영 전 Orchestrator round-trip). 완화 = governance state poisoning 비대칭상 정당 (authoritative source 무결성 > verify 비용). single-layer collapse 시 ADR-070 D1 verify 주체 invariant 위배 — 비용 회피 reject.
- **ADR-103 mechanism 의존** — 실 hash 알고리즘 / Confluence property schema / base_url allowlist 가 본 ADR 미정 (ADR-103 reserved). 완화 = §결정 4 명시 policy/mechanism 분리 + [hypothesis] Atlassian REST page schema 미verify 표기 (ADR-103 empirical verify 위임). 본 ADR commit 시점 verify 의무는 정책 layer 만 enforce.
- **3-anchor AND 의 staleness window** — git → Confluence sync window 동안 version 메타 (B) / SHA 표식 (C) 가 transient mismatch 가능. 완화 = mismatch reject + git source 우선 정정 (§결정 1) — staleness 시 git 우선이 안전 default. 단 sync 빈도 / window = ADR-103 owner.
- **forward cross-ref (ADR-103/102) reserved** — ADR-103 (mechanism) 미작성 상태에서 본 ADR 이 실 wire 위임 + ADR-102 (약화 정당화) 비대상 명시. 완화 = §컨텍스트 forward cross-ref reserved 명시 (미존재 anchor 단언 금지, ADR-082) + ADR-RESERVATION row 102/103 status `reserved` verified.
- **mechanical_enforcement_actions `[]` Wave 1 declaration-only** — verify 의무 mechanical wire = ADR-103 (W4). pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier (ADR-070 §D5 / ADR-082 §결정 6 retain pattern).

## 해소 기준

N/A — permanent policy (is_transitional: false). Confluence REST 응답 무결성 verify (SSRF / 응답 변조 boundary) 는 Atlassian 재결합 후 영구 security 정책 방향. dual-layer + 3-anchor AND cross-check + governance state poisoning 차단 = 순수 security 강화 (약화 아님) → 약화 정당화 불요.

**약화 정당화 경로 비대상 (ADR-099 §결정 4-A 정합)**: 본 ADR-101 은 **순수 security 강화** (Layer 2 응답 무결성 verify 신설, additive) 이므로 S4 ADR-102 sunset_justification (ratchet 약화 정당화) 경로의 **비대상** 이다. ADR-102 약화 정당화는 Layer 2 lint (Atlassian-allow grep allowlist) 영역 한정 (ADR-099 §결정 4-A) — 본 ADR-101 의 응답 무결성 verify (security guard) 영역은 ADR-102 약화 정당화 경로 비대상.

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: anchor 추가 — 4번째 anchor 도입 / dual-layer 강화 — 3차 verify layer / read scope 확장 — verify 적용 doc type 확대). 약화 방향 (예: 3-anchor → single-anchor 축소 / Orchestrator 2차 verify 면제 / git → Confluence SoR-work 역전 / read 가 write 권한 상속) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption false 강화 영역 (SSRF / 응답 변조 / governance state poisoning = security guard) — category = security (전체가 trust boundary 무결성 검증 본체). ADR-099 / ADR-100 (category governance, security 차단 패턴을 Layer 1 carrier 로 보존) 와 달리, 본 ADR-101 은 **전체가 security** 이므로 frontmatter category = security (보안 ADR presumption false 강화 정합).

## 관련 파일

- `docs/adr/ADR-100-confluence-doc-ssot-recognition.md` — §결정 5 가 본 ADR-101 을 trust boundary 무결성 owner 로 forward cross-ref (검증 완료, sister W1 S2 MERGED). §결정 1 Confluence SoR-docs authoritative (governance state poisoning 비대칭 근거) + §결정 4 Layer 1 deny (SSRF Layer 1)
- `docs/adr/ADR-099-atlassian-allow-redefinition.md` — §결정 5 MCP endpoint SSRF / 응답 변조 boundary 위임 + §결정 1 Layer 1 permission deny (SSRF 1차 방벽). §결정 4-A 약화 정당화 layer 분리 (본 ADR 비대상)
- `docs/adr/ADR-070-codex-verify-before-trust.md` — 본 ADR = D1/D3 Confluence REST output sub-domain instantiate (외부 source output verify 동일 axis). D5 declaration-only retain pattern 답습
- `docs/adr/ADR-103-git-confluence-sync-mechanism.md` — policy / mechanism 분리 — 실 hash 알고리즘 / Confluence property schema (SHA 표식) / base_url 도메인 allowlist (SSRF Layer 3) / sync agent narrow allow wire 실 결정 owner (**reserved — W4 carrier, 본 commit 시점 미작성**)
- `docs/adr/ADR-102-ratchet-weakening-governance-anchor.md` — S4 ratchet 약화 정당화 anchor — 본 ADR-101 은 순수 security 강화 = 약화 정당화 경로 **비대상** (Layer 2 lint 영역 한정, ADR-099 §결정 4-A). (**reserved — S4 carrier, 본 commit 시점 미작성**)
- `.claude/settings.json` — §결정 3 SSRF Layer 1 (ADR-100 §결정 4 `mcp__atlassian` deny baseline) cross-ref — 실 wire = Phase 2 S2/S3 carrier
- `docs/adr/ADR-RESERVATION.md` — row 101 reserved → active 전환
