"""tools/phylopic.py: paging must follow `next` links (the old fetchers stopped after page 0)."""
import io, json, urllib.error

import phylopic as pp


class FakeAPI:
    """Serves canned responses by path and records every request."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def __call__(self, path):
        self.calls.append(path)
        r = self.routes[path]
        if isinstance(r, Exception):
            raise r
        return r


def image_page(uuids, next_path=None):
    links = {"items": [{"href": f"/images/{u}?build=562"} for u in uuids]}
    if next_path:
        links["next"] = {"href": next_path}
    return {"_links": links}


def http_404():
    return urllib.error.HTTPError("u", 404, "Not Found", {}, io.BytesIO(b""))


def test_uuid_of():
    assert pp.uuid_of("/images/abc-123?build=562") == "abc-123"


def test_pages_follows_next_until_absent():
    api = FakeAPI({"/a": {"_links": {"next": {"href": "/b"}}}, "/b": {"_links": {"next": {"href": "/c"}}}, "/c": {"_links": {}}})
    assert len(list(pp.pages("/a", api, pause=0))) == 3
    assert api.calls == ["/a", "/b", "/c"]


def test_clade_image_uuids_collects_every_page():
    nodes = f"/nodes?build={pp.BUILD}&filter_name=accipitridae&page=0"
    first = f"/images?build={pp.BUILD}&filter_clade=node-1&page=0"
    api = FakeAPI({
        nodes: {"_links": {"items": [{"href": "/nodes/node-1?build=562"}]}},
        first: image_page([f"a{i}" for i in range(48)], "/p1"),
        "/p1": image_page([f"b{i}" for i in range(48)], "/p2"),
        "/p2": image_page(["c0", "c1"]),
    })
    uuids = pp.clade_image_uuids("Accipitridae", api, pause=0)
    assert len(uuids) == 98 and uuids[0] == "a0" and uuids[-1] == "c1"


def test_clade_without_node_is_empty():
    api = FakeAPI({f"/nodes?build={pp.BUILD}&filter_name=foo&page=0": {"_links": {"items": []}}})
    assert pp.clade_image_uuids("Foo", api, pause=0) == []


def test_clade_404_is_empty_not_an_error():
    api = FakeAPI({f"/nodes?build={pp.BUILD}&filter_name=foo&page=0": http_404()})
    logs = []
    assert pp.fetch_clades(["Foo"], api, pause=0, log=logs.append) == {"Foo": []}
    assert logs == []


def test_fetch_clades_logs_real_errors_and_continues():
    ok_nodes = f"/nodes?build={pp.BUILD}&filter_name=good&page=0"
    api = FakeAPI({
        f"/nodes?build={pp.BUILD}&filter_name=bad&page=0": RuntimeError("boom"),
        ok_nodes: {"_links": {"items": [{"href": "/nodes/n?x"}]}},
        f"/images?build={pp.BUILD}&filter_clade=n&page=0": image_page(["x"]),
    })
    logs = []
    assert pp.fetch_clades(["Bad", "Good"], api, pause=0, log=logs.append) == {"Bad": [], "Good": ["x"]}
    assert logs == ["Bad: boom"]


def test_all_images_reads_embedded_items_across_pages():
    first = (f"/images?build={pp.BUILD}&filter_clade={pp.AVES}&page=0"
             "&embed_items=true&embed_specificNode=true&embed_contributor=true")
    api = FakeAPI({
        first: {"_embedded": {"items": [{"uuid": "1"}]}, "_links": {"next": {"href": "/n"}}},
        "/n": {"_embedded": {"items": [{"uuid": "2"}]}, "_links": {}},
    })
    assert [x["uuid"] for x in pp.all_images(api, pause=0)] == ["1", "2"]


def test_clade_names():
    anc = {"1": {"family": ["Corvidae", "Crows"]}, "2": {"family": ["Anatidae", None]},
           "3": {"family": ["Corvidae", "Crows"]}, "4": {"family": None}}
    assert pp.clade_names(anc, "family") == ["Anatidae", "Corvidae"]


def test_committed_clade_lists_are_not_truncated_at_one_page():
    """Regression: with page=0 only, every list was capped at 48 uuids."""
    from paths import ROOT
    import os
    with open(os.path.join(ROOT, "data-src", "pp", "ord.json")) as f:
        orders = json.load(f)
    assert max(map(len, orders.values())) > 48
