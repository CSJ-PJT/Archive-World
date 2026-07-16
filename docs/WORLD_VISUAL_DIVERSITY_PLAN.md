# Archive City visual diversity production plan

This plan is for non-identifying, Seoul-capital-region-inspired urban form. It
does not reproduce a particular building, logo, sign, or copyrighted model.
Colour alone never creates a new family. Every accepted family has distinct
footprint, massing, facade rhythm, roof/mechanical geometry, and metadata.

## Targets and acceptance

|Area|Minimum families|Primary visual rules|
|---|---:|---|
|Residential|30|tower, slab, mixed-use, villa, townhouse; height and balcony variation|
|CBD / ArchiveOS / Ledger|30|landmark, office, financial, civic; stepped/tapered/twin/podium forms|
|Market / Commercial|25|mall, retail street, hotel, culture, neighbourhood commerce|
|Nexus Industrial|25|assembly, research, utility, tank, silo, substation, office|
|Logistics / Port|25|cross-dock, cold store, fulfilment, warehouse, terminal, yard|
|Civic / Education / Health|20|school, campus, hospital, emergency, library, data/telecom|
|Infrastructure / Environment|30|bridges, stations, portals, utility, water, park, noise/barrier|

The final city target is 120–180 verified unique models, with at least 60
distinct building families. Major cameras should show a single building no
more than three times; CBD, Residential, Industrial, and Logistics should
remain below 15% repeated silhouette exposure.

## Existing previews and approved improvement targets

The current fourteen previews remain the asset-overview baseline. They are not
evidence that the diversity target is already met. The next visual pass must
preserve their subject matter while adding the following measurable context.

|Current preview group|Current baseline limitation|Approved next target|
|---|---|---|
|`city-overview`, `birds-eye-view`|Repeated tower/slab silhouettes dominate the city read.|City Hero View at 65–75% city occupancy and an additional 55–70 degree aerial view, with diverse district massing visible.|
|`archiveos-overview`, `ledger-overview`|Few office-family silhouettes make the CBD and financial core read alike.|Separate landmark, office, financial and civic families; retain an Asset Overview and add a District Context view for each district.|
|`residential-overview`|A small set of residential slabs creates obvious repetition.|Twenty reviewed Residential Batch 1 candidates, then a minimum of 30 residential families with varied plan, podium, balcony and roof geometry.|
|`market-overview`|Commercial blocks lack a distinct street and loading pattern.|Low-rise retail street, mall, hotel, culture and neighbourhood-commercial families with pedestrian and service context.|
|`nexus-overview`, `logistics-overview`|Industrial and logistics buildings repeat warehouse silhouettes.|Separate plant, research, utility, cross-dock, cold-store, terminal and yard forms; show truck/service circulation in context.|
|`han-river-bridges-overview`, `west-sea-port-overview`, `infrastructure-overview`|Infrastructure reads as isolated props instead of a connected system.|Bridge, port, station, utility and waterside families connected to roads, blocks and shore conditions.|
|`north-east-mountains-overview`, `south-plains-overview`, `topography-overview`|Terrain is visible but the adjoining urban edge has limited block logic.|Context cameras that show terrain-to-city transitions, road access, parks and appropriate low/high-density land use.|

Before any new family is registered, its contact sheet and geometry-signature
review must show a form difference beyond colour or a renamed duplicate.

## Production gate

Each batch is independently reviewed before the next begins. Its external
report must include preview/contact sheet, triangle/material/texture data,
GLB validation, ground alignment, geometry-signature duplicate review,
license/source record, and canonical acceptance decision.

1. Residential: 20 candidates.
2. CBD / Financial: 20 candidates.
3. Industrial / Logistics: 25 candidates.
4. Market / Civic: 20 candidates.
5. Infrastructure: 20 candidates.

Procedural families are seeded and retain footprint, floor count, podium,
facade grid, balcony, entrance, roof plant, and LOD metadata. Existing GLB
reuse is limited to separated districts and ±15% scale variation. Incoming
assets require explicit source/license metadata and review before canonical
promotion.

## Camera and performance plan

Every district receives an Asset Overview and a District Context camera. The
next approved pass adds seven context images, at least ten street-level images,
and a contact sheet while retaining the existing fourteen previews. Geometry
is evaluated with LOD, instancing, frustum/distance culling, atlas reuse, and
lazy district loading. FPS and memory targets are reported only from measured
results, never estimates.
