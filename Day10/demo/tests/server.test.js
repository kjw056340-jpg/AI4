import { before, after, test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { fileURLToPath } from 'node:url';

let server, baseURL;
before(async () => {
  server = spawn(process.execPath, ['server.js'], {
    cwd: fileURLToPath(new URL('../', import.meta.url)),
    env: { ...process.env, PORT: '0' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  baseURL = await new Promise((resolve, reject) => {
    let output = '';
    const timer = setTimeout(() => reject(new Error('Preview server did not start')), 10000);
    server.once('error', error => { clearTimeout(timer); reject(error); });
    server.once('exit', code => { clearTimeout(timer); reject(new Error(`Preview server exited: ${code}`)); });
    server.stdout.on('data', chunk => {
      output += chunk;
      const match = output.match(/http:\/\/localhost:(\d+)/);
      if (match) { clearTimeout(timer); resolve(`http://127.0.0.1:${match[1]}/`); }
    });
  });
});
after(async () => {
  if (server && server.exitCode === null && !server.killed) {
    const exit = once(server, 'exit');
    server.kill();
    await exit;
  }
});

test('home returns the app shell, Korean encoding and browser security header', async () => {
  const response = await fetch(baseURL);
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /text\/html; charset=utf-8/);
  assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
  assert.match(await response.text(), /note-demo — 생각이 모이는 곳/);
});
test('all locally referenced assets resolve at both a domain root and Pages project path', async () => {
  const html = await (await fetch(baseURL)).text();
  const references = [...html.matchAll(/(?:src|href)="([^"#]+)"/g)].map(m => m[1]).filter(value => !value.startsWith('data:'));
  assert.deepEqual(references.sort(), ['./app.js', './style.css']);
  for (const reference of references) {
    const rootURL = new URL(reference, baseURL);
    const projectURL = new URL(reference, new URL('note-demo/', baseURL));
    assert.ok(projectURL.pathname.startsWith('/note-demo/'), 'Asset must remain under the Pages project path');
    const response = await fetch(rootURL);
    assert.equal(response.status, 200);
    assert.ok((await response.text()).length > 0);
  }
});
test('JavaScript modules and CSS have browser-compatible MIME types', async () => {
  for (const [file, mime] of [['app.js', 'text/javascript'], ['model.js', 'text/javascript'], ['style.css', 'text/css']]) {
    const response = await fetch(new URL(file, baseURL));
    assert.equal(response.status, 200);
    assert.ok(response.headers.get('content-type').startsWith(mime));
  }
});
test('missing resources and private project files cannot be served', async () => {
  for (const file of ['missing.html', 'package.json', 'schema.sql', 'README.md']) {
    assert.equal((await fetch(new URL(file, baseURL))).status, 404);
  }
});
test('encoded path traversal cannot escape public directory', async () => {
  const response = await fetch(baseURL + '%2e%2e%2fschema.sql');
  assert.equal(response.status, 403);
});
test('malformed URL encoding does not crash the server', async () => {
  assert.equal((await fetch(baseURL + '%ZZ')).status, 404);
  assert.equal((await fetch(baseURL)).status, 200);
});
