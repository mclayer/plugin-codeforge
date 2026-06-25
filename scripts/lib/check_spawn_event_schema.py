#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_spawn_event_schema.py — spawn-event-v1 contract lint
#
# Carrier: CFP-2393 Phase 2 (구현) / Epic CFP-2391 S3
# 출처: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
#       — spawn-event row 모델이 OMC per-agent registry 차용. 본 lint 는 codeforge 측
#       contract invariant 검증으로 OMC 직접 차용 아님 (contract↔runtime guard).
#
# 책임 (Change Plan §5 / §8.2 — 8 검증 항목):
#   (a) kind:registry frontmatter (kind: registry + registry: spawn-event present).
#   (b) §1/§2/§3/§4 headings present.
#   (c) Allow-list ONLY — §2 field 표 19 row, free-form string field 0 (enum/numeric/hash only).
#   (d) attribution_confidence invariant — enum {attributed, unattributed, unsupported}
#       + default unattributed + literal "unattributed" 존재.
#   (e) agent_type semi-open membership — enum reject 검증 아님; unknown-agent fallback 존재
#       + roster-derived 규칙 명시 검증 (F4 정정 — strict closed-set reject 금지).
#   (f) event_type closed enum — {agent_start, agent_stop, tool, file_touch, mode_change} 명시.
#   (g) idempotency — event_id deterministic 규칙 (sha256, random UUID 금지) 명시 present.
#   (h) opt-in default false — literal 또는 동등 present.
#   + contract↔runtime PARITY (선택) — append_spawn_event.py row key ↔ contract 19 set 일치.
#
# 불변식:
#   - 0 API call, local read only.
#   - 3-tier exit (ADR-060 §결정 15): 0 PASS / 1 violation (warning) / 2 setup error.
#
# 사용:
#   python3 check_spawn_event_schema.py check [--contract-path <path>] [--repo-root <path>]
#
# Prior art: check_deferred_followup_reconcile.py / check_doc_section_schema.py /
#            check_doc_frontmatter.py (frontmatter yaml.safe_load 패턴)

import argparse
import os
import re
import sys

# Windows cp949 인코딩 회피 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


_DEFAULT_CONTRACT_REL = os.path.join(
    "docs", "inter-plugin-contracts", "spawn-event-v1.md"
)

# contract §2 Allow-list 19 field (정확 키 — SSOT)
_CONTRACT_19_FIELDS = [
    "event_id", "schema_version", "timestamp", "story_key", "lane_label",
    "agent_type", "attribution_confidence", "input_tokens", "output_tokens",
    "cache_creation_input_tokens", "cache_read_input_tokens", "cost_usd",
    "duration_ms", "tool_call_count", "actor", "parent_event_id",
    "consumer_scope", "event_type", "elapsed_seconds",
]

_EVENT_TYPE_VALUES = ["agent_start", "agent_stop", "tool", "file_touch", "mode_change"]
_ATTRIBUTION_VALUES = ["attributed", "unattributed", "unsupported"]


# ─────────────────────── frontmatter / 본문 split ────────────────────────────

def _split_frontmatter(text):
    """`---\\n ... \\n---\\n` frontmatter 와 본문 분리.

    Returns (frontmatter_dict | None, body_str).
    """
    if not text.startswith("---\n"):
        return None, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None, text
    fm_text = parts[0][4:]  # leading '---\n' 제거
    body = parts[1]
    if yaml is None:
        return None, body
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, body
    return (fm if isinstance(fm, dict) else None), body


# ─────────────────────── 검증 항목 (a)~(h) + parity ──────────────────────────

def _check_frontmatter_kind(fm, violations):
    """(a) kind:registry frontmatter — kind: registry + registry: spawn-event."""
    if fm is None:
        violations.append("(a) frontmatter 부재 또는 parse 실패")
        return
    if fm.get("kind") != "registry":
        violations.append("(a) frontmatter kind != registry (got: %r)" % fm.get("kind"))
    if fm.get("registry") != "spawn-event":
        violations.append(
            "(a) frontmatter registry != spawn-event (got: %r)" % fm.get("registry")
        )


def _check_headings(body, violations):
    """(b) §1/§2/§3/§4 headings present."""
    # `## 1. 목적` / `## 2. Schema` / `## 3. 항목` / `## 4. 변경 규칙` 형태 (§ optional)
    for n in (1, 2, 3, 4):
        pat = re.compile(r"(?m)^#{1,4}\s*(§)?%d[\.\s]" % n)
        if not pat.search(body):
            violations.append("(b) §%d heading 부재" % n)


def _check_allowlist_19(body, violations):
    """(c) Allow-list ONLY — §2 field 표 19 row 전부 present + free-form string field 0.

    19 field 가 §2 표에 `| \\`field\\` |` 형태로 전부 등장하는지 + free-form string
    타입 선언 부재 검증. 'free-form string field' 명시 부재 = 구조적 차단 (T-INFO-8).
    """
    missing = []
    for field in _CONTRACT_19_FIELDS:
        # `| \`event_id\` |` 형태 (백틱 wrapped, 표 cell)
        pat = re.compile(r"\|\s*`%s`\s*\|" % re.escape(field))
        if not pat.search(body):
            missing.append(field)
    if missing:
        violations.append(
            "(c) §2 Allow-list 19 field 중 표 미등장: %s" % ", ".join(missing)
        )

    # free-form string field 0 검증 — 명시적 "free-form string field 0/부재" 선언 present
    if not re.search(r"free-form string field\s*(0개|0건|부재|0)", body):
        violations.append(
            "(c) 'free-form string field 0/부재' 명시 부재 (T-INFO-8 구조적 차단 선언)"
        )


def _check_attribution_invariant(body, violations):
    """(d) attribution_confidence invariant — enum 3값 + default unattributed + literal."""
    for v in _ATTRIBUTION_VALUES:
        if v not in body:
            violations.append("(d) attribution_confidence enum 값 '%s' 미명시" % v)
    # default unattributed 명시
    if not re.search(r"default\s*[=:]?\s*`?unattributed`?", body):
        violations.append("(d) attribution_confidence default unattributed 미명시")
    # literal "unattributed" 존재 (위 enum loop 가 이미 cover 하지만 명시 검증)
    if "unattributed" not in body:
        violations.append("(d) literal 'unattributed' 부재")


def _check_agent_type_semi_open(body, violations):
    """(e) agent_type semi-open — unknown-agent fallback + roster-derived 규칙 명시.

    strict closed-set reject 검증 금지 (F4 정정) — fallback 존재 + roster 규칙만 검증.
    """
    if "unknown-agent" not in body:
        violations.append("(e) agent_type 'unknown-agent' fallback 명시 부재")
    if not re.search(r"roster[- ]?derived|roster-derived|roster", body):
        violations.append("(e) agent_type roster-derived 규칙 명시 부재")
    # semi-open 명시 (strict closed-set 아님 확인)
    if "semi-open" not in body:
        violations.append("(e) agent_type semi-open 선언 부재")


def _check_event_type_enum(body, violations):
    """(f) event_type closed enum — 5값 전부 명시."""
    for v in _EVENT_TYPE_VALUES:
        if v not in body:
            violations.append("(f) event_type enum 값 '%s' 미명시" % v)


def _check_idempotency(body, violations):
    """(g) idempotency — event_id deterministic (sha256, random UUID 금지) 명시."""
    if not re.search(r"deterministic", body):
        violations.append("(g) event_id deterministic 규칙 명시 부재")
    if "sha256" not in body:
        violations.append("(g) event_id sha256 규칙 명시 부재")
    if not re.search(r"random UUID\s*금지|UUID\s*금지", body):
        violations.append("(g) 'random UUID 금지' 명시 부재")


def _check_opt_in_default_false(body, violations):
    """(h) opt-in default false — literal 또는 동등 present."""
    # "opt-in default false" 또는 "opt_in_default_false" 또는 "opt-in" + "default false" 조합
    has_optin = bool(re.search(r"opt[-_ ]?in", body, re.IGNORECASE))
    has_default_false = bool(re.search(r"default\s*false|default false|default_false", body, re.IGNORECASE))
    if not (has_optin and has_default_false):
        violations.append("(h) 'opt-in default false' (또는 동등) 명시 부재")


def _check_runtime_parity(repo_root, violations, notes):
    """contract↔runtime PARITY (선택) — append_spawn_event.py _ROW_KEYS ↔ contract 19 set.

    import 가능 시 빈 row key 추출해 19 set 비교 (Phase 2 contract=runtime 일치 가정).
    import 어려우면 skip (notes 기록 — Phase 1 theater 회피, runtime parity 는 별 검증).
    """
    lib_dir = os.path.join(repo_root, "scripts", "lib")
    append_module_path = os.path.join(lib_dir, "append_spawn_event.py")
    if not os.path.isfile(append_module_path):
        notes.append("parity: append_spawn_event.py 부재 — runtime parity skip")
        return
    try:
        sys.path.insert(0, lib_dir)
        import append_spawn_event as _ase  # noqa: import-after-path
        runtime_keys = set(getattr(_ase, "_ROW_KEYS", ()))
    except Exception as e:  # pragma: no cover
        notes.append("parity: append_spawn_event import 실패 (%s) — runtime parity skip" % e)
        return
    finally:
        if lib_dir in sys.path:
            try:
                sys.path.remove(lib_dir)
            except ValueError:
                pass

    contract_keys = set(_CONTRACT_19_FIELDS)
    if runtime_keys != contract_keys:
        missing_in_runtime = sorted(contract_keys - runtime_keys)
        extra_in_runtime = sorted(runtime_keys - contract_keys)
        violations.append(
            "(parity) append_spawn_event _ROW_KEYS ↔ contract 19 set 불일치 — "
            "runtime missing: %s / runtime extra: %s"
            % (missing_in_runtime, extra_in_runtime)
        )
    else:
        notes.append("parity: append_spawn_event _ROW_KEYS == contract 19 set (일치)")


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    contract_path = args.contract_path or os.path.join(repo_root, _DEFAULT_CONTRACT_REL)

    if not os.path.isfile(contract_path):
        print(
            "[codeforge-spawn-event-lint-setup-error] check-spawn-event-schema: "
            "contract file 부재: %s" % contract_path,
            file=sys.stderr,
        )
        sys.exit(2)

    if yaml is None:
        print(
            "[codeforge-spawn-event-lint-setup-error] check-spawn-event-schema: "
            "pyyaml 미설치 — frontmatter 검증 불가",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        with open(contract_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(
            "[codeforge-spawn-event-lint-setup-error] check-spawn-event-schema: "
            "contract read 실패: %s" % e,
            file=sys.stderr,
        )
        sys.exit(2)

    fm, body = _split_frontmatter(text)

    violations = []
    notes = []

    _check_frontmatter_kind(fm, violations)        # (a)
    _check_headings(body, violations)              # (b)
    _check_allowlist_19(body, violations)          # (c)
    _check_attribution_invariant(body, violations) # (d)
    _check_agent_type_semi_open(body, violations)  # (e)
    _check_event_type_enum(body, violations)       # (f)
    _check_idempotency(body, violations)           # (g)
    _check_opt_in_default_false(body, violations)  # (h)
    _check_runtime_parity(repo_root, violations, notes)  # parity (선택)

    for note in notes:
        print("::notice::check-spawn-event-schema: %s" % note)

    if violations:
        for v in violations:
            print("::warning::check-spawn-event-schema: VIOLATION — %s" % v)
        print("")
        print(
            "check-spawn-event-schema: %d violation (warning tier — 비차단, advisory). "
            "spawn-event-v1.md contract §2/§3 정합 검토 요." % len(violations)
        )
        sys.exit(1)

    print(
        "check-spawn-event-schema: PASS — (a)~(h) + parity 전부 충족 "
        "(19 field Allow-list / attribution invariant / semi-open agent_type / "
        "idempotency / opt-in default false)"
    )
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="spawn-event-v1 contract lint (CFP-2393 Phase 2 — kind:registry + Allow-list)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="contract schema 검증")
    check_p.add_argument("--contract-path", default="",
                         help="spawn-event-v1.md 경로 (default: <repo-root>/docs/inter-plugin-contracts/...)")
    check_p.add_argument("--repo-root", default=".",
                         help="repo root (default 현재 디렉터리)")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
