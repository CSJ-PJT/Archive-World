from pathlib import Path
import ast

source = (Path(__file__).parent / "blender" / "urban_stream_final" /
          "support_rework_v13_integrated.py")
text = source.read_text(encoding="utf-8")
ast.parse(text)
required = (
    "_front_envelope", "_side_rear_envelope", "_deep_ground_floor",
    "integrated-front-infill", "integrated-front-jamb-return",
    "integrated-front-head-return", "integrated-front-sill-return",
    "integrated-front-centre-mullion", "integrated-front-transom",
    "integrated-front-projected-fin", "integrated-side-centre-mullion",
    "integrated-side-transom", "integrated-rear-mullion",
    "occupied-lobby-table", "occupied-lobby-chair",
    "occupied-lobby-glass-infill", "occupied-lobby-jamb-return",
    "_grammar_specific_architecture", "identity-vertical-megaframe",
    "identity-civic-portal-pier", "identity-transit-long-canopy",
    "identity-cultural-roof-lantern", '"identityComponents": identity',
    '"detachedWindowCount": 0', '"officeV5Changed": False',
    'for spec in SPECS', 'for lod in ("LOD0", "LOD1", "LOD2")',
    '"revision": 14', 'support-body-v14-metropolitan-precision.json',
)
missing = [token for token in required if token not in text]
assert not missing, missing
assert "archive-cbd-twin-atrium-pq-v5" not in text
for forbidden in ("bpy.data.images.load", "bpy.data.images.save", "Image Texture",
                  "architecture_factory_v3"):
    assert forbidden not in text, forbidden
print("support family v13 wall-first envelope contract: PASS")
