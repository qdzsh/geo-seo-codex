#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const packageRoot = path.resolve(__dirname, '..');

function run(command, args) {
  const result = spawnSync(command, args, {
    cwd: packageRoot,
    stdio: 'inherit',
    shell: false,
  });

  if (result.error) {
    console.error(`Failed to run ${command}: ${result.error.message}`);
    return 1;
  }

  return result.status ?? 1;
}

let exitCode;
if (process.platform === 'win32') {
  exitCode = run('pwsh', [
    '-NoLogo',
    '-NoProfile',
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    path.join(packageRoot, 'install.ps1'),
  ]);
} else {
  exitCode = run('bash', [path.join(packageRoot, 'install.sh')]);
}

process.exit(exitCode);
