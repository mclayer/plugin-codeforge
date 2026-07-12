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


# ── CFP-2612 / ADR-150 §결정 10 — §8.9 런타임 DAST 보안 동적 축 doc-section lint.
#    check_section_8_8 verbatim 동형(single `dast` axis — 4기법 loop 미복제). NA_85_SUBSTANTIVE_RE 재사용.
#    정직 천장(ADR-150 §결정3): applicability 레코드 + 12 산출물 필드 + status enum + infeasible⟹reason
#    + 2 cross-field 선언-정합(§결정4)까지만 fail-closed. 검출력/완결성/사유타당성/g_boundary_check 준수는 강제 안 함.
#    ★ §8.6 gap 무관: §8.9 헤딩 존재만 트리거.
SECTION_8_9_HEADER_RE = re.compile(r"^####? §8\.9\b", re.MULTILINE)
SECTION_8_9_0_HEADER_RE = re.compile(r"^#####? §8\.9\.0\b", re.MULTILINE)
SECTION_8_9_1_HEADER_RE = re.compile(r"^#####? §8\.9\.1\b", re.MULTILINE)
SECTION_8_9_X_HEADER_RE = re.compile(r"^#####? §8\.9\.x\b", re.MULTILINE)
APPLICABILITY_8_9_ROW_RE = re.compile(r"\|\s*dast\s*\|\s*(DO|N/A)\s*\|", re.MULTILINE)
# §8.9.1 dast DO 시 12 unconditional 산출물 계약 필드 (change-plan §3.2). infeasibility_reason=conditional, g_boundary_check=region-token(별도).
DAST_8_9_FIELDS = ["target", "attack_surface", "scanner_or_harness", "payload_class", "oracle", "repro_seed", "execution_budget", "pass_condition", "status", "auth_mode", "environment_ref", "observed_result"]
DAST_STATUS_ENUM = {"executed", "infeasible", "natural_na"}
DAST_PAYLOAD_ACTIVE = {"active", "destructive"}
NONPROD_MARKER_RE = re.compile(r"(?i)(non-prod|nonprod|ephemeral|staging|sandbox|local|throwaway|disposable)")


def _slice_8_9_subsection(body: str, sub: str) -> str:
    hdr_re = re.compile(r"^#####? §" + re.escape(sub) + r"\b", re.MULTILINE)
    m = hdr_re.search(body)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
    end = start + (nxt.start() if nxt else len(body) - start)
    return body[start:end]


# ── CFP-2624 / ADR-152 §결정 7 — §8.10 dark-path activation manifest doc-section lint.
#    check_section_8_9 verbatim 동형(single `dark_path` axis — 4기법 loop 미복제). NA_85_SUBSTANTIVE_RE 재사용.
#    정직 천장(ADR-152 §결정3): applicability 레코드 + 6 산출물 필드 + status enum + 2 cross-field 선언-정합
#    (activation-honesty / infeasible⟹reason)까지만 fail-closed. 검출력(discriminating-B 실행사)/열거 완결성/
#    사유타당성/g_boundary_check 준수는 강제 안 함 — G3-review·advisory defense-in-depth.
#    ★ §8.8/§8.9 zero-touch: §8.9 region-slice 종료 정규식이 이미 `^#{1,4}\s+\S`(L447) — 4-hash `#### §8.10`
#      형제에서 정확히 종료(§8.9 region 이 §8.10 으로 bleed 안 함). G5 L355 예외 불요.
#    ★ §8.6 gap 무관: §8.10 헤딩 존재만 트리거.
SECTION_8_10_HEADER_RE = re.compile(r"^####? §8\.10\b", re.MULTILINE)
SECTION_8_10_0_HEADER_RE = re.compile(r"^#####? §8\.10\.0\b", re.MULTILINE)
SECTION_8_10_1_HEADER_RE = re.compile(r"^#####? §8\.10\.1\b", re.MULTILINE)
SECTION_8_10_X_HEADER_RE = re.compile(r"^#####? §8\.10\.x\b", re.MULTILINE)
APPLICABILITY_8_10_ROW_RE = re.compile(r"\|\s*dark_path\s*\|\s*(DO|N/A)\s*\|", re.MULTILINE)
# §8.10.1 dark_path DO 시 6 unconditional 산출물 계약 필드 (change-plan §3.3). infeasibility_reason=conditional, g_boundary_check=region-token(별도).
DARK_PATH_8_10_FIELDS = ["flag_identifier", "default_state", "activation_test_ref", "on_state_assertion", "discriminating_basis", "status"]
DARK_PATH_STATUS_ENUM = {"activated", "infeasible", "natural_na"}
ON_STATE_ASSERTION_MIN = 15  # activation-honesty(§3.5a) — substantive ON-state assertion 최소 길이.


def _slice_8_10_subsection(body: str, sub: str) -> str:
    hdr_re = re.compile(r"^#####? §" + re.escape(sub) + r"\b", re.MULTILINE)
    m = hdr_re.search(body)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
    end = start + (nxt.start() if nxt else len(body) - start)
    return body[start:end]


# ── CFP-2624 / ADR-152 §결정 5 — G3(b) EPIC-RESULTS 요구-슬라이스 매핑 섹션 presence lint.
#    파일명 `EPIC-RESULTS-*.md` gate(기존 retro false-positive 0). 섹션 present ∧ (≥1 well-formed row
#    `slice|{story|defer}|tracking-ref` ∨ N/A-substantive) ∧ 천장 문구 present(AC-8). 완결성이 아닌
#    산출물 존재만 강제 — 모든 슬라이스 열거(AC-6a) = PMO Epic-close 감사 obligation(declared).
EPIC_RESULTS_NAME_RE = re.compile(r"^EPIC-RESULTS-.+\.md$")
SLICE_MAPPING_HEADER_RE = re.compile(r"^##\s+§requirement-slice-mapping\b", re.MULTILINE)
SLICE_ROW_RE = re.compile(r"^\|\s*[^|]+\|\s*(story|defer)\s*\|\s*[^|]+\|", re.MULTILINE)
SLICE_CEILING_TOKEN = "완결성"  # 천장 문구 anchor — 슬라이스 열거 완결성 미강제 정직 공개(AC-8).


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
    nxt3 = re.search(r"^#{1,4}\s+\S", body[m88.end():], re.MULTILINE)
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


def check_section_8_9(md_path: Path, body: str) -> list:
    # CFP-2612 / ADR-150 §결정 10 — §8.9 런타임 DAST 로스터 lint(§8.8 동형, single dast). §8.9 헤딩 부재 → 무검사.
    fails = []
    if not SECTION_8_9_HEADER_RE.search(body):
        return []

    if not SECTION_8_9_0_HEADER_RE.search(body):
        fails.append(f"{md_path}: §8.9 본문 존재하나 §8.9.0 Applicability decision 헤딩 부재")
        return fails

    # §8.9 region slice(§8.9 헤딩 ~ 다음 #{1,4} 헤딩) — g_boundary_check token 검사 scope 격리.
    m89 = SECTION_8_9_HEADER_RE.search(body)
    nxt = re.search(r"^#{1,4}\s+\S", body[m89.end():], re.MULTILINE)
    region_end = m89.end() + (nxt.start() if nxt else len(body) - m89.end())
    section_89 = body[m89.start():region_end]

    m = APPLICABILITY_8_9_ROW_RE.search(body)
    if not m:
        fails.append(f"{md_path}: §8.9.0 표 의 dast 행 누락 (DO/N/A 미파싱)")
        return fails
    status_cell = m.group(1)

    # AC-2c — g_boundary_check token presence(Epic G2 soak/restart/replay ∧ G4 fuzz 경계 무침범, fail-closed).
    if "g_boundary_check" not in section_89:
        fails.append(f"{md_path}: §8.9 g_boundary_check token 부재 — Epic G2(soak/restart/replay)·G4(fuzz) 경계 확인 누락 (AC-2c)")  # MUT-B-G-TOKEN

    if status_cell == "DO":
        sub_body = _slice_8_9_subsection(body, "8.9.1")
        if not sub_body:
            fails.append(f"{md_path}: §8.9.0 dast=DO 이나 §8.9.1 산출물 계약 본문 부재 (AC-2a)")
            return fails
        missing_fields = [f for f in DAST_8_9_FIELDS if f not in sub_body]
        if missing_fields:
            fails.append(f"{md_path}: §8.9.1 dast DO 필수 산출물 필드 누락 — {missing_fields} (AC-2a)")  # MUT-A-DO-FIELDS
        # AC-2b — status enum(3-value{executed/infeasible/natural_na}) + infeasible⟹infeasibility_reason(30자 minimum).
        sm = re.search(r"^\s*[-*]?\s*status:\s*(\S+)", sub_body, re.MULTILINE)
        status_val = sm.group(1) if sm else None
        if status_val is not None and status_val not in DAST_STATUS_ENUM:
            fails.append(f"{md_path}: §8.9.1 status enum 위반 '{status_val}' — {sorted(DAST_STATUS_ENUM)} 중 하나 (AC-2b)")  # MUT-D-STATUS-ENUM
        rm = re.search(r"^\s*[-*]?\s*infeasibility_reason:\s*(.+)", sub_body, re.MULTILINE)
        reason_ok = bool(rm) and len(rm.group(1).strip()) >= 30
        if status_val == "infeasible" and not reason_ok:
            fails.append(f"{md_path}: §8.9.1 status=infeasible 이나 infeasibility_reason(30자 minimum) 부재 (AC-2b)")  # MUT-E-INFEAS-REASON
        # AC-6a — blast-radius(§3.4a): payload_class ∈ {active,destructive} ⟹ environment_ref non-prod/ephemeral marker.
        pm = re.search(r"^\s*[-*]?\s*payload_class:\s*(\S+)", sub_body, re.MULTILINE)
        payload_val = pm.group(1) if pm else None
        if payload_val in DAST_PAYLOAD_ACTIVE:
            em = re.search(r"^\s*[-*]?\s*environment_ref:\s*(.+)", sub_body, re.MULTILINE)
            env_val = em.group(1) if em else ""
            if not NONPROD_MARKER_RE.search(env_val):
                fails.append(f"{md_path}: §8.9.1 payload_class={payload_val} 이나 environment_ref non-prod/ephemeral marker 부재 — blast-radius 미격리 (AC-6a)")  # MUT-F-ACTIVE-PROD
        # AC-6b — authenticated 정합(§3.4b): attack_surface authenticated ∧ auth_mode=unauthenticated ⟹ infeasibility_reason present.
        asm = re.search(r"^\s*[-*]?\s*attack_surface:\s*(.+)", sub_body, re.MULTILINE)
        surface_val = asm.group(1).lower() if asm else ""
        am = re.search(r"^\s*[-*]?\s*auth_mode:\s*(\S+)", sub_body, re.MULTILINE)
        auth_val = am.group(1) if am else None
        if re.search(r"(?<!un)authenticated", surface_val) and auth_val == "unauthenticated" and not reason_ok:
            fails.append(f"{md_path}: §8.9.1 attack_surface authenticated ∧ auth_mode=unauthenticated 이나 infeasibility_reason 부재 — silent false-negative (AC-6b)")  # MUT-G-AUTH-UNAUTH
    else:  # status_cell == "N/A" (aggregate)
        if not SECTION_8_9_X_HEADER_RE.search(body):
            fails.append(f"{md_path}: §8.9.0 dast=N/A 인데 §8.9.x N/A 명시 헤딩 부재")
        else:
            m89x = SECTION_8_9_X_HEADER_RE.search(body)
            start = m89x.end()
            next_header = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
            end = start + (next_header.start() if next_header else len(body) - start)
            section_body = body[start:end].strip()
            if not NA_85_SUBSTANTIVE_RE.search(section_body):
                fails.append(f"{md_path}: §8.9.x N/A reason 가 substantive 30자 minimum 미충족 — vague reason 차단 (CFP-2612 / ADR-150 결정10)")

    return fails


def check_section_8_10(md_path: Path, body: str) -> list:
    # CFP-2624 / ADR-152 §결정 7 — §8.10 dark-path activation manifest lint(§8.9 동형, single dark_path). §8.10 헤딩 부재 → 무검사.
    fails = []
    if not SECTION_8_10_HEADER_RE.search(body):
        return []

    if not SECTION_8_10_0_HEADER_RE.search(body):
        fails.append(f"{md_path}: §8.10 본문 존재하나 §8.10.0 Applicability decision 헤딩 부재")
        return fails

    # §8.10 region slice(§8.10 헤딩 ~ 다음 #{1,4} 헤딩) — g_boundary_check token 검사 scope 격리.
    m810 = SECTION_8_10_HEADER_RE.search(body)
    nxt = re.search(r"^#{1,4}\s+\S", body[m810.end():], re.MULTILINE)
    region_end = m810.end() + (nxt.start() if nxt else len(body) - m810.end())
    section_810 = body[m810.start():region_end]

    m = APPLICABILITY_8_10_ROW_RE.search(body)
    if not m:
        fails.append(f"{md_path}: §8.10.0 표 의 dark_path 행 누락 (DO/N/A 미파싱)")
        return fails
    status_cell = m.group(1)

    # AC-1a — g_boundary_check token presence(Epic G2 soak/restart/replay ∧ G4 fuzz ∧ G5 attack 경계 무침범, fail-closed).
    if "g_boundary_check" not in section_810:
        fails.append(f"{md_path}: §8.10 g_boundary_check token 부재 — Epic G2(soak/restart/replay)·G4(fuzz)·G5(DAST) 경계 확인 누락 (AC-1a)")  # MUT-DARK-B-G-TOKEN

    if status_cell == "DO":
        sub_body = _slice_8_10_subsection(body, "8.10.1")
        if not sub_body:
            fails.append(f"{md_path}: §8.10.0 dark_path=DO 이나 §8.10.1 산출물 계약 본문 부재 (AC-1a)")
            return fails
        missing_fields = [f for f in DARK_PATH_8_10_FIELDS if f not in sub_body]
        if missing_fields:
            fails.append(f"{md_path}: §8.10.1 dark_path DO 필수 산출물 필드 누락 — {missing_fields} (AC-1a)")  # MUT-DARK-A-DO-FIELDS
        # status enum(3-value{activated/infeasible/natural_na}).
        sm = re.search(r"^\s*[-*]?\s*status:\s*(\S+)", sub_body, re.MULTILINE)
        status_val = sm.group(1) if sm else None
        if status_val is not None and status_val not in DARK_PATH_STATUS_ENUM:
            fails.append(f"{md_path}: §8.10.1 status enum 위반 '{status_val}' — {sorted(DARK_PATH_STATUS_ENUM)} 중 하나 (AC-1a)")  # MUT-DARK-C-STATUS-ENUM
        # conditional infeasibility_reason(30자 minimum).
        rm = re.search(r"^\s*[-*]?\s*infeasibility_reason:\s*(.+)", sub_body, re.MULTILINE)
        reason_ok = bool(rm) and len(rm.group(1).strip()) >= 30
        # cross-field (a) activation-honesty(§3.5a): status=activated ⟹ activation_test_ref non-empty ∧ on_state_assertion substantive(≥15자).
        #   ★ 값 캡처 = `[ \t]*(.*)$` (same-line only) — `\s*` 는 개행을 삼켜 빈 값이 다음 줄 내용을 흡수함(false-fill 방지).
        atm = re.search(r"^\s*[-*]?\s*activation_test_ref:[ \t]*(.*)$", sub_body, re.MULTILINE)
        atref = atm.group(1).strip() if atm else ""
        osm = re.search(r"^\s*[-*]?\s*on_state_assertion:[ \t]*(.*)$", sub_body, re.MULTILINE)
        osassert = osm.group(1).strip() if osm else ""
        if status_val == "activated" and not (atref and len(osassert) >= ON_STATE_ASSERTION_MIN):
            fails.append(f"{md_path}: §8.10.1 status=activated 이나 activation_test_ref 공백 또는 on_state_assertion(15자 minimum) 부재 — 빈 stub 활성화 위장 차단 (AC-2 activation-honesty §3.5a)")  # MUT-DARK-D-ACTIVATION
        # cross-field (b) infeasible-reason(§3.5b).
        if status_val == "infeasible" and not reason_ok:
            fails.append(f"{md_path}: §8.10.1 status=infeasible 이나 infeasibility_reason(30자 minimum) 부재 (AC-1a §3.5b)")  # MUT-DARK-E-INFEAS-REASON
    else:  # status_cell == "N/A" (aggregate)
        if not SECTION_8_10_X_HEADER_RE.search(body):
            fails.append(f"{md_path}: §8.10.0 dark_path=N/A 인데 §8.10.x N/A 명시 헤딩 부재")
        else:
            m810x = SECTION_8_10_X_HEADER_RE.search(body)
            start = m810x.end()
            next_header = re.search(r"^#{1,6}\s+\S", body[start:], re.MULTILINE)
            end = start + (next_header.start() if next_header else len(body) - start)
            section_body = body[start:end].strip()
            if not NA_85_SUBSTANTIVE_RE.search(section_body):
                fails.append(f"{md_path}: §8.10.x N/A reason 가 substantive 30자 minimum 미충족 — vague reason 차단 (CFP-2624 / ADR-152 결정7)")

    return fails


def check_epic_results_slice_mapping(md_path: Path, body: str) -> list:
    # CFP-2624 / ADR-152 §결정 5 — G3(b) EPIC-RESULTS 요구-슬라이스 매핑 섹션 presence lint(AC-6b).
    #   파일명 EPIC-RESULTS-*.md gate → 섹션 present ∧ (≥1 well-formed row ∨ N/A-substantive) ∧ 천장 문구 present.
    #   완결성(모든 슬라이스 열거, AC-6a)은 강제 안 함 — PMO Epic-close 감사 obligation(declared).
    fails = []
    if not EPIC_RESULTS_NAME_RE.match(md_path.name):
        return []
    m = SLICE_MAPPING_HEADER_RE.search(body)
    if not m:
        fails.append(f"{md_path}: EPIC-RESULTS §requirement-slice-mapping 섹션 부재 — 요구 슬라이스 silent drop 차단 (AC-6b)")  # MUT-SLICE-PRESENCE
        return fails
    # 섹션 region slice(## §requirement-slice-mapping ~ 다음 ## 헤딩).
    start = m.end()
    nxt = re.search(r"^##\s+\S", body[start:], re.MULTILINE)
    end = start + (nxt.start() if nxt else len(body) - start)
    section = body[start:end]
    # ≥1 well-formed row(slice|{story|defer}|tracking-ref) OR N/A-substantive(30자 minimum).
    has_row = bool(SLICE_ROW_RE.search(section))
    has_na = bool(NA_85_SUBSTANTIVE_RE.search(section.strip()))
    if not (has_row or has_na):
        fails.append(f"{md_path}: §requirement-slice-mapping 섹션 present 이나 well-formed row(slice|(story|defer)|tracking-ref) 또는 N/A(30자 minimum) 부재 (AC-6b)")  # MUT-SLICE-ROW
    # 천장 문구 present(AC-8 no-hollow — 슬라이스 열거 완결성 미강제 정직 공개).
    if SLICE_CEILING_TOKEN not in section:
        fails.append(f"{md_path}: §requirement-slice-mapping 정직 천장 문구('{SLICE_CEILING_TOKEN}') 부재 — 슬라이스 열거 완결성 미강제 공개 누락 (AC-8)")  # MUT-SLICE-CEILING
    return fails


def main():
    warns = []
    section_7_4_warns = []
    conditional_warns = []
    section_8_5_warns = []
    section_8_7_warns = []
    section_8_8_warns = []
    section_8_9_warns = []
    section_8_10_warns = []
    slice_mapping_warns = []
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
                s89_fails = check_section_8_9(md, text)
                section_8_9_warns.extend(s89_fails)
                s810_fails = check_section_8_10(md, text)
                section_8_10_warns.extend(s810_fails)
            if prefix == "docs/retros":
                slice_fails = check_epic_results_slice_mapping(md, text)
                slice_mapping_warns.extend(slice_fails)

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

    total_fails = len(warns) + len(section_7_4_warns) + len(conditional_warns) + len(section_8_5_warns) + len(section_8_7_warns) + len(section_8_8_warns) + len(section_8_9_warns) + len(section_8_10_warns) + len(slice_mapping_warns) + len(debate_transcript_warns)
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
        if section_8_9_warns:
            print(f"  [CFP-2612 §8.9 DAST 로스터 applicability] {len(section_8_9_warns)} 건")
            for w in section_8_9_warns:
                print(f"  - {w}")
        if section_8_10_warns:
            print(f"  [CFP-2624 §8.10 dark-path 로스터 applicability] {len(section_8_10_warns)} 건")
            for w in section_8_10_warns:
                print(f"  - {w}")
        if slice_mapping_warns:
            print(f"  [CFP-2624 EPIC-RESULTS §requirement-slice-mapping] {len(slice_mapping_warns)} 건")
            for w in slice_mapping_warns:
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
