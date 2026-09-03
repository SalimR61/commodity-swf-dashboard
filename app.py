# app.py
# Main Streamlit dashboard

import streamlit as st
from reference import COMMODITIES
from prices import get_current_price, get_price_windows, DATA_CAVEAT
from news import get_articles_for_commodity
from matching import find_fund_for_article
from commentary import generate_commentary

st.set_page_config(
    page_title="Commodity & SWF Dashboard",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 12px;
    border-radius: 8px;
    transition: transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
    color: #5F5E5A !important;
}
[data-testid="stMetricValue"] {
    color: #0B1929 !important;
}
[data-testid="stMetricDelta"] {
    color: #1B7A3D !important;
}
[data-testid="stMetricDelta"] svg {
    fill: #1B7A3D !important;
}
div.block-container {
    animation: fadeIn 0.5s ease-in;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#F0F2F4;font-size:44px;font-weight:800;margin-bottom:4px;border-bottom:3px solid #E8A33D;display:inline-block;padding-bottom:8px;">Commodity Compass</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#F0F2F4;font-size:16px;font-weight:600;margin:14px 0 4px;">Live commodity news, price movement, and the sovereign wealth funds behind the headlines.</p>
""", unsafe_allow_html=True)

st.markdown(f"""
<p style="color:#B8860B;font-size:12px;font-style:italic;margin:0 0 20px;">* {DATA_CAVEAT}</p>
""", unsafe_allow_html=True)

commodity_options = {details["display_name"]: key for key, details in COMMODITIES.items()}
selected_name = st.radio("Choose a commodity", options=list(commodity_options.keys()), horizontal=True)
commodity_key = commodity_options[selected_name]
display_name = selected_name

st.markdown(f"""
<h2 style="color:#F0F2F4;font-size:24px;font-weight:700;margin:20px 0 12px;">{display_name}</h2>
""", unsafe_allow_html=True)

price = get_current_price(commodity_key)
windows = get_price_windows(commodity_key)

st.metric(label="Current price", value=f"${price:.2f}")

cols = st.columns(5)
for col, (label, pct) in zip(cols, windows.items()):
    if pct is not None:
        col.metric(label=label, value=f"{pct}%", delta=f"{pct}%")

st.subheader("Related news")
articles = get_articles_for_commodity(commodity_key, page_size=3)

for article in articles:
    fund_match = find_fund_for_article(article, commodity_key)
    commentary = generate_commentary(article, windows, fund_match)

    fund_html = ""
    if fund_match:
        fund_html = f"<span style='background-color:#FDF3E3;color:#8A5A00;font-size:12px;padding:3px 10px;border-radius:12px;display:inline-block;margin-top:6px;'>💼 {fund_match['fund']} · {fund_match['country']}</span>"

    st.markdown(f"""
    <div style="background-color:#FFFFFF;border-left:4px solid #E8A33D;border-radius:8px;padding:16px 20px;margin-bottom:16px;">
        <a href="{article['webUrl']}" target="_blank" style="color:#0B1929;font-size:18px;font-weight:700;text-decoration:none;line-height:1.4;">{article['webTitle']}</a>
        <br>{fund_html}
        <p style="color:#3A3A3A;font-size:14px;margin:12px 0 0;line-height:1.5;">{commentary}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <p style="color:#F0F2F4;font-size:15px;font-weight:700;margin-bottom:6px;">About the builder</p>
    <p style="color:#B8BEC7;font-size:13px;line-height:1.6;margin:0;">
    Built by Salim, a third-year Economics student with a strong interest in commodities and geopolitics.
    This project was built to gain hands-on experience integrating live market data, news APIs, and AI into a working tool.
    </p>
    <p style="margin-top:10px;font-size:13px;">
    <a href="https://www.linkedin.com/in/salim-rachid-3247a8278/" target="_blank" style="color:#7FB8E8;">LinkedIn</a>
    &nbsp;·&nbsp;
    <span style="color:#7A828C;">GitHub repo coming soon</span>
    </p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <p style="color:#F0F2F4;font-size:15px;font-weight:700;margin-bottom:6px;">Data sources</p>
    <p style="color:#7A828C;font-size:12px;line-height:1.8;margin:0;">
    Prices: Yahoo Finance (yfinance)<br>
    News: The Guardian Open Platform<br>
    Commentary: Claude (Anthropic)
    </p>
    """, unsafe_allow_html=True)