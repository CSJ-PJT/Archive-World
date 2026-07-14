#!/usr/bin/env node
/**
 * Resumable, single-Blender bulk processor for the Archive-World inventory.
 * It deliberately delegates one asset at a time to the already validated
 * canary pipeline, preserving the original source and its checksum.
 */
import { spawn } from 'node:child_process';
import { statfs, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { ensureDir, exists, fileInfo, readJson, writeJson } from './lib/files.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = new Set(process.argv.slice(2));
const resume = args.has('--resume');
const dryRun = args.has('--dry-run');
const blender = process.env.BLENDER_PATH || process.env.USER_BLENDER_PATH;
const relative = (value) => path.relative(root, value).replaceAll('\\', '/');
const now = () => new Date().toISOString();

function categoryPath(asset) {
  return asset.category === 'unknown' ? ['unknown'] : [asset.category, asset.subcategory ?? 'unknown'];
}

function outputPaths(asset) {
  const category = categoryPath(asset);
  const master = path.join(root, 'assets', 'optimized', 'master', ...category, `${asset.assetId}.glb`);
  const web = path.join(root, 'assets', 'optimized', 'web', ...category, asset.assetId);
  return {
    master,
    lods: [0, 1, 2].map((level) => path.join(web, `lod${level}.glb`)),
    preview: path.join(root, 'assets', 'previews', ...category, `${asset.assetId}.png`),
    thumbnail: path.join(root, 'assets', 'thumbnails', ...category, `${asset.assetId}.webp`),
    metadata: path.join(root, asset.metadataFile)
  };
}

async function sourceMatches(asset) {
  const source = path.join(root, asset.sourceFile);
  return (await exists(source)) && (await fileInfo(source)).sha256 === asset.sourceChecksum;
}

async function completed(asset) {
  const output = outputPaths(asset);
  if (!(await sourceMatches(asset)) || !(await exists(output.metadata))) return false;
  if (!(await exists(output.master)) || !(await exists(output.preview)) || !(await exists(output.thumbnail))) return false;
  if (!(await Promise.all(output.lods.map(exists))).every(Boolean)) return false;
  const metadata = await readJson(output.metadata);
  return metadata.sourceChecksum === asset.sourceChecksum && metadata.masterFile && metadata.webFiles?.length === 3;
}

function executeAsset(asset) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [path.join(root, 'src', 'canary.mjs'), asset.assetId], {
      cwd: root,
      env: process.env,
      stdio: 'inherit'
    });
    child.on('error', reject);
    child.on('exit', (code, signal) => code === 0 ? resolve() : reject(new Error(`asset process failed (${signal ?? `exit ${code}`})`)));
  });
}

async function freeGiB() {
  const disk = await statfs(root);
  return Math.round((Number(disk.bavail) * Number(disk.bsize) / 1024 ** 3) * 10) / 10;
}

function progress(completedCount, total, startedAt, currentId) {
  const elapsedMs = Date.now() - startedAt;
  const average = completedCount ? elapsedMs / completedCount : 0;
  return {
    completed: completedCount,
    total,
    currentAsset: currentId,
    elapsedMs,
    estimatedRemainingMs: Math.round(Math.max(0, total - completedCount) * average)
  };
}

async function manifests(results) {
  const complete = results.filter((item) => ['COMPLETED_WITH_WARNINGS', 'REUSED'].includes(item.status));
  const entries = [];
  for (const result of complete) {
    const metadata = await readJson(outputPaths(result.asset).metadata);
    entries.push({
      assetId: result.asset.assetId,
      category: result.asset.category,
      subcategory: result.asset.subcategory ?? null,
      sourceChecksum: result.asset.sourceChecksum,
      sourceFile: result.asset.sourceFile,
      master: metadata.masterFile,
      lods: metadata.lods?.map(({ level, path: file, bytes, sha256 }) => ({ level, path: file, bytes, sha256 })) ?? [],
      preview: metadata.preview,
      thumbnail: metadata.thumbnail,
      validationStatus: metadata.validationStatus,
      warnings: metadata.warnings ?? []
    });
  }
  const manifestRoot = path.join(root, 'assets', 'manifests');
  const grouped = Object.groupBy(entries, (entry) => entry.category ?? 'unknown');
  await writeJson(path.join(manifestRoot, 'archive-world-assets.json'), { schema: 'archive-world.local-manifest/v1', generatedAt: now(), assets: entries });
  for (const category of ['buildings', 'vehicles', 'roads', 'environment', 'props', 'unknown']) {
    await writeJson(path.join(manifestRoot, `${category}.json`), { schema: 'archive-world.category-manifest/v1', category, generatedAt: now(), assets: grouped[category] ?? [] });
  }
  return entries;
}

async function contactSheets(entries) {
  const directory = path.join(root, 'reports', 'contact-sheets');
  await ensureDir(directory);
  for (const [category, assets] of Object.entries(Object.groupBy(entries, (entry) => entry.category ?? 'unknown'))) {
    const tiles = assets.map((asset, index) => {
      const x = (index % 4) * 260; const y = Math.floor(index / 4) * 210;
      return `<g transform="translate(${x} ${y})"><rect width="250" height="200" rx="10" fill="#ffffff" stroke="#cbd5e1"/><image href="../../${asset.thumbnail}" x="10" y="10" width="230" height="145" preserveAspectRatio="xMidYMid meet"/><text x="12" y="176" font-size="12" fill="#0f172a">${asset.assetId}</text><text x="12" y="192" font-size="10" fill="#475569">${asset.validationStatus}</text></g>`;
    }).join('');
    const height = Math.max(220, Math.ceil(assets.length / 4) * 210);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="${height}" viewBox="0 0 1040 ${height}"><rect width="100%" height="100%" fill="#f8fafc"/>${tiles}</svg>`;
    await writeFile(path.join(directory, `${category}.svg`), svg, 'utf8');
  }
}

async function reports(results, entries, startedAt) {
  const failed = results.filter((item) => item.status === 'FAILED');
  const warnings = results.filter((item) => item.status === 'COMPLETED_WITH_WARNINGS' || item.status === 'REUSED').flatMap((item) => (item.warnings ?? []).map((warning) => ({ assetId: item.asset.assetId, warning })));
  const categories = Object.fromEntries(Object.entries(Object.groupBy(results, (item) => item.asset.category ?? 'unknown')).map(([key, values]) => [key, {
    total: values.length,
    completed: values.filter((item) => item.status === 'COMPLETED_WITH_WARNINGS').length,
    reused: values.filter((item) => item.status === 'REUSED').length,
    failed: values.filter((item) => item.status === 'FAILED').length
  }]));
  const outputBytes = entries.flatMap((entry) => entry.lods ?? []).reduce((total, lod) => total + (lod.bytes ?? 0), 0);
  const sourceBytes = results.reduce((total, item) => total + (item.asset.sourceBytes ?? 0), 0);
  const report = {
    schema: 'archive-world.bulk-results/v1', generatedAt: now(), resume, blenderConcurrency: 1,
    durationMs: Date.now() - startedAt, totals: {
      inventory: results.length,
      completed: results.filter((item) => item.status === 'COMPLETED_WITH_WARNINGS').length,
      warnings: results.filter((item) => item.status === 'COMPLETED_WITH_WARNINGS').length,
      failed: failed.length,
      reused: results.filter((item) => item.status === 'REUSED').length,
      sourceBytes, outputWebLodBytes: outputBytes, lodCount: entries.reduce((total, entry) => total + entry.lods.length, 0),
      freeGiB: await freeGiB(), blenderCrashes: failed.filter((item) => /blender|signal/i.test(item.error ?? '')).length
    }, categories, results: results.map(({ asset, ...result }) => ({ assetId: asset.assetId, category: asset.category, subcategory: asset.subcategory ?? null, sourceChecksum: asset.sourceChecksum, ...result }))
  };
  await writeJson(path.join(root, 'reports', 'bulk-results.json'), report);
  await writeJson(path.join(root, 'reports', 'failed-assets.json'), { generatedAt: now(), failures: failed.map(({ asset, ...item }) => ({ assetId: asset.assetId, ...item })) });
  await writeJson(path.join(root, 'reports', 'warnings.json'), { generatedAt: now(), warnings });
  const markdown = `# Archive-World Bulk Results\n\n- Inventory: ${report.totals.inventory}\n- Completed with warnings: ${report.totals.completed}\n- Reused: ${report.totals.reused}\n- Failed: ${report.totals.failed}\n- Free disk: ${report.totals.freeGiB} GiB\n- Blender crashes: ${report.totals.blenderCrashes}\n\n## Categories\n\n|Category|Total|Completed|Reused|Failed|\n|---|---:|---:|---:|---:|\n${Object.entries(categories).map(([name, value]) => `|${name}|${value.total}|${value.completed}|${value.reused}|${value.failed}|`).join('\n')}\n`;
  await writeFile(path.join(root, 'reports', 'bulk-results.md'), markdown, 'utf8');
  await writeJson(path.join(root, 'reports', 'missing-assets.json'), { schema: 'archive-world.missing-assets/v1', generatedAt: now(), missing: failed.map(({ asset, error }) => ({ assetId: asset.assetId, category: asset.category, status: 'PROCESSING_FAILED', reason: error })) });
  await writeFile(path.join(root, 'reports', 'world-readiness.md'), `# Archive Industrial City Readiness\n\nBulk pipeline status: ${failed.length ? 'PARTIAL_PASS' : 'PASS_WITH_WARNINGS'}.\n\n- Processed assets: ${entries.length}/${results.length}\n- Failed assets: ${failed.length}\n- Local-only manifests: assets/manifests/archive-world-assets.json\n- OCI upload: not performed\n- World assembly, Asset Browser, and Three.js Viewer: not performed\n`, 'utf8');
}

async function main() {
  if (!resume) throw new Error('Bulk processing requires --resume to protect completed checkpoints.');
  const mapping = await readJson(path.join(root, 'reports', 'asset-id-map.json'));
  const assets = mapping.assets.map((asset) => ({ ...asset, sourceBytes: 0 }));
  for (const asset of assets) asset.sourceBytes = (await fileInfo(path.join(root, asset.sourceFile))).bytes;
  const reusable = [];
  const pending = [];
  for (const asset of assets) (await completed(asset) ? reusable : pending).push(asset);
  const initial = await Promise.all(reusable.map(async (asset) => ({
    asset,
    status: 'REUSED',
    warnings: (await readJson(outputPaths(asset).metadata)).warnings ?? [],
    startedAt: null,
    finishedAt: now()
  })));
  console.log(JSON.stringify({ inventory: assets.length, reusable: reusable.length, pending: pending.length, dryRun, blenderConcurrency: 1 }, null, 2));
  if (dryRun) return;
  if (!blender || !(await exists(blender))) throw new Error('BLENDER_PATH must point to an existing Blender executable before Bulk processing can start.');
  const startedAt = Date.now(); const results = [...initial];
  for (const asset of pending) {
    const stageStarted = Date.now();
    try {
      await executeAsset(asset);
      if (!(await completed(asset))) throw new Error('FINAL_VALIDATION_FAILED');
      const metadata = await readJson(outputPaths(asset).metadata);
      results.push({ asset, status: 'COMPLETED_WITH_WARNINGS', warnings: metadata.warnings ?? [], startedAt: new Date(stageStarted).toISOString(), finishedAt: now(), durationMs: Date.now() - stageStarted });
    } catch (error) {
      results.push({ asset, status: 'FAILED', error: error.message, startedAt: new Date(stageStarted).toISOString(), finishedAt: now(), durationMs: Date.now() - stageStarted });
    }
    const state = progress(results.length, assets.length, startedAt, asset.assetId);
    if (results.length % 5 === 0 || results.length === assets.length) console.log(JSON.stringify({ ...state, freeGiB: await freeGiB() }));
  }
  const entries = await manifests(results);
  await contactSheets(entries);
  await reports(results, entries, startedAt);
}

main().catch((error) => { console.error(`Bulk processing error: ${error.message}`); process.exitCode = 1; });
