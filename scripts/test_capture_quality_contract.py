from pathlib import Path

source = Path("scripts/urban_stream/analyze_capture_quality.ps1").read_text(encoding="utf-8")
for token in ("mean", "p05", "p50", "p95", "blackClip", "whiteClip",
              "contrast", "variance", "blankFrame", "pngSignature",
              '$temporary="$target.tmp"'):
    assert token in source, token
assert "C:\\Users\\" not in source
print("capture quality metric contract: PASS")
