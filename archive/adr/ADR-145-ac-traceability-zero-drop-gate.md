---
adr_number: 145
title: 요건 traceability zero-drop 게이트 — AC-ID 부여 + phase-aware 2-tier presence/mapping fail-closed (semantic 천장 정직 공개)
status: Accepted
category: governance
date: 2026-07-11
carrier_story: CFP-2603
supersedes: []
related_adrs:
  - ADR-006  # §8 Test Contract authoring mechanism owner — 이 mechanism 이 AC-1..AC-8 emit. Amd2 L266 "presence-anchor completeness 를 real 인 양 강제 = 검사연극" = 본 게이트 천장(AC-8) 의 isomorphic 선례. G1 = 이 관례를 요구사항 단계 범용 AC-ID 로 일반화 (충돌 아님, 상류 확장)
  - ADR-008  # Inter-plugin Contract Versioning — requirements-output-v1 count→AC-list = additive MINOR(v1.2, count 보존) / design-output-v2 marker = additive MINOR(v2.5). count 제거 MAJOR 회피 (CONFLICT-A 해소, §결정 6)
  - ADR-119  # research-before-claims — 게이트는 proxy 아닌 ground-truth 검증. presence/mapping 만 fail-closed, semantic 완전검증 강제하는 척 = 검사연극(§결정 4). 천장 정직 공개(2 잔여, §결정 5)
  - ADR-125  # 요구사항리뷰 lane — §결정2 "branch-protection 6-tuple 불변" 선례는 phase-gate INTERNAL 흡수 전제. 본 ADR 은 fail-closed 비호환(anchor=warning-tier + fast-pass bypass 실측)으로 이 선례를 override 하고 신규 required job 정당화 (CONFLICT-C, §결정 3). §5.6 RO-1 = ADR-125 Amd2-style additive disjoint 축 신설 선례
  - ADR-127  # no-exemption 정식 풀 플로우 — 게이트에 skip/opt-out/default-green 경로 신설 금지 상위 원칙. transition = forward-only + grandfather (skip-toggle 금지, §결정 4 AC-7)
  - ADR-069  # Multi-Repo Story Key System — AC-ID owner 아님 (오귀속 정정, Domain+Continuity 이중 확인). AC-ID = Story-local namespace, ADR-069 Key system 과 disjoint
  - ADR-052  # 요구사항 single-shot / divergence debate — user→AC hop defense-in-depth 3층 중 (c) Codex proactive check divergence
  - ADR-136  # frontend 품질게이트 표준 — Amd3 L1/L2/L3 execution-liveness 3요건 + L3 "linter 자체 mutation-self-test" (born-missing linter file∧function grep-only = CFP-2545 false-oracle → §8 linter self-test, CONFLICT-B 해소). frontend.applicable default-false 2-layer 동형(consumer-applicability)
  - ADR-133  # ADR-RESERVATION atomic claim — 본 ADR 번호(145) claim→write→row-append 3-step 발급 (claimant ArchitectAgent:CFP-2603)
  - ADR-060  # shadow-required 승격 evidence-gate 선례(§결정 6/19) — 본 ADR 에서 (B) shadow-required = 미채택 대안(§대안); 채택 = (A) 즉시 required. ModuleArch digest 의 "ADR-130 §결정6 7-day-green" 오citation 정정 (ADR-130 = applicability⊥closure, 무관)
  - ADR-005  # N/A 명시 패턴 — §11 데이터 마이그레이션 N/A (wrapper-self governance, schema/data 무변경) 근거
  - ADR-068  # boundary invariant I-1~I-5 — deputy mandate boundary (chief tie-break ladder 2단계) + I-3 guard placement(unconditional 우선) + I-4 wording SSOT
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs). ADR-127 :115 정합
  - ADR-151  # (Amendment 1) G6 형제 — live=6-tuple ↔ doc=7-tuple divergence 를 "CFP-2609 reconcile 대기"로 명문 기록(ground-truth). §결정 8 이 그 reconcile carrier. self-test execution-liveness = 등록 ordering invariant 의 self-test green 채널 근거
  - ADR-152  # (Amendment 1) G3 형제 — Epic CFP-2602 "게이트 G당 1 신규 ADR" 패턴이 신규 게이트에만 적용됨(152=G3 dark-path 점유)을 A2-5 판정에서 인용. CFP-2609=G1 완결 carrier(신규 게이트 아님) → Amendment 채택 근거
  - ADR-130  # (Amendment 1) applicability⊥closure positive-whitelist — per-PR applicability(축 c) 가 consumer-배포 applicability(축 a)·repo-guard(축 b)와 disjoint 함의 selector. positive detection·non-suppressible 성질 차용(§결정 8 B)
related_concepts:
  - ac-traceability-zero-drop
  - presence-mapping-ceiling-honesty
  - per-pr-applicability-scoping
is_transitional: false
---

# ADR-145 — 요건 traceability zero-drop 게이트 (AC-ID + phase-aware 2-tier presence/mapping fail-closed)

## 상태

Accepted (2026-07-11 KST) — CFP-2603 (Epic CFP-2602 G1) carrier. 사용자 요건이 요구사항→설계→§8 테스트→구현 사슬을 지나며 조용히 증발하는 병(Gap A, 요건-현실 갭)을 도메인 불변식 위반으로 재정의하고 기계 게이트로 강제하는 governance SSOT. 강화(ratchet↑) 방향 — 기존 게이트 무변경 위에 신규 fail-closed 게이트 1개 + 계약 2 additive MINOR + review obligation 1축 추가. 약화 surface 0.

**Amendment 1** (2026-07-12 KST, CFP-2609 — Epic CFP-2602 G1 완결 carrier): **§결정 8** 신설 — (1) per-PR applicability 가드(신호 C = resolved authoritative §5 ≥1 normative AC presence, 3번째 applicability 축) (2) §결정4 no-optout 정의역 명확화("opt-out(적용 PR escape) ≠ applicability-scoping(비대상 판정)", exception-through-interpretation 봉인) (3) I-APPLIC 불변식(objective ∧ non-suppressible ∧ 판정불가≠비적용 anti-degradation ∧ forward-only) (4) 단일 판별 모델(phase × resolve-outcome 매트릭스) (5) §결정3 이 선언한 6→7 required 등록의 미완결 reconcile 완결(live=6-tuple → doc=7-tuple 로 승격, ADR-151 이 명문한 divergence 해소). ratchet↑ 방향 — scope 정정(false-red 제거)이지 검출력 약화 아님. 약화 surface 0. **§결정1-7 무supersede·무rewrite**(append-only).

## 컨텍스트

사용자 원문(Story §1 verbatim): mctrader 개발 중 "5분/1시간 compactor" 요건을 세 번 주장했으나 반영되지 못함. 3-angle forensic 실측 결과 = 요건이 lane 경계를 넘으며 증발(Gap A). 실측된 증발 지점:

- **유일 계약 `requirements-output-v1` 이 AC 전체를 `sub_agent_results.analyst.acceptance_criteria_count: <int>` 정수 하나로 붕괴** [verified: `docs/inter-plugin-contracts/requirements-output-v1.md` L90, origin/main]. 항목 identity 소멸 → 하류 lane 이 "사용자가 요구한 것의 체크리스트"를 하나도 쥐지 못함.
- `scripts/lib/check_story_section_schema.py` = §N 헤딩 존재만 검사(§1~§11 strict), AC↔테스트 매핑 로직 부재, fail-closed `sys.exit(1 if errors>0)` [verified: L133-140].
- `.github/workflows/phase-gate-mergeable.yml` = 단일 job `check-gate` [verified L21]. **anchor 계층(CFP-900 §4.13 L369 / S6 provenance L581 / S7 L648)이 전부 `checks.create` 이후 try/catch-silent warning-tier** [verified] + **fast-pass OR-gate(`isEpicLabel||isSiblingPr||isPostMergeFix||isLabelMismatchOnly`) L359 → early-return success L414-423** — Epic/sibling PR 은 in-line matrix 를 우회.
- 각 lane 이 사용자 요건을 산문으로 재해석해 자기 범위를 스스로 재도출 → 항목 침묵 삭제가 전 게이트 green.

도메인 불변식 **I-AC**: "AC 는 사용자 의도의 안정적 참조자이며 lane 경계를 넘어 보존돼야 한다." 현재 계약은 identity(AC-N)를 정수 count 로 붕괴시켜 이를 깬다.

외부 근거(Story §6 재인용 — 신규 외부 단정 없음): RTM + bidirectional traceability 는 확립된 관행이다 (ISO/IEC/IEEE 29148 traceability mechanism / DO-178C §5.5(Software Development Process Traceability)·§6.4 상위요건↔하위요건↔검증자산 양방향 필수 / NASA SWE-052·SWE-059 bidirectional). 동시에 RTM 은 드롭을 **줄이지만 없애지 못한다** — traceability rot / 유지비용 / rubber-stamping (Jama Software). ∴ 자동화로 rot·수동오류는 저감하나 semantic 완전성 봉인은 불가(§결정 5 근거).

## 결정

AC 에 lane 경계를 넘어 안정적인 식별자(AC-ID)를 부여하고, `AC-N ↔ §8 명명 테스트 ↔ 실 테스트파일` zero-drop 을 신규 fail-closed 기계 게이트로 강제하되, 기계가 강제 가능한 것(presence/mapping)의 천장을 정직히 공개한다. 착지 = 신규 lint 모듈 + 신규 required workflow + 계약 2 additive MINOR + 요구사항리뷰 lane 3번째 disjoint 축.

### 결정 1 — presence/mapping 천장 + no-hollow 정직 (ADR-006 Amd2 L266 isomorphic)

- **기계 게이트는 presence/mapping 까지만 fail-closed 로 강제한다**: (i) AC-N well-formed + §5.2 **machine-enforced 필수 4필드(id/statement/source/tier)** 존재·well-formed (derived 필드 verification/coverage_required/phase = §결정6 파생, Hop1 미재검증), (ii) 모든 AC-N → ≥1 §8 명명 테스트 매핑, (iii) 명명 테스트의 실 파일 ∧ 실 symbol 존재(born-missing 차단).
- **"테스트가 요건을 의미상 올바르게·완전히 검증하는가"(semantic correctness/completeness)를 강제하는 척 = 검사연극** — ADR-006 Amd2 L266("presence-anchor completeness 를 real 인 양 강제 = 검사연극")의 **isomorphic 선례**를 직접 적용한다 (ADR-119 §결정 4 정합).
- **두 잔여 정직 공개 (no-hollow honesty)**: (a) test-semantic 완전성 미강제, (b) **user→AC 분해-완결성**(AC 집합이 사용자 의도에 완전한지) 미강제. 둘 다 fail-closed 아니며 §결정 2 review obligation + advisory 로 mitigate. **"완전 봉인" hard-claim 금지** — "구조적 born-missing fail-closed + semantic 저감 + 잔여 정직 공개"로 재약속.
- **(c) layer-separation clarification (잔여 아님 — count 는 2 유지)**: §5.2 derived 필드(verification/coverage_required/phase) 완결성은 **미강제 잔여가 아니다** — 계약(requirements-output-v1)·Hop2·review 층에서 실제 강제되며, 게이트의 §5-parse Hop1 만 재검증하지 않는다(강제 지점 이동, 미강제 아님). ∴ 잔여 count = **2 로 유지**(`CEILING_DISCLOSURE`·Change Plan §3.2(e)/§8.1 정합). required 4필드(id/statement/source/tier)는 Hop1 `validate_ac_record` fail-closed 로 강제(AC-2 non-hollow).

### 결정 2 — phase-aware 2-tier + 3-tier AC model + user→AC review obligation

**phase-aware 2-tier** (ADR-127 Phase 1 문서 / Phase 2 구현 PR 분리 정합 — Phase 1 시점 실 테스트파일 부재하므로 단일 tier 는 전면 false-FAIL):
- **Tier-1 (Phase 1)** = AC-N ↔ §8 계약에 **명명된** 테스트 fidelity (이름·매핑 존재). born-missing 미실행.
- **Tier-2 (Phase 2)** = §8 명명 테스트 ↔ **실 파일 ∧ 실 symbol** 존재.
- **phase 신호 = EXPLICIT** (Story frontmatter `phase:` / workflow `--phase` 명시 인자) — diff 추론 금지 (TestContract dissent-1 채택, ambiguity 제거).

**3-tier AC model** (§5.2 `tier` enum — Risk5 bypass surface 대응 §결정 2 하단):
- `normative` = fail-closed 기계 강제 (AC-1a·AC-2..AC-9). §8 명명 테스트로 커버.
- `declared` = fail-closed 아님, human/review-verified obligation (AC-1b). 대조할 요건 인벤토리 부재로 기계 강제 불가 — §5.6 RO-1 이 검증. **forged machine test 금지**.
- `advisory` = 경보만, blocking FAIL 권한 없음 (AC-10).

**user→AC review obligation (RO-1)**: 첫 hop(사용자 산문 → AC 민팅)은 대조할 요건 인벤토리가 없어 fail-closed 불가(Hop0). 요구사항리뷰 lane 이 §1 verbatim 사용자 원문 ↔ §5 AC 목록을 대조하여 "구별되는 각 사용자 요건이 ≥1 AC 에 매핑됨"(AC-1b 완결성)을 검증한다(미매핑 = review FIX, 설계 진입 차단). **ADR-125 Amendment 2 방식의 additive disjoint 축** — 요구사항리뷰 lane 의 3번째 축(external-fact / internal-invariant / **AC-decomposition-completeness**)으로 편입. binding = `requirements.md` review-checklist + `RequirementsReviewPLAgent.md` + `codeforge:review-responsibility` matrix. **tier 배정 검증 동반 (Risk5)**: user AC 를 advisory 로 오분류하면 강제가 약화되므로 RO-1 이 tier 배정 자체를 review-gate 한다.

- **defense-in-depth 3층** (user→AC hop, 모두 fail-closed 아님을 결정 1(b)가 공개): (a) RO-1 §1↔§5 diff + (b) AC-10 advisory 반복주장 신호 + (c) ADR-052 divergence(Codex proactive).

### 결정 3 — 신규 dedicated required workflow (CONFLICT-C divergence 정당화)

- **phase-gate-mergeable.yml 확장 기각 (Feasibility Barrier 1)**: check-gate 에 in-line matrix 를 얹으면 두 실패 모드 — (a) anchor 계층과 동형인 warning-tier(merge 미차단, ratchet 0) 또는 (b) fast-pass OR-gate(L359→L414-423) 로 Epic/sibling PR bypass. 양쪽 다 fail-closed 요건(AC-7)과 비호환. [verified: phase-gate-mergeable.yml L369/L581/L648 warning-tier + L359 fast-pass bypass, origin/main]
- **신규 dedicated workflow `.github/workflows/ac-traceability-matrix.yml`** (job-id = context name `ac-traceability-matrix`, double-context 회피) 를 **day-1 hard-fail** 로 배선한다 — fail-closed 로직 즉시 활성(실 red/green + PR red X).
- **wrapper-self-only 확정 (F1 — consumer born-broken 방지)**: 신규 workflow 는 `ALLOWED_HUB_REPOS: mclayer/codeforge-internal-docs` 하드코딩 + fail-closed no-optout 이라 consumer repo 에 배포되면 consumer venue≠whitelist → return false → 전 consumer PR born-broken hard-block. venue-shape self-test job wrapper-guard 선례를 따라 workflow 에 **repo-guard `if: github.repository == 'mclayer/plugin-codeforge'`** 를 명시한다(`templates/github-workflows/` byte-identical copy 도 동일 guard 상속 → consumer 배포 시 inert job skip). consumer 전파(ALLOWED_HUB_REPOS venue 파라미터화 + `project.yaml` applicability 게이트)는 **별도 follow-up Story** — 지금 consumer 활성 배포 금지(§대안·Change Plan §12.1).
- **CONFLICT-C divergence 정당화**: ADR-125 §결정2 "branch-protection 6-tuple 불변" 선례는 phase-gate **INTERNAL 흡수**(요구사항리뷰 gate 를 기존 check-gate 로 매핑)를 전제했다. 본 게이트는 그 흡수 경로가 **fail-closed 비호환**(anchor=warning-tier + fast-pass bypass 실측)이므로 선례가 성립하지 않는다 → 신규 required job 이 정당하다. ADR-125 선례 override 는 **비호환 근거에 한정**되며 6-tuple 불변 원칙 자체를 폐기하지 않는다.
- **branch-protection required_contexts 등록(6→7-tuple) = 사용자 결정 → 채택 = (A) 즉시 required 등록** (2026-07-11 사용자 결정): G1 게이트를 도입하는 Phase 2 PR 머지 시점에 `required_status_checks.contexts[]` 에 신규 context `ac-traceability-matrix` 를 즉시 추가(6→7-tuple). CLAUDE.md "브랜치 보호" 표 + arch-doc C4 갱신은 Phase 2 PR 동반.
- **A 채택의 born-broken 안전 전제 (핵심 정당화 — 2 guard 구분)**: 즉시 required 의 실패 모드는 둘이며 각각 별 guard 로 차단된다 —
  - **(i) false-green (permissive/hollow)** = 게이트가 결함을 놓쳐 무의미하게 통과 → **§8 self-test(mutation-kill A/B/C + F-fixture 12종 RED→GREEN)가 merge-precondition** 으로 차단(hollow 린터는 self-test RED 로 merge 불가).
  - **(ii) false-red / born-dead** = 게이트가 정상 PR 을 오차단하거나 아예 실행되지 않음 → **workflow-runs-on-own-PR**(G1 도입 Phase 2 PR 자체가 신규 게이트의 실 red/green 을 산출)로 검출.
  - **∴ ordering invariant (등록 순서 강제)**: `workflow 착륙 → self-test suite green 확인 → 게이트가 자기 PR 에 실 green 산출 확인 → THEN required_contexts 등록`. 이 순서를 지키면 born-broken 린터는 required 로 등재 불가. 안전 전제 = **self-test green ∧ own-PR green**(born-broken gate class 대비 — CFP-2530 css-lint born-invalid / CFP-2535 execution-liveness 계보). false-red 재발 시 revert = trivial(§결과·Rollback).
- (참고: ModuleArch digest 의 "ADR-130 §결정6 7-day-green" 은 오citation — ADR-130 = applicability⊥closure 분류. shadow-required 승격 evidence-gate SSOT = ADR-060 §결정 6/19. 본 결정에서 shadow-required(B)는 §대안 참조 — 고려됐으나 미채택.)

### 결정 4 — fail-closed no-optout + AC-ID namespace + sub-letter grammar

- **fail-closed no-optout (AC-7)**: skip-PASS / opt-out / default-green 경로 부재. 판정 불가(cross-repo fetch 실패 / token 부재 / 403·404)는 **helper fail-closed 패턴**(phase-gate-mergeable.yml `if(!token) return false` L232 형)을 재사용 — main-path degrade(L69-70 PR-label fallback)는 재사용 금지. **403/404 conflation 가드**: born-missing verdict 는 `resp.ok` 확인 후에만 — "읽을 수 없음"을 "존재하지 않음→verdict 없음"으로 해석 금지.
- **fetch 물리 재구현 회피 (F2 — Phase 2 carryover)**: adapter-층 cross-repo fetch(PAT/whitelist/token/`resp.ok` 403-404 가드)를 phase-gate 로부터 물리 복제하면 2 divergent copy = drift 위험. 본 결정은 "개념 재사용" 선언에 그치지 않고, Phase 2 에서 cross-repo fetch 를 **shared reusable-workflow / composite-action 으로 추출**해 단일 소유·재사용할 의도를 명시한다(비차단, ADR-042 Amd13 reusability 정합).
- **4 bypass vector 차단(F-AC7-a..d)**: 빈 AC 목록 / 미선언 §8 / stub 명명 회피 / phase 오선언.
- **transition = forward-only + grandfather** (Story date/KEY 기준). **skip-toggle 신설 금지** — toggle 은 ADR-127/AC-7 opt-out 이 된다.
- **AC-ID namespace = Story-local** (`AC-N`); cross-Story 참조 = `<KEY>:AC-N`.
- **AC_ID_RE SSOT = sub-letter 수용** (`^AC-(\d+)([a-z])?$`): 본 Story 자체의 `AC-1a`/`AC-1b` sub-letter ID 가 naive `AC-\d+` regex 에 조용히 drop 되면 zero-drop 위반(CRITICAL TRAP — RefactorAgent). AC_ID_RE 는 단일 SSOT leaf(`scripts/lib/ac_id.py`)로 추출하여 lint·계약·후속 재사용이 공유한다.

### 결정 5 — born-missing = 실 symbol/node resolve (grep 금지) + linter self-test (CONFLICT-B)

- **born-missing 검출 = 실 파일 ∧ 실 symbol resolve** (Python `ast` 파싱으로 명명 테스트 함수/클래스 node 존재 확인) — **grep 금지**(F-ORACLE-GUARD). presence-grep(파일∧함수 문자열 매칭)은 CFP-2545 false-oracle 계열 결함(주석·docstring·문자열 안 매칭 = 거짓 PASS).
- **linter 자체 mutation-self-test 의무** (ADR-136 Amd3 L3 / CFP-2535 execution-liveness): "file∧function grep 만으로 born-missing 판정" 자체가 false-oracle 이므로, born-missing linter 는 자기 자신을 mutation A/B/C 로 반증 통과해야 한다. §8 Test Contract 에 linter self-test 포함.

### 결정 6 — 계약 2 additive MINOR (CONFLICT-A 회피)

- **`requirements-output-v1` v1.1 → v1.2 (additive MINOR)**: 기존 `sub_agent_results.analyst.acceptance_criteria_count: <int>` **보존**(제거 = MAJOR = CONFLICT-A). 신규 top-level `acceptance_criteria[]`(optional, `sub_agent_results`/`writes_completed` 와 peer) 추가 — 각 item = §5.2 스키마 **2-등급**: **required(id/statement/source/tier) = machine-enforced (Hop1 `validate_ac_record` fail-closed, AC-2 non-hollow)** + **derived(verification/coverage_required/phase) = 파생(`coverage_required←tier+Hop2` / `phase←run-phase+tier` / `verification←tier+Hop2·review`), present 시 format-only, 완결성 = 계약·Hop2·review 층(게이트 §5-parse 미재검증)**. **게이트가 list 실재를 강제**(AC-3 항목화 전달)하되 **계약 field 는 영구 optional 유지**(ADR-008 §결정2 backward-compat MINOR).
- **`design-output-v2` v2.4 → v2.5 (additive MINOR, Model A)**: `chief_author_artifact.ac_coverage_self_check_passed: bool` marker 추가 (기존 self-check disjoint 축 group `architecture_doc_updated` 등과 peer, default false). marker 텍스트 = "**authoritative Test Contract location** 에서 AC↔§8 coverage self-check 통과"(문서유형별 — "Story §8" 단정 금지). packet 에 RTM 중복 금지(marker bool 만).
- **RTM location-resolution 규칙 (P1 — 게이트가 Test Contract 를 resolve 하는 위치)**: 게이트는 §8 Test Contract(RTM)를 **그것이 authoritative 하게 존재하는 위치**에서 resolve 한다 — **wrapper-self dogfood Story = Change Plan §8**(Story §8=개발서사 placeholder 일 때) / **consumer Story = Story §8 mirror**. 이 규칙이 없으면 Phase 2 구현자가 wrapper-self 의 Story §8(placeholder)을 파싱 → 본 Story 자신의 Phase 2 PR 을 false-FAIL(게이트가 막으려는 바로 그 silent location-mismatch). 게이트 입력은 문서유형 판별 후 authoritative location 을 선택한다.
- **MANIFEST 3-point parity** (Phase 2 mechanical sync): 각 계약의 (i) frontmatter contract_version, (ii) 본문 version, (iii) `docs/inter-plugin-contracts/MANIFEST.yaml` entry 를 동시 이동(v1.2 / v2.5). atomic.

### 결정 7 — 모듈 경계 (Ports & Adapters — network-0 pure core)

- **pure core (offline-testable, network-0)**: `scripts/lib/ac_id.py`(leaf — AC_ID_RE grammar + §5.2 스키마 파서) + `scripts/lib/check_ac_traceability_matrix.py`(매핑 로직 — Hop1 AC well-formed / Hop2 AC↔§8 coverage / Hop3 §8↔symbol born-missing).
- **adapter I/O layer (경계 confined)**: `scripts/check-ac-traceability-matrix.sh`(thin wrapper — ADR-061 §결정1 convention, `check-venue-shape-fidelity-presence.sh` 동형) + `.github/workflows/ac-traceability-matrix.yml`(fetch/cross-repo I/O 전담).
- 3 seam(parse / Phase1-map / Phase2-born-missing)이 phase-aware 2-tier 의 구조적 불변식. cross-repo fetch·fs I/O 는 workflow layer 에만.

### 결정 8 — per-PR applicability 가드 + "opt-out ≠ applicability-scoping" 정의역 명확화 + 6→7 required 등록 reconcile 완결 (Amendment 1, CFP-2609)

**배경**: §결정3 이 (A) 즉시 required 등록(6→7-tuple)을 선언했으나, 등록의 born-broken 안전 전제("self-test green ∧ own-PR green")가 CFP-2603 시점에 미충족 — 게이트가 story_uri 부재/transient-ref PR · Phase-1 rtm_uri 부재 · §5-AC 없는 governance PR 을 무조건 fail-closed 처리하여 **자기 PR 을 포함한 정상 PR 전부 오차단**(false-red). 즉시 등록 시 repo 파괴 → 등록 HELD(merge 경계 verify-before-trust, ADR-119). live=6-tuple ↔ doc(CLAUDE.md 브랜치 보호 표 + branch-protection-audit)=7-tuple divergence 로 잔존(ADR-151 이 "CFP-2609 reconcile 대기"로 명문 기록). 본 Amendment = 그 reconcile carrier — §결정3 의 미완결 등록을 **적용성(applicability) 가드 선수정 후** 안전 완결한다.

**A2-5 판정 (Amendment vs 신규 ADR — ADR-146 §결정11 / ADR-151 §결정1 verbatim 구조; 양 prong 반증)**:
- **Amendment prong (ADR-145 로 착륙) = 채택**: CFP-2609 은 (i) §결정4 no-optout 의 **정의역 명확화**("opt-out ≠ applicability-scoping") + (ii) §결정3 이 이미 선언한 6→7 등록의 **미완결 실행** 뿐이다. 신규 mechanism 도입 0 — 신규 workflow 0(기존 `ac-traceability-matrix.yml`/core 수정), 신규 required context 0(§결정3 이 이미 선언한 6→7), 신규 스키마 0(§5.2 AC schema·`AC_ID_RE` 재사용), 신규 게이트/카테고리 0. per-PR applicability 는 기존 게이트의 self-scoping 정련이지 standalone governance mechanism 아님 → 별 context/결정/결과 블록이 ADR-145 중복.
- **신규 ADR prong (왜 신규 아닌가) = 기각**: Epic CFP-2602 "게이트 G당 1 신규 ADR" 패턴은 *신규 게이트 G*(G1=145 / G2=148 / G3=152 / G4=146 / G5=150 / G6=151)에 적용된다. CFP-2609 은 신규 게이트를 추가하지 않고 **G1(ADR-145) 자신의 applicability 정련 + 등록 완결** carrier 이므로 새 G 슬롯이 아니다. per-PR applicability("세 번째 적용성 축")는 개념적으로 신규이나 ac-traceability 게이트 작동 *내부*에 confined — ADR-133 atomic-claim 신규 번호 소요 0.
- **판정 = Amendment 1 (ADR-145 무supersede)** — diff-proven: 본 Amendment 는 §결정4·§결정3 을 rewrite/삭제하지 않고(append-only) 문언의 해석-정의역만 정련 + 등록 완결. 어느 것도 신규 결정/mechanism 아님.

**(A) "opt-out ≠ applicability-scoping" — §결정4 no-optout 정의역 명확화**:
- §결정4 "skip-PASS / opt-out / default-green 경로 부재 + skip-toggle 신설 금지"의 정의역 = **적용 대상 PR 의 escape**(§5 에 AC 를 선언한 PR 이 검사를 회피). 무손상 유지.
- **applicability-scoping** = 그 이전 단계에서 "이 PR 이 애초 검사 대상이냐"를 objective 하게 가르는 직교(orthogonal) 선행 판정. 검사 대상 부재(추적할 AC 자체가 없음) PR 은 **불변식 I-AC 의 정의역 밖** — skip-PASS/opt-out 이 아니라 자연 N/A(ADR-127 §결정5 3축 AND 동형).
- ∴ "비적용 PR → in-job exit 0" 은 §결정4 위반이 아니다. **exception-through-interpretation 봉인**: 두 판정은 순차 직교이며 서로 약화하지 않는다.

**(B) per-PR applicability 축 = 신호 C (기존 2 축과 disjoint)**:
- 본 프로젝트 applicability 3 축: (a) consumer-배포 applicability(ADR-130 positive-whitelist) · (b) repo-level applicability(§결정3 F1 repo-guard `if: github.repository ==`) · **(c) per-PR applicability = 본 Amendment 신설**.
- **신호 C = resolved authoritative §5 에 ≥1 normative AC presence**. positive detection(선언 표면 *있음* 탐지 — self-declared opt-out 플래그·label 토글·diff-touch 금지, 신호 A/D/E/F 기각) + presence-based(semantic 판단 금지, §결정1 천장 상속).
- **비적용 positive 확정 = resolve-success ∧ 0 normative AC**(authoritative 소스 clean-parse 후 normative AC 0). 두 clean 경로: (i) §5 AC 선언 표면 구조적 부재(§5 없음 또는 §5 에 AC 표 없음) (ii) §5 AC 표 present + records well-formed + 0 normative(전부 declared/advisory).

**(C) I-APPLIC 불변식 codify (신규 — §2.4 Story)** — applicability 신호 = objective ∧ non-suppressible ∧ 판정불가≠비적용 ∧ forward-only/grandfather:
- **판정불가 ≠ 비적용 (최중요, anti-degradation)**: cross-repo fetch 실패 / 403 / 404 / frontmatter-parse 실패 / local-unreadable / §5 malformed-table = **판정불가 → FAIL**(§결정4 helper fail-closed 재사용). 어떤 degraded 경로도 "비적용 skip"으로 흡수 금지(born-hollow 봉인). **anti-degradation guard**: §5 에 AC-ID 형 토큰(`AC-\d+`)이 present 인데 parseable AC 표 부재 = 산문 AC 선언 + 표 파손 = degradation → FAIL(skip 금지). 비적용 skip 은 (AC 표 부재 ∧ AC-ID 토큰 부재)의 positive 부재에서만 도달.
- **non-suppressible**: 적용 PR 이 억제가능 신호(story_uri 마커 삭제·label)로 비적용 위장 불가 — story_uri 마커 삭제 = 판정불가 FAIL(adapter `if(!storyUri) fail`). resolved §5 를 비게 하려면 authoritative Story §5 물리삭제 필요(고가시 + RO-1 §1↔§5 완결성 포착 + tier 배정 RO-1 gate).
- **empty-AC bypass 무손상**: §5 AC 표 present + 0 rows = F-AC7-a bypass(선언 표면 구축 후 비움) → FAIL 절대 재개방 금지. "AC 표 부재(비적용)" vs "AC 표 present + 0 rows(bypass)" 구조적 구분.
- **forward-only + grandfather**: 등록은 향후 PR 강제 — G3~G6 기머지 PR 소급 재검증 아님(Story date/KEY 기준).

**(D) 단일 판별 모델 = phase × resolve-outcome 매트릭스** (§1.1 §5-absence + §1.2 Phase-1 rtm_uri + §1.3 story_uri verify 를 개별 패치 금지 — 단일 모델로 통합). 적용성 verdict = **core 단일 소유**(adapter 재파싱 = drift 금지):

| resolve outcome | phase 1 | phase 2 |
|---|---|---|
| 판정불가(fetch/403/404/frontmatter/unreadable/malformed-table) | FAIL | FAIL |
| 비적용(AC 표 부재 ∧ AC-ID 토큰 부재; 또는 records present·0 normative) | PASS(exit 0) | PASS(exit 0) |
| empty-AC(표 present, 0 rows) | FAIL(F-AC7-a) | FAIL(F-AC7-a) |
| 적용, rtm_uri 부재(RTM not-yet) | Hop1 only(Hop2 skip) | FAIL(RTM 필수) |
| 적용, rtm=placeholder/absent | FAIL(F-AC7-b/b2) | FAIL |
| 적용, rtm resolved | Hop1+Hop2 | Hop1+Hop2+Hop3 |

- **rtm_uri Phase-1 not-yet (§1.2)**: Phase-1 PR(§1-7)은 §8 RTM 이 아직 산출물 아님 — rtm_uri 마커 부재 = not-yet-applicable → Hop1 only(placeholder fallback false-fail 제거). placeholder(§8 "작성 예정")로의 *fallback* 은 금지(F-AC7-b2 = FAIL). not-yet 은 adapter 의 EXPLICIT 신호(rtm_uri 마커 부재 ∧ phase 1)이지 placeholder 흡수 아님.

**(E) in-job 판정 (F-1/F-2/F-3 GitHub 플랫폼 제약)**: required + workflow-skip = 영구 Pending → merge 차단(GitHub Docs verified). ∴ 적용성 가드 = **항상 실행 in-job 판정 + exit code**. job-level `if:` skip(runner 배정 前 server 평가 = disk 부재, hashFiles/steps context 부적격) / `on.pull_request.paths` 필터(required-pending 함정) **금지**. trigger 는 `pull_request`(paths 필터 없음) 유지, 분기는 in-job. 비적용 PR 도 checkout + in-job exit 0(job-skip 아님).

**(F) story_uri 영구 ref (§1.3 — 404 3-class)**: story_uri = **영구 ref(internal-docs main / immutable commit SHA)**, transient feature 브랜치 ref 금지(Class A 404 회피). 404 는 단일원인 처리 금지 — auth-masking(403→404 masking, F-5 GitHub Docs) vs genuine ref-missing 구분, **둘 다 판정불가 FAIL**(skip 흡수 금지). false-fail 은 영구-ref *convention* 으로 예방(404 흡수 아님). frontmatter-parse 실패(Class B)=post-fetch 판정불가 FAIL(root-cause = 영구 ref 실 frontmatter resolve).

**(G) 6→7 required 등록 reconcile 완결 (§결정3 HELD 해제)**:
- **ground-truth**: doc SSOT(CLAUDE.md 브랜치 보호 표 + branch-protection-audit)=7-tuple(`ac-traceability-matrix` 포함, doc-ahead) ↔ live(gh api)=6-tuple. reconcile = **live 를 doc 로 승격**(6→7 live 등록) — doc 표 무변경.
- **ordering invariant (§결정3 상속)**: workflow 착륙 → self-test suite green(`ac-traceability-self-test.yml`) → CFP-2609 own-PR green(적용성 가드 실 red/green 산출) → THEN 등록. own-PR green 미달 시 등록 보류 후 통보.
- **등록 실행 = Orchestrator post-merge gh api**: POST `/branches/main/protection/required_status_checks/contexts` append(권장, F-4 저위험) 또는 GET→full-PUT 6-보존 replace. 사후 GET `/protection` 로 정확히 7개(기존 6 전부 잔존 + `ac-traceability-matrix`) 실측(AC-9). 등록 *act* = human/Orchestrator gate(forged machine test 금지, AC-8) / doc↔live parity = 기계검증 outcome(AC-9 `test_seven_tuple_preserves_six`).

**(H) 정직 천장 (disclosed ceiling 상속)**: 적용성 신호 = presence-based. 게이트가 "이 PR 이 마땅히 AC 를 가졌어야 하는가"(semantic)를 판정하지 않는다 — non-gameability 는 신호 C + RO-1(§1↔§5 완결성·tier 배정) + AC-10 advisory + Codex divergence defense-in-depth 로 저감(gate-internal semantic 강제 = 검사연극 §결정1 금지). AC-0 under-minting gaming = §결정1(b) Hop0 기인정 disclosed ceiling — CFP-2609 신규 확대 아님. "완전 봉인" hard-claim 금지.

**불변 무손상**: fail-closed 핵심(적용-미추적 = FAIL, §결정4 AC-7) + F1 wrapper-self repo-guard(consumer 오탐 0) + F-AC7-a 빈-AC FAIL + presence/mapping 천장(§결정1) + `AC_ID_RE` sub-letter(§결정4) 전부 무손상. 본 Amendment = scope 정정(false-red 제거)이지 검출력 약화 아님(evidence-gated ratchet ↑ 방향, ADR-064/058/102).

## 대안 (기각 근거)

- **계약 count 제거 → AC-list (MAJOR v2.0)**: 새 ADR + 양-plugin bump + migration 필요 = double-ADR + 파괴적. → 기각, additive MINOR(count 보존, §결정 6) 채택.
- **phase-gate-mergeable.yml in-line 흡수**: warning-tier 또는 fast-pass bypass 로 fail-closed 불가(§결정 3 실측). → 기각, 신규 required job.
- **born-missing = file∧function grep**: CFP-2545 false-oracle(§결정 5). → 기각, ast symbol resolve.
- **skip-toggle 신설**: ADR-127/AC-7 opt-out. → 기각(§결정 4).
- **branch-protection 등록 = (B) shadow-required 하이브리드**(workflow day-1 hard-fail 로 실 red/green + PR red X, `required_contexts` 등록은 지속 green + born-broken-clear 확인 후 ADR-060 §결정6/19 evidence-gate 로 승격): **고려됐으나 미채택** — 사용자가 (A) 즉시 required 를 선택(2026-07-11). 채택 근거 = A 의 born-broken 위험이 게이트 self-test merge-precondition 으로 이미 구조적 차단되어(§결정 3) shadow 유예의 이득이 낮고, 즉시 fail-closed 가 요건-현실 갭 차단(Story 목적)에 직결. B 는 양안 보존 기록으로만 잔존.
- **(Amendment 1) CFP-2609 = 신규 ADR(per-PR applicability 축 신설)**: per-PR applicability 가 "어디에도 정의 없는 세 번째 축"이므로 신규 ADR 도 고려됐으나 **기각** — A2-5 양 prong(§결정 8) 반증: 신규 mechanism(workflow/스키마/게이트/context) 0 + Epic "게이트 G당 1 ADR" 패턴은 신규 게이트에만 적용(CFP-2609=G1 완결 carrier, ADR-152 가 G3 로 152 점유하므로 신규 게이트 slot 아님). → ADR-145 Amendment(§결정4 정의역 명확화 + §결정3 등록 완결) 채택.
- **(Amendment 1) 적용성 = job-level `if:` / `on.paths` skip**: required + workflow-skip = 영구 Pending → merge 차단(F-1 GitHub Docs) + job-level `if:` = disk 부재로 계산 불가(F-2). → 기각, in-job exit-code 판정(§결정 8 E).
- **(Amendment 1) 적용성 신호 = story_uri 마커(A) / Epic·sibling label(E) / diff src touch(D)**: A/E = 억제가능 opt-out 벡터(§결정3 fast-pass bypass 재유입), D = §결정2 diff-추론 금지 위반. → 기각, 신호 C(resolved §5 normative-AC presence, non-suppressible, §결정 8 B).

## 결과

- 사용자 요건이 AC-ID 로 민팅되면 요구사항→설계→§8→구현 사슬에서 침묵 삭제가 구조적으로 불가능(presence/mapping fail-closed). 미민팅(Hop0)은 RO-1 review + advisory 로 defense-in-depth.
- traceability rot·수동오류 저감 + semantic 잔여 2건 정직 공개 = ADR-119/ADR-006 Amd2 정합(검사연극 회피).
- Epic CFP-2602 게이트 disjoint: G1(AC↔명명 §8 테스트 ∧ diff 실재) ⊥ G2(runtime liveness) ⊥ G3(discriminating 행사). 공유 = 원리(선언→실행, Epic #2346 계보)뿐.

### Amendment 1 결과 (CFP-2609)

- **적용성 3 축 확립**: (a) consumer-배포(ADR-130) ⊥ (b) repo-level(F1 repo-guard) ⊥ (c) per-PR(신호 C) — 게이트가 정의역 밖 PR(추적할 AC 부재)을 false-red 로 오차단하지 않으면서 fail-closed 핵심(적용-미추적=FAIL)을 무손상 보존. false-red 제거(scope 정정)이지 검출력 약화 아님.
- **doc-vs-live divergence 해소**: §결정3 이 선언한 6→7 등록의 미완결분이 CFP-2609 로 완결(ordering invariant 준수 post-merge Orchestrator gh api). ADR-151 이 기록한 "CFP-2609 reconcile 대기" 항목 해소 — reconcile 후 live=doc=7-tuple.
- **born-hollow 봉인 강화**: I-APPLIC anti-degradation(판정불가·degraded 경로의 skip 흡수 금지) + self-test 3경로 discriminating mutant(비적용→PASS / 적용-미추적→FAIL / empty-AC→FAIL)로 게이트가 빈 껍데기화하지 않음을 merge-precondition 으로 강제(CFP-2530/2535 계보).

## 관련 파일

- Story: `<internal-docs>/wrapper/stories/CFP-2603.md` (§7 설계 서사) · **(Amd1)** `<internal-docs>/wrapper/stories/CFP-2609.md` (§7 적용성 가드 설계 서사)
- Change Plan: `<internal-docs>/wrapper/change-plans/cfp-2603-g1-ac-traceability-matrix.md` · **(Amd1)** `<internal-docs>/wrapper/change-plans/cfp-2609-g1-applicability-guard-required-registration.md`
- 신규(Phase 2): `scripts/lib/ac_id.py` · `scripts/lib/check_ac_traceability_matrix.py` · `scripts/check-ac-traceability-matrix.sh` · `.github/workflows/ac-traceability-matrix.yml`
- **(Amd1) 수정(Phase 2)**: `scripts/lib/check_ac_traceability_matrix.py`(적용성 verdict core 단일 소유 — `run()` phase×resolve-outcome 매트릭스) · `.github/workflows/ac-traceability-matrix.yml`(story_uri 영구 ref + rtm_uri not-yet + 404 3-class) · `tests/scripts/test_check-ac-traceability-matrix.sh`(적용성 3경로 discriminating mutant) · `templates/github-workflows/ac-traceability-matrix.yml`(L2 byte-identical)
- **(Amd1) 코드-외 조치(Phase 2 post-merge)**: branch-protection `required_status_checks` 6→7-tuple 등록(Orchestrator gh api, ordering invariant 준수 + 사후 GET 7-tuple 실측)
- 계약(Phase 2): `docs/inter-plugin-contracts/requirements-output-v1.md`(v1.2) · `design-output-v2.md`(v2.5) · `MANIFEST.yaml`
- review binding(Phase 2): `plugins/codeforge-review/templates/review-checklists/requirements.md` · `plugins/codeforge-review/agents/RequirementsReviewPLAgent.md` · `codeforge:review-responsibility` matrix
- 선례: `scripts/lib/check_venue_shape_fidelity_presence.py`(near-exact 구조 선례, warning-tier → 본 게이트는 fail-closed 상향)
