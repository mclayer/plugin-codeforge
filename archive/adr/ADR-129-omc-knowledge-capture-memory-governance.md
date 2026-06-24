---
adr_number: 129
title: "OMC-adopt 지식캡처 + 메모리 다이어트 — 완료시점 capture 게이트 + MEMORY.md 용량관리 규약"
status: Accepted
category: governance
date: 2026-06-24
carrier_story: CFP-2392
parent_epic: CFP-2391
supersedes: null
amends: null
amendments: []
related_stories:
  - CFP-2392  # 본 ADR 신설 carrier (지식캡처 게이트 + MEMORY.md 용량관리)
  - CFP-2391  # parent Epic (OMC-adopt)
related_adrs:
  - ADR-045   # Amendment 14 동반 — phase:완료 precondition 에 capture self-check 추가 (§D-12 worktree-clean self-check 동형 — local-only warning-tier, required CI 0)
  - ADR-071   # Amendment 12 동반 — §18.7 deferred carrier (MEMORY.md 슬림화 mechanism) resolved_carrier: ADR-129 마커 (defer 해제)
  - ADR-128   # archetype — 완료 단계 정식화 (구조 동형: workflow:null warning-tier local self-check + paired Amendments, NEW ADR 채택, 흡수 거부). 본 ADR 의 강제 선례 SSOT.
  - ADR-051   # skill 형식 SSOT (skills/<slug>/SKILL.md subdir + frontmatter name/description + trigger ≥20 lines)
  - ADR-119   # §결정 9 제안 필요성 3문 게이트 — 동형 패턴(noise 억제 3문 게이트)이나 도메인 disjoint(작업 제안 필터 ↔ 지식 캡처 필터), 통합 금지 cross-ref only
  - ADR-064   # §결정 7 evidence-gated SYMMETRIC ratchet — overlay 의 capture 강도 약화 = evidence-gate + sunset_justification 필요
  - ADR-058   # §결정 5 sunset_justification — overlay weakening clause 의 evidence-gate carrier
  - ADR-060   # evidence-enforceable framework — capture/capacity local-only check 의 warning-tier 등록 (workflow:null, §결정 5 신규 entry warning 시작 / §결정 6 promotion gate)
  - ADR-099   # workflow:null local-only check 선례 (CI 미wire — standalone/세션-개시 호출)
  - ADR-122   # workflow:null local-only check 선례 (회귀 방지 gate)
  - ADR-127   # 모든 면제·단축경로 폐지 — capture 게이트 = forcing function 추가(ratchet 강화) 방향 정합 / change-plan 면제 폐지(본 Story change-plan 산출)
  - ADR-024   # Amendment 19 §B required 6-tuple bypass 신설 금지 invariant — 본 게이트가 required CI check 신설 안 함 정합
  - ADR-068   # boundary completeness invariants — 게이트 차원(검증대상/timing/evidence/tier) 정합
  - ADR-120   # §결정 3 skill = 절차 split — capture 게이트 절차 skill 분리 정합
related_files:
  - archive/adr/ADR-045-story-retro-mandatory-trigger.md
  - archive/adr/ADR-071-orchestrator-user-dialog-convergence.md
  - skills/knowledge-capture-gate/SKILL.md
  - docs/orchestrator-playbook.md
  - CLAUDE.md
  - docs/evidence-checks-registry.yaml
  - docs/domain-knowledge/domain/governance-principle/knowledge-capture-and-memory-governance.md
mechanical_enforcement_actions:
  # 본 ADR = 지식캡처 게이트 + MEMORY.md 용량관리 umbrella. 두 게이트 = 로컬-only check.
  # capture 게이트 = 완료 시점 marker 검출(로컬). MEMORY.md = ~/.claude/projects/<hash>/memory 외부 파일(클라우드 러너 미접근).
  # → 둘 다 required CI check 불가. evidence-checks-registry 등록 = warning-tier + workflow:null (ADR-099/ADR-122/ADR-128 선례).
  # Phase 1 = declarative (본 ADR + paired amendments + skill + playbook pointer + Story §8 test contract). Phase 2 = mechanical wire(별 PR).
  - action: knowledge-capture-completion-gate
    status: deferred-followup     # Wave 1 declarative (본 Phase 1 ADR + skill SSOT + playbook §9.7.2 pointer + ADR-045 Amendment 14 §D-13 precondition). actual local check 스크립트 + evidence-registry workflow:null entry active 전환 = Phase 2 PR scope.
    progress_note: "완료 처리 시점에 재사용 지식 capture admission 결과 흔적(capture artifact OR 명시적 no-capture note)이 존재하는가 검출. 3문 게이트(구글5분/코드베이스특정/실제노력) 자체 판정 = semantic(behavioral, Orchestrator self-eval), lint 은 '흔적 존재'만 presence 검사. 로컬-only (workflow:null, ADR-099/ADR-122/ADR-128 선례). required check 신설 금지(ADR-024 Amd19 §B). fail-safe = git/gh 미인증 시 exit 0 보존(hard-block 금지). Phase 2 = scripts/check-capture-gate-completion.sh + evidence-registry warning-tier entry active 전환."
    target_section: §결정 1
  - action: memory-capacity-gate
    status: deferred-followup     # Wave 1 declarative (본 Phase 1 ADR + skill §2 slimming-protocol SSOT). actual local check 스크립트 + evidence-registry workflow:null entry active 전환 = Phase 2 PR scope.
    progress_note: "MEMORY.md size > 24.4KB 시 slimming 수행 흔적(size 감소 또는 archive 갱신) AND active-Story entry 보존(lossless invariant) 검출. MEMORY.md = ~/.claude/projects/<hash>/memory/MEMORY.md = repo 외부 + 클라우드 러너 미접근 → CI lint 불가(ADR-128 worktree-clean 동근원). 'archive 적격 완료-Story 판정' = semantic(honest decline, ADR-119 abstention), lint 은 size + entry presence 만. fail-safe = MEMORY.md 경로 부재 시 exit 0 no-op(graceful). Phase 2 = scripts/check-memory-capacity.sh + evidence-registry warning-tier entry active 전환."
    target_section: §결정 2
related_carrier_issues: []
is_transitional: false
sunset_justification: null
---

# ADR-129: OMC-adopt 지식캡처 + 메모리 다이어트

## 상태

Accepted (2026-06-24 KST, CFP-2392 carrier, parent Epic CFP-2391). `is_transitional: false` — 영구 정책. 본 ADR 은 **forcing function 추가(ratchet 강화) 방향** — 완료 시점의 재사용 지식 외부화를 자율준수 의존에서 게이트형 확인으로 격상하고, MEMORY.md 용량관리를 "선언됐으나 mechanism 미구현"(ADR-071 §18.7 deferred) 상태에서 실 규약으로 실현한다. 약화 방향이 아니므로 ADR-058 §결정 5 `sunset_justification` 의무 비대상.

## 본질 선언

> **두 net-new 게이트, 한 도메인 문제(휘발성 운영지식의 디스크 영속화)의 두 면을 codify 한다. (A) 완료 처리 시점에 "이번 작업에서 재사용 가능한 지식이 나왔는가 — 나왔다면 외부화했는가" 를 강제 확인하는 capture 게이트. (B) 그렇게 축적된 MEMORY.md 가 용량 cap(24.4KB)을 넘을 때 무손실로 슬림화하는 용량관리 규약. 신규 lane·신규 required CI check 는 만들지 않고, 기존 `phase:완료` 게이트형 완료 단계(ADR-128)를 local-only warning-tier self-check 로 확장한다. 외부 차용 = oh-my-claudecode(MIT) skillify 의 3문 캡처 게이트 admission 휴리스틱 1건뿐 — 나머지(경로 규약·char-budget·용량 cap·슬림화 전략)는 codeforge 내부 도출이다.**

## 컨텍스트

### 사용자 directive (Story §1 = CFP-2392)

OMC(oh-my-claudecode) 의 지식 캡처 / 메모리 관리 패턴을 codeforge 에 차용하되, codeforge 의 in-repo skill·domain-knowledge SSOT 와 ADR-071 MEMORY.md cap 규약 위에 정합하게 얹는다. parent Epic CFP-2391 = OMC-adopt 묶음의 S1.

### 두 약점 (실측 검증된 갭)

| 갭 | 본질 | 실측 근거 |
|---|---|---|
| **갭 A — capture timing 공백** | 완료 시점에 재사용 지식 외부화를 강제하는 forcing function 0. retro(ADR-045)는 post-hoc + multi-Story + ADR escalation 단위라 single-task pre-completion 외부화를 잡지 못함 | retro.md + PMOAgent self-write(`docs/retros/**`, Story §11, `gate:retro-complete`) 에 "재사용지식 캡처" 항목 ABSENT `[verified]` (Story §2.2 firsthand inventory). skills/ 약 19개 중 `knowledge-capture` skill ABSENT `[verified]`. |
| **갭 B — 용량관리 mechanism 미구현** | ADR-071 §18.2 가 24.4KB cap 을 선언하고 §18.3 이 슬림화를 normative 로 규정했으나, §18.7 이 "MEMORY.md 인덱스 entry 슬림화 mechanism" 을 별 carrier 로 **deferred** 처리 → 선언만 있고 실 규약·실행 흔적 0 | ADR-071 §18.7:1030 `[verified]` "MEMORY.md 인덱스 entry 슬림화 mechanism … 별 carrier (사용자 memory management protocol) defer". MEMORY.md rendered = 27.8KB > 24.4 cap → harness 가 "Only part loaded" truncate `[verified]` (session-reminder). |

핵심 통찰 = 갭 A 는 "캡처 시점" 의 공백이고 갭 B 는 "캡처된 것의 용량" 의 공백이다. 둘 다 **휘발성 운영지식의 디스크 영속화** 라는 한 도메인 문제의 두 면 — capture(들어오는 흐름) + slimming(쌓인 것의 관리). 따라서 한 skill·한 ADR umbrella 로 묶되, 두 개의 독립 게이트(§결정 1 / §결정 2)로 codify 한다 (Story §5.1 — 두 net-new feature, 한 도메인).

### OMC 차용 범위 (firsthand — 무엇은 차용이고 무엇은 내부 도출인가)

oh-my-claudecode `skills/skillify/SKILL.md` (MIT, Copyright (c) 2025 Yeachan Heo, WebFetch firsthand) 의 3문 admission gate 만 차용한다:

1. "Could someone Google this in 5 minutes?" → No
2. "Is this specific to this codebase, project, or workflow?" → Yes
3. "Did this take real debugging, design, or operational effort to discover?" → Yes
(3문 모두 YES 일 때만 캡처)

**차용하지 않는 것 (firsthand 정정)**:
- OMC 의 경로 규약(`~/.claude/skills/omc-learned/`, `.omc/skills/`) — codeforge 는 in-repo `skills/<slug>/SKILL.md` + `docs/domain-knowledge/` SSOT 를 그대로 유지. OMC 경로 미차용 `[verified]` (Story §6.3).
- OMC skillify 에는 char-cap·descriptor-only·Expertise/Workflow split 이 **없음** `[verified]` (firsthand) → 본 ADR 의 char-budget(§결정 2)은 OMC 가 아니라 ADR-071 §18.2 cap + harness reminder 의 **internal 도출**이다.

## 결정

### §결정 1 — 갭 A: 완료시점 capture 게이트 (로컬-only warning-tier, required CI 불가)

`phase:완료` transition 의 precondition 에 **"이번 Story 에서 재사용 가능한 지식이 외부화됐는가" capture self-check** 1항을 추가한다 (ADR-045 Amendment 14 §D-13 carrier — ADR-128 §D-12 worktree-clean self-check 와 동형 구조).

**(1) admission 휴리스틱 (3문 게이트 — semantic, behavioral)**

작업 완료 시 Orchestrator 가 3문을 self-eval 한다 (OMC skillify 차용, §컨텍스트 verbatim). 3문 모두 YES 면 그 지식은 캡처 대상이다. 이 admission 판정 자체는 **semantic judgment** 이라 mechanical lint 불가 — behavioral directive (Story §8.3 anti-theater 분류).

**(2) routing (skill vs domain-knowledge)**

캡처 대상이면 산출물 형식을 결정한다:
- **절차/실행 가능한 운영 지식** → `skills/<slug>/SKILL.md` (ADR-051 form, ADR-120 §결정 3 skill=절차 split 정합).
- **사실/원리/패턴 지식** → `docs/domain-knowledge/<category>/<slug>.md` (예: `docs/domain-knowledge/domain/governance-principle/` EXISTS `[verified]`).

routing 의 상세 decision = `skills/knowledge-capture-gate/SKILL.md` §1 SSOT.

**(3) 게이트 tier (비협상 — warning-first, required CI 불가)**

`phase:완료` transition = Orchestrator self-write(로컬)이고 capture artifact 검출 = 완료 시점 working-tree marker 검출(로컬)이라 **required CI check 불가**. 3-조합으로 기계화 (ADR-128 §결정 2 답습):

1. **(a) Orchestrator behavioral precondition** — playbook §9.7.2 완료 단계 수렴 SSOT 에 capture self-check pointer 1줄 + ADR-045 Amendment 14 §D-13 precondition 1항.
2. **(b) 로컬 check 스크립트** — `scripts/check-capture-gate-completion.sh` (Phase 2). 완료 marker 시점에 capture artifact(신규 `skills/<slug>/SKILL.md` 또는 `docs/domain-knowledge/.../*.md`) **OR** 명시적 no-capture note("캡처 대상 검토 완료 — 외부화 불요(사유)" 1줄) 흔적을 검사. 둘 다 부재 = WARN.
3. **(c) evidence-checks-registry 등록 = warning-tier + `workflow: null`** — 로컬 전용 (ADR-099/ADR-122/ADR-128 worktree-clean 선례 동형, `# CI 미wire — standalone / 세션-개시 호출` marker).

**(4) warning-first + forced-no-silent-skip (검사연극 회피)**

게이트는 **always exit 0 advisory** (warning-tier). 그러나 "캡처할 게 없다" 는 결론도 **명시적 흔적** 으로 남겨야 한다 (no-capture note) — silent skip 금지. capture artifact 0 ∧ no-capture note 0 = WARN emit (Story §8.1 TC3 discriminating-negative). 즉 "캡처했다" 와 "검토했는데 불요" 둘 중 하나는 흔적이 있어야 한다. 이로써 게이트가 "항상 통과(failing fixture 부재)" 인 검사연극이 되지 않는다 (anti-theater = missing-case, Story §8.1).

**(5) fail-safe** — git/gh 미인증 시 exit 0 보존 (data-loss 가드, hard-block 금지). 완료 marker 부재(진행 중) 시 exit 0 no-op (E3 동형 — 미해당 시 발동 안 함).

### §결정 2 — 갭 B: MEMORY.md 용량관리 규약 (ADR-071 §18.7 deferred mechanism 실현)

ADR-071 §18.2 가 선언한 24.4KB cap 과 §18.3 의 슬림화 normative 를, §18.7 이 deferred 한 **실 mechanism** 으로 실현한다 (ADR-071 Amendment 12 가 §18.7 defer 를 `resolved_carrier: ADR-129` 로 해제).

**(1) 용량 SSOT (2-layer budget)**

MEMORY.md 용량은 2-layer 로 관리한다:

| layer | budget | source |
|---|---|---|
| **(a) per-entry one-line** | 인덱스 entry 1건 ≤ 약 200자 (one-line), 상세는 topic 파일로 | harness session-reminder verbatim "Keep index entries to one line under ~200 chars; move detail into topic files" `[verified]` |
| **(b) total file** | MEMORY.md 전체 ≤ 24.4KB | ADR-071 §18.2:977 `[verified]` cap SSOT |

**실측 근거 (forcing function evidence)** `[verified]`: MEMORY.md on-disk = 16.6KB(16602 bytes, 65 lines)이나 rendered/session-reminder = 27.8KB(>24.4 cap, harness 가 "Only part loaded" truncate). 최장 인덱스 entry = 390/383/359/351/348자 (가이드 ~200자 대비 초과). 2-layer 가 둘 다 필요한 이유 = (a) 위반(긴 한 줄)이 (b) 위반(총량)을 견인하기 때문. 상세는 topic 파일(`[title](topic.md)` + `[[wikilink]]` cross-ref, 기존 convention)로 이동한다.

**중요 — 출처 명확화 (firsthand 정정)**: char-budget 은 OMC 차용이 **아니다**. OMC skillify 에는 char-cap·descriptor-only split 이 없다 `[verified]`. (a) one-line ~200자 = harness reminder 도출, (b) 24.4KB = ADR-071 §18.2 도출 — 둘 다 internal.

**(2) 슬림화 전략 (oldest-first + completed-Story consolidate)**

`size > 24.4KB` 시:
- **oldest-first** — 가장 오래된 entry 부터 슬림화 (ADR-071 §18.3:983-988 normative 답습).
- **completed-Story consolidate** — 완료된 Story 의 여러 entry 를 topic 파일로 통합·압축.
- **archive-not-delete** — 슬림화는 내용 삭제가 아니라 topic 파일로 **이동** (무손실).
- **active-Story preserve** — 진행 중(active) Story 의 entry 는 슬림화 대상 제외 (lossless invariant, Story §8.2 TC3).

**(3) lossless invariant (무손실)**

슬림화 후 (a) active-Story entry 가 보존돼야 하고 (b) 슬림화된 내용은 archive(topic 파일)에 존재해야 한다. 이 invariant 위반 = WARN (Story §8.2). "이 entry 가 archive 적격 완료-Story 인가" 판정 = **semantic** → mechanical lint 불가, honest decline (ADR-119 abstention) — lint 은 size + entry presence 만 검사 (Story §8.3).

**(4) 게이트 tier (로컬-only warning-tier)**

MEMORY.md = `~/.claude/projects/<hash>/memory/MEMORY.md` = repo 외부 + 클라우드 러너 미접근 → CI lint 불가 (ADR-128 worktree-clean 과 동근원). evidence-checks-registry 등록 = warning-tier + `workflow: null` (Phase 2). fail-safe = MEMORY.md 경로 부재(harness 미생성) 시 exit 0 no-op (graceful).

### §결정 3 — axis-disjoint vs ADR-045 retro (흡수 거부, NEW ADR 정당화) + ADR-051/ADR-119 정합

본 capture 게이트는 ADR-045 retro 와 **3축 disjoint** 라 ADR-045 §D-9 로 흡수 불가 — NEW ADR umbrella 가 정당하다 (ArchitectAnalyst):

| 축 | capture 게이트 (본 ADR) | ADR-045 retro |
|---|---|---|
| **TIMING** | pre-completion forcing (완료 직전 강제) | post-hoc (Phase 2 PR merge 후) |
| **UNIT** | single-task (이번 작업) | multi-Story (cross-Story pattern) |
| **OUTPUT** | skill / domain-knowledge artifact | ADR escalation (`escalation_action`) |

또한 §결정 2(R2)는 **다른 ADR**(ADR-071)의 §18.7 deferred carrier 를 실현한다. 두 mechanism, 두 ADR → umbrella NEW ADR 정당.

**강제 선례 = ADR-128** (구조적으로 동일한 archetype): ADR-128 도 완료 단계 정식화를 `workflow: null` warning-tier local self-check 로 하면서 ADR-040 + ADR-045 에 paired Amendments 를 달고 **흡수하지 않고 NEW ADR 로 신설**했다. 본 ADR 은 동일 archetype·동일 선택 — ADR-045 + ADR-071 에 paired Amendments(§결정 1 / §결정 2 carrier) + NEW umbrella.

**ADR-051 정합**: 본 ADR 의 skill 산출물 = `skills/knowledge-capture-gate/SKILL.md` subdir form + frontmatter `name`/`description` + trigger ≥20 lines (ADR-051 SSOT).

**ADR-119 정합 (통합 금지 cross-ref only)**: 본 capture 게이트(3문 admission)와 ADR-119 §결정 9 제안 필요성 3문 게이트는 **동형 패턴**(둘 다 noise 억제 3문 게이트)이나 **도메인 disjoint** — ADR-119 = 작업 제안·follow-up Issue 발의 필터, 본 게이트 = 지식 캡처 필터. **통합 금지, cross-ref 만** (RefactorAgent — domain disjoint 이므로 한 게이트로 묶으면 서로 다른 결정면을 융합하는 over-abstraction). skill §3 에 cross-ref annotation.

**완료-self-check family 관찰 (escalation-tier, 강제 추상화 아님)**: worktree-clean(ADR-128) + capture(본 ADR)가 모두 `phase:완료` local-only warning-tier self-check 라는 family 가 emerging 한다. 그러나 지금 강제 추상화(공통 게이트 프레임워크 신설)는 하지 않는다 — pattern_count 2 는 ADR-045 §D-9 threshold 이나 두 게이트의 검증 대상(worktree 잔존 vs 지식 흔적)이 disjoint 라 공통화 이득 < 비용 (ADR-119 §결정 9 3문 게이트: 깨지지 않음 / 이득<비용 / 안 봐도 할 일 아님). family 가 3+ 로 늘면 그때 escalation (관찰만 박제, RefactorAgent confirm).

### §결정 4 — overlay evidence-gated symmetric ratchet + weakening clause

consumer overlay 는 capture 게이트의 **강도** 를 조정할 수 있으나 ADR-064 §결정 7 evidence-gated **SYMMETRIC** ratchet 가 적용된다:

- **강화 (strengthen)** — overlay 가 capture 강도를 높이는 것(예: warning → 더 엄격한 self-check, 추가 routing rule)은 **free** (evidence 불요).
- **약화 (weaken)** — overlay 가 capture 강도를 낮추는 것(예: 게이트 비활성화, no-capture note 면제)은 **evidence + `sunset_justification` 필요** (ADR-064 §결정 7 Amendment 8 + ADR-058 §결정 5). overlay 는 정책을 확장만 가능하고 축소 불가(CLAUDE.md overlay invariant)이므로, capture 게이트 약화는 evidence-gate 를 통과한 경우에만 (ADR-127 §결정 6 overlay 면제확장채널 폐지 정합 — overlay 가 면제 채널이 되지 않음).

이 weakening clause 는 본 게이트가 자율준수 약화 압력에 침식되지 않게 하는 ratchet 안전장치다 (Story AC-6).

### §결정 5 — MIT 출처 표기 (oh-my-claudecode 차용 명시)

3문 캡처 게이트 admission 휴리스틱은 oh-my-claudecode 차용이므로 출처를 명시한다 (Story AC-7, license hygiene):

> "3문 캡처 게이트 admission 휴리스틱 = oh-my-claudecode(MIT, Copyright (c) 2025 Yeachan Heo) skillify SKILL.md 차용."

이 표기는 `skills/knowledge-capture-gate/SKILL.md` §1 + 본 ADR §컨텍스트에 박제한다. 차용 범위 = admission 3문 1건뿐 (경로·char-budget·cap·슬림화 전략은 internal, §컨텍스트 firsthand 정정).

### §결정 6 — Phase 1 declarative / Phase 2 mechanical-wire split + 2 deferred registry entries

본 Story 는 ADR-128 의 Phase 1/2 split 을 답습한다:

- **Phase 1 (본 lane)** — declarative: 본 ADR-129 + ADR-045 Amendment 14 + ADR-071 Amendment 12 + `skills/knowledge-capture-gate/SKILL.md` + playbook §9.7.2 pointer + CLAUDE.md skill 표 행 + Story §8 test contract 명세. evidence-checks-registry entry 2종 = `status: deferred-followup` (ADR-128 worktree-clean Phase 1 선례 동형).
- **Phase 2 (별 PR)** — 실 check 스크립트 2종(`scripts/check-capture-gate-completion.sh` + `scripts/check-memory-capacity.sh`) + anti-theater test 2종 + registry warning-tier entry 2종 active 전환.

**2 deferred registry entries** (Phase 1 = declarative seed, Phase 2 = active 전환):
- `knowledge-capture-completion-gate` (owner_adr ADR-129, carrier_adr ADR-060, warning-tier, `workflow: null`, status deferred-followup).
- `memory-capacity-gate` (owner_adr ADR-129, carrier_adr ADR-060, warning-tier, `workflow: null`, status deferred-followup).

ADR-060 §결정 5 — 모든 신규 entry warning 시작. §결정 6 promotion = `pr_cumulative_min: 20` + `failure_threshold: 0` + sibling_dependencies (Phase 2 carrier).

### §결정 7 — required CI 불가 / branch protection 6-tuple 무변경 / change-plan 산출(면제 아님)

- **required CI check 신설 0 / branch protection 6-tuple 무변경** — 두 게이트 모두 로컬-only(완료 marker working-tree + ~/.claude 외부 파일). 신규 required check 자체를 안 만들어 ADR-024 Amendment 19 §B "required 6-tuple bypass escape valve 신설 금지" invariant 원천 정합.
- **change-plan 산출 (면제 아님)** — ADR-054 doc-only fast-path 는 ADR-127 이 supersede 했다(면제 폐지). 따라서 본 Story 는 lightweight change-plan 을 산출한다 (`wrapper/change-plans/cfp-2392-omc-knowledge-capture-memory-governance.md`). lightweight 인 이유 = 본 ADR draft 가 §3 도입 설계 SSOT 역할을 충족(ADR-128 §결정 8 ADR-carrier 정합)하므로 change-plan = 요약 + carrier map. 이는 노력 절감 skip 이 아니라 산출물 SSOT 통합 (ADR-127 §결정 5 "단축 vs N/A" 3축 구분).
- **마켓플레이스 sync 불요** — 신규 skill = `skills/` 자동 발견(plugin.json enumerate 0) + marketplace 4필드(name/version/description/author) 무영향 + CLAUDE.md skill 표 행 추가는 핵심흐름 의미변경이라 plugin.json bump 대상(설계 lane = 선언, 실 bump = Phase 2 또는 carrier PR). marketplace mirrored-field 변경 0 → `marketplace_sync_required: false` (Change Plan §13 declare).

## 결과

- 완료시점 capture 게이트 = `phase:완료` precondition 의 local-only warning-tier self-check (no new lane, no new required CI). 재사용 지식 외부화가 자율준수 의존에서 게이트형 확인으로 격상.
- MEMORY.md 용량관리 규약 = ADR-071 §18.7 deferred mechanism 실현. 2-layer budget(per-entry ~200자 + total 24.4KB) + oldest-first/completed-Story consolidate 슬림화 + lossless invariant.
- 두 게이트 = 한 skill(`knowledge-capture-gate`) + 한 ADR umbrella, 두 독립 게이트.
- OMC 차용 = 3문 admission 휴리스틱 1건 + MIT 출처 표기. 경로·char-budget·cap·슬림화 = internal 도출 (firsthand 정정).
- ADR-128 archetype 답습 — NEW ADR + paired Amendments(ADR-045 / ADR-071) + Phase 1 declarative / Phase 2 mechanical-wire.
- required CI 신설 0 / branch protection 6-tuple 무변경 / overlay symmetric ratchet → ADR-127/ADR-064 정합.

## 비용 (정직 고지)

- 두 게이트 = warning-tier advisory + behavioral precondition (로컬-only, CI hard-block 불가) → Orchestrator 자율준수 의존이 0 으로 떨어지지 않는다. CI hard-block 으로 만들 수 없는 구조적 한계(완료 marker working-tree + MEMORY.md 클라우드 미접근)를 받아들인다. mitigation = local check 스크립트 + evidence-registry 등록으로 behavioral compliance 보조.
- 3문 admission 자체는 semantic 이라 mechanical lint 불가 — lint 은 "흔적 존재" 만 검사하고 "이 지식이 실제 재사용 가능한가" 는 Orchestrator self-eval (honest decline, ADR-119 abstention). 게이트가 자동으로 지식 품질을 보장하지 못함을 명시한다.
- MEMORY.md 슬림화 후 "이 entry 가 archive 적격 완료-Story 인가" 판정도 semantic — lint 은 size + presence 만. 잘못된 슬림화(완료로 오판한 active Story archive)는 lossless invariant lint(active-Story entry presence)가 일부만 잡는다.

## 해소 기준

N/A — `is_transitional: false` (영구 정책, 강화 방향 ratchet).

## 관련

- [ADR-045](ADR-045-story-retro-mandatory-trigger.md) — Amendment 14 (§D-13 phase:완료 precondition capture self-check 추가)
- [ADR-071](ADR-071-orchestrator-user-dialog-convergence.md) — Amendment 12 (§18.7 deferred carrier resolved_carrier: ADR-129)
- [ADR-128](ADR-128-completion-stage-formalization.md) — 완료 단계 정식화 (본 ADR archetype — 흡수 거부 + paired Amendments + Phase 1/2 split SSOT)
- [ADR-051](ADR-051-ssot-skill-extraction-pattern.md) — skill subdir form SSOT
- [ADR-119](ADR-119-research-before-claims.md) — §결정 9 제안 필요성 3문 게이트 (동형·도메인 disjoint, cross-ref only)
- [ADR-064](ADR-064-decision-principle-mandate.md) — §결정 7 evidence-gated symmetric ratchet (overlay weakening clause)
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — §결정 5 sunset_justification (weakening evidence-gate)
- [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) — evidence-checks-registry framework (warning tier 2 entry)
- [ADR-099](ADR-099-atlassian-allow-redefinition.md) / [ADR-122](ADR-122-superpowers-dependency-removal.md) — workflow:null local-only check 선례
- [ADR-127](ADR-127-mandatory-full-flow-no-exemption.md) — 면제·단축 폐지 (본 ADR ratchet 정합 + change-plan 산출)
- [ADR-120](ADR-120-token-relocation-eligibility-criteria.md) — §결정 3 skill = 절차 split
- CFP-2392 — 본 ADR carrier Story / CFP-2391 — parent Epic (OMC-adopt)
