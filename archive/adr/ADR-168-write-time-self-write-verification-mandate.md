---
adr_number: 168
title: Write-time self-write verification mandate — internal lane agent write-time semantic truth verify super-class (ADR-082 재제정)
status: Accepted
category: governance
date: 2026-07-26
carrier_story: CFP-2840
supersedes:
  - ADR-082
amends: null
reinterpretation: false  # ADR-167 §결정 1(b) — 본 ADR 은 ADR-082 실효 규범의 의미 무변경 재제정(restatement)이지 소급 재해석이 아니다. 신규 저작(재해석 marker false).
is_transitional: false
related_adrs:
  - ADR-082  # 재제정 대상 — 본 ADR 이 supersede. 구본 = 본문 byte-보존 in-place 동결(이력 담보), 실효 규범은 본 ADR 로 이관
  - ADR-167  # 재제정(compaction) ratchet SSOT — 본 ADR = ADR-167 의 첫 실물 정산(워스트 1위 ADR-082)
  - ADR-073  # disjoint 보완 — Orchestrator cross-repo state/assumption verify (§결정 1 layer 1)
  - ADR-070  # disjoint 보완 — external worker(Codex) output verify (§결정 1 layer 2). D5 declaration-only retain 선례
  - ADR-045  # §D-9 cross_story_pattern_adr_trigger — 원 carrier escalation forcing function (§결정 1 layer 4)
  - ADR-067  # 결정 1 max FIX 3/3 reassessment + 결정 3 RESET vs escalation — §결정 3 정정 재귀 무한루프 cap 재사용
  - ADR-058  # §결정 5 약화 방향 차단 + is_transitional:false + EC-3 self-protection anchor
  - ADR-040  # Amendment 3 mechanical_enforcement_actions[] schema + worktree convention(§결정 1 sub-scope 1-J)
  - ADR-064  # §결정 1 unitary scope(§결정 7/8) + §결정 7 symmetric evidence-gated ratchet
  - ADR-068  # I-4 wording SSOT + I-5 empirical-source annotation(§결정 2(a))
  - ADR-085  # coordination axis disjoint complement (구 Amendment 3 cross-ref-only → 관련 ADR 로 흡수, disposition drop)
  - ADR-052  # Codex proactive check touchpoint #2 (§결정 10.A)
  - ADR-060  # 게이트 tier host framework (warning-tier + registry)
  - ADR-061  # Python SSOT + thin wrapper convention (mechanical wire)
  - ADR-063  # marketplace mirrored-field atomic invariant (agent .md content 변경 시 sync)
  - ADR-024  # branch protection + hotfix-bypass label family(§결정 13.A)
  - ADR-013  # dogfood-out internal-docs SSOT path(§결정 1 sub-scope 1-J)
  - ADR-151  # §결정 7 honesty ceiling — presence ≠ truth(§결정 16 상속)
  - ADR-119  # honest ceiling 어휘 SSOT
  - ADR-136  # I-6 honest ceiling 어휘 SSOT
  - ADR-133  # ADR 번호 atomic claim — 본 ADR 번호(168) 발급
  - ADR-050  # ADR-RESERVATION GitOpsAgent monopoly — row 전이
related_stories:
  - CFP-2840
related_files:
  - CLAUDE.md  # verify-before-trust 4-layer 단락 — ADR-168 canonical anchor(구 ADR-082 인용 정정 = 역참조 정비 Phase 2)
  - docs/orchestrator-playbook.md  # §3.10/§3.14 cross-ref
  - archive/adr/ADR-RESERVATION.md  # amendment-slot pre-reservation(§결정 1 sub-scope 1-G) SSOT + ADR-number row(82 archived / 168 신설)
  - docs/evidence-checks-registry.yaml  # owner_adr ADR-082 계열 7 entry → ADR-168 re-home(Phase 2)
  - templates/story-page-structure.md  # §2.1 verified-state codify(§결정 12.A) 역참조 정정(Phase 2)
  - scripts/lib/check_adr_amendment_threshold.py  # 재제정 완료 게이트 Superseded-skip 배선(Phase 2, Story §7)
# effective_count 재시작 = 0: 본문 `^#{2,4} Amendment` 헤딩 0 ∧ frontmatter amendments:/amendment_log: 키 생략(양쪽 결합, AC-1). ADR-167 §결정 5 재제정 신규 count 0 재시작 정합.
mechanical_enforcement_actions:  # 재제정 re-home(§5.5(c)) — action 명(stable identifier) + 현행 wired 상태만. 진행 서사·SHA·pattern_count·label bump 이력 = 구 ADR-082 동결 보존. evidence-checks-registry owner_adr 실 flip = Phase 2. 구 sub-scope 1-W(orchestrator-spawn-prompt-fact-verify) = de-bloat 제거 유지(ADR-058 §결정 5 ratchet) → 미등재(복원 금지, disposition Amd34 drop).
  - action: corpus-claim-verify
    status: deferred-followup
    target_section: §결정 2(a)
  - action: cross-plugin-ownership-verify
    status: deferred-followup
    target_section: §결정 2(d)
  - action: amendment-number-frontmatter-verify
    status: warning-tier wired  # 양방향(forward+backward) staleness lint 배선 완료
    target_section: §결정 9
  - action: cross-repo-label-sync
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-D
  - action: spawn-prompt-head-pin-presence
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-E
  - action: mid-spawn-drift-detection
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-F
  - action: amendment-slot-reservation-check
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-G
  - action: pre-spawn-prompt-finalize-verify
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-H
  - action: issue-body-claim-pre-screen
    status: warning-tier wired  # 4 sub-pattern presence-lint 배선 완료
    target_section: §결정 15
  - action: worktree-target-authority-verify
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-J
  - action: numeric-claim-write-time-verify
    status: warning-tier wired(governance-docs scope) / declarative(PR-level scope)  # 1-N wired, 1-P 선언만
    target_section: §결정 1 sub-scope 1-K / 1-N / 1-O / 1-P
  - action: spawn-prompt-fact-verify
    status: warning-tier wire SSOT(1-Z) / Phase 2 actual wire 별 carrier
    target_section: §결정 1 sub-scope 1-L / 1-Z
  - action: synthesis-vs-commit-gap-check
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-M
  - action: execution-context-state-presence
    status: deferred-followup(registry deferred — Wave 1 declarative)  # 1-V G4: registry SSOT 신뢰
    target_section: §결정 1 sub-scope 1-V
  - action: subagent-self-report-post-task-verify
    status: deferred-followup
    target_section: §결정 1 sub-scope 1-X
  - action: resource-safety-claim-proof-presence
    status: warning-tier wire complete(5-piece)  # 배선 완료·active
    target_section: §결정 16
---

# ADR-168: Write-time self-write verification mandate — internal lane agent write-time semantic truth verify super-class (ADR-082 재제정)

## 상태

**Accepted** (2026-07-26 KST, CFP-2840 Phase 1 carrier).

**재제정 선언 (no-substantive-change — ADR-167 §결정 4(a) 필수 요소 (a))**: 본 ADR 은 **ADR-082(write-time self-write verification mandate)의 현행 실효 규범을 의미 무변경으로 깨끗한 신규 record 에 재작성한 재제정(re-enactment / recodification)**이다. 허용 변경 = **구조 개선·obsolete 제거·모호 해소·기술 정정 4종 한정**. 의무/금지/조건/예외의 규범 효력은 무변경이다. 의미 변경이 필요하면 재제정이 아니라 **별개 amendment 또는 신규 결정으로 분리**한다(본 Story 는 그런 항목을 발견하지 않았다 — 발견 시 해당 항목을 재제정에서 제외하고 분리, AC-5). 구 ADR-082 는 **본문 byte 무변경 in-place 동결**로 잔존하며(이력 담보), `status: Superseded by ADR-168` 로 전이한다. 실효 규범의 단일 canonical source = 본 ADR-168.

재제정 배경 = ADR-167(ADR amendment 누적 임계 재제정 ratchet)의 **첫 실물 정산**. 대상 = baseline `grandfathered_at` 워스트 1위 ADR-082(effective_count 76). effective_count 76 = **dual-block(amendments[] 38 + amendment_log[] 38) 합산 artifact** 이며 실제 distinct amendment = 38 — 본 ADR 은 원 §결정 1-8 + 38 amendment 가 접은 실효 규범을 §결정-level 로 fold 하고 **count 0 재시작**한다(ADR-167 §결정 5).

## 본질 선언

lane agent(RequirementsPL / ArchitectAgent / DeveloperPL 등)가 §9 evidence 작성 / Phase 0 ChangeImpactAgent mapping / Story corpus enumeration / Issue body authorship 시 **write-time 에 source·value·ownership 을 verify 없이 단언**하는 것을 금지한다. 작성한 **값 자체가 사실과 일치하는가**를 write 직전 source direct verify 후 write 한다. 본 ADR 이 충족되지 않으면 아래 §결정 mechanism 을 몇 개 쌓든 의미 없다 — 모든 §결정 은 본질을 보조하는 scaffolding 이다.

기존 codeforge governance 의 self-write 검증 layer 는 (1) write 권한 actor 경계(ledger write = Orchestrator monopoly) + (2) syntactic ownership(non-owner destructive write / monopoly unauthorized mutation) 만 정의한다. **(3) write-time semantic truth(작성 값이 사실과 일치하는가) verify layer 가 도메인 공백**이었고, 본 super-class 가 이 (3) layer 를 신설한 anchor 다.

## 컨텍스트

### 재제정 대상 = write-time semantic truth verify super-class

ADR-082 는 다음 pattern corpus(super-class 결함의 실증)를 anchor 로 신설됐다: (1a) 설계 corpus slip(factually FALSE corpus 단정) / (1b) 정정-2nd-slip(정정 행위 자체 미검증) / (2) §9 evidence stale(ADR frontmatter value source verify 없이 단언) / (3) Phase 0 cross-plugin ownership 추정. PMOAgent ADR-045 §D-9 pattern_count ≥ threshold 2 forcing function 산물(escalation_action `escalate_user`)이 단일 super-class 통합을 도출했다.

38 amendment 는 전량 `direction: strengthening`(ratchet-up — forbid scope 축소 0) 로, 실효 규범 = "가장 넓게 확장된 최종 상태"의 단일 스냅샷으로 fold 가능하다. 본 ADR 은 그 fold 를 §결정-level 로 수행한다.

### 해석 우선순위 조항 (R2 — no-substantive-change presumption)

본 ADR-168 의 문언과 구 ADR-082 규범이 상충하는 것으로 보일 때, **재제정 처분표(아래 §재제정 처분표)에 명시 변경으로 표기된 지점 외에는 구 규범의 의미가 우선**한다(no-substantive-change presumption). SSOT 지위 자체는 ADR-168 이 보유하되, 이 우선순위는 **상충 해소 한정 semantics** 이며 이중원본을 뜻하지 않는다 — 구 ADR-082 는 이력 담보로 동결 잔존할 뿐 규범 source 가 아니다. 재제정 처분표는 재제정 후에도 코드·문서의 "ADR-082 §결정 N / Amendment M" 인용을 신 위치로 해소하는 **영구 참조 해소 자료(lookup)**로 기능한다(R6).

## 결정

> 번호 보존 restatement — 생존 §결정은 ADR-082 원번호를 유지한다(§16 = resource-safety 그대로 §16). §결정 1 이 verify-before-trust 4-layer 표 + write-time verify sub-scope 1-A~1-Z(26종)를 host 한다.

### §결정 1 — Layer disjoint 판정 표 + write-time verify sub-scope host

verify-before-trust governance 는 4 disjoint layer 로 구성된다. 각 layer 는 verify 대상 / 행위 주체가 서로 disjoint 하며, 본 표가 4-layer 의 공통 anchor 다.

| Layer | ADR | verify 대상 / scope |
|---|---|---|
| Orchestrator cross-repo state / assumption verify | ADR-073 | Orchestrator 행위 한정 — cross-repo state + assumption 기술 시 `git fetch` + `git show origin/main:<path>` direct verify + `verified-via` annotation |
| external worker (Codex) output verify | ADR-070 | 외부 worker output 한정 — Codex finding evidence ground truth 를 Orchestrator direct file Read 로 verify, mismatch 시 verdict reject |
| **internal lane agent self-write verify (본 ADR)** | **ADR-168** | **lane agent §9 evidence / Phase 0 mapping / corpus enumeration / Issue body authorship write-time** — 작성 값 자체가 사실과 일치하는가 source direct verify 후 write |
| retro corpus enumeration (PMOAgent §5 pattern_count) | ADR-045 §D | retro pattern aggregation — cross-Story pattern_count ≥ threshold 검출 시 ADR escalation forcing function |

> 4-layer 로 충분하다(5th row 불요). ADR-085(multi-session coordination)은 verify-before-trust 와 별 axis(coordination axis — verify 가 충족돼도 coordination 부재 시 parallel race, 둘 다 필요한 orthogonal layer)로, cross-ref 관계는 관련 ADR 로 흡수한다(구 Amendment 3 = cross-ref-only, 규범 substance 0).

#### §결정 1 layer 1 — write-time verify sub-scope (1-A ~ 1-Z, 공통 4-tuple primitive)

layer 1(Orchestrator scope + chief author scope + lane PL scope)은 특정 authorship surface 마다 write-time verify-before-write 를 강제한다. 전 sub-scope 는 **공통 4-tuple primitive**를 surface 에 특화한 것이다:

- **(a) source 식별** — claim 의 ground truth source(command / 파일 경로 / API probe)를 명시한다(명시 가능해야 verify 가능).
- **(b) direct execute** — 작성 직전 source 를 fresh 실행해 actual value 를 획득한다(cached / 추정 / planning-time stale value 금지).
- **(c) claim ↔ actual cross-verify** — claim 값과 actual 값을 1:1 일치 verify 한다. semantic ambiguity 발견 시 source 정밀화 의무.
- **(d) verified-via annotation** — 일치 시에만 write + `verified-via` / `<...>_verified: <bool>` annotation 부착. mismatch 시 abort + sentinel 발화 / Orchestrator escalate.

각 sub-scope 는 이 primitive 를 아래 surface 로 특화한다(구 ADR-082 의 per-sub-scope 4-tuple 전문은 동결 ADR-082 본문에 byte-보존 — row 단위 spot-check anchor):

| sub-scope | verify surface | 유래 | wired 상태 |
|---|---|---|---|
| **1-A** | Orchestrator cross-repo state verify (read-time, ADR-073 base row) | base(pre-existing, amendment 비귀속) | ADR-073 layer |
| **1-B** | Orchestrator-authored Issue body authorship pre-publish verify | Amd 2 | declaration-only |
| **1-C** | lane PL spawn prompt user-utterance verbatim anchor(재합성·요약·paraphrase 금지) | Amd 5 | behavioral |
| **1-D** | cross-repo label-write authority verify-before-write | Amd 14 | deferred-followup |
| **1-E** | spawn prompt SHA-anchor pre-spawn pin | Amd 15 | deferred-followup |
| **1-F** | spawn-internal periodic origin re-pin protocol | Amd 16 | deferred-followup |
| **1-G** | amendment-slot pre-reservation strict claim (행위의무 4-tuple만; slot schema = `관련파일: ADR-RESERVATION.md` pointer) | Amd 17 | deferred-followup |
| **1-H** | Orchestrator §10 FIX Ledger resolution field source/evidence verify | Amd 18 | deferred-followup |
| **1-I** | pre-spawn-prompt-finalize verify layer(worktree-create ~ spawn-prompt-finalize window polling) | Amd 19 | deferred-followup |
| **1-J** | cross-repo worktree target authority verify(worktree path ↔ remote URL, `worktree_target_repo` field) | Amd 21 | deferred-followup |
| **1-K** | numeric claim write-time strict claim(6-dimension closed-set: line/file/API/pattern_count/commit/row count) | Amd 22 | declaration(governance docs) |
| **1-L** | spawn prompt fact verify-before-trust(worker→worker handoff upstream-inherited stale fact) | Amd 23 | Wave 2 wire = 1-Z |
| **1-M** | own-author synthesis 보고 ↔ actual git commit gap verify | Amd 24 | deferred-followup |
| **1-N** | 1-K Wave 2 mechanical enforcement wire(governance docs scope) | Amd 25 | **wired · active** |
| **1-O** | PR commit message + PR body numeric claim write-time strict claim | Amd 26 | declaration-only |
| **1-P** | 1-O Wave 2 mechanical enforcement wire SSOT(PR-level artifact scope) | Amd 27 | 선언만(actual script 미wired) |
| **1-Q** | ADR dual-block parity 3-invariant forward-prevention lint | Amd 28 | 최종형 = 1-U(narrow) |
| **1-R** | mid-Story FIX-loop re-verification mandate | Amd 29 | 미wired |
| **1-S** | ADR frontmatter block convention SSOT(FixB/C live; FixA = 1-U supersede) | Amd 30 | FixB/C live |
| **1-T** | PMOAgent retro write-time verify-before-trust mandate | Amd 31 | 미wired |
| **1-U** | dual-block gate — 1-Q lint scope 를 dual-block(양 array non-empty) ADR 로 narrow | Amd 32 | **wired · active(현행 최종 dual-block gate)** |
| **1-V** | execution_context_state 5 sub-field declare(working_dir / target_write_repo / staged_files / branch / remote_sync) | Amd 33 | Wave 1 declarative(registry deferred) |
| **1-W** | ~~orchestrator_spawn_prompt_fact_verify_before_embed~~ — **de-bloat 제거(복원 금지)**; C1-C5 fact patterns 는 1-Z handoff axis 로 이관 | Amd 34 | **제거(obsolete)** |
| **1-X** | subagent_self_report_post_task_verify(Orchestrator ← subagent "DONE/PASS/MERGED" 보고 후 artifact 실존·내용 verify) | Amd 35 | deferred-followup |
| **1-Y** | amendment_array_ordering_convention(amendments[] + amendment_log[] 배열 ordering SSOT: id ascending + reservation_date tie-break; `amendment_log[].sub_scope` field = mapping SSOT) | Amd 36 | convention(향후 ADR-167 재배치 여지 — 본 Story 범위 밖) |
| **1-Z** | spawn_prompt_fact_verify Wave 2 mechanical wire SSOT(1-L 최초 배선; PR-body-proxy static presence-only lint) | Amd 37 | Phase 1 SSOT 선언(Phase 2 실배선 미완) |

> sub-scope 는 전량 disjoint axis 다(surface 특화). 인접 sub-scope 간에도 verify 대상이 disjoint(예: 1-D label-write authority ↔ 1-J filesystem write-target authority). 1-U 가 1-Q(Amd 28) / 1-S FixA(Amd 30) 의 dual-block-narrow 최종형이며, 순차 수정된 중간 상태(1-Q 원서술 / 1-S FixA)는 이력이다(동결 ADR-082 보존).

### §결정 2 — Write-time verify 의무 (scope a-d)

lane agent 가 owned section 에 아래 4종을 write 할 때 write 직전 source direct verify 후 write 한다.

- **(a) corpus / fixture enumeration** — "예시 N건 / 전무 / 부재 / 다수" + file-path 인용 패턴 write 시 `git show origin/main:<path>` verify 후 `[verified: git show origin/main:<path>]` annotation 부착 의무(ADR-068 I-5 empirical-source annotation 과 directly-analogous mechanical 패턴).
- **(b) design-lane self-check** — ArchitectAgent §3 / §7 corpus enumeration + ADR frontmatter value 인용 시 verify 후 write. **정정 행위 자체도 동일 verify 의무**(§결정 3 재귀 cross-ref).
- **(c) §9 evidence write-time verify** — lane agent 가 §9 verdict evidence 에 ADR frontmatter value / contract field value 기재 시 source file direct Read verify 후 write.
- **(d) Phase 0 cross-plugin ownership verify** — ChangeImpactAgent Phase 0 mapping 시 `templates/*` 항목 wrapper-local 단정 전 cross-plugin SSOT verify 1-step 의무(verify source = `codeforge:lane-self-write-boundary` skill).

### §결정 3 — 정정 행위 재귀 verify + 무한 루프 cap

§결정 2 verify 누락이 사후 정정될 때, **정정 write 도 새 self-write artifact 이므로 동일 §결정 2 verify 대상**(재귀)이다. 무한 루프(verify the fix of the verify …) 차단은 **신규 메커니즘 미도입, 기존 layer 재사용** — ADR-067 결정 1(max FIX 3/3 도달 시 deterministic implementability reassessment trigger) + 결정 3(ArchitectPL 재량 RESET vs escalation 권한) 복합 재사용(over-engineering 회피).

### §결정 4 — Citation ≠ Assertion 경계

- **citation**(출처 명시) = attribution 으로 충분 → verify 면제.
- **assertion**(값을 사실로 주장) = §결정 2 verify 의무.

§결정 2 의 verify 의무는 **assertion 에만** 적용된다(인용된 타 lane 판정의 재검증 아님 — over-verify 회피).

### §결정 5 — Provisional marker defer

Phase 0 mapping 이 planning-phase 진행 중(spec/plan 미완성)일 때는 미완성 값에 `[provisional]` marker 를 부착하고 write-time verify 를 **defer** 한다. 최종 verify 의무 시점 = lane spawn 직전(`codeforge:story-epic-flow-preflight` preflight). `[provisional]` marker 부재 시 §결정 2 즉시 적용(defer 면제 조건 = explicit marker).

### §결정 6 — known-limitation (`mechanical_enforcement_actions[]` rationale binding)

`mechanical_enforcement_actions[]` 의 구성 및 warning-tier / deferred-followup / declaration-only 혼재는 **누락이 아니라 명시적 known-limitation 결정**이다(ADR-040 Amendment 3 schema 정합 — DesignReview 가 "missing enforcement" 로 flag 하지 않도록 explicit binding). rationale: (1) scope 2(d) cross-plugin ownership 의 verify source 는 `lane-self-write-ownership-matrix.yaml` machine_readable_ssot 로 실재하되 cross-plugin doc-ownership sub-tree 는 확장 append-only 영역이다(구조상 신규 registry 창설 아님). (2) super-class 결함은 scope (a)/(b)/(c)/(d)가 단일 anchor 로 묶인 unitary scope(ADR-064 §결정 1) — 일부만 mechanical 화 시 anchor 분절, behavioral mandate 가 공통 forcing function 으로 우선. (3) declaration-only retain 선례 = ADR-070 §D5.

**self-referential trap 회피(EC-3)**: 본 ADR 이 corpus 패턴을 본문에 인용/포함하는 것, 그리고 frontmatter `is_transitional: false` + `## 해소 기준 = N/A(permanent)` 선언은 §결정 2 verify 대상이 *아니다*(permanent 정책 선언 = source verify 가 적용될 mutable value 아님). DesignReview 가 "ADR 이 자기 frontmatter 를 verify 안 했다" 로 flag 하지 않도록 명문화한 self-protection.

### §결정 7 — scope (e) FIX 명세 depth-aware 분리 (scope 외)

scope (e) FIX 명세 depth-aware(broken-link/path 정정 FIX 명세 시 directory depth + 정정 규칙 범위 필드)는 **본 ADR scope 외**. write-time truth verify(a-d, behavioral) ↔ FIX 명세 depth-aware(e, fix-event-v1 schema 확장) = disjoint 관심사 — 동일 묶음 시 ADR-064 §결정 1 unitary scope 위반. (e) = 별도 CFP carrier.

### §결정 8 — per-area 분할 (scope a/b/c/d 각 별 ADR) 거부 (scope 외)

4 scope = 단일 super-class 결함의 4 layer 표현. §결정 1 layer disjoint 표가 공통 anchor. per-area 분할 시 super-class anchor 가 4 ADR 로 분절되어 cross-Story pattern aggregation(ADR-045 §D-9)의 forcing function 이 약화된다 → 단일 super-class 유지.

### §결정 9 — Amendment 번호 citation plan-time staleness 차단

거버넌스 artifact(β-issue body / spec / change-plan / PR body / ADR amendment 본문) 안에서 ADR 또는 inter-plugin contract 의 amendment 번호를 인용할 때, 인용 직전 target frontmatter `amendments:`(또는 `amendment_log`)를 `Read` 로 직접 확인한 후 **정확 next-slot `M = max(amendment_id) + 1` 만 사용**한다. `M > max+1`(forward-staleness) / `M ≤ max`(backward-staleness) **양방향** stale citation 을 차단한다.

verify-before-cite 의무: (1) target frontmatter 항목 직접 Read → (2) 현재 max `amendment_id` 확인 → (3) 새 번호 = 정확히 `max+1` → (4) `verified-via: <경로 및 시각>` annotation 부착. 본 §결정 은 §결정 2(b)의 sub-specialization(plan-time 시점 명시). Wave 2 mechanical lint(`amendment-number-frontmatter-verify`, 양방향 비교 + `[FORWARD-STALE]`/`[BACKWARD-STALE]` + self-reference exemption + templates/** filter)는 wired. ADR-068 I-4 wording SSOT 연계(stale 번호 = wording drift 원인).

### §결정 10 — ArchitectAgent write-time discipline (4 sub-scope)

§결정 1 layer 1 + §결정 2 scope(a-d)의 write-time verify mandate 가 ArchitectAgent(codeforge-design chief author)의 4 write-time discipline 으로 확장된다(disjoint axis, 단일 super-class unitary).

- **§결정 10.A — Codex TP#2 inline FIX 8-anchor mirror coverage checklist**: ArchitectAgent §3 직후 Codex proactive check touchpoint #2(ADR-052) verified-true P1 finding inline FIX 시 8 anchor 동시 갱신 의무 — (1) Change Plan §3 (2) §4 Risk (3) §7 Threat model (4) §10 미해소 이견 (5) Story §7 mirror (6) ADR carrier reference (7) **ADR 본문 §결정 N 표·단락(누락 빈발 anchor)** (8) ADR 신규 §결정 본문. verbatim wording 일관(ADR-068 I-4 wording SSOT).
- **§결정 10.B — Mid-author partial revert propagation gap**: mid-author FIX body normative correction 직후 frontmatter inline comment / appendix / table cell 까지 propagation 의무 — (1) `grep -rn "<stale-label>" <touched-files>` cross-check (2) DesignReviewPL body↔frontmatter/appendix/table 일관성 audit (3) post-FIX reverse-mutual grep(to-remove grep = 0 ∧ to-add grep ≥ N).
- **§결정 10.C — self-introduced script-behavior claim verify**: ArchitectAgent 가 codeforge script behavior claim(예: "parse-X.py skips template entries") 작성 시 empirical verify 의무 — (1) `[verified-via: <command>]` annotation + command run(미verify 시 `[unverified — DesignReview to confirm]`) (2) DesignReviewPL dedicated audit(script 실행 + source grep) (3) mutual cross-check before iter complete.
- **§결정 10.D — META self-application pattern**: Story 가 template / codification change 를 도입하면 carrier Story 자신에 1st applied case 로 적용(eat your own dog food) — (1) "이 codification 이 지금 쓰는 Story 에 적용되나?" 자문 (2) yes 시 Story 자체 적용 (3) META self-application 명시(amendment body / Change Plan §11 / Story cross-ref) (4) DesignReviewPL audit. (§10.D 의 Wave 2 mechanical wire `meta-self-application-wire` registry entry 는 **미등록** — behavioral pattern 만 preserve, 미wired 정직 기재.)

### §결정 11 — Code-level write-time semantic truth verify (2 sub-scope)

super-class scope 가 Code-level write-time discipline 으로 확장된다(§결정 10 governance artifact write-time 과 disjoint — 본 §결정 = 코드 artifact write-time).

- **§결정 11.A — Test code production binding verify**: bug-fix test = real production code source/exec 의무(sed-extract real fn, NOT inline hand-copy — inline-copy = tautology / zero regression binding). (1) DeveloperPL/QADev: real artifact source/exec(bash fn `sed -n '/^funcname() {/,/^}/p'` → source; NEVER re-type) (2) discriminating-fixture: sed-substitute bug INTO extracted real fn, assert RED (3) CodeReviewPL audit: existence-only guard + inline body + hand-written `*_masked`/`*_mock` tautology smell grep (4) acceptance: production fix revert → test RED, 잔존 GREEN = tautology.
- **§결정 11.B — Script error visibility audit**: script `2>/dev/null` 가 success/failure 보고하며 real error 마스킹 = mis-diagnosis amplifier META-ROOT. (1) 리소스 create/state change 보고 script 는 `2>/dev/null` 금지(error path) — `err=$(cmd 2>&1)` 로 stderr capture + failure verbatim surface. `2>/dev/null` = benign expected-noise(`command -v` probe 등)만 (2) root-cause 진단 = RAW signal(run log, NOT script summary) 우선 (3) CodeReview/SecurityTest audit: `Grep '2>/dev/null' scripts/**` resource-creating/state-changing command flag.

### §결정 12 — RequirementsPL + retro-time verify (2 sub-scope)

super-class scope 가 (a) RequirementsPL §2.1 verified-state mandate strengthening + (b) retro-time empirical verify 로 확장된다(write-time-only → write-time + retro-time lifecycle).

- **§결정 12.A — Issue body §2.1 verified state table mandate strengthening**: Orchestrator 가 follow-up CFP Issue body author 시 RequirementsPL spawn prompt MUST include verify-before-trust mandate — (1) cited lint output 를 worktree 직접 재현 (2) cited line number direct Read(parallel-merge 후 shift 가능) (3) cited gh-side state direct probe (4) cited path direct existence check. §2.1 verified state table mandatory(`issue_origin: orchestrator_authored_followup` 의무). §1 verbatim Issue(immutable) + §2 verified state(downstream drive) 양 layer 보존.
- **§결정 12.B — Retro-time wave_defer empirical verify**: Story 가 sub-scope 를 Wave 2/3 follow-up 로 defer 시 rationale("will auto-resolve via mechanism X")를 retro time 에 empirical verify 의무(Story-write time 가정 금지). deferral reason 이 hypothesis 인 경우 FALSE 가능성 검증 — 확인 시 follow-up = precautionary(deprioritize 가능) / 반증 시 genuinely required(priority 격상 + root cause re-diagnose).

### §결정 13 — GitOps verify-before-trust discipline (3 sub-scope)

super-class scope 가 GitOps coordination layer 로 확장된다.

- **§결정 13.A — Main drift bypass audit pattern**: wrapper PR 이 pre-existing main drift 를 inherit 시 표준 hotfix-bypass labels + `[bypass-justification]` audit comment 적용 — (1) pre-merge: 각 failing non-required check 를 CFP-introduced vs pre-existing main drift 로 분류(direct git diff) (2) 표준 hotfix-bypass label gh CLI 적용 (3) `[bypass-justification]` marker comment(per-finding root cause + verify-before-trust evidence + ADR-024 audit trail cross-ref) (4) PMO retro pattern_count tracking(≥ 2 same drift class = ADR escalation candidate).
- **§결정 13.B — HEAD SHA pin step 0**: async multi-agent coordination 안 branch artifact verify 시 — (1) step 0: `gh api repos/<owner>/<repo>/commits/<branch> --jq '.sha'` 로 current HEAD 해결 후 pin (2) `?ref=<pinned-sha>` 로 content verify(mid-chain SHA / agent self-claim SHA blind verify 금지) (3) incremental commit signal 시 explicit HEAD re-resolve (4) stale REJECT correction = process error → 신속 withdraw.
- **§결정 13.C — Branch protection 환경 worktree cleanup 순서**: main branch protection active repo 에서 — (1) Option 1(Merge Locally) 제시 금지 (2) Option 2(Push + PR) 선택 후 worktree 는 PR merge 확인 후 정리 (3) merge 확인 = `gh pr view <number> --json mergedAt` 또는 사용자 확인 (4) plugin-codeforge repo 항상 적용 + consumer 권장.

### §결정 14 — PMOAgent retro batch closure pattern

Multi-CFP retro emission → batch-create simultaneously + sequential doc-only fast-path execution single session 패턴을 codify 한다(workflow pattern reusability — 연속 Story 의 retro 를 한 세션에 batch 처리).

### §결정 15 — Issue body stale-claim super-class verify-before-trust write-time pre-screen

Orchestrator/lane 가 Issue body 를 author 할 때 4 sub-pattern closed-set 의 stale-claim 을 write-time 에 pre-screen 한다: (a) PR #NNNN merge state stale / (b) CFP-NNNN MERGED/CLOSED state stale / (c) count number stale("X VIOLATIONs" / "Y defect" / "pattern_count Z") / (d) sister carrier origin claim stale("CFP-NNNN carrier"). §결정 9(amendment-number sub-class)의 super-class. mechanical wire(`issue-body-claim-pre-screen`, presence-lint + code-span / quoted-text / templates/** / §9 transcript EXEMPT guard)는 wired.

### §결정 16 — resource-safety-claim ↔ proof-link write-time 정직 discipline

governance/보안 tooling(evidence-check 게이트·보안 script·워크플로 YAML)의 **docstring + inline 주석 + workflow YAML 주석**에 resource-safety/복잡도/DoS-guard 안전성-claim(closed-set: catastrophic backtracking 0 / ReDoS-safe/free / DoS 가드 / resource exhaustion 방어 / scan cap = 작업량 bound / nested quantifier 0 / injection-safe 등)을 쓸 때, 작성 주체는 (a) **paired proof-reference**(reproducer / wall-clock 벤치마크 / 복잡도 회귀 self-test 링크) 동반, **또는** (b) **honest-ceiling downgrade**("bounded degradation, 임의 입력 무해 아님")를 수행한다. 무증거 안전성 단정 금지.

2-layer 착지: **Layer 1**(행위 mandate) = write-time declaration(SecurityArchitectAgent / DeveloperAgent / QADeveloperAgent / InfraEngineerAgent roster/skill prose) + 리뷰 falsify. **Layer 2**(artifact presence lint, warning-tier) = 안전성-claim ↔ paired proof-ref/ceiling 의 **presence** 정적 검사(claim 감지 + proof-ref/ceiling 둘 다 부재 → FLAG). mechanism = §결정 15/§결정 11 presence-lint 답습(신규 CLASS 아님). born-safe 4-axis DoS bound(리터럴 substring 우선 nested-quantifier 0 / index-advance O(n) tokenize / per-physical-line length truncate / islice read cap)로 자기참조 DoS 회피. 5-piece mechanical wire(Python SSOT + thin wrapper + byte-identical workflow pair + discriminating self-test + registry warning-tier entry)는 wired·active.

**honesty ceiling(ADR-151 §결정 7 상속, presence ≠ truth)**: lint 은 proof-ref/ceiling **presence** 만 검사하며 claim **참됨**은 미강제한다. "over-claim 완전 봉인" hard-claim 금지. detection(보안테스트 execution-backed probe) 존치.

## 결과

- ADR-073(Orchestrator cross-repo) + ADR-070(Codex external worker) disjoint super-class layer 로서 internal lane agent self-write write-time semantic truth verify 를 §결정 1 4-layer 표 공통 anchor 로 codify.
- §결정 2 scope(a-d) write-time verify + §결정 1 sub-scope 1-A~1-Z(26종, 1-W 제거 후 25 live) 로 authorship surface 확장. 공통 4-tuple primitive(source / execute / cross-verify / annotation)로 압축 표현(구 per-sub-scope 4-tuple 전문 = 동결 ADR-082 보존).
- §결정 3 정정 재귀 + ADR-067 cap 재사용 / §결정 4 citation ≠ assertion / §결정 5 provisional defer / §결정 6 known-limitation + EC-3 self-protection.
- §결정 9-16 amendment-신설 §결정 fold(§9 amendment-number verify / §10 ArchitectAgent / §11 Code-level / §12 RequirementsPL+retro / §13 GitOps / §14 PMO batch / §15 Issue body stale / §16 resource-safety).
- (−) 의미 무변경(semantic fidelity) 검증 oracle 은 기계화 불가(ADR-167 §결정 7 honest ceiling) — 담보 = no-substantive-change 선언 + 재제정 처분표 + 8-lane 리뷰 신구 대조. "완전 봉인" 류 hard-claim 없음.
- (−) mechanical_enforcement_actions 다수 = deferred-followup / declaration-only(각 sub-scope wired 상태 정직 기재). evidence-checks-registry owner_adr 실 re-home = Phase 2.

## 재제정 처분표 (disposition table — ADR-167 §결정 4(b) 필수 요소 (b))

> 구 §결정/amendment → 신 위치 매핑(zero-drop) + 신 규범문 유래(source-credit, zero-insertion). granularity = §결정-level. 처리 태그 = carrier-preserved / 기술정정 / obsolete제거. R4 앵커(ADR-082 절/헤딩/Amendment 번호)는 "구 앵커" 열 — 동결 ADR-082 에서 row 단위 spot-check(3470행 raw diff 무의미). N:1 = 본 건 supersedes N=1(ADR-082 단일).

### (1) 원 §결정 1-8 (ADR-082 최초 codify) → §결정 1-8 (번호 보존)

| 구 §결정 | 신 위치 | 태그 | 구 앵커 (ADR-082) | 비고 |
|---|---|---|---|---|
| §결정 1 (4-layer 표) | §결정 1 | carrier-preserved | `### §결정 1` | 4-layer 표 + sub-scope host. layer 3 owner = ADR-082 → **ADR-168**(SSOT 전이, 구조개선) |
| §결정 2 (scope a-d) | §결정 2 | carrier-preserved | `### §결정 2` | — |
| §결정 3 (정정 재귀 cap) | §결정 3 | carrier-preserved | `### §결정 3` | ADR-067 재사용 |
| §결정 4 (citation≠assertion) | §결정 4 | carrier-preserved | `### §결정 4` | — |
| §결정 5 (provisional defer) | §결정 5 | carrier-preserved | `### §결정 5` | — |
| §결정 6 (known-limitation) | §결정 6 | carrier-preserved | `### §결정 6` | rationale 의 Amd1 partial-stale 정정 fold(아래 Amd1 참조) |
| §결정 7 (scope e 분리) | §결정 7 | carrier-preserved | `### §결정 7` | scope 외 거부 |
| §결정 8 (per-area 분할 거부) | §결정 8 | carrier-preserved | `### §결정 8` | scope 외 거부 |

### (2) amendment 신설 §결정 9-16 + §결정 1 sub-scope

38 distinct amendment(effective_count 76 = dual-block 합산 artifact, distinct = 38)의 처분. **zero-drop 완결**(38 amendment + 1-A base = 39 entry).

| Amd | carrier | 신 위치 | 태그 | 구 앵커 (ADR-082) | 비고 (R3 사유 / G-item / wired) |
|---|---|---|---|---|---|
| 1 | CFP-841 | §결정 6 | **기술정정** | `## Amendment 1` / `### §결정 6` | rationale 1 partial-stale 정정(lane-self-write-ownership-matrix.yaml 실재 — registry 부재 아닌 cross-plugin 확장) fold. dated Wave 서사 제거 |
| 2 | CFP-1016 | §결정 1 sub-scope 1-B | carrier-preserved | `## Amendment 2` | Issue-body authorship pre-publish verify |
| 3 | CFP-1041 | **drop** → 관련 ADR ADR-085 | **obsolete제거** | `## Amendment 3` | cross-ref-only(규범 substance 0) — ADR-085 coordination axis disjoint complement. §결정 규범문 재기재 불요, 관련 ADR 로 흡수 |
| 4 | CFP-1058 | **drop** → 1-G pointer | **obsolete제거** | `## Amendment 4` | ADR-RESERVATION `amendments_reserved[]` schema cross-ref. Amd17(1-G)이 schema codify supersede → 별도 규범문 불요(schema = ADR-RESERVATION.md pointer) |
| 5 | CFP-1110 | §결정 1 sub-scope 1-C | carrier-preserved | `## Amendment 5` | lane PL spawn prompt user-utterance verbatim anchor |
| 6 | CFP-1198 | §결정 9 | **기술정정** | `## Amendment 6` / `### §결정 9` | §결정 9 신설. Amd7 양방향 확장에 흡수 → §9 현행 최종형(forward+backward)만 기재, forward-only Wave 1 중간 상태 제거(모호 해소) |
| 7 | CFP-1312 | §결정 9 | carrier-preserved | `## Amendment 7` | §9 양방향 확장(Amd6과 fold, 현행 최종) |
| 8 | CFP-1329 | §결정 10 (10.A-D) | carrier-preserved | `## Amendment 8` / `### §결정 10` | ArchitectAgent write-time discipline 4 sub |
| 9 | CFP-1330 | §결정 11 (11.A/B) | carrier-preserved | `## Amendment 9` / `### §결정 11` | Code-level write-time 2 sub |
| 10 | CFP-1332 | §결정 12 (12.A/B) | carrier-preserved | `## Amendment 10` / `### §결정 12` | RequirementsPL §2.1 + retro-time |
| 11 | CFP-1338 | §결정 13 (13.A-C) | carrier-preserved | `## Amendment 11` / `### §결정 13` | GitOps 3 sub |
| 12 | CFP-1339 | §결정 14 | carrier-preserved | `## Amendment 12` / `### §결정 14` | PMO retro batch closure |
| 13 | CFP-1390 | §결정 10.D 부속 | **obsolete제거(부분)** | `## Amendment 13` | §10.D META Wave 2 `meta-self-application-wire` registry entry **미등록**(G1). behavioral pattern 은 §10.D preserve, Wave 2 진행 서사 제거 |
| 14 | CFP-1336 | §결정 1 sub-scope 1-D | carrier-preserved | `## Amendment 14` | cross-repo label-write authority verify |
| 15 | CFP-1437 | §결정 1 sub-scope 1-E | carrier-preserved | `## Amendment 15` | spawn prompt SHA-anchor pre-spawn pin |
| 16 | CFP-1436 | §결정 1 sub-scope 1-F | carrier-preserved | `## Amendment 16` | spawn-internal periodic origin re-pin |
| 17 | CFP-1435 | §결정 1 sub-scope 1-G | **기술정정(구조개선)** | `## Amendment 17` | 행위의무 4-tuple(a-d) preserve. RESERVATION schema 1.1(`amendments_reserved[]` enum) **verbatim 재게재 금지**(living SSOT drift 회피) → schema = `관련파일: ADR-RESERVATION.md` pointer(§결정 4(a) 구조개선, 실질 무변경). G5/D |
| 18 | CFP-1342 | §결정 1 sub-scope 1-H | carrier-preserved | `## Amendment 18` | Orchestrator §10 FIX Ledger resolution field verify |
| 19 | CFP-FU-A | §결정 1 sub-scope 1-I | **obsolete제거(부분)** | `## Amendment 19` | pre-spawn-prompt-finalize verify layer. collision renumber 서사(11th/12th occurrence) 제거, 행위의무만 |
| 20 | CFP-1559 | §결정 15 | carrier-preserved | `## Amendment 20` / `### §결정 15` | Issue body stale-claim 4 sub-pattern(a-d) |
| 21 | CFP-1578 | §결정 1 sub-scope 1-J | carrier-preserved | `## Amendment 21` | cross-repo worktree target authority verify |
| 22 | CFP-1601 | §결정 1 sub-scope 1-K | carrier-preserved | `## Amendment 22` | numeric claim write-time strict claim(6-dim closed-set) |
| 23 | CFP-1590 | §결정 1 sub-scope 1-L | carrier-preserved | `## Amendment 23` | spawn prompt fact verify. Wave 2 wire = 1-Z(Amd37) |
| 24 | CFP-1589 | §결정 1 sub-scope 1-M | carrier-preserved | `## Amendment 24` | own-author synthesis ↔ git commit gap verify |
| 25 | CFP-1612 | §결정 1 sub-scope 1-N | carrier-preserved (**wired·active**) | `## Amendment 25` | 1-K Wave 2 mechanical wire(governance docs scope). Wave 진행 서사 제거, 실현 상태만 |
| 26 | CFP-1637 | §결정 1 sub-scope 1-O | carrier-preserved | `## Amendment 26` | PR commit msg + PR body numeric claim strict claim |
| 27 | CFP-1647 | §결정 1 sub-scope 1-P | carrier-preserved (**선언만 미wired**) | `## Amendment 27` | 1-O Wave 2 wire SSOT — actual script 미wired 정직 기재(G-정직) |
| 28 | CFP-1648 | §결정 1 sub-scope 1-Q | **obsolete제거 (N:1)** | `## Amendment 28` | ADR dual-block parity 3-invariant lint. Amd30(FixA)+Amd32에 순차 supersede → **1-U 최종형만**(G3). Amd28 원서술 배제 |
| 29 | CFP-1683 | §결정 1 sub-scope 1-R | carrier-preserved (**미wired**) | `## Amendment 29` | mid-Story FIX-loop re-verification. 미wired 정직 |
| 30 | CFP-1688 | §결정 1 sub-scope 1-S | **obsolete제거(부분)** | `## Amendment 30` | ADR frontmatter block convention SSOT. FixB/C live, **FixA = 1-U supersede**(G3) → FixA 역사 배제, FixB/C만 |
| 31 | CFP-1684 | §결정 1 sub-scope 1-T | carrier-preserved (**미wired**) | `## Amendment 31` | PMOAgent retro write-time verify. 미wired 정직 |
| 32 | CFP-1734 | §결정 1 sub-scope 1-U | carrier-preserved (**wired·active 현행최종**) | `## Amendment 32` | dual-block gate(양 array non-empty ADR narrow) = 1-Q/1-S 최종형. **N:1 fold(Amd28+30+32 → 최종)**(G3) |
| 33 | CFP-1787 | §결정 1 sub-scope 1-V | carrier-preserved (**Wave 1 declarative**) | `## Amendment 33` | execution_context_state 5 sub-field declare. registry `execution-context-state-presence: deferred` → "Wave 1 declarative(Wave 2 상충 미확정)" 정직(G4, registry SSOT 신뢰) |
| 34 | CFP-1842 | **drop** → 1-Z 이관 | **obsolete제거** | `## Amendment 34` | orchestrator_spawn_prompt_fact_verify(1-W). **de-bloat 제거 유지·복원 금지**(ADR-058 §결정 5 ratchet). C1-C5 fact patterns 는 1-Z(handoff axis)로 이식(부활 아님). G7 |
| 35 | CFP-822 | §결정 1 sub-scope 1-X | carrier-preserved | `## Amendment 35` | subagent_self_report_post_task_verify |
| 36 | CFP-1613 | §결정 1 sub-scope 1-Y | carrier-preserved | `## Amendment 36` | amendment_array_ordering_convention(id ascending + reservation_date tie-break; `amendment_log[].sub_scope` field = mapping SSOT). G8: 향후 ADR-167 재배치 여지(본 Story 범위 밖) |
| 37 | CFP-2383 | §결정 1 sub-scope 1-Z | carrier-preserved (**Phase 1 SSOT 선언, Phase 2 미완**) | `## Amendment 37` | 1-L Wave 2 wire SSOT(PR-body-proxy presence-only lint). Phase 2 실배선 미완 정직(G-정직) |
| 38 | CFP-2646 | §결정 16 | carrier-preserved (**wired·active**) | `## Amendment 38` / `### §결정 16` | resource-safety-claim ↔ proof-link presence-lint(5-piece wired) |

### (3) base row (amendment 비귀속 — zero-drop 완결성)

| 항목 | 신 위치 | 태그 | 구 앵커 | 비고 |
|---|---|---|---|---|
| **1-A** (base) | §결정 1 sub-scope 1-A | 예외 등재 (G6) | `### §결정 1` layer 표 row 1 / `#### §결정 10.C` "1-A ... base" | Orchestrator cross-repo state verify(read-time base, ADR-073 precedent 파생). 어느 amendment 에도 귀속 안 됨 — zero-drop 완결성 위해 별도 등재(AC-4 / R1 유의) |

**공통 dated-history 제거(전 amendment 적용)**: `pattern_count N reach` / "META Nth applied case" 카운트 / SHA pin 값 / collision·reslot 서사 / label-registry version bump 이력 = 의무/금지/조건/예외 아닌 **저작 증적** → 본 ADR 본문 전량 제거(구 ADR-082 동결이 이력 담보). 이는 R3 문언 실질변경 아닌 dated-annotation 제거(재제정 허용 변경 = obsolete 제거).

## 관련 파일

- `CLAUDE.md` — verify-before-trust 4-layer 단락(구 ADR-082 인용 → ADR-168 canonical 정정 = Phase 2 역참조 정비)
- `docs/orchestrator-playbook.md` — §3.10(Codex Proactive Check) + §3.14(user-dialog) cross-ref
- `archive/adr/ADR-RESERVATION.md` — amendment-slot pre-reservation(§결정 1 sub-scope 1-G) SSOT + ADR-number row(82 `active → archived` / 168 신설)
- `docs/evidence-checks-registry.yaml` — owner_adr ADR-082 계열 7 entry → ADR-168 re-home(Phase 2)
- `templates/story-page-structure.md` — §2.1 verified-state codify(§결정 12.A) 역참조 정정(Phase 2)
- `scripts/lib/check_adr_amendment_threshold.py` — 재제정 완료 게이트 Superseded-skip 배선(Phase 2)

## 해소 기준

N/A — permanent governance policy. write-time self-write semantic truth verify super-class 상시 적용(is_transitional: false). ADR-064 §self-application top-down ratchet 정합(강화 방향 only — verify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과. **self-referential 주의**: 본 §해소 기준 부재(`N/A — permanent`) 선언 자체가 §결정 2 write-time verify 대상이 *아니다*(§결정 6 EC-3 self-protection).
