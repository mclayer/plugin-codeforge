#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2944_form_set_parity_mutation_kill.py

CFP-2944 Phase 2 (구현) — D1 mutation-kill 검증 (AC-8).

계약 SSOT: Story CFP-2944 §7.12 Test Contract
  - D1: form-set 4면 동일성 — fence ↔ §결정7표 ↔ hook ch1 TEXT ↔ hook ch2 TEXT ↔ consumer-guide
  - AC-8: mutation-kill 실증 의무
  - §7.12.3 mutant 계획 + M-A5'

규범 SSOT: ADR-025 Amendment 4 (fence) + ADR-141 Amendment 8 (mirror)

테스트 원칙:
  - mutant 는 standing test 안에서 구성
  - RED→GREEN 둘 다 assert (동어반복 금지)
  - 절대수치 assert 금지 — INV-T6
  - 하드코딩 금지 — seam 파싱 사용

EXIT 계약:
  - 0 = PASS / 1 = 위반 / 2 = setup error
  - stdout distinct marker = `[form-set-parity] PASS|FAIL|setup error:…`
"""
import os
import sys
import tempfile
import subprocess
import importlib.util
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def _import_seam():
    """seam: scripts/lib/check_form_set_parity.py 동적 import."""
    root = Path(__file__).resolve().parents[2]
    seam_path = root / "scripts" / "lib" / "check_form_set_parity.py"
    spec = importlib.util.spec_from_file_location("check_form_set_parity", seam_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cfsp = _import_seam()


def repo_root() -> Path:
    """repo-root 탐색 (environment-agnostic)."""
    here = Path(__file__).resolve()
    candidate = here.parents[2]
    if (candidate / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md").is_file():
        return candidate
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=str(here.parent),
        )
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except Exception:
        pass
    return candidate


def run_parity_check(check_root: Path, args=None) -> tuple:
    """seam 실행 (check_form_set_parity.py).

    반환: (exit_code, stdout, stderr)
    Windows 인코딩 해결: PYTHONUTF8=1 + encoding UTF-8

    check_root: 검사할 repo root (ADR-025 파일이 있는 위치) — **cwd 로만** 준다.
      스크립트 자신은 항상 원본 repo 것을 쓴다(검사 대상 문면만 tmp 로 갈아끼우고 검사기는 고정).
    args: 스크립트에 넘길 위치 인자 (경로 인자 엣지 케이스용 — §8.8.1 미존재 경로·basename 불일치).
    """
    # 실제 원본 repo 의 스크립트 사용
    actual_root = repo_root()
    script = actual_root / "scripts" / "lib" / "check_form_set_parity.py"
    if not script.is_file():
        return 2, "", f"Script not found: {script}"

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = ["python3", str(script)]
    if args:
        cmd.extend(str(a) for a in args)

    try:
        # cwd 를 check_root 로 설정해 ADR-025 파일을 찾도록 함
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(check_root),
            env=env,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "Timeout"
    except Exception as e:
        return 2, "", str(e)


def materialize_surfaces(src_root: Path, dst_root: Path, adr_override=None, skip_adr=False):
    """`cfsp.SURFACES` 전건을 dst_root 로 복제 (면 경로 하드코딩 0 — SURFACES 파생).

    adr_override: ADR-025 사본 내용을 이 문자열로 대체 (mutant 주입).
    skip_adr: ADR-025 를 아예 복제하지 않는다 (부재 시뮬레이션).
    """
    adr_rel = cfsp.HOME_MARKER
    for surface in cfsp.SURFACES:
        rel = surface["path"]
        if rel == adr_rel and skip_adr:
            continue
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel == adr_rel and adr_override is not None:
            dst.write_text(adr_override, encoding="utf-8", newline="\n")
            continue
        src = src_root / rel
        if src.is_file():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")


def assert_variant_on_disk(tmpdir_p: Path, original: str, label: str):
    """디스크에 놓인 ADR 사본이 실제로 **변이본**인지 확인 (F-CL-007 강화층).

    구성 시점의 `mutant != original` 만으로는 못 잡는 사고가 따로 있다 — mutant 를 쓴 뒤
    surface 복제 루프가 **같은 경로를 원본으로 덮어써** 변이가 소실되는 순서 사고다.
    그 경우 검사는 pristine 문면을 보게 되고 "생존 기대" mutant 는 조용히 vacuous 해진다.
    따라서 실행 직전에 사용 지점(디스크)에서 확인한다.
    """
    on_disk = (tmpdir_p / cfsp.HOME_MARKER).read_text(encoding="utf-8")
    assert on_disk != original, (
        f"{label}: 디스크 사본이 원본과 동일 — 변이가 덮어쓰기로 소실됐다 (검사 정의역 이탈)"
    )


def run_vague_pause_check(root: Path) -> tuple:
    """vague_pause_taxonomy_presence 검사 실행.

    반환: (exit_code, stdout, stderr)
    """
    script = root / "scripts" / "lib" / "check_vague_pause_taxonomy_presence.py"
    if not script.is_file():
        return 2, "", f"Script not found: {script}"

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(root),
            env=env,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "Timeout"
    except Exception as e:
        return 2, "", str(e)


def test_form_set_parity_mutation_kill():
    """D1: form-set parity mutation-kill 검증 (필수 함수명 — RTM ac-traceability-matrix)

    - baseline GREEN 실증
    - seam self-test 위임
    - mutant discriminating 실증 (M-A1 주요 mutant)
    - M-A5' 알려진 생존자 박제
    - M-D1, M-N2, M-F1 엣지 mutant
    """
    root = repo_root()

    # ── 1. seam self-test 위임 ──
    actual_script = root / "scripts" / "lib" / "check_form_set_parity.py"
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            ["python3", str(actual_script), "--self-test"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(root), env=env, timeout=30
        )
        exit_code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except Exception as e:
        exit_code, stdout, stderr = 2, "", str(e)

    assert exit_code == 0, f"seam self-test RED: exit={exit_code}, stderr={stderr}\n{stdout}"
    assert "[self-test] PASS" in stdout, f"seam self-test 마커 부재: {stdout}"

    # ── 2. baseline GREEN (실제 repo) ──
    exit_baseline, stdout_baseline, stderr_baseline = run_parity_check(root)
    assert exit_baseline == 0, f"baseline RED: exit={exit_baseline}, stderr={stderr_baseline}\n{stdout_baseline}"
    assert cfsp.MARKER in stdout_baseline, f"baseline marker 부재: {stdout_baseline}"

    # ── 3. M-A1: form-set 4면 동일성 — 대조군 2×2 실증 ──
    # AC-8 핵심: 4면 검사 × (baseline / mutant) = 2×2 네 값 assert
    # 현행 lint(vague-pause) 가 mutant 에서 생존 → 신규 검사의 판별력이 필요함을 증명

    adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"
    if adr_src.is_file():
        adr_text = adr_src.read_text(encoding="utf-8")

        # ── 동적 form id 획득 (INV-T4 prepare) ──
        try:
            fence_baseline = cfsp.parse_fence(adr_text)
            assert len(fence_baseline) > 0, "fence must have entries"
        except Exception as e:
            raise AssertionError(f"M-A1 fence parse baseline failed: {e}")

        target_form_id = fence_baseline[0][0]  # 첫 form id (예: over-halt)

        # ── M-A1 mutant: fence 에서 target_form_id 행 삭제 ──
        # 패턴: target_form_id | <axis> 형식의 행을 fence 안에서 제거
        # 이렇게 하면 4면 검사에서 target_form_id 가 fence 에는 없지만 다른 면에는 있다는 위반 검출
        mutant_content = adr_text
        lines = mutant_content.split("\n")
        new_lines = []
        in_fence = False
        deleted_fence_entry = False
        for line in lines:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                new_lines.append(line)
                continue

            # fence 안에서 target_form_id 의 inventory 행 삭제 (1회)
            if (in_fence and not deleted_fence_entry and
                target_form_id in line and "|" in line and not line.strip().startswith("#")):
                # 이게 fence inventory 행인지 확인 (form_id | axis 형식)
                parts = line.split("|")
                if len(parts) >= 2 and parts[0].strip() == target_form_id:
                    deleted_fence_entry = True
                    continue  # 이 행 건너뜀

            new_lines.append(line)

        mutant_content = "\n".join(new_lines)
        assert deleted_fence_entry, (
            f"M-A1: fence 에서 `{target_form_id}` inventory 행을 찾지 못해 변이가 적용되지 않았다 "
            f"(fence 형식 drift) — 검사 정의역 이탈"
        )
        assert mutant_content != adr_text, "M-A1: 변이 미적용(앵커 drift) — 검사 정의역 이탈"

        # ── tmp 에 모든 surface 복제 (mutant ADR 포함) ──
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_p = Path(tmpdir)

            materialize_surfaces(root, tmpdir_p, adr_override=mutant_content)

            # ── 현행 lint 스크립트만 tmp 로 복제 ──
            # 비대칭 주의(F-CR-005): `run_parity_check` 는 **원본 repo 의 스크립트**를 쓰고 cwd 만
            # tmp 로 주므로 parity 스크립트 사본은 필요 없다(과거의 사본은 미사용 잔재였다).
            # 반면 `run_vague_pause_check` 는 넘겨받은 root 밑에서 스크립트를 찾으므로 사본이 필수다.
            for rel in ("scripts/lib/check_vague_pause_taxonomy_presence.py",):
                src_s = root / rel
                dst_s = tmpdir_p / rel
                dst_s.parent.mkdir(parents=True, exist_ok=True)
                dst_s.write_text(src_s.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")

            assert_variant_on_disk(tmpdir_p, adr_text, "M-A1")

            # ── 2×2 네 값 (검사 2종 × regime 2) ──
            # (1,1) 신규 검사 / baseline
            exit_parity_base, stdout_parity_base, _ = run_parity_check(root)
            assert exit_parity_base == 0, f"M-A1 (1,1): expected 0, got {exit_parity_base}"
            assert cfsp.MARKER in stdout_parity_base, "M-A1 (1,1): marker 부재"

            # (1,2) 신규 검사 / mutant — KILL
            exit_parity_mut, stdout_parity_mut, _ = run_parity_check(tmpdir_p)
            assert exit_parity_mut == 1, (
                f"M-A1 (1,2): 신규 검사가 form 삭제 mutant 를 죽여야 한다 "
                f"(expected exit 1, got {exit_parity_mut}). "
                f"2 = setup error 이며 kill 이 아니다. stdout={stdout_parity_mut}"
            )
            assert cfsp.MARKER in stdout_parity_mut, "M-A1 (1,2): marker 부재"

            # (2,1) 현행 lint / baseline
            exit_vague_base, _, _ = run_vague_pause_check(root)
            assert exit_vague_base == 0, f"M-A1 (2,1): expected 0, got {exit_vague_base}"

            # (2,2) 현행 lint / mutant — SURVIVE (판별력 0 대조군)
            # 현행 lint 는 taxonomy 라벨 3 리터럴 presence 만 보고 named 예시(form id)는 보지 않는다.
            # 따라서 같은 mutant 에서 살아남으며, 그 생존이 곧 "예시 축 판별력 0" 의 증거다.
            exit_vague_mut, _, _ = run_vague_pause_check(tmpdir_p)
            assert exit_vague_mut == 0, (
                f"M-A1 (2,2): 현행 lint 는 이 mutant 에서 생존해야 한다 "
                f"(expected exit 0, got {exit_vague_mut}) — 생존이 판별력 순증의 근거다"
            )

    # ── 4. M-A5': 알려진 생존자 박제 ──
    # anchor 규약 밖 bare 산문 토큰(form-id 형식이지만 backtick/괄호 없음)은 미탐됨
    # → 생존 (exit 0) 기대, 정직 천장 선언

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

        if adr_src.is_file():
            adr_text = adr_src.read_text(encoding="utf-8")

            # mutant: anchor 규약 밖 bare 산문에 form-id 형식 토큰을 §결정 7 region 안에 심는다.
            # **라인 단위 삽입**이어야 한다 — 과거 구현은 `find("## ", idx+1)` 로 삽입 지점을 잡았는데
            # 그 패턴은 `### 결정 7` 자신의 offset 1 에서 먼저 매칭돼(`###` 안에 `## ` 가 있다)
            # heading 을 `#` 와 `## 결정 7` 로 쪼갰다. 그러면 region heading 이 사라져
            # fail-closed(region 부재) exit 1 이 나며, 이는 "bare 토큰 미탐" 과 전혀 다른 사유다.
            fence_a5 = cfsp.parse_fence(adr_text)
            assert fence_a5, "M-A5' setup: fence 파싱 0행"
            bare_id = fence_a5[0][0] + "-phantom"
            a5_lines = []
            a5_inserted = False
            for line in adr_text.split("\n"):
                a5_lines.append(line)
                if not a5_inserted and line.startswith("### 결정 7"):
                    a5_lines.append(
                        f"Note: {bare_id} detection may miss bare text without anchor markers."
                    )
                    a5_inserted = True
            mutant_content = "\n".join(a5_lines)
            assert a5_inserted, "M-A5': `### 결정 7` heading 미발견 — 변이 미적용(앵커 drift)"
            assert mutant_content != adr_text, "M-A5': 변이 미적용(앵커 drift) — 검사 정의역 이탈"
            # 심은 토큰이 anchor 규약 **밖**임을 확정한다 (규약 안이면 생존 기대 자체가 틀린다).
            assert bare_id not in cfsp.extract_anchored_ids(mutant_content), (
                f"M-A5': 심은 토큰 `{bare_id}` 이 anchor 규약 안으로 추출됐다 — known-survivor 전제 붕괴"
            )

            # 순서 주의: ADR 은 override 로, 나머지 면은 원본으로 **한 번에** 놓는다.
            # (과거 구현은 mutant 를 먼저 쓰고 뒤이은 복제 루프가 그것을 원본으로 덮어써
            #  생존 assert 가 pristine 문면 위에서 vacuous 하게 통과했다.)
            materialize_surfaces(root, tmpdir_p, adr_override=mutant_content)
            assert_variant_on_disk(tmpdir_p, adr_text, "M-A5'")

            # M-A5': bare text 생존 (exit 0) — 정직 천장
            exit_m_a5_prime, stdout_m_a5_prime, _ = run_parity_check(tmpdir_p)
            assert exit_m_a5_prime == 0, (
                f"M-A5' (bare text): exit={exit_m_a5_prime}. "
                f"정직 천장: 방향 ② 는 anchor 규약(backtick/괄호) 준수면에만 검출. "
                f"규약 밖 bare 산문은 미탐 — 이는 설계의 intended 한계 (ADR-025 §A4-6 정직 천장)."
            )

    # ── 5. M-D1: fence 에 형식 미매칭 행 추가 → known-survivor (생존) ──
    # fence 는 `<form_id> | <axis>` 형식만 등재 → 형식 미매칭 행(`5-hour limit | unknown-axis`)은 무시
    # 따라서 이 mutant 는 fence 검사에서 위반 미검출 (known-survivor)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        adr_src = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

        if adr_src.is_file():
            adr_text = adr_src.read_text(encoding="utf-8")

            # fence 찾기
            fence_start = adr_text.find("```")
            fence_end = adr_text.find("```", fence_start + 1) if fence_start >= 0 else -1

            if fence_start >= 0 and fence_end > fence_start:
                # fence 블록 내부에 형식 미매칭 행 추가
                mutant_content = (
                    adr_text[:fence_end] +
                    "\n5-hour limit | unknown-axis | example\n" +
                    adr_text[fence_end:]
                )
            else:
                mutant_content = adr_text

            assert mutant_content != adr_text, (
                "M-D1: 변이 미적용 — fence 토큰 쌍 미발견(앵커 drift). 검사 정의역 이탈"
            )

            materialize_surfaces(root, tmpdir_p, adr_override=mutant_content)
            assert_variant_on_disk(tmpdir_p, adr_text, "M-D1")

            # M-D1: known-survivor (형식 미매칭 행은 파싱되지 않음)
            # fence 는 "형식이 맞는 행만" 파싱하므로 5-hour limit 은 inventory 에 추가되지 않음
            # 따라서 형식 미매칭 mutant 는 fence 관점에서는 기존과 동일 → 위반 미검출
            exit_m_d1, stdout_m_d1, _ = run_parity_check(tmpdir_p)
            assert exit_m_d1 == 0, (
                f"M-D1 known-survivor: 형식 미매칭 행은 fence 무시 → 기존 동일 (exit={exit_m_d1})"
            )

    # ── 6. M-N2: ADR-025 부재 → honest no-op ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        # ADR-025 파일을 복제하지 않음 (부재 시뮬레이션)
        materialize_surfaces(root, tmpdir_p, skip_adr=True)
        assert not (tmpdir_p / cfsp.HOME_MARKER).exists(), (
            "M-N2: 부재 시뮬레이션인데 ADR-025 사본이 존재한다 — 변이 미적용"
        )

        # M-N2: ADR-025 부재 시 honest no-op (exit 0)
        exit_m_n2, stdout_m_n2, _ = run_parity_check(tmpdir_p)
        assert exit_m_n2 == 0, (
            f"M-N2: ADR-025 부재 시 honest no-op 으로 exit==0 (exit={exit_m_n2})"
        )
        # marker 에 "no-op" 또는 "파일 부재" 포함
        assert cfsp.MARKER in stdout_m_n2, f"M-N2: marker 부재 {stdout_m_n2}"

    # ── 7. M-F1: fuzz 엣지 케이스 (§8.8.1 input_surface 선언 전건) ──
    # 선언(§8.8.1): 비-UTF8 · 8191/8192/8193자 라인 · fence 미닫힘 · 0byte · fence 0행 ·
    #   fence 중복 id · 미존재 경로 · basename 불일치
    # oracle(§8.8.1): uncaught traceback **0** ∧ exit ∈ {0,1,2} ∧ **그 exit 에 대응하는
    #   distinct marker 동반**. marker 동반이 필수인 이유 = traceback 발 exit 1 과 위반 exit 1 이
    #   종료 코드만으로는 구별 불가하기 때문이다. setup error marker 는 stderr 로 나가므로
    #   stdout+stderr 합에서 찾는다(선언이 "stdout/stderr marker" 라고 못박은 그대로).
    # pass_condition(§8.8.1) 기준값을 그대로 못박는다:
    #   비-UTF8 → 2 / 경로 미존재 → 2 / basename 불일치 → 0(honest no-op) /
    #   0byte·fence 0행 → 2 / fence 중복 id → 2 / 8193자 라인 → 정상 처리(0)
    #
    # 케이스 종류(kind):
    #   "adr-bytes"    ADR 사본을 raw bytes 로 기록 (다른 면 없음)
    #   "adr-text"     ADR 사본을 텍스트로 기록 (다른 면 없음 — setup 축에서 먼저 끊긴다)
    #   "adr-full"     ADR override + 4 면 전건 복제 (정상 처리 경로까지 도달해야 하는 케이스)
    #   "arg-missing"  존재하지 않는 **경로 인자**를 넘긴다 (파일을 만들지 않는다)
    #   "arg-basename" basename 이 다른 실재 파일을 경로 인자로 넘긴다
    #
    # 본 절은 자족적으로 문면을 다시 획득한다 (앞 절 분기 실행 여부에 의존하지 않는다).
    adr_src = root / cfsp.HOME_MARKER
    assert adr_src.is_file(), f"M-F1 setup: ADR-025 부재 — wrapper home 전제 불성립: {adr_src}"
    adr_text = adr_src.read_text(encoding="utf-8")

    # 합성 문면은 실 form id 를 쓰지 않는다 (INV-T5 동형 — tautological 방어).
    syn_unclosed = (
        "# 합성 ADR (M-F1 fence 미닫힘 (a)형 — 후속 ``` 전무)\n"
        "\n### 결정 7 — 합성\n\n```\nalpha-form | A2 | 합성 무발화 정지\n"
    )
    syn_dup_id = (
        "# 합성 ADR (M-F1 fence 중복 id)\n"
        "\n### 결정 7 — 합성\n\n```\nalpha-form | A2 | 합성 무발화 정지\n"
        "alpha-form | A1 | 합성 중복 등재\n```\n"
    )
    syn_no_fence = (
        "# 합성 ADR (M-F1 fence 0행 — inventory fence 자체가 없다)\n"
        "\n### 결정 7 — 합성\n\n표만 있고 form-set fence 가 없다.\n"
    )

    def _adr_with_long_line(width):
        """실 ADR 문면의 §결정 7 heading 직후에 `width` 길이 산문 라인 1개를 삽입."""
        out = []
        inserted = False
        for line in adr_text.split("\n"):
            out.append(line)
            if not inserted and line.startswith("### 결정 7"):
                out.append("a" * width)
                inserted = True
        assert inserted, "M-F1 long-line: `### 결정 7` heading 미발견 — 변이 미적용"
        return "\n".join(out)

    fuzz_cases = [
        # (name, kind, payload, expected_exit, expected_marker_fragment)
        ("non-utf8", "adr-bytes", b"\xff\xfe", 2, "setup error"),
        ("0byte-file", "adr-text", "", 2, "setup error"),
        ("fence-0-row", "adr-text", syn_no_fence, 2, "setup error"),
        ("fence-unclosed-a", "adr-text", syn_unclosed, 2, "setup error"),
        ("fence-dup-id", "adr-text", syn_dup_id, 2, "setup error"),
        ("long-line-8191", "adr-full", _adr_with_long_line(8191), 0, "PASS"),
        ("long-line-8192", "adr-full", _adr_with_long_line(8192), 0, "PASS"),
        ("long-line-8193", "adr-full", _adr_with_long_line(8193), 0, "PASS"),
        ("arg-path-not-exist", "arg-missing", None, 2, "setup error"),
        ("arg-basename-mismatch", "arg-basename", None, 0, "honest no-op"),
    ]

    for fuzz_name, kind, payload, expected_exit, expected_fragment in fuzz_cases:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_p = Path(tmpdir)
            adr_copy = tmpdir_p / cfsp.HOME_MARKER
            adr_copy.parent.mkdir(parents=True, exist_ok=True)
            call_args = None

            if kind == "adr-bytes":
                adr_copy.write_bytes(payload)
            elif kind == "adr-text":
                adr_copy.write_text(payload, encoding="utf-8", newline="\n")
            elif kind == "adr-full":
                materialize_surfaces(root, tmpdir_p, adr_override=payload)
                assert_variant_on_disk(tmpdir_p, adr_text, f"M-F1 {fuzz_name}")
            elif kind == "arg-missing":
                # 파일을 **만들지 않는다** — 실제로 존재하지 않는 경로를 인자로 넘긴다.
                missing = tmpdir_p / "archive" / "adr" / "no-such-adr-file.md"
                assert not missing.exists(), f"M-F1 {fuzz_name}: 경로가 존재하면 케이스가 성립하지 않는다"
                call_args = [missing]
            elif kind == "arg-basename":
                other = tmpdir_p / "archive" / "adr" / "NOT-THE-ADR-025-BASENAME.md"
                other.write_text("# basename 이 다른 실재 파일\n", encoding="utf-8", newline="\n")
                assert other.is_file() and other.name != cfsp.ADR025_BASENAME, (
                    f"M-F1 {fuzz_name}: 실재 ∧ basename 불일치 전제가 성립하지 않는다"
                )
                call_args = [other]
            else:  # pragma: no cover - 케이스 종류 오타 방어
                raise AssertionError(f"M-F1 {fuzz_name}: 알 수 없는 kind={kind}")

            exit_fuzz, stdout_fuzz, stderr_fuzz = run_parity_check(tmpdir_p, args=call_args)
            combined = (stdout_fuzz or "") + (stderr_fuzz or "")

            assert exit_fuzz == expected_exit, (
                f"M-F1 {fuzz_name}: 예상 exit={expected_exit}, 실제={exit_fuzz}. "
                f"stdout={stdout_fuzz}, stderr={stderr_fuzz}"
            )
            # oracle ①: uncaught traceback 0
            assert "Traceback (most recent call last)" not in (stderr_fuzz or ""), (
                f"M-F1 {fuzz_name}: uncaught traceback 검출 — 엣지가 예외로 새고 있다. stderr={stderr_fuzz}"
            )
            # oracle ②: distinct marker 동반 (종료 코드만으로 구별 불가한 축을 닫는다)
            assert cfsp.MARKER in combined, (
                f"M-F1 {fuzz_name}: distinct marker `{cfsp.MARKER}` 부재 — "
                f"traceback 발 종료와 정상 판정을 구별할 수 없다. stdout={stdout_fuzz}, stderr={stderr_fuzz}"
            )
            # oracle ③: 그 exit 에 **대응하는** marker 인지 (marker 만 있고 사유가 다른 경우 배제)
            assert expected_fragment in combined, (
                f"M-F1 {fuzz_name}: exit={exit_fuzz} 에 대응하는 marker 조각 `{expected_fragment}` 부재. "
                f"stdout={stdout_fuzz}, stderr={stderr_fuzz}"
            )

    print("[form-set-parity] PASS — mutation-kill 실증 완료 (M-A1 2×2 + M-A5' + M-D1 + M-N2 + M-F1 fuzz)")


if __name__ == "__main__":
    test_form_set_parity_mutation_kill()
