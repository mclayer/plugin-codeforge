#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_cfp2963_ci_runner_provisioning_check.py — CFP-2963 Phase 2 §8.1.1 RTM self-test.

계약 SSOT:
  Change Plan `cfp-2963-mclats-arc-ci-runner.md` §8.1.1 RTM (codeforge-internal-docs
  커밋 `f6c61c97`) — wrapper-self dogfood 이므로 RTM 앵커 = Change Plan §8 (ADR-145 §결정10).
  AC 원문 = Story `CFP-2963.md` §5.3 AC-8 / AC-13 / AC-15.

명명 테스트 ↔ AC 매핑 (RTM §8.1.1 그대로 — 심볼명 변경 금지):
  - AC-8  : test_provisioning_check_private_unset_fails_loud
            test_provisioning_check_public_unset_passes
  - AC-13 : test_provisioning_check_require_windows_matrix_leg
            test_provisioning_check_http403_degrades_exit3
  - AC-15 : test_adr147_transitional_disposition_recorded_nonvacuous

검증 대상 (실 산출물):
  - `scripts/ci-runner-provisioning-check.sh` — ADR-147 §결정 2/4(ii)/11 provisioning
    invariant lint. visibility 분기 exit 계약 + `--require-windows` matrix leg +
    403 graceful degrade(exit 3).
  - `archive/adr/` — ADR-147 축별 처분 기록(R1~R9) 문면.

★ 정직 천장 (RTM §8.1.1 이 declare 한 부분 환원 — 확대 해석 금지):
  본 파일은 **도구 축(lint 도구의 판별력)** 과 **wrapper 파일 축(처분 문면 실재)** 만
  실증한다. 다음은 **실증하지 않는다**:
  - AC-8 의 조직 상태(roster 전수 변수 SET / org-level `^CI_RUNS_ON_` = 0) — org API 축.
  - AC-13 의 재정합 완료라는 조직 상태 — 분모 = AC-8 roster 술어, org API 축.
  - AC-15 처분의 **내용 타당성** — presence/문면 축까지만 (ADR-145 CEILING (i) 상속).
  즉 "본 테스트 GREEN = 컷오버 준비 완료" 는 **성립하지 않는다**.

anti-theater 규칙 (본 Story 가 반복 격퇴한 hollow-oracle class 봉인):
  - 검사 대상 = **실 산출물 경로**(`scripts/ci-runner-provisioning-check.sh` / `archive/adr/`).
    로직 사본을 만들어 사본을 검사하지 않는다. 부정 대조(mutant) 실행 시에만
    `CFP2963_PROVISIONING_SCRIPT` / `CFP2963_ADR_ROOT` 로 대상을 임시 치환한다.
  - 외부 접촉 0 — `gh` 는 PATH 경계 fake 로 치환(network·org·클러스터 접촉 없음).
    fake 미호출(=PATH 주입 실패 → 실 `gh`/org 상태 의존) 은 **호출 로그 assert 로 봉인**.
    org 상태에 의존해 통과하는 테스트는 그 자체가 결함이므로 fail-loud 로 만든다.
  - exit code **완전 일치**로 판정한다. 특히 3(graceful degrade) ≠ 2(도구 오류) ≠
    1(fail-loud) 를 각각 대조 leg 로 구별한다 — "필드 부재" 와 "도구 오류" 를
    구별 못 하는 오라클은 본 Story 의 기존 실사고 class 다.
  - AC-15 는 presence-grep 금지: 표 헤더에서 `처분` 열 위치를 해석해 **항목별 셀**을
    추출하고 닫힌 처분 어휘(채택/기각/이월) 를 요구한다. `R9` 문자열이 파일에 남아
    있어도 그 항의 처분 셀이 비면 FAIL 한다(공허 통과 봉인).

CI: lint.yml hook-unit-tests job (ubuntu-latest). 로컬 Windows 는 Git Bash 사용.
  ★ bare `bash` 신뢰 금지 — WSL relay(System32\\bash.exe) 는 PATH 주입 stub 을
  실행하지 못해 **빈 출력 거짓 통과**를 만든다. 후보 bash 를 "PATH 확장자-없는 stub
  실행" round-trip 으로 검증한 뒤에만 채택한다 (tests/scripts/
  test_cfp2701_story_form_parser_contract.py 의 동형 함정 회피 규율 승계 — 그 파일의
  probe 는 awk round-trip 이라 본 파일이 의존하는 mechanism 을 담보하지 못해 재작성).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

# tests/scripts/ → repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# 기본 대상 = 실 산출물. env 치환은 **부정 대조(mutant) 전용** (기본 경로 = 실물 유지).
SCRIPT = Path(
    os.environ.get("CFP2963_PROVISIONING_SCRIPT")
    or (REPO_ROOT / "scripts" / "ci-runner-provisioning-check.sh")
)
ADR_ROOT = Path(os.environ.get("CFP2963_ADR_ROOT") or (REPO_ROOT / "archive" / "adr"))

LINUX_VAR = "CI_RUNS_ON_LINUX_JSON"
WINDOWS_VAR = "CI_RUNS_ON_WINDOWS_JSON"

# 실 roster 표기 (Story §5.3 AC-8 분모 술어 예시) — 판정에는 무영향, 재현성용 고정 인자.
PRIVATE_REPO = "mclayer/mcfleet"
PUBLIC_REPO = "mclayer/plugin-codeforge"


# ============================================================ 파일 IO (LF 강제)

def _write_text_lf(path: Path, text: str) -> None:
    """LF 로 기록. ★ Windows 기본 newline 변환(CRLF)은 bash 스크립트를 파손시킨다
    (`$'\\r': command not found`) → stub 은 반드시 LF."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _make_executable(path: Path) -> None:
    os.chmod(path, 0o755)


# ============================================================ working-bash 해석

_PROBE_MARKER = "__cfp2963_stub_ok__"

_PROBE_STUB = f"""#!/usr/bin/env bash
printf '%s' '{_PROBE_MARKER}'
"""


def _candidate_bashes() -> list[str]:
    """후보 bash. Windows Git Bash 절대경로 우선(WSL relay 회피) → PATH 순."""
    cands: list[str] = []
    for p in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ):
        if os.path.exists(p):
            cands.append(p)
    which = shutil.which("bash")
    if which and which not in cands:
        cands.append(which)
    return cands


def _resolve_working_bash() -> str | None:
    """본 파일이 의존하는 mechanism 자체를 round-trip 한 bash 만 신뢰한다.

    mechanism = (a) bash 기동 (b) PATH 주입 디렉터리의 **확장자 없는** 스크립트를
    발견·실행. 둘 중 하나라도 안 되면 stub 이 조용히 무시되고 실 `gh` 가 불려
    거짓 결과를 만든다 → 후보에서 배제.
    """
    for bash in _candidate_bashes():
        with tempfile.TemporaryDirectory() as td:
            probe = Path(td) / "cfp2963probe"
            _write_text_lf(probe, _PROBE_STUB)
            try:
                _make_executable(probe)
            except OSError:
                continue
            env = dict(os.environ)
            env["PATH"] = str(Path(td)) + os.pathsep + env.get("PATH", "")
            try:
                res = subprocess.run(
                    [bash, "-c", "cfp2963probe"],
                    capture_output=True, text=True, encoding="utf-8",
                    env=env, timeout=60,
                )
            except Exception:
                continue
            if res.returncode == 0 and res.stdout.strip() == _PROBE_MARKER:
                return bash
    return None


_CANDIDATE_BASHES = _candidate_bashes()
WORKING_BASH = _resolve_working_bash()

_SKIP_NO_BASH = pytest.mark.skipif(
    not _CANDIDATE_BASHES,
    reason="bash 부재 환경 — 실 게이트 실행면은 ubuntu-latest (lint.yml hook-unit-tests)",
)


# ============================================================ `gh` 경계 fake

# 계약: `gh api <path> [--jq ...]` 만 응답. 그 밖의 호출 형태는 rc=97 로 fail-loud
# (스크립트가 예상 밖 경로로 gh 를 부르면 조용히 통과하지 않고 드러난다).
_GH_STUB = r"""#!/usr/bin/env bash
# CFP-2963 test double for `gh` — 경계 fake. network/org/cluster 접촉 0.
set -uo pipefail

printf '%s\n' "$*" >> "${GH_STUB_LOG:?GH_STUB_LOG unset}"

if [ "${1:-}" != "api" ]; then
  printf 'gh stub: unexpected invocation: %s\n' "$*" >&2
  exit 97
fi

path="${2:-}"
name=""
case "$path" in
  */actions/variables/*)
    name="${path##*/}"
    ref="GH_STUB_VAR_${name}"
    state="${!ref:-unset}"
    ;;
  repos/*)
    state="${GH_STUB_VISIBILITY_STATE:-ok}"
    ;;
  *)
    printf 'gh stub: unexpected api path: %s\n' "$path" >&2
    exit 97
    ;;
esac

case "$state" in
  ok)
    printf '%s\n' "${GH_STUB_VISIBILITY:?GH_STUB_VISIBILITY unset}"
    exit 0 ;;
  present)
    printf '{"name":"%s","value":"stub"}\n' "$name"
    exit 0 ;;
  unset)
    printf 'gh: Not Found (HTTP 404) — https://api.github.com/%s\n' "$path" >&2
    exit 1 ;;
  forbidden)
    printf 'gh: HTTP 403: Forbidden — must have admin rights to Repository. (https://api.github.com/%s)\n' "$path" >&2
    exit 1 ;;
  error)
    printf 'error connecting to api.github.com: dial tcp: lookup api.github.com: no such host\n' >&2
    exit 1 ;;
  *)
    printf 'gh stub: unknown state: %s\n' "$state" >&2
    exit 97 ;;
esac
"""


def _run_check(
    tmp_path: Path,
    *,
    repo: str,
    visibility: str = "private",
    visibility_state: str = "ok",
    variables: dict[str, str] | None = None,
    extra_args: tuple[str, ...] = (),
) -> tuple[int, str]:
    """실 산출물 스크립트를 `gh` 경계 fake 아래 실행. returns (rc, stdout+stderr)."""
    assert WORKING_BASH is not None, (
        "bash 후보는 실재하나 'PATH stub 실행' round-trip 실패 — 하네스 전제 파손. "
        "침묵 skip 금지(거짓 통과 봉인)."
    )
    assert SCRIPT.is_file(), f"검증 대상 산출물 부재: {SCRIPT}"

    bindir = tmp_path / "stubbin"
    bindir.mkdir(exist_ok=True)
    stub = bindir / "gh"
    _write_text_lf(stub, _GH_STUB)
    _make_executable(stub)

    log = tmp_path / "gh-stub-invocations.log"
    _write_text_lf(log, "")

    env = dict(os.environ)
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
    env["GH_STUB_LOG"] = str(log)
    env["GH_STUB_VISIBILITY"] = visibility
    env["GH_STUB_VISIBILITY_STATE"] = visibility_state
    for var_name, state in (variables or {}).items():
        env[f"GH_STUB_VAR_{var_name}"] = state

    res = subprocess.run(
        [WORKING_BASH, SCRIPT.as_posix(), "--repo", repo, *extra_args],
        capture_output=True, text=True, encoding="utf-8",
        env=env, timeout=120, cwd=str(REPO_ROOT),
    )
    combined = (res.stdout or "") + (res.stderr or "")

    # ── false-oracle 봉인 2종 (판정 전 무조건 검사) ──
    assert "gh stub: unexpected" not in combined and "gh stub: unknown state" not in combined, (
        f"경계 fake 가 예상 밖 형태로 호출됨 — 판정 무효.\n{combined}"
    )
    assert log.read_text(encoding="utf-8").strip(), (
        "gh 경계 fake 가 한 번도 호출되지 않음 — PATH 주입 실패로 실 gh/org 상태에 "
        f"의존했을 가능성. 판정 무효.\nrc={res.returncode}\n{combined}"
    )
    return res.returncode, combined


# ============================================================ AC-8

@_SKIP_NO_BASH
@pytest.mark.parametrize("visibility", ["private", "internal"])
def test_provisioning_check_private_unset_fails_loud(tmp_path: Path, visibility: str):
    """AC-8: self-hosted 대상(private/internal)에서 `CI_RUNS_ON_LINUX_JSON` UNSET =
    fail-loud(exit 1). 조용한 통과 0.

    Story §5.3 AC-8 ②③ (roster 전수 SET 확인 + `ci-runner-provisioning-check.sh` exit 0)
    의 **도구 축** — 변수 미설정이 exit 0 으로 새면 컷오버 시 hosted billing hard-block
    → required-check merge deadlock(AC-11) 이 무경보로 통과한다.

    ★ 판별 구조: 동일 fixture 에서 변수 present 면 exit 0 임을 함께 행사한다
    (무조건 FAIL 하는 lint 도 이 대조 leg 에서 죽는다).
    """
    rc, out = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility=visibility,
        variables={LINUX_VAR: "unset"},
    )
    assert rc == 1, f"UNSET 인데 fail-loud 아님 (rc={rc}) — provisioning gap 무경보 통과.\n{out}"
    assert "PROVISIONING GAP" in out, f"gap 진단 문면 부재 — loudness 미달.\n{out}"
    assert "FAIL-LOUD" in out, f"fail-loud 표지 부재.\n{out}"
    assert LINUX_VAR in out, f"미설정 변수명 미지목 — 조치 불가능한 경보.\n{out}"

    # 양성 대조 — 변수 SET 이면 통과해야 한다 (무조건-FAIL mutant kill).
    rc_ok, out_ok = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility=visibility,
        variables={LINUX_VAR: "present"},
    )
    assert rc_ok == 0, f"변수 SET 인데 통과 실패 (rc={rc_ok}) — 위양성.\n{out_ok}"
    assert "PROVISIONING GAP" not in out_ok, f"SET 상태에 gap 진단 발화 — 위양성.\n{out_ok}"


@_SKIP_NO_BASH
def test_provisioning_check_public_unset_passes(tmp_path: Path):
    """AC-8 ④: wrapper public repo 는 변수 UNSET 이 정상 → exit 0 (fail-loud 아님).

    Story §5.3 AC-8 ④ = "wrapper 2 public repo 변수 unset 유지" 확인. 이 분기가
    private 과 뭉개지면 public 에서 위양성 FAIL 이 나고, 반대로 lint 가 public 에
    SET 을 정상으로 보면 8-tuple required context 영구 pending(merge deadlock,
    §2.2 C-1 조건부 면역의 조건) 을 놓친다.

    ★ 판별 구조: (a) public+unset = PASS (b) public+SET = PASS 이되 WARN 발화
    (비-blocking 계약) (c) 동일 unset 이 private 에서는 exit 1 — visibility 분기가
    실제로 작동함을 대조로 고정한다.
    """
    rc, out = _run_check(
        tmp_path, repo=PUBLIC_REPO, visibility="public",
        variables={LINUX_VAR: "unset"},
    )
    assert rc == 0, f"public+unset 은 정상 상태인데 통과 실패 (rc={rc}) — 위양성 차단.\n{out}"
    assert "PASS" in out, f"PASS 판정 문면 부재.\n{out}"
    assert "FAIL-LOUD" not in out and "PROVISIONING GAP" not in out, (
        f"public 정상 상태에 gap 경보 발화.\n{out}"
    )

    # (b) public 에 변수 SET = delta-0 의도 위반 신호이나 비-blocking(PASS + WARN).
    rc_set, out_set = _run_check(
        tmp_path, repo=PUBLIC_REPO, visibility="public",
        variables={LINUX_VAR: "present"},
    )
    assert rc_set == 0, f"public+SET 은 비-blocking 계약인데 차단됨 (rc={rc_set}).\n{out_set}"
    assert "WARN" in out_set, f"public+SET 에 WARN 신호 부재 — 의도 위반이 무음 통과.\n{out_set}"

    # (c) visibility 분기 대조 — 동일 unset 이 private 에서는 fail-loud.
    rc_priv, out_priv = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private",
        variables={LINUX_VAR: "unset"},
    )
    assert rc_priv == 1, (
        f"동일 UNSET 이 private 에서도 exit 0 — visibility 분기 소실(AC-8 분기 계약 파손). "
        f"rc={rc_priv}\n{out_priv}"
    )


# ============================================================ AC-13

@_SKIP_NO_BASH
def test_provisioning_check_require_windows_matrix_leg(tmp_path: Path):
    """AC-13: `--require-windows` 는 matrix os-leg repo 의 `CI_RUNS_ON_WINDOWS_JSON`
    까지 필수화한다 (ADR-147 §결정 11).

    Story §5.3 AC-13 ① = roster 전 repo 에 lint exit 0 전건. matrix repo 에서
    windows leg 변수가 빠지면 group5(self-hosted-private) 라우팅을 상실하므로
    linux 만 보고 통과시키면 안 된다.

    ★ 판별 구조 3-leg: (a) 플래그 O + windows UNSET = exit 1 (b) **동일 fixture**
    플래그 X = exit 0 (플래그가 차이를 만든다 — 상시-요구 mutant kill)
    (c) 플래그 O + 양쪽 SET = exit 0 (상시-FAIL mutant kill).
    """
    fixture = {LINUX_VAR: "present", WINDOWS_VAR: "unset"}

    # (a) 플래그 O — windows leg 요구가 실제로 발동.
    rc_req, out_req = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private",
        variables=fixture, extra_args=("--require-windows",),
    )
    assert rc_req == 1, (
        f"--require-windows 인데 {WINDOWS_VAR} UNSET 이 통과 (rc={rc_req}) — "
        f"matrix leg 요구 소실.\n{out_req}"
    )
    assert WINDOWS_VAR in out_req, f"windows leg 변수명 미지목.\n{out_req}"
    assert "PROVISIONING GAP" in out_req, f"gap 진단 부재.\n{out_req}"

    # (b) 동일 fixture, 플래그 X — single-leg 거버넌스 repo 는 통과해야 한다.
    rc_noflag, out_noflag = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private", variables=fixture,
    )
    assert rc_noflag == 0, (
        f"--require-windows 미지정인데 windows 변수를 요구 (rc={rc_noflag}) — "
        f"single-leg repo 전수 위양성.\n{out_noflag}"
    )
    assert WINDOWS_VAR not in out_noflag, (
        f"플래그 없이 windows leg 를 검사 — 옵션 계약 파손.\n{out_noflag}"
    )

    # (c) 플래그 O + 양쪽 SET — 정상 provisioning 은 통과.
    rc_ok, out_ok = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private",
        variables={LINUX_VAR: "present", WINDOWS_VAR: "present"},
        extra_args=("--require-windows",),
    )
    assert rc_ok == 0, f"양쪽 SET 인데 통과 실패 (rc={rc_ok}) — 위양성.\n{out_ok}"


@_SKIP_NO_BASH
def test_provisioning_check_http403_degrades_exit3(tmp_path: Path):
    """AC-13: 권한 부족(HTTP 403) 은 exit 3 graceful degrade(WARN 비-blocking) —
    fail-loud(1) 로도 도구 오류(2) 로도 뭉개지 않는다.

    운영 귀결: 403 을 1 로 뭉개면 권한 없는 operator 실행이 전부 위양성 차단이 되고,
    403 을 "변수 없음"으로 뭉개면 **미설정과 조회 불가가 동일 판정**이 되어 roster
    전수 SET 주장이 근거를 잃는다.

    ★ 판별 구조 4-leg: (a) visibility 조회 403 = 3 (b) 변수 조회 403 = 3 이며
    gap 경보 미발화(≠1) (c) **403 이 아닌 gh 실패 = 2** — "필드 부재/권한 부족"과
    "도구 오류"를 구별한다 (d) 동일 경로의 404 = 1 — 3 과 1 이 실제로 갈린다.
    """
    # (a) visibility probe 403 → 3.
    rc_vis, out_vis = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private", visibility_state="forbidden",
    )
    assert rc_vis == 3, f"visibility 403 이 graceful degrade(3) 아님 (rc={rc_vis}).\n{out_vis}"
    assert "WARN" in out_vis, f"WARN(비-blocking) 신호 부재.\n{out_vis}"

    # (b) 변수 probe 403 → 3, 그리고 gap 경보로 오분류되지 않는다.
    rc_var, out_var = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private",
        variables={LINUX_VAR: "forbidden"},
    )
    assert rc_var == 3, f"변수 조회 403 이 graceful degrade(3) 아님 (rc={rc_var}).\n{out_var}"
    assert "PROVISIONING GAP" not in out_var and "FAIL-LOUD" not in out_var, (
        f"조회 불가(403)를 미설정(gap)으로 오분류 — 판정 근거 오염.\n{out_var}"
    )

    # (c) 403 이 아닌 gh 실패는 error(2) — degrade 로 삼키지 않는다.
    rc_err, out_err = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private",
        variables={LINUX_VAR: "error"},
    )
    assert rc_err == 2, (
        f"403 이 아닌 도구 오류가 exit 2 로 분류되지 않음 (rc={rc_err}) — "
        f"오류를 degrade/PASS 로 삼키면 무검증 통과.\n{out_err}"
    )

    # (d) 같은 probe 경로의 404 는 fail-loud(1) — 3 과 1 이 실제로 갈린다.
    rc_404, out_404 = _run_check(
        tmp_path, repo=PRIVATE_REPO, visibility="private",
        variables={LINUX_VAR: "unset"},
    )
    assert rc_404 == 1, (
        f"404(미설정)가 fail-loud(1) 아님 (rc={rc_404}) — 403/404 판정이 뭉개짐.\n{out_404}"
    )


# ============================================================ AC-15

_R_KEYS = tuple(f"R{i}" for i in range(1, 10))
# 닫힌 처분 어휘 — Story §5.3 AC-15 ② 원문("채택/기각/이월 포함").
_DISPOSITION_TOKENS = ("채택", "기각", "이월")
_SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")


def _norm_cell(cell: str) -> str:
    """마크다운 강조·공백 제거 정규화 (토큰 포함 판정 + 공백 셀 판정용)."""
    return re.sub(r"[*`\s]+", "", cell)


def _split_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [c.strip() for c in stripped.strip("|").split("|")]


def _collect_r_dispositions(md_text: str) -> dict[str, list[str]]:
    """`항` 키 열 + `처분` 열 헤더를 해석해 R-N → 처분 셀(들) 매핑을 구조 추출한다.

    presence-grep 이 아니다: 열 위치를 헤더에서 해석하고 **해당 항의 셀**만 읽는다.
    행이 헤더와 열 수가 다르면(파싱 이상) 수집하지 않는다 → 항 누락 = fail-closed.
    """
    found: dict[str, list[str]] = {}
    lines = md_text.splitlines()
    idx = 0
    while idx < len(lines):
        cells = _split_row(lines[idx])
        if not cells or _norm_cell(cells[0]) != "항":
            idx += 1
            continue
        disp_idx = next(
            (i for i, c in enumerate(cells) if "처분" in _norm_cell(c)), None
        )
        if disp_idx is None:
            idx += 1
            continue
        ncols = len(cells)
        row_idx = idx + 1
        sep = _split_row(lines[row_idx]) if row_idx < len(lines) else None
        if sep and all(_SEPARATOR_CELL.match(c) for c in sep):
            row_idx += 1
        while row_idx < len(lines):
            row = _split_row(lines[row_idx])
            if row is None:
                break
            if len(row) == ncols:
                key = _norm_cell(row[0])
                if re.fullmatch(r"R[1-9]", key):
                    found.setdefault(key, []).append(_norm_cell(row[disp_idx]))
            row_idx += 1
        idx = row_idx
    return found


def test_adr147_transitional_disposition_recorded_nonvacuous():
    """AC-15: ADR-147 과도기 처분이 `archive/adr/` 문서에 **항별로 비공허하게** 기록됨.

    Story §5.3 AC-15 원문 oracle:
      ① `archive/adr/` 에 ADR-147 amendment(또는 신규 ADR) 파일 실재
      ② 그 문서 안에 R1~R9 **각 항의 처분**(채택/기각/이월 포함)이 항 번호 명시로
         매핑 — 9/9 확인 가능해야 PASS (누락 항 = FAIL, 이월도 명시면 PASS)

    ★ 비공허 판정 정의 (presence-grep 과의 차이 — 본 테스트의 판별력 핵심):
      - 파일 전역 문자열 검색이 **아니다**. 표 헤더에서 `처분` 열 위치를 해석한 뒤
        각 R-N 행의 **자기 셀**만 읽는다.
      - 그 셀이 공백이면 FAIL — `R9` 라는 문자열이 파일에 그대로 남아 있어도 죽는다.
      - 그 셀이 닫힌 처분 어휘(채택/기각/이월) 중 하나를 포함해야 한다 — `TBD`/`—`
        같은 미정 placeholder 는 통과하지 못한다.
      - 9 항 zero-drop. 행이 사라지면 FAIL.
      - 어느 **한 문서**가 9/9 를 충족해야 한다 (여러 문서 조각 합산 불가 — AC 원문
        "그 문서 안에").

    ★ 정직 천장: presence/문면 축까지만이다. 처분 **내용의 타당성**(그 결정이 옳은지)
      은 본 테스트가 판정하지 않는다 (ADR-145 CEILING (i) 상속, RTM §8.1.1 명시).
    """
    assert ADR_ROOT.is_dir(), f"ADR 루트 부재: {ADR_ROOT}"
    docs = sorted(ADR_ROOT.glob("*.md"))
    assert docs, f"ADR 문서 0건: {ADR_ROOT}"

    winner: Path | None = None
    diagnostics: list[str] = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        if "ADR-147" not in text:  # 주제 결속 — ADR-147 처분 기록만 후보.
            continue
        rmap = _collect_r_dispositions(text)
        if not rmap:
            continue
        problems: list[str] = []
        for key in _R_KEYS:
            cells = rmap.get(key)
            if not cells:
                problems.append(f"{key}: 처분 표 행 부재(zero-drop 위반)")
                continue
            for cell in cells:  # 중복 기재 시 전부 비공허해야 한다.
                if not cell:
                    problems.append(f"{key}: 처분 셀 공백 (항 번호만 잔존 = 공허 기록)")
                elif not any(tok in cell for tok in _DISPOSITION_TOKENS):
                    problems.append(
                        f"{key}: 닫힌 처분 어휘{list(_DISPOSITION_TOKENS)} 부재 "
                        f"(셀={cell[:60]!r})"
                    )
        if not problems:
            winner = doc
            break
        diagnostics.append(f"- {doc.name}: " + "; ".join(problems))

    assert winner is not None, (
        "ADR-147 R1~R9 처분을 9/9 비공허하게 기록한 문서가 "
        f"{ADR_ROOT} 안에 없음 (AC-15 미이행).\n" + ("\n".join(diagnostics) or "- 후보 문서 0건")
    )
