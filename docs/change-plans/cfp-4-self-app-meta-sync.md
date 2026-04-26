---
title: Self-application 메타 정합 — story-init.yml drift sync + CLAUDE.md self-app stage 정정 + plugin.json v0.9·20 정합
slug: cfp-4-self-app-meta-sync
status: draft
author: ClaudeOrchestrator (Claude+Codex 종합 리뷰 발견)
reviewers: [user]
related_adrs: [ADR-001-review-agent-unification]
created: 2026-04-27
story: CFP-4
---

## §1. 목적

CFP-1/2/3 plugin self-application 흐름 완료 직후 Claude+Codex 종합 리뷰에서 식별된 **3건 P1 SSOT drift** 일괄 정합. 본 변경은 P1 #1 + #3 + #4 묶음 (Codex 리뷰 발견). P1 #2 (`validate_config.py` `story_cutoff` 검증 부재)는 invariant 자동화 본질이라 CFP-5로 분리.

### 수용 기준

- `.github/workflows/story-init.yml` ↔ `templates/github-workflows/story-init.yml` byte-identical
- `CLAUDE.md` "Plugin 자체 적용 (dogfooding)" 섹션이 stage-2 완료 + stage-3 (CFP-5 잠정) 예고 명시
- `.claude-plugin/plugin.json` `version: 0.9.0` + description의 agent 수 "20 core 에이전트" + ADR-001 lane-agnostic 통합 + dogfooding 언급 명시
- `docs/stories/CFP-4.md` + `docs/change-plans/cfp-4-...md` 영속화

## §2. 현재 구조 분석

### 2.1 SSOT drift 3 layer

종합 리뷰에서 식별된 drift 패턴: **"코드는 바뀌었는데 narrative SSOT는 stale 그대로"**.

| Drift | 파일 | 상태 |
|---|---|---|
| (a) Self-app workflow drift | `.github/workflows/story-init.yml` | template sentinel parser + 동적 `default_branch` 미적용 (구 range parser + `main` hardcoded) |
| (b) Stage narrative drift | `CLAUDE.md` "Plugin 자체 적용" 섹션 | "1단계 현재 / 2단계 향후"로 적혀있으나 실제 stage-2 인프라(CFP-2) 완료 + main 머지됨 |
| (c) Distribution metadata drift | `.claude-plugin/plugin.json` | `version: 0.7.1` + "24 core 에이전트" 광고 — v0.9·20 정합 미반영. consumer 설치·호환성 판단 가장 바깥 meta가 stale |

### 2.2 발견 경로

CFP-3 PR #27 작업 직후 사용자 요청에 따른 Claude+Codex 양 리뷰:
- **Codex**: 4 P1 + 2 P2 발견 (이 3건 + `validate_config.py` `story_cutoff` 검증 부재 + README narrative + phase-gate-mergeable PR-label fallback)
- **Claude**: Codex 발견 보강 + 추가 P1 (PR #27 미머지 — 별개) + 4 P2/P3
- **양측 합의**: "다음 단계 우선순위는 새 기능 추가가 아니라 'SSOT를 SSOT답게 유지하는 자동 invariant'" (Codex executive summary verbatim)

### 2.3 다른 5 workflow drift 부재 확인

`fix-ledger-sync.yml`, `phase-gate-mergeable.yml`, `phase-label-invariant.yml`, `story-section-1-immutable.yml`, `subissue-from-impl-manifest.yml`은 template과 byte-identical 확인 (`diff -q` 점검). story-init.yml만 drift.

### 2.4 Mapper 변호 근거

기존 narrative를 보존하자는 Mapper 입장: "stage-1/2 narrative는 CFP-1 Story 생성 시점에 정확. plugin.json도 v0.7.1 시점 정확. 변경 시 historical accuracy 훼손."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- (a) workflow drift는 self-application의 핵심 가치(consumer와 동일 artifact dogfood)를 직접 약화. consumer가 codeforge 받았을 때 동작이 plugin 자체에서 검증된 적 없음. 즉시 sync 필요
- (b)(c) narrative/meta drift는 consumer 신뢰 신호 직접 약화. plugin.json은 marketplace 표시·설치 결정에 쓰이는 메타라 stale은 명백한 user-facing 결함
- Mapper 변호는 historical 회고성으로만 의미 — 활성 narrative SSOT가 stale인 게 더 큰 비용

Mapper 우려는 §3.5 정정 narrative에 "CFP-2 머지로 stage-2 완료" 이력 명시 + `plugin.json` description에 "v0.9 lane-agnostic review 통합" 명시로 흡수.

### 3.2 변경 영역 — 3개 정합

#### A. `.github/workflows/story-init.yml` ↔ template sync

`templates/github-workflows/story-init.yml` 그대로 복사. diff:
- Sentinel 기반 awk parser (`/^### A/{flag=1; next} /^### /{flag=0} flag`) 적용 — Optional 필드 비어있어도 EOF 흘러가지 않음
- `default_branch` `.claude/_overlay/project.yaml`에서 `yq` 동적 read — `main` hardcoded 제거

#### B. `CLAUDE.md` "Plugin 자체 적용" 섹션 정정

```markdown
- **1단계 완료** (CFP-1): Story 작성 의무 정책 + `docs/stories/` 디렉토리 + 수동 Story 작성
- **2단계 완료** (CFP-2): `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` + `.github/workflows/`에 6종 워크플로우 + `.github/PULL_REQUEST_TEMPLATE.md` + `.github/CODEOWNERS` 도입
- **3단계 향후** (CFP-5 잠정): `templates/**` ↔ `.github/**` parity + frontmatter ↔ CLAUDE.md 표 ↔ plugin.json 정합 자동 점검 CI
- **End-to-end 실증** (CFP-7 잠정): 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → workflow 자동 동작 첫 검증
```

추가로 Branch protection 가이드 1줄 (PR body에서만 안내됐던 것 → CLAUDE.md에 영속화).

#### C. `.claude-plugin/plugin.json` v0.9·20 정합

```json
{
  "version": "0.9.0",
  "description": "... 20 core 에이전트 ... Lane-agnostic review 워커 통합 (ADR-001) · Plugin self-application dogfooding ..."
}
```

### 3.3 ADR 정합성

- ADR-001 (review-agent-unification): plugin.json description에 명시 — lane-agnostic 통합이 v0.9 본질
- 신규 ADR 필요: 없음

### 3.4 본 변경에서 처리하지 않는 것 (scope 외)

| 항목 | 사유 |
|---|---|
| `validate_config.py` `story_cutoff` 검증 (Codex P1 #2) | invariant 자동화 본질이라 CFP-5에서 통합 처리 |
| README · plugin-design.md stale narrative (Codex P2) | 본 PR이 chore-meta-sync 본질이라 README 재작성은 별개 정정 PR 가치 |
| phase-gate-mergeable.yml PR-label fallback (Codex P2) | SSOT 이중화 정책 결정 필요, 별개 검토 |

## §4. API 계약

### 4.1 plugin.json schema

기존 schema 그대로. `version` · `description` 필드만 갱신. `name`, `author`, `keywords` 보존.

### 4.2 CLAUDE.md "Plugin 자체 적용" 섹션 텍스트

§3.2 B verbatim.

### 4.3 story-init.yml 동작

template과 동일하므로 별도 spec 없음. template SSOT 참조.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/story-init.yml` | 수정 (template overwrite) | DocsAgent (= 본 작업자) | 적용 완료 |
| `CLAUDE.md` | 수정 (Plugin 자체 적용 섹션 정정) | DocsAgent | 적용 완료 |
| `.claude-plugin/plugin.json` | 수정 (version + description) | DocsAgent | 적용 완료 |
| `docs/stories/CFP-4.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-4-self-app-meta-sync.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. 단순 정합 chore.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — 메타 정합 chore, 코드 변경 없음
- 통합 테스트: **N/A**
- 인프라 테스트: **워크플로우 yaml syntax 검증** (GitHub Actions push 시 자동)

### §8.2 경계 조건·invariant

- `.github/workflows/story-init.yml` ↔ `templates/github-workflows/story-init.yml` byte-identical (`diff -q` PASS)
- `plugin.json.version` ↔ `CHANGELOG.md` 최상단 일치 (`0.9.0`)
- CLAUDE.md "20 core 에이전트" 일관 (PR #26 audit P0 #5와 정합)
- `default_branch` `.claude/_overlay/project.yaml`에서 동적 read — main 외 사용자가 default branch를 다른 이름으로 설정 시도 동일 동작

### §8.3 Perf Baseline

**N/A** — 메타 변경.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (Plugin meta chore).

Commit 시리즈 1개 또는 2개:
- **Commit 1** (택1): 3 정합 파일 일괄 (`story-init.yml` + `CLAUDE.md` + `plugin.json`)
- **Commit 2**: Story file + Change Plan 영속화

또는:
- **Commit 1**: `.github/workflows/story-init.yml` sync
- **Commit 2**: `CLAUDE.md` self-app stage 정정
- **Commit 3**: `.claude-plugin/plugin.json` v0.9 정합
- **Commit 4**: Story + Change Plan

후자가 git 추적·revert 단위 명확. 채택: **후자 (4 commits)**.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- **ADR-001**: plugin.json description에 인용. 일치
- **신규 ADR 필요 없음**: chore meta 정합
