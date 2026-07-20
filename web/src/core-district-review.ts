import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {mergeGeometries} from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {EffectComposer} from 'three/examples/jsm/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/examples/jsm/postprocessing/RenderPass.js';
import {GTAOPass} from 'three/examples/jsm/postprocessing/GTAOPass.js';
import {UnrealBloomPass} from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/examples/jsm/postprocessing/OutputPass.js';

type Family={id:string;status:string;lod:Record<string,string>};
type Instance={familyId:string;position:[number,number,number];rotationY:number;scale:number;chunk:string};
type StreamLight={position:[number,number,number];color:'cyan'|'warm';intensity:number;distanceM:number};
type HeroZone={id:string;status:string;uri:string;performanceUri?:string;actual3D:boolean;buildingCount:number;radiusM:number;geometryRevision?:number;geometry?:{triangles?:number}};
type Manifest={status:string;badges:string[];families:Family[];instances:Instance[];blocks:{id:string;type:string}[];infrastructure:{uri:string};urbanStream?:{uri:string;lengthM:number;bridges:number;accessPoints:number;viewerLights?:StreamLight[]};heroZones?:HeroZone[];metrics:Record<string,number>};
type CameraPreset={name:string;position:[number,number,number];target:[number,number,number]};

const cameras:CameraPreset[]=[
 {name:'aerial-core',position:[420,235,510],target:[15,42,0]},
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
 {name:'archive-water-plaza',position:[-315,6.20,-29],target:[-250,3.80,8]},
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
 // Precision expansion cameras hold a true 1.65m eye height above the +2.30m
 // upper terrace and frame an occupied room, water and bridge in one view.
 {name:'hero-s-ledger-terrace',position:[30,4.30,-24],target:[82,4.00,8]},
 {name:'hero-s-ledger-frontage',position:[96,4.05,-16],target:[58,4.15,10]},
 {name:'hero-s-transit-junction',position:[202,4.20,-18],target:[270,4.00,8]},
 {name:'hero-s-transit-entry',position:[302,4.05,-15],target:[265,4.15,10]},
 {name:'hero-s-core-corridor',position:[105,3.95,11],target:[185,4.4,-8]},
 {name:'hero-s-east-gateway',position:[315,3.95,10],target:[350,5.0,-20]},
 {name:'technical-status',position:[500,250,540],target:[0,35,0]},
 {name:'hero-archive-axis',position:[-340,4.8,-17],target:[-190,3.4,3]},
 {name:'hero-water-section',position:[-270,9.0,52],target:[-270,.3,0]},
 {name:'hero-gateway-approach',position:[-300,5.5,30],target:[-250,4.6,0]},
 {name:'hero-north-lobby',position:[-345,4.1,-22],target:[-300,3.4,58]},
 {name:'hero-south-frontage',position:[-345,4.1,22],target:[-300,3.4,-58]},
 {name:'hero-civic-terrace',position:[-330,4.6,10],target:[-300,4.0,24]},
 {name:'hero-archive-aerial',position:[-80,130,110],target:[-250,18,0]},
 // The upper civic terrace is at +2.30m; 3.95m is a true 1.65m eye height.
 {name:'hero-s-street-axis',position:[-340,3.95,-15],target:[-218,3.2,1]},
 {name:'hero-s-frontage',position:[-300,3.95,-18],target:[-325,4.2,-60]},
 // The upper civic terrace is +2.30m; 3.95m is a true 1.65m eye height.
 {name:'hero-s-water-plaza',position:[-350,4.35,-16],target:[-244,3.35,3]},
 // Opposite-bank gateway review keeps the occupied frontage and bridge
 // approach in one unobstructed 1.65m eye-level composition.
 {name:'hero-s-gateway',position:[-230,3.95,-28],target:[-250,3.5,0]},
];

function material(color:number,roughness=.72,metalness=0){return new THREE.MeshStandardMaterial({color,roughness,metalness});}
function stableFamilyTone(id:string){let value=2166136261;for(const char of id)value=(value^char.charCodeAt(0))*16777619;return Math.abs(value)%6;}
const supportMaterialPool=new Map<string,THREE.Material>();
function pooledSupportMaterial(key:string,create:()=>THREE.Material){const cached=supportMaterialPool.get(key);if(cached)return cached;const value=create();supportMaterialPool.set(key,value);return value;}
function finalizeSupportFamilyMaterials(root:THREE.Object3D,familyId:string,performance=false){
 // Office V5 is a frozen PO asset: neither its geometry nor authored material
 // is remapped by the district-review layer.
 if(familyId==='archive-cbd-twin-atrium-pq-v5')return;
 const tone=stableFamilyTone(familyId);
 const stone=[0x968b7b,0x838987,0x9b927d,0x777d7c,0xa19787,0x878177][tone],metal=[0x33434a,0x3e3833,0x2f4244,0x454b4b,0x4d4036,0x2c3b40][tone];
 root.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const current=child.material,name=current.name.toLowerCase();child.castShadow=!performance;child.receiveShadow=true;
  if(name.includes('occupied-window-glass'))child.material=pooledSupportMaterial(`occupied-window-${tone}-${performance}`,()=>performance?new THREE.MeshStandardMaterial({name:`support-occupied-window-${tone}`,color:[0x315562,0x425a60,0x304f59,0x40535a,0x34525c,0x39494f][tone],roughness:.22,metalness:.08,emissive:0xc46b2c,emissiveIntensity:.03}):proceduralGlazing(new THREE.MeshPhysicalMaterial({name:`support-occupied-window-${tone}`,color:[0x294d5a,0x3c555d,0x294c56,0x3b5156,0x2e5059,0x33464b][tone],roughness:.18,metalness:.03,clearcoat:.76,clearcoatRoughness:.14,emissive:0xc46b2c,emissiveIntensity:.03}),`support-occupied-${tone}`,.12));
  else if(name.includes('curtain-wall-glass')||name.includes('residential-glass')||name.includes('blue-gray-glass'))child.material=pooledSupportMaterial(`glass-${tone}-${performance}`,()=>performance?new THREE.MeshStandardMaterial({name:`support-glass-${tone}`,color:[0x315562,0x425a60,0x304f59,0x40535a,0x34525c,0x39494f][tone],roughness:.24,metalness:.12}):proceduralGlazing(new THREE.MeshPhysicalMaterial({name:`support-glass-${tone}`,color:[0x284d59,0x3d555c,0x2b4c56,0x3b5156,0x2e5059,0x33464b][tone],roughness:.16,metalness:.03,clearcoat:.82,clearcoatRoughness:.13}),`support-glass-${tone}`,.09));
  else if(name.includes('limestone')||name.includes('painted-concrete')||name.includes('precast')||name.includes('archive-warm-stone'))child.material=pooledSupportMaterial(`stone-${tone}`,()=>proceduralSurface(new THREE.MeshStandardMaterial({name:`support-stone-${tone}`,color:stone,roughness:.64}),`support-stone-${tone}`,.055,.18));
  else if(name.includes('granite')||name.includes('dark-stone'))child.material=pooledSupportMaterial('granite',()=>new THREE.MeshStandardMaterial({name:'support-granite',color:0x343839,roughness:.56}));
  else if(name.includes('dark-metal')||name.includes('painted-steel')||name.includes('service-charcoal'))child.material=pooledSupportMaterial(`dark-metal-${tone}`,()=>new THREE.MeshStandardMaterial({name:`support-dark-metal-${tone}`,color:metal,roughness:.42,metalness:.46}));
  else if(name.includes('light-metal')||name.includes('aluminum')||name.includes('archive-metal'))child.material=pooledSupportMaterial('light-metal',()=>new THREE.MeshStandardMaterial({name:'support-light-metal',color:0x6f7778,roughness:.38,metalness:.58}));
  else if(name.includes('ledger-bronze'))child.material=pooledSupportMaterial('bronze',()=>new THREE.MeshStandardMaterial({name:'support-bronze',color:0x705039,roughness:.38,metalness:.55}));
  else if(name.includes('dry-stone'))child.material=pooledSupportMaterial('dry-stone',()=>new THREE.MeshStandardMaterial({name:'support-dry-stone',color:0x696b67,roughness:.82}));
  else if(name.includes('warm-interior'))child.material=pooledSupportMaterial('warm-interior',()=>new THREE.MeshStandardMaterial({name:'support-warm-interior',color:0x5f3b29,roughness:.64,emissive:0x7d3514,emissiveIntensity:.5}));
  else if(name.includes('sidewalk'))child.material=pooledSupportMaterial('sidewalk',()=>new THREE.MeshStandardMaterial({name:'support-sidewalk',color:0x777a75,roughness:.88}));
  else if(name.includes('asphalt'))child.material=pooledSupportMaterial('asphalt',()=>new THREE.MeshStandardMaterial({name:'support-asphalt',color:0x252a2d,roughness:.92}));
 });
}
function finalizeInfrastructureMaterials(root:THREE.Object3D){
 const palette={asphalt:material(0x242a2d,.9),sidewalk:material(0x8a8e88,.82),plaza:material(0xaaa394,.74),curb:material(0x626965,.86),foliage:material(0x285b32,.88),groundcover:material(0x416044,.94),timber:material(0x56381f,.72),human:material(0x786f67,.7),vehicle:material(0x303b46,.52,.2),metal:material(0x29343b,.45,.55),glass:new THREE.MeshPhysicalMaterial({color:0x345e6d,roughness:.2,metalness:0,transmission:.08,transparent:true,opacity:.82})};
 root.traverse(child=>{if(!(child instanceof THREE.Mesh))return;child.castShadow=true;child.receiveShadow=true;const name=child.name.toLowerCase();if(name.includes('tree-crown'))child.material=palette.foliage;else if(name.includes('groundcover')||name.includes('shrub'))child.material=palette.groundcover;else if(name.includes('tree-trunk'))child.material=palette.timber;else if(name.includes('road-asphalt')||name.includes('bus-bay'))child.material=palette.asphalt;else if(name.includes('sidewalk')||name.includes('crosswalk'))child.material=palette.sidewalk;else if(name.includes('plaza')||name.includes('median')||name.includes('parcel-surface'))child.material=palette.plaza;else if(name.includes('curb'))child.material=palette.curb;else if(name.includes('human'))child.material=palette.human;else if(name.includes('vehicle'))child.material=palette.vehicle;else if(name.includes('glass')||name.includes('station-entrance'))child.material=palette.glass;else if(name.includes('streetlight')||name.includes('bollard')||name.includes('rack'))child.material=palette.metal;});
}
const heroMaterialPool=new Map<string,THREE.Material>();
function proceduralSurface(material:THREE.MeshStandardMaterial,key:string,amount=.06,scale=.22){
 const bump=(amount*.30).toFixed(4);
 const paver=key==='promenade-paver'?"float archiveGrid=min(abs(fract(vArchiveWorldPosition.x*.50)-.5),abs(fract(vArchiveWorldPosition.z*.72)-.5));float archiveJoint=1.0-smoothstep(.018,.055,archiveGrid);diffuseColor.rgb*=1.0-archiveJoint*.18;":"";
 material.onBeforeCompile=shader=>{shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vArchiveWorldPosition;').replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvArchiveWorldPosition=(modelMatrix*vec4(transformed,1.0)).xyz;');shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 vArchiveWorldPosition;\nfloat archiveHash(vec3 p){return fract(sin(dot(p,vec3(12.9898,78.233,45.164)))*43758.5453);}') .replace('#include <color_fragment>','#include <color_fragment>\nfloat archiveVariation=(archiveHash(floor(vArchiveWorldPosition*'+scale.toFixed(3)+'))-.5)*'+amount.toFixed(3)+';float archiveFine=(sin(vArchiveWorldPosition.x*5.7)+sin(vArchiveWorldPosition.y*6.3)+cos(vArchiveWorldPosition.z*7.1))*.006;diffuseColor.rgb*=1.0+archiveVariation+archiveFine;'+paver).replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=clamp(roughnessFactor+archiveVariation*.75,0.08,1.0);').replace('#include <normal_fragment_maps>','#include <normal_fragment_maps>\nvec3 archiveBump=vec3(sin(vArchiveWorldPosition.y*5.1+vArchiveWorldPosition.z*2.7),sin(vArchiveWorldPosition.z*4.7+vArchiveWorldPosition.x*3.1),cos(vArchiveWorldPosition.x*5.3-vArchiveWorldPosition.y*2.9));normal=normalize(normal+archiveBump*'+bump+');');};
 material.customProgramCacheKey=()=>`archive-procedural-${key}-${amount}-${scale}`;return material;
}
function pooledHeroMaterial(key:string,create:()=>THREE.Material){const cached=heroMaterialPool.get(key);if(cached)return cached;const value=create();heroMaterialPool.set(key,value);return value;}
function proceduralGlazing<T extends THREE.MeshStandardMaterial>(glass:T,key:string,variation=.10){
 glass.onBeforeCompile=shader=>{shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vArchiveGlassWorld;').replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvArchiveGlassWorld=(modelMatrix*vec4(transformed,1.0)).xyz;');shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 vArchiveGlassWorld;\nfloat archiveGlassHash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}') .replace('#include <color_fragment>','#include <color_fragment>\nfloat archiveFloor=floor(vArchiveGlassWorld.y/3.55);float archiveBay=floor((vArchiveGlassWorld.x+vArchiveGlassWorld.z)*.18);float archiveGlassVariation=(archiveGlassHash(vec2(archiveFloor,archiveBay))-.5)*'+variation.toFixed(3)+';float archiveSpandrel=smoothstep(.72,.93,fract(vArchiveGlassWorld.y/3.55));diffuseColor.rgb*=1.0+archiveGlassVariation-archiveSpandrel*.10;').replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=clamp(roughnessFactor+archiveGlassVariation*.28,0.08,.48);');};
 glass.customProgramCacheKey=()=>`archive-procedural-glazing-${key}-${variation}`;return glass;
}
function proceduralWaterMaterial(performance=false){
 const water=performance
  ?new THREE.MeshStandardMaterial({name:'hero-water-performance',color:0x174854,roughness:.42,metalness:0})
  :new THREE.MeshPhysicalMaterial({name:'hero-water-cinematic',color:0x123f4a,roughness:.22,metalness:0,transmission:.08,transparent:true,opacity:.94,depthWrite:true,clearcoat:.68,clearcoatRoughness:.16,ior:1.333,thickness:.38});
 if(!performance){water.onBeforeCompile=shader=>{shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vArchiveWaterWorld;').replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvArchiveWaterWorld=(modelMatrix*vec4(transformed,1.0)).xyz;');shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 vArchiveWaterWorld;').replace('#include <normal_fragment_maps>','#include <normal_fragment_maps>\nfloat streamWaveA=sin(vArchiveWaterWorld.x*.37+vArchiveWaterWorld.z*.91)+.45*sin(vArchiveWaterWorld.x*1.23-vArchiveWaterWorld.z*.58);float streamWaveB=cos(vArchiveWaterWorld.x*.61-vArchiveWaterWorld.z*.43)+.35*cos(vArchiveWaterWorld.x*1.57+vArchiveWaterWorld.z*.74);normal=normalize(normal+vec3(streamWaveA*.014,0.0,streamWaveB*.011));').replace('#include <color_fragment>','#include <color_fragment>\nfloat streamFlow=.965+.035*sin(vArchiveWaterWorld.x*.19+vArchiveWaterWorld.z*.53);float streamCross=clamp(abs(vArchiveWaterWorld.z)/8.0,0.0,1.0);vec3 streamDeep=vec3(.035,.145,.180);vec3 streamShallow=vec3(.105,.265,.270);diffuseColor.rgb=mix(streamDeep,streamShallow,smoothstep(.30,1.0,streamCross))*streamFlow;');};water.customProgramCacheKey=()=> 'archive-procedural-water-v3-depth-edge';}
 return water;
}
function finalizeHeroMaterials(root:THREE.Object3D,performance=false,zoneId=''){
 root.updateMatrixWorld(true);const materialWorldPosition=new THREE.Vector3();
 root.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const current=child.material,name=current.name.toLowerCase();
  child.getWorldPosition(materialWorldPosition);const transit=zoneId==='ledger-transit-corridor'&&materialWorldPosition.x>=180,archive=zoneId==='archive-water-plaza',palette=archive?'archive':transit?'transit':'ledger';
  child.castShadow=true;child.receiveShadow=true;
  if(name.includes('foliage-'))child.geometry.computeVertexNormals();
  if(name.includes('shallow-water'))child.material=pooledHeroMaterial(`water-${performance}`,()=>proceduralWaterMaterial(performance));
  else if(name.includes('frontage-glass')||name.includes('pavilion-glass'))child.material=pooledHeroMaterial(`frontage-glass-${palette}-${performance}`,()=>proceduralGlazing(performance?new THREE.MeshStandardMaterial({name:'frontage-glass-'+palette,color:transit?0x50646a:archive?0x244b58:0x3b4142,roughness:.24,metalness:.08}):new THREE.MeshPhysicalMaterial({name:'frontage-glass-'+palette,color:transit?0x3d5b62:archive?0x214b59:0x353d3e,roughness:transit?.18:.14,metalness:transit?.12:.03,transmission:transit?.20:.28,transparent:true,opacity:transit?.84:.78,depthWrite:true,clearcoat:.84,clearcoatRoughness:.10,ior:1.46,thickness:.34}),'frontage-'+palette,.08));
  else if(name.includes('occupied-window-glass'))child.material=pooledHeroMaterial('occupied-window-glass',()=>proceduralGlazing(new THREE.MeshPhysicalMaterial({name:'occupied-window-glass',color:0x183945,roughness:.15,metalness:.05,clearcoat:.72,clearcoatRoughness:.10,emissive:0xa45b23,emissiveIntensity:.08}),'occupied',.13));
  else if(name.includes('blue-gray-glass'))child.material=pooledHeroMaterial(`blue-gray-glass-${performance}`,()=>proceduralGlazing(performance?new THREE.MeshStandardMaterial({name:'blue-gray-glass',color:0x244852,roughness:.28,metalness:.10}):new THREE.MeshPhysicalMaterial({name:'blue-gray-glass',color:0x214754,roughness:.15,metalness:.04,clearcoat:.88,clearcoatRoughness:.11}),'tower',.115));
  else if(name.includes('archive-warm-stone'))child.material=pooledHeroMaterial('archive-warm-stone-'+palette,()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'archive-warm-stone-'+palette,color:transit?0x7f8988:0xa89478,roughness:transit?.58:.66}),'archive-warm-stone-'+palette,.095,.16));
  else if(name.includes('ledger-limestone'))child.material=pooledHeroMaterial('ledger-limestone',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'ledger-limestone',color:0x77756e,roughness:.62}),'ledger-limestone',.085,.18));
  else if(name.includes('ledger-granite'))child.material=pooledHeroMaterial('ledger-granite',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'ledger-granite',color:0x313638,roughness:.56}),'ledger-granite',.04,.28));
  else if(name.includes('archive-metal'))child.material=pooledHeroMaterial('archive-metal-'+palette,()=>new THREE.MeshStandardMaterial({name:'archive-metal-'+palette,color:transit?0x516168:0x294c56,roughness:transit?.27:.32,metalness:transit?.74:.62}));
  else if(name.includes('ledger-bronze'))child.material=pooledHeroMaterial('ledger-bronze',()=>new THREE.MeshStandardMaterial({name:'ledger-bronze',color:0x76502f,roughness:.34,metalness:.68}));
  else if(name.includes('dry-stone'))child.material=pooledHeroMaterial('dry-stone',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'dry-stone',color:0x686963,roughness:.78}),'dry-stone',.065,.32));
  else if(name.includes('wet-stone'))child.material=pooledHeroMaterial('wet-stone',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'wet-stone',color:0x3b4746,roughness:.34}),'wet-stone',.035,.38));
  else if(name.includes('promenade-paver'))child.material=pooledHeroMaterial('promenade-paver',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'promenade-paver',color:0x555d59,roughness:.82}),'promenade-paver',.075,.28));
  else if(name.includes('foliage-deep'))child.material=pooledHeroMaterial('foliage-deep',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'foliage-deep',color:0x173f29,roughness:.90}),'foliage-deep',.18,.56));
  else if(name.includes('foliage-mid'))child.material=pooledHeroMaterial('foliage-mid',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'foliage-mid',color:0x2f613c,roughness:.88}),'foliage-mid',.16,.52));
  else if(name.includes('foliage-light'))child.material=pooledHeroMaterial('foliage-light',()=>proceduralSurface(new THREE.MeshStandardMaterial({name:'foliage-light',color:0x52754a,roughness:.86}),'foliage-light',.14,.48));
  else if(name.includes('timber-accent'))child.material=pooledHeroMaterial('timber-accent',()=>new THREE.MeshStandardMaterial({name:'timber-accent',color:0x5c3b20,roughness:.68}));
  else if(name.includes('warm-interior'))child.material=pooledHeroMaterial('warm-interior',()=>new THREE.MeshStandardMaterial({name:'warm-interior',color:0x51392f,roughness:.58,emissive:0xb55b22,emissiveIntensity:.72}));
  else if(name.includes('warm-light'))child.material=pooledHeroMaterial('warm-light',()=>new THREE.MeshStandardMaterial({name:'warm-light',color:0xffd5a0,roughness:.42,emissive:0xffa84f,emissiveIntensity:1.15}));
  else if(name.includes('archive-cyan-light'))child.material=pooledHeroMaterial('archive-cyan-light',()=>new THREE.MeshStandardMaterial({name:'archive-cyan-light',color:0x70d7df,roughness:.38,emissive:0x208a9b,emissiveIntensity:.95}));
  else if(performance){const tone=stableFamilyTone(name),key='performance-generic-'+tone;child.material=pooledHeroMaterial(key,()=>new THREE.MeshStandardMaterial({name:key,color:[0x6f7775,0x596c70,0x81786b,0x4e5958,0x756b5f,0x485f63][tone],roughness:.72,metalness:tone===1||tone===5?.14:.03}));}
 });
}

function consolidatePerformanceRoot(root:THREE.Object3D){
 root.updateMatrixWorld(true);const buckets=new Map<string,{material:THREE.Material;geometries:THREE.BufferGeometry[]}>();
 root.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const key=child.material.uuid,bucket=buckets.get(key)??{material:child.material,geometries:[] as THREE.BufferGeometry[]};bucket.geometries.push(child.geometry.clone().applyMatrix4(child.matrixWorld));buckets.set(key,bucket);});
 const merged=new THREE.Group();for(const bucket of buckets.values()){const geometry=mergeGeometries(bucket.geometries,false);if(!geometry)throw new Error('performance hero merge failure');const mesh=new THREE.Mesh(geometry,bucket.material);mesh.frustumCulled=true;merged.add(mesh);}root.clear();root.add(merged);
}
function needsPerformanceConsolidation(root:THREE.Object3D){let meshCount=0;root.traverse(child=>{if(child instanceof THREE.Mesh)meshCount++;});return meshCount>32;}

export async function createCoreDistrictReview(app:HTMLDivElement,base:string,manifestFile='core-district-3d.json'){
 const manifest=await fetch(`${base}/manifest/${manifestFile}`).then(r=>{if(!r.ok)throw new Error(`manifest ${r.status}`);return r.json() as Promise<Manifest>});
 const hasExpandedZones=manifest.heroZones?.some(zone=>zone.id==='ledger-transit-corridor')??false;
 const query=new URLSearchParams(location.search),requestedLod=query.get('lod'),performanceMode=query.get('performance')==='1',cinematicMode=!performanceMode&&query.get('cinematic')!=='0',reviewLod=requestedLod==='LOD0'||requestedLod==='LOD2'?requestedLod:performanceMode?'LOD2':'LOD1';
 const preset=Number(query.get('camera')??0),selected=cameras[preset%cameras.length],reviewHeroCamera=!!manifest.heroZones?.length&&preset>=35;
 // Street review streams the complete Hero GLB plus only the surrounding
 // 300 m support context.  This mirrors the authored chunk corridor and keeps
 // every object that can contribute to the 40-degree review frustum.
 const performanceFocus=new THREE.Vector3(...selected.target),performanceRadiusM=reviewHeroCamera?220:Infinity;
 const includePerformanceInstance=(item:Instance)=>!performanceMode||!Number.isFinite(performanceRadiusM)||Math.hypot(item.position[0]-performanceFocus.x,item.position[2]-performanceFocus.z)<performanceRadiusM;
 const includePerformanceHero=(zone:HeroZone)=>!performanceMode||!reviewHeroCamera||(performanceFocus.x<-100?zone.id==='archive-water-plaza':zone.id==='ledger-transit-corridor');
 const streamLabel=manifest.urbanStream?`<dt>Stream</dt><dd>${manifest.urbanStream.lengthM.toFixed(0)}m / ${manifest.urbanStream.bridges} bridges</dd>`:'';
 app.innerHTML=`<main class="core3d"><aside><div class="brand"><span>ARCHIVE</span><strong>${manifest.urbanStream?'CORE + URBAN STREAM':'CORE DISTRICT 3D'}</strong></div><p class="core-warning">${manifest.badges.join('<br/>')}</p><button id="core-aerial">Aerial</button><button id="core-street">Street</button><button id="core-day">Day</button><button id="core-night">Night</button><label><input id="core-infra" type="checkbox" checked/> Street/Public Realm</label><label><input id="core-buildings" type="checkbox" checked/> Buildings</label>${manifest.urbanStream?'<label><input id="core-stream" type="checkbox" checked/> Urban Stream</label>':''}<label>LOD<select id="core-lod"><option>LOD1</option><option>LOD0</option><option>LOD2</option></select></label><dl><dt>Actual families</dt><dd>${manifest.metrics.actualFamilies}</dd><dt>Actual blocks</dt><dd>${manifest.metrics.actualBlocks}</dd><dt>Instances</dt><dd>${manifest.metrics.buildingInstances}</dd><dt>Proxy ratio</dt><dd>${(manifest.metrics.planningProxyRatio*100).toFixed(1)}%</dd>${streamLabel}</dl><div id="core-perf">LOADING ACTUAL GLB…</div></aside><section><div id="core-canvas"></div><div class="core-badge">${manifest.badges.join(' · ')}</div></section></main>`;
 if(query.get('clean')==='1')app.querySelector('.core3d')?.classList.add('clean-capture');
 const host=app.querySelector<HTMLElement>('#core-canvas')!,perf=app.querySelector<HTMLElement>('#core-perf')!;
 const scene=new THREE.Scene();scene.background=null;scene.fog=new THREE.Fog(0xaebdc0,1450,2850);
 const skyUniforms={topColor:{value:new THREE.Color(0x365f85)},bottomColor:{value:new THREE.Color(0xd6d1c7)},offset:{value:24.0},exponent:{value:.72}};
 const sky=new THREE.Mesh(new THREE.SphereGeometry(2600,32,16),new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,uniforms:skyUniforms,vertexShader:'varying vec3 vWorldPosition; void main(){vec4 worldPosition=modelMatrix*vec4(position,1.0);vWorldPosition=worldPosition.xyz;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'uniform vec3 topColor;uniform vec3 bottomColor;uniform float offset;uniform float exponent;varying vec3 vWorldPosition;void main(){float h=normalize(vWorldPosition+vec3(0.0,offset,0.0)).y;gl_FragColor=vec4(mix(bottomColor,topColor,max(pow(max(h,0.0),exponent),0.0)),1.0);}'}));scene.add(sky);
 const camera=new THREE.PerspectiveCamera(manifest.heroZones?.length?45:52,1,.35,4000);camera.position.set(740,570,790);
 const renderer=new THREE.WebGLRenderer({antialias:!performanceMode,preserveDrawingBuffer:!performanceMode,powerPreference:'high-performance',stencil:false});renderer.setPixelRatio(performanceMode?.28:Math.min(devicePixelRatio,1));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.AgXToneMapping;renderer.toneMappingExposure=.98;renderer.shadowMap.enabled=!performanceMode;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.shadowMap.autoUpdate=!performanceMode&&!!manifest.heroZones?.length;host.append(renderer.domElement);
 const composer=cinematicMode?new EffectComposer(renderer):undefined;
 if(composer){composer.addPass(new RenderPass(scene,camera));const gtao=new GTAOPass(scene,camera,window.innerWidth,window.innerHeight);gtao.updateGtaoMaterial({radius:.92,distanceExponent:1.66,thickness:.74,distanceFallOff:1,scale:1,samples:24});gtao.updatePdMaterial({samples:10,radius:2.6,radiusExponent:2});gtao.blendIntensity=.62;composer.addPass(gtao);const bloom=new UnrealBloomPass(new THREE.Vector2(window.innerWidth,window.innerHeight),.10,.18,.96);composer.addPass(bloom);composer.addPass(new OutputPass());}
 if(!performanceMode){const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(new RoomEnvironment(),.04).texture;scene.environmentIntensity=.34;pmrem.dispose();}
 const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,55,0);controls.enableDamping=!performanceMode;
 const hemi=new THREE.HemisphereLight(0xeaf3f5,0x29322d,.38);scene.add(hemi);
 const lightingTarget=new THREE.Vector3(...selected.target);const sun=new THREE.DirectionalLight(0xffd2a0,4.35);sun.position.copy(lightingTarget).add(new THREE.Vector3(-390,310,-430));sun.castShadow=!performanceMode&&!!manifest.heroZones?.length;sun.shadow.mapSize.set(performanceMode?1024:4096,performanceMode?1024:4096);sun.shadow.camera.left=-230;sun.shadow.camera.right=230;sun.shadow.camera.top=180;sun.shadow.camera.bottom=-180;sun.shadow.camera.near=60;sun.shadow.camera.far=1200;sun.shadow.bias=-.00018;sun.target.position.copy(lightingTarget);scene.add(sun,sun.target);
 const coolFill=new THREE.DirectionalLight(0xb8d5df,.16);coolFill.position.copy(lightingTarget).add(new THREE.Vector3(430,260,480));coolFill.target.position.copy(lightingTarget);scene.add(coolFill,coolFill.target);
 const plazaLights=[[-130,28,105],[250,28,105],[0,24,-220],[-260,18,-80],[340,20,80]].map(([x,y,z])=>{const light=new THREE.PointLight(0xffd39a,0,220,1.4);light.position.set(x,y,z);scene.add(light);return light;});
 const heroLights=(manifest.heroZones?.length?[[-326,8,-58],[-260,10,-60],[-190,8,-56],[-326,8,58],[-258,10,60],[-188,8,56]]:[]).map(([x,y,z])=>{const light=new THREE.PointLight(0xffb46c,0,45,2.15);light.position.set(x,y,z);scene.add(light);return light;});
 const heroAtriumLights=(manifest.heroZones?.length?[[-329.5,6.8,50.2],[-322.2,6.8,-49.8]]:[]).map(([x,y,z])=>{const light=new THREE.PointLight(0xffba78,0,31,2.1);light.position.set(x,y,z);scene.add(light);return light;});
 const heroFrontageLights=(manifest.heroZones?.length?[-320,-252,-187].flatMap(x=>[-39,39].flatMap(z=>[[x,5.4,z],[x-8,4.2,z]])):[]).map(([x,y,z],index)=>{const light=new THREE.PointLight(index%2?0xffa96a:0xffc78e,0,index%2?30:38,2.05);light.position.set(x,y,z);scene.add(light);return light;});
 const heroRouteLights=(manifest.heroZones?.length?[-335,-290,-245,-200,-165].flatMap(x=>[-13,13].map(z=>[x,4.2,z])):[]).map(([x,y,z])=>{const light=new THREE.PointLight(0xffc27c,0,48,1.85);light.position.set(x,y,z);scene.add(light);return light;});
 const heroPromenadeLights=(manifest.heroZones?.length?[-330,-285,-240,-195,-165].flatMap(x=>[-27,27].map(z=>[x,5.4,z])):[]).map(([x,y,z])=>{const light=new THREE.PointLight(0xffb66f,0,42,1.75);light.position.set(x,y,z);scene.add(light);return light;});
 const heroBridgeLights=(manifest.heroZones?.length?[[-250,5.2,-10],[-250,5.2,10],[-300,5.6,-22]]:[]).map(([x,y,z])=>{const light=new THREE.PointLight(0x70dce4,0,52,1.9);light.position.set(x,y,z);scene.add(light);return light;});
 const expandedNodeLights=(hasExpandedZones?[[60,6.2,-40],[60,6.2,40],[260,6.4,-40],[260,6.4,40],[238,7.2,37],[282,7.2,37]]:[]).map(([x,y,z],index)=>{const light=new THREE.PointLight(index<2?0xffb06a:0xffc27c,0,index<2?48:42,2.05);light.position.set(x,y,z);scene.add(light);return light;});
 const expandedRouteLights=(hasExpandedZones?[-100,-52,-4,44,92,140,188,236,284,332].flatMap(x=>[-14,14].map(z=>[x,4.3,z])):[]).map(([x,y,z])=>{const light=new THREE.PointLight(0xffbd78,0,38,1.9);light.position.set(x,y,z);scene.add(light);return light;});
 const streamLights=(manifest.urbanStream?.viewerLights??[]).map(spec=>{const light=new THREE.PointLight(spec.color==='cyan'?0x5eeeff:0xffc77d,0,spec.distanceM,1.6);light.position.set(...spec.position);scene.add(light);return {light,intensity:spec.intensity};});
 const setSupportMaterialState=(night:boolean)=>buildings.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const mat=child.material as THREE.MeshStandardMaterial;if(mat.name.includes('support-occupied-window'))mat.emissiveIntensity=night?.46:.02;else if(mat.name.includes('support-warm-interior'))mat.emissiveIntensity=night?1.38:.18;});
 const setHeroMaterialState=(night:boolean)=>{heroZones.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const mat=child.material as THREE.MeshStandardMaterial,name=mat.name.toLowerCase();if(name.includes('occupied-window-glass'))mat.emissiveIntensity=night?1.05:.02;else if(name.includes('warm-interior'))mat.emissiveIntensity=night?2.45:.20;else if(name.includes('warm-light'))mat.emissiveIntensity=night?1.72:.07;else if(name.includes('archive-cyan-light'))mat.emissiveIntensity=night?.88:.03;});setSupportMaterialState(night);};
 const groundMaterial=new THREE.MeshStandardMaterial({color:0x343b37,roughness:.94});
 if(manifest.urbanStream){for(const side of [-1,1]){const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,650),groundMaterial);ground.rotation.x=-Math.PI/2;ground.position.set(0,-.08,side*350);ground.receiveShadow=true;scene.add(ground);}}else{const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,1400),groundMaterial);ground.rotation.x=-Math.PI/2;ground.position.y=-.08;ground.receiveShadow=true;scene.add(ground);}
 const loader=new GLTFLoader(),buildings=new THREE.Group(),infrastructure=new THREE.Group(),urbanStream=new THREE.Group(),heroZones=new THREE.Group();scene.add(buildings,infrastructure,urbanStream,heroZones);const started=performance.now();
 if(performanceMode){document.title='CORE3D_LOADING|FAMILIES';await new Promise<void>(resolve=>setTimeout(resolve,0));}
 const assetRevision='v18-metropolitan-aaa-envelope',loaded=new Map<string,THREE.Object3D>();await Promise.all(manifest.families.map(async family=>{const gltf=await loader.loadAsync(`${base}/${family.lod[reviewLod]}?rev=${assetRevision}`);finalizeSupportFamilyMaterials(gltf.scene,family.id,performanceMode);loaded.set(family.id,gltf.scene);}));
 if(performanceMode){document.title='CORE3D_LOADING|SUPPORT_ENTRIES';await new Promise<void>(resolve=>setTimeout(resolve,0));}
 type FamilyMaterialEntry={familyId:string;material:THREE.Material;geometry:THREE.BufferGeometry;items:Instance[]};
 const supportEntries:FamilyMaterialEntry[]=[];
 for(const family of manifest.families){const source=loaded.get(family.id);if(!source)continue;source.updateMatrixWorld(true);const items=manifest.instances.filter(item=>item.familyId===family.id&&includePerformanceInstance(item));if(!items.length)continue;const buckets=new Map<string,{material:THREE.Material;geometries:THREE.BufferGeometry[]}>();source.traverse(child=>{if(!(child instanceof THREE.Mesh)||Array.isArray(child.material))return;const key=performanceMode?'performance-family':child.material.uuid,bucket=buckets.get(key)??{material:performanceMode?pooledSupportMaterial(`performance-family-${stableFamilyTone(family.id)}`,()=>new THREE.MeshStandardMaterial({name:'performance-family',color:[0x66777a,0x77736a,0x596b70,0x6d7472,0x756b5f,0x52666b][stableFamilyTone(family.id)],roughness:.66,metalness:.08})):child.material as THREE.Material,geometries:[] as THREE.BufferGeometry[]};bucket.geometries.push(child.geometry.clone().applyMatrix4(child.matrixWorld));buckets.set(key,bucket);});for(const [materialId,bucket] of buckets){const geometry=bucket.geometries.length===1?bucket.geometries[0]:mergeGeometries(bucket.geometries,false);if(!geometry)throw new Error(`merge failure ${family.id}/${materialId}`);supportEntries.push({familyId:family.id,material:bucket.material,geometry,items});}if(performanceMode)await new Promise<void>(resolve=>setTimeout(resolve,0));}
 for(const entry of supportEntries){const mesh=new THREE.InstancedMesh(entry.geometry,entry.material,entry.items.length);mesh.name=`batch-${entry.familyId}-${entry.material.name}`;mesh.userData={familyId:entry.familyId,status:'ACTUAL_GLTF_MATERIAL_BATCH'};mesh.castShadow=!performanceMode;mesh.receiveShadow=true;entry.items.forEach((item,index)=>{mesh.setMatrixAt(index,new THREE.Matrix4().compose(new THREE.Vector3(...item.position),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),item.rotationY),new THREE.Vector3(item.scale,item.scale,item.scale)));});mesh.instanceMatrix.needsUpdate=true;buildings.add(mesh);}
 if(performanceMode){document.title='CORE3D_LOADING|HERO_GLBS';await new Promise<void>(resolve=>setTimeout(resolve,0));}
 // Precision Hero assets replace the stream corridor.  District infrastructure
 // stays present for aerial/context cameras, but its legacy centreline road is
 // excluded from Hero street evidence so vehicles never overlap the water.
 if(!reviewHeroCamera){const infra=await loader.loadAsync(`${base}/${manifest.infrastructure.uri}?rev=${assetRevision}`);finalizeInfrastructureMaterials(infra.scene);infrastructure.add(infra.scene);}
 if(manifest.urbanStream&&!manifest.heroZones?.length){const stream=await loader.loadAsync(`${base}/${manifest.urbanStream.uri}?rev=v11-stream-final`);urbanStream.add(stream.scene);}
 const loadedHeroZoneIds:string[]=[];
 if(manifest.heroZones){for(const zone of manifest.heroZones.filter(includePerformanceHero)){const heroAssetRevision=`${zone.status}-g${zone.geometryRevision??0}-${zone.geometry?.triangles??'geometry'}-${performanceMode?'lod2-v5':'hero'}`,heroUri=performanceMode&&zone.performanceUri?zone.performanceUri:zone.uri;const hero=await loader.loadAsync(`${base}/${heroUri}?rev=${encodeURIComponent(heroAssetRevision)}`);finalizeHeroMaterials(hero.scene,performanceMode,zone.id);if(performanceMode&&needsPerformanceConsolidation(hero.scene))consolidatePerformanceRoot(hero.scene);hero.scene.userData={heroZone:zone.id,status:zone.status,actual3D:true,performanceLod:performanceMode,preconsolidatedByMaterial:true};heroZones.add(hero.scene);loadedHeroZoneIds.push(zone.id);if(performanceMode)await new Promise<void>(resolve=>setTimeout(resolve,0));}}
 if(performanceMode){document.title='CORE3D_LOADING|RENDER_SETUP';await new Promise<void>(resolve=>setTimeout(resolve,0));}
 // Read-only screenshot diagnostics identify the actual mesh/material under a
 // failed review pixel, so blank-wall defects can be fixed at their source.
 (window as any).__archiveReviewPick=(clientX:number,clientY:number)=>{const rect=renderer.domElement.getBoundingClientRect(),pointer=new THREE.Vector2(((clientX-rect.left)/rect.width)*2-1,-((clientY-rect.top)/rect.height)*2+1),raycaster=new THREE.Raycaster();raycaster.setFromCamera(pointer,camera);return raycaster.intersectObjects([heroZones,buildings,infrastructure],true).slice(0,8).map(hit=>{const mesh=hit.object as THREE.Mesh,mat=Array.isArray(mesh.material)?mesh.material[0]:mesh.material;return {name:mesh.name,material:mat?.name??'none',distance:+hit.distance.toFixed(2),familyId:mesh.userData?.familyId??mesh.parent?.userData?.familyId??null,heroZone:mesh.parent?.userData?.heroZone??null};});};
 const ready=performance.now();perf.textContent=`READY ${Math.round(ready-started)}ms · ${reviewLod} · calibrated material hierarchy`;
 const activeSupportInstances=supportEntries.reduce((sum,entry)=>sum+entry.items.length,0);
 let frames=0,last=performance.now(),previous=last,fps=0,warmupReset=false;const frameTimes:number[]=[];
 function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,true);composer?.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}
 new ResizeObserver(resize).observe(host);resize();
 function animate(){requestAnimationFrame(animate);if(!performanceMode)controls.update();if(composer)composer.render();else renderer.render(scene,camera);frames++;const now=performance.now(),delta=now-previous;previous=now;if(!warmupReset&&now-ready>8000){frameTimes.length=0;frames=0;last=now;warmupReset=true;}if(delta>0&&delta<1000&&warmupReset){frameTimes.push(delta);if(frameTimes.length>600)frameTimes.shift();}if(now-last>=1000){fps=frames*1000/(now-last);frames=0;last=now;const sorted=[...frameTimes].sort((a,b)=>a-b),p99=sorted[Math.max(0,Math.ceil(sorted.length*.99)-1)]??1000,lowFps=1000/p99,info=renderer.info.render;perf.dataset.metrics=JSON.stringify({readyMs:Math.round(ready-started),fps:+fps.toFixed(1),lowFps:+lowFps.toFixed(1),sampleFrames:frameTimes.length,drawCalls:info.calls,triangles:info.triangles,instances:manifest.instances.length,activeSupportInstances,pixelRatio:renderer.getPixelRatio(),lod:reviewLod,cinematic:cinematicMode});perf.textContent=`READY ${Math.round(ready-started)}ms · ${reviewLod} · FPS ${fps.toFixed(1)} · 1% low ${lowFps.toFixed(1)} · draw ${info.calls} · tri ${info.triangles.toLocaleString()}`;document.title=`CORE3D|${fps.toFixed(1)}|${lowFps.toFixed(1)}|${info.calls}|${info.triangles}`;}}
 animate();
const setTime=(mode:'day'|'dusk'|'night')=>{if(mode==='night'){skyUniforms.topColor.value.set(0x030a13);skyUniforms.bottomColor.value.set(0x15293a);skyUniforms.exponent.value=.92;scene.fog=new THREE.Fog(0x0b1724,980,2300);scene.environmentIntensity=.16;renderer.toneMappingExposure=.82;hemi.intensity=.13;sun.intensity=.025;coolFill.intensity=.055;setHeroMaterialState(true);plazaLights.forEach(x=>x.intensity=performanceMode?0:42);heroLights.forEach(x=>x.intensity=performanceMode?0:38);heroAtriumLights.forEach(x=>x.intensity=performanceMode?0:44);heroFrontageLights.forEach((x,index)=>x.intensity=performanceMode?0:index%2?24:34);heroRouteLights.forEach(x=>x.intensity=performanceMode?0:23);heroPromenadeLights.forEach(x=>x.intensity=performanceMode?0:28);heroBridgeLights.forEach(x=>x.intensity=performanceMode?0:24);expandedNodeLights.forEach((x,index)=>x.intensity=performanceMode?0:index<2?34:38);expandedRouteLights.forEach(x=>x.intensity=performanceMode?0:20);streamLights.forEach(x=>x.light.intensity=performanceMode?0:x.intensity*.62);}else if(mode==='dusk'){skyUniforms.topColor.value.set(0x3e4966);skyUniforms.bottomColor.value.set(0xe2a070);skyUniforms.exponent.value=.70;scene.fog=new THREE.Fog(0x7c7180,1250,2800);scene.environmentIntensity=.34;renderer.toneMappingExposure=.96;hemi.intensity=.25;sun.intensity=1.65;coolFill.intensity=.10;setHeroMaterialState(true);plazaLights.forEach(x=>x.intensity=performanceMode?0:28);heroLights.forEach(x=>x.intensity=performanceMode?0:28);heroAtriumLights.forEach(x=>x.intensity=performanceMode?0:28);heroFrontageLights.forEach((x,index)=>x.intensity=performanceMode?0:index%2?13:20);heroRouteLights.forEach(x=>x.intensity=performanceMode?0:14);heroPromenadeLights.forEach(x=>x.intensity=performanceMode?0:18);heroBridgeLights.forEach(x=>x.intensity=performanceMode?0:16);expandedNodeLights.forEach((x,index)=>x.intensity=performanceMode?0:index<2?20:23);expandedRouteLights.forEach(x=>x.intensity=performanceMode?0:12);streamLights.forEach(x=>x.light.intensity=performanceMode?0:x.intensity*.38);}else{skyUniforms.topColor.value.set(0x23689d);skyUniforms.bottomColor.value.set(0xc2d7e1);skyUniforms.exponent.value=.56;scene.fog=new THREE.Fog(0xc5d7df,2600,5000);scene.environmentIntensity=.48;renderer.toneMappingExposure=1.05;hemi.intensity=.46;sun.intensity=4.85;coolFill.intensity=.18;setHeroMaterialState(false);plazaLights.forEach(x=>x.intensity=0);heroLights.forEach(x=>x.intensity=0);heroAtriumLights.forEach(x=>x.intensity=0);heroFrontageLights.forEach(x=>x.intensity=0);heroRouteLights.forEach(x=>x.intensity=0);heroPromenadeLights.forEach(x=>x.intensity=0);heroBridgeLights.forEach(x=>x.intensity=0);expandedNodeLights.forEach(x=>x.intensity=0);expandedRouteLights.forEach(x=>x.intensity=0);streamLights.forEach(x=>x.light.intensity=0);}};
 const applyLightingHierarchy=(mode:'day'|'dusk'|'night')=>{if(mode==='day'||performanceMode)return;const scale=mode==='night'?1:.62;plazaLights.forEach(x=>x.intensity=30*scale);heroLights.forEach(x=>x.intensity=16*scale);heroAtriumLights.forEach(x=>x.intensity=30*scale);heroFrontageLights.forEach((x,index)=>x.intensity=(index%2?18:26)*scale);heroRouteLights.forEach(x=>x.intensity=7.5*scale);heroPromenadeLights.forEach(x=>x.intensity=13.5*scale);heroBridgeLights.forEach(x=>x.intensity=21*scale);expandedNodeLights.forEach((x,index)=>x.intensity=(index<2?28:32)*scale);expandedRouteLights.forEach(x=>x.intensity=8*scale);streamLights.forEach(x=>x.light.intensity=x.intensity*.24*scale);};
 const applyTime=(mode:'day'|'dusk'|'night')=>{setTime(mode);applyLightingHierarchy(mode);};
 app.querySelector<HTMLButtonElement>('#core-aerial')!.onclick=()=>{camera.position.set(740,570,790);controls.target.set(0,55,0)};
 app.querySelector<HTMLButtonElement>('#core-street')!.onclick=()=>{camera.position.set(0,7,360);controls.target.set(0,24,0)};
 app.querySelector<HTMLButtonElement>('#core-day')!.onclick=()=>applyTime('day');app.querySelector<HTMLButtonElement>('#core-night')!.onclick=()=>applyTime('night');
 app.querySelector<HTMLInputElement>('#core-infra')!.onchange=e=>infrastructure.visible=(e.target as HTMLInputElement).checked;app.querySelector<HTMLInputElement>('#core-buildings')!.onchange=e=>buildings.visible=(e.target as HTMLInputElement).checked;
 const streamToggle=app.querySelector<HTMLInputElement>('#core-stream');if(streamToggle)streamToggle.onchange=e=>{urbanStream.visible=(e.target as HTMLInputElement).checked;heroZones.visible=(e.target as HTMLInputElement).checked;};
 camera.position.set(...selected.position);controls.target.set(...selected.target);
 const pose=(query.get('pose')??'').split(',').map(Number);if(pose.length===6&&pose.every(Number.isFinite)){camera.position.set(pose[0],pose[1],pose[2]);controls.target.set(pose[3],pose[4],pose[5]);}
 applyTime(query.get('time')==='night'?'night':query.get('time')==='dusk'?'dusk':'day');
}
