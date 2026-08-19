#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-34 (ζ arc F3) — Workflow yaml syntax + regex fixture tests
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# 검사: 3 핵심 workflow의 yaml syntax + 핵심 regex 패턴 존재 + Python re-impl fixture 검증
# Usage / exit code / semantics 상세: scripts/check-workflow-yaml.sh header.
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
    print("⚠ check-workflow-yaml: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

errors = []

# === 1. yaml 파싱 + 패턴 존재 검증 ===
EXPECTED_PATTERNS = {
    "templates/github-workflows/fix-ledger-sync.yml": [
        r"##\\s\*10\\\.",
        r"\[FIX #",
        r"fix:.*-retry",
    ],
    "templates/github-workflows/subissue-from-impl-manifest.yml": [
        r"##\\s\*8\\\.5",
        r"impl-manifest",
    ],
    ".github/workflows/phase-gate-mergeable.yml": [
        r"Related\|Closes\|Fixes\|Resolves",
        r"phase:",
        r"gate:",
    ],
}

for yml_path, patterns in EXPECTED_PATTERNS.items():
    p = Path(yml_path)
    if not p.exists():
        errors.append(f"{yml_path}: 파일 부재")
        continue
    raw = p.read_text(encoding="utf-8")
    try:
        yaml.safe_load(raw)
    except yaml.YAMLError as e:
        errors.append(f"{yml_path}: yaml 파싱 실패 — {e}")
        continue
    for pat in patterns:
        if not re.search(pat, raw):
            errors.append(f"{yml_path}: 핵심 패턴 부재 — {pat!r}")

# === 2. Fixture 1: fix-ledger-sync.yml §10 row parsing (Python parallel impl) ===
#
# ★ CFP-2985 D-20 — 본 fixture 는 **계약에서 유도**한다 (하드코딩 금지).
#
#   직전 판은 7-column §10 표를 소스에 리터럴로 박아두고 그것을 검증했다. 그 결과 계약
#   `fix-event-v1` 이 v1.0 7열 → v1.6 15열 로 이동하고 `원인 판정` 값공간이 2 → 6 으로
#   늘어나는 동안 이 fixture 는 **한 번도 움직이지 않은 채 GREEN 이었다**. cause 칸에 대해
#   무언가를 주장하는 마지막 자산이 조용히 틀린 값을 동결하고 있었다는 뜻이다.
#   ⇒ 열 수·열 이름·값공간을 상수로 두지 않는다. 계약 §10 정본 표를 파싱해 산출한다.
#
#   ★ 상수 fallback 을 두지 않는다 — 파싱이 실패하면 fallback 으로 조용히 넘어가는 게 아니라
#     error 다. fallback 이 있으면 계약 drift 가 영원히 관측되지 않는다 (fail-closed).
#
#   ★ 계약 §10 정본 표는 markdown **코드펜스 안**에 있다. 펜스를 제외하고 스캔하면
#     검출 0건이 되고 아래 vacuity 가드가 그것을 RED 로 만든다 (조용한 0건 금지).

CONTRACT_PATH = Path("docs/inter-plugin-contracts/fix-event-v1.md")
PROD_PARSER_PATH = Path("templates/github-workflows/fix-ledger-sync.yml")


def strip_cell(s):
    return s.replace("`", "").strip()


def _is_pipe_row(line):
    return line.startswith("|")


def _is_separator_row(line):
    return re.match(r"^\|[\s|:-]+\|$", line) is not None


def split_row(line):
    """프로덕션 파서와 동일 분해: row.split('|').slice(1,-1).map(stripCell)"""
    return [strip_cell(c) for c in line.split("|")[1:-1]]


def iter_markdown_tables(text, include_fenced):
    """text 안 markdown 표를 (header_cells, data_row_lines) 로 산출.

    include_fenced=False 면 코드펜스 내부를 건너뛴다. 계약 §10 정본 표는 펜스 안이므로
    False 로 스캔하면 0건이 된다 — 그 사실 자체를 검사에 쓴다(아래 판별 가드).
    """
    tables = []
    in_fence = False
    cur_header = None
    cur_rows = None
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            # 펜스 경계에서 진행 중이던 표를 **버리지 않고 flush** 한다.
            # 정본 표는 펜스 닫힘 직전에 끝나므로 여기서 버리면 include_fenced=True 여도 0건이 된다.
            if cur_header is not None and cur_rows:
                tables.append((cur_header, cur_rows))
            in_fence = not in_fence
            cur_header, cur_rows = None, None
            continue
        if in_fence and not include_fenced:
            continue
        stripped = line.strip()
        if _is_pipe_row(stripped):
            if cur_header is None:
                cur_header = split_row(stripped)
                cur_rows = []
            elif _is_separator_row(stripped):
                continue
            else:
                cur_rows.append(stripped)
        else:
            if cur_header is not None and cur_rows:
                tables.append((cur_header, cur_rows))
            cur_header, cur_rows = None, None
    if cur_header is not None and cur_rows:
        tables.append((cur_header, cur_rows))
    return tables


def contract_section10_tables(text, include_fenced=True):
    """계약 안 §10 행 형식 표 전부 — 헤더 첫 칸이 'Iter' 인 표로 식별."""
    out = []
    for header, rows in iter_markdown_tables(text, include_fenced=include_fenced):
        if header and header[0] == "Iter":
            out.append((header, rows))
    return out


def contract_cause_enum(text):
    """계약 §2 schema 표의 `원인 판정` 행에서 enum 값공간을 산출.

    형식: | 원인 판정 | enum | required | A / B / C (...주석) |
    첫 괄호·별표 앞까지만 값 목록으로 보고 '/' 로 분해한다.
    """
    for header, rows in iter_markdown_tables(text, include_fenced=True):
        for row in rows:
            cells = split_row(row)
            if len(cells) >= 4 and cells[0] == "원인 판정" and cells[1] == "enum":
                desc = cells[3]
                head = re.split(r"[(（★]", desc, maxsplit=1)[0]
                vals = [v.strip() for v in head.split("/")]
                return [v for v in vals if v and " " not in v]
    return []


def prod_parser_cell_indices(text):
    """프로덕션 JS 파서가 하드코딩한 `<field>: cells[N]` 바인딩을 산출."""
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"(\w+)\s*:\s*cells\[(\d+)\]", text)}


# 프로덕션 파서 필드명 → 계약 §10 헤더명. 이 바인딩이 본 검사의 대상이다
# (인덱스는 JS 에서, 이름은 계약에서 유도하고 둘의 정합만 여기서 주장한다).
PROD_FIELD_TO_HEADER = {
    "ts": "시각",
    "lane": "레인",
    "trigger": "트리거",
    "cause": "원인 판정",
    "scope": "재실행 범위",
    "reset": "RESET?",
}

if not CONTRACT_PATH.exists():
    errors.append(f"{CONTRACT_PATH}: 계약 파일 부재 — §10 fixture 유도 불가")
elif not PROD_PARSER_PATH.exists():
    errors.append(f"{PROD_PARSER_PATH}: 프로덕션 §10 파서 부재 — 인덱스 바인딩 유도 불가")
else:
    contract_text = CONTRACT_PATH.read_text(encoding="utf-8")
    prod_text = PROD_PARSER_PATH.read_text(encoding="utf-8")

    s10_tables = contract_section10_tables(contract_text, include_fenced=True)
    cause_enum = contract_cause_enum(contract_text)
    prod_idx = prod_parser_cell_indices(prod_text)

    # -- vacuity 가드 (조용한 0건 금지) --------------------------------------
    if not s10_tables:
        errors.append(
            f"§10 fixture: {CONTRACT_PATH} 에서 §10 행 표를 0건 추출 — "
            "정본 표는 코드펜스 안이다 (include_fenced 미적용 의심). 상수 fallback 없음 = RED")
    if not cause_enum:
        errors.append("§10 fixture: 계약 §2 `원인 판정` enum 값공간 추출 0건")
    if not prod_idx:
        errors.append(f"§10 fixture: {PROD_PARSER_PATH} 에서 `cells[N]` 바인딩 추출 0건")

    # -- 펜스 제외 스캔은 0건이어야 한다 (include_fenced 가 load-bearing 임을 실증) --
    if s10_tables:
        unfenced = contract_section10_tables(contract_text, include_fenced=False)
        if unfenced:
            errors.append(
                "§10 fixture: 펜스 제외 스캔이 §10 표를 %d 건 반환 — 정본 표 위치 전제가 깨졌다"
                % len(unfenced))

    if s10_tables and cause_enum and prod_idx:
        # 정본 = 열이 가장 많은 표 (v1.6 15열). backward-compat 7열 표도 함께 존재한다.
        canonical_header, canonical_rows = max(s10_tables, key=lambda t: len(t[0]))
        SECTION10_FIXTURE = "\n".join(
            ["| " + " | ".join(canonical_header) + " |"] + canonical_rows)

        # -- (a) 프로덕션 하드코딩 인덱스가 계약 헤더의 같은 자리를 가리키는가 --
        #    계약이 열을 삽입·재배열하면 cells[4] 는 조용히 다른 칸을 읽는다.
        for field, header_name in PROD_FIELD_TO_HEADER.items():
            if field not in prod_idx:
                errors.append(f"§10 fixture: 프로덕션 파서에 `{field}: cells[N]` 바인딩 부재")
                continue
            n = prod_idx[field]
            if n >= len(canonical_header):
                errors.append(
                    f"§10 fixture: 프로덕션 `{field}: cells[{n}]` 가 "
                    f"계약 {len(canonical_header)}열 밖")
            elif canonical_header[n] != header_name:
                errors.append(
                    f"§10 fixture: 인덱스 drift — 프로덕션 `{field}: cells[{n}]` 인데 "
                    f"계약 {n}번 열은 {canonical_header[n]!r} (기대 {header_name!r})")

        # -- (b) 정본 표를 프로덕션 파서와 동일 술어로 파싱 --
        events = []
        for row in canonical_rows:
            cells = split_row(row)
            if len(cells) < 6:
                continue
            if not re.match(r"^\d+$", cells[0] or ""):
                continue
            events.append({
                "iter": int(cells[0]),
                "lane": cells[prod_idx["lane"]],
                "cause": cells[prod_idx["cause"]],
                "reset": cells[prod_idx["reset"]],
            })
        if len(events) != len(canonical_rows):
            errors.append(
                f"§10 fixture: 정본 표 {len(canonical_rows)} 행 중 {len(events)} 행만 파싱 — "
                "프로덕션 파서가 계약 예시를 전건 소비하지 못한다")
        if events and [e["iter"] for e in events] != list(range(1, len(events) + 1)):
            errors.append(f"§10 fixture: Iter 연번 불연속 — {[e['iter'] for e in events]}")

        # -- (c) 추출된 cause 가 계약 §2 값공간 안인가 (값공간도 유도) --
        for e in events:
            if e["cause"] not in cause_enum:
                errors.append(
                    f"§10 fixture: Iter {e['iter']} cause {e['cause']!r} 가 계약 §2 "
                    f"`원인 판정` 값공간 {cause_enum} 밖")

        # -- (d) 값공간 확장이 실제로 표에 도달했는가 (2값 시절 동결 방지) --
        used = {e["cause"] for e in events}
        if len(cause_enum) > 2 and used <= {"설계", "구현"}:
            errors.append(
                f"§10 fixture: 계약 값공간은 {len(cause_enum)}값인데 정본 표가 쓰는 값은 "
                f"{sorted(used)} 뿐 — 확장이 예시에 도달하지 않았다")

        # -- (e) backward-compat 표의 헤더가 정본의 접두인가 --
        #    계약이 "trailing optional column 추가라 regex 비충돌" 이라 주장하는 근거 그 자체.
        for header, _rows in s10_tables:
            if header is canonical_header:
                continue
            if canonical_header[:len(header)] != header:
                errors.append(
                    "§10 fixture: backward-compat 표 헤더가 정본의 접두가 아니다 — "
                    f"{header} vs {canonical_header[:len(header)]}")

        # -- (f) RESET 마커가 표에 실재하는가 (RESET 시맨틱스 검출력 보존) --
        if events and not any(e["reset"].startswith("RESET") for e in events):
            errors.append("§10 fixture: 정본 표에 RESET 마커 행이 0 — RESET 검출력 대조군 소실")

# === 3. Fixture 2: subissue-from-impl-manifest.yml §8.5 + Issue 추출 ===
ISSUE_BODY_FIXTURE = """- **Story KEY**: PLG-1
- **Issue**: #42
- **Phase 1 PR**: ..."""
issue_match = re.search(r"^\s*-\s*\*\*Issue\*\*:\s*#(\d+)", ISSUE_BODY_FIXTURE, re.MULTILINE)
if not issue_match or issue_match.group(1) != "42":
    errors.append(f"subissue fixture: Issue 추출 실패 (expected #42, got {issue_match})")

# === 4. Fixture 3: phase-gate-mergeable.yml Closes/Fixes/Resolves 추출 ===
ref_re = re.compile(r"(?:Related|Closes|Fixes|Resolves):?\s+#(\d+)", re.IGNORECASE)

PR_POS = "Implementation done. Closes #5 + Resolves: #10. Also Fixes #15."
pos_refs = sorted(ref_re.findall(PR_POS), key=int)
if pos_refs != ["5", "10", "15"]:
    errors.append(f"phase-gate fixture pos: expected ['5','10','15'], got {pos_refs}")

PR_NEG = "Closing #5"  # 다른 동사
neg_refs = ref_re.findall(PR_NEG)
if neg_refs:
    errors.append(f"phase-gate fixture neg ('Closing'): expected empty, got {neg_refs}")

PR_RELATED = "Related #99"
rel_refs = ref_re.findall(PR_RELATED)
if rel_refs != ["99"]:
    errors.append(f"phase-gate fixture related: expected ['99'], got {rel_refs}")

# === Output ===
if errors:
    print(f"::error::CFP-34 workflow-yaml (STRICT): {len(errors)} 건")
    for e in errors:
        print(f"  - {e}")
    print("strict 모드 — workflow yaml syntax / 핵심 regex / fixture 위반 시 PR 차단.")
    sys.exit(1)

print("✓ CFP-34 workflow-yaml: 3 workflow yaml 패턴 + 3 fixture 검증 충족")
