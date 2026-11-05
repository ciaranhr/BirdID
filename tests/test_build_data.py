"""Unit tests for tools/build_data.py, plus a check that the committed app/data is up to date."""
import filecmp, os

import pytest

import build_data as bd


# ---------- helpers ----------

def test_norm_strips_everything_but_letters():
    assert bd.norm("Black-faced Cuckoo-shrike") == "blackfacedcuckooshrike"
    assert bd.norm(None) == ""


@pytest.mark.parametrize("v,expected", [("12.5", 12.5), ("0", None), ("-3", None), ("", None), (None, None), ("n/a", None)])
def test_num_only_accepts_positive_numbers(v, expected):
    assert bd.num(v) == expected


# ---------- Garnett morphometrics ----------

def row(sci, common, length="20", species="1", extinct="0", lo="", hi="", mass="50"):
    return {
        "17_Species_2": species, "32_Extinct_4": extinct,
        "7_Taxon_scientific_name_CandB_2": sci, "3_Taxon_common_name_2": common,
        "96_Body_length_8": length, "97_Body_length_min_8": lo, "98_Body_length_max_8": hi,
        "99_Body_mass_average_8": mass,
    }


@pytest.fixture
def morph():
    return bd.Morph([
        row("Porphyrio porphyrio", "Purple Swamphen", "45"),
        row("Corvus coronoides", "Australian Raven", "52", lo="50", hi="54", mass="650"),
        row("Corvus coronoides perplexus", "Raven (ssp)", "99", species="0"),
        row("Threskiornis moluccus", "Australian White Ibis", "70"),
        row("Pardalotus striatus", "Striated Pardalote", "10"),
        row("Pardalotus striatellus", "Fake Pardalote", "11"),  # same 5-letter stem "stria"
        row("Dromaius baudinianus", "Kangaroo Island Emu", "140", extinct="1"),
    ])


def test_morph_matches_scientific_name(morph):
    assert morph("Corvus coronoides", "whatever") == {"len": 52.0, "lenMin": 50.0, "lenMax": 54.0, "mass": 650.0}


def test_morph_ignores_subspecies_rows(morph):
    assert morph("Corvus coronoides", "")["len"] == 52.0


def test_morph_uses_synonyms_for_inat_taxonomy(morph):
    assert morph("Porphyrio melanotus", "Australasian Swamphen")["len"] == 45.0


def test_morph_falls_back_to_common_name(morph):
    assert morph("Corvus novus", "Australian Raven")["len"] == 52.0


def test_morph_epithet_stem_fallback_only_when_unambiguous(morph):
    assert morph("Threskiornis moluccanus", "")["len"] == 70.0
    assert morph("Pardalotus striatulus", "") == {}  # two candidates share the stem


def test_morph_skips_extinct_and_unknown(morph):
    assert morph("Dromaius baudinianus", "Kangaroo Island Emu") == {}
    assert morph("Nonexistent bird", "Nobody") == {}


def test_morph_reads_real_csv():
    m = bd.Morph.from_csv(os.path.join(bd.SRC, "Australian_Bird_Data_Version_1.csv"))
    magpie = m("Gymnorhina tibicen", "Australian Magpie")
    assert 35 < magpie["len"] < 45 and magpie["mass"] > 200


# ---------- PhyloPic ----------

def pp_image(uuid, name, size="100x100", lic="https://creativecommons.org/publicdomain/zero/1.0/",
             vector=True, attribution="Someone"):
    links = {
        "license": {"href": lic},
        "specificNode": {"title": name},
        "contributor": {"title": "Contributor"},
    }
    if vector:
        links["vectorFile"] = {"href": f"https://images.phylopic.org/images/{uuid}/vector.svg", "sizes": size}
    return {"uuid": uuid, "_links": links, "attribution": attribution}


def test_pp_record_parses_licence_size_and_credit():
    r = bd.pp_record(pp_image("u1", " Corvus coronoides ", "120.4x80.6",
                              lic="https://creativecommons.org/licenses/by/4.0/", attribution=None))
    assert r["name"] == "Corvus coronoides"
    assert (r["w"], r["h"]) == (120, 81)
    assert r["lic"] == "CC BY 4.0" and r["rank"] == 1
    assert r["by"] == "Contributor"  # falls back when attribution is missing


def test_pp_record_without_vector_is_skipped():
    assert bd.pp_record(pp_image("u1", "Corvus", vector=False)) is None


def test_pp_record_unknown_licence_ranks_last():
    r = bd.pp_record(pp_image("u1", "Corvus", lic="https://example.org/weird"))
    assert r["rank"] == 9 and r["lic"] == "https://example.org/weird"


def make_pp(images, fam=None, ord_=None, flight=(), block=(), perched=()):
    return bd.PhyloPic(images, fam or {}, ord_ or {}, flight=set(flight), block=set(block), perched=set(perched))


def test_best_prefers_reviewed_perched_then_flight_then_unreviewed():
    imgs = [pp_image("unrev", "Corvus a"), pp_image("fly", "Corvus b"), pp_image("perch", "Corvus c")]
    pp = make_pp(imgs, flight={"fly"}, perched={"perch"})
    recs = list(pp.by_uuid.values())
    assert pp.best(recs)["uuid"] == "perch"
    assert pp.best([r for r in recs if r["uuid"] != "perch"])["uuid"] == "fly"


def test_best_never_returns_blocked():
    pp = make_pp([pp_image("bad", "Corvus a")], block={"bad"})
    assert pp.best(list(pp.by_uuid.values())) is None


def test_best_penalises_odd_aspect_ratio_then_restrictive_licence():
    imgs = [
        pp_image("wide", "Corvus a", "400x100"),
        pp_image("nc", "Corvus b", "100x100", lic="https://creativecommons.org/licenses/by-nc/3.0/"),
        pp_image("cc0", "Corvus c", "100x100"),
    ]
    pp = make_pp(imgs)
    assert pp.best(list(pp.by_uuid.values()))["uuid"] == "cc0"
    assert pp.best([pp.by_uuid["wide"], pp.by_uuid["nc"]])["uuid"] == "nc"


def test_silhouette_falls_back_species_genus_family_order():
    imgs = [
        pp_image("sp", "Corvus coronoides"),
        pp_image("gen", "Corvus"),
        pp_image("fam", "Cracticus nigrogularis"),
        pp_image("ord", "Malurus cyaneus"),
    ]
    pp = make_pp(imgs, fam={"Corvidae": ["fam", "missing-uuid"]}, ord_={"Passeriformes": ["ord"]}, flight={"ord"})
    assert pp.silhouette("Corvus coronoides", "Corvus", "Corvidae", "Passeriformes")["level"] == "species"
    assert pp.silhouette("Corvus mellori", "Corvus", "Corvidae", "Passeriformes")["level"] == "genus"
    fam = pp.silhouette("Strepera graculina", "Strepera", "Corvidae", "Passeriformes")
    assert fam["level"] == "family" and fam["uuid"] == "fam" and fam["pose"] == "perched"
    order = pp.silhouette("Pitta versicolor", "Pitta", "Pittidae", "Passeriformes")
    assert order["level"] == "order" and order["pose"] == "flight"
    assert pp.silhouette("Emu x", "Dromaius", None, None) is None


def test_silhouette_output_has_only_public_fields():
    pp = make_pp([pp_image("sp", "Corvus coronoides")])
    sil = pp.silhouette("Corvus coronoides", "Corvus", None, None)
    assert set(sil) == {"uuid", "url", "w", "h", "name", "by", "lic", "licUrl", "level", "pose"}


# ---------- species, groups, benchmarks ----------

def inat_row(tid, sci, common=None, count=10):
    return {"count": count, "taxon": {"id": tid, "name": sci, "preferred_common_name": common,
                                      "default_photo": {"square_url": f"https://x/{tid}/square.jpg"}}}


def test_build_species_merges_sources():
    m = bd.Morph([row("Corvus coronoides", "Australian Raven", "52")])
    pp = make_pp([pp_image("sp", "Corvus coronoides")])
    anc = {"1": {"family": ["Corvidae", "Crows"], "order": ["Passeriformes", None], "genus": ["Corvus", None]}}
    sp = bd.build_species([inat_row(1, "Corvus coronoides", "Australian Raven"), inat_row(2, "Foo bar")], anc, m, pp)
    assert sp[0]["len"] == 52.0 and sp[0]["family"] == "Corvidae" and sp[0]["sil"]["uuid"] == "sp"
    assert sp[1]["common"] == "Foo bar" and sp[1]["len"] is None and sp[1]["family"] is None
    assert bd.species_stats(sp) == {"len": 1, "mass": 1, "sil": {"species": 1, "none": 1}}


def test_build_groups_resolves_aliases_and_reports_problems():
    species = [
        {"id": 1, "common": "Superb Fairywren", "sci": "Malurus cyaneus", "len": 14},
        {"id": 2, "common": "Variegated Fairywren", "sci": "Malurus lamberti", "len": 14},
        {"id": 3, "common": "Emu", "sci": "Dromaius novaehollandiae", "len": None},
    ]
    groups = [
        {"title": "Wrens", "cat": "Small", "tips": ["t"],
         "species": ["Superb Fairy-wren|Superb Fairywren", "Malurus lamberti", "Splendid Fairywren"]},
        {"title": "Lonely", "species": ["Emu"]},
    ]
    out, bench, problems = bd.build_groups(species, groups, ["Superb Fairywren", "Emu", "Dodo"])
    assert out == [{"title": "Wrens", "ids": [1, 2], "tips": ["t"], "cat": "Small"}]  # <2 species -> dropped
    assert bench == [1]  # Emu has no length, Dodo doesn't exist
    assert any("Splendid Fairywren" in p for p in problems)
    assert any("'Emu'" in p for p in problems) and any("Dodo" in p for p in problems)


def test_curated_groups_and_benchmarks_all_resolve(tmp_path):
    """Every name in confusion_groups.py must match a species in the real data."""
    *_, problems = bd.build(out=str(tmp_path))
    assert problems == []


def test_committed_app_data_is_up_to_date(tmp_path):
    """Fails if data-src/ or the tools changed without re-running tools/build_data.py."""
    bd.build(out=str(tmp_path))
    for name in ("species.json", "groups.json"):
        assert filecmp.cmp(tmp_path / name, os.path.join(bd.OUT, name), shallow=False), \
            f"app/data/{name} is stale - run python3 tools/build_data.py"
