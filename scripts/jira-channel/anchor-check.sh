#!/usr/bin/env bash
# CFP-2285 S4 (#2290) — Jira 결정 채널 stale anchor 재확인 검사
# 인용 출처: ADR-099 Amendment 1 §A1-3 (short open-window / late-answer 무시) 의 확장 +
#   설계 근거(확정): "stale anchor = 늦은 답 + 대상 Story/commit 변경(squash-merge 등) 시
#   자동 적용 말고 재확인". 즉 답이 늦게 도착했는데 그 사이 결정 대상(anchor)이 사라졌거나
#   닫혔으면(squash-merge 로 commit SHA 가 교체되거나 Story 가 closed) 그 답을 **자동 적용하지
#   않고** 사용자에게 재확인한다. 본 스크립트는 그 판정(anchor valid vs stale)만 결정론적으로
#   수행한다 — 재확인 결정 post 자체는 skill/Orchestrator 담당.
#
#   결정론적 repo/issue 사실 조회만 수행한다(MCP 호출 없음 — Jira post/poll 은 skill/Orchestrator).
#   commit 사실 = worktree git 실측(Read 류). story 사실 = gh CLI(가용 시) — 미가용/미인증 시
#   graceful degrade(commit 검사만으로 판정, warning stderr).
#
# 입력 (commit OR story 최소 1개 — 둘 다 없으면 입력오류):
#   $1 = commit SHA (선택) — 결정 대상 anchor 의 commit 식별자. 주어지면 commit 존재 검사.
#   $2 = story/issue key (선택) — 주어지면 issue open 여부 검사. 두 형식 모두 처리:
#          (a) bare 번호  예: 2290         → git origin 에서 도출한 owner/repo 에 대해 조회
#          (b) OWNER/REPO#번호  예: o/r#2290 → 그 repo 에 대해 조회 (cwd 비의존)
#   commit($1) 과 story($2) 가 둘 다 주어지면 AND — 둘 다 valid 여야 exit 0.
#   commit 없이 story 만 검사하려면 빈 commit 으로 호출: anchor-check.sh "" 2290
# 출력/exit:
#   anchor valid (검사 대상 모두 valid: commit 존재 / story open|미지정 / gh degrade) -> exit 0  (자동 적용 가능)
#   stale       (commit 부재 OR story closed)                                       -> exit 2  + 사유 stderr
#   입력 오류   (commit·story 둘 다 미지정/빈값)                                     -> exit 3
#
# NOTE: exit 0 = "anchor valid(자동 적용 가능)", exit 2 = "stale(재확인 필요)" 신호다.
#   deny-scan.sh(exit 0=clean / exit 2=BLOCKED) 와 동일한 exit 의미축(0=정상 진행 / 2=중단·재확인).
#   echo-guard.sh(exit 0=skip) 와는 의미축이 다름에 주의.
#
# ADR-061 §결정 1 — bash 우선(복잡 로직 아님, git/gh 사실 조회 + 분기).
set -euo pipefail

# ---- 입력 검증 (commit OR story 최소 1개 — 둘 다 없으면 입력오류) ----
COMMIT_SHA="${1:-}"
STORY_KEY="${2:-}"
if [ -z "$COMMIT_SHA" ] && [ -z "$STORY_KEY" ]; then
  echo "anchor-check: commit SHA(\$1) 와 story key(\$2) 가 둘 다 비었음 — 입력 오류 (최소 1개 필요)" >&2
  exit 3
fi

# ---- (A) commit 존재 검사 (worktree git 실측, commit 주어진 경우만) ----
# `git cat-file -e <sha>^{commit}` = 해당 객체가 commit 으로 존재하면 exit 0, 없으면 비0.
# squash-merge 등으로 원본 commit 이 사라지면(SHA 교체) 여기서 부재로 판정된다.
# commit 미지정(빈값) 이면 commit 검사를 건너뛰고 story 검사만으로 판정한다(commit-optional).
if [ -n "$COMMIT_SHA" ]; then
  if git cat-file -e "${COMMIT_SHA}^{commit}" 2>/dev/null; then
    :
  else
    echo "anchor-check: stale — commit 부재: ${COMMIT_SHA} (squash-merge/rebase 로 교체되었을 수 있음)" >&2
    exit 2
  fi
fi

# ---- (B) story/issue open 검사 (선택, gh CLI — graceful degrade) ----
# $2 가 주어지면 gh 로 issue state 를 조회한다. gh 미설치/미인증/조회 실패는 graceful degrade:
#   (commit 검사 통과 또는 commit 미지정)만으로 valid 판정하고 warning 을 stderr 로 남긴다(채널 가용성 우선).
#
# repo 고정: gh issue view 는 `--repo OWNER/REPO` 없이 호출하면 cwd-default repo 에 의존한다.
#   결정 채널은 임의 cwd 에서 호출될 수 있으므로 repo 를 명시 고정한다:
#     (a) $2 가 OWNER/REPO#번호 형식 → 그 repo 를 사용(cwd 비의존).
#     (b) $2 가 bare 번호 → git origin remote 에서 owner/repo 를 도출해 사용.
#   둘 다 도출 실패하면 graceful degrade(story 검사 생략).
if [ -n "$STORY_KEY" ]; then
  ISSUE_NUM=""
  ISSUE_REPO=""
  case "$STORY_KEY" in
    */*'#'*)
      # OWNER/REPO#번호 형식 — repo 와 번호를 분리.
      ISSUE_REPO="${STORY_KEY%#*}"   # '#' 앞 = OWNER/REPO
      ISSUE_NUM="${STORY_KEY##*#}"   # '#' 뒤 = 번호
      ;;
    *)
      # bare 번호 — git origin 에서 owner/repo 도출.
      ISSUE_NUM="$STORY_KEY"
      ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"
      if [ -n "$ORIGIN_URL" ]; then
        # https://github.com/OWNER/REPO(.git) 또는 git@github.com:OWNER/REPO(.git) → OWNER/REPO.
        ISSUE_REPO="$ORIGIN_URL"
        ISSUE_REPO="${ISSUE_REPO%.git}"                 # 후행 .git 제거
        ISSUE_REPO="${ISSUE_REPO#*://*/}"               # scheme://host/ 접두 제거 (https 형)
        ISSUE_REPO="${ISSUE_REPO#*:}"                   # git@host: 접두 제거 (ssh 형)
        # 위 두 치환 후 남은 형태가 OWNER/REPO 인지 확인(슬래시 1개 + '#'·공백·':' 없음).
        case "$ISSUE_REPO" in
          */*) : ;;
          *) ISSUE_REPO="" ;;
        esac
      fi
      ;;
  esac

  if ! command -v gh >/dev/null 2>&1; then
    echo "anchor-check: warning — gh CLI 미설치, story open 검사 생략(commit 검사만으로 판정): ${STORY_KEY}" >&2
  elif [ -z "$ISSUE_REPO" ]; then
    echo "anchor-check: warning — repo 도출 실패(origin remote 부재/형식 불명), story open 검사 생략: ${STORY_KEY}" >&2
  else
    # gh issue view 가 실패(미인증/존재X/네트워크/부재 repo)하면 STATE 가 비어 graceful degrade.
    STATE="$(gh issue view "$ISSUE_NUM" --repo "$ISSUE_REPO" --json state --jq '.state' 2>/dev/null || true)"
    if [ -z "$STATE" ]; then
      echo "anchor-check: warning — gh issue 조회 실패(미인증/부재/네트워크), story open 검사 생략: ${ISSUE_REPO}#${ISSUE_NUM}" >&2
    else
      # gh 의 state 는 대문자(OPEN/CLOSED). 대소문자 무시 비교로 closed 판정.
      if printf '%s' "$STATE" | grep -qiE '^closed$'; then
        echo "anchor-check: stale — story closed: ${ISSUE_REPO}#${ISSUE_NUM} (state=${STATE}) — 답이 닫힌 대상에 늦게 도착" >&2
        exit 2
      fi
    fi
  fi
fi

# (commit 미지정 | commit 존재) AND (story 미지정 | story open | gh degrade) → anchor valid.
exit 0
