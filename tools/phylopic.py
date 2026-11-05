#!/usr/bin/env python3
"""Fetch PhyloPic bird silhouette metadata into data-src/pp/.

Usage:
  python3 tools/phylopic.py all    <out_dir>   # every Aves image (embedded)   -> <out_dir>/pp/all.json
  python3 tools/phylopic.py family <out_dir>   # image uuids per iNat family   -> <out_dir>/pp/fam.json
  python3 tools/phylopic.py order  <out_dir>   # image uuids per iNat order    -> <out_dir>/pp/ord.json

family/order read <out_dir>/inat_anc.json (from fetch_anc.py) for the clade names.
Every listing follows the API's `next` links, so large clades are not truncated
to the first page.
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://api.phylopic.org"
BUILD = 562  # PhyloPic data build; bump when the API starts rejecting it
AVES = "667b8664-5dd7-487e-ba56-c6c5c95055a2"
HEADERS = {"User-Agent": "BirdID-personal-app"}
PAUSE = 0.3


def http_get(path):
    req = urllib.request.Request(API + path, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def uuid_of(href):
    """'/images/<uuid>?build=562' -> '<uuid>'"""
    return href.split("/")[2].split("?")[0]


def pages(path, get=http_get, pause=PAUSE):
    """Yield each page of a paged listing, starting at `path` and following `next`."""
    while path:
        d = get(path)
        yield d
        path = (d.get("_links", {}).get("next") or {}).get("href")
        if path and pause:
            time.sleep(pause)


def all_images(get=http_get, pause=PAUSE):
    path = (f"/images?build={BUILD}&filter_clade={AVES}&page=0"
            "&embed_items=true&embed_specificNode=true&embed_contributor=true")
    out = []
    for d in pages(path, get, pause):
        out += d.get("_embedded", {}).get("items", [])
    return out


def clade_image_uuids(name, get=http_get, pause=PAUSE):
    """All image uuids under the PhyloPic node whose name matches `name` (e.g. 'Accipitridae')."""
    try:
        d = get(f"/nodes?build={BUILD}&filter_name={urllib.parse.quote(name.lower())}&page=0")
    except urllib.error.HTTPError as e:
        if e.code == 404:  # the API answers 404 when no node has that name
            return []
        raise
    items = d.get("_links", {}).get("items", [])
    if not items:
        return []
    node = uuid_of(items[0]["href"])
    out = []
    for page in pages(f"/images?build={BUILD}&filter_clade={node}&page=0", get, pause):
        out += [uuid_of(x["href"]) for x in page.get("_links", {}).get("items", [])]
    return out


def clade_names(anc, rank):
    """Sorted unique scientific names at `rank` ('family' / 'order') from inat_anc.json."""
    return sorted({v[rank][0] for v in anc.values() if v.get(rank)})


def fetch_clades(names, get=http_get, pause=PAUSE, log=print):
    res = {}
    for n in names:
        try:
            res[n] = clade_image_uuids(n, get, pause)
        except Exception as e:  # keep going; a missing clade just means no fallback silhouette
            res[n] = []
            log(f"{n}: {e}")
    return res


def main(argv):
    if len(argv) != 3 or argv[1] not in ("all", "family", "order"):
        sys.exit(__doc__)
    kind, out_dir = argv[1], argv[2]
    os.makedirs(os.path.join(out_dir, "pp"), exist_ok=True)
    if kind == "all":
        data = all_images()
        print(len(data), "images")
        fname = "all.json"
    else:
        with open(os.path.join(out_dir, "inat_anc.json")) as f:
            anc = json.load(f)
        data = fetch_clades(clade_names(anc, kind))
        print(len(data), kind, "|", sum(map(len, data.values())), "images |",
              "none for:", [k for k, v in data.items() if not v])
        fname = "fam.json" if kind == "family" else "ord.json"
    with open(os.path.join(out_dir, "pp", fname), "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main(sys.argv)
