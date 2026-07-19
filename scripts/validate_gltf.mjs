import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
const require=createRequire(import.meta.url);const validatorRoot=process.env.ARCHIVE_GLTF_VALIDATOR_DIR;
let validateBytes;
try{({validateBytes}=validatorRoot?require(path.join(validatorRoot,'node_modules','gltf-validator')):require('gltf-validator'));}
catch(error){console.error(JSON.stringify({status:'BLOCKED',reason:'OFFICIAL_VALIDATOR_MISSING',detail:error.code??error.message}));process.exit(2);}
const args=process.argv.slice(2);const strictIndex=args.indexOf('--strict');const strict=strictIndex>=0;if(strict)args.splice(strictIndex,1);const reportIndex=args.indexOf('--report');const reportPath=reportIndex>=0?args.splice(reportIndex,2)[1]:null;
async function expand(items){const out=[];for(const item of items){const s=await fs.stat(item);if(s.isDirectory()){for(const e of await fs.readdir(item,{recursive:true}))if(/\.gl(?:b|tf)$/i.test(e))out.push(path.join(item,e));}else out.push(item);}return out.sort();}
const files=await expand(args);if(!files.length){console.error('usage: node validate_gltf.mjs [--strict] [--report report.json] <file.glb|folder>...');process.exit(2);}
const results=[];
for(const file of files){try{const result=await validateBytes(new Uint8Array(await fs.readFile(file)),{externalResourceFunction:async uri=>{try{return new Uint8Array(await fs.readFile(path.resolve(path.dirname(file),uri)));}catch{return null;}}});const messages=result.issues.messages??[];results.push({file,errors:result.issues.numErrors,warnings:result.issues.numWarnings,infos:messages.filter(x=>x.severity>=2).length,messages});}catch(error){results.push({file,errors:1,warnings:0,infos:0,messages:[{code:'VALIDATOR_EXCEPTION',message:error.message,severity:0}]});}}
const summary={files:results.length,errors:results.reduce((n,x)=>n+x.errors,0),warnings:results.reduce((n,x)=>n+x.warnings,0),infos:results.reduce((n,x)=>n+x.infos,0)};const output={status:summary.errors?'FAIL':strict&&summary.warnings?'STRICT_WARNING_FAIL':'PASS',validator:'gltf-validator@2.0.0-dev.3.10',strict,summary,results};if(reportPath)await fs.writeFile(reportPath,JSON.stringify(output,null,2));console.log(JSON.stringify(output,null,2));if(summary.errors||(strict&&summary.warnings))process.exitCode=1;
