"""Shared output-root contract for reproducible Archive World Blender builds.

The repository is an immutable source/fixture tree during an official build.
Every mutable Blender, runtime, preview, metadata, report, and Viewer artifact
is placed below the output root.  Paths written into generated manifests are
logical paths relative to that root, never machine-specific absolute paths.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OUTPUT_ROOT = "C:/ArchiveData/World/Generated"


def option(args: list[str], name: str) -> str | None:
    try:
        return args[args.index(name) + 1]
    except (ValueError, IndexError):
        return None


@dataclass(frozen=True)
class WorldOutput:
    root: Path

    @property
    def v2_runtime(self) -> Path:
        return self.root / "v2" / "runtime"

    @property
    def v2_metadata(self) -> Path:
        return self.root / "v2" / "metadata"

    @property
    def v3_runtime(self) -> Path:
        return self.root / "v3" / "runtime"

    @property
    def v3_scenes(self) -> Path:
        return self.root / "v3" / "scenes"

    @property
    def v3_previews(self) -> Path:
        return self.root / "v3" / "previews"

    @property
    def v3_renders(self) -> Path:
        return self.root / "v3" / "renders"

    @property
    def v3_metadata(self) -> Path:
        return self.root / "v3" / "metadata"

    @property
    def v3_viewer(self) -> Path:
        return self.root / "v3" / "viewer"

    @property
    def reports(self) -> Path:
        return self.root / "reports"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def cache(self) -> Path:
        return self.root / "cache"

    def ensure(self) -> None:
        for path in (
            self.v2_runtime,
            self.v2_metadata,
            self.v3_runtime,
            self.v3_scenes,
            self.v3_previews,
            self.v3_renders,
            self.v3_metadata,
            self.v3_viewer,
            self.reports,
            self.logs,
            self.cache,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def logical(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()


def resolve_output_root(args: list[str]) -> WorldOutput:
    value = option(args, "--output-root") or os.environ.get("ARCHIVE_WORLD_OUTPUT_ROOT") or DEFAULT_OUTPUT_ROOT
    output = WorldOutput(Path(value).expanduser().resolve())
    output.ensure()
    return output
