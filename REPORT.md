# Report & storyboard - The Silent Majority

**Author:** Lelia GHEZALI · EFREI Paris · BIA · 20231141
**App:** `<deployed URL>` · **Video:** `<video link>` · **Repo:** `<GitHub URL>`

## 1. Problem framing

The 2026 municipal elections (15 and 22 March 2026) took place in a context of national political instability,
a year before the 2027 presidential election. Municipal elections are the most local vote: they choose who runs
schools, roads and local services. When a large share of registered voters stays home, local councils are chosen
by a minority. This project asks **who is still taking part, and where participation breaks down**.

- **Audience:** citizens and journalists; local officials and civic associations planning turnout efforts.
- **Key questions:** size of abstention and blank/null voting (Q1), link with commune size (Q2), geography (Q3),
  effect of having a single list (Q4), mobilisation between rounds (Q5).
- **Takeaway the user should leave with:** abstention is not uniform — it is concentrated in specific places and
  types of communes, and part of the “non-vote” is an active rejection of the choice offered.

## 2. Storyboard

| # | Screen section | Question | Visual | Interaction | Headline (computed live) |
|---|---|---|---|---|---|
| 0 | Hook | Why care? | Quote block with the national abstention count | — | “X % of registered voters did not vote…” |
| 1 | The big picture | Q1 | 4 KPI tiles with Δ vs France | All sidebar filters | “In your selection, X % stayed home — N pts above/below France” |
| 2 | Big-city phenomenon? | Q2 | Bar chart by size band + average line | Indicator, region, department | “Abstention goes from A % in the smallest communes to B % in the largest” |
| 3 | Where? | Q3 | Department choropleth + top/bottom-10 ranking + table | Indicator, filters, hover | “Highest in …, lowest in …” |
| 4 | Every commune | Distribution | Histogram + threshold line | Threshold slider | “In the typical commune…” |
| 5 | No real choice | Q4 | Blank+null share by number of lists | Filters | “Where one list ran, X % voted blank/null vs Y %” |
| 6 | Runoff | Q5 | Histogram of participation change | Filters | “Participation rose in X % of runoff communes” |
| 7 | Data quality | Trust | Checks, missing values, exclusions | Round tabs | — |
| 8 | Insights & next steps | So what? | Insight box + implications | Follows filters | — |

## 3. Data work

Source: Ministère de l'Intérieur results published on data.gouv.fr under Licence Ouverte 2.0 (exact files in
`data/SOURCES.json`). Cleaning, validation and weighting are described in the README (§5). Results of the checks
on the real files (from the app's *Data quality* section):

| Round | Raw rows | Clean communes | Excluded (reasons) | Failed checks |
|---|---|---|---|---|
| 1 | `…` | `…` | `…` | `…` |
| 2 | `…` | `…` | `…` | `…` |

## 4. Findings (fill in from the app with no filter)

1. National abstention: `…` % (`…` people); blank + null: `…` % of voters.
2. Size effect: `…` % in communes < 100 voters vs `…` % in communes ≥ 100,000.
3. Geography: highest `…` (`…` %), lowest `…` (`…` %).
4. Single-list communes: `…` % blank/null vs `…` % elsewhere.
5. Runoff: participation rose in `…` % of `…` runoff communes (median `…` pts).

## 5. Limitations and ethics

Registered voters only (unregistered citizens invisible); provisional results subject to appeals; Paris/Lyon/Marseille
sector voting; small-commune volatility (handled by weighting); overseas departments not drawn on the map;
associations, not causes. Only aggregated counts per commune are used — no personal data. The dashboard is
deliberately **non-partisan**: it does not analyse party results.

## 6. Next steps

Join INSEE socio-economic indicators; compare with 2014 and 2020; polling-station analysis in large cities;
estimate unregistered population.
