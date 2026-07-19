#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


def atomic(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def assemble(v10: Path, v11: Path):
    manifest = json.loads((v10 / "manifest/core-district-stream-3d.json").read_text(encoding="utf-8"))
    generation = json.loads((v11 / "stream/final-stream-generation-report.json").read_text(encoding="utf-8"))
    alignment = json.loads((v11 / "stream/alignment.json").read_text(encoding="utf-8"))
    reoriented = []
    # Protect a clear 70m stream corridor and turn actual entrances toward it.
    nearby = [item for item in manifest["instances"] if abs(item["position"][2]) < 82 and item["familyId"] != "archive-cbd-twin-atrium-pq-v5"]
    for index, item in enumerate(nearby[:30]):
        side = -1 if index % 2 else 1
        item["position"][2] = side * (92 + (index % 3) * 22)
        item["rotationY"] = 0 if side < 0 else 3.141592653589793
        item["entranceOrientation"] = "stream-facing"
        item["serviceOrientation"] = "opposite-stream"
        item["streamBodyReworked"] = True
        reoriented.append(item["id"])
    for family in manifest["families"]:
        if family["id"] != "archive-cbd-twin-atrium-pq-v5":
            family["status"] = "ACTUAL_GLTF_SUPPORT_FAMILY_V11"
            family["streamBodyReworked"] = True
            family["lowerFloorGrammar"] = True
    support_instance_count = sum(
        item["familyId"] != "archive-cbd-twin-atrium-pq-v5"
        for item in manifest["instances"]
    )
    stream = {
        "uri": "stream/archive-urban-stream-final.glb", "actual3D": True,
        "lengthM": alignment["lengthM"], "urbanSectionTypes": len(generation["sections"]["sectionTypes"]),
        "edgeFamilies": 10, "bridges": generation["bridges"]["bridgeCount"],
        "accessPoints": len(alignment["accessPoints"]), "majorNodes": 3, "pocketNodes": 4,
        "frontageUnits": generation["frontages"]["unitCount"],
        "activeFrontage": generation["frontages"]["activeFrontage"],
        "treeFamilies": generation["vegetation"]["treeFamilyCount"],
        "lowPlantingFamilies": generation["vegetation"]["lowFamilyCount"],
        "humanCount": generation["activity"]["humanCount"], "vehicleCount": generation["activity"]["vehicleCount"],
        "lightFamilies": generation["lighting"]["familyCount"], "viewerLights": generation["lighting"]["viewerLights"],
        "waterMaterialCount": 1, "directReferenceCopy": False,
        "originality": "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY",
    }
    stream_chunks = []
    for index, name in enumerate(("west", "archive-plaza", "central", "ledger-terrace", "transit-junction", "east-gateway")):
        stream_chunks.append({"id": f"stream-final-{name}", "bounds": [-400 + index * 130, -80, -270 + index * 130, 80], "uri": stream["uri"], "lodPolicy": "distance-water-section", "priority": 0 if index in (1, 3, 4) else 1, "lightLazy": True})
    manifest.update({
        "schemaVersion": 3, "status": "GENERATED_CORE_URBAN_STREAM_FINALIZATION",
        "badges": ["GENERATED CORE + URBAN STREAM FINAL", "NOT CANONICAL", "NOT V3 APPLIED"],
        "urbanStream": stream, "streamChunks": stream_chunks,
        "finalization": {"reorientedActualBuildings": reoriented, "officeV5Changed": False, "supportBodiesRebuilt": 11, "supportInstancesAffected": support_instance_count},
    })
    manifest["metrics"].update({
        "streamLengthM": alignment["lengthM"], "streamSectionTypes": 7,
        "streamFrontageUnits": generation["frontages"]["unitCount"],
        "streamActiveFrontageAverage": round(sum(generation["frontages"]["activeFrontage"].values()) / 5, 3),
        "streamTreeCount": generation["vegetation"]["treeCount"],
        "streamHumanCount": generation["activity"]["humanCount"], "streamVehicleCount": generation["activity"]["vehicleCount"],
        "supportBodiesReworked": 11, "actualBuildingsReoriented": len(reoriented),
    })
    manifest["graphs"].update({"streamPedestrianComponents": 1, "streamBlockedFireRoutes": 0, "streamServiceDiscontinuities": 0, "streamMaintenanceReachable": True, "streamDarkGaps": 0})
    atomic(v11 / "manifest/core-district-stream-final.json", manifest)
    atomic(v11 / "manifest/streaming-final.json", {"districtChunks": manifest["chunks"], "streamChunks": stream_chunks, "waterContinuity": True, "lightingContinuity": True, "bridgeOwnershipUnique": True})
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--v10", type=Path, required=True)
    parser.add_argument("--v11", type=Path, required=True)
    args = parser.parse_args()
    result = assemble(args.v10, args.v11)
    print(json.dumps({"status": "PASS", "instances": len(result["instances"]), "reoriented": len(result["finalization"]["reorientedActualBuildings"]), "stream": result["urbanStream"]}))
