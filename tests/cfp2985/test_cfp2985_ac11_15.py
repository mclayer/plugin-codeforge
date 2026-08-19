"""CFP-2985 RTM 8.1.1 — AC-11 (3) · AC-12 (2) · AC-13 (1) · AC-14 (2) · AC-15 (1) 명명 테스트.

AC-11 = 유령 컬럼 지시 0 · 두 계약 컬럼 집합 대조 · 열거 명령 기록.
AC-12 = normative/declared 라벨 presence + declared 사유 non-empty.
AC-13 = 신규 bypass 라벨 ↔ RED run 참조 pairing.
AC-14 = mechanical enforcement 선언 ↔ registry entry 대조 · TB-1 사다리 전건.
AC-15 = 집계 산출물 경로·필드·택일·배제사유 **동시** 충족.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _cfp2985_spec as S  # noqa: E402

# wrapper 전역 스캔 루트 (자원 상한 — 무제한 rglob 금지, 8.3 born-safe bound 상속)
SCAN_ROOTS = ("docs", "plugins", "templates", "skills", "archive")
SCAN_FILE_CAP = 4000

STORY_PAGE_STRUCTURE_REL = "templates/story-page-structure.md"
MERGE_BASE_SHA = "ecfe62d63"          # Change Plan 이 좌표 규율로 고정한 wrapper merge-base

LADDER_EXIT_TOKENS = ("ladder-path-key", "ladder-path-missing", "ladder-unwired")


def _scan_md(roots=SCAN_ROOTS, cap=SCAN_FILE_CAP):
    n = 0
    for r in roots:
        base = S.REPO_ROOT / r
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            n += 1
            if n > cap:
                return
            yield p


# ---------------------------------------------------------------------------
# AC-11
# ---------------------------------------------------------------------------
def test_ac11_phantom_column_directive_zero_sites():
    """AC-11 leg1 — 10 표에 없는 컬럼명 기록 지시가 wrapper 전역에서 0 이다.

    RTM: 5.3 verification "grep 술어(현 위반 3 site -> 0)".
    ★ 정당 사용(`root_cause_class` 집계 축, 32 파일)과 **반드시 구별**한다 —
      무차별 grep 봉합은 false RED + 실동작 스크립트 파괴다 (4.3 E-7).
    """
    cols = S.contract_section10_columns(S.wrapper_text(S.CONTRACT_FIX_EVENT_REL))
    assert cols, ("계약에서 10 컬럼 집합을 파싱하지 못했다 — 판정불가(fail-closed). "
                  "정본 표는 코드펜스 안이라 펜스 포함 경로가 필요하다.")
    pred = lambda t: not S.phantom_column_directives(t, cols)  # noqa: E731

    control = ("§10 FIX Ledger row 의 `원인 판정` column 에 값을 기록한다.\n"
               "`reproducer_command` optional column 은 finding 생성 시점에 기록한다.\n"
               "집계는 root_cause_class 를 축으로 한다.\n")
    mutants = [
        ("없는 컬럼 지시 주입 (resolution)",
         control + "§10 FIX Ledger row 의 resolution column 에 기록 의무\n"),
        ("없는 컬럼 지시 주입 (root_cause)",
         control + "§10 row 의 root_cause column 에 기록한다\n"),
        ("합성 지시 (root_cause + resolution)",
         control + "§10 FIX Ledger row 의 root_cause + resolution column 만으로 기록\n"),
    ]
    green = [
        ("정당 컬럼 지시만", control),
        ("집계 축 정당 사용 확장", control + "root_cause_class 분포를 집계한다.\n"),
        ("컬럼 장식 표기", control.replace("`원인 판정` column", "**원인 판정** column")),
        ("문맥 밖 언급 (10 무관)", control + "resolution column 은 다른 시스템 개념이다\n"),
    ]
    for nm, txt in mutants:
        assert txt != control, "mutant '%s' 주입 실패" % nm
    S.assert_discriminating(pred, control, mutants, green, label="AC-11/phantom-column")

    sites, scanned = [], 0
    for p in _scan_md():
        scanned += 1
        try:
            t = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, name, _ln in S.phantom_column_directives(t, cols):
            sites.append("%s:%d (%s)" % (str(p.relative_to(S.REPO_ROOT)).replace("\\", "/"),
                                         lineno, name))
    # INV-V — 검사 대상이 0 이면 GREEN 금지 (vacuous 가드).
    assert scanned > 0, "스캔 코퍼스 0 — vacuous GREEN 금지"
    assert not sites, (
        "유령 컬럼 지시 site 잔존 (%d 파일 스캔): %s. "
        "Change Plan 5 의 D-2(debate-protocol-v1) · D-3(review-pl-base) 미착지 상태다."
        % (scanned, sorted(set(sites))))


def section10_column_set(text):
    """문서의 10 FIX Ledger 표 헤더에서 컬럼명 집합 (가장 긴 것 = 정본 선언).

    include_fenced=True — 계약도 템플릿도 정본 표를 ```markdown 펜스 **안에** 둔다.
    펜스를 빼면 양쪽 다 0 이 되고, 0 == 0 이라 대조가 통과한다 (vacuous 일치).
    """
    best = set()
    for header, _rows in S.md_tables(text, include_fenced=True):
        cells = [c.strip() for c in header if c.strip()]
        if "Iter" in cells and any("원인" in c for c in cells) and len(cells) > len(best):
            best = set(cells)
    return best


def test_ac11_contract_column_name_sets_match():
    """AC-11 leg2 — 두 계약이 선언한 10 컬럼명 집합이 일치한다.

    RTM: 5.3 verification "두 계약 컬럼명 집합 대조".
    대상 = `fix-event-v1.md`(Column SSOT) ↔ `templates/story-page-structure.md` 10.
    """
    a = "| Iter | 시각 | 원인 판정 | RESET? |\n|---|---|---|---|\n| 1 | t | 설계 | — |\n"
    b = "| Iter | 시각 | 원인 판정 | RESET? |\n|---|---|---|---|\n| 1 | t | 구현 | — |\n"
    pred = lambda pair: section10_column_set(pair[0]) == section10_column_set(pair[1])  # noqa: E731

    mutants = [
        ("한쪽에 컬럼 1개 누락",
         (a, b.replace("| Iter | 시각 | 원인 판정 | RESET? |",
                       "| Iter | 시각 | 원인 판정 |").replace("| 1 | t | 구현 | — |",
                                                              "| 1 | t | 구현 |"))),
        ("한쪽에 컬럼 1개 추가",
         (a, b.replace("| RESET? |", "| RESET? | replay_verdict |").replace(
             "| — |", "| — | null |").replace("|---|---|---|---|", "|---|---|---|---|---|"))),
        ("컬럼명 철자 변형", (a, b.replace("원인 판정", "원인판정"))),
    ]
    green = [
        ("행 값만 다름", (a, b)),
        ("컬럼 순서 동일 · 행 수 상이", (a, b + "| 2 | t2 | 설계 | — |\n")),
    ]
    S.assert_discriminating(pred, (a, b), mutants, green, label="AC-11/column-set-match")

    contract = S.wrapper_text(S.CONTRACT_FIX_EVENT_REL)
    template = S.wrapper_text(STORY_PAGE_STRUCTURE_REL)
    c_cols, t_cols = section10_column_set(contract), section10_column_set(template)
    assert c_cols, "계약에서 10 표 헤더를 찾지 못했다"
    assert t_cols, "%s 에서 10 표 헤더를 찾지 못했다" % STORY_PAGE_STRUCTURE_REL
    assert c_cols == t_cols, (
        "10 컬럼 집합 drift — 계약에만 있음: %s / 템플릿에만 있음: %s. "
        "Change Plan 5 의 D-5(story-page-structure v1.3 11열 -> v1.6 정합) 미착지 상태다."
        % (sorted(c_cols - t_cols), sorted(t_cols - c_cols)))


def enumeration_command_recorded(text):
    """열거 명령이 **실행 가능한 형태로** 기록됐는가 (미기록 시 비-zero exit)."""
    for m in re.finditer(r"`([^`\n]{6,})`", text):
        cmd = m.group(1).strip()
        if re.match(r"^(grep|rg|bash|sh|python3?|git)\s+\S", cmd):
            return True
    for line in text.split("\n"):
        s = line.strip()
        if re.match(r"^(grep|rg|bash|sh|python3?|git)\s+\S", s):
            return True
    return False


def test_ac11_enumeration_command_recorded():
    """AC-11 leg3 — 판정에 사용한 열거 명령이 기록돼 있다.

    RTM: 5.3 verification "열거 명령 미기록 시 비-zero exit".
    """
    control = "열거 명령: `grep -rnE 'resolution column' docs plugins templates`\n"
    mutants = [
        ("명령 미기록 (서술만)", "wrapper 전역을 훑어 3 site 를 찾았다.\n"),
        ("명령 자리를 대시로", "열거 명령: `—`\n"),
        ("명령이 아니라 결과 수치만", "열거 결과: `3 site`\n"),
        ("공란", ""),
    ]
    green = [
        ("python 진입점", "열거 명령: `python3 scripts/lib/check_adr_admission.py --list`\n"),
        ("펜스 밖 bare 명령 줄", "다음으로 열거한다\ngrep -rn 'resolution column' docs\n"),
        ("git 명령", "재현: `git grep -n 'resolution column'`\n"),
    ]
    S.assert_discriminating(enumeration_command_recorded, control, mutants, green,
                            label="AC-11/enumeration-command")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    assert enumeration_command_recorded(story), (
        "Story 에 열거 산출 명령이 기록되지 않았다 (판정 재현 불가)")


# ---------------------------------------------------------------------------
# AC-12 — 라벨 presence + declared 사유
# ---------------------------------------------------------------------------
LABELS = ("normative", "declared", "확인 불가")


def label_rows(text):
    """라벨 컬럼을 가진 표들 -> [(row_cells, label_idx)]."""
    out = []
    for header, rows in S.md_tables(text):
        idx = -1
        for i, h in enumerate(header):
            if S.norm_header(h) in ("라벨", "tier", "label"):
                idx = i
                break
        if idx < 0:
            continue
        for cells in rows:
            if len(cells) > idx:
                out.append((cells, idx))
    return out


def labels_present(rows):
    """모든 행이 closed-set 라벨을 보유하는가."""
    if not rows:
        return False
    for cells, idx in rows:
        if S.norm_cell(cells[idx]) not in LABELS:
            return False
    return True


def declared_reasons_non_empty(rows):
    """`declared` 행은 **사유** 셀이 non-empty 여야 한다 (ADR-181 결정 6 부착 의무)."""
    if not rows:
        return False
    for cells, idx in rows:
        if S.norm_cell(cells[idx]) != "declared":
            continue
        tail = [S.norm_cell(c) for i, c in enumerate(cells) if i > idx]
        if not any(len(t) >= 4 for t in tail):
            return False
    return True


_LBL_CTL = [(["INV-A", "내용 A", "normative", "판정 경로 A"], 2),
            (["INV-B", "내용 B", "declared", "오라클 부재라 기계 판정 불가"], 2)]


def test_ac12_normative_declared_label_present():
    """AC-12 leg1 — 규범 항목마다 normative/declared 라벨이 부착돼 있다.

    RTM: 5.3 verification "라벨 presence lint".
    """
    mutants = [
        ("라벨 셀 공란", [(["INV-A", "내용", "", "경로"], 2), _LBL_CTL[1]]),
        ("closed-set 밖 라벨 (advisory)",
         [(["INV-A", "내용", "advisory", "경로"], 2), _LBL_CTL[1]]),
        ("라벨 자리에 대시", [(["INV-A", "내용", "—", "경로"], 2), _LBL_CTL[1]]),
        ("행 자체가 0 (vacuous)", []),
    ]
    green = [
        ("장식 붙은 라벨", [(["INV-A", "내용", "**normative**", "경로"], 2), _LBL_CTL[1]]),
        ("확인 불가 라벨", [(["INV-C", "내용", "확인 불가", "이관처 X"], 2)]),
        ("행 확장", _LBL_CTL + [(["INV-C", "내용", "normative", "경로"], 2)]),
    ]
    S.assert_discriminating(labels_present, _LBL_CTL, mutants, green,
                            label="AC-12/label-presence")

    adr = S.wrapper_text(S.ADR181_REL)
    rows = label_rows(adr)
    assert rows, "ADR-181 에서 라벨 컬럼을 가진 표를 찾지 못했다 — 검사 정의역 0"
    bad = [S.norm_cell(c[idx]) for c, idx in rows if S.norm_cell(c[idx]) not in LABELS]
    assert not bad, "ADR-181 라벨 컬럼에 closed-set 밖 값: %s" % sorted(set(bad))


def test_ac12_declared_reason_non_empty():
    """AC-12 leg2 — `declared` 항목에 기계 판정 불가 사유가 1줄 이상 병기돼 있다.

    RTM: 5.3 verification "declared 항목의 사유 필드 non-empty".
    """
    mutants = [
        ("사유 셀 공란", [_LBL_CTL[0], (["INV-B", "내용 B", "declared", ""], 2)]),
        ("사유가 대시", [_LBL_CTL[0], (["INV-B", "내용 B", "declared", "—"], 2)]),
        ("사유 컬럼 자체가 없음", [_LBL_CTL[0], (["INV-B", "내용 B", "declared"], 2)]),
        ("행 0 (vacuous)", []),
    ]
    green = [
        ("사유가 긴 산문", [_LBL_CTL[0],
                            (["INV-B", "내용", "declared", "정지 문제 근사라 전수 열거 불가"], 2)]),
        ("normative 행은 사유 무관", [(["INV-A", "내용", "normative", "—"], 2), _LBL_CTL[1]]),
    ]
    S.assert_discriminating(declared_reasons_non_empty, _LBL_CTL, mutants, green,
                            label="AC-12/declared-reason")

    adr = S.wrapper_text(S.ADR181_REL)
    rows = label_rows(adr)
    assert rows, "ADR-181 라벨 표 부재 — 검사 정의역 0"
    assert declared_reasons_non_empty(rows), (
        "ADR-181 의 `declared` 행 중 사유 병기가 없는 행이 있다 (결정 6 부착 의무 위반)")


# ---------------------------------------------------------------------------
# AC-13 — 신규 bypass 라벨 ↔ RED run 참조
# ---------------------------------------------------------------------------
_BYPASS_NAME_RE = re.compile(r"^\s*-\s+name:\s*(hotfix-bypass:[\w.:-]+)\s*$")
_RUN_REF_RE = re.compile(r"(actions/runs/\d+|run[_ -]?id\s*[:=]\s*\d+|RED\s*run\s*[:=]?\s*\S+)", re.I)


def bypass_entries(text):
    """`- name: hotfix-bypass:<x>` entry -> {이름: 그 entry 블록 텍스트}."""
    lines = text.split("\n")
    out, cur, buf = {}, None, []
    for ln in lines:
        m = _BYPASS_NAME_RE.match(ln)
        if m:
            if cur:
                out[cur] = "\n".join(buf)
            cur, buf = m.group(1), [ln]
            continue
        if cur is not None:
            if re.match(r"^\s*-\s+name:\s", ln):
                out[cur] = "\n".join(buf)
                cur, buf = None, []
                continue
            buf.append(ln)
    if cur:
        out[cur] = "\n".join(buf)
    return out


def new_bypass_entries_paired(new_names, entries):
    """신규 bypass entry 각각이 RED run 참조를 보유하는가 (짝 부재 시 비-zero exit)."""
    for name in new_names:
        block = entries.get(name, "")
        if not _RUN_REF_RE.search(block):
            return False
    return True


def test_ac13_new_bypass_label_requires_red_run_reference():
    """AC-13 — 신규 bypass 라벨은 대응 게이트의 RED run 참조를 선행 보유한다.

    RTM: 5.3 verification "label registry 신규 bypass entry ↔ RED run 참조 pairing 검사".
    정의역 = **신규** entry (baseline cut 이후) — 소급 적용하지 않는다 (11.2 NG-1 미소급).
    """
    entries = {
        "hotfix-bypass:alpha": "  - name: hotfix-bypass:alpha\n    red_run: https://github.com/o/r/actions/runs/123\n",
        "hotfix-bypass:beta": "  - name: hotfix-bypass:beta\n    note: run_id = 456 에서 RED 확인\n",
        "hotfix-bypass:gamma": "  - name: hotfix-bypass:gamma\n    note: 참조 없음\n",
    }
    pred = lambda names: new_bypass_entries_paired(names, entries)  # noqa: E731
    control = ["hotfix-bypass:alpha", "hotfix-bypass:beta"]
    mutants = [
        ("참조 없는 신규 entry 포함", control + ["hotfix-bypass:gamma"]),
        ("등재조차 안 된 이름", control + ["hotfix-bypass:missing"]),
        ("참조 없는 entry 단독", ["hotfix-bypass:gamma"]),
    ]
    green = [
        ("URL 형식 참조", ["hotfix-bypass:alpha"]),
        ("run id 형식 참조 (형식 다양성 허용)", ["hotfix-bypass:beta"]),
        ("신규 0건", []),
    ]
    S.assert_discriminating(pred, control, mutants, green, label="AC-13/bypass-run-pairing")

    reg = S.wrapper_text(S.CONTRACT_LABEL_REL)
    head = bypass_entries(reg)
    assert head, "label-registry 에서 bypass entry 를 하나도 파싱하지 못했다 — 파서 dead"
    rc, base_text, _ = S.run_rc(["git", "show", "%s:%s" % (MERGE_BASE_SHA, S.CONTRACT_LABEL_REL)])
    assert rc == 0, "merge-base %s 의 label-registry 를 읽지 못했다 (rc=%d)" % (MERGE_BASE_SHA, rc)
    base = bypass_entries(base_text)
    new_names = sorted(set(head) - set(base))
    assert new_bypass_entries_paired(new_names, head), (
        "RED run 참조 없는 신규 bypass entry: %s"
        % [n for n in new_names if not _RUN_REF_RE.search(head.get(n, ""))])


# ---------------------------------------------------------------------------
# AC-14 — mechanical enforcement 정산 + TB-1 사다리
# ---------------------------------------------------------------------------
_ME_ANCHOR_RE = re.compile(r"^\*\*mechanical enforcement\*\*:\s*(.*)$", re.M)
_RETRACT_RE = re.compile(r"(없다|철회|retract)")


def me_claims_settled(text, registry_names):
    """ADR 본문의 `**mechanical enforcement**:` 선언이 registry entry 를 갖거나 철회됐는가."""
    hits = _ME_ANCHOR_RE.findall(text)
    if not hits:
        return True                     # 선언 0 = 정산할 것이 없다
    for tail in hits:
        if _RETRACT_RE.search(tail):
            continue
        named = set(re.findall(r"`([\w.:-]+)`", tail)) | set(re.findall(r"\b([\w-]{6,})\b", tail))
        if not (named & set(registry_names)):
            return False
    return True


def test_ac14_mechanical_enforcement_claim_registry_pairing():
    """AC-14 leg1 — mechanical enforcement 선언이 registry entry 를 갖거나 철회돼 있다.

    RTM: 5.3 verification "ADR 본문 `mechanical enforcement` 문자열 ↔
    `docs/evidence-checks-registry.yaml` entry 존재 대조".
    """
    reg_names = {"fix-ledger-conformance", "adr-admission"}
    pred = lambda t: me_claims_settled(t, reg_names)  # noqa: E731
    control = "**mechanical enforcement**: `fix-ledger-conformance` warning-tier lint.\n"
    mutants = [
        ("registry 없는 새 선언 주입",
         control + "**mechanical enforcement**: `ghost-lint-presence` 가 집행 중이다.\n"),
        ("registry 없는 선언 단독",
         "**mechanical enforcement**: `ghost-lint-presence` 가 집행 중이다.\n"),
        ("이름 없는 현재형 단정",
         "**mechanical enforcement**: 이미 기계로 강제되고 있다.\n"),
    ]
    green = [
        ("철회 문면", "**mechanical enforcement**: 없다 — 본 선언은 Amendment 4 에서 철회됐다.\n"),
        ("선언 0", "본 결정에는 기계 강제 선언이 없다.\n"),
        ("registry 등재된 다른 이름", "**mechanical enforcement**: `adr-admission` checker.\n"),
    ]
    S.assert_discriminating(pred, control, mutants, green, label="AC-14/me-registry-pairing")

    registry = S.wrapper_text(S.REGISTRY_REL)
    names = set(re.findall(r"^\s*-\s+name:\s*([\w.:-]+)\s*$", registry, re.M))
    assert names, "evidence-checks-registry 에서 entry 이름을 하나도 파싱하지 못했다 — 파서 dead"
    adr067 = S.wrapper_text("archive/adr/ADR-067-fix-ledger-implementability-escalation.md")
    assert adr067 is not None, "ADR-067 부재"
    assert me_claims_settled(adr067, names), (
        "ADR-067 의 mechanical enforcement 선언 중 registry entry 도 없고 철회도 안 된 것이 있다: %s"
        % [t for t in _ME_ANCHOR_RE.findall(adr067) if not _RETRACT_RE.search(t)])


def iv_table_rows(adr_text):
    """ADR-181 결정 5 3-dt (iv) 결정표 -> [(id, 입력, 기대, exit사유)]."""
    for header, rows in S.md_tables(adr_text):
        if not any("입력 바이트" in h for h in header):
            continue
        out = []
        for cells in rows:
            if len(cells) < 4:
                continue
            out.append((S.norm_cell(cells[0]), cells[1], S.norm_cell(cells[2]),
                        S.norm_cell(cells[3])))
        return out
    return []


def ladder_rungs_exercised(rows):
    """사다리 **전 단**이 표에서 판별되는가.

    (가) 목록 비어있지 않음 -> (나) 경로 키 -> (다) 실재 -> 배선, 그리고 사다리 성공(GREEN) 1건.
    이 leg 이 없던 판에서 `len(mea) >= 1` 만 구현한 stub 이 표 43행을 **전건 통과**했다
    (ADR-181 결정 5 P0 — 열 라운드 동안 "강제가 실재하는가" 가지의 판별 행이 0 이었다).
    """
    if not rows:
        return False
    reasons = {r[3] for r in rows}
    if not set(LADDER_EXIT_TOKENS) <= reasons:
        return False
    return any(exp == "GREEN" and _has_nonempty_mea(inp) for _rid, inp, exp, _rs in rows)


def _has_nonempty_mea(input_cell):
    """입력 셀이 **비어있지 않은** mechanical_enforcement_actions 목록을 담는가."""
    if re.search(r"K\s*:\s*`?\s*\[\s*\]", input_cell):
        return False
    if re.search(r"K\s*:\s*\[[^\]\s]", input_cell):            # 인라인 비-빈 리스트
        return True
    # 블록형 — `K:` 뒤(백틱·공백·개행 마커 무관)에 `- ` 항목이 온다.
    return bool(re.search(r"K\s*:\s*[`\s]*(?:⏎|\n)[`\s]*-\s", input_cell))


def test_ac14_tb1_ladder_all_rungs():
    """AC-14 leg2 / TB-1 — 사다리 전 단이 (iv) 결정표에서 판별된다.

    RTM: 8.C "`TB-1` 사다리" (AC-14 구체화 · `AC-14 ⊂ TB-1` 이며 8.C 가 두 술어를
    합치지 않는다고 명시하므로 별 leg).
    ★ 정직 천장 (declared): 본 테스트는 **표가 사다리 가지를 판별하는가**와
      **checker 실물이 존재하는가**까지 본다. (iv) 67행 전건을 실제로 구동해 대조하는
      acceptance run 은 checker 자신의 discriminating self-test 소관(D-7c)이며,
      그 구동을 여기서 했다고 인용하면 over-claim 이다.
    """
    ctl = [("45", "`D` ⏎ `K:` ⏎ `  - script_path: scripts/x.sh`", "GREEN", "—"),
           ("43", "`D` ⏎ `K:` ⏎ `  - scripts/x.sh`", "RED", "ladder-path-key"),
           ("46", "`D` ⏎ `K:` ⏎ `  - script_path: scripts/absent.sh`", "RED", "ladder-path-missing"),
           ("49", "`D` ⏎ `K:` ⏎ `  - script_path: docs/x.md`", "RED", "ladder-unwired")]
    mutants = [("ladder-path-key 판별 행 제거", [r for r in ctl if r[3] != "ladder-path-key"]),
               ("ladder-path-missing 판별 행 제거",
                [r for r in ctl if r[3] != "ladder-path-missing"]),
               ("ladder-unwired 판별 행 제거", [r for r in ctl if r[3] != "ladder-unwired"]),
               ("사다리 성공(GREEN) 행 제거", [r for r in ctl if r[2] != "GREEN"]),
               ("전 행이 빈 목록 (43행 판 형상)",
                [("1", "`D` ⏎ `K: []  # OK`", "GREEN", "—"),
                 ("2", "`D` ⏎ `K: []`", "RED", "line-form")]),
               ("표가 빔", [])]
    green = [("면제 경로 행 추가", ctl + [("2", "`D` ⏎ `K: []`", "RED", "line-form")]),
             ("행 순서 변경", list(reversed(ctl)))]
    S.assert_discriminating(ladder_rungs_exercised, ctl, mutants, green,
                            label="AC-14/tb1-ladder-rungs")

    adr = S.wrapper_text(S.ADR181_REL)
    rows = iv_table_rows(adr)
    assert rows, "ADR-181 (iv) 결정표를 찾지 못했다 — 수용 기준 정본 부재"
    assert ladder_rungs_exercised(rows), (
        "(iv) 표가 사다리 전 단을 판별하지 않는다. 실측 exit 사유 집합=%s"
        % sorted({r[3] for r in rows}))

    checker = S.wrapper_path("scripts/lib/check_adr_admission.py")
    wrapper_sh = S.wrapper_path("scripts/check-adr-admission.sh")
    missing = [str(p.relative_to(S.REPO_ROOT)).replace("\\", "/")
               for p in (checker, wrapper_sh) if not p.is_file()]
    assert not missing, (
        "admission checker 실물 부재: %s — Change Plan 5 D-7c 미착지. "
        "(iv) 표 %d 행이 수용 기준인데 그것을 재현할 주체가 없다." % (missing, len(rows)))


# ---------------------------------------------------------------------------
# AC-15 — 집계 산출 계약 문면
# ---------------------------------------------------------------------------
AGG_PATHS = ("docs/kpi/dev-process-trend-snapshot.json", "docs/kpi/dev-process-trend-history.jsonl")
AGG_FIELDS = ("pattern_count", "pattern_status", "root_cause_class")
_CHOICE_RE = re.compile(r"(택일|_ROW_KEYS\s*(에|편입)|별\s*feeder|대체\s*feeder)")
_EXCLUSION_RE = re.compile(r"(배제\s*사유|선택하지\s*않은|미채택\s*사유|하지\s*않는다)")


def aggregate_sink_declared(text):
    """산출물 경로 2건 ∧ 필드명 3건 ∧ 택일 선언 마커 ∧ 배제 사유 **동시** 충족 (단일 assert)."""
    if not all(p in text for p in AGG_PATHS):
        return False
    if not all(f in text for f in AGG_FIELDS):
        return False
    if not _CHOICE_RE.search(text):
        return False
    m = _EXCLUSION_RE.search(text)
    if not m:
        return False
    return len(text[m.end():m.end() + 200].strip()) >= 4


def test_ac15_aggregate_sink_contract_fields_and_choice_declared():
    """AC-15 — 집계 산출물 경로·필드·택일·배제사유가 **동시에** 확정돼 있다.

    RTM: 5.3 verification "산출물 경로 문자열 2건 ∧ 필드명 3건 ∧ 택일 선언 마커 ∧
    배제 사유 non-empty **동시 충족**(단일 assert)".
    """
    # ★ 4 조건을 **고유 토큰이 든 별 줄**로 분리한다 — 한 줄에 두 조건이 섞이면 그 줄 하나를
    #   지우는 mutant 가 두 조건을 동시에 끄고(H-6 위반), 남은 문장이 다른 조건을 대신 만족시켜
    #   mutant 가 조용히 생존한다 (본 하네스가 2건 자기검출).
    line_paths = "산출물 = `%s` + `%s`.\n" % (AGG_PATHS[0], AGG_PATHS[1])
    line_fields = "필드 = `%s` / `%s` / `%s`.\n" % AGG_FIELDS
    line_choice = "도달 경로 = `_ROW_KEYS` 편입 쪽으로 택일한다.\n"
    line_excl = "배제 사유 — 원장을 직접 읽는 쪽은 이중 진실을 만든다.\n"
    control = line_paths + line_fields + line_choice + line_excl
    mutants = [
        ("경로 1건 삭제", control.replace(AGG_PATHS[1], "")),
        ("필드 1건 삭제", control.replace(AGG_FIELDS[0], "")),
        ("택일 선언 마커 삭제", control.replace(line_choice, "")),
        ("배제 사유 문단 삭제", control.replace(line_excl, "")),
        ("배제 사유 자리를 공란으로",
         control.replace(line_excl, "배제 사유 —\n")),
        ("공란", ""),
    ]
    green = [
        ("줄 순서 변경", line_excl + line_choice + line_fields + line_paths),
        ("필드 순서 변경",
         control.replace("`pattern_count` / `pattern_status`", "`pattern_status` / `pattern_count`")),
        ("주변 산문 추가", control + "\n이 선택은 4.4 가 확정한다.\n"),
    ]
    for nm, txt in mutants[:5]:
        assert txt != control, "mutant '%s' 주입 실패" % nm
    S.assert_discriminating(aggregate_sink_declared, control, mutants, green,
                            label="AC-15/aggregate-sink-declaration")

    plan = S.internal_docs_text(S.PLAN_REL)
    if plan is None:
        return
    assert aggregate_sink_declared(plan), (
        "Change Plan 4.4 에 집계 산출 계약 4항(경로 2 · 필드 3 · 택일 · 배제사유)이 "
        "동시 충족되지 않는다")
