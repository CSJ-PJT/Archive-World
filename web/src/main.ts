import './style.css';
import type { District } from './types';

const runtimeBase=(import.meta.env.VITE_ARCHIVE_WORLD_ASSET_BASE_URL ?? '').replace(/\/$/,'');
const app=document.querySelector<HTMLDivElement>('#app')!;
const districts=['city','archiveos','market','nexus','logistics','ledger','residential','infrastructure'] as const;
const label:Record<string,string>={city:'City',archiveos:'ArchiveOS',market:'Market',nexus:'Nexus',logistics:'Logistics',ledger:'Ledger',residential:'Residential',infrastructure:'Infrastructure'};
const overview:Record<string,string>={city:'v3/city-overview.png',archiveos:'v3/archiveos-overview.png',market:'v3/market-overview.png',nexus:'v3/nexus-overview.png',logistics:'v3/logistics-overview.png',ledger:'v3/ledger-overview.png',residential:'v3/residential-overview.png',infrastructure:'v3/infrastructure-overview.png'};
app.innerHTML=`<main class="shell"><aside class="sidebar"><div class="brand"><span>ARCHIVE</span><strong>WORLD</strong></div><p class="eyebrow">DIGITAL TWIN · CITY V3 GEOGRAPHY EDITION</p><div class="button-stack" id="presets"></div><hr/><button id="open-viewer">Load 3D district viewer</button><p class="hint">초기 진입은 City overview PNG만 표시합니다. 3D 뷰어는 요청 시에만 Three.js와 district runtime GLB를 지연 로드합니다.</p><hr/><label>District filter</label><div class="filters" id="filters"></div><hr/><div class="metric"><span>Runtime policy</span><b>OVERVIEW → LAZY</b></div><div class="metric"><span>Runtime mode</span><b id="runtime">${(import.meta.env.VITE_RUNTIME_DATA_MODE ?? 'mock').toUpperCase()}</b></div></aside><section class="viewport"><div id="canvas"></div><img class="overview" id="overview" src="v3/city-overview.png" alt="Archive City v3 overview"/><div class="hud"><span id="load">OVERVIEW READY · 3D NOT LOADED</span></div><aside class="selection" id="selection"><p class="eyebrow">ASSET INSPECTOR</p><h2>선택 없음</h2><dl><dt>Mode</dt><dd>Overview</dd></dl></aside></section></main>`;

const image=document.querySelector<HTMLImageElement>('#overview')!, status=document.querySelector<HTMLElement>('#load')!, canvas=document.querySelector<HTMLElement>('#canvas')!, selection=document.querySelector<HTMLElement>('#selection')!;
let viewer: import('./viewer-runtime').WorldViewer | undefined;
let viewerPromise: Promise<import('./viewer-runtime').WorldViewer> | undefined;
async function ensureViewer(){
  if(viewer)return viewer;
  viewerPromise ??= import('./viewer-runtime').then(({createWorldViewer})=>createWorldViewer({host:canvas,status,select:(text)=>{selection.innerHTML=`<p class="eyebrow">ASSET INSPECTOR</p><h2>${text}</h2><dl><dt>Runtime</dt><dd>V3 linked district</dd></dl>`;},runtimeBase}));
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
