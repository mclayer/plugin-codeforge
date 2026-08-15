#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/scripts/test_cfp2984_ac_named_tests.py — CFP-2984 §8.1 RTM 명명 테스트 심볼 모듈.

★ 왜 이 파일이 필요한가 (실측 근거, 추정 아님)
  required 게이트 `ac-traceability-matrix` 의 Hop3 는 명명 테스트가 **Python `ast` 심볼로 실재**하는지
  본다 — `scripts/lib/check_ac_traceability_matrix.py:_collect_symbols_one_root` 는 `*.py` 만 walk 해
  `ast.FunctionDef/AsyncFunctionDef/ClassDef` node 이름만 수집한다. **bash 함수는 보이지 않고**, 주석·
  문자열 매칭도 아니다(grep 아님). 따라서 §8.1 RTM 의 bare 식별자(`test_stall_predicate` 등)가 `def` 로
  실재하지 않으면 `hop3_born_missing` 이 required 게이트를 FAIL 시킨다.

★ 계층 분업 (두 벌 중복이 아니다)
  - `tests/scripts/test_<name>.sh` = **실 self-test**(bash, 순수 픽스처). AC 판별력의 SSOT 이며
    required job `invariant-check` 의 corpus step 이 25본을 명시 열거로 실행한다.
  - 본 `.py` = **심볼 제공 + 실행 위임**. 각 명명 식별자를 `def` 로 정의하고 본문에서 대응 `.sh` 를
    subprocess 로 **실제 실행**해 `rc == 0` 을 assert 한다. 스텁(`pass`) 금지 — 스텁도 Hop3 는
    통과시키지만(F-STUB confess) 그것은 정확히 본 Story 가 겨냥하는 "존재 != 실행" 이다.
  - 선례: CFP-2884 는 반대 방향(`.sh` wrapper → `.py` pytest 위임)을 이미 사용한다.

★ ADR-151 bijection 정의역 밖
  메타-게이트 `_check_corpus` 는 `tests/scripts/*.sh` 만 대조한다(`tests_dir.glob("*.sh")`). `.py` 는
  정의역 밖이라 인벤토리 등재 대상이 아니며, 등재하면 오히려 `record→missing file` 로 exit 1 이 된다
  (기존 `conftest.py` · `test_ac_traceability_matrix.py` 선례 동일).

★ 정직 천장 (over-claim 금지 — 숨기지 않고 적는다)
  (i) 본 모듈이 **required tier 에서 소비되는 방식은 `ast` 정적 파싱**이다(매 PR, `ac-traceability-matrix`).
      즉 파일 자체는 dead 가 아니지만, 그 소비는 심볼 존재 확인까지다.
  (ii) 함수 **본문의 실 실행**(pytest run)을 수행하는 workflow step 은 현재 **0 건**이다. AC 판별력의
      실행 보장은 `.sh` 쪽 채널(required `invariant-check` corpus step)이 진다. 본 모듈을 실행 채널로도
      닫으려면 `ac-traceability-self-test.yml`(non-required, Hop3 명명 suite 4종의 기존 홈)에
      `python3 -m pytest tests/scripts/test_cfp2984_ac_named_tests.py -q` 1 step 추가로 충분하나,
      그 파일은 본 작업 단위의 배선 소유 밖이라 **DevPL 경유 회부**한다. 이 문단을 지우고 "실행된다" 로
      바꿔 쓰는 것이 곧 over-claim 이다.
  (iii) 여기서 `rc == 0` 이 참이라는 것은 해당 `.sh` 가 자기 오라클을 통과했다는 뜻이지, 그 오라클이
      discriminating 하다는 뜻이 아니다(검출력 = G3 축, mutant 원장 소관).

Exit 계약: 각 테스트는 대상 `.sh` 의 REAL exit code 를 판정한다. 대상 부재·bash 부재는 **skip 이 아니라
FAIL**(fail-closed — 판정불가를 성공으로 접지 않는다; pytest.ini 의 "skip 금지" 규율 동형).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests" / "scripts"
INVENTORY = REPO_ROOT / "docs" / "selftest-execution-liveness-inventory.yaml"
META_GATE = REPO_ROOT / "scripts" / "check-selftest-execution-liveness.sh"

# 본 Story 가 신설한 self-test corpus (N = 25 = Change Plan §8.1 AC-12 측정식 산출값).
# 이 튜플이 모듈 내 단일 정본 — 아래 delegating 함수의 리터럴은 `_run_sh` 가 멤버십으로 검증한다
# (리터럴 오타 = 즉시 FAIL, 조용한 no-op 방지).
CFP2984_CORPUS = (
    "test_check-salvage-bundle.sh",
    "test_salvage_side_effect_dedup.sh",
    "test_bundle_field_allowlist.sh",
    "test_salvage_no_retry_reapply.sh",
    "test_bundle_pre_push_redaction.sh",
    "test_nontest_script_execution_liveness.sh",
    "test_retry_after_derivation.sh",
    "test_retry_layer_overlap.sh",
    "test_retry_ladder_no_dead_step.sh",
    "test_native_multiplier_stance.sh",
    "test_wait_source_header_class.sh",
    "test_intensity_branch_no_silent_zero.sh",
    "test_stall_predicate.sh",
    "test_termination_record_query.sh",
    "test_ledger_freshness_guard.sh",
    "test_split_plan_structure.sh",
    "test_failure_class_coverage_set.sh",
    "test_recovery_procedure_class_coverage.sh",
    "test_incomplete_state_preservation_path.sh",
    "test_declared_count_vs_actual.sh",
    "test_declared_tier_vs_actual.sh",
    "test_declared_field_consumer_class.sh",
    "test_event_channel_resolution.sh",
    "test_detection_surface_scope.sh",
    "test_external_observer_visibility.sh",
)

# 기존재 자산 (AC-12a — 본 Story 신설분 아님, 개명 불가·타 소유).
PREEXISTING = ("test_check-selftest-execution-liveness.sh",)

EXPECTED_CHANNEL = "workflow:invariant-check.yml:invariant-check"

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

    - basename 은 CFP2984_CORPUS ∪ PREEXISTING 멤버여야 한다(리터럴 오타 가드).
    - 파일 부재 = FAIL (skip 아님). corpus 파일 부재는 ADR-151 bijection 에서도 exit 1 이다.
    - 실패 시 stdout/stderr tail 을 assertion 메시지에 실어 진단을 남긴다.
    """
    if basename not in CFP2984_CORPUS and basename not in PREEXISTING:
        pytest.fail(
            f"'{basename}' 는 선언된 corpus 밖 — 함수 리터럴과 CFP2984_CORPUS 정본이 어긋났다"
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


def _load_inventory_records():
    """인벤토리 레코드 목록. PyYAML 부재·파싱 실패 = FAIL (판정불가 fail-closed)."""
    try:
        import yaml
    except ImportError:
        pytest.fail("PyYAML 부재 — 인벤토리 등재 판정불가(fail-closed). `pip install pyyaml`.")
    if not INVENTORY.is_file():
        pytest.fail(f"{INVENTORY} 부재 — 등재 판정불가(fail-closed).")
    with open(INVENTORY, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    recs = (doc or {}).get("self_tests")
    assert isinstance(recs, list), "인벤토리 최상위 'self_tests' (list) 부재/형식 오류."
    return [r for r in recs if isinstance(r, dict)]


# ═══════════════════════════════════════════════════════════════════════════════
# §8.1 RTM 명명 테스트 — 25본 위임 (심볼 = Hop3 정의역 / 본문 = REAL 실행)
# ═══════════════════════════════════════════════════════════════════════════════


def test_check_salvage_bundle():
    """AC-1 / AC-2 / AC-4 — 번들 스키마 하한·손상 조각 태깅·실패 경로 종료코드."""
    _run_sh("test_check-salvage-bundle.sh")


def test_salvage_side_effect_dedup():
    """AC-3 — side-effect 원장 row 스키마 닫힘성 + 정규화 키 dedup(INV-T8)."""
    _run_sh("test_salvage_side_effect_dedup.sh")


def test_bundle_field_allowlist():
    """AC-31 — 번들 필드 allowlist 차집합 + 값 형태 술어(wip_summary 예외)."""
    _run_sh("test_bundle_field_allowlist.sh")


def test_salvage_no_retry_reapply():
    """AC-33 — salvage 경로 재시도 발행 0(INV-T6, 무한후퇴 차단)."""
    _run_sh("test_salvage_no_retry_reapply.sh")


def test_bundle_pre_push_redaction():
    """AC-32 — 착지 객체 그래프 전수 스캔(중간 커밋 secret 포함) + redact 엔진 재사용."""
    _run_sh("test_bundle_pre_push_redaction.sh")


def test_nontest_script_execution_liveness():
    """AC-12b — bijection 정의역 밖 스크립트의 실행 채널 부재 차단."""
    _run_sh("test_nontest_script_execution_liveness.sh")


def test_retry_after_derivation():
    """AC-5a — 상대초 헤더 vs 절대시각 헤더의 대기시간 유도 정합."""
    _run_sh("test_retry_after_derivation.sh")


def test_retry_layer_overlap():
    """AC-5c — 층 통합 레지스트리 중첩 + 역방향 4 leg(오라벨 우회 봉쇄)."""
    _run_sh("test_retry_layer_overlap.sh")


def test_retry_ladder_no_dead_step():
    """AC-23 — 사다리 slot 해소 실패 0건(slot frozen / tenant 교체)."""
    _run_sh("test_retry_ladder_no_dead_step.sh")


def test_native_multiplier_stance():
    """AC-5b — 네이티브 승수 한정어 보존 + 대기 총합 < idle-timeout 형식."""
    _run_sh("test_native_multiplier_stance.sh")


def test_wait_source_header_class():
    """AC-30 — 대기 출처 헤더 클래스 구분(절대 vs 상대) 보존."""
    _run_sh("test_wait_source_header_class.sh")


def test_intensity_branch_no_silent_zero():
    """AC-24 — 데이터원 부재를 조용한 0 으로 접지 않고 명시 보고."""
    _run_sh("test_intensity_branch_no_silent_zero.sh")


def test_stall_predicate():
    """AC-8 / AC-9 — stall 2항 AND + 3-state 출력 + 진행신호 closed set."""
    _run_sh("test_stall_predicate.sh")


def test_termination_record_query():
    """AC-11 — 다중 clock-domain 정규화 단일 경로 + 채널 필드 매핑 테이블."""
    _run_sh("test_termination_record_query.sh")


def test_ledger_freshness_guard():
    """AC-11b — stale 2항 AND + 임계의 분포-함수 형식 강제."""
    _run_sh("test_ledger_freshness_guard.sh")


def test_split_plan_structure():
    """AC-7 — 컨텍스트 분할 계획의 구조 보존(구조→산문 등가변형 검출)."""
    _run_sh("test_split_plan_structure.sh")


def test_failure_class_coverage_set():
    """AC-25 — 실패 4-class closed set 의 SSOT 단일성."""
    _run_sh("test_failure_class_coverage_set.sh")


def test_recovery_procedure_class_coverage():
    """AC-27 — 회수 절차 4-class 커버리지(body + frontmatter description)."""
    _run_sh("test_recovery_procedure_class_coverage.sh")


def test_incomplete_state_preservation_path():
    """AC-28 — 회수 전 쓰기 동결 순서 불변식."""
    _run_sh("test_incomplete_state_preservation_path.sh")


def test_declared_count_vs_actual():
    """AC-6 — 선언 카운트 ↔ 파서 재계수 대조(자기 정의역 명시 포함)."""
    _run_sh("test_declared_count_vs_actual.sh")


def test_declared_tier_vs_actual():
    """AC-16 — 선언 tier ↔ 정본 3 leg(표 단위 앵커링)."""
    _run_sh("test_declared_tier_vs_actual.sh")


def test_declared_field_consumer_class():
    """AC-26 — 선언 필드의 소비자 class 3값 분류 기록."""
    _run_sh("test_declared_field_consumer_class.sh")


def test_event_channel_resolution():
    """AC-14 — 질문 ↔ 원장 채널 매핑 해석(오귀속 검출)."""
    _run_sh("test_event_channel_resolution.sh")


def test_detection_surface_scope():
    """AC-15 — 감지기 정의역 한정(INV-T7) + recovery 되먹임 공집합(INV-I0)."""
    _run_sh("test_detection_surface_scope.sh")


def test_external_observer_visibility():
    """AC-29 — 수집 0 사실·사유 가시화(exit code 무접촉 + 3제약)."""
    _run_sh("test_external_observer_visibility.sh")


# ═══════════════════════════════════════════════════════════════════════════════
# AC-12 / AC-12a — 등재 자체와 메타-게이트 자기 검증
# ═══════════════════════════════════════════════════════════════════════════════


def test_selftest_inventory_registration():
    """AC-12 — 신설 25본이 ADR-151 인벤토리에 전건 등재됐는가 (배선 채널·tier 포함).

    메타-게이트 자체는 재사용하고(재발명 0), 그 위에 **본 Story 의 25본** 이라는 좁은 정의역을
    직접 대조한다. 메타-게이트만 돌리면 "전체가 bijection 이다" 까지만 알 수 있어, 25본이 다른
    채널·다른 tier 로 등재된 경우를 못 잡는다.
    """
    records = _load_inventory_records()
    by_name = {}
    for rec in records:
        st = rec.get("self_test")
        if isinstance(st, str):
            by_name.setdefault(st.replace("\\", "/"), []).append(rec)

    missing = [n for n in CFP2984_CORPUS if f"tests/scripts/{n}" not in by_name]
    assert not missing, (
        f"인벤토리 미등재 {len(missing)}본: {missing}. ADR-151 bijection 은 양방향 전칭이라 "
        f"미등재 1본도 `missing file→record` 로 exit 1 이다(등재는 선택이 아니라 강제)."
    )

    dup = [n for n in CFP2984_CORPUS if len(by_name[f"tests/scripts/{n}"]) > 1]
    assert not dup, f"self-test 당 정확히 1 레코드 위반(중복): {dup}"

    bad_channel, bad_status, bad_tier, empty_gbc = [], [], [], []
    for n in CFP2984_CORPUS:
        rec = by_name[f"tests/scripts/{n}"][0]
        if rec.get("execution_channel") != EXPECTED_CHANNEL:
            bad_channel.append((n, rec.get("execution_channel")))
        if rec.get("channel_status") != "alive":
            bad_status.append((n, rec.get("channel_status")))
        if rec.get("blocking_tier") != "required":
            bad_tier.append((n, rec.get("blocking_tier")))
        gbc = rec.get("g_boundary_check")
        if not isinstance(gbc, str) or not gbc.strip():
            empty_gbc.append(n)
    assert not bad_channel, f"실행 채널이 {EXPECTED_CHANNEL} 아님: {bad_channel}"
    assert not bad_status, f"channel_status alive 아님: {bad_status}"
    assert not bad_tier, f"blocking_tier required 아님(required job 배선인데 tier 미표기): {bad_tier}"
    assert not empty_gbc, f"g_boundary_check 공백: {empty_gbc}"

    # 메타-게이트 REAL 실행 — bijection(양방향) + AC-2 배선 실재까지 위임 검증.
    if not META_GATE.is_file():
        pytest.fail(f"{META_GATE} 부재 — 메타-게이트 위임 판정불가(fail-closed).")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [_bash(), str(META_GATE), "--repo-root", str(REPO_ROOT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=_SH_TIMEOUT_SEC,
        env=env,
    )
    tail = "\n".join(((proc.stdout or "") + (proc.stderr or "")).splitlines()[-30:])
    assert proc.returncode == 0, (
        f"check-selftest-execution-liveness.sh REAL exit {proc.returncode} (기대 0)\n{tail}"
    )


def test_check_selftest_execution_liveness():
    """AC-12a — 메타-게이트 재귀 L3 self-test(기존 자산) 실행.

    파일명에 하이픈이 있어 게이트 식별자 정규식으로는 명명 불가하고 타 소유라 개명도 불가하므로,
    본 심볼이 그 실행을 위임한다(§8.1 RTM AC-12a 행).
    """
    _run_sh("test_check-selftest-execution-liveness.sh")


if __name__ == "__main__":  # 직접 실행 시 pytest 위임 (수동 진단용).
    sys.exit(pytest.main([__file__, "-q"]))
