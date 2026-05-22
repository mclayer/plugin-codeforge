#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-894 / ADR-060 §결정 6 — inter-plugin-contract MANIFEST↔frontmatter parity lint
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
# CFP-1242 / ADR-065 Amendment 4 — INV-1 parity scope expansion to kind:registry
#
# Scope (wrapper-local):
#   INV-1: docs/inter-plugin-contracts/MANIFEST.yaml Active row ↔
#          docs/inter-plugin-contracts/<file>.md frontmatter version 일치 검증.
#          BOTH MANIFEST sections are now covered:
#            (a) kind:contract → `contracts` section, field name = `contract_version`
#            (b) kind:registry → `registries` section, field name = `version`
#          frontmatter field is read per-section (contracts use `contract_version`,
#          registries use `version`). Membership semantic: a file's frontmatter version
#          MUST appear among the file's Active MANIFEST row version(s) — multiple Active
#          rows (parallel-session append) are tolerated as long as the frontmatter is one
#          of them. Non-Active rows (Archived / Sunsetted / Deprecated) are skipped.
#
#   IMPORTANT (CFP-1242 corrected diagnosis): sibling-sync exemption (ADR-010 §결정 2,
#   kind:registry) is ORTHOGONAL to MANIFEST↔frontmatter parity. The prior exclusion of
#   `registries` from this lint conflated the two: registries are exempt from CROSS-REPO
#   sibling sync, but their MANIFEST row ↔ wrapper-local frontmatter parity is still an
#   invariant. The earlier code iterated ONLY manifest["contracts"], leaving registries
#   version parity unguarded — that iteration gap (NOT a "MANIFEST excludes kind:registry"
#   policy) let label_registry accumulate 7 mis-ordered Active rows that drifted past S4.
#
# Out-of-scope (Phase 2 deferred):
#   - body `## N. payload` schema 안 version literal parity (per-entry heterogeneity —
#     section enumeration in MANIFEST 필요, separate carrier CFP)
#   - cross-repo canonical frontmatter parity (CODEFORGE_CROSS_REPO_PAT 의존, ADR-066)
#
# Detection target:
#   - 7 kind:contract entries (review_verdict / requirements_output / design_output /
#     develop_output / test_verdict / pmo_output / git_ops_event) + any future addition.
#   - 9 kind:registry entries (label_registry / debate_protocol / evidence_check_registry /
#     severity_propagation / parallel_dispatch_protocol / defense_in_depth_sublayer_registry /
#     reconcile_protocol / imperative_walker_protocol / operational_signal) + any future addition.
#
# Self-ref graceful (CFP-702/744 교훈): MANIFEST.yaml 부재 시 sys.exit(0).
#
# Usage / exit code:
#   bash scripts/check-inter-plugin-contracts-parity.sh
#   exit 0 = PASS (모든 Active MANIFEST row ↔ frontmatter version 일치 — contracts + registries)
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
    """Normalize version to string for comparison.

    yaml.safe_load may return string (quoted) or float (unquoted "1.1" → 1.1).
    """
    if v is None:
        return ""
    return str(v).strip()


# (section_key, manifest_version_field, frontmatter_version_field, label)
# CFP-1242: registries section + `version` field added — INV-1 parity scope expansion.
_SECTION_SPECS = [
    ("contracts", "contract_version", "contract_version", "contract"),
    ("registries", "version", "version", "registry"),
]


def _check_section(
    manifest: dict,
    section_key: str,
    manifest_version_field: str,
    frontmatter_version_field: str,
    kind_label: str,
    violations: list,
) -> int:
    """Check INV-1 parity for one MANIFEST section.

    Active MANIFEST rows are grouped per file; the file's frontmatter version MUST be a
    MEMBER of that file's set of Active row versions (tolerates multiple Active rows from
    parallel-session append). Returns the count of Active files parity-checked.

    Appends drift descriptions to `violations`. Returns 0 if section absent (graceful).
    """
    section = manifest.get(section_key, [])
    if not isinstance(section, list):
        violations.append(f"MANIFEST.{section_key} not a list (config error)")
        return 0

    # entry_name + file → set of Active manifest versions (membership target)
    active_versions: dict = {}  # (entry_name, fname) -> set[str]
    for entry in section:
        if not isinstance(entry, dict):
            continue
        entry_name = entry.get("name", "<unnamed>")
        files = entry.get("files", [])
        if not isinstance(files, list):
            continue
        for fent in files:
            if not isinstance(fent, dict):
                continue
            fname = fent.get("file")
            status = fent.get("status", "")
            # Only verify Active rows (Archived / Sunsetted / Deprecated = historical)
            if status != "Active":
                continue
            if not fname:
                continue
            mver = _normalize_version(fent.get(manifest_version_field))
            active_versions.setdefault((entry_name, fname), set()).add(mver)

    checked = 0
    for (entry_name, fname), mvers in active_versions.items():
        file_path = CONTRACTS_DIR / fname
        if not file_path.exists():
            # MANIFEST completeness is check_inter_plugin_contracts.py's job — not here.
            continue

        checked += 1

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            violations.append(f"[{kind_label}] {entry_name}/{fname}: 파일 읽기 실패 — {e}")
            continue

        fm = _parse_frontmatter(content)
        fver = _normalize_version(fm.get(frontmatter_version_field))

        if not fver:
            mvers_str = ", ".join(sorted(mvers))
            violations.append(
                f"[{kind_label}] {entry_name}/{fname}: frontmatter "
                f"{frontmatter_version_field} 필드 부재 — "
                f"MANIFEST Active=`{mvers_str}` vs frontmatter=<absent>"
            )
            continue

        if fver not in mvers:
            mvers_str = ", ".join(sorted(mvers))
            violations.append(
                f"[{kind_label}] {entry_name}/{fname}: INV-1 parity drift — "
                f"frontmatter=`{fver}` ∉ MANIFEST Active 행 {{`{mvers_str}`}} "
                f"(frontmatter version MUST be a member of Active MANIFEST rows)"
            )

    return checked


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

    # Config-error guard: top-level sections, if present, MUST be lists.
    for section_key, *_ in _SECTION_SPECS:
        sec = manifest.get(section_key)
        if sec is not None and not isinstance(sec, list):
            sys.stderr.write(
                f"[inter-plugin-contracts-parity] FAIL: MANIFEST.{section_key} not a list\n"
            )
            return 2

    violations: list = []
    checked_count = 0

    # CFP-1242: iterate BOTH contracts (contract_version) AND registries (version).
    for section_key, mver_field, fm_field, kind_label in _SECTION_SPECS:
        checked_count += _check_section(
            manifest, section_key, mver_field, fm_field, kind_label, violations
        )

    if violations:
        sys.stderr.write(
            f"[inter-plugin-contracts-parity] FAIL: {len(violations)} INV-1 parity drift 감지 "
            f"({checked_count} Active file checked — contracts + registries):\n"
        )
        for v in violations:
            sys.stderr.write(f"  • {v}\n")
        sys.stderr.write(
            "  CFP-834 §11.4 INV-1 carrier — MANIFEST row ↔ wrapper sibling frontmatter parity invariant\n"
            "  CFP-1242 / ADR-065 Amendment 4 — kind:registry (`registries` section) now guarded\n"
            "  (warning mode — ADR-060 §결정 5 / CFP-894 carrier)\n"
            "  Bypass: hotfix-bypass:inter-plugin-contracts-parity label + PR description ### Bypass reason\n"
        )
        return 1

    sys.stdout.write(
        f"[inter-plugin-contracts-parity] PASS: INV-1 parity OK "
        f"({checked_count} Active file checked — contracts + registries)\n"
    )
    return 0


def main() -> int:
    return check_parity()


if __name__ == "__main__":
    sys.exit(main())
