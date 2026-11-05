#!/usr/bin/env python3
"""Merge source data into app/data/species.json and app/data/groups.json.

Sources (all in data-src/, fetched by the tools/fetch_*.py scripts):
  - iNaturalist species counts for Aves in Australia (place 6744) + ancestry
  - Garnett et al. 2015 "Australian Bird Data Version 1" (CC0) for body length / mass
  - PhyloPic silhouettes (various CC licences, attribution kept)

Usage: python3 tools/build_data.py
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data-src")
OUT = os.path.join(ROOT, "app", "data")

from confusion_groups import GROUPS, BENCHMARKS  # noqa: E402
from silhouette_review import FLIGHT, BLOCK, PERCHED  # noqa: E402


def norm(s):
    return re.sub(r"[^a-z]", "", (s or "").lower())


def num(v):
    try:
        f = float(v)
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None


# ---------- Garnett morphometrics ----------
abd_by_sci, abd_by_common = {}, {}
with open(os.path.join(SRC, "Australian_Bird_Data_Version_1.csv"), encoding="latin1") as f:
    for r in csv.DictReader(f):
        if r["17_Species_2"] != "1" or r["32_Extinct_4"] == "1":
            continue
        rec = {
            "len": num(r["96_Body_length_8"]),
            "lenMin": num(r["97_Body_length_min_8"]),
            "lenMax": num(r["98_Body_length_max_8"]),
            "mass": num(r["99_Body_mass_average_8"]),
        }
        abd_by_sci[norm(r["7_Taxon_scientific_name_CandB_2"])] = rec
        abd_by_common[norm(r["3_Taxon_common_name_2"])] = rec

# iNaturalist (2020s taxonomy) -> Garnett 2015 name, for splits/renames
SYNONYMS = {
    "Porphyrio melanotus": "Porphyrio porphyrio",
    "Anthus australis": "Anthus novaeseelandiae",
    "Ardea plumifera": "Ardea intermedia",
    "Ardea coromanda": "Ardea ibis",
    "Butorides atricapilla": "Butorides striatus",
    "Cinnyris frenatus": "Nectarinia jugularis",
    "Malurus assimilis": "Malurus lamberti",
    "Tyto javanica": "Tyto alba",
    "Sericornis maculatus": "Sericornis frontalis",
    "Todiramphus sordidus": "Todiramphus chloris",
    "Cacatua leadbeateri": "Lophochroa leadbeateri",
    "Edolisoma tenuirostre": "Coracina tenuirostris",
    "Myiagra nana": "Myiagra rubecula",
    "Anarhynchus mongolus": "Charadrius mongolus",
    "Melithreptus chloropsis": "Melithreptus lunatus",
    "Meliphaga imitatrix": "Meliphaga gracilis",
    "Gallirallus sylvestris": "Hypotaenidia sylvestris",
    "Gygis candida": "Gygis alba",
    "Threskiornis molucca": "Threskiornis moluccus",
}

# fuzzy fallback: same genus, same epithet stem (moluccus/molucca, striatus/striata)
abd_by_stem = {}
with open(os.path.join(SRC, "Australian_Bird_Data_Version_1.csv"), encoding="latin1") as f:
    for r in csv.DictReader(f):
        if r["17_Species_2"] == "1" and r["32_Extinct_4"] != "1":
            parts = r["7_Taxon_scientific_name_CandB_2"].split()
            if len(parts) >= 2:
                abd_by_stem.setdefault((parts[0].lower(), parts[1][:5].lower()), []).append(
                    abd_by_sci[norm(r["7_Taxon_scientific_name_CandB_2"])])


def morph(sci, common):
    m = abd_by_sci.get(norm(SYNONYMS.get(sci, sci))) or abd_by_common.get(norm(common))
    if not m:
        parts = sci.split()
        if len(parts) == 2:
            c = abd_by_stem.get((parts[0].lower(), parts[1][:5].lower()), [])
            if len(c) == 1:
                m = c[0]
    return m or {}

# ---------- PhyloPic ----------
pp_all = json.load(open(os.path.join(SRC, "pp", "all.json")))
pp_fam = json.load(open(os.path.join(SRC, "pp", "fam.json")))
pp_ord = json.load(open(os.path.join(SRC, "pp", "ord.json")))

LIC_RANK = {
    "publicdomain/zero/1.0": 0, "publicdomain/mark/1.0": 0,
    "licenses/by/4.0": 1, "licenses/by/3.0": 1, "licenses/by-sa/3.0": 2,
    "licenses/by-nc/3.0": 3, "licenses/by-nc-sa/3.0": 3,
}
LIC_LABEL = {
    "publicdomain/zero/1.0": "CC0", "publicdomain/mark/1.0": "Public domain",
    "licenses/by/4.0": "CC BY 4.0", "licenses/by/3.0": "CC BY 3.0",
    "licenses/by-sa/3.0": "CC BY-SA 3.0", "licenses/by-nc/3.0": "CC BY-NC 3.0",
    "licenses/by-nc-sa/3.0": "CC BY-NC-SA 3.0",
}

pp_by_uuid, pp_by_species, pp_by_genus = {}, {}, {}
for im in pp_all:
    L = im["_links"]
    lic = re.sub(r"^https?://creativecommons.org/|/$", "", L["license"]["href"])
    vec = L.get("vectorFile") or {}
    if not vec.get("href"):
        continue
    w, h = (round(float(x)) for x in vec["sizes"].split("x"))
    name = L["specificNode"]["title"].strip()
    rec = {
        "uuid": im["uuid"],
        "url": vec["href"],
        "w": w, "h": h,
        "name": name,
        "by": im.get("attribution") or L["contributor"]["title"],
        "lic": LIC_LABEL.get(lic, lic),
        "licUrl": L["license"]["href"],
        "rank": LIC_RANK.get(lic, 9),
    }
    pp_by_uuid[im["uuid"]] = rec
    parts = name.split()
    if len(parts) >= 2:
        pp_by_species.setdefault(norm(" ".join(parts[:2])), []).append(rec)
    pp_by_genus.setdefault(norm(parts[0]), []).append(rec)


def best(cands):
    """Prefer roughly 'perched' aspect ratios (flying birds are very wide), then open licences."""
    cands = [c for c in cands if c["uuid"] not in BLOCK]
    if not cands:
        return None

    def score(r):
        ar = r["w"] / r["h"]
        # reviewed-perched first, then known flight poses, then unreviewed
        status = 0 if r["uuid"] in PERCHED else 1 if r["uuid"] in FLIGHT else 2
        odd_shape = not (0.55 <= ar <= 1.9)
        return (status, odd_shape, r["rank"], r["name"])

    return sorted(cands, key=score)[0]


def silhouette(sci, genus, family, order):
    for level, cands in (
        ("species", pp_by_species.get(norm(sci))),
        ("genus", pp_by_genus.get(norm(genus))),
        ("family", [pp_by_uuid[u] for u in pp_fam.get(family or "", []) if u in pp_by_uuid]),
        ("order", [pp_by_uuid[u] for u in pp_ord.get(order or "", []) if u in pp_by_uuid]),
    ):
        b = best(cands or [])
        if b:
            out = {k: b[k] for k in ("uuid", "url", "w", "h", "name", "by", "lic", "licUrl")}
            out["level"] = level
            out["pose"] = "flight" if b["uuid"] in FLIGHT else "perched"
            return out
    return None


# ---------- iNaturalist species ----------
inat = json.load(open(os.path.join(SRC, "inat_species.json")))
anc = json.load(open(os.path.join(SRC, "inat_anc.json")))

species, stats = [], {"len": 0, "mass": 0, "sil": {}}
for row in inat:
    t = row["taxon"]
    a = anc.get(str(t["id"]), {})
    fam = (a.get("family") or [None, None])
    order = (a.get("order") or [None, None])
    genus = (a.get("genus") or [t["name"].split()[0], None])[0]
    common = t.get("preferred_common_name") or t["name"]
    m = morph(t["name"], common)
    sil = silhouette(t["name"], genus, fam[0], order[0])
    photo = (t.get("default_photo") or {}).get("square_url")
    sp = {
        "id": t["id"],
        "sci": t["name"],
        "common": common,
        "family": fam[0], "familyCommon": fam[1],
        "obs": row["count"],
        "photo": photo,
        "len": m.get("len"), "lenMin": m.get("lenMin"), "lenMax": m.get("lenMax"),
        "mass": m.get("mass"),
        "sil": sil,
    }
    species.append(sp)
    stats["len"] += sp["len"] is not None
    stats["mass"] += sp["mass"] is not None
    lvl = sil["level"] if sil else "none"
    stats["sil"][lvl] = stats["sil"].get(lvl, 0) + 1

by_common = {norm(s["common"]): s for s in species}
by_sci = {norm(s["sci"]): s for s in species}


def resolve(name):
    """name may be 'Common Name' or 'Common Name|Alias|Genus species'."""
    for alt in name.split("|"):
        s = by_common.get(norm(alt)) or by_sci.get(norm(alt))
        if s:
            return s
    return None


problems = []
groups_out = []
for g in GROUPS:
    ids = []
    for n in g["species"]:
        s = resolve(n)
        if s:
            ids.append(s["id"])
        else:
            problems.append(f"group '{g['title']}': no match for '{n}'")
    if len(ids) >= 2:
        groups_out.append({"title": g["title"], "ids": ids, "tips": g.get("tips", []), "cat": g.get("cat", "")})

bench_ids = []
for n in BENCHMARKS:
    s = resolve(n)
    if s and s["len"]:
        bench_ids.append(s["id"])
    else:
        problems.append(f"benchmark: no match/length for '{n}'")

os.makedirs(OUT, exist_ok=True)
json.dump(species, open(os.path.join(OUT, "species.json"), "w"), separators=(",", ":"))
json.dump({"groups": groups_out, "benchmarks": bench_ids},
          open(os.path.join(OUT, "groups.json"), "w"), separators=(",", ":"), indent=None)

print(f"{len(species)} species | length {stats['len']} | mass {stats['mass']} | silhouettes {stats['sil']}")
print(f"{len(groups_out)} confusion groups, {len(bench_ids)} benchmarks")
for p in problems:
    print("  !", p)
