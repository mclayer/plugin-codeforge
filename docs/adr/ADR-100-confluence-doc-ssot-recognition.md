---
adr_number: 100
title: Confluence doc SSOT 인정 — wrapper governance docs 의 Confluence authoritative readable source 추가 (ADR-013 §결정 1 partial extend)
status: Accepted
category: governance
date: 2026-05-22
carrier_story: CFP-1215
parent_epic: CFP-1146
related_stories:
  - CFP-1215     # 본 carrier (Epic-A Wave 1 Story-2)
  - CFP-1146     # umbrella Epic-A (Atlassian suite 재결합 governance reversal)
related_adrs:
  - ADR-099      # Wave 1 Story-1 (sister, hard prerequisite — check-no-atlassian lint 역전 / Atlassian-allow 재정의). §결정 1 Layer 1 permission deny / Layer 2 lint allowlist 2-layer 분리. 본 ADR-100 의 평문 Confluence 참조가 ADR-099 §결정 2 Layer 2 allowlist 영역에 포함
  - ADR-013      # codeforge family dogfood-out — §결정 1 KEEP/MOVE. 본 ADR = §결정 1 KEEP 영역에 Confluence authoritative sync 추가 (partial extend, NOT full supersede — git SoR-work ↔ Confluence SoR-docs disjoint axis)
  - ADR-041      # doc location registry — §결정 6 Trigger #1/#2 (새 doc type / location 변경). 본 ADR = confluence variant / authoritative_source field intent declare-only, 실 yaml 변경 = ADR-103 defer (double-amendment 회피, schema_version 1.0→1.1 MINOR 예고)
  - ADR-027      # consumer adoption protocol — §결정 5 (consumer 절차 SSOT = consumer-guide.md). project.yaml atlassian.* schema = natural extend (충돌 0, bootstrap validation 자동 cover). token secret = *_env reference (project-config-schema.md deploy 1password env-key precedent 정합)
  - ADR-101      # verify-before-trust Confluence REST ground-truth — §결정 5 trust boundary (SSRF / 응답 변조 무결성 검증 owner). 본 commit 시점 reserved (S3 carrier, 미작성)
  - ADR-103      # git↔Confluence sync mechanism — narrow allow wire / sync agent / doc-locations.yaml confluence path 실 결정 owner. 본 commit 시점 reserved (W4 carrier, 미작성)
  - ADR-070      # verify-before-trust (외부 worker output) — §결정 5 Confluence REST 응답 변조 boundary 검증 책임 (ADR-101 ground-truth verify 정합)
  - ADR-064      # decision principle mandate — §self-application top-down ratchet (Layer 1 security 강화 = 약화 아님, sunset_justification null 정당)
  - ADR-058      # ADR sunset criteria mandate — §결정 7 보안 ADR presumption 인접 / §결정 5 ratchet (Layer 1 security 강화 방향)
  - ADR-082      # write-time self-write verification — forward cross-ref (ADR-101/103) reserved 명시 (미작성 anchor 단언 금지)
related_files:
  - .claude/settings.json                                                        # §결정 4 Layer 1 permissions.deny baseline SSOT (실 wire = Phase 2 S2/S3 carrier) + CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 verified (§결정 5 SendMessage leak surface)
  - docs/project-config-schema.md                                                # §결정 3 atlassian.* schema 신설 (token = *_env reference, deploy 1password env-key precedent 정합, 실 wire = Phase 2)
  - docs/doc-locations.yaml                                                       # §결정 2 confluence variant / authoritative_source field intent declare (실 변경 = ADR-103 defer)
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md                       # §결정 1 partial extend 대상 (KEEP 영역 Confluence authoritative sync 추가)
  - docs/adr/ADR-RESERVATION.md                                                   # row 100 reserved → active 전환
mechanical_enforcement_actions: []   # declaration-only Wave 1 — §결정 3 atlassian.* schema validator + §결정 4 settings.json deny baseline 실 wire = Phase 2 (S2/S3 carrier). ADR-082 §결정 6 retain pattern (Wave 1 declare / Wave 2 wire). pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier
is_transitional: false   # permanent governance — Confluence doc SSOT 인정 (git SoR-work ↔ Confluence SoR-docs disjoint axis) 은 Atlassian 재결합 후 영구 정책 방향. §결정 4 Layer 1 settings.json deny baseline + §결정 3 token-env-reference schema = 순수 security 강화 방향 (약화 아님)
sunset_justification: null   # is_transitional false — Confluence authoritative sync 추가 + Layer 1 deny baseline 은 영구 + security 강화. ADR-013 §결정 1 KEEP/MOVE 의미 약화 0건 (partial extend = KEEP 목록 보존, Confluence readable layer 추가). S4 ADR-102 약화 정당화는 Layer 2 lint 영역 한정 (ADR-099 §결정 4-A) — 본 ADR Layer 1 (security) + 데이터 흐름 (Confluence readable 추가) 영역은 약화 정당화 불요
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-1419
    date: 2026-05-24
    summary: "design doc Confluence-mirror 인정 범위 확장 — §결정 1 의 단일 'wrapper git-commit governance docs' phrasing 위에 ADR-111 closed-enum 4 대상 (ADR / Living Architecture / Change Plan / Domain Knowledge) 정식 codify. write boundary = ADR-103 sync agent 보존 (단방향 git→Confluence)."
    sunset_justification: "N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: 인정 범위 명시화 + closed-enum codify, forbid scope 축소 아님). ADR-064 §self-application top-down ratchet 정합. is_transitional: false 유지 (permanent governance policy)."
---

# ADR-100 — Confluence doc SSOT 인정 (wrapper governance docs 의 Confluence authoritative readable source 추가)

## 상태

`Accepted` (2026-05-22 KST) — CFP-1215 carrier (Epic-A Wave 1 Story-2). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 / ADR-099 row 99 chief author precedent 정합). 별도 Story file 없음 (Wave 1 Story-1 ADR-099 답습 — ADR 가 §3 설계 SSOT). dogfood-out (ADR-013): change-plan 은 wrapper repo 에 commit 안 함, ADR 만 wrapper commit.

## 컨텍스트

### 동인

사용자가 codeforge 의 git-native governance 에 Atlassian suite (Jira + Confluence) 를 **의도적으로 재결합** 결정했다 (Epic-A / CFP-1146). 이는 v0.7→v0.8 의 breaking change — Atlassian backend 완전 제거 — 의 **reversal** 이다 (사용자 비용 인지). brainstorm Phase 0+1+2 수렴 결과 Epic-A 의 4-layer architecture:

| Layer | source-of-record | 보존 / 신설 | Epic / Wave |
|---|---|---|---|
| **SoR-work** | GitHub (Issue / PR / commit) | 보존 (변경의 source of record) | 전 Wave invariant |
| **SoR-docs** | Confluence authoritative readable | A-2 신설 (wrapper governance docs) | 본 ADR-100 (W1 S2) |
| SoE-Jira (C) | Jira | 개인 layer (Systems of Engagement) | W4+ defer |
| SoE-Confluence (D) | Confluence 개인 영역 | 개인 layer | W4+ defer |

본 ADR-100 = **A-2 (SoR-docs = wrapper governance docs Confluence authoritative)** 의 governance SSOT. 선행 Wave 1 Story-1 (ADR-099, MERGED) 가 lint 역전 (hard prerequisite) 을 codify 했고, 본 ADR 은 그 위에서 "Confluence 가 wrapper governance docs 의 authoritative readable source 가 됨" 을 인정한다.

이 결정의 핵심 긴장: ADR-013 §결정 1 (dogfood-out KEEP/MOVE) + ADR-041 (doc location registry) 가 doc 의 git-native 위치를 SSOT 로 확정한 상태에서, Confluence 를 authoritative readable source 로 추가하면 두 SSOT 가 충돌할 위험이다. 본 ADR 은 **partial extend (NOT full supersede)** 로 이 긴장을 해소한다 — git = SoR-work, Confluence = SoR-docs 의 **disjoint axis** 명시가 핵심 mechanism.

### verified-via — 본 ADR 의 모든 사실 인용 검증

본 ADR 의 모든 §결정 / line / §N 인용은 ground truth direct Read 위에서 작성됐다 (ADR-082 §결정 2 write-time self-write verification 정합).

> verified-via: Read docs/adr/ADR-013 (worktree HEAD `49c3a82`) L107-108 / L126-127 — §결정 1 KEEP = `docs/adr/` + `docs/inter-plugin-contracts/` + `docs/orchestrator-playbook.md` + `templates/` + `scripts/` (plugin repo 잔류 runtime SSOT). MOVE = `docs/superpowers/specs/` + `docs/superpowers/plans/` + `docs/retros/` + `docs/stories/` + `docs/change-plans/` (internal-docs dogfood). §결정 1 본문 (L59-65) = "Plugin repo 잔류 = runtime SSOT (CLAUDE.md / playbook / ADR / inter-plugin-contracts / templates / scripts / agents / presets)".
> verified-via: Read docs/adr/ADR-041 (worktree) L41-89 §결정 1-6 — `docs/doc-locations.yaml` 단일 yaml SSOT. §결정 6 Trigger #1 (새 doc type → row 추가) / #2 (location 변경 → variants 갱신 + ADR amendment + migration). §결정 5 schema versioning (field 추가 = MINOR).
> verified-via: Read docs/doc-locations.yaml (worktree) L6 `schema_version: "1.0"` / L93-104 `adr` entry — variants = `single_repo` 단독 (confluence variant **부재**), `authoritative_source` field **부재**. doc_types 16 entry 어디에도 confluence variant 미존재.
> verified-via: Read docs/adr/ADR-027 (worktree) L145-147 §결정 5 — "Consumer 절차 SSOT = `docs/consumer-guide.md`. 본 ADR 은 결정만 freeze, 절차/명령어 SSOT 는 consumer-guide." → §결정 5 는 token 직접 규정 **아님** (SecurityArch P2 정정 정합). L700-742 §결정 11 — consumer overlay `deploy.*` schema 확장 (secret = env reference suffix).
> verified-via: Read docs/project-config-schema.md (worktree) L368-393 — deploy.* secret field = env-key reference suffix 패턴: `auth_secret_env` (L372) / `connect_token_env` (L384) / `key_secret_env` (L392). 평문 token 직접 기재 0건 — 모두 "GitHub Secrets key" / "env key" reference. → atlassian.* token schema 의 `*_env` reference 패턴 precedent.
> verified-via: Read docs/adr/ADR-099 (worktree) — §결정 1 2-layer (Layer 1 mcp__atlassian permission deny SSOT / Layer 2 lint grep 평문 allowlist) + §결정 2 allowlist 표 (L119 "wrapper docs/** Confluence authoritative 영역 / 사유 A-2 governance reversal / carrier ADR = ADR-100"). 본 ADR-100 = 그 carrier.
> verified-via: Bash `grep CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS .claude/settings.json` (worktree) L3 = `"1"` — agent-teams enabled 활성. → §결정 5 SendMessage secret leak surface = 실재 (가설 아님).
> verified-via: Read docs/adr/ADR-RESERVATION.md (worktree) L141 — row 100 = CFP-1146, status `reserved`, ADR file = `ADR-100-confluence-doc-ssot-recognition.md` (reservation 확정 파일명 정합). row 101 (ADR-101 verify-before-trust Confluence REST) / row 103 (ADR-103 git↔Confluence sync mechanism) = 모두 `reserved` (미작성 — forward cross-ref).
> verified-via: Bash `ls docs/adr/ADR-100*` (worktree) — file 부재 확인 (신규 작성).

### forward cross-ref reserved 명시 (ADR-082)

본 ADR 은 **ADR-101 (S3 verify-before-trust Confluence REST)** 와 **ADR-103 (W4 git↔Confluence sync mechanism)** 를 cross-ref 하나, 두 ADR 은 **본 commit 시점 미작성 (reserved)** 이다 (ADR-RESERVATION row 101/103 status `reserved` verified). 따라서 본 ADR 의 ADR-101/103 인용은 "owner 위임 + reserved" 로만 기술하며, 그 §결정 N 내용을 존재하듯 단언하지 않는다 (ADR-099 동일 pattern — 미존재 anchor 를 §0 verify 없이 단언 금지).

## 결정

### §결정 1 — Confluence doc SSOT 인정: ADR-013 §결정 1 KEEP 영역 partial extend (git SoR-work ↔ Confluence SoR-docs disjoint axis)

**판정 = partial extend** (NOT full supersede, NOT amend). ADR-100 은 ADR-013 §결정 1 의 **KEEP 목록 (`docs/adr/` + `docs/inter-plugin-contracts/` + playbook 등 plugin repo 잔류 runtime SSOT)** 에 **Confluence authoritative readable source 를 추가**한다 — git-commit 위치를 Confluence 로 재분류하지 않고, git 보존 위에 Confluence readable layer 를 얹는다.

#### disjoint axis (의미 희석 차단 — ArchitectAnalyst 권고)

ADR-013 §결정 1 KEEP 목록을 MOVE 로 재분류하면 full supersede + Epic-A SoR-work=GitHub 원칙 충돌 (금지). 두 SSOT 의 의미를 다음 disjoint axis 로 분리한다:

| axis | source-of-record | 의미 | 변경 source |
|---|---|---|---|
| **git = SoR-work** | GitHub git-commit (`docs/adr/` 등) | **변경의 source of record** — PR / commit / review gate / CODEOWNERS 결재가 거치는 정식 변경 채널 | 보존 (ADR-013 §결정 1 KEEP invariant) |
| **Confluence = SoR-docs** | Confluence authoritative readable | **doc 의 authoritative readable source** — 읽는 사람이 정식으로 참조하는 권위 readable 사본 | 추가 (본 ADR-100) |

즉 git 은 "**무엇을 어떻게 바꾸는가**" 의 SSOT (변경 ledger), Confluence 는 "**완성된 doc 을 어디서 권위 있게 읽는가**" 의 SSOT (readable authoritative). 두 축은 충돌하지 않는다 — sync 방향은 git → Confluence (변경은 git 에서 발생, Confluence 는 readable mirror 가 authoritative readable 로 격상). ADR-013 §결정 1 KEEP/MOVE 의미는 **희석되지 않는다** (KEEP 목록 그대로 git 보존, Confluence 는 readable layer 추가).

#### Confluence authoritative 대상 범위 정밀화 (이의 3 해소)

ArchitectAnalyst 이의 3 (dogfood vs consumer Confluence sync 범위 불일치) 을 다음으로 정밀화한다 — Epic-A A-2 "wrapper docs/{adr,retros,change-plans,inter-plugin-contracts}" 가 ADR-013 KEEP/MOVE 양쪽에 걸치는 모호성 해소:

| 대상 영역 | git 위치 | Confluence authoritative 대상 | sync source repo | carrier |
|---|---|---|---|---|
| **wrapper git-commit governance docs** (KEEP) — `docs/adr/` + `docs/inter-plugin-contracts/` + `docs/domain-knowledge/` + `docs/orchestrator-playbook.md` | wrapper repo (plugin) | **YES (본 ADR-100 1차 대상)** | wrapper repo | 본 ADR-100 |
| **dogfood-out docs** (MOVE) — `retros/` + `change-plans/` + `stories/` + `specs/` + `plans/` | internal-docs repo (dogfood) | YES (Epic-A scope 안) — 단 sync source = **internal-docs repo** (wrapper 아님) | mclayer/codeforge-internal-docs | ADR-103 (sync source repo 별도) |
| **consumer (비-dogfood) docs** | consumer repo (single_repo) | Epic-B scope (consumer multi-tenant) | consumer repo | Epic-B |

**§결정 1 의 "wrapper docs" = wrapper git-commit governance docs 로 정밀 정의** (KEEP 영역 우선 대상). dogfood-out docs (retros/change-plans/stories) 는 Epic-A scope 안이나 sync source 가 wrapper repo 가 아니라 **internal-docs repo** 다 (ADR-013 §결정 1 MOVE 정합 — dogfood artifact 는 internal-docs SSOT). consumer docs 는 Epic-B (multi-tenant). 이 3-way 분리로 "wrapper docs/** 가 KEEP/MOVE 양쪽 걸침" 모호성을 해소한다.

#### ADR-013 cross-ref Amendment 동반 (1줄 declare)

본 ADR-100 = ADR-013 §결정 1 의 partial extend 이므로, ADR-013 측에 1줄 cross-ref Amendment 동반을 **declare** 한다 (Phase 2 또는 후속 carrier 위임): "ADR-013 §결정 1 KEEP 영역에 Confluence authoritative readable sync 추가 허용 (git SoR-work 보존, Confluence SoR-docs readable layer 추가) — ADR-100 §결정 1." 본 cross-ref Amendment 는 ADR-013 KEEP/MOVE 목록을 변경하지 않는다 (additive, supersede 아님 — anti-drift historic-preserving 정합).

**채택 근거 (ADR-064 §결정 3 룰 2 — 권장 1 + 대안 1)**: partial extend (권장) 은 (1) Epic-A SoR-work=GitHub 원칙 보존 (git KEEP invariant) + (2) Confluence authoritative readable 인정 (A-2 governance reversal) + (3) ADR-013 의미 약화 0건 (disjoint axis 명시). **대안 = full supersede** (KEEP→MOVE 재분류, 채택 안 함, 근거 기록) — git 보존 원칙 충돌 + ADR-013 §결정 1 의미 파괴 → reject.

### §결정 2 — ADR-041 doc-locations.yaml 영향: confluence variant / authoritative_source field intent declare-only (실 변경 ADR-103 defer)

ADR-100 의 Confluence authoritative 인정은 ADR-041 doc-locations.yaml 에 **confluence variant** 또는 **`authoritative_source` field** 신설을 요구한다 — `adr` entry 등에 git path 외 Confluence authoritative readable 위치를 표기할 수단이 필요하다 (현 schema_version 1.0, `adr` entry variants = `single_repo` 단독 / `authoritative_source` field 부재, verified).

**그러나 실 yaml 변경은 ADR-103 까지 defer** — ADR-100 은 intent declare-only:

- **defer 근거 (ADR-041 §결정 6 Trigger #2 double-amendment 회피)**: ADR-103 (git↔Confluence sync mechanism) 이 미작성 (reserved) 상태이므로 **Confluence path 패턴 자체가 미정** 이다. sync mechanism 이 결정되기 전에 doc-locations.yaml 에 confluence variant path 를 확정 기재하면, ADR-103 결정 시 재변경 (double-amendment) 이 불가피하다. 따라서 본 ADR-100 은 **개념 declare** (confluence variant / authoritative_source field 가 신설될 것임 + schema_version 1.0→1.1 MINOR 가 발생할 것임) 만 하고, 실 yaml row 변경은 ADR-103 carrier 에 위임한다.
- **schema_version 1.0 → 1.1 MINOR 예고**: confluence variant 또는 authoritative_source field 추가 = backward-compatible field 추가 → ADR-041 §결정 5 (field 추가 = MINOR) 정합. 실 bump = ADR-103 commit 시점.
- **ADR-041 cross-ref Amendment 동반 (declare)**: ADR-041 §결정 6 Trigger #1 (새 variant/field 도입) 발동을 ADR-103 carrier 가 처리하되, 본 ADR-100 이 그 intent 를 선언한다. ADR-041 측 1줄 cross-ref: "Confluence authoritative readable source 도입 (ADR-100 §결정 2 intent declare) → confluence variant / authoritative_source field + schema_version 1.0→1.1 = ADR-103 carrier 실 변경."

본 §결정 2 = ADR-041 §결정 6 Trigger #2 double-amendment 회피 (sync mechanism 미결정 상태에서 yaml path 확정 기재 보류).

### §결정 3 — project.yaml atlassian.* schema (SecurityArch 권고 schema, secret = `*_env` reference only, ADR-027 natural extend)

consumer overlay `.claude/_overlay/project.yaml` 에 `atlassian.*` schema 를 신설한다 (실 wire = Phase 2 — project-config-schema.md 갱신). SecurityArch 권고 + project-config-schema.md deploy 1password env-key precedent 정합:

```yaml
atlassian:
  enabled: <bool>                 # true = Atlassian suite 재결합 활성 / false = git-native only (default)
  confluence:
    base_url: <string>            # NOT secret (Internal) — Confluence instance base URL
    space_key: <string>           # NOT secret (Internal) — Confluence space key
    api_token_env: <string>       # env key name (예: "ATLASSIAN_API_TOKEN") — 평문 token 금지, env reference only
    user_email_env: <string>      # env key name — basic-auth pair (Atlassian REST = email + token)
  jira:                           # W4+ declare-only (SoE-Jira 개인 layer, 본 ADR scope 외 — schema placeholder)
    project_key: <string>         # NOT secret (Internal)
```

#### secret boundary (SecurityArch §7.1)

- **Secret = `api_token` + `user_email`** (Atlassian REST basic-auth pair) — schema field 는 **`*_env` reference (env key name)** 만 허용, 평문 token / email 직접 기재 **금지**. 값은 env / secret store 경유 주입.
- **Internal (NOT secret) = `base_url` / `space_key` / `project_key`** — 평문 기재 허용.
- **precedent (verified)**: project-config-schema.md deploy.* 의 `auth_secret_env` (L372) / `connect_token_env` (L384) / `key_secret_env` (L392) = 모두 env-key reference suffix 패턴 (평문 secret 직접 기재 0건). atlassian.* token 도 동일 `_env` suffix reference 패턴.
- **token 인용 정정 (SecurityArch P2)**: 본 schema 의 token 규정 근거는 "ADR-027 §결정 5 본문" 이 **아니다** (§결정 5 = "consumer 절차 SSOT = consumer-guide.md", verified L145-147 — token 직접 규정 아님). 정확한 cite = **ADR-027 consumer adoption schema 정합 + project-config-schema.md deploy.1password env-key precedent (L380-385)**.

#### ADR-027 natural extend (충돌 0)

atlassian.* schema 신설은 ADR-027 amendment 불요 — atlassian.* schema 가 project-config-schema.md 갱신으로 bootstrap validation 이 자동 cover 한다 (ADR-027 §결정 1 bootstrap 검증 책임 = wrapper overlay/hooks/, ArchitectAnalyst 권고). consumer 측은 project-config-schema.md SCHEMA_RULES validator 추가 (Phase 2 carrier) 로 자동 검증. ADR-027 와 충돌 surface 없음 = natural extend.

### §결정 4 — Layer 1 settings.json mcp__atlassian deny baseline (SecurityArch P1 — scope 분리, narrow allow W4 defer)

`.claude/settings.json` `permissions.deny` 에 `mcp__atlassian` 서버 전체 + 모든 tool 을 deny baseline 으로 wire 한다 (실 wire = Phase 2 — S2/S3 carrier). ADR-099 §결정 1 Layer 1 (permission deny SSOT) 정합:

```jsonc
// .claude/settings.json permissions.deny (S2/S3 carrier wire)
"deny": ["mcp__atlassian", "mcp__atlassian__*"]
```

+ **모든 agent preset 에 atlassian tool 미포함 (= 자연 deny)** — preset tool list 에 `mcp__atlassian__*` 을 넣지 않음으로써 default 차단.

#### deny vs narrow-allow mechanically 충돌 경고 (SecurityArch P1 CRITICAL)

Claude Code permissions 에서 **deny 가 allow 를 무조건 이긴다** (first-match-wins / deny precedence, WebFetch verified). 따라서 다음 동시 설정 = **mechanically broken**:

- `deny: ["mcp__atlassian", "mcp__atlassian__*"]` (서버 전체) **+** `allow: ["mcp__atlassian__<tool>"]` (narrow) 를 동시에 설정하면 → narrow allow 가 deny 에 막혀 **무효** (narrow allow tool 도 deny precedence 로 차단됨).

이 충돌의 함의:

- **현 시점 narrow allow 받을 정식 sync agent = 미존재** (W4 / ADR-103 carrier — sync agent 미정의). 사용처 0 시점에 read-only narrow allow 를 선제 부여하면 SSRF / 응답 변조 surface 를 사용처 없이 개방 = 최소권한 위반.
- 따라서 **narrow allow = W4 declare-only defer** (SecurityArch P1 채택 = (a) W4 defer / read-only 선제 부여 reject).
- **W4 에서 narrow allow wire 시 settings deny 를 서버-전체로 유지하면 안 됨** — scope 분리 / managed-only 메커니즘 (deny 를 narrow allow 대상 tool 에서 제외하거나, managed permission layer 로 분리) 이 필요하다. 이 scope 분리 메커니즘의 empirical verify = **ADR-103 owner** (deny precedence 우회 방법은 ADR-103 가 WebFetch / 실측 verify 후 결정).

#### Layer 분리 cross-ref (ADR-099 §결정 1 정합)

본 §결정 4 (Layer 1 permission deny) 는 ADR-099 §결정 2 (Layer 2 lint grep 평문 allowlist) 와 **disjoint** 다 — Layer 1 = `mcp__atlassian__*` MCP 호출 차단 (settings.json + agent preset, security 보장) / Layer 2 = 평문 `atlassian|Confluence|Jira` 참조 governance detection (grep lint, warning tier). 본 ADR-100 의 평문 Confluence 참조 (governance docs) 는 ADR-099 §결정 2 Layer 2 allowlist 영역에 포함된다 (L119 표 — "wrapper docs/** Confluence authoritative 영역 / carrier ADR-100").

### §결정 5 — trust boundary (SecurityArch §7.5 통합: SendMessage leak / SSRF / 응답 변조, ADR-101 cross-ref)

Atlassian 재결합은 신규 외부 trust boundary 를 도입한다. SecurityArch consult 결과를 명시 + Layer 1 permission deny 가 1차 방벽임을 cross-ref 한다 (boundary completeness I-1/I-2 정합):

#### agent-teams SendMessage secret leak (SecurityArch P1)

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성 (settings.json L3 verified). W4 sync agent (ADR-103) 의 Confluence REST 응답이 SendMessage 로 sibling teammate 에 전파되면 → **token literal / Confluence content 누설** 가능. 완화 (W4 / ADR-103 위임):

- **sync agent tool output sanitization 의무** — Confluence REST 응답을 SendMessage payload 에 넣기 전 token literal / 민감 content 제거.
- **api_token literal 금지 (env indirect only)** — token 은 env 경유만 (§결정 3 `*_env` reference 정합), agent transcript / SendMessage / log 에 literal 등장 0건.

#### SSRF / 응답 변조 surface (SecurityArch §7.5)

- **Confluence REST = outbound-only + read 우선** — Confluence → wrapper inbound webhook 없음 (outbound-only). write 는 ADR-103 (sync mechanism) **단일 진입점** 만 (Layer 1 narrow allow 대상 = ADR-103 sync agent, W4 defer).
- **`mcp__atlassian__*` endpoint = SSRF (내부 자원 도달) + 응답 변조 (Confluence 응답이 wrapper governance state 오염) surface**. boundary 검증 책임 = **ADR-101 ground-truth verify** (Confluence 응답을 신뢰 전 git-side ground truth 와 cross-check, ADR-070 verify-before-trust 외부 worker output 정합). ADR-101 = 본 commit 시점 reserved (S3 carrier, 미작성).
- **Layer 1 permission deny = SSRF 1차 방벽** (§결정 4) — 무단 endpoint 호출 자체 차단. ADR-101 = 정식 채널 응답의 무결성 보장 (2차 layer).

#### boundary completeness (I-1 / I-2)

- **I-1 (token schema env-ref only)** — §결정 3 atlassian.* token field 가 `*_env` reference 만 허용 (평문 금지). schema 의 secret field semantic 명시 = API contract semantic completeness.
- **I-2 (cross-module propagation)** — Layer 1 (본 ADR-100 §결정 4 deny baseline) → ADR-101 (Confluence REST ground-truth verify) → ADR-103 (sync agent narrow allow + scope 분리) 의 trust boundary propagation 명시. 각 layer 의 owner / 책임 / reserved 상태를 cross-ref 표기.

본 §결정 5 는 ADR-100 이 boundary 를 enforce 하는 것이 아니라 (ADR-101/103 owner) **boundary 존재 + Layer 1 deny 가 1차 방벽임을 명시 cross-ref** 한다.

## 결과

### 긍정

- A-2 (SoR-docs = wrapper governance docs Confluence authoritative) governance SSOT 확립 — Confluence 가 wrapper governance docs 의 authoritative readable source 로 인정됨.
- ADR-013 §결정 1 의미 약화 0건 — partial extend (git SoR-work KEEP 보존 + Confluence SoR-docs readable layer 추가) 의 disjoint axis 명시로 dogfood-out 정책 무손상.
- ADR-041 double-amendment 회피 — confluence variant / authoritative_source field intent declare-only, 실 yaml 변경은 sync mechanism 결정 (ADR-103) 후 single change.
- security 강화 방향 — Layer 1 settings.json deny baseline (§결정 4) + token-env-reference schema (§결정 3) = 무단 MCP 호출 차단 + token 평문 노출 0건 (순수 강화, 약화 아님).
- consumer adoption natural extend — atlassian.* schema 가 ADR-027 bootstrap validation 자동 cover (ADR-027 amendment 불요, 충돌 0).

### 부정 / trade-off

- **deny + narrow-allow mechanically 충돌 risk (SecurityArch P1 CRITICAL)** — Claude Code deny precedence (first-match-wins) 로 서버-전체 deny + narrow allow 동시 설정 = narrow allow 무효. 완화 = narrow allow W4 defer (§결정 4) + W4 wire 시 scope 분리 / managed-only 메커니즘 (deny 우회 방법 empirical verify = ADR-103 owner). 본 trade-off 를 명시 고정하지 않으면 W4 에서 narrow allow 가 silent 무효화될 risk.
- agent-teams SendMessage secret leak surface (SecurityArch P1) — `AGENT_TEAMS=1` 활성 하 sync agent Confluence 응답이 sibling 에 전파 시 token / content 누설. 완화 = sync agent output sanitization + api_token literal 금지 (env indirect only) — W4 / ADR-103 위임.
- Confluence authoritative ↔ git desync risk — git 변경이 Confluence 에 sync 되기 전 window 동안 Confluence readable 이 stale. 완화 = sync 방향 git → Confluence (변경은 git source) + ADR-101 ground-truth verify (Confluence 응답을 git 과 cross-check). 단 sync 빈도 / staleness window = ADR-103 owner (sync mechanism).
- ADR-041 yaml 변경 defer 의 인지 부하 — confluence variant intent 만 declare, 실 path 미정 (ADR-103 까지). 완화 = §결정 2 의 명시적 defer 근거 (double-amendment 회피) + schema_version 1.0→1.1 MINOR 예고.
- forward cross-ref (ADR-101/103) reserved — 두 ADR 미작성 상태에서 본 ADR 이 그들에 책임 위임. 완화 = §컨텍스트 forward cross-ref reserved 명시 (미존재 anchor 단언 금지, ADR-082) + ADR-RESERVATION row 101/103 status `reserved` verified.
- mechanical_enforcement_actions `[]` Wave 1 declaration-only — §결정 3 schema validator + §결정 4 settings.json deny baseline 실 wire = Phase 2 (S2/S3 carrier). pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier (ADR-082 §결정 6 retain pattern).

## 해소 기준

N/A — permanent policy (is_transitional: false). Confluence doc SSOT 인정 (git SoR-work ↔ Confluence SoR-docs disjoint axis) 은 Atlassian 재결합 후 영구 정책 방향. §결정 4 Layer 1 settings.json deny baseline + §결정 3 token-env-reference schema = 순수 security 강화 (약화 아님) → 약화 정당화 불요.

**약화 정당화 layer 분리 (ADR-099 §결정 4-A 정합)**: 본 ADR 의 Layer 1 (security: deny baseline + token-env-reference) + 데이터 흐름 (Confluence readable source 추가) 영역은 **약화 정당화 불요** (순수 강화 + additive). ADR-013 §결정 1 KEEP/MOVE 의미 약화 0건 (partial extend = KEEP 목록 보존). S4 ADR-102 sunset_justification (ratchet 약화 정당화) 는 **Layer 2 lint (Atlassian-allow grep allowlist) 영역 한정** (ADR-099 §결정 4-A) — 본 ADR-100 의 Layer 1 / 데이터 흐름 영역은 ADR-102 약화 정당화 경로 비대상.

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: Layer 1 deny baseline 강화 / token secret 강제 강화 / Confluence ground-truth verify 강화). 약화 방향 (예: Layer 1 mcp__atlassian deny 제거 / token 평문 mount 허용 / git SoR-work → Confluence SoR-work 역전) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 인접 (token secret + SSRF / 응답 변조 boundary = security guard). 단 category = governance (Confluence doc SSOT 인정 거버넌스 결정 본체) — security 차단 패턴은 Layer 1 permission carrier + §결정 5 trust boundary 로 보존.

## 관련 파일

- `docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md` — §결정 1 partial extend 대상 (KEEP 영역 Confluence authoritative sync 추가, 1줄 cross-ref Amendment declare)
- `docs/adr/ADR-041-doc-location-registry.md` — confluence variant / authoritative_source field intent declare (실 변경 = ADR-103 defer, schema_version 1.0→1.1 MINOR 예고, 1줄 cross-ref Amendment declare)
- `docs/adr/ADR-027-consumer-adoption-protocol.md` — atlassian.* schema natural extend (충돌 0, bootstrap validation 자동 cover)
- `docs/adr/ADR-099-atlassian-allow-redefinition.md` — Wave 1 Story-1 sister (Layer 1 permission deny / Layer 2 lint allowlist 2-layer SSOT). 본 ADR 평문 Confluence 참조 = ADR-099 §결정 2 Layer 2 allowlist 영역
- `docs/adr/ADR-101-verify-before-trust-confluence-rest.md` — §결정 5 Confluence REST 응답 변조 / SSRF boundary ground-truth verify owner (**reserved — S3 carrier, 본 commit 시점 미작성**)
- `docs/adr/ADR-103-git-confluence-sync-mechanism.md` — narrow allow wire / sync agent / doc-locations.yaml confluence path 실 결정 owner (**reserved — W4 carrier, 본 commit 시점 미작성**)
- `docs/project-config-schema.md` — §결정 3 atlassian.* schema 신설 (token = `*_env` reference, deploy 1password env-key precedent 정합, 실 wire = Phase 2)
- `.claude/settings.json` — §결정 4 Layer 1 `permissions.deny: ["mcp__atlassian", "mcp__atlassian__*"]` baseline SSOT (실 wire = Phase 2 S2/S3 carrier) + agent preset atlassian tool 미포함 (자연 deny)
- `docs/doc-locations.yaml` — §결정 2 confluence variant / authoritative_source field intent declare (실 변경 = ADR-103 defer)
- `docs/adr/ADR-RESERVATION.md` — row 100 reserved → active 전환
