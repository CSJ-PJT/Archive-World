from pathlib import Path
t=(Path(__file__).parents[1]/'scripts/core_district/build_core_district.ps1').read_text()
for stage in ('families','infrastructure','assembly','viewer'):assert stage in t
assert 'Blender 5.2 missing' in t and 'checkpoints' in t and "C:/ArchiveData/" in t
assert '/mnt/c/ArchiveData' not in t.split('python')[0]
print('Core reproducible build source PASS')
