#!/usr/bin/env python3
"""Summarize measured V11 WebGL performance without converting estimates to measurements."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def index(report: dict) -> dict:
    return {item["mode"]: {key: item[key] for key in ("averageFps", "onePercentLow", "criticalFps", "drawCalls", "triangles")} for item in report["results"]}


def summarize(root: Path) -> dict:
    lod1 = read(root / "performance/lod1/viewer-performance.json")
    lod2 = read(root / "performance/lod2-optimized/viewer-performance.json")
    a, b = index(lod1), index(lod2)
    triangle_reduction = round(1 - b["day"]["triangles"] / a["day"]["triangles"], 3)
    fps_change = round(b["day"]["averageFps"] - a["day"]["averageFps"], 1)
    conclusion = "HEADLESS_MAIN_THREAD_OR_TIMER_BOUND" if triangle_reduction > .4 and fps_change < 2 else "GPU_OR_GEOMETRY_SENSITIVE"
    gates = {
        "drawCallsBelow350": max(b["day"]["drawCalls"], b["night"]["drawCalls"]) <= 350,
        "dayAverage30": b["day"]["averageFps"] >= 30,
        "nightAverage30": b["night"]["averageFps"] >= 30,
        "dayLow20": b["day"]["onePercentLow"] >= 20,
        "nightLow20": b["night"]["onePercentLow"] >= 20,
        "critical24": min(b["day"]["criticalFps"], b["night"]["criticalFps"]) >= 24,
    }
    payload = {
        "status": "PASS" if all(gates.values()) else "PARTIAL",
        "measurement": "HEADLESS_CHROME_ACTUAL_WEBGL",
        "hardwareChrome": "UNKNOWN_AUTHENTIC_SAMPLE_UNAVAILABLE",
        "lod1": a,
        "lod2Optimized": b,
        "triangleReduction": triangle_reduction,
        "dayFpsChange": fps_change,
        "bottleneckConclusion": conclusion,
        "gates": gates,
        "note": "Headless and Hardware Chrome are not interchangeable. Failed hardware capture is reported as UNKNOWN.",
    }
    atomic(root / "performance/final-performance-summary.json", payload)
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    report = summarize(args.root)
    print(json.dumps(report))
