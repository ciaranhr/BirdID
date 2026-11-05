#!/usr/bin/env python3
"""Merge source data into app/data/species.json and app/data/groups.json.

Sources (all in data-src/, fetched by tools/fetch_inat.py, fetch_anc.py and phylopic.py):
  - iNaturalist species counts for Aves in Australia (place 6744) + ancestry
  - Garnett et al. 2015 "Australian Bird Data Version 1" (CC0) for body length / mass
  - PhyloPic silhouettes (various CC licences, attribution kept)

Usage: python3 tools/build_data.py
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data-src")
OUT = os.path.join(ROOT, "app", "data")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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


class Morph:
    """Garnett body length/mass lookup: by scientific name (with SYNONYMS), common name,
    then a fuzzy same-genus/same-epithet-stem fallback (moluccus/molucca, striatus/striata)."""

    def __init__(self, rows):
        self.by_sci, self.by_common, self.by_stem = {}, {}, {}
        scis = []
        for r in rows:
            if r["17_Species_2"] != "1" or r["32_Extinct_4"] == "1":
                continue
            rec = {
                "len": num(r["96_Body_length_8"]),
                "lenMin": num(r["97_Body_length_min_8"]),
                "lenMax": num(r["98_Body_length_max_8"]),
                "mass": num(r["99_Body_mass_average_8"]),
            }
            sci = r["7_Taxon_scientific_name_CandB_2"]
            self.by_sci[norm(sci)] = rec
            self.by_common[norm(r["3_Taxon_common_name_2"])] = rec
            scis.append(sci)
        for sci in scis:  # after the pass, so duplicate names resolve to the final record
            parts = sci.split()
            if len(parts) >= 2:
                self.by_stem.setdefault((parts[0].lower(), parts[1][:5].lower()), []).append(
                    self.by_sci[norm(sci)])

    @classmethod
    def from_csv(cls, path):
        with open(path, encoding="latin1") as f:
            return cls(csv.DictReader(f))

    def __call__(self, sci, common):
        m = self.by_sci.get(norm(SYNONYMS.get(sci, sci))) or self.by_common.get(norm(common))
        if not m:
            parts = sci.split()
            if len(parts) == 2:
                c = self.by_stem.get((parts[0].lower(), parts[1][:5].lower()), [])
                if len(c) == 1:  # ambiguous stems are skipped rather than guessed
                    m = c[0]
        return m or {}


# ---------- PhyloPic ----------

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


def pp_record(im):
    """One PhyloPic API image -> our record, or None if it has no vector file."""
    L = im["_links"]
    vec = L.get("vectorFile") or {}
    if not vec.get("href"):
        return None
    lic = re.sub(r"^https?://creativecommons.org/|/$", "", L["license"]["href"])
    w, h = (round(float(x)) for x in vec["sizes"].split("x"))
    return {
        "uuid": im["uuid"],
        "url": vec["href"],
        "w": w, "h": h,
        "name": L["specificNode"]["title"].strip(),
        "by": im.get("attribution") or L["contributor"]["title"],
        "lic": LIC_LABEL.get(lic, lic),
        "licUrl": L["license"]["href"],
        "rank": LIC_RANK.get(lic, 9),
    }


class PhyloPic:
    def __init__(self, pp_all, pp_fam, pp_ord, flight=FLIGHT, block=BLOCK, perched=PERCHED):
        self.fam, self.ord = pp_fam, pp_ord
        self.flight, self.block, self.perched = flight, block, perched
        self.by_uuid, self.by_species, self.by_genus = {}, {}, {}
        for im in pp_all:
            rec = pp_record(im)
            if not rec:
                continue
            self.by_uuid[rec["uuid"]] = rec
            parts = rec["name"].split()
            if len(parts) >= 2:
                self.by_species.setdefault(norm(" ".join(parts[:2])), []).append(rec)
            self.by_genus.setdefault(norm(parts[0]), []).append(rec)

    def best(self, cands):
        """Reviewed-perched first, then known flight poses, then unreviewed; within those prefer
        roughly perched aspect ratios (flying birds are very wide), then open licences."""
        cands = [c for c in cands if c["uuid"] not in self.block]
        if not cands:
            return None

        def score(r):
            ar = r["w"] / r["h"]
            status = 0 if r["uuid"] in self.perched else 1 if r["uuid"] in self.flight else 2
            odd_shape = not (0.55 <= ar <= 1.9)
            return (status, odd_shape, r["rank"], r["name"])

        return min(cands, key=score)

    def silhouette(self, sci, genus, family, order):
        for level, cands in (
            ("species", self.by_species.get(norm(sci))),
            ("genus", self.by_genus.get(norm(genus))),
            ("family", [self.by_uuid[u] for u in self.fam.get(family or "", []) if u in self.by_uuid]),
            ("order", [self.by_uuid[u] for u in self.ord.get(order or "", []) if u in self.by_uuid]),
        ):
            b = self.best(cands or [])
            if b:
                out = {k: b[k] for k in ("uuid", "url", "w", "h", "name", "by", "lic", "licUrl")}
                out["level"] = level
                out["pose"] = "flight" if b["uuid"] in self.flight else "perched"
                return out
        return None


# ---------- iNaturalist species ----------

def build_species(inat, anc, morph, pp):
    species = []
    for row in inat:
        t = row["taxon"]
        a = anc.get(str(t["id"]), {})
        fam = a.get("family") or [None, None]
        order = a.get("order") or [None, None]
        genus = (a.get("genus") or [t["name"].split()[0], None])[0]
        common = t.get("preferred_common_name") or t["name"]
        m = morph(t["name"], common)
        species.append({
            "id": t["id"],
            "sci": t["name"],
            "common": common,
            "family": fam[0], "familyCommon": fam[1],
            "obs": row["count"],
            "photo": (t.get("default_photo") or {}).get("square_url"),
            "len": m.get("len"), "lenMin": m.get("lenMin"), "lenMax": m.get("lenMax"),
            "mass": m.get("mass"),
            "sil": pp.silhouette(t["name"], genus, fam[0], order[0]),
        })
    return species


def species_stats(species):
    stats = {"len": 0, "mass": 0, "sil": {}}
    for sp in species:
        stats["len"] += sp["len"] is not None
        stats["mass"] += sp["mass"] is not None
        lvl = sp["sil"]["level"] if sp["sil"] else "none"
        stats["sil"][lvl] = stats["sil"].get(lvl, 0) + 1
    return stats


class Resolver:
    def __init__(self, species):
        self.by_common = {norm(s["common"]): s for s in species}
        self.by_sci = {norm(s["sci"]): s for s in species}

    def __call__(self, name):
        """name may be 'Common Name' or 'Common Name|Alias|Genus species'."""
        for alt in name.split("|"):
            s = self.by_common.get(norm(alt)) or self.by_sci.get(norm(alt))
            if s:
                return s
        return None


def build_groups(species, groups=GROUPS, benchmarks=BENCHMARKS):
    """-> (groups_out, bench_ids, problems). Groups with < 2 resolved species are dropped."""
    resolve = Resolver(species)
    problems, groups_out = [], []
    for g in groups:
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
    for n in benchmarks:
        s = resolve(n)
        if s and s["len"]:
            bench_ids.append(s["id"])
        else:
            problems.append(f"benchmark: no match/length for '{n}'")
    return groups_out, bench_ids, problems


# ---------- main ----------

def load_json(*parts):
    with open(os.path.join(*parts)) as f:
        return json.load(f)


def build(src=SRC, out=OUT):
    morph = Morph.from_csv(os.path.join(src, "Australian_Bird_Data_Version_1.csv"))
    pp = PhyloPic(load_json(src, "pp", "all.json"), load_json(src, "pp", "fam.json"),
                  load_json(src, "pp", "ord.json"))
    species = build_species(load_json(src, "inat_species.json"), load_json(src, "inat_anc.json"), morph, pp)
    groups_out, bench_ids, problems = build_groups(species)

    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "species.json"), "w") as f:
        json.dump(species, f, separators=(",", ":"))
    with open(os.path.join(out, "groups.json"), "w") as f:
        json.dump({"groups": groups_out, "benchmarks": bench_ids}, f, separators=(",", ":"))
    return species, groups_out, bench_ids, problems


def main():
    species, groups_out, bench_ids, problems = build()
    stats = species_stats(species)
    print(f"{len(species)} species | length {stats['len']} | mass {stats['mass']} | silhouettes {stats['sil']}")
    print(f"{len(groups_out)} confusion groups, {len(bench_ids)} benchmarks")
    for p in problems:
        print("  !", p)


if __name__ == "__main__":
    main()
