#!/usr/bin/env node
import { existsSync, readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
const root=resolve(import.meta.dirname,'..');
const layout=JSON.parse(readFileSync(resolve(root,'assets/world/archive-city-v2-layout.json'),'utf8'));
const runtime=JSON.parse(readFileSync(resolve(root,'assets/runtime/v2/archive-city-v2-manifest.json'),'utf8'));
const ids=new Set(), nodes=new Set(layout.roadTopology.nodes.map((n)=>n.nodeId)); const failures=[];
for(const i of layout.instances){if(ids.has(i.instanceId))failures.push(`duplicate:${i.instanceId}`);ids.add(i.instanceId);if(!existsSync(resolve(root,i.runtimePath)))failures.push(`path:${i.runtimePath}`);}
for(const e of layout.roadTopology.edges){if(!nodes.has(e.from)||!nodes.has(e.to)||e.from===e.to)failures.push(`edge:${e.edgeId}`);}
for(const d of runtime.districts){if(!existsSync(resolve(root,d.runtimePath))||!existsSync(resolve(root,d.previewPath)))failures.push(`district:${d.id}`);if(statSync(resolve(root,d.runtimePath)).size>=2*1024**3)failures.push(`lfs-size:${d.id}`);}
if(new Set(layout.districts).size!==7)failures.push('district-count');
console.log(JSON.stringify({layout:failures.length?'FAIL':'PASS',instances:layout.instances.length,nodes:nodes.size,edges:layout.roadTopology.edges.length,districts:runtime.districts.length,failures}));
process.exitCode=failures.length?1:0;
