#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# ADR-056 — docs/domain-knowledge/domain + concept 경로 분기, kind 필드 검증 추가 (CFP-376)
# CFP-391 — registry kind 필수 필드에 canonical_repo / canonical_path / date 추가 (debate-protocol-v1)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
# 검사: 5 owner doc path 의 frontmatter 필수 필드
# Usage / exit code / semantics 상세: scripts/check-doc-frontmatter.sh header.
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
    print("⚠ check-doc-frontmatter: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

REQUIRED = {
    "docs/change-plans": {"title", "slug", "status", "author", "created", "story"},
    "docs/adr":          {"adr_number", "title", "status", "category", "date"},
    "docs/domain-knowledge/domain": {"kind", "title", "area", "topic_slug", "status", "updated"},
    "docs/domain-knowledge/concept": {"kind", "title", "slug", "status", "updated"},
    "docs/retros":       {"title", "date", "sprint_period", "cfp_keys", "authors"},
    "docs/inter-plugin-contracts": {"kind", "registry", "version", "status", "authors",
                                    "canonical_repo", "canonical_path", "date"},
}

warns = []
for prefix, fields in REQUIRED.items():
    path = Path(prefix)
    if not path.exists():
        continue
    for md in sorted(path.rglob("*.md")):
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
                pass
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
# CFP-2453 / ADR-091 Amd3 — lexicon_relation kind 등록 (consumer application-BC lexicon.md schema).
#   domain/<area>/lexicon.md 는 domain_fact 와 동일 REQUIRED 필드 set(kind/title/area/topic_slug/
#   status/updated) 공유 — KIND_VALID 만 확장 (REQUIRED 무변경). concept-dictionary 는 기존
#   concept_definition 재사용(경로 owner 기반, 신규 kind 0) — concept/ KIND_VALID 무변경.
KIND_VALID = {
    "docs/domain-knowledge/domain": {"domain_fact", "lexicon_relation"},
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
