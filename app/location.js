// "Species near me": the user's chosen location (GPS or a state/territory) and the iNaturalist
// species counts for it. No DOM access here; storage, geolocation and fetch are injectable for tests.

const INAT = 'https://api.inaturalist.org/v1';
const KEY = 'birdid.location.v1';
const COUNTS_KEY = 'birdid.localCounts.v1';
export const COUNTS_MAX_AGE = 7 * 24 * 3600 * 1000; // refresh local counts weekly
export const RADII = [10, 25, 50, 100, 250];        // km
export const DEFAULT_RADIUS = 50;

// iNaturalist place ids (admin level 10, children of Australia / 6744)
export const REGIONS = [
  { id: 12986, name: 'Australian Capital Territory' },
  { id: 6825, name: 'New South Wales' },
  { id: 9994, name: 'Northern Territory' },
  { id: 7308, name: 'Queensland' },
  { id: 6899, name: 'South Australia' },
  { id: 6829, name: 'Tasmania' },
  { id: 7830, name: 'Victoria' },
  { id: 6827, name: 'Western Australia' },
];

/** Two decimal places (~1 km): enough for a 10 km+ radius, and all that's sent to iNaturalist. */
export const roundCoord = (x) => Math.round(x * 100) / 100;

/**
 * Locations: { kind: 'gps', lat, lng, radius } or { kind: 'region', id, name }.
 * Returns null for anything malformed (e.g. hand-edited storage).
 */
export function validLocation(loc) {
  if (!loc || typeof loc !== 'object') return null;
  if (loc.kind === 'gps' && Number.isFinite(loc.lat) && Number.isFinite(loc.lng) && RADII.includes(loc.radius)) {
    return { kind: 'gps', lat: roundCoord(loc.lat), lng: roundCoord(loc.lng), radius: loc.radius };
  }
  if (loc.kind === 'region') {
    const r = REGIONS.find((x) => x.id === loc.id);
    if (r) return { kind: 'region', id: r.id, name: r.name };
  }
  return null;
}

export function loadLocation(storage = localStorage) {
  try {
    return validLocation(JSON.parse(storage.getItem(KEY)));
  } catch {
    return null;
  }
}

export function saveLocation(loc, storage = localStorage) {
  if (loc) storage.setItem(KEY, JSON.stringify(validLocation(loc)));
  else storage.removeItem(KEY);
}

/** Short label: "within 50 km of you" / "Tasmania". */
export function locationLabel(loc) {
  if (!loc) return 'All of Australia';
  return loc.kind === 'gps' ? `within ${loc.radius} km of you` : loc.name;
}

/** Stable key for caching counts per location. */
export const locationKey = (loc) => (loc.kind === 'gps' ? `gps:${loc.lat},${loc.lng},${loc.radius}` : `region:${loc.id}`);

export function countsUrl(loc, page = 1) {
  const p = new URLSearchParams({ taxon_id: 3, quality_grade: 'research', per_page: 500, page, locale: 'en-AU' });
  if (loc.kind === 'gps') { p.set('lat', loc.lat); p.set('lng', loc.lng); p.set('radius', loc.radius); }
  else p.set('place_id', loc.id);
  return `${INAT}/observations/species_counts?${p}`;
}

/** All pages of species counts for `loc` -> { taxonId: count }. */
export async function fetchCounts(loc, getJSON) {
  const counts = {};
  for (let page = 1; page <= 10; page++) {
    const d = await getJSON(countsUrl(loc, page));
    for (const r of d.results) counts[r.taxon.id] = r.count;
    if (!d.results.length || Object.keys(counts).length >= d.total_results) break;
  }
  return counts;
}

/**
 * Counts for `loc` as a Map(taxonId -> count), from a fresh-enough cache or the network.
 * If the network fails, falls back to a stale cache (e.g. offline in the field); else throws.
 */
export async function localCounts(loc, getJSON, { storage = localStorage, now = Date.now() } = {}) {
  const key = locationKey(loc);
  let cached = null;
  try {
    const all = JSON.parse(storage.getItem(COUNTS_KEY));
    if (all && all.key === key) cached = all;
  } catch { /* corrupt cache: ignore */ }
  const toMap = (c) => new Map(Object.entries(c.counts).map(([k, v]) => [+k, v]));
  if (cached && now - cached.at < COUNTS_MAX_AGE) return { counts: toMap(cached), at: cached.at, stale: false };
  try {
    const counts = await fetchCounts(loc, getJSON);
    try {
      storage.setItem(COUNTS_KEY, JSON.stringify({ key, at: now, counts })); // only the current location is kept
    } catch { /* storage full: still usable this session */ }
    return { counts: toMap({ counts }), at: now, stale: false };
  } catch (e) {
    if (cached) return { counts: toMap(cached), at: cached.at, stale: true };
    throw e;
  }
}

/** Current position, rounded. Rejects with a user-readable message. */
export function currentPosition(geo = globalThis.navigator?.geolocation) {
  return new Promise((resolve, reject) => {
    if (!geo) { reject(new Error('Location is not available in this browser.')); return; }
    geo.getCurrentPosition(
      (p) => resolve({ lat: roundCoord(p.coords.latitude), lng: roundCoord(p.coords.longitude) }),
      (e) => reject(new Error(e.code === 1 ? 'Location permission was denied.' : 'Couldn’t get your location.')),
      { enableHighAccuracy: false, timeout: 15000, maximumAge: 10 * 60 * 1000 },
    );
  });
}
