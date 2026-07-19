from pathlib import Path
import sys

sys.path.insert(0, str(Path("scripts/urban_stream")))

from validate_integrated_stream import validate

result = validate("/mnt/c/ArchiveData/World/Generated/v10/core-urban-stream-integrated-rework")
assert result["status"] == "PASS" and all(result["checks"].values())
assert not result["validation"]["emptyMeshes"]
assert not result["validation"]["looseGeometry"]
print("urban stream production contracts: PASS")
