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

# Windows stdout encoding fix (UTF-8 for Korean characters)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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

# ── ★ wrapper job2 run 블록 문면 — **단일 원본** (2026-08-19 정정) ───────────
#  왜 상수로 올렸나: 아래 M-13h~k · M-16-* 7개 함수가 이 문면을 **각자 리터럴로
#  복제**하고 있었고, CFP-2978 W-3b(파일목록 4→5) · W-3b-1(로스터 6→12) ·
#  W-3d(V1b `set -euo pipefail`) 착지로 문면이 이동하자 **7개가 동시에
#  ANCHOR-MISS** 로 죽었다.
#  ★재현 명령 (수치를 박지 않는다 — 이름 집합으로 판정한다):
#    python - <<'PY'
#    import importlib.util,sys
#    s=importlib.util.spec_from_file_location("mh", "tests/scripts/cfp2978-mutant-lab/mutant_harness.py")
#    m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
#    live=open(".github/workflows/parallel-work-sentinel-check.yml",encoding="utf-8").read()
#    miss=[k for k,v in m.MUTANTS.items()
#          if v[0].endswith("parallel-work-sentinel-check.yml")
#          and (lambda f: (f(live), False)[1] if not _try(f,live) else True)(v[1])]
#    PY
#   ⇒ 판정 = *"wrapper workflow 대상 mutant 중 ANCHOR-MISS 인 **이름 집합이 공집합**"*
#     (개수 assert 금지 — 일반 규칙 ①).
#  ★ job2 가 다시 편집되면 **여기만** 고친다.
J2_PYTEST_FILES = (
    "tests/scripts/test_cfp2976_sentinel_prefix.py "
    "tests/scripts/test_consumer_asset_currency.py "
    "tests/scripts/test_cfp2978_workflow_shape.py "
    "tests/scripts/test_cfp2978_resource_scan_shape.py "
    "tests/scripts/test_cfp2978_envelope_pin.py"
)
#  collect step 의 node-ID 로스터 (W-3b-1 — 순서까지 문면 그대로)
J2_COLLECT_ROSTER = (
    "test_2976_a_derive_from_overlay",
    "test_2976_b_fail_closed",
    "test_2976_c_determined_contract",
    "test_d4_leg1_ingest_funnel_projects_four_keys",
    "test_d4_leg2_file_level_response_rejected",
    "test_d4_leg3_no_forbidden_key_access_literal",
    "test_envelope_pin_reference_matches_landed_pin",
    "test_envelope_pin_domain_derivation_selfcheck",
    "test_envelope_pin_coverage_table_witnesses",
    "test_ac4_leg1_determined_is_true_and_lists_present",
    "test_ac4_leg2_branch_names_match_corpus_regex",
    "test_ac4_leg3_excluded_self_repo_is_slug",
)
A_J2_RUNPYTEST_HEAD = (
    "      - name: Run pytest tests (W-3b)\n"
    "        id: run-pytest\n"
)
A_J2_RUNPYTEST_BODY = (
    "        run: |\n"
    "          set -euo pipefail\n"
    f"          python3 -m pytest {J2_PYTEST_FILES} -q\n"
)
A_J2_COLLECT = (
    "      - name: Collect pytest tests (W-3b-1, verify node IDs present)\n"
    "        id: collect\n"
    "        run: |\n"
    "          set -euo pipefail\n"
    f"          python3 -m pytest {J2_PYTEST_FILES} --collect-only -q"
    " > /tmp/pytest_collected.txt 2>&1\n"
    "          cat /tmp/pytest_collected.txt\n"
) + "".join(
    f'          grep -q "{_n}" /tmp/pytest_collected.txt'
    f' || {{ echo "ERROR: {_n} not found"; exit 1; }}\n'
    for _n in J2_COLLECT_ROSTER
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


# ★ M-13h~l: wrapper workflow 의 "Run pytest tests (W-3b)" step 의 run block 변이.
#   Step name 앵커로 안전하게 위치 고정. 평문 스칼라 `run: cmd || :` 는 YAML 파싱 에러 → 블록 스칼라.

def m_13h(t: str) -> str:
    """'Run pytest tests (W-3b)' step 의 run block 을 `|| :` 우회로 변경."""
    new_run = A_J2_RUNPYTEST_BODY.replace(" -q\n", " -q || :\n")
    return _replace_once(
        t,
        A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY,
        A_J2_RUNPYTEST_HEAD + new_run,
        "M-13h",
    )


def m_13i(t: str) -> str:
    """'Run pytest tests (W-3b)' step 의 run block 을 `; true` 형태로 변경."""
    new_run = A_J2_RUNPYTEST_BODY.replace(" -q\n", " -q ; true\n")
    return _replace_once(
        t,
        A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY,
        A_J2_RUNPYTEST_HEAD + new_run,
        "M-13i",
    )


def m_13j(t: str) -> str:
    """'Run pytest tests (W-3b)' step 의 run block 을 `set +e` + `exit 0` 으로 변경 (둘 다)."""
    # ★ V1b(`set -euo pipefail`) 착지 후이므로 「set +e 로 교체 + 말미 exit 0」이
    #   원 의도(rc 흡수)의 현행 판본이다.
    new_run = A_J2_RUNPYTEST_BODY.replace(
        "          set -euo pipefail\n", "          set +e\n"
    ) + "          exit 0\n"
    return _replace_once(
        t,
        A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY,
        A_J2_RUNPYTEST_HEAD + new_run,
        "M-13j",
    )


def m_13k(t: str) -> str:
    """'Run pytest tests (W-3b)' step 에 step-level shell 주입."""
    new_run = "        shell: bash {0}\n" + A_J2_RUNPYTEST_BODY
    return _replace_once(
        t,
        A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY,
        A_J2_RUNPYTEST_HEAD + new_run,
        "M-13k",
    )


def m_13l(t: str) -> str:
    """workflow 최상단 `defaults.run.shell` 1줄 우회 (원거리 표면)."""
    return _replace_once(
        t, "permissions:\n",
        "defaults:\n  run:\n    shell: bash {0}\n\npermissions:\n", "M-13l")


# ── W-16 신규 mutant (정의역 확장 축) ────────────────────────────────────────
# W-16 leg 는 `.github/workflows/` ∧ `templates/github-workflows/` 양쪽을 본다.
# 단독 변이는 canonical 을 주로 겨냥하고, twin-drift 는 template 만 변경한다.


def m_16_rm_w3b(t: str) -> str:
    """'Run pytest tests (W-3b)' step 통째 제거 (job2 에서)."""
    return _replace_once(
        t, A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY, "", "M-16-rm-w3b"
    )


def m_16_rm_install(t: str) -> str:
    """'Install test dependencies' step 제거 (job2 에서)."""
    return _replace_once(
        t,
        "      - name: Install test dependencies\n"
        "        run: python -m pip install --quiet pytest pyyaml\n",
        "",
        "M-16-rm-install"
    )


def m_16_rm_collect(t: str) -> str:
    """'Collect pytest tests (W-3b-1, ...)' step 통째 제거 (job2 에서)."""
    return _replace_once(t, A_J2_COLLECT, "", "M-16-rm-collect")


def m_16_coe_job2(t: str) -> str:
    """job2 pytest step 에 continue-on-error: true 주입 (leg③)."""
    return _replace_once(
        t,
        "      - name: Run pytest tests (W-3b)\n"
        "        id: run-pytest\n",
        "      - name: Run pytest tests (W-3b)\n"
        "        id: run-pytest\n"
        "        continue-on-error: true\n",
        "M-16-coe-job2"
    )


def m_16_trailing_cmd(t: str) -> str:
    """W-3b run block 에 후행 명령 1줄 추가 (W-3b 블록 스칼라화 축)."""
    # ★ run 은 이미 블록 스칼라(W-3d V1b)이므로 「후행 명령 1줄 추가」가 현행 판본.
    new_run = A_J2_RUNPYTEST_BODY + '          echo "Pytest completed"\n'
    return _replace_once(
        t,
        A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY,
        A_J2_RUNPYTEST_HEAD + new_run,
        "M-16-trailing-cmd",
    )


def m_16_job_defaults_shell(t: str) -> str:
    """job2 에 defaults.run.shell 주입 (A5 축 — job 레벨 reach)."""
    return _replace_once(
        t,
        "  parallel-work-sentinel-test:\n",
        "  parallel-work-sentinel-test:\n"
        "    defaults:\n"
        "      run:\n"
        "        shell: bash {0}\n",
        "M-16-job-defaults-shell"
    )


def m_16_twin_drift(t: str) -> str:
    """twin 정의역만: step shell 주입 (독립성 검증용)."""
    # 이 함수는 templates/github-workflows/… 에만 적용된다.
    # 실제 변이는 run_one 호출 시 target 이 "templates/…" 로 지정되면 작동.
    return _replace_once(
        t,
        "      - name: Run pytest tests (W-3b)\n"
        "        id: run-pytest\n",
        "      - name: Run pytest tests (W-3b)\n"
        "        id: run-pytest\n"
        "        shell: bash {0}\n",
        "M-16-twin-drift"
    )


# ── 복합 mutant 함수 (독립적 순차 적용 불가능한 쌍) ───────────────────────────
# M-13i 와 M-13k 는 같은 step 의 다른 부분을 변경하므로, 순차 적용하면
# 앵커 미적중이 발생한다. 복합 변이 함수를 별도로 작성한다.


def m_composite_13i_13k(t: str) -> str:
    """복합: '; true' 추가 + step 'shell: bash {0}' (동시 적용)."""
    new_run = "        shell: bash {0}\n" + A_J2_RUNPYTEST_BODY.replace(" -q\n", " -q ; true\n")
    return _replace_once(
        t,
        A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY,
        A_J2_RUNPYTEST_HEAD + new_run,
        "M-13i+M-13k",
    )


def m_composite_13i_13l(t: str) -> str:
    """복합: '; true' 추가 + workflow 'defaults.run.shell' (동시 적용, A4 축)."""
    # 먼저 workflow 레벨 defaults 추가
    t = _replace_once(
        t, "permissions:\n",
        "defaults:\n  run:\n    shell: bash {0}\n\npermissions:\n", "M-13i+M-13l/defaults")
    # 그 후 pytest step에 '; true' 추가
    new_run = A_J2_RUNPYTEST_BODY.replace(" -q\n", " -q ; true\n")
    return _replace_once(
        t,
        A_J2_RUNPYTEST_HEAD + A_J2_RUNPYTEST_BODY,
        A_J2_RUNPYTEST_HEAD + new_run,
        "M-13i+M-13l/run",
    )


def m_13a(t: str) -> str:
    """scripts/lib/check_parallel_work_sentinel.py 의 _exit_pass 에서
    payload.setdefault("determined", True) 줄 제거 (L184 상당).
    기대값 = 런타임 RED (M-13a 단독 killer). 정적 피드백 불가.
    test_cfp2976_sentinel_prefix.py 의 test_2976_c_determined_contract 가
    setdefault 부재를 assert 해 RED 를 관측.
    """
    # 앵커: "    payload.setdefault" 4칸 들여쓰기 줄 (docstring 무관)
    anchor = '    payload.setdefault("determined", True)'
    return _replace_once(t, anchor, '', "M-13a")


def m_13e_empty(t: str) -> str:
    return ""


def m_13e_malformed(t: str) -> str:
    return _replace_once(t, A_JOB1_HEADER, A_JOB1_HEADER + "    : : [unbalanced\n", "M-13e/malformed")


def m_13e_delete(t: str) -> str:
    return "__DELETE__"


MUTANTS: Dict[str, Tuple[str, Callable[[str], str], str]] = {
    "M-13a":            ("scripts/lib/check_parallel_work_sentinel.py", m_13a, "RED (런타임 kill — determined 부재)"),
    "M-13h":            (".github/workflows/parallel-work-sentinel-check.yml", m_13h, "정적 GREEN (declared) | 중첩 runtime: delta 소멸 (rc 흡수)"),
    "M-13i":            (".github/workflows/parallel-work-sentinel-check.yml", m_13i, "정적 GREEN (declared) | 중첩 runtime: delta 소멸"),
    "M-13j":            (".github/workflows/parallel-work-sentinel-check.yml", m_13j, "정적 GREEN (declared) | 중첩 runtime: delta 소멸 (set +e + exit 0)"),
    "M-13k":            (".github/workflows/parallel-work-sentinel-check.yml", m_13k, "정적 RED (w16_c: step_shell 신설) | 중첩 runtime: delta 소멸"),
    "M-13l":            (".github/workflows/parallel-work-sentinel-check.yml", m_13l, "정적 RED (w16_d: defaults_run_shell 신설) | 중첩 runtime: delta 소멸"),
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
    # W-16 신규 — 정의역 확장 축
    "M-16-rm-w3b":       (".github/workflows/parallel-work-sentinel-check.yml", m_16_rm_w3b,        "모든 w16 leg RED (W-3b 임계) + 봉투 핀 RED"),
    "M-16-rm-install":   (".github/workflows/parallel-work-sentinel-check.yml", m_16_rm_install,    "w16_a, b, c, d, f RED (w16_e 미포함) + 봉투 핀 RED"),
    "M-16-rm-collect":   (".github/workflows/parallel-work-sentinel-check.yml", m_16_rm_collect,    "w16_a, b, c, d, f RED (w16_e 미포함) + 봉투 핀 RED"),
    "M-16-coe-job2":     (".github/workflows/parallel-work-sentinel-check.yml", m_16_coe_job2,      "w16_b RED (leg③ — job2 coe 주입)"),
    "M-16-trailing-cmd": (".github/workflows/parallel-work-sentinel-check.yml", m_16_trailing_cmd,  "봉투 핀(PIN_ENVELOPE_SHA256) RED — 구 담지자 w16_g 는 폐기(설계 §8.B: run 스칼라 전문이 봉투에 담겨 계수 핀을 승계)"),
    "M-16-job-defaults-shell": (".github/workflows/parallel-work-sentinel-check.yml", m_16_job_defaults_shell, "w16_d RED (A5 축 — job defaults.run.shell)"),
    "M-16-twin-drift":   ("templates/github-workflows/parallel-work-sentinel-check.yml", m_16_twin_drift, "[wrapper-twin] RED ∧ [wrapper-canonical] GREEN (독립성)"),
}


# ── 복합 mutant 로스터 (구성 + 기대값) ──────────────────────────────────────────
# rc 흡수 판별은 대조(delta 소멸)에서만 선다. 단독은 RED, 복합은 GREEN 이어야
# 흡수가 성립함을 입증한다. 이를 "같은 실행 계열"에서 보여야 논증이 성립.
COMPOSITES: Dict[str, Tuple[List[str], Callable[[str], str], str]] = {
    "M-13i+M-13k": (
        ["M-13i", "M-13k"],
        m_composite_13i_13k,
        "정적 RED(w16_c ∧ w16_e) ∧ 런타임 GREEN(흡수 성립)"
    ),
    "M-13i+M-13l": (
        ["M-13i", "M-13l"],
        m_composite_13i_13l,
        "정적 RED(w16_d ∧ w16_e) ∧ 런타임 GREEN(흡수 성립, A4 축)"
    ),
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


# ── (d) 런타임 오라클 실행 ─────────────────────────────────────────────────
def run_runtime_face(run_dir: Path) -> Dict[str, object]:
    """run tree 의 workflow 를 W-13 으로 파싱해 job2 의 pytest step 을 실제 실행.

    기대값: M-13a 단독 → rc=1 (determined 부재 → killer test 실패)
           M-13a+rc흡수 → rc=0 (흡수가 오류도 먹음)
    """
    import yaml
    try:
        from workflow_shape import load_workflow_shape
    except ImportError:
        sys.path.insert(0, str(run_dir / "scripts" / "lib"))
        from workflow_shape import load_workflow_shape

    workflow_path = run_dir / ".github" / "workflows" / "parallel-work-sentinel-check.yml"
    if not workflow_path.exists():
        return {"verdict": "ERROR", "reason": "workflow file not found"}

    # workflow YAML 파싱
    with open(workflow_path, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}

    jobs = doc.get("jobs", {})
    job2_def = jobs.get(JOB2, {})
    if not job2_def:
        return {"verdict": "ERROR", "reason": f"job {JOB2} not found"}

    steps = job2_def.get("steps", [])
    if not steps:
        return {"verdict": "ERROR", "reason": "no steps"}

    # Run pytest step 찾기 (id: run-pytest)
    pytest_step = None
    for s in steps:
        if s.get("id") == "run-pytest":
            pytest_step = s
            break

    if not pytest_step or not pytest_step.get("run"):
        return {"verdict": "ERROR", "reason": "pytest step not found"}

    # effective shell 결정
    wf_shell = doc.get("defaults", {}).get("run", {}).get("shell", "bash -e {0}")
    job_shell = job2_def.get("defaults", {}).get("run", {}).get("shell")
    step_shell = pytest_step.get("shell")

    eff_shell = step_shell or job_shell or wf_shell

    # shell 옵션 파싱
    shell_cmd = "bash"
    shell_args = []
    if "{0}" in eff_shell:
        parts = eff_shell.replace("{0}", "").split()
        shell_cmd = parts[0]
        shell_args = parts[1:] if len(parts) > 1 else []

    # pytest step run — Git Bash 로 실행 (셸 연산자 지원)
    try:
        run_cmd = pytest_step["run"]

        # Git Bash 명시 경로 (WSL bash 회피)
        BASH = os.environ.get("CFP2978_BASH", r"C:\Program Files\Git\bin\bash.exe")

        # run 본문을 임시 .sh 파일에 작성
        script_path = run_dir / ".cfp2978_run.sh"
        script_path.write_text(run_cmd, encoding="utf-8")

        # errexit 옵션 결정 (defaults.run.shell에 명시된 경우 제외)
        errexit = True
        if doc.get("defaults", {}).get("run", {}).get("shell"):
            # "bash {0}" 형태 = errexit 없음 (M-13k/M-13l 테스트용)
            if "bash {0}" in doc.get("defaults", {}).get("run", {}).get("shell"):
                errexit = False
        if job_shell and "bash {0}" in job_shell:
            # A5 축 — job 레벨 defaults.run.shell (M-16-job-defaults-shell)
            errexit = False
        if step_shell and "bash {0}" in step_shell:
            errexit = False

        # Git Bash 로 실행
        args = [BASH] + (["-e"] if errexit else []) + [str(script_path)]
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(run_dir), timeout=60)
        rc = result.returncode

        # pytest stdout 파싱: "FAILED <test_name>" 패턴 추출
        failed_tests = []
        for line in result.stdout.splitlines():
            if line.startswith("FAILED"):
                # FAILED tests/scripts/test_xxx.py::test_name - ...
                parts = line.split("::")
                if len(parts) >= 2:
                    test_name = parts[-1].split()[0]  # test_name 까지만
                    failed_tests.append(test_name)

        # continue-on-error 적용
        coe = pytest_step.get("continue-on-error", False)
        if rc != 0 and coe:
            rc = 0

        return {
            "verdict": "GREEN" if rc == 0 else "RED",
            "returncode": result.returncode,
            "rc_after_coe": rc,
            "stdout_lines": len(result.stdout.splitlines()),
            "failed_tests": failed_tests,
            "stderr_excerpt": result.stderr[:200] if result.stderr else "",
        }
    except Exception as e:
        return {"verdict": "ERROR", "reason": str(type(e).__name__)}


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
    (run_dir / ".github" / "workflows").mkdir(parents=True)
    (run_dir / "templates" / "github-workflows").mkdir(parents=True)

    # ── tests/scripts: pytest test 파일 4개 + conftest
    shutil.copy2(CONFTEST, run_dir / "tests" / "scripts" / "conftest.py")
    # ★ 복사 목록은 **job2 가 실제로 실행하는 목록에서 파생**한다 (2026-08-19 정정).
    #   손으로 적은 사본을 두면 job2 목록이 늘 때 갈리고, 갈린 순간 runtime_face 가
    #   `ERROR: file or directory not found` 로 **무변이 baseline 에서도 RED** 가 되어
    #   판별력이 0 이 된다 — 그 면의 RED 는 mutant 검출이 아니라 **하네스 결함**이다.
    #   ★실측(정정 전): `--baseline` 의 runtime_face = RED, 전 M-16 mutant 가 동일
    #     stderr(`test_cfp2978_envelope_pin.py` 부재) ⇒ 항진 RED.
    #   ★재현: `--baseline` 산출의 runtime_face verdict 가 GREEN 이어야 한다
    #     (무변이가 RED 면 어떤 mutant 의 RED 도 검출 근거가 못 된다).
    for test_file in sorted({Path(p).name for p in J2_PYTEST_FILES.split()}):
        src = REPO_ROOT / "tests" / "scripts" / test_file
        if src.exists():
            shutil.copy2(src, run_dir / "tests" / "scripts" / test_file)

    # ── scripts/lib: W-13 + wrapper lib 파일들
    shutil.copy2(W13_MODULE, run_dir / "scripts" / "lib" / W13_MODULE.name)
    for lib_file in [
        "check_parallel_work_sentinel.py",
        "check_consumer_asset_currency.py",
        # ★ W-21 참조 구현 — `test_cfp2978_envelope_pin.py` 가 import 한다.
        #   미배치면 그 테스트가 skip 이 아니라 **수집 ERROR** 로 죽는다.
        "envelope_pin.py",
    ]:
        src = REPO_ROOT / "scripts" / "lib" / lib_file
        if src.exists():
            shutil.copy2(src, run_dir / "scripts" / "lib" / lib_file)

    # ── .github/workflows: 2개 workflow 파일
    for wf_file in [
        "parallel-work-sentinel-check.yml",
        "consumer-asset-currency-check.yml",
    ]:
        src = REPO_ROOT / ".github" / "workflows" / wf_file
        if src.exists():
            shutil.copy2(src, run_dir / ".github" / "workflows" / wf_file)

    # ── templates/github-workflows: workflow template 파일들
    for wf_file in [
        "parallel-work-sentinel-check.yml",
    ]:
        src = REPO_ROOT / "templates" / "github-workflows" / wf_file
        if src.exists():
            shutil.copy2(src, run_dir / "templates" / "github-workflows" / wf_file)

    # ── tests/fixtures: fixture yml + manifest
    for f in FIXTURES:
        shutil.copy2(FIXTURE_DIR / f, run_dir / "tests" / "fixtures" / "cfp2978" / f)
    # fixtures_manifest.md
    manifest_src = FIXTURE_DIR / "fixtures_manifest.md"
    if manifest_src.exists():
        shutil.copy2(manifest_src, run_dir / "tests" / "fixtures" / "cfp2978" / "fixtures_manifest.md")
    # 벤더 fixture sentinel-old-07d1127a.py.txt
    vendor_src = FIXTURE_DIR / "sentinel-old-07d1127a.py.txt"
    if vendor_src.exists():
        shutil.copy2(vendor_src, run_dir / "tests" / "fixtures" / "cfp2978" / "sentinel-old-07d1127a.py.txt")

    return run_dir




def run_one(mid: str) -> Dict[str, object]:
    target, fn, expected = MUTANTS[mid]
    run_dir = build_run_tree(mid)
    fixdir = run_dir / "tests" / "fixtures" / "cfp2978"

    # 변이 적용 (앵커 적중 강제)
    # target 이 fixture 파일명이면 fixdir / target, 아니면 run_dir / target 해석
    if "/" in target or target.startswith("."):
        # run tree 상대경로 (e.g., "scripts/lib/check_parallel_work_sentinel.py")
        target_path = run_dir / target
    else:
        # fixture 파일명 (e.g., "mctrader-sentinel.yml")
        target_path = fixdir / target

    src = target_path.read_text(encoding="utf-8")
    mutated = fn(src)
    if mutated == src:
        raise SystemExit(f"[NO-OP] {mid}: 변이 결과가 원본과 동일 — 관측 무효")
    if mutated == "__DELETE__":
        target_path.unlink()            # P-1 축 (파일 소실)
    else:
        target_path.write_text(mutated, encoding="utf-8", newline="")

    pytest_res = run_pytest_face(run_dir)
    w13_res = run_w13_face(fixdir)
    straw_res = run_straw_face(fixdir)
    runtime_res = run_runtime_face(run_dir)

    result = {
        "mutant": mid,
        "target": target,
        "expected": expected,
        "pytest_face": {k: v for k, v in pytest_res.items() if k != "raw"},
        "w13_face": {k: v for k, v in w13_res.items() if k != "raw"},
        "straw_face": straw_res,
        "runtime_face": runtime_res,
        "run_dir": str(run_dir),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{mid}.pytest.txt").write_text(pytest_res["raw"], encoding="utf-8")
    (LOG_DIR / f"{mid}.json").write_text(
        json.dumps({**result, "w13_raw": w13_res["raw"]}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return result


def run_composite(mids: List[str]) -> Dict[str, object]:
    """★중첩 변이 — 여러 mutant 를 **한 run tree 에 순차 적용**한 뒤 면을 측정한다.

    존재 이유 (§8.B 처방 3):
      rc 흡수 mutant(M-13h~l)는 **단독으로는 판별되지 않는다** — 원래 GREEN 인
      job 이 GREEN 으로 남을 뿐이라 관측이 무정보다. 판별은 오직 대조에서 선다:

          delta(M-13a) != ∅   ∧   delta(M-13h + M-13a) == ∅

      좌항은 "런타임 축에 teeth 가 있다", 우항은 "rc 흡수가 그 teeth 를 삼킨다"
      를 뜻한다. 둘을 **같은 실행 계열**에서 내야 "런타임 축이 상위 방어이고
      흡수 표면이 실재 위협"이라는 결론이 성립한다. 한쪽만 내면 논증이 아니다.

    ★본 함수는 **실행**한다. 추론으로 대체하지 않는다 — 중첩 결과를 논리로
      유도해 적으면 그것은 관측이 아니라 전방 참조다.
    """
    label = "+".join(mids)
    run_dir = build_run_tree(label.replace("+", "_plus_"))
    fixdir = run_dir / "tests" / "fixtures" / "cfp2978"

    for mid in mids:
        if mid not in MUTANTS:
            raise SystemExit(f"unknown mutant in composite: {mid}")
        target, fn, _ = MUTANTS[mid]
        tp = (run_dir / target) if ("/" in target or target.startswith(".")) \
            else (fixdir / target)
        src = tp.read_text(encoding="utf-8")
        mutated = fn(src)
        # 앵커 적중 강제 — 중첩에서 앞선 변이가 뒤 변이의 앵커를 깨뜨렸는데
        # 조용히 no-op 이 되면 "흡수 때문에 GREEN" 을 거짓 주장하게 된다.
        if mutated == src:
            raise SystemExit(f"[NO-OP] {mid} in composite {label}: 변이 무효 — 관측 폐기")
        tp.write_text(mutated, encoding="utf-8", newline="")

    pytest_res = run_pytest_face(run_dir)
    runtime_res = run_runtime_face(run_dir)
    w13_res = run_w13_face(fixdir)

    result = {
        "composite": label,
        "applied": mids,
        "pytest_face": {k: v for k, v in pytest_res.items() if k != "raw"},
        "runtime_face": runtime_res,
        "w13_face": {k: v for k, v in w13_res.items() if k != "raw"},
        "run_dir": str(run_dir),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"COMPOSITE_{label.replace('+', '_plus_')}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return result


def run_composite_registered(label: str) -> Dict[str, object]:
    """COMPOSITES 로스터에 등재된 복합 mutant 를 실행.

    COMPOSITES[label] = ([실제 mutant ID], 복합변이함수, 기대값)
    """
    if label not in COMPOSITES:
        raise SystemExit(f"unknown composite: {label}")

    mids, fn, expected = COMPOSITES[label]
    run_dir = build_run_tree(label.replace("+", "_plus_"))
    fixdir = run_dir / "tests" / "fixtures" / "cfp2978"

    # 복합 변이 함수 사용 (M-13i + M-13k 등 동시 적용)
    target, _, _ = MUTANTS[mids[0]]  # 첫 번째 mutant의 target 사용
    tp = (run_dir / target) if ("/" in target or target.startswith(".")) \
        else (fixdir / target)
    src = tp.read_text(encoding="utf-8")
    mutated = fn(src)
    if mutated == src:
        raise SystemExit(f"[NO-OP] {label}: 변이 무효 — 관측 폐기")
    tp.write_text(mutated, encoding="utf-8", newline="")

    pytest_res = run_pytest_face(run_dir)
    runtime_res = run_runtime_face(run_dir)
    w13_res = run_w13_face(fixdir)

    result = {
        "composite": label,
        "composed_from": mids,
        "expected": expected,
        "pytest_face": {k: v for k, v in pytest_res.items() if k != "raw"},
        "runtime_face": runtime_res,
        "w13_face": {k: v for k, v in w13_res.items() if k != "raw"},
        "run_dir": str(run_dir),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"COMPOSITE_{label.replace('+', '_plus_')}.pytest.txt").write_text(
        pytest_res["raw"], encoding="utf-8")
    (LOG_DIR / f"COMPOSITE_{label.replace('+', '_plus_')}.json").write_text(
        json.dumps({**result, "w13_raw": w13_res["raw"]}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return result


def baseline() -> Dict[str, object]:
    """변이 0 기준선 — 네 면 모두 GREEN 이어야 관측이 성립한다."""
    run_dir = build_run_tree("_baseline")
    fixdir = run_dir / "tests" / "fixtures" / "cfp2978"
    p = run_pytest_face(run_dir)
    w = run_w13_face(fixdir)
    s = run_straw_face(fixdir)
    rt = run_runtime_face(run_dir)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "_baseline.pytest.txt").write_text(p["raw"], encoding="utf-8")
    (LOG_DIR / "_baseline.json").write_text(
        json.dumps({"pytest": {k: v for k, v in p.items() if k != "raw"},
                    "w13": w, "straw": s, "runtime": rt}, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return {"pytest": {k: v for k, v in p.items() if k != "raw"}, "w13": w, "straw": s, "runtime": rt}


def selfcheck_anchors() -> int:
    """★ 앵커 정합 전수 자기검사 (2026-08-19 신설).

    왜 필요한가 — 이 하네스의 앵커는 `.github/workflows/parallel-work-sentinel-check.yml`
    문면 **리터럴**이라 그 파일이 편집되면 조용히 죽는다. `_replace_once` 는
    fail-closed 라 「조용히 GREEN」은 아니지만, **그 mutant 를 실제로 돌릴 때까지
    아무도 모른다** — 즉 결함의 발견이 우연에 달려 있다.
    2026-08-19 실측: W-3b(파일목록 4→5) · W-3b-1(로스터 6→12) · W-3d(V1b) 착지로
    wrapper workflow 대상 mutant 다수 + COMPOSITES 2종이 동시에 ANCHOR-MISS 였다.

    ⇒ 한 명령으로 **전수** 확인한다. 판정 = **미적중 이름 집합이 공집합**
      (개수 assert 금지 — 일반 규칙 ①: 카디널리티 형 금지, 이름 집합으로 판정).

    사용:  python tests/scripts/cfp2978-mutant-lab/mutant_harness.py --selfcheck
           exit 0 = 전건 적중 / exit 1 = 미적중 이름 나열
    ★ `.github/workflows/**` 편집 직후 · 핀 채취 직전에 돌릴 것.
    """
    faces = {
        "live": REPO_ROOT / ".github" / "workflows" / "parallel-work-sentinel-check.yml",
        "twin": REPO_ROOT / "templates" / "github-workflows" / "parallel-work-sentinel-check.yml",
    }
    rc = 0
    for face_name, path in faces.items():
        if not path.exists():
            print(f"[{face_name}] MISSING FILE: {path}")
            rc = 1
            continue
        text = path.read_text(encoding="utf-8")
        miss = []
        for mid, (target, fn, _e) in MUTANTS.items():
            if not target.endswith("parallel-work-sentinel-check.yml"):
                continue
            try:
                fn(text)
            except BaseException:  # noqa: BLE001 — _replace_once 는 SystemExit 을 던진다
                miss.append(mid)
        for label, (_mids, fn, _e) in COMPOSITES.items():
            try:
                fn(text)
            except BaseException:  # noqa: BLE001
                miss.append(f"COMPOSITE:{label}")
        print(f"[{face_name}] ANCHOR-MISS 이름집합 = {sorted(miss)}")
        if miss:
            rc = 1
    a, b = faces["live"], faces["twin"]
    if a.exists() and b.exists():
        parity = a.read_text(encoding="utf-8") == b.read_text(encoding="utf-8")
        print(f"[byte-parity] live == templates twin : {parity}")
        if not parity:
            rc = 1
    if rc:
        print("\n★ 미적중 발생 — 앵커 상수(J2_PYTEST_FILES / J2_COLLECT_ROSTER /"
              " A_J2_RUNPYTEST_* / A_J2_COLLECT)를 현행 job2 문면으로 재동기화할 것."
              " 흩어진 리터럴이 아니라 **그 블록 한 곳만** 고치면 된다.")
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true",
                    help="앵커 정합 전수 자기검사 (미적중 이름 집합 공집합 판정)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--run", nargs="*", default=None)
    ap.add_argument("--run-all", action="store_true")
    # ★중첩 변이 — rc 흡수의 판별은 대조(delta 소멸)에서만 선다 (§8.B 처방 3).
    ap.add_argument("--compose", nargs="+", default=None,
                    metavar="MID",
                    help="여러 mutant 를 한 run tree 에 겹쳐 적용 후 런타임 면 측정 "
                         "(예: --compose M-13h M-13a)")
    ap.add_argument("--run-all-composites", action="store_true",
                    help="COMPOSITES 로스터의 모든 복합 mutant 실행")
    a = ap.parse_args()

    if a.selfcheck:
        return selfcheck_anchors()
    if a.list:
        for k, (t, _, e) in MUTANTS.items():
            print(f"{k:16} target={t:24} expected={e}")
        print("\n=== COMPOSITES ===")
        for label, (mids, _, e) in COMPOSITES.items():
            print(f"{label:16} composed_from={'+'.join(mids):16} expected={e}")
        return 0
    if a.baseline:
        print(json.dumps(baseline(), ensure_ascii=False, indent=2, default=str))
        return 0
    if a.compose:
        print(json.dumps(run_composite(a.compose), ensure_ascii=False, indent=2, default=str))
        return 0
    if a.run_all_composites:
        out = []
        for label in COMPOSITES:
            r = run_composite_registered(label)
            out.append(r)
            print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
            print("-" * 78)
        (LOG_DIR / "composites_summary.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return 0

    ids = list(MUTANTS) if a.run_all else (a.run or [])
    # 결함 C: 무인자 호출 가드 — summary.json 무손상 유지
    if not ids:
        ap.print_usage()
        return 1
    out = []
    for mid in ids:
        if mid not in MUTANTS:
            raise SystemExit(f"unknown mutant: {mid}")
        r = run_one(mid)
        out.append(r)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        print("-" * 78)
    # ★ 결함 C-2 (2026-08-19 신설) — **부분 실행이 전수 로스터 산출을 파괴하지 않는다**.
    #   구 문면은 `--run <일부>` 도 `summary.json` 을 통째로 덮어썼다. 실사고:
    #   `--run` 4종 실행 1회로 35-entry 전수 산출이 4-entry 로 소실됐다 (본 커밋에서
    #   immutable ref `c54550f01` 로부터 복원). 「무인자 가드」(결함 C)는 인자가
    #   **0개**인 경우만 막았고, **부분 집합**인 경우가 여집합으로 남아 있었다 —
    #   이 Story 가 반복해 맞은 *"가드의 정의역이 위험의 정의역보다 좁다"* 형태.
    #   ⇒ `summary.json` 은 **전수 실행(--run-all)일 때만** 기록하고, 부분 실행은
    #     `summary.partial.json` 으로 분리한다.
    if a.run_all:
        (LOG_DIR / "summary.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    else:
        (LOG_DIR / "summary.partial.json").write_text(
            json.dumps({"note": "부분 실행 산출 — 전수 로스터 산출(summary.json) 아님",
                        "ran": ids, "results": out},
                       ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(f"[partial] {len(ids)} mutant 실행 — summary.partial.json 기록 "
              f"(summary.json 무접촉: 전수 산출 보존)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
