# BirdID Shapes

A phone-friendly web app (PWA) that complements Merlin for Australian birds:

- **Size ladder**: each species drawn at true relative scale next to familiar birds (fairy-wren, sparrow, magpie, raven, ibis, eagle…).
- **Confusion groups**: 43 curated Australian look-alike sets with true-scale silhouettes, length/weight ratios, field-mark notes and photo rows side by side. You can also compare any 2–5 species.
- **Real-world photos**: research-grade iNaturalist observations from Australia, filterable by adult/juvenile/male/female, sorted by "best" or "recent" (recent gives more typical, imperfect views).

## Run locally

```bash
cd app && python3 -m http.server 8000
# open http://localhost:8000
```

To try it on your phone over Wi-Fi, use `python3 -m http.server 8000 --bind 0.0.0.0` and open `http://<computer-ip>:8000`.
Offline caching (the service worker) only works over HTTPS or on localhost.

## Deploy (GitHub Pages)

Pushing to `main` deploys `app/` to GitHub Pages via `.github/workflows/pages.yml`.
After changing app files, bump `VERSION` in `app/sw.js` so installed copies pick up the update.

## Rebuilding the data

`app/data/*.json` is generated from `data-src/` by:

```bash
python3 tools/build_data.py
```

To refresh the sources (each script takes an output directory and writes JSON there; copy the results into `data-src/`):

| Script | Source |
|---|---|
| `tools/fetch_inat.py` | iNaturalist species counts for birds in Australia |
| `tools/fetch_anc.py` | iNaturalist genus/family/order for each species |
| `tools/fetch_pp.py`, `fetch_fam.py`, `fetch_ord.py` | PhyloPic bird silhouettes, by family/order |

Hand-curated inputs:

- `tools/confusion_groups.py`: the look-alike groups, tips and size-ladder benchmark birds.
- `tools/silhouette_review.py`: PhyloPic images reviewed as perched / in-flight / blocked.

## Credits

- Body length & mass: Garnett et al. (2015) *Scientific Data* 2:150061, CC0.
- Photos: iNaturalist observers (credited per photo).
- Silhouettes: PhyloPic contributors (credited under each size ladder).
