"""Verify v3 Blend files can resolve only repository-relative linked resources."""
import bpy, json, sys
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
repo=Path(args[args.index('--repo')+1]).resolve() if '--repo' in args else Path.cwd()
targets=[repo/'scenes/archive-city-v3.blend']+sorted((repo/'scenes/v3').glob('*.blend'))
fail=[]; records=[]
for target in targets:
    bpy.ops.wm.open_mainfile(filepath=str(target))
    libraries=[]
    for library in bpy.data.libraries:
        # Library file paths are relative to the currently opened Blend, not
        # to the library itself. Passing library= here incorrectly adds a
        # second `v3/` segment for master-scene dependencies.
        resolved=Path(bpy.path.abspath(library.filepath)).resolve()
        valid=resolved.exists() and (resolved==repo or repo in resolved.parents)
        libraries.append({'path':str(resolved.relative_to(repo)).replace('\\','/') if valid else str(resolved),'valid':valid})
        if not valid: fail.append(f'broken-library:{target.name}:{library.filepath}')
    packed=[]; images=[]
    for image in bpy.data.images:
        if image.packed_file: packed.append(image.name)
        if image.source=='FILE' and image.filepath:
            resolved=Path(bpy.path.abspath(image.filepath,library=image.library)).resolve()
            valid=resolved.exists() and (resolved==repo or repo in resolved.parents)
            images.append({'path':str(resolved.relative_to(repo)).replace('\\','/') if valid else str(resolved),'valid':valid})
            if not valid: fail.append(f'broken-image:{target.name}:{image.name}')
    if packed: fail.extend(f'packed-image:{target.name}:{name}' for name in packed)
    records.append({'blend':str(target.relative_to(repo)).replace('\\','/'),'libraries':libraries,'packedImages':packed,'images':images})
report={'blendLinks':'PASS' if not fail else 'FAIL','records':records,'failures':fail}
(repo/'reports/archive-city-v3-blend-link-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print('V3_BLEND_LINKS='+json.dumps({'status':report['blendLinks'],'files':len(records),'failures':len(fail)}))
if fail: raise RuntimeError(';'.join(fail[:8]))
