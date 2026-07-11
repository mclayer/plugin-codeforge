---
adr_number: 148
title: G2 지속-liveness soak 게이트 — 2-표면(선언 fail-closed ⊥ 런타임 soak)·3-layer·verdict-kernel seam + 정직 천장(CrashLoopBackOff 근절)
status: Accepted
category: governance
date: 2026-07-12
carrier_story: CFP-2613
supersedes: []
related_adrs:
  - ADR-121  # deprecate-deploy-lanes — soak verdict = liveness 스코프 고정(생존 binary ∧ sink monotone). 성능 metric(p50/p95/throughput) 진입 = deploy-review 부활선(§결정10 금지선). pre-merge test-lane soak ≠ post-deploy 성능. 예방체인 잔여 catch-owner = ADR-121 §결정8 기존 consumer post-deploy smoke(cross-ref, 신규 메커니즘 금지)
  - ADR-014  # operational-risk-ssot Amd7 §7.4.7 outcome-signal 3요소 선언 의무 — G2 = 선언→실측 승격. "consumer 실측 위임" 부분철회 아님(3-layer 로 위임 보존, §결정1/3)
  - ADR-015  # stateful-test-category Amd1 §8.5 soak/restart + wrapper-self declarative 면제 — 면제 삭제 금지(면제 위에 실행 게이트 추가, §결정3/5). ADR-055 deferred thread realize. StatefulTest 소생 아님
  - ADR-136  # frontend-quality-gate 결정14 execution-liveness 3요건(L1 blocking/L2 full-scope/L3 self-tested) = 표면A blocking 승격 상위 원리(§결정4). §8.7 frontend 실렌더 = backend 데몬 등가물 청사진
  - ADR-146  # dynamic-test-burden-flip(G4) §결정3 soak=G2 단일소유 명시 위임 + g2_boundary_check Epic 경계 fail-closed. §결정8 "완전 봉인 hard-claim 금지" 정직천장 선례 상속(§결정8). §결정4 "test liveness" 어휘 금지 상속(축3 = 지속-liveness-runtime)
  - ADR-008  # inter-plugin-contract-versioning — test-verdict-v2 soak_liveness_results = additive MINOR v2.2→v2.3(신규 optional top-level, backward-compatible). requirements-output-v1 = 편집 0(§결정9)
  - ADR-060  # adequacy SSOT + 승격 evidence-gate — 표면A warning→blocking 승격 = self-test(L3 mutation-kill) evidence 종속. self-test 없이 승격 = ADR-060 위반 + hollow(§결정4)
  - ADR-006  # testcontract-architect Amd2 §8 Test Contract + 정직 천장(hollow-gate 금지). 엣지 도출 기법 walk(tier A/B) active. §8 Test Contract = ArchitectAgent chief 통합(§결정8)
  - ADR-048  # test lane 재조정 — TestAgent/StatefulTestAgent deprecated, IntegrationTest 단일 실행 agent. §8.5 소생 금지 근거(§결정5)
  - ADR-055  # IntegrationTest Epic-level Deployability 4-step 소유 — G2 표면B = 이 4-step 의 soak 확장 편입(단일 실행 agent 보존, §결정5)
  - ADR-139  # background-wait liveness gate(축2 orchestration-wait) — G2 = 축3(runtime). 개념 재사용(K8s probe rule/detection≠recovery/fail-open 금지 상속), 축 자체 직교. soak 대기 자체의 무한 hang = 축2 wall-clock ceiling 적용(§결정2 어휘 혼동 차단)
  - ADR-133  # ADR-RESERVATION atomic claim — 본 ADR 번호(148) claim(claimant ArchitectAgent:CFP-2613:g2-design)
  - ADR-005  # N/A 명시 패턴 — §11 데이터 마이그레이션(§11.1~§11.5) 자연 N/A substantive reason(wrapper-self governance, RDB/persistence/schema 무변경) + §11.6 CONDITIONAL-ACTIVE narrow(§결정12)
  - ADR-119  # research-before-claims / outcome-honesty — proxy 아닌 ground-truth(terminal sink) 검증 = G2 철학 뿌리. 게이트 verdict = outcome ground-truth 로만 단정(INV-D1)
  - ADR-127  # no-exemption 정식 풀 플로우 — fail-closed no-optout(skip-PASS 폐지, AC-10). G2 = 강화 방향(계승)
  - ADR-013  # dogfood-out — 본 ADR = Story §7 설계 SSOT, Change Plan(internal-docs wrapper/change-plans) 병존
related_concepts:
  - persistent-liveness-soak
  - crashloop-runtime-gap
is_transitional: false
---

# ADR-148 — G2 지속-liveness soak 게이트 (2-표면·3-layer·verdict-kernel seam + 정직 천장)

## 상태

Accepted (2026-07-12 KST) — CFP-2613 (Epic CFP-2602 G2) carrier. "프로덕션 이미지를 배포하면 CrashLoopBackOff 되는 결과물"(Gap B, 런타임-현실 갭)을 게이트 도메인 불변식 위반으로 재정의하고, codeforge 게이트에 **지속-liveness(soak-liveness) = 프로세스가 N분 살아 실제 일 하는가** 개념을 first-class 로 도입하는 governance SSOT. 강화(ratchet↑) 방향 — 기존 §7.4.7 outcome-signal 선언·§8.5 soak 면제·IntegrationTest Deployability 4-step 위에 **표면 A 선언 fail-closed 승격 + 표면 B 런타임 soak 편입**을 얹는다. **약화 surface 0** — 신규 required context 편입은 **사용자 결정으로 유보**(shadow-first, §결정10). ADR-015 declarative 면제·ADR-121 consumer 위임 무손상.

> **번호 발급 (ADR-133 atomic claim)**: `scripts/lib/adr-reservation-atomic-claim.py` claim 실행 완료 — claimant `ArchitectAgent:CFP-2613:g2-design`, exit 0, 반환 **148**(origin/main `adr-reservation-claim-state.json` `max_adr_number: 147` → 148, race 0). RESERVATION row inline append 은 commit 시점 ArchitectAgent 경로(ADR-070) 유지 — Phase 1 PR carrier 에서 수행.

## 컨텍스트

사용자 원문(Story §1 verbatim, 2026-07-11 KST): "data collector를 만들었으나 crashloopbackoff되는 결과물을 내놨다 … 요건을 충족하고 사용 가능한 결과물을 만드는 건 기본인거잖아". 본 child Story(G2) 범위 = **"배포하면 CrashLoopBackOff 되는 결과물" = Gap B(런타임-현실 갭)** 직접 대응. 부모 Epic CFP-2602 의 fail-closed 게이트 3종 중 G2 = 지속-liveness soak 게이트.

**핵심 진단**: codeforge 게이트가 **런타임 데몬의 "지속 생존"을 판정할 도메인 개념을 first-class 로 갖고 있지 않다.** IntegrationTest Deployability 는 `up -d --wait`로 t≈0 기동만 보고(db_probes 미정의=step 생략-PASS / health_checks 미정의=default HTTP :8000/health 200 = HTTP-only), 지연 크래시·비-HTTP 데몬의 terminal-sink 진행성 부재를 놓친다. 이것이 사용자 carrier(배포 후 CrashLoop)의 게이트-측 진원이다.

실측된 갭(deputy 종합, origin/main 6.75.0 04cf1138 실측):

- **표면 A 진원**: `scripts/check-operational-outcome-signal.sh` = §7.4.7 3요소 + §8.5.1 soak presence grep, **warning-tier `exit 0` always**(L14/L84-85) — 선언 부재가 침묵으로 green. operational:true 스코핑·self-test job `operational-outcome-signal-test`(dirty/clean discriminating) 이미 존재 = 승격 seed. [verified: origin/main]
- **표면 B 진원**: `plugins/codeforge-test/agents/IntegrationTestAgent.md` Deployability 4-step = t≈0 boot + HTTP-only. soak step 부재. [verified: origin/main]
- **soak 알고리즘 부분 재사용 가능**: `templates/github-workflows/post-deploy-benchmark.yml` L112-180 = terminal-sink monotone poll(역행→FAIL / floor 창 net 순증 0→freeze FAIL / manifestation-derived∨duration_floor 1800s 종점). **단 이것은 sink 축 단독** — 프로세스 생존(exit/restart) 관측·boot-grace 창은 부재(§결정3 F1). 또한 이 workflow 는 `invariant-check.yml` L47 `CONSUMER_ONLY_WORKFLOWS` 등재 = wrapper-self 미실행 consumer 템플릿. [verified: origin/main]

도메인 불변식 **INV-D1(ground-truth over proxy)**: liveness 판정 1차 metric = terminal downstream sink 의 monotone 전진(적재 종점 = outcome ground-truth). ingest-boundary·internal proxy 아님 — ingest 가 green 이어도 downstream 적재가 동결될 수 있다.

외부 근거(Story §6 재인용 — 신규 외부 단정 없음): Soak/endurance testing = 지속 부하 하 누적 결함 발견(`source: grafana.com/load-testing/types-of-load-testing`, soak=average-load 장시간 변형). K8s liveness probe = "실행 중이나 진행 못 하는(deadlock) 상태 재시작"(`source: kubernetes.io/docs/concepts/workloads/pods/probes`), cardinal rule "대상 진행성만" — non-HTTP 데몬은 exec/tcpSocket/grpc native handler 로도 판정 가능(HTTP 200 강제 아님). Startup probe = 느린 부팅 유예(오kill 방지). Testcontainers = 실 의존성 ephemeral 컨테이너(`source: testcontainers.com`). 정직 천장 = 유한 관측창은 결함 부재를 증명 못 함(absence of evidence ≠ evidence of absence — heisenbug/flaky). ∴ soak 은 확률저감·결정론적 boot-bail 포착이지 봉인 아님.

## 결정

codeforge 게이트에 지속-liveness soak 개념을 **정직하게 두 표면으로 분리**해 도입한다: (A) 선언 fail-closed 정적 lint(wrapper dogfood 가능·전 Story normative) + (B) 런타임 soak 실행(consumer normative·wrapper declarative 면제 + fixture-daemon self-test). 판정 = 프로세스 생존(exit/restart 0) ∧ terminal-sink monotone 전진(HTTP-200 아님). soak verdict 은 liveness 스코프에 고정(성능 metric 진입 금지 = ADR-121 부활선). 게이트가 기계 강제 가능한 것(선언 presence·구조)의 천장을 정직 공개(no-hollow) — "완전 봉인"은 봉인하는 척 금지.

### 도메인 불변식 (INV-D1 ~ INV-D6 — 게이트 판정의 공리, 명문)

- **INV-D1 (ground-truth over proxy)**: liveness 1차 metric = terminal downstream sink 의 monotone 전진(적재 종점 = outcome ground-truth). ingest-boundary·internal proxy 아님. [근거: ADR-014 Amd7 §7.4.7(B) + ADR-119 §결정10]
- **INV-D2 (2-표면 분리)**: 선언(정적·wrapper dogfood 가능·전 Story normative) ⊥ 실행(동적·consumer normative·wrapper declarative 면제). → 결정 1.
- **INV-D3 (liveness = 생존 ∧ sink 전진, HTTP-200 아님)**: 판정 = 프로세스 생존(exit==0 ∧ restart_count==0) **AND** terminal-sink monotone 전진. 둘 중 하나만 = FAIL. non-HTTP 데몬은 sink 전진으로 판정. → 결정 5.
- **INV-D4 (soak duration = manifestation-derived OR duration floor)**: 고정 단창 금지. blanket pre-merge 1800s 금지. → 결정 7. [근거: ADR-015 Amd1]
- **INV-D5 (실사-mock 경계 = 외부만 mock, 내부는 실 코드경로)**: 외부 의존성(etcd/minio/feed)만 실사-mock, 대상 데몬 자신은 실 프로덕션 이미지·실 코드경로. `MCTRADER_SOURCE=fake` 금지. → 결정 5.
- **INV-D6 (정직 천장)**: "N분 생존·sink 전진 관측"은 증명, "무한 미래·모든 크래시 모드 봉인"은 증명 불가. "완전 봉인" hard-claim = 검사연극 = FAIL. → 결정 8. [근거: ADR-146 §결정8 + ADR-006 Amd2]

### 결정 1 — 2-표면 분리 (INV-D2, presence-ceiling 동형)

두 표면을 한 게이트로 뭉개면 wrapper-self 가 실 soak 을 못 돌려 검사연극(hollow)이 되거나, 반대로 consumer 를 mass-break 한다. 정직 분리:

| 표면 | 성격 | 검증 주체 | 정직 등급 |
|---|---|---|---|
| **A — 선언 fail-closed** | 정적 lint(선언 존재·유형 강제) | wrapper CI dogfood 가능(runtime 0) | 전 Story normative — 미선언=FAIL |
| **B — 런타임 soak 실행** | 동적(실 부팅→N분 soak→생존∧sink 전진) | consumer normative / wrapper 는 게이트 메커니즘 fixture-daemon self-test | wrapper declarative 면제(ADR-015 Amd1 유지) |

- **Dependency direction 불변식**: 표면 A(선언) ← 표면 B(실행) 정방향. 표면 A 가 test-verdict.soak_liveness_results 를 read = **금지**(순환 + runtime-0 dogfood 파괴). A 의 의존 closure = Story 파일 + 선언 schema read 로 고정(docker/net/컨테이너 0).
- **선언 schema 단일 SSOT**: 표면 A/B 어느 쪽도 필드 목록을 re-encode 금지(contract drift 차단). A=presence 검증만, B=실행만.

### 결정 2 — 지속-liveness-runtime 축 확정 + 3-sense 동음이의 가드 (ADR-139/146 어휘 규율 상속)

"liveness"는 codeforge 안에서 3개 직교 축으로 쓰인다. G2 = **축 3**. 혼동 금지:

| 축 | 질문 | 실패 형태 | SSOT |
|---|---|---|---|
| 1 adequacy(충분성) | 게이트가 충분히 검사하는가 | green-but-dead | ADR-060 / G4(ADR-146) |
| 2 liveness-orchestration(대기 생동성) | 대기가 유한시간 내 결론 | stall / 무한 대기 | ADR-139 |
| **3 지속-liveness-runtime ← 본 G2** | 배포된 프로세스가 N분 살아 실제 일 하는가 | 지연 크래시 / terminal-sink 동결 | **본 ADR** |

- ADR-139(축2)의 K8s liveness probe cardinal rule / detection≠recovery 분리 / fail-open 금지(stall≠PASS)는 축3 설계에 **개념 재사용** — 단 축 자체는 직교. soak 대기 자체가 무한 hang 하면 그것은 축2(wall-clock ceiling INV-L1) 대상.

### 결정 3 — verdict-kernel seam (재사용의 정확한 경계 — §3 blanket_designrefactor debate 수렴)

Story §4.1 "post-deploy-benchmark.yml 을 pre-merge boot-time 으로 당김 + 신규 runner 금지"는 **구조적으로 부분 부정확** — 정정한다.

- **F1 정정 (재사용은 sink-monotone 축 절반만)**: post-deploy-benchmark.yml soak = sink_metric() monotone poll 단독. **프로세스 생존(exit/restart 카운트) + boot-grace 창 = genuinely net-new layer** — 재사용할 기존 구현 없음. INV-D3(생존 ∧ sink-monotone **AND**)의 생존축을 self-test 하지 않으면 "CrashLoop 하지만 restart replay 로 sink 여전히 전진" 케이스가 현 알고리즘에서 PASS = 정확히 사용자 원 carrier 재현. 따라서 fixture-daemon self-test 는 **재사용 경로(monotone) + 신규 경로(생존/grace) 둘 다 커버**하고 mutation 표적을 양 경로 각각에 둔다.
- **정답 seam (통째 당김·통째 복붙 둘 다 기각)**: 통째 당김 → 성능 assert(§결정10) 유입. 통째 복붙 → clone. **verdict kernel = 순수 판정 함수** `evaluate_soak_sample(prev, cur, first, threshold, floor, deadline_reached) → {CONTINUE | FAIL_REGRESSION | FAIL_FREEZE | PASS_THRESHOLD | PASS_FLOOR}` **+ 안정 reason-code enum = 단일소스화**. orchestration(boot-grace / fixture-daemon 기동 / restart counting / CI 마커 / 실-sink query / sleep-poll)= **vehicle-local 신작**(컨텍스트 divergence 정당).
- **kernel 물리형태 = 구현(Dev) 소관**: post-deploy-benchmark.yml = CONSUMER_ONLY_WORKFLOWS 이므로 wrapper-self 미실행. 물리형태 2안 (A) `templates/` 소script(consumer-distributed, wrapper self-test 호출 가능) / (B) schema 문서 canonical spec + reason-code enum, vehicle embed — 확정은 §3 결정 밖(seam 배치만 본 ADR 확정, 물리 배치 = Phase 2 구현).
- kernel 추출 후 호출자 = post-deploy(기존) + pre-merge IntegrationTest boot-soak(신규) + wrapper fixture-daemon self-test(신규) = 3.
- **[Phase 2 구현 각주] shipped 안정 reason-code enum = 6종**: 본 절 enum 5종(`CONTINUE|FAIL_REGRESSION|FAIL_FREEZE|PASS_THRESHOLD|PASS_FLOOR`)에 더해 실배선 kernel(`scripts/lib/soak-verdict-kernel.sh`)은 **`FAIL_THRESHOLD_MISS`** 1종을 additive 로 포함한다. 이는 기존 `post-deploy-benchmark.yml` 의 "deadline 경과 ∧ threshold 미도달 → exit 1" FAIL path 를 **behavior-invariant 로 label** 한 것(exit code·게이트 semantics 무변경 = 동작-불변 리팩터). 게이트 판정 의미 변경이 아닌 impl-level single-sourcing 이므로 본 §결정3 결정을 정정하지 않는다(enum 은 5→6 additive, 5종 semantics 전원 불변).

### 결정 4 — 표면 A execution-liveness 3요건 (ADR-060 evidence-gate 종속)

표면 A(선언 lint)의 warning→blocking 승격은 **execution-liveness 3요건**(ADR-136 결정14)을 AND 로 충족해야 유효 — any 미충족 = 게이트 무효:

- **L1 blocking**: warning-tier `exit 0` → `exit 1`(fail-closed RED). 데몬 Story 한정.
- **L2 full-scope**: operational:true ∧ long_running_daemon Story 전원 + `templates/`·`.github/` 양 copy 커버, 우회 0.
- **L3 self-tested**: fixture-daemon self-test 로 정상→PASS / 크래시→FAIL / 가드 mutation→RED 실증(mutation-kill).
- **★ blocking 승격 = ADR-060 evidence-gate 종속**: self-test(L3)가 landed 되어 RED→GREEN + mutation-kill 실증하면 그것이 곧 ADR-060 evidence 충족 → day-1 blocking 방어 가능. **self-test 없이 blocking 승격 = ADR-060 위반 + hollow.** 기존 `operational-outcome-signal-test` job = L3 seed.

### 결정 5 — 표면 B = IntegrationTest Deployability soak 편입 (StatefulTest 소생 배제)

- 표면 B 배선 = `IntegrationTestAgent.md` Deployability 4-step 에 soak step 추가((a) 계열 — docker-compose.test 부팅 이미 수행, ADR-048/055 단일 실행 agent 보존). **StatefulTest(§8.5) 소생 배제**(ADR-048 deprecated 되돌리기 = 재논의 비용). §8.5 soak/restart 개념은 IntegrationTest 편입으로 realize(어휘로만 참조).
- **실사-mock 경계(INV-D5)**: 외부 의존성만 testcontainers 실 컨테이너(precondition-bearing stateful deps — etcd lease/minio/WAL volume, 부재가 곧 CrashLoop 원인이므로 관대한 stub 은 bail-path 은폐) + 합성 고volume 피드(hermetic, 실 venue egress 0). **대상 데몬 = 실 프로덕션 이미지·실 코드경로**(`MCTRADER_SOURCE=fake` 금지, AC-5). prod mem_limit 적용(OOMKill class pre-merge 로 당김).
- **판정 = 생존 ∧ sink 전진, HTTP-200 아님(INV-D3)**: 프로세스 생존(exit==0 ∧ restart_count==0) AND terminal-sink monotone 전진. flat(전진 0)/역행 = 프로세스 살아있어도 FAIL(AC-7, ingest green ≠ sink 전진). non-HTTP sink-advance 판정표면 = 로그 progress / metric endpoint / DB committed row count / object-store part / consumer offset — **K8s native probe handler(exec/httpGet/tcpSocket/grpc)가 아닌 G2 신설 개념**(monotone 값 반환 exec custom probe 등가).

### 결정 6 — daemon_type 스코핑 + sink_probes[] schema (인터페이스 hazard 3종 회피)

- **daemon_type discriminator 신설(operational:true overload 금지)**: `operational:true` = NECESSARY but NOT SUFFICIENT(has-outcome-signal ⊥ is-a-daemon 직교 속성 conflate 차단). enum `{long_running_daemon, request_response_service, batch_job, cli, none}`, 게이트 scope = `long_running_daemon ∧ operational:true`. HTTP 서비스(request_response_service)는 기존 HTTP-200 default 유지(mass-breakage 회피).
- **escape 3중 차단**: ① operational:true Story 는 daemon_type 선언 **필수**(누락=FAIL, silent default 금지) ② 구조-corroboration lint(restart:always ∧ no-HTTP-bind ∧ background-loop → 데몬인데 비-데몬 선언 = escalate) ③ review anchor(완전 자동분류 불가 = 정직 천장).
- **AC-2 fail-closed 를 기존 필드 재해석으로 걸지 말 것(breaking 회피)**: health_checks/db_probes "미정의=생략(PASS)" 의미 뒤집기 = 기존 인터페이스 breaking change. → fail-closed 는 **신규 discriminator(daemon_type) + sink_probes[] presence** 에 key("long_running_daemon Story ⇒ sink_probes[] 선언 필수"). 기존 health_checks/db_probes 부재 의미 **전원 불변**.
- **sink_probes[] = dual-location**: change-plan §7.4.7(설계 선언, prose: sink/metric/임계/trigger-type) ⊥ project.yaml integration_test(런타임 배선). entry = cohesion cluster `{name, probe_type(sink-advance/exec/log-progress), metric_command, boot_grace_seconds, threshold | duration_floor_seconds, poll_interval_seconds}`(db_probes[] entry mirror) — boot-grace/liveness-유형을 top-level 산발 금지. daemon_type·sink_probes = origin/main 전무(신설).

### 결정 7 — soak duration = manifestation-derived PRIMARY + floor fallback (INV-D4)

- 고정 단창 금지(ADR-015 Amd1). duration = manifestation-derived PRIMARY(실패-class 임계를 넘는 대표 최소창 — 예: 사용자 원 "5분/1시간 compactor" = ≥1 full compaction cycle / flush 누적 / RSS-to-OOM) + duration_floor fallback(임계 정량 미도출 시). **blanket 1800s pre-merge 금지**(cost → opt-out 압력) — full-duration 은 post-deploy. `manifestation-trigger-type`(time ∨ volume) 선언 신설.
- **boot-grace 창(soundness)**: exit/restart 카운트는 **선언된 boot-grace 창 경과 후에만 시작**(K8s startup probe 근거 — 느린-부팅 데몬 false-FAIL 방지). grace 내 exit = 부팅실패로 별도 판정. boot-grace 는 bounded escape-valve(ceiling ≤ soak/2, readiness-signal 우선) — 무한 grace = 크래시 은폐 → self-test mutation 표적(grace=∞ → RED). 미도입 시 flaky-soak → opt-out 압력 = 게이트 unsound.

### 결정 8 — 정직 천장 (AC-9, ADR-146 §결정8 / ADR-006 상속, INV-D6)

- soak 은 "N분 생존·sink 전진 관측"(증명 가능)을 증명하나 "무한 미래 안정성·모든 크래시 모드 봉인"(증명 불가 — absence ≠ evidence-of-absence, heisenbug/flaky)은 증명하지 못한다. 게이트 문서·판정은 이 둘을 정직 구분해야 하며, **"완전 봉인" hard-claim = 검사연극 = FAIL.**
- **예방체인 2단**: pre-merge 실사-mock soak(실-프로덕션 boot[실 WAL 볼륨권한/실 WS egress/venue lease-under-load] 미증명) → 잔여 catch-owner = **post-deploy consumer 실-의존성 smoke**(ADR-121 §결정8 기존 smoke, cross-ref만 — 신규 post-deploy 메커니즘 신설 금지). soak PASS = 완전 봉인 아님.

### 결정 9 — test-verdict-v2 v2.3 additive (ADR-008 MINOR) + requirements-output-v1 편집 0

- `soak_liveness_results` = **독립 top-level optional object**(deployability_verified boolean 하위 nesting = type change = MAJOR → 금지). 필드: `{survival: bool(exit==0 ∧ restart_count==0), sink_monotone_progressed: bool, soak_verified: bool, liveness_declared: bool, soak_duration_s, soak_duration_basis: enum(manifestation|floor), boot_grace_s: nullable, honest_ceiling_ack: bool}`. **perf 필드(p50/p95/throughput) 배제**(§결정10). additive MINOR v2.2→v2.3.
- **hollow 방지**: (i) 게이트 merge-block key = **`soak_verified==false`** = (`survival==false ∨ sink_monotone_progressed==false`) 양축 — INV-D3/INV-T1 AND 정합(생존만 block key 삼으면 sink-freeze[생존∧flat, AC-7] block 누락) (ii) self-test 가 "크래시→survival=false→FAIL" ∧ "flat-sink→sink_monotone_progressed=false→FAIL" 둘 다 실증.
- **requirements-output-v1 = 편집 0**(v1.2 tier-aware 가 이미 2-surface 강제: normative → named §8 test 필수, declared/advisory → exempt). AC tier cut = 선언층 AC(AC-1/3/4/5) normative(표면A self-test 기계검증) / 실행층 -e = **declared**(wrapper runtime-0 라 실 soak 불가 → fixture-daemon self-test 가 declared 실행축의 wrapper-side 검증 채널; **declared ≠ 무검증**). AC-ID suffix = 소문자 [a-z].

### 결정 10 — ADR-121 성능-assert 물리 배제 (F2) + required 편입 = 사용자 결정(shadow-first)

- **F2 성능-assert 누출 차단**: 재사용 workflow 의 throughput_target/rss_ceiling_mb step 은 명시 미채택. pre-merge soak module closure = **생존 + monotone-sink core 만**. `soak_liveness_results` schema 에 perf 필드 물리 배제 → schema 가 성능 verdict 를 실을 수 없다. soak verdict = liveness 스코프 고정(성능 metric = deploy-review 부활선, ADR-121 §결정C 금지).
- **F3 required 편입 = 사용자 결정(비가역+consumer mass-break = ask-trigger)**: **LIVE branch-protection = 6-tuple** [verified: gh api live = 6-tuple, 2026-07-12 (`phase-gate-mergeable`/`invariant-check`/`doc frontmatter schema (CFP-28 — strict)`/`doc section schema (CFP-28 — strict)`/`check-gate`/`Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)`) / CLAUDE.md doc = 7-tuple(doc-ahead drift) — proxy≠ground-truth]. 표면 A lint 를 required contexts 편입 = **LIVE 6→7-tuple**(구 "7→8" 는 doc proxy 오독 → 폐기; **최종 tuple 크기 = G1 `ac-traceability-matrix` 등록 순서 의존**, 현재 live 미등록 = dead-gate) = 사용자 결정. **설계리뷰 escalate.** 권장 = **shadow-first**(blocking 승격[L1]하되 required 미편입 → bounded window 실 PR 신호 관측 → 후속 CFP 편입) — **G1 이 즉시-required 등록에 실제 실패(live dead-gate)한 정황이 shadow-first 를 강하게 지지**. 본 ADR 은 blocking 승격 원리만 확정, required 편입 여부는 사용자 결정으로 유보.
- **[관찰됨·미조치, ADR-119 §결정9] G1 documented⊥live drift**: `ac-traceability-matrix` 는 문서(CLAUDE.md/ADR-145 §결정3)상 required(6→7)이나 gh api LIVE 미등록 = dead-gate. **G2 out-of-scope(sibling-disjoint) — CFP-2609(G1 required 등록 완결 carrier)로 라우팅**, G2 에서 수정 금지.

### 결정 11 — sibling disjoint (g2_boundary_check, ADR-146 §결정3)

- soak/restart/replay = **G2 단일소유**(ADR-146 §결정3 명시 위임). G4 `g2_boundary_check` token 이 §8.8 4기법(fuzz/property/load/concurrency)이 soak 로 넘어가지 않음을 fail-closed 검사. G2 는 concurrency(interleaving 축)/dark-flag(G3) 재발명 금지. G1(CFP-2603) AC-traceability v1.2 = 준수(재발명 아님).

### 결정 12 — §11 데이터 마이그레이션 N/A + §11.6 CONDITIONAL-ACTIVE narrow (ADR-005 패턴)

- 본 Story = wrapper-self governance — RDB/persistence/schema 변경 0. §11.1~§11.5(schema/migration/rollback/integrity/backfill) = **자연 N/A**(substantive reason: 게이트 schema·lint·agent-md·contract 만 변경, DB 무접촉).
- **§11.6 idempotency = CONDITIONAL-ACTIVE narrow**: restart-capable append-sink 데몬(consumer) 의 sink metric = **committed/deduped count**(replay 시 double-count → false monotone-advance 차단). full replay test(§8.5.3) = G2 out-of-scope(sibling-disjoint). 이 narrow 는 설계 원리(선언 schema 의 metric semantics)만 규정 — 실 replay 실행 게이트 아님.

## 정직 천장 (본 ADR 스스로의 한계 공개)

본 ADR 은 게이트가 기계 강제 가능한 것(선언 presence·구조·필드값 실소비·self-test mutation-kill)의 fail-closed 를 확정한다. 강제하지 **못하는** 것을 정직 공개한다: (a) 실사-mock 이 실 프로덕션 boot 전제(실 볼륨권한/실 egress/venue lease-under-load)를 충분히 재현하는지 = 재현 충실도의 review-tier 판단(잔여 = post-deploy smoke). (b) manifestation 임계가 실 실패-class 를 대표하는지 = 도메인 판단(review anchor). (c) 무한 미래 안정성·모든 크래시 모드 = 증명 불가(§결정8). "완전 봉인"을 봉인하는 척 하지 않는다 — 구조 fail-closed + 형식누락 저감 + 잔여 정직 공개의 defense-in-depth.

## 대안 (기각 근거)

- **단일 게이트로 표면 A/B 통합**: wrapper-self 가 실 데몬이 없어 실 soak 불가 → schema presence 검사만 남아 검사연극(hollow) OR 반대로 consumer mass-break. 기각 → 2-표면 분리(결정1).
- **StatefulTest(§8.5) 소생**: §8.5.1 soak 로직 존재하나 ADR-048 deprecated 되돌리기 = 단일 실행 agent 원칙(ADR-055) 위반 + 재논의 비용. 기각 → IntegrationTest Deployability 편입(결정5).
- **post-deploy-benchmark.yml 통째 pre-merge 당김**: throughput/RSS 성능 assert 유입 = ADR-121 deploy-review 부활선(AC-6). 통째 복붙 = clone. 둘 다 기각 → verdict-kernel seam(결정3).
- **HTTP-200 default 로 non-HTTP 데몬 판정**: deadlock 데몬(running-but-no-progress)을 놓침(INV-D3 위반). 기각 → sink-advance 신설 개념(결정5/6).
- **표면 A 즉시 required 편입(LIVE 6→7-tuple)**: 적용성 가드 없이 신규 required context = consumer mass-break 비가역 리스크. 기각 → shadow-first + 사용자 결정 유보(결정10). G1 즉시-등록 실패(live dead-gate) 정황이 이 기각을 실증.
- **soak 고정 blanket duration(예 1800s) pre-merge**: cost → opt-out 압력 = 게이트 unsound. 기각 → manifestation-derived + floor(결정7).

## 결과

**긍정**: 사용자 carrier(배포 후 CrashLoopBackOff)의 게이트-측 진원(지연 크래시·terminal-sink 동결 미포착)을 도메인 불변식(INV-D1~D6)으로 재정의하고 fail-closed 강제 경로를 확보. wrapper-self 는 fixture-daemon self-test 로 게이트 메커니즘을 정직 dogfood(runtime-0 딜레마 해소), consumer 는 실 soak 로 실효. ADR-015 declarative 면제·ADR-121 consumer 위임·기존 health_checks/db_probes 의미 전원 무손상(강화 방향).

**부정/비용**: 표면 B 실 soak = consumer CI 시간·자원 비용(manifestation 최소창으로 완충). fixture-daemon self-test 신작 = Phase 2 구현 부담. daemon_type/sink_probes 신규 schema = consumer 주입 학습곡선.

**미결(하류 이관)**: (1) required 편입 여부(**LIVE 6→7-tuple**, 최종 크기 = G1 등록순서 의존) = **사용자 결정**(설계리뷰 escalate, shadow-first 권장). (2) verdict-kernel 물리형태(templates/ 소script vs schema spec-embed) = Phase 2 구현. (3) manifestation 임계 대표성·실사-mock 재현 충실도 = review-tier + post-deploy smoke(정직 천장). (4) **G1 documented⊥live drift(dead-gate)** = CFP-2609 라우팅(G2 out-of-scope).

**후속**: Phase 2(같은 Story §8-§11 PR) = 표면 A lint 승격 + 표면 B soak step + sink_probes[]/daemon_type schema + fixture-daemon self-test + test-verdict-v2 v2.3 실배선. ADR-RESERVATION row inline append(claimant `ArchitectAgent:CFP-2613:g2-design`, 번호 148).

## 관련 파일

- `plugin-codeforge/scripts/check-operational-outcome-signal.sh` — 표면 A 승격 진원(warning→blocking, L1)
- `plugin-codeforge/.github/workflows/operational-outcome-signal-lint.yml` + `operational-outcome-signal-test` job — 표면 A CI wire + L3 self-test seed
- `plugin-codeforge/plugins/codeforge-test/agents/IntegrationTestAgent.md` — 표면 B Deployability soak step 편입 대상
- `plugin-codeforge/templates/github-workflows/post-deploy-benchmark.yml` — verdict-kernel sink-monotone 재사용 소스(CONSUMER_ONLY)
- `plugin-codeforge/docs/inter-plugin-contracts/test-verdict-v2.md` — soak_liveness_results additive v2.2→v2.3
- `plugin-codeforge/plugins/codeforge-design/templates/change-plan.md` §7.4.7/§8.5 — sink_probes[]/daemon_type 선언 schema
- `codeforge-internal-docs/wrapper/change-plans/cfp-2613-g2-persistent-liveness-soak-gate.md` — 파일 단위 배선 + §8 Test Contract full (본 ADR 병존)
- `codeforge-internal-docs/wrapper/stories/CFP-2613.md` §7 — 설계 서사 요약(본 ADR = 결정 SSOT)
