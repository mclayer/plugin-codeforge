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
amendment_log: []
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
- `docs/adr/ADR-RESERVATION.md` — row 103 reserved → active 전환
