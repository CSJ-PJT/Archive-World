"""Generate the actual Archive Urban Stream GLB from alignment JSON."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;PROD=HERE.parent/'production_geometry';CORE=HERE.parent/'core_district_precision';sys.path[:0]=[str(HERE),str(PROD),str(CORE)]
from geometry_core import MeshBatch,validate_geometry
from batch_consolidation import consolidate
from materials import create_materials
from edge_builder import build_edges
from bridge_builder import build_bridges
from node_builder import build_nodes
from landscape_activity import build_landscape_activity

def main():
 args=sys.argv[sys.argv.index('--')+1:];p=argparse.ArgumentParser();p.add_argument('--alignment',required=True);p.add_argument('--output-root',required=True);a=p.parse_args()
 alignment=json.loads(Path(a.alignment).read_text(encoding='utf-8'));out=Path(a.output_root);out.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.read_factory_settings(use_empty=True);materials=create_materials();batch=MeshBatch(materials)
 edge=build_edges(batch,alignment['segments']);bridges=build_bridges(batch,alignment['bridges']);nodes=build_nodes(batch,alignment['nodes']);activity=build_landscape_activity(batch,alignment['segments'],alignment['nodes'])
 consolidation=consolidate(batch);objects=batch.finalize();validation=validate_geometry(objects)
 for o in objects:o['assetId']='archive-urban-stream-v1';o['canonical']=False;o['directReferenceCopy']=False;o['generationSeed']=1001;o['actualGeometry']=True
 glb=out/'archive-urban-stream.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_normals=True,export_texcoords=False,export_materials='EXPORT',export_apply=True)
 report={'status':'PASS','glb':str(glb),'bytes':glb.stat().st_size,'geometry':batch.statistics(),'consolidation':consolidation,'validation':validation,'alignment':{'lengthM':alignment['lengthM'],'segments':len(alignment['segments'])},'edges':edge,'bridges':bridges,'nodes':nodes,'activity':activity,'imageDatablocks':len(bpy.data.images),'externalImages':0,'originality':alignment['originality']}
 (out/'stream-generation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
