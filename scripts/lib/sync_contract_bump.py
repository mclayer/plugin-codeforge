#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-408 — Cross-repo sibling sync PR sequence 자동화
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# mode_preserve: 100755
#
# inter-plugin contract version bump 시 3단계 sync PR sequence 자동 생성:
#   1) Canonical lane plugin repo (MAJOR bump 필수 first per ADR-010 Amendment 2)
#   2) Wrapper sibling repo (mclayer/plugin-codeforge)
#   3) Marketplace mirror PR (mclayer/marketplace) — version field 변경 시
#
# Usage / exit code / semantics 상세: scripts/sync-contract-bump.sh header.
import sys, json, os, subprocess, re
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
    print("ERROR: pyyaml 미설치 (meta-error)", file=sys.stderr)
    sys.exit(2)


def lookup_contract(contract_name: str, manifest_path: str) -> dict:
    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # contracts[] = kind:contract entries (ADR-010 정합)
    for entry in data.get("contracts", []) or []:
        if entry.get("name") == contract_name or entry.get("name") == contract_name.replace("-", "_"):
            canonical_repo = entry.get("canonical_repo")
            canonical_path = entry.get("canonical_path", "docs/inter-plugin-contracts/")
            if not canonical_repo:
                print(f"ERROR: contract {contract_name} canonical_repo null (wrapper-canonical?)", file=sys.stderr)
                sys.exit(3)
            files = entry.get("files", [])
            active_file = None
            for fent in files:
                if fent.get("status") == "Active":
                    active_file = fent.get("file")
                    break
            return {
                "name": entry["name"],
                "canonical_repo": canonical_repo,
                "canonical_path": canonical_path,
                "active_file": active_file,
                "kind": "contract",
            }
    # Not in contracts[] — check registries[] (kind:registry — out of scope)
    for entry in data.get("registries", []) or []:
        if entry.get("name") == contract_name or entry.get("name") == contract_name.replace("-", "_"):
            print(f"ERROR: '{contract_name}' is kind:registry — sync-contract-bump.sh applies to kind:contract only (ADR-010 §결정 3)", file=sys.stderr)
            sys.exit(3)
    # Also check by file prefix
    for entry in (data.get("contracts") or []) + (data.get("registries") or []):
        for fent in entry.get("files", []):
            fname = fent.get("file", "")
            if fname.startswith(f"{contract_name}-"):
                kind = "contract" if entry in (data.get("contracts") or []) else "registry"
                if kind == "registry":
                    print(f"ERROR: '{contract_name}' matches kind:registry file — sync-contract-bump.sh applies to kind:contract only", file=sys.stderr)
                    sys.exit(3)
    print(f"ERROR: contract '{contract_name}' MANIFEST.yaml 미등록", file=sys.stderr)
    sys.exit(3)


if __name__ == "__main__":
    # This module is invoked by sync-contract-bump.sh via python3 - <contract> <manifest>
    # Print JSON result to stdout
    if len(sys.argv) >= 3:
        contract_name = sys.argv[1]
        manifest_path = sys.argv[2]
        result = lookup_contract(contract_name, manifest_path)
        print(json.dumps(result))
        sys.exit(0)
    else:
        print("Usage: sync_contract_bump.py <contract-name> <manifest-path>", file=sys.stderr)
        sys.exit(2)
