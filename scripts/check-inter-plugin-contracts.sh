#!/usr/bin/env bash
# CFP-33 (ζ arc F2) — Inter-plugin contract validator
#
# 검사: docs/inter-plugin-contracts/** 에서 kind: contract 파일의 frontmatter + 본문 sanity
#
# kind: registry 파일은 check-doc-frontmatter.sh + check-doc-section-schema.sh 가 처리.
# 본 lint 는 kind: contract 파일 전담.
#
# Required frontmatter (kind: contract):
#   - kind, contract_version, status, related_plugins, related_adrs, authors
#
# Required body sanity:
#   - 최소 ## 1. 또는 ## 2. 형태의 섹션 3개 이상 (구조화 강제)
#   - changelog 또는 v 변경 이력 안내 섹션 권장 (warning, not error — soft check)
#
# Strict 모드: warning 발견 시 exit 1 → CI 차단.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import sys, re
from pathlib import Path

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
        # frontmatter 없으면 contract 가 아님 — skip (registry 또는 narrative 문서일 수 있음)
        continue

    try:
        fm_text = text.split("\n---\n", 1)[0][4:]
        fm = yaml.safe_load(fm_text)
    except Exception as e:
        errors.append(f"{md}: frontmatter parse 실패 ({type(e).__name__}: {e})")
        continue

    if not isinstance(fm, dict) or fm.get("kind") != "contract":
        # contract 가 아니면 skip (registry 등)
        continue

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

    # 5. 본문 구조화 sanity — 최소 3개 ## 섹션
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    section_count = len(re.findall(r"^## ", body, re.MULTILINE))
    if section_count < 3:
        errors.append(f"{md}: 본문 ## 섹션 부족 ({section_count} < 3) — 구조화 강제")

if errors:
    print(f"::error::CFP-33 inter-plugin-contracts (STRICT): {len(errors)} 건")
    for e in errors:
        print(f"  - {e}")
    print("strict 모드 — kind: contract schema 위반 시 PR 차단.")
    sys.exit(1)

print(f"✓ CFP-33 inter-plugin-contracts: {contracts_seen} contract(s) schema 충족")
PY

echo ""
echo "(check-inter-plugin-contracts: strict 모드 — kind: contract 파일 frontmatter + 본문 sanity)"
