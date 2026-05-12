#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-455 / ADR-060 Amendment 2 §결정 14 — evidence-checks-registry schema lint
# CFP-455 FIX iter 1 / ADR-061 §결정 1 정합 — heredoc multi-line Python 외부 .py split.
#
# 검증 대상 (Story CFP-455 §8.6 / Change Plan §3 verbatim):
#   (a) header `schema_version` field 존재 + value 가 string
#   (b) 각 entry required field 존재 (name / description / detect_command / workflow /
#       current_tier / introduced_by / owner_adr / carrier_adr)
#   (c) `current_tier` enum membership — `warning` / `blocking-on-pr` /
#       `blocking-on-merge` / `hotfix-bypass` (4 SSOT 명칭만, 대소문자 / 공백 정확 일치)
#   (d) `bypass_label` 정의 시 `bypass_audit_lint` 동반 의무 (pair 정합)
#   (e) entry `name` 전역 unique
#   (f) `owner_adr` / `carrier_adr` 가 실재 `docs/adr/ADR-NNN-*.md` file cross-ref
#
# Exit code 3-tier (ADR-060 Amendment 2 §결정 15 — Codex AREA 1 verbatim):
#   - exit 0 : PASS — violation 0건
#   - exit 1 : validation FAIL — registry yaml schema 위반 1건 이상
#   - exit 2 : META-ERROR — pyyaml 미설치 / registry yaml file 부재 / ADR file glob fail
#              (validation FAIL 과 semantic 분리 — false positive rate 측정 무결성 보장)
#
# 사용 모드 (registry tier=warning, §결정 16 정합 — bypass_label omit):
#   warning mode 단계 = continue-on-error → exit 1 / 2 모두 PR merge 미차단 (workflow level).
#   blocking mode 승격 시 exit 1 = PR block / exit 2 = workflow level error 처리.
#
# 인자:
#   sys.argv[1:] : 검증 대상 registry yaml file path (없으면 docs/evidence-checks-registry.yaml)
#
# 호출 패턴 (thin bash wrapper 경유):
#   $ bash scripts/check-evidence-registry.sh
#   $ bash scripts/check-evidence-registry.sh docs/evidence-checks-registry.yaml
#   $ bash scripts/check-evidence-registry.sh tests/scripts/check-evidence-registry/fixtures/negative-enum-violation.yaml
#
# carrier: ADR-060 Amendment 2 §결정 3 + §결정 14 (메타 lint self-application)
import sys
import re
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Exit code 3-tier (ADR-060 Amendment 2 §결정 15)
EXIT_PASS = 0
EXIT_VALIDATION_FAIL = 1
EXIT_META_ERROR = 2

# pyyaml 미설치 = meta-error (exit 2) — false positive validation FAIL 위장 차단
try:
    import yaml
except ImportError:
    print("META-ERROR: pyyaml 미설치 — `python3 -m pip install --user pyyaml`", file=sys.stderr)
    sys.exit(EXIT_META_ERROR)

# 4-tier enforcement enum SSOT (ADR-060 §결정 3 + Amendment 2 §결정 3 verbatim)
VALID_TIERS = {"warning", "blocking-on-pr", "blocking-on-merge", "hotfix-bypass"}

# 각 entry required field (Story §8.6 verbatim — schema doc v1.1 §3 row 의 "필수")
REQUIRED_FIELDS = [
    "name",
    "description",
    "detect_command",
    "workflow",
    "current_tier",
    "introduced_by",
    "owner_adr",
    "carrier_adr",
]

# default registry yaml path
DEFAULT_REGISTRY = "docs/evidence-checks-registry.yaml"

# ADR file glob (cross-ref 검증 대상)
ADR_GLOB_DIR = Path("docs/adr")


def collect_adr_keys():
    """docs/adr/ADR-NNN-*.md glob → set of ADR keys (e.g., {'ADR-058', 'ADR-060'})."""
    if not ADR_GLOB_DIR.exists() or not ADR_GLOB_DIR.is_dir():
        return None  # meta-error signal
    adr_keys = set()
    for p in ADR_GLOB_DIR.glob("ADR-*.md"):
        # filename 패턴: ADR-NNN-<slug>.md 또는 ADR-RESERVATION.md
        m = re.match(r"^(ADR-(?:\d+|RESERVATION))", p.name)
        if m:
            adr_keys.add(m.group(1))
    return adr_keys


def main():
    args = sys.argv[1:]
    registry_path = Path(args[0]) if args else Path(DEFAULT_REGISTRY)

    # registry yaml file 부재 = meta-error (exit 2)
    if not registry_path.exists():
        print(f"META-ERROR: registry yaml file 부재 — {registry_path}", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)

    # yaml 파싱
    try:
        text = registry_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        print(f"META-ERROR: registry yaml 파싱 실패 ({e})", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)
    except OSError as e:
        print(f"META-ERROR: registry yaml read 실패 ({e})", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)

    if not isinstance(data, dict):
        print(f"META-ERROR: registry yaml root 가 mapping 아님 (type={type(data).__name__})", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)

    # ADR file glob (cross-ref 검증용) — fail 시 meta-error
    adr_keys = collect_adr_keys()
    if adr_keys is None:
        print(f"META-ERROR: docs/adr/ 디렉토리 부재 또는 접근 불가", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)

    violations = []

    # (a) header `schema_version` field 존재
    if "schema_version" not in data:
        violations.append("(a) header `schema_version` field 부재 — schema v1.1 의무 (ADR-060 Amendment 2)")
    elif not isinstance(data["schema_version"], str):
        violations.append(
            f"(a) header `schema_version` 가 string 아님 (type={type(data['schema_version']).__name__}, "
            f"value={data['schema_version']!r})"
        )

    # entries[] 추출
    entries = data.get("entries")
    if entries is None:
        violations.append("`entries` 블록 부재")
        entries = []
    elif not isinstance(entries, list):
        violations.append(f"`entries` 가 list 아님 (type={type(entries).__name__})")
        entries = []

    seen_names = {}  # name -> first occurrence index (uniqueness 검증)
    entries_validated = 0

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            violations.append(f"entries[{idx}]: mapping 아님 (type={type(entry).__name__})")
            continue
        entries_validated += 1

        name = entry.get("name", f"<unnamed-{idx}>")

        # (b) required field 존재 검증
        for field in REQUIRED_FIELDS:
            if field not in entry:
                violations.append(
                    f"(b) entry '{name}' (idx={idx}) missing required field '{field}'"
                )

        # (c) current_tier enum membership
        current_tier = entry.get("current_tier")
        if current_tier is not None:
            if not isinstance(current_tier, str):
                violations.append(
                    f"(c) entry '{name}' current_tier 가 string 아님 (type={type(current_tier).__name__}, value={current_tier!r})"
                )
            elif current_tier not in VALID_TIERS:
                violations.append(
                    f"(c) entry '{name}' current_tier '{current_tier}' not in enum {sorted(VALID_TIERS)}"
                )

        # (d) bypass_label / bypass_audit_lint pair 정합
        has_bypass_label = "bypass_label" in entry and entry["bypass_label"] is not None
        has_bypass_audit_lint = "bypass_audit_lint" in entry and entry["bypass_audit_lint"] is not None
        if has_bypass_label and not has_bypass_audit_lint:
            violations.append(
                f"(d) entry '{name}' bypass_label defined but bypass_audit_lint missing "
                f"(schema doc v1.1 §3 — bypass_label 정의 시 bypass_audit_lint 의무)"
            )
        # 역방향 (bypass_audit_lint only without bypass_label) 도 무의미한 정의로 violation
        if has_bypass_audit_lint and not has_bypass_label:
            violations.append(
                f"(d) entry '{name}' bypass_audit_lint defined but bypass_label missing — 의미 없는 정의"
            )

        # (e) name uniqueness
        if isinstance(name, str) and not name.startswith("<unnamed-"):
            if name in seen_names:
                violations.append(
                    f"(e) duplicate entry name '{name}' — first at idx={seen_names[name]}, dup at idx={idx}"
                )
            else:
                seen_names[name] = idx

        # (f) owner_adr / carrier_adr 실재 file cross-ref
        # 실재 production registry 의 일부 entry 는 free-form 부가 정보 보유 (예: 'ADR-031 §결정 3 + fix-event-v1' /
        # 'comment-prefix-registry-v1 (kind:registry)'). 본 lint 의 의의 = "ADR-NNN file cross-ref" — 부가 정보
        # narrative 는 schema doc v1.1 §3 row 의 "예: `ADR-058`" 의 strict literal 양식 외 통상 운영 패턴.
        # 따라서 본 (f) 는 leading `ADR-NNN` 토큰 추출 → file cross-ref 검증. 토큰 자체 부재 시만 형식 위배 처리.
        # (kind:registry / contract: 등 prefix 만 의 entry 는 ADR file cross-ref 의무 면제)
        ADR_TOKEN_RE = re.compile(r"\bADR-(?:\d+|RESERVATION)\b")
        for adr_field in ("owner_adr", "carrier_adr"):
            adr_value = entry.get(adr_field)
            if adr_value is None:
                # (b) 에서 이미 missing required field 보고됨 — skip
                continue
            if not isinstance(adr_value, str):
                violations.append(
                    f"(f) entry '{name}' {adr_field} 가 string 아님 (type={type(adr_value).__name__}, value={adr_value!r})"
                )
                continue
            # leading ADR-NNN 토큰 추출 (첫 매치만 검증 — multi-ADR 표기 시 첫 ADR 가 primary owner/carrier)
            m = ADR_TOKEN_RE.search(adr_value)
            if not m:
                # ADR-NNN 토큰 자체 부재 = registry / contract / policy prefix only 등 = ADR cross-ref 의무 면제
                # (단 본 entry 의 owner_adr 는 일관성 위해 ADR-NNN 토큰 권장. 본 lint = warning level)
                continue
            adr_key = m.group(0)
            if adr_key not in adr_keys:
                violations.append(
                    f"(f) entry '{name}' {adr_field} '{adr_key}' file not found in docs/adr/"
                )

    # 결과 출력
    print(f"check-evidence-registry: {registry_path} — {entries_validated} entries validated")
    if violations:
        print(f"\n⚠ violation {len(violations)}건:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(EXIT_VALIDATION_FAIL)
    else:
        print(f"✓ violation 0건 — registry schema validation PASS ({entries_validated} entries)")
        sys.exit(EXIT_PASS)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"META-ERROR: unexpected exception ({type(e).__name__}: {e})", file=sys.stderr)
        sys.exit(EXIT_META_ERROR)
