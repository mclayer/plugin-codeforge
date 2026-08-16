---
adr_number: 177
title: 절대주장 저작 결박 ratchet — 신규 선언 줄에 정직 천장 마커 또는 테스트 동반 의무 (diff-scoped)
date: 2026-08-15
status: Accepted
category: governance
carrier_story: CFP-2949
supersedes: null
amends: null  # new-sibling — ADR-119 §결정 8 이 기계화를 외부 carrier 로 위임했고 ADR-168 §결정 16 은 presence-lint class 라 정의역 disjoint (§결정 1)
related_adrs:
  - ADR-119  # 검증 후 단언 — 본 ADR 이 기계화하는 규범 원본. §결정 3(검증 ∨ abstention) + §결정 8(Wave 1 declarative-only, 기계화는 후속 carrier CFP 의무)
  - ADR-168  # write-time self-write verification — §결정 16(resource-safety-claim ↔ proof-link)이 최근친. 본 ADR 은 그 축을 어휘·정의역 양쪽에서 일반화한 별개 class (§결정 1)
  - ADR-171  # evidence-enforceable promotion framework — 신규 check 는 warning-tier entry 로 등록하고 §결정 6 승격 gate 를 거친다
  - ADR-154  # hard-gate self-verification — ADR 형태 판정(A2-5 both-prong) 구조를 본 ADR 이 답습. 게이트 자기검증 축은 disjoint
  - ADR-158  # author-time self-gate — 저작시점 축 kin. 그쪽은 기존 required 게이트의 shift-left, 본 ADR 은 신규 check 라 disjoint
  - ADR-130  # 게이트 required 승격 시 신 이름 green 재적립 선례 — 본 ADR 이 required 승격을 별 Story 로 미루는 근거
  - ADR-172  # 같은 carrier Story 의 주제 ADR. 본 ADR 과 subject disjoint(잔재 관측 ↔ 저작 결박)
  - ADR-145  # AC-ID zero-drop — 본 게이트의 Story 측 traceability 경로
  - ADR-133  # ADR 번호 atomic claim — 본 ADR 번호(177) 점유 mechanism
related_stories:
  - CFP-2949
related_cfps:
  - CFP-2949  # carrier — 구현리뷰 6 라운드가 같은 class 를 반복 지적한 것이 계기
related_files:
  - tests/scripts/_absolute_claim_ratchet.py  # 검사 SSOT (wrapper 3183cef1b 착지 — ArchitectPL firsthand 실행 확인)
  - tests/scripts/test_absolute_claim_ratchet.py  # 판별력·대조군·mutant 하네스
  - docs/evidence-checks-registry.yaml  # warning-tier entry `absolute-claim-ratchet` 등록 완료 (ADR-171 §결정 5)
  - .github/workflows/absolute-claim-ratchet.yml  # warning-tier job (비-required)
is_transitional: false
mechanical_enforcement_actions:
  - absolute-claim-ratchet  # warning-tier. 배선 = tests/scripts/_absolute_claim_ratchet.py + .github/workflows/absolute-claim-ratchet.yml + evidence-checks-registry entry (wrapper 3183cef1b 착지). required 승격 없음 — branch protection 8-tuple 무변경.
---

# ADR-177: 절대주장 저작 결박 ratchet — 신규 선언 줄에 정직 천장 마커 또는 테스트 동반 의무 (diff-scoped)

## 상태

Accepted (2026-08-15) — CFP-2949 Phase 2 구현리뷰 max-FIX escalation 에 대한 사용자 결정의 결정 기록.

## 컨텍스트

CFP-2949 구현리뷰가 6 라운드를 돌았고, 그중 **4 사이클이 같은 형상으로 재발**했다: **글로 쓴 단정의 정의역이 그것을 검사하는 오라클의 정의역보다 넓다.** 새 docstring·헤더 주석·설계 산출물 문장이 절대주장 어휘를 쓰는데, 그 명제를 정의역으로 삼는 검사가 없어 **RED 가 될 수 없는 선언**이 된다.

계보는 라운드마다 한 겹씩 안쪽으로 이동했다:

| 라운드 | 결함 형상 |
|---|---|
| iter3 | Impl Manifest 수치가 동결 HEAD 아닌 이전 SHA 기준 |
| iter4 | harness 헤더가 subprocess 도달 site 를 하나로 단정 — firsthand 반증 |
| iter5 | `extract_adr_section` 이 자기 docstring 과 다르게 동작 · §8.7 수치 stale 3회차 |
| iter6 | 잔여 열거가 자원 bound 축을 누락 · ADR 문면과 실배선 정면 모순 · docstring 자기모순 |

**직전 라운드(iter5)의 처방은 수치 축을 겨냥했다** — §8.7 Impl Manifest 의 수치 저작 주체를 사람에서 기계로 옮겼다(`gen-impl-manifest.sh` + live 대조 층). 그 처방은 실제로 작동했다: origin/main merge 로 merge-base 가 이동했을 때 live 대조 층이 위반 14건을 잡아냈다.

**그럼에도 다음 라운드에 같은 class 가 재발했고, 재발면이 이동했다.** iter6 findings 8건의 축 분포 = **수치 축 0 건 · 산문 선언 축 5 건**. 즉 iter5 가설(*"괴리는 수치 표면이므로 저작 주체를 기계로 옮기면 닫힌다"*)은 참이었으나 **정의역이 좁았다**. 재발 인스턴스는 전부 **직전 봉합 커밋 자신이 저작한 신규 줄**이었다 — 재시도 기구가 결함 생성기였다.

ADR-067 §결정 2 implementability reassessment 가 3회차로 발동해 정량 dual metric 3/3 HIT + 정성 trigger (i) HIT 로 `reset_and_redesign` 양 conjunct 봉쇄를 판정했고, **escalation 이 의무**가 됐다. 사용자에게 올린 2안 중 **"새로 쓰는 줄만 결박"(diff-scoped ratchet)** 이 선택됐다. 본 ADR 은 그 결정의 기록이다.

## 결정

### §결정 1 — ADR 형태 판정 (Amendment vs 신규 ADR — A2-5 both-prong)

ADR-154 §결정 1 의 both-prong 판정 구조를 답습한다("신규 ADR 없이 기존 ADR 변경 금지" ∧ 그 역 "기존 ADR 로 착륙 가능한데 왜 신규" 양쪽을 반증).

- **Amendment prong (ADR-119 로 착륙) = 기각.** ADR-119 는 본 게이트가 기계화하는 규범의 원본이다 — §결정 3 의 *(검증 선행) ∨ (abstention 명시)* 이접이 본 게이트의 *(테스트 동반) ∨ (`[ceiling:]` 마커)* 이접과 같은 골격이다. 그러나 ADR-119 **§결정 8 이 스스로** `mechanical_enforcement_actions: []` 로 Wave 1 declarative-only 를 못박고, 기계화를 *"ADR-060(→ADR-171) 4-tier promotion framework 경로 — **후속 carrier CFP full-lane 의무**"* 로 **외부 위임**했다. 본 게이트를 ADR-119 Amendment 로 착륙시키면 그 §결정 8 의 위임 결정 자체를 뒤집는다. ⇒ ADR-119 = **norm anchor cross-ref**, home 아님.
- **Amendment prong (ADR-168 §결정 16 으로 착륙) = 기각.** §결정 16 이 최근친이다 — 안전성-claim 에 (a) paired proof-reference **또는** (b) honest-ceiling downgrade 를 요구하는 이접 구조가 본 게이트와 동형이다. 그러나 세 축이 disjoint 다: **① claim 어휘** — §결정 16 은 `closed-set resource-safety/DoS-guard`(catastrophic backtracking·ReDoS·scan cap 등) 한정, 본 게이트는 도메인 무관 일반 절대주장 어휘. **② 대상 정의역** — §결정 16 은 governance/보안 tooling 의 docstring·주석·workflow YAML **아티팩트 스냅샷**, 본 게이트는 **커밋 diff 의 추가 줄**. **③ 판정 형식** — §결정 16 은 스스로 *"mechanism = §결정 15/§결정 11 presence-lint 답습(**신규 CLASS 아님**)"* 이라고 선언한 **정적 presence** 검사이고, 본 게이트는 **변경 이벤트 결박**(co-change)이다. ADR-168 자신의 어휘로 판정하면 본 게이트는 **신규 CLASS** 다. ⇒ ADR-168 = **최근친 cross-ref**, home 아님.
- **Amendment prong (ADR-172 로 착륙) = 기각.** subject-disjoint. ADR-172 = 로컬 스케줄 작업 기반 잔재 관측. 본 ADR = 저작면 결박. 같은 carrier Story 라는 사실은 subject 동일성을 만들지 않는다.
- **신규 ADR prong = 채택.** (i) **distinct context** — 구현리뷰 4 사이클 연속 재발(threshold N=2 초과) + 재발면이 수치→산문으로 이동한 실측. (ii) **distinct decisions** — diff-scoped 정의역(코퍼스 열거자 회피) · co-change 결박 · `[ceiling:]` 마커 문법과 빈 마커 우선순위 · 어휘 한글 한정. (iii) **distinct result** — 신규 warning-tier check + registry entry + 자기적용. G-family 선례(ADR-145/146/148/150/151/152/153/154 = 각 신규 게이트 = 신규 ADR)와 정합.
- **ADR-119/168/171/172 무수정.** 본 ADR 은 cross-ref 만 하고 supersede·rewrite 하지 않는다.

### §결정 2 — 결박 규칙 (줄 단위, 우선순위 순 — 5 tier)

커밋이 절대주장 어휘를 포함한 줄을 **추가**하면 다음 판정을 받는다:

| 우선순위 | 조건 | disposition | 처분 |
|---|---|---|---|
| ① | `[ceiling:]` 마커 + 사유 공백·구두점만 | `empty-ceiling` | **위반** |
| ② | `[bound: <test-symbol>]` + 심볼 실재 | `bound` | 통과 — **강한 해소** |
| ② | 같은 마커 + 심볼 미해소 | `unresolved-bound` | **위반** |
| ③ | `[ceiling: <사유>]` + 사유 유의미 | `ceiling` | 통과 |
| ④ | 마커 없음 + 같은 diff 에 `tests/**` 변경 존재 | `test-accompanied` | 통과 — **약함** |
| ⑤ | 그 외 | `unbound` | **위반** |

**①이 ④보다 앞선다.** 빈 마커는 "천장을 선언하겠다"는 의사표시를 해놓고 내용을 비운 것이라 미선언보다 나쁘고, 동반 통과로 씻겨나가면 ①이 사문이 된다. **②의 미해소도 ④가 씻지 못한다** — 실재하지 않는 테스트 이름을 적어 넣는 것이 가장 값싼 우회이기 때문이다.

**`[bound:]` 심볼 실재 판정은 AST 기반이다.** `tests/**` 를 `ast` 로 파싱해 정의된 함수·클래스 이름을 모아 대조한다. 문자열 매칭(grep)이면 주석·docstring 안 이름이 통과하므로 쓰지 않는다(ADR-136 Amd 3 L3 *"born-missing = ast, grep-only = false-oracle"*). 수집기는 신설하지 않고 같은 문제를 이미 푼 `scripts/lib/check_ac_traceability_matrix.py:collect_test_symbols`(Hop3 born-missing)를 **import 재사용**한다. `symbol_index` 기본값 = 빈 집합(fail-closed)이며 tests 루트 부재는 **판정 불가**로 다룬다(통과 아님).

**마커는 같은 줄에 있어야 한다.** 앞줄에 달아둔 마커는 그 줄을 풀어주지 않는다(줄 단위 판정).

### §결정 3 — 정의역 = 커밋 diff 의 추가 줄 (코퍼스 열거자 회피)

검사 대상은 `origin/main...HEAD` 3-dot diff 의 **추가 줄**뿐이다. 기존 재고는 정의역 밖이다.

이 좁힘은 편의가 아니라 **재귀 회피**다. "선언을 빠짐없이 찾아내는 검사"를 만들려면 먼저 코퍼스 열거자가 완전해야 하는데, 그 완전성을 보증할 수단이 없으므로 열거자 자신이 다시 *"선언 정의역 > 검사 정의역"* 인스턴스가 된다. 목적은 재고 청산이 아니라 **출혈 중단**이다.

비교 축은 §8.7 Impl Manifest 생성기(`scripts/lib/impl_manifest.py:git_diff_axis`)와 **공유**한다 — 두 번째 기준을 정의하지 않는다.

### §결정 4 — 기각한 대안: 재고 전수 결박 (corpus token-bind)

**기각안** = 재고 절대주장 줄(실측 310줄 — wrapper 65 / codeforge-internal-docs 245) 전부에 `[bound: <oracle-id>]` 또는 `[ceiling: <사유>]` 부착을 강제하고 미부착을 위반으로.

**장점** = 신규뿐 아니라 기존 재고까지 덮는다.

**기각 사유** = 310줄 일괄 retrofit 은 **blanket `[ceiling:]` 스탬핑을 유인**한다. 그것은 정확히 본 Story 가 4 사이클 반복한 실패 — *선언으로 검사를 대신하기* — 의 재생산이며, 게이트가 그 유인을 만들면 게이트 자신이 결함 생성기가 된다. **단계 도입**(신규 결박 정착 → 재고 확장)을 채택한다. 재고 확장은 별 Story 의 판단 사항으로 남긴다.

### §결정 5 — 천장을 산문이 아니라 테스트로 각인 (착지 — 심볼 인용)

본 게이트의 최대 우회는 **패러프레이즈**다. 어휘 목록은 의미 판정기가 아니므로, 같은 절대주장을 목록 밖 표현으로 쓰면 통과한다.

이 false-negative 를 **산문 천장이 아니라 테스트 assert 로 박는다** — 목록 밖 등가 표현을 담은 diff 에 대해 위반이 나오지 않음을 단언하는 테스트를 둔다. 그러면 나중에 검사기를 의미 축으로 넓히는 순간 **그 테스트가 RED 가 되어 천장 문서 갱신이 강제**된다. 천장을 문서에만 적으면 검사기가 넓어져도 문서는 stale 로 남고, 그 stale 이 본 ADR 이 겨냥하는 class 다.

★ **착지 (2026-08-15, wrapper `3183cef1b`)**: 각인 심볼 = **`test_paraphrased_absolute_claim_is_outside_detection_domain`** (`tests/scripts/test_absolute_claim_ratchet.py`). 등가 표현 3종을 쓰며, 각 표현에 대해 **먼저 어휘 매칭이 비었음을 확인**한 뒤 claim 이 잡히지 않음을 단언한다 — 그 선행 확인이 없으면 어휘가 나중에 확장됐을 때 각인이 조용히 무의미해진다.

★ **저작 이력 (은폐 금지)**: 본 ADR 초판(`8266e0e82`)은 이 결정을 **미착지**로 기록했다. 당시 실측에서 같은 테스트 파일의 test 함수 22개를 전수 열거했고 해당 각인은 부재였으며, 천장은 검사 모듈 docstring **산문**에만 있었다 — 즉 게이트가 자기 천장을 자기 규칙으로 결박하지 않은 상태였다. ArchitectPL 이 그 사실을 회부했고 구현 lane 이 각인을 신설해 닫았다(테스트 22 → 34). **초판의 "미착지" 기재를 삭제하지 않고 이력으로 남긴다.**

### §결정 6 — 정직 천장 (over-claim 차단 — 7항) + 실측 정량치

**★ 본 게이트가 세우는 것은 *"신규 선언이 오라클에 결박된다"* 가 아니라 「천장 마커 결박 ⊕ 테스트 동반(판별력 낮음) ⊕ `[bound:]` 심볼 실재 검증」이다.** 이 문면보다 넓게 기술하지 말 것.

**실측 정량치 (wrapper `3183cef1b`, 브랜치 diff 전수)**:

| 모드 | 결과 |
|---|---|
| 기본 | 위반 없음 · `bound` 0 · `ceiling` 7 · `test-accompanied` **132** (추가줄 9915 중 claim 139) |
| strict (④ 동반 해소를 무효화) | **위반 132** |

⇒ **④ 가 얼마나 약한지를 주장이 아니라 수치로 남긴다.** claim 139 중 **132(약 95%)** 가 ④ 로 통과했다. 리포트는 ④ 통과 줄을 **전량 열거**한다(무증상 통과 금지).

**천장 7항**:

1. **④ 는 결박이 아니라 동반 강제다.** `tests/**` 의 *어떤* 변경이든 통과시키며, 그 변경이 해당 명제를 정의역으로 삼는지 판정하지 않는다. 실효 판별력의 정량치가 위 132/139 다. ④ 를 제거하지는 않았다 — 제거하면 기존 저작 흐름이 막히므로, 대신 저자가 고를 수 있는 **강한 해소 경로로 ②(`[bound:]`)** 를 뒀다.
2. **`[bound:]` 도 심볼 실재까지만 본다.** 그 테스트가 해당 명제를 실제로 반증하는지는 판정하지 않는다 — 이름만 맞는 무관한 테스트여도 통과한다.
3. **패러프레이즈 false-negative 잔존.** 어휘 목록 밖 표현은 통과한다(§결정 5 가 이 범위를 테스트로 각인).
4. **use 와 mention 을 구분하지 못한다.** 어휘를 *언급*하는 줄(어휘 정의 · 합성 fixture · 검사 자신을 설명하는 산문)도 걸린다. 그 줄들은 `[ceiling:]` 로 정직하게 처리한다.
5. **기존 재고 미커버 + cross-repo 미도달.** 재고 310줄 중 245줄은 `codeforge-internal-docs`(Change Plan · Story) 소재라 wrapper CI 에 경로가 없고, 그 repo 의 기본 브랜치는 required check 를 보유하지 않는다.
6. **커밋 기준이다.** 워킹트리에만 있고 커밋되지 않은 줄은 검사 대상이 아니다.
7. **마커는 같은 줄만 · 비-required · 어휘는 한글 한정.** bypass env 는 **두지 않았다** — 비-required 라 막을 merge 가 없어 완화 대상이 성립하지 않기 때문이다. **required 승격 시 bypass 채널 신설이 의무**가 된다(§결정 7).

**본 게이트가 잡지 못하는 결함 class (명시)**: CFP-2949 iter6 F-CR6-01 형 — *자원 bound(작업량 상한)가 만든 탐지 공백* — 은 선언↔오라클 결박 문제가 아니라 **bound 의미론**("못 찾음"을 "없음"으로 결론짓는가) 문제다. 같은 Story 의 잔여 **축 오분류**(ADR-172 A4-3 — 잔여를 열거해도 축을 틀리게 붙이면 모순이 검출되지 않는다) 역시 어휘 결박의 정의역 밖이다.

### §결정 6.1 — 자기적용이 형식이 아니었다는 증거 (실측 이력)

게이트 **첫 실행에서 게이트가 자기 자신을 잡았다** — `tests/scripts/_absolute_claim_ratchet.py:54` 가 rc=1 로 FAIL 했고, 원인은 저자가 마커를 **앞줄 주석**에 달아 둔 것이었다. 처분은 규칙 완화(앞줄 마커 허용)가 아니라 **같은 줄 trailing 으로 이동**이었고, 그 형상을 `test_ceiling_marker_on_preceding_line_does_not_discharge` 로 고정했다.

**교차 검증**: 같은 게이트가 ArchitectPL 이 ADR-172 Amendment 4 에 단 `[ceiling:]` **5줄**을 정상 해소했다 — 즉 자기 파일만 통과시키는 자기정합이 아니다.

### §결정 7 — required 승격 금지 (branch protection 무변경)

본 게이트는 **warning-tier 로만 착지**한다. wrapper branch protection required contexts **8-tuple 은 변경하지 않는다.**

승격 경로는 ADR-171 §결정 6 승격 gate(binary AND condition)를 따르며, 신 job 이름으로 green 을 재적립하는 기간이 선행해야 한다(ADR-130 §결정 6 이 정확히 그 chicken-egg 로 rename 을 deferred 시킨 선례). ⇒ 승격은 **별 Story** 의 사안이고 본 Story 에서 수행하지 않는다.

registry 등록은 ADR-171 §결정 5(신규 entry = warning mode continue-on-error) 절차를 따른다. **등록 완료** — `docs/evidence-checks-registry.yaml` entry `absolute-claim-ratchet`(`current_tier: warning` · `owner_adr: ADR-177` · `carrier_adr: ADR-171` · `promotion_trigger: advisory`). ★ **정직 기재**: registry 미등록을 FAIL 시키는 **역방향 스캔 게이트는 부재**로 실측됐다 — 즉 *"registry 등재가 기계로 강제된다"* 로 쓰면 안 되며, 이 등록은 **저작 규율 준수**의 산물이다. `bypass_label` 은 omit 했다(warning tier 라 막을 merge 가 없어 완화 대상이 성립하지 않는다). **required 승격 carrier 가 bypass 채널 신설 의무를 승계**한다.

### §결정 8 — 자기적용 (dogfood)

본 게이트는 **자기 자신의 산출물에 선적용**된다 — 검사 모듈·테스트·본 ADR 문면이 전부 정의역 안이며, 절대주장 어휘를 쓴 줄은 같은 규칙으로 `[ceiling:]` 마커를 달거나 위반으로 계상된다. 자기적용을 면제하면 게이트가 자기에게만 관대한 구조가 되고, 그 형상은 본 Story 가 반복 처벌해온 *제정자 = 수혜자* 구조다.

어휘는 **한글 한정**으로 고정한다. 영문 등가어(`always` / `atomic` 등)는 이 repo 에서 오탐원이다 — `.github/workflows/**` 의 `always()` 16 site 가 실측 근거다. 어휘 목록 자체는 테스트가 고정한다(목록 변경 = 테스트 변경 강제).

## 결과

**얻는 것 (1 class 만 정직 기재)**: 새로 저작되는 절대주장 줄이 **정직 천장 선언 없이는 조용히 들어오지 못한다**. iter6 재발 인스턴스가 전부 직전 봉합 커밋 자신이 저작한 신규 줄이었으므로, 겨냥 지점은 결함 생성기 자체다.

**얻지 못하는 것**: 재고 청산 · 패러프레이즈 차단 · 명제-오라클 실 대응 판정 · cross-repo 도달 · bound 의미론 결함 검출. 넷째까지는 §결정 6 이, 다섯째는 §결정 4 가 각각 정직 기재한다.

**비용**: wrapper CI 1 job(warning-tier) + 저작자 측 마커 부착 습관. 기존 재고 파일은 미접촉이라 대량 retrofit diff 가 발생하지 않는다.

**측정 가능한 실패 신호**: `[ceiling:]` 마커가 사유 없이 남발되기 시작하면(빈 마커 위반 건수가 아니라 *유의미하지만 내용 없는* 사유 문자열의 증가) §결정 4 가 기각한 blanket 스탬핑이 신규 줄에서 재현되는 것이다. 그 신호가 관측되면 본 ADR 은 재검토 대상이다.

## 관련 파일

- `tests/scripts/_absolute_claim_ratchet.py` — 검사 SSOT (어휘·판정 우선순위·리포트)
- `tests/scripts/test_absolute_claim_ratchet.py` — 판별력 · 대조군(오탐) · mutant 하네스 · live 자기적용
- `docs/evidence-checks-registry.yaml` — warning-tier entry `absolute-claim-ratchet` (ADR-171 §결정 5, 등록 완료)
- `.github/workflows/absolute-claim-ratchet.yml` — warning-tier job (비-required)
- `archive/adr/ADR-119-research-before-claims.md` — 규범 원본 (§결정 3 이접 · §결정 8 위임)
- `archive/adr/ADR-168-write-time-self-write-verification-mandate.md` — 최근친 (§결정 16 presence-lint class)

## 해소 기준

본 ADR 은 영구 정책이 아니라 **재검토 조건을 보유한 도입기 결정**이다.

1. **재고 확장 판단** — 신규 결박이 정착(연속 라운드에서 신규 `unbound` 위반 유입이 관측되지 않음)한 뒤, §결정 4 가 미룬 재고 확장을 별 Story 가 판정한다.
2. **required 승격 판단** — ADR-171 §결정 6 승격 gate 충족 시 별 Story 가 판정한다(§결정 7).
3. **폐기 조건** — §결정 5 의 패러프레이즈 각인이 착지한 뒤에도 산문 축 재발이 계속되면, 어휘 기반 접근 자체가 부적합하다는 신호이므로 본 ADR 을 재제정 대상으로 올린다.
