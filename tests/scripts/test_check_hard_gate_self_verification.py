#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
CFP-2684 / ADR-154 — hard-gate-self-verification 메타-게이트 execution-backed RTM self-test (.py).

왜 이 파일이 존재하는가 (ac-traceability Hop3 born-missing 해소):
  wrapper-self ac-traceability 게이트 Hop3 는 `tests-root` 아래 **`*.py` 를 ast 파싱**
  (`collect_test_symbols` — grep 아님)해 Change Plan §8 RTM 의 명명 테스트를 실 symbol 로 resolve
  한다. 본 메타-게이트의 재귀 self-test 는 `.sh`(AC-7 two-meta-gate cross-seal 위해 ADR-151
  `.sh`-glob 인벤토리 enroll 필수)라 shell function → ast 미resolve → §8 normative AC 10개가
  born-missing(Hop3 FAIL) 된다. §5 에 normative AC 10개라 ac_applicability:none 은 anti-hollow
  guard 가 거부(none-위장). → **`.py` RTM 테스트가 필수**(CFP-2680 `.py` 선례 답습).

계약 (Change Plan §8.2.1 RTM, story@a5bfc521 §5.3 verbatim):
  coverage_required=yes normative AC 각각(AC-1/2/3/4/5/6/7/8/12/13)에 대해 **RTM 명명 테스트와
  정확히 같은 이름의 `def test_<name>(...)`** 함수를 둔다. Hop3 는 bare-name ast 매칭이므로
  함수명이 §8.2.1 백틱 인용 식별자와 1:1 일치해야 resolve 된다.

  AC-1  test_ac1_positive_control_present   positive-control anchor 보유→exit0 ↔ 부재→exit1
  AC-2  test_ac2_two_exit_shape             2-exit-differ shape→exit0 ↔ string-only→exit1
  AC-3  test_ac3_empty_target_failclosed    enrolled0 honest-degrade→exit0 ↔ unparseable subj→exit1
  AC-4  test_ac4_unknown_input_failclosed   valid repo-root→exit0 ↔ 미존재/비-dir→exit1
  AC-5  test_ac5_execution_trace_emit       green verdict stdout trace present ↔ M4 neutralize→소실
  AC-6  test_ac6_three_way_taxonomy_present 3-way + '결함 아님'→exit0 ↔ 토큰/예외 부재→exit1
  AC-7  test_ac7_self_application           TC-CLEAN-PASS + M1 positive-leak(자기 subject) + bijection
  AC-8  test_ac8_honest_ceiling_present     ceiling + presence≠truth + over-claim 부재→exit0 ↔ 부재→exit1
  AC-12 test_ac12_crossref_nodup           named≥6 + 3영역 + 재codify 부재→exit0 ↔ <6/재codify/영역누락→exit1
  AC-13 test_ac13_identity_probe           identity_bearing:true+probe→exit0 ↔ probe부재→exit1; 미선언=no-op

oracle 정직 (presence-grep/false-oracle 금지, ADR-119 §결정4·ADR-145 §결정5):
  각 함수 = REAL gate core(scripts/lib/check_hard_gate_self_verification.py)를 subprocess 로
  fixture 대상 실행 → **REAL exit code + REAL stderr AC-tag** 대조 pos/neg discriminating.
  present→exit0 이 absent/mutant→exit1 과 반드시 DIFFER(anti-theater). AC-5/AC-7 은 REAL gate copy
  를 sed 없이 문자열 치환 mutation(baseline↔mutant)으로 fail-closed 분기 load-bearing 을 실증
  (double-guard: anchor 미매칭→명시 FAIL(recipe drift, silent pass 금지) + mutated py_compile).

Windows-safe (직전 .sh /tmp→C:\tmp 아티팩트 교훈):
  - subprocess 는 `sys.executable` 로 gate core 직접 호출(bash wrapper path Windows 미해결 회피).
  - `text=True` 대신 `stdout/stderr=PIPE`(bytes) + `.decode('utf-8', errors='replace')` — non-UTF-8
    locale(cp949)에서 게이트 한글 UTF-8 출력 decode crash 회피.
  - fixture 는 pytest `tmp_path`(repo-root escape 0 → gate T-TRAVERSE resolve guard 통과).

정직 천장 (ADR-154 §결정4 / INV-5): 본 테스트는 presence/shape/format/fail-closed 까지만 실측한다.
  검출 sufficiency(L3)를 기계강제하지 않는다 — undecidable(review-tier, AC-9). presence ≠ truth.

인벤토리: ADR-151 selftest-execution-liveness 인벤토리는 `tests/scripts/*.sh` glob 이므로 본 `.py`
  는 미대상(CFP-2680 선례처럼 N/A — enroll 불필요, selftest-liveness 게이트 무영향).

`.sh` 무손상: 본 `.py` 는 `.sh`(AC-7 ADR-151 cross-seal 원본)를 실행/변경하지 않는다 — dual
  (Hop3 `.py`-ast resolve ∥ AC-7 `.sh` cross-seal). `.sh` 는 그대로 CI 에서 실행된다.
"""

import py_compile
import subprocess
import sys
from pathlib import Path

# tests/scripts/test_x.py → parents[0]=scripts, parents[1]=tests, parents[2]=repo-root.
REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_PY = REPO_ROOT / "scripts" / "lib" / "check_hard_gate_self_verification.py"
CONCEPT_REL = "docs/domain-knowledge/concept/hard-gate-self-verification.md"

# ── mutation anchors (real gate 에서 firsthand 확인 — recipe drift 시 명시 FAIL) ──
# M1 (AC-7 self-application): 자기 positive-control fail-closed 분기 no-op → positive-leak.
FROM_M1 = "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"
TO_M1 = "    if False:  # neutralized M1 positive-control-presence (self-test mutation)"
# M4 (AC-5 trace 축, exit 불변): green verdict trace 문구 토큰 치환 → stdout 소실.
FROM_M4 = "enrolled={enrolled} subject scanned"
TO_M4 = "NEUTRALIZED-M4-TRACE-TOKEN"


# ─────────────────────────── subprocess helper (Windows-safe) ───────────────────────────
def _run_gate(gate_py, repo_root):
    """REAL gate core 를 sys.executable 로 직접 실행 → (returncode, stdout, stderr).

    bytes PIPE + utf-8/replace decode (non-UTF-8 locale 한글 crash 회피). bash wrapper 미경유
    (Windows python subprocess 가 'bash' PATH 해소 불가 → py-path 직접).
    """
    proc = subprocess.run(
        [sys.executable, str(gate_py), "--repo-root", str(repo_root)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")
    return proc.returncode, out, err


def _mutate(gate_src, frm, to, dest):
    """REAL gate source 문자열을 1:1 치환한 mutant 를 dest 에 write.

    double-guard: (a) anchor 미매칭 → AssertionError(recipe drift, false PASS 금지)
                  (b) mutated 는 valid python (py_compile).
    """
    assert frm in gate_src, f"mutation anchor 미매칭 (recipe drift — real gate 변경? NOT silent pass): {frm!r}"
    dest.write_text(gate_src.replace(frm, to, 1), encoding="utf-8")
    py_compile.compile(str(dest), doraise=True)
    return dest


# ─────────────────────────── fixture emitters (gate 계약 reconciled) ───────────────────────────
def _concept_lines(mode="green"):
    """concept doc emit — GREEN 은 AC-6/8/12 동시 충족. mode 로 단일 토큰 결함 주입.

    [reconciled: gate _TAXONOMY_TOKENS / _HONEST_DEGRADE_EXCEPTION / _CEILING_TOKENS /
     _PRESENCE_TRUTH_TOKENS / _NAMED_CONCEPTS(≥6) / _NEW_DEF_AREAS / _detect_recodify / _detect_overclaim]
    토큰 격리: 각 결함 토큰이 정확히 1곳에만 존재하도록 heading/area 에서 중복 배제(단일 mode 가 정확 제거).
    """
    L = ["# hard gate self-verification concept (fixture)", ""]
    L.append("## 3-way taxonomy (antonym)")
    L.append("- silent-green — 게이트 green 이나 검출력 0 = 결함(위양성)")
    if mode != "no_tax":
        L.append("- silent-fallback — 검증 경로 우회/흡수 = 결함(위양성)")
    L.append("- honest-degrade — 의도적 fail-open + 정직 공개 = 정상")
    if mode != "no_exc":
        L.append("  honest-degrade 는 결함 아님 (오탐 방지 codify 필수 — 무차별 검출 = 위양성).")
    L.append("")
    L.append("## ceiling")
    if mode != "no_ceiling":
        L.append("검출 sufficiency = undecidable — 정직 천장(honest-ceiling). L3 review-tier(AC-9).")
    if mode != "no_pt":
        L.append("presence ≠ truth. bounded degradation.")
    if mode == "overclaim":
        L.append("이 메타-게이트는 universal detection 완전 봉인 을 달성한다.")
    L.append("")
    L.append("## named cross-ref (super-class compose, 재정의 0)")
    L.append("- red-green-stash-proof — RED proof (ADR-082 §11.A)")
    L.append("- vacuous-pass — 검출력 0 green 상위 class")
    L.append("- execution-liveness — self-test 채널 alive L1 (ADR-151)")
    if mode != "few_named":
        L.append("- discriminating-fixture — clean↔mutant 구별 (ADR-006 §8.7)")
        L.append("- discriminating-A/B — self-test / product activation (ADR-152)")
        L.append("- mutation-hollow-gate — meta-hollow 차단")
        L.append("- honest-degrade — 정직 공개 cross-ref")
    L.append("")
    L.append("## 신규 정의 3영역")
    L.append("super-class 명명 + taxonomy codify")
    if mode != "no_area":
        L.append("+ internal-control identity-probe.")
    if mode == "recodify":
        L.append("- execution-liveness = 재정의 대입 (cross-ref only 위반)")
    return "\n".join(L) + "\n"


def _subject_lines(mode="good"):
    """enrolled hard-gate self-test fixture (fake 대상 게이트의 self-test).

    [reconciled: gate _ENROLL_MARKERS('hgsv-enroll') / _POSITIVE_CONTROL_ANCHORS / _has_two_exit_shape
     (≥2 X=$? + -eq 0 + -ne 0) / _IDENTITY_BEARING_DECL / _PROBE_ANCHORS]
    """
    L = ["#!/usr/bin/env bash", "# hgsv-enroll (hard gate self-test fixture subject)"]
    if mode != "no_positive":
        L.append("# positive-control: sanity mutant→RED (결함앞 RED 상시 증명)")
    if mode in ("id_no_probe", "id_probe"):
        L.append("# identity_bearing: true")
    if mode == "id_probe":
        L.append("# internal-control: resolved-target 원문대조 known-answer probe")
    if mode == "no_shape":
        # string-only(exit-capture 0) → _has_two_exit_shape False → AC-2 RED.
        L.append('echo "clean case: exit 0 expected"')
        L.append('echo "mutant case: exit 1 expected"')
    else:
        # 2-exit-differ shape: ≥2 exit-capture + clean(-eq 0) + mutant(-ne 0).
        L.append("run_gate clean; rc=$?")
        L.append("run_gate mutant; mrc=$?")
        L.append('if [ "$rc" -eq 0 ]; then echo clean-ok; fi')
        L.append('if [ "$mrc" -ne 0 ]; then echo mutant-red; fi')
    return "\n".join(L) + "\n"


def _build(root, concept_mode="green", subject_mode="good", enrolled_zero=False, add_unreadable=False):
    """fixture repo-root build — concept doc + (enrolled subject) + non-enrolled decoy [+ unreadable]."""
    concept_dir = root / "docs" / "domain-knowledge" / "concept"
    tests_dir = root / "tests" / "scripts"
    concept_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    (concept_dir / "hard-gate-self-verification.md").write_text(_concept_lines(concept_mode), encoding="utf-8")
    if not enrolled_zero:
        (tests_dir / "test_subject_good.sh").write_text(_subject_lines(subject_mode), encoding="utf-8")
    # 미 enroll decoy(marker 부재) — subject 발견에서 제외되어야(무영향 실증).
    (tests_dir / "test_decoy_plain.sh").write_text(
        "#!/usr/bin/env bash\n# no enroll marker here\nexit 0\n", encoding="utf-8"
    )
    if add_unreadable:
        # 디렉터리를 *.sh 로 생성 → open() OSError → _read_lines None → AC-4 unreadable fail-closed.
        (tests_dir / "test_unreadable.sh").mkdir(parents=True, exist_ok=True)
    return root


# ═════════════════════════════ RTM §8.2.1 — 명명 테스트 (present→exit0 ↔ absent→exit1) ═════════════════════════════
def test_ac1_positive_control_present(tmp_path):
    """AC-1 — positive-control self-test anchor 보유→exit0 ↔ 부재→exit1 (M1 대상)."""
    g = _build(tmp_path / "green")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    r = _build(tmp_path / "red", subject_mode="no_positive")
    rrc, _ro, rerr = _run_gate(GATE_PY, r)
    assert grc == 0, gerr
    assert rrc == 1, rerr
    assert "[AC-1]" in rerr, rerr
    assert grc != rrc  # anti-theater discriminating


def test_ac2_two_exit_shape(tmp_path):
    """AC-2 — 2-exit-differ shape→exit0 ↔ string-only(capture 0)→exit1 (M6 seal: shape-scan≠string-scan)."""
    g = _build(tmp_path / "green")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    r = _build(tmp_path / "red", subject_mode="no_shape")
    rrc, _ro, rerr = _run_gate(GATE_PY, r)
    assert grc == 0, gerr
    assert rrc == 1, rerr
    assert "[AC-2]" in rerr, rerr
    assert grc != rrc


def test_ac3_empty_target_failclosed(tmp_path):
    """AC-3 — enrolled 0 honest-degrade(명시 선언)→exit0 ↔ unparseable enrolled subject→exit1(silent skip 금지)."""
    z = _build(tmp_path / "zero", enrolled_zero=True)
    zrc, zout, zerr = _run_gate(GATE_PY, z)
    assert zrc == 0, zerr
    assert "honest-degrade" in zout, zout  # 침묵 GREEN 아님 — 명시 honest-degrade 선언 emit
    # 정상 subject 존재도 exit0.
    g = _build(tmp_path / "green")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    assert grc == 0, gerr
    # unparseable/unreadable enrolled subject (dir-as-.sh) → fail-closed exit1.
    r = _build(tmp_path / "red", add_unreadable=True)
    rrc, _ro, rerr = _run_gate(GATE_PY, r)
    assert rrc == 1, rerr
    assert "[AC-4]" in rerr or "읽기 불가" in rerr, rerr
    assert zrc != rrc  # honest-degrade(0) ≠ unparseable(1)


def test_ac4_unknown_input_failclosed(tmp_path):
    """AC-4 — valid repo-root→exit0 ↔ 미존재/비-dir repo-root→exit1 (default 실행=silent-fallback 금지)."""
    g = _build(tmp_path / "green")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    assert grc == 0, gerr
    # 미존재 repo-root.
    nrc, _no, nerr = _run_gate(GATE_PY, tmp_path / "does_not_exist")
    assert nrc == 1, nerr
    assert "[AC-4]" in nerr, nerr
    # 비-dir repo-root(파일).
    afile = tmp_path / "afile"
    afile.write_text("x\n", encoding="utf-8")
    frc, _fo, ferr = _run_gate(GATE_PY, afile)
    assert frc == 1, ferr
    assert "[AC-4]" in ferr, ferr
    assert grc != nrc and grc != frc


def test_ac5_execution_trace_emit(tmp_path):
    """AC-5 — green verdict stdout execution-trace present ↔ M4 neutralize→token 소실(exit 불변 0→0)."""
    fx = _build(tmp_path / "fx")
    rc, out, err = _run_gate(GATE_PY, fx)
    assert rc == 0, err
    assert "subject scanned" in out, out
    assert "enrolled=" in out, out
    # discriminating (M4 = stdout 축, exit 불변): trace 토큰 치환 → 소실 실증(trace load-bearing).
    gate_src = GATE_PY.read_text(encoding="utf-8")
    mutant = _mutate(gate_src, FROM_M4, TO_M4, tmp_path / "mutant_gate.py")
    mrc, mout, merr = _run_gate(mutant, fx)
    assert mrc == 0, merr  # M4 는 exit-flip 아님 (stdout 축)
    assert "subject scanned" not in mout, "M4 neutralize 후에도 trace token 잔존 — trace 비-load-bearing(false-oracle)"


def test_ac6_three_way_taxonomy_present(tmp_path):
    """AC-6 — silent-green≠silent-fallback≠honest-degrade 3-way + '결함 아님' 예외 present→exit0 ↔ 부재→exit1 (M2)."""
    g = _build(tmp_path / "green")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    assert grc == 0, gerr
    for mode in ("no_tax", "no_exc"):
        r = _build(tmp_path / ("red_" + mode), concept_mode=mode)
        rrc, _ro, rerr = _run_gate(GATE_PY, r)
        assert rrc == 1, (mode, rerr)
        assert "[AC-6]" in rerr, (mode, rerr)
        assert grc != rrc


def test_ac7_self_application(tmp_path):
    """AC-7 — 메타-게이트 자기 positive-control(자기 subject mutant→RED) + inventory bijection (born-hollow FORBIDDEN).

    self-application 3-축:
      (a) TC-CLEAN-PASS: valid 번들 → exit0 (L3 sufficiency 미강제 실증).
      (b) M1 positive-leak: baseline(positive-control 부재 kill-fixture)=exit1 → M1 분기 neutralize=exit0
          = KILLED (게이트 자기 fail-closed 분기 load-bearing — 자기 subject 에 규약 재귀 적용).
      (c) inventory bijection: ADR-151 selftest-execution-liveness 인벤토리에 `.sh` cross-seal 1행 enroll
          + `.sh` 원본 무손상 presence (two-meta-gate mutual cross-seal, meta-hollow 무한후퇴 차단).
    """
    # (a) TC-CLEAN-PASS.
    clean = _build(tmp_path / "clean")
    crc, _co, cerr = _run_gate(GATE_PY, clean)
    assert crc == 0, cerr

    # (b) M1 positive-leak (자기 subject mutant→RED 분기 load-bearing).
    kill_fx = _build(tmp_path / "kill", subject_mode="no_positive")
    base_rc, _bo, berr = _run_gate(GATE_PY, kill_fx)
    assert base_rc == 1, f"baseline kill-fixture(positive-control 부재)는 exit1 이어야 (AC-1 RED). got {base_rc}: {berr}"
    gate_src = GATE_PY.read_text(encoding="utf-8")
    mutant = _mutate(gate_src, FROM_M1, TO_M1, tmp_path / "mutant_gate.py")
    mut_rc, _mo, _me = _run_gate(mutant, kill_fx)
    assert mut_rc == 0, f"M1 neutralize 후 mutant 는 exit0 이어야 (positive-control 검사 제거). got {mut_rc}"
    assert base_rc == 1 and mut_rc == 0  # KILLED positive-leak (baseline 1 → mutant 0)

    # (c) inventory bijection + `.sh` cross-seal 원본 무손상.
    sh = REPO_ROOT / "tests" / "scripts" / "test_check-hard-gate-self-verification.sh"
    assert sh.is_file(), ".sh AC-7 cross-seal self-test 원본 부재(무손상 dual 위반)"
    inventory = (REPO_ROOT / "docs" / "selftest-execution-liveness-inventory.yaml").read_text(encoding="utf-8")
    assert 'tests/scripts/test_check-hard-gate-self-verification.sh' in inventory, (
        "ADR-151 selftest-execution-liveness 인벤토리에 `.sh` self-test bijection enroll 부재"
    )


def test_ac8_honest_ceiling_present(tmp_path):
    """AC-8 — ceiling + presence≠truth present ∧ over-claim 부재→exit0 ↔ 부재/over-claim→exit1 (INV-5 P0)."""
    g = _build(tmp_path / "green")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    assert grc == 0, gerr
    for mode in ("no_ceiling", "no_pt", "overclaim"):
        r = _build(tmp_path / ("red_" + mode), concept_mode=mode)
        rrc, _ro, rerr = _run_gate(GATE_PY, r)
        assert rrc == 1, (mode, rerr)
        assert "[AC-8]" in rerr, (mode, rerr)
        assert grc != rrc


def test_ac12_crossref_nodup(tmp_path):
    """AC-12 — named cross-ref ≥6 + 신규 정의 3영역 + 재codify 부재→exit0 ↔ <6/영역누락/재codify→exit1."""
    g = _build(tmp_path / "green")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    assert grc == 0, gerr
    for mode in ("few_named", "no_area", "recodify"):
        r = _build(tmp_path / ("red_" + mode), concept_mode=mode)
        rrc, _ro, rerr = _run_gate(GATE_PY, r)
        assert rrc == 1, (mode, rerr)
        assert "[AC-12]" in rerr, (mode, rerr)
        assert grc != rrc


def test_ac13_identity_probe(tmp_path):
    """AC-13 — self-declared identity_bearing:true + internal-control probe present→exit0 ↔ probe부재→exit1; 미선언=no-op (M5)."""
    g = _build(tmp_path / "green", subject_mode="id_probe")
    grc, _go, gerr = _run_gate(GATE_PY, g)
    assert grc == 0, gerr
    r = _build(tmp_path / "red", subject_mode="id_no_probe")
    rrc, _ro, rerr = _run_gate(GATE_PY, r)
    assert rrc == 1, rerr
    assert "[AC-13]" in rerr, rerr
    # 미선언(=미대상, self-declared selector) → probe 없어도 exit0 (정직 no-op).
    noop = _build(tmp_path / "noop")  # good subject, identity_bearing 미선언
    nrc, _no, nerr = _run_gate(GATE_PY, noop)
    assert nrc == 0, nerr
    assert grc != rrc
