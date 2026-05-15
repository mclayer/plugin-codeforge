#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-407 / ADR-062 — carrier Story bootstrap dependency mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Usage / exit code / semantics 상세: scripts/check-carrier-bootstrap.sh header.
import sys, re, os
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("⚠ check-carrier-bootstrap: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

# Type prefix v1.0 (ADR-062 §결정 1 verbatim — 5 prefix only)
VALID_TYPE_PREFIXES = {"adr", "contract", "policy", "workflow", "script"}

# Story KEY 형식: <PREFIX>-<NUMBER>
KEY_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")

# typed key 형식: <type>:<identifier>
TYPED_KEY_RE = re.compile(r"^([a-z]+):(.+)$")

violations = []
files_checked = 0

paths = sys.argv[1:]
if not paths:
    paths = sorted(str(p) for p in Path("docs/stories").glob("*-*.md"))

for p in paths:
    path = Path(p)
    if not path.exists():
        violations.append(f"{p}: file 부재")
        continue
    text = path.read_text(encoding="utf-8")
    files_checked += 1

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        continue
    try:
        fm = yaml.safe_load(fm_match.group(1)) or {}
    except yaml.YAMLError as e:
        violations.append(f"{p}: frontmatter YAML 파싱 실패 ({e})")
        continue

    body = text[fm_match.end():]

    carrier_story = fm.get("carrier_story")
    exempt_protocols = fm.get("bootstrap_exempt_protocols")
    own_key = fm.get("key")

    if carrier_story is None and exempt_protocols is None:
        continue

    if carrier_story is not None and exempt_protocols is None:
        violations.append(
            f"{p}: `carrier_story` 선언 시 `bootstrap_exempt_protocols` 필드 의무 "
            f"(ADR-062 §결정 1 — typed key list)"
        )
        continue

    if carrier_story is None and exempt_protocols is not None:
        violations.append(
            f"{p}: `bootstrap_exempt_protocols` 선언 시 `carrier_story` 필드 의무 "
            f"(ADR-062 §결정 1)"
        )
        continue

    if not isinstance(carrier_story, str):
        violations.append(
            f"{p}: `carrier_story` 가 string 아님 ({carrier_story!r}) — ADR-062 §결정 1"
        )
        continue
    if not KEY_RE.match(carrier_story):
        violations.append(
            f"{p}: `carrier_story` KEY 형식 위배 ({carrier_story!r}) — `<PREFIX>-<NUMBER>` 의무 (ADR-062 §결정 1)"
        )

    if not isinstance(exempt_protocols, list):
        violations.append(
            f"{p}: `bootstrap_exempt_protocols` 가 list 아님 ({type(exempt_protocols).__name__}) — ADR-062 §결정 1"
        )
        continue
    if not exempt_protocols:
        violations.append(
            f"{p}: `bootstrap_exempt_protocols` empty list — carrier 선언했으나 면제 protocol 부재 (ADR-062 §결정 1)"
        )
        continue

    typed_keys = []
    for idx, elem in enumerate(exempt_protocols):
        if not isinstance(elem, str):
            violations.append(
                f"{p}: `bootstrap_exempt_protocols[{idx}]` 가 string 아님 ({elem!r}) — ADR-062 §결정 1"
            )
            continue
        m = TYPED_KEY_RE.match(elem)
        if not m:
            violations.append(
                f"{p}: `bootstrap_exempt_protocols[{idx}]` typed key 형식 위배 ({elem!r}) — "
                f"`<type>:<identifier>` 의무 (ADR-062 §결정 1)"
            )
            continue
        type_prefix, identifier = m.group(1), m.group(2)
        if type_prefix not in VALID_TYPE_PREFIXES:
            violations.append(
                f"{p}: `bootstrap_exempt_protocols[{idx}]` 미정의 type prefix '{type_prefix}' "
                f"({elem!r}) — 표준 5 prefix {sorted(VALID_TYPE_PREFIXES)} (ADR-062 §결정 1)"
            )
            continue
        typed_keys.append((type_prefix, identifier))

    if own_key and carrier_story == own_key:
        section3_match = re.search(
            r"^##\s+§3\..*?$(.*?)(?=^##\s+§4|^##\s+§|\Z)",
            body, re.MULTILINE | re.DOTALL
        )
        section3_body = section3_match.group(1) if section3_match else ""

        for type_prefix, identifier in typed_keys:
            if type_prefix in ("adr", "contract"):
                if identifier not in section3_body:
                    violations.append(
                        f"{p}: §3 본문에 `{type_prefix}:{identifier}` 참조 부재 "
                        f"(ADR-062 §결정 2 (b) — carrier protocol 이 §3 ADR 목록에 명시 의무)"
                    )

print(f"check-carrier-bootstrap: {files_checked} Story files 검증")
if violations:
    print(f"\n⚠ violation {len(violations)}건:", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
    sys.exit(1)
else:
    print("✓ violation 0건 — carrier bootstrap mechanical check PASS")
    sys.exit(0)
