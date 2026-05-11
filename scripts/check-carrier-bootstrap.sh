#!/usr/bin/env bash
# CFP-407 / ADR-062 — carrier Story bootstrap dependency mechanical lint (warning mode)
#
# 검증 대상 (ADR-062 §결정 1-2 verbatim):
#   (a) Story frontmatter `carrier_story` 존재 시 string 타입 + KEY 형식 (`<prefix>-<number>`)
#   (b) `bootstrap_exempt_protocols` 존재 시 list of string + 각 원소 `"<type>:<identifier>"` 형식
#   (c) type prefix 가 표준 5 prefix (adr|contract|policy|workflow|script) 중 하나
#   (d) carrier_story 가 자기 자신 KEY 와 동일 (= 본 Story 가 carrier) 시,
#       §3 본문에 bootstrap_exempt_protocols 의 adr:/contract: prefix 원소 모두 참조
#
# Type prefix v1.0 (5종 only — ADR-062 §결정 1):
#   - adr:       (예: adr:ADR-062)
#   - contract:  (예: contract:debate-protocol-v1)
#   - policy:    (예: policy:todowrite-progress-visualization)
#   - workflow:  (예: workflow:retro-mandatory.yml)
#   - script:    (예: script:check-carrier-bootstrap.sh)
#
# 사용 모드 (registry tier=warning):
#   - exit 0 : violation 0건 또는 warning mode (continue-on-error)
#   - exit 1 : violation 1건 이상 (workflow level conditional)
#
# 인자:
#   $@ : 검증 대상 Story file path list (없으면 docs/stories/<PREFIX>-*.md glob)
#
# 명령 라인:
#   $ bash scripts/check-carrier-bootstrap.sh docs/stories/CFP-407.md
#   $ bash scripts/check-carrier-bootstrap.sh    # all stories
#
# carrier: ADR-062 §결정 8 (self-application 첫 사례 = CFP-407 자체)
set -euo pipefail
# 인자 있을 시 호출자 cwd 기준 경로 해석.
# 인자 없을 시 codeforge repo root 로 이동 후 docs/stories/ glob.
if [ "$#" -eq 0 ]; then
    cd "$(dirname "$0")/.."
fi

python3 - "$@" <<'PY'
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
    print("⚠ check-carrier-bootstrap: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

# Type prefix v1.0 (ADR-062 §결정 1 verbatim — 5 prefix only)
VALID_TYPE_PREFIXES = {"adr", "contract", "policy", "workflow", "script"}

# Story KEY 형식: <PREFIX>-<NUMBER> (예: CFP-407, MCT-112, PLG-7)
KEY_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")

# typed key 형식: <type>:<identifier>
TYPED_KEY_RE = re.compile(r"^([a-z]+):(.+)$")

violations = []
files_checked = 0

paths = sys.argv[1:]
if not paths:
    paths = sorted(str(p) for p in Path("docs/stories").glob("*-*.md"))

for p in paths:
    path = Path(p)
    if not path.exists():
        violations.append(f"{p}: file 부재")
        continue
    text = path.read_text(encoding="utf-8")
    files_checked += 1

    # frontmatter 추출
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        # Story file frontmatter 부재 = story file 아님 (skip, not violation)
        continue
    try:
        fm = yaml.safe_load(fm_match.group(1)) or {}
    except yaml.YAMLError as e:
        violations.append(f"{p}: frontmatter YAML 파싱 실패 ({e})")
        continue

    body = text[fm_match.end():]

    carrier_story = fm.get("carrier_story")
    exempt_protocols = fm.get("bootstrap_exempt_protocols")
    own_key = fm.get("key")

    # (carrier_story 미선언 + bootstrap_exempt_protocols 미선언) = non-carrier Story → 면제
    if carrier_story is None and exempt_protocols is None:
        continue

    # carrier_story 만 선언 + bootstrap_exempt_protocols 미선언 = 누락
    if carrier_story is not None and exempt_protocols is None:
        violations.append(
            f"{p}: `carrier_story` 선언 시 `bootstrap_exempt_protocols` 필드 의무 "
            f"(ADR-062 §결정 1 — typed key list)"
        )
        continue

    # bootstrap_exempt_protocols 만 선언 + carrier_story 미선언 = 의미 모호
    if carrier_story is None and exempt_protocols is not None:
        violations.append(
            f"{p}: `bootstrap_exempt_protocols` 선언 시 `carrier_story` 필드 의무 "
            f"(ADR-062 §결정 1)"
        )
        continue

    # (a) carrier_story string + KEY 형식
    if not isinstance(carrier_story, str):
        violations.append(
            f"{p}: `carrier_story` 가 string 아님 ({carrier_story!r}) — ADR-062 §결정 1"
        )
        continue
    if not KEY_RE.match(carrier_story):
        violations.append(
            f"{p}: `carrier_story` KEY 형식 위배 ({carrier_story!r}) — `<PREFIX>-<NUMBER>` 의무 (ADR-062 §결정 1)"
        )

    # (b) bootstrap_exempt_protocols list of string
    if not isinstance(exempt_protocols, list):
        violations.append(
            f"{p}: `bootstrap_exempt_protocols` 가 list 아님 ({type(exempt_protocols).__name__}) — ADR-062 §결정 1"
        )
        continue
    if not exempt_protocols:
        violations.append(
            f"{p}: `bootstrap_exempt_protocols` empty list — carrier 선언했으나 면제 protocol 부재 (ADR-062 §결정 1)"
        )
        continue

    typed_keys = []
    for idx, elem in enumerate(exempt_protocols):
        if not isinstance(elem, str):
            violations.append(
                f"{p}: `bootstrap_exempt_protocols[{idx}]` 가 string 아님 ({elem!r}) — ADR-062 §결정 1"
            )
            continue
        m = TYPED_KEY_RE.match(elem)
        if not m:
            violations.append(
                f"{p}: `bootstrap_exempt_protocols[{idx}]` typed key 형식 위배 ({elem!r}) — "
                f"`<type>:<identifier>` 의무 (ADR-062 §결정 1)"
            )
            continue
        type_prefix, identifier = m.group(1), m.group(2)
        # (c) type prefix 표준 5 prefix
        if type_prefix not in VALID_TYPE_PREFIXES:
            violations.append(
                f"{p}: `bootstrap_exempt_protocols[{idx}]` 미정의 type prefix '{type_prefix}' "
                f"({elem!r}) — 표준 5 prefix {sorted(VALID_TYPE_PREFIXES)} (ADR-062 §결정 1)"
            )
            continue
        typed_keys.append((type_prefix, identifier))

    # (d) §3 본문 정합 — carrier_story 가 자기 자신 KEY 와 동일 시
    if own_key and carrier_story == own_key:
        # §3 본문 추출 (다음 ## §4 또는 다음 ## 까지)
        section3_match = re.search(
            r"^##\s+§3\..*?$(.*?)(?=^##\s+§4|^##\s+§|\Z)",
            body, re.MULTILINE | re.DOTALL
        )
        section3_body = section3_match.group(1) if section3_match else ""

        for type_prefix, identifier in typed_keys:
            # adr: / contract: prefix 만 §3 본문 정합 검증 (§3 = ADR 전용)
            if type_prefix in ("adr", "contract"):
                # identifier 가 §3 본문에 substring match 되는지 검사
                if identifier not in section3_body:
                    violations.append(
                        f"{p}: §3 본문에 `{type_prefix}:{identifier}` 참조 부재 "
                        f"(ADR-062 §결정 2 (b) — carrier protocol 이 §3 ADR 목록에 명시 의무)"
                    )

print(f"check-carrier-bootstrap: {files_checked} Story files 검증")
if violations:
    print(f"\n⚠ violation {len(violations)}건:", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
    sys.exit(1)
else:
    print("✓ violation 0건 — carrier bootstrap mechanical check PASS")
    sys.exit(0)
PY
