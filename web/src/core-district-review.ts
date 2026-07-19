import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {mergeGeometries} from 'three/examples/jsm/utils/BufferGeometryUtils.js';

type Family={id:string;status:string;lod:Record<string,string>};
type Instance={familyId:string;position:[number,number,number];rotationY:number;scale:number;chunk:string};
type Manifest={status:string;badges:string[];families:Family[];instances:Instance[];blocks:{id:string;type:string}[];infrastructure:{uri:string};urbanStream?:{uri:string;lengthM:number;bridges:number;accessPoints:number};metrics:Record<string,number>};
type CameraPreset={name:string;position:[number,number,number];target:[number,number,number]};

const cameras:CameraPreset[]=[
 {name:'aerial-core',position:[740,570,790],target:[0,55,0]},
 {name:'archive-plaza',position:[0,14,520],target:[0,28,0]},
 {name:'ledger-boulevard',position:[-470,65,500],target:[-120,28,60]},
 {name:'office-v5-approach',position:[540,100,420],target:[150,35,0]},
 {name:'bird-plaza',position:[0,430,50],target:[0,0,0]},
 {name:'service-rear',position:[-430,55,-330],target:[-50,22,-170]},
 {name:'transit-entrance',position:[320,38,-500],target:[250,18,-170]},
 {name:'retail-frontage',position:[0,22,-390],target:[0,18,-40]},
 {name:'skyline',position:[600,180,-480],target:[120,60,0]},
 {name:'park-edge',position:[-620,45,80],target:[-250,22,0]},
 {name:'landmark-context',position:[160,70,540],target:[-130,25,100]},
 {name:'taxi-dropoff',position:[460,45,330],target:[250,16,120]},
];

export async function createCoreDistrictReview(app:HTMLDivElement,base:string,manifestFile='core-district-3d.json'){
 const manifest=await fetch(`${base}/manifest/${manifestFile}`).then(r=>{if(!r.ok)throw new Error(`manifest ${r.status}`);return r.json() as Promise<Manifest>});
 const streamLabel=manifest.urbanStream?`<dt>Stream</dt><dd>${manifest.urbanStream.lengthM.toFixed(0)}m / ${manifest.urbanStream.bridges} bridges</dd>`:'';
 app.innerHTML=`<main class="core3d"><aside><div class="brand"><span>ARCHIVE</span><strong>${manifest.urbanStream?'CORE + URBAN STREAM':'CORE DISTRICT 3D'}</strong></div><p class="core-warning">${manifest.badges.join('<br/>')}</p><button id="core-aerial">Aerial</button><button id="core-street">Street</button><button id="core-day">Day</button><button id="core-night">Night</button><label><input id="core-infra" type="checkbox" checked/> Street/Public Realm</label><label><input id="core-buildings" type="checkbox" checked/> Buildings</label>${manifest.urbanStream?'<label><input id="core-stream" type="checkbox" checked/> Urban Stream</label>':''}<label>LOD<select id="core-lod"><option>LOD1</option><option>LOD0</option><option>LOD2</option></select></label><dl><dt>Actual families</dt><dd>${manifest.metrics.actualFamilies}</dd><dt>Actual blocks</dt><dd>${manifest.metrics.actualBlocks}</dd><dt>Instances</dt><dd>${manifest.metrics.buildingInstances}</dd><dt>Proxy ratio</dt><dd>${(manifest.metrics.planningProxyRatio*100).toFixed(1)}%</dd>${streamLabel}</dl><div id="core-perf">LOADING ACTUAL GLB…</div></aside><section><div id="core-canvas"></div><div class="core-badge">${manifest.badges.join(' · ')}</div></section></main>`;
 const host=app.querySelector<HTMLElement>('#core-canvas')!,perf=app.querySelector<HTMLElement>('#core-perf')!;
 const scene=new THREE.Scene();scene.background=new THREE.Color(0xaac2d0);scene.fog=new THREE.Fog(0xaac2d0,900,2200);
 const camera=new THREE.PerspectiveCamera(52,1,.5,4000);camera.position.set(740,570,790);
 const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;renderer.shadowMap.enabled=true;renderer.shadowMap.autoUpdate=false;host.append(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,55,0);controls.enableDamping=true;
 const hemi=new THREE.HemisphereLight(0xeaf5ff,0x52614c,1.8);scene.add(hemi);
 const sun=new THREE.DirectionalLight(0xfff0d0,2.6);sun.position.set(-500,900,-350);scene.add(sun);
 const plazaLights=[[-130,28,105],[250,28,105],[0,24,-220],[-260,18,-80],[340,20,80]].map(([x,y,z])=>{const light=new THREE.PointLight(0xffd39a,0,220,1.4);light.position.set(x,y,z);scene.add(light);return light;});
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,1400),new THREE.MeshStandardMaterial({color:0x596761,roughness:.95}));ground.rotation.x=-Math.PI/2;ground.position.y=-.08;scene.add(ground);
 const loader=new GLTFLoader(),buildings=new THREE.Group(),infrastructure=new THREE.Group(),urbanStream=new THREE.Group();scene.add(buildings,infrastructure,urbanStream);const started=performance.now();
 const assetRevision='v9-material-hierarchy-2',loaded=new Map<string,THREE.Object3D>();await Promise.all(manifest.families.map(async family=>{const gltf=await loader.loadAsync(`${base}/${family.lod.LOD1}?rev=${assetRevision}`);loaded.set(family.id,gltf.scene);}));
 for(const family of manifest.families){const source=loaded.get(family.id);if(!source)continue;source.updateMatrixWorld(true);const items=manifest.instances.filter(item=>item.familyId===family.id),buckets=new Map<string,{material:THREE.Material;geometries:THREE.BufferGeometry[]}>();source.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const key=child.material.uuid,bucket=buckets.get(key)??{material:child.material as THREE.Material,geometries:[] as THREE.BufferGeometry[]};bucket.geometries.push(child.geometry.clone().applyMatrix4(child.matrixWorld));buckets.set(key,bucket);});for(const [materialId,bucket] of buckets){const geometry=mergeGeometries(bucket.geometries,false);if(!geometry)throw new Error(`merge failure ${family.id}/${materialId}`);const mesh=new THREE.InstancedMesh(geometry,bucket.material,items.length);mesh.name=`batch-${family.id}-${bucket.material.name}`;mesh.userData={familyId:family.id,status:'ACTUAL_GLTF_MATERIAL_BATCH'};items.forEach((item,index)=>{mesh.setMatrixAt(index,new THREE.Matrix4().compose(new THREE.Vector3(...item.position),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),item.rotationY),new THREE.Vector3(item.scale,item.scale,item.scale)));});mesh.instanceMatrix.needsUpdate=true;buildings.add(mesh);}}
 const infra=await loader.loadAsync(`${base}/${manifest.infrastructure.uri}?rev=${assetRevision}`);infrastructure.add(infra.scene);const ready=performance.now();
 if(manifest.urbanStream){const stream=await loader.loadAsync(`${base}/${manifest.urbanStream.uri}?rev=v10-stream-1`);urbanStream.add(stream.scene);}
 let frames=0,last=performance.now(),previous=last,fps=0;const frameTimes:number[]=[];
 function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
 new ResizeObserver(resize).observe(host);resize();
 function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);frames++;const now=performance.now(),delta=now-previous;previous=now;if(delta>0&&delta<1000){frameTimes.push(delta);if(frameTimes.length>600)frameTimes.shift();}if(now-last>=1000){fps=frames*1000/(now-last);frames=0;last=now;const sorted=[...frameTimes].sort((a,b)=>a-b),p99=sorted[Math.max(0,Math.ceil(sorted.length*.99)-1)]??1000,lowFps=1000/p99,info=renderer.info.render;perf.dataset.metrics=JSON.stringify({readyMs:Math.round(ready-started),fps:+fps.toFixed(1),lowFps:+lowFps.toFixed(1),sampleFrames:frameTimes.length,drawCalls:info.calls,triangles:info.triangles,instances:manifest.instances.length,pixelRatio:renderer.getPixelRatio()});perf.textContent=`READY ${Math.round(ready-started)}ms · FPS ${fps.toFixed(1)} · 1% low ${lowFps.toFixed(1)} · draw ${info.calls} · tri ${info.triangles.toLocaleString()}`;document.title=`CORE3D|${fps.toFixed(1)}|${lowFps.toFixed(1)}|${info.calls}|${info.triangles}`;}}
 animate();
 const setTime=(mode:'day'|'dusk'|'night')=>{if(mode==='night'){scene.background=new THREE.Color(0x111b2d);scene.fog=new THREE.Fog(0x111b2d,750,1900);renderer.toneMappingExposure=1;hemi.intensity=.8;sun.intensity=.38;plazaLights.forEach(x=>x.intensity=110);}else if(mode==='dusk'){scene.background=new THREE.Color(0x766f7f);scene.fog=new THREE.Fog(0x766f7f,850,2050);renderer.toneMappingExposure=.98;hemi.intensity=1.1;sun.intensity=.85;plazaLights.forEach(x=>x.intensity=48);}else{scene.background=new THREE.Color(0xaac2d0);scene.fog=new THREE.Fog(0xaac2d0,900,2200);renderer.toneMappingExposure=1.05;hemi.intensity=1.8;sun.intensity=2.6;plazaLights.forEach(x=>x.intensity=0);}};
 app.querySelector<HTMLButtonElement>('#core-aerial')!.onclick=()=>{camera.position.set(740,570,790);controls.target.set(0,55,0)};
 app.querySelector<HTMLButtonElement>('#core-street')!.onclick=()=>{camera.position.set(0,7,360);controls.target.set(0,24,0)};
 app.querySelector<HTMLButtonElement>('#core-day')!.onclick=()=>setTime('day');app.querySelector<HTMLButtonElement>('#core-night')!.onclick=()=>setTime('night');
 app.querySelector<HTMLInputElement>('#core-infra')!.onchange=e=>infrastructure.visible=(e.target as HTMLInputElement).checked;app.querySelector<HTMLInputElement>('#core-buildings')!.onchange=e=>buildings.visible=(e.target as HTMLInputElement).checked;
 const streamToggle=app.querySelector<HTMLInputElement>('#core-stream');if(streamToggle)streamToggle.onchange=e=>urbanStream.visible=(e.target as HTMLInputElement).checked;
 const query=new URLSearchParams(location.search),preset=Number(query.get('camera')??0),selected=cameras[preset%cameras.length];camera.position.set(...selected.position);controls.target.set(...selected.target);setTime(query.get('time')==='night'?'night':query.get('time')==='dusk'?'dusk':'day');
}
