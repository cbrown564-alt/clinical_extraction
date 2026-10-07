import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';

// Exercise the packaged Worker, including route handling and private assets.
const port = 3214;
const base = `http://localhost:${port}`;
const server = spawn('npm', ['run', 'start:vinext', '--', '--port', String(port), '--mode', 'migration-preview'], {
  env: { ...process.env, NEXT_PUBLIC_DEMO_SURFACE: '1', CF_MIGRATION_MODE: 'migration-preview' },
  stdio: 'ignore', detached: process.platform !== 'win32',
});
const request = (route, body) => fetch(base + route, body === undefined ? {} : {
  method: 'POST', headers: { 'Content-Type': 'application/json', Origin: base }, body: JSON.stringify(body),
});
try {
  let ready = false;
  for (let i = 0; i < 60; i++) {
    if (server.exitCode !== null) throw new Error(`Worker preview exited ${server.exitCode}`);
    try { ready = (await request('/api/registry')).ok; } catch { /* starting */ }
    if (ready) break;
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  assert(ready, 'Packaged Worker did not start');
  for (const route of ['/demo', '/workbench', '/longitudinal', '/semantic-support-review']) {
    const response = await request(route);
    assert.equal(response.status, 200, route);
    assert.match(response.headers.get('X-Robots-Tag') ?? '', /noindex/, route);
  }
  for (const route of ['/mock-data/registry.json', '/.vite/manifest.json', '/not-a-page', '/_saved-api/api/paper/gan/dev750/gan_llm_only/gemini37flash/scored']) {
    assert.equal((await request(route)).status, 404, route);
  }
  const panel = await request('/api/paper/gan/dev750');
  assert.equal(panel.status, 200);
  assert.deepEqual(await panel.json(), JSON.parse(readFileSync('../results/letter-benchmarks/gan/dev750_panel.json', 'utf8')));
  for (const route of ['/api/paper/gan/dev750/gan_llm_only/gemini37flash/scored', '/api/paper/exect/dev140/llm_select/gemini37flash/scored']) {
    const response = await request(route);
    assert.equal(response.status, 200, route);
    assert.deepEqual(await response.json(), JSON.parse(readFileSync('.cloudflare/output/v0/workers/default/assets/_saved-api' + route, 'utf8')));
  }
  const frame = await request('/longitudinal/data');
  assert.equal(frame.status, 200);
  const data = await frame.json();
  assert(data.selected.documents.length > 0, 'Authored synthetic frame missing');
  assert.equal(data.selected.provenance.attempt?.raw_capture, undefined);
  assert.equal((await request('/longitudinal/data?patient=invalid')).status, 400);
  assert.equal((await request('/api/run/note', { source_row_index: 16021 })).status, 200, 'POST body must survive Worker routing');
  const replay = await request('/demo/replay', { id: 16021 });
  assert.equal(replay.status, 503);
  assert.match((await replay.json()).error, /saved decision is available/);
  console.log('Packaged Worker pages, public APIs, private assets, POST body and saved-decision recovery passed');
} finally {
  if (process.platform === 'win32') server.kill();
  else try { process.kill(-server.pid, 'SIGTERM'); } catch { /* already stopped */ }
}
