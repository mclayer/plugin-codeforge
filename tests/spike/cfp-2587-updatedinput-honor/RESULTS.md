# CFP-2587 feasibility spike — RESULTS (Gate-A / Gate-B)

**Verdict: Gate-A = GO · Gate-B = GO.** `updatedInput` is honored under the production
multi-hook Bash topology on Claude Code CLI **2.1.204** (Windows 11). #15897's
`updatedInput`-drop-under-multiple-hooks did **NOT** reproduce in this environment/version.

This is a **topology-measurement** gate (AC-21), not a version claim: the reproduction
replicates the real production 4-hook `PreToolUse(Bash)` topology and falsifies the
`updatedInput` drop failure-mode. Because #15897 is *closed-as-not-planned* (no upstream
fix, not version-bounded), GO is **conditional on fail-open remaining the safety net**:
worst-case (a future regression that drops `updatedInput`) = clean prefix loss = original
`description` = ADR-143 advisory ceiling = ratchet-up, never wrong-value substitution.

## How measured

`inject.py` is a **spike instrument** (not the production hook). It deliberately rewrites
the *observable* `command` (Bash) / `prompt` (Agent) field so "was `updatedInput` honored?"
is a binary signal in the child session's **tool_result** (ground truth of execution),
while ALSO prefixing `description` in the same `updatedInput` dict to show the real target
field rides along identically. Run via `run.sh` (`claude -p ... --settings ... --output-format
stream-json --include-hook-events`), from inside the plugin repo so the 3 real codeforge
`PreToolUse(Bash)` siblings (`cross-repo-gh-safety`, `repo-confinement`,
`git-branch-delete-merge-gate`) fire for real → genuine production 4-hook topology.

## Runs & findings

| run | topology | variant | model requested | EXECUTED (tool_result) | finding |
|---|---|---|---|---|---|
| GATEA001 | 4 × PreToolUse:Bash (3 real siblings + injection) | fullecho, **bare** (no permissionDecision) | `echo SPIKE_ORIGINAL` | `SPIKE_INJECTED` | **HONORED** — Gate-A GO; #15897 not reproduced |
| ALLOW01 | 4 × PreToolUse:Bash | fullecho + `permissionDecision:"allow"` | `echo SPIKE_ORIGINAL` | `SPIKE_INJECTED` | HONORED — allow also works |
| BARE01 | 4 × PreToolUse:Bash | `{"description":...}` ONLY (no command) | `echo SPIKE_ORIGINAL` | **schema-validation FAILURE: "required parameter `command` is missing"** | **REPLACE semantics confirmed → whole-echo MANDATORY (T-1)**; a partial `updatedInput` HARD-FAILS the tool (not fail-open) |
| GATEB01 | 2 × PreToolUse:Agent (plugin agent-gate + injection) | fullecho, bare | subagent prompt `Please reply HELLO` | subagent replied `SPIKE_INJECTED` | **HONORED** — Gate-B GO |
| LEAF01 | 4 × PreToolUse:Bash, Bash issued **inside a subagent** | fullecho, bare | subagent ran `echo SPIKE_ORIGINAL` | `SPIKE_INJECTED` | HONORED under subagent + multi-hook |

## Payload-shape facts (real fixtures in `fixtures/`, ADR-006 Amd1 real-shape)

- **Bash top-level** (`bash-top-level.json`): `agent_type` **absent** → §7.7-3 top-level Bash EXCLUDE is correct.
- **Bash-in-subagent** (`bash-in-subagent.json`): `agent_type="general-purpose"`, `agent_id` present
  → confirms §6 fact-2 (agent_type present inside a subagent call); leaf② subject source = payload `agent_type` (AC-8). ✓
- **Agent spawn** (`agent-spawn.json`): `tool_input` carries `subagent_type` (+ `description`,`prompt`,`run_in_background`)
  → header subject source = `tool_input.subagent_type` (AC-7). Top-level Agent payload has no `agent_type` → dispatcher name never injected (§결정 1). ✓
- Payload top-level keys: `session_id, transcript_path, cwd, prompt_id, permission_mode, agent_id, agent_type, effort, hook_event_name, tool_name, tool_input, tool_use_id`.
- Subagent-spawn tool_name = **`Agent`** (matcher `Agent` catches it). ✓

## Design implications (feed to implementation)

1. **REPLACE-safe whole-echo is REQUIRED, not defensive** (BARE01). The production hook MUST
   emit a full copy of `tool_input` with only `description` prepended. On ANY failure it MUST
   emit **nothing** (no partial `updatedInput`) — a malformed `updatedInput` hard-fails the tool.
2. **bare `updatedInput` (no `permissionDecision`) is honored** → G4 (never allow-override) is viable.
3. Both surfaces GO → implement Agent (in-place merge) + Bash (new sibling) injection.
4. Fail-open bound is load-bearing (retain), since #15897 is closed-not-planned.

## Reproduce

```
bash run.sh          # runs all 5 variants, prints the honor signal per run
```
Requires: `claude` CLI on PATH, codeforge plugin enabled (provides the 3 real Bash siblings),
`python` on PATH. Env: `SPIKE_VARIANT`, `SPIKE_NONCE`, `SPIKE_LOG`, `SPIKE_STAMP` (see `inject.py`).
