#!/usr/bin/env bash
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# CFP-46 PR-G — §7.4 운영 리스크 schema (5 항목) + CONDITIONAL N/A 사유 (10자 minimum) 강제
# CFP-47 PR-G — §8.5 Stateful / restart invariant tests applicability lint (30자 minimum)
# 검사: 5 owner doc path 의 본문 필수 섹션 헤딩
#
# Section schema source:
#   - docs/change-plans/**            templates/change-plan.md  §1-§11 (주요 8개)
#                                     ※ CFP-1 ~ CFP-18 (CFP-3·CFP-17 제외) 은 schema 도입 이전 legacy
#                                       allowlist로 면제. CFP-19+ 부터 docs/superpowers/{specs,plans}/*
#                                       패턴이라 docs/change-plans/ 추가 작성 자체가 드물어짐.
#                                     ※ CFP-46 — §7.4 운영 리스크 5 항목 (DR / Cancel-on-disconnect /
#                                       Clock sync / Rate limit / Env isolation) + CONDITIONAL 절 N/A
#                                       사유 (10자 minimum) 강제. ADR-014 결정 #4 lint enforcement.
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

# CFP-46 — §7.4 운영 리스크 의무 5 항목 (ADR-014 결정 #4)
SECTION_7_4_HEADER_RE = re.compile(r"^### §7\.4\b", re.MULTILINE)
SECTION_7_4_REQUIRED_ITEMS = [
    "DR",
    "Cancel-on-disconnect",
    "Clock sync",
    "Rate limit",
    "Env isolation",
]

# CFP-46 — CONDITIONAL 표시된 헤딩 (### / #### 모두 허용)
# 형식: "### §7.4.3 Clock sync (CONDITIONAL)" 또는 "### §11.6 Idempotency invariant (CONDITIONAL)"
CONDITIONAL_HEADER_RE = re.compile(
    r"^(?P<hashes>#{2,6})\s+(?P<title>[^\n]*?\(CONDITIONAL\))\s*$",
    re.MULTILINE,
)

# CFP-46 — N/A 사유 (10자 minimum, em dash 또는 hyphen 허용)
# NA_JUSTIFY_RE: applied to single-line first_nontrivial only — MULTILINE flag unnecessary
NA_JUSTIFY_RE = re.compile(r"^N/A\s+[—\-]\s+\S.{9,}")

# CFP-47 — §8.5 Stateful / restart invariant tests applicability
# §8.5.0 Applicability decision 표 (4 적용 조건 row) + Y/N 기반 §8.5.1 또는 §8.5.4 강제
SECTION_8_5_HEADER_RE = re.compile(r"^####? §8\.5\b", re.MULTILINE)
SECTION_8_5_0_HEADER_RE = re.compile(r"^#####? §8\.5\.0\b", re.MULTILINE)
SECTION_8_5_1_HEADER_RE = re.compile(r"^#####? §8\.5\.1\b", re.MULTILINE)
SECTION_8_5_4_HEADER_RE = re.compile(r"^#####? §8\.5\.4\b", re.MULTILINE)
# §8.5.0 표 의 4 row 의 Y/N — 표 line 안의 | Y | 또는 | N | 토큰
APPLICABILITY_ROW_RE = re.compile(
    r"\|\s*(Long-running connection|Stateful in-memory cache|Background worker|Process restart-aware system)[^\|]*\|\s*([YN])\s*\|",
    re.MULTILINE,
)
# CFP-47 vague N/A reason 차단 — substantive 30자 minimum (CFP-46의 10자 minimum 보다 강화)
# applicability decision 은 더 신중한 결정 요구 (Codex 개선 #1)
NA_85_SUBSTANTIVE_RE = re.compile(r"^N/A\s+[—\-]\s+\S.{29,}", re.MULTILINE)


def check_section_7_4(md_path: Path, body: str) -> list:
    """§7.4 운영 리스크 5 항목 존재 여부. 헤딩이 없으면 skip (개별 file 의무 아님 — 본문 작성된 경우만)."""
    if not SECTION_7_4_HEADER_RE.search(body):
        return []  # §7.4 자체가 없으면 본 lint 비대상 (template §7.4 누락은 §7. 보안 검출 + N/A 처리)
    missing = []
    for item in SECTION_7_4_REQUIRED_ITEMS:
        # 단어 경계로 정확 매칭 (item 이름이 본문 어딘가에 등장하면 OK)
        # "DR" 은 흔한 약어이므로 §7.4 sub-section 헤딩 안에서 매칭하도록 하되,
        # 일단 본문 전체 substring 매칭으로 충분 (false-negative 보다 false-positive 보수적)
        if item not in body:
            missing.append(item)
    return missing


def check_conditional_na(md_path: Path, body: str) -> list:
    """CONDITIONAL 표시된 헤딩 다음 줄 ~ 다음 헤딩 사이에 N/A 사유 또는 본문이 있어야 함."""
    fails = []
    lines = body.splitlines()
    # 헤딩 line 번호 + 다음 같은-or-shallower-깊이 헤딩 line 번호 lookup
    for m in CONDITIONAL_HEADER_RE.finditer(body):
        # match start offset → line number
        start = m.start()
        line_num = body[:start].count("\n")
        depth = len(m.group("hashes"))
        # 다음 헤딩 (같거나 얕은 깊이) 찾기
        # ## ~ ###### 까지 hash 1 ~ 6
        next_header_re = re.compile(
            r"^(#{1," + str(depth) + r"})\s+\S", re.MULTILINE
        )
        end_line = len(lines)
        for nm in next_header_re.finditer(body, m.end()):
            end_line = body[: nm.start()].count("\n")
            break
        # 본문 추출 (헤딩 다음 line ~ end_line)
        body_block = "\n".join(lines[line_num + 1 : end_line]).strip()
        if not body_block:
            fails.append(
                f"{md_path}:{line_num+1} CONDITIONAL '{m.group('title').strip()}' — 본문 또는 N/A 사유 부재"
            )
            continue
        # N/A 단독? (사유 없는 'N/A' 만)
        first_nontrivial = body_block.split("\n", 1)[0].strip()
        if first_nontrivial == "N/A" or re.match(r"^N/A\s*$", first_nontrivial):
            fails.append(
                f"{md_path}:{line_num+1} CONDITIONAL '{m.group('title').strip()}' — N/A 사유 부재 (10자 minimum 필요)"
            )
            continue
        # N/A — <사유> 형식이지만 10자 미달?
        if first_nontrivial.startswith("N/A"):
            if not NA_JUSTIFY_RE.match(first_nontrivial):
                fails.append(
                    f"{md_path}:{line_num+1} CONDITIONAL '{m.group('title').strip()}' — N/A 사유 10자 minimum 미충족 ('{first_nontrivial}')"
                )
                continue
        # 그 외 본문 작성 OK
    return fails


def check_section_8_5(md_path: Path, body: str) -> list:
    """§8.5 applicability + body presence 검증 (CFP-47 / ADR-015 결정 5).

    Rules:
    - §8.5 헤딩 부재 → 본 lint 비대상 (template §8.5 누락은 §8 N/A 처리로 위임)
    - §8.5.0 헤딩 부재 → FAIL
    - §8.5.0 표 4 row 부재 (4 적용 조건 모두 매칭 부재) → FAIL
    - 1+ row Y AND §8.5.1 헤딩 부재 → FAIL
    - 4 row N AND §8.5.4 헤딩 부재 → FAIL
    - 4 row N AND §8.5.4 본문 N/A reason vague (substantive 30자 minimum 미충족) → FAIL
    """
    fails = []
    if not SECTION_8_5_HEADER_RE.search(body):
        return []  # §8.5 자체 부재 → §8 N/A 영역, 본 lint 비대상

    if not SECTION_8_5_0_HEADER_RE.search(body):
        fails.append(f"{md_path}: §8.5 본문 존재하나 §8.5.0 Applicability decision 헤딩 부재")
        return fails

    # §8.5.0 표 의 4 row 추출
    rows = APPLICABILITY_ROW_RE.findall(body)
    found_rows = {row[0]: row[1] for row in rows}
    expected = {
        "Long-running connection",
        "Stateful in-memory cache",
        "Background worker",
        "Process restart-aware system",
    }
    missing = expected - set(found_rows.keys())
    if missing:
        fails.append(f"{md_path}: §8.5.0 표 의 4 적용 조건 행 누락 — {sorted(missing)}")
        return fails

    yes_count = sum(1 for v in found_rows.values() if v == "Y")
    no_count = sum(1 for v in found_rows.values() if v == "N")

    if yes_count >= 1:
        # §8.5.1 헤딩 강제
        if not SECTION_8_5_1_HEADER_RE.search(body):
            fails.append(
                f"{md_path}: §8.5.0 에 1+ Y ({yes_count}개) 인데 §8.5.1 Long-running invariant tests 본문 부재"
            )

    if no_count == 4:
        # §8.5.4 헤딩 + N/A 본문 substantive 강제
        if not SECTION_8_5_4_HEADER_RE.search(body):
            fails.append(f"{md_path}: §8.5.0 4 N 인데 §8.5.4 N/A 명시 헤딩 부재")
        else:
            # §8.5.4 본문 추출 후 substantive check
            m_84 = SECTION_8_5_4_HEADER_RE.search(body)
            start = m_84.end()
            # 다음 헤딩 까지
            next_header = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
            end = start + (next_header.start() if next_header else len(body) - start)
            section_body = body[start:end].strip()
            if not NA_85_SUBSTANTIVE_RE.search(section_body):
                fails.append(
                    f"{md_path}: §8.5.4 N/A reason 가 substantive 30자 minimum 미충족 — vague reason 차단 (CFP-47 / ADR-015 결정 5)"
                )

    return fails


warns = []
section_7_4_warns = []
conditional_warns = []
section_8_5_warns = []
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
        # CFP-46 — change-plan 만 §7.4 + CONDITIONAL 검증
        if prefix == "docs/change-plans":
            s74_missing = check_section_7_4(md, text)
            if s74_missing:
                section_7_4_warns.append(
                    f"{md}: §7.4 운영 리스크 항목 누락 — {s74_missing}"
                )
            cond_fails = check_conditional_na(md, text)
            conditional_warns.extend(cond_fails)
            # CFP-47 — §8.5 applicability lint (change-plan 만)
            s85_fails = check_section_8_5(md, text)
            section_8_5_warns.extend(s85_fails)

# CFP-46 — change-plan 외 path (예: stories) 도 CONDITIONAL N/A 사유 강제
# (e.g. story §11 Idempotency CONDITIONAL — 향후 story schema 적용 시 활용)
for extra_prefix in ["docs/stories"]:
    extra_path = Path(extra_prefix)
    if not extra_path.exists():
        continue
    for md in sorted(extra_path.rglob("*.md")):
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        text = md.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            parts = text.split("\n---\n", 1)
            if len(parts) == 2:
                text = parts[1]
        cond_fails = check_conditional_na(md, text)
        conditional_warns.extend(cond_fails)

total_fails = len(warns) + len(section_7_4_warns) + len(conditional_warns) + len(section_8_5_warns)
if total_fails:
    print(f"::error::CFP-46/CFP-47 doc-section-schema (STRICT): {total_fails} 건")
    if warns:
        print(f"  [필수 섹션 누락] {len(warns)} 건")
        for w in warns:
            print(f"  - {w}")
    if section_7_4_warns:
        print(f"  [§7.4 운영 리스크 항목 누락] {len(section_7_4_warns)} 건")
        for w in section_7_4_warns:
            print(f"  - {w}")
    if conditional_warns:
        print(f"  [CONDITIONAL N/A 사유 부재] {len(conditional_warns)} 건")
        for w in conditional_warns:
            print(f"  - {w}")
    if section_8_5_warns:
        print(f"  [CFP-47 §8.5 applicability] {len(section_8_5_warns)} 건")
        for w in section_8_5_warns:
            print(f"  - {w}")
    print("strict 모드 — schema 위반 시 PR 차단. 신규 작성은 templates/<doc-type>.md schema + ADR-014 §7.4 5 항목 + CONDITIONAL N/A 사유 (10자 minimum) + CFP-47 §8.5 applicability (30자 minimum) 준수 필수.")
    sys.exit(1)

print("✓ CFP-46/CFP-47 doc-section-schema: 5 owner path schema + §7.4 5 항목 + CONDITIONAL N/A 사유 + §8.5 applicability 모두 충족")
PY

echo ""
echo "(check-doc-section-schema: strict 모드 (CFP-28부터). CFP-46 — §7.4 schema + CONDITIONAL N/A regex 추가. CFP-47 — §8.5 applicability lint 추가 (30자 minimum). warning 발견 시 exit 1)"
