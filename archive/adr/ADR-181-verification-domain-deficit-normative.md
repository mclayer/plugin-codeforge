---
adr_number: 181
title: 검증 정의역 결손(P⊋V) 규범 — 정의·정직 불변식·게이트 설계 제약·접합부
date: 2026-08-16
status: Accepted
category: governance
carrier_story: CFP-2985
supersedes: null
amends: null  # new-sibling — 기존 계약 supersede 0. ADR-067/ADR-171 은 본 ADR 을 인용하는 적용 carrier (§결정 8)
related_adrs:
  - ADR-067  # fix-ledger implementability escalation — FIX 닫기 조건 축의 적용 carrier (Amendment 4)
  - ADR-171  # evidence-enforceable promotion framework — 신규 entry 의 carrier_adr(host). §결정 5 가 "owner ADR + carrier_adr 귀속" 경로를 명시 허용하므로 ADR-171 amendment 0 (재제정 effective_count 0 보존)
  - ADR-119  # 검증 후 단언 — §결정 10② 가 "반증"을 규정하나 반증의 정의역은 미규정. 본 ADR 이 그 공백을 채운다 (§결정 1)
  - ADR-151  # presence ≠ truth — 정직 천장 규범. 본 ADR §결정 6 이 그 라벨 규율을 승계
  - ADR-155  # dev-process observability substrate — _ROW_KEYS closed allow-list, 본 ADR INV-C 의 실물 서식지
  - ADR-156  # metric aggregation escalation feed — 정직-null 로 결손을 보고 중인 선례 (INV-D 의 모범)
  - ADR-070  # verify-before-trust — 선언-only 13 amendment 계보. §결정 5 admission test 의 반면교사
  - ADR-127  # 정식 8 lane + Phase 1/2 PR 분리 — 본 ADR 의 Phase 경계 근거
  - ADR-145  # AC traceability zero-drop — normative AC ↔ 명명 테스트 결속 선례
  - ADR-133  # ADR 번호 atomic claim — 본 ADR 번호(181) 예약 mechanism
related_stories:
  - CFP-2985
related_cfps:
  - CFP-2985  # carrier — FIX 원인 계측 채널 실채움 + 검증 정의역 선언
related_files:
  - docs/inter-plugin-contracts/fix-event-v1.md  # 원인 판정 값공간 + 정의역 선언 필드. ★ 현 실버전 = v1.5 — v1.6 MINOR bump 는 본 PR 내 D-1 로 미착지(현재형 기술 금지, §결정 5 ②)
  - docs/inter-plugin-contracts/dev-process-event-v1.md  # root_cause_class 원장 키. ★ 현 실버전 = v1.0 — v1.1 MINOR bump 는 Phase 2 (D-19 / carrier plugin-codeforge#2985 / 만기 2026-09-15)
  - docs/evidence-checks-registry.yaml  # fix-ledger-conformance entry (owner_adr = 본 ADR). ★ 본 PR 에 실 append 완료 — 112 → 113 entry
  - docs/domain-knowledge/concept/verification-domain-deficit.md  # 개념 서술 SSOT (본 ADR 이 규범 SSOT)
is_transitional: false
mechanical_enforcement_actions: []  # Phase 2 이행 — scripts/lib/check_fix_ledger_conformance.py + thin wrapper + workflow twin + discriminating self-test. carrier = plugin-codeforge#2985 / 만기 2026-09-15. ★ 본 빈 리스트는 §결정 5 의 두 충족 경로 중 **면제 경로**(len==0 ∧ carrier ∧ 만기)로 ② 를 충족한다 — 사다리 경로((가)(나)(다)) 가 아니며, 따라서 "돌아가는 검사가 있다" 를 주장하지 않는다(§결정 5 면제 경로 천장 문단 참조). ① = 본 PR 의 docs/evidence-checks-registry.yaml row fix-ledger-conformance (112 → 113, current_tier warning / status deferred-followup) 로 충족 — firsthand 재검증: grep -c 'fix-ledger-conformance' docs/evidence-checks-registry.yaml → 3(정의 1 + 주석 2). 만기 경과 시 면제 경로를 잃고 사다리 경로만 남으므로 부적법 전환된다.
---

# ADR-181: 검증 정의역 결손(P⊋V) 규범 — 정의·정직 불변식·게이트 설계 제약·접합부

## 상태

Accepted (2026-08-16) — CFP-2985 Phase 1 설계 carrier.

## 컨텍스트

### 왜 개념에 규범 SSOT 가 필요한가 — 유령이 실물로 관측됐다

`root_cause_taxonomy` 는 이 repo 에서 **참조 4 site / 정의 0 건**이다 (firsthand @ wrapper `ecfe62d63`):
`archive/adr/ADR-045-story-retro-mandatory-trigger.md:487` · `docs/inter-plugin-contracts/pmo-output-v1.md:122` ·
`plugins/codeforge-pmo/agents/PMOAgent.md:188` · `plugins/codeforge-pmo/templates/retro.md:79`.
정의가 없으므로 ADR-045 §D-9 의 **2차 검출 채널이 값공간 부재로 사망**했고, 아무도 그 사망을 보고하지 않았다.

CFP-2985 는 `P`(처방 정의역) / `V`(검증 정의역) / `D = P \ V` 라는 개념을 도입하며, 그 개념을
`fix-event-v1`(계약) · ADR-067(FIX 닫기) · ADR-171(게이트 tier) · 신규 checker 네 곳에서 참조한다.
**참조 4 곳에 정의 0 곳** — `root_cause_taxonomy` 와 정확히 같은 형상이다.
따라서 본 ADR 의 첫 존재 이유는 새 규범의 추가가 아니라 **정의의 착지면 확보**다.

### 규범 공백의 정확한 좌표

`ADR-119` §결정 10② 는 "수정됨 = 반증 후 단언" 을 규정한다. 그러나 **반증의 정의역**은 규정하지 않는다 —
무엇을 반증 대상으로 삼아야 하는지가 저자 재량이다. 그 재량이 실측으로 어떻게 소진되는지:

- `fix-event-v1.md:304` — FIX "수정됨" close = `replay_verdict == PASS` (원 reproducer 재실행 GREEN).
  `reproducer_command`(`:88`)는 **단수 명령**이다. 형제 site 는 탐지 실패하는 것이 아니라 **정의상 검사 범위 밖**이다.
- CFP-2949 = 봉합 커밋 자신이 형제 site 검출력을 파괴했고, 3 라운드 전부 GREEN 아래에서 결함이 생존했다.
- CFP-2985 요구사항 lane 실측 — FIX 3회차 이상 진입 Story 54건에서 "검증 정의역·맹점" 결함 class 가
  나머지 522건 대비 **4.10×** (문서 바이트 정규화, 건/MB). 같은 성격의 분석 어휘인 hollow-oracle 은 **0.45×** 로
  오히려 낮아 균일 인플레가 아니다(교란 통제).

### 이 ADR 이 스스로 넘어야 하는 시험

본 ADR 은 "선언 1건 추가" 가 될 위험을 태생적으로 진다. `ADR-070` 은 amendment **13개** 전건이
`mechanical_enforcement_actions: []` 였다(firsthand: `grep -cE '^  - amendment_id:' archive/adr/ADR-070-*.md` → 13).
그중 Amendment 12 는 코드까지 쓰고 트리거에 안 붙였다(`grep -rn 'check-fix-replay-disposition' .github/` → 0 match).
따라서 §결정 5 는 **본 ADR 자신에게 먼저 적용되는 admission test** 다.

## 결정

### 결정 1 — 개념 정의 SSOT (P / V / D)

| 기호 | 정의 |
|---|---|
| **P (처방 정의역)** | 그 수정의 인과 주장이 논리적으로 적용되는 site 전체 집합. "이 원인 때문에 깨졌다" 고 말하는 순간 같은 원인이 성립하는 모든 자리가 P 에 들어온다 |
| **V (검증 정의역)** | 닫기 시점에 실제로 재검사·재실행·재관찰한 site 집합 |
| **D = P 차집합 V (결손)** | "고쳐졌다" 고 선언됐지만 아무도 쳐다보지 않은 자리 |

- **P ⊋ V 는 결함이 아니라 상시 상태다.** 본 ADR 이 금지하는 것은 `D` 가 비어 있지 않은 것이 아니라
  **`D` 를 미선언 상태로 두는 것**이다. 완전성(`D` 공집합) 요구는 오라클 부재로 기계 판정 불가이며(§결정 6),
  normative 로 세우면 반드시 선언-only 로 착지한다.
- 서술 SSOT = `docs/domain-knowledge/concept/verification-domain-deficit.md`. **규범 SSOT = 본 ADR.**
  두 문서가 충돌하면 본 ADR 이 정본.
- 본 정의를 참조하는 문서는 정의를 **재진술하지 않고 본 §결정 1 을 인용**한다
  (재진술 = 값공간 분기 = §결정 4 접합부 위반).

### 결정 2 — 정직 불변식 7종 + 기계판정 라벨

> 라벨 규율 = §결정 6. `normative` = 판정 경로(입력 → 비교 → exit code)를 적을 수 있음. `declared` = 못 적음.

| ID | 불변식 | 라벨 | 판정 경로 또는 불가 사유 |
|---|---|---|---|
| **INV-D** 정의역 정직 | 검사 정의역 ⊇ 선언 정의역. 선언 문면이 실 검사 범위보다 넓으면 위반 | `normative` (부분) | 선언 문면 ↔ fixture·코퍼스 정의역 대조 → 불일치 시 비-zero exit. 완전성은 `declared` — "선언이 실 범위를 안 넘는가" 는 보되 "실 범위가 충분한가" 는 못 본다 |
| **INV-R** 범주 분리 | **재진입 라우팅 축**(`원인 판정` — 값 개수 = 재진입 가능 lane 수)과 **결함 class 축**(`defect_family` 계열)을 같은 enum·같은 집계 키로 assert 금지 | `normative` | 집계 산출물에서 두 축의 교차 키 부재 assert |
| **INV-A** append-only 정정 | 기록면 정정은 기존 행 mutate 금지, **다음 행 append** | `normative` | cut SHA 이후 diff 에서 기존 행 변경 0 assert |
| **INV-N** 분모 하한 | 판정 표의 `normative` 개수 ≥ 선언 하한. 전건 `declared` flip 으로 게이트를 초록으로 만드는 경로 차단 | `normative` | 개수 파싱 → 하한 미만 시 비-zero exit. 천장 — 하한 감소만 막고 애초 낮게 선언하는 것은 못 막는다(자기신고) |
| **INV-P** 파서 정의역 동일성 | 같은 대상면을 읽는 파서가 2개 이상이면 **같은 입력에서 같은 산출 집합**을 내거나, **차이를 열거·방출**한다 | `normative` | 두 파서 산출 대칭차 계산 → 차이 목록이 선언 문면과 불일치 시 비-zero exit. **"대칭차 0" 을 요구하지 않는다** — 현 시점 대칭차가 이미 0 이 아니다(아래 근거) |
| **INV-C** 채널 도달 | census 키 전량이 방출되고 baseline 헤더에 기록된다. **판정이 이동했는데 말해주는 채널이 0 인 상태 금지** | `normative` | 키 개수 + 헤더 기록 presence + 실행 간 drift 보고. **정수 exit 금지**(ratchet-in 회피) — exit 는 키 부재·카운터 불변에만 |
| **INV-V** vacuous 금지 | 검사 대상이 0 이면 GREEN 금지 — `corpus_scanned == 0` 이면 `vacuous=1` + exit 1 | `normative` | 실행 산출 파싱. 천장 — 전멸형(0)은 막고 **부분 소실형은 못 막는다**. 부분 소실은 가드가 아니라 **존재 오라클**이 필요하다 |

**INV-P 가 "대칭차 0" 을 요구할 수 없는 근거 (firsthand @ internal-docs `7e3127a8` / wrapper `ecfe62d63`)**:
§10 을 읽는 **프로덕션 파서가 이미 1개 가동 중**이다 — internal-docs `.github/workflows/fix-ledger-sync.yml:352-371`
(파이프 행 filter → `allRows.slice(1)` 헤더 skip → `cells.length < 6` 배제 → **`cells[4]` 인덱스 하드코딩** = `cause`).
그 구간 앵커(`:334`)는 `## 10.` 점 필수 · `§` 표기 불허 · 종료 `## 11.` 단일형 · 비-global 첫 매치 · 펜스 무인지의
**4중 협착**이다. 그리고 그 미러 검증기 wrapper `scripts/lib/check_workflow_yaml.py:60-98` 은 **CI caller 0 = dead**.
대칭차는 이미 0 이 아니고, 그 사실을 보고하는 채널도 0 이다. 따라서 요구는 **차이의 열거·방출**이다.

### 결정 3 — 게이트 설계 제약: "기계 강제" 라 부르기 전 8항

아래 8항 전건 충족 전에는 어떤 산출물도 문면에서 **"기계 강제" / "mechanical enforcement" / "hard-gate"** 로 기술하지 않는다.

| # | 조건 | 판정 형태 |
|---|---|---|
| C-1 | 의존성 설치 step 실재 (외부 의존 0 이면 **그 사실을 선언**) | workflow YAML assert |
| C-2 | 호출 workflow 실재 — 판정 술어는 **이름 grep 이 아니라 소비자 정의역 열거**(아래) | 3-채널 열거 |
| C-3 | 실행 증거를 **값으로 방출** (census 키 + 위반 수) | 로그 키 파싱 |
| C-4 | 대조군 mutant 로 RED 실증 — **base GREEN 을 같은 실행에서 동반**. 대조군 없는 RED 는 항진 오라클과 구별 불가 | 실행 결과 대조 |
| C-5 | required 등재 = 문서 표 ∧ 실 API 양쪽 | 문서 표만 `normative`, **API 실등록은 `declared`** |
| C-6 | **우회 라벨을 게이트보다 먼저 만들지 않는다** — 생성 선행조건 = 그 게이트가 RED 를 낸 실 CI run 참조 | registry ↔ run pairing |
| C-7 | tier 강등 1줄(`continue-on-error` 재삽입 · `paths` filter 삽입)을 테스트가 assert. **그 assert 는 검사 대상과 다른 workflow 에 둔다** — 대상 workflow 삭제가 assert 까지 죽인다 | 별 workflow YAML assert |
| C-8 | 배선을 후속 Phase 로 연기하는 항목마다 **carrier Issue 번호 + 만기일** 동반 | 표 파싱 |

**dead 판정 술어 (이름 grep 금지 — 본 ADR 채택 정본)**:

```
dead(X) := (X 를 소비할 수 있는 채널 전집합 C 를 열거한 명령이 기록돼 있고)
           ∧ (C 의 각 원소에 대해 X 도달 여부를 개별 판정했고)
           ∧ (도달하면서 blocking 인 채널이 0)
열거 채널 3종:
  (1) 이름 인용   : grep -rn '<basename-stem>' .github/
  (2) glob 러너   : glob 정의역 디렉터리와 X 경로 대조 — enrollment 는 실행이 아니다
  (3) 인벤토리    : execution_channel / channel_status / blocking_tier 3필드 판독
```

이름 grep 단독 판정은 **파일명을 인용하지 않고 소비하는 러너를 구조적으로 볼 수 없다**.
그 술어로 내린 dead 판정은 `declared` 이며 `normative` 로 기술 금지.

### 결정 4 — 접합부(joint) 규약

**접합부** = 둘 이상의 술어가 **같은 대상**을 볼 때 그 술어들이 쓰는 값공간의 정합 관계.

- 개별 술어가 각각 선언돼 있고 각각 정확해도, **두 술어의 값공간이 어긋나면 그 사이로 대상이 빠진다.**
  negative 실물 — 구간 앵커의 whitespace 값공간이 유니코드 전체인데 하위 술어의 정규화가 ASCII 3종이면,
  앵커는 통과하고 하위 판정만 실패해 **침묵 누락**이 된다.
  positive 실물 — 두 술어가 같은 토큰 집합을 공유하면 잔여 방출이 **구조적으로 보장**된다.
- **규범**: 새 술어를 도입하는 저작물은 그 술어가 **기존 어느 술어와 같은 대상을 보는지** 명시하고,
  같은 대상을 보는 쌍마다 값공간이 **동일한지 / 다른지(다르면 차이를 열거)** 를 선언한다.
- **완전성 주장 금지** (`declared`): 접합부 전수 열거는 술어 쌍 수만큼의 조합이므로 **전집합 판정 불가**.
  본 규약이 강제하는 것은 **"새로 도입한 술어에 대해 접합 선언을 했는가"** 까지다.
- 실물 3자 불일치 사례 — 마크다운 코드스팬 안의 파이프 문자: ⓐ 표 경계 규칙 = **비-분리자** /
  ⓑ GFM 렌더러 = **분리자**(백슬래시 이스케이프 요구) / ⓒ 이 repo 의 AC 표 파서 = 그 이스케이프 **미처리**.
  이스케이프하면 ⓒ 가 깨지고 안 하면 ⓑ 가 깨진다.
  **처분 = 이스케이프가 아니라 파이프를 표 밖 코드블록으로 이동**(세 소비자 동시 만족).

### 결정 5 — admission test: 새 규범 선언의 입장료

**신규 규범 항목을 ADR·계약·skill 문면에 추가하는 저작물은 동일 PR 에서 아래 3항을 전건 충족한다.**

| # | 요구 | 미충족 시 |
|---|---|---|
| ① | `docs/evidence-checks-registry.yaml` 에 대응 entry 가 **존재**한다 (tier = `warning` 로 태어남 — ADR-171 §결정 5). script·workflow 가 후속 Phase 면 entry status 필드에 **정직 표기** | 선언-only |
| ② | 본문이 **아직 존재하지 않는 enforcement 자산을 현재형으로 기술하지 않는다.** 미건설 자산은 미래형 + carrier + 만기로만 | 유령 선언 |
| ③ | `mechanical_enforcement_actions: []` 는 **carrier Issue 번호 + 만기일 주석 병기 시에만** 적법 | ADR-070 계보 |

- **기계 판정 분해**: ①③ = `normative` (frontmatter·registry 구조 파싱). ② = **`declared`** —
  산문의 시제 판정 술어가 부재한다. 대신 ② 의 기계 대체물로
  **frontmatter `mechanical_enforcement_actions[]` 각 항목의 3단 전건**을 쓴다:
  (가) 리스트 길이 ≥ 1 (나) 각 항목이 repo 내 **실재 실행 파일**로 해석 (다) 그 경로가 workflow `run:` 줄에 **등장**.
  (다)가 마지막 이빨이다 — (나)까지면 "파일만 만들고 안 돌린다" 가 통과한다.

#### ★ ③ ↔ (가) 값공간 관계 선언 (§결정 4 의 자기적용 — 미선언 시 판정 불가)

③ 과 (가) 는 **같은 대상**(`frontmatter mechanical_enforcement_actions`)을 보면서 `[]` 에 정반대 값을
내린다 — ③ 은 적법, (가) 는 부적법. §결정 4 는 이런 쌍에 값공간 관계 선언을 의무화하므로 여기서 선언한다.
**미선언 상태로 두면 어느 쪽이 exit 를 내는지 결정 불가이며, 그것이 본 §결정 5 를 판정 불가로 만든다.**

| 술어 | 성격 | 정의역 | `[]` 판정 |
|---|---|---|---|
| ③ | **admission**(저작 시점 입장 조건) | 신규 규범 항목을 추가하는 **그 PR 의 diff** | carrier + 만기 병기 시 **적법** |
| (가)(나)(다) | **enforcement-reality**(강제 실재 사다리) | 동일 | 길이 0 이므로 **미충족** |

**관계 = 배타가 아니라 포괄적 OR.** ② 는 아래 둘 중 **하나**로 충족된다:

```
admissible(entry) :=
      ( len(mea) >= 1  AND  각 항목이 실재 실행파일  AND  그 경로가 workflow run: 줄에 등장 )   # 사다리 경로
   OR ( len(mea) == 0  AND  carrier 주석이 /#\d+/ 매치  AND  만기 주석이 /\d{4}-\d{2}-\d{2}/ 매치 )  # 면제 경로
```

- **왜 AND 가 아닌가**: ①②③ 을 "전건 충족" 으로 묶은 것은 ①·②·③ **항목 간** 관계이지,
  ② 내부의 두 충족 경로 간 관계가 아니다. 사다리와 면제를 AND 로 읽으면 `[]` 는 영원히 부적법이 되어
  ③ 이 사문화되고, 반대로 ③ 만 읽으면 사다리가 사문화된다. **둘 다 살아 있어야 ③ 이 의미를 갖는다.**
- **면제 경로의 천장 (`declared`, 지우고 인용 금지)**: 면제 경로를 택한 선언에 대해 **(다) 는 도달하지 않는다.**
  즉 그 선언은 "돌아가는 검사가 있다" 를 증명하지 않으며, 증명하는 것은 **만기가 박혀 있다** 뿐이다.
  이것은 ADR-070 §D5 면제에 날짜 문자열을 덧댄 것과 **형태가 같다.** 다른 점은 단 하나 —
  만기 경과가 **기계 판정 가능**하다는 것이다(문자열 비교). 그 차이 외에는 면제이며, 그렇게 부른다.
- **만기 경과 시 처분**: 면제 경로는 **시한부**다. 만기일이 지난 `[]` 는 면제 경로를 잃고
  사다리 경로만 남으므로 부적법이 된다. 이것이 면제가 영구 회피구가 되지 않는 유일한 기제다.

★ **검사기 정의역 (INV-D 자기적용 — 코퍼스-wide 소급 아님)**: 본 §결정 5 의 기계 검사 정의역 =
**PR diff forward-only** (해당 PR 이 신규 추가·수정한 ADR 파일). merge-base 시점에 이미 존재하던
ADR 은 정의역 **밖**이다. 근거 — §결정 5 문면이 "신규 규범 항목을 추가하는 **저작물**" 로 저작 시점을
scope 로 삼고, 소급 적용하면 코퍼스 전수 `[]`·키부재 다수가 즉시 born-red 가 되어
**전 PR 자해 차단**이 된다(§결정 7 이 경계하는 비용 발산). 선례 = `adr-amendment-parity` entry 가
동일하게 "PR diff forward-only, merge-base 대비" 정의역을 쓴다.
★ **그 scope 술어의 정직한 한계 (`declared`)**: "무엇이 **신규 규범 항목** 추가인가" 는 의미론적 판정이라
기계 술어로 닫히지 않는다. 기계가 판정하는 것은 "PR 이 ADR 파일을 추가·수정했는가" 까지이며,
그 안에서 규범 항목 추가 여부는 리뷰 판정 축이다. **이 술어를 `normative` 로 라벨하지 않는다.**

- **자기적용 (실측 기준)**: 본 ADR frontmatter 는 ③ 형식(carrier `plugin-codeforge#2985` + 만기
  `2026-09-15`)을 따르며 **면제 경로**로 ② 를 충족한다 — 사다리 경로가 아니다(위 천장 문단 적용 대상).
  ① 은 본 ADR 과 **같은 PR 의 `docs/evidence-checks-registry.yaml` row**(`fix-ledger-conformance`,
  `current_tier: warning`, `status: deferred-followup`)로 충족된다.

- ★ **ADR-070 §D5-C 정산 (선제 기각안 반박)**: ADR-070 `:309` 는 대안 (D5-C)
  "declaration-only retain 영역에서도 evidence-checks-registry entry append" 를
  **"registry schema scope 침해 — 실행 가능한 mechanical lint 부재 entry append 는 schema 의미 약화"**
  로 기각했다. 본 §결정 5 ① 은 그 기각안을 되살리므로 반박 없이는 상충이다. **반박 = 그 전제가 거짓이다** —
  기각 논거는 "registry schema 가 미건설 상태를 표현할 수단이 없다" 를 전제하는데,
  schema 는 `status: deferred-followup` 을 **이미 보유**하며 본 registry 안에 **14 entry 선례**가 있다
  (firsthand: `grep -c '^    status: deferred-followup' docs/evidence-checks-registry.yaml` → 14).
  미건설 자산을 가리키는 entry 는 schema 의미를 **약화**시키는 것이 아니라 미건설 사실을
  **기계 가독 형태로 고정**한다 — 문면 산문에만 남기는 쪽이 오히려 관측 불가다.
  ⇒ D5-C 는 **부분 채택**: entry append 는 하되 `status` 정직 표기를 **동반 의무**로 부과한다
  (무표기 append 였다면 ADR-070 의 기각 논거가 그대로 성립했을 것이다).

### 결정 6 — 정직 라벨 3분 + over-claim 금지

| 라벨 | 뜻 | 부착 의무 |
|---|---|---|
| `normative` | fail-closed 기계 강제 — 판정 경로를 적을 수 있음 | 판정 경로 1줄 병기 |
| `declared` | 기계 판정 불가 — human/review-verified | **왜 불가한지 사유 1줄 병기** |
| `확인 불가` | 본 lane 이 측정하지 않음 (네트워크·권한·비용) | 측정 주체 또는 이관처 1줄 병기 |

- **`advisory` 등급 신설 금지** — 선행 실패(CFP-842)가 `advisory only, blocking-on-pr 미승격` 으로 설계돼
  만들었어도 못 막을 상태였다. 필요한 것은 낮은 등급이 아니라 정직한 라벨이다.
- **억지 승격 금지 / 임의 강등 금지 대칭**: 기계 판정 불가를 `normative` 로 올리면 유령 선언이 되고,
  사용자 원 요건 유래 항목을 `declared` 로 내리면 fail-closed 강제가 약화된다. 둘 다 위반이다.
- **over-claim 어휘 금지**: "100% 기계강제" · "완전 봉인" · "hard-gate" 는 §결정 3 8항 전건 충족 ∧ 잔여 0 일 때만.
  잔여가 있으면 **잔여를 문장으로 적는다**.
- **유인 이동은 제거가 아니다**: 자기신고 분모를 파생값으로 바꾸는 완화는 유인을 **이동·가시화**시킬 뿐 봉인하지 않는다.
  그 사실을 완화 옆에 적지 않으면 "해결됨" 으로 오독된다.

### 결정 7 — 정의역 확대는 AC 신설이 아니라 사정거리 확대로 착지한다

검사가 놓친 축이 발견됐을 때의 기본 착지 = **기존 검사의 정의역 확대**이며 신규 AC·신규 게이트 신설이 아니다.

- 근거(비용): 신규 AC 는 판정 경로를 분기시켜 **어느 쪽이 exit 를 내는지 모호**해지고, 신규 게이트는
  ADR-171 §결정 6 의 **PR 누적 20 + evidence 6종** warm-up 을 새로 시작시킨다.
- 예외 = 확대할 기존 검사가 **없을 때**. 그때만 신설하며 §결정 5 admission test 를 통과해야 한다.
- 확대 시 의무: 확대 전·후 산출을 **같은 실행에서 대조**하고, 확대가 형제 검출력을 감소시키지 않음을 실증한다 —
  봉합 판정 **(가) 지정 mutant RED ∧ (나) 형제 site 회귀 0**, 둘 다 필요.
  봉합 커밋 자신이 형제 검출력을 파괴한 전례가 이 repo 에 실재한다.

### 결정 8 — 본 ADR 과 적용 carrier 의 관계

- 본 ADR = **정의·불변식 SSOT** (`owner_adr`).
- `ADR-067` Amendment 4 = FIX 닫기 조건 축의 적용 carrier.
- `ADR-171` = 신규 registry entry 의 **`carrier_adr`(framework host)** 이며 **amendment 를 받지 않는다.**
  ADR-171 §결정 5 가 신규 entry 등록 경로를 "ADR-171 amendment **또는** owner ADR 의 amendment +
  `carrier_adr` 귀속" 으로 규정하므로 후자를 택한다. 근거 = ADR-171 은 ADR-060 재제정 산물로
  **`effective_count` 재시작 0**(본문 Amendment 헤딩 0 ∧ frontmatter amendment_log 키 생략)을
  의도적으로 확보한 상태이며, entry 1건 등록을 위해 그 상태를 파기하는 것은 ADR-167 §결정 5
  compaction ratchet 대비 비용이 크다. 귀속은 registry entry 의 `owner_adr` / `carrier_adr` 필드가 운반한다.
- 적용 carrier 는 본 ADR 의 정의를 **재진술하지 않고 인용**한다 (§결정 1 말미 규율).

## 결과

**긍정**

- 참조 4곳·정의 0곳으로 죽은 `root_cause_taxonomy` 의 형상이 P/V/D 개념에서 재발하지 않는다 — 정의 착지면이 생겼다.
- `ADR-119` §결정 10② 의 "반증" 에 **정의역 축**이 붙는다. 반증 대상 선택이 저자 재량에서 선언 의무로 이동한다.
- §결정 5 가 선언-only 의 **비용을 0 에서 양수로** 만든다. registry entry·carrier·만기 없이는 선언 자체가 불가.
- §결정 7 이 AC·게이트 개수 팽창을 억제한다 — 발견마다 신규 required 를 늘리면 warm-up 비용이 발산한다.

**부정·비용**

- 본 ADR 은 Phase 1 시점에 `mechanical_enforcement_actions: []` 다. 실 checker 는 Phase 2
  (carrier `plugin-codeforge#2985` / 만기 `2026-09-15`).
  **그 사이 구간에서 본 ADR 의 강제력은 0 이며 이는 선언이다.**
- INV-D·INV-N·INV-V 는 전부 **천장을 동반**한다 (완전성 미판정 / 자기신고 하한 / 부분 소실 미검출).
  천장 문장을 지운 채 인용하면 그 순간 over-claim 이 된다.
- §결정 4 접합부는 **전집합 판정 불가**다. 새 술어 도입 시 접합 선언 의무까지만 강제한다.
- ★ **§결정 5 면제 경로가 (다)의 사정거리를 잘라낸다.** `[]` + carrier + 만기로 태어난 선언에 대해
  "그 경로가 workflow `run:` 줄에 등장하는가"(마지막 이빨)는 **평가되지 않는다.** 따라서 면제 경로를
  택한 선언은 강제 실재를 증명하지 않으며, 증명하는 것은 만기가 박혀 있다는 사실뿐이다.
  이 손실을 감수하는 이유 = 대안(면제 경로 폐지 = `len >= 1` 전면 강제)이 코퍼스 다수를 즉시
  born-red 로 만들어 **전 PR 자해 차단**이 되기 때문이며, 이는 §결정 7 이 경계하는 비용 발산이다.
  **"§결정 5 가 선언-only 를 봉인했다" 고 적으면 그 순간 over-claim 이다** — 봉인한 것이 아니라
  **비용을 0 에서 양수로 올리고 만기를 붙였다.**
- ★ **§결정 5 의 실 검사 정의역은 PR diff forward-only 이며 코퍼스 소급이 아니다.** 즉 merge-base
  시점의 기존 선언-only 는 본 ADR 로 **정리되지 않는다.** 코퍼스 실측(본 PR 시점, `archive/adr/ADR-*.md`
  174 파일 · frontmatter 파싱 기준): 키 부재 84 + 빈 리스트 53 = **137 (78.7%)** 가 사다리 경로 (가)에서
  미충족이다. 본 ADR 은 그 137 을 건드리지 않으며, **신규 저작이 138 번째가 되는 것만** 막는다.
- 새 ADR 1건 추가 자체가 "선언 1건 추가" 의 가장 값싼 형태일 위험을 진다. 그 위험은 §결정 5 를
  **본 ADR 자신에게 먼저 적용**함으로써만 상쇄되며, 상쇄 여부는 Phase 2 실행으로 판정된다.

## 관련 파일

- [ADR-067](ADR-067-fix-ledger-implementability-escalation.md) — Amendment 4 (FIX 닫기 조건 적용 carrier)
- [ADR-171](ADR-171-evidence-enforceable-promotion-framework.md) — `carrier_adr`(framework host). **amendment 0** — §결정 8 근거
- [ADR-167](ADR-167-adr-amendment-compaction-ratchet.md) — amendment compaction ratchet (ADR-171 무접촉 판정의 비용 근거)
- [ADR-119](ADR-119-research-before-claims.md) — §결정 10② 반증 규범 (본 ADR 이 정의역 축 보강)
- `docs/inter-plugin-contracts/fix-event-v1.md` — v1.6 (`원인 판정` 값공간 + 정의역 선언 필드)
- `docs/inter-plugin-contracts/dev-process-event-v1.md` — v1.1 (`root_cause_class` 원장 키)
- `docs/evidence-checks-registry.yaml` — `fix-ledger-conformance` entry (owner_adr = 본 ADR)
- `docs/domain-knowledge/concept/verification-domain-deficit.md` — 개념 서술 SSOT

## 해소 기준

N/A — permanent policy
