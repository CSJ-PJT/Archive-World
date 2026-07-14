#!/usr/bin/env node
/** Prepare the canonical, portable GLB library used by Archive City v2. */
import { cp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, relative } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const manifest = JSON.parse(await readFile(resolve(root, 'assets/manifests/archive-world-assets.json'), 'utf8')).assets;
const incoming = process.env.MESHY_INCOMING_MODELS_ROOT;
const runtimeRoot = resolve(root, 'assets/runtime/v2');
const selected = {
  'building-archiveos-2e8c32fa':'control-center', 'building-archive-15186c21':'control-center', 'building-archiveos2-a614889b':'control-center',
  'building-market-9badf3fa':'commercial', 'building-market-181c8568':'commercial',
  'building-nexus-5b2737a0':'factory', 'building-nexus-9adda402':'factory', 'building-a-2-0e6498d0':'factory', 'building-b-0da0b3c5':'factory', 'building-c-f2297019':'factory',
  'building-archive-logistics-4cd90681':'warehouse', 'building-archive-1-ea52880d':'warehouse', 'building-archive-2-2fe57f23':'warehouse',
  'building-ledger-181c8568':'bank', 'building-ledger2-ea294a50':'bank',
  'building-1-d57f1be7':'office', 'building-2-cfee9093':'office', 'building-3-3d248d87':'apartment', 'building-4-874697a4':'apartment', 'building-5-8ec67334':'apartment', 'building-6-c55667d3':'apartment', 'building-7-d09a344b':'office', 'building-8-9034e896':'office',
  'vehicle-1-a74d9cb9':'vehicle', 'vehicle-2-49e64913':'vehicle', 'vehicle-1-d7e1871c':'vehicle', 'vehicle-2-c600d4bd':'vehicle', 'vehicle-asset-535bcba9':'vehicle', 'vehicle-3-234d82b4':'vehicle',
  'road-asset-7b6c3ac5':'road', 'road-meshy-ai-divided-highway-0713093526-texture-b5202be0':'road', 'road-meshy-ai-divided-highway-0713093537-texture-bf450ac3':'road', 'road-meshy-ai-four-way-intersection-0713093554-texture-5239da66':'road',
};
const incomingAssets = {
  'road-curved-modular-90-v2':'road', 'road-elevated-ramp-straight-v1':'road', 'streetlight-traffic-signal-v1':'street-prop', 'roadside-safety-barrier-v1':'street-prop',
  'security-gate-road-lane-v1':'street-prop', 'truck-yard-parking-module-v1':'street-prop', 'power-substation-compact-v1':'environment', 'communications-tower-compact-v1':'environment',
  'container-yard-modular-v1':'environment', 'cold-storage-loading-dock-v1':'environment', 'vehicle-forklift-industrial-v1':'vehicle', 'vehicle-agv-platform-v1':'vehicle', 'vehicle-inspection-drone-v1':'vehicle',
};
if (!incoming) throw new Error('MESHY_INCOMING_MODELS_ROOT is required.');
await mkdir(resolve(runtimeRoot, 'library'), { recursive:true });
const out=[];
for (const [assetId, category] of Object.entries(selected)) {
  const source=manifest.find((a)=>a.assetId===assetId); if (!source) throw new Error(`missing manifest asset ${assetId}`);
  const path=source.lods.find((l)=>l.level===2)?.path ?? source.master; const target=resolve(runtimeRoot,'library',`${assetId}.glb`);
  await cp(resolve(root,path),target); const bytes=(await readFile(target)).length;
  out.push({assetId,category,sourcePath:path,runtimePath:relative(root,target).replaceAll('\\','/'),lodLevels:[2],checksum:createHash('sha256').update(await readFile(target)).digest('hex'),bytes,license:null,sourceNote:'Meshy source via validated optimized LOD2'});
}
for (const [assetId, category] of Object.entries(incomingAssets)) {
  const source=resolve(incoming,`${assetId}.glb`); const target=resolve(runtimeRoot,'library',`${assetId}.glb`);
  await cp(source,target); const bytes=(await readFile(target)).length;
  out.push({assetId,category,sourcePath:`incoming/${assetId}.glb`,runtimePath:relative(root,target).replaceAll('\\','/'),lodLevels:[0],checksum:createHash('sha256').update(await readFile(target)).digest('hex'),bytes,license:null,sourceNote:'Incoming generated infrastructure; canonical copy retained unchanged'});
}
await writeFile(resolve(runtimeRoot,'asset-library.json'),JSON.stringify({version:'2.0.0',assets:out},null,2)+'\n');
console.log(JSON.stringify({runtimeAssets:out.length,bytes:out.reduce((n,a)=>n+a.bytes,0)}));
