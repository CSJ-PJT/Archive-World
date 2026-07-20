import {spawn} from 'node:child_process';
import {mkdir,writeFile} from 'node:fs/promises';
import {basename,join,resolve} from 'node:path';
import {tmpdir} from 'node:os';

const chrome=process.env.CHROME_PATH??'C:/Program Files/Google/Chrome/Application/chrome.exe';
const baseUrl=process.argv[2]??'http://127.0.0.1:4176/?mode=metropolitan&metrobase=/generated/v14/metropolitan-precision-all-districts';
const output=resolve(process.argv[3]??'C:/ArchiveData/World/Generated/v14/metropolitan-precision-all-districts/renders');
const port=Number(process.env.ARCHIVE_CDP_PORT??9360);
const defaults=['full','archiveos-core','ledger-financial','market-commercial','nexus-technology','residential-north','civic-cultural','logistics-edge'];
const views=(process.env.ARCHIVE_METRO_VIEWS??defaults.join(',')).split(',').filter(Boolean);
const times=(process.env.ARCHIVE_CAPTURE_TIMES??'day,night').split(',').filter(Boolean);
const sleep=ms=>new Promise(resolveSleep=>setTimeout(resolveSleep,ms));
async function json(url,attempts=80){let last;for(let attempt=0;attempt<attempts;attempt++){try{const response=await fetch(url);if(response.ok)return response.json();last=new Error(`${response.status}`);}catch(error){last=error;}await sleep(250);}throw last??new Error(`CDP unavailable: ${url}`);}
function cdp(socketUrl){const socket=new WebSocket(socketUrl);let id=0;const pending=new Map();const ready=new Promise((resolveReady,reject)=>{socket.onopen=resolveReady;socket.onerror=reject;});socket.onmessage=event=>{const message=JSON.parse(event.data);const callback=pending.get(message.id);if(callback){pending.delete(message.id);callback(message);}};return async(method,params={})=>{await ready;const requestId=++id;const result=new Promise((resolveResult,reject)=>{const timer=setTimeout(()=>reject(new Error(`CDP timeout: ${method}`)),60000);pending.set(requestId,message=>{clearTimeout(timer);message.error?reject(new Error(JSON.stringify(message.error))):resolveResult(message.result);});});socket.send(JSON.stringify({id:requestId,method,params}));return result;};}

await mkdir(output,{recursive:true});
const profile=join(tmpdir(),`archive-metro-cdp-${process.pid}`);
const child=spawn(chrome,['--headless=new','--disable-gpu-sandbox','--hide-scrollbars','--window-size=1920,1080',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore',windowsHide:true});
const report=[];
try{
 const targets=await json(`http://127.0.0.1:${port}/json/list`),target=targets.find(item=>item.type==='page');if(!target)throw new Error('CDP page target missing');
 const call=cdp(target.webSocketDebuggerUrl);await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1920,height:1080,deviceScaleFactor:1,mobile:false});
 for(const district of views){for(const time of times){const url=`${baseUrl}&district=${district}&time=${time}&rev=metro-v14`;const started=Date.now();await call('Page.navigate',{url});let title='';for(let attempt=0;attempt<180;attempt++){await sleep(250);const states=await fetch(`http://127.0.0.1:${port}/json/list`).then(response=>response.json());title=states.find(item=>item.id===target.id)?.title??'';if(title.startsWith('METRO3D|'))break;}if(!title.startsWith('METRO3D|'))throw new Error(`Viewer not ready: ${district}/${time} (${title})`);await sleep(1500);const state=await fetch(`http://127.0.0.1:${port}/json/list`).then(response=>response.json());title=state.find(item=>item.id===target.id)?.title??title;const image=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});const filename=`${district}-${time}.png`,bytes=Buffer.from(image.data,'base64');if(bytes.length<10000||bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error(`Invalid capture: ${filename}`);await writeFile(join(output,filename),bytes);const [_,fps,drawCalls,triangles]=title.split('|');report.push({district,time,filename:basename(filename),bytes:bytes.length,fps:Number(fps),drawCalls:Number(drawCalls),triangles:Number(triangles),durationMs:Date.now()-started,actualWebGL:true});}}
 await writeFile(join(output,'capture-report.json'),JSON.stringify({status:'PASS',count:report.length,resolution:'1920x1080',report},null,2));process.stdout.write(`${JSON.stringify({status:'PASS',count:report.length,output})}\n`);
}finally{child.kill();}
