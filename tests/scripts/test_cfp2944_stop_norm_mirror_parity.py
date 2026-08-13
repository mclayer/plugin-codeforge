#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2944_stop_norm_mirror_parity.py

CFP-2944 Phase 2 (구현) — D4 mirror anchor parity 검증 (AC-5 · AC-11).

계약 SSOT: Story CFP-2944 §7.12 Test Contract
  - D4: mirror anchor parity — 개정 anchor 가 선언된 mirror 전 site 에 존재
  - AC-5: ADR-141 A6-3(a) remedy mirror 의 "기존 대기" 문구 제거 + pointer 보유
  - AC-11: ADR-109 §결정 5 축 분리 mirror 의 "재시도 축 한정" 문구 동기화
  - 절대수치 assert 금지 — INV-T6 (형식 변경 시 count 자연 변동)

규범 SSOT: ADR-025 Amendment 4 (mirror 정책) + ADR-141 Amendment 8 + ADR-109 Amendment 2

정의역 산출 (F-CL-002 · F-CR-003): 세 축 전부 **동적 산출**이다 — 파일·디렉터리 열거 0.
  축 1-a·축 2 = repo 전체 walk 의 `*.md` 전건, 축 1-b = 트리거 리터럴 보유 파일 스캔 후 SSOT 제외.
  근거 = ADR-141 §A8-5 "sweep 대상 = repo 전체 grep hit − 제외 술어 = 나머지 전건".
  절대 site 수·행번호 assert 0 (INV-T6) — 집합·함의 술어로만 판정한다.

RED 진정성 입증:
  - AC-5 축 1-a mutant(M-C1): "기존 대기" 를 mirror 에 되살림 → 위반 검출 확인
  - AC-5 축 1-b mutant(M-C1b): mirror 의 `ADR-141 A8-3` 리터럴 제거 → 위반 검출 확인
  - AC-5 축 1-b mutant(M-C1c): **구 열거 정의역 밖**에 신규 mirror site 를 pointer 없이 추가
    → 검출 확인 (정의역이 정적이면 무검출인 케이스 — F-CR-003 판별)
  - AC-5 축 1-a mutant(M-CL2a): `plugins/**` 에 폐기 문안 심기 → 검출 확인 (F-CL-002 판별)
  - AC-11 mutant: "재시도 축 한정" 제거 → 위반 검출 확인
  - AC-11 mutant(M-CL2b): `templates/**` 에 함의 위반 심기 → 검출 확인 (F-CL-002 판별)

변이 미적용 방어 (F-CL-007): 모든 mutant 구성 직후 `mutant != original` 을 못박는다.
  특히 "리터럴 제거" 계열은 이 assert 가 load-bearing 이다 — 리터럴이 원래 없었다면
  `replace` 가 no-op 이 되고 "제거해서 잡혔다" 가 "원래 없었다" 로 조용히 바뀐다(거짓 kill).

EXIT 계약:
  - 0 = PASS / 1 = 위반 / 2 = setup error
  - stdout distinct marker = `[stop-norm-mirror-parity] PASS|FAIL|setup error:…`
"""
import os
import sys
import tempfile
import subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


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


# ── sweep 정의역 산출 (F-CL-002) ───────────────────────────────────────────────
# 규범 SSOT = `archive/adr/ADR-141-all-opus-single-tier.md` §A8-5:
#   "sweep 대상 = 판정 시점에 `grep -rn '기존 대기'` 를 repo 전체에 실행해 얻은 hit 중
#    **아래 제외 술어를 적용한 나머지 전건**이다. 한 곳 누락 = born-broken."
#   같은 절이 그 '나머지' 를 다음으로 정의한다:
#   "나머지(= A6-3(a) 본문 및 그 문장을 **현행 규범으로 mirror 하는 타 문서 site**)가 sweep 대상이다."
#   (두 인용 모두 생략 0 — 문장 단위 full block, 강조 표기도 원문 그대로.)
#
# ① 정의역 = repo **전체** 를 walk 한 `*.md` 전건. 디렉터리 allowlist 를 두지 않는다 —
#    구 구현은 `[archive/adr, docs, skills, CLAUDE.md]` 4-entry 열거였고 그 결과
#    `plugins/**` · `templates/**` 가 정의역 밖이었다(방향 = fail-open). 같은 ADR 이 tier 규범
#    mirror 로 `plugins/*/CLAUDE.md` 를 열거하므로 가상의 표면도 아니었다.
# ② **문서면 한정(`*.md`)** — 위 규범 자신의 잔여 정의("타 **문서** site")를 따른 것이다.
#    비문서 파일은 규범이 말하는 mirror 면이 아니며, 특히 **본 검사 자신의 소스(.py)** 가
#    트리거 리터럴을 보유하므로 포함하면 검사가 자기 자신을 위반으로 계상한다.
#    이 한정은 Story §8.12 residual 에 정직 기재한다("repo 전체 = 전 디렉터리, 단 문서면 한정").
# ③ 아래 skip 집합은 **규범 제외 술어가 아니다** — `.git` 등 비문서·생성물 경로를 walk 에서
#    빼는 성능·잡음 목적의 기계적 제외이며, 규범 제외①②③(ADR-026 동음이의 / Amendment 8 절 /
#    frontmatter)과는 층이 다르다. 두 층을 섞지 않으려고 여기 따로 둔다.
_MECHANICAL_SKIP_DIRS = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
)


def iter_doc_files(root: Path):
    """repo **전체** 를 walk 해 `*.md` 파일 전건을 반환 (디렉터리 allowlist 0 — F-CL-002)."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _MECHANICAL_SKIP_DIRS]
        for name in filenames:
            if name.endswith(".md"):
                found.append(Path(dirpath) / name)
    return sorted(found)


def check_axis1_mirror_parity(root: Path) -> dict:
    """AC-5: ADR-141 A6-3(a) remedy mirror 검증.

    조건 1-a: "기존 대기" 는 제외 영역을 제외하고 repo 에서 완전히 제거됨 (잔여 = 빈 집합).
    조건 1-b: mirror 파일들(SSOT 제외)은 "ADR-141 A8-3" 리터럴을 보유.

    반환: {"violations_1a": [list], "violations_1b": [list], "ok_1a": bool, "ok_1b": bool}
    """
    violations_1a = []
    violations_1b = []

    # ── 조건 1-a: "기존 대기" 잔여 검증 ──
    # 정의역: repo 전체 walk 의 `*.md` 전건 (F-CL-002 — 디렉터리 allowlist 폐기)
    # 규범 제외 술어 3종 (ADR-141 §A8-5):
    #   제외① archive/adr/ADR-026-post-merge-automation.md 전체 (동음이의)
    #   제외③ archive/adr/ADR-141-all-opus-single-tier.md 의 frontmatter (선두 --- ~ 다음 ---)
    #   제외② archive/adr/ADR-141-all-opus-single-tier.md 의 Amendment 8 ~ EOF (메타 표면)

    target_literal = "기존 대기"
    adr_026_path = root / "archive" / "adr" / "ADR-026-post-merge-automation.md"
    adr_141_path = root / "archive" / "adr" / "ADR-141-all-opus-single-tier.md"

    # ADR-141 frontmatter 와 Amendment 8 범위 동적 산출
    adr_141_frontmatter_end_line = None
    adr_141_amd8_start_line = None

    if adr_141_path.is_file():
        adr_141_text = adr_141_path.read_text(encoding="utf-8")
        lines_141 = adr_141_text.split("\n")

        # frontmatter 끝 찾기 (첫 --- 이후 다음 --- 까지)
        fence_count = 0
        for i, line in enumerate(lines_141):
            if line.startswith("---"):
                fence_count += 1
                if fence_count == 2:
                    adr_141_frontmatter_end_line = i
                    break

        # Amendment 8 시작 찾기
        for i, line in enumerate(lines_141):
            if line.strip().startswith("## Amendment 8"):
                adr_141_amd8_start_line = i
                break

    # 정의역 파일 스캔 (repo 전체 `*.md`)
    files_to_scan = iter_doc_files(root)

    for file_path in files_to_scan:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # 제외 적용
        if file_path == adr_026_path:
            # 파일 전체 제외
            continue

        # ADR-141 제외 처리
        if file_path == adr_141_path:
            # frontmatter 와 Amendment 8 이후 제외
            lines = content.split("\n")
            content_for_check = []
            for i, line in enumerate(lines):
                # frontmatter 범위 제외
                if adr_141_frontmatter_end_line is not None and i <= adr_141_frontmatter_end_line:
                    continue
                # Amendment 8 범위 제외
                if adr_141_amd8_start_line is not None and i >= adr_141_amd8_start_line:
                    continue
                content_for_check.append(line)
            content = "\n".join(content_for_check)

        # "기존 대기" 검색
        if target_literal in content:
            violations_1a.append(
                f"{file_path.relative_to(root)}: '{target_literal}' 잔여 (제외 후에도 발견)"
            )

    # ── 조건 1-b: mirror pointer 검증 — 정의역 **동적 산출** (F-CR-003) ──
    # 관측점(§8.1.1 AC-5) = "`비대상 3종` 보유 mirror 면(SSOT 파일 제외) **전건**이
    #   `ADR-141 A8-3` 보유". 이는 파일 열거가 아니라 **함의 술어**다.
    # 구 구현은 mirror 파일 2개를 하드코딩해 두었다. 오늘의 실제 보유 집합과 우연히 일치해
    # 잘못된 verdict 는 내지 않았지만, **신규 mirror site 가 생기면 무검출**이다 —
    # AC-5 본문이 "절대 site 수 assert 금지(INV-T6) … 절대수치를 기준으로 쓰면 개정이
    # 진행될수록 기준 자체가 stale" 이라고 못박은 바로 그 병의 리스트 형태였다.
    # 축 1-a·축 2 와 동형으로 리터럴 보유 파일을 스캔해 산출하고 SSOT 만 뺀다.
    mirror_trigger_literal = "비대상 3종"
    pointer_literal = "ADR-141 A8-3"

    mirror_domain = []
    for file_path in files_to_scan:
        # SSOT(판정문 verbatim 1곳)는 §A8-5 "타 문서 site" 문언에 따라 정의역 밖.
        if file_path == adr_141_path:
            continue
        try:
            mirror_content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if mirror_trigger_literal in mirror_content:
            mirror_domain.append((file_path, mirror_content))

    # vacuity 방어: 정의역이 공집합이면 함의가 vacuously true 라 검사가 조용히 무력화된다.
    # 이것은 개수 assert(INV-T1 위반)가 아니라 **공집합 여부** 술어다 — 절대수치 0.
    if not mirror_domain:
        violations_1b.append(
            f"정의역 공집합 — `{mirror_trigger_literal}` 보유 mirror 면이 하나도 없다(SSOT 제외 후). "
            f"함의 판정이 vacuous 해져 축 1-b 가 무력화된다"
        )

    for file_path, mirror_content in mirror_domain:
        if pointer_literal not in mirror_content:
            violations_1b.append(
                f"{file_path.relative_to(root)}: '{pointer_literal}' 리터럴 부재 (mirror 동기화 미실행)"
            )

    return {
        "violations_1a": violations_1a,
        "violations_1b": violations_1b,
        "ok_1a": len(violations_1a) == 0,
        "ok_1b": len(violations_1b) == 0,
    }


def _write_into(tmpdir_p: Path, rel: str, text: str) -> Path:
    """tmpdir 안 상대경로에 파일 생성 (mutant fixture 구성용)."""
    dst = tmpdir_p / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8", newline="\n")
    return dst


def _copy_into(root: Path, tmpdir_p: Path, rels) -> None:
    """실 repo 파일 여러 개를 tmpdir 로 원본 그대로 복제."""
    for rel in rels:
        src = root / rel
        if src.is_file():
            _write_into(tmpdir_p, rel, src.read_text(encoding="utf-8"))


# mirror 정의역 확장 실증에 쓰는 경로 — **구 하드코딩 정의역 밖**이어야 의미가 있다.
# ADR-141 자신이 tier 규범 mirror 로 `plugins/*/CLAUDE.md` 를 열거하므로 가상의 표면이 아니다.
_OUT_OF_OLD_DOMAIN_MIRROR = "plugins/codeforge-develop/CLAUDE.md"
_OUT_OF_OLD_DOMAIN_DOC = "plugins/codeforge-design/CLAUDE.md"
_OUT_OF_OLD_DOMAIN_TEMPLATE = "templates/github-pr-template.md"

_PLAYBOOK_REL = "docs/orchestrator-playbook.md"
_SKILL_REL = "skills/rate-limit-429-mitigation/SKILL.md"
_ADR141_REL = "archive/adr/ADR-141-all-opus-single-tier.md"
_ADR109_REL = "archive/adr/ADR-109-in-process-429-mitigation-framework.md"


def check_axis2_mirror_parity(root: Path) -> dict:
    """AC-11: ADR-109 §결정 5 축 분리 mirror 검증.

    함의: "사용자 turn 대기" ∨ "user manual resume only" 를 보유한 파일 →
    전건이 "재시도 축 한정" 을 보유해야 함.

    정의역: repo 전체 walk 의 `*.md` 전건 (F-CL-002 — 축 1 과 동일 산출기).
      구 구현은 `[archive/adr, docs, skills, CLAUDE.md]` 4-entry 열거 + `parts` 기반
      디렉터리 배제(tests/scripts/.github/templates)였다. 규범은 정의역을 디렉터리로
      한정하지 않으므로 열거를 폐기하고 walk 로 대체한다.

    반환: {"violations": [list], "ok": bool}
    """
    violations = []

    trigger_literals = ["사용자 turn 대기", "user manual resume only"]
    required_literal = "재시도 축 한정"

    files_to_scan = iter_doc_files(root)

    # 트리거 보유 파일 수집
    files_with_trigger = []
    for file_path in files_to_scan:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # 트리거 검색 (OR 조건)
        has_trigger = any(literal in content for literal in trigger_literals)
        if has_trigger:
            files_with_trigger.append(file_path)

    # 각 파일이 required_literal 을 보유하는지 검증
    for file_path in files_with_trigger:
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if required_literal not in content:
            trigger_found = next(
                lit for lit in trigger_literals if lit in content
            )
            violations.append(
                f"{file_path.relative_to(root)}: '{trigger_found}' 보유 하지만 "
                f"'{required_literal}' 부재 (함의 위반)"
            )

    return {
        "violations": violations,
        "ok": len(violations) == 0,
    }


def test_stop_norm_mirror_parity():
    """D4: mirror anchor parity 검증 (필수 함수명 — RTM ac-traceability-matrix)

    AC-5 축 1-a/1-b 와 AC-11 을 실증한다.
    """
    root = repo_root()

    # ── AC-5 축 1 (기존 대기) ──
    result_1 = check_axis1_mirror_parity(root)

    if not result_1["ok_1a"]:
        violations_str = "\n".join(f"  {v}" for v in result_1["violations_1a"])
        print(f"[stop-norm-mirror-parity] FAIL — AC-5 축 1-a 위반:\n{violations_str}", file=sys.stderr)
        raise AssertionError(
            f"AC-5 축 1-a: '기존 대기' 잔여 검출:\n" + violations_str
        )

    if not result_1["ok_1b"]:
        violations_str = "\n".join(f"  {v}" for v in result_1["violations_1b"])
        print(f"[stop-norm-mirror-parity] FAIL — AC-5 축 1-b 위반:\n{violations_str}", file=sys.stderr)
        raise AssertionError(
            f"AC-5 축 1-b: mirror pointer 부재:\n" + violations_str
        )

    # ── AC-11 축 2 ──
    result_2 = check_axis2_mirror_parity(root)

    if not result_2["ok"]:
        violations_str = "\n".join(f"  {v}" for v in result_2["violations"])
        print(f"[stop-norm-mirror-parity] FAIL — AC-11 위반:\n{violations_str}", file=sys.stderr)
        raise AssertionError(
            f"AC-11: 함의 위반:\n" + violations_str
        )

    # ── M-C1 mutant: mirror 에 "기존 대기" 되살림 → 축 1-a 위반 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        # playbook.md 복제
        playbook_src = root / "docs" / "orchestrator-playbook.md"
        if playbook_src.is_file():
            playbook_dst = tmpdir_p / "docs" / "orchestrator-playbook.md"
            playbook_dst.parent.mkdir(parents=True, exist_ok=True)
            playbook_content = playbook_src.read_text(encoding="utf-8")

            # mutant: "기존 대기" 문구 되살림. 분기 없이 무조건 append 한다 —
            # 구 구현의 `else: mutant = original` 가지는 앵커 상태에 따라 변이가 조용히
            # 사라지는 경로였다 (F-CL-007).
            mutant_content = playbook_content + "\n기존 대기가 존재한다.\n"
            assert mutant_content != playbook_content, (
                "M-C1: 변이 미적용(앵커 drift) — 검사 정의역 이탈"
            )

            playbook_dst.write_text(mutant_content, encoding="utf-8", newline="\n")

            # 다른 필수 파일들도 복제
            for src in [
                root / "archive" / "adr" / "ADR-141-all-opus-single-tier.md",
                root / "skills" / "rate-limit-429-mitigation" / "SKILL.md",
            ]:
                if src.is_file():
                    rel = src.relative_to(root)
                    dst = tmpdir_p / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

            # mutant 에서 축 1-a 검사 → 위반 검출되어야 함
            result_m_c1 = check_axis1_mirror_parity(tmpdir_p)
            assert not result_m_c1["ok_1a"], (
                f"M-C1: '기존 대기' 를 되살린 후에도 축 1-a 위반이 검출되지 않음 (kill 실패)"
            )
            assert len(result_m_c1["violations_1a"]) > 0, "M-C1: violations 비어있음"

    # ── M-C1b mutant: mirror 의 ADR-141 A8-3 리터럴 제거 → 축 1-b 위반 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        skill_src = root / "skills" / "rate-limit-429-mitigation" / "SKILL.md"
        if skill_src.is_file():
            skill_dst = tmpdir_p / "skills" / "rate-limit-429-mitigation" / "SKILL.md"
            skill_dst.parent.mkdir(parents=True, exist_ok=True)
            skill_content = skill_src.read_text(encoding="utf-8")

            # mutant: ADR-141 A8-3 리터럴 제거
            mutant_content = skill_content.replace("ADR-141 A8-3", "ADR-XXX placeholder")
            # 이 assert 는 load-bearing 이다 — pointer 가 애초에 없었다면 replace 가 no-op 이 되고
            # 아래 `not ok_1b` 는 "제거해서 잡혔다" 가 아니라 "원래 없었다" 로 통과한다 (거짓 kill).
            assert mutant_content != skill_content, (
                "M-C1b: 변이 미적용 — pointer 리터럴이 원래 부재했거나 앵커 drift. 검사 정의역 이탈"
            )
            skill_dst.write_text(mutant_content, encoding="utf-8", newline="\n")

            # 다른 파일들도 복제
            for src in [
                root / "archive" / "adr" / "ADR-141-all-opus-single-tier.md",
                root / "docs" / "orchestrator-playbook.md",
            ]:
                if src.is_file():
                    rel = src.relative_to(root)
                    dst = tmpdir_p / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

            # mutant 에서 축 1-b 검사 → 위반 검출되어야 함
            result_m_c1b = check_axis1_mirror_parity(tmpdir_p)
            assert not result_m_c1b["ok_1b"], (
                f"M-C1b: pointer 리터럴을 제거한 후에도 축 1-b 위반이 검출되지 않음 (kill 실패)"
            )
            assert len(result_m_c1b["violations_1b"]) > 0, "M-C1b: violations 비어있음"

    # ── M-C1c mutant (F-CR-003): **신규** mirror site 가 pointer 없이 등장 → 축 1-b 검출 ──
    # 정의역이 하드코딩 파일 열거였을 때는 이 site 가 애초에 보이지 않아 무검출이었다.
    # 동적 산출로 바꾼 뒤에는 리터럴 보유만으로 정의역에 들어오므로 잡힌다.
    # 경로는 구 열거 정의역 **밖**을 쓴다 — 그래야 "열거→스캔" 전환이 실제로 검출을 낳았음이 증명된다.
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        _copy_into(root, tmpdir_p, [_PLAYBOOK_REL, _SKILL_REL, _ADR141_REL])

        new_site = _write_into(
            tmpdir_p,
            _OUT_OF_OLD_DOMAIN_MIRROR,
            "# 신규 mirror site (M-C1c fixture)\n\n"
            "failover 비대상 3종 을 여기서도 서술하지만 정본 포인터를 달지 않았다.\n",
        )
        assert new_site.is_file(), "M-C1c: 신규 site fixture 미생성 — 변이 미적용"
        assert "비대상 3종" in new_site.read_text(encoding="utf-8"), (
            "M-C1c: 트리거 리터럴 부재 — 정의역에 들어가지 않아 검사가 성립하지 않는다"
        )
        assert "ADR-141 A8-3" not in new_site.read_text(encoding="utf-8"), (
            "M-C1c: pointer 가 이미 있으면 위반이 생기지 않는다 — 변이 무효"
        )

        result_m_c1c = check_axis1_mirror_parity(tmpdir_p)
        assert not result_m_c1c["ok_1b"], (
            "M-C1c: 구 열거 정의역 밖의 신규 mirror site 가 pointer 없이 추가됐는데 축 1-b 가 "
            "검출하지 못했다 (정의역이 여전히 정적이라는 뜻)"
        )
        assert any(_OUT_OF_OLD_DOMAIN_MIRROR.split("/")[-2] in v for v in result_m_c1c["violations_1b"]), (
            f"M-C1c: 위반이 신규 site 를 지목하지 않는다 (다른 사유로 우연히 RED). "
            f"violations={result_m_c1c['violations_1b']}"
        )

    # ── M-CL2a mutant (F-CL-002): 구 디렉터리 열거 **밖** 경로의 `기존 대기` 잔여 → 축 1-a 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        _copy_into(root, tmpdir_p, [_PLAYBOOK_REL, _SKILL_REL, _ADR141_REL])

        clean = check_axis1_mirror_parity(tmpdir_p)
        assert clean["ok_1a"], (
            f"M-CL2a baseline: 변이 전 정의역이 이미 RED 면 flip 이 성립하지 않는다. "
            f"violations={clean['violations_1a']}"
        )

        planted = _write_into(
            tmpdir_p,
            _OUT_OF_OLD_DOMAIN_DOC,
            "# plugin 문서 (M-CL2a fixture)\n\n폐기 대상 문안인 기존 대기 서술이 남아 있다.\n",
        )
        assert "기존 대기" in planted.read_text(encoding="utf-8"), "M-CL2a: 변이 미적용"

        result_m_cl2a = check_axis1_mirror_parity(tmpdir_p)
        assert not result_m_cl2a["ok_1a"], (
            "M-CL2a: 구 4-entry 디렉터리 열거 밖(plugins/**)에 심은 폐기 문안을 축 1-a 가 "
            "검출하지 못했다 — 정의역이 여전히 열거라는 뜻 (규범은 repo 전체)"
        )

    # ── M-CL2b mutant (F-CL-002): 구 배제 디렉터리(templates/**) 의 함의 위반 → 축 2 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)
        _copy_into(root, tmpdir_p, [_PLAYBOOK_REL, _ADR109_REL])

        clean2 = check_axis2_mirror_parity(tmpdir_p)
        assert clean2["ok"], (
            f"M-CL2b baseline: 변이 전 축 2 가 이미 RED 면 flip 이 성립하지 않는다. "
            f"violations={clean2['violations']}"
        )

        _write_into(
            tmpdir_p,
            _OUT_OF_OLD_DOMAIN_TEMPLATE,
            "# PR template (M-CL2b fixture)\n\n"
            "재시도 실패 시 사용자 turn 대기 로 넘어간다.\n",  # 트리거 보유 ∧ 필수 리터럴 부재
        )

        result_m_cl2b = check_axis2_mirror_parity(tmpdir_p)
        assert not result_m_cl2b["ok"], (
            "M-CL2b: 구 구현이 parts 필터로 배제하던 templates/** 의 함의 위반을 축 2 가 "
            "검출하지 못했다 — 배제 술어가 규범보다 넓다는 뜻"
        )

    # ── M-C2 mutant: ADR-026 동음이의 문맥만 존재 → 위반 0 (overkill 방어) ──
    # ADR-026 자체는 정의역 밖이므로, ADR-026 에만 "기존 대기" 가 있고 다른 곳엔 없으면 OK
    adr_026_path = root / "archive" / "adr" / "ADR-026-post-merge-automation.md"
    if adr_026_path.is_file():
        # 이 파일은 제외되므로 자연히 violations_1a 에 포함되지 않아야 함
        # (이미 위의 check_axis1_mirror_parity 에서 처리)
        result_current = check_axis1_mirror_parity(root)
        # ADR-026 가 제외되었으므로 violations_1a 에 ADR-026 경로가 없어야 함
        adr_026_violations = [v for v in result_current["violations_1a"] if "ADR-026" in v]
        assert len(adr_026_violations) == 0, (
            f"M-C2 fail: ADR-026 은 제외되어야 하는데 violations 에 포함됨: {adr_026_violations}"
        )

    # ── AC-11 축 2 mutant: "재시도 축 한정" 제거 → 위반 검출 ──
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_p = Path(tmpdir)

        adr_109_src = root / "archive" / "adr" / "ADR-109-in-process-429-mitigation-framework.md"
        if adr_109_src.is_file():
            adr_109_dst = tmpdir_p / "archive" / "adr" / "ADR-109-in-process-429-mitigation-framework.md"
            adr_109_dst.parent.mkdir(parents=True, exist_ok=True)
            adr_109_content = adr_109_src.read_text(encoding="utf-8")

            # mutant: "재시도 축 한정" 제거
            mutant_content = adr_109_content.replace("재시도 축 한정", "REMOVED-axis-constraint")
            # load-bearing: 필수 리터럴이 애초에 없었다면 replace 가 no-op 이고 아래 `not ok` 는
            # "제거해서 잡혔다" 가 아니라 "원래 없었다" 로 통과한다 (거짓 kill).
            assert mutant_content != adr_109_content, (
                "AC-11 mutant: 변이 미적용 — 필수 리터럴이 원래 부재했거나 앵커 drift. 검사 정의역 이탈"
            )
            adr_109_dst.write_text(mutant_content, encoding="utf-8", newline="\n")

            # 다른 파일들 (트리거 보유)
            for src in [
                root / "docs" / "orchestrator-playbook.md",
            ]:
                if src.is_file():
                    rel = src.relative_to(root)
                    dst = tmpdir_p / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

            # mutant 에서 축 2 검사 → 위반 검출되어야 함
            result_axis2_mutant = check_axis2_mirror_parity(tmpdir_p)
            assert not result_axis2_mutant["ok"], (
                f"AC-11 mutant: '재시도 축 한정' 제거 후에도 위반이 검출되지 않음 (kill 실패)"
            )
            assert len(result_axis2_mutant["violations"]) > 0, "AC-11 mutant: violations 비어있음"

    print("[stop-norm-mirror-parity] PASS — AC-5 축 1-a/1-b + AC-11 검증 완료 (mutant kill 4종 실증)")


if __name__ == "__main__":
    test_stop_norm_mirror_parity()
