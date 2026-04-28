#!/usr/bin/env bash
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# 검사: 5 owner doc path 의 본문 필수 섹션 헤딩
#
# Section schema source:
#   - docs/change-plans/**            templates/change-plan.md  §1-§11 (주요 8개)
#                                     ※ CFP-1 ~ CFP-18 (CFP-3·CFP-17 제외) 은 schema 도입 이전 legacy
#                                       allowlist로 면제. CFP-19+ 부터 docs/superpowers/{specs,plans}/*
#                                       패턴이라 docs/change-plans/ 추가 작성 자체가 드물어짐.
#   - docs/adr/**                     templates/adr.md          ## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 관련 파일
#   - docs/domain-knowledge/**        templates/domain-knowledge.md ## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력
#   - docs/retros/**                  templates/retro.md         ## §1 / ## §2 / ## §3 / ## §4 (제목 자유, §N prefix만 강제)
#   - docs/inter-plugin-contracts/**  registry kind: ## 1. 목적 / ## 2. Schema / ## 3. 항목 / ## 4. 변경 규칙
#                                     ※ kind: contract 파일은 본 lint 적용 안 함 (CFP-33부터)
#                                       check-inter-plugin-contracts.sh 가 별도 검증
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
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
        r"^### §10\.",      # ADR 정합성 + 신규 ADR 필요 여부 판정 — 헤딩 prefix만 (template §10)
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
        # 회고 종류 (closure / cross-Story / sprint / session)별 §1 명칭이 자연스럽게 다름.
        # schema intent는 "첫 메이저 섹션이 §1로 시작" — prefix만 강제, 제목 자유.
        r"^## §1\s+\S",
        r"^## §2\s+\S",
        r"^## §3\s+\S",
        r"^## §4\s+\S",
    ],
    "docs/inter-plugin-contracts": [
        r"^## 1\. 목적",
        r"^## 2\. Schema",
        r"^## 3\. 항목",
        r"^## 4\. 변경 규칙",
    ],
}

# Legacy change-plan allowlist — pre-CFP-27 schema 이전 산출물.
# CFP-19+ 부터 docs/superpowers/{specs,plans}/* 패턴 적용으로 docs/change-plans/ 디렉토리는
# 사실상 freeze. Backfill 비용 회피하고 신규 작성에 대해서만 strict 적용.
LEGACY_CHANGE_PLAN_CFPS = {1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18}

# CFP-33 — kind:contract 파일은 본 lint 적용 안 함 (별도 lint 운영, 섹션 schema 자유)
KIND_CONTRACT_RE = re.compile(r"^kind:\s*contract\s*$", re.MULTILINE)

warns = []
for prefix, patterns in REQUIRED_SECTIONS.items():
    path = Path(prefix)
    if not path.exists():
        continue
    for md in sorted(path.rglob("*.md")):
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        # Legacy change-plan allowlist (path-scoped)
        if prefix == "docs/change-plans":
            m = re.match(r"^cfp-(\d+)-", md.name)
            if m and int(m.group(1)) in LEGACY_CHANGE_PLAN_CFPS:
                continue
        # CFP-33 kind:contract dispatch — 본 lint 적용 안 함 (regex로 frontmatter peek)
        if prefix == "docs/inter-plugin-contracts":
            raw_peek = md.read_text(encoding="utf-8")
            if raw_peek.startswith("---\n"):
                fm_peek_block = raw_peek.split("\n---\n", 1)[0][4:]
                if KIND_CONTRACT_RE.search(fm_peek_block):
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
    print(f"::error::CFP-28 doc-section-schema (STRICT): {len(warns)} 건")
    for w in warns:
        print(f"  - {w}")
    print("strict 모드 — schema 위반 시 PR 차단. 신규 작성은 templates/<doc-type>.md schema 준수 필수.")
    sys.exit(1)

print("✓ CFP-32 doc-section-schema: 5 owner path 전부 schema 충족")
PY

echo ""
echo "(check-doc-section-schema: strict 모드 (CFP-28부터). warning 발견 시 exit 1)"
