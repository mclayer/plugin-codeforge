---
adr_number: 131
title: "cross-repo 책임 배치 거버넌스 모델 — 토폴로지 SSOT 1급화 + 메타불변식 게이트 계약 + 기계/사람 판정 분리 (Epic CFP-2418 Story 1)"
status: Proposed
category: governance
date: 2026-06-26
carrier_story: CFP-2419
parent_epic: CFP-2418
supersedes: null
amends: null
amendments: [1]
amendment_log:
  - amendment: 1
    carrier_story: CFP-2428
    date: 2026-06-26
    summary: |
      declared-marker layer(L1 코드→책임) 신설 (Epic CFP-2418 deferred FU) — §결정 3/4 가 deferred 한
      "책임 의미단위 깊은 파생 — 마커 시스템 선결" 의 marker layer 실현. L2(책임→레포, CFP-2422) 의
      sibling layer — 검사 layer disjoint(L1 코드 위치 정합 vs L2 소유레포 정합), join-key=responsibility
      byte-identical namespace 공유, 합쳐져 L1→L2→L3 transitive 일관성 완성. drift 3종(a unmarked / b
      marker↔topology 불일치 / c stale marker) = warning-tier(continue-on-error, OPA Gatekeeper
      enforcementAction 점진 승격 — hard-block 은 별 후속 CFP). 재정의 명문: "의미단위 깊은 파생" 중
      *의미* 부분은 의미추론=검사연극(ADR-119 위반)이라 불가 판명 → *구조* 일관성+drift 만 기계화,
      *의미* 정합은 attestation 영구화(review-responsibility 행 d 무변경). ratchet 강화 방향(marker
      layer 신설 = governance 확장, 약화 surface 0) — is_transitional:false 유지. 신규 ADR 번호 0
      (Amendment — ADR-RESERVATION 무변경). 신규 영구·CONDITIONAL deputy 0 / RACI R row 0 / axis-disjoint.
      Phase 1 = 본 Amendment(선언만) / Phase 2(구현 lane) = 스키마 본문 + drift-check 스크립트 +
      workflow(templates+.github byte-identical) + tests. branch protection 6-tuple 무변경.
deputy_inputs:
  CodebaseMapper: as-is_roster_mandate_facts_+_ADR-042_876_chief_authority_+_RefactorAgent_46_advisory_boundary
  Refactor: repo-분해_advisory_무축소_경계_확정_(escalation-tier_제안만,_확정은_disjoint)
  ModuleArch: 레포_내부_boundary_axis_disjoint_확인_(레포_소유_배치_⊥_module/aggregate_boundary)
  SecurityArchitect: N/A_—_wrapper-self_governance_codify_(위협모델/auth/data_부재)
  TestContractArchitect: N/A_—_검사_스크립트_0_신설_(Story_2_carrier,_Phase_1_선언만)
  DataArchitect: N/A_—_데이터_마이그레이션_부재_(overlay_additive_backward-compat만)
related_stories:
  - CFP-2419  # 본 ADR 신설 carrier (Epic CFP-2418 Story 1 — 선행 Story)
  - CFP-2418  # parent Epic — cross-repo 책임 배치 거버넌스 (wrapper-self)
  - CFP-2428  # Amendment 1 carrier — declared-marker layer (Epic CFP-2418 deferred FU)
related_adrs:
  - ADR-069   # multi-repo story key system — repos[].components 예약필드 활성화 source (Amendment 1 동반 발의)
  - ADR-130   # applicability ⊥ closure 메타불변식 게이트 — 상류 토대 (패턴 계보), ⚠ 공백 처리 방향 차이 (layer 분리 명시)
  - ADR-042   # agent model + deputy mandate — chief repo-level boundary authority (L876) cross-ref, RACI 충돌 0
  - ADR-086   # deputy 신설 결정 framework — axis-disjoint 5-checklist 동형 자기적용
  - ADR-020   # cross-repo Epic Mode A/B/C — Story file 라우팅 조직 패턴 (직교 anchor)
  - ADR-119   # research-before-claims — 검사연극 금지 + 외부지식 source 인용 정합
related_files:
  - docs/project-config-schema.md
  - archive/adr/ADR-069-multi-repo-story-key-system.md
  - archive/adr/ADR-RESERVATION.md
  - plugins/codeforge-design/agents/ArchitectAgent.md
  - tests/scripts/test_check-responsibility-topology.sh
is_transitional: false
---

# ADR-131: cross-repo 책임 배치 거버넌스 모델

## 상태

Proposed (2026-06-26) — Epic CFP-2418 (cross-repo 책임 배치 거버넌스) Story 1 (선행) carrier. wrapper-self 거버넌스 codify (실 도메인 설계결정 0). Phase 1 = 선언만 (검사 스크립트·required check 0 신설 — Story 2/3 carrier).

> **category cross-ref (CFP-2753 정규화)**: primary `governance` — 본 결정 성격(거버넌스 모델, 규칙4 단일 primary). 구 compound `orchestration/governance` 의 secondary 축 `orchestration`(cross-repo topology / Orchestrator-level 발급 자동화)은 정보 손실 방지 위해 본문 cross-ref 로 보존. [verified: ADR-153 Amendment 1 A1-1]

## 본질 선언

멀티레포 시스템에서 **"어느 레포가 무슨 책임을 소유하는가(책임 배치)"** 는 코드의 정적 의존 경계와 **다른 축**이다. 코드 경계(import 방향·vendoring·SHA-pin)는 컴파일러·관습이 방어하지만, *책임의 소유레포 귀속* 은 사람이 쓴 hub prose 에만 살아 있고 어떤 게이트도 강제하지 않았다. 본 ADR 은 이 공백을 — **새 advocate 에이전트 신설 없이** — 토폴로지 SSOT 1급화 + 메타불변식 게이트 계약 + 기계/사람 판정 분리로 닫는다.

## 컨텍스트

### 진단 (증거 기반 — handoff spec §2, file:line 실측 4 병렬 탐지 + Codex 적대 검증)

| 가설 | 판정 | 근거 |
|---|---|---|
| (a) 소유 지도 부재 | **거짓** | mctrader `repos.md §7` = 강한 불변 소유 DAG + `build-coordination.md` CO-1~14 ledger |
| (b) 코드가 지도 위반 | **거짓** | 의존방향 위반 0 / 도메인타입 vendoring 0 / git 의존 100% SHA-pin. Rust 컴파일러 + 관습이 *정적* 경계 방어 |
| **(c) 프로세스가 배치를 검문 안 함** | **참 (핵심)** | 배치 결정이 hub prose 에만 존재 + 어떤 게이트도 강제 안 함. review-responsibility 매트릭스에 배치 검문 행 0. **주인 없는 책임(CO-14: Sharpe/MDD)** 이 감사로 뒤늦게 발견 `[verified]` (handoff spec §2 (c)행) |

진짜 공백 = *전담 advocate 에이전트* 가 아니라 **배치 결정 산출물 + 강제 게이트 + 상위 발급 자동화**. 사용자 원 발화("멀티레포 전략 관리 에이전트")는 Codex 적대 리뷰로 MVP 축소 — 책임 *의미단위* 양방향 declared↔derived 검증은 마커 시스템 없이 기계화 불가하므로 deferred.

### 설계 에이전트 roster 의 mandate 공백 (chief authority pre-exists)

어느 기존 design 에이전트도 "레포 소유 배치"를 1급 mandate 로 갖지 않으나, **repo-level 분해 경계 확정 권한은 이미 chief(ArchitectAgent)에 귀속**되어 있다 `[verified]` (ADR-042:876 "repo-level 분해 경계 확정 = ArchitectAgent chief authority (macro-architecture, ModuleArch mandate 초과 — ModuleArch consult)"):

| 에이전트 | 현 mandate 경계 | "레포 소유 배치" 포함? |
|---|---|---|
| ModuleArchitectAgent | module/package boundary + dependency direction (**레포 *내부*** boundary axis) | 아니오 — 레포 내부만 |
| RefactorAgent | repo-분해 구조 advocacy(escalation-tier) — repo-분해 *pressure 식별·제안*, **경계 확정은 disjoint** | 아니오 — 제안만, advisory 보존 (RefactorAgent.md repo-분해 구조 escalation 축; 측정 축은 구현 리팩터링 Story C 이관 — CFP-2539 / ADR-042 Amendment 18, repo-분해 존치로 무축소 premise TRUE) |
| ArchitectAgent (chief) | Change Plan §1-§13 + ADR draft author. **"repo-level 분해 경계 확정 = chief authority"** 이미 보유 (ADR-042:876) | 부분 — repo 분해 *경계* 는 chief 권한이나 "토폴로지 SSOT 1급 author" 는 미명시 |

→ 본 ADR = 이미 chief authority 에 귀속된 "repo-level 경계 확정" 권한을 **"토폴로지 SSOT 1급 author"로 명시 확장**하는 wording-level 명문화 (신규 영구 deputy 0, 신규 RACI R row 0 — authority pre-exists).

### 외부 지식 배경 (source 인용 — ADR-119 정합)

- **Nx `@nx/owners`**: 선언은 프로젝트 단위, 강제는 파일 단위로 CODEOWNERS 로 *컴파일*. → "wrapper 메타불변식만 강제 / consumer overlay 정책값 주입" 분리 모델의 외부 근거 (source: Nx Enterprise `@nx/owners`). **개념 인용, 채택 도구 아님** — `@nx/owners` 는 유료 Nx Enterprise 기능이라 도구 채택이 아니라 컴파일 모델만 차용.
- **declared↔derived 일관성 합성 유추**: Bazel strict-deps(forward — actual deps ⊆ declared deps) + Terraform drift detection(reverse — state refresh→compare) **2-도구 합성**으로 유추 (source: Bazel strict-deps / Terraform drift detection — 단일 도구의 feature 아닌 forward+reverse 합성). CFP-2412 3-way consistency gate 가 이미 차용한 계보를 동형 재사용.
- **OPA Gatekeeper progressive enforcement**: `enforcementAction`(warn → deny) 점진 승격 (source: OPA Gatekeeper `enforcementAction` — raw OPA 가 아니라 Gatekeeper 의 admission control 기능). → 메타불변식 게이트가 Story 2 에서 warning tier 부터 점진 승격하는 패턴의 외부 근거.
- **GitHub CODEOWNERS**: 파일 경로↔owner 의 *구조적* 매칭만 강제, "이 owner 가 *적절한가*"는 리뷰어 판단에 위임 (source: GitHub Docs — CODEOWNERS). → "구조=hard-block / 의미=attestation 요구만(검사연극 금지)" 의 직접 선례.

## 결정

### 결정 1 — 토폴로지 SSOT 1급화 (author = ArchitectAgent chief 권한 확장, 신규 영구 deputy 0)

cross-repo 책임 배치를 **1급 설계 산출물**(토폴로지 SSOT)로 격상한다. "어느 레포가 무슨 책임을 소유하는가"는 더 이상 사람이 쓴 hub prose 가 아니라, 게이트가 검사 가능한 구조화 산출물에 기록된다.

- **author = ArchitectAgent (chief)** — 신규 영구 advocate 에이전트 신설 0. "repo-level 분해 경계 확정 = chief authority"(ADR-042:876)가 *이미* 존재하므로, 본 결정은 그 권한을 "토폴로지 SSOT 1급 author"로 **명시 확장**하는 wording-level 명문화일 뿐 신규 R 의 부여가 아니다.
- **RACI 충돌 0 (cross-ref ADR-042:876)** — 소유레포 *확정* 의 R = chief 단독. ADR-042 가 이미 chief 에 귀속한 권한이므로 deputy-mandate RACI matrix 에 신규 R row 추가 불요 (topology SSOT 1급 author = pre-existing chief authority 의 표현 정밀화).
- **ModuleArch consult 유지** — ADR-042:876 의 "ModuleArch consult" 패턴 답습. 레포 *내부* boundary 는 여전히 ModuleArch advocacy, chief 가 repo-level 확정 시 consult.

### 결정 2 — wrapper 는 메타불변식만 강제 (4 메타불변식 명문 + layer 분리 verbatim)

codeforge wrapper 는 **메타불변식(구조적 사실)만 강제**하고, "어느 레포가 무엇을 소유하는가"의 구체 맵은 consumer overlay 가 주입한다 (Nx `@nx/owners` 컴파일 모델 — 선언=프로젝트 단위 / 강제=파일 단위, source: Nx Enterprise `@nx/owners`. 개념 인용·채택 도구 아님).

**4 메타불변식 (wrapper 강제 대상)**:
1. **모든 책임이 정확히 1 소유레포** — 각 책임 항목은 owner_repo 1개를 가진다 (0개도 2개도 아님).
2. **주인없는 책임 0** — 변경이 건드린 레포 집합에 토폴로지 SSOT 소유 선언 없는 책임이 존재하면 위반.
3. **중복소유 0** — 동일 책임이 N≥2 레포에 owner 로 등장하면 위반.
4. **SSOT 파일 존재 + 스키마 유효** — 토폴로지 SSOT 산출물이 존재하고 스키마(소유레포 + 근거 + 연결 작업단위/ADR/change-plan 링크 ≥1)를 만족.

**layer 분리 (verbatim — AC-2 필수)**: 본 ADR 의 **"정책값 공백 = PASS"** 는 ADR-130 의 **fail-closed(`unknown` = exit 1, ADR-130:96)** 와 **다른 LAYER** 이다. 둘은 모순이 아니다 — ADR-130 의 fail-closed 는 *wrapper 구조 검증* layer(미분류 자산을 안전하게 차단), ADR-131 의 "정책값 공백 PASS" 는 *consumer 정책값 미주입* layer(opt-in 무손상 — frontend-only/단일레포 consumer 비차단)이다. wrapper 가 강제하는 것은 *구조의 유효성*(메타불변식 4종)이지 *정책 내용의 존재*가 아니다. consumer 가 `repo_topology.applicable: false`(또는 미주입)이면 메타불변식 게이트 PASS, `applicable: true` 후 맵을 비우면 스키마 유효성만 검사하되 정책 내용 공백은 PASS.

### 결정 3 — 게이트 = 메타불변식 hard-block + 거친 파생 (깊은 파생 deferred)

게이트는 **구조적 사실**만 hard-block 한다:
- **메타불변식 hard-block** — 결정 2 의 4종(고아/중복/SSOT 부재·스키마 무효).
- **거친 파생 hard-block** — 선언 소유레포 vs 변경이 실제 건드린 레포 집합의 *집합 단위* 불일치.
- **책임 의미단위 깊은 파생 = deferred** — "선언된 소유레포가 *의미상 올바른* 도메인 레포냐"의 양방향 declared↔derived 검증은 **마커 시스템 선결**이라 본 Epic scope 외 (deferred follow-up, 별도 CFP — 결정 4 + Out-of-Scope 참조).

declared↔derived 일관성 모델은 Bazel strict-deps(forward — actual ⊆ declared) + Terraform drift detection(reverse — refresh→compare) **2-도구 합성 유추**다 (source: Bazel strict-deps / Terraform drift detection — 단일 도구 feature 아닌 forward+reverse 합성). **Story 1 은 계약 정의만** — 실 hard-block 검사 스크립트는 Story 2 carrier (warning tier 부터 점진 승격, OPA Gatekeeper `enforcementAction` 패턴 — source: OPA Gatekeeper).

### 결정 4 — 기계 vs 사람 판정 분리 (검사연극 금지, ADR-119 정합)

판정을 두 종류로 분리한다:
- **구조적 사실 = 기계 hard-block** — 파일이 어느 레포에 있나 / 소유 선언이 있나 없나 / 중복인가. 기계가 단정 가능.
- **의미적 정합 = 사람 판정** — "이 책임이 *이 도메인 레포에* 있는 게 옳은가"는 기계가 단정 불가. 단정하면 검사연극(false GREEN/RED). 따라서 게이트는 의미 판정을 **"소유 선언 + 리뷰어 근거인용 attestation 을 기계적으로 *요구*만"** 하고 **승인 자체는 대신 판단하지 않는다** (ADR-119 검사연극 금지 정합).

직접 선례 = GitHub CODEOWNERS (source: GitHub Docs) — 파일 경로↔owner 구조적 매칭만 강제, owner 적절성은 리뷰어 위임. 점진 승격 = OPA Gatekeeper `enforcementAction`(warn→deny, source: OPA Gatekeeper) — Story 2 가 warning tier 부터.

### 결정 5 — 상위 자동화 = ADR-069 Phase 2 구현 (story-init.yml components 소비, Story 3)

상위 multi-repo 발급 자동화(`story-init.yml` 이 예약필드 `repos[].components` 를 소비 → repo-target 자동 라우팅 + 토폴로지 SSOT 대조)는 **ADR-069 Phase 2 구현**이다 (Story 3 carrier). 본 ADR 은 그 mechanism 을 *격상 codify* 만 하고, 실 구현은 Story 3. ADR-069 Amendment 1 (동반 발의)이 `repos[].components` → repo 라우팅 Phase 2 codify 를 담고, "소유레포 결정 source = ADR-131 토폴로지 SSOT" cross-ref 로 069 §결정4 priority 1(frontmatter 소유레포)의 채움 source 가 131 임을 못박는다.

## axis-disjoint 5-checklist 자기적용 (ADR-086 동형)

신규 chief 권한 확장이 기존 roster 권한을 축소·중복하지 않음을 5-checklist 로 논증:

1. **axis disjoint** — 토폴로지 SSOT author(**repo-level 소유 배치**) ⊥ ModuleArch(**레포 *내부* boundary**) ⊥ RefactorAgent(**repo-분해 *advocacy***). 세 축 비중첩 — 같은 결정을 두 에이전트가 R 로 갖지 않는다.

2. **RefactorAgent advisory 무축소 (verbatim 박제 — AC-5)** —

   > 배치 결정 강제 = 소유레포 *확정·기록* 강제이지 *분해 제안* 강제 아님 — RefactorAgent advisory(escalation-tier 제안) 무축소

   RefactorAgent 의 repo-분해 *pressure 식별·제안*(escalation-tier) 권한은 무손상이다(RefactorAgent.md:46). ADR-131 이 강제하는 것은 소유레포의 *확정·기록*이지 *분해 제안*이 아니다. 이 한 줄 없으면 구현리뷰가 mandate 축소로 오판한다.

3. **RACI R 단일** — 소유레포 *확정*의 R = chief 단독 (ADR-042:876 기존 귀속 명시 확장). 신규 R row 0 — RACI matrix 에 신규 행 추가 없음 (authority pre-exists, deputy-mandate SKILL.md 편집 = Story 1 scope 외).

4. **deputy 0 신설** — 영구 deputy roster(6 permanent) 무변경 (ADR-042 6 permanent 무손상). chief 책임 확장 wording 만 — 신규 영구·CONDITIONAL deputy 0.

5. **fail-safe layer 분리** — "공백 PASS"(consumer 정책 opt-in) ≠ ADR-130 fail-closed(wrapper 구조). 두 layer 모순 아님 (결정 2 verbatim).

## Out-of-Scope (MVP 경계 — 의도적 비대상, 명시 의무)

- **책임 *의미단위* 깊은 파생검증** — "선언된 소유레포가 *의미상 올바른* 도메인 레포냐"의 양방향 declared↔derived 검증은 **마커 시스템 선결**이라 본 Epic scope 외. **deferred follow-up (별도 CFP)** — 책임 마커 시스템이 먼저 구축돼야 의미단위 파생이 기계화 가능 (AC-8). 게이트는 구조적 사실(고아/중복/거친 drift)만 hard-block, 의미 판정은 "리뷰어 근거인용 attestation 요구"로만(승인 자체는 대신 판단 안 함 — 검사연극 금지, ADR-119 정합).
- **게이트 실행 스크립트** (고아/중복/거친파생 hard-block 로직) — **Story 2** carrier.
- **story-init.yml multi-repo 발급 자동화** (`repos[].components` 소비 라우팅) — **Story 3** carrier.
- **consumer adoption** (mctrader 우회 스크립트→정품 교체) — 본 Epic 밖 별도 follow-on.

## collision check

`git ls-tree origin/main archive/adr/` numeric max = **ADR-130** (Epic CFP-2394 Story A, CFP-2395 carrier) → **131 free**. ADR-RESERVATION.md 등록 max row = **130** (CFP-2395 점유). → row 131 append 정합 (verified-via worktree base `b469bd41d8f889f664a4263db6c06e7e1cf41bc3` + commit 직전 재verify). ADR-129(CFP-2392 OMC-adopt) · ADR-130(CFP-2395) 모두 file 실재 = numeric max 130 확정.

## 결과

### Positive

- cross-repo 책임 배치가 1급 산출물로 격상 — 감사가능성·책임추적성·일관성 (UC-1/2/3).
- 신규 영구 에이전트 0 + 신규 RACI R 0 — roster·governance surface 무팽창 (chief authority pre-exists).
- consumer opt-in 무손상 — frontend-only/단일레포 consumer 비차단 (정책값 공백 PASS, EC-1).
- Story 2/3 의 검사·대조 대상 전제 확정 (스키마 = S2 검사대상, S3 대조대상).

### Negative

- Story 1 은 *선언만* — 실 enforcement(hard-block)는 Story 2 까지 미실현 (의도적 Phase 분리, 회귀 0 차단 — 신규 required check 가 기존 PR 영구 차단하지 않게).
- 깊은 파생검증 deferred — 의미단위 정합은 당분간 리뷰어 attestation 에 의존 (마커 시스템 선결).

### Neutral

- 토폴로지 SSOT 물리 위치 = `docs/project-config-schema.md` 신규 섹션 (overlay 스키마 SSOT 와 응집, doc-locations.yaml trigger 없음 — 기존 섹션 확장). chief write surface = ArchitectAgent.md permissions allow-list 에 `docs/project-config-schema.md` 추가로 정합 (write-surface 갭 해소, AC-4).

## 해소 기준

N/A — permanent policy (영구 강화 ratchet, 약화 surface 0 — chief authority 확장 + 메타불변식 추가, sunset_justification 비대상 ADR-058 §결정 5).

## Amendment 1 (CFP-2428 — declared-marker layer 신설, Epic CFP-2418 deferred FU)

> [Amendment 1 — carrier CFP-2428, 2026-06-26 KST] §결정 3/4 가 명시 deferred 한 **"책임 의미단위 깊은 파생 — 마커 시스템 선결"** 의 **marker layer(L1 코드→책임)** 를 신설한다. ratchet **강화 방향**(governance 확장 — marker layer 추가) — 약화 surface 0. 본 ADR 의 L2(책임→레포) 메타불변식 게이트(§결정 2/3, CFP-2422)의 **sibling layer**. 신규 ADR 번호 0 (Amendment — ADR-RESERVATION 무변경).

### A1-1 declared-marker layer(L1 코드→책임) 신설 — §결정 3/4 deferred 의 marker layer 실현

§결정 3/4 + Out-of-Scope 가 "책임 의미단위 깊은 파생검증 = 마커 시스템 선결 → deferred follow-up (별도 CFP)" 로 미룬 그 **별도 CFP = CFP-2428**. 본 Amendment 는 deferred 항목 중 **marker layer 자체**를 신설한다:

- **L1 marker layer = 코드↔책임 marker manifest** — consumer overlay 의 per-repo "경로/모듈 → 책임" 선언 산출물(`repo_topology.responsibility_markers[]`). 본 ADR 의 **L2(책임↔레포 = `repo_topology.responsibilities[]`)** 와 **검사 layer 가 disjoint** — L2 게이트(CFP-2422)는 책임의 *소유레포* 정합(고아/중복/거친파생), L1 게이트(CFP-2428)는 책임의 *코드 위치* 정합(unmarked/불일치/stale). 둘이 합쳐져 **L1→L2→L3(fs) transitive 일관성**을 완성한다 (보강 관계, 중복 0).
- **join-key = `responsibility` byte-identical namespace 계약** — L1 manifest 의 책임 식별자와 L2 `repo_topology.responsibilities[].responsibility` 가 **byte-identical 동일 namespace**. 이 키가 두 선언 산출물(L1·L2)을 묶는 유일 연결고리이며, drift 검출은 이 키 기준 set 대조로 환원(의미 추론 0 — 문자열 매칭).

### A1-2 재정의 명문 — "의미단위 깊은 파생" 중 *의미* 부분은 검사연극이라 불가, *구조* 일관성만 기계화

§결정 3/4 의 deferred 문구("마커 시스템 선결 → 책임 의미단위 깊은 파생/검증 기계화")는 *의미 정합의 기계 추론*을 약속하는 뉘앙스였으나, CFP-2428 Phase 0 외부도구 조사(ArchUnit·Nx tags·Bazel·CODEOWNERS·dependency-cruiser·CodeQL — source: 6 도구 firsthand 조사) 결과 **코드의 *의미*를 추론해 "이 코드 = 책임 R" 을 자율 귀속하는 도구는 0** 으로 판명. 전부 **사람 선언 마커 + 구조 대조** 방식. 따라서:

- **"의미단위 깊은 검증"의 *의미* = (불가능한) 의미 추론이 아니라 선언마커 transitive 일관성**이다 — L1(코드↔책임 marker manifest) + L2(책임↔레포 topology) + L3(실제 fs 위치)의 transitive 일관성 + drift 검출(실현 가능). 의미 추론(불가·검사연극·ADR-119 위반)이 아님.
- **honest promise-gap acknowledge (silent drop 아님)**: 본 ADR deferred 문구의 "의미단위 깊은 파생" 중 *구조* 부분만 CFP-2428 이 기계화하고, *의미* 부분("이 책임이 *의미상* 옳은 도메인 레포냐")은 **사람 attestation 으로 영구화**(기계 자동화로 흡수되지 않음). 간극을 조용히 누락하지 않고 명시한다 (ADR-119 정합).

### A1-3 drift 3종 = warning-tier (점진 승격, CFP-2422 동형)

L1 marker drift surface 3종 — 전부 **구조적 사실**(set membership / 문자열 동등 / 경로 존재)이라 기계 단정 가능, false GREEN/RED 0:

- **(a) unmarked** — L2 토폴로지가 선언한 책임 R 이 L1 manifest 에 entry 0 (`R ∈ topology.responsibilities` 이나 `R ∉ manifest`). set-diff `topology.responsibilities − manifest.responsibilities ≠ ∅`.
- **(b) marker↔topology 불일치** — L1 manifest 의 책임 R 이 가리키는 레포 ≠ L2 `owner_repo[R]`. 문자열 동등 `manifest[R].repo ≠ topology.owner_repo[R]`.
- **(c) stale marker** — L1 manifest entry 경로/모듈이 L3 실제 fs 에 부재(이동·소멸 코드). 경로 존재 fs-stat `os.path.exists`.

세 종류 모두 **warning-tier(continue-on-error 비차단)** — §결정 3 의 L2 게이트와 동형 점진 승격(OPA Gatekeeper `enforcementAction` warn→deny — source: OPA Gatekeeper). hard-block ratchet 은 증거 축적 후 **별도 후속 CFP** (본 Amendment scope = warning 까지). manifest 자체가 stale 될 수 있는 자기적용 함정은 warning-tier 라 *차단 아닌 변경시점 surfacing* 으로 회피 (hard-block 이었다면 manifest 갱신 누락이 무관 PR 을 막는 자기모순 — CFP-2422 동형).

### A1-4 의미정합 attestation 영구화 — review-responsibility 행 (d) 무변경

§결정 4 의 "의미적 정합 = 사람 판정" 은 marker layer 도입 후에도 **무변경**:

- 기계는 *선언 마커의 구조 일관성 + drift 3종* 만 담당. "risk-metrics 책임이 mctrader-engine 에 있는 게 *도메인상* 옳은가" 는 review-responsibility 매트릭스 **attestation 행 (d)**(리뷰어 근거인용)에 영구 위임 — 기계가 단정하면 검사연극(false GREEN/RED, ADR-119 위반).
- review-responsibility 매트릭스 attestation 행 (d) **무변경** (marker 도입 = 구조 검사 layer 추가일 뿐 의미 판정 자동화 0).

### A1-5 axis-disjoint + ratchet 강화 (약화 surface 0)

§axis-disjoint 5-checklist 동형 자기적용 — marker layer 신설이 기존 roster/게이트 권한을 축소·중복하지 않음:

1. **axis disjoint** — L1 marker layer(**코드↔책임 위치 정합**) ⊥ L2 topology(**책임↔레포 소유 정합**, 본 ADR §결정 2) ⊥ ModuleArch(**레포 *내부* boundary**) ⊥ RefactorAgent(**repo-분해 advocacy**). 검사 명제 비중첩(같은 join-key `responsibility` 공유하나 대조 대상 disjoint).
2. **deputy 0 / RACI R row 0** — 영구·CONDITIONAL deputy roster 무변경, 신규 advocate 에이전트 0, 신규 RACI R row 0 (marker manifest 스키마 author = ArchitectAgent chief, 기존 §결정 1 토폴로지 SSOT 1급 author 권한의 자연 확장).
3. **wrapper 메타불변식만 / consumer overlay 주입** — wrapper 는 schema 유효성 + join-key namespace 일관성만 강제, 구체 "어느 경로 = 무슨 책임" 맵은 consumer overlay 주입(consumer-authored, wrapper write 0). **공백/미주입 = PASS**(layer 분리 fail-open, §결정 2 동형).
4. **ratchet 강화** — marker layer 신설 = governance 확장(강화 방향), 약화 surface 0. `is_transitional: false` 유지 (sunset_justification 비대상, ADR-058 §결정 5).

### A1-6 신규 ADR 0 + Phase 분리

- **신규 ADR 번호 0** — Amendment 이므로 ADR-RESERVATION 무변경 (본 Amendment 발의 시 reservation max = 131 = 본 ADR 자신, 신규 row append 0).
- **Phase 분리 (ADR-127)**: CFP-2428 Phase 1 = 본 Amendment(선언만). Phase 2(구현 lane) = `docs/project-config-schema.md` marker manifest 스키마 본문 + drift-check 스크립트(`check-responsibility-marker-drift.sh` + `lib/check_responsibility_marker_drift.py`) + warning-tier workflow(templates + `.github` byte-identical) + discriminating tests. branch protection 6-tuple 무변경 invariant 절대 보존(non-required warning-tier).
- **상세 설계 SSOT** = Change Plan `<internal-docs>/wrapper/change-plans/cfp-2428-responsibility-marker-drift.md` + Story CFP-2428 §3.

## 관련 파일

- [`docs/project-config-schema.md`](../../docs/project-config-schema.md) — 토폴로지 SSOT 스키마 (overlay 주입형) 신규 섹션
- [`archive/adr/ADR-069-multi-repo-story-key-system.md`](ADR-069-multi-repo-story-key-system.md) — Amendment 1 (components→repo 라우팅 Phase 2 codify, 소유레포 source cross-ref)
- [`archive/adr/ADR-RESERVATION.md`](ADR-RESERVATION.md) — row 131 append
- [`plugins/codeforge-design/agents/ArchitectAgent.md`](../../plugins/codeforge-design/agents/ArchitectAgent.md) — 토폴로지 SSOT 1급 author 권한 확장 + write-surface 갭 해소
- [ADR-042](ADR-042-agent-model-selection-policy.md) — chief repo-level boundary authority (L876) cross-ref
- [ADR-130](ADR-130-applicability-closure-integrity.md) — 메타불변식 게이트 계보 (⚠ layer 분리)
- [ADR-069](ADR-069-multi-repo-story-key-system.md) — components 예약필드 활성화 (Phase 2)
- [ADR-086](ADR-086-deputy-creation-decision-framework.md) — axis-disjoint 5-checklist 동형
- [ADR-020](ADR-020-cross-repo-epic-pattern.md) — Story file 라우팅 조직 패턴 (직교 anchor)
- [ADR-119](ADR-119-research-before-claims.md) — 검사연극 금지 + 외부지식 source 인용 정합
- Change Plan: [`<internal-docs>/wrapper/change-plans/cfp-2419-cross-repo-placement-governance.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-2419-cross-repo-placement-governance.md)
- Story: [`<internal-docs>/wrapper/stories/CFP-2419.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-2419.md)
