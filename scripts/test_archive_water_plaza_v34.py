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
    "v34-side-integrated-opening-infill", "v34-side-opening-jamb-return",
    "v34-side-opening-head-return", "v34-side-opening-sill-return",
    "v34-side-structural-pier", "v34-side-structural-floor-band",
    "v34-rear-integrated-service-window",
    "v34-rear-mechanical-service-band",
    "_add_chamfered_mass", "v34-tower-chamfered-structural-core",
    "v34-upper-chamfered-structural-core", '"chamferedPrimaryMassCount": 12',
    "v34-institutional-vertical-fin", "v34-horizontal-terrace-band",
    "v34-civic-portal-megaframe", '"distinctFacadeGrammarCount": 3',
    "v34-facade-to-body-corner-return", '"facadeBodyCornerReturnCount": 24',
    "v34-archive-crown-service-volume", "v34-ledger-roof-terrace",
    "v34-civic-roof-lantern-interior", '"distinctRoofGrammarCount": 3',
    "_secondary_ground_floor_grammar", "v34-deep-public-arcade-roof",
    "v34-corner-public-room-glass", '"secondaryGroundFloorGrammarCount": 2',
    '"inhabitedArcadeCount": 2', '"cornerPublicRoomCount": 2',
    '"sidePerOpeningEnvelope": True',
    "_add_stream_civic_rooms", "v34-stream-room-water-edge-seat",
    "v34-stream-room-pergola-slat", '"programmedStreamRoomCount": len(stream_rooms)',
    '"lowerPromenadeMidDetailHumanCount": 12',
    "_add_occupied_setback_terraces", "v34-podium-roof-terrace-slab",
    "v34-tower-transfer-terrace-slab", '"occupiedSetbackTerraceCount": 18',
)
for token in required:
    assert token in source, token
assert "bpy.data.images.load" not in source
assert "bpy.data.images.save" not in source
assert "v34-integrated-glass-field" not in source
print("archive water plaza v34 wall-first architecture contract: PASS")
