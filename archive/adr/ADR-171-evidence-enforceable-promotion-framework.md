---
adr_number: 171
title: Evidence-enforceable promotion framework — declaration → warning → enforce 점진 적용 SSOT (ADR-060 재제정)
status: Accepted
category: governance
date: 2026-08-04
carrier_story: CFP-2875
supersedes:
  - ADR-060
amends: null
reinterpretation: false  # ADR-167 §결정 1(b) — 본 ADR 은 ADR-060 실효 규범의 의미 무변경 재제정(restatement)이지 소급 재해석이 아니다. 신규 저작(재해석 marker false).
is_transitional: false
mechanical_enforcement_actions:
  # ADR-040 Amendment 3 §결정 7.A (A안 list[object]). 개별 entry 의 detect/workflow/tier SSOT = docs/evidence-checks-registry.yaml (frontmatter 중복 보유 금지 — B안 거부 사유 정합).
  # 구 ADR-060 fm 13건 중 registry `entries[].name` 실재 11건 승계. registry 미등재 orphan 2건(codex-network-scope-presence / parallel-anchors-checked-presence)은 불승계(drop) — ADR-167 §결정 4(a) obsolete 제거 범주, 처분표 (3) drop row 가시화 (무단 누락 아님).
  # 이행 진행 서사(Phase 1/2 scope 열거)는 dated — 동결 구본 ADR-060 fm 보존, 본 승계본 = 요지 1줄.
  - action: story-section-ownership
    status: warning
    progress_note: "CFP-722 (구 Amd13) carrier — lane-self-write-boundary mechanical-enforcement layer. blocking-on-pr 승격 target = §결정 27"
    target_section: §결정 27
  - action: increment-justification-presence
    status: warning
    progress_note: "CFP-2061-S1 (구 Amd16) carrier — 검사·ADR·스크립트 순증 PR 정당화 marker 게이트"
    target_section: §결정 30
  - action: governance-drift-detection
    status: warning
    progress_note: "CFP-2061-S4 (구 Amd17) carrier — 거버넌스 지표 7종 주기 재계측 + drift 이슈 자동 발행 cron"
    target_section: §결정 31
  - action: deferred-followup-reconcile
    status: warning
    progress_note: "CFP-2381 (구 Amd18) carrier — §결정 19 auto_blocking 라벨의 mechanical forcing function. self-entry = §결정 32 self-application 자연 회피"
    target_section: §결정 32
  - action: deferral-carrier-declared
    status: warning
    progress_note: "CFP-2591 (구 Amd20) carrier — registry 밖 declaration surface 의 no-TBD carrier-mandate lint (§7.9.E)"
    target_section: §결정 32
  - action: lane-count-ssot-consistency
    status: warning
    progress_note: "CFP-2426 (구 Amd19) carrier — canonical lane 수(10, ADR-125 Amd1) SSOT mechanical consistency"
    target_section: §결정 33
  - action: peer-completion-falsifiability
    status: warning
    progress_note: "CFP-2597 (구 fm Amd21) carrier — ADR-044 Amendment 6 §결정 12 축③ warning-tier 등록. owner_adr = ADR-044. 정직 상한: warning = ceiling (blocking 승격 = false assurance)"
    target_section: §결정 5
  - action: shell-test-exit-masking-detect
    status: warning
    progress_note: "CFP-2635 (구 fm Amd22) carrier — shell self-test 코퍼스 exit-masking·mock-seam false-coverage 정적 검출. honesty-ceiling source = ADR-151 §결정 7"
    target_section: §결정 5
  - action: infra-resource-undeclared-surface
    status: warning
    progress_note: "CFP-2700 (구 fm Amd23 미선언축) carrier — 인프라 자원 manifest drift 게이트. new-only ratchet(§7.9.D baseline) + §결정 32 surfacing(NO-FLIP). owner_adr = ADR-157"
    target_section: §결정 5
  - action: infra-resource-orphan-reconcile
    status: warning
    progress_note: "CFP-2700 (구 fm Amd23 orphan축) carrier — manifest dead declaration 검출. §결정 5 warning first → §결정 6 3-AND 승격. owner_adr = ADR-157"
    target_section: §결정 5
  - action: evidence-registry-structure-verify
    status: warning
    progress_note: "CFP-881 (구 Amd26) carrier — registry yaml 구조 무결성 3계층 게이트(문법/스키마 단정/중복키 surface). paired_owner_adr = ADR-151"
    target_section: §결정 5
related_stories:
  - CFP-2875  # 본 재제정 carrier (선제 — GREEN 유지 국면)
  - CFP-389   # 원 carrier (구 ADR-060 최초 codify, parent Epic CFP-388)
related_adrs:
  - ADR-060  # 재제정 대상 — 본 ADR 이 supersede. 구본 = 본문 byte-보존 in-place 동결(이력 담보), 실효 규범은 본 ADR 로 이관
  - ADR-167  # 재제정(compaction) ratchet SSOT — 본 건 트리거 = 선제(§결정 1 이원 트리거 미발화 상태의 자발 수행, effective 40 == grandfathered_at 40 GREEN 유지)
  - ADR-168  # 재제정 선례 실물 A(ADR-082→168) — registry owner_adr 재기재 선례 + §결정 16 resource-safety claim 증거 의무(구 ADR-082 Amd38 재제정)
  - ADR-170  # 재제정 선례 실물 B(ADR-039→170) — 구조 준거(번호 보존 restatement + 처분표 이원 앵커 + R2 해석우선순위)
  - ADR-133  # ADR 번호 atomic claim — 본 ADR 번호(171) 발급(§결정 4 fallback 경로 — 설계 lane push 금지)
  - ADR-050  # ADR-RESERVATION registry — row 171 append + warning mode prior art
  - ADR-058  # 직접 동인 — sunset criteria declaration mandate(§결정 8 CFP-B carrier) + §결정 5 약화 evidence-gate + §결정 8 모달 어휘 사전 owner
  - ADR-024  # branch policy — Amendment 3 hotfix-bypass:* audit-trailed exception channel + §결정 6.A per-entry namespace
  - ADR-063  # marketplace atomic invariant — plugin bump 동반 시 sync 의무(§결정 18)
  - ADR-037  # plugin version bump 분류 — governance behavior 변경 = MINOR / archive/** 비귀속
  - ADR-040  # Amendment 3 §결정 7.A/7.B — mechanical_enforcement_actions binding 규약
  - ADR-061  # Python script convention(thin wrapper + scripts/lib SSOT, NO heredoc) + Amd3 ReDoS guard — §결정 23 의 yaml-shell 영역 sibling
  - ADR-005  # templates ↔ .github workflow byte-identical pair
  - ADR-064  # §결정 1/5 CFP-scope-unitary + §결정 7 evidence-gated symmetric ratchet
  - ADR-068  # I-2/I-3 — §결정 25 ALLOWLIST guard placement intent + (구 §결정 29 축) declaration source
  - ADR-081  # Amendment 4 §결정 D1.D network_scope 4-tier enum — 구 §결정 28 축 declaration source(현재 registry 미등재 orphan — §결정 28)
  - ADR-044  # Amendment 6 §결정 12 — peer-completion-falsifiability 축③ 결정 SSOT(owner_adr)
  - ADR-151  # §결정 7 honesty ceiling — presence ≠ truth 상한 source(다수 entry paired)
  - ADR-157  # 인프라 자원 manifest D1~D5 결정 SSOT — infra-resource 2 entry owner_adr
  - ADR-125  # Amendment 1 canonical lane 수=10 — §결정 33 ground-truth + required contexts 무변경 선호
  - ADR-145  # forward-only + grandfather 산식 공동 근거(threshold-baseline GENERATED 헤더 쌍 인용 — ADR-145 무접촉, ADR-060→본 ADR 만 재지향)
  - ADR-153  # threshold-baseline 공집합 은퇴 방향 — 접촉 0(단조 shrink 경로 정합)
  - ADR-119  # research-before-claims + §결정 9 제안 필요성 게이트 — 검사연극 금지 정합
  - ADR-127  # 정식 플로우 비협상 + required 신설 0 ratchet(§7.9.G)
  - ADR-031  # §14 Lane Evidence Orchestrator monopoly — §결정 27 cross-ref only(재정의 0)
  - ADR-013  # dogfood-out — Story file cross-repo 경계
related_files:
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md  # framework schema SSOT (kind:registry, §결정 1)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # registries: versioning 추적 (§결정 2)
  - docs/evidence-checks-registry.yaml  # registry data 단일 SSOT (§결정 2) — 헤더 L4 + owner_adr 11 + paired_owner_adr 3 + carrier_adr 105 재지향 = Phase 2 (쌍-보존 예외 1건: :549-550 carrier_adr+carrier_amendment: 5 페어)
  - scripts/lib/check_adr_amendment_threshold.py  # ratchet 게이트 — ADR-060 리터럴 4개소(:5/:43/:390/:652) re-home = Phase 2 (:390 은 --write-baseline 재생성보다 선행 필수)
  - docs/adr-amendment-threshold-baseline.yaml  # ADR-060 행 제거 16→15 (--write-baseline 단일 writer 경유, 손편집 금지 — Phase 2)
  - archive/adr/ADR-060-evidence-enforceable-promotion-framework.md  # status: Superseded by ADR-171 전이 (frontmatter 최소행, 본문 byte-frozen — Phase 2)
  - archive/adr/ADR-RESERVATION.md  # row 171 신설(Phase 1, 본 Story) + row 60 active → archived 전이(Phase 2 — 요약표 enum, superseded 아님; amendments_reserved sub-tree adr_number 60/amendment_id 25 row 는 spent 무접촉)
  - plugins/codeforge-develop/agents/DeveloperPLAgent.md  # live anchor re-home (Phase 2)
  - plugins/codeforge-pmo/agents/PMOAgent.md  # live anchor re-home (Phase 2)
  - plugins/codeforge-requirements/agents/codex-proactive-check.md  # live anchor re-home (Phase 2)
  - docs/orchestrator-playbook.md  # live anchor re-home 8행 (Phase 2)
  - hooks/session-start  # live anchor re-home (Phase 2 — pretooluse-agent-spawn-gate / pretooluse-inline-write-gate 동반 3종)
  - docs/wording-dictionary.md  # 인용 re-home (Phase 2 — lint 로직 자체는 ADR-060 리터럴 비의존)
  - docs/wording-dictionary-baseline.yaml  # GENERATED — writer 리터럴 re-home 후 재생성 경로 (Phase 2, INV-R)
  - docs/doc-location-registry.md  # 인용 re-home (Phase 2)
  - docs/architecture/codeforge-family.md  # ADR-060 인용 3건 = 전부 dated 서사(구조 4영역 무변) — 번호 재지향만 (Phase 2)
# effective_count 재시작 = 0: 본문 `^#{2,4} Amendment` 헤딩 0 ∧ frontmatter amendments:/amendment_log: 키 자체 생략(양쪽 결합). ADR-167 §결정 5 재제정 신규 count 0 재시작 정합. (mechanical_enforcement_actions 는 count 산식 비대상.)
---

# ADR-171: Evidence-enforceable promotion framework — declaration → warning → enforce 점진 적용 SSOT (ADR-060 재제정)

## 상태

**Accepted** (2026-08-04 KST, CFP-2875 Phase 1 carrier).

**재제정 선언 (no-substantive-change — ADR-167 §결정 4(a) 필수 요소 (a))**: 본 ADR 은 **ADR-060(evidence-enforceable promotion framework)의 현행 실효 규범을 의미 무변경으로 깨끗한 신규 record 에 재작성한 재제정(re-enactment / recodification)**이다. 허용 변경 = **구조 개선·obsolete 제거·모호 해소·기술 정정 4종 한정**. 의무/금지/조건/예외의 규범 효력은 무변경이다. 의미 변경이 필요하면 재제정이 아니라 **별개 amendment 또는 신규 결정으로 분리**한다(본 Story 는 그런 항목을 발견하지 않았다). 구 ADR-060 은 **본문 byte 무변경 in-place 동결**로 잔존하며(이력 담보), `status: Superseded by ADR-171` 로 전이한다(전이 = Phase 2). 실효 규범의 단일 canonical source = 본 ADR-171.

**선제(preemptive) 국면 declare — 선례와 다른 유일 완료-bar 축**: 본 재제정은 ADR-167 ratchet 의 **3번째 실물 정산이자 첫 선제 케이스**다. 선례 2건(ADR-082→168 / ADR-039→170)은 게이트 RED 상태에서 착수한 해소형이었으나, 본 건의 착수 시점 게이트 판정 = **GREEN**(effective_count 40 == grandfathered_at 40, `check_adr_amendment_threshold` branch (iii) 경계 정확 착지 — 다음 amendment 1건이면 branch (ii) RED). 완료-bar = "RED → GREEN 해소"가 아니라 **"GREEN → GREEN 유지(무회귀)"**이며, `exit 0` 단독은 무변별(baseline 제거를 누락해도 GREEN)이므로 완료 증거 = 양성 증거 4점(Story CFP-2875 §5.3 AC-5). 사용자 directive verbatim: "급한 수정 시점에 재제정까지 떠안는 사고를 피하기 위해 … 선례와 동일 절차로 **선제 재제정**하라" / "재제정은 정확성이 곧 산출물" (Story CFP-2875 §1, 2026-07-31).

**fold 방향 declare**: 구 ADR-060 amendment 는 fm 26 entry 중 direction 표기 15건 = strengthen 13 · clarify 2 · **weaken 0** (미표기 11건은 direction 필드 도입 전 초기 entry — 전건 "ratchet 위반 0건 / 강화 방향" 명문 보유). 약화 fold 예외 없음 — 실효 규범은 "가장 넓게 확장된 최종 상태"의 단일 스냅샷으로 fold 가능하며 본 ADR 은 그 fold 를 §결정-level 로 수행한다. clarify 2건(구 Amd24 fact-correction / 구 Amd25 promotion provenance)은 정정된 사실·승격된 tier 의 **최종 상태만** 재기술한다.

## 본질 선언

codeforge 의 모든 mechanical governance check 는 **단일 framework** 를 따른다: **선언(declaration) → warning(비차단 관측) → enforce(차단) 점진 승격 + 증거 게이트(evidence-gated promotion)**. 신규 check 는 warning 으로 태어나고(§결정 5), 승격은 자동이 아니라 **누적 증거 3-AND 게이트**(§결정 6)를 통과한 별도 carrier 의 명시 결정으로만 일어나며, 운영 장애는 **audit-trailed bypass channel**(§결정 7/8)로 흡수한다. 이 본질이 충족되지 않으면 나머지 §결정 mechanism 을 몇 개 쌓든 의미 없다 — registry(§결정 1/2)·tier enum(§결정 3)·메타 검증(§결정 14/15/25)·개별 entry 등록 결정(§결정 4/21~33)은 전부 이 본질을 보조하는 scaffolding 이다.

## 컨텍스트

### 규범 원천 (구 ADR-060 승계)

ADR-058(CFP-387)이 ADR `## 해소 기준` 섹션과 `is_transitional` frontmatter 를 의무화했으나 **declaration only** 단계에 머물렀고, 그 §결정 8 이 기계적 강제(CI lint)를 CFP-B(잠정) 별도 carrier 로 분리했다. 구 ADR-060(CFP-389, 2026-05-11)이 그 **CFP-B carrier** — declaration 의 첫 evidence-enforceable mechanical check 도입 + 모든 후속 evidence check 가 따를 점진 적용 framework SSOT. 직접 동인 = ① ADR-058 declaration 의 moral governance 한계(작성자 자발 준수 의존) ② codeforge governance 진화 패턴(ADR-050 warning-mode prior art / ADR-024 Amd2 drift detection)의 정형화 ③ 사용자 brainstorming 합의(2026-05-11): "안전망 측정가능 종료" + "evidence-enforceable 점진 적용" + "velocity-normalized metric" ④ hotfix 시 정책 위반을 흡수할 audit-trailed exception channel 부재(사용자 ESCALATE 결정 = Option A `hotfix-bypass:*` label family). 외부 prior art = feature flag sunset(측정성 3-tuple) / 입법 sunset clause / CI/CD progressive enforcement(advisory → blocking 점진) — 상세 = 동결 구본 컨텍스트.

### 재제정 대상 · fold 소스 구조

구 ADR-060 은 3007행 / fm `amendment_log` 26 entry / 본문 ratchet-매칭 Amendment 헤딩 40(H2 19 + H3 21) / `effective_count = max(40, 26) = 40` record 다. 결정 번호 공간 = **자체 `### 결정 1~12` + amendment 신설 §결정 13~34 + §7.9.A~H sub-절**(비연속 — §결정 13~18 은 구 Amd1·2 신설, 19~26 은 구 Amd6~12 신설, 27~33 은 구 Amd13~19 신설, 34 는 구 Amd21(CFP-2678) 신설, §7.9 는 구 Amd20 신설). 헤딩-fm 표면 간 pre-existing drift 2종을 실측 그대로 기록한다: ① 본문 헤딩 40 > fm 26 (parity 게이트 forward-only 설계상 영구 미발화 — 본 재제정이 건드리지 않음) ② 본문 `Amendment 21` 헤딩(CFP-2678)과 fm `amendment: 21`(CFP-2597)은 **carrier 가 다른 별개 identity**(헤딩-단독 1건 + fm-단독 8건 — 처분표 (1)-보충 참조). 구본 amendment 의 큰 비중(§결정 21·22·24·25·27~33 + 신규-§결정-0 등록 5건)은 "N번째 warning-tier entry 등록" 서사이며, 그 entry 들의 **현행 SSOT 는 이미 `docs/evidence-checks-registry.yaml`**(§결정 2)이다 — 등록 이력·entry yaml 사본은 신 본문에 재기재하지 않고(중복 표면 제거) 처분표 + 동결 구본이 담보한다. 이것이 40 → 실효 규범으로 접히는 주된 fold direction 이다.

### 해석 우선순위 조항 (R2 — no-substantive-change presumption)

본 ADR-171 의 문언과 구 ADR-060 규범이 상충하는 것으로 보일 때, **재제정 처분표(아래 §재제정 처분표)에 명시 변경으로 표기된 지점 외에는 구 규범의 의미가 우선**한다(no-substantive-change presumption). SSOT 지위 자체는 ADR-171 이 보유하되, 이 우선순위는 **상충 해소 한정 semantics** 이며 이중원본을 뜻하지 않는다 — 구 ADR-060 은 이력 담보로 동결 잔존할 뿐 규범 source 가 아니다. 재제정 처분표는 재제정 후에도 코드·문서의 "ADR-060 §결정 N / Amendment M" 인용을 신 위치로 해소하는 **영구 참조 해소 자료(lookup)**로 기능한다.

## 결정

> 번호 보존 restatement — 생존 §결정은 ADR-060 원번호를 유지한다(§결정 5 는 그대로 §결정 5, §7.9.D 는 그대로 §7.9.D). 외부 인용("ADR-060 §결정 N" — 최다 anchor 쌍 = §결정 5/6)은 번호 무변으로 "ADR-171 §결정 N" 재지향만으로 해소된다. 재번호 금지.

### 결정 1 — Framework SSOT 위치 = `docs/inter-plugin-contracts/evidence-check-registry-v1.md`

evidence-enforceable framework 의 schema doc + 운영 룰 = **kind:registry** entry. 위치 = `docs/inter-plugin-contracts/evidence-check-registry-v1.md`. 분류 근거: ADR-058 §결정 8 declaration 을 mechanical 검증 가능한 cross-cutting protocol 로 변환 → kind:contract(lane plugin 간 typed schema) 아닌 kind:registry(wrapper-owned cross-cutting protocol) 정합. 기존 kind:registry(`comment-prefix-registry-v1` / `fix-event-v1` / `label-registry-v2`)와 동일 위치 + 동일 lint chain. `inter-plugin-contracts/MANIFEST.yaml` 의 `registries:` 블록에 등재.

### 결정 2 — Registry data = `docs/evidence-checks-registry.yaml` (single SSOT)

본 framework 의 모든 evidence check entry 는 단일 yaml `docs/evidence-checks-registry.yaml` 에 정의한다. schema = `evidence-check-registry-v1.md` SSOT. MANIFEST.yaml `registries:` 블록은 **versioning 추적 only** — data 자체는 yaml. **Registry data = single SSOT**: entry 의 detect_command / workflow / current_tier / promotion_criteria / recurrence / owner_adr / carrier_adr / introduced_by 등 entry-level 사실의 현행값은 registry 가 유일 원본이며, ADR 본문·frontmatter 는 그 사본을 보유하지 않는다(ADR-040 Amendment 3 §결정 7.A binding 은 entry **name 참조**만).

### 결정 3 — 4-tier enforcement enum + `current_tier` required + surfacing qualifier

evidence-checks-registry.yaml 의 각 entry 는 `current_tier` 필드를 **required** 로 보유한다(구 Amd2 가 optional → required 전환 deliver — schema v1.1). enum:

| tier | 동작 | branch protection 영향 |
|---|---|---|
| `warning` | continue-on-error 또는 non-required check. PR comment / job summary 경고만. | required_status_checks.contexts 미부착 |
| `blocking-on-pr` | required check. PR merge 차단. **단 surfacing qualifier 참조** | contexts 부착 — surfacing sub-mode 는 예외 |
| `blocking-on-merge` | post-merge guard (예: phase-gate-mergeable). PR open 단계는 통과, merge 시점 차단. | contexts 부착 |
| `hotfix-bypass` | bypass label 적용 PR 만 skip + audit comment 의무. label 부재 시 blocking-on-pr 등가. | contexts 부착 (+ bypass workflow) |

**surfacing qualifier (구 Amd20 §7.9.B reconciliation fold)**: `current_tier: blocking-on-pr` 자체는 required contexts membership 을 **함의하지 않는다**. surfacing sub-mode = **continue-on-error 제거만 · contexts 무변경**(red-X + sticky 표면화). required 편입은 별개 escalation 이다(ADR-125 required contexts 무변경 선호 — 편입 시 fail-closed narrowing override 근거 명시 의무, ADR-145 §결정 3 선례). tier 승격은 게이트의 강제 속성을 presence → truth 로 올리지 않는다 — **honesty ceiling 은 tier 와 독립**(ADR-151 §결정 7, 구 Amd25 재확인).

### 결정 4 — 첫 entry = ADR sunset criteria lint (`scripts/check-adr-sunset-criteria.sh`)

registry 의 첫 entry = `adr-sunset-criteria`(현행 entry 값 = registry SSOT — 본문 yaml 사본 비보유). lint script 책임 4건은 live 규범으로 승계한다: (a) ADR `is_transitional: true|false` frontmatter 존재 검증 (b) `## 해소 기준` 섹션 존재 검증 (c) is_transitional=false 시 "N/A — permanent policy" 1줄 또는 동등 형식 허용 (d) is_transitional=true 시 측정성 3-tuple(metric / who / how) 존재 검증 + 모달 어휘 1차 사전(§결정 9) 매치 검사. exit = 0(PASS) / 1(FAIL). bypass label 적용 PR 은 workflow 가 lint 실행 자체를 skip(label 기반 conditional skip).

### 결정 5 — 첫 적용 = warning mode (continue-on-error) + 신규 entry 등록 절차

**warning-first 원칙**: 모든 신규 evidence check 의 첫 도입 tier = `warning`(continue-on-error 또는 non-required, branch protection contexts 미부착). blocking 계열로 태어나는 entry 는 없다(manifest 기부착 entry 의 소급 분류 예외 = 구 §결정 13 dated 이행분).

**신규 entry 등록 절차 (현재형 — 구 Amd21(fm)~26 반복 관행의 fold)**: framework 의 자연스러운 사용 사례 entry 추가(신규 mechanism 0)는 **신규 §결정 없이** 등록 가능하다 — 본 §결정 5 warning-first + §결정 6 promotion gate 상속을 명시한 ADR-171 amendment(또는 owner ADR 의 amendment + `carrier_adr` 귀속)로 registry row append. 필수 동반: ① frontmatter `mechanical_enforcement_actions[]` entry(신규 lint carrier 시 — ADR-040 Amd3 §결정 7.A) ② owner_adr(정책 SSOT ADR) / carrier_adr(framework host) 분리 기재 ③ self-application 무한루프 회피 판정(§결정 32/33 선례) ④ 실 script + workflow + discriminating self-test 동반(Phase 분리 시 status 로 정직 표기).

**운영 가이드**: 첫 warning 출현 ≤ 14 days 동안 false positive ≥ 5건 발생 시 → workflow 일시 정지(admin only) + 본 ADR 보완 carrier 발의. solo-dev 환경(reviewer count=0) → 사용자 본인 적극 체크 의무(PR review 단계 warning manual 확인).

### 결정 6 — 승격 gate (binary, AND condition) + baseline-relative harmonization

warning → blocking-on-pr(또는 blocking-on-merge) 승격 조건 = **3 condition AND**:

- **(a) PR 누적 ≥ 20** (`pr_cumulative_min`): entry 도입 후 main PR merge 누적. bypass label 적용 PR 도 throughput 카운트에 포함.
- **(b) bypass 외 failure count = 0** (`failure_threshold: 0`): **measurement = 각 PR 의 final commit(= PR branch 최종 commit, merge 전략 무관) 의 lint 결과** 기준 — PR 진행 중 warning 을 해소하고 merge 시점 final state 가 PASS 면 failure 미카운트(warning mode 의 의도 = PR 진행 무차단 + final 정합 측정). **baseline-relative 재해석 (구 Amd20 §7.9.C fold)**: grandfather baseline(§7.9.D)을 보유한 entry 는 `failure = 0` 을 **new-debt failure = 0** 으로 판정한다 — baseline 동결분(pre-existing debt)은 failure 미카운트, baseline 이후 신규 유입만 집계(Clean-as-You-Code ↔ warning-first 조화).
- **(c) sibling Story merged** (`sibling_dependencies`): per-entry 의존 sibling 의 main merge 완결. 현행 값 = registry per-entry field SSOT. 관행 2종 승계 — 폐기된 carrier 는 replace 아닌 **append 보존**(폐기 history 가시화) / **self-carrier 제외**(자기 promotion gate 평가 trigger 가 자기 PR merge 인 tautology 회피).

승격 carrier(별도 CFP — 자동 transition 아님, governance 보존)의 evidence 산출물 6종 의무: (i) GitHub Actions 누적 run 이력 URL (ii) bypass 외 failure count = 0 증빙 (iii) PR 누적 ≥ 20 카운트 증빙 (iv) **GitHub Actions outage runbook**(enforce 진입 시 외부 의존 영향 분석 + manual fallback path) (v) **audit comment author 검증 lint**(comment author = `github-actions[bot]` 검증 — spoofing 차단, §결정 8) (vi) **sticky comment pattern**(at-most-once 보장, §결정 8). 6 산출물 부재 시 승격 carrier PR block. 자동화 카운터 인프라는 후속 carrier 책임 — 본 ADR 는 gate 정의만 제공. 승격 실물 선례 = resource-safety-claim-proof-presence(구 Amd25 — 3/3 MET + surfacing flip, registry `promoted_by`/`promoted_date` provenance field 가 이력 SSOT).

### 결정 7 — Hotfix bypass channel = `hotfix-bypass:*` label family (audit-trailed exception)

운영 장애 hotfix 가 정책 위반을 강제하는 경우의 audit-trailed exception channel:

- **label naming**: `hotfix-bypass:<entry-name>` family — **per-entry namespace 한정**(registry entry `bypass_label` 필드, ADR-024 Amendment 3 §결정 6.A). 단일 global bypass label 금지(§대안 E 거부 승계 — scope 통제).
- **권한자**: repo admin only(solo-dev = 사용자 본인). **PR 경유 의무 유지**: bypass label = lint skip only — push/merge 경로는 PR 경유 유지(ADR-024 §결정 6 + enforce_admins 호환).
- **audit 전용 채널 — 정책 회피 등록 차단 (구 Amd3 sharpening fold)**: `hotfix-bypass:*` 는 운영 장애 hotfix 의 일회성 exception 통로이며, 정책 위반을 회피하는 영구 등록 채널이 아니다(ADR-064 §결정 5 ratchet 정합). label 부착 PR 마다 audit comment 자동 발의 + audit log 집계 의무(§결정 8). enforce 승격 carrier 진입 시 bypass 적용 PR 누적 회수(`bypass_pr_count`)가 evidence 검토 대상.
- **label-registry-v2 등재**: 신규 bypass label = label-registry-v2 entry 동반(family member 등재 — 현행 member 목록 SSOT = label-registry-v2).

### 결정 8 — Audit trail schema

bypass label 적용 PR 마다 GitHub Actions bot 가 PR comment 1개 자동 append. comment body schema(단일 textual form, CI-parsable):

```
[hotfix-bypass-audit] PR=<number> label_applied_by=<user> reason=<bypass_reason_textbox> ADR_files=<comma-separated-paths> timestamp=<ISO8601>
```

`reason` = PR description 내 `### Bypass reason` 섹션 본문(workflow 추출, 부재 시 PR block). `timestamp` = ISO8601 UTC(Z suffix). **Re-entry 안전망**: bypass PR 의 변경 ADR 가 sunset criteria 누락 상태면 audit comment 에 `[sunset-criteria-deferred]` 태그 + 후속 보완 Issue 자동 발의. **Audit assertion lint**: `scripts/check-bypass-audit-comment.sh` — bypass label 부착 PR 의 audit comment 1+ 존재 검증. **author 검증 + sticky at-most-once**: warning mode 단계 = comment 존재만 검증(advisory) — enforce 승격 carrier 가 author = `github-actions[bot]` 강화 검증 lint(§결정 6 (v)) + sticky comment pattern(find-then-upsert, at-least-once → at-most-once, §결정 6 (vi))을 의무 도입한다. 실배선 실물 = deferred-followup-reconcile self-entry carrier trio(§7.9.F).

### 결정 9 — 모달 어휘 1차 사전 = ADR-058 §결정 8 의 4 표현 only

registry `modal_anti_pattern_dictionary.version: "1.0"` 의 4 표현 verbatim: "안정화되면" / "임시" / "한시적" / "until further notice". 확장 어휘는 별도 carrier 가 `dictionary_version: "1.1"` MINOR bump 로 수행한다. **amendment chain SSOT 위치**: dictionary 확장의 default = **ADR-058 amendment**(§결정 8 이 declaration SSOT owner — 본 framework 는 mechanical carrier 로서 verbatim 재인용) / framework 자체 변경 동반 시만 본 ADR amendment. registry field 는 version 추적만 — 언어 정의 SSOT 아님. **substring → word boundary 전환 의무**: v1.0 = substring match(conservative — false positive 감수). v1.1 확장 도입 시점에 word boundary regex 전환 의무(한국어 morpheme-aware tokenizer 또는 ASCII fallback).

### 결정 10 — velocity-normalized metric (throughput 독립)

승격 gate 의 metric = "20+ PR 누적 무사고" — Story 수 / 일자 / sprint 의존 X. 근거: codeforge wrapper repo throughput 가변(solo-dev, dogfood + consumer 혼재) → sprint-주기 metric 은 throughput 변동 시 의도와 어긋남. PR 누적 = 변경 누적의 직접 신호(false positive 검증 표본 수 보장). bypass label PR 도 throughput 카운트 — bypass 빈도 자체가 throughput 의 일부, 별도 metric 분리 불필요.

### 결정 11 — Framework SSOT 자체는 영구 정책 (sunset 불가)

본 ADR 자체 분류 = `is_transitional: false`(permanent policy carrier — ADR-058 §결정 6 self-defeat 회피 정합). 본 ADR 의 효력 종료 조건 = **본 ADR 의 supersede** 또는 codeforge 의 evidence-enforceable governance 자체 폐지(recursive sunset 무한 후행 회피). 구 ADR-060 → 본 ADR-171 재제정이 바로 그 supersede 경로의 실물이며, framework 를 폐지하지 않고 record 만 교체한다 — 본 §결정의 지위는 신 record 에 그대로 승계된다. 단 본 framework 의 **개별 evidence check entry**(registry row)는 individual 하게 sunset 가능: entry deprecate → registry row `status: deprecated` 또는 row 삭제 / enforce 전환 = entry-level mode transition(framework SSOT 자체 sunset 아님).

### 결정 12 — Declaration + first mechanical check 일체화 (CFP-B carrier — 이행 완료 현재형)

구 ADR-060 은 ADR-058 §결정 8 의 CFP-B(잠정) carrier 로서 declaration(framework SSOT) + first mechanical check(ADR sunset lint)를 일체 도입했고, 후속 확장(인벤토리 backfill / 4-tier 정식화)은 별도 carrier 로 분리해 전부 이행 완료됐다(구 Amd1·2 정정 포함 — 최종 carrier chain 의 현행값 = registry `sibling_dependencies` field). 본 §결정은 그 이행-완료 상태를 현재형 invariant 로 재기술한다: **framework 확장은 carrier 분리 원칙을 따른다** — declaration·mechanical check·retroactive backfill 을 한 Story 에 번들하지 않는다(ADR-064 §결정 5 CFP-scope-unitary 정합).

### 결정 13 — 인벤토리 backfill SSOT (이행 완료 + scope 한정)

구 Amd1 이 기존 ad-hoc evidence check 의 4-criteria(detect_command + workflow + owner_adr/contract + tier signal) 전수 inspect 로 그룹 A(등록) / 그룹 B(보류 — owner_adr 정합 ADR 부재 등) / 그룹 C(등록 제외 — sub-utility / consumer-only) 분류를 확정하고 registry row append 를 이행 완료했다. **현행 인벤토리의 SSOT = registry**(entry 증감·tier 변경은 registry 가 유일 원본 — 시점 스냅샷 표는 동결 구본 보존). live 규범으로 승계하는 것:

- **scope 한정**: 후속 framework entry 는 각 carrier ADR / Story 가 자체 registry row 등록을 책임진다(인벤토리 표의 재열거 대상 아님).
- **그룹 B 처리 원칙**: owner_adr 정합 ADR 미존재 entry 는 등록 보류 — owner 도입(또는 owner_adr=null schema 확장) 후 등록.
- **그룹 C consumer-only bullet = SSOT 참조 단일화**(§결정 34): consumer-only workflow 목록의 authoritative SSOT = `.github/workflows/invariant-check.yml` 의 `CONSUMER_ONLY_WORKFLOWS` bash 배열 — 본 ADR 은 사본 enumeration 을 보유하지 않는다.

### 결정 14 — 메타 검증 2축 분리 (anomaly / schema) + 현행 실물

메타 lint 는 scope 가 다른 2축으로 분리한다(구 Amd1 §결정 14 신설 + 구 Amd2 정정): **메타 anomaly detection**(registry 미등록 신규 evidence-enforceable 패턴 자동 발견 — inventory 축) vs **메타 schema/구조 validation**(registry yaml 자체의 schema·구조 정합 — data 축). 이행 이력: anomaly 축은 구 Amd11(CFP-442)이 deliver 했으나 그 산출물(`evidence-registry-anomaly` entry + script)은 2026-06-10 de-bloat 로 은퇴했다(§결정 25). **현행 live 실물 = data 축의 `evidence-registry-structure-verify`**(구 Amd26, CFP-881 — 3계층: A 문법 safe_load / B 스키마 단정[최상위 allowlist·entries list·name non-empty unique·current_tier enum case-sensitive] / C 중복키 collecting UniqueKeyLoader surface. honesty ceiling = 구조만·presence ≠ truth, ADR-151 §결정 7 상속). anomaly 축의 재도입은 §결정 5 등록 절차를 따르는 별도 carrier 영역이다.

### 결정 15 — 메타 lint exit-code 3-tier semantics (framework-wide 관행)

framework lint 의 exit code 의미: **0 = PASS** / **1 = validation FAIL**(1+ violation — warning mode 는 continue-on-error 로 merge 무차단, blocking 승격 시 PR block) / **2 = meta-error**(tooling 오류 — yaml 파싱 실패 / 의존성 미설치 / 대상 file 부재 등, lint logic 실행 불가 상황의 분리 명시). 근거: meta-error 가 validation FAIL 로 위장되면 false positive rate 측정(§결정 5 운영 가이드 14d/5건 trigger)이 왜곡 — 3-tier 분리가 측정 무결성을 보장한다. 본 semantics 는 후속 게이트 다수가 상속한 framework-wide 관행이다(§결정 20/25/30/33 실증).

### 결정 16 — warning-tier bypass_label policy

- **warning tier** = 비차단이므로 bypass 의미 부적용 → `bypass_label` field = **optional**(omit 권고).
- **blocking-on-pr / blocking-on-merge** = bypass_label optional(운영 장애 채널 필요성 분리 평가).
- **hotfix-bypass tier** = bypass_label **required**(정의상 bypass channel SSOT).

### 결정 17 — Retroactive reclassification failure handling

`current_tier` enum membership 위반 발견 시(future drift / human error — enum 외 값 주입 등): 메타 구조 lint exit 1 + blocking 승격 상태면 PR block — **immediate fail**(tolerant mode 금지 — required 필드의 mechanical 효력 유지). warning mode 단계 = continue-on-error 로 merge 가능하되 violation 명확 표시 + 운영 가이드 trigger 적용.

### 결정 18 — Marketplace/sibling sync necessity

kind:registry 산출물(registry yaml / schema doc / MANIFEST)은 wrapper-owned — **sibling sync 불필요**(ADR-010 scope 외). 단 plugin.json version bump 동반 시 marketplace mirrored field sync 가 ADR-063 atomic invariant 로 의무(marketplace sync PR 선행 merge). `archive/**` 단독 변경은 plugin.json bump 비귀속(ADR-037 A2-3 / A2-6 면제).

### 결정 19 — Recurrence-based advisory promotion signal

registry schema 의 `recurrence:` field(count / last_occurrence / threshold / promotion_trigger — 구 Amd6, schema v1.2)가 machine-usable recurrence metric 을 제공한다. `recurrence.count >= recurrence.threshold` 도달 시:

- **advisory**(`promotion_trigger: advisory`): PR comment 만(warning tier 유지, blocking transition 없음). `[recurrence-threshold-reached]` marker.
- **auto_blocking**(`promotion_trigger: auto_blocking`): 별도 carrier Story 가 actual `warning → blocking-on-pr` 승격 평가 **의무**(자동 transition 아님 — governance 보존). 이 의무의 mechanical forcing function = §결정 32(carrier-부재 검출 — 라벨의 강제력 결합).
- **none**(default): count 누적만.

본 §결정 = §결정 6 승격 gate 의 supplementary signal — 3-AND 와 OR 관계 아님(additional advisory). actual transition 은 여전히 별도 carrier 의무. **warning *도입* 임계와 별개**: 본 signal 은 warning→blocking 승격용이며, warning 첫 도입은 §결정 5 소관(재발 임계는 advisory — PMO authority 재평가로 하회 도입 가능, §결정 33 pattern_count=2 실증).

### 결정 20 — Entry name ↔ workflow file naming convention

- **EXACT match(default)** / **partial match**(substring 자연 변형 허용) / **multi-job pattern**(단일 workflow 안 여러 job 이 별개 entry — entry name = job name) / **Conservative no-rename policy**(기존 entry 의 workflow rename 금지 — CI history + required contexts 영향 회피, 신규 entry 만 EXACT 권장).
- **Lint enforcement**(`scripts/check-evidence-registry-naming.sh`): workflow file 존재 검증 의무 + DRIFT(no match) entry = allowlist hardcode 의무(현행 allowlist = script SSOT) + `Retired` status entry skip + exit 3-tier(§결정 15).

### 결정 21 — `workflow-permissions-block-presence` 등록 (구 Amd8)

workflow yml top-level `permissions:` block 부재 mechanical lint — GitHub Actions least-privilege 정합(부재 시 GITHUB_TOKEN 전 scope 자동 grant → top-level 명시 + per-job override 패턴 강제). 등록·tier·bypass 현행값 = registry entry SSOT. 잔여 live 규범: **T1 base = `contents: read` top-level + 필요 job 만 conditional escalate**(스케줄 issue-create job 만 `issues: write` — least privilege, top-level escalation 금지). CFP-300 SHA-pinning 과 직교 결합(supply chain family — 두 정책 independent invariant).

### 결정 22 — `workflow-yaml-parse` 등록 (구 Amd9)

multi-line bash BODY heredoc 패턴이 yaml ScannerError / GitHub Actions Go parser `jobs:[]` silent fail 을 유발해 workflow 가 zero-coverage 로 도는 결함(6 file 실측 sentinel)의 재발 방지 게이트 — PyYAML safe_load + actionlint dual validation. 등록·tier 현행값 = registry entry SSOT. broken workflow = absent 와 동치이므로 본 게이트는 framework measurement 정당성(§결정 6 표본)의 전제다.

### 결정 23 — workflow yml BODY heredoc anti-pattern + 정상 패턴 SSOT

**금지(anti-pattern)**: `run: |` block scalar 안 `BODY="${VAR}` + 0-indent 3-backtick fence + 0-indent `${...}` interpolation 조합 — yaml scanner 의 block scalar 종료 모호성 유발(PyYAML strict ScannerError / Actions Go parser silent fail).

**권장(정상 패턴 3종)**: **(A)** printf format string + variable arg — `BODY=$(printf '%s\n\n```\n%s\n```\n\n%s' "$HEADER" "$LINT_OUT" "$FOOTER")`(single-quoted format 이 yaml scanner 영역 외) / **(B)** ANSI-C quoting — `BODY=$'...\n'"$VAR"$'...'`(fence 가 quoted scalar 안 포함) / **(C)** external script call — multi-line > 5줄 시 `bash scripts/emit-*.sh ... > /tmp/body.md` + `--body-file`(ADR-061 §결정 1 의 yaml-shell 영역 extension — escape 책임을 script 가 흡수).

lint enforcement = §결정 22 게이트. ADR-061 §결정 1(Python heredoc 금지)과 동일 root cause family 의 yaml-shell 영역 SSOT.

### 결정 24 — `bootstrap-labels-precondition` 등록 (구 Amd10)

consumer repo PR open 시 codeforge 필수 label set(phase:* / gate:* / type:* / hotfix-bypass:* / severity:* / audit:* / component:*) 부재 자동 감지 + `bootstrap-labels.sh` idempotent 호출 — PR-time precondition check pattern 의 baseline. 등록·tier 현행값 = registry entry SSOT. 잔여 live 규범: workflow 본문 = 외부 script 단일 호출(§결정 23 anti-pattern 차단) / chicken-and-egg 회피(warning tier + first-PR-ever 보호 + contexts 미부착) / PAT-loop prevention(`types: [opened]` filter + per-PR concurrency dedup) / PAT = ADR-066 정합 + GITHUB_TOKEN fallback(silent advisory degradation).

### 결정 25 — 메타 anomaly lint (`evidence-registry-anomaly`) — 등록 후 은퇴 (현행 상태 기록)

구 Amd11 이 메타 anomaly lint(sub-check 1 registry ↔ 인벤토리 parity + sub-check 2 신규 evidence-enforceable 패턴 4-criteria 후보 식별 + ALLOWLIST self-exempt 2-purpose[candidate false-positive 회피 ∧ start-up existence assertion — ADR-068 I-3 unconditional/conditional guard placement 명시] + exit 3-tier)를 deliver 했다. 그 산출물(entry + script)은 **2026-06-10 de-bloat 로 은퇴** — 현행 registry 에 동명 entry 부재. 상세 scope 명세 = 동결 구본 보존. 잔여 live 규범: **anomaly(inventory) 축 ↔ structure/schema(data) 축은 disjoint**(§결정 14) — 후자의 live 실물 = `evidence-registry-structure-verify`. anomaly 축 재도입은 §결정 5 절차의 별도 carrier 영역.

### 결정 26 — KPI history accumulation 메커니즘 선택 결정 규칙 SSOT (구 Amd12)

**scope boundary**: 본 §결정은 **metric-sample history**(window 단위 누적 KPI 측정값 시계열)만 규율한다. scope 외 = ① gate-transition / lifecycle-status log(상태 전이 audit 기록 — metric 값 아님) ② 이미 별도 ADR/contract 가 owner 인 비-KPI 시계열. scope 외 데이터에 본 규칙을 적용하지 않는다(category error 방지) — 해당 KPI 에 metric-sample history 가 신설되면 그 시점에 새로 적용.

**결정 규칙 (decidable 입력 2변수 → deterministic 출력)**:

- `window_shape`: gate 판정 window 형태 — `rolling-multi-month` / `single-fixed-window`. 산정 priority = (1) registry 해당 entry `sunset_gate` window 표현(gate 판정 실 SSOT) → (2) KPI JSON `window_months` → (3) 모호 시 tie-break. **dual-window 불일치 시 registry `sunset_gate` window 우선(E-2)**.
- `entry_cardinality`: entry 구조·성장 특성 — `multi-field-or-unbounded` / `flat-bounded`. 선언된 schema field 에서만 도출(주관적 성장 추정 금지).
- **출력 1줄 규칙**: `window_shape == rolling-multi-month` **OR** `entry_cardinality == multi-field-or-unbounded` → **별도 append-only `docs/kpi/<kpi>-history.jsonl`**(+ snapshot `history_file` pointer + measure script `--history-out` idempotent) / 둘 다 아니면 → **embedded `"history"` 배열**.

**tie-break(E-1)**: 모호 시 **별도 jsonl**(테스트 격리·무한 확장성·diff-noise 최소 — 안전 방향). **E-2.1(governing window 자체 미해소)**: dual-window 불일치가 미정정 상태면 분류 = **보류(deferred)** + 잠정 jsonl 권고만(즉시 마이그레이션 강제 아님) — 최종 분류는 불일치 정정 follow-up 해소 후 재산정("정합 무변경" 단정 금지). **통일 key 정책**: 신규 KPI embedded 패턴의 history key 명 = `"history"` 강제(변종 key 신규 도입 금지) / 기존 KPI 는 grandfather(즉시 rename 강제 아님). **E-4**: history data 0건이면 패턴 변경 요구도 "trivially 정합"(follow-up 양산 방지). **rationale 요지**: jsonl = diff-noise 최소·테스트 격리·무한 확장 / embedded = 단일 file atomic read·단순성 — rolling·multi-field·unbounded 에서 jsonl 우월. **follow-up 경계**: 규칙이 정렬을 요구해도 실제 마이그레이션 실행(schema bump + script + workflow)은 각 독립 follow-up CFP(ADR-064 §결정 5 CFP-scope-unitary). 적용 시점 = 발효 후 신규/변경 KPI 부터 binding(retroactive 강제 아님). 3-KPI 최초 분류표(rate-limit-fallback = jsonl 정합 / retro-alert-pickup-rate = E-2.1 보류 / marketplace-drift-rate = scope 외)의 dated 도출 상세 = 동결 구본.

### 결정 27 — `story-section-ownership` 등록 (구 Amd13)

Story file per-section lane ownership matrix(`codeforge:lane-self-write-boundary` skill = normative SSOT)의 mechanical-enforcement layer — destructive rewrite incident(PR #441 +216/-850) 차단 forcing function. 등록·tier 현행값 = registry entry SSOT. 잔여 live 규범: ① **cross-ref only — ownership semantic 재정의 0건**(ADR-031 §14 monopoly + fix-event-v1 §10 monopoly + Orchestrator-owned delegate subagent 포함 정의는 각 원문이 ground truth) ② blocking-on-pr 승격 시 precondition = internal-docs CODEOWNERS 부재 해소(cross-repo bypass-authz path) ③ expedited promotion gate 는 encode 하지 않음 — §결정 6 STANDARD threshold(FUTURE labeled option 은 별도 carrier, ADR-064 §결정 1 정합).

### 결정 28 — `codex-network-scope-presence` — 등록 결정 · 현행 registry 미등재 (orphan 기록)

구 Amd14 가 ADR-081 Amendment 4 §결정 D1.D(`network_scope` 4-tier enum) 본문 확장의 mechanical enforcement layer 로 entry 등록을 결정했다(dual-binding 첫 사례 — declaration source ADR-081 / enforcement source 본 framework). **현행 상태**: Phase 2(실 lint script + workflow) 미이행(구 fm status `deferred-followup`) ∧ **registry 에 동명 entry 부재**(2026-06-10 de-bloat "고아 theater entry" 제거 이력 — 착수 전 기존 drift). 본 재제정은 이 orphan 을 fm `mechanical_enforcement_actions` 에 **불승계(drop)** 한다(처분표 (3) — ADR-167 §결정 4(a) obsolete 제거 범주). declaration 축 규범(4-tier enum·legacy boolean grace)은 ADR-081 Amendment 4 가 SSOT 로 잔존 — 게이트 재도입 시 §결정 5 등록 절차를 새로 따른다.

### 결정 29 — `parallel-anchors-checked-presence` — 등록 결정 · 현행 registry 미등재 (orphan 기록)

구 Amd15 가 ADR-068 I-2(cross-module propagation completeness) review-verdict layer realization Wave 3 로 entry 등록을 결정했다(3-state semantic: absent → WARNING / clean·matched → PASS. 5 pattern_type closed-set = review-verdict-v4 SSOT). **현행 상태**: registry 에 동명 entry 부재(orphan drift) → fm **불승계(drop)**(처분표 (3)). declaration 축 규범(I-2 + review-verdict-v4 `findings[].parallel_anchors_checked[]` schema)은 각 원문이 SSOT 로 잔존 — 재도입 시 §결정 5 절차.

### 결정 30 — `increment-justification-presence` 등록 (구 Amd16)

거버넌스 순증(검사·ADR·스크립트 신규 추가) PR 의 정당화 의무 게이트 — 약화 방향은 tier-downgrade 마커가 차단하나 순증 방향 정당화 강제가 공백이었던 경계를 메운다. 등록·tier 현행값 = registry entry SSOT. 잔여 live 규범: **trigger-path closed-set 4종**((a) registry entries row 신규 append (b) `scripts/check-*.{sh,py}` 신규 파일 (c) workflow yml 신규 파일 (d) `archive/adr/ADR-*.md` 신규 adr_number — Amendment append 제외) + **marker 형식** `[increment-justification] why=<...> blocks-or-replaces=<...>`(PR body line-start anchor + 2 요소 AND) + 3-state semantic(비대상 PASS / marker 존재 PASS / 누락 WARNING / setup exit 2) + self-meta loop 회피(self-exempt 채널 + 자가적용 marker 이중 부착).

### 결정 31 — `governance-drift-detection` 등록 (구 Amd17)

거버넌스 지표 7종(registry entry 수 / workflow 수 / 매-PR workflow 수 / shell 수 / shell LOC / ADR 수 / ADR byte) baseline 대비 상대 증가율 임계 초과 시 이슈 자동 발행 cron(advisory exit 0). 등록·tier·baseline 현행값 = registry entry + `docs/kpi/` SSOT. 잔여 live 규범: **dedup signature = sha256("governance-drift|metric|increase|bucket") — current_val 절대 제외**(포함 시 측정값 변동마다 signature 변동 → dedup 무력화·이슈 폭주) + cron 시각 분산(ADR-109).

### 결정 32 — `deferred-followup-reconcile` — §결정 19 auto_blocking 라벨의 mechanical forcing function (구 Amd18, §7.9.A 개정 반영)

§결정 19 의 auto_blocking 라벨은 "별도 carrier 가 승격 평가 의무" 선언만으로는 강제력 0 — 본 게이트가 "임계 초과 + auto_blocking + 전용 carrier 부재" entry 를 자동 검출해 forcing function 을 결합한다.

- **검출 1급 firing = 3-AND, status-agnostic**: `(recurrence.count >= recurrence.threshold) AND (promotion_trigger == "auto_blocking") AND carrier_absent(entry)` — status 라벨이 아닌 **실제 배선 결손** 기준(`status: Active` 인데 workflow 미배선인 entry 도 포착). warning-tier 라 broad-scope false positive 의 merge 차단 비용 = 0.
- **`carrier_absent` = OR 결합**: `detect_command` 경로 OR `workflow` 경로 중 하나라도 파일 ABSENT 면 carrier-incomplete. **경로 추출 = 닫힌집합 + fail-loud**: 단일 interpreter + 단일 파일 token 형태만 resolve — `null`/prose 마커는 검사 제외, 복합·모호 형태(`bash -c` / `A && B`)는 `UNRESOLVED` 분류 + warning(True/False 단정 금지 — 추정 회피). **workflow 2-root parity**: 값이 `templates/github-workflows/` 면 ADR-005 상 self-app `.github/workflows/` 동반 실존 확인(둘 중 하나 ABSENT = incomplete).
- **firing scope 외**: `promotion_trigger == advisory`(secondary informational 보고만 — §결정 19 advisory 의미 보존) / `warning_tier_initial` / threshold 미정의 entry / self-entry(carrier 실존 자연 PASS).
- **강제 action 3택**(flag entry 마다 택일): ① 배선 carrier 발의 ② `tier-downgrade-justification:` 근거 강등 ③ 폐기(de-bloat). **표면화 tier(구 §7.9.A 개정 최종 상태)**: 강제 action 의 표면 = `blocking-on-pr (surfacing)` Tier 1(continue-on-error 제거 = red-X + sticky, required contexts 미편입 — §결정 3 surfacing qualifier) — 단 **flip 은 baseline main 착지 후 별도 PR**(NO-FLIP: baseline 을 도입하는 PR 자신이 surfacing 이면 baseline 부재 상태에서 전 PR self-block — self-deadlock 회피). Tier 2(hard-required 편입) = FUTURE/OOS.
- **self-application 회피**: self-entry 는 처음부터 `status: Active` + 실파일(detect/workflow)을 동일 PR 동반 신설 → `carrier_absent == false` 자연 PASS(별도 self-skip 분기 불요).
- **discriminating self-test**: registry fixture 기반 — 검출돼야 할 entry 미검출 시 RED + 동일 workflow 내 self-validation test job(continue-on-error 미적용, mutation 생존 0).

### 결정 33 — `lane-count-ssot-consistency` 등록 (구 Amd19)

canonical 작업레인 수(10 — ADR-125 Amendment 1 정본 SSOT)의 분산 문서 사본 단조 유지 mechanical enforcement("registration 완료 ≠ enforcement 실효" 갭 봉합 — stale N 값 drift 2 Story 연속 leak 실증, pattern_count=2 로 warning *도입*은 §결정 5 소관·§결정 19 승격 임계와 무충돌). 등록·tier 현행값 = registry entry SSOT. 잔여 live 규범:

- **firing**: `stale_token_match(line) AND NOT allowlist_match(line)` — stale 매칭 **이후** allowlist 필터(역전 시 부정문 오검출). exit 3-tier(§결정 15). ReDoS-safe line-by-line(ADR-061 Amd3).
- **N-range = canonical-10 특정값 detection (documented-limitation)**: 미래 lane 증감 ADR-125 Amendment 는 N-range 정규식 갱신(+ fixture range 확장)을 그 Amendment 의 **REQUIRED mechanical-sync 항**으로 포함해야 한다.
- **allowlist 5축(channel-split — 토큰 아닌 syntactic channel 단위 면제)**: ①within-line 이중토큰(lane *plugin* count 별도 축 — 라인 전체 면제 금지, 잔여 재검사) ②negation(동일 라인 인접) ③history(date 행 / amendment_log span line-local boolean toggle — span 무한확장 금지 / 인용·버전이력) ④path(`archive/adr/**` 등) ⑤counterfactual(`만약` 가정 마커 — 마커 부재 단독 단언은 면제 아님).
- **self-application**: self-entry description 에 count 토큰(N≠10) 미포함 의무 + self-source 파일 SELF_EXCLUDE + 실파일 동일 PR 동반 신설.

### 결정 34 — 그룹 C consumer-only bullet: 사본 enumeration → SSOT 참조 단일화 (구 Amd21, CFP-2678)

§결정 13 그룹 C 의 consumer-only workflow bullet 은 **사본 enumeration 을 보유하지 않는다** — authoritative 목록 = `.github/workflows/invariant-check.yml` 의 `CONSUMER_ONLY_WORKFLOWS` bash 배열(안정 심볼 참조, line-number 하드코딩 금지). 둘째 사본이 없으면 drift 가 구조적으로 불가능(prevention-by-design — point-in-time snapshot 산문 mirror 가 SSOT 확장 4회를 미반영한 lag 실증에서 도출). ADR 본문에 개별 workflow 명 목록 재추가 = drift 재유입 → **금지(self-defending)**. parity lint 는 미채택 — 사본 제거 후 지킬 대상이 소멸해 vacuous(ADR-119 §결정 9 3문 게이트 FAIL, detection 대신 elimination).

### §7.9 — deferred-followup forcing-function 봉합 결정군 (구 Amd20 신설 — 번호 보존)

> 구 Amd20 이 §7.9.A~H 로 신설한 framework-wide 결정군. A/B/C 는 본 재제정에서 각 대상 §결정 본문에 fold 됐다(anchor 는 lookup 용으로 보존).

#### §7.9.A — §결정 32.D surfacing tier (fold into §결정 32)

`blocking-on-pr (surfacing)` Tier 1 도입 + NO-FLIP(self-deadlock 회피 — flip 은 baseline main 착지 후 별도 PR) + Tier 2 FUTURE/OOS — 최종 상태는 §결정 32 강제 action 절에 재기술 완료.

#### §7.9.B — §결정 3 reconciliation (fold into §결정 3)

surfacing qualifier: `current_tier: blocking-on-pr` 이 required contexts membership 을 함의하지 않음 — §결정 3 에 재기술 완료(실측 drift 소급 정합화 포함).

#### §7.9.C — §결정 6 harmonization (fold into §결정 6)

`failure_threshold = 0` 의 baseline-relative(new-debt failure=0) 재해석 — §결정 6 (b) 에 재기술 완료.

#### §7.9.D — grandfather baseline 메커니즘 (framework-wide)

new-only ratchet 이 필요한 게이트는 grandfather baseline 을 다음 **5요소 형판**으로 도입한다(이론적 근거 = SonarQube Clean-as-You-Code + betterer ratchet):

- **enumerated-freeze**: 도입 시점 대상을 snapshot 으로 열거 동결(locator + token + reason).
- **2-owner section**: 축별 소유 섹션 분리(예: gate_flags / declaration_surfaces).
- **single-writer gen tool**: 전용 생성 도구만 write(손 편집 금지 — DO NOT EDIT BY HAND). CI 는 gen 미호출(regen-and-diff-zero 게이트 신설 금지 — provenance drift 회피).
- **content_digest tamper-evident**: sha256 over canonical 내용(provenance/generated_at 제외) — 손 편집 tamper 검출.
- **monotonic shrink**: baseline 은 축소만(정리 시 subtract) — 증식 금지 ratchet.

준수 구현의 정확 인용(구 Amd24 fact-correction 반영): digest·shrink 실물 = `scripts/lib/check_deferred_followup_reconcile.py`(compute_content_digest / stored↔recomputed 불일치 검출 / grandfathered_ok NOT-worse 술어) + `scripts/lib/gen_deferred_followup_baseline.py`(single-writer, prune = shrink only). 형판 채택 게이트가 "재사용"을 주장할 때 그 의미 = **기제/패턴 축**(5요소 형판 답습)이며 코드 상속 축이 아니다 — 상속할 구현이 없는 채 "재사용" 주장 = hollow claim(코드로 상속된 실증 있음). legacy debt 는 별도 backward-triage carrier.

#### §7.9.E — carrier-mandate entry (no-TBD lint, `deferral-carrier-declared`)

deferral 선언 시 carrier CFP + registry 등재를 **필수화** — registry **밖** declaration surface(문서/워크플로/스킬)의 미해결 placeholder(미확정 TBD 마커 / 미발급 CFP 번호 / 미배선 FU 마커)를 grep-기반 검출 + registry cross-check(named carrier membership) + allowlist false-positive 차단 + baseline grandfather(new-only, §7.9.D). **declared→registered 강제 결합** — 선언만 하고 미등재인 silent debt 차단. (a) registry 안 FLAG 는 sibling `deferred-followup-reconcile`(§결정 32) 소관 — 두 축 **disjoint**. bypass_label 미신설(advisory 게이트 — attack surface 최소화).

#### §7.9.F — §결정 6 carrier trio (self-entry evidence_artifacts 실배선)

self-entry `deferred-followup-reconcile` 에 §결정 6 (iv)(v)(vi) 3종 실배선: outage runbook(`docs/runbooks/deferred-followup-reconcile-enforce-outage.md`) + author-verify lint(`scripts/check-audit-comment-author.sh` — presence-only spoof gap 봉합, warning mode 비차단) + sticky comment at-most-once(hidden marker find-then-upsert).

#### §7.9.G — ADR-127/ADR-024 amendment 불요 + honest forcing ceiling

Tier 1 surfacing 은 required contexts 를 회피 → ADR-127 required-check SSOT 무변경 + ADR-024 bypass invariant 미발화. **honest forcing ceiling**: surfacing 게이트는 hard block 을 미주장한다 — admin 우회는 구조적으로 가능(required 아님)하며, 우회는 audit + count 로 **관측만** 한다(mechanical 차단 아님).

#### §7.9.H — Cross-ref

§결정 19(forcing 대상 라벨) / §결정 3·5·6(qualifier·warning-first·gate harmonization) / ADR-061·ADR-127·ADR-024·ADR-063·ADR-058 — 관계는 각 §결정 본문에 내장 재기술 완료.

## 결과

- declaration → warning → enforce 점진 승격 + 증거 게이트 + audit-trailed bypass 라는 framework 본질(§결정 1~12)과, 그 위에 누적된 운영 규범(메타 검증 2축·exit 3-tier·naming·KPI history 규칙·forcing function·surfacing·grandfather baseline 형판 — §결정 13~34·§7.9)이 **단일 record** 로 재계보화 — 규범 효력 무변경.
- 구본 대비 정리: "N번째 entry 등록" 서사·entry yaml 사본·sibling chain 누적 나열·Mermaid 동기 서사·시점별 hotfix-bypass family member 순번 → **registry SSOT 참조로 단일화**(§결정 2 원칙의 자기 적용). dated 진행 서사·FIX 정정 이력·저작 증적 제거(동결 구본이 이력 담보). 구 Amd24 fact-correction 3건은 정정된 사실만 본문 반영.
- effective_count 40 → **0 재시작**(ADR-167 §결정 5) — 본문 Amendment 헤딩 0 ∧ fm amendment 배열 키 생략. threshold 게이트 baseline 은 ADR-060 행 제거로 16→15 단조감소(Phase 2, `--write-baseline` 단일 writer).
- (−) 의미 무변경(semantic fidelity) 검증 oracle 은 기계화 불가(ADR-167 §결정 7 honest ceiling) — 담보 = no-substantive-change 선언 + 재제정 처분표 + 8-lane 리뷰 신구 대조. "완전 봉인" 류 hard-claim 없음.
- (−) 역참조 re-home(registry 120개소 + 스크립트 4개소 + live anchor 문서군)은 **어떤 게이트도 검증하지 않는 순수 정확성 축**(owner_adr/carrier_adr 파싱 게이트 0 실측) — 누락은 조용히 통과하므로 정확성 담보는 Phase 2 bijection re-grep + 리뷰 축 전담.

## 재제정 처분표 (disposition table — ADR-167 §결정 4(b) 필수 요소 (b))

> **대사식(카운트 축)**: R = **40**(amendment 헤딩 — ratchet 산정 단위 전수. 이원 앵커 + H2/H3 레벨 명기) + **12**(자체 §결정 1~12) + **13**(fm mechanical_enforcement_actions — drop 2 포함 전건 row) = **65 row**. fm `amendment_log` 26 은 별도 블록이 아니라 (1) 블록의 **"fm" 열**로 흡수한다(effective_count = max(40, 26) — 합산 아님, 별도 블록 = 이중계상). 추가로 **(1)-보충: fm-단독 identity 8건**(ratchet-매칭 헤딩 무기여 — 카운트 비계상)을 명시해 amendment **identity 축**(fm 26 + 헤딩-단독 1 = 27) zero-drop 을 완결한다.
> 태그 enum = carrier-preserved / 기술정정 / 기술정정(구조개선) / 기술정정(부분) / carrier-preserved (inline fold into §결정 M) / obsolete제거. 이원 앵커 규칙: 신설형(전용 본문 헤딩 보유) = 본문 헤딩(+레벨) / in-place fold형(전용 헤딩 부재) = `amendment_log[N]` + fold 대상 §결정. 전 row 공통: no-substantive-change(NSC) 판정 열 — `Y` = 의무·금지·조건·예외 4축 무변 / `Y(4종)` = 허용 변경 4종 내 처리(근거 = 태그).

### (1) amendment 헤딩 40 (H2 19 + H3 21 — ratchet 산정 단위 전수)

| # | 구 앵커 (헤딩·레벨) | carrier | fm | 신 위치 | 태그 | NSC |
|---|---|---|---|---|---|---|
| 1 | `## Amendment 1 (CFP-390…)` H2 | CFP-390 | [1] | 분해 → row 20~23 (§결정 6c·12 정정 + §결정 13·14) | carrier-preserved | Y |
| 2 | `## Amendment 2 (CFP-455…)` H2 | CFP-455 | [2] | 분해 → row 24~30 (§결정 3·6c·14~18) + 다이어그램 동기 서사 = obsolete제거(구본 동결) | carrier-preserved | Y(4종) |
| 3 | `## Amendment 7 (CFP-508…)` H2 | CFP-508 | [7] | §결정 20 | carrier-preserved | Y |
| 4 | `## Amendment 8 (CFP-530…)` H2 | CFP-530 | [8] | §결정 21 — entry yaml 사본·16-file tier 매핑·family 순번 = registry/이력 SSOT 이관(구본 동결) | 기술정정(구조개선) | Y(4종) |
| 5 | `## Amendment 10 (CFP-662…)` H2 | CFP-662 | [10] | §결정 24 — entry yaml 사본·RETRO 서사 동결 이관 | 기술정정(구조개선) | Y(4종) |
| 6 | `## Amendment 11 (CFP-442…)` H2 | CFP-442 | [11] | §결정 25 (은퇴 현행 상태 기록) + §결정 14 이행 | 기술정정 | Y(4종) |
| 7 | `## Amendment 12 (CFP-734…)` H2 | CFP-734 | [12] | §결정 26 | carrier-preserved | Y |
| 8 | `## Amendment 13 (CFP-722…)` H2 | CFP-722 | [13] | §결정 27 | carrier-preserved | Y |
| 9 | `## Amendment 14 (CFP-963…)` H2 | CFP-963 | [14] | §결정 28 (orphan 현행 상태 기록 — fm drop 은 (3) row 참조) | 기술정정 | Y(4종) |
| 10 | `## Amendment 15 (CFP-1306…)` H2 | CFP-1306 | [15] | §결정 29 (동상) | 기술정정 | Y(4종) |
| 11 | `## Amendment 16 (CFP-2061-S1…)` H2 | CFP-2061-S1 | [16] | §결정 30 | carrier-preserved | Y |
| 12 | `## Amendment 17 (CFP-2061-S4…)` H2 | CFP-2061-S4 | [17] | §결정 31 | carrier-preserved | Y |
| 13 | `## Amendment 18 (CFP-2381…)` H2 | CFP-2381 | [18] | §결정 32 (32.F STALE flip·32.G 권고·32.H F4 택일 = 이행 완료 dated — 구본 동결) | carrier-preserved | Y(4종) |
| 14 | `## Amendment 19 (CFP-2426…)` H2 | CFP-2426 | [19] | §결정 33 | carrier-preserved | Y |
| 15 | `## Amendment 20 (CFP-2591…)` H2 | CFP-2591 | [20] | §7.9.A~H (A/B/C = §결정 32/3/6 fold) + NO-FLIP Stage 서사 = dated(구본 동결) | carrier-preserved | Y |
| 16 | `## Amendment 21 (CFP-2678…)` H2 | CFP-2678 | **부재** (헤딩-단독 — 본문/fm 번호 충돌 pre-existing drift: fm[21] = CFP-2597 별개 identity) | §결정 34 | carrier-preserved | Y |
| 17 | `## Amendment 24 (CFP-2719…)` H2 | CFP-2719 | [24] | fact-correction 3건 → §7.9.D 정확 인용·hollow 정정·ADR-168 §결정 16 증거 의무 pointer 로 본문 반영(정정 서사 자체 = dated, 구본 동결) | 기술정정 | Y |
| 18 | `## Amendment 25 (CFP-2650…)` H2 | CFP-2650 | [25] | 승격 provenance = registry `promoted_by/promoted_date` SSOT 이관 + "surfacing ≠ required"·honesty-ceiling tier-독립 = §결정 3 fold | 기술정정(구조개선) | Y |
| 19 | `## Amendment 26 (CFP-881…)` H2 | CFP-881 | [26] | §결정 14 현행 실물 + fm mea 11번째 entry (신규 §결정 0 — §결정 5 절차 상속) | carrier-preserved | Y |
| 20 | `### Amendment 1-결정 6 (c) 정정` H3 | CFP-390 | [1] | §결정 6 (c) — sibling chain 정정 이력은 registry field 값으로 수렴(append-보존 관행만 §결정 6 승계) | carrier-preserved (inline fold into §결정 6) | Y |
| 21 | `### Amendment 1-결정 12 정정` H3 | CFP-390 | [1] | §결정 12 — carrier 목록 정정 최종 상태로 재기술 | carrier-preserved (inline fold into §결정 12) | Y |
| 22 | `### Amendment 1-결정 13 (신설)` H3 | CFP-390 | [1] | §결정 13 — 그룹 A/B/C 시점 표 = dated(구본 동결), scope 한정·그룹 B 원칙·그룹 C SSOT 참조만 승계 | 기술정정(구조개선) | Y(4종) |
| 23 | `### Amendment 1-결정 14 (신설)` H3 | CFP-390 | [1] | §결정 14 | carrier-preserved | Y |
| 24 | `### Amendment 2-결정 3 (변경)` H3 | CFP-455 | [2] | §결정 3 (current_tier required 최종 상태) | carrier-preserved (inline fold into §결정 3) | Y |
| 25 | `### Amendment 2-결정 6 (c) 정정` H3 | CFP-455 | [2] | §결정 6 (c) — append-보존·self-carrier 제외 관행 승계 | carrier-preserved (inline fold into §결정 6) | Y |
| 26 | `### Amendment 2-결정 14 (정정)` H3 | CFP-455 | [2] | §결정 14 (anomaly/schema 2축 분리) | carrier-preserved | Y |
| 27 | `### Amendment 2-결정 15 (신설)` H3 | CFP-455 | [2] | §결정 15 | carrier-preserved | Y |
| 28 | `### Amendment 2-결정 16 (신설)` H3 | CFP-455 | [2] | §결정 16 | carrier-preserved | Y |
| 29 | `### Amendment 2-결정 17 (신설)` H3 | CFP-455 | [2] | §결정 17 | carrier-preserved | Y |
| 30 | `### Amendment 2-결정 18 (신설)` H3 | CFP-455 | [2] | §결정 18 | carrier-preserved | Y |
| 31 | `### Amendment 10-결정 24 (신설)` H3 | CFP-662 | [10] | §결정 24 | carrier-preserved | Y |
| 32 | `### Amendment 11-결정 25 (신설)` H3 | CFP-442 | [11] | §결정 25 — scope SSOT 상세 = 구본 동결(산출물 은퇴 반영 = 현행 사실 기록) | 기술정정 | Y(4종) |
| 33 | `### Amendment 12-결정 26 (신설)` H3 | CFP-734 | [12] | §결정 26 — 26.A~F 승계 / 26.D 도출 상세·26.G lane 분류 = dated(구본 동결) | 기술정정(구조개선) | Y(4종) |
| 34 | `### Amendment 13-결정 27 (신설)` H3 | CFP-722 | [13] | §결정 27 | carrier-preserved | Y |
| 35 | `### Amendment 14-결정 28 (신설)` H3 | CFP-963 | [14] | §결정 28 (orphan 기록 — 등록 결정 자체는 구본 동결) | 기술정정 | Y(4종) |
| 36 | `### Amendment 15-결정 29 (신설)` H3 | CFP-1306 | [15] | §결정 29 (동상) | 기술정정 | Y(4종) |
| 37 | `### Amendment 16-결정 30 (신설)` H3 | CFP-2061-S1 | [16] | §결정 30 — 30.C exempt 잠정 경계·30.D stash proof = dated(구본 동결) | carrier-preserved | Y(4종) |
| 38 | `### Amendment 17-결정 31 (신설)` H3 | CFP-2061-S4 | [17] | §결정 31 — 7지표 표·31.D TC 목록 = 요지 승계(상세 구본 동결) | carrier-preserved | Y(4종) |
| 39 | `### Amendment 18-결정 32 (신설)` H3 | CFP-2381 | [18] | §결정 32 — 32.A 갭 서사·32.B 실측 표 = dated(구본 동결), 검출·action·self-app 규범 전량 승계 | carrier-preserved | Y |
| 40 | `### Amendment 19-결정 33 (신설)` H3 | CFP-2426 | [19] | §결정 33 — 33.E pattern_count 정당화 = 원칙만 승계 | carrier-preserved | Y |

**(1)-보충 — fm-단독 identity 8건 (ratchet-매칭 헤딩 무기여, 카운트 비계상 — identity 축 zero-drop 완결용)**

| 구 앵커 | carrier | 신 위치 | 태그 | NSC |
|---|---|---|---|---|
| `amendment_log[3]` (전용 헤딩 부재) | CFP-449 | §결정 7 (audit 전용 채널 sharpening fold) + `decision-principle-vocab` entry = registry SSOT | carrier-preserved (inline fold into §결정 7) | Y |
| `amendment_log[4]` (전용 헤딩 부재) | CFP-481 | `auto-phase-label` entry 등록 = registry SSOT (§결정 5 절차 선례) | 기술정정(구조개선) | Y(4종) |
| `amendment_log[5]` (전용 헤딩 부재) | CFP-506 | `claude-md-line-cap` entry 등록 = registry SSOT (registry :549-550 `carrier_adr`+`carrier_amendment: 5` 페어 = 쌍-보존 예외 대상 — Phase 2 치환 제외, dated provenance) | 기술정정(구조개선) | Y(4종) |
| `amendment_log[6]` + 본문 `### §결정 19 (Amendment 6…)` H3(비매칭 형식 — count 무기여) | CFP-509 | §결정 19 + recurrence schema(v1.2) 도입 이력 | carrier-preserved | Y |
| `amendment_log[9]` + 본문 `### §결정 22/23 (Amendment 9…)` H3 ×2(비매칭 형식) | CFP-583 | §결정 22 + §결정 23 | carrier-preserved | Y |
| `amendment_log[21]` (전용 헤딩 부재 — 본문 `Amendment 21` 헤딩은 CFP-2678 별개 identity) | CFP-2597 | `peer-completion-falsifiability` = fm mea 7번째 entry + registry SSOT (§결정 5 신규-§결정-0 절차) | carrier-preserved (inline fold into §결정 5) | Y |
| `amendment_log[22]` (전용 헤딩 부재) | CFP-2635 | `shell-test-exit-masking-detect` = fm mea 8번째 entry + registry SSOT | carrier-preserved (inline fold into §결정 5) | Y |
| `amendment_log[23]` (전용 헤딩 부재) | CFP-2700 | `infra-resource-{undeclared-surface,orphan-reconcile}` = fm mea 9·10번째 entry + registry SSOT (구 Amd24 정정 반영 — hollow claim 미상속) | carrier-preserved (inline fold into §결정 5) | Y |

### (2) 자체 §결정 1~12 (ADR-060 최초 codify, CFP-389) → §결정 1~12 (번호 보존)

| 구 §결정 | 신 위치 | 태그 | 구 앵커 (ADR-060) | 비고 |
|---|---|---|---|---|
| §결정 1 (Framework SSOT 위치) | §결정 1 | carrier-preserved | `### 결정 1` | §5.5 CL-1 채택 서사 제거(저작 증적) |
| §결정 2 (Registry data single SSOT) | §결정 2 | **기술정정(구조개선)** | `### 결정 2` | "entry-level 현행값 = registry 유일 원본" 정형 문장 추가 — §결정 2 원칙의 명시화(본 재제정 fold direction 의 근거 조항) |
| §결정 3 (4-tier enum) | §결정 3 | **기술정정(구조개선)** | `### 결정 3` | 구 Amd2(required 전환) + §7.9.B(surfacing qualifier) + 구 Amd25(honesty-ceiling tier-독립) fold — "CFP-391 이 후속 명시" dated 서사 제거 |
| §결정 4 (첫 entry) | §결정 4 | **기술정정(구조개선)** | `### 결정 4` | entry yaml 사본 → registry SSOT 이관. lint 책임 4건·exit·bypass skip = 전량 승계 |
| §결정 5 (warning mode 첫 적용) | §결정 5 | **기술정정(구조개선)** | `### 결정 5` | workflow 양식 상세(trigger·paths·pip) = dated 이행분(구본 동결). 신규 entry "신규 §결정 0" 등록 절차 = 구 Amd21(fm)~26 반복 관행의 fold(현재형 일반 규칙 승격 — 규범 신설 아닌 기존 관행 모아쓰기) |
| §결정 6 (승격 gate 3-AND) | §결정 6 | **기술정정(구조개선)** | `### 결정 6` | (c) sibling 구체 CFP 열거 → registry field SSOT + 관행 2종(append-보존/self-carrier 제외 — 구 Amd1·2·11 fold). evidence 6 산출물(i~vi) 전량 승계. §7.9.C baseline-relative fold |
| §결정 7 (hotfix bypass channel) | §결정 7 | carrier-preserved | `### 결정 7` | 구 Amd3 sharpening 문단 = 본문 fold(구본은 (Amendment 3) 표기로 기반영). label-registry MINOR 절차 서사 = dated |
| §결정 8 (audit trail schema) | §결정 8 | carrier-preserved | `### 결정 8` | schema·re-entry·lint·author 검증·sticky 전량 승계 + §7.9.F 실배선 실물 pointer |
| §결정 9 (모달 어휘 1차 사전) | §결정 9 | carrier-preserved | `### 결정 9` | 4 표현 verbatim + chain SSOT 위치 + word-boundary 전환 의무 승계 |
| §결정 10 (velocity-normalized metric) | §결정 10 | carrier-preserved | `### 결정 10` | — |
| §결정 11 (영구 정책) | §결정 11 | carrier-preserved | `### 결정 11` | supersede 종료 경로 = 본 재제정이 실물 — 지위 신 record 승계 명시(기술정정) |
| §결정 12 (CFP-B carrier 일체화) | §결정 12 | **기술정정** | `### 결정 12` | 후속 carrier 잠정 목록(CFP-C/D 등) = 이행 완료 dated → carrier 분리 원칙만 현재형 재기술 |

### (3) fm mechanical_enforcement_actions 13건 (승계 11 + drop 2)

| # | action (구 fm) | 유래 | 처분 | 태그 |
|---|---|---|---|---|
| 1 | story-section-ownership | 구 Amd13 (CFP-722) | **승계** — 신 fm entry + §결정 27 | carrier-preserved |
| 2 | codex-network-scope-presence | 구 Amd14 (CFP-963) | **drop** — registry `entries[].name` 부재(2026-06-10 de-bloat 고아 제거 이력·Phase 2 미이행 deferred-followup) = fm↔registry 불일치 drift. 승계 시 사실과 불일치 상태 복제 → 불승계. §결정 28 이 현행 상태 기록·재도입 경로 명시(무단 누락 아님) | **obsolete제거** |
| 3 | parallel-anchors-checked-presence | 구 Amd15 (CFP-1306) | **drop** — registry `entries[].name` 부재(동일 drift 범주). §결정 29 기록 | **obsolete제거** |
| 4 | increment-justification-presence | 구 Amd16 (CFP-2061-S1) | **승계** — §결정 30 | carrier-preserved |
| 5 | governance-drift-detection | 구 Amd17 (CFP-2061-S4) | **승계** — §결정 31 | carrier-preserved |
| 6 | deferred-followup-reconcile | 구 Amd18 (CFP-2381) | **승계** — §결정 32 | carrier-preserved |
| 7 | deferral-carrier-declared | 구 Amd20 (CFP-2591) | **승계** — §7.9.E (target_section §결정 32) | carrier-preserved |
| 8 | lane-count-ssot-consistency | 구 Amd19 (CFP-2426) | **승계** — §결정 33 | carrier-preserved |
| 9 | peer-completion-falsifiability | 구 fm Amd21 (CFP-2597) | **승계** — §결정 5 (신규 §결정 0) | carrier-preserved |
| 10 | shell-test-exit-masking-detect | 구 fm Amd22 (CFP-2635) | **승계** — §결정 5 | carrier-preserved |
| 11 | infra-resource-undeclared-surface | 구 fm Amd23 (CFP-2700) | **승계** — §결정 5 (+§7.9.D/§결정 32 surfacing 상속) | carrier-preserved |
| 12 | infra-resource-orphan-reconcile | 구 fm Amd23 (CFP-2700) | **승계** — §결정 5 | carrier-preserved |
| 13 | evidence-registry-structure-verify | 구 Amd26 (CFP-881) | **승계** — §결정 5/14 | carrier-preserved |

**(3) 공통 기술정정**: 승계 11건의 `progress_note` 는 이행 진행 서사(Phase 1/2 scope 열거·prior art 목록·plugin bump 이력)를 제거한 요지 1줄로 compact 재기술 — entry-level 상세의 현행 SSOT = registry(§결정 2), 이행 이력 = 동결 구본 fm. `status`·`target_section` 값은 verbatim 보존(승계 11건 전건 registry `entries[].name` 실재 grep 대조 완료 — 2026-08-04).

**공통 dated-history 제거 (전 블록 적용)**: "N번째 warning-tier entry" 순번 arithmetic / hotfix-bypass family member 순번("20번째 family member" 류 — 현행 SSOT = label-registry-v2) / sibling_dependencies chain 누적 나열(현행 SSOT = registry field) / entry yaml 사본 블록 / Mermaid carrier chain 동기 서사 / TDD stash·bats TC 개수 증적 / plugin.json bump 이력 / "ratchet 위반 0건" 반복 선언(fold 방향 declare 로 일괄 흡수) / FIX iter 정정 서사 = 의무·금지·조건·예외가 아닌 **저작 증적·시점 표기** → 본 ADR 본문 전량 제거(동결 구본 ADR-060 이 이력 담보). 재제정 허용 변경 4종 내.

**비-§결정 섹션 처분**: 구본 컨텍스트(직접 동인 5·prior art)는 요지 승계(§컨텍스트), `## 결과`/`## Trade-off` 는 신 결과 절로 압축, `## 대안`(B/C/E 거부)은 거부 논거가 살아있는 지점에 내장(§결정 5 warning-first = 대안 C 거부 / §결정 7 per-entry namespace = 대안 E 거부 / §결정 7 bypass 채널 존재 = 대안 B 거부 — 전부 §결정 내장 승계), `## 다이어그램`(Mermaid — sibling chain dated 표기 포함) = obsolete제거(구본 동결). `## 해소 기준` = 동일 선언 승계.

## 관련 파일

**Phase 1 (본 Story)**:

- `archive/adr/ADR-RESERVATION.md` — ADR-number row 171 신설 (dual-key 3-leg: 파일명 ∧ frontmatter `adr_number: 171` ∧ row)

**Phase 2 (atomic bundle — 순서 = barrier 봉인)**:

> [선행] marketplace sync PR merge(plugin.json 실변경 확정 시 — ADR-063) → [P2 단일 PR] ① 구 ADR-060 frontmatter `status: Superseded by ADR-171` 전이(본문 byte 무변경, numstat 1/1) ② 게이트 스크립트 리터럴 re-home(`check_adr_amendment_threshold.py` :5/:43/:390/:652 + GENERATED writer 리터럴 5개소 — **:390 은 ③보다 반드시 선행**, 역순이면 재생성이 구 앵커 재주입) ③ `--write-baseline` 재생성(16→15, **cwd = repo root** — thin wrapper 는 인자 있으면 cd 생략) + 잔여 GENERATED baseline 재생성·diff = 헤더 앵커 행만 검증(INV-R) ④ registry 값-앵커 119개소 치환(쌍-보존 예외 1건 :549-550 제외) + 헤더 L4 ⑤ live anchor re-home(agent .md 3종·playbook·hooks 3종·contracts·wording-dictionary·doc-location-registry·family.md) ⑥ RESERVATION row 60 `active → archived` ⑦ 게이트 GREEN 양성 증거 실측 + self-test 무회귀. **역순 분리 금지 근거** = baseline 제거 단독 선행 시 branch (i) RED(S2 시뮬레이션 실증) + 전이 없는 재생성 = picked 재포함으로 제거 silent 미이행.

- `archive/adr/ADR-060-evidence-enforceable-promotion-framework.md` — status 전이 (frontmatter 최소행)
- `docs/adr-amendment-threshold-baseline.yaml` — ADR-060 행 제거 16→15 (`--write-baseline` 단일 writer, 손편집 금지)
- `scripts/lib/check_adr_amendment_threshold.py` — 리터럴 4개소 re-home
- `docs/evidence-checks-registry.yaml` — 헤더 L4 + `owner_adr` 11 + `paired_owner_adr` 3 + `carrier_adr` 105 = 120개소 중 119 치환(값-앵커 한정 `:[[:space:]]+ADR-060([^0-9]|$)` — loose `.*` 금지) + 쌍-보존 예외 1건(:549-550) + 인라인 주석 "ADR-060 Amendment N" 9건 dated provenance 보존 + 대사 1행 `ADR-171.*Amendment [0-9]+` == 0
- GENERATED writer 리터럴 잔여 5개소 (2026-08-04 소비 직전 re-Read 실측) — `scripts/check-wording-dictionary.sh:452` / `scripts/lib/gen_deferred_followup_baseline.py:49` / `scripts/lib/check_infra_resource_drift.py:97` / `scripts/lib/check_path_relocation_consistency.py:666` / `scripts/lib/check_resource_safety_claim_proof.py:400` (각 재생성 결정론 확인 후 in-scope — 재생성 diff = 헤더 앵커 행만인지 검증(INV-R), 비결정론 writer 는 해당 쌍만 f/u 분리 + 잠복 명시)
- `plugins/{codeforge-develop,codeforge-pmo,codeforge-requirements}/agents/` 3종 + `docs/orchestrator-playbook.md` + `hooks/` 3종 + `docs/inter-plugin-contracts/`(재-grep 전수 — PATCH bump + MANIFEST row) + `docs/wording-dictionary.{md,yaml}` + `docs/doc-location-registry.md` + `docs/architecture/codeforge-family.md` — live anchor re-home
- `archive/adr/ADR-RESERVATION.md` — row 60 `active → archived`(요약표 enum — `superseded` 금지, 2-표 enum 비대칭. `amendments_reserved[]` sub-tree 의 `adr_number: 60 / amendment_id: 25`(CFP-2650) row = **무접촉** — sub-tree enum 별개 축 + status active = spent 적용완료, Superseded 전이 후 amend 봉쇄 = ADR-014 의도 동작)

**Phase 2 전역 re-grep 규율**: 위 개소 수치·라인 번호는 Phase 1 저작 시점 실측 스냅샷(2026-08-04, base 2c2c3f09a)이다 — Phase 2 재지향 시 파일별 전 인용을 re-grep 으로 재실측 후 전수 재지향한다(라인 드리프트·병렬 신규 entry 착지 방어 — registry 는 rebase 마다 재-grep).

**광역 역참조 sweep**(`.md` 122 파일 + scripts/workflows gray 주석층 224건) = **follow-up 분리** — 구본 파일 존속으로 링크 불파손(선례 CFP-2855/#2877·CFP-2885/#2887 이 ADR-082→168 광역 sweep 을 f/u 로 완주한 경로 답습).

## 해소 기준

N/A — permanent policy (evidence-enforceable promotion framework SSOT 상시 적용, `is_transitional: false`). 구 ADR-060 §결정 11 의 동일 선언 승계 — 본 ADR 의 효력 종료 조건 = 본 ADR 의 supersede 또는 evidence-enforceable governance 자체 폐지. 개별 evidence check entry 의 individual sunset 은 framework 운영의 정상 동작이며 본 SSOT 의 sunset 이 아니다.
