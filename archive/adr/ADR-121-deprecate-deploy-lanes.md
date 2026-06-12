---
adr_number: 121
title: "deprecate-deploy-lanes — codeforge-deploy / codeforge-deploy-review 2 lane 폐지 + 배포 완전 위임 (consumer GitHub Actions + Environments dev/stg/prd)"
status: Accepted
category: lifecycle
date: 2026-06-13
carrier_story: CFP-2218
parent_epic: "mclayer/plugin-codeforge#2217"
supersedes: [ADR-087, ADR-088]
amends: null
amendments: []
related_stories:
  - CFP-2218  # 본 ADR 신설 carrier (Epic CFP-2217 S1)
related_adrs:
  - ADR-023  # §결정 2 Deprecate 7-step 절차 SSOT — 본 폐지가 따르는 절차 (§결정 D 매핑 표)
  - ADR-087  # 폐지 대상 #1 — Deploy lane (→ Superseded by 본 ADR)
  - ADR-088  # 폐지 대상 #2 — Deploy Review lane (→ Superseded by 본 ADR)
  - ADR-026  # Amendment 6 §결정 8 "Epic close → Deploy trigger hook" — lane 폐지로 무효화 (본 ADR 은 충돌 식별·박제만, Amendment = Wave 2/후속 — §결정 E)
  - ADR-042  # Amendment 9 — DeployPL/DeployWorker/DeployReviewPL/DeployReviewWorker 4 agent tier entry — lane 폐지 시 deprecated (roster 정리 = Wave 2 — §결정 E)
  - ADR-105  # auto-rollback 재정의 — ADR-087 §결정 5 blue-green/3h 보존 anchor 직접 계승 → anchor 소실 (재정의 또는 consumer 자율 환원 = Wave 2/후속 — §결정 E)
  - ADR-106  # 운영 metric → PMOAgent input 회로 — deploy-review 성능 verdict 소실과 연결 (소실 수용 — §결정 6/§결정 E)
  - ADR-089  # schema 변경 7원칙 — 존치 (배포 매커니즘 독립, consumer migration 순서 가이드에 존속 — §결정 E)
  - ADR-063  # marketplace atomic invariant — Wave 2 (S5) entry 2건 제거 시 sync PR 선행 merge 의무 (cross-ref only)
  - ADR-054  # doc-only 판정 — 본 carrier = 신규 ADR 포함 full-lane (단일 product PR, Phase 1/2 분리 없음)
related_files:
  - archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md
  - archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md
  - archive/adr/ADR-023-lane-plugin-lifecycle.md
  - plugins/codeforge-deploy/  # Wave 2 (S5) 물리 제거 대상 — 본 ADR 시점 touch 0
  - plugins/codeforge-deploy-review/  # Wave 2 (S5) 물리 제거 대상 — 본 ADR 시점 touch 0
  - docs/inter-plugin-contracts/deploy-output-v1.md  # S2 Deprecated → Wave 2 삭제
  - docs/inter-plugin-contracts/deploy-review-output-v1.md  # S2 Deprecated → Wave 2 삭제
  - .github/workflows/phase-gate-mergeable.yml  # Wave 2 (S6) — deploy lane presence 검사 제거 + protection 5-tuple atomic
mechanical_enforcement_actions: []  # Wave 1 declarative-only — 물리 제거 / branch protection 전환 = Wave 2 (S5/S6) 별 carrier
wave_2_wire_carrier: "Epic #2217 S5 (물리 제거 — sunset gate 경과 실측 후) + S6 (정합 연쇄 — CLAUDE.md 8→6 lane + branch protection 6→5-tuple atomic)"
is_transitional: false
---

# ADR-121: deprecate-deploy-lanes — deploy / deploy-review 2 lane 폐지 + 배포 완전 위임

## 상태

Accepted (2026-06-13 KST, CFP-2218 carrier — Epic [#2217](https://github.com/mclayer/plugin-codeforge/issues/2217) S1). `is_transitional: false` — 영구 폐지 결정 기록.

## 본질 선언

> **codeforge 가 직접 수행하던 배포 (blue-green / atomic swap / 3시간 보존 / 자동 rollback — ADR-087) 와 배포리뷰 (성능 측정 / cutover 사후 검증 — ADR-088) 를 폐지하고, 배포를 consumer repo 의 GitHub Actions + GitHub Environments (dev/stg/prd) 에 완전 위임한다.** 본 ADR 은 폐지 **결정의 박제** (ADR-023 §결정 2 step 3) — 물리 제거는 sunset date 경과 후 Wave 2 (Epic #2217 S5/S6) 가 수행한다.

## 컨텍스트

- **사용자 요구 원문 취지** (Epic #2217 §why, 2026-06-13 KST): "dev/stg/prd 환경으로 나눠 배포 필요. 이건 GitHub 이 잘하는 일 — deploy 자체를 GitHub 에 위임하자." Orchestrator 가 하이브리드(실행만 위임) / 완전 위임 2안 제시 → 사용자 **완전 위임** 선택.
- **실전 미투입 실측**: deploy lane (ADR-087) / deploy-review lane (ADR-088) = 실측 0회. ADR-087 `[empirical-source: TBD]` 미해소 3개소 (healthcheck 60s / drain 30s·300s / retention 3h) + 산출물 계약 2종 (deploy-output-v1 / deploy-review-output-v1) placeholder 0.1. 전환 비용이 지금 최소. `verified-via` Epic #2217 §why + spec `wrapper/specs/CFP-2217.md` §1.
- **근본 동기**: 배포 자동화 오버엔지니어링 회피 + 유지보수 부채 경감.

## 결정 (확정 결정 8개 — spec §2 verbatim)

> 아래 1~8 = Epic spec (`codeforge-internal-docs` `wrapper/specs/CFP-2217.md` §2, status: confirmed) 확정 결정 verbatim. `verified-via` spec §2 direct read (2026-06-13 KST).

1. codeforge-deploy + codeforge-deploy-review **양 lane plugin 폐지** — ADR-023 §결정 2 4-step (CFP Story + 최소 1개월 deprecation period + ADR-NNN-deprecate 신설 + marketplace removal) 준수
2. 배포 = consumer repo GitHub Actions + GitHub Environments(dev/stg/prd) 단독. stg→prd = required reviewers 승인 게이트. **mclayer org = enterprise plan 실측 확인** (`gh api orgs/mclayer` → plan.name: enterprise; GitHub Docs 기준 Free/Pro/Team 은 private repo required reviewers 불가 — Enterprise 라 가용)
3. wrapper 제공물 = consumer 위임 템플릿만 (workflow seed + Environments 설정 가이드 + post-deploy smoke job)
4. **GitOpsAgent 병합 비채택** — GitOpsAgent = git operations(branch tree/worktree/merge) 전담, 배포 권한 모델과 disjoint (docker/ssh 0, main push deny). ADR 에 비채택 결정 박제
5. ADR-087/088 → status Superseded. project-config-schema.md `deploy.*` 섹션 축소 재정의. 계약 2종(deploy-output/deploy-review-output) Deprecated → Wave 2 삭제
6. open Epic 처리: #1265 = "GitHub Actions 위임 도입" 재정의 / #1263·#1264 = 폐기 (폐지 대상 메커니즘 검증) — S1 ADR 명시
7. branch protection contexts 6-tuple → 5-tuple (`Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)` 제거) — workflow 제거와 **atomic** 처리 의무 (과거 stuck-"expected" 전 PR 머지 불능 선례)
8. 8 lane plugin family → 6 lane. smoke 검증 = consumer workflow post-deploy job 환원

> **정정 노트 (결정 1 의 "4-step" 표기)**: spec §2 결정 1 의 "ADR-023 §결정 2 4-step" 표기는 **spec 오류** — ADR-023 §결정 2 실측 = **7-step** (`verified-via git show origin/main:archive/adr/ADR-023-lane-plugin-lifecycle.md` §결정 2, 2026-06-13 KST). verbatim 보존 의무로 원문 유지, 실제 준수 절차는 §결정 D 의 7-step 매핑 표가 SSOT.

## 결정 A: D-day / sunset date — Wave 2 gate anchor

- **D-day** := 본 ADR 의 carrier PR 이 `mclayer/plugin-codeforge` main 에 **merge 된 일자** (KST, ISO 8601 `+09:00` 날짜 환산).
- **sunset date** := **D-day + 1 calendar month** (KST). 달력 월 가산 — 30일 고정 아님 (예: D-day 2026-06-13 → sunset 2026-07-13). ADR-023 §결정 2 step 2 "Deprecation period — 최소 1 month" 정합.
- **Wave 2 (S5 물리 제거) 선행 조건** = `현재 KST ≥ sunset date` 실측 gate. **단축 금지** (ADR-023 §결정 2 위반).
- **gate 판정 실측 명령** (Wave 2 worker SSOT):

```bash
# D-day 실측 (본 ADR carrier PR 의 mergedAt → KST 날짜 환산)
gh pr list --repo mclayer/plugin-codeforge --search "CFP-2218 ADR-121 in:title" --state merged --json number,mergedAt
# sunset = D-day + 1 calendar month. 현재 KST < sunset 이면 Wave 2 (S5) 진입 금지.
```

- 본 ADR 작성일 = 2026-06-13 KST. **당일 merge 시 D-day = 2026-06-13 / sunset = 2026-07-13** (merge 일이 다르면 위 실측 명령이 우선 — 작성일 표기는 참고값).

## 결정 B: GitOpsAgent 병합 비채택 (결정 4 심화 rationale)

사용자 원발화에 포함된 "GitOpsAgent 와 병합할까?" 제안은 **비채택** (Orchestrator 권고 + 사용자 합의):

| 축 | GitOpsAgent | 배포 실행 주체 |
|---|---|---|
| mandate | git operations 전담 — hierarchical branch tree / worktree lifecycle / sequential merge / FIX iteration 재구성 | 환경별 배포 실행 + 승인 게이트 |
| 권한 모델 | docker/ssh 권한 0 + main push deny | deploy secrets / 환경 격리 / production write |
| 결론 | 두 권한 모델이 **disjoint** — 병합 시 git 전담 agent 에 배포 권한이 유입되어 최소 권한 원칙 훼손. 배포 실행은 GitHub Actions (consumer 측) 가 담당하므로 codeforge agent 어디에도 배포 권한 불요 | — |

## 결정 C: 소실 수용 명시 (사용자 명시 수용 — Epic #2217 §why)

완전 위임으로 다음 3종 기능이 **소실되며, 사용자가 이를 명시 수용**했다 (2026-06-13 KST, AskUserQuestion "완전 위임" 선택):

1. **성능 자동 verdict** — deploy-review lane 의 latency p50/p95/p99 / throughput / error rate 자동 비교 판정 (ADR-088 §결정 2)
2. **FIX dispatch** — 성능 기준 미충족 시 root cause 1차 진단 + 구현/설계/요구사항 lane FIX 자동 회부
3. **debate-protocol-v1 trigger** — 성능 모델 결정 분열 시 cross-module adversarial debate 자동 발동 (ADR-059 연동)

GitHub native 등가물 없음 — smoke 검증만 consumer workflow post-deploy job 으로 환원 (결정 8). FAIL 시 workflow 실패 → promote 차단 → 사람 판단.

## 결정 D: ADR-023 §결정 2 7-step 매핑 (S1 이행분 vs Wave 2 잔여분)

ADR-023 §결정 2 Deprecate 의무 절차 = 7-step 실측 (`verified-via git show origin/main:archive/adr/ADR-023-lane-plugin-lifecycle.md` §결정 2). 본 Epic 의 step 매핑:

| step | ADR-023 §결정 2 내용 | 이행 시점 | 비고 |
|---|---|---|---|
| 1 | CFP Story 작성 (rationale / migration path / 영향 contract / 흡수 계획) | **S1 (본 Story CFP-2218)** | Epic CFP-2217 spec/plan + 본 Story §2 |
| 2 | Deprecation period — 최소 1 month | **S1 anchor 박제** (§결정 A) | 기간 경과 자체는 Wave 2 gate 에서 실측 |
| 3 | ADR-NNN-deprecate 작성 (supersedes 명시) | **S1 (본 ADR-121)** | frontmatter `supersedes: [ADR-087, ADR-088]` |
| 4 | Marketplace removal (entry 제거, ADR-016 sync) | Wave 2 (**S5**) | ADR-063 sync PR 선행 merge 의무 |
| 5 | Plugin repo 처리 — archive (delete X, git history 보존) | Wave 2 (**S5**) | 모노레포 (ADR-118 D3) 정합: `plugins/codeforge-deploy*/` 디렉터리 삭제 = git history 보존 충족 |
| 6 | Inter-plugin contract status `Active` → `Archived` | S2 (Deprecated 마킹) → Wave 2 (**S5** 삭제) | deploy-output-v1 / deploy-review-output-v1 |
| 7 | Wrapper update (CLAUDE.md composition map / 8→6 lane sequence) | Wave 2 (**S6**) | branch protection 6→5-tuple 과 atomic |

## 결정 E: 영향 ADR 5종 — 충돌 식별·박제 (본 ADR 은 수정 비대상)

아래 ADR 들은 본 폐지 결정과 충돌하거나 영향을 받는다. **본 ADR (S1) 은 식별·박제만** — 실제 Amendment / 제거는 Wave 2 (S6) 또는 후속 CFP carrier.

| ADR | 충돌 지점 | 처분 방향 |
|---|---|---|
| ADR-026 | Amendment 6 §결정 8 "Epic close → Deploy trigger hook" (Epic Issue closed + `gate:retro-complete` → DeployPL spawn) — lane 폐지로 trigger 무효 | Wave 2: Amendment 또는 hook 제거 |
| ADR-042 | Amendment 9 — DeployPL(Sonnet)/DeployWorker(Sonnet)/DeployReviewPL(Opus)/DeployReviewWorker(Sonnet) 4 agent tier entry | Wave 2: roster 에서 deprecated 정리 |
| ADR-105 | auto-rollback 재정의 — ADR-087 §결정 5 (blue-green + 3h 보존) 를 직접 제약으로 계승, anchor 소실 | Wave 2/후속: 재정의 또는 consumer 자율 환원 명시 |
| ADR-106 | 운영 metric → PMOAgent input 회로 — deploy-review 성능 verdict 소실과 연결 | §결정 C 소실 수용에 포섭 — 후속 carrier 에서 input source 재정의 |
| ADR-089 | schema 변경 7원칙 (expand→contract) | **존치** — 배포 매커니즘 독립 (spec §5). blue-green 폐지 후에도 consumer migration 순서 가이드 (S3) 에 존속 |

## 결정 F: open Epic issue 3건 disposition (박제 — 실 동작은 Epic close 시점)

| Issue | 처분 | 사유 |
|---|---|---|
| [#1263](https://github.com/mclayer/plugin-codeforge/issues/1263) (CFP-1245 Phase C — auto-rollback staged 검증) | **폐기 (close)** | 폐지 대상 메커니즘 (ADR-087 자동 rollback) 의 검증 Epic — 대상 소멸로 무효 |
| [#1264](https://github.com/mclayer/plugin-codeforge/issues/1264) (CFP-1245 Phase D — canary auto-promote 검증) | **폐기 (close)** | 동일 사유 |
| [#1265](https://github.com/mclayer/plugin-codeforge/issues/1265) (mctrader 배포 lane consumer adoption) | **재정의** | "GitHub Actions 위임 도입" 으로 scope 전환 — Epic CFP-2217 후속 연결 (close 아님) |

- **실행 시점**: 본 ADR 은 처분 결정의 **박제만** 수행. 실제 GitHub close / 재정의 코멘트 = **Epic CFP-2217 close 시점** (spec §4 AC-5 "Given Epic close" 기준 정합).

## 거부된 대안

### 대안 A: GitOpsAgent 병합 (배포 기능을 GitOpsAgent 에 흡수)

- 거부 사유: §결정 B — 권한 모델 disjoint. git 전담 agent 에 배포 권한 유입은 최소 권한 원칙 훼손. 사용자 원발화의 제안이었으나 Orchestrator 권고로 비채택 합의.

### 대안 B: 하이브리드 위임 (실행만 GitHub, verdict/FIX dispatch 는 codeforge 잔존)

- 거부 사유: 사용자가 완전 위임 명시 선택 (2026-06-13 KST). verdict/FIX dispatch 잔존 = deploy-review lane agent 유지 = 유지보수 부채 경감 목적 미달. 소실 3종은 §결정 C 로 명시 수용.

### 대안 C: 즉시 물리 제거 (deprecation period 생략)

- 거부 사유: ADR-023 §결정 2 step 2 "최소 1 month" 위반. consumer (mctrader) migration 시간 필요 — S3 템플릿 handoff 가 Wave 2 전 선행 의무 (spec §5).

## 결과

- deploy / deploy-review 2 lane = 본 ADR merge 시점부터 **deprecated** (신규 spawn 비권장, S2 에서 plugin CLAUDE.md deprecation 배너 + plugin.json PATCH bump).
- ADR-087 / ADR-088 = `status: Superseded by ADR-121` (frontmatter 단일 변경 — 본문 byte 무변경, 이력 보존).
- Wave 2 (S5/S6) 가 sunset gate 경과 후 물리 제거 + 정합 연쇄 (8→6 lane / protection 5-tuple atomic / ADR-026·042 정리) 수행.
- consumer 배포 = GitHub Environments dev(자동) → stg(자동 promote) → prd(required reviewers 승인) + post-deploy smoke job.

## 해소 기준

N/A — 영구 폐지 결정 기록. Wave 2 이행 추적 = Epic [#2217](https://github.com/mclayer/plugin-codeforge/issues/2217) (S5/S6) + §결정 A gate.

## 관련 파일

- [ADR-023](ADR-023-lane-plugin-lifecycle.md) — Deprecate 7-step 절차 SSOT
- [ADR-087](ADR-087-deploy-lane-and-lifecycle-extension.md) — 폐지 대상 #1 (Superseded)
- [ADR-088](ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — 폐지 대상 #2 (Superseded)
- `wrapper/specs/CFP-2217.md` + `wrapper/plans/CFP-2217.md` (internal-docs repo) — Epic spec / plan SSOT
