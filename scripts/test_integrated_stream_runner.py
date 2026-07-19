from pathlib import Path

source = Path("scripts/urban_stream/build_integrated_stream.ps1").read_text(encoding="utf-8")
for stage in ("plan", "geometry", "assembly", "validate", "viewer"):
    assert f"Mark {stage}" in source
for contract in ("--strict", "checkpoints", "wslpath", "--factory-startup", "npm.cmd run typecheck"):
    assert contract in source
assert "git clean" not in source and "git add -A" not in source
assert "/mnt/c/" not in source
print("integrated stream runner: PASS")
