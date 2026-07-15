#!/usr/bin/env node
import { existsSync, readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';

const root=resolve(import.meta.dirname,'..');
const layout=JSON.parse(readFileSync(resolve(root,'assets/world/archive-city-v3-layout.json'),'utf8'));
const runtime=JSON.parse(readFileSync(resolve(root,'assets/runtime/v3/archive-city-v3-manifest.json'),'utf8'));
const fail=[];
const ids=new Set();
for(const item of layout.instances){
  if(ids.has(item.instanceId)) fail.push(`duplicate:${item.instanceId}`); ids.add(item.instanceId);
  if(!existsSync(resolve(root,item.runtimePath))) fail.push(`asset-path:${item.instanceId}`);
}
if(new Set(layout.districts).size!==7) fail.push('district-count');
const bounds=layout.geography?.worldBounds;
if(!bounds || bounds.max[0]-bounds.min[0]<10000 || bounds.max[1]-bounds.min[1]<10000) fail.push('city-extent');
const river=layout.geography?.river;
if(!river || river.shape!=='curved' || !Array.isArray(river.centerline) || river.centerline.length<8) fail.push('curved-river');
if((layout.geography?.bridges?.length??0)<3) fail.push('bridges');
if((layout.geography?.northMountains??0)<3 || (layout.geography?.eastMountains??0)<3) fail.push('mountain-coverage');
if(!layout.geography?.westSea || !layout.geography?.southPlains) fail.push('coast-or-plains');
if((layout.geography?.outerHighwayModules?.length??0)<4 || (layout.geography?.interchanges?.length??0)<2) fail.push('highway-or-ic');
const nodes=new Set(layout.roadTopology.nodes.map((node)=>node.nodeId));
for(const edge of layout.roadTopology.edges){
  if(!nodes.has(edge.from)||!nodes.has(edge.to)||edge.from===edge.to) fail.push(`edge:${edge.edgeId}`);
  if(edge.connectionStandard!=='ArchiveRoadV2-12m'||!edge.assetId) fail.push(`road-contract:${edge.edgeId}`);
  else if(!existsSync(resolve(root,'assets/runtime/v3/library',`${edge.assetId}.glb`)) && !existsSync(resolve(root,'assets/runtime/v2/library',`${edge.assetId}.glb`))) fail.push(`road-path:${edge.assetId}`);
}
const adjacency=new Map([...nodes].map((id)=>[id,new Set()]));
for(const edge of layout.roadTopology.edges){adjacency.get(edge.from)?.add(edge.to);adjacency.get(edge.to)?.add(edge.from);}
const seen=new Set(['archiveos']), queue=['archiveos']; while(queue.length){for(const next of adjacency.get(queue.shift())??[]){if(!seen.has(next)){seen.add(next);queue.push(next);}}}
for(const district of ['market','nexus','logistics','ledger','residential']) if(!seen.has(district)) fail.push(`disconnected:${district}`);
const stats=layout.statistics??{};
if((stats.totalInstances??0)<1500 || (stats.totalInstances??0)>1900) fail.push('total-density');
if((stats.buildingInstances??0)<900 || (stats.buildingInstances??0)>1150) fail.push('building-density');
if((stats.vehicleInstances??0)<140 || (stats.vehicleInstances??0)>180) fail.push('vehicle-density');
if((stats.roadModules??0)<55) fail.push('road-module-density');
if((stats.propsAndTrees??0)<350 || (stats.propsAndTrees??0)>500) fail.push('public-realm-density');
const centers=layout.geography?.districtCenters??{};
const distance=(a,b)=>Math.hypot((a?.[0]??Infinity)-(b?.[0]??-Infinity),(a?.[1]??Infinity)-(b?.[1]??-Infinity));
for(const [a,b,min] of [['archiveos','residential',500],['archiveos','market',700],['nexus','logistics',800]]) {
  if(distance(centers[a],centers[b])<min) fail.push(`district-distance:${a}-${b}`);
}
if(distance(centers.residential,centers.nexus)<1500) fail.push('district-buffer:residential-nexus');
for(const district of runtime.districts){
  for(const file of [district.runtimePath,district.previewPath,district.blendPath]) if(!existsSync(resolve(root,file))) fail.push(`district-output:${district.id}:${file}`);
  if(existsSync(resolve(root,district.runtimePath)) && statSync(resolve(root,district.runtimePath)).size>=2*1024**3) fail.push(`district-size:${district.id}`);
}
for(const file of ['city-overview.png','birds-eye-view.png','topography-overview.png']) if(!existsSync(resolve(root,'assets/previews/v3',file))) fail.push(`preview:${file}`);
console.log(JSON.stringify({layout:fail.length?'FAIL':'PASS',instances:layout.instances.length,nodes:nodes.size,edges:layout.roadTopology.edges.length,statistics:stats,failures:fail}));
process.exitCode=fail.length?1:0;
