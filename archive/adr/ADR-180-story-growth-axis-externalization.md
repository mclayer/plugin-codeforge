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

측정 단위는 **처방이 줄이겠다고 선언한 양과 동일**해야 한다. **줄수 · heading 수 · 섹션 수 · 파일 총 바이트를 판정 단위로 채택 금지.**

근거는 `claude-md-line-cap` 의 실패가 "줄수라서" 가 아니라 **"선언한 양과 재는 양이 달라서"** 라는 데 있다. 파일 총 크기도 같은 함정이다 — 우리가 줄이겠다고 선언한 것은 저장량이 아니라 읽기 단가다.

```
lane 진입당 실읽기량 = Σ_섹션 ( 섹션바이트 × 그 섹션을 입력으로 선언한 독자 수 )
```

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
| E-1 | heading `##` → `###` 강등 | +2 B | §9 = 0 B → **GREEN** |
| E-2 | `## ` 뒤 U+200B 1자 삽입 (렌더 동일) | +3 B | §9 = 0 B → **GREEN** |
| E-3 | §9 선두에 코드펜스로 `## 11.` 인용 → 슬라이서 조기 종결 | +65 B | §9 = 39 B → **GREEN** |
| **E-4** | §9 본문 전량을 §4 말미로 보상 이동 | **0 B** | §9 = 82 B → **GREEN**, 총량 완전 보존 |

**E-4 가 결정적이다**: read-cold §9 를 read-hot §4 로 옮기면 §4 가 53,653 → **104,590 B** 가 된다. **실읽기량은 악화되는데 섹션 cap 은 GREEN 이고 비용은 0 이다.** 악의를 가정할 필요도 없다 — 섹션 간 재배치는 저작자가 우연히 할 수 있는 정상 편집이다.

⇒ **섹션 cap 단독 설계는 born-broken 이다.** §결정 1 의 실읽기량 목적함수는 E-4 를 자동으로 RED 로 만든다 (§4 는 전 독자가 읽으므로).

앵커 3속성 = **명시**(주석 마커, 구조 우연 비결합) ∧ **쌍**(시작/종료, 미쌍 = FAIL) ∧ **유일**(파일 내·코퍼스 내, 중복 = FAIL — "첫 매칭 사용" 금지).

### §결정 5 — grandfather baseline 키는 **안정 식별자**이지 파일 경로가 아니다

선례 3종(`infra-resource-baseline.yaml` / `path-relocation-baseline.yaml` / `resource-safety-claim-baseline.yaml`)의 `new-only subtract` 는 **baseline 에 열거된 것만 면제**한다. 키가 파일 경로면 **분할·개명 순간 grandfather 를 잃고 위반이 신규 생성**된다.

**본 Story 의 목적이 곧 분할이므로 이는 예외가 아니라 확률 1의 정상 경로다.** 요구사항 lane 이 이미 경고했다 — *"Story 를 무손실 재구조화하는 행위 자체가 위반을 신규 생성한다 — 본 Story 의 목적과 정면 충돌."*

- 키 = **Story KEY 축 안정 식별자**. wording 형(file|word|content 3-튜플)은 **반면교사로 거부**
- 필수 필드 = `baseline_tree_sha`(고정 SHA 스냅샷, AC-8) + `baseline_media: LF` + `content_digest`(수기 편집 시 비정상 종료) + `frozen_at`
- **Tricorder 동결형** ratchet (전수 선수정 후 활성화 + ratchet up 영구 고정). 확장은 `--allow-baseline-growth --reason` 경유만 (monotonic shrink)
- **touched 판정 = diff 는 스캔 대상 선별에만 쓰고 위반 판정에는 쓰지 않는다.** `violation(f) ⟺ metric(f, HEAD) > ceiling(f)`. "touched = 임의 diff" 로 두면 오타 수정과 무손실 재구조화가 위반을 신규 생성해 **규칙이 장려할 행동을 처벌한다**
- **backfill = 영구적으로 안 한다** (deferred TODO 아님, 채택한 설계). 근거 = Clean-as-You-Code / Tricorder 선례 + 650건 일괄 편집은 §1 immutable 게이트를 전건 트립 + 감사 기록 대량 재작성은 정보 삭제 금지 역행

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
3. (a) 를 택하면 대리 metric 이 필요한데, 유일한 후보인 파일 크기가 §결정 4 의 E-4 로 **이미 반증**됐다.

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
- **R-5 처방의 수신자가 lane 이 아니다.** 직전 라운드 총 증가 +33,253 B 중 **Orchestrator 의 §9 verdict 쓰기가 +19,827 B**(약 60%). §9 는 Orchestrator·리뷰 write monopoly 면이므로 lane 저작 규약으로 설계하면 최대 기여자를 안 건드린다.

### 정량 인용 규약 (본 Story 에서 틀린 수가 넘어간 경로의 봉합)

**모든 정량 주장 = 값 + 기준 트리 SHA + 매체 + 정의역(분모) 4-tuple.** 본 Story 에서 잘못 전파된 수치가 전부 분모·정의역 미병기였다:

| 폐기값 | 정본 |
|---|---|
| "586개 Story" | 트리별 **576**(`4ce40368`) / 587(`a78d8c88`) / 588(`7e3127a8`), 게이트 실 정의역 `*/stories/*.md` = **650** |
| "§9 유일 tree-invariant 1위" | **delta base 한정.** 정적 base 3위 |
| "§1 잔여 136" | **120** |

특히 "§1 잔여 136" 은 R4 에서 리뷰 PL 과 Codex 가 **둘 다 독립 "재현됨"** 으로 확증했던 값이다. **3자가 같은 틀린 값을 확증했다** — 관측면이 같으면 다중화 이득이 0 이라는 것의 실물이다.

## 대안 검토

- **파일 크기 hard cap** — ADR-058 §결정 5 가 거부. 게다가 E-4(비용 0 보상 이동)로 반증됐다.
- **줄수 cap** — `claude-md-line-cap` 이 GREEN 인 채 +82.4% 성장을 허용한 실증이 있다.
- **4번째 reader-side 읽기 규약** — 축 A 실패 3건의 반복.
- **일회성 압축 후 방치** — CFP-2211 이 2개월 만에 +31.8% 복귀.
- **2단 계층 참조** — 외부 실증상 이득 0 이며 정확도 0.9126 → 0.6398 붕괴. 인덱싱 깊이 ≤ 1 (AC-12)의 근거.

## 미해결 (설계리뷰 회부)

1. **AC-19 해석** — 규칙 층 일반성으로 읽는 것이 타당한가 (§결정 3 정직 고지).
2. **`check_story_section_schema.py` 순회가 `.glob` 인지 `.rglob` 인지 미확인** — `rglob` 이면 consumer 에서 자식 배치 판정이 뒤집힌다.
3. **repo 설정 "Send secrets to workflows from pull requests" 상태 미조회** — fork PR PAT 노출 판정 입력.
4. **AC-21 (측정 단위 정합) 민팅 후 RO-1 재확인** — R4 PASS 이후 추가되는 AC 이므로 AC 분해 완결성 재검증이 필요하다.
