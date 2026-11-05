"""End-to-end flows through the real app (index.html + app.js) with a fake iNaturalist API.

The `app` fixture fails any test that logs a console error, throws, or makes an unexpected
external request - which also catches CORS failures on images.
"""
import re

from playwright.sync_api import expect

# FakeNet serves 45 observations per taxon (30 + 15); page 1 has one dead bird and one feather,
# which the gallery must skip.
PAGE1_PHOTOS = 28
ALL_PHOTOS = 43


def open_species(app, s):
    app.goto(f"/#/s/{s['id']}")
    expect(app.locator("h1")).to_have_text(s["common"])


# ---------- home & search ----------

def test_home_lists_every_group_by_category(app, groups):
    app.goto("/")
    expect(app.locator(".group-card")).to_have_count(len(groups["groups"]))
    cats = list(dict.fromkeys(g["cat"] for g in groups["groups"]))
    expect(app.locator(".cat-title")).to_have_text(cats)
    expect(app.locator("[data-nav=home]")).to_have_class(re.compile("active"))


def test_search_shows_results_and_hides_groups(app):
    app.goto("/")
    app.fill("#q", "raven")
    expect(app.locator("#qres li").first).to_contain_text("Australian Raven")
    expect(app.locator("#groups")).to_be_hidden()
    app.fill("#q", "zzqqxx")
    expect(app.locator("#qres")).to_have_text("No matches")
    app.fill("#q", "")
    expect(app.locator("#groups")).to_be_visible()


def test_search_result_opens_species(app, sp):
    app.goto("/")
    app.fill("#q", "magpie")
    app.locator("#qres a", has_text="Australian Magpie").first.click()
    expect(app).to_have_url(re.compile(rf"#/s/{sp('Australian Magpie')['id']}$"))
    expect(app.locator("h1")).to_have_text("Australian Magpie")


# ---------- species page ----------

def test_species_page_stats_and_size_ladder(app, sp):
    magpie = sp("Australian Magpie")
    open_species(app, magpie)
    expect(app.locator(".stat-line")).to_contain_text("37–43 cm")
    expect(app.locator(".stat-line")).to_contain_text("280 g")
    rungs = app.locator(".ladder .rung")
    expect(rungs).to_have_count(5)  # the species + 2 smaller + 2 larger benchmark birds
    labels = rungs.locator(".rung-label b").all_inner_texts()
    assert "Australian Magpie" in labels and len(set(labels)) == 5
    expect(app.locator(".sil.ref")).to_have_count(4)
    expect(app.locator(".scalebar")).to_contain_text("cm")
    expect(app.locator(".credit")).to_contain_text("Garnett")


def test_ladder_rungs_are_sorted_by_length(app, sp, species):
    open_species(app, sp("Australian Magpie"))
    names = app.locator(".ladder .rung-label b").all_inner_texts()
    by_name = {s["common"]: s["len"] for s in species}
    lens = [by_name[n] for n in names]
    assert lens == sorted(lens)


def test_ladder_fits_without_horizontal_scroll(app, sp):
    open_species(app, sp("Australian Magpie"))
    wrap = app.locator(".ladder-wrap")
    assert wrap.evaluate("(el) => el.scrollWidth <= el.clientWidth + 1")


def test_species_without_length_explains_why(app, species):
    s = next(x for x in species if not x["len"])
    open_species(app, s)
    expect(app.locator(".card").first).to_contain_text("No body-length data")


def test_unknown_species_id(app):
    app.goto("/#/s/999999999")
    expect(app.locator("main")).to_contain_text("Species not found")


def test_gallery_loads_pages_and_skips_dead_and_non_organism(app, net, sp):
    open_species(app, sp("Australian Magpie"))
    grid = app.locator(".gallery button")
    expect(grid).to_have_count(PAGE1_PHOTOS)
    app.locator(".sentinel").scroll_into_view_if_needed()
    expect(grid).to_have_count(ALL_PHOTOS)
    expect(app.locator(".loading")).to_have_text("45 observations")
    assert [c["page"] for c in net.api_calls] == ["1", "2"]
    first = net.api_calls[0]
    assert first["taxon_id"] == str(sp("Australian Magpie")["id"])
    assert first["place_id"] == "6744" and first["quality_grade"] == "research" and first["order_by"] == "votes"


def test_gallery_images_use_crossorigin_only_where_supported(app, sp):
    open_species(app, sp("Australian Magpie"))
    expect(app.locator(".gallery button")).to_have_count(PAGE1_PHOTOS)
    imgs = app.locator(".gallery img")
    for i in range(4):
        img = imgs.nth(i)
        src = img.get_attribute("src")
        if "s3.amazonaws.com" in src:
            assert img.get_attribute("crossorigin") == "anonymous"
        else:
            assert img.get_attribute("crossorigin") is None
    # every visible image actually decoded (a CORS mistake would leave naturalWidth at 0)
    imgs.first.scroll_into_view_if_needed()
    app.wait_for_function("() => [...document.querySelectorAll('.gallery img')].slice(0, 6).every((i) => i.complete && i.naturalWidth > 0)")


def test_gallery_filter_and_order_chips_requery(app, net, sp):
    open_species(app, sp("Superb Fairywren"))
    expect(app.locator(".gallery button")).to_have_count(PAGE1_PHOTOS)
    app.click("[data-filter=female]")
    expect(app.locator("[data-filter=female]")).to_have_attribute("aria-pressed", "true")
    expect(app.locator(".gallery button")).to_have_count(PAGE1_PHOTOS)
    assert (net.api_calls[-1]["term_id"], net.api_calls[-1]["term_value_id"]) == ("9", "10")
    app.click("[data-order=created_at]")
    assert net.api_calls[-1]["order_by"] == "created_at"
    assert net.api_calls[-1]["term_value_id"] == "10"  # filter is kept when changing order


def test_gallery_error_is_shown(app, net, sp, allow_http_errors):
    net.status = 404
    open_species(app, sp("Australian Magpie"))
    expect(app.locator(".loading")).to_have_text("Couldn't load photos: HTTP 404")


def test_gallery_with_no_results(app, net, sp):
    net.total = 0
    open_species(app, sp("Australian Magpie"))
    expect(app.locator(".loading")).to_have_text("No photos match this filter.")


# ---------- lightbox ----------

def test_lightbox_navigation_and_close_via_history(app, sp):
    magpie = sp("Australian Magpie")
    open_species(app, magpie)
    app.locator(".gallery button").nth(2).click()
    lb = app.locator("#lightbox")
    expect(lb).to_be_visible()
    expect(lb.locator(".lb-caption")).to_contain_text("3/")
    expect(lb.locator(".lb-caption")).to_contain_text("Australian Magpie")
    expect(lb.locator(".lb-caption")).to_contain_text("Tagged: adult")
    app.keyboard.press("ArrowRight")
    expect(lb.locator(".lb-caption")).to_contain_text("4/")
    app.keyboard.press("ArrowLeft")
    app.keyboard.press("ArrowLeft")
    expect(lb.locator(".lb-caption")).to_contain_text("2/")
    app.keyboard.press("Escape")
    expect(lb).to_be_hidden()
    expect(app.locator("h1")).to_have_text("Australian Magpie")  # closing doesn't leave the page
    expect(app).to_have_url(re.compile(rf"#/s/{magpie['id']}$"))


def test_lightbox_closes_on_browser_back(app, sp):
    open_species(app, sp("Australian Magpie"))
    app.locator(".gallery button").first.click()
    expect(app.locator("#lightbox")).to_be_visible()
    app.go_back()
    expect(app.locator("#lightbox")).to_be_hidden()
    expect(app.locator("h1")).to_have_text("Australian Magpie")


def test_lightbox_large_image_crossorigin_matches_host(app, sp):
    open_species(app, sp("Australian Magpie"))
    app.locator(".gallery button").nth(0).click()  # even index -> S3 host in FakeNet
    big = app.locator("#lightbox .lb-stage img")
    expect(big).to_have_attribute("src", re.compile(r"s3\.amazonaws\.com/.*/large\."))
    expect(big).to_have_attribute("crossorigin", "anonymous")
    app.keyboard.press("ArrowRight")  # odd index -> static.inaturalist.org, which has no CORS
    expect(big).to_have_attribute("src", re.compile(r"static\.inaturalist\.org/.*/large\."))
    assert big.get_attribute("crossorigin") is None
    app.wait_for_function("() => { const i = document.querySelector('#lightbox img'); return i.complete && i.naturalWidth > 0; }")


# ---------- compare ----------

def test_group_card_opens_comparison(app, groups, species):
    g = groups["groups"][0]
    by_id = {s["id"]: s for s in species}
    app.goto("/")
    app.locator(".group-card", has_text=g["title"]).click()
    expect(app.locator("h1")).to_have_text(g["title"])
    expect(app.locator(".cmp-chips .chip a")).to_have_text([by_id[i]["common"] for i in g["ids"]])
    expect(app.locator("table.stats tr")).to_have_count(len(g["ids"]) + 1)
    expect(app.locator(".tips li")).to_have_count(len(g["tips"]))
    expect(app.locator("[data-strip]")).to_have_count(len(g["ids"]))
    for i in range(len(g["ids"])):
        expect(app.locator(f"[data-strip='{i}'] .strip button").first).to_be_visible()


def test_compare_ratios(app, sp):
    a, b = sp("Australian Magpie"), sp("Magpie-lark")
    app.goto(f"/#/c/{a['id']},{b['id']}")
    expect(app.locator("table.stats")).to_contain_text(f"{a['len'] / b['len']:.2f}× longer")
    expect(app.locator("table.stats")).to_contain_text(f"{a['mass'] / b['mass']:.1f}× heavier")


def test_reference_birds_toggle(app, sp):
    a, b = sp("Australian Magpie"), sp("Magpie-lark")
    app.goto(f"/#/c/{a['id']},{b['id']}")
    n = app.locator("#ladder .rung").count()
    assert n > 2
    app.click("#refs")
    expect(app.locator("#ladder .rung")).to_have_count(2)
    app.click("#refs")
    expect(app.locator("#ladder .rung")).to_have_count(n)


def test_remove_species_from_comparison(app, groups):
    g = next(x for x in groups["groups"] if len(x["ids"]) == 3)
    app.goto(f"/#/c/{','.join(map(str, g['ids']))}?g={groups['groups'].index(g)}")
    expect(app.locator("h1")).to_have_text(g["title"])
    app.locator(f"[data-rm='{g['ids'][0]}']").click()
    expect(app).to_have_url(re.compile(rf"#/c/{g['ids'][1]},{g['ids'][2]}$"))  # group title dropped
    expect(app.locator(".cmp-chips .chip a")).to_have_count(2)
    expect(app.locator("main h1")).to_have_count(0)


def test_compare_from_scratch_with_picker(app, sp):
    app.goto("/")
    app.click("[data-nav=compare]")
    expect(app.locator("main")).to_contain_text("Pick 2–5 birds")
    for name in ("Little Raven", "Australian Raven"):
        app.click("#add")
        expect(app.locator("#picker")).to_be_visible()
        app.fill("#picker-input", name)
        app.locator("#picker-results button", has_text=name).first.click()
        expect(app.locator("#picker")).to_be_hidden()
    expect(app.locator(".cmp-chips .chip a")).to_have_text(["Little Raven", "Australian Raven"])
    expect(app.locator("#ladder .rung").first).to_be_visible()
    # the picker hides species already in the comparison
    app.click("#add")
    app.fill("#picker-input", "raven")
    expect(app.locator("#picker-results")).not_to_contain_text("Little Raven")
    app.click("#picker [data-close]")
    expect(app.locator("#picker")).to_be_hidden()
    expect(app.locator(".cmp-chips .chip a")).to_have_count(2)


def test_compare_caps_at_five_species(app, groups, species):
    ids = [s["id"] for s in species[:7]]
    app.goto(f"/#/c/{','.join(map(str, ids))}")
    expect(app.locator(".cmp-chips .chip a")).to_have_count(5)
    expect(app.locator("#add")).to_have_count(0)


def test_species_page_compare_any_uses_picker(app, sp):
    magpie, currawong = sp("Australian Magpie"), sp("Pied Currawong")
    open_species(app, magpie)
    app.click("#cmp-any")
    app.fill("#picker-input", "pied currawong")
    app.locator("#picker-results button", has_text="Pied Currawong").first.click()
    expect(app).to_have_url(re.compile(rf"#/c/{magpie['id']},{currawong['id']}$"))


# ---------- about & offline-related markup ----------

def test_about_page_counts(app, species, groups):
    app.goto("/#/about")
    expect(app.locator("main")).to_contain_text(f"{len(species)} species · {len(groups['groups'])} confusion groups")


def test_species_thumbnails_use_crossorigin_only_where_supported(app):
    app.goto("/")
    app.fill("#q", "a")
    imgs = app.locator("#qres img")
    expect(imgs.first).to_be_visible()
    for img in imgs.all():
        src = img.get_attribute("src")
        expected = "anonymous" if "s3.amazonaws.com" in src else None
        assert img.get_attribute("crossorigin") == expected, src
