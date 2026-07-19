from pathlib import Path

source = Path("scripts/urban_stream/build_final_stream.ps1").read_text(encoding="utf-8")
for stage in ("prepare", "support", "geometry", "assembly", "validate", "viewer"):
    assert f"RunStage {stage}" in source
for contract in ("checkpoints", "SKIP completed", "--strict", "wslpath", "--factory-startup", "npm.cmd run typecheck", "CORE_STREAM_FINAL_BASE_URL"):
    assert contract in source
assert "git clean" not in source and "git add -A" not in source
assert "/mnt/c/" not in source
assert "core-urban-stream-integrated-rework" in source
print("final stream reproducible runner: PASS")
