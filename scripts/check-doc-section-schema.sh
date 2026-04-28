#!/usr/bin/env bash
# CFP-27 Phase 0b
# 검사: 4 owner doc path 의 본문 필수 섹션 헤딩 (warning 모드 — exit=0 with warnings)
#
# Section schema source:
#   - docs/change-plans/**     templates/change-plan.md  §1-§11 (주요 8개)
#   - docs/adr/**              templates/adr.md          ## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 관련 파일
#   - docs/domain-knowledge/** templates/domain-knowledge.md ## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력
#   - docs/retros/**           templates/retro.md         ## §1 결과 / ## §2 / ## §3 / ## §4 (§5-§8 선택)
#
# CFP-28에서 strict 모드 (exit=1) 전환.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY' || true
import sys, re
from pathlib import Path

REQUIRED_SECTIONS = {
    "docs/change-plans": [
        # change-plan.md 본문 §1-§11 중 항상 필요한 핵심 8개 (선택 §은 제외)
        r"^### §1\. 목적",
        r"^### §2\. 현재 구조",
        r"^### §3\. 도입할 설계",
        r"^### §4\. API 계약",
        r"^### §7\. 보안",   # 보안 설계 (CFP-17 이후 항상 필요, 무관 시 N/A 명시)
        r"^### §8\. Test Contract",
        r"^### §10\.",      # FIX Ledger 위치 — 정확 명칭은 schema 변동, 헤딩 prefix만
        r"^### §11\.",      # 데이터 마이그레이션 (CFP-21 이후)
    ],
    "docs/adr": [
        r"^## 상태",
        r"^## 컨텍스트",
        r"^## 결정",
        r"^## 결과",
        r"^## 관련 파일",
    ],
    "docs/domain-knowledge": [
        r"^## 정의",
        r"^## 컨텍스트",
        r"^## 핵심 규칙",
        r"^## 경계",
        r"^## 관련 ADR",
        r"^## 변경 이력",
    ],
    "docs/retros": [
        r"^## §1 결과",
        r"^## §2 ",   # 무엇이 잘 갔나
        r"^## §3 ",   # 무엇이 막혔나
        r"^## §4 ",   # 다음에 할 일
    ],
}

warns = []
for prefix, patterns in REQUIRED_SECTIONS.items():
    path = Path(prefix)
    if not path.exists():
        continue
    for md in sorted(path.rglob("*.md")):
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        text = md.read_text(encoding="utf-8")
        # frontmatter 영역 제거
        if text.startswith("---\n"):
            parts = text.split("\n---\n", 1)
            if len(parts) == 2:
                text = parts[1]
        missing = []
        for p in patterns:
            if not re.search(p, text, re.MULTILINE):
                missing.append(p)
        if missing:
            warns.append(f"{md}: 필수 섹션 누락 — {missing}")

if warns:
    print(f"⚠ CFP-27 doc-section-schema (WARN): {len(warns)} 건")
    for w in warns:
        print(f"  - {w}")
    print("⚠ warning 모드 — CFP-28 strict 전환 시점에 모두 fix 또는 allowlist 필요")
else:
    print("✓ CFP-27 doc-section-schema: 4 owner path 전부 schema 충족")
PY

echo ""
echo "(check-doc-section-schema: warning 모드 — exit 0 강제. CFP-28에서 strict 전환)"
exit 0
