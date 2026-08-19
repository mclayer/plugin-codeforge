#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/scripts/test_cfp2995_ac_named_tests.py — CFP-2995 §8.1.1 RTM 명명 테스트 심볼 모듈.

★ 왜 이 파일이 필요한가 (실측 근거, 추정 아님)
  required 게이트 `ac-traceability-matrix` 의 Hop3 는 명명 테스트가 **Python `ast` 심볼로 실재**하는지
  본다 — `scripts/lib/check_ac_traceability_matrix.py:_collect_symbols_one_root` (`:515`-`:532`) 는
  `os.walk` 중 `if not name.endswith(".py"): continue` 후 `ast.FunctionDef/AsyncFunctionDef/ClassDef`
  **node 이름만** 수집한다. **bash 함수는 비가시**이고 grep 도 문자열 매칭도 아니다. 따라서 §8.1.1 RTM
  의 bare 식별자가 `def` 로 실재하지 않으면 `hop3_born_missing` 이 required 게이트를 FAIL 시킨다.
  Hop2 는 Phase 1+2 양쪽에서 돌고 `tier == "normative"` 면 phase 무관하게 명명 테스트를 요구하므로
  (`check_ac_traceability_matrix.py:455`), `rtm_uri` 가 붙는 순간 **17 전건**이 걸린다.

★ 계층 분업 (두 벌 중복이 아니다 — Change Plan §3.7)
  - `tests/scripts/*.sh` = **실 self-test**(bash, 순수 픽스처). AC 판별력의 SSOT 이며 required job
    `invariant-check` 의 corpus step 이 **명시 열거**(glob 금지)로 실행한다.
  - 본 `.py` = **심볼 제공 + 실행 위임**. 각 명명 식별자를 `def` 로 정의하고 본문에서 대응 `.sh` 를
    subprocess 로 **실제 실행**해 `rc == 0` 을 assert 한다.
  - **스텁(`pass`) 금지** — 스텁도 Hop3 는 통과시키지만 그것이 정확히 본 Story 가 겨냥하는
    «존재 != 실행» 이다. 선례(`test_cfp2984_ac_named_tests.py`)가 같은 금지를 명문화한다.

★ ADR-151 bijection 정의역 밖 — **인벤토리 등재 금지**
  메타-게이트 `_check_corpus` 는 `tests_dir.glob("*.sh")` (`:354`) 만 대조한다. `.py` 는 정의역 밖이라
  인벤토리 등재 대상이 아니며, **등재하면 오히려 `record→missing file` 로 exit 1** 이 된다(`:379`).
  기존 `conftest.py` · `test_ac_traceability_matrix.py` · `test_cfp2984_ac_named_tests.py` 선례 동일.

★ 정직 천장 (over-claim 금지 — 숨기지 않고 적는다. Change Plan §3.7 H-1/H-2/H-3)
  (H-1) **목적 = 심볼 제공이지 실행이 아니다.** 본 모듈의 존재 이유는 Hop3(`ac-traceability-matrix`)가
      `ast` 로 읽을 **Python 심볼 제공**이다. 실행 채널을 더하는 것이 목적이 아니다.
  (H-2) **소비는 `ast` 정적 파싱까지다.** required tier 에서의 소비 방식은 매 PR `ast` 정적 파싱이며
      **심볼 존재 확인까지**다. 파일이 dead 는 아니나 그 소비는 거기서 멈춘다.
  (H-3) **본문 실행 workflow 0건 = 미착수가 아니라 의도된 결정이다.** 각 함수는 대응 `.sh` 를
      subprocess 로 돌려 rc=0 을 assert 하는데, 그 `.sh` 는 이미 required `invariant-check` corpus
      step 이 **직접** 실행한다 ⇒ pytest 채널을 더하면 **같은 `.sh` 를 두 번 돌릴 뿐 새로 검증되는
      것이 없다**(러너 시간만 2배).
      ★ **잔여(정직 declare): 그 대가로 본 모듈의 본문은 어떤 채널에서도 실행되지 않는다.** 경로가
      틀어지거나 assert 가 항진식으로 썩어도 아무도 잡지 못한다 — **심볼 존재 ≠ 본문 실행**.
      이 잔여를 "실행된다" 로 바꿔 쓰는 것이 곧 over-claim 이다.
  (H-4) `rc == 0` 이 참이라는 것은 해당 `.sh` 가 자기 오라클을 통과했다는 뜻이지, 그 오라클이
      discriminating 하다는 뜻이 아니다(검출력은 mutant 원장 소관).

★★ 선례 대비 **신규 잔여 1건 — 위임 입도**(본 Story 고유, 침묵 금지. Change Plan §3.7 말미)
  선례 CFP-2984 는 **25 `def` ↔ 25 `.sh` 1:1** 이었으나 본 모듈은 **17 `def` ↔ 2 `.sh`** 다.
  ⇒ 위임 입도가 **파일 단위이지 케이스 단위가 아니다** — 한 `def` 의 `rc == 0` 은 그 `.sh` **전체**가
  통과했다는 뜻이고 **해당 AC 의 케이스만 통과했다는 뜻이 아니다.** 같은 `.sh` 에 위임하는 형제
  `def` 들은 서로 구별되지 않는 판정을 반환한다(11 개가 한 파일, 6 개가 다른 한 파일).
  케이스 필터를 신설하지 **않는다** — 본문이 어떤 채널에서도 실행되지 않으므로(H-3) 필터가 사는
  이득이 0 이며 3문 게이트 미충족이다. 미래 Story 가 pytest 실행을 배선하면 이 입도 격차가
  **실재하게 된다**. 그때 닫아야 할 자리를 여기 적어 둔다.

★ declared 5건은 본 모듈 정의역 밖 — AC-11 · AC-15 · AC-16 · AC-18 · AC-22 는 기계 판정면이 없고
  문면 리뷰로 판정한다(§8.1.1). 심볼을 만들면 «존재 != 실행» 을 한 겹 더 쌓을 뿐이다.

Exit 계약: 각 테스트는 대상 `.sh` 의 REAL exit code 를 판정한다. 대상 부재·bash 부재는 **skip 이 아니라
FAIL**(fail-closed — 판정불가를 성공으로 접지 않는다). 이 규율은 본 Story 의 주제 그 자체다:
「봐야 하는데 못 봤다」를 「볼 것이 없었다」로 접으면 그것이 곧 silent-zero 다.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests" / "scripts"

# 본 Story 가 확장하는 self-test 2본 (§8.1 커버리지 표 — 신규 `.sh` 0, §9.8 판정).
#   이 튜플이 모듈 내 단일 정본 — 아래 delegating 함수의 리터럴은 `_run_sh` 가 멤버십으로 검증한다
#   (리터럴 오타 = 즉시 FAIL, 조용한 no-op 방지).
CFP2995_CORPUS = (
    "test_external_observer_visibility.sh",   # AC-1·2·3·4·5·19  (watchdog 생산자 축)
    "test_bundle_pre_push_redaction.sh",      # AC-6·7·8·9·10·12·13·14·17·20·21 (salvage·ADR-179·범위경계)
)

_SH_TIMEOUT_SEC = 600


def _bash():
    """bash 실행 파일 경로. 부재 = 판정불가 = FAIL (skip 금지)."""
    exe = shutil.which("bash")
    if not exe:
        pytest.fail(
            "bash 부재 — self-test 위임 실행 판정불가(fail-closed). "
            "skip 하면 '실행 안 됐는데 green' 이 되므로 FAIL 로 처리한다."
        )
    return exe


def _run_sh(basename):
    """`tests/scripts/<basename>` 를 REAL 실행하고 rc == 0 을 assert.

    - basename 은 CFP2995_CORPUS 멤버여야 한다(리터럴 오타 가드).
    - 파일 부재 = FAIL (skip 아님). corpus 파일 부재는 ADR-151 bijection 에서도 exit 1 이다.
    - 실패 시 stdout/stderr tail 을 assertion 메시지에 실어 진단을 남긴다.
    """
    if basename not in CFP2995_CORPUS:
        pytest.fail(
            f"'{basename}' 는 선언된 corpus 밖 — 함수 리터럴과 CFP2995_CORPUS 정본이 어긋났다"
            f"(드리프트 가드)."
        )
    path = TESTS_DIR / basename
    if not path.is_file():
        pytest.fail(
            f"{path} 부재 — 명명 테스트의 실 self-test 가 없다(존재 != 실행 이전에 존재부터 결손). "
            f"ADR-151 bijection 에서도 record→missing file 로 exit 1."
        )
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run(
            [_bash(), str(path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_SH_TIMEOUT_SEC,
            env=env,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"{basename}: {_SH_TIMEOUT_SEC}s 초과 — hang(판정불가) = FAIL.")
    tail = "\n".join((proc.stdout or "").splitlines()[-25:])
    err = "\n".join((proc.stderr or "").splitlines()[-25:])
    assert proc.returncode == 0, (
        f"{basename}: REAL exit {proc.returncode} (기대 0)\n"
        f"--- stdout tail ---\n{tail}\n--- stderr tail ---\n{err}"
    )
    return proc


# ═══════════════════════════════════════════════════════════════════════════════
# §8.1.1 RTM 명명 테스트 — normative 17 위임
#   심볼 = Hop3 정의역 / 본문 = REAL 실행 (스텁 0)
#   ★ 입도 잔여: 아래 17 `def` 는 2 개의 `.sh` 로 위임한다 — 파일 단위이지 케이스 단위가 아니다
#     (모듈 docstring «신규 잔여 1건» 참조). 형제 `def` 들은 구별되지 않는 판정을 반환한다.
# ═══════════════════════════════════════════════════════════════════════════════

# ── watchdog 생산자 축 → test_external_observer_visibility.sh (6본) ──────────────


def test_watchdog_http_error_not_silent_zero():
    """AC-1 — HTTP 오류 코드가 exit code 를 건드리지 않는 witness 로 관측돼 영점으로 접히지 않는다."""
    _run_sh("test_external_observer_visibility.sh")


def test_watchdog_count_completeness_signalled():
    """AC-2 — 수집 완전성 결손 3 갈래(혼합 배열 · 산출 실패 · 페이지네이션 truncation)가 각자 사유를 방출."""
    _run_sh("test_external_observer_visibility.sh")


def test_watchdog_genuine_zero_preserved():
    """AC-3 — 역방향 보호: 200 + 빈 배열은 `(ok, 0, none)` 을 그대로 방출한다."""
    _run_sh("test_external_observer_visibility.sh")


def test_watchdog_exit_contract_unchanged():
    """AC-4 — 종료문 · 비차단 설정 · 분기별 출력 키 3 정의역이 착지 전 불변 리비전과 원소 단위로 동일."""
    _run_sh("test_external_observer_visibility.sh")


def test_watchdog_failure_class_resolution():
    """AC-5 — `unobserved_reason` 값 공간이 실패 class 를 구체 사유로 해상한다(뭉갬 0)."""
    _run_sh("test_external_observer_visibility.sh")


def test_watchdog_curl_stderr_preserved():
    """AC-19 — transport 실패 시 curl stderr 와 parse 진단이 폐기되지 않는다(침묵 3축)."""
    _run_sh("test_external_observer_visibility.sh")


# ── salvage 가드·좁히기·ADR-179 사이트·범위 경계 축 →
#    test_bundle_pre_push_redaction.sh (11본) ────────────────────────────────────


def test_scan_blob_line_cap_isolated():
    """AC-6 — `LINE_CAP` 단독 트립(나머지 2 상한은 도달 불가로 고정)."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_scan_blob_parse_timeout_injected():
    """AC-7 — `PARSE_TIMEOUT_S` 포화 가드 발동을 결정론적 주입으로 실증 + 호출 witness >= 1."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_scan_blob_undecidable_control():
    """AC-8 — 판정 불가 대조군: 포화가 통과가 아니라 `undecidable` 로 접힌다."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_scan_blob_guard_mutants_killed():
    """AC-9 — 각 가드를 무조건 통과로 뒤집는 변이가 RED(차분 판정, 절대 상태 금지)."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_rule_regex_narrowing_mutant_killed():
    """AC-10 — 탐지기 정규식 좁히기 변이가 잡힌다(교차 오염 방지: 대상 룰 격리 단언)."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_rule_definitions_unchanged():
    """AC-12 — 동결 2 파일 내용 전체 + 차단룰 집합 + 탐지기 정규식 리터럴이 착지 전과 동일."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_adr179_jwt_sites_consistent():
    """AC-13 — ADR-179 F-12 정정 4 사이트가 재위치 앵커로 식별되고 각자 탐지 여부를 진술한다."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_adr179_jwt_claim_matches_execution():
    """AC-14 — 정정문의 함의가 D1(bare 11) ∪ D2(문맥 래핑 6) 전건에서 실 탐지기 실행과 일치."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_cfp2995_scope_boundary():
    """AC-17 — 인접 Story 소유 표면·접근 금지 목록 변경 0 + 판별기 판별력(내부 1건 / 외부 0건)."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_heldout_witness_not_copied_from_impl():
    """AC-20 — held-out 증인이 구현에서 복사되지 않았음(내부-순환 conjunct 정의역 제외)."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_threshold_conjunct_boundary_pairs():
    """AC-21 — 임계 conjunct 경계쌍(길이·엔트로피 하한 전후)이 각각 판정을 가른다."""
    _run_sh("test_bundle_pre_push_redaction.sh")
