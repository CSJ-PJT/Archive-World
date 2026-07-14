#!/usr/bin/env node
/**
 * Best-effort Archive task notification. Credentials are read from the
 * process environment or the sibling ArchiveOS local .env file only.
 * No credential is logged, and notification failures never fail the task.
 */
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const workspaceRoot = resolve(import.meta.dirname, '..', '..');
const args = process.argv.slice(2);
const value = (name, fallback = null) => {
  const index = args.indexOf(`--${name}`);
  return index >= 0 ? args[index + 1] ?? fallback : fallback;
};
const redact = (text) => String(text ?? '')
  .replace(/https?:\/\/[^\s]+/gi, '[redacted-url]')
  .replace(/[A-Za-z0-9_-]{20,}/g, '[redacted]');
const env = { ...process.env };
const envFile = resolve(workspaceRoot, 'ArchiveOS', '.env');
if (existsSync(envFile)) {
  for (const line of readFileSync(envFile, 'utf8').split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (match && env[match[1]] === undefined) env[match[1]] = match[2].replace(/^['"]|['"]$/g, '');
  }
}

const notification = {
  service: value('service', 'Archive'),
  task: value('task', 'unspecified'),
  result: value('result', 'FAIL'),
  tests: value('tests', 'NOT_RUN'),
  build: value('build', 'NOT_RUN'),
  duration: value('duration', 'unknown'),
  commit: value('commit', 'none'),
  blocker: value('blocker', 'none'),
};
const text = [
  `*Archive task completed* — ${notification.result === 'PASS' ? 'PASS' : 'FAIL'}`,
  `- Service: ${notification.service}`,
  `- Task: ${notification.task}`,
  `- Tests: ${notification.tests}`,
  `- Build: ${notification.build}`,
  `- Duration: ${notification.duration}`,
  `- Commit: ${notification.commit}`,
  `- Blocker: ${notification.blocker}`,
].join('\n');

async function send() {
  const { SLACK_WEBHOOK_URL: webhook, SLACK_BOT_TOKEN: token, SLACK_CHANNEL: channel } = env;
  if (token && channel) {
    const response = await fetch('https://slack.com/api/chat.postMessage', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify({ channel, text }),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok || body.ok !== true) throw new Error(`slack_api_${response.status || 'error'}`);
    return 'sent:bot-token';
  }
  if (webhook) {
    const response = await fetch(webhook, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }),
    });
    if (!response.ok) throw new Error(`slack_webhook_${response.status}`);
    return 'sent:webhook';
  }
  return 'skipped:not-configured';
}

send().then((status) => console.log(`ARCHIVE_SLACK_NOTIFY=${status}`)).catch((error) => {
  console.warn(`ARCHIVE_SLACK_NOTIFY=isolated-failure:${redact(error.message)}`);
  process.exitCode = 0;
});
