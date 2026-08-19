---
adr_number: 109
title: in-process Anthropic infra 429 surgical mitigation framework
status: Accepted
is_transitional: false
category: tooling-infrastructure
date: 2026-05-24
related_files:
  - skills/rate-limit-429-mitigation/SKILL.md
  - mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1354-in-process-429-mitigation.md
  - docs/kpi/429-incident.json
  - docs/kpi/429-incident-history.jsonl
  # templates/github-workflows/429-incident-telemetry.yml — Amendment 3 청산: 파일 부재(삭제 커밋 `017926df4` "prune 2단계"). 3년 가까이 "(Phase 2 scope)" 로 표기된 채 dangling 이었다. 재도입 시 신규 carrier 로 재등재할 것 — 본 주석은 삭제 이력 보존용
  - templates/team-spec-decompose.yaml
  - templates/team-spec-requirements.yaml
  - templates/team-spec-design.yaml
  - templates/team-spec-design-review.yaml
  - templates/team-spec-develop.yaml
  - templates/team-spec-code-review.yaml
  - templates/team-spec-security-test.yaml
related_stories:
  - CFP-1354
  - CFP-2823   # Amendment 1 carrier — §결정 1 감지집합 session/usage-limit class 편입 + fable-리밋 failover 합성
  - CFP-2944   # Amendment 2 carrier — 한도류 신호 판별식 D primary 이관 (본 ADR 소유 아님, 침범 금지)
  - CFP-2984   # Amendment 3 carrier — dead tenant 참조 정정 + 대기원 헤더 의미 정정 + dangling related_files 청산 + CB threshold telemetry-gated 재선언 + declaration-only 처분 + §결정 2 backoff single-SSOT
  - CFP-2967   # Amendment 4 carrier — §결정 4 telemetry 실채움 인계 수취(breaker 자동 무장 금지) + §결정 8.2 write ownership 확정 + OR-1 하한 declare
related_cfps:   # CFP-2967 Amendment 4 - related_stories mirror (key newly introduced, full mirror not partial)
  - CFP-1354
  - CFP-2823
  - CFP-2944
  - CFP-2984
  - CFP-2967
related_adrs:
  - ADR-039
  - ADR-044
  - ADR-057
  - ADR-064
  - ADR-067
  - ADR-068
  - ADR-082
  - ADR-097
  - ADR-104
  - ADR-106
  - ADR-108
  - ADR-141   # Amendment 1 — fable-리밋 opus failover override carrier (§결정 3 step2 dead slot re-tenant)
  - ADR-179   # Amendment 3 — salvage 번들 회수·인계 규약. 본 ADR = 신호 감지·재시도 remedy 축 / ADR-179 = remedy 발동 후 회수 판정 축 (disjoint)
  - ADR-043   # Amendment 4 sibling — 본 채널의 privacy·공표 경계 소유(ADR-043 Amendment 7 = allow-list 7 필드 + bound (2')). 본 ADR = 운영·write ownership·기록 어휘 축 (disjoint)
mechanical_enforcement_actions:
  - 429-retry-evidence-presence   # Amendment 3 처분 = **승격 후보 유지**(3종 중 유일). 대상 = §결정 8.1 marker regex — 구체 정본이 실재하고 marker 제거 mutant 가 discriminating. 승격 실행은 Phase 2 이며 discriminating mutant 실증 동반 의무(ADR-171 §결정 6), warning-first 로 태어난다(ADR-171 §결정 5)
  # debate-parallel-cap-check   — Amendment 3 처분 = **승격 기각 (always-green hollow)**. 대상 field `parallel_spawn_cap` 이 team-spec 7 file 에 전건 실재(3-hit/파일 실측)라 presence 검사가 구조적 항상-GREEN. 선언만 남기면 "기계 강제가 있다" 는 over-claim
  # deputy-stagger-check        — Amendment 3 처분 = **승격 기각 (동상)**. 대상 field `spawn_stagger_ms` 동일 사유. 두 항목은 삭제가 아니라 주석으로 보존 — 발의 이력과 기각 사유를 같은 자리에 남긴다(재발의 시 이 근거를 반증할 것)
amendments:
  - amendment: 1
    carrier_story: CFP-2823
    date: 2026-07-24
    scope: >-
      §결정 1 detection closed-set 을 base 4-tuple 에서 session/usage-limit class 2 literal
      편입해 확장 — `session limit`(확정, 2026-07-24 실관측 `You've hit your session limit`)
      + `usage limit`(추정·미실측, fail-open — 요구사항-named 개념 커버, 유일 firsthand 등장 =
      본 ADR §컨텍스트 §1:54 부정 문맥 "not your usage limit") = base 4 + class 2 = 6 literal.
      실관측 세션 한도 문자열이 base 4-tuple 과 substring 0/4 불일치(firsthand 반증)라 확장
      필수. 3→4 확장 선례(§결정 1 "Server is temporarily limiting" 편입, L97) 동형 — 별도
      enum 신설 아님, 단일 §결정 1 closed-set 확장, literal-substring `no regex wildcard`
      invariant 유지. §결정 1 base 4-tuple = byte-intact 보존(rewrite 0). 동반 = fable-리밋
      opus failover 의 ADR-109 합성 배치(§결정 3 step2 dead slot[구 ADR-057 §결정 2, moot]
      re-tenant + fable step1 bypass + cascade depth fable→opus hop count-in) — carrier =
      ADR-141 Amendment 6(SSOT), 본 amendment 는 감지집합 확장 SSOT + 합성 배치 codify.
      529(§결정 6)는 disjoint 유지(failover 감지집합 NOT-IN, `429`≠`529`). 상세 = 본문
      `## Amendment 1`.
    sunset_justification: >-
      N/A — §결정 1 closed-set invariant("5번째 pattern 추가 = 본 ADR Amendment 의무")의
      정확 이행이자 ratchet 강화 방향(감지 집합 확대, 약화 0). ADR-109 §해소 기준
      "N/A permanent policy — sunset_justification 면제" 상속(ADR-058 §결정 5 / ADR-064
      §결정 7 evidence-gated symmetric ratchet 강화 방향 정합).
  - amendment: 2
    carrier_story: CFP-2944
    date: 2026-08-12
    reinterpretation: true   # §결정 1/Amd1 감지집합의 *지위* 를 "판정 primary"에서 "비망라 fast-path"로 재해석 (문면·code-fence byte 무변경, 열거 내용 무변경) + §결정 5 "user manual resume only"의 정의역을 재시도 축 한정으로 재해석. self-declared — 의미 판정은 리뷰 lane 축.
    scope: >-
      한도류 신호 판정의 primary 를 §결정 1/Amendment 1 closed-set 열거에서 **의미론적
      판별식 D** 로 이관한다(열거는 비망라 fast-path 로 강등, code-fence byte 무변경 ·
      재열거 0 · 경쟁 enum 0). 구성: (b) **D-0 발신자 전제** — 판정 정의역 = 본 세션
      harness agent 실행 계층이 발신한 종료·오류 신호 한정, 타 벤더 API 한도(GitHub 등)는
      정의역 밖(firsthand: GitHub `API rate limit exceeded for user ID 12345.` = 6-literal
      1/6 매칭 → 전제 없이는 Anthropic 축 처방이 오착지). (c) 입력 표면 scope 불변식을
      판별식 본체에 부착(playbook §3.0.12b 문언을 fast-path 절에서 판정 절차 전체로 승격).
      (d)(e) D-i~D-iii 3항 + **4치 출력**(D-out-1 자기해소 / D-out-2 액션의존 /
      D-out-3 확정 부정 / D-indeterminate 평가 불확정). (f) negative control 2방향
      (N-a 비한도류 · N-b 자기해소 아님). (g) **판정 신호 원문 verbatim 기록 금지**
      (§결정 10 redaction matrix 확장 — 분류 결과·limb·근거 1줄만). (h) D-out-1
      자기확증 반증 축. (i) **§결정 5 축 한정 개정** — "자동 재시도 금지"(bounded retry
      상한) 보존, "작업 진행 중단"만 분리 + remedy 단조 비용 사다리 R0~R4(신규 재시도
      예산 0). 상세 = 본문 `## Amendment 2`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 방향 =
      **양방향 ratchet, 각 방향 firsthand evidence 동반**(ADR-064 §결정 7 evidence-gated
      symmetric ratchet): ① 감지 *대상 클래스* 확대(강화) 근거 = 현행 제품 문면 4/4
      6-literal 미매칭 firsthand 반증 ② 감지 *정의역* 축소(D-0 발신자 전제 = 오탐 제거)
      근거 = 타 벤더 문자열 1/6 매칭 firsthand reproducer + ADR-141 A6-6 "오탐 = 더 높은
      리스크(opus 낭비 + 실결함 은폐)" 자기선언. §결정 1 closed-set invariant("5번째
      pattern 추가 = Amendment 의무")는 **미발동** — 본 Amendment 는 literal 을 추가하지
      않는다(열거 무증감).
  - amendment: 3
    carrier_story: CFP-2984
    date: 2026-08-15
    reinterpretation: true   # 순수 additive 아님 — 개정 6건 중 4건이 기존 조항의 *지위·정의역* 을 소급 재규정한다. ① §결정 4 CB threshold 를 "telemetry 실채움 전까지 **미발동(non-firing)**" 으로 재선언 — 수치 무변경인 채 조항의 규범 지위가 live control → 구조적 발동 불가 declare 로 바뀐다(Amd2 marker 와 동형 축: 문면 무변경 + 지위 재해석). ② §결정 2 `Retry-After` 대기원의 **정의역 축소** — 구 문면이 `anthropic-ratelimit-*-reset` 과 `Retry-After` 를 "또는" 으로 묶던 것을 `retry-after` **한정**으로 좁히고 reset 계열을 대기원에서 배제. 기존 override rule 의 발동 조건이 달라지므로 additive 아님(단 이 건은 문면 편집 동반 — 재해석 ∧ 개정). ③ §결정 3 step2 / §결정 1 SSOT consumer 열거 / §결과 3곳에서 cross-model slot 의 tenant 를 `ADR-057 §결정 2` → `ADR-141 Amendment 6` 로 교체하며 구 tenant 의 지위를 "live 지시 대상" → "prior tenant, moot/dead" 로 재규정. ④ `mechanical_enforcement_actions` 3종 중 2종을 "선언된 기계 강제" → "승격 기각(always-green hollow)" 로 지위 강등. 방향 = 전건 **강화**(완화 0) 이나 지위 재규정이 실재하므로 `false` 로 적을 수 없다. self-declared — 의미 판정은 리뷰 lane 축.
    scope: >-
      **Amendment 2 절(본문 `## Amendment 2` ~ 파일 끝) 무접촉** — Proposed 조항 위 normative
      스택 금지(Orchestrator 판정 C). 본 Amendment 는 Accepted 본체(§결정 1~10) 와 frontmatter
      만 개정하고, Amendment 2 블록 안의 바이트는 하나도 바꾸지 않는다. 개정 6건:
      (1) **dead tenant 참조 정정** — §결정 3 step2 등이 지시하던 `ADR-057 §결정 2`(Sonnet→Opus)
      는 ADR-141 로 moot/dead 다. 그 사실은 이미 `:54`·`:341` 메타 절에 적혀 있었으나 **규범 본문에
      전파되지 않았다**(결함 class = "못 봤다" 가 아니라 "자기 인식을 규범면에 전파 안 함"). tenant
      만 교체하고 **slot ordinal 1..4 는 frozen** — 번호 재정렬은 ADR-141 A6-2(Accepted)의
      "step1 bypass → step2 직행" 을 **의미 반전**시키며(문법·참조가 멀쩡해 검출 불가) slot-번호
      의존 표면 26행/4파일 동기 수정을 강제한다. 구 tenant 는 `prior tenant … moot` 로 인접
      표기 보존(ADR-141 A6-6 dead-mark 보존 동형).
      (2) **§결정 2 `Retry-After` 대기원 헤더 의미 정정** — 현행 문면이 `anthropic-ratelimit-*-reset`
      과 `Retry-After` 를 "또는" 으로 묶고 RFC 7231 포맷 서술을 두 헤더에 공통 적용하는 구조라,
      절대시각 헤더가 초 단위 대기원으로 오독된다. 대기원 = `retry-after`(초 단위 상대값) **한정**,
      reset 계열은 절대시각이라 대기원에서 제외하고 잔여 창 계산에만 쓴다.
      (3) **dangling `related_files` 청산** — `templates/github-workflows/429-incident-telemetry.yml`
      파일 부재(삭제 커밋 `017926df4`). 삭제 아닌 주석 보존.
      (4) **§결정 4 CB threshold telemetry-gated 재선언** — 값 확정이 아니라 **미발동 선언**.
      3 window 전부 `docs/kpi/429-incident*` 의존인데 그 데이터원의 기계 append 경로가 0건이라
      breaker 는 구조적으로 open 될 수 없다. hollow-gate 를 GREEN 으로 위장하지 않기 위해
      "telemetry 실채움 전까지 미발동" 을 문면화한다. threshold 수치 변경 0.
      (5) **declaration-only 3종 처분** — `429-retry-evidence-presence` 1종만 승격 후보 유지,
      `debate-parallel-cap-check`·`deputy-stagger-check` 2종은 always-green hollow 로 승격 기각
      (대상 field 가 team-spec 7 file 에 전건 실재 → presence 검사가 항진). 주석 보존.
      (6) **§결정 2 backoff single-SSOT 조항 신설** — detection enum 에는 `:148` single-SSOT
      규율이 있어 skill 이 재열거를 거부하는데 backoff 곡선에는 동형 조항이 없어 skill 이 값을
      옮겨 적었고 이미 divergence 가 발생했다(SSOT 는 cap 위치를 열어뒀고 사본이 그것을 결정).
      규율의 정의역을 backoff 파라미터로 확장한다. **수치 자체는 무변경.**
      상세 = 본문 `## Amendment 3`.
    sunset_justification: >-
      N/A — `is_transitional: false` permanent policy 유지(§해소 기준 무변경). 방향 = **강화**:
      (a) 죽은 참조 제거 (b) 오독 유발 문면 정정 (c) hollow gate 의 GREEN 위장 차단
      (d) over-claim(기계 강제 3종 선언) 을 1종으로 축소 — 어느 항목도 기존 통제를 완화하지
      않는다. §결정 1 closed-set invariant 미발동(literal 무증감). §결정 2 backoff 수치·
      §결정 4 threshold 수치·§결정 3 slot ordinal 전건 무변경 — 본 Amendment 는 **참조 대상과
      선언 지위**만 정정한다. ADR-064 §결정 7 evidence-gated symmetric ratchet: 강화 evidence =
      ① `:54`·`:341` 자기 인식 ↔ 규범 본문 불일치 firsthand ② telemetry 데이터원 기계 append
      0건 firsthand ③ team-spec 7 file 3-field 전건 실재 firsthand.
  - amendment: 4
    carrier_story: CFP-2967
    date: 2026-08-19
    reinterpretation: true   # 순수 additive 아님 — 2건이 기존 조항의 지위·정의역을 재규정한다. ① Amendment 3 (4) 의 §결정 4 "telemetry 실채움 전까지 미발동" 선언을 **유지하되 사유를 교체**한다(데이터원 부재 → 임계 미검증). 데이터원이 채워진 뒤에도 breaker 는 미발동이며(U-2 사용자 확정), 이 재선언 없이는 실채움이 곧 자동 무장으로 오독된다. ② §결정 8.2 dual-tier 서술의 지위를 "두 파일이 있다"에서 "파일별 단독 writer 가 정해져 있다"로 재규정하고 집계기의 event tier write 권한을 read-only 로 강등한다. 방향 = 전건 강화(완화 0)이나 지위 재규정이 실재하므로 false 로 적을 수 없다. self-declared — 의미 판정은 리뷰 lane 축.
    scope: >-
      **Amendment 2 절(본문 `## Amendment 2` 블록) 무접촉** — `status: Proposed` ∧ CFP-2944
      소유이므로 그 안의 바이트를 하나도 바꾸지 않는다(Amendment 3 A3-0 동형 승계). 개정 5건:
      (1) **§결정 4 telemetry 실채움 인계 수취·종결** — Amendment 3 (4) 가 "telemetry 실채움 =
      본 Amendment scope 밖(계측 채널 실채움은 병렬 Story 소관)" 으로 인계했고 CFP-2967 축 ① 이
      그 수취인이다. 단 **U-2 사용자 확정 = circuit breaker threshold 자동 무장 금지** — 데이터가
      채워져도 §결정 4 는 미발동 유지하며 미발동의 사유만 "데이터원 부재" → "임계 미검증" 으로
      바뀐다. 3-window threshold 의 `[hypothesis]` 태그 해소(임계 재보정)는 별건이며 본 Story
      정의역 밖(ADR-068 I-5 dimensional empirical grounding — 데이터 존재는 측정의 시작점이지
      완료점이 아니다). (2) **§결정 8.2 producer/aggregator write ownership 확정** —
      `429-incident-history.jsonl`(event tier) = producer 단독 writer(append-only, kernel-atomic
      append, read-modify-write 금지) / `429-incident.json`(aggregate tier) = 집계기 단독 writer /
      집계기의 event tier 접근 = **read-only 강등**. 현행 위반 3종을 firsthand 실측으로 적시하고
      처분한다(V-1 주간 요약행을 event log 에 write — 키 집합 공유 0개 / V-2 동주
      `history_lines.pop()` / V-3 `seek(0);truncate()` 전체 재작성). 소유권 분리가 append-truncate
      레이스·동주 중복 집계·행 순서 의존 3종을 정의역에서 소거한다. aggregate tier 는
      `marker_incident_count`·`event_incident_count`·합 `weekly_incident_count` 를 분리 노출한다.
      (3) **OR-1 잔여 declare** — 본 채널의 429 계수는 **항상 하한(lower bound)이며 상한이 아니다.
      낮은 intensity bucket 을 "부하가 낮다"의 증거로 사용 금지(훅 timeout fail-open 의 부분 유실이
      정확히 고부하 구간에 집중되므로 편향 방향이 확정적). 편향 크기는 미측정. (4) **기록 어휘 ≠
      감지 어휘 분리** — `StopFailure` matcher 토큰 `rate_limit`(언더스코어)는 §결정 1 감지집합의
      어느 literal 과도 다른 값공간이며, `error_pattern` 값공간에 그것이 들어가는 것이 §결정 1
      감지집합에 원소를 추가하지 않음을 명시한다. **§결정 1 closed-set invariant 미발동 — detection
      literal 무증감.** (5) **§결정 10 90일 retention ↔ event tier 보존 요구 정의역 한정** — 보존
      요구의 정의역은 집계기 실행 경로이며 명시적 age-bounded 회전 actor 는 그 정의역 밖이다(무조건
      영구 무삭제로 읽으면 retention 조항과 자기모순). 상세 = 본문 `## Amendment 4`.
    sunset_justification: >-
      N/A — `is_transitional: false` permanent policy 유지(§해소 기준 무변경). 방향 = **강화**:
      (a) 단독 writer 확정으로 이력 파괴·중복 집계 경로를 정의역에서 제거 (b) breaker 자동 무장을
      명시 금지해 근거 없는 상수의 fail-closed 오작동 차단 (c) 계수의 하한 성격을 declare 해
      과소 산출을 "부하 낮음" 으로 오독하는 경로 차단 (d) 기록/감지 어휘 분리로 closed-set
      invariant 오염과 원시 에러 텍스트 기록을 동시 차단 — 어느 항목도 기존 통제를 완화하지
      않는다. §결정 1 detection literal · §결정 2 backoff 수치 · §결정 4 threshold 수치 ·
      §결정 3 slot ordinal 전건 **무변경**. ADR-064 §결정 7 evidence-gated symmetric ratchet:
      강화 evidence = ① 집계기 event-tier write 3종 firsthand(base `7a12d0a0f`) ② repo PUBLIC ∧
      착지 파일 git tracked firsthand ③ `StopFailure` matcher 값공간 벤더 문서 firsthand.
---

# ADR-109: in-process Anthropic infra 429 surgical mitigation framework

## 상태

`Accepted` (2026-05-24 KST) — CFP-1354 (Epic CFP-1353 Story A) chief author direct write per ADR-070 / CFP-578 chief author precedent. Sibling Story B (#1355) = OS-level external session auto-resume disjoint axis (ADR-110 reserved).

## 컨텍스트

사용자 발화 verbatim (Story §1, story-section-1-immutable 강제):

> codeforge의 개선이나 consumer 프로젝트 작업 중 API Limit이 걸리는 때가 있다. 이 때 limit이 풀리면 자동 시작했으면 좋겠는데
> 그리고 이런 에러가 발생하는 것도 해결해야 한다.
> API Error: Server is temporarily limiting requests (not your usage limit) · Rate limited

본 발화 = 2 axis disjoint mechanism layer (Epic CFP-1353 split):

- **Axis A (본 ADR-109 / Story A scope)**: in-process Orchestrator throttle — Claude Code session alive context, Anthropic infra 429 surgical mitigation. 사용자 발화 "이런 에러가 발생하는 것도 해결" 영역
- **Axis B (sibling ADR-110 / Story B scope)**: OS-level external session auto-resume — session dead context. 사용자 발화 "limit이 풀리면 자동 시작" 영역

기존 SSOT cover:

- **cross-model substitution axis** (§결정 3 step2 slot) — 현 tenant = **ADR-141 Amendment 6** (fable-리밋 → opus failover, max 1회 per-spawn). 본 ADR 와 **disjoint axis** (within-model timing axis). *prior tenant: ADR-057 §결정 2 (Sonnet → Opus) — ADR-141 로 **moot/dead**, dead-mark 보존* [Amendment 3 정정].
- **ADR-039 §결정 2** — Inline whitelist closed 4-entry enumeration (L99-L110). 5번째 entry "429 retry inline allowed" 신설 압박 명시 차단.
- **ADR-064 §결정 4 Trace 4** — multi-task spawn default = parallel (amendment_log L14-L15 + L97-L98 parallel-dispatch-prompt-check binding).
- **ADR-067** — max FIX 3/3 cap (§10 FIX Ledger). 429 retry ≠ FIX (운영 phase telemetry axis disjoint).
- **ADR-097 §결정 1** — paradigm replacement closed-set 3 조건 AND (9+ ADR sunset / 단일 atomic Epic / wholesale replacement). 본 ADR = 4 ADR amendment + 1 신설 sunset 0 → carve-out 비대상.
- **ADR-104 / ADR-106** — 운영 phase 1st-class 정의 + 운영 metric → PMOAgent input 회로.
- **ADR-108** — label-registry forcing function (description text `"Nth hotfix-bypass:* family member"` raw grep count parity).

기존 영역 부재 (GAP):

- **Detection 4-tuple SSOT**: ADR-057 / playbook §3.0.12 / skill body = 3 source 분산. 사용자 발화 verbatim `"Server is temporarily limiting"` = 어디에도 등장 0 (verified Grep).
- **Backoff curve normative**: empirical-source annotation (ADR-068 I-5) 의무 영역 부재.
- **Sequential composition**: same-model retry (within-model) → ADR-057 §결정 2 cross-model fallback escalation 합성 부재.
- **Circuit breaker 3-window AND**: 429 cascade 영역 자동 차단 정책 부재.
- **§10 vs §14 boundary**: 429 retry telemetry → §10 FIX Ledger 오용 시 ADR-067 RESET contamination risk.
- **Secret redaction matrix**: KPI commit 시 org_id / account_id 누설 영역 unconditional invariant 부재.
- **Retry primitive 위치**: Orchestrator inline (ADR-039 closed 4-entry 압박) vs skill body (closed 4-entry 보호) 결정 영역.

본 ADR = 위 7 GAP normative SSOT carrier — 10 §결정 통합 codify.

## 결정

### §결정 1 — Detection 4-tuple (single SSOT)

429 rate-limit detection = 다음 4 pattern any-match (closed-set, no regex wildcard):

```
"rate limit"
"quota exceeded"
"429"
"Server is temporarily limiting"
```

- **Single SSOT**: 본 §결정 1 = detection enum 단일 source. **ADR-141 Amendment 6** / `codeforge:rate-limit-429-mitigation` skill body / `docs/orchestrator-playbook.md` §3.0.12 = consumer cross-ref only (중복 정의 차단). *prior 열거의 `ADR-057 §결정 2` 는 moot/dead 라 소비자 목록에서 교체* [Amendment 3 정정].
- **4-tuple expansion rationale**: 사용자 발화 verbatim `"Server is temporarily limiting"` (Story §1) = 기존 3-pattern SSOT 미커버 (ArchitectAnalyst gap closure verified Grep — `"Server is temporarily limiting"` = 기존 SSOT 어디에도 등장 0).
- **closed-set invariant**: 5번째 pattern 추가 시 본 ADR Amendment 의무 (ratchet 강화 방향, ADR-064 §결정 7 정합).

### §결정 2 — Exp-backoff curve + Retry-After header 우선

- **Backoff curve**: full jitter `random_uniform(0, base * 2^attempt)` with `base=1s`, single attempt cap = 60s, total max attempts = 6 (1s → 2s → 4s → 8s → 16s → 32s nominal, jittered)
  - **empirical-source** (ADR-068 I-5 dimensional empirical grounding 정합): [verified-via: AWS Architecture Blog "Exponential Backoff And Jitter" Marc Brooker 2015-03-04, https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/] — full jitter algorithm verbatim 답습 (no-overlap retry distribution, contention avoidance proven)
- **Retry-After header 우선**: **`retry-after` header presence 시에만** exp-backoff override. 값 = 초 단위 상대값이므로 그대로 대기시간으로 유도한다.
  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 — `Retry-After` = delta-seconds 또는 HTTP-date]
  - **★ `anthropic-ratelimit-*-reset` 은 대기원이 아니다 (Amendment 3 정정)**: 해당 계열 헤더는 **RFC 3339 절대시각**이라 초 단위 대기값이 아니며, 쓰임은 "창이 언제 리셋되는가" 의 정보 제공이다. 두 헤더를 `또는` 으로 묶고 RFC 7231 포맷 서술을 공통 적용하던 구 문면은 **절대시각을 초 단위 대기원으로 오독**시킨다. 잔여 창 계산에 reset 시각을 참고하는 것은 허용하되, **대기원(wait source) 명명 대상에서는 제외**한다. 두 헤더의 의미 클래스가 다르다는 사실이 정정의 근거이며, 대기 산출 함수는 `retry-after` 부재 시 header 유래 대기를 산출하지 않는다.
  - **empirical-source**: [verified-via: Anthropic public docs https://platform.claude.com/docs/en/api/rate-limits — `anthropic-ratelimit-*-reset` = RFC 3339 절대시각 / `retry-after` = 초 단위]

> **★ Single SSOT — backoff 파라미터 (Amendment 3 신설)**: 본 §결정 2 = backoff 파라미터(formula · base · single-attempt cap · max attempts · nominal 계열 · 누적 budget) **단일 source**. `codeforge:rate-limit-429-mitigation` skill body / `docs/orchestrator-playbook.md` = **cross-ref only, 수치 재기재 금지**. §결정 6(529 cooldown 값)도 동형이다.
>
> 근거 = 규율의 정의역이 좁았다는 실측: detection enum 에는 `§결정 1` single-SSOT 조항이 있어 skill 이 실제로 재열거를 거부하는데(“확장 literal 재열거 금지(단일 SSOT)”), 바로 옆 backoff 에는 동형 조항이 없어 skill 이 값을 그대로 옮겨 적었다. 그리고 **이미 divergence 가 발생했다** — 본 §결정 2 는 `random_uniform(0, base * 2^attempt)` + 별도 진술 "single attempt cap = 60s" 로 cap 을 **표본 밖**에 두었는데, skill 사본은 `random_uniform(0, min(60, base * 2^attempt))` 로 cap 을 **상한 안**으로 옮겼다. SSOT 가 열어둔 자유도를 사본이 결정한 것이며, 두 문서를 읽은 두 사람이 서로 다른 구현을 얻는다. 이는 "장래 drift 위험" 이 아니라 **관측된 divergence** 다.
>
> **수치 무변경** — 본 Amendment 는 값을 바꾸지 않고 **소유권만** 고정한다. 사본 pointer 화(수치 8행 제거)는 Phase 2. Amendment 절 안의 dated 감사 기록(“무변경 확인 …”)은 **무접촉 보존** — 규범면 정정이 감사면 이력을 덮어쓰지 않는다.

### §결정 3 — Sequential composition (same-model retry → cross-model fallback)

429 detection 시 retry sequence:

1. **Same-model retry 1회** (within-model timing axis, 본 ADR 신설) — §결정 2 exp-backoff 적용
2. **실패 시 → cross-model substitution (step2 slot)** — 현 tenant = **ADR-141 Amendment 6** (fable-리밋 → opus failover, max 1회 per-spawn-attempt, cross-model substitution axis disjoint cross-ref). *prior tenant: ADR-057 §결정 2 (Sonnet → Opus) — moot/dead, `:341` re-tenant note 참조* [Amendment 3 정정]
3. **opus 도 429 → 6 attempts soak** (§결정 2 max 6 attempts cap) → §결정 4 circuit breaker open
4. **Cascade depth ≥ 2 → §결정 5 user manual resume only** ("자동 재시도 금지" invariant 정합 — 현 정박 = 본 §결정 5 자신 + ADR-141 A6-4 cascade count-in) [Amendment 3 정정]

> **★ slot ordinal frozen (Amendment 3, 비협상)**: 위 step 번호 `1..4` 는 **재정렬 금지**다. step2 는 빈 slot 이 아니라 **ADR-141 Amendment 6 가 점유 중인 live slot** 이며(구 tenant 만 dead), 번호를 당기면 ADR-141 A6-2(Accepted)의 "§결정 3 **step1**(same-model exp-backoff soak)을 bypass 하고 **step2**(cross-model substitution)로 직행" 이 *"soak 을 bypass 하고 soak 으로 직행"* 이라는 자기모순 지시로 읽힌다. 이 실패 양태는 stale pointer(링크 끊김, 검출 가능)가 아니라 **의미 반전**(문법·참조 모두 유효 → 검출 불가)이다. slot-번호 의존 표면 실측 = **26행 / 4파일**(ADR-109 · ADR-141 · playbook · rate-limit SKILL) — 1행만 놓쳐도 조용한 규범 변조가 된다. 참조는 서수 대신 **경로 키**(`same-model-timing` / `cross-model-substitution` / `soak` / `manual-resume`)로 옮기는 것을 권장한다.

**cross-model axis invariant 보존 cross-ref**: 본 §결정 3 = within-model timing axis (same-model retry 우선) — cross-model substitution axis(현 tenant ADR-141 Amendment 6) 와 sequential composition 정합. **ADR-057 amendment 0** — ADR-057 은 `Superseded`(by ADR-141) 이며 본 ADR 이 그 문서를 개정하지 않는다. 단 ADR-057 **§결정 4 / §결정 6(529 cooldown)** 은 미분류 remedy 라우팅의 **배타 지배 참조**로 여전히 유효하며 본 Amendment 의 정정 대상이 **아니다**(치환 시 미분류 사건 라우팅이 끊긴다).

### §결정 4 — Circuit breaker 3-window AND

Circuit breaker open trigger = 3 window 모두 충족 (AND):

| Window | Threshold | Source |
|---|---|---|
| Fast | 5건 / 1min | `docs/kpi/429-incident-history.jsonl` rolling window |
| Medium | 10건 / 5min | 동상 |
| Slow | 3건 / 1 week | `docs/kpi/429-incident.json` weekly aggregate |

- **[hypothesis]**: 본 3-window threshold = baseline 추정. Phase 2 telemetry refine 의무 (post-deploy actual incident rate 측정 후 사용자 확인 — ADR-068 I-5 dimensional empirical grounding 정합).
- **circuit breaker open 후**: §결정 5 cascade depth ≥ 2 처리 (user manual resume only).
- **★ telemetry-gated 재선언 (Amendment 3 — 값 확정 아님)**: 위 3 window 는 전부 `docs/kpi/429-incident-history.jsonl` / `docs/kpi/429-incident.json` 에 의존하는데, **그 데이터원의 기계 append 경로가 0건**이다 — 계량 스크립트의 호출자를 repo 전수 검색하면 문서 언급 2줄뿐이고 실행 표면이 없으며(`templates/github-workflows/` 에 429 telemetry workflow 부재), history 파일의 DATA 행은 **2행**(수기 기입, 2026-05-26 · 2026-07-02)이다. 30분·1분·5분 rolling window count 는 항구적으로 0 이므로 **breaker 는 구조적으로 open 될 수 없다.**
  - 따라서 본 §결정 4 는 **telemetry 실채움 전까지 미발동(non-firing) 상태임을 명시 선언**한다. threshold 수치는 무변경이며, 이 선언은 값 확정이 아니라 **지위 정직화**다 — 발동 불가 게이트를 발동 가능한 것처럼 두면 hollow gate 가 GREEN 으로 위장된다.
  - **동일 데이터원 공유 표면 declare**: `codeforge:rate-limit-429-mitigation` skill body 의 intensity 분기(`count_429_incidents_last_30min()`) 도 같은 파일에 걸려 있어 **동일 결함을 공유**한다 — intensity 는 상시 `0` 으로 낙하한다. 데이터원 부재를 침묵으로 삼키지 말고 **명시 보고**할 것.
  - **telemetry 실채움 = 본 Amendment scope 밖**(계측 채널 실채움은 병렬 Story 소관). 본 Amendment 는 미발동 사실의 **declare 까지만** 한다.

### §결정 5 — Cascade depth ≥ 2 → user manual resume only

`cascade_depth` 정의 = 단일 user request 안 retry sequence 의 nested cascade level. depth ≥ 2 (예: same-model 429 → Opus fallback → Opus 429 → 2차 retry burst) 시:

- **자동 재시도 금지** (ADR-057 §결정 2 invariant verbatim 답습)
- **user manual resume only** — `AskUserQuestion` escalation 또는 사용자 turn 대기
- **`docs/kpi/429-incident-history.jsonl` `cascade_depth` field append-only event log** (ADR-106 운영 metric → PMOAgent input 회로 정합)

### §결정 6 — 429 vs 529 disjoint 분기

- **429** (Anthropic rate limit) = §결정 1 4-tuple detection + §결정 2 exp-backoff
- **529** (Anthropic overloaded) = retry 무의미, **longer cooldown 60s base max 300s** (5x longer cap)
  - **rationale**: 529 = service-wide overload signal (single retry sequence 영역 외, sustained high load 영역). exp-backoff 적용 시 cascade amplification risk → longer cooldown invariant.
  - **detection**: HTTP 529 status code (`"529"` substring 별도 detection enum 추가 영역 = 본 §결정 6 — §결정 1 4-tuple disjoint axis)

### §결정 7 — Retry primitive 위치 = skill body (ADR-039 closed 4-entry 보호)

Retry sequence 자체 implementation 위치 = `codeforge:rate-limit-429-mitigation` skill body 안 3-step procedure (탐지 / 대기 / 재시도). Orchestrator inline whitelist (ADR-039 §결정 2 closed 4-entry: 사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report) 확장 0건.

- **rationale**: ADR-039 §결정 2 L110 verbatim "5번째 카테고리 추가 = ADR-039 amendment 의무. 본 closed enumeration 가 future '429 retry inline allowed' 압박을 차단" — closed enumeration 보호 우선 (RefactorAgent pattern 2 권고 + chief 결정 정합).
- **ADR-039 §결정 9 신설** (CFP-1354 Amendment N): §결정 2 4-entry 무변경 + §결정 9 carryover sunset_justification — rate-limit second-order risk 측정 = 본 §결정 7 + §결정 8 흡수.
- **alternative reject**: ADR-039 5번째 entry "429 retry inline allowed" 추가 = chief REJECT (InfraOp D-13 advocacy REJECTED, 본 결정 + ADR-039 Amendment N 정합).

### §결정 8 — Telemetry SSOT (§14 Lane Evidence marker + KPI dual-tier)

#### §결정 8.1 §14 Lane Evidence marker

`transcript` field 의무 marker:

```
[429-auto-retry: count=<N>, final_status=<success|failed>]
```

- regex (mechanical lint `429-retry-evidence-presence` warning tier, declaration-only Wave 1):

```
\[429-auto-retry: count=\d+, final_status=(success|failed)\]
```

#### §결정 8.2 KPI dual-tier

- `docs/kpi/429-incident.json` — weekly aggregate (cron, `rate-limit-fallback.json` precedent 답습)
- `docs/kpi/429-incident-history.jsonl` — append-only event log (ADR-106 `operational-signal-history.jsonl` precedent 답습)
- **schema**: §결정 10 secret redaction matrix 정합

### §결정 9 — §10 FIX Ledger vs §14 telemetry axis disjoint (ADR-067 RESET contamination 차단)

- **§10 FIX Ledger** = governance FIX root cause classification (ADR-067 max FIX 3/3 cap + RESET counter)
- **§14 Lane Evidence** = lane-spawn evidence audit trail (ADR-031 §결정 1)
- **429 incident marker** (`[429-auto-retry: count=N, final_status=...]`) = **§14 only** (운영 phase metric, ADR-104 정합)
- **§10 row append 금지**: 429 retry → fix:* label 미부착 + ADR-067 RESET counter 영향 0 (invariant 보존)
- **boundary violation 차단 invariant**: 본 §결정 9 = ADR-067 RESET contamination 차단 정합 (운영 phase telemetry vs governance FIX disjoint axis 명시 의무)

### §결정 10 — Secret redaction matrix (unconditional invariant ADR-068 I-3)

| 데이터 | 분류 | 처리 |
|---|---|---|
| `org_id` | Secret | **strip (collection-time)** — unconditional invariant (ADR-068 I-3 defense-in-depth) |
| `account_id` | Secret | 동상 strip |
| `session_uuid` | Internal | hash (SHA-256 truncated 8-byte) |
| `api_endpoint` | Internal | mask (domain only, path strip) |
| `timestamp` | Public | verbatim (KST `+09:00` ISO 8601, ADR-079 §결정 2) |
| `error_message` | Internal | verbatim (4-tuple enum match only, no user prompt verbatim) |
| `retry_count` / `cascade_depth` / `final_status` / `lane` / `agent_role` (enum) | Public | verbatim |

- **Retention**: 90일 raw event JSONL + 영구 weekly aggregate JSON (dual-tier — ADR-058 §결정 5 sunset_justification 면제, governance 영구 보존)
- **unconditional invariant rationale** (ADR-068 I-3 정합): org_id / account_id 수집 자체 금지 (defense-in-depth) — 후속 redaction step 의존 0 (collection-time strip)

## 결과

### 긍정

- **사용자 발화 cover**: `"Server is temporarily limiting"` 4-tuple detection + 5 sub-area surgical mitigation framework 신설 (Story §1 verbatim 영역 정합)
- **ADR-039 closed 4-entry invariant 보존**: 5번째 entry 신설 0 (RefactorAgent pattern 2 권고 + chief 결정)
- **cross-model substitution axis invariant 보존**: 해당 axis 무변경, within-model timing axis disjoint cross-ref (현 tenant = ADR-141 Amendment 6; *prior: ADR-057 §결정 2 — moot/dead*) [Amendment 3 정정]
- **ADR-067 RESET contamination 차단**: §결정 9 §10 vs §14 boundary 명시 의무
- **ADR-068 I-5 dimensional empirical grounding 정합**: backoff curve empirical-source = AWS Marc Brooker 2015 + threshold 3건 [hypothesis] Phase 2 refine
- **ADR-082 §결정 6 retain pattern 답습**: `mechanical_enforcement_actions: []` declaration-only Wave 1 (pattern_count ≥ 2 재발 시 follow-up CFP MUST promote)

### 부정·trade-off

- **3 mechanical_enforcement_actions warning tier deferred-followup**: actual mechanical wire = Phase 2 sibling sub-Story carrier (Phase 1 PR scope 외)
- **`[hypothesis]` threshold (§결정 4 circuit breaker 3-window)**: Phase 2 telemetry refine 의무 = post-deploy actual incident rate 측정 후 사용자 확인 (immediate value 제한)
- **Retry primitive 위치 = skill body**: Orchestrator inline 0건 = retry overhead = skill spawn cost (mitigation: skill body decision tree caching, Phase 2 refine 영역)

### 영향 받는 코드·레이어·운영 경계

- **Orchestrator** (top-level Claude session) — detection 4-tuple match logic (ADR-039 inline whitelist 1번 entry 사용자 dialog scope 안 verify-before-trust, Story §2.1 verified state table 1st applied dogfood case 답습)
- **`codeforge:rate-limit-429-mitigation` skill body** — 3-step procedure (탐지 / 대기 / 재시도) + decision tree (Phase 0 brainstorm sequential 2-batch fallback)
- **§14 Lane Evidence transcript writer** — marker regex schema 정합
- **KPI artifact writer** (`docs/kpi/429-incident.json` + `429-incident-history.jsonl`) — §결정 10 redaction matrix 적용
- **debate-protocol-v1 v1.2 `pause_condition`** (declarative) — round N+1 진입 직전 cascade detection (별 carrier, version bump 결정 영역)
- **7 team-spec yaml** — `parallel_spawn_cap` + `spawn_stagger_ms` + `cascade_circuit_breaker` 3 field 신설 (ADR-044 Amendment N, atomic sibling sync)

## 해소 기준

N/A — permanent policy

`is_transitional: false` 영역 (Anthropic infra 429 = 운영 영구 fact, 사용자 plan upgrade 영역 disjoint). ADR-058 §결정 7 보안 ADR default presumption `false` 정합. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (5 sub-area normative SSOT 신설), 약화 0건. sunset_justification 면제.

## 관련 파일

- [skills/rate-limit-429-mitigation/SKILL.md](../../skills/rate-limit-429-mitigation/SKILL.md) — §결정 7 retry primitive 위치 SSOT
- `mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1354-in-process-429-mitigation.md` — Phase 1 Change Plan carrier (dogfood-out per ADR-013, `doc-locations.yaml change_plan dogfood variant` 정합)
- `docs/kpi/429-incident.json` (Phase 2 scope) — §결정 8.2 weekly aggregate KPI
- `docs/kpi/429-incident-history.jsonl` (Phase 2 scope) — §결정 8.2 append-only event log
- ~~`templates/github-workflows/429-incident-telemetry.yml` (Phase 2 scope) — telemetry workflow warning tier~~ → **Amendment 3 청산**: 파일 부재(삭제 커밋 `017926df4`). dangling 상태로 존치되며 "Phase 2 에 있다" 는 인상을 주었다. 재도입 시 신규 carrier 로 재등재
- `templates/team-spec-*.yaml` (7 file) — ADR-044 Amendment N `parallel_spawn_cap` + `spawn_stagger_ms` + `cascade_circuit_breaker` field 신설
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 7 closed 4-entry 보호 + Amendment N §결정 9 carryover sunset_justification
- [ADR-044](ADR-044-phase-scoped-sequential-team.md) — Amendment N team-spec yaml schema 확장
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — §결정 3 sequential composition cross-ref (cross-model substitution axis disjoint)
- [ADR-064](ADR-064-decision-principle-mandate.md) — §결정 4 Trace 4 Amendment N surgical exception channel
- [ADR-067](ADR-067-fix-ledger-implementability-escalation.md) — §결정 9 RESET contamination 차단 cross-ref
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — I-3 defense-in-depth (§결정 10) + I-5 dimensional empirical grounding (§결정 2)
- [ADR-082](ADR-082-write-time-self-write-verification-mandate.md) — §결정 6 retain pattern 답습 (declaration-only Wave 1)
- [ADR-097](ADR-097-paradigm-replacement-governance-anchor.md) — closed-set 3 조건 AND 미충족 (paradigm replacement 비대상)
- [ADR-104](ADR-104-operational-phase-definition.md) — 운영 phase 1st-class 정의
- [ADR-106](ADR-106-operational-signal-pmo-input-circuit.md) — 운영 metric → PMOAgent input 회로
- [ADR-108](ADR-108-label-registry-v2-frozen-baseline-description-carry-drift.md) — label-registry forcing function (description text raw grep count parity)

## Amendment 1 (CFP-2823 — session/usage-limit class 감지집합 편입 + fable-리밋 failover 합성)

**날짜**: 2026-07-24 KST · **carrier**: CFP-2823 · **방향**: ratchet **강화**(§결정 1 detection closed-set 확대, 약화 0). 본 Amendment 가 §결정 1 closed-set invariant("5번째 pattern 추가 = 본 ADR Amendment 의무")의 정확 이행이다. **§결정 1 base 4-tuple 은 byte-intact 보존**(rewrite 0) — 본 Amendment 가 class 2 literal 을 추가할 뿐이다. fable-리밋 opus failover 의 규범 SSOT = [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 6; 본 Amendment 는 그 감지 SSOT + framework 합성 배치를 codify 한다.

### (a) 확장 rationale (firsthand 반증)

실관측 리밋 문자열 (2026-07-24, CFP-2823 진행 중 fable PL 이 세션 리밋으로 mid-run 조기종료하며 발화):

```
Agent terminated early due to an API error: You've hit your session limit · resets 10:20pm (Asia/Seoul)
```

이 문자열은 §결정 1 base 4-tuple(`rate limit` / `quota exceeded` / `429` / `Server is temporarily limiting`)과 substring **0/4 불일치**(firsthand — reproducer `any(p in s for p in base)` = exit 1 RED). 즉 §결정 1 이 사용자 요구(사용량/세션 한도 감지, CFP-2823 §1)를 **미커버**한다. → session/usage-limit class 를 §결정 1 closed-set 에 편입해야 커버된다.

### (b) 확장 감지집합 (본 Amendment = 확장 SSOT)

session/usage-limit 포함 detection = 다음 6 literal any-match (closed-set, no regex wildcard — §결정 1 invariant 승계):

```
"rate limit"
"quota exceeded"
"429"
"Server is temporarily limiting"
"session limit"
"usage limit"
```

- 앞 4 literal = **§결정 1 base 4-tuple, byte-frozen**(순서·문자 무변경). 뒤 2 literal = **본 Amendment 1 신규 class 2**: `"session limit"`(확정 — 2026-07-24 실관측) + `"usage limit"`(추정·미실측 — 요구사항-named 개념 커버, fail-open; (f) 참조).
- **별도 enum 신설 아님** — 단일 §결정 1 closed-set 확장(3→4 확장 선례[§결정 1 "Server is temporarily limiting" 편입, L97] 동형). literal-substring `no regex wildcard` invariant 유지(정규식 wildcard 도입 0).

### (c) enum single-SSOT 강화 (G1)

본 code-fence(6 literal) = detection enum 단일 source. `codeforge:rate-limit-429-mitigation` skill body / `docs/orchestrator-playbook.md` §3.0.12 / ADR-141 Amendment 6 = **prose cross-ref only**(중복 정의 0, §결정 1 "Single SSOT" 규율 승계). AC-4 discriminating check fixture 는 본 code-fence 를 **파싱해 enum source 로** 사용한다 — 하드코딩 사본 금지(fixture-vs-SSOT drift 차단).

### (d) fable-리밋 failover 합성 배치

ADR-141 Amendment 6(규범 SSOT)의 fable-리밋 opus failover 를 본 framework 에 합성한다:

- **§결정 3 step2 dead slot re-tenant** — step2(cross-model substitution)가 cross-ref 하던 구 ADR-057 §결정 2(sonnet rate-limit→opus)는 ADR-141 로 moot/dead 라 구조적으로 비어 있다. fable 브랜치가 신규 trigger(fable 리밋)로 그 slot 을 re-tenant(부활 아님 — ADR-057 Superseded 유지).
- **fable step1 bypass** — fable 리밋 시 step1(fable same-model exp-backoff soak)을 건너뛰고 step2(fable→opus)로 즉시 직행(Option A 즉시전환 — ADR-141 A6-2 근거 3층: reset long-horizon / 별개 pool / Retry-After trap). opus 착지 **후** 비로소 §결정 2 exp-backoff / §결정 3 step1·3·4 가 opus 를 same-model 로 재정박.
- **cascade depth count-in** — fable→opus hop = `cascade_depth` **1(COUNTS)**. opus 착지 후 opus 자기 within-model soak 은 미증가. opus soak 소진 후 cascade ≥ 2 = §결정 5 user manual resume only.
- **§14 격리** — failover = §14 전용 태그 `[rate-limit-failover:fable→opus]`(§결정 9 §10 FIX Ledger 금지 상속, 기존 §결정 8 `[429-auto-retry: ...]` 및 dead 태그 `[rate-limit-fallback:sonnet→opus]`/`[model-unavailable-fallback:fable→opus]` 와 비합산·별도 measurement).

### (e) 529 disjoint 재확인

529(`529` / `overloaded`) = pool-agnostic service-wide overload → **failover 감지집합 NOT-IN**. §결정 6(429 vs 529 disjoint — longer cooldown 60s→300s)이 correct handler 이며, 529 에 failover 적용 시 §결정 6 "cascade amplification risk" 정합으로 futile+amplifying. literal `429` ≠ `529`(substring 무접점) 확인 — 529 는 본 Amendment 확장 감지집합에 편입하지 않는다(운영 근거 = pool-agnostic overload, 단순 "enum 밖" 아님).

### (f) `usage limit` negated-context 정직 note + `429` over-match wart

- **`usage limit` = 추정·미실측** — 실관측 runtime 문자열은 `session limit` 뿐(`usage limit` 관측 0건, discriminating check 무기여). 유일 firsthand 등장 = 본 ADR §컨텍스트 §1(L54)의 **부정 문맥** `Server is temporarily limiting requests (not your usage limit)`. 부정 문맥 substring 매칭은 무해하나(fail-open bounded) literal 선정 근거는 부실 — 요구사항-named 개념(사용량 한도, CFP-2823 §1 intake 결정 3) 커버용으로 유지(over-inclusion 무해·bounded). 설계리뷰/구현 lane corroborate 대상.
- **`429` bare-substring over-match** — `429` 는 무관 문자열(예: `error 10429`)에 substring 매칭될 수 있는 bounded wart. no-regex-wildcard invariant 와 tension(좁히려면 word-boundary 필요하나 wildcard 금지)이나, 현재는 fail-open bounded 로 수용(§결정 1 base 이미 동일 성질). 좁힐지는 설계 재량.
- **case-sensitivity gap** — closed-set 대소문자 구분 substring 이라 `Session Limit`(대문자) 형태는 miss 가능. 실관측은 소문자 `session limit` 이라 현 위험 낮음 — literal 선정·case-fold 여부는 설계리뷰 escalate 후보(CFP-2823 §5.7).

## Amendment 2 (CFP-2944 — 한도류 신호 판별식 D primary 이관 + 발신자 전제(D-0) + §결정 5 축 분리)

**날짜**: 2026-08-12 KST · **carrier**: CFP-2944 · **status**: Proposed (Phase 1 draft — 착지 전) · **방향**: **양방향 ratchet**(감지 대상 클래스 확대[강화] ⊕ 감지 정의역 축소[오탐 제거], 각 방향 firsthand evidence 동반 — ADR-064 §결정 7).

**본 Amendment 가 하지 않는 것 (선언 우선)**: §결정 1 base 4-tuple 및 **Amendment 1 (b) 6-literal code-fence = byte 무변경**. literal 추가·삭제·순서 변경 0, 재열거 0, 경쟁 enum 신설 0. 따라서 §결정 1 closed-set invariant("5번째 pattern 추가 시 Amendment 의무")는 **미발동**이다. 본 Amendment 는 열거를 건드리지 않고 **판정 primary 를 열거 밖 상위 규칙으로 이관**한다.

### (a) 문제 — 열거 완전성 가정의 firsthand 반증

Amendment 1 은 감지집합을 4→6 literal 로 확장했으나 "열거로 닫힌다"는 가정 자체는 유지했다. CFP-2944 요구사항 lane 이 본 ADR code-fence 를 **파싱해**(하드코딩 사본 0) `any(p in s for p in lits)` 를 실행한 결과:

| 문자열 | 출처 | 6-literal any-match |
|---|---|---|
| `You've reached your Fable 5 limit. Run /usage-credits to continue` | CFP-2944 리뷰 PL 실사망 문구 (firsthand) | **0/6** |
| `Approaching 5-hour limit.` | 공식 support 12466728 | **0/6** |
| `5-hour limit reached - resets [time].` | 공식 support 12466728 (`blocking error message` 로 규정) | **0/6** |
| `5-hour limit resets [time] - continuing with usage credits.` | 공식 support 12466728 | **0/6** |
| `You've hit your session limit · resets 10:20pm (Asia/Seoul)` | 2026-07-24 실관측 (**대조군**) | 1/6 (`session limit`) |

제품 문면은 모델명·한도 창 길이·플랜에 따라 변하는 **가변 표층**이고 열거는 그 표층의 과거 스냅샷이다. 열거가 primary 인 한 §결정 3·ADR-141 Amendment 6 의 remedy 는 **실사례에서 점화되지 않는다**. 이는 같은 SSOT 의 같은 병리 3번째 발현(3→4→6 확장)이며, 4번째 확장(7번째 literal)으로는 닫히지 않는다.

### (b) D-0 발신자 전제 — 판정 정의역 (신설)

**D-0 (전제)**: 본 판정 절차의 정의역 = **본 세션 harness 가 실행하는 agent 계층이 발신한 종료·오류 신호**(Anthropic API/harness 발). 타 서비스·타 벤더 API 의 한도 신호(GitHub·외부 SaaS 등)는 **정의역 밖**이며 각자의 소관 통제로 라우팅된다.

- **firsthand reproducer (정의역 없이 발생하는 오착지)**: GitHub REST primary 한도 문면 `API rate limit exceeded for user ID 12345.` 은 6-literal 중 `rate limit` 에 **1/6 매칭**한다. §결정 1/Amendment 1 의 매칭은 즉시 확정이므로, D-0 이 없으면 **GitHub 한도가 Anthropic 축 처방**(fable→opus failover · usage credits · §결정 2 backoff)으로 착지한다 — 무효 조치 + 실결함 은폐.
- **D-0 은 fast-path 에도 소급 적용된다** — 즉 §결정 1/Amendment 1 감지집합의 **적용 전제**다. code-fence 는 무변경이며(전제는 fence 밖 prose), 열거는 D-0 을 통과한 신호에 대해서만 평가된다.
- **방향 정직**: 이는 감지 **정의역의 축소**(오탐 제거)다. 약화가 아니라 정확도 강화로 판정하는 근거 = ADR-141 A6-6 자기선언 — "오탐 = 더 높은 리스크(opus 낭비 + 실결함 은폐)".

### (c) 입력 표면 scope 불변식 — 판정 절차 전체에 부착

`docs/orchestrator-playbook.md` §3.0.12b 의 scope 문언은 현재 **6-literal fast-path 절에만** 소속되어 판별식을 덮지 못한다. 본 Amendment 는 이를 판정 절차 전체(fast-path ∪ 판별식 D)의 불변식으로 승격한다 — 원문 생략 없는 full-block 인용:

> **감지** = ADR-109 §결정1 Amendment 1 감지집합 any-match(6 literal — base 4-tuple + `session limit` + `usage limit`). enum authoritative SSOT = ADR-109 §결정1 Amendment 1 code-fence(**cross-ref only — 재열거 금지, 중복 정의 0**). scope 불변식 = error/termination notification 표면 한정(subagent substantive output 본문 NOT — false-positive hazard). 발동 표면 2종 = (a) spawn-시점 거부 ∪ (b) mid-run 조기종료(`Agent terminated early ...` task-notification).

**승격 후 scope (판정 절차 전체 적용)**: 판정 입력으로 허용되는 표면 = (a) spawn-시점 거부 ∪ (b) mid-run 조기종료 task-notification **2종 한정**. **비허용 표면**: subagent substantive output 본문 / 도구 반환 텍스트(PR·Issue 본문·WebFetch·외부 워커 출력·repo 파일) / 사용자 외 제3자가 내용을 통제할 수 있는 임의 텍스트. 본 scope 는 판별식 D 가 열거보다 **넓은 문면**을 받아들이기 때문에 오히려 더 엄격히 요구된다 — 넓은 판정면 ⊕ 무경계 입력면 = 분류 입력 주입 취약(CFP-2944 §7 T6).

### (d) 판별식 D (primary)

D-0 을 충족하고 (c) scope 표면에서 도착한 종료·오류 신호가 다음 3항을 **전부** 충족하면 한도류로 분류한다:

| 항 | 내용 |
|---|---|
| **D-i 자원 소진 지시** | 신호가 사용량·한도·요금제 자원의 소진 또는 경계 도달을 지시한다. 모델명·한도 창 길이·플랜명은 **가변 표층**(`Fable 5 limit` / `5-hour limit` / `session limit`) — 특정 문면에 의존하지 않는다. 여기서 "창" = **한도 리셋 창**(5시간 rolling·주간)이며 **컨텍스트 창(context window)과 무관**하다(컨텍스트 창 초과 = D-i 불충족, 요청 형상 축) |
| **D-ii 작업 결함 무관** | 원인이 요청 내용의 결함(로직 오류·입력 오류·권한 오류·모델 미존재)이 아니라 **자원 가용성**이다 |
| **D-iii 회복 가능** | 시간 경과 또는 대체 자원(usage credits · 별개 모델 pool · 과금 전환)으로 해소 가능한 class 다 |

**fast-path 의 지위 (강등 — 폐지 아님)**: §결정 1/Amendment 1 6-literal = **비망라 기계 fast-path**. 매칭 = 한도류 **확정**(D-i~iii 재평가 불요, 단 D-0·(c) scope 는 여전히 전제) → 착지 분기는 (e) 로 재판정. **미매칭은 "한도 아님"을 의미하지 않는다** — 미매칭 시 판별식 D 로 판정을 계속한다.

### (e) D 의 출력 = 4치 (라우팅 표)

| 출력 | 성립 조건 | 라우팅 | 그 입력 클래스를 이미 지배하는 통제 |
|---|---|---|---|
| **D-out-1 한도류·자기해소** | D 충족 ∧ remedy 가 **이미 활성화된 대체 자원**(활성 credits 잔액·별개 모델 pool)이거나 Orchestrator 액션 없이 배경에서 해소 | 의지적 정지 사유 아님 — 계속 | 없음 (본 축이 채우는 공백) |
| **D-out-2 한도류·액션의존** | D 충족 ∧ remedy 실행이 **사용자·관리자 액션**(활성화·결제·cap 인상)에 의존 | 1회 통지 → 대기·중단 금지 → 제어 회복 시 계속 | ADR-025 §결정 6 whitelist #1(User environment 변경 의무 = 정당 통지) — 통지는 **보존**, "통지 후 무기한 대기"만 금지 |
| **D-out-3 한도류 아님 (확정된 부정)** | N-a 해당 **또는** D 3항 중 1+ 가 **명확히** 미충족 | 본 축 무개입 — 각 축 기존 소관 | ADR-057 §결정 4 · §결정 6(529 cooldown) · ADR-117 §결정 3 |
| **D-indeterminate 평가 불확정** | fast-path 미매칭 ∧ D 3항을 확정 평가할 수 없음(정보 부족·문면 모호) ∧ N-a 미해당 | **미분류** — remedy 라우팅 무개입(아래 배타 지배 인용), 의지적 정지 사유로도 삼지 않음 | `docs/orchestrator-playbook.md:528` / `ADR-057:149` — 미분류 → **failover 미발동 + task-failure 분류**(silent fallback 금지) |

**`시간 경과` 의 위치 (외연 겹침 해소)**: `시간 경과` 는 remedy **선택지**가 아니라 Orchestrator 액션 없이 흐르는 **배경 해소 사실**이다. 따라서 D-out-1 의 성립 조건에 배경 사실로 기술되며 D-out-2 의 "액션 의존" limb 과 겹치지 않는다("고른다"는 행위가 없으므로 remedy 선택 축에 등장하지 않는다).

**D-out-3 ⊥ D-indeterminate (disjoint 못박기)**: 전자는 "한도류가 아님"이 **확정**된 상태, 후자는 **판정 자체가 확정되지 않은** 상태다. 둘을 합치면 "모르는 것"이 "아니라고 확정된 것"으로 흘러 자동 처방이 붙는다 — 이 경계가 본 Amendment 가 여는 유일한 신규 상태이며, 그 상태의 remedy 라우팅은 위 표의 배타 지배 통제가 그대로 유지한다(본 Amendment 는 인용만 하고 개정하지 않는다).

### (f) negative control — 2 방향

- **(N-a) 한도류 자체가 아님 → D-out-3**: model-unavailable · floor 미달(버전 문제 — 시간·credits 로 해소 불가, D-iii 불충족) / `stop_reason: refusal`(D-ii 불충족) / 로직·입력·권한 오류(D-ii 불충족) / **컨텍스트 창 초과**(요청 형상 축 — D-i 불충족) / `529`·`overloaded`(별개 축 — §결정 6 cooldown) / **타 벤더 API 한도**(D-0 정의역 밖 — GitHub primary·secondary rate limit 등). (N-a) 가 있어야 판별식이 "모든 실패를 한도로 읽는" 반대 방향 오분류로 번지지 않는다.
- **(N-b) 한도류이나 자기해소 아님 → D-out-2 필수(D-out-1 금지)**: usage credits **미활성**/활성화 액션 필요(`Enable usage credits to continue using Claude` — support 11145838)가 유일한 공식 anchor 보유 사례. 구조 동형 후보(결제 수단 실패 · 구독 만료 · 조직 spend cap 도달 · **주간 한도**)는 `[미검증 — 구조 동형 후보, 공식 anchor 미확보]` 로 표기하며 제품 사실로 단정하지 않는다(ADR-119). 판정 기준은 문면이 아니라 **구조적 술어** — "remedy 실행 주체가 Orchestrator 인가, 사람인가". 사람이면 D-out-2.

### (g) 기록 규약 — 판정 신호 원문 verbatim 기록 금지 (§결정 10 확장)

§결정 10 redaction matrix 는 `error_message` 를 `verbatim (4-tuple enum match only, ...)` 로 규정한다. 판별식 D 로 분류된 신호는 정의상 **matched literal 이 부재**하므로 그 규정의 정의역 밖이며, 감사를 유지하려 원문 기록으로 흐르면 §결정 10 과 충돌한다. 본 Amendment 는 다음을 규약한다:

- **기록 허용 3요소**: ① 분류 결과(`D-out-1|D-out-2|D-out-3|D-indeterminate`) ② 판정 limb(어느 항이 성립/불성립인지) ③ 근거 요약 **1줄**(모델-클래스·자원 축의 추상 서술).
- **금지**: 신호 **원문 verbatim** / plan·model tier 문면(`Fable 5 limit` → "모델-클래스 한도 도달" 로 추상화) / credits 잔액·금액 / 결제·과금 식별자 / `org_id`·`account_id`(§결정 10 기존 금지 승계).
- **근거**: 본 규약이 늘리는 기록 트래픽의 착지면에는 **공개 표면**이 포함된다(§14 lane evidence → PR body 미러, `docs/kpi/*.jsonl` 커밋). 기존 deny-list regex 는 로컬 원장 경로에만 적용되므로 공개 착지면에는 redact 층이 부재하다 — 자동 redaction 층 신설 대신 **저작 규율**로 막고 그 한계를 (l) 에 정직 declare 한다.
- matched literal(6중 1)은 닫힌 값공간이라 기록 허용(Amendment 1 auditability 권고 무손상).

### (h) D-out-1 자기확증 반증 축

D-iii(회복 가능)는 **예측**이므로 반증 축이 없으면 D-out-1 이 무한 자기확증한다. 다음을 재판정 의무로 둔다: **동일 신호가 연속 2회 이상 D-out-1 로 판정됐는데 작업이 전진하지 않으면** 자기해소 가정이 반증된 것으로 보고 D-iii 불충족을 재평가한다(→ D-out-2 또는 D-out-3/D-indeterminate). `연속 2회` 임계는 **임의 선택**이다 — 반증 축의 *존재* 가 요구사항이고 값은 운영 관측으로 조정 가능하다(정직 declare).

### (i) §결정 5 축 한정 개정 — 재시도 중단 ⊥ 작업 중단

§결정 5 의 현행 문언은 다음과 같다 — **생략 없는 인용**(§결정 5 본문 전건 = intro 조건절 1 + bullet 3):

> `cascade_depth` 정의 = 단일 user request 안 retry sequence 의 nested cascade level. depth ≥ 2 (예: same-model 429 → Opus fallback → Opus 429 → 2차 retry burst) 시:
>
> - **자동 재시도 금지** (ADR-057 §결정 2 invariant verbatim 답습)
> - **user manual resume only** — `AskUserQuestion` escalation 또는 사용자 turn 대기
> - **`docs/kpi/429-incident-history.jsonl` `cascade_depth` field append-only event log** (ADR-106 운영 metric → PMOAgent input 회로 정합)

**보존(무변경)**: `cascade_depth` 정의 · depth ≥ 2 판정 · **자동 재시도 금지**(bounded retry 상한 = 비용 폭주·429 cascade 증폭 가드) · `AskUserQuestion` escalation 경로 · KPI append.

**축 분리(개정)**: `user manual resume only` 의 정의역은 **재시도(동일 호출 재발행) 축 한정**이다. 이 조항은 "그 시점 이후 Orchestrator 의 모든 작업 진행이 사용자 turn 을 기다려야 한다"는 뜻이 **아니다**. cascade 상한 소진 후에도 — ① 실패한 호출의 재발행은 금지되고 ② **남은 독립 작업으로의 전진은 계속**된다. "사용자 turn 대기"는 재시도 재개의 조건이지 작업 진행의 조건이 아니다.

**remedy 단조 비용 사다리 (예산 곱셈 차단)**: 한도 축이 미확정인 상태에서 유비용 remedy 를 순차로 여러 개 시도하면 예산이 곱해진다. 따라서 remedy 는 다음 사다리로만 진행한다:

| rung | 내용 | 비용 | 진입 조건 |
|---|---|---|---|
| R0 축 재판정 | fast-path → 판별식 D → 4치 출력 | 0 | 항상 첫 단계 |
| **R1 전진(forward)** | 실패 호출을 재발행하지 않고 **남은 독립 작업**으로 진행 | 0 | 항상 |
| R2 1회 통지 | remedy 주체가 사람이면 whitelist #1 통지 1회 후 R1 복귀 | 0 | D-out-2 |
| R3 canonical remedy | 축이 **확정된 경우에만** 그 축 고유 remedy **정확히 1종** | 유비용 (기존 상한 내) | 축 확정 ∧ 해당 축에 remedy 실재 |
| R4 낙하 | R3 실패 시 두 번째 유비용 remedy 로 가지 **않고** R0→R1/R2 로 낙하 | 0 | R3 소진 |

- **I-1 예산 곱셈 차단**: 유비용 rung(R3) 진입은 **축 확정이 전제조건**이다. 축이 확정되면 remedy 는 1종으로 결정되므로 "여러 개 시도"가 구조적으로 불가하고, 미확정(D-indeterminate)이면 R3 자체가 닫힌다(위 (e) 배타 지배 통제).
- **I-2 전진 ≠ 재시도**: 재시도 counter 는 **동일 호출 재발행**을 센다. R1 전진은 다른 작업이므로 backoff·cascade·per-spawn 어느 counter 도 증가시키지 않는다. 본 Amendment 는 **어떤 경로에도 신규 재시도 예산을 추가하지 않는다**(신규 counter 0).
- 무변경 확인: §결정 2 backoff max 6/60s/≤75s · Retry-After override · §결정 3 sequential composition · §결정 4 CB 3-window · §결정 6 529 cooldown · ADR-141 Amendment 6 per-spawn 1회 · 미분류 재spawn 0 · Amendment 7 cap-down.

### (j) 정직 천장 (over-claim 금지)

1. **D 는 모델 판정이다** — 기계 검증 표면이 없다. fast-path 만 기계적이고 D-0·D-i~D-iii·4치 라우팅은 prompt-mandate(advisory)다. "판별식 도입 = 감지 100%" 주장 금지.
2. 본 Amendment 는 **비의지적 종료를 0 으로 만들지 않는다** — 한도 순간 토큰 발화 불가 구간·in-flight 즉사는 정의역 밖(OOS)이다.
3. 감지 미탐(D 미충족 낙하)의 안전 방향 = **failover 미발동**(현행 동작 degrade) 유지 — fail-open bounded, 회귀 0.
4. (g) 기록 규약은 **저작 규율**이며 공개 착지면의 자동 redaction 층이 아니다. 규율 미준수 시 유출 가능성은 잔존한다(수용 리스크, 명시 declare).

### Cross-ref

- §결정 1 / Amendment 1 (b) — 감지집합 code-fence(**byte 무변경 · cross-ref only**). 본 Amendment 는 그 열거의 *지위* 만 재해석한다.
- §결정 5 — (i) 축 한정 개정 대상. §결정 2/3/4/6 = 무변경.
- §결정 10 — (g) redaction matrix 확장(비-enum 신호 기록 규약).
- [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 6 A6-3(a) / Amendment 8 — Orchestrator 세션 축 재개봉(본 Amendment 는 감지·재시도 축, Amendment 8 은 행위 규범 축).
- [ADR-025](ADR-025-stop-discipline-non-whitelist-as-defect.md) Amendment 4 — 한도류 신호 발 의지적 정지의 stop-discipline 착지(본 Amendment = 판정, ADR-025 = 정지 적법성). **§A4-8 = 본 carrier 저작물 전체의 자기적용 결박 총칙** — 판정문 verbatim SSOT 1곳, 본 Amendment 는 pointer 만 둔다. 본 Amendment 의 문면 축 술어((i) full-block 인용 규율 · (j) 천장 서술)도 그 dry-run 대상이며 결과는 Story `CFP-2944` §7.16 에 기록된다(런타임 축 술어 — D-0 · 판별식 D · remedy 사다리 — 는 정의역이 신호·행동이라 문면 자기적용 대상이 아니다).
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) §결정 4 / `docs/orchestrator-playbook.md:528` — 미분류 remedy 라우팅 **배타 지배**(인용만, 개정 0).
- [ADR-119](ADR-119-research-before-claims.md) — 외부 제품 사실 인용 규율(공식 anchor 미확보 항목의 `[미검증]` 표기).

## Amendment 3 (CFP-2984 — dead tenant 참조 정정 + 대기원 헤더 의미 정정 + dangling 청산 + CB telemetry-gated 재선언 + declaration-only 처분 + backoff single-SSOT)

**날짜**: 2026-08-15 KST · **carrier**: CFP-2984 · **status**: Proposed (Phase 1 draft) · **방향**: **강화**(죽은 참조 제거 · 오독 유발 문면 정정 · hollow gate 위장 차단 · over-claim 축소, 약화 0).

### A3-0. 정의역 — Amendment 2 무접촉 (비협상)

**Amendment 2(`## Amendment 2` 절 전체) 는 본 Amendment 의 정의역 밖이다.** Amendment 2 는 `status: Proposed` 이고 CFP-2944 소유이며, Proposed 조항 위에 normative 를 쌓으면 (a) 착지 실패 시 본 조항이 참조 대상 부재로 born-stale 이 되고 (b) 타 Story 소유 구조를 개변하게 된다. 본 Amendment 는 그 절 안의 **바이트를 하나도 바꾸지 않는다**.

- **본 Amendment 가 Amendment 2 에 요구하는 변경 = 0건.** Amendment 2 착지 여부와 무관하게 본 Amendment 는 완전하게 성립한다.
- **절 경계 note (정직)**: 본 Amendment 를 파일 말미에 append 함으로써 Amendment 2 의 **암묵 종단자가 EOF 에서 `## Amendment 3` heading 으로 바뀐다**. Amendment 2 는 자기 절 경계를 EOF 로 정의하는 조항을 두지 않으므로 규범 영향은 없으나, 절 경계를 파일 끝에 결박해 읽는 도구가 있다면 이 사실이 입력이다.
- **금지 확인**: Amendment 2 흡수·재정의·착지 0 / Amendment 2 문면 인라인 복제 0 / Amendment 2 고유 식별자(판별식·출력값·rung 번호)를 본 Amendment normative 문면에 사용 0.

### A3-1. dead tenant 참조 정정 — 실행분과 **보류분**

결함 class 는 "못 봤다" 가 아니다. `:54`(frontmatter amendment 1 scope) 와 §결정 3 하단 re-tenant note 는 step2 slot 이 dead tenant 를 cross-ref 한다는 사실을 **이미 기록**하고 있었다. 그 자기 인식이 **규범 본문에 전파되지 않은 것**이 결함이다.

**정정 실행 (7행)**

| 파일 | 위치 | 조치 |
|---|---|---|
| 본 ADR | §컨텍스트 인접 ADR 열거 | tenant 교체 + prior dead-mark 인접 보존 |
| 본 ADR | §결정 1 Single SSOT consumer 열거 | 동상 |
| 본 ADR | §결정 3 step 2 | 동상 + **slot ordinal frozen 규범 신설** |
| 본 ADR | §결정 3 step 4 | invariant 정박 대상을 §결정 5 자신 + ADR-141 A6-4 로 교체 |
| 본 ADR | §결정 3 하단 invariant 보존 cross-ref | 동상 + ADR-057 §결정 4/6 배타 지배 **유효** 명시 |
| 본 ADR | §결과 > 긍정 | 동상 |
| `skills/rate-limit-429-mitigation/SKILL.md` | 사다리 attempt 2 rung | 동상 (slot ordinal 무변경) |

**정정 보류 3행 (★ 판정 C 와 (A) 분류가 직접 충돌하는 지점 — 발견 사항)**

원 분류는 정정 대상을 10행으로 셌으나, 그중 **3행은 정정하면 다른 것이 깨진다**:

| 위치 | 보류 사유 |
|---|---|
| 본 ADR §결정 5 첫 bullet ("자동 재시도 금지 (ADR-057 §결정 2 invariant verbatim 답습)") | Amendment 2 (i) 가 이 bullet 을 **"생략 없는 인용"** 으로 verbatim 인용하고 있고, 같은 절이 그 bullet 을 **"보존(무변경)"** 으로 declare 한다. 원본을 고치면 그 인용이 stale 이 되는데 **인용면은 Amendment 2 소속이라 판정 C 로 수정 불가**하다. 즉 원본과 인용을 동시에 맞출 수 있는 편집이 존재하지 않는다 → **원본 보존이 유일한 무결 선택** |
| Amendment 2 (i) 안의 위 인용 블록 | 정의역 밖(A3-0) + 인용 메타면(폐기·개정 대상 문언을 기록하는 면은 verbatim 보존이 의무) |
| `skills/rate-limit-429-mitigation/SKILL.md` cascade bullet ("자동 재시도 금지 …") | 위 §결정 5 bullet 의 **mirror** — SSOT 와 함께 이동해야 하므로 SSOT 가 보류인 동안 mirror 도 보류. 부수 사실: 해당 위치는 미머지 인접 브랜치가 바로 다음 줄을 수정 중이라 접촉 시 hunk 충돌을 만든다 |

- **보류의 실 손실**: 위 3행은 `Superseded` 문서의 §결정을 invariant 근거로 계속 인용한다. 다만 인용된 명제("자동 재시도 금지") **자체는 살아 있고**, 본 §결정 5 와 ADR-141 A6-4 가 독립적으로 같은 invariant 를 보유하므로 **행동 영향은 0** 이다. 끊긴 것은 귀속(attribution)이지 규범이 아니다.
- **해소 경로**: Amendment 2 착지 후, 그 소유 Story 가 인용 블록과 원본을 **같은 커밋에서** 동기 정정하는 것이 유일한 무결 경로다. 본 Amendment 는 그 의무를 상대에게 요구하지 않고 **여기 기록만** 한다.

### A3-2. 주간 한도 anchor — **부분 보강 (태그 해소 아님)**

세션 진행 중 주간 한도 도달이 firsthand 관측됐다(제품 표면 문자열 실관측 — carrier Story §9.2 dogfood datapoint). 이는 "주간 한도" 가 실재 제품 상태임을 보이는 **제품표면 anchor** 다.

- **그러나 `[미검증 — 구조 동형 후보, 공식 anchor 미확보]` 표기는 해소되지 않는다.** 그 표기가 요구하는 것은 **공식 문서 anchor**(벤더 문서·support article)이고, 세션 관측 문자열은 그 등급이 아니다. 등급이 다른 증거로 태그를 지우면 ADR-119 위반이다.
- **또한 그 표기 자체가 Amendment 2 (f) 소속**이라 본 Amendment 가 문면을 고칠 수 없다(A3-0).
- ⇒ 본 항은 **관측 사실의 기록**이며, 태그 해소는 공식 anchor 확보 후 Amendment 2 소유 Story 소관이다. **부분 보강으로만 계상**한다.

### A3-3. declaration-only 3종 처분

| action | 처분 | 근거 |
|---|---|---|
| `429-retry-evidence-presence` | **승격 후보 유지 (1종)** | §결정 8.1 marker regex 라는 구체 정본이 실재하고, marker 제거가 discriminating mutant 로 성립한다. 승격 실행 = Phase 2, **discriminating mutant 실증 동반 의무**, warning-first 로 태어난다 |
| `debate-parallel-cap-check` | **승격 기각** | 대상 field `parallel_spawn_cap` 이 `templates/team-spec-*.yaml` **7 file 전건**에 실재(3-field/파일 실측) → presence 검사가 **구조적 항상-GREEN** = always-green hollow |
| `deputy-stagger-check` | **승격 기각** | 대상 field `spawn_stagger_ms` 동일 사유 |

- **부수 실측 (정직 기록)**: 세 field(`parallel_spawn_cap` · `spawn_stagger_ms` · `cascade_circuit_breaker`) 를 **파싱·소비하는 실행 코드는 repo 내 0건**이다(정의역 = git-tracked `*.py *.sh *.js *.ts *.yml *.bats *.json *.toml`, 매칭 파일 0). 선언면과 산문 인용면만 존재한다. 런타임에서 모델이 yaml 을 prompt-level 로 읽는 행위는 이 정적 grep 의 정의역 **밖**이며 **확인 불가**다 — "소비자 0" 을 기계 소비자 축으로만 한정해 읽을 것.
- 기각 2종은 **삭제하지 않고 frontmatter 주석으로 보존**한다 — 발의 이력과 기각 사유를 같은 자리에 남겨야 재발의자가 이 근거를 반증하고 들어올 수 있다.

### A3-4. 정직 천장

1. 본 Amendment 는 **참조 대상과 선언 지위만** 정정한다 — §결정 2 backoff 수치 · §결정 4 threshold 수치 · §결정 3 slot ordinal · §결정 1 detection literal 전건 **무변경**(closed-set invariant 미발동).
2. **CB telemetry-gated 재선언은 breaker 를 고치지 않는다.** 데이터원을 채우는 것은 본 Amendment scope 밖이며, 선언은 "지금 발동 불가" 라는 사실의 가시화일 뿐이다. 이 선언으로 게이트가 작동하게 됐다고 읽으면 안 된다.
3. **backoff single-SSOT 는 문면 규율이지 기계 강제가 아니다.** 사본의 수치 재기재를 막는 lint 는 Phase 2 이며, 그 lint 도 리터럴 스캔 층에서는 우회 가능하다 — "수치 복제가 봉인된다" 주장 금지.
4. **A3-1 보류 3행은 미해소 잔여다.** "10행 전부 정정했다" 로 계상하지 말 것 — 실행 7 / 보류 3 이 정확한 회계다.

### Cross-ref

- §결정 2 / §결정 3 / §결정 4 / §결정 8.1 / §결과 — 본 Amendment 의 개정 대상.
- §결정 5 — **무접촉 보존**(A3-1 보류 사유). §결정 1 detection closed-set — 무접촉(literal 무증감).
- `## Amendment 2` — **무접촉**(A3-0). 본 Amendment 는 그 조항에 normative 의존 0.
- [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 6 — §결정 3 step2 slot 의 현 tenant. **Amendment 10**(CFP-2984 동반) = 그 failover 경로의 salvage 인계.
- [ADR-179](ADR-179-agent-salvage-bundle-handoff.md) — remedy 발동 후 회수 판정 축(본 ADR = 감지·재시도 축, disjoint). §결정 7 skill body 3-step 이 ADR-179 §결정 7 의 산출 고정 착지면이다.
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — `Superseded`(by ADR-141). §결정 2 = moot/dead(본 Amendment 정정 대상) / **§결정 4 · §결정 6 = 유효**(미분류 remedy 라우팅 배타 지배 — 정정 대상 아님, 치환 시 라우팅 단절).
- [ADR-171](ADR-171-evidence-enforceable-promotion-framework.md) §결정 5·6 — declaration-only 승격은 warning-first + evidence-gate.
- [ADR-119](ADR-119-research-before-claims.md) — A3-2 태그 비해소 근거(증거 등급 불일치 시 abstention 유지).


## Amendment 4 (CFP-2967 — §결정 4 telemetry 실채움 인계 수취·종결 + §결정 8.2 write ownership 확정 + OR-1 하한 declare + 기록 어휘/감지 어휘 분리 + retention 정의역 한정)

**날짜**: 2026-08-19 KST · **carrier**: CFP-2967 · **status**: Proposed (Phase 1 draft) · **방향**: **강화**(단독 writer 확정 · 자동 무장 금지 · 계수 하한 성격 declare · 어휘 분리, 약화 0).

### A4-0. 정의역 — Amendment 2 무접촉 (비협상)

**`## Amendment 2` 절 전체는 본 Amendment 의 정의역 밖이다.** 그 절은 `status: Proposed` 이고 CFP-2944 소유이며, Proposed 조항 위에 normative 를 쌓으면 (a) 착지 실패 시 본 조항이 참조 대상 부재로 born-stale 이 되고 (b) 타 Story 소유 구조를 개변하게 된다. 본 Amendment 는 그 절 안의 **바이트를 하나도 바꾸지 않는다** (Amendment 3 A3-0 규율 승계).

- **본 Amendment 가 Amendment 2 에 요구하는 변경 = 0건.** 착지 여부와 무관하게 본 Amendment 는 완전하게 성립한다.
- **절 경계 note (정직)**: 본 Amendment 를 파일 말미에 append 함으로써 **Amendment 3 의 암묵 종단자가 EOF 에서 `## Amendment 4` heading 으로 바뀐다**. Amendment 3 은 자기 절 경계를 EOF 로 정의하는 조항을 두지 않으므로 규범 영향은 없으나, 절 경계를 파일 끝에 결박해 읽는 도구가 있다면 이 사실이 입력이다.
- **금지 확인**: Amendment 2 흡수·재정의·착지 0 / 문면 인라인 복제 0 / 고유 식별자(판별식 D·출력 4치·rung 번호)를 본 Amendment normative 문면에 사용 0.

### A4-1. §결정 4 — telemetry 실채움 인계 **수취·종결** (단 breaker 자동 무장은 금지)

Amendment 3 (4) 는 §결정 4 circuit breaker 를 "telemetry 실채움 전까지 **미발동(non-firing)**" 으로 재선언하면서, 그 실채움을 명시적으로 인계했다 — 본 ADR §결정 4 verbatim: "**telemetry 실채움 = 본 Amendment scope 밖**(계측 채널 실채움은 병렬 Story 소관). 본 Amendment 는 미발동 사실의 **declare 까지만** 한다."

**CFP-2967 축 ① 이 그 인계의 수취인이다.** 신규 producer 를 `StopFailure` 훅(matcher `rate_limit`)으로 등록해 per-incident 행을 `docs/kpi/429-incident-history.jsonl` 에 기계 append 하고, 집계기가 그것을 읽어 `docs/kpi/429-incident.json` 을 write 한다. Amendment 3 이 지목한 "기계 append 경로 0건" 은 이로써 닫힌다(착지 = Phase 2).

**★ 그러나 수취되는 것은 데이터원뿐이며, breaker 는 자동으로 무장되지 않는다 (U-2 사용자 확정).**

- **§결정 4 3-window threshold 는 데이터가 채워져도 미발동을 유지한다.** 임계 재보정(`[hypothesis]` 태그 해소)은 **별건**이며 본 Story 정의역 밖이다.
- 근거: 그 threshold 3종은 자기 문면이 `[hypothesis] baseline 추정` 이고 "post-deploy actual incident rate 측정 후 사용자 확인" 을 조건으로 건다. **데이터원이 채워지는 순간은 그 측정의 시작점이지 완료점이 아니다.** 근거 없는 상수를 데이터 존재만으로 무장시키는 것은 ADR-068 I-5 dimensional empirical grounding 위반이며, 하필 첫 무장이 잘못된 임계로 일어나면 그 오작동은 **작업 전면 봉쇄**(fail-closed) 형태로 나타난다 — 관측 채널을 켠 대가로 가용성을 잃는 교환이다.
- ⇒ **Amendment 3 의 미발동 선언은 본 Amendment 착지 후에도 유효하다.** 바뀌는 것은 미발동의 **사유**뿐이다: 종전 *"데이터원 부재"* → 이후 *"임계 미검증(measurement pending)"*. 본 절을 "telemetry 가 채워졌으니 breaker 가 살아났다" 로 읽으면 정확히 반대다.

**인계 항목별 정확한 회계 (종결/미종결 분리)**

| 인계 항목 (Amendment 3 지목) | 처분 |
|---|---|
| 기계 append 경로 0건 | **종결** — 축 ① producer 가 닫는다 (규범 확정 = 본 Amendment / 실착지 = Phase 2) |
| breaker 가 구조적으로 open 될 수 없음 | **미종결 · 의도적 유지** — U-2. 구조적 불가에서 **정책적 미발동**으로 성격만 전환된다 |
| intensity 상시 `0` 낙하 (동일 데이터원 공유 표면) | **부분 종결** — 데이터가 흐르면 `0` 낙하는 해소되나, 부재·신선도 축의 판정 형상은 축 ① 설계 소관이며 본 Amendment 는 그 결과를 단정하지 않는다 |

### A4-2. §결정 8.2 — producer/aggregator write ownership 확정 (현행 위반 3종 적시·처분)

**신설 규범 (단독 writer 확정)**

| tier | 파일 | 단독 writer | 접근 규약 |
|---|---|---|---|
| event | `docs/kpi/429-incident-history.jsonl` | **producer** | append-only. **kernel-atomic append**(POSIX `O_APPEND` 단일 write / Windows `FILE_APPEND_DATA`). **read-modify-write 금지** |
| aggregate | `docs/kpi/429-incident.json` | **집계기** | 전체 재작성 허용(단독 소유) |

- **집계기의 event tier 접근 = read-only 강등.** 집계기는 event log 에 **어떤 바이트도 쓰지 않는다.**
- read-modify-write 금지의 근거는 이 repo 자신의 봉인이다 — `scripts/lib/append_spawn_event.py` 가 형제 구현을 이름으로 지목해 **복사 금지**를 선언하고(`append_stop_event.py _atomic_append` = lost-update bug: whole-file read + `os.replace` 는 rename 만 원자적이고 read-modify-write 전체는 아니다) 대체 primitive 를 제공한다. 본 채널의 표적 시나리오가 **다수 서브에이전트 동시 429 버스트**라 동시 append 는 예외가 아니라 **모달 케이스**이며, lost-update 는 사건이 가장 몰릴 때 계수를 깎아 완화 기제를 굶기는 방향으로 정확히 틀린다.

**현행 위반 3종** — firsthand, base `7a12d0a0f`. 수치·좌표가 아니라 **재현 명령**을 정본으로 둔다:

| # | 위반 | 재현 (`scripts/lib/measure_429_incident.py`) | 처분 |
|---|---|---|---|
| **V-1** | 집계기가 **주간 요약행을 event log 에 write** 한다. 그 행의 키 집합 `{week, measured_at, weekly_incident_count, cascade_incidents, max_cascade_depth, gate_status}` 은 per-incident 스키마 `{timestamp, lane, agent_role, retry_count, final_status, cascade_depth, error_pattern}` 과 **공유 키 0개** — 한 파일에 해상도가 다른 두 레코드형이 섞인다 | `grep -n "current_entry = {" ` 로 요약행 구성 지점 ∧ `grep -n "429-incident-history.jsonl"` 로 기록 대상 확인(`history_file` 기본값) | **제거** — 요약행은 aggregate tier 로 이동 |
| **V-2** | 동주 요약행 **`history_lines.pop()`** — 마지막 줄만 보고 같은 주면 삭제 | `grep -n "history_lines.pop()"` | **제거** — append-only 계약 위반이자 **행 순서 가정 의존**. per-incident 행이 요약행 뒤에 붙으면 pop 이 빗나가 같은 주 요약행이 **중복 누적**된다 |
| **V-3** | **`fp.seek(0)` → `fp.truncate()`** 로 파일 전체 재작성 | `grep -n "fp.truncate()"` | **제거** — append-only 파일의 truncate 는 이력 파괴 경로다 |

**★ 정직 정정 (과장 차단)**: "집계기가 truncate 로 파괴한 이력이 실재한다" 는 **과장**이다 — `docs/kpi/429-incident.json` 의 `measured_at` 이 `null` 이고 해당 파일 git 이력 전건이 feature 커밋이므로 **집계기는 이 파일에 한 번도 실행된 적이 없다**. 파괴는 **경로만 실재하고 미발생**이다. 이 정정은 위험을 낮추지 않는다 — 배선되는 순간이 **첫 실행이자 첫 파괴**이므로 born-broken 판정을 오히려 **강화**한다.

**소유권 분리가 닫는 것 (부수 — "고친다" 가 아니라 "발생 기제를 없앤다")**

- **producer append ↔ 집계기 truncate 레이스** — 집계기가 read 한 뒤 truncate 하기 전 producer 가 append 하면 그 행이 소실된다. 순차 fixture 로는 잡히지 않는 경합이며, 집계기가 event tier 를 쓰지 않으면 정의역에서 사라진다.
- **동주 중복 집계** — V-2 의 귀결. 요약행이 event tier 에 없으면 발생 불가.
- **행 순서 의존** — 판독자가 "마지막 줄" 에 의존하는 구조가 제거된다. 이것은 부수 효과 이상이다: `docs/kpi/*.jsonl` 에 `merge=union` 을 검토할 수 있게 만드는 **전제조건**이다(현행은 전제 미충족이라 검토 자체가 불가). `.gitattributes` 에 `merge=` 속성이 0건이라 병렬 브랜치 append 가 말단행에서 매번 충돌하는 현행 문제의 해소 경로이나, **본 Amendment 는 `merge=union` 을 채택하지 않는다** — 채택은 read-time dedup 실재를 두 번째 전제로 요구하며 그 판정은 별건이다 `[source: git-scm.com/docs/gitattributes — union 은 추가된 줄을 임의 순서로 남기며 "Do not use this if you do not understand the implications."]`.

**가산항 분리 노출 (aggregate tier 규약)**: `429-incident.json` 은 `marker_incident_count`(§결정 8.1 §14 Lane Evidence 마커 유래) · `event_incident_count`(event tier 유래) · 합 `weekly_incident_count` 를 **따로** 둔다. 훗날 두 모집단이 겹치기 시작해도 합 안에 조용히 흡수되지 않고 **보인다**. 두 모집단의 합집합은 **해상도가 호환되는 유일 지점인 주간 집계에서만** 일어난다 — §14 마커에는 timestamp 가 없어 30분 window 에 **원리적으로 기여 불가**하므로 event tier 에서의 합집합은 애초에 성립하지 않는다.

### A4-3. OR-1 — 본 채널의 429 계수는 항상 **하한**이다 (잔여 declare)

> **OR-1**: 본 채널이 산출하는 429 계수는 **항상 하한(lower bound)이며 상한이 아니다. 낮은 intensity bucket 을 "부하가 낮다" 의 증거로 사용하는 것을 금지한다.**

- **근거**: producer 는 훅이고 훅은 timeout 시 fail-open 으로 낙하한다(해당 사건 미기록). 만료 확률은 호스트 부하와 함께 오르므로 **유실은 정확히 고부하 구간에 집중**된다.
- **전손과 부분 유실의 비대칭**: 채널이 전면 정지하면 신선도 축이 그것을 잡아 보수 fallback 으로 낙하시킨다 — 즉 **전손은 안전 방향으로 민다**. 그러나 **부분 유실은 신선도를 정상으로 유지한 채 계수만 낮춰** bucket 을 과소 산출하며, 이 구간에는 대응하는 안전장치가 없다.
- **"완화 불가" 가 아니다 (과대 declare 금지)**: 시스템 수준 완화는 실재한다 — 훅 예산 헤드룸 / producer 자기부하 제거 / 소비측 낙하 방향 반전. OR-1 이 declare 하는 것은 이 완화들이 **닫지 못하는 부분 유실 구간의 편향 방향**이지 "아무 완화도 없다" 가 아니다.
- **편향 크기는 미측정**이며 그 측정 채널 신설은 본 Story 범위 밖이다 — 방향만 확정이다.

### A4-4. 기록 어휘 ≠ 감지 어휘 (§결정 1 closed-set invariant **미발동** 명시)

`StopFailure` 훅의 matcher 는 error type 을 필터하며 그 값 예시에 **`rate_limit`(언더스코어)** 이 포함된다 `[source: code.claude.com/docs/en/hooks — 직접 WebFetch 2026-08-19: `rate_limit` · `overloaded` · `authentication_failed` · `billing_error` · `server_error` 등 열거]`. 이 토큰은 §결정 1 감지집합(+ Amendment 1 확장)의 **어느 literal 과도 다른 값공간**이다.

**분리 규범 (본 Amendment 신설)**

| 어휘 | 값공간 SSOT | 무엇을 정하는가 |
|---|---|---|
| **감지 어휘** (detection vocabulary) | 본 ADR §결정 1 closed-set (+ Amendment 1) | 무엇을 429/한도류로 **판정할 것인가** |
| **기록 어휘** (record vocabulary) | ADR-043 Amendment 7 (B) `error_pattern` 값공간 | 무엇을 event log 에 **적을 것인가** |

- 두 값공간은 **disjoint 한 목적**을 가지며 서로의 원소를 상속하지 않는다.
- ⇒ **`error_pattern` 값공간에 `rate_limit` 이 들어가는 것은 §결정 1 감지집합에 원소를 추가하지 않는다.** 따라서 **§결정 1 closed-set invariant("5번째 pattern 추가 = 본 ADR Amendment 의무")는 본 Amendment 에서 미발동**이며, detection literal 은 **무증감**이다.
- **분리를 명시하지 않으면 두 오작동이 발생한다**: (a) 누군가 `rate_limit` 을 5번째 감지 literal 로 오해해 추가하고 closed-set invariant 를 건드린다 — 감지집합은 판정 정의역이라 원소 추가가 오탐을 낳는다 (b) producer 가 감지 literal 과 매칭을 맞추려 **원시 에러 텍스트**를 기록해 §결정 10 redaction matrix 와 ADR-043 Amendment 7 (B)(`error_pattern` = 폐쇄 enum only)를 **동시에** 위반한다. **(b) 는 공개 착지면과 직결되므로 P0** 다.
- **★ 명칭 불일치 실측 — 미해소 잔여 declare (본 Amendment 는 matrix 행을 고치지 않는다)**: §결정 10 redaction matrix 는 **`error_message`** 를 `verbatim (4-tuple enum match only, no user prompt verbatim)` 로 규정하는데, event tier 실 스키마의 필드명은 **`error_pattern`** 이다 (`docs/kpi/429-incident-history.jsonl:3` 자기 헤더 verbatim: `# Schema: {timestamp, lane, agent_role, retry_count, final_status, cascade_depth, error_pattern}`) — **matrix 가 명명하는 필드와 스키마가 명명하는 필드가 다르다.** 이 불일치는 "matrix 에 `error_message = verbatim` 이 있으니 에러 원문을 적어도 된다" 는 오독 경로를 연다.
  - **본 Amendment 의 판정**: 그 matrix 행은 본 채널 `error_pattern` 에 대한 **원문 기록 허가가 아니다.** 본 채널의 기록 어휘 SSOT 는 ADR-043 Amendment 7 (B)(폐쇄 enum only)이며 위 (b) 금지가 우선한다.
  - **matrix 행 자체의 명칭 정정은 본 Amendment 가 수행하지 않는다.** ⇒ **미해소 잔여**이며 정정은 별건이다.
    - **★ 이월 사유 정정 (설계리뷰 1회차 F-5 · P2)**: 초판은 사유를 "타 표면을 조사하지 않았다" 로 적었으나 그것은 **거짓**이다 — 조사는 수행됐고(1 grep) 답도 나와 있다. 재현: `grep -rn "error_message" --include=*.md --include=*.py --include=*.yaml --include=*.yml --include=*.sh .` → 본 ADR 자신을 제외한 **교차 소비 표면 = `ADR-179-agent-salvage-bundle-handoff.md:137` 단 1건** (`scripts/lib/**.py` 히트는 무관한 지역 변수·docstring 이라 본 matrix 행의 소비자가 아니다 — **계수 축 명시 (설계리뷰 2회차 P2-2)**: 위 `grep -rn` 은 **행** 단위 출력이라 `scripts/lib` 하위 히트는 **6 행 / 4 파일** 이다. 초판이 적은 "4건" 은 파일 수 축으로는 참, 병기 명령의 출력 축(행)으로는 거짓이었다. 축을 재현 명령에 맞춰 고정한다 — 행 수 = `grep -rn "error_message" scripts/lib --include=*.py | wc -l`, 파일 수 = 같은 명령의 `-rln` 판. 어느 축이든 본 판정(교차 소비 표면 1건)은 무영향). **그 실측 결과는 이월을 약화시키는 게 아니라 더 강하게 정당화한다** — ADR-179:137 이 이 행을 **이름으로**("§결정 10 `error_message` 행의 no user prompt verbatim 상속") 인용하므로, matrix 행을 `error_pattern` 으로 rename 하면 그 인용이 **가리킬 대상을 잃는다**. 즉 정정은 ADR-179 동반 수정을 요구하는 cross-ADR 작업이며 본 Amendment 의 정의역 밖이다. ⇒ **정정된 사유 = 미조사가 아니라 cross-ADR 파급이 실측으로 확인됨.** 그때까지 오독 차단은 본 판정 문면이 담당하고, 본 절을 근거로 "matrix 가 정합해졌다" 고 읽으면 over-claim 이다.
- **부수 (구현 함정)**: 현행 문자열 가드 `_SAFE_STR_RE = ^[0-9A-Za-z_\-:\.]{0,128}$` 는 공백을 허용하지 않아 §결정 1 literal 중 공백을 포함하는 값이 그대로는 통과하지 못한다. 해결은 **화이트리스트에 공백을 추가하는 것이 아니라 값을 토큰화하는 것**이다 — 기록 어휘가 폐쇄 enum 인 이상 토큰이 정본이고 원문은 애초에 기록 대상이 아니다. 이 함정을 화이트리스트 완화로 풀면 (b) 경로가 열린다.

### A4-5. §결정 10 90일 retention ↔ event tier 보존 요구 — 정의역 한정

§결정 10 Retention 은 "**90일 raw event JSONL** + 영구 weekly aggregate JSON" 을 규정한다. 한편 본 Story 는 event tier 에 "집계기 실행 후 선행 행이 전건 보존된다" 는 요구를 둔다. 두 규범을 **무조건**으로 읽으면 자기모순이다 — 90일 회전이 곧 선행 행 삭제이므로.

- **정의역 한정**: 그 보존 요구의 정의역은 **집계기 실행 경로**다. 규범 내용은 "집계기는 event tier 에서 어떤 행도 제거하지 않는다" 이며, **명시적 age-bounded 회전 actor(90일 retention 이행 주체)는 그 정의역 밖**이다. 그 actor 의 삭제는 위반이 아니다.
- **두 규범은 층이 다르다** — 하나는 *누가 쓸 수 있는가*(ownership), 다른 하나는 *얼마나 오래 남는가*(retention). 층이 다르므로 충돌이 아니라 병존이다.
- **양방향 오독 차단**: 회전 actor 는 **아직 존재하지 않는다**(본 Story 가 신설하지 않는다). 존재하지 않는 actor 를 근거로 보존 요구를 약화하지 말 것이며, 반대로 보존 요구를 근거로 §결정 10 retention 조항을 무효화하지도 말 것.

### A4-6. 정직 천장

1. 본 Amendment 는 **규범 확정**이며, producer 신설·집계기 read-only 강등을 실현하는 코드 변경은 전건 **Phase 2**(carrier = `mclayer/plugin-codeforge#2967`). **그 사이 구간에서 본 Amendment 의 강제력은 0 이며 이는 선언이다.**
2. **V-1 / V-2 / V-3 은 "고쳤다" 가 아니라 "위반으로 판정하고 처분을 규정했다" 이다.** 코드는 아직 그대로다 — 본 절을 근거로 "집계기가 read-only 가 됐다" 고 읽으면 over-claim 이다.
3. **breaker 는 여전히 미발동이다**(A4-1 / U-2). 데이터가 흐르기 시작해도 §결정 4 는 발동하지 않는다.
4. **OR-1 의 편향 크기는 미측정이다.** 확정된 것은 **방향**(하한)뿐이며, 그 하한이 실제 값과 얼마나 벌어지는지는 모른다 — 방향 확정을 크기 확정으로 승격시키지 말 것. 훅 만료 확률의 절대값 역시 미측정이다.
5. **`## Amendment 2` 절 무접촉**(A4-0). 본 Amendment 가 그 절에 요구하는 변경은 0건이며, 그 절의 착지 여부와 무관하게 본 Amendment 는 완전 성립한다.
6. **`mechanical_enforcement_actions` 무증감** — 본 Amendment 는 기계 강제 action 을 신설하지 않는다. Amendment 3 이 남긴 승격 후보 1종·기각 2종 주석은 무접촉이며, 본 Amendment 의 규범(단독 writer·어휘 분리)에 대응하는 기계검사의 설계·착지는 Phase 2 소관이다.

### Cross-ref

- **§결정 4** / **§결정 8.2** / **§결정 10** — 본 Amendment 의 개정 대상.
- **§결정 1** detection closed-set — **무접촉**(literal 무증감, A4-4).
- **§결정 5** / **§결정 9** — 무변경. 429 marker 의 **§14 only** 배타 유지 ∧ 본 Amendment 의 event tier 는 §10 FIX Ledger 와 여전히 disjoint(ADR-067 RESET contamination 차단 무손상).
- **`## Amendment 2`** — **무접촉**(A4-0). 본 Amendment 는 그 조항에 normative 의존 0.
- [ADR-043](ADR-043-codeforge-telemetry-privacy-policy.md) **Amendment 7** — sibling. 본 채널의 **privacy·공표 경계·allow-list 7 필드·bound (2')** 는 그쪽 소유이고, 본 Amendment 는 **운영·write ownership·인계 수취·기록 어휘** 소유(disjoint). `error_pattern` 은 두 문면이 만나는 유일 지점이며 값공간 SSOT = ADR-043 Amendment 7 (B), 값공간이 §결정 1 과 disjoint 라는 판정 = 본 A4-4.
- [ADR-068](ADR-068-boundary-completeness-invariants.md) I-5 — A4-1 U-2 의 근거(dimensional empirical grounding — 근거 없는 상수 무장 금지).
- [ADR-179](ADR-179-agent-salvage-bundle-handoff.md) — remedy 발동 후 회수 판정 축(본 ADR = 감지·재시도·계측 축, disjoint).
