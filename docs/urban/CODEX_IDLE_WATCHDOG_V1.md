# Codex Idle Watchdog V1

This is a repository-local Python watchdog. It polls every ten minutes and
uses an atomic checkpoint in `state/archive-world-marathon.json`. It is not a
ChatGPT browser automation mechanism.

## Liveness model

`WATCHDOG_RUNNING` and `WORKER_RUNNING` are separate. The UI/reporting layer
may say *working* only while a worker PID, relevant child, worker heartbeat,
worker stdout/stderr, Generated output, source diff, test result, or commit has
changed in the last ten minutes. A watchdog with no worker is explicitly
`WATCHDOG_RUNNING + WORKER_IDLE`.

`AUTH_BLOCKED` is a resume-transport condition, never a Track failure. A Track
remains pending for an authenticated runner or the active Codex session. Only
an actual content/validation failure belongs in `blockedTracks`.

## Safety contract

The watchdog only considers a resume when the queue has a pending track and
all of these are unchanged for ten minutes: Marathon PID, Blender/Node/Python
children, heartbeat, watchdog log size, Generated file count/bytes, Git HEAD,
and the approved worktree baseline. `COMPLETE`, `WAITING_APPROVAL`, `BLOCKED`,
and `GATE_WAITING` never resume. A branch/HEAD/worktree mismatch becomes
`BLOCKED`; the watchdog never fixes Git state.

It permits at most two restarts for one track, six in 24 hours, and one restart
per 30 minutes. It records every attempt in `restartHistory`. A resume command
must be installed on `PATH`; an unavailable command is reported as
`resume-command-unavailable`, not silently treated as success.

## Commands (WSL)

```bash
cd /mnt/c/ArchivePJT/Archive-World
python3 scripts/test_archive_world_watchdog.py
python3 scripts/automation/archive_world_watchdog.py --config config/archive-world-watchdog.json --dry-run --once
nohup python3 scripts/automation/archive_world_watchdog.py --config config/archive-world-watchdog.json \
  >> logs/archive-world-watchdog-daemon.log 2>&1 &
cat state/archive-world-watchdog.pid
tail -f logs/archive-world-watchdog.log
python3 scripts/automation/archive_world_resume.py --state state/archive-world-marathon.json
kill "$(cat state/archive-world-watchdog.pid)"
```

The Codex CLI bundled with the Windows app may be mounted non-executable in
WSL. The one-time local bootstrap is therefore:

```bash
mkdir -p /home/csj1116/.local/lib/archive-world
cp '/mnt/c/Program Files/WindowsApps/OpenAI.Codex_26.707.9981.0_x64__2p2nqsd0c76g0/app/resources/codex' \
  /home/csj1116/.local/lib/archive-world/codex
chmod 700 /home/csj1116/.local/lib/archive-world/codex
/home/csj1116/.local/lib/archive-world/codex exec --help
```

After a Windows/WSL reboot, run the `nohup` command again. It deliberately does
not register a Windows Scheduled Task. Recovery notifications are emitted as
structured log events. The resumed Codex prompt includes the one permitted
recovery notification and the configured channel ID; no token or webhook is
stored in this repository.
