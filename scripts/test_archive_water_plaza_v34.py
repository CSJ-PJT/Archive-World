from pathlib import Path

source = (Path(__file__).parent / "blender" / "hero_zones" / "archive_water_plaza_v34.py").read_text(encoding="utf-8")
required = (
    "WALL_FIRST_PER_OPENING_INFILL_AND_INHABITED_PODIUM",
    "v34-facade-room-back", "v34-integrated-window-infill",
    "v34-structural-facade-pier", "v34-attached-spandrel",
    "v34-frontage-continuous-floor", "v34-frontage-continuous-ceiling",
    "v34-frontage-continuous-back", "v34-bounded-frontage-glass",
    '"detachedWindowCount": 0', '"stackedDecorativeGridCount": 0',
    'assert len(bpy.data.images) == 0', '"minimumScore": 95',
    "_occludes_camera", '"smoothOrganicObjectCount"',
    "v34-signature-lobby-glass", "v34-signature-entry-terrace",
    '"signatureProjectedLobbyCount": 2',
    "v34-interior-floor-plate", "v34-primary-depth-frame",
    "v34-signature-cafe-table", '"signatureCafeTerraceCount": 2',
    "_add_architectural_tree", '"nearFieldTreeSilhouetteCount": 3',
    "_add_signature_activity_layer", '"signatureActivityHumanCount"',
    '"signatureBicycleRackCount": 5',
    "v34-window-jamb-return", "v34-window-head-return",
    "v34-window-sill-return", '"singleFacadeGlassCardCount": 0',
    '"perOpeningInfill": True',
    "_add_mid_detail_human", '"nearFieldMidDetailHumanCount"',
    '"detail": "MID_DETAIL_NEAR_FIELD"',
    "v34-civic-island-stone-edge", "v34-civic-island-layered-planting",
    "v34-civic-forecourt-axis-inlay", '"inhabitedCivicIslandCount": 2',
    "v34-side-integrated-window-ribbon", "v34-side-ribbon-jamb",
    "v34-side-structural-floor-band", "v34-rear-integrated-service-window",
    "v34-rear-mechanical-service-band",
    "_add_chamfered_mass", "v34-tower-chamfered-structural-core",
    "v34-upper-chamfered-structural-core", '"chamferedPrimaryMassCount": 12',
)
for token in required:
    assert token in source, token
assert "bpy.data.images.load" not in source
assert "bpy.data.images.save" not in source
assert "v34-integrated-glass-field" not in source
print("archive water plaza v34 wall-first architecture contract: PASS")
