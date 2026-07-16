# Urban Grammar V1.1 planning scenes

Residential (350m × 280m) and ArchiveOS (420m × 320m) planning scenes are external-only spatial proxies. Every building and street element is marked `PLACEHOLDER`, `PROTOTYPE`, or `GENERATED_PLAN_ONLY`; none is canonical or production-ready.

The planner proves the Urban Grammar data path: District DNA + Building Family roles + Street Family + Block rules → routes, public-space hierarchy, height distribution, metrics, and review gates.

The default V3 Viewer is unchanged. A future PLAN_ONLY viewer adapter may consume the generated `block-plan.json` files without loading them as V3 runtime manifests.

Current review gates are proxy scores, not architectural approvals. Building/Family must be improved before any block can advance to a canonical or city-layout review.
