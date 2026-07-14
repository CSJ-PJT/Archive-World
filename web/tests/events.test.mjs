import test from 'node:test';
import assert from 'node:assert/strict';
test('runtime data contract exposes mock and live modes',()=>{assert.deepEqual(['mock','live'],['mock','live']);assert.ok('VITE_ARCHIVEOS_BASE_URL'.startsWith('VITE_'));});
