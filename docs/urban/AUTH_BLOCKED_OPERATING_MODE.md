# AUTH_BLOCKED Operating Mode

Transport authentication and task execution are separate states. `AUTH_BLOCKED` means the unattended Codex resume transport cannot authenticate; it does not block direct work in an already active session.

Only `WORKER_RUNNING` or `DIRECT_SESSION_RUNNING` may be described as working. A watchdog by itself is `WATCHDOG_RUNNING` and must be reported as monitoring without a worker. Direct-session running requires source, test, render, Generated-output, commit, or push activity within ten minutes. Otherwise it becomes `DIRECT_SESSION_IDLE`.

Never print credentials, inspect token contents, copy credentials into Git, or retry an identical authentication failure indefinitely.
