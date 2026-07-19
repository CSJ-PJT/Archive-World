"""Purpose-specific roof and mechanical geometry."""


def residential_roofs(batch, masses, lod):
    detail={"LOD0":3,"LOD1":2,"LOD2":1}[lod]; equipment=0
    for index,(x,y,w,d,floors,floor_h,base) in enumerate(masses):
        top=base+floors*floor_h
        # Four parapet edges preserve the roof outline at every LOD.
        for cx,cy,dx,dy in ((x,y-d/2,w,.3),(x,y+d/2,w,.3),(x-w/2,y,.3,d),(x+w/2,y,.3,d)):
            batch.add_box("res-roof-parapet","precast-concrete",(cx,cy,top+.55),(dx,dy,1.1))
        batch.add_box("res-machine-room","light-metal-panel",(x+w*.12,y,top+2.8),(w*.42,d*.42,5.6)); equipment+=1
        batch.add_box("res-hvac-screen","dark-metal-panel",(x-w*.22,y+d*.18,top+1.6),(w*.28,d*.22,3.2)); equipment+=1
        if detail>=2:
            batch.add_box("res-maintenance-walkway","sidewalk-concrete",(x,y-d*.28,top+.15),(w*.62,1.1,.3)); equipment+=1
            for solar in range(2 if detail==2 else 4):
                batch.add_box("res-solar-panel","dark-metal-panel",(x-w*.25+solar*w*.16,y+d*.28,top+.65),(w*.12,d*.2,.16),-.18); equipment+=1
        if detail==3:
            batch.add_box("res-service-enclosure","painted-steel",(x+w*.28,y-d*.2,top+1.1),(w*.18,d*.18,2.2)); equipment+=1
    return {"equipmentCount":equipment,"parapetEdges":len(masses)*4,"skylineArticulation":len(masses)*2}


def office_roofs(batch, towers, lod):
    detail={"LOD0":3,"LOD1":2,"LOD2":1}[lod]; equipment=0
    for index,(x,y,w,d,floors,floor_h,base) in enumerate(towers):
        top=base+floors*floor_h
        for cx,cy,dx,dy in ((x,y-d/2,w,.35),(x,y+d/2,w,.35),(x-w/2,y,.35,d),(x+w/2,y,.35,d)):
            batch.add_box("office-roof-parapet","limestone",(cx,cy,top+.7),(dx,dy,1.4))
        crown_h=9 if index==0 else 5.5
        batch.add_box("office-crown","light-metal-panel",(x,y,top+crown_h/2),(w*.72,d*.72,crown_h)); equipment+=1
        batch.add_box("office-machine-room","dark-metal-panel",(x+w*.2,y-d*.15,top+2.0),(w*.3,d*.35,4)); equipment+=1
        for unit in range(3 if detail==3 else 2 if detail==2 else 1):
            batch.add_box("office-hvac-unit","painted-steel",(x-w*.25+unit*w*.2,y+d*.25,top+.9),(w*.13,d*.18,1.8)); equipment+=1
        if detail>=2:
            batch.add_box("office-maintenance-walkway","sidewalk-concrete",(x,y-d*.3,top+.14),(w*.7,1.0,.28)); equipment+=1
        # The communications silhouette is retained in every LOD; only radial detail changes.
        batch.add_cylinder("office-communications-proxy","aluminum",(x,y,top+crown_h+3),.18,6,10 if detail==3 else 8 if detail==2 else 6); equipment+=1
        if detail==3:
            batch.add_box("office-hvac-screen","dark-metal-panel",(x-w*.28,y+d*.2,top+1.4),(w*.22,d*.25,2.8)); equipment+=1
    return {"equipmentCount":equipment,"parapetEdges":len(towers)*4,"crownVariants":len(towers)}
