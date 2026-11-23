"""Unit tests for app/lib.js, run in Chromium by importing the module into a page."""
import pytest


@pytest.fixture
def lib(app):
    app.goto("/#/about")
    app.wait_for_selector("text=What this is")

    def call(expr, *args):
        return app.evaluate(f"async (args) => {{ const L = await import('/lib.js'); return ({expr})(...args); }}", list(args))
    return call


@pytest.mark.parametrize("grams,text", [
    (None, "—"), (0, "—"), (7.5, "7.5 g"), (8.0, "8 g"), (19.96, "20 g"), (280, "280 g"),
    (999.4, "999 g"), (1000, "1.0 kg"), (3450, "3.5 kg"), (10000, "10 kg"), (36000, "36 kg"),
])
def test_fmt_mass(lib, grams, text):
    assert lib("L.fmtMass", grams) == text


def test_fmt_len(lib):
    assert lib("L.fmtLen", {"len": 41, "lenMin": 37, "lenMax": 43}) == "37–43 cm"
    assert lib("L.fmtLen", {"len": 41, "lenMin": 41, "lenMax": 41}) == "41 cm"
    assert lib("L.fmtLen", {"len": 41, "lenMin": None, "lenMax": 43}) == "41 cm"
    assert lib("L.fmtLen", {"len": None}) == "—"


def test_esc(lib):
    assert lib("L.esc", "<a href=\"x\">'&'</a>") == "&lt;a href=&quot;x&quot;&gt;&#39;&amp;&#39;&lt;/a&gt;"
    assert lib("L.esc", None) == ""


def test_photo_size(lib):
    assert lib("L.photoSize", "https://h/photos/1/square.jpeg", "large") == "https://h/photos/1/large.jpeg"
    assert lib("L.photoSize", "https://h/photos/1/medium.jpg", "large") == "https://h/photos/1/large.jpg"
    assert lib("L.photoSize", None, "large") == ""


@pytest.mark.parametrize("url,cors", [
    ("https://inaturalist-open-data.s3.amazonaws.com/photos/1/square.jpg", True),
    ("https://images.phylopic.org/images/x/vector.svg", True),
    ("https://static.inaturalist.org/photos/1/square.jpg", False),  # no CORS headers on this host
    ("https://evil.example/inaturalist-open-data.s3.amazonaws.com/x.jpg", False),
    ("", False), ("not a url", False),
])
def test_is_cors_image(lib, url, cors):
    assert lib("L.isCorsImage", url) is cors


def test_img_tag_adds_crossorigin_only_for_cors_hosts(lib):
    s3 = lib("L.imgTag", "https://inaturalist-open-data.s3.amazonaws.com/p/1/square.jpg")
    static = lib("L.imgTag", "https://static.inaturalist.org/p/1/square.jpg")
    assert 'crossorigin="anonymous"' in s3 and 'loading="lazy"' in s3
    assert "crossorigin" not in static
    assert lib("L.imgTag", 'x"><script>', 'alt=""') == '<img src="x&quot;&gt;&lt;script&gt;" alt="">'


def test_set_img_src_switches_crossorigin(lib):
    result = lib("""(a, b) => {
        const img = new Image();
        L.setImgSrc(img, a); const first = img.getAttribute('crossorigin');
        L.setImgSrc(img, b); const second = img.getAttribute('crossorigin');
        return [first, second];
    }""", "https://inaturalist-open-data.s3.amazonaws.com/p/1/large.jpg", "https://static.inaturalist.org/p/2/large.jpg")
    assert result == ["anonymous", None]


SEARCH = """async (q) => {
    const sp = await (await fetch('/data/species.json')).json();
    sp.forEach(L.indexSpecies);
    return L.search(sp, q, 10).map((s) => s.common);
}"""


def test_search_ranks_name_prefix_first_then_popularity(lib):
    res = lib(SEARCH, "raven")
    assert res[0] == "Australian Raven"  # word-prefix match, most observed
    assert {"Little Raven", "Forest Raven"} <= set(res)


def test_search_scientific_family_and_multiword(lib):
    assert lib(SEARCH, "gymnorhina")[0] == "Australian Magpie"
    assert lib(SEARCH, "superb fairy")[0] == "Superb Fairywren"
    honeyeaters = lib(SEARCH, "honeyeater")
    assert len(honeyeaters) == 10  # limit applies
    assert sum("Honeyeater" in n for n in honeyeaters) >= 8  # name matches outrank family-only ones
    assert lib(SEARCH, "  ") == [] and lib(SEARCH, "zzqqxx") == []


def test_sil_dims(lib):
    perched = {"len": 10, "sil": {"w": 200, "h": 100, "pose": "perched"}}
    tall = {"len": 10, "sil": {"w": 50, "h": 100, "pose": "perched"}}
    flight = {"len": 10, "sil": {"w": 200, "h": 100, "pose": "flight"}}
    assert lib("L.silDims", perched, 2) == {"w": 20, "h": 10, "flight": False}
    assert lib("L.silDims", tall, 2) == {"w": 10, "h": 20, "flight": False}
    assert lib("L.silDims", flight, 2) == {"w": 44, "h": 22, "flight": True}  # 2.2x wingspan
    assert lib("L.silDims", {"len": 10, "sil": None}, 1) == {"w": 8, "h": 8, "flight": False}


def test_nearest_benchmarks(lib):
    bench = [{"id": i, "len": l} for i, l in enumerate([13, 15, 20, 25, 33, 41])]
    ids = lambda *a: [b["id"] for b in lib("L.nearestBenchmarks", bench, *a)]
    assert ids(22, None) == [1, 2, 3, 4]
    assert ids(20, 2) == [0, 1, 3, 4]       # excludes the species itself; ties count as "below"
    assert ids(5, None) == [0, 1]           # nothing smaller
    assert ids(100, None, 1, 1) == [5]


def test_is_hybrid(lib):
    assert lib("L.isHybrid", {"sci": "Anas superciliosa × platyrhynchos"}) is True
    assert lib("L.isHybrid", {"sci": "Anas superciliosa"}) is False


# ---------- ID key ----------

TRAITS = [{"key": "bill", "label": "Bill colour", "tier": 0}, {"key": "eye", "label": "Eye", "tier": 0},
          {"key": "call", "label": "Call", "tier": 2}]


def sp_(i, name, length=None):
    return {"id": i, "common": name, "len": length}


def test_mark_leaves_expand_plumages_with_species_defaults(lib):
    species = [sp_(1, "Wren"), sp_(2, "Robin"), sp_(3, "No marks")]
    marks = {"1": {"t": {"call": "trill"}, "p": {"male": {"bill": "black"}, "female": {"bill": "brown"}}, "ok": False},
             "2": {"t": {"bill": "black"}, "ok": True}}
    leaves = lib("(sp, m) => L.markLeaves(sp, m).map((l) => [l.label, l.plumage, l.t, l.ok])", species, marks)
    assert leaves == [["Wren (male)", "male", {"call": "trill", "bill": "black"}, False],
                      ["Wren (female)", "female", {"call": "trill", "bill": "brown"}, False],
                      ["Robin", "", {"bill": "black"}, True]]


KEY_TO_TEXT = """(leaves, traits) => {
  const walk = (n) => n.trait
    ? { q: n.trait.label, a: n.branches.map((b) => [b.value, b.unknown.map((l) => l.label), walk(b.node)]) }
    : n.leaves.map((l) => l.label);
  return walk(L.buildKey(leaves.map((l) => ({ s: { len: l.len || null }, label: l.label, t: l.t })), traits));
}"""


def leaf(label, length=None, **t):
    return {"label": label, "len": length, "t": t}


def test_key_picks_the_most_even_split_and_is_case_insensitive(lib):
    leaves = [leaf("A", bill="black", eye="red"), leaf("B", bill="Black", eye="white"),
              leaf("C", bill="pale", eye="yellow")]
    # eye splits 1/1/1, bill only 2/1
    assert lib(KEY_TO_TEXT, leaves, TRAITS) == {"q": "Eye", "a": [["red", [], ["A"]], ["white", [], ["B"]], ["yellow", [], ["C"]]]}
    two = [leaf("A", bill="black"), leaf("B", bill="BLACK "), leaf("C", bill="pale")]
    assert lib(KEY_TO_TEXT, two, TRAITS)["a"][0][:2] == ["black", []]


def test_key_prefers_visible_marks_over_call_on_equal_splits(lib):
    leaves = [leaf("A", bill="black", call="x"), leaf("B", bill="pale", call="y")]
    assert lib(KEY_TO_TEXT, leaves, TRAITS)["q"] == "Bill colour"


def test_key_sends_unknown_leaves_down_every_branch(lib):
    leaves = [leaf("A", eye="red"), leaf("B", eye="white"), leaf("C", bill="black"), leaf("D", bill="pale")]
    key = lib(KEY_TO_TEXT, leaves, TRAITS)
    # every trait has 2 unknowns; the first equally good one (bill) is used, A and B under each answer
    assert key["q"] == "Bill colour"
    (v1, unk1, sub1), (v2, unk2, sub2) = key["a"]
    assert unk1 == unk2 == ["A", "B"]
    assert sub1["q"] == "Eye"


def test_key_stops_when_nothing_separates(lib):
    assert lib(KEY_TO_TEXT, [leaf("A", bill="black"), leaf("B", bill="black")], TRAITS) == ["A", "B"]
    assert lib(KEY_TO_TEXT, [leaf("A")], TRAITS) == ["A"]


def test_key_splits_on_size_only_with_a_clear_gap(lib):
    big_gap = [leaf("Small", 20, bill="black"), leaf("Big", 30, bill="black")]
    assert lib(KEY_TO_TEXT, big_gap, TRAITS) == {"q": "Size", "a": [
        ["smaller (up to 20 cm)", [], ["Small"]], ["larger (30 cm or more)", [], ["Big"]]]}
    close = [leaf("A", 20, bill="black"), leaf("B", 24, bill="black")]
    assert lib(KEY_TO_TEXT, close, TRAITS) == ["A", "B"]


def test_compare_rows_flag_differences_first(lib):
    leaves = [{"t": {"bill": "black", "eye": "red"}}, {"t": {"bill": "black", "eye": "White"}}]
    rows = lib("(l, t) => L.compareRows(l, t).map((r) => [r.key, r.cells, r.differs])", leaves, TRAITS)
    assert rows == [["eye", ["red", "White"], True], ["bill", ["black", "black"], False]]
