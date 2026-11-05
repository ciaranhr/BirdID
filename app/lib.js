// Pure helpers shared by app.js (and imported directly by the test suite). No DOM access here.

export const WINGSPAN_FACTOR = 2.2; // flight-pose silhouettes: longest side ~ wingspan ~ 2.2 x body length

// Image hosts that send `Access-Control-Allow-Origin: *`. Loading these with crossorigin="anonymous"
// gives the service worker a readable CORS response instead of an opaque one (Chrome counts every
// opaque cache entry as ~7 MB against the storage quota). static.inaturalist.org (all-rights-reserved
// photos) sends no CORS headers, so it must NOT get crossorigin or the image fails to load.
export const CORS_IMAGE_HOSTS = ['inaturalist-open-data.s3.amazonaws.com', 'images.phylopic.org'];

export function isCorsImage(url) {
  try {
    return CORS_IMAGE_HOSTS.includes(new URL(url).hostname);
  } catch {
    return false;
  }
}

export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export const norm = (s) => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
export const photoSize = (url, size) => (url || '').replace(/\/(square|small|medium|thumb)\./, `/${size}.`);
export const fmtLen = (s) => (s.len ? `${s.lenMin && s.lenMax && s.lenMin !== s.lenMax ? `${s.lenMin}–${s.lenMax}` : s.len} cm` : '—');
export const fmtMass = (g) => (!g ? '—' : g >= 1000 ? `${(g / 1000).toFixed(g >= 10000 ? 0 : 1)} kg` : `${g < 20 ? g.toFixed(1).replace(/\.0$/, '') : Math.round(g)} g`);
export const genus = (s) => s.sci.split(' ')[0];
/** iNaturalist names hybrids 'Genus a × b' (or 'Genus a × Other b'). */
export const isHybrid = (s) => s.sci.includes('×');

/** `<img>` markup; adds crossorigin only for hosts that support it. */
export function imgTag(url, attrs = 'alt="" loading="lazy"') {
  return `<img src="${esc(url)}"${isCorsImage(url) ? ' crossorigin="anonymous"' : ''} ${attrs}>`;
}

/** Set an <img>/Image element's src, with crossOrigin matching the host. */
export function setImgSrc(el, url) {
  if (isCorsImage(url)) el.crossOrigin = 'anonymous';
  else el.removeAttribute('crossorigin');
  el.src = url;
}

/** Adds the lowercase search keys (_c common, _s scientific, _f family) used by search(). */
export function indexSpecies(s) {
  s._c = norm(s.common); s._s = norm(s.sci); s._f = norm(`${s.familyCommon || ''} ${s.family || ''}`);
  return s;
}

/** Rank species by match quality, then by number of observations. */
export function search(species, q, limit = 40) {
  q = norm(q);
  if (!q) return [];
  const words = q.split(' ');
  const out = [];
  for (const s of species) {
    let sc = 0;
    if (s._c.startsWith(q)) sc = 5;
    else if (s._c.split(' ').some((w) => w.startsWith(q))) sc = 4;
    else if (words.every((w) => s._c.includes(w))) sc = 3;
    else if (s._s.includes(q)) sc = 2;
    else if (words.every((w) => s._f.includes(w))) sc = 1;
    if (sc) out.push([sc, s]);
  }
  return out.sort((a, b) => b[0] - a[0] || b[1].obs - a[1].obs).slice(0, limit).map((x) => x[1]);
}

/** Drawn size of a silhouette at k px/cm; flight poses are scaled to approximate wingspan. */
export function silDims(s, k) {
  const flight = s.sil?.pose === 'flight';
  const longest = (flight ? s.len * WINGSPAN_FACTOR : s.len) * k;
  if (!s.sil) return { w: longest * 0.8, h: longest * 0.8, flight };
  const { w, h } = s.sil;
  return w >= h ? { w: longest, h: longest * h / w, flight } : { w: longest * w / h, h: longest, flight };
}

/** Up to `below` benchmark birds no longer than `len` and `above` longer ones. */
export function nearestBenchmarks(bench, len, excludeId, below = 2, above = 2) {
  const b = bench.filter((s) => s && s.id !== excludeId).sort((a, c) => a.len - c.len);
  const lo = b.filter((s) => s.len <= len).slice(-below);
  const hi = b.filter((s) => s.len > len).slice(0, above);
  return [...lo, ...hi];
}
