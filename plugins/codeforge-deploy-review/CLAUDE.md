# CLAUDE.md

> ⚠ **DEPRECATED (ADR-121, 2026-06-13 KST)** — 본 lane plugin 은 폐지 결정됨. sunset = **2026-07-13 KST** (이후 Wave 2 에서 물리 제거 — Epic #2217 S5/S6). 대체 경로 = consumer repo GitHub Actions + GitHub Environments (dev/stg/prd) 완전 위임. 상세: `archive/adr/ADR-121-deprecate-deploy-lanes.md`.

## 언어 정책

모든 응답·코드 주석·문서 작성에서 **한글을 주 언어로 사용**. 영어는 기술 용어·코드·고유명사 등 필요한 경우에만 사용. 한자(일본어·중국어 포함) 사용 절대 금지.

## Plugin identity

`codeforge-deploy-review` = codeforge family **배포 리뷰 (Deploy Review) lane plugin** (CFP-1059 / [ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md)). codeforge 6 → 8 lane 확장의 #7 배포 리뷰 lane. **production 환경 성능 측정을 1st-class 검증 phase 로 격상**.

본 plugin 은 **codeforge core (wrapper) 의존** — 단독 동작 불가. wrapper Orchestrator 가 DeployReviewPLAgent 스폰 + verdict 수령. SessionStart hook 이 codeforge core 설치 verify.

본 lane scope = **"한 번 끝나는 검증" 만** (smoke / 성능 비교 / cutover 사후 검증). 운영 phase (continuous monitoring — canary promote / rollback 신호 회수 / regression 감지 / channel drift / cutover monitoring 30일 / smoke ongoing) 와 disjoint — 운영 phase = 별 Epic carrier.

## Agent 2종 + 1 deputy

| Agent | Model tier | Mandate |
|---|---|---|
| **DeployReviewPLAgent** | **Opus** | production-grade 성능 측정 1st-class lead — smoke / 성능 비교 / cutover 사후 검증 verdict 종합. 성능 미충족 시 root cause 1차 진단 + debate-protocol-v1 cross-module trigger + 구현/설계/요구사항 lane FIX dispatch. adversarial debate 자동 발동 영역 (Opus tier mandatory) |
| **DeployReviewWorkerAgent** | opus | smoke test 실행 (HTTP shadow / WebSocket·daemon 대기 mode) + 성능 비교 baseline 수집 (latency / throughput / error rate / CPU·memory) + cutover 사후 검증 worker |
| **ProductionEvidenceDeputyAgent** | (CONDITIONAL deputy) | production cutover evidence quad (functional / security / monitoring / testing 4 source). ADR-72 이관 — codeforge-design CONDITIONAL → 본 lane 정식. production cutover-touching Story 시 spawn |

Agent model tier 정책 SSOT = [ADR-042 Amendment 9](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-042-agent-model-selection-policy.md) (DeployReviewPL opus / DeployReviewWorker opus). 전 에이전트 opus 단일 tier (ADR-141 — fallback 대상 없음). DeployReviewPL opus = 본 lane 이 adversarial debate 자동 발동 영역이므로 mandatory (ADR-042 §결정 1 정합).

## 8 lane composition 의 #7 배포 리뷰 lane

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포 → [배포 리뷰]
```

- **호출 시점**: 배포 lane (DeployPLAgent) 이 green 컨테이너 healthcheck PASS 후, atomic swap 직전 (검증 3종 시점 — ADR-088 §결정 3).
- **PASS 후**: DeployPLAgent 에 atomic swap 허용 신호 → blue 3-시간 보존.
- **FAIL 시** (ADR-088 §결정 5): code-level → DeveloperPL / design-level → ArchitectPL / requirements-level → RequirementsPL / cross-module → debate-protocol-v1 자동 발동.

## 검증 3종 (한 번 끝나는 — ADR-088 §결정 3)

| 검증 | 시점 | 매커니즘 |
|---|---|---|
| **smoke** | atomic swap 직전 (green healthcheck 후) | HTTP request shadow (production 트래픽 미러링) + WebSocket·daemon 대기 mode (대기 안정성) |
| **성능 비교** | atomic swap 직전 (smoke 통과 후) | latency p50/p95/p99 / throughput / error rate / CPU·memory baseline 대비 `[empirical-source: TBD]` |
| **cutover 사후 검증** | atomic swap 직후 ~ 3-시간 보존 종료 | 실 production 트래픽 error rate / latency 회귀 감지 + 사용자 영향 신호 |

검증 mode (ADR-088 §결정 6): HTTP shadow (REST/GraphQL/gRPC) / WebSocket·daemon 대기 (시세 수집 daemon / 백그라운드 worker). consumer 가 service 별 `project.yaml deploy.services[].verification_mode` 명시.

## 기존 review lane 과의 disjoint axis (ADR-088)

- **DesignReview** = ADR 정합 / 설계 보장성 (code/production-level 미접근)
- **CodeReview** = 구현 품질 (production runtime 측정 미접근)
- **SecurityTest** = code-level 보안 정합 (production 성능 측정 미접근)
- **IntegrationTest** = 시나리오 단위 정합 (production cutover 사후 검증 미접근)
- **Deploy Review (본 lane)** = production 환경 성능 측정 + cutover 사후 검증 — 위 4 review lane 모두와 disjoint axis

## ProductionEvidenceDeputy 이관 (ADR-088 §결정 4 / ADR-72 Amendment 4)

본 lane 정식 deputy. ownership = codeforge-design CONDITIONAL → codeforge-deploy-review 정식 이관 (CFP-1059 Story-3). mandate body = ADR-72 §결정 1-7 verbatim 유지 (이관은 parent_pl / ssot_position 만 변경). production cutover-touching Story 시 CONDITIONAL spawn. InfraOperationalArch (codeforge-design) 와 disjoint axis — policy SSOT (design-time) vs evidence SSOT (runtime).

## Self-write 책임

본 plugin agent 는 read-only 분석 + 성능 측정 (curl / docker) 만. `src/**` / `tests/**` / `docs/**` 직접 write 권한 없음. Story / Epic §14 Lane Evidence `deploy-review` row 갱신은 Orchestrator 가 처리 (ADR-088 §결정 8). 성능 미충족 FIX root cause 최종 판정 = ArchitectPL (DeveloperPL 1차 진단 후, ADR-035).

## §14 Lane Evidence 의무

매 배포 리뷰 lane spawn 시 Story / Epic §14 Lane Evidence 표에 `deploy-review` row append (ADR-031 lane-evidence-check.yml extension). `mechanical_enforcement_actions: [deploy-review-lane-spawn-evidence]` declaration-only Wave 1 (ADR-088 §결정 8). Bypass = `hotfix-bypass:deploy-review-lane-spawn` label.

## wrapper / lane plugin self-application = N/A (ADR-088 §결정 7)

ADR-087 §결정 6 precedent 정합 — wrapper / lane plugin = 배포 리뷰 lane spawn N/A. ProductionEvidenceDeputy wrapper-self-app N/A (CFP-954 precedent) = 이관 후에도 보존.

## 결정 원칙 + 시각 표시

codeforge [ADR-064](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-064-decision-principle-mandate.md) normative SSOT (4 어휘 anchor + forbid-list dictionary) + [ADR-079](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-079-kst-timestamp-display-mandate.md) KST `+09:00` ISO 8601 zoned 적용.

## 관련 ADR

- [ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — Deploy Review lane 신설 + ProductionEvidenceDeputy 이관 (본 plugin SSOT carrier)
- [ADR-087](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) — Deploy lane (직전 lane)
- [ADR-042 Amendment 9](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-042-agent-model-selection-policy.md) — DeployReviewPL opus + DeployReviewWorker opus (ADR-141 로 opus 단일 tier 통일)
- [ADR-72](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md) — ProductionEvidenceDeputy mandate (이관 후 본 lane deputy)
- [ADR-068](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-068-boundary-completeness-invariants.md) — I-5 dimensional empirical grounding (성능 측정 baseline TBD)
- [ADR-059](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-059-debate-protocol-v1.md) — 성능 미충족 cross-module debate trigger
- [ADR-035](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-035-fix-root-cause-final-decider.md) — root cause 최종 판정 = ArchitectPL
