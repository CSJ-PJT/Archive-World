"""Merge MeshBatch role buckets by material to reduce GLB draw calls."""
from collections import defaultdict
def consolidate(batch):
 merged=defaultdict(lambda:{'vertices':[],'faces':[],'components':0})
 for (_,material),bucket in batch.data.items():
  target=merged[(f'consolidated-{material}',material)];offset=len(target['vertices']);target['vertices'].extend(bucket['vertices']);target['faces'].extend(tuple(offset+i for i in face) for face in bucket['faces']);target['components']+=bucket['components']
 batch.data=merged;return {'meshBuckets':len(merged),'strategy':'one-mesh-per-material','semanticGeometryPreserved':True}
