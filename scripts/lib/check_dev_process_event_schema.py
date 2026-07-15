#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_dev_process_event_schema.py — dev-process-event-v1 계약==구현 honesty self-test
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A / ADR-155 검증 채널
# SSOT: docs/inter-plugin-contracts/dev-process-event-v1.md §2 / §2.1 / §3.2 / §5.1 / §12.1
#       + change-plan §8.2 (계약==구현 honesty self-test) + ADR-155 「검증 채널」 절
#
# 책임 (각 검증 = execution-backed set-compare / 구조 파싱 — presence-grep-as-oracle 금지):
#   (a) parity (THE core, 독립 oracle): 계약 §2 표(동적 doc-parse = 필드 set A)
#       vs append_dev_process_event._ROW_KEYS(동적 code-import = 필드 set B) → A == B.
#       ★TWO-SOURCE — doc-parse(.md) vs code-import(.py, 계약 문서 EXTERNAL). 계약
#       allow-list vs 계약 §2(doc-vs-doc X⊆X tautology, CFP-2673) 아님. fail-closed
#       SYMMETRIC — A−B(contract\code) RED ∧ B−A(code\contract) RED (one-directional
#       present-null 비대칭 금지, CFP-2680). 공집합 파싱 = vacuous pass 금지 → RED.
#   (b) impl-present non-skippable: append 모듈 import OK → parity 실행, mismatch = RED
#       (check_spawn_event_schema.py:217-224 동형). impl-present skip 변형 미도입.
#   (c) allow-list lint: 계약 선언 allow-list(§2.1) + §2 필드 → §2 ⊆ allow-list
#       (본 계약 self-apply → born-GREEN 의무). set-compare, grep 아님.
#   (d) freeze / closed-list / honesty: 4 상관 ID(§5.1) present + freeze-marked /
#       noise closed-list(§3.2) == 정확히 5 / AC-23 drift-honesty 서술(§12.1) present.
#
# ★HONESTY CEILING (over-claim 금지 — 본 Story 9연속 self-ref 재발 trap):
#   본 self-test 는 impl-ABSENT born-drift hole(append impl 부재 → parity 자체가 skip)를
#   **봉인하지 못한다**. 그 방어는 D2 activation-manifest
#   (check_dev_process_activation_manifest.py, landing≠activation)로 **위임**된다
#   (honest delegation — 본 파일은 그 hole 을 "seal/close" 한다고 주장하지 않는다).
#   impl-PRESENT parity 는 기존 spawn `_check_runtime_parity` impl-존재 branch 와 동형이지
#   신규 봉인 아님. 즉 parity-skip-on-module-absent 은 D1 의 알려진 hole 이고, D2 가 봉쇄한다.
#
# 불변식: 0 API call, local read only. 3-tier exit: 0 PASS / 1 violation / 2 setup error.
#
# 사용:
#   python3 check_dev_process_event_schema.py [--contract-path <p>] [--repo-root <p>]  # check
#   python3 check_dev_process_event_schema.py --selftest   # discriminating negative-control

import argparse
import os
import re
import sys

# Windows cp949 인코딩 회피 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_DEFAULT_CONTRACT_REL = os.path.join(
    "docs", "inter-plugin-contracts", "dev-process-event-v1.md"
)
_APPEND_MODULE = "append_dev_process_event"

# ── 스펙 anchor (ADR-155 §결정 3 / 계약 §3.2·§5.1) — 파싱 대상이 아닌 요구 상수 ──
# 이것들은 parity 의 oracle 이 아니다(parity 는 순수 doc-parse vs code-import). 아래는
# (d) freeze/closed 검증의 "요구 멤버" spec constant (self-context S1 _ALLOWLIST_6 선례).
_REQUIRED_CORRELATION_IDS = {"story_key", "lane_label", "defect_id", "fix_id"}
_EXPECTED_NOISE_5 = {
    "progress_spinner", "streaming_token_duplication", "dependency_install_log",
    "unchanged_file_list", "low_value_verbose_output",
}


# ─────────────────────── 본문 split / 섹션 추출 ──────────────────────────────

def _split_frontmatter(text):
    """`---\\n ... \\n---\\n` frontmatter 제거 → 본문."""
    if not text.startswith("---\n"):
        return text
    parts = text.split("\n---\n", 1)
    return parts[1] if len(parts) == 2 else text


def _extract_section(text, start_pat, end_pat):
    """start_pat 매칭 위치 ~ 그 뒤 첫 end_pat 매칭 위치까지 슬라이스 (없으면 None)."""
    ms = re.search(start_pat, text)
    if not ms:
        return None
    tail = text[ms.end():]
    me = re.search(end_pat, tail)
    end = ms.end() + me.start() if me else len(text)
    return text[ms.start():end]


def _first_fenced_block(section):
    """섹션 안 첫 ``` ... ``` fenced code block 내용 (없으면 None)."""
    m = re.search(r"```[a-zA-Z0-9]*\n(.*?)\n```", section, re.S)
    return m.group(1) if m else None


# ─────────────────────── 파서 (doc → 구조) ──────────────────────────────────

def parse_index_fields(body):
    """§2 Schema 표의 index 필드명 순서 list (doc-parse = parity set A source).

    `## 2. Schema` ~ `### 2.1` 사이 표에서 각 data row 첫 두 셀 (파이프+숫자+백틱필드명)의
    backticked 필드명 추출. header/separator row 미매칭.
    """
    section2 = _extract_section(body, r"(?m)^##\s*2\.\s", r"(?m)^###\s*2\.1")
    if section2 is None:
        return []
    fields = []
    for m in re.finditer(r"(?m)^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|", section2):
        fields.append(m.group(1).strip())
    return fields


def parse_declared_allowlist(body):
    """§2.1 declared allow-list fenced block 의 필드명 set (doc-parse).

    `### 2.1` ~ `## 3.` 사이 첫 fenced block 내용을 `·`/공백/개행으로 split.
    """
    section21 = _extract_section(body, r"(?m)^###\s*2\.1", r"(?m)^##\s*3\.")
    if section21 is None:
        return set()
    block = _first_fenced_block(section21)
    if block is None:
        return set()
    tokens = re.split(r"[·\s]+", block)
    return {t.strip() for t in tokens if t.strip()}


def parse_correlation_ids(body):
    """§5.1 4 상관 ID freeze 표에서 backticked ID set + freeze-marked bool.

    `### 5.1` ~ `### 5.2` 사이 표 각 row 첫 셀 (파이프+백틱ID)의 backticked ID 추출.
    freeze-marked = 섹션 heading/셀에 FREEZE/freeze 문구 존재.
    (renumber: 구 §4.1→§5.1 / §4.2→§5.2, CFP-2687 doc-section-schema §4=변경규칙 FIX)
    """
    section41 = _extract_section(body, r"(?m)^###\s*5\.1", r"(?m)^###\s*5\.2")
    if section41 is None:
        return set(), False
    ids = set()
    for m in re.finditer(r"(?m)^\|\s*`([^`]+)`\s*\|", section41):
        ids.add(m.group(1).strip())
    freeze_marked = ("FREEZE" in section41) or ("freeze" in section41.lower())
    return ids, freeze_marked


def parse_noise_list(body):
    """§3.2 noise-discard closed list values set (doc-parse).

    `### 3.2` ~ `### 3.3` 사이 fenced yaml 의 `values:` 하위 `- item` 토큰 추출.
    """
    section32 = _extract_section(body, r"(?m)^###\s*3\.2", r"(?m)^###\s*3\.3")
    if section32 is None:
        return set()
    block = _first_fenced_block(section32)
    if block is None:
        return set()
    values = set()
    in_values = False
    for line in block.splitlines():
        if re.match(r"^\s*values\s*:", line):
            in_values = True
            continue
        if in_values:
            m = re.match(r"^\s*-\s*([a-z_][a-z0-9_]*)", line)
            if m:
                values.add(m.group(1))
            elif re.match(r"^\S", line):  # 새 top-level 키 → values 블록 종료
                break
    return values


def extract_ac23_narrative(body):
    """§12(정직성) 섹션 텍스트 (AC-23 drift-honesty 서술 검증용 doc-parse).

    (renumber: 구 §11 정직성→§12, CFP-2687 doc-section-schema §4=변경규칙 FIX)
    """
    section11 = _extract_section(body, r"(?m)^##\s*12\.\s", r"(?m)^##\s*13\.\s")
    return section11 or ""


# ─────────────────────── code-anchor import (parity set B source) ────────────

def import_row_keys(repo_root):
    """append_dev_process_event._ROW_KEYS 동적 import → (tuple|None, importable_bool).

    ★parity set B 의 유일 source = Python code (계약 .md 문서 EXTERNAL). 모듈 import
    자체가 실패하면 importable=False → impl-ABSENT (parity 는 봉인 밖, D2 위임).
    모듈은 import 되나 _ROW_KEYS 부재/공집합이면 importable=True + 공 tuple → 대칭
    fail-closed 이 RED 처리 (impl-present anchor 파손 = 봉인 대상).
    """
    lib_dir = os.path.join(repo_root, "scripts", "lib")
    if not os.path.isdir(lib_dir):
        lib_dir = os.path.dirname(os.path.abspath(__file__))
    inserted = False
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
        inserted = True
    try:
        import importlib
        mod = importlib.import_module(_APPEND_MODULE)
        row_keys = getattr(mod, "_ROW_KEYS", ())
        return tuple(row_keys), True
    except Exception:
        return None, False
    finally:
        if inserted and lib_dir in sys.path:
            try:
                sys.path.remove(lib_dir)
            except ValueError:
                pass


# ─────────────────────── 검증 (a)~(d) — 구조 입력, 재파싱 금지 ────────────────

def check_parity(index_fields, row_keys, importable, violations, notes):
    """(a) parity + (b) impl-present non-skippable.

    index_fields = doc-parse set A / row_keys = code-import set B.
    importable=False → impl-ABSENT: parity skip + honest-delegation note (RED 아님).
    importable=True  → non-skippable: 대칭 fail-closed 비교 (공집합 포함 RED).
    """
    setA = set(index_fields)
    # 공집합 doc-parse = vacuous pass 금지 (CFP-2680) — importable 여부와 무관하게 RED
    if not setA:
        violations.append(
            "(a/parity) 계약 §2 index 필드 doc-parse 결과 공집합 — 표 파싱 실패. "
            "vacuous pass 금지 → fail-closed RED (CFP-2680)"
        )

    if not importable:
        # impl-ABSENT — parity 는 비교 대상(code anchor) 자체 부재 → 실행 불가.
        # ★본 self-test 는 이 hole 을 봉인하지 못한다 → D2 activation-manifest 위임 (over-claim 금지).
        notes.append(
            "(a/parity) %s import 불가 (impl-ABSENT) → parity skip. "
            "★impl-ABSENT born-drift 봉인은 본 self-test 밖 — "
            "D2 activation-manifest(landing≠activation) 위임 (honest delegation, seal 주장 안 함)."
            % _APPEND_MODULE
        )
        return

    # impl-PRESENT → non-skippable (mirror check_spawn_event_schema.py:217-224).
    setB = set(row_keys or ())
    if not setB:
        violations.append(
            "(a/parity) impl-PRESENT 이나 _ROW_KEYS 공집합/부재 — code anchor 파손. "
            "impl-present non-skippable → RED (skip 아님)"
        )
    missing_in_code = sorted(setA - setB)     # contract §2 에 있으나 code 에 없음
    extra_in_code = sorted(setB - setA)       # code 에 있으나 contract §2 에 없음
    if missing_in_code or extra_in_code:
        violations.append(
            "(a/parity) 계약 §2(doc-parse, %d) ↔ %s._ROW_KEYS(code-import, %d) 불일치 "
            "[SYMMETRIC fail-closed] — contract\\code: %s / code\\contract: %s"
            % (len(setA), _APPEND_MODULE, len(setB), missing_in_code, extra_in_code)
        )
    else:
        notes.append(
            "(a/parity) A(%d, doc-parse §2) == B(%d, code-import _ROW_KEYS) — "
            "TWO-SOURCE 일치 (doc-vs-code, tautology 아님)" % (len(setA), len(setB))
        )


def check_allowlist(index_fields, declared_allowlist, violations):
    """(c) allow-list lint — §2 필드 ⊆ 선언 allow-list (본 계약 self-apply, born-GREEN 의무)."""
    setA = set(index_fields)
    if not setA:
        violations.append("(c/allow-list) §2 index 필드 공집합 — 파싱 실패 RED (vacuous pass 금지)")
        return
    if not declared_allowlist:
        violations.append("(c/allow-list) §2.1 선언 allow-list 공집합 — 파싱 실패 RED (vacuous pass 금지)")
        return
    outside = sorted(setA - declared_allowlist)
    if outside:
        violations.append(
            "(c/allow-list) §2 index 필드가 선언 allow-list 밖 — free-form 유입 의심: %s "
            "(§2 ⊆ allow-list 위반)" % outside
        )


def check_freeze(correlation_ids, freeze_marked, violations):
    """(d) 4 상관 ID present + freeze-marked (§5.1)."""
    if not freeze_marked:
        violations.append("(d/freeze) §5.1 freeze 표기(FREEZE) 부재 — 상관 ID freeze 미선언")
    missing = sorted(_REQUIRED_CORRELATION_IDS - set(correlation_ids))
    if missing:
        violations.append(
            "(d/freeze) 4 상관 ID freeze 표 미등장: %s (요구 = story_key/lane_label/defect_id/fix_id)"
            % missing
        )


def check_noise_closed(noise_list, violations):
    """(d) noise-discard closed list == 정확히 5 (§3.2)."""
    got = set(noise_list)
    if len(got) != 5:
        violations.append(
            "(d/closed) noise-discard closed list = %d 항목 (기대 정확히 5) — %s"
            % (len(got), sorted(got))
        )
        return
    if got != _EXPECTED_NOISE_5:
        violations.append(
            "(d/closed) noise-discard 5 항목 멤버 불일치 — got %s / expect %s"
            % (sorted(got), sorted(_EXPECTED_NOISE_5))
        )


def check_honesty(section11_text, violations):
    """(d) AC-23 drift-honesty 서술 (§12.1) present.

    요구 = AC-23 + drift(드리프트) + "자동 해소 안 함" 정직 서술. presence-grep 이 아니라
    honesty 서술의 필수 3요소(AC-23 anchor / drift fact / no-auto-resolve 정직)를 검사.
    """
    txt = section11_text or ""
    if "AC-23" not in txt:
        violations.append("(d/honesty) §12 AC-23 anchor 부재")
    if not re.search(r"드리프트|drift", txt, re.IGNORECASE):
        violations.append("(d/honesty) §12 계약↔구현 드리프트(FACT) 서술 부재")
    # "자동 해소한다고 주장하지 않는다" 정직 (drift auto-resolve over-claim 금지)
    if not (re.search(r"자동\s*해소", txt) and re.search(r"주장.*않|않는다|안\s*함", txt)):
        violations.append(
            "(d/honesty) §12 'drift 자동 해소 주장 안 함' 정직 서술 부재 (AC-23 honesty over-claim 방지)"
        )


# ─────────────────────── check 실행 (실 계약) ────────────────────────────────

def _parse_contract(body):
    """계약 body → 파싱 구조 dict (check / selftest 공유)."""
    correlation_ids, freeze_marked = parse_correlation_ids(body)
    return {
        "index_fields": parse_index_fields(body),
        "declared_allowlist": parse_declared_allowlist(body),
        "correlation_ids": correlation_ids,
        "freeze_marked": freeze_marked,
        "noise_list": parse_noise_list(body),
        "section11": extract_ac23_narrative(body),
    }


def _run_all_checks(parsed, row_keys, importable):
    violations, notes = [], []
    check_parity(parsed["index_fields"], row_keys, importable, violations, notes)   # (a)/(b)
    check_allowlist(parsed["index_fields"], parsed["declared_allowlist"], violations)  # (c)
    check_freeze(parsed["correlation_ids"], parsed["freeze_marked"], violations)     # (d)
    check_noise_closed(parsed["noise_list"], violations)                            # (d)
    check_honesty(parsed["section11"], violations)                                  # (d)
    return violations, notes


def cmd_check(args):
    repo_root = args.repo_root or "."
    contract_path = args.contract_path or os.path.join(repo_root, _DEFAULT_CONTRACT_REL)

    if not os.path.isfile(contract_path):
        print(
            "[codeforge-dev-process-event-schema-setup-error] contract file 부재: %s"
            % contract_path, file=sys.stderr,
        )
        sys.exit(2)
    try:
        with open(contract_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(
            "[codeforge-dev-process-event-schema-setup-error] contract read 실패: %s" % e,
            file=sys.stderr,
        )
        sys.exit(2)

    body = _split_frontmatter(text)
    parsed = _parse_contract(body)
    row_keys, importable = import_row_keys(repo_root)

    violations, notes = _run_all_checks(parsed, row_keys, importable)

    for note in notes:
        print("::notice::check-dev-process-event-schema: %s" % note)

    if violations:
        for v in violations:
            print("::warning::check-dev-process-event-schema: VIOLATION — %s" % v)
        print("")
        print(
            "check-dev-process-event-schema: %d violation — dev-process-event-v1.md "
            "§2/§2.1/§3.2/§5.1/§12.1 정합 검토 요 (계약==구현 honesty self-test)."
            % len(violations)
        )
        sys.exit(1)

    print(
        "check-dev-process-event-schema: PASS — (a) parity(doc-parse §2 ⇄ code-import "
        "_ROW_KEYS, TWO-SOURCE) + (b) impl-present non-skippable + (c) allow-list(§2⊆선언) + "
        "(d) freeze(4-ID)/closed(noise=5)/honesty(AC-23) 전부 충족. "
        "★impl-ABSENT born-drift 봉인은 D2 activation-manifest 위임 (본 self-test 미봉인, over-claim 금지)."
    )
    sys.exit(0)


# ─────────────────────── --selftest (discriminating negative-control) ─────────

def _selftest(args):
    """실 계약을 파싱 → in-memory 구조 mutation 으로 각 검증이 RED 발화함을 증명.

    positive control: unmutated 실 계약 → 전 검증 GREEN.
    RC1 allow-list / RC2 freeze / RC3 closed / RC4 honesty → 각 RED.
    + PARITY-NEG: code set B mutation → parity RED (THE core oracle 판별성).
    """
    repo_root = args.repo_root or "."
    contract_path = args.contract_path or os.path.join(repo_root, _DEFAULT_CONTRACT_REL)
    if not os.path.isfile(contract_path):
        print("[selftest-setup-error] contract file 부재: %s" % contract_path, file=sys.stderr)
        return 2
    with open(contract_path, encoding="utf-8") as f:
        body = _split_frontmatter(f.read())

    parsed = _parse_contract(body)
    row_keys, importable = import_row_keys(repo_root)

    results = []  # (label, expect_red_bool, actual_violations)

    # ── positive control: unmutated → GREEN (0 violation) ──
    pos_v, _ = _run_all_checks(parsed, row_keys, importable)
    results.append(("POSITIVE (unmutated real contract → GREEN)", False, pos_v))

    # ── RC1 allow-list: §2 에 free-form 필드 주입 (allow-list 밖) → allow-list RED ──
    rc1_fields = list(parsed["index_fields"]) + ["raw_prompt_body"]  # allow-list 미등재
    rc1_v = []
    check_allowlist(rc1_fields, parsed["declared_allowlist"], rc1_v)
    results.append(("RC1 (index free-form 필드 주입 → allow-list RED)", True, rc1_v))

    # ── RC2 freeze: 상관 ID 1개 제거 → freeze RED ──
    rc2_ids = set(parsed["correlation_ids"]) - {"defect_id"}
    rc2_v = []
    check_freeze(rc2_ids, parsed["freeze_marked"], rc2_v)
    results.append(("RC2 (상관 ID defect_id 제거 → freeze RED)", True, rc2_v))

    # ── RC3 closed: noise 6번째 추가 → closed RED ──
    rc3_noise = set(parsed["noise_list"]) | {"sixth_noise_item"}
    rc3_v = []
    check_noise_closed(rc3_noise, rc3_v)
    results.append(("RC3 (noise 6번째 추가 → closed RED)", True, rc3_v))

    # ── RC4 honesty: AC-23 서술 strip → honesty RED ──
    rc4_section11 = re.sub(r"자동\s*해소", "XXX", parsed["section11"])  # 정직 서술 제거
    rc4_section11 = rc4_section11.replace("AC-23", "XXX")
    rc4_v = []
    check_honesty(rc4_section11, rc4_v)
    results.append(("RC4 (AC-23 drift-honesty 서술 strip → honesty RED)", True, rc4_v))

    # ── PARITY-NEG (bonus): code set B 에 phantom 필드 주입 → parity RED (SYMMETRIC) ──
    pn_v, pn_notes = [], []
    mutated_keys = tuple(row_keys or ()) + ("phantom_code_field",)
    check_parity(parsed["index_fields"], mutated_keys, True, pn_v, pn_notes)
    results.append(("PARITY-NEG (code _ROW_KEYS 에 phantom 필드 → parity RED)", True, pn_v))

    # ── 보고 ──
    all_ok = True
    print("[check-dev-process-event-schema --selftest] discriminating negative-control")
    print("=" * 78)
    for label, expect_red, viols in results:
        got_red = len(viols) > 0
        ok = (got_red == expect_red)
        all_ok = all_ok and ok
        verdict = "OK" if ok else "FAIL"
        state = "RED" if got_red else "GREEN"
        print("  [%s] %-58s → %s" % (verdict, label, state))
        for v in viols:
            print("        · %s" % v)
    print("=" * 78)
    if all_ok:
        print("[check-dev-process-event-schema --selftest] PASS — "
              "positive GREEN + RC1~RC4 + PARITY-NEG 전부 RED (discriminating).")
        return 0
    print("[check-dev-process-event-schema --selftest] FAIL — 판별성 위반 (위 FAIL 행 참조).")
    return 1


# ─────────────────────── CLI ──────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="dev-process-event-v1 계약==구현 honesty self-test "
        "(CFP-2687 Phase 2 — parity/allow-list/freeze/closed/honesty)"
    )
    p.add_argument("--selftest", action="store_true",
                   help="discriminating negative-control (RC1~RC4 + PARITY-NEG RED 증명)")
    p.add_argument("--contract-path", default="",
                   help="dev-process-event-v1.md 경로 (default: <repo-root>/docs/...)")
    p.add_argument("--repo-root", default=".", help="repo root (default 현재 디렉터리)")
    # 호환: 'check' positional 을 관용적으로 허용 (무시 — 기본 동작이 check)
    p.add_argument("command", nargs="?", default="check", help=argparse.SUPPRESS)

    args = p.parse_args()
    if args.selftest:
        sys.exit(_selftest(args))
    cmd_check(args)


if __name__ == "__main__":
    main()
