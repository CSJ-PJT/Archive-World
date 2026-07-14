# Archive task completion notifications

`scripts/archive-task-runner.mjs` reports the terminal state of a long task with
a detached best-effort notification. It first uses the existing local
`SLACK_BOT_TOKEN` and `SLACK_CHANNEL` configuration, then falls back to
`SLACK_WEBHOOK_URL` when available. Credentials are never written to logs or
messages.

Notification delivery does not affect the wrapped task's exit code. Messages
include service, task, PASS/FAIL, test result, build result, elapsed time,
commit hash when available, and blocker.

Example:

```powershell
node scripts/archive-task-runner.mjs --service Archive-World --task viewer-build --cwd . --tests PASS --build PASS -- npm.cmd run build
```

Only variable names belong in project files. Keep actual token, webhook, and
channel values in local environment configuration.

For an aggregate gate, `--result`, `--commit`, and `--blocker` can override the
notification fields while the wrapped command retains its own exit code.
