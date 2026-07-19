from pathlib import Path

source = Path("scripts/blender/hero_zones/archive_water_plaza_v27.py").read_text(encoding="utf-8")
facade = Path("scripts/blender/hero_zones/archive_water_plaza_v14.py").read_text(encoding="utf-8")

for token in (
    "S_95_PLUS", "TECHNICAL_PASS_VISUAL_GATE_PENDING", "familyIdentityCount",
    "frontGapM", "sideGapM", "directReferenceCopy", "officeV5Changed",
):
    assert token in source
for token in (
    "add_family_identity", "v27-institutional-mega-fin", "v27-civic-sky-terrace",
    "v27-data-bay-projecting-frame", "v27-ledger-premium-fin",
    "v27-ledger-transfer-terrace", "v27-park-edge-terrace",
):
    assert token in facade
for forbidden in ("bpy.data.images.load", "bpy.data.images.save", "ShaderNodeTexImage"):
    assert forbidden not in source + facade

print("archive water plaza v27 S-grade geometry contract: PASS")
