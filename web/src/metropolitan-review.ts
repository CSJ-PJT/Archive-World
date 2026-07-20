import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';

type District={id:string;identity:string;palette:string;polygon:number[][];instanceCount:number;camera:{position:number[];target:number[]}};
type Building={id:string;districtId:string;palette:string;position:number[];rotationZ:number;dimensions:number[];podiumHeight:number;upperScale:number;massing:string;activeFrontage:number;nightOccupancy:number;frozenPO:boolean};
type Block={id:string;districtId:string;center:number[];palette:string;activityClusters:string[];treeVariantOffset:number};
type PrecisionScene={status:string;badges:string[];boundsMeters:number[];districts:District[];blocks:Block[];instances:Building[];metrics:{districtCount:number;blockCount:number;buildingInstances:number;uniqueFamilies:number;activityClusters:number;planningProxyRatio:number}};
type TimeMode='day'|'dusk'|'night';
const SAFETY_BADGES=['NOT CANONICAL','NOT V3 APPLIED'] as const;

const PALETTES:Record<string,{stone:number;glass:number;metal:number;ground:number;light:number}>={
 archive:{stone:0xc4c1b6,glass:0x567581,metal:0x657a82,ground:0xa9aaa3,light:0x91d8df},
 ledger:{stone:0x77736b,glass:0x425c65,metal:0x765b49,ground:0x8d8980,light:0xffc98b},
 market:{stone:0x9e7b66,glass:0x496973,metal:0x594b45,ground:0x9d8a7c,light:0xffae78},
 nexus:{stone:0xabb3b0,glass:0x4d7481,metal:0x596f72,ground:0x919c98,light:0x8cd6d1},
 logistics:{stone:0x747974,glass:0x3f555a,metal:0x454d4c,ground:0x6f736e,light:0xf1b47a},
 residential:{stone:0xb9b5aa,glass:0x63808a,metal:0x77756e,ground:0x9ca196,light:0xffc49b},
 'residential-warm':{stone:0xc2b1a2,glass:0x5e7c85,metal:0x78665c,ground:0xa89c90,light:0xffbd8c},
 civic:{stone:0xc6c0b2,glass:0x657d83,metal:0x6d716d,ground:0xaaa79e,light:0xffcf9d},
 riverfront:{stone:0xa7ada7,glass:0x4c7884,metal:0x5e706e,ground:0x87958d,light:0x8fdbe2},
 park:{stone:0xaaa99d,glass:0x527079,metal:0x647066,ground:0x718371,light:0xffc795},
 transit:{stone:0xa7afb2,glass:0x476d79,metal:0x53656b,ground:0x888f8e,light:0x9ee9e8},
 infrastructure:{stone:0x6c716f,glass:0x42555a,metal:0x414948,ground:0x686d68,light:0xe0a36e},
 'residential-east':{stone:0xb4b2a8,glass:0x5b7881,metal:0x6c746f,ground:0x969e94,light:0xffc09a},
};

const box=new THREE.BoxGeometry(1,1,1);
const dummy=new THREE.Object3D();
const material=(color:number,roughness=.62,metalness=.08)=>new THREE.MeshStandardMaterial({color,roughness,metalness});

function matrix(x:number,y:number,z:number,sx:number,sy:number,sz:number,rotation:number){
 dummy.position.set(x,y,z);dummy.scale.set(sx,sy,sz);dummy.rotation.set(0,rotation,0);dummy.updateMatrix();return dummy.matrix.clone();
}

export async function createMetropolitanReview(app:HTMLDivElement,base:string){
 const response=await fetch(`${base}/metropolitan-precision-scene.json`);if(!response.ok)throw new Error(`Metropolitan precision scene unavailable: ${response.status}`);
 const manifest=await response.json() as PrecisionScene;
 if(!SAFETY_BADGES.every(badge=>manifest.badges.includes(badge)))throw new Error('Metropolitan precision safety badges are missing.');
 app.innerHTML=`<main class="metro-review metro-3d"><aside><div class="brand"><span>ARCHIVE</span><strong>METROPOLITAN PRECISION</strong></div><p class="metro-warning">${manifest.badges.join('<br/>')}</p><label>District<select id="metro-district"><option value="full">Full Metropolitan</option>${manifest.districts.map(d=>`<option value="${d.id}">${d.id.replaceAll('-',' ')}</option>`).join('')}</select></label><div class="metro-times"><button data-time="day">Day</button><button data-time="dusk">Dusk</button><button data-time="night">Night</button></div><label><input id="metro-life" type="checkbox" checked/> Urban life</label><label><input id="metro-green" type="checkbox" checked/> Landscape</label><dl><dt>Districts</dt><dd>${manifest.metrics.districtCount}</dd><dt>Blocks</dt><dd>${manifest.metrics.blockCount}</dd><dt>Buildings</dt><dd>${manifest.metrics.buildingInstances}</dd><dt>Families</dt><dd>${manifest.metrics.uniqueFamilies}</dd><dt>Activity clusters</dt><dd>${manifest.metrics.activityClusters}</dd><dt>Planning proxy</dt><dd>${(manifest.metrics.planningProxyRatio*100).toFixed(0)}%</dd></dl><p class="hint">Drag to orbit · wheel to zoom · right-drag to pan</p></aside><section><div id="metro-webgl"></div><div id="metro-status" class="hud">METRO3D LOADING</div><div class="metro-badge">${manifest.badges.join(' · ')}</div></section></main>`;
 const host=app.querySelector<HTMLDivElement>('#metro-webgl')!;const status=app.querySelector<HTMLElement>('#metro-status')!;
 const scene=new THREE.Scene();scene.background=new THREE.Color(0xaebfc9);scene.fog=new THREE.FogExp2(0xaebfc9,.000055);
 const camera=new THREE.PerspectiveCamera(43,16/9,2,18000);camera.position.set(3300,2450,4100);
 const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.04;host.append(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,0,0);controls.enableDamping=true;controls.maxDistance=10000;controls.minDistance=60;
 const ambient=new THREE.HemisphereLight(0xdde8ee,0x4b554d,2.15);scene.add(ambient);
 const sun=new THREE.DirectionalLight(0xfff2db,3.7);sun.position.set(-1600,3100,2200);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-2100;sun.shadow.camera.right=2100;sun.shadow.camera.top=1900;sun.shadow.camera.bottom=-1900;sun.shadow.camera.far=7200;scene.add(sun);
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(6800,5800),material(0x7e8884,.96));ground.rotation.x=-Math.PI/2;ground.position.y=-.5;ground.receiveShadow=true;scene.add(ground);
 const waterMat=new THREE.MeshPhysicalMaterial({color:0x2f6470,roughness:.26,metalness:.05,transparent:true,opacity:.82,clearcoat:.45});
 const river=new THREE.Mesh(new THREE.PlaneGeometry(6000,300),waterMat);river.rotation.x=-Math.PI/2;river.position.set(0,.08,-600);scene.add(river);
 const stream=new THREE.Mesh(new THREE.PlaneGeometry(2350,34),waterMat);stream.rotation.x=-Math.PI/2;stream.position.set(780,.12,210);scene.add(stream);

 const nightMaterials:THREE.MeshStandardMaterial[]=[];
 for(const [paletteKey,palette] of Object.entries(PALETTES)){
  const buildings=manifest.instances.filter(item=>item.palette===paletteKey);if(!buildings.length)continue;
  const podiumMat=material(palette.stone,.72,.04),towerMat=material(palette.stone,.58,.08),frameMat=material(palette.metal,.38,.62);
  const upperMat=material(palette.glass,.34,.14),windowMat=new THREE.MeshStandardMaterial({color:palette.glass,roughness:.32,metalness:.12,emissive:palette.light,emissiveIntensity:0});nightMaterials.push(windowMat);
  const podium=new THREE.InstancedMesh(box,podiumMat,buildings.length),tower=new THREE.InstancedMesh(box,towerMat,buildings.length),upper=new THREE.InstancedMesh(box,upperMat,buildings.length),crown=new THREE.InstancedMesh(box,frameMat,buildings.length),lobby=new THREE.InstancedMesh(box,windowMat,buildings.length),frontGlass=new THREE.InstancedMesh(box,windowMat,buildings.length),sideGlass=new THREE.InstancedMesh(box,windowMat,buildings.length),bands=new THREE.InstancedMesh(box,frameMat,buildings.length*3);
  [podium,tower,upper,crown,lobby,frontGlass,sideGlass,bands].forEach(mesh=>{mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=true;scene.add(mesh);});
  buildings.forEach((item,index)=>{const [x,z]=item.position,[w,d,h]=item.dimensions,p=item.podiumHeight,u=item.upperScale,r=item.rotationZ;const towerH=Math.max(4,h-p);const axis=item.massing==='setback-slab'?.88:item.massing==='point-crown'?.72:item.massing==='courtyard-edge'?.82:1,tw=w*axis;podium.setMatrixAt(index,matrix(x,p/2,z,w*1.12,p,d*1.08,r));tower.setMatrixAt(index,matrix(x,p+towerH*.34,z,tw,towerH*.68,d,r));upper.setMatrixAt(index,matrix(x+(item.massing==='stepped-tower'?w*.12:0),p+towerH*.84,z,w*u,towerH*.32,d*u,r));crown.setMatrixAt(index,matrix(x,p+towerH+1.1,z,w*(u+.05),2.2,d*(u+.05),r));const front=d*.58,lobbyX=x+Math.sin(r)*front,lobbyZ=z+Math.cos(r)*front;lobby.setMatrixAt(index,matrix(lobbyX,p*.28,lobbyZ,w*.48,Math.max(3.2,p*.5),2.8,r));const frontOffset=d*.502,fx=x+Math.sin(r)*frontOffset,fz=z+Math.cos(r)*frontOffset;frontGlass.setMatrixAt(index,matrix(fx,p+towerH*.36,fz,tw*.84,towerH*.58,.22,r));const sideOffset=tw*.502,sx=x+Math.cos(r)*sideOffset,sz=z-Math.sin(r)*sideOffset;sideGlass.setMatrixAt(index,matrix(sx,p+towerH*.36,sz,.22,towerH*.58,d*.82,r));for(let band=0;band<3;band++){const by=p+towerH*(.18+band*.19);bands.setMatrixAt(index*3+band,matrix(fx,by,fz,tw*.9,.34,.34,r));}});
 }

 for(const [paletteKey,palette] of Object.entries(PALETTES)){const districtBlocks=manifest.blocks.filter(item=>item.palette===paletteKey);if(!districtBlocks.length)continue;const blockMat=new THREE.MeshStandardMaterial({color:palette.ground,roughness:.92});const blocks=new THREE.InstancedMesh(box,blockMat,districtBlocks.length);blocks.receiveShadow=true;districtBlocks.forEach((item,index)=>blocks.setMatrixAt(index,matrix(item.center[0],.16,item.center[1],205,.32,166,0)));scene.add(blocks);}
 const treeGroup=new THREE.Group(),lifeGroup=new THREE.Group();scene.add(treeGroup,lifeGroup);
 const trunk=new THREE.InstancedMesh(new THREE.CylinderGeometry(.55,.9,7,7),material(0x574538,.88),manifest.blocks.length*2);const crown=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(3.8,1),material(0x355c42,.86),manifest.blocks.length*2);let treeIndex=0;
 for(const item of manifest.blocks){for(let lane=0;lane<2;lane++){const ox=(lane?45:-45)+item.treeVariantOffset*.3,oz=(lane?27:-27);trunk.setMatrixAt(treeIndex,matrix(item.center[0]+ox,3.5,item.center[1]+oz,1,1,1,0));const scale=.82+(item.treeVariantOffset%7)*.045;crown.setMatrixAt(treeIndex,matrix(item.center[0]+ox,9,item.center[1]+oz,scale,scale*(1.05+(lane*.08)),scale,0));treeIndex++;}}treeGroup.add(trunk,crown);
 const people=new THREE.InstancedMesh(new THREE.CapsuleGeometry(.34,.9,3,6),material(0x293d48,.72),manifest.blocks.length*3);let person=0;for(const item of manifest.blocks){for(let n=0;n<3;n++){const a=(n-1)*3.2;people.setMatrixAt(person++,matrix(item.center[0]+a,1,item.center[1]+34+(n%2)*2,1,1,1,0));}}lifeGroup.add(people);
 const streetMat=material(0x30383a,.96);const streets=new THREE.Group();for(let x=-2900;x<=2900;x+=250){const road=new THREE.Mesh(new THREE.BoxGeometry(24,.18,5000),streetMat);road.position.set(x,.02,0);streets.add(road);}for(let z=-2400;z<=2400;z+=220){const road=new THREE.Mesh(new THREE.BoxGeometry(6000,.2,24),streetMat);road.position.set(0,.03,z);streets.add(road);}scene.add(streets);

 function resize(){const section=host.parentElement!;const width=Math.max(640,section.clientWidth),height=Math.max(480,section.clientHeight);renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();}resize();window.addEventListener('resize',resize);
 let mode:TimeMode='day';function setTime(next:TimeMode){mode=next;const night=next==='night',dusk=next==='dusk';scene.background=new THREE.Color(night?0x061827:dusk?0x8a7180:0xaebfc9);scene.fog!.color.copy(scene.background);ambient.intensity=night?.52:dusk?1.05:2.15;sun.intensity=night?.16:dusk?1.45:3.7;renderer.toneMappingExposure=night?.82:dusk?.95:1.04;waterMat.color.setHex(night?0x173f4b:dusk?0x315a69:0x2f6470);nightMaterials.forEach(mat=>mat.emissiveIntensity=night?.24:dusk?.10:0);}
 app.querySelectorAll<HTMLButtonElement>('[data-time]').forEach(button=>button.onclick=()=>setTime(button.dataset.time as TimeMode));
 app.querySelector<HTMLInputElement>('#metro-life')!.onchange=event=>lifeGroup.visible=(event.target as HTMLInputElement).checked;app.querySelector<HTMLInputElement>('#metro-green')!.onchange=event=>treeGroup.visible=(event.target as HTMLInputElement).checked;
 function focus(id:string){if(id==='full'){camera.position.set(3300,2450,4100);controls.target.set(0,45,0);}else{const district=manifest.districts.find(item=>item.id===id);if(district){const [x0,z0]=district.polygon[0],[x1,z1]=district.polygon[2];const span=Math.max(x1-x0,z1-z0);controls.target.set((x0+x1)/2,38,(z0+z1)/2);camera.position.set((x0+x1)/2+span*.36,Math.max(190,span*.32),(z0+z1)/2+span*.46);}}controls.update();}
 const districtSelect=app.querySelector<HTMLSelectElement>('#metro-district')!;districtSelect.onchange=()=>focus(districtSelect.value);
 const query=new URLSearchParams(location.search);const requestedDistrict=query.get('district'),requestedTime=query.get('time') as TimeMode|null;if(requestedDistrict){districtSelect.value=requestedDistrict;focus(requestedDistrict);}else focus('full');if(requestedTime&&['day','dusk','night'].includes(requestedTime))setTime(requestedTime);
 const clock=new THREE.Clock(),samples:number[]=[];function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);const delta=clock.getDelta();if(delta>0&&samples.length<180)samples.push(1/delta);const fps=samples.length?Math.min(240,samples.reduce((a,b)=>a+b,0)/samples.length):0;const info=renderer.info.render;status.textContent=`METRO3D · ${mode.toUpperCase()} · ${manifest.metrics.buildingInstances} BUILDINGS · ${info.calls} DRAWS · ${info.triangles.toLocaleString()} TRI · ${fps.toFixed(0)} FPS`;document.title=`METRO3D|${fps.toFixed(1)}|${info.calls}|${info.triangles}`;}animate();
}
