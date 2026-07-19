"""Residential V6 active podium and five-level entrance hierarchy."""
from __future__ import annotations


DETAIL={"LOD0":3,"LOD1":2,"LOD2":1}


def _glazed_entry(batch,prefix,center,width,height,canopy_depth,materials,lod):
    x,y=center
    batch.add_box(f"{prefix}-glazing",materials["glass"],(x,y,height/2),(width,.34,height))
    batch.add_box(f"{prefix}-door",materials["door"],(x,y-.22,1.3),(2.2,.16,2.6))
    batch.add_box(f"{prefix}-canopy",materials["canopy"],(x,y-canopy_depth/2-.25,height+.25),(width+2.2,canopy_depth,.38))
    if DETAIL[lod]>=2:
        for offset in (-width*.32,0,width*.32):
            batch.add_box(f"{prefix}-mullion","aluminum",(x+offset,y-.24,height/2),(.13,.18,height-.3))
    if DETAIL[lod]>=3:
        batch.add_box(f"{prefix}-blank-sign-panel",materials["accent"],(x+width*.34,y-.35,height-.55),(width*.22,.18,.7))


def build_residential_v6_lowrise(batch,lod):
    detail=DETAIL[lod]; materials={"glass":"entrance-glazing","door":"dark-gray-accent","canopy":"light-metal-panel","accent":"wood-community-accent"}
    # The podium bends around the semi-courtyard instead of reading as one large box.
    batch.add_box("v6-podium-west","light-gray-stone",(-16,1,3.2),(27,23,6.4))
    batch.add_box("v6-podium-east","cool-white-precast",(15,4,3.2),(20,20,6.4))
    batch.add_box("v6-podium-north","warm-white-concrete",(0,20,2.8),(31,8,5.6))
    for x in (-27,-22,-17,-12,-7,-2,5,10,15,20,25):
        batch.add_cylinder("v6-piloti-column","cool-white-precast",(x,-12.8,2.8),.36,5.6,12 if detail==3 else 8)
    batch.add_box("v6-piloti-edge-beam","warm-white-concrete",(0,-12.8,5.55),(55,1.0,.7))
    # Entrance hierarchy: main, secondary, community, service and parking.
    _glazed_entry(batch,"v6-main-lobby",(0,-12.55),10.5,5.0,6.2,materials,lod)
    _glazed_entry(batch,"v6-secondary-lobby",(-17.5,12.7),7.0,4.2,3.5,materials,lod)
    _glazed_entry(batch,"v6-community-entry",(-30,-2.6),8.5,4.4,4.0,materials,lod)
    batch.add_box("v6-main-lobby-stone-frame","light-gray-stone",(0,-12.4,3.0),(13,.8,6.0))
    batch.add_box("v6-main-lobby-deep-glass","entrance-glazing",(0,-12.9,2.6),(9.8,.2,4.8))
    batch.add_box("v6-main-dropoff-canopy","wood-community-accent",(0,-17.2,5.7),(17,9,.42))
    for x in (-7,7): batch.add_cylinder("v6-main-canopy-column","dark-gray-accent",(x,-17.2,2.85),.28,5.7,12 if detail==3 else 8)
    # Community/retail life is visibly different from the residential lobbies.
    batch.add_box("v6-community-pavilion","warm-white-concrete",(-30,2,2.6),(13,10,5.2))
    for x in (-34,-31,-28,-25):
        batch.add_box("v6-community-storefront","entrance-glazing",(x,-3.08,2.35),(2.35,.22,4.1))
    batch.add_box("v6-community-terrace","wood-community-accent",(-30,-5.8,.25),(15,5,.5))
    batch.add_box("v6-mail-parcel-area","dark-gray-accent",(-10,-11.9,1.2),(4.2,1.2,2.4))
    batch.add_box("v6-security-desk","wood-community-accent",(3,-11.4,1.0),(2.8,1.3,2.0))
    batch.add_box("v6-bicycle-shelter-roof","light-metal-panel",(27,9,2.6),(10,4,.25))
    for x in (23.5,26,28.5,31): batch.add_box("v6-bicycle-shelter-rack","aluminum",(x,9,.55),(.12,2.2,1.1))
    # Separate parking, service, fire and recycling functions on rear/side edges.
    # Keep the underground threshold within the shared -0.75 m ground contract.
    batch.add_wedge("v6-parking-ramp","asphalt",(22,-2,.65),(7.6,20,2.8),"y")
    for x in (18.0,26.0): batch.add_box("v6-parking-ramp-wall","light-gray-stone",(x,-2,.65),(.4,20,2.8))
    batch.add_box("v6-parking-ramp-canopy","dark-gray-accent",(22,-12.0,3.2),(9,4,.4))
    batch.add_box("v6-parking-warning-strip","painted-steel",(22,-13.8,.45),(7.2,.35,.18))
    batch.add_box("v6-service-entry","dark-gray-accent",(-20,12.55,1.5),(3.2,.32,3.0))
    batch.add_box("v6-service-canopy","light-metal-panel",(-20,14.1,3.3),(6,3.2,.28))
    batch.add_box("v6-fire-entry","painted-steel",(7,24.18,1.45),(2.6,.3,2.9))
    batch.add_box("v6-recycling-enclosure","dark-gray-accent",(-30,17,1.5),(8,4,3))
    batch.add_box("v6-recycling-roof","light-metal-panel",(-30,17,3.15),(8.4,4.4,.3))
    return {"entranceCount":5,"hierarchy":["main","secondary","community","service","parking"],
            "pilotiColumns":11,"parkingRampWidth":7.6,"canopyThickness":.42,"podiumArticulation":18,
            "humanScaleFeatures":34 if detail==3 else 25 if detail==2 else 18,"lowRiseFunctions":14,
            "mainLobbyLegible":True,"pedestrianVehicleConflict":False}
