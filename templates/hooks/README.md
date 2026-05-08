# templates/hooks — CFP-137 agent-team lifecycle hooks

Claude Code hook scripts for the agent-team coordination lifecycle.
3 hooks register against shared task-list events and idle transitions.

## Hook index

| Script | Trigger | Exit 0 | Exit 2 |
|---|---|---|---|
| [`teammate-idle.sh`](teammate-idle.sh) | Teammate enters idle state | allow idle | nudge back to work (pending tasks remain) |
| [`task-created.sh`](task-created.sh) | New task added to shared list | allow creation | reject creation (cycle / schema fail) |
| [`task-completed.sh`](task-completed.sh) | Task marked complete | accept completion | reject completion (evidence missing) |

All scripts use `#!/usr/bin/env bash` + `set -euo pipefail`. Exit code semantics
follow Claude Code hook spec — `0` = continue, `2` = block.

## Env vars

| Var | Used by | Meaning |
|---|---|---|
| `CLAUDE_TEAM_NAME` | teammate-idle | Team identifier (design / requirements / ...) |
| `CLAUDE_TEAMMATE_NAME` | teammate-idle | Teammate identifier (SecurityArch / OpRiskArch / ...) |
| `CLAUDE_TASK_ID` | task-created · task-completed | Task identifier |
| `CLAUDE_TASK_TITLE` | task-created | Task title (free-form) |
| `CLAUDE_TASK_DEPENDENCIES` | task-created | Comma-separated upstream task IDs |
| `CLAUDE_TASK_COMPLETOR` | task-completed | Teammate identifier who marked complete |

## Registration in `.claude/settings.json`

```jsonc
{
  "hooks": {
    "TeammateIdle":  [{ "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/templates/hooks/teammate-idle.sh"  }] }],
    "TaskCreated":   [{ "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/templates/hooks/task-created.sh"   }] }],
    "TaskCompleted": [{ "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/templates/hooks/task-completed.sh" }] }]
  }
}
```

Make scripts executable: `chmod +x templates/hooks/*.sh`.

## Customization

Each script ships as a no-op skeleton (exit 0). Edit per-consumer to enable:

- **teammate-idle**: pending-task scan via task list backend → exit 2 if claims open
- **task-created**: dependency-cycle DFS over task graph → exit 2 on cycle
- **task-completed**: gate label attach via `gh api` + Story §9/§11 update trigger

Bypass: rename script or remove from `settings.json` `hooks` block.
