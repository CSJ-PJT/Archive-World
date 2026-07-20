#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.metropolitan.finalize_metropolitan_precision import build_precision_scene


scene = build_precision_scene()
assert scene["status"] == "GENERATED_METROPOLITAN_PRECISION"
assert scene["canonical"] is False and scene["v3Applied"] is False
assert scene["runtimeMutation"] is False and scene["mainMerge"] is False
assert len(scene["districts"]) == 13
assert len(scene["blocks"]) >= 450
assert len(scene["instances"]) >= 3900
assert scene["metrics"]["uniqueFamilies"] == 42
assert scene["metrics"]["planningProxyRatio"] == 0
assert scene["metrics"]["activityClusters"] >= len(scene["blocks"]) * 3
assert len({item["palette"] for item in scene["districts"]}) >= 10
assert len({item["massing"] for item in scene["instances"]}) == 6
assert len({item["facade"] for item in scene["instances"]}) == 7
assert all(item["activeFrontage"] >= .15 for item in scene["instances"])
assert all(item["status"] == "ACTUAL_RUNTIME_GEOMETRY_CONTRACT" for item in scene["instances"])
assert Counter(item["districtId"] for item in scene["instances"]) == Counter({item["id"]: item["instanceCount"] for item in scene["districts"]})
assert not any(item["canonical"] or item["v3Applied"] for item in scene["instances"])
print("metropolitan precision all-district contract: PASS")
