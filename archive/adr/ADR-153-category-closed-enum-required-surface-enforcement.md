---
adr_number: 153
title: ADR category closed_enum semantic 강제 실배선 — 기존 required doc-frontmatter surface 위 fail-closed membership 강제(편승, 7-tuple 무변경) + (file,case-folded-value) grandfather shrink-only + CFP-2615 warning-tier declared plan 의 membership-scoped supersede
status: Accepted
category: governance
date: 2026-07-14
carrier_story: CFP-2680
supersedes: []
related_adrs:
  - ADR-102  # 강 의존 — ratchet 약화 evidence-gate governance anchor(formal-ADR-없는 spec-level predecessor reversal 의 sunset_justification mechanism). 본 ADR 이 CFP-2615 규칙 8 "warning-tier standalone" declared plan 을 required-surface fail-closed 로 뒤집는 traceable-reversal. 강화 방향(warning→required)이라 sunset_justification 불요(약화 아님)
  - ADR-058  # 강 의존 — ADR sunset criteria mandate. §결정 3 측정성 3-tuple(metric/who/how) = 실패 메시지가 안내하는 정식 확장 절차의 sunset_justification 구성. §결정 5 Amendment justification(약화 evidence-gate) = 본 게이트를 나중에 warning 으로 낮추거나 우회 label 을 여는 것만 evidence 대상, fail-closed 추가는 강화(evidence 불요)
  - ADR-060  # 강 의존 — evidence-enforceable promotion framework. §결정 5(첫 적용 = warning mode)/§결정 6(승격 gate) warning-first 사다리 = 본 ADR 에서 **N/A**(§결정 4): 본 강제는 net-new gate 가 아니라 이미 required 인 fail-closed 게이트(`doc frontmatter schema (CFP-28 — strict)`)의 semantic 확장. 사다리의 soak/false-assurance 우려는 AC-7 corpus-GREEN dry-run + shrink-only grandfather 로 해소
  - ADR-091  # 강 의존 — ArchitectLane DDD vocabulary governance §결정 4 Published Language content duplication 금지 = 단일 owner location. lint 은 enum 을 하드코딩하지 않고 `docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum` 을 동적 read-only 참조("16"/"18" count 상수 금지)
  - ADR-145  # 강 의존 — 요건 traceability zero-drop 게이트(ac-traceability-matrix, 7-tuple required). 본 Story 8 normative AC → RTM authoritative 위치 = Change Plan §8(wrapper-self dogfood). AC↔§8↔실 test 무손실 매핑 의무. §결정5 grep-oracle 금지 = self-test 는 실 subprocess exit+substring
  - ADR-150  # 형제 선례 — 런타임 DAST 축(§8.9) 신설. "fail-closed lint mechanism = 자기 ADR + 기존 required strict context 편승(신규 required context 0)" 구조 twin. 본 ADR 은 `doc frontmatter schema (CFP-28 — strict)` 에 편승(150 은 `doc section schema` 편승)
  - ADR-151  # 형제 선례 + 정합 — self-test execution-liveness 인벤토리/메타-게이트. 본 self-test 는 `.py`(pytest) → ADR-151 메타-게이트가 `tests/scripts/*.sh` 를 glob 하므로 인벤토리 미등재 = born-red 0(N/A). liveness = 전용 non-required pytest workflow(day-1 hard-fail), 기존 test_ac_*.py suite 동형
  - ADR-152  # 형제 선례 — dark-path activation forcing function(G3). 최근접 구조 twin(fail-closed doc-lint + 기존 strict context 편승 + presence/구조 천장 정직 공개 + 신규 required context 0). §결정 구조·정직 천장 관례 답습
  - ADR-131  # grandfather 대상 — cross-repo responsibility placement governance. `category: orchestration/governance`(compound, 18-enum 비원소) = FROZEN_BASELINE_3 원소 1
  - ADR-132  # grandfather 대상 — consumer branch-protection auto-wire. `category: governance/security`(compound) = FROZEN_BASELINE_3 원소 2
  - ADR-133  # grandfather 대상 + 번호 claim — adr-reservation atomic claim. `category: orchestration/governance`(compound) = FROZEN_BASELINE_3 원소 3. 번호 153 claim = ADR-133 dual-key 3-leg(filename ∧ frontmatter ∧ RESERVATION row) — GH_TOKEN 부재로 OCC primitive 대신 fresh git ls-tree 실측(origin/main max=152, 149 orphan gap) 기반 RESERVATION row(§결정 4 fallback)
  - ADR-127  # 정합 — 모든 변경 = 정식 full 10-lane + Phase 1/2 PR 분리(doc-only fast-path 폐지, §결정 1/2). 본 mechanical lint Story = doc-only 단축 없이 full-lane. (ADR-054 doc-only fast-path 는 ADR-127 로 superseded)
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan 병존(internal-docs `wrapper/change-plans/cfp-2680-category-closed-enum-enforcement.md`)
  - ADR-119  # research-before-claims / 게이트=ground-truth — 게이트는 membership presence(값이 목록에 있나)까지만 fail-closed. "이 category 가 조직적으로 옳은가"(의미 매핑 정확성)는 강제 안 함(안내만) — 강제하는 척 = 검사연극
  - ADR-068  # 약 의존(배경) — boundary completeness invariants. I-3 unconditional guard placement(membership 위반 = 무조건 fail-closed) + I-4 wording SSOT(case_normalization: lowercase_canonical 정합)
related_concepts:
  - closed-set-enum-ci-enforcement
  - controlled-vocabulary-governed-extension
  - enum-ssot-drift-proofing
is_transitional: false
---

# ADR-153 — ADR category closed_enum semantic 강제 실배선 (governance frontmatter lint)

## 상태

Accepted (2026-07-14 KST) — CFP-2680 (lineage: CFP-1523 declarative_layer → CFP-2590 정산/CFP-2615 carrier 발급 → 본 Story mechanical wire, Wave 2) carrier. "ADR frontmatter 의 `category:` 값이 governance closed_enum(`docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum` 18-entry, `open_extension: false`, case-fold 대조) 밖일 때 기존 required doc-schema 워크플로 표면에서 fail-closed 로 강제 발화하도록 semantic membership check 를 실배선"하는 governance SSOT. 현행 required doc-schema lint(`check_doc_frontmatter.py`)는 category 필드 **존재(presence)** 만 검사 — 값 membership(semantic) 미검사. 이 semantic check 1건을 **기존 required 표면에 편승** 추가(standalone warning-tier 스크립트 신설 회피 — CFP-2591 §2.4 "warning 강제피로" 답습 차단). 강화(ratchet↑) 방향, 약화 surface 0(신규 required context 0, branch-protection 7-tuple 무변경, inter-plugin 계약 무변경, 신규 category 0). sunset_justification = N/A(permanent governance ratchet, ADR-058 §결정 5 강화 방향).

## 컨텍스트

사용자 원문(Story §1 verbatim): 신규·변경 ADR frontmatter 의 `category:` 값이 governance closed_enum 밖일 때, 기존 required doc-schema 워크플로 표면에서 fail-closed 로 강제 발화 + 별도 ADR Amendment(sunset_justification 3-tuple) 안내 메시지 포함 + case-fold 대조. standalone warning-tier 스크립트 신설 회피(기존 required 표면 편승).

실측된 gap 및 제약(요구사항 lane §2/§4 + 설계 lane firsthand):

- **structural-only → semantic gap**: `check_doc_frontmatter.py` `REQUIRED`(L27-36)이 `docs/adr`+`archive/adr` 에 `category` 필드 **존재**만 검사 [verified: scripts/lib/check_doc_frontmatter.py:29-30]. `KIND_VALID`(L77-100) = frontmatter 필드 **값**을 valid-set 대조하는 동형 선례 [verified: L77-100] → `CATEGORY_VALID` analog 은 기계적 확장. "단순 reuse" 불성립(structural ≠ semantic) → 신규 membership 로직 1건을 required 표면에 추가.
- **enum SSOT = 18-entry closed_enum**: `docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum` = 18 lowercase 엔트리(16 in-use + 2 예약 `dogfood-out`/`agent-tier`) [verified: docs/confluence-ia-tree.yaml:63-80], `open_extension: false`(L56), `case_fold_during_check: true`(L59). "16 vs 18" narrative label 오기는 lint 설계 blocker 아님 — lint 은 무조건 yaml `closed_enum` 리터럴에 동적 바인딩("16"/"18" count 상수 금지). 예약 2값을 false-reject 하면 회귀.
- **full-corpus rglob → born-red 3건**: `check_doc_frontmatter.py` 는 diff-scope 가 아니라 `archive/adr` 전체 rglob(L43,85) [verified: L43,85]. 선재 compound 위반 3건 실측 — ADR-131 `orchestration/governance`, ADR-132 `governance/security`, ADR-133 `orchestration/governance` [verified: archive/adr grep] — slash-compound 는 18-enum 어느 단일 원소도 아니며 case-fold 후에도 미스매치. strict membership 추가 시 CFP-2680 자기 Phase 2 PR 이 즉시 3건 실패(born-red). "신규·변경" 이라 말해도 기계 표면이 full-corpus 이므로 3건을 명시 처리해야 한다(codeforge 반복 경고 "born-red lint 재발" CFP-2661/2672/2673 답습 차단).
- **CFP-2615 declared plan 모순**: 현 SSOT 2곳이 본 요구사항 확정과 모순 — `adr-category-lane-mapping.md` 규칙 8(CFP-2615 = warning-tier standalone `scripts/check-adr-category-lane-coverage.sh`) [verified: adr-category-lane-mapping.md:190-196] + `confluence-ia-tree.yaml deferred_followup_lint`(tier: warning) [verified: confluence-ia-tree.yaml:81-89]. 둘 다 "fail-closed semantic check on existing required surface, standalone 없음"으로 정합 필요. 한 곳만 고치면 SSOT drift(CFP-2661 census-floor).
- **self-referential dogfood 위험**: 본 Story 가 신설하는 semantic check 자신이 그 결함(false-oracle·over-claim·enum 위반)을 범하기 쉬운 lint-building Story. self-application self-test(execution-backed, positive-control) + AC 표 파서 self-check 필수. 본 ADR 자기 `category: governance` 는 18-enum 리터럴 entry 1 [verified: confluence-ia-tree.yaml:63] → 자기 게이트 통과.

도메인 불변식(Story §2.1):

- **INV-1**(controlled vocabulary): `category:` 는 자유 텍스트가 아니라 통제 어휘. `open_extension: false` = authoring 시점 확장 불가, 확장은 별도 ADR Amendment 정식 절차로만.
- **INV-2**(closed-set ratchet): fail-closed 강제 *추가* = 강화 방향(evidence 불요). 이 게이트를 warning 으로 낮추거나 우회 label 을 여는 것 = 약화(evidence-gate 대상). grandfather 예외가 ratchet 약화로 전락하지 않으려면 예외 집합이 shrink-only.
- **INV-3**(SSOT read-only): lint 은 enum 정의를 소유하지 않고 yaml `closed_enum` 을 read-only 참조만(하드코딩 금지 — ADR-091 §결정 4).
- **INV-4**(정직 천장): 게이트는 membership presence("값이 목록에 있나")까지만 fail-closed. "이 category 가 옳은가"(의미 매핑 정확성/coverage)는 강제 불가 = 안내만 + review attestation(강제하는 척 = 검사연극, ADR-119).

## 결정

ADR `category` closed_enum membership 강제를 **기존 required doc-frontmatter surface(`check_doc_frontmatter.py`) 위 fail-closed semantic check 1건**으로 실배선하되, (i) 선재 compound 3건은 `(file, case-folded-value)` tuple-keyed frozen 3-tuple grandfather(shrink-only)로 born-red 회피, (ii) CFP-2615 warning-tier declared plan 은 **membership-scoped**로 supersede(standalone coverage script 미빌드, coverage/mapping-accuracy 축은 OOS 유지), (iii) 게이트가 강제 가능한 것(membership presence)의 천장을 정직 공개(coverage 정확성 미강제)한다. 착지 = `CATEGORY_VALID` 블록(`check_doc_frontmatter.py`) + `.py` pytest self-test + 전용 non-required pytest workflow + 3-surface 정합(모두 Phase 2, 동일 Story). 결정 SSOT = 본 ADR / 파일 단위 배선·필드 spec = Change Plan.

### 결정 1 — 강제 mechanism: 기존 required surface 위 fail-closed semantic membership (편승, 7-tuple 무변경)

- **강제 표면 = `check_doc_frontmatter.py`** 에 `CATEGORY_VALID` 값-검증 블록 추가(`KIND_VALID` L77-100 동형). scope = `docs/adr` + `archive/adr` 2 prefix 한정(category 는 ADR 전용 필드). 위반 시 `warns` append → 기존 `::error::CFP-28 doc-frontmatter (STRICT)` 헤더 아래 편입 → 기존 `sys.exit(1)`.
- **required context 편승**: 이 표면은 이미 branch-protection **7-tuple** required context `doc frontmatter schema (CFP-28 — strict)`(lint.yml `doc-frontmatter` job) 소속 [verified: Story §4.0 L97]. semantic check 가 그 표면에 편승 → **신규 standalone script·workflow 0, 신규 required context 0, 7-tuple 무변경, exit code semantics(0 pass/1 위반) 무변경**. ADR-150/152 = "fail-closed lint = 자기 ADR + 기존 required strict context 편승" 구조 twin(150/152 는 `doc section schema` 편승, 본 ADR 은 `doc frontmatter schema` 편승).
- **enum 동적 read(하드코딩 금지, INV-3)**: closed_enum 을 `docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum` 에서 CWD-relative 경로로 per-run 1회 로드(per-file loop 밖). "16"/"18" count 상수·enum 리터럴 하드코딩 금지(ADR-091 §결정 4 단일 owner location — 3중 사본 drift 차단).
- **case-fold membership**: 입력 category 값 = ASCII lower + strip 후 18-entry enum 문자열 **전체 단위** membership(`case_normalization: lowercase_canonical` 정합). `&`·`/`·공백 split 금지 — split = false-negative loophole(compound 가 통과) + 유효 multi-word 원소(`team & process` 등) 파손.
- **presence↔membership 순서**: `category is None` 시 membership skip(REQUIRED 가 이미 "필수 필드 누락" 보고 — 이중 경고 회피).
- **stray body line 안전**: 기존 yaml frontmatter parse(`text.split("\n---\n",1)[0][4:]` → `yaml.safe_load`) 재사용 — raw `^category:` regex 재구현 금지(ADR-071 L373 body `category:` 이중매치 회귀 차단, ReDoS 표면 유입 0).

### 결정 2 — grandfather: `(file, case-folded-value)` tuple-keyed frozen 3-tuple, shrink-only + 명명 정규화 follow-up carrier

- **FROZEN_BASELINE_3**(동결·명명, `(str, str)` 튜플 3개): `(archive/adr/ADR-131-cross-repo-responsibility-placement-governance.md, orchestration/governance)`, `(archive/adr/ADR-132-consumer-branch-protection-auto-wire.md, governance/security)`, `(archive/adr/ADR-133-adr-reservation-atomic-claim.md, orchestration/governance)`.
- **grandfather 근거**: (1) 규칙 1 이 이미 legacy Capitalized frontmatter "retain, rewrite=별 carrier" 선례 확립 [verified: adr-category-lane-mapping.md:102,224]. (2) 3건 정규화는 "이 ADR 의 올바른 단일 category 는 무엇인가" 결정 요구 = category→lane 매핑 정확성 재검토 = 명시적 OOS(Story §1). (3) ratchet 은 "소급 전량 수정" 아니라 "신규 약화 금지"(INV-2). compound = 규칙 4(multi-lane ADR = 단일 primary category + cross-ref note) 위반 debt 이며, 단일 primary 선택 자체가 OOS 매핑 결정 → follow-up 소관.
- **shrink-only(INV-2 보존, Phase 2 self-test 기계화)**: self-test 의 비교 baseline 은 source `FROZEN_BASELINE_3` 를 import/ast-extract 한 객체가 **아니라**, test 파일 안에 물리적으로 분리된 독립 하드코딩 리터럴 `_EXPECTED_BASELINE_3`(= `(file, case-folded-value)` 3-tuple, source set 과 **별개 객체**)이다. assert = `ast_extract(source.FROZEN_BASELINE_3) ⊆ _EXPECTED_BASELINE_3` — **연산자는 `⊆` 유지(절대 `==` 아님)**. 근거: `==` 는 legit removal(ADR-132 등이 규칙 4 대로 정규화되어 source 에서 빠짐 = shrink 허용 대상)을 FAIL 시켜 shrink-only "removal→holds" 를 위반한다. `⊆` + frozen test-local baseline 이 value-swap(count-보존 신규 원소 ∉ `_EXPECTED_BASELINE_3` → FAIL)은 잡고 removal(subset → PASS)은 허용하는 유일 정답. source ast-extract 를 source 자기자신과 비교(X⊆X, 항상참)하면 tautology — count-보존 value-swap 미검출 = INV-2 약화 벡터 방치이므로 금지(한 operand 를 "하드코딩 test literal ∧ script ast-extract" 로 동시 규정하지 않는다). 부수 조건: 각 value ∉ closed_enum ∧ 각 file 존재 ∧ count ≤ 3. Append(4번째)/value-swap → `⊆` FAILS(=약화 차단); removal → holds(축소 허용). **Phase 2 impl 제약**: `FROZEN_BASELINE_3` 는 순수 module-level `{(str, str), ...}` set 리터럴(`ast.literal_eval`-able, `frozenset(...)` call-wrap 금지, 동적 생성 금지) — self-test 가 ast-extract 가능해야 한다.
- **명명 follow-up carrier(naive `deferred_followup_cfp: CFP-` 금지 — CFP-2590 §7.1 named-carrier regression)**: ADR-131/132/133 을 규칙 4 대로 단일 primary category + cross-ref 로 정규화하는 별도 CFP = allowlist shrink 경로. carrier 는 named form **CFP-2682** 로 발급 완료(Orchestrator 발급 — Story §7 완료보고).

### 결정 3 — CFP-2615 warning-tier declared plan 의 membership-scoped supersede (standalone coverage script 미빌드) + 3-surface 정합

- **membership-scoped supersede(NOT blanket)**: CFP-2615 의 *membership-enforcement* intent 는 CFP-2680(required-surface fail-closed)으로 실현. standalone `scripts/check-adr-category-lane-coverage.sh` 는 **빌드하지 않는다**. 잔여 category→lane *coverage/mapping-accuracy* 축은 OOS(Story §5.6) 유지 — "coverage delivered" over-claim 금지. FU-1523-2(Confluence IA drift) 무접촉.
- **3-surface 정합(one-place-only = SSOT drift, CFP-2661 census-floor — Phase 2, change-plan §5 명시)**: (1) `docs/confluence-ia-tree.yaml lane_mapping_rule.deferred_followup_lint` (2) `adr-category-lane-mapping.md` 규칙 8 CFP-2615 sub-section (3) 동 파일 frontmatter `deferred_followup_cfps` CFP-2615 entry — 셋 모두 "required-surface fail-closed semantic check on existing required surface(standalone 없음), superseded by CFP-2680"로 정합. 한 곳만 = drift.
- **traceable-reversal(ADR-102)**: CFP-2615 규칙 8 = "warning-tier standalone" declared plan → required-surface fail-closed 로 뒤집는 predecessor reversal. 방향 = warning→required = **강화** → sunset_justification 불요(약화 아님, ADR-102/ADR-058 §결정 5).

### 결정 4 — ADR-060 warning-first 사다리 = N/A (net-new gate 아닌 already-required fail-closed gate 의 semantic 확장)

- **N/A 명시**: ADR-060 §결정 5(첫 적용 = warning mode)/§결정 6(승격 gate binary AND) warning-first 사다리는 본 강제에 **적용 안 됨**. 근거: 본 강제는 net-new 게이트가 아니라 **이미 required 인 fail-closed 게이트(`doc frontmatter schema (CFP-28 — strict)`)의 semantic 확장**(structural presence → semantic membership, 동일 exit surface). 사다리의 soak/false-assurance 우려는 (a) AC-7 corpus-GREEN dry-run(현 코퍼스가 merge 시점 GREEN 임을 execution-backed 증명) + (b) shrink-only grandfather(선재 위반 격리, 신규만 live)로 이미 해소.
- ADR-150/152 선례 동형(기존 required strict context 에 fail-closed 편입 시 warning-first 사다리 미경유).

### 결정 5 — fail 방향: membership 위반 = fail-closed / enum-source 부재·unparseable = fail-OPEN + stderr 경고 (disjoint 모드)

- **membership 위반 = fail-closed(exit 1)**: closed_enum 밖 값 → block. 에러 메시지 MUST 포함 substring = 검출된 값 + `ADR Amendment` + `sunset_justification`(정식 확장 절차 안내 — 규칙 5 = 별 sub-CFP + ADR-058 §결정 3 sunset_justification 3-tuple[metric/who/how] + SSOT doc Amendment + yaml row append + schema MINOR bump). warn-append 라인에 sentinel 주석 `# CAT-MEMBERSHIP-FAIL`(mutation-kill 표적).
- **enum-source(confluence-ia-tree.yaml) 부재/unparseable = fail-OPEN + stderr 경고**: CATEGORY_VALID check 만 skip(membership 미검사), 기존 `import yaml` 실패 시 `sys.exit(0)` fail-open 선례(L21-25) 미러. **fail-open on source ≠ membership fail-closed 약화**(disjoint 모드) — enum-source 있고 값이 밖이면 여전히 fail-closed. compensating control = ADR files in scope 인데 enum-source 부재/empty 시 high-visibility stderr 경고.
- **edge escalation(설계 위임 질문 결정)**:
  - (D4-esc-1) **blank/empty category → fail-closed**(§5.4 "막을지 = 설계" 위임 질문의 설계 답): empty-after-strip → invalid(block). corpus 0 blanks → born-red 0. AC-1 invalid partition 에 folds(blank = non-member) — §5 edit 불요.
  - (D4-esc-2) **non-str category → guard, no-crash, fail-closed**(INV-9): `isinstance(cat, str)` guard; non-str(yaml list/int) → invalid(fail-closed), NOT `.casefold()` → AttributeError traceback(전체 required gate 를 fail-BREAK 시킴). change-plan §8 nonstr-no-crash test.
  - (D4-esc-3) **신규 echo 값 sanitize**(LOG-1): AC 가 강제하는 echo 값(author-controlled)의 CR/LF strip → 단일 라인, ≤80 truncate, leading `::` neutralize — GHA annotation-injection 차단. 기존 `kind` echo 는 retrofit 안 함(pre-existing, OOS — observed residual only).

### 결정 6 — closed-set ratchet framing (강화 방향, sunset_justification N/A) + 정직 잔여

- **강화(ratchet↑) 방향**: 신규 required context 0, branch-protection 7-tuple 무변경, inter-plugin 계약 무변경, 신규 category 0. sunset_justification = N/A(permanent governance ratchet, ADR-058 §결정 5 강화 방향, `is_transitional: false`).
- **정직 잔여(record, NOT actioned)**: (PS-2) yaml alias-bomb/billion-laughs = pre-existing(기존 REQUIRED parse L61 이 이미 노출, 본 ADR 도입 아님 — PR review 완화). (ES-1) same-PR enum-source deletion fail-open bypass = acceptable(source 신뢰, merge-permission 경계; compensating control = ADR files in scope 인데 enum-source 부재/empty 시 high-visibility 경고). (RES-3) category→lane coverage/mapping-accuracy 정확성 = 본 게이트 미강제(membership presence 만) — over-claim 금지, review attestation.
- **self-test = `.py` pytest(NOT shell)**: ac-traceability Hop3(ADR-145)이 RTM named test 를 Python `ast`(`*.py` under `tests`)로 resolve. shell 함수명 미resolve → Phase 2 born-red. 8 normative AC → ac-applicability-none 선언 불가 → RTM names = Python `def`/`class` symbol 의무. self-test = 전용 non-required workflow(wrapper-self-only `if: github.repository == 'mclayer/plugin-codeforge'`, day-1 hard-fail) 배선(ADR-151 메타-게이트 `tests/scripts/*.sh` glob → `.py` 미등재 = born-red 0, N/A). 세부 = change-plan §8.

## 대안 (기각 근거)

- **slash/`&`/공백 split 후 토큰별 enum 대조(3건 통과)**: `orchestration/governance` 를 `/` split 해 통과시키면 closed-set invariant 무력화 false-negative loophole(위반이 통과) + 유효 multi-word 원소(`team & process`·`plugin architecture`) 파손 → 기각, 전체 문자열 단위 membership(§결정 1).
- **diff-scope 구현(신규·변경분만 강제)**: 현 script 는 git 인지 0(순수 filesystem full-corpus 스캔) → base ref 탐지 + 로컬 mode 분기 = 아키텍처 이탈, born-red 회피 목적만으로 git-diff 결합 유입 → 기각, grandfather(§결정 2).
- **선재 3건 즉시 first-segment 정규화**: first-segment = primary 판단은 OOS 매핑 결정(Story §1) + scope unitary(ADR-064 §결정 5) 위반 → 기각, grandfather + 명명 follow-up(§결정 2).
- **standalone warning-tier 스크립트 신설(CFP-2615 규칙 8 원안)**: alert-fatigue(경고 35~91% non-actionable — Story §6.2, arXiv 2311.07482) → 별도 warning 표면 구조적 무시, "warning 강제피로"(CFP-2591 §2.4) → 기각, 기존 required 표면 편승(§결정 1).
- **enum hardcode + drift-detection 테스트**: yaml 실재하므로 hardcode fallback 불요 + 3중 사본 drift(ADR-091 §결정 4 위반) → 기각, 동적 read(§결정 1).
- **CFP-2615 blanket "done" supersede**: membership-enforcement 는 CFP-2680 이 실현하나 coverage/mapping-accuracy 축은 미빌드 → blanket 선언 = over-claim → 기각, membership-scoped supersede(§결정 3).
- **enum COUNT assert("16"/"18")**: SSOT 자기불일치(16 label vs 18 리터럴) + 예약 2값 false-reject 회귀 → 기각, list membership 만(§결정 1).
- **신규 required workflow context(tuple 확장)**: presence/semantic doc-lint 는 기존 strict context 로 충분 → 기각, `CATEGORY_VALID` EXTEND(§결정 1).
- **self-test = shell `.sh`**: ac-traceability Hop3 가 `.py` ast 로만 named test resolve → shell 함수명 미resolve = Phase 2 born-red → 기각, `.py` pytest(§결정 6).

## 결과

- ADR frontmatter `category:` 값이 governance closed_enum 밖(compound/미지값/blank/non-str)이면 기존 required 게이트 `doc frontmatter schema (CFP-28 — strict)` 가 구조적으로 차단(exit 1 + 검출된 값 + `ADR Amendment`+`sunset_justification` 안내). 선재 compound 3건은 shrink-only grandfather 로 격리 → 현 코퍼스 GREEN(AC-7). 신규·변경 ADR 의 compound 도입은 live FAIL. enum-source 부재/unparseable 은 fail-open + 경고(membership fail-closed 무약화, disjoint).
- 강화 surface: 신규 required context 0 / branch-protection **7-tuple 무변경**(기존 strict context `doc frontmatter schema (CFP-28 — strict)` 편승) / inter-plugin 계약 무변경 / 신규 category 0 / exit code semantics 무변경. sunset_justification = N/A(ADR-058 §결정 5 강화 방향).
- 정직 천장(INV-4, ADR-119): 게이트는 membership presence 까지만 fail-closed. category→lane coverage/mapping-accuracy 정확성·분류체계 품질·"조직적으로 옳은 category"는 강제 안 함(안내 + review attestation) — "모든 out-of-enum 차단" over-claim 금지(grandfather 3건 exempt = "3건 grandfathered, shrink-only" 정직 기술). ADR-150 §8.9.5 / ADR-152 §8.10.5 잔여 공개 동형.
- CFP-2615 warning-tier declared plan(규칙 8 + yaml deferred_followup_lint) = membership-scoped superseded(3-surface 정합, Phase 2). standalone coverage script 미빌드 — coverage 축 OOS 유지. 명명 정규화 follow-up carrier(CFP-2682) = allowlist shrink 경로(named form).
- **wrapper-self dogfood 정합**: 본 ADR 자기 `category: governance` = 18-enum entry 1 → 자기 게이트 통과(self-application). self-test = execution-backed(`.py` pytest, positive-control) — false-oracle(source grep) / drift-0 tautology(gate 와 동일 yaml 읽어 self-match) 금지, hardcoded known-bad(`bogus-not-in-enum`/`orchestration/governance`) + known-good(`architecture`/reserved `agent-tier`) 음성 대조. self-referential 결함(false-oracle·over-claim·enum 위반) 재범 차단.

## 관련 파일

- Story: `<internal-docs>/wrapper/stories/CFP-2680.md` (§7 설계 서사 / §3 ADR-153 확정)
- Change Plan: `<internal-docs>/wrapper/change-plans/cfp-2680-category-closed-enum-enforcement.md` (§8 = authoritative RTM, AC-1..8 → `test_*`)
- 수정(Phase 2): `scripts/lib/check_doc_frontmatter.py`(`CATEGORY_VALID` 블록 + `FROZEN_BASELINE_3` 순수 set 리터럴 + enum 동적 read + case-fold membership + `# CAT-MEMBERSHIP-FAIL` sentinel + echo sanitize) · `docs/confluence-ia-tree.yaml`(`deferred_followup_lint` CFP-2615 supersede 정합) · `docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md`(규칙 8 CFP-2615 sub-section supersede + frontmatter `deferred_followup_cfps` CFP-2615 entry 정합)
- 신규(Phase 2): `tests/scripts/test_check_doc_frontmatter_category.py`(execution-backed pytest — per-AC discriminating pos/neg + tautology/false-oracle sealing + shrink-only ast-extract + mutation-kill sentinel line) · `.github/workflows/doc-frontmatter-category-test.yml`(wrapper-self-only non-required, day-1 hard-fail pytest — 신규 required context 0)
- grandfather 대상: `archive/adr/ADR-131-cross-repo-responsibility-placement-governance.md` · `archive/adr/ADR-132-consumer-branch-protection-auto-wire.md` · `archive/adr/ADR-133-adr-reservation-atomic-claim.md`
- 번호 claim: `archive/adr/ADR-RESERVATION.md`(row 153 dual-key 3-leg) — origin/main max=152 fresh 실측(git ls-tree, 149 orphan gap), GH_TOKEN 부재로 OCC primitive 대신 RESERVATION row(ADR-133 §결정4 fallback)
- 선례: `scripts/lib/check_doc_frontmatter.py` `KIND_VALID`(값-검증 동형) · ADR-150(§8.9 fail-closed lint + 기존 required strict context 편승 형판) · ADR-152(§8.10 dark-path — 최근접 구조 twin) · ADR-151(self-test execution-liveness 인벤토리 — `.py` N/A 근거) · ADR-145(ac-traceability RTM location-resolution) · ADR-102(traceable-reversal) · ADR-058(§결정 3 sunset 3-tuple / §결정 5 약화 evidence-gate) · ADR-091(§결정 4 단일 owner location) · ADR-127(full 10-lane, doc-only fast-path 폐지)
