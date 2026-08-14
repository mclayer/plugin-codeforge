---
kind: concept_definition
slug: shared-script-distribution-and-drift
story: CFP-2978
date: 2026-08-15
author: ResearcherAgent
---

# 공유 스크립트 배포·동기화 (shared script distribution) 와 vendoring drift

## 정의

- **vendoring**: 외부(또는 형제 repo) 코드를 자기 repo 에 사본으로 복사해 두는 방식. 사본은 원본과 링크가 없어 갱신은 전적으로 사람 손에 의존한다.
- **drift**: 정본(SSOT)과 사본 사이에 시간이 지나며 누적되는 내용 격차. 업계 관측 — "대부분의 팀은 vendored 코드를 최신으로 유지할 규율이 없고, 조용히 stale 해지다가 CVE 6버전 뒤에서 발견된다" [nesbitt.io 2026](https://nesbitt.io/2026/02/10/lockfiles-killed-vendoring.html).
- **배포 채널 vs 강제 채널 분리**: 스크립트를 *어떻게 나르느냐*(배포)와 *격차가 생겼을 때 어떻게 검출·차단하느냐*(강제)는 별개 축. 손복사는 두 축 모두 부재.
- **pin**: 사본/참조가 정본의 어떤 버전(커밋 SHA·태그)에 대응하는지의 기계 판독 가능한 기록. pin 이 없으면 drift 는 비가시.

## 패턴 6종 요약 (외부 표준 근거)

| 패턴 | 1줄 정의 | 핵심 외부 사실 |
|---|---|---|
| vendoring(손복사) | 사본 복사, 링크 없음 | drift 필연 — lockfile+checksum DB 가 업계 대체재 ([nesbitt.io](https://nesbitt.io/2026/02/10/lockfiles-killed-vendoring.html)) |
| git subtree | 사본 + 이력 병합, `git pull -s subtree` 로 갱신 | "자동으로 upstream 과 sync 되지 않음" ([GitHub Docs](https://docs.github.com/en/get-started/using-git/about-git-subtree-merges)) |
| git submodule | 커밋 SHA pointer, 사본 없음 | clone 시 빈 디렉터리·detached HEAD 등 마찰 문서화 ([git-scm book](https://git-scm.com/book/en/v2/Git-Tools-Submodules)); Dependabot `gitsubmodule` ecosystem 이 bump PR 자동화 ([GitHub Docs](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories)) |
| 패키지 배포 | pip `git+https@<ref>` 또는 사설 index, uv 는 PEP 723 단일파일 지원 | pip VCS pinning 공식 지원 ([pip docs](https://pip.pypa.io/en/stable/topics/vcs-support/)); 사설 index 는 정적 파일 서버로도 가능 ([PyPA](https://packaging.python.org/en/latest/guides/hosting-your-own-index/)) |
| composite action / reusable workflow | 검사 로직을 action/workflow 로 패키징, `@<ref>` 참조 | private repo 라도 같은 org 내 공유 GA ([changelog 2022-12](https://github.blog/changelog/2022-12-13-github-actions-sharing-actions-and-reusable-workflows-from-private-repositories-is-now-ga/)); runner 가 1시간짜리 scoped read token 으로 action repo 를 자동 다운로드 ([GitHub Docs](https://docs.github.com/actions/creating-actions/sharing-actions-and-workflows-with-your-organization)) |
| 파일 싱크 봇 | 정본 push 시 대상 repo 에 PR 자동 개설 | repo-file-sync-action 등, PAT 필요 ([Redocly/repo-file-sync-action](https://github.com/Redocly/repo-file-sync-action)) |

## 경계 조건 (이 org 유형에 적용 시)

- `GITHUB_TOKEN` 은 해당 repo 단일 scope — cross-repo private checkout/dispatch 는 PAT 또는 GitHub App 필요 ([community #46566](https://github.com/orgs/community/discussions/46566)).
- org-level "require workflows to pass" ruleset 은 Enterprise 플랜 전용 ([github.blog](https://github.blog/enterprise-software/ci-cd/enforcing-code-reliability-by-requiring-workflows-with-github-repository-rules/)) — Team 플랜 org 는 중앙 강제 불가, repo 별 required check 등록만 가능.
- reusable workflow 참조는 SHA/태그/브랜치 — pin 을 브랜치로 두면 drift 재발, SHA/태그로 두면 bump 절차가 필요 (Dependabot `github-actions` ecosystem 이 bump 자동화 후보 — private action 대상 동작 여부는 별도 확인 필요).
