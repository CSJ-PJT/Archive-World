#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { copyFile, mkdir, readdir, rename, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { ensureDir, exists, readJson, writeJson } from './lib/files.mjs';
import { readGlbDocument } from './lib/gltf.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sourceRoot = process.env.MESHY_SOURCE_ROOT;
if (!sourceRoot) throw new Error('MESHY_SOURCE_ROOT must point to the read-only Meshy source root.');
const supported = new Set(['.glb', '.gltf', '.fbx', '.obj', '.zip', '.png', '.jpg', '.jpeg', '.webp', '.exr', '.hdr', '.bin', '.mtl', '.blend']);
const models = new Set(['.glb', '.gltf', '.fbx', '.obj']);

function relative(file) { return path.relative(sourceRoot, file).replaceAll('\\', '/'); }
function projectRelative(file) { return path.relative(root, file).replaceAll('\\', '/'); }
function toAscii(value) {
  return value.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
    .replace(/archive\s*os/g, 'archiveos').replace(/archive\s*logistis|archive\s*logistics/g, 'logistics')
    .replace(/archive\s*market/g, 'market').replace(/archive\s*nexus/g, 'nexus').replace(/archive\s*ledger/g, 'ledger')
    .replace(/물류\s*트럭/g, 'logistics-truck').replace(/화물\s*트럭/g, 'cargo-truck').replace(/냉동\s*탑차/g, 'refrigerated-truck')
    .replace(/통근\s*버스/g, 'commuter-bus').replace(/공장/g, 'factory').replace(/도로/g, 'road').replace(/산책로/g, 'walkway')
    .replace(/주유소/g, 'gas-station').replace(/높은\s*빌딩/g, 'high-rise').replace(/입구/g, 'entrance')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'asset';
}

function classify(item) {
  const evidence = [item.originalRelativePath, item.sceneNames?.join(' '), item.nodeNames?.join(' ')].join(' ').toLowerCase();
  const has = (...terms) => terms.some((term) => evidence.includes(term));
  if (has('물류 트럭', '화물 트럭', '냉동 탑차', ' truck')) return { category: 'vehicles', subcategory: 'trucks', confidence: 'high', evidence: 'source path and GLB scene/node names' };
  if (has('통근 버스', ' bus')) return { category: 'vehicles', subcategory: 'unknown', confidence: 'medium', evidence: 'vehicle indicated by source path/name; no bus taxonomy configured' };
  if (has('four_way', 'four way', 'intersection', '교차')) return { category: 'roads', subcategory: 'intersections', confidence: 'high', evidence: 'source path/name and GLB metadata' };
  if (has('highway', 'road', '도로', '진입로')) return { category: 'roads', subcategory: 'straight', confidence: 'medium', evidence: 'source path/name and GLB metadata' };
  if (has('archive os', 'archiveos')) return { category: 'buildings', subcategory: 'archiveos', confidence: 'high', evidence: 'source path and GLB metadata' };
  if (has('archive market', 'market')) return { category: 'buildings', subcategory: 'market', confidence: 'high', evidence: 'source path and GLB metadata' };
  if (has('archive nexus', 'nexus', 'factory', '공장')) return { category: 'buildings', subcategory: 'factory', confidence: 'high', evidence: 'source path and GLB metadata' };
  if (has('archive logistis', 'archive logistics', '물류')) return { category: 'buildings', subcategory: 'logistics', confidence: 'high', evidence: 'source path and GLB metadata' };
  if (has('archive ledger', 'ledger')) return { category: 'buildings', subcategory: 'ledger', confidence: 'high', evidence: 'source path and GLB metadata' };
  if (has('빌딩', 'building', '주유소', 'gas-station')) return { category: 'buildings', subcategory: 'infrastructure', confidence: 'medium', evidence: 'source path/name and GLB metadata' };
  return { category: 'unknown', subcategory: null, confidence: 'low', evidence: 'insufficient semantic evidence for safe classification' };
}

function primitiveTriangles(primitive, accessors) {
  const count = primitive.indices === undefined ? (accessors[primitive.attributes?.POSITION]?.count ?? 0) : (accessors[primitive.indices]?.count ?? 0);
  if ([5, 6].includes(primitive.mode)) return Math.max(0, count - 2);
  return primitive.mode === undefined || primitive.mode === 4 ? Math.floor(count / 3) : 0;
}

function analyzeDocument(document, bytes) {
  const accessors = document.accessors ?? []; const meshes = document.meshes ?? []; const nodes = document.nodes ?? [];
  const primitives = meshes.flatMap((mesh) => mesh.primitives ?? []);
  const positionAccessors = primitives.map((p) => accessors[p.attributes?.POSITION]).filter(Boolean);
  const dimensions = positionAccessors.reduce((out, accessor) => {
    if (!accessor.min || !accessor.max) return out;
    return { min: out.min.map((v, i) => Math.min(v, accessor.min[i])), max: out.max.map((v, i) => Math.max(v, accessor.max[i])) };
  }, { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] });
  const hasBounds = dimensions.min.every(Number.isFinite) && dimensions.max.every(Number.isFinite);
  const externalUris = [...(document.buffers ?? []), ...(document.images ?? [])].map((value) => value.uri).filter(Boolean);
  const invalidTransforms = nodes.filter((node) => [...(node.matrix ?? []), ...(node.translation ?? []), ...(node.rotation ?? []), ...(node.scale ?? [])].some((value) => !Number.isFinite(value))).map((node) => node.name ?? null);
  const negativeScaleNodes = nodes.filter((node) => (node.scale ?? []).some((value) => value < 0)).map((node) => node.name ?? null);
  const badTextureRefs = (document.textures ?? []).map((texture, index) => ({ texture, index })).filter(({ texture }) => texture.source !== undefined && !document.images?.[texture.source]).map(({ index }) => index);
  const warnings = [];
  if (!document.scenes?.length) warnings.push('NO_SCENE');
  if (!meshes.length) warnings.push('NO_MESH');
  if (externalUris.length) warnings.push('EXTERNAL_URI');
  if (invalidTransforms.length) warnings.push('INVALID_TRANSFORM');
  if (negativeScaleNodes.length) warnings.push('NEGATIVE_SCALE');
  if (badTextureRefs.length) warnings.push('MISSING_TEXTURE_REFERENCE');
  if (!hasBounds) warnings.push('MISSING_POSITION_BOUNDS');
  if (primitives.some((p) => p.attributes?.NORMAL === undefined)) warnings.push('MISSING_NORMALS');
  const nodeNames = nodes.map((node) => node.name).filter(Boolean);
  const animationClips = (document.animations ?? []).map((animation, index) => animation.name || `animation-${index}`);
  const wheelNodes = nodeNames.filter((name) => /wheel|tire|바퀴/i.test(name));
  const doorNodes = nodeNames.filter((name) => /door|문/i.test(name));
  const bounds = hasBounds ? { min: dimensions.min, max: dimensions.max } : null;
  return {
    validationStatus: warnings.some((warning) => ['NO_SCENE', 'NO_MESH', 'EXTERNAL_URI', 'INVALID_TRANSFORM', 'MISSING_TEXTURE_REFERENCE'].includes(warning)) ? 'INVALID' : warnings.length ? 'VALID_WITH_WARNINGS' : 'VALID',
    meshCount: meshes.length, nodeCount: nodes.length, primitiveCount: primitives.length,
    vertexCount: positionAccessors.reduce((sum, accessor) => sum + (accessor.count ?? 0), 0),
    triangleCount: primitives.reduce((sum, primitive) => sum + primitiveTriangles(primitive, accessors), 0),
    materialCount: document.materials?.length ?? 0, textureCount: document.textures?.length ?? 0,
    imageCount: document.images?.length ?? 0, animationCount: document.animations?.length ?? 0,
    skinCount: document.skins?.length ?? 0, sceneCount: document.scenes?.length ?? 0,
    bounds, dimensions: bounds ? bounds.max.map((value, index) => value - bounds.min[index]) : null,
    externalUris, invalidTransforms, negativeScaleNodes, badTextureRefs, warnings,
    nodeNames, sceneNames: (document.scenes ?? []).map((scene) => scene.name).filter(Boolean), animationClips, wheelNodes, doorNodes,
    rigged: (document.skins?.length ?? 0) > 0, animationReady: (document.skins?.length ?? 0) > 0 || animationClips.length > 0,
    bytes, generator: document.asset?.generator ?? null, extensionsUsed: document.extensionsUsed ?? []
  };
}

async function sha256(file) {
  return new Promise((resolve, reject) => {
    const hash = createHash('sha256'); const input = createReadStream(file);
    input.on('error', reject); input.on('data', (chunk) => hash.update(chunk)); input.on('end', () => resolve(hash.digest('hex')));
  });
}

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const results = await Promise.all(entries.map(async (entry) => entry.isDirectory() ? walk(path.join(directory, entry.name)) : [path.join(directory, entry.name)]));
  return results.flat();
}

async function inventory() {
  if (!(await exists(sourceRoot))) throw new Error(`Meshy source is unavailable: ${sourceRoot}`);
  // Incoming and Rejected are operational queues, not part of the immutable 46-file source baseline.
  const files = (await walk(sourceRoot)).filter((file) => {
    const rel = relative(file).toLowerCase();
    return !rel.startsWith('incoming/') && !rel.startsWith('rejected/');
  }); const records = [];
  for (const file of files.sort()) {
    const info = await stat(file); const extension = path.extname(file).toLowerCase();
    const record = { originalRelativePath: relative(file), filename: path.basename(file), extension, bytes: info.size, modifiedAt: info.mtime.toISOString(), sha256: await sha256(file), supported: supported.has(extension), type: models.has(extension) ? 'model' : extension === '.zip' ? 'archive' : ['.png', '.jpg', '.jpeg', '.webp', '.exr', '.hdr'].includes(extension) ? 'texture' : 'other', zipContents: [] };
    if (extension === '.glb') {
      try { Object.assign(record, analyzeDocument((await readGlbDocument(file)).document, info.size)); }
      catch (error) { record.validationStatus = 'INVALID'; record.warnings = [`GLB_PARSE_ERROR: ${error.message}`]; }
    }
    if (record.type === 'model') Object.assign(record, classify(record));
    records.push(record);
  }
  const duplicateGroups = Object.values(Object.groupBy(records, ({ sha256: value }) => value)).filter((group) => group.length > 1).map((group) => ({ sha256: group[0].sha256, files: group.map(({ originalRelativePath, bytes }) => ({ originalRelativePath, bytes })) }));
  const unsupported = records.filter((record) => !record.supported);
  const reportDir = path.join(root, 'reports'); await ensureDir(reportDir);
  await writeJson(path.join(reportDir, 'meshy-inventory.json'), { schema: 'archive-world.meshy-inventory/v1', sourceRoot, createdAt: new Date().toISOString(), files: records });
  await writeJson(path.join(reportDir, 'duplicate-assets.json'), { schema: 'archive-world.duplicates/v1', duplicateGroups });
  await writeJson(path.join(reportDir, 'unsupported-files.json'), unsupported);
  const summary = `# Meshy Inventory\n\n- Source: \`${sourceRoot}\`\n- Files: ${records.length}\n- Bytes: ${records.reduce((sum, record) => sum + record.bytes, 0)}\n- Models: ${records.filter((record) => record.type === 'model').length}\n- Duplicate SHA groups: ${duplicateGroups.length}\n- Unsupported: ${unsupported.length}\n\n|Category|Assets|\n|---|---:|\n${Object.entries(Object.groupBy(records.filter((record) => record.type === 'model'), (record) => `${record.category}/${record.subcategory ?? 'none'}`)).map(([key, value]) => `|${key}|${value.length}|`).join('\n')}\n`;
  await writeJson(path.join(root, '.pipeline', 'inventory-state.json'), { sourceRoot, generatedAt: new Date().toISOString(), files: records.map(({ originalRelativePath, sha256, bytes }) => ({ originalRelativePath, sha256, bytes })) });
  await import('node:fs/promises').then(({ writeFile }) => writeFile(path.join(reportDir, 'meshy-inventory.md'), summary));
  await import('node:fs/promises').then(({ writeFile }) => writeFile(path.join(reportDir, 'unsupported-files.md'), unsupported.length ? unsupported.map((record) => `- ${record.originalRelativePath}`).join('\n') + '\n' : '# Unsupported files\n\nNone.\n'));
  console.log(JSON.stringify({ files: records.length, models: records.filter((record) => record.type === 'model').length, duplicateGroups: duplicateGroups.length, unsupported: unsupported.length }, null, 2));
  return records;
}

function assetId(record) {
  const kind = record.category === 'buildings' ? 'building' : record.category === 'vehicles' ? 'vehicle' : record.category === 'roads' ? 'road' : record.category === 'environment' ? 'environment' : 'unknown';
  return `${kind}-${toAscii(path.basename(record.filename, record.extension))}-${record.sha256.slice(0, 8)}`.slice(0, 63);
}

async function ingest() {
  const report = await readJson(path.join(root, 'reports', 'meshy-inventory.json'));
  const map = []; const failures = [];
  for (const record of report.files.filter((item) => item.type === 'model' && item.supported)) {
    const id = assetId(record); const categoryPath = record.category === 'unknown' ? ['unknown'] : [record.category, record.subcategory ?? 'unknown'];
    const destination = path.join(root, 'assets', 'source', 'meshy', ...categoryPath, record.filename);
    try {
      await ensureDir(path.dirname(destination));
      if (await exists(destination)) {
        if ((await sha256(destination)) !== record.sha256) throw new Error('existing destination checksum differs; refusing overwrite');
      } else {
        const temporary = `${destination}.partial`;
        await copyFile(path.join(sourceRoot, record.originalRelativePath), temporary);
        if ((await sha256(temporary)) !== record.sha256) throw new Error('copied checksum mismatch');
        await rename(temporary, destination);
      }
      const sourceFile = projectRelative(destination);
      const metadataPath = path.join(root, 'assets', 'metadata', ...categoryPath, `${id}.json`);
      const metadata = { schema: 'archive-world.asset-metadata/v1', assetId: id, originalName: record.filename, originalRelativePath: record.originalRelativePath, category: record.category, subcategory: record.subcategory, source: 'Meshy', sourceFormat: record.extension.slice(1), sourceChecksum: record.sha256, version: null, license: null, dimensions: record.dimensions ?? null, bounds: record.bounds ?? null, pivotPolicy: null, meshCount: record.meshCount ?? null, nodeCount: record.nodeCount ?? null, vertices: record.vertexCount ?? null, triangles: record.triangleCount ?? null, materials: record.materialCount ?? null, textures: record.textureCount ?? null, skins: record.skinCount ?? null, animations: record.animationClips ?? [], animationReady: record.animationReady ?? false, rigged: record.rigged ?? false, wheelNodes: record.wheelNodes ?? [], doorNodes: record.doorNodes ?? [], lods: [], sourceFile, masterFile: null, webFiles: [], preview: null, thumbnail: null, fileSizes: { source: record.bytes, master: null, web: null }, pipelineVersion: '0.2.0', processedAt: new Date().toISOString(), warnings: [...(record.warnings ?? []), 'BLENDER_PROCESSING_BLOCKED: executable not available during Phase 2'], validationStatus: record.validationStatus ?? (record.supported ? 'UNSUPPORTED' : 'UNSUPPORTED') };
      await writeJson(metadataPath, metadata);
      map.push({ assetId: id, originalRelativePath: record.originalRelativePath, sourceFile, metadataFile: projectRelative(metadataPath), category: record.category, subcategory: record.subcategory, sourceChecksum: record.sha256, validationStatus: metadata.validationStatus, classificationEvidence: record.evidence, classificationConfidence: record.confidence });
    } catch (error) { failures.push({ originalRelativePath: record.originalRelativePath, error: error.message }); }
  }
  await writeJson(path.join(root, 'reports', 'asset-id-map.json'), { schema: 'archive-world.asset-id-map/v1', generatedAt: new Date().toISOString(), assets: map, failures });
  await writeJson(path.join(root, '.pipeline', 'state.json'), { pipelineVersion: '0.2.0', stage: 'INGESTED_BLENDER_BLOCKED', generatedAt: new Date().toISOString(), assets: map.map(({ assetId: id, sourceChecksum, validationStatus }) => ({ assetId: id, sourceChecksum, validationStatus })) });
  console.log(JSON.stringify({ ingested: map.length, failures: failures.length, blender: 'BLOCKED' }, null, 2));
}

async function verify() {
  const mapping = await readJson(path.join(root, 'reports', 'asset-id-map.json'));
  const results = [];
  for (const asset of mapping.assets) {
    const original = path.join(sourceRoot, asset.originalRelativePath);
    const source = path.join(root, asset.sourceFile);
    const [originalChecksum, copiedChecksum] = await Promise.all([sha256(original), sha256(source)]);
    results.push({ assetId: asset.assetId, originalRelativePath: asset.originalRelativePath, sourceFile: asset.sourceFile, expectedChecksum: asset.sourceChecksum, originalChecksum, copiedChecksum, matches: originalChecksum === asset.sourceChecksum && copiedChecksum === asset.sourceChecksum });
  }
  const mismatches = results.filter((result) => !result.matches);
  await writeJson(path.join(root, 'reports', 'source-integrity.json'), { schema: 'archive-world.source-integrity/v1', verifiedAt: new Date().toISOString(), checked: results.length, mismatches, results });
  console.log(JSON.stringify({ checked: results.length, mismatches: mismatches.length }, null, 2));
}

async function readiness() {
  const mapping = await readJson(path.join(root, 'reports', 'asset-id-map.json'));
  const count = (category, subcategory) => mapping.assets.filter((asset) => asset.category === category && (!subcategory || asset.subcategory === subcategory)).length;
  const requirements = [
    ['ArchiveOS District', count('buildings', 'archiveos'), ['Control Center', 'AI/Data Center', 'Security Center']],
    ['Market District', count('buildings', 'market'), ['Commerce Hub', 'Order Center', 'Warehouse']],
    ['Nexus District', count('buildings', 'factory'), ['Smart Factory', 'Quality Building', 'Material Warehouse', 'Maintenance Facility']],
    ['Logistics District', count('buildings', 'logistics'), ['Distribution Center', 'Truck Terminal', 'Cold Storage', 'Container Yard']],
    ['Ledger District', count('buildings', 'ledger'), ['Settlement Center', 'Financial Data Center', 'Audit/Reconciliation Center']],
    ['Infrastructure', count('roads'), ['roads', 'intersections', 'parking', 'truck yard', 'bridge/ramp', 'power', 'communication', 'security gate']],
    ['Vehicles', count('vehicles'), ['truck', 'delivery van', 'forklift', 'AGV', 'drone']]
  ].map(([district, available, required]) => ({ district, status: available ? 'PARTIAL' : 'MISSING', availableSourceAssets: available, required }));
  const missing = requirements.flatMap((item) => item.required.map((name) => ({ district: item.district, asset: name, status: item.status === 'MISSING' ? 'MISSING' : 'UNVERIFIED' })));
  const markdown = `# Archive Industrial City Readiness\n\nThis is source-level readiness only. No source asset is web-ready until the Blender canary succeeds.\n\n|Area|Status|Available source assets|\n|---|---|---:|\n${requirements.map((item) => `|${item.district}|${item.status}|${item.availableSourceAssets}|`).join('\n')}\n\n## Blocker\n\nBlender executable is unavailable, so no canary, optimized model, LOD, render, or world scene has been generated.\n`;
  await writeJson(path.join(root, 'reports', 'missing-assets.json'), { schema: 'archive-world.missing-assets/v1', generatedAt: new Date().toISOString(), missing });
  await import('node:fs/promises').then(({ writeFile }) => writeFile(path.join(root, 'reports', 'world-readiness.md'), markdown));
  console.log(JSON.stringify({ districts: requirements.length, blender: 'BLOCKED', worldScene: 'NOT_CREATED' }, null, 2));
}

const command = process.argv[2];
try {
  if (command === 'inventory') await inventory();
  else if (command === 'ingest') await ingest();
  else if (command === 'verify') await verify();
  else if (command === 'readiness') await readiness();
  else throw new Error('Usage: node src/bulk.mjs <inventory|ingest|verify|readiness>');
} catch (error) { console.error(`Bulk pipeline error: ${error.message}`); process.exitCode = 1; }
