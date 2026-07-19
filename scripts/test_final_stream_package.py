from pathlib import Path

source = Path("scripts/urban_stream/package_final_stream.ps1").read_text(encoding="utf-8")
for contract in ("REFERENCE_ONLY_NOT_IMPLEMENTATION_OUTPUT", "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY", "checksums.json", "Get-FileHash", "Compress-Archive", "canonical=$false", "v3Applied=$false"):
    assert contract in source
assert "git clean" not in source and "git add -A" not in source
assert "Generated\\v11\\core-urban-stream-finalization" in source
print("final stream package contract: PASS")
