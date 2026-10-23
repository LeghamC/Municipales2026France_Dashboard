import streamlit as st

from utils.prep import aggregate, runoff_comparison


def _insights(ctx: dict) -> list[str]:
    sel, nat = ctx["sel"], ctx["selection"]
    out = [
        f"**{nat['abstention_rate']:.0%} of registered voters stayed home** in the selection "
        f"({nat['abstentions']:,.0f} people), and {nat['blank_null_share']:.1%} of voters chose no list."
    ]
    by_size = aggregate(sel, "size_band")
    if len(by_size) >= 2:
        small, big = by_size.iloc[0], by_size.iloc[-1]
        gap = (big["abstention_rate"] - small["abstention_rate"]) * 100
        out.append(
            f"**Size matters:** abstention is {abs(gap):.0f} points {'higher' if gap > 0 else 'lower'} in the largest "
            f"communes ({big['abstention_rate']:.0%}) than in the smallest ({small['abstention_rate']:.0%})."
        )
    by_dep = aggregate(sel, ["dep_code", "dep_name"])
    if len(by_dep) >= 2:
        spread = (by_dep["abstention_rate"].max() - by_dep["abstention_rate"].min()) * 100
        out.append(f"**Geography matters too:** {spread:.0f} points separate the most and least abstentionist departments.")
    d = sel.dropna(subset=["n_lists"])
    if not d.empty and (d["n_lists"] == 1).any() and (d["n_lists"] >= 2).any():
        one = aggregate(d[d["n_lists"] == 1]).iloc[0]["blank_null_share"]
        many = aggregate(d[d["n_lists"] >= 2]).iloc[0]["blank_null_share"]
        out.append(
            f"**No choice, more protest:** blank and null ballots reach {one:.0%} where a single list ran, vs {many:.0%} elsewhere."
        )
    cmp = runoff_comparison(ctx["data"])
    if not cmp.empty:
        cmp = cmp[cmp["insee"].isin(sel["insee"])]
        if not cmp.empty:
            out.append(
                f"**Runoffs:** participation moved by a median of {cmp['delta_participation_pts'].median():+.1f} points "
                f"between rounds in the {len(cmp):,} communes concerned."
            )
    return out


def render(ctx: dict) -> None:
    st.header("Key insights & next steps")
    st.success("\n".join(f"- {line}" for line in _insights(ctx)))
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            """
#### What it implies
- **Turnout efforts should start where the silence is loudest:** large communes and the departments at the
  top of the ranking concentrate most of the people who did not vote.
- **A blank ballot is a message, not apathy:** voters who turn up only to reject every option are not
  disengaged — they are dissatisfied with the choice offered. Where a single list runs, encouraging
  competing lists may matter as much as encouraging turnout.
- **Low turnout narrows the base of local mandates:** in communes where most registered voters stayed
  home, the elected council was chosen by a minority of the electorate.
"""
        )
    with right:
        st.markdown(
            """
#### What would come next
- Join **INSEE socio-economic indicators** (income, age structure) by commune to test what *explains* abstention.
- Compare with the **2020 and 2014 municipal elections** to separate a trend from a one-off
  (2020 was disrupted by COVID-19).
- Go down to **polling-station level** in large cities, where the files allow it.
- Estimate the **unregistered population** to measure total non-participation.
"""
        )
    st.caption(
        "These findings describe associations in official counts; they do not establish causes. "
        "See “Data quality & limitations” above."
    )
