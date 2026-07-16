#!/usr/bin/env node
/** Structural GLB and candidate-contract validator for the external Batch 1 output. */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { generatedRoot } from '../src/world-output.mjs';

const root = resolve(process.env.ARCHIVE_WORLD_OUTPUT_ROOT ?? generatedRoot ?? 'C:/ArchiveData/World/Generated');
const manifestPath = resolve(root, 'v3/metadata/candidates/residential-batch1-manifest.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const errors = [];
const signatures = new Map();

function fail(assetId, error) { errors.push({ assetId, error }); }
function inspect(asset) {
  const bytes = readFileSync(resolve(root, asset.runtimePath));
  if (bytes.subarray(0, 4).toString('ascii') !== 'glTF') return fail(asset.assetId, 'invalid-magic');
  if (bytes.readUInt32LE(4) !== 2 || bytes.readUInt32LE(8) !== bytes.length) return fail(asset.assetId, 'invalid-header');
  const jsonLength = bytes.readUInt32LE(12), jsonType = bytes.readUInt32LE(16);
  if (jsonType !== 0x4e4f534a || 20 + jsonLength > bytes.length) return fail(asset.assetId, 'invalid-json-chunk');
  const gltf = JSON.parse(bytes.subarray(20, 20 + jsonLength).toString('utf8').trim());
  if (!gltf.meshes?.length || !gltf.accessors?.length) fail(asset.assetId, 'missing-mesh-or-accessor');
  const digest = createHash('sha256').update(bytes).digest('hex');
  if (digest !== asset.sha256) fail(asset.assetId, 'checksum-mismatch');
  if (!asset.groundAligned) fail(asset.assetId, 'ground-alignment-failed');
  if (!asset.floors || !asset.footprint?.length || !asset.materialCount) fail(asset.assetId, 'metadata-incomplete');
  const prior = signatures.get(asset.geometryFingerprint) ?? [];
  prior.push(asset.assetId); signatures.set(asset.geometryFingerprint, prior);
}

for (const asset of manifest.assets) inspect(asset);
for (const [fingerprint, ids] of signatures) if (ids.length > 1) errors.push({ assetId: ids.join(','), error: `duplicate-geometry-fingerprint:${fingerprint}` });
const report = {
  schema: 'archive-world.residential-batch1-validator/v1',
  manifest: 'v3/metadata/candidates/residential-batch1-manifest.json',
  candidates: manifest.assets.length,
  validatorErrors: errors.length,
  groundAligned: manifest.assets.filter((asset) => asset.groundAligned).length,
  metadataComplete: manifest.assets.filter((asset) => asset.floors && asset.footprint?.length && asset.materialCount).length,
  duplicateFingerprints: [...signatures.values()].filter((ids) => ids.length > 1),
  errors,
};
writeFileSync(resolve(root, 'reports/residential-batch1-validator.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report));
if (errors.length || manifest.assets.length !== 20 || report.groundAligned !== 20 || report.metadataComplete !== 20) process.exit(1);
