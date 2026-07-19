from pathlib import Path
p=Path(__file__).parents[1]/'scripts/core_district/capture_core_review.ps1';t=p.read_text()
assert "@('aerial','archive-plaza'" in t and "$times=@('day','dusk','night')" in t
assert '--window-size=1920,1080' in t and 'capture failed' in t
print('Core district capture source PASS')
