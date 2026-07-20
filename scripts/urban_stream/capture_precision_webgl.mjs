import {spawn} from 'node:child_process';
import {mkdir, writeFile} from 'node:fs/promises';
import {basename, join, resolve} from 'node:path';
import {tmpdir} from 'node:os';

const chrome = process.env.CHROME_PATH ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const baseUrl = process.argv[2] ?? 'http://127.0.0.1:4176/?mode=coreprecision&clean=1&cinematic=1';
const output = resolve(process.argv[3] ?? 'C:/ArchiveData/World/Generated/v13/core-stream-s-grade/renders/metropolitan-precision-v41');
const port = Number(process.env.ARCHIVE_CDP_PORT ?? 9336);
const allViews = [
  ['district-aerial', 0], ['district-skyline', 8],
  ['ledger-terrace', 35], ['ledger-frontage', 36],
  ['transit-junction', 37], ['transit-entry', 38],
  ['archive-axis', 42], ['archive-aerial', 48],
  ['archive-street', 49], ['archive-frontage', 50],
  ['archive-water-plaza', 51], ['archive-gateway', 52],
];
const selectedNames = new Set((process.env.ARCHIVE_CAPTURE_VIEWS ?? '').split(',').filter(Boolean));
const views = selectedNames.size ? allViews.filter(([name]) => selectedNames.has(name)) : allViews;
const times = (process.env.ARCHIVE_CAPTURE_TIMES ?? 'day,dusk,night').split(',');
const pickPoints = (process.env.ARCHIVE_PICK_POINTS ?? '').split(';').filter(Boolean).map(value => value.split(',').map(Number)).filter(value => value.length === 2 && value.every(Number.isFinite));
const performanceSeconds = Number(process.env.ARCHIVE_PERFORMANCE_SECONDS ?? 0);
const performanceOnly = process.env.ARCHIVE_PERFORMANCE_ONLY === '1';

const sleep = ms => new Promise(resolvePromise => setTimeout(resolvePromise, ms));
async function json(url, attempts = 80) {
  let last;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try { const response = await fetch(url); if (response.ok) return response.json(); last = new Error(`${response.status}`); }
    catch (error) { last = error; }
    await sleep(250);
  }
  throw last ?? new Error(`CDP unavailable: ${url}`);
}

function cdp(socketUrl) {
  const socket = new WebSocket(socketUrl);
  let id = 0;
  const pending = new Map();
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (!message.id) return;
    const callback = pending.get(message.id);
    if (callback) { pending.delete(message.id); callback(message); }
  };
  const ready = new Promise((resolveReady, reject) => {
    socket.onopen = resolveReady;
    socket.onerror = reject;
  });
  return async (method, params = {}) => {
    await ready;
    const requestId = ++id;
    const response = new Promise((resolveResponse, reject) => {
      const timer = setTimeout(() => { pending.delete(requestId); reject(new Error(`CDP timeout: ${method}`)); }, 120000);
      pending.set(requestId, message => { clearTimeout(timer); message.error ? reject(new Error(JSON.stringify(message.error))) : resolveResponse(message.result); });
    });
    socket.send(JSON.stringify({id: requestId, method, params}));
    return response;
  };
}

await mkdir(output, {recursive: true});
const profile = join(tmpdir(), `archive-cdp-${process.pid}`);
const chromeFlags = [
  '--headless=new', '--disable-gpu-sandbox', '--hide-scrollbars',
  '--window-size=1920,1080', `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, 'about:blank',
];
if (performanceOnly) chromeFlags.splice(3, 0, '--disable-frame-rate-limit', '--disable-gpu-vsync');
const child = spawn(chrome, chromeFlags, {stdio: 'ignore', windowsHide: true});

const report = [];
try {
  const targets = await json(`http://127.0.0.1:${port}/json/list`);
  const target = targets.find(item => item.type === 'page');
  if (!target) throw new Error('CDP page target missing');
  const call = cdp(target.webSocketDebuggerUrl);
  await call('Page.enable');
  await call('Runtime.enable');
  await call('Emulation.setDeviceMetricsOverride', {width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false});
  for (const [name, camera] of views) {
    for (const time of times) {
      const url = `${baseUrl}&camera=${camera}&time=${time}&rev=metropolitan-precision-v41`;
      const started = Date.now();
      await call('Page.navigate', {url});
      let title = '', previousTitle = '';
      for (let attempt = 0; attempt < 360; attempt += 1) {
        await sleep(500);
        const states = await fetch(`http://127.0.0.1:${port}/json/list`).then(response => response.json());
        title = states.find(item => item.id === target.id)?.title ?? '';
        if (title !== previousTitle) { process.stderr.write(`[capture] ${name}/${time}: ${title || 'UNTITLED'}\n`); previousTitle = title; }
        if (title.startsWith('CORE3D|')) break;
      }
      if (!title.startsWith('CORE3D|')) throw new Error(`Viewer not ready: ${name}/${time} (${title})`);
      const picks = [];
      for (const [x, y] of pickPoints) {
        const value = await call('Runtime.evaluate', {expression: `window.__archiveReviewPick?.(${x},${y})`, returnByValue: true});
        picks.push({x, y, hits: value.result?.value ?? []});
      }
      const performanceSamples = [];
      if (performanceSeconds > 0) {
        await sleep(8000);
        for (let second = 0; second < performanceSeconds; second += 1) {
          if (performanceOnly) {
            const states = await fetch(`http://127.0.0.1:${port}/json/list`).then(response => response.json());
            const currentTitle = states.find(item => item.id === target.id)?.title ?? '';
            const parts = currentTitle.split('|').map((value, index) => index ? Number(value) : value);
            if (parts[0] === 'CORE3D' && parts.slice(1).every(Number.isFinite)) performanceSamples.push({second, fps: parts[1], lowFps: parts[2], drawCalls: parts[3], triangles: parts[4], source: 'cdp-target-title'});
          } else {
            const value = await call('Runtime.evaluate', {expression: `document.querySelector('#core-perf')?.dataset.metrics ?? ''`, returnByValue: true});
            const raw = value.result?.value ?? '';
            if (raw) performanceSamples.push({second, ...JSON.parse(raw)});
          }
          await sleep(1000);
        }
      }
      if (performanceOnly) {
        report.push({name, camera, time, filename: null, bytes: 0, title, durationMs: Date.now() - started, actualWebGL: true, picks, performanceSamples, performanceOnly: true});
        continue;
      }
      const image = await call('Page.captureScreenshot', {format: 'png', captureBeyondViewport: false});
      const filename = `${name}-${time}.png`;
      const bytes = Buffer.from(image.data, 'base64');
      if (bytes.length < 10000 || bytes.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') throw new Error(`Invalid capture: ${filename}`);
      await writeFile(join(output, filename), bytes);
      report.push({name, camera, time, filename: basename(filename), bytes: bytes.length, title, durationMs: Date.now() - started, actualWebGL: true, picks, performanceSamples});
    }
  }
  await writeFile(join(output, 'capture-report.json'), JSON.stringify({status: 'PASS', count: report.length, resolution: '1920x1080', report}, null, 2));
  process.stdout.write(`${JSON.stringify({status: 'PASS', count: report.length, output})}\n`);
} finally {
  child.kill();
}
