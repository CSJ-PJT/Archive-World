import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const { validateBytes }=createRequire(import.meta.url)('gltf-validator');
const args=process.argv.slice(2);const reportIndex=args.indexOf('--report');const report=reportIndex>=0?args.splice(reportIndex,2)[1]:null;
async function expand(items){const out=[];for(const item of items){const s=await fs.stat(item);if(s.isDirectory()){for(const e of await fs.readdir(item,{recursive:true}))if(e.endsWith('.glb'))out.push(path.join(item,e));}else out.push(item);}return out;}
const files = await expand(args);
if (!files.length) throw new Error('usage: node validate_gltf.mjs [--report report.json] <file.glb|folder>...');
const results=[];
for (const file of files) { const report=await validateBytes(new Uint8Array(await fs.readFile(file)), {externalResourceFunction: async()=>null}); results.push({file,errors:report.issues.numErrors,warnings:report.issues.numWarnings,messages:report.issues.messages}); }
const output={validator:'gltf-validator@2.0.0-dev.3.10',results};if(report)await fs.writeFile(report,JSON.stringify(output,null,2));console.log(JSON.stringify(output,null,2));
if (results.some(x=>x.errors)) process.exitCode=1;
