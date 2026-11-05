// BirdID Shapes - size ladders, silhouettes, real-world photos and confusion-pair comparisons.
// Vanilla JS, no build step. Data: data/species.json + data/groups.json (built by tools/build_data.py),
// live photos from the iNaturalist API. Pure helpers live in lib.js.

import {
  WINGSPAN_FACTOR, esc, photoSize, fmtLen, fmtMass, genus, isHybrid, imgTag, setImgSrc,
  indexSpecies, search as searchIn, silDims, nearestBenchmarks as nearestIn,
} from './lib.js';

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
const view = document.getElementById('view');

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
const search = (q, limit) => searchIn(SPECIES, q, limit);
const popular = (n = 25) => [...SPECIES].sort((a, b) => b.obs - a.obs).slice(0, n);

function resultItem(s, tag = 'a') {
  const img = s.photo ? imgTag(s.photo) : '<span class="thumb"></span>';
  const inner = `${img}<span class="names"><b>${esc(s.common)}</b><i>${esc(s.sci)}${s.len ? ` · ${s.len} cm` : ''}</i></span>`;
  return tag === 'a'
    ? `<li><a href="#/s/${s.id}">${inner}</a></li>`
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

function viewHome() {
  setNav('home');
  const cats = [...new Set(GROUPS.map((g) => g.cat))];
  view.innerHTML = `
    <input class="search" id="q" type="search" placeholder="Search a species, e.g. 'raven' or 'honeyeater'…" autocomplete="off" enterkeyhint="search">
    <ul class="results" id="qres"></ul>
    <div id="groups">
      <p class="muted small" style="margin:.8rem 0 0">Tap a group to compare look-alikes side by side: true-scale silhouettes, sizes, field-mark notes and real iNaturalist photos.</p>
      ${cats.map((c) => `
        <h3 class="cat-title">${esc(c)}</h3>
        <div class="group-list">
          ${GROUPS.map((g, i) => [g, i]).filter(([g]) => g.cat === c).map(([g, i]) => `
            <a class="group-card" href="#/c/${g.ids.join(',')}?g=${i}">
              <div class="stack">${g.ids.slice(0, 3).map((id) => imgTag(BYID.get(id)?.photo || '')).join('')}</div>
              <span>${esc(g.title)}</span>
            </a>`).join('')}
        </div>`).join('')}
    </div>`;
  const q = document.getElementById('q'), res = document.getElementById('qres'), groups = document.getElementById('groups');
  q.addEventListener('input', () => {
    const r = search(q.value);
    res.innerHTML = r.map((s) => resultItem(s)).join('') || (q.value.trim() ? '<li class="empty">No matches</li>' : '');
    groups.hidden = !!q.value.trim();
  });
}

function similarSpecies(s) {
  const out = [];
  const seen = new Set([s.id]);
  const push = (x, why) => { if (x && !seen.has(x.id)) { seen.add(x.id); out.push([x, why]); } };
  const g = genus(s);
  const candidates = SPECIES.filter((x) => !isHybrid(x));
  candidates.filter((x) => genus(x) === g && x.obs >= 5).sort((a, b) => b.obs - a.obs).slice(0, 5).forEach((x) => push(x, 'same genus'));
  if (s.len) {
    candidates.filter((x) => x.family === s.family && x.len && Math.abs(x.len - s.len) / s.len <= 0.25 && x.obs >= 20)
      .sort((a, b) => b.obs - a.obs).slice(0, 5).forEach((x) => push(x, 'same family, similar size'));
  }
  return out.slice(0, 8);
}

function viewSpecies(id) {
  setNav('');
  const s = BYID.get(id);
  if (!s) { view.innerHTML = '<p class="empty">Species not found.</p>'; return; }
  const groups = GROUPS.map((g, i) => [g, i]).filter(([g]) => g.ids.includes(s.id));
  const sim = similarSpecies(s);
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
      </div>
    </div>
    <section class="card"><h2>Size ladder</h2>${ladder}</section>
    ${groups.length || sim.length ? `<section class="card"><h2>Compare with…</h2>
      <div class="chips">
        ${groups.map(([g, i]) => `<a class="chip" href="#/c/${g.ids.join(',')}?g=${i}">⚖︎ ${esc(g.title)}</a>`).join('')}
        ${sim.map(([x]) => `<a class="chip" href="#/c/${s.id},${x.id}">vs ${esc(x.common)}</a>`).join('')}
        <button class="chip" id="cmp-any">+ any species…</button>
      </div></section>` : `<section class="card"><button class="btn ghost" id="cmp-any">+ Compare with any species…</button></section>`}
    <section class="card"><h2>Real-world photos</h2>
      <p class="muted small" style="margin:-.3rem 0 .6rem">Research-grade iNaturalist observations from Australia. Try “Recent” for typical distant, backlit and in-flight views.</p>
      <div id="gfilters"></div><div id="gallery"></div>
    </section>`;
  view.querySelector('#cmp-any').onclick = () => Picker.open((o) => (location.hash = `#/c/${s.id},${o}`), [s.id]);

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
      <p class="muted small">Or start from one of the <a href="#/">confusion groups</a>.</p>`;
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

function viewAbout() {
  setNav('about');
  view.innerHTML = `
    <section class="card"><h2>What this is</h2>
      <p>A companion to Merlin for the parts of ID that photos in field guides don't cover well: <b>shape</b>, <b>size</b>, and what birds <b>really look like</b> in ordinary photos - distant, backlit, in flight.</p>
      <ul class="tips">
        <li><b>Size ladder</b> - every species drawn to true relative scale beside familiar birds (fairy-wren, sparrow, magpie, raven…).</li>
        <li><b>Confusion groups</b> - curated Australian look-alikes with field-mark notes and synced photo rows.</li>
        <li><b>Real-world photos</b> - research-grade iNaturalist observations from Australia; filter by adult/juvenile/male/female. “Recent” order gives typical, unpolished views.</li>
      </ul>
    </section>
    <section class="card"><h2>Install on your phone</h2>
      <p><b>iPhone (Safari):</b> Share → “Add to Home Screen”.<br><b>Android (Chrome):</b> ⋮ menu → “Install app” / “Add to Home screen”.</p>
      <p class="muted small">The app shell, species data and photos you've viewed are cached for patchy reception. New photos need a connection.</p>
    </section>
    <section class="card"><h2>Accuracy notes</h2>
      <ul class="tips small">
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
function route() {
  cleanup.forEach((f) => f()); cleanup = [];
  const [path, qs] = location.hash.replace(/^#/, '').split('?');
  const parts = path.split('/').filter(Boolean);
  const params = new URLSearchParams(qs || '');
  if (parts[0] === 's') viewSpecies(+parts[1]);
  else if (parts[0] === 'c') {
    const ids = [...new Set((parts[1] || '').split(',').filter(Boolean).map(Number))];
    viewCompare(ids, params.has('g') ? +params.get('g') : null);
  }
  else if (parts[0] === 'about') viewAbout();
  else viewHome();
  window.scrollTo(0, 0);
}

async function boot() {
  view.innerHTML = '<p class="loading">Loading…</p>';
  try {
    const [species, groups] = await Promise.all([
      fetch('data/species.json').then((r) => r.json()),
      fetch('data/groups.json').then((r) => r.json()),
    ]);
    SPECIES = species;
    for (const s of SPECIES) {
      BYID.set(indexSpecies(s).id, s);
    }
    GROUPS = groups.groups; BENCH = groups.benchmarks;
  } catch (e) {
    view.innerHTML = `<p class="empty">Couldn't load data (${esc(e.message)}).</p>`;
    return;
  }
  window.addEventListener('hashchange', route);
  route();
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
}
boot();
