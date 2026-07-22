---
adr_number: 111
title: Confluence-mirror classification policy SSOT — design doc 4-mirror + Issue-only retain 5-exempt closed-enum
status: Accepted
category: governance
date: 2026-05-24
carrier_story: CFP-1419
parent_epic: CFP-1415
supersedes: null
amends: null
amendments: [1, 2]
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-1618
    date: 2026-05-25  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1"]
    nature: ratchet-up  # closed-enum 4 → 5 영역 확장 (ADR-058 §결정 5 강화 방향 sunset_justification 면제)
    sunset_justification: null  # ratchet-up — closed-enum 인정 범위 확장 (forbid scope 축소 0, ADR-013 §결정 1 KEEP 의미 보존 + ADR-100 §결정 1 partial extend 의미 보존). ADR-058 §결정 5 ratchet 강화 방향 면제 정합. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 (강화 = pattern_count evidence — CFP-1584 Phase 1 audit 결과 4 영역 외 Playbook 영역 발견, 분류 부재 시 sibling Story 마다 재논의 비용 발생)
    note: "§결정 1 closed-enum 4 → 5 영역 추가 (5번째 영역 = orchestrator-runbook, `docs/orchestrator-playbook.md` SSOT). Origin = CFP-1584 Phase 1 audit (PR #1608 merged 2026-05-25 11:08:46Z) — Sub-A (CFP-1524 Sub-A) Confluence push 진입 시 4 영역 (ADR / Living Architecture / Change Plan / Domain Knowledge) 외 Playbook 영역 발견, ADR-111 classification 적용 불가. 5번째 영역 정의 = `docs/orchestrator-playbook.md` (Orchestrator 의 세션 생명주기 + 스폰 시퀀스 + Preflight 체크 + FIX 루프 + 세션 재개 + 트러블슈팅 + cross-agent write coordination + context packet + observability boundary + post-merge automation + sibling sync 절차 등 운영 절차 SSOT). git 위치 = `docs/orchestrator-playbook.md` (wrapper repo). sync source repo = wrapper repo (plugin). sync direction = 단방향 git → Confluence (4 mirror 영역 정합). **scope boundary (derived default)**: orchestrator-playbook 영역 한정 — 일반 runbook 영역 (예: deployment runbook / oncall runbook / production incident runbook 등) **포함 안 함**. 확장 시 별 CFP carrier 의무 (open_extension: false). Amendment 1 = ratchet 강화 방향 (closed-enum 확장 + 인정 범위 명시화), ADR-058 §결정 5 sunset_justification 면제. §결정 3 IA axis = orchestrator-playbook 영역 = cross-cutting sibling 또는 per-plugin top-level (wrapper) sub-page 양 IA axis 모두 허용 (현 시점 flat 3-parent hierarchy CFP-1146 W5 cutover transitional 정합). 정식 재구조화는 Sub-B carrier (별 Story 영역, 본 Amendment scope 외). §결정 4 diagram strategy + §결정 5 cross-link discipline 적용 영역 = 5번째 영역에도 동일 적용 (의미 변경 0, 적용 영역 확장 만 — §결정 3/4/5 본문 무수정 invariant 보존). docs/confluence-ia-tree.yaml `playbook_pages_adr_111_classification` block 동반 명시 (mapping declaration, source-of-truth = ADR-111 §결정 1 5번째 row). collision-rebase ratchet: amendment_log 직전 origin max amendment_id 재확인 = 0 (baseline `amendment_log: []`) → 1. amendments_reserved[] pre-claim 면제 (단일 session 영역, parallel race 0 verified). META-self-applied 0 (closed-enum 확장 carrier, ADR-082 §결정 9 verify-before-cite 영역 외)."
  - amendment_id: 2
    carrier_story: CFP-1668
    date: 2026-05-26  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1", "§결정 2"]
    nature: ratchet-up  # consumer scope binding 명시화 — SYMMETRIC subset (consumer ⊆ wrapper, 확장 0 invariant) + Issue-only retain consumer scope 동일 적용 (forbid scope 축소 0)
    sunset_justification: null  # ratchet-up — consumer scope binding 명시화 (forbid scope 축소 0, wrapper invariant 보존). ADR-058 §결정 5 ratchet 강화 방향 면제 정합. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 (강화 = pattern_count evidence — Wave 1 wrapper-canonical Confluence migration codify, consumer-facing operability 부재로 mctrader `unknown` 분류 영역 super-class incident 발생)
    note: "Wave 1 wrapper-canonical Confluence migration codify (CFP-1668) — consumer-facing operability 신설 carrier. §결정 1 closed-enum 5 mirror 대상 의 consumer scope binding 명시화 — consumer 측 mirror 대상 = wrapper closed-enum 5 의 **SYMMETRIC subset** (consumer ⊆ wrapper closed-enum 5, 확장 0 invariant 보존). 사용자 Q-1 답 verbatim = SYMMETRIC subset 확정 (2026-05-26 KST). §결정 2 Issue-only retain consumer scope 동일 적용 명시 — Story file / FIX Ledger / Lane Evidence / decision packet / spawn prompt 5 영역 consumer 측 도 Confluence mirror 금지. 사용자 Q-2 답 verbatim = YES 동일 적용 확정 (2026-05-26 KST, ratchet 강화 명시). consumer overlay project.yaml 의 `atlassian.confluence.issue_only_retain_targets` field 신설은 불필요 (§결정 2 inline binding sufficient). collision-rebase ratchet: amendment_log 직전 origin max amendment_id 재확인 = 1 (Amendment 1 / CFP-1618 merged 2026-05-25 KST) → 2. amendments_reserved[] pre-claim = ADR-RESERVATION row 416-421 active (commit 77e378e4, sub-scope 1-G META 12th applied). carrier_story CFP-1668 verified-via `git show origin/main:docs/adr/ADR-RESERVATION.md` row append. META-self-applied (ADR-082 §결정 1 sub-scope 1-G 12th applied case + sub-scope 1-E PRE-SPAWN-ORIGIN-MAIN-SHA pin verified `89c8721d179182a60ef8bb8b4b8806cc01bf78ba`). enum_closure annotation (ADR-068 I-2 cross-module propagation completeness) = consumer mirror_targets[] ⊆ wrapper closed-enum 5 invariant verify. ADR-100 Amendment 2 paired sibling (동일 CFP-1668 Phase 1 PR scope, 본 carrier 와 axis disjoint — ADR-100 §결정 1/3 wrapper-consumer binding ↔ 본 ADR-111 §결정 1/2 closed-enum subset binding)."
related_stories:
  - CFP-1419     # 본 carrier (Mega-Epic CFP-1415 Sub-A S1.1)
  - CFP-1415     # umbrella Mega-Epic (Confluence-as-derived-mirror governance standardization)
  - CFP-1417     # sub-Epic (Sub-A bundle)
  - CFP-1618     # Amendment 1 carrier — §결정 1 closed-enum 4 → 5 영역 확장 (5번째 = orchestrator-runbook, origin CFP-1584 Phase 1 audit)
  - CFP-1584     # Amendment 1 origin — Sub-A Phase 1 audit 결과 4 영역 외 Playbook 영역 발견 (PR #1608 merged 2026-05-25 11:08:46Z)
  - CFP-1524     # parent Epic (Sub-B S2.4 real backfill umbrella)
related_adrs:
  - ADR-100      # Confluence doc SSOT 인정 — §결정 1 "wrapper git-commit governance docs" phrasing 의 enumeration carrier. 본 ADR-111 = ADR-100 §결정 1 위에 closed-enum 4 대상 (ADR / Living Architecture / Change Plan / Domain Knowledge) 정식 codify. ADR-100 Amendment 1 동반 발의 (본 PR scope).
  - ADR-099      # Atlassian-allow redefinition — §결정 1 2-layer (Layer 1 permission deny / Layer 2 lint allowlist). 본 ADR-111 평문 Confluence 참조 = ADR-099 §결정 2 Layer 2 allowlist 영역 (governance docs 평문 인용 허용 carrier).
  - ADR-103      # git↔Confluence sync mechanism — sync direction (단방향 git→Confluence) + write boundary (sync agent 단일 진입점). 본 ADR-111 §결정 1 mirror 대상 sync 책임 owner.
  - ADR-013      # codeforge family dogfood-out — §결정 1 KEEP/MOVE. 본 ADR-111 §결정 2 Issue-only retain 영역 = ADR-013 §결정 1 KEEP 영역 정합 (Story file / FIX Ledger / Lane Evidence = git Issue body bidirectional binding, Confluence mirror 금지).
  - ADR-041      # doc location registry — §결정 6 Trigger #1/#2. 본 ADR-111 §결정 1 closed-enum 4 대상 = ADR-041 doc_types 4 entry (adr / architecture_doc / change_plan / domain_knowledge) 위치 SSOT 정합. confluence variant / authoritative_source field intent = ADR-103 carrier (declare-only).
  - ADR-068      # boundary completeness invariants — I-4 wording SSOT chief tie-break ladder Amendment 2. 본 ADR-111 §결정 3 IA axis / §결정 5 cross-link discipline 어휘 single SSOT 정합.
  - ADR-064      # decision principle mandate — §결정 7 evidence-gated symmetric ratchet (Amendment 8). 본 ADR-111 신설 = ratchet 강화 방향 (closed-enum codify + cross-link discipline 의무).
  - ADR-058      # ADR sunset criteria mandate — §결정 5 ratchet 강화 방향 sunset_justification 면제. 본 ADR-111 is_transitional: false permanent governance ratchet 정합.
  - ADR-078      # living architecture doc SSOT — per-plugin self-owned `docs/architecture/`. 본 ADR-111 §결정 1 closed-enum 2번째 대상 (Living Architecture page) carrier.
  - ADR-082      # write-time self-write verification mandate — §결정 1 layer 1-C USER-UTTERANCE-VERBATIM block (spawn prompt). 본 ADR-111 §결정 2 5번째 면제 (spawn prompt) anchor.
related_files:
  - docs/adr/                                                                     # §결정 1 closed-enum 1번째 대상 (ADR)
  - docs/architecture/                                                            # §결정 1 closed-enum 2번째 대상 (Living Architecture page, ADR-078 carrier)
  - docs/change-plans/                                                            # §결정 1 closed-enum 3번째 대상 (Change Plan)
  - docs/domain-knowledge/                                                        # §결정 1 closed-enum 4번째 대상 (Domain Knowledge)
  - docs/orchestrator-playbook.md                                                 # §결정 1 closed-enum 5번째 대상 (Orchestrator Playbook, Amendment 1 CFP-1618 carrier — orchestrator-runbook scope boundary 한정)
  - docs/confluence-ia-tree.yaml                                                  # §결정 1 5번째 대상 split mapping SSOT (playbook_split_pages[] + playbook_pages_adr_111_classification declaration block, Amendment 1 CFP-1618 동반 갱신)
  - docs/adr/ADR-100-confluence-doc-ssot-recognition.md                           # ADR-100 Amendment 1 동반 발의 — design doc Confluence-mirror 인정 범위 확장 (closed-enum 4 대상 명시화)
  - docs/adr/ADR-RESERVATION.md                                                   # row 111 reserved → active 전환
mechanical_enforcement_actions:
  - issue-design-content-confluence-link    # §결정 5 cross-link discipline lint — Issue body design content 참조 시 Confluence anchor + git anchor 양쪽 link 의무 grep-presence (warning-tier deferred-followup Wave 1). 실 wire = Sub-A S1.3 / CFP-1421 carrier (templates/github-workflows/issue-design-content-confluence-link.yml). ADR-082 §결정 6 retain pattern 답습 (Wave 1 declare / Wave 2 wire). pattern_count >= 2 재발 시 follow-up CFP MUST promote
is_transitional: false   # permanent governance ratchet — Confluence-mirror classification policy (design doc 4-mirror + Issue-only retain 5-exempt) 는 Atlassian 재결합 후 영구 분류 mechanism layer. closed-enum 도입 = 강화 방향 (인정 범위 명시화 + Issue-only retain 면제 명시화). 약화 0건 (ADR-013 §결정 1 KEEP 의미 보존 + ADR-100 §결정 1 partial extend 의미 보존)
sunset_justification: null   # is_transitional false — closed-enum 4 mirror 대상 codify + closed-enum 5 Issue-only retain 면제 codify = 영구 분류 정책 + 강화 방향 (forbid scope 축소 0건). ADR-058 §결정 5 ratchet 강화 방향 sunset_justification 면제. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 (강화 = pattern_count evidence — Confluence-as-derived-mirror governance standardization 영역 closed-enum 부재로 모호성 6+ window evidence)
---

# ADR-111 — Confluence-mirror classification policy SSOT (design doc 4-mirror + Issue-only retain 5-exempt closed-enum)

## 상태

`Accepted` (2026-05-24 KST) — CFP-1419 carrier (Mega-Epic CFP-1415 Sub-A S1.1). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved` 미경유 직접 `active` 전환 (ADR-099/100/101/102/103/104/105/106/107/108/109/110 row precedent 정합 — chief author scope). dogfood-out (ADR-013): change-plan 은 wrapper repo 에 commit 안 함, ADR 만 wrapper commit.

## 컨텍스트

### 동인

Mega-Epic CFP-1415 (Confluence-as-derived-mirror governance standardization) Phase 1 brainstorming 10 declare + 1 사용자 확정 결과의 normative codify. ADR-100 §결정 1 가 Confluence authoritative readable 대상을 "wrapper git-commit governance docs" 단일 phrasing 으로 인정했으나, 실 운영 영역에서 **design doc 4 대상 vs Issue-only retain 5 면제** 의 closed-enum 분류 부재로 모호성 누적 (6+ window evidence — Story file / FIX Ledger / Lane Evidence 영역의 Confluence mirror 적용 여부 sibling Story 마다 재논의 발생). 본 ADR-111 = 그 closed-enum 분류 mechanism layer 의 SSOT codify.

### 핵심 긴장

ADR-100 §결정 1 "wrapper git-commit governance docs" = enumeration 미codify → 후속 sibling Story 마다 (a) design doc 인가 (b) Issue-only retain 영역인가 재판정 비용 발생. 본 ADR-111 = 분류 mechanism 을 closed-enum 으로 박제 (정책 결정 분기 0 invariant). 핵심 = git SoR-work invariant (ADR-013 §결정 1 KEEP) + Confluence SoR-docs readable layer 추가 (ADR-100 §결정 1 partial extend) 의 disjoint axis 보존 위에 분류 mechanism layer 만 신설.

### Sub-A S1.1 위치 (Mega-Epic CFP-1415)

본 ADR-111 = Sub-A bundle (CFP-1417) S1.1 — Confluence-mirror classification policy SSOT 영역. sibling S1.2 = ADR-100 Amendment 1 동반 발의 (본 PR scope). sibling S1.3 = mechanical enforcement wire (`issue-design-content-confluence-link.yml` workflow + lint, CFP-1421 carrier). S1.4 = CLAUDE.md cross-ref (별 Story 영역, 본 PR scope 외).

### ADR 번호 race resolution (verify-before-trust catch)

#1419 body 의 "ADR-107 신설" claim = stale (CFP-1317 이미 ADR-107 "Plugin declarative seed drift detection" 점유, status active 2026-05-24 KST). race 후 next available = ADR-111 (ADR-RESERVATION.md row 100~110 점유 verified via `git show origin/main:docs/adr/ADR-RESERVATION.md` direct fetch). #1419 body 의 모든 "ADR-107" reference = 본 PR 에서 "ADR-111" 로 translate. Issue body cleanup (EPIC #1415 + sub-Epic #1417 + Story #1419 body updates) = post-merge follow-up scope (본 PR scope 외).

## 결정

### §결정 1 — Confluence mirror authoritative 대상 closed-enum 5 (design doc 영역, Amendment 1 후)

design doc 영역 의 Confluence mirror authoritative readable 대상을 다음 5 대상 closed-enum 으로 박제한다 (open_extension: false, 확장 시 별도 CFP carrier 의무). **5번째 영역 (orchestrator-runbook) = Amendment 1 (CFP-1618) 확장** — origin CFP-1584 Phase 1 audit 결과 4 영역 외 Playbook 영역 발견 carrier:

| # | 대상 | git 위치 | sync source repo | carrier ADR | sync direction |
|---|---|---|---|---|---|
| 1 | **ADR** | `docs/adr/` | wrapper repo (plugin) | ADR-100 §결정 1 + 본 ADR-111 §결정 1 | 단방향 git → Confluence |
| 2 | **Living Architecture page** | per-plugin `docs/architecture/` (9 plugin family — wrapper + 8 lane) | wrapper repo + 6 lane plugin repo (CFP-949 Sub-Epic 6 lane plugin self-owned architecture doc seed) | ADR-078 (living architecture doc SSOT) | 단방향 git → Confluence |
| 3 | **Change Plan** | `docs/change-plans/` (dogfood = internal-docs repo) | mclayer/codeforge-internal-docs (dogfood-out) + consumer repo (single_repo) | ADR-103 (sync mechanism — sync source repo 개별) | 단방향 git → Confluence |
| 4 | **Domain Knowledge** | `docs/domain-knowledge/` | wrapper repo (plugin) | ADR-100 §결정 1 (wrapper git-commit governance docs 영역) | 단방향 git → Confluence |
| 5 | **Orchestrator Playbook** (orchestrator-runbook) | `docs/orchestrator-playbook.md` | wrapper repo (plugin) | ADR-111 §결정 1 Amendment 1 (CFP-1618) | 단방향 git → Confluence |

**모든 sync direction = 단방향 git → Confluence** (ADR-100 §결정 1 disjoint axis 정합 — git = SoR-work / Confluence = SoR-docs readable mirror). write boundary = ADR-103 sync agent 단일 진입점 (Confluence → wrapper inbound webhook 0).

**Living Architecture page sync source repo 다중성 (CFP-949 정합)**: per-plugin self-owned `docs/architecture/` 는 wrapper + 6 lane plugin repo 가 각각 SSOT (CFP-949 Sub-Epic 6 lane plugin self-owned architecture doc seed merged). sync source repo = wrapper repo (wrapper architecture) + codeforge-{requirements, design, develop, review, test, pmo} repo (lane plugin architecture). ADR-103 sync mechanism = 2-repo source resolver (wrapper governance docs + internal-docs dogfood) precedent 답습.

**Change Plan sync source repo dogfood/consumer 분기**: dogfood (wrapper plugin family) = internal-docs repo SSOT (ADR-013 §결정 1 MOVE 영역). consumer = consumer repo (single_repo) SSOT. sync source = repo 별로 결정 (ADR-103 carrier).

**Orchestrator Playbook scope boundary (5번째 영역, Amendment 1 — CFP-1618)**: 5번째 영역 = `docs/orchestrator-playbook.md` (Orchestrator 의 세션 생명주기 + 스폰 시퀀스 + Preflight 체크 + FIX 루프 + 세션 재개 + 트러블슈팅 + cross-agent write coordination + context packet + observability boundary + post-merge automation + sibling sync 절차 등 운영 절차 SSOT). **scope boundary (derived default)**: orchestrator-playbook 영역 한정 — 일반 runbook 영역 (예: deployment runbook / oncall runbook / production incident runbook / disaster recovery runbook 등) **포함 안 함**. 확장 시 별도 CFP carrier 의무 (open_extension: false). split granularity = §-level page split (CFP-1524 Sub-A CFP-1584 carrier, 17 § + 부록 A+B 통합 = 19 entry skeleton + CRITICAL Step 0 §.N-level 추가 분할 carrier 별도 follow-up CFP). split mapping SSOT = `docs/confluence-ia-tree.yaml` `playbook_split_pages[]` array + `playbook_pages_adr_111_classification` declaration block. §결정 3 IA axis 적용 영역: orchestrator-playbook = cross-cutting sibling 영역 (현 시점 flat 3-parent hierarchy CFP-1146 W5 cutover transitional, 정식 재구조화 Sub-B carrier defer). §결정 4 diagram strategy + §결정 5 cross-link discipline 동일 적용 (5번째 영역에도 diagram-as-code 의무 + git anchor + Confluence anchor 양쪽 link 의무 — §결정 3/4/5 본문 무수정 invariant 보존, 적용 영역 확장 만).

#### consumer scope binding — SYMMETRIC subset (Amendment 2 — CFP-1668 Wave 1)

본 ADR §결정 1 closed-enum 5 (Amendment 1 후) 의 **consumer scope binding** 명시화 — consumer 측 mirror 대상 = wrapper closed-enum 5 의 **SYMMETRIC subset** (consumer ⊆ wrapper, 확장 0 invariant). 사용자 Q-1 답 verbatim = SYMMETRIC subset 확정 (CFP-1668, 2026-05-26 KST).

| consumer scope | 의미 | invariant |
|---|---|---|
| **subset 선택 mechanism** | consumer 가 자기 `atlassian.confluence.mirror_targets[]` field 안 wrapper closed-enum 5 중 일부 또는 전체 entry 선택 (예: `[adr]` / `[adr, change_plan]` / `[adr, architecture_doc, change_plan, domain_knowledge, orchestrator_playbook]` 모두) | enum_closure 검증 — 각 entry ∈ {adr, architecture_doc, change_plan, domain_knowledge, orchestrator_playbook}. wrapper 외 신규 type 추가 금지 (open_extension: false) |
| **per-consumer space 결정** | consumer 가 자기 Confluence space (예: mctrader = `MCT`, 미래 consumer = 자기 결정) 의 root parent page 를 `atlassian.confluence.homepage_id` 로 명시 — per-consumer 영역, wrapper space (예: `CFP`) 와 disjoint | wrapper space namespace 침범 0건. consumer 자기 space ownership |
| **sync source repo** | consumer repo (자기 git source) — 단방향 git→Confluence (ADR-100 §결정 1 disjoint axis 정합) | sync direction immutable |
| **mirror_targets[] enum 확장** | 별도 CFP 의무 (wrapper closed-enum 5 본문 변경 = 별도 ADR-111 Amendment carrier — 본 Amendment 1 / Amendment 2 의 precedent) | open_extension: false (Q-1 SYMMETRIC subset 확정) |

**ADR-068 I-2 cross-module propagation completeness — enum_closure annotation 의무**:

consumer scope binding 의 5 entry enum (`adr` / `architecture_doc` / `change_plan` / `domain_knowledge` / `orchestrator_playbook`) = wrapper SSOT 와 **enum_closure** (parallel_anchors_checked annotation per review-verdict-v4 v4.9 `findings[].parallel_anchors_checked[]`). consumer schema field `confluence.mirror_targets[]` validation 시 wrapper closed-enum 5 의 enum_closure 검증 의무 (Phase 2 bootstrap validation carrier).

**ratchet 영향**: ratchet 강화 only — (a) closed-enum 5 invariant 보존 (forbid scope 축소 0) (b) consumer scope binding 명시화 = security boundary 확장 (consumer 측 mirror 대상 enum 검증 mechanism 신설 영역) ≠ 약화. open_extension: false invariant 보존.

**implementation defer** — 실 consumer schema row append + enum_closure validation lint = Phase 2 carrier (`docs/project-config-schema.md` block extension + Wave 2 bootstrap validation wire). 본 Amendment 2 = declarative anchor only (ADR-082 §결정 6 retain pattern 답습 — Wave 1 declare / Wave 2 wire).

### §결정 2 — Issue-only retain closed-enum 5 (Confluence mirror 금지 면제 영역)

다음 5 영역은 git/Issue 양 채널 유지 + **Confluence mirror 금지** (closed-enum, open_extension: false):

| # | 영역 | 보관 채널 | 금지 근거 |
|---|---|---|---|
| 1 | **Story file** (§1-§14) | git (codeforge-internal-docs SSOT — ADR-013 §결정 1 MOVE) + Issue body (bidirectional binding) | Issue body bidirectional binding 영역 — 양 채널 sync 가 codeforge governance 의 1차 mechanism (Issue label / phase / fix:* mirror). Confluence 3-way mirror 는 sync invariant 복잡도 폭발 (ADR-013 §결정 1 dogfood-out invariant 위반 risk) |
| 2 | **FIX Ledger §10** | git Story file §10 + Issue label mirror (fix-ledger-sync.yml) | fix-event-v1 v1.3 contract — Orchestrator 단독 §10 append 독점 (CFP-32). Issue label 가 보조 channel. Confluence mirror 추가 시 3-way sync invariant collapse (Orchestrator monopoly 영역 침범) |
| 3 | **Lane Evidence §14** | git Story file §14 + Issue body table (Story-scoped) | ADR-031 lane spawn evidence carrier — Story 종료 시 archived. Confluence mirror 는 Story-scoped temporary 영역 인지 부하 증가 (long-tail governance 영역 아님) |
| 4 | **Decision Packet** | Lane PL synthesis verdict (review-verdict-v4 / requirements-output-v1 / design-output-v1 / develop-output-v1 etc.) ephemeral | Lane PL synthesis ephemeral output — Story §9 verdict block 영구화 영역만 git 보존 + 그 외 packet 본문은 lane spawn 종료 시 소멸. Confluence mirror = ephemeral artifact 영역 침범 |
| 5 | **spawn prompt** | subagent ephemeral (Orchestrator dispatch context) | ADR-082 §결정 1 layer 1-C USER-UTTERANCE-VERBATIM block carrier — spawn prompt 첫 줄 verbatim anchor 영역, ephemeral subagent context. Confluence mirror = subagent ephemeral 영역 침범 + USER-UTTERANCE 평문 secret leak surface 신설 risk (ADR-082 §결정 1 layer 1-C 정합) |

**근거 정합 ADR**: (1) Story file = ADR-013 §결정 1 dogfood-out invariant + ADR-031 Story SSOT + Issue body bidirectional binding (codeforge native mechanism). (2) FIX Ledger = fix-event-v1 v1.3 contract Orchestrator monopoly (CFP-32). (3) Lane Evidence = ADR-031 Story-scoped temporary. (4) Decision Packet = lane plugin output ephemeral (review-verdict-v4 verdict block 만 git 영구). (5) spawn prompt = ADR-082 §결정 1 layer 1-C USER-UTTERANCE-VERBATIM block ephemeral.

**ADR-013 §결정 1 KEEP 영역 정합**: 5 면제 영역 모두 ADR-013 §결정 1 KEEP 영역 (plugin repo 잔류 runtime SSOT 또는 ephemeral subagent context) — Confluence SoR-docs readable layer 추가 영역이 아니다. 본 §결정 2 = ADR-013 §결정 1 KEEP 의미 약화 0건 invariant 강화 (mirror 금지 명시화).

#### consumer scope 동일 적용 (Amendment 2 — CFP-1668 Wave 1)

본 §결정 2 의 closed-enum 5 Issue-only retain 영역 = **consumer 측에도 동일 적용** (mirror 금지 invariant ratchet 강화). 사용자 Q-2 답 verbatim = YES 동일 적용 확정 (CFP-1668, 2026-05-26 KST).

| 영역 (wrapper-self) | consumer scope 동일 적용 | 의미 |
|---|---|---|
| **Story file** (§1-§14) | consumer repo Story file (consumer 자기 internal-docs 또는 consumer repo 안 stories/) Confluence mirror 금지 | consumer 측 도 Issue body bidirectional binding 영역 = 양 채널 sync 가 governance 1차 mechanism. Confluence 3-way mirror 는 sync invariant 복잡도 폭발 |
| **FIX Ledger §10** | consumer Story file §10 Confluence mirror 금지 | fix-event-v1 v1.3 contract — Orchestrator 단독 §10 append 독점 (CFP-32). consumer 측 도 동일 monopoly 영역 |
| **Lane Evidence §14** | consumer Story file §14 Confluence mirror 금지 | ADR-031 lane spawn evidence carrier — Story-scoped temporary 영역, consumer 측 도 동일 |
| **Decision Packet** | consumer lane PL synthesis ephemeral output Confluence mirror 금지 | Lane PL synthesis ephemeral — consumer 측 lane plugin 출력도 동일 ephemeral 영역 |
| **spawn prompt** | consumer subagent ephemeral context Confluence mirror 금지 | ADR-082 §결정 1 layer 1-C USER-UTTERANCE-VERBATIM block carrier — consumer 측 도 동일 ephemeral + 평문 secret leak surface 차단 영역 |

**consumer overlay schema field 신설 0** — consumer 측 mirror 금지 invariant 는 **§결정 2 inline binding sufficient** (consumer overlay project.yaml 안 `atlassian.confluence.issue_only_retain_targets` field 신설은 불필요). consumer 측 sync agent (ADR-103 carrier) 가 본 §결정 2 enum 5 영역을 mirror 대상 enum 에서 자동 제외 의무 (구현 영역).

**근거 정합 ADR (consumer scope 동일 적용)**:

1. **Story file** = ADR-013 §결정 1 KEEP 영역 (consumer repo Story file 도 consumer SSOT) + ADR-031 Story SSOT + Issue body bidirectional binding (codeforge native mechanism, consumer 측 도 동일)
2. **FIX Ledger** = fix-event-v1 v1.3 Orchestrator monopoly (CFP-32 — consumer 측 도 동일 monopoly)
3. **Lane Evidence** = ADR-031 Story-scoped temporary (consumer 측 도 동일)
4. **Decision Packet** = lane plugin output ephemeral (consumer 측 도 동일 ephemeral)
5. **spawn prompt** = ADR-082 §결정 1 layer 1-C USER-UTTERANCE-VERBATIM block ephemeral (consumer 측 도 동일)

**ratchet 영향**: ratchet 강화 only — (a) consumer scope 동일 적용 명시화 = mirror 금지 영역 확장 (forbid scope 확장 = 강화) (b) ADR-013 §결정 1 KEEP 의미 약화 0건 (consumer repo SSOT ownership 보존). open_extension: false invariant 보존.

### §결정 3 — Confluence IA (Information Architecture) axis

Confluence 측 page hierarchy IA axis 를 다음 2-axis 로 정의한다:

| axis | 영역 | 예시 |
|---|---|---|
| **per-plugin top-level** | 9 plugin family (wrapper + 8 lane plugin) 의 각 root page | `codeforge (wrapper)` / `codeforge-requirements` / `codeforge-design` / ... / `codeforge-deploy-review` |
| **cross-cutting sibling** | wrapper governance / inter-plugin contracts / Orchestrator playbook 등 plugin-spanning 영역 | `Inter-plugin Contracts` / `Orchestrator Playbook` / `ADR (cross-cutting)` |

**현 시점 flat 3-parent hierarchy (CFP-1146 W5 cutover)** = transitional. 본 ADR-111 가 IA axis 를 codify 한 후 정식 재구조화는 Sub-B carrier (deferred — 별 Story 영역, 본 PR scope 외).

**원칙**: per-plugin top-level 우선 (cross-cutting sibling 은 inter-plugin contract 영역 또는 wrapper-level governance 한정). 모든 design doc closed-enum 4 대상 (§결정 1) = per-plugin top-level 안 sub-page 로 배치 (예: ADR-100 → `codeforge (wrapper) / ADR / ADR-100`).

### §결정 4 — Diagram strategy: diagram-as-code (Mermaid / PlantUML)

design doc 안 diagram = **diagram-as-code (Mermaid / PlantUML) 우선**. Confluence native macro (drawio / Gliffy / Lucidchart embed) **회피**.

**근거**:
- **git SSOT 보존**: diagram-as-code = git source 안 평문 fenced code block (마크다운 안 직접 embed). git diff / PR review 가능.
- **ADF round-trip lossy 회피**: Confluence storage format (ADF) ↔ markdown round-trip 시 native macro 는 lossy (markdown→Confluence direction 에서 source representation 손실). diagram-as-code = round-trip safe (markdown fenced code block 보존).
- **ADR-103 sync mechanism 정합**: sync direction 단방향 git → Confluence (§결정 1 정합) — diagram-as-code 는 Confluence 측에서도 native rendering 지원 (Mermaid plugin / PlantUML macro 활용 가능, ADR-103 sync agent carrier 가 render setup).

**예외 영역 (Confluence native macro 허용)**: (a) 사용자 직접 작업 영역 (개인 SoE-Confluence layer — Epic-A scope 외) / (b) external embed (외부 도구 link, sync 대상 아님). 본 ADR 의 design doc 4 closed-enum 대상 (§결정 1) = native macro 사용 금지.

### §결정 5 — Cross-link discipline (git anchor + Confluence anchor 양쪽 link 의무)

§결정 1 mirror 영역 (closed-enum 4 design doc 대상) git source 마다 Confluence anchor link 의무 부착. 역방향도 동일 (Issue body design content 참조 시 Confluence anchor + git anchor 양쪽 link 의무).

**의무 영역 enum**:

| 영역 | 의무 anchor 형식 | 예시 |
|---|---|---|
| design doc git source frontmatter / body | `confluence_anchor: <full URL>` field (frontmatter optional) OR body 안 cross-link footer (frontmatter 부재 시) | `confluence_anchor: https://<workspace>.atlassian.net/wiki/spaces/<space>/pages/<id>/<slug>` |
| Issue body 안 design content 참조 (예: "ADR-100 §결정 1 정합") | 양쪽 link — Confluence anchor (`[ADR-100 Confluence](https://...)`) + git anchor (`[git source](docs/adr/ADR-100-...md)`) | 양 anchor 동시 노출 |
| PR body 안 design doc 인용 | 동일 — 양쪽 link 의무 | (Issue body 동형) |

**근거**: Confluence readable layer (SoR-docs) 와 git source layer (SoR-work) 의 disjoint axis (ADR-100 §결정 1) 가 사용자 navigation 영역에서도 양 channel 동시 가시화 의무 — 한쪽 link 만 노출 시 다른 channel 의 freshness / staleness window 인지 비용 폭발.

**mechanical enforcement (warning-tier deferred-followup)**:
- **lint name**: `issue-design-content-confluence-link` (1 entry, warning-tier).
- **scope**: Issue body / PR body 안 `(ADR|architecture|change-plan|domain-knowledge) ?-?\d+` regex match 시 Confluence anchor 또는 git anchor 둘 다 grep-presence 의무.
- **Phase 2 wire**: Sub-A S1.3 / CFP-1421 carrier — `templates/github-workflows/issue-design-content-confluence-link.yml` + `scripts/check-issue-design-content-confluence-link.sh` + bats fixture + evidence-checks-registry row append.
- **bypass label**: `hotfix-bypass:issue-design-content-confluence-link` (별 carrier 시 label-registry-v2 family member 신설).
- **rationale**: declaration-only Wave 1 — ADR-082 §결정 6 retain pattern 답습 (Wave 1 declare / Wave 2 wire). pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier.

## 결과

### 긍정

- design doc Confluence mirror 인정 범위 closed-enum 4 codify (§결정 1) + Issue-only retain 면제 영역 closed-enum 5 codify (§결정 2) — 사용자 / 에이전트 분류 결정 분기 0 invariant.
- ADR-100 §결정 1 enumeration 부재 해소 — sibling Story 마다 재논의 비용 차단 (6+ window evidence 영역 정책 mechanism layer 박제).
- ADR-013 §결정 1 KEEP / ADR-100 §결정 1 partial extend 의 disjoint axis 보존 (git SoR-work + Confluence SoR-docs) + closed-enum 분류 layer 추가만 신설 (의미 약화 0건).
- Confluence IA axis 정의 (§결정 3) → 정식 재구조화 Sub-B carrier 위임 가능 (flat 3-parent hierarchy transitional 명시).
- diagram-as-code 의무화 (§결정 4) — ADF round-trip lossy 회피 + git source representation 보존.
- cross-link discipline (§결정 5) — git ↔ Confluence 양 channel 동시 가시화 mechanism (사용자 navigation cost 감소).

### 부정 / trade-off

- closed-enum 9 (4 mirror + 5 retain) 의 확장 영역 (예: 신규 design doc type 도입) 시 별도 CFP carrier 의무 (open_extension: false). 완화 = §결정 1/2 enum 확장 명시 carrier path (별도 ADR Amendment + ADR-RESERVATION row 신설).
- Confluence anchor field (§결정 5 frontmatter `confluence_anchor`) 신설 = 4 design doc 영역 frontmatter schema 갱신 (선택적) — 실 wire 시 ADR-041 doc-locations.yaml schema 갱신 동반 (ADR-103 carrier defer 영역 정합).
- diagram-as-code (§결정 4) 의무화 = Confluence native macro 사용처 영역 migration 필요 (현 시점 사용처 0 추정 — verify 영역). 완화 = §결정 4 예외 영역 enum (외부 embed / 개인 SoE 영역) 명시.
- mechanical_enforcement_actions `[issue-design-content-confluence-link]` Wave 1 declaration-only — 실 wire = Sub-A S1.3 / CFP-1421 carrier. pattern_count >= 2 재발 시 follow-up CFP MUST promote.
- ADR-100 Amendment 1 동반 발의 = 본 PR scope 안 dual-binding (ADR-111 신설 + ADR-100 Amendment 1) — change scope 정합 verify 의무 (3 files only invariant 보존).

## 해소 기준

N/A — permanent policy

N/A — permanent governance ratchet (`is_transitional: false`). closed-enum 4 mirror 대상 codify + closed-enum 5 Issue-only retain 면제 codify = 영구 분류 정책 mechanism layer. ADR-058 §결정 5 ratchet 강화 방향 sunset_justification 면제 정합. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 (강화 = closed-enum 도입 + cross-link discipline mandate, 약화 0건 — forbid scope 축소 아님).

amendment 시 sunset_justification 의무 (약화 방향 evidence-gate, ADR-058 §결정 5 + ADR-064 §결정 7 Amendment 8 evidence-gated symmetric ratchet 정합) — 강화 방향 (예: closed-enum 4 mirror 확장 / closed-enum 5 retain 강화 / cross-link discipline 강화 / IA axis 정밀화) 은 sunset_justification 면제. 약화 방향 (예: closed-enum 4 mirror 축소 / closed-enum 5 retain 축소 / cross-link discipline 의무 제거 / diagram-as-code 의무 약화) 은 ADR-058 §결정 5 sunset_justification 의무로 evidence-gate 통과 요구.

## 대안

### 대안 1 — full Confluence migration (단방향 → 양방향 bidirectional sync) [reject]

git source → Confluence readable mirror 가 아니라 **양방향 bidirectional sync** (Confluence 측 편집 → git 측 reverse sync 포함) 채택.

- **reject 근거**: (a) ADF round-trip lossy (Confluence storage format ↔ markdown round-trip 시 source representation 손실 — diagram / table / formatting 영역 lossy verified pattern). (b) git SSOT 약화 (variant truth — Confluence 측 편집 = git source 와 disagree 영역 발생, ADR-013 §결정 1 KEEP invariant 위반). (c) ADR-100 §결정 1 disjoint axis (git = SoR-work / Confluence = SoR-docs readable) 의 의미 파괴 — SoR-work 가 양 channel 분산 시 변경 ledger 단일 source 가 아님.

### 대안 2 — Issue body 전체 Confluence migration [reject]

Story file / FIX Ledger / Lane Evidence 영역 (Issue body bidirectional binding 영역) 도 Confluence mirror 대상으로 확장.

- **reject 근거**: (a) ADR-013 §결정 1 KEEP 영역 위반 (Story file = codeforge-internal-docs SSOT, FIX Ledger / Lane Evidence = git Story file SSOT). (b) Issue body bidirectional binding 영역 = codeforge governance 의 1차 mechanism (Issue label / phase / fix:* mirror) — Confluence 3-way mirror 추가 시 sync invariant 복잡도 폭발 (3-way drift surface 신설). (c) FIX Ledger fix-event-v1 v1.3 contract Orchestrator monopoly (CFP-32) — Confluence mirror = monopoly 영역 침범. (d) spawn prompt USER-UTTERANCE-VERBATIM block (ADR-082 §결정 1 layer 1-C) = ephemeral subagent context, 평문 secret leak surface 신설 risk.

## Cross-ref

- **ADR-100 (Confluence doc SSOT 인정)** = §결정 1 enumeration carrier — 본 ADR-111 §결정 1 closed-enum 4 대상 codify carrier. ADR-100 Amendment 1 동반 발의 (본 PR scope) — design doc Confluence-mirror 인정 범위 확장 (단방향 git→Confluence sync 정책 위에 4-대상 enum 명시).
- **ADR-099 (Atlassian-allow redefinition)** = §결정 2 Layer 2 lint allowlist 영역 — 본 ADR-111 평문 Confluence 참조 = ADR-099 §결정 2 Layer 2 allowlist 영역 (governance docs 평문 인용 허용 carrier).
- **ADR-103 (git↔Confluence sync mechanism)** = sync direction (단방향 git→Confluence) + write boundary (sync agent 단일 진입점) owner. 본 ADR-111 §결정 1 mirror 대상 sync 책임 위임. ADR-103 = doc-locations.yaml confluence variant / authoritative_source field 실 변경 owner (ADR-100 §결정 2 defer 영역 정합).
- **ADR-013 (codeforge family dogfood-out)** = §결정 1 KEEP 영역 정합 — 본 ADR-111 §결정 2 Issue-only retain 5 면제 영역 모두 ADR-013 §결정 1 KEEP 영역 (plugin repo 잔류 runtime SSOT 또는 ephemeral subagent context).
- **ADR-041 (doc location registry)** = §결정 6 Trigger #1/#2 — 본 ADR-111 §결정 1 closed-enum 4 대상 = ADR-041 doc_types 4 entry (adr / architecture_doc / change_plan / domain_knowledge) 위치 SSOT 정합. confluence variant / authoritative_source field intent declare = ADR-103 carrier (declare-only).
- **ADR-068 I-4 (wording SSOT chief tie-break ladder Amendment 2)** = 본 ADR-111 §결정 3 IA axis / §결정 5 cross-link discipline 어휘 single SSOT 정합.
- **ADR-064 §결정 7 (evidence-gated symmetric ratchet Amendment 8)** = 본 ADR-111 신설 = ratchet 강화 방향 (closed-enum codify + cross-link discipline 의무), sunset_justification 면제.
- **ADR-058 §결정 5 (sunset_justification mandate)** = 본 ADR-111 is_transitional: false permanent governance ratchet 정합.
- **ADR-078 (living architecture doc SSOT)** = §결정 1 closed-enum 2번째 대상 (Living Architecture page) carrier — per-plugin self-owned `docs/architecture/`.
- **ADR-082 §결정 1 layer 1-C (USER-UTTERANCE-VERBATIM block)** = §결정 2 5번째 면제 (spawn prompt) anchor — ephemeral subagent context, 평문 secret leak surface 차단 정합.

## 관련 파일

- `docs/adr/` — §결정 1 closed-enum 1번째 대상 (ADR)
- `docs/architecture/` — §결정 1 closed-enum 2번째 대상 (Living Architecture page, ADR-078 carrier — 9 plugin family per-plugin self-owned)
- `docs/change-plans/` — §결정 1 closed-enum 3번째 대상 (Change Plan, dogfood = internal-docs repo SSOT)
- `docs/domain-knowledge/` — §결정 1 closed-enum 4번째 대상 (Domain Knowledge)
- `docs/orchestrator-playbook.md` — §결정 1 closed-enum 5번째 대상 (Orchestrator Playbook, Amendment 1 CFP-1618 carrier — orchestrator-runbook scope boundary 한정, 일반 runbook 영역 비포함)
- `docs/confluence-ia-tree.yaml` — §결정 1 5번째 대상 split mapping SSOT (`playbook_split_pages[]` array + `playbook_pages_adr_111_classification` declaration block, Amendment 1 CFP-1618 동반 갱신)
- `docs/adr/ADR-100-confluence-doc-ssot-recognition.md` — ADR-100 Amendment 1 동반 발의 carrier (design doc Confluence-mirror 인정 범위 확장 — 단일 phrasing 위에 closed-enum 4 대상 정식 codify)
- `docs/adr/ADR-099-atlassian-allow-redefinition.md` — §결정 2 Layer 2 lint allowlist 영역 (평문 Confluence 참조 허용 영역 정합)
- `docs/adr/ADR-103-git-confluence-sync-mechanism.md` — sync mechanism owner (sync direction / write boundary / doc-locations.yaml confluence variant 실 변경)
- `docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md` — §결정 1 KEEP 영역 정합 (Issue-only retain 5 면제 영역 정합)
- `docs/adr/ADR-041-doc-location-registry.md` — doc_types 4 entry (adr / architecture_doc / change_plan / domain_knowledge) 위치 SSOT 정합
- `docs/adr/ADR-078-living-architecture-doc.md` — §결정 1 closed-enum 2번째 대상 carrier
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — §결정 2 5번째 면제 (spawn prompt) anchor + §결정 5 declaration-only Wave 1 retain pattern 답습
- `templates/github-workflows/issue-design-content-confluence-link.yml` — §결정 5 cross-link discipline lint workflow (Phase 2 wire — Sub-A S1.3 / CFP-1421 carrier, 본 PR scope 외)
- `docs/adr/ADR-RESERVATION.md` — row 111 reserved → active 전환
