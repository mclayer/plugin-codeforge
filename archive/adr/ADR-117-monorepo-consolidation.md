---
adr_number: 117
title: codeforge 모노레포 통합 — 8 lane repo wrapper 흡수 + 9-plugin 정체성 유지
status: Accepted
category: architecture
date: 2026-06-11
carrier_story: CFP-2152
is_transitional: false
amends: null
supersedes: null
related_adrs:
  - ADR-063  # marketplace atomic invariant — source 필드 github-repo → git-subdir Amendment 는 S5 carrier 로 deferred
  - ADR-088  # ProductionEvidence ownership — S4 원본 판정 근거
  - ADR-016  # marketplace 등록 규칙 — S5 에서 적용
  - ADR-037  # version bump 규칙 — S5 에서 적용
---

# ADR-117: codeforge 모노레포 통합 — 8 lane repo wrapper 흡수 + 9-plugin 정체성 유지

- **Epic**: mclayer/plugin-codeforge#2151 / **carrier Story**: CFP-2152 (S1 토대)
- **spec SSOT**: `mclayer/codeforge-internal-docs` `wrapper/specs/2026-06-11-monorepo-consolidation-design.md` (사용자 승인 2026-06-11)

## 맥락 — 측정된 문제

codeforge 는 wrapper + 8 lane plugin 이 각각 전용 repo 를 갖는 9-repo 분산 구조였다. 2026-06-11 전수 인벤토리 (5축 병렬 실측):

- 8 lane repo 실질 내용 = 에이전트 정의 43 + 정형 CI 21, 합계 **190 파일 / 1.7 MB** (repo 당 평균 24 파일).
- 분리 구조 기인 유지 기계: strict 검사 스크립트 16 + lib 4, contract mirror 15파일, 9-repo branch protection 수동 관리.
- 마찰 실측: 분리 기인 hotfix-bypass 누적 strict 109회 (marketplace 계열 포함 229회). 분리 기인 evidence 검사 9개 중 6개 workflow 부재 stale dead.
- 부분 설치 실현 = deploy/deploy-review opt-in 1건뿐 — 분산 구조의 전제 (독립 소비) 미성립, 사실상 distributed monolith.
- 플랫폼 제약 없음: 단일 repo 다중 plugin = marketplace `git-subdir` source 공식 지원, lane hooks 0.

## 결정 (Epic 차원 — D1~D7)

| # | 결정 | 근거 |
|---|---|---|
| D1 | lane repo 8개 = GitHub **archive** (삭제 금지) | 이력·이슈 보존, 가역성 |
| D2 | git 이력 **보존** 흡수 (subtree, `--squash` 회피) | blame/조사 연속성 |
| D3 | 디렉터리 = `plugins/<정식 plugin name>/` | plugin.json `name` 1:1, 모호성 0 |
| D4 | spawn 식별자·plugin name/version 무변경 | 소비자 (mctrader) 영향 0 — agent 네임스페이스는 plugin name 기준 |
| D5 | contract canonical↔mirror 이중체계 폐지 → 단일 원본 | open #2141 은 대상물 소멸로 흡수·close (S2) |
| D6 | ADR 예약 2건 = 본 ADR-117 (신규) + ADR-063 Amendment (source 필드 형식, **S5 carrier**) | family scope 9-plugin 불변 → Amendment 로 충분 |
| D7 | walk_plan.py TOPOLOGICAL_ORDER 순서값 불변, walk *경로*만 단일 repo 화 | 순서 SSOT 동결 위반 방지 (S4) |

### 이행 순서 — 3 Phase / 6 Story

| Phase | Story | 내용 | 게이트 |
|---|---|---|---|
| 1 흡수 | S1 (CFP-2152) | 8 lane subtree 이력보존 흡수 → `plugins/` | dry-run path 충돌 0 (진입 차단 게이트) |
| 1 | S2 | contract mirror 단일화 + MANIFEST 재작성 + #2141 close | S1 후 (S3 과 병렬 가능) |
| 1 | S3 | 분리기인 CI/script 소멸 + lane workflows 정리 + `plugins/` lint 격리 재평가 | S1 후 |
| 1 | S4 | walk_plan 단일-repo 재설계 + ProductionEvidenceDeputy 원본 판정 (ADR-088 기준) | S3 후 권장 |
| 2 게이트 | S5 | marketplace source `git-subdir` 교체 + version bump + ADR-063 Amendment + `/plugins update` 실측 | 실패 시 정지 무해 (lane repo 생존) |
| 3 은퇴 | S6 | lane repo 8 archive + branch protection 9→1 + label/PAT 정리 | **S5 실측 통과 = hard gate (비가역 구간)** |

## S1 설계 결정 (DD-1~DD-7) — 전부 dry-run 실측 근거

설계 lane 이 2026-06-11 scratch dry-run (wrapper base `2deaac1f` = 당시 origin/main, 8 lane HEAD pin) 으로 실측 후 확정:

1. **DD-1 흡수 명령** = `git subtree add --prefix=plugins/<plugin name> <lane HEAD SHA>` (`--squash` 금지). 실측: 8/8 충돌 0, merge commit 8 + lane commit 368 유입, **tree SHA 8/8 lane 원본과 IDENTICAL** (무변경 이동 증명), 8 lane root commit 전부 상이 (이력 독립 — SHA graft 이슈 부재).
2. **DD-2 2-PR 구성**: PR-A (선행) = 본 ADR + CI scope guard 2파일 → PR-B (후행) = 순수 흡수 add-only. 단일 PR 은 "흡수 PR = `plugins/**` 만 신규" AC 가 기계적으로 깨짐.
3. **DD-3 `plugins/` CI 격리 구역**: full-tree 스캐너 2종 (`scripts/check-markdown-links.py`, `scripts/lib/check_adr_citation_slug.py` EXCLUDE_DIRS) 에서 `plugins/` 제외. 실측: guard 부재 시 lane 잔여물이 broken link 38건 + 인용 위반 16건 유발, guard 적용 시 전부 PASS + `--self-test` PASS. lane 콘텐츠는 비수정 (정리·재평가 = S3).
4. **DD-4 이력 보존 검증 명령**: subtree merge 경계에서 `git log -- <새 경로>` 는 흡수 commit 1건만, `--follow` 는 0건 반환 (실측). 유효 검증 = (a) lane HEAD `git merge-base --is-ancestor` ×8, (b) `rev-list --count` delta = lane commit 총수 + 8, (c) `git blame` 이 lane 시절 commit 을 원경로와 함께 귀속 (실측: `75fe11b` 2026-04-29).
5. **DD-5 merge 방식 통제**: 흡수 PR 은 **merge-commit 방식만** (`gh pr merge --merge`). squash = 이력 collapse, rebase = merge 평탄화. repo 설정 실측 3방식 모두 허용 상태 → 절차 통제 의무 (repo 설정 재편은 S6).
6. **DD-6 rollback**: merge 전 = branch 폐기 / merge 후 = `git revert -m 1` ×8 역순. S6 전 전 구간 lane repo 원본 생존 = 완전 가역.
7. **DD-7 PR 원자성**: 8 merge commit × 단일 흡수 PR — 8-PR 분할은 main 에 부분 흡수 창을 노출하므로 기각.

부수 실측 사실: lane test repo 에 `§` 포함 파일명 3건 존재 → 검증 명령은 `git -c core.quotepath=false` 의무. GitHub Actions 는 루트 `.github/workflows/` 만 실행하므로 `plugins/<name>/.github/workflows/` 는 무해 잔존 (정리 = S3).

## 결과

- **소비자 영향 0**: 9 plugin 매니페스트·name/version·spawn 식별자 불변. S5 전까지 marketplace view 자체가 불변.
- wrapper 는 S1 직후 `plugins/` 하위에 8 lane 트리 + 그 전체 이력 (368 commits) 을 보유. blame/조사 연속성 확보.
- cross-repo 유지 기계 (strict 검사·mirror·9-repo protection) 는 S2~S6 에서 단계 소멸.
- 비가역 작업 (archive·protection 해체) 은 S5 `/plugins update` 실측 hard gate 뒤에만 진입.

## 실행 참조

- S1 실행 절차·검증 스크립트 SSOT: `mclayer/codeforge-internal-docs` `wrapper/change-plans/cfp-2152-monorepo-absorption.md`
- Story file: 동 repo `wrapper/stories/CFP-2152.md`
