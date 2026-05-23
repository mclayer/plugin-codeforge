---
adr_number: 88
title: Deploy Review lane 신설 — codeforge-deploy-review plugin + ProductionEvidenceDeputy ownership 이관
status: Accepted
category: lifecycle
date: 2026-05-20
carrier_story: CFP-1059
parent_epic: CFP-1059
related_stories:
  - CFP-1059  # carrier Epic
related_adrs:
  - ADR-087  # Deploy lane (sibling carrier within CFP-1059 — disjoint axis: 매커니즘 실행 ↔ 한 번 끝나는 검증)
  - ADR-72  # ProductionEvidenceDeputy mandate + Epic cutover gate (Amendment N 동반 — ownership 이관 mirror)
  - ADR-014  # operational risk SSOT (Amendment N 동반 — DeployReviewPL boundary)
  - ADR-042  # agent model selection (Amendment 9 동반 — DeployReviewPL Opus tier)
  - ADR-068  # boundary completeness invariants (I-5 dimensional empirical grounding — 성능 측정 기준)
  - ADR-059  # debate-protocol-v1 (성능 미충족 시 cross-module debate trigger)
  - ADR-089  # Schema 변경 7 원칙 (sibling carrier — 양방향 smoke 검증 anchor)
  - ADR-090  # Cross-layer 참조 정책 (sibling carrier)
  - ADR-026  # post-merge automation (Amendment N 동반 — Epic close → Deploy → Deploy Review cascade)
  - ADR-054  # doc-only fast-path (본 carrier Story-1 적격)
  - ADR-082  # write-time self-write verification (본 ADR self-write evidence enumeration 정합)
  - ADR-070  # Codex verify-before-trust (chief author direct write precedent)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무
related_files:
  - docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md
  - docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md
  - docs/adr/ADR-014-operational-risk-ssot-distribution.md
  - docs/adr/ADR-042-agent-model-selection-policy.md
  - docs/adr/ADR-026-post-merge-automation.md
  - docs/adr/ADR-068-boundary-completeness-invariants.md
  - docs/adr/ADR-059-debate-protocol-v1.md
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - templates/github-workflows/bidirectional-smoke.yml  # Phase 1 skeleton
  - skills/deputy-mandate/SKILL.md  # ProductionEvidence 이관 mirror cross-ref
amendment_log: []
amendments: []
is_transitional: false  # permanent lane structure — 약화 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null
mechanical_enforcement_actions:
  - deploy-review-lane-spawn-evidence  # declaration-only Wave 1 (ADR-087 precedent 답습)
---

# ADR-088 — Deploy Review lane 신설 (codeforge-deploy-review plugin + ProductionEvidenceDeputy ownership 이관)

## 상태

`Accepted (2026-05-20 KST)` — CFP-1059 Epic Story-1 carrier. ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. doc-only fast-path (ADR-054 Category 2).

## 컨텍스트

### 동인

사용자 발화 verbatim (CFP-1059 Epic body §1):

> "배포 > 배포 리뷰 레인은 어떤가? 배포 리뷰에서는 다른 리뷰 대비 성능 측정이 포함되고 성능 기준이 충족되지 않거나 리뷰 상 요구사항 또는 설계에 재조정이 필요한 경우 back하게 되는 것이다."

→ **WHY-2 (보조 motivation)**: 성능을 1st-class 검증 phase 로 격상.

### 기존 review lane 과의 disjoint axis

- **DesignReview** = ADR 정합 / 설계 보장성. code-level / production-level 미접근.
- **CodeReview** = 구현 품질. production runtime 측정 미접근.
- **SecurityTest** = code-level 보안 정합. production 환경 성능 측정 미접근.
- **IntegrationTest (codeforge-test)** = 시나리오 단위 정합 검증. production cutover 사후 검증 미접근.

→ **Deploy Review (본 ADR)** = production 환경 성능 측정 + cutover 사후 검증 영역, 위 4 review lane 모두와 disjoint axis.

### ProductionEvidenceDeputy 이관 동인

현재 (ADR-72) ProductionEvidenceDeputy = `codeforge-design` lane 의 CONDITIONAL deputy. 본 deputy 의 mandate = production cutover-touching Story 시 spawn 의무 (4 prerequisite measurement source).

**문제**: ProductionEvidenceDeputy mandate 가 production 환경 평가 영역 — 설계 lane 의 design 결정 layer 와 axis 불일치.

**해결**: ownership = `codeforge-design` CONDITIONAL → `codeforge-deploy-review` 정식 이관. mandate body 자체는 보존 (ADR-72 §결정 1-7 그대로).

### 사용자 결정 (2026-05-20 KST)

- 본 Epic scope = "한 번 끝나는 검증" 만 — smoke / 성능 비교 / cutover 사후 검증 3종.
- 운영 phase 8 후보 (canary promote / rollback 신호 회수 / 사용자 피드백 / regression 감지 / channel drift / 우선순위 입력 / cutover monitoring / smoke ongoing) = **별 Epic carrier** (본 Epic close 후 발의).
- 성능 기준 미충족 시 = 요구사항 / 설계 lane FIX 발동 (debate-protocol-v1 cross-module trigger 가능 — ADR-059).

## 결정

### §결정 1 — codeforge-deploy-review lane plugin 정식 신설

새 lane plugin `codeforge-deploy-review@mclayer` 신설. 8 lane composition 의 #7 row (ADR-087 §결정 1 표 참조).

본 lane scope = "한 번 끝나는 검증" 만 (운영 phase 영역과 disjoint — 별 Epic carrier).

### §결정 2 — DeployReviewPLAgent (Opus) + DeployReviewWorkerAgent (Sonnet) 2종 신설

| Agent | Model tier | Mandate |
|---|---|---|
| **DeployReviewPLAgent** | **Opus** | 성능 측정 + cutover 사후 검증 lead — smoke / 성능 비교 / cutover 사후 verdict 종합. 성능 기준 미충족 시 debate-protocol-v1 cross-module trigger (ADR-059) + ArchitectPL / RequirementsPL FIX dispatch. 본 lane = adversarial debate 자동 발동 영역 (Opus tier mandatory — ADR-042 §결정 1 정합) |
| **DeployReviewWorkerAgent** | Sonnet | smoke test 실행 (HTTP shadow / WebSocket·daemon 대기) + 성능 비교 baseline 수집 (latency / throughput / error rate) + cutover 사후 검증 worker |

ADR-042 Amendment 9 sibling carrier — 4 agent tier 결정 (DeployPL/Worker Sonnet + DeployReviewPL Opus + DeployReviewWorker Sonnet).

### §결정 3 — 검증 3종 (한 번 끝나는, 운영 phase 와 disjoint)

| 검증 | 시점 | 매커니즘 |
|---|---|---|
| **smoke** | atomic swap 직전 (green 컨테이너 healthcheck 후) | HTTP request shadow (production 트래픽 미러링 일부) — request/response 비교 + WebSocket·daemon 대기 mode (대기 안정성 검증) |
| **성능 비교** | atomic swap 직전 (smoke 통과 후) | latency p50/p95/p99 / throughput / error rate / CPU·memory baseline 대비. **[empirical-source: TBD]** — consumer 별 baseline 측정 의무 (mctrader 첫 적용 시 측정 후 lock-in) |
| **cutover 사후 검증** | atomic swap 직후 ~ 3-시간 보존 종료 시점 | 실 production 트래픽 의 error rate / latency 회귀 감지 + 사용자 영향 신호 수집 |

세 검증 모두 "한 번 끝나는" — 운영 phase 의 continuous monitoring (smoke ongoing / cutover monitoring 30일) 와 disjoint.

### §결정 4 — ProductionEvidenceDeputy ownership 이관

| 영역 | Before (ADR-72 현행) | After (본 ADR + ADR-72 Amendment N) |
|---|---|---|
| Ownership | `codeforge-design` lane CONDITIONAL deputy | `codeforge-deploy-review` lane 정식 deputy |
| Mandate body | 변경 없음 — ADR-72 §결정 1-7 verbatim 유지 |
| Spawn trigger | production cutover-touching Story 시 의무 (4 prerequisite measurement source) — 변경 없음 |
| wrapper-self-app | N/A (CFP-954 precedent 정합 — wrapper / lane plugin 영역 미적용) — 보존 |

ADR-72 Amendment N sibling carrier (mirror 갱신).

### §결정 5 — 성능 기준 미충족 시 FIX 발동 + debate-protocol-v1 trigger

- 성능 기준 미충족 (성능 비교 단계 fail) → DeployReviewPL이 verdict `FAIL` + root cause 1차 진단.
- root cause = code-level → DeveloperPL FIX (구현 lane 재진입).
- root cause = design-level (architecture / 성능 모델 결정) → ArchitectPL FIX (설계 lane 재진입).
- root cause = requirements-level (성능 기준 자체 재조정) → RequirementsPL FIX (요구사항 lane 재진입).
- root cause = cross-module (양 architect 의견 분열) → debate-protocol-v1 자동 발동 (ADR-059, multi-round adversarial debate).
- ArchitectPL 최종 판정 (DeveloperPL 1차 진단 받은 후) — ADR-035 정합.

### §결정 6 — 검증 매커니즘 selection (HTTP vs WebSocket·daemon)

- **HTTP shadow** = REST/GraphQL/gRPC API endpoint 보유 service (예: `mctrader-web`). production 트래픽 mirror.
- **WebSocket·daemon 대기 mode** = WebSocket / 시세 수집 daemon / 백그라운드 worker (예: `mctrader-market`, `mctrader-market-bithumb`, `mctrader-engine`). active connection 안정성 + 메시지 throughput 측정.
- consumer 가 service 별 검증 mode 명시 의무 (`project.yaml deploy.services[].verification_mode: http | websocket | daemon` — ADR-027 Amendment N).

### §결정 7 — wrapper / lane plugin 자체 self-application = N/A

- ADR-087 §결정 6 precedent 정합 — wrapper / lane plugin = deploy lane spawn N/A, 본 Deploy Review lane spawn 도 N/A.
- ProductionEvidenceDeputy wrapper-self-app N/A (CFP-954 precedent) = 본 lane 이관 후에도 보존.

### §결정 8 — Lane spawn evidence 의무 (declaration-only Wave 1)

- Story §14 Lane Evidence 표에 `deploy-review` row append 의무 (ADR-031 lane-evidence-check.yml extension).
- `mechanical_enforcement_actions: [deploy-review-lane-spawn-evidence]` declaration-only Wave 1.
- Bypass = `hotfix-bypass:deploy-review-lane-spawn` label.


## 해소 기준

N/A — permanent policy

## 결과

### Cascade trigger chain

```
Epic close
  ↓
auto-deploy.yml (ADR-026 Amendment N + ADR-087)
  ↓
DeployPLAgent spawn (배포 lane) — 변경 repo enumeration + blue-green sequence
  ↓
green 컨테이너 healthcheck PASS
  ↓
DeployReviewPLAgent spawn (배포 리뷰 lane, 본 ADR) — smoke + 성능 비교
  ↓
verdict: PASS → atomic swap trigger → blue 3-시간 보존
verdict: FAIL → 자동 rollback + FIX dispatch (debate-protocol-v1 가능)
  ↓
atomic swap 후 cutover 사후 검증 (3-시간 동안 active monitoring)
```

### Self-application bootstrap mitigation (ADR-082 §결정 2 정합)

본 ADR-088 작성 evidence:

- ADR-RESERVATION row 88 = CFP-1059 active (commit `2104183`)
- ADR-087 sibling carrier file 생성 확인 (본 commit batch 이전 step)
- ADR-72 본문 = Amendment N 미적용 baseline (Amendment N 추가 = Task 12 영역, 본 Story-1 별 commit)

## 관련 파일

- [ADR-087](ADR-087-deploy-lane-and-lifecycle-extension.md) — sibling carrier (Deploy lane)
- [ADR-72](ADR-72-production-evidence-deputy-and-epic-cutover-gate.md) — Amendment N (ownership 이관 mirror)
- [ADR-014](ADR-014-operational-risk-ssot-distribution.md) — Amendment N (DeployReviewPL boundary)
- [ADR-042](ADR-042-agent-model-selection-policy.md) — Amendment 9 (DeployReviewPL Opus + DeployReviewWorker Sonnet)
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — I-5 (성능 측정 dimensional empirical grounding)
- [ADR-059](ADR-059-debate-protocol-v1.md) — 성능 미충족 시 cross-module debate trigger
- [ADR-089](ADR-089-schema-change-7-principles.md) — sibling carrier (양방향 smoke 검증 anchor)
- [ADR-090](ADR-090-cross-layer-reference-policy.md) — sibling carrier
- `templates/github-workflows/bidirectional-smoke.yml` (Phase 1 skeleton)
- `skills/deputy-mandate/SKILL.md` — ProductionEvidence ownership 이관 mirror cross-ref
