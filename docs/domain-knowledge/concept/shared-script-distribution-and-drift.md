---
kind: concept_definition
type: domain-knowledge
slug: shared-script-distribution-and-drift
title: 공유 스크립트 배포·동기화 (shared script distribution) 와 vendoring drift
status: Active
updated: 2026-08-15
carrier_story: CFP-2978
author: ResearcherAgent
related_adrs:
  - ADR-176  # consumer 배포 자산 currency 축 — 본 concept 의 배포·강제 2축 어휘를 소비하는 carrier (CFP-2978)
  - ADR-076  # 선언적 reconciliation upgrade flow — L128 이 regen-agents.sh `cp -n`(no-clobber) 의 갱신 불가를 기록
tags:
  - vendoring
  - drift
  - shared-script
  - distribution
  - pin
sources:
  - https://nesbitt.io/2026/02/10/lockfiles-killed-vendoring.html        # vendoring drift 업계 관측
  - https://docs.github.com/en/get-started/using-git/about-git-subtree-merges  # subtree = 자동 sync 아님
  - https://git-scm.com/book/en/v2/Git-Tools-Submodules                  # submodule 마찰
  - https://pip.pypa.io/en/stable/topics/vcs-support/                    # pip VCS pinning
  - https://packaging.python.org/en/latest/guides/hosting-your-own-index/  # 사설 index
  - https://docs.github.com/actions/creating-actions/sharing-actions-and-workflows-with-your-organization  # action 공유·scoped token
  - https://github.com/Redocly/repo-file-sync-action                     # 파일 싱크 봇
---

# 공유 스크립트 배포·동기화 (shared script distribution) 와 vendoring drift

## 정의

- **vendoring**: 외부(또는 형제 repo) 코드를 자기 repo 에 사본으로 복사해 두는 방식. 사본은 원본과 링크가 없어 갱신은 전적으로 사람 손에 의존한다.
- **drift**: 정본(SSOT)과 사본 사이에 시간이 지나며 누적되는 내용 격차. 업계 관측 — "대부분의 팀은 vendored 코드를 최신으로 유지할 규율이 없고, 조용히 stale 해지다가 CVE 6버전 뒤에서 발견된다" [nesbitt.io 2026](https://nesbitt.io/2026/02/10/lockfiles-killed-vendoring.html).
- **배포 채널 vs 강제 채널 분리**: 스크립트를 *어떻게 나르느냐*(배포)와 *격차가 생겼을 때 어떻게 검출·차단하느냐*(강제)는 별개 축. 손복사는 두 축 모두 부재.
- **pin**: 사본/참조가 정본의 어떤 버전(커밋 SHA·태그)에 대응하는지의 기계 판독 가능한 기록. pin 이 없으면 drift 는 비가시.

## 컨텍스트

codeforge wrapper 는 검사·훅 스크립트의 정본을 자기 repo 에 두고, consumer 프로젝트에는 그 사본을 배치하는 구조다. CFP-2978 에서 이 구조의 실패가 실물로 관측됐다 — wrapper 정본 `scripts/lib/check_parallel_work_sentinel.py` 가 consumer 4곳에 손복사된 뒤 CFP-2451 세대에서 동결된 채 정본만 전진했고, 사본은 판별력을 잃은 상태로 착수 통행증을 계속 발급했다 (상세 = [ADR-176](../../../archive/adr/ADR-176-consumer-asset-currency-and-exit-contract.md) §컨텍스트).

이 실패는 "복사를 안 했다"가 아니라 **배포 채널과 강제 채널을 모두 손절차에 맡긴 결과**다. 본 concept 은 그 두 축의 값 공간(배포 패턴 6종)과 이 org 유형에 적용할 때의 물리적 제약을 정리해, 설계가 선택지를 오해 없이 비교할 수 있게 하는 데 목적이 있다. 어느 패턴을 채택할지는 본 문서가 결정하지 않는다 (설계 lane 소관 — §경계).

## 핵심 규칙

- **R-1 배포 ⊥ 강제**: 배포 채널을 고른다고 강제 채널이 따라오지 않는다. 예 — git subtree 는 사본 갱신 수단을 주지만 "자동으로 upstream 과 sync 되지 않음"이 공식 문서의 명시 사실 ([GitHub Docs](https://docs.github.com/en/get-started/using-git/about-git-subtree-merges)). 배포 패턴 선정 시 검출·차단 채널을 별도로 지정해야 한다.
- **R-2 pin 부재 = drift 비가시**: 사본이 정본의 어느 버전에 대응하는지 기계 판독 가능한 기록이 없으면 격차는 관측 자체가 불가하다(§정의 pin). 따라서 "복사했다"는 사실은 최신성의 증거가 되지 못한다.
- **R-3 pin 대상이 브랜치면 drift 재발**: 참조를 SHA/태그로 고정해야 격차가 고정되며, 그 대가로 bump 절차가 필요해진다 (§경계 3번째 항목).

### 패턴 6종 요약 (외부 표준 근거)

| 패턴 | 1줄 정의 | 핵심 외부 사실 |
|---|---|---|
| vendoring(손복사) | 사본 복사, 링크 없음 | drift 필연 — lockfile+checksum DB 가 업계 대체재 ([nesbitt.io](https://nesbitt.io/2026/02/10/lockfiles-killed-vendoring.html)) |
| git subtree | 사본 + 이력 병합, `git pull -s subtree` 로 갱신 | "자동으로 upstream 과 sync 되지 않음" ([GitHub Docs](https://docs.github.com/en/get-started/using-git/about-git-subtree-merges)) |
| git submodule | 커밋 SHA pointer, 사본 없음 | clone 시 빈 디렉터리·detached HEAD 등 마찰 문서화 ([git-scm book](https://git-scm.com/book/en/v2/Git-Tools-Submodules)); Dependabot `gitsubmodule` ecosystem 이 bump PR 자동화 ([GitHub Docs](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories)) |
| 패키지 배포 | pip `git+https@<ref>` 또는 사설 index, uv 는 PEP 723 단일파일 지원 | pip VCS pinning 공식 지원 ([pip docs](https://pip.pypa.io/en/stable/topics/vcs-support/)); 사설 index 는 정적 파일 서버로도 가능 ([PyPA](https://packaging.python.org/en/latest/guides/hosting-your-own-index/)) |
| composite action / reusable workflow | 검사 로직을 action/workflow 로 패키징, `@<ref>` 참조 | private repo 라도 같은 org 내 공유 GA ([changelog 2022-12](https://github.blog/changelog/2022-12-13-github-actions-sharing-actions-and-reusable-workflows-from-private-repositories-is-now-ga/)); runner 가 1시간짜리 scoped read token 으로 action repo 를 자동 다운로드 ([GitHub Docs](https://docs.github.com/actions/creating-actions/sharing-actions-and-workflows-with-your-organization)) |
| 파일 싱크 봇 | 정본 push 시 대상 repo 에 PR 자동 개설 | repo-file-sync-action 등, PAT 필요 ([Redocly/repo-file-sync-action](https://github.com/Redocly/repo-file-sync-action)) |

## 경계

- **In scope**: 공유 스크립트의 배포 패턴 값 공간(6종) + drift 의 정의·가시성 조건(pin) + 이 org 유형(Team 플랜 · private consumer repo)에 적용할 때의 제약.
- **Out of scope**: 어느 패턴을 채택할지의 결정 및 그 기계 강제 설계 (설계 lane / ADR 소관 — 본 concept 은 선택지의 제약 조건만 제공). 특정 자산의 currency 판정 요건·신뢰경계 = ADR-176 소관.
- **Anti-pattern**: ① 배포 채널 도입을 강제 채널 확보로 계상 (R-1) ② pin 없는 사본을 "최신"으로 단정 (R-2) ③ 브랜치 pin 을 고정으로 계상 (R-3).

### 경계 조건 (이 org 유형에 적용 시)

- `GITHUB_TOKEN` 은 해당 repo 단일 scope — cross-repo private checkout/dispatch 는 PAT 또는 GitHub App 필요 ([community #46566](https://github.com/orgs/community/discussions/46566)).
- org-level "require workflows to pass" ruleset 은 Enterprise 플랜 전용 ([github.blog](https://github.blog/enterprise-software/ci-cd/enforcing-code-reliability-by-requiring-workflows-with-github-repository-rules/)) — Team 플랜 org 는 중앙 강제 불가, repo 별 required check 등록만 가능.
- reusable workflow 참조는 SHA/태그/브랜치 — pin 을 브랜치로 두면 drift 재발, SHA/태그로 두면 bump 절차가 필요 (Dependabot `github-actions` ecosystem 이 bump 자동화 후보 — private action 대상 동작 여부는 별도 확인 필요).

## 관련 ADR

- **ADR-176** — consumer 배포 자산 currency 축 (Proposed, carrier CFP-2978). 본 concept 의 "배포 ⊥ 강제" 2축과 pin 정의를 소비해 currency 판정 요건(pin / 2분할 질의 / UNDECIDABLE≠PASS / blob SHA 비교자)을 규정한다. 개념 정의 = 본 문서, 판정 규범 = ADR-176.
- **ADR-076** — 선언적 reconciliation upgrade flow SSOT. L128 이 `regen-agents.sh` = agent md `cp -n`(no-clobber) 라 "wrapper 변경분 자동 propagate **불가**"임을 이미 기록했다 — 손복사 경로의 drift 가 이 repo 에서 문서화된 최초 지점이며, 대안 규정은 ADR-176 이 수령했다.

## 변경 이력

| 일자(KST) | Story | 변경 |
|---|---|---|
| 2026-08-15 | CFP-2978 | 신규 — 배포 패턴 6종 + drift/pin 정의 + 이 org 유형 경계 조건 정리 (ResearcherAgent 저작). concept doc schema(frontmatter 필수 5필드 + 필수 6섹션) 정합 배치. |
