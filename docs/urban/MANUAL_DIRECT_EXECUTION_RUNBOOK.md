# Manual Direct Execution Runbook

Use this mode when unattended resume transport is `AUTH_BLOCKED` but an interactive Codex session is active.

1. Confirm the feature branch, HEAD, status, external Generated root, and protected paths.
2. Record `DIRECT_SESSION_RUNNING` only while a real activity signal is fresh.
3. Execute the next independent queue item directly; do not wait for the watchdog.
4. Run the task-specific unit/smoke tests and path/secret scans.
5. Stage only explicit verified files; never use `git add -A`.
6. Inspect the cached diff, commit the independent unit, push normally, and confirm local/remote HEAD.
7. Continue to the next queue item. Preserve failed outputs externally with an honest status.

Canonical promotion, production layout changes, runtime changes, main merge, and bulk family generation remain approval gates.
