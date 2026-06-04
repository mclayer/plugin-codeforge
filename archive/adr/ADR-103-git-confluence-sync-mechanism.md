---
adr_number: 103
title: git→Confluence sync mechanism — custom GitHub Action + 3-anchor hash-git-source + Option B narrow allow + walker §2.G post-walk hook + doc-locations confluence variant (declaration-only Wave 1)
status: Accepted
category: tooling-infrastructure
date: 2026-05-22
carrier_story: CFP-1250
parent_epic: CFP-1146
related_stories:
  - CFP-1250     # 본 carrier (Epic-A Wave 4 — git↔Confluence sync mechanism 결정)
  - CFP-1146     # umbrella Epic-A (Atlassian suite 재결합 governance reversal)
related_adrs:
  - ADR-099      # Wave 1 Story-1 (MERGED) — §결정 1 2-layer (Layer 1 mcp__atlassian permission deny / Layer 2 lint grep allowlist). 본 ADR §결정 3 narrow allow = Layer 1 의 "정식 sync agent narrow allow 대상" 실 결정 owner (ADR-099 §결정 1 Layer 1 위임)
  - ADR-100      # Wave 1 Story-2 (MERGED) — §결정 2 (doc-locations confluence variant / authoritative_source field 실 변경 = ADR-103 defer) + §결정 4 ("scope 분리 / managed-only 메커니즘 empirical verify = ADR-103 owner" — deny precedence 우회) + §결정 5 (sync agent output sanitization / token env-indirect = W4 위임). 본 ADR = 그 위임 owner
  - ADR-101      # Wave 1 Story-3 (MERGED) — §결정 1 3-anchor (A content hash / B version / C sync commit SHA) policy + dual-layer verify (1차 sync agent / 2차 Orchestrator) + §결정 3 SSRF Layer 3 (base_url 도메인 allowlist) + §결정 4 policy(101)/mechanism(103) boundary. 본 ADR = mechanism only — "무엇을 verify" 재정의 금지 invariant (ADR-101 §결정 4)
  - ADR-102      # Wave 1 Story-4 (MERGED) — ratchet 약화 evidence-gate anchor. 본 ADR §결정 3 Option B allow-by-omission = 유일 weakening surface → atlassian-tool-drift check 로 mitigate. allowlist 확장 약화 정당화 경로 = ADR-102 §결정 3 3-tuple (Layer 2 한정) cross-ref
  - ADR-013      # codeforge family dogfood-out — §결정 5 source-repo-resolver: sync source 가 wrapper repo (governance docs) + internal-docs repo (dogfood-out docs) 2-repo. ADR-013 §결정 1 KEEP (wrapper) / MOVE (internal-docs) 정합
  - ADR-041      # doc location registry — §결정 5 confluence variant / authoritative_source field 실 변경 (ADR-100 §결정 2 위임 받음). schema_version 1.0→1.1 MINOR. 단 declaration-only Wave 1 — 실 yaml 변경 = 후속 Phase
  - ADR-070      # verify-before-trust (외부 worker output) — §결정 2 3-anchor verify wire-point = read path gating (write 시 stamp / read 시 dual verify). Confluence REST output = D1/D3 instantiate (ADR-101 sub-domain). §D5 declaration-only retain pattern 답습
  - ADR-058      # ADR sunset criteria mandate — §결정 7 보안 ADR presumption 인접 (§결정 3/4 security boundary) / §결정 5 ratchet (Option B allow-by-omission 약화 surface = atlassian-tool-drift mitigate). is_transitional false (sync mechanism = 강화 방향)
  - ADR-064      # decision principle mandate — §self-application top-down ratchet (sync mechanism 신설 = 강화) + §결정 3 룰 2 (권장 1 + 대안 1). §결정 1 sync 구현체 / §결정 3 narrow allow 모두 권장+대안 형식
  - ADR-066      # PAT rotation policy — §결정 5 source-repo-resolver internal-docs repo cross-repo PAT scope (CODEFORGE_CROSS_REPO_PAT) cross-ref — dogfood-out docs sync source repo 접근
mechanical_enforcement_actions: []   # declaration-only Wave 1 — §결정 1 custom GitHub Action / §결정 2 3-anchor 실 hash 알고리즘 + Confluence property schema / §결정 3 Option B per-tool deny decomposition + atlassian-tool-drift check + sync agent home / §결정 4 SSRF dual-channel + token sanitization / §결정 5 walker §2.G MINOR bump + doc-locations confluence variant 실 변경 = 모두 후속 Phase (Epic body S13 + W5 carrier). ADR-082 §결정 6 / ADR-070 §D5 / ADR-100 / ADR-101 retain pattern (Wave 1 declare / Wave 2 wire). atlassian-tool-drift = 첫 promotion candidate (Option B allow-by-omission 유일 weakening surface), pattern_count >= 2 재발 시 follow-up CFP MUST promote to warning-tier evidence-checks-registry entry
is_transitional: false   # permanent tooling-infrastructure — git→Confluence one-way sync mechanism (custom GitHub Action + 3-anchor hash-git-source + Option B narrow allow + SSRF dual-channel) 은 Atlassian 재결합 후 영구 sync 정책 방향. sync 구현체 결정 + narrow allow scope 분리 + SSRF 3-layer chain Layer 3 = 강화 방향 (security boundary 신설 + 최소권한). 유일 약화 surface (Option B allow-by-omission) 은 atlassian-tool-drift check 로 mitigate (§결과 명시)
sunset_justification: null   # is_transitional false — sync mechanism 결정 자체는 영구 + 강화 방향 (sync 구현체 + narrow allow 최소권한 + SSRF Layer 3 + 3-anchor verify wire-point). ADR-101 policy 의미 약화 0건 (mechanism instantiate only, "무엇을 verify" 재정의 금지 invariant 보존). Option B allow-by-omission (신규 upstream atlassian tool 이 deny 열거 누락 시 자동 통과) = 유일 weakening surface → atlassian-tool-drift check 로 mitigate (verified snapshot 고정 + drift warning) — 약화 차단 mechanism 동반이므로 본 ADR 자체는 강화. amendment 시 sunset_justification 의무 (ADR-058 §결정 5) — 약화 방향 (one-way → bidirectional sync / 3-anchor → single-anchor / Option B narrow allow → 서버전체 allow) 차단
amendment_log:
  - amendment: 1
    date: 2026-05-24 KST
    carrier_story: CFP-1492
    parent_epic: CFP-1415   # Mega-Epic Confluence-as-derived-mirror governance standardization (CLOSED early, anomaly noted) / Sub-B parent: #1490 Confluence space IA migration + legacy backfill (MCP-direct deviation)
    direction: strengthening   # alternative routing path 추가 = ratchet 강화 (PRIMARY mark engine path 보존, carrier-preserved per ADR-097 §결정 3 정합)
    sunset_justification: null   # paradigm replacement 아님 (ADR-097 closed-set 3 조건 AND 미충족: 9+ ADR/contract 동시 sunset 0, 단일 atomic Epic carrier 0 — surgical deviation only). ADR-058 §결정 5 sunset_justification 의무 = ratchet 강화 방향이므로 N/A
    summary: "MCP-direct path codify as alternative routing rule + deviation declare schema 4-tuple + mark engine path #1320 retain for future PRIMARY (CFP-1146 W5-S17 #1310 + Sub-B S2.1 #1498 2 prior MCP-direct application 의 retroactive codify — precedent first, codify second). subagent OAuth limitation 명시 (Orchestrator inline path 의무 영역)."
  - amendment: 2
    date: 2026-06-01 KST
    carrier_story: CFP-1321
    parent_epic: CFP-1146   # umbrella Epic-A (Atlassian suite 재결합 governance reversal) — W5-S15 chief synthesis P1-1 보안 gap carrier
    direction: strengthening   # write-time permission 한계 정직 declare + read-path dual-layer verify 를 interim load-bearing 보상통제로 명시 강조 = ratchet 강화 (ADR-101 dual-layer verify 보존 + load-bearing 격상, 약화 surface 0건)
    sunset_justification: null   # 강화 방향 (보상통제 load-bearing 명시 + 예방 수정 Wave 2 carrier declare). ADR-058 §결정 5 sunset_justification 의무 = 강화 방향이므로 N/A. ADR-101 policy 의미 약화 0건 (§결정 1 dual-layer verify 재정의 0건, 이미 존재하는 verify 를 P1-1 맥락 load-bearing 으로 명시만). write-time prevention 미보장 = 정직 declare (agent file §7.6 미완화 위협 declare 정합) — 보호 강도 축소 아님 (기존 미wire 상태의 정직 문서화)
    summary: "sync agent write-time permission enforce 한계 명문화 (permissionMode: default 가 parent defaultMode: bypassPermissions 하 무효 — write 차단 실 enforce = disallowedTools + tools allowlist + settings deny 의존, 그 settings deny wire 자체가 §결정 3 후속 Phase deferred → write-time prevention 현재 구조적 미보장) + read-path dual-layer verify (§결정 2 / ADR-101 §결정 1) interim load-bearing 보상통제 명시 강조 (변조/무단 write = read path 3-anchor AND + Orchestrator 2차 independent verify dual-PASS gate 에서 catch → governance state poisoning 전 차단) + write-time prevention 예방 수정 후보 2종 (sync agent 별 session/process 실행 / settings sync-agent 전용 non-bypassPermissions profile 분리) = Wave 2 mechanical carrier declare. declaration-only Wave 1 (실 wire = 별 sub-CFP). #1321 W5-S15 P1-1 보안 gap carrier."
---

# ADR-103 — git→Confluence sync mechanism (custom GitHub Action + 3-anchor hash-git-source + Option B narrow allow)

## 상태

`Accepted` (2026-05-22 KST) — CFP-1250 carrier (Epic-A Wave 4, 5-slot bundle 5/5 마지막). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 / ADR-099 row 99 / ADR-100 row 100 / ADR-101 row 101 / ADR-102 row 102 chief author precedent 정합). 별도 Story file 없음 (Wave 1 Story-1~4 ADR-099/100/101/102 답습 — ADR 가 §3 설계 SSOT). dogfood-out (ADR-013): change-plan 은 wrapper repo 에 commit 안 함, ADR 만 wrapper commit.

**declaration-only Wave 1 invariant**: 본 ADR 은 sync mechanism 의 **설계 결정 SSOT** 다 (ADR-100/101/102/104 declaration-only Wave 1 패턴 답습). 실 sync 구현 (settings per-tool deny / sandbox config / sync agent 실 정의 / GitHub Action yml / doc-locations.yaml 실 변경 / walker §2.G 실 MINOR bump) = **후속 Phase / Story** (Epic body S13 + Wave 5 carrier). 본 ADR = 어떤 mechanism 을 쓸지 결정만, 실 wire 0건.

## 컨텍스트

### 동인

Epic-A Wave 1 (ADR-099 lint 역전 / ADR-100 Confluence SoR-docs 인정 / ADR-101 verify-before-trust Confluence REST / ADR-102 ratchet 약화 evidence-gate) 가 governance foundation 을 완결했다. 그러나 4 ADR 모두 **mechanism 결정을 ADR-103 (W4) 에 위임** 했다 — git 변경을 Confluence 로 실제로 어떻게 sync 하는가, narrow allow 를 deny precedence 충돌 없이 어떻게 wire 하는가, 3-anchor verify 의 실 hash 알고리즘 / Confluence property schema 는 무엇인가. 본 ADR-103 = 그 mechanism owner.

핵심 mechanism 질문 4종 (W1 ADR 위임):
1. **sync 구현체** — git markdown → Confluence push 를 무엇으로 구현하는가 (Forge / Connect / Exalate / custom GitHub Action).
2. **narrow allow scope 분리** — ADR-100 §결정 4 가 경고한 "deny precedence (서버전체 deny) 가 narrow allow 를 무조건 이긴다" 충돌을 어떻게 우회하는가.
3. **3-anchor 실 구현** — ADR-101 §결정 1 의 (A) content hash / (B) version / (C) sync commit SHA 를 실제로 무엇 위에 계산/저장하는가.
4. **doc-locations / walker 영향** — ADR-100 §결정 2 (confluence variant) + ArchitectAnalyst R5 (walker fold) 의 실 변경 형식.

### ADR-101 §결정 4 policy/mechanism boundary invariant (load-bearing)

본 ADR-103 = **mechanism only**. ADR-101 §결정 4 가 명시한 boundary 를 절대 보존한다 — ADR-101 = "신뢰 전 **무엇을** verify" (정책), ADR-103 = "verify 를 **코드가 어떻게**" (mechanism). 본 ADR 은 3-anchor 의 **AND 의미** / **dual-layer verify 주체 (1차 sync agent / 2차 Orchestrator)** 를 **재정의하지 않는다** — ADR-101 §결정 1 policy 를 mechanism 으로 instantiate 만 한다. "anchor A 의 hash 대상이 무엇인가" (git source vs Confluence rendered) 는 mechanism 결정 (본 ADR §결정 2) 이지만, "3 anchor 가 AND 로 match 해야 무결" / "Orchestrator 2차 verify 무조건" 는 ADR-101 invariant (본 ADR 변경 0건).

### verified-via — 본 ADR 의 모든 사실 인용 검증

본 ADR 의 모든 §결정 / line / §N 인용은 ground truth direct Read / git verify 위에서 작성됐다 (ADR-082 §결정 2 write-time self-write verification 정합). external claim (Atlassian REST / Forge / rate-limit) 은 Researcher WebFetch verified 인용 (재-WebFetch 불요, source 위임).

> verified-via: Read docs/adr/ADR-100 (worktree HEAD `cf349d7`, MERGED) L111-121 §결정 2 — confluence variant / authoritative_source field intent declare-only, 실 yaml 변경 = ADR-103 defer (double-amendment 회피, schema_version 1.0→1.1 MINOR 예고). L150-171 §결정 4 — Layer 1 settings.json `mcp__atlassian` deny baseline + deny precedence (first-match-wins) 로 서버전체 deny + narrow allow 동시 = mechanically broken, "scope 분리 / managed-only 메커니즘 empirical verify = ADR-103 owner". L177-199 §결정 5 — sync agent output sanitization / api_token literal 금지 (env indirect) / outbound-only / write = ADR-103 단일 진입점, W4 위임.
> verified-via: Read docs/adr/ADR-101 (worktree, MERGED) L72-112 §결정 1 — 3-anchor (A content hash 응답 doc body 정규화 hash ↔ git source hash / B version 메타 replay 탐지 / C sync commit SHA 표식 lineage) AND cross-check + dual-layer verify (1차 sync agent / 2차 Orchestrator, single-layer collapse 금지) + mismatch reject + 실 hash 알고리즘 / Confluence property schema = [hypothesis] Atlassian REST page schema 미verify, ADR-103 owner. L114-127 §결정 2 — outbound-only + read/write tool set disjoint narrow-allow (read 가 write 권한 상속 금지). L128-138 §결정 3 — SSRF 3-layer chain (Layer 1 ADR-100 deny / Layer 2 ADR-101 응답 무결성 / Layer 3 ADR-103 base_url 도메인 allowlist). L140-155 §결정 4 — ADR-101 policy / ADR-103 mechanism 분리 ("무엇을 verify" / "어떻게").
> verified-via: Read docs/adr/ADR-099 (worktree, MERGED) L91-110 §결정 1 Layer 1 (mcp__atlassian permission deny SSOT) / Layer 2 (lint grep allowlist) 2-layer + 정식 sync agent narrow allow 대상 위임. L82-89 grep substring false-negative (SecurityArch P0).
> verified-via: Read docs/adr/ADR-102 (worktree, MERGED) L107-141 §결정 3 — sunset_justification 3-tuple (Layer 2 lint allowlist 확장 한정, Layer 1 carrier-preserved 약화 대상 아님). 약화 정당화 경로 cross-ref.
> verified-via: Read docs/inter-plugin-contracts/imperative-walker-protocol-v1.md (worktree) L118-120 §2.A.3 — walk_result enum `open_extension: false` **unconditional** (ADR-068 I-3, "충돌 시 unconditional 우선"). L300-301 §4.2 — MINOR = "신규 codify source ADR 영역 § append (§2.G 등)". L304-309 §4.3 — Amendment trigger 현재 (a) ADR-092~098 Amendment / (b) ADR-076 / (c) CFP-1155 / (d) reconcile v1.13 sunset. trigger (e) ADR-103 = 미존재 (본 ADR §결정 5 declare 의 후속 MINOR bump 대상).
> verified-via: Read docs/doc-locations.yaml (worktree) L6 `schema_version: "1.0"` / L93-104 `adr` entry — variants = `single_repo` 단독 (confluence variant **부재**), `authoritative_source` field **부재**, owner_agent = `codeforge-design:ArchitectAgent`. ADR-100 §결정 2 defer 대상 정합.
> verified-via: Bash `grep CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS .claude/settings.json` (worktree HEAD `cf349d7`) L3 = `"1"` — agent-teams enabled 활성. → §결정 4 SendMessage secret leak surface 실재 (ADR-100 §결정 5 정합).
> verified-via: Read docs/adr/ADR-RESERVATION.md (worktree) L147 — row 103 = CFP-1146, status `reserved`, ADR file = `ADR-103-git-confluence-sync-mechanism.md` (reservation 확정 파일명 정합). row 99~102 = `active` (sister W1 MERGED, §결정 N 인용 가능).
> verified-via: Bash `ls docs/adr/ADR-103*` (worktree) — file 부재 확인 (신규 작성).

### external claim 인용 출처 (Researcher WebFetch verified — 재-WebFetch 불요)

본 ADR 의 Atlassian / Confluence Cloud / OSS sync engine 사실 인용은 Researcher 의 11-source WebFetch verify 결과를 인용한다 (Orchestrator external verify 완료, 본 chief author 재-WebFetch 불요 — ADR-070 verify-before-trust 외부 source output 의 Orchestrator-mediated verify 정합):

- **sync 구현체 후보 평가** (Researcher external): (a) Forge = "no public endpoints, Atlassian invokes internally" = inbound architecture / Connect = 2025-09-17 marketplace 신규 제출 불가 / (b) Exalate = issue/work-item sync 제품 (Jira↔ITSM), git docs tree source 비-1st-class + 유료 / (c) custom GitHub Action = OSS markdown→Confluence engine (`mark` Apache-2.0 v16.4.0 / `markdown-confluence` 기반) thin verify wrapper.
- **Confluence Cloud REST v2 3-anchor feasibility** (Researcher external): content properties API (arbitrary JSON key, 32KB/property, unlimited properties) — anchor C (sync SHA) production precedent `confluence-updater` (SHA label skip-if-unchanged) / native page version field — anchor B / **storage format LOSSY** (round-trip 비-deterministic, ADF-rich silent content loss) → anchor A content hash 대상 = git source (Confluence rendered NOT).
- **Confluence Cloud points-based rate-limit** (Researcher external, 2026-03-02 live, Tier 1 65k pts/hr) — batch + Retry-After backoff.
- **basic-auth = email + API token** (Researcher external) — ADR-100 §결정 3 `api_token_env` + `user_email_env` pair 정합 (token 단독 아님).

[hypothesis] 표기 (Researcher 미verify 영역, 본 ADR 가 단언하지 않음): Korean heading anchor encoding (Confluence heading anchor `pagename-headingname` lowercase ↔ markdown slug deterministic transform — smoke check 의무) / 실 tool name (`mcp__atlassian__*` 개별 tool 명) / confluence path 정확 형식.

### forward cross-ref — Wave 1 sister MERGED + 후속 Phase wire reserved (ADR-082)

본 ADR 은 sister ADR-099 / ADR-100 / ADR-101 / ADR-102 (모두 Wave 1, MERGED, file 존재 verified) 의 §결정 N 을 인용 가능하다. 단 본 ADR 의 실 mechanism wire (settings per-tool deny / sandbox config / sync agent yml / GitHub Action / doc-locations.yaml 실 row / walker §2.G 실 MINOR bump) 는 **본 commit 시점 미작성 (후속 Phase — Epic body S13 + Wave 5 carrier)** 이다. 따라서 본 ADR 의 mechanism 결정은 "설계 결정 + 후속 wire 위임" 으로만 기술하며, 미작성 산출물 (실 yml / 실 yaml row) 을 존재하듯 단언하지 않는다 (ADR-099/100/101/102 declaration-only Wave 1 동일 pattern).

## 결정

### §결정 1 — sync 구현체 = custom GitHub Action (OSS markdown→Confluence engine 기반, one-way git→Confluence push)

**권장 = (c) custom GitHub Action.** git 변경을 Confluence 로 sync 하는 구현체는 OSS markdown→Confluence engine (`mark` Apache-2.0 / `markdown-confluence` 기반) 를 codeforge 가 **thin verify wrapper** 로 own 하는 custom GitHub Action 이다. 호출 방향은 **one-way git → Confluence push** (변경은 git source, Confluence 는 readable mirror 가 authoritative readable 로 격상 — ADR-100 §결정 1 disjoint axis 정합).

#### 구현체 구조

- **engine** = OSS markdown→Confluence converter (`mark` v16.4.0 또는 `markdown-confluence/publish` Action thin variant — Researcher external 권장). codeforge 는 engine 을 재구현하지 않고, conversion + push 를 engine 에 위임하고 그 위에 **3-anchor verify wrapper** (§결정 2) + **token env-indirect 주입** (§결정 4) + **rate-limit backoff** (§결과) 만 own.
- **trigger** = git push (wrapper governance docs 변경) → GitHub Action workflow → engine conversion → Confluence REST push → 3-anchor stamp (§결정 2 write path).
- **one-way invariant** = git → Confluence 단방향. Confluence → git 역방향 push 0건 (역방향 = inbound surface 신설 = 약화, ADR-101 §결정 2 outbound-only invariant 정합).

#### 거부 대안 (ADR-064 §결정 3 룰 2 — 권장 1 + 대안 1, 근거 기록)

- **(a) Forge / Connect = reject (Researcher external verified)**: Forge = "no public endpoints, Atlassian invokes internally" = **inbound architecture** → ADR-101 §결정 2 outbound-only invariant 직접 위반. Connect = 2025-09-17 marketplace 신규 제출 불가 (dead). 단일 org dogfood 에 marketplace app 도입 = over-engineering.
- **(b) Exalate = reject (Researcher external verified)**: issue/work-item sync 제품 (Jira↔ITSM) 으로 git docs tree source 가 비-1st-class — wrong product class + 유료.
- **대안 (채택 가능 fallback) = `markdown-confluence/publish` Action thin variant** — `mark` 외 동일 product class OSS Action. engine 선택은 thin wrapper 구조상 swap 가능 (codeforge 가 own 하는 verify wrapper 는 engine-agnostic).

**채택 근거**: custom GitHub Action (c) 은 (1) outbound-only invariant 정합 (push 방향, inbound endpoint 0) + (2) OSS engine 재사용 (conversion 재구현 회피, codeforge 는 verify wrapper 만 own) + (3) GitHub Action native (git push trigger 자연 정합, dogfood-out 정합) → 권장.

### §결정 2 — 3-anchor 실 구현 = hash-git-source (anchor A ambiguity 해소) + content property (anchor C) + native version (anchor B), ADR-101 §결정 1 mechanism instantiate

ADR-101 §결정 1 의 3-anchor policy 를 다음 mechanism 으로 instantiate 한다. **ADR-101 invariant (3-anchor AND 의미 / dual-layer verify 주체) 재정의 0건** — 본 §결정 2 는 "각 anchor 를 무엇 위에 계산/저장하는가" mechanism 만 결정한다.

#### anchor A ambiguity 해소 — hash 대상 = git source (Confluence rendered NOT)

ADR-101 §결정 1 anchor A 는 "응답 doc body 정규화 hash ↔ git source hash" 로 기술됐으나, **무엇을 정규화하는가** 가 mechanism 영역 미정이었다. 본 §결정 2 가 해소한다:

- **hash 대상 = `sha256(git source markdown)`** — git markdown source 를 정규화 후 sha256. Confluence storage format (rendered XHTML/ADF) 는 **hash 대상 아님**.
- **근거 (Researcher external verified)**: Confluence storage format 은 **LOSSY** (round-trip 비-deterministic — markdown → Confluence storage → markdown round-trip 시 ADF-rich content silent loss). rendered Confluence 를 hash 대상으로 하면 동일 git source 가 매 sync 마다 다른 hash 를 낼 수 있다 (비-deterministic). 따라서 hash 대상은 git source 단방향 고정.
- **Confluence 측 저장** = git-source-hash 사본을 Confluence **content property** 에 저장 (anchor A 비교 시 git source 재hash ↔ Confluence content property 의 git-source-hash 사본 비교, rendered body 비교 아님).
- **"정규화" 정의** = git markdown 정규화 (line-ending 통일 / trailing-whitespace 제거 등 deterministic 변환). **Confluence storage XHTML 정규화 시도 금지** (LOSSY round-trip 회피).

이 해소로 anchor A 가 deterministic 해진다 — git source 가 SoR-work invariant (ADR-100 §결정 1) 이므로 git-source-hash 가 ground truth, Confluence 는 그 사본만 보관.

#### anchor B (version) = Confluence native page version field (Researcher external verified)

Confluence page native version field (optimistic concurrency) 를 anchor B 로 사용 — replay (구 버전 응답 재사용) 탐지. git 기록의 sync version ↔ Confluence page version 비교 (ADR-101 §결정 1 anchor B policy instantiate).

#### anchor C (sync commit SHA) = Confluence content property (Researcher external verified)

- **저장 위치 = content properties API** (Researcher external: arbitrary JSON key, 32KB/property, unlimited properties).
- **production precedent** = `confluence-updater` (SHA label skip-if-unchanged) — sync commit SHA 를 content property 에 저장 후, 다음 sync 시 SHA 변경 없으면 skip (idempotent push).
- anchor C 비교 = Confluence content property 의 SHA 표식 ↔ git log SHA (lineage 무결성, ADR-101 §결정 1 anchor C policy instantiate).

#### 3-anchor verify wire-point = READ path gating (write path 아님, SecurityArch mandate)

SecurityArch verified — 3-anchor verify 의 wire-point 은 **read path (governance-state reflection gating)** 다 (write path 아님):

- **write path** (git → Confluence push 시점) = engine 이 conversion 후 push 하며 3-anchor (A hash / B version / C SHA) 를 Confluence content property 에 **stamp** (기록).
- **read path** (Confluence governance state 반영 시점) = ADR-101 §결정 1 dual-layer verify 적용 — 1차 (sync agent) Confluence content property 의 3-anchor 읽어 git source 와 cross-check + 2차 (Orchestrator) independent git ground truth 재확정 (single-layer collapse 금지). **dual-PASS 시만 governance state reflect**.
- staleness window 동안 stale read = anchor mismatch → git fallback (safe — ADR-101 §결정 1 mismatch git source 우선 정정 instantiate).

**ADR-101 invariant 보존 명시**: dual-layer verify 주체 (1차 sync agent / 2차 Orchestrator) + 3-anchor AND 의미 = ADR-101 §결정 1 policy. 본 §결정 2 는 그 verify 가 read path 에 wire 됨 + 각 anchor 의 실 계산/저장 대상만 결정 (policy 재정의 0건, ADR-101 §결정 4 boundary).

### §결정 3 — narrow allow = Option B (per-tool deny decomposition) + atlassian-tool-drift check + plugin-agent 제약 (sync agent = non-plugin scope) + read/write structural 분리

ADR-100 §결정 4 가 위임한 "scope 분리 / managed-only 메커니즘 empirical verify" 의 답이다. SecurityArch WebFetch-verified 결과 = **Option A mechanically IMPOSSIBLE**, narrow allow = **Option B**.

#### Option A impossible (SecurityArch WebFetch verified — CRITICAL)

ADR-100 §결정 4 가 경고한 "settings 서버전체 deny + agent preset narrow-allow" (Option A) 는 **mechanically 불가능**하다 (SecurityArch WebFetch verified):

- **deny precedence scope-spanning**: "denied at any level, no other level can allow" — 서버전체 deny 가 설정되면 어느 level 에서도 narrow allow 불가.
- **subagent `tools` = RESTRICTIVE** (inherited pool 축소, grant 아님): subagent frontmatter `tools` 는 상속 pool 을 줄이는 필터이지, 새 권한을 grant 하지 못한다.
- **settings deny 위 agent-frontmatter tier 부재**: settings deny 를 override 할 agent-frontmatter level tier 가 존재하지 않는다.

→ ADR-103 가 Option A 를 author 하면 **silently-broken narrow-allow** (ADR-100 §결정 4 경고 실현 — narrow allow tool 이 deny precedence 로 무효, 무음 실패). 채택 reject.

#### Option B = per-tool deny decomposition (narrow allow 정답)

settings deny 를 **서버전체 → 개별 tool 열거** 로 분해한다:

- `deny` = `mcp__atlassian__*` 서버전체 **대신** narrow-allow 대상 tool 을 **제외한 개별 atlassian tool 을 열거** deny.
- `allow` = narrow-allow 대상 tool (정식 sync agent 가 쓰는 read tool) **그것만** allow.
- 결과: deny precedence 는 열거된 개별 tool 만 차단, narrow-allow tool 은 deny 목록에 없으므로 allow 유효 (서버전체 deny 의 scope-spanning 회피).

이것이 ADR-099 §결정 1 Layer 1 ("정식 sync agent 의 preset 만 narrow allow") 의 실 mechanism 이다 — Layer 1 permission deny SSOT 의 narrow allow 대상 = Option B per-tool deny decomposition.

#### atlassian-tool-drift check 의무 (Option B 의 유일 weakening surface mitigate — SecurityArch mandate)

Option B 의 ratchet-weakening surface = **allow-by-omission**: 신규 upstream atlassian tool 이 추가되면, deny 가 개별 열거 방식이므로 신규 tool 이 deny 목록에 없어 **자동 통과** (의도치 않은 권한 개방). 이를 다음으로 mitigate (의무):

- **deny 열거를 verified snapshot 에 고정** — 현 시점 atlassian tool 전체 목록을 verified snapshot 으로 고정.
- **atlassian-tool-drift check** = upstream atlassian MCP server 의 tool 목록 ↔ verified snapshot diff. 신규 tool 등장 (drift) 시 warning — deny 열거 갱신 의무 발화.
- **tier** = warning-tier (ADR-060 evidence-checks-registry framework). **pattern_count >= 2 재발 시 promote** (allow-by-omission 실제 발생 2회 시 blocking 승격).
- 이 check 가 **ADR-100 §결정 4 safe-default 를 재-open 안 하게 하는 필수 mitigation** — Option B 가 서버전체 deny safe-default 를 개별 열거로 완화하지만, drift check 가 누락 tool 을 잡아 safe-default 효력을 유지.

본 atlassian-tool-drift check = 본 ADR `mechanical_enforcement_actions: []` 의 **첫 promotion candidate** (frontmatter 정합).

#### plugin-agent 제약 — sync agent = non-plugin scope 결정 (SecurityArch load-bearing, 미루기 불가)

SecurityArch verified — **plugin-shipped agent 은 `mcpServers` / `permissionMode` / `hooks` frontmatter 불가**. codeforge agent = plugin agent → **sync agent 는 plugin agent 일 수 없다** (mcpServers context-isolation / permissionMode 구조 분리 필요 시). 본 ADR 이 sync agent home/scope 를 결정한다:

| 후보 | sync agent home | 적합성 |
|---|---|---|
| **(권장) project-scope `.claude/agents/`** | consumer/wrapper project repo 의 `.claude/agents/` (plugin-shipped 아님) | plugin-agent frontmatter 제약 회피 — `mcpServers`/`permissionMode` 지정 가능. dogfood-out 정합 (wrapper repo `.claude/agents/` self-app) |
| (대안) managed-settings | enterprise managed permission layer | enterprise 환경 한정 (B-3 allowManagedDomainsOnly 정합). 단일 org dogfood 에 과함 |

**채택 = project-scope `.claude/agents/`** (권장) — plugin-shipped 가 아닌 project-scope agent 로 정의하면 plugin-agent frontmatter 제약 (mcpServers/permissionMode/hooks 불가) 을 회피한다. 실 agent 파일 정의 = 후속 Phase (Wave 5 carrier). 본 ADR 은 sync agent 가 **plugin agent 가 아니라 project-scope agent 임** 을 결정 (미루기 불가 — Option B narrow allow 가 sync agent scope 에 의존).

#### read/write structural 분리 (ADR-101 §결정 2 policy-disallow 보다 강화 — SecurityArch mandate)

sync agent 는 **two agent def 로 structural 분리** (ADR-101 §결정 2 read/write disjoint narrow-allow 의 mechanism instantiate, policy-disallow 보다 강화):

- **read-verify agent** = `disallowedTools: [write]` — Confluence read + 3-anchor verify 전용 (write 권한 구조적 부재).
- **write-commit agent** = `tools: [read, write]` — git → Confluence push 전용 (단일 진입점, ADR-101 §결정 2 write 단일 진입점 instantiate).
- **`disallowedTools` 가 `tools` 보다 먼저 적용** (SecurityArch verified) — read-verify agent 가 write 권한을 상속할 수 없도록 구조적 차단 (ADR-101 §결정 2 "read 가 write 권한 상속 금지" 의 structural enforce, policy-level disallow 보다 강).

**채택 근거 (ADR-064 §결정 3 룰 2)**: Option B + atlassian-tool-drift + structural 분리 (권장) 은 (1) deny precedence 충돌 회피 (Option A impossible 회피) + (2) allow-by-omission weakening surface mitigate (drift check) + (3) read/write structural disjoint (policy 보다 강) → 권장. **대안 = Option A** (서버전체 deny + narrow allow) = mechanically impossible → reject.

### §결정 4 — SSRF Layer 3 dual-channel + token env-indirect + background:true + 3-anchor verify wire-point (read path gating)

ADR-101 §결정 3 SSRF 3-layer chain 의 **Layer 3 (base_url 도메인 allowlist)** owner 다. SecurityArch verified mechanism:

#### SSRF Layer 3 = dual-channel (WebFetch + sandbox 둘 다 — SecurityArch mandate)

- **WebFetch domain rule + sandbox.network.allowedDomains 둘 다** 설정 (single channel 불충분):
  - **WebFetch domain rule** = WebFetch tool 의 허용 도메인 제한.
  - **sandbox.network.allowedDomains** = Bash egress 도메인 제한 — **WebFetch 만 제한하면 Bash egress 가 open** (SSRF 우회). 둘 다 설정해야 base_url 외 호출 차단.
- **base_url = `project.yaml atlassian.confluence.base_url` single source** (ADR-100 §결정 3 schema 정합) — SSRF Layer 3 allowlist 의 single source of truth.
- **enterprise = `allowManagedDomainsOnly`** (B-3) — enterprise 환경은 managed domain 만 허용 (consumer overlay tz override 와 동일 wrapper-canonical 강제 패턴).

#### token env-indirect literal 금지 everywhere + 응답 envelope sanitization

- **token = env-indirect literal 금지 everywhere** (apiKeyHelper precedent, SecurityArch) — api_token / user_email 은 env 경유만 (ADR-100 §결정 3 `*_env` reference 정합). agent transcript / SendMessage / log / lint output 에 literal 등장 0건.
- **Confluence 응답 envelope sanitization** (SendMessage leak, `AGENT_TEAMS=1` verified 활성) — sync agent 가 Confluence REST 응답을 SendMessage payload 에 넣기 전 token literal / 민감 content 제거 (ADR-100 §결정 5 SendMessage leak surface mitigate).
- **sync agent `background: true`** (auto-deny fail-closed, SecurityArch) — sync agent 를 background 로 실행해 prompt-less auto-deny (fail-closed default — 사용자 개입 없는 권한 요청은 거부).

#### 3-anchor verify wire-point = read path gating (write path 아님, §결정 2 cross-ref)

§결정 2 의 read/write wire-point 분리 재명시 (SecurityArch mandate): write 시 3-anchor stamp into Confluence property / read 시 1차 (sync agent) + 2차 (Orchestrator independent git ground truth, single-layer collapse 금지) dual verify → **dual-PASS 시만 governance state reflect**. staleness window = stale read 가 anchor fail → git fallback (safe).

**채택 근거 (ADR-064 §결정 3 룰 2)**: dual-channel SSRF + token env-indirect + background fail-closed (권장) 은 (1) Bash egress 우회 차단 (WebFetch 단독 불충분) + (2) token literal 노출 0건 (env-indirect + envelope sanitization) + (3) auto-deny fail-closed → 권장. **대안 = WebFetch 단독 SSRF** = Bash egress open → reject (SSRF 우회).

### §결정 5 — R5 walker §2.G post-walk hook fold (declare) + R2 doc-locations confluence variant (declare) + gap 3 source-repo-resolver

ArchitectAnalyst prior-art 통합 — 두 영역 (walker / doc-locations) 영향 + cross-repo gap 을 declare 한다. **declaration-only Wave 1** — 실 변경 (walker §2.G 실 MINOR bump / doc-locations.yaml 실 row) 은 후속 Phase.

#### R5 — walker §2.G post-walk hook fold (ArchitectAnalyst verified)

git→Confluence sync 는 walker walk_result enum 으로 **fold 불가** (verified):

- **walk_result enum fold 불가** = imperative-walker-protocol-v1 §2.A.3 `open_extension: false` **unconditional** (verified L118-120, ADR-068 I-3). consumer overlay 가 walk_result enum 값을 임의 확장 못 함 → sync 를 enum 값으로 추가 불가.
- **§2.G 신규 codify source 로 MINOR bump** = §4.2 (verified L301) "MINOR = 신규 codify source ADR 영역 § append (§2.G 등)" 에 정합 — git→Confluence sync 를 walker §2.G 신규 codify source 영역으로 append (MINOR bump).
- **§4.3 trigger (e) ADR-103 추가** = 현 §4.3 Amendment trigger 는 (a)~(d) (verified L304-309, ADR-103 미존재) → 본 ADR 가 trigger (e) ADR-103 추가를 **declare** (실 trigger append = walker MINOR bump carrier).
- **sync = post-walk hook (walk step 아님)**: reconcile→walker 재정의 영역 — git→Confluence sync 는 walk transaction 완료 후 **post-walk hook side-effect** 다 (walk step 자체 아님). walk 가 changelog 처리를 끝낸 후 sync 가 트리거되는 side-effect.
- **declaration-only**: 본 ADR-103 = 실 walker §2.G MINOR bump **declare** 만 (실 bump = 후속 Phase / Wave 5 carrier). ADR-100 §결정 2 doc-locations defer 와 동일 declaration-only 패턴.

#### R2 — doc-locations confluence variant (ArchitectAnalyst verified, ADR-100 §결정 2 위임 받음)

ADR-100 §결정 2 가 confluence variant / authoritative_source field 실 yaml 변경을 ADR-103 에 위임했다 (verified L111-121). 본 ADR 가 그 형식을 **declare** (실 변경 = 후속 Phase):

- **confluence variant 형식** = `https://<instance>.atlassian.net/wiki/spaces/<space>/pages/<page_id>` + content property SHA ([hypothesis] confluence path 정확 형식 — Researcher 미verify 영역, 본 ADR 단언 안 함, 후속 Phase smoke check).
- **`authoritative_source` field** = doc-locations.yaml `adr` 등 entry 에 git path 외 Confluence authoritative readable 위치 표기 field 신설 (현 schema_version 1.0, verified L6 — confluence variant / authoritative_source field 부재).
- **schema_version 1.0 → 1.1 MINOR** = field 추가 = backward-compatible (ADR-041 §결정 5 field 추가 = MINOR 정합, ADR-100 §결정 2 예고 정합).
- **declaration-only**: 본 ADR = confluence variant / authoritative_source field 형식 + schema 1.0→1.1 MINOR **declare** 만 (실 yaml row 변경 = 후속 Phase / Wave 5 carrier — declaration-only Wave 1 정합).

#### gap 3 — source-repo-resolver (ArchitectAnalyst verified, dogfood-out cross-repo)

sync source 가 **2-repo** 다 (ADR-013 dogfood-out 정합):

- **wrapper governance docs** (KEEP) = wrapper repo (`docs/adr/` + `docs/inter-plugin-contracts/` + `docs/domain-knowledge/` + playbook) — ADR-100 §결정 1 1차 대상.
- **dogfood-out docs** (MOVE) = internal-docs repo (`retros/` + `change-plans/` + `stories/`) — sync source = mclayer/codeforge-internal-docs (wrapper 아님, ADR-100 §결정 1 표 정합).
- **source-repo-resolver** = doc-locations.yaml `dogfood_scope` + variants 로 sync source repo derive (core sub-problem) — 어느 doc 이 어느 repo source 인지 resolve. internal-docs repo 접근 = CODEFORGE_CROSS_REPO_PAT scope (ADR-066 cross-ref).
- **declaration-only**: source-repo-resolver 실 구현 = 후속 Phase. 본 ADR 은 2-repo source 분리 + resolver 필요성 declare.

#### invariant 금지 (ArchitectAnalyst)

본 §결정 5 는 다음 invariant 를 위반하지 않는다: git = SoR-work (역방향 금지, one-way git→Confluence) / ADR-101 3-anchor + dual-layer (재정의 0건) / walker `open_extension: false` (walk_result fold 불가, §2.G append) / ADR-101 §결정 4 policy(101)/mechanism(103) boundary (본 ADR = mechanism only).

## 결과

### 긍정

- sync mechanism 결정 SSOT 확립 — Epic-A Wave 1 4 ADR 이 위임한 4 mechanism 질문 (sync 구현체 / narrow allow / 3-anchor 실 구현 / doc-locations·walker) 을 본 ADR 이 닫음 (Wave 4 = Epic-A mechanism 완결).
- ADR-101 policy 의미 약화 0건 — mechanism instantiate only (3-anchor AND 의미 / dual-layer verify 주체 재정의 0건). ADR-101 §결정 4 boundary invariant 보존.
- anchor A ambiguity 해소 — hash 대상 = git source (Confluence rendered NOT) 로 deterministic. Confluence storage LOSSY round-trip 회피 (silent content loss 차단).
- Option A impossible 명시 + Option B 채택 — ADR-100 §결정 4 "scope 분리 메커니즘 empirical verify = ADR-103 owner" 위임 응답. silently-broken narrow-allow (deny precedence) 회피.
- security 강화 방향 — Option B per-tool deny + read/write structural 분리 (policy 보다 강) + SSRF Layer 3 dual-channel + token env-indirect + background fail-closed = 최소권한 + SSRF 차단 강화 (약화 아님).
- plugin-agent 제약 해소 — sync agent = non-plugin (project-scope) scope 결정으로 mcpServers/permissionMode 지정 가능 (plugin-shipped frontmatter 제약 회피).
- walker / doc-locations 영향 declare — walk_result fold 불가 (§2.A.3 unconditional) → §2.G post-walk hook MINOR bump declare + doc-locations confluence variant / schema 1.0→1.1 declare (실 변경 후속 Phase, double-amendment 회피).

### 부정 / trade-off

- **Confluence Cloud points-based rate-limit (Researcher external verified, 2026-03-02 live, Tier 1 65k pts/hr)** — sync 빈도/batch 크기에 따라 rate-limit 도달. 완화 = batch + Retry-After backoff (§결정 1 thin wrapper own). rate-limit 도달 시 staleness window 증가 trade-off (git source 는 무손상, Confluence readable 만 지연 reflect).
- **Option B allow-by-omission ratchet risk (SecurityArch, 유일 weakening surface)** — 신규 upstream atlassian tool 이 deny 열거 누락 시 자동 통과. 완화 = atlassian-tool-drift check 의무 (verified snapshot 고정 + drift warning, §결정 3). pattern_count >= 2 재발 시 promote (첫 promotion candidate). 본 mitigation 부재 시 safe-default 재-open risk.
- **Confluence storage format LOSSY (Researcher external verified)** — rendered Confluence round-trip 비-deterministic (ADF-rich silent content loss). 완화 = anchor A hash 대상 = git source (Confluence rendered NOT, §결정 2). SoR git 무손상 — Confluence readable mirror degrade 만 (git-source-authoritative 안전).
- **cross-repo source-repo-resolver 복잡도 (gap 3)** — sync source 2-repo (wrapper governance docs + internal-docs dogfood-out docs). 완화 = doc-locations dogfood_scope + variants derive + CODEFORGE_CROSS_REPO_PAT scope (ADR-066). 실 resolver = 후속 Phase.
- **[hypothesis] 미verify 영역** — Korean heading anchor encoding (deterministic transform smoke check 의무) / 실 tool name / confluence path 정확 형식 = Researcher 미verify. 완화 = [hypothesis] 명시 (본 ADR 단언 안 함) + 후속 Phase smoke check 의무 (Korean heading anchor encoding).
- **forward wire reserved (declaration-only Wave 1)** — 실 mechanism wire (settings per-tool deny / sandbox config / sync agent yml / GitHub Action / doc-locations.yaml 실 row / walker §2.G 실 MINOR bump) = 후속 Phase (Epic body S13 + Wave 5 carrier). 완화 = §컨텍스트 forward cross-ref reserved 명시 (미작성 산출물 단언 금지, ADR-082) + ADR-100/101/102 declaration-only Wave 1 동일 pattern.
- **mechanical_enforcement_actions `[]` Wave 1 declaration-only** — sync mechanism 실 wire = 후속 Phase. atlassian-tool-drift check = 첫 promotion candidate (Option B allow-by-omission 유일 weakening surface), pattern_count >= 2 재발 시 follow-up CFP MUST promote to warning-tier (ADR-082 §결정 6 / ADR-070 §D5 retain pattern). 본 ADR category = tooling-infrastructure (normative) 이나 declaration-only Wave 1 이므로 `[]` + 첫 promotion candidate 명시 (ADR-040 Amendment 3 normative-boundary mandate 정합 — 후속 wire carrier 가 mechanical action binding).

## 해소 기준

N/A — permanent policy (`is_transitional: false`). git→Confluence one-way sync mechanism (custom GitHub Action + 3-anchor hash-git-source + Option B narrow allow + SSRF dual-channel) 은 Atlassian 재결합 후 영구 sync 정책 방향. sync 구현체 + narrow allow scope 분리 + SSRF Layer 3 + 3-anchor verify wire-point = 강화 방향 (security boundary 신설 + 최소권한) → 약화 정당화 불요.

**유일 weakening surface = Option B allow-by-omission (atlassian-tool-drift check 로 mitigate)**: §결정 3 Option B per-tool deny decomposition 은 서버전체 deny safe-default 를 개별 열거로 완화한다 — 신규 upstream atlassian tool 이 deny 열거 누락 시 자동 통과 = allow-by-omission. 이 유일 약화 surface 는 **atlassian-tool-drift check** (verified snapshot 고정 + drift warning, 첫 promotion candidate) 로 mitigate 한다 — 약화 차단 mechanism 동반이므로 본 ADR 자체는 강화 방향. allowlist 확장 약화 정당화 경로 (Layer 2 lint) 는 ADR-102 §결정 3 3-tuple cross-ref (Layer 2 한정 — 본 ADR 의 Layer 1 narrow allow scope 분리는 ADR-102 약화 정당화 영역과 disjoint, 순수 mechanism 강화).

**ADR-101 policy 의미 약화 0건 (ADR-101 §결정 4 boundary invariant)**: 본 ADR = mechanism only. 3-anchor AND 의미 / dual-layer verify 주체 (1차 sync agent / 2차 Orchestrator) 재정의 0건 — ADR-101 §결정 1 policy 를 mechanism 으로 instantiate 만 한다. "무엇을 verify" 는 ADR-101 invariant (본 ADR 변경 불가).

amendment 시 sunset_justification 의무 (ADR-058 §결정 5) — ratchet 강화 방향만 허용 (예: 4번째 anchor 도입 / atlassian-tool-drift check warning → blocking 승격 / SSRF Layer 추가 / read/write structural 분리 강화). 약화 방향 (예: one-way → bidirectional sync 역전 / 3-anchor → single-anchor 축소 / Option B narrow allow → 서버전체 allow / token env-indirect → 평문 mount / dual-channel SSRF → WebFetch 단독 축소) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 인접 (§결정 3 narrow allow + §결정 4 SSRF / token secret = security guard). 단 category = tooling-infrastructure (git→Confluence sync mechanism 본체 — sync 구현체 / hash 알고리즘 / doc-locations·walker wiring) — security 차단 패턴은 §결정 3 (Option B + structural 분리) + §결정 4 (SSRF dual-channel + token env-indirect) 로 보존 (ADR-101 = category security, 본 ADR = mechanism 본체 tooling-infrastructure 분류 — ADR-058 §결정 7 보안 presumption false 강화는 §결정 3/4 boundary 로 충족).

## 관련 파일

- `docs/adr/ADR-099-atlassian-allow-redefinition.md` — §결정 1 Layer 1 (정식 sync agent narrow allow 대상 위임). 본 ADR §결정 3 = Option B 실 mechanism (W1 S1 MERGED)
- `docs/adr/ADR-100-confluence-doc-ssot-recognition.md` — §결정 2 (doc-locations confluence variant defer) + §결정 4 (scope 분리 메커니즘 empirical verify = ADR-103 owner) + §결정 5 (sync agent sanitization / token env-indirect W4 위임). 본 ADR = 위임 owner (W1 S2 MERGED)
- `docs/adr/ADR-101-verify-before-trust-confluence-rest.md` — §결정 1 3-anchor policy + dual-layer verify (본 ADR §결정 2 mechanism instantiate, 재정의 0건) + §결정 3 SSRF Layer 3 (본 ADR §결정 4 owner) + §결정 4 policy/mechanism boundary invariant (W1 S3 MERGED)
- `docs/adr/ADR-102-ratchet-weakening-governance-anchor.md` — Option B allow-by-omission 약화 정당화 경로 cross-ref (Layer 2 lint 한정, 본 ADR Layer 1 narrow allow scope 분리는 disjoint) (W1 S4 MERGED)
- `docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md` — §결정 5 source-repo-resolver 2-repo source (wrapper KEEP / internal-docs MOVE)
- `docs/adr/ADR-041-doc-location-registry.md` — §결정 5 confluence variant / authoritative_source field + schema_version 1.0→1.1 MINOR (declare-only, 실 변경 후속 Phase)
- `docs/inter-plugin-contracts/imperative-walker-protocol-v1.md` — §결정 5 R5 walker §2.G post-walk hook MINOR bump declare (§2.A.3 walk_result fold 불가 unconditional / §4.2 MINOR = 신규 codify source § append / §4.3 trigger (e) ADR-103 추가 declare)
- `docs/adr/ADR-066-pat-rotation-policy.md` — §결정 5 source-repo-resolver internal-docs repo CODEFORGE_CROSS_REPO_PAT scope cross-ref
- `.claude/settings.json` — §결정 3 Option B per-tool deny decomposition + §결정 4 SSRF Layer 3 sandbox.network.allowedDomains (실 wire = 후속 Phase)
- `docs/project-config-schema.md` — §결정 4 base_url single source (`atlassian.confluence.base_url`, ADR-100 §결정 3 schema)
- `docs/adr/ADR-RESERVATION.md` — row 103 reserved → active 전환 + amendments_reserved row (adr_number: 103, amendment_id: 1, CFP-1492)

## Amendment 1 (2026-05-24 KST) — MCP-direct routing rule (deviation declare, mark engine path retain for future)

### 동인

CFP-1146 W5-S17 #1310 (182 page Confluence cutover, MERGED 2026-05-23 KST) 가 ATLASSIAN_API_TOKEN GitHub secret 미주입 + ADR-103 §결정 1 custom GitHub Action mark engine path (#1320) deferred 상태에서 **MCP-direct ad-hoc invocation** (Orchestrator main session OAuth + Atlassian MCP `mcp__plugin_atlassian_atlassian__createConfluencePage` + `updateConfluencePage` 직접 호출) 으로 cutover 를 완수했다 (first MCP-direct precedent). Sub-B S2.1 #1498 (49 page IA tree bootstrap + `docs/confluence-ia-tree.yaml` schema SSOT, MERGED 2026-05-24 KST) 가 동일 deviation path 를 답습하며 second application 으로 안착했다.

사용자 directive 2026-05-24 KST `"atlassian mcp로 하면되잖아"` 가 본 deviation path 의 정식 codify 를 발화 — 2 prior MCP-direct application 을 retroactive 정식 declare 하고 mark engine path 를 **retain for future PRIMARY** 로 보존한다 (precedent first, codify second).

본 Amendment 는 ADR-103 §결정 1 의 sync 구현체 결정 (custom GitHub Action mark engine path) 를 **약화시키지 않는다** — alternative routing rule 추가만, primary path 보존 (carrier-preserved per ADR-097 §결정 3 정합 ratchet 강화 방향).

### verified-via (Amendment 1 사실 인용 검증, ADR-082 §결정 2 write-time self-write verification 정합)

> verified-via: `gh issue view 1310 --repo mclayer/plugin-codeforge --json title,state,closedAt` (2026-05-24 KST) → title = `[CFP-1146 W5-S17] A.4 cutover — MCP-direct full sync (182 page, deviation declare)`, state = `CLOSED`, closedAt = `2026-05-23T10:24:53Z` (first MCP-direct precedent verified).
> verified-via: `gh pr view 1498 --repo mclayer/plugin-codeforge --json title,state,mergedAt,headRefName` (2026-05-24 KST) → title = `[CFP-1491] Confluence space CFP IA tree bootstrap — 49 page (MCP-direct) + docs/confluence-ia-tree.yaml (Sub-B S2.1 of EPIC #1415)`, state = `MERGED`, mergedAt = `2026-05-24T06:31:42Z`, headRefName = `cfp-1491-confluence-space-tree-bootstrap` (second MCP-direct application verified).
> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md (worktree HEAD `14999bd`, base commit) frontmatter L26 `amendment_log: []` → length 0, Amendment 1 = first amendment (verified amendment_id slot).
> verified-via: Read docs/adr/ADR-RESERVATION.md (worktree) L268-272 last amendments_reserved row = adr_number 44 / amendment_id 3 / CFP-1438. ADR-082 Amendment 17 §결정 1 sub-scope (1-G) strict claim mandate 충족 — 본 Amendment 1 commit 전 ADR-RESERVATION amendments_reserved[] row (adr_number 103 / amendment_id 1 / CFP-1492) pre-append + verified-via annotation `pre_reservation_verified: true`.
> verified-via: Issue #1492 body `gh issue view 1492 --repo mclayer/plugin-codeforge --json body` (2026-05-24 KST) AC-1/AC-2/AC-3 blocking + AC-4/AC-5 advisory. **Filename drift detected**: Issue body references `ADR-103-confluence-mirror-sync-engine.md`, ground truth file = `ADR-103-git-confluence-sync-mechanism.md` (per ADR-RESERVATION row 103 L147 + worktree ls). Amendment 1 = actual file ground truth verbatim (verify-before-trust ADR-073 §결정 1 정합).

### 결정 — MCP-direct path codify as alternative routing rule

#### 결정 1-A — Routing rule decision tree (PRIMARY vs ALTERNATIVE)

ADR-103 §결정 1 custom GitHub Action mark engine path (#1320 deferred) 와 본 Amendment 의 MCP-direct path 를 다음 routing rule 로 분리한다:

| Routing | Path | 활성 조건 | Scope |
|---|---|---|---|
| **PRIMARY** (retain for future) | mark engine path — custom GitHub Action + OSS markdown→Confluence engine (`mark` v16.4.0 / `markdown-confluence/publish`) + 3-anchor stamp content property + SSRF Layer 3 dual-channel + token env-indirect (ADR-103 §결정 1-4) | `ATLASSIAN_API_TOKEN` GitHub secret 주입 활성 + Issue #1320 (Epic-A F3 sync engine carrier) merged + ongoing sync 영역 (git push 자동 trigger) | wrapper governance docs 영속 sync, dogfood-out docs 영속 sync, full 3-anchor verify wire-point (write/read path) |
| **ALTERNATIVE** (deviation channel) | MCP-direct path — Atlassian MCP `mcp__plugin_atlassian_atlassian__createConfluencePage` + `updateConfluencePage` + `getConfluencePage` 직접 호출 (Orchestrator main session OAuth scope, mark engine 미경유) | `ATLASSIAN_API_TOKEN` secret 미활성 + Issue #1320 deferred 상태 + ad-hoc cutover / legacy backfill / IA tree bootstrap / drift detection 영역만 | one-shot batch sync (legacy backfill / IA tree bootstrap / 사후 정정), 일상 sync 비대상 (mark engine 활성 후 defer) |

**우선순위 invariant**: `PRIMARY > ALTERNATIVE` — mark engine path 활성 상태에서는 MCP-direct path 사용 금지 (정상 영속 sync = PRIMARY 단독). ALTERNATIVE 는 mark engine 비활성 영역만 cover (`null|deferred` channel).

#### 결정 1-B — Deviation declare schema 4-tuple

MCP-direct path 사용 시 다음 4 항목 의무 declare (Story / Change Plan / PR description 어느 한 곳 이상):

1. **deviation trigger** — 사용 사유 명시 (예: `mark engine #1320 deferred + secret 미주입` / `ad-hoc cutover, one-shot batch` / `legacy backfill, ATLASSIAN_API_TOKEN 부재`). 사용자 directive verbatim citation 권장 (CFP-1492 = `"atlassian mcp로 하면되잖아"` precedent 답습).
2. **deviation mechanism** — 사용 MCP tool 명세 (예: `mcp__plugin_atlassian_atlassian__createConfluencePage` + `updateConfluencePage` + `getConfluencePage` 3 tool, 31 tool family 중 사용 subset). mark engine path 미경유 사실 명시.
3. **deviation scope** — 영향 page count + 영역 enumeration (예: `49 page + IA tree bootstrap` / `182 page + legacy cutover`). 일상 sync 비포함 명시 (mark engine 활성 후 defer 영역).
4. **3-anchor stamp accept-as-zero** — content property `version_id` / `git_sha` / `last_synced_at` 3-anchor (§결정 2) **부착 불가** (MCP-direct = content property tool 부재) → **0건 acceptance**. mark engine 활성 후 backfill 가능 영역으로 declare (deferred verify wire-point).

본 4-tuple 부재 시 PR open 차단 (DesignReviewPL check item AC-4, advisory tier — 실 mechanical lint 는 deferred follow-up).

#### 결정 1-C — subagent OAuth limitation 명시

Atlassian MCP 의 OAuth scope 는 **Orchestrator main session 한정**이다 (subagent spawn 영역 = unauthenticated). 본 deviation channel 사용 시:

- **Orchestrator inline path 의무** — MCP-direct invocation 은 Orchestrator main session 안에서 inline 실행 (ADR-039 inline whitelist 영역 확장 = false, subagent OAuth unauthenticated 우회 mechanism 아님). subagent spawn 으로 MCP-direct 호출 위임 시 401 unauthenticated 차단.
- **ArchitectPL design lane 영역** — Phase 1 산출물 작성 시 subagent spawn 이 표준 (ADR-082 §결정 1 sub-scope 1-C 정합). MCP-direct deviation 영역 = doc-only 1-file edit scope 안에서 Orchestrator inline path 우회 acceptable (low complexity + ADR-039 inline whitelist 1번 entry 사용자 dialog payload 정합, deviation 자체가 사용자 directive verbatim citation 영역).
- **future mark engine path (#1320)** = sync agent project-scope `.claude/agents/` (plugin-shipped 아님) 안에서 `mcpServers` 지정 가능 (ADR-103 §결정 3 plugin-agent 제약 해소 정합) — mark engine 활성 후 subagent OAuth 영역 회피 + 정식 OAuth scope 보유.

#### 결정 1-D — LOSSY risk acknowledgment + drift detection 의무

MCP-direct path 의 trade-off (carrier-preserved invariant 보존 영역 외, 약화 surface):

- **LOSSY risk** — Atlassian MCP `createConfluencePage` / `updateConfluencePage` 의 markdown → Confluence storage format 변환은 OSS mark engine 보다 **추가 escape 처리 누락 가능** (CFP-1146 W5-S17 evidence: 특정 markdown escape pattern silent loss 사례). hash 대상 anchor A (git source) 는 deterministic 유지 (ADR-103 §결정 2 정합), readable Confluence body 만 degrade 가능. **mark engine 활성 후 OSS engine 으로 backfill 권장**.
- **3-anchor stamp 부재** = read path 3-anchor verify (§결정 2 dual-layer verify) **wire 불가** — sync agent 1차 verify + Orchestrator 2차 verify 모두 mark engine 활성 전까지 manual / cron lint 영역으로 대체. drift detection cron workflow (Sub-B S2.5 carrier) 가 compensate 의무 (page age + content hash sample check).
- **약화 surface mitigate** = drift detection cron (S2.5) + mark engine 활성 후 atomic backfill (legacy MCP-direct page 의 3-anchor stamp 일괄 부착) + ADR-082 §결정 6 retain pattern (pattern_count ≥ 2 재발 시 mechanical lint promote 의무).

### 결정 1-E — mark engine path retain for future PRIMARY (Issue #1320)

본 Amendment 는 ADR-103 §결정 1 custom GitHub Action mark engine path 결정을 **약화시키지 않는다** (carrier-preserved per ADR-097 §결정 3 정합):

- **Issue #1320** (Epic-A F3 sync engine carrier) = deferred 상태 보존, 본 Amendment 으로 cancel / supersede 0건.
- **`ATLASSIAN_API_TOKEN` GitHub secret 주입 후 mark engine path 활성 가능** — 활성 시점에 PRIMARY routing rule 발효 (decision tree 1-A 표 정합), MCP-direct path = 자동 deferred (영속 sync 영역 비대상).
- **paradigm replacement 아님** (ADR-097 closed-set 3 조건 AND 미충족):
  - (a) 9+ ADR/contract 동시 sunset = **미충족** (sunset 0건, alternative path 추가만)
  - (b) 단일 atomic Epic carrier = **미충족** (CFP-1492 = single Story carrier, Epic carrier 아님)
  - (c) ratchet 강화 carve-out = **충족** (alternative path 추가 = 강화 방향)
  → 3 조건 AND 미충족 (1/3) → paradigm replacement carve-out 미적용, **surgical deviation only**.
- **본 Amendment 는 ratchet 강화 방향 (alternative path 추가, carrier-preserved sunset 0건)** — ADR-058 §결정 5 sunset_justification 의무 N/A (약화 방향 아님).

### 결과 (Amendment 1 영역만)

#### 긍정

- MCP-direct deviation channel 정식 codify — 2 prior application (CFP-1146 W5-S17 #1310 + Sub-B S2.1 #1498) 의 retroactive formalize. 향후 동일 deviation 영역 (drift detection ad-hoc invocation / legacy backfill / Sub-B S2.3-S2.5 carrier) 에서 deviation declare 4-tuple 답습 가능.
- mark engine path PRIMARY 보존 — Issue #1320 deferred 상태 그대로, paradigm replacement 미적용 (carrier-preserved). 약화 surface 0건.
- routing rule decision tree 명문화 — PRIMARY vs ALTERNATIVE 활성 조건 / scope disjoint codify, 영속 sync 영역 vs ad-hoc batch 영역 boundary 명확.
- subagent OAuth limitation 명시 — Orchestrator inline path 의무 영역 codify, subagent MCP-direct invocation 시 401 차단 root cause 사전 안내.
- sub-Epic #1490 5/5 child Story 완료 condition 충족 trigger 가능 (Sub-B S2.2 = 5/5).

#### 부정 / trade-off

- **3-anchor stamp accept-as-zero (MCP-direct 영역만)** — content property tool 부재로 dual-layer verify wire 불가. 완화 = mark engine 활성 후 backfill + drift detection cron (S2.5 carrier).
- **LOSSY risk (markdown escape silent loss)** — MCP 변환 vs mark engine 변환 차이로 특정 escape pattern 누락 가능. 완화 = git source = SoR-work 무손상 (anchor A deterministic 유지, ADR-103 §결정 2 정합) + mark engine 활성 후 OSS engine 으로 backfill.
- **deviation channel 남용 risk** — 본 Amendment 가 mark engine path 활성 전 모든 sync 를 MCP-direct 로 우회하는 anti-pattern 유발 가능. 완화 = routing rule decision tree (1-A) ALTERNATIVE scope 영역 제한 (one-shot batch + ad-hoc + legacy backfill 만) + 일상 sync 비대상 invariant 명시 + DesignReviewPL check item AC-4 advisory.
- **mechanical lint deferred** — deviation declare 4-tuple presence lint = follow-up CFP carrier (본 Amendment = declarative). pattern_count ≥ 2 재발 시 promote 의무 (ADR-082 §결정 6 retain pattern). 현재 pattern_count = 3 (CFP-1146 W5-S17 + Sub-B S2.1 + 본 Amendment) → **promote candidate** (follow-up CFP carrier).

### invariant 금지 (Amendment 1)

본 Amendment 는 다음 invariant 를 위반하지 않는다:

- **one-way git → Confluence push invariant** (ADR-103 §결정 1) — MCP-direct path 도 `createConfluencePage` / `updateConfluencePage` 만 사용 (write 방향), Confluence → git 역방향 push 0건. outbound-only invariant 보존 (ADR-101 §결정 2 정합).
- **ADR-101 policy 의미 약화 0건** (ADR-101 §결정 4 boundary invariant) — 3-anchor AND 의미 / dual-layer verify 주체 재정의 0건. 단지 mark engine 비활성 영역만 3-anchor stamp accept-as-zero 영역으로 declare (deferred wire-point, policy 약화 아님).
- **carrier-preserved sunset 0건** (ADR-097 §결정 3) — mark engine path 약화/sunset 0건, alternative path 추가만.
- **subagent OAuth scope invariant 보존** — MCP-direct 가 subagent unauthenticated 영역 우회 mechanism 아님 명시 (Orchestrator inline path 의무).
- **paradigm replacement carve-out 미적용** (ADR-097 §결정 1 closed-set 3 조건 AND 미충족) — surgical deviation only.

## Amendment 2 (2026-06-01 KST) — sync agent write-time permission 한계 명문화 + read-path dual-layer verify load-bearing 보상통제 지정

### 동인

CFP-1146 W5-S15 chief synthesis P1-1 (보안 gap) 가 sync write-commit agent (`.claude/agents/confluence-sync-write-commit.md`) 의 write 차단 enforce 구조 결함을 식별했다. agent 의 Confluence write 차단은 `disallowedTools` + `tools` allowlist + `settings.json` deny 3중에 의존하는데, agent frontmatter 의 `permissionMode: default` 가 parent `defaultMode: bypassPermissions` 에 의해 override 되어 무효화된다. agent file 자체가 이미 이 한계를 declare 한다 (verified-via 아래 인용) — write-time 권한 prompt 가 parent bypassPermissions 하에서 무효이므로, sync agent 의 unchecked Confluence write 위협이 미완화 상태로 남는다.

본 Amendment 는 (1) 이 write-time permission enforce 한계를 정직하게 명문화하고 (2) 이미 존재하는 read-path dual-layer verify (§결정 2 / ADR-101 §결정 1) 를 P1-1 맥락에서 **interim load-bearing 보상통제**로 명시 강조하며 (3) write-time prevention 예방 수정 후보를 Wave 2 mechanical carrier 로 declare 한다. **ADR-101 policy 의미 약화 0건** — 이미 존재하는 dual-layer verify 를 P1-1 맥락 load-bearing 으로 명시만 할 뿐, "무엇을 verify" (ADR-101 §결정 4 boundary invariant) 재정의 0건.

### verified-via (Amendment 2 사실 인용 검증, ADR-082 §결정 2 write-time self-write verification 정합)

> verified-via: Read `.claude/agents/confluence-sync-write-commit.md` (worktree HEAD `4b130353`) L9 `permissionMode: default` + L33-38 "ADR-103 인용 정정" 블록 — "`permissionMode: default` 는 parent `bypassPermissions` 하에서 무효 — write 차단 실 enforce = `disallowedTools` 로 구현". L40-54 §7.6 미완화 위협 declare — "`defaultMode: bypassPermissions` 하에서 write-commit agent 의 Confluence write 는 unchecked 상태 ... write 시점 권한 prompt 는 무효" + 사후 guard 3중 (`tools` allowlist 4-tool / `settings.json` deny 24-tool W5-S14 ADR-103 §결정 3 / read path 3-anchor dual-layer verify) + "본 위협 미완화 declare — 완화 강화는 별 follow-up CFP".
> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md (worktree HEAD `4b130353`, 본 file base) §결정 2 L134-142 — 3-anchor verify wire-point = READ path gating (write path 아님). read path = ADR-101 §결정 1 dual-layer verify (1차 sync agent / 2차 Orchestrator independent git ground truth, single-layer collapse 금지) → **dual-PASS 시만 governance state reflect**. staleness window stale read = anchor mismatch → git fallback.
> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md §결정 3 L168-177 (atlassian-tool-drift) + L179-188 (plugin-agent 제약, sync agent = project-scope `.claude/agents/`) + L190-196 (read/write structural 분리). 본문 내 실 settings per-tool deny wire = 후속 Phase 명시 (L42 declaration-only Wave 1 invariant + L23 frontmatter `mechanical_enforcement_actions: []` + L304 `.claude/settings.json` Option B per-tool deny "실 wire = 후속 Phase").
> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md §컨텍스트 L56-58 (ADR-101 §결정 4 policy/mechanism boundary invariant load-bearing) + §결정 2 L142 ("dual-layer verify 주체 + 3-anchor AND 의미 = ADR-101 §결정 1 policy. 본 §결정 2 는 그 verify 가 read path 에 wire 됨 + 각 anchor 의 실 계산/저장 대상만 결정, policy 재정의 0건").
> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md frontmatter L26-33 amendment_log[] = amendment 1 단일 entry (direction strengthening, CFP-1492) → 본 Amendment 2 = second amendment (amendment_id slot 2 verified).

### 결정 — write-time permission 한계 명문화 + read-path 보상통제 load-bearing 지정

#### §결정 6 — sync agent write-time permission 한계 + read-path dual-layer verify load-bearing 보상통제 지정 (Amendment 2, CFP-1321)

본 §결정 6 은 W5-S15 P1-1 보안 gap 을 3-point 로 닫는다. write-time prevention 미보장 정직 declare + read-path verify 를 interim load-bearing 보상통제로 명시 + 예방 수정 Wave 2 carrier declare.

##### 6-A — write-time permission enforce 한계 명문화 (정직 declare)

sync write-commit agent 의 Confluence write 차단 enforce 는 다음 구조적 한계를 가진다 (agent file §7.6 미완화 위협 declare 정합, verified-via 인용):

- **`permissionMode: default` 무효화**: agent frontmatter 의 `permissionMode: default` 는 parent `defaultMode: bypassPermissions` 에 의해 override 된다 — write 시점 권한 prompt 가 무효. parent bypassPermissions 가 subagent permissionMode 를 이긴다 (platform inherent).
- **write 차단 실 enforce = 3중 의존**: 그러므로 write-time write 차단의 실 enforce 는 (1) `disallowedTools` + (2) `tools` allowlist 4-tool 한정 + (3) `settings.json` deny 에 의존한다.
- **그 settings deny wire 자체가 deferred**: 그런데 (3) settings deny 의 실 wire (Option B per-tool deny decomposition) 는 §결정 3 에서 후속 Phase (Epic body S13 + Wave 5 carrier) 로 deferred 다 (verified-via — L42 declaration-only Wave 1 + L304 "실 wire = 후속 Phase"). → **write-time prevention 은 현재 구조적으로 미보장** (정직 declare).
- **정직 declare invariant**: 본 한계는 agent file §7.6 가 이미 declare 한 미완화 위협을 ADR-103 mechanism SSOT 로 끌어올려 명문화한 것이다 — 미wire 상태의 정직 문서화이지 보호 강도 축소가 아니다 (ADR-058 §결정 5 약화 surface 0건).

##### 6-B — read-path dual-layer verify = interim load-bearing 보상통제 (in-scope 강화)

write-time prevention 이 미보장이어도, 변조/무단 write 가 governance state 를 오염시키기 전에 차단하는 보상통제가 이미 존재한다 — §결정 2 의 read-path dual-layer verify (ADR-101 §결정 1 wire) 다. 본 Amendment 가 이를 P1-1 맥락에서 **interim load-bearing 보상통제**로 명시 강조한다:

- **read-path 보상통제 mechanism (§결정 2 / ADR-101 §결정 1, 재정의 0건)**: governance state 반영 시점에 (1차 sync agent) Confluence content property 의 3-anchor (A git-source-hash / B native version / C sync commit SHA) 를 git source 와 cross-check (AND) + (2차 Orchestrator) independent git ground truth 재확정 (single-layer collapse 금지) → **dual-PASS 시만 governance state reflect**.
- **load-bearing 의미**: write-time prevention 이 미보장인 interim 구간 동안, 무단/변조 write 는 Confluence 에 land 할 수 있으나 read path 의 3-anchor AND mismatch + Orchestrator 2차 independent verify (dual-PASS gate) 에서 catch 된다 — **governance state poisoning 전 차단** (mismatch → git source 우선 정정, ADR-101 §결정 1 instantiate). git = SoR-work invariant 이므로 git source 가 ground truth, 오염된 Confluence read 는 anchor fail 로 reject.
- **ADR-101 policy 재정의 0건 (boundary invariant 보존)**: 본 6-B 는 이미 존재하는 dual-layer verify 를 P1-1 맥락 load-bearing 으로 **명시 강조만** 한다. 3-anchor AND 의미 / dual-layer verify 주체 (1차 sync agent / 2차 Orchestrator) = ADR-101 §결정 1 policy (본 Amendment 변경 불가). "무엇을 verify" 재정의 0건 (ADR-101 §결정 4 policy/mechanism boundary invariant load-bearing 보존, verified-via L56-58 / L142).
- **interim 한정**: 본 보상통제는 write-time prevention 이 미wire 인 interim 구간의 load-bearing guard 다. write-time prevention (6-C) wire 후에도 read-path verify 는 보존 (defense-in-depth) — 단 "유일 load-bearing" 지위는 interim 한정.

##### 6-C — write-time prevention 예방 수정 후보 = Wave 2 mechanical carrier declare

write-time prevention 강화는 settings.json / orchestration wire 영역으로 declaration-only Wave 1 범위 밖이다. 예방 후보 2종을 Wave 2 mechanical carrier (별 sub-CFP) 로 declare 한다 (ADR-064 §결정 3 룰 2 — 권장 1 + 대안 1):

- **(권장) sync agent 별 session/process 실행** — sync write-commit agent 를 parent Orchestrator session 과 분리된 session/process 로 실행해 parent `defaultMode: bypassPermissions` 상속을 차단한다. 분리 session 은 non-bypassPermissions default 를 가지므로 agent frontmatter `permissionMode: default` 가 무효화되지 않는다 — write-time 권한 prompt 가 실 enforce 된다. (sync agent `background: true` auto-deny fail-closed, §결정 4 정합과 결합 시 prompt-less auto-deny.)
- **(대안) settings.json sync-agent 전용 non-bypassPermissions profile 분리** — settings 의 `defaultMode` 를 sync agent scope 한정 non-bypassPermissions profile 로 분리한다. parent 전역 bypassPermissions 와 sync agent profile 을 disjoint 하게 wire (Option B per-tool deny decomposition 의 profile-level 확장).
- **declaration-only Wave 1**: 두 후보 모두 settings.json / orchestration 실 wire 영역 = 본 Amendment 범위 밖. 실 wire = Wave 2 mechanical carrier (별 sub-CFP). §결정 3 settings deny deferral 패턴 답습 (ADR-082 §결정 6 / ADR-070 §D5 retain pattern — pattern_count >= 2 재발 시 follow-up CFP MUST promote).
- **채택 근거 (ADR-064 §결정 3 룰 2)**: 권장 (별 session/process 실행) 은 (1) parent bypassPermissions 상속 자체를 차단 (구조적 root cause 해소) + (2) `background: true` auto-deny fail-closed 와 결합 시 prompt-less 차단 → 권장. 대안 (settings profile 분리) 은 settings.json 단일 file 수정으로 가능하나 profile-level disjoint wire 복잡도 + bypassPermissions scope-spanning 위험 잔존 → 차선.

### 결과 (Amendment 2 영역만)

#### 긍정

- W5-S15 P1-1 보안 gap 정직 명문화 — write-time permission enforce 한계 (permissionMode 무효화 + settings deny deferred) 를 agent file §7.6 declare 에서 ADR-103 mechanism SSOT 로 끌어올림. 미wire 상태의 정직 문서화 (보호 강도 축소 아님).
- read-path dual-layer verify load-bearing 명시 — write-time prevention 미보장 interim 구간의 보상통제 mechanism 명확화. governance state poisoning 전 차단 (3-anchor AND + Orchestrator 2차 verify dual-PASS gate).
- ADR-101 policy 의미 약화 0건 — 이미 존재하는 dual-layer verify 를 P1-1 맥락 load-bearing 으로 명시만 (3-anchor AND 의미 / verify 주체 재정의 0건, §결정 4 boundary invariant 보존).
- 예방 수정 경로 codify — write-time prevention 후보 2종 (session/process 분리 권장 / settings profile 분리 대안) Wave 2 carrier declare. interim 보상통제 → 예방 수정 transition path 명확.

#### 부정 / trade-off

- **write-time prevention interim 미보장** — settings deny wire (§결정 3 후속 Phase) 전까지 sync agent 의 unchecked Confluence write 가 구조적으로 가능. 완화 = read-path dual-layer verify load-bearing 보상통제 (6-B, governance state poisoning 전 catch) + write-time prevention Wave 2 carrier (6-C).
- **보상통제 = sufficient-not-complete** — read-path verify 는 governance state 오염을 차단하나, Confluence readable mirror 자체에 무단 write 가 land 하는 것은 막지 못한다 (catch-after-write, not prevent). git = SoR-work 무손상이므로 governance 무결성은 보존되나 Confluence readable degrade 가능. 완화 = write-time prevention Wave 2 wire 후 prevent-before-write 로 격상.
- **mechanical lint deferred** — write-time prevention 실 wire (session/process 분리 / settings profile) = Wave 2 mechanical carrier (별 sub-CFP). 본 Amendment = declarative (declaration-only Wave 1). ADR-082 §결정 6 / ADR-070 §D5 retain pattern (pattern_count >= 2 재발 시 promote 의무).

### invariant 금지 (Amendment 2)

본 Amendment 는 다음 invariant 를 위반하지 않는다:

- **ADR-101 policy 의미 약화 0건** (ADR-101 §결정 4 boundary invariant) — 3-anchor AND 의미 / dual-layer verify 주체 (1차 sync agent / 2차 Orchestrator) 재정의 0건. 이미 존재하는 verify 를 P1-1 맥락 load-bearing 으로 명시만 (mechanism 강조, policy 재정의 아님).
- **one-way git → Confluence push invariant** (ADR-103 §결정 1) — write-time prevention 후보 (6-C) 도 git → Confluence 단방향 보존, 역방향 push 0건 (outbound-only, ADR-101 §결정 2 정합).
- **ratchet 강화 방향** (ADR-058 §결정 5) — write-time permission 한계 정직 declare + read-path verify load-bearing 명시 + 예방 수정 Wave 2 carrier = 강화 방향 (보호 강도 축소 0건, 미wire 상태의 정직 문서화 + 보상통제 명시). 약화 surface 0건 → sunset_justification N/A.
- **declaration-only Wave 1** (§결정 3 / ADR-082 §결정 6 / ADR-070 §D5 retain pattern) — 예방 수정 실 wire = Wave 2 mechanical carrier (별 sub-CFP). `mechanical_enforcement_actions: []` + `is_transitional: false` 유지.
- **carrier-preserved sunset 0건** (ADR-097 §결정 3) — 기존 §결정 1-5 + Amendment 1 약화/sunset 0건, §결정 6 추가만 (보상통제 load-bearing 명시 + 예방 후보 declare).
