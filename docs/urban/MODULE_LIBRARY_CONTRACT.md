# Architecture Module Library Contract

The module library is a composition contract for facades, entrances, roofs, and ground interfaces. Each module records dimensions in metres, anchors, orientation, allowed scale and rotation, collision bounds, adjacency, district compatibility, LOD behavior, material slots, deterministic seed inputs, provenance, and lifecycle status.

Validation rejects duplicate IDs, missing or non-positive dimensions, invalid bounds, orphan anchors, unknown adjacency targets, incomplete LOD contracts, and missing provenance. Module boards are generated evidence only and remain outside Git. A module's presence in the catalog does not make it canonical.

Current foundation: 15 facade, 10 entrance, 8 roof, and 12 ground modules. Front, side, rear, service, roof, and ground completeness must be evaluated at the composed-building level as well.
