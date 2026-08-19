"""CFP-2985 RTM 8.1.1 — AC-7 (1) · AC-8 (1) · AC-9 (2) · AC-10a (1) · AC-10b (2) 명명 테스트.

AC-7 · AC-8 = `declared` tier — **천장 문면 presence 만** 검사한다.
  ADR-145 CEILING 상 declared 는 Hop2/Hop3 강제 대상이 아니며, 여기 적힌 이름은 강제된 것이
  아니라 5.3 이 이미 규정한 presence 검사에 붙인 이름이다 (forged machine test 아님).
AC-9  = 자기적용 2-leg (leg-self 스캔 목록 등장 ∧ leg-live checker CI 실행).
AC-10a = baseline cut 선언 presence (Phase 1 문서 축 — Phase 2 산출물 미참조).
AC-10b = baseline 이 자기 Story 를 삼키지 않았는가 (자기면제 함정).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _cfp2985_spec as S  # noqa: E402

STORY_BASENAME = "CFP-2985.md"
BASELINE_REL = "scripts/section10-cause-baseline.txt"     # internal-docs D-8

_UNJUDGEABLE_RE = re.compile(r"(기계\s*판정\s*(불가|하지\s*않)|판정\s*불가|machine[- ]undecidable)")
_CLAIM_RE = re.compile(r"(전집합(임|이라고)?\s*(을|를)?\s*기계\s*판정|완전성을\s*기계\s*강제|"
                       r"100%\s*기계\s*강제|완전\s*봉인)")


def ceiling_statement_present(text, axis_tokens):
    """천장 문면 presence — 불가 선언 ∧ 축 토큰 ∧ **사유 본문** 을 같은 문장에서 보유한다.

    ADR-181 결정 6: `declared` 는 **왜 불가한지 사유 1줄 병기**가 부착 의무다.
    사유 없이 "불가" 만 적은 문면은 라벨 규율 미충족이므로 통과시키지 않는다.
    """
    if _CLAIM_RE.search(text):
        return False
    for sent in re.split(r"(?<=[.。\n])", text):
        if not _UNJUDGEABLE_RE.search(sent):
            continue
        if not any(tok in sent for tok in axis_tokens):
            continue
        tail = _UNJUDGEABLE_RE.split(sent, maxsplit=1)[-1]
        reason = re.sub(r"^[\s\-—–:·]*", "", tail).strip()
        if len(reason) >= 4:
            return True
    return False


def _ceiling_case(axis_tokens, reason):
    control = "본 항목은 기계 판정 불가 — %s. human/review-lane 판단으로 대체한다.\n" % reason
    # ★ 무관 문장 mutant 는 **축 토큰을 하나도 담지 않아야** 유효하다. 담으면 술어가 옳게
    #   True 를 내는데 그것을 "생존" 으로 읽어 정반대 결론에 이른다 (본 하네스가 1회 실측).
    neutral = "다른 무엇인가는 기계 판정 불가 — 근거가 없다.\n"
    assert not any(tok in neutral for tok in axis_tokens), (
        "무관 문장 mutant 가 축 토큰을 담았다 — 무효 mutant. 축=%r" % (axis_tokens,))
    mutants = [
        ("천장 문면 삭제", "본 항목은 리뷰 lane 이 본다.\n"),
        ("사유 없이 불가만", "본 항목은 기계 판정 불가.\n"),
        ("축 토큰 없는 일반 불가 문장", neutral),
        ("완전성 주장으로 대체", "본 항목은 %s 를 전집합임을 기계 판정한다.\n" % axis_tokens[0]),
        ("over-claim 어휘 혼입", control + "따라서 100% 기계 강제된다.\n"),
        ("공란", ""),
    ]
    green = [
        ("표기 변형 (판정 불가 : 사유)",
         "본 항목은 판정 불가 : %s (%s)\n" % (reason, axis_tokens[0])),
        ("사유가 길고 괄호 포함", control.replace(".", " (정규식 · AST · 의미).")),
    ]
    return control, mutants, green


def test_ac7_enumeration_completeness_ceiling_present():
    """AC-7 (declared) — "열거 site 집합이 전집합인지는 기계 판정 불가" 천장 문면이 실재한다.

    RTM: 5.3 verification "기계 판정 불가(class 동일성 술어가 결함마다 상이) ·
    천장 문면 presence 만 검사".
    """
    axis = ("열거", "전집합", "완전성", "site 집합")
    control, mutants, green = _ceiling_case(axis, "class 동일성 술어가 결함마다 상이하다 (열거·전집합)")
    S.assert_discriminating(lambda t: ceiling_statement_present(t, axis),
                            control, mutants, green, label="AC-7/ceiling-presence")

    adr = S.wrapper_text(S.ADR181_REL)
    assert "declared" in adr and "사유 1줄 병기" in adr, (
        "ADR-181 결정 6 의 `declared` 라벨 부착 의무(사유 1줄 병기) 문면이 부재 — "
        "천장 선언의 규범 근거가 없다")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    row = _ac_row(story, "AC-7")
    assert row, "Story 5.3 에서 AC-7 행을 찾지 못했다"
    assert ceiling_statement_present(" ".join(row), axis), (
        "Story 5.3 AC-7 행에 천장 문면(불가 선언 + 사유)이 없다")


def test_ac8_root_cause_truth_ceiling_present():
    """AC-8 (declared) — "기록된 원인 값이 실제 원인과 일치하는지는 기계 판정 불가" 천장이 실재한다.

    RTM: 5.3 verification "기계 판정 불가(오라클 부재 — `decided_by` 자기 증명) ·
    천장 문면 presence 만 검사".
    """
    axis = ("원인", "오라클", "decided_by", "진위")
    control, mutants, green = _ceiling_case(axis, "오라클 부재 — 원인 값을 쓰는 주체가 곧 decided_by 다")
    S.assert_discriminating(lambda t: ceiling_statement_present(t, axis),
                            control, mutants, green, label="AC-8/ceiling-presence")

    contract = S.wrapper_text(S.CONTRACT_FIX_EVENT_REL)
    assert "decided_by" in contract, (
        "계약 %s 에 `decided_by` 부재 — 자기 증명 천장의 지시 대상이 없다"
        % S.CONTRACT_FIX_EVENT_REL)

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    row = _ac_row(story, "AC-8")
    assert row, "Story 5.3 에서 AC-8 행을 찾지 못했다"
    assert ceiling_statement_present(" ".join(row), axis), (
        "Story 5.3 AC-8 행에 천장 문면(불가 선언 + 사유)이 없다")


# ---------------------------------------------------------------------------
# AC-9 — 자기적용 2-leg
# ---------------------------------------------------------------------------
def scan_list_covers(scan_list, target_basename=STORY_BASENAME):
    """leg-self — 스캔 목록에 대상 Story 가 **물리적으로 등장**하는가 (자기면제 탐지).

    경로 표기 변형(`./`, 절대·상대)에는 둔감하고, **목록에서 빠진 것**에만 반응한다.
    """
    for item in scan_list or []:
        name = str(item).replace("\\", "/").rstrip("/").split("/")[-1]
        if name == target_basename:
            return True
    return False


def test_ac9_leg_self_own_story_in_scan_list():
    """AC-9 leg-self — checker 스캔 목록에 본 Story 파일이 등장한다.

    RTM: 8.C "AC-9 자기적용 2-leg" 의 `leg-self`.
    자기면제(정의역에서 자기를 빼기)는 이 Story 가 겨냥한 결함 class 그 자체다.
    """
    control = ["wrapper/stories/CFP-1746.md", "wrapper/stories/CFP-2985.md",
               "wrapper/stories/CFP-966.md"]
    mutants = [
        ("자기 Story 를 목록에서 제외", [p for p in control if STORY_BASENAME not in p]),
        ("목록 자체가 빔", []),
        ("이름만 비슷한 파일로 대체",
         ["wrapper/stories/CFP-2985-notes.md", "wrapper/stories/CFP-966.md"]),
        ("디렉터리만 등재", ["wrapper/stories/"]),
    ]
    green = [
        ("절대 경로 표기", ["/x/y/wrapper/stories/CFP-2985.md"]),
        ("./ 접두 표기", ["./wrapper/stories/CFP-2985.md"]),
        ("역슬래시 경로", ["wrapper\\stories\\CFP-2985.md"]),
        ("목록 확장", control + ["wrapper/stories/CFP-2913.md"]),
    ]
    S.assert_discriminating(scan_list_covers, control, mutants, green,
                            label="AC-9/leg-self-scan-list")

    root = S.internal_docs_root()
    if root is None:
        return
    checker = root / "scripts" / "lib" / "check_story_section10_cause.py"
    assert checker.is_file(), (
        "internal-docs %s 부재 — Change Plan 5 D-7b(CausePolicy adapter) 미착지. "
        "스캔 목록을 산출할 주체가 없어 leg-self 를 실행으로 확인할 수 없다." % checker)
    rc, out, _ = S.run_rc([sys.executable, str(checker), "--list"], cwd=root)
    assert rc == 0, "checker --list rc=%d" % rc
    assert scan_list_covers(out.split()), (
        "checker 스캔 목록에 %s 부재 — 자기면제" % STORY_BASENAME)


def test_ac9_leg_live_checker_executed_in_ci():
    """AC-9 leg-live — checker 가 CI 에서 **실제로 실행**된다 (선언이 아니라 배선).

    RTM: 8.C "AC-9 자기적용 2-leg" 의 `leg-live`.
    이 Story 의 3회차 실패 지점이 정확히 여기다 — checker 는 있는데 CI 도달이 0 이었다.
    """
    ctl = ("name: x\non:\n  pull_request:\njobs:\n  fix-ledger-conformance:\n"
           "    runs-on: ubuntu-latest\n    steps:\n"
           "      - name: dep\n        run: pip install pyyaml\n"
           "      - name: run\n        run: bash scripts/check-adr-admission.sh\n")
    pred = lambda t: (S.wf_has_checker_invocation(t) and S.wf_no_continue_on_error(t)  # noqa: E731
                      and S.wf_no_path_filters(t))
    mutants = [
        ("호출 step 삭제",
         ctl.replace("      - name: run\n        run: bash scripts/check-adr-admission.sh\n", "")),
        ("호출을 echo 언급으로 강등",
         ctl.replace("run: bash scripts/check-adr-admission.sh",
                     "run: echo 'bash scripts/check-adr-admission.sh 는 나중에'")),
        ("호출을 주석 줄로 강등",
         ctl.replace("run: bash scripts/check-adr-admission.sh",
                     "run: '# bash scripts/check-adr-admission.sh'")),
        ("continue-on-error 로 tier 강등",
         ctl.replace("    runs-on: ubuntu-latest\n",
                     "    runs-on: ubuntu-latest\n    continue-on-error: true\n")),
        ("paths filter 로 대부분 PR 에서 미실행",
         ctl.replace("  pull_request:\n", "  pull_request:\n    paths:\n      - 'x/**'\n")),
    ]
    green = [
        ("step 이름 변경", ctl.replace("- name: run", "- name: admission")),
        ("python 진입점으로 등가 변경",
         ctl.replace("bash scripts/check-adr-admission.sh",
                     "python3 scripts/lib/check_adr_admission.py")),
    ]
    for nm, txt in mutants + green:
        assert txt != ctl, "mutant/변형 '%s' 주입 실패" % nm
    S.assert_discriminating(pred, ctl, mutants, green, label="AC-9/leg-live-ci")

    real = S.wrapper_text(S.CHECKER_WORKFLOW_REL)
    assert real is not None, (
        "%s 부재 — checker 의 CI 실행 채널 0. '선언은 있는데 강제가 없다' 의 재현이다."
        % S.CHECKER_WORKFLOW_REL)
    assert pred(real) is True, "%s 가 checker 를 실제로 실행하지 않는다" % S.CHECKER_WORKFLOW_REL


# ---------------------------------------------------------------------------
# AC-10a — baseline cut 선언
# ---------------------------------------------------------------------------
_CUT_ANCHOR_RE = re.compile(r"(baseline\s*cut|cut\s*기준|cut\s*시점|cut\s*시각)", re.I)


def cut_declaration_present(text):
    """cut 마커 앵커 ∧ SHA 40자 ∧ ISO 8601(KST offset) **3항 동시 충족**.

    하나라도 부재면 비-zero exit — **부분 선언은 거절**한다 (5.4 AC-10a mutant2).
    Phase 2 산출물을 참조하지 않는다 (Phase 1 에서 독립 판정 가능해야 vacuous 를 피한다).
    """
    if not _CUT_ANCHOR_RE.search(text):
        return False
    return bool(S.SHA40_RE.search(text)) and bool(S.ISO8601_KST_RE.search(text))


def test_ac10a_baseline_cut_marker_sha40_iso8601_present():
    """AC-10a — cut 선언이 앵커 + SHA 40자 + ISO 8601 을 **동시** 보유한다.

    RTM: 5.3 verification "cut 마커 앵커 정규식 ∧ SHA 40자 정규식 ∧ ISO 8601 정규식 3항
    동시 충족(단일 assert, 하나라도 부재 시 비-zero)".
    """
    control = ("| cut 기준 commit SHA (40자) | `%s` |\n"
               "| cut 시각 | `%s` |\n" % (S.CUT_SHA, S.CUT_TIME))
    mutants = [
        ("선언 전체 삭제", "| 항목 | 값 |\n"),
        ("앵커 문면만 제거", control.replace("cut 기준 commit SHA (40자)", "commit").replace(
            "cut 시각", "시각")),
        ("SHA 없이 시각만", "| cut 시각 | `%s` |\n" % S.CUT_TIME),
        ("시각 없이 SHA 만", "| cut 기준 commit SHA | `%s` |\n" % S.CUT_SHA),
        ("short SHA 로 축약", control.replace(S.CUT_SHA, S.CUT_SHA[:8])),
        ("offset 없는 시각", control.replace(S.CUT_TIME, "2026-08-16T18:06:03")),
        ("UTC offset (KST 아님)", control.replace(S.CUT_TIME, "2026-08-16T18:06:03+00:00")),
    ]
    green = [
        ("offset 콜론 없는 표기", control.replace("+09:00", "+0900")),
        ("앵커 표기 변형", control.replace("cut 기준 commit SHA (40자)", "baseline cut 기준 SHA")),
        ("주변 산문 추가", control + "\n귀결 — 본 Story 의 10 행은 전건 cut 이후다.\n"),
    ]
    for nm, txt in mutants + green:
        assert txt != control, "mutant/변형 '%s' 주입 실패" % nm
    S.assert_discriminating(cut_declaration_present, control, mutants, green,
                            label="AC-10a/cut-declaration")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    assert cut_declaration_present(story), (
        "Story 7.11 자기적용 baseline cut 선언(SHA 40자 + KST ISO 8601)이 부재")
    assert S.CUT_SHA in story, "선언된 cut SHA 가 %s 와 다르다" % S.CUT_SHA[:8]


# ---------------------------------------------------------------------------
# AC-10b — baseline 자기면제 함정
# ---------------------------------------------------------------------------
def baseline_excludes(entries, target_basename=STORY_BASENAME):
    """baseline entry 에 대상 Story path 가 **부재**한가. 경로 등가 표기에 둔감해야 한다."""
    for e in entries or []:
        path = str(e).split(":")[0].replace("\\", "/").rstrip("/")
        if path.split("/")[-1] == target_basename:
            return False
    return True


def test_ac10b_baseline_excludes_own_story_entry():
    """AC-10b leg1 — baseline 파일에 본 Story path entry 가 없다 (자기면제 함정 차단).

    RTM: 5.3 verification "baseline 파일 파싱 → 본 Story path entry 부재 assert".
    """
    control = ["wrapper/stories/CFP-1746.md:158", "wrapper/stories/CFP-966.md:12"]
    mutants = [
        ("본 Story entry 추가", control + ["wrapper/stories/CFP-2985.md:7"]),
        ("절대 경로 등가 표기로 추가", control + ["/repo/wrapper/stories/CFP-2985.md:7"]),
        ("./ 접두 등가 표기로 추가", control + ["./wrapper/stories/CFP-2985.md:7"]),
        ("역슬래시 등가 표기로 추가", control + ["wrapper\\stories\\CFP-2985.md:7"]),
    ]
    green = [
        ("무관 Story 추가", control + ["wrapper/stories/CFP-2913.md:5"]),
        ("이름이 겹치는 다른 파일", control + ["wrapper/stories/CFP-2985-followup.md:3"]),
        ("빈 baseline", []),
    ]
    S.assert_discriminating(baseline_excludes, control, mutants, green,
                            label="AC-10b/self-exemption")

    root = S.internal_docs_root()
    if root is None:
        return
    baseline = root / BASELINE_REL
    assert baseline.is_file(), (
        "internal-docs %s 부재 — Change Plan 5 D-8(baseline 생성) 미착지." % BASELINE_REL)
    entries = [ln.strip() for ln in baseline.read_text(encoding="utf-8").split("\n")
               if ln.strip() and not ln.strip().startswith("#")]
    assert baseline_excludes(entries), (
        "baseline 이 본 Story entry 를 포함 — Phase 1 위반이 동결되어 숨는다")


def test_ac10b_no_post_cut_row_in_baseline():
    """AC-10b leg2 — cut SHA 이후 append 된 행이 baseline 에 0건이다.

    RTM: 5.3 verification "cut SHA 기준 `git log` 대조로 cut 이후 행의 baseline 편입 0".
    기계화 형태 = baseline 이 인용하는 모든 파일이 **cut SHA 시점에 실재**해야 한다
    (cut 이후 생성분은 그 시점에 없으므로 편입될 수 없다).
    """
    at_cut = {"wrapper/stories/CFP-1746.md", "wrapper/stories/CFP-966.md"}

    def pred(entries):
        for e in entries or []:
            path = re.sub(r"^\./", "", str(e).split(":")[0].replace("\\", "/"))
            if path not in at_cut:
                return False
        return True

    control = ["wrapper/stories/CFP-1746.md:158", "wrapper/stories/CFP-966.md:12"]
    mutants = [
        ("cut 이후 생성 파일 편입", control + ["wrapper/stories/CFP-3001.md:4"]),
        ("본 Story (전건 cut 이후) 편입", control + ["wrapper/stories/CFP-2985.md:7"]),
        ("cut 시점 부재 경로", ["wrapper/stories/NEW.md:1"]),
    ]
    green = [
        ("./ 등가 표기", ["./wrapper/stories/CFP-1746.md:158"]),
        ("빈 baseline", []),
        ("같은 파일 다중 행", control + ["wrapper/stories/CFP-966.md:13"]),
    ]
    S.assert_discriminating(pred, control, mutants, green, label="AC-10b/post-cut-rows")

    root = S.internal_docs_root()
    if root is None:
        return
    baseline = root / BASELINE_REL
    assert baseline.is_file(), (
        "internal-docs %s 부재 — D-8 미착지, cut 대조 대상이 없다." % BASELINE_REL)
    bad = []
    for ln in baseline.read_text(encoding="utf-8").split("\n"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        path = re.sub(r"^\./", "", ln.split(":")[0].replace("\\", "/"))
        rc, _, _ = S.run_rc(["git", "cat-file", "-e", "%s:%s" % (S.CUT_SHA, path)], cwd=root)
        if rc != 0:
            bad.append(path)
    assert not bad, (
        "baseline 이 cut SHA %s 시점에 없던 경로를 편입: %s" % (S.CUT_SHA[:8], sorted(set(bad))))


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------
def _ac_row(story_text, ac_id):
    """Story 5.3 AC 표에서 해당 AC 행의 셀 목록. 못 찾으면 []."""
    for header, rows in S.md_tables(story_text):
        if S.col_index(header, "verification") < 0 and not any(
                "verification" in S.norm_header(h) for h in header):
            continue
        for cells in rows:
            if cells and S.norm_cell(cells[0]) == ac_id:
                return cells
    for header, rows in S.md_tables(story_text):
        for cells in rows:
            if cells and S.norm_cell(cells[0]) == ac_id and len(cells) >= 5:
                return cells
    return []
