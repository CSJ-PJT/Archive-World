"""LOD target and cross-LOD consistency contracts."""

TARGETS={
 "residential":{"LOD0":(60000,140000),"LOD1":(25000,70000),"LOD2":(8000,25000)},
 "office":{"LOD0":(80000,180000),"LOD1":(35000,90000),"LOD2":(10000,30000)},
}
DETAIL={"LOD0":3,"LOD1":2,"LOD2":1}


def validate_single(mode,lod,metrics):
    low,high=TARGETS[mode][lod]; triangles=metrics["triangles"]
    return {"lod":lod,"triangles":triangles,"target":[low,high],"triangleTargetPass":low<=triangles<=high,
            "groundZPass":abs(metrics["bounds"]["min"][2])<=.75,"originPass":metrics["origin"]==[0,0,0],
            "emptyMeshes":metrics["emptyMeshes"],"looseGeometry":metrics["looseGeometry"]}


def validate_set(mode,reports):
    tri={lod:reports[lod]["geometry"]["triangles"] for lod in ("LOD0","LOD1","LOD2")}
    boxes={lod:reports[lod]["geometry"]["bounds"] for lod in tri}
    extent=lambda b:[round(b["max"][i]-b["min"][i],3) for i in range(3)]
    base=extent(boxes["LOD0"])
    deviation={lod:max(abs(a-b) for a,b in zip(extent(boxes[lod]),base)) for lod in tri}
    return {"triangles":tri,"ratios":{"LOD1toLOD0":round(tri["LOD1"]/tri["LOD0"],4),"LOD2toLOD0":round(tri["LOD2"]/tri["LOD0"],4)},
            "strictDecrease":tri["LOD0"]>tri["LOD1"]>tri["LOD2"],"boundsDeviationMeters":deviation,
            "boundsConsistent":max(deviation.values())<=2.0,"originConsistent":all(reports[l]["geometry"]["origin"]==[0,0,0] for l in tri)}
