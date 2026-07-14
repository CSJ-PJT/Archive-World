import { open, readFile } from 'node:fs/promises';

const GLB_MAGIC = 0x46546c67;
const GLB_VERSION = 2;
const JSON_CHUNK = 0x4e4f534a;

export async function readGlbDocument(filePath) {
  const handle = await open(filePath, 'r');
  try {
    const header = Buffer.alloc(20);
    const { bytesRead } = await handle.read(header, 0, header.length, 0);
    if (bytesRead < 20) throw new Error('GLB is too small to contain a valid header.');
    if (header.readUInt32LE(0) !== GLB_MAGIC) throw new Error('Invalid GLB magic; expected glTF binary (glTF).');
    const version = header.readUInt32LE(4);
    if (version !== GLB_VERSION) throw new Error(`Unsupported GLB version ${version}; expected 2.`);
    const declaredLength = header.readUInt32LE(8);
    const fileSize = (await handle.stat()).size;
    if (declaredLength !== fileSize) throw new Error(`GLB length mismatch: header=${declaredLength}, file=${fileSize}.`);
    const jsonLength = header.readUInt32LE(12);
    if (header.readUInt32LE(16) !== JSON_CHUNK || 20 + jsonLength > fileSize) throw new Error('GLB does not have a valid JSON chunk.');
    const jsonChunk = Buffer.alloc(jsonLength);
    await handle.read(jsonChunk, 0, jsonLength, 20);
    let document;
    try { document = JSON.parse(jsonChunk.toString('utf8').trim()); }
    catch { throw new Error('GLB JSON chunk cannot be parsed.'); }
    if (document.asset?.version !== '2.0') throw new Error('GLB asset.version must be "2.0".');
    return { document, bytes: fileSize, version };
  } finally { await handle.close(); }
}

export async function inspectGlb(filePath) {
  const buffer = await readFile(filePath);
  if (buffer.length < 20) throw new Error('GLB is too small to contain a valid header.');
  if (buffer.readUInt32LE(0) !== GLB_MAGIC) throw new Error('Invalid GLB magic; expected glTF binary (glTF).');
  const version = buffer.readUInt32LE(4);
  if (version !== GLB_VERSION) throw new Error(`Unsupported GLB version ${version}; expected 2.`);
  const declaredLength = buffer.readUInt32LE(8);
  if (declaredLength !== buffer.length) throw new Error(`GLB length mismatch: header=${declaredLength}, file=${buffer.length}.`);
  const chunkLength = buffer.readUInt32LE(12);
  if (buffer.readUInt32LE(16) !== JSON_CHUNK || 20 + chunkLength > buffer.length) throw new Error('GLB does not have a valid JSON chunk.');
  let document;
  try { document = JSON.parse(buffer.subarray(20, 20 + chunkLength).toString('utf8').trim()); }
  catch { throw new Error('GLB JSON chunk cannot be parsed.'); }
  if (document.asset?.version !== '2.0') throw new Error('GLB asset.version must be "2.0".');
  return {
    format: 'glb', version, bytes: buffer.length,
    meshCount: document.meshes?.length ?? 0,
    vertexCount: (document.accessors ?? []).reduce((total, value) => total + (value.type === 'VEC3' && value.count ? value.count : 0), 0),
    triangleCount: (document.accessors ?? []).reduce((total, value) => total + (value.type === 'SCALAR' && value.count ? Math.floor(value.count / 3) : 0), 0),
    materialCount: document.materials?.length ?? 0, textureCount: document.textures?.length ?? 0, animationCount: document.animations?.length ?? 0,
    sceneCount: document.scenes?.length ?? 0, extensionsUsed: document.extensionsUsed ?? [],
    generator: document.asset.generator ?? null
  };
}
