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
  - amendment: 3
    date: 2026-06-16 KST
    carrier_story: CFP-confluence-aprime
    parent_epic: null   # surgical 단일 Story (A-prime 운영 모델 git 박제 + forward 동기화 스캐폴드)
    direction: strengthening   # A-prime 운영 모델 = 기존 one-way git→Confluence push (§결정 1) 위에 forward 경로 자동화 + backward(Confluence 편집 → git PR 제안, lossy-tolerant) 경로 추가. git = SoR-work invariant (ADR-100 §결정 1) 무손상 확장 — backward 는 "제안"(PR 역류)일 뿐 git 이 최종 정본, 역방향 직접 write 0건. ratchet 강화 (운영 모델 명문화 + 자동화 스캐폴드, 약화 surface 0건)
    sunset_justification: null   # 강화 방향 (운영 모델 codify + forward 자동화 scaffold + backward 설계). ADR-058 §결정 5 sunset_justification 의무 = 강화 방향이므로 N/A. one-way git→Confluence push invariant (§결정 1) 무손상 — forward 는 그 단방향 push 의 자동화, backward 는 inbound 직접 write 가 아니라 git PR 제안(사람 검토 + git 최종 정본)이므로 outbound-only invariant (ADR-101 §결정 2) 위반 0건. ADR-101 policy 의미 약화 0건 (3-anchor AND / dual-layer verify 주체 재정의 0건). ADR-100 git=SoR-work 보존 (Confluence = 공식 읽기 + 사람 편집 표면 격상이되 작성 정본은 git, 편집은 PR 역류). 약화 방향 (forward 자동 폐지 / backward 직접 git write / git=SoR-work 역전) 차단
    summary: "A-prime 운영 모델 codify — git = 작성 정본(SoR-work) 불변 + Confluence = 공식 읽기 + 사람 편집 표면 격상. forward(자동 git→Confluence): git 문서 main 머지 → CI 가 변경 doc 추출 → ADR-123 읽기 표준으로 AI 재렌더 후 발행(secret 부재 시 dry-run, 실 호출 0). backward(Confluence 편집 → git PR 제안): 주기적 폴링으로 변경 페이지 감지 → ADF→markdown 변환(lossy, 제안 수준) → gh pr create 로 제안 PR(git 이 최종 정본, 손실 허용). forward scaffold = scripts/confluence_forward_sync.py (ADR-061 외부 .py) + .github/workflows/confluence-forward-sync.yml (required check 아님) + docs/confluence-mirror-manifest.yaml (파일경로→page_id). backward = 설계만(구현 후속). mirror 대상 = ADR-111 closed-enum 5 (ADR/Living Architecture/Change Plan/Domain Knowledge/Orchestrator Playbook) + guides, 면제 = Story/FIX/Lane Evidence/decision packet/spawn prompt (ADR-111 §결정 2 retain-ban). declaration + scaffold-only (실 자동 발행 = secret 주입 후속)."
  - amendment: 4
    date: 2026-06-16 KST
    carrier_story: CFP-confluence-aprime
    parent_epic: null   # surgical 단일 Story (A-prime forward 1차 경로 = secret 없는 MCP 세션 방식 명확화)
    direction: strengthening   # forward 동기화의 1차(primary) 경로를 명확화 — git 문서를 편집하는 주체가 항상 Claude 세션(에이전트/Orchestrator)이므로, 그 세션이 같은 흐름에서 MCP(Atlassian)로 Confluence 를 갱신한다(secret·CI 불필요). CI GitHub Action + 토큰 secret 경로 = 선택적 무인(headless) fallback 한정. Amendment 1 MCP-direct path 와 동일 원리의 정식 1차 경로 격상 — 약화 surface 0건(기존 §결정 7 forward 자동화 보존, 1차/fallback 우선순위만 명문화)
    sunset_justification: null   # 강화 방향 (forward 1차 경로 명확화 + secret 의존 제거). ADR-058 §결정 5 sunset_justification 의무 = 강화 방향이므로 N/A. §결정 1 one-way git→Confluence push invariant 무손상 — MCP 세션 경로도 createConfluencePage/updateConfluencePage(write 방향)만, 역방향 직접 write 0건(Amendment 1 §결정 1-A ALTERNATIVE invariant 정합). ADR-101 §결정 2 outbound-only invariant 보존. CI Action + secret 경로 = 폐기 아님(선택적 무인 fallback 보존). 약화 방향(MCP 세션 1차 경로 폐지 / secret 강제 회귀 / backward 직접 git write) 차단
    summary: "A-prime forward 1차 경로 = secret 없는 MCP 세션 방식 명확화 — git 문서를 편집하는 주체가 항상 Claude 세션(codeforge 에이전트/Orchestrator)이므로, forward 동기화는 그 세션이 같은 흐름(ADR-026 post-merge 후처리)에서 MCP(Atlassian)로 Confluence 페이지를 갱신한다(secret·CI·cron 불필요). 250페이지 초기 이관과 동일 방식, 변경분만 처리. 시점 = 문서 PR 머지 후처리. CI GitHub Action(scripts/confluence_forward_sync.py + confluence-forward-sync.yml) + 토큰 secret 경로 = 선택적 무인(headless) fallback 한정(세션 없이 돌릴 때만). backward(Confluence 편집 → git PR 제안)도 동일 원리 — 세션이 MCP 로 Confluence 읽어 ADF→markdown 변환 후 git PR 제안. Amendment 1 MCP-direct path(precedent first)를 forward 정식 1차 경로로 격상. §결정 1 one-way push + ADR-101 outbound-only invariant 무손상(MCP 세션도 write 방향만, 역방향 직접 write 0건)."
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
- `scripts/confluence_forward_sync.py` — Amendment 3 (§결정 7) forward 동기화 스캐폴드 + Amendment 4 (§결정 8-B) 선택적 무인(headless) fallback (ADR-061 외부 .py, --build-manifest / 기본 sync 모드, secret 부재 dry-run). 1차 경로 = Claude 세션 MCP 갱신(secret 불필요, §결정 8-A)
- `.github/workflows/confluence-forward-sync.yml` — Amendment 3 (§결정 7-B) forward CI workflow + Amendment 4 (§결정 8-B) 선택적 무인(headless) fallback (on push main, paths docs/** + archive/adr/**, required check 아님, secret 미설정 dry-run). 1차 경로 = Claude 세션 MCP 갱신(§결정 8-A)
- `docs/confluence-mirror-manifest.yaml` — Amendment 3 (§결정 7-B) 파일경로 → page_id manifest schema (--build-manifest 로 채움)
- `docs/confluence-mirror-playbook.md` — Amendment 3 (§결정 7) §자동화 로드맵 A-prime 갱신 + backward 편집 역류 설계 절

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

## Amendment 3 (2026-06-16 KST) — A-prime 운영 모델 (forward 자동 git→Confluence + backward Confluence 편집 → git PR 제안)

### 동인

사용자가 codeforge 문서 운영을 **A-prime 모델**로 확정했다 — git = 작성 정본(SoR-work) 은 그대로 두되, Confluence 를 단순 "읽기 사본"에서 **공식 "정본 읽기 + 사람 편집 화면"**으로 격상한다. 사람은 Confluence 에서 읽고 편집할 수 있으며, 그 편집은 git 으로 역류(PR 제안)된다. 핵심은 기존 git=정본 결정(ADR-100 §결정 1 git SoR-work)의 **역전이 아니라 확장**이다 — git 이 여전히 최종 정본이고, backward 경로는 손실 허용 "제안"일 뿐이다.

이는 §결정 1 의 one-way git→Confluence push 결정을 두 경로로 구체화한다:

- **forward (앞 방향, 자동)**: git 문서 변경(main 머지) → Confluence 자동 갱신. ADR-123(문서 가독성·소통 표준) 읽기 표준으로 AI 재렌더 후 발행. 기존 §결정 1 의 one-way push 를 CI 자동화로 instantiate.
- **backward (뒤 방향, 제안)**: 사람이 Confluence 페이지를 편집 → git PR 제안으로 역류. 손실 허용("제안" 수준) — git 이 최종 정본, 사람이 PR 을 검토·머지해야 정본 반영.

본 Amendment 는 §결정 1 의 one-way invariant 를 **약화시키지 않는다** — forward 는 그 단방향 push 의 자동화이고, backward 는 Confluence → git **직접 write 가 아니라** git PR 제안(사람 검토 + git 최종 정본)이다. inbound 직접 write surface 0건 (ADR-101 §결정 2 outbound-only invariant 보존).

### verified-via (Amendment 3 사실 인용 검증, ADR-082 §결정 2 write-time self-write verification 정합)

> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md (worktree, 본 file base) §결정 1 L98-114 — sync 구현체 = custom GitHub Action (OSS markdown→Confluence engine 기반, one-way git→Confluence push) + one-way invariant (git → Confluence 단방향, Confluence → git 역방향 push 0건). 본 Amendment 3 forward = §결정 1 push 의 자동화 instantiate, backward = git PR 제안(역방향 직접 push 아님) → one-way invariant 보존.
> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md §결정 2 L116-142 — 3-anchor (A git-source-hash / B native version / C sync commit SHA) + dual-layer verify (1차 sync agent / 2차 Orchestrator). 본 Amendment 3 = 각 anchor 의 실 계산/저장 대상 + AND 의미 재정의 0건 (ADR-101 §결정 4 boundary invariant 보존).
> verified-via: Read archive/adr/ADR-100-confluence-doc-ssot-recognition.md §결정 1 — git SoR-work ↔ Confluence SoR-docs disjoint axis (git = 작성 정본, Confluence = authoritative readable). 본 Amendment 3 = Confluence 를 "사람 편집 표면"으로 격상하되 작성 정본 = git 보존 (편집은 PR 역류). ADR-100 Amendment 3 동반 발의 (cross-ref).
> verified-via: Read archive/adr/ADR-111-confluence-mirror-classification-policy.md §결정 1 (closed-enum 5 mirror 대상: ADR / Living Architecture / Change Plan / Domain Knowledge / Orchestrator Playbook) + §결정 2 (Issue-only retain 5 면제: Story file / FIX Ledger / Lane Evidence / decision packet / spawn prompt). 본 Amendment 3 forward scaffold 의 mirror 대상 = ADR-111 closed-enum 정합, retain-ban 영역 제외.
> verified-via: Read archive/adr/ADR-123-document-readability-and-communication-standard.md §결정 1-7 + 개정 1 — 읽기 표준(쉬운 말 / 격식 문서체 / 구조 결론 우선 / 한글 주 언어 / Confluence 렌더 한정 규칙 + 출처 패널 data-type="panel-note"). 본 Amendment 3 forward 의 AI 재렌더 = ADR-123 읽기 표준 적용.
> verified-via: Read archive/adr/ADR-061-python-script-writing-convention.md §결정 1 — 외부 .py 파일 실행 의무 (bash heredoc 안 multi-line Python 금지). 본 Amendment 3 forward scaffold = scripts/confluence_forward_sync.py 외부 .py (heredoc 0).
> verified-via: Read docs/adr/ADR-103-git-confluence-sync-mechanism.md frontmatter amendment_log[] = amendment 1 (CFP-1492) + amendment 2 (CFP-1321) → 본 Amendment 3 = third amendment (amendment_id slot 3 verified).

### 결정 — A-prime 운영 모델 codify (forward 자동 + backward 제안)

#### §결정 7 — A-prime 운영 모델: forward 자동 git→Confluence + backward Confluence 편집 → git PR 제안 (Amendment 3, CFP-confluence-aprime)

본 §결정 7 은 §결정 1 의 one-way git→Confluence push 를 A-prime 운영 모델로 구체화한다 — forward 자동 경로 + backward 제안 경로. git = SoR-work invariant (ADR-100 §결정 1) 무손상 확장.

##### 7-A — 역할 정의 (git = 작성 정본 / Confluence = 공식 읽기 + 사람 편집 표면)

| 채널 | 역할 | 변경 |
|---|---|---|
| **git** | 작성 정본(SoR-work) — 에이전트가 markdown 작성, PR · CI · 버전 거버넌스 적용 | 변경 없음 (ADR-100 §결정 1 git SoR-work 보존) |
| **Confluence** | 공식 "정본 읽기 + 사람 편집 화면" — 사람이 읽고 편집 가능 | "읽기 전용 사본" → "읽기 + 사람 편집 표면" 격상 (기존 §결정 1 readable mirror 확장) |

**역전 아님 invariant**: Confluence 가 사람 편집 표면으로 격상되더라도 **작성 정본 = git** 이다. Confluence 편집은 git PR 제안으로 역류하며(7-C), 사람이 PR 을 검토·머지해야 정본에 반영된다. git → Confluence → (편집) → git PR 제안 → (검토·머지) → git 의 닫힌 고리에서 git 이 항상 ground truth (ADR-100 §결정 1 disjoint axis 보존).

##### 7-B — forward 경로 (앞 방향, 자동 git → Confluence)

git 문서 변경(main 머지)이 Confluence 사본을 자동 갱신한다:

1. **변경 감지** — main push 시 CI 가 변경된 mirror 대상 문서를 추출(git diff 또는 인자로 받은 파일 목록).
2. **AI 재렌더** — Anthropic API(Claude) 로 ADR-123 읽기 표준 HTML 로 재렌더(쉬운 말 / 구조 결론 우선 / 출처 패널 `data-type="panel-note"` / 한글 제목 등).
3. **발행** — manifest(`docs/confluence-mirror-manifest.yaml`) 에서 파일경로 → page_id 를 찾아 Confluence REST 로 update. manifest 에 없으면 "최초 수동 발행 필요" 로그(자동 신규 생성은 중복 페이지 위험으로 보류, playbook §재이관 절차 정합).
4. **secret 부재 = dry-run** — `ANTHROPIC_API_KEY` / Confluence 자격증명 미설정 시 실제 API 호출 0건(dry-run), 변경 추출 + 매칭 결과만 로그.

forward 는 §결정 1 one-way push 의 CI 자동화 instantiate 다 — 새 mechanism 이 아니라 기존 단방향 push 의 trigger(git push) + engine(AI 재렌더) + verify(3-anchor stamp, §결정 2) wire.

##### 7-C — backward 경로 (뒤 방향, Confluence 편집 → git PR 제안, lossy-tolerant)

사람이 Confluence 페이지를 직접 편집한 경우, 그 편집을 git 으로 역류한다 — **단 "제안"(PR) 수준, git 이 최종 정본**:

1. **변경 감지** — 주기적 폴링(예: cron)으로 native version 이 마지막 sync SHA(§결정 2 anchor C) 이후 증가한 페이지 감지.
2. **역변환** — Confluence ADF/storage format → markdown 변환(**lossy** — round-trip 비-deterministic, 제안 수준).
3. **PR 제안** — 변환된 markdown 을 git feature 브랜치에 반영하고 `gh pr create` 로 제안 PR 생성. 사람이 검토·정정 후 머지해야 정본 반영.

**lossy-tolerant invariant**: backward 는 손실 허용이다 — ADF → markdown round-trip 이 비-deterministic이므로 변환 결과는 "초안 제안"일 뿐이고, 사람 검토가 정확성 게이트다. git = SoR-work 이므로 변환이 부정확해도 git 정본은 사람 머지 전까지 무손상.

**inbound 직접 write 아님 invariant (one-way push 보존)**: backward 는 Confluence → git **직접 push 가 아니다** — git PR 제안(사람 검토 + git 최종 머지)이다. 따라서 §결정 1 one-way git→Confluence push invariant + ADR-101 §결정 2 outbound-only invariant 위반 0건. Confluence → wrapper inbound webhook 0건 (폴링은 git 측 outbound read).

##### 7-D — mirror 대상 / 면제 (ADR-111 closed-enum 정합)

forward/backward 대상 = ADR-111 §결정 1 closed-enum 5 (ADR / Living Architecture / Change Plan / Domain Knowledge / Orchestrator Playbook) + 사람이 읽는 guides(안내서) 영역. ADR-111 §결정 2 Issue-only retain 5 면제(Story file / FIX Ledger / Lane Evidence / decision packet / spawn prompt) 는 **sync 대상 제외**(진행 산출물 — git · Issue 채널 한정, Confluence mirror 금지).

##### 7-E — 한계 정직 declare (secret 필요 / ADF lossy / scaffold-only)

- **secret 필요** — forward 자동 발행은 `ANTHROPIC_API_KEY`(AI 재렌더) + Confluence 자격증명(`CONFLUENCE_*`) 주입이 전제. 미주입 시 dry-run(실 호출 0). 완전 자동은 secret 운영 주입 후 활성(playbook §자동화 로드맵 정합).
- **ADF lossy (backward)** — Confluence storage/ADF → markdown 변환은 비-deterministic round-trip 이라 제안 수준. 정확성 게이트 = 사람 PR 검토.
- **scaffold-only (Wave 1)** — 본 Amendment 의 forward 는 scaffold(스크립트 + workflow + manifest schema) 까지, 실 자동 발행(secret 주입 + manifest 전수 채움)은 후속. backward 는 **설계만**(구현 = 복잡 + secret 필요, 후속 carrier). declaration + scaffold-only.

### 결과 (Amendment 3 영역만)

#### 긍정

- A-prime 운영 모델 git 박제 — git = 작성 정본 / Confluence = 공식 읽기 + 사람 편집 표면 역할이 §결정 1 위에 명문화. forward 자동 + backward 제안 양 경로 codify.
- forward 자동화 scaffold — 기존 §결정 1 one-way push 의 CI 자동화 instantiate (변경 감지 + AI 재렌더 + 발행 + 3-anchor stamp). secret 부재 dry-run fail-safe.
- git = SoR-work 보존 (역전 아님) — Confluence 격상이 작성 정본을 옮기지 않음. backward 는 PR 제안(사람 검토 + git 최종 정본), inbound 직접 write 0건.
- ADR-101 policy 의미 약화 0건 — 3-anchor AND / dual-layer verify 주체 재정의 0건 (§결정 4 boundary invariant 보존). forward 발행 시 3-anchor stamp = §결정 2 그대로.
- 한계 정직 declare — secret 필요 / ADF lossy / scaffold-only 명시 (playbook §자동화 로드맵 정합, 거짓 "완전 자동" 주장 0건).

#### 부정 / trade-off

- **backward 구현 미완 (설계만)** — Confluence 편집 → git PR 제안 경로는 설계 declare 까지, 실 폴링/변환/PR 생성 = 후속 carrier (복잡 + secret 필요). 완화 = 설계 명문화(7-C) + backward 미활성 동안 playbook §재이관 절차(사람 수행)가 정본 보호.
- **forward 자동 발행 미활성 (secret 부재)** — `ANTHROPIC_API_KEY` + Confluence 자격증명 미주입 시 dry-run 만, 실 발행 0. 완화 = dry-run fail-safe(실 호출 0 안전 동작) + secret 주입 후 활성 + playbook §자동화 로드맵 정직 declare.
- **ADF lossy (backward)** — round-trip 비-deterministic 으로 backward 변환이 부정확 가능. 완화 = "제안"(PR) 수준 invariant + 사람 검토 정확성 게이트 + git = SoR-work 무손상 (사람 머지 전 정본 보존).
- **manifest 전수 미채움** — `docs/confluence-mirror-manifest.yaml` 예시 2~3 entry 만, 전수 채움 = 후속. manifest 부재 page 는 forward 시 "최초 수동 발행 필요" 로그 + skip (중복 페이지 대량 생성 차단).

### invariant 금지 (Amendment 3)

본 Amendment 는 다음 invariant 를 위반하지 않는다:

- **one-way git → Confluence push invariant** (§결정 1) — forward 는 단방향 push 의 자동화, backward 는 git PR 제안(역방향 직접 push 아님). Confluence → wrapper inbound webhook 0건, outbound-only invariant (ADR-101 §결정 2) 보존.
- **git = SoR-work invariant** (ADR-100 §결정 1) — Confluence 가 사람 편집 표면으로 격상되되 작성 정본 = git. backward 편집은 PR 제안(사람 검토 + git 최종 머지) → git 항상 ground truth, 역전 0건.
- **ADR-101 policy 의미 약화 0건** (ADR-101 §결정 4 boundary invariant) — 3-anchor AND 의미 / dual-layer verify 주체 (1차 sync agent / 2차 Orchestrator) 재정의 0건. forward 발행 시 3-anchor stamp = §결정 2 instantiate.
- **mirror classification 무손상** (ADR-111 §결정 1/2) — mirror 대상 = closed-enum 5, 면제 = Issue-only retain 5 (Confluence mirror 금지). forward/backward 가 retain-ban 영역을 sync 하지 않음.
- **ratchet 강화 방향** (ADR-058 §결정 5) — 운영 모델 codify + forward 자동화 scaffold + backward 설계 = 강화 방향 (one-way push 자동화 + 사람 편집 표면 격상, 약화 surface 0건). sunset_justification N/A.
- **declaration + scaffold-only Wave 1** — backward 구현 + forward 실 자동 발행(secret 주입 + manifest 전수) = 후속 carrier. `mechanical_enforcement_actions: []` + `is_transitional: false` 유지.

## Amendment 4 (2026-06-16 KST) — forward 1차 경로 = secret 없는 MCP 세션 방식 명확화 (CI + secret = 선택적 무인 fallback)

### 동인

Amendment 3 §결정 7-B 가 forward 경로를 CI 자동화(GitHub Action + AI 재렌더 + secret) 중심으로 기술하면서, secret 부재 시 dry-run(7-E)을 한계로 declare 했다. 그러나 핵심 사실을 명확히 못 박지 못했다 — **git 문서를 편집하는 주체는 항상 Claude 세션(codeforge 에이전트 또는 Orchestrator)이다.** 따라서 forward 동기화는 별도 CI·secret·cron 없이도 **그 세션이 같은 흐름에서 MCP(Atlassian)로 Confluence 페이지를 갱신**하면 충분하다.

이는 가설이 아니라 실증된 경로다 — Amendment 1 §결정 1-A 가 codify 한 MCP-direct path(Orchestrator main session OAuth + `createConfluencePage`/`updateConfluencePage` 직접 호출)가 이미 250여 페이지 초기 이관을 secret 없이 완수했다. forward 동기화는 그 동일 방식을 **변경분에만** 적용하는 것이다.

본 Amendment 는 §결정 7-B forward 경로의 **1차(primary) 경로 = secret 없는 MCP 세션 방식**임을 명확화하고, CI GitHub Action + 토큰 secret 경로를 **선택적 무인(headless) fallback**으로 격하 명시한다. backward(7-C)도 동일 원리(세션이 MCP 로 Confluence 읽어 git PR 제안)임을 명시한다. §결정 1 one-way push invariant + §결정 7 forward 자동화 보존 — 1차/fallback 우선순위만 명문화하는 강화 방향이다.

### verified-via (Amendment 4 사실 인용 검증, ADR-082 §결정 2 write-time self-write verification 정합)

> verified-via: Read archive/adr/ADR-103-git-confluence-sync-mechanism.md (worktree, 본 file base) §결정 7-B L536-545 — forward 경로(변경 감지 → AI 재렌더 → 발행 → secret 부재 dry-run) + 7-E L563-567 secret 필요 한계 declare. 본 Amendment 4 = 그 forward 의 1차 경로를 MCP 세션 방식으로 명확화(CI + secret = fallback 격하), §결정 7 forward 자동화 본문 보존(확장만).
> verified-via: Read archive/adr/ADR-103-git-confluence-sync-mechanism.md Amendment 1 §결정 1-A L350-355 — MCP-direct path(Orchestrator main session OAuth + `mcp__plugin_atlassian_atlassian__createConfluencePage`/`updateConfluencePage`/`getConfluencePage` 직접 호출, mark engine 미경유) + 1-C L368-374 subagent OAuth limitation(Orchestrator inline path 의무). 본 Amendment 4 = 그 MCP-direct path 를 forward 정식 1차 경로로 격상(precedent first, codify second).
> verified-via: Read archive/adr/ADR-103-git-confluence-sync-mechanism.md Amendment 1 §결정 1-A L350-355 PRIMARY/ALTERNATIVE 표 — 기존 routing 은 mark engine(secret 활성) = PRIMARY / MCP-direct = ALTERNATIVE(secret 미활성·ad-hoc 한정)였다. 본 Amendment 4 가 A-prime forward 일상 sync 영역에서 우선순위를 재정렬한다(MCP 세션 = 1차 / CI+secret = headless fallback). Amendment 1 deviation declare 4-tuple(1-B)은 MCP 세션 forward 의 표준 절차로 흡수.
> verified-via: 외부 지식(검증 후 단언) — Atlassian MCP 의 OAuth scope 는 세션 단위로 부여되며(Amendment 1 §결정 1-C 명시), 세션이 직접 MCP tool 을 호출하면 별도 토큰 secret(`CONFLUENCE_API_TOKEN` 등) 주입 없이 Confluence write 가 가능하다. CI runner 는 세션이 없으므로 token secret 으로 basic-auth 해야 한다(headless fallback 의 secret 의존 근거).
> verified-via: Read docs/adr/ADR-026 (worktree, post-merge 후처리 — 가용 시 cross-ref) — PR merge 후처리 자동화 flow. forward MCP 세션 갱신 시점 = 문서 PR 머지 후처리(post-merge) 단계 정합. (ADR-026 본문 직접 인용은 후속 verify 영역 — 시점 명시만, mechanism 재정의 0건.)
> verified-via: Read archive/adr/ADR-103-git-confluence-sync-mechanism.md frontmatter amendment_log[] = amendment 1 (CFP-1492) + amendment 2 (CFP-1321) + amendment 3 (CFP-confluence-aprime) → 본 Amendment 4 = fourth amendment (amendment_id slot 4 verified).

### 결정 — forward 1차 경로 = MCP 세션 / CI + secret = 선택적 무인 fallback

#### §결정 8 — forward 1차 경로 = secret 없는 MCP 세션 방식 (Amendment 4, CFP-confluence-aprime)

본 §결정 8 은 §결정 7-B forward 경로의 1차/fallback 우선순위를 명문화한다. §결정 7 forward 자동화 본문(7-A~7-E)은 보존하며, "어느 경로가 1차인가"만 확정한다.

##### 8-A — 1차 경로 = Claude 세션 MCP 갱신 (secret·CI·cron 불필요)

forward 동기화의 1차(primary) 경로는 **문서를 편집한 Claude 세션이 같은 흐름에서 MCP(Atlassian)로 Confluence 를 직접 갱신**하는 것이다.

- **근거 — 편집 주체 = 항상 Claude 세션**: git 문서(ADR / Living Architecture / Change Plan / Domain Knowledge / Orchestrator Playbook / guides)를 작성·수정하는 주체는 언제나 codeforge 에이전트 또는 Orchestrator 다. 그 세션이 문서를 머지한 직후 같은 세션 안에서 변경분을 MCP 로 Confluence 에 반영하면, 별도 인프라(CI runner / token secret / cron)가 전혀 필요 없다.
- **시점 = 문서 PR 머지 후처리(ADR-026 post-merge)**: forward MCP 갱신은 문서 PR 머지 후처리 단계에서 수행한다. 머지를 확인한 Orchestrator 가 변경된 mirror 대상 문서를 ADR-123 읽기 표준으로 재렌더한 뒤 MCP `updateConfluencePage`(신규는 `createConfluencePage`)로 발행한다.
- **mechanism = Amendment 1 MCP-direct path 의 forward 격상**: 사용 tool = `mcp__plugin_atlassian_atlassian__getConfluencePage` / `updateConfluencePage` / `createConfluencePage`(Amendment 1 §결정 1-A ALTERNATIVE 와 동일 tool subset). Orchestrator inline path 의무(Amendment 1 §결정 1-C) — MCP 의 OAuth scope 는 Orchestrator main session 한정이므로 subagent spawn 위임 시 401 unauthenticated 차단, MCP 갱신은 Orchestrator main session inline 실행.
- **secret 0건**: MCP 세션 경로는 세션 OAuth scope 를 쓰므로 `ANTHROPIC_API_KEY` / `CONFLUENCE_API_TOKEN` 등 토큰 secret 주입이 불필요하다(AI 재렌더도 세션 자체가 Claude 이므로 별도 API 키 불요). 이것이 250여 페이지 초기 이관을 secret 없이 완수한 그 방식이며, forward 는 변경분에만 동일하게 적용한다.

##### 8-B — CI GitHub Action + 토큰 secret 경로 = 선택적 무인(headless) fallback

§결정 7-B 가 기술한 CI 자동화 경로(scripts/confluence_forward_sync.py + .github/workflows/confluence-forward-sync.yml + token secret)는 **1차 경로가 아니라 선택적 무인(headless) fallback** 이다.

- **fallback 적용 영역 = 세션 없이 돌릴 때만**: Claude 세션 밖에서 무인으로 forward 를 돌려야 하는 경우(예: 사람·에이전트 개입 없는 야간 배치 / 외부 트리거)에 한정. 일상 forward(세션이 문서를 머지하는 정상 흐름)는 1차 MCP 세션 경로가 cover.
- **fallback 의 secret 의존**: CI runner 는 세션 OAuth 가 없으므로 token secret(`CONFLUENCE_API_TOKEN` 등 basic-auth)으로 인증해야 한다 — 이것이 §결정 7-E secret 필요 / dry-run 한계의 실제 적용 범위다(1차 경로가 아니라 fallback 의 전제).
- **fallback 보존(폐기 아님)**: CI Action 경로는 폐기되지 않는다. 무인 실행 surface 를 위해 scaffold 로 보존하되, 우선순위는 MCP 세션 경로 다음이다.

##### 8-C — backward 도 동일 원리 (세션 + MCP)

backward(§결정 7-C, Confluence 편집 → git PR 제안)도 동일 원리다 — Claude 세션이 MCP(`getConfluencePage` / `getConfluencePageDescendants`)로 변경된 페이지를 읽어 ADF → markdown 변환 후 `gh pr create` 로 git PR 제안을 만든다. backward 역시 1차 경로 = 세션 + MCP(secret·cron 불필요), 무인 폴링 cron 은 선택적 fallback. inbound 직접 write 0건 invariant(§결정 7-C, 폴링은 git 측 outbound read + PR 제안) 무손상.

##### 8-D — invariant 보존 명시

- **§결정 1 one-way git→Confluence push invariant**: MCP 세션 경로도 `createConfluencePage`/`updateConfluencePage`(write 방향)만 사용, Confluence → git 역방향 직접 write 0건. backward 는 git PR 제안(사람 검토 + git 최종 정본).
- **ADR-101 §결정 2 outbound-only invariant**: MCP 세션 read(`getConfluencePage`)는 git 측 outbound, inbound webhook 0건.
- **§결정 2 3-anchor / dual-layer verify 재정의 0건**: MCP 세션 발행 시에도 3-anchor stamp(§결정 2) 적용. 단 MCP-direct 영역의 content property 3-anchor 부착 한계(Amendment 1 §결정 1-D accept-as-zero)는 동일 적용 — mark engine(CI) 활성 시 backfill 가능 영역.
- **§결정 7 forward 자동화 본문 보존**: 본 §결정 8 은 §결정 7-A~7-E 를 약화·삭제하지 않는다. forward 자동화 본문은 그대로 두고 1차/fallback 우선순위만 명문화한다(확장만).

### 결과 (Amendment 4 영역만)

#### 긍정

- forward 1차 경로 명확화 — "편집 주체 = 항상 Claude 세션" 이라는 핵심 사실 위에 1차 경로(세션 MCP 갱신, secret·CI·cron 불필요)를 못 박음. 250페이지 초기 이관과 동일 방식의 변경분 적용으로 정합.
- secret 의존 제거(1차 경로) — 토큰 secret 주입 없이도 forward 가 즉시 동작 가능(세션 OAuth scope). secret 은 무인 fallback 의 전제로 격하.
- CI Action 경로 보존(폐기 아님) — 무인 실행 surface 를 위해 scaffold 보존, 우선순위만 1차 MCP 세션 다음으로 명시.
- Amendment 1 MCP-direct precedent 의 forward 정식 격상 — 이미 실증된 경로를 forward 1차 경로로 codify(precedent first, codify second).
- invariant 무손상 — §결정 1 one-way push / ADR-101 outbound-only / §결정 2 3-anchor / §결정 7 forward 자동화 본문 보존(확장만).

#### 부정 / trade-off

- **세션 OAuth scope = Orchestrator main session 한정** — MCP 세션 forward 는 Orchestrator inline path 의무(Amendment 1 §결정 1-C), subagent 위임 시 401 차단. 완화 = inline path 명시(8-A) + 무인 실행 필요 시 CI fallback(8-B).
- **MCP-direct content property 3-anchor 부착 한계** — MCP 세션 경로는 content property tool 부재로 3-anchor stamp accept-as-zero(Amendment 1 §결정 1-D). 완화 = mark engine(CI fallback) 활성 시 backfill + read-path drift detection.
- **backward 구현 미완** — 8-C 도 설계 declare(§결정 7-C 정합), 실 폴링/변환/PR 생성 = 후속 carrier. 완화 = 1차 경로 원리 명시 + backward 미활성 동안 playbook §재이관 절차(사람 수행)가 정본 보호.

### invariant 금지 (Amendment 4)

본 Amendment 는 다음 invariant 를 위반하지 않는다:

- **one-way git → Confluence push invariant** (§결정 1) — MCP 세션 경로도 write 방향만, 역방향 직접 write 0건. backward 는 git PR 제안.
- **git = SoR-work invariant** (ADR-100 §결정 1) — git 이 작성 정본, MCP 세션은 그 정본을 Confluence 로 push 만. 역전 0건.
- **ADR-101 policy 의미 약화 0건** (ADR-101 §결정 4 boundary invariant) — 3-anchor AND 의미 / dual-layer verify 주체 재정의 0건.
- **§결정 7 forward 자동화 보존** — 7-A~7-E 약화·삭제 0건, 1차/fallback 우선순위 명문화만(확장).
- **CI Action + secret 경로 보존** (폐기 아님) — 무인 fallback scaffold 보존, 우선순위만 격하.
- **ratchet 강화 방향** (ADR-058 §결정 5) — forward 1차 경로 명확화 + secret 의존 제거 = 강화 방향(약화 surface 0건). sunset_justification N/A.
- **declaration + scaffold-only Wave 1** — `mechanical_enforcement_actions: []` + `is_transitional: false` 유지.
