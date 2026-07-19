from pathlib import Path
import ast

source = Path("scripts/blender/urban_stream_final/vegetation_v11.py").read_text(encoding="utf-8")
ast.parse(source)
for feature in ("tree-trunk-tapered", "tree-branch-proxy", "tree-crown-multilobe", "low-planting-cluster", '"maxAdjacentVariant": 2'):
    assert feature in source
assert "range(6)" in source and "range(8)" in source
assert '"floatingPlants": 0' in source and '"routeIntrusions": 0' in source
print("final vegetation system: PASS")
