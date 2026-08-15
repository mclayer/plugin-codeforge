#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mutant_harness.py — CFP-2978 Phase 2 잔여 mutant 실행 관측 하네스.

목적
----
Change Plan §8.A mutant roster 를 **실행**해 두 오라클면의 verdict 를 나란히 낸다.

  (a) 테스트면 오라클  = tests/scripts/test_cfp2978_workflow_shape.py (W-14) 의 pytest leg
  (b) 실 모듈 오라클   = scripts/lib/workflow_shape.py (W-13) 의 `load_workflow_shape` 파생 leg

두 면을 분리 측정하는 이유: **추출기가 같아도 leg 집합은 다를 수 있다**. 두 면이
갈리면 그것은 ① W-13 구현 결함이 아니라 ② W-14 의 **leg 부재**(계산은 되는데
assert 하지 않는 사문 필드)를 가리킨다 — 두 면을 같은 입력에 나란히 걸어야만
그 판별이 선다.

★ 이력(수리 완료): 초판 W-14 는 W-13 을 import 하지 않고 자체 추출기 +
  bare `yaml.safe_load` 를 재구현했고, 그 상태에서 mutant 11 종이 pytest 면에서
  조용히 통과했다. 현재 W-14 는 W-13 을 import 해 호출하며 사문 필드 10 종에
  assert leg(F1~F10)을 보유한다. 본 하네스는 그 수리의 **전/후 대조 측정기**이자
  회귀 감시기로 남는다.

규율
----
* 원본 fixture 는 **읽기 전용**. 변이는 scratch run tree 사본에만 가한다.
* 모든 변이는 **앵커 적중 검증**(`assert mutated != original`)을 통과해야 한다.
  앵커를 놓친 no-op 변이는 GREEN 을 내며, 그 GREEN 은 "미검출" 로 오독된다
  — 이 하네스가 겨냥하는 vacuous 함정 자신이므로 fail-closed 로 막는다.
* run tree 는 repo 밖(scratchpad)에 둔다. repo 안에 두면 `test_*.py` 사본이
  pytest 수집에 걸려 basename 충돌을 일으킨다.

CLI:
    python mutant_harness.py --list
    python mutant_harness.py --run M-envfile M-quot ...
    python mutant_harness.py --run-all
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ── 경로 ─────────────────────────────────────────────────────────────────────
LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cfp2978"
TEST_FILE = REPO_ROOT / "tests" / "scripts" / "test_cfp2978_workflow_shape.py"
CONFTEST = REPO_ROOT / "tests" / "scripts" / "conftest.py"
# W-14 는 W-13 을 import 해 호출한다 ⇒ run tree 도 repo 배치를 그대로 재현해야
# 테스트면이 실행된다. (미배치 시 W-14 는 skip 이 아니라 수집 ERROR 로 죽는다 —
# 그 RED 는 mutant 검출이 아니라 하네스 결함이므로 여기서 미리 막는다.)
W13_MODULE = REPO_ROOT / "scripts" / "lib" / "workflow_shape.py"
SCRATCH = Path(
    os.environ.get(
        "CFP2978_LAB_SCRATCH",
        r"C:\Users\mccho\AppData\Local\Temp\claude\c--workspace-mclayer-plugin-codeforge"
        r"\5d775507-319e-44aa-a978-46cc2af066fd\scratchpad\cfp2978-runs",
    )
)
LOG_DIR = LAB_DIR / "logs"

FIXTURES = [
    "mctrader-sentinel.yml",
    "mctrader-backtest.yml",
    "mctrader-market.yml",
    "mctrader-engine.yml",
]

sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

PIN_MCTRADER_GROUP = (
    "${{ github.workflow }}-"
    "${{ github.event_name == 'pull_request' && github.event.pull_request.number "
    "|| github.run_id }}"
)
TEMPLATE_GROUP = "${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}"
CANON_RUNS_ON = (
    "${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || '[\"ubuntu-latest\"]') }}"
)
JOB1 = "parallel-work-sentinel"
JOB2 = "parallel-work-sentinel-test"

# ── 변이 앵커 (fixture 문면 리터럴 — 적중 실패 시 하네스가 죽는다) ──────────
A_TOP_CONCURRENCY = (
    "concurrency:\n"
    "  group: ${{ github.workflow }}-${{ github.event_name == 'pull_request' "
    "&& github.event.pull_request.number || github.run_id }}\n"
    "  cancel-in-progress: true\n"
)
A_JOB1_HEADER = "  parallel-work-sentinel:\n"
A_JOB2_HEADER = "  parallel-work-sentinel-test:\n"
A_JOB1_TIMEOUT = (
    "    timeout-minutes: 10   # MTD-1325 D3 — tier: 경량 체크 (hung-잡 360분 슬롯 점유 차단)\n"
    "    steps:\n"
    "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1\n"
    "\n"
    "      - name: Bypass note (label present)\n"
)
A_JOB1_FIRST_STEP = (
    "    steps:\n"
    "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1\n"
    "\n"
    "      - name: Bypass note (label present)\n"
)
A_STEP_COE = (
    "        continue-on-error: ${{ env.SENTINEL_TIER != 'blocking' }}"
)
A_MARKET_JOB2_RUNS_ON = (
    "    runs-on: ${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || '[\"ubuntu-latest\"]') }}\n"
    "    steps:\n"
    "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1\n"
    "      - name: Set up Python\n"
)


def _replace_once(text: str, anchor: str, repl: str, label: str) -> str:
    """앵커 1회 치환 + 적중 검증. 미적중 = 하네스 사망 (no-op 변이의 가짜 GREEN 차단)."""
    if anchor not in text:
        raise SystemExit(f"[ANCHOR-MISS] {label}: 앵커 미적중 — 변이 무효, 관측 중단")
    out = text.replace(anchor, repl, 1)
    if out == text:
        raise SystemExit(f"[NO-OP] {label}: 치환 후 문면 불변 — 변이 무효")
    return out


# ── 변이 정의 ────────────────────────────────────────────────────────────────
# 각 항목: (target fixture, mutate_fn, 기대 verdict 설명)

def m_envfile(t: str) -> str:
    """$GITHUB_ENV 인라인 기입 step 을 job1 선두에 주입 (§8.F 채널 #5)."""
    return _replace_once(
        t,
        A_JOB1_FIRST_STEP,
        "    steps:\n"
        "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1\n"
        "\n"
        "      - name: Injected env-file write\n"
        "        run: |\n"
        '          echo "STORY_KEY_PREFIX=CFP" >> "$GITHUB_ENV"\n'
        "\n"
        "      - name: Bypass note (label present)\n",
        "M-envfile",
    )


def m_envfile_blk(t: str) -> str:
    """여러 줄 블록 리다이렉트 형 (§8.F 미포섭 declared 잔여 — GREEN 이 기대값)."""
    return _replace_once(
        t,
        A_JOB1_FIRST_STEP,
        "    steps:\n"
        "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1\n"
        "\n"
        "      - name: Injected env-file write (block redirect)\n"
        "        run: |\n"
        "          {\n"
        '            echo "STORY_KEY_PREFIX=CFP"\n'
        '          } >> "$GITHUB_ENV"\n'
        "\n"
        "      - name: Bypass note (label present)\n",
        "M-envfile-blk",
    )


def m_envkey(t: str) -> str:
    """YAML env: 3레벨 주입 — workflow / job1 / job1.step[1]."""
    t = _replace_once(
        t,
        "env:\n  SENTINEL_TIER: warning",
        "env:\n  INJECTED_WF_KEY: wf\n  SENTINEL_TIER: warning",
        "M-envkey/workflow",
    )
    t = _replace_once(
        t,
        A_JOB1_HEADER,
        A_JOB1_HEADER + "    env:\n      INJECTED_JOB_KEY: job\n",
        "M-envkey/job",
    )
    t = _replace_once(
        t,
        "      - name: Bypass note (label present)\n",
        "      - name: Bypass note (label present)\n"
        "        env:\n"
        "          INJECTED_STEP_KEY: step\n",
        "M-envkey/step",
    )
    return t


def m_envctr(t: str) -> str:
    """container.env 주입 (§8.F 채널 #6)."""
    return _replace_once(
        t,
        A_JOB1_HEADER,
        A_JOB1_HEADER
        + "    container:\n"
        + "      image: ubuntu:24.04\n"
        + "      env:\n"
        + "        INJECTED_CTR_KEY: ctr\n",
        "M-envctr",
    )


def m_quot(t: str) -> str:
    """top-level `"concurrency":` 따옴표 키 (backtest — grep straw 는 미적중)."""
    return _replace_once(
        t,
        "permissions:\n",
        '"concurrency":\n'
        "  group: injected-quoted-key\n"
        "  cancel-in-progress: true\n"
        "\n"
        "permissions:\n",
        "M-quot",
    )


def m_job4(t: str) -> str:
    """job property 4칸 들여쓰기 concurrency 주입 (backtest job1)."""
    return _replace_once(
        t,
        A_JOB1_HEADER,
        A_JOB1_HEADER
        + "    concurrency:\n"
        + "      group: injected-job-level-4space\n"
        + "      cancel-in-progress: true\n",
        "M-job4",
    )


def m_own1(t: str) -> str:
    """job1 job-level continue-on-error 주입 (소속 판정 축)."""
    return _replace_once(
        t,
        A_JOB1_HEADER,
        A_JOB1_HEADER + "    continue-on-error: true\n",
        "M-own1",
    )


def m_own2(t: str) -> str:
    """job2 job-level continue-on-error 주입 (소속 판정 축 — job1 과 다른 leg 이어야)."""
    return _replace_once(
        t,
        A_JOB2_HEADER,
        A_JOB2_HEADER + "    continue-on-error: true\n",
        "M-own2",
    )


def m_dup(t: str) -> str:
    """top-level 중복 `concurrency:` 키 주입 (silent last-wins 축)."""
    return _replace_once(
        t,
        A_TOP_CONCURRENCY,
        A_TOP_CONCURRENCY
        + "concurrency:\n"
        + "  group: injected-duplicate\n"
        + "  cancel-in-progress: false\n",
        "M-dup",
    )


def r1_remove_top_concurrency(t: str) -> str:
    return _replace_once(t, A_TOP_CONCURRENCY, "", "R-1")


def r2_group_third_expr(t: str) -> str:
    return _replace_once(
        t,
        "  group: ${{ github.workflow }}-${{ github.event_name == 'pull_request' "
        "&& github.event.pull_request.number || github.run_id }}\n",
        "  group: ${{ github.sha }}\n",
        "R-2",
    )


def r4_remove_one_timeout(t: str) -> str:
    """job2 의 timeout-minutes 1개만 삭제 (2 → 1)."""
    return _replace_once(
        t,
        "    runs-on: ubuntu-latest\n"
        "    timeout-minutes: 10   # MTD-1325 D3 — tier: 경량 체크 (hung-잡 360분 슬롯 점유 차단)\n",
        "    runs-on: ubuntu-latest\n",
        "R-4",
    )


def r5_market_job2_canonical(t: str) -> str:
    """market job2 runs-on → ubuntu-latest (로컬 개조 소실)."""
    return _replace_once(t, A_MARKET_JOB2_RUNS_ON,
                         "    runs-on: ubuntu-latest\n"
                         "    steps:\n"
                         "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1\n"
                         "      - name: Set up Python\n",
                         "R-5")


def r6_timeout_job_to_step(t: str) -> str:
    """job1 timeout-minutes 를 job-level → step-level 로 **이동** (카디널리티 불변)."""
    return _replace_once(
        t,
        A_JOB1_TIMEOUT,
        "    steps:\n"
        "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1\n"
        "        timeout-minutes: 10\n"
        "\n"
        "      - name: Bypass note (label present)\n",
        "R-6",
    )


def r7_coe_step_to_job2(t: str) -> str:
    """continue-on-error 를 job1.step → job2.job-level 로 **이동** (총 1개 불변)."""
    t = _replace_once(t, A_STEP_COE + "  # CFP-2490", "        # (moved)  # CFP-2490", "R-7/remove")
    t = _replace_once(
        t,
        A_JOB2_HEADER,
        A_JOB2_HEADER + "    continue-on-error: true\n",
        "R-7/add",
    )
    return t


def t_taut_overwrite(t: str) -> str:
    """사본(backtest 정본 형상)을 mctrader 자리에 통째로 덮음 — 로컬 개조 전멸."""
    return (FIXTURE_DIR / "mctrader-backtest.yml").read_text(encoding="utf-8")


# ── 축 격리 변형 (지정형이 두 축을 섞을 때 판별용) ──────────────────────────
# 지정형 M-envfile 은 **step 을 추가**하므로 step 인덱스가 밀려 env_keys·coe 경로가
# 부수적으로 변한다. 그 RED 는 env-file 축의 검출이 아니다. 아래 in-place 변형은
# 기존 step[2] 의 run 문면에만 기입해 **env-file 축을 단독 격리**한다.
A_RUN_TAIL = '          echo "$OUT" >> "$GITHUB_STEP_SUMMARY"\n'


def m_envfile_inplace(t: str) -> str:
    return _replace_once(
        t, A_RUN_TAIL,
        A_RUN_TAIL + '          echo "STORY_KEY_PREFIX=CFP" >> "$GITHUB_ENV"\n',
        "M-envfile-inplace")


def m_envfile_blk_inplace(t: str) -> str:
    return _replace_once(
        t, A_RUN_TAIL,
        A_RUN_TAIL
        + "          {\n"
        + '            echo "STORY_KEY_PREFIX=CFP"\n'
        + '          } >> "$GITHUB_ENV"\n',
        "M-envfile-blk-inplace")


def m_dup_same(t: str) -> str:
    """**값이 동일한** 중복 키 주입 — last-wins 가 값을 바꾸지 않는 형태.

    지정형 M-dup 은 다른 값을 넣어 last-wins 가 group 을 바꾸므로 E2 가 **부수적으로**
    RED 가 된다(중복 자체의 검출이 아니다). 본 변형은 그 우연 경로를 제거해
    `DupSafeLoader` 단독 기여를 격리한다.
    """
    return _replace_once(t, A_TOP_CONCURRENCY, A_TOP_CONCURRENCY + A_TOP_CONCURRENCY,
                         "M-dup-same")


# ── P4 rc 흡수군 + degenerate (§8.B) ────────────────────────────────────────
# ★ Change Plan §8.B L731/L733 declared: M-13h~M-13j 는 **정적 층 GREEN 유지 가능**이
#   기대값이다(완결 근거 = M-13a 런타임 kill). W-13 에는 run 문면 rc-관용구 스캐너가
#   없으므로 GREEN 은 결함이 아니라 **선언된 정직 천장**이다.
A_JOB2_RUN = "      - name: Run test_check-parallel-work-sentinel.sh (회귀 시 exit 1 차단)\n" \
             "        run: bash tests/scripts/test_check-parallel-work-sentinel.sh\n"


def _job2_run(repl: str, label: str) -> Callable[[str], str]:
    def fn(t: str) -> str:
        return _replace_once(t, A_JOB2_RUN, repl, label)
    return fn


# ★ `run: cmd || :` 를 **평문 스칼라**로 쓰면 줄 끝 `: ` 가 YAML 매핑 키로 읽혀
#   parse error 가 난다(1차 실행에서 실측 — 그 RED 는 rc 흡수 검출이 아니라 하네스
#   결함이었다). 실제 우회자가 쓸 형태 = 블록 스칼라. 그 형태로 교정한다.
m_13h = _job2_run(
    "      - name: Run test_check-parallel-work-sentinel.sh (회귀 시 exit 1 차단)\n"
    "        run: |\n"
    "          bash tests/scripts/test_check-parallel-work-sentinel.sh || :\n", "M-13h")
m_13i = _job2_run(
    "      - name: Run test_check-parallel-work-sentinel.sh (회귀 시 exit 1 차단)\n"
    "        run: bash tests/scripts/test_check-parallel-work-sentinel.sh ; true\n", "M-13i")
m_13j = _job2_run(
    "      - name: Run test_check-parallel-work-sentinel.sh (회귀 시 exit 1 차단)\n"
    "        run: |\n"
    "          set +e\n"
    "          bash tests/scripts/test_check-parallel-work-sentinel.sh\n"
    "          exit 0\n", "M-13j")
m_13k = _job2_run(
    "      - name: Run test_check-parallel-work-sentinel.sh (회귀 시 exit 1 차단)\n"
    "        shell: bash {0}\n"
    "        run: bash tests/scripts/test_check-parallel-work-sentinel.sh\n", "M-13k")


def m_13l(t: str) -> str:
    """workflow 최상단 `defaults.run.shell` 1줄 우회 (원거리 표면)."""
    return _replace_once(
        t, "permissions:\n",
        "defaults:\n  run:\n    shell: bash {0}\n\npermissions:\n", "M-13l")


def m_13e_empty(t: str) -> str:
    return ""


def m_13e_malformed(t: str) -> str:
    return _replace_once(t, A_JOB1_HEADER, A_JOB1_HEADER + "    : : [unbalanced\n", "M-13e/malformed")


def m_13e_delete(t: str) -> str:
    return "__DELETE__"


MUTANTS: Dict[str, Tuple[str, Callable[[str], str], str]] = {
    "M-13h":            ("mctrader-sentinel.yml", m_13h,           "정적 GREEN (declared — 완결=M-13a 런타임)"),
    "M-13i":            ("mctrader-sentinel.yml", m_13i,           "정적 GREEN (declared)"),
    "M-13j":            ("mctrader-sentinel.yml", m_13j,           "정적 GREEN (declared)"),
    "M-13k":            ("mctrader-sentinel.yml", m_13k,           "RED (step_shell 신설로 관측)"),
    "M-13l":            ("mctrader-sentinel.yml", m_13l,           "RED (defaults_run_shell 신설로 관측)"),
    "M-13e-empty":      ("mctrader-sentinel.yml", m_13e_empty,     "exit 2 (P-3 not_mapping)"),
    "M-13e-malformed":  ("mctrader-sentinel.yml", m_13e_malformed, "exit 2 (P-2 parse_error)"),
    "M-13e-delete":     ("mctrader-sentinel.yml", m_13e_delete,    "exit 2 (P-1 file_missing)"),
    "M-envfile-inplace":     ("mctrader-sentinel.yml", m_envfile_inplace,     "RED (축 격리)"),
    "M-envfile-blk-inplace": ("mctrader-sentinel.yml", m_envfile_blk_inplace, "GREEN (declared 한계, 축 격리)"),
    "M-dup-same":            ("mctrader-sentinel.yml", m_dup_same,            "RED (exit 2) — pytest 는 눈멂 예상"),
    # P0
    "M-envfile":     ("mctrader-sentinel.yml", m_envfile,            "RED (env_file_keys 신규 키)"),
    "M-envfile-blk": ("mctrader-sentinel.yml", m_envfile_blk,        "GREEN (declared 미포섭 한계)"),
    "M-envkey":      ("mctrader-sentinel.yml", m_envkey,             "RED (env_keys 3레벨)"),
    "M-envctr":      ("mctrader-sentinel.yml", m_envctr,             "RED (container_env_keys)"),
    # P1
    "M-quot":        ("mctrader-backtest.yml", m_quot,               "RED (E6 — 따옴표 키)"),
    "M-job4":        ("mctrader-backtest.yml", m_job4,               "RED (E7 — 4칸 들여쓰기)"),
    # P2
    "M-own1":        ("mctrader-sentinel.yml", m_own1,               "RED — job1 leg 만"),
    "M-own2":        ("mctrader-sentinel.yml", m_own2,               "RED — job2 leg 만"),
    "M-dup":         ("mctrader-sentinel.yml", m_dup,                "RED (exit 2 meta-error)"),
    # P3
    "R-1":           ("mctrader-sentinel.yml", r1_remove_top_concurrency, "E1 RED"),
    "R-2":           ("mctrader-sentinel.yml", r2_group_third_expr,  "E2 RED ∧ E1/E3/E4/E5 GREEN"),
    "R-4":           ("mctrader-sentinel.yml", r4_remove_one_timeout, "E5 RED"),
    "R-5":           ("mctrader-market.yml",   r5_market_job2_canonical, "E8 RED"),
    "R-6":           ("mctrader-sentinel.yml", r6_timeout_job_to_step, "E5 RED (relocation)"),
    "R-7":           ("mctrader-sentinel.yml", r7_coe_step_to_job2,  "leg③ RED (relocation)"),
    "T-taut":        ("mctrader-sentinel.yml", t_taut_overwrite,     "straw GREEN ∧ real RED"),
}


# ── (a) 테스트면 오라클 실행 ─────────────────────────────────────────────────
def run_pytest_face(run_dir: Path) -> Dict[str, object]:
    test_copy = run_dir / "tests" / "scripts" / "test_cfp2978_workflow_shape.py"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_copy), "-q", "--tb=line", "-rf", "-p", "no:cacheprovider"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(run_dir),
    )
    out = proc.stdout + proc.stderr
    failed = sorted({
        line.split("::")[-1].split(" ")[0]
        for line in out.splitlines()
        if line.startswith("FAILED") and "::" in line
    })
    errored = sorted({
        line.split("::")[-1].split(" ")[0]
        for line in out.splitlines()
        if line.startswith("ERROR") and "::" in line
    })
    return {
        "returncode": proc.returncode,
        "failed_legs": failed,
        "errored_legs": errored,
        "verdict": "GREEN" if proc.returncode == 0 else "RED",
        "raw": out,
    }


# ── (b) 실 모듈(W-13) 오라클 실행 ────────────────────────────────────────────
_PRISTINE_CACHE: Dict[str, object] = {}


def _pristine_sentinel():
    """원본(무변이) sentinel fixture 의 W-13 shape — 대조 기준값의 SSOT."""
    import workflow_shape as ws
    if "sentinel" not in _PRISTINE_CACHE:
        _PRISTINE_CACHE["sentinel"] = ws.load_workflow_shape(
            str(FIXTURE_DIR / "mctrader-sentinel.yml"))
    return _PRISTINE_CACHE["sentinel"]


def _dict_delta(base: dict, cur: dict) -> dict:
    """기준 대비 추가/삭제/변경된 항목만 (전문 덤프 대신 위반 경로 열거 — §8.A 규칙)."""
    d = {}
    for k in set(base) | set(cur):
        if base.get(k) != cur.get(k):
            d[k] = {"base": base.get(k), "mutant": cur.get(k)}
    return d


def _w13_legs(fixdir: Path) -> Dict[str, object]:
    """W-13 `load_workflow_shape` 위에 E1~E8 + 소속(leg③) + 주입채널 leg 을 세운다."""
    import workflow_shape as ws

    legs: Dict[str, object] = {}
    raw: Dict[str, object] = {}

    def fail(name: str, msg: str) -> None:
        legs[name] = f"RED: {msg}"

    # --- mctrader (sentinel) -------------------------------------------------
    try:
        s = ws.load_workflow_shape(str(fixdir / "mctrader-sentinel.yml"))
    except ws.ShapeError as e:
        for n in ("E1", "E2", "E3", "E4", "E5", "leg3-own1", "leg3-own2",
                  "env-file", "env-keys", "env-ctr"):
            fail(n, f"ShapeError[{e.error_kind}] (CLI exit 2)")
        raw["sentinel_error"] = e.to_payload()
        s = None

    if s is not None:
        legs["E1"] = "GREEN" if (s.top_concurrency is not None
                                 and "concurrency" in s.concurrency_paths) else "RED"
        grp = (s.top_concurrency or {}).get("group")
        legs["E2"] = "GREEN" if grp == PIN_MCTRADER_GROUP else f"RED: group={grp!r}"
        legs["E3"] = "GREEN" if grp != TEMPLATE_GROUP else "RED: template expr"
        jobc = [p for p in s.concurrency_paths if p.startswith("jobs.")]
        legs["E4"] = "GREEN" if not jobc else f"RED: {jobc}"
        jt = {k: v for k, v in s.timeout_paths.items() if "[" not in k}
        legs["E5"] = ("GREEN" if (len(jt) == 2 and all(v == 10 for v in jt.values()))
                      else f"RED: {sorted(jt.items())}")
        # leg ③ — 소속 판정 (W-13 `_owned_by`)
        try:
            own1 = s.coe_paths_of(JOB1)
            own2 = s.coe_paths_of(JOB2)
            legs["leg3-own1"] = ("GREEN" if own1 == [f"jobs.{JOB1}.steps[2].continue-on-error"]
                                 else f"RED: {own1}")
            legs["leg3-own2"] = "GREEN" if own2 == [] else f"RED: {own2}"
            # bare startswith 대조 실증 (결격 구현이었다면 무엇이 되는가)
            bare1 = [p for p in s.coe_paths if p.startswith(f"jobs.{JOB1}")]
            bare2 = [p for p in s.coe_paths if p.startswith(f"jobs.{JOB2}")]
            raw["ownership"] = {
                "coe_paths": s.coe_paths,
                "owned_by(job1)": own1, "owned_by(job2)": own2,
                "bare_startswith(job1)": bare1, "bare_startswith(job2)": bare2,
                "bare_misclassifies": bare1 != own1 or bare2 != own2,
            }
        except ws.ShapeError as e:
            fail("leg3-own1", f"ShapeError[{e.error_kind}]")
            fail("leg3-own2", f"ShapeError[{e.error_kind}]")
        # 주입 채널 leg — 기준값은 **원본 fixture 에서 실측**한 것과 대조한다
        # (손으로 적은 기대값은 그 자체가 오라클 결함원이 된다 — baseline 1차 실행에서 실증).
        b = _pristine_sentinel()
        legs["env-file"] = ("GREEN" if s.env_file_keys == b.env_file_keys
                            else f"RED: {s.env_file_keys} (base={b.env_file_keys})")
        legs["env-keys"] = ("GREEN" if s.env_keys == b.env_keys
                            else f"RED: {_dict_delta(b.env_keys, s.env_keys)}")
        legs["env-ctr"] = ("GREEN" if s.container_env_keys == b.container_env_keys
                           else f"RED: {s.container_env_keys}")
        # §8.B rc 흡수 — shell 우회 표면 (M-13k / M-13l)
        legs["shell-step"] = ("GREEN" if s.step_shell == b.step_shell
                              else f"RED: {_dict_delta(b.step_shell, s.step_shell)}")
        legs["shell-defaults"] = ("GREEN" if (s.defaults_run_shell == b.defaults_run_shell
                                              and s.job_defaults_run_shell == b.job_defaults_run_shell)
                                  else f"RED: wf={s.defaults_run_shell!r} job={s.job_defaults_run_shell}")
        raw["sentinel_shape"] = s.to_dict()

    # --- backtest / engine / market -----------------------------------------
    for nm, fn in (("backtest", "mctrader-backtest.yml"),
                   ("engine", "mctrader-engine.yml"),
                   ("market", "mctrader-market.yml")):
        try:
            o = ws.load_workflow_shape(str(fixdir / fn))
        except ws.ShapeError as e:
            legs[f"E6[{nm}]"] = f"RED: ShapeError[{e.error_kind}] (exit 2)"
            legs[f"E7[{nm}]"] = f"RED: ShapeError[{e.error_kind}] (exit 2)"
            continue
        legs[f"E6[{nm}]"] = "GREEN" if o.top_concurrency is None and \
            "concurrency" not in o.concurrency_paths else f"RED: {o.concurrency_paths}"
        jc = [p for p in o.concurrency_paths if p.startswith("jobs.")]
        legs[f"E7[{nm}]"] = "GREEN" if not jc else f"RED: {jc}"
        if nm == "market":
            canon = {JOB1: CANON_RUNS_ON, JOB2: "ubuntu-latest"}
            delta = ws.runs_on_local_delta(o, canon)
            legs["E8"] = "GREEN" if JOB2 in delta else f"RED: delta={delta}"
            raw["market_runs_on"] = o.runs_on
            raw["market_delta"] = delta

    return {"legs": legs, "raw": raw}


def run_w13_face(fixdir: Path) -> Dict[str, object]:
    res = _w13_legs(fixdir)
    legs = res["legs"]
    reds = sorted(k for k, v in legs.items() if str(v).startswith("RED"))
    return {
        "verdict": "GREEN" if not reds else "RED",
        "red_legs": reds,
        "legs": legs,
        "raw": res["raw"],
    }


# ── straw 대조군 (T-taut 짝 관측) ────────────────────────────────────────────
def run_straw_face(fixdir: Path) -> Dict[str, object]:
    """밀짚 오라클 — W-14 `test_oracle_taut_*` 이 쓰는 형태 그대로.

    "두 job 에 runs-on 이 존재하는가" 만 본다. 정본 상속값을 포함한 원시
    `runs_on` 위의 assert 라 **항진에 가깝다** (판별력 ~0).
    """
    import workflow_shape as ws
    try:
        s = ws.load_workflow_shape(str(fixdir / "mctrader-sentinel.yml"))
    except ws.ShapeError as e:
        return {"verdict": "RED", "detail": f"ShapeError[{e.error_kind}]"}
    ok = all(jid in s.runs_on for jid in (JOB1, JOB2))
    return {"verdict": "GREEN" if ok else "RED", "detail": {"runs_on": s.runs_on}}


# ── 실행 ─────────────────────────────────────────────────────────────────────
def build_run_tree(mid: str) -> Path:
    run_dir = SCRATCH / mid
    if run_dir.exists():
        shutil.rmtree(run_dir)
    (run_dir / "tests" / "scripts").mkdir(parents=True)
    (run_dir / "tests" / "fixtures" / "cfp2978").mkdir(parents=True)
    (run_dir / "scripts" / "lib").mkdir(parents=True)
    shutil.copy2(TEST_FILE, run_dir / "tests" / "scripts" / TEST_FILE.name)
    shutil.copy2(CONFTEST, run_dir / "tests" / "scripts" / "conftest.py")
    # W-13 원본은 **변이 대상이 아니다** — 변이는 fixture 에만 가한다.
    shutil.copy2(W13_MODULE, run_dir / "scripts" / "lib" / W13_MODULE.name)
    for f in FIXTURES:
        shutil.copy2(FIXTURE_DIR / f, run_dir / "tests" / "fixtures" / "cfp2978" / f)
    return run_dir


def run_one(mid: str) -> Dict[str, object]:
    target, fn, expected = MUTANTS[mid]
    run_dir = build_run_tree(mid)
    fixdir = run_dir / "tests" / "fixtures" / "cfp2978"

    # 변이 적용 (앵커 적중 강제)
    src = (fixdir / target).read_text(encoding="utf-8")
    mutated = fn(src)
    if mutated == src:
        raise SystemExit(f"[NO-OP] {mid}: 변이 결과가 원본과 동일 — 관측 무효")
    if mutated == "__DELETE__":
        (fixdir / target).unlink()            # P-1 축 (파일 소실)
    else:
        (fixdir / target).write_text(mutated, encoding="utf-8", newline="")

    pytest_res = run_pytest_face(run_dir)
    w13_res = run_w13_face(fixdir)
    straw_res = run_straw_face(fixdir)

    result = {
        "mutant": mid,
        "target": target,
        "expected": expected,
        "pytest_face": {k: v for k, v in pytest_res.items() if k != "raw"},
        "w13_face": {k: v for k, v in w13_res.items() if k != "raw"},
        "straw_face": straw_res,
        "run_dir": str(run_dir),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{mid}.pytest.txt").write_text(pytest_res["raw"], encoding="utf-8")
    (LOG_DIR / f"{mid}.json").write_text(
        json.dumps({**result, "w13_raw": w13_res["raw"]}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return result


def baseline() -> Dict[str, object]:
    """변이 0 기준선 — 두 면 모두 GREEN 이어야 관측이 성립한다."""
    run_dir = build_run_tree("_baseline")
    fixdir = run_dir / "tests" / "fixtures" / "cfp2978"
    p = run_pytest_face(run_dir)
    w = run_w13_face(fixdir)
    s = run_straw_face(fixdir)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "_baseline.pytest.txt").write_text(p["raw"], encoding="utf-8")
    (LOG_DIR / "_baseline.json").write_text(
        json.dumps({"pytest": {k: v for k, v in p.items() if k != "raw"},
                    "w13": w, "straw": s}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return {"pytest": {k: v for k, v in p.items() if k != "raw"}, "w13": w, "straw": s}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--run", nargs="*", default=None)
    ap.add_argument("--run-all", action="store_true")
    a = ap.parse_args()

    if a.list:
        for k, (t, _, e) in MUTANTS.items():
            print(f"{k:16} target={t:24} expected={e}")
        return 0
    if a.baseline:
        print(json.dumps(baseline(), ensure_ascii=False, indent=2, default=str))
        return 0

    ids = list(MUTANTS) if a.run_all else (a.run or [])
    out = []
    for mid in ids:
        if mid not in MUTANTS:
            raise SystemExit(f"unknown mutant: {mid}")
        r = run_one(mid)
        out.append(r)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        print("-" * 78)
    (LOG_DIR / "summary.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
