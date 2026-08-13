---
adr_number: 173
title: round-continuation dispatch 채널 — FIX 회차 named agent 재개의 적격·계약·관측 SSOT
status: Accepted
category: governance
date: 2026-08-13
carrier_story: CFP-2946
parent_epic: null
supersedes: null
amends: null
reinterpretation: false
is_transitional: false
mechanical_enforcement_actions: []
related_stories:
  - CFP-2946
related_adrs:
  - ADR-067   # 재평가 스폰 fresh-only carve-out + Iter 소비 규칙 (Amendment 4 = 본 ADR 의 짝)
  - ADR-141   # Amd 6/7 — tier override 인스턴스 재개 부적격 (충돌 없음: 4 site 전부 tier-override 지배문 종속)
  - ADR-170   # §결정 19 lead 유일 dispatch 주체 (force-resume 선례) / §결정 2 표 row 7 (c) record-only
  - ADR-139   # background-wait liveness — max-wait 창 조건부 재사용, INV-L2 fail-open 금지 상속
  - ADR-143   # advisory ceiling 정직 라벨 선례 + §결정 3 T1/T4 재실측 trigger
  - ADR-119   # 검증 후 단언 / over-claim 금지
  - ADR-008   # 계약 버전 규칙 — MAJOR 4-trigger 해당 0 → MINOR
  - ADR-043   # dev-process-event index field 추가 = amendment 의무
  - ADR-163   # dev-process-event 계약 축
  - ADR-115   # runtime hook enforcement record-only·fail-open — 재개 가드를 deny 로 세우지 않음
  - ADR-109   # 429 retry ≠ FIX (Iter 오염 차단)
  - ADR-145   # required contexts 8-tuple 무변경
  - ADR-155   # dev-process observability substrate
  - ADR-078   # living architecture 갱신 의무
related_files:
  - docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md
  - docs/inter-plugin-contracts/dev-process-event-v1.md
  - docs/orchestrator-playbook.md
  - docs/architecture/codeforge-family.md
  - plugins/codeforge-review/templates/review-pl-base.md
  - scripts/lib/check_round_continuation_eligibility.py
---

# ADR-173: round-continuation dispatch 채널

## 상태

Accepted (2026-08-13, carrier CFP-2946)

## 본질 선언

**종료한 subagent 를 이름으로 다시 불러 이어서 시키는 것**과 **빈 컨텍스트로 새로 만드는 것**은 비용·리스크 프로파일이 다른 **별개의 dispatch 기제**다. 본 ADR 은 전자를 `round-continuation`(회차-연속 채널)으로 명명하고, 그 **적격 술어 · 메시지 계약 · 관측 축 · 발신 주체 · 동시성 계상**을 확정한다. 아끼는 문맥과 오염되는 문맥은 **같은 토큰**이므로, 채널 도입은 반드시 **자기 리셋 표면**과 **fail-closed 적격 판정**을 동반한다.

## 컨텍스트

### 문제

FIX 루프는 회차마다 리뷰어·chief 급 subagent 를 fresh re-spawn 한다. 이때 **context packet 재구축 + spawn-시점 hook 직렬 지연세**가 매 회차 반복 지불된다. FIX 루프 장기화 실례 = CFP-2913 구현리뷰 16회차.

플랫폼 사실이 이 전제를 바꿨다 `[verified — 실행 버전 2.1.225 / 공식 문서 code.claude.com/docs/en/sub-agents §Resume subagents]`:
- `SendMessage` 도구 설명 원문: *"names keep working after an agent completes (a send resumes it from its transcript)"*
- 완료된 subagent 가 `SendMessage` 수신 시 **새 `Agent` invocation 없이 background 자동 재개**되며, 이 경로는 **agent teams 활성화를 요구하지 않는다**(env flag 무관).

⇒ **"one-shot subagent" 는 더 이상 플랫폼 제약이 아니다.**

### 이 채널이 정면으로 만나는 지점 4곳

1. **tier 경계** — `effective = min(frontmatter, orchestrator)` 의 집행은 fresh-spawn + `model:` override **전용**이다. 재개가 이 집행 지점을 우회할 수 있다.
2. **worker 무상태 전제** — `parallel-dispatch-protocol-v1` I-6.1 (내용 앵커 = *"input packet hash 동일 → output deterministic"*)은 재개와 **직접 충돌**한다. 재개는 transcript 상태를 **의도적으로 carry** 하기 때문이다.
3. **FIX 카운터** — 재개 회차가 `Iter` 를 소비하지 않으면 max-FIX 3/3 게이트가 **무력화**된다. 비용 최적화가 **안전 카운터를 우회**하는 형태다.
4. **anchoring** — ADR-067 이 `reasoning_carryover` 3-part packet 으로 회피하려던 해악이 **agent 인스턴스 존속**으로 되살아난다. 상세 판정 = 아래 §결정 8 + ADR-067 Amendment 4.

### 명칭이 문제인 이유

repo 에 `resume` 가 이미 **4개의 서로 다른 의미**로 존재한다 — ① `/resume` 세션 cold-resume ② pause-and-resume FIX **카운터** 보존 ③ SendMessage resume(tier-override 금지 문맥) ④ force-resume(lead 가 stall 된 PL 을 깨움, 허용 문맥). 신규 채널을 `resume` 로 부르면 **5번째 충돌**이 된다.

### 섹션 번호 순서가 정본 신호가 아니라는 실측

본 채널과 별개로, carrier Story 는 AC 게이트가 **vacuous PASS** 하는 scaffold 결함을 함께 해소한다. 파서 `_extract_section_n` 이 `search()`(첫 매치)로 섹션을 잡아 §1 verbatim 인용 안의 shadow 헤딩을 정본으로 오인하는 문제다. 후보 처방 중 **canonical-order 계열**(섹션 번호 순서 검증)이 실패하는 이유가 결정적이다 `[verified — corpus 578 전수 실행 + 독립 구조 재산출 2 관측면 일치]`:

| Story | H2 번호열 |
|---|---|
| `CFP-2946` | `[1, 0,1,2,3,4,5, 2,3,4,5,6,7,8,9,10,11]` |
| `CFP-1333` | `[0,1,2,3,7,11, 4,5,6,7,8,8,8,9,10,11,12,13,14, 9]` |
| `CFP-801` | `[1,2,3,7,11, 4,4,4,4,5,6,8,9,10,10,11,12,13,14]` |

세 문서 모두 **번호열이 단조가 아니다**(`7,11` 이 `4` 앞에 오거나 verbatim 블록이 통째로 앞에 온다). ⇒ ★**"섹션 번호 순서"는 이 corpus 에서 정본을 식별하는 신호가 아니다**★ 는 것이 canonical-order 계열 **전체**의 실패 원인이다. 상세 = §결정 7.

## 결정

### §결정 1 — 채널 명칭 = `round-continuation` (한글 "회차-연속 채널"), `resume` 어근 재사용 금지

repo 전역(`docs/**` + `archive/adr/**` + `templates/**` + `skills/**`) grep **0 hits** 로 충돌 부재 확인. 파생 식별자 전부 동일 규율을 따른다 — enum 값 `continued`(≠ `resume`) / index field `dispatch_mode` / evaluator `check_round_continuation_eligibility.py` / env `CODEFORGE_ROUND_CONTINUATION_MAX_TRANSCRIPT_AGE_SEC`.

**근거**: 위 4중 동음이의를 5번째로 늘리지 않는다. 특히 ②(FIX 카운터 축)와 ③(tier-override 금지 축)은 본 채널과 **인접하되 별개**이므로 어휘 혼동이 곧 규범 오적용이 된다.

### §결정 2 — 적격 술어 = 6축 통합, fail-closed

evaluator 는 **pure predicate** 로 `(bool, reason_enum)` 을 반환한다. **6축 중 하나라도 미충족·미확보(None)면 부적격**이다(통합 술어이므로 향후 축 추가 시 자동 상속).

| 축 | 술어 |
|---|---|
| A. tier | `effective_tier == frontmatter_tier` (runtime `model:` override 미발생) |
| B. 종료 상태 | `termination_cause == normal` ∧ `outcome == success`. 두 축 **직교 유지**(단일 flat enum 으로 conflate 금지), 어느 쪽이든 `null`·미도착 = 부적격 |
| C. 원인 코드 | "판독면 stale" 계열 = 부적격. 미도착·불명·**enum 미등재 신규 코드**도 부적격 |
| D. 회차 인접 | `Iter` 인접(N→N+1) ∧ 동일 `lane_label` ∧ 동일 `reset_generation` |
| E. 세션 동일 | 세션 식별자 일치. 부재·불확실 = 부적격 |
| F. transcript 무결 | `compact_boundary` **이벤트 실재** 시 부적격(본문 문자열 grep 아님) ∧ 프로세스 재시작 플래그 미set ∧ `age ≤ T` |
| G. agent 종류 | `agent_kind == custom` 만 적격 (내장 Explore/Plan agent 는 `agentId` 미반환 ⇒ 재개 원천 불가) |

**축 A 의 근거는 ADR-141 과의 충돌이 아니라 정책적 보수성이다** `[verified — 지배문 직접 확인]`. ADR-141 의 `SendMessage resume 금지` 4 site 는 전부 **tier-override 지배문 종속**이며(`A6-2. failover 절차` step 2 내부 / 주어 = *"cap-down spawn 은"*), 정상 회차 재개는 **ADR-141 미규정 영역**이다. 축 A 를 유지하는 실 근거 2항 = ① 재개 시 tier 유지는 **플랫폼 구현 의존** 성질이고 codeforge 는 그 거동을 자기 게이트로 검증하지 않는다 ② `effective_tier == frontmatter_tier` 단일 비교는 감사 가능하고 판정 실패 방향이 **항상 안전**하다.

★**override 는 인스턴스 속성이므로 그 이후 전 회차에서 계속 부적격이다**★ — 1회성 판정으로 읽히면 다음 회차에 cap 이 조용히 풀린다.

**부적격의 귀결은 차단이 아니라 fresh re-spawn 이다.** 어떤 회차도 block/deny 되지 않고 **수행 경로만 달라진다** — 이것이 `outcome`/`termination_cause` 의 record-only 제약(ADR-170 §결정 2 표 row 7 `(c)`)과 **정의역이 분리**되는 근거다(품질 판정 게이트 ↔ dispatch 적격 판정).

### §결정 3 — 재개 메시지 계약 = 4요소 + **5번째 요소(무효화 선언)**

**4요소**: ① fresh KST 앵커 ② 현 HEAD SHA ③ 재판독 의무 파일 목록(**repo-relative 경로 강제** — 절대경로는 host username 노출) ④ FIX 지시서. 각 요소 present ∧ 비어있지 않음(whitespace·`TBD` 불가).

★**5번째 요소 = "직전 자기 결론을 전제로 삼지 않는다" 무효화 선언**★ 을 신설한다.

**근거**: `RequirementsReviewPLAgent` 의 **hypothesis-withheld** 규율(작성측 진단을 packet 에서 숨겨 anti-anchoring 을 얻음)이 재개 경로에서 **구조적으로 우회**된다 — packet 을 숨겨도 agent 자신의 잔존 컨텍스트에 직전 결론이 남는다. 선행사례 3종이 같은 방향을 지지한다 `[verified]`: **AutoGen** 은 `load_state()` 와 별개로 `on_reset()` 을 **의무화**하고, **LangGraph**(thread 분리)·**OpenAI Agents SDK**(세 전략 분리)도 "상태를 잇는 API"와 "상태를 버리는 API"를 **분리 노출**한다. ⇒ 재개 채널만 만들고 리셋 축을 만들지 않는 설계는 선행사례에서 이탈한다.

**금지 어휘**: 재개 메시지는 **사실 + 지시**만 담고 verdict·승인·권한·설정변경 어휘를 담지 않는다. **재개 메시지 = 지시이지 승인 아님.** 플랫폼 불변식이 막는 것은 *권한 상승*이지 *판정 오염*이 아니다.

### §결정 4 — 발신 주체 = Orchestrator(또는 Story-scope 위임 teammate) closed 한정 + 재개 유효 창 3중 교집합

ADR-170 §결정 19 (내용 앵커 = *"lead 가 유일 dispatch 주체"*) 승계. 본 채널은 그 §결정 19 의 **force-resume 선례**(stall 구제)를 *정상 회차* 로 **용도 확장**한 것이며, dispatch 토폴로지 변경이지 **ownership 변경이 아니다**(§10 FIX Ledger Orchestrator append 독점 무손상).

★**재개 유효 창 = 세션 동일 ∩ transcript 나이 `T` 이내 ∩ compaction 경계 부재**★ 의 3중 교집합을 단일 "재개 자격 만료 규칙"으로 진술한다. **폐기(revocation) 수단은 `fresh 강제`가 유일**하다 — 개별 재개를 무효화하는 토큰 기제는 없다.

**`T` = 운영 구성값 위임**: 이름 `CODEFORGE_ROUND_CONTINUATION_MAX_TRANSCRIPT_AGE_SEC`, 위치 = playbook max-wait 규약 표 인접 행, **default = 14400초(4시간)**.
`[empirical-source: CFP-2946 §9 요구사항리뷰 iter1~iter9 시각 9점 실측 — 회차 간격 8개 중 ≤4h 가 6/8. 초과 2건(8h09m·6h21m)은 야간 공백 = repo HEAD·roster stale 개연 최대 구간이라 fresh 가 옳다. 정직 표기: n=8 · 단일 Story · 단일 lane]`
`cleanupPeriodDays`(30일)는 **보존 기간이지 재개 유효 기간이 아니므로** 차용하지 않는다. env 미설정 = default / 파싱실패·음수·비수치 = **부적격 고정**(무한대 해석 금지). consumer overlay 는 **축소 방향만**.

### §결정 5 — 관측 = `dev-process-event-v1` optional index field `dispatch_mode: enum{fresh, continued}` (MINOR + amendment 의무)

`event_type` 9번째 enum 값 추가는 **비채택**한다.
- AC parity self-test 는 **계약 §2 필드 표 ↔ `_ROW_KEYS`** 를 대조하므로 **field 추가는 검증 범위 안**이나 **enum 값은 `_ROW_KEYS` 멤버가 아니라 사각**이다.
- 재개는 새로운 사건 *종류*가 아니라 기존 dispatch 행위의 *양상(modifier)* 이다.
- ★양 경로 모두 ADR-043 amendment 의무를 진다★ — "field 추가는 MINOR 라 amendment 를 피한다"는 전제는 실측상 **거짓**이므로 선택 근거가 되지 못한다.

**공통 비용 명시**: 어느 경로든 판별력 회복에는 `hooks/pretooluse-dev-process-capture.py` 에 `tool_name == "SendMessage"` **3rd 분기 추가**가 별도로 필요하다(현행 2분기: `Agent`→`prompt_input` / 그 외 전부 →`tool_call`).

**판별 축은 enum(닫힌 값) 한정**이다 — agent name·`agentId`·자유 문자열 필드를 신설하지 않는다(18-필드 allow-list ONLY, free-form string content field 0).

**관측 누수 0 불변식**: `재개 row + fresh row = 총 회차 수`.

### §결정 6 — 원장 = playbook §14.11 Spawn ID 대장이 흡수 (신규 원장 신설 금지), `name`·`agent_id` 2 컬럼 추가

§14.11 은 이미 (a) `.claude-work/progress/<KEY>.md` (b) Orchestrator 단독 write (c) spawn 직전 즉시 기록 (d) gitignored ephemeral 이며 **목적이 이미** (내용 앵커) *"SendMessage target 모호성 해소 + 병렬 spawn 추적"* — **동일 문제·동일 grain(per-spawn row)** 이다. 두 번째 원장을 세우면 같은 spawn 이벤트에 row-sync 부채가 생긴다.

이미 `agent_type` 을 보유하므로 `name` 컬럼 추가로 ★`name → agent_type → frontmatter tier` 경로가 완성★ 된다 — 이것이 tier 가드 부분 기계화의 **유일한 경로**다(현행 repo 에 `name→agent_type` 매핑은 코드·문서 모두 **0건**). `agent_id` 는 name 해석 실패 시 fallback 도달 경로다.

★**`spawn-event-v1` writer topology 무접촉**★(별 파일·별 채널) ⇒ 그 계약의 amendment 의무는 발동하지 않는다.

**raw `agentId` 배치 3항**: ① host-local gitignored 원장 **한정** ② `.claude/ledger/*.jsonl` 유입 금지 ③ Story file·PR body·Issue comment 등 **커밋·발행 표면 금지**. 근거 = `spawn-event-v1` 의 *"actor = session ID hash(raw 금지)"* / *"transcript_path 값 절대 미저장"* 동일 계열.

**name 유일성**: `<agent 약칭>-<story KEY 소문자>` 규약은 동일 Story 회차간 자기충돌을 일으키지 않아야 한다(latest-wins). `/clear` 가 세션 식별자에 미치는 영향은 ★**확인 불가**★ ⇒ **fail-closed**(식별자 불확실 = 부적격).

### §결정 7 — 동시 실행 상한: 재개분은 **동시 실행(running) 수**로 계상, 예약은 카운팅 세마포어

플랫폼은 재개를 **한도 검사 없이** 통과시켜 running count 를 상한 너머로 밀 수 있다 `[verified — 공식 문서]`. 계상은 codeforge 측 책임이다.

- **상한 축 = 동시 실행(running) subagent 수.** ★spawn 수 기준 금지★ — 재개는 정의상 spawn 이 아니므로 계상 0 이 되어 **원리적으로 뚫린다**.
- **reserve = fail-closed / release = fail-open(시한부 강제 회수)** 의 ★비대칭★. release 를 fail-closed 로 두면 누수 slot 이 영구 점유해 전 lane 이 교착된다 — **상한 자체가 DoS 벡터**가 된다.
- **release 정본 시점** = 실산출 수신 또는 ADR-139 max-wait ceiling 도달.
- **primitive** = **디렉터리 원자 생성(`slots/slot-<n>` 개별 `mkdir`)** 또는 `os.open(O_CREAT|O_EXCL)`. 실행환경 `win32` 라 `flock` 미가용이며, repo 내 원자 예약 primitive 선례는 **0건**(신규 도입). 실행 모델 = **다중 프로세스**.
- ★**단일 공유 lock 파일 금지**★ — 사내 "병렬충돌 가드가 병렬도 최대 순간 fail-open(공유 lock)" 형상의 재발이다. **슬롯 예약은 lock 이 아니라 카운팅 세마포어**다.

**축 분할 (다른 Story 소유면 편집 금지)**: 플랫폼 동시 20 = CFP-2926 기결정(인용만) / batch cap 7→13 = CFP-2914 §7.8 소유(편집 금지) / **재개분 계상 + 예약 원자성 = 본 ADR 소유**.

**`re-dispatch max-retry cap = 2` 우회 방지**: 재개 시도가 이 cap 을 소비하는지 명시해야 한다 — 미명시 시 `재개→fresh→재개→fresh` 로 cap 이 무력화된다(구체 규칙 = ADR-067 Amendment 4 (d)).

### §결정 8 — 계약 착지: `parallel-dispatch-protocol-v1` 같은 파일 MINOR bump, I-6.1 **및 I-6.5** 정의역을 fresh dispatch 한정으로 축소

**MINOR 근거**: ADR-008 §결정 3 MAJOR 4-trigger(필수필드 추가·제거·rename / type 변경 / enum 값 제거·의미변경 / 흐름 방향 역전) **해당 0건**. 재개는 §6.4 `env_invariants` 에 없던 **3rd 분기 additive** 이며 `env_0_default_subagent_context` / `env_1_agent_teams_enabled` 2분기는 그대로 유지된다. 신규 문서 분리는 **비채택** — `MANIFEST.yaml` 에 해당 row 가 이미 등재돼 있어 registry 2단계 + cross-ref 이중화 비용만 추가된다.

**정의역 축소 = guarantee 철회가 아니다.** I-6.1 은 schema 가 아니라 **prose invariant** 이고 기존 소비자가 전부 fresh dispatch 였으므로, 이는 **신규 모드 도입 시점의 boundary 명문화**다.

★**I-6.5 도 함께 축소**★: 재개 실패 후 fresh 는 정의상 **다른 상태에서 출발**하므로 I-6.5(worker crash/timeout re-dispatch 결과 동일성)도 born-broken 이다. I-6.6(cross-batch state isolation)은 **batch 축**이라 round 축과 disjoint 하므로 정의역 밖으로 **유지**한다.

**version 번호는 사전 확정하지 않는다** — merge 직전 origin/main `version` 을 재실측한 뒤 다음 MINOR 를 부여한다(병렬 Story 와의 번호 충돌 회피).

**파서 해소 = 처방B(하위번호 제외 + 마지막 매치)**. canonical-order 계열 비채택 근거 = 위 §컨텍스트 번호열 실측. canonical-A(greedy run)는 `CFP-1333`·`CFP-801` 에서 `4` 지점에 run 이 끊겨 정본 §5 가 run 밖으로 밀리며 `UNDECIDABLE`→`NO_AC_SURFACE` **보호 약화 2건을 신설**한다. canonical-B(LIS)는 `CFP-2946` 에서 최장 증가 부분열이 `verbatim 0..5 + 정본 꼬리 6..11` = 12 가 되어 §5 대응 원소가 ★**verbatim 의 `## 5. gotcha`**★ 가 된다 — 미해소를 넘어 **shadow 를 정본으로 능동 선택**한다. 처방B 는 대신 *"verbatim 인용은 구조상 항상 정본보다 앞"* 이라는 **문서 위치 신호**를 쓰며 양 소비 진입점에서 부수피해 0 이다.

> **처방B 의 정직 한계**: *"정본이 항상 마지막"* 은 **경험적 규칙성**이지 원리적 보증이 아니다. 정본 뒤에 또 다른 shadow 가 오는 문서가 장래 생기면 깨진다. 실 corpus 578 에서 그런 형상이 **0건**이라는 것이 채택 근거이지 "구조적으로 불가능"이 아니다.

### §결정 9 — ADR-067 과의 층위 분리는 **조건부 성립**: 재평가 스폰 지점에서 불성립 ⇒ ADR-067 Amendment 4 로 carve-out

ADR-067 이 회피하는 해악의 실체는 **anchoring(이전 framing 고정)** 이지 전체 transcript 의 물리적 이동이 아니다 — `transcript_ref` 명세(내용 앵커 = *"Full transcript verbatim 회피"*)가 *"회피 수단 ← 근거(anchoring 차단)"* 의 **수단-목적 구조**이고, motivation vector 3(내용 앵커 = *"Codex D6 적대적 검토 발견"*)이 *"reasoning trail 보존 + **새 framing 가능성** 양립"* 을 **co-equal 목표**로 명시한다.

목적이 anchoring 차단이라면, **agent 인스턴스 존속은 packet 규율을 완전히 준수하더라도 동일 해악을 packet 을 우회하는 별 채널(agent 자신의 잔존 컨텍스트)로 실현**한다. ⇒ "packet 은 요약, agent 는 살아있다"는 **packet 축에서 참이나 해악 축에서 거짓**이다.

단 이 불성립은 **ADR-067 이 실제로 결정을 내린 지점(§결정 1 trigger `current_count == 3`)에 한정**된다. 그 이전 통상 회차에 ADR-067 은 대응 결정을 보유하지 않으며, 오히려 현행 규범이 `reasoning_carryover` full-text 전달·debate transcript verbatim 주입으로 **carry 를 의무화**한다 — 통상 회차의 재개는 **기존 의무의 더 싼 구현**이다.

⇒ **결정**: 층위 분리는 정의역을 `재평가 trigger 미도달 회차` 로 좁힐 때만 성립하며, **ADR-067 §결정 1/3 의 재평가 스폰은 본 채널의 적용 제외(fresh-only)** 다. 이 carve-out 은 **ADR-067 안에 명문화**한다(Amendment 4) — 채널 도입으로 ADR-067 자신의 문구 *"ArchitectPLAgent re-spawn"* 이 **중의적(fresh 인가 continuation 인가)** 이 되므로, 신규 ADR 에만 두면 §결정 1 독자가 carve-out 을 모른다.

**대체 불가 확인**: 판독면 stale 가드는 *원인 코드* 축이나 재평가 trigger 는 **원인 코드와 무관하게 FIX 3회 누적으로 발동**하고, 독립 peer 최소 1 fresh 보존은 *dual-peer 리뷰 회차* 대상이나 **ArchitectPL 재평가는 peer 구조가 아니다**. ⇒ 별 축이 필요하다.

**부수 사실 취급**: `reasoning_carryover` 소비자는 **문서 계약층 3 site 뿐**이며 `.py`/`.sh`/`.js` 소비자는 **0건**이다. 이 사실은 *"1세대 처방이 기계 배선되지 않았다"* 만 입증하며 ★**처방 실패 ≠ 미배선**★ — §결정 5 의 논거(anchoring 차단) 자체를 반증하지 않는다. **위 판정은 이 미배선 사실에 의존하지 않는다.**

### §결정 10 — 검출력 보존: 독립 관측면 최소 1, 비용 축 단독 결론 금지

- **dual-peer 리뷰 회차에서 두 peer 를 동시에 재개로 덮지 않는다** — 최소 1 peer 는 fresh 로 유지해 **독립 관측면이 0 이 되지 않게** 한다.
- **비용 대조 리포트는 비용 축 단독으로 결론내지 않는다.** 검출력 축(발견 건수·심각도 분포)을 병기하고, 미측정이면 추정치로 채우지 않고 **"미측정"** 을 명시한다.

**근거** `[verified]`: 재검사 수확 체감(Biffl·Halling·Köhle 31개 팀 통제 실험 — 재검사의 benefit·net gain 이 1차보다 유의하게 낮으나 대부분 팀에서 여전히 양(+)) + capture-recapture 결함 총수 추정이 **두 탐색의 독립을 전제**한다는 사실. 그리고 ★**비대칭 가시성**★ — 비용 절감은 초 단위로 계측되고 검출력 손실은 "발견되지 않은 결함"이라 **정의상 관측면에 없다**. 계측만 붙이면 판단이 **구조적으로 재개 쪽 편향**된다. 계측 자체의 교란은 probe effect 문헌(Mytkowicz 등 — 3% 미만 오버헤드에서도 metric 을 올바로 추론할 수 없는 교란 발생)이 뒷받침한다.

> `[verified — 조사했으나 발견 없음]`: "동일 reviewer agent 재사용이 리뷰 품질에 미치는 영향"을 멀티에이전트 프레임워크 맥락에서 **정량 측정한 문헌은 발견하지 못했다**. 위 항목은 인간 대상 SE 문헌의 전이이며 전이 자체가 검증된 등가는 아니다 `[hypothesis]`.

### §결정 11 — evaluator 는 measurement append 경로와 **양방향 zero-import** 로 분리

파일 = `scripts/lib/check_round_continuation_eligibility.py`. `check_` 접두는 pure predicate 관행(83건), `append_` 는 writer(4건)이므로 **접두 자체가 이미 축 분리 신호**다. enum 은 **로컬 재선언**한다 — 직접 선례 = `scripts/lib/check_spawn_event_schema.py` 가 `_OUTCOME_VALUES`/`_TERMINATION_CAUSE_VALUES` 를 주석으로 출처만 밝히고 로컬 상수로 재선언한다.

**결박이 양방향인 이유**: 단방향만 두면 향후 "편의상" evaluator 를 append 안으로 끌어들이는 결합 표면이 남는다. ADR-170 §결정 21 적용범위 item 3(내용 앵커 = *"outcome/termination_cause 는 판정 결과 저장이지 판정 로직 inline 실행 아님"*)이 지키려는 것은 **append 프로세스 안에 판정 로직이 없다**는 사실이므로, 결박도 양방향이어야 정합이다.

**검사 = `ast` import-edge assert 이며 이는 신규 검사 종류다.** 기존 Hop3(`ast.parse`/`ast.walk` 사용)는 **symbol-presence** 검사이지 import-edge 가 아니며, repo 전체에서 `ast.Import`/`ast.ImportFrom` 을 수집하는 검사는 **0건**이다. "동형"은 **기법 수준**(stdlib ast + SyntaxError fail-closed)이지 검사 재사용이 아니다.

### §결정 12 — 정직 라벨 (advisory ceiling — "100% 기계강제" 표현 금지)

ADR-143 선례 형식을 따라, 본 채널에서 **기계 강제가 원리적으로 불가한 표면 4종**을 명시 declare 한다:

| # | 표면 | 성질 |
|---|---|---|
| 1 | `hooks/hooks.json` PreToolUse matcher 5종에 **`SendMessage` 0건** ⇒ 재개 회차에 spawn-gate 4-block 검증이 **구조적 미발화** | 검증 책임이 **hook(기계) → Orchestrator 저작(advisory)** 으로 이동. ★**경계 신설이 아니라 통제 약화**★ 로 정확히 기술 |
| 2 | `SendMessage` payload 에 **tier 판정 정보가 구조적으로 부재** | tier 가드 실준수는 기계 게이트 불가 |
| 3 | evaluator 분리 **우회 3종** = 문자열 동적 조립 `importlib` / `sys.modules` reflection / **코드 복붙** | AST 로 원리적 미차단 |
| 4 | 메시지 5번째 요소(무효화 선언)의 **실효** | presence 만 검사 가능, "실제로 전제를 버렸는가"는 판정 불가 |

**미완화 수용 2건**: (a) 메시지 문면 규율(SC-1)·anti-anchoring(SC-2)의 실준수 = advisory ceiling (b) **packet 재구축이 수행하던 sanitize 재작성 지점(choke point)이 재개 경로에 부재**함은 **재개의 정의상 불가피**하므로 완화가 아니라 **정직 declare** + 노출 창 축소(compaction 경계·`T`)로 처리한다.

**대칭 표면 정직 기재**: *"재개가 민감정보 보존 기간을 연장한다"* 는 ★**거짓**★ 이다 — `cleanupPeriodDays` 보존은 transcript 존재의 함수이지 재개의 함수가 아니며, fresh spawn transcript 도 동일 보존을 받는다.

### §결정 13 — 효과 기술 규율 (over-claim 금지)

본 채널의 효과를 **"모든 FIX 루프에서 재spawn 비용 제거"** 로 기술하지 않는다. 정확한 기술 = ★**"재개 적격 회차에 한해, 그리고 세션 Orchestrator tier 에 따라 실효 표면이 달라지는 조건부 절감"**★.

- opus Orchestrator 세션에서 **fable 지정 6종은 cap-down 대상이라 재개 불가**하며, 이는 **의도된 설계 경계이지 결함이 아니다**(안전을 실효 범위보다 우선한 선택).
- **이득 귀속 정확성**: spawn 지연의 지배 원인은 **프로세스 fork 단가 × hook 내부 다중 fork** 이며 "hook 개수"가 아니다 `[empirical-source: CFP-2946 §4.2 firsthand — Windows/MSYS 단일 호스트, 타 플랫폼 일반화 근거 없음]`. 재개 채널은 그 비용을 **우회**할 뿐 **제거하지 않는다**. 경쟁 처방인 **hook 내부 fork 통합**과는 ★**경쟁이 아니라 보완**★ 관계이며(재개 불가 회차에서 fork 비용은 그대로 남는다), 절감분을 재개 채널에 **과대계상하지 않는다**.

## 결과

### 긍정

- FIX 루프 재개 적격 회차에서 **context packet 재구축 + spawn-시점 hook 지연세**를 회피한다.
- ADR-067 이 `reasoning_carryover` 로 달성하려던 **architectural amnesia 차단**의 **더 싼 구현**을 통상 회차에 제공한다(§결정 9 3단).
- `name → agent_type → frontmatter tier` 경로가 원장 컬럼 추가로 완성돼 tier 가드가 **부분 기계화**된다(이전에는 매핑 경로가 repo 에 0건이었다).
- `dispatch_mode` 축으로 재개/fresh **비용·검출력 대조가 관측 가능**해진다(spawn-event timestamp 역산법은 판별력 0 으로 실증됐으므로 사용하지 않는다).

### 부정 · 수용한 비용

- **실효 표면이 세션 Orchestrator 모델에 의존**한다(§결정 13). opus 세션에서는 fable 지정 6종 재개가 원천 불가하다.
- **검출력 손실 리스크** — 동일 리뷰어 반복은 관측면을 다중화하지 않는다. §결정 10 이 최악(관측면 0)을 차단하나 한계 수익 저하 자체는 남는다.
- **통제 커버리지 축소** — 재개 회차에 spawn-gate 가 미발화한다(§결정 12 표면 1).
- **sanitize choke point 소실**(§결정 12 미완화 (b)).
- 신규 원자 예약 primitive 도입(선례 0건) — §결정 7.

### 계약 · 문서 영향

| 대상 | 영향 |
|---|---|
| `parallel-dispatch-protocol-v1` | MINOR — §6.4 3rd 분기 + I-6.1/I-6.5 정의역 축소 |
| `dev-process-event-v1` | MINOR + ADR-043 amendment — `dispatch_mode` index field |
| `spawn-event-v1` / `fix-event-v1` | **무접촉** (writer topology·§10 스키마 본체 불변) |
| `docs/orchestrator-playbook.md` | §14.11 컬럼 2 추가 / §3.0.12b·c 인접 재개 절 / max-wait 표 인접 `T` 행 |
| `docs/architecture/codeforge-family.md` | `## 인터페이스 계약` + `## 데이터 흐름` 갱신 + `### C4 Component` 편입 (ADR-078) |
| branch protection required contexts | **8-tuple 무변경** (AC-16 (b)층은 non-required) |
| ADR-067 | **Amendment 4** (§결정 9) |

## 관련 파일

- [ADR-067](ADR-067-fix-ledger-implementability-escalation.md) — Amendment 4 = 본 ADR 의 짝 (재평가 fresh-only carve-out + `Iter` 소비 규칙)
- [ADR-141](ADR-141-all-opus-single-tier.md) — Amd 6/7 tier override (충돌 없음 — 4 site 전부 tier-override 지배문 종속)
- [ADR-170](ADR-170-orchestrator-subagent-default-inline-whitelist.md) — §결정 19 dispatch 단일 권위 / §결정 2 표 row 7 `(c)` record-only
- [ADR-139](ADR-139-background-wait-liveness-gate.md) — max-wait 창 조건부 재사용, INV-L2 상속
- `docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md` — I-6.1/I-6.5 정의역 + §6.4 3rd 분기
- `docs/inter-plugin-contracts/dev-process-event-v1.md` — `dispatch_mode` index field
- `docs/orchestrator-playbook.md` — §14.11 Spawn ID 대장 / max-wait 표 / 재개 절차
- `scripts/lib/check_round_continuation_eligibility.py` — 적격 evaluator (Phase 2)
- `plugins/codeforge-review/templates/review-pl-base.md` — 재개 분기 단일 지점
- internal-docs `wrapper/change-plans/round-continuation-dispatch-channel.md` — 본 ADR 의 Change Plan

## 해소 기준

N/A — permanent policy (dispatch 채널 규범). 단 §결정 2 축 A(tier 보수 제약)는 **재검토 조건을 보유**한다: codeforge 가 재개 시 tier 유지 거동을 **자기 게이트로 직접 검증**하게 되면 제약 완화를 재검토할 수 있다. 그 재검토는 별도 Story 소관이며 본 ADR 의 sunset 이 아니다(§결정 2 의 fail-closed 술어는 어떤 경우에도 안전 방향이다).
</content>
