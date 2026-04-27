---
title: Bootstrap drift 자동 검출 + label 자동 부트스트랩 script (CFP-11 후속)
slug: cfp-12-bootstrap-check-and-labels
status: draft
author: ClaudeOrchestrator (CFP-11 §11 후속)
reviewers: [user]
related_adrs: []
created: 2026-04-27
story: CFP-12
---

## §1. 목적

CFP-11에서 발견한 환경 drift 2종 (org permission OFF / 18 label 부재)을 SessionStart hook에서 자동 검출하고, label 부재는 idempotent script로 1회 회복 가능하도록 보강.

CFP-11 §11 §"향후 작업"의 CFP-12 + CFP-13 통합 (둘 다 환경 부트스트랩 drift 검출/회복으로 책임 동일).

### 수용 기준

- `overlay/hooks/check-bootstrap.sh` non-blocking (drift 시 stderr WARN, exit 0)
- org permission API 검증: `default_workflow_permissions == "write"` + `can_approve_pull_request_reviews == true`
- 18 plugin label 존재 검증 (개별 enumerate)
- `scripts/bootstrap-labels.sh` idempotent (create or edit, 기존 색상/desc 갱신)
- `regen-agents.sh` SessionStart 통합 (project.yaml validate 직후, `|| true` 비차단)
- yq 의존 회피 → PyYAML로 통일

## §2. 현재 구조 분석

### 2.1 CFP-11 발견 환경 drift

**Drift A — org-level Workflow permissions OFF**:
- 증상: `GitHub Actions is not permitted to create or approve pull requests`
- 원인: org Settings → Actions → "Workflow permissions" → "Allow GitHub Actions to create PRs" OFF
- 자동 fix 불가 (org admin scope 필요, 1인 maintainer 환경 자동화 어려움)

**Drift B — 18 plugin label 부재**:
- 증상: `gh issue create --label "type:story" → not found`
- 원인: 신규 repo 생성 직후 plugin label 자동 부트스트랩 부재
- 자동 fix 가능 (`gh label create` x18, idempotent)

### 2.2 SessionStart hook 현재 구조

`overlay/hooks/regen-agents.sh`:
1. PLUGIN_ROOT resolve
2. validate_config.py로 project.yaml schema 검증 (fail-fast)
3. 20 core agent + overlay 병합 → `.claude/agents/*.md` 생성
4. CLAUDE.md merge (overlay 있을 시)

env 정합 검증은 부재 — workflow가 의도대로 동작 가능한지 모르는 상태로 진행.

### 2.3 Mapper 변호 근거

기존 SessionStart 단순성 보존 입장: "consumer-guide 부트스트랩 단계 명시로 충분. SessionStart에 추가 호출은 매 세션 부담."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- non-blocking WARN은 매 세션 reminder 역할 — 사람의 주의 의존을 명시적 안내로 대체
- gh API 1-2회 호출 비용 minimal (~1초), 첫 사용 막힘 비용보다 훨씬 작음
- CFP-1~10 자동 검출 패턴 일관성

### 3.2 check-bootstrap.sh 구조

```bash
# project.yaml에서 org/repo 추출 (Python+PyYAML)
ORG_REPO=$(python3 - <<PYEOF
import sys, yaml
data = yaml.safe_load(open(sys.argv[1])) or {}
gh = data.get("github", {})
print(f"{gh.get('org','')}|{gh.get('repo','')}")
PYEOF
)

# Check 1: org permission
PERM=$(gh api repos/$ORG/$REPO/actions/permissions/workflow)
# default_workflow_permissions == "write" + can_approve == true 검증

# Check 2: 18 label 존재
EXISTING=$(gh label list --limit 100 --json name)
# REQUIRED_LABELS x18 enumerate, 부재 시 WARN
```

3 silent-skip 조건:
- gh CLI 미설치
- gh auth status 실패
- project.yaml 미존재

WARN 시 exit code 0 (non-blocking).

### 3.3 bootstrap-labels.sh

idempotent 18 label 생성:
- `gh label create` 실패 시 `gh label edit` 시도 (color/desc 갱신)
- 둘 다 실패 시 한 줄 에러 표시 후 다음 label로 진행

### 3.4 regen-agents.sh wiring

```bash
# Validate project.yaml schema (기존)
if [ -f "$VALIDATE_SCRIPT" ]; then
    python3 "$VALIDATE_SCRIPT" "$OVERLAY_PROJECT_YAML" || exit 1
fi

# Bootstrap drift check (CFP-12, non-blocking)
if [ -x "$BOOTSTRAP_CHECK_SCRIPT" ]; then
    OVERLAY_PROJECT_YAML="$OVERLAY_PROJECT_YAML" bash "$BOOTSTRAP_CHECK_SCRIPT" || true
fi
```

`|| true`로 hook 자체 abort 방지.

### 3.5 yq → PyYAML 교체 결정

초기 구현은 yq 사용했으나 local test에서 yq 미설치 silent skip 발견 (Test 1). PyYAML은 validate_config.py가 사용하는 plugin 필수 의존이므로 추가 부담 zero.

### 3.6 ADR 정합성

- ADR-001/002 무관
- 신규 ADR 불요

## §4. API 계약

본 Story는 신규 script 추가 + 기존 hook 1줄 wiring. API 계약 변경 없음.

stderr 출력 형식 (drift 시):
```
[check-bootstrap] N 부트스트랩 drift 발견 (non-blocking):
[bootstrap] WARN: <drift 종류>
           → <안내>
           → <미해결 시 영향>
```

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `overlay/hooks/check-bootstrap.sh` | 신규 | DocsAgent | 작성 완료, Test PASS |
| `overlay/hooks/regen-agents.sh` | 수정 | DocsAgent | wiring 완료 |
| `scripts/bootstrap-labels.sh` | 신규 | DocsAgent | 작성 완료, idempotent test PASS |
| `docs/consumer-guide.md` | 수정 (§2d / §2f 자동화 참조) | DocsAgent | 적용 완료 |
| `docs/stories/CFP-12.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-12-...md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. 기존 SessionStart hook 구조 보존 + 1줄 wiring 추가만.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — bash script + GitHub API 의존, plugin pytest 인프라 없음
- 통합 테스트: **Local 3 시나리오** — bootstrap-labels 멱등성 / check-bootstrap 정상 detect / regen-agents end-to-end
- 인프라 테스트: **N/A**

### §8.2 경계 조건·invariant

- **Test 1 — bootstrap-labels.sh 멱등성**: 모든 label 존재 시 18 update + exit 0
- **Test 2 — check-bootstrap.sh detect**: org permission OFF (default=read) → 1 WARN + exit 0
- **Test 3 — regen-agents.sh chain**: validate → check-bootstrap → 20 agent regen 정상
- **Edge case — gh 미설치**: silent skip (exit 0)
- **Edge case — yq 미설치**: PyYAML 교체로 회피
- **Edge case — gh auth status 실패**: silent skip (DocsAgent가 별도 안내)

### §8.3 Perf Baseline

**N/A** — gh API 1-2회 호출 (<2s), session 시작 시 사용자 인지 부담 minimal.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (메타 script).

Commit 시리즈 1개 (모든 산출물 일관 포함).

본 PR base는 `main`. CFP-11 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- ADR-001/002 무관
- 신규 ADR 불요
- ADR-003 (조건부) 후보: invariant vs 환경 부트스트랩 vs 가이드 책임 분리 — 3 layer 모두 자리잡았으니 ADR로 정리할 시점 (CFP-13 별도 Story로 또는 본 Story 후속)
