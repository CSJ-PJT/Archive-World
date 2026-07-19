#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: str | Path) -> dict:
    root = Path(root)
    manifest = read_json(root / "manifest/core-district-stream-3d.json")
    generation = read_json(root / "stream/stream-generation-report.json")
    alignment = read_json(root / "stream/alignment.json")

    checks = {
        "actualStreamGLB": (root / manifest["urbanStream"]["uri"]).is_file(),
        "length650": alignment["lengthM"] >= 650,
        "edgeFamilies8": generation["edges"]["count"] >= 8,
        "crossings6": generation["bridges"]["bridgeCount"] >= 6,
        "majorNodes3": generation["nodes"]["majorNodes"] >= 3,
        "pocketNodes4": generation["nodes"]["pocketNodes"] >= 4,
        "accessible6": sum(point["accessible"] for point in alignment["accessPoints"]) >= 6,
        "reworkedBlocks8": sum(block.get("streamOriented", False) for block in manifest["blocks"]) >= 8,
        "pedestrianConnected": manifest["graphs"]["streamPedestrianComponents"] == 1,
        "serviceFireConnected": manifest["graphs"]["streamBlockedFireRoutes"] == 0,
        "waterContinuous": generation["edges"]["waterContinuity"],
        "bedContinuous": generation["edges"]["bedContinuity"],
        "noFloating": generation["activity"]["floatingObjects"] == 0,
        "noImages": generation["imageDatablocks"] == 0,
        "noProxy": manifest["metrics"]["planningProxyRatio"] == 0,
        "directCopyZero": not manifest["urbanStream"]["directReferenceCopy"],
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": manifest["metrics"],
        "geometry": generation["geometry"],
        "validation": generation["validation"],
    }
    (root / "reports").mkdir(exist_ok=True)
    (root / "reports/integrated-validation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result))
    raise SystemExit(result["status"] != "PASS")
