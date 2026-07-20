import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const source = await readFile(new URL('./urban_stream/capture_precision_webgl.mjs', import.meta.url), 'utf8');
for (const token of ['Page.captureScreenshot', 'Emulation.setDeviceMetricsOverride', 'CORE3D|', 'actualWebGL: true', 'child.kill()', '1920, height: 1080', 'ARCHIVE_CAPTURE_VIEWS', 'ARCHIVE_PICK_POINTS', '__archiveReviewPick', '/json/list', 'previousTitle', 'ARCHIVE_PERFORMANCE_SECONDS', 'ARCHIVE_PERFORMANCE_ONLY', 'performanceSamples', 'performanceOnly: true', 'cdp-target-title', '--disable-frame-rate-limit', '--disable-gpu-vsync']) assert.ok(source.includes(token), token);
assert.ok(!source.includes('--virtual-time-budget='));
console.log('precision WebGL CDP capture contract: PASS');
