import './style.css';
import type { District } from './types';

const generatedMode=import.meta.env.VITE_ARCHIVE_WORLD_RUNTIME_MODE==='generated';
const planningMode=new URLSearchParams(window.location.search).get('mode')==='planning';
const metropolitanMode=new URLSearchParams(window.location.search).get('mode')==='metropolitan';
const coreDistrictMode=new URLSearchParams(window.location.search).get('mode')==='core3d';
const coreStreamMode=new URLSearchParams(window.location.search).get('mode')==='corestream';
const coreStreamFinalMode=new URLSearchParams(window.location.search).get('mode')==='corestreamfinal';
const generatedBase=(import.meta.env.VITE_ARCHIVE_WORLD_GENERATED_BASE_URL ?? '').replace(/\/$/,'');
const runtimeBase=generatedMode?generatedBase:(import.meta.env.VITE_ARCHIVE_WORLD_ASSET_BASE_URL ?? '').replace(/\/$/,'');
const modeLabel=generatedMode?'GENERATED MODE':'SOURCE MODE';
const app=document.querySelector<HTMLDivElement>('#app')!;
if(coreStreamFinalMode){
  const streamBase=(import.meta.env.VITE_ARCHIVE_WORLD_CORE_STREAM_FINAL_BASE_URL ?? '').replace(/\/$/,'');
  if(!streamBase){app.innerHTML='<main class="planning-error">CORE_STREAM_FINAL_REVIEW requires VITE_ARCHIVE_WORLD_CORE_STREAM_FINAL_BASE_URL.</main>';}else{void import('./core-district-review').then(({createCoreDistrictReview})=>createCoreDistrictReview(app,streamBase,'core-district-stream-final.json'));}
}else if(coreStreamMode){
  const streamBase=(import.meta.env.VITE_ARCHIVE_WORLD_CORE_STREAM_BASE_URL ?? '').replace(/\/$/,'');
  if(!streamBase){app.innerHTML='<main class="planning-error">CORE_DISTRICT_STREAM_REVIEW requires VITE_ARCHIVE_WORLD_CORE_STREAM_BASE_URL.</main>';}else{void import('./core-district-review').then(({createCoreDistrictReview})=>createCoreDistrictReview(app,streamBase,'core-district-stream-3d.json'));}
}else if(coreDistrictMode){
  const coreBase=(import.meta.env.VITE_ARCHIVE_WORLD_CORE_DISTRICT_BASE_URL ?? '').replace(/\/$/,'');
  if(!coreBase){app.innerHTML='<main class="planning-error">CORE_DISTRICT_3D_REVIEW requires <code>VITE_ARCHIVE_WORLD_CORE_DISTRICT_BASE_URL</code>.</main>';}else{void import('./core-district-review').then(({createCoreDistrictReview})=>createCoreDistrictReview(app,coreBase));}
}else if(metropolitanMode){
  const metropolitanBase=(import.meta.env.VITE_ARCHIVE_WORLD_METROPOLITAN_BASE_URL ?? '').replace(/\/$/,'');
  if(!metropolitanBase){app.innerHTML='<main class="planning-error">METROPOLITAN_REVIEW requires <code>VITE_ARCHIVE_WORLD_METROPOLITAN_BASE_URL</code>. Generated output only.</main>';}else{void import('./metropolitan-review').then(({createMetropolitanReview})=>createMetropolitanReview(app,metropolitanBase));}
}else if(planningMode){
  const planningBase=(import.meta.env.VITE_ARCHIVE_WORLD_PLANNING_BASE_URL ?? '').replace(/\/$/,'');
  if(!planningBase){app.innerHTML='<main class="planning-error">PLAN_ONLY 모드는 <code>VITE_ARCHIVE_WORLD_PLANNING_BASE_URL</code>가 필요합니다. Generated planning output만 지정하십시오.</main>';}else{void import('./planning-mode').then(({createPlanningMode})=>createPlanningMode(app,planningBase));}
}else{
const districts=['city','archiveos','market','nexus','logistics','ledger','residential','infrastructure'] as const;
const label:Record<string,string>={city:'City',archiveos:'ArchiveOS',market:'Market',nexus:'Nexus',logistics:'Logistics',ledger:'Ledger',residential:'Residential',infrastructure:'Infrastructure'};
const preview=(name:string)=>generatedMode?`${generatedBase}/v3/previews/${name}-overview.png`:`v3/${name}-overview.png`;
const overview:Record<string,string>={city:preview('city'),archiveos:preview('archiveos'),market:preview('market'),nexus:preview('nexus'),logistics:preview('logistics'),ledger:preview('ledger'),residential:preview('residential'),infrastructure:preview('infrastructure')};
app.innerHTML=`<main class="shell"><aside class="sidebar"><div class="brand"><span>ARCHIVE</span><strong>WORLD</strong></div><p class="eyebrow">DIGITAL TWIN · CITY V3 GEOGRAPHY EDITION</p><div class="button-stack" id="presets"></div><hr/><button id="open-viewer">Load 3D district viewer</button><p class="hint">초기 진입은 City overview PNG만 표시합니다. 3D 뷰어는 요청 시에만 Three.js와 district runtime GLB를 지연 로드합니다.</p><hr/><label>District filter</label><div class="filters" id="filters"></div><hr/><div class="metric"><span>Runtime policy</span><b>OVERVIEW → LAZY</b></div><div class="metric"><span>Runtime mode</span><b id="runtime">${modeLabel}</b></div></aside><section class="viewport"><div id="canvas"></div><img class="overview" id="overview" src="${overview.city}" alt="Archive City v3 overview"/><div class="hud"><span id="load">OVERVIEW READY · 3D NOT LOADED</span></div><aside class="selection" id="selection"><p class="eyebrow">ASSET INSPECTOR</p><h2>선택 없음</h2><dl><dt>Mode</dt><dd>${modeLabel}</dd></dl></aside></section></main>`;

const image=document.querySelector<HTMLImageElement>('#overview')!, status=document.querySelector<HTMLElement>('#load')!, canvas=document.querySelector<HTMLElement>('#canvas')!, selection=document.querySelector<HTMLElement>('#selection')!;
let viewer: import('./viewer-runtime').WorldViewer | undefined;
let viewerPromise: Promise<import('./viewer-runtime').WorldViewer> | undefined;
async function ensureViewer(){
  if(viewer)return viewer;
  viewerPromise ??= import('./viewer-runtime').then(({createWorldViewer})=>createWorldViewer({host:canvas,status,select:(text)=>{selection.innerHTML=`<p class="eyebrow">ASSET INSPECTOR</p><h2>${text}</h2><dl><dt>Runtime</dt><dd>V3 linked district · ${modeLabel}</dd></dl>`;},runtimeBase,generatedMode}));
  viewer=await viewerPromise; image.style.opacity='.16'; return viewer;
}
async function activate(id:string){
  image.src=overview[id]??overview.city;image.alt=`${label[id]??id} overview`;
  const active=await ensureViewer();active.focus(id);
}
const presetHost=document.querySelector<HTMLElement>('#presets')!;
for(const id of districts){const button=document.createElement('button');button.textContent=label[id];button.onclick=()=>{void activate(id);};presetHost.append(button);}
document.querySelector<HTMLButtonElement>('#open-viewer')!.onclick=()=>{void activate('city');};
const filterHost=document.querySelector<HTMLElement>('#filters')!;
for(const id of districts.slice(1) as readonly District[]){const item=document.createElement('label');item.className='filter';item.innerHTML=`<input type="checkbox" checked/> ${label[id]}`;const checkbox=item.querySelector<HTMLInputElement>('input')!;checkbox.onchange=()=>viewer?.setDistrict(id,checkbox.checked);filterHost.append(item);}
}
