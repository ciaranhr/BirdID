// Service worker: app shell + data precached; silhouettes and photos cached as viewed;
// iNaturalist API network-first with cache fallback (for patchy reception in the field).
const VERSION = 'v1';
const SHELL = `shell-${VERSION}`, IMG = 'img-v1', API = 'api-v1';
const IMG_MAX = 600, API_MAX = 150;
const SHELL_FILES = [
  './', 'index.html', 'styles.css', 'app.js', 'manifest.webmanifest',
  'data/species.json', 'data/groups.json',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (![SHELL, IMG, API].includes(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

async function trim(name, max) {
  const c = await caches.open(name);
  const keys = await c.keys();
  for (let i = 0; i < keys.length - max; i++) await c.delete(keys[i]);
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // images: phylopic silhouettes, iNat photos -> cache-first
  if (url.hostname === 'images.phylopic.org' || url.hostname.endsWith('inaturalist-open-data.s3.amazonaws.com') ||
      url.hostname === 'static.inaturalist.org') {
    e.respondWith((async () => {
      const c = await caches.open(IMG);
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok || res.type === 'opaque') { c.put(req, res.clone()); trim(IMG, IMG_MAX); }
      return res;
    })());
    return;
  }

  // iNat API -> network-first, fall back to last cached response
  if (url.hostname === 'api.inaturalist.org') {
    e.respondWith((async () => {
      const c = await caches.open(API);
      try {
        const res = await fetch(req);
        if (res.ok) { c.put(req, res.clone()); trim(API, API_MAX); }
        return res;
      } catch (err) {
        const hit = await c.match(req);
        if (hit) return hit;
        throw err;
      }
    })());
    return;
  }

  // same-origin app files -> stale-while-revalidate
  if (url.origin === self.location.origin) {
    e.respondWith((async () => {
      const c = await caches.open(SHELL);
      const hit = await c.match(req, { ignoreSearch: true });
      const net = fetch(req).then((res) => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    })());
  }
});
