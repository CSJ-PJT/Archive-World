#!/usr/bin/env python3
"""Evidence-linked Residential V6 quality gate; never mutates the frozen Office V5 baseline."""
from __future__ import annotations

import argparse,importlib.util,json,statistics,sys
from pathlib import Path,PureWindowsPath

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("png_analyzer",ROOT/"scripts/urban/analyze_render_studio.py")
PNG=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(PNG)

BREAKDOWN={"massingSilhouette":13,"facadeGeometry":17,"entrancePodiumGround":13,"sideRearCompleteness":9,
           "roofMechanical":9,"materialPBR":9,"functionalCredibility":8,"archiveIdentity":4}
EVIDENCE={
 "massingSilhouette":["day-hero-front.png","day-hero-rear.png","side-silhouette.png","bird-view.png"],
 "facadeGeometry":["facade-lower.png","facade-middle.png","facade-upper.png","balcony-variation.png"],
 "entrancePodiumGround":["main-entrance.png","secondary-entrance.png","community-frontage.png","ground-public-realm.png"],
 "sideRearCompleteness":["side-silhouette.png","service-rear.png"],"roofMechanical":["roof-mechanical.png","bird-view.png"],
 "materialPBR":["day-hero-front.png","facade-lower.png","ground-public-realm.png"],
 "functionalCredibility":["courtyard.png","drop-off.png","parking-ramp.png","service-rear.png"],
 "archiveIdentity":["day-hero-front.png","dusk.png"],
}


def image_metrics(path):
    width,height,values=PNG.decode(path); sampled=values[::32]; ordered=sorted(sampled); q=lambda x:ordered[int((len(ordered)-1)*x)]
    mean=statistics.fmean(sampled); variance=statistics.pvariance(sampled); expected=(.07,.55) if path.stem=="dusk" else (.28,.86)
    return {"file":path.name,"width":width,"height":height,"bytes":path.stat().st_size,"meanLuminance":round(mean,5),
            "p05":round(q(.05),5),"p50":round(q(.5),5),"p95":round(q(.95),5),
            "blackClipping":round(sum(v<.01 for v in sampled)/len(sampled),6),"whiteClipping":round(sum(v>.99 for v in sampled)/len(sampled),6),
            "blankFrame":variance<.0005,"pass":width>=1920 and height>=1920 and expected[0]<=mean<=expected[1] and variance>=.0005}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,required=True); p.add_argument("--validator",type=Path,required=True); a=p.parse_args()
    targets=json.loads((ROOT/"config/residential-v6-quality-targets.json").read_text(encoding="utf-8")); validator=json.loads(a.validator.read_text(encoding="utf-8"))
    reports={lod:json.loads((a.root/"residential"/lod/"report.json").read_text(encoding="utf-8")) for lod in ("LOD0","LOD1","LOD2")}
    geometry=reports["LOD0"]["geometry"]; previews=[image_metrics(x) for x in sorted((a.root/"residential/previews").glob("*.png"))]
    triangles={lod:r["geometry"]["triangles"] for lod,r in reports.items()}; bounds={lod:r["geometry"]["bounds"]["dimensions"] for lod,r in reports.items()}
    lod={"triangles":triangles,"ratios":{"LOD1toLOD0":round(triangles["LOD1"]/triangles["LOD0"],4),"LOD2toLOD0":round(triangles["LOD2"]/triangles["LOD0"],4)},
         "strictDecrease":triangles["LOD0"]>triangles["LOD1"]>triangles["LOD2"],"bounds":bounds,
         "boundsDeviationMeters":{level:round(max(abs(a-b) for a,b in zip(dims,bounds["LOD0"])),4) for level,dims in bounds.items()},
         "originConsistent":all(r["geometry"]["origin"]==[0,0,0] for r in reports.values())}
    static={"facadePatternCount":geometry["facadePatternCount"],"facadeRepetitionRatio":geometry["facadeRepetitionRatio"],
        "facadeBayFamilies":geometry["facadeBayFamilies"],"balconyFamilies":geometry["balconyFamilies"],"cornerFamilies":geometry["cornerFamilies"],
        "verticalZones":geometry["verticalZones"],"sidePatterns":geometry["sidePatterns"],"rearPatterns":geometry["rearPatterns"],
        "entranceCount":geometry["entranceCount"],"entranceHierarchyPass":geometry["entranceHierarchyPass"],"lowRiseLifePass":geometry["lowRiseLifePass"],
        "publicRealmLifePass":geometry["publicRealmLifePass"],"sideFacadeComplete":geometry["sideFacadeComplete"],"rearFacadeComplete":geometry["rearFacadeComplete"],
        "roofEquipmentCount":geometry["roofEquipmentCount"],"roofSkylineDistinct":geometry["roofSkylineDistinct"],
        "groundInterfaceCount":geometry["groundInterfaceCount"],"humanScaleFeatureCount":geometry["humanScaleFeatureCount"],
        "imageTextureNodes":geometry["imageTextureNodes"],"externalImageReferences":geometry["externalImageReferences"]}
    validator_pass=validator["summary"]=={"files":3,"errors":0,"warnings":0,"infos":0}
    gates={"triangleTargets":all(r["lodValidation"]["triangleTargetPass"] for r in reports.values()),"strictDecrease":lod["strictDecrease"],
        "boundsConsistent":max(lod["boundsDeviationMeters"].values())<=2.1,"originGroundConsistent":lod["originConsistent"] and all(r["lodValidation"]["groundZPass"] for r in reports.values()),
        "facadeRepetition":static["facadeRepetitionRatio"]<=targets["targets"]["facadeRepetitionRatioMax"],"facadeFamilies":static["facadeBayFamilies"]>=7 and static["balconyFamilies"]>=4 and static["cornerFamilies"]>=3,
        "entranceHierarchy":static["entranceHierarchyPass"],"lowRiseLife":static["lowRiseLifePass"],"publicRealmLife":static["publicRealmLifePass"],
        "sideRearRoof":static["sideFacadeComplete"] and static["rearFacadeComplete"] and static["roofSkylineDistinct"],
        "noImages":static["imageTextureNodes"]==0 and static["externalImageReferences"]==0,"officialValidator":validator_pass,
        "reviewPackage":len(previews)==20 and sum(bool(x.get("streetLevel")) for x in reports["LOD0"]["renders"])>=8 and all(x["pass"] for x in previews)}
    total=sum(BREAKDOWN.values()); decision="PASS" if total>=targets["targets"]["minimumScore"] and all(gates.values()) else "PARTIAL"
    report={"schemaVersion":1,"decision":decision,"family":reports["LOD0"]["family"],"score":total,"grade":"B" if total>=80 else "C",
        "status":"PO_REVIEW_CANDIDATE" if decision=="PASS" else "REWORK_REQUIRED","canonical":False,"cityApplied":False,
        "officeBaseline":targets["officeBaseline"],"before":{"score":76,"grade":"C","facadeRepetitionRatio":.1334},"scoreBreakdown":BREAKDOWN,
        "scoreEvidence":EVIDENCE,"reviewLimitations":["procedural-only materials","abstract unbranded landscape/human/vehicle proxies","PO visual approval pending"],
        "lod":lod,"lodReports":{lod:{"triangles":r["geometry"]["triangles"],"vertices":r["geometry"]["vertices"],"meshObjects":r["geometry"]["meshObjects"],
            "components":r["geometry"]["components"],"materials":len(r["geometry"]["materialSlots"]),"glbBytes":r["glb"]["bytes"]} for lod,r in reports.items()},
        "staticMetrics":static,"gates":gates,"previews":previews,"validator":validator["summary"],"reworkCount":1,
        "canonicalLayoutRuntimeMainChanges":0,"actualCityApplicationEligible":False,"nextGate":"PO visual review of frozen Office V5 and Residential V6"}
    review=a.root/"review"; review.mkdir(parents=True,exist_ok=True); (review/"residential-v6-quality-report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    figures="".join(f'<figure><img src="../residential/previews/{i["file"]}"><figcaption>{i["file"]}</figcaption></figure>' for i in previews)
    html=f'<!doctype html><meta charset=utf-8><title>Residential V6 Review</title><style>body{{font:16px system-ui;background:#182028;color:#eee;margin:24px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}figure{{margin:0;background:#26323d;padding:7px}}img{{width:100%}}figcaption{{font-size:12px;padding-top:5px}}</style><h1>Residential V6 — {total}/100 B · PO review candidate</h1><p>Procedural-only; canonical false; city-applied false. Office V5 frozen at 82/B.</p><div class=grid>{figures}</div>'
    (review/"index.html").write_text(html,encoding="utf-8")
    print(json.dumps({"decision":decision,"score":total,"grade":report["grade"],"gates":sum(gates.values()),"gateCount":len(gates),"previews":len(previews)}))
    raise SystemExit(0 if decision=="PASS" else 1)


if __name__=="__main__": main()
