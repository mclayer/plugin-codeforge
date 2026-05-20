---
name: root-cause-decision
description: FIX 원인 판정 decision table. failure 유형별 1차 가정·설계 escalate 조건. FIX 루프 트리거 시 Orchestrator 호출 의무. fix-ledger-schema와 함께 호출.
tools: Read
---

# FIX 원인 판정 Decision Table

> 참조 테이블 skill — 내용을 읽고 FIX 원인 판정에 적용하세요.

## 호출 시점

FIX 루프 트리거 시 (설계리뷰 / 구현리뷰 / 구현테스트 / 보안테스트 FAIL). DeveloperPL 1차 진단 전 Orchestrator 호출.

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
| **배포 리뷰 cutover 사후 검증 FAIL (ProductionEvidence 4 measurement source, CFP-1059 / ADR-088 §결정 3 + ADR-72)** | **설계** | ADR-72 §결정 1-7 4 prerequisite measurement source 누락 또는 모순 — functional / security / monitoring / testing 4-tuple evidence 부재 |
| **배포 리뷰 schema 7 원칙 self-check FAIL (CFP-1059 / ADR-089)** | **설계** | §11 데이터 마이그레이션 안 7 원칙 (양방향 호환 / expand-contract 분리 / reverse / 양방향 smoke / cross-repo / backup / hard limit) 위반 — ArchitectAgent Phase 1 self-check 미흡 |
| **Cross-layer 의존 영향 mis-감지 (CFP-1059 / ADR-090 §결정 1)** | 구현 | ADR-090 §결정 1 자동 감지 (deps / volume / ORM / contract MANIFEST) miss → 설계, 사용자 declare 영역 누락 → 구현 (consumer overlay deploy.* schema 영역) |
| **변경 순서 invariant 위반 (expand source-first / contract leaf-first, CFP-1059 / ADR-090 §결정 2)** | **설계** | ADR-090 §결정 2 변경 순서 invariant 미준수 — 묶음 전체 rollback 영역, Change Plan §11 layer dependency 영역 부재 |

## P1 품질 local vs boundary 판정 기준

- **local**: finding이 1개 파일 또는 1개 함수 범위에 한정, 설계 결정과 무관한 개별 구현 결함
- **boundary**: finding이 여러 파일·계층에 걸침, 또는 Change Plan에 "이 경계·패턴 어떻게 가야 하는지" 지침이 부족해서 발생한 이슈
- DeveloperPL이 1차 진단 시 이 분류를 포함 → ArchitectPLAgent 최종 판정

## 판정 후 액션

- **설계 원인 판정 시**: Change Plan 갱신 (§3/§6/§7/§8 해당 항목) → Phase 1 follow-up PR → 설계 리뷰 레인부터 재실행
- **구현 원인 판정 시**: Change Plan 유지, Phase 2 PR commit append → 구현 리뷰 재실행
