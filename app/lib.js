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

/**
 * Comparator: species recorded locally first (most local records first), then most observed
 * Australia-wide. `local` is a Map(taxonId -> local count) or null when no location is set.
 */
export const byLocalThenObs = (local) => (a, b) =>
  (local ? (local.get(b.id) || 0) - (local.get(a.id) || 0) : 0) || b.obs - a.obs;

/** Rank species by match quality, then local records (if a location is set), then observations. */
export function search(species, q, limit = 40, local = null) {
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
  const tie = byLocalThenObs(local);
  return out.sort((a, b) => b[0] - a[0] || tie(a[1], b[1])).slice(0, limit).map((x) => x[1]);
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

export const LIST_SORTS = [
  { key: 'family', label: 'Family' },
  { key: 'common', label: 'Common name' },
  { key: 'sci', label: 'Scientific name' },
];

const cmpText = (a, b) => a.localeCompare(b, 'en', { sensitivity: 'base' });

/**
 * The species list: non-hybrid species matching `q` (common, scientific or family name), optionally
 * only those recorded locally, as sections [{ title, sub, items }]. Family sort gives one section per
 * family (by family common name, birds A-Z within it); the other sorts give a single flat section.
 */
export function speciesList(species, { q = '', sort = 'family', local = null, nearOnly = false } = {}) {
  const words = norm(q).split(' ').filter(Boolean);
  const items = species.filter((s) => !isHybrid(s)
    && (!nearOnly || !local || local.has(s.id))
    && words.every((w) => s._c.includes(w) || s._s.includes(w) || s._f.includes(w)));
  if (sort === 'sci') return [{ title: '', items: items.sort((a, b) => cmpText(a.sci, b.sci)) }];
  if (sort === 'common') return [{ title: '', items: items.sort((a, b) => cmpText(a.common, b.common)) }];
  const fams = new Map();
  for (const s of items) {
    if (!fams.has(s.family)) fams.set(s.family, { title: s.familyCommon || s.family || 'Other', sub: s.family || '', items: [] });
    fams.get(s.family).items.push(s);
  }
  const out = [...fams.values()].sort((a, b) => cmpText(a.title, b.title));
  out.forEach((f) => f.items.sort((a, b) => cmpText(a.common, b.common)));
  return out;
}

// ---------- dichotomous ID key (data/marks.json) ----------

/**
 * Key entries for `species`: one per species, or one per plumage ("Superb Fairywren (female)") for
 * birds whose sexes/ages differ. Species without marks are left out.
 * -> [{ s, label, plumage, t: {trait: value}, ok }]
 */
export function markLeaves(species, marks) {
  const out = [];
  for (const s of species) {
    const m = marks[s.id];
    if (!m) continue;
    const pl = Object.entries(m.p || {});
    if (!pl.length) out.push({ s, label: s.common, plumage: '', t: { ...m.t }, ok: !!m.ok });
    for (const [p, t] of pl) out.push({ s, label: `${s.common} (${p})`, plumage: p, t: { ...m.t, ...t }, ok: !!m.ok });
  }
  return out;
}

const normVal = (v) => String(v).trim().toLowerCase();
const known = (v) => v != null && String(v).trim() !== '';

/** Body lengths only split a set when the gap between two sizes is at least this ratio. */
export const SIZE_GAP = 1.3;

/** A 'size' value function for these leaves (split at the widest clear length gap), or null. */
export function sizeSplit(leaves) {
  const lens = [...new Set(leaves.map((l) => l.s.len).filter(Boolean))].sort((a, b) => a - b);
  let best = null;
  for (let i = 1; i < lens.length; i++) {
    const r = lens[i] / lens[i - 1];
    if (r >= SIZE_GAP && (!best || r > best.r)) best = { r, lo: lens[i - 1], hi: lens[i] };
  }
  if (!best) return null;
  return (l) => (!l.s.len ? undefined : l.s.len <= best.lo ? `smaller (up to ${best.lo} cm)` : `larger (${best.hi} cm or more)`);
}

/**
 * A key over `leaves`: { leaves } at a tip, or { trait: {key, label}, branches: [{ value, unknown, node }] }.
 * At each step it picks the trait whose largest branch is smallest (the most even split), preferring
 * traits every leaf has, then visible marks over shape/behaviour over call/range. Leaves with no
 * value for the chosen trait go down every branch (listed in `unknown`). Every branch is smaller
 * than its parent, so the recursion ends; a tip with 2+ leaves means the marks can't separate them.
 */
export function buildKey(leaves, traits) {
  if (leaves.length < 2) return { leaves };
  const fns = traits.map((tr) => ({ key: tr.key, label: tr.label, tier: tr.tier || 0, val: (l) => l.t[tr.key] }));
  const size = sizeSplit(leaves);
  if (size) fns.push({ key: 'size', label: 'Size', tier: 1, val: size });
  let best = null;
  fns.forEach((tr, i) => {
    const groups = new Map(), unknown = [];
    for (const l of leaves) {
      const v = tr.val(l);
      if (!known(v)) { unknown.push(l); continue; }
      const k = normVal(v);
      if (!groups.has(k)) groups.set(k, { value: String(v).trim(), leaves: [] });
      groups.get(k).leaves.push(l);
    }
    if (groups.size < 2) return;
    const branches = [...groups.values()].map((b) => ({ value: b.value, leaves: [...b.leaves, ...unknown], unknown }));
    const maxB = Math.max(...branches.map((b) => b.leaves.length));
    if (maxB >= leaves.length) return;
    const cost = maxB + 0.6 * tr.tier + 1.5 * unknown.length;
    if (!best || cost < best.cost - 1e-9) best = { cost, tr, branches };
  });
  if (!best) return { leaves };
  return {
    trait: { key: best.tr.key, label: best.tr.label },
    branches: best.branches.map((b) => ({ value: b.value, unknown: b.unknown, node: buildKey(b.leaves, traits) })),
  };
}

/**
 * Side-by-side rows for `leaves`: every trait at least one of them has, as
 * [{ key, label, cells: [value|null], differs }], rows that tell them apart first.
 */
export function compareRows(leaves, traits) {
  const rows = [];
  for (const tr of traits) {
    const cells = leaves.map((l) => (known(l.t[tr.key]) ? String(l.t[tr.key]).trim() : null));
    if (!cells.some(Boolean)) continue;
    rows.push({ key: tr.key, label: tr.label, cells, differs: new Set(cells.filter(Boolean).map(normVal)).size > 1 });
  }
  return rows.sort((a, b) => b.differs - a.differs);
}
