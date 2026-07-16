/* Loaded only after the user opens the 3D viewer. The landing route keeps the
 * city overview PNG and does not download Three.js or any district GLB. */
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import fixtureLayout from '../../assets/world/archive-city-v3-layout.json';
import fixtureManifest from '../../assets/runtime/v3/archive-city-v3-manifest.json';
import type { District } from './types';

type RuntimeOptions = { host: HTMLElement; status: HTMLElement; select: (text: string) => void; runtimeBase: string; generatedMode: boolean };
export type WorldViewer = { focus(id: string): void; setDistrict(id: District, visible: boolean): void; dispose(): void };
const colors: Record<District, number> = { archiveos: 0x26a9da, market: 0x8757c9, nexus: 0x4d8d57, logistics: 0xc87828, ledger: 0x3f6f9c, residential: 0x6a9b70, infrastructure: 0x64747f, vehicle: 0x23b6c7 };
const presets: Record<string, { position: [number, number, number]; target: [number, number, number] }> = {
  city:{position:[6800,6200,7200],target:[0,0,0]}, archiveos:{position:[850,720,2400],target:[0,0,1520]}, market:{position:[-900,700,-650],target:[-1900,0,-1500]}, nexus:{position:[1450,760,-900],target:[450,0,-1900]}, logistics:{position:[3550,780,-600],target:[2500,0,-1650]}, ledger:{position:[-750,720,2850],target:[-1680,0,1800]}, residential:{position:[3150,760,3050],target:[2200,0,1900]}, infrastructure:{position:[6400,5800,5900],target:[0,0,0]},
};

async function generatedJson<T>(base:string,path:string):Promise<T>{
  const response=await fetch(`${base.replace(/\/$/,'')}/${path}`);
  if(!response.ok) throw new Error(`generated-output:${response.status}:${path}`);
  return response.json() as Promise<T>;
}

export async function createWorldViewer(options: RuntimeOptions): Promise<WorldViewer> {
  const { host, status, select, runtimeBase, generatedMode } = options;
  let layout:any=fixtureLayout, runtimeManifest:any=fixtureManifest;
  if(generatedMode){
    try {
      [layout,runtimeManifest]=await Promise.all([
        generatedJson<any>(runtimeBase,'v3/metadata/archive-city-v3-layout.json'),
        generatedJson<any>(runtimeBase,'v3/metadata/archive-city-v3-manifest.json'),
      ]);
    } catch (error) {
      status.textContent='GENERATED OUTPUT UNAVAILABLE';
      throw error;
    }
  }
  const renderer = new THREE.WebGLRenderer({ antialias:true, powerPreference:'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5)); renderer.setSize(host.clientWidth, host.clientHeight); renderer.shadowMap.enabled=true; host.replaceChildren(renderer.domElement);
  const scene = new THREE.Scene(); scene.background=new THREE.Color(0x071018); scene.fog=new THREE.Fog(0x071018,2000,11000);
  const camera=new THREE.PerspectiveCamera(48,host.clientWidth/host.clientHeight,1,18000); const controls=new OrbitControls(camera,renderer.domElement); controls.maxDistance=15000; controls.minDistance=24; controls.maxPolarAngle=Math.PI*.48;
  scene.add(new THREE.HemisphereLight(0xa4dcff,0x142018,2.1)); const sun=new THREE.DirectionalLight(0xfff2d4,2.5); sun.position.set(55,90,38); scene.add(sun);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(10000,10000),new THREE.MeshStandardMaterial({color:0x14232a,roughness:.92})); ground.rotation.x=-Math.PI/2; scene.add(ground);
  const groups=new Map<District,THREE.Group>(); const root=new THREE.Group(); scene.add(root);
  (['archiveos','market','nexus','logistics','ledger','residential','infrastructure'] as District[]).forEach((district)=>{const group=new THREE.Group();groups.set(district,group);root.add(group);});
  const box=new THREE.BoxGeometry(1,1,1);
  for (const value of layout.instances as any[]) {
    const district=value.district as District; const group=groups.get(district) ?? groups.get('infrastructure')!;
    const state=value.state ?? 'building'; const height=state==='vehicle'?4:state==='tree'?18:state==='road'?0.35:state==='water'?0.08:state==='mountain'?460:state==='building'||state==='landmark'?32:8;
    const width=state==='road'?value.footprint??18:state==='water'?400:state==='terrain'?10000:state==='mountain'?240:state==='building'?28:12;
    const proxy=new THREE.Mesh(box,new THREE.MeshStandardMaterial({color:colors[district] ?? colors.infrastructure,roughness:.72,metalness:.12}));
    proxy.scale.set(width,height,state==='road'?Math.max(width,30):width*.72); proxy.position.set(value.position[0],height/2,value.position[2]); proxy.rotation.y=value.rotation?.[1] ?? 0; proxy.frustumCulled=true; proxy.userData=value; group.add(proxy);
  }
  const loader=new GLTFLoader(); const loaded=new Map<string,THREE.Group>(); const pathById=new Map<string,string>(runtimeManifest.districts.map((district:any)=>[String(district.id),String(district.runtimePath)]));
  const loadDistrict=(id:string)=>{ if(!runtimeBase||id==='city'||loaded.has(id)) return; const path=pathById.get(id); if(!path) return; status.textContent=`LOADING ${id.toUpperCase()} DETAIL…`; const resolved=generatedMode?path:path.replace(/^assets\//,''); loader.load(`${runtimeBase.replace(/\/$/,'')}/${resolved}`,(gltf)=>{gltf.scene.name=`Runtime_${id}`;scene.add(gltf.scene);loaded.set(id,gltf.scene);status.textContent=`${id.toUpperCase()} DETAIL READY`;},undefined,()=>{status.textContent=`RUNTIME UNAVAILABLE · ${id}`;}); };
  const focus=(id:string)=>{const preset=presets[id]??presets.city;camera.position.fromArray(preset.position);controls.target.fromArray(preset.target);controls.update();loadDistrict(id);};
  const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2(); renderer.domElement.addEventListener('pointerdown',(event)=>{pointer.x=event.offsetX/renderer.domElement.clientWidth*2-1;pointer.y=-(event.offsetY/renderer.domElement.clientHeight)*2+1;raycaster.setFromCamera(pointer,camera);const hit=raycaster.intersectObjects(root.children,true)[0];if(hit){const item=hit.object.userData as any;select(`${item.instanceId ?? 'district asset'} · ${item.assetId ?? 'proxy'} · ${item.district ?? 'infrastructure'}`);}});
  let frame=0;const animate=()=>{frame=requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);}; animate(); focus('city'); status.textContent=`OVERVIEW READY · ${layout.instances.length} INSTANCES`;
  const resize=()=>{renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();};window.addEventListener('resize',resize);
  return {focus,setDistrict:(id,visible)=>{const group=groups.get(id);if(group)group.visible=visible;const runtime=loaded.get(id);if(runtime)runtime.visible=visible;},dispose:()=>{cancelAnimationFrame(frame);window.removeEventListener('resize',resize);renderer.dispose();host.replaceChildren();}};
}
