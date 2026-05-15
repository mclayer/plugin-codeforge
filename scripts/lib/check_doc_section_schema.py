#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# CFP-46 PR-G — §7.4 운영 리스크 schema (5 항목) + CONDITIONAL N/A 사유 (10자 minimum) 강제
# CFP-47 PR-G — §8.5 Stateful / restart invariant tests applicability lint (30자 minimum)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Usage / exit code / semantics 상세: scripts/check-doc-section-schema.sh header.
import sys, re
from pathlib import Path

REQUIRED_SECTIONS = {
    "docs/change-plans": [
        r"^### §1\. 목적",
        r"^### §2\. 현재 구조",
        r"^### §3\. 도입할 설계",
        r"^### §4\. API 계약",
        r"^### §7\. 보안",
        r"^### §8\. Test Contract",
        r"^### §10\.",
        r"^### §11\.",
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

LEGACY_CHANGE_PLAN_CFPS = {1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18}

KIND_CONTRACT_RE = re.compile(r"^kind:\s*contract\s*$", re.MULTILINE)

SECTION_7_4_HEADER_RE = re.compile(r"^### §7\.4\b", re.MULTILINE)
SECTION_7_4_REQUIRED_ITEMS = [
    "DR",
    "Cancel-on-disconnect",
    "Clock sync",
    "Rate limit",
    "Env isolation",
]

CONDITIONAL_HEADER_RE = re.compile(
    r"^(?P<hashes>#{2,6})\s+(?P<title>[^\n]*?\(CONDITIONAL\))\s*$",
    re.MULTILINE,
)

NA_JUSTIFY_RE = re.compile(r"^N/A\s+[—\-]\s+\S.{9,}")

SECTION_8_5_HEADER_RE = re.compile(r"^####? §8\.5\b", re.MULTILINE)
SECTION_8_5_0_HEADER_RE = re.compile(r"^#####? §8\.5\.0\b", re.MULTILINE)
SECTION_8_5_1_HEADER_RE = re.compile(r"^#####? §8\.5\.1\b", re.MULTILINE)
SECTION_8_5_4_HEADER_RE = re.compile(r"^#####? §8\.5\.4\b", re.MULTILINE)
APPLICABILITY_ROW_RE = re.compile(
    r"\|\s*(Long-running connection|Stateful in-memory cache|Background worker|Process restart-aware system)[^\|]*\|\s*([YN])\s*\|",
    re.MULTILINE,
)
NA_85_SUBSTANTIVE_RE = re.compile(r"^N/A\s+[—\-]\s+\S.{29,}", re.MULTILINE)

DEBATE_TRANSCRIPT_HEADER_RE = re.compile(
    r"^###\s+Debate transcript:\s*(?P<anchor>.*)$",
    re.MULTILINE,
)
ROUND_ENTRY_RE = re.compile(r"^\s*-\s*index:\s*\d+", re.MULTILINE)
TRIGGER_BLOCK_RE = re.compile(r"^####\s+trigger\b", re.MULTILINE)
TERMINATION_BLOCK_RE = re.compile(r"^####\s+termination\b", re.MULTILINE)
ROUNDS_BLOCK_RE = re.compile(r"^####\s+rounds\b", re.MULTILINE)


def check_debate_transcript(md_path: Path, body: str) -> list:
    fails = []
    lines = body.splitlines()
    for m in DEBATE_TRANSCRIPT_HEADER_RE.finditer(body):
        start = m.start()
        line_num = body[:start].count("\n")
        anchor = m.group("anchor").strip()
        if not anchor:
            fails.append(
                f"{md_path}:{line_num+1} debate transcript section — anchor_id empty (header format '### Debate transcript: <anchor_id>')"
            )
        next_header_re = re.compile(r"^#{1,3}\s+\S", re.MULTILINE)
        end_pos = len(body)
        for nm in next_header_re.finditer(body, m.end()):
            end_pos = nm.start()
            break
        section_body = body[m.end():end_pos]
        if not TRIGGER_BLOCK_RE.search(section_body):
            fails.append(
                f"{md_path}:{line_num+1} debate transcript '{anchor}' — '#### trigger' sub-block 부재"
            )
        if not ROUNDS_BLOCK_RE.search(section_body):
            fails.append(
                f"{md_path}:{line_num+1} debate transcript '{anchor}' — '#### rounds' sub-block 부재"
            )
        else:
            rounds_match = ROUNDS_BLOCK_RE.search(section_body)
            rounds_start = rounds_match.end()
            next_sub_header = re.search(r"^####\s+\S", section_body[rounds_start:], re.MULTILINE)
            rounds_end = rounds_start + (next_sub_header.start() if next_sub_header else len(section_body) - rounds_start)
            rounds_body = section_body[rounds_start:rounds_end]
            if not ROUND_ENTRY_RE.search(rounds_body):
                fails.append(
                    f"{md_path}:{line_num+1} debate transcript '{anchor}' — rounds[] 비어있음 (최소 1 라운드 '- index: <int>' entry 의무)"
                )
        if not TERMINATION_BLOCK_RE.search(section_body):
            fails.append(
                f"{md_path}:{line_num+1} debate transcript '{anchor}' — '#### termination' sub-block 부재"
            )
    return fails


def check_section_7_4(md_path: Path, body: str) -> list:
    if not SECTION_7_4_HEADER_RE.search(body):
        return []
    missing = []
    for item in SECTION_7_4_REQUIRED_ITEMS:
        if item not in body:
            missing.append(item)
    return missing


def check_conditional_na(md_path: Path, body: str) -> list:
    fails = []
    lines = body.splitlines()
    for m in CONDITIONAL_HEADER_RE.finditer(body):
        start = m.start()
        line_num = body[:start].count("\n")
        depth = len(m.group("hashes"))
        next_header_re = re.compile(
            r"^(#{1," + str(depth) + r"})\s+\S", re.MULTILINE
        )
        end_line = len(lines)
        for nm in next_header_re.finditer(body, m.end()):
            end_line = body[: nm.start()].count("\n")
            break
        body_block = "\n".join(lines[line_num + 1 : end_line]).strip()
        if not body_block:
            fails.append(
                f"{md_path}:{line_num+1} CONDITIONAL '{m.group('title').strip()}' — 본문 또는 N/A 사유 부재"
            )
            continue
        first_nontrivial = body_block.split("\n", 1)[0].strip()
        if first_nontrivial == "N/A" or re.match(r"^N/A\s*$", first_nontrivial):
            fails.append(
                f"{md_path}:{line_num+1} CONDITIONAL '{m.group('title').strip()}' — N/A 사유 부재 (10자 minimum 필요)"
            )
            continue
        if first_nontrivial.startswith("N/A"):
            if not NA_JUSTIFY_RE.match(first_nontrivial):
                fails.append(
                    f"{md_path}:{line_num+1} CONDITIONAL '{m.group('title').strip()}' — N/A 사유 10자 minimum 미충족 ('{first_nontrivial}')"
                )
                continue
    return fails


def check_section_8_5(md_path: Path, body: str) -> list:
    fails = []
    if not SECTION_8_5_HEADER_RE.search(body):
        return []

    if not SECTION_8_5_0_HEADER_RE.search(body):
        fails.append(f"{md_path}: §8.5 본문 존재하나 §8.5.0 Applicability decision 헤딩 부재")
        return fails

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
        if not SECTION_8_5_1_HEADER_RE.search(body):
            fails.append(
                f"{md_path}: §8.5.0 에 1+ Y ({yes_count}개) 인데 §8.5.1 Long-running invariant tests 본문 부재"
            )

    if no_count == 4:
        if not SECTION_8_5_4_HEADER_RE.search(body):
            fails.append(f"{md_path}: §8.5.0 4 N 인데 §8.5.4 N/A 명시 헤딩 부재")
        else:
            m_84 = SECTION_8_5_4_HEADER_RE.search(body)
            start = m_84.end()
            next_header = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
            end = start + (next_header.start() if next_header else len(body) - start)
            section_body = body[start:end].strip()
            if not NA_85_SUBSTANTIVE_RE.search(section_body):
                fails.append(
                    f"{md_path}: §8.5.4 N/A reason 가 substantive 30자 minimum 미충족 — vague reason 차단 (CFP-47 / ADR-015 결정 5)"
                )

    return fails


def main():
    warns = []
    section_7_4_warns = []
    conditional_warns = []
    section_8_5_warns = []
    debate_transcript_warns = []
    for prefix, patterns in REQUIRED_SECTIONS.items():
        path = Path(prefix)
        if not path.exists():
            continue
        for md in sorted(path.rglob("*.md")):
            if md.name.lower() in {"readme.md", "index.md"}:
                continue
            if prefix == "docs/change-plans":
                m = re.match(r"^cfp-(\d+)-", md.name)
                if m and int(m.group(1)) in LEGACY_CHANGE_PLAN_CFPS:
                    continue
            if prefix == "docs/inter-plugin-contracts":
                raw_peek = md.read_text(encoding="utf-8")
                if raw_peek.startswith("---\n"):
                    fm_peek_block = raw_peek.split("\n---\n", 1)[0][4:]
                    if KIND_CONTRACT_RE.search(fm_peek_block):
                        continue
            text = md.read_text(encoding="utf-8")
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
            if prefix == "docs/change-plans":
                s74_missing = check_section_7_4(md, text)
                if s74_missing:
                    section_7_4_warns.append(
                        f"{md}: §7.4 운영 리스크 항목 누락 — {s74_missing}"
                    )
                cond_fails = check_conditional_na(md, text)
                conditional_warns.extend(cond_fails)
                s85_fails = check_section_8_5(md, text)
                section_8_5_warns.extend(s85_fails)

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
            debate_fails = check_debate_transcript(md, text)
            debate_transcript_warns.extend(debate_fails)

    total_fails = len(warns) + len(section_7_4_warns) + len(conditional_warns) + len(section_8_5_warns) + len(debate_transcript_warns)
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
        if debate_transcript_warns:
            print(f"  [CFP-391 §9 debate transcript schema] {len(debate_transcript_warns)} 건")
            for w in debate_transcript_warns:
                print(f"  - {w}")
        print("strict 모드 — schema 위반 시 PR 차단. 신규 작성은 templates/<doc-type>.md schema + ADR-014 §7.4 5 항목 + CONDITIONAL N/A 사유 (10자 minimum) + CFP-47 §8.5 applicability (30자 minimum) + CFP-391 §9 debate transcript (anchor_id + rounds[] + trigger/termination) 준수 필수.")
        sys.exit(1)

    print("✓ CFP-46/CFP-47/CFP-391 doc-section-schema: 5 owner path schema + §7.4 5 항목 + CONDITIONAL N/A 사유 + §8.5 applicability + §9 debate transcript 모두 충족")


if __name__ == "__main__":
    main()
