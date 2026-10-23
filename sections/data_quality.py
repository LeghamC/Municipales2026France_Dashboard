import pandas as pd
import streamlit as st

from utils.constants import ROUND_DATES


def _round_report(q: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows in the official file", f"{q['rows_raw']:,}")
    c2.metric("Communes kept after cleaning", f"{q['rows_clean']:,}")
    c3.metric("Duplicates removed", f"{q.get('duplicates', 0):,}")
    c4.metric("Abstentions recomputed", f"{q.get('abstentions_derived', 0):,}", help="Rows where the file had no abstention count: computed as registered − voters.")

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("**Validation checks**")
        checks = pd.DataFrame(q["checks"])
        if not checks.empty:
            checks["status"] = checks.apply(
                lambda r: "➖ not testable" if r["tested"] == 0 else ("✅ pass" if r["failed"] == 0 else f"⚠️ {r['failed']:,} rows fail"),
                axis=1,
            )
            st.dataframe(checks[["check", "tested", "failed", "status"]], hide_index=True, width="stretch",
                         column_config={"check": "Check", "tested": "Rows tested", "failed": "Rows failing", "status": "Status"})
        st.markdown("**Rows excluded**")
        excluded = pd.DataFrame(q["excluded"])
        if excluded.empty:
            st.success("No row had to be excluded.")
        else:
            st.dataframe(excluded, hide_index=True, width="stretch", column_config={"reason": "Reason", "rows": "Rows"})
    with right:
        st.markdown("**Missing values per field**")
        miss = pd.DataFrame(q["missing"])
        miss["share"] = miss["missing"] / q["rows_raw"]
        st.dataframe(
            miss,
            hide_index=True,
            width="stretch",
            column_config={
                "column": "Field",
                "source_column": "Column in the official file",
                "missing": st.column_config.NumberColumn("Missing", format="%d"),
                "share": st.column_config.ProgressColumn("Share missing", format="percent", min_value=0, max_value=1),
            },
        )


def render(ctx: dict) -> None:
    st.header("Data quality & limitations")
    st.markdown(
        "**Every figure above comes from the official results file, after the checks below.** "
        "Rates are recomputed from raw counts rather than taken from the file's percentage columns."
    )
    reports = ctx["reports"]
    tabs = st.tabs([f"Round {q['round']} — {ROUND_DATES[q['round']]}" for q in reports])
    for tab, q in zip(tabs, reports):
        with tab:
            _round_report(q)

    with st.expander("Known limitations and how to read them", expanded=True):
        st.markdown(
            """
- **Abstention is measured among *registered* voters only.** Citizens who are not registered, or registered
  in the wrong place, are invisible here — so real non-participation is higher than shown.
- **Results are provisional by nature:** the Ministry publishes them subject to appeals before administrative
  courts and later corrections.
- **Paris, Lyon and Marseille** vote by sector (arrondissement); depending on the file, they appear as a single
  commune or are absent from the commune-level file.
- **Very small communes** produce extreme percentages; that is why every aggregate is weighted by voters.
- **Overseas departments** are included in all totals and rankings but are not drawn on the mainland map.
- **No causal claim:** commune size, location or the number of lists are *associated* with abstention here;
  income, age, mobility or local context are not in this dataset and may explain part of the pattern.
- **Privacy:** the data contains aggregated counts per commune only — no individual voter information.
"""
        )
    st.divider()
