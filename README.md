# BirdID Shapes

## 📱 Open the app: **https://ciaranhr.github.io/BirdID/**

Open the link on your phone, then add it to your home screen so it works like an app:

- **iPhone (Safari):** Share → *Add to Home Screen*
- **Android (Chrome):** ⋮ menu → *Install app* / *Add to Home screen*

---

A phone-friendly web app (PWA) that complements Merlin for Australian birds:

- **Birds near you (home page)**: the birds recorded around you (or the most-recorded Australian birds), searchable. Tap one to see what it looks like, a **dichotomous ID key** that asks the questions that separate them (bill colour? throat? tail?), and a side-by-side table of field marks with the differences highlighted. The key is computed from a per-species trait table, so with a location set it only keys out the look-alikes recorded near you. Birds whose sexes or ages differ (fairy-wrens, Mallard, grebes…) get one entry per plumage.
- **Size ladder**: each species drawn at true relative scale next to familiar birds (fairy-wren, sparrow, magpie, raven, ibis, eagle…).
- **Confusion groups**: 43 curated Australian look-alike sets with true-scale silhouettes, length/weight ratios, field-mark notes and photo rows side by side, reached from each bird's look-alike page. You can also compare any 2–5 species.
- **Real-world photos**: research-grade iNaturalist observations from Australia, filterable by adult/juvenile/male/female, sorted by "best" or "recent" (recent gives more typical, imperfect views).
- **Species list**: every bird with its common and scientific name, grouped by family or sorted A–Z, searchable by any of them.
- **Species near you**: set a location (GPS, rounded to ~1 km, or a state/territory) and search, look-alike suggestions and the species list favour birds with research-grade iNaturalist records there. Counts are cached on the phone for a week, so they work offline.

## Run locally

```bash
cd app && python3 -m http.server 8000
# open http://localhost:8000
```

To try it on your phone over Wi-Fi, use `python3 -m http.server 8000 --bind 0.0.0.0` and open `http://<computer-ip>:8000`.
Offline caching (the service worker) only works over HTTPS or on localhost.

## Tests

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m playwright install chromium
.venv/bin/pytest                 # everything (~15 s)
.venv/bin/pytest -m "not e2e"    # Python only, no browser (<1 s)
```

- `tests/test_build_data.py`, `tests/test_phylopic.py`: the data tools, including a check that
  the committed `app/data/*.json` matches a fresh build (fails if you forget to rebuild).
- `tests/test_data_integrity.py`: the generated data, and that it agrees with `sw.js` / `lib.js`
  (image hosts, precached files).
- `tests/e2e/`: headless Chromium against a local server with a fake iNaturalist API and fake image
  hosts (no real network). `test_lib.py` unit-tests `app/lib.js`; `test_app.py` covers the user
  flows; `test_sw.py` tests the service worker's caching. Any console error or unexpected external
  request fails a test.

CI runs the suite on every push and pull request; deploys only happen if it passes.

## Deploy (GitHub Pages)

Pushing to `main` tests and then deploys `app/` to GitHub Pages via `.github/workflows/pages.yml`.
The deploy stamps `VERSION` in `app/sw.js` with the commit hash (`tools/stamp_version.py`), so installed
copies pick up each release automatically. There's no manual version bump.

## Rebuilding the data

`app/data/*.json` is generated from `data-src/` by:

```bash
python3 tools/build_data.py
```

To refresh the sources (each script takes an output directory and writes JSON there; copy the results into `data-src/`):

| Script | Source |
|---|---|
| `tools/fetch_inat.py <dir>` | iNaturalist species counts for birds in Australia |
| `tools/fetch_anc.py <dir>` | iNaturalist genus/family/order for each species |
| `tools/phylopic.py all\|family\|order <dir>` | PhyloPic bird silhouettes: all Aves, and per family/order (needs `inat_anc.json`) |

Hand-curated inputs:

- `tools/confusion_groups.py`: the look-alike groups, tips and size-ladder benchmark birds.
- `tools/silhouette_review.py`: PhyloPic images reviewed as perched / in-flight / blocked.
- `tools/field_marks.py`: per-species field marks for the ID key (bill colour, throat, tail, call, range…),
  with per-plumage overrides. **Draft**: add a species to `CHECKED` once its marks are verified against a
  field guide; until then the app shows a "draft" note under its key.

## Credits

- Body length & mass: Garnett et al. (2015) *Scientific Data* 2:150061, CC0.
- Photos: iNaturalist observers (credited per photo).
- Silhouettes: PhyloPic contributors (credited under each size ladder).
