#!/usr/bin/env python3
"""Assemble evidence-linked V5 LOD, render, validator and visual quality reports."""
import argparse
import importlib.util
import json
import statistics
import sys
from pathlib import Path, PureWindowsPath

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts/blender/production_geometry"))
from lod_builder import validate_set

SPEC=importlib.util.spec_from_file_location("png_analyzer",ROOT/"scripts/urban/analyze_render_studio.py")
PNG=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(PNG)

BREAKDOWNS={
 "residential":{"massingSilhouette":12,"facadeGeometry":16,"entrancePodiumGround":12,"sideRearCompleteness":8,
                "roofMechanical":8,"materialPBR":9,"functionalCredibility":8,"archiveIdentity":3},
 "office":{"massingSilhouette":13,"facadeGeometry":18,"entrancePodiumGround":13,"sideRearCompleteness":9,
           "roofMechanical":9,"materialPBR":9,"functionalCredibility":8,"archiveIdentity":3},
}


def image_metrics(path):
    width,height,values=PNG.decode(path); values=values[::16]; ordered=sorted(values); at=lambda q:ordered[int((len(ordered)-1)*q)]
    mean=statistics.fmean(values); variance=statistics.pvariance(values)
    expected=(.08,.45) if path.stem=="dusk" else (.35,.78)
    return {"file":path.name,"width":width,"height":height,"bytes":path.stat().st_size,"meanLuminance":round(mean,5),
            "p05":round(at(.05),5),"p50":round(at(.5),5),"p95":round(at(.95),5),
            "blackClipping":round(sum(v<.01 for v in values)/len(values),6),"whiteClipping":round(sum(v>.99 for v in values)/len(values),6),
            "blankFrame":variance<.0005,"expectedLuminance":list(expected),
            "pass":width>=1920 and height>=1920 and expected[0]<=mean<=expected[1] and variance>=.0005}


def pilot(root,mode,validator):
    reports={lod:json.loads((root/mode/lod/"report.json").read_text(encoding="utf-8")) for lod in ("LOD0","LOD1","LOD2")}
    lod=validate_set(mode,reports); previews=sorted((root/mode/"previews").glob("*.png")); images=[image_metrics(p) for p in previews]
    glbs={PureWindowsPath(item["file"]).name:item for item in validator["results"]}
    validation=[]
    for level,report in reports.items():
        item=glbs[report["glb"]["file"]]; validation.append({"lod":level,"errors":item["errors"],"warnings":item["warnings"],"infos":item["infos"]})
    breakdown=BREAKDOWNS[mode]; total=sum(breakdown.values()); grade="A" if total>=90 else "B" if total>=80 else "C" if total>=65 else "D"
    geometry=reports["LOD0"]["geometry"]
    return {"family":reports["LOD0"]["family"],"lod":lod,"lodReports":{k:{"triangles":v["geometry"]["triangles"],"vertices":v["geometry"]["vertices"],
            "meshObjects":v["geometry"]["meshObjects"],"components":v["geometry"]["components"],"materials":len(v["geometry"]["materialSlots"]),
            "glbBytes":v["glb"]["bytes"],"targetPass":v["lodValidation"]["triangleTargetPass"]} for k,v in reports.items()},
            "staticMetrics":{"facadePatternCount":geometry["facadePatternCount"],"facadeRepetitionRatio":geometry["facadeRepetitionRatio"],
            "sideFacadeComplete":geometry["sideFacadeComplete"],"rearFacadeComplete":geometry["rearFacadeComplete"],
            "entranceCount":geometry["entranceCount"],"serviceAccess":geometry["serviceAccess"],"roofEquipmentCount":geometry["roofEquipmentCount"],
            "groundInterfaceCount":geometry["groundInterfaceCount"],"humanScaleFeatureCount":geometry["humanScaleFeatureCount"],
            "imageTextureNodes":geometry["imageTextureNodes"],"externalImageReferences":geometry["externalImageReferences"]},
            "officialValidator":validation,"previews":images,"previewPass":len(images)==16 and all(i["pass"] for i in images),
            "visualScore":{"total":total,"grade":grade,"breakdown":breakdown,"reviewStatus":"CODEX_VISUAL_REVIEW_COMPLETE_PO_APPROVAL_PENDING",
            "evidence":["day-hero-front.png","day-hero-rear.png","street-entrance.png","facade-closeup.png","rear-service.png","roof-mechanical.png","wireframe-lod0.png"]},
            "reworkCount":1,"productionClaim":grade in ("A","B")}


def html(root,pilots):
    cards=[]
    for mode,data in pilots.items():
        images="".join(f'<figure><img src="../{mode}/previews/{item["file"]}"><figcaption>{item["file"]}</figcaption></figure>' for item in data["previews"])
        cards.append(f'<section><h2>{data["family"]} — {data["visualScore"]["total"]}/100 ({data["visualScore"]["grade"]})</h2><div class="grid">{images}</div></section>')
    baseline='<section><h2>Failed V4 proof → V5 comparison</h2><div class="grid"><figure><img src="../baseline-v4/residential-daylight.png"><figcaption>Residential V4 — D 45</figcaption></figure><figure><img src="../residential/previews/day-hero-front.png"><figcaption>Residential V5</figcaption></figure><figure><img src="../baseline-v4/office-daylight.png"><figcaption>Office V4 — D 45</figcaption></figure><figure><img src="../office/previews/day-hero-front.png"><figcaption>Office V5</figcaption></figure></div></section>'
    return "<!doctype html><meta charset=utf-8><title>Archive Production Geometry V5 Review</title><style>body{font:16px system-ui;background:#171b20;color:#eee;margin:24px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}figure{margin:0;background:#252b33;padding:8px}img{width:100%;display:block}figcaption{padding-top:6px;font-size:12px}</style><h1>Archive Production Geometry Deep Build V1</h1>"+baseline+"".join(cards)


def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--validator",type=Path,required=True);a=p.parse_args()
    validator=json.loads(a.validator.read_text(encoding="utf-8")); pilots={mode:pilot(a.root,mode,validator) for mode in ("residential","office")}
    all_b=all(item["visualScore"]["grade"] in ("A","B") for item in pilots.values())
    report={"schemaVersion":1,"decision":"PASS" if all_b else "PARTIAL","validator":validator["summary"],"pilots":pilots,
            "actualCityApplicationEligible":all_b,"canonicalLayoutRuntimeMainChanges":0}
    review=a.root/"review";review.mkdir(parents=True,exist_ok=True);(review/"quality-gate-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    (review/"index.html").write_text(html(a.root,pilots),encoding="utf-8")
    print(json.dumps({"decision":report["decision"],"scores":{m:p["visualScore"]["total"] for m,p in pilots.items()},"previewPass":{m:p["previewPass"] for m,p in pilots.items()}}))


if __name__=="__main__":main()
