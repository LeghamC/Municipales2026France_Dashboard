import streamlit as st

from utils.constants import LICENSE_LABEL, SOURCE_LABEL


def render(ctx: dict) -> None:
    nat = ctx["national"]
    st.title("The Silent Majority")
    st.subheader("Who stayed home at the 2026 municipal elections — and where?")
    st.caption(f"Source: {SOURCE_LABEL} — {LICENSE_LABEL}")

    st.markdown(
        f"""
> **{nat['abstention_rate']:.0%} of registered voters did not vote** in the
> {"first" if ctx["round"] == 1 else "second"} round of the March 2026 municipal elections —
> that is **{nat['abstentions']:,.0f} people** out of {nat['inscrits']:,.0f} registered.
"""
    )

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown(
            """
#### Why this matters
Municipal elections choose the mayors and councils who run schools, local roads, housing
and public services in roughly 35,000 communes. They took place on 15 and 22 March 2026,
in a period of national political instability and a year before the 2027 presidential
election. When abstention is high, councils are elected by a minority of residents —
which raises a simple democratic question: **who is still taking part?**

#### What this dashboard answers
1. **How big** is abstention, and how many voters turned up only to cast a blank or null ballot?
2. **Is it a big-city phenomenon?** How does it change with commune size?
3. **Where** is it concentrated across French departments?
4. **When there is no real choice** (a single list), do voters turn up to reject it?
5. **Does a runoff mobilise or tire voters?** (communes with a 2nd round)
"""
        )
    with right:
        st.markdown(
            """
#### Who it is for
Citizens and journalists curious about civic participation, and **local officials or
associations** looking for where turnout efforts would matter most.

#### How to read it
- Use the **sidebar** to pick a round, an indicator, a region, departments or commune sizes.
- Every number and chart updates with your selection.
- Rates are always computed as **totals ÷ totals** (weighted by voters), never as an
  average of commune percentages.
- This is **descriptive** data: it shows *where* abstention is high, not *why*.
"""
        )
    st.divider()
