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
import sys

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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
    "archive/adr": [
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

# CFP-2505 / ADR-136 결정10 — §8.7 UI 실렌더 검증 CONDITIONAL lint (§8.5 동형).
# ★ §8.6 gap allow: change-plan.md §8 은 §8.5.4 → §8.7 로 §8.6 을 의도적으로 건너뛴다
# (§8.6 Integration 은 story-page-structure.md 에만 존재). REQUIRED_SECTIONS["docs/change-plans"]
# 에 §8.6 패턴이 없으므로(추가 금지) §8.6 부재는 schema 오류로 오탐되지 않는다. 본 §8.7 lint 도
# §8.6 존재를 전제하지 않는다 — §8.7 헤딩이 있으면 §8.7.0/§8.7.1 만 검사 (gap 무관).
SECTION_8_7_HEADER_RE = re.compile(r"^####? §8\.7\b", re.MULTILINE)
SECTION_8_7_0_HEADER_RE = re.compile(r"^#####? §8\.7\.0\b", re.MULTILINE)
SECTION_8_7_1_HEADER_RE = re.compile(r"^#####? §8\.7\.1\b", re.MULTILINE)
SECTION_8_7_X_HEADER_RE = re.compile(r"^#####? §8\.7\.x\b", re.MULTILINE)
APPLICABILITY_8_7_ROW_RE = re.compile(
    r"\|\s*(CSS/SCSS 파일 변경|컴포넌트 변경|스타일 토큰/테마 변경|layout-affecting 속성 변경)[^\|]*\|\s*([YN])\s*\|",
    re.MULTILINE,
)

# ── CFP-2605 / ADR-146 §결정 5 — §8.8 동적 테스트 로스터(fuzz/property/load/concurrency) doc-section lint.
#    check_section_8_5 / check_section_8_7 verbatim 동형(I/O (md_path, body)->list, NA_85_SUBSTANTIVE_RE 재사용).
#    burden-flip 표준(do-it-unless-proven-infeasible)의 §8.8 4기법 좌표 presence/구조 fail-closed.
#    ★ §8.6 gap 무관: §8.8 헤딩 존재만 트리거(§8.6/§8.7 존재 전제 안 함).
#    ★ 정직 천장(ADR-146 결정8): 게이트는 applicability 표·산출물 계약 필드 presence/구조까지만 —
#      검출력(discriminating=G3)/열거 완결성/사유 타당성은 review·advisory·G3 로 defense-in-depth(강제 금지).
SECTION_8_8_HEADER_RE = re.compile(r"^####? §8\.8\b", re.MULTILINE)
SECTION_8_8_0_HEADER_RE = re.compile(r"^#####? §8\.8\.0\b", re.MULTILINE)
SECTION_8_8_X_HEADER_RE = re.compile(r"^#####? §8\.8\.x\b", re.MULTILINE)
APPLICABILITY_8_8_ROW_RE = re.compile(
    r"\|\s*(fuzz|property|load|concurrency)\s*\|\s*(DO|N/A)\s*\|",
    re.MULTILINE,
)
# 기법별 §8.8.N sub-section 번호 + DO 시 필수 산출물 계약 필드(change-plan §3.2 / Story §5.2)
TECHNIQUE_8_8_META = {
    "fuzz": ("8.8.1", ["target", "input_surface", "oracle", "seed_or_corpus", "execution_budget", "pass_condition"]),
    "property": ("8.8.2", ["property_definition", "input_generator", "sample_budget", "pass_condition"]),
    "load": ("8.8.3", ["load_profile", "metrics", "threshold_or_baseline_ref", "duration"]),
    "concurrency": ("8.8.4", ["shared_state", "execution_model", "worker_count", "oracle", "duration"]),
}


def _slice_8_8_subsection(body: str, sub: str) -> str:
    hdr_re = re.compile(r"^#####? §" + re.escape(sub) + r"\b", re.MULTILINE)
    m = hdr_re.search(body)
    if not m:
        return ""
    start = m.end()
    # CFP-2605 FIX(F-CR-002): slice 종료 경계 ^#{1,6} — §8.5.4/§8.7.x homolog 정합
    #   (§8.8.N 이 ≤3# 헤딩 직전 마지막 sub 일 때 over-slice 로 인한 이론적 field-masking 봉인).
    nxt = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
    end = start + (nxt.start() if nxt else len(body) - start)
    return body[start:end]


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


def check_section_8_7(md_path: Path, body: str) -> list:
    # CFP-2505 / ADR-136 결정10 — §8.7 UI 실렌더 검증 CONDITIONAL lint (§8.5 동형).
    # ★ §8.6 gap allow: §8.7 헤딩 존재만 트리거 — §8.6 존재를 전제하지 않으므로
    #   change-plan.md §8.5.4 → §8.7 gap 이 false-positive 를 내지 않는다.
    fails = []
    if not SECTION_8_7_HEADER_RE.search(body):
        return []

    if not SECTION_8_7_0_HEADER_RE.search(body):
        fails.append(f"{md_path}: §8.7 본문 존재하나 §8.7.0 Applicability decision 헤딩 부재")
        return fails

    rows = APPLICABILITY_8_7_ROW_RE.findall(body)
    found_rows = {row[0]: row[1] for row in rows}
    expected = {
        "CSS/SCSS 파일 변경",
        "컴포넌트 변경",
        "스타일 토큰/테마 변경",
        "layout-affecting 속성 변경",
    }
    missing = expected - set(found_rows.keys())
    if missing:
        fails.append(f"{md_path}: §8.7.0 표 의 4 적용 조건 행 누락 (Y/N 미파싱) — {sorted(missing)}")
        return fails

    yes_count = sum(1 for v in found_rows.values() if v == "Y")
    no_count = sum(1 for v in found_rows.values() if v == "N")

    if yes_count >= 1:
        if not SECTION_8_7_1_HEADER_RE.search(body):
            fails.append(
                f"{md_path}: §8.7.0 에 1+ Y ({yes_count}개) 인데 §8.7.1 render-truth 도구 독립성 본문 부재"
            )

    if no_count == 4:
        if not SECTION_8_7_X_HEADER_RE.search(body):
            fails.append(f"{md_path}: §8.7.0 4 N 인데 §8.7.x N/A 명시 헤딩 부재")
        else:
            m_87x = SECTION_8_7_X_HEADER_RE.search(body)
            start = m_87x.end()
            next_header = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
            end = start + (next_header.start() if next_header else len(body) - start)
            section_body = body[start:end].strip()
            if not NA_85_SUBSTANTIVE_RE.search(section_body):
                fails.append(
                    f"{md_path}: §8.7.x N/A reason 가 substantive 30자 minimum 미충족 — vague reason 차단 (CFP-2505 / ADR-136 결정10)"
                )

    return fails


def check_section_8_8(md_path: Path, body: str) -> list:
    # CFP-2605 / ADR-146 §결정 5 — §8.8 동적 로스터 lint(§8.5/§8.7 동형). §8.8 헤딩 부재 → 무검사.
    fails = []
    if not SECTION_8_8_HEADER_RE.search(body):
        return []

    if not SECTION_8_8_0_HEADER_RE.search(body):
        fails.append(f"{md_path}: §8.8 본문 존재하나 §8.8.0 Applicability decision 헤딩 부재")
        return fails

    # §8.8 region slice(§8.8 헤딩 ~ 다음 ### 헤딩) — g2 token 검사 scope 격리.
    m88 = SECTION_8_8_HEADER_RE.search(body)
    nxt3 = re.search(r"^###\s+\S", body[m88.end():], re.MULTILINE)
    region_end = m88.end() + (nxt3.start() if nxt3 else len(body) - m88.end())
    section_88 = body[m88.start():region_end]

    rows = APPLICABILITY_8_8_ROW_RE.findall(body)
    found_rows = {row[0]: row[1] for row in rows}
    expected = {"fuzz", "property", "load", "concurrency"}
    missing = expected - set(found_rows.keys())
    if missing:
        fails.append(f"{md_path}: §8.8.0 표 의 4 기법 행 누락 (DO/N/A 미파싱) — {sorted(missing)}")
        return fails

    do_count = sum(1 for v in found_rows.values() if v == "DO")
    na_count = sum(1 for v in found_rows.values() if v == "N/A")

    # AC-7 — g2_boundary_check token presence(Epic G2 경계 soak/restart/replay 무침범 확인, fail-closed).
    if "g2_boundary_check" not in section_88:
        fails.append(f"{md_path}: §8.8 g2_boundary_check token 부재 — Epic G2 경계(soak/restart/replay) 확인 누락 (AC-7)")  # MUT-B-G2-TOKEN

    if do_count >= 1:
        for tech in ("fuzz", "property", "load", "concurrency"):
            status = found_rows[tech]
            sub, req_fields = TECHNIQUE_8_8_META[tech]
            sub_body = _slice_8_8_subsection(body, sub)
            if status == "DO":
                if not sub_body:
                    fails.append(f"{md_path}: §8.8.0 {tech}=DO 이나 §{sub} 산출물 계약 본문 부재 (AC-3)")
                    continue
                missing_fields = [f for f in req_fields if f not in sub_body]
                if missing_fields:
                    fails.append(f"{md_path}: §{sub} {tech} DO 필수 산출물 필드 누락 — {missing_fields} (AC-3/4)")  # MUT-A-DO-FIELDS
                if tech == "load" and "§8.3" not in sub_body:
                    fails.append(f"{md_path}: §{sub} load DO 이나 §8.3 Perf Baseline(saturation!=regression) 관계 token 부재 (AC-6)")  # AC-6-LOAD-PERF
            else:  # status == "N/A" (mixed-case since do_count>=1)
                if not NA_85_SUBSTANTIVE_RE.search(sub_body.strip()):
                    fails.append(f"{md_path}: §{sub} {tech}=N/A(mixed) 이나 per-technique substantive infeasibility_reason(30자 minimum) 부재 (AC-2 hollow-gap)")  # MUT-C-MIXED-NA

    if na_count == 4:
        if not SECTION_8_8_X_HEADER_RE.search(body):
            fails.append(f"{md_path}: §8.8.0 4 N/A 인데 §8.8.x N/A 명시 헤딩 부재")
        else:
            m88x = SECTION_8_8_X_HEADER_RE.search(body)
            start = m88x.end()
            next_header = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
            end = start + (next_header.start() if next_header else len(body) - start)
            section_body = body[start:end].strip()
            if not NA_85_SUBSTANTIVE_RE.search(section_body):
                fails.append(f"{md_path}: §8.8.x N/A reason 가 substantive 30자 minimum 미충족 — vague reason 차단 (CFP-2605 / ADR-146 결정5)")

    return fails


def main():
    warns = []
    section_7_4_warns = []
    conditional_warns = []
    section_8_5_warns = []
    section_8_7_warns = []
    section_8_8_warns = []
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
                s87_fails = check_section_8_7(md, text)
                section_8_7_warns.extend(s87_fails)
                s88_fails = check_section_8_8(md, text)
                section_8_8_warns.extend(s88_fails)

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

    total_fails = len(warns) + len(section_7_4_warns) + len(conditional_warns) + len(section_8_5_warns) + len(section_8_7_warns) + len(section_8_8_warns) + len(debate_transcript_warns)
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
        if section_8_7_warns:
            print(f"  [CFP-2505 §8.7 UI 실렌더 applicability] {len(section_8_7_warns)} 건")
            for w in section_8_7_warns:
                print(f"  - {w}")
        if section_8_8_warns:
            print(f"  [CFP-2605 §8.8 동적 로스터 applicability] {len(section_8_8_warns)} 건")
            for w in section_8_8_warns:
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
