# app.py
# Main Streamlit dashboard

import streamlit as st
from datetime import datetime
from reference import COMMODITIES
from prices import get_current_price, get_price_windows, get_price_history,get_secondary_market_price, DATA_CAVEAT
from news import get_articles_for_commodity
from matching import find_fund_for_article, match_articles_to_price_dates
from commentary import generate_commentary, generate_market_overview
import plotly.graph_objects as go

st.set_page_config(
    page_title="Commodity Compass",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #EAEAE7;
    padding: 12px;
    border-radius: 8px;
    transition: transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
    color: #8A8D91 !important;
}
[data-testid="stMetricValue"] {
    color: #0B1929 !important;
}
[data-testid="stMetricDelta"] {
    color: #166534 !important;
}
[data-testid="stMetricDelta"] svg {
    fill: #166534 !important;
}
[data-testid="stPlotlyChart"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #EAEAE7;
}
div.block-container {
    animation: fadeIn 0.5s ease-in;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
div[role="radiogroup"] {
    gap: 12px;
    margin-bottom: 8px;
}
div[role="radiogroup"] label {
    background-color: #FFFFFF;
    border: 1.5px solid #EAEAE7;
    border-radius: 10px;
    padding: 16px 28px;
    transition: all 0.2s ease;
    cursor: pointer;
    min-width: 140px;
}
div[role="radiogroup"] label:hover {
    border-color: #0B1929;
}
div[role="radiogroup"] label svg {
    display: none;
}
div[role="radiogroup"] label [data-testid="stMarkdownContainer"] p {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #0B1929 !important;
    margin: 0 !important;
}
div[role="radiogroup"] label:has(input:checked) {
    background-color: #0B1929;
    border-color: #0B1929;
}
div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#0B1929;font-size:38px;font-weight:800;margin-bottom:4px;border-bottom:3px solid #B8860B;display:inline-block;padding-bottom:6px;">Commodity Compass</p>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#3A3A3A;font-size:15px;font-weight:600;margin:14px 0 4px;">Live commodity news, price movement, and the sovereign wealth funds behind the headlines.</p>
""", unsafe_allow_html=True)

st.markdown(f"""
<p style="color:#9C6B1F;font-size:12px;font-style:italic;margin:0 0 6px;">* {DATA_CAVEAT}</p>
""", unsafe_allow_html=True)

st.markdown(f"""
<p style="color:#8A8D91;font-size:11px;margin:0 0 20px;">Page loaded {datetime.now().strftime('%H:%M:%S')} — prices and news may be cached for up to 5 minutes.</p>
""", unsafe_allow_html=True)

commodity_options = {details["display_name"]: key for key, details in COMMODITIES.items()}
selected_name = st.radio("Choose a commodity", options=list(commodity_options.keys()), horizontal=True)
commodity_key = commodity_options[selected_name]
display_name = selected_name

sensitivity = COMMODITIES[commodity_key]["geopolitical_sensitivity"]
sensitivity_bg = "#FDEDEC" if sensitivity == "High" else "#FBEEDC"
sensitivity_color = "#B91C1C" if sensitivity == "High" else "#9C6B1F"
milestone = COMMODITIES[commodity_key].get("milestone")

price = get_current_price(commodity_key)
windows = get_price_windows(commodity_key)

st.markdown(f"""
<span style="color:#0B1929;font-size:22px;font-weight:700;">{display_name}</span>
<span style="background-color:{sensitivity_bg};color:{sensitivity_color};font-size:11px;font-weight:600;padding:3px 10px;border-radius:10px;margin-left:10px;">⚡ {sensitivity} geopolitical sensitivity</span>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
st.metric(label="Current price", value=f"${price:.2f}")
secondary = COMMODITIES[commodity_key].get("secondary_market")
if secondary:
    secondary_price = get_secondary_market_price(secondary["ticker"])
    st.caption(f"{secondary['name']}: ${secondary_price:.2f}")

cols = st.columns(5)
for col, (label, pct) in zip(cols, windows.items()):
    if pct is not None:
        col.metric(label=label, value=f"{pct}%", delta=f"{pct}%")

with st.spinner("Generating market overview..."):
    overview = generate_market_overview(commodity_key, display_name, windows, sensitivity, milestone, price)

st.markdown(f"""
<div style="background-color:#0B1929;border-radius:8px;padding:18px 22px;margin:16px 0;">
<p style="color:#B8860B;font-size:12px;font-weight:700;margin:0 0 8px;text-transform:uppercase;letter-spacing:0.5px;">Market Overview</p>
<p style="color:#D6DBE1;font-size:14px;line-height:1.7;margin:0;">{overview}</p>
</div>
""", unsafe_allow_html=True)

history = get_price_history(commodity_key)
articles = get_articles_for_commodity(commodity_key, page_size=3)
matched = match_articles_to_price_dates(articles, history)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=history.index,
    y=history["Close"],
    mode="lines",
    line=dict(color="#0B1929", width=2),
    name=display_name,
))

if milestone is not None:
    fig.add_hline(
        y=milestone,
        line_dash="dash",
        line_color="#B8860B",
        annotation_text=f"${milestone:,} milestone",
        annotation_position="top left",
    )

if matched:
    fig.add_trace(go.Scatter(
        x=[m["date"] for m in matched],
        y=[m["price"] for m in matched],
        mode="markers",
        marker=dict(size=9, color="#B8860B", line=dict(width=1.5, color="#FFFFFF"), opacity=0.95),
        text=[m["article"]["webTitle"] for m in matched],
        hovertemplate="<b>%{text}</b><br>$%{y:.2f}<extra></extra>",
        name="News",
        showlegend=False,
    ))

fig.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#3A3A3A"),
    height=400,
    margin=dict(t=60, b=40, l=40, r=40),
    xaxis=dict(gridcolor="#F0F0EE", color="#3A3A3A"),
    yaxis=dict(gridcolor="#F0F0EE", title="Price ($)", color="#3A3A3A"),
)

st.plotly_chart(fig, use_container_width=True)

if milestone is not None:
    st.markdown(f"""
    <p style="color:#8A8D91;font-size:12px;margin:-8px 0 20px;">
    The dashed line marks ${milestone:,} — a widely watched psychological price level in {display_name.lower()} markets, often referenced in trading commentary as a signal of market sentiment.
    </p>
    """, unsafe_allow_html=True)

st.markdown("""
<p style="color:#0B1929;font-size:18px;font-weight:700;margin:20px 0 10px;">Related news</p>
""", unsafe_allow_html=True)

if not articles:
    st.info(f"No highly relevant {display_name.lower()} articles found in the last few days. Check back later or try another commodity.")
else:
    for article in articles:
        fund_match = find_fund_for_article(article, commodity_key)

        with st.spinner("Generating analysis..."):
            commentary = generate_commentary(article, windows, fund_match)

        fund_html = ""
        if fund_match:
            fund_html = f"<span style='background-color:#FBEEDC;color:#9C6B1F;font-size:12px;padding:3px 10px;border-radius:12px;display:inline-block;margin-top:6px;'>💼 {fund_match['fund']} · {fund_match['country']}</span>"

        st.markdown(f"""
        <div style="background-color:#FFFFFF;border:1px solid #EAEAE7;border-left:4px solid #B8860B;border-radius:8px;padding:16px 20px;margin-bottom:16px;">
            <a href="{article['webUrl']}" target="_blank" style="color:#0B1929;font-size:18px;font-weight:700;text-decoration:none;line-height:1.4;">{article['webTitle']}</a>
            <br>{fund_html}
            <p style="color:#3A3A3A;font-size:14px;margin:12px 0 0;line-height:1.5;">{commentary}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

with st.expander("How this dashboard works"):
    st.markdown("""
    For the selected commodity, this tool pulls recent, relevance-ranked news articles, live and historical price
    data, and matches each article to the country it relates to and that country's sovereign wealth fund. Claude
    (Anthropic's AI model) then generates short commentary grounded specifically in the real price figures already
    calculated — it's asked to reference actual numbers and explicitly permitted to say when a headline and the
    price data don't clearly connect, rather than invent a link.
    """)

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <p style="color:#0B1929;font-size:15px;font-weight:700;margin-bottom:6px;">About the builder</p>
    <p style="color:#5F6368;font-size:13px;line-height:1.6;margin:0;">
    Built by Salim, a third-year Economics student with a strong interest in commodities and geopolitics.
    This project was built to gain hands-on experience integrating live market data, news APIs, and AI into a working tool.
    </p>
    <p style="margin-top:10px;font-size:13px;">
    <a href="https://www.linkedin.com/in/salim-rachid-3247a8278/" target="_blank" style="color:#0B1929;font-weight:600;">LinkedIn</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/SalimR61/commodity-swf-dashboard" target="_blank" style="color:#0B1929;font-weight:600;">GitHub</a>
    </p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <p style="color:#0B1929;font-size:15px;font-weight:700;margin-bottom:6px;">Data sources</p>
    <p style="color:#8A8D91;font-size:12px;line-height:1.8;margin:0;">
    Prices: Yahoo Finance (yfinance)<br>
    News: The Guardian Open Platform<br>
    Commentary: Claude (Anthropic)
    </p>
    """, unsafe_allow_html=True)