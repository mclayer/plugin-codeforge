---
adr_number: 180
title: Story 성장축 외부화 — 읽기 표면 분할 + 실읽기량 목적함수
status: Proposed
is_transitional: false
category: Process
date: 2026-08-15
carrier_story: CFP-2986
related_adrs:
  - ADR-058  # §결정 5 count cap 거부 — 본 ADR 이 "차단 아닌 신호" 통로로 우회 (거부 선례 무손상)
  - ADR-167  # §결정 6 "차단이 아닌 재제정 의무 신호" — 본 ADR 이 사용하는 유일 통로
  - ADR-142  # L1 read 위임 + carve-out CLOSED 6항 — Orchestrator read 경로 무변경 제약의 출처
  - ADR-171  # evidence-enforceable promotion framework — required 승격 3-AND 사전조건
  - ADR-130  # §결정 6 7일-green 창 (repository 단위) + unique job name 의무
  - ADR-127  # 모든 변경 Story 의무 + §결정 5 산출물 target 부재 N/A
  - ADR-119  # 검증-후-단언 — 무출처 단정 금지, honest-ceiling 라벨
  - ADR-006  # Amendment 2 엣지케이스 tier A always-active
  - ADR-005  # plugin-meta-na — CONDITIONAL deputy N/A 근거
related_files:
  - archive/adr/ADR-058-adr-sunset-criteria-mandate.md
  - archive/adr/ADR-167-adr-amendment-compaction-ratchet.md
  - .github/workflows/ac-traceability-matrix.yml
  - scripts/check-claude-md-line-cap.sh
related_stories:
  - CFP-2986
  - CFP-2984  # 병렬 A — 실패·재시도 축 (파일면 서로소)
  - CFP-2985  # 병렬 B — FIX 계측 축 (§10 필드 정의 소유)
---

# ADR-180: Story 성장축 외부화 — 읽기 표면 분할 + 실읽기량 목적함수

## 상태

`Proposed` (2026-08-15 KST) — CFP-2986 Phase 1 설계 lane draft. ArchitectPLAgent 직접 작성 (chief author spawn 이 산출물 미착지 → PL synthesizer 통합 저작, env=0 fallback 동형). adr_number = ADR-133 claim primitive 반환값 **180** (state branch `adr-reservation-state` OCC — 175~179 는 CFP-2963 / CFP-2978 / CFP-2949 / CFP-2966 / CFP-2984 가 선점 실측, 파일시스템 max+1(175) 사용 시 충돌).

## 맥락

Story file 이 lane 마다 반복 읽히는데 비대해져 읽기 단가가 오른다. 요구사항 lane 이 4 라운드 리뷰를 거쳐 확정한 실측 (기준 트리 `4ce40368`, 매체 LF `git archive`, 정의역 `wrapper/stories/*.md` 576건):

- Δ_total = 60.5457 KB (avg 2800+ 92.84 KB − avg 1-999 32.30 KB)
- 귀속 1위 = **§9 품질게이트 이력 21.0%** — 단 **delta base 한정**. 정적 전 코퍼스 base 에서는 §4 13.17% > §5 12.34% > **§9 12.23% (3위)**
- FIX 축: §9 = 원장 0행 2.65 KB → 3-5행 10.70 → **6행+ 41.67 KB**

### 같은 비용을 겨냥한 선행 처방이 전부 실패했고, 실패 원인이 두 축이다

**축 A — 집행 수단이 reader 자율 준수**: P1 `templates/story-page-structure.md` 읽기 규약 / P2 playbook §12 섹션 캐시 / P3 ADR-142 L1. 셋 다 `Read` 도구에 섹션 주소지정이 없어 **원리적으로 강제 불가**. `Read(파일)` 는 파일 전체를 연다.

**축 B — 집행이 있어도 일회성이거나 단위가 어긋남**:
- CFP-2211 — 237줄 압축이 2개월 만에 1,367 → 1,585 로 **+31.8% 복귀**
- `scripts/check-claude-md-line-cap.sh:8` `CAP=320`(**줄수**) — 게이트 GREEN 인 채 CLAUDE.md 가 76,957 B(`bd321fb9`) → 140,396 B(`f2e78b16`) **+82.4%** 성장. B/줄 244 → 438. **줄을 길게 써서 게이트를 만족시켰다.**

⇒ **4번째 reader-side 규약은 4번째 실패이고, 일회성 압축은 반감기를 상속한다.**

### 크기 hard cap 은 이미 거부된 shape

ADR-058 §결정 5 가 count cap 을 "정당한 사례까지 차단할 위험" 으로 거부했다. ADR-167 §결정 6 이 그 거부를 유지하면서 남긴 유일한 통로가 **"차단이 아닌 의무 신호"** 다.

---

## 결정

### §결정 1 — 목적함수는 파일 크기가 아니라 lane 진입당 실읽기 바이트다

측정 단위는 **처방이 줄이겠다고 선언한 양과 동일**해야 한다. **줄수 · heading 수 · 섹션 수 · 자식 포함 총 바이트를 판정 단위로 채택 금지.**

> **금지 단위의 정확한 외연 (협착 — 설계리뷰 R1 P1-2)**: 금지 대상은 **`bytes(parent) + Σ bytes(children)`(자식 포함 총 바이트)** 이지 `bytes(parent)` 가 아니다. 자식 포함 총량은 **pure move 하에서 항등**이므로(분할은 바이트를 부모에서 자식으로 옮길 뿐 총합을 보존한다) 처방의 효과를 원리적으로 0 으로 계상한다 — 섹션 단위 집계를 기각한 것과 **정확히 같은 사유**다. 반면 `bytes(parent)` 는 아래 `read_cost` 의 **주항**이며 정당한 피연산자다. AC-21 이 열거하는 3종(줄수·heading 수·섹션 수)에 본 항목을 더한 4종이 금지 집합이고, 확대분은 자기 공식의 주항이 아니라 **총합 형태**에 한정된다.

근거는 `claude-md-line-cap` 의 실패가 "줄수라서" 가 아니라 **"선언한 양과 재는 양이 달라서"** 라는 데 있다. 자식 포함 총 크기도 같은 함정이다 — 우리가 줄이겠다고 선언한 것은 저장량이 아니라 읽기 단가다.

```
read_cost(story) = Σ_{r ∈ readers} [ bytes(parent) + Σ_{c ∈ children : opens(r,c)} bytes(c) ]

opens(r,c)  ⟺  r 이 read-declaration registry 에 미등재      (보수 default)
              ∨  declares(r) ∩ carries(c) ≠ ∅
```

**집계 경계는 파일이다 — 섹션 단위 집계는 채택하지 않는다.** 섹션 단위 형태 `Σ_섹션(섹션바이트 × 선언 독자 수)` 는 **분할 개입에 대해 항등**이다: §9 을 자식으로 옮겨도 §9 의 바이트도 §9 을 선언한 독자 수도 불변이므로 항이 정확히 0 만큼 변한다. 그 공식은 이미 "독자는 선언한 섹션만 읽는다"를 **가정**하는데, 바로 그 가정이 거짓이라는 것이 본 ADR 의 출발점이다(`Read` 는 파일 전체를 연다). 분할의 가치는 **선언하지 않은 섹션을 물리적으로 안 열게 만드는 것**인데 섹션 단위 집계는 그 비용을 처음부터 0 으로 계상한다.

⇒ **단위를 바이트로 맞추는 것만으로는 부족하고 집계 경계가 집행 경계와 같아야 한다.** 이것이 본 결정의 핵심이며, 어긋나면 `claude-md-line-cap` 과 같은 class 의 실패가 한 층 안쪽에서 재발한다(게이트가 항상 0 을 보고).

**보수 default**: 미등재 reader 는 모든 자식을 여는 것으로 계상한다 ⇒ 레지스트리 불완전은 비용을 과대 계상할 뿐 과소 계상하지 않으며, 불완전성이 거짓 "개선" 판정을 만들 수 없다.

> **따름정리 — 빈 레지스트리에서는 채택 공식도 항등이다 (설계리뷰 R1 P1-1)**: 보수 default 는 미등재 reader 에 대해 `opens(r,c) = true` 이므로, 레지스트리가 비면 `d = N` 이 되고 `read_cost = N × (bytes(parent) + Σ bytes(children))` = **자식 포함 총 바이트의 N 배** 다. pure move 는 그 총합을 보존하므로 **모든 분할 개입에 대해 Δ = 0** — Phase 1 에서 기각한 섹션 단위 공식과 같은 자리로 퇴화한다. 절감량은 커버리지의 함수이며 정확히 `Δ = −(N − d) × bytes(child)` 다 (PL firsthand 실행 확인: `N=8, child=50,000` 에서 `d=8` → Δ=0 / `d=4` → −200,000 / `d=1` → −350,000).
>
> ⇒ **레지스트리는 술어의 부속물이 아니라 술어의 정의역이다.** 커버리지 하한 미달 시 게이트는 "절감 0"(= 판정) 이 아니라 **`UNDETERMINED`(= 판정 불가)** 를 방출해야 하며, 이 구별이 없으면 day-1 에 AC-1 이 공허 통과하고 AC-5 는 충족 불가가 된다. 하한과 방출 규약은 §결정 8 Phase 2 산출물의 **필수 동반 항목**이다 (하한 미정의 상태로 배선 금지).

**정직 상한**: 이것은 **선언된** 읽기 비용이다. 선언과 실제 agent 거동의 일치는 `Read` 에 집행면이 없어 기계 검증 불가 — **attested, not verified**. "실제 읽기량을 잰다"고 주장하지 않는다.

**파일 경계가 실읽기량의 유일한 집행 가능 경계다** — `Read` 가 파일 단위로 열리므로, 섹션을 파일 밖으로 내보내는 것만이 "안 읽게" 만든다. 이것이 축 A(reader 자율)를 구조적으로 회피하는 유일한 경로다.

### §결정 2 — 처방은 압축이 아니라 **성장축의 이전**이다

append-heavy 섹션을 자식 파일로 외부화한다. 정보는 삭제하지 않고 **순수 이동(pure move)** 한다.

**자연 실험 (n=1, PL firsthand)** — 본 Story 자신에서 개입 없이 관측됐다. Orchestrator 가 §9.4a 를 append 한 전후를 같은 슬라이서로 실측 (`git show <sha>:wrapper/stories/CFP-2986.md`, LF, CR=0 양 트리 확인):

| | `fe43c9f0` | `e7d136cb` | Δ |
|---|---:|---:|---:|
| 총 크기 | 184,477 | 188,422 | +3,945 |
| §9 | 50,967 | 54,912 | **+3,945** |
| 그 외 10개 섹션 | — | — | **정확히 0** |
| §9+§10 분할 후 잔여 | **127,495** | **127,495** | **0** |
| §9-only 분할 후 잔여 | 133,510 | 133,510 | **0** |

**증가분 100% 가 §9 단독에 착지했고, 분할 후 잔여는 1바이트도 움직이지 않았다.**

⇒ parent 의 성장은 append-heavy 축에 **국소화**돼 있으며, 그 축을 외부화하면 parent 는 회차와 함께 자라기를 멈춘다. 코퍼스 상관(0행 2.65 → 6행+ 41.67 KB)은 교란 요인이 열려 있으나 본 관측은 **동일 파일 · 동일 슬라이서 · 단일 변인**이다.

**이것이 축 B 에 대한 반론이다**: CFP-2211 이 원복한 이유는 *압축*이었기 때문이다. 압축은 저작 압력이 그대로라 반감기를 갖는다. 본 처방은 **성장 축 자체를 옮기므로** 반감기 상속이 성립하지 않는다.

> **정직 조건 (ADR-119)**: ① **n=1 자연 실험**이며 반복 관측이 아니다. ② 관측 주체(Orchestrator)가 곧 수혜 축(§9)의 저작자라 **자기 선택 편향 가능성**이 있다. 다만 append 시점에 본 실험이 의도되지 않았고 §9.4a 는 **Codex peer 지연착지 흡수라는 독립 사유**로 저작됐다 — 편향 반론은 이 사실에 선다.

### §결정 3 — 규칙은 섹션 이름이 아니라 **섹션 성질 술어**에 keyed 된다

§1-§11 은 단일 부류가 아니다 (요구사항 lane §6.3 U4, 실측 확정):

- **이벤트 로그 계열** (§9, §10) — append-only · 시간순 · 항목 단위 · **재생 가능**
- **서사 문서 계열** (§4, §7, §5, §8, §2, §6) — 저작물 · 개정 대상 · **재생 불가**

*"단일 처방을 균일 적용하면 어느 한쪽은 반드시 정보 삭제 금지를 위반한다"* — 서사에 snapshot 적용 = 요약 정본화(손실) / 이벤트 로그에 크기 규약 적용 = 기록 누락(손실).

그런데 AC-19 는 규칙이 **특정 섹션 전용이 아닌 섹션 무관 일반 규칙**일 것을 요구한다. 해소:

> 규칙은 섹션 **identity** 를 참조하지 않고 섹션 **성질**(`append_only` / `regenerable` / `read_tier` / `splittable`)을 참조한다. 성질은 기계 판독 가능한 레지스트리에 선언되고, 예외 사유는 **폐쇄 enum `reason_code`** 로만 표기한다 (AC-10 — 자유서술 사유 불인정).

> **정직 고지**: 이는 **규칙 층의 일반성이지 효과 층의 일반성이 아니다.** 데이터 층에서 섹션 정체성이 되돌아오고 실 발화는 §9·§10 에 착지한다. AC-19 를 효과 층으로 읽으면 어떤 설계도 충족 불가하다 (귀속 편재가 실측 결론 자체이므로). 본 ADR 은 AC-19 를 **규칙 층**으로 해석하며, 이 해석의 타당성 판정을 설계리뷰 lane 에 회부한다.

### §결정 4 — 구간 경계는 **명시 앵커 쌍**이다

heading 기반 암묵 경계("다음 heading 까지")를 금지한다.

근거 1 — **margin 이 얇다** (실측): LEGC **5줄** / AUTHOR 24 / CORPUS 34 / SELF 38 / BASE 51. 인용블록에 5줄만 추가돼도 정상 저작이 false RED 를 맞는다. 경계가 **문서 구조 우연에 결합**돼 있다.

근거 2 — **h2 헤딩 슬라이싱은 구조적으로 취약하다.** 프로토타입 게이트에 실파일 변형을 투입한 실증 (대조군 M0 = RED, §9 = 50,967 B 확인 후). **§4.2.2a 정본 V1 슬라이서에서도 전건 GREEN**:

| ID | 변형 | 비용 | 결과 |
|---|---|---:|---|
| E-1 | heading `##` → `###` 강등 | **+1 B** | §9 = 0 B → **GREEN** |
| E-2 | `## ` 뒤 U+200B 1자 삽입 (렌더 동일) | +3 B | §9 = 0 B → **GREEN** |
| E-3 | §9 선두에 코드펜스로 `## 11.` 인용 → 슬라이서 조기 종결 | +65 B | §9 = 39 B → **GREEN** |
| **E-4** | §9 본문 전량을 §4 말미로 보상 이동 | **0 B** | §9 = **30 B**(heading 줄 잔여) → **GREEN**, 총량 완전 보존 |

**E-4 가 결정적이다**: read-cold §9 를 read-hot §4 로 옮기면 §4 가 53,653 → **104,590 B** 가 된다. **독자가 지는 읽기 부담은 악화되는데 섹션 cap 은 GREEN 이고 비용은 0 이다.** 악의를 가정할 필요도 없다 — 섹션 간 재배치는 저작자가 우연히 할 수 있는 정상 편집이다.

> **용어 주의 (설계리뷰 R2 P2-b)**: 위 문장의 "읽기 부담" 은 **비형식 서술**이며 §결정 1 의 형식 용어 `read_cost` 가 **아니다.** 채택 metric 은 file-granular 이라 E-4 에 대해 `Δ read_cost = 0`(아래 정정 주석) — 따라서 "실읽기량(=`read_cost`)이 악화된다" 고 쓰면 **문서 자기 정의어로 거짓**이 된다. 두 층을 분리 표기한다: 독자 체감(§4 를 읽는 사람이 실제로 넘겨야 하는 분량)은 악화되고, 선언된 목적함수 값은 불변이다. 이 괴리가 곧 E-4 의 방어를 목적함수가 아닌 **앵커 쌍 ∧ INV-S2** 에 귀속시켜야 하는 이유다.

⇒ **섹션 cap 단독 설계는 born-broken 이다.**

> **정정 (설계리뷰 R1 P0-1) — E-4 를 막는 것은 §결정 1 의 목적함수가 아니다.** 종전 기재("§결정 1 의 실읽기량 목적함수는 E-4 를 자동으로 RED 로 만든다 — §4 는 전 독자가 읽으므로")를 **철회한다.** 채택한 file-granular `read_cost` 는 자식이 없는 파일에서 `N × bytes(parent)` 이고 E-4 는 `bytes(parent)` 를 **정확히 보존**하므로 `Δ = 0` — **E-4 에 대해 중립**이다 (구성상 항등이며 실측 일치: `fe43c9f0` 총량 184,477 → 184,477, Δ=+0 [verified — PL firsthand, `git archive` LF, CR=0]). 철회 사유는 2중이다 — ① 괄호 안 근거("§4 는 전 독자가 읽으므로")는 **섹션×독자 가중** 논법인데 §결정 1 이 바로 그 집계를 기각했다(같은 ADR 안 배타). ② 그 문장은 §결정 8 의 자기 구속("술어 배선 전 게이트가 있다고 선언하지 않는다")을 정면으로 깬다.
>
> **E-4 의 실 방어 = 본 결정의 앵커 쌍 ∧ §8.4 INV-S2.** 앵커 쌍은 구간 경계를 문서 구조 우연에서 떼어내 E-1~E-3 계열을 차단하고, INV-S2 는 **앵커 델타 없는 총량 보존 하의 섹션 간 대량 이동**을 직접 검출한다. 정보 무손실 축은 INV-S1(pure-move digest)이 담당한다.

#### 불변식 발화 술어 — INV-S1 ∧ INV-S2 는 발화 조건이 상보적이다 (설계리뷰 R1 P1-5)

`digest(before.§n) == digest(after.§n ∪ children[n])` 을 **무스코프**로 적용하면 분할 이후의 정상 append 가 전부 `before ≠ after` 로 false RED 가 된다(born-broken). 이를 피하려 "분할 커밋 한정" 으로 좁히면 E-4 는 분할 커밋이 아니므로 **유일한 실 방어가 발화하지 않는다.** 양자택일이 모두 파손이므로 **판별 술어**를 명시한다:

```
anchor_delta(PR) = anchors(before) Δ anchors(after)        # cfp-split 마커 대칭차

INV-S1  발화 ⟺ anchor_delta ≠ ∅                            # 분할 / 역분할 / 앵커 재배치 커밋
        판정  for each section n ∈ sections(anchor_delta):
                 digest(before.§n) == digest(strip_stub(after.§n) ∪ children[n])

INV-S2  발화 ⟺ anchor_delta = ∅                            # 총량 조건 없음 (R2 P0-A 봉합)
        판정  RED ⟺ ∃ i≠j :  Δ§i ≤ −θ_move  ∧  Δ§j ≥ +θ_move
              (θ_move = 4,096 B — Phase 2 에서 코퍼스 분포로 재정)
              reason_code ∈ 폐쇄 enum 선언 시 RED → **신호**로 강등 (§결정 7 비차단 축)
```

> **봉합 (설계리뷰 R2 P0-A) — `∧ |Δ bytes(parent)| ≤ θ_total` conjunct 를 제거한다.** 종전 술어는 `anchor_delta = ∅` 반쪽 **안에서 다시** 총량으로 좁혀, **E-4 회피 비용이 정확히 65 바이트**가 되는 사각을 만들었다(경계 ±1 반전 실증: append 64 B → RED / **65 B → NOT_FIRED**). 정상 라운드 append 가 +19,167 B 이므로 **사각은 예외가 아니라 기본 경로**였다. θ_total 게이팅은 born-broken 회피에 **불필요**하다 — 순수 append 는 감소 섹션이 없어 `∃i: Δ§i ≤ −θ_move` 가 **정의상 거짓**이라 판정식만으로 이미 GREEN 이고, 게이팅은 검출력만 파괴했다. `θ_total` 상수는 본 결정에서 소멸한다.
>
> **정직 한정 (설계리뷰 R3)**: 위 born-broken 논거는 **순수 append 만 덮는다.** **혼합 편집**(한 섹션 감소 ∧ 다른 섹션 증가가 같은 커밋에 발생)은 감소 섹션이 실재하므로 발화하며, 본 Story 자신이 권고하는 보조 레버(중복 서술 제거 ∧ 설계 서사 증가)가 정확히 이 형상이라 **FIRED** 한다 [실행 확인]. 이는 결함이 아니라 **비차단 신호 축의 정의된 거동**이며 `reason_code: AUTHORED_CONSOLIDATION` 으로 흡수한다. 다만 그 흡수는 **저작자 선언에 의존**하므로 E-4 공격자도 같은 선언을 할 수 있다 — INV-S2 는 `reason_code` 하에서 **차단자가 아니라 기록자**로 퇴화한다. E-4 의 실 차단력은 **앵커 쌍 ∧ INV-S1**(무손실 축)이 진다. 전량 등재 = Change Plan §8.12 **축 B**.

두 발화 조건은 `anchor_delta` 를 기준으로 **상보 분할**이다 — **단 이 상보성은 `anchor_delta` 한 축에서만 참이며, 어느 한쪽 발화 조건에 다른 축의 conjunct 를 추가하는 순간 그 반쪽 안에 사각이 생긴다** (종전 `θ_total` 이 정확히 그 사례였다 — 설계리뷰 R2 P0-A). 봉합 후에는 `anchor_delta` 가 유일 판별자이므로 어떤 PR 도 양쪽 모두에서 빠져나가지 않는다 [실행 확인 — 아래 배터리, 봉합안 열]. 정상 저작(총량 증가 동반 append)은 감소 섹션 부재로 INV-S2 가 **발화하되 GREEN**, 앵커 불변으로 INV-S1 미발화다.

> **종전 단언의 철회 (R2 P0-A)**: 종전 기재 *"어떤 PR 도 양쪽 모두에서 빠져나가는 사각이 없다"* 는 **`θ_total` conjunct 가 존재하는 한 명시적으로 거짓**이었다. 위 재선언은 conjunct 제거 **후** 배터리를 실행해 확인한 뒤에만 발화한 것이다(AC-17 자기적용 — mutant falsify 후 선언).

**실행 확인 (PL firsthand 반증 하네스, 기준 트리 `8307618d` / 매체 LF raw CR=0 / 슬라이서 V1 / 정의역 = Story 파일 1건 229,897 B)** — 술어를 문면 그대로 구현해 봉합 **전·후** 를 같은 배터리로 대조했다. `Δbytes` 는 parent 총량 증분:

| 변형 | Δbytes | INV-S1 | INV-S2 (종전) | **INV-S2 (봉합)** |
|---|---:|---|---|---|
| M0 무변경 (대조군) | +0 | NOT_FIRED | GREEN | **GREEN** |
| M-SPLIT 정상 분할 (pure move) | −8,539 | **GREEN** | NOT_FIRED | NOT_FIRED |
| M-LOSS 분할 중 500 B 소실 | −8,539 | **RED** | NOT_FIRED | NOT_FIRED |
| **M-APPEND 정상 append 1,000 B (대조군)** | +1,000 | NOT_FIRED | *NOT_FIRED* | **GREEN** — false RED 0 |
| **M-APPEND 정상 append 50,000 B (대조군)** | +50,000 | NOT_FIRED | *NOT_FIRED* | **GREEN** — false RED 0 |
| **M-DELETE 8,620 B 삭제 (대조군)** | −8,620 | NOT_FIRED | *NOT_FIRED* | **GREEN** |
| M-NORMAL 정상 §9 append | +3,946 | NOT_FIRED | *NOT_FIRED* | **GREEN** |
| **M-E4 §9→§4 보상 이동 (0 B)** | +0 | NOT_FIRED | **RED** | **RED** `[(9,4)]` |
| M-E4′ 동일 + `reason_code` 선언 | +0 | NOT_FIRED | SIGNAL (비차단) | SIGNAL (비차단) |
| M-MIX-64 이동 + append 64 B | +64 | NOT_FIRED | **RED** | **RED** `[(9,4)]` |
| **M-MIX-min 이동 + append 65 B** | **+65** | NOT_FIRED | ***NOT_FIRED* ← 사각** | **RED** `[(9,4)]` |
| M-MIX 이동 + append 1,000 B | +1,000 | NOT_FIRED | *NOT_FIRED* ← 사각 | **RED** `[(9,4)]` |
| M-MIX-SPLIT §9→§7 + append 1,000 B | +1,000 | NOT_FIRED | *NOT_FIRED* ← 사각 | **RED** `[(9,7)]` |

**라벨 규약 (설계리뷰 R2 P1-E 정정)**: 종전 표는 M-APPEND 를 `GREEN`, M-NORMAL 을 `NOT_FIRED` 로 적어 **같은 성질(미발화)에 다른 라벨**을 부여했다 — 미발화를 통과로 계상한 것이며 §8.2 M-MARGIN 절이 금지한 형상의 자기 재발이었다. 위 표는 *기울임* `NOT_FIRED` = 미발화(통과 아님) / `GREEN` = 발화 후 통과로 **판정 상태를 문자 그대로** 표기한다. 봉합안에서는 이 대조군들이 실제로 발화 후 GREEN 이므로 **라벨과 실판정이 일치한다**(이중 이득).

**검출 정의역 비축소 (R2 Iter 5 가설 — 봉합 부작용 축)**: 봉합 전 RED 였던 변형이 봉합 후 non-RED 로 바뀐 건수 = **0**. 봉합 후 신규 RED = **3**(M-MIX-min · M-MIX · M-MIX-SPLIT). 즉 이번 봉합은 검출 정의역을 **순확대**했고 축소분이 없다 [전수 대조 실행 확인].

13/13 기대 일치. **정직 한계**: 이 하네스는 설계 술어의 반증 도구이지 Phase 2 게이트 코드가 아니다 — "게이트가 배선됐다" 고 주장하지 않는다 (§결정 8 자기 구속). **하네스 자체의 아티팩트 1건을 자체 발견·정정**했다: 섹션 말미 절단을 줄 경계에 정렬하지 않으면 다음 h2 앞의 개행이 사라져 그 heading 이 무효화되고 §10 이 §9 에 흡수된다(섹션 Δ 가 `(10,4)` 로 거짓 산출). 위 표는 전부 정렬 후 값이며 `(9,4)` 가 정본이다.

**봉합안도 못 잡는 것 (§8.12 등재)**: ① **이동 출처에 이동량 이상 재-append** — §9→§4 로 8,000 B 이동 후 §9 에 9,000 B 재-append 하면 §9 의 순 Δ 가 **양수**라 `∃i: Δ§i ≤ −θ_move` 가 거짓 → **GREEN** [실행 확인] ② **θ_move 미만 분산 이동** — §9→§4/§5/§6 으로 3,673 / 3,353 / 3,879 B(총 10,905 B, 총량 완전 보존)를 쪼개 옮기면 개별 Δ 가 전부 임계 미만이라 **GREEN** [실행 확인]. 두 회피는 종전·봉합안 **양쪽 모두** 통과하므로 봉합의 회귀가 아니라 **잔존 한계**로 정직 등재한다.

앵커 3속성 = **명시**(주석 마커, 구조 우연 비결합) ∧ **쌍**(시작/종료, 미쌍 = FAIL) ∧ **유일**(파일 내·코퍼스 내, 중복 = FAIL — "첫 매칭 사용" 금지).

#### INV-S3 발화 조건은 무조건이며 판정은 3항 AND 다 (설계리뷰 R2 P0-B · P1-C)

```
INV-S3  발화 ⟺ 항상                                        # 발화 조건 없음 (R2 P0-B 봉합)
        판정  for each domain D ∈ DOMAINS:  leg1 ∧ leg2 ∧ leg3
              leg1  집합 동일성   : ids(declared_D) == ids(extract_D(after))
              leg2  절대 cardinality : |extract_D(after)| == card(declared_D)   # basis = D 가 선언
              leg3  per-cell 값 동일성: ∀k ∈ declared_D : extract_D(after)[k] == declared_D[k]
                    (D.leg3 == not_applicable 이면 leg3_na_reason 폐쇄 enum 선언 의무 — 조용한 skip 금지)

        extract_D 정의역 = strip_stub(after.§n) ∪ children[n]   # INV-S1 과 동일 재조립 (R3)
```

#### 정의역은 자족적으로 선언된다 — 전역 추출 규칙 금지 (설계리뷰 R3 P0-1)

**전역 단일 추출 규칙은 born-broken 이었다.** R2 는 `extraction: table_cells_only` 를 전 정의역에 걸었는데, AC-ID 착지면 하나(Change Plan §1)는 **표가 아니라 산문 한 줄**이라 추출이 **0** 이 되고 선언은 13 이었다 — INV-S3 가 무조건 발화하므로 **모든 PR 에서 무조건 RED**. 세 AC 정의역의 **실 판별자가 서로 다르다**는 것이 실측으로 확인됐다 (절 경계 / 표 행 필터 / 산문 줄 앵커).

> **이것이 봉합 상호작용의 실물이다.** P0-B(무조건 발화)와 P1-D(표 행 한정)는 **각각 정확한 봉합**이었고 단독으로는 어느 쪽도 이 결함을 만들지 않는다. 합성된 뒤에야 무조건 false RED 가 생겼다. ⇒ **봉합의 검증 축에 "직전 봉합들과의 조합" 을 추가한다** — 최소 통과선 = **무변경 정본 파일이 전 봉합 동시 적용 하에서 GREEN**.

따라서 각 정의역은 다음을 **스스로** 선언하며, 하나라도 누락하면 **배선을 금지**한다 (fail-closed):

```
kind              quantitative_cells | ac_id_landing
file, section     추출 대상 파일 · 절
span_kind         table | line | section        # span 이 좁힌다 — 사후 필터로 좁히지 않는다
span_anchor       기계 판독 정규식               # YAML 주석 금지 (R3 P1-4)
fence_aware       코드펜스 안 '#' 을 heading 으로 보지 않는다
cardinality_basis cell_count | id_occurrence_count
leg3              applicable | not_applicable(+ leg3_na_reason 폐쇄 enum)
expected          원소 → 값(또는 출현수) 매핑     # card 는 여기서 유도 (이중 원본 금지)
status            enforced | deferred            # deferred = UNDETERMINED 방출 (GREEN 아님)
```

**`cardinality_basis` 를 전역 `raw_rows` 로 두는 것도 born-broken 이었다** — "원시 행 수" 를 문자 그대로 적용하면 4 정의역 중 **3 이 무조건 RED** 다(한 표 행이 6 개 ID 를 보유하거나, 데이터 행이 1 행뿐이거나, 표 자체가 없다). 정본은 계열별로 `cell_count` / `id_occurrence_count` 다.

**`fence_aware` 는 장식이 아니다** — 절 경계 판정이 코드펜스 안의 `#` 줄을 heading 으로 오인하면 대상 절이 조기 종결돼 정량 정의역이 **22셀 → 0셀** 로 붕괴한다(P0-1 과 동일 class). 주입 mutant 로 load-bearing 을 실증했다.

**P0-B 봉합 — `anchor_delta ≠ ∅` 게이팅 제거.** Iter 4 는 전역 집합 → 정의역별 분해로 **양화는 고쳤으나** 같은 봉합에서 발화 조건 `anchor_delta ≠ ∅` 를 **새로 붙였다.** C-13(정의역 간 상쇄)은 분할과 무관한 위협인데 검사가 **분할 커밋 전용**이 된 것이다 — 형식 해소·실질 축소. 실증: RTM 에서만 `AC-7` 을 삭제한 mutant 를 **분할 없는 일반 편집 PR** 로 주입하면 `anchor_delta = ∅` 라 **NOT_FIRED**. 게이팅 제거 후 동일 mutant 는 **RED 로 복귀**하고, 정상 산문 편집 대조군은 **GREEN**(false RED 0)이다 [양쪽 실행 확인].

**P1-C 봉합 — leg3(per-cell 값 동일성) 신설 + 판정면 이전.** Story 자기 문면이 요구한 제품 게이트 요건은 *"per-cell identity 고정 ∧ 정의역별 분해"* 인데 Iter 4 는 **두 번째 연언지만** 착지시켰다. 종전 2항 AND(집합 동일성 · 절대 cardinality)는 **둘 다 값을 보지 않으므로** C-7 원형 공격(식별자·개수 온전, **값**만 오염)이 그대로 통과한다 [실증: `12.29 KB` → `9.85 KB` 치환 mutant 가 2항 AND 에서 **GREEN**, leg3 추가 시 **RED**. leg 제거 실험으로 **leg3 가 단독 검출자**임을 확인].

봉합에는 **판정면 이전**이 함께 필요하다 — 세 leg 의 비교 기준을 `before` 가 아니라 **baseline artifact 선언값**으로 둔다.

> **근거 정정 (설계리뷰 R3 — 결론 유지, 근거 교체)**: 종전 근거 *"공격자가 같은 PR 안에서 before 를 함께 옮길 수 있어 무력하다"* 는 **재현되지 않는다** — 단일 PR 안에서 before 를 함께 옮기면 차분면이 그 이동 자체를 본다 [실측: 차분면 RED]. 3 관측자 중 1 만 재현을 주장했고 2 는 반증했다. 근거를 철회한다.
>
> **실 판별자는 둘이다**: ① **정의역 위치 앵커 추출** — 무관 위치의 정확한 행 복제가 결손을 복원하지 못한다 [실증: Story L1588 C-7 실형상(은폐 −2셀 + 무관 위치 복제 +2셀)이 before/after 에서 **GREEN**, 선언값+앵커에서 **RED**]. ② **선행 오염의 영구 지속** — 차분면에는 **절대 앵커가 없어** 오염이 일단 착지하면 이후 모든 PR 에서 before·after 가 똑같이 오염돼 차분이 0 이 된다 [실증: PR1 오염 착지 → PR2 정상 편집 시 **차분면 GREEN(영구 무장해제) / baseline 면 RED 지속**]. ②가 판정면 선택의 **주 근거**다.
>
> **판정면 선택을 반증하는 mutant 를 로스터에 등재한다** (`M-PREEXIST`) — 종전에는 0 건이라, Phase 2 가 before/after 로 구현해도 로스터 전건이 통과했다. **설계가 선택한 것마다 그 선택을 반증하는 mutant 가 있어야 한다**는 규율을 §결정 4 의 일부로 명문화한다. 따라서 (a) `cells` 선언을 개수 → **(셀ID → 값) 매핑**으로 확장하고 (b) 정의역 추출은 선언된 위치에 앵커해 **무관 위치 복제가 결손을 복원하지 못하게** 하며 (c) 정의역 내 **파싱 실패는 조용한 skip 이 아니라 결손**으로 드러나야 한다. 상세 = Change Plan §8.4 · §11.5.

### §결정 5 — grandfather baseline 키는 **안정 식별자**이지 파일 경로가 아니다

선례 3종(`infra-resource-baseline.yaml` / `path-relocation-baseline.yaml` / `resource-safety-claim-baseline.yaml`)의 `new-only subtract` 는 **baseline 에 열거된 것만 면제**한다. 키가 파일 경로면 **분할·개명 순간 grandfather 를 잃고 위반이 신규 생성**된다.

**본 Story 의 목적이 곧 분할이므로 이는 예외가 아니라 확률 1의 정상 경로다.** 요구사항 lane 이 이미 경고했다 — *"Story 를 무손실 재구조화하는 행위 자체가 위반을 신규 생성한다 — 본 Story 의 목적과 정면 충돌."*

- 키 = **Story KEY 축 안정 식별자**. wording 형(file|word|content 3-튜플)은 **반면교사로 거부**
- 필수 필드 = `baseline_tree_sha`(고정 SHA 스냅샷, AC-8) + `baseline_media: LF` + `content_digest`(수기 편집 시 비정상 종료) + `frozen_at`
- **Tricorder 동결형** ratchet (전수 선수정 후 활성화 + ratchet up 영구 고정). 확장은 `--allow-baseline-growth --reason` 경유만 (monotonic shrink)
- **touched 판정 = diff 는 스캔 대상 선별에만 쓰고 위반 판정에는 쓰지 않는다.** `violation(f) ⟺ metric(f, HEAD) > ceiling(f)`. "touched = 임의 diff" 로 두면 오타 수정과 무손실 재구조화가 위반을 신규 생성해 **규칙이 장려할 행동을 처벌한다**
- **backfill = 영구적으로 안 한다** (deferred TODO 아님, 채택한 설계). 근거 = Clean-as-You-Code / Tricorder 선례 + 650건 일괄 편집은 §1 immutable 게이트를 전건 트립 + 감사 기록 대량 재작성은 정보 삭제 금지 역행
- **신규 Story 의 ceiling 산출 규칙** (설계리뷰 R1 P2 — `entries` 는 baseline 등재분만 보유하므로 신규는 조회 실패가 아니라 **정의된 경로**여야 한다):

```
ceiling(key) = entries[key].ceiling        if key ∈ entries        # grandfather
             = DEFAULT_CEILING             otherwise               # 신규 — 면제 아님

DEFAULT_CEILING = baseline 동결 트리 코퍼스의 read_cost 분포 p50 (Phase 2 산출 정수, 동결)
ratchet(touched) : ceiling ← min(ceiling, metric(HEAD))            # monotonic shrink
```

  **CFP-2986 자신이 첫 신규 대상**이므로 자기 면제 없이 `DEFAULT_CEILING` 을 적용받는다. `entries` 미등재를 "제한 없음" 으로 읽는 구현은 금지한다 — 그것이 확정 1("신규 + touched ratchet")을 신규 축에서 공허하게 만든다.

### §결정 6 — 배선은 internal-docs checkout 형이며 승격은 수동 절차다

**측정 대상과 판정 로직을 같은 repo 에 둔다.** `actions/checkout` 만으로 실파일 측정이 되므로 cross-repo fetch · PAT · whitelist · URI 파싱이 **전부 불요**하다.

이것이 결정적인 이유 — 현행 cross-repo fetch 는 **path traversal 로 whitelist 가 완전 우회**된다 (firsthand 실증): `blob/main/../../../attacker/evil/contents/x.md` 가 whitelist 를 PASS 하는데 실제 조립 URL 은 `/repos/attacker/evil/...` + PAT 첨부. 검사한 값(`owner/repo`)과 실제 요청 값(정규화 후 경로)이 다른 객체다 (CWE-22 × CWE-20). **fetch 를 안 하면 이 계열 위협이 전부 비해당이 된다.**

배선 형상 제약 (전건 실측):

1. **`on.paths` 필터 금지** — workflow-level path skip 은 check context 자체를 생성하지 않아 required 시 영구 `Expected — Waiting for status`. **`on: pull_request` 무필터 + 내부 graceful no-op** 이 강제 형상 (선례 `story-section10-time-lint.yml:32-34`)
2. **트리거 glob 과 검사 glob 의 깊이를 일치**시킨다 — `story-section-ownership-check.yml` 이 트리거 `*/stories/**`(재귀) vs 검사 `*/stories/*.md`(단일 레벨) 비대칭이라, 하위 디렉터리 파일은 **job 은 돌고 스캔 0건인 무증상 GREEN** 이 된다. 이는 §1 immutable 의 "침묵 skip" 과 **동형 재발**이다
3. **자식 파일은 평면 배치** (`wrapper/stories/CFP-NNNN-SN.md`) — 기존 관행 18건과 동형이고 위 glob 비대칭을 회피
4. **job name 에 tier 어휘 금지** — 승격 시 rename 이 필요해지고 rename 은 7일-green 재적립 chicken-egg 로 들어간다
5. **auto-commit-back 금지** — `GITHUB_TOKEN` push 는 required check 를 재트리거하지 못해 영구 정지

**승격은 자동이 아니다.** ADR-130 §결정 6 의 승격을 측정·집행하는 코드는 **0건**이다 (전수 grep — 히트는 무관 TTL 과 주석 문면뿐). 정확한 이름은 **수동 승격 절차 + 사전조건 체크리스트**다. 7일 창은 GitHub 문서 verbatim 상 **repository 단위**이므로 PR 실행만으로 채워지며 main push 는 불요하다.

**승격 사전조건**: internal-docs open PR 중 **CONFLICTING 8건** 정리 (충돌 PR 은 merge ref 가 없어 workflow 가 아예 안 돌고 required 가 영구 Pending) + `enforce_admins: true` 이므로 관리자 우회 없음.

### §결정 7 — 효과는 명제별로 분리한다 (비차단 신호 ∧ fail-closed 무결성)

- **"너무 큰가"** = 분할 의무 **신호**, 비차단 (ADR-058 거부 선례 회피, ADR-167 통로)
- **"정보를 잃었는가"** = dangling pointer · 앵커 미쌍 · pure-move 위반 = **fail-closed**

AC-15(비차단)와 AC-20(비정상 종료)은 모순이 아니다. AC-20 의 술어는 *"위반 fixture 투입 시 **검사 스크립트** 종료코드 비정상"* 이지 merge 차단이 아니다 — AC-20 은 AC-15 의 비차단 선택이 **hollow gate 로 전락하는 것을 막는 anti-hollow 가드**다.

### §결정 8 — 실읽기량 술어는 Phase 1 에서 **정의**하고 Phase 2 에서 **배선**한다

Orchestrator 확정 3(기계강제 필수)과 만나는 지점이므로 명시 판정한다. 선택지는 (a) 기계화 가능한 대리 metric + C1 함정 회피 mutant 실증 / (b) 술어 기계화를 Phase 2 로 이월하고 Phase 1 은 구조까지 착지.

**채택 = (b).** 근거:

1. 실읽기량 술어는 **lane → 섹션 읽기 선언 레지스트리**를 입력으로 요구한다. 선언은 현재 agent 정의에 **산문으로** 존재한다 (`§1-7` 선언 6 파일 / `ArchitectPLAgent.md:187` = `§1-7·§9` / `review-pl-base.md:284` = 매 DesignReview 진입 §9 scan). 이를 레지스트리로 승격하는 것이 술어 기계화의 실체이며 코드·스키마 산출물이다 → Phase 2 범위.
2. **Phase 1 이 공허하지 않다.** 구조 불변식은 술어 없이도 기계 검증 가능하다 — 자식 파일 존재 ∧ 앵커 쌍 ∧ pure-move digest ∧ 깊이 ≤ 1. §결정 2 의 실측이 보인 대로 **분할 후 잔여가 트리 불변**이므로 구조 자체가 검증 대상이 된다.
3. (a) 를 택하면 대리 metric 이 필요한데, 유일한 후보인 **자식 포함 총 바이트가 pure move 하에서 항등**이라 처방의 효과를 원리적으로 측정할 수 없다 — 섹션 단위 집계를 §결정 1 에서 기각한 것과 같은 사유이고, count cap 계열은 ADR-058 §결정 5 가 이미 거부했다. (종전 근거였던 "E-4 로 이미 반증" 은 **범주 오류라 철회**한다 — E-4 는 총 바이트를 완전 보존하므로 총량 metric 을 반증하지 못한다. §결정 4 정정 참조.)

> **금지 (자기 구속)**: 술어가 배선되기 전에 "실읽기량 게이트가 있다" 고 선언하지 않는다. 그것이 정확히 본 Story 가 4 라운드에 걸쳐 잡아낸 hollow oracle 형상이다. **Phase 1 은 작동하는 게이트를 주장하지 않는다.**

---

## 결과

### 긍정

- 성장 축(§9·§10)이 외부화되어 parent 가 FIX·리뷰 회차와 곱셈으로 자라지 않는다 (§결정 2 실측)
- 축 A(reader 자율)·축 B(일회성·단위 어긋남) 어느 쪽에도 해당하지 않는다
- cross-repo fetch 제거로 신규 신뢰경계가 0 이다
- grandfather 가 안정 식별자 키라 분할 행위 자체가 위반을 만들지 않는다

### 부정 · 잔여 위험 (정직 선언)

- **R-1 순응형 회피 — 완화 불가.** 크기 압력을 저작자에게 부과하면 최적화 방향이 "압축된 서사" 가 아니라 **"쓰지 않기"** 다. 게이트를 **정직하게 만족시키면서** 정보 삭제 금지를 깬다. 미저작은 diff 에 존재하지 않으므로 **원리적으로 검출 불가**하다. 에이전트 저작이 증가분의 93.7% 라 표적과 회피 행위자가 같은 집합이다. 유일한 완화는 유인 재설계 — AC-13 공식 배출구로 "옮겨 쓰기" 비용을 "안 쓰기" 아래로 내린다 (Amazon 6-pager 가 appendix 를 공식 무제한 예외로 두는 것과 동형). **이는 기계강제의 예외가 아니라 기계강제의 정직한 상한이다.**
- **R-2 day-1 merge 차단력 0.** internal-docs `required_status_checks` 키가 부재하므로 도입기 게이트는 LOUD warning 이다. "기계 강제" 라 부르지 않는다.
- **R-3 §9 는 최대 레버인데 최약 경계다.** `MONOPOLY_SECTIONS = {"10","10.5","13","14"}` 에 **§9 가 없고** `SECTION_OWNERS["9"]` 는 4 lane = 사실상 any.
- **R-4 GREEN 축적은 배선 증거가 아니다.** grandfather 가 전건 면제하므로 도입 당일 기대 RED = 0. **의도적 위반 PR 1건으로 RED 능력을 실증**하지 않으면 미배선 게이트를 승격하게 된다.
- **R-6 mutation harness 미선언 (정직 등재 — Phase 2 이행 항목).** `wrapper/spikes/cfp-2986-s0/` 에 `mutation_harness` 선언이 **없다**(grep 0건). ADR-154 A1-7 선언 의무는 Phase 2 이행 항목으로 등재하며, 본 ADR·Change Plan §8.11·Story §7.11 **3면 모두**에 기록해 Phase 2 시야 이탈 경로를 닫는다. 위 §결정 4 의 반증 하네스는 ad-hoc 이며 이 선언을 대체하지 않는다.
- **R-7 ModuleArch 의 실질 우려는 metric 교체로 소멸하지 않는다.** deputy 가 `T=130,000 B` 로 표현한 것의 실질은 "**carrier 가 자기 규칙을 자기 파일에서 못 지키는 상태**" 였다. 임계값 형태는 §결정 1 이 폐기했으나 우려 자체는 `read_cost` 축으로 이전한다 — 판정면 = 자기적용(AC-10)이고, 판정 시점 = 술어 배선 후(Phase 2)다. **Phase 1 에서 이 우려는 미해소이며 "무효화" 라벨이 "해소" 를 뜻하지 않는다.**
- **R-5 처방의 수신자가 lane 이 아니다.** 직전 라운드 총 증가 +33,253 B 중 **Orchestrator 의 §9 verdict 쓰기가 +19,827 B**(약 60%). §9 는 Orchestrator·리뷰 write monopoly 면이므로 lane 저작 규약으로 설계하면 최대 기여자를 안 건드린다.
- **R-8 INV-S2 봉합 후에도 남는 회피 2종 (잔존 한계 — 회귀 아님).** ① **이동 출처에 이동량 이상 재-append** — 이동 후 출처 섹션의 순 Δ 가 양수가 되어 `∃i: Δ§i ≤ −θ_move` 가 거짓 → GREEN. ② **θ_move 미만 분산 이동** — 총량을 완전 보존한 채 여러 섹션으로 쪼개면 **증가 측** 개별 Δ 가 전부 임계 미만이라 페어 조건이 불성립 → GREEN. 둘 다 봉합 **전후 모두** 통과하므로 봉합의 회귀가 아니다. 임계 하향은 정상 저작 false RED 를 유발해 닫지 못하며, 닫으려면 페어 가정을 버리고 **감소 총합 ↔ 증가 총합** 술어로 가야 하는데 그것은 **R-10 의 false-positive 정의역을 넓힌다** — 교환비 미측정, Phase 2 계량 대상. (Change Plan §8.12 축 A-4·A-5 / Story §7.11 **3면 동시 기록**)
- **R-9 INV-S3 leg3 의 선언 정의역 한계.** leg3 는 **baseline 에 선언된 셀만** 본다. 선언 밖 신규 정량 셀이 틀린 값으로 태어나면 검출 대상이 아니다 — `coverage_floor` 축의 문제이지 leg3 의 결함은 아니나, **"값 오류를 전부 잡는다" 는 주장은 성립하지 않는다.** (Change Plan §8.12 축 A-6 / Story §7.11 **3면 동시 기록**)
- **R-10 INV-S2 가 정상 혼합 편집을 발화시킨다 (false-positive 축 — R3 신설).** 감소 ∧ 증가가 같은 커밋에 있는 정상 저작이 발화하며, 그 실물이 **본 Story 자신이 권고하는 보조 레버**다 [실행 확인]. `reason_code: AUTHORED_CONSOLIDATION` 으로 흡수하되 그 흡수는 저작자 선언 의존이라 INV-S2 를 **기록자로 퇴화**시킨다. **오라클의 정직 목록은 양 축(못 잡는 것 ∧ 잘못 잡는 것)이어야 한다** — R2 까지 false-negative 축만 등재한 것이 이 결함이 3 라운드 생존한 직접 원인이다. (Change Plan §8.12 축 B / §8.3 행 11 / Story §7.11 **3면 동시 기록**)

> **R-6 이 세운 "3면 동시 기록" 규약을 R-8·R-9 에 소급 적용했다 (설계리뷰 R3 P2).** 종전 R-8·R-9 는 Change Plan §8.12 와 Story §7.11 **2면**에만 있었고 본 ADR §결과에 부재해, 규약을 세운 문서가 그 규약을 자기 항목에 안 지키는 상태였다. R-10 은 신설 시점부터 3면이다.

### 정량 인용 규약 (본 Story 에서 틀린 수가 넘어간 경로의 봉합)

**모든 정량 주장 = 값 + 기준 트리 SHA + 매체 + 정의역(분모) 4-tuple.** 본 Story 에서 잘못 전파된 수치가 전부 분모·정의역 미병기였다:

| 폐기값 | 정본 |
|---|---|
| "586개 Story" | 트리별 **576**(`4ce40368`) / 587(`a78d8c88`) / 588(`7e3127a8`), 게이트 실 정의역 `*/stories/*.md` = **650** |
| "§9 유일 tree-invariant 1위" | **delta base 한정.** 정적 base 3위 |
| "§1 잔여 136" | **120** |
| E-1 비용 "+2 B" | **+1 B** (`##`→`###` = 1자, 실행 확인) |
| E-4 행 "§9 = 82 B" | **30 B** (heading 줄 `## 9. 품질 게이트 이력\n` 단독; 같은 행 §4 = 104,590 과 산술 정합) |
| "E-4 가 파일 크기 metric 을 반증" | **범주 오류 — 철회.** E-4 는 총 바이트를 완전 보존한다 |
| "CP §1 매핑 **실측 13** = 선언 13" (전역 표 행 규칙 하) | **거짓 — 철회.** 전역 `table_cells_only` 하 실측 **0**(§1 에 `|` 시작 줄 0개). 정본 = 정의역별 산문 줄 앵커에서 **13** |
| `cardinality_basis: raw_rows` (전역) | **born-broken — 철회.** 4 정의역 중 **3** 이 무조건 RED. 정본 = `cell_count` / `id_occurrence_count` |
| "`AC-99` 오염을 **표 행 한정**이 배제한다" | **오귀속 — 정정.** `AC-99` 소재가 **표 행**이라 그 필터로 배제되지 않는다. 실 배제자 = **절 경계** |
| "before 를 함께 옮길 수 있어 차분면이 무력" | **재현 실패 — 철회.** 실 판별자 = **선행 오염의 영구 지속**(차분면에 절대 앵커 부재) |

특히 "§1 잔여 136" 은 R4 에서 리뷰 PL 과 Codex 가 **둘 다 독립 "재현됨"** 으로 확증했던 값이다. **3자가 같은 틀린 값을 확증했다** — 관측면이 같으면 다중화 이득이 0 이라는 것의 실물이다.

## 대안 검토

- **자식 포함 총 바이트 hard cap** — ADR-058 §결정 5 가 count cap 을 "정당한 사례까지 차단할 위험" 으로 거부했고, 더해 **pure move 하에서 항등**이라 본 처방의 효과를 0 으로 계상한다(측정 수단으로 실격). *E-4 를 기각 근거로 인용하지 않는다* — E-4 는 총 바이트를 완전 보존하므로 이 metric 을 반증하지 못한다(설계리뷰 R1 P0-1 정정).
- **줄수 cap** — `claude-md-line-cap` 이 GREEN 인 채 +82.4% 성장을 허용한 실증이 있다.
- **4번째 reader-side 읽기 규약** — 축 A 실패 3건의 반복.
- **일회성 압축 후 방치** — CFP-2211 이 2개월 만에 +31.8% 복귀.
- **2단 계층 참조** — 외부 실증상 이득 0 이며 정확도 0.9126 → 0.6398 붕괴. 인덱싱 깊이 ≤ 1 (AC-12)의 근거.

## 미해결 (설계리뷰 회부)

1. **AC-19 해석** — 규칙 층 일반성으로 읽는 것이 타당한가 (§결정 3 정직 고지). **설계리뷰 R1 미처분 — 잔존.**
2. ~~`check_story_section_schema.py` 순회가 `.glob` 인지 `.rglob` 인지 미확인~~ → **종결**: `:70` = `.glob`(비재귀) 확인. 평면 배치 판정 무손상.
3. ~~repo 설정 "Send secrets to workflows from pull requests" 상태 미조회~~ → **종결(favorable, 단 간접)**: internal-docs `allow_forking: false` · `forks_count: 0` ⇒ **fork 자체가 불가하므로 도달 가능한 효과 0**. *정직 한계* — 토글 값을 직접 read 한 것이 아니라 **전제조건(forkability)이 거짓임**을 측정했다. `pull_request_target` 금지 명문화는 이와 무관하게 유지한다.
4. ~~AC-21 민팅 후 RO-1 재확인~~ → **종결**: AC 21행 / normative 15 / declared 6, §8.1 RTM 15행 전건 매핑 + named test 15개 유일 — zero-drop 성립. 잔여는 AC-21 provenance 뿐이며 §5.5 원장 갱신은 요구사항 lane owned 라 Orchestrator scoped write 로 회부.
5. **Phase 1 normative AC 7건에 Phase 1 검증수단이 0 이다** (신규 — 설계리뷰 R1 P2). 해당 = **AC-2 · AC-4 · AC-8 · AC-10 · AC-12 · AC-15 · AC-19** [PL 전수 재계수 확인, §5.3 표 21행]. `phase` 컬럼은 **요건의 착지 phase** 이지 검증수단의 배선 phase 가 아니며, §8.1 RTM 의 named test 15건은 전부 Phase 2 산출물이다. Phase 1 에 `rtm_uri` 를 부착하지 않는 이유가 정확히 이것이다(부착 시 Hop2 가 발동해 미배선 매핑을 전건 위반으로 잡는다). **Phase 1 은 이 7건에 대해 "검증됐다" 고 주장하지 않는다** — 표기 정합을 위해 phase 컬럼을 사후 변경하는 것도 금지한다(요구사항 lane owned ∧ 값 조작).
