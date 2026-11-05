"""Browser test fixtures: a local static server for app/, and a fake network.

Every request that isn't to the local server is answered by FakeNet (iNaturalist API, photo hosts,
PhyloPic) or aborted, so the suite never touches the real internet. The fake image hosts mirror the
real CORS headers: S3 and PhyloPic send Access-Control-Allow-Origin, static.inaturalist.org doesn't.
"""
import base64, functools, http.server, json, os, threading, time
from urllib.parse import parse_qs, urlparse

import pytest

from paths import APP

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'
CORS_HOSTS = {"inaturalist-open-data.s3.amazonaws.com", "images.phylopic.org"}
NO_CORS_HOSTS = {"static.inaturalist.org"}


def pytest_collection_modifyitems(items):
    for item in items:
        if "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


@pytest.fixture(scope="session")
def base_url():
    handler = functools.partial(_QuietHandler, directory=APP)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    # "localhost" (not 127.0.0.1) so it's a secure context: service workers and CacheStorage work
    yield f"http://localhost:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, base_url):
    # Playwright can't route requests made by a service worker, so app tests run without one;
    # test_sw.py exercises the worker's logic directly.
    return {**browser_context_args, "base_url": base_url, "service_workers": "block",
            "viewport": {"width": 420, "height": 860}}


@pytest.fixture(scope="session")
def species():
    with open(os.path.join(APP, "data", "species.json")) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sp(species):
    """Look up a species by common name."""
    by_name = {s["common"]: s for s in species}
    return by_name.__getitem__


@pytest.fixture(scope="session")
def groups():
    with open(os.path.join(APP, "data", "groups.json")) as f:
        return json.load(f)


class FakeNet:
    def __init__(self, base_url):
        self.base_url = base_url
        self.total = 45          # observations per taxon; 30 per page
        self.status = 200        # set to e.g. 404 to make the observations API fail
        self.dead_on_page1 = 0   # mark this many page-1 observations as dead (gallery skips them)
        self.api_delay = 0       # seconds to hold each observations response
        self.api_calls = []      # parsed query params of every observations request
        self.image_requests = []
        self.blocked = []

    def observations(self, q):
        page, per = int(q["page"]), int(q["per_page"])
        n = max(0, min(per, self.total - (page - 1) * per))
        results = []
        for j in range(n):
            oid = int(q["taxon_id"]) * 1000 + page * 100 + j
            host = "inaturalist-open-data.s3.amazonaws.com" if j % 2 == 0 else "static.inaturalist.org"
            annotations = [{"controlled_attribute_id": 1, "controlled_value_id": 2}]  # adult
            if page == 1 and (j == 3 or j < self.dead_on_page1):
                annotations.append({"controlled_attribute_id": 17, "controlled_value_id": 19})  # dead
            if page == 1 and j == 5:
                annotations.append({"controlled_attribute_id": 22, "controlled_value_id": 25})  # feather
            results.append({
                "id": oid, "observed_on": "2026-01-02", "place_guess": f"Place {j}",
                "annotations": annotations,
                "photos": [{"url": f"https://{host}/photos/{oid}/square.jpg", "attribution": f"(c) Observer {oid}"}],
            })
        return {"total_results": self.total, "page": page, "per_page": per, "results": results}

    def handle(self, route):
        url = urlparse(route.request.url)
        if route.request.url.startswith(self.base_url):
            return route.continue_()
        if url.hostname == "api.inaturalist.org" and url.path == "/v1/observations":
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            self.api_calls.append(q)
            if self.api_delay:
                time.sleep(self.api_delay)
            if self.status != 200:
                return route.fulfill(status=self.status, body="{}", headers={"Access-Control-Allow-Origin": "*"})
            return route.fulfill(status=200, content_type="application/json",
                                 headers={"Access-Control-Allow-Origin": "*"}, body=json.dumps(self.observations(q)))
        if url.hostname in CORS_HOSTS | NO_CORS_HOSTS:
            self.image_requests.append(route.request.url)
            svg = url.path.endswith(".svg")
            headers = {"Content-Type": "image/svg+xml" if svg else "image/png"}
            if url.hostname in CORS_HOSTS:
                headers["Access-Control-Allow-Origin"] = "*"
            return route.fulfill(status=200, headers=headers, body=SVG if svg else PNG)
        self.blocked.append(route.request.url)
        return route.abort()


@pytest.fixture
def net(context, base_url):
    fake = FakeNet(base_url)
    context.route("**/*", fake.handle)
    return fake


class ErrorLog(list):
    allow_http = False  # set by the allow_http_errors fixture

    def unexpected(self):
        return [e for e in self if not (self.allow_http and e.startswith("Failed to load resource"))]


@pytest.fixture
def console_errors(page):
    """Collects console errors and uncaught exceptions; `app` asserts none are unexpected."""
    errors = ErrorLog()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    return errors


@pytest.fixture
def allow_http_errors(console_errors):
    """For tests that deliberately return HTTP errors: the browser logs each one to the console."""
    console_errors.allow_http = True


@pytest.fixture
def app(page, net, console_errors):
    """The app page with fake network; fails the test on any console error or unexpected request."""
    yield page
    assert console_errors.unexpected() == [], console_errors
    assert net.blocked == [], f"unexpected external requests: {net.blocked}"
