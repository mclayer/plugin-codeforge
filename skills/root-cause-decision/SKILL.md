---
name: root-cause-decision
description: FIX 원인 판정 decision table. failure 유형별 1차 가정·설계 escalate 조건. FIX 루프 트리거 시 Orchestrator 호출 의무. fix-ledger-schema와 함께 호출.
tools: Read
---

# FIX 원인 판정 Decision Table

> 참조 테이블 skill — 내용을 읽고 FIX 원인 판정에 적용하세요.

## 호출 시점

FIX 루프 트리거 시 (설계리뷰 / 구현리뷰 / 구현테스트 / 보안테스트 / 배포 / 배포리뷰 FAIL). DeveloperPL 1차 진단 전 Orchestrator 호출.

- **runtime 실패 분기 (3rd rung)**: runtime 실패(제품 동작 실패)가 표면 증상-anchored 진단 OR 설계 escalation 종점까지 가서도 반복 FAIL 이면 — 이는 FIX loop(구현 ↔ 설계 ping-pong) 가 아니라 **문제정의 오류 → 요구사항 lane 재진입** 의 별 경로다 (아래 §iteration 가설 차별화 원칙 의 3rd rung escalation 적용). ADR-064 §결정 13.

## 프로세스

설계 리뷰 FIX는 DeveloperPL 개입 없이 ArchitectPLAgent 직접 회귀. 구현 리뷰·구현 테스트·보안 테스트 FIX는 DeveloperPL 1차 원인 진단 → Orchestrator 경유 → ArchitectPLAgent 최종 판정. 모든 경우 evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무. Story file §10 FIX Ledger에 누적.

## 원인 판정 테이블

| Failure 유형 | 1차 가정 | 설계 원인 escalate 조건 |
|---|---|---|
| **설계 리뷰 P0 §7 누락** | **설계** | 항상 설계 (ArchitectAgent chief author 미흡) |
| Unit test FAIL | 구현 | 테스트 사양이 Change Plan 계약과 불일치 |
| Integration test FAIL | 구현 | 모듈 경계·계약 위반 |
| Infra test FAIL | 구현 | 배포/환경 요구 Change Plan 누락 |
| 성능 test FAIL | **설계** | 단순 최적화로 해결되면 구현 |
| Code review P0 보안 | 구현 | trust boundary 설계 오류 |
| Code review P0 아키텍처 | **설계** | 레이어·의존성 방향 위반 |
| **Code review P1 품질 (local)** | 구현 | 단일 파일·함수 내 품질 (naming, 작은 중복, 가독성) |
| **Code review P1 품질 (boundary)** | **설계** | 모듈 경계·인터페이스·패턴 일관성 (여러 파일 공통 이슈, 설계 지침 부재) |
| **보안 테스트 (opt-in — security_ai:true) P0 injection·credential hardcode** | 구현 | 코드 단위 결함 |
| **보안 테스트 (opt-in — security_ai:true) P1 암호학 오용·CVE** | 구현 | 코드 수정·버전 업그레이드로 해결 |
| **보안 테스트 (opt-in — security_ai:true) P1 boundary 권한 일관성** | **설계** | 여러 파일·레이어 공통 지침 부재 |
| **보안 테스트 (opt-in — security_ai:true) P0 trust boundary 위반** | 구현 | §7.1에 boundary 부재·모순 또는 §7.1과 코드 boundary 불일치 → 설계 |
| **보안 테스트 (opt-in — security_ai:true) P0 auth/authz 결함** | 구현 | §7.3 인증·권한 모델 자체 결함 → 설계. 모델은 맞으나 구현 결함 → 구현 유지 |
| **구현 테스트 Migration FAIL · data integrity 위반 · rollback 실패** | 구현 | §11.1-§11.5 부재·모순 → 설계. 모델은 맞으나 script 결함 → 구현 유지 |
| **§7.4 DR/disconnect cascade FAIL** | 구현 | §7.4 boundary 부재·모순 → 설계 |
| **§7.4 Rate limit / IP ban** | 구현 | §7.4 quota·throttling 정책 부재 → 설계 |
| **§7.4 Env isolation 위반 (live ↔ staging 누설)** | 구현 | §7.4 isolation 모델 부재 → 설계 |
| **§7.4 Clock skew FAIL (CONDITIONAL active)** | 구현 | §7.4 skew tolerance 부재·N/A 모순 → 설계 |
| **§11 Idempotency 위반 (CONDITIONAL active)** | 구현 | §11 invariant 부재·N/A 모순 → 설계 |
| **§8.5 Cache / state drift (long-running)** | 구현 | §8.5.1 long-running invariant 정의 부재 또는 §7.4.1 DR boundary 부재 → 설계 |
| **§8.5 Unbounded background accumulation** | 구현 | §7.4.4 rate limit / quota 정책 부재 또는 §8.5.1 worker queue bound 정의 부재 → 설계 |
| **§8.5 Restart recovery loss** | 구현 | §7.4.5 env isolation 모델 부재 또는 §11.6 idempotency CONDITIONAL active 인데 spec 부재 → 설계 |
| **§8.5 Idempotency replay failure (§11.6 active 시)** | 구현 | §11.6 idempotency invariant 정의 부재 → 설계 |
| **Real-funds 손실 (Live trade) — CONDITIONAL Live touching Story** | 구현 | §7.4 live exposure limit / §11 ledger invariant / first-trade cap 부재 시 → 설계 |
| **Kill switch 자동 발동 실패 (CONDITIONAL Live touching Story)** | 구현 | §7.4 trigger condition 부재 시 → 설계 |
| **Kill switch manual override 실패 (CONDITIONAL Live touching Story)** | 구현 | operator-action-v1 schema / protocol 부재 시 → 설계 |
| **Partial fill reconciliation 실패 (CONDITIONAL Live touching Story)** | 구현 | §11 partial fill invariant 부재 시 → 설계 |
| **Fee handling drift (CONDITIONAL Live touching Story)** | 구현 | §11 fee accounting invariant 부재 시 → 설계 |
| **Dockerfile build FAIL (CI) (CFP-128 / ADR-033)** | 구현 | Change Plan §3 image strategy / multi-stage 부재 → 설계 |
| **Container image CVE P0 (trivy) (CFP-128 / ADR-033)** | 구현 | base image 자체 stale (4y old, EOL) → 설계 |
| **hadolint P1 violation (CFP-128 / ADR-033)** | 구현 | (단일 파일) — 항상 구현 |
| **Compose service health check FAIL (CFP-128 / ADR-033)** | 구현 | §7.4 health check policy 부재 → 설계 |
| **Container secret 누설 (env / log / image layer) (CFP-128 / ADR-033)** | 구현 | §7.5 secret mount 전략 부재 → 설계 |
| **Network mode 위반 (internal service host network 노출) (CFP-128 / ADR-033)** | 구현 | §7.1 network boundary 부재·모순 → 설계 |
| **§7.4 Container restart loop / volume mount race (CFP-128 / ADR-033)** | 구현 | §7.4 restart policy / volume invariant 부재 → 설계 |
| **배포 lane healthcheck FAIL (CFP-1059 / ADR-087)** | 구현 | §12 배포 manifest 안 healthcheck endpoint 정의 부재 또는 §7.4 health check policy 부재 → 설계 |
| **배포 lane atomic swap FAIL (Traefik label flip race, CFP-1059 / ADR-087)** | 구현 | §3 도입할 설계 안 atomic swap mechanism 부재 또는 ADR-087 §결정 5 매커니즘 unsupported → 설계 |
| **배포 lane secret lookup FAIL (1Password Connect / .env fallback, CFP-1059 / ADR-087)** | 구현 | consumer overlay deploy.1password.* 부재 + .env fallback 미설정 → 설계 또는 consumer config 부재 (root cause = consumer 영역) |
| **배포 lane 자동 rollback 발동 (3-시간 보존 window 안, CFP-1059 / ADR-087)** | 구현 | §8 Test Contract 안 production smoke fixture 부재 → 설계, smoke spec 정상 but blue-green 매커니즘 결함 → 구현 |
| **배포 리뷰 smoke FAIL (양방향 호환 위반, CFP-1059 / ADR-088 + ADR-089 §결정 4)** | **설계** | §11 데이터 마이그레이션 안 ADR-089 7 원칙 §결정 1 (양방향 호환) 위반 — backward / forward 양방향 호환 미보장 |
| **배포 리뷰 성능 비교 FAIL (production runtime ↔ pre-deploy baseline, CFP-1059 / ADR-088)** | **설계** | ADR-068 I-5 dimensional empirical grounding 정합 — §3 도입할 설계 안 성능 invariant 부재 또는 `[empirical-source: TBD]` annotation 미해소. 단순 최적화로 해결 시 구현, 매커니즘 자체 결함 시 설계 (debate-protocol-v1 trigger 의무) |
| **배포 리뷰 cutover 사후 검증 FAIL (ProductionEvidence 4 measurement source, CFP-1059 / ADR-088 §결정 3 + ADR-072)** | **설계** | ADR-072 §결정 1-7 4 prerequisite measurement source 누락 또는 모순 — functional / security / monitoring / testing 4-tuple evidence 부재 |
| **배포 리뷰 schema 7 원칙 self-check FAIL (CFP-1059 / ADR-089)** | **설계** | §11 데이터 마이그레이션 안 7 원칙 (양방향 호환 / expand-contract 분리 / reverse / 양방향 smoke / cross-repo / backup / hard limit) 위반 — ArchitectAgent Phase 1 self-check 미흡 |
| **Cross-layer 의존 영향 mis-감지 (CFP-1059 / ADR-090 §결정 1)** | 구현 | ADR-090 §결정 1 자동 감지 (deps / volume / ORM / contract MANIFEST) miss → 설계, 사용자 declare 영역 누락 → 구현 (consumer overlay deploy.* schema 영역) |
| **변경 순서 invariant 위반 (expand source-first / contract leaf-first, CFP-1059 / ADR-090 §결정 2)** | **설계** | ADR-090 §결정 2 변경 순서 invariant 미준수 — 묶음 전체 rollback 영역, Change Plan §11 layer dependency 영역 부재 |
| **runtime 실패 (제품 동작 실패) — 표면 증상-anchored 진단 OR escalation 종점(설계) 반복 FAIL (CFP-2358 / ADR-064 §결정 13)** | **요구사항(문제정의 오류)** | 문제정의 자체 재검증 필요 → 요구사항 lane 재진입 (FIX loop 아님). ADR-064 §결정 13 |

## P1 품질 local vs boundary 판정 기준

- **local**: finding이 1개 파일 또는 1개 함수 범위에 한정, 설계 결정과 무관한 개별 구현 결함
- **boundary**: finding이 여러 파일·계층에 걸침, 또는 Change Plan에 "이 경계·패턴 어떻게 가야 하는지" 지침이 부족해서 발생한 이슈
- DeveloperPL이 1차 진단 시 이 분류를 포함 → ArchitectPLAgent 최종 판정

## 판정 후 액션

- **설계 원인 판정 시**: Change Plan 갱신 (§3/§6/§7/§8 해당 항목) → Phase 1 follow-up PR → 설계 리뷰 레인부터 재실행
- **구현 원인 판정 시**: Change Plan 유지, Phase 2 PR commit append → 구현 리뷰 재실행

### FIX-close 시점 ground-truth replay 의무 (CFP-2480 / ADR-070 Amendment 12 + ADR-119 §결정 10②)

> 진단 시점(위 decision table)은 falsification discipline 을 강제하나, **닫기 시점은 공백** 이었다 — E3 가 이 공백을 메운다. 본 3rd rung generative invariant sweep 의 close-time Codex 자동화 layer (중복 게이트 아님 — 진단=falsify 발화 / 닫기=replay 반증 후 close, 같은 Popper 비대칭의 다른 시점).

FIX "수정됨" 으로 §10 FIX Ledger 를 닫기 전, 원 finding 을 정당화한 reproducer 를 재실행해 **반증(이제 통과)** 확인 의무:

- **close 조건 = 원 reproducer 가 결정론적 GREEN 재현** (외부 Retest — finding 정당화한 *바로 그* 실패 명령이 fix 포함 worktree HEAD 에서 통과). 주장만으로 닫기 불가. `replay_verdict == PASS` 시만 close (fix-event-v1 v1.4).
- **reproduce-before-fix**: reproducer (실패 명령 + base SHA) 는 finding *생성 시점* 에 `reproducer_command` (fix-event-v1 v1.4) 로 기록 — 닫기 시점 재실행 가능하도록. reproducer 미기록 finding = close 불가 (`undetermined` 보류).
- **다회 결정론 확인** (1회 GREEN close 금지): flaky 가 false-GREEN(수정 안 했는데 우연 통과 → 부당 close, §1 목적 정면 훼손 최위험) + false-RED(진짜 고쳤는데 flaky → max-FIX 부당 소진) 양방향 오염. `deterministic_runs_required` 횟수 전부 GREEN 후만 close. mixed → `undetermined` quarantine.
- **실행자 ≠ 판정자**: Codex 가 replay 실행·보고, close 판정은 PL/Orchestrator 직접 재현 falsify 후 (`[hypothesis]` → `[verified]`). §10 close = Orchestrator 단독 (writer monopoly).
- **replay-impossible**: 실행 가능 명령으로 환원 불가한 finding (코드 P1 가독성·의미 판정 등) = `replay_verdict: replay-impossible` + **사유 명시 의무** (silent 면제 금지). 사람 검토 후보로 별도 disposition.
- **replay FAIL = max-FIX 카운터 disjoint** (`codeforge:fix-ledger-schema` 참조): replay `falsified` 는 닫기 거부((A)축 fail-closed)지 새 FIX iter 아님 — max-FIX 3/3 소비 안 함. 무한거부 backstop = fix-attempt 카운터.
- **결정 SSOT**: `scripts/lib/fix_replay_disposition.py` (pure function `decide_replay_disposition(packet)` → (verdict, provenance), INV-FR1~5 + INV-FR-FLAKY-1~3 + provenance 동반). concept SSOT = `docs/domain-knowledge/concept/fix-ground-truth-replay.md` (F-1~F-5).

## iteration 가설 차별화 원칙

> behavioral discipline — mechanical lint 불가, review/Orchestrator judgment 으로 검증.

- **매 FIX iteration 은 직전 iteration 과 다른 가설을 세운다.** 같은 원인 가설로 반복 수정(동일 fix 재시도)은 금지 — FIX Ledger §10 에 직전 iteration 의 가설이 기록되므로, 새 iteration 은 그것과 구별되는 가설을 명시해야 한다.
- **같은 가설이 2회 연속 FAIL 하면 1차 가정(구현 vs 설계)을 재분류** — 구현 가설이 반복 실패하면 설계 원인으로 escalate 고려 (위 decision table 의 "설계 원인 escalate 조건" 재평가).
- **3rd rung escalation (runtime 실패 — 문제정의 오류로 재분류)**: runtime 실패(제품 동작 실패) Story 에서 설계 escalation 종점까지 가서도 반복 FAIL **이거나** 직전 진단이 표면 증상-anchored(코드·invariant 미실측 상태에서 로그 문구·에러 메시지·관찰 현상으로 원인 직행 단정)이면 — 1차 가정을 **구현/설계가 아니라 문제정의 오류로 재분류** → FIX loop(구현 ↔ 설계 ping-pong) 가 아니라 **요구사항 lane 재진입** 으로 전환한다. 재진입 시 아래 재진입 규율 3종을 적용한다:
  1. **prohibited prior (가설 격리)** — 기존 진단(Orchestrator / lane 의 원인 단정)을 '검증 대상 가설' 로 격리한다. 재진입한 요구사항 / 요구사항리뷰 lane 에 **가설을 숨기고**(hypothesis-withheld) `{코드, 증상, outcome-contract, invariant-surface}` 4-tuple 만 제공한다 — 가설을 정답이 아닌 반증 대상으로 숨겨 확증 편향을 차단.
  2. **generative invariant sweep** — 실패 경로의 long-lived mutable 구조를 열거하고, 각 구조의 bound / lifetime / ordering invariant 를 명시하고, 코드 보존 여부를 실측한다 (ADR-068 I-8 standing invariant-surface = `docs/system-invariants.md` 색인을 cross-ref 해 enumeration 완전성 보강 — I-8 색인이 standing 기록처, 본 sweep 이 그 surface 의 소비자).
  3. **비대칭 결정규칙** — 증상을 설명하는 **file:line 으로 짚힌 위반 invariant 1개 > "확인함 OK" N개**. 단일 falsification 이 N attestation 을 이긴다 (Popper 비대칭).
  근거: ADR-064 §결정 13 (root-cause 사다리 3rd rung) + ADR-125 Amendment 2 (요구사항리뷰 lane 측 internal-invariant falsification 게이트, sibling carrier).
- DeveloperPL 1차 진단 보고 시 다음 형식으로 가설 차별을 명시할 것: **"이번 iteration 가설: \<X\> (직전 iteration 가설 \<Y\> 와 차별점: \<Z\>)"**.
- 근거: ADR-064 normative (FIX 의사결정 원칙). 외부 디버깅 skill 이 제공하던 hypothesis-differentiation discipline 을 본 skill 이 흡수.
