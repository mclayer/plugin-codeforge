#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1117-S3 / ADR-091 §결정 4 + §결정 6 — Ubiquitous Language drift mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# === 목적 ===
# codeforge governance BC 의 Ubiquitous Language SSOT (docs/glossary.md) 와 Story file 안
# DDD term 사용의 일관성 검증. ADR-091 §결정 4 (Published Language) + §결정 6 (lint tier) 의
# vocabulary theater 차단 forcing function (INV-5):
#   (a) glossary term presence verify — glossary anchor (### <term>) count >= threshold (50)
#   (b) Story §ubiquitous_language `ddd_terms` enumeration ↔ glossary anchor drift detection
#       (glossary 에 정의 entry 없는 DDD term 사용 = warning)
#
# === scope ===
#   - docs/glossary.md = SSOT (term anchor source — ### heading entry)
#   - docs/stories/*.md = §ubiquitous_language block 안 ddd_terms enumeration (drift 검사 대상)
#   wrapper-local 자족 (별 repo 의존 0).
#
# === drift 판정 ===
# Story ddd_terms entry 가 glossary anchor 와 normalize 매칭 안 됨 = drift (warning).
# normalize: lowercase + 괄호/약자/BC qualifier 제거 후 substring 매칭 (예:
# "Aggregate (governance BC)" → glossary "### Aggregate (governance BC)" 매칭).
#
# === glossary presence threshold ===
# ADR-091 Story-1 carrier 가 50+ term SSOT 명시 (목차 50+ term). presence threshold = 50.
# anchor count < 50 = glossary 손상 의심 (warning).
#
# === exit code (adr-sunset-criteria.py 패턴 답습) ===
#   0 = PASS (drift 0건)
#   1 = drift 감지 (glossary presence 미달 / Story ddd_terms glossary 외 term) — fail signal.
#       warning mode = workflow `continue-on-error: true` 가 PR merge 미차단 보장.
#
# === Usage ===
#   python3 scripts/lib/check_ubiquitous_language.py [story_file ...]
#   인자 = 검사 대상 Story file path list (미제공 시 default = docs/stories/*.md glob).
#   glossary path = 고정 (docs/glossary.md).
import sys
import re
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

GLOSSARY_PATH = Path("docs/glossary.md")
GLOSSARY_TERM_PRESENCE_THRESHOLD = 50  # ADR-091 Story-1 "50+ term SSOT"

# glossary ### heading = term anchor entry. ## = category heading (제외).
GLOSSARY_ANCHOR_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def normalize_term(term: str) -> str:
    """term normalize — lowercase + 괄호 내용 보존 + 공백 압축. drift 매칭용."""
    t = term.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def normalize_for_substring(term: str) -> str:
    """괄호/약자 제거한 core token — substring 매칭 fallback용."""
    t = term.strip().lower()
    t = re.sub(r"\([^)]*\)", "", t)   # 괄호 내용 제거
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_glossary_anchors(text: str):
    """glossary ### heading anchor set 반환 (normalized + core token 2 form)."""
    full = set()
    core = set()
    for m in GLOSSARY_ANCHOR_RE.finditer(text):
        raw = m.group(1)
        full.add(normalize_term(raw))
        c = normalize_for_substring(raw)
        if c:
            core.add(c)
    return full, core


# Story §ubiquitous_language ddd_terms enumeration 추출.
# yaml block (ddd_terms: \n  - <term>) 또는 prose list 형식 포착.
DDD_TERMS_BLOCK_RE = re.compile(
    r"ddd_terms\s*:\s*\n((?:\s*-\s*.+\n?)+)",
    re.IGNORECASE,
)
DDD_TERM_ITEM_RE = re.compile(r"^\s*-\s*(.+?)\s*(?:#.*)?$", re.MULTILINE)


def extract_story_ddd_terms(text: str):
    """Story 본문 안 ddd_terms enumeration 항목 list 반환 (없으면 [])."""
    terms = []
    for block in DDD_TERMS_BLOCK_RE.finditer(text):
        body = block.group(1)
        for item in DDD_TERM_ITEM_RE.finditer(body):
            raw = item.group(1).strip().strip("`\"'")
            # placeholder 제거 (template 예시 <term>)
            if raw.startswith("<") and raw.endswith(">"):
                continue
            if raw:
                terms.append(raw)
    return terms


def term_in_glossary(term: str, anchors_full, anchors_core) -> bool:
    nt = normalize_term(term)
    if nt in anchors_full:
        return True
    nc = normalize_for_substring(term)
    if nc and nc in anchors_core:
        return True
    # substring fallback — Story term core token 이 glossary anchor core token 의 부분/포함 관계
    if nc:
        for a in anchors_core:
            if nc == a or nc in a or a in nc:
                return True
    return False


def main():
    paths = sys.argv[1:]
    if not paths:
        d = Path("docs/stories")
        paths = sorted(str(p) for p in d.glob("*.md")) if d.is_dir() else []

    drift = []

    # (a) glossary presence verify
    if not GLOSSARY_PATH.exists():
        print(
            f"⚠ check-ubiquitous-language: {GLOSSARY_PATH} 부재 "
            f"(ADR-091 §결정 4 Published Language SSOT) — glossary presence 검증 불가",
            file=sys.stderr,
        )
        sys.exit(1)

    glossary_text = GLOSSARY_PATH.read_text(encoding="utf-8")
    anchors_full, anchors_core = extract_glossary_anchors(glossary_text)
    anchor_count = len(anchors_full)

    print(f"check-ubiquitous-language: glossary anchor {anchor_count} term (threshold {GLOSSARY_TERM_PRESENCE_THRESHOLD})")

    if anchor_count < GLOSSARY_TERM_PRESENCE_THRESHOLD:
        drift.append(
            f"docs/glossary.md: term anchor {anchor_count} < threshold "
            f"{GLOSSARY_TERM_PRESENCE_THRESHOLD} (ADR-091 Story-1 50+ term SSOT — glossary 손상 의심)"
        )

    # (b) Story ddd_terms drift detection
    stories_checked = 0
    stories_with_terms = 0
    for p in paths:
        path = Path(p)
        if not path.exists() or not path.name.endswith(".md"):
            continue
        text = path.read_text(encoding="utf-8")
        stories_checked += 1
        story_terms = extract_story_ddd_terms(text)
        if not story_terms:
            continue
        stories_with_terms += 1
        for term in story_terms:
            if not term_in_glossary(term, anchors_full, anchors_core):
                drift.append(
                    f"{p}: §ubiquitous_language ddd_terms 안 {term!r} 가 "
                    f"docs/glossary.md 에 정의 entry 부재 (Ubiquitous Language drift — "
                    f"glossary anchor 추가 또는 term 정정 의무, ADR-091 §결정 4)"
                )

    print(f"check-ubiquitous-language: Story {stories_checked} file 검증 ({stories_with_terms} ddd_terms enumeration 보유)")

    if drift:
        print(f"\n⚠ drift {len(drift)}건 (Ubiquitous Language — INV-5 vocabulary theater 차단 대상):", file=sys.stderr)
        for d in drift:
            print(f"  - {d}", file=sys.stderr)
        # warning mode = workflow continue-on-error 가 PR merge 미차단 보장.
        sys.exit(1)

    print("✓ drift 0건 — Ubiquitous Language mechanical check PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
