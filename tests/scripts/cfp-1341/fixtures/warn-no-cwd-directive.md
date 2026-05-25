# Fixture: WARN — no cwd directive (sentinel for [WARN-CWD-DIRECTIVE-ABSENT])

Story content with Lane PL spawn but NO cwd directive in window.

## §14 Lane Evidence

### DesignReviewPLAgent spawn (test fixture)

spawn command (no cwd directive — should trigger WARN):
```
DesignReviewPLAgent spawn with verify-via-direct-Read
some unrelated content
more unrelated content
```

verify-via output (WARN expected — cwd directive 3 forms 모두 부재).

This fixture intentionally lacks `git -C`, `cd <path>`, and `[WORKTREE-CWD:]` directives within ±20 line window of the spawn marker, simulating the CFP-1316 iter 2 sentinel pattern where DesignReviewPL inline_orchestrator_verify substituted default cwd silently.
