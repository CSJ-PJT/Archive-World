from pathlib import Path

source = (Path(__file__).parent / "blender" / "hero_zones" / "archive_water_plaza_v34.py").read_text(encoding="utf-8")
base_source = (Path(__file__).parent / "blender" / "hero_zones" / "archive_water_plaza_v12.py").read_text(encoding="utf-8")
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
    "v35-signature-vestibule-inner-glass",
    "v35-signature-atrium-mezzanine-slab",
    "v35-signature-atrium-rear-portal",
    '"deepAtriumLobbyCount": 2', '"signatureLobbyDepthM": 10.8',
    "_add_signature_tower_civic_wing",
    "v35-signature-civic-wing-structural-body",
    "v35-signature-civic-wing-integrated-glass",
    '"signatureTowerCivicWingCount": 2',
    "v34-interior-floor-plate", "v34-primary-depth-frame",
    "v34-signature-cafe-table", '"signatureCafeTerraceCount": 2',
    "_add_architectural_tree", "_add_irregular_canopy_lobe",
    '"nearFieldTreeSilhouetteCount": 12',
    "v34-species-tree-tapered-trunk", "v34-species-tree-secondary-branch",
    "v34-species-tree-irregular-crown",
    "_add_signature_activity_layer", '"signatureActivityHumanCount"',
    '"signatureBicycleRackCount": 5',
    "v34-window-jamb-return", "v34-window-head-return",
    "v34-window-sill-return", '"singleFacadeGlassCardCount": 0',
    '"perOpeningInfill": True',
    "v34-integrated-skyroom-floor", "v34-integrated-skyroom-ceiling",
    "v34-integrated-skyroom-back", "v34-integrated-skyroom-glass",
    "v34-integrated-skyroom-side-return", "v34-integrated-skyroom-ledge",
    '"integratedSkyRoomCount"', '"featureCellsRemovedBeforeRoomBuild"',
    "_add_mid_detail_human", '"nearFieldMidDetailHumanCount"',
    '"detail": "MID_DETAIL_NEAR_FIELD"',
    "_add_seated_human", "v35-human-seated-upper-leg",
    '"seatedMidDetailHumanCount": 6',
    "v34-civic-island-stone-edge", "v35-civic-island-irregular-planting",
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
    '"coordinatedBuildingPaletteCount": 6',
    "_secondary_ground_floor_grammar", "v34-deep-public-arcade-roof",
    "v34-corner-public-room-glass", '"secondaryGroundFloorGrammarCount": 2',
    '"inhabitedArcadeCount": 2', '"cornerPublicRoomCount": 2',
    '"sidePerOpeningEnvelope": True',
    "_add_stream_civic_rooms", "v34-stream-room-water-edge-seat",
    "v34-stream-room-pergola-slat", '"programmedStreamRoomCount": len(stream_rooms)',
    '"lowerPromenadeMidDetailHumanCount": 12',
    "_add_stream_liner_architecture", "v34-liner-floor",
    "v34-liner-rear-wall", "v34-liner-side-wall",
    "v34-liner-integrated-glass", "v34-liner-window-jamb-return",
    "v34-liner-arcade-canopy", "v34-liner-entry-door",
    "v34-liner-covered-parent-connector", '"streamLinerBuildingCount"',
    "v35-liner-public-room-floor", "v35-liner-public-room-side-partition",
    "v35-liner-entry-vestibule-return", '"streamLinerDeepPublicRoomCount"',
    "_add_archive_civic_section_rebuild", "v35-archive-section-step",
    "v35-archive-accessible-ramp-lower", '"archiveCivicSectionCount"',
    "_consolidate_scene_objects_by_material",
    "GLOBAL_STATIC_ONE_MESH_PER_SEMANTIC_MATERIAL",
    '"runtimeGeometry"', '"materialBuckets"',
    "_add_occupied_setback_terraces", "v34-podium-roof-terrace-slab",
    "v34-tower-transfer-terrace-slab", '"occupiedSetbackTerraceCount": 18',
)
for token in required:
    assert token in source, token
assert "bpy.data.images.load" not in source
assert "bpy.data.images.save" not in source
assert "v34-integrated-glass-field" not in source
assert "hero-gateway-diagonal-brace" not in base_source
assert "hero-gateway-bank-marker" in base_source
assert "hero-gateway-approach-plinth" in base_source
for token in (
    "_add_metropolitan_precision_layer", "v37-archive-gateway-deck",
    "v37-cafe-terrace-paving", "v37-water-edge-planting-pocket",
    '"archiveGatewayBridge": 1', '"cafeTerraces": 2',
    '"plantedWaterEdgePockets": 6',
):
    assert token in source, token
assert 'archive-water-plaza-hero-v37.glb' in source
print("archive water plaza v37 metropolitan precision contract: PASS")
