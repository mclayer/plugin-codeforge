---
adr_number: 17
title: Skill override path enforcement for codeforge dogfood artifacts
status: Accepted
category: Team & Process
date: 2026-05-01
related_files:
  - CLAUDE.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - scripts/check-dogfood-artifact-paths.sh
  - templates/github-workflows/dogfood-artifact-paths.yml
related_stories:
  - CFP-56
is_transitional: false
---

# ADR-017: Skill override path enforcement for codeforge dogfood artifacts

## 상태

Accepted (2026-05-01) — CFP-56 carrier. ADR-013 Amendment 1로 연결된다.

## 컨텍스트

CFP-55는 `dependencies` 필드 정책을 ADR-016 Amendment 1로 마무리하면서, "ADR-013 amend (skill override path lane 의무)"를 CFP-56 / ADR-017로 명시적으로 분리 보류했다. ADR-013과 `CLAUDE.md`는 이미 `superpowers:brainstorming` spec 저장 위치와 `superpowers:writing-plans` plan 저장 위치를 plugin repo의 `docs/superpowers/`가 아니라 `mclayer/codeforge-internal-docs/<plugin-folder>/{specs,plans}/`로 override해야 한다고 정한다. 그러나 현재 한계는 trust-based이다. Orchestrator가 path override를 잊으면 spec/plan이 plugin repo에 조용히 생성되고, PR에서 자동 차단되지 않는다.

## 결정

### 결정 1: 금지 경로

codeforge family plugin repo에서는 `docs/superpowers/specs/**`와 `docs/superpowers/plans/**`를 dogfood artifact 금지 경로로 정한다. 해당 산출물의 정식 위치는 internal-docs repo이다.

### 결정 2: CI 강제

각 plugin repo PR은 GitHub Actions에서 금지 경로를 검사해야 한다. 위반 시 PR check는 fail-closed 한다.

### 결정 3: 재사용 lint script

검사 로직은 `scripts/check-dogfood-artifact-paths.sh`에 둔다. workflow는 이 script를 호출만 하며, 기존 strict lint script 패턴을 따른다.

### 결정 4: DesignReviewPL 보조 감사

DesignReviewPL은 ADR-013/ADR-017 준수 여부를 감사 항목으로 유지한다. 단, 사람 감사는 CI를 대체하지 않는다.

### 결정 5: 허용 범위

ADR 문서, playbook, template 본문에서 금지 경로를 "문자열로 설명"하는 것은 허용한다. 실제 파일이 금지 디렉터리 아래 생성되는 것만 차단한다.

## 결과

긍정: skill default override 누락이 PR 단계에서 즉시 드러나며, ADR-013 dogfood-out 정책이 기계적으로 지켜진다.

부정: workflow template과 lint script를 7개 plugin repo에 배포해야 한다 (본 CFP 는 wrapper 만, lane 6 repo 는 후속 CFP).

Trade-off: pre-commit보다 늦게 실패하지만, 설치 여부에 의존하지 않는 CI가 authoritative control이 된다.

## 거부된 대안

- **E-A: DesignReviewPL 감사만 사용** — 기존 trust-based 한계 반복. 사람 review 만 catch, 누락 risk 미해소.
- **E-B: pre-commit hook만 사용** — 빠르지만 hook 설치 보장 부재. 다양한 Orchestrator session/agent/contributor 환경에서 reliable enforcement 불가.
- **E-D: Repo-local lint script만 (no CI)** — 좋은 testable primitive 이지만 CI 없으면 trust-based 와 동일.

## 해소 기준

N/A — permanent policy



- `CLAUDE.md`
- `docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md`
- `scripts/check-dogfood-artifact-paths.sh`
- `scripts/test-check-dogfood-artifact-paths.sh`
- `templates/github-workflows/dogfood-artifact-paths.yml`

## Amendment 1 (2026-05-05, CFP-113)

### 컨텍스트

본 ADR-017 의 결정 1 (금지 경로) 은 file 생성 위치만 lint 한다. 그러나 lane plugin agent md 의 권한 표기 (`allowed-tools` frontmatter 또는 본문 `Edit/Write(...)` 표기) 에 stale `docs/superpowers/**` 잔존 — 4 agent file (codeforge-review 의 DesignReviewPL / CodeReviewPL / SecurityTestPL + codeforge-pmo 의 PMOAgent) 권한에 ADR-013 dogfood-out 후 갱신 안 됨. file 생성 lint 만으로 catch 안 됨.

### 결정

ADR-017 §결정 1 (금지 경로) 의 lint 대상에 다음 추가:

- **agent md 의 권한 표기에 `docs/superpowers/**` 잔존 금지** — `Edit(docs/superpowers/...)` / `Write(docs/superpowers/...)` 패턴 모두 fail-closed
- 검사 위치: `agents/**.md` (lane plugin) 의 frontmatter `allowed-tools` 및 본문 권한 표기
- 검사 script: `scripts/check-superpowers-integration.sh` (CFP-113 신규) check 2

### 적용 시점 (effective date)

본 Amendment 1 effective date = CFP-113 Phase 1 PR merge 직후. Phase 2-7 lane plugin PR 가 stale path 정리 의무 이행 (mandatory acceptance criteria, [ADR-028](ADR-028-superpowers-integration-policy.md) §결정 6 정합).

### 관련 파일 추가

- `scripts/check-superpowers-integration.sh`
- `scripts/test-check-superpowers-integration.sh`
- `templates/github-workflows/superpowers-integration.yml`
- `docs/adr/ADR-028-superpowers-integration-policy.md`
