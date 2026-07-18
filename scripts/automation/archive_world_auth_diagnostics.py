#!/usr/bin/env python3
"""Safe Codex transport diagnostics: report configuration presence, never values."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


def exists(path: str | None) -> bool:
    return bool(path and Path(path).exists())


home = os.environ.get("HOME")
codex_home = os.environ.get("CODEX_HOME", str(Path(home or "/nonexistent") / ".codex"))
command = "/home/csj1116/.local/lib/archive-world/codex"
version = subprocess.run([command, "exec", "--version"], text=True, capture_output=True, check=False)
report = {
    "user": os.environ.get("USER"),
    "home": home,
    "shell": os.environ.get("SHELL"),
    "pathHasCodex": bool(shutil.which("codex")),
    "codexExecutableExists": exists(command),
    "codexVersionExit": version.returncode,
    "codexVersion": version.stdout.strip(),
    "codeXHomeSet": "CODEX_HOME" in os.environ,
    "codexHomeExists": exists(codex_home),
    "configExists": exists(str(Path(codex_home) / "config.toml")),
    "authFilePresence": {
        "auth.json": exists(str(Path(codex_home) / "auth.json")),
        "credentials.json": exists(str(Path(codex_home) / "credentials.json")),
    },
    "xdgConfigHomeSet": "XDG_CONFIG_HOME" in os.environ,
    "loginShell": bool(os.environ.get("SHLVL")),
    "secretValuesRead": False,
}
print(json.dumps(report, indent=2))
