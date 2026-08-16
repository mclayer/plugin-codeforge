---
kind: concept_definition
type: domain-knowledge
slug: verification-domain-deficit
title: Verification-domain deficit (검증 정의역 결손 — 처방 정의역 P ⊋ 검증 정의역 V, D = P \ V 가 다음 회차의 결함이 된다)
status: Active
updated: 2026-08-15
carrier_story: CFP-2985
related_adrs:
  - ADR-067  # fix-ledger implementability escalation — affected_scope / affected_paths_with_depth 도입 (선행 부분시도, warning-tier)
  - ADR-070  # verify-before-trust — FIX close 시점 적용, replay_verdict 3-상태 disposition
  - ADR-119  # research-before-claims Amd 2 — "수정됨 = 반증 후 단언" close-time wire
  - ADR-155  # dev-process observability substrate — _ROW_KEYS 18-field allow-list (집계 기질)
  - ADR-156  # metric aggregation escalation feed — root_cause_class uncomputable_missing_key DEFAULT 경로
related_concepts:
  - vacuous-pass                             # 퇴화 사례 (V = ∅). 본 개념은 진부분집합 사례 (∅ ⊊ V ⊊ P)
  - mutation-based-hollow-gate-detection     # 게이트가 "무엇을 검증하는가" 를 반증 — 본 개념의 detector 축 자매
  - fix-ground-truth-replay                  # V = {reproducer_command} 싱글턴을 계약으로 고정한 당사자
  - lane-verification-floor                  # 검증 강도(누가 봤나) 축 — 본 개념은 검증 범위(어디까지 봤나) 축, disjoint
  - claim-to-evidence-audit                  # 주장↔증거 대응 축
tags:
  - verification-domain
  - variant-analysis
  - incomplete-fix
  - omission-error
  - sibling-site
  - defeater
  - baconian-probability
  - odc
  - fix-close-gate
sources:
  - https://projectzero.google/2022/06/2022-0-day-in-wild-exploitationso-far.html   # Project Zero — 2022 상반기 in-the-wild 0-day 중 9건이 기존 패치 취약점의 variant
  - https://github.blog/security/vulnerability-research/codeql-zero-to-hero-part-3-security-research-with-codeql/  # variant analysis 정의 + MRVA
  - https://arxiv.org/pdf/2511.17799                                                 # Incomplete security bug fixes in Linux kernel — "missing similar components" 분류
  - https://ieeexplore.ieee.org/document/6224298                                     # Park et al. MSR 2012 — supplementary bug fixes, 22~33% 가 2회 이상 수정
  - https://link.springer.com/article/10.1007/s10664-016-9432-x                      # An empirical study of supplementary patches in open source projects (EMSE)
  - https://resources.sei.cmu.edu/asset_files/TechnicalReport/2015_005_001_434813.pdf # Goodenough/Weinstock/Klein — Eliminative Argumentation, defeater, Baconian x|y
  - https://arxiv.org/abs/2405.15800                                                 # Defeaters and Eliminative Argumentation in Assurance 2.0
  - https://arxiv.org/abs/2205.04522                                                 # Assessing Confidence with Assurance 2.0 — confirmation bias / Negative Perspective
  - https://en.wikipedia.org/wiki/Orthogonal_defect_classification                   # ODC — defect type / trigger / qualifier 분리
  - https://www.chillarege.com/odc/                                                  # ODC 원저자(Chillarege) — "defect stream 에서 insight 를 추출"
  - https://ldra.com/ldra-blog/do-178c-structural-coverage-analysis/                 # DO-178C 구조 커버리지 갭 해소 의무 (4-way 사유 분기)
  - https://www.iso9001help.co.uk/10.2-Nonconformity-and-Corrective-Action.html      # ISO 9001:2015 10.2.1 — "유사 부적합이 존재하거나 발생할 수 있는지 판단"
  - https://www.ideagen.com/thought-leadership/blog/the-most-common-fda-483-observations  # FDA 483 최다 지적 = CAPA(21 CFR 820.100)
  - https://sre.google/sre-book/postmortem-culture/                                  # Google SRE — blameless postmortem / action item 추적
  - https://artoflean.com/reference/yokoten/                                         # Toyota yokoten — 대책의 수평 전개
  - https://cacm.acm.org/research/lessons-from-building-static-analysis-tools-at-google/  # Google 정적분석 — "모든 인스턴스를 자동 수정" 지향
---

## 정의

**Verification-domain deficit (검증 정의역 결손)** = 어떤 수정(fix)이 주장하는 **처방 정의역**보다 그 수정을 닫을 때 실제로 재검사한 **검증 정의역**이 좁은 상태. 형식적으로:

- **P (처방 정의역, prescription domain)** = 그 수정의 인과 주장이 논리적으로 적용되는 site 전체 집합. "이 원인 때문에 깨졌다" 라고 말하는 순간, 같은 원인이 성립하는 모든 자리가 P 에 들어온다.
- **V (검증 정의역, verification domain)** = 닫기 시점에 실제로 재검사·재실행·재관찰한 site 집합.
- **D = P \ V (결손)** = "고쳐졌다" 고 선언됐지만 아무도 쳐다보지 않은 자리.

**핵심 명제**: `D ≠ ∅` 이면 다음 회차에서 발견되는 것은 *수리 실패* 가 아니라 **D 의 원소**다. 즉 반복 회차는 "같은 결함을 못 고쳐서" 도는 게 아니라 "고친 적 없는 형제 자리를 이제서야 봐서" 돈다.

### vacuous-pass 와의 관계 (퇴화 vs 진부분집합)

| | 관계 | 게이트가 하는 말 | 실패 형태 |
|---|---|---|---|
| [vacuous-pass](vacuous-pass.md) | `V = ∅` | "위반 0건" | 전칭명제의 공허한 참 — 검사 대상이 없었다 |
| **verification-domain deficit** | `∅ ⊊ V ⊊ P` | "재현 명령이 GREEN 이다" | 참인 진술이지만 정의역이 좁다 — 검사는 했는데 한 자리만 |

vacuous-pass 는 antecedent 가 빈 **퇴화** 사례고, 본 개념은 정의역이 **진부분집합**인 사례다. 둘은 같은 논리 결함군(전칭명제의 정의역 통제 실패)의 두 극이며, vacuous-pass 게이트를 다 통과해도 본 결손은 남는다.

## 컨텍스트

본 개념은 CFP-2985 요구사항 lane 의 실측에서 도출됐다. FIX 3회차 이상 진입 Story **54건**과 나머지 **522건**을
문서 바이트로 정규화해(건/MB) 결함 class 별 밀도를 비교한 결과, "검증 정의역·맹점" 이 **4.10×** 로 최대 판별자였다.
같은 성격의 분석 어휘인 hollow-oracle 은 **0.45×** 로 오히려 낮아, 이 격차가 고회차 Story 의 문서량에서 오는
균일 인플레가 아님이 통제됐다.

왜 이 개념이 필요한가 — 회차의 성질이 "수리 실패" 가 아니기 때문이다. firsthand 기록된 계보는 매 회차가
**같은 class 의 새 인스턴스를 한 층 안쪽에서** 발견한다: 배제 반대급부 미계상 → 표기만 바꾸고 주장 잔존 →
시제 미전환 → 검사 정의역에 자기 기록면 누락 (CFP-2913) / 수직 괴리 → **봉합 커밋 자신이 형제 site 검출력 파괴**
→ 처음부터 없던 커버리지 (CFP-2949). 고칠 대상을 못 고친 것이 아니라, **고칠 대상의 범위를 좁게 잡았다.**

**규범 SSOT = [ADR-181](../../../archive/adr/ADR-181-verification-domain-deficit-normative.md)** (§결정 1 정의 /
§결정 2 불변식 7종 / §결정 3 게이트 설계 제약 / §결정 4 접합부). 본 문서는 **서술 SSOT** 이며,
두 문서가 충돌하면 ADR-181 이 정본이다.

## 왜 이것이 "규율 부족" 이 아니라 "계약이 그렇게 정의함" 인가

codeforge 의 FIX 닫기 규칙은 `docs/inter-plugin-contracts/fix-event-v1.md:304` (base `ecfe62d63`) 에서:

> `FIX "수정됨" close = replay_verdict == PASS 시만 성립 (F-1 — 원 reproducer 재실행 GREEN = 외부 Retest).`

즉 닫기 게이트의 검증 정의역은 **계약상 싱글턴** `V = {reproducer_command}` 다. `reproducer_command` 는 같은 계약 `:88` 에서 "finding 을 정당화한 실패 명령 verbatim + base SHA" — 단수 명령이다.

따라서 형제 자리(sibling site)는 **탐지 실패하는 게 아니라 정의상 검사 범위 밖**이다. 이 게이트를 아무리 성실하게 운용해도 `D` 는 줄지 않는다. 이것이 "FIX = 결함 1건을 고치는 것으로 정의되어 있다" 의 기계적 실체다.

**정직한 라벨**: 이 결손은 `replay_verdict` 의 결함이 아니다. `replay_verdict` 는 자기 목적(고쳤다는 주장의 반증 — ADR-119 §결정 10②)을 정확히 달성한다. 결손은 **그 목적이 정의역을 다루지 않는다는 것**이다. 두 축은 disjoint 이며, 본 개념은 기존 게이트를 대체하지 않고 직교 축을 추가한다.

## 외부 선행 개념 매핑 (용어를 발명하지 않기)

| codeforge 현상 | 표준 용어 | 출처 |
|---|---|---|
| 원인은 맞췄는데 다른 자리에 같은 결함 잔존 | **omission error** / **supplementary bug fix** | Park et al., MSR 2012 |
| 같은 결함 class 의 다른 인스턴스 | **variant** | Project Zero / CodeQL |
| variant 를 능동적으로 찾는 행위 | **variant analysis** | GitHub CodeQL |
| 유사 컴포넌트 중 일부만 패치 | **missing similar components** | Linux kernel incomplete-fix 연구 |
| "이 주장이 틀릴 수 있는 이유" 1건 | **defeater** | Goodenough/Weinstock/Klein (SEI) |
| 해소된 defeater / 전체 defeater 비 | **Baconian probability `x\|y`** | 동상 |
| 커버리지 갭을 사유별로 해소할 의무 | **structural coverage resolution** | DO-178C |
| 유사 부적합 존재 여부 판단 의무 | **ISO 9001:2015 10.2.1** | ISO 9001 |
| 대책의 수평 전개 | **yokoten (横展)** | Toyota TPS |

**결론**: "검증 정의역 결손" 이라는 *관계* 자체에 대한 단일 표준어는 없다. 그러나 그 구성요소는 전부 성숙한 표준어를 갖는다 — 결손의 원소 = **defeater/variant**, 결손의 척도 = **Baconian x|y**, 결손을 메우는 행위 = **variant analysis / yokoten**, 결손 해소를 닫기 조건으로 삼는 게이트 형태 = **DO-178C 커버리지 해소 / ISO 9001 10.2.1 / FDA CAPA**. 새 용어는 관계에만 붙이고 원소·척도·행위는 표준어를 쓴다.

## 핵심 규칙

### VD-1: 인과 주장은 정의역 주장을 수반한다

"원인 = X" 라고 말하는 것은 "X 가 성립하는 모든 자리가 영향권" 이라고 말하는 것과 동치다. 원인을 좁게 쓰면(예: "이 파일의 이 줄") P 가 작아지지만, 그때 그 진술은 **원인이 아니라 위치**다. ODC 가 defect **type**(무엇이 틀렸나) / **qualifier**(빠짐·틀림·불필요) / **trigger**(무엇이 그것을 노출시켰나) 를 분리하는 이유가 이것 — 이 셋이 각각 다른 정의역을 만든다.

**따름정리**: 현행 `원인 판정 ∈ {설계, 구현}` (`fix-event-v1.md:156-161`) 은 ODC 기준으로 cause 속성이 **아니다**. 어느 lane 으로 되돌아갈지를 정하는 **라우팅 결정**이고, ODC 의 어떤 축(type/qualifier/trigger)에도 대응하지 않는다. 2-값은 정의역을 전혀 생성하지 못한다 — `P(설계)` 는 "설계 전체" 라서 쓸모가 없고 `P(구현)` 도 같다.

### VD-2: 결손은 측정 가능해야 한다 — `x|y` 형태

Baconian probability 는 confidence 를 `x|y` (해소된 defeater 수 | 전체 defeater 수) 로 표기한다. FIX 닫기에 그대로 이식하면:

- `y` = 이 원인이 생성할 수 있다고 **선언한** site 수 (열거 결과)
- `x` = 실제로 **검사한** site 수
- `y - x` = 결손, 미해소 잔여

**중요**: `x|y` 는 확률이 아니라 **정직한 미완성 표시**다. `3|7` 은 "43% 안전" 이 아니라 "4개는 아직 안 봤다" 는 뜻이다. 이 점이 본 개념을 점수화·게임화로부터 지키는 유일한 방어선이다 (아래 VD-4).

### VD-3: 열거의 완전성은 증명 불가 — 정직 상한

defeater 열거는 근본적으로 미완결이다. Assurance 2.0 문헌은 "defeater 를 못 없앴으면 그것이 참인지 거짓인지 *모른다*" 고 명시하고, 완전성·불확실성이 assurance case 의 알려진 한계라고 기술한다. 열거를 강제하는 어떤 게이트도 **"전부 찾았다" 를 검증할 수 없다.**

따라서 게이트가 판정할 수 있는 것과 없는 것을 분리해야 한다:

| 판정 | 기계 판정 가능? | 근거 |
|---|---|---|
| 열거가 **존재**하는가 (필드가 비었나) | 가능 | presence check |
| 열거된 site 가 **실재**하는가 (경로가 존재하나) | 가능 | path resolve |
| 검사했다고 한 site 를 **실제로 검사했나** | 부분적 | 실행 증거(명령·diff·grep 결과) 대조 |
| 열거가 **완전**한가 | **불가능** | 정지문제급 / 열거 완전성 미증명 |

"완전한가" 를 기계 판정한다고 주장하는 순간 그 게이트는 hollow 다. 이 구분을 계약 문면에 박아 두는 것이 [hard-gate-self-verification](hard-gate-self-verification.md) 및 ADR-119 정직성 규율과 정합한다.

### VD-4: 열거 연극(enumeration theater) 이 이 개념의 1급 실패 모드다

"영향 site 를 열거하라" 는 요구는 Goodhart 압력에 직접 노출된다. 외부 증거:

- FDA 483 지적 **1위가 CAPA(21 CFR 820.100)** — 즉 "원인 규명 + 재발 방지 + 유사 사례 확인" 을 **법으로 강제해도** 그 프로세스 자체가 최다 부적합 항목이 된다. 강제만으로 품질이 따라오지 않는다는 30년 산업 증거.
- 조직 압력이 "빨리 닫기" 를 요구하면 *그럴듯한* 원인이 *맞는* 원인을 대체한다.
- Google SRE postmortem 실무에서도 action item 종결률이 핵심 지표로 지목될 만큼 후속 조치가 표류한다.
- ODC 자체도 rater 훈련 없이는 inter-rater agreement 가 나쁘다 — 분류 필드는 **훈련·값공간 설계 없이는 신뢰할 수 없는 데이터**를 만든다.

**설계 함의**: 열거 필드는 (a) 값공간이 작고 (b) 열거 방법이 재현 가능(예: grep/query 문자열을 같이 기록)해야 게임 저항성이 생긴다. "몇 개 찾았나" 를 자유서술로 받으면 `1|1` 이 기본값이 되어 필드가 있으나 마나가 된다 — 이는 CFP-2985 가 고치려는 바로 그 상태(계약에 필드는 있고 채워지지 않음)의 재생산이다.

### VD-5: 열거는 재현 가능한 query 로 표현될 때만 검증 가능하다

variant analysis 가 산업에서 작동하는 이유는 "비슷한 걸 찾아봤다" 가 아니라 **query 를 작성해서 코드베이스 전체에 돌렸다** 이기 때문이다. CodeQL 의 MRVA 는 하나의 query 를 수천 프로젝트에 동시 실행한다. Google 정적분석 실무의 지향도 "결함을 찾는 것" 이 아니라 "예상되는 컴파일 에러의 모든 인스턴스를 자동으로 고치는 것" 이다.

**함의**: 열거의 증거는 site 목록이 아니라 **site 목록을 산출한 명령**이다. 목록은 위조 가능하지만 명령은 재실행 가능하다. 이는 `reproducer_command` 가 이미 채택한 설계 원리(명령을 저장해 닫기 시점에 재실행)를 정의역 축으로 확장한 것이며, 동시에 그 계약의 `command` schema 제약(repo-relative 게이트/테스트 호출 형태만, raw shell 금지 — `fix-event-v1.md:88`)을 그대로 상속해야 한다는 뜻이다.

### VD-6: 집계 기질(substrate)이 없으면 필드는 존재해도 데이터가 되지 않는다

codeforge 의 dev-process-event 원장은 **content-blind allow-list** 다 — `scripts/lib/append_dev_process_event.py:391` 는 `_ROW_KEYS` 밖 kwarg 을 **drop** 한다. 그리고 `:514` 는 `len(_ROW_KEYS) == 18` 을 self-test 로 고정한다. 계약 문서 `dev-process-event-v1.md:95` 는 §2 필드표와 `_ROW_KEYS` 의 byte-consistency 를 요구하고 born-drift 를 FAIL 로 규정한다.

**함의 (born-broken 함정)**: Story 문서에 원인 값을 아무리 성실히 적어도, 그 키가 `_ROW_KEYS` 에 없으면 원장 계층에서 **조용히 버려진다**. "필드를 채웠다" 와 "집계된다" 는 별개 명제이며, 후자는 계약 amendment + parity self-test 갱신 + 문서표 동반 수정이라는 확정 cascade 를 요구한다. ADR-164 는 정확히 이 cascade 비용 때문에 상관 ID 추가안을 **기각한 선례**다 (`ADR-164:75`).

## 안티패턴

- **"고쳤으니 닫는다"** — V 를 선언하지 않은 close. 현행 default.
- **원인 필드에 위치를 적기** — "X 파일 Y 함수" 는 정의역을 만들지 않는다(VD-1).
- **`1|1` 기본값** — 열거 필드가 있으나 항상 자기 자신 1건만 담는 상태(VD-4).
- **완전성 주장** — "모든 site 를 확인했다" 는 기계 검증 불가 주장의 참칭(VD-3).
- **목록만 있고 명령 없음** — 재현 불가 열거(VD-5).
- **원장 미배선 채 필드 신설** — silent drop(VD-6).

## 자기적용 (self-application)

본 개념을 도입하는 Story 자신의 FIX 회차가 이 채널의 적용 대상이 **아니면** 그 도입은 born-broken 이다. 근거: codeforge 는 dogfood 프로젝트이고, "닫기 조건" 을 바꾸는 변경은 자기 lane 의 닫기 조건에 즉시 구속된다. 도입 Story 의 §10 FIX Ledger row 가 새 필드를 비워 둔 채 머지되면, 그 필드는 첫날부터 `22/576` 의 운명을 반복한다.

## 경계

본 개념이 **다루는 것**과 **다루지 않는 것**을 명시한다 — 경계를 적지 않으면 개념 자신이 P ⊋ V 를 저지른다.

| 축 | 본 개념 | 인접 개념 (본 개념 아님) |
|---|---|---|
| 검증 **범위** (어디까지 봤나) | ★ **본 개념** | — |
| 검증 **강도** (얼마나 세게 봤나) | 다루지 않음 | `lane-verification-floor` · FIX ground-truth replay(`replay_verdict`) |
| 검사 대상이 **아예 없음** (`V` 공집합) | 다루지 않음 (퇴화 극) | `vacuous-pass` |
| 게이트가 **무엇을 검증하는지** 반증 | 다루지 않음 (자매 축) | `mutation-based-hollow-gate-detection` |
| 주장 ↔ 증거 대응 | 다루지 않음 | `claim-to-evidence-audit` |

**본 개념이 주장하지 않는 것 (over-claim 차단)**:

- `D` 를 **비우는 방법**을 주장하지 않는다. `P ⊋ V` 는 상시 상태이며, 금지 대상은 `D` 의 존재가 아니라
  **`D` 를 미선언으로 두는 것**이다.
- 열거가 **전집합인지 판정**하지 않는다. class 동일성 술어가 결함마다 다르므로(정규식/AST/의미) 기계 판정 불가다.
- **원인 값이 참인지 판정**하지 않는다. 오라클이 없다 — `decided_by` 가 값을 쓰는 주체 자신이라 자기 증명이 된다.
- 위 3항은 `declared` 천장이며, `normative` 로 승격하면 그 순간 유령 선언이 된다.

## 관련 ADR

| ADR | 관계 |
|---|---|
| [ADR-181](../../../archive/adr/ADR-181-verification-domain-deficit-normative.md) | ★ **규범 SSOT** — 본 문서의 정의를 규범으로 확정. 정의 재진술 금지 규율의 발원 |
| [ADR-067](../../../archive/adr/ADR-067-fix-ledger-implementability-escalation.md) | Amendment 4 = FIX 닫기 조건 적용 carrier. 선행 부분시도 = `affected_scope` / `affected_paths_with_depth`(warning-tier) |
| [ADR-119](../../../archive/adr/ADR-119-research-before-claims.md) | §결정 10② "수정됨 = 반증 후 단언" — 반증은 규정하나 **반증의 정의역은 미규정**. 본 개념이 그 공백 |
| [ADR-070](../../../archive/adr/ADR-070-codex-verify-before-trust.md) | verify-before-trust. amendment 13건 전건 `mechanical_enforcement_actions: []` = 선언-only 계보 반면교사 |
| [ADR-155](../../../archive/adr/ADR-155-dev-process-observability-substrate.md) | `_ROW_KEYS` closed allow-list — 집계 기질. 키 부재 시 silent drop(VD-6)의 실물 지점 |
| [ADR-156](../../../archive/adr/ADR-156-dev-process-metric-aggregation-escalation-feed.md) | 집계 회로. `pattern_status = uncomputable_missing_key` 를 **정직-null 로 보고 중** — 결손 공개의 모범 |
| [ADR-151](../../../archive/adr/ADR-151-selftest-execution-liveness-inventory.md) | §결정 7 `presence ≠ truth` — 본 문서 전 규칙의 천장 규범 |

## 변경 이력

| 날짜 | 변경 | carrier |
|---|---|---|
| 2026-08-15 | 최초 작성 — 정의 · 외부 선행 개념 매핑 · 핵심 규칙 VD-1~VD-6 · 안티패턴 · 자기적용 | CFP-2985 요구사항 lane |
| 2026-08-16 | `## 컨텍스트` · `## 경계` · `## 관련 ADR` · `## 변경 이력` 신설 (doc section schema STRICT 충족) + 규범 SSOT = ADR-181 명시. **개념 내용 변경 0** — 섹션 골격과 경계 선언만 추가 | CFP-2985 설계 lane (ArchitectAgent) |
