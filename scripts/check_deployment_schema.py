#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_deployment_schema.py - consumer overlay deploy.* schema validation
CFP-1059-S5: declarative seed (Story-1 T16) -> actual mechanical lint wire

exit codes (ADR-060 §결정 15 — 3-tier):
  0 = PASS (or opt-in skip: deploy block / file absent)
  1 = FAIL (schema violation — deploy block present but invalid)
  2 = lint-internal-error (yaml.YAMLError / unexpected exception — fail-loud, ADR-089)

Security invariant (§7 SecurityArch, change-plan §7.1):
  - Secret env-name 검증만 (env-name string 정의 여부)
  - Secret VALUE dereference 0 (os.environ 접근 금지)
  - Finding message = sub-field name + missing child name only (value verbatim echo 금지)

ADR refs:
  ADR-061: external .py mandatory (multi-line Python > 5줄)
  ADR-070: yaml.safe_load (grep heuristic 금지, #881 lesson)
  ADR-089: fail-loud on parse error (silent fallback 차단)
  ADR-060: exit code 3-tier
  ADR-068 I-5: port 22 = SSH standard (empirical exemption — numeric default documented below)

Schema SSOT: docs/project-config-schema.md L362-L391 (deploy.* 5 sub-field)
"""

from __future__ import annotations

import sys
from typing import Any


def _fail(message: str) -> None:
    """Print a FAIL finding. Message = field/child name only (no values)."""
    print(f"[FAIL] {message}", file=sys.stderr)


def _warn(message: str) -> None:
    """Print a WARNING (not a hard FAIL). exit 0 but warning emitted."""
    print(f"[WARNING] {message}")


def _info(message: str) -> None:
    """Print informational message."""
    print(f"[INFO] {message}")


def validate_host_mapping(hm: Any, findings: list[str]) -> None:
    """
    host_mapping: array of {host: str, containers: [str]}
    §3.2 rule: array + each element dict + 'host' str + 'containers' list
    """
    if not isinstance(hm, list):
        findings.append("host_mapping must be a list (array)")
        return
    if len(hm) == 0:
        findings.append("host_mapping must have at least one entry")
        return
    for idx, entry in enumerate(hm):
        if not isinstance(entry, dict):
            findings.append(f"host_mapping[{idx}] must be a mapping (dict)")
            continue
        if "host" not in entry or not isinstance(entry["host"], str):
            findings.append(f"host_mapping[{idx}].host must be a string")
        if "containers" not in entry or not isinstance(entry["containers"], list):
            findings.append(f"host_mapping[{idx}].containers must be a list")


def validate_docker_hub(dh: Any, findings: list[str]) -> None:
    """
    docker_hub: {org: str, image_prefix: str, auth_secret_env: str}
    §3.2 rule: dict + 3 required str children
    Security: auth_secret_env = env-name only (value dereference 0)
    """
    if not isinstance(dh, dict):
        findings.append("docker_hub must be a mapping (dict)")
        return
    for child in ("org", "image_prefix", "auth_secret_env"):
        if child not in dh:
            findings.append(f"docker_hub.{child} is required")
        elif not isinstance(dh[child], str):
            findings.append(f"docker_hub.{child} must be a string")


def validate_traefik(tr: Any, findings: list[str]) -> None:
    """
    traefik: {enabled: bool, network: str, domain_pattern: str}
    §3.2 rule: dict + enabled bool strict (string "true" is FAIL) + 2 str children
    ADR-068 I-1 unconditional guard: isinstance(v, bool) — Python "true" str != bool
    """
    if not isinstance(tr, dict):
        findings.append("traefik must be a mapping (dict)")
        return
    if "enabled" not in tr:
        findings.append("traefik.enabled is required")
    else:
        enabled = tr["enabled"]
        # Strict bool check: Python yaml.safe_load parses true → True (bool), "true" → str
        if not isinstance(enabled, bool):
            findings.append(
                f"traefik.enabled must be a boolean (true/false), got {type(enabled).__name__}"
            )
        elif not enabled:
            _info("traefik.enabled=false - manual orchestration override path (informational)")
    for child in ("network", "domain_pattern"):
        if child not in tr:
            findings.append(f"traefik.{child} is required")
        elif not isinstance(tr[child], str):
            findings.append(f"traefik.{child} must be a string")


def validate_1password(op: Any, findings: list[str], has_production_marker: bool) -> None:
    """
    1password: {enabled: bool, connect_host_env: str, connect_token_env: str, vault: str}
    §3.2 rule: dict + enabled bool + 3 env-name str children
    §7.1 security: env-name검증만 (connect_token_env value는 dereference 0)
    TC-5: enabled=false + production marker → warning (not FAIL)
    """
    if not isinstance(op, dict):
        findings.append("1password must be a mapping (dict)")
        return
    if "enabled" not in op:
        findings.append("1password.enabled is required")
    else:
        enabled = op["enabled"]
        if not isinstance(enabled, bool):
            findings.append(
                f"1password.enabled must be a boolean (true/false), got {type(enabled).__name__}"
            )
        elif not enabled:
            if has_production_marker:
                _warn(
                    "1password.enabled=false with production marker detected - "
                    "less-secure .env fallback in production (consider enabling 1Password)"
                )
            else:
                _warn("1password.enabled=false - less-secure .env fallback path")
    # Validate env-name strings only (value dereference 0 — §7.1 security invariant)
    for child in ("connect_host_env", "connect_token_env", "vault"):
        if child not in op:
            findings.append(f"1password.{child} is required")
        elif not isinstance(op[child], str):
            findings.append(f"1password.{child} must be a string")


def validate_ssh_targets(st: Any, findings: list[str]) -> None:
    """
    ssh_targets: array of {host: str, user: str, key_secret_env: str, port: int (default 22)}
    §3.2 rule: array + each element dict + 3 required str + port int (default 22 허용)
    §7.1 security: key_secret_env = env-name only (value dereference 0)
    ADR-068 I-5: port 22 = SSH standard RFC 4251 — numeric default empirical exemption
    """
    if not isinstance(st, list):
        findings.append("ssh_targets must be a list (array)")
        return
    if len(st) == 0:
        findings.append("ssh_targets must have at least one entry")
        return
    for idx, entry in enumerate(st):
        if not isinstance(entry, dict):
            findings.append(f"ssh_targets[{idx}] must be a mapping (dict)")
            continue
        for child in ("host", "user", "key_secret_env"):
            if child not in entry:
                findings.append(f"ssh_targets[{idx}].{child} is required")
            elif not isinstance(entry[child], str):
                findings.append(f"ssh_targets[{idx}].{child} must be a string")
        # port is optional (default 22 = SSH standard, RFC 4251); if present must be int
        if "port" in entry and not isinstance(entry["port"], int):
            findings.append(
                f"ssh_targets[{idx}].port must be an integer (default 22)"
            )


def validate_deploy_block(cfg: dict[str, Any]) -> list[str]:
    """
    Validate all 5 sub-fields of deploy block.
    Returns list of FAIL finding messages (empty = PASS).
    """
    findings: list[str] = []

    REQUIRED_SUBFIELDS = ("host_mapping", "docker_hub", "traefik", "1password", "ssh_targets")
    for field in REQUIRED_SUBFIELDS:
        if field not in cfg:
            findings.append(f"deploy.{field} is required but missing")

    # Detect production marker for 1password warning (TC-5)
    # project-level environment field (not in deploy block itself)
    # Note: this is passed in from caller context
    has_production_marker = cfg.get("_has_production_marker", False)

    if "host_mapping" in cfg:
        validate_host_mapping(cfg["host_mapping"], findings)
    if "docker_hub" in cfg:
        validate_docker_hub(cfg["docker_hub"], findings)
    if "traefik" in cfg:
        validate_traefik(cfg["traefik"], findings)
    if "1password" in cfg:
        validate_1password(cfg["1password"], findings, has_production_marker)
    if "ssh_targets" in cfg:
        validate_ssh_targets(cfg["ssh_targets"], findings)

    return findings


def main(project_yaml_path: str) -> int:
    """
    Main entry point.
    Returns exit code: 0 (PASS/skip) / 1 (FAIL) / 2 (lint-internal-error)
    """
    # Step 1: Load YAML — fail-loud on parse error (ADR-089 원칙 4)
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        print("[lint-internal-error] PyYAML not installed", file=sys.stderr)
        return 2

    try:
        with open(project_yaml_path, encoding="utf-8") as fh:
            parsed = yaml.safe_load(fh)
    except (FileNotFoundError, OSError):
        # Overlay absent = opt-in PASS (deploy block not configured)
        _info("Overlay file absent - skipping (opt-in PASS)")
        return 0
    except yaml.YAMLError as exc:
        # Fail-loud: malformed YAML = lint-internal-error
        print(f"[lint-internal-error] yaml.YAMLError: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"[lint-internal-error] Unexpected error reading file: {exc}", file=sys.stderr)
        return 2

    # Step 2: Extract deploy block — absent = opt-in PASS
    if not isinstance(parsed, dict):
        _info("project.yaml parsed as non-dict — skipping (opt-in PASS)")
        return 0

    deploy_cfg = parsed.get("deploy")
    if deploy_cfg is None:
        _info("deploy block absent - skipping (opt-in PASS, Story-1 fallback semantic)")
        return 0

    if not isinstance(deploy_cfg, dict):
        _fail("deploy must be a mapping (dict)")
        return 1

    # Step 3: Detect production marker (project-level environment field)
    has_production_marker = False
    project_block = parsed.get("project", {})
    if isinstance(project_block, dict):
        env_val = project_block.get("environment", "")
        if isinstance(env_val, str) and "prod" in env_val.lower():
            has_production_marker = True
    # Also check top-level environment key
    top_env = parsed.get("environment", "")
    if isinstance(top_env, str) and "prod" in top_env.lower():
        has_production_marker = True

    # Inject marker into cfg for sub-validator (no mutation of source data)
    deploy_cfg_with_marker = dict(deploy_cfg)
    deploy_cfg_with_marker["_has_production_marker"] = has_production_marker

    # Step 4: Validate deploy block
    findings = validate_deploy_block(deploy_cfg_with_marker)

    if findings:
        for finding in findings:
            _fail(finding)
        return 1

    print("[PASS] deploy.* schema validation passed")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <project.yaml>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
