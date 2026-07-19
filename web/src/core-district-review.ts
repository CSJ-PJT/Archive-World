import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {mergeGeometries} from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {EffectComposer} from 'three/examples/jsm/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/examples/jsm/postprocessing/RenderPass.js';
import {GTAOPass} from 'three/examples/jsm/postprocessing/GTAOPass.js';
import {OutputPass} from 'three/examples/jsm/postprocessing/OutputPass.js';

type Family={id:string;status:string;lod:Record<string,string>};
type Instance={familyId:string;position:[number,number,number];rotationY:number;scale:number;chunk:string};
type StreamLight={position:[number,number,number];color:'cyan'|'warm';intensity:number;distanceM:number};
type HeroZone={id:string;status:string;uri:string;actual3D:boolean;buildingCount:number;radiusM:number};
type Manifest={status:string;badges:string[];families:Family[];instances:Instance[];blocks:{id:string;type:string}[];infrastructure:{uri:string};urbanStream?:{uri:string;lengthM:number;bridges:number;accessPoints:number;viewerLights?:StreamLight[]};heroZones?:HeroZone[];metrics:Record<string,number>};
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
 {name:'stream-aerial',position:[0,360,470],target:[0,0,0]},
 {name:'archive-water-plaza',position:[-240,14,86],target:[-240,3,4]},
 {name:'ledger-stream-terrace',position:[60,12,-86],target:[60,3,0]},
 {name:'transit-stream-junction',position:[260,13,88],target:[260,3,2]},
 {name:'slim-steel-bridge',position:[-310,8,60],target:[-310,1,16]},
 {name:'stepped-stream-edge',position:[-270,7,-54],target:[-250,1,5]},
 {name:'green-stream-edge',position:[-150,7,55],target:[-150,1,-8]},
 {name:'archive-gateway-bridge',position:[65,9,65],target:[65,2,8]},
 {name:'stream-pavilion',position:[-258,8,-58],target:[-240,2,10]},
 {name:'accessible-ramp',position:[245,7,-58],target:[260,1,8]},
 {name:'service-stream-crossing',position:[300,8,60],target:[300,1,-4]},
 {name:'future-riverfront-corridor',position:[390,12,-85],target:[300,3,0]},
 {name:'water-closeup',position:[-30,3.8,24],target:[20,.2,0]},
 {name:'promenade-sequence',position:[-180,5.2,42],target:[-85,1.3,0]},
 {name:'pocket-wetland',position:[345,6,38],target:[345,1,-15]},
 {name:'cafe-terrace',position:[-120,5.5,-42],target:[-120,1,12]},
 {name:'ledger-lunch-terrace',position:[60,6.5,-48],target:[60,1,15]},
 {name:'archive-active-frontage',position:[-255,6,48],target:[-250,2,-18]},
 {name:'transit-waiting-plaza',position:[260,7,-55],target:[260,2,15]},
 {name:'formal-ledger-bridge',position:[-195,7,-50],target:[-195,1,0]},
 {name:'stream-section-depth',position:[-70,10,70],target:[-70,0,0]},
 {name:'activity-node',position:[145,6,46],target:[150,1,-5]},
 {name:'night-lighting-axis',position:[0,18,120],target:[0,2,0]},
 {name:'technical-status',position:[500,250,540],target:[0,35,0]},
 {name:'hero-archive-axis',position:[-340,3.3,12],target:[-225,1.5,0]},
 {name:'hero-water-section',position:[-270,9.0,52],target:[-270,.3,0]},
 {name:'hero-gateway-approach',position:[-300,5.5,30],target:[-250,4.6,0]},
 {name:'hero-north-lobby',position:[-345,4.1,-22],target:[-300,3.4,58]},
 {name:'hero-south-frontage',position:[-345,4.1,22],target:[-300,3.4,-58]},
 {name:'hero-civic-terrace',position:[-330,4.6,10],target:[-300,4.0,24]},
 {name:'hero-archive-aerial',position:[-250,160,180],target:[-250,18,0]},
];

function material(color:number,roughness=.72,metalness=0){return new THREE.MeshStandardMaterial({color,roughness,metalness});}
function stableFamilyTone(id:string){let value=2166136261;for(const char of id)value=(value^char.charCodeAt(0))*16777619;return Math.abs(value)%3;}
function finalizeSupportFamilyMaterials(root:THREE.Object3D,familyId:string,performance=false){
 // Office V5 is a frozen PO asset: neither its geometry nor authored material
 // is remapped by the district-review layer.
 if(familyId==='archive-cbd-twin-atrium-pq-v5')return;
 const tone=stableFamilyTone(familyId);
 const stone=[0x928a7d,0x858a88,0x9a927f][tone],metal=[0x33434a,0x3e3833,0x2f4244][tone];
 root.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const current=child.material,name=current.name.toLowerCase();child.castShadow=!performance;child.receiveShadow=true;
  if(name.includes('curtain-wall-glass')||name.includes('residential-glass'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:[0x244853,0x334b52,0x263f49][tone],roughness:.24,metalness:.12});
  else if(name.includes('limestone')||name.includes('painted-concrete')||name.includes('precast'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:stone,roughness:.72});
  else if(name.includes('granite')||name.includes('dark-stone'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x343839,roughness:.56});
  else if(name.includes('dark-metal')||name.includes('painted-steel'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:metal,roughness:.42,metalness:.46});
  else if(name.includes('light-metal')||name.includes('aluminum'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x6f7778,roughness:.38,metalness:.58});
  else if(name.includes('sidewalk'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x777a75,roughness:.88});
  else if(name.includes('asphalt'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x252a2d,roughness:.92});
 });
}
function finalizeInfrastructureMaterials(root:THREE.Object3D){
 const palette={asphalt:material(0x242a2d,.9),sidewalk:material(0x8a8e88,.82),plaza:material(0xaaa394,.74),curb:material(0x626965,.86),foliage:material(0x285b32,.88),timber:material(0x56381f,.72),human:material(0x786f67,.7),vehicle:material(0x303b46,.52,.2),metal:material(0x29343b,.45,.55),glass:new THREE.MeshPhysicalMaterial({color:0x345e6d,roughness:.2,metalness:0,transmission:.08,transparent:true,opacity:.82})};
 root.traverse(child=>{if(!(child instanceof THREE.Mesh))return;const name=child.name.toLowerCase();if(name.includes('tree-crown'))child.material=palette.foliage;else if(name.includes('tree-trunk'))child.material=palette.timber;else if(name.includes('road-asphalt')||name.includes('bus-bay'))child.material=palette.asphalt;else if(name.includes('sidewalk')||name.includes('crosswalk'))child.material=palette.sidewalk;else if(name.includes('plaza')||name.includes('median'))child.material=palette.plaza;else if(name.includes('curb'))child.material=palette.curb;else if(name.includes('human'))child.material=palette.human;else if(name.includes('vehicle-body'))child.material=palette.vehicle;else if(name.includes('glass')||name.includes('station-entrance'))child.material=palette.glass;else if(name.includes('streetlight')||name.includes('bollard')||name.includes('rack'))child.material=palette.metal;});
}
function finalizeHeroMaterials(root:THREE.Object3D,performance=false){
 root.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const current=child.material,name=current.name.toLowerCase();
  child.castShadow=true;child.receiveShadow=true;
  if(name.includes('shallow-water'))child.material=performance?new THREE.MeshStandardMaterial({name:current.name,color:0x24616a,roughness:.34,metalness:.04,transparent:false}):new THREE.MeshPhysicalMaterial({name:current.name,color:0x24616a,roughness:.28,metalness:.05,transmission:.08,transparent:true,opacity:.9,depthWrite:true,side:THREE.DoubleSide});
  else if(name.includes('frontage-glass')||name.includes('pavilion-glass'))child.material=performance?new THREE.MeshStandardMaterial({name:current.name,color:0x315c65,roughness:.26,metalness:.08}):new THREE.MeshPhysicalMaterial({name:current.name,color:0x456f76,roughness:.18,metalness:.03,transmission:.32,transparent:true,opacity:.58,depthWrite:false,clearcoat:.55,clearcoatRoughness:.18});
  else if(name.includes('occupied-window-glass'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x2e535c,roughness:.26,metalness:.08,emissive:0x9b5b25,emissiveIntensity:.08});
  else if(name.includes('blue-gray-glass'))child.material=performance?new THREE.MeshStandardMaterial({name:current.name,color:0x183943,roughness:.28,metalness:.12}):new THREE.MeshPhysicalMaterial({name:current.name,color:0x183943,roughness:.18,metalness:.15,clearcoat:.6,clearcoatRoughness:.2});
  else if(name.includes('archive-warm-stone'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x8f8778,roughness:.73});
  else if(name.includes('ledger-limestone'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x878681,roughness:.67});
  else if(name.includes('ledger-granite'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x343a3c,roughness:.48});
  else if(name.includes('archive-metal'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x294c56,roughness:.32,metalness:.62});
  else if(name.includes('ledger-bronze'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x76502f,roughness:.34,metalness:.68});
  else if(name.includes('dry-stone'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x696b67,roughness:.8});
  else if(name.includes('wet-stone'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x3b4746,roughness:.34});
  else if(name.includes('promenade-paver'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x747a76,roughness:.87});
  else if(name.includes('foliage-deep'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x234f2d,roughness:.88});
  else if(name.includes('foliage-mid'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x376c3b,roughness:.86});
  else if(name.includes('foliage-light'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x5c8350,roughness:.84});
  else if(name.includes('timber-accent'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x5c3b20,roughness:.68});
  else if(name.includes('warm-interior'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x5f3b29,roughness:.64,emissive:0x7d3514,emissiveIntensity:1.15});
  else if(name.includes('warm-light'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0xffd5a0,roughness:.35,emissive:0xffa84f,emissiveIntensity:2.0});
  else if(name.includes('archive-cyan-light'))child.material=new THREE.MeshStandardMaterial({name:current.name,color:0x7eeaf0,roughness:.3,emissive:0x20a9bd,emissiveIntensity:1.7});
 });
}

export async function createCoreDistrictReview(app:HTMLDivElement,base:string,manifestFile='core-district-3d.json'){
 const manifest=await fetch(`${base}/manifest/${manifestFile}`).then(r=>{if(!r.ok)throw new Error(`manifest ${r.status}`);return r.json() as Promise<Manifest>});
 const query=new URLSearchParams(location.search),requestedLod=query.get('lod'),performanceMode=query.get('performance')==='1',cinematicMode=!performanceMode&&query.get('cinematic')==='1',reviewLod=requestedLod==='LOD0'||requestedLod==='LOD2'?requestedLod:performanceMode?'LOD2':'LOD1';
 const streamLabel=manifest.urbanStream?`<dt>Stream</dt><dd>${manifest.urbanStream.lengthM.toFixed(0)}m / ${manifest.urbanStream.bridges} bridges</dd>`:'';
 app.innerHTML=`<main class="core3d"><aside><div class="brand"><span>ARCHIVE</span><strong>${manifest.urbanStream?'CORE + URBAN STREAM':'CORE DISTRICT 3D'}</strong></div><p class="core-warning">${manifest.badges.join('<br/>')}</p><button id="core-aerial">Aerial</button><button id="core-street">Street</button><button id="core-day">Day</button><button id="core-night">Night</button><label><input id="core-infra" type="checkbox" checked/> Street/Public Realm</label><label><input id="core-buildings" type="checkbox" checked/> Buildings</label>${manifest.urbanStream?'<label><input id="core-stream" type="checkbox" checked/> Urban Stream</label>':''}<label>LOD<select id="core-lod"><option>LOD1</option><option>LOD0</option><option>LOD2</option></select></label><dl><dt>Actual families</dt><dd>${manifest.metrics.actualFamilies}</dd><dt>Actual blocks</dt><dd>${manifest.metrics.actualBlocks}</dd><dt>Instances</dt><dd>${manifest.metrics.buildingInstances}</dd><dt>Proxy ratio</dt><dd>${(manifest.metrics.planningProxyRatio*100).toFixed(1)}%</dd>${streamLabel}</dl><div id="core-perf">LOADING ACTUAL GLB…</div></aside><section><div id="core-canvas"></div><div class="core-badge">${manifest.badges.join(' · ')}</div></section></main>`;
 if(query.get('clean')==='1')app.querySelector('.core3d')?.classList.add('clean-capture');
 const host=app.querySelector<HTMLElement>('#core-canvas')!,perf=app.querySelector<HTMLElement>('#core-perf')!;
 const scene=new THREE.Scene();scene.background=new THREE.Color(0x9fadb3);scene.fog=new THREE.Fog(0x9fadb3,1200,2600);
 const camera=new THREE.PerspectiveCamera(manifest.heroZones?.length?44:52,1,.35,4000);camera.position.set(740,570,790);
 const renderer=new THREE.WebGLRenderer({antialias:!performanceMode,preserveDrawingBuffer:!performanceMode});renderer.setPixelRatio(performanceMode?.5:Math.min(devicePixelRatio,1));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;renderer.shadowMap.enabled=!performanceMode;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=!performanceMode&&!!manifest.heroZones?.length;host.append(renderer.domElement);
 const composer=cinematicMode?new EffectComposer(renderer):undefined;
 if(composer){composer.addPass(new RenderPass(scene,camera));const gtao=new GTAOPass(scene,camera,window.innerWidth,window.innerHeight);gtao.updateGtaoMaterial({radius:3.2,distanceExponent:1.7,thickness:1.1,distanceFallOff:1,scale:1,samples:16});gtao.updatePdMaterial({samples:8,radius:6,radiusExponent:2});gtao.blendIntensity=.72;composer.addPass(gtao);composer.addPass(new OutputPass());}
 if(!performanceMode){const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(new RoomEnvironment(),.04).texture;pmrem.dispose();}
 const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,55,0);controls.enableDamping=true;
 const hemi=new THREE.HemisphereLight(0xe7eef0,0x323a37,.82);scene.add(hemi);
 const sun=new THREE.DirectionalLight(0xffdfb6,2.25);sun.position.set(-520,760,-620);sun.castShadow=!performanceMode&&!!manifest.heroZones?.length;sun.shadow.mapSize.set(1536,1536);sun.shadow.camera.left=-260;sun.shadow.camera.right=260;sun.shadow.camera.top=220;sun.shadow.camera.bottom=-220;sun.shadow.camera.near=120;sun.shadow.camera.far=1500;sun.shadow.bias=-.00035;sun.target.position.set(-250,0,0);scene.add(sun,sun.target);
 const plazaLights=[[-130,28,105],[250,28,105],[0,24,-220],[-260,18,-80],[340,20,80]].map(([x,y,z])=>{const light=new THREE.PointLight(0xffd39a,0,220,1.4);light.position.set(x,y,z);scene.add(light);return light;});
 const heroLights=(manifest.heroZones?.length?[[-326,8,-58],[-260,10,-60],[-190,8,-56],[-326,8,58],[-258,10,60],[-188,8,56]]:[]).map(([x,y,z])=>{const light=new THREE.PointLight(0xffb46c,0,85,1.8);light.position.set(x,y,z);scene.add(light);return light;});
 const streamLights=(manifest.urbanStream?.viewerLights??[]).map(spec=>{const light=new THREE.PointLight(spec.color==='cyan'?0x5eeeff:0xffc77d,0,spec.distanceM,1.6);light.position.set(...spec.position);scene.add(light);return {light,intensity:spec.intensity};});
 const setHeroMaterialState=(night:boolean)=>heroZones.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const mat=child.material as THREE.MeshStandardMaterial,name=mat.name.toLowerCase();if(name.includes('occupied-window-glass'))mat.emissiveIntensity=night?2.4:.08;else if(name.includes('warm-interior'))mat.emissiveIntensity=night?3.2:.22;else if(name.includes('warm-light'))mat.emissiveIntensity=night?5.5:.55;else if(name.includes('archive-cyan-light'))mat.emissiveIntensity=night?3.1:.4;});
 const groundMaterial=new THREE.MeshStandardMaterial({color:0x4f5a55,roughness:.96});
 if(manifest.urbanStream){for(const side of [-1,1]){const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,650),groundMaterial);ground.rotation.x=-Math.PI/2;ground.position.set(0,-.08,side*350);ground.receiveShadow=true;scene.add(ground);}}else{const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,1400),groundMaterial);ground.rotation.x=-Math.PI/2;ground.position.y=-.08;ground.receiveShadow=true;scene.add(ground);}
 const loader=new GLTFLoader(),buildings=new THREE.Group(),infrastructure=new THREE.Group(),urbanStream=new THREE.Group(),heroZones=new THREE.Group();scene.add(buildings,infrastructure,urbanStream,heroZones);const started=performance.now();
 const assetRevision='v9-material-hierarchy-3',loaded=new Map<string,THREE.Object3D>();await Promise.all(manifest.families.map(async family=>{const gltf=await loader.loadAsync(`${base}/${family.lod[reviewLod]}?rev=${assetRevision}`);finalizeSupportFamilyMaterials(gltf.scene,family.id,performanceMode);loaded.set(family.id,gltf.scene);}));
 for(const family of manifest.families){const source=loaded.get(family.id);if(!source)continue;source.updateMatrixWorld(true);const items=manifest.instances.filter(item=>item.familyId===family.id),buckets=new Map<string,{material:THREE.Material;geometries:THREE.BufferGeometry[]}>();source.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const key=child.material.uuid,bucket=buckets.get(key)??{material:child.material as THREE.Material,geometries:[] as THREE.BufferGeometry[]};bucket.geometries.push(child.geometry.clone().applyMatrix4(child.matrixWorld));buckets.set(key,bucket);});for(const [materialId,bucket] of buckets){const geometry=mergeGeometries(bucket.geometries,false);if(!geometry)throw new Error(`merge failure ${family.id}/${materialId}`);const mesh=new THREE.InstancedMesh(geometry,bucket.material,items.length);mesh.name=`batch-${family.id}-${bucket.material.name}`;mesh.userData={familyId:family.id,status:'ACTUAL_GLTF_MATERIAL_BATCH'};items.forEach((item,index)=>{mesh.setMatrixAt(index,new THREE.Matrix4().compose(new THREE.Vector3(...item.position),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),item.rotationY),new THREE.Vector3(item.scale,item.scale,item.scale)));});mesh.instanceMatrix.needsUpdate=true;buildings.add(mesh);}}
 if(!manifest.heroZones?.length){const infra=await loader.loadAsync(`${base}/${manifest.infrastructure.uri}?rev=${assetRevision}`);finalizeInfrastructureMaterials(infra.scene);infrastructure.add(infra.scene);}
 if(manifest.urbanStream&&!manifest.heroZones?.length){const stream=await loader.loadAsync(`${base}/${manifest.urbanStream.uri}?rev=v11-stream-final`);urbanStream.add(stream.scene);}
 if(manifest.heroZones){for(const zone of manifest.heroZones){const hero=await loader.loadAsync(`${base}/${zone.uri}?rev=${encodeURIComponent(zone.status)}`);finalizeHeroMaterials(hero.scene,performanceMode);hero.scene.userData={heroZone:zone.id,status:zone.status,actual3D:true};heroZones.add(hero.scene);}}
 const ready=performance.now();perf.textContent=`READY ${Math.round(ready-started)}ms · ${reviewLod} · calibrated material hierarchy`;
 let frames=0,last=performance.now(),previous=last,fps=0,warmupReset=false;const frameTimes:number[]=[];
 function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);composer?.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}
 new ResizeObserver(resize).observe(host);resize();
 function animate(){requestAnimationFrame(animate);controls.update();if(composer)composer.render();else renderer.render(scene,camera);frames++;const now=performance.now(),delta=now-previous;previous=now;if(!warmupReset&&now-ready>8000){frameTimes.length=0;frames=0;last=now;warmupReset=true;}if(delta>0&&delta<1000&&warmupReset){frameTimes.push(delta);if(frameTimes.length>600)frameTimes.shift();}if(now-last>=1000){fps=frames*1000/(now-last);frames=0;last=now;const sorted=[...frameTimes].sort((a,b)=>a-b),p99=sorted[Math.max(0,Math.ceil(sorted.length*.99)-1)]??1000,lowFps=1000/p99,info=renderer.info.render;perf.dataset.metrics=JSON.stringify({readyMs:Math.round(ready-started),fps:+fps.toFixed(1),lowFps:+lowFps.toFixed(1),sampleFrames:frameTimes.length,drawCalls:info.calls,triangles:info.triangles,instances:manifest.instances.length,pixelRatio:renderer.getPixelRatio(),lod:reviewLod,cinematic:cinematicMode});perf.textContent=`READY ${Math.round(ready-started)}ms · ${reviewLod} · FPS ${fps.toFixed(1)} · 1% low ${lowFps.toFixed(1)} · draw ${info.calls} · tri ${info.triangles.toLocaleString()}`;document.title=`CORE3D|${fps.toFixed(1)}|${lowFps.toFixed(1)}|${info.calls}|${info.triangles}`;}}
 animate();
 const setTime=(mode:'day'|'dusk'|'night')=>{if(mode==='night'){scene.background=new THREE.Color(0x111b2d);scene.fog=new THREE.Fog(0x111b2d,750,1900);scene.environmentIntensity=.24;renderer.toneMappingExposure=.86;hemi.intensity=.34;sun.intensity=.14;setHeroMaterialState(true);plazaLights.forEach(x=>x.intensity=performanceMode?0:75);heroLights.forEach(x=>x.intensity=performanceMode?0:95);streamLights.forEach(x=>x.light.intensity=performanceMode?0:x.intensity);}else if(mode==='dusk'){scene.background=new THREE.Color(0x766f7f);scene.fog=new THREE.Fog(0x766f7f,850,2050);scene.environmentIntensity=.52;renderer.toneMappingExposure=.93;hemi.intensity=.82;sun.intensity=.72;setHeroMaterialState(true);plazaLights.forEach(x=>x.intensity=performanceMode?0:32);heroLights.forEach(x=>x.intensity=performanceMode?0:48);streamLights.forEach(x=>x.light.intensity=performanceMode?0:x.intensity*.45);}else{scene.background=new THREE.Color(0x9fadb3);scene.fog=new THREE.Fog(0x9fadb3,1200,2600);scene.environmentIntensity=.62;renderer.toneMappingExposure=.90;hemi.intensity=.82;sun.intensity=2.25;setHeroMaterialState(false);plazaLights.forEach(x=>x.intensity=0);heroLights.forEach(x=>x.intensity=0);streamLights.forEach(x=>x.light.intensity=0);}};
 app.querySelector<HTMLButtonElement>('#core-aerial')!.onclick=()=>{camera.position.set(740,570,790);controls.target.set(0,55,0)};
 app.querySelector<HTMLButtonElement>('#core-street')!.onclick=()=>{camera.position.set(0,7,360);controls.target.set(0,24,0)};
 app.querySelector<HTMLButtonElement>('#core-day')!.onclick=()=>setTime('day');app.querySelector<HTMLButtonElement>('#core-night')!.onclick=()=>setTime('night');
 app.querySelector<HTMLInputElement>('#core-infra')!.onchange=e=>infrastructure.visible=(e.target as HTMLInputElement).checked;app.querySelector<HTMLInputElement>('#core-buildings')!.onchange=e=>buildings.visible=(e.target as HTMLInputElement).checked;
 const streamToggle=app.querySelector<HTMLInputElement>('#core-stream');if(streamToggle)streamToggle.onchange=e=>{urbanStream.visible=(e.target as HTMLInputElement).checked;heroZones.visible=(e.target as HTMLInputElement).checked;};
 const preset=Number(query.get('camera')??0),selected=cameras[preset%cameras.length];camera.position.set(...selected.position);controls.target.set(...selected.target);
 const pose=(query.get('pose')??'').split(',').map(Number);if(pose.length===6&&pose.every(Number.isFinite)){camera.position.set(pose[0],pose[1],pose[2]);controls.target.set(pose[3],pose[4],pose[5]);}
 setTime(query.get('time')==='night'?'night':query.get('time')==='dusk'?'dusk':'day');
}
