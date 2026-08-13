#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2944_form_record_structure.py

CFP-2944 Phase 2 (구현) — D2/D3 form-record 구조 검증 (AC-7a).

계약 SSOT: Story CFP-2944 §7.12 Test Contract
  - D2: form-record 구조 술어 — 각 form 행이 discriminant 3항 anchor + tier 라벨 보유
  - D3: negative-control presence — 각 신규 form 행(CFP-2944)에 정당 구분선
  - AC-7a: 신규 form 행이 ① 축별 discriminant 3항 ② tier 라벨 을 보유함을 assert
  - INV-T2: ∀ form: discriminant 3항 anchor + tier 라벨 보유

규범 SSOT: ADR-025 Amendment 4 §결정 7 표 구조 + ADR-025 §A4-2 discriminant 정의

RED 진정성 입증:
  - M-B1: fence 등재 첫 id 의 표 자기 행에서 첫 셀 anchor 제거 → D2 자기 행 부재 위반 검출
  - M-N1: 산문(§결정 7 heading)만 변경 → 위반 0 (오탐 방어)
  - M-E1: `check-tier-honesty.py` 의 lever registry 가 지목하는 **tier-선언 라인**에 긍정
    enforcement 토큰을 주입한 ADR-025 사본으로, 그 스크립트를 **실제로 실행**해
    baseline `exit 0` ↔ mutant `exit 1` 의 flip 을 assert 한다. 두 방향 모두 **정확한 값**에
    못박으므로 `X or <else 진입조건>` 형태의 항진 disjunct 가 없다.
    · 정의역: 스크립트가 lever artifact 경로를 **cwd 상대**로 해석하므로, registry 의 lever
      artifact 전건(스크립트 자신 포함 — 그것도 lever 다)을 tmpdir 로 복제한 뒤 cwd 를 그리로 준다.
      한 개만 복제하면 나머지 lever 부재로 baseline 도 RED 가 돼 판별이 성립하지 않는다.

변이 미적용 방어 (F-CL-007): 모든 mutant 구성 직후 `mutant != original` 을 못박는다.
  앵커 리터럴이 drift 하면 `replace` 가 no-op 이 되어 mutant == original 이 되고, 그때
  "kill 확인" assert 는 조용히 vacuous 해진다(거짓 음성). 본 파일의 mutant 앵커는 가능한 한
  fence 파싱·registry 에서 **동적 획득**하고, 그럼에도 남는 리터럴 앵커는 이 assert 로 막는다.

EXIT 계약:
  - 0 = PASS / 1 = 위반 / 2 = setup error
  - stdout distinct marker = `[form-record-structure] PASS|FAIL|setup error:…`
"""
import os
import sys
import subprocess
import importlib.util
import tempfile
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
    """repo-root 탐색."""
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


TIER_HONESTY_REL = os.path.join("scripts", "check-tier-honesty.py")


def import_tier_honesty():
    """seam: `scripts/check-tier-honesty.py` 동적 import.

    lever registry(`LEVERS`)·tier-선언 라인 discriminator(`label_re`)·긍정 enforcement
    토큰(`ENFORCEMENT_TOKENS`)을 **그 스크립트에서 그대로 가져오기** 위한 것이다.
    테스트가 같은 리터럴을 재기술하면 registry drift 시 mutant 가 조용히 빗나간다.
    module-level 부작용 0 (실행부는 `__main__` 가드 안).
    """
    path = repo_root() / TIER_HONESTY_REL
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("check_tier_honesty", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def materialize_levers(tier_honesty, src_root: Path, dst_root: Path, adr_basename, adr_override=None):
    """tier-honesty lever registry 의 artifact 전건을 dst_root 로 복제 (경로 하드코딩 0).

    `adr_override` 가 주어지면 ADR-025 lever 사본만 그 내용으로 대체한다.
    반환: 복제된 상대경로 집합.
    """
    copied = set()
    for lever in tier_honesty.LEVERS:
        rel = lever["artifact"]
        src = src_root / rel
        if not src.is_file():
            continue
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if adr_override is not None and Path(rel).name == adr_basename:
            dst.write_text(adr_override, encoding="utf-8", newline="\n")
        else:
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        copied.add(rel)
    return copied


def run_tier_honesty_check(root: Path) -> tuple:
    """`root` 를 cwd 로 삼아 그 안의 `check-tier-honesty.py` **사본**을 실행.

    스크립트는 lever artifact 를 cwd 상대 경로로 찾으므로, cwd = root 로 주면 root 에
    복제된 lever 사본 집합이 그대로 검사 정의역이 된다(원본 repo 미접촉).
    사본이 없으면 exit 2 로 **setup error 를 노출**한다 — 구 구현처럼 `0` 을 돌려주면
    "실행 불가" 가 "통과" 로 흡수돼 판별이 사라진다.

    반환: (exit_code, stdout, stderr)
    """
    script = root / TIER_HONESTY_REL
    if not script.is_file():
        return 2, "", f"[setup] lever 사본 부재 — 실행 불가: {script}"

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


def test_form_record_structure():
    """D2/D3: form-record 구조 검증 (필수 함수명 — RTM ac-traceability-matrix)

    Main entry point for AC-7a form record structure verification.
    seam API 사용 (자기 파서 재구현 금지).
    """
    root = repo_root()
    adr_file = root / "archive" / "adr" / "ADR-025-stop-discipline-non-whitelist-as-defect.md"

    if not adr_file.is_file():
        raise AssertionError(f"[form-record-structure] FAIL — ADR-025 not found: {adr_file}")

    adr_text = adr_file.read_text(encoding="utf-8")

    # ── D2/D3 검증: seam API 호출 (자기 파서 금지) ──
    violations = cfsp.check_row_structure(adr_text)

    assert violations == [], (
        f"[form-record-structure] FAIL — D2/D3 구조 위반: {violations}"
    )

    # ── M-B1 mutant: 표 첫 셀에서 form id anchor 제거 → D2 자기 행 부재 위반 ──
    # 대상 id·대상 행 모두 **fence 파싱 + seam 의 첫-셀 판정**으로 동적 획득한다(리터럴 0).
    # 치환어는 한글이라 anchor 추출 규약(소문자 kebab)에 걸리지 않는다 → anchor 소실이 확정된다.
    fence_rows = cfsp.parse_fence(adr_text)
    assert fence_rows, "M-B1 setup: fence 파싱 0행 — form-set SSOT 부재로 mutant 구성 불가"
    target_form_id = fence_rows[0][0]

    table_lines = [ln for ln in adr_text.split("\n") if ln.strip().startswith("|")]
    own_rows = [ln for ln in table_lines if target_form_id in cfsp.extract_anchored_ids(cfsp._first_cell(ln))]
    assert own_rows, (
        f"M-B1 setup: `{target_form_id}` 의 첫-셀 anchor 자기 행 미발견 (표 구조 drift) — 검사 정의역 이탈"
    )
    victim_row = own_rows[0]
    victim_first_cell = cfsp._first_cell(victim_row)
    scrubbed_row = victim_row.replace(
        victim_first_cell, victim_first_cell.replace(target_form_id, "앵커제거됨"), 1
    )
    mutant_b1 = adr_text.replace(victim_row, scrubbed_row, 1)
    assert mutant_b1 != adr_text, "M-B1: 변이 미적용(앵커 drift) — 검사 정의역 이탈"
    assert target_form_id not in cfsp.extract_anchored_ids(cfsp._first_cell(scrubbed_row)), (
        "M-B1: 첫 셀에서 anchor 가 실제로 제거되지 않음 — 변이 무효"
    )

    violations_b1 = cfsp.check_row_structure(mutant_b1)
    assert violations_b1, (
        f"M-B1: 첫 셀 anchor 제거 후에도 violations 비어있음. violations={violations_b1}"
    )
    assert any("자기 행 부재" in v for v in violations_b1), (
        f"M-B1: 예상된 '자기 행 부재' 메시지 없음. violations={violations_b1}"
    )

    # ── M-N1 mutant: 산문만 변경 → violations 여전히 빈 리스트 ──
    # 표 밖 heading 만 수정 (구조에 영향 없음). 앵커 = seam `decision7_table_region` 이 쓰는
    # region 시작 prefix 와 동일하므로 접미만 덧붙여 region 판정을 보존한다.
    region_heading_prefix = "### 결정 7"
    n1_lines = []
    n1_applied = False
    for line in adr_text.split("\n"):
        if not n1_applied and line.startswith(region_heading_prefix):
            line = line + " (M-N1 산문 변경 — 구조 무영향)"
            n1_applied = True
        n1_lines.append(line)
    mutant_n1 = "\n".join(n1_lines)
    assert n1_applied, f"M-N1: region heading `{region_heading_prefix}` 미발견 — 검사 정의역 이탈"
    assert mutant_n1 != adr_text, "M-N1: 변이 미적용(앵커 drift) — 검사 정의역 이탈"

    violations_n1 = cfsp.check_row_structure(mutant_n1)
    assert violations_n1 == [], (
        f"M-N1: 산문만 변경했는데 violations 발생 (오탐). violations={violations_n1}"
    )

    # ── M-E1 mutant: tier-선언 라인에 긍정 enforcement 토큰 주입 → tier-honesty RED ──
    # 지키는 것: ADR-025 의 form 행 tier 라벨은 `[advisory]` 이며 그 선언 라인에 긍정 enforcement
    # 언어가 섞이면 tier 거짓이다(ADR-144 §결정 7). 즉 D-GATE warning-tier 유지의 회귀 방어다.
    #
    # 판별 성립 조건 = baseline `exit 0` ↔ mutant `exit 1` **양방향 값 고정**.
    # 앵커(어느 라인이 tier 선언인가)와 payload(어떤 토큰이 위반인가)를 registry 에서 가져오므로
    # registry 가 바뀌면 mutant 가 빗나가는 대신 아래 setup assert 가 먼저 터진다.
    tier_honesty = import_tier_honesty()
    assert tier_honesty is not None, (
        f"M-E1 setup: `{TIER_HONESTY_REL}` 부재 — lever registry 획득 불가 (검사 정의역 이탈)"
    )

    vp_levers = [l for l in tier_honesty.LEVERS if Path(l["artifact"]).name == adr_file.name]
    assert vp_levers, (
        f"M-E1 setup: lever registry 에 `{adr_file.name}` artifact 가 없다 (registry drift)"
    )
    vp_lever = vp_levers[0]
    assert tier_honesty.ENFORCEMENT_TOKENS, "M-E1 setup: ENFORCEMENT_TOKENS 공집합 — payload 없음"
    payload_token = tier_honesty.ENFORCEMENT_TOKENS[0]

    e1_lines = []
    e1_applied = False
    for line in adr_text.split("\n"):
        m = vp_lever["label_re"].search(line)
        if not e1_applied and m:
            # 매칭 시작 지점(= tier 선언 앵커) 바로 앞에 주입 — 라인 선두에 가까워
            # 스크립트의 MAX_SCAN_LINE truncate 창 안에 확실히 들어간다.
            line = line[: m.start()] + payload_token + " " + line[m.start():]
            e1_applied = True
        e1_lines.append(line)
    mutant_e1 = "\n".join(e1_lines)
    assert e1_applied, (
        f"M-E1 setup: `{vp_lever['name']}` lever 의 tier-선언 라인 미발견 "
        f"(label_re drift) — 검사 정의역 이탈"
    )
    assert mutant_e1 != adr_text, "M-E1: 변이 미적용(앵커 drift) — 검사 정의역 이탈"

    with tempfile.TemporaryDirectory() as tmpdir:
        base_root = Path(tmpdir) / "baseline"
        mut_root = Path(tmpdir) / "mutant"

        copied_base = materialize_levers(tier_honesty, root, base_root, adr_file.name, None)
        copied_mut = materialize_levers(tier_honesty, root, mut_root, adr_file.name, mutant_e1)
        assert copied_base == copied_mut, (
            f"M-E1: baseline/mutant lever 정의역 불일치 — 두 실행이 비교 가능하지 않다. "
            f"base={sorted(copied_base)} mut={sorted(copied_mut)}"
        )
        assert vp_lever["artifact"] in copied_base and TIER_HONESTY_REL in copied_base, (
            f"M-E1: 필수 lever 사본 누락 (검사 대상 ADR 또는 실행 스크립트). copied={sorted(copied_base)}"
        )

        exit_base, stdout_base, stderr_base = run_tier_honesty_check(base_root)
        exit_mut, stdout_mut, stderr_mut = run_tier_honesty_check(mut_root)

        # (1) baseline GREEN — 변이 없는 사본 집합은 통과해야 한다.
        #     여기서 RED 가 나면 정의역 구성이 잘못된 것이지 mutant 가 잡힌 게 아니다.
        assert exit_base == 0, (
            f"M-E1 baseline: 변이 없는 lever 사본에서 exit 0 이어야 한다. "
            f"exit={exit_base}, stdout={stdout_base}, stderr={stderr_base}"
        )
        assert "[tier-honesty] PASS" in stdout_base, (
            f"M-E1 baseline: PASS marker 부재 — 실행이 성립하지 않았다. stdout={stdout_base}"
        )

        # (2) mutant RED — 정확히 exit 1(위반). 2(setup error)는 kill 이 아니다.
        assert exit_mut == 1, (
            f"M-E1 mutant: tier-선언 라인에 긍정 enforcement 토큰 `{payload_token}` 을 주입했으므로 "
            f"exit 1(위반)이어야 한다. 2 = setup error 이며 kill 이 아니다. "
            f"exit={exit_mut}, stdout={stdout_mut}, stderr={stderr_mut}"
        )
        assert "[tier-honesty] FAIL" in stdout_mut, (
            f"M-E1 mutant: FAIL marker 부재 — traceback 발 exit 와 구별 불가. stdout={stdout_mut}"
        )
        # 위반 **축**까지 지목 — 다른 사유(예: lever 부재 Axis1)로 우연히 RED 가 난 경우를 배제한다.
        assert "Axis2" in stdout_mut and payload_token in stdout_mut, (
            f"M-E1 mutant: 기대한 Axis2(enforcement 언어) 위반이 아니다 — 우연 RED 배제 실패. "
            f"stdout={stdout_mut}"
        )
        assert exit_base != exit_mut, "M-E1: baseline/mutant 종료코드 flip 부재 (판별력 0)"

    print("[form-record-structure] PASS — D2/D3 구조 검증 및 mutant 판별 완료 (M-B1 + M-N1 + M-E1)")


if __name__ == "__main__":
    test_form_record_structure()
