---
adr_number: 184
title: 요구사항리뷰 4축 발동 관측 레코드 — 증적 정의역·라운드 단위·정직 상한
date: 2026-08-19
status: Proposed
category: governance
carrier_story: CFP-3022
parent_epic: "mclayer/plugin-codeforge#3016"
is_transitional: false
supersedes: null
amends:
  - ADR-125  # Amendment 5 (동일 carrier CFP-3022, 동일 PR) — §결정 6 declarative-only 를 실 판정 분기로 승격 + 4축 관측 레코드 의무. supersede 아님 (§결정 6 문면 무손상 append-only)
related_adrs:
  - ADR-125  # 요구사항리뷰 lane 규범 SSOT — 본 ADR 의 유일한 amend 대상 (Amendment 5). §결정 6 = 이행 대상 원문
  - ADR-008  # inter-plugin contract versioning — §결정 2(선택 필드 추가·enum 값 추가 = MINOR) 를 그대로 적용. 새 판례 0 → Amendment 미발동 (§결정 9)
  - ADR-044  # peer floor (SoD: implementer ≠ certifier) + peer_verdicts[] optional array 선례. §결정 1 층1 형상의 직접 구조적 선례, §결정 4 완화 경로의 근거. ★ title 은 "Phase-scoped sequential team SSOT" 이나 body 가 peer floor 를 보유 — 번호↔주제 비자명, firsthand 확인 후 인용 (§자기적용 3)
  - ADR-058  # §결정 5 보호강도 비축소 ratchet — §결정 6 이 `continue-on-error` 부착을 금지하는 근거
  - ADR-119  # 검증 후 단언 — 검사연극 금지 원문. §결정 4 의 완화 경로 `source:` 부산물 발생원
  - ADR-127  # N/A 는 단축이 아니라 정식 분류의 정상 결과 — §결정 3 `정상 N/A` 상태의 규범 근거
  - ADR-152  # 정직 천장 = presence/구조 fail-closed, activation-detection-forcing 아님 — §결정 4 의 직접 근거
  - ADR-155  # dev-process-event-v1 — accounting 재기록 금지. §결정 1 이 이 채널을 기각한 근거 (상관 ID JOIN 만 허용)
  - ADR-163  # measurement channel architecture — closed enumeration. 신규 채널을 만들지 않으므로 Amendment 미발동 (§결정 9)
  - ADR-170  # Orchestrator inline whitelist 4-sub-scope closed enum — §9 는 기존 sub-scope #1 재사용이라 미발동. ADR-182 신규 섹션 대안 채택 시 5번째 추가 = 확정 발동 (§결정 9 조건절)
  - ADR-171  # evidence-enforceable promotion framework — §결정 6 승격 3-AND. §결정 6 fallback(W2) 채택 시에만 인용
  - ADR-031  # §14 Lane Evidence FROZEN 12-field schema — cardinality 불일치로 §14 경로 기각 (§결정 1). lane 7→8 수리는 #2956 소관, 본 ADR 무접촉
  - ADR-182  # 리뷰 심사 정의역 ↔ FIX 증적 정의역 분리 (status = Accepted, firsthand 확인) — 신규 증적 섹션은 번호 미확정이라 본 ADR 이 의존하지 않는다 (§결정 1 대안절)
  - ADR-133  # ADR 번호 atomic claim / §결정 4 fallback — 본 ADR 번호 184 발급 경로 (§결정 9 말미)
  - ADR-178  # 관측 산출 어휘 = 선언값·실측값·불일치 3-tuple, verdict 어휘 금지 — 본 ADR 전체의 서술 규율
related_stories:
  - CFP-3022
related_files:
  - plugins/codeforge-review/agents/RequirementsReviewPLAgent.md  # 4축 실배선 + category_enum + review_packet 2블록 (정본 ∧ variant:runtime-failure)
  - plugins/codeforge-review/templates/review-checklists/requirements.md  # 축 식별자 SSOT (파일명 ↔ lane_id 비대칭 — §결정 8)
  - plugins/codeforge-review/agents/CodexReviewAgent.md  # peer 프롬프트 — `#### lane=` 헤딩 5 : `category from {` 집합 4 (§결정 7 P-1/P-2 근거)
  - docs/inter-plugin-contracts/review-verdict-v4.md  # 층1 `axis_activation[]` 착지 계약 (MINOR)
  - .github/workflows/invariant-check.yml  # category/severity parity 게이트 — 정의역 확장 대상 (§결정 6·7)
  - templates/story-page-structure.md  # 층2 §9 서브섹션 스킴 — 요구사항리뷰 슬롯 신설 대상
---

# ADR-184: 요구사항리뷰 4축 발동 관측 레코드 — 증적 정의역·라운드 단위·정직 상한

## 상태

Proposed (2026-08-19). Carrier = CFP-3022 (Epic `mclayer/plugin-codeforge#3016` 의 E-4). ADR-125 Amendment 5 와 **동일 carrier·동일 Phase 1 PR** 로 착지한다.

## 컨텍스트

> **측정 정본 규약**: 본 ADR 의 모든 수치는 아래 명령의 산출이며 **계약값은 명령이지 수치가 아니다**. 기준 SHA (wrapper `origin/main`) = **`7a12d0a0fa8b213de1b70cb655133523ed622902`**. 값이 달라지면 명령을 재실행한 쪽이 옳다.
>
> **선행 앵커 승계 규율**: 선행 산출(deputy 9본 · PL 판정 1~12)의 다수는 앵커 `485977cf8` 에서 측정됐다. 구간 diff `485977cf8..7a12d0a0f` = 7 파일이며 그중 3건이 `archive/adr/**` 다. 따라서 **`archive/adr/**` 값은 전건 fresh 재측정했고**(§자기적용), `plugins/codeforge-review/**` · `.github/workflows/**` · `docs/inter-plugin-contracts/**` 는 구간 diff 공집합이라 승계하되 본 문서 작성 시점에 fresh 앵커에서 재실행해 재현을 확인했다.

### 축 식별자 — 리터럴 집합으로만 지목한다

요구사항리뷰 lane 의 심사 축 = `{external-fact-dependency, internal-invariant, ac-decomposition-completeness, internal-fitness}` (4원소).

**서수 인용 금지.** ADR-125 자신이 같은 대상을 "3번째 disjoint 축" 과 "4번째 disjoint 축" 두 수로 부른다 — 오타가 아니라 서로 다른 집합(lane 전 축 / additive-disjoint-axis 패턴 계보)을 센 결과이며, 3-계열 독법에서 사라지는 축이 하필 `ac-decomposition-completeness` 다. 서수 인용이 그 모순의 재발 경로이므로 본 ADR·본 ADR 의 하류 배선은 축을 **항상 식별자 리터럴 집합**으로 지목한다. 처분 = ADR-125 Amendment 5 §A5.4.

### 문제 — 채널 부재가 아니라 처방이 다른 두 결함

ADR-125 §결정 6 은 깊은 다출처 검증 발동이 "무조건이 아니다 — 매 Story 강제 발동 아님(declarative-only)" 이라 선언한다. 그러나 **선언과 실제가 일치하는지 관찰할 채널이 없다**. 발동 여부가 어디에도 기록되지 않으므로 "이 lane 이 비용만큼 값을 하는가" 에 추정으로만 답하게 된다.

| Gap | 기전 | 처방 계열 |
|---|---|---|
| **Gap A — 어휘 정합 붕괴** | 기성 parity 게이트(`.github/workflows/invariant-check.yml`)의 `LANES` 정의역에 `requirements-review` 가 부재해 축 식별자 drift 가 green 아래 상주 | 기성 게이트 **정의역 확장 + 실 drift 동시 수리** (§결정 6·7·8) |
| **Gap B — 발동-후-null** | `review-verdict-v4` 는 `findings[]` 로만 축 정보를 나르고 finding 은 결함이 있을 때만 생성된다. `external-fact-dependency`·`internal-fitness` 는 규정상 "0건 = 정상". ⇒ **"축이 돌았고 결함 0" 과 "축이 안 돌았다" 가 동일 관측(배열에 없음)** | **신규** — 축 발동 레코드 신설 (§결정 1·2·3) |

parity 게이트는 어휘 정합만 볼 뿐 발동 여부를 보지 않으므로 Gap A 를 닫아도 Gap B 는 남는다. 두 gap 은 disjoint 하게 배정된다.

### 현행 실태 (firsthand, 기준 SHA `7a12d0a0f`)

재현:

```sh
cd <wrapper worktree>   # HEAD = 7a12d0a0f
export PYTHONIOENCODING=utf-8
python3 - <<'EOF'
import re
from pathlib import Path
B = "plugins/codeforge-review/"
pl = Path(B+"agents/RequirementsReviewPLAgent.md").read_text(encoding="utf-8")
print("PL strict MATCH:", bool(re.search(r"category_enum:\s*\n((?:\s*-\s*[a-z-]+\s*\n)+)", pl)))
m = re.search(r"category_enum:\s*\n((?:\s*-\s*[a-z-]+[^\n]*\n)+)", pl)
print("PL relax:", re.findall(r"-\s*([a-z-]+)", m.group(1)))
for n in ["DesignReviewPLAgent","CodeReviewPLAgent","SecurityTestPLAgent","RequirementsReviewPLAgent"]:
    t = Path(B+f"agents/{n}.md").read_text(encoding="utf-8")
    blk = re.search(r"```ya?ml\s*\nreview_packet:[\s\S]*?\n```", t)
    print(n, re.findall(r'^\s*contract_version:\s*"?([0-9.]+)"?\s*$', blk.group(0), re.M))
cx = Path(B+"agents/CodexReviewAgent.md").read_text(encoding="utf-8")
print("Codex 헤딩:", re.findall(r"^####\s*lane=(\S+)", cx, re.M))
print("Codex 집합 수:", len(re.findall(r"category from \{", cx)))
EOF
```

산출 (본 ADR 저작 시점 firsthand):

| 관측 지점 | 산출 | 귀결 |
|---|---|---|
| 게이트 PL 정규식 `category_enum:\s*\n((?:\s*-\s*[a-z-]+\s*\n)+)` | **MATCH 실패** | 인라인 주석 보유 행 때문에 블록 자체를 못 잡는다 |
| 완화 정규식 재추출 | 9 리터럴 — 실 8 + phantom **`verdict-v`**, `ac-decomposition-completeness` **부재** | 주석 본문 `review-verdict-v4` 에서 `-` 뒤 `verdict-v` 가 카테고리로 민팅 (§결정 7 P-3) |
| `review_packet` `contract_version` | design/code/security = `1.0`, requirements-review = **`1.1`** | 게이트 리터럴 `"1.0"` 정확 일치 술어와 불일치 — **PL 쪽이 앞서 있다**. 되돌리면 회귀 (§결정 6 절단) |
| Codex `#### lane=` 헤딩 | 5개 — `requirements-review` 가 **2회**(정본 + `variant: runtime-failure`) | 헤딩 5 : `category from {` 집합 **4** = 비대칭 (§결정 7 P-2 근거) |

> **선언값 · 실측값 · 불일치 (ADR-178 어휘)** — 선행 PL 공통 입력은 완화 재추출 결과를 **8**, 본 저작 실측은 **9** 로 적었다. **둘 다 참이며 정의역(ref) 차이**다: 8 = 주석 선제거 후 strict 적용(strip-then-strict), 9 = 주석 존치 상태 완화 적용(relax-in-place, phantom 1 포함). 양측 합치 사실 = `ac-decomposition-completeness` 누락. **불일치 항목 없음.** 두 수를 하나로 뭉치면 어느 쪽도 재현되지 않는다.

### 정직성 전제 — 이 ADR 이 감당할 수 없는 것

축을 수행하는 주체와 그 발동을 기록하는 주체가 동일하다. 따라서 **자기 선언 boolean 은 원리적으로 "실제로 수행했는가" 를 증명하지 못한다.** 본 ADR 은 이 한계를 없애는 척하지 않고 **위치를 특정하고 완화를 그 지점에 겨눈다** (§결정 4).

## 결정

### 결정 1 — 축 레코드는 2층 구조다 (층1 packet optional array · 층2 Story §9 확장)

"레코드가 어디 한 곳에 산다" 는 단일 질문으로 풀면 오설계다. 현행 write 경계상 review PL·워커는 Story 파일을 직접 쓰지 않고 packet(구조화 반환값)만 만들며, Story §9 append 는 Orchestrator 몫이다. 따라서 축 레코드는 **서로 다른 두 아티팩트**로 나뉜다.

| 층 | 아티팩트 | write 주체 | 성격 |
|---|---|---|---|
| **층1 (구조화 원본)** | `review-verdict-v4` packet 의 신규 필드 `axis_activation[]` — **verdict-level optional array** | lane worker (기존 synthesis 채널, 변경 0) | 세션·PR 생애주기 안에서만 산다 |
| **층2 (영속 착지 = 증적 정의역)** | Story **§9 품질 게이트 이력** 의 요구사항리뷰 전용 서브섹션 | Orchestrator (기존 sub-scope 재사용) | 후속 재측정이 읽을 수 있는 영속 파일 |

층1 만으로는 "판독 규칙까지" 요구를 충족하지 못한다 — packet 은 영속 파일이 아니고, `templates/story-page-structure.md` §9.1 의 "packet yaml block embed **권장**"(의무 아님)이라는 문구가 이미 그 결손을 자인한다. 층2 만으로는 기계 집계 가능한 구조가 없다.

**층1 형상 = optional array (MINOR), required 아님.** 근거:

- `review-verdict-v4` 는 v4.0 BREAKING 이후 **MAJOR 무선례**이며 누적 bump 전건이 MINOR 경로다.
- 직접 구조적 선례 = `peer_verdicts[]` (ADR-044) — verdict-level optional array, findings 유무와 무관하게 의미를 나르고, 강제는 스키마가 아니라 **외부 게이트**가 담당.
- required 로 만들면 `axis_activation` 개념이 없는 design/code/security packet 이 **스키마 위반으로 즉시 born-red** 된다 — 본 ADR §결정 6 이 차단하려는 것과 동일 결함 class 의 계약층 재현.
- **required 여도 강제력이 늘지 않는다**: 스키마 `required:true` 는 필드 presence 만 강제하고 cardinality(정확히 4건)나 축 식별자 집합의 완전성은 표현하지 못한다. 결국 외부 게이트를 다시 도입해야 하므로 추가 강제력 0, 비용만 MAJOR 4대 의무.

**lane-conditional**: `axis_activation[]` 은 `lane == "requirements-review"` 에만 존재한다. 나머지 3 lane 은 필드 자체가 부재이며 이는 §결정 3 의 4상태 중 **어느 것도 아니다**(`capable:false` 조차 아님 — 개념이 정의되지 않음). 선례 = `living_architecture_updated_self_check_passed` (단일 lane 전용 optional field). 이 구분이 없으면 3 lane packet 의 필드 부재를 오탐으로 잡는 회귀가 생긴다.

**기각한 착지 후보 3종 (침묵 금지 — 사유 명시)**:

| 후보 | 기각 사유 |
|---|---|
| **§14 Lane Evidence** (ADR-031) | ① `outcome` enum = `PASS\|FIX\|SKIPPED\|ESCALATED` 라 "정상 N/A" 를 `SKIPPED` 로 표현하면 §결정 3 의 3-way 구별이 **같은 값으로 붕괴** ② §14 는 **lane 당 1 row** 스키마인데 축 레코드는 **iteration 당 4 row** 가 필요 — 13번째 field 추가가 아니라 **row cardinality 재구조화**. FROZEN 12-field schema Amendment + 재구조화 = 이중 비용 ③ lane 7→8 수리는 이미 별 carrier(#2956) 진행 중이라 재차 착지 = 상충 |
| **`dev-process-event-v1`** (ADR-155) | ADR-155 명문 위반 — verdict/산출물 요약 accounting 은 각 output 계약 소유이고 dev-process 이벤트는 accounting **재기록이 아니다**. 축 필드 값 자체를 여기 담으면 review-verdict-v4 가 이미 소유한 accounting 의 재기록. 이 채널은 **상관 ID 포인터만** 나를 수 있다 |
| **신규 measurement channel** (ADR-163 편입) | closed enumeration 에 row 신설 = Amendment 확정 발동 + 0-API/latency ceiling 등 무거운 governance 상속. 얻는 것은 기존 채널 payload 로도 얻어지므로 **governance 비용 > 이득** |

**대안(채택 아님, 조건부 후속)**: ADR-182 가 지정한 신규 증적 전용 monopoly 섹션은 메타-텍스트 타입 정의("census·측정 기록") 상 축 발동 기록과 개념적으로 정확히 일치한다. 그러나 그 섹션은 **번호가 아직 확정되지 않았다**(ADR-182 본문이 "섹션 번호는 본 ADR 이 예단하지 않는다" 고 명시). 본 Story 를 미착지 섹션에 의존시키면 계측기가 개입보다 먼저 착지해야 한다는 순서 원칙에 역행한다. ⇒ **지금은 §9, 그 섹션 확정 후 이관은 후속 carrier 판단** (§결정 9 의 ADR-170 조건절과 연동).

### 결정 2 — 레코드 정의역 = **라운드(리뷰 iteration) 당**. Story 당 아님

유일성 키 = **`(story_key, iteration, axis_id)` 3-tuple**. 이 3-tuple 은 §10 FIX Ledger 의 `Iter` 컬럼·§14 의 iteration 필드가 이미 쓰는 라운드-로컬 순번 관행과 동형이라 신규 개념이 아니다.

**근거**: 관측상 같은 Story 의 서로 다른 iteration 이 서로 다른 축 산출을 낸다(같은 1건의 재확인이 아니라 라운드마다 독립 재실행). Story 당으로 뭉치면 어느 iteration 값이 "그 Story 의" 값인지 정의되지 않고, 최신 값으로 덮으면 이력이 소실되어 Gap B("그 라운드에 발동했는가")를 사후에 답할 수 없다. 또한 완화 기전(dual-peer)도 라운드마다 재실행되므로, 레코드 단위가 라운드가 아니면 "그 라운드의 peer 결과가 그 라운드의 축 레코드를 검증했다" 는 결속이 끊긴다.

**대가 — 정직 인정**: 라운드 당 절단은 축별 분모(`applicable:true` 건수)를 **라운드 수에 비례해 부풀린다**. 5회 FIX 를 거친 Story 1개가 1회에 통과한 Story 5개와 분모에서 동일하게 계상된다. 이는 실제 문제이며 "라운드 당" 을 택했다고 사라지지 않는다.

**파생 규율 — 집계 레이어에서 2지표 분리 (합산·단일 순위 금지)**:

| 지표 | 산출식 | 답하는 질문 |
|---|---|---|
| **execution-cost** | `COUNT(axis_record) GROUP BY axis_id` (라운드 단위 원본 그대로) | "이 축이 총 몇 번 실행됐는가" — 비용 |
| **story-breadth** | `COUNT(DISTINCT story_key) GROUP BY axis_id WHERE applicable=true` | "몇 개 Story 가 이 축의 대상이었는가" — 채택률 |

원본 레코드는 **라운드 단위 append-only 보존**(정보 손실 0)하고, 두 지표는 **집계 레이어에서만** 파생한다. 두 지표를 하나의 비율로 합산하거나 단일 순위로 매기면 실패다 — 정의역이 다른 두 수를 섞는 것이기 때문이다.

**재시도 idempotency**: 동일 3-tuple 재기록 시 **덮어쓰기 금지 · append 재시도 전 존재 확인**. (Orchestrator 전사 도중 세션 중단 후 재개가 실제 발생 경로.)

### 결정 3 — 4상태 taxonomy = 4 직교 필드. AC-5↔AC-7 overlap 은 구현 수준에서 정밀화한다

"발동" 은 단일 boolean 이 아니다. 레코드는 최소 4 직교 필드를 갖는다.

| 필드 | 구별하는 것 |
|---|---|
| `applicable` | 발동 조건 성립 여부 — **축별 분모** 생성원 |
| `capable` | 구조적 발동 가능 여부 — 미배선을 정상 N/A 와 분리 |
| `executed` | 실제 수행 여부 (중단·도구 실패로 인한 미판정 포함) |
| `yield` | 산출 finding 수 (**0 포함** — 0 은 결측이 아니라 값이다) |

동반 필드: `reason`(=`executed:false` 일 때 substantive 문자열 필수) · `payload_ref`(=`executed:true` 일 때 부산물 참조).

판정식:

| 상태 | 판정식 |
|---|---|
| 억지 발동 — **자기모순형만** | `applicable:false` ∧ `executed:true` ∧ `yield≥1` |
| 정상 N/A | `applicable:false` ∧ `executed:false` ∧ `capable:true` |
| 무발동 은폐 | **`capable:true` ∧** `applicable:true` ∧ `executed:false` |
| 구조적 발동 불능 | `capable:false` |

**`capable:true` 조건절은 본 ADR 의 신설분이다.** 4 필드로 직교 분리했음에도 `capable:false ∧ applicable:true ∧ executed:false` 조합에서 **무발동 은폐 판정식과 구조적 발동 불능이 동시 성립**한다 — 직교축 conflate anti-pattern 이 필드 층이 아니라 **판정식 층**에서 재현된 것이다. `capable:false` 표본은 정의상 은폐가 아니라 미배선이므로(별 상태가 이미 잡는다), 조건절 추가는 의도를 좁히는 것이 아니라 **의도대로 구현**하는 것이다.

⇒ **처분 = 구현 수준 정밀화. AC 문면 변경 아님.** 요구사항 lane 재진입 없이 설계 lane 이 흡수한다. 단 이 판단 자체가 해석이므로 설계리뷰 심사 대상으로 남긴다.

**`yield:0` 은 결측이 아니다** — `executed:true ∧ yield:0` 은 "축이 돌았고 결함이 없었다" 는 **양성 정보**이며, 이것이 Gap B 를 닫는 유일한 값이다. 집계에서 `yield:0` 레코드를 결측으로 취급하면 Gap B 가 그대로 재개통한다.

### 결정 4 — 정직 상한: 무발동 은폐만 기계 차단한다. 억지 발동은 **원리적으로** 기계 차단 불가

**본 ADR 및 그 하류 산출물 어디에도 "억지 발동과 무발동 은폐를 둘 다 기계 구별한다" 는 단정을 두지 않는다.**

무엇이 결정 가능하고 무엇이 아닌가 — 위치를 특정한다:

| 대상 | 판정 가능성 | 근거 |
|---|---|---|
| 필드 조합의 **내부 모순**(억지 발동 자기모순형) | 결정 가능 | 레코드 내부 일관성 — 외부 사실 참조 0, 자족 술어 |
| 필드 presence · 값 도메인 | 결정 가능 | 구문 검사 |
| `reason` 비공백 | 결정 가능 — **presence 만** | 문자열의 진실성은 대상 밖 |
| `payload_ref` **참조 대상의 실재** | 결정 가능 | 좌표 resolve. 단 "실제로 열람했는지" 는 대상 밖 |
| 무발동 은폐 | **조건부** 결정 가능 | `applicable:true` 로 **기록된 경우에 한함** |
| **`applicable` 값의 진리성** | **원리적으로 결정 불가** | 아래 |

**단일 결정불가 지점 (single point of undecidability)**: `applicable` 은 "이 Story 의 결론이 외부사실에 의존하는가" 류의 의미론적 판단이고, 그 판단의 ground truth 가 **시스템 안에 표상되어 있지 않다**. 검증자가 참조할 **독립 oracle 이 부재**하며, oracle 없는 attestation 은 검증 불가다. 구현 미비가 아니라 **정의상의 불가**다.

**그리고 이 지점은 두 감사식의 공통 전제다** — 억지 발동 판정식은 `applicable:false` 를, 무발동 은폐 판정식은 `applicable:true` 를 요구한다. ⇒ **`applicable` 을 사실과 다르게 적는 단 하나의 행위가 두 감사식을 동시에 무력화한다. 감사 커버리지 전량이 이 필드 하나에 걸린 SPOF 다.**

**완화 3종 — 얻는 것과 얻지 못하는 것을 분리해 적는다**:

| 완화 | 기전 | 얻지 못하는 것 |
|---|---|---|
| **dual-peer (SoD)** | 검증 floor = ≥1 independent peer, implementer ≠ certifier (ADR-044). 축소 실행은 **가시 마커와 사유를 남겨야 하고 침묵이 차단 대상** — 이 형태가 Gap B 의 원형이다 | peer 도 동일 oracle 부재에 놓인다. 불일치 확률을 낮출 뿐 진리를 얻지 못한다 |
| **사후 표본 감사** | payload 를 대조 대상으로 삼아 사람이 표본 검사 | 표본 밖은 미검사. 커버리지 ≠ 1 |
| **`applicable` 3-tuple 교차** | 기록자 단독 선언값을 `선언값 · 독립 파생 신호 · 불일치` 3-tuple 로 승격 (아래 표) | **불일치 검출이지 진리 검증이 아니다** |

`applicable` 3-tuple 의 독립 파생 신호(기록자 저작이 아닌 것):

| 축 (식별자 리터럴) | 독립 파생 신호 | 모순 판정식 |
|---|---|---|
| `external-fact-dependency` | 산출물의 `source:` 인용 존재 — ADR-119 가 이미 부과한 의무라 부산물이 자연 발생 | `applicable:false` ∧ 외부출처 인용 ≥1 → 억지 N/A 후보 |
| `internal-invariant` | runtime-failure Story 한정(ADR-125 Amendment 2) — Story label / §10 원장의 runtime 실패 기록 | runtime-failure 신호 존재 ∧ `applicable:false` → 모순 후보 |
| `ac-decomposition-completeness` | **무조건 축 — `applicable` 상수 true** | `applicable ≠ true` 이면 즉시 위반 (§결정 5) |
| `internal-fitness` | ADR-125 Amendment 3 결정 B 의 조건절 신호 | 조건 신호 존재 ∧ `applicable:false` → 모순 후보 |

**바뀌는 것 / 바뀌지 않는 것**: `applicable` 진리성이 결정 불가라는 사실은 **바뀌지 않는다**. 바뀌는 것은 거짓 기록이 **무비용으로** 통과하지 않는다는 점 — 거짓 `applicable:false` 는 이제 산출물의 다른 부분과 **모순 신호를 남겨야** 통과한다. 보안 어휘로 **inconsistency detection 이지 truth verification 이 아니다.**

**payload 는 위조 비용이 수행 비용 이상일 때만 완화로 기능한다.** 자유 서술·에이전트 저작 요약·검사 건수 숫자는 위조 비용 ≈ 0 이라 **무력**하다. 유효한 형태 = ① repo 좌표 + 기준 SHA(부분 유효 — 실재는 증명, 열람은 미증명) ② **재현 명령 + 그 판정 산출**(결정론적이면 제3자 재실행이 곧 반증) ③ **외부 시스템 발급 상관 ID**(발급자가 에이전트가 아님 — 최강). 4축 중 3축의 최선 payload 가 **이미 다른 규율이 생성 중인 부산물**(ADR-119 `source:` / Story §5.7 매핑)이므로, 설계는 신규 저작 부담이 아니라 **기존 부산물의 결속**으로 간다.

**tier 는 진실성을 사지 못한다**: payload 필드의 tier 를 올려도 바뀌는 것은 오직 "필드가 **비어 있을 때** 머지가 막히는가" 뿐이며 **위조된 payload 는 어느 tier 에서도 통과**한다. 따라서 tier 승격은 본 ADR 의 완화 경로가 아니다. `declared` tier 의 실효는 "차단" 이 아니라 **감사 표면의 생성**(사후 표본 감사가 대조할 대상이 생김)이며, 그 실효는 non-zero 다. 승격을 원하면 **payload 누락률 자체를 재측정 관측 항목으로 등재**해 후속 carrier 가 ADR-171 §결정 6 의 증거로 쓰게 한다.

### 결정 5 — `ac-decomposition-completeness` 는 감사 가능성 면에서 구조적으로 유일하게 튼튼하다

이 축은 4축 중 **유일하게 무조건 발동**이며, 따라서 **`applicable` 이 상수 true** 다. `applicable` 이 상수인 축에서는 §결정 4 가 특정한 단일 결정불가 지점이 **존재하지 않는다** — 기록자가 그 필드로 거짓말할 값 공간이 없기 때문이다.

⇒ **self-attestation 위조 표면이 구조적으로 0.** 스키마는 이 축의 `applicable` 을 상수 true 로 고정하고, `applicable ≠ true` 로 기록된 해당 축 레코드는 즉시 기계 검출한다.

이 사실은 별도로 기록할 값어치가 있다. "유일한 무조건 축" 이라는 성질이 **감사 가능성 측면에서도 유일하게 튼튼함**을 뜻하며, 나머지 3축의 완화가 왜 상한을 가질 수밖에 없는지를 대조로 설명해 준다. 동시에 이 축은 4위치 중 계약 `findings[].type` enum 에만 리터럴이 없는 **선례 비대칭** 상태다 — 같은 방식으로 신설된 두 축 중 뒤에 온 것만 양쪽에 배선됐다. 따라서 이 축의 리터럴 추가는 발명이 아니라 **직전 선례와의 대칭 복원**이다.

### 결정 6 — born-red 회피: **동시 수리(원자 착지)가 default, warning-tier 는 fallback**. 기존 step 에 `continue-on-error` 부착은 금지

`invariant-check` 는 branch protection required 8-tuple 의 구성원이다. 실재 drift 를 남긴 채 게이트 정의역만 넓히면 required context 가 즉시 RED 가 되어 **이 변경 자신의 PR 이 머지 불가**가 된다.

| 안 | 구현 | 기존 3 lane 보호 | 판정 |
|---|---|---|---|
| **W1 — 동시 수리** | 정의역 확장 + 실 drift 수리를 **한 원자**로 착지 | 무손상 | **default** |
| **W2 — 분리 step warning-tier** | 확장분만 **별도 step** 으로 분리하고 그 step 에만 `continue-on-error: true` | 무손상 (기존 step 무접촉) | **fallback** |
| **W3 — 기존 step 에 `continue-on-error`** | 1행 추가 | **동반 상실** | **금지** |

**W3 금지 근거**: `continue-on-error` 는 **step 단위 키**이고 현행 게이트는 4 lane 전부가 하나의 `LANES` 리스트·하나의 step 안에 있다. 그 step 에 붙이면 `design`/`code`/`security` 3 lane 의 강제도 **함께** 사라진다 — 대상 lane 하나를 비차단으로 만들려던 조치가 **이미 작동 중인 3 lane 보호를 동반 상실**시킨다. 이는 **ADR-058 §결정 5 보호강도 비축소 ratchet 정면 위반**이다. `source:` [GitHub Docs — Setting exit codes for actions / continue-on-error](https://docs.github.com/en/actions/creating-actions/setting-exit-codes-for-actions)

**W1 이 default 인 이유**: 수리 대상 결손이 전부 문서·workflow 편집이라 같은 PR 안에서 닫힌다. warning-tier 는 "drift 를 지금 못 고칠 때" 의 경로이므로 지금 고칠 수 있으면 fallback 이다. 신규 required context 신설도 하지 않는다(8-tuple 무변경) — 신규 context 승격은 7일 green 재적립 chicken-egg 를 밟는다.

**W2 채택 시 부관 (승격 조건 명시 의무)**: ① 승격 게이트 = ADR-171 §결정 6 의 **3-AND**(PR 누적 하한 ∧ bypass 외 failure 0 ∧ sibling 조건) ② baseline 동결로 창 이후 **신규 유입만** failure 집계 ③ **기한 없는 advisory 상주 금지** — 승격 trigger 를 "drift 가 전부 수리된 최초 실행(불일치 0 방출)" 으로 못박고 그 조건이 기계 판정 가능해야 한다. 그렇지 않으면 hollow-gate 로 퇴화한다 ④ **정직 상한**: 창 동안 그 게이트는 **관측만 한다**. "게이트가 있으니 drift 가 막힌다" 는 창 안에서 거짓이다 — 실효는 가시화뿐 ⑤ **승격 ≠ required 편입** — `continue-on-error` 제거는 required contexts 멤버십을 함의하지 않는다.

**정의역 밖에 남기는 표면 1건 (침묵 금지)**: PL 파일 손열거 × `contract_version` 정확 일치 술어는 본 변경에서 **확장하지 않는다**. 이유는 방향이 반대이기 때문이다 — 다른 세 지점은 "대상 lane 을 SSOT 에 맞춘다" 가 수리이지만, 이 지점은 **PL 쪽이 앞서 있어**(`1.1`) "PL 을 `1.0` 으로 되돌린다" 가 **회귀**다. 옳은 수리는 게이트 술어를 lane-aware 로 바꾸는 것이고 그 판단은 계약 소유 축(ADR-008)에 속한다. **이 절단과 사유를 명시 기재한다** — 침묵하면 "주장 범위 > 검사 정의역" 의 자기재현이다.

### 결정 7 — 파서 규율 3항 (P-1 상한 · P-2 앵커 유일성 · P-3 정화 선행)

축 식별자 정합 게이트가 문서 문면에서 값을 추출하는 한, 게이트의 입력은 **신뢰할 수 없는 텍스트**다. 아래 3항은 **실행 가능 mutant 으로 실증된 3 경로**를 각각 겨눈다.

| 규율 | 내용 | 겨누는 실증 경로 |
|---|---|---|
| **P-1 — 추출 구간 상한(terminator) 의무** | 앵커 이후 추출은 **다음 섹션 경계에서 종료**한다. 상한 없는 `.*?` + DOTALL 금지 | **타 lane 값 차용**. 앵커된 lane 블록에 값 집합이 없으면 게이트는 NO-MATCH(fail-closed) 가 아니라 **다음 lane 의 집합을 가져와** 비교한다 — mutant 실행 결과 한 lane 의 추출 산출이 다른 lane 의 정본 집합과 동일해졌다. 이것은 은닉(커버리지 결손)이 아니라 **오귀속(거짓 판정)** 이다 |
| **P-2 — 앵커 매치 수 ≠ 1 이면 오류로 종결** | 앵커가 0개면 fail-closed, **2개 이상이어도 fail-closed**. first-match-wins 금지 | 대상 lane 의 `#### lane=` 헤딩이 **2회** 등장하고(정본 + `variant: runtime-failure`) 헤딩 5 : 집합 4 의 비대칭이 실재한다. 현행 게이트는 우연히 1번째를 잡아 정답이나, **헤딩 순서 변경·변종 블록에 집합 추가·변종을 정본으로 지정** 중 무엇이든 판정을 뒤집는다. **구성이 아니라 우연으로 맞다** |
| **P-3 — 주석은 값 정규식 도달 전에 제거** | 1단(블록 추출) → **주석 제거** → 2단(값 추출) 순서를 강제. raw 텍스트 재스캔 금지 | 주석 본문의 `review-verdict-v4` 에서 `verdict-v` 가 카테고리로 **민팅**된다. 완화 정규식 3변종 전건에서 동일 phantom 이 나왔다 ⇒ 결함은 *어떤 완화를 골랐는가* 가 아니라 **2단 재스캔 구조 자체**다. 1단을 아무리 정교하게 완화해도 2단이 raw 텍스트를 다시 훑는 한 표면은 닫히지 않는다 |

**P-1 은 단독으로 부족하다** — lazy 매칭은 앵커 이후 **첫 번째** 값 집합을 취하는데 그 첫 번째가 정본이라는 보장이 없다. 프롬프트 템플릿 파일에서 **예시를 적는 것은 정상적이고 권장되는 저작 행위**이므로, 산문 예시가 정본 enum 을 선점하는 경로는 침투 시나리오가 아니라 **평상시 문서 개선 행위로 발동**한다(악의 가정 불요). ⇒ 정본 집합은 **산문과 구별되는 표지**(fenced block 또는 지정 키)로 지목되어야 한다.

**정직 상한 — 정규식 안전성 단정 없음**: 본 ADR 은 신설 정규식의 ReDoS 안전성을 주장하지 않는다("catastrophic backtracking 0" 류 단정 금지). 최종 형태·벤치마크·reproducer 가 본 ADR 의 산출이 아니기 때문이다.

### 결정 8 — 손열거 대신 파생. 단 「폐쇄 검사」의 독립성 주장은 **2축 + 1축**으로 좁힌다

게이트가 다루는 4-tuple(`lane_id`, SSOT checklist 파일, PL 파일, Codex 앵커 토큰)을 **손으로 적은 매핑표**로 두지 않는다. 손으로 적은 열거는 「파생 규칙」이라 이름 붙여도 파생하지 않으며, 그 표 자체가 새로운 drift 표면이 된다.

**규칙 문면을 리터럴로 실행한 결과 4-tuple 전부가 repo 안에서 이미 파생 가능하다** — PL 파일 glob → 각 파일의 정본 `review_packet` 블록(`variant:` 키 **부재**가 정본 술어) → 그 블록의 `lane` 과 `checklist_path`. 파생 산출은 4 lane · anomaly 0 이었고, 손열거(3)와의 **차집합이 곧 drift**(파생에만 존재 = 대상 lane)였다. 부수 효과로 경로 비대칭(lane_id ↔ 파일명)이 자동 해소된다 — 비대칭 파일명이 PL 파일의 `checklist_path` 에 **이미 정본으로 적혀 있고** 파생식이 그것을 읽기 때문이다.

**폐쇄 검사(파생의 필수 짝) — 독립성 주장을 정확히 적는다.** 파생식만으로는 "레지스트리가 현실보다 좁다" 를 막지 못하므로 독립 정의역과의 대조 1본을 붙인다. 그러나 그 대조의 독립성은 **"3정의역 상호 검증" 이 아니다**:

> **정확한 서술 = 2축 검증(`lane_id`: 파생 ↔ Codex 헤딩 토큰) + 1축 검증(파일 참조 무결성: 파생 `checklist_path` ↔ checklist 파일).**
> 대조 전에 `checklist_path` 로 매핑하지 않으면 **경로 비대칭(lane_id ↔ 파일명 stem)이 거짓 불일치로 보고**되며, 어긋나는 1원소가 하필 본 작업이 추가하려는 바로 그 lane 이다.
> 1축 검증이 잡는 것 = **orphan**(참조되지 않는 checklist 파일) + **dangling**(참조하는데 대상 부재). 잡지 못하는 것 = **`lane_id` 자체의 drift** — 그건 2축 검증 담당이다.

이 문면은 실행으로 확정됐다: 문면 그대로의 3정의역 직접 대조 = **거짓 양성**, `checklist_path` 경유 매핑 후 = 양측 공집합(양성 대조군 성립), 정본 packet 제거 mutant 와 미참조 checklist 신설 mutant **2본 모두 검출**(음성 대조군 성립).

**정직 상한 — 이것이 파생의 상한을 보여주는 첫 실례다**: 파생화는 「손열거 4곳 → 1곳」이 아니라 **「손열거 4곳 → 0곳 + 술어 1개」**다. 그러나 술어 자체(정본 packet = `variant:` 키 부재)는 여전히 **저작된 규약**이며, 규약이 현실과 어긋나면(예: 세 번째 packet 종류 등장) **파생은 조용히 틀린다**. 이 경고는 추상 우려가 아니다 — 같은 절에 붙어 있던 폐쇄 검사가 정확히 그 방식으로 틀렸고(이름은 "3정의역 상호 검증" 인데 실제 정의역은 값 공간이 어긋남), 그것이 **봉합 안쪽 재발**의 실물이다. **"100% 기계강제" 아님** — 폐쇄 검사는 잔여를 좁히지만 없애지 않는다.

### 결정 9 — Amendment 발동 여부를 **전건 명시 기재**한다 (침묵 = 누락으로 읽힌다)

접촉 가능 ADR 중 **Amendment 가 실제로 발동하는 것은 ADR-125 1건**이다. 나머지는 조건 회피가 성립했다. 회피 판정을 침묵하면 후속 감사자가 "검토 누락" 으로 읽으므로 전건 기재한다.

| ADR | Amendment 의무 발생 조건 | 본 설계의 판정 | 발동 |
|---|---|---|---|
| **ADR-125** | §결정 6 을 선언 → 실 판정 분기로 승격 | **정면 해당** — 본 ADR 의 이행 대상 | **발동 — Amendment 5** |
| ADR-163 | 관측 채널이 measurement channel 목록에 새 row 로 편입될 때 | 신규 채널 **기각**(§결정 1) — 기존 채널 payload 에 얹는다 | 미발동 (조건 회피) |
| ADR-031 | 발동 기록을 §14 12-field schema 에 얹을 때 | §14 **미사용 확정**(§결정 1 — outcome enum 붕괴 + cardinality 불일치). lane 7→8 수리는 별 carrier 진행 중이라 재차 착지 = 상충 | 미발동 |
| ADR-170 | 기록 write 주체로 **5번째 inline sub-scope 를 추가**할 때 | §9 는 **기존 sub-scope 재사용** ⇒ closed enum 무접촉 | 미발동 — **단 조건절 존치**: ADR-182 신규 증적 섹션 대안을 채택하면 그 섹션은 현행 열거 어디에도 속하지 않으므로 **5번째 추가 = Amendment 확정 발동** |
| ADR-182 | 신규 증적 섹션에 착지시킬 때 | status = **`Accepted`**(firsthand 확인 — `Proposed` 아님). 그러나 섹션 **번호가 미확정**이라 지금 의존 불가 | 미발동 (이관은 후속 판단) |
| ADR-008 | 계약 필드·enum 을 건드릴 때 새 판례가 생기면 | 본 변경의 두 bump 전건이 **기존 §결정 2 문면을 그대로 적용**(선택 필드 추가 + enum 값 추가 = MINOR). 새 판례·예외 0 | 미발동 |
| ADR-155 | `dev-process-event-v1` 로 accounting 을 재기록할 때 | 채널 자체 **기각**(§결정 1 — 정면 위반) | 미발동 |
| ADR-171 | warning-tier 승격 경로를 쓸 때 | W1(동시 수리) default ⇒ warning-tier 창 미발생 | 미발동 — W2 fallback 채택 시 **인용**(승격 3-AND). 인용은 Amendment 가 아니다 |

**write 주체 선택은 정직 상한을 완화하지 않는다 (오귀속 차단)**: 층2 의 write 주체를 Orchestrator 로 두는 이유는 §결정 4 의 자기보고 문제 완화가 **아니라** ① 기존 sub-scope 재사용으로 Amendment 비용 회피 ② Story 파일 append-only 무결성이다. 값을 결정하는 주체(review PL·워커)와 파일에 쓰는 주체(Orchestrator)는 **별개 축**이며, 전사 시점에 값의 진위를 독립 재검증하는 절차는 본 설계에 없다. "write 주체를 Orchestrator 로 했으니 억지 발동 문제가 완화됐다" 는 **over-claim** 이다.

**번호 발급 경로**: `adr_number: 184` = ADR-133 §결정 4 fallback(설계 lane 제약상 claim state-branch push 불가) 하의 **3-leg firsthand 실측** — ① 파일 실재 최대 = 182 ② RESERVATION 요약표 row 최대 = 171(**stale**) ③ open PR 점유 = 183. `max(file)+1 = 183` 과 `max(registry)+1 = 172` 는 **둘 다 틀린다**. 명령·산출은 §자기적용 1. **merge 직전 3-leg 재실행 의무** — 값이 달라지면 파일명·frontmatter `adr_number`·registry row 를 전부 갱신한다(claim 은 잠정, 착지가 확정).

## 자기적용 — 본 ADR 저작 중 발현·검출한 동형 결함 3건

본 ADR 은 "**검사 장치의 정의역이 그 장치의 주장 범위와 어긋나면, 장치는 초록불을 내면서 아무것도 재지 않는다**" 를 고발한다. 저작 과정 자체가 그 class 를 3회 더 산출했고, 셋 다 **저작 규율(규칙 문면을 리터럴로 실행해 산출과 기재를 대조)** 이 잡았다.

**1. ADR 번호 3-leg — naive 계산 2종이 모두 틀린다 (재현)**

```sh
W=<wrapper worktree>; git -C "$W" fetch origin main -q
git -C "$W" rev-parse origin/main                                    # 7a12d0a0f
git -C "$W" ls-tree --name-only origin/main archive/adr/ | grep -oE 'ADR-[0-9]+' \
  | grep -oE '[0-9]+' | sort -n | tail -1                            # leg1
git -C "$W" show origin/main:archive/adr/ADR-RESERVATION.md \
  | grep -oE '^\| ([0-9]+) \|' | grep -oE '[0-9]+' | sort -n | tail -1   # leg2
for n in $(MSYS_NO_PATHCONV=1 gh pr list --repo mclayer/plugin-codeforge --state open \
             --json number --jq '.[].number'); do
  MSYS_NO_PATHCONV=1 gh api --paginate "repos/mclayer/plugin-codeforge/pulls/$n/files" \
    --jq '.[] | select(.filename|test("archive/adr/ADR-[0-9]+")) | select(.status=="added") | .filename'
done                                                                  # leg3
```

산출 = leg1 `182` · leg2 `171` · leg3 `183`(open PR 점유). ⇒ 다음 가용 = **184**. **미머지 브랜치를 정의역에 넣지 않으면 정확히 이 충돌이 재발한다** — leg3 부재가 곧 "검사 정의역이 주장 범위보다 좁다" 의 발현이다.

**2. 결정 서수 추출기 — 옳은 수를 틀린 경로로 산출했다 (가장 나쁜 형태)**

선행 산출이 문서화한 추출 명령 `grep -nE '^#{2,4} .*결정 [0-9]+' <file> | grep -v 'ADR-[0-9]'` 을 ADR-125 에 리터럴 실행하면 **`결정 1·2·3` 과 `#### 결정 A`·`#### 결정 B` 5행**이 남고 최대값 6 이 나온다. 그런데 배제 필터 없는 실행은 **`### 결정 1` ~ `### 결정 6` 6개 헤딩**을 낸다.

⇒ 문서화된 추출기는 실 헤딩 `결정 4`·`결정 5`·`결정 6` 을 **전부 탈락**시킨다(세 헤딩 제목이 각각 다른 ADR 번호를 인용하므로 교차인용 배제 필터에 걸린다). 그리고 `#### 결정 B — §결정 6 scope 확장…` 이라는 **Amendment 헤딩 안의 교차인용**에서 6 을 주워 최대값을 맞춘다. **수는 맞고 경로는 전부 틀렸다** — 산출과 기대가 일치하므로 어떤 불일치 신호도 발생하지 않는다. 이것이 본 ADR §결정 7 P-2(앵커 매치 수 ≠ 1 이면 오류로 종결)가 필요한 이유의 ADR-저작 층 실례다.

**3. 번호 ↔ 주제 대응은 자명하지 않다 — 인용 전 파일을 연다**

`ADR-044` 의 실 파일명·title 은 **`ADR-044-phase-scoped-sequential-team.md` / "Phase-scoped sequential team SSOT"** 이다. 그런데 본 ADR 이 §결정 1·4 에서 인용하는 근거(peer floor `SoD: implementer ≠ certifier`, `peer_verdicts[]` optional array)는 그 body 에 **실재한다** — Amendment 로 누적된 것이다. **title 만 보고 "주제 불일치 = 오인용" 으로 판단했다면 옳은 인용을 거짓으로 기각했을 것**이고, 반대로 확인 없이 옮겼다면 「지목한 절이 실재하는 경우」(감사자가 "이미 정정됨" 으로 읽는 최악의 앵커 오류)를 재현했을 것이다. ADR-170·ADR-171·ADR-182 도 동일 절차로 firsthand 확인했다(§관련 파일 하단).

## 결과

- 요구사항리뷰 4축의 발동 여부가 **라운드 단위로 기계 집계 가능한 형태**로 남는다 — 층1(packet optional array) + 층2(Story §9 확장). 신규 measurement channel 0, 신규 required CI context 0, FROZEN schema 접촉 0.
- **무발동 은폐**는 기계 식별 대상이 된다. **억지 발동은 자기모순형만** 기계 식별되며, `applicable` 진리성은 **원리적 결정불가**로 명시 잔존한다 — 완화(dual-peer · 표본 감사 · 3-tuple 교차)는 **불일치 검출이지 진리 검증이 아니다**.
- `ac-decomposition-completeness` 는 `applicable` 상수 true 로 **self-attestation 위조 표면이 구조적으로 0** — 4축 중 유일하게 감사 가능성이 온전하다.
- 게이트 정의역 확장은 **실 drift 동시 수리와 한 원자**로 착지한다. 기존 step 에 `continue-on-error` 를 붙이는 경로는 **금지**(3 lane 보호 동반 상실 = ADR-058 ratchet 위반).
- 축 식별자 4-tuple 은 손열거가 아니라 **파생 + 폐쇄 검사**로 유지되며, 폐쇄 검사의 독립성은 **2축 + 1축**으로 정확히 서술된다.
- ADR-125 Amendment 5 가 동일 PR 로 착지해 §결정 6 declarative-only 를 실 판정 분기로 승격한다. **다른 7 ADR 은 Amendment 미발동** — 조건 회피 판정을 §결정 9 표에 명시 기재했다.

**미해소 긴장 (후속 판단 대상, 본 ADR 이 닫지 않는다)**

| # | 긴장 | 현 처분 |
|---|---|---|
| 1 | ADR-182 신규 증적 섹션으로의 **이관 의무를 규범으로 박을지** | 관찰 기재. 지금 박으면 본 작업이 미착지 섹션의 착지 순서에 종속된다(계측기가 개입보다 먼저 착지해야 한다는 원칙에 역행). 채택 시 ADR-170 Amendment 확정 발동 |
| 2 | PL 파일 × `contract_version` 술어의 **lane-aware 전환** | 본 변경 정의역 밖 — 계약 소유 축(ADR-008) 판단. §결정 6 말미에 절단과 사유를 명시 기재해 침묵을 방지했다 |
| 3 | 파생 술어(`variant:` 키 부재 = 정본)가 **현실과 어긋날 때의 조용한 오작동** | §결정 8 정직 상한으로 잔존. 폐쇄 검사가 좁히지만 없애지 않는다 |
| 4 | RESERVATION 요약표가 **ADR-171 이후 stale** (row 없는 실재 파일 다수) | **관찰만**. 본 작업의 강제 요인이 아니며(3문 게이트 미충족) follow-up 을 발의하지 않는다. 실무 귀결 = **레지스트리를 단독 정본으로 쓰면 오판한다** — 3-leg 중 leg1·leg3 이 실질 정본, leg2 는 보조 |

## 관련 파일

| 경로 | 관계 |
|---|---|
| `archive/adr/ADR-125-requirements-review-lane.md` | **Amendment 5 동반 착지** — §결정 6 승격 + 4축 관측 레코드 의무. 본 ADR 의 유일한 amend 대상 |
| `plugins/codeforge-review/agents/RequirementsReviewPLAgent.md` | 4축 실배선 · `category_enum` · `review_packet` 2블록(정본 ∧ `variant: runtime-failure`). 층1 producer |
| `plugins/codeforge-review/templates/review-checklists/requirements.md` | 축 식별자 SSOT. 파일명 ↔ `lane_id` 비대칭의 정본 매핑원 = PL 파일 `checklist_path` (§결정 8) |
| `plugins/codeforge-review/agents/CodexReviewAgent.md` | peer 프롬프트 — `#### lane=` 헤딩 5 : `category from {` 집합 4 (§결정 7 P-1/P-2 실증면) |
| `docs/inter-plugin-contracts/review-verdict-v4.md` | 층1 `axis_activation[]` optional array 착지 계약 (ADR-008 §결정 2 MINOR) |
| `.github/workflows/invariant-check.yml` | category/severity parity 게이트 — 정의역 확장 + 파서 규율 적용 대상 (§결정 6·7·8) |
| `templates/story-page-structure.md` | 층2 — §9 요구사항리뷰 전용 서브섹션 신설 대상 |
| `archive/adr/ADR-RESERVATION.md` | `adr_number: 184` row 등재 (§결정 9 발급 경로) |

**firsthand 확인한 인용 대상 (번호 ↔ 주제 대응, 기준 SHA `7a12d0a0f`)**

| ADR | 실 파일명 | title (verbatim) |
|---|---|---|
| ADR-044 | `ADR-044-phase-scoped-sequential-team.md` | Phase-scoped sequential team SSOT (CFP-134 Epic Wave 2) — **body 에 peer floor·`peer_verdicts[]` 실재** |
| ADR-170 | `ADR-170-orchestrator-subagent-default-inline-whitelist.md` | Orchestrator subagent default … binary always-spawn + inline whitelist (ADR-039 재제정) |
| ADR-171 | `ADR-171-evidence-enforceable-promotion-framework.md` | Evidence-enforceable promotion framework … (ADR-060 재제정) — §결정 6 = 승격 gate (binary, AND condition) |
| ADR-182 | `ADR-182-review-domain-write-domain-separation.md` | 리뷰 심사 정의역·FIX 증적 정의역 분리 … — **status = `Accepted`** |

## 해소 기준

N/A — permanent policy.

본 ADR 은 전환기 조치가 아니라 **관측 레코드의 영구 계약**이다. 축 레코드의 2층 구조·라운드 정의역·4상태 taxonomy·정직 상한은 요구사항리뷰 lane 이 존속하는 한 유효하며, lane 자체가 재편되면 그 재편 carrier 가 본 ADR 을 supersede 한다(개별 조항의 시한 해소가 아니라 상위 lane 규범과 함께 처분된다).

단 **§결정 6 의 W2(warning-tier) 를 fallback 으로 채택한 경우에 한해** 그 advisory 분기는 전환기 조치이며, 승격·제거 조건은 ADR-171 §결정 6 의 3-AND 를 따른다(본 ADR 이 별도 시한을 두지 않는다 — 기한 없는 advisory 상주 금지 부관이 §결정 6 에 명시돼 있다).
