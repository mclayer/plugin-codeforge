#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-389 / ADR-060 / ADR-058 — ADR sunset criteria mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Usage / exit code / semantics 상세: scripts/check-adr-sunset-criteria.sh header.
import sys, re, os
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("⚠ check-adr-sunset-criteria: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

# Modal anti-pattern dictionary v1.0 (ADR-058 §결정 8 verbatim — 4 표현 only)
MODAL_ANTI_PATTERNS = [
    "안정화되면",
    "임시",
    "한시적",
    "until further notice",
]

PERMANENT_PHRASE_RE = re.compile(r"N/A\s*[—\-—]\s*permanent policy", re.IGNORECASE)
SUNSET_SECTION_RE = re.compile(r"^##\s+해소\s*기준\s*$", re.MULTILINE)
THREE_TUPLE_TERMS = ["metric", "who", "how"]

# ADR-RESERVATION.md 는 ADR governance 레지스트리 (real ADR 아님) — 면제
# CFP-2661 D9: EXEMPT union — ADR 실 위치 archive/adr (PR #1973 이동). 구경로 docs/adr 형은 consumer 정답
#   경로라 union 보존(치환 아님). archive/adr RESERVATION 도 registry → 면제 union (scope union 과 원자).
EXEMPT_PATHS = {"docs/adr/ADR-RESERVATION.md", "archive/adr/ADR-RESERVATION.md"}

violations = []
files_checked = 0
adr_candidates = 0  # CFP-2661 D9 census: no-arg default 의 ADR 후보 수 (exempt 前, anti-vacuity floor).

paths = sys.argv[1:]
if not paths:
    # CFP-2661 D9: no-arg fallback union docs/adr ∪ archive/adr. docs/adr dead → 구판 0건 = vacuous-PASS
    #   ("0 ADR files 검증" / exit 0). registry detect_command(무인자)가 이 dead executor. CI argv 경로는 alive.
    paths = sorted(
        str(p) for d in ("docs/adr", "archive/adr") for p in Path(d).glob("ADR-*.md")
    )

for p in paths:
    path = Path(p)
    # census: exempt 前 ADR 후보 집계 (실재 ADR-*.md 만; anti-vacuity discovered floor — AC-5).
    if path.name.startswith("ADR-") and path.exists():
        adr_candidates += 1
    # CFP-2661 D9: separator 정규화 (Windows backslash → forward slash) 후 exempt 매치 — cross-platform.
    if p.replace("\\", "/") in EXEMPT_PATHS:
        continue
    if not path.exists():
        violations.append(f"{p}: file 부재")
        continue
    if not path.name.startswith("ADR-"):
        continue
    text = path.read_text(encoding="utf-8")
    files_checked += 1

    # frontmatter 추출
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        violations.append(f"{p}: frontmatter 부재")
        continue
    try:
        fm = yaml.safe_load(fm_match.group(1)) or {}
    except yaml.YAMLError as e:
        violations.append(f"{p}: frontmatter YAML 파싱 실패 ({e})")
        continue

    body = text[fm_match.end():]

    # (a) is_transitional 필드 존재
    if "is_transitional" not in fm:
        violations.append(f"{p}: frontmatter `is_transitional: true|false` 필드 미선언 (ADR-058 §결정 4 default=true 안전망 추정 — explicit declaration 요구)")
        is_transitional = True  # default
    else:
        val = fm["is_transitional"]
        if isinstance(val, bool):
            is_transitional = val
        else:
            violations.append(f"{p}: frontmatter `is_transitional` 가 boolean 아님 ({val!r})")
            is_transitional = True

    # (b) ## 해소 기준 섹션 존재
    if not SUNSET_SECTION_RE.search(body):
        violations.append(f"{p}: 본문 `## 해소 기준` 섹션 부재 (ADR-058 §결정 2)")
        continue  # 섹션 부재 시 (c)/(d) 검증 skip

    # 해소 기준 섹션 본문 추출 (다음 ## 또는 EOF 까지)
    sunset_match = re.search(
        r"^##\s+해소\s*기준\s*$(.*?)(?=^##\s|\Z)",
        body, re.MULTILINE | re.DOTALL
    )
    sunset_body = sunset_match.group(1).strip() if sunset_match else ""

    if is_transitional is False:
        # (c) is_transitional=false 시 "N/A — permanent policy" 1줄 또는 동등 형식
        if not PERMANENT_PHRASE_RE.search(sunset_body):
            violations.append(
                f"{p}: `is_transitional: false` 시 `## 해소 기준` 본문은 "
                f"\"N/A — permanent policy\" 표현 의무 (ADR-058 §결정 2)"
            )
    else:
        # (d) is_transitional=true 시 측정성 3-tuple + 모달 어휘 검사
        lower_body = sunset_body.lower()
        missing_terms = [t for t in THREE_TUPLE_TERMS if t not in lower_body]
        if missing_terms:
            violations.append(
                f"{p}: `is_transitional: true` 시 `## 해소 기준` 본문에 "
                f"측정성 3-tuple ({'/'.join(THREE_TUPLE_TERMS)}) 모두 명시 의무 "
                f"(ADR-058 §결정 3). 누락 = {missing_terms}"
            )
        for modal in MODAL_ANTI_PATTERNS:
            if modal.lower() in sunset_body.lower():
                violations.append(
                    f"{p}: `## 해소 기준` 본문에 모달 anti-pattern \"{modal}\" 매치 "
                    f"(ADR-058 §결정 3 + ADR-060 §결정 9 — modal_anti_pattern_dictionary v1.0)"
                )

# CFP-2661 D9 census (AC-5 — anti-vacuity floor). adr_candidates = 실 스캔 surface 크기 (scope=∅ 이면 0 노출).
print(
    f"check-adr-sunset-criteria: census adr_candidates={adr_candidates} files_checked={files_checked} "
    f"(candidates = discovered ADR surface, anti-vacuity floor; 구판 no-arg = 0 = vacuous-PASS)"
)
print(f"check-adr-sunset-criteria: {files_checked} ADR files 검증")
if violations:
    print(f"\n⚠ violation {len(violations)}건:", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
    sys.exit(1)
else:
    print("✓ violation 0건 — sunset criteria mechanical check PASS")
    sys.exit(0)
