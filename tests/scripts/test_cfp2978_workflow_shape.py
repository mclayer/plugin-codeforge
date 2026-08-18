#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CFP-2978 AC-10 workflow 구조 오라클 — W-14 (pytest 배선면).

★ 본 파일은 구조 술어를 **재구현하지 않는다**. 유일한 추출기는
  `scripts/lib/workflow_shape.py` (W-13) 이고, 본 파일은 그 `load_workflow_shape()`
  가 돌려준 `WorkflowShape` 위에 **assert leg 만** 세운다.

  구 판 이력(수리 대상): 본 파일은 자체 `extract_workflow_shape()` + bare
  `yaml.safe_load()` 를 재구현하고 있었다. bare `safe_load` 는 W-13 비협상 계약 (2)
  가 금지한 형태이며(중복 키 silent last-wins), 그 판의 GREEN 은 W-13 오라클이
  아니라 **그 흉내**를 검증했다. 결과로 mutant 11 종(M-envfile / M-envfile-inplace /
  M-envfile-blk / M-envkey / M-envctr / M-own1 / M-own2 / R-7 / M-dup-same / M-13k /
  M-13l)이 pytest 면에서 조용히 통과했다 — 그 결함의 수리가 본 판이다.

────────────────────────────────────────────────────────────────────────────
정의역 선언 (§8.D rule 3)
────────────────────────────────────────────────────────────────────────────
전 leg 의 정의역 = **구조(structure)**. 관측 채널 = W-13 `DupSafeLoader` 파싱 산출
(`WorkflowShape` 필드). text-grep 정의역 leg 은 본 파일에 **부분 존재**한다.
예외 = `test_f0_*` (본 파일 소스 자기 점검, 정의역 = text) + `test_w16_e_*`
(wrapper step run 문면 스캔).

────────────────────────────────────────────────────────────────────────────
leg 인벤토리 — shape 14 필드 전건 피복
────────────────────────────────────────────────────────────────────────────
AC-10 은 "4 repo backfill 을 거쳐 로컬 개조가 보존되는가" 를 묻는다. 실측 결과
shape 14 필드는 정확히 두 부류로 갈린다:

  (가) **repo 별 차등 필드 4종** — `top_concurrency` · `concurrency_paths` ·
       `timeout_paths` · `runs_on`.  → E1~E8 leg (로컬 개조 자체)
  (나) **4 repo 불변 필드 10종** — `job_ids` · `coe_paths` · `job_if` · `step_if` ·
       `env_keys` · `container_env_keys` · `env_file_keys` · `step_shell` ·
       `defaults_run_shell` · `job_defaults_run_shell`.  → F1~F10 leg (보존 불변식)

(나) 는 구 판에서 **계산만 되고 조회 0** 이었다(사문 필드). 주입·이동 mutant 가
전부 이 집합에 착지했으므로 사문 = 미검출과 1:1 대응이었다. 본 판은 (나) 를
**4 fixture 전건에 대해 핀 리터럴 동일성**으로 못박는다 — 핀 값의 출처는
pristine fixture 실측(`python scripts/lib/workflow_shape.py <fixture>`)이다.

────────────────────────────────────────────────────────────────────────────
술어형 규칙 준수 (§8.D)
────────────────────────────────────────────────────────────────────────────
* rule 1 (카디널리티) — 개수는 **경로 집합의 파생값**으로만 쓰고, 실패 보고는 항상
  위반 **경로를 열거**한다. E5 는 `len(...) == 2` 가 아니라 경로→값 매핑 전문
  동일성으로 판정하므로 relocation(R-6)이 카디널리티 불변인 채로도 관측된다.
* rule 2 (부재-assert) — `== {}` / `is None` leg 은 전부 양성 앵커(`_anchor_*`)와
  AND 로만 성립한다. 앵커 없는 부재-assert 는 미파싱 상태에서 공허 참이 된다.
* rule 4 (관측 가능성) — 관측 채널은 W-13 이 실제로 emit 하는 필드뿐이다.
  W-13 이 emit 하지 않는 축(예: composite action 내부 `continue-on-error`,
  여러 줄 블록 리다이렉트 `$GITHUB_ENV` 기입)은 **declared 잔여**이며 본 파일이
  GREEN 을 내는 것은 검출 성공이 아니다 — W-13 docstring "알려진 실패 모드" 참조.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

# ── W-13 결속 (자체 재구현 금지 — 본 파일의 존재 이유) ───────────────────────
# `scripts/lib/workflow_shape.py` 를 보유한 조상 디렉터리를 찾아 sys.path 에 넣는다.
# (tests/scripts/conftest.py 도 같은 주입을 하지만, 본 파일이 conftest 없이 단독
#  실행될 때도 성립해야 하므로 자족 해결한다.)
# 미발견 = **fail-closed**. skip 이 아니다 — "오라클 본체를 못 읽은 상태"는 GREEN 이
# 아니라는 INV-5 를 pytest 수집 ERROR 로 종결한다.
def _locate_w13_root() -> Path:
    here = Path(__file__).resolve()
    for cand in here.parents:
        if (cand / "scripts" / "lib" / "workflow_shape.py").is_file():
            return cand
    raise RuntimeError(
        "W-13 모듈 미발견: scripts/lib/workflow_shape.py 를 보유한 조상 디렉터리가 없다. "
        f"(탐색 기점={here}) — 본 오라클은 W-13 없이 성립하지 않으며 자체 재구현하지 않는다."
    )


_W13_ROOT = _locate_w13_root()
if str(_W13_ROOT / "scripts" / "lib") not in sys.path:
    sys.path.insert(0, str(_W13_ROOT / "scripts" / "lib"))

from workflow_shape import (  # noqa: E402  (sys.path 주입 이후여야 함)
    ShapeError,
    WorkflowShape,
    dup_safe_load,
    load_workflow_shape,
    runs_on_local_delta,
)

# ── fixture 결속 ─────────────────────────────────────────────────────────────
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "cfp2978"

CONSUMER_FIXTURES = {
    "mctrader": "mctrader-sentinel.yml",
    "mctrader-backtest": "mctrader-backtest.yml",
    "mctrader-market": "mctrader-market.yml",
    "mctrader-engine": "mctrader-engine.yml",
}
ALL_REPOS = tuple(CONSUMER_FIXTURES)

# ── W-16 wrapper 정의역 확장 ──────────────────────────────────────────────────
WRAPPER_WORKFLOWS = {
    "wrapper-canonical": ".github/workflows/parallel-work-sentinel-check.yml",
    "wrapper-twin": "templates/github-workflows/parallel-work-sentinel-check.yml",
}
WRAPPER_FACES = tuple(WRAPPER_WORKFLOWS)

JOB1 = "parallel-work-sentinel"
JOB2 = "parallel-work-sentinel-test"

# ── 핀 리터럴 (§8.A — 출처 = pristine fixture 실측) ──────────────────────────
PIN_MCTRADER_GROUP = (
    "${{ github.workflow }}-"
    "${{ github.event_name == 'pull_request' && github.event.pull_request.number "
    "|| github.run_id }}"
)
# wrapper 정본 template 표현식 (github.ref 축) — mctrader 로컬 개조가 이것으로
# 되돌아가면 AC-10 위반. E3 의 부동등 대상.
TEMPLATE_GROUP = "${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}"

# 정본 runs-on (wrapper template 상속값)
CANON_RUNS_ON_JOB1 = "${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || '[\"ubuntu-latest\"]') }}"
CANON_RUNS_ON_JOB2 = "ubuntu-latest"
CANON_RUNS_ON = {JOB1: CANON_RUNS_ON_JOB1, JOB2: CANON_RUNS_ON_JOB2}

# (가) repo 별 차등 — mctrader 전용
PIN_MCTRADER_TIMEOUT_PATHS: Dict[str, Any] = {
    f"jobs.{JOB1}.timeout-minutes": 10,
    f"jobs.{JOB2}.timeout-minutes": 10,
}

# (나) 4 repo 불변 — F1~F10 핀
PIN_JOB_IDS: List[str] = [JOB1, JOB2]
PIN_COE_PATHS: List[str] = [f"jobs.{JOB1}.steps[2].continue-on-error"]
PIN_COE_OWNED = {JOB1: PIN_COE_PATHS, JOB2: []}

_IF_BYPASS = (
    "${{ contains(github.event.pull_request.labels.*.name, "
    "'hotfix-bypass:parallel-work-sentinel-pickup') }}"
)
_IF_NOT_BYPASS = (
    "${{ !contains(github.event.pull_request.labels.*.name, "
    "'hotfix-bypass:parallel-work-sentinel-pickup') }}"
)
PIN_JOB_IF: Dict[str, Any] = {
    JOB1: None,
    JOB2: "github.repository == 'mclayer/plugin-codeforge'",
}
PIN_STEP_IF: Dict[str, List[Any]] = {
    JOB1: [None, _IF_BYPASS, _IF_NOT_BYPASS],
    JOB2: [None, None, None],
}
# job1.steps[2] = sentinel 실행 step (PR_TITLE/GH_TOKEN 주입 + 큰 run 블록 보유)
RUN_STEP_ENV_PATH = f"jobs.{JOB1}.steps[2]"
PIN_ENV_KEYS: Dict[str, List[str]] = {
    "workflow": ["SENTINEL_TIER"],
    RUN_STEP_ENV_PATH: ["PR_TITLE", "GH_TOKEN"],
}
PIN_CONTAINER_ENV_KEYS: Dict[str, List[str]] = {}
PIN_ENV_FILE_KEYS: Dict[str, List[str]] = {}
PIN_STEP_SHELL: Dict[str, List[Any]] = {JOB1: [None, None, None], JOB2: [None, None, None]}
PIN_DEFAULTS_RUN_SHELL = None
PIN_JOB_DEFAULTS_RUN_SHELL: Dict[str, Any] = {JOB1: None, JOB2: None}

# ── W-16 wrapper 핀 리터럴 (§8.A — 출처 = pristine wrapper 실측, commit 8a9cbf944) ──
# wrapper job_ids = consumer 와 동일 (PIN_JOB_IDS 재사용)
# wrapper coe_paths = consumer 와 동일 (PIN_COE_PATHS 재사용)
# wrapper step_shell: job1=[None]*3, job2=[None]*6
PIN_WRAPPER_STEP_SHELL: Dict[str, List[Any]] = {JOB1: [None, None, None], JOB2: [None] * 6}

# W-16 job2 step 명 (텍스트 정의역)
PIN_WRAPPER_JOB2_STEP_NAMES = {
    2: "Install test dependencies",
    3: "Collect pytest tests (W-3b-1, verify node IDs present)",
    4: "Run pytest tests (W-3b)",
}

# ── W-16 A8 idioms (bash rc 흡수 관용구) — 6종 ───────────────────────────────
#
# W-13 파서로는 관측 불가(composite action/여러 줄 리다이렉트 미포섭)이므로
# 텍스트 스캔으로 정의역 보완.
#
# ★ FIX Iter 4 (CR-1) — **공백 관용 regex 로 전환**. 구 판은 needle 을 공백 1개
#   고정 리터럴 바이트열로 두어, 셸이 동일하게 해석하는 표기 변형이 전부 샜다.
#   firsthand 실측 (`-q <idiom>` 을 W-3b step 에 주입, `bash -e` rc 는 3종 모두 0):
#       `-q || true`   -> pytest 2 failed  (검출)
#       `-q ||  true`  -> pytest 75 passed (BYPASS)   ← 공백 2
#       `-q||true`     -> pytest 75 passed (BYPASS)   ← 공백 0
#   즉 셸은 셋을 구별하지 않는데 검출기는 정확히 한 바이트열에만 반응했다.
#   ⇒ 6종 전건을 regex 로 통일하고 공백을 `\s` 로 관용한다 (리터럴 `in` 분기 소멸).
#
# ★ `set` 항목만 `\b` 배치가 비대칭인 이유 (의도적):
#     - **선두** `\b` 필요: 없으면 `offset +e` 가 오검출된다.
#     - **말미** `\b` 금지: 붙이면 `set +ex`(errexit+xtrace 동시 해제 — 실 흡수형)를
#       놓친다. 구 판 리터럴 `in` 검사는 `set +ex` 를 잡았으므로 말미 `\b` 는
#       검출력 **회귀**다. 두 probe 가 이 비대칭을 각각 고정한다.
#
# 정의역 (§8.D rule 3 — 정직 선언). 아래 문면은 실패 메시지에 실려 나간다.
_A8_DOMAIN = (
    "A8 정의역 = **단일 step `run` 문면의 공백 관용 텍스트 스캔**. "
    "행 계속(`\\` 줄바꿈 이음)·변수 간접(`$X`/`${X}` 로 관용구를 우회 조립)·"
    "here-doc 내부 은닉은 **정의역 밖**이며 본 스캔이 GREEN 을 내는 것은 "
    "검출 성공이 아니다. 또한 6종은 **열거이지 전수가 아니다** — "
    "`! false` · `set +o errexit` · `trap ... ERR` 등 rc 흡수 표면은 "
    "애초에 열거에 없다(이 사실 자체를 선언으로 남긴다)."
)

_A8_IDIOMS = (
    (r"\|\|\s*true\b", "|| true"),
    (r"\|\|\s*:", "|| :"),
    (r"\|\|\s*exit\s+0\b", "|| exit 0"),
    (r";\s*true\b", "; true"),
    (r"\bset\s+\+e", "set +e"),
    (r"\bif\b[^\n]*;\s*then\b", "if …; then"),
)

# ★ 술어 자기판별 probe — **자기 display 만 되먹이면 순환 확인**이다.
#   구 판 probe 는 `f"echo hello {idiom_display} world"` 로 공백 1 변형만 시험해
#   위 BYPASS 2종을 원리적으로 발견할 수 없었다. 공백 0 / 2 / tab 을 명시 등재한다.
_A8_PROBE_POSITIVES: Dict[str, List[str]] = {
    "|| true": [
        "python3 -m pytest -q || true",     # 공백 1
        "python3 -m pytest -q ||  true",    # 공백 2  ← 구 판 BYPASS
        "python3 -m pytest -q||true",       # 공백 0  ← 구 판 BYPASS
        "python3 -m pytest -q ||\ttrue",    # tab
    ],
    "|| :": [
        "python3 -m pytest -q || :",
        "python3 -m pytest -q ||  :",
        "python3 -m pytest -q||:",
        "python3 -m pytest -q ||\t:",
    ],
    "|| exit 0": [
        "python3 -m pytest -q || exit 0",
        "python3 -m pytest -q ||  exit  0",
        "python3 -m pytest -q||exit 0",
        "python3 -m pytest -q ||\texit\t0",
    ],
    "; true": [
        "python3 -m pytest -q ; true",
        "python3 -m pytest -q ;  true",
        "python3 -m pytest -q;true",
        "python3 -m pytest -q ;\ttrue",
    ],
    "set +e": [
        "set +e",
        "set  +e",
        "set\t+e",
        "set +ex",                          # ★ 말미 `\b` 를 붙이면 여기서 놓친다
    ],
    "if …; then": [
        "if false; then :; fi",
        "if false ;  then :; fi",
        "if false;then :; fi",
        "if false ;\tthen :; fi",
    ],
}

# ★ 음성 probe — 술어가 **아무거나 잡는 항진 needle** 이 아님을 고정한다.
#   (양성 probe 만 있으면 `re.compile(".")` 도 전 probe 를 통과한다.)
_A8_PROBE_NEGATIVES: Dict[str, List[str]] = {
    "|| true": ["python3 -m pytest -q || truexyz", "echo trueish"],
    "|| :": ["python3 -m pytest -q | : "],          # 단일 파이프는 rc 흡수 관용구 아님
    "|| exit 0": ["python3 -m pytest -q || exit 1"],
    "; true": ["python3 -m pytest -q ; truexyz"],
    "set +e": ["offset +e", "set -e"],              # ★ 선두 `\b` 를 빼면 offset 오검출
    "if …; then": ["verify if present"],
}


# ── 로딩 (W-13 단일 진입점) ──────────────────────────────────────────────────
def shape_of(repo: str) -> WorkflowShape:
    """`repo` fixture 의 `WorkflowShape` (W-13 `load_workflow_shape` 단일 경로).

    전제 위반(P-1~P-6)은 `ShapeError` 로 전파돼 pytest FAILED = RED 가 된다.
    삼키지 않는다 — 읽지 못한 상태의 종결은 GREEN 이 아니다 (INV-5).
    """
    return load_workflow_shape(str(FIXTURE_DIR / CONSUMER_FIXTURES[repo]))


def wrapper_shape_of(face: str) -> WorkflowShape:
    """`face` wrapper workflow 의 `WorkflowShape` (W-13 `load_workflow_shape` 단일 경로).

    W-16 정의역 확장. wrapper 자신의 workflow 2 면(canonical + twin template).
    """
    return load_workflow_shape(str(_W13_ROOT / WRAPPER_WORKFLOWS[face]))


# ── 양성 앵커 (§8.D rule 2 — 부재-assert 전용) ───────────────────────────────
def _anchor_jobs(shape: WorkflowShape, repo: str) -> None:
    """"job 을 실제로 파싱해 관측했다" 양성 앵커."""
    assert shape.job_ids == PIN_JOB_IDS, (
        f"[{repo}] 양성 앵커 실패 — job_ids={shape.job_ids}, 기대={PIN_JOB_IDS}. "
        "이 앵커 없이는 뒤따르는 부재-assert 가 공허 참이 된다 (§8.D rule 2)."
    )


def _anchor_steps(shape: WorkflowShape, repo: str) -> None:
    """"step 을 실제로 열거했다" 양성 앵커 (step 수 3/3)."""
    _anchor_jobs(shape, repo)
    counts = {jid: len(shape.step_if.get(jid, [])) for jid in PIN_JOB_IDS}
    assert counts == {JOB1: 3, JOB2: 3}, (
        f"[{repo}] 양성 앵커 실패 — step 수={counts}, 기대={{'{JOB1}': 3, '{JOB2}': 3}}"
    )


def _anchor_run_step(shape: WorkflowShape, repo: str) -> None:
    """"`run:` 문면을 보유한 step 을 실제로 스캔했다" 양성 앵커.

    `env_file_keys` 부재 leg 전용. 스캔 대상 step 자체가 사라지거나 인덱스가 밀리면
    "기입 없음" 이 공허 참이 되므로, 그 step 의 실재를 먼저 세운다.
    """
    _anchor_steps(shape, repo)
    assert RUN_STEP_ENV_PATH in shape.env_keys, (
        f"[{repo}] 양성 앵커 실패 — 스캔 대상 run step {RUN_STEP_ENV_PATH} 부재 "
        f"(env_keys 경로={sorted(shape.env_keys)}). env_file_keys 부재 판정이 공허해진다."
    )


def _anchor_wrapper_steps(shape: WorkflowShape, face: str) -> None:
    """"wrapper job2 의 step 을 실제로 열거했다" 양성 앵커 (step 수 6).

    W-16 wrapper 전용. job2 (parallel-work-sentinel-test) 는 6 step을 보유.
    """
    _anchor_jobs(shape, face)
    counts = {jid: len(shape.step_if.get(jid, [])) for jid in PIN_JOB_IDS}
    assert counts == {JOB1: 3, JOB2: 6}, (
        f"[{face}] 양성 앵커 실패 — step 수={counts}, 기대={{'{JOB1}': 3, '{JOB2}': 6}}"
    )


# ════════════════════════════════════════════════════════════════════════════
# F0 — 오라클 결속 자기 점검 (born-broken 가드)
#      정의역 = text (본 파일 소스) + 모듈 동일성
# ════════════════════════════════════════════════════════════════════════════
def test_f0_oracle_bound_to_w13_not_reimplemented():
    """W-14 가 W-13 을 **실제로 호출**하는지 (자체 재구현 회귀 차단).

    구 판 결함의 직접 회귀 가드다. 이 leg 이 없으면 누군가 다시 로컬 추출기를
    심어도 나머지 leg 이 전부 GREEN 인 채 "흉내를 검증" 하는 상태로 되돌아간다.
    """
    # (1) 추출기 모듈 동일성 — W-13 파일에서 왔는가
    assert load_workflow_shape.__module__ == "workflow_shape", (
        f"load_workflow_shape 의 모듈이 workflow_shape 가 아님: {load_workflow_shape.__module__}"
    )
    w13_file = Path(sys.modules["workflow_shape"].__file__).resolve()
    assert w13_file.parts[-3:] == ("scripts", "lib", "workflow_shape.py"), (
        f"W-13 모듈 경로가 scripts/lib/workflow_shape.py 가 아님: {w13_file}"
    )

    # (2) 본 파일 안에 로컬 추출기 재구현이 없는가 (text 정의역)
    #
    # ★ 금지 패턴은 **조각으로 조립**한다. 리터럴로 적으면 이 leg 자신의 소스를
    #   검출해 무조건 RED 가 된다 (자기참조 함정 — firsthand 실측으로 확인).
    #   그 결과 본 스캔의 정의역에서 **자기 자신은 구조적으로 제외**된다:
    #   "재구현이 전혀 없다" 의 증명이 아니라 "구 판 형태로의 회귀가 없다" 의 가드다.
    _DEF = "def "
    banned_names = ("extract_workflow_shape", "load_workflow_yaml")

    # 술어 비공허 통제 — 조립된 needle 이 실제 def 문면을 잡는지 (오타·조립 실패 차단).
    # 이 통제가 없으면 needle 철자가 틀려도 스캔이 조용히 항상 통과한다.
    for name in banned_names:
        probe = f"{_DEF}{name}(workflow_yaml: dict) -> dict:\n    return {{}}\n"
        assert (_DEF + name) in probe, f"스캔 술어 고장: needle `{_DEF}{name}` 이 합성 def 를 못 잡음"

    src = Path(__file__).read_text(encoding="utf-8")
    for name in banned_names:
        assert (_DEF + name) not in src, (
            f"로컬 추출기 재구현 검출: `{_DEF}{name}` — W-13 단일 추출기 계약 위반"
        )

    # (3) fixture 로딩이 W-13 경로를 타는가 (실호출 산출로 확인)
    shape = shape_of("mctrader")
    assert isinstance(shape, WorkflowShape), f"shape 형이 WorkflowShape 가 아님: {type(shape)}"


# ════════════════════════════════════════════════════════════════════════════
# E1~E8 — repo 별 차등 필드 (로컬 개조 자체).  정의역 = 구조
# ════════════════════════════════════════════════════════════════════════════
def test_e1_mctrader_top_concurrency_exists():
    """E1 (AC-10): mctrader top-level `concurrency` 존재 (경로 ∧ 매핑 둘 다)."""
    shape = shape_of("mctrader")

    assert shape.top_concurrency is not None, "E1: top_concurrency 가 None"
    assert "concurrency" in shape.concurrency_paths, (
        f"E1: 'concurrency' 경로 부재 — concurrency_paths={shape.concurrency_paths}"
    )


def test_e2_mctrader_group_equals_pin():
    """E2 (AC-10): mctrader `group` == 핀 리터럴 (문자열 동일성, 부분일치 아님)."""
    shape = shape_of("mctrader")

    assert shape.top_concurrency is not None, "E2 전제: top_concurrency 부재"
    group_value = shape.top_concurrency.get("group")
    assert group_value == PIN_MCTRADER_GROUP, (
        "E2: group 불일치\n"
        f"  기대: {PIN_MCTRADER_GROUP}\n"
        f"  실측: {group_value}"
    )


def test_e3_mctrader_template_group_absent():
    """E3 (AC-10): mctrader group 이 wrapper 정본 표현식으로 되돌아가지 않았다.

    §8.D rule 2 — 순수 부재-assert 단독 금지. 양성 앵커(E2 동일성)와 **AND** 로만
    성립시킨다.
    """
    shape = shape_of("mctrader")

    assert shape.top_concurrency is not None, "E3 전제: top_concurrency 부재"
    group_value = shape.top_concurrency.get("group")

    # 양성 앵커 (존재 + 값 확정)
    assert group_value == PIN_MCTRADER_GROUP, (
        f"E3 양성 앵커 실패: group={group_value!r} != 핀 리터럴"
    )
    # 부재 (정본 표현식 아님)
    assert group_value != TEMPLATE_GROUP, (
        f"E3: group 이 wrapper 정본 표현식으로 복귀함 — {group_value}"
    )


def test_e4_mctrader_no_job_concurrency():
    """E4 (AC-10): mctrader `jobs.*.concurrency == ∅` (양성 앵커 = top-level 실재)."""
    shape = shape_of("mctrader")

    _anchor_jobs(shape, "mctrader")
    assert "concurrency" in shape.concurrency_paths, (
        f"E4 양성 앵커 실패: top-level concurrency 부재 — {shape.concurrency_paths}"
    )
    job_paths = shape.job_concurrency_paths()
    assert job_paths == [], f"E4: job 하위 concurrency 경로 검출 — {job_paths}"


def test_e5_mctrader_timeout_paths_pinned():
    """E5 (AC-10): mctrader `timeout-minutes` 경로→값 매핑 전문 동일성.

    §8.D rule 1 — 카디널리티를 1차 입력으로 쓰지 않는다. `len(...) == 2` 대신
    **경로 집합 자체**를 핀과 대조하므로, 카디널리티를 유지한 채 job-level →
    step-level 로 옮기는 relocation(R-6)이 정의상 관측된다. 실패 보고는 위반
    경로를 열거한다.
    """
    shape = shape_of("mctrader")

    _anchor_jobs(shape, "mctrader")
    actual = dict(shape.timeout_paths)
    if actual != PIN_MCTRADER_TIMEOUT_PATHS:
        missing = sorted(set(PIN_MCTRADER_TIMEOUT_PATHS) - set(actual))
        extra = sorted(set(actual) - set(PIN_MCTRADER_TIMEOUT_PATHS))
        changed = sorted(
            f"{p}: {PIN_MCTRADER_TIMEOUT_PATHS[p]!r} -> {actual[p]!r}"
            for p in set(actual) & set(PIN_MCTRADER_TIMEOUT_PATHS)
            if actual[p] != PIN_MCTRADER_TIMEOUT_PATHS[p]
        )
        pytest.fail(
            "E5: timeout 경로 집합 불일치 (위반 경로 열거)\n"
            f"  소실: {missing}\n"
            f"  신규: {extra}\n"
            f"  값변경: {changed}"
        )


@pytest.mark.parametrize("repo", ["mctrader-backtest", "mctrader-engine", "mctrader-market"])
def test_e6_backtest_no_top_concurrency(repo):
    """E6 (AC-10): backtest/engine/market top-level `concurrency == ∅`."""
    shape = shape_of(repo)

    _anchor_jobs(shape, repo)  # §8.D rule 2 양성 앵커
    assert shape.top_concurrency is None, (
        f"E6 [{repo}]: top_concurrency 가 존재 — {shape.top_concurrency}"
    )
    assert "concurrency" not in shape.concurrency_paths, (
        f"E6 [{repo}]: top-level concurrency 경로 검출 — {shape.concurrency_paths}"
    )


@pytest.mark.parametrize("repo", ["mctrader-backtest", "mctrader-engine", "mctrader-market"])
def test_e7_backtest_no_job_concurrency(repo):
    """E7 (AC-10): backtest/engine/market `jobs.*.concurrency == ∅`."""
    shape = shape_of(repo)

    _anchor_jobs(shape, repo)  # §8.D rule 2 양성 앵커
    job_paths = shape.job_concurrency_paths()
    assert job_paths == [], f"E7 [{repo}]: job 하위 concurrency 경로 검출 — {job_paths}"


def test_e8_market_job2_runs_on_custom():
    """E8 (AC-10): market job2 `runs-on` 로컬 개조 보존.

    ★ 판정은 파생 접근자 `runs_on_local_delta(shape, CANON)` **위에서만** 한다
      (W-13 docstring 명시). 원시 `shape.runs_on` 위의 assert 는 정본 상속값을
      포함하므로 항진 = 판별력 0 이며, 그 형태는 T-taut 대조군 전용이다.
    """
    shape = shape_of("mctrader-market")

    _anchor_jobs(shape, "mctrader-market")
    delta = runs_on_local_delta(shape, CANON_RUNS_ON)
    assert JOB2 in delta, (
        f"E8: market job2 의 로컬 개조가 소실됨 (정본으로 복귀) — delta={delta}, "
        f"runs_on={shape.runs_on}"
    )
    assert delta[JOB2] == CANON_RUNS_ON_JOB1, (
        f"E8: market job2 runs-on 값이 기대 개조값과 다름 — {delta[JOB2]!r}"
    )


# ════════════════════════════════════════════════════════════════════════════
# F1~F10 — 4 repo 불변 필드 (backfill 보존 불변식).  정의역 = 구조
#          구 판에서 계산만 되고 조회 0 이던 **사문 필드 10종**이 여기 대응한다.
# ════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f1_job_ids_pinned(repo):
    """F1 — `job_ids` (선언 순 job id) 4 repo 불변."""
    shape = shape_of(repo)
    assert shape.job_ids == PIN_JOB_IDS, (
        f"F1 [{repo}]: job_ids 불일치 — 실측={shape.job_ids}, 기대={PIN_JOB_IDS}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f2a_coe_paths_pinned(repo):
    """F2a — `coe_paths` 경로 집합 전문 불변 (§8.B leg ③ 표면).

    카디널리티가 아니라 경로 집합 자체를 핀과 대조하므로, 총 개수를 유지한 채
    job1.step → job2 로 옮기는 relocation(R-7)도 관측된다.
    """
    shape = shape_of(repo)

    _anchor_jobs(shape, repo)
    assert shape.coe_paths == PIN_COE_PATHS, (
        f"F2a [{repo}]: coe_paths 불일치 (위반 경로 열거)\n"
        f"  실측: {shape.coe_paths}\n"
        f"  기대: {PIN_COE_PATHS}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f2b_coe_ownership_partition_pinned(repo):
    """F2b — `continue-on-error` 의 **job 소속 분할** 불변.

    ★ F2a 와 **분리된 leg** 이다. 한 함수 안에 두면 경로 집합 assert 가 먼저
      터져 소속 assert 가 영영 실행되지 않는다 — 소속 축이 assert 는 있으나
      RED 방향으로 한 번도 구동되지 않는 **장식 assert** 가 된다
      (firsthand: 분리 전 M-own1 / M-own2 / R-7 셋 다 경로 집합 assert 에서 종결).

    소속 판정은 W-13 `coe_paths_of()` (= `_owned_by`) 로만 한다 — 비협상 계약 (1).
    """
    shape = shape_of(repo)

    _anchor_jobs(shape, repo)
    owned = {jid: shape.coe_paths_of(jid) for jid in PIN_JOB_IDS}  # P-5 강제
    assert owned == PIN_COE_OWNED, (
        f"F2b [{repo}]: continue-on-error 소속 분할 변동\n"
        f"  실측: {owned}\n"
        f"  기대: {PIN_COE_OWNED}"
    )


# job id 진부분 문자열 충돌을 재현하는 최소 합성 workflow.
# `parallel-work-sentinel` ⊂ `parallel-work-sentinel-test` 이고, coe 는 **job2 에만** 있다.
_OWNERSHIP_PROBE_DOC = (
    "name: ownership-probe\n"
    "jobs:\n"
    f"  {JOB1}:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - run: echo job1\n"
    f"  {JOB2}:\n"
    "    runs-on: ubuntu-latest\n"
    "    continue-on-error: true\n"
    "    steps:\n"
    "      - run: echo job2\n"
)


def test_f2c_ownership_is_not_bare_startswith():
    """F2c — 비협상 계약 (1): 소속 판정이 bare `startswith` 가 **아님**을 실증.

    두 판정 형태가 실제로 갈리는 입력(job id 진부분 문자열 충돌)을 만들어, 결격
    형태였다면 무엇이 되는지를 같은 산출 위에서 대조한다. 이 대조가 없으면
    `coe_paths_of()` 를 호출한다는 사실만으로 계약 준수를 **주장만** 하게 된다.
    """
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / "ownership-probe.yml"
        probe.write_text(_OWNERSHIP_PROBE_DOC, encoding="utf-8", newline="")
        shape = load_workflow_shape(str(probe))

    job2_coe = f"jobs.{JOB2}.continue-on-error"
    assert shape.coe_paths == [job2_coe], (
        f"F2c 전제 붕괴: 합성 probe 의 coe_paths={shape.coe_paths}, 기대=[{job2_coe!r}]"
    )

    owned_job1 = shape.coe_paths_of(JOB1)
    bare_job1 = [p for p in shape.coe_paths if p.startswith(f"jobs.{JOB1}")]

    # 정본 판정: job1 은 coe 를 보유하지 않는다
    assert owned_job1 == [], f"F2c: `_owned_by` 판정이 오분류 — job1 소속={owned_job1}"
    # 결격 판정: bare startswith 는 job2 경로를 job1 소속으로 끌어온다
    assert bare_job1 == [job2_coe], (
        f"F2c 대조 전제 붕괴: bare startswith 가 job2 경로를 안 잡음 — {bare_job1}"
    )
    # 두 형태가 실제로 갈린다 = 계약 (1) 이 load-bearing
    assert owned_job1 != bare_job1, (
        "F2c: 두 판정 형태가 같은 결과를 냈다 — 이 입력은 계약 (1) 을 실증하지 못한다"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f3_job_if_pinned(repo):
    """F3 — `job_if` (job-level `if` 원문) 4 repo 불변."""
    shape = shape_of(repo)
    assert dict(shape.job_if) == PIN_JOB_IF, (
        f"F3 [{repo}]: job_if 불일치 — 실측={dict(shape.job_if)}, 기대={PIN_JOB_IF}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f4_step_if_pinned(repo):
    """F4 — `step_if` (step 순서별 `if` 원문) 4 repo 불변.

    step 순서 자체가 계약이다 — step 삽입·삭제로 인덱스가 밀리면 리스트가 달라져
    관측된다.
    """
    shape = shape_of(repo)
    assert {k: list(v) for k, v in shape.step_if.items()} == PIN_STEP_IF, (
        f"F4 [{repo}]: step_if 불일치\n"
        f"  실측: {dict(shape.step_if)}\n"
        f"  기대: {PIN_STEP_IF}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f5_env_keys_pinned(repo):
    """F5 — `env_keys` (workflow / job / step 3 레벨 전건) 4 repo 불변.

    §8.F 주입 채널 — YAML `env:` 로의 키 주입이 3 레벨 어디에 들어와도 관측된다.
    """
    shape = shape_of(repo)
    actual = {k: list(v) for k, v in shape.env_keys.items()}
    if actual != PIN_ENV_KEYS:
        missing = sorted(set(PIN_ENV_KEYS) - set(actual))
        extra = sorted(set(actual) - set(PIN_ENV_KEYS))
        changed = sorted(
            f"{p}: {PIN_ENV_KEYS[p]} -> {actual[p]}"
            for p in set(actual) & set(PIN_ENV_KEYS)
            if actual[p] != PIN_ENV_KEYS[p]
        )
        pytest.fail(
            f"F5 [{repo}]: env_keys 불일치 (위반 경로 열거)\n"
            f"  소실 경로: {missing}\n"
            f"  신규 경로: {extra}\n"
            f"  키 변동: {changed}"
        )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f6_container_env_keys_absent(repo):
    """F6 — `container_env_keys == ∅` (§8.F 주입 채널 #6, 양성 앵커 AND).

    `container.env` 는 job 실행 컨테이너에 환경변수를 심는 별개 주입 표면이다.
    """
    shape = shape_of(repo)

    _anchor_jobs(shape, repo)  # §8.D rule 2
    assert dict(shape.container_env_keys) == PIN_CONTAINER_ENV_KEYS, (
        f"F6 [{repo}]: container.env 키 주입 검출 — {dict(shape.container_env_keys)}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f7_env_file_keys_absent(repo):
    """F7 — `env_file_keys == ∅` (§8.F 주입 채널 #5, 양성 앵커 AND).

    ★ **정의역 = 인라인 `$GITHUB_ENV` 기입 표기 한정 · 전수 아님** (§8.F C-3,
      W-13 `_scan_env_file_keys` docstring 이 포섭/미포섭 축의 SSOT).
      여러 줄 블록 리다이렉트 · heredoc · `exec` 재지정 · 변수 간접화 · 타 언어
      writer · 간접 스크립트 호출은 **declared 미포섭 잔여**다. 본 leg 의 GREEN 을
      "환경변수 주입 없음" 으로 인용하면 over-claim 이다.
    """
    shape = shape_of(repo)

    _anchor_run_step(shape, repo)  # §8.D rule 2 — 스캔 대상 step 실재
    assert dict(shape.env_file_keys) == PIN_ENV_FILE_KEYS, (
        f"F7 [{repo}]: $GITHUB_ENV 인라인 기입 검출 — {dict(shape.env_file_keys)}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f8_step_shell_pinned(repo):
    """F8 — `step_shell` (step 순서별 `shell:` 원문) 4 repo 불변 (전건 미지정).

    §8.B rc 흡수 표면 — step 단위 `shell: bash {0}` 지정은 셸의 `-e` 를 떨궈
    run 블록 중간 실패를 흡수한다(GitHub Actions 기본은 `bash -e`). 그 1줄 주입이
    여기서 관측된다.
    """
    shape = shape_of(repo)

    _anchor_steps(shape, repo)  # §8.D rule 2
    actual = {k: list(v) for k, v in shape.step_shell.items()}
    assert actual == PIN_STEP_SHELL, (
        f"F8 [{repo}]: step `shell:` 지정 변동 — 실측={actual}, 기대={PIN_STEP_SHELL}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f9_defaults_run_shell_absent(repo):
    """F9 — workflow-level `defaults.run.shell` 부재 (§8.B 원거리 1줄 우회 표면).

    workflow 최상단 `defaults: run: shell: bash {0}` 한 줄은 **전 job·전 step** 의
    셸을 한꺼번에 바꾼다. 주입 지점이 검사 대상 job 에서 멀어 눈에 띄지 않는다.
    """
    shape = shape_of(repo)

    _anchor_jobs(shape, repo)  # §8.D rule 2
    assert shape.defaults_run_shell == PIN_DEFAULTS_RUN_SHELL, (
        f"F9 [{repo}]: workflow-level defaults.run.shell 주입 검출 — "
        f"{shape.defaults_run_shell!r}"
    )


@pytest.mark.parametrize("repo", ALL_REPOS)
def test_f10_job_defaults_run_shell_absent(repo):
    """F10 — job-level `jobs.<id>.defaults.run.shell` 부재 (§8.B 우회 표면)."""
    shape = shape_of(repo)

    _anchor_jobs(shape, repo)  # §8.D rule 2
    assert dict(shape.job_defaults_run_shell) == PIN_JOB_DEFAULTS_RUN_SHELL, (
        f"F10 [{repo}]: job-level defaults.run.shell 주입 검출 — "
        f"{dict(shape.job_defaults_run_shell)}"
    )


# ════════════════════════════════════════════════════════════════════════════
# F11 — 비협상 계약 (2): DupSafeLoader (중복 키 silent last-wins 차단)
# ════════════════════════════════════════════════════════════════════════════
_DUP_DOC = (
    "name: dup-probe\n"
    "concurrency:\n"
    "  group: A\n"
    "concurrency:\n"
    "  group: B\n"
    "jobs:\n"
    "  only-job:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - run: echo hi\n"
)


def test_f11_duplicate_key_fail_closed():
    """F11 — 같은 레벨 중복 키는 `ShapeError(workflow_parse_error)` 로 fail-closed.

    대조 실증(같은 입력, 두 파서): bare `yaml.safe_load` 는 **에러 0 으로 마지막
    값만 남긴다**. 그 파서 위에 세운 "top-level concurrency 개수 == 1" 류 leg 은
    중복 주입에 구조적으로 눈이 먼다. 본 leg 은 W-13 이 그 경로를 차단함을
    firsthand 로 확정한다 (W-13 비협상 계약 (2)).
    """
    yaml = pytest.importorskip("yaml", reason="PyYAML 부재 — W-13 P-6 정의역 밖")

    # 대조군: bare safe_load = silent last-wins (에러 0)
    silent = yaml.safe_load(_DUP_DOC)
    assert silent["concurrency"] == {"group": "B"}, (
        f"대조 전제 붕괴: bare safe_load 가 last-wins 를 내지 않음 — {silent['concurrency']}"
    )

    # 본군: W-13 = fail-closed
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / "dup.yml"
        probe.write_text(_DUP_DOC, encoding="utf-8", newline="")
        with pytest.raises(ShapeError) as exc:
            load_workflow_shape(str(probe))
    assert exc.value.error_kind == "workflow_parse_error", (
        f"F11: error_kind 불일치 — {exc.value.error_kind!r}, 기대 'workflow_parse_error'"
    )


# ════════════════════════════════════════════════════════════════════════════
# W-16 — wrapper 정의역 확장 (§8.B leg③ 표면 보호).  정의역 = 구조 + 텍스트
#        wrapper 자신의 workflow 2 면(canonical + twin template) 을 정의역에 편입
# ════════════════════════════════════════════════════════════════════════════
#
# ★ (6-a) 과잉 RED 오독 차단 + 곱 실측표
# ───────────────────────────────────────────────────────────────────────────
# A8 6종 중 단독으로 흡수하는 것은 5종이고, `; true` 만 `bash {0}` (A3·A4·A5)
# **곱**에서만 흡수한다 (단독은 휴면). 따라서 본 leg 이 `; true` 에 RED 를 내는
# 것은 fail-closed 방향의 **과잉 RED**이며, "정적 RED = 실 흡수"로 읽으면 오독이다.
#
# | 관용구 | `bash -e` (정본 기본) | `bash {0}` (A3/A4/A5 주입) |
# |---|---|---|
# | `false` | 1 | 1 |
# | `false \|\| true` | 0 | 0 |
# | `false \|\| :` | 0 | 0 |
# | `false \|\| exit 0` | 0 | 0 |
# | **`false ; true`** | **1** | **0** |  ← 곱에서만 흡수
# | `set +e` / `exit 0` | 0 | 0 |
# | `if false; then :; fi` | 0 | 0 |
#
# ★ (6-b) Change Plan 문면 오류 + W-3b-1 활성 표면
# ───────────────────────────────────────────────────────────────────────────
# CP §5.1 W-16 행 괄호는 "W-3b·W-3b-1 = 단일 명령 step" 이라 쓰지만, **W-3b-1
# 은 거짓**이다 — 실측 **8 줄** (비어있지 않은 줄 수). 단일 명령인 것은 **W-3b 뿐**
# 이고, A3·A4·A5 의 휴면은 rc 를 나르는 **W-3b 가 단일 명령**이라는 사실에 근거.
#
# 더 중요한 사실: **W-3b-1 은 휴면이 아니라 활성 흡수 표면**이다. W-3b-1 에 `shell:`
# 이 주입되면 수집 실패가 조용히 삼켜진다. 이것이 `test_w16_c` 가 job2 6 step 전건
# 의 `step_shell` 을 `[None]*6` 으로 못박는 실질 근거다 — W-3b 만 지키면 충분하다는
# 읽기는 틀렸다.
@pytest.mark.parametrize("face", WRAPPER_FACES)
def test_w16_a_wrapper_face_anchor(face):
    """W-16.a — wrapper workflow 양성 앵커 (파일 실재, job 수, step 수, dup_safe_load).

    W-13 결속 자기 점검과 동형. wrapper 2 면 모두 W-13 으로 로드되고, 기본 형상을
    반복적으로 확인한다.
    """
    shape = wrapper_shape_of(face)

    # 파일 실재
    wf_path = _W13_ROOT / WRAPPER_WORKFLOWS[face]
    assert wf_path.is_file(), f"W-16.a [{face}]: workflow 파일 부재 — {wf_path}"

    # W-13 로드 확인
    assert isinstance(shape, WorkflowShape), (
        f"W-16.a [{face}]: shape 형이 WorkflowShape 아님 — {type(shape)}"
    )
    assert load_workflow_shape.__module__ == "workflow_shape", (
        f"W-16.a [{face}]: 모듈이 workflow_shape 아님 — {load_workflow_shape.__module__}"
    )

    # 기본 형상
    assert shape.job_ids == PIN_JOB_IDS, (
        f"W-16.a [{face}]: job_ids 불일치 — {shape.job_ids}"
    )
    assert len(shape.step_if[JOB1]) == 3, (
        f"W-16.a [{face}]: job1 step 수 불일치 — {len(shape.step_if[JOB1])}"
    )
    assert len(shape.step_if[JOB2]) == 6, (
        f"W-16.a [{face}]: job2 step 수 불일치 — {len(shape.step_if[JOB2])}"
    )

    # dup_safe_load 모듈 동일성
    assert dup_safe_load.__module__ == "workflow_shape", (
        f"W-16.a [{face}]: dup_safe_load 모듈이 workflow_shape 아님 — {dup_safe_load.__module__}"
    )


@pytest.mark.parametrize("face", WRAPPER_FACES)
def test_w16_b_job2_coe_paths_empty_strict(face):
    """W-16.b — wrapper job2 `coe_paths_of` 공정 (§8.B leg③ 표면).

    §8.D rule 2 — 부재-assert 양성 앵커와 AND. job2 는 continue-on-error 를 보유하지
    않는다는 것을 직접 확인하고, job1 은 기대 핀과 일치함을 동시 보증한다.
    """
    shape = wrapper_shape_of(face)

    _anchor_wrapper_steps(shape, face)

    # job2 는 coe 부재 (엄격한 판정)
    job2_coe = shape.coe_paths_of(JOB2)
    assert job2_coe == [], (
        f"W-16.b [{face}]: job2 continue-on-error 검출 — {job2_coe}"
    )

    # job1 은 기대 핀 일치 (양성 앵커)
    job1_coe = shape.coe_paths_of(JOB1)
    assert job1_coe == PIN_COE_PATHS, (
        f"W-16.b [{face}]: job1 coe_paths_of 불일치 — {job1_coe}"
    )


@pytest.mark.parametrize("face", WRAPPER_FACES)
def test_w16_c_job2_step_shell_all_none(face):
    """W-16.c — wrapper job2 `step_shell` 전문 [None]*6 (A3 봉인).

    job1 도 동시 검증해 형제 독립성을 보장한다.
    """
    shape = wrapper_shape_of(face)

    _anchor_wrapper_steps(shape, face)

    actual = {k: list(v) for k, v in shape.step_shell.items()}
    assert actual == PIN_WRAPPER_STEP_SHELL, (
        f"W-16.c [{face}]: step_shell 불일치\n"
        f"  실측: {actual}\n"
        f"  기대: {PIN_WRAPPER_STEP_SHELL}"
    )


@pytest.mark.parametrize("face", WRAPPER_FACES)
def test_w16_d_defaults_run_shell_absent(face):
    """W-16.d — wrapper `defaults.run.shell` 및 job defaults 부재 (A4·A5 봉인).

    양성 앵커 (job 확정)와 AND.
    """
    shape = wrapper_shape_of(face)

    _anchor_wrapper_steps(shape, face)

    assert shape.defaults_run_shell is None, (
        f"W-16.d [{face}]: defaults_run_shell 존재 — {shape.defaults_run_shell!r}"
    )
    assert dict(shape.job_defaults_run_shell) == PIN_JOB_DEFAULTS_RUN_SHELL, (
        f"W-16.d [{face}]: job_defaults_run_shell 불일치 — {dict(shape.job_defaults_run_shell)}"
    )


@pytest.mark.parametrize("face", WRAPPER_FACES)
def test_w16_e_pytest_step_run_free_of_a8_idioms(face):
    """W-16.e — wrapper job2 W-3b step `run` 문면에 A8 idioms 6종 부재 (텍스트 정의역).

    A8 = bash rc 흡수 관용구: `|| true` · `|| :` · `|| exit 0` · `; true` ·
    `set +e` · `if …; then` 등 6종. W-13 파서는 composite action / 여러 줄
    리다이렉트를 미포섭하므로 **텍스트 스캔으로 보완 정의역**.

    정의역: W-3b step ("Run pytest tests (W-3b)") 의 `run` 문면.

    ★ (3) 명 기반 조회: step 인덱스 고정(`steps[4]`) 금지. step 이 하나 삽입되면
      엉뚱한 step 을 스캔하고도 GREEN 이 된다. 반드시 step 명으로 찾아야 한다.
    """
    wf_path = _W13_ROOT / WRAPPER_WORKFLOWS[face]
    with open(wf_path, "r", encoding="utf-8") as f:
        data = dup_safe_load(f.read())  # ★ (4) dup_safe_load(f) → dup_safe_load(f.read())

    jobs = data.get("jobs", {})
    job2 = jobs.get(JOB2, {})
    steps = job2.get("steps", [])

    # W-3b step 을 명으로 찾기
    w3b_step_name = "Run pytest tests (W-3b)"
    w3b_step = None
    for s in steps:
        if s.get("name") == w3b_step_name:
            w3b_step = s
            break
    assert w3b_step is not None, (
        f"W-16.e [{face}]: W-3b step 명 미검출 — {w3b_step_name}"
    )
    # 찾은 step 의 name 을 다시 assert 해 자기 앵커를 세우기
    assert w3b_step.get("name") == w3b_step_name, (
        f"W-16.e [{face}]: W-3b step name 재확인 실패 — {w3b_step.get('name')}"
    )
    run_text = w3b_step.get("run", "")

    assert run_text, f"W-16.e [{face}]: W-3b step run 부재 — {w3b_step}"

    # ── 술어 자기판별 통제 (CR-1) ────────────────────────────────────────────
    # probe 표 자체의 양성 앵커: 6종 전건이 양·음 probe 를 보유해야 한다.
    # (이 앵커 없이는 idiom 을 추가하고 probe 를 빠뜨려도 조용히 GREEN 이 된다.)
    _displays = {d for _, d in _A8_IDIOMS}
    assert set(_A8_PROBE_POSITIVES) == _displays, (
        f"W-16.e probe 표 결손(양성) — 미등재={_displays - set(_A8_PROBE_POSITIVES)}, "
        f"잉여={set(_A8_PROBE_POSITIVES) - _displays}"
    )
    assert set(_A8_PROBE_NEGATIVES) == _displays, (
        f"W-16.e probe 표 결손(음성) — 미등재={_displays - set(_A8_PROBE_NEGATIVES)}, "
        f"잉여={set(_A8_PROBE_NEGATIVES) - _displays}"
    )

    for idiom_pattern, idiom_display in _A8_IDIOMS:
        positives = _A8_PROBE_POSITIVES[idiom_display]
        negatives = _A8_PROBE_NEGATIVES[idiom_display]
        assert positives and negatives, (
            f"W-16.e 술어 고장: `{idiom_display}` probe 가 비었다 (공허 통제)"
        )
        for probe in positives:
            assert re.search(idiom_pattern, probe), (
                f"W-16.e 술어 고장(양성 probe): regex `{idiom_pattern}` 이 "
                f"{probe!r} 를 못 잡음 — 셸은 이 표기를 `{idiom_display}` 과 동일 해석한다"
            )
        for probe in negatives:
            assert not re.search(idiom_pattern, probe), (
                f"W-16.e 술어 고장(음성 probe): regex `{idiom_pattern}` 이 "
                f"{probe!r} 를 잘못 잡음 — 항진 needle"
            )

    # ── 실제 스캔 — A8 idiom 부재 (양성 앵커 = 위 step 명 재확인 + run 비공백) ──
    for idiom_pattern, idiom_display in _A8_IDIOMS:
        assert not re.search(idiom_pattern, run_text), (
            f"W-16.e [{face}]: A8 idiom `{idiom_display}` (regex `{idiom_pattern}`) 검출 — "
            f"W-3b step run 문면에 부재해야 함. run={run_text!r}\n{_A8_DOMAIN}"
        )


@pytest.mark.parametrize("face", WRAPPER_FACES)
def test_w16_f_job2_step_names_pinned(face):
    """W-16.f — wrapper job2 3 step 명 pin (텍스트 정의역).

    W-3b-1·W-3b 등 공식 명이 step 이름으로 반영되도록 정의역 핀.
    """
    wf_path = _W13_ROOT / WRAPPER_WORKFLOWS[face]
    with open(wf_path, "r", encoding="utf-8") as f:
        data = dup_safe_load(f.read())  # ★ (4) dup_safe_load(f) → dup_safe_load(f.read())

    jobs = data.get("jobs", {})
    job2 = jobs.get(JOB2, {})
    steps = job2.get("steps", [])

    for idx, expected_name in PIN_WRAPPER_JOB2_STEP_NAMES.items():
        assert len(steps) > idx, f"W-16.f [{face}]: step 인덱스 {idx} 부족"
        actual_name = steps[idx].get("name", "<unnamed>")
        assert actual_name == expected_name, (
            f"W-16.f [{face}] step[{idx}]: 명 불일치\n"
            f"  기대: {expected_name!r}\n"
            f"  실측: {actual_name!r}"
        )


# ════════════════════════════════════════════════════════════════════════════
# 오라클 판별력 실증 — in-test mutant (§8.A mutant roster)
# ════════════════════════════════════════════════════════════════════════════
# 원본 fixture 는 읽기 전용. 변이는 tempdir 사본에만 가하고, 앵커 미적중은
# **하네스 결함**이므로 fail-closed 로 죽인다 (no-op 변이의 가짜 GREEN 차단).
A_TOP_CONCURRENCY_BLOCK = (
    "concurrency:\n"
    "  group: ${{ github.workflow }}-${{ github.event_name == 'pull_request' "
    "&& github.event.pull_request.number || github.run_id }}\n"
    "  cancel-in-progress: true\n"
)


def _mutate_to_tempfile(repo: str, anchor: str, repl: str, label: str, td: str) -> Path:
    src = (FIXTURE_DIR / CONSUMER_FIXTURES[repo]).read_text(encoding="utf-8")
    assert anchor in src, (
        f"{label}: 앵커 미적중 — 변이 무효. fixture 문면이 바뀌었다면 앵커를 갱신하라."
    )
    mutated = src.replace(anchor, repl, 1)
    assert mutated != src, f"{label}: 치환 후 문면 불변 — 변이 무효 (no-op)"
    out = Path(td) / CONSUMER_FIXTURES[repo]
    out.write_text(mutated, encoding="utf-8", newline="")
    return out


def test_oracle_mutation_r1_remove_mctrader_top_concurrency():
    """R-1 (§8.A): mctrader top-level `concurrency` 블록 제거 → E1 축 RED.

    형제 독립성도 함께 실증한다 — E5(timeout) 축은 이 변이에 **영향받지 않아야**
    한다. 한 변이가 무관한 leg 까지 무너뜨리면 원인 귀속이 불가능해진다.

    ★ 형제 비교의 기준은 핀 상수가 아니라 **같은 파일의 변이 전 산출**이다
      (self-referential). 핀을 기준으로 삼으면 바깥에서 이미 fixture 를 건드린
      상황에서 "R-1 이 E5 를 깼다" 는 **틀린 귀속**이 보고된다.
    """
    base = shape_of("mctrader")
    with tempfile.TemporaryDirectory() as td:
        mutant = _mutate_to_tempfile("mctrader", A_TOP_CONCURRENCY_BLOCK, "", "R-1", td)
        shape = load_workflow_shape(str(mutant))

    # E1 축이 실제로 무너지는가 (판별력)
    assert shape.top_concurrency is None, (
        f"R-1: E1 축이 여전히 GREEN — top_concurrency={shape.top_concurrency}"
    )
    assert "concurrency" not in shape.concurrency_paths, (
        f"R-1: concurrency 경로가 남아있음 — {shape.concurrency_paths}"
    )
    # 형제 축 독립 — 변이 전(base) 대비 불변이어야 (기준 = 같은 파일 자신)
    assert dict(shape.timeout_paths) == dict(base.timeout_paths), (
        f"R-1: 무관한 E5 축이 동반 변동 — 변이전={dict(base.timeout_paths)}, "
        f"변이후={dict(shape.timeout_paths)}"
    )


def test_oracle_taut_template_vs_mctrader_runs_on():
    """T-taut (§8.A): 항진 대조군 — 밀짚 오라클 vs 실 오라클.

    밀짚 = 원시 `runs_on` 위의 "두 job 에 runs-on 이 존재하는가". 정본 상속값을
    포함하므로 로컬 개조가 전멸해도 GREEN 이다 (판별력 ~0).
    실 오라클 = 파생값(`runs_on_local_delta`) + 값 동일성(E2).

    본 leg 은 **두 오라클이 같은 입력쌍에서 실제로 갈리는지**를 확정한다. 갈리지
    않으면 T-taut 는 대조군 역할을 못 한다.

    ★ 판정은 핀 상수가 아니라 **mctrader as-found ↔ backtest 덮어쓰기 두 산출의
      대조**로만 한다 (self-referential). 핀을 기준으로 삼으면 이 leg 이 E2·E5 를
      중복 판정해 무관한 변이에서까지 동반 RED 를 내고 원인 귀속을 흐린다.
      "mctrader 가 핀과 같은가" 는 E2·E5 의 몫이다.
    """
    base = shape_of("mctrader")

    # T-taut mutant — backtest 정본 형상으로 통째 덮어쓰기 (로컬 개조 전멸)
    with tempfile.TemporaryDirectory() as td:
        overwritten = Path(td) / CONSUMER_FIXTURES["mctrader"]
        overwritten.write_text(
            (FIXTURE_DIR / CONSUMER_FIXTURES["mctrader-backtest"]).read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="",
        )
        mutant = load_workflow_shape(str(overwritten))

    # (1) 밀짚 오라클은 **양쪽 다** GREEN = 판별력 0 (이것이 대조군의 요점)
    straw_base = all(jid in base.runs_on for jid in PIN_JOB_IDS)
    straw_mutant = all(jid in mutant.runs_on for jid in PIN_JOB_IDS)
    assert straw_base and straw_mutant, (
        "T-taut 대조 전제 붕괴: 밀짚 오라클이 한쪽에서 RED — "
        f"base={straw_base}, mutant={straw_mutant}"
    )

    # (2) 실 오라클(구조 술어)은 두 입력을 **구별한다**
    real_divergent = (
        base.top_concurrency != mutant.top_concurrency
        or dict(base.timeout_paths) != dict(mutant.timeout_paths)
    )
    assert real_divergent, (
        "T-taut: 실 오라클이 두 입력을 구별하지 못했다 — 밀짚과 판별력이 같아졌고, "
        "mctrader 의 로컬 개조가 정본 형상과 구분되지 않는다는 뜻이다 "
        f"(top_concurrency={mutant.top_concurrency}, timeout_paths={dict(mutant.timeout_paths)})"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
