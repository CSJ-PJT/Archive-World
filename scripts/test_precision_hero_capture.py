from pathlib import Path


source = Path("scripts/urban_stream/capture_precision_hero_s.ps1").read_text(encoding="utf-8")
for token in (
    "1920,1080",
    "actualWebGL=$true",
    "eyeHeightM=1.65",
    "district-aerial",
    "ledger-terrace",
    "transit-junction",
    "archive-water-plaza",
    "archive-gateway",
    "METROPOLITAN_CORE_STREAM_PRECISION",
    "virtual-time-budget",
    "capture-report.json.tmp",
):
    assert token in source, token
assert "C:\\Users\\" not in source
print("precision hero S capture contract: PASS")
