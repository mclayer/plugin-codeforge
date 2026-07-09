#!/usr/bin/env bash
# CFP-2587 feasibility spike reproduction runner (Gate-A / Gate-B).
# Runs claude -p with the spike injection hook added to the real production hook
# topology and prints, per run, whether updatedInput was HONORED (executed the
# rewritten sentinel) or DROPPED (executed the model's original command).
#
# Prereqs: claude CLI on PATH; codeforge plugin enabled (supplies the 3 real
# PreToolUse(Bash) siblings so the topology is a genuine multi-hook set); python on PATH.
set -uo pipefail
cd "$(dirname "$0")"
STAMP="$(date -u -d '+9 hours' '+%m/%d %H:%M' 2>/dev/null || echo '01/01 00:00')"

signal() {  # $1=jsonl
  PYTHONIOENCODING=utf-8 python - "$1" <<'PY'
import json,sys
lines=[json.loads(l) for l in open(sys.argv[1],encoding="utf-8") if l.strip()]
pre=[e for e in lines if e.get("type")=="system" and e.get("subtype")=="hook_started" and e.get("hook_event")=="PreToolUse"]
req=res=None
for e in lines:
    if e.get("type")=="assistant":
        for b in e.get("message",{}).get("content",[]):
            if isinstance(b,dict) and b.get("type")=="tool_use" and b.get("name") in ("Bash","Agent"):
                req=(b.get("input") or {}).get("command") or (b.get("input") or {}).get("prompt")
    if e.get("type")=="user":
        for b in e.get("message",{}).get("content",[]):
            if isinstance(b,dict) and b.get("type")=="tool_result":
                c=b.get("content")
                if isinstance(c,list): c="".join(x.get("text","") for x in c if isinstance(x,dict))
                res=c
print(f"  PreToolUse hooks fired={len(pre)}  requested={req!r}  EXECUTED={str(res)[:90]!r}")
PY
}

run_bash() {  # $1=variant $2=nonce $3=settings
  export SPIKE_VARIANT="$1" SPIKE_NONCE="$2" SPIKE_STAMP="$STAMP" SPIKE_LOG="$PWD/.payload-$2.log"
  rm -f "$SPIKE_LOG"
  timeout 240 claude -p "Run this exact Bash command once then stop, nothing else: echo SPIKE_ORIGINAL_$2" \
    --settings "$3" --dangerously-skip-permissions \
    --output-format stream-json --verbose --include-hook-events > ".out-$2.jsonl" 2>/dev/null
  echo "[$1/$2]"; signal ".out-$2.jsonl"; rm -f ".out-$2.jsonl" "$SPIKE_LOG"
}

echo "== Gate-A (Bash, production 4-hook topology) =="
run_bash fullecho_bare  GA_BARE  settings.gate-a.json
run_bash fullecho_allow GA_ALLOW settings.gate-a.json
run_bash baredesc_bare  GA_REPL  settings.gate-a.json
echo "== Gate-B (Agent) — spawn a subagent manually to exercise, see RESULTS.md =="
echo "   (Agent-surface run needs a Task-spawning prompt; see RESULTS.md GATEB01/LEAF01)"
