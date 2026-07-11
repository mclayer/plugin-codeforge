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
  - ADR-060  # warning-tier evidence framework + 승격 evidence-gate — shadow-required → required_contexts 승격 evidence-gate 선례(§결정 6/19). ModuleArch digest 의 "ADR-130 §결정6 7-day-green" 오citation 정정 (ADR-130 = applicability⊥closure, 무관)
  - ADR-005  # N/A 명시 패턴 — §11 데이터 마이그레이션 N/A (wrapper-self governance, schema/data 무변경) 근거
  - ADR-068  # boundary invariant I-1~I-5 — deputy mandate boundary (chief tie-break ladder 2단계) + I-3 guard placement(unconditional 우선) + I-4 wording SSOT
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs). ADR-127 :115 정합
related_concepts:
  - ac-traceability-zero-drop
  - presence-mapping-ceiling-honesty
is_transitional: false
---

# ADR-145 — 요건 traceability zero-drop 게이트 (AC-ID + phase-aware 2-tier presence/mapping fail-closed)

## 상태

Accepted (2026-07-11 KST) — CFP-2603 (Epic CFP-2602 G1) carrier. 사용자 요건이 요구사항→설계→§8 테스트→구현 사슬을 지나며 조용히 증발하는 병(Gap A, 요건-현실 갭)을 도메인 불변식 위반으로 재정의하고 기계 게이트로 강제하는 governance SSOT. 강화(ratchet↑) 방향 — 기존 게이트 무변경 위에 신규 fail-closed 게이트 1개 + 계약 2 additive MINOR + review obligation 1축 추가. 약화 surface 0.

## 컨텍스트

사용자 원문(Story §1 verbatim): mctrader 개발 중 "5분/1시간 compactor" 요건을 세 번 주장했으나 반영되지 못함. 3-angle forensic 실측 결과 = 요건이 lane 경계를 넘으며 증발(Gap A). 실측된 증발 지점:

- **유일 계약 `requirements-output-v1` 이 AC 전체를 `sub_agent_results.analyst.acceptance_criteria_count: <int>` 정수 하나로 붕괴** [verified: `docs/inter-plugin-contracts/requirements-output-v1.md` L90, origin/main]. 항목 identity 소멸 → 하류 lane 이 "사용자가 요구한 것의 체크리스트"를 하나도 쥐지 못함.
- `scripts/lib/check_story_section_schema.py` = §N 헤딩 존재만 검사(§1~§11 strict), AC↔테스트 매핑 로직 부재, fail-closed `sys.exit(1 if errors>0)` [verified: L133-140].
- `.github/workflows/phase-gate-mergeable.yml` = 단일 job `check-gate` [verified L21]. **anchor 계층(CFP-900 §4.13 L369 / S6 provenance L581 / S7 L648)이 전부 `checks.create` 이후 try/catch-silent warning-tier** [verified] + **fast-pass OR-gate(`isEpicLabel||isSiblingPr||isPostMergeFix||isLabelMismatchOnly`) L359 → early-return success L414-423** — Epic/sibling PR 은 in-line matrix 를 우회.
- 각 lane 이 사용자 요건을 산문으로 재해석해 자기 범위를 스스로 재도출 → 항목 침묵 삭제가 전 게이트 green.

도메인 불변식 **I-AC**: "AC 는 사용자 의도의 안정적 참조자이며 lane 경계를 넘어 보존돼야 한다." 현재 계약은 identity(AC-N)를 정수 count 로 붕괴시켜 이를 깬다.

외부 근거(Story §6 재인용 — 신규 외부 단정 없음): RTM + bidirectional traceability 는 확립된 관행이다 (ISO/IEC/IEEE 29148 traceability mechanism / DO-178C §5.4·§6.4 상위요건↔하위요건↔검증자산 양방향 필수 / NASA SWE-052·SWE-059 bidirectional). 동시에 RTM 은 드롭을 **줄이지만 없애지 못한다** — traceability rot / 유지비용 / rubber-stamping (Jama Software). ∴ 자동화로 rot·수동오류는 저감하나 semantic 완전성 봉인은 불가(§결정 5 근거).

## 결정

AC 에 lane 경계를 넘어 안정적인 식별자(AC-ID)를 부여하고, `AC-N ↔ §8 명명 테스트 ↔ 실 테스트파일` zero-drop 을 신규 fail-closed 기계 게이트로 강제하되, 기계가 강제 가능한 것(presence/mapping)의 천장을 정직히 공개한다. 착지 = 신규 lint 모듈 + 신규 required workflow + 계약 2 additive MINOR + 요구사항리뷰 lane 3번째 disjoint 축.

### 결정 1 — presence/mapping 천장 + no-hollow 정직 (ADR-006 Amd2 L266 isomorphic)

- **기계 게이트는 presence/mapping 까지만 fail-closed 로 강제한다**: (i) AC-N well-formed + §5.2 스키마 필드 존재, (ii) 모든 AC-N → ≥1 §8 명명 테스트 매핑, (iii) 명명 테스트의 실 파일 ∧ 실 symbol 존재(born-missing 차단).
- **"테스트가 요건을 의미상 올바르게·완전히 검증하는가"(semantic correctness/completeness)를 강제하는 척 = 검사연극** — ADR-006 Amd2 L266("presence-anchor completeness 를 real 인 양 강제 = 검사연극")의 **isomorphic 선례**를 직접 적용한다 (ADR-119 §결정 4 정합).
- **두 잔여 정직 공개 (no-hollow honesty)**: (a) test-semantic 완전성 미강제, (b) **user→AC 분해-완결성**(AC 집합이 사용자 의도에 완전한지) 미강제. 둘 다 fail-closed 아니며 §결정 2 review obligation + advisory 로 mitigate. **"완전 봉인" hard-claim 금지** — "구조적 born-missing fail-closed + semantic 저감 + 잔여 정직 공개"로 재약속.

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
- **CONFLICT-C divergence 정당화**: ADR-125 §결정2 "branch-protection 6-tuple 불변" 선례는 phase-gate **INTERNAL 흡수**(요구사항리뷰 gate 를 기존 check-gate 로 매핑)를 전제했다. 본 게이트는 그 흡수 경로가 **fail-closed 비호환**(anchor=warning-tier + fast-pass bypass 실측)이므로 선례가 성립하지 않는다 → 신규 required job 이 정당하다. ADR-125 선례 override 는 **비호환 근거에 한정**되며 6-tuple 불변 원칙 자체를 폐기하지 않는다.
- **branch-protection required_contexts 등록(6→7-tuple) = 사용자 결정** (비가역·거버넌스 tuple 변경): 두 옵션 — (A) 즉시 등록(day-1 merge blocker) vs (B) **shadow-required 하이브리드**(workflow 는 day-1 hard-fail 로 실 red/green, required_contexts 등록은 지속 green + born-broken-clear 확인 후 승격 — ADR-060 §결정 6/19 승격 evidence-gate 선례). 설계 권고 = **(B) shadow-required**. 설계리뷰 lane 으로 escalate. (참고: ModuleArch digest 의 "ADR-130 §결정6 7-day-green" 은 오citation — ADR-130 = applicability⊥closure 분류. 승격 근거 SSOT = ADR-060.)

### 결정 4 — fail-closed no-optout + AC-ID namespace + sub-letter grammar

- **fail-closed no-optout (AC-7)**: skip-PASS / opt-out / default-green 경로 부재. 판정 불가(cross-repo fetch 실패 / token 부재 / 403·404)는 **helper fail-closed 패턴**(phase-gate-mergeable.yml `if(!token) return false` L232 형)을 재사용 — main-path degrade(L69-70 PR-label fallback)는 재사용 금지. **403/404 conflation 가드**: born-missing verdict 는 `resp.ok` 확인 후에만 — "읽을 수 없음"을 "존재하지 않음→verdict 없음"으로 해석 금지.
- **4 bypass vector 차단(F-AC7-a..d)**: 빈 AC 목록 / 미선언 §8 / stub 명명 회피 / phase 오선언.
- **transition = forward-only + grandfather** (Story date/KEY 기준). **skip-toggle 신설 금지** — toggle 은 ADR-127/AC-7 opt-out 이 된다.
- **AC-ID namespace = Story-local** (`AC-N`); cross-Story 참조 = `<KEY>:AC-N`.
- **AC_ID_RE SSOT = sub-letter 수용** (`^AC-(\d+)([a-z])?$`): 본 Story 자체의 `AC-1a`/`AC-1b` sub-letter ID 가 naive `AC-\d+` regex 에 조용히 drop 되면 zero-drop 위반(CRITICAL TRAP — RefactorAgent). AC_ID_RE 는 단일 SSOT leaf(`scripts/lib/ac_id.py`)로 추출하여 lint·계약·후속 재사용이 공유한다.

### 결정 5 — born-missing = 실 symbol/node resolve (grep 금지) + linter self-test (CONFLICT-B)

- **born-missing 검출 = 실 파일 ∧ 실 symbol resolve** (Python `ast` 파싱으로 명명 테스트 함수/클래스 node 존재 확인) — **grep 금지**(F-ORACLE-GUARD). presence-grep(파일∧함수 문자열 매칭)은 CFP-2545 false-oracle 계열 결함(주석·docstring·문자열 안 매칭 = 거짓 PASS).
- **linter 자체 mutation-self-test 의무** (ADR-136 Amd3 L3 / CFP-2535 execution-liveness): "file∧function grep 만으로 born-missing 판정" 자체가 false-oracle 이므로, born-missing linter 는 자기 자신을 mutation A/B/C 로 반증 통과해야 한다. §8 Test Contract 에 linter self-test 포함.

### 결정 6 — 계약 2 additive MINOR (CONFLICT-A 회피)

- **`requirements-output-v1` v1.1 → v1.2 (additive MINOR)**: 기존 `sub_agent_results.analyst.acceptance_criteria_count: <int>` **보존**(제거 = MAJOR = CONFLICT-A). 신규 top-level `acceptance_criteria[]`(optional, `sub_agent_results`/`writes_completed` 와 peer) 추가 — 각 item = §5.2 스키마{id/statement/source/verification/coverage_required/phase/tier}. **게이트가 list 실재를 강제**(AC-3 항목화 전달)하되 **계약 field 는 영구 optional 유지**(ADR-008 §결정2 backward-compat MINOR).
- **`design-output-v2` v2.4 → v2.5 (additive MINOR, Model A)**: `chief_author_artifact.ac_coverage_self_check_passed: bool` marker 추가 (기존 self-check disjoint 축 group `architecture_doc_updated` 등과 peer, default false). **Story §8 doc = authoritative RTM** — packet 에 RTM 중복 금지(marker 만).
- **MANIFEST 3-point parity** (Phase 2 mechanical sync): 각 계약의 (i) frontmatter contract_version, (ii) 본문 version, (iii) `docs/inter-plugin-contracts/MANIFEST.yaml` entry 를 동시 이동(v1.2 / v2.5). atomic.

### 결정 7 — 모듈 경계 (Ports & Adapters — network-0 pure core)

- **pure core (offline-testable, network-0)**: `scripts/lib/ac_id.py`(leaf — AC_ID_RE grammar + §5.2 스키마 파서) + `scripts/lib/check_ac_traceability_matrix.py`(매핑 로직 — Hop1 AC well-formed / Hop2 AC↔§8 coverage / Hop3 §8↔symbol born-missing).
- **adapter I/O layer (경계 confined)**: `scripts/check-ac-traceability-matrix.sh`(thin wrapper — ADR-061 §결정1 convention, `check-venue-shape-fidelity-presence.sh` 동형) + `.github/workflows/ac-traceability-matrix.yml`(fetch/cross-repo I/O 전담).
- 3 seam(parse / Phase1-map / Phase2-born-missing)이 phase-aware 2-tier 의 구조적 불변식. cross-repo fetch·fs I/O 는 workflow layer 에만.

## 대안 (기각 근거)

- **계약 count 제거 → AC-list (MAJOR v2.0)**: 새 ADR + 양-plugin bump + migration 필요 = double-ADR + 파괴적. → 기각, additive MINOR(count 보존, §결정 6) 채택.
- **phase-gate-mergeable.yml in-line 흡수**: warning-tier 또는 fast-pass bypass 로 fail-closed 불가(§결정 3 실측). → 기각, 신규 required job.
- **born-missing = file∧function grep**: CFP-2545 false-oracle(§결정 5). → 기각, ast symbol resolve.
- **skip-toggle 신설**: ADR-127/AC-7 opt-out. → 기각(§결정 4).

## 결과

- 사용자 요건이 AC-ID 로 민팅되면 요구사항→설계→§8→구현 사슬에서 침묵 삭제가 구조적으로 불가능(presence/mapping fail-closed). 미민팅(Hop0)은 RO-1 review + advisory 로 defense-in-depth.
- traceability rot·수동오류 저감 + semantic 잔여 2건 정직 공개 = ADR-119/ADR-006 Amd2 정합(검사연극 회피).
- Epic CFP-2602 게이트 disjoint: G1(AC↔명명 §8 테스트 ∧ diff 실재) ⊥ G2(runtime liveness) ⊥ G3(discriminating 행사). 공유 = 원리(선언→실행, Epic #2346 계보)뿐.

## 관련 파일

- Story: `<internal-docs>/wrapper/stories/CFP-2603.md` (§7 설계 서사)
- Change Plan: `<internal-docs>/wrapper/change-plans/cfp-2603-g1-ac-traceability-matrix.md`
- 신규(Phase 2): `scripts/lib/ac_id.py` · `scripts/lib/check_ac_traceability_matrix.py` · `scripts/check-ac-traceability-matrix.sh` · `.github/workflows/ac-traceability-matrix.yml`
- 계약(Phase 2): `docs/inter-plugin-contracts/requirements-output-v1.md`(v1.2) · `design-output-v2.md`(v2.5) · `MANIFEST.yaml`
- review binding(Phase 2): `plugins/codeforge-review/templates/review-checklists/requirements.md` · `plugins/codeforge-review/agents/RequirementsReviewPLAgent.md` · `codeforge:review-responsibility` matrix
- 선례: `scripts/lib/check_venue_shape_fidelity_presence.py`(near-exact 구조 선례, warning-tier → 본 게이트는 fail-closed 상향)
