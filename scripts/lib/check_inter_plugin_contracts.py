#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-33 (ζ arc F2) — Inter-plugin contract validator
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# 검사: docs/inter-plugin-contracts/** 에서 kind: contract 파일의 frontmatter + 본문 sanity
# Usage / exit code / semantics 상세: scripts/check-inter-plugin-contracts.sh header.
import sys, re
from pathlib import Path
import sys

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:
    print("⚠ check-inter-plugin-contracts: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

CONTRACT_REQUIRED_FIELDS = {
    "kind",
    "contract_version",
    "status",
    "related_plugins",
    "related_adrs",
    "authors",
}

contracts_dir = Path("docs/inter-plugin-contracts")
if not contracts_dir.exists():
    print("✓ CFP-33 inter-plugin-contracts: 디렉토리 부재 — skip")
    sys.exit(0)

# CFP-42: Manifest completeness — every MANIFEST.yaml entry must exist as a file
manifest_path = contracts_dir / "MANIFEST.yaml"
manifest_files = set()  # set of basenames declared in MANIFEST
if manifest_path.exists():
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"::error::CFP-42 MANIFEST.yaml parse 실패: {e}")
        sys.exit(1)
    for entry in (manifest or {}).get("contracts", []):
        for fent in entry.get("files", []):
            fname = fent.get("file")
            if fname:
                manifest_files.add(fname)
                if not (contracts_dir / fname).exists():
                    print(f"::error::CFP-42 manifest entry {entry.get('name')} v{fent.get('contract_version')} missing sibling file {fname}")
                    sys.exit(1)

errors = []
contracts_seen = 0

for md in sorted(contracts_dir.rglob("*.md")):
    if md.name.lower() in {"readme.md", "index.md"}:
        continue

    text = md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        continue

    try:
        fm_text = text.split("\n---\n", 1)[0][4:]
        fm = yaml.safe_load(fm_text)
    except Exception as e:
        errors.append(f"{md}: frontmatter parse 실패 ({type(e).__name__}: {e})")
        continue

    if not isinstance(fm, dict) or fm.get("kind") != "contract":
        continue

    # CFP-42: orphan check — kind:contract must be registered in MANIFEST
    if md.name not in manifest_files:
        errors.append(f"{md}: orphan kind:contract file (not registered in MANIFEST.yaml)")

    contracts_seen += 1

    # 1. 필수 frontmatter 필드
    missing = CONTRACT_REQUIRED_FIELDS - set(fm.keys())
    if missing:
        errors.append(f"{md}: contract 필수 필드 누락 — {sorted(missing)}")

    # 2. contract_version 형식 (semver-like: "X.Y" 또는 "X.Y.Z")
    cv = fm.get("contract_version", "")
    if cv and not re.match(r'^\d+\.\d+(\.\d+)?$', str(cv)):
        errors.append(f'{md}: contract_version 형식 위반 (X.Y 또는 X.Y.Z 필요) — "{cv}"')

    # 3. status enum
    status_val = fm.get("status", "")
    if status_val and status_val not in {"Draft", "Active", "Deprecated", "Archived"}:
        errors.append(f'{md}: status 값 위반 (Draft|Active|Deprecated|Archived) — "{status_val}"')

    # 4. related_plugins, related_adrs, authors 는 list
    for list_field in ("related_plugins", "related_adrs", "authors"):
        val = fm.get(list_field)
        if val is not None and not isinstance(val, list):
            errors.append(f'{md}: {list_field} 는 list 여야 함 — got {type(val).__name__}')
        elif isinstance(val, list) and len(val) == 0:
            errors.append(f"{md}: {list_field} 빈 list 금지")

    # CFP-42: sibling must reference ADR-008 + ADR-010
    related_adrs_str = " ".join(str(x) for x in (fm.get("related_adrs") or []))
    if "ADR-008" not in related_adrs_str:
        errors.append(f"{md}: related_adrs must reference ADR-008 (versioning rule)")
    if "ADR-010" not in related_adrs_str:
        errors.append(f"{md}: related_adrs must reference ADR-010 (sibling sync policy)")

    # 5. 본문 구조화 sanity — 최소 3개 ## 섹션
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    section_count = len(re.findall(r"^## ", body, re.MULTILINE))
    if section_count < 3:
        errors.append(f"{md}: 본문 ## 섹션 부족 ({section_count} < 3) — 구조화 강제")

    # CFP-42: sibling marker section
    if not re.search(r"\*\*상위 SSOT 위치\*\*:", body):
        errors.append(f"{md}: sibling marker section missing (need '**상위 SSOT 위치**:' in body)")

if errors:
    print(f"::error::CFP-33 inter-plugin-contracts (STRICT): {len(errors)} 건")
    for e in errors:
        print(f"  - {e}")
    print("strict 모드 — kind: contract schema 위반 시 PR 차단.")
    sys.exit(1)

print(f"✓ CFP-33 inter-plugin-contracts: {contracts_seen} contract(s) schema 충족")
