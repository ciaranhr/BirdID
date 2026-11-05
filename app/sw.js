// Service worker: app shell + data precached; silhouettes and photos cached as viewed;
// iNaturalist API network-first with cache fallback (for patchy reception in the field).
const VERSION = 'dev'; // replaced with the commit hash at deploy time (tools/stamp_version.py)
const SHELL = `shell-${VERSION}`;
// v2: images now arrive as CORS responses. The v1 cache held opaque entries, which would also be
// served (and fail) for crossorigin requests to the same URL, so it is dropped on activate.
const IMG = 'img-v2';
// Hosts without CORS headers (static.inaturalist.org) can only give opaque responses. Chrome counts
// each opaque entry as ~7 MB of quota whatever its real size, so those get a separate, small cache.
const IMG_OPAQUE = 'img-opaque-v1';
const API = 'api-v1';
const IMG_MAX = 600, IMG_OPAQUE_MAX = 40, API_MAX = 150;
const CACHES = [SHELL, IMG, IMG_OPAQUE, API];
const IMAGE_HOSTS = ['images.phylopic.org', 'inaturalist-open-data.s3.amazonaws.com', 'static.inaturalist.org'];
const SHELL_FILES = [
  './', 'index.html', 'styles.css', 'app.js', 'lib.js', 'manifest.webmanifest',
  'data/species.json', 'data/groups.json',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png',
];

self.addEventListener('install', (e) => {
  // cache: 'reload' bypasses the HTTP cache so a new VERSION never precaches stale files
  e.waitUntil(caches.open(SHELL)
    .then((c) => c.addAll(SHELL_FILES.map((f) => new Request(f, { cache: 'reload' }))))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (!CACHES.includes(k)) await caches.delete(k);
    await self.clients.claim();
  })());
});

async function trim(name, max) {
  const c = await caches.open(name);
  const keys = await c.keys();
  for (let i = 0; i < keys.length - max; i++) await c.delete(keys[i]);
}

/** Store and trim; never throws (a full quota just means that response isn't cached). */
async function store(name, max, req, res) {
  try {
    const c = await caches.open(name);
    await c.put(req, res);
    if (max) await trim(name, max);
  } catch (err) {
    console.warn('[sw] cache put failed', name, req.url, err);
  }
}

/** Where an image response should be cached, or null to not cache it. */
function imageCacheFor(res) {
  if (res.type === 'opaque') return [IMG_OPAQUE, IMG_OPAQUE_MAX];
  if (res.ok) return [IMG, IMG_MAX];
  return null;
}

async function cachedImage(e, req) {
  // the same URL may be in either cache; a CORS request must not be answered with an opaque entry
  const hit = req.mode === 'cors'
    ? await (await caches.open(IMG)).match(req)
    : await caches.match(req, { cacheName: IMG }) || await caches.match(req, { cacheName: IMG_OPAQUE });
  if (hit) return hit;
  const res = await fetch(req);
  const where = imageCacheFor(res);
  if (where) e.waitUntil(store(where[0], where[1], req, res.clone()));
  return res;
}

async function networkFirstApi(e, req) {
  try {
    const res = await fetch(req);
    if (res.ok) e.waitUntil(store(API, API_MAX, req, res.clone()));
    return res;
  } catch (err) {
    const hit = await (await caches.open(API)).match(req);
    if (hit) return hit;
    throw err;
  }
}

async function staleWhileRevalidate(e, req) {
  const c = await caches.open(SHELL);
  const hit = await c.match(req, { ignoreSearch: true });
  const net = fetch(req).then((res) => {
    if (res.ok) e.waitUntil(store(SHELL, 0, req, res.clone()));
    return res;
  });
  if (hit) {
    e.waitUntil(net.catch(() => {}));
    return hit;
  }
  return net;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (IMAGE_HOSTS.includes(url.hostname)) e.respondWith(cachedImage(e, req));
  else if (url.hostname === 'api.inaturalist.org') e.respondWith(networkFirstApi(e, req));
  else if (url.origin === self.location.origin) e.respondWith(staleWhileRevalidate(e, req));
});
