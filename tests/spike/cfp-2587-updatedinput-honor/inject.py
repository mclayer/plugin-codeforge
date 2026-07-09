#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2587 feasibility spike — PreToolUse updatedInput honor probe (Gate-A / Gate-B).
#
# THIS IS A SPIKE INSTRUMENT, not the production hook. It deliberately rewrites the
# observable `command` field (Bash) / `prompt` field (Agent) so that whether the
# harness HONORS updatedInput is a *binary, unambiguous* signal in the child
# session's tool output — the cleanest possible falsification of #15897
# ("updatedInput dropped when multiple PreToolUse hooks execute"). The production
# hook only rewrites `description`; here `description` is ALSO prefixed in the same
# updatedInput dict to demonstrate the real target field rides along identically.
#
# Variants (env SPIKE_VARIANT):
#   fullecho_bare  — updatedInput = full echo of tool_input, command/prompt rewritten
#                    to observable sentinel + description prefixed; NO permissionDecision
#                    (== the production G4 bare-updatedInput design).
#   fullecho_allow — same, plus permissionDecision:"allow".
#   baredesc_bare  — updatedInput = {"description": prefixed} ONLY (no command/prompt).
#                    REPLACE-vs-MERGE probe: under REPLACE the command is lost.
#
# Every payload is appended (raw) to $SPIKE_LOG for real-shape fixture capture.
import json
import os
import sys

VARIANT = os.environ.get("SPIKE_VARIANT", "fullecho_bare")
NONCE = os.environ.get("SPIKE_NONCE", "NONCE")
LOG = os.environ.get("SPIKE_LOG", "")
STAMP = os.environ.get("SPIKE_STAMP", "07/09 19:30")


def _log(obj):
    if not LOG:
        return
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    try:
        payload = json.loads(raw)
    except Exception:
        _log({"parse_error": raw[:200]})
        return 0

    _log({"phase": "payload", "keys": sorted(payload.keys()),
          "tool_name": payload.get("tool_name"),
          "agent_type": payload.get("agent_type"),
          "agent_id": payload.get("agent_id"),
          "tool_input_keys": sorted((payload.get("tool_input") or {}).keys()),
          "raw": payload})

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return 0

    orig_desc = tool_input.get("description", "") or ""
    subject = payload.get("agent_type") or tool_input.get("subagent_type") or "SpikeAgent"
    # namespace strip (my-plugin:reviewer -> reviewer)
    if ":" in subject:
        subject = subject.split(":")[-1]
    prefixed_desc = "[%s] %s - %s" % (subject, STAMP, orig_desc or "spike")

    updated = None
    if tool_name == "Bash":
        if VARIANT == "baredesc_bare":
            updated = {"description": prefixed_desc}
        else:
            updated = dict(tool_input)
            updated["description"] = prefixed_desc
            # observable rewrite: sentinel proves honor
            updated["command"] = "echo SPIKE_INJECTED_%s" % NONCE
    elif tool_name in ("Agent", "Task"):
        if VARIANT == "baredesc_bare":
            updated = {"description": prefixed_desc}
        else:
            updated = dict(tool_input)
            updated["description"] = prefixed_desc
            # observable rewrite of prompt so subagent echoes sentinel
            updated["prompt"] = ("Reply with exactly this token and nothing else: "
                                 "SPIKE_INJECTED_%s" % NONCE)
    else:
        return 0

    hso = {"hookEventName": "PreToolUse", "updatedInput": updated}
    if VARIANT == "fullecho_allow":
        hso["permissionDecision"] = "allow"
    out = {"hookSpecificOutput": hso}
    _log({"phase": "emit", "variant": VARIANT, "emitted": out})
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    sys.stderr.write("[spike-inject] variant=%s tool=%s honored-signal-pending\n"
                     % (VARIANT, tool_name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
