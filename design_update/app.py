import pandas as pd
import streamlit as st

from sections import conclusions, data_quality, deep_dives, intro, overview
from utils.constants import LICENSE_LABEL, METRICS, ROUND_DATES, SIZE_LABELS, SOURCE_LABEL
from utils.io import load_geojson
from utils.pipeline import build, load_processed
from utils.prep import aggregate
from utils.style import inject_css

st.set_page_config(page_title="The Silent Majority — Municipales 2026", page_icon="🗳️", layout="wide")
inject_css()


@st.cache_data(show_spinner="Loading and cleaning the election data…")
def get_data() -> tuple[pd.DataFrame, list[dict]]:
    loaded = load_processed()
    if loaded is None:
        try:
            loaded = build(save=True)
        except FileNotFoundError:
            from utils.fetch import fetch_geojson, fetch_round

            fetch_round(1)
            try:
                fetch_round(2)
            except Exception:
                pass
            fetch_geojson()
            loaded = build(save=True)
    df, reports = loaded
    df = df.copy()
    df["size_band"] = pd.Categorical(df["size_band"].astype(str), categories=SIZE_LABELS, ordered=True)
    return df, reports


@st.cache_data(show_spinner=False)
def get_geojson() -> dict | None:
    geo = load_geojson()
    if geo is None:
        try:
            from utils.fetch import fetch_geojson

            fetch_geojson()
            geo = load_geojson()
        except Exception:
            geo = None
    return geo


try:
    data, reports = get_data()
except Exception as exc:
    st.error(
        "The data could not be loaded. Run `python scripts/download_data.py` from the project folder, "
        f"then reload this page.\n\nDetails: {exc}"
    )
    st.stop()

geojson = get_geojson()
rounds = sorted(data["round"].unique())

with st.sidebar:
    st.markdown('<div class="side-brand">The Silent Majority<span>Municipales 2026 · explorer</span></div>', unsafe_allow_html=True)
    st.divider()
    round_no = st.radio(
        "Election round",
        rounds,
        format_func=lambda r: f"1st round — {ROUND_DATES[1]} (all communes)" if r == 1 else f"2nd round — {ROUND_DATES[2]} (runoff communes only)",
        help="Most communes elect their council in the 1st round. Only communes where no list won outright held a 2nd round.",
    )
    metric = st.selectbox(
        "Indicator shown on the charts",
        list(METRICS),
        format_func=lambda m: METRICS[m]["label"],
        help="Changes the map, the size chart, the distribution and the ranking.",
    )
    st.caption(METRICS[metric]["help"])

    round_df = data[data["round"] == round_no]
    regions = st.multiselect("Region", sorted(round_df["region"].unique()), placeholder="All regions")
    dept_pool = round_df[round_df["region"].isin(regions)] if regions else round_df
    dept_options = (
        dept_pool[["dep_code", "dep_name"]].drop_duplicates().sort_values("dep_code")
        .assign(label=lambda d: d["dep_code"] + " — " + d["dep_name"].astype(str))
    )
    depts = st.multiselect("Department", dept_options["label"].tolist(), placeholder="All departments")
    sizes = st.multiselect(
        "Commune size (registered voters)",
        SIZE_LABELS,
        placeholder="All sizes",
        help="Communes are grouped by their number of registered voters, a proxy for population.",
    )
    threshold = st.slider(
        "“Majority stayed home” threshold",
        min_value=0.30, max_value=0.80, value=0.50, step=0.05, format="%.2f",
        help="A commune is flagged when its abstention rate is at or above this value (0.50 = 50 %). Used in the KPIs and the distribution chart.",
    )
    st.divider()
    st.caption(f"Source: {SOURCE_LABEL}  \nLicense: {LICENSE_LABEL}")

sel = round_df
if regions:
    sel = sel[sel["region"].isin(regions)]
if depts:
    codes = [d.split(" — ")[0] for d in depts]
    sel = sel[sel["dep_code"].isin(codes)]
if sizes:
    sel = sel[sel["size_band"].isin(sizes)]

if sel.empty:
    st.warning("No commune matches these filters. Widen the selection in the sidebar.")
    st.stop()

ctx = {
    "data": data,
    "round": round_no,
    "metric": metric,
    "threshold": threshold,
    "round_df": round_df,
    "sel": sel,
    "national": aggregate(round_df).iloc[0],
    "selection": aggregate(sel).iloc[0],
    "is_filtered": bool(regions or depts or sizes),
    "geojson": geojson,
    "reports": reports,
}

intro.render(ctx)
overview.render(ctx)
deep_dives.render(ctx)
data_quality.render(ctx)
conclusions.render(ctx)
