"""Checks on the committed app/data/*.json that the app relies on."""
import json, os, re
from urllib.parse import urlparse

import pytest

from paths import APP

MAX_COMPARE = 5  # app.js


def load(name):
    with open(os.path.join(APP, "data", name)) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def species():
    return load("species.json")


@pytest.fixture(scope="module")
def by_id(species):
    return {s["id"]: s for s in species}


@pytest.fixture(scope="module")
def groups():
    return load("groups.json")


def js_string_list(path, const):
    """The string literals in `const NAME = [...]` from a JS file."""
    with open(os.path.join(APP, path)) as f:
        m = re.search(rf"const {const} = \[(.*?)\];", f.read(), re.S)
    assert m, f"{const} not found in {path}"
    return re.findall(r"'([^']+)'", m.group(1))


def test_species_ids_unique(species):
    assert len({s["id"] for s in species}) == len(species)


def test_species_required_fields(species):
    for s in species:
        assert isinstance(s["id"], int) and s["sci"] and s["common"], s
        assert s["obs"] >= 1, s


def test_lengths_consistent(species):
    for s in species:
        if s["len"]:
            assert 5 <= s["len"] <= 250, s["common"]
            if s["lenMin"]:
                assert s["lenMin"] <= s["len"], s["common"]
            if s["lenMax"]:
                assert s["len"] <= s["lenMax"], s["common"]


def test_most_species_have_length_and_silhouette(species):
    assert sum(bool(s["len"]) for s in species) / len(species) > 0.75
    assert all(s["sil"] for s in species if s["len"]), "every species with a length should get a silhouette"


def test_silhouettes_well_formed(species):
    for s in species:
        sil = s["sil"]
        if not sil:
            continue
        assert sil["w"] > 0 and sil["h"] > 0
        assert sil["level"] in {"species", "genus", "family", "order"}
        assert sil["pose"] in {"perched", "flight"}
        assert sil["url"].startswith("https://images.phylopic.org/") and sil["url"].endswith(".svg")
        assert sil["licUrl"].startswith("https://") and sil["lic"] and sil["by"]
        assert "NC" not in sil["lic"] or sil["lic"].startswith("CC BY-NC")


def test_groups_reference_real_species(groups, by_id):
    assert len(groups["groups"]) >= 40
    for g in groups["groups"]:
        assert 2 <= len(g["ids"]) <= MAX_COMPARE, g["title"]  # compare view shows at most 5
        assert len(set(g["ids"])) == len(g["ids"]), g["title"]
        assert all(i in by_id for i in g["ids"]), g["title"]
        assert g["tips"] and g["cat"], g["title"]


def test_benchmarks_have_lengths_and_span_the_size_range(groups, by_id):
    lens = [by_id[i]["len"] for i in groups["benchmarks"]]
    assert all(lens)
    assert min(lens) <= 15 and max(lens) >= 150  # fairy-wren ... emu


def test_every_image_host_is_handled_by_the_service_worker(species):
    """A photo or silhouette host the SW doesn't know about won't be cached for offline use."""
    sw_hosts = set(js_string_list("sw.js", "IMAGE_HOSTS"))
    hosts = {urlparse(s["photo"]).hostname for s in species if s["photo"]}
    hosts |= {urlparse(s["sil"]["url"]).hostname for s in species if s["sil"]}
    assert hosts <= sw_hosts


def test_cors_hosts_are_a_subset_of_sw_image_hosts():
    assert set(js_string_list("lib.js", "CORS_IMAGE_HOSTS")) <= set(js_string_list("sw.js", "IMAGE_HOSTS"))


def test_shell_files_exist():
    for f in js_string_list("sw.js", "SHELL_FILES"):
        if f != "./":
            assert os.path.isfile(os.path.join(APP, f)), f


def test_every_local_module_is_precached():
    """An ES module import missing from SHELL_FILES breaks the app offline."""
    shell = set(js_string_list("sw.js", "SHELL_FILES"))
    for name in os.listdir(APP):
        if name.endswith(".js") and name != "sw.js":
            assert name in shell, f"{name} is not in sw.js SHELL_FILES"


def test_manifest_icons_exist():
    with open(os.path.join(APP, "manifest.webmanifest")) as f:
        manifest = json.load(f)
    for icon in manifest["icons"]:
        assert os.path.isfile(os.path.join(APP, icon["src"])), icon["src"]
