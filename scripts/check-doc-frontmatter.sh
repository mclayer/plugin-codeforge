#!/usr/bin/env bash
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# ADR-056 — docs/domain-knowledge/domain + concept 경로 분기, kind 필드 검증 추가 (CFP-376)
# CFP-391 — registry kind 필수 필드에 canonical_repo / canonical_path / date 추가 (debate-protocol-v1)
# 검사: 5 owner doc path 의 frontmatter 필수 필드
#
# Path / 필수 frontmatter 필드 source:
#   - docs/change-plans/**            templates/change-plan.md frontmatter (title, slug, status, author, created, story)
#   - docs/adr/**                     templates/adr.md          (adr_number, title, status, category, date)
#   - docs/domain-knowledge/domain/** templates/domain-knowledge.md (kind, title, area, topic_slug, status, updated)
#   - docs/domain-knowledge/concept/**templates/concept.md (kind, title, slug, status, updated)
#   - docs/retros/**                  templates/retro.md         (title, date, sprint_period, cfp_keys, authors)
#   - docs/inter-plugin-contracts/**  registry kind: {kind, registry, version, status, authors,
#                                                    canonical_repo, canonical_path, date}  # CFP-391 보강
#                                     ※ kind: contract 파일은 본 lint 적용 안 함 — CFP-33
#                                       check-inter-plugin-contracts.sh 가 별도 검증
#
# Strict 모드: warning 발견 시 exit 1 → CI에서 PR 차단. 신규 작성은 templates/<doc-type>.md schema 준수 필수.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
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
    "docs/domain-knowledge/domain": {"kind", "title", "area", "topic_slug", "status", "updated"},
    "docs/domain-knowledge/concept": {"kind", "title", "slug", "status", "updated"},
    "docs/retros":       {"title", "date", "sprint_period", "cfp_keys", "authors"},
    # CFP-391 — registry kind 에 canonical_repo + canonical_path + date 추가 (debate-protocol-v1 도입)
    # rationale: kind:registry 는 wrapper-owned canonical (sibling mirror 없음). canonical_repo / canonical_path 가
    # registry SSOT 위치를 자기 frontmatter 안에서 명시. date 는 amendment_log 부재 시점에서 변경 시각 추적용.
    "docs/inter-plugin-contracts": {"kind", "registry", "version", "status", "authors",
                                    "canonical_repo", "canonical_path", "date"},
}

# CFP-33 — kind-based dispatch: docs/inter-plugin-contracts/는 두 종류 파일 보유:
#   - kind: registry → 본 lint가 검증 (REQUIRED 표 적용)
#   - kind: contract → check-inter-plugin-contracts.sh 가 별도 검증 — 본 lint는 skip
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
        # CFP-33 kind:contract dispatch — 본 lint 적용 안 함 (별도 lint)
        if prefix == "docs/inter-plugin-contracts":
            try:
                fm_peek_text = text.split("\n---\n", 1)[0][4:]
                fm_peek = yaml.safe_load(fm_peek_text)
                if isinstance(fm_peek, dict) and fm_peek.get("kind") == "contract":
                    continue
            except Exception:
                pass  # parse 실패 시 아래에서 다시 잡힘
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

# ADR-056 — kind 유효값 검증
KIND_VALID = {
    "docs/domain-knowledge/domain": {"domain_fact"},
    "docs/domain-knowledge/concept": {"concept_definition"},
}
for prefix, valid_kinds in KIND_VALID.items():
    path = Path(prefix)
    if not path.exists():
        continue
    for md in sorted(path.rglob("*.md")):
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        try:
            fm_text = text.split("\n---\n", 1)[0][4:]
            fm = yaml.safe_load(fm_text)
            if not isinstance(fm, dict):
                continue
            kind_val = fm.get("kind", "")
            if kind_val not in valid_kinds:
                warns.append(f"{md}: kind 유효값 아님 ('{kind_val}' — 허용: {valid_kinds})")
        except Exception:
            pass

if warns:
    print(f"::error::CFP-28 doc-frontmatter (STRICT): {len(warns)} 건")
    for w in warns:
        print(f"  - {w}")
    print("strict 모드 — schema 위반 시 PR 차단. 신규 작성은 templates/<doc-type>.md frontmatter schema 준수 필수.")
    sys.exit(1)

print("✓ CFP-32 doc-frontmatter: 5 owner path 전부 schema 충족")
PY

echo ""
echo "(check-doc-frontmatter: strict 모드 (CFP-28부터). warning 발견 시 exit 1)"
