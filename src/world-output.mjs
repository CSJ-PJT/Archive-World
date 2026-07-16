import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

export const repositoryRoot = resolve(import.meta.dirname, '..');
export const generatedRoot = process.env.ARCHIVE_WORLD_OUTPUT_ROOT
  ? resolve(process.env.ARCHIVE_WORLD_OUTPUT_ROOT)
  : null;

export const usingGeneratedOutput = Boolean(generatedRoot);

export function worldPath(generatedPath, fixturePath) {
  return usingGeneratedOutput
    ? resolve(generatedRoot, generatedPath)
    : resolve(repositoryRoot, fixturePath);
}

export function ensureGeneratedDirectory(...parts) {
  const folder = resolve(generatedRoot ?? repositoryRoot, ...parts);
  mkdirSync(folder, { recursive: true });
  return folder;
}
