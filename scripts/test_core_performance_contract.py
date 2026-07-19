import re
from pathlib import Path

SOURCE=Path('scripts/core_district/measure_core_performance.ps1').read_text(encoding='utf-8')
assert "DurationSeconds = 30" in SOURCE
assert "HEADLESS_CHROME_ACTUAL_WEBGL" in SOURCE
assert "UNKNOWN_NOT_MEASURED" in SOURCE
assert "HARDWARE_CHROME_ACTUAL_WEBGL" in SOURCE
assert '[switch]$Hardware' in SOURCE
assert re.search(r'onePercentLow=.*lowFps',SOURCE)
assert 'averageFps' in SOURCE and 'drawCalls' in SOURCE and 'triangles' in SOURCE
print('core performance capture contract: PASS')
