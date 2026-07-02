# CLAUDE.md

> ⚠ **DEPRECATED (ADR-121, 2026-06-13 KST)** — 본 lane plugin 은 폐지 결정됨. sunset = **2026-07-13 KST** (이후 Wave 2 에서 물리 제거 — Epic #2217 S5/S6). 대체 경로 = consumer repo GitHub Actions + GitHub Environments (dev/stg/prd) 완전 위임. 상세: `archive/adr/ADR-121-deprecate-deploy-lanes.md`.

## 언어 정책

모든 응답·코드 주석·문서 작성에서 **한글을 주 언어로 사용**. 영어는 기술 용어·코드·고유명사 등 필요한 경우에만 사용. 한자(일본어·중국어 포함) 사용 절대 금지.

## Plugin identity

`codeforge-deploy` = codeforge family **배포 (Deploy) lane plugin** (CFP-1059 / [ADR-087](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md)). codeforge 6 → 8 lane 확장의 #6 배포 lane.

본 plugin 은 **codeforge core (wrapper) 의존** — 단독 동작 불가. codeforge wrapper 의 Orchestrator 가 DeployPLAgent 를 스폰하고 verdict 를 수령. SessionStart hook 이 codeforge core 설치 여부 verify (미설치 시 fail-fast + install 안내).

deploy lane scope = **consumer 의 application repo 배포 영역** (codeforge plugin marketplace publish 와 disjoint — ADR-063).

## Agent 2종

| Agent | Model tier | Mandate |
|---|---|---|
| **DeployPLAgent** | opus | 배포 매커니즘 실행 lead — Epic 묶음 단위 발동, 변경 repo enumeration, blue-green sequence orchestration, healthcheck 검증, atomic swap trigger, 3-시간 보존 timer, 자동 rollback 결정. DeployWorkerAgent spawn + verdict 종합 |
| **DeployWorkerAgent** | opus | 각 repo 배포 worker — 9-step 마이그레이션 sequence 실 실행. idempotent script + graceful shutdown + healthcheck poll + secret provider lookup (1Password Connect 또는 fallback) + reverse proxy label 갱신 (Traefik primary) |

Agent model tier 정책 SSOT = [ADR-042 Amendment 9](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-042-agent-model-selection-policy.md) (DeployPL opus / DeployWorker opus). 전 에이전트 opus 단일 tier (ADR-141 — fallback 대상 없음).

## 8 lane composition 의 #6 배포 lane

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → [배포] → 배포 리뷰
```

- **호출 시점**: consumer application repo 의 Epic 묶음이 통합테스트 / 보안테스트 통과 후 close → auto-deploy trigger (ADR-026 Amendment N + ADR-087 §결정 7). consumer `project.yaml deploy.enabled: true` 선언 시에만 활성 (default false, backward-compat).
- **PASS 후 다음 lane**: 배포 리뷰 lane (DeployReviewPLAgent — smoke / 성능 비교 / cutover 사후 검증, [ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md)).
- **FAIL 시**: healthcheck FAIL → 자동 rollback. 성능 미충족 (배포 리뷰 verdict FAIL) → 구현 / 설계 / 요구사항 lane back.

## 배포 매커니즘 (단일 — ADR-087 §결정 5)

blue-green + atomic swap + 3-시간 보존 + 자동 rollback. 9-step sequence (빌드 → expand migration → green start → 건강 확인 → 검증 → atomic swap → blue drain → 3-시간 보존 → 정리).

인프라 stack (wrapper-level primary, consumer override 가능):

| 영역 | Primary | Consumer override |
|---|---|---|
| 빌드 | GitHub Actions | consumer 자체 workflow |
| 저장 | Docker Hub | `project.yaml deploy.registry` (EC-7 self-hosted fork) |
| 배포 | SSH pull (다중 호스트) | — |
| 비밀 | 1Password Connect | `.env` + GitHub Actions secret fallback (EC-1) |
| traffic 분배 | Traefik (label-based) | nginx / Caddy / haproxy (EC-2, Wave 5+ abstraction) |

배포 단위 = repo (consumer 묶음 Epic 안 변경된 repo 만, ADR-087 §결정 3).

## Self-write 책임

본 plugin agent 는 read-only 분석 + 배포 매커니즘 실행 (docker / ssh / migration script) 만. `src/**` / `tests/**` / `docs/**` 직접 write 권한 없음. Story / Epic §14 Lane Evidence `deploy` row 갱신은 Orchestrator 가 처리 (ADR-087 §결정 8). GitHub Issue 코멘트는 wrapper Orchestrator 경유.

**consumer overlay schema authoring scope = wrapper SSOT 영역** (CFP-1317-S2 / ADR-068 I-4): `project.yaml deploy.*` schema 정의 = wrapper [`docs/project-config-schema.md` deploy 섹션](https://github.com/mclayer/plugin-codeforge/blob/main/docs/project-config-schema.md#deploy-섹션-설명-cfp-1059--adr-087--adr-088) 단일 SSOT. 본 plugin `templates/deploy-mechanism.md` = 9-step sequence + Edge Cases reference doc layer 만 (schema mirror 0건, drift 0 invariant).

## §14 Lane Evidence 의무

매 배포 lane spawn 시 Story / Epic §14 Lane Evidence 표에 `deploy` row append (ADR-031 lane-evidence-check.yml extension). `mechanical_enforcement_actions: [deploy-lane-spawn-evidence]` declaration-only Wave 1 (ADR-087 §결정 8). Bypass = `hotfix-bypass:deploy-lane-spawn` label.

## wrapper / lane plugin self-application = N/A (ADR-087 §결정 6)

- wrapper repo + lane plugin repo 자체의 release = marketplace publish (ADR-063 cover) — deploy lane spawn 미적용.
- consumer application repo (예: mctrader) 만 deploy lane 활성화.

## 결정 원칙

codeforge 의 모든 결정 제안 시점에 [ADR-064](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-064-decision-principle-mandate.md) normative SSOT 적용 (best-effort / broad coverage / full-scope / active amendment 4 어휘 anchor + forbid-list dictionary). 본 plugin 도 동일 적용.

## 시각 표시 정책 (KST, ISO 8601)

governance display layer 의 모든 시각 표기 = KST `+09:00` ISO 8601 zoned 강제 ([ADR-079](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-079-kst-timestamp-display-mandate.md)).

## 관련 ADR

- [ADR-087](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) — Deploy lane 신설 + lane lifecycle 6→8 (본 plugin SSOT carrier)
- [ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — Deploy Review lane (다음 lane)
- [ADR-042 Amendment 9](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-042-agent-model-selection-policy.md) — DeployPL/Worker opus tier (ADR-141 로 opus 단일 tier 통일)
- [ADR-023](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-023-lane-plugin-lifecycle.md) — lane plugin lifecycle
- [ADR-026](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-026-post-merge-automation.md) — Epic close → Deploy trigger
- [ADR-027](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-027-consumer-adoption-protocol.md) — project.yaml deploy.* schema
- [ADR-089](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-089-schema-change-7-principles.md) — expand-contract 마이그레이션 분리
- [ADR-068](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-068-boundary-completeness-invariants.md) — I-4 wording SSOT (CFP-1317-S2 plugin file d-B redirect 결정 근거) + I-5 dimensional empirical grounding (healthcheck window / graceful drain / retention period — wrapper ADR-087 §결정 5 본문 단일 anchor)
- [ADR-045](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-045-story-retro-mandatory-trigger.md) — §D-9 pattern_count 누적 escalation (mctrader#1272 (d) 6회째 declarative seed drift super-class evidence → S3 ADR-107 carrier)
- [ADR-013](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md) — dogfood-out family (Story file 위치 = `mclayer/codeforge-internal-docs/wrapper/stories/CFP-1317-S2.md`)
