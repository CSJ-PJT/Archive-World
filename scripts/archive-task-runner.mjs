#!/usr/bin/env node
/** Run an Archive task and asynchronously notify without changing its exit code. */
import { spawn, spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const repositoryRoot = resolve(import.meta.dirname, '..');
const args = process.argv.slice(2);
const separator = args.indexOf('--');
if (separator < 0 || !args[separator + 1]) {
  throw new Error('Usage: archive-task-runner.mjs --service <name> --task <name> [--cwd <path>] -- <command> [args]');
}
const option = (name, fallback) => {
  const index = args.indexOf(`--${name}`);
  return index >= 0 ? args[index + 1] ?? fallback : fallback;
};
const service = option('service', 'Archive-World');
const task = option('task', 'unspecified');
const cwd = resolve(repositoryRoot, option('cwd', '.'));
const command = args.slice(separator + 1);
const started = Date.now();
const git = spawnSync('git', ['rev-parse', '--short', 'HEAD'], { cwd, encoding: 'utf8', shell: process.platform === 'win32' });
const detectedCommit = git.status === 0 ? git.stdout.trim() : 'none';
let finished = false;

function finish(error) {
  if (finished) return;
  finished = true;
  const result = option('result', error ? 'FAIL' : 'PASS');
  const elapsed = `${((Date.now() - started) / 1000).toFixed(1)}s`;
  const notifier = resolve(import.meta.dirname, 'archive-task-notify.mjs');
  const tests = option('tests', 'NOT_RUN');
  const build = option('build', 'NOT_RUN');
  const commit = option('commit', detectedCommit);
  const blocker = error ? String(error.message).replace(/\s+/g, '_').slice(0, 160) : option('blocker', 'none');
  const notifyArgs = [notifier, '--service', service, '--task', task, '--result', result, '--tests', tests, '--build', build, '--duration', elapsed, '--commit', commit, '--blocker', blocker];
  const reporter = spawn(process.execPath, notifyArgs, { cwd: repositoryRoot, detached: true, stdio: 'ignore' });
  reporter.unref();
  process.exitCode = error ? 1 : 0;
}

const child = spawn(command[0], command.slice(1), { cwd, stdio: 'inherit', shell: process.platform === 'win32' });
child.once('error', finish);
child.once('exit', (code, signal) => finish(code === 0 ? null : new Error(signal || `exit_${code}`)));
