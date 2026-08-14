---
adr_number: 175
title: landed 셸 게이트의 hollow 여부를 커밋된 2-arm corpus 실행으로 분류하는 fail-closed 메타-게이트 신설 — M-1(동적 kill 분류 + arm-invariant 판정기 계약) · M-2(분모 단조 하한) 2 축 ONLY + sidecar manifest 스키마. 검출 sufficiency=undecidable 정직 천장 무손상(INV-5 불가침), 재귀 자기적용
status: Accepted
category: governance
date: 2026-08-15
carrier_story: CFP-2963
supersedes: []
related_adrs:
  - ADR-154  # 강 의존(핵심 렌즈, **무수정 cross-ref** — supersede/rewrite 0). 적용 대상(landed-gate 정의) = ADR-154 Amendment 2 A2-2 가 SSOT 로 보유하며 본 ADR 은 재정의하지 않고 참조만 한다(§결정 2). 재사용 조항: §결정 2 3-way taxonomy / §결정 4 honest-ceiling + INV-5 / §결정 5 2-control(positive-control ⊕ internal-control) / §결정 6 fail-direction + T-TRAVERSE / §결정 7 born-hollow 금지 + `sed-mutation on REAL gate copy` + inventory bijection cross-seal / §결정 8 5-piece chain + warning-tier / §결정 9 재codify 0. 본 ADR = 그 조항들의 **corpus 실행 축 신규 mechanism** 이며 조항 자체를 개정하지 않는다
  - ADR-151  # 강 의존 — §결정 1 신규 ADR prong 3-conjunct((i) 신규 fail-closed 메타-게이트 (ii) 신규 인벤토리 스키마 (iii) 메타-게이트 자신의 재귀 L3 자기적용) 가 본 건에 **3/3** 성립해 형태 판정의 결정 근거(§결정 1). 배선면: 신설 harness self-test 가 인벤토리에 1행 enroll(8-field 스키마 **무접촉** — 확장은 sidecar 분리). 인벤토리 스키마 자체는 amend 하지 않는다
  - ADR-152  # 정합만(cross-ref, amend 금지) — discriminating-A/B 어휘·honest-ceiling 구조 + §결정 8 `KILLED ⟺` 단정 형판. 본 ADR 의 verdict 함수는 그 형판의 corpus 축 파생이며 어휘를 재정의하지 않는다
  - ADR-168  # 무접촉(경계) — 구 ADR-082 재제정본. write-time semantic truth verify super-class 는 kin 이나 본 ADR 은 cross-ref 만
  - ADR-171  # 승격 evidence-gate 축 — §결정 6 3-AND(PR 누적 ≥20 / failure=0 / sibling) + §결정 10 velocity-normalized 증거 기한. 본 게이트 day-1 = warning-tier, required 승격은 그 프레임으로 defer(등급·승격 축 ⊥ 검출보장 축)
  - ADR-157  # 형판 제공(기전 차용 · 방향 반전) — `docs/infra-resource-baseline.yaml` + `scripts/lib/check_infra_resource_drift.py` 의 baseline 무결성 기전(content_digest 결박 · single-writer · audited-escape · exit 3 substrate-failure)을 D-3 이 차용하되 **단조 방향을 반전**한다(§결정 5). ADR-157 무수정
  - ADR-130  # 배선 제약 — §결정 6 7일 green 미적립(day-1 required 구조적 불가) + `on: paths:` 금지(required check permanent-pending 함정). 계약 소유자 아님
  - ADR-145  # 정합만 — G1 3-tier AC(normative/declared/advisory) 문법. 본 게이트의 self-test 는 셸이라 `ac-traceability-matrix` 명명 테스트 열 정의역 밖(§결정 10 회부 declare)
  - ADR-133  # ADR 번호 claim — 본 ADR 번호(175) OCC atomic claim(§결정 11). dual-key 3-leg 정합
  - ADR-119  # research-before-claims / 게이트=ground-truth — 정직 천장(§결정 9) + 제안 필요성 게이트 통과 근거 + "absence of evidence ≠ evidence of absence"(도달 마커 요구의 근거)
  - ADR-127  # no-exemption — D-4 `non-applicable` opt-in 미제공의 정신적 근거(면제 칸 = 우회로). skip-offer 금지 정합
  - ADR-174  # sibling(동 carrier Story CFP-2963) — MCLATS ARC CI 러너 topology. subject disjoint(러너 인프라 ⊥ 게이트 검출-integrity), 본 ADR 과 무충돌
  - ADR-013  # dogfood-out — 본 ADR = 결정면 SSOT, 배선면 = internal-docs `wrapper/change-plans/cfp-2963-mclats-arc-ci-runner.md` §8.QC-MECH
related_concepts:
  - mutation-based-hollow-gate-detection
  - execution-based-review-verification
  - lane-verification-floor
is_transitional: false
---

# ADR-175 — landed 셸 게이트 hollow 여부의 corpus 동적 실행-분류 메타-게이트

## 상태

Accepted (2026-08-15 KST) — CFP-2963 carrier. *"검사처럼 보이나 어떤 입력으로도 FAIL 하지 않는 게이트"* 를 **커밋된 2-arm corpus 를 실행해 분류**하는 fail-closed 메타-게이트를 신설하는 governance SSOT. ADR-154 가 세운 정적 presence/shape 축은 **형태가 정상인 행위 결함**(fail-open 셸 술어 · index-pin 정의역 누락)을 구조적으로 담지 못하고, 광역 정적 스캔은 ADR-154 §결정 3 이 이미 기각했다 — 남는 통로가 실행 관측 하나이므로 그 통로를 신규 mechanism 으로 연다.

**신규 normative = M-1(2-arm corpus 동적 kill 분류 + arm-invariant 판정기 계약) · M-2(분모 단조 하한) 2 축 ONLY.** 나머지는 전부 ADR-154 기존 조항 재사용이며 **재codify 0**(§결정 6). 강화(ratchet↑) 방향 · 약화 surface 0(신규 required context **0** · branch-protection **8-tuple 무변경** · inter-plugin 계약 무변경 · 신규 category 0). **INV-5(ceiling immutable) 무손상** — 본 ADR 은 L3 detection sufficiency 를 기계강제로 격상하지 않으며, 그 격상 시도 자체가 INV-5 위반이다.

## 컨텍스트

### 도메인 사실 (firsthand 실측 — 2026-08-14~15)

- **기존 3층의 정의역 경계**: `scripts/lib/check_hard_gate_self_verification.py:57` 의 subject 발견 계약 = `<DIR>/tests/scripts/*.sh` **∧** inline enrollment marker(`hard-gate-self-verification: enrolled` | `hgsv-enroll`, 상수 `:106 _ENROLL_MARKERS`). ⇒ subject 3 조건 = ① 같은 repo ② `tests/scripts/*.sh` 경로 ③ opt-in 마커. **lane 산출물로 저작된 셸 게이트는 전건 불충족 = 구조적으로 정의역 밖**이며, 이는 층 B 의 결함이 아니라 **설계된 경계**다.
- **정적 축이 담지 못하는 형상**: 본 arc 가 낳은 대표 결함(게이트 판정이 `if` 조건절 안에 있어 `set -e` 면제 → rc≠0 을 삼키는 fallback → 정수 비교 실패 rc=2 → else 로 흐름)은 **정적 형태가 정상**이다. 위반은 형태가 아니라 *어떤 입력에서도 FAIL 하지 않는다* 는 **행위**에 있다.
- **광역 스캔은 기각 상태**: ADR-154 §결정 3 = *"광역 archetype-B silent-fallback scan 채택 안 함 — honest-degrade FP 지뢰밭(26 script / 127 occurrence 정당 no-op)"*. 어휘 열거로 관용구를 잡는 설계는 본 ADR 하에서도 채택 불가다.
- **corpus 구축 가능성**: `scripts/*.sh` **176** 중 순수 forwarder **71** ⇒ 실 술어 보유 ≈ **105**. *"wrapper 셸이 전부 thin forwarder 라 corpus 구축 불가"* 주장은 실측으로 반증됐다.
- **census 실측**: `tests/scripts/*.sh` = **76** / `docs/selftest-execution-liveness-inventory.yaml` 레코드 = **76** / `docs/evidence-checks-registry.yaml` entry = **112** / `scripts/check-*.sh` = **118** `[ArchitectAgent firsthand]`.
- **판별자 실측 모집단**: `scripts/lib/check_*.py` **83** 중 종단 성공 emit 보유 = **34**, 그중 계수를 문면에 임베드한 것 = **14**. 마커 계약을 *계수 임베드* 로 잡으면 정의역이 14 로 좁아지고, *입력 의존 종단 문면* 으로 잡으면 34 로 넓어진다.

### 왜 지금 (제안 필요성 게이트 — ADR-119 §결정 9 3-질문 통과)

① **깨졌나** — 본 arc 검토에서 *"검사처럼 보이나 아무것도 막지 않는 것"* 이 반복 발현했고, 그중 기계 판정 가능 유형이 기존 3층 정의역 **밖**에 있음이 실측으로 확정됐다. ② **이득 > 비용** — 5-piece chain 은 landed 형판이라 신규 chain 형식 0 이고, 신규 mechanism 은 corpus discovery adapter 하나다. ③ **관찰자 없어도 할 일** — 사용자가 명시 선택한 처분(*"기계 강제 검사를 신설"*)이며 A안(*"지금대로 + 정직 기록"*)은 명시 거부됐다.

## 결정

### 결정 1 — ADR 형태 판정: 신규 ADR 채택 (설계리뷰가 Amendment 판정을 뒤집었다 — 판정 전환의 정직 기재)

**★ 판정 이력을 무언 폐기하지 않는다.** 본 계약은 설계 lane 초판에서 **ADR-154 Amendment 2 로 착지**했고, 그 판정(A2-1)은 §결정 1 3-prong 자기적용 = **1/3** 을 근거로 Amendment 를 채택했다. **설계리뷰가 그 판정을 뒤집었고(DR-M5), 본 ADR 이 그 전환의 착지점이다.** A2-1 의 근거는 이력으로 보존하되 결론은 전환된다.

| prong (ADR-154 §결정 1) | A2-1 자기판정 | **재판정** | 근거 |
|---|---|---|---|
| (i) distinct context | 부분 성립 → 기각 | **부분 성립** | 모집단 상이(셸 게이트 · lane 산출물)는 사실. 기각 근거였던 Amendment 1 선례는 본 건에 부적용(아래 ②) |
| (ii) distinct decisions | 기각 (*"신규 결정 1 점뿐"*) | **부분 성립 — 자기 계수와 모순이었다** | 같은 Amendment 의 A2-6 이 *"신규 normative 는 M-1 · M-2 **둘뿐**"* 을 선언한다. (ii) 기각은 자기 문서가 **2** 라 한 수를 **1** 로 세워야 성립하므로 불가. M-2(분모 단조 하한)는 modality 가 아니라 **census 불변식**이다 |
| (iii) distinct result | **성립(자인)** | **성립** | 신규 fail-closed 메타-게이트 **1** + 신규 workflow **1** + 신규 sidecar manifest 스키마 **1** |

**⇒ 리트머스 = 2~3/3 → 신규 ADR.** A2-1 이 Amendment 채택 근거로 든 3 중 2 가 반증되고 1 만 견고하게 잔존한다:

1. **근거 1(*"§결정 9 + §결정 2 가 신규 ADR 을 구조적으로 막는다"*) = 거짓 딜레마.** 신규 ADR 이 super-class·taxonomy·2-control 을 *다시 정의해야 한다* 는 명제가 성립하지 않는다 — **ADR-154 §결정 1 자신이** *"본 ADR 은 cross-ref/재사용만 하고 supersede/rewrite 하지 않는다"* 로 착지했고 ADR-151 §결정 1 도 동문을 보유한다. Epic CFP-2602 G-family(ADR-145/146/148/150/151/152/153)가 전부 그 형태다. 결정적으로 **A2-1 이 스스로 등재한 반대 처분**(*"신규 ADR + ADR-154 전면 cross-ref(재codify 0 유지)"*)이 이 근거를 자기 무력화한다.
2. **근거 3 + (i) 기각이 의존한 Amendment 1(A1-1) 선례 = 본 건에 부적용.** A1-1 은 **0/3** 이고 (iii) 를 *결정적으로* 기각하며 그 사유가 *"결과가 남의 carrier"* 였다. **A2-1 자신이 *"그 사유는 본 건에 없다"* 라고 자인**한다 — 결정적 prong 이 반대로 뒤집힌 사안에 선례를 확장한 것이다. 또한 A1-1 은 declaration-only · **신규 workflow 0** 이었고 본 건은 **workflow 1** + 메타-게이트 1 + 스키마 1 이다.
3. **인용된 두 test 가 오히려 신규 ADR 방향.** **ADR-151 §결정 1** 신규 ADR prong 3-conjunct 실문언 = *(i) 신규 fail-closed 메타-게이트 (ii) 신규 인벤토리 스키마 (iii) 메타-게이트 자신의 재귀 L3 자기적용* — 본 건은 **3/3**: (i) A2-1 자인 ✓ / (ii) sidecar manifest = **신규 durable 스키마** ✓(*"남의 스키마를 확장하지 않았다"* 와 *"신규 스키마 0"* 은 다른 명제이며, A2-8(b) 자신이 *"필드 정의 + versioning 미확정"* 으로 신규 스키마의 실재를 자인했다) / (iii) 자기적용(§결정 4 ⑧) ✓.

**⇒ 잔존하는 견고한 근거 = 1건뿐(A1-3 조건절의 SSOT 귀속).** *"A1-3 의 유보가 언제 풀리는가"* 의 소유자가 ADR-154 라는 것은 **참**이며, 남의 문서가 그 조건을 해제하면 A1-3 의 의미가 두 문서에 갈린다. ⇒ **처분 = 분할**:

- **ADR-154 Amendment 2 = 축소 존치** — A2-2(적용 대상 확장 = landed-gate) + A1-3 조건 해제 명시 + 본 ADR 로의 포인터. SSOT 귀속 보존.
- **본 ADR = 신규 normative 본체(M-1·M-2) + 경계·opt-in·manifest·천장·결속** 이관.

이 분할은 **normative 본체 2벌 저작(DR-M8)도 동시에 해소**한다 — 결정면 정본 = 본 ADR 단독, 배선면 = Change Plan §8.QC-MECH 이며 중복 표 0 이다. 따라서 *"천장 동시-변경 불변식"* 의 양단은 이제 **본 ADR §결정 9 ↔ §8.QC-MECH MECH-9** 다.

**경쟁 home 배제(무언 폐기 금지)**: **ADR-151** = self-test 코퍼스 execution-liveness(채널 alive) — subject disjoint, 본 ADR 은 인벤토리 8-field 스키마를 확장하지 않는다. **ADR-171** = 승격 evidence-gate 축 — 등급/승격 축 ⊥ 검출보장 축. **ADR-130** = 배선 제약이지 계약 소유자 아님. **ADR-157** = 형판 제공자이며 본 ADR 이 그 문서를 개정하지 않는다.

### 결정 2 — 적용 대상 = landed-gate (ADR-154 Amendment 2 A2-2 cross-ref · 재codify 0)

적용 대상 모집단의 정의 SSOT 는 **ADR-154 Amendment 2 A2-2** 가 보유한다 — *"lane 산출물로 저작돼 repo 에 landed 된 게이트 스크립트(셸 포함) — 경로·커밋·해시라는 안정 좌표를 보유하는 모집단"*. 본 ADR 은 그 정의를 **참조만 하고 재정의하지 않는다**(§결정 9 재codify 0 동형). A1-3 의 조건부 유보가 해제되는 조건도 ADR-154 소유다.

**적용 = 신규·개정 landed-gate. forward-only ratchet** — 이미 착지한 산출물(76 self-test 포함)을 소급 위반으로 재분류하지 않는다. retrofit 은 review-tier + 별 carrier defer(ADR-171 evidence-gate 형판).

**★ 미측정 정직 고지**: landed 76 self-test 가 실제로 M-1·M-2 결함을 보유하는지는 **재지 않았다**. 그래서 소급 강제도 하지 않고 *"landed 는 안전하다"* 는 단정도 하지 않는다 — 둘 다 근거가 없다.

### 결정 3 — ★경계: 무엇을 끌어들이지 않는가 (born-broken · 무한후퇴 방지)

- **⊥ cross-repo fetch** — 배선은 **wrapper 자기 게이트 한정**이다. PUBLIC repo 의 CI 가 PRIVATE repo 를 읽으려면 토큰이 필요하고 fork PR 은 secrets 미전달이므로 **가장 낮은 신뢰 모집단에서 정확히 게이트가 조용히 degrade** 한다 — 게이트가 자기 목적을 배반하는 형태다. 타 repo 커버리지는 그 repo 자체 CI 의 별 carrier 소관.
- **⊥ 3번째 메타 층** — 신설 게이트의 무결성은 **ADR-154 §결정 7 inventory bijection cross-seal 에 편입**하는 것으로 닫는다(§결정 4 ⑧). *"게이트를 검증하는 게이트를 검증하는 게이트"* 를 만들지 않는다. **차단점은 이미 §결정 7 이 소유**하며, 그것이 닫는 것은 **미enroll 회귀**다 — **위조 판정기 회귀는 별 축(대조군 설계)** 이므로 두 축을 혼동해 상위 주장으로 읽지 말 것.
- **⊥ ADR-151 인벤토리 스키마 확장** — 신설 게이트 self-test 는 인벤토리에 **1행 enroll** 하되(bijection 유지) 게이트 manifest 는 **sidecar 분리 + foreign key join** 이다(§결정 8). 근거 = 키스페이스 상이(인벤토리 키 = self-test 경로 **76** ↔ 게이트 키 = registry entry **112** / 셸 게이트 파일 **118**) — 한 테이블을 넓히면 sparse-wide + 다중 키 혼재로 **bijection 이 새 키를 검증하지 못한 채 형식만 통과**한다.
- **⊥ 광역 정적 스캔** — ADR-154 §결정 3 무변경(기각 상태 유지).
- **⊥ 신규 required context** — day-1 등재 0(§결정 9).

### 결정 4 — 신규 normative ① **M-1 = 2-arm corpus 동적 kill 분류 + arm-invariant 판정기 계약**

landed-gate 의 hollow 여부를 **커밋된 corpus 를 실행해 분류**한다. 구성 9:

**① 2-arm 전건 AND**

| arm | 표본 | 기대 verdict | 없으면 무엇이 통과하는가 |
|---|---|---|---|
| **arm-H** | 어떤 입력에서도 FAIL 하지 않는 게이트 표본 | `HOLLOW` | *"아무것도 잡지 못하는 판정기"* 와 **구별 불가** |
| **arm-L** | 결함 입력에서 FAIL 하고 정상 입력에서 PASS 하는 표본(**대조군**) | `LIVE` | ***"전부 HOLLOW 로 찍는 무조건-true 판정기"*** 가 arm-H 만으로 만점 |

**arm-H 전건 `HOLLOW` ∧ arm-L 전건 `LIVE`** 일 때만 PASS.

★**2-control 과의 관계 — 상속 주장을 정정한다(거짓 상속 제거).** 2-arm 은 ADR-154 §결정 5 의 **positive-control 축**만 instantiate 한다. arm-H·arm-L 은 **둘 다 subject 측 대조군**이므로 *"선언 대상 = 실행 대상"* 을 증명하는 **internal-control 축은 2-arm 만으로는 미인스턴스화**다. internal-control 축은 아래 **② 도달 판정 probe** 가 §결정 5 internal-control 3형 중 *"unknown-input negative"* 의 **직접 instance**(신규 mechanism 0)로 **부분 충당**한다 — **완전 충당이 아니다**(§결정 9 잔여 참조).

**② 도달 판정 = differential delivery probe (마커 주입 0)**

*"게이트 로직이 판정 지점에 도달했는가"* 는 **주입이 아니라 상속으로** 얻는다. sed 파생 표본은 FAIL 분기만 중화되고 **PASS 경로 종단 emit 은 원본에서 그대로 물려받으므로**, arm-H 에 도달 마커를 새로 손저작할 필요가 없다 — ADR-154 §결정 7 *"손저작 금지"* 및 §결정 6 *"신규 0"* 과 **무충돌**이다.

> **`DELIVERED ⟺ terminal_line(kill-fixture) ≠ terminal_line(empty-fixture)`**

**empty-fixture** = 투입이 전달되지 않은 상태(대상 root 부재가 아니라 **대상 0건**). 종단 문면이 두 투입에서 **같으면** 게이트는 투입을 실제로 소비하지 않은 것이므로 `¬DELIVERED` → **INDETERMINATE**(아래 I-7).

**③ 판정기 계약은 arm-invariant 다 (역산 채널 3개를 닫는다)**

stamp 를 arm 별로 분기하지 **않는다** — 필드 shape 이 arm 을 누설해 역산 채널을 하나 더 열기 때문이다. 마커는 **arm 의 속성이 아니라 대상 게이트의 속성**이므로 **게이트에 keying** 한다. 그 결과 stamp 가 arm-invariant 가 되고 arm 분기는 verdict 함수에서 자동으로 떨어진다.

- ⓐ **파일명·경로 arm 어휘 denylist** — 표본 식별자에 `arm-?[hl]` · `hollow` · `live` 출현 금지. **평면 배치**(arm 별 하위 디렉터리 금지).
- ⓑ **기대 실패 시그니처 필드 제거** — 양 arm 이 **동일 필드집합**을 갖는다. (구 계약이 arm-H 에 요구하던 *"기대 실패 시그니처"* 는 arm-H 에 **정의역 자체가 없었고**, 그 요구가 `arm-H 전건 HOLLOW` 를 도달 불가로 만들어 born-broken 을 낳았다.)
- ⓒ **`declared_arm` projection 배제** — 판정기 프로세스에 arm 선언을 투입하지 않는다.

**④ verdict 함수 (arm 미투입)**

- **`LIVE` ⟺** `kill.fail=1 ∧ fail_stage = kill_target_stage ∧ clean.fail=0 ∧ clean.term=1 ∧ DELIVERED`
- **`HOLLOW` ⟺** `kill.fail=0 ∧ kill.term=1 ∧ clean.fail=0 ∧ clean.term=1 ∧ DELIVERED`
- **그 외 = `INDETERMINATE`**

**⑤ INDETERMINATE 11 조건 전수 + 계상 규율**

| ID | 조건 |
|---|---|
| **I-1** | anchor 매치 ≠ 1(표본 파생 지점 특정 실패) |
| **I-2** | 표본 syntax invalid |
| **I-3** | 기동 실패 · timeout |
| **I-4** | rc ∉ 선언 exit_space |
| **I-5** | 양쪽(kill·clean) 모두 FAIL |
| **I-6** | 마커 전무 = **판정 지점 미도달** |
| **I-7** | `¬DELIVERED`(② probe 실패) |
| **I-8** | fail-marker 단계 id 불일치(엉뚱한 단계에서 실패) |
| **I-9** | `clean.term = 0`(정상 입력에서 종단 미도달) |
| **I-10** | 선언한 stream 이 아닌 곳에서 마커 관측 |
| **I-11** | kill·clean 관측이 동일 |

★**계상 규율 = 분모 N 에 포함 · `detected` 에 불포함.** INDETERMINATE 를 분모에서 제외하면 *"표본을 깨뜨려 N 을 줄이는"* 경로가 열린다. **corpus 에 INDETERMINATE 가 1건 이상이면 exit 1** 이다.

**⑥ 판별자 형식 (전부 landed 형판 — 신규 스키마 0)**

| 축 | 확정 형식 | 실측 근거 |
|---|---|---|
| **fail-marker** | `::error::[<STAGE-ID>] <msg>` — **stderr** | landed lib py **35** / sh **21** |
| **terminal-marker** | `✓ <gate>: <입력 의존 문면>` — **stdout** | 종단 성공 emit **34/83** |
| **매칭** | **고정문자열 포함(`grep -qF`) — 정규식 금지** | 판정기 자신의 ReDoS·오탐 채널 차단 |
| **다단 분해** | `[<STAGE-ID>]` 대괄호 값 | 단계 id 로 I-8 판정 |
| **INDETERMINATE emit 토큰** | landed **`NOT_RUN`** 재사용 | 신규 값공간 0 |

★**baseline sanity 선행** — mutant 실행 **전에** 원본이 기대 관측을 내는지 확인한다. 원본이 기대 관측을 못 내면 *"대조 무의미"* 로 **FAIL** 한다(대조군 없는 오라클 = hollow).

**⑦ rc 의 지위 (확정 문면 — 양 문서 통일)**

> **rc 는 관측 벡터의 한 좌표이며 단독 판별자로 사용하지 않는다. 판별은 선언 stream 위 마커 문면 + 단계 id 로 한다.**

★ *"rc 는 판별자로 무효"* 는 **과대**다 — rc 가 판별 정보를 전혀 담지 않는 것이 아니라(미존재 root 투입은 rc=1 로 갈린다), **단독으로는** FAIL 축·PASS 축 양방향에서 판별에 실패한다. 실측 2-앵커: ⓐ **FAIL 축** — 12 leg 전건이 프로세스 rc=1 이라 어느 leg 이 FAIL 했는지 rc 로 판별 불가 ⓑ **PASS 축** — index-pin 우회 mutant 가 **정상과 동일하게 rc=0**. **구체 스키마 회부 메뉴에서 `exit code` 를 제거**한다(배제한 선택지를 회부 메뉴에 남기는 자기모순 해소).

**⑧ ★ 자기적용 (필수 — 누락 시 본 계약이 결함 class 의 인스턴스가 된다)**

신설 harness 자신이 신규 hard gate 이므로 **ADR-154 enrollment marker 부착** ∧ **`_has_two_exit_shape` 만족**(`:200`) ∧ **`docs/selftest-execution-liveness-inventory.yaml` 1행 enroll**. enroll 이 곧 §결정 7 cross-seal 편입이며, 그 위 3번째 메타 층은 만들지 않는다.

**⑨ 표본 = 커밋된 산출물 · 실 게이트 파생**

즉석 생성(`mktemp -d` 류) 금지 — 표본이 실행 시점에 생성되면 표본 자체가 검토 대상이 되지 못하고 표본 변경이 리뷰 없이 통과한다. 선례 형판 = `tests/fixtures/codex-review-output/`(커밋된 표본 **7 파일**). 파생은 **실 게이트 사본에서**(ADR-154 §결정 7 `sed-mutation on REAL gate copy`, inline hand-copy = tautology = born-hollow **금지**).

**★왜 더 강하게 쓰지 않았는가 (rationale — 약하게 쓴 이유가 계약의 일부다)**

M-1 은 **저자가 선언한 표본 집합에 대한 kill 판정**만 강제한다. ***"임의 게이트가 hollow 인지 판정한다" 로 쓰지 않는다 — 금지다.*** 후자는 임의 프로그램의 detection sufficiency 일반 판정 = equivalent-mutant = halting 동치이며 **ADR-154 §결정 4 INV-5 정면 위반** + over-claim P0 다. 따라서 M-1 은 **corpus 에 없는 형상의 hollow 는 잡지 못한다** — 이 약함은 결함이 아니라 **천장**이다. ★**다음 저자에게**: 이 문면을 *"약하게 쓴 실수"* 로 읽고 *"모든 hollow 게이트를 검출한다"* 로 강화하지 말 것. **강화 시도가 곧 INV-5 위반이다.**

### 결정 5 — 신규 normative ② **M-2 = 분모 단조 하한** (ADR-154 §결정 7 born-hollow 금지의 corpus 축 leg)

**gap**: census-floor 는 `0` 만 막고 bijection 은 drift 만 막는다 ⇒ **corpus 표본과 그 레코드를 함께 지우면 둘 다 통과**한다. 분모가 조용히 줄어든 게이트는 여전히 green 이며 이것이 ADR-154 §결정 2 의 **silent-green** 정의에 정확히 해당한다.

| ID | 술어 | 왜 필요한가 |
|---|---|---|
| **D-1** | **항목별 census emit** | 총합만 emit 하면 **N 축소와 구별 불가** |
| **D-2** | **`N < baseline` = FAIL** | 동반 삭제 경로를 닫는 유일 술어(비협상) |
| **D-3** | **baseline = 비감소 high-water mark** (아래 별도 상술) | baseline 이 따라 내려가면 D-2 가 공허 |
| **D-4** | 본 게이트에 **`non-applicable` opt-in 미제공** | **면제 칸이 곧 우회로**다 |
| **D-5** | **항목별 `detected` 개별 emit** | 합계만으로는 arm 별 결손이 상계돼 보이지 않는다 |

**★ D-3 상술 — 기전은 차용하되 단조 방향은 반전한다**

**형판 = `docs/infra-resource-baseline.yaml` + `scripts/lib/check_infra_resource_drift.py`.**

- **차용(그대로)** — ⓐ 파일 형식 ⓑ **`content_digest` 결박**(수기 편집 = **exit 3 substrate-failure**, `scripts/check-infra-resource-drift.sh:16-19` 실측) ⓒ **single-writer** 규율 ⓓ **audited-escape**(플래그 + `--reason TEXT` 없이는 거부, 사유가 baseline 파일에 각인) ⓔ **untrusted old baseline ⇒ 미결정 처리**(`write_baseline()` `:936-961` — `corrupt` 이면 `(3, 0, corrupt)`).
- **반전(비교 방향)** — 형판 실배선은 `added = sorted(set(new_pairs) - set(old_pairs))` 가 비지 않으면 **거부**하는 **성장 거부(하향 ratchet)** 다. 본 D-3 은 그 부호를 뒤집어 **`removed = sorted(set(old) - set(new))` 가 비지 않으면 거부** 하며, escape 플래그도 `--allow-baseline-growth` → **`--allow-baseline-shrink --reason TEXT`** 로 반전한다.
- **금지** — corpus baseline 에 대한 **`--write-baseline` 형 자기 하향 재생성 경로**를 두지 않는다(두어야 한다면 D-2 assert **하위**에 게이팅해 D-2 를 우회하지 못하게 한다).

★★**정직 declare — 단조 방향은 신규다(선례 0).** repo 의 baseline 6종(`adr-amendment-threshold` / `infra-resource` / `path-relocation` / `resource-safety-claim` / `wording-dictionary` / `deferred-followup`)은 **전부 shrink 방향**이다. 즉 **비감소 census baseline 의 선례는 repo 에 존재하지 않는다** — 본 D-3 은 landed 형판에서 **기전만** 차용하고 **방향은 새로 세운다**. (`scripts/lib/adr-reservation-atomic-claim.py:168` 의 *"단조 비감소"* 는 **ADR 번호 할당 카운터**라 corpus census 형판이 아니며 선례로 인용하지 않는다.)

> **★ 오인용 경보(형판 답습 함정)** — 초판 설계는 D-3 형판으로 `docs/adr-amendment-threshold-baseline.yaml` 을 인용했으나, 그 파일 헤더는 *"B-1 **단조 비증가**(entry 값 증가·추가 금지, N 하향 재산정 예외)"* 이고 소비자 `scripts/lib/check_adr_amendment_threshold.py` 분기 (iv) 는 `effective < grandfathered_at` 일 때 **baseline 동조 shrink 를 요구**(`--write-baseline` 재실행)한다. **실카운트가 내려가면 baseline 을 따라 내리라고 처방하는 하향 ratchet** 이며 본 D-3 이 원하는 방향의 정확히 반대다. 그 형판을 그대로 재사용하면 D-2 가 영구 공허해진다.

**born-hollow 가드 승계**: 분모 0 → PASS 는 §결정 7 이 금지한 형태의 재현이므로 **`exit 3` fail-closed**(선례 `scripts/check-infra-resource-drift.sh:18` · `scripts/check-path-relocation-consistency.sh:14`). **신규 exit 값공간 0.**

**INV-5 무관**: **표본 건수 계수와 baseline 대소 비교**는 concrete 케이스에서 decidable 하다 — detection sufficiency 판정이 아니다.

### 결정 6 — ★신규 0 명시: 나머지는 전부 ADR-154 기존 조항 재사용 (과대주장 절제)

| 처방 | 처분 | 커버하는 **기존** 조항 |
|---|---|---|
| 표본이 실 게이트에서 파생돼야 함(손저작 금지) | **신규 0** | **§결정 7** `sed-mutation on REAL gate copy` |
| corpus 표본 실행 실패·판독 불가 = 통과 금지 | **신규 0** | **§결정 6** fail-direction(unparseable subject = fail-closed) |
| 도달 판정 probe(unknown-input negative 축) | **신규 0** | **§결정 5** internal-control 3형 중 1 의 직접 instance |
| 신설 게이트 자신의 마커 + 2-exit shape + 인벤토리 enroll | **신규 0** | **§결정 7** self-application(AC-7) + bijection cross-seal |
| corpus 파일 open 경로 제한 · regex bound | **신규 0** | **§결정 6** T-TRAVERSE + CFP-2635/2646 born-safe REUSE |
| day-1 warning-tier · 5-piece chain · required 승격 defer | **신규 0** | **§결정 8** |
| silent-green ≠ silent-fallback ≠ honest-degrade 판정 | **신규 0** | **§결정 2** 3-way taxonomy |

★**과대주장 절제가 본 ADR 의 신뢰성이다.** 위를 "신규" 로 계상하면 §결정 9(재codify 0)를 어기고 *"같은 규칙 두 벌"* 을 생산한다. **본 ADR 의 신규 normative 는 M-1 · M-2 둘뿐이다.**

### 결정 7 — applicability = self-declared opt-in **+ 적격 전제** (ADR-154 §결정 5 `identity_bearing` / A1-7 `mutation_harness` 형판 재사용)

- landed-gate 가 **corpus 대상임을 선언**하면 M-1·M-2 가 대상이 된다. **미선언 = 미대상(정직 no-op).** semantic 추론으로 대상을 확정하지 않는다(비결정·gameable).
- ★**단, D-4 와 충돌하지 않는다** — opt-in 은 *"어떤 게이트가 대상인가"* 를 가르는 **applicability selector** 이고, D-4 가 금지한 것은 *"대상으로 확정된 뒤 개별 항목을 면제하는 칸"* 이다. **대상 선정 축 ⊥ 대상 내 면제 축.**
- ★**opt-in 취소는 D-4 정의역 밖의 분모 축소 경로다** — `true → false` 되돌림은 *대상 이탈* 이라 D-4(대상 내 면제)가 잡지 못한다. ⇒ **opt-in 취소를 D-2 분모 감소 사유로 명시 계상**하고, 그것을 근거로 한 baseline 재산정을 금지한다.
- ★**적격 전제(신설) — 부적격 게이트는 opt-in 할 수 없다.** (a) **단계 scoping 된 fail-marker** 보유 ∧ (b) **입력에 따라 변하는 종단 emit** 보유. 미보유 게이트는 **부적격(정직 no-op)** 이며 선언해도 대상이 되지 않는다. 이 전제는 **3-fixture 예비 실행으로 기계 판독 가능**하므로, 판정 불가능한 게이트가 corpus 에 들어와 born-broken 을 만드는 경로를 사전에 닫는다.
- ★**이 절은 normative 계수에 들어가지 않는다** — §결정 5 자신의 어휘가 가른다(*"applicability = self-declared(opt-in), probe presence = normative"*). 따라서 §결정 6 의 *"신규 normative = M-1 · M-2 둘뿐"* 은 본 절에도 불구하고 유지된다.

**잔여 상속(신규 저작 0)**: *"모든 진짜 landed-gate 가 실제로 self-declare 했는가"*(열거 완결성)는 **기계 강제 불가 — self-declared 의존**이다. ADR-154 §결과의 AC-13 열거-완결성 residual 처분을 그대로 상속한다(honest-ceiling 공개 + review-tier 판정). 새 잔여 문법을 만들지 않는다.

### 결정 8 — sidecar manifest 계약 (신규 durable 스키마 — 형태 판정 (ii) 의 실체)

**파일 = `docs/hollow-gate-corpus-manifest.yaml`.** **신규 스키마 패밀리 0** — `docs/evidence-checks-registry.yaml` 형판을 재사용한다. ADR-151 인벤토리 **8-field 무접촉**(1행 enroll 은 기존 스키마 사용).

**4 블록 · 소비자 disjoint**

| 블록 | 내용 | 소비자 경계 |
|---|---|---|
| `gates[]` | 대상 게이트 id · 마커 계약(fail-marker stage id · terminal-marker) · content hash | **판정기 가시 · arm-invariant** |
| `samples[]` | 표본 경로 · 대상 게이트 foreign key · kill/clean/empty fixture | **arm 어휘 denylist**(`arm-?[hl]|hollow|live`) · **평면 배치**(arm 하위 디렉터리 금지) |
| `build[]` | 표본 파생 절차(원 게이트 · 앵커 · 변형) | **판정기 projection 제외** |
| `classification[]` | 선언 arm · 기대 verdict | **reconciler 전용 · 판정기 미투입** |

**fail-direction**

- `source_sha256` 불일치 → **exit 3(substrate-failure)** · **자동 갱신 금지**(자동 갱신은 drift 를 침묵으로 흡수한다).
- 마커 미관측 → **INDETERMINATE** + corpus **exit 1**.
- **금지키 denylist 9종**(`non_applicable` · `waiver` · `xfail` 등) — 현행 hit **0** 이므로 **ratchet-UP only**(기존 통과분 소급 RED 0).

**bijection · 분모**

- corpus 디렉터리 하위 **전 파일이 정확히 1개 `samples[]` 를 참조**(orphan 0).
- `hollow_corpus: true` 게이트마다 **`declared_arm` L ≥ 1 ∧ H ≥ 1**.
- **`N_gates` · `N_armL` · `N_armH` 개별 emit + 개별 baseline 대조**.
- 전 계수 0 → **exit 3**.

**versioning = 신규 규약 0** — `docs/inter-plugin-contracts/evidence-check-registry-v1.md:197-199` SemVer 룰을 cross-ref 한다. ★**mass-RED 위험 처분은 선례가 이미 보유한다** — 동 파일 `:139` 의 `current_tier` optional → required 전환이 **MINOR** 로 처리된 근거가 *"기존 22 entry retroactive presence 실측 선행(모두 현행 보유 verified — mechanical regression 0건)"* 이다. ⇒ **확정 규칙**:

> **optional → required 전환은 「전 레코드 presence 100% 를 사전 실측·기록한 커밋」에서만 MINOR 다. 실측이 선행하지 않으면 MAJOR 이며, 동일 커밋에서 원자적 backfill 을 동반해야 한다.**

이로써 *"optional + default 2단 ratchet"* 과 *"76 레코드 원자 backfill"* 은 **택일 선택지가 아니라 bump 등급이 가르는 단일 규칙의 두 분기**다.

**inter-plugin MANIFEST 등재 불요**(wrapper-self 산출물).

### 결정 9 — 정직 천장 (본 ADR 자신의 잔여 — 미기재 시 겨냥한 class 재생산)

- ★**커버리지는 부분집합이다 (기준 = 인스턴스).** 본 arc 결함 **20 인스턴스** 중 기계 강제 **가능 = 7**(T1 fail-open 셸 술어 2 · T2 index-pin 정의역 누락 1 · T3 비집행 표면의 fail-closed 운반 1 · T4 열거↔검사 대응 결손[좁힘] 2 · T5 부정 대조 미실행 1), **불가 = 13**(T6 조건부 사실의 무조건 서술 **5** = 의미 축 paraphrase 무한 · T7 문서 검증계약 4요건 미비 **8** = presence-lint 자신이 같은 class). **이 비율을 상향 인용하는 서술을 금지한다.**
  > **계수 기준 정정 기록(무언 폐기 금지)**: 초판 headline 은 *"가능 5 / 불가 6 / 분모 11"* 이었으나 **기준이 혼재**했다 — `가능 5` 는 **유형** 수(T1~T5), `불가 6` 은 **인스턴스** 계상이었고 **분모 11 은 도출이 문서 어디에도 없었다**. 기준을 **인스턴스** 로 통일해 전건 열거·재계수한 결과가 **7/20** 이다. **7/20 = 0.350 < 5/11 = 0.455** 이므로 재계수는 비율을 **하향**한다(즉 구 headline 이 이미 비율을 상향하고 있었다 — 자기 규칙 위반의 자진 정정). 유형 기준(5/7 = 0.714)은 상향이므로 **채택 불가**.
- ★**day-1 강제 대상 = wrapper 자기 게이트 한정**(§결정 3). 본 carrier Story 가 낳은 타 repo 게이트 스크립트는 **이 계약으로 즉시 강제되지 않는다** — 그 repo 는 CI 자체가 부재하며 커버는 별 carrier 다. **재발 채널을 하나 닫았을 뿐 carrier 자신의 산출물은 아직 그 채널 밖**이다.
- ★**arm-L 대조군의 정당성을 판정하는 상위 심급은 없다.** 표본이 잘못 저작되면 게이트는 그것을 알 수 없다. binding stamp 는 **drift 를 막을 뿐 최초 저작 오류를 막지 않는다.**
- ★**day-1 warning-tier = 자기 RED 가 merge 를 막지 못한다**(*governance-tier dark* quasi-pattern). 완화 = 게이트가 **stdout 에 그 사실을 직접 emit** 하고, 승격 trigger 를 **증거 기한**(PR 누적 20 도달 — ADR-171 §결정 6/§결정 10)으로 확정해 무기한 defer 를 막는 것뿐이다. **문서 선언은 읽는 쪽이 없으면 0 이다.**
- ★★**arm-invariant 판정기 계약은 역산 채널을 3개 닫지만 라벨 역산을 해결하지 않는다.** 잔여 3 을 명시한다 — ⓐ `build[]`·`classification[]` projection 배제는 **프로세스 경계 규약**이지 격리 보증이 아니다 ⓑ 표본 **개수·순서 통계**로부터의 추측은 차단되지 않는다 ⓒ **본 계약 단독으로 역산 판정기를 배제할 수 없다**. 완전 배제는 **blinded 섭동**(경로·파일명·arm 배정·stamp 좌표를 고정한 채 알려진 hollowing 변형을 주입해 `LIVE → HOLLOW` 뒤집힘을 전건 요구)을 요구하며 그 설계는 **별 축 소관**이다. 판정기 계약 `classify(sample_artifact, fixtures{kill,clean,empty}, gate_markers)` 는 **3항 전부 arm-invariant** 이므로 blinded 섭동과 **정면 양립**한다.
- ★**opt-in 적격 게이트 모집단 크기가 미측정이다.** 적격 전제(§결정 7)를 충족하는 landed-gate 가 몇 개인지는 재지 않았다(실행 실측은 1 게이트 표본에 한정됐다). ⇒ **day-1 corpus 규모는 이 미측정 수에 상한된다** — 규모를 근거로 커버리지를 인용하지 말 것.
- ★**본 수리가 남긴 미확정 1건**: **corpus 배치 경로 규칙**(작업값 = `tests/fixtures/hollow-gate-corpus/`, 형상 제약 = 게이트별 평면 서브디렉터리 · arm 서브디렉터리 금지). 판별자 스키마와 sidecar manifest 필드·versioning 은 **본 ADR 에서 확정됐다**(§결정 4 ⑥ / §결정 8).
- ★**어휘 금지**: 본 ADR 에 대해 *"universal / 완전 봉인 / class 봉쇄 / 근절"* 류 framing 금지 — ADR-154 §결정 4 + **INV-5 무손상**이며 위반 시 설계리뷰 P0. 본 ADR 이 주장하는 것은 **"기계 강제가 실재하는 부분집합(20 중 7)을 만들었다"** 와 **"day-1 커버리지는 wrapper 자기 게이트 한정"** 뿐이다.

### 결정 10 — 접촉 경계 + carrier 결속

- **ADR-154 / ADR-151 / ADR-152 / ADR-168 무수정 cross-ref** — supersede/rewrite **0**. ADR-154 Amendment 2 는 본 ADR 과 **분할 존치**(§결정 1): A2-2 적용 대상 + A1-3 조건 해제 + 본 ADR 포인터만 보유한다. **ADR-151 인벤토리 8-field 스키마 무접촉**(1행 enroll = 기존 스키마 사용). **ADR-157 무수정**(형판 제공만).
- **강화 방향 유지(약화 surface 0)**: 신규 required context **0** · branch-protection **8-tuple 무변경** · inter-plugin 계약 **무변경** · 신규 category **0**. ★**신규 workflow = 1**(wrapper-self-only · non-required · day-1 hard-fail) — 이를 은폐하지 않는다. required 등재 0 이므로 약화 surface 는 여전히 0.
- **`continue-on-error` 금지** — warning-tier 는 *"required context 아님"* 이지 *"job 이 초록으로 흘러감"* 이 아니다. 도입기 무력화는 게이트를 태어날 때부터 hollow 로 만든다.
- **`on: paths:` 금지 · `runs-on: ubuntu-latest` 리터럴 고정** — 전자는 ADR-130 required check permanent-pending 함정 상속, 후자는 **fork 제출 셸을 실행**하는 게이트이므로 self-hosted 로의 조용한 전환을 구조적으로 막기 위함이다(변수 경유 시 org 변수 1개로 42 workflow 가 전환된다).
- **carrier 결속(계약면 ⊥ 구현면)**: **계약면 = 본 ADR**(Phase 1) ⊥ **구현면 = CFP-2963 Phase 2 산출물**. 구현면 산출물 **9개**(sidecar manifest 1 + corpus fixture 디렉터리 1 + 5-piece chain 5 + `docs/evidence-checks-registry.yaml` warning-tier entry 1행 + `docs/selftest-execution-liveness-inventory.yaml` enroll 1행)는 Change Plan **§5 파일 단위 변경 계획에 개별 행으로 결속**되고 **§8.AC `G1-mech-corpus` 독립 설계 게이트**가 그 분모를 검사한다. 배선 상세 SSOT = internal-docs `wrapper/change-plans/cfp-2963-mclats-arc-ci-runner.md` **§8.QC-MECH**. ADR-154 §결정 8 의 *"Phase 1 = ADR + Change Plan NARRATIVE only"* **무손상**.
- ★**천장 동시-변경 불변식**: 본 ADR **§결정 9** 의 정직 천장과 §8.QC-MECH **MECH-9** 의 정직 천장은 **같은 문면을 양쪽에 보유**한다 — **한쪽에서만 천장을 완화해 인용하는 것을 금지**하며 바꾸려면 **두 문서가 함께** 바뀌어야 한다. 한쪽만 완화하는 것 자체가 본 ADR 이 겨냥하는 class(*선언과 실상태의 조용한 괴리*)의 문서-축 발현이다. (분할 이관으로 normative 본체 중복은 해소됐으므로 이 불변식의 적용 범위는 **천장 문면 + 계수** 로 한정된다.)
- ★**AC 결속의 잔여 — 요구사항 lane 회부 계류**: 신설 harness 의 self-test 는 `tests/scripts/test_check-*.sh`(셸)이고, Change Plan §8.1.1 RTM 머리말이 *"명명 테스트 열에 셸 함수·스크립트 경로를 백틱으로 적지 않는다 — 적으면 파서가 식별자로 오인해 born-missing"* 을 비협상으로 못박는다. ⇒ AC 신설·tier 판정은 **요구사항 lane 소유**이며 설계가 대행하지 않는다. **회부 종결 전까지 본 산출물군은 `ac-traceability-matrix` 정의역 밖**이다(§8.AC 회부 packet SSOT).
- ★**mandate 편차 정직 기재**: 본 계약의 초판은 설계 lane 6 permanent deputy 중 **4 미수령** 상태에서 통합됐고, 그 결과 **회부한 축에서 실제로 P0 가 발생**했다. 본 개정은 APIContractArchitectAgent 수령분(판별자 계약 · sidecar manifest — **실행 재현 기반**)을 반영해 미확정 3건 중 2건을 확정했다. 잔여 축(대조군 blinded 섭동 설계 · arm 별 분모 하한 분해 · corpus 경로 확정 · 운영 리스크 6-sub)은 **후속 deputy 수령분으로 반영**한다.

### 결정 11 — ADR 번호 claim (ADR-133 OCC atomic)

번호 **175** = **ADR-133 claim primitive 반환값**. `scripts/lib/adr-reservation-atomic-claim.py --repo mclayer/plugin-codeforge --state-path adr-reservation-claim-state.json --branch adr-reservation-state --claimant ArchitectAgent:CFP-2963:20260815-012319` → **`175`**, state branch 레코드 `{adr_number: 175, claimant: ArchitectAgent:CFP-2963:20260815-012319, status: claimed}` firsthand 확인(claim 전 `max_adr_number` = 174 → claim 후 175). **max+1 자체 재계산 미사용** — claim 반환 번호를 그대로 채택했다.

**dual-key 3-leg 정합**: filename `ADR-175-landed-gate-corpus-dynamic-hollow-classification.md` ∧ frontmatter `adr_number: 175` ∧ `archive/adr/ADR-RESERVATION.md` row 175. claim(점유 직렬화) ↔ RESERVATION append(영속 기록) **disjoint**(ADR-133 §결정 3 / ADR-070 chief author inline append).

## 결과

### 강화 방향 (ratchet↑, 약화 surface 0)

- 신규 required context **0** · branch-protection **8-tuple 무변경** · inter-plugin 계약 **무변경** · 신규 category **0** · ADR-154/151/152/157/168 **무수정**.
- 신규 workflow **1**(wrapper-self-only · non-required · day-1 hard-fail · `continue-on-error` 금지) — 명시 declare.
- sidecar manifest 금지키 denylist 현행 hit **0** ⇒ **ratchet-UP only**(기존 통과분 소급 RED 0).
- forward-only — landed 산출물 소급 무효화 **0**.

### 경계 (disjoint 축 — 재유입 봉인)

- **⊥ ADR-151**(self-test 채널 alive) — 본 ADR = 게이트 **검출-integrity 의 corpus 실행 축**. 인벤토리 enroll 은 공유하나 스키마는 분리(sidecar).
- **⊥ ADR-171**(승격 등급 축) · **⊥ ADR-130**(배선 제약) · **⊥ ADR-174**(러너 인프라).
- **⊥ L3 detection sufficiency** — INV-5 불가침. 본 ADR 은 그 천장을 **옮기지 않는다**.
- **⊥ 광역 정적 스캔**(ADR-154 §결정 3 기각 유지) · **⊥ cross-repo fetch** · **⊥ 3번째 메타 층**.

### Living Architecture 영향

`docs/architecture/codeforge-family.md` — **boundaries** 축에 wrapper-self CI 게이트 corpus 실행 경계 1건 추가(신규 workflow 1 + corpus fixture 디렉터리). **modules/interfaces/data_flow 무영향**(신규 module 0 · inter-plugin contract 0 · 데이터 흐름 변경 0).

## 해소 기준

N/A — permanent policy (`is_transitional: false`). 단 **§결정 9 의 미확정 1건(corpus 경로 규칙)** 은 후속 deputy 수령 시 본 ADR Amendment 가 아니라 **Change Plan §8.QC-MECH 배선면 확정**으로 착지한다(결정면 ⊥ 배선면 분리 유지).

## 관련 파일

- [ADR-154](ADR-154-hard-gate-self-verification-forcing-function.md) — 상위 렌즈. **무수정 cross-ref**(§결정 2/4/5/6/7/8/9 재사용). Amendment 2 = 적용 대상(A2-2) + A1-3 조건 해제 + 본 ADR 포인터로 축소 존치
- [ADR-151](ADR-151-selftest-execution-liveness-inventory.md) — 인벤토리 1행 enroll(8-field 스키마 무접촉) + §결정 1 신규 ADR prong 3-conjunct(형태 판정 근거)
- [ADR-157](ADR-157-infra-resource-manifest-drift-gate.md) — D-3 형판 제공(기전 차용 · 방향 반전). 무수정
- [ADR-171](ADR-171-evidence-enforceable-promotion-framework.md) — warning → required 승격 evidence-gate(§결정 6 3-AND · §결정 10 증거 기한)
- [ADR-133](ADR-133-adr-reservation-atomic-claim.md) — 번호 claim primitive(§결정 11)
- `docs/hollow-gate-corpus-manifest.yaml` — 본 ADR §결정 8 sidecar manifest (Phase 2 산출)
- `docs/evidence-checks-registry.yaml` — warning-tier entry 1행 (Phase 2 산출)
- `docs/selftest-execution-liveness-inventory.yaml` — 신설 harness self-test 1행 enroll (Phase 2 산출)
- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — versioning 규약 cross-ref(`:197-199` SemVer · `:139` MINOR 선례)
- internal-docs `wrapper/change-plans/cfp-2963-mclats-arc-ci-runner.md` §8.QC-MECH — **배선면 SSOT**(결정면 ⊥ 배선면)
- internal-docs `wrapper/stories/CFP-2963.md` §9.12 — 본 ADR 을 낳은 설계리뷰 verdict(판정 전환 근거)
