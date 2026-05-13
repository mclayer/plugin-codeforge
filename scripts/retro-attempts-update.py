#!/usr/bin/env python3
"""retro-attempts.jsonl 업데이트 스크립트 (CFP-138 / ADR-045 §D-4 Phase 2)
ADR-061 §결정 1 — multi-line Python script 외부 파일 분리.

env vars (required):
  _SK  — story_key to update
  _NS  — new status
  _TS  — timestamp (ISO8601)
  _NA  — new attempt_n (0 = skip update)

input:  /tmp/retro-state/current.jsonl
output: updated JSONL text to stdout
"""
import json
import os

sk = os.environ["_SK"]
ns = os.environ["_NS"]
ts = os.environ["_TS"]
na = int(os.environ["_NA"])

updated = []
try:
    with open("/tmp/retro-state/current.jsonl") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d.get("story_key") == sk:
                d["status"] = ns
                d["last_attempted_at"] = ts
                if na > 0:
                    d["attempt_n"] = na
            updated.append(json.dumps(d))
except FileNotFoundError:
    pass

print("\n".join(updated) + "\n")
