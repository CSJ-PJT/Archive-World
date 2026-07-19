# Pilot Generation Guide

`scripts/blender/generate_quality_pilot_lod2.py` produces two procedural-only LOD2 smoke pilots. Run grammar, module, material, and no-image checks before Blender export. LOD2 is generated before any expensive LOD0 attempt.

Required outputs are the GLB, neutral/daylight/wireframe smoke images, a generation report, and a separate official-validator report. Static metrics cover objects, proxy triangles, materials, modules, facade patterns, entrances, service access, roof equipment, ground contact, bounds, scale, and origin.

The current smoke geometry is explicitly not production-ready. Static scorecards remain `PROVISIONAL_STATIC_ONLY`; A/B visual grades require human review of production-resolution LOD0/LOD1/LOD2 evidence.
