#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/scripts/test_check_hollow_gate_corpus.py

CFP-2963 / ADR-175 — hollow-gate corpus 판정 하네스(scripts/lib/check_hollow_gate_corpus.py)의
RTM self-test (pytest). 형제 `tests/scripts/test_check-hollow-gate-corpus.sh` 와 **dual**:

  - `.sh`  = 인벤토리 enroll 채널(selftest-execution-liveness bijection) + CI job 실행 진입점.
  - `.py`  = RTM 채널. ac-traceability Hop3 는 `ast` 로 `def test_*` 를 resolve 하므로 `.sh` 만으로는
             AC 가 born-missing 된다. 둘 다 있어야 AC 가 실제 실행 함수로 착지한다.

두 파일은 관측면이 겹치되 **접근 경로가 다르다**: `.sh` 는 전부 subprocess 로 REAL exit code 를 보고,
본 파일은 core 를 **in-process import** 해 판정 함수·materialize 를 직접 부른다(부수 경로 없이 계약을
직접 falsify). exit-code 경로만 subprocess 로 확인한다.

★ 판정 기준 3건 (형제 `.sh` 헤더와 동일 — 어기면 정상 corpus 를 오판한다)
  ① 「균일 = 하네스 사망」의 정의는 "전 leg 동일"이지 "전부 상이가 아님"이 아니다. day-1 실측 8 leg 은
     4 distinct 가 정상이며 `s02 kill ≡ s02 clean` 은 결함이 아니라 arm-H 의 정의다.
  ② 판별자 = 마커 문면이지 프로세스 rc 가 아니다. rc 는 I-4(선언 exit_space 이탈)에만 쓰인다.
  ③ mutation KILLED ⟺ baseline(무변형)=기대 exit AND mutant=다른 exit. 한쪽만 보면 무효.

★ 정직 천장 (ADR-175 / ADR-151 §결정7 / INV-5)
  본 self-test 가 보장하는 것은 **등재 표본에 대한 관측 기반 판별력**까지다. corpus 밖 게이트 일반으로
  외삽하지 않는다 — 미등재 게이트의 hollow 여부는 본 채널의 값공간 밖(미판정)이다. presence != truth:
  GREEN 은 "하네스가 주입된 결함 앞에서 RED 를 냈다"이지 "hollow 게이트가 더는 없다"가 아니다.
  검출 sufficiency 는 undecidable 이므로 'universal' / 'class 봉쇄' 류 단정은 하지 않는다.

repo 실파일은 일절 수정하지 않는다 — 변형은 전부 tmp_path 안 shadow repo-root 와 core 사본에서만.
"""

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# conftest.py 가 scripts/ 와 scripts/lib/ 를 sys.path 에 주입한다.
import check_hollow_gate_corpus as hgc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PY = REPO_ROOT / "scripts" / "lib" / "check_hollow_gate_corpus.py"
MANIFEST = REPO_ROOT / "docs" / "hollow-gate-corpus-manifest.yaml"
BASELINE = REPO_ROOT / "docs" / "hollow-gate-corpus-baseline.yaml"
CORPUS = REPO_ROOT / "tests" / "fixtures" / "hollow-gate-corpus"
GATE_SRC = REPO_ROOT / "scripts" / "lib" / "check_hard_gate_self_verification.py"

TERM_PREFIX = "✓ check-hard-gate-self-verification:"


# ══════════════════════════════════════════════════════════════════════════════
# NOT_RUN 가드 — 검사 대상 부재 시 skip 이 아니라 명시 실패 (false PASS 금지)
# ══════════════════════════════════════════════════════════════════════════════
def _require_substrate():
    missing = [
        str(p) for p in (CORE_PY, MANIFEST, BASELINE, GATE_SRC, CORPUS / "s01", CORPUS / "s02")
        if not p.exists()
    ]
    if missing:
        pytest.fail(f"NOT_RUN — 검사 대상 부재: {missing} (대상 미착륙 상태에서 초록을 내지 않는다)")


# ══════════════════════════════════════════════════════════════════════════════
# helper — shadow repo-root / manifest emitter / subprocess 실행
# ══════════════════════════════════════════════════════════════════════════════
def build_shadow(tmp_path, extra="none"):
    """repo 실파일 무오염 shadow repo-root.

    corpus 하위 전 파일이 정확히 1개 samples[] 를 참조해야 하므로(bijection), 시나리오가
    manifest 로 참조할 표본 디렉터리만 담는다.
    """
    root = tmp_path / f"shadow_{extra}_{len(list(tmp_path.iterdir()))}"
    (root / "docs").mkdir(parents=True)
    (root / "scripts" / "lib").mkdir(parents=True)
    corpus = root / "tests" / "fixtures" / "hollow-gate-corpus"
    corpus.mkdir(parents=True)
    shutil.copyfile(BASELINE, root / "docs" / "hollow-gate-corpus-baseline.yaml")
    shutil.copyfile(GATE_SRC, root / "scripts" / "lib" / GATE_SRC.name)
    for sid in ("s01", "s02"):
        shutil.copytree(CORPUS / sid, corpus / sid)
    if extra == "s03":
        shutil.copytree(CORPUS / "s01", corpus / "s03")
    if extra == "s04":
        shutil.copytree(CORPUS / "s01", corpus / "s04")
        # 오염 = 목표 축(AC-1, kill 의 test_subject_good) + 타 축(AC-8, xkill 의 concept doc) 동시 발화.
        rel = "docs/domain-knowledge/concept/hard-gate-self-verification.md.sample"
        shutil.copyfile(CORPUS / "s01" / "xkill" / rel, corpus / "s04" / "kill" / rel)
    return root


_GATE_BLOCK = """schema_version: "1.0"
gates:
  - id: check-hard-gate-self-verification
    source_path: scripts/lib/check_hard_gate_self_verification.py
    entry: gate.py
    invoke_args: ["--repo-root", "{{fixture}}"]
    fail_marker_stream: stderr
    terminal_marker_stream: stdout
    fail_marker_stage_id: "{stage}"
    terminal_marker_prefix: "{term}"
    exit_space: {exit_space}
"""

_SAMPLE_ROW = """  - id: {sid}
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/{sid}
    fixtures: {{ kill: {kill}, clean: clean, empty: empty, xkill: {xkill} }}
"""

_RECIPE_BODY = """    derived_from: s01
    target: {target}
    anchor_from: "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"
    anchor_to: "    if False:  # neutralized M1 positive-control-presence"
"""


def write_manifest(path, stage="AC-1", exit_space="[0, 1]", extra="none", flip=False,
                   probe=True, samples="normal", recipe_target="gate.py.sample",
                   forbidden=False, probe_anchor_from=None, derived_from_mismatch=False,
                   recipe_anchor_mismatch=False):
    """시나리오 manifest 를 생성한다 (repo 의 shipped manifest 는 건드리지 않는다)."""
    out = [_GATE_BLOCK.format(stage=stage, term=TERM_PREFIX, exit_space=exit_space)]
    if samples == "empty":
        out.append("samples: []\n")
    else:
        out.append("samples:\n")
        out.append(_SAMPLE_ROW.format(sid="s01", kill="kill", xkill="xkill"))
        out.append(_SAMPLE_ROW.format(sid="s02", kill="kill", xkill="xkill"))
        if extra == "s03" or derived_from_mismatch:
            # 축 어긋남: kill 자리에 xkill(AC-8 축) fixture 를 앉힌다 — 선언 stage 는 AC-1 인데
            # 관측 stage 는 {AC-8, SUMMARY} 라 짝이 맞지 않는다.
            # OR derived_from_mismatch 테스트용 s03 (IC-1 negative)
            out.append(_SAMPLE_ROW.format(sid="s03", kill="xkill", xkill="kill"))
        if extra == "s04":
            out.append(_SAMPLE_ROW.format(sid="s04", kill="kill", xkill="xkill"))
    out.append("build:\n  - sample: s02\n")
    # ⓺ provenance derived_from 변조
    derived = "s03" if derived_from_mismatch else "s01"
    out.append(f"    derived_from: {derived}\n")
    out.append(f"    target: {recipe_target}\n")
    # anchor 변조 (recipe target 변조 시 다른 anchor 사용)
    if recipe_anchor_mismatch:
        out.append('    anchor_from: "nonexistent_anchor_string_that_will_not_match"\n')
    else:
        out.append('    anchor_from: "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"\n')
    out.append('    anchor_to: "    if False:  # neutralized M1 positive-control-presence"\n')
    if probe:
        out.append("  - probe: p01\n")
        out.append("    derived_from: s01\n")
        out.append("    target: gate.py.sample\n")
        # probe anchor 변조 (I-1 테스트용)
        if probe_anchor_from:
            out.append(f'    anchor_from: "{probe_anchor_from}"\n')
        else:
            out.append('    anchor_from: "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"\n')
        out.append('    anchor_to: "    if False:  # neutralized"\n')
    out.append("classification:\n")
    lo, hi = ("H", "HOLLOW"), ("L", "LIVE")
    a01, a02 = (lo, hi) if flip else (("L", "LIVE"), ("H", "HOLLOW"))
    if samples != "empty":
        out.append(f"  - sample: s01\n    declared_arm: {a01[0]}\n    expected_verdict: {a01[1]}\n")
        out.append(f"  - sample: s02\n    declared_arm: {a02[0]}\n    expected_verdict: {a02[1]}\n")
        if extra == "s03" or derived_from_mismatch:
            out.append(f"  - sample: s03\n    declared_arm: L\n    expected_verdict: LIVE\n")
        if extra == "s04":
            out.append(f"  - sample: {extra}\n    declared_arm: L\n    expected_verdict: LIVE\n")
    if probe:
        arm = ("L", "LIVE") if flip else ("H", "HOLLOW")
        out.append(f"  - probe: p01\n    declared_arm: {arm[0]}\n    expected_verdict: {arm[1]}\n")
    if forbidden:
        out.append('\nwaiver: "판정 회피 키공간 — denylist 명명 3종 중 1"\n')
    path.write_text("".join(out), encoding="utf-8", newline="\n")
    return path


def run_core(root, manifest=None, core=None):
    """core 를 subprocess 로 실행 → (rc, stdout, stderr). REAL exit code 관측."""
    argv = [sys.executable, str(core or CORE_PY), "--repo-root", str(root)]
    if manifest is not None:
        argv += ["--manifest", str(manifest)]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=600)
    return (proc.returncode,
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"))


def verdict_of(stdout, unit):
    """하네스가 emit 한 `verdict:` 문면에서 verdict 추출 — rc 역추론 금지(판정 기준 ②)."""
    for ln in stdout.splitlines():
        if ln.startswith(f"verdict: unit={unit} "):
            for tok in ln.split():
                if tok.startswith("verdict="):
                    return tok.split("=", 1)[1]
    return None


def census_of(stdout, axis):
    for ln in stdout.splitlines():
        if ln.startswith(f"census: {axis}="):
            return int(ln.split("=", 1)[1])
    return None


def obs(fail=False, term=False, stages=(), observed=()):
    """synthetic LegObs — 판정식을 직접 falsify 하기 위한 관측 벡터."""
    return hgc.LegObs(fail, term, frozenset(stages), frozenset(observed))


def mutate_core(tmp_path, label, old, new):
    """실 core 파일 사본만 sed 상당 치환 (double-guard: 실치환 확인 + compile 확인)."""
    mut = tmp_path / f"mut_{label}.py"
    text = CORE_PY.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"{label}: mutation anchor 매치 != 1 (NOT_RUN — false PASS 금지)"
    mut.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    compile(mut.read_text(encoding="utf-8"), str(mut), "exec")  # 변형본이 valid python 인지
    return mut


# ══════════════════════════════════════════════════════════════════════════════
# T-1 양방향 — 정방향 PASS ↔ 역방향(축 어긋난 선언)도 여전히 RED
# ══════════════════════════════════════════════════════════════════════════════
def test_t1a_pristine_corpus_passes_with_zero_indeterminate():
    """T-1ⓐ 정방향: 무변형 corpus → exit 0 · N_indeterminate=0 · s01=LIVE / s02=HOLLOW / p01=HOLLOW."""
    _require_substrate()
    rc, out, err = run_core(REPO_ROOT)
    assert rc == 0, f"무변형 corpus 가 exit={rc}\n{err}"
    assert census_of(out, "N_indeterminate") == 0
    assert verdict_of(out, "s01") == "LIVE"
    assert verdict_of(out, "s02") == "HOLLOW"
    assert verdict_of(out, "p01") == "HOLLOW"


def test_t1b_autohit_stage_declaration_is_still_red():
    """T-1ⓑ 역방향: 상수 footer(SUMMARY)를 kill_target_stage 로 선언하면 exit 1 + XKILL-AXIS.

    ★ 이것이 없으면 "고쳐서 통과"와 "판별력을 죽여서 통과"를 구별할 수 없다.
    """
    _require_substrate()
    rc, _out, err = run_core(REPO_ROOT, manifest=_tmp_manifest("summary", stage="SUMMARY"))
    assert rc == 1, f"축이 자동 적중하는 선언이 exit={rc} 로 통과\n{err}"
    assert "::error::[XKILL-AXIS]" in err


def test_t1b_xkill_axis_is_the_sole_detector_of_autohit_declaration():
    """T-1ⓑ 보강: 그 어긋남을 잡는 것은 **xkill 축-disjoint 뿐**이다.

    verdict(LIVE/HOLLOW/HOLLOW) · N_indeterminate=0 · IC · census · baseline 은 전부 정상 통과한다
    → M6(축-disjoint 검사)가 load-bearing 임의 실행 증명.
    """
    _require_substrate()
    rc, out, err = run_core(REPO_ROOT, manifest=_tmp_manifest("summary2", stage="SUMMARY"))
    assert rc == 1
    assert verdict_of(out, "s01") == "LIVE"
    assert verdict_of(out, "s02") == "HOLLOW"
    assert verdict_of(out, "p01") == "HOLLOW"
    assert census_of(out, "N_indeterminate") == 0
    stages = [ln for ln in err.splitlines() if ln.startswith("::error::")]
    kinds = {ln.split("]")[0].split("[")[-1] for ln in stages}
    assert kinds == {"XKILL-AXIS", "SUMMARY"}, f"XKILL-AXIS 외 다른 축도 검출함: {kinds}"


_TMP_DIR = None


def _tmp_manifest(name, **kw):
    global _TMP_DIR
    if _TMP_DIR is None:
        import tempfile
        _TMP_DIR = Path(tempfile.mkdtemp(prefix="hgc-pytest-"))
    return write_manifest(_TMP_DIR / f"manifest_{name}.yaml", **kw)


def teardown_module(module):  # noqa: D103 — 부산물 0
    if _TMP_DIR is not None:
        shutil.rmtree(_TMP_DIR, ignore_errors=True)


# ══════════════════════════════════════════════════════════════════════════════
# 판정기 arm-invariance — 구조(시그니처) + 실행(라벨 뒤집기) 양쪽
# ══════════════════════════════════════════════════════════════════════════════
def test_verdict_signature_cannot_reach_declared_arm():
    """`_verdict()` 시그니처에 arm/declared/expected 가 구조적으로 부재 = arm-invariance 의 기계 근거."""
    import inspect
    params = list(inspect.signature(hgc._verdict).parameters)
    assert params == ["bundle", "kill_target_stage"], params
    for banned in ("arm", "declared", "expected", "classification"):
        assert not any(banned in p for p in params)


def test_arm_invariance_verdict_unchanged_under_label_flip(tmp_path):
    """classification 을 통째로 뒤집어도 verdict 는 불변 — 불일치는 reconcile 단계에서만 발생."""
    _require_substrate()
    root = build_shadow(tmp_path)
    mf = write_manifest(tmp_path / "m_flip.yaml", flip=True)
    rc, out, err = run_core(root, manifest=mf)
    assert verdict_of(out, "s01") == "LIVE"
    assert verdict_of(out, "s02") == "HOLLOW"
    assert verdict_of(out, "p01") == "HOLLOW"
    assert rc == 1
    assert err.count("::error::[VERDICT]") == 3


# ══════════════════════════════════════════════════════════════════════════════
# 판정식 — 마커 관측만으로 LIVE / HOLLOW / INDETERMINATE (rc 미투입)
# ══════════════════════════════════════════════════════════════════════════════
def test_verdict_live_hollow_indeterminate_from_marker_observation_only():
    """동결 판정식 3분기. 입력은 마커 관측뿐이며 프로세스 rc 는 어디에도 들어가지 않는다."""
    target = "AC-1"
    kill_live = obs(fail=True, term=False, stages=(target, "SUMMARY"),
                    observed=(("stderr", "::error::[AC-1] x"), ("stderr", "::error::[SUMMARY] y")))
    clean = obs(fail=False, term=True, observed=(("stdout", TERM_PREFIX + " ok"),))
    empty = obs(fail=False, term=True, observed=(("stdout", TERM_PREFIX + " degrade"),))
    assert hgc._verdict(hgc.VerdictBundle(kill_live, clean, empty), target)[0] == "LIVE"

    # arm-H: kill 이 clean 과 **동일** 관측을 낸다 = 결함 앞에서도 GREEN. 이것이 HOLLOW 의 정의다.
    kill_hollow = clean
    assert hgc._verdict(hgc.VerdictBundle(kill_hollow, clean, empty), target)[0] == "HOLLOW"

    # 축이 어긋난 kill(AC-8 만 울림) = 어느 정의도 만족하지 않음.
    kill_wrong = obs(fail=True, term=False, stages=("AC-8", "SUMMARY"),
                     observed=(("stderr", "::error::[AC-8] z"),))
    assert hgc._verdict(hgc.VerdictBundle(kill_wrong, clean, empty), target)[0] == "INDETERMINATE"


def test_delivered_requires_kill_and_empty_observations_to_differ():
    """DELIVERED ⟺ observed_line_set(kill) != observed_line_set(empty). 같으면 I-7 로 판정불가."""
    target = "AC-1"
    same = obs(fail=False, term=True, observed=(("stdout", TERM_PREFIX + " ok"),))
    verdict, delivered = hgc._verdict(hgc.VerdictBundle(same, same, same), target)
    assert delivered is False
    assert verdict == "INDETERMINATE"
    assert "I-7" in hgc._post_verdict_labels(hgc.VerdictBundle(same, same, same), target, verdict, delivered)


def test_i8_stenosis_conjunct_is_load_bearing_for_arm_h():
    """M1 대응: I-8 의 `kill.fail=1` 협착이 없으면 정상 arm-H 가 공허 참으로 전멸한다.

    arm-H 의 kill 은 fail_stage=∅ 이므로 `target not in ∅` 은 항상 참이다 — 협착 conjunct 만이
    그 공허 참을 막는다. 여기서는 두 술어를 나란히 계산해 conjunct 의 기여를 직접 보인다.
    """
    target = "AC-1"
    clean = obs(fail=False, term=True, observed=(("stdout", TERM_PREFIX + " ok"),))
    empty = obs(fail=False, term=True, observed=(("stdout", TERM_PREFIX + " degrade"),))
    bundle = hgc.VerdictBundle(clean, clean, empty)          # arm-H shape (kill ≡ clean)
    verdict, delivered = hgc._verdict(bundle, target)
    assert verdict == "HOLLOW"
    labels = hgc._post_verdict_labels(bundle, target, verdict, delivered)
    assert "I-8" not in labels, "정상 arm-H 에 I-8 이 붙으면 born-RED"
    # 협착 conjunct 를 뺀 술어는 참이 된다 = 그 conjunct 가 유일한 방어다.
    assert (target not in bundle.kill.fail_stages) is True
    assert (bundle.kill.fail and target not in bundle.kill.fail_stages) is False


def test_i11_guard_is_load_bearing_for_arm_h():
    """M2 대응: I-11 의 `¬LIVE ∧ ¬HOLLOW` 가드가 없으면 arm-H 가 전멸한다.

    arm-H 는 정의상 kill 관측 ≡ clean 관측이므로 I-11 의 뒷 conjunct 는 항상 참이다.
    """
    target = "AC-1"
    clean = obs(fail=False, term=True, observed=(("stdout", TERM_PREFIX + " ok"),))
    empty = obs(fail=False, term=True, observed=(("stdout", TERM_PREFIX + " degrade"),))
    bundle = hgc.VerdictBundle(clean, clean, empty)
    verdict, delivered = hgc._verdict(bundle, target)
    assert verdict == "HOLLOW"
    assert bundle.kill.observed == bundle.clean.observed, "arm-H 의 정의(결함 앞에서도 동일 관측)"
    assert "I-11" not in hgc._post_verdict_labels(bundle, target, verdict, delivered)

    # 반대로 verdict 가 어느 쪽도 아니면서 관측이 같으면 I-11 이 붙어야 한다.
    mute = obs(fail=False, term=False, observed=(("stdout", "noise"),))
    b2 = hgc.VerdictBundle(mute, mute, empty)
    v2, d2 = hgc._verdict(b2, target)
    assert v2 == "INDETERMINATE"
    assert "I-11" in hgc._post_verdict_labels(b2, target, v2, d2)


def test_marker_stream_declaration_is_enforced_i10():
    """I-10: 선언한 stream 이 아닌 곳에서 마커가 관측되면 관측 무결성 위반으로 잡힌다."""
    gate = {"fail_marker_stream": "stderr", "terminal_marker_stream": "stdout",
            "terminal_marker_prefix": TERM_PREFIX}
    _o, wrong = hgc._observe("::error::[AC-1] on stdout\n", "", gate)
    assert wrong and "fail-marker" in wrong[0]
    o2, wrong2 = hgc._observe("", "", gate)
    assert wrong2 == [] and o2.fail is False and o2.term is False


# ══════════════════════════════════════════════════════════════════════════════
# exit_space (T-2)
# ══════════════════════════════════════════════════════════════════════════════
def test_exit_space_empty_is_loud_substrate_failure(tmp_path):
    """T-2ⓐ: 빈 exit_space 는 조용한 INDETERMINATE 가 아니라 loud exit 3 이어야 한다.

    `rc ∉ ∅` 이 공허 참이 되어 전 leg 이 조용히 INDETERMINATE 로 흐르는 경로를 만들지 않는다.
    ★ 판정 술어 주의: SUBSTRATE 메시지 본문이 사유 설명으로 'I-4' 를 인용하므로 문자열 유무가
      아니라 `::error::[INDETERMINATE]` **라벨** 유무로 읽는다.
    """
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_es0.yaml", exit_space="[]"))
    assert rc == 3, err
    assert "::error::[SUBSTRATE]" in err
    assert "::error::[INDETERMINATE]" not in err


def test_exit_space_normal_does_not_trigger_i4(tmp_path):
    """T-2ⓑ: [0, 1] 은 day-1 실측 rc(kill=1 / clean=0 / empty=0 / xkill=1) 전건을 포함 → I-4 미발동."""
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_es_ok.yaml"))
    assert rc == 0, err
    assert "::error::[INDETERMINATE]" not in err


def test_exit_space_narrowed_triggers_i4(tmp_path):
    """T-2ⓒ: [0] 으로 좁히면 kill leg 의 rc=1 이 I-4 를 발동시켜 exit 1."""
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_es1.yaml", exit_space="[0]"))
    assert rc == 1
    assert "(I-4)" in err and "선언 exit_space" in err


# ══════════════════════════════════════════════════════════════════════════════
# census 7축 — 축별 개별 emit (총합 emit 금지)
# ══════════════════════════════════════════════════════════════════════════════
def test_census_emits_seven_axes_individually():
    """M4 대응: 축별 1줄 고정 형식. 총합 1줄로 degrade 하면 어느 축이 줄었는지 구별 불가."""
    _require_substrate()
    rc, out, _err = run_core(REPO_ROOT)
    assert rc == 0
    lines = [ln for ln in out.splitlines() if ln.startswith("census: ")]
    assert len(lines) == 7
    axes = [ln.split(": ", 1)[1].split("=")[0] for ln in lines]
    assert tuple(axes) == hgc.CENSUS_AXES
    assert census_of(out, "N_gates") == 1
    assert census_of(out, "N_armL") == 1
    assert census_of(out, "N_armH") == 1
    assert census_of(out, "N_probe") == 1
    assert census_of(out, "N_detected") == 2
    assert census_of(out, "N_flip") == 1


def test_census_axes_are_compared_individually_against_baseline():
    """baseline 대조는 축별이다 — 총 N 이 불변인 채 arm 간 상계로 판별력이 빠지는 경로를 닫는다."""
    _require_substrate()
    rc, out, _err = run_core(REPO_ROOT)
    assert rc == 0
    cmp_axes = [ln.split(": ", 1)[1].split(" ")[0] for ln in out.splitlines()
                if ln.startswith("baseline-cmp: ")]
    assert set(cmp_axes) == set(hgc.LOWER_BOUND_AXES)
    assert "N_indeterminate" not in cmp_axes, "N_indeterminate 는 하한이 아니라 상한 축"


# ══════════════════════════════════════════════════════════════════════════════
# IC-4 exec-tree blinding — arm 누설 표면 부재 (in-process 직접 관측)
# ══════════════════════════════════════════════════════════════════════════════
def _load_manifest():
    import yaml
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def test_ic4_exec_tree_carries_no_arm_leaking_surface(tmp_path):
    """exec dir 에 stamp / manifest / baseline / probe 가 **부재**함을 직접 관측한다.

    배경: stamp.yaml.sample 의 `source_sha256 == artifact_sha256` 여부가 arm 과 1:1 상관이다
    (s01 참 / s02 거짓). stamp 가 exec dir 로 새면 라벨 역산 채널이 되므로 IC-4 가 그것을 닫는다.
    """
    _require_substrate()
    man = _load_manifest()
    sample = next(s for s in man["samples"] if s["id"] == "s01")
    gate = next(g for g in man["gates"] if g["id"] == sample["gate"])
    exec_root = tmp_path / "exec"
    exec_root.mkdir()
    unit_dir, _fx, _sha, err = hgc._materialize(
        exec_root, REPO_ROOT, sample, sample["fixtures"]["kill"], gate["entry"], None)
    assert err is None, err
    names = [p.name for p in unit_dir.rglob("*") if p.is_file()]
    assert names, "materialize 결과가 비어있음 (관측 전제 파손)"
    for tok in hgc.BLINDING_FORBIDDEN_TOKENS:
        assert not any(tok in n.lower() for n in names), f"exec dir 에 '{tok}' 누설: {names}"
    assert not any(n.endswith(".sample") for n in names), f".sample 잔재: {names}"
    assert hgc._blinding_violations(unit_dir, exec_root) == []


def test_ic4_exec_unit_dir_is_reassigned_each_materialize(tmp_path):
    """exec dir 명은 실행마다 재배정된다 — 표본 id·leg 이름을 경로에 남기지 않는다."""
    _require_substrate()
    man = _load_manifest()
    sample = next(s for s in man["samples"] if s["id"] == "s01")
    gate = next(g for g in man["gates"] if g["id"] == sample["gate"])
    exec_root = tmp_path / "exec2"
    exec_root.mkdir()
    seen = []
    for _ in range(2):
        unit_dir, _fx, _sha, err = hgc._materialize(
            exec_root, REPO_ROOT, sample, sample["fixtures"]["kill"], gate["entry"], None)
        assert err is None, err
        seen.append(unit_dir.name)
    assert seen[0] != seen[1], seen
    for nm in seen:
        assert "s01" not in nm and "kill" not in nm, f"exec dir 명에 표본/leg 식별자 누설: {nm}"


def test_ic4_leaked_stamp_in_fixture_is_loud_substrate_failure(tmp_path):
    """fixture 안에 stamp 가 잠입하면 exit 3 — blinding assert 가 실제로 강제됨(M5 대응)."""
    _require_substrate()
    root = build_shadow(tmp_path)
    # s01·s02 양쪽에 동일하게 주입 (한쪽에만 넣으면 provenance 검사가 트리 동일성 파손으로 먼저 발화)
    (root / "tests/fixtures/hollow-gate-corpus/s01/clean/stamp_leak.txt").write_text("leak\n")
    (root / "tests/fixtures/hollow-gate-corpus/s02/clean/stamp_leak.txt").write_text("leak\n")
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_leak.yaml"))
    assert rc == 3, err
    assert "exec-tree blinding 파손" in err and "stamp_leak.txt" in err


# ══════════════════════════════════════════════════════════════════════════════
# substrate-failure (exit 3) 조건
# ══════════════════════════════════════════════════════════════════════════════
def test_substrate_zero_denominator_axis_exits_three(tmp_path):
    """⓵ 분모 0 — probe 축을 없애면 N_probe=0 으로 corpus 실체 부재."""
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_np.yaml", probe=False))
    assert rc == 3, err
    assert "분모 0 축" in err and "N_probe" in err


def test_substrate_empty_samples_exits_three(tmp_path):
    """⓵ samples[] 비움 — 표본 0 은 manifest shape 층에서 loud 실패."""
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_ns.yaml", samples="empty"))
    assert rc == 3, err
    assert "samples" in err


def test_substrate_missing_baseline_exits_three(tmp_path):
    """⓶ baseline 부재 — 자동 각인으로 흐르지 않고 loud 실패."""
    _require_substrate()
    root = build_shadow(tmp_path)
    (root / "docs" / "hollow-gate-corpus-baseline.yaml").unlink()
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_nb.yaml"))
    assert rc == 3, err
    assert "baseline 부재" in err


def test_substrate_baseline_digest_binds_manual_edit(tmp_path):
    """⓶ baseline 수기 편집 — content_digest 결박으로 검출."""
    _require_substrate()
    root = build_shadow(tmp_path)
    bp = root / "docs" / "hollow-gate-corpus-baseline.yaml"
    bp.write_text(bp.read_text(encoding="utf-8").replace("N_detected: 2", "N_detected: 1"),
                  encoding="utf-8", newline="\n")
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_bd.yaml"))
    assert rc == 3, err
    assert "content_digest 불일치" in err


def test_baseline_digest_formula_is_reproducible():
    """content_digest 산식이 문서 기재대로 재현되는지 독립 계산으로 대조(known-answer)."""
    _require_substrate()
    import yaml
    data = yaml.safe_load(BASELINE.read_text(encoding="utf-8"))
    axes = {a: int(data["axes"][a]) for a in hgc.CENSUS_AXES}
    payload = "schema_version=1.0\n" + "".join(f"{a}={axes[a]}\n" for a in hgc.CENSUS_AXES) \
              + f"reason={data['reason']}\n"
    expect = "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert data["content_digest"] == expect
    assert hgc._baseline_digest(axes, data["reason"]) == expect


def test_substrate_stamp_drift_exits_three(tmp_path):
    """⓷ stamp drift — source_sha256 이 현행과 어긋나면 자동 갱신 없이 loud 실패."""
    _require_substrate()
    root = build_shadow(tmp_path)
    sp = root / "tests/fixtures/hollow-gate-corpus/s01/stamp.yaml.sample"
    lines = []
    for ln in sp.read_text(encoding="utf-8").splitlines():
        lines.append('source_sha256: "' + "0" * 64 + '"' if ln.startswith("source_sha256:") else ln)
    sp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_sd.yaml"))
    assert rc == 3, err
    assert "source_sha256 drift" in err


def test_substrate_bijection_orphan_exits_three(tmp_path):
    """⓸ bijection 파손 — corpus 파일이 samples[] 참조 0 이면 loud 실패."""
    _require_substrate()
    root = build_shadow(tmp_path)
    (root / "tests/fixtures/hollow-gate-corpus/s01/orphan.txt").write_text("orphan\n")
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_or.yaml"))
    assert rc == 3, err
    assert "samples[] 참조 0개" in err


def test_substrate_recipe_target_outside_sample_exits_three(tmp_path):
    """⓺ recipe 대상이 samples[] 밖이면 loud 실패."""
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(
        tmp_path / "m_rt.yaml", recipe_target="../s02/gate.py.sample"))
    assert rc == 3, err
    assert "samples[] 밖" in err


def test_substrate_forbidden_manifest_key_exits_three(tmp_path):
    """금지키(denylist 명명 3종) — 판정 회피 키공간이 manifest 에 등장하면 loud 실패."""
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_fk.yaml", forbidden=True))
    assert rc == 3, err
    assert "금지키 사용" in err
    assert set(hgc.FORBIDDEN_MANIFEST_KEYS) == {"non_applicable", "waiver", "xfail"}


# ══════════════════════════════════════════════════════════════════════════════
# T-4 / T-6 — post-day-1 편입 · fixture 순도
# ══════════════════════════════════════════════════════════════════════════════
def test_t4_post_day1_axis_mispaired_sample_is_red(tmp_path):
    """T-4: day-1 이후 편입된 표본의 축 짝짓기가 어긋나면 RED (3중 검출).

    ★ 정직 천장: 이 RED 는 **선언 stage 와 관측 stage 의 불일치**를 잡은 것이지 "새 표본의 kill 축이
      그 게이트를 대표하는가"(축 대표성)를 잡은 것이 아니다. 축 대표성의 bearer 는 문서 규약뿐이며
      기계 강제가 없다 — 통과를 만들려고 검사를 약화시키지 않는다.
    """
    _require_substrate()
    root = build_shadow(tmp_path, extra="s03")
    rc, out, err = run_core(root, manifest=write_manifest(tmp_path / "m_t4.yaml", extra="s03"))
    assert rc == 1, err
    assert verdict_of(out, "s03") == "INDETERMINATE"
    assert "unit=s03: I-8 성립" in err
    assert "::error::[XKILL-AXIS] unit=s03" in err
    assert "::error::[VERDICT] unit=s03" in err


def test_t6_polluted_fixture_lands_on_live_by_membership_semantics(tmp_path):
    """T-6 fixture 순도: 목표 축 + 타 축 **동시** 발화 시 의도한 착지 = LIVE 허용(RED 아님).

    근거: 판정식의 conjunct 는 `kill_target_stage ∈ fail_stage(kill)` 즉 **멤버십**이지 배타성이
    아니다(ADR-175 DR4-M1 — 한 leg 의 stage id 개수는 고정이 아니며 상수 footer 와 공존한다).
    배타성을 요구하도록 좁히면 day-1 정상 표본(AC-1 + SUMMARY 공존)이 즉시 born-RED 가 된다.
    ⇒ 순도는 기계 강제 대상이 아니고 표본 제작 규약이 진다(하네스 docstring 의 축 대표성 잔여와 동근).
    """
    _require_substrate()
    root = build_shadow(tmp_path, extra="s04")
    rc, out, err = run_core(root, manifest=write_manifest(tmp_path / "m_t6.yaml", extra="s04"))
    assert rc == 0, err
    assert verdict_of(out, "s04") == "LIVE"
    kill_line = next(ln for ln in out.splitlines() if ln.startswith("obs-digest: unit=s04 leg=kill "))
    assert "'AC-1'" in kill_line and "'AC-8'" in kill_line, kill_line


# ══════════════════════════════════════════════════════════════════════════════
# mutation kill (subprocess) — .sh 와 독립 경로로 M1 / M2 / M6 재확인
# ══════════════════════════════════════════════════════════════════════════════
def test_mutation_m1_i8_stenosis_conjunct_killed(tmp_path):
    """M1 KILLED: baseline exit 0 → mutant exit 1 (arm-H 가 I-8 로 전멸)."""
    _require_substrate()
    base_rc, _o, _e = run_core(REPO_ROOT)
    assert base_rc == 0, "baseline 이 0 이 아니면 kill 대조 자체가 무효"
    mut = mutate_core(
        tmp_path, "m1",
        "    if bundle.kill.fail and kill_target_stage not in bundle.kill.fail_stages:",
        "    if kill_target_stage not in bundle.kill.fail_stages:  # M1-neutralized")
    rc, _out, err = run_core(REPO_ROOT, core=mut)
    assert rc != base_rc, "M1 SURVIVED — 협착 conjunct 가 판별에 기여하지 않음"
    assert "I-8" in err


def test_mutation_m2_i11_guard_killed(tmp_path):
    """M2 KILLED: baseline exit 0 → mutant exit 1 (arm-H 가 I-11 로 전멸)."""
    _require_substrate()
    base_rc, _o, _e = run_core(REPO_ROOT)
    assert base_rc == 0
    mut = mutate_core(
        tmp_path, "m2",
        "    if (not live) and (not hollow) and (bundle.kill.observed == bundle.clean.observed):",
        "    if (bundle.kill.observed == bundle.clean.observed):  # M2-neutralized")
    rc, _out, err = run_core(REPO_ROOT, core=mut)
    assert rc != base_rc, "M2 SURVIVED — I-11 가드가 판별에 기여하지 않음"
    assert "I-11" in err


def test_mutation_m6_xkill_axis_disjoint_killed(tmp_path):
    """M6 KILLED: 축 자동적중 manifest 에서 baseline exit 1 → mutant exit 0 (검출자 소멸)."""
    _require_substrate()
    mf = write_manifest(tmp_path / "m_m6.yaml", stage="SUMMARY")
    base_rc, _o, _e = run_core(REPO_ROOT, manifest=mf)
    assert base_rc == 1
    mut = mutate_core(
        tmp_path, "m6",
        '                if tgt in legs["xkill"].fail_stages:',
        "                if False:  # M6-neutralized")
    rc, _out, _err = run_core(REPO_ROOT, manifest=mf, core=mut)
    assert rc != base_rc, "M6 SURVIVED — 상수 footer 선언이 무증상 통과"
    assert rc == 0


# ══════════════════════════════════════════════════════════════════════════════
# 정직 천장 (INV-5)
# ══════════════════════════════════════════════════════════════════════════════
def test_honest_ceiling_vocabulary_is_absent_and_ceiling_is_stated():
    """PASS 발화가 천장을 동반하고, over-claim 어휘는 등장하지 않는다."""
    _require_substrate()
    rc, out, _err = run_core(REPO_ROOT)
    assert rc == 0
    for word in ("완전 봉인", "universal detection", "class 봉쇄", "근절"):
        assert word not in out, f"over-claim 어휘 '{word}' 가 하네스 stdout 에 등장 (INV-5)"
    assert "presence ≠ truth" in out
    assert "corpus 밖" in out


def test_identity_probe_resolved_target_matches_committed_artifact():
    """internal-control identity probe — known-answer 원문대조.

    하네스가 emit 한 `resolved-target ... sha256=<X>` 가 커밋 파일 s01/gate.py.sample 의 sha256 과
    문면 일치해야 한다. 기대값은 하네스 출력이 아니라 독립 계산이며(자기 출력 순환 인용 아님),
    일치는 "판정기가 실제로 그 커밋 artifact 를 열었다"의 내부 대조 증거다.
    """
    _require_substrate()
    known = hashlib.sha256((CORPUS / "s01" / "gate.py.sample").read_bytes()).hexdigest()
    rc, out, _err = run_core(REPO_ROOT)
    assert rc == 0
    line = next(ln for ln in out.splitlines() if ln.startswith("resolved-target: unit=s01 "))
    assert line.endswith("sha256=" + known), f"{line}\nknown={known}"


# ══════════════════════════════════════════════════════════════════════════════
# 신설 커버리지 4종 — FIX-A/B/C 변경사항 반영
# ══════════════════════════════════════════════════════════════════════════════

def test_i1_anchor_mismatch_in_probe_recipe_unit(tmp_path):
    """I-1 anchor 매치 ≠ 1: run-time probe 정의역만 (commit-sample은 ⓺ provenance 소관).

    probe recipe 의 anchor_from 을 corpus 부재 문자열로 → I-1 발동 → exit 1 + '매치 ≠ 1 … (I-1)'.
    commit-sample 은 recipe=None 이므로 I-1 가드 미도달 — 이 비대칭이 ⓺ provenance 검사를 필요하게 한다.
    """
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(
        tmp_path / "m_i1.yaml", probe_anchor_from="nonexistent_anchor_string"))
    assert rc == 1, f"I-1 미발동: rc={rc}\n{err}"
    assert "anchor 매치" in err and "≠ 1" in err and "I-1" in err, f"I-1 문면 미관측: {err}"


def test_substrate_provenance_anchor_mismatch_in_derived_from(tmp_path):
    """⓺ provenance (a): 파생 지점 특정 — recipe anchor 매치 ≠ 1.

    recipe 의 anchor_from 을 corpus 부재 문자열로 → s02.derived_from(s01)에서 anchor 미매치
    → provenance 파손 → exit 3.
    """
    _require_substrate()
    root = build_shadow(tmp_path)
    rc, _out, err = run_core(root, manifest=write_manifest(
        tmp_path / "m_prov_anchor.yaml",
        recipe_anchor_mismatch=True))  # recipe anchor 변조
    assert rc == 3, f"provenance 미발동: rc={rc}\n{err}"
    assert "provenance 파손" in err and "anchor 매치" in err and "≠ 1" in err, \
        f"provenance anchor 문면 미관측: {err}"


def test_substrate_provenance_tree_mismatch(tmp_path):
    """⓺ provenance (c): 트리 동일성 — 두 표본의 파일 집합(바이트)이 동일하지 않음.

    s02 에 여분 파일 추가 (recipe target·stamp 제외) → 트리 동일성 파손 → exit 3.
    """
    _require_substrate()
    root = build_shadow(tmp_path)
    # s02 에 여분 파일 넣기
    (root / "tests/fixtures/hollow-gate-corpus/s02/clean/extra.txt").write_text("extra\n")
    rc, _out, err = run_core(root, manifest=write_manifest(tmp_path / "m_prov_tree.yaml"))
    assert rc == 3, f"tree mismatch 미발동: rc={rc}\n{err}"
    assert "provenance 파손" in err and "트리 동일성" in err, \
        f"provenance tree 문면 미관측: {err}"


def test_ic1_probe_unit_arm_anchored_measurement(tmp_path):
    """IC-1 armL-anchored positive: probe unit 의 arm 라벨 측정 정상 (FIX-B).

    probe 정의역에서 armL-anchored 를 측정 (sample 정의역과 구분).
    정상 corpus 에서는 probe p01 이 declared_arm H(HOLLOW) 와 일치.
    """
    _require_substrate()
    rc, out, _err = run_core(REPO_ROOT)
    assert rc == 0, "baseline 이 FAIL 이면 ic 측정 불가"
    assert "::error::[IC-1]" not in out, "정상 corpus 에 IC-1 발동하면 측정 파손"


