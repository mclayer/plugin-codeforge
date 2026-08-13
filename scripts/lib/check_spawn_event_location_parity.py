#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_spawn_event_location_parity.py — CFP-2926 NG-10 spawn-event-v1 4-location parity.

**존재 이유**: 계약 개정(CFP-2926 Amendment 5 — `agent_start_at` / `agent_stop_at` /
`stop_time_source` 3 additive field)이 ★일부 location 에만 착지하는 형상★(부분 착지 =
born-broken)을 잡는다. Story §11.A.2 는 "lint 대조 4 location(#1~#4) + `amendment_log`(#5)
= 표 5행 전건을 단일 커밋에서 동시에 옮기지 않으면 lint RED. 하나라도 빠지면 born-broken"
을 명시한다.

**계수 규약 (Story §11.A.2 서두 blockquote)**: `N-location` = `amendment_log` 를 ★제외★ 한
수 = lint parity 대조 대상 수 = **4**. `amendment_log` 는 이력 append 라 heading↔표↔
`_ROW_KEYS` 상호 대조에 참여하지 않으므로 **계수에서 뺀다**. 단 ★커밋 원자성 대상에는
포함★ 되므로 본 게이트는 이를 **비계수(non-counted) 5번째 검사**로 실행한다 —
`trace.locations_compared` 는 규약대로 4 를 유지하고, `trace.amendment_log_checked` 로
분리 계상한다 (RTM §8.0.2 `test_spawn_event_schema_4location_parity` 행이 "heading/표/
`_ROW_KEYS`/amendment_log" 를 열거하는 것과 정합).

대조 location (Story §11.A.2 표 verbatim):

| # | location | 기대 |
|---|---|---|
| 1 | frontmatter `version` | `"1.2.1"` → **`"1.3.0"`** |
| 2 | `## 2. Schema (N개 필드 …)` heading 선언 수 | `23개` → **`26개`** |
| 3 | §2 필드 표 | 3 row 추가 (타입 열 = `ISO8601 UTC` / `enum` — ★free-form `string` 금지★) |
| 4 | `scripts/lib/append_spawn_event.py` `_ROW_KEYS` | 3 key 추가 (23 → 26) |
| 5 | `amendment_log` (★비계수★) | Amendment 5 (CFP-2926) append |

ADR-154 번들 4항목 (Story §8.0.8 (1) NG-10 행 verbatim):
  - `[154-AC-3]` empty  : ★resolve 된 location < 4 → **RED**★
      ⇒ 본 게이트는 generic default(`empty_target()` = INCONCLUSIVE)가 아니라 **per-gate
        spec 의 RED** 를 따른다 (§8.0.8 NG-10 행이 NG-15 의 INCONCLUSIVE 와 의도적으로
        갈라져 있음 — 더 엄격한 쪽). ★`0 == 0` 을 "통과"로 읽는 경로 0★
  - `[154-AC-4]` unknown: location 파일 unparseable → **fail-closed RED (exit 1)**
  - `[154-AC-5]` trace  : numeric — 대조 location 수(=4) · resolve 수 · match 수 · 파싱 행 수
  - ★셀 완전성 (F-CR-007 봉합)★: L3 은 이름·타입 2셀만 보던 정규식 파싱에 더해
    §2 표의 **header 열 수 ↔ 각 data row 셀 수** 를 별도로 센다. 5열 헤더에 4셀만 있는
    행(= 마지막 `Sanitize` 열 누락)이 본 Story 에서 3건 출생했는데 구 판본은 PASS 를 냈다.
    셀 수 불일치 = RED / §2 재추출 실패 = RED (fail-closed).
    ★한계★: 셀 *개수*만 본다 — 셀 *내용*의 정확성(예: `non-sensitive` 가 맞는 분류인가)은
    여전히 관측면 밖이다.
  - `[154-AC-13]` probe : resolved-target echo (실제로 무엇을 봤는지 — 경로·anchor·관측값).
      추출 수 0 → `EXTRACTION_EMPTY` fail-closed

★**경로 오타 = vacuous pass 고전형**★ — 대상 경로가 틀려 0 location 을 대조하고 GREEN 을
내면 게이트가 아니라 장식이다. 따라서 (a) 파일 부재/파싱 실패는 RED, (b) resolve 수를
trace 에 numeric 으로 노출, (c) 실제 resolve 된 경로를 identity_probe 에 echo 한다.

CLI:
    python scripts/lib/check_spawn_event_location_parity.py [--repo-root .]
        [--contract-path <spawn-event-v1.md>] [--append-path <append_spawn_event.py>]

exit: 0=PASS / 1=RED / 3=INCONCLUSIVE (gate_verdict SSOT)

★정직 — 본 게이트가 **검출하지 못하는** 축 (over-claim 금지):
  (a) **의미 정합 미검증**: 필드 *설명* 문면이 실제 의미와 맞는지(예: 두 필드의 설명이
      서로 뒤바뀐 경우)는 보지 않는다. 이름·타입 토큰·개수·위치만 본다.
  (b) **원자성(단일 커밋) 미검증**: "동시에 옮겼는가"가 아니라 "현재 트리에 전부 있는가"
      만 본다. 4 location 을 4 커밋에 나눠 넣어도 최종 상태가 같으면 PASS 다.
  (c) **runtime 행 미검증**: 실제 원장 row 가 3 필드를 채우는지는 무관 (그 축 = NG-16 /
      AC-2b 산출기). 본 게이트는 계약 문면 ↔ code anchor 정적 대조다.
  (d) **타입 토큰 = presence 휴리스틱**: 타입 셀에 `ISO8601`/`enum` 문자열이 있는지만 본다.
      셀이 의미상 옳은 타입인지는 판정하지 않는다.
  (e) **자원 안전성**: 단일 문서 1회 read + anchored 정규식 선형 스캔이라는 **bounded
      degradation 선언**이며, "임의 입력 무해(ReDoS-safe)" 단정이 아니다 — 복잡도 회귀
      self-test·wall-clock 벤치마크 미동반 (ADR-168 §결정 16 honest-ceiling).
"""

import argparse
import importlib.util
import json
import os
import re
import sys

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gate_verdict import GateResult, emit, unknown_input, PASS, RED  # noqa: E402

# ★reuse-before-write (ADR-140)★ — §2 표 실파싱 / heading 선언 수 파서는
# check_spawn_event_schema.py 가 **이미 보유**한다 (F-CR-003 에서 하드코딩 상수를 걷어내고
# doc-parse 로 재작성된 그 파서). 신규 파서 작성 = 중복 유입이므로 그대로 import 재사용한다
# (선례: check_platform_inherent_prose → check_fanout_subject_prose, check_harness_temp_residue
# → check_orphan_worktree_classify).
import check_spawn_event_schema as ses  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-10"

_DEFAULT_CONTRACT_REL = os.path.join(
    "docs", "inter-plugin-contracts", "spawn-event-v1.md"
)
_DEFAULT_APPEND_REL = os.path.join("scripts", "lib", "append_spawn_event.py")

# ── 기대값 (Story §11.A.1 / §11.A.2 표) ──────────────────────────────────────
_TARGET_VERSION = "1.3.0"
_TARGET_FIELD_COUNT = 26
_ADDITIVE_FIELDS = ("agent_start_at", "agent_stop_at", "stop_time_source")
# 타입 열 요구 토큰 — ★free-form `string` 금지★ (§11.A.2 #3 / T-INFO-8)
_ADDITIVE_TYPE_TOKENS = {
    "agent_start_at": "iso8601",
    "agent_stop_at": "iso8601",
    "stop_time_source": "enum",
}
_AMENDMENT_LABEL = "Amendment 5"
_AMENDMENT_CARRIER = "CFP-2926"

# 계수 규약: amendment_log 제외 (§11.A.2 서두)
_COUNTED_LOCATIONS = 4


# ─────────────────────── 입력 resolve ────────────────────────────────────────

def _read_contract(contract_path):
    """계약 문서 read + frontmatter split.

    Returns (status, fm, body).
      status: "ok" | "missing" | "unreadable:<err>" | "frontmatter_unparseable"
    """
    if not os.path.isfile(contract_path):
        return "missing", None, ""
    try:
        with open(contract_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception as exc:  # pragma: no cover - I/O 예외 경로
        return "unreadable:%s" % str(exc)[:80], None, ""
    fm, body = ses._split_frontmatter(text)  # 동일 계열 파서 재사용 (doc-parse SSOT)
    if not isinstance(fm, dict):
        return "frontmatter_unparseable", None, body
    return "ok", fm, body


def _load_row_keys(append_path):
    """`_ROW_KEYS` code-import (parity set B).

    ★파일 경로 지정 import★ — 게이트의 핵심 실패축이 "경로 오타 = vacuous pass" 이므로
    module-name import 가 아니라 **resolve 된 경로** 를 그대로 load 하고 그 경로를
    identity_probe 에 echo 한다.

    Returns (row_keys_tuple | None, status).
      status: "ok" | "missing" | "import_error:<err>" | "attr_missing"
    """
    if not os.path.isfile(append_path):
        return None, "missing"
    lib_dir = os.path.dirname(os.path.abspath(append_path))
    mod_stem = os.path.splitext(os.path.basename(append_path))[0]
    inserted = lib_dir not in sys.path
    if inserted:
        sys.path.insert(0, lib_dir)
    try:
        spec = importlib.util.spec_from_file_location(
            "_ng10_parity_%s" % mod_stem, append_path
        )
        if spec is None or spec.loader is None:
            return None, "import_error:spec_none"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:
        return None, "import_error:%s" % str(exc)[:80]
    finally:
        if inserted and lib_dir in sys.path:
            try:
                sys.path.remove(lib_dir)
            except ValueError:  # pragma: no cover
                pass
    keys = getattr(mod, "_ROW_KEYS", None)
    if not keys:
        return None, "attr_missing"
    return tuple(keys), "ok"


# ─────────────────────── location 별 판정 ────────────────────────────────────

def _loc(loc_id, anchor, source, resolved, ok, observed, detail=""):
    """location 판정 record (identity_probe echo 단위)."""
    return {
        "id": loc_id,
        "anchor": anchor,
        "source": source,
        "resolved": bool(resolved),
        "ok": bool(ok),
        "observed": observed,
        "detail": detail,
    }


def _check_frontmatter_version(fm, contract_path):
    if not isinstance(fm, dict) or "version" not in fm:
        return _loc(
            "L1_frontmatter_version", "version:", contract_path, False, False, None,
            "frontmatter `version` 키 미해석",
        )
    observed = str(fm.get("version"))
    ok = observed == _TARGET_VERSION
    return _loc(
        "L1_frontmatter_version", "version:", contract_path, True, ok, observed,
        "" if ok else "기대 %r ≠ 실측 %r" % (_TARGET_VERSION, observed),
    )


def _check_heading_declared_count(body, contract_path):
    declared = ses.parse_declared_field_count(body)
    if declared is None:
        return _loc(
            "L2_section2_heading_count", "## 2. Schema (N개 필드 …)", contract_path,
            False, False, None, "heading 선언 수 미해석 (heading rename / 형식 이탈)",
        )
    ok = declared == _TARGET_FIELD_COUNT
    return _loc(
        "L2_section2_heading_count", "## 2. Schema (N개 필드 …)", contract_path,
        True, ok, declared,
        "" if ok else "기대 %d ≠ 선언 %d" % (_TARGET_FIELD_COUNT, declared),
    )


def _split_md_cells(row):
    r"""markdown 표 한 줄 → 셀 리스트. ``\|`` (escaped pipe) 는 구분자로 세지 않는다."""
    inner = row.strip()
    inner = inner[1:] if inner.startswith("|") else inner
    inner = inner[:-1] if inner.endswith("|") else inner
    cells, buf, esc = [], "", False
    for ch in inner:
        if esc:
            buf += ch
            esc = False
        elif ch == "\\":
            esc = True
            buf += ch
        elif ch == "|":
            cells.append(buf)
            buf = ""
        else:
            buf += ch
    cells.append(buf)
    return cells


_MD_SEPARATOR_RE = re.compile(r"^\|[\s:|-]+\|?$")


def scan_section2_cell_counts(body):
    """§2 표의 header 셀 수 ↔ 각 data row 셀 수 대조 → (header_n, [(row_no, first_cell, n), ...]).

    ★왜 필요한가 (F-CR-007)★: 기존 파싱(`parse_section2_fields`)은 정규식으로 ``| `name` |
    타입 |`` 앞 2 셀만 떠서 ★행이 5열 헤더에 4셀만 갖고 있어도 PASS★ 였다. 실제로 본
    Story 가 그 형상의 행 3개(`termination_cause`/`agent_start_at`/`agent_stop_at`)를
    출생시켰고 게이트는 침묵했다. 셀 완전성은 별 축이므로 별도로 센다.

    반환 2번째 원소 = ★헤더와 셀 수가 다른 행만★ (정상 행은 담지 않는다).
    header 를 못 찾으면 (None, []) — caller 가 fail-closed 처리.
    """
    section2 = ses._extract_section(body, r"(?m)^##\s*2\.\s", r"(?m)^##\s*2\.1")
    if section2 is None:
        return None, []
    section2 = ses._strip_fenced_blocks(section2)
    header_n = None
    mismatches = []
    for row_no, line in enumerate(section2.split("\n"), 1):
        s = line.strip()
        if not s.startswith("|"):
            continue
        if _MD_SEPARATOR_RE.match(s):
            continue
        cells = _split_md_cells(s)
        if header_n is None:
            header_n = len(cells)
            continue
        if len(cells) != header_n:
            first = cells[0].strip() if cells else ""
            mismatches.append((row_no, first, len(cells)))
    return header_n, mismatches


def _check_field_table(parsed_fields, contract_path, body=None):
    if not parsed_fields:
        return _loc(
            "L3_section2_field_table", "§2 필드 표", contract_path,
            False, False, 0, "EXTRACTION_EMPTY — §2 표 data row 0건 (파싱 실패/섹션 이동)",
        )
    names = [n for n, _t in parsed_fields]
    types = {n: t for n, t in parsed_fields}
    problems = []
    if len(names) != _TARGET_FIELD_COUNT:
        problems.append("표 실측 %d행 ≠ 기대 %d행" % (len(names), _TARGET_FIELD_COUNT))
    # ★셀 완전성★ (F-CR-007) — header 열 수와 다른 data row = RED.
    if body is not None:
        header_n, mismatches = scan_section2_cell_counts(body)
        if header_n is None:
            problems.append("§2 섹션 재추출 실패 — 셀 완전성 미검사 (fail-closed)")
        elif mismatches:
            problems.append(
                "셀 수 불일치 %d행 (header %d열): %s"
                % (
                    len(mismatches),
                    header_n,
                    ", ".join("%s=%d셀" % (name or "?", n) for _r, name, n in mismatches),
                )
            )
    for field in _ADDITIVE_FIELDS:
        if field not in types:
            problems.append("additive field `%s` 미착지" % field)
            continue
        token = _ADDITIVE_TYPE_TOKENS[field]
        cell = types[field].lower()
        if token not in cell:
            problems.append(
                "`%s` 타입 열 = %r — 요구 토큰 %r 부재 (free-form string 금지)"
                % (field, types[field], token)
            )
    return _loc(
        "L3_section2_field_table", "§2 필드 표", contract_path,
        True, not problems, len(names), " / ".join(problems),
    )


def _check_row_keys(row_keys, status, append_path):
    if row_keys is None:
        return _loc(
            "L4_append_row_keys", "_ROW_KEYS", append_path, False, False, 0,
            "code anchor 미해석 (%s)" % status,
        )
    problems = []
    if len(row_keys) != _TARGET_FIELD_COUNT:
        problems.append(
            "_ROW_KEYS %d개 ≠ 기대 %d개" % (len(row_keys), _TARGET_FIELD_COUNT)
        )
    for field in _ADDITIVE_FIELDS:
        if field not in row_keys:
            problems.append("additive key `%s` 미착지" % field)
    return _loc(
        "L4_append_row_keys", "_ROW_KEYS", append_path, True, not problems,
        len(row_keys), " / ".join(problems),
    )


def _check_amendment_log(fm, contract_path):
    """★비계수★ 5번째 location — `amendment_log` Amendment 5 (CFP-2926) append.

    계수(`locations_compared`)에는 넣지 않으나 (§11.A.2 계수 규약), 커밋 원자성 대상이므로
    verdict 에는 참여한다 ("표 5행 전건 … 하나라도 빠지면 born-broken").
    """
    log = fm.get("amendment_log") if isinstance(fm, dict) else None
    if not isinstance(log, list) or not log:
        return _loc(
            "L5_amendment_log", "amendment_log", contract_path, False, False, 0,
            "amendment_log 미해석 또는 공목록",
        )
    hit = 0
    for entry in log:
        # default=str — dict 형 entry 에 YAML date 스칼라가 있으면 순수 dumps 는 TypeError
        # (dev-process-event-v1 amendment_log 의 실 형상. 본 계약은 문자열 entry 지만
        #  형식 변경에 대해 fail-safe 하게 둔다).
        text = (
            entry if isinstance(entry, str)
            else json.dumps(entry, ensure_ascii=False, default=str)
        )
        if _AMENDMENT_LABEL in text and _AMENDMENT_CARRIER in text:
            hit += 1
    ok = hit > 0
    return _loc(
        "L5_amendment_log", "amendment_log", contract_path, True, ok, len(log),
        "" if ok else "`%s` + `%s` 항목 부재" % (_AMENDMENT_LABEL, _AMENDMENT_CARRIER),
    )


# ─────────────────────── evaluate ────────────────────────────────────────────

def evaluate(contract_path, append_path):
    """4 counted location + 1 non-counted(amendment_log) 대조 → GateResult."""
    status, fm, body = _read_contract(contract_path)

    parsed_fields = ses.parse_section2_fields(body) if status == "ok" else []
    row_keys, rk_status = _load_row_keys(append_path)

    if status == "ok":
        locations = [
            _check_frontmatter_version(fm, contract_path),
            _check_heading_declared_count(body, contract_path),
            _check_field_table(parsed_fields, contract_path, body),
            _check_row_keys(row_keys, rk_status, append_path),
        ]
        amendment = _check_amendment_log(fm, contract_path)
    else:
        # 계약 문서 자체가 미해석 → 계약측 3 location 전부 unresolved.
        # ★경로 오타/파일 부재가 여기로 떨어진다 — GREEN 경로 없음★
        unresolved_detail = "계약 문서 미해석 (%s)" % status
        locations = [
            _loc("L1_frontmatter_version", "version:", contract_path,
                 False, False, None, unresolved_detail),
            _loc("L2_section2_heading_count", "## 2. Schema (N개 필드 …)", contract_path,
                 False, False, None, unresolved_detail),
            _loc("L3_section2_field_table", "§2 필드 표", contract_path,
                 False, False, 0, unresolved_detail),
            _check_row_keys(row_keys, rk_status, append_path),
        ]
        amendment = _loc(
            "L5_amendment_log", "amendment_log", contract_path,
            False, False, 0, unresolved_detail,
        )

    all_checks = locations + [amendment]
    resolved = sum(1 for entry in locations if entry["resolved"])
    matched = sum(1 for entry in locations if entry["resolved"] and entry["ok"])

    trace = {
        "locations_compared": _COUNTED_LOCATIONS,
        "locations_resolved": resolved,
        "locations_matched": matched,
        "amendment_log_checked": 1,
        "amendment_log_matched": 1 if amendment["ok"] else 0,
        "section2_rows_parsed": len(parsed_fields),
        "row_keys_count": len(row_keys) if row_keys else 0,
        "expected_field_count": _TARGET_FIELD_COUNT,
    }
    identity_probe = {
        "contract_path": contract_path,
        "append_path": append_path,
        "contract_status": status,
        "row_keys_status": rk_status,
        "extraction": "EXTRACTION_EMPTY" if not parsed_fields else "OK",
        "locations": all_checks,
    }

    # (1) unknown-input fail-closed [154-AC-4] — 파싱 불가 입력은 조용히 제외하지 않는다
    if status != "ok":
        return unknown_input(
            gate_id=GATE_ID,
            reason="UNKNOWN_INPUT_CONTRACT_%s" % status.split(":")[0].upper(),
            trace=trace,
            identity_probe=identity_probe,
        )
    if rk_status.startswith("import_error"):
        return unknown_input(
            gate_id=GATE_ID,
            reason="UNKNOWN_INPUT_APPEND_MODULE_UNPARSEABLE",
            trace=trace,
            identity_probe=identity_probe,
        )
    if not parsed_fields:
        return unknown_input(
            gate_id=GATE_ID,
            reason="EXTRACTION_EMPTY_SECTION2_TABLE",
            trace=trace,
            identity_probe=identity_probe,
        )

    # (2) empty-target [154-AC-3] — resolve < 4 → ★RED★ (per-gate spec, §8.0.8 NG-10 행)
    if resolved < _COUNTED_LOCATIONS:
        unresolved = [e["id"] for e in locations if not e["resolved"]]
        return GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="EMPTY_TARGET_LOCATIONS_UNRESOLVED: %d/%d resolve — %s"
                   % (resolved, _COUNTED_LOCATIONS, ", ".join(unresolved)),
            trace=trace,
            identity_probe=identity_probe,
        )

    # (3) parity mismatch — 부분 착지 검출 (본 게이트의 존재 이유)
    failed = [e for e in all_checks if not e["ok"]]
    if failed:
        return GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="LOCATION_PARITY_MISMATCH (%d/%d location): %s"
                   % (len(failed), len(all_checks),
                      " | ".join("%s: %s" % (e["id"], e["detail"]) for e in failed)),
            trace=trace,
            identity_probe=identity_probe,
        )

    return GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="spawn-event-v1 %s — 4 counted location + amendment_log 전건 착지"
               % _TARGET_VERSION,
        trace=trace,
        identity_probe=identity_probe,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_spawn_event_location_parity.py",
        description="CFP-2926 NG-10 — spawn-event-v1 4-location parity (Story §11.A.2).",
    )
    parser.add_argument("--repo-root", default=".", help="repo 루트 (default: .)")
    parser.add_argument(
        "--contract-path", default=None,
        help="spawn-event-v1.md 경로 (default: <repo-root>/%s)" % _DEFAULT_CONTRACT_REL,
    )
    parser.add_argument(
        "--append-path", default=None,
        help="append_spawn_event.py 경로 (default: <repo-root>/%s)" % _DEFAULT_APPEND_REL,
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    repo_root = os.path.abspath(args.repo_root)
    contract_path = args.contract_path or os.path.join(repo_root, _DEFAULT_CONTRACT_REL)
    append_path = args.append_path or os.path.join(repo_root, _DEFAULT_APPEND_REL)

    return emit(evaluate(contract_path, append_path))


if __name__ == "__main__":
    sys.exit(main())
