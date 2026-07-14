import { spawn } from 'node:child_process';

export function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    // Windows command shims in node_modules/.bin are .cmd files and cannot be
    // executed by CreateProcess directly. Node's shell handling resolves them.
    const shell = options.shell ?? (process.platform === 'win32' && /\.(cmd|bat)$/i.test(command));
    const child = spawn(command, args, { stdio: 'inherit', shell, ...options });
    child.on('error', (error) => reject(new Error(`Could not start ${command}: ${error.message}`)));
    child.on('exit', (code, signal) => {
      if (code === 0) resolve();
      else reject(new Error(`${command} failed (${signal ? `signal ${signal}` : `exit ${code}`}).`));
    });
  });
}
