"""'Species near me': app/location.js unit tests, plus the location page, species list and local ranking
in the real app. FakeNet answers species_counts from `net.local` ({taxon_id: count})."""
import json, re

import pytest
from playwright.sync_api import expect

SYDNEY = {"latitude": -33.868820, "longitude": 151.209296}


# ---------- location.js (pure module, run in the browser) ----------

@pytest.fixture
def loc(app):
    app.goto("/#/about")
    app.wait_for_selector("text=What this is")

    def call(body, *args):
        return app.evaluate(f"""async (args) => {{
            const L = await import('/location.js');
            const mem = () => {{ const m = new Map(); return {{
                getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)),
                removeItem: (k) => m.delete(k), _m: m }}; }};
            return ({body})(...args);
        }}""", list(args))
    return call


def test_valid_location_rounds_and_rejects_junk(loc):
    assert loc("(x) => L.validLocation(x)", {"kind": "gps", "lat": -33.868820, "lng": 151.209296, "radius": 50}) == \
        {"kind": "gps", "lat": -33.87, "lng": 151.21, "radius": 50}
    assert loc("(x) => L.validLocation(x)", {"kind": "region", "id": 6829, "name": "ignored"}) == \
        {"kind": "region", "id": 6829, "name": "Tasmania"}
    for bad in [None, "x", {"kind": "gps", "lat": "1", "lng": 2, "radius": 50}, {"kind": "gps", "lat": 1, "lng": 2, "radius": 37},
                {"kind": "region", "id": 1}, {"kind": "planet"}]:
        assert loc("(x) => L.validLocation(x)", bad) is None


def test_save_and_load_location(loc):
    assert loc("""() => { const s = mem();
        L.saveLocation({ kind: 'region', id: 7830 }, s); const a = L.loadLocation(s);
        L.saveLocation(null, s); const b = L.loadLocation(s);
        s.setItem('birdid.location.v1', '{not json'); const c = L.loadLocation(s);
        return [a, b, c]; }""") == [{"kind": "region", "id": 7830, "name": "Victoria"}, None, None]


def test_counts_url(loc):
    gps = loc("() => L.countsUrl({ kind: 'gps', lat: -33.87, lng: 151.21, radius: 25 }, 2)")
    assert "lat=-33.87" in gps and "lng=151.21" in gps and "radius=25" in gps and "page=2" in gps
    assert "taxon_id=3" in gps and "quality_grade=research" in gps and "place_id" not in gps
    region = loc("() => L.countsUrl({ kind: 'region', id: 6829 })")
    assert "place_id=6829" in region and "lat=" not in region


def test_fetch_counts_follows_pages(loc):
    result = loc("""async () => {
        const pages = { 1: { total_results: 3, results: [{ count: 9, taxon: { id: 1 } }, { count: 5, taxon: { id: 2 } }] },
                        2: { total_results: 3, results: [{ count: 1, taxon: { id: 3 } }] } };
        const urls = [];
        const counts = await L.fetchCounts({ kind: 'region', id: 6829 },
            async (u) => { urls.push(u); return pages[new URL(u).searchParams.get('page')]; });
        return [counts, urls.length]; }""")
    assert result == [{"1": 9, "2": 5, "3": 1}, 2]


LOCAL_COUNTS = """async (now, fail, preload) => {
    const s = mem(), calls = [];
    if (preload) s.setItem('birdid.localCounts.v1', JSON.stringify(preload));
    const getJSON = async (u) => { calls.push(u); if (fail) throw new Error('offline');
        return { total_results: 1, results: [{ count: 4, taxon: { id: 42 } }] }; };
    try {
        const r = await L.localCounts({ kind: 'region', id: 6829 }, getJSON, { storage: s, now });
        return { counts: [...r.counts], stale: r.stale, calls: calls.length, saved: JSON.parse(s.getItem('birdid.localCounts.v1')) };
    } catch (e) { return { error: e.message, calls: calls.length }; }
}"""
DAY = 24 * 3600 * 1000


def test_local_counts_fetches_and_caches(loc):
    r = loc(LOCAL_COUNTS, 1000, False, None)
    assert r["counts"] == [[42, 4]] and r["calls"] == 1 and not r["stale"]
    assert r["saved"] == {"key": "region:6829", "at": 1000, "counts": {"42": 4}}


def test_local_counts_uses_fresh_cache_without_network(loc):
    cache = {"key": "region:6829", "at": 0, "counts": {"7": 2}}
    r = loc(LOCAL_COUNTS, 6 * DAY, False, cache)
    assert r["counts"] == [[7, 2]] and r["calls"] == 0


def test_local_counts_refreshes_old_cache_and_falls_back_when_offline(loc):
    cache = {"key": "region:6829", "at": 0, "counts": {"7": 2}}
    fresh = loc(LOCAL_COUNTS, 8 * DAY, False, cache)
    assert fresh["counts"] == [[42, 4]] and fresh["calls"] == 1
    offline = loc(LOCAL_COUNTS, 8 * DAY, True, cache)
    assert offline["counts"] == [[7, 2]] and offline["stale"] is True


def test_local_counts_ignores_cache_for_another_place_and_errors_offline(loc):
    other = {"key": "region:7830", "at": 0, "counts": {"7": 2}}
    assert loc(LOCAL_COUNTS, 1, True, other) == {"error": "offline", "calls": 1}


def test_current_position_rounds_and_explains_errors(loc):
    assert loc("""() => L.currentPosition({ getCurrentPosition: (ok) => ok({ coords: { latitude: -42.88214, longitude: 147.32941 } }) })""") \
        == {"lat": -42.88, "lng": 147.33}
    assert loc("""() => L.currentPosition({ getCurrentPosition: (ok, err) => err({ code: 1 }) }).catch((e) => e.message)""") \
        == "Location permission was denied."
    assert loc("() => L.currentPosition(null).catch((e) => e.message)") == "Location is not available in this browser."


# ---------- local ranking & list helpers in lib.js ----------

def test_by_local_then_obs_and_search_tiebreak(loc):
    r = loc("""async () => {
        const Lib = await import('/lib.js');
        const sp = [{ id: 1, obs: 100 }, { id: 2, obs: 50 }, { id: 3, obs: 10 }];
        const local = new Map([[3, 5], [2, 1]]);
        const a = [...sp].sort(Lib.byLocalThenObs(null)).map((s) => s.id);
        const b = [...sp].sort(Lib.byLocalThenObs(local)).map((s) => s.id);
        const all = (await (await fetch('/data/species.json')).json()).map(Lib.indexSpecies);
        const forest = all.find((s) => s.common === 'Forest Raven');
        const plain = Lib.search(all, 'raven', 3).map((s) => s.common);
        const tas = Lib.search(all, 'raven', 3, new Map([[forest.id, 50]])).map((s) => s.common);
        return { a, b, plain, tas }; }""")
    assert r["a"] == [1, 2, 3] and r["b"] == [3, 2, 1]
    assert r["plain"][0] == "Australian Raven"
    assert r["tas"][0] == "Forest Raven"  # same match quality: the locally recorded one wins


def test_species_list_grouping_sorting_and_filters(loc):
    r = loc("""async () => {
        const Lib = await import('/lib.js');
        const all = (await (await fetch('/data/species.json')).json()).map(Lib.indexSpecies);
        const fam = Lib.speciesList(all);
        const flat = Lib.speciesList(all, { sort: 'sci' })[0].items.map((s) => s.sci);
        const common = Lib.speciesList(all, { sort: 'common' })[0].items.map((s) => s.common);
        const magpie = all.find((s) => s.common === 'Australian Magpie');
        const near = Lib.speciesList(all, { sort: 'common', nearOnly: true, local: new Map([[magpie.id, 3]]) })[0].items.map((s) => s.common);
        const bySci = Lib.speciesList(all, { q: 'gymnorhina', sort: 'common' })[0].items.map((s) => s.common);
        const byFam = Lib.speciesList(all, { q: 'artamidae' }).map((f) => f.sub);
        return {
            famTitles: fam.map((f) => f.title), famCount: fam.reduce((a, f) => a + f.items.length, 0),
            hybrids: all.filter(Lib.isHybrid).length, total: all.length,
            flatSorted: flat.every((x, i) => i === 0 || flat[i - 1].localeCompare(x, 'en', { sensitivity: 'base' }) <= 0),
            commonFirst: common[0], near, bySci, byFam };
    }""")
    assert r["famTitles"] == sorted(r["famTitles"], key=str.lower)
    assert r["famCount"] == r["total"] - r["hybrids"]  # hybrids aren't listed
    assert r["flatSorted"] and r["commonFirst"] < "B"
    assert r["near"] == ["Australian Magpie"]
    assert r["bySci"] == ["Australian Magpie"]
    assert r["byFam"] == ["Artamidae"]


# ---------- the app ----------

def set_region(app, name):
    app.locator(".locbar-main").first.click()
    expect(app).to_have_url(re.compile(r"#/location$"))
    app.locator("[data-region]", has_text=name).click()


def test_no_location_by_default(app, net):
    app.goto("/")
    expect(app.locator(".locbar")).to_contain_text("All of Australia")
    expect(app.locator(".locbar")).to_contain_text("Set a location")
    assert net.counts_calls == []


def test_pick_region_returns_to_page_and_persists(app, net, sp, species):
    raven, forest = sp("Australian Raven"), sp("Forest Raven")
    hybrid = next(s for s in species if "×" in s["sci"])
    # a hybrid and a taxon missing from the app's data aren't counted: the bar matches the list
    net.local = {forest["id"]: 120, raven["id"]: 3, hybrid["id"]: 9, 999999999: 4}
    app.goto("/#/about")
    app.click("[data-nav=home]")
    set_region(app, "Tasmania")
    expect(app).to_have_url(re.compile(r"#/$"))  # back on home
    expect(app.locator(".locbar")).to_contain_text("Tasmania")
    expect(app.locator(".locbar")).to_contain_text("2 species recorded")
    assert net.counts_calls[-1]["place_id"] == "6829"
    app.go_back()  # the location page isn't left in the history: Back goes to the page before home
    expect(app).to_have_url(re.compile(r"#/about$"))
    # survives a reload, served from the local cache (no new request)
    n = len(net.counts_calls)
    app.goto("/#/")
    app.reload()
    expect(app.locator(".locbar")).to_contain_text("2 species recorded")
    assert len(net.counts_calls) == n


def test_use_my_location_rounds_coordinates(app, net, context, sp):
    context.grant_permissions(["geolocation"])
    context.set_geolocation(SYDNEY)
    net.local = {sp("Noisy Miner")["id"]: 900}
    app.goto("/#/list")
    app.locator(".locbar-main").click()
    app.select_option("#radius", "25")
    app.click("#use-gps")
    expect(app).to_have_url(re.compile(r"#/list$"))  # back where we started
    expect(app.locator(".locbar")).to_contain_text("Within 25 km of you")
    q = net.counts_calls[-1]
    assert (q["lat"], q["lng"], q["radius"]) == ("-33.87", "151.21", "25")  # ~1 km precision only
    assert "place_id" not in q


def test_location_denied_explains_and_offers_regions(app, net):
    app.goto("/#/location")  # no permission granted in this context
    app.click("#use-gps")
    expect(app.locator("#gps-msg")).to_contain_text("pick a state or territory")
    expect(app.locator("#use-gps")).to_be_enabled()
    assert net.counts_calls == []


def test_clear_location(app, net, sp):
    net.local = {sp("Australian Magpie")["id"]: 5}
    app.goto("/")
    set_region(app, "Victoria")
    expect(app.locator(".locbar")).to_contain_text("1 species recorded")
    app.locator(".locbar-main").click()
    app.click("#loc-clear")
    expect(app.locator(".locbar")).to_contain_text("All of Australia")
    assert app.evaluate("() => localStorage.getItem('birdid.location.v1')") is None


def test_failed_counts_show_retry(app, net, sp, allow_http_errors):
    net.counts_status = 404
    app.goto("/")
    set_region(app, "Queensland")
    expect(app.locator(".locbar")).to_contain_text("Couldn't load local records")
    net.counts_status = 200
    net.local = {sp("Australian Magpie")["id"]: 5}
    app.locator("[data-loc-retry]").click()
    expect(app.locator(".locbar")).to_contain_text("1 species recorded")


def test_search_and_picker_rank_local_species_first(app, net, sp):
    forest = sp("Forest Raven")
    net.local = {forest["id"]: 120}
    app.goto("/")
    app.fill("#q", "raven")
    expect(app.locator("#qres li").first).to_contain_text("Australian Raven")
    set_region(app, "Tasmania")
    expect(app.locator(".locbar")).to_contain_text("1 species recorded")
    app.fill("#q", "raven")
    expect(app.locator("#qres li").first).to_contain_text("Forest Raven")
    expect(app.locator("#qres li").first).to_contain_text("nearby")
    # the compare picker's default list is "popular near you"
    app.goto(f"/#/c/{sp('Australian Magpie')['id']}")
    app.click("#add")
    expect(app.locator("#picker-results li").first).to_contain_text("Forest Raven")


def test_species_page_shows_local_records(app, net, sp):
    magpie, emu = sp("Australian Magpie"), sp("Emu")
    net.local = {magpie["id"]: 1234}
    app.goto("/")
    set_region(app, "Victoria")
    expect(app.locator(".locbar")).to_contain_text("1 species recorded")
    app.goto(f"/#/s/{magpie['id']}")
    expect(app.locator("#local-line")).to_have_text("📍 1,234 research-grade records in Victoria")
    app.goto(f"/#/s/{emu['id']}")
    expect(app.locator("#local-line")).to_have_text("📍 No research-grade records in Victoria")


def test_similar_species_prefer_local(app, net, sp):
    # Pacific Black Duck's genus-mates by Australia-wide records: Chestnut Teal, Grey Teal, Mallard
    duck, grey = sp("Pacific Black Duck"), sp("Grey Teal")
    net.local = {grey["id"]: 10, duck["id"]: 50}
    app.goto("/")
    set_region(app, "Northern Territory")
    expect(app.locator(".locbar")).to_contain_text("2 species recorded")
    app.goto(f"/#/s/{duck['id']}")
    first = app.locator("#cmp-card .chip", has_text=re.compile(r"^vs ")).first
    expect(first).to_contain_text("Grey Teal")
    expect(first).to_contain_text("📍")


# ---------- species list page ----------

def test_species_list_shows_scientific_names_by_family(app, species, sp):
    total = sum("×" not in s["sci"] for s in species)
    app.goto("/")
    app.click("[data-nav=list]")
    expect(app.locator("[data-nav=list]")).to_have_class(re.compile("active"))
    expect(app.locator("#lcount")).to_have_text(f"{total} of {total} species")
    expect(app.locator(".splist li")).to_have_count(total)
    magpie_row = app.locator(".splist li", has_text="Australian Magpie")
    expect(magpie_row.locator(".sn")).to_have_text("Gymnorhina tibicen")
    expect(app.locator(".fam-title", has_text="Artamidae")).to_have_count(1)
    expect(app.locator("#near-only")).to_be_hidden()  # no location set


def test_species_list_filter_and_sorts(app):
    app.goto("/#/list")
    app.fill("#lq", "corvus")
    expect(app.locator("#lcount")).to_contain_text(re.compile(r"^[1-9]\d* of"))
    assert all(t.startswith("Corvus ") for t in app.locator(".splist .sn").all_inner_texts())
    app.fill("#lq", "")
    app.click("[data-sort=sci]")
    expect(app.locator(".fam-title")).to_have_count(0)
    sci = app.locator(".splist .sn").all_inner_texts()
    assert sci == sorted(sci, key=str.lower)
    app.click("[data-sort=common]")
    first = app.locator(".splist .cn").first.inner_text()
    assert first[0] in "AB"


def test_species_list_nearby_only(app, net, sp):
    a, b = sp("Australian Magpie"), sp("Superb Fairywren")
    net.local = {a["id"]: 40, b["id"]: 7}
    app.goto("/#/list")
    set_region(app, "Victoria")
    expect(app).to_have_url(re.compile(r"#/list$"))
    expect(app.locator("#near-only")).to_be_visible()
    app.click("#near-only")
    expect(app.locator(".splist li")).to_have_count(2)
    expect(app.locator("#lcount")).to_have_text("2 of 839 species recorded in Victoria")
    expect(app.locator(".splist li", has_text="Australian Magpie").locator(".lc")).to_have_text("📍 40")


def test_species_list_restores_scroll_and_filters_after_visiting_a_species(app):
    app.goto("/#/list")
    app.fill("#lq", "honeyeater")
    row = app.locator(".splist li a").nth(25)
    row.scroll_into_view_if_needed()
    y = app.evaluate("() => scrollY")
    assert y > 200
    row.click()
    expect(app.locator("h1")).to_be_visible()
    app.go_back()
    expect(app.locator("#lq")).to_have_value("honeyeater")
    app.wait_for_function("(y) => Math.abs(scrollY - y) < 5", arg=y)


@pytest.mark.parametrize("width", [360, 420])
def test_nav_fits_on_small_phones(app, page, width):
    page.set_viewport_size({"width": width, "height": 740})
    app.goto("/#/list")
    expect(app.locator("[data-nav=about]")).to_be_visible()
    assert app.evaluate("() => document.documentElement.scrollWidth <= innerWidth")
    box = app.locator("[data-nav=about]").bounding_box()
    assert box["x"] + box["width"] <= width
