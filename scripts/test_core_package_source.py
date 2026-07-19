from pathlib import Path
t=(Path(__file__).parents[1]/'scripts/core_district/package_core_district.py').read_text()
assert 'hashlib.sha256' in t and "'cache' not in p.parts" in t and "'canonical':False" in t
print('Core district package source PASS')
