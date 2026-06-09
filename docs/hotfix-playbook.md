# Hotfix Playbook (운영 장애 대응)

> **Source**: `docs/orchestrator-playbook.md` §10 에서 분리 (CFP-93, P2-9 follow-up — cognitive overhead reduction). mctrader debut audit 시점 까지 hotfix 사용 사례 0 — full 7-lane flow 가 default. 본 playbook = 첫 hotfix 발생 시 활성화.

> **ADR-039 적용 (CFP-275, 2026-05-08)**: 본 Hotfix 경로 (Minimal / Medium 양 경로) 도 Orchestrator subagent default 적용 — emergency hotfix 도 무조건 spawn, exception 없음 (사용자 verbatim "무조건"). Hotfix 의 fast-path 본질 (Phase skip / lane skip) 무변, mechanism 만 spawn 의무. 정책 SSOT [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) + normative SSOT [playbook §3.0](orchestrator-playbook.md).

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
 · CodebaseMapper·Refactor·SecurityArchitect·InfraOperationalArchitect·TestContractArch·ModuleArchitect deputy 생략, chief author 단독 (ArchitectPLAgent 검수 생략)
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

## 6. cross-repo land_order post-merge 경로 (CFP-795 / ADR-026 Amendment 4 §결정 6)

cross-repo Story (1 Story = N PR, mctrader Mode B hub-centralized) 의 land_order 후 발견된 **safe defect** (byte-equivalence INV 위반 등, 신규 코드·로직 0) 정정 전용 경로. §1 Minimal / §2 Medium 과 별 경로 — 운영 장애 adrenaline 없는 정정.

> **`post-merge-fix` ≠ `hotfix:minimal`**: 본 경로 = cross-repo land_order 정정 전용 (보안 non-touch 역참조 시 보안테스트 실질 N/A). `hotfix:minimal` = 운영 장애 단일 파일 수정 (설계리뷰 생략만, 보안테스트 필수). 두 경로 혼동 금지.

### 적용 조건 (3가지 모두 충족)

1. **cross-repo Story land_order 후** 발견된 defect (이미 정상 phase flow 로 land 된 PR 의 정정)
2. **safe defect** — 신규 코드·로직 0 (byte-equivalence revert, import 정리, lint fix 등)
3. **원 MERGED PR §7 보안 non-touch** — 정정 대상 원 PR 이 보안 영역 미접촉 (조건 3 양면 검증)

### 사용 절차 (Orchestrator 의무)

```
1. Orchestrator: hotfix PR body 에 기재
   story_uri: https://github.com/<hub-owner>/<hub-repo>/blob/main/<plugin>/stories/<KEY>.md
   corrects_pr: <owner>/<repo>#<N>  (정정 대상 원 MERGED PR)

2. Orchestrator: hub Story §10 FIX Ledger row append (fix-event-v1 monopoly, CFP-32)
   — 현재 hotfix PR 번호 포함 의무

3. Orchestrator: hotfix PR 에 post-merge-fix label 수동 부착
   — fix-event-v1 §10 row 작성과 동시 (label 먼저 단독 부착 금지)

4. CI: phase-gate-mergeable.yml 3-조건 AND 평가
   — 조건 1 (label) ∧ 조건 2 (hub §10 row binding + ALLOWED_HUB_REPOS strict match) ∧ 조건 3 (원 PR + hotfix 양면 SECURITY_PATHS non-match)
   — 전건 충족 시 fast-pass success (admin override 불요)

5. Merge 후: hub Story §10 row 에 hotfix 결과 기재 (Orchestrator monopoly)
```

### 재귀 hotfix depth 제한

hotfix-1 merge 후 bug 발견 → hotfix-2: hub Story §10 row chain depth ≤ 2 만 허용. depth > 2 → escalate 강제 (BLOCK). 재귀 hotfix 는 §1 Minimal 또는 §2 Medium 경로 재진입 권고.

### admin-override interim 경로 (정책 아님)

3-조건 AND 충족 불가 + 긴급 필요 시: admin-merge 를 **임시** 사용 가능. 단 사후 감사 §3 의무 적용 + hotfix-playbook §3 Audit Issue 소급 작성 의무. "admin override 정책화" = 불가 (`enforce_admins:true` invariant — ADR-024, CFP-70).

### consumer hub PAT scope

consumer hub repo 가 mclayer/codeforge-internal-docs 가 아닌 경우: 해당 consumer 측 `CODEFORGE_CROSS_REPO_PAT` 가 hub repo `contents:read` 보유 의무. consumer-guide §1g + ADR-066 PAT rotation policy 참조. `ALLOWED_HUB_REPOS` workflow env 에 consumer hub 추가 (overlay 확장 가능, 축소 불가 — ADR-026 Amd 4 §결정 6 (화이트리스트) + ADR-024 Amendment 2 §결정 A (확장-only 패턴) + ADR-116 (주입 mechanism)).
