"""CFP-2985 RTM 8.1.1 — AC-3 (3) · AC-4 (2) · AC-5 (2) · AC-6 (1) 명명 테스트.

AC-3 = 8.C CI 실행 보장 계약 (C-1~C-5) 의 YAML 축.
AC-4 = 검증 정의역 선언 presence + 공허 값 배제.
AC-5 = 열거 산출 명령 schema + 열거 site path resolve.
AC-6 = 열거 site mutation 전건 RED (실 site 에 실제로 주입해서 판정한다).
"""

import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import _cfp2985_spec as S  # noqa: E402

# Change Plan 5 D-10 — checker 를 호출하는 workflow (job name `fix-ledger-conformance`).
CHECKER_WORKFLOW_REL = S.CHECKER_WORKFLOW_REL

# 본 스위트를 부르는 workflow (8.C 를 스위트 자신에 적용 — "존재하는데 실행되지 않으면 dead test").
SUITE_WORKFLOW_REL = ".github/workflows/cfp2985-rtm-contract-test.yml"


# ---------------------------------------------------------------------------
# AC-3 술어 — 8.C C-1 ~ C-5  (단일 정의처 = _cfp2985_spec, AC-9 와 공용)
# ---------------------------------------------------------------------------
wf_has_checker_invocation = S.wf_has_checker_invocation
wf_has_dependency_resolution = S.wf_has_dependency_resolution
wf_no_continue_on_error = S.wf_no_continue_on_error
wf_no_path_filters = S.wf_no_path_filters
wf_job_if_always_reports = S.wf_job_if_always_reports
wf_invocation_contract = S.wf_invocation_contract


_WF_CONTROL = """name: fix ledger conformance
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  fix-ledger-conformance:
    if: github.repository == 'mclayer/plugin-codeforge'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install test dependencies
        run: pip install pyyaml pytest
      - name: Run admission checker
        run: bash scripts/check-adr-admission.sh --phase 2
"""


def test_ac3_workflow_yaml_invocation_contract():
    """AC-3 leg1 — checker 호출 workflow 가 C-1~C-4 를 동시 충족한다.

    RTM: 5.3 verification "workflow YAML assert(호출 step ∧ install step ∧
    `continue-on-error` 부재 ∧ `paths`·`paths-ignore` 부재 ∧ job `if:`)" ⊕ 8.C C-1~C-5.
    mutant 는 **C 항목별로 개별** 주입한다 (H-6 묶음 ablation 금지).
    """
    ctl = _WF_CONTROL
    mutants = [
        ("C-1 호출 step 삭제",
         ctl.replace("      - name: Run admission checker\n"
                     "        run: bash scripts/check-adr-admission.sh --phase 2\n", "")),
        ("C-2 install step 삭제",
         ctl.replace("      - name: Install test dependencies\n"
                     "        run: pip install pyyaml pytest\n", "")),
        ("C-3 continue-on-error 재삽입",
         ctl.replace("    runs-on: ubuntu-latest\n",
                     "    runs-on: ubuntu-latest\n    continue-on-error: true\n")),
        ("C-4 paths filter 삽입",
         ctl.replace("  pull_request:\n",
                     "  pull_request:\n    paths:\n      - 'archive/adr/**'\n")),
        ("C-4 paths-ignore filter 삽입",
         ctl.replace("  pull_request:\n",
                     "  pull_request:\n    paths-ignore:\n      - '**.md'\n")),
        ("C-4 job if 가 PR 내용에 조건",
         ctl.replace("    if: github.repository == 'mclayer/plugin-codeforge'\n",
                     "    if: contains(github.event.pull_request.labels.*.name, 'adr')\n")),
    ]
    green = [
        ("install 명령 등가 변형 (python -m pip)",
         ctl.replace("run: pip install pyyaml pytest",
                     "run: python -m pip install pyyaml pytest")),
        ("stdlib-only 선언으로 대체",
         ctl.replace("      - name: Install test dependencies\n"
                     "        run: pip install pyyaml pytest\n",
                     "      # 의존성 0 — stdlib-only checker 임을 선언한다\n")),
        ("job 이름 변경", ctl.replace("fix-ledger-conformance:", "conformance:")),
    ]
    for nm, txt in mutants + green:
        assert txt != ctl, "mutant/변형 '%s' 주입 실패(원문 무변경)" % nm

    S.assert_discriminating(wf_invocation_contract, ctl, mutants, green,
                            label="AC-3/workflow-invocation-contract")

    real = S.wrapper_text(CHECKER_WORKFLOW_REL)
    assert real is not None, (
        "%s 부재 — Change Plan 5 D-10(checker 호출 workflow) 미착지. "
        "checker 가 존재해도 CI 도달 0 이면 3회차 실패 지점의 재현이다." % CHECKER_WORKFLOW_REL
    )
    failed = [nm for nm, fn in (("C-1 호출", wf_has_checker_invocation),
                                ("C-2 의존성", wf_has_dependency_resolution),
                                ("C-3 continue-on-error", wf_no_continue_on_error),
                                ("C-4 path filter", wf_no_path_filters),
                                ("C-4 job if", wf_job_if_always_reports)) if not fn(real)]
    assert not failed, "%s 가 8.C 미충족: %s" % (CHECKER_WORKFLOW_REL, failed)


def test_ac3_unrelated_pr_reports_success_not_pending():
    """AC-3 leg2 — 무관 변경 PR 에서도 결론이 report 된다 (pending 잔존 = FAIL).

    RTM: 5.3 verification "10 무관 변경 PR 에서 `success` report 됨을 실 run 으로 실증".
    ★ 정직 천장 (declared): **실 CI run 은 단위 테스트 사거리 밖**이다. 여기서 기계 판정하는 것은
      "pending 을 만드는 구조가 없는가"(workflow 레벨 skip 유발 필터 0) 이며, 실 run URL 첨부는
      Story 문면 leg 으로만 대조한다. 이 두 줄을 지우고 "실 run 을 검증한다" 고 인용하면 over-claim 이다.
    """
    ctl = _WF_CONTROL
    pred = lambda t: wf_no_path_filters(t) and wf_job_if_always_reports(t)  # noqa: E731
    mutants = [
        ("paths filter (workflow 레벨 skip)",
         ctl.replace("  pull_request:\n", "  pull_request:\n    paths:\n      - 'x/**'\n")),
        ("paths-ignore filter",
         ctl.replace("  pull_request:\n", "  pull_request:\n    paths-ignore:\n      - '**.md'\n")),
        ("job if 가 label 조건",
         ctl.replace("    if: github.repository == 'mclayer/plugin-codeforge'\n",
                     "    if: contains(github.event.pull_request.labels.*.name, 'adr')\n")),
        ("job if 가 변경 파일 조건",
         ctl.replace("    if: github.repository == 'mclayer/plugin-codeforge'\n",
                     "    if: github.event.pull_request.changed_files > 0\n")),
    ]
    green = [
        ("repo 가드만 있는 job if", ctl),
        ("job if 완전 제거",
         ctl.replace("    if: github.repository == 'mclayer/plugin-codeforge'\n", "")),
        ("branches 지정은 push 에만", ctl),
    ]
    for nm, txt in mutants:
        assert txt != ctl, "mutant '%s' 주입 실패" % nm
    S.assert_discriminating(pred, ctl, mutants, green, label="AC-3/always-report")

    real = S.wrapper_text(CHECKER_WORKFLOW_REL)
    assert real is not None, "%s 부재 — D-10 미착지" % CHECKER_WORKFLOW_REL
    assert pred(real) is True, (
        "%s 에 workflow 레벨 skip 유발 필터가 있다 — 무관 PR 에서 context 가 pending 으로 잔존한다"
        % CHECKER_WORKFLOW_REL
    )


def test_ac3_collected_test_count_non_zero():
    """AC-3 leg3 / 8.C C-5 — 수집 테스트 수가 non-zero 다 (**실행 산출로 판정**).

    RTM: 5.3 verification "수집 테스트 수 non-zero".
    ★ 이 leg 이 없으면 "workflow 는 있는데 아무것도 안 돈다" 가 GREEN 이 된다
      (이 repo 의 self-test step 이 생성 이래 `No module named pytest` 로 한 번도 import 를
      넘지 못한 실례가 정확히 그 형상이다).
    """
    suite_dir = Path(__file__).resolve().parent

    def collected(target):
        rc, out, err = S.run_rc([sys.executable, "-m", "pytest", str(target),
                                 "--collect-only", "-q", "-p", "no:cacheprovider"])
        m = re.search(r"(\d+)\s+tests?\s+collected", out) or re.search(r"^(\d+)\s+tests?$", out, re.M)
        if m:
            return int(m.group(1))
        return 0 if rc != 0 else len(re.findall(r"::test_", out))

    empty = suite_dir.parent / "_cfp2985_collect_probe_empty"
    empty.mkdir(exist_ok=True)
    try:
        n_ctl = collected(suite_dir)
        n_mut = collected(empty)
    finally:
        try:
            empty.rmdir()
        except OSError:
            pass

    # H-4 — 대조군 선통과 확인 후에만 mutant 를 해석한다.
    assert n_ctl > 0, ("대조군 수집 0 — 이 상태에서 '빈 정의역 수집 0' 은 판별력이 없다(H-4). "
                       "수집기 자체가 죽었는지 먼저 본다.")
    assert n_mut == 0, ("빈 정의역에서도 수집 %d — 수집 계수기가 정의역과 무관하게 값을 낸다 "
                        "(hollow oracle)" % n_mut)
    assert n_ctl > 0, "본 스위트 수집 테스트 수 0 — dead test 위 GREEN"


# ---------------------------------------------------------------------------
# AC-4 술어 — 검증 정의역 선언
# ---------------------------------------------------------------------------
VD_ENUM_FIELD = "verification_domain_enumeration"
VD_COVERAGE_FIELD = "verification_domain_coverage"

_HOLLOW_RE = (
    re.compile(r"^\s*(null|none|n/?a|tbd|-{1,2}|—|–|\?+)\s*$", re.I),
    re.compile(r"^\s*0\s*(대|/|:|vs\.?)\s*0\s*$"),
    re.compile(r"^\s*1\s*(대|/|:|vs\.?)\s*1\s*$"),   # 자기 자신 1건만 = 공허
)


def hollow_declaration(value):
    """공허 선언인가 -> True 면 **거절**(비-zero exit) 대상."""
    if value is None:
        return True
    v = S.norm_cell(str(value))
    if not v:
        return True
    return any(p.match(v) for p in _HOLLOW_RE)


def declaration_present(text, marker):
    """고정 마커 앵커 + 뒤 내용 non-empty. 마커 표기는 정규화 후 매칭(전각 콜론 · 공백 변형 허용).

    두 배치 형상을 **모두** 인정한다 — 설계는 선언을 10 표의 trailing optional column 으로
    둘 수도, 문서 `키: 값` 줄로 둘 수도 있다 (5.4 AC-4 의 "10 행 배치 / machine 층 배치"
    조건부 mutant 가 그 두 형상을 가리킨다). 한 형상만 보면 다른 형상이 vacuous GREEN 이 된다.
    """
    norm = re.sub(r"[：]", ":", text)
    norm = re.sub(r"[  -​　]", " ", norm)
    pat = re.compile(r"%s\s*[:=]\s*(.+)$" % re.escape(marker), re.M)
    for m in pat.finditer(norm):
        val = m.group(1).strip()
        if val and not hollow_declaration(val):
            return True
    # 표 컬럼 배치 — 헤더 셀에 마커가 있으면 그 열의 데이터 셀이 non-hollow 여야 한다.
    for header, rows in S.md_tables(norm):
        idx = next((k for k, h in enumerate(header) if marker in h), -1)
        if idx < 0:
            continue
        for cells in rows:
            if len(cells) > idx and not hollow_declaration(cells[idx]):
                return True
    return False


def test_ac4_verification_domain_declaration_present():
    """AC-4 leg1 — 검증 정의역 선언(열거 산출 명령 + 검사 수 대 열거 수)이 실재한다.

    RTM: 5.3 verification "고정 마커 앵커 정규식 + 뒤 내용 non-empty".
    """
    # 구분자 행이 없으면 마크다운 표가 아니다 — fixture 자신이 malformed 이면
    # "표 배치에서 인식 안 됨" 이 술어 결함처럼 보인다 (본 하네스가 1회 자기검출).
    ctl = ("| Iter | 원인 판정 | %s | %s |\n"
           "|---|---|---|---|\n"
           "| 1 | 설계 | `bash scripts/check-adr-admission.sh --list` | 12 대 12 |\n"
           % (VD_ENUM_FIELD, VD_COVERAGE_FIELD))
    doc_ctl = ("%s: bash scripts/check-adr-admission.sh --list\n"
               "%s: 12 대 12\n" % (VD_ENUM_FIELD, VD_COVERAGE_FIELD))
    pred = lambda t: (declaration_present(t, VD_ENUM_FIELD)                    # noqa: E731
                      and declaration_present(t, VD_COVERAGE_FIELD))

    mutants = [
        ("열거 명령 선언 삭제",
         "\n".join(l for l in doc_ctl.split("\n") if VD_ENUM_FIELD not in l)),
        ("coverage 선언 삭제",
         "\n".join(l for l in doc_ctl.split("\n") if VD_COVERAGE_FIELD not in l)),
        ("coverage 값 공허 (0 대 0)", doc_ctl.replace("12 대 12", "0 대 0")),
        ("coverage 값 공허 (대시)", doc_ctl.replace("12 대 12", "—")),
        ("coverage 값 공허 (null)", doc_ctl.replace("12 대 12", "null")),
        ("coverage 값 공허 (자기 1건만)", doc_ctl.replace("12 대 12", "1 대 1")),
        ("값 자리 공란", doc_ctl.replace("12 대 12", "")),
    ]
    green = [
        ("전각 콜론 표기", doc_ctl.replace(":", "：")),
        ("공백 변형", doc_ctl.replace(": ", " :  ")),
        ("부분 커버리지 값", doc_ctl.replace("12 대 12", "3 대 12")),
    ]
    for nm, txt in mutants + green:
        assert txt != doc_ctl, "mutant/변형 '%s' 주입 실패" % nm
    S.assert_discriminating(pred, doc_ctl, mutants, green, label="AC-4/vd-declaration")
    assert pred(ctl) is True, "표 행 배치 형상에서도 선언이 인식돼야 한다"

    contract = S.wrapper_text(S.CONTRACT_FIX_EVENT_REL)
    missing = [f for f in (VD_ENUM_FIELD, VD_COVERAGE_FIELD) if f not in contract]
    assert not missing, (
        "계약 %s 에 검증 정의역 선언 필드 부재: %s. "
        "Change Plan 4.1(fix-event-v1 v1.6 — 2 필드 신설, D-1) 미착지 상태다."
        % (S.CONTRACT_FIX_EVENT_REL, missing)
    )


def test_ac4_hollow_declaration_value_rejected():
    """AC-4 leg2 — 공허 값(`0 대 0` · 대시 · `null` · 자기 1건만)이 배제된다.

    RTM: 5.3 verification "공허 패턴(0 대 0 · 대시 · null) 배제".
    """
    pred = lambda v: not hollow_declaration(v)  # noqa: E731
    control = "12 대 12"
    mutants = [("0 대 0", "0 대 0"), ("0/0", "0/0"), ("대시", "—"), ("하이픈", "-"),
               ("null", "null"), ("N/A", "N/A"), ("TBD", "TBD"),
               ("자기 1건만", "1 대 1"), ("공란", ""), ("None 값", None)]
    green = [("부분 커버리지", "3 대 12"), ("전량 커버리지", "12 대 12"),
             ("장식 붙은 값", "**8 대 20**"), ("콜론 표기", "5:40")]
    S.assert_discriminating(pred, control, mutants, green, label="AC-4/hollow-rejection")


# ---------------------------------------------------------------------------
# AC-5 술어 — 열거 산출 명령 schema + site path resolve
# ---------------------------------------------------------------------------
_RAW_SHELL_RE = re.compile(
    r"(\|\s*(sh|bash)\b|;|&&|\|\||`|\$\(|>\s*/|rm\s+-rf|curl\b|wget\b|eval\b|sudo\b)")
_GATE_ENTRY_RE = re.compile(
    r"^(bash|sh|python3?|python)\s+(-m\s+pytest\s+)?(?:\./)?"
    r"(scripts/|tests/|hooks/|\.github/)")


def reproducer_command_ok(cmd):
    """`reproducer_command` schema — repo-relative 게이트·테스트 호출, raw shell free-string 금지."""
    if not isinstance(cmd, str) or not cmd.strip():
        return False
    c = cmd.strip()
    if _RAW_SHELL_RE.search(c):
        return False
    if c.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", c):     # 절대 경로 금지
        return False
    if ".." in c:
        return False
    return bool(_GATE_ENTRY_RE.match(c))


def site_paths_resolve(paths, root=None):
    """열거 site 경로가 전건 resolve 되는가. `./x` 와 `x` 는 등가.

    ★ `exists()` 가 아니라 `is_file()` 이다 — 디렉터리까지 resolve 로 인정하면
      경로를 상위 디렉터리로 **절단**하는 것만으로 미해결 site 가 통과한다
      (본 하네스가 자기 오라클에서 잡아낸 과대 판정 1건).
    """
    base = Path(root or S.REPO_ROOT)
    for p in paths:
        rel = str(p).split(":")[0].strip()
        rel = re.sub(r"^\./", "", rel)
        if not rel or not (base / rel).is_file():
            return False
    return True


def test_ac5_reproducer_command_schema_conformance():
    """AC-5 leg1 — 열거 산출 명령이 `reproducer_command` schema 를 만족한다.

    RTM: 5.3 verification "`reproducer_command` schema 형식 검사
    (repo-relative 게이트·테스트 호출, raw shell 금지)".
    """
    control = "bash scripts/check-adr-admission.sh --phase 2"
    mutants = [
        ("raw shell 파이프", "grep -rn 'x' . | sh"),
        ("명령 연결", "bash scripts/x.sh && rm -rf build"),
        ("세미콜론 체인", "bash scripts/x.sh; echo done"),
        ("커맨드 치환", "bash scripts/x.sh $(whoami)"),
        ("절대 경로", "/usr/bin/bash /opt/x.sh"),
        ("상위 경로 탈출", "bash ../other-repo/scripts/x.sh"),
        ("게이트·테스트 진입점 아님", "echo hello"),
        ("네트워크 취득", "curl https://example.com/x.sh"),
        ("공란", ""),
    ]
    green = [
        ("./ 접두 등가 표기", "bash ./scripts/check-adr-admission.sh --phase 2"),
        ("pytest 진입점", "python3 -m pytest tests/cfp2985/test_cfp2985_ac03_06.py"),
        ("python 스크립트 진입점", "python3 scripts/lib/check_adr_admission.py --list"),
        ("hooks 진입점", "bash hooks/tests/test_x.sh"),
    ]
    S.assert_discriminating(reproducer_command_ok, control, mutants, green,
                            label="AC-5/reproducer-schema")

    contract = S.wrapper_text(S.CONTRACT_FIX_EVENT_REL)
    assert "reproducer_command" in contract, (
        "계약 %s 에 `reproducer_command` 정의 부재 — schema 상속 근거가 없다"
        % S.CONTRACT_FIX_EVENT_REL)


def test_ac5_enumerated_site_path_resolves():
    """AC-5 leg2 — 열거된 site 경로가 실제로 resolve 된다 (미해결 1건 이상이면 비-zero exit).

    RTM: 5.3 verification "열거 site 경로 path resolve".
    열거 정본 = AC-11 이 지목한 유령 컬럼 지시 3 site (wrapper-local 실물).
    """
    real_sites = [S.CONTRACT_DEBATE_REL, S.REVIEW_PL_BASE_REL, S.CONTRACT_FIX_EVENT_REL]
    control = list(real_sites)
    mutants = [
        ("실재하지 않는 경로 1건 주입", real_sites + ["docs/inter-plugin-contracts/nope-v9.md"]),
        ("오타 경로", ["docs/inter-plugin-contracts/fix-event-v0.md"]),
        ("디렉터리만 남긴 절단 경로", ["docs/inter-plugin-contracts/"]),
        ("공란 항목", real_sites + [""]),
    ]
    green = [
        ("./ 등가 표기", ["./" + p for p in real_sites]),
        ("line 좌표 첨부 표기", ["%s:352" % S.CONTRACT_DEBATE_REL]),
    ]
    S.assert_discriminating(site_paths_resolve, control, mutants, green,
                            label="AC-5/site-path-resolve")
    assert site_paths_resolve(real_sites) is True, "열거 site 중 resolve 실패 존재"


# ---------------------------------------------------------------------------
# AC-6 — 열거 site mutation 전건 RED
# ---------------------------------------------------------------------------
def mutation_report_all_red(report):
    """{site: verdict} — 전 site 가 RED 여야 한다. 미실행(None)도 위반이다 (미실행 site 탐지)."""
    if not report:
        return False
    return all(v == "RED" for v in report.values())


def test_ac6_enumerated_site_mutation_all_red():
    """AC-6 — 열거 site 에 mutant 를 **실제로 주입**했을 때 전 site 가 RED 를 낸다.

    RTM: 5.3 verification "mutation 실행 결과 대조 — 전 site RED, 1건이라도 생존 시 비-zero exit".
    ★ 표기가 아니라 **실행 결과**로 판정한다 (5.4 AC-6 mutant3).
    """
    # (1) 오라클 자신의 판별력 — 미실행 site 와 생존 site 를 구별하는가.
    ctl_report = {"site-a": "RED", "site-b": "RED", "site-c": "RED"}
    S.assert_discriminating(
        mutation_report_all_red, ctl_report,
        mutants=[("1건 생존", {"site-a": "RED", "site-b": "GREEN", "site-c": "RED"}),
                 ("1건 미실행", {"site-a": "RED", "site-b": None, "site-c": "RED"}),
                 ("전건 미실행", {}),
                 ("전건 생존", {"site-a": "GREEN"})],
        green_variants=[("site 수 확장", dict(ctl_report, **{"site-d": "RED"}))],
        label="AC-6/mutation-report-oracle")

    # (2) 실 site 실행 — 열거 3 site 각각에 유령 컬럼 지시를 주입해 검출을 확인한다.
    contract = S.wrapper_text(S.CONTRACT_FIX_EVENT_REL)
    cols = S.contract_section10_columns(contract)
    assert cols, ("계약에서 10 컬럼 집합을 파싱하지 못했다 — 판정불가(fail-closed). "
                  "정본 표는 ```markdown 펜스 안에 있다.")
    sites = [S.CONTRACT_DEBATE_REL, S.REVIEW_PL_BASE_REL, S.CONTRACT_FIX_EVENT_REL]
    injected = "10 FIX Ledger row 의 `phantom_ac6 column` 에 기록 의무\n"

    report = {}
    for rel in sites:
        base = S.wrapper_text(rel)
        assert base is not None, "열거 site %s 미해결 — 미실행 site" % rel
        hits_after = S.phantom_column_directives(base + "\n" + injected, cols)
        names_after = {n for _, n, _ in hits_after}
        report[rel] = "RED" if "phantom_ac6" in names_after else "GREEN"
    assert mutation_report_all_red(report), (
        "열거 site mutation 생존: %s" % {k: v for k, v in report.items() if v != "RED"})

    # (3) 대조군 — 주입 0 인 원문에서 그 mutant 토큰이 검출되지 않는다 (항진 오라클 배제).
    for rel in sites:
        names = {n for _, n, _ in S.phantom_column_directives(S.wrapper_text(rel), cols)}
        assert "phantom_ac6" not in names, (
            "%s 원문에서 주입하지도 않은 토큰이 검출됐다 — 오라클이 항진이다" % rel)
