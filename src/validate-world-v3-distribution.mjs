#!/usr/bin/env node
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { resolve, relative } from 'node:path';
import { ensureGeneratedDirectory, generatedRoot, repositoryRoot, usingGeneratedOutput, worldPath } from './world-output.mjs';

const root=repositoryRoot;
const mib=1024**2, gib=1024**3, fail=[];
const libraries=JSON.parse(readFileSync(worldPath('v3/metadata/asset-libraries-v3.json','scenes/v3/asset-libraries-v3.json'),'utf8')).libraries;
const manifest=JSON.parse(readFileSync(worldPath('v3/metadata/archive-city-v3-manifest.json','assets/runtime/v3/archive-city-v3-manifest.json'),'utf8'));
const layout=JSON.parse(readFileSync(worldPath('v3/metadata/archive-city-v3-layout.json','assets/world/archive-city-v3-layout.json'),'utf8'));
const generatedPath=(value)=>usingGeneratedOutput?resolve(generatedRoot,value):resolve(root,value);
const walk=(folder)=>readdirSync(folder,{withFileTypes:true}).flatMap((entry)=>{const path=resolve(folder,entry.name);return entry.isDirectory()?walk(path):[path];});
const sceneRoot=worldPath('v3/scenes','scenes/v3');
const runtimeRoot=worldPath('v3/runtime','assets/runtime/v3');
const allFiles=[...walk(sceneRoot),...walk(runtimeRoot)];
const rows=allFiles.map((path)=>({path:usingGeneratedOutput?relative(generatedRoot,path).replaceAll('\\','/'):relative(root,path).replaceAll('\\','/'),bytes:statSync(path).size})).sort((a,b)=>b.bytes-a.bytes);
const isTransient=(path)=>/\.(blend1|blend2|autosave|tmp|log)$/i.test(path);
const candidates=rows.filter((row)=>!isTransient(row.path));
const excludedTransient=rows.filter((row)=>isTransient(row.path));
const blends=candidates.filter((row)=>row.path.endsWith('.blend'));
const over500=blends.filter((row)=>row.bytes>500*mib); const over2g=rows.filter((row)=>row.bytes>=2*gib);
for(const item of libraries){
  if(!existsSync(generatedPath(item.libraryPath))) fail.push(`missing-library:${item.assetId}`);
  if((item.bytes??0)>500*mib) fail.push(`library-over-500mb:${item.assetId}`);
  for(const texture of item.texturePaths??[]) if(!existsSync(generatedPath(texture))) fail.push(`missing-texture:${item.assetId}:${texture}`);
}
for(const item of layout.instances) if(!existsSync(generatedPath(item.runtimePath))) fail.push(`missing-runtime-source:${item.instanceId}`);
for(const district of manifest.districts){
  const runtime=generatedPath(district.runtimePath); if(!existsSync(runtime)) {fail.push(`missing-runtime:${district.id}`);continue;}
  const bytes=readFileSync(runtime,{encoding:null}); if(bytes.subarray(0,4).toString('ascii')!=='glTF') fail.push(`invalid-glb:${district.id}`);
}
if(!manifest.preloadPolicy || manifest.preloadPolicy.overview!=='infrastructure' || manifest.preloadPolicy.districtDetail!=='lazy') fail.push('runtime-preload-policy');
const result={distribution:fail.length?'FAIL':'PASS',outputMode:usingGeneratedOutput?'generated':'fixture',assetLibraries:libraries.length,blendFiles:blends.length,over500BlendFiles:over500,over2GiBFiles:over2g,largestFiles:candidates.slice(0,20),textureDirectoryBytes:candidates.filter((row)=>row.path.includes('/textures/')).reduce((sum,row)=>sum+row.bytes,0),excludedTransient:{files:excludedTransient.length,bytes:excludedTransient.reduce((sum,row)=>sum+row.bytes,0),largest:excludedTransient.slice(0,8)},failures:fail};
writeFileSync(usingGeneratedOutput?resolve(ensureGeneratedDirectory('reports'),'archive-city-v3-distribution-validation.json'):resolve(root,'reports/archive-city-v3-distribution-validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result)); process.exitCode=fail.length?1:0;
