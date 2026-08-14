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

이 분할로 *"천장 동시-변경 불변식"* 의 양단은 **본 ADR §결정 9 ↔ §8.QC-MECH MECH-9** 가 된다.

> ★★**정정 — 구 문면의 *"normative 본체 2벌 저작(DR-M8) 동시 해소 · 중복 표 0"* 은 거짓이었다(설계리뷰 DR2-M3 · 문면 철회)**: 분할이 옮긴 것은 **그릇**이고 **2벌 구조는 불변**이다(분할 전 = ADR-154 A2-4/A2-5 ⊕ CP MECH-4/MECH-5 **2벌** / 분할 후 = 본 ADR §결정 4·5 ⊕ CP MECH-4/MECH-5 **2벌**). 실제로 **divergence 1건이 발생**했다 — §결정 4 ④ 가 적격 식을 `diagnostic_line_set` 으로 적어 정본 `observed_line_set` 과 갈렸다(**DR2-M4**, 본 Tranche 정정). ⇒ 거짓 주장을 제거하고 아래 규칙으로 대체한다:
> - **결정면 정본 = 본 ADR 단독.** 계약 문언(verdict 함수 · `I-1`~`I-11` · `D-1`~`D-5` · census 7축 · exit 3 조건 · W · manifest 4블록 · 적격 3-conjunct · hollowing recipe · `IC-1`~`IC-6` · 금지키 denylist)의 원본은 본 ADR 이다.
> - **Change Plan §8.QC-MECH = 배선면 단독** — ID cross-ref + 배선 귀결(파일·경로·형판·실측 앵커·평가 절차)만 적는다.
> - **불일치 시 본 ADR 이 우선**한다. 배선면이 갈리면 배선면을 고친다(역방향 금지).
> - ★**정직 declare**: **중복 채널은 제거되지 않았다.** 위 우선순위 규칙은 drift 를 *막는* 장치가 아니라 drift 발생 시 **해소를 결정 가능하게** 만드는 장치다. *"중복 0"* 이라 쓰지 않는다.

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

landed-gate 의 hollow 여부를 **커밋된 corpus 를 실행해 분류**한다. 구성 10:

**① 2-arm 전건 AND**

| arm | 표본 | 기대 verdict | 없으면 무엇이 통과하는가 |
|---|---|---|---|
| **arm-H** | 어떤 입력에서도 FAIL 하지 않는 게이트 표본 | `HOLLOW` | *"아무것도 잡지 못하는 판정기"* 와 **구별 불가** |
| **arm-L** | 결함 입력에서 FAIL 하고 정상 입력에서 PASS 하는 표본(**대조군**) | `LIVE` | ***"전부 HOLLOW 로 찍는 무조건-true 판정기"*** 가 arm-H 만으로 만점 |

**arm-H 전건 `HOLLOW` ∧ arm-L 전건 `LIVE`** 일 때만 PASS.

★**2-control 과의 관계 — 상속 주장을 정정한다(거짓 상속 제거).** 2-arm 은 ADR-154 §결정 5 의 **positive-control 축**만 instantiate 한다. arm-H·arm-L 은 **둘 다 subject 측 대조군**이므로 *"선언 대상 = 실행 대상"* 을 증명하는 **internal-control 축은 2-arm 만으로는 미인스턴스화**다. internal-control 축은 아래 **② 도달 판정 probe** 가 §결정 5 internal-control 3형 중 *"unknown-input negative"* 의 **직접 instance**(신규 mechanism 0)로 **부분 충당**한다 — **완전 충당이 아니다**(§결정 9 잔여 참조).

**② 도달 판정 = differential delivery probe (마커 주입 0)**

*"게이트 로직이 판정 지점에 도달했는가"* 는 **주입이 아니라 상속으로** 얻는다. sed 파생 표본은 FAIL 분기만 중화되고 **PASS 경로 종단 emit 은 원본에서 그대로 물려받으므로**, arm-H 에 도달 마커를 새로 손저작할 필요가 없다 — ADR-154 §결정 7 *"손저작 금지"* 및 §결정 6 *"신규 0"* 과 **무충돌**이다.

> ★★**`DELIVERED ⟺ observed_line_set(kill-fixture) ≠ observed_line_set(empty-fixture)`** (설계리뷰 DR2-M1 처방 ⓑ — 구 `terminal_line` 판정식 **폐기**)

**empty-fixture (★단일 구성 확정 — DR2-M1 처방 ⓐ)** = **대상 0건 ∧ 게이트의 나머지 필수 입력은 `clean` 과 동일**. 관측 라인 집합이 두 투입에서 **같으면** 게이트는 투입을 실제로 소비하지 않은 것이므로 `¬DELIVERED` → **INDETERMINATE**(아래 I-7).

**②-c ★★ 도달 축 비교 대상 통일 + `empty-fixture` 단일 구성 확정 (설계리뷰 DR2-M1 — 구 문면이 두 구성을 허용했고 그중 하나가 born-RED 였다. 무언 정정 금지)**

> **배치 주의** — ②-c 는 **도달 축**의 확정이라 ② 바로 뒤에 둔다. 아래 **②-b 는 적격 축**의 분리이며, 라벨 순서(b→c)가 아니라 **축 순서(도달 → 적격)** 로 읽는다.

구 정의 *"대상 root 부재가 아니라 대상 0건"* 은 **나머지 필수 입력 축을 미규정**해 두 구성을 허용했다 — **①** 나머지 입력 정상 ∧ 대상 0건 / **②** 나머지 입력 결손 ∧ 대상 0건. `check_hard_gate_self_verification` 실측에서 **② 는 kill 과 종단 라인이 byte 동일**(양쪽 `::error::[SUMMARY] … 위반 1건 (fail-closed, exit1)`, rc 도 양쪽 1)이라 구 식으로 `¬DELIVERED` → I-7 → `INDETERMINATE` 가 되고, **그 게이트가 §결정 9 가 지정한 day-1 arm-L base** 이므로 corpus 가 **day-1 born-RED** 가 된다 `[ArchitectPL firsthand 2026-08-15 — scratchpad 3-fixture, repo 무수정, `python3 scripts/lib/check_hard_gate_self_verification.py --repo-root <fixture>`]`.

| 처방 | 내용 | 성격 |
|---|:-:|---|
| **ⓐ** | `empty-fixture` **단일 구성 확정**(위 정의) — 구성 ② 배제 | 정의 모호 제거. **표본 저자의 준수에 의존**하는 규약 |
| ★**ⓑ** | 도달 축 비교 대상을 `terminal_line` → **`observed_line_set`** 통일 | **판정식 자체** — 구성과 무관하게 성립. 구성 ② 에서도 `{[AC-6],[SUMMARY]}` ↔ `{[AC-8],[SUMMARY]}` 로 갈린다 `[ArchitectPL firsthand]` |

★**ⓐ·ⓑ 는 각각 독립적으로 충분하며 병치는 defense-in-depth 다. 1급은 ⓑ 다** — 규약(ⓐ)을 유일 방어로 두면 표본 저작 오류가 그대로 통과하며, 그것이 본 ADR 이 겨냥하는 *"규약 선언에 의존하는 봉합"* class 다.
★**정직 한정(일반화 금지)** — ⓑ 의 강건성 실증은 **HGSV 1 게이트**에서다. *"`observed_line_set` 이 모든 게이트의 empty ↔ kill 을 가른다"* 로 일반화하지 않는다. 성립 **선결 = 적격 3-conjunct (a)**(단계 scoping 된 fail-marker)이며 (a) 미충족 게이트에서는 성립하지 않는다.
★**비교 *상대* 는 여전히 분리**한다 — 도달 축 = `kill ↔ **empty**` / 적격 축 = `kill ↔ **clean**`. ②-b 가 금지한 것은 `empty` 를 **적격 축**에 쓰는 것이지 관측면 공유가 아니다. **비교 대상(무엇을 보는가) 통일 · 비교 상대(무엇과 대는가) 분리.**

**②-b ★★ 이 식의 용도는 둘로 갈린다 — 하나는 유효하고 하나는 무효다 (10-게이트 회차 실측 반증)**

구 문면은 위 식을 **단일 용도**로 적었고, 그 결과 0-context 구현자가 **적격/판별력 판정에도** 같은 식을 쓰게 된다. **10-게이트 회차 실측이 그 사용을 양방향으로 반증**했다.

| 용도 | 식 | 판정 |
|---|---|---|
| **도달(delivery) 판정** — *"투입이 게이트에 전달됐는가"* | `term(kill) ≠ term(empty)` | ★**유효 — 유지**(§결정 5 internal-control 3형 중 *unknown-input negative* 의 instance) |
| **적격/판별력 판정** — *"게이트가 정상 입력과 결함 입력을 가르는가"* | `term(kill) ≠ term(empty)` | ★★**무효 — 폐기** |

**폐기 근거 (양방향 실측)**

- **위양성** — 10-게이트 회차에서 **9/10 이 이 식을 통과했으나 실제 결함 검출은 2/10** 이었다. `empty` leg 은 **data-absence 경로**를 밟아 문면이 갈릴 뿐이며, 그 갈림은 *"정상 입력 vs 결함 입력"* 의 판별과 **무관**하다. 즉 이 식으로 적격을 재면 **부적격 게이트 7개가 적격으로 계상**된다.
- **위음성** — `check_hard_gate_self_verification` 은 kill 에서 `::error::[AC-8]`(결함) · empty 에서 `::error::[AC-6]`(부재)를 내어 **두 입력을 완전히 판별**한다. 그런데 **두 leg 이 똑같이 `[SUMMARY]` 상수 footer 로 종단**하므로(`scripts/lib/check_hard_gate_self_verification.py:394` `_error("SUMMARY", …)` — `:155` 가 `::error::[{ac_id}]` 로 emit) `terminal_line` 이 **같아져 탈락**한다. ⇒ **가장 모범적인 게이트가 이 식에서 떨어진다.**
  ★**측정 fixture 구성 병기 + 앵커 강도 정정(DR2-M1 처방 ⓒ — 구 `[firsthand]` 단독 표기는 제3자 재현 불가였다)** `[ArchitectPL firsthand 2026-08-15]`: 이 AC-8/AC-6 pair 는 **empty 구성 ②**(위 ②-c 가 배제한 *나머지 필수 입력 결손* 구성 — 구체적으로 concept-doc **부재** ∧ 대상 0건)에서 측정됐다. kill = concept-doc 에서 `presence ≠ truth` 토큰 제거(AC-8 단일 위반) ∧ 대상 0건. **rc 는 양 leg 모두 1**. ★★**본 앵커는 구성 ② 한정이며 ⓐ 가 구성 ② 를 배제한 뒤에는 보조 앵커로 강등된다** — 정본 구성 ① 에서 empty leg 종단은 `✓ … honest-degrade — enrolled=0 …`(rc=0)라 kill 과 **갈리므로** 구 식이 HGSV 를 탈락시키지 않는다. ⇒ **비교 대상 교체(`terminal_line` → `observed_line_set`)의 load-bearing 앵커는 본 항이 아니라 아래 ★ `check_living_architecture_update` 앵커**(census 라인 축 — 구성 무관)이며, **대조 상대 교체(`empty` → `clean`)의 앵커는 위 위양성**(구성 무관)이다. 두 다리는 무손상이고 본 항만 조건부로 강등된다.

**★ 확정 대체 (적격/판별력 축 전용)**

> **적격 판정 = `observed_line_set(kill-fixture) ≠ observed_line_set(clean-fixture)`**

- **대조 상대 교체** — `empty` → **`clean`**. 적격은 *"결함 입력 ↔ 정상 입력"* 의 판별력이지 *"투입 있음 ↔ 투입 없음"* 이 아니다. `empty` 는 **도달 축 전용**으로 남는다.
- **비교 대상 교체** — **마지막 줄 하나(`terminal_line`)가 아니라 관측 라인 집합(`observed_line_set`)**. 상수 종단 footer 를 갖는 게이트가 판별력을 갖고도 탈락하는 위음성 경로를 닫는다.
- ★**`observed_line_set` 의 정의역 = 선언 stream 위 관측 라인 전체** — `::error::[<STAGE-ID>]` **∪** `::notice::` **∪ census 라인**(`scanned-N: …` 형). `::error::` 집합으로 좁히면 안 된다: `check_living_architecture_update` 는 leg 간 `scanned-N: changed=0 structural_surface=0 derived_docs=0` ↔ `changed=2 structural_surface=1 derived_docs=1` 로 **입력 의존 관측을 내지만 그 줄은 종단 라인도 `::error::` 도 아니며**, 좁은 정의역은 이 게이트를 **판별력 보유에도 부적격으로 오분류**한다 `[ArchitectPL firsthand — 동적 2-leg]`.

★**rc 무관 3번째 앵커(⑦ 보강)** — 위 2-leg 관측은 **`::error::` 를 내고도 rc=0** 이다(meta-error leg 포함) `[ArchitectPL firsthand]`. ⑦ 이 든 2-앵커(FAIL 축 12-leg 전건 rc=1 · PASS 축 우회 mutant rc=0)에 이어 **rc 가 단독 판별자가 아님을 보이는 3번째 독립 재현**이며, 이번 앵커는 **`::error::` 관측과 rc 가 서로 어긋나는** 형태라 앞 둘과 다른 방향에서 같은 결론을 지지한다.
- **두 식을 한 문면에서 분리 유지할 의무** — 하나로 뭉쳐 적으면 구현자가 적격 판정에 `empty` leg 을 쓰고, 그 순간 위 위양성 7 이 그대로 재현된다. ★**분리되는 것은 「비교 상대」**(도달 = `empty` / 적격 = `clean`)이며 **「비교 대상」은 ②-c 로 `observed_line_set` 통일**이다. **본 항의 계약 문언 정본 = 본 ADR** 이고 §8.QC-MECH MECH-4 는 이 ID 를 cross-ref 한다(구 *"동일 문면을 양쪽에 보유한다"* 문면은 §결정 1 DR2-M3 처분으로 **철회** — 중복 저작 의무화가 divergence 채널을 재생산했다).

**③ 판정기 계약은 arm-invariant 다 (역산 채널 3개를 닫는다)**

stamp 를 arm 별로 분기하지 **않는다** — 필드 shape 이 arm 을 누설해 역산 채널을 하나 더 열기 때문이다. 마커는 **arm 의 속성이 아니라 대상 게이트의 속성**이므로 **게이트에 keying** 한다. 그 결과 stamp 가 arm-invariant 가 되고 arm 분기는 verdict 함수에서 자동으로 떨어진다.

- ⓐ **파일명·경로 arm 어휘 denylist** — 표본 식별자에 `arm-?[hl]` · `hollow` · `live` 출현 금지. **평면 배치**(arm 별 하위 디렉터리 금지).
- ⓑ **기대 실패 시그니처 필드 제거** — 양 arm 이 **동일 필드집합**을 갖는다. (구 계약이 arm-H 에 요구하던 *"기대 실패 시그니처"* 는 arm-H 에 **정의역 자체가 없었고**, 그 요구가 `arm-H 전건 HOLLOW` 를 도달 불가로 만들어 born-broken 을 낳았다.)
- ⓒ **`declared_arm` projection 배제** — 판정기 프로세스에 arm 선언을 투입하지 않는다.

**④ verdict 함수 (arm 미투입)**

- **`LIVE` ⟺** `kill.fail=1 ∧ fail_stage = kill_target_stage ∧ clean.fail=0 ∧ clean.term=1 ∧ DELIVERED`
- **`HOLLOW` ⟺** `kill.fail=0 ∧ kill.term=1 ∧ clean.fail=0 ∧ clean.term=1 ∧ DELIVERED`
- **그 외 = `INDETERMINATE`**

★**`DELIVERED` 의 정의역 = 도달 축 한정**(②-b). verdict 함수가 소비하는 `DELIVERED` 는 **`observed_line_set(kill) ≠ observed_line_set(empty)`** 로 계산한 **도달 판정**이며, **적격 판정과 같은 좌표가 아니다**. 적격(**`observed_line_set(kill) ≠ observed_line_set(clean)`**)은 **§결정 7 적격 전제**에서 **corpus 진입 전에** 판정되므로 verdict 함수의 입력이 아니다. **두 좌표를 한 변수로 합치면 ②-b 위양성 7 이 verdict 함수 내부로 이전한다.** 두 좌표를 가르는 것은 **비교 상대**(`empty` ↔ `clean`)이지 관측면이 아니다.

> ★**정정 기록(설계리뷰 DR2-M4 — 무언 정정 금지)**: 본 항의 구 문면은 적격 식을 **`diagnostic_line_set(kill) ≠ diagnostic_line_set(clean)`** 으로 적었다. 이는 정본(위 ②-b `observed_line_set`)이 **명시적으로 금지한 좁힘**(*"`::error::` 집합으로 좁히면 안 된다 — `check_living_architecture_update` 를 판별력 보유에도 부적격으로 오분류한다"*) 그 자체였고, 0-context 구현자가 이 식을 채택하면 **적격 하한이 내려가** day-1 born-RED 압력이 커진다. **`diagnostic_line_set` 은 본 ADR 의 값공간에서 폐기**하며 전 site 정본은 `observed_line_set` 이다. 이 divergence 는 §결정 1 이 *"중복 표 0"* 이라 주장했던 그 채널의 **실 발현**이며, 그 거짓 주장도 본 Tranche 에서 함께 철회됐다(DR2-M3).

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
| **fail-marker** | `::error::[<STAGE-ID>] <msg>` — **stderr** | `::error::` 보유 — **명시 분모 기준**: lib py **27**/83 · top-level `scripts/check_*.py` **0**/6 · sh **20**/118 (합 **47**) `[firsthand]`. ★구 표기 *"landed lib py 35 / sh 21"* 은 **넓은 glob**(`scripts/lib/*.py` **147** · `scripts/*.sh` **176**) 기준이라 **다른 모집단**이었다 — 전수 교체 |
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

**⑩ ★★ blinded 섭동 probe — 라벨 역산 판정기 배제 (DR-M1 봉합 · 실행 실증 완료)**

§결정 9 가 *"별 축 소관"* 으로 회부했던 **blinded 섭동**을 본 항이 확정한다. TestContractArch 수령분 · **실행 RED→GREEN 실증 완료**.

**IC-1 좌표 충돌 불변식 (본 장치의 성립 근거)**

> **probe 는 모든 커밋 좌표에서 arm-L 과 일치한다** — 같은 게이트 id · 같은 stamp · 같은 원 표본 · 같은 fixture 3종. **기대 verdict 만 반대**다.

⇒ 출력이 **커밋 좌표만의 함수**인 판정기는 두 입력에 **같은 답을 낼 수밖에 없고, 정의상 한쪽에서 틀린다.** ★**arm-H/arm-L 2-arm 만으로는 성립 불가**다 — 그 둘은 좌표가 갈리므로 좌표 함수 판정기가 둘을 구별해 맞힐 수 있다. **좌표를 고정한 채 기대값만 뒤집는 세 번째 입력**이 있어야 역산이 falsify 된다.

**IC-2 flip assert** — `PRE(arm-L 무변형) = LIVE` → `POST(in-place 섭동) = HOLLOW` **뒤집힘을 전건 요구**한다. 실행 실증 원문:

```
PRE  (arm-L 무변형)   verdict=LIVE   kill: rc=1 stages=['AC-1','SUMMARY']
POST (in-place 섭동)  verdict=HOLLOW kill: rc=0 stages=[] term=1
FLIP: LIVE -> HOLLOW => PASS
라벨 역산 판정기: PRE=LIVE POST=LIVE => 뒤집힘 없음 => RED
```

**falsify 되는 판정기 class 6종 (전건 RED — 실행 기반만 GREEN) · ★H-1 경로 실증 — §결정 9 *hollowing recipe 실증 부분성* 참조. 설계리뷰 DR2-M10 = 무한정 인용 site 전수 병기**

| # | 판정기 class | RED 가 되는 기전 |
|---|---|---|
| **1** | **tautology**(무조건 통과) | flip 미발생 ⇒ IC-2 전건 요구 위반 |
| **2** | **경로·파일명의 함수** | probe·arm-L 경로 동일(IC-1) ⇒ 같은 답 ⇒ 뒤집힘 0 |
| **3** | **stamp 의 함수** | stamp 동일(IC-1) ⇒ 같은 답 ⇒ 뒤집힘 0 |
| **4** | **`manifest.classification[]` 의 함수** | classification 판정기 미투입(③ ⓒ) ∧ 좌표 동일 ⇒ 같은 답 |
| **5** | **전부 `HOLLOW` 로 찍음** | PRE(arm-L 무변형)이 `HOLLOW` ⇒ baseline sanity 위반 |
| **6** | **전부 `LIVE` 로 찍음** | POST 가 `LIVE` ⇒ flip 0 |

**IC-3 posture — recipe 는 커밋, 산출물은 run-time materialize (오해 차단)**

★**⑨ *"즉석 생성 금지"* 와 무충돌**이다. ⑨ 가 금지한 것은 **리뷰 불가 표본**이지 **커밋된 recipe 의 materialize** 가 아니다. probe 의 **섭동 recipe 자체가 커밋되어 리뷰 대상**이며, 산출물만 실행 시 만들어진다 — **ADR-154 §결정 7 `sed-mutation on REAL gate copy` 및 §11.6 복제본 확정과 동형**이다(그 선례도 recipe 는 커밋·mutant 는 런타임 `cp`+`sed`).

> ★**deputy 자기 반증(승계 의무)**: probe 를 **9번째 커밋 표본**으로 두면 평범한 arm-H 와 구별 불가가 되어 **IC-1 좌표 충돌 성질이 소멸**한다. 커밋 표본이 아니라 materialize 인 이유가 이것이며, 이는 취향이 아니라 **장치의 성립 조건**이다.

**IC-4 exec-tree blinding** — exec dir 에 `manifest` · `stamp` · `baseline` · `probe[]` **부재** ∧ exec dir 명 **실행별 재배정** ∧ **전 표본 동일 절차** materialize. (파손 = `exit 3` — §결정 5 exit 3 조건.)

**IC-5 resolved target echo** — 판정기가 **자기가 연 artifact 의 해시를 emit** 하고 `sha(S_L) ≠ sha(P)` ∧ **좌표 일치**를 assert 한다. §결정 5 internal-control 3형 중 **resolved target echo 의 직접 instance** ⇒ **신규 mechanism 0**.

**IC-6 recipe ↔ kill-fixture 1:1 pairing** — landed 선례 시그니처를 답습한다.

> ★★**pairing 의 실 구속 = 「파일 짝짓기」가 아니라 「축 짝짓기」다 (설계리뷰 iter2 최종검수 잔여 처분 — 미명시 시 IC-2 flip 파손)**: **arm-H recipe 가 중화하는 검사 축 ≡ arm-L kill-fixture 가 위반시키는 축**이어야 한다. H-1 은 `_POSITIVE_CONTROL_ANCHORS` 분기 **하나**만 중화하며 그 상수의 소비 지점은 게이트 안에 **1곳**(`scripts/lib/check_hard_gate_self_verification.py:226` — 바로 위 `# MUTATION-SENTINEL M1`)이고 그 분기가 emit 하는 것은 **`::error::[AC-1]`**(`:227`)다 `[ArchitectAgent firsthand 2026-08-15]`. **AC-8 축은 disjoint 경로**(`_CEILING_TOKENS`/`_PRESENCE_TRUTH_TOKENS`/`_detect_overclaim` → `:310`·`:313`·`:317`)라 H-1 이 건드리지 않는다. ⇒ **AC-8 축 kill-fixture 는 arm-L 로서 적법**하지만(`kill {::error::[AC-8],::error::[SUMMARY]}` ↔ `clean {✓ terminal}` ⇒ `LIVE`) **H-1 과 짝지으면 POST 도 `LIVE` 라 flip 이 성립하지 않는다** `[ArchitectPL firsthand — 실행 재현]`. 축 짝짓기를 명시하지 않으면 **pairing 이 형식만 충족되고 flip 은 깨진다** — *"적법한 arm-L kill-fixture 를 골랐는데 probe 가 안 뒤집히는"* born-RED 경로다. **검사 가능성** = §결정 4 ⑤ **baseline sanity 선행**(원본이 기대 단계 id 를 내는지 → 파생 후 그 단계가 사라지는지). 축 불일치면 파생 후에도 같은 단계 id 가 남아 **I-8 또는 flip 실패**로 검출된다. day-1 실배치의 fixture 정체 확정 = Change Plan **MECH-4 ⑫ day-1 최소 구성 확정표**. ★**정확한 landed 시그니처는 `run_mutation_exit <label> <red_builder> <FROM> <TO>` (4항 — recipe 는 `FROM`/`TO` **쌍**)**이며 `run_mutation_stdout` 은 assert token 을 더한 5항이다 `[firsthand — tests/scripts/test_check-hard-gate-self-verification.sh:415 정의 · :443 stdout 변형 · :557-562 호출부]`. *(3항 형 `run_mutation_kill <label> <builder> <desc>` 도 repo 에 있으나(`tests/scripts/test-check-doc-section-8-8.sh:519`) 그것은 **fixture builder 형**이라 실 게이트 사본 sed 축의 형판이 아니다 — 형판은 4항 쪽이다.)*

**★ 신규 mechanism 0 논증 (실측)** — landed `run_mutation_exit` 이 이미 다음을 구현한다 `[firsthand]`: **baseline sanity**(`base_ec != 1` → *"대조 무의미 — fixture 부정확"*) · **실 게이트 사본**(`cp "$GATE_PY" "$mut"`) · **1:1 sed**(`sed_neutralize`) · **미적용 시 `NOT_RUN`**(*"sed 미치환 … false PASS 금지"*) · **double-guard**(`py_valid` 실패 = NOT_RUN) · **flip assert**(`base_ec=1 ∧ mut_ec=0` → KILLED). ⇒ **본 설계가 바꾼 것은 판별 축 하나뿐**이다 — **rc → 마커 문면**(⑦).

**hollowing recipe = landed 재사용 (4종)**

| recipe | 상태 | 처분 |
|---|---|---|
| **H-1** `FROM_M1`/`TO_M1` — `if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):` → `if False:` | ★**실증 완료** | **채택** — FAIL 분기만 중화하고 종단 emit 은 보존 ⇒ `HOLLOW` shape 정합 |
| **H-2~H-4** | **미실증** | liveness 축 후보로 존치. 실증 전 day-1 계상 금지 |

★**`FROM_M4`/`TO_M4` 는 부적합 — 기각 사유 기재**: `FROM_M4` 는 **종단 마커 자체**(`print(f"✓ check-hard-gate-self-verification: enrolled={enrolled} subject scanned …")`)이고 `TO_M4` 가 그것을 `print("neutralized-m4-trace")` 로 치환한다 `[firsthand — :406-412]`. ⇒ **`clean.term = 0` 이 되어 I-9 발동 → `HOLLOW` 가 아니라 `INDETERMINATE`** 를 만든다. hollowing recipe 는 **FAIL 분기를 중화하되 종단 emit 을 보존**해야 하므로 M4 축은 정의상 부적합이다.

**★왜 더 강하게 쓰지 않았는가 (rationale — 약하게 쓴 이유가 계약의 일부다)**

M-1 은 **저자가 선언한 표본 집합에 대한 kill 판정**만 강제한다. ***"임의 게이트가 hollow 인지 판정한다" 로 쓰지 않는다 — 금지다.*** 후자는 임의 프로그램의 detection sufficiency 일반 판정 = equivalent-mutant = halting 동치이며 **ADR-154 §결정 4 INV-5 정면 위반** + over-claim P0 다. 따라서 M-1 은 **corpus 에 없는 형상의 hollow 는 잡지 못한다** — 이 약함은 결함이 아니라 **천장**이다. ★**다음 저자에게**: 이 문면을 *"약하게 쓴 실수"* 로 읽고 *"모든 hollow 게이트를 검출한다"* 로 강화하지 말 것. **강화 시도가 곧 INV-5 위반이다.**

### 결정 5 — 신규 normative ② **M-2 = 분모 단조 하한** (ADR-154 §결정 7 born-hollow 금지의 corpus 축 leg)

**gap**: census-floor 는 `0` 만 막고 bijection 은 drift 만 막는다 ⇒ **corpus 표본과 그 레코드를 함께 지우면 둘 다 통과**한다. 분모가 조용히 줄어든 게이트는 여전히 green 이며 이것이 ADR-154 §결정 2 의 **silent-green** 정의에 정확히 해당한다.

| ID | 술어 | 왜 필요한가 |
|---|---|---|
| **D-1** | **census 7축 개별 emit** | 총합만 emit 하면 **N 축소와 구별 불가** |
| **D-2** | **축별 `N < baseline` = FAIL** — ★**집계 비교 금지** | 동반 삭제 경로를 닫는 유일 술어(비협상) |
| **D-3** | **baseline = 비감소 high-water mark** (아래 별도 상술) | baseline 이 따라 내려가면 D-2 가 공허 |
| **D-4** | 본 게이트에 **`non-applicable` opt-in 미제공** | **면제 칸이 곧 우회로**다 |
| **D-5** | **축별 `detected` 개별 emit** | 합계만으로는 arm 별 결손이 상계돼 보이지 않는다 |

**★ census 7축 확정**: `N_gates` · `N_armL` · `N_armH` · `N_probe` · `N_detected` · `N_flip` · `N_indeterminate` — **전건 개별 emit + 개별 baseline 대조**.

★★**D-2 는 축별 비교이며 *"총합 N"* 단일 대조를 금지한다.** 총 N 이 불변인 채 **arm-H ↔ arm-L 이 상계**되는 경로가 집계 비교에서 열리며, 그 경로를 닫는 것이 본 술어의 실 목적이다.

★**`N_indeterminate` 는 상한 축이다** — 나머지 6축은 *"이보다 작아지면 FAIL"* 인 하한이나 이 축은 **`≥ 1 = exit 1`**(§결정 4 ⑤ 계상 규율 승계).

**★ exit 3 조건 최종형 (6)**: ⓵ `N_gates`·`N_armL`·`N_armH`·`N_probe` 중 하나라도 `== 0` ⓶ baseline 부재·`content_digest` 불일치·parse 실패 ⓷ stamp drift ⓸ bijection 파손 ⓹ ★**exec-tree blinding 파손**(신규 — IC-4) ⓺ recipe 대상이 `samples[]` 밖.

**★ opt-in 취소 계상 (W — 수령 3항. 선언 3 = 열거 3. ★`W-2`·`W-3` 은 *미수령 번호* 이며 결손이 아니다 — 원 packet 번호를 보존한 것이고 그 번호로 명명된 **술어가 정의된 적이 없다**(★*"전역 0 hit"* 로 쓰지 않는다 — 본 문장 자신이 그 토큰을 쓰므로 자기 반증이 된다. 검사 술어는 **「`W-2`/`W-3` 로 명명된 normative 술어 정의행」 0** 이다). 재번호 대신 번호 보존을 택한 이유 = 수령 packet 대조 가능성 유지. 설계리뷰 DR2-M11)**: **W-1** `ever_declared` high-water mark(취소가 **D-2 를 자동 트립**) · **W-4** 취소는 하한을 면제하지 않는다(**두 겹 차단**) · **W-5** `withdrawn[]` **판정기 미투입**(reconciler 전용).

> ★**§결정 7 opt-in ⊥ D-4 문면 정정**: 둘은 disjoint 하다. ★단 ***"disjoint 하므로 안전"* 이라 쓰지 않는다** — disjoint 이기 때문에 **효과 중첩의 틈**(취소를 통한 분모 축소)이 생기고, 그 틈은 **별 술어 W 로 회수**된다. disjoint 는 안전의 근거가 아니라 **별 술어가 필요한 이유**다.

**★ D-4 축 positive-control fixture 의무**: denylist 금지키 현행 hit **0**(§결정 8)이므로 *"0 hit ⇒ 항상 green"* 은 **공허**하다. **denylist 키 1개를 주입한 manifest 에서 RED 실증**이 없으면 D-4 는 선언만 있고 그것을 강제하는 관측이 0 이다.

**★ D-3 상술 — 기전은 차용하되 단조 방향은 반전한다**

**★ baseline 파일 = `docs/hollow-gate-corpus-baseline.yaml` 확정** — **7축 각각의 high-water mark** 보유 · `content_digest` 결박 대상.

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
- ★**적격 전제(신설) — 부적격 게이트는 opt-in 할 수 없다. 3-conjunct.**

  | # | 전제 | 내용 |
  |---|---|---|
  | **(a)** | **단계 scoping 된 fail-marker** 보유 | `::error::[<STAGE-ID>]` — I-8 단계 판정의 성립 조건 |
  | **(b)** | **입력 의존 관측** 보유 | `observed_line_set` 이 kill ↔ clean 에서 갈린다(§결정 4 ②-b — *종단* emit 이 아니라 **관측 라인 집합**) |
  | **(c)** | ★**drivability**(신설) | *"게이트가 자기 정의역을 **명시 인자로** 받아 주입된 트리를 실제로 채점하는가"* |

  미보유 = **부적격(정직 no-op)** 이며 선언해도 대상이 되지 않는다. 판정 불가능한 게이트가 corpus 에 들어와 born-broken 을 만드는 경로를 사전에 닫는다.

- ★★**(c) drivability 가 1급 전제인 이유 — 하네스 자신이 hollow 가 되는 직행 경로다.** 게이트 다수가 repo-root 를 **자기 위치에서 유도**하거나(래퍼의 `cd "$SCRIPT_DIR/.."` — `scripts/check-doc-locations.sh:15` `[firsthand]`) 변경 집합을 **git diff 로 수집**한다(`scripts/check-living-architecture-update.sh:38` `collect_changed_files '.' | python3 … --changed-from-stdin` `[firsthand]`). ⇒ `cd <fixture>` **+ bare 호출** 방식으로 하네스를 짜면 게이트가 **fixture 를 아예 읽지 않고 실 repo(또는 git 컨텍스트)를 채점하고 항상 통과**한다. **1차 census 측정자 자신이 이 함정에 빠져 거짓 0 을 냈다** — 본 arc 거짓-0 의 4번째 재현이다.

- ★**harness 계약(비협상)**: 게이트 정의역은 **명시 인자 주입**(`--repo-root <fixture>` · `--changed-from-stdin` 형)으로만 지정한다. **`cd <fixture>` + bare 호출 금지.** (c) 미충족 = **부적격(정직 no-op)** 이며, 미확인 상태로 corpus 에 넣는 것은 **harness 자기 hollow** 다.

- ★**평가 규약 3항 (신설 — 순서·단위·방법)**

  | 항 | 규약 | 근거 |
  |---|---|---|
  | **ⓐ 평가 순서** | **(c) → (a) → (b)** 순으로만 평가한다 | **(b) 는 (c) 충족을 전제로만 유효**하다 — 잘못 구동하면 산출이 입력 무관해지고 그것이 *"(b) 실패"* 로 오분류된다(실 결함은 (c)). 순서를 뒤집으면 (c) 결함이 (b) 결함으로 계상돼 **적격 모집단이 체계적으로 과소계상**된다 `[ArchitectPL firsthand]` |
  | **ⓑ 적격 단위** | 적격은 게이트 단위가 아니라 **(게이트, invocation surface) 쌍**에 부여된다. harness 는 **core 면**을 명시 인자·CWD 주입으로 구동하며 **래퍼면 기준 판정을 금지**한다 | `check-doc-locations.sh` 는 `cd "$SCRIPT_DIR/.."` 로 repo root 를 강제해 **래퍼면은 구동 불가**이나, core 는 `Path("docs/doc-locations.yaml")` = **CWD 상대**(`scripts/lib/check_doc_locations.py:33`)라 **구동 가능**하다 `[firsthand]`. 래퍼면 기준 판정은 (c) 를 체계적으로 과소계상한다 |
  | **ⓒ 판정 방법** | 판정은 **동적 2-leg 실행으로만** 확정한다. **정적 grep 은 후보 선별까지만**이며 확정 근거로 쓰지 않는다 | (a)·(b) 는 **정적 판정 불가**다 — 단계 id 가 f-string 변수 안에 들어가면 형식문자열 grep 이 놓친다(`check_doc_locations.py` 는 `errors.append(f"[1/7] …")` 후 `::error::{e}` 로 emit — `:71,78`; 이 파일이 정적 grep 에 잡힌 것은 **무관한 `:228` `::error::[7/7]` 리터럴 덕분인 우연**이라 파일 단위 hit 조차 신뢰할 수 없다) `[firsthand]` |

- ★**(c) 의 기계 판독** — 3-fixture 예비 실행 **+ 정의역 주입 확인**: *"주입 트리에서만 나올 수 있는 관측이 실제로 나오는가"*. 예 = `check_doc_locations` core 가 주입 yaml 에 대해 `OK [5/7] no absolute paths` · `OK [6/7] doc_type name uniqueness` 를 내는 것 `[ArchitectPL firsthand]`. 이 확인 없이는 *"통과"* 가 **채점 대상이 실 repo 였다**는 사실과 구별되지 않는다.
- ★**이 절은 normative 계수에 들어가지 않는다** — §결정 5 자신의 어휘가 가른다(*"applicability = self-declared(opt-in), probe presence = normative"*). 따라서 §결정 6 의 *"신규 normative = M-1 · M-2 둘뿐"* 은 본 절에도 불구하고 유지된다.

- ★★**day-1 corpus 정의역 = 적격 실증분 한정 (U-1 처분 ⓐ — 확정)**. 부적격 base 를 편입하면 `INDETERMINATE` 가 쌓여 `≥1 = exit 1` 로 **corpus born-RED** 가 된다. ⇒ ⓐ **적격 실증분만 day-1 편입** ⓑ 미편입분은 **`"day-1 미편입 — base 적격화 후 편입(이월)"`** 을 사유와 함께 **명시**(삭제·은폐 금지 — 파생 설계는 보존하고 편입 시점만 이월). ★**arm 축에 따라 처분 어휘를 갈라 쓰지 않는다**(arm-H base 는 *이월* · arm-L 후보는 *기각* 으로 갈렸던 구 문면은 DR2-M2 ⓔ 로 통일 — 두 집합의 부적격 사유가 동일하고 일부는 **같은 파일**이다) ⓒ ★**`N_gates ≥ 2` 형 상수 하한을 day-1 에 걸지 않는다**(실증 base 가 1 이면 그 자체로 born-RED) — baseline 은 **실착지 값에서 출발하는 forward-only ratchet**(§결정 5 D-3) ⓓ ★**day-1 실배치 좌표는 배선면이 확정한다** — **day-1 최소 구성 확정표**(arm-L 1 · arm-H 1 · probe 1 의 게이트·디렉터리·파생) SSOT = Change Plan **MECH-4 ⑫**. `[TBD Phase 2]` 는 `N_*` **값**에만 붙고 **구성 자체는 확정**이며, 그 확정 구성이 **4 축 전건 하한 1 을 보장**해 born-RED 를 닫는다(DR2-M2 ⓓ).
  - **소급 부여안 기각 근거**: *"부적격 base 에 마커 계약을 소급 부여한다"* 는 **A안으로 이미 기각된 retrofit 과 동일 종류**(가동 중 production 게이트의 출력 형식 변경)다. **같은 ADR 안에서 같은 처방을 한쪽은 기각·한쪽은 채택하면 일관성이 파손**되고 §결정 2 **forward-only ratchet** 과도 모순이다.
  - ★**프레이밍 동반 의무**: *"day-1 corpus 가 작다"* 는 **결함이 아니라 ratchet 의 출발점**이며 **신규·개정 게이트가 3-conjunct 를 충족하며 착지할 때마다 단조 증가**한다. **둘 중 하나만 쓰면 각각 과대·과소**이므로 병기한다. 정의 site = Change Plan **MECH-4 ⑫**(중복 저작 회피 — 나머지는 cross-ref).

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
  > **계수 기준 정정 기록(무언 폐기 금지)**: 초판 headline 은 *"가능 5 / 불가 6 / 분모 11"* 이었으나 **기준이 혼재**했다 — `가능 5` 는 **유형** 수(T1~T5), `불가 6` 은 **인스턴스** 계상이었고 **분모 11 은 도출이 문서 어디에도 없었다**. 기준을 **인스턴스** 로 통일해 전건 열거·재계수한 결과가 **7/20** 이다. **7/20 = 0.350 < 5/11 = 0.455** 이므로 재계수는 비율을 **하향**한다(즉 구 headline 이 이미 비율을 상향하고 있었다 — 자기 규칙 위반의 자진 정정). 유형 기준(5/7 = 0.714)은 상향이므로 **채택 불가**. ★**분모 20 자체가 술어 의존이다(DR2-M12 · U-5 자기 적용)** — T7 열거의 `C-2/R2-1` 을 **동일 결함의 2-원장 식별자로 보아 1 계상**한 값이 20 이며, **2 로 세면 T7 9 → 불가 14 → 분모 21 → 7/21** 이다. 본 ADR 은 **1 계상 술어**를 채택하고 그 술어를 명기한다 — 술어 없는 분모는 재현 불가다.
- ★**day-1 강제 대상 = wrapper 자기 게이트 한정**(§결정 3). 본 carrier Story 가 낳은 타 repo 게이트 스크립트는 **이 계약으로 즉시 강제되지 않는다** — 그 repo 는 CI 자체가 부재하며 커버는 별 carrier 다. **재발 채널을 하나 닫았을 뿐 carrier 자신의 산출물은 아직 그 채널 밖**이다.
- ★**arm-L 대조군의 정당성을 판정하는 상위 심급은 없다.** 표본이 잘못 저작되면 게이트는 그것을 알 수 없다. binding stamp 는 **drift 를 막을 뿐 최초 저작 오류를 막지 않는다.**

- ★★**day-1 arm-L 은 메타-게이트에서 파생되므로 인식론적으로 결합돼 있다 (논리적 무순환이 이것을 상쇄하지 않는다). ★단 이 결합은 「불가피」가 아니라 「day-1 선택의 귀결」이다 — 설계리뷰 DR2-M7 정정.**

  **구 문면의 전제가 거짓이었다(무언 정정 금지)**: 구 문면은 *"arm-L base 후보 3 이 전건 부적격이라 arm-L 은 **적격 실증 2**(HGSV · SEL)에서 취해진다 ⇒ **유일 원천**이 cross-seal 두 층"* 이라 적어 결합을 **불가피한 천장**으로 기술했다. 그러나 **같은 §결정 9 가 아래에서 동적 재판정으로 `check_living_architecture_update` · `check_doc_locations` 를 적격으로 뒤집고 *"적격은 하한 4"* 를 확정**하며, **그 2 는 cross-seal 메타-게이트가 아니다**. ⇒ *"유일 원천"* 은 **본 ADR 자신에 의해 반증**된다. **표기 확정 = 전 site *"적격 실증 2"* → *"적격 base 하한 4 중 arm-L 채택 1(day-1)"***.

  | 결합 | 내용 | 귀결 | ★회피 가능성 |
  |---|---|---|---|
  | **ⓐ 공통-모드** | day-1 arm-L 이 cross-seal 층 B 게이트(HGSV)에서 파생 | 그 게이트가 hollow 화되면 **봉인과 대조군이 동시에 열화**하고 corpus 는 RED 를 내되 *"표본 오저작 ↔ 원 게이트 hollow 화 ↔ recipe drift"* **3자를 미분별** | ★**회피 가능** — arm-L 을 적격 base 중 **비-메타게이트**(CLAU · CDL)로 이전하면 **소멸** |
  | **ⓑ 변경 증폭** | 그 게이트를 **정당하게** 편집할 때마다 stamp 불일치 → `exit 3` → 같은 PR 에서 corpus 재파생 강제 | 하필 **거버넌스 Story 가 가장 자주 건드리는 파일**이라 마찰이 상시화 | ★**부분 회피** — arm-L 이전으로 arm-L 축은 소멸하나 **arm-H day-1 파생(H-1)이 같은 파일 계열에 결박**돼 arm-H 축 마찰은 잔존(H-2~H-4 미실증이라 대체 recipe 부재) |

  > **천장 문면(정정판)**: **day-1 arm-L 은 메타-게이트에서 파생되므로 그 게이트에 대한 독립 상위 심급이 아니다** — corpus 의 arm-L 관측은 **동결 사본의 합성 fixture 위 거동**에 관한 것이지 **CI 상 live 거동의 증거가 아니다.** ★**「불가피」로 인용 금지**(회피 경로가 실재한다) ∧ ★**「이미 소멸」로 인용 금지**(day-1 에는 실재한다). **천장을 상향 인용하는 것도 하향 인용하는 것도 같은 규율 위반이다.**

  **day-1 에 유지하는 사유(명시 의무 — DR2-M7 ⓑ)**: 비-메타게이트 2 는 **적격 판정만 있고 corpus 표본이 저작되지 않았다**(kill/clean/empty fixture 형상 · terminal-marker 문면 · 파생 recipe 미확정). 거기서 day-1 arm-L 을 취하면 **DR2-M2 가 지적한 「미지정 born-RED」를 다른 게이트에서 재생산**한다. HGSV 는 그 좌표가 **전건 firsthand 실측**돼 있다. **이전 선결 = ⓘ fixture 3종 형상 확정 ⓙ 무변형 사본 2-leg baseline sanity 실측**이며 Phase 2 harness 착지 후 저비용으로 충족된다 `[empirical-source: TBD — Phase 2]`.

  완화(해소 아님) = **reconciler 3-way 진단 의무**(위 3자 분별 보고) · **판정기 미투입**(`classification[]` 규약 동형).
- ★**day-1 warning-tier = 자기 RED 가 merge 를 막지 못한다**(*governance-tier dark* quasi-pattern). 완화 = 게이트가 **stdout 에 그 사실을 직접 emit** 하고, 승격 trigger 를 **증거 기한**(PR 누적 20 도달 — ADR-171 §결정 6/§결정 10)으로 확정해 무기한 defer 를 막는 것뿐이다. **문서 선언은 읽는 쪽이 없으면 0 이다.**
- ★★**arm-invariant 판정기 계약은 역산 채널을 3개 닫지만 라벨 역산을 해결하지 않는다.** 잔여 3 을 명시한다 — ⓐ `build[]`·`classification[]` projection 배제는 **프로세스 경계 규약**이지 격리 보증이 아니다 ⓑ 표본 **개수·순서 통계**로부터의 추측은 차단되지 않는다 ⓒ **본 계약 단독으로 역산 판정기를 배제할 수 없다**. **좌표 역산 축의 배제**는 **blinded 섭동**(경로·파일명·arm 배정·stamp 좌표를 고정한 채 알려진 hollowing 변형을 주입해 `LIVE → HOLLOW` 뒤집힘을 전건 요구)을 요구한다(★구 *"완전 배제"* 표기 폐기 — **무실행 축(HC-1)은 그 장치로도 닫히지 않는다**, 설계리뷰 DR2-M9). 판정기 계약 `classify(sample_artifact, fixtures{kill,clean,empty}, gate_markers)` 는 **3항 전부 arm-invariant** 이므로 blinded 섭동과 **정면 양립**한다.
  > ★**갱신(회부 해제)**: blinded 섭동은 **§결정 4 ⑩ 으로 착지**했고 **판정기 class 6종을 실행으로 falsify** 했다 **(★H-1 경로 실증 — 아래 *hollowing recipe 실증 부분성* 참조)**. ⇒ **구 잔여 3 중 ⓒ 는 좌표 역산 축에서 해소**되고, **남는 것은 아래 HC-1·HC-2 두 축**이다. ★**ⓑ 의 닫힘 범위는 「결정론적 함수」까지다(축 분해 — 과대·과소 양방 회피)**: blinded 섭동은 **출력이 개수·서수의 결정론적 함수**인 판정기를 falsify 한다(좌표가 같으므로 PRE=POST 답 ⇒ 뒤집힘 0 ⇒ RED). **그러나 HC-2 가 말하는 잔여는 그것이 아니라 「통계적 추측」**이다 — 표본 분포를 알고 확률적으로 arm 을 찍는 판정기는 flip 을 통과할 수 있다. ⇒ **ⓑ 결정론 축 = 닫힘 / ⓑ 통계 축 = HC-2 로 존치.** 구 문면의 *"ⓐⓑ 잔여를 실제로 닫는다"* 는 **결정론 축 한정**으로 읽어야 하며, 그 한정 없이 인용하면 HC-2 와 정면 충돌한다.

- ★**blinded 섭동 착지 후 잔여 `HC-N` (수령 2항 — 선언 2 = 열거 2. 미수령 번호를 채워 넣지 않는다)**

  > ★**네임스페이스 규약 — `HC-` = Honest Ceiling**: 배선면 Change Plan 에 **선재 `C-N` 식별자 2종**(§3.9 `C-3` · 요구사항리뷰 finding `C-2/R2-1`)이 있어 `C-N` 은 동음이의를 낳는다(같은 class 의 앞선 처분 = `INV-5` 한정 표기 · 숫자 `139` 단위 라벨 — **본 건이 4번째**). 개명 선례 = **D-6 네임스페이스 규약**(구 `I-N` → `ID-N`). **선재 식별자는 무접촉** — 개명 대상은 본 ADR 이 신설한 천장 축뿐이다. **양문서 동일 명칭 보유**(천장 동시-변경 불변식).
  - **HC-1 정적 패턴 판정기** — probe 는 *"출력이 **실행물의 함수**"* 임만 강제하고 ***"실제로 실행했다"* 는 강제하지 못한다.** 표본을 실행하지 않고 그 **내용을 정적으로 읽어** 같은 답을 내는 판정기는 IC-2 flip 을 통과할 수 있다(hollowing 변형이 파일 내용에 남으므로). ⇒ 본 장치가 배제하는 것은 **좌표 역산**이지 **내용 정적 분석**이 아니다.
  - **HC-2 개수·순서 통계** — 표본 개수·서수 배열로부터의 추측은 여전히 차단되지 않는다. ★**day-1 소규모 구간에서 이 잔여가 가장 크다** — 표본이 적을수록 통계 추측의 탐색 공간이 작기 때문이며, 이는 **day-1 corpus 가 작다는 사실과 직접 연동**된다(§결정 7 day-1 정의역). corpus 가 단조 증가하면 이 잔여는 **감소 방향**으로 움직인다.

- ★**hollowing recipe 실증 부분성** — 채택 recipe 4 중 **실행 실증은 H-1 뿐**이며 **H-2~H-4(liveness 축)는 미실증**이다. 따라서 *"probe 가 판정기 class 6종을 falsify 한다"* 는 **H-1 경로에서 실증된 것**이고, 나머지 3 경로는 **설계상 동형이라는 기대**이지 실증이 아니다. `[empirical-source: TBD — Phase 2]`

- ★**day-1 `N_probe` 미확정** — probe 표본 수가 확정되지 않아 **§결정 5 D-2 의 `N_probe` 축 baseline 출발값이 미정**이다. 따라서 그 축의 비감소 ratchet 은 **착지 시점에야 기준선을 얻는다**. `[empirical-source: TBD — Phase 2]`
- ★★**day-1 적격 모집단은 「미확정」이다 — 1차 census 는 방법 결함으로 폐기됐고, 그 수치를 인용하는 것을 금지한다.**

  1차 census 는 **정적 grep + 래퍼면 구동**으로 산출됐고 **두 방향으로 틀렸다**: ⓐ **(c) 미충족을 (b) 실패로 오분류**한다(잘못 구동하면 산출이 입력 무관해지고 그것이 *"(b) 없음"* 으로 보인다 — 실 결함은 (c)) ⓑ **f-string 변수 안 단계 id 를 놓친다**(형식문자열 grep 의 정의상 한계). ⇒ **동적 2-leg 재판정이 2 게이트를 적격으로 뒤집었다** `[ArchitectPL firsthand]`:

  | 게이트 | 1차 census | 동적 재판정 | 뒤집힌 근거 |
  |---|---|---|---|
  | `check_living_architecture_update` | 부적격(*"(b) 성공 문면 상수"*) | ★**적격** | leg 간 `scanned-N: changed=0 structural_surface=0 derived_docs=0` ↔ `changed=2 structural_surface=1 derived_docs=1` — **종단 라인도 `::error::` 도 아닌 census 라인**이 입력 의존 |
  | `check_doc_locations` | 부적격(*"(b) 성공 문면 상수"*) | ★**적격** | 주입 yaml 에서만 나오는 `OK [5/7] no absolute paths` · `OK [6/7] doc_type name uniqueness` ⇒ (b) ∧ (c) 동시 충족. 그 `[5/7]` 이 **정적 grep 미검출 (a) 의 실증**이기도 하다 |

  ⇒ **적격은 「하한 4」이며 확정치가 아니다.** 정확한 census 는 **`(c)→(a)→(b)` 순 동적 3-conjunct 평가**(§결정 7 평가 규약 ⓐ~ⓒ)로만 산출된다. ★**본 천장에 적격/분모 비율을 기재하지 않는다** — 방법이 확정되기 전의 비율은 그 자체가 본 ADR 이 겨냥하는 class(*선언과 실상태의 조용한 괴리*)의 발현이다.

- ★**모집단 분모 자체가 술어 의존이다(단일 확정치 인용 금지).** *"`check_*.py` 83 + `check-*.sh` 118"* 형 단순 합은 **틀렸다** — sh 다수가 lib py 코어로 위임하는 **thin wrapper** 라 구현 단위가 중복 계상된다. 중복제거 분모 = **lib py 83 + top-level `scripts/check_*.py` 6 + 독립 shell N** 이며, **N 은 thin-wrapper 판별 술어에 민감**하다 `[firsthand — 술어 4종 실측]`:

  | thin-wrapper 판별 술어 | thin | 독립 sh | 분모 |
  |---|---|---|---|
  | 비주석 줄에 임의 `.py` 호출 | 86 | 32 | **121** |
  | 비주석 줄에 `check_[a-z_]*\.py` 참조 | 72 | 46 | **135** |
  | 5-piece chain 1:1 미러(`check-X.sh` ↔ `check_X.py`) | 68 | 50 | **139** |
  | `exec python3` ∨ `python3 …scripts/lib/` | 62 | 56 | **145** |

  ⇒ **분모 band = 121~145.** 술어를 명기하지 않은 분모는 **재현 불가**이며, 그런 분모 위에 세운 비율은 인용하지 않는다.

  ★★**U-5 — 측정자 3인이 갈렸다(단일 수치 금지의 실증)**: 같은 모집단에 대해 **`134` / `121~145` / `207`** 세 값이 나왔다. ⇒ **어떤 단일 수치도 쓰지 않는다.** 문서는 **정의역 술어 + 그 술어로 산출한 값**만 적고, ***"술어가 다르면 값이 다르다"* 는 사실 자체를 기재**한다. ★***"약 N개"* 류 완곡 표현도 금지** — 완곡은 술어를 숨겨 재현 불가를 은폐한다.

  ★**단위 라벨 — 숫자 `139` 동음이의 주의**: 위 표의 값은 전부 **게이트 구현 단위 모집단**이다. 그중 **139** 는 **§8.QC 검증계약 동결 분모 `151/139/12` 의 139 와 숫자만 같을 뿐 정의역이 다르다** — 전자는 게이트 구현 단위 수, 후자는 검증계약 항목 충족 수다. **일치는 우연이며 §8.QC 분모는 본 Tranche 에서 무접촉**이다.
- ★**TestContractArch 축 = 수령·확정 완료(회부 해제)** — **blinded 섭동**(§결정 4 ⑩ IC-1~IC-6, 실행 실증) · **arm 별 분모 하한 분해**(§결정 5 census 7축 + 축별 D-2 + exit 3 조건 6) · **arm-L 표본 타당성**(구 후보 3 day-1 미편입·이월 → **적격 base 하한 4 중 arm-L 채택 1(day-1)** + 인식론적 결합 천장 — ★**회피 가능**으로 정정, DR2-M7). ★**확정 후 남는 잔여 = HC-1·HC-2 + U-2~U-5 TBD**(위). 판별자 스키마와 sidecar manifest 필드·versioning 은 **본 ADR 에서 확정**됐고(§결정 4 ⑥ / §결정 8), **corpus 배치 경로·형상**(확정 = `tests/fixtures/hollow-gate-corpus/`, 형상 = **표본별 opaque 서수 단일 tier** · arm 어휘·결함유형 접미 **양쪽 미채택** · arm tier 금지) 및 **운영 리스크 6-sub·§11.6 멱등**은 **배선면 Change Plan §8.QC-MECH 에서 확정**됐다(결정면 ⊥ 배선면 분리 유지 — §해소 기준). ★**회부 축의 종결은 위 천장 항목들의 해소가 아니다** — 커버리지 7/20 · day-1 wrapper 한정 · arm-L 상위심급 부재 **및 인식론적 결합 2** · warning-tier dark · **역산 잔여 HC-1·HC-2** · 적격 모집단 미확정(1차 census 폐기)은 **전건 존치**한다.
  > ★**형상 제약 문면 정정(구 "게이트별 평면 서브디렉터리")**: 한 게이트에서 표본이 여럿 파생되므로(실측 — `check_confirmation_record_schema_resume.py` 하나에서 3) 게이트 keying 은 디렉터리 **안에서** 표본을 다시 명명하게 만들어 ⓐ 가 닫은 명명 채널을 재개방한다. ⇒ **표본별 단일 tier** 로 정정한다. *"평면(arm tier 금지)"* 제약은 **무손상**이다. 또한 표본 식별자에서 **결함유형 접미도 배제**한다 — T1~T5 유형명이 전부 hollow-측 어휘라 denylist 리터럴을 피해도 동일한 arm 추론 채널이 복원되기 때문이며, ⓐ 의 목적은 토큰 제거가 아니라 **arm 추론 차단**이다.
- ★★**선-계측 배선 = A안 확정(retrofit 미채택 · 별 carrier 회부).** 선-계측(flat-error 게이트 **단계 id 부여** + 성공 문면 상수 게이트 **입력 의존 값 주입**)은 **본 Story 미채택**이다. 근거는 **커버리지 수치에 의존하지 않는다**(수치가 실제로 흔들렸다 — U-5):
  - **실패 모드 정합(결정적)** — 본 arc 지배 class 인스턴스가 **전부 이 Story 가 신설한 게이트·산출물에서 발현**했다(T1 GATE ①② fail-open · T2 index-pin · T3 주석 sentinel · T4 default-deny 무검사 · T5 AC-15 선언-미이행 · T6 조건부-무조건 서술). ★**기존 landed 모집단 발현이 아니다** ⇒ **§결정 2 forward-only ratchet 이 실제 발현 지점을 정확히 덮는다.** 낮은 day-1 적격 수는 **커버리지 실패가 아니라 모집단 오정의**였다. *(★ 인스턴스 계수는 T4 계상 술어에 따라 11↔12 로 갈리므로 **단일 수치로 인용하지 않는다** — 근거는 수치가 아니라 **"발현 지점이 전부 신설분"** 이라는 정성 명제가 진다.)*
  - **자기모순 회피** — 본 ADR 이 **같은 Story 안에서** *"적용 = 신규·개정 landed-gate, 소급 재분류 0"* 을 codify 했다. retrofit 채택은 그 결정과 **자기모순**이다.
  - **비용·위험** — 대상이 전부 **가동 중 production 게이트(required 포함)**. 출력 형식 변경은 downstream(workflow grep · self-test assertion · required context)을 깨뜨리며, **"대규모 동시 변경 + 검출력 미실증"** 은 본 arc 가 반복 격퇴한 class 의 신규 표면이다.
  - **최소 seeding 도 미채택** — 실효 +1~2 를 위해 production 게이트를 건드리는 것은 **발견 ≠ 필요**(ADR-119 §결정 9 3문 게이트) 미충족.
  - ★**별 carrier = 무기한 defer 아님**: **후보 범위** = **(a) 축만 미달** 코호트(`::error::` 보유 ∧ 단계 id 없음 — ★크기는 **동적 재판정 후에만 확정**, 단일 확정치 금지) / **착수 조건** = ⓐ 본 harness 착지로 **동적 3-conjunct 판정기가 실재**할 것 ∧ ⓑ 게이트당 **downstream 영향 실측** 선행 / **금지** = **일괄 배치 변경**(게이트 단위 점진 · 각 건이 자기 self-test 로 RED→GREEN 실증).

- ★**어휘 금지**: 본 ADR 에 대해 *"universal / 완전 봉인 / class 봉쇄 / 근절"* 류 framing 금지 — ADR-154 §결정 4 + **INV-5 무손상**이며 위반 시 설계리뷰 P0. 본 ADR 이 주장하는 것은 **"기계 강제가 실재하는 부분집합(20 중 7)을 만들었다"** 와 **"day-1 커버리지는 wrapper 자기 게이트 한정"** 뿐이다.

### 결정 10 — 접촉 경계 + carrier 결속

- **ADR-154 / ADR-151 / ADR-152 / ADR-168 무수정 cross-ref** — supersede/rewrite **0**. ADR-154 Amendment 2 는 본 ADR 과 **분할 존치**(§결정 1): A2-2 적용 대상 + A1-3 조건 해제 + 본 ADR 포인터만 보유한다. **ADR-151 인벤토리 8-field 스키마 무접촉**(1행 enroll = 기존 스키마 사용). **ADR-157 무수정**(형판 제공만).
- **강화 방향 유지(약화 surface 0)**: 신규 required context **0** · branch-protection **8-tuple 무변경** · inter-plugin 계약 **무변경** · 신규 category **0**. ★**신규 workflow = 1**(wrapper-self-only · non-required · day-1 hard-fail) — 이를 은폐하지 않는다. required 등재 0 이므로 약화 surface 는 여전히 0.
- **`continue-on-error` 금지** — warning-tier 는 *"required context 아님"* 이지 *"job 이 초록으로 흘러감"* 이 아니다. 도입기 무력화는 게이트를 태어날 때부터 hollow 로 만든다.
- **`on: paths:` 금지 · `runs-on: ubuntu-latest` 리터럴 고정** — 전자는 ADR-130 required check permanent-pending 함정 상속. ★**후자의 근거는 정정됐다(InfraOp firsthand 반증)**: 구 문면은 리터럴이 *"fork 제출 셸의 호스트 실행을 구조적으로 막는다"* 고 적었으나 **거짓**이다. `pull_request` 이벤트는 workflow·코드를 **PR merge commit 에서** 취하므로(base default branch 기준은 `pull_request_target` 뿐 [source: docs.github.com — "Securely using pull_request_target"]) **fork PR 은 자기 PR 안에서 그 리터럴을 편집할 수 있다 — 리터럴은 fork 를 구속하지 못한다.** 실 격리는 다른 층이 만든다: **L1** fork PR **secrets 미전달** + `GITHUB_TOKEN` read-only [source: docs.github.com — "Managing GitHub Actions settings"] · **L2** public repo 는 `CI_RUNS_ON_LINUX_JSON` 미설정 → coalesce `["ubuntu-latest"]`(ADR-147 §결정 2) · **L3** runner group **2개 전건** `allows_public_repositories=false` ⇒ GitHub 이 거부 · **L4** first-time contributor 실행 승인 · **L5 = 리터럴 고정(최약 보조층)**. ⇒ **리터럴은 유지하되 근거를 L5 로 정정**하며, *"이것이 fork 실행을 막는다"* 는 서술을 **금지**한다. 부수: 리터럴은 repo 관행(`vars.` 형 **42 workflow**)에서의 **이탈**이므로 workflow 에 **주석 1행 declare** 의무(미declare 시 장래 일괄 정규화가 되돌린다). 선례 = 리터럴 job **110**(`css-lint.yml` `css-lint-test` · `hard-gate-self-verification-test.yml` · `selftest-execution-liveness-test.yml`) `[firsthand]`.
- **carrier 결속(계약면 ⊥ 구현면)**: **계약면 = 본 ADR**(Phase 1) ⊥ **구현면 = CFP-2963 Phase 2 산출물**. 구현면 산출물 **10개**(sidecar manifest 1 + corpus fixture 디렉터리 1 + 5-piece chain 5 + `docs/evidence-checks-registry.yaml` warning-tier entry 1행 + `docs/selftest-execution-liveness-inventory.yaml` enroll 1행 + **`docs/hollow-gate-corpus-baseline.yaml` census baseline 1**)는 Change Plan **§5 파일 단위 변경 계획에 개별 행으로 결속**되고 **§8.AC `G1-mech-corpus` 독립 설계 게이트**가 그 분모를 검사한다. ★**정정 기록(설계리뷰 DR2-M5 — 무언 정정 금지)**: 구 표기는 **9개**였고 **§결정 5 가 확정 신설한 census baseline 파일이 열거에서 누락**돼 있었다. 그 파일은 **D-2(축별 `N < baseline` = FAIL)·D-3(비감소 ratchet)의 소비 대상 전체**이므로, 누락 상태에서는 *"구현이 이걸 안 만들면 RED 가 나는가"* 라는 §결정 10 자신의 결속 판정 기준이 **그 산출물에 대해서만 성립하지 않았다**(corpus 게이트 자신의 exit 3 조건 ⓶ 로만 사후 검출). 배선 상세 SSOT = internal-docs `wrapper/change-plans/cfp-2963-mclats-arc-ci-runner.md` **§8.QC-MECH**. ADR-154 §결정 8 의 *"Phase 1 = ADR + Change Plan NARRATIVE only"* **무손상**.
- ★**천장 동시-변경 불변식**: 본 ADR **§결정 9** 의 정직 천장과 §8.QC-MECH **MECH-9** 의 정직 천장은 **같은 문면을 양쪽에 보유**한다 — **한쪽에서만 천장을 완화해 인용하는 것을 금지**하며 바꾸려면 **두 문서가 함께** 바뀌어야 한다. 한쪽만 완화하는 것 자체가 본 ADR 이 겨냥하는 class(*선언과 실상태의 조용한 괴리*)의 문서-축 발현이다. (분할 이관으로 normative 본체 중복은 해소됐으므로 이 불변식의 적용 범위는 **천장 문면 + 계수** 로 한정된다.)
- ★**AC 결속의 잔여 — 요구사항 lane 회부 계류**: 신설 harness 의 self-test 는 `tests/scripts/test_check-*.sh`(셸)이고, Change Plan §8.1.1 RTM 머리말이 *"명명 테스트 열에 셸 함수·스크립트 경로를 백틱으로 적지 않는다 — 적으면 파서가 식별자로 오인해 born-missing"* 을 비협상으로 못박는다. ⇒ AC 신설·tier 판정은 **요구사항 lane 소유**이며 설계가 대행하지 않는다. **회부 종결 전까지 본 산출물군은 `ac-traceability-matrix` 정의역 밖**이다(§8.AC 회부 packet SSOT).
- ★**mandate 편차 정직 기재**: 본 계약의 초판은 설계 lane 6 permanent deputy 중 **4 미수령** 상태에서 통합됐고, 그 결과 **회부한 축에서 실제로 P0 가 발생**했다. 1차 개정이 APIContractArchitectAgent 수령분(판별자 계약 · sidecar manifest — **실행 재현 기반**)을, 2차 개정이 **ModuleArchitectAgent**(corpus 경로·형상·dependency direction) + **InfraOperationalArchitectAgent**(운영 리스크 6-sub · §11.6 멱등)를 반영했다. 3차 개정이 **TestContractArchitectAgent**(blinded 섭동 IC · census 7축 · arm-L 타당성)를 반영했다. ⇒ ★**4 미수령 전건 수령·반영 완료 — 미수령 잔여 0.** 단 **수령 완료는 천장 해소가 아니다**(HC-1·HC-2 + U-2~U-5 존치). ★**미수령이 실제로 P0 를 낳았다는 사실은 사후에도 확증됐다** — ModuleArch 수령분이 **required 게이트 정의역 침범**(`check_ac_traceability_matrix` 가 corpus `.py` 심볼을 편입해 AC↔named-test 판정을 fail-open 시키는 경로 — Change Plan MECH-8)을, InfraOp 수령분이 §결정 10 리터럴 근거의 오류를 각각 반증했다. *"수령 전 통합" 은 회부 표기로 갈음되지 않는다.*

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

N/A — permanent policy (`is_transitional: false`). 단 **§결정 9 의 미확정 1건(TestContractArch 축 — blinded 섭동 · arm 별 분모 하한 분해 · arm-L 표본 타당성)** 은 후속 deputy 수령 시 본 ADR Amendment 가 아니라 **Change Plan §8.QC-MECH 배선면 확정**으로 착지한다(결정면 ⊥ 배선면 분리 유지). ★ 선행 2건(**corpus 경로·형상**[ModuleArch] · **운영 리스크 6-sub·§11.6 멱등**[InfraOp])은 **이 경로로 이미 착지**했다 — 본 ADR 무Amendment.

## 관련 파일

- [ADR-154](ADR-154-hard-gate-self-verification-forcing-function.md) — 상위 렌즈. **무수정 cross-ref**(§결정 2/4/5/6/7/8/9 재사용). Amendment 2 = 적용 대상(A2-2) + A1-3 조건 해제 + 본 ADR 포인터로 축소 존치
- [ADR-151](ADR-151-selftest-execution-liveness-inventory.md) — 인벤토리 1행 enroll(8-field 스키마 무접촉) + §결정 1 신규 ADR prong 3-conjunct(형태 판정 근거)
- [ADR-157](ADR-157-infra-resource-manifest-drift-gate.md) — D-3 형판 제공(기전 차용 · 방향 반전). 무수정
- [ADR-171](ADR-171-evidence-enforceable-promotion-framework.md) — warning → required 승격 evidence-gate(§결정 6 3-AND · §결정 10 증거 기한)
- [ADR-133](ADR-133-adr-reservation-atomic-claim.md) — 번호 claim primitive(§결정 11)
- `docs/hollow-gate-corpus-manifest.yaml` — 본 ADR §결정 8 sidecar manifest (Phase 2 산출)
- `docs/hollow-gate-corpus-baseline.yaml` — 본 ADR §결정 5 census baseline(7축 high-water mark · `content_digest` 결박). **D-2/D-3 의 소비 대상 전체** (Phase 2 산출 — ★설계리뷰 DR2-M5 로 본 목록에 신설)
- `docs/evidence-checks-registry.yaml` — warning-tier entry 1행 (Phase 2 산출)
- `docs/selftest-execution-liveness-inventory.yaml` — 신설 harness self-test 1행 enroll (Phase 2 산출)
- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — versioning 규약 cross-ref(`:197-199` SemVer · `:139` MINOR 선례)
- internal-docs `wrapper/change-plans/cfp-2963-mclats-arc-ci-runner.md` §8.QC-MECH — **배선면 SSOT**(결정면 ⊥ 배선면)
- internal-docs `wrapper/stories/CFP-2963.md` §9.12 — 본 ADR 을 낳은 설계리뷰 verdict(판정 전환 근거)
