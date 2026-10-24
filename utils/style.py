import html

import streamlit as st

NAVY = "#0d366b"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#14213d"
MUTED = "#5b6475"
SURFACE = "#ffffff"
CANVAS = "#f5f4f0"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Inter:wght@400;500;600&display=swap');

html, body, .stMarkdown, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, .stCaption {{ font-family: 'Inter', system-ui, sans-serif; }}
.block-container {{ padding-top: 3.5rem; max-width: 1280px; }}
h1, h2, h3, h4, h1 span, h2 span, h3 span, h4 span {{ font-family: 'Fraunces', Georgia, serif !important; color: {INK}; letter-spacing: -0.01em; }}
.hero h1, .hero h1 span {{ color: #fff !important; }}

.hero {{
  background: radial-gradient(circle at 85% 20%, rgba(42,120,214,.55), transparent 45%),
              linear-gradient(135deg, {NAVY} 0%, #10284d 100%);
  color: #fff; border-radius: 22px; padding: 2.6rem 2.8rem 2.2rem; margin-bottom: 1.6rem;
  box-shadow: 0 18px 40px -18px rgba(13,54,107,.55);
}}
.hero .eyebrow {{ text-transform: uppercase; letter-spacing: .14em; font-size: .78rem; font-weight: 600; color: #b7d3f6; }}
.hero h1 {{ color: #fff !important; font-size: clamp(2.4rem, 5vw, 3.8rem); font-weight: 800; margin: .3rem 0 .2rem; padding: 0; line-height: 1.05; }}
.hero .lead {{ font-size: 1.2rem; color: #dbe7f7; margin-bottom: 1.8rem; max-width: 46rem; }}
.hero .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1.6rem; border-top: 1px solid rgba(255,255,255,.18); padding-top: 1.4rem; }}
.hero .stat .num {{ font-family: 'Fraunces', Georgia, serif; font-size: 2.6rem; font-weight: 800; line-height: 1; color: #fff; }}
.hero .stat .num.accent {{ color: #ffb38f; }}
.hero .stat .lbl {{ font-size: .88rem; color: #b7d3f6; margin-top: .35rem; max-width: 14rem; }}
.hero .source {{ font-size: .75rem; color: #9db7d9; margin-top: 1.4rem; }}

.sec {{ display: flex; align-items: flex-end; gap: 1rem; margin: 2.6rem 0 .6rem; }}
.sec .num {{ font-family: 'Fraunces', Georgia, serif; font-size: 3.2rem; font-weight: 800; line-height: .85; color: {BLUE}; opacity: .9; }}
.sec .kicker {{ text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 600; color: {ORANGE}; }}
.sec h2 {{ margin: 0 !important; padding: 0 !important; font-size: 1.9rem !important; }}

.headline {{ border-left: 4px solid {ORANGE}; background: {SURFACE}; padding: .9rem 1.1rem; border-radius: 0 12px 12px 0;
  font-size: 1.05rem; color: {INK}; margin: .4rem 0 1rem; box-shadow: 0 1px 2px rgba(20,33,61,.06); }}

[data-testid="stMetric"] {{
  background: {SURFACE}; border: 1px solid #e6e4de; border-radius: 16px; padding: 1.1rem 1.2rem;
  box-shadow: 0 1px 2px rgba(20,33,61,.05), 0 8px 24px -16px rgba(20,33,61,.25);
  border-top: 4px solid {BLUE};
}}
[data-testid="stMetricValue"] {{ font-family: 'Fraunces', Georgia, serif; font-weight: 800; color: {INK}; }}

[data-testid="stPlotlyChart"] {{
  background: {SURFACE}; border: 1px solid #e6e4de; border-radius: 16px; padding: .8rem .8rem .2rem;
  box-shadow: 0 1px 2px rgba(20,33,61,.05);
}}
[data-testid="stExpander"] details {{ background: {SURFACE}; border-radius: 14px; border-color: #e6e4de; }}

[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #eef3fb 0%, {CANVAS} 60%); border-right: 1px solid #e3e6ec; }}
[data-testid="stSidebar"] h2 {{ font-size: 1.35rem; }}
.side-brand {{ font-family: 'Fraunces', Georgia, serif; font-weight: 800; font-size: 1.25rem; color: {NAVY}; line-height: 1.15; }}
.side-brand span {{ display: block; font-family: 'Inter', sans-serif; font-weight: 500; font-size: .78rem; color: {MUTED};
  text-transform: uppercase; letter-spacing: .12em; margin-top: .3rem; }}

hr {{ border-color: #e3e1db !important; }}
.stCaption, [data-testid="stCaptionContainer"] {{ color: {MUTED} !important; }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(eyebrow: str, title: str, lead: str, stats: list[tuple[str, str, bool]], source: str) -> None:
    items = "".join(
        f'<div class="stat"><div class="num{" accent" if accent else ""}">{html.escape(n)}</div>'
        f'<div class="lbl">{html.escape(lbl)}</div></div>'
        for n, lbl, accent in stats
    )
    st.markdown(
        f'<div class="hero" role="banner"><div class="eyebrow">{html.escape(eyebrow)}</div>'
        f"<h1>{html.escape(title)}</h1><div class=\"lead\">{html.escape(lead)}</div>"
        f'<div class="stats">{items}</div><div class="source">{html.escape(source)}</div></div>',
        unsafe_allow_html=True,
    )


def section(title: str, num: int | None = None, kicker: str = "") -> None:
    num_html = f'<div class="num">{num:02d}</div>' if num is not None else ""
    kicker_html = f'<div class="kicker">{html.escape(kicker)}</div>' if kicker else ""
    st.markdown(
        f'<div class="sec">{num_html}<div>{kicker_html}<h2>{html.escape(title)}</h2></div></div>',
        unsafe_allow_html=True,
    )


def headline(markdown_text: str) -> None:
    text = html.escape(markdown_text)
    parts = text.split("**")
    rendered = "".join(f"<strong>{p}</strong>" if i % 2 else p for i, p in enumerate(parts))
    st.markdown(f'<div class="headline">{rendered}</div>', unsafe_allow_html=True)

