import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { inspectGlb } from '../src/lib/gltf.mjs';

function glb(document) {
  const json = Buffer.from(JSON.stringify(document));
  const padded = Buffer.concat([json, Buffer.alloc((4 - json.length % 4) % 4, 0x20)]);
  const buffer = Buffer.alloc(20 + padded.length);
  buffer.writeUInt32LE(0x46546c67, 0);
  buffer.writeUInt32LE(2, 4);
  buffer.writeUInt32LE(buffer.length, 8);
  buffer.writeUInt32LE(padded.length, 12);
  buffer.writeUInt32LE(0x4e4f534a, 16);
  padded.copy(buffer, 20);
  return buffer;
}

test('inspects a valid GLB 2.0 document', async () => {
  const dir = await mkdtemp(path.join(tmpdir(), 'archive-world-'));
  const file = path.join(dir, 'valid.glb');
  await writeFile(file, glb({ asset: { version: '2.0' }, meshes: [{}], scenes: [{}], materials: [{}], animations: [{}] }));
  const report = await inspectGlb(file);
  assert.equal(report.meshCount, 1);
  assert.equal(report.materialCount, 1);
  assert.equal(report.animationCount, 1);
});

test('rejects an invalid GLB header', async () => {
  const dir = await mkdtemp(path.join(tmpdir(), 'archive-world-'));
  const file = path.join(dir, 'invalid.glb');
  await writeFile(file, 'not a GLB');
  await assert.rejects(() => inspectGlb(file), /too small/);
});
