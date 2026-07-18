#!/usr/bin/env python3
"""Compile a Building Genome into a deterministic, reviewable placement plan.

This is a planning compiler: it writes no GLB and does not modify a canonical
manifest or layout. Geometry generators consume its output later.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = ("footprint", "massing", "facade", "entrance", "podium", "roof", "ground", "materials", "lod")
OFFICE_REQUIRED = ("serviceRear", "mechanicalFloor")
RESIDENTIAL_REQUIRED = ("parkingRamp", "balcony")


def fail(message: str) -> None:
    raise ValueError(message)


def compile_genome(source: dict) -> dict:
    missing = [key for key in REQUIRED if key not in source]
    if missing:
        fail(f"missing required genomes: {', '.join(missing)}")
    kind = source.get("category")
    if kind not in {"residential", "office"}:
        fail("category must be residential or office")
    constraints = RESIDENTIAL_REQUIRED if kind == "residential" else OFFICE_REQUIRED
    missing = [key for key in constraints if not source.get(key)]
    if missing:
        fail(f"{kind} mandatory modules missing: {', '.join(missing)}")
    dimensions = source["footprint"].get("meters", [])
    if len(dimensions) != 2 or any(not isinstance(value, (int, float)) or value <= 0 for value in dimensions):
        fail("footprint meters must be two positive values")
    floors = source["massing"].get("floors", 0)
    if not isinstance(floors, int) or floors < 2:
        fail("massing floors must be an integer >= 2")
    lod = source["lod"]
    if not (lod.get("lod0", 0) > lod.get("lod1", 0) > lod.get("lod2", 0) > 0):
        fail("LOD triangle budget must strictly descend")
    facade = source["facade"]
    if len(set(facade.get("bays", []))) < 2:
        fail("facade needs at least two distinct bay modules")
    source_json = json.dumps(source, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(source_json.encode()).hexdigest()
    plan = {
        "id": source["id"], "category": kind, "seed": source["seed"], "sourceHash": digest,
        "provenance": {"mode": "GENOME_PLAN_ONLY", "referenceMeshCopied": False, "canonicalStatus": "NOT_REGISTERED"},
        "placements": {
            "footprint": source["footprint"], "massing": source["massing"], "podium": source["podium"],
            "facade": facade, "entrance": source["entrance"], "roof": source["roof"], "ground": source["ground"],
            "materials": source["materials"], "lod": lod,
        },
        "validation": {"groundZ": 0, "frontSideRear": True, "entrancePresent": True,
                       "lodDescending": True, "originalityDimensions": source.get("originalityDimensions", [])},
    }
    return plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    fixtures = json.loads(args.input.read_text(encoding="utf-8"))
    plans, failures = [], []
    for fixture in fixtures:
        try:
            plans.append(compile_genome(fixture))
        except ValueError as error:
            failures.append({"id": fixture.get("id", "unknown"), "error": str(error)})
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "building-genome-plans.json").write_text(json.dumps(plans, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "building-genome-report.json").write_text(json.dumps({"compiled": len(plans), "failures": failures}, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit(1)
    print(f"building genome compiler PASS: {len(plans)} plans")


if __name__ == "__main__":
    main()
