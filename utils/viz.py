import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import METRICS

BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRAY = "#8a8985"
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
FONT = dict(family="Inter, Segoe UI, sans-serif", size=13)


def _layout(fig: go.Figure, height: int = 420, **kwargs) -> go.Figure:
    kwargs.setdefault("margin", dict(l=10, r=10, t=30, b=10))
    fig.update_layout(
        height=height,
        font=FONT,
        hoverlabel=dict(font_size=13),
        bargap=0.25,
        **kwargs,
    )
    return fig


def pct_axis(fig: go.Figure, axis: str = "y", title: str = "") -> go.Figure:
    getattr(fig, f"update_{axis}axes")(tickformat=".0%", title_text=title, showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    return fig


def reference_line(fig: go.Figure, value: float, label: str, axis: str = "y") -> go.Figure:
    kw = dict(line_dash="dash", line_color=GRAY, line_width=1.5, annotation_text=label, annotation_font_color=GRAY)
    if axis == "y":
        fig.add_hline(y=value, annotation_position="top left", **kw)
    else:
        fig.add_vline(x=value, annotation_position="top right", **kw)
    return fig


def choropleth_departments(agg: pd.DataFrame, geojson: dict, metric: str) -> go.Figure:
    label = METRICS[metric]["label"]
    fig = px.choropleth(
        agg,
        geojson=geojson,
        locations="dep_code",
        featureidkey="properties.code",
        color=metric,
        color_continuous_scale=SEQ_BLUE,
        hover_name="dep_name",
        hover_data={metric: ":.1%", "communes": ":,", "inscrits": ":,", "dep_code": True},
        labels={metric: label, "communes": "Communes", "inscrits": "Registered voters", "dep_code": "Code"},
    )
    fig.update_traces(marker_line_color="rgba(255,255,255,0.8)", marker_line_width=0.6)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_coloraxes(colorbar=dict(title=METRICS[metric]["short"], tickformat=".0%"))
    return _layout(fig, height=560)


def bar_by_size(agg: pd.DataFrame, metric: str, national: float) -> go.Figure:
    label = METRICS[metric]["label"]
    fig = px.bar(
        agg,
        x="size_band",
        y=metric,
        text=agg[metric].map(lambda v: f"{v:.0%}"),
        custom_data=["communes", "inscrits"],
        color_discrete_sequence=[BLUE],
    )
    fig.update_traces(
        marker_line_width=0,
        textposition="outside",
        hovertemplate="<b>%{x} registered voters</b><br>" + label + ": %{y:.1%}<br>Communes: %{customdata[0]:,}<br>Registered voters: %{customdata[1]:,}<extra></extra>",
    )
    pct_axis(fig, "y", label + " (%)")
    fig.update_xaxes(title_text="Commune size (number of registered voters)")
    reference_line(fig, national, f"Selection average {national:.1%}")
    return _layout(fig, uniformtext_minsize=10)


def histogram_communes(df: pd.DataFrame, metric: str, threshold: float | None = None) -> go.Figure:
    label = METRICS[metric]["label"]
    fig = px.histogram(df, x=metric, nbins=50, color_discrete_sequence=[BLUE])
    fig.update_traces(
        marker_line_width=0,
        hovertemplate=label + ": %{x}<br>Communes: %{y:,}<extra></extra>",
    )
    pct_axis(fig, "x", label + " (%) - one commune = one count")
    fig.update_yaxes(title_text="Number of communes")
    if threshold is not None:
        reference_line(fig, threshold, f"Threshold {threshold:.0%}", axis="x")
    return _layout(fig, height=380)


def ranking_departments(agg: pd.DataFrame, metric: str, n: int = 10) -> go.Figure:
    label = METRICS[metric]["label"]
    ranked = agg.sort_values(metric)
    top = ranked.tail(n).assign(group=f"Highest {n}")
    bottom = ranked.head(n).assign(group=f"Lowest {n}")
    data = pd.concat([bottom, top]).drop_duplicates("dep_code")
    data["name"] = data["dep_name"].astype(str) + " (" + data["dep_code"].astype(str) + ")"
    fig = px.bar(
        data,
        x=metric,
        y="name",
        color="group",
        orientation="h",
        color_discrete_map={f"Highest {n}": ORANGE, f"Lowest {n}": BLUE},
        custom_data=["communes", "inscrits"],
        text=data[metric].map(lambda v: f"{v:.1%}"),
    )
    fig.update_traces(
        marker_line_width=0,
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>" + label + ": %{x:.1%}<br>Communes: %{customdata[0]:,}<br>Registered voters: %{customdata[1]:,}<extra></extra>",
    )
    pct_axis(fig, "x", label + " (%)")
    fig.update_traces(cliponaxis=False)
    fig.update_xaxes(range=[0, data[metric].max() * 1.18])
    fig.update_yaxes(title_text="", categoryorder="total ascending")
    return _layout(fig, height=max(420, 26 * len(data)), legend=dict(title="", orientation="h", y=1.0, yanchor="bottom", x=0), margin=dict(l=10, r=10, t=50, b=10))


def bar_by_lists(agg: pd.DataFrame, metric: str) -> go.Figure:
    label = METRICS[metric]["label"]
    fig = px.bar(
        agg,
        x="lists_label",
        y=metric,
        text=agg[metric].map(lambda v: f"{v:.0%}"),
        custom_data=["communes"],
        color_discrete_sequence=[BLUE],
    )
    fig.update_traces(
        marker_line_width=0,
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>" + label + ": %{y:.1%}<br>Communes: %{customdata[0]:,}<extra></extra>",
    )
    pct_axis(fig, "y", label + " (%)")
    fig.update_xaxes(title_text="Number of lists on the ballot")
    return _layout(fig, height=380)


def runoff_histogram(cmp: pd.DataFrame) -> go.Figure:
    fig = px.histogram(cmp, x="delta_participation_pts", nbins=40, color_discrete_sequence=[BLUE])
    fig.update_traces(marker_line_width=0, hovertemplate="Change: %{x} pts<br>Communes: %{y:,}<extra></extra>")
    fig.update_xaxes(title_text="Participation change, 2nd round − 1st round (percentage points)", ticksuffix=" pts")
    fig.update_yaxes(title_text="Number of communes")
    reference_line(fig, 0, "No change", axis="x")
    return _layout(fig, height=360)
