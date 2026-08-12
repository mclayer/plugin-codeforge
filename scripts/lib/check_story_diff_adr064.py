#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_story_diff_adr064.py — NG-19 / AC-7 story diff `ADR-064` 무접촉 스캐너.

CFP-2926 Story §8.0.8 (1) NG-19. 3-state verdict + execution-trace = `gate_verdict`
재사용(신규 verdict 체계 발명 0), repo-root 해석 = `check_fanout_subject_prose` 의
공용 primitive 재사용.

── 판정 목표 ──────────────────────────────────────────────────────────────
AC-7 은 "본 Story **산출물**이 `ADR-064` 를 변경하지 않는다" 를 요구한다(§5.3 —
"ADR-064 byte 무변경"이라는 **통제 밖** 조건에서 **본 Story diff 기준**으로 축소된
범위, P0-4). 따라서 본 게이트의 판정 대상은 repo 전역 상태가 아니라
★base…head diff 의 변경 파일 집합★ 이다.

  base…head diff 파일 집합 ∩ `archive/adr/ADR-064-*.md` == ∅

── ★0 파일 = RED★ (vacuous 참 금지) ───────────────────────────────────────
diff 해석 결과가 **0 파일**이면 위 교집합은 정의상 공집합이 되어 술어가 **vacuously
true** 가 된다. base 를 오지정하거나(존재하지 않는 ref → 해석 실패), head==base
이거나, 잘못된 repo 를 가리키면 게이트는 "ADR-064 미포함"을 외치며 GREEN 이 되는데
그것은 ★검사를 한 적이 없다는 뜻★ 이다 (설계리뷰 iter2 P1-A 가 지목한 지점).

  ⇒ 본 게이트는 `diff 파일 수 == 0` 을 **명시 분기**로 잡아 **RED** 를 낸다.
    ★"우연히 RED" 에 기대지 않는다 — 전용 reason(`EMPTY_DIFF`)으로 분리한다.★
    ★Story §8.0.8 NG-19 행이 empty-target 처분을 `RED` 로 명시 규정하므로,
    `gate_verdict.empty_target()`(INCONCLUSIVE) 이 아니라 RED 를 낸다 —
    `[154-AC-3]` non-GREEN floor 보다 **엄격한 방향**이다.★

── 4항목 이행 (ADR-154 번들) ──────────────────────────────────────────────
  `[154-AC-3]` empty-target : diff 파일 수 0 → **RED** (`EMPTY_DIFF`)
  `[154-AC-4]` unknown-input: base/head ref 미해석 · merge-base 실패 · git 실행
                             실패 · 경로 UTF-8 디코드 실패 · 제어문자 경로
                             → **fail-closed RED (exit 1)**. 조용한 행 제외 0.
  `[154-AC-5]` trace        : `diff_files`(numeric) · `base_sha` · `head_sha` ·
                             `merge_base_sha` · `forbidden_matches`(numeric)
  `[154-AC-13]` identity_probe: resolved-target echo — base ref 인자 → 실제 채택
                             후보 → resolved SHA, 실행한 diff 커맨드, 금지 패턴,
                             변경 파일 digest. ★base 오지정 = 전건 vacuous 이므로
                             base 해석 결과 자체가 곧 probe 다.★

── 이 게이트가 보증하지 않는 것 (정직 선언) ──────────────────────────────
  (a) **범위는 `base…head` diff 뿐**이다. `ADR-064` 의 repo 전역 byte 상태,
      다른 브랜치·다른 Story 의 변경, merge 이후 재변경은 보지 않는다. §11.A.5 의
      "절대 카운트(45/45)" 는 본 게이트 보증 밖 이동값이다.
  (b) **파일 경로 축만** 본다. `ADR-064` 의 *내용* 을 다른 파일에서 재서술·왜곡하는
      변경(예: 인용 왜곡)은 미검출 — 그 축은 NG-3 frozen 앵커(A-2)와 리뷰 lane 소관.
  (c) working tree 의 **uncommitted 변경은 대상 아님**(`git diff` 대상이 commit 간).
      커밋되지 않은 ADR-064 편집은 이 게이트를 통과한다.
  (d) base 를 **호출자가 공급**한다. 호출자가 head 와 동일한 base 를 주면 0 파일 →
      RED 로 떨어지므로 조용한 통과는 막지만, "옳은 base 인가"는 판정 밖이다
      (probe echo 로 **리뷰 가능**하게만 만든다).
  (e) **net-diff 의미론** — `base…head` 는 range 안 중간 상태를 접는다. 따라서
      "range 안에서 ADR-064 를 **새로 만들었다가** 다른 이름으로 rename 해 치운"
      경우 net diff 에 `ADR-064` 경로가 남지 않아 미검출이다 `[verified: 본 게이트
      합성 repo 실측 — base 에 파일 부재 시 create→rename 은 최종 이름만 노출]`.
      실 형상에서는 ADR-064 가 base(main)에 **이미 존재**하므로 삭제·rename 은
      구 경로가 delete 로 노출돼 검출된다(그 경로는 명명 테스트가 커버). 그럼에도
      "모든 접촉 형태를 검출한다"는 주장은 하지 않는다.
  (f) 자원 안전성: 경로 문자열 위 anchored 정규식 1개 + 선형 순회. 이는
      **bounded degradation 선언**이지 "임의 입력 무해(ReDoS-safe)" 단정이 아니다 —
      복잡도 회귀 self-test·wall-clock 벤치마크 미동반 (ADR-168 §결정 16
      honest-ceiling).
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gate_verdict as gv  # noqa: E402
import check_fanout_subject_prose as fanout  # noqa: E402

# Windows console(cp949) 호환 — 기존 scripts/lib 관례 답습.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-19:AC-7-story-diff-adr064-untouched"

# ★무접촉 대상★ — AC-7 이 지목하는 경로 패턴 (repo-relative posix, anchored).
FORBIDDEN_PATH_PATTERN = re.compile(r"^archive/adr/ADR-064-[^/]*\.md$")

DEFAULT_BASE = "origin/main"
DEFAULT_HEAD = "HEAD"

# reason 접두 (테스트·리뷰가 분기 식별에 쓰는 안정 토큰).
R_EMPTY_DIFF = "EMPTY_DIFF"
R_BASE_UNRESOLVED = "BASE_UNRESOLVED"
R_HEAD_UNRESOLVED = "HEAD_UNRESOLVED"
R_MERGE_BASE_FAILED = "MERGE_BASE_FAILED"
R_DIFF_FAILED = "DIFF_FAILED"
R_PATH_UNPARSEABLE = "PATH_UNPARSEABLE"
R_GIT_UNAVAILABLE = "GIT_UNAVAILABLE"
R_ADR064_TOUCHED = "ADR064_TOUCHED"


class GitInvocationError(Exception):
    """[154-AC-4] git 해석 불가 — fail-closed 로 사상하기 위한 예외."""

    def __init__(self, reason_code: str, detail: str) -> None:
        super().__init__("%s: %s" % (reason_code, detail))
        self.reason_code = reason_code
        self.detail = detail


def _git(repo_root: Path, args: List[str]) -> Tuple[int, bytes, str]:
    """git 실행 → (rc, stdout_bytes, stderr_text).

    ★stdout 을 bytes 로 받는다★ — 경로 바이트열의 UTF-8 디코드 실패를 게이트가
    직접 판정해야 하므로 (텍스트 모드의 replace/ignore 흡수 금지).
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise GitInvocationError(R_GIT_UNAVAILABLE, "git 미설치: %s" % (exc,))
    except OSError as exc:
        raise GitInvocationError(R_GIT_UNAVAILABLE, "git 실행 실패: %s" % (exc,))
    stderr = proc.stderr.decode("utf-8", errors="replace").strip()
    return proc.returncode, proc.stdout, stderr


def resolve_ref(repo_root: Path, ref: str) -> Optional[str]:
    """ref → commit SHA. 미해결 시 None (호출자가 fail-closed 처리)."""
    rc, out, _ = _git(repo_root, ["rev-parse", "--verify", "--quiet", "%s^{commit}" % (ref,)])
    if rc != 0:
        return None
    sha = out.decode("utf-8", errors="replace").strip()
    return sha or None


def resolve_base(repo_root: Path, base_arg: str) -> Tuple[Optional[str], str, List[str]]:
    """base 후보 해석. (sha, 채택 라벨, 시도한 후보 목록).

    `origin/main` 처럼 remote-tracking 를 그대로 주면 그것만 시도하고, `main` 처럼
    bare 이름이면 `origin/main` → `main` 순으로 시도한다 (CI/로컬 양쪽 수용).
    """
    base = base_arg.strip()
    candidates = [base] if "/" in base else ["origin/%s" % (base,), base]
    for candidate in candidates:
        sha = resolve_ref(repo_root, candidate)
        if sha:
            return sha, candidate, candidates
    return None, base, candidates


def diff_paths(repo_root: Path, from_sha: str, to_sha: str) -> List[str]:
    """`git diff --name-only -z --no-renames <from> <to>` → repo-relative posix 경로 목록.

    ★`-z`★ = NUL 구분 raw 경로 — `core.quotepath` 이스케이프 경로를 원천 배제한다.
    ★`--no-renames`★ = rename 을 delete+add 로 펼쳐 `ADR-064` 이름 변경을 놓치지 않는다.
    디코드 실패·제어문자 경로는 **조용히 제외하지 않고** fail-closed 로 올린다.
    """
    rc, out, err = _git(
        repo_root, ["diff", "--name-only", "-z", "--no-renames", from_sha, to_sha]
    )
    if rc != 0:
        raise GitInvocationError(R_DIFF_FAILED, "git diff rc=%d stderr=%s" % (rc, err))
    paths: List[str] = []
    for chunk in out.split(b"\0"):
        if not chunk:
            continue
        try:
            path = chunk.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GitInvocationError(
                R_PATH_UNPARSEABLE, "경로 UTF-8 디코드 실패: %r (%s)" % (chunk[:80], exc)
            )
        if any(ord(ch) < 0x20 for ch in path):
            raise GitInvocationError(
                R_PATH_UNPARSEABLE, "경로에 제어문자 포함: %r" % (path[:120],)
            )
        paths.append(path.replace("\\", "/"))
    return sorted(set(paths))


def evaluate(
    repo_root: Path, base_arg: str = DEFAULT_BASE, head_arg: str = DEFAULT_HEAD
) -> gv.GateResult:
    identity_probe = {
        "channel": "git diff base 해석 (base…head 변경 파일 집합)",
        "repo_root": str(repo_root).replace("\\", "/"),
        "base_ref_arg": base_arg,
        "head_ref_arg": head_arg,
        "forbidden_path_pattern": FORBIDDEN_PATH_PATTERN.pattern,
    }
    trace = {
        "diff_files": 0,
        "base_sha": None,
        "head_sha": None,
        "merge_base_sha": None,
        "forbidden_matches": 0,
    }

    # [154-AC-4] ref 미해석·git 실패 → fail-closed RED.
    try:
        base_sha, base_label, base_candidates = resolve_base(repo_root, base_arg)
        identity_probe["base_ref_candidates"] = base_candidates
        if base_sha is None:
            return gv.unknown_input(
                GATE_ID,
                "%s — diff base %r 미해석 (후보: %s). base 오지정 = 전건 vacuous 이므로 통과 금지"
                % (R_BASE_UNRESOLVED, base_arg, ", ".join(base_candidates)),
                trace=trace,
                identity_probe=identity_probe,
            )
        identity_probe["base_ref_resolved"] = base_label
        identity_probe["base_sha"] = base_sha
        trace["base_sha"] = base_sha

        head_sha = resolve_ref(repo_root, head_arg)
        if head_sha is None:
            return gv.unknown_input(
                GATE_ID,
                "%s — head ref %r 미해석" % (R_HEAD_UNRESOLVED, head_arg),
                trace=trace,
                identity_probe=identity_probe,
            )
        identity_probe["head_sha"] = head_sha
        trace["head_sha"] = head_sha

        rc, mb_out, mb_err = _git(repo_root, ["merge-base", base_sha, head_sha])
        if rc != 0:
            return gv.unknown_input(
                GATE_ID,
                "%s — merge-base(%s, %s) 실패 rc=%d stderr=%s"
                % (R_MERGE_BASE_FAILED, base_sha[:12], head_sha[:12], rc, mb_err),
                trace=trace,
                identity_probe=identity_probe,
            )
        merge_base = mb_out.decode("utf-8", errors="replace").strip()
        if not merge_base:
            return gv.unknown_input(
                GATE_ID,
                "%s — merge-base 출력 공백 (공통 조상 부재 추정)" % (R_MERGE_BASE_FAILED,),
                trace=trace,
                identity_probe=identity_probe,
            )
        identity_probe["merge_base_sha"] = merge_base
        trace["merge_base_sha"] = merge_base
        identity_probe["diff_command"] = (
            "git -C <repo_root> diff --name-only -z --no-renames %s %s"
            % (merge_base, head_sha)
        )

        paths = diff_paths(repo_root, merge_base, head_sha)
    except GitInvocationError as exc:
        return gv.unknown_input(
            GATE_ID,
            "%s (fail-closed): %s" % (exc.reason_code, exc.detail),
            trace=trace,
            identity_probe=identity_probe,
        )

    trace["diff_files"] = len(paths)
    identity_probe["diff_file_digest_sha256"] = fanout.digest_paths(paths)
    identity_probe["diff_file_sample"] = paths[:25]

    # ★[154-AC-3] empty-target — 0 파일 = vacuous 참 → RED (명시 분기).★
    if not paths:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "%s — diff 해석 결과 0 파일 (base=%s head=%s). 0 매치를 'ADR-064 미포함'으로 "
            "읽으면 vacuous 참 — 검사를 한 적이 없다는 뜻이므로 통과시키지 않는다"
            % (R_EMPTY_DIFF, base_label, head_arg),
            trace=trace,
            identity_probe=identity_probe,
        )

    hits = [p for p in paths if FORBIDDEN_PATH_PATTERN.match(p)]
    trace["forbidden_matches"] = len(hits)

    if hits:
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "%s — 본 Story diff 가 ADR-064 를 변경한다 (AC-7 위반): %s"
            % (R_ADR064_TOUCHED, ", ".join(hits)),
            trace=trace,
            identity_probe=identity_probe,
        )

    return gv.GateResult(
        GATE_ID,
        gv.PASS,
        "diff %d 파일 대조 — ADR-064 경로 0 건 (base=%s @%s → head=%s @%s)"
        % (len(paths), base_label, base_sha[:12], head_arg, head_sha[:12]),
        trace=trace,
        identity_probe=identity_probe,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="NG-19 / AC-7 story diff ADR-064 무접촉 스캐너"
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument(
        "--base",
        default=os.environ.get("BASE_REF") or os.environ.get("GITHUB_BASE_REF") or DEFAULT_BASE,
        help="diff base ref (기본 origin/main). ★오지정 = 전건 vacuous★",
    )
    parser.add_argument("--head", default=DEFAULT_HEAD)
    args = parser.parse_args(argv)

    repo_root = fanout.resolve_repo_root(args.repo_root)
    return gv.emit(evaluate(repo_root, args.base, args.head))


if __name__ == "__main__":
    sys.exit(main())
