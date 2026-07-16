#!/usr/bin/env node
/** Serve the generated Viewer and world output on localhost only.
 *
 * This is intentionally a local development helper: it never exposes the
 * generated files on a public interface and it rejects paths outside either
 * the generated Viewer bundle or the generated world root.
 */
import { createReadStream, existsSync, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { resolve, sep } from 'node:path';

const args=process.argv.slice(2);
const option=(name)=>{const index=args.indexOf(name);return index<0?undefined:args[index+1];};
const outputRoot=resolve(option('--output-root') ?? process.env.ARCHIVE_WORLD_OUTPUT_ROOT ?? 'C:/ArchiveData/World/Generated');
const viewerRoot=resolve(outputRoot,'v3','viewer');
const host=option('--host') ?? '127.0.0.1';
const port=Number(option('--port') ?? 4173);
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.glb':'model/gltf-binary','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.map':'application/json; charset=utf-8'};
const inside=(root,target)=>target===root || target.startsWith(`${root}${sep}`);
const type=(file)=>mime[file.slice(file.lastIndexOf('.')).toLowerCase()] ?? 'application/octet-stream';

if(!existsSync(viewerRoot)) throw new Error(`Generated Viewer not found: ${viewerRoot}`);
const server=createServer((request,response)=>{
  const url=new URL(request.url ?? '/',`http://${host}:${port}`);
  const relative=decodeURIComponent(url.pathname).replace(/^\/+/, '');
  const root=relative.startsWith('generated/')?outputRoot:viewerRoot;
  const requestPath=relative.startsWith('generated/')?relative.slice('generated/'.length):relative;
  let target=resolve(root,requestPath || 'index.html');
  if(!inside(root,target)){response.writeHead(403).end('forbidden');return;}
  if(!existsSync(target) || statSync(target).isDirectory()) target=resolve(viewerRoot,'index.html');
  if(!inside(viewerRoot,target) && !inside(outputRoot,target)){response.writeHead(403).end('forbidden');return;}
  response.writeHead(200,{'Content-Type':type(target),'Cache-Control':'no-store'});
  createReadStream(target).pipe(response);
});
server.listen(port,host,()=>console.log(JSON.stringify({status:'PASS',host,port,viewerRoot,generatedRoot:outputRoot})));
