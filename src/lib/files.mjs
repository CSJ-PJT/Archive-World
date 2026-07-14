import { createHash } from 'node:crypto';
import { access, mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';

export async function exists(filePath) {
  try { await access(filePath); return true; } catch { return false; }
}

export async function ensureDir(directory) { await mkdir(directory, { recursive: true }); }
export async function readJson(filePath) { return JSON.parse(await readFile(filePath, 'utf8')); }

export async function writeJson(filePath, value) {
  await ensureDir(path.dirname(filePath));
  await writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

export async function fileInfo(filePath) {
  const content = await readFile(filePath);
  const info = await stat(filePath);
  return { bytes: info.size, sha256: createHash('sha256').update(content).digest('hex') };
}

export async function filesRecursively(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const fullPath = path.join(directory, entry.name);
    return entry.isDirectory() ? filesRecursively(fullPath) : [fullPath];
  }));
  return nested.flat();
}
