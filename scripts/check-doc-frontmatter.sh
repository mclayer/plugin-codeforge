#!/usr/bin/env bash
# CFP-27 Phase 0b
# 검사: 4 owner doc path 의 frontmatter 필수 필드 (warning 모드 — exit=0 with warnings)
#
# Path / 필수 frontmatter 필드 source:
#   - docs/change-plans/**     templates/change-plan.md frontmatter (title, slug, status, author, created, story)
#   - docs/adr/**              templates/adr.md          (adr_number, title, status, category, date)
#   - docs/domain-knowledge/** templates/domain-knowledge.md (title, area, topic_slug, status, updated)
#   - docs/retros/**           templates/retro.md         (title, date, sprint_period, cfp_keys, authors)
#
# CFP-28 dogfooding에서 strict 모드로 전환 (exit=1).
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY' || true
import sys, re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠ check-doc-frontmatter: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

REQUIRED = {
    "docs/change-plans": {"title", "slug", "status", "author", "created", "story"},
    "docs/adr":          {"adr_number", "title", "status", "category", "date"},
    "docs/domain-knowledge": {"title", "area", "topic_slug", "status", "updated"},
    "docs/retros":       {"title", "date", "sprint_period", "cfp_keys", "authors"},
}

warns = []
for prefix, fields in REQUIRED.items():
    path = Path(prefix)
    if not path.exists():
        continue
    for md in sorted(path.rglob("*.md")):
        # README 또는 index 파일은 schema 대상 아님
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            warns.append(f"{md}: frontmatter 부재")
            continue
        try:
            fm_text = text.split("\n---\n", 1)[0][4:]
            fm = yaml.safe_load(fm_text)
        except Exception as e:
            warns.append(f"{md}: frontmatter parse 실패 ({type(e).__name__})")
            continue
        if not isinstance(fm, dict):
            warns.append(f"{md}: frontmatter는 mapping이어야 함")
            continue
        missing = fields - fm.keys()
        if missing:
            warns.append(f"{md}: 필수 필드 누락 — {sorted(missing)}")

if warns:
    print(f"⚠ CFP-27 doc-frontmatter (WARN): {len(warns)} 건")
    for w in warns:
        print(f"  - {w}")
    print("⚠ warning 모드 — CFP-28 strict 전환 시점에 모두 fix 또는 allowlist 필요")
else:
    print("✓ CFP-27 doc-frontmatter: 4 owner path 전부 schema 충족")
PY

# 항상 exit 0 (warning 모드)
echo ""
echo "(check-doc-frontmatter: warning 모드 — exit 0 강제. CFP-28에서 strict 전환)"
exit 0
