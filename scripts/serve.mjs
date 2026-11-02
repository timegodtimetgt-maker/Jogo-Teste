import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
const args = process.argv.slice(2);
const production = args.includes('--dist');
const root = path.resolve(production ? 'dist' : '.');
const types = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.mjs':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.json':'application/json; charset=utf-8', '.svg':'image/svg+xml', '.png':'image/png', '.webmanifest':'application/manifest+json', '.apk':'application/vnd.android.package-archive' };
const port = Number(process.env.PORT || 5173);
http.createServer(async (req,res) => {
  try {
    const urlPath = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (urlPath.split('/').includes('..') || urlPath.split('/').some(s => s.startsWith('.'))) throw new Error('path');
    const relative = urlPath === '/' ? 'index.html' : urlPath.slice(1);
    let target = path.resolve(root, relative);
    // Serve only app files; never expose checkout metadata or Android source.
    if (!['index.html','sw.js','manifest.webmanifest'].includes(relative) && !/^(src|images|content|icons)\//.test(relative)) throw new Error('path');
    if (!production && /^(images|content|icons)\//.test(relative)) target = path.resolve(root, 'public', relative);
    if (!production && ['sw.js','manifest.webmanifest'].includes(relative)) target = path.resolve(root,'public',relative);
    if (!(await stat(target)).isFile()) throw new Error('file');
    res.writeHead(200, { 'Content-Type': types[path.extname(target)] || 'application/octet-stream', 'Cache-Control':'no-cache', 'X-Content-Type-Options':'nosniff' });
    res.end(await readFile(target));
  } catch { res.writeHead(404, {'Content-Type':'text/plain; charset=utf-8'}); res.end('Arquivo não encontrado'); }
}).listen(port, '0.0.0.0', () => console.log(`Aventura das Letras: porta ${port} (${production ? 'produção' : 'desenvolvimento'})`));
