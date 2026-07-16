import { readFileSync } from 'node:fs';
import { worldPath } from './world-output.mjs';

const layout=JSON.parse(readFileSync(worldPath('v3/metadata/archive-city-v3-layout.json','assets/world/archive-city-v3-layout.json'),'utf8'));
const fail=[];
const [minX,minZ]=layout.geography.worldBounds.min;
const [maxX,maxZ]=layout.geography.worldBounds.max;
const buildings=layout.instances.filter((item)=>['building','landmark'].includes(item.state));
const roads=[...layout.instances.filter((item)=>item.state==='road'),...layout.roadModules]
  .map((item)=>({x:item.position[0],z:item.position[2],id:item.instanceId??item.moduleId}));
const vehicles=layout.instances.filter((item)=>item.state==='vehicle');
let overlapPairs=0;
for(const item of layout.instances){
  const [x,y,z]=item.position;
  if(![x,y,z,item.footprintMeters].every(Number.isFinite)) fail.push(`nonfinite:${item.instanceId}`);
  if(x<minX || x>maxX || z<minZ || z>maxZ) fail.push(`outside-world:${item.instanceId}`);
  if(Math.abs(y)>0.01) fail.push(`floating-or-underground:${item.instanceId}`);
  if(!(item.footprintMeters>0)) fail.push(`missing-footprint:${item.instanceId}`);
}
for(let a=0;a<buildings.length;a++) for(let b=a+1;b<buildings.length;b++) {
  const left=buildings[a],right=buildings[b];
  if(left.district!==right.district) continue;
  const dx=left.position[0]-right.position[0], dz=left.position[2]-right.position[2];
  // A conservative circular-footprint proxy flags only clear building core
  // collisions. Roads, plazas and intentional podium adjacency are excluded.
  if(Math.hypot(dx,dz)<(left.footprintMeters+right.footprintMeters)*0.18) overlapPairs++;
}
if(overlapPairs) fail.push(`building-overlap:${overlapPairs}`);
let vehicleNearRoute=0;
for(const vehicle of vehicles){
  const nearest=Math.min(...roads.map((road)=>Math.hypot(vehicle.position[0]-road.x,vehicle.position[2]-road.z)));
  if(nearest<=850) vehicleNearRoute++;
  else fail.push(`vehicle-off-route:${vehicle.instanceId}`);
}
console.log(JSON.stringify({
  spatial:fail.length?'FAIL':'PASS',
  overlapPairs,
  groundAligned:layout.instances.length,
  vehicleNearRoute,
  vehicles:vehicles.length,
  proxy:'layout-footprint and route-distance validation',
  failures:fail,
}));
process.exitCode=fail.length?1:0;
