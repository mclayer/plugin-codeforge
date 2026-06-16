#!/usr/bin/env bash
# test-check-plugin-version-bump-self.sh — CFP-2310 S2 (#2312) companion self-test
#
# scripts/check-plugin-version-bump-self.sh 의 eval 모드를 discriminating fixture
# (RED→GREEN proof) 로 검증한다. ADR-037 Amendment 2 §결정 A2-5 (TestContractArch) 렌즈 이행:
#   (a) RED  — lane agent 삭제 PR + lane 미bump = under-bump FAIL
#   (b) GREEN — lane agent 추가 + lane MINOR bump = PASS
#   (c) 면제 — archive/** only PR = no-surface-touch 면제 PASS (bump 0)
#   (d) coupling RED — lane agent 삭제 + wrapper root surface 동반 + wrapper 미bump = T2 FAIL
#   (e) MAJOR atomic RED — wrapper major bump 단독, sibling 8 미bump = A2-9 cross-check FAIL
#
# 각 fixture 디렉터리 scripts/test-fixtures/version-bump-self/<case>/ 안:
#   changed-files       : "<status>\t<path>" 줄들 (TAB 구분)
#   commit-msgs         : 멀티라인 commit 메시지 (Conventional Commits prefix)
#   bump-spec           : "<plugin>:<base>-><head>" 줄들
#   expected-verdict    : "PASS" 또는 "FAIL" 1줄
#   expected-violation  : (선택) 발동돼야 할 violation/메커니즘 마커 regex. 줄마다 1 패턴.
#                         각 패턴이 eval stdout(violation/로그 줄)에 grep -E 매치돼야 PASS.
#                         F-4 — verdict 뿐 아니라 "어느 메커니즘이 load-bearing 인가" 를 assert
#                         → wrong-reason FAIL(중복 경로로 우연 FAIL) 차단. fixture isolation 강제.
#   forbid-violation    : (선택) 발동되면 안 되는 마커 regex. 줄마다 1 패턴. 매치되면 self-test FAIL.
#                         (예: GREEN fixture 에 어떤 violation 도 발동 안 함을 강제.)
#
# production script (check-plugin-version-bump-self.sh) 와 동일 핵심 로직 compute_verdict 를
# eval 진입점으로 호출 — dead-suite 회피, 실 평가 경로 검증.
#
# Exit codes:
#   0 = 모든 fixture verdict + violation 마커 일치 (RED→GREEN proof + isolation 성립)
#   1 = 1+ fixture verdict 또는 violation 마커 불일치 (proof / isolation 깨짐)
#   2 = production script 부재 / fixture dir 부재 / fixture 파일 결손 (fail-loud)

set -uo pipefail

# Windows cp949 회피 — UTF-8 강제 (CI ubuntu 무영향, 로컬 자가검증 보호)
export LC_ALL="${LC_ALL:-C.UTF-8}" 2>/dev/null || true

# --root 로 전달할 repo root: 인자 1 우선, 없으면 현재 디렉터리
REPO_ROOT="${1:-$(pwd)}"
GATE="$REPO_ROOT/scripts/check-plugin-version-bump-self.sh"
FIXTURE_DIR="$REPO_ROOT/scripts/test-fixtures/version-bump-self"

# ── fail-loud 환경 점검 ──
if [ ! -f "$GATE" ]; then
    echo "[self-test] ERROR: production 게이트 script 부재: $GATE" >&2
    exit 2
fi
if [ ! -d "$FIXTURE_DIR" ]; then
    echo "[self-test] ERROR: fixture 디렉터리 부재: $FIXTURE_DIR" >&2
    exit 2
fi

PASS_COUNT=0
FAIL_COUNT=0

# fixture 디렉터리 loop (각 case 하위 디렉터리)
for case_dir in "$FIXTURE_DIR"/*/; do
    [ -d "$case_dir" ] || continue
    cname="$(basename "$case_dir")"

    changed_files="$case_dir/changed-files"
    commit_msgs="$case_dir/commit-msgs"
    bump_spec="$case_dir/bump-spec"
    expected_file="$case_dir/expected-verdict"

    # 4개 입력 파일 결손 = fail-loud (fixture 자체 결함)
    missing=""
    [ -f "$changed_files" ] || missing="$missing changed-files"
    [ -f "$commit_msgs" ]   || missing="$missing commit-msgs"
    [ -f "$bump_spec" ]     || missing="$missing bump-spec"
    [ -f "$expected_file" ] || missing="$missing expected-verdict"
    if [ -n "$missing" ]; then
        echo "[self-test] ERROR: fixture '$cname' 입력 파일 결손:$missing" >&2
        exit 2
    fi

    expected_verdict="$(head -1 "$expected_file" | tr -d '[:space:]')"
    if [ "$expected_verdict" != "PASS" ] && [ "$expected_verdict" != "FAIL" ]; then
        echo "[self-test] ERROR: fixture '$cname' expected-verdict 값 비정상: '$expected_verdict'" >&2
        exit 2
    fi

    # eval 모드 호출 — --root 는 worktree repo root (templates mirror / family ADR 실측 기준)
    eval_out="$(bash "$GATE" --eval \
        --changed-files "$changed_files" \
        --commit-msgs "$commit_msgs" \
        --bump-spec "$bump_spec" \
        --root "$REPO_ROOT" 2>/dev/null)"

    # stdout 마지막 VERDICT= 줄 파싱
    actual_verdict="$(printf '%s\n' "$eval_out" | grep -E '^VERDICT=' | tail -1 | cut -d= -f2)"

    # case 별 실패 사유 누적 (verdict + violation 마커)
    case_fail=""

    if [ "$actual_verdict" != "$expected_verdict" ]; then
        case_fail="verdict='$actual_verdict' != expected='$expected_verdict'"
    fi

    # F-4 — expected-violation 마커 assert (load-bearing 메커니즘 isolate)
    violation_file="$case_dir/expected-violation"
    if [ -f "$violation_file" ]; then
        while IFS= read -r pat; do
            pat="${pat%$'\r'}"
            [ -n "$pat" ] || continue
            case "$pat" in \#*) continue ;; esac   # 주석 줄 skip
            if ! printf '%s\n' "$eval_out" | grep -qE "$pat"; then
                case_fail="${case_fail:+$case_fail; }expected-violation 미발동: /$pat/"
            fi
        done < "$violation_file"
    fi

    # forbid-violation 마커 assert (발동되면 안 되는 패턴)
    forbid_file="$case_dir/forbid-violation"
    if [ -f "$forbid_file" ]; then
        while IFS= read -r pat; do
            pat="${pat%$'\r'}"
            [ -n "$pat" ] || continue
            case "$pat" in \#*) continue ;; esac
            if printf '%s\n' "$eval_out" | grep -qE "$pat"; then
                case_fail="${case_fail:+$case_fail; }forbid-violation 발동됨(금지): /$pat/"
            fi
        done < "$forbid_file"
    fi

    if [ -z "$case_fail" ]; then
        echo "[self-test] PASS: $cname (verdict=$actual_verdict)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "[self-test] FAIL: $cname — $case_fail" >&2
        # 디버그용 평가 로그 발췌 (불일치 시에만 노출)
        echo "  ── eval 로그 ──" >&2
        printf '%s\n' "$eval_out" | sed 's/^/  /' >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

echo ""
echo "[self-test] Summary: $PASS_COUNT pass, $FAIL_COUNT fail"

if [ "$PASS_COUNT" -eq 0 ] && [ "$FAIL_COUNT" -eq 0 ]; then
    echo "[self-test] ERROR: 평가된 fixture 0개 — fixture 디렉터리 비었거나 패턴 불일치" >&2
    exit 2
fi

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
exit 0
