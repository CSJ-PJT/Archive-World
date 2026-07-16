#!/usr/bin/env node
/**
 * Read-only baseline analysis for visual-diversity planning.
 *
 * It never promotes or mutates an asset.  "visible" counts are explicitly a
 * layout/camera-distance proxy; render-time occlusion needs a later Blender
 * capture pass and is not represented as measured visibility here.
 */
import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const args=process.argv.slice(2);
const option=(name)=>{const index=args.indexOf(name);return index<0?undefined:args[index+1];};
const root=resolve(import.meta.dirname,'..');
const outputRoot=resolve(option('--output-root') ?? process.env.ARCHIVE_WORLD_OUTPUT_ROOT ?? 'C:/ArchiveData/World/Generated');
const reportRoot=resolve(outputRoot,'reports'); mkdirSync(reportRoot,{recursive:true});
const layout=JSON.parse(readFileSync(resolve(root,'assets/world/archive-city-v3-layout.json'),'utf8'));
const assetLibrary=JSON.parse(readFileSync(resolve(root,'assets/runtime/v3/asset-library.json'),'utf8')).assets;
const cameras={
  city:[0,0,6200], archiveos:[0,1520,2400], market:[-1900,-1500,2200], nexus:[450,-1900,2400],
  logistics:[2500,-1650,2500], ledger:[-1680,1800,2300], residential:[2200,1900,2500], infrastructure:[-3300,400,2600],
};
const sha=(bytes)=>{let hash=0;for(const value of bytes.subarray(0,Math.min(bytes.length,4096))) hash=(hash*31+value)>>>0;return hash.toString(16).padStart(8,'0');};

function glbStats(relativePath){
  const path=resolve(root,relativePath);
  if(!path || !statSync(path).size) return {error:'missing'};
  const bytes=readFileSync(path); const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  if(bytes.subarray(0,4).toString('ascii')!=='glTF') return {error:'invalid-glb'};
  let offset=12, json={};
  while(offset+8<=bytes.length){const length=view.getUint32(offset,true), type=view.getUint32(offset+4,true);offset+=8;if(type===0x4E4F534A){json=JSON.parse(bytes.subarray(offset,offset+length).toString('utf8'));break;}offset+=length;}
  const accessors=json.accessors??[], meshes=json.meshes??[], materials=json.materials??[], images=json.images??[];
  let triangles=0, min=[Infinity,Infinity,Infinity], max=[-Infinity,-Infinity,-Infinity]; const materialIds=new Set();
  for(const mesh of meshes) for(const primitive of mesh.primitives??[]){
    const accessor=accessors[primitive.indices ?? primitive.attributes?.POSITION];
    if(accessor?.count) triangles+=Math.floor(accessor.count/3);
    if(Number.isInteger(primitive.material)) materialIds.add(primitive.material);
    const position=accessors[primitive.attributes?.POSITION];
    if(position?.min&&position?.max) for(let i=0;i<3;i++){min[i]=Math.min(min[i],position.min[i]);max[i]=Math.max(max[i],position.max[i]);}
  }
  const bounds=min[0]===Infinity?null:{min,max,dimensions:min.map((value,index)=>Number((max[index]-value).toFixed(3)))};
  const textureBytes=images.reduce((sum,image)=>sum+(json.bufferViews?.[image.bufferView]?.byteLength??0),0);
  const geometrySignature=[meshes.length,Math.round(triangles/100)*100,materialIds.size,bounds?.dimensions?.map((value)=>Math.round(value/5)*5).join('x')??'none'].join(':');
  const textureSignature=[images.length,Math.round(textureBytes/65536)*65536].join(':');
  return {bytes:bytes.length,fileProbe:sha(bytes),triangles,materialCount:materials.length,usedMaterialCount:materialIds.size,textureCount:images.length,textureBytes,bounds,geometrySignature,textureSignature};
}

const instanceByAsset=new Map(assetLibrary.map((asset)=>[asset.assetId,[]]));
for(const instance of layout.instances) (instanceByAsset.get(instance.assetId) ?? instanceByAsset.set(instance.assetId,[]).get(instance.assetId)).push(instance);
const assetRows=assetLibrary.map((asset)=>{
  const instances=instanceByAsset.get(asset.assetId)??[];
  const stats=glbStats(asset.runtimePath);
  const visibleByCamera=Object.fromEntries(Object.entries(cameras).map(([id,[x,z,height]])=>[id,instances.filter((instance)=>Math.hypot(instance.position[0]-x,instance.position[2]-z)<=Math.max(1100,height*.72)).length]));
  return {assetId:asset.assetId,category:asset.category,district:asset.district??null,sourceType:asset.source??asset.sourceNote??'unknown',runtimePath:asset.runtimePath,instanceCount:instances.length,visibleByCamera, ...stats};
});
const assetById=new Map(assetRows.map((row)=>[row.assetId,row]));
const districts={};
for(const district of layout.districts){
  const buildings=layout.instances.filter((item)=>item.district===district&&['building','landmark'].includes(item.state));
  const rows=buildings.map((item)=>assetById.get(item.assetId)).filter(Boolean);
  const families=new Map(); const textures=new Map();
  for(const row of rows){families.set(row.geometrySignature,(families.get(row.geometrySignature)??0)+1);textures.set(row.textureSignature,(textures.get(row.textureSignature)??0)+1);}
  const repeated=[...families.values()].filter((count)=>count>1).reduce((sum,count)=>sum+count,0);
  const repeatedTexture=[...textures.values()].filter((count)=>count>1).reduce((sum,count)=>sum+count,0);
  districts[district]={buildingInstances:buildings.length,uniqueBuildingAssets:new Set(buildings.map((item)=>item.assetId)).size,uniqueSilhouettes:families.size,silhouetteRepeatRate:buildings.length?Number((repeated/buildings.length*100).toFixed(2)):0,textureRepeatRate:buildings.length?Number((repeatedTexture/buildings.length*100).toFixed(2)):0};
}
const top20=[...assetRows].sort((left,right)=>right.instanceCount-left.instanceCount||left.assetId.localeCompare(right.assetId)).slice(0,20).map((row)=>({assetId:row.assetId,category:row.category,instances:row.instanceCount,risk:row.instanceCount>=5?'HIGH':row.instanceCount>=3?'MEDIUM':'LOW',geometrySignature:row.geometrySignature}));
const buildingRows=assetRows.filter((row)=>(instanceByAsset.get(row.assetId)??[]).some((item)=>['building','landmark'].includes(item.state)));
const report={
  schema:'archive-world.visual-diversity-baseline/v1',
  sourceHead:option('--head')??null,
  method:{visibleCount:'layout/camera-distance proxy; not render-time occlusion',similarity:'GLB geometry/material/bounds signature; not image embedding'},
  totals:{assets:assetRows.length,instances:layout.instances.length,buildingInstances:layout.instances.filter((item)=>['building','landmark'].includes(item.state)).length,distinctBuildingAssets:buildingRows.length,averageInstancesPerAsset:Number((layout.instances.length/assetRows.length).toFixed(2))},
  top20,districts,assets:assetRows,
};
const markdown=['# Archive World Visual Diversity Baseline','','- Visibility: layout/camera-distance proxy; it is not a render-time occlusion result.','- Similarity: GLB geometry/material/bounds signature; it is not a visual embedding.','','## Most repeated assets','','|Asset|Category|Instances|Risk|','|---|---|---:|---|',...top20.map((row)=>`|${row.assetId}|${row.category}|${row.instances}|${row.risk}|`),'','## District repetition','','|District|Building instances|Unique assets|Unique silhouettes|Silhouette repeat|Texture repeat|','|---|---:|---:|---:|---:|---:|',...Object.entries(districts).map(([id,row])=>`|${id}|${row.buildingInstances}|${row.uniqueBuildingAssets}|${row.uniqueSilhouettes}|${row.silhouetteRepeatRate}%|${row.textureRepeatRate}%|`)].join('\n');
writeFileSync(resolve(reportRoot,'asset-diversity-baseline.json'),JSON.stringify(report,null,2)+'\n');
writeFileSync(resolve(reportRoot,'asset-diversity-baseline.md'),markdown+'\n');
const concepts=['courtyard','slab-a','slab-b','point-a','point-b','stepped','pair','arc','bridge','terrace','mid-court','mid-bar','mid-zig','mid-l','shop-base','villa-a','villa-b','town-row','town-corner','civic-living'];
const blocks=(kind,x,y)=>{
  const base=`<rect x="${x+14}" y="${y+92}" width="106" height="18" rx="2" fill="#697f8c"/>`;
  const tower=(dx,width,height)=>`<rect x="${x+dx}" y="${y+92-height}" width="${width}" height="${height}" rx="2" fill="#2e697d"/>`;
  if(kind==='courtyard') return `${base}${tower(22,25,68)}${tower(80,25,68)}<rect x="${x+47}" y="${y+54}" width="48" height="18" fill="#9bb857"/>`;
  if(kind.includes('slab')) return `${base}${tower(kind==='slab-a'?36:26,kind==='slab-a'?58:78,kind==='slab-a'?82:65)}<path d="M${x+24} ${y+55}h92M${x+24} ${y+70}h92" stroke="#b6d8df"/>`;
  if(kind.startsWith('point')) return `${base}${tower(46,40,88)}<rect x="${x+34}" y="${y+26}" width="64" height="20" fill="#2e697d"/>`;
  if(kind==='stepped'||kind==='terrace') return `${base}${tower(34,68,42)}${tower(45,46,66)}${tower(56,24,88)}`;
  if(kind==='pair'||kind==='bridge') return `${base}${tower(25,32,78)}${tower(78,32,64)}${kind==='bridge'?`<rect x="${x+55}" y="${y+42}" width="28" height="12" fill="#9bb857"/>`:''}`;
  if(kind==='arc') return `${base}<path d="M${x+28} ${y+90}Q${x+68} ${y+15} ${x+108} ${y+90}Z" fill="#2e697d"/>`;
  if(kind.startsWith('mid')) return `${base}${tower(24,88,48)}${kind==='mid-zig'?`<path d="M${x+24} ${y+62}l22-12 22 12 22-12 22 12" stroke="#b6d8df" fill="none"/>`:''}`;
  if(kind==='shop-base') return `${base}${tower(43,48,58)}<rect x="${x+18}" y="${y+82}" width="98" height="14" fill="#c69b56"/>`;
  if(kind.startsWith('villa')||kind.startsWith('town')) return `${base}${tower(24,28,32)}${tower(58,28,42)}${tower(92,20,28)}`;
  return `${base}${tower(35,70,54)}<rect x="${x+48}" y="${y+26}" width="44" height="16" fill="#9bb857"/>`;
};
const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="900" height="720" viewBox="0 0 900 720"><rect width="900" height="720" fill="#102027"/><text x="30" y="34" fill="#eef7f8" font-family="sans-serif" font-size="20">Residential Batch 1 · Concept Massing Sheet</text><text x="30" y="56" fill="#b6d8df" font-family="sans-serif" font-size="12">CONCEPT ONLY · NOT A MODEL · NOT MANIFEST ELIGIBLE</text>${concepts.map((kind,index)=>{const col=index%5,row=Math.floor(index/5),x=25+col*175,y=78+row*156;return `<g><rect x="${x}" y="${y}" width="150" height="138" rx="6" fill="#17313b" stroke="#49616a"/>${blocks(kind,x,y)}<text x="${x+10}" y="${y+128}" fill="#eef7f8" font-family="sans-serif" font-size="11">${String(index+1).padStart(2,'0')} · ${kind}</text></g>`;}).join('')}</svg>`;
writeFileSync(resolve(reportRoot,'residential-batch-1-concept-sheet.svg'),svg);
console.log(JSON.stringify({status:'PASS',reportRoot,assets:report.totals.assets,instances:report.totals.instances,top20,districts,conceptSheet:resolve(reportRoot,'residential-batch-1-concept-sheet.svg')}));
