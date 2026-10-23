# Report & storyboard — The Silent Majority

**Author:** Lélia GHEZALI · EFREI Paris · BIA · 20231141
**App:** https://silent-majority-2026.streamlit.app/ · **Repo:** https://github.com/LeghamC/Municipales2026France_Dashboard.git

## 1. Problem framing

The 2026 municipal elections (15 and 22 March 2026) took place in a context of national political instability,
a year before the 2027 presidential election. Municipal elections are the most local vote: they choose who runs
schools, roads and local services. When a large share of registered voters stays home, local councils are chosen
by a minority. This project asks **who is still taking part, and where participation breaks down**.

- **Audience:** citizens and journalists; local officials and civic associations planning turnout efforts.
- **Key questions:** size of abstention and blank/null voting (Q1), link with commune size (Q2), geography (Q3),
  effect of having a single list (Q4), mobilisation between rounds (Q5).
- **Takeaway the user should leave with:** abstention is not uniform — it peaks in medium-sized towns and in
  specific departments, and part of the “non-vote” is an active rejection of the choice offered.

## 2. Storyboard

| # | Screen section | Question | Visual | Interaction | Headline (computed live) |
|---|---|---|---|---|---|
| 0 | Hook | Why care? | Quote block with the national abstention count | — | “43 % of registered voters did not vote… 20,697,441 people” |
| 1 | The big picture | Q1 | 4 KPI tiles with Δ vs France | All sidebar filters | “Across France, 42.9 % stayed home, 5.4 % voted blank or null” |
| 2 | Big-city phenomenon? | Q2 | Bar chart by size band + average line | Indicator, region, department | “From 29 % to 44 %, peaking at 48 % in towns of 20,000–99,999 voters” |
| 3 | Where? | Q3 | Department choropleth + top/bottom-10 ranking + table | Indicator, filters, hover | “Highest in Seine-Saint-Denis (53.3 %), lowest in Cantal (29.0 %)” |
| 4 | Every commune | Distribution | Histogram + threshold line | Threshold slider | “In the typical commune, abstention is 36.8 %” |
| 5 | No real choice | Q4 | Blank+null share by number of lists | Filters | “Where one list ran, 14 % voted blank/null vs 3 %” |
| 6 | Runoff | Q5 | Histogram of participation change | Filters | “Participation rose in 67 % of runoff communes (median +1.1 pts)” |
| 7 | Data quality | Trust | Checks, missing values, exclusions | Round tabs | — |
| 8 | Insights & next steps | So what? | Insight box + implications | Follows filters | — |

## 3. Data work

Source: Ministère de l'Intérieur results published on data.gouv.fr under Licence Ouverte 2.0 (exact files in
`data/SOURCES.json`). Cleaning, validation and weighting are described in the README (§5).

| Round | Raw rows | Clean communes | Excluded (reasons) | Failed checks |
|---|---|---|---|---|
| 1 | 34,836 | 34,800 | 36 — 35 outside the 101 departments (other overseas collectivities), 1 with more voters than registered voters | 0 / 3 (each check run on 34,800 rows); no duplicates, no missing values |
| 2 | 1,526 | 1,501 | 25 — all outside the 101 departments (other overseas collectivities) | 0 / 3 (each check run on 1,501 rows); no duplicates, no missing values |

All 1,501 second-round communes were matched to their first-round results on the rebuilt INSEE code (100 % join),
which confirms that commune codes were reconstructed consistently across the two files.

## 4. Findings (1st round, no filter unless stated)

1. National abstention: 42.9 % (20,697,441 of 48,249,945 registered voters); 5.4 % of voters cast a blank or
   null ballot; in 3,432 communes (10 %) at least half of registered voters stayed home.
2. Size effect: abstention rises steadily with commune size, from 29 % (< 100 voters) to a peak of 48 % in towns
   of 20,000–99,999 voters, then falls back to 44 % in cities of 100,000+. Medium-sized towns, not the largest
   cities, are the most abstentionist.
3. Geography: abstention ranges from 29.0 % in Cantal to 53.3 % in Seine-Saint-Denis, a 24.3-point gap.
   The top 10 is dominated by the Paris suburbs (Seine-Saint-Denis, Val-d'Oise 49.9 %, Val-de-Marne 49.3 %,
   Seine-et-Marne 48.4 %), two overseas departments (Martinique 52.2 %, Guyane 51.4 %) and Grand Est
   (Haut-Rhin, Marne, Meurthe-et-Moselle, 47.7–48.2 %). The lowest rates are in rural central and southern
   France (Cantal, Lozère, Aveyron, Corrèze, Creuse, Gers, Hautes-Alpes), Corsica and Mayotte.
4. Typical commune vs France: the median commune has an abstention rate of 36.8 %, six points below the
   national rate (42.9 %). Most communes are small and small communes abstain less, while most voters live in
   larger towns where abstention is higher, so the national rate sits above the typical commune.
5. No real choice: where only one list ran, 14 % of voters cast a blank or null ballot, versus 3 % where they had
   a choice (2 % with 4 lists or more). Turning up only to reject the single option offered is a form of
   participation that abstention figures miss.
6. Runoff: in the 1,501 communes that held a 2nd round, participation rose in 67 % of them, with a modest median
   change of +1.1 points; most communes moved by less than 5 points either way. A runoff mobilises slightly,
   it does not transform turnout.

## 5. Limitations and ethics

Registered voters only (unregistered citizens invisible); provisional results subject to appeals; Paris/Lyon/Marseille
sector voting; small-commune volatility (handled by weighting); overseas departments not drawn on the map;
associations, not causes. A handful of communes show close to 100 % abstention; they are kept in the data (they
pass all checks) but are very small and weigh almost nothing in the weighted rates. Their cause cannot be
determined from this dataset. Only aggregated counts per commune are used — no personal data. The dashboard is
deliberately **non-partisan**: it does not analyse party results.

## 6. Next steps

Join INSEE socio-economic indicators to test what explains the medium-town peak and the departmental gaps;
compare with 2014 and 2020 (2020 was disrupted by COVID-19); polling-station analysis in large cities;
estimate the unregistered population to measure total non-participation.
