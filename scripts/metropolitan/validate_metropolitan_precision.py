#!/usr/bin/env python3
"""Validate the Generated-only all-district precision scene and WebGL evidence."""
import argparse
import json
from pathlib import Path


PNG = bytes.fromhex("89504e470d0a1a0a")


def validate(root: Path) -> dict:
    scene_path = root / "metropolitan-precision-scene.json"
    capture_path = root / "renders" / "all-districts-final" / "capture-report.json"
    errors = []
    if not scene_path.exists():
        errors.append("scene-missing")
        return {"status": "FAIL", "errors": errors}
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    if scene.get("canonical") or scene.get("v3Applied") or scene.get("runtimeMutation") or scene.get("mainMerge"):
        errors.append("protected-boundary-mutation")
    if len(scene.get("districts", [])) != 13:
        errors.append("district-count")
    if len(scene.get("instances", [])) < 3900:
        errors.append("building-count")
    if scene.get("metrics", {}).get("planningProxyRatio") != 0:
        errors.append("planning-proxy")
    if not capture_path.exists():
        errors.append("capture-report-missing")
        captures = []
    else:
        captures = json.loads(capture_path.read_text(encoding="utf-8")).get("report", [])
    expected = {(district["id"], time) for district in scene.get("districts", []) for time in ("day", "night")}
    expected |= {("full", "day"), ("full", "night")}
    actual = {(item.get("district"), item.get("time")) for item in captures}
    if expected != actual:
        errors.append("capture-coverage")
    for item in captures:
        path = capture_path.parent / item["filename"]
        if not path.exists() or path.stat().st_size < 10000 or path.read_bytes()[:8] != PNG:
            errors.append(f"invalid-capture:{item.get('filename')}")
    fps = [float(item.get("fps", 0)) for item in captures]
    draws = [int(item.get("drawCalls", 9999)) for item in captures]
    if fps and min(fps) < 30:
        errors.append("headless-fps-below-30")
    if draws and max(draws) >= 350:
        errors.append("draw-call-budget")
    report = {
        "status": "PASS" if not errors else "FAIL", "errors": errors,
        "districts": len(scene.get("districts", [])), "blocks": len(scene.get("blocks", [])),
        "buildings": len(scene.get("instances", [])), "captures": len(captures),
        "headlessFpsMin": round(min(fps), 1) if fps else None,
        "headlessFpsAverage": round(sum(fps) / len(fps), 1) if fps else None,
        "drawCallsMax": max(draws) if draws else None,
        "trianglesMax": max((int(item.get("triangles", 0)) for item in captures), default=None),
        "hardwareChrome": "UNKNOWN", "officialGlbValidator": "NOT_APPLICABLE_RUNTIME_GEOMETRY",
        "protected": {"canonical": False, "v3Applied": False, "runtimeMutation": False, "mainMerge": False},
    }
    target = root / "reports" / "metropolitan-precision-validation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    result = validate(Path(args.output_root))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
