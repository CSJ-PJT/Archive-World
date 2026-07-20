import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from urban_stream.assemble_precision_hero import (EXPANDED_REPLACED, REPLACED,
                                                  FAMILY_BY_BLOCK_ROLE, assemble)

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);baseline=root/"baseline";target=root/"target"
    (baseline/"manifest").mkdir(parents=True);(target/"hero-archive").mkdir(parents=True)
    (target/"hero-expanded").mkdir(parents=True)
    manifest={
        "instances":[{"id":value} for value in sorted(REPLACED | EXPANDED_REPLACED)]+[{"id":"keep"}],
        "families":[],"blocks":[],"infrastructure":{"uri":"infrastructure.glb"},
        "metrics":{"buildingInstances":13,"actualFamilies":12,"actualBlocks":22,"planningProxyRatio":0},
        "badges":[],
    }
    (baseline/"manifest/core-district-stream-final.json").write_text(json.dumps(manifest),encoding="utf-8")
    report={"revision":29,"qualityTarget":{"grade":"S","minimumScore":95},"buildingCount":6,
            "geometry":{"triangles":479272},"lobbyCount":6,"retailPublicBayCount":54,
            "humanCount":131,"treeCount":38}
    (target/"hero-archive/archive-water-plaza-hero-v29-report.json").write_text(json.dumps(report),encoding="utf-8")
    expanded={"revision":36,"buildingCount":13,"zones":["Ledger","Transit"],
              "geometry":{"triangles":552512},"life":{"humanCount":60,"treeCount":40},
              "corridor":{"lengthM":500,"waterBedContinuous":True}}
    (target/"hero-expanded/core-stream-ledger-transit-v36-report.json").write_text(json.dumps(expanded),encoding="utf-8")
    result=assemble(baseline,target,"v29","v36",95)
    assert len(result["instances"])==1
    assert result["heroZones"][0]["uri"].endswith("hero-v29.glb")
    assert result["precision"]["revision"]==36
    assert result["precision"]["requiredScore"]==95
    assert result["precision"]["qualityTarget"]["grade"]=="S"
    assert result["precision"]["mode"]=="ALL_CORE_STREAM_ZONES"
    assert result["precision"]["nextZoneLocked"] is False
    assert len(result["heroZones"])==2
    assert result["heroZones"][1]["buildingCount"]==13
    assert result["heroZones"][0]["performanceUri"].endswith("v29-lod2.glb")
    assert result["heroZones"][1]["performanceUri"].endswith("v36-lod2.glb")
    assert result["metrics"]["buildingInstances"]==20
    assert result["precision"]["metropolitanComposition"]["officeV5Changed"] is False
    assert result["precision"]["metropolitanComposition"]["scatterRowsRemoved"] is True
    assert result["heroZones"][0]["geometryRevision"] == 29
    assert result["heroZones"][1]["geometryRevision"] == 36
    assert len(FAMILY_BY_BLOCK_ROLE)>=12
    saved=json.loads((target/"manifest/core-district-stream-precision.json").read_text(encoding="utf-8"))
    assert saved==result

print("precision hero assembler version contract: PASS")
