# The Silent Majority — Abstention at the 2026 French municipal elections

An interactive Streamlit data story about **who stayed home** at the municipal elections of
15 and 22 March 2026: how large abstention was, whether it is a big-city phenomenon, where it is
concentrated, and whether voters who turned up still rejected every option (blank and null ballots).

- **Deployed app:** `<paste your Streamlit Community Cloud URL here>`
- **Demo video:** `<paste your video link here>`
- **Author:** `<First LAST>` — EFREI Paris, group BIA — student ID 20231141

---

## 1. Story and audience

| | |
|---|---|
| **Hook** | Nearly half of registered voters may skip the most local of all elections — in a period of national political instability, a year before the 2027 presidential election. |
| **Audience** | Citizens and journalists interested in civic participation; local officials and associations deciding where turnout efforts matter most. |
| **Questions** | Q1 How big is abstention, and how many voters cast a blank/null ballot? · Q2 Does it grow with commune size? · Q3 Which departments are most affected? · Q4 Do single-list communes see more blank/null ballots? · Q5 Does a runoff mobilise or tire voters? |
| **Narrative pattern** | Compare groups/regions (map + ranking) and rankings & distribution, closed by a before/after view of the two rounds. |

The narrative arc and the storyboard are detailed in [`REPORT.md`](REPORT.md).

## 2. Data

| File | Source | License |
|---|---|---|
| Commune-level results, 1st round (15 March 2026) | Ministère de l'Intérieur, published on [data.gouv.fr](https://www.data.gouv.fr/) — dataset “Élections municipales 2026 – Résultats du premier tour” | Licence Ouverte / Open Licence 2.0 |
| Commune-level results, 2nd round (22 March 2026) | [Élections municipales 2026 – Résultats du second tour](https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-second-tour) | Licence Ouverte / Open Licence 2.0 |
| Department boundaries (map only) | [france-geojson](https://github.com/gregoiredavid/france-geojson) (simplified departments) | See the repository for its license and original source |

The exact files and URLs used are recorded automatically in `data/SOURCES.json` by the download script.
Raw CSV files are **not** committed (see `.gitignore`); the script downloads them.

## 3. Run it locally (clean checkout)

Requires Python 3.12 or 3.13.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_data.py        # downloads, cleans, writes data/processed/
streamlit run app.py
```

Or with `make`: `make install data run`.

**If the automatic download cannot find a file** (dataset renamed on data.gouv.fr), open the dataset page,
copy the link of the *commune-level* CSV (not the polling-station file, not the list of elected officials) and run:

```bash
python scripts/download_data.py --url-t1 "<csv link round 1>" --url-t2 "<csv link round 2>"
```

You can also save the files by hand as `data/raw/municipales2026_t1_communes.csv` and
`data/raw/municipales2026_t2_communes.csv`, then run the script again.

## 4. Project structure

```
app.py                  # page config, data loading (cached), sidebar filters, section order
sections/
  intro.py              # hook, context, questions, audience
  overview.py           # KPI row tied to the filters
  deep_dives.py         # size, map + ranking, distribution, single-list communes, runoff
  data_quality.py       # validation checks, missing values, exclusions, limitations
  conclusions.py        # insights computed from the selection, implications, next steps
utils/
  constants.py          # paths, URLs, region mapping, size bands, metric definitions
  io.py                 # robust CSV reading (encoding, separator, ragged rows), GeoJSON loading
  fetch.py              # data.gouv.fr API download
  prep.py               # column mapping, cleaning, validation, aggregation
  pipeline.py           # build / load the processed parquet + quality report
  viz.py                # Plotly chart functions with a shared style
scripts/download_data.py
data/raw/               # downloaded files (CSV ignored by git)
data/processed/         # cleaned parquet + quality_report.json
```

## 5. Method

**Cleaning** (`utils/prep.py`)
1. Column names are matched by normalised name (accents, case and punctuation removed), so the code works with
   the different header styles the Ministry has used; percentage columns are ignored.
2. Counts are parsed from French formatting (spaces as thousand separators, comma decimals).
3. INSEE commune codes are rebuilt from department + commune codes (overseas codes ZA…ZM mapped to 971…976).
4. Rows are excluded, and counted, when codes are missing, registered voters are zero, voters exceed
   registered voters, the department is outside the 101 departments, or the commune code is duplicated.
5. Abstentions are recomputed as registered − voters when the column is absent.
6. The number of lists per commune is counted from the `Voix N` columns when the file has them.

**Validation checks** shown in the app: voters + abstentions = registered; blank + null + valid = voters;
rates within 0–100 %; missing values per field; duplicates.

**Indicators** are always computed as sums of counts divided by sums of counts (weighted by voters), never as
averages of commune percentages: abstention rate = abstentions ÷ registered; participation = voters ÷ registered;
blank + null share = (blank + null) ÷ voters.

**Performance:** cleaning runs once and is saved to parquet; `st.cache_data` caches loading and the GeoJSON.

## 6. Limitations

- Abstention is measured among **registered** voters only; unregistered citizens are invisible.
- Results are published subject to appeals and later corrections.
- Paris, Lyon and Marseille vote by sector; their treatment depends on the commune-level file.
- Small communes produce extreme percentages (hence weighting).
- Overseas departments are in all totals but not drawn on the mainland map.
- Associations only — no causal claim. Socio-economic factors are not in the data.

## 7. Deployment (Streamlit Community Cloud)

1. Run `python scripts/download_data.py` locally, then commit `data/processed/` and `data/raw/departements.geojson`
   (small files) so the deployed app does not depend on data.gouv.fr being reachable.
2. Push the repository to GitHub.
3. On share.streamlit.io: *Create app* → choose the repo, branch `main`, main file `app.py`, Python 3.12 or 3.13 → Deploy.

## 8. Reproducibility

Dependencies are pinned in `requirements.txt`. No random sampling is used (the full dataset is processed),
so results are deterministic for a given source file.
