const CACHE = 'aventura-letras-v1';
self.addEventListener('install', event => event.waitUntil((async () => {
  const cache = await caches.open(CACHE);
  const content = await fetch('/content/words.json');
  if (!content.ok) throw new Error('Conteúdo indisponível');
  const words = await content.json();
  await cache.addAll(['/', '/index.html', '/src/style.css', '/src/app.js', '/src/game.js', '/manifest.webmanifest', '/icons/icon.svg', '/content/words.json', ...words.map(w => w.image)]);
  await self.skipWaiting();
})()));
self.addEventListener('activate', event => event.waitUntil((async () => {
  for (const key of await caches.keys()) if (key !== CACHE) await caches.delete(key);
  await self.clients.claim();
})()));
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(fetch(event.request).catch(async () => (await caches.match(event.request)) || new Response('Disponível após a primeira visita online.', {status:503})));
});
