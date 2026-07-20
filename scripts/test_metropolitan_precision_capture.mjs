import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const source=fs.readFileSync(new URL('./metropolitan/capture_metropolitan_precision.mjs',import.meta.url),'utf8');
test('metropolitan precision capture records actual WebGL evidence',()=>{assert.match(source,/METRO3D\|/);assert.match(source,/Page\.captureScreenshot/);assert.match(source,/actualWebGL:true/);assert.match(source,/archiveos-core/);assert.match(source,/ledger-financial/);assert.match(source,/logistics-edge/);assert.match(source,/1920,height:1080/);});
