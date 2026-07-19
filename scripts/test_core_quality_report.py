from pathlib import Path
t=(Path(__file__).parents[1]/'scripts/core_district/quality_report.py').read_text()
assert 'visualScore' in t and 'below B/80' in t and 'Headless WebGL' in t
assert 'canonical":False' in t and 'v3Applied":False' in t
print('Core quality report source PASS')
