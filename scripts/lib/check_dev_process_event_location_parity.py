#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_dev_process_event_location_parity.py — CFP-2926 NG-11 dev-process-event-v1 5-location parity.

**존재 이유**: 계약 개정(CFP-2926 Amendment 1 — `writer_key` / `artifact_key` ★additive
2필드★)이 ★일부 location 에만 착지하는 형상★(부분 착지 = born-broken)을 잡는다.
Story §11.A.3 는 "lint 대조 5 location(#1~#5) + `amendment_log`(#6) = 표 6행 전건이 단일
커밋" 을 명시하며, ★#4 `§2.1 declared allow-list 코드블록`★ 은 브리핑이 누락했던
location 이다 (3-location → 5-location 정정 carrier).

**계수 규약 (Story §11.A.2 서두 blockquote, §11.A.3 가 상속)**: `N-location` =
`amendment_log` ★제외★ = lint parity 대조 대상 수 = **5**. `amendment_log` 는 이력 append 라
heading↔표↔allow-list↔`_ROW_KEYS` 상호 대조에 참여하지 않으므로 계수에서 뺀다. 단 커밋
원자성 대상에는 포함되므로 본 게이트는 **비계수(non-counted) 6번째 검사**로 실행한다
(`trace.locations_compared` = 5 유지, `trace.amendment_log_checked` 분리 계상 — RTM §8.0.2
`test_dev_process_event_5location_parity` 행의 "heading/표/§2.1 allow-list/`_ROW_KEYS`/
amendment_log" 열거와 정합).

대조 location (Story §11.A.3 표 verbatim):

| # | location | 기대 |
|---|---|---|
| 1 | frontmatter `version` | `"1.0"` → **`"1.1"`** |
| 2 | `## 2. Schema (index tier — N 필드 …)` | `18 필드` → **`20 필드`** |
| 3 | §2 필드 표 | 2 row 추가 (`#19` `writer_key` / `#20` `artifact_key`, 타입 = **sha256 string**) |
| 4 | ★**§2.1 declared allow-list 코드블록**★ | 2 원소 추가 (브리핑 미언급 location) |
| 5 | `scripts/lib/append_dev_process_event.py` `_ROW_KEYS` | 2 key 추가 (18 → 20) |
| 6 | `amendment_log` (★비계수★) | Amendment 1 (CFP-2926) append |

★`first_write` / `last_write` 는 계약 필드가 **아니다**★ — Story §7.5.3 P2 술어
("`(writer_key, artifact_key)` 별 `[first_write, last_write)` 반개구간")의 **파생 구간
끝점**이며, timestamp 열을 `(writer_key, artifact_key)` 로 group 해 **산출**하는 값이다.
따라서 본 게이트의 기대 필드 집합은 `writer_key` · `artifact_key` **2개** 뿐이다
(§7.5.3 = "additive 2필드", §11.A.3 #3 = "2 row 추가").

ADR-154 번들 4항목 (Story §8.0.8 (1) NG-11 행 — NG-10 "동상"):
  - `[154-AC-3]` empty  : ★resolve 된 location < 5 → **RED**★ (generic INCONCLUSIVE default
      가 아니라 per-gate spec 의 RED — §8.0.8 NG-11 행이 NG-15 와 의도적으로 갈라짐)
  - `[154-AC-4]` unknown: location 파일 unparseable → **fail-closed RED (exit 1)**
  - `[154-AC-5]` trace  : numeric — 대조 location 수(=5) · resolve 수 · match 수 · 파싱 행 수
  - `[154-AC-13]` probe : resolved-target echo. 추출 수 0 → `EXTRACTION_EMPTY` fail-closed

★**경로 오타 = vacuous pass 고전형**★ — 0 location 을 대조하고 GREEN 을 내면 게이트가
아니라 장식이다. 파일 부재/파싱 실패 = RED, resolve 수 = numeric trace, resolve 된 경로 =
identity_probe echo.

CLI:
    python scripts/lib/check_dev_process_event_location_parity.py [--repo-root .]
        [--contract-path <dev-process-event-v1.md>]
        [--append-path <append_dev_process_event.py>]

exit: 0=PASS / 1=RED / 3=INCONCLUSIVE (gate_verdict SSOT)

★정직 — 본 게이트가 **검출하지 못하는** 축 (over-claim 금지):
  (a) **의미 정합 미검증**: 필드 *설명* 문면의 정확성은 보지 않는다. 이름·타입 토큰·행
      번호·개수만 본다. ★실증 사례★ — 본 Story 착수 시점 계약 §2 는 `writer_key`/
      `artifact_key` 의 **설명이 서로 뒤바뀌어** 있었고(§7.5.3 = writer_key sha256(agent_id)),
      본 게이트는 그 상태를 **PASS 로 통과시켰다**. 그 뒤바뀜은 같은 PR 의 커밋
      `4a8d000d8`("계약 §2 표 writer_key/artifact_key 설명 뒤바뀜 정정")이 **이미 수정**했다
      — 즉 현행 계약 문면은 정상이고, 여기 남는 것은 "본 게이트가 이 축을 보지 못한다"는
      **능력 한계 선언**뿐이다. (구 문면은 이를 현재시제 미수정으로 단정해 사실·귀속 둘 다
      거짓이었다 — 구현리뷰 F-CR-006.)
  (b) **원자성(단일 커밋) 미검증**: 최종 트리 상태만 본다. 5 location 을 5 커밋에 나눠도
      최종 상태가 같으면 PASS.
  (c) **hash 값 정확성 미검증**: 실제 append 가 sha256 을 넣는지, 경로 원문이 새는지는
      무관 (그 축 = check_dev_process_event_schema / redaction 게이트).
  (d) **타입 토큰 = presence 휴리스틱**: 타입 셀에 `sha256` 문자열이 있는지만 본다.
  (e) **자원 안전성**: 단일 문서 1회 read + anchored 정규식 선형 스캔이라는 **bounded
      degradation 선언**이며 "임의 입력 무해(ReDoS-safe)" 단정이 아니다 — 복잡도 회귀
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

# ★reuse-before-write (ADR-140)★ — §2 index 필드 표 파서 / §2.1 declared allow-list 파서 /
# frontmatter split 은 check_dev_process_event_schema.py 가 **이미 보유**(동 계약의 doc-parse
# SSOT). 신규 파서 작성 = 중복 유입이므로 그대로 import 재사용한다. 본 파일이 추가로 쓰는
# 것은 (i) heading 선언 수 파서(dev-process heading 방언 `N 필드` — spawn 의 `N개` 파서와
# 형식이 달라 sibling 이 미보유) (ii) 타입 열 조회기(sibling 은 필드명만 노출) 2개뿐이며,
# 둘 다 sibling 의 `_extract_section` 위에 얹은 **확장**이다 (섹션 추출 재구현 0).
import check_dev_process_event_schema as dpes  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 플랫폼 의존
        pass

GATE_ID = "NG-11"

_DEFAULT_CONTRACT_REL = os.path.join(
    "docs", "inter-plugin-contracts", "dev-process-event-v1.md"
)
_DEFAULT_APPEND_REL = os.path.join("scripts", "lib", "append_dev_process_event.py")

# ── 기대값 (Story §11.A.1 / §11.A.3 표 / §7.5.3) ──────────────────────────────
_TARGET_VERSION = "1.1"
_TARGET_FIELD_COUNT = 20
# ★additive 2필드 — first_write/last_write 는 계약 필드 아님 (P2 술어의 파생 구간 끝점)★
_ADDITIVE_FIELDS = ("writer_key", "artifact_key")
_ADDITIVE_ROW_INDEX = {"writer_key": 19, "artifact_key": 20}  # §11.A.3 #3 `#19`/`#20`
_ADDITIVE_TYPE_TOKEN = "sha256"  # 타입 = sha256 string (§11.A.3 #3 / §7.5.3)
_AMENDMENT_CARRIER = "CFP-2926"
_AMENDMENT_LABELS = ("Amendment 1", "A1")  # 문자열 entry / dict entry(id: A1) 양형

# 계수 규약: amendment_log 제외 (§11.A.2 서두 → §11.A.3 상속)
_COUNTED_LOCATIONS = 5

_SECTION2_START = r"(?m)^##\s*2\.\s"
_SECTION2_END = r"(?m)^###\s*2\.1"
# `| 19 | `writer_key` | sha256 string | ...` — sibling `parse_index_fields` 와 동일 행
# 형상이되 **행 번호 + 타입 열**까지 캡처 (sibling 은 필드명만 반환).
_INDEX_ROW_RE = re.compile(r"(?m)^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|([^|]*)\|")
# `## 2. Schema (index tier — 20 필드 Allow-list ONLY)` heading 방언
_DECLARED_COUNT_RE = re.compile(r"(?m)^##\s*2\.\s*Schema\s*\(([^)\n]*)\)")
_COUNT_IN_PAREN_RE = re.compile(r"(\d+)\s*필드")


# ─────────────────────── 입력 resolve ────────────────────────────────────────

def _read_contract(contract_path):
    """계약 문서 read + frontmatter 분리.

    sibling `_split_frontmatter` 는 본문만 반환하므로(frontmatter dict 미노출)
    frontmatter 는 yaml 로 별도 파싱한다.

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
    body = dpes._split_frontmatter(text)  # 동일 계열 파서 재사용 (doc-parse SSOT)
    if not text.startswith("---\n") or "\n---\n" not in text:
        return "frontmatter_unparseable", None, body
    try:
        import yaml
        fm = yaml.safe_load(text.split("\n---\n", 1)[0][4:])
    except Exception:
        return "frontmatter_unparseable", None, body
    if not isinstance(fm, dict):
        return "frontmatter_unparseable", None, body
    return "ok", fm, body


def _parse_declared_field_count(body):
    """§2 heading 이 선언한 필드 개수 (`## 2. Schema (index tier — 20 필드 …)`) → int|None.

    spawn-event 의 `(\\d+)개 필드` 방언과 형식이 달라 sibling 파서를 못 쓴다 (신규 개념 0 —
    같은 "heading 선언 수 ↔ 표 실측" 대조축의 방언 어댑터).
    """
    m = _DECLARED_COUNT_RE.search(body)
    if not m:
        return None
    m2 = _COUNT_IN_PAREN_RE.search(m.group(1))
    return int(m2.group(1)) if m2 else None


def _parse_index_rows(body):
    """§2 표 행 → {field_name: (row_index, type_cell)}.

    sibling `parse_index_fields` 가 반환하지 않는 **행 번호 + 타입 열** 조회용 확장.
    섹션 추출은 sibling `_extract_section` 재사용 (재구현 0).
    """
    section2 = dpes._extract_section(body, _SECTION2_START, _SECTION2_END)
    if section2 is None:
        return {}
    rows = {}
    for m in _INDEX_ROW_RE.finditer(section2):
        rows[m.group(2).strip()] = (int(m.group(1)), m.group(3).strip())
    return rows


def _load_row_keys(append_path):
    """`_ROW_KEYS` code-import (parity set B).

    ★파일 경로 지정 import★ — 핵심 실패축이 "경로 오타 = vacuous pass" 이므로 module-name
    import(sibling `import_row_keys` 는 repo_root 기반 name import)가 아니라 **resolve 된
    경로** 를 load 하고 그 경로를 identity_probe 에 echo 한다.

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
            "_ng11_parity_%s" % mod_stem, append_path
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
    declared = _parse_declared_field_count(body)
    if declared is None:
        return _loc(
            "L2_section2_heading_count", "## 2. Schema (index tier — N 필드 …)",
            contract_path, False, False, None,
            "heading 선언 수 미해석 (heading rename / 형식 이탈)",
        )
    ok = declared == _TARGET_FIELD_COUNT
    return _loc(
        "L2_section2_heading_count", "## 2. Schema (index tier — N 필드 …)",
        contract_path, True, ok, declared,
        "" if ok else "기대 %d ≠ 선언 %d" % (_TARGET_FIELD_COUNT, declared),
    )


def _check_field_table(index_fields, index_rows, contract_path):
    if not index_fields:
        return _loc(
            "L3_section2_field_table", "§2 필드 표", contract_path,
            False, False, 0, "EXTRACTION_EMPTY — §2 표 data row 0건 (파싱 실패/섹션 이동)",
        )
    problems = []
    if len(index_fields) != _TARGET_FIELD_COUNT:
        problems.append(
            "표 실측 %d행 ≠ 기대 %d행" % (len(index_fields), _TARGET_FIELD_COUNT)
        )
    for field in _ADDITIVE_FIELDS:
        if field not in index_rows:
            problems.append("additive field `%s` 미착지" % field)
            continue
        row_idx, type_cell = index_rows[field]
        want_idx = _ADDITIVE_ROW_INDEX[field]
        if row_idx != want_idx:
            problems.append(
                "`%s` 행 번호 %d ≠ 기대 #%d" % (field, row_idx, want_idx)
            )
        if _ADDITIVE_TYPE_TOKEN not in type_cell.lower():
            problems.append(
                "`%s` 타입 열 = %r — 요구 토큰 %r 부재 (index tier free-form 금지)"
                % (field, type_cell, _ADDITIVE_TYPE_TOKEN)
            )
    return _loc(
        "L3_section2_field_table", "§2 필드 표", contract_path,
        True, not problems, len(index_fields), " / ".join(problems),
    )


def _check_declared_allowlist(allowlist, contract_path):
    """★#4 — §2.1 declared allow-list 코드블록 (브리핑 미언급 location)★."""
    if not allowlist:
        return _loc(
            "L4_declared_allowlist", "§2.1 declared allow-list 코드블록", contract_path,
            False, False, 0,
            "EXTRACTION_EMPTY — allow-list 코드블록 0 원소 (섹션/fence 이동)",
        )
    problems = []
    if len(allowlist) != _TARGET_FIELD_COUNT:
        problems.append(
            "allow-list %d원소 ≠ 기대 %d원소" % (len(allowlist), _TARGET_FIELD_COUNT)
        )
    for field in _ADDITIVE_FIELDS:
        if field not in allowlist:
            problems.append("allow-list 에 `%s` 미착지" % field)
    return _loc(
        "L4_declared_allowlist", "§2.1 declared allow-list 코드블록", contract_path,
        True, not problems, len(allowlist), " / ".join(problems),
    )


def _check_row_keys(row_keys, status, append_path):
    if row_keys is None:
        return _loc(
            "L5_append_row_keys", "_ROW_KEYS", append_path, False, False, 0,
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
        "L5_append_row_keys", "_ROW_KEYS", append_path, True, not problems,
        len(row_keys), " / ".join(problems),
    )


def _check_amendment_log(fm, contract_path):
    """★비계수★ 6번째 location — `amendment_log` Amendment 1 (CFP-2926) append."""
    log = fm.get("amendment_log") if isinstance(fm, dict) else None
    if not isinstance(log, list) or not log:
        return _loc(
            "L6_amendment_log", "amendment_log", contract_path, False, False, 0,
            "amendment_log 미해석 또는 공목록",
        )
    hit = 0
    for entry in log:
        # default=str — YAML 이 `date: 2026-08-12` 를 datetime.date 로 실체화하므로
        # 순수 json.dumps 는 TypeError 를 낸다 (dict 형 entry 의 실 형상).
        text = (
            entry if isinstance(entry, str)
            else json.dumps(entry, ensure_ascii=False, default=str)
        )
        if _AMENDMENT_CARRIER in text and any(lbl in text for lbl in _AMENDMENT_LABELS):
            hit += 1
    ok = hit > 0
    return _loc(
        "L6_amendment_log", "amendment_log", contract_path, True, ok, len(log),
        "" if ok else "`%s` + %s 항목 부재"
                      % (_AMENDMENT_CARRIER, " | ".join(_AMENDMENT_LABELS)),
    )


# ─────────────────────── evaluate ────────────────────────────────────────────

def evaluate(contract_path, append_path):
    """5 counted location + 1 non-counted(amendment_log) 대조 → GateResult."""
    status, fm, body = _read_contract(contract_path)

    if status == "ok":
        index_fields = dpes.parse_index_fields(body)      # sibling 재사용 (이름·순서)
        index_rows = _parse_index_rows(body)              # 확장 (행 번호·타입 열)
        allowlist = dpes.parse_declared_allowlist(body)   # sibling 재사용 (§2.1)
    else:
        index_fields, index_rows, allowlist = [], {}, set()

    row_keys, rk_status = _load_row_keys(append_path)

    if status == "ok":
        locations = [
            _check_frontmatter_version(fm, contract_path),
            _check_heading_declared_count(body, contract_path),
            _check_field_table(index_fields, index_rows, contract_path),
            _check_declared_allowlist(allowlist, contract_path),
            _check_row_keys(row_keys, rk_status, append_path),
        ]
        amendment = _check_amendment_log(fm, contract_path)
    else:
        # ★경로 오타/파일 부재가 여기로 떨어진다 — GREEN 경로 없음★
        detail = "계약 문서 미해석 (%s)" % status
        locations = [
            _loc("L1_frontmatter_version", "version:", contract_path,
                 False, False, None, detail),
            _loc("L2_section2_heading_count", "## 2. Schema (index tier — N 필드 …)",
                 contract_path, False, False, None, detail),
            _loc("L3_section2_field_table", "§2 필드 표", contract_path,
                 False, False, 0, detail),
            _loc("L4_declared_allowlist", "§2.1 declared allow-list 코드블록",
                 contract_path, False, False, 0, detail),
            _check_row_keys(row_keys, rk_status, append_path),
        ]
        amendment = _loc("L6_amendment_log", "amendment_log", contract_path,
                         False, False, 0, detail)

    all_checks = locations + [amendment]
    resolved = sum(1 for entry in locations if entry["resolved"])
    matched = sum(1 for entry in locations if entry["resolved"] and entry["ok"])

    trace = {
        "locations_compared": _COUNTED_LOCATIONS,
        "locations_resolved": resolved,
        "locations_matched": matched,
        "amendment_log_checked": 1,
        "amendment_log_matched": 1 if amendment["ok"] else 0,
        "section2_rows_parsed": len(index_fields),
        "declared_allowlist_size": len(allowlist),
        "row_keys_count": len(row_keys) if row_keys else 0,
        "expected_field_count": _TARGET_FIELD_COUNT,
    }
    identity_probe = {
        "contract_path": contract_path,
        "append_path": append_path,
        "contract_status": status,
        "row_keys_status": rk_status,
        "extraction": (
            "EXTRACTION_EMPTY" if (not index_fields or not allowlist) else "OK"
        ),
        "additive_fields_expected": list(_ADDITIVE_FIELDS),
        "locations": all_checks,
    }

    # (1) unknown-input fail-closed [154-AC-4]
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
    if not index_fields or not allowlist:
        return unknown_input(
            gate_id=GATE_ID,
            reason="EXTRACTION_EMPTY_SECTION2_OR_ALLOWLIST",
            trace=trace,
            identity_probe=identity_probe,
        )

    # (2) empty-target [154-AC-3] — resolve < 5 → ★RED★ (per-gate spec, §8.0.8 NG-11 행)
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
        reason="dev-process-event-v1 %s — 5 counted location + amendment_log 전건 착지"
               % _TARGET_VERSION,
        trace=trace,
        identity_probe=identity_probe,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_dev_process_event_location_parity.py",
        description="CFP-2926 NG-11 — dev-process-event-v1 5-location parity (Story §11.A.3).",
    )
    parser.add_argument("--repo-root", default=".", help="repo 루트 (default: .)")
    parser.add_argument(
        "--contract-path", default=None,
        help="dev-process-event-v1.md 경로 (default: <repo-root>/%s)"
             % _DEFAULT_CONTRACT_REL,
    )
    parser.add_argument(
        "--append-path", default=None,
        help="append_dev_process_event.py 경로 (default: <repo-root>/%s)"
             % _DEFAULT_APPEND_REL,
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    repo_root = os.path.abspath(args.repo_root)
    contract_path = args.contract_path or os.path.join(repo_root, _DEFAULT_CONTRACT_REL)
    append_path = args.append_path or os.path.join(repo_root, _DEFAULT_APPEND_REL)

    return emit(evaluate(contract_path, append_path))


if __name__ == "__main__":
    sys.exit(main())
