#!/usr/bin/env node
import { copyFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { ensureDir, exists, fileInfo, filesRecursively, readJson, writeJson } from './lib/files.mjs';
import { inspectGlb } from './lib/gltf.mjs';
import { run } from './lib/process.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const defaults = {
  assetRoot: 'assets', lodRatios: [1, 0.5, 0.2],
  draco: { method: 'edgebreaker', quantizePosition: 14, quantizeNormal: 10, quantizeTexcoord: 12 },
  render: { previewSize: 1024, thumbnailSize: 320, transparent: true },
  oci: { profile: 'DEFAULT', namespace: '', bucket: 'archive-world-assets', prefix: 'digital-twin' }
};

function usage() {
  console.log(`Archive-World pipeline\n\nCommands:\n  init\n  ingest <Meshy-output.glb> <asset-id>\n  validate <asset-id|path-to.glb>\n  build <asset-id>\n  metadata <asset-id>\n  manifest [asset-id]\n  upload <asset-id>`);
}

function assetId(value) {
  if (!/^[a-z0-9][a-z0-9-]{1,62}$/.test(value ?? '')) throw new Error('Asset ID must be 2-63 lowercase letters, numbers, or hyphens.');
  return value;
}

async function config() {
  const localPath = path.join(root, 'world.config.json');
  const local = await exists(localPath) ? await readJson(localPath) : {};
  return { ...defaults, ...local, draco: { ...defaults.draco, ...local.draco }, render: { ...defaults.render, ...local.render }, oci: { ...defaults.oci, ...local.oci } };
}

function paths(cfg, id) {
  const assets = path.resolve(root, cfg.assetRoot);
  return {
    assets, source: path.join(assets, 'source', `${id}.glb`), work: path.join(root, '.work', id),
    optimized: path.join(assets, 'optimized', id), preview: path.join(assets, 'previews', `${id}.png`),
    thumbnail: path.join(assets, 'thumbnails', `${id}.png`), metadata: path.join(assets, 'world', `${id}.metadata.json`),
    manifest: path.join(assets, 'world', `${id}.manifest.json`)
  };
}

async function blender(cfg, script, args) {
  const executable = process.env.BLENDER_PATH || cfg.blenderPath || 'blender';
  await run(executable, ['--background', '--python', path.join(root, 'scripts', 'blender', script), '--', ...args], { cwd: root });
}

async function gltfTransform(args) {
  const executable = process.platform === 'win32' ? path.join(root, 'node_modules', '.bin', 'gltf-transform.cmd') : path.join(root, 'node_modules', '.bin', 'gltf-transform');
  if (!(await exists(executable))) throw new Error('gltf-transform is not installed. Run npm install before compression.');
  await run(executable, args, { cwd: root });
}

async function initialize(cfg) {
  for (const folder of ['source', 'optimized', 'previews', 'thumbnails', 'animations', 'materials', 'world']) await ensureDir(path.join(root, cfg.assetRoot, folder));
  await ensureDir(path.join(root, '.work'));
  const localConfig = path.join(root, 'world.config.json');
  if (!(await exists(localConfig))) await copyFile(path.join(root, 'world.config.example.json'), localConfig);
  console.log('Pipeline folders are ready. Configure world.config.json and .env before OCI upload.');
}

async function validate(cfg, value) {
  const target = value?.endsWith('.glb') ? path.resolve(root, value) : paths(cfg, assetId(value)).source;
  if (!(await exists(target))) throw new Error(`GLB not found: ${target}`);
  const report = await inspectGlb(target);
  if (report.meshCount === 0) throw new Error('GLB contains no meshes.');
  const executable = process.platform === 'win32' ? path.join(root, 'node_modules', '.bin', 'gltf-transform.cmd') : path.join(root, 'node_modules', '.bin', 'gltf-transform');
  if (await exists(executable)) await gltfTransform(['validate', target]);
  else console.warn('gltf-transform is not installed; only the built-in GLB structural validation was run.');
  console.log(JSON.stringify({ valid: true, file: path.relative(root, target), ...report }, null, 2));
  return report;
}

async function ingest(cfg, sourceFile, id) {
  id = assetId(id);
  const input = path.resolve(root, sourceFile);
  if (path.extname(input).toLowerCase() !== '.glb') throw new Error('Only Meshy GLB uploads are accepted by this pipeline.');
  if (!(await exists(input))) throw new Error(`Upload file not found: ${input}`);
  await validate(cfg, input);
  const output = paths(cfg, id).source;
  await ensureDir(path.dirname(output));
  await copyFile(input, output);
  console.log(`Ingested ${path.relative(root, input)} -> ${path.relative(root, output)}`);
}

async function optimizeAndLod(cfg, id) {
  const p = paths(cfg, id);
  await ensureDir(p.work); await ensureDir(p.optimized);
  const optimizedWork = path.join(p.work, 'optimized.glb');
  await blender(cfg, 'optimize.py', ['--input', p.source, '--output', optimizedWork]);
  await blender(cfg, 'lod.py', ['--input', optimizedWork, '--output-dir', p.work, '--ratios', cfg.lodRatios.join(',')]);
  for (let index = 0; index < cfg.lodRatios.length; index += 1) {
    await gltfTransform(['draco', path.join(p.work, `lod${index}.glb`), path.join(p.optimized, `lod${index}.glb`), '--method', cfg.draco.method, '--quantize-position', String(cfg.draco.quantizePosition), '--quantize-normal', String(cfg.draco.quantizeNormal), '--quantize-texcoord', String(cfg.draco.quantizeTexcoord)]);
  }
}

async function render(cfg, id) {
  const p = paths(cfg, id);
  await ensureDir(path.dirname(p.preview)); await ensureDir(path.dirname(p.thumbnail));
  const input = path.join(p.work, 'optimized.glb');
  await blender(cfg, 'render_preview.py', ['--input', input, '--output', p.preview, '--size', String(cfg.render.previewSize), '--transparent', String(cfg.render.transparent)]);
  await blender(cfg, 'render_preview.py', ['--input', input, '--output', p.thumbnail, '--size', String(cfg.render.thumbnailSize), '--transparent', String(cfg.render.transparent)]);
}

async function metadata(cfg, id) {
  const p = paths(cfg, id); const source = await inspectGlb(p.source); const lods = [];
  for (let index = 0; index < cfg.lodRatios.length; index += 1) {
    const file = path.join(p.optimized, `lod${index}.glb`);
    lods.push({ level: index, ratio: cfg.lodRatios[index], path: path.relative(root, file).replaceAll('\\', '/'), ...(await fileInfo(file)), ...(await inspectGlb(file)) });
  }
  const document = {
    schema: 'archive-world.asset-metadata/v1', assetId: id,
    source: { path: path.relative(root, p.source).replaceAll('\\', '/'), ...(await fileInfo(p.source)), ...source }, lods,
    preview: { path: path.relative(root, p.preview).replaceAll('\\', '/'), ...(await fileInfo(p.preview)) },
    thumbnail: { path: path.relative(root, p.thumbnail).replaceAll('\\', '/'), ...(await fileInfo(p.thumbnail)) },
    generatedAt: new Date().toISOString(), pipeline: { blender: 'CLI', compression: 'Draco' }
  };
  await writeJson(p.metadata, document); console.log(`Metadata: ${path.relative(root, p.metadata)}`); return document;
}

async function oneManifest(cfg, id) {
  const p = paths(cfg, id); const metadataDocument = await readJson(p.metadata);
  const prefix = [cfg.oci.prefix, id].filter(Boolean).join('/');
  const document = {
    schema: 'archive-world.three-manifest/v1', assetId: id, generatedAt: new Date().toISOString(),
    loader: { type: 'GLTFLoader', dracoDecoder: { required: true, path: '/draco/' } },
    preview: `${prefix}/previews/${id}.png`, thumbnail: `${prefix}/thumbnails/${id}.png`,
    lods: metadataDocument.lods.map(({ level, ratio, bytes, sha256 }) => ({ level, ratio, url: `${prefix}/optimized/lod${level}.glb`, bytes, sha256 })),
    metadata: `${prefix}/world/${id}.metadata.json`
  };
  await writeJson(p.manifest, document); return document;
}

async function manifest(cfg, id) {
  if (id) { assetId(id); await oneManifest(cfg, id); console.log(`Manifest: assets/world/${id}.manifest.json`); return; }
  const world = path.join(root, cfg.assetRoot, 'world');
  for (const file of await filesRecursively(world)) if (file.endsWith('.metadata.json')) await oneManifest(cfg, path.basename(file, '.metadata.json'));
  console.log('All available manifests generated.');
}

async function upload(cfg, id) {
  id = assetId(id); const p = paths(cfg, id);
  const namespace = process.env.OCI_OS_NAMESPACE || cfg.oci.namespace;
  const bucket = process.env.OCI_OS_BUCKET || cfg.oci.bucket;
  const profile = process.env.OCI_CLI_PROFILE || cfg.oci.profile;
  const base = process.env.OCI_OS_PREFIX || cfg.oci.prefix;
  if (!namespace || !bucket) throw new Error('OCI namespace and bucket are required. Set OCI_OS_NAMESPACE and OCI_OS_BUCKET.');
  const uploads = [...(await filesRecursively(p.optimized)), p.preview, p.thumbnail, p.metadata, p.manifest];
  for (const file of uploads) {
    const relative = path.relative(p.assets, file).replaceAll('\\', '/').split('/');
    const [category, ...rest] = relative;
    // optimized assets include the asset ID in their local directory, while OCI
    // consistently places the ID directly below the configured deployment prefix.
    const objectParts = category === 'optimized' ? [base, id, category, ...rest.slice(1)] : [base, id, category, ...rest];
    await run('oci', ['os', 'object', 'put', '--namespace', namespace, '--bucket-name', bucket, '--name', objectParts.filter(Boolean).join('/'), '--file', file, '--force', '--profile', profile], { cwd: root });
  }
  console.log(`Uploaded ${uploads.length} files to oci://${bucket}/${base}/${id}`);
}

async function build(cfg, id) {
  id = assetId(id); await validate(cfg, id); await optimizeAndLod(cfg, id); await render(cfg, id); await metadata(cfg, id); await manifest(cfg, id);
  console.log(`Build completed for ${id}. Run npm run world -- upload ${id} when OCI credentials are ready.`);
}

const [command, ...args] = process.argv.slice(2);
try {
  const cfg = await config();
  if (!command || command === '--help' || command === '-h') usage();
  else if (command === 'init') await initialize(cfg);
  else if (command === 'ingest') await ingest(cfg, args[0], args[1]);
  else if (command === 'validate') await validate(cfg, args[0]);
  else if (command === 'build') await build(cfg, args[0]);
  else if (command === 'metadata') await metadata(cfg, assetId(args[0]));
  else if (command === 'manifest') await manifest(cfg, args[0]);
  else if (command === 'upload') await upload(cfg, args[0]);
  else throw new Error(`Unknown command: ${command}`);
} catch (error) { console.error(`Pipeline error: ${error.message}`); process.exitCode = 1; }
