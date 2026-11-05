"""Service worker tests.

Playwright can't intercept requests made *by* a service worker, so most tests load sw.js into a
harness page instead: its event listeners are captured and called directly, using the page's real
CacheStorage and a real (Playwright-routed) fetch. Real opaque and CORS responses therefore behave
exactly as in production. test_offline_reload_with_real_worker covers actual registration.
"""
import re

import pytest

S3 = "https://inaturalist-open-data.s3.amazonaws.com/photos/{}/medium.jpg"
STATIC = "https://static.inaturalist.org/photos/{}/medium.jpg"
API = "https://api.inaturalist.org/v1/observations?taxon_id=8575&page={}&per_page=30"

HARNESS = """<!DOCTYPE html><html><body><script>
window.__h = {};
self.addEventListener = (type, fn) => { __h[type] = fn; };
self.skipWaiting = async () => {};
Object.defineProperty(self, 'clients', { value: { claim: async () => {} } });
const realFetch = window.fetch.bind(window);
window.__net = { offline: false, calls: [] };
window.fetch = (req) => {
  __net.calls.push(typeof req === 'string' ? req : req.url);
  return __net.offline ? Promise.reject(new TypeError('Failed to fetch (offline)')) : realFetch(req);
};
// Run one SW event; resolves with what was passed to respondWith (null if not handled)
// after every waitUntil promise has settled.
window.dispatch = async (type, request) => {
  const waits = [];
  let responded = null;
  __h[type]({ request, waitUntil: (p) => waits.push(p), respondWith: (p) => { responded = p; } });
  const res = responded && await responded;
  await Promise.all(waits);
  return res;
};
// fetch event for url; returns a summary of the response
window.sw = async (url, init = {}) => {
  const res = await dispatch('fetch', new Request(url, init));
  return res && { type: res.type, status: res.status, body: res.type === 'opaque' ? null : await res.text() };
};
window.cacheUrls = async (name) => (await (await caches.open(name)).keys()).map((r) => r.url);
</script><script src="/sw.js"></script></body></html>"""


@pytest.fixture
def h(app, base_url):
    """Harness page with sw.js loaded; the `app` fixture still fails on console errors / stray requests."""
    app.route(f"{base_url}/__harness.html", lambda r: r.fulfill(status=200, content_type="text/html", body=HARNESS))
    app.goto("/__harness.html")
    app.wait_for_function("() => typeof window.__h.fetch === 'function'")
    return app


def calls(h):
    return h.evaluate("() => __net.calls.length")


# ---------- install / activate ----------

def test_install_precaches_the_whole_shell(h, base_url):
    h.evaluate("() => dispatch('install')")
    shell = h.evaluate("SHELL_FILES")
    cached = h.evaluate("() => cacheUrls(SHELL)")
    assert len(cached) == len(shell)
    assert f"{base_url}/lib.js" in cached and f"{base_url}/data/species.json" in cached


def test_activate_deletes_old_caches_only(h):
    h.evaluate("""async () => {
        for (const n of ['shell-v1', 'img-v1', 'something-else', ...CACHES]) await caches.open(n);
        await dispatch('activate');
    }""")
    assert sorted(h.evaluate("() => caches.keys()")) == sorted(h.evaluate("CACHES"))


# ---------- images ----------

def test_cors_image_is_cached_as_cors_and_served_offline(h):
    url = S3.format(1)
    first = h.evaluate("(u) => sw(u, { mode: 'cors' })", url)
    assert first["type"] == "cors" and first["status"] == 200
    assert h.evaluate("() => cacheUrls(IMG)") == [url]
    assert h.evaluate("() => cacheUrls(IMG_OPAQUE)") == []
    n = calls(h)
    h.evaluate("() => { __net.offline = true; }")
    again = h.evaluate("(u) => sw(u, { mode: 'cors' })", url)
    assert again["type"] == "cors" and calls(h) == n  # straight from cache


def test_opaque_image_goes_to_the_small_opaque_cache(h):
    url = STATIC.format(1)
    res = h.evaluate("(u) => sw(u, { mode: 'no-cors' })", url)
    assert res["type"] == "opaque"
    assert h.evaluate("() => cacheUrls(IMG_OPAQUE)") == [url]
    assert h.evaluate("() => cacheUrls(IMG)") == []
    n = calls(h)
    assert h.evaluate("(u) => sw(u, { mode: 'no-cors' })", url)["type"] == "opaque"
    assert calls(h) == n


def test_cors_request_is_never_answered_with_an_opaque_entry(h):
    """An opaque cached response for a crossorigin <img> would make the image fail to load."""
    url = S3.format(2)
    h.evaluate("(u) => sw(u, { mode: 'no-cors' })", url)  # e.g. cached before crossorigin was added
    assert h.evaluate("() => cacheUrls(IMG_OPAQUE)") == [url]
    n = calls(h)
    res = h.evaluate("(u) => sw(u, { mode: 'cors' })", url)
    assert res["type"] == "cors" and calls(h) == n + 1


def test_no_cors_request_can_use_a_cors_entry(h):
    url = S3.format(3)
    h.evaluate("(u) => sw(u, { mode: 'cors' })", url)
    n = calls(h)
    assert h.evaluate("(u) => sw(u, { mode: 'no-cors' })", url)["type"] == "cors"
    assert calls(h) == n


def test_opaque_cache_is_capped(h):
    cap = h.evaluate("IMG_OPAQUE_MAX")
    urls = [STATIC.format(i) for i in range(cap + 5)]
    h.evaluate("async (us) => { for (const u of us) await sw(u, { mode: 'no-cors' }); }", urls)
    assert h.evaluate("() => cacheUrls(IMG_OPAQUE)") == urls[5:]  # oldest evicted first


def test_failed_image_is_not_cached(h, allow_http_errors):
    h.route(re.compile(r"https://inaturalist-open-data\.s3\.amazonaws\.com/.*"),
            lambda r: r.fulfill(status=404, headers={"Access-Control-Allow-Origin": "*"}, body=""))
    res = h.evaluate("(u) => sw(u, { mode: 'cors' })", S3.format(4))
    assert res["status"] == 404
    assert h.evaluate("() => cacheUrls(IMG)") == []


def test_quota_errors_do_not_break_responses(h):
    h.evaluate("() => { Cache.prototype.put = () => Promise.reject(new DOMException('full', 'QuotaExceededError')); }")
    warnings = []
    h.on("console", lambda m: warnings.append(m.text) if m.type == "warning" else None)
    res = h.evaluate("(u) => sw(u, { mode: 'cors' })", S3.format(5))
    assert res["type"] == "cors" and res["status"] == 200
    assert h.evaluate("() => cacheUrls(IMG)") == []
    h.wait_for_timeout(50)
    assert any("cache put failed" in w for w in warnings)


# ---------- iNaturalist API ----------

def test_api_is_network_first_with_offline_fallback(h, net):
    url = API.format(1)
    online = h.evaluate("(u) => sw(u)", url)
    assert online["status"] == 200 and '"total_results": 45' in online["body"]
    net.total = 7  # a fresh network response must win over the cache
    assert '"total_results": 7' in h.evaluate("(u) => sw(u)", url)["body"]
    h.evaluate("() => { __net.offline = true; }")
    assert '"total_results": 7' in h.evaluate("(u) => sw(u)", url)["body"]


def test_api_offline_without_cache_fails(h):
    h.evaluate("() => { __net.offline = true; }")
    err = h.evaluate("(u) => sw(u).then(() => 'ok', (e) => e.message)", API.format(2))
    assert "offline" in err


def test_api_errors_are_not_cached(h, net, allow_http_errors):
    net.status = 500
    assert h.evaluate("(u) => sw(u)", API.format(3))["status"] == 500
    assert h.evaluate("() => cacheUrls(API)") == []


# ---------- app shell ----------

def test_shell_is_stale_while_revalidate(h, base_url):
    url = f"{base_url}/styles.css"
    h.evaluate("""async (u) => { const c = await caches.open(SHELL); await c.put(u, new Response('old')); }""", url)
    assert h.evaluate("(u) => sw(u)", url)["body"] == "old"     # cached copy first...
    fresh = h.evaluate("(u) => sw(u)", url)["body"]               # ...updated in the background
    assert "--brand" in fresh


def test_shell_offline_with_cache_and_ignores_query(h, base_url):
    h.evaluate("() => dispatch('install')")
    h.evaluate("() => { __net.offline = true; }")
    res = h.evaluate("(u) => sw(u)", f"{base_url}/app.js?v=123")
    assert res["status"] == 200 and "lib.js" in res["body"]


def test_non_get_and_unknown_hosts_are_not_intercepted(h, base_url):
    assert h.evaluate("(u) => sw(u, { method: 'POST', body: 'x' })", f"{base_url}/data/species.json") is None
    assert h.evaluate("() => sw('https://example.com/x.png')") is None


# ---------- the real thing ----------

def test_offline_reload_with_real_worker(browser, base_url, groups):
    """Register sw.js for real, go offline, reload: the app must still start."""
    ctx = browser.new_context(base_url=base_url, service_workers="allow")
    try:
        page = ctx.new_page()
        page.goto("/#/about")  # no external images on this page
        page.wait_for_selector("text=What this is")
        page.evaluate("() => navigator.serviceWorker.ready")
        page.wait_for_function("() => caches.has('shell-v2')")
        ctx.set_offline(True)
        page.goto("/#/")
        page.wait_for_selector(".group-card")
        assert page.locator(".group-card").count() == len(groups["groups"])
    finally:
        ctx.close()
