"""Production facade systems with independent front, side and rear rules."""
from __future__ import annotations


LOD_DETAIL = {"LOD0": 3, "LOD1": 2, "LOD2": 1}


def _window_front(batch, x, y, z, width, height, materials, lod, prefix):
    depth = 0.18 if lod == "LOD0" else 0.12
    batch.add_box(f"{prefix}-window-recess", materials["glass"], (x,y,z), (width,height*0.035, height))
    if LOD_DETAIL[lod] >= 2:
        frame = max(0.07, width*0.055)
        batch.add_box(f"{prefix}-mullion", materials["frame"], (x-width/2,y-.08,z), (frame,.14,height+.16))
        batch.add_box(f"{prefix}-mullion", materials["frame"], (x+width/2,y-.08,z), (frame,.14,height+.16))
    if LOD_DETAIL[lod] >= 3:
        frame = max(0.07, height*0.045)
        batch.add_box(f"{prefix}-transom", materials["frame"], (x,y-.08,z-height/2), (width+.12,.14,frame))
        batch.add_box(f"{prefix}-transom", materials["frame"], (x,y-.08,z+height/2), (width+.12,.14,frame))
        batch.add_box(f"{prefix}-sill", materials["accent"], (x,y+.02,z-height/2-.08), (width+.18,depth,.12))


def _window_side(batch, x, y, z, width, height, materials, lod, prefix, direction):
    batch.add_box(f"{prefix}-window-recess", materials["glass"], (x,y,z), (width*.035,width,height))
    if LOD_DETAIL[lod] >= 2:
        frame=max(.07,width*.055)
        batch.add_box(f"{prefix}-mullion",materials["frame"],(x+direction*.08,y-width/2,z),(height+.16,frame,.14))
        batch.add_box(f"{prefix}-mullion",materials["frame"],(x+direction*.08,y+width/2,z),(height+.16,frame,.14))
    if LOD_DETAIL[lod] >= 3:
        frame=max(.07,height*.045)
        batch.add_box(f"{prefix}-transom",materials["frame"],(x+direction*.08,y,z-height/2),(.14,width+.12,frame))
        batch.add_box(f"{prefix}-transom",materials["frame"],(x+direction*.08,y,z+height/2),(.14,width+.12,frame))


def residential_facades(batch, masses, lod):
    materials={"glass":"residential-glass","frame":"aluminum","accent":"precast-concrete"}
    stats={"patterns":set(),"windows":0,"balconies":0,"mullions":0,"depthRangeMeters":[.15,1.2]}
    floor_step = 1 if lod != "LOD1" else 2
    for index,mass in enumerate(masses):
        x,y,w,d,floors,floor_h,base=mass
        bays=max(5,int(w/2.1)); side_bays=max(3,int(d/2.4)); bay_w=(w-1.2)/bays; side_w=(d-1.2)/side_bays
        for floor in range(1,floors,floor_step):
            z=base+floor*floor_h+floor_h*.52
            for bay in range(bays):
                bx=x-w/2+.6+bay_w*(bay+.5)
                _window_front(batch,bx,y-d/2-.035,z,bay_w*.72,floor_h*.58,materials,lod,"res-front")
                _window_front(batch,bx,y+d/2+.035,z,bay_w*.62,floor_h*.48,materials,lod,"res-rear")
                stats["windows"]+=2
            for bay in range(side_bays):
                by=y-d/2+.6+side_w*(bay+.5)
                _window_side(batch,x-w/2-.035,by,z,side_w*.62,floor_h*.5,materials,lod,"res-side",-1)
                if bay%2==0:_window_side(batch,x+w/2+.035,by,z,side_w*.55,floor_h*.44,materials,lod,"res-core-side",1)
                stats["windows"]+=1+(bay%2==0)
            balcony_stride={"LOD0":2,"LOD1":4,"LOD2":6}[lod]
            if floor%balcony_stride==0:
                bw=w*.42; side=-1 if (floor//balcony_stride+index)%2 else 1; bx=x+side*w*.22
                batch.add_box("res-balcony-slab","precast-concrete",(bx,y-d/2-.72,z-.72),(bw,1.35,.18))
                batch.add_box("res-balcony-railing","balcony-glass",(bx,y-d/2-1.34,z-.18),(bw,.08,1.05))
                if lod=="LOD0":
                    batch.add_box("res-balcony-return","aluminum",(bx-bw/2,y-d/2-.72,z-.18),(.08,1.25,1.05))
                    batch.add_box("res-balcony-return","aluminum",(bx+bw/2,y-d/2-.72,z-.18),(.08,1.25,1.05))
                stats["balconies"]+=1
        # Core/service blind bay, slab bands, and mechanical floor are intentionally distinct.
        batch.add_box("res-core-blind-bay","dark-stone",(x+w/2+.13,y+d*.12,base+floors*floor_h*.52),(.3,d*.26,floors*floor_h*.78))
        mechanical_z=base+(floors-2)*floor_h
        batch.add_box("res-mechanical-band","light-metal-panel",(x,y-d/2-.12,mechanical_z),(w+.2,.28,.65))
        band_stride={"LOD0":3,"LOD1":5,"LOD2":7}[lod]
        for floor in range(band_stride,floors,band_stride):
            batch.add_box("res-slab-edge","precast-concrete",(x,y-d/2-.12,base+floor*floor_h),(w+.2,.26,.18))
    stats["patterns"]={"recessed-window","projected-balcony","core-blind","rear-service","mechanical-band"}
    stats["mullions"]=stats["windows"]*(2 if lod!="LOD2" else 0)
    stats["patterns"]=sorted(stats["patterns"])
    return stats


def office_facades(batch, towers, lod):
    materials={"glass":"curtain-wall-glass","frame":"aluminum","accent":"dark-metal-panel"}
    stats={"patterns":set(),"panels":0,"mullions":0,"depthRangeMeters":[.12,1.5]}
    floor_step=1 if lod!="LOD1" else 2
    for index,tower in enumerate(towers):
        x,y,w,d,floors,floor_h,base=tower
        front_bays=max(6,int(w/1.65)); side_bays=max(5,int(d/1.75)); fw=(w-.8)/front_bays; sw=(d-.8)/side_bays
        for floor in range(1,floors,floor_step):
            z=base+floor*floor_h+floor_h*.5
            for bay in range(front_bays):
                bx=x-w/2+.4+fw*(bay+.5)
                _window_front(batch,bx,y-d/2-.06,z,fw*.82,floor_h*.72,materials,lod,"office-front")
                _window_front(batch,bx,y+d/2+.06,z,fw*.74,floor_h*.62,materials,lod,"office-rear")
                stats["panels"]+=2
            for bay in range(side_bays):
                by=y-d/2+.4+sw*(bay+.5)
                _window_side(batch,x-w/2-.06,by,z,sw*.78,floor_h*.68,materials,lod,"office-side",-1)
                if bay%3!=0:_window_side(batch,x+w/2+.06,by,z,sw*.7,floor_h*.58,materials,lod,"office-service-side",1)
                stats["panels"]+=1+(bay%3!=0)
        fin_stride={"LOD0":1,"LOD1":2,"LOD2":3}[lod]
        for bay in range(0,front_bays+1,fin_stride):
            bx=x-w/2+.4+fw*bay
            batch.add_box("office-vertical-fin","dark-metal-panel",(bx,y-d/2-.42,base+floors*floor_h*.52),(.16,.72,floors*floor_h*.9))
            stats["mullions"]+=1
        for floor in range(4,floors,4 if lod!="LOD2" else 8):
            batch.add_box("office-spandrel-band","light-metal-panel",(x,y-d/2-.19,base+floor*floor_h),(w+.2,.3,.28))
        for floor in range(10,floors,12):
            z=base+floor*floor_h
            batch.add_box("office-mechanical-floor","dark-metal-panel",(x,y-d/2-.22,z),(w+.4,.38,1.1))
            batch.add_box("office-mechanical-floor","dark-metal-panel",(x,y+d/2+.22,z),(w+.4,.38,1.1))
        batch.add_box("office-rear-service-wall","granite",(x+w/2+.16,y+d*.18,base+floors*floor_h*.45),(.36,d*.3,floors*floor_h*.72))
    stats["patterns"]={"curtain-wall","recessed-bay","vertical-fin","spandrel","mechanical-floor","rear-service-wall"}
    stats["patterns"]=sorted(stats["patterns"])
    return stats
