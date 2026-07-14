import { copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { ensureDir, exists, fileInfo, readJson, writeJson } from './lib/files.mjs';
import { inspectGlb } from './lib/gltf.mjs';
import { run } from './lib/process.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const blender = process.env.BLENDER_PATH || process.env.USER_BLENDER_PATH;
const ids = ['building-archiveos-2e8c32fa', 'vehicle-1-a74d9cb9', 'road-asset-7b6c3ac5'];
const selectedIds = process.argv.slice(2).length ? process.argv.slice(2) : ids;
const transform = path.join(root, 'node_modules', '.bin', process.platform === 'win32' ? 'gltf-transform.cmd' : 'gltf-transform');
const relative = (file) => path.relative(root, file).replaceAll('\\', '/');

async function blenderRun(script, args) {
  await run(blender, ['--background', '--python', path.join(root, 'scripts', 'blender', script), '--', ...args], { cwd: root });
}

async function transformRun(args) { await run(transform, args, { cwd: root }); }

async function processAsset(asset) {
  const started = Date.now();
  const source = path.join(root, asset.sourceFile); const checksumBefore = (await fileInfo(source)).sha256;
  const category = [asset.category, asset.subcategory ?? 'unknown'];
  const master = path.join(root, 'assets', 'optimized', 'master', ...category, `${asset.assetId}.glb`);
  const work = path.join(root, '.work', 'canary', asset.assetId);
  const web = path.join(root, 'assets', 'optimized', 'web', ...category, asset.assetId);
  const preview = path.join(root, 'assets', 'previews', ...category, `${asset.assetId}.png`);
  const thumbnail = path.join(root, 'assets', 'thumbnails', ...category, `${asset.assetId}.webp`);
  await Promise.all([ensureDir(path.dirname(master)), ensureDir(work), ensureDir(web), ensureDir(path.dirname(preview)), ensureDir(path.dirname(thumbnail))]);
  const reusable = (await exists(master)) && (await Promise.all([0, 1, 2].map((index) => exists(path.join(web, `lod${index}.glb`))))).every(Boolean) && await exists(preview) && await exists(thumbnail);
  if (!reusable) {
    await blenderRun('optimize.py', ['--input', source, '--output', master]);
    await blenderRun('lod.py', ['--input', master, '--output-dir', work, '--ratios', '1,0.5,0.2']);
    for (const index of [0, 1, 2]) await transformRun(['draco', path.join(work, `lod${index}.glb`), path.join(web, `lod${index}.glb`), '--method', 'edgebreaker']);
    await blenderRun('render_preview.py', ['--input', master, '--output', preview, '--size', '1600', '--transparent', 'false']);
    await blenderRun('render_preview.py', ['--input', master, '--output', thumbnail, '--size', '512', '--transparent', 'false']);
  }
  const checksumAfter = (await fileInfo(source)).sha256;
  if (checksumBefore !== checksumAfter || checksumBefore !== asset.sourceChecksum) throw new Error('SOURCE_CHECKSUM_CHANGED');
  const sourceInfo = await inspectGlb(source); const masterInfo = await inspectGlb(master);
  if (!masterInfo.meshCount || masterInfo.materialCount !== sourceInfo.materialCount || masterInfo.textureCount !== sourceInfo.textureCount) throw new Error('MASTER_MESH_MATERIAL_OR_TEXTURE_PRESERVATION_FAILED');
  const lods = [];
  for (const index of [0, 1, 2]) { const file = path.join(web, `lod${index}.glb`); const info = await inspectGlb(file); if (!info.meshCount || info.materialCount !== sourceInfo.materialCount || info.textureCount !== sourceInfo.textureCount) throw new Error(`LOD${index}_MESH_MATERIAL_OR_TEXTURE_PRESERVATION_FAILED`); lods.push({ level: index, path: relative(file), triangles: info.triangleCount, vertices: info.vertexCount, reductionRatio: sourceInfo.triangleCount ? info.triangleCount / sourceInfo.triangleCount : null, ...(await fileInfo(file)), materialCount: info.materialCount, textureCount: info.textureCount, animationCount: info.animationCount }); }
  if (!(await exists(preview)) || !(await exists(thumbnail))) throw new Error('RENDER_OUTPUT_MISSING');
  const metadataPath = path.join(root, asset.metadataFile); const metadata = await readJson(metadataPath);
  Object.assign(metadata, { masterFile: relative(master), webFiles: lods.map(({ path: value }) => value), preview: relative(preview), thumbnail: relative(thumbnail), lods, fileSizes: { source: sourceInfo.bytes, master: (await fileInfo(master)).bytes, web: lods.reduce((sum, value) => sum + value.bytes, 0) }, processedAt: new Date().toISOString(), blenderVersion: '4.5.10 LTS', validationStatus: 'COMPLETED_WITH_WARNINGS', warnings: [...new Set([...(metadata.warnings ?? []).filter((warning) => warning !== 'BLENDER_PROCESSING_BLOCKED: executable not available during Phase 2'), 'MESH_PRIMITIVE_GENERATED_TANGENT_SPACE'])], canary: { importSuccess: true, exportSuccess: true, sourceChecksumBefore: checksumBefore, sourceChecksumAfter: checksumAfter, masterChecksum: (await fileInfo(master)).sha256, durationMs: Date.now() - started, orientation: 'glTF Y-up via Blender exporter', unit: 'meter', pivot: 'source hierarchy preserved; no forced re-centering' } });
  await writeJson(metadataPath, metadata);
  return { assetId: asset.assetId, status: metadata.validationStatus, master: relative(master), web: lods.map(({ path: value }) => value), preview: relative(preview), thumbnail: relative(thumbnail), durationMs: Date.now() - started, warnings: metadata.warnings };
}

try {
  if (!blender || !(await exists(blender))) throw new Error('BLENDER_PATH is not an executable file.');
  const map = (await readJson(path.join(root, 'reports', 'asset-id-map.json'))).assets;
  const results = [];
  for (const id of selectedIds) { const asset = map.find((value) => value.assetId === id); if (!asset) throw new Error(`Canary mapping missing: ${id}`); results.push(await processAsset(asset)); }
  await writeJson(path.join(root, 'reports', 'canary-results.json'), { schema: 'archive-world.canary/v1', generatedAt: new Date().toISOString(), blender: '4.5.10 LTS', results });
  await writeJson(path.join(root, 'assets', 'manifests', 'canary-assets.json'), { schema: 'archive-world.local-manifest/v1', assets: results.map(({ assetId, status, web, preview, thumbnail }) => ({ assetId, status, defaultLod: 0, lodUrls: web, previewUrl: preview, thumbnailUrl: thumbnail })) });
  console.log(JSON.stringify({ completed: results.length, results }, null, 2));
} catch (error) { console.error(`Canary error: ${error.message}`); process.exitCode = 1; }
