#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_return_envelope_schema.py — return-envelope-v1 contract 문서 well-formed lint
#
# Carrier: CFP-2572 Phase 2 (구현) / ADR-142 §결정 3.
#
# Tier: [measurement].
#   문서 well-formed 검증 (schema file-lint) — runtime 반환 준수 강제 아님
#   (fix-event-v1 이 문서 schema 인 것과 동형). block/deny/강제 언어 0.
#   lint GREEN = "문서가 계약 형식을 갖췄다" 이지 "런타임 반환이 cap 을 지켰다" 가 아니다
#   (hollow-gate 위장 금지 — ADR-119 검증-후-단언, return-envelope-v1.md §6 정합).
#
# 책임 (3 check — 전부 hold 해야 PASS, 아니면 exit != 0):
#   (M1) envelope.meta cap field 존재 (§2 섹션 안 size_bytes / cap_bytes / over_cap).
#   (M2) raw-exclusion clause 존재 (raw 배제/미포함 절).
#   (M3) MANIFEST.yaml contracts: 아래 return_envelope / return-envelope-v1.md 등록.
#
# RED 진정성 (test-check-return-envelope-schema.sh discriminating):
#   RB1 = fixture 에서 cap 절 제거 → (M1) RED.
#   RB2 = fixture 에서 raw-exclusion 절 제거 → (M2) RED.
#   RB3 = MANIFEST fixture 에서 return_envelope entry 제거 → (M3) RED.
#
# 불변식: 0 API call, local read only. 3-tier exit: 0 PASS / 1 violation / 2 setup error.
#
# 사용:
#   python3 check_return_envelope_schema.py check \
#     [--ldoc-path <path>] [--manifest-path <path>] [--repo-root <path>]

import argparse
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


_DEFAULT_LDOC_REL = os.path.join(
    "docs", "inter-plugin-contracts", "return-envelope-v1.md"
)
_DEFAULT_MANIFEST_REL = os.path.join(
    "docs", "inter-plugin-contracts", "MANIFEST.yaml"
)

_CAP_FIELDS = ["size_bytes", "cap_bytes", "over_cap"]


def _extract_section(text, start_pat, end_pat):
    ms = re.search(start_pat, text)
    if not ms:
        return None
    tail = text[ms.end():]
    me = re.search(end_pat, tail)
    end = ms.end() + me.start() if me else len(text)
    return text[ms.start():end]


# ─────────────────────── (M1) envelope.meta cap field ────────────────────────

def _check_cap_fields(ldoc_text, violations):
    """(M1) §2 envelope 구조 섹션 안 cap field(size_bytes/cap_bytes/over_cap) 존재.

    §2 (## 2 ~ ## 3) 로 scope — §3 표의 inline 백틱 언급과 무관하게 envelope.meta 정의 검증.
    """
    section2 = _extract_section(ldoc_text, r"(?m)^## 2\.", r"(?m)^## 3\.")
    if section2 is None:
        violations.append("(M1) return-envelope-v1.md §2 envelope 구조 섹션 부재")
        return
    missing = [f for f in _CAP_FIELDS if f not in section2]
    if missing:
        violations.append(
            "(M1) envelope.meta cap field 부재: %s (§2 size cap 회계 절 누락)"
            % ", ".join(missing)
        )


# ─────────────────────── (M2) raw-exclusion clause ───────────────────────────

def _check_raw_exclusion(ldoc_text, violations):
    """(M2) raw-exclusion clause (raw diff/원문 미포함 — evidence_ref 포인터만) 존재.

    §3 (## 3 ~ ## 4) DRY single-owner 섹션으로 scope — §6 의 lint-scoping meta 언급
    ("raw-exclusion clause 존재") 과 무관하게 실 불변식 절 존재만 검증 (hollow-gate 회피).
    """
    section3 = _extract_section(ldoc_text, r"(?m)^## 3\.", r"(?m)^## 4\.")
    if section3 is None:
        violations.append("(M2) return-envelope-v1.md §3 envelope 소유 불변식 섹션 부재")
        return
    if not re.search(r"raw[- ]?exclusion|raw[^\n]{0,15}미포함", section3):
        violations.append(
            "(M2) raw-exclusion clause 부재 — raw diff/원문 미포함 절(§3 DRY single owner) 누락"
        )


# ─────────────────────── (M3) MANIFEST 등록 ──────────────────────────────────

def _check_manifest_registration(manifest_text, violations):
    """(M3) MANIFEST.yaml contracts: 아래 return_envelope / return-envelope-v1.md 등록.

    yaml parse primary (contracts 리스트 안 name==return_envelope + files 안 파일명) +
    parse 실패 시 text 검색 fallback.
    """
    registered = False
    if yaml is not None:
        try:
            data = yaml.safe_load(manifest_text)
            if isinstance(data, dict):
                for entry in (data.get("contracts") or []):
                    if not isinstance(entry, dict):
                        continue
                    if entry.get("name") == "return_envelope":
                        files = entry.get("files") or []
                        for fr in files:
                            fname = fr.get("file") if isinstance(fr, dict) else str(fr)
                            if fname and "return-envelope-v1.md" in fname:
                                registered = True
                                break
                    if registered:
                        break
        except yaml.YAMLError:
            registered = None  # parse 실패 → text fallback
    if registered is None or (yaml is None):
        registered = ("name: return_envelope" in manifest_text
                      and "return-envelope-v1.md" in manifest_text)

    if not registered:
        violations.append(
            "(M3) MANIFEST.yaml contracts: 아래 return_envelope / return-envelope-v1.md 등록 부재"
        )


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def _read_file(path, label):
    if not os.path.isfile(path):
        print(
            "[codeforge-return-envelope-lint-setup-error] check-return-envelope-schema: "
            "%s file 부재: %s" % (label, path),
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print(
            "[codeforge-return-envelope-lint-setup-error] check-return-envelope-schema: "
            "%s read 실패: %s" % (label, e),
            file=sys.stderr,
        )
        sys.exit(2)


def cmd_check(args):
    repo_root = args.repo_root or "."
    ldoc_path = args.ldoc_path or os.path.join(repo_root, _DEFAULT_LDOC_REL)
    manifest_path = args.manifest_path or os.path.join(repo_root, _DEFAULT_MANIFEST_REL)

    ldoc_text = _read_file(ldoc_path, "return-envelope-v1.md")
    manifest_text = _read_file(manifest_path, "MANIFEST.yaml")

    violations = []
    _check_cap_fields(ldoc_text, violations)                 # (M1)
    _check_raw_exclusion(ldoc_text, violations)              # (M2)
    _check_manifest_registration(manifest_text, violations)  # (M3)

    if violations:
        for v in violations:
            print("::warning::check-return-envelope-schema: VIOLATION — %s" % v)
        print("")
        print(
            "check-return-envelope-schema: %d violation "
            "([measurement] 문서 well-formed — runtime 반환 준수 강제 아님)." % len(violations)
        )
        sys.exit(1)

    print(
        "check-return-envelope-schema: PASS — [measurement] 문서 well-formed "
        "((M1) envelope.meta cap field / (M2) raw-exclusion clause / (M3) MANIFEST 등록). "
        "runtime 반환 준수 강제 아님 (fix-event-v1 이 문서 schema 인 것과 동형)."
    )
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="return-envelope-v1 문서 well-formed lint "
        "(CFP-2572 Phase 2 — [measurement], runtime 강제 아님)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="문서 well-formed 검증 (schema file-lint)")
    check_p.add_argument("--ldoc-path", default="",
                         help="return-envelope-v1.md 경로 (default: <repo-root>/docs/...)")
    check_p.add_argument("--manifest-path", default="",
                         help="MANIFEST.yaml 경로 (default: <repo-root>/docs/.../MANIFEST.yaml)")
    check_p.add_argument("--repo-root", default=".", help="repo root (default 현재 디렉터리)")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
