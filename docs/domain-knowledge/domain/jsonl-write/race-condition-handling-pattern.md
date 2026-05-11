---
kind: domain_fact
type: domain-knowledge
area: jsonl-write
topic_slug: race-condition-handling-pattern
title: Cross-repo JSONL write race condition handling pattern — Contents API SHA-based optimistic concurrency (Pattern A 의무) vs Long-lived branch (Pattern B) vs File lock (Pattern C)
status: Active
tags:
  - jsonl
  - race-condition
  - github-api
  - concurrency
  - cross-repo
related_adrs:
  - ADR-026  # post-merge-counters.jsonl carrier (Pattern A implementation precedent — post-merge-telemetry.sh)
  - ADR-045  # retro-attempts.jsonl carrier (Phase 1 follow-up amendment_id=1 — Pattern A 의무 명시)
related_stories:
  - CFP-74   # ADR-026 carrier — post-merge-followup automation
  - CFP-138  # ADR-045 carrier — Story retro mandatory trigger (boundary issue resolution carrier)
created: 2026-05-09
updated: 2026-05-09
amended: 2026-05-09  # CFP-289: Retry Semantics section added
---

# Cross-repo JSONL write race condition handling pattern

## Summary

Cross-repo JSONL 파일에 **다수 GitHub Actions workflow run** 이 concurrent push 를 시도할 때 발생하는 **lost-update / race condition** 문제를 해결하기 위한 3-종 패턴 비교 + 선택 기준 SSOT. **Pattern A (GitHub Contents API SHA-based optimistic concurrency)** 가 모든 cross-repo jsonl write 의 **default 의무 패턴**.

## Pattern

### Pattern A — Contents API SHA-based optimistic concurrency (default 의무)

GitHub Contents API `PUT /repos/{owner}/{repo}/contents/{path}` 에 기존 file blob SHA 를 mandatory 파라미터로 전달 → server-side atomic SHA mismatch 검출 (409 Conflict) → client retry loop (max 3 + jitter). Cross-repo jsonl write 시 git clone + push 패턴을 대체하는 **lost-update-safe** 의무 패턴.

**구현 참조**: `scripts/post-merge-telemetry.sh` line 60-110 (CFP-74 / ADR-026 — Codex P0 fix 시 도입).

### Pattern B — Long-lived branch + sequential merge queue

Per-write feature branch + sequential PR merge (queue order). concurrent write rate > ~10/min 또는 strict ordering 의무 시 고려. codeforge family 에서는 Pattern A 로 충분하여 **미사용 default**.

### Pattern C — File lock + retry (local-only)

`flock(2)` Unix advisory lock + retry-on-conflict. local file system jsonl 전용 — cross-repo 에 무효. codeforge family 는 모든 jsonl 이 cross-repo 이므로 **미사용 default**.

## Usage

**모든 cross-repo jsonl write workflow 에서 Pattern A 를 의무 적용**. git clone + git push 패턴 금지.

```bash
# Pattern A pseudocode — retry loop with SHA-based optimistic concurrency
for retry in 1 2 3; do
    SHA=$(gh api "repos/${REPO}/contents/${PATH}?ref=${BRANCH}" --jq '.sha' 2>/dev/null || echo "")
    EXISTING=$(gh api "repos/${REPO}/contents/${PATH}?ref=${BRANCH}" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")
    NEW_CONTENT_B64=$(printf '%s\n%s\n' "$EXISTING" "$NEW_ENTRY" | base64 -w0)
    ARGS=(-X PUT "repos/${REPO}/contents/${PATH}" -f message="$MSG" -f content="$NEW_CONTENT_B64" -f branch="$BRANCH")
    [[ -n "$SHA" ]] && ARGS+=(-f sha="$SHA")
    if gh api "${ARGS[@]}"; then break; fi
    sleep $((RANDOM % 5 + 1))  # jitter — concurrent client thundering herd 회피
done
```

**적용 대상** (binding):
- `post-merge-counters.jsonl` (ADR-026 / CFP-74) — 이미 Pattern A 적용
- `retro-attempts.jsonl` (ADR-045 / CFP-138) — Pattern A 의무 적용 대상
- 미래 신설 cross-repo jsonl 전부

**Long-lived branch 의무**: cross-repo jsonl write 는 main 직접 push 금지 (ADR-026 §결정 4) → 전용 long-lived branch (예: `telemetry-counters`, `retro-attempts-state`) + 단일 rolling PR.

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

## Retry Semantics (Pattern A 의무 — CFP-289)

Pattern A retry loop 의 HTTP status 별 동작과 exhausted 처리를 명시. 두 sink (post-merge-telemetry.sh + retro-mandatory.yml) 의 동작 기준 SSOT.

### 4xx HTTP status → 즉시 실패 (no-retry)

**4xx = client error** — retry 해도 결과가 바뀌지 않음. 재시도 낭비 + 잘못된 상태를 마스킹할 위험.

| Code | 원인 | 동작 |
|---|---|---|
| 401 Unauthorized | PAT 만료 / scope 부족 | 즉시 exit 1 + stderr 에 `::error::` 출력 |
| 403 Forbidden | repo 접근 불가 / branch protection | 즉시 exit 1 + stderr |
| 404 Not Found | repo / branch / path 가 존재하지 않음 (branch 미생성 전 race 가능 — 아래 edge case 참조) | 즉시 exit 1 + stderr |
| 409 Conflict (SHA mismatch) | **예외 — concurrent write** | 재시도 (아래 5xx/409 섹션 참조) |
| 422 Unprocessable | 잘못된 payload (content 인코딩 오류 등) | 즉시 exit 1 + stderr |

**구현 의무**: HTTP code 가 4xx (409 제외) 이면 retry loop 즉시 break → exit 1. `sleep` 없이 즉시 실패.

```bash
if echo "$HTTP_CODE" | grep -qE '^4[0-9]{2}$' && ! echo "$HTTP_CODE" | grep -q '^409$'; then
  echo "::error::4xx client error (HTTP ${HTTP_CODE}) — no retry, aborting" >&2
  exit 1
fi
```

### 5xx / network timeout → exponential backoff retry

**5xx = server error / transient** — GitHub API 일시 장애 또는 network timeout. 재시도로 자동 복구 가능.

| 상태 | 동작 |
|---|---|
| 5xx (500, 502, 503, 504) | retry with exponential backoff |
| Network timeout / curl error (exit ≠ 0, HTTP code 미취득) | retry with exponential backoff |
| 409 Conflict (SHA mismatch) | re-fetch SHA + retry with jitter |

**Backoff 스케줄** (retry max 3 → 총 4 attempt: 1 initial + 3 retry):

| Attempt | 설명 | Sleep before next |
|---|---|---|
| 1 (initial) | first try | 실패 시 2s sleep |
| 2 (retry 1) | backoff 1 | 실패 시 4s sleep |
| 3 (retry 2) | backoff 2 | 실패 시 8s sleep |
| 4 (retry 3) | backoff 3 (final) | 실패 시 → exhausted fallback |

409 (SHA conflict) 시 jitter (`sleep $((RANDOM % 5 + 1))`) 추가 — thundering herd 회피. 5xx 는 deterministic backoff (2/4/8s) + 선택적 jitter 허용.

```bash
BACKOFF_DELAYS=(2 4 8)
for ATTEMPT in 1 2 3 4; do
  # ... PUT ...
  HTTP_CODE=...
  if echo "$HTTP_CODE" | grep -qE '^(200|201)$'; then
    break   # success
  elif echo "$HTTP_CODE" | grep -q '^409$'; then
    echo "::warning::SHA conflict attempt $ATTEMPT — re-fetch + jitter retry" >&2
    sleep $(( RANDOM % 5 + 1 ))
  elif echo "$HTTP_CODE" | grep -qE '^4[0-9]{2}$'; then
    echo "::error::4xx client error (HTTP ${HTTP_CODE}) — no retry" >&2
    exit 1
  else
    # 5xx or network error
    IDX=$(( ATTEMPT - 1 ))
    DELAY=${BACKOFF_DELAYS[$IDX]:-8}
    echo "::warning::5xx/network error (HTTP ${HTTP_CODE}) attempt $ATTEMPT — backoff ${DELAY}s" >&2
    sleep "$DELAY"
  fi
done
```

### Exhausted fallback — 절대 silent drop 금지

**3 retry 모두 실패 시** (attempt 4 실패 후):

1. **stderr 에 `::error::` 출력** (GitHub Actions annotation 포함)
2. **exit 1 (non-zero exit)** — upstream workflow fail + caller 에게 실패 전파
3. **절대 silent drop 금지** — telemetry / retry-state-machine write 는 관찰가능성의 핵심. 조용히 무시하면 forcing function 이 무효화됨

```bash
echo "::error::Pattern A retries exhausted after 3 attempts (HTTP ${HTTP_CODE}) — story=${STORY_KEY}" >&2
exit 1
```

**downstream 처리 의무**: workflow caller 가 이 exit 1 을 uncaught 로 두면 GitHub Actions job 이 failure 상태로 기록됨. 이것이 의도된 동작 — silent loss 보다 visible failure.

### stderr capture 의무

**Pattern A retry loop 내부의 모든 diagnostic output = stderr 전용** (`>&2`).

| 출력 종류 | 채널 |
|---|---|
| `::notice::` (성공 알림) | stdout (GitHub Actions annotation 정상 동작) |
| `::warning::` (retry 경고, conflict 감지) | **stderr** (`>&2`) |
| `::error::` (4xx 즉시 실패, exhausted fallback) | **stderr** (`>&2`) |
| 디버그 / 진단 중간 출력 | **stderr** (`>&2`) |

**근거**: retry loop 의 경고/오류를 stdout 에 섞으면 JSONL content 파이프라인이 오염될 수 있음. stderr 분리 = stdout 을 순수 data channel 로 유지 (향후 retry helper script 의 pipe 안전성).

### Edge cases

| 상황 | 동작 |
|---|---|
| **SHA collision** (concurrent write — 409) | re-read file + SHA re-fetch → retry. jitter sleep. |
| **Empty file initialization race** (branch 방금 생성, file 미존재 — 404) | branch 생성 직후 file 미존재 = 정상 (initial write). SHA 없이 PUT (create). 단, 이미 file 이 생겼다가 사라진 404 = 즉시 fail (예외 처리 구분 필요). |
| **Atomic rename failure** (Contents API internal — 5xx) | retry with fresh SHA re-fetch. 이전 SHA 재사용 금지 (stale SHA 로 다시 PUT 하면 409 → infinite conflict 가능). |
| **Branch 미생성 상태에서 PUT** (404) | 사전 branch 생성 step 의 idempotent check 가 선행 의무. 선행 step 없이 PUT → 즉시 4xx exit. |
| **Base64 encode 오류** (local — python3 / base64 없음) | local execution error = retry 대상 아님. 즉시 exit 1 + stderr. |

### 면제 경계 (out-of-scope)

- **Local-only jsonl** (codeforge wrapper repo 의 `.codeforge/` flag 등) = cross-repo race 무관. file system advisory lock 또는 simple write OK
- **In-memory state** (Phase 1 first-attempt grace period 의 sleep 300 step state 등) = jsonl 영역 외
- **Read-only jsonl** (예: retro-retry-helper.sh 의 due entry parse) = race 무관

### 위반 시 처리

- DesignReviewPL = boundary issue P0 fail (cross-file pattern 부재 = 설계 지침 위반)
- CodeReviewPL = boundary issue P0 fail (Pattern A 미적용 implementation = lost-update risk)
- 회귀 spec = 본 페이지 cross-ref 명시 + 해당 ADR amendment + DesignReview re-run

## 관련 ADR

- **ADR-026 / CFP-74** — post-merge-counters.jsonl carrier (Pattern A implementation precedent — post-merge-telemetry.sh)
- **ADR-045 / CFP-138** — retro-attempts.jsonl carrier (Phase 1 follow-up amendment_id=1 — Pattern A 의무 명시)

## 변경 이력

- **2026-05-09 (CFP-289)**: Retry Semantics 섹션 추가 — 4xx/5xx HTTP status 구분 / exhausted fallback behavior / stderr capture 의무 / edge case 5종. Two sink (post-merge-telemetry.sh + retro-mandatory.yml) conformance 검증 동반 (EPIC-RESULTS-CFP-134 §5 Group A candidate #1).
- **2026-05-09**: 신설 (CFP-138 Phase 1 follow-up — FIX iter 2 boundary resolution from CodeReviewPL Iter 1 P0 A-2 + P0 C-1). ArchitectPLAgent 최종 판정 정합 — C-1 = 설계 (boundary), Pattern A 의무 명시.
