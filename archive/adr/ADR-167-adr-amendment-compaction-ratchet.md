---
adr_number: 167
title: ADR amendment 누적 임계 재제정(compaction) ratchet
date: 2026-07-25
status: Accepted
category: governance
carrier_story: CFP-2812
supersedes: null
amends: null  # new-sibling — ADR-058 §결정 5 옵션 A 거부 무변경 pointer-only + genre-layers 폐기·교체 절 접합. 기존 계약 supersede 0.
related_adrs:
  - ADR-058  # pointer-only — §결정 5 옵션 A(count cap) 거부 유지(차단≠재제정 트리거, response type disjoint) + §결정 9/10 능동 일몰 anchor·위생편집(word-level) vs 재제정(record-level) 경계
  - ADR-121  # supersede mechanics 선례(3건 퇴역, status 전이 shape) — semantic 선례 아님(deprecation ≠ carrier-preserved 재제정). supersedes 배열 drift(ADR-105 누락) = D8 실증
  - ADR-133  # ADR 번호 atomic claim 3단계 재사용(발명 0) — 본 ADR 번호(167) 발급 mechanism
  - ADR-050  # RESERVATION 잠금 재사용 — 단계 6 active → archived 전이
  - ADR-097  # §결정 3 bulk(9+) carrier-preserved — 조건 완화 아닌 disjoint 신규 codify(단일-ADR 경로, ADR-095 §결정 3 specialize 패턴)
  - ADR-095  # age 축 threshold(GA/Beta 시간)와 disjoint 병존 — 대체 아님, carry-over invariant 보존
  - ADR-064  # §결정 7 evidence-gated symmetric ratchet = 재제정 justification framework. CFP-2804 이연 cascade 실증 = why 근거
  - ADR-145  # forward-only + grandfather 페어(I-APPLIC) 답습 — 소급 fail 0
  - ADR-153  # grandfather-then-retire 직접 선례 — baseline 은퇴 경로
  - ADR-060  # 게이트 host framework — warning tier + registry + promotion criteria
  - ADR-074  # count 파싱 primitive 기존재 — 재사용 비채택(first-key-wins semantics 보존)
  - ADR-119  # honest-ceiling 명문 어휘 패턴(§결정 6 정직 천장)
  - ADR-136  # honest-ceiling 명문 어휘 패턴(I-6 정직 천장)
  - ADR-151  # self-test liveness inventory 등록 의무
  - ADR-082  # §결정 16 resource-safety claim 정직
  - ADR-146  # §8.8 burden-flip 동적 테스트 로스터
  - ADR-127  # 재제정 1건 = full 8-lane Story 비용 구조(후속 Story 단위)
  - ADR-014  # superseded ADR amend 결격 규범 기존재 — 기계 강제 편입 미편성(게이트 scope 밖 관찰 기록)
related_stories:
  - CFP-2812
related_files:
  - scripts/lib/check_adr_amendment_threshold.py  # count 산식 + grandfather baseline 대조 게이트(THRESHOLD_N SSOT)
  - docs/adr-amendment-threshold-baseline.yaml  # grandfather baseline(도입 시점 산식 스캔 — 단조 비증가)
  - docs/domain-knowledge/domain/governance-principle/adr-active-sunset-procedure.md  # G1 4번째 트리거 + G2 C-1 variant(Superseded 경로) + supersedes N:1 전수 기재
is_transitional: false
amendments:
  - amendment_id: 1
    carrier_story: CFP-2840
    date: 2026-07-26
    reinterpretation: false  # 본문 §결정 1-8 소급 재해석 아님 — §결정 5 "퇴역 시 항목 제거"의 count 게이트 realization 명문화(규범 substance 무변경)
    summary: "§결정 5 Superseded-skip semantics 명문화 — 재제정 완료 상태(구 ADR status: Superseded 전이 + baseline 항목 제거) 무모순 성립을 위해 count 게이트가 status: Superseded 계열 3형을 (a) threshold 판정 ∧ (b) --write-baseline picked 양층에서 skip(census files_checked 계수 유지, no-false-skip: Accepted/Proposed/Sunsetted/None/empty 절대 skip 안 함). ratchet 강화 방향(퇴역 realization 게이트 배선)."
    sunset_justification: "N/A — ratchet 강화 방향 (퇴역 realization 게이트 Superseded-skip 배선, forbid scope 축소 아님). ADR-058 §결정 5 강화 방향. is_transitional: false 유지."
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-2840
    reservation_date: 2026-07-26 KST
    sub_scope: "§결정 5"
    reinterpretation: false
    summary: "게이트 Superseded-skip semantics 명문화(§결정 5 realization) — CFP-2840 Phase 2 게이트 배선 carrier."
mechanical_enforcement_actions: []  # 게이트 배선(threshold/parity workflow + baseline + registry 2 entry) = CFP-2812 §5 이행. 본 ADR = 재제정 ratchet 규범 결정 SSOT. Amendment 1(CFP-2840) = §결정 5 Superseded-skip 게이트 배선(is_superseded_status 7번째 순수 helper + 양층 skip).
---

# ADR-167: ADR amendment 누적 임계 재제정(compaction) ratchet

## 상태

**Accepted** (2026-07-25 KST, CFP-2812 Phase 2 carrier — 설계리뷰 PASS 후 landed). 발의 근거 = ADR corpus append-only 누적 부채의 사후 sweep(REACTIVE) 고비용 실증(CFP-2697/2799/2804). draft 원류 = CFP-2812 Change Plan §10.1 embedded(embedded 시점 표기 = Proposed → landed = Accepted). `Closes CFP-2812 설계 fork(§9)`.

## 컨텍스트

codeforge ADR corpus 는 append-only (본문 동결 + Amendment append) 라 Amendment 누적 시 본문(구 서술)과 실효 규범(접힌 상태)이 어긋나는 stale drift 가 생긴다. 실측 (2026-07-23): Amendment 헤딩 539건/75문서, 상위 5개 문서가 46%. 사후 sweep (CFP-2697/2799/2804) 은 고비용이고 미집행 시 구 표현이 신규 저작으로 재생산됨이 실증됐다 (CFP-2804). 외부 ADR 표준 (Nygard/MADR/adr-tools) 은 supersede mechanics 는 정의하나 **"언제 supersede 해야 하는가" 트리거 규범이 없다** — 임계 기반 트리거 규범화가 본 ADR 의 고유 substance 다. `source: cognitect.com/blog/2011/11/15/documenting-architecture-decisions, adr.github.io/madr (Story §6.1 C1 승계)`

**용어 정의** (AC-1 ⑧): **compaction = 재제정 (re-enactment/recodification)** — 실효 규범을 의미 무변경으로 깨끗한 신규 record 에 재작성하고 구본을 동결 퇴역시키는 것. **이력 삭제가 아니다** — Kafka log compaction (key마다 최신값만 보존, 구 레코드 물리 삭제) semantics 를 **명시 부정**한다: 구 ADR 은 본문 byte-보존 + in-place 동결 유지 (이력 = 구 ADR 동결 보존). 의미 모델의 원류 = 법제 재제정 (positive law codification — "restate without substantive change"). `source: docs.confluent.io/kafka/design/log_compaction.html, uscode.house.gov/codification (Story §6.1 C2/C3 승계)`

## 결정

**§결정 1 — 이원 트리거 (기계 count 축 / 리뷰 판정 축 분리)** (AC-1 ①): ADR 은 다음 둘 중 하나로 "재제정 의무" 상태가 된다.
- (a) **기계 count 축**: `effective_count >= N` — CI 게이트가 기계 판정한다.
- (b) **리뷰 판정 축**: 본문 의미를 소급 재해석하는 조항 (semantic reinterpretation) 부착 — 저작 시점 self-declare marker (`reinterpretation: true`) + 리뷰 lane 인간 판정. **기계 게이트 비대상임을 명시** — count 는 부피 프록시일 뿐이며, 대형 amendment 병합·재해석 위장 등 Goodhart gaming 은 리뷰 판정 축이 보완한다 (축 분리 선언 = hollow-gate 회피). `source: buttondown.com/hillelwayne (Goodhart — Story §6.2 U4 승계)`
- "재제정 의무" = 기존 3축 (lifecycle `status:` / `sunset_status:` / `is_transitional:`) 어디에도 속하지 않는 **4번째 disjoint 유지보수 부채 신호** — 저장 필드 없이 게이트 계산형(count 축) + marker(판정 축) 로 표현되며, clear 조건 = 재제정 완료 시 구 ADR 의 `status: Superseded by ADR-Y` 전이로 자연 종결.

**§결정 2 — counting 단위 + N (단일 SSOT)** (AC-1 ②):
- counting 단위 = **`effective_count = max(본문 헤딩 count, frontmatter entry 합산 count)`**. 본문 헤딩 = `^#{2,4} Amendment` 정규식. frontmatter = `amendment_log` 배열 길이 + `amendments` 배열 길이 **합산** (2-dialect 공존 실측 대응). count 는 배열 길이 기준 — entry 내부 key dialect 무관.
- 판정 = **이상 (`>=`)**.
- **N 의 operational SSOT = 게이트 스크립트 상수 단일 리터럴** (`scripts/lib/check_adr_amendment_threshold.py` `THRESHOLD_N`). 본 ADR 은 값을 리터럴로 담지 않는다 (genre-layers 예방규약 V2 — 가변값 리터럴 임베드 금지, 기수-제거). 도입 시점 값 = 10 (2026-07-24 dated 스냅샷 기술 — 규범 아님). **N 변경 절차** = 본 ADR amendment 의무 + baseline 재산정 동반 (소급 fail 0 원칙이 새 N 에도 유지 — §결정 5). CLAUDE.md 등 다표면 리터럴 복제 금지 — 참조는 pointer 로만.

**§결정 3 — 재제정 경로 = 기존 supersede + 능동 일몰 mechanics 재사용 (신규 절차 발명 0)** (AC-1 ③):
- 실행 = ① 신규 ADR 번호 = ADR-133 atomic claim ② 현행 실효 규범을 깨끗한 본문으로 재작성한 신규 ADR 발행 ③ 구 ADR `status: Superseded by ADR-<신규>` 전이 (ADR-121 shape — 본문 byte 무변경) ④ G3 역참조 갱신 (adr-active-sunset-procedure) ⑤ RESERVATION row `active → archived` (단계 6, GitOpsAgent monopoly) ⑥ grandfather baseline 항목 제거.
- 참조 절차 = adr-active-sunset-procedure **G1 6단계** (ADR-121 이 매핑한 ADR-023 §결정 2 7-step 은 lane-plugin lifecycle 절차 — 참조 대상 아님). G1 단계 1 트리거 목록에 본 ADR 의 이원 트리거가 4번째 항목으로 추가된다. G2 에는 Superseded (named 후계) 경로 variant 가 신설된다 (기존 C-1 = Sunsetted 전용).
- **`supersedes:` 배열 = 전 퇴역 대상 전수 기재 (N:1)** — ADR-121 의 ADR-105 배열 누락 실증 재발 방지. mechanical lint 는 G3.3 declarative-only 정합 (pattern_count 재발 시 후속 carrier).
- **ADR-097 §결정 3 과의 관계**: 그쪽 carrier-preserved sunset 은 bulk (9+ 동시 sunset) scope 진입조건이 있는 closed-set — 본 결정은 그 조건을 완화하지 않고 **단일-ADR carrier-preserved 재제정을 disjoint 신규 개념으로 codify** 한다 (ADR-095 §결정 3 이 carrier-preserved 개념을 metric 차원으로 specialize 한 선례와 동일 패턴).
- **genre-layers 접합**: 본 결정은 genre-layers "폐기·교체 1급화 (authoring-reflex 교정)" 절에 접합한다 — 그 절은 record-level 교체의 집행 SSOT 를 ADR-058 §결정 9 로 이미 위임했고 (신설 0 명문), 본 ADR 은 그 위임 경로에 트리거만 얹는다 (재서술 없이 인용). hygiene class (i)-(iv) (in-place word-level 위생) 와는 단위가 다르다 — 재제정은 frozen 본문을 아예 건드리지 않으므로 ADR-058 §결정 10 위생편집보다 보수적이다.

**§결정 4 — 재제정 산출물 필수 요소** (AC-1 ④⑤): 재제정으로 발행되는 신규 ADR 은 다음 2요소를 필수 포함한다 (법제 재제정 2대 불변식 승계).
- (a) **no-substantive-change 명시 선언**: "본 ADR 은 구 ADR(들)의 실효 규범을 의미 무변경으로 재작성한 재제정이다" — 허용 변경 = 구조 개선·obsolete 제거·모호 해소·기술 정정 한정. **의미 변경이 필요하면 재제정이 아니라 신규 결정으로 분리**한다. `source: uscode.house.gov/codification/legislation.shtml (Story §6.1 C2 승계)`
- (b) **disposition table**: 구 §결정 → 신 §결정 매핑 표 (N:1 포함 — 폐기/재정의/이관 각 항목 명시. ADR-121 §결정 E/F 관행의 필수 템플릿 요소 승격).
- 의미 무변경 검증 oracle 은 기계화 불가 (§결정 7) — 담보 = 위 2요소 + 8-lane 리뷰 신구 대조.

**§결정 5 — forward-only 적용 경계 + grandfather** (AC-1 ⑥):
- 적용 경계 = **forward-only + grandfather 페어** (ADR-145 I-APPLIC 답습): 게이트 강제는 도입 이후 신규 누적분부터. 기존 backlog 는 소급 fail 0.
- baseline = **ADR 단위 grandfathered-at count** — 집합·값 = 게이트 실제 산식의 도입 시점 corpus 스캔으로 산정 (독립 리터럴 목록 금지 — 산식↔baseline 소스 동일성 invariant). baseline **단조 비증가** (entry 값 증가·추가 금지 — 유일 예외 = N 하향 변경 시 재산정) + 퇴역 시 항목 제거 + **재제정 신규 ADR 은 count 0 재시작** (사이클 반복 정합 — 트리거 재발동 = 정상 동작).
- 신규 amendment 는 **frontmatter entry 기재 의무 (forward-only)** — parity lint 가 heading-only 저작을 검출하고, 신규 entry 는 `reinterpretation:` boolean marker 를 필수 포함한다.
- **backfill 경계 (오검출 방지 semantics)**: grandfather 기준 = 도입 시점 스캔의 **관측치**. 도입 시점에 이미 관측된 amendment 의 사후 frontmatter 등록은 max() 산식상 count 를 바꾸지 않는다 (오검출 0). 도입 시점 양 표면 모두에 비가시였던 은닉 누적의 사후 노출은 **소급이 아닌 신규 관측 — 검출 정당 (지연 검출)**. "소급 fail 0" 의 보호 대상 = 도입 시점 관측 가능했던 누적.

**§결정 6 — ADR-058 §결정 5 옵션 A 거부와의 관계 (pointer-only)** (AC-1 ⑦): ADR-058 §결정 5 는 amendment count cap (옵션 A — hard limit 이 정당한 amendment 까지 차단할 위험) 을 거부했고, **그 거부는 본 ADR 에 의해 변경되지 않는다**. 본 ADR 의 임계는 amendment 를 **차단하지 않는다** — amendment 횟수는 여전히 무제한이며, 임계 도달의 효과는 "재제정 의무" 신호 발생뿐이다 (response type disjoint: 차단 cap ≠ 재제정 트리거). 본 항은 ADR-058 §결정 5 본문 무변경 pointer-only 참조다 — 재서술 금지 (split-brain 자기생산 차단).

**§결정 7 — honest ceiling (기계화 불가 명문)**: 본 ADR 의 기계 게이트가 보증하는 것은 (a) count 산식 판정 (b) marker 의 presence/type consistency (c) baseline 무결성 검사 — **까지다**. 다음은 기계화 불가하며 리뷰 판정 축 (인간 판정) 의 몫이다: 재해석 여부의 의미 판정 / prose-only 본문 편집 (양 표면 미기재 — count 게이트 완전 회피 사각) / 재제정의 의미 무변경 (semantic fidelity) 검증. **금지 표현**: "모든 재해석을 기계 검출"·"stale drift 재발 근절"·"완전 봉인" 류 hard-claim 금지 (ADR-119 §결정 6 / ADR-136 I-6 정직 천장 정합).

**§결정 8 — 기존 threshold 축과의 병존**: 본 count 축은 ADR-095 의 age 축 (도입 사유 해소 후 GA/Beta 시간 threshold) 을 **대체하지 않는다** — disjoint 신규 threshold 축으로 병존한다 (동일 대상 ADR 에 두 축이 독립 발동 가능). 기존 sunset 체계 (ADR-058 3-tuple / ADR-095 age / 본 ADR count·재해석) 의 carry-over invariant 는 전량 보존된다.

## 결과

(+) stale drift 를 사후 sweep (REACTIVE) 이 아닌 임계 트리거 (PREVENTIVE) 로 예방 — CFP-2697/2799/2804 계열 비용 구조 절감. (+) 신규 절차 발명 0 — 전 mechanics 기존 자산 재사용. (−) 재제정 의무 1건 = full 8-lane Story 1건 비용 (ADR-127). (−) marker 진위·prose-only 편집은 기계 보증 밖 잔존 (§결정 7 정직 명시). backlog 18건 (도입 시점 실측) 의 실제 재제정 = 후속 Story (워스트 상위부터, 자발 — grandfather 로 강제 아님).

**cross-ref**: ADR-058 §결정 5 (pointer-only)/§결정 9·10 · genre-layers 폐기·교체 1급화 절 · ADR-121 (mechanics 선례 — semantic 선례 아님) · ADR-133/ADR-050 (번호·잠금) · ADR-097 §결정 3 (disjoint specialize) · ADR-095 (age 축 병존) · ADR-064 §결정 7 (symmetric ratchet) · ADR-145 (forward-only+grandfather) · ADR-153 (baseline 은퇴 선례) · ADR-060 (게이트 tier host) · ADR-119/ADR-136 (honest ceiling).

## 관련 파일

- `scripts/lib/check_adr_amendment_threshold.py` — 게이트 SSOT (순수 함수 6종 + THRESHOLD_N 단일 리터럴 + fail-closed 파싱 + B-1/B-2 baseline 무결성)
- `scripts/check-adr-amendment-threshold.sh` / `scripts/check-adr-amendment-parity.sh` — thin wrapper (count 축 / 판정 forward-only 축)
- `docs/adr-amendment-threshold-baseline.yaml` — grandfather baseline (`--write-baseline` 단일 writer 생성, 산식↔baseline 소스 동일성)
- `templates/github-workflows/adr-amendment-threshold.yml` + `.github/workflows/` (byte-parity 쌍) — warning-tier CI 게이트 (threshold / parity 2 job)
- `docs/domain-knowledge/domain/governance-principle/adr-active-sunset-procedure.md` — 재제정 실행 절차 (G1 4번째 트리거 + G2 C-1 Superseded variant)
- `plugins/codeforge-design/templates/adr.md` — `reinterpretation:` forward-only marker 필수 필드
- `docs/evidence-checks-registry.yaml` — 게이트 tier/promotion 등록 (owner_adr ADR-167 / carrier_adr ADR-060)

## 해소 기준

N/A — permanent policy (ADR amendment 누적 임계 재제정 ratchet 상시 적용, is_transitional: false).

## Amendment 1 (CFP-2840) — §결정 5 Superseded-skip semantics 명문화

- `direction: strengthening` / `reinterpretation: false` (본문 소급 재해석 아님 — §결정 5 "퇴역 시 항목 제거"의 count 게이트 realization 명문화, 규범 substance 무변경).
- **§결정 5 보강 (Superseded-skip semantics)**: 재제정 완료 상태(구 ADR `status: Superseded by ADR-Y` 전이 + baseline 항목 제거)의 무모순 성립을 위해, count 게이트(`scripts/lib/check_adr_amendment_threshold.py`)는 `status: Superseded` 계열 3형(bare `Superseded` / `Superseded by ADR-NNN` / `Superseded-by-ADR-MMM`) ADR 을 (a) threshold 판정 ∧ (b) `--write-baseline` picked 선별 **양층에서 skip** 한다. skip 대상도 census(`files_checked`) 계수는 유지한다(anti-vacuity). skip 은 `status: Superseded` 계열만 — `Accepted` / `Proposed` / `Sunsetted` / `None` / empty 는 절대 skip 하지 않는다(no-false-skip).
- **honest ceiling 상속 (§결정 7)**: 재제정 *설계 시점*(본 Story 병합 전)에는 live corpus 에 Superseded ∧ effective ≥ N ADR = 0 이었으나, **본 Story 재제정으로 ADR-082(`status: Superseded by ADR-168`, effective 76 ≥ N, byte-frozen 본문)가 첫 permanent-live 케이스**가 되어 skip 브랜치를 상시 exercise 한다 — "skip 은 production 에서 안 밟힘/dead-branch" 오독 금지. 회귀 담보 = 격리 fixture + 양방향 mutation self-test(설계 시점 dead-branch 대비 도입, 이후 permanent-live 회귀 보장). **Superseded status 진정성**(genuine 재제정 vs bare-flip evasion) 검증 = **governance-tier**(C-1 variant named-successor `Superseded by ADR-Y` 필수 + archive/adr PR review + branch protection + ADR-014 superseded-amend 결격) — 기계 skip 은 status 표기만 신뢰하며 진정성은 human review 축 위임(honest-ceiling, self-gaming 잔여 정직 수용). "완전 봉인" 류 hard-claim 은 하지 않는다.
- `sunset_justification`: N/A — ratchet 강화 방향(퇴역 realization 게이트 배선, forbid scope 축소 0).
- 게이트 코드·self-test 실배선 = CFP-2840 Phase 2 (`scripts/lib/check_adr_amendment_threshold.py` `is_superseded_status` 7번째 순수 helper + 양층 skip + `tests/scripts/test_adr-amendment-threshold.sh` 확장).
