# Hotfix Playbook (운영 장애 대응)

> **Source**: `docs/orchestrator-playbook.md` §10 에서 분리 (CFP-93, P2-9 follow-up — cognitive overhead reduction). mctrader debut audit 시점 까지 hotfix 사용 사례 0 — full 7-lane flow 가 default. 본 playbook = 첫 hotfix 발생 시 활성화.

> **ADR-039 적용 (CFP-275, 2026-05-08)**: 본 Hotfix 경로 (Minimal / Medium 양 경로) 도 Orchestrator subagent default 적용 — emergency hotfix 도 무조건 spawn, exception 없음 (사용자 verbatim "무조건"). Hotfix 의 fast-path 본질 (Phase skip / lane skip) 무변, mechanism 만 spawn 의무. 정책 SSOT [ADR-039](adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) + normative SSOT [playbook §3.0](orchestrator-playbook.md).

정상 7-레인 full flow 는 Story 1건당 반나절~수일 소요. 운영 장애로 즉시 대응 필요한 경우 아래 2 경로 중 하나 선택. **어느 경로든 사후 감사는 동일하게 수행**.

## 1. Minimal Path (`severity:bug` — 기본 hotfix)

단일 파일·함수 범위 버그 수정, 계획·리뷰 생략.

```
Orchestrator → (사용자 승인) → 관련 `role: dev` 에이전트 단독 → 수정 + 테스트 실행
 · Change Plan 생략 (Story Issue body 에 버그 근거 1-3줄만)
 · 설계 리뷰 생략, 구현 리뷰 생략
 · 구현 테스트 게이트는 유지 (TestAgent 기능 모드만, 성능 게이트 생략)
 · 보안 테스트는 Codex peer 만 실행 (credential/injection 스팟 체크 — Claude peer 생략)
 · GitHub 라벨: `type:bug` + `hotfix:minimal`
 · 단일 PR (Phase 1+2 분할 없이)
```

**적용 조건** (모두 충족):
- 변경 라인 수 ≤ 30
- 설계 결정 없음 (기존 인터페이스·계약 그대로)
- 단일 파일 수정
- 운영 장애 복구 목적 (사용자가 명시)
- **보안 경계 변경 없음** (auth·권한·trust boundary 미변경) — 있으면 Medium Path 강제

## 2. Medium Path (`severity:critical` — 심각 hotfix)

여러 파일 걸친 운영 장애, 설계·구현 리뷰 축약.

```
Orchestrator → (사용자 승인) → ArchitectAgent (chief author) 빠른 Change Plan (§1·§5·§8 축약) → DevPL 구현 → TestAgent → SecurityTestPL
 · CodebaseMapper·Refactor·SecurityArchitect·OperationalRiskArchitect·TestContractArch·DataMigrationArchitect deputy 생략, chief author 단독 (ArchitectPLAgent 검수 생략)
 · 설계 리뷰 생략
 · 구현 리뷰는 **Claude만** 실행 (Codex 생략 — 시간 절약)
 · 구현 테스트 게이트는 기능 + 성능 모두 수행
 · 보안 테스트는 Claude + Codex 둘 다 필수 (hotfix라도 보안 우회 금지)
 · GitHub 라벨: `type:bug` + `hotfix:critical`
 · 단일 PR
```

**적용 조건**: 사용자가 `severity:critical` 명시 + 운영 장애 복구 목적.

## 3. 사후 감사 (X 경로 — 양 hotfix 공통 의무)

Hotfix merge 완료 후 **next working session** 초두에 Orchestrator 가 자동 수행. **모든 step 의 mechanism = subagent spawn** (ADR-039 §결정 1 / §결정 6 — Hotfix 의 fast-path 본질 무변, mechanism 만 spawn 의무):

1. **Audit Issue 자동 생성**: Orchestrator 가 Audit Issue 생성 전용 delegate subagent spawn → spawn 된 delegate 가 GitHub Issue Forms (audit.yml) 기반 `mcp__github__issue_write` 호출. label `audit:post-hotfix` + `phase:요구사항` (Orchestrator-owned delegate semantics, ADR-039 §결정 3 + §결정 12 / ADR-031 Amendment 1)
2. **Change Plan 소급 작성**: Orchestrator → ArchitectAgent (chief author) spawn → hotfix 변경 diff 를 소급해 Change Plan 작성 (§1-10 전부, 단 실구현은 이미 존재 상태). ArchitectAgent self-write `docs/change-plans/` commit (CFP-26 owner direct write)
3. **구현 리뷰 소급**: Orchestrator → CodeReviewPL spawn → hotfix 변경사항 대상 소급 리뷰 (Claude + Codex worker subagent 병렬 spawn 모두)
4. **보안 테스트 소급** (Minimal Path 에서 Claude peer 생략한 경우에 한함): Orchestrator → SecurityTestPL spawn → hotfix 대상 보안 리뷰 전체 재수행
5. **ADR 영향 검토**: Orchestrator → ArchitectAgent (chief author) spawn → 변경이 ADR 결정을 위반/변경하는지 검토, 필요 시 ADR 갱신 (ArchitectAgent self-write `docs/adr/`)
6. Audit Issue 는 PR 없이 close 가능 (문서·ADR 갱신만 필요한 경우 → docs PR 1건으로 close — close 자체도 Orchestrator-owned delegate subagent 경유)

**사후 감사 생략 금지** — hotfix 는 "빠르게 대응 후 반드시 감사" 가 원칙.

## 4. 관련 문서

- [`docs/orchestrator-playbook.md`](orchestrator-playbook.md) §10 (entry pointer)
- [`CLAUDE.md`](../CLAUDE.md) §"레인 7개" — Hotfix 경로 예외 명시
- `audit:post-hotfix` label = label-registry-v1
- `hotfix:minimal` / `hotfix:critical` label = label-registry-v1

## 5. 활성화 trigger

- 첫 운영 장애 발생 시 본 playbook 채택
- mctrader debut audit (Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P2-9) 까지 사용 사례 0 — 본 playbook 은 dormant
