---
title: Invariant Check Phase A — workflow parity + plugin.json↔CHANGELOG version + agent count
slug: cfp-5-invariant-check-phase-a
status: draft
author: ClaudeOrchestrator (Claude+Codex 종합 리뷰 합의)
reviewers: [user]
related_adrs: [ADR-001-review-agent-unification]
created: 2026-04-27
story: CFP-5
---

## §1. 목적

Claude+Codex 종합 리뷰의 가장 큰 합의 결론(verbatim Codex executive summary): **"다음 단계 우선순위는 새 기능 추가가 아니라 SSOT를 SSOT답게 유지하는 자동 invariant"**.

CFP-1/2/3/4 self-application 흐름에서 발견된 SSOT drift 패턴 — workflow drift, narrative stage drift, distribution metadata drift, agent count drift — 을 **자동으로 차단**하는 GitHub Actions workflow 도입. Phase 분할로 단계적 도입, **본 Story는 Phase A** (mechanical invariant 3종, low risk, fast win).

### 수용 기준

- `.github/workflows/invariant-check.yml` 존재, push to main + pull_request to main 트리거
- 3 invariant check 모두 정의 + 통과 시 `✓` 메시지 + 실패 시 `::error::` annotation
- main 현재 상태에서 3 check 모두 PASS (회귀 0건)
- `templates/github-workflows/**` ↔ `.github/workflows/**` byte-identical 점검 (CFP-2/4 정합 보존)
- `.claude-plugin/plugin.json.version` ↔ `CHANGELOG.md` 최상단 [version] 일치 점검 (CFP-4에서 정합)
- `ls agents/*.md` 개수 ↔ `CLAUDE.md` 첫 매칭 "N core 에이전트" 일치 점검 (PR #26 audit P0 #5 정합)

## §2. 현재 구조 분석

### 2.1 Drift 패턴의 경험적 증거

CFP 4건의 self-application 흐름이 노출한 drift:

| Story | Drift 종류 | 발견 경로 |
|---|---|---|
| CFP-2 | `.claude/_overlay/project.yaml` PLG → CFP (overlay 정정) | 작업 중 발견 |
| CFP-3 | `docs/migration-guide.md` v0.8→v0.9 섹션 부재 | 정합성 점검 |
| CFP-4 P1 #1 | `.github/workflows/story-init.yml` ↔ template parser drift | Codex 종합 리뷰 |
| CFP-4 P1 #3 | `CLAUDE.md` self-application stage narrative drift | Codex 종합 리뷰 |
| CFP-4 P1 #4 | `.claude-plugin/plugin.json` v0.9 + 20 agents 미정합 | Codex 종합 리뷰 |
| audit Round 1·2 | "24/25 → 20 core 에이전트", inline decision table 7곳 등 다수 | 사용자 광범위 audit |

이들은 모두 **"코드는 바뀌었는데 narrative SSOT는 stale"** 동일 패턴. 수동 audit으로 정합되지만 재발 위험. **Drift 자동 차단**이 본질적 해결.

### 2.2 GitHub Actions 환경 활용 가능

Plugin은 이미 `.github/workflows/`에 6 plugin workflow + `lint.yml` + `test.yml`을 보유. invariant check 1개 더 추가는 자연스러움. 이미 yq, jq 사용 중이라 추가 의존성 없음.

### 2.3 Phase 분할 근거

전체 invariant 후보 (8건+) 한 번에 도입 시:
- Python validator 코드 작성 + 테스트 부담 큼
- Regex 기반 frontmatter 파싱 등 fragile
- Workflow 디버깅 어려움

→ **Mechanical 3건 먼저** (yaml diff + version match + integer match) 도입, 검증 후 Phase B/C/D로 점진 확장.

### 2.4 Mapper 변호 근거

기존 audit-by-human 패턴 유지하자는 Mapper 입장: "사용자가 광범위 audit (Round 1·2)을 직접 수행하는 패턴이 1인 maintainer 환경에서 충분. 자동화는 over-engineering."

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 부분 채택 (Phase A만)**.

근거:
- Mapper 우려 일부 타당 — 1인 환경에서 자동화 ROI 낮을 수 있음
- 그러나 audit-by-human 패턴은 (a) maintainer time burnout 위험 (b) 발견 지연 (CFP-3 v0.9 migration guide gap이 commit 3d2bfb2 머지 후 며칠 지나서 종합 리뷰로 발견된 사례) (c) consumer가 plugin 받는 시점에 SSOT drift가 user-facing 결함으로 노출 위험
- Phase A 3 invariant은 모두 mechanical (yaml diff + integer match + version string match) — 구현 복잡도 낮고 false positive 위험 매우 낮음. ROI 확실
- Phase B/C/D는 복잡도 높아 별도 평가 필요 — 본 Story scope 외

Mapper 우려는 §3.4 Phase 분할로 흡수 (전체 invariant 자동화 한 번에 도입 회피).

### 3.2 `.github/workflows/invariant-check.yml` 설계

**Trigger**: `push` to main + `pull_request` to main.

**Job 단계** (3 step, 순차 실행, 단일 step 실패 시 전체 FAIL):

#### Step 1: Workflow parity

```bash
for f in templates/github-workflows/*.yml; do
  base=$(basename "$f")
  target=".github/workflows/${base}"
  [ -f "$target" ] || { echo "::error::Missing $target"; EXIT=1; continue; }
  diff -q "$f" "$target" > /dev/null || { echo "::error::Drift $target"; EXIT=1; }
done
exit $EXIT
```

검증 대상: `templates/github-workflows/*.yml` (6개) ↔ `.github/workflows/<basename>.yml`. drift 발견 시 `diff` 출력으로 어디가 다른지 표시.

#### Step 2: Version match

```bash
PJ_VER=$(jq -r '.version' .claude-plugin/plugin.json)
CL_VER=$(grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1 | sed -E 's/^## \[(.*)\]$/\1/')
[ "$PJ_VER" = "$CL_VER" ] || exit 1
```

검증 대상: `.claude-plugin/plugin.json.version` ↔ `CHANGELOG.md` 최상단 `## [N.N.N]` 헤더. 미일치 시 둘 다 print + FAIL.

#### Step 3: Agent count

```bash
AGENT_COUNT=$(ls agents/*.md | wc -l | tr -d ' ')
DOC_COUNT=$(grep -oE '[0-9]+ core 에이전트' CLAUDE.md | head -1 | grep -oE '[0-9]+')
[ "$AGENT_COUNT" = "$DOC_COUNT" ] || exit 1
```

검증 대상: `ls agents/*.md` 실제 파일 수 ↔ `CLAUDE.md` 첫 매칭 "N core 에이전트". CLAUDE.md에 여러 곳에 표현이 있어도 첫 매칭(보통 line 3 narrative)이 가장 신뢰성 있는 source.

### 3.3 Permissions

```yaml
permissions:
  contents: read
```

invariant check는 read-only이므로 minimal scope. 다른 plugin workflow와 동일 패턴.

### 3.4 Phase 분할 — 본 Story scope 외

| Phase | Invariant | 별도 Story |
|---|---|---|
| **B** | `validate_config.py`에 `story_cutoff.additional_exempt_categories` 검증 + unknown key reject (Codex P1 #2) | CFP-6 (잠정) |
| **C-1** | frontmatter `permissions.allow` ↔ `CLAUDE.md` "Write queue 의뢰 권한" 표 정합 | CFP-7 (잠정) |
| **C-2** | ADR-002 footer SSOT 참조 1줄 패턴 검증 (모든 agent md의 "## 문서화 표준" 섹션) | CFP-8 (잠정) |
| **C-3** | `code.md` `dup-local: P1` 같은 SSOT enum 정합 | CFP-9 (잠정) |
| **D** | `docs/migration-guide.md` v0.X→v0.Y 섹션 존재 ↔ `CHANGELOG.md` 최상단 BREAKING 정합 | CFP-10 (잠정) |

Phase B는 다음 Story로 자연스럽게 이어짐. Phase C는 복잡도 높아 한꺼번에 다루는 게 좋을지 별도 평가.

### 3.5 ADR 정합성

- **ADR-001** 무관
- **ADR-002** (DocsAgent footer SSOT 참조 1줄 유지): 본 Phase A는 ADR-002 검증 미포함 (Phase C-2). 영향 없음
- 신규 ADR 필요 없음

## §4. API 계약

### 4.1 GitHub Actions workflow yaml schema

기존 plugin workflow와 동일 패턴. `name` · `on` · `permissions` · `jobs.<name>.{runs-on, steps[]}` 표준 GitHub Actions schema 준수.

### 4.2 Error annotation 형식

`::error file=<path>::<message>` 형식 사용 (GitHub Actions native annotation). PR review에서 inline 에러로 표시.

### 4.3 Exit code semantics

각 step `exit 1` = step 실패 → workflow FAIL. 모든 step 통과 시 workflow SUCCESS → `phase-gate-mergeable.yml` 같은 다른 required check와 함께 PR mergeable status에 기여.

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `.github/workflows/invariant-check.yml` | 신규 | DocsAgent (= 본 작업자) | 적용 완료 + local sim 3 invariant PASS |
| `docs/stories/CFP-5.md` | 신규 | DocsAgent | 작성 중 |
| `docs/change-plans/cfp-5-invariant-check-phase-a.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. 기존 인프라 변경 없이 새 workflow 1개 추가만.

## §8. Test Contract

### §8.1 커버리지 계획

- 단위 테스트: **N/A** — bash one-liner workflow, 별도 단위 테스트 인프라 없음
- 통합 테스트: **Local simulation으로 3 invariant 검증 완료** (workflow parity OK / version 0.9.0 ↔ 0.9.0 / agent count 20 ↔ 20)
- 인프라 테스트: **GitHub Actions 자동 lint** (push 시) — yaml syntax 검증

### §8.2 경계 조건·invariant

- **Workflow parity**: `templates/github-workflows/*.yml` 신규 추가 시 `.github/workflows/`에도 동일 파일 자동 sync 의무 (CFP-2 인프라 도입 시 6개 동시 추가했음). drift 발견 시 fail-hard
- **Version match**: `plugin.json.version` 또는 `CHANGELOG.md` 한쪽만 갱신 시 fail-hard. 새 release 시 둘 다 동기 갱신 의무
- **Agent count**: `agents/` 디렉토리에서 `*.md` 추가/삭제 시 `CLAUDE.md` 첫 "N core 에이전트" 동기 갱신 의무. PR #26 audit P0 #5 invariant를 자동화로 영구 보존
- **Edge cases**:
  - `agents/.DS_Store` 등 hidden file: `*.md` glob이 자동 제외
  - CLAUDE.md에 "N core 에이전트" 표현 다중 등장: `head -1`로 첫 매칭만 사용 (line 3 narrative가 SSOT)
  - 한국어 vs 영문 표현: 본 Phase는 한국어 "에이전트"만 검증. 영문 "agents"도 보강 가능하나 false positive 위험으로 보류
  - `templates/github-workflows/`에 새 파일 추가 시 `.github/workflows/`에 미복사 → "Missing" error로 명시

### §8.3 Perf Baseline

**N/A** — workflow execution time이 핵심 지표가 아니며, 3 step bash가 < 5초 예상.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (Plugin meta 변경, 새 인프라 1개 추가).

Commit 시리즈 2개:
- **Commit 1**: `.github/workflows/invariant-check.yml` 신규
- **Commit 2**: `docs/stories/CFP-5.md` + `docs/change-plans/cfp-5-...md` 영속화

본 PR base는 `main`. PR #27 close + PR #31 merged 후 standalone.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- **ADR-001**: 무관
- **ADR-002**: 본 Phase A 미포함 (Phase C-2가 ADR-002 footer 검증)
- **신규 ADR 필요**: **없음**. invariant 자동 점검 도입은 Process Decision의 인프라 적용. 향후 Phase B/C가 추가될 때 ADR로 격상할지 별도 평가 (Process Decision의 ADR 격상 trigger는 audit Round 2 ADR-002 신설 패턴 참조)
