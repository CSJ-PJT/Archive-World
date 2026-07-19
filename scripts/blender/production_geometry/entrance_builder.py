"""Human-scale residential and office entrance/podium systems."""


def residential_entrance(batch, lod):
    detail = {"LOD0":3,"LOD1":2,"LOD2":1}[lod]
    # Active podium and a genuinely open piloti rhythm expressed by columns and beams.
    batch.add_box("res-podium-core","dark-stone",(0,1,3.0),(38,24,6.0))
    for x in (-15,-10,-5,0,5,10,15):
        batch.add_cylinder("res-piloti-column","precast-concrete",(x,-13,2.7),.38,5.4,12 if detail==3 else 8)
    batch.add_box("res-piloti-beam","precast-concrete",(0,-13,5.45),(34,1.0,.7))
    batch.add_box("res-lobby-glazing","residential-glass",(0,-12.55,2.6),(9,.28,4.8))
    batch.add_box("res-lobby-frame","aluminum",(0,-12.78,5.0),(10,1.1,.32))
    batch.add_box("res-entry-canopy","light-metal-panel",(0,-15.4,5.2),(13,5.6,.34))
    batch.add_box("res-entry-door","dark-metal-panel",(0,-12.82,1.25),(2.2,.18,2.5))
    batch.add_box("res-security-desk","wood-accent",(3,-11.8,1.0),(2.2,1.0,2.0))
    # Parking ramp is dimensional rather than a painted rectangle.
    batch.add_wedge("res-parking-ramp","asphalt",(17,-5,-.6),(7.2,18,2.4),"y")
    batch.add_box("res-ramp-wall","precast-concrete",(13.25,-5,.65),(.35,18,2.5))
    batch.add_box("res-ramp-wall","precast-concrete",(20.75,-5,.65),(.35,18,2.5))
    batch.add_box("res-parking-header","dark-stone",(17,-14.0,2.2),(8.0,.5,1.2))
    batch.add_box("res-service-entry","dark-metal-panel",(-19,6,1.3),(.3,3.0,2.6))
    batch.add_box("res-fire-entry","painted-steel",(-8,12.2,1.25),(2.2,.25,2.5))
    # Community pavilion and courtyard pergola make the active base legible as a residential complex.
    batch.add_box("res-community-pavilion","precast-concrete",(-25,5,2.4),(10,8,4.8))
    batch.add_box("res-community-glazing","residential-glass",(-25,.85,2.3),(7,.25,3.8))
    batch.add_box("res-community-canopy","light-metal-panel",(-25,-1.1,4.6),(9,4,.28))
    if detail>=2:
        for x in (-12,-8,-4,4,8,12):
            batch.add_cylinder("res-courtyard-pergola-column","precast-concrete",(x,13,1.5),.18,3,8)
        batch.add_box("res-courtyard-pergola","wood-accent",(0,13,3.2),(28,3,.24))
    if detail>=2:
        for x in (-4,-2,2,4): batch.add_box("res-lobby-mullion","aluminum",(x,-12.75,2.7),(.12,.22,4.5))
    return {"entranceCount":4,"pilotiColumns":7,"parkingRampWidth":7.2,"canopyThickness":.34,
            "humanScaleFeatures":16 if detail==3 else 11,"podiumArticulation":11}


def office_entrance(batch, lod):
    detail={"LOD0":3,"LOD1":2,"LOD2":1}[lod]
    batch.add_box("office-podium-core","limestone",(0,1,7.0),(54,34,14.0))
    batch.add_box("office-atrium-volume","curtain-wall-glass",(0,-16.2,7.0),(18,.7,12.0))
    batch.add_box("office-atrium-crown","light-metal-panel",(0,-16.5,13.2),(19,1.2,.55))
    batch.add_box("office-main-door","dark-metal-panel",(0,-16.65,1.7),(3.6,.22,3.4))
    batch.add_box("office-dropoff-canopy","light-metal-panel",(0,-21.0,7.0),(24,9.0,.48))
    for x in (-10,-5,5,10): batch.add_cylinder("office-canopy-column","granite",(x,-21,3.5),.32,7.0,12 if detail==3 else 8)
    # Storefront rhythm gives the podium a public face rather than one large box.
    for x in range(-23,24,5):
        batch.add_box("office-storefront","curtain-wall-glass",(x,-16.35,4.0),(3.8,.35,6.5))
        if detail>=2: batch.add_box("office-storefront-frame","aluminum",(x+2.05,-16.58,4),(.15,.25,7))
    batch.add_wedge("office-parking-ramp","asphalt",(20,-3,-.5),(8.0,20,2.6),"y")
    batch.add_box("office-parking-wall","granite",(15.8,-3,.8),(.4,20,2.8))
    batch.add_box("office-parking-wall","granite",(24.2,-3,.8),(.4,20,2.8))
    batch.add_box("office-loading-bay","dark-metal-panel",(-27,9,2.2),(.45,7,4.4))
    batch.add_box("office-service-door","painted-steel",(-20,18.2,1.6),(3.2,.3,3.2))
    batch.add_box("office-loading-canopy","dark-metal-panel",(-22,16.5,4.8),(11,5,.35))
    if detail>=2:
        for x in (-7,-3.5,0,3.5,7): batch.add_box("office-atrium-mullion","aluminum",(x,-16.62,7),(.16,.18,11.5))
        for z in (3.5,7,10.5): batch.add_box("office-atrium-transom","aluminum",(0,-16.63,z),(17,.18,.16))
    for x in range(-12,13,3): batch.add_cylinder("office-security-bollard","dark-metal-panel",(x,-26,.65),.16,1.3,8)
    return {"entranceCount":5,"storefrontBays":10,"canopyColumns":4,"parkingRampWidth":8.0,
            "humanScaleFeatures":18 if detail==3 else 12,"podiumArticulation":13}
