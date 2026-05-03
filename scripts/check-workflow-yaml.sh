#!/usr/bin/env bash
# CFP-34 (ζ arc F3) — Workflow yaml syntax + regex fixture tests
#
# 검사: 3 핵심 workflow의 yaml syntax + 핵심 regex 패턴 존재 + Python re-impl fixture 검증
#
# - templates/github-workflows/fix-ledger-sync.yml — §10 row parsing (consumer-only, CFP-67/68)
# - templates/github-workflows/subissue-from-impl-manifest.yml — §8.5 row parsing (consumer-only, CFP-68)
# - .github/workflows/phase-gate-mergeable.yml — Closes/Fixes/Resolves ref extraction (plugin-self)
#
# Codex round 2 조건 #3 직접 대응: encoding-sensitive regex CI 사전 lint.
# Python re-impl 이 yaml 안 JS 와 drift 시 fixture가 catch (yaml 변경 후 Python 미동기 = fail).
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import sys, re, yaml
from pathlib import Path

errors = []

# === 1. yaml 파싱 + 패턴 존재 검증 ===
EXPECTED_PATTERNS = {
    # CFP-68 — consumer-only workflow 의 yaml content 검증 source 를 templates/ 로 align.
    # plugin-codeforge 는 internal-docs Story binding 사용으로 .github/workflows/ self-app 부재 (CONSUMER_ONLY_WORKFLOWS exclusion).
    "templates/github-workflows/fix-ledger-sync.yml": [
        r"##\\s\*10\\\.",
        r"\[FIX #",
        r"fix:.*-retry",
    ],
    "templates/github-workflows/subissue-from-impl-manifest.yml": [
        r"##\\s\*8\\\.5",
        r"impl-manifest",
    ],
    # plugin-self workflow — .github/workflows/ 에서 직접 검증.
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
SECTION10_FIXTURE = """| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | 2026-04-29T10:15:00Z | 설계-리뷰 | DesignReviewPL P0 x 2 | 설계 | Change Plan section3 재작성 | --- |
| 2    | 2026-04-29T14:22:00Z | 구현-테스트 | 성능 mean +15 | 설계 | Change Plan section3 재작성 | RESET 구현-리뷰 |
| 3    | 2026-04-30T09:00:00Z | 보안-테스트 | SecurityTestPL P0 x 1 | 구현 | DeveloperAgent 재스폰 | --- |"""

# fix-ledger-sync.yml 의 row parsing 로직 mirror:
#   rows = lines.filter(l.startsWith('|') && !match(/^\|[\s|:-]+\|$/))
#   dataRows = rows.slice(1)
#   cells = row.split('|').slice(1, -1).map(stripCell)
#   stripCell: lstrip backtick, rstrip backtick
def strip_cell(s):
    return s.replace("`", "").strip()

rows = [
    line for line in SECTION10_FIXTURE.split("\n")
    if line.startswith("|") and not re.match(r"^\|[\s|:-]+\|$", line)
]
data_rows = rows[1:]  # header skip
events = []
for row in data_rows:
    cells = [strip_cell(c) for c in row.split("|")[1:-1]]
    if len(cells) < 6:
        continue
    if not cells[0].isdigit():
        continue
    events.append({
        "iter": int(cells[0]),
        "lane": cells[2],
        "cause": cells[4],
        "reset": cells[6] if len(cells) > 6 else "",
    })

if len(events) != 3:
    errors.append(f"fix-ledger fixture: 3 행 기대, 파싱 결과 {len(events)} 행")
else:
    if events[0]["iter"] != 1 or events[0]["lane"] != "설계-리뷰":
        errors.append(f"fix-ledger fixture row 0 mismatch: {events[0]}")
    if events[1]["reset"] != "RESET 구현-리뷰":
        errors.append(f"fix-ledger fixture row 1 RESET 마커 mismatch: {events[1]['reset']!r}")
    if events[2]["cause"] != "구현":
        errors.append(f"fix-ledger fixture row 2 cause mismatch: {events[2]['cause']!r}")

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
PY

echo ""
echo "(check-workflow-yaml: strict 모드 — yaml syntax + 핵심 regex + Python re-impl fixture)"
