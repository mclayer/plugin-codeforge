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
    "archive/adr":       {"adr_number", "title", "status", "category", "date"},
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

# ─────────────────────────────────────────────────────────────────────────────
# CFP-2680 / ADR-153 — CATEGORY_VALID: ADR category closed_enum semantic membership.
#   기존 required doc-frontmatter surface 편승 fail-closed (KIND_VALID 동형 선례).
#   enum SSOT = docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum (동적 read,
#   하드코딩 금지 — ADR-091 §결정 4 / INV-3). scope = docs/adr + archive/adr (ADR 전용 필드).
# ─────────────────────────────────────────────────────────────────────────────

# shrink-only 동결 — append 금지(4번째 = ratchet 약화, INV-2). 순수 module-level set 리터럴
# (ast.literal_eval-able; frozenset(...) call-wrap 금지, 동적 생성 금지 — self-test ast-extract).
FROZEN_BASELINE_3 = {
    ("archive/adr/ADR-131-cross-repo-responsibility-placement-governance.md", "orchestration/governance"),
    ("archive/adr/ADR-132-consumer-branch-protection-auto-wire.md", "governance/security"),
    ("archive/adr/ADR-133-adr-reservation-atomic-claim.md", "orchestration/governance"),
}

CATEGORY_SCOPE = ("docs/adr", "archive/adr")


def _cat_fold(value):
    # case-fold + strip, whole-string (split 금지 — compound loophole 차단). ASCII enum casefold==lower.
    return value.strip().casefold()


def _cat_sanitize_echo(value):
    # author-controlled 값 GHA annotation-injection 안전화 (LOG-1 / D4-esc-3):
    # CR/LF→공백(단일 라인), leading ':' neutralize, ≤80 truncate.
    s = str(value).replace("\r", " ").replace("\n", " ").lstrip(":")
    return s[:80]


def _cat_load_closed_enum():
    # enum 동적 read (per-run 1회, loop 밖 — INV-3), CWD-relative.
    # 부재/unparseable/empty → None (fail-OPEN 신호, membership skip).
    enum_path = Path("docs/confluence-ia-tree.yaml")
    if not enum_path.exists():
        return None
    try:
        data = yaml.safe_load(enum_path.read_text(encoding="utf-8"))
        raw = data["lane_mapping_rule"]["closed_enum"]
        folded = {_cat_fold(e) for e in raw if isinstance(e, str)}
        return folded or None
    except Exception:
        return None


_cat_enum_folded = _cat_load_closed_enum()
if _cat_enum_folded is None:
    # enum-source 부재/unparseable = fail-OPEN + stderr 경고 (기존 import yaml fail-open L21-25 미러).
    # membership fail-closed 무약화 (disjoint 모드) — CATEGORY_VALID 만 skip.
    if any(Path(p).exists() for p in CATEGORY_SCOPE):
        print("⚠ CATEGORY_VALID: closed_enum source (docs/confluence-ia-tree.yaml "
              "lane_mapping_rule.closed_enum) 부재/unparseable — category membership 미검사 (fail-open)",
              file=sys.stderr)
else:
    _cat_guidance = ("별도 ADR Amendment(sunset_justification 3-tuple: metric/who/how) 필요. "
                     "유효 집합 출처: docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum")
    for prefix in CATEGORY_SCOPE:
        path = Path(prefix)
        if not path.exists():
            continue
        for md in sorted(path.rglob("*.md")):
            if md.name.lower() in {"readme.md", "index.md"}:
                continue
            text = md.read_text(encoding="utf-8")
            if not text.startswith("---\n"):
                continue  # REQUIRED 가 이미 frontmatter 부재 보고
            try:
                fm_text = text.split("\n---\n", 1)[0][4:]
                fm = yaml.safe_load(fm_text)
            except Exception:
                continue  # REQUIRED 가 이미 parse 실패 보고
            if not isinstance(fm, dict):
                continue
            if "category" not in fm:
                continue  # 진짜 absent(키 부재) — REQUIRED 가 필수 필드 누락 단독 보고 (이중 경고 회피)
            cat = fm["category"]
            if cat is None:
                # present-null(`category:` bare 또는 `category: null`) — 키 존재·값 null (F-CR-2680-1).
                # absent 아님(키 존재) → REQUIRED 미보고 → blank 와 동일 fail-closed 경로 (D4-esc-1).
                warns.append(f"{md}: category (null) ∉ closed_enum — {_cat_guidance}")  # CAT-MEMBERSHIP-FAIL
                continue
            if not isinstance(cat, str):
                # non-str guard (D4-esc-2 / INV-9) — .casefold() AttributeError 로 gate 붕괴 방지
                warns.append(f"{md}: category (non-str {type(cat).__name__}) ∉ closed_enum — {_cat_guidance}")  # CAT-MEMBERSHIP-FAIL
                continue
            folded = _cat_fold(cat)
            if not folded:
                # blank/empty-after-strip → fail-closed (D4-esc-1)
                warns.append(f"{md}: category (blank) ∉ closed_enum — {_cat_guidance}")  # CAT-MEMBERSHIP-FAIL
                continue
            if (md.as_posix(), folded) in FROZEN_BASELINE_3:
                continue  # grandfather (shrink-only, FROZEN_BASELINE_3)
            if folded not in _cat_enum_folded:
                warns.append(f"{md}: category '{_cat_sanitize_echo(cat)}' ∉ closed_enum — {_cat_guidance}")  # CAT-MEMBERSHIP-FAIL

if warns:
    print(f"::error::CFP-28 doc-frontmatter (STRICT): {len(warns)} 건")
    for w in warns:
        print(f"  - {w}")
    print("strict 모드 — schema 위반 시 PR 차단. 신규 작성은 templates/<doc-type>.md frontmatter schema 준수 필수.")
    sys.exit(1)

print("✓ CFP-32 doc-frontmatter: 5 owner path 전부 schema 충족")
