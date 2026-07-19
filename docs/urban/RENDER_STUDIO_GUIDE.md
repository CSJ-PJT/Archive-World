# Render Studio Guide

The architectural review studio is a deterministic smoke/review environment, not a beauty-render claim. Its eight presets live in `config/render-studio-presets.json`: daylight hero, overcast material, street level, rear/service, bird view, dusk, wireframe review, and neutral turntable.

Run Blender with `scripts/blender/calibrated_render_studio.py`, then run `scripts/urban/analyze_render_studio.py` against the external output directory. A preset passes only when the PNG signature, dimensions, non-blank frame, luminance percentiles, clipping limits, occupancy, contrast, ground contact, file size, and duration contract pass. Blender's Render Result pixel array is not used for headless validation.

All output belongs under `C:/ArchiveData/World/Generated/...`. Preset contracts must remain repository-relative and contain no user-home paths.
