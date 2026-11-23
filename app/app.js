// BirdID Shapes - size ladders, silhouettes, real-world photos and confusion-pair comparisons.
// Vanilla JS, no build step. Data: data/species.json + data/groups.json (built by tools/build_data.py),
// live photos from the iNaturalist API. Pure helpers live in lib.js.

import {
  WINGSPAN_FACTOR, esc, photoSize, fmtLen, fmtMass, genus, isHybrid, imgTag, setImgSrc,
  indexSpecies, search as searchIn, silDims, nearestBenchmarks as nearestIn,
  byLocalThenObs, speciesList, LIST_SORTS, markLeaves, buildKey, compareRows,
} from './lib.js';
import {
  REGIONS, RADII, DEFAULT_RADIUS, loadLocation, saveLocation, validLocation, locationLabel,
  localCounts, currentPosition,
} from './location.js';

const INAT = 'https://api.inaturalist.org/v1';
const PLACE_AU = 6744;
const COLORS = ['var(--c0)', 'var(--c1)', 'var(--c2)', 'var(--c3)', 'var(--c4)'];
const MAX_COMPARE = 5;
const LADDER_H = 170;        // px height of the tallest silhouette

const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'adult', label: 'Adult', q: { term_id: 1, term_value_id: 2 } },
  { key: 'juvenile', label: 'Juvenile', q: { term_id: 1, term_value_id: 8 } },
  { key: 'male', label: 'Male', q: { term_id: 9, term_value_id: 11 } },
  { key: 'female', label: 'Female', q: { term_id: 9, term_value_id: 10 } },
];
const ORDERS = [
  { key: 'votes', label: 'Best photos' },
  { key: 'created_at', label: 'Recent (typical views)' },
];
const ANNOT = { 2: 'adult', 8: 'juvenile', 10: 'female', 11: 'male' };

let SPECIES = [], BYID = new Map(), GROUPS = [], BENCH = [];
let MARKS = {}, TRAITS = []; // field marks for the ID key: {taxonId: {t, p?, ok}}, [{key, label, tier}]
const view = document.getElementById('view');

// ---------- location ("species near me") ----------
// LOC: the saved location or null; LOCAL: Map(taxonId -> research-grade records there) once loaded.
let LOC = loadLocation();
let LOCAL = null;
const local = { status: LOC ? 'loading' : 'off', stale: false, error: '', req: 0 };
const localListeners = new Set(); // per-view updaters; cleared on every route change

/** "within 50 km of you" / "in Tasmania" */
const locIn = (loc) => (loc.kind === 'gps' ? locationLabel(loc) : `in ${loc.name}`);

async function loadLocal() {
  const req = ++local.req;
  LOCAL = null;
  Object.assign(local, { status: LOC ? 'loading' : 'off', stale: false, error: '' });
  notifyLocal();
  if (!LOC) return;
  try {
    const r = await localCounts(LOC, getJSON);
    if (req !== local.req) return; // the location changed meanwhile
    LOCAL = r.counts;
    Object.assign(local, { status: 'ready', stale: r.stale });
  } catch (e) {
    if (req !== local.req) return;
    Object.assign(local, { status: 'error', error: e.message });
  }
  notifyLocal();
}

function setLocation(loc) {
  LOC = validLocation(loc);
  saveLocation(LOC);
  loadLocal();
}

function locBarInner() {
  const label = LOC ? locationLabel(LOC) : 'All of Australia';
  const status = local.status === 'loading' ? 'Loading local records…'
    : local.status === 'error' ? `Couldn't load local records (${esc(local.error)}) <button type="button" class="link-btn" data-loc-retry>Retry</button>`
    : local.status === 'ready' ? `${localListedCount().toLocaleString()} species recorded${local.stale ? ' · saved copy' : ''}`
    : 'Set a location to see what’s around you';
  return `<a class="locbar-main" href="#/location"><span class="pin" aria-hidden="true">📍</span>
      <b>${esc(label.charAt(0).toUpperCase() + label.slice(1))}</b><span class="change">Change</span></a>
    <div class="muted small locbar-status" role="status">${status}</div>`;
}
/** Local species the app can show (iNaturalist also counts hybrids and birds added since the data build). */
const localListedCount = () => SPECIES.filter((s) => !isHybrid(s) && LOCAL.has(s.id)).length;
const locBar = () => `<div class="locbar" data-locbar>${locBarInner()}</div>`;

function notifyLocal() {
  document.querySelectorAll('[data-locbar]').forEach((el) => { el.innerHTML = locBarInner(); });
  localListeners.forEach((fn) => fn());
}
document.addEventListener('click', (e) => { if (e.target.closest('[data-loc-retry]')) loadLocal(); });

// ---------- utils ----------
async function getJSON(url, tries = 3) {
  for (let i = 0; i < tries; i++) {
    const r = await fetch(url);
    if (r.ok) return r.json();
    if (r.status === 429 || r.status >= 500) { await new Promise((ok) => setTimeout(ok, 1200 * (i + 1))); continue; }
    throw new Error(`HTTP ${r.status}`);
  }
  throw new Error('iNaturalist is busy - try again in a moment');
}

// ---------- search ----------
const search = (q, limit) => searchIn(SPECIES, q, limit, LOCAL);
const popular = (n = 25) => SPECIES.filter((s) => !isHybrid(s)).sort(byLocalThenObs(LOCAL)).slice(0, n);

/** A species row: a link (to `href` + id) or, with tag 'button', a picker choice. `note` is extra muted text. */
function resultItem(s, tag = 'a', { href = '#/s/', note = '' } = {}) {
  const img = s.photo ? imgTag(s.photo) : '<span class="thumb"></span>';
  const n = LOCAL?.get(s.id);
  const near = n ? ` · <span class="nearby">nearby${tag === 'a' ? ` (${n.toLocaleString()})` : ''}</span>` : '';
  const key = tag === 'a' && MARKS[s.id] ? '<span class="keybadge" title="Has an ID key">ID key</span>' : '';
  const inner = `${img}<span class="names"><b>${esc(s.common)}</b><i>${esc(s.sci)}${s.len ? ` · ${s.len} cm` : ''}${near}</i>${
    note ? `<i>${esc(note)}</i>` : ''}</span>${key}`;
  return tag === 'a'
    ? `<li><a href="${href}${s.id}">${inner}</a></li>`
    : `<li><button type="button" data-id="${s.id}">${inner}</button></li>`;
}

// ---------- silhouettes & size ladder ----------
function silHTML(s, w, h, color, ref) {
  if (!s.sil) return `<div class="sil missing" style="width:${w}px;height:${h}px" title="No silhouette"></div>`;
  const u = `url('${s.sil.url}')`;
  return `<div class="sil${ref ? ' ref' : ''}" role="img" aria-label="${esc(s.common)} silhouette"
    style="width:${w.toFixed(1)}px;height:${h.toFixed(1)}px;${color ? `background-color:${color};` : ''}-webkit-mask-image:${u};mask-image:${u}"></div>`;
}

/** items: [{s, color?, ref?}] - only species with a body length are drawn. */
function ladderHTML(items) {
  items = items.filter((it) => it.s.len).sort((a, b) => a.s.len - b.s.len);
  if (!items.length) return '<p class="muted small">No body-length data for these species.</p>';
  const maxH1 = Math.max(...items.map((it) => silDims(it.s, 1).h));
  let k = LADDER_H / maxH1; // px per cm
  // shrink to fit the screen width so every bird is visible without scrolling
  const avail = Math.min(view.clientWidth, 760) - 66; // minus main + card padding
  const minCol = Math.max(54, Math.min(76, Math.floor(avail / items.length)));
  const colW = (it, kk) => Math.max(silDims(it.s, kk).w + 14, minCol);
  const totalW = (kk) => items.reduce((acc, it) => acc + colW(it, kk), 0);
  if (totalW(k) > avail) { // binary-search the largest scale that fits
    let lo = 0, hi = k;
    for (let i = 0; i < 30; i++) { const mid = (lo + hi) / 2; if (totalW(mid) <= avail) lo = mid; else hi = mid; }
    k = lo || k;
  }
  const slotH = Math.ceil(Math.max(...items.map((it) => silDims(it.s, k).h))) + 6;
  let anyFlight = false;
  const rungs = items.map((it) => {
    const d = silDims(it.s, k);
    anyFlight ||= d.flight;
    return `<div class="rung" style="width:${colW(it, k).toFixed(0)}px">
      <div class="slot" style="height:${slotH}px">${silHTML(it.s, d.w, d.h, it.color, it.ref)}</div>
      <div class="rung-label"${it.ref ? ' style="opacity:.7"' : ''}>
        <b${it.color ? ` style="color:${it.color}"` : ''}>${esc(it.s.common)}</b>${fmtLen(it.s)}${d.flight ? ' · in flight' : ''}
      </div></div>`;
  }).join('');
  // a scale bar of a round number of cm, 30-160 px long
  const cm = [5, 10, 20, 50, 100].find((c) => c * k >= 30) || 100;
  const credits = [...new Map(items.filter((it) => it.s.sil).map((it) => [it.s.sil.url, it.s])).values()];
  return `<div class="ladder-wrap"><div class="ladder">${rungs}</div></div>
    <div class="scalebar"><i style="width:${(cm * k).toFixed(1)}px"></i>${cm} cm</div>
    ${anyFlight ? `<div class="legend-flight">"In flight" silhouettes are scaled to an estimated wingspan (≈${WINGSPAN_FACTOR}× body length).</div>` : ''}
    <div class="credit">Lengths are bill-tip to tail-tip (Garnett et al. 2015). Silhouettes: ${credits.map(silCredit).join('; ')}</div>`;
}

function silCredit(s) {
  const sil = s.sil;
  const lvl = sil.level === 'species' ? '' : ` (${sil.level}-level stand-in)`;
  return `<a href="https://www.phylopic.org/images/${esc(sil.uuid)}" target="_blank" rel="noopener">${esc(sil.name)}</a>${lvl} by ${esc(sil.by)}, <a href="${esc(sil.licUrl)}" target="_blank" rel="noopener">${esc(sil.lic)}</a>`;
}

const nearestBenchmarks = (len, excludeId, below, above) => nearestIn(BENCH.map((id) => BYID.get(id)), len, excludeId, below, above);

// ---------- iNaturalist gallery ----------
class Gallery {
  constructor(taxonId, filter = 'all', order = 'votes') {
    Object.assign(this, { taxonId, filter, order, items: [], page: 0, done: false, loading: false, total: null, error: null });
    this.listeners = new Set();
  }
  url() {
    const p = new URLSearchParams({
      taxon_id: this.taxonId, place_id: PLACE_AU, quality_grade: 'research', photos: 'true',
      per_page: 30, page: this.page, order_by: this.order, order: 'desc', locale: 'en-AU',
    });
    const f = FILTERS.find((x) => x.key === this.filter);
    if (f?.q) for (const [k, v] of Object.entries(f.q)) p.set(k, v);
    return `${INAT}/observations?${p}`;
  }
  async more() {
    if (this.loading || this.done) return;
    this.loading = true; this.page++; this.emit();
    try {
      const d = await getJSON(this.url());
      this.total = d.total_results;
      for (const o of d.results) {
        const ann = new Map((o.annotations || []).map((a) => [a.controlled_attribute_id, a.controlled_value_id]));
        if (ann.get(17) === 19) continue;                     // dead
        if (ann.has(22) && ann.get(22) !== 24) continue;      // feather / track / bone etc.
        const tags = [...ann.values()].map((v) => ANNOT[v]).filter(Boolean);
        for (const p of (o.photos || []).slice(0, 4)) {
          this.items.push({
            thumb: photoSize(p.url, 'medium'), large: photoSize(p.url, 'large'),
            obsId: o.id, date: o.observed_on, place: o.place_guess, attr: p.attribution, tags,
          });
        }
      }
      if (d.results.length < 30 || this.page * 30 >= d.total_results) this.done = true;
    } catch (e) {
      this.error = e.message; this.page--; this.done = true;
    }
    this.loading = false; this.emit();
  }
  retry() {
    this.error = null; this.done = false;
    this.more();
  }
  on(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }
  emit() { this.listeners.forEach((fn) => fn(this)); }
}

function filterChips(cur, order) {
  return `<div class="chips" data-filters>
    ${FILTERS.map((f) => `<button class="chip" data-filter="${f.key}" aria-pressed="${f.key === cur}">${f.label}</button>`).join('')}
  </div>
  <div class="chips" data-orders style="margin-top:.4rem">
    ${ORDERS.map((o) => `<button class="chip" data-order="${o.key}" aria-pressed="${o.key === order}">${o.label}</button>`).join('')}
  </div>`;
}

const RETRY = '<button type="button" class="link-btn" data-retry>Retry</button>';

/**
 * Shared wiring for the photo grid and the compare strips: append new thumbnails as pages arrive,
 * show status (with a Retry button after an error), and keep loading while the visible area
 * isn't full - otherwise a short first page leaves nothing to scroll and paging stalls.
 */
function wireGallery(container, gallery, label, { list, status, statusText, wantsMore }) {
  let shown = 0;
  const update = (g) => {
    for (; shown < g.items.length; shown++) {
      const it = g.items[shown];
      const b = document.createElement('button');
      b.innerHTML = imgTag(it.thumb);
      const idx = shown;
      b.onclick = () => Lightbox.open(g, idx, label);
      list.appendChild(b);
    }
    status.innerHTML = g.error ? `Couldn't load photos: ${esc(g.error)} ${RETRY}` : esc(statusText(g));
    if (!g.loading && !g.done && !g.error) {
      requestAnimationFrame(() => { if (container.isConnected && wantsMore()) gallery.more(); });
    }
  };
  status.addEventListener('click', (e) => { if (e.target.closest('[data-retry]')) gallery.retry(); });
  const off = gallery.on(update);
  update(gallery);
  gallery.more();
  return off;
}

function gridGallery(container, gallery, label) {
  container.innerHTML = '<div class="gallery"></div><div class="loading"></div><div class="sentinel"></div>';
  const sentinel = container.querySelector('.sentinel');
  const MARGIN = 600;
  const off = wireGallery(container, gallery, label, {
    list: container.querySelector('.gallery'),
    status: container.querySelector('.loading'),
    statusText: (g) => (g.loading ? 'Loading photos…'
      : !g.items.length ? 'No photos match this filter.'
      : g.done ? `${g.total?.toLocaleString()} observations` : ''),
    wantsMore: () => sentinel.getBoundingClientRect().top < innerHeight + MARGIN,
  });
  const io = new IntersectionObserver((e) => { if (e[0].isIntersecting) gallery.more(); }, { rootMargin: `${MARGIN}px` });
  io.observe(sentinel);
  return () => { off(); io.disconnect(); };
}

function stripGallery(container, gallery, label) {
  container.innerHTML = '<div class="strip"></div><div class="loading small"></div>';
  const strip = container.querySelector('.strip');
  const nearEnd = () => strip.scrollLeft + strip.clientWidth > strip.scrollWidth - 500;
  strip.addEventListener('scroll', () => { if (nearEnd()) gallery.more(); }, { passive: true });
  return wireGallery(container, gallery, label, {
    list: strip,
    status: container.querySelector('.loading'),
    statusText: (g) => (g.loading && !g.items.length ? 'Loading…' : !g.items.length && g.done ? 'No photos match this filter.' : ''),
    wantsMore: nearEnd,
  });
}

// ---------- lightbox ----------
const Lightbox = (() => {
  const el = document.getElementById('lightbox');
  const img = el.querySelector('img');
  const cap = el.querySelector('.lb-caption');
  let g = null, i = 0, label = '', off = null;
  const render = () => {
    const it = g.items[i];
    if (!it) return;
    setImgSrc(img, it.large);
    const nxt = g.items[i + 1]; if (nxt) setImgSrc(new Image(), nxt.large);
    cap.innerHTML = `<b>${esc(label)}</b> · ${esc(it.date || '')} · ${esc(it.place || '')}
      ${it.tags.length ? `<br>Tagged: ${esc(it.tags.join(', '))}` : ''}
      <br><span style="opacity:.75">${esc(it.attr)}</span> ·
      <a href="https://www.inaturalist.org/observations/${it.obsId}" target="_blank" rel="noopener">iNaturalist ↗</a>
      · ${i + 1}/${g.done ? g.items.length : `${g.items.length}+`}`;
    if (i >= g.items.length - 4) g.more();
  };
  const go = (d) => { const n = i + d; if (n >= 0 && n < g.items.length) { i = n; render(); } };
  let closing = false; // history.back() is async: a second Escape before popstate would leave the page
  const close = () => { if (!el.hidden && !closing) { closing = true; history.back(); } };
  const hide = () => { el.hidden = true; closing = false; img.src = ''; off?.(); off = null; document.body.style.overflow = ''; };
  el.querySelector('[data-close]').onclick = close;
  el.querySelector('.lb-prev').onclick = () => go(-1);
  el.querySelector('.lb-next').onclick = () => go(1);
  let x0 = null, y0 = null;
  el.addEventListener('touchstart', (e) => { if (e.touches.length === 1) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; } }, { passive: true });
  el.addEventListener('touchend', (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) go(dx < 0 ? 1 : -1);
    else if (dy > 90 && Math.abs(dy) > Math.abs(dx)) close();
    x0 = null;
  });
  document.addEventListener('keydown', (e) => {
    if (el.hidden) return;
    if (e.key === 'ArrowRight') go(1); else if (e.key === 'ArrowLeft') go(-1); else if (e.key === 'Escape') close();
  });
  window.addEventListener('popstate', () => { if (!el.hidden) hide(); });
  return {
    open(gallery, idx, lbl) {
      g = gallery; i = idx; label = lbl;
      off = g.on(() => render());
      history.pushState({ overlay: 'lb' }, '');
      el.hidden = false; document.body.style.overflow = 'hidden';
      render();
    },
  };
})();

// ---------- species picker ----------
const Picker = (() => {
  const el = document.getElementById('picker');
  const input = document.getElementById('picker-input');
  const list = document.getElementById('picker-results');
  let cb = null, exclude = new Set();
  const show = () => {
    const res = (input.value.trim() ? search(input.value) : popular()).filter((s) => !exclude.has(s.id));
    list.innerHTML = res.map((s) => resultItem(s, 'button')).join('') || '<li class="empty">No matches</li>';
  };
  input.addEventListener('input', show);
  let picked = null, closing = false;
  const close = () => { if (!el.hidden && !closing) { closing = true; history.back(); } };
  list.addEventListener('click', (e) => {
    const b = e.target.closest('[data-id]');
    if (!b || closing) return;
    picked = +b.dataset.id;
    close(); // popstate handler below hides the sheet, then navigates
  });
  el.querySelector('[data-close]').onclick = close;
  el.addEventListener('click', (e) => { if (e.target === el) close(); });
  window.addEventListener('popstate', () => {
    if (el.hidden) return;
    el.hidden = true; closing = false; document.body.style.overflow = '';
    const id = picked, fn = cb;
    picked = null; cb = null;
    if (id != null) fn?.(id);
  });
  return {
    open(onPick, excl = []) {
      cb = onPick; exclude = new Set(excl);
      history.pushState({ overlay: 'picker' }, '');
      el.hidden = false; document.body.style.overflow = 'hidden';
      input.value = ''; show();
      setTimeout(() => input.focus(), 50);
    },
  };
})();

// ---------- views ----------
let cleanup = [];
function setNav(key) {
  document.querySelectorAll('[data-nav]').forEach((a) => a.classList.toggle('active', a.dataset.nav === key));
}

// ---------- home: birds near you ----------
const HOME_PAGE = 40;
const homeState = { q: '', shown: HOME_PAGE, scroll: 0 };

/** Birds for the home list: those recorded locally (most records first), else the most observed. */
function homeBirds() {
  const all = SPECIES.filter((s) => !isHybrid(s) && (!LOCAL || LOCAL.has(s.id)));
  return all.sort(byLocalThenObs(LOCAL));
}

function viewHome() {
  setNav('home');
  view.innerHTML = `
    ${locBar()}
    <input class="search" id="q" type="search" placeholder="Search a bird, e.g. 'raven' or 'honeyeater'…" autocomplete="off" enterkeyhint="search" value="${esc(homeState.q)}">
    <p class="muted small home-note" id="home-note" role="status"></p>
    <ul class="results" id="qres"></ul>
    <div class="more-wrap"><button class="btn ghost" id="more" hidden>Show more</button></div>`;
  const q = view.querySelector('#q'), res = view.querySelector('#qres'), more = view.querySelector('#more');
  const note = view.querySelector('#home-note');
  const draw = () => {
    const text = homeState.q.trim();
    const opts = { href: '#/id/' };
    if (text) {
      const r = search(text, 60);
      note.textContent = '';
      res.innerHTML = r.map((s) => resultItem(s, 'a', opts)).join('') || '<li class="empty">No matches</li>';
      more.hidden = true;
      return;
    }
    const all = homeBirds();
    note.textContent = `${LOCAL ? `Birds recorded ${locIn(LOC)}, most recorded first.`
      : LOC && local.status === 'loading' ? 'Loading birds near you… showing the most-recorded Australian birds meanwhile.'
      : 'The most-recorded Australian birds. Set a location to list the birds around you.'} Tap one to see its look-alikes and how to tell them apart.`;
    res.innerHTML = all.slice(0, homeState.shown).map((s) => resultItem(s, 'a', opts)).join('') || '<li class="empty">No birds</li>';
    more.hidden = all.length <= homeState.shown;
  };
  q.addEventListener('input', () => { homeState.q = q.value; homeState.shown = HOME_PAGE; draw(); });
  more.onclick = () => { homeState.shown += HOME_PAGE; draw(); };
  draw();
  localListeners.add(draw);
  return homeState.scroll;
}

// ---------- look-alikes & ID key ----------
const MAX_LOOKALIKES = 8;
const lookState = { nearOnly: true };

const groupsOf = (s) => GROUPS.map((g, i) => [g, i]).filter(([g]) => g.ids.includes(s.id));

/**
 * Birds that look like `s`. A bird in a curated confusion group gets its group mates plus same-genus
 * birds (family-and-size matches would add noise, e.g. ibis for a spoonbill); others get similarSpecies.
 */
function lookalikes(s) {
  const out = [], seen = new Set([s.id]);
  const push = (x, why) => { if (x && !seen.has(x.id)) { seen.add(x.id); out.push({ x, why }); } };
  const groups = groupsOf(s);
  for (const [g] of groups) g.ids.forEach((id) => push(BYID.get(id), g.title));
  for (const [x, why] of similarSpecies(s)) if (!groups.length || why === 'same genus') push(x, why);
  return out.slice(0, MAX_LOOKALIKES);
}

function leafLink(l, me, unk) {
  return `<a href="#/id/${l.s.id}"${l.s.id === me ? ' class="me"' : ''}>${esc(l.label)}</a>${
    unk.has(l.label) ? '<sup class="unk" title="Not recorded for a feature above, so listed under each answer">?</sup>' : ''}`;
}

/** Nested couplets: "Bill colour? black → Royal Spoonbill; pale yellow → Yellow-billed Spoonbill". */
function keyHTML(node, me, unk = new Set()) {
  if (!node.trait) {
    const names = node.leaves.map((l) => leafLink(l, me, unk)).join(', ');
    return node.leaves.length > 1
      ? `<span class="key-tip">→ ${names} <span class="muted small">(not separated by the recorded marks: compare photos)</span></span>`
      : `<span class="key-tip">→ ${names}</span>`;
  }
  return `<div class="couplet"><div class="key-q">${esc(node.trait.label)}?</div><ul>${node.branches.map((b) => {
    const u = new Set([...unk, ...b.unknown.map((l) => l.label)]);
    return `<li><span class="key-a">${esc(b.value)}</span> ${keyHTML(b.node, me, u)}</li>`;
  }).join('')}</ul></div>`;
}

function compareTableHTML(leaves, me) {
  const rows = compareRows(leaves, TRAITS);
  return `<div class="table-scroll"><table class="marks">
    <thead><tr><th></th>${leaves.map((l) => `<th${l.s.id === me ? ' class="me"' : ''}>${esc(l.s.common)}${
      l.plumage ? `<br><span class="muted small">${esc(l.plumage)}</span>` : ''}</th>`).join('')}</tr></thead>
    <tbody>
      <tr><th>Length</th>${leaves.map((l) => `<td>${fmtLen(l.s)}</td>`).join('')}</tr>
      ${rows.map((r) => `<tr${r.differs ? ' class="diff"' : ''}><th>${esc(r.label)}</th>${
        r.cells.map((c) => `<td>${c ? esc(c) : '<span class="muted">—</span>'}</td>`).join('')}</tr>`).join('')}
    </tbody></table></div>
    <p class="muted small">Highlighted rows differ between these birds.</p>`;
}

function viewLookalikes(id) {
  setNav('home');
  const s = BYID.get(id);
  if (!s) { view.innerHTML = '<p class="empty">Species not found.</p>'; return; }
  view.innerHTML = `
    <div class="hero">
      ${imgTag(photoSize(s.photo, 'medium'), 'alt=""')}
      <div>
        <h1>${esc(s.common)}</h1>
        <div class="sci">${esc(s.sci)}</div>
        <div class="stat-line"><span>Length <b>${fmtLen(s)}</b></span></div>
        <div class="local-line small" id="local-line"></div>
        <a class="small" href="#/s/${s.id}">Size ladder &amp; photos →</a>
      </div>
    </div>
    <div id="look"></div>`;
  const look = view.querySelector('#look');
  const draw = () => {
    view.querySelector('#local-line').innerHTML = localLine(s);
    const all = lookalikes(s);
    const filtering = lookState.nearOnly && !!LOCAL;
    const shown = filtering ? all.filter((o) => LOCAL.has(o.x.id)) : all;
    const hidden = filtering ? all.filter((o) => !LOCAL.has(o.x.id)) : [];
    const set = [s, ...shown.map((o) => o.x)];
    const leaves = markLeaves(set, MARKS);
    const noMarks = set.filter((x) => !MARKS[x.id]);
    const groups = groupsOf(s);
    const cmpIds = set.slice(0, MAX_COMPARE).map((x) => x.id);

    look.innerHTML = `
      <section class="card"><div class="row"><h2 style="margin:0">Looks similar</h2><span class="spacer"></span>
        ${LOCAL ? `<button class="chip" id="near-only" aria-pressed="${lookState.nearOnly}">📍 Near you only</button>` : ''}</div>
        ${shown.length ? `<ul class="results">${shown.map((o) => resultItem(o.x, 'a', { href: '#/id/', note: o.why })).join('')}</ul>`
          : `<p class="muted">${all.length ? `None of its look-alikes have been recorded ${esc(locIn(LOC))}.` : 'No look-alikes listed for this bird yet.'}</p>`}
        ${hidden.length ? `<p class="muted small" id="hidden-note">Also similar, but not recorded ${esc(locIn(LOC))}: ${
          hidden.map((o) => `<a href="#/id/${o.x.id}">${esc(o.x.common)}</a>`).join(', ')}.</p>` : ''}
      </section>
      ${leaves.length >= 2 ? `
        <section class="card" id="key-card"><h2>Tell them apart</h2>
          <div class="key">${keyHTML(buildKey(leaves, TRAITS), s.id)}</div>
          ${noMarks.length ? `<p class="muted small">No field marks recorded yet for ${noMarks.map((x) => esc(x.common)).join(', ')}.</p>` : ''}
          <div class="note">${leaves.some((l) => !l.ok) ? `Draft: some marks for ${esc([...new Set(leaves.filter((l) => !l.ok).map((l) => l.s.common))].join(', '))} aren't confirmed yet. `
            : ''}Field marks are checked against published species descriptions, not a field guide in hand. Confirm with Pizzey &amp; Knight, Morcombe, Menkhorst or Merlin.</div>
        </section>
        <section class="card" id="marks-card"><h2>Side by side</h2>${compareTableHTML(leaves, s.id)}</section>`
      : set.length >= 2 ? '<section class="card" id="key-card"><h2>Tell them apart</h2><p class="muted">No ID key for these birds yet. Compare their sizes and photos below.</p></section>' : ''}
      ${groups.map(([g, i]) => `<section class="card"><h2>Field notes · ${esc(g.title)}</h2>
        <ul class="tips">${g.tips.map((t) => `<li>${esc(t)}</li>`).join('')}</ul>
        <p style="margin:.7rem 0 0"><a class="chip" href="#/c/${g.ids.join(',')}?g=${i}">⚖︎ Sizes &amp; photos for this group</a></p></section>`).join('')}
      ${set.length >= 2 ? `<section class="card"><a class="btn" id="cmp-set" href="#/c/${cmpIds.join(',')}">Compare sizes &amp; photos side by side</a>
        ${set.length > MAX_COMPARE ? `<p class="muted small">Shows the first ${MAX_COMPARE}.</p>` : ''}</section>` : ''}`;
    const near = look.querySelector('#near-only');
    if (near) near.onclick = () => { lookState.nearOnly = !lookState.nearOnly; draw(); };
  };
  draw();
  localListeners.add(draw);
}

function localLine(s) {
  const n = LOCAL?.get(s.id) || 0;
  return !LOC ? ''
    : local.status === 'loading' ? '<span class="muted">Checking local records…</span>'
    : local.status !== 'ready' ? ''
    : n ? `📍 <b>${n.toLocaleString()}</b> research-grade record${n === 1 ? '' : 's'} ${esc(locIn(LOC))}`
    : `📍 <span class="muted">No research-grade records ${esc(locIn(LOC))}</span>`;
}

function similarSpecies(s) {
  const out = [];
  const seen = new Set([s.id]);
  const push = (x, why) => { if (x && !seen.has(x.id)) { seen.add(x.id); out.push([x, why]); } };
  const g = genus(s);
  const candidates = SPECIES.filter((x) => !isHybrid(x));
  const rank = byLocalThenObs(LOCAL);
  candidates.filter((x) => genus(x) === g && x.obs >= 5).sort(rank).slice(0, 5).forEach((x) => push(x, 'same genus'));
  if (s.len) {
    candidates.filter((x) => x.family === s.family && x.len && Math.abs(x.len - s.len) / s.len <= 0.25 && x.obs >= 20)
      .sort(rank).slice(0, 5).forEach((x) => push(x, 'same family, similar size'));
  }
  return out.slice(0, 8);
}

function viewSpecies(id) {
  setNav('');
  const s = BYID.get(id);
  if (!s) { view.innerHTML = '<p class="empty">Species not found.</p>'; return; }
  const groups = groupsOf(s);
  const ladder = s.len
    ? ladderHTML([{ s, color: 'var(--c0)' }, ...nearestBenchmarks(s.len, s.id).map((b) => ({ s: b, ref: true }))])
    : '<p class="muted small">No body-length data for this species (often vagrants, hybrids or domestic birds).</p>';
  view.innerHTML = `
    <div class="hero">
      ${imgTag(photoSize(s.photo, 'medium'), 'alt=""')}
      <div>
        <h1>${esc(s.common)}</h1>
        <div class="sci">${esc(s.sci)}</div>
        <div class="muted small">${esc(s.familyCommon || s.family || '')}</div>
        <div class="stat-line"><span>Length <b>${fmtLen(s)}</b></span><span>Weight <b>${fmtMass(s.mass)}</b></span></div>
        <div class="local-line small" id="local-line"></div>
      </div>
    </div>
    <section class="card"><h2>Size ladder</h2>${ladder}</section>
    <div id="cmp-card"></div>
    <section class="card"><h2>Real-world photos</h2>
      <p class="muted small" style="margin:-.3rem 0 .6rem">Research-grade iNaturalist observations from Australia. Try “Recent” for typical distant, backlit and in-flight views.</p>
      <div id="gfilters"></div><div id="gallery"></div>
    </section>`;
  const drawLocal = () => {
    view.querySelector('#local-line').innerHTML = localLine(s);
    const sim = similarSpecies(s);
    view.querySelector('#cmp-card').innerHTML = groups.length || sim.length ? `<section class="card"><h2>Compare with…</h2>
      <p style="margin:0 0 .6rem"><a class="btn" id="look-link" href="#/id/${s.id}">Look-alikes &amp; how to tell them apart</a></p>
      <div class="chips">
        ${groups.map(([g, i]) => `<a class="chip" href="#/c/${g.ids.join(',')}?g=${i}">⚖︎ ${esc(g.title)}</a>`).join('')}
        ${sim.map(([x]) => `<a class="chip" href="#/c/${s.id},${x.id}">vs ${esc(x.common)}${LOCAL?.get(x.id) ? ' 📍' : ''}</a>`).join('')}
        <button class="chip" id="cmp-any">+ any species…</button>
      </div></section>` : '<section class="card"><button class="btn ghost" id="cmp-any">+ Compare with any species…</button></section>';
    view.querySelector('#cmp-any').onclick = () => Picker.open((o) => (location.hash = `#/c/${s.id},${o}`), [s.id]);
  };
  drawLocal();
  localListeners.add(drawLocal);

  const state = { filter: 'all', order: 'votes' };
  const mount = () => {
    cleanup.forEach((f) => f()); cleanup = [];
    view.querySelector('#gfilters').innerHTML = filterChips(state.filter, state.order);
    const g = new Gallery(s.id, state.filter, state.order);
    cleanup.push(gridGallery(view.querySelector('#gallery'), g, s.common));
  };
  view.querySelector('#gfilters').addEventListener('click', (e) => {
    const f = e.target.closest('[data-filter]'), o = e.target.closest('[data-order]');
    if (f) state.filter = f.dataset.filter; else if (o) state.order = o.dataset.order; else return;
    mount();
  });
  mount();
}

function viewCompare(ids, gIdx) {
  setNav('compare');
  const sp = ids.map((id) => BYID.get(id)).filter(Boolean).slice(0, MAX_COMPARE);
  const nav = (list, keepG) => { location.hash = `#/c/${list.map((x) => x.id).join(',')}${keepG && gIdx != null ? `?g=${gIdx}` : ''}`; };
  const addBtn = sp.length < MAX_COMPARE ? '<button class="chip" id="add">+ Add species</button>' : '';

  if (sp.length < 2) {
    view.innerHTML = `
      <section class="card"><h2>Compare species</h2>
        <p class="muted">Pick 2–${MAX_COMPARE} birds to see them at true relative size, with photos side by side.</p>
        <div class="chips cmp-chips">${sp.map((s, i) => chipHTML(s, i)).join('')}${addBtn}</div>
      </section>
      <p class="muted small">Or <a href="#/">pick a bird</a> to see its look-alikes and how to tell them apart.</p>`;
    wireCompareChips(sp, nav);
    return;
  }

  const setKey = sp.map((s) => s.id).sort().join(',');
  let group = gIdx != null ? GROUPS[gIdx] : null;
  if (group && group.ids.slice().sort().join(',') !== setKey) group = null;
  const related = group ? [] : GROUPS.filter((g) => sp.filter((s) => g.ids.includes(s.id)).length >= 2);
  const tipsGroups = group ? [group] : related;

  const lens = sp.filter((s) => s.len);
  const minLen = Math.min(...lens.map((s) => s.len)), minMass = Math.min(...sp.filter((s) => s.mass).map((s) => s.mass));
  const meanLen = lens.reduce((a, s) => a + s.len, 0) / (lens.length || 1);
  const ref = lens.length ? nearestBenchmarks(meanLen, null, 1, 1).filter((b) => !sp.some((s) => s.id === b.id)) : [];

  view.innerHTML = `
    ${group ? `<h1 style="font-size:1.3rem;margin-bottom:.6rem">${esc(group.title)}</h1>` : ''}
    <div class="chips cmp-chips" style="margin-bottom:.9rem">${sp.map((s, i) => chipHTML(s, i)).join('')}${addBtn}</div>
    <section class="card">
      <div class="row"><h2 style="margin:0">True-scale size</h2><span class="spacer"></span>
        <button class="chip" id="refs" aria-pressed="true">Reference birds</button></div>
      <div id="ladder" style="margin-top:.6rem"></div>
    </section>
    <section class="card">
      <table class="stats">
        <tr><th></th><th>Length</th><th>Weight</th></tr>
        ${sp.map((s, i) => `<tr>
          <th style="color:${COLORS[i]}">${esc(s.common)}</th>
          <td class="num">${fmtLen(s)}${s.len && lens.length > 1 && s.len !== minLen ? `<br><span class="muted small">${(s.len / minLen).toFixed(2)}× longer</span>` : ''}</td>
          <td class="num">${fmtMass(s.mass)}${s.mass && s.mass !== minMass ? `<br><span class="muted small">${(s.mass / minMass).toFixed(1)}× heavier</span>` : ''}</td>
        </tr>`).join('')}
      </table>
    </section>
    ${tipsGroups.length ? tipsGroups.map((g) => `<section class="card"><h2>How to tell them apart${group ? '' : ` · ${esc(g.title)}`}</h2>
      <ul class="tips">${g.tips.map((t) => `<li>${esc(t)}</li>`).join('')}</ul>
      <div class="note">Quick field-mark reminders - confirm with a field guide (Pizzey &amp; Knight, Morcombe, Menkhorst) or Merlin.</div></section>`).join('') : ''}
    <section class="card"><h2>Photos side by side</h2>
      <p class="muted small" style="margin:-.3rem 0 .6rem">Swipe each row. Filters apply to every species - e.g. “Female” for fairy-wrens.</p>
      <div id="cfilters"></div><div id="strips"></div>
    </section>`;
  wireCompareChips(sp, nav);

  const ladderEl = view.querySelector('#ladder');
  const refsBtn = view.querySelector('#refs');
  const drawLadder = () => {
    const on = refsBtn.getAttribute('aria-pressed') === 'true';
    ladderEl.innerHTML = ladderHTML([...sp.map((s, i) => ({ s, color: COLORS[i] })), ...(on ? ref.map((b) => ({ s: b, ref: true })) : [])]);
  };
  refsBtn.onclick = () => { refsBtn.setAttribute('aria-pressed', refsBtn.getAttribute('aria-pressed') !== 'true'); drawLadder(); };
  if (!ref.length) refsBtn.hidden = true;
  drawLadder();

  const state = { filter: 'all', order: 'votes' };
  const strips = view.querySelector('#strips');
  const mount = () => {
    cleanup.forEach((f) => f()); cleanup = [];
    view.querySelector('#cfilters').innerHTML = filterChips(state.filter, state.order);
    strips.innerHTML = sp.map((s, i) => `
      <div class="strip-head"><span class="dot" style="background:${COLORS[i]}"></span><a href="#/s/${s.id}">${esc(s.common)}</a></div>
      <div data-strip="${i}"></div>`).join('');
    sp.forEach((s, i) => {
      const g = new Gallery(s.id, state.filter, state.order);
      cleanup.push(stripGallery(strips.querySelector(`[data-strip="${i}"]`), g, s.common));
    });
  };
  view.querySelector('#cfilters').addEventListener('click', (e) => {
    const f = e.target.closest('[data-filter]'), o = e.target.closest('[data-order]');
    if (f) state.filter = f.dataset.filter; else if (o) state.order = o.dataset.order; else return;
    mount();
  });
  mount();
}

function chipHTML(s, i) {
  return `<span class="chip"><span class="dot" style="background:${COLORS[i]}"></span><a href="#/s/${s.id}">${esc(s.common)}</a><button class="x" data-rm="${s.id}" aria-label="Remove ${esc(s.common)}">×</button></span>`;
}
function wireCompareChips(sp, nav) {
  view.querySelectorAll('[data-rm]').forEach((b) => (b.onclick = () => nav(sp.filter((s) => s.id !== +b.dataset.rm), false)));
  const add = view.querySelector('#add');
  if (add) add.onclick = () => Picker.open((id) => nav([...sp, BYID.get(id)], false), sp.map((s) => s.id));
}

// ---------- species list ----------
const listState = { q: '', sort: 'family', nearOnly: false, scroll: 0 };

function viewList() {
  setNav('list');
  const total = SPECIES.filter((s) => !isHybrid(s)).length;
  view.innerHTML = `
    ${locBar()}
    <input class="search" id="lq" type="search" placeholder="Filter by common, scientific or family name…" autocomplete="off" enterkeyhint="search" value="${esc(listState.q)}">
    <div class="chips list-controls">
      ${LIST_SORTS.map((o) => `<button class="chip" data-sort="${o.key}" aria-pressed="${o.key === listState.sort}">${o.label}</button>`).join('')}
      <button class="chip" id="near-only" aria-pressed="${listState.nearOnly}">📍 Recorded nearby</button>
    </div>
    <p class="muted small" id="lcount" role="status"></p>
    <div id="splist"></div>`;
  const nearBtn = view.querySelector('#near-only');
  const draw = () => {
    nearBtn.hidden = !LOCAL;
    const near = listState.nearOnly && !!LOCAL;
    const sections = speciesList(SPECIES, { ...listState, nearOnly: near, local: LOCAL });
    const n = sections.reduce((acc, sec) => acc + sec.items.length, 0);
    view.querySelector('#lcount').textContent = `${n.toLocaleString()} of ${total.toLocaleString()} species${near ? ` recorded ${locIn(LOC)}` : ''}`;
    const row = (s) => {
      const c = LOCAL?.get(s.id);
      return `<li><a href="#/s/${s.id}"><span class="cn">${esc(s.common)}</span><i class="sn">${esc(s.sci)}</i>${
        c ? `<span class="lc" title="Research-grade records ${esc(locIn(LOC))}">📍 ${c.toLocaleString()}</span>` : ''}</a></li>`;
    };
    view.querySelector('#splist').innerHTML = sections.map((sec) => `
      ${sec.title ? `<h3 class="fam-title">${esc(sec.title)} <i>${esc(sec.sub)}</i></h3>` : ''}
      <ul class="splist">${sec.items.map(row).join('')}</ul>`).join('') || '<p class="empty">No matches</p>';
  };
  view.querySelector('#lq').addEventListener('input', (e) => { listState.q = e.target.value; draw(); });
  view.querySelector('.list-controls').addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    if (b.dataset.sort) listState.sort = b.dataset.sort;
    else listState.nearOnly = !listState.nearOnly;
    view.querySelectorAll('[data-sort]').forEach((x) => x.setAttribute('aria-pressed', x.dataset.sort === listState.sort));
    nearBtn.setAttribute('aria-pressed', listState.nearOnly);
    draw();
  });
  draw();
  localListeners.add(draw);
  return listState.scroll; // restore the position when coming back from a species page
}

// ---------- location page ----------
let cameFromApp = false; // opened from another page of the app (so Back returns there)

function viewLocation() {
  setNav('');
  const radius = LOC?.kind === 'gps' ? LOC.radius : DEFAULT_RADIUS;
  view.innerHTML = `
    <section class="card"><h2>Your location</h2>
      <p class="muted small">Used to show which birds have research-grade iNaturalist records near you. Your position is rounded
        to about 1&nbsp;km, kept on this device, and sent only to iNaturalist.</p>
      <p>Now: <b id="loc-now">${esc(LOC ? locationLabel(LOC) : 'All of Australia')}</b></p>
      <div class="row loc-gps">
        <button class="btn" id="use-gps">📍 Use my current location</button>
        <label class="small">within <select id="radius">${RADII.map((r) => `<option value="${r}"${r === radius ? ' selected' : ''}>${r} km</option>`).join('')}</select></label>
      </div>
      <p class="small" id="gps-msg" role="status"></p>
    </section>
    <section class="card"><h2>Or pick a state or territory</h2>
      <div class="chips">${REGIONS.map((r) => `<button class="chip" data-region="${r.id}" aria-pressed="${LOC?.kind === 'region' && LOC.id === r.id}">${esc(r.name)}</button>`).join('')}</div>
    </section>
    <section class="card"><button class="btn ghost" id="loc-clear">Use all of Australia (no location)</button></section>`;
  const done = (loc) => {
    setLocation(loc);
    if (cameFromApp) history.back(); else location.replace('#/');
  };
  const msg = view.querySelector('#gps-msg');
  view.querySelector('#use-gps').onclick = async (e) => {
    e.target.disabled = true;
    msg.textContent = 'Finding you…';
    try {
      const pos = await currentPosition();
      done({ kind: 'gps', ...pos, radius: +view.querySelector('#radius').value });
    } catch (err) {
      msg.textContent = `${err.message} You can pick a state or territory instead.`;
      e.target.disabled = false;
    }
  };
  view.querySelectorAll('[data-region]').forEach((b) => {
    b.onclick = () => done({ kind: 'region', id: +b.dataset.region });
  });
  view.querySelector('#loc-clear').onclick = () => done(null);
}

function viewAbout() {
  setNav('about');
  view.innerHTML = `
    <section class="card"><h2>What this is</h2>
      <p>A companion to Merlin for the parts of ID that photos in field guides don't cover well: <b>shape</b>, <b>size</b>, and what birds <b>really look like</b> in ordinary photos - distant, backlit, in flight.</p>
      <ul class="tips">
        <li><b>Birds near you</b> - the birds recorded around you. Tap one to see what it could be confused with, an <b>ID key</b> that asks the questions that tell them apart (bill colour, throat, tail…), and a side-by-side table of field marks.</li>
        <li><b>Size ladder</b> - every species drawn to true relative scale beside familiar birds (fairy-wren, sparrow, magpie, raven…).</li>
        <li><b>Confusion groups</b> - ${GROUPS.length} curated Australian look-alike sets with field-mark notes and synced photo rows.</li>
        <li><b>Real-world photos</b> - research-grade iNaturalist observations from Australia; filter by adult/juvenile/male/female. “Recent” order gives typical, unpolished views.</li>
        <li><b>Species near you</b> - set a location (GPS or a state) and search, suggestions and the species list favour birds actually recorded there.</li>
      </ul>
    </section>
    <section class="card"><h2>Install on your phone</h2>
      <p><b>iPhone (Safari):</b> Share → “Add to Home Screen”.<br><b>Android (Chrome):</b> ⋮ menu → “Install app” / “Add to Home screen”.</p>
      <p class="muted small">The app shell, species data and photos you've viewed are cached for patchy reception. New photos need a connection.</p>
    </section>
    <section class="card"><h2>Accuracy notes</h2>
      <ul class="tips small">
        <li>The ID key is built from short field-mark notes checked against published species descriptions (Wikipedia articles citing HANZAB and the field guides), not a printed field guide. Keys that include marks not yet confirmed say so. Birds whose sexes or ages differ get one entry per plumage.</li>
        <li>Lengths are average bill-tip-to-tail-tip measurements; individual birds and sexes vary (ranges shown where known).</li>
        <li>Silhouettes come from PhyloPic. Where no drawing exists for the exact species, a relative from the same genus, family or order stands in - shape is then approximate. The credit under each ladder says which.</li>
        <li>Silhouettes are scaled so their longest side matches body length (or ≈${WINGSPAN_FACTOR}× for in-flight drawings), so treat the ladder as a guide to <i>relative</i> size.</li>
      </ul>
    </section>
    <section class="card"><h2>Data &amp; credits</h2>
      <ul class="tips small">
        <li>Photos &amp; species list: <a href="https://www.inaturalist.org" target="_blank" rel="noopener">iNaturalist</a> - each photo credited to its photographer with its licence.</li>
        <li>Body length &amp; mass: Garnett, S.T. et al. (2015) <i>Biological, ecological, conservation and legal information for all species and subspecies of Australian bird.</i> Scientific Data 2:150061 (CC0).</li>
        <li>Silhouettes: <a href="https://www.phylopic.org" target="_blank" rel="noopener">PhyloPic</a> contributors, credited individually under each size ladder.</li>
      </ul>
      <p class="muted small">${SPECIES.length} species · ${GROUPS.length} confusion groups</p>
    </section>`;
}

// ---------- router ----------
let current = null; // the view being shown, before this route() call

function route() {
  cleanup.forEach((f) => f()); cleanup = [];
  localListeners.clear();
  const [path, qs] = location.hash.replace(/^#/, '').split('?');
  const parts = path.split('/').filter(Boolean);
  const params = new URLSearchParams(qs || '');
  if (current === 'list') listState.scroll = window.scrollY;
  if (current === '') homeState.scroll = window.scrollY;
  cameFromApp = parts[0] === 'location' && current !== null;
  current = parts[0] || '';
  let y = 0;
  if (parts[0] === 's') viewSpecies(+parts[1]);
  else if (parts[0] === 'id') viewLookalikes(+parts[1]);
  else if (parts[0] === 'c') {
    const ids = [...new Set((parts[1] || '').split(',').filter(Boolean).map(Number))];
    viewCompare(ids, params.has('g') ? +params.get('g') : null);
  }
  else if (parts[0] === 'list') y = viewList();
  else if (parts[0] === 'location') viewLocation();
  else if (parts[0] === 'about') viewAbout();
  else y = viewHome();
  window.scrollTo(0, y);
}

async function boot() {
  view.innerHTML = '<p class="loading">Loading…</p>';
  try {
    const [species, groups, marks] = await Promise.all(
      ['species', 'groups', 'marks'].map((f) => fetch(`data/${f}.json`).then((r) => r.json())));
    SPECIES = species;
    for (const s of SPECIES) {
      BYID.set(indexSpecies(s).id, s);
    }
    GROUPS = groups.groups; BENCH = groups.benchmarks;
    MARKS = marks.marks; TRAITS = marks.traits;
  } catch (e) {
    view.innerHTML = `<p class="empty">Couldn't load data (${esc(e.message)}).</p>`;
    return;
  }
  window.addEventListener('hashchange', route);
  route();
  loadLocal();
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
}
boot();
