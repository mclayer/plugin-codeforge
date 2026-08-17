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
  - docs/evidence-checks-registry.yaml  # fix-ledger-conformance + adr-admission entry 2건 (owner_adr = 본 ADR). ★ 본 PR 실 append — 112 → 114 (설계리뷰 FIX Iter 5 정정: 직전 판 "113" 은 append 1건 누락)
  - docs/domain-knowledge/concept/verification-domain-deficit.md  # 개념 서술 SSOT (본 ADR 이 규범 SSOT)
is_transitional: false
mechanical_enforcement_actions: []  # carrier=#2985 expiry=2026-09-15 [repo=mclayer/plugin-codeforge] — ★ 고정 토큰 형식 (§결정 5 ③-dt (ii), 설계리뷰 FIX Iter 4). 앞의 세 토큰(carrier / expiry / [repo=...])만이 기계 판정 입력이며 이하 산문은 판정 정의역 밖이다 — 이 선언은 ADR-181 §결정 5 ③-dt (ii) PFX 선두 앵커 술어로 실제 배선됐다(설계리뷰 FIX Iter 4, 판별 행 18). Phase 2 이행 — scripts/lib/check_fix_ledger_conformance.py + thin wrapper + workflow twin + discriminating self-test. ★ 본 빈 리스트는 §결정 5 의 두 충족 경로 중 **면제 경로**(len==0 ∧ carrier ∧ 만기)로 ② 를 충족한다 — 사다리 경로((가)(나)(다)) 가 아니며, 따라서 "돌아가는 검사가 있다" 를 주장하지 않는다(§결정 5 면제 경로 천장 문단 참조). ① = 본 PR 의 docs/evidence-checks-registry.yaml row **2건**(fix-ledger-conformance + adr-admission, current_tier warning / status deferred-followup) 로 충족. ★ 설계리뷰 FIX Iter 5 정정 — 직전 판의 "112 → 113" 과 "grep -c → 3(정의 1 + 주석 2)" 은 **둘 다 stale** 이었다(각각 append 1건 누락 / 신설 row 의 workflow 키가 같은 파일명을 가리켜 출현이 늘었다). 정수 pin 대신 **재현 규칙**으로 적는다 — entry 수: grep -c '^  - name:' docs/evidence-checks-registry.yaml (merge-base ecfe62d63 = 112, HEAD = 그 값 + 본 PR append 분) / 문자열 출현: grep -c 'fix-ledger-conformance' docs/evidence-checks-registry.yaml (HEAD 실측 5 — 정의 1 + detect_command 1 + workflow 2 + 주석 1). 만기 경과 시 면제 경로를 잃고 사다리 경로만 남으므로 부적법 전환된다.
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
| ③ | `mechanical_enforcement_actions: []` 는 **carrier Issue 번호 + 만기일 주석 병기 시에만** 적법. ★ **주석의 위치 = 그 키와 같은 물리 줄의 trailing 주석**(아래 ③-loc) | ADR-070 계보 |

#### ★ ③-loc — "어느 주석인가" 술어 확정 (설계리뷰 FIX Iter 2 신설)

직전 판의 ③ 은 carrier·만기를 **"주석에 병기"** 라고만 적고 **어느 주석인지 말하지 않았다.** 그 미지정이
두 해석을 동시에 성립시켰고, 두 해석이 같은 파일에 정반대 판정을 내리므로 **술어가 판정 불가**였다:

| 해석 | 판정 술어 | 이 repo 실측 귀결 |
|---|---|---|
| 엄격 — 해당 키와 **같은 물리 줄**의 trailing 주석 | 아래 ③-dt (iii) 의 `LINE` 캡처 1군에서 **고정 토큰** `carrier=#` · `expiry=` 탐색 (★ FIX Iter 3 — 직전 판의 `\s` 기반 자유 텍스트 탐색은 엔진 의존 ∧ 부인 문장 통과로 폐기) | ADR-043·ADR-067 = **RED**(주석 0바이트) |
| 느슨 — frontmatter **아무 데나** carrier·만기 형식이 있으면 충족 | frontmatter 전체 텍스트에서 `#\d+` · `\d{4}-\d{2}-\d{2}` 탐색 | **hollow-GREEN** — ADR-067 frontmatter 는 `#1113`(β2 audit) · `#2957`(데드락 Issue) · `#7`(merge-time 규칙 번호), ADR-043 은 `#2686`(Epic) 을 이미 보유한다. 셋 다 **이 선언의 carrier 가 아니다** |

**채택 = 엄격 해석**(같은 물리 줄 trailing 주석). 근거 3항:

1. **느슨 해석은 항진에 수렴한다** — 위 실측처럼 amendment summary·related_cfps 주석에 박힌 무관한
   Issue 번호와 무관한 날짜(`date:` 필드 자체가 `\d{4}-\d{2}-\d{2}`)가 **거의 모든 ADR 에서** 매치한다.
   즉 느슨 술어는 대상을 가르지 못하므로 §결정 2 INV-V 가 금지하는 형상(검사가 있으나 판별력 0)이다.
2. **결속이 국소여야 정정이 국소다** — carrier·만기는 `[]` **그 값**의 시한부 사유이므로, 값과 주석이
   떨어지면 값을 채운 뒤에도 주석이 남아 stale 이 된다. 같은 줄이면 값 편집이 주석을 강제로 마주친다.
3. **기계 판정이 1줄 정규식으로 닫힌다** — frontmatter 전체 파싱·문맥 추론 없이 판정 경로가 적힌다
   (§결정 6 `normative` 부착 요건).

★ **자기적용 결과**: 본 규칙 확정으로 같은 PR 의 `ADR-043` · `ADR-067` 이 RED 였다(둘 다 `[]` + 주석 0바이트).
**두 파일에 trailing 주석을 실제로 부여**해 청산했다 — 규칙을 자기 ADR 하나에만 적용하고 형제 둘에는
적용하지 않는 비대칭이 직전 판의 결함이었다.

- **기계 판정 분해**: ①③ = `normative` (frontmatter·registry 구조 파싱). ② = **`declared`** —
  산문의 시제 판정 술어가 부재한다. 대신 ② 의 기계 대체물로
  **frontmatter `mechanical_enforcement_actions[]` 각 항목의 3단 전건**을 쓴다:
  (가) 리스트 길이 ≥ 1 (나) 각 항목이 repo 내 **실재 실행 파일**로 해석 (다) 그 경로가 workflow `run:` 줄에 **등장**.
  (다)가 마지막 이빨이다 — (나)까지면 "파일만 만들고 안 돌린다" 가 통과한다.
  ★ (나) 의 **경로 키 closed-set 은 아래 ③-dt (vii) `③-key` 가 확정**한다 (설계리뷰 FIX Iter 3 신설 —
  직전 판은 면제 가지에만 위치 술어를 주고 사다리 가지에는 주지 않아 (나)(다)가 판정 불가였다).
  ★ (나)(다)의 **술어 민감도 정직 고지**: 항목 스키마가 균질하지 않다(실측 — `action`/`status`/
  `target_section`/`script_path`/`workflow`/`detect_command` 등 dict 키 다수 + bare scalar 항목 공존).
  따라서 (나)(다) 통과 수는 **경로 추출 술어에 의존**하며 단일 정수로 고정되지 않는다.
  ★ 직전 판이 여기 적었던 **"13종"** 은 재현 실패로 **철회**한다 — 재현 명령과 두 독립 실측(35 대 36)의
  괴리 원인은 ③-dt (vii) 표에 있다. 아래 §결과의 사다리 수치는 그 사실과 함께 읽는다.

#### ★ ③ ↔ (가) 값공간 관계 선언 (§결정 4 의 자기적용 — 미선언 시 판정 불가)

③ 과 (가) 는 **같은 대상**(`frontmatter mechanical_enforcement_actions`)을 보면서 `[]` 에 정반대 값을
내린다 — ③ 은 적법, (가) 는 부적법. §결정 4 는 이런 쌍에 값공간 관계 선언을 의무화하므로 여기서 선언한다.
**미선언 상태로 두면 어느 쪽이 exit 를 내는지 결정 불가이며, 그것이 본 §결정 5 를 판정 불가로 만든다.**

| 술어 | 성격 | 정의역 | `[]` 판정 |
|---|---|---|---|
| ③ | **admission**(저작 시점 입장 조건) | 신규 규범 항목을 추가하는 **그 PR 의 diff** | carrier + 만기 병기 시 **적법** |
| (가)(나)(다) | **enforcement-reality**(강제 실재 사다리) | 동일 | 길이 0 이므로 **미충족** |

**관계 = 배타가 아니라 포괄적 OR.** ② 는 아래 둘 중 **하나**로 충족된다.

---

#### ★★ ③-dt — 술어의 매체 전환: 산문+정규식 조각 → **결정표** (설계리뷰 FIX Iter 3)

**왜 매체를 바꾸는가.** 직전 3 판은 ③ 을 **산문 + 정규식 조각**으로만 적었다. 그 결과 매 심사가
다른 독법을 채택할 수 있었고 패치는 그 라운드의 독법만 막았다 — 층이 9번 이동한 공통 기전이다.
**결정적 실물 (설계리뷰 R3, Orchestrator 가 양측 재현 → 둘 다 정확)**: 직전 판의 술어
`^mechanical_enforcement_actions:\s*\[\]\s*#(.*)$` 는 **어느 엔진·모드로 읽을지를 적지 않았고**,
그래서 같은 입력이 엔진에 따라 갈렸다.

| 입력 형태 | 행 단위 엔진 (`grep -E`) | 버퍼 단위 엔진 (Python `re.M`) |
|---|---|---|
| 같은 줄 trailing 주석 | GREEN | GREEN |
| 주석을 **다음 줄**에 배치 | RED | **GREEN** |
| 빈 줄 2개 + **3줄 아래** 무관 주석 | RED | **GREEN** |

`\s` 가 개행을 포함하므로 버퍼 단위 엔진에서는 `[]` 와 임의 거리의 주석이 **같은 줄 trailing 으로 오독**된다.
심사자 대립은 과실이 아니라 **술어 자신이 판정 불가**였던 것이다. ⇒ **원소 단위 패치를 한 번 더 하면
10번째 층이 온다.** 처분 = 술어를 **결정표(구체 입력 → 기대판정)** 로 옮기고, 정규식은 그 표를
만족하는 **구현 한 가지**로 강등한다.

**★ 이 결정표 = Phase 2 checker 의 수용 기준(acceptance criteria)이다.** checker 는 **(iv) 표의 전 행**을
**전건 재현해야** 하며, 어느 한 행이라도 어긋나면 그 checker 는 본 §결정 5 를 구현한 것이 아니다.

★ **행수를 정수로 pin 하지 않는다 (설계리뷰 FIX Iter 5, P1-1)** — 직전 판은 이 자리에 **"아래 16행"**
이라 적었는데 표는 **19행**이었다. 수용 기준이 최소치를 말하면 **어느 3행이든 빼도 문면상 적법**해진다
(자기 포함 함정과 같은 계보 — 정수를 계약으로 두면 그 정수가 ratchet-in 된다). ⇒ 정본 = **"표의 전 행"**
이며, 행수가 필요하면 **재현 규칙**으로 얻는다:

```
grep -cE '^\| (\*\*)?[0-9]+[a-z]?(\*\*)? \|' <이 파일의 (iv) 표>
```

##### (0-a) ★★★ 규범 매체의 재확정 — 정규식 **텍스트** 강등, **참조 구현** 승격 (설계리뷰 FIX Iter 5)

**왜 또 매체를 올리는가 — 실물 (firsthand)**. Iter 4 는 (i)2 의 `[ \t]` 함정을 **발견해 고쳤다.**
그런데 **바로 다음 항 (i)3 의 `[^\n]` 이 정확히 같은 함정**이었다:

```
grep -E 'a[^\n]b'    "anb" -> 0 (글자 n 을 배제)  /  "axb" -> 1  /  "a\b" -> 0
Python re a[^\n]b    "anb" -> True (개행만 배제)  /  "axb" -> True
```

POSIX ERE 는 `[^\n]` 을 **{개행 아님}이 아니라 {백슬래시·글자 `n` 아님}** 으로 읽는다. 정상형 주석의
`[repo=mclayer/plugin-codeforge]` 안 `n`(`plugin`)이 앵커를 깨므로 **문면대로 ERE 로 구현하면
행 1(정상형 카나리아)이 RED** 다. ablation 실측 — 이 문자군 **하나**를 오전사하면 **12행이 뒤집힌다**
(아래 (0-c) `CBODY` 행). 두 라운드 연속으로 **인접한 항**에서 같은 class 가 재발했다.

⇒ **개별 문자군을 고치는 방식으로는 닫히지 않는 class 다.** 규범이 정규식 **텍스트**인 한
"같은 문면, 다른 엔진" 은 구조적으로 재발한다. 처분 = **규범 매체를 3층으로 재확정**한다.

| 층 | 산출물 | 지위 | 충돌 시 |
|---|---|---|---|
| **1** | **(iv) 결정표** — 입력 바이트 → 기대 판정 | **normative (판정 SSOT)** | 최우선 |
| **2** | **참조 구현** — Python `re` + `yaml.safe_load` **단일** 구현 | **normative (유일 규정 구현)** | 표와 어긋나면 **구현이 틀렸다** |
| **3** | 본문의 정규식 텍스트 (`LINE`/`CAR`/`EXP`/`REPO`/`PFX` 블록) | **설명용 (non-normative)** | 표·구현과 어긋나면 **텍스트가 틀렸다** |

- **왜 참조 구현이 2층인가**: 표는 판정을 고정하지만 **실행되지 않는다.** 실행되는 단일 구현이 있어야
  "문면을 옮겨 적다 틀리는" 경로 자체가 사라진다. 텍스트는 그 구현을 읽기 쉽게 보여주는 주석으로 강등된다.
- ★★ **이 승격이 즉시 회수한 것 (firsthand)**: 참조 구현을 **실제로 실행**하자 표와 **2행이 어긋났다** —
  본문 텍스트만 읽던 4 라운드 동안 아무도 보지 못한 결함이다. 두 건 다 아래에서 정정한다
  (**행 8** = `mea-missing` 의 판독 계층 오류 · **행 20** = YAML 이 탭을 금지하는 위치).
  **실행되지 않는 규범은 자기 모순을 숨긴다** — 이것이 매체를 한 층 더 올린 실증 근거다.

##### (0-b) ★★ `D-CLS` — 문자군의 입장료: **2엔진 교차 행 동반 의무** (설계리뷰 FIX Iter 5 신설)

`D-LEG` 는 **leg** 이 표에 흔적 없이 들어오는 경로를 봉인했다. 그러나 `[ \t]` → `[^\n]` 연쇄가 보여준 것은
**leg 이 아니라 그 안의 문자군**이 검증 없이 들어온다는 것이다. leg 축과 문자군 축은 다르므로 규칙을 하나 더 박는다:

> **`D-CLS` (규칙)** — 본 §결정 5 의 판정 술어에 등장하는 **모든 문자군 토큰**(`[...]` 대괄호 집합 ·
> `.` · `\s`/`\d`/`\w` 류 축약)은 아래 (i-x) **문자군 교차표에 행 1개**를 가진다. 행은
> **(a) 엔진별 규정 표기 (b) 2엔진 실측 결과 (c) 오전사(transliteration) 시 무엇이 깨지는가** 를 담는다.
> **행 없는 문자군은 규정 표기가 아니다.**

- **왜 leg 규칙으로 안 되는가**: `[^\n]` 은 `LINE` leg **안**에 있고 `LINE` 은 이미 L1·L2 를 충족했다.
  즉 leg 축 검사를 전부 통과한 상태에서 문자군이 틀려 있었다. **검사 축이 다르면 통과도 따로 세야 한다.**
- **기계 판정 가능성 (`normative`)**: 술어 블록에서 문자군 토큰을 추출해 교차표 행 집합과 대조하는 것은
  문자열 연산으로 닫힌다 — `D-LEG` L2(의미론적 "판별하는가")보다 판정이 싸다.

##### (0) ★★★ `D-LEG` — 새 leg 의 입장료: **판별 행 동반 의무** (설계리뷰 FIX Iter 4 신설)

**직전 판이 고정한 것은 판정이고, 고정하지 못한 것은 판정에 들어가는 자유 변수였다.** 결정표는
매체 전환에 성공해 3자 독립 재현이 전건 일치했으나, **표와 함께 들어온 새 leg 3종**(상한 `over-cap` ·
`amendment_log` 배제 · 고정 토큰)이 다시 **산문으로만** 들어왔다. 그래서 표는 신·구 술어를 판별하면서도
**새 leg 자신은 판별하지 못했다.** 규칙으로 박는다:

> **`D-LEG` (규칙)** — 본 §결정 5 의 판정 leg 을 **신설·수정**하는 저작은 동일 PR 에서 아래 2항을
> **전건** 충족한다.
>
> **`leg` 의 리터럴 정의 (L1 자기적용 — 설계리뷰 FIX Iter 5)**:
> `leg :=` **참조 구현 `exempt()` 안에서 단독으로 exit 사유를 방출할 수 있는 판정 분기 1개**,
> 또는 **그 분기의 판정을 바꾸는 자유 변수 1개**(문자군 표기 · 계수 축 · 앵커 필드 선택).
> 즉 leg 의 외연은 산문 열거가 아니라 **참조 구현의 토글 키 집합**(`DEFAULT_LEGS`)으로 고정된다.
>
> | # | 요구 | 미충족 판정 |
> |---|---|---|
> | **L1** | **입력원을 리터럴로 지정**한다 — 그 leg 이 읽는 값의 출처를 **파일 경로 · 필드명 · 블록 경계** 수준의 리터럴로 적는다. `발행일` · `오늘` · `이슈 번호` 같은 **지시어만으로는 미충족** | 자유 변수 잔존 |
> | **L2** | ★★ **ablation 기록을 동반**한다 — 그 leg 을 **제거한 판(leg-off)과 규정판(leg-on)의 전 행 verdict 차이를 실행으로 산출**해 표로 남긴다. 차이가 **verdict 축에서 0**이면 미충족이며, 그 사실(또는 도달 불가 증명, 또는 결합 leg 지목)을 **명시**한다 | 수용 기준 아님 |
>
> **미충족 leg 은 결정표의 수용 기준이 아니다.** 근거 — checker 가 그 leg 을 **구현하지 않아도**
> 표 전건 재현이 성립하므로, 그 leg 은 "재현해야 할 것" 의 집합에 들어가 있지 않다.
> **판별하지 못하는 행은 수용 기준이 아니다** 를 leg 축으로 뒤집은 것이 `D-LEG` 다.

★★★ **L2 를 존재-assert 에서 ablation 기록으로 승격한 이유 (설계리뷰 FIX Iter 5, P0-A — 3자 전건 지목)**

직전 판의 L2 는 *"판별하는 행이 **적어도 하나** 있다"* 만 강제하고, 그 천장을 **정직하게 선언**했다.
**그 천장이 즉시 실물로 뚫렸다 (firsthand)**: `REPO` leg 을 **구현하지 않은** checker 가 19행 verdict 를
**전건 재현**한다 — 행 17은 `REPO` 없이도 RED 이고(`PFX` 가 `[repo=…]` 접미를 이미 요구하므로),
바뀌는 것은 exit 사유뿐이다(`repo-token` → `token-order`). 따라서 *"이 행이 GREEN 이면 carrier 가
repo 한정이 아니다"* 라는 근거 문장은 **거짓**이었다.

★ **이것은 R4 가 부결한 행 5 반례와 동형이며, 행 5 반례를 막으려 만든 규칙의 첫 자기적용 표 안에서 재발했다.**
★★ **교훈 — 존재-assert 는 정직하게 선언해도 존재-assert 다.** 천장 declare 는 정직성 요건을 충족시키지만
**결함을 제거하지 않는다.** "판별 행이 있다" 는 **저자가 지목**하는 명제이고, ablation 은 **실행이 산출**하는
관측이다. 전자는 틀려도 통과하고 후자는 틀리면 표에 0 이 찍힌다.

- **처분 = 지목을 실행으로 대체**. 각 leg 에 대해 `leg-on` / `leg-off` 를 **전 행에 돌려** 차이를 기록한다
  (아래 (0-c)). `REPO` 는 **중복 repo 행 17b** 로 실증했다 — 규정 RED / `REPO` 제거 시 **GREEN**.
- ★ **부수 회수 3건** — ablation 을 실제로 돌리자 **행 지목만으로는 보이지 않던 over-claim 3건**이 드러났다:
  `mea-missing` · `fm-parse-error` · `BLANK` (아래 (0-c) 주석). 세 건 다 직전 판이 "봉인한다" 고 적은 항목이다.

★ **정확한 반례가 이미 표 안에 있었다 (firsthand)**: 행 5(`expiry=9999-12-31` → RED)는 `발행일` 을
**어느 날짜로 읽든 세 독법 전부 RED** 다(9999년은 어떤 유한 상한도 초과). 즉 상한 leg 은 표에 들어왔지만
**상한을 틀리게 구현해도 행 5 는 통과**한다 — L2 미충족의 실물. 처분은 아래 (vi) 에서 `발행일` 을
리터럴 고정(L1)하고 **행 15·16 을 신설**(L2)하는 것이다.

★ **`D-LEG` 의 적용 범위**: 본 §결정 5 안의 leg 뿐 아니라, 본 ADR 을 인용하는 **적용 carrier** 가
자기 절에서 신설하는 판정 leg 에도 적용된다. 그 경우 L2 의 착지처는 (iv) 결정표가 아니라
**그 절 자신의 대조군 표**다 (예 — CFP-2985 Change Plan §8.D 의 양성/음성/신규 leg 는 §8.D 대조군 표에 착지).

★ **`D-LEG`·`D-CLS` 자신의 자기면제 근거 (설계리뷰 FIX Iter 5, P1-5 — 명시 의무)**: 두 규칙은
§결정 5 의 **판정 leg 이 아니라 저작 규칙(meta)** 이다 — 위 `leg :=` 정의상 `exempt()` 의 exit 사유를
방출하지 않으므로 leg 의 외연 밖이다. **자기적용이 성립하지 않는 이유는 무한 후퇴다**:
`D-LEG` 에 L2 를 적용하려면 "`D-LEG` 를 제거한 판" 의 전 행 verdict 차이를 재야 하는데,
`D-LEG` 제거는 verdict 를 바꾸지 않고 **표의 행 집합 자체**를 바꾼다. 즉 측정 대상(표)이 측정 규칙에
의존해 **고정점이 없다.** ⇒ 자기적용 대신 **다른 축의 반증 가능성**을 둔다 —
*"`D-LEG` 도입 후 신설된 leg 중 ablation 기록 없이 들어온 것이 있는가"*. 이번 판 실측 = **0**
(아래 (0-c) 표가 `DEFAULT_LEGS` 전 키를 덮는다). 이 명제는 거짓일 수 있으므로 검사연극이 아니다.

★ **`D-LEG` 의 천장 (`declared`)**: L2 는 ablation 승격 후에도 **알려진 표 행에 대한 차이**만 잰다.
leg 의 **모든 오독 방식**을 판별하는 행 집합을 요구하지 않는다 — 오독 공간은 열거로 닫히지 않기 때문이다
((viii) 결정표 천장과 같은 근거). 개선된 것은 **"leg 이 표에 흔적을 남기지 않고 들어오는 경로"의 봉인**과
**"저자가 지목한 판별력" 을 "실행이 산출한 판별력" 으로 교체**한 것이며, 완전성이 아니다.

##### (0-c) ★★★ leg ablation 기록 (L2 이행 — firsthand 전건 실행)

**산출 방법**: 참조 구현의 `DEFAULT_LEGS` 키를 하나씩 끄고 **(iv) 표 전 행**을 재실행해
`(verdict, exit사유)` 가 규정판과 달라지는 행을 모은다. 실행일 pin = `2026-08-17`.

| leg-off | 뒤집힌 행 수 | 뒤집힌 행 (`on` -> `off`) | verdict 축 판별 |
|---|---|---|---|
| `SCOPE` | 1 | 19: `GREEN` -> `RED/line-form` | ✓ |
| `LINE`(정확히 1회) | 1 | 22: `RED/line-form` -> `GREEN` | ✓ |
| `MEA` | 1 | 10: `RED/mea-missing` -> `RED/line-form` | ✗ **사유만** |
| `CAR` | 2 | 6: 사유만 · **11: `RED` -> `GREEN`** | ✓ |
| `EXP` | 1 | 12: `RED` -> `GREEN` | ✓ |
| `REPO` | 2 | 17: 사유만(`repo-token`->`token-order`) · **17b: `RED` -> `GREEN`** | ✓ (**17b 로만**) |
| `PFX` | 1 | 18: `RED` -> `GREEN` | ✓ |
| `EXPIRED` | 1 | 13: `RED` -> `GREEN` | ✓ |
| `OVERCAP` | 2 | 5 · 15: `RED` -> `GREEN` | ✓ |
| `FMPARSE` | 2 | 14 · 20: `fm-parse-error` -> `mea-missing` | ✗ **사유만** |
| `BLANK` (`LINE` 공백군) | **0** | — | ✗ **도달 불가 (아래)** |
| `BLANK_PFX` (`PFX` 공백군) | 1 | 21: `GREEN` -> `RED/token-order` | ✓ |
| `CBODY` (주석 본문군) | **12** | 1 · 5 · 6 · 11 · 12 · 13 · 15 · 16 · 17b · 18 · 19 · 21 (**1·16·19·21 은 `GREEN` -> `RED`**) | ✓ |
| `COUNT` (출현 -> 존재) | 3 | 11 · 12 · 17b: `RED` -> `GREEN` | ✓ |
| `PUBDATE` = 최신 amendment | 2 | 15: `RED`->`GREEN` · 16: `GREEN`->`RED` | ✓ **양방향** |
| `PUBDATE` = 실행일 | 1 | 15: `RED` -> `GREEN` | ✓ |

★★ **단독 ablation 이 verdict 를 못 바꾼 3건 = 직전 판이 "봉인한다" 고 적은 항목들이다.** 정직 정산:

| leg | 직전 판의 주장 | **실측** | 정정 |
|---|---|---|---|
| `MEA` (`mea-missing`) | "가장 싼 회피구(**키 삭제**) 봉인" | 키를 지워도 `LINE` 이 이미 RED — 바뀌는 것은 **exit 사유뿐** | 봉인이 아니라 **진단 정밀화**. `LINE` 과 **중복 방어**이며 그 사실을 적는다 |
| `FMPARSE` | "파싱 실패를 skip 으로 두면 회피구" | 단독 off 는 `MEA` 가 받아내 여전히 RED | **`MEA` 와 결합 방어**. 아래 쌍 ablation 이 실제 회피구를 보인다 |
| `BLANK` | (`[[:blank:]]` 표기 leg) | 판별 행 **0** — 신설 불가 | **YAML 구조적 도달 불가** (아래 (0-d)) |

★ **쌍 ablation — 단독으로는 사유만 바뀌던 leg 이 결합 시 실제 회피구를 연다 (firsthand)**:

| leg-off 쌍 | `GREEN` 화되는 행 | 뜻 |
|---|---|---|
| `FMPARSE` + `MEA` | **14 · 20** | ★ 실제 회피구 — frontmatter 를 깨뜨리면 통과. 두 leg 이 **함께** 막는다 |
| `MEA` + `LINE`(정확히 1회) | 22 | 키 줄을 2회 적어 첫 줄만 읽히게 하는 경로 |
| `REPO` + `PFX` | 17 · 17b · 18 | repo 동일성 축 전체 소실 |
| `CAR` + `PFX` | 11 · 18 | carrier 계수 축 소실 |

⇒ **정직 결론**: `MEA` · `FMPARSE` 는 **독립 leg 이 아니라 중복 방어 쌍**이다. 각각이 단독으로 회피구를
봉인한다고 적으면 over-claim 이고, **둘 중 하나만 구현한 checker 도 표를 전건 재현**한다. 이 사실을
여기 적어 두 leg 의 지위를 정직하게 고정한다 — 지우고 인용하면 over-claim 이다.

##### (0-d) ★★ `BLANK` leg 은 판별 행이 **없는 것이 아니라 있을 수 없다** (P1-4 처분)

P1-4 는 *"`[[:blank:]]` leg 에 판별 행 0 — 탭 포함 판별 행 신설"* 을 요구했다. **신설을 시도해 실패했고,
실패가 정답이었다 (firsthand)**:

```
yaml.safe_load 로 각 위치의 탭을 실측 (frontmatter 1블록)
  K: []<TAB># c      -> ScannerError   (LINE 의 값-주석 사이)
  K:<TAB>[]  # c     -> ScannerError   (LINE 의 키-값 사이)
  K: []  #<TAB>c     -> PARSE-OK       (주석 본문 안)
  "K": []  # c       -> PARSE-OK       (인용 키)
```

**YAML 은 `LINE` 의 공백군이 놓인 두 위치에서 정확히 탭을 금지한다.** 그러므로 `LINE` 의 탭 half 를
행사하는 입력은 **`FMPARSE` 가 먼저 `fm-parse-error` RED 를 내며**, 어떤 입력으로도 `GREEN` 이 될 수 없다.
⇒ 판별 행 0 은 **커버리지 공백이 아니라 도달 불가의 증명**이다. 그 증명을 **행 20**(`RED/fm-parse-error`)으로
표에 고정한다 — 도달 불가를 주장만 하지 않고 **행으로 못 박는다**.

★★ **여기서 걸러진 함정**: P1-4 를 문면대로 이행해 "탭 포함 행 = GREEN" 을 신설했다면 그 행은
**`fm-parse-error` 로 RED** 가 되어 기대와 어긋났을 것이고, 기대를 `RED` 로 맞추면 **`BLANK` 와 무관한
이유로 RED 인 행**이 "탭 leg 판별 행" 으로 표에 앉는다 — 이 Story 가 5 라운드 내내 고발한 hollow oracle 그 자체다.
★ **탭 half 가 실제로 살아 있는 곳은 `PFX`** 다(주석 본문 = YAML 이 탭을 허용하는 유일 위치).
그래서 `BLANK_PFX` 는 **행 21** 로 정상 판별된다. ⇒ **공백군 leg 을 위치별로 분해**했고, 한쪽은 도달 불가,
한쪽은 판별 행 보유다. 분해 전에는 두 사실이 하나의 "`[[:blank:]]` leg" 으로 뭉쳐 있어 어느 쪽도 보이지 않았다.

##### (i) 판독 엔진·모드 명시 — 엔진 비의존 재현 조건 (★ FIX Iter 4 전면 재작성)

정규식만 적는 것으로는 부족하다. **어느 엔진에서든 아래 표를 재현하려면 다음 4항을 지켜야 한다.**

1. **모드 = multiline**(`^` `$` 가 줄 경계). `DOTALL` **금지**.
   ★ **`SCOPE` 와 `DOTALL` 금지는 충돌하지 않는다 (FIX Iter 5 확인, P2-5)** — `SCOPE`(frontmatter 절단)는
   **정규식이 아니라 블록 절단**이며 두 엔진 모두 정규식 밖에서 수행한다((i-x-B) 첫 행). 즉 `DOTALL` 이
   지배하는 축(`.` 의 개행 포섭)과 `SCOPE` 가 지배하는 축(검사 대상 문자열의 범위)이 **disjoint** 하다.
   ★ 오히려 `SCOPE` 는 `DOTALL` 금지를 **덜 중요하게** 만든다 — 검사 문자열이 frontmatter 로 좁혀지면
   개행을 넘나드는 오매치의 사정거리도 그만큼 줄기 때문이다. 다만 그것은 **완화이지 대체가 아니며**,
   `DOTALL` 금지는 그대로 유지한다(frontmatter 안에도 개행은 있다).
2. **공백 문자군 = 스페이스(U+0020)와 탭(U+0009) 2문자만. `\s` 금지.**
   `\s` 는 개행을 포함하므로 행 3·4 를 GREEN 으로 만든다 — 행 단위 엔진에서는 우연히 RED 지만
   버퍼 단위 엔진에서는 GREEN 이라 **판정이 엔진에 의존**한다.
   ★★ **표기는 엔진마다 다르며, 직전 판의 `[ \t]` 는 POSIX ERE 에서 틀린다 (firsthand)**:

   ```
   grep -E 'a[ \t]b'        실제 탭 -> 0 (허용하려던 것을 못 잡음)
                            글자 t  -> 1 (의도한 적 없는 것을 잡음)
   grep -E 'a[[:blank:]]b'  실제 탭 -> 1 / 글자 t -> 0   (정상)
   ```

   ERE 는 `\t` 이스케이프를 해석하지 않아 `[ \t]` 를 **{스페이스, 백슬래시, 문자 t}** 집합으로 읽는다.
   ⇒ **규정 표기 = POSIX ERE `[[:blank:]]` / Python·PCRE `[ \t]`**(여기서 `\t` 는 실제 탭). 두 표기는
   같은 2문자 집합을 가리키며, **어느 하나를 다른 엔진에 그대로 옮겨 쓰면 안 된다**(Python `re` 는
   `[[:blank:]]` 를 POSIX 클래스로 해석하지 않는다).
3. ★★ **주석 본문 문자군 — 불변식은 "개행에 도달하지 못한다" 이고, 표기는 엔진별이다**
   (설계리뷰 FIX Iter 5 전면 정정 — 직전 판의 *"`[^\n]` 만, `.` 금지"* 는 **ERE 에서 틀린다**).

   ```
   grep -E 'a[^\n]b'    "anb" -> 0   "axb" -> 1   "a\b" -> 0     (글자 n·백슬래시를 배제)
   Python re a[^\n]b    "anb" -> True  "axb" -> True             (개행만 배제)
   ```

   ⇒ **규정 표기 = POSIX ERE `.` / Python·PCRE `[^\n]`**(+ `DOTALL` 금지). 근거가 엔진마다 다르다:
   - **ERE(`grep`)에서 `.` 이 안전한 이유는 정규식 의미가 아니라 버퍼 구조다** — `grep` 은 입력을
     행 단위로 잘라 넘기므로 개행이 애초에 버퍼에 없다. 즉 `.` 은 **구조적으로** 개행에 도달 불가다.
   - **Python 에서 `.` 이 위험한 이유는 `DOTALL` 이 켜질 수 있기 때문**이다. 그래서 Python 가지는
     `DOTALL`-면역인 `[^\n]` 을 쓴다.
   - ★ **오전사 비용 실측 (firsthand)**: ERE 가지의 `.` 을 `[^\n]` 으로 옮겨 적으면 정상형 주석의
     `[repo=mclayer/plugin-codeforge]` 안 `n`(`plugin`)이 앵커를 깨 **14행이 뒤집히고 행 1(정상형)이 RED** 다.
     Python 가지에서 `[^\n]` 을 ERE 문면으로 오전사한 경우도 동일하게 **14행 뒤집힘**((0-c) `CBODY`).
   - **이 항은 `D-CLS` 의 첫 적용 대상**이며 아래 (i-x) 문자군 교차표 3행이 그 기록이다.
4. ★ **계수는 행 계수가 아니라 출현 계수다.** `grep -c` 는 **매치한 줄 수**를 센다 —
   firsthand: `carrier=#2985 carrier=#1` 한 줄에서 `grep -cE 'carrier=#[1-9][0-9]{0,6}'` → **1**,
   `grep -oE … | wc -l` → **2**. 행 계수를 쓰면 **행 11·12(중복 토큰 = RED)가 통과**하고,
   중복 만기로 창을 연장하는 경로(행 12 가 막으려던 바로 그것)가 열린다.
   ⇒ 정본 = `grep -o … | wc -l` 또는 Python `len(re.findall(...))`.

즉 **개행을 먹을 수 있는 문자군을 술어에서 전부 제거**하는 것이 행 3·4 를 RED 로 만드는 기제이고,
**계수 축을 행에서 출현으로 옮기는 것**이 행 11·12 를 RED 로 만드는 기제다.

###### (i-x) ★★ 2엔진 교차 — **문자군 축**(`D-CLS`) + **leg 축**(`D-LEG`) 분리 (FIX Iter 5 전면 재작성)

직전 판은 두 축을 한 표에 섞어 두었고, 그래서 **leg 축을 전부 통과한 상태에서 문자군이 틀려 있었다.**
축을 나눠 각각 전수 기재한다. ★ **ERE 가지의 지위 = 규범 구현이 아니라 이식 부록(portability annex)**
— 그 존재 이유는 **표기 오전사를 잡는 차분 오라클**이며, 실제로 `[ \t]`(Iter 4)와 `[^\n]`(Iter 5)을 잡아냈다.

**(i-x-A) 문자군 교차표 (`D-CLS` 이행 — 술어에 등장하는 전 문자군)**

| 문자군 | 쓰이는 곳 | POSIX ERE 규정 표기 | Python `re` 규정 표기 | 오전사 시 무엇이 깨지는가 (firsthand) |
|---|---|---|---|---|
| 공백군 | `LINE` 의 키-값·값-주석 사이 | `[[:blank:]]` | `[ \t]` (실제 탭) | ERE 에서 `[ \t]` = {스페이스, `\`, 글자 `t`} — 실탭 미매치 ∧ 글자 t 오매치 |
| 공백군 | `PFX` 의 토큰 사이 | `[[:blank:]]` | `[ \t]` | 동상. **행 21 이 판별** ((0-c) `BLANK_PFX`) |
| **주석 본문군** | 캡처 `c` | ★ **`.`** (행 단위 버퍼 = 개행 도달 불가) | ★ **`[^\n]`** (+ `DOTALL` 금지) | ★★ 서로 옮겨 적으면 **14행 뒤집힘 · 행 1 born-red** |
| 숫자군 | `carrier` · `expiry` | `[0-9]` | `[0-9]` | `\d` 금지 — Python 에서 유니코드 숫자까지 먹는다 |
| 토큰 경계군 | lookaround 대체 / lookbehind 안 | `[^0-9A-Za-z_-]` | `[^0-9A-Za-z_-]` | 동치 (부정 집합이라 엔진 차 없음) |
| repo 문자군 | `[repo=owner/name]` | `[A-Za-z0-9_.-]` | `[A-Za-z0-9_.-]` | 집합 안 `.` 은 리터럴 — 밖으로 빼면 임의문자 |

★ **`.` 의 채택 여부 = 엔진별로 정반대이며 그것이 정답이다** — ERE 가지 **채택**(구조적 안전),
Python 가지 **금지**(`DOTALL` 위험). 직전 판의 무조건 *"`.` 금지"* 는 Python 근거를 ERE 에 그대로
옮긴 것이었고, 그것이 바로 이 표가 막으려는 오전사다.

**(i-x-B) leg 교차표 (누락 3종 편입 — P0-C 조치 3 / P2-4)**

| leg | POSIX ERE + shell 재현 | Python `re` + `yaml` 재현 | 교차 결과 |
|---|---|---|---|
| ★ `SCOPE` (frontmatter 절단) | **정규식 아님** — `awk 'NR==1 && /^---$/ {f=1;next} f && /^---$/ {exit} f'` | 줄 배열 절단 | 동치 (**양쪽 다 정규식 밖** — 직전 판은 이 leg 을 교차표에 아예 안 넣었다) |
| ★ **캡처 `c` 추출** | ★★ **named capture 부재** → `grep -E` 로 줄을 고른 뒤 `sed -E 's/^…#//'` **치환**으로 대체 | `(?P<c>…)` 캡처 | ★★ **기전이 다르다** (매치-후-치환 vs 캡처). ★ **R3 엔진 분열의 원 기전이 이 칸의 미규정이었다** |
| ★ `mea-missing` (키 부재) | **근사만** — `grep -cE '^"?mechanical_enforcement_actions"?:'` (표기 변형을 손으로 열거) | `"mechanical_enforcement_actions" in yaml.safe_load(fm)` | ★ **비동치** — ERE 는 *표기* 열거, Python 은 *YAML 의미*. 현 fixture 집합에서만 우연히 일치 |
| `LINE` (줄 형태) | 가능 — `[[:blank:]]` + `.` | 가능 — `[ \t]` + `[^\n]` | 동치 (표기만 다름) |
| `CAR` / `EXP` (출현 계수) | lookaround 부재 → 2패스 우회 (아래) | lookbehind/lookahead | 동치 |
| `REPO` (repo 토큰) | 가능 (경계가 `[` `]` 리터럴이라 lookaround 불요) | 가능 | 동치 |
| `PFX` (선두 배치) | 가능 (`^` 앵커) | 가능 | 동치 |
| ★ `fm-parse-error` | ★★ **구현 불가** — shell 에 YAML 파서 부재 | `yaml.safe_load` + `try/except` | ★★ **비동치 · ERE 가지가 `GREEN` 으로 fail-open** (행 14·20 실측) |
| `over-cap` 의 발행일 | 근사 — `grep -E '^date:'` + `date -u -d` | `yaml.safe_load(fm)["date"]` | 근사 (표기 의존) |
| 계수 축 | `grep -o` 출현 목록 → `wc -l` (`grep -c` 금지 — 행 계수) | `len(re.findall())` | 동치 |
| 날짜 비교 | `sort` 사전순 (ISO 8601 이라 성립) + `date -u -d` | `date.fromisoformat` | 동치 |

★★ **2엔진 차분 실행 결과 (firsthand, 본 판 저작 시점)**: (iv) 표 **전 25행**을 두 구현으로 각각 돌려
`(verdict, exit사유)` 를 비교했다 — **일치 23 / 불일치 2**. 불일치는 **행 14 · 20** 이고 **둘 다
`fm-parse-error`** 이며 **ERE 가지가 `GREEN`(fail-open)** 이다.

⇒ ★★★ **이 2행이 ERE 가지를 규범에서 내리는 결정적 근거다.** "엔진 비의존" 은 표기 층에서만 참이고,
**파서 층에서는 ERE 가지가 원리적으로 도달할 수 없다.** 직전 판이 *"2엔진 18/18"* 이라 적을 수 있었던 것은
행 14 를 *"정규식 술어 밖"* 으로 **정의역에서 빼 두었기** 때문이며, 정의역을 좁혀 얻은 일치를
엔진 동치의 근거로 쓴 것이다 — 이 Story 가 반복 고발한 **검사 정의역 협착**의 자기 실례다.

★ **정직 고지 (`declared`)**: "엔진 비의존" 은 이제 다음만 뜻한다 — **(iv) 표의 정규식-판정 가능 부분집합
(23행)에 대해 두 구현이 일치한다.** 파서 층(2행)은 불일치이며, **전 행 재현은 참조 구현만 달성한다.**

★★ **`CAR`/`EXP` 의 ERE 2패스 우회 — 수용 기준 leg 이 아니라 robustness 선택으로 강등한다**
(설계리뷰 FIX Iter 5, P1-3 정정)

**직전 판의 채택 근거가 결정표와 어긋나 있었다**: (i-x) 가 1패스를 기각한 두 칸(*"행 11 인접 중복"* ·
*"8자리"*)은 **결정표 행이 아닌 입력**에서 나왔다 — **행 11 의 두 `carrier` 토큰은 비인접**이고
8자리 입력은 표에 아예 없었다. ⇒ 처분으로 **두 입력을 실제 행으로 신설**했다(**행 23** 인접 중복 ·
**행 24** 8자리). 그 뒤 ablation 을 돌린 결과:

> **2패스 → 1패스 (a)형 으로 되돌리면 뒤집히는 행 = 1개(행 23)이며, 그것도 `verdict` 가 아니라
> `exit 사유`뿐이다** (`carrier-token` → `token-order`). **`verdict` 축 판별 = 0.**

**원인** — `PFX` 가 `carrier=#N` **직후 공백 + `expiry=`** 를 독립 요구하므로, 인접 중복도 8자리 초과도
`PFX` 에서 이미 걸린다. 즉 2패스는 **`PFX` 와 중복 방어**이며 단독 판별력이 없다.

⇒ **정직 강등**: 2패스는 **exit 사유의 정확성을 위한 robustness 선택**이지 수용 기준 leg 이 아니다.
1패스로 구현한 checker 도 **(iv) 표를 전건 재현**하며, 그 사실을 숨기지 않는다.
★ 이 강등은 `D-LEG` L2 를 ablation 으로 승격한 덕에 **드러났다** — 존재-assert 였다면 "행 23 이 판별한다"
로 통과했을 것이다(행 23 은 실제로 1패스에서 값이 바뀌므로). **verdict 축을 명시한 것이 차이를 만들었다.**

| ERE 시도 | 행 6 (`non-carrier=#3`) | **행 23** (인접 중복) | **행 24** (8자리) | 판정 |
|---|---|---|---|---|
| 경계 없음 `carrier=#[1-9][0-9]{0,6}` | **1 (오탐)** | 2 | 1 (오탐) | ✗ |
| 앞뒤 **양쪽** 경계 교대 — 아래 (a) 형 | 0 | **1 (인접 소비)** | 1 | 사유만 어긋남 |
| ★ **선행 경계만** + **자릿수 초과 별도 패스** — 아래 (b) 형 | 0 | **2** | **초과 패스가 1 → RED** | ★ 채택 (robustness) |

```
# (a) 부적합 — 후행 경계까지 소비해 인접 토큰이 1로 셈된다
grep -oE '(^|[^0-9A-Za-z_-])carrier=#[1-9][0-9]{0,6}([^0-9]|$)'

# (b) 채택 — 패스 1: 출현 계수 (선행 경계만 소비하므로 인접 토큰이 살아남는다)
grep -oE '(^|[^0-9A-Za-z_-])carrier=#[1-9][0-9]{0,6}' | wc -l      # == 1 이어야 함
#     패스 2: 자릿수 초과 탐지 (7자리 상한 위반)
grep -oE '(^|[^0-9A-Za-z_-])carrier=#[0-9]{8}' | wc -l             # == 0 이어야 함
```

- **왜 패스 2 가 따로 필요한가**: 후행 경계를 패턴에 넣으면 `-o` 가 구분자를 먹어 **인접 중복이 1로 셈**된다
  (위 표 2행). 후행 경계를 빼면 `carrier=#12345678` 이 앞 7자리만 매치해 통과한다. 두 요구가
  단일 ERE 패스에서 양립하지 않으므로 **축을 나눈다.**
- ★ **`grep -P`(PCRE lookaround) 는 규정 구현으로 두지 않는다** — 본 개발 환경에서 **미가용**이다
  (firsthand: `grep -P 'x' /dev/null >/dev/null 2>&1; echo $?` → **2**). 가용성이 환경에 의존하는
  경로를 수용 기준의 유일 실현으로 삼으면 재현 조건이 환경 의존이 된다.
- ★ **정직 고지 (`declared`)**: "엔진 비의존" 은 **표를 재현하는 실현이 각 엔진에 존재한다** 는 뜻이지
  **같은 정규식 문자열이 두 엔진에서 동작한다** 는 뜻이 아니다. 직전 판은 이 둘을 구분하지 않았다.
  ★ **Iter 5 추가 정정** — 그 진술조차 **파서 층에서는 거짓**이다. ERE 가지에는 `fm-parse-error` 를
  재현하는 실현이 **존재하지 않는다**(위 (i-x-B)). 따라서 정확한 진술은
  **"정규식-판정 가능 부분집합에 한해 각 엔진에 실현이 존재한다"** 이다.

##### (ii) 고정 토큰 형식 — 자유 텍스트 탐색 폐기

직전 판은 trailing 주석 **안 아무 데나** `#\d+` 와 `\d{4}-\d{2}-\d{2}` 를 찾았다. 그 주석은
**산문**이다 — firsthand 실측 길이: `ADR-067` **658자** · `ADR-181` **599자** · `ADR-043` **557자**.
산문 안 자유 탐색은 **부인 문장도 통과**시킨다(행 6). ⇒ **key=value 고정 토큰**으로 전환한다.

★★ **아래 블록의 지위 = (0-a) 3층 중 층 3 — 설명용(non-normative)** (FIX Iter 5).
판정 SSOT 는 (iv) 결정표이고, 유일 규정 구현은 Python `re` + `yaml.safe_load` 참조 구현이다.
**이 텍스트가 표·참조 구현과 어긋나면 어긋난 쪽은 이 텍스트다.**

```
# 아래는 Python·PCRE 표기다 (설명용). POSIX ERE 표기는 (i) 3·4항 + (i-x-A) 문자군 교차표를 따른다.
SCOPE:= 파일 선두 frontmatter 블록 (1행 `---` 부터 다음 단독 `---` 직전까지)   # ★ FIX Iter 4 — 파일 전체 아님
LINE := ^mechanical_enforcement_actions:[ \t]*\[\][ \t]*#(?P<c>[^\n]*)$      # SCOPE 안에서만, multiline, DOTALL 금지
CAR  := (?<![0-9A-Za-z_-])carrier=#(?P<n>[1-9][0-9]{0,6})(?![0-9])           # 캡처 c 안에서만
EXP  := (?<![0-9A-Za-z_-])expiry=(?P<d>[0-9]{4}-[0-9]{2}-[0-9]{2})(?![0-9])  # 캡처 c 안에서만
REPO := (?<![0-9A-Za-z_-])\[repo=(?P<r>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\]    # 캡처 c 안에서만  ★ FIX Iter 4 신설
PFX  := ^[ \t]*carrier=#[1-9][0-9]{0,6}[ \t]+expiry=[0-9]{4}-[0-9]{2}-[0-9]{2}[ \t]+\[repo=[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\]
                                                                             # 캡처 c 의 **선두**에 앵커  ★ FIX Iter 4 신설
```

- **왜 lookbehind/lookahead 가 붙는가**: 접두 없는 `carrier=#` 는 산문 안 `…non-carrier=#3…` 같은
  우연 매치를 허용한다. 경계를 박아 **토큰이 토큰으로만 읽히게** 한다.
- **왜 캡처 `c` 안에서만 찾는가**: 파일 전체에서 찾으면 ③-loc 의 국소성이 즉시 무너진다.
- ★★ **`SCOPE` 신설 — `LINE` 의 정의역이 파일 전체였다 (`D-LEG` L1 적용, FIX Iter 4)**.
  직전 판은 "`LINE` 이 **file 전체**에서 정확히 1회 매치" 라고 적었다. 그러면 **본문에 형식 예시를
  열 0 코드블록으로 적는 순간 매치가 1→2 로 늘어 자기 파일이 RED** 가 된다. 현행이 GREEN 인 것은
  결정표 리터럴이 **표 셀·blockquote 안이라 `| ` 접두가 붙는다는 우연**에 의존했다.
  ⇒ 정의역을 **frontmatter 블록**으로 좁힌다. 두 결함이 동시에 닫힌다 — (a) 본문 col-0 예시로 인한
  self-RED (b) **자기 형식을 코드펜스로 예시할 수 없다**는 저작 제약(형식을 정의하는 문서가 그 형식을
  보여주지 못하는 상태). **판별 행 = 행 19**(본문 col-0 코드블록에 정상형 1줄 추가 → frontmatter 정의역이면
  GREEN, 파일 전체 정의역이면 `line-form` RED). firsthand 매치 수: 파일 전체 **2** / frontmatter **1**.
- ★★ **`REPO` 신설 — carrier 가 형식만 검증됐다 (`D-LEG` L1/L2 적용, FIX Iter 4)**.
  firsthand: `carrier=#9999999` · `carrier=#1` 둘 다 `CAR` 를 통과한다(각각 매치 1). 즉 술어는
  **번호가 형식에 맞는가**만 보고 **그 번호가 무엇인가**를 보지 않았다. 반면 실제 3 ADR 은 전부
  `[repo=mclayer/plugin-codeforge]` 접미를 이미 쓰고 있었는데(firsthand 3/3) **술어에 그 토큰이 없었다** —
  R3 이 지목한 "셋 다 이 선언의 carrier 가 아니다" 가 **위치만 고쳐지고 동일성은 미해결**로 남은 자리다.
  ⇒ carrier 를 **repo 한정(repo-qualified)** 으로 만든다. **판별 행 = 행 17**(repo 토큰 제거 → `repo-token` RED).
  ★★ **천장 (`declared`) — 직전 판의 천장 문장 자체가 over-claim 이었다 (FIX Iter 5, P1-2)**:
  직전 판은 *"현재 봉인된 것은 아무 숫자나 쓰기가 아니라 **아무 repo 나 가리키기** 다"* 라 적었다.
  **거짓이다 (firsthand)** — 임의 `owner/name` 이 전부 통과한다:

  ```
  [repo=mclayer/plugin-codeforge] -> GREEN     [repo=evil/nonexistent]      -> GREEN
  [repo=mclayer/plugin-codeforg]  -> GREEN     [repo=a/b] · [repo=0/0]      -> GREEN
  ```

  ⇒ **정본 천장**: `REPO` 가 봉인하는 것은 **repo 토큰의 부재**뿐이다. *어느* repo 인지는 검사하지 않으므로
  오타 repo·존재하지 않는 repo·타인 repo 가 모두 통과한다. `REPO` 의 실제 이득은 **주석 형태를
  `owner/name` 을 포함한 3-토큰 정규형으로 강제**해 산문 매설을 어렵게 만드는 것이며, **동일성 검증이 아니다.**
  "그 번호의 Issue 가 그 repo 에 실재하는가" 는 물론이고 **"그 repo 가 이 repo 인가"** 조차
  Phase 2 이관 대상이다(carrier `#2985` / 만기 2026-09-15). 이 문단을 지우고 인용하면 over-claim 이다.
  ★ **왜 지금 리터럴 고정을 안 하는가**: 술어에 `mclayer/plugin-codeforge` 를 박으면 consumer repo 에서
  본 ADR 을 재사용할 수 없다. 값 고정은 checker 설정 축이지 술어 축이 아니다 — 그 분리를 여기 적는다.
- ★★ **`PFX` 신설 — "선두 배치" 선언이 미배선이었다 (`D-LEG` L1/L2 적용, FIX Iter 4)**.
  현행 3 ADR 의 주석은 "**앞의 두 토큰만이 기계 판정 입력이며 이하 산문은 판정 정의역 밖이다**" 라고
  선언하는데, 직전 술어는 **캡처 `c` 전체**에서 토큰을 찾았다 — 즉 **부인 산문 한가운데에 토큰을 매설해도
  GREEN** 이었다. 선언이 술어에 걸려 있지 않았다. ⇒ 선두 앵커를 술어로 만든다.
  **판별 행 = 행 18**(토큰 앞에 산문 삽입 → `token-order` RED).
  ★ **접미 산문은 여전히 허용**이며 그것이 선언의 내용이다(판정 입력 아님). 접미에 무효 토큰을 덧붙이는
  경로는 `PFX` 가 아니라 **`CAR`/`EXP` 의 "캡처 `c` 전체에서 정확히 1회"** 가 막는다(행 11·12) —
  두 leg 이 선두와 접미를 나눠 맡는다.

##### (iii) 판정 술어 = **참조 구현** (층 2 — normative)

★★ **평가 순서가 leg 목록의 일부다** (FIX Iter 5) — 직전 판은 `mea-missing` 을 `line-form` 주석에
곁들여 적었을 뿐 **어느 것이 먼저 exit 하는지 적지 않았고**, 그래서 exit 사유가 구현마다 갈렸다.
아래 순서가 규정이며 (iv) 표의 exit 사유 열이 그 순서의 관측이다.

★★ **`mea-missing` 의 판독 계층 정정 (FIX Iter 5 — 참조 구현 실행이 잡아낸 2건 중 1건)**:
직전 판의 `mea-missing` 은 **행 정규식**(`^mechanical_enforcement_actions:`)이었다. 그러면
**행 8(인용 키 `"K": []`)** 이 `mea-missing` 으로 exit 해 표의 기대(`line-form`)와 어긋난다 —
YAML 상 키는 **존재**하는데 정규식은 부재라고 답하기 때문이다. ⇒ **키 존재 판정을 `yaml.safe_load`
결과의 키 멤버십으로 옮긴다.** 같은 처분이 §8.D `N3` 에서도 독립적으로 필요했다(둘 다 "물리 줄 문자열"을
"파싱값" 으로 올리는 동형 처분).

```
exempt(file) :=
      frontmatter YAML 파싱 성공                     # 실패 = RED                 [fm-parse-error]
  AND "mechanical_enforcement_actions" in 파싱값      # 키 부재 = RED              [mea-missing]
                                                     # ★ 정규식 아님 — YAML 키 멤버십
  AND LINE 이 SCOPE(frontmatter 블록) 안에서 정확히 1회 매치   # 0/2+ = RED   [line-form]
  AND CAR 이 캡처 c 안에서 정확히 1회 **출현**     # 0회 = RED / 2회 이상 = RED  [carrier-token]
  AND EXP 이 캡처 c 안에서 정확히 1회 **출현**     # 0회 = RED / 2회 이상 = RED  [expiry-token]
  AND REPO 가 캡처 c 안에서 정확히 1회 **출현**    # 0회 = RED / 2회 이상 = RED  [repo-token]
  AND PFX 가 캡처 c 의 **선두**에 매치             # 미매치 = RED               [token-order]
  AND date.fromisoformat(d) >= 실행일(UTC)          # 하한 — 경과 면제 차단      [expired]
  AND date.fromisoformat(d) <= 발행일 + 180일       # 상한 — 무한 만기 차단      [over-cap]
       # ★ 발행일 := 같은 frontmatter 의 `date:` 필드 값 (리터럴 고정 — 아래 (vi))

ladder(file) :=
      len(mea) >= 1
  AND 각 항목에서 경로가 추출된다 (경로 키 closed-set — 아래 ③-key)
  AND 그 경로가 repo 내 실재 실행 파일
  AND 그 경로가 workflow run: 줄에 등장

admissible(file) := ladder(file) OR exempt(file)
```

- ★ **복수 토큰 = 선택 규칙이 아니라 RED** (설계리뷰 R3 N-2 처분). 만기가 2개일 때 `max` 를 택하면
  **fail-open 경로**가 생긴다(먼 날짜를 하나 더 적으면 연장된다). "정확히 1회" 는 선택 문제를
  **발생시키지 않는** 방식으로 닫는다.
- ★ **키 자체 부재 = RED (`mea-missing`)**. 문면에 없으면 checker 저자가 "키 없으면 스킵" 을
  자연스럽게 짠다 — 실측 근거: 현행 `scripts/check-doc-frontmatter.sh` 는 이 키를 **한 번도 언급하지 않는다**
  (`grep -c mechanical_enforcement_actions scripts/check-doc-frontmatter.sh` → **0**, firsthand).
  ★★ **단, 직전 판의 "가장 싼 회피구(키 삭제)를 봉인한다" 는 over-claim 이다 (FIX Iter 5, ablation 실측)**:
  이 leg 을 꺼도 **행 10 의 verdict 는 RED 그대로**이고 exit 사유만 `line-form` 으로 바뀐다.
  키를 지우면 `LINE` 이 매치할 줄이 없어 어차피 RED 이기 때문이다. ⇒ 이 leg 의 실제 기여는
  **봉인이 아니라 진단 정밀화 + `fm-parse-error` 와의 상호 보완**이다((0-c) 쌍 ablation — 둘을 함께 끄면
  행 14·20 이 `GREEN` 이 된다). **`LINE` 과 중복 방어**임을 여기 적는다.
- ★ **frontmatter YAML 파싱 실패 = RED (`fm-parse-error`), skip 아님**. 근거는 본 저작의
  **자기 실례**다 — 아래 ③-key census 를 돌린 파서가 `try/except: continue` 로
  `archive/adr/ADR-082-write-time-self-write-verification-mandate.md` 를 **조용히 탈락**시켰고,
  그것이 심사 실측(48 파일)과 본 저작 실측(47 파일)이 갈린 원인이다(firsthand). 파싱 실패를
  skip 으로 두면 **frontmatter 를 깨뜨리는 것이 회피구**가 된다.

##### (iv) ★★ 결정표 — 구체 입력 → 기대판정 (checker 수용 기준)

입력 열은 frontmatter 안 실제 바이트다. `<판정>` 열의 대괄호 토큰은 위 (iii) 의 exit 사유이며
checker 는 이 토큰을 stdout 으로 방출한다(어느 행에서 걸렸는지 관측 가능해야 봉합이 검증된다).

###### (iv-0) ★★ 입력 바이트 정본 — 산문 서술 금지 (설계리뷰 FIX Iter 4, P1-3)

직전 판은 14행 중 **9행만 리터럴**이고 5행이 산문 서술("빈 줄 2개 + 3줄 아래 무관 주석")이었다.
특히 **행 4 는 구판 판정이 입력에 의존**한다 — 그 무관 주석에 토큰이 0이면 구판도 RED 지만
`#1113` 과 날짜가 들어 있으면 구판은 **GREEN** 이다. 그런데 ADR·Story·Change Plan 3곳 공통으로
"구판으로 돌리면 행 3·4·9 가 GREEN" 이라 적혀 있었으므로, **입력을 고정하지 않으면 그 문장 자체가
재현 불가**였다. ⇒ 모든 행의 입력을 **완전한 바이트 fixture** 로 고정한다.

**공통 골격** — 각 행의 입력 = 아래 fixture 의 `<FM>` 자리에 그 행의 바이트를 넣은 파일 전체다.

```
---
<FM>
---
```

**공통 상수** (행마다 재기술하지 않는다):

```
D    := date: 2026-08-16
R    := [repo=mclayer/plugin-codeforge]        # ★ FIX Iter 5 신설 — 생략기호 `[repo=…]` 전면 치환용
OK   := carrier=#2985 expiry=2026-09-15 R      # (R 은 위 리터럴로 전개된다)
K    := mechanical_enforcement_actions
TAB  := U+0009 실제 탭 1문자                     # ★ FIX Iter 5 — 행 20·21 이 이 상수를 쓴다
실행일 := 2026-08-17 (UTC)     # 재현용 pin. 행 13(expired)·행 15(over-cap) 판정이 이 값에 의존한다
```

★★ **`R` 신설 이유 (FIX Iter 5, P0-D)** — 직전 판은 (iv-0) 에서 *"모든 행을 완전한 바이트 fixture 로
고정한다"* 고 선언해 놓고 **6행(11·12·13·15·16·18)에 생략기호 `[repo=…]` 를 남겼다.** 리터럴 독법이면
그 6행은 `REPO` 미매치로 판정이 달라지고, 특히 **행 16**(발행일 leg 의 **유일한 역방향** 판별 행)이
`RED` 로 바뀌어 **판별이 소멸**한다. ⇒ 상수 `R` 을 정의하고 6행을 전부 치환했다.
**선언과 표가 어긋난 자리를 표 쪽에서 닫는다.**

★ **재현 시 `실행일` 을 반드시 위 값으로 pin 할 것** — 그러지 않으면 시간 의존 행(13)의 기대가
실행 시점에 따라 달라져 "전건 재현" 이 성립하지 않는다. 이것은 (iii) `expired` leg 이 도입한
시간 의존 판정((viii) 아래 `③-exp` 문단)의 필연적 귀결이며, 결함이 아니라 **재현 조건의 일부**다.

★★ **검사기 정의역도 표 안에 둔다 (설계리뷰 FIX Iter 4, P2-3)** — 직전 판의 결정표는 `정의역` 이라는
말을 **한 번도 담지 않았고**, 정의역은 표 밖 산문(아래 `③-exp` 말미 `INV-D` 자기적용 문단)에만 결속돼
있었다. 수용 기준이 "표 전건 재현" 이라면 **재현자가 무엇을 대상으로 돌려야 하는지도 표와 함께 있어야 한다.**

| 축 | 값 |
|---|---|
| **파일 정의역 (P)** | **PR diff forward-only** — 해당 PR 이 추가·수정한 `archive/adr/ADR-*.md` (merge-base 대비) |
| 정의역 **밖** | merge-base 시점에 이미 존재하던 ADR (코퍼스 소급 0 — 소급하면 전 PR 자해 차단) |
| **파일 내 정의역** | `SCOPE` = frontmatter 블록 (본문 제외 — 위 (ii) `SCOPE`) |
| 선례 | `adr-amendment-parity` entry 가 동일하게 "PR diff forward-only, merge-base 대비" 를 쓴다 |

이 표는 표 밖 `INV-D` 자기적용 문단의 **재진술이 아니라 그 문단이 SSOT 인 값의 표 내 결속**이다
(§결정 4 접합부 규약 — 값이 두 곳에 적히면 어느 쪽이 SSOT 인지 명시한다).

| # | 입력 바이트 (`<FM>`) | 기대 | exit 사유 | 무엇을 판별하는가 |
|---|---|---|---|---|
| 1 | `D` ⏎ `K: []  # OK` | **GREEN** | — | 의도한 정상형. 이 행이 RED 면 검사기가 규범보다 좁아 자기 ADR 3건이 born-red |
| 2 | `D` ⏎ `K: []` | **RED** | `line-form` | **R2** — `ADR-043`·`ADR-067` 이 실제로 이 상태였다. 주석 0바이트 |
| 3 | `D` ⏎ `K: []` ⏎ `# OK` | **RED** | `line-form` | **R3 엔진 분열의 실물.** 구판 `\s` = GREEN / 신판 = RED ⇒ **`\s` 금지 leg 판별** |
| 4 | `D` ⏎ `K: []` ⏎ ⏎ ⏎ `# beta2 audit #1113 (2026-05-21)` | **RED** | `line-form` | 동상(원거리). ★ **주석 바이트가 load-bearing** — `#1113` 과 날짜를 담았기에 구판 자유텍스트 탐색이 GREEN 이 된다. 산문 서술이었다면 재현 불가였다 |
| 5 | `D` ⏎ `K: []  # carrier=#2985 expiry=9999-12-31 [repo=mclayer/plugin-codeforge]` | **RED** | `over-cap` | 상한 leg **존재**. ★ 단 **상한의 기준일은 판별하지 못한다**(세 독법 전부 RED) — 그 결손을 행 15·16 이 메운다 |
| 6 | `D` ⏎ `K: []  # carrier none. not #0. expiry TBD - 2099-01-01 is only an example` | **RED** | `carrier-token` | **R3 부인 문장 GREEN.** 고정 토큰 전환 leg 판별 |
| 7 | `D` ⏎ `K: [ ]  # OK` | **RED** | `line-form` | **R3 P2** — YAML 등가 표기. (v) 표기 정규형 선언 leg |
| 8 | `D` ⏎ `"K": []  # OK` | **RED** | `line-form` | 동상(인용 키) |
| 9 | `D` ⏎ `K:` ⏎ `  []  # OK` | **RED** | `line-form` | 동상(flow 개행). 구판 `\s` 에서는 GREEN |
| 10 | `D` ⏎ `status: Accepted` (키 자체 부재) | **RED** | `mea-missing` | **R3 P1** — 가장 싼 회피구(키 삭제) 봉인 leg |
| 11 | `D` ⏎ `K: []  # carrier=#2985 expiry=2026-09-15 R carrier=#1` | **RED** | `carrier-token` | **출현 계수 leg 판별** — `grep -c`(행 계수)면 GREEN(firsthand 1 대 2) |
| 12 | `D` ⏎ `K: []  # carrier=#2985 expiry=2026-09-15 R expiry=2027-01-01` | **RED** | `expiry-token` | 동상. 먼 날짜를 하나 더 적어 창을 연장하는 경로 봉인 |
| 13 | `D` ⏎ `K: []  # carrier=#2985 expiry=2020-01-01 R` | **RED** | `expired` | 하한(경과) leg 판별. 실행일 pin `2026-08-17` 의존 |
| 14 | `D` ⏎ `K: []  # OK` ⏎ `broken: "unterminated` | **RED** | `fm-parse-error` | **파서 계층 leg** — census 파서가 `ADR-082` 를 조용히 탈락시킨 자기 실례. ★ **FIX Iter 5 — 산문 서술("파싱 실패하는 파일")을 리터럴 바이트로 교체**했고, 참조 구현 승격으로 **정규식 술어 밖이 아니라 정의역 안**이 됐다. ★ ERE 가지는 이 행에서 `GREEN` 으로 fail-open ((i-x-B)) |
| **15** | `date: 2026-05-13` ⏎ `amendment_log:` ⏎ `  - date: 2026-08-16` ⏎ `K: []  # carrier=#2985 expiry=2026-12-01 R` | **RED** | `over-cap` | ★★ **발행일 leg (정방향)**. frontmatter `date` 독법 = **RED**(상한 2026-11-09) / amendment 저작일 독법 = **GREEN**(2027-02-12) / 실행일 독법 = **GREEN**. **오독하면 판정이 뒤집힌다** |
| **16** | `D` ⏎ `amendment_log:` ⏎ `  - date: 2026-05-17` ⏎ `K: []  # carrier=#2985 expiry=2027-01-01 R` | **GREEN** | — | ★★ **발행일 leg (역방향)**. frontmatter `date` 독법 = **GREEN**(상한 2027-02-12) / 최신 amendment 독법 = **RED**(2026-11-13). 역방향까지 있어야 leg 이 양쪽으로 고정된다 |
| **17** | `D` ⏎ `K: []  # carrier=#2985 expiry=2026-09-15` (repo 토큰 부재) | **RED** | `repo-token` | ★★ **FIX Iter 5 정정 — 이 행은 `REPO` 를 판별하지 못한다.** `REPO` 를 꺼도 `PFX` 가 `R` 접미를 요구해 RED 이며 **사유만** `token-order` 로 바뀐다. 판별은 행 17b 가 맡는다. 이 행이 재는 것 = **{`REPO`,`PFX`} 쌍** |
| **17b** | `D` ⏎ `K: []  # OK R` (repo 토큰 **2회**) | **RED** | `repo-token` | ★★ **FIX Iter 5 신설 — `REPO` 의 진짜 판별 행 (P0-A)**. `REPO` 제거 시 `PFX`·`CAR`·`EXP` 전부 통과해 **GREEN**. ablation 실측으로 확정 |
| **18** | `D` ⏎ `K: []  # this is not a carrier=#2985 expiry=2026-09-15 R` | **RED** | `token-order` | ★ **`PFX` leg 판별**. 부인 산문 안에 토큰을 매설하는 경로. `PFX` 없으면 GREEN |
| **19** | `D` ⏎ `K: []  # OK` **∧ 본문에 열 0 코드블록으로 같은 줄 1회 재등장** | **GREEN** | — | ★ **`SCOPE` leg 판별**. 파일 전체 정의역이면 매치 2회 → `line-form` RED. firsthand 매치수 = 파일 전체 **2** / frontmatter **1** |
| **20** | `D` ⏎ `K: []` + `TAB` + `# OK` | **RED** | `fm-parse-error` | ★★ **FIX Iter 5 신설 — `LINE` 공백군의 탭 half 가 도달 불가임을 고정 (P1-4)**. YAML 이 이 위치의 탭을 금지하므로 **어떤 입력으로도 GREEN 이 될 수 없다.** (0-d) 참조 |
| **21** | `D` ⏎ `K: []  # carrier=#2985` + `TAB` + `expiry=2026-09-15 R` | **GREEN** | — | ★★ **FIX Iter 5 신설 — `PFX` 공백군의 탭 half 판별 (P1-4)**. 주석 본문은 YAML 이 탭을 허용하는 **유일** 위치. 공백군을 스페이스 전용으로 좁히면 `token-order` RED |
| **22** | `D` ⏎ `K: []  # OK` ⏎ `K: []  # carrier=#2985 expiry=2099-01-01 R` | **RED** | `line-form` | ★★ **FIX Iter 5 신설 — "정확히 1회" 부분 leg 판별**. YAML 중복 키는 합법이라 파싱은 통과한다. "1회 이상" 으로 완화하면 **먼 만기를 한 줄 더 적어 통과**한다 |
| **23** | `D` ⏎ `K: []  # carrier=#2985 carrier=#1 expiry=2026-09-15 R` | **RED** | `carrier-token` | ★ **FIX Iter 5 신설 — 인접 중복(사이 공백 1)**. ERE 양쪽경계 1패스가 인접 토큰을 1로 세는 경로. ★ 단 verdict 는 `PFX` 가 이미 RED — **사유만** 갈린다((i-x) 2패스 강등 근거) |
| **24** | `D` ⏎ `K: []  # carrier=#12345678 expiry=2026-09-15 R` | **RED** | `carrier-token` | ★ **FIX Iter 5 신설 — 8자리(자릿수 상한 초과)**. 직전 판이 2패스 채택 근거로 든 입력이 **표에 없었다** — 그 결손을 메운다 |

★★ **실행 확인 (firsthand, 본 판 저작 시점)**: (iv) 표 **전 25행**을 **참조 구현**(Python `re` +
`yaml.safe_load`)으로 실행했다 — **기대 일치 25/25 · 불일치 0**(판정과 exit 사유가 모두 일치).
**이식 부록**(POSIX ERE + shell)으로도 같은 25행을 돌려 **일치 23 / 불일치 2** 를 얻었다 —
불일치는 **행 14 · 20**, 둘 다 `fm-parse-error` 이며 **ERE 가지가 `GREEN` 으로 fail-open** 한다((i-x-B)).

★★ **직전 판의 *"2엔진 18/18"* 은 행 14 를 정의역에서 빼고 얻은 수치였다.** 이번 판은 참조 구현 승격으로
그 행을 **정의역 안**에 두었고, 그러자 불일치가 드러났다. **수치가 나빠진 것이 아니라 정의역이 정직해진 것**이며,
"좁힌 정의역에서 얻은 100%" 를 엔진 동치의 근거로 쓰던 자리를 여기서 닫는다.

★ **판별력 실증 (항진 아님)**: 같은 25행을 **구판 `\s` + 자유텍스트 + 파일 전체 정의역** 술어로 돌리면
**17행**(3 · 4 · 5 · 6 · 9 · 11 · 12 · 13 · 14 · 15 · 17 · 17b · 18 · 19 · 20 · 23 · 24)에서 verdict 가 갈린다.
★ 그 중 **행 19 는 역방향**(신 `GREEN` / 구 `RED`)이다 — 표가 한 방향으로만 조여진 것이 아니라
**양방향으로 고정**돼 있음을 보인다(단방향이면 "전부 RED 로 만드는 구현" 이 통과한다).

★★ **`D-LEG` 자기적용 결과 (FIX Iter 5 — L2 를 ablation 으로 재판정)**:

**직전 판의 L2 열은 "판별 행" 을 저자가 **지목**한 것이었다. ablation 으로 재판정하니 3칸이 틀렸다.**

| leg | L1 (입력원 리터럴) | **L2 (ablation verdict 판별)** | 직전 판 지목 | 재판정 |
|---|---|---|---|---|
| `over-cap` 의 **발행일** | `frontmatter date:` 필드 | ★ **행 15·16 양방향** | 행 15·16 | ✓ 정확 |
| `carrier` 의 **동일성** (`REPO`) | `[repo=owner/name]` 토큰 | ★ **행 17b** (신설) | 행 17 | ✗ **틀림** — 행 17 은 `PFX` 가 이미 RED (P0-A) |
| **선두 배치** (`PFX`) | 캡처 `c` 선두 앵커 | 행 18 | 행 18 | ✓ 정확 |
| `LINE` 의 **정의역** (`SCOPE`) | frontmatter 블록 | 행 19 | 행 19 | ✓ 정확 |
| `LINE` 의 **"정확히 1회"** | 매치 수 = 1 | ★ **행 22** (신설) | (미지목) | ✗ **누락** — 직전 판엔 판별 행 0 |
| `mea-missing` | YAML 키 멤버십 | ★ **없음** (사유만) | "키 삭제 봉인" | ✗ **over-claim** — `LINE` 중복 방어 |
| `fm-parse-error` | `yaml.safe_load` 예외 | ★ **없음** (사유만) — `MEA` 와 쌍으로만 판별 | (미지목) | ✗ **단독 판별 0** |
| 공백군 (`LINE`) | `[[:blank:]]` / `[ \t]` | ★ **도달 불가** (행 20 이 증명) | (미지목) | ✗ **신설 불가** (P1-4) |
| 공백군 (`PFX`) | 동상 | ★ **행 21** (신설) | (미지목) | ✓ 신설 |
| 주석 본문군 | `.` / `[^\n]` | ★ **14행** (행 1 포함) | (미지목) | ★ **`D-CLS` 로 이관** |
| ERE **2패스** | 선행 경계 + 초과 패스 | ★ **없음** (사유만) | "1패스 불가" | ✗ **robustness 로 강등** (P1-3) |
| `amendment_log` **배제** | 적용 carrier 측(ADR-067 §9.4 처분 7) | Change Plan §8.D `N3` ablation 표 | §8.D mutantB | ✓ (§8.D 에서 재설계) |

★★★ **이 표가 이번 판의 요지다** — 직전 판은 **12칸 중 4칸만 정확**했고 나머지는 over-claim·누락·오지목이었다.
**저자 지목과 실행 산출의 차이가 정확히 그 8칸**이며, 그것이 L2 를 존재-assert 에서 ablation 으로
올린 이유다. 규칙을 바꾸지 않았다면 이 8칸은 이번에도 통과했을 것이다.

##### (v) ★ 표기 정규형 선언 — split-brain 처분 (R3 P2 / N-6)

행 7·8·9 는 **YAML 의미가 같은데 RED** 다. 이를 "정규식 판독과 PyYAML 판독의 split-brain" 으로
부르면 결함처럼 읽히지만, **처분은 정규식을 YAML 근사로 넓히는 것이 아니다.** 넓히면 술어가 다시
문맥 추론으로 돌아가 판정 불가로 회귀한다. ⇒ **면제 경로는 표기 정규형을 요구한다**고 선언한다:

> 면제 경로(`exempt`)를 타려는 선언은 `mechanical_enforcement_actions: []` **단일 줄 리터럴 형태**로
> 적는다. YAML 상 등가인 다른 표기(`[ ]` · 인용 키 · flow 개행 · block 리스트 0항목)는
> **면제 경로 부적격**이며 exit 사유는 `line-form` 이다.

- 이것은 **false-RED 가 아니라 선언된 형식 제약**이다. 차이 — false-RED 는 규범이 허용한 것을
  검사가 거르는 상태이고, 여기서는 **규범 자신이 표기를 좁혔다.**
- 좁혀도 되는 근거: 면제는 **예외 경로**이며 예외를 쓰는 저작자에게 정규형 1줄을 요구하는 비용은
  거의 0 이다. 반면 표기 다양성을 허용하면 술어가 YAML 파서와 정규식 사이에서 영원히 어긋난다.
- ★ **`ladder` 경로에는 이 제약이 없다** — 사다리는 PyYAML 파싱 결과(`len(mea) >= 1`)로만 판정하므로
  표기 자유다. 제약은 면제 경로 한정이다. 두 leg 의 판독 계층이 다르다는 사실을 여기 적는다.

##### (vi) ★ 만기 상한 = **발행일 + 180일** (R3 신설) — ★★ `발행일` 리터럴 확정 (FIX Iter 4)

하한(`>= 실행일`)만으로는 `9999-12-31` 이 통과한다(행 5). 상한을 신설하고 그 값의 근거를 적는다.

###### (vi-1) ★★ `발행일` 의 입력원 확정 (`D-LEG` L1)

**직전 판은 상한을 `발행일 + 180일` 로 적고 `발행일` 을 정의하지 않았다.** firsthand —
`grep -n '발행일 :=' archive/adr/ADR-181-*.md` → **0건**(3 hit 전부 사용처). 그 결과 세 독법이
동시에 성립했고, 실제 3 ADR 에서 상한이 **3개월 넘게 갈라진다**:

| 독법 | ADR-181 | ADR-067 | ADR-043 | 상한 격차 |
|---|---|---|---|---|
| **frontmatter `date:`** (실측 `2026-08-16` / `2026-05-13` / `2026-05-09`) | 2027-02-12 | 2026-11-09 | **2026-11-05** | ★ 최대 **99일** |
| 최신 `amendment_log[].date` | 2027-02-12 | **2027-02-12** | 2027-02-12 | — |
| 실행일 | 실행 시점 + 180 | 〃 | 〃 | 매 PR 재개 |

> **확정 — `발행일 := 같은 frontmatter 의 `date:` 필드 값`.** 다른 값을 택하려면 그 근거를 문면에 명시한다.

**택일 근거 3항**:

1. ★★ **amendment 저작일 독법은 상한을 무력화한다** — amendment 는 계속 추가되므로 그 독법에서는
   PR 마다 창이 `그 PR 의 저작일 + 180` 으로 **재개**된다. 즉 `9999-12-31` 을 한 번에 적는 경로는
   막히지만 **180일씩 나눠 적는 무한**이 열린다. 한 번에 적는 무한만 막고 나눠 적는 무한을 열어두면
   상한 leg 의 목적(면제의 영구화 차단)이 달성되지 않는다.
2. **실행일 독법은 같은 결함의 극단** — 창이 매 실행마다 재개되므로 상한이 사실상 소멸한다.
3. **`date:` 는 문서의 불변 앵커** — frontmatter `date` 는 그 ADR 이 언제 발효했는지의 SSOT 이며
   amendment 로 갱신되지 않는다(실측 — ADR-067 은 amendment 4회 후에도 `date: 2026-05-13`).
   면제가 "그 결정 이후 얼마나 오래 미건설로 남아 있는가" 를 재려면 앵커는 **결정 시점**이어야 한다.

★★ **판별 행 (`D-LEG` L2) = 행 15·16**. 행 15 는 `date` 독법에서만 RED(정방향), 행 16 은
`date` 독법에서만 GREEN(역방향)이다. 두 행이 함께 있어야 leg 이 양쪽으로 고정된다 —
**한 방향만 두면 "더 넓게 읽는 구현" 또는 "더 좁게 읽는 구현" 중 하나가 통과한다.**

★ **직전 판에는 판별 행이 0개였다 (firsthand)**: 기존 14행을 세 독법으로 전수 실행한 결과
**갈리는 행 0개**. 상한 leg 은 표에 들어왔으나 표는 그 leg 의 자유 변수를 전혀 고정하지 못했다.
이것이 `D-LEG` 를 신설한 직접 동인이다.

###### (vi-2) 상한값 180 의 근거

| 성질 | 요구 | 채택값이 만족하는가 |
|---|---|---|
| 유한 | 무한 만기 = 면제의 영구화 = ADR-070 §D5 계보로 회귀 | 예 |
| **발행일 상대** | 절대 상한(예 "2027-01-01 이전")은 시간이 지나면 코퍼스 전체를 born-red 로 만든다 | 예 |
| 현행 저작 수용 | ★ **정정** — 아래 (vi-3) | 예 (최악 **1.40x** 여유) |
| 검토 주기 미만 | 1년을 넘으면 면제가 연 단위 검토를 **건너뛰고** 생존한다 | 예 (180 < 365) |

###### (vi-3) ★ 근거표 3행의 정정 — "3 ADR = 30일" 은 **1건만 참이었다**

직전 판은 "현행 3 ADR = 발행 `2026-08-16` / 만기 `2026-09-15` = **30일** (6배 여유)" 라 적었다.
`발행일` 을 `date:` 로 확정하면 그 문장은 **3건 중 1건(ADR-181)에만** 해당한다. 실측:

| ADR | `date:` | `expiry=` | 실 span | 180 대비 여유배수 |
|---|---|---|---|---|
| ADR-181 | 2026-08-16 | 2026-09-15 | **30일** | 6.00x |
| ADR-067 | 2026-05-13 | 2026-09-15 | **125일** | 1.44x |
| ADR-043 | 2026-05-09 | 2026-09-15 | **129일** | **1.40x** ← 최악 |

⇒ 근거표 3행의 정본 = **"현행 3 ADR span = 30 / 125 / 129일, 최악 여유배수 1.40x"**.
★ 이 정정은 180 이라는 값의 채택을 바꾸지 않지만(1.40x > 1 이므로 여전히 수용), **"6배 여유" 라는
안전 마진 서술은 거짓**이었다. 형제 2건이 `[]` 를 이번 PR 에 새로 붙였고 그 만기를 자기 발행일이 아니라
**본 Story 의 만기에 맞췄기 때문**이며, 그 사실이 근거표에 반영되지 않았다.

★ **자의성 정직 고지 (`declared`)**: 180 은 위 4성질을 만족하는 값 중 **하나**이며 유일해가 아니다.
그 자의성을 숨기지 않는다. 다만 이 값을 pin 하는 것은 INV-C 위반이 **아니다** — INV-C 가 금지하는
pin 은 "잔여일 수" 같은 **관측 카운터를 exit 조건으로 삼는 것**이고, 상한은 **형식 조건**이다.
두 축이 다르므로 여기서 구분해 적는다.
★ **여유가 1.40x 로 좁다는 사실의 귀결 (`declared`)**: 형제 2건은 만기를 30일 더 미루면 상한을 넘긴다.
이것은 결함이 아니라 **상한이 실제로 무는 지점이 가깝다는 관측**이며, 만기 연장 요구가 오면
`over-cap` 이 실제로 RED 를 낼 것이라는 뜻이다(면제 갱신은 그때 사다리 경로로 이행해야 한다).

##### (vii) ★ ③-key — 사다리 (나)의 **경로 키** closed-set (R3 N-1)

면제 가지에는 ③-loc 처방이 생겼는데 **사다리 가지에는 같은 처방이 없었다** — 항목의 어느 키에서
경로를 꺼내는지 미선언이라 (나)(다)가 판정 불가였다. 확정:

```
PATH_KEYS := ["script_path", "workflow", "detect_command", "action",
              "script", "path", "check", "workflow_path"]      # closed-set
경로 추출 = 항목이 dict 이고 PATH_KEYS 중 1개 이상 보유 → 그 값들이 경로 후보
항목이 bare scalar(문자열) → 경로 키 부재 ⇒ 사다리 미충족 (RED)
```

★ **census (firsthand, 재현 명령 병기 — 정수 pin 아님)**:

정의역 = `archive/adr/ADR-*.md` glob (174 파일, `ADR-RESERVATION.md` 포함).
★ **재현 시 순진 파서를 쓰지 말 것** — `try/except: continue` 는 `ADR-082` 를 조용히 떨어뜨린다.
파싱 실패 파일은 **탈락시키지 말고 mea 블록만 격리 재파싱**하거나 **오류로 보고**해야 아래 값이 나온다:

```
recovered: files=48 items=169 distinct_dict_keys=35
```

| 축 | 순진 파서 (`try/except: continue`) | **복구 후** | 심사 실측 | 판정 |
|---|---|---|---|---|
| glob 파일수 | **174** | 174 | 174 | 일치 |
| `mea` 비어있지 않은 파일 | **47** | **48** | 48 | ★ **복구 후 정확히 일치** |
| 총 항목 | **152** | **169** | 169 | ★ **복구 후 정확히 일치** |
| bare scalar 항목 | **39** | 39 | 39 | 일치 |
| dict 키 종류 | **35** | **35** | 36 | ★ **여전히 1 괴리** — 아래 잔여 |
| `PATH_KEYS` 로 경로 추출되는 dict 항목 | 107 | — | — | 술어 의존 (정수 pin 안 함) |

★★ **괴리의 원인이 전부 규명됐다 (firsthand)**: 순진 파서가 `ADR-082-write-time-self-write-verification-mandate.md`
하나를 YAML `ScannerError`(인용 스칼라 스캔 실패)로 **조용히 탈락**시켰고, 그 파일의
`mechanical_enforcement_actions` 는 **항목 17개를 보유**한다.
⇒ **47 + 1 = 48** ∧ **152 + 17 = 169** — 두 축이 **정확히** 심사 실측으로 복구된다.

★ **인용 정정 (설계리뷰 FIX Iter 4, P2-4)** — 직전 판은 위 괄호에 `:620-682` / 키 **6종**
(`action`/`status`/`target_section`/`verified_files`/`origin_main_sha`/`last_git_fetch_timestamp`)
이라 적었다. 재실측하면 둘 다 틀렸다:

| 축 | 직전 판 | **재실측 (firsthand)** |
|---|---|---|
| `mea` 블록 범위 | `:620-682` | **`:620-671`** (다음 최상위 키 직전) |
| 항목 dict 키 종류 | 6종 | **3종** — `action` / `status` / `target_section` |
| 나머지 3종의 실제 소속 | (미기재) | **`pre_lookup_evidence:` (`:673-682`) 하위** — `mea` 와 무관한 **별개 최상위 frontmatter 키** |

즉 직전 판의 범위가 11줄 넘쳐 **이웃 키의 하위 필드를 `mea` 항목 키로 흡수**했다.
★ **복구 논증 자체는 무손상** — `47 + 1 = 48` 과 `152 + 17 = 169` 는 **항목 개수** 축이고
이 정정은 **키 종류** 축이다. 두 축이 disjoint 하므로 결론(파싱 실패를 skip 으로 두면 안 된다)은 유지된다.
정정하는 것은 그 결론에 딸린 **인용의 정확성**이다.
★ 이것이 결정표 **행 14**(`fm-parse-error` = RED, skip 아님)의 직접 근거다. 파싱 실패를 skip 으로 두면
**frontmatter 를 깨뜨리는 것이 가장 싼 회피구**가 되며, 여기서는 그 회피구가 **검사기가 아니라 census
자신**을 이미 속였다.

★ **잔여 (정직 기재, `declared`)**: dict 키 종류만 **35 대 36** 으로 남는다. 복구 후에도 좁혀지지 않았으므로
이 축은 **키 정규화 술어**에 의존한다고 본다 — 산출 술어가 다른 두 관측을 억지로 일치시키지 않고 잔여로 적는다.

★ **추정 원인 정정 (설계리뷰 FIX Iter 4, P2-5)** — 직전 판은 후보로 "대소문자·별칭·**중첩 dict 하강 여부**"
를 나열했다. **중첩 하강 가설은 반증됐다 (firsthand)**: 항목 dict 를 재귀 하강해 전 depth 의 키를 모으면
**35 그대로**이고 하강으로만 얻어지는 키는 **0개**다(`deep - flat = ∅`). 즉 코퍼스의 `mea` 항목에는
중첩 dict 가 사실상 없다.
⇒ 잔여 +1 의 **유일 남은 후보 = bare scalar 항목(39개)의 계수 범주** — 심사 측 산출 술어가
bare scalar 를 "키 없음" 이 아니라 하나의 범주로 세었다면 35 + 1 = 36 이 된다.
★ **확정하지 않는다** — 심사 측 산출 술어를 직접 보지 못했으므로 이는 **후보**이며, 잔여는
**유지**한다. 반증된 가설을 지우고 남은 가설을 확정으로 승격하는 것이 이 Story 가 4 라운드 내내
고발한 형상이므로, 여기서는 **반증 사실만 기록하고 잔여를 그대로 둔다.**

★★ **직전 판의 "13종 키" 는 철회한다 (R3 P1)**. 재현되지 않았다 — 같은 축의 두 독립 실측이
**35 / 36** 이고 직전 판의 13 은 어느 쪽으로도 재현되지 않았으며 산출 술어가 미상이다.
★ 이 자리에 정수를 다시 박지 않고 **재현 명령 + 괴리 원인 + 잔여**를 적는다.
"13종" 이 하필 **"정수 pin 금지" 문단의 근거 정수**였다는 것이 이 class 의 자기 실례다.

##### (viii) ★ 결정표의 천장 (`declared` — 지우고 인용 금지)

**이 표는 "이제 모든 우회를 막았다" 를 주장하지 않는다.** 표는 **알려진 입력형만** 고정하며,
미지 입력형에 대한 완전성은 `declared` 다. 근거 — 입력 공간은 바이트 문자열 전체이고 그 전집합에
대한 판정은 열거로 닫히지 않는다. 실제로 표의 행은 **매 라운드 늘었고**
(R2·R3 에서 9행 → **R4 에서 5행**(15·16·17·18·19) → **R5 에서 6행**(17b·20·21·22·23·24)),
그 사실은 "다음 라운드에 새 행이 없다" 를 **함의하지 않는다.**
★ **행수를 여기 정수로 박지 않는다** — 위 (0-a) 재현 규칙으로 얻는다(자기 포함 함정 회피).
★ **`D-LEG` 가 바꾼 것** — 직전 라운드까지 새 행은 **심사가 우회를 발견해야** 생겼다.
`D-LEG` 이후에는 **leg 을 신설하는 저작 자신이 행을 동반**해야 한다.
★★ **`D-LEG` L2 를 ablation 으로 올리면서 바뀐 것이 하나 더 있다** — 직전 판까지는 저자가
"이 행이 판별한다" 고 **지목**하면 통과였고, 그래서 **틀린 지목이 통과했다**(위 자기적용 표 8칸).
이제는 실행이 산출한 차이만 인정되므로, **틀린 지목은 표에 0 으로 찍힌다.**
그럼에도 ablation 은 **표 안의 행에 대해서만** 차이를 재므로, 표 밖 입력형에 대한 완전성은 여전히 아니다.
- 이 표가 실제로 개선한 것 = **판정 주체의 존재**다. 직전 판은 심사자마다 독법이 갈렸고 이제는
  갈릴 때 **어느 행이 어긋났는지 지목**할 수 있다. 그것이 매체 전환의 이득이며 완전성은 아니다.
- 새 입력형이 발견되면 처분은 **행 추가**이며(§결정 7 정의역 확대) 신규 AC·신규 게이트 신설이 아니다.

---

- **왜 AND 가 아닌가**: ①②③ 을 "전건 충족" 으로 묶은 것은 ①·②·③ **항목 간** 관계이지,
  ② 내부의 두 충족 경로 간 관계가 아니다. 사다리와 면제를 AND 로 읽으면 `[]` 는 영원히 부적법이 되어
  ③ 이 사문화되고, 반대로 ③ 만 읽으면 사다리가 사문화된다. **둘 다 살아 있어야 ③ 이 의미를 갖는다.**
- **면제 경로의 천장 (`declared`, 지우고 인용 금지)**: 면제 경로를 택한 선언에 대해 **(다) 는 도달하지 않는다.**
  즉 그 선언은 "돌아가는 검사가 있다" 를 증명하지 않으며, 증명하는 것은 **만기가 박혀 있다** 뿐이다.
  이것은 ADR-070 §D5 면제에 날짜 문자열을 덧댄 것과 **형태가 같다.** 다른 점은 단 하나 —
  만기 경과가 **기계 판정 가능**하다는 것이다(날짜 비교). 그 차이 외에는 면제이며, 그렇게 부른다.
- **만기 경과 시 처분**: 면제 경로는 **시한부**다. 만기일이 지난 `[]` 는 면제 경로를 잃고
  사다리 경로만 남으므로 부적법이 된다. 이것이 면제가 영구 회피구가 되지 않는 유일한 기제다.

#### ★ ③-exp — 그 "유일한 기제" 에 검출 주체가 0 이었다 (설계리뷰 FIX Iter 2 정산)

**firsthand 반증 (wrapper `bb2778865`)**: `grep -rn "mechanical_enforcement_actions" scripts/ hooks/ .github/ tests/`
→ **hit 3건 전부 주석·docstring**(`scripts/check_parallel_dispatch_prompt.py:7` ·
`.github/workflows/adr-reservation-claim-test.yml:17` · `.github/workflows/adr-uniqueness-check.yml:10`).
**이 필드를 파싱하는 코드는 repo 에 0 건이다.** 그리고 직전 판의 면제 술어는 만기를 **형식 정규식**으로만 봤다 —
`\d{4}-\d{2}-\d{2}` 는 `1999-01-01` 도 통과시킨다. ⇒ 만기가 지나도 GREEN 이므로 **실질 무기한 면제**이고,
그러면 ADR-070 §D5 계보와 구별되지 않는다. "영구 회피구가 되지 않는 유일한 기제" 라는 자기 정당화가
**그 시점에 근거를 결여**하고 있었다.

**처분 = 정당화 축 강등이 아니라 경과 판정 leg 신설** (택일 근거):

| 선택지 | 판정 | 사유 |
|---|---|---|
| (A) 정당화 축을 정직 강등 — "만기는 표기일 뿐" | ✗ | 그렇게 적으면 §결정 5 가 ADR-070 §D5 와 **의미상 동일**해진다. 본 ADR 의 존재 이유(선언-only 비용을 0 에서 양수로) 가 소멸하므로 강등은 ADR 자체를 사문화한다 |
| ★ (B) **경과 판정 leg 신설** (날짜 비교) | ★ **채택** | 비용이 1줄이다(`date.fromisoformat(m) >= 실행일`). 형식 정규식이 이미 날짜를 캡처하므로 파싱 재작업 0. 강등하면 잃는 것이 크고 신설하면 드는 것이 작다 |

- **재사용 조사 결과 (firsthand)**: `scripts/lib/decision_record_disposition.py` 의 `membership-expiry` ·
  `phantom-enforcement` 축을 재사용 후보로 검토했으나 **부적합**이다 — 그 모듈의 `membership-expiry` 는
  **branch-protection required-context 집합의 멤버십** 판정이지 달력 만기가 아니며, 모듈 전체에
  `datetime`/`date` import 가 **0 건**이다(`grep -n "datetime\|date(" scripts/lib/decision_record_disposition.py`
  → 매치 0). 즉 재사용할 달력 primitive 가 그 파일에 없다. ⇒ **신규 1줄 비교**로 구현한다.
- **mutant 5번째 (Phase 2 checker 대조군 의무)**: `(e)` **만기를 과거일로 치환**(예 `2020-01-01`) → **RED**.
  이 mutant 가 GREEN 이면 경과 판정 leg 이 배선되지 않은 것이며, 그 상태에서 위 (B) 채택 근거는 무효다.
  ★ **FIX Iter 3 — mutant 열거를 결정표로 승격**: 개별 mutant 를 산문으로 나열하는 방식이 라운드마다
  새 mutant 를 낳았으므로(9층 이동), 이제 **③-dt (iv) 결정표가 대조군 집합의 SSOT** 다
  (★ FIX Iter 5 — 행수 정수 pin 제거).
  위 (a)~(e) 는 그 표의 행 2·10·13 등에 흡수됐고, 신규 `(f)` **만기 상한 초과**(`9999-12-31`) → **RED**
  는 표 행 5 다. 개별 mutant 를 여기 추가하지 않고 **표에 행을 추가**한다.
- ★ **경과 leg 이 도입하는 새 성질 — 시간 의존 판정 (`declared` 천장)**: 같은 커밋이 오늘 GREEN, 만기 후 RED 다.
  이는 결함이 아니라 **시한부의 정의**이지만, 게이트가 `warning` tier 로 태어나야 하는 이유이기도 하다
  (ADR-171 §결정 5 warning-first 와 독립적으로 같은 결론). 또한 **잔여일 수는 카운터로 방출**하되
  **특정 정수를 exit 조건으로 pin 하지 않는다**(INV-C ratchet-in 회피).
- ★ **여전히 남는 천장**: 만기 도래 시 RED 를 내는 것은 **그 검사가 실제로 배선된 뒤**다. Phase 1 시점에는
  checker 자체가 미건설이므로 본 leg 도 **선언**이다. 그 사실을 여기 적는다 — 이 문단을 지우고 인용하면 over-claim 이다.

★ **검사기 정의역 (INV-D 자기적용 — 코퍼스-wide 소급 아님)**: 본 §결정 5 의 기계 검사 정의역 =
**PR diff forward-only** (해당 PR 이 신규 추가·수정한 ADR 파일). merge-base 시점에 이미 존재하던
ADR 은 정의역 **밖**이다. 근거 — §결정 5 문면이 "신규 규범 항목을 추가하는 **저작물**" 로 저작 시점을
scope 로 삼고, 소급 적용하면 코퍼스 전수 `[]`·키부재 다수가 즉시 born-red 가 되어
**전 PR 자해 차단**이 된다(§결정 7 이 경계하는 비용 발산). 선례 = `adr-amendment-parity` entry 가
동일하게 "PR diff forward-only, merge-base 대비" 정의역을 쓴다.
★ **그 scope 술어의 정직한 한계 (`declared`)**: "무엇이 **신규 규범 항목** 추가인가" 는 의미론적 판정이라
기계 술어로 닫히지 않는다. 기계가 판정하는 것은 "PR 이 ADR 파일을 추가·수정했는가" 까지이며,
그 안에서 규범 항목 추가 여부는 리뷰 판정 축이다. **이 술어를 `normative` 로 라벨하지 않는다.**

- **자기적용 (실측 기준)**: 본 ADR frontmatter 는 ③ 형식(`carrier=#2985 expiry=2026-09-15
  [repo=mclayer/plugin-codeforge]` 선두 배치)을 따르며 **면제 경로**로 ② 를 충족한다 —
  사다리 경로가 아니다(위 천장 문단 적용 대상).
  ① 은 본 ADR 과 **같은 PR 의 `docs/evidence-checks-registry.yaml` row 2건**으로 충족된다 —
  `fix-ledger-conformance` (원장 축) · **`adr-admission`** (본 §결정 5 자신의 게이트 축), 둘 다
  `current_tier: warning` / `status: deferred-followup`.
  ★★ **`adr-admission` 을 본문에 명시한다 (FIX Iter 5, P2-2)** — 직전 판은 이 entry 를 registry 에
  append 해 놓고 **ADR 문면에서 한 번도 언급하지 않았다**(firsthand: `grep -c 'adr-admission'` 본 파일 → **0**).
  자기 §결정을 집행할 게이트의 이름이 그 §결정 본문에 없으면 **registry 와 ADR 이 서로를 못 가리키고**,
  그것이 §결정 4(접합부 규약)가 금지하는 형상이다. 두 row 의 owner_adr = 본 ADR 이며
  **`adr-admission` 이 (iv) 결정표를 구현하는 checker 의 registry 상 이름**이다.
- ★★ **FIX Iter 5 자기적용 재검증 (firsthand, 2엔진)**: 이번 판이 바꾼 것
  (`mea-missing` 의 YAML 계층 이관 · 공백군 위치별 분해 · 주석 본문군 엔진별 표기 · 신규 행 6종)을
  반영한 **참조 구현**과 **이식 부록**을 **실 파일 3건**에 각각 적용했다 —
  `ADR-181` · `ADR-067` · `ADR-043` **전건 GREEN**(참조 구현 3/3 ∧ ERE 3/3, 판정·사유 일치).
  즉 규칙을 좁히면서 자기 ADR 을 born-red 로 만들지 않았다. 특히 `over-cap` 은 `발행일` 을
  `date:` 로 고정한 뒤에도 3건 모두 통과한다(여유 6.00x / 1.44x / 1.40x — 위 (vi-3)).

- ★ **ADR-070 §D5-C 정산 (선제 기각안 반박)**: ADR-070 `:309` 는 대안 (D5-C)
  "declaration-only retain 영역에서도 evidence-checks-registry entry append" 를
  **"registry schema scope 침해 — 실행 가능한 mechanical lint 부재 entry append 는 schema 의미 약화"**
  로 기각했다. 본 §결정 5 ① 은 그 기각안을 되살리므로 반박 없이는 상충이다. **반박 = 그 전제가 거짓이다** —
  기각 논거는 "registry schema 가 미건설 상태를 표현할 수단이 없다" 를 전제하는데,
  schema 는 `status: deferred-followup` 을 **이미 보유**하며 본 registry 안에 **다수의 선례**가 있다.
  ★ **고정 정수를 적지 않는다 (설계리뷰 FIX Iter 2 정정)** — 직전 판은 "14 entry 선례" 로 적었으나
  같은 명령을 지금 실행하면 **15** 다. 본 PR 이 append 한 `fix-ledger-conformance` 행이 스스로를
  세었기 때문이다(**자기 포함 함정** — 세어 적는 행위가 대상을 늘린다). ⇒ **재현 규칙 + immutable ref** 로 적는다:
  `grep -c '^    status: deferred-followup' docs/evidence-checks-registry.yaml`
  — merge-base `ecfe62d63` 시점 = **14**(본 PR 무관 선례), HEAD 시점 = 그 값 + 본 PR append 분.
  논증에 필요한 것은 "선례가 0 이 아니다" 이며 그 명제는 두 시점 모두에서 참이다.
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
  시점의 기존 선언-only 는 본 ADR 로 **정리되지 않는다.**

  ★★ **코퍼스 실측 — 직전 판의 `137 (78.7%)` 은 파서 산물이었다 (설계리뷰 FIX Iter 2 정정)**.
  직전 판은 "키 부재 84 + 빈 리스트 53 = 137" 로 적었고 **산출 술어를 병기하지 않았다.** 리뷰가 순진
  행-스캔 파서로 `84/53` 을 재현해 그 값이 **YAML 의미가 아니라 특정 파싱 방식의 산물**임을 확정했다.
  오분류 11건에는 본 PR 이 `carrier_adr` 로 지정한 **`ADR-171` 자신**(항목 11개 보유)이 포함된다.

  | 축 | 값 |
  |---|---|
  | 정의역 | `archive/adr/ADR-*.md` glob = **174 파일** (`ADR-RESERVATION.md` 포함) |
  | 방법 A — PyYAML frontmatter 파싱 | 키 부재 **84** / 빈 리스트 **42** / 비어있지 않음 **48** |
  | 방법 B — 원시 grep(파서 무관) | `mechanical_enforcement_actions: []` 리터럴 **42** · 키 보유 **90** ⇒ 90 − 42 = **48** |
  | 3단 전건 (가) 미충족 | 84 + 42 = **126 (72.4%)** — 두 방법이 독립적으로 일치 |

  재현 명령(정의역·술어 동반):

  ```
  python -c "import glob,io,yaml;fs=sorted(glob.glob('archive/adr/ADR-*.md'));a=e=n=0
  for f in fs:
      t=io.open(f,encoding='utf-8').read(); d=yaml.safe_load(t[3:t.find(chr(10)+'---',3)]) if t.startswith('---') else None
      v=(d or {}).get('mechanical_enforcement_actions','__MISSING__')
      a+=v=='__MISSING__'; e+= v!='__MISSING__' and not v; n+= v!='__MISSING__' and bool(v)
  print(len(fs),a,e,n)"
  ```

  ★ **사다리 3단 통과 수 (S1 → S2 → S3)** — S1 = **48** (위 두 방법 일치, 견고). S2(항목이 실재 실행
  파일로 해석) · S3(그 경로가 workflow 텍스트에 등장) 은 **경로 추출 술어에 의존**하며 단일 정수가 아니다:
  리뷰(Codex) 술어 = **24 → 20**, 본 저작 술어 변종 2종 = **16 → 10** (확장자 `.py/.sh/.js/.ts` 한정) ·
  **18 → 14** (`.yml/.yaml` 포함, basename 매치). ⇒ **S2·S3 은 정본 정수를 확정하지 않는다** —
  항목 스키마가 13종 키 형상으로 비균질하기 때문이며(③ 아래 민감도 고지), 확정해야 할 것은 정수가 아니라
  **술어의 명시**다. S1 = 48 만이 방법-불변이다.

  ★ **수치를 normative AC 로 pin 하지 않는다** — 위 수는 전부 **관측**이며 게이트의 exit 조건이 아니다
  (INV-C ratchet-in 회피). 본 ADR 은 그 126 을 건드리지 않으며, **신규 저작이 127 번째가 되는 것만** 막는다.

  ★ **정직 고지 (은폐 금지)**: 같은 축에 대해 세션 중 `139 (79.9%)` 라는 값도 보고된 바 있으나,
  그 값은 **파서 변종 4종 어디에서도 재현되지 않았고 산출 술어가 미상**이다. 재현 불가한 수치는
  근거로 쓰지 않으며 그 사실을 지우지 않는다(ADR-119 — 재현 불가는 "추정" 으로 표기).
- 새 ADR 1건 추가 자체가 "선언 1건 추가" 의 가장 값싼 형태일 위험을 진다. 그 위험은 §결정 5 를
  **본 ADR 자신에게 먼저 적용**함으로써만 상쇄되며, 상쇄 여부는 Phase 2 실행으로 판정된다.

## 관련 파일

- [ADR-067](ADR-067-fix-ledger-implementability-escalation.md) — Amendment 4 (FIX 닫기 조건 적용 carrier)
- [ADR-171](ADR-171-evidence-enforceable-promotion-framework.md) — `carrier_adr`(framework host). **amendment 0** — §결정 8 근거
- [ADR-167](ADR-167-adr-amendment-compaction-ratchet.md) — amendment compaction ratchet (ADR-171 무접촉 판정의 비용 근거)
- [ADR-119](ADR-119-research-before-claims.md) — §결정 10② 반증 규범 (본 ADR 이 정의역 축 보강)
- `docs/inter-plugin-contracts/fix-event-v1.md` — ★ **현 실버전 = `version: "1.5"`**(firsthand `:4`).
  `원인 판정` 값공간 확장 + 정의역 선언 필드를 담는 **v1.6 MINOR 는 아직 존재하지 않는다** —
  D-1 / carrier `plugin-codeforge#2985` / 만기 `2026-09-15`
- `docs/inter-plugin-contracts/dev-process-event-v1.md` — ★ **현 실버전 = `version: "1.0"`**(firsthand `:4`).
  `root_cause_class` 원장 키를 담는 **v1.1 MINOR 는 아직 존재하지 않는다** —
  D-19 / carrier `plugin-codeforge#2985` / 만기 `2026-09-15`

★ 직전 판은 위 두 줄을 `v1.6` · `v1.1` 로 **현재형 기술**했다. 이는 본 ADR §결정 5 ②
("아직 존재하지 않는 enforcement 자산을 현재형으로 기술하지 않는다")의 **자기위반**이었으며,
같은 파일 frontmatter `related_files` 주석(`:26`·`:27`)이 이미 실버전을 정확히 적고 있어 **자기모순**이기도 했다.
설계리뷰 FIX Iter 2 에서 정정한다.
- `docs/evidence-checks-registry.yaml` — `fix-ledger-conformance` entry (owner_adr = 본 ADR)
- `docs/domain-knowledge/concept/verification-domain-deficit.md` — 개념 서술 SSOT

## 해소 기준

N/A — permanent policy
