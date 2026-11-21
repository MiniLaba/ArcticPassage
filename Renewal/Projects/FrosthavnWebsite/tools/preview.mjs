import http from 'node:http';
import { readFile, stat, realpath } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { spawn } from 'node:child_process';

const root = await realpath(fileURLToPath(new URL('../dist/', import.meta.url)));
const identity = 'FrosthavnWebsite-1.0.0';
const mime = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.svg':'image/svg+xml', '.png':'image/png', '.webp':'image/webp', '.jpg':'image/jpeg', '.woff2':'font/woff2', '.txt':'text/plain; charset=utf-8' };
const server = http.createServer(async (req, res) => {
  try {
    if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405); res.end(); return; }
    const url = new URL(req.url ?? '/', 'http://127.0.0.1');
    if (url.pathname === '/_frosthavn_preview_health') { res.writeHead(200, {'Content-Type':'text/plain'}); res.end(identity); return; }
    let filename = path.resolve(root, '.' + decodeURIComponent(url.pathname));
    if (filename !== root && !filename.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
    if ((await stat(filename)).isDirectory()) filename = path.join(filename, 'index.html');
    filename = await realpath(filename);
    if (!filename.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
    const body = await readFile(filename);
    res.writeHead(200, {'Content-Type':mime[path.extname(filename)] ?? 'application/octet-stream','Content-Length':body.length,'X-Content-Type-Options':'nosniff','Cache-Control':'no-cache'});
    res.end(req.method === 'HEAD' ? undefined : body);
  } catch { res.writeHead(404); res.end('Not found'); }
});
const open = url => { if (!process.argv.includes('--no-open')) spawn('open', [url], {stdio:'ignore'}).unref(); };
const listen = port => new Promise((resolve, reject) => { server.once('error', reject); server.listen(port, '127.0.0.1', () => {server.removeListener('error', reject); resolve();}); });
try { await listen(4175); }
catch (error) {
  if (error.code !== 'EADDRINUSE') throw error;
  const existing = await fetch('http://127.0.0.1:4175/_frosthavn_preview_health').then(r=>r.text()).catch(()=>null);
  if (existing === identity) { open('http://127.0.0.1:4175/'); console.log('霜灯港官网预览已在运行。'); process.exit(0); }
  await listen(0);
}
const url = `http://127.0.0.1:${server.address().port}/`;
console.log(`霜灯港官网：${url}\n这是本机预览，关闭此窗口即可停止。`);
open(url);
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => server.close(()=>process.exit(0)));
