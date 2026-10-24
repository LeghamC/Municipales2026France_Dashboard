import streamlit as st


def _delta_pts(value: float, ref: float, filtered: bool) -> str | None:
    if not filtered:
        return None
    return f"{(value - ref) * 100:+.1f} pts vs France"


def render(ctx: dict) -> None:
    sel, nat, s = ctx["sel"], ctx["national"], ctx["selection"]
    filtered, threshold = ctx["is_filtered"], ctx["threshold"]
    flagged = int((sel["abstention_rate"] >= threshold).sum())

    st.header("1 · The big picture")
    if filtered:
        gap = (s["abstention_rate"] - nat["abstention_rate"]) * 100
        direction = "above" if gap > 0 else "below"
        st.markdown(
            f"**In your selection, {s['abstention_rate']:.1%} of registered voters stayed home: "
            f"{abs(gap):.1f} points {direction} the national rate ({nat['abstention_rate']:.1%}).**"
        )
    else:
        st.markdown(
            f"**Across France, {nat['abstention_rate']:.1%} of registered voters stayed home, and "
            f"{nat['blank_null_share']:.1%} of those who voted cast a blank or null ballot.**"
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Registered voters",
        f"{s['inscrits']:,.0f}",
        help=f"Across {int(s['communes']):,} communes in the current selection.",
    )
    c2.metric(
        "Abstention rate",
        f"{s['abstention_rate']:.1%}",
        _delta_pts(s["abstention_rate"], nat["abstention_rate"], filtered),
        delta_color="inverse",
        help="Abstentions ÷ registered voters (weighted).",
    )
    c3.metric(
        "Blank + null ballots",
        f"{s['blank_null_share']:.1%}",
        _delta_pts(s["blank_null_share"], nat["blank_null_share"], filtered),
        delta_color="inverse",
        help="(Blank + null) ÷ voters. Voters who turned up but chose no list.",
    )
    c4.metric(
        f"Communes where ≥ {threshold:.0%} stayed home",
        f"{flagged:,}",
        f"{flagged / len(sel):.0%} of communes",
        delta_color="off",
        help="Change the threshold in the sidebar.",
    )
    st.caption(
        "KPI description: four headline figures for the current selection: registered voters, abstention rate, "
        "share of blank and null ballots, and number of communes above the abstention threshold. When filters are "
        "active, the small figures compare the selection with France as a whole (red = worse than the national figure)."
    )
    st.divider()
