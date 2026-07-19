import json
import tempfile
from pathlib import Path

from urban_stream.assemble_precision_hero import REPLACED, assemble

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);baseline=root/"baseline";target=root/"target"
    (baseline/"manifest").mkdir(parents=True);(target/"hero-archive").mkdir(parents=True)
    manifest={
        "instances":[{"id":value} for value in sorted(REPLACED)]+[{"id":"keep"}],
        "families":[],"blocks":[],"infrastructure":{"uri":"infrastructure.glb"},
        "metrics":{"buildingInstances":13,"actualFamilies":12,"actualBlocks":22,"planningProxyRatio":0},
        "badges":[],
    }
    (baseline/"manifest/core-district-stream-final.json").write_text(json.dumps(manifest),encoding="utf-8")
    report={"revision":29,"qualityTarget":{"grade":"S","minimumScore":95},"buildingCount":6,
            "geometry":{"triangles":479272},"lobbyCount":6,"retailPublicBayCount":54,
            "humanCount":131,"treeCount":38}
    (target/"hero-archive/archive-water-plaza-hero-v29-report.json").write_text(json.dumps(report),encoding="utf-8")
    result=assemble(baseline,target,"v29",95)
    assert len(result["instances"])==1
    assert result["heroZones"][0]["uri"].endswith("hero-v29.glb")
    assert result["precision"]["revision"]==29
    assert result["precision"]["requiredScore"]==95
    assert result["precision"]["qualityTarget"]["grade"]=="S"
    saved=json.loads((target/"manifest/core-district-stream-precision.json").read_text(encoding="utf-8"))
    assert saved==result

print("precision hero assembler version contract: PASS")
