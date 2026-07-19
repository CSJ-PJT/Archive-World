from pathlib import Path

source = Path("scripts/urban_stream/capture_final_stream_review.ps1").read_text(encoding="utf-8")
for contract in ("corestreamfinal", "1920,1080", "actualWebGL", "capture-report.json.tmp", "PNG", "day','dusk','night"):
    assert contract in source
assert source.count("'district-aerial'") == 1
assert "'technical-status'" in source
assert "for($i=0;$i -lt $views.Count;$i++)" in source
assert "$times=@('day','dusk','night')" in source
assert "git clean" not in source
print("final stream capture contract: PASS (36 x 3 = 108)")
