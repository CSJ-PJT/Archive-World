"""Create canonical, external Blender libraries for Archive City v3 assets.

Each library owns one GLB asset and its extracted relative textures. District
scenes only link these collections; they never embed the same mesh/image data.
The script is deterministic and does not write to v2 or Meshy source paths.
"""
import bpy, json, re, sys
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
repo=Path(args[args.index('--repo')+1]).resolve() if '--repo' in args else Path.cwd()
assets=json.loads((repo/'assets/runtime/v3/asset-library.json').read_text(encoding='utf8'))['assets']
library_root=repo/'scenes/v3/libraries'; texture_root=repo/'assets/runtime/v3/textures'
library_root.mkdir(parents=True,exist_ok=True); texture_root.mkdir(parents=True,exist_ok=True)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def safe(value):
    return re.sub(r'[^a-zA-Z0-9_.-]+','-',value).strip('-') or 'image'

def move_imported_to_collection(asset_id):
    collection=bpy.data.collections.new('ASSET_'+asset_id)
    bpy.context.scene.collection.children.link(collection)
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(repo/asset['runtimePath']))
    imported=[obj for obj in bpy.data.objects if obj not in before]
    for obj in imported:
        for old in list(obj.users_collection): old.objects.unlink(obj)
        collection.objects.link(obj)
    points=[]
    for obj in imported:
        if obj.type=='MESH': points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if points:
        low=Vector((min(point.x for point in points),min(point.y for point in points),min(point.z for point in points)))
        high=Vector((max(point.x for point in points),max(point.y for point in points),max(point.z for point in points)))
        center=(low+high)/2
        # Canonical asset origin: footprint centre at z=0. This is the same
        # placement contract used by the former direct GLB importer.
        for obj in imported:
            if obj.parent is None: obj.location-=Vector((center.x,center.y,low.z))
    return collection

def extract_textures(asset_id):
    target=texture_root/asset_id; target.mkdir(parents=True,exist_ok=True)
    exported=[]
    for index,image in enumerate(bpy.data.images):
        suffix='.png'
        file=target/f'{index:03d}-{safe(image.name)}{suffix}'
        try:
            # glTF imports expose embedded images as packed datablocks that can
            # report has_data=False. Unpack them first; skipping on has_data
            # would silently retain the embedded image in every Blend library.
            if image.packed_file:
                # Blender's WRITE_LOCAL places packed textures in a `textures/`
                # directory next to the Blend and derives the filename from the
                # datablock name. Give every asset/image a stable unique name so
                # libraries never overwrite each other's Image_0.jpg files.
                image.name=f'{asset_id}-{index:03d}'
                image.filepath=''
                image.unpack(method='WRITE_LOCAL')
                external_root=library_root/'textures'
                candidates=sorted(external_root.glob(f'{safe(image.name)}.*'))
                actual=candidates[-1] if candidates else file
                image.filepath=bpy.path.relpath(str(actual))
                exported.append(str(actual.relative_to(repo)).replace('\\','/'))
                continue
            if not image.has_data: continue
            image.filepath=bpy.path.relpath(str(file))
            image.filepath_raw=str(file)
            image.filepath_raw=str(file)
            image.file_format='PNG'
            image.save()
            image.filepath=bpy.path.relpath(str(file))
            exported.append(str(file.relative_to(repo)).replace('\\','/'))
        except RuntimeError as error:
            # Procedural or already external images may not expose pixels. Keep
            # their source link rather than packing a duplicate into the Blend.
            image.pack(as_png=False) if False else None
            print(f'TEXTURE_WARNING asset={asset_id} image={image.name} error={error}')
    return exported

written=[]
for asset in assets:
    asset_id=asset['assetId']; source=repo/asset['runtimePath']; output=library_root/f'{asset_id}.blend'
    if not source.exists(): raise RuntimeError(f'missing asset runtime: {source}')
    reset()
    collection=move_imported_to_collection(asset_id)
    bpy.context.scene['assetId']=asset_id
    bpy.context.scene['sourceRuntimePath']=asset['runtimePath']
    bpy.context.preferences.filepaths.use_relative_paths=True
    bpy.ops.wm.save_as_mainfile(filepath=str(output),check_existing=False)
    # Blender can only reliably clear GLB packed image data after the target
    # Blend has a filepath. Save once, materialize images, then save again.
    textures=extract_textures(asset_id)
    bpy.context.scene['texturePaths']=json.dumps(textures)
    bpy.ops.wm.save_as_mainfile(filepath=str(output),check_existing=False)
    written.append({'assetId':asset_id,'libraryPath':str(output.relative_to(repo)).replace('\\','/'),'texturePaths':textures,'bytes':output.stat().st_size})

(repo/'scenes/v3/asset-libraries-v3.json').write_text(json.dumps({'version':'3.1.0','libraries':written},indent=2)+'\n',encoding='utf8')
print(json.dumps({'assetLibraries':'PASS','count':len(written),'maxBytes':max((item['bytes'] for item in written),default=0)}))
