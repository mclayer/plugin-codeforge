---
type: domain-knowledge
area: jsonl-write
topic_slug: race-condition-handling-pattern
title: Cross-repo JSONL write race condition handling pattern — Contents API SHA-based optimistic concurrency (Pattern A 의무) vs Long-lived branch (Pattern B) vs File lock (Pattern C)
status: Active
related_adrs:
  - ADR-026  # post-merge-counters.jsonl carrier (Pattern A implementation precedent — post-merge-telemetry.sh)
  - ADR-045  # retro-attempts.jsonl carrier (Phase 1 follow-up amendment_id=1 — Pattern A 의무 명시)
related_stories:
  - CFP-74   # ADR-026 carrier — post-merge-followup automation
  - CFP-138  # ADR-045 carrier — Story retro mandatory trigger (boundary issue resolution carrier)
created: 2026-05-09
updated: 2026-05-09
---

# Cross-repo JSONL write race condition handling pattern

## 정의

**Cross-repo JSONL write** = codeforge orchestration 의 **persistent observability** 영역 (post-merge-counters.jsonl + retro-attempts.jsonl + 미래 신설). 동일 jsonl file 에 **다수 GitHub Actions workflow run** 이 **concurrent push** 발화 시 발생하는 **lost-update / race condition** 문제에 대한 **3 종 pattern** 비교 + 선택 기준. 본 페이지는 **Pattern A 를 모든 cross-repo jsonl write 의 default 의무 패턴** 으로 명시.

## 컨텍스트

CFP-138 Phase 2 구현 리뷰 lane FIX iter 1 P0 C-1 (CodeReviewPL finding):
- `retro-attempts.jsonl` 의 4 git push points (first attempt write + retry-state-machine 의 success/failed/escalated status update) 가 **race condition 미처리**
- Phase 2 PR #291 implementation = `git clone + python3 modify + git add + commit + git push` pattern → concurrent push 시 second push **non-fast-forward fail** (silent lost-update risk)
- ADR-026 post-merge-counters.jsonl 도 **동일 mirror 결함** — cross-file pattern 일관성 issue 가 "여러 파일 공통 이슈, 설계 지침 부재" → boundary issue 진정

ArchitectPLAgent 최종 원인 판정 (CLAUDE.md decision table P1 boundary rule SSOT):
- **C-1 = 설계 (boundary)**: ADR-026 + ADR-045 cross-file design gap = "jsonl write race condition handling pattern" 명시 부재
- **선행 사례 (post-merge-telemetry.sh)**: Contents API SHA-based optimistic concurrency 가 이미 implementation 정합 — 단 doc 명시 부재로 future implementer 가 다시 inconsistent pattern 선택 (recurrence risk)

본 페이지 = boundary issue resolution carrier — **Pattern A 의무** + Pattern B/C 비교 + git clone + bare push 금지 명시.

## 핵심 규칙

### Pattern A — Contents API SHA-based optimistic concurrency (**권장 default, 모든 cross-repo jsonl write 의무**)

**Mechanism**: GitHub Contents API `PUT /repos/{owner}/{repo}/contents/{path}` 가 `sha` 매개변수 (existing file blob SHA) 를 mandatory 로 받음 — concurrent write 시 server 가 SHA mismatch 검출 후 **409 Conflict** return. client 가 retry loop 로 (max 3) re-fetch + re-apply.

**선행 사례**: `scripts/post-merge-telemetry.sh` line 60-110 (CFP-74 / ADR-026 carrier — Codex P0 fix 시 도입).

**Pseudocode** (post-merge-telemetry.sh line 73-90 mirror):

```bash
INTERNAL_DOCS_REPO="mclayer/codeforge-internal-docs"
JSONL_PATH="wrapper/retro-attempts.jsonl"  # or post-merge-counters.jsonl etc.
BRANCH="telemetry-counters"  # long-lived branch, not main (ADR-026 §결정 4 정합)

# Build new entry
ENTRY=$(jq -nc --arg ts "$TIMESTAMP" --arg sk "$STORY_KEY" ... '{...}')

# Retry loop with SHA-based optimistic concurrency
for retry in 1 2 3; do
    # Fetch existing content + SHA from target branch
    EXISTING=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${JSONL_PATH}?ref=${BRANCH}" \
                  --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")
    SHA=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${JSONL_PATH}?ref=${BRANCH}" \
                  --jq '.sha' 2>/dev/null || echo "")

    # Append new entry (preserve trailing newline — Codex P1 #3 fix in post-merge-telemetry.sh)
    if [[ -n "$EXISTING" ]]; then
        NEW_CONTENT=$(printf '%s\n%s\n' "$EXISTING" "$ENTRY")
    else
        NEW_CONTENT=$(printf '%s\n' "$ENTRY")
    fi
    NEW_CONTENT_B64=$(printf '%s' "$NEW_CONTENT" | base64 -w0)

    # PUT with SHA (or create if SHA empty — first write)
    ARGS=(-X PUT "repos/${INTERNAL_DOCS_REPO}/contents/${JSONL_PATH}"
        -f message="$COMMIT_MSG"
        -f content="$NEW_CONTENT_B64"
        -f branch="$BRANCH")
    [[ -n "$SHA" ]] && ARGS+=(-f sha="$SHA")

    if gh api "${ARGS[@]}"; then
        echo "::notice::JSONL write success (retry=$retry)"
        break
    else
        # 409 conflict — concurrent push detected. retry with fresh SHA + jitter.
        echo "::warning::JSONL write 409 conflict (retry=$retry/3)"
        sleep $((RANDOM % 5 + 1))
    fi
done
```

**선택 기준**:
- ✓ Cross-repo write (PAT 의무, branch + PR 패턴 정합 — ADR-026 §결정 4 정합)
- ✓ Concurrent write rate ≤ ~10/min (GitHub Contents API rate limit 5000 req/h 무관 정상 한도)
- ✓ Lost-update unacceptable (telemetry / retry state machine — silent loss = forcing function 무효)
- ✓ Race detect 의무 (server-side SHA validation — atomic at GitHub side)

**Long-lived branch 정합**: cross-repo jsonl write 는 main 직접 push 금지 (ADR-026 §결정 4) → long-lived branch (예: `telemetry-counters` for ADR-026, `retro-attempts-state` for ADR-045) + 단일 rolling PR. 본 branch 안에서 SHA-based optimistic concurrency 사용.

### Pattern B — Long-lived branch + sequential merge queue (high-volume — 미사용 default)

**Mechanism**: per-write feature branch (`retro-attempt-${PR_NUM}-${ATTEMPT_N}`) + sequential PR merge (queue order). queue 처리 = GitHub Actions concurrency group + auto-merge.

**선택 기준**:
- ✓ Concurrent write rate > ~10/min (Pattern A 의 409 retry overhead 가 path 지연)
- ✓ Strict ordering 의무 (timestamp 순 vs PR merge order 순 등)
- ✗ Over-engineering for jsonl typical use case (codeforge family 는 모두 Pattern A 충분)

**현재 사용 사례**: 미사용 (참조용).

### Pattern C — File lock + retry (local-only — 미사용 default)

**Mechanism**: `flock(2)` Unix advisory lock + retry-on-conflict. local file system 에 jsonl 작성 시.

**선택 기준**:
- ✓ Local-only jsonl (cross-repo 미사용)
- ✓ Single host concurrent process race
- ✗ Cross-repo unsuitable (advisory lock 은 file system 영역 — GitHub remote 에 무효)

**현재 사용 사례**: 미사용 (참조용 only — codeforge family 는 모든 jsonl 이 cross-repo).

## 경계

### 의무 경계 (binding rules)

1. **모든 cross-repo jsonl write workflow = Pattern A 의무** (post-merge-telemetry.sh 이미 정합 + retro-mandatory.yml Phase 2 PR 의무 + 미래 신설 모두). consistent pattern → cross-file inconsistency 회피
2. **`git clone + git add + git commit + git push` pattern 금지 cross-repo jsonl 영역** — lost-update risk (concurrent push 시 second push = non-fast-forward fail without recovery, silent telemetry loss)
3. **Long-lived branch + 단일 rolling PR 패턴 의무** (ADR-026 §결정 4 정합 — main 직접 push 금지)
4. **Retry max = 3** (network blip 자동 복구 — Pattern A pseudocode `for retry in 1 2 3` SSOT). 3 회 fail 후 `::error::` log + workflow exit 1 (downstream alert)
5. **409 conflict 시 jitter sleep** (`sleep $((RANDOM % 5 + 1))`) — concurrent client thundering herd 회피

### 면제 경계 (out-of-scope)

- **Local-only jsonl** (codeforge wrapper repo 의 `.codeforge/` flag 등) = cross-repo race 무관. file system advisory lock 또는 simple write OK
- **In-memory state** (Phase 1 first-attempt grace period 의 sleep 300 step state 등) = jsonl 영역 외
- **Read-only jsonl** (예: retro-retry-helper.sh 의 due entry parse) = race 무관

### 위반 시 처리

- DesignReviewPL = boundary issue P0 fail (cross-file pattern 부재 = 설계 지침 위반)
- CodeReviewPL = boundary issue P0 fail (Pattern A 미적용 implementation = lost-update risk)
- 회귀 spec = 본 페이지 cross-ref 명시 + 해당 ADR amendment + DesignReview re-run

## 변경 이력

- **2026-05-09**: 신설 (CFP-138 Phase 1 follow-up — FIX iter 2 boundary resolution from CodeReviewPL Iter 1 P0 A-2 + P0 C-1). ArchitectPLAgent 최종 판정 정합 — C-1 = 설계 (boundary), Pattern A 의무 명시.
