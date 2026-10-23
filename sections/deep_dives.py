import pandas as pd
import streamlit as st

from utils.constants import METRICS
from utils.prep import aggregate, runoff_comparison
from utils.viz import (
    bar_by_lists,
    bar_by_size,
    choropleth_departments,
    histogram_communes,
    ranking_departments,
    runoff_histogram,
)


def _alt(text: str) -> None:
    st.caption(f"Chart description: {text}")


def size_section(ctx: dict) -> None:
    metric, sel = ctx["metric"], ctx["sel"]
    label = METRICS[metric]["label"]
    by_size = aggregate(sel, "size_band")
    st.header(f"{ctx['n']()} · Is it a big-city phenomenon?")
    if len(by_size) >= 2:
        first, last = by_size.iloc[0], by_size.iloc[-1]
        st.markdown(
            f"**{label} goes from {first[metric]:.0%} in communes with {first['size_band']} registered voters "
            f"to {last[metric]:.0%} in those with {last['size_band']}.**"
        )
    st.plotly_chart(bar_by_size(by_size, metric, ctx["selection"][metric]), width="stretch")
    _alt(
        f"Bar chart of the {label.lower()} by commune size band, from the smallest communes on the left to the "
        "largest on the right, with a dashed line for the selection average. Hover a bar for the number of communes and voters."
    )


def geo_section(ctx: dict) -> None:
    metric, sel, geojson = ctx["metric"], ctx["sel"], ctx["geojson"]
    label = METRICS[metric]["label"]
    by_dep = aggregate(sel, ["dep_code", "dep_name", "region"])
    st.header(f"{ctx['n']()} · Where is it concentrated?")
    if len(by_dep) >= 2:
        hi = by_dep.loc[by_dep[metric].idxmax()]
        lo = by_dep.loc[by_dep[metric].idxmin()]
        st.markdown(
            f"**{label}: highest in {hi['dep_name']} ({hi[metric]:.1%}), lowest in {lo['dep_name']} ({lo[metric]:.1%}).**"
        )
    map_col, rank_col = st.columns([3, 2], gap="large")
    with map_col:
        metro = by_dep[~by_dep["dep_code"].str.len().eq(3)]
        if geojson is None:
            st.info("Map unavailable: the department boundaries file could not be loaded. The ranking on the right shows the same data.")
        elif metro.empty:
            st.info("The selected departments are overseas and are not drawn on this mainland map — see the ranking.")
        else:
            st.plotly_chart(choropleth_departments(metro, geojson, metric), width="stretch")
            _alt(
                f"Map of mainland France where each department is shaded by its {label.lower()}: darker blue means a higher "
                "value. Overseas departments are not drawn on the map but appear in the ranking and in all totals."
            )
    with rank_col:
        n = min(10, max(1, len(by_dep) // 2)) if len(by_dep) > 1 else 1
        st.plotly_chart(ranking_departments(by_dep, metric, n=n), width="stretch")
        _alt(
            f"Horizontal bars ranking the {n} departments with the highest {label.lower()} (orange) and the {n} lowest (blue)."
        )
    with st.expander("Department table"):
        table = by_dep.sort_values(metric, ascending=False)[["dep_code", "dep_name", "region", "communes", "inscrits", metric]]
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={
                "dep_code": "Code",
                "dep_name": "Department",
                "region": "Region",
                "communes": st.column_config.NumberColumn("Communes", format="%d"),
                "inscrits": st.column_config.NumberColumn("Registered voters", format="%d"),
                metric: st.column_config.NumberColumn(label, format="percent"),
            },
        )


def distribution_section(ctx: dict) -> None:
    metric, sel, threshold = ctx["metric"], ctx["sel"], ctx["threshold"]
    label = METRICS[metric]["label"]
    st.header(f"{ctx['n']()} · Behind the averages: every commune")
    median = sel[metric].median()
    st.markdown(f"**In the typical (median) commune, the {label.lower()} is {median:.1%} — but the spread is wide.**")
    show_threshold = threshold if metric == "abstention_rate" else None
    st.plotly_chart(histogram_communes(sel, metric, show_threshold), width="stretch")
    _alt(
        f"Histogram of the {label.lower()} across individual communes: each bar counts how many communes fall in a range."
        + (" A dashed vertical line marks the threshold set in the sidebar." if show_threshold is not None else "")
    )
    st.caption(
        "Note: very small communes produce extreme percentages (a commune with 40 voters moves 2.5 points per voter), "
        "which explains the long tails."
    )


def choice_section(ctx: dict) -> None:
    sel = ctx["sel"]
    if sel["n_lists"].isna().all():
        return
    d = sel.dropna(subset=["n_lists"]).copy()
    d = d[d["n_lists"] > 0]
    if d.empty:
        return
    d["lists_label"] = pd.cut(d["n_lists"].astype(int), [0, 1, 2, 3, 10_000], labels=["1 list", "2 lists", "3 lists", "4+ lists"])
    agg = aggregate(d, "lists_label")
    st.header(f"{ctx['n']()} · When there is no real choice")
    if len(agg) >= 2 and "1 list" in agg["lists_label"].astype(str).values:
        one = agg[agg["lists_label"].astype(str) == "1 list"].iloc[0]
        many = aggregate(d[d["n_lists"] >= 2]).iloc[0]
        st.markdown(
            f"**Where only one list ran, {one['blank_null_share']:.0%} of voters cast a blank or null ballot, "
            f"versus {many['blank_null_share']:.0%} where they had a choice.**"
        )
    st.plotly_chart(bar_by_lists(agg, "blank_null_share"), width="stretch")
    _alt(
        "Bar chart of the share of blank and null ballots by number of lists competing in the commune. "
        "Hover a bar for the number of communes."
    )
    st.caption("The number of lists is counted from the vote columns of the official file (lists with at least one vote).")


def runoff_section(ctx: dict) -> None:
    cmp = runoff_comparison(ctx["data"])
    if cmp.empty:
        return
    cmp = cmp[cmp["insee"].isin(ctx["sel"]["insee"])]
    if cmp.empty:
        return
    st.header(f"{ctx['n']()} · Does a runoff mobilise voters?")
    rose = (cmp["delta_participation_pts"] > 0).mean()
    st.markdown(
        f"**In {len(cmp):,} communes that held a 2nd round, participation rose in {rose:.0%} of them "
        f"(median change {cmp['delta_participation_pts'].median():+.1f} points).**"
    )
    st.plotly_chart(runoff_histogram(cmp), width="stretch")
    _alt(
        "Histogram of the change in participation between the two rounds for communes with a runoff. "
        "Bars right of the dashed zero line are communes where more people voted in the 2nd round."
    )


def render(ctx: dict) -> None:
    counter = iter(range(2, 20))
    ctx["n"] = lambda: next(counter)
    size_section(ctx)
    st.divider()
    geo_section(ctx)
    st.divider()
    distribution_section(ctx)
    st.divider()
    choice_section(ctx)
    runoff_section(ctx)
    st.divider()
