# Architecture Factory V2

Incoming GLB files are reference-only. The factory does not split, import, copy, or combine reference mesh or texture data into generated buildings.

`architecture-grammar/references/` contains building-rule JSON only: massing, facade rhythm, balcony logic, core, roof, side treatment, material language, and density. It deliberately contains no vertices, mesh statistics, texture data, dimensions, or source geometry.

The generator composes grammar IDs through these modules: Footprint, Tower, Podium, Facade, Balcony, Core, Roof, Entrance, Material Composer, LOD, and Metadata.

Generated output is never committed before approval:

`C:\\ArchiveData\\World\\Generated\\Factory\\Buildings\\<family>\\{LOD,Metadata,Preview,Textures}`

For every derived family, the originality contract requires at least seven changes across footprint, height, floor count, podium, facade, balcony, roof, core, material composition, entrance, window grid, and silhouette. Simple scaling, recoloring, texture substitution, reference mesh reuse, and canonical/layout registration are prohibited in Phase 1.
