#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-894 / ADR-060 §결정 6 — inter-plugin-contract MANIFEST↔frontmatter parity lint
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Scope (Phase 1, wrapper-local):
#   INV-1: docs/inter-plugin-contracts/MANIFEST.yaml `contract_version` row ↔
#          docs/inter-plugin-contracts/<file>.md frontmatter `contract_version` byte-identical 검증
#
# Out-of-scope (Phase 2 deferred):
#   - body `## N. payload` schema 안 contract_version literal parity (per-contract heterogeneity —
#     section enumeration in MANIFEST 필요, separate carrier CFP)
#   - cross-repo canonical frontmatter parity (CODEFORGE_CROSS_REPO_PAT 의존, ADR-066)
#
# Detection target: 7 kind:contract entries (review_verdict / requirements_output / design_output /
#                   develop_output / test_verdict / pmo_output / git_ops_event) + any future addition.
# kind:registry entries (label-registry-v2, debate-protocol-v1 등) = ADR-010 §결정 2 sibling sync
#                   면제 — 자체적으로 wrapper canonical, parity 대상 외.
#
# Self-ref graceful (CFP-702/744 교훈): MANIFEST.yaml 부재 시 sys.exit(0).
#
# Usage / exit code:
#   bash scripts/check-inter-plugin-contracts-parity.sh
#   exit 0 = PASS (모든 MANIFEST row ↔ frontmatter contract_version 일치)
#   exit 1 = FAIL (1개 이상 parity drift 감지) — warning tier per ADR-060 §결정 5
#   exit 2 = configuration error (MANIFEST parse 실패 등)
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

try:
    import yaml
except ImportError:
    sys.stderr.write("⚠ check-inter-plugin-contracts-parity: pyyaml 미설치 — skip\n")
    sys.exit(0)

CONTRACTS_DIR = Path("docs/inter-plugin-contracts")
MANIFEST_PATH = CONTRACTS_DIR / "MANIFEST.yaml"


def _parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content.

    Returns parsed frontmatter dict, or {} if absent/unparseable.
    """
    if not content.startswith("---\n"):
        return {}
    try:
        end_idx = content.index("\n---\n", 4)
    except ValueError:
        return {}
    fm_text = content[4:end_idx]
    try:
        parsed = yaml.safe_load(fm_text)
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}


def _normalize_version(v) -> str:
    """Normalize contract_version to string for comparison.

    yaml.safe_load may return string (quoted) or float (unquoted "1.1" → 1.1).
    """
    if v is None:
        return ""
    return str(v).strip()


def check_parity() -> int:
    """Run INV-1 parity check.

    Returns exit code: 0=PASS, 1=FAIL, 2=config error.
    """
    if not CONTRACTS_DIR.exists():
        sys.stderr.write(
            "[inter-plugin-contracts-parity] SKIP: docs/inter-plugin-contracts/ 부재 — "
            "self-ref graceful (continue-on-error)\n"
        )
        return 0

    if not MANIFEST_PATH.exists():
        sys.stderr.write(
            f"[inter-plugin-contracts-parity] SKIP: {MANIFEST_PATH} 부재 — "
            "self-ref graceful\n"
        )
        return 0

    try:
        manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        sys.stderr.write(f"[inter-plugin-contracts-parity] FAIL: MANIFEST.yaml parse 실패: {e}\n")
        return 2

    if not isinstance(manifest, dict):
        sys.stderr.write("[inter-plugin-contracts-parity] FAIL: MANIFEST root not a mapping\n")
        return 2

    contracts = manifest.get("contracts", [])
    if not isinstance(contracts, list):
        sys.stderr.write("[inter-plugin-contracts-parity] FAIL: MANIFEST.contracts not a list\n")
        return 2

    violations = []
    checked_count = 0

    for entry in contracts:
        if not isinstance(entry, dict):
            continue
        contract_name = entry.get("name", "<unnamed>")
        files = entry.get("files", [])
        if not isinstance(files, list):
            continue

        for fent in files:
            if not isinstance(fent, dict):
                continue
            fname = fent.get("file")
            manifest_version = _normalize_version(fent.get("contract_version"))
            status = fent.get("status", "")

            # Only verify Active contracts (Archived = historical, not parity-checked)
            if status != "Active":
                continue
            if not fname:
                continue

            file_path = CONTRACTS_DIR / fname
            if not file_path.exists():
                # MANIFEST completeness is check_inter_plugin_contracts.py's job — not here.
                # We can't parity-check what's missing. Skip silently (separation of concerns).
                continue

            checked_count += 1

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                violations.append(
                    f"{contract_name}/{fname}: 파일 읽기 실패 — {e}"
                )
                continue

            fm = _parse_frontmatter(content)
            frontmatter_version = _normalize_version(fm.get("contract_version"))

            if not frontmatter_version:
                violations.append(
                    f"{contract_name}/{fname}: frontmatter contract_version 필드 부재 — "
                    f"MANIFEST=`{manifest_version}` vs frontmatter=<absent>"
                )
                continue

            if manifest_version != frontmatter_version:
                violations.append(
                    f"{contract_name}/{fname}: INV-1 parity drift — "
                    f"MANIFEST=`{manifest_version}` ↔ frontmatter=`{frontmatter_version}` "
                    f"(2-touchpoint MUST byte-identical for Active contracts)"
                )

    if violations:
        sys.stderr.write(
            f"[inter-plugin-contracts-parity] FAIL: {len(violations)} INV-1 parity drift 감지 "
            f"({checked_count} Active contract file checked):\n"
        )
        for v in violations:
            sys.stderr.write(f"  • {v}\n")
        sys.stderr.write(
            "  CFP-834 §11.4 INV-1 carrier — MANIFEST row ↔ wrapper sibling frontmatter parity invariant\n"
            "  (warning mode — ADR-060 §결정 5 / CFP-894 carrier)\n"
            "  Bypass: hotfix-bypass:inter-plugin-contracts-parity label + PR description ### Bypass reason\n"
        )
        return 1

    sys.stdout.write(
        f"[inter-plugin-contracts-parity] PASS: INV-1 parity OK "
        f"({checked_count} Active contract file checked)\n"
    )
    return 0


def main() -> int:
    return check_parity()


if __name__ == "__main__":
    sys.exit(main())
