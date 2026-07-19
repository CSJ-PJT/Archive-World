from pathlib import Path

source = Path("scripts/urban_stream/capture_stream_review.ps1").read_text(encoding="utf-8")
assert "corestream" in source and "1920,1080" in source
assert "archive-water-plaza" in source and "transit-stream-junction" in source
assert "future-riverfront-corridor" in source and "service-stream-crossing" in source
assert "$times=@('day','dusk','night')" in source
assert "actualWebGL=$true" in source and "invalid PNG" in source
print("stream capture contract: PASS")
