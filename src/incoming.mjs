#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { ensureDir, writeJson } from './lib/files.mjs';
import { readGlbDocument } from './lib/gltf.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const incomingModels = process.env.MESHY_INCOMING_MODELS_ROOT;
const rejectedRoot = process.env.MESHY_REJECTED_ROOT;
if (!incomingModels || !rejectedRoot) {
  throw new Error('MESHY_INCOMING_MODELS_ROOT and MESHY_REJECTED_ROOT must be configured for Incoming processing.');
}

async function sha256(file) {
  return new Promise((resolve, reject) => {
    const hash = createHash('sha256'); const stream = createReadStream(file);
    stream.on('data', (chunk) => hash.update(chunk)); stream.on('error', reject);
    stream.on('end', () => resolve(hash.digest('hex')));
  });
}

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map((entry) => entry.isDirectory() ? walk(path.join(directory, entry.name)) : [path.join(directory, entry.name)]));
  return nested.flat();
}

async function inspectGlb(file, bytes) {
  const { document } = await readGlbDocument(file);
  const meshes = document.meshes ?? []; const scenes = document.scenes ?? [];
  const warnings = [];
  if (!scenes.length) warnings.push('NO_SCENE');
  if (!meshes.length) warnings.push('NO_MESH');
  const invalid = warnings.length > 0;
  return {
    validationStatus: invalid ? 'REJECTED' : warnings.length ? 'NEEDS_REVIEW' : 'QUEUED_FOR_REVIEW',
    meshCount: meshes.length, nodeCount: (document.nodes ?? []).length,
    materialCount: (document.materials ?? []).length, textureCount: (document.textures ?? []).length,
    animationCount: (document.animations ?? []).length, skinCount: (document.skins ?? []).length,
    bytes, warnings
  };
}

async function rejectedByFilename() {
  const records = new Map();
  for (const entry of await readdir(rejectedRoot, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith('.rejection.json')) continue;
    try {
      const record = JSON.parse(await readFile(path.join(rejectedRoot, entry.name), 'utf8'));
      records.set(path.basename(record.rejectedFile ?? ''), record);
    } catch { /* A malformed rejection record cannot make an incoming model valid. */ }
  }
  return records;
}

async function inventory() {
  const files = await walk(incomingModels);
  const rejected = await rejectedByFilename();
  const assets = [];
  for (const file of files.sort()) {
    const info = await stat(file); const ext = path.extname(file).toLowerCase();
    const asset = {
      incomingRelativePath: path.relative(incomingModels, file).replaceAll('\\', '/'),
      filename: path.basename(file), extension: ext, bytes: info.size, modifiedAt: info.mtime.toISOString(),
      checksum: await sha256(file), sourceQueue: 'Incoming/Models', canonicalAssetId: null,
      classification: 'NEEDS_REVIEW', manifestEligible: false, pipelineStatus: 'PENDING'
    };
    if (ext !== '.glb') {
      asset.validationStatus = 'UNSUPPORTED'; asset.pipelineStatus = 'REJECTED'; asset.warnings = ['UNSUPPORTED_INCOMING_MODEL_FORMAT'];
    } else {
      try { Object.assign(asset, await inspectGlb(file, info.size)); }
      catch (error) { asset.validationStatus = 'REJECTED'; asset.pipelineStatus = 'REJECTED'; asset.warnings = [`GLB_PARSE_ERROR: ${error.message}`]; }
    }
    const rejection = rejected.get(asset.filename);
    if (rejection) {
      asset.validationStatus = 'REJECTED'; asset.pipelineStatus = 'REJECTED';
      asset.rejectionRecord = path.relative(root, path.join(rejectedRoot, `${path.basename(asset.filename, '.glb')}.rejection.json`)).replaceAll('\\', '/');
      asset.warnings = [...(asset.warnings ?? []), rejection.reason ?? 'REJECTED_BY_REVIEW'];
    }
    assets.push(asset);
  }
  const summary = {
    schema: 'archive-world.incoming-inventory/v1', generatedAt: new Date().toISOString(), incomingModels,
    policy: { existingBaseline: 'reports/source-integrity.json', manifestPolicy: 'PASS_ONLY_AFTER_SINGLE_ASSET_PIPELINE', rejectedPolicy: 'record-only; never delete or move original incoming files' },
    totals: { files: assets.length, glb: assets.filter((item) => item.extension === '.glb').length, queued: assets.filter((item) => item.validationStatus === 'QUEUED_FOR_REVIEW').length, rejected: assets.filter((item) => item.validationStatus === 'REJECTED').length, unsupported: assets.filter((item) => item.validationStatus === 'UNSUPPORTED').length },
    assets
  };
  await ensureDir(path.join(root, 'reports'));
  await writeJson(path.join(root, 'reports', 'incoming-inventory.json'), summary);
  console.log(JSON.stringify(summary.totals, null, 2));
}

if (process.argv[2] !== 'inventory') throw new Error('Usage: node src/incoming.mjs inventory');
await inventory();
