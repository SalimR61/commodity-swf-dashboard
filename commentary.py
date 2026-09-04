# commentary.py
# Generates short, data-grounded commentary on an article using the Anthropic API

import os
import streamlit as st
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@st.cache_data(ttl=1800)
def generate_commentary(article, price_windows, fund_match):
    headline = article["webTitle"]

    price_summary = ", ".join(
        f"{label}: {pct}%" for label, pct in price_windows.items() if pct is not None
    )

    fund_line = ""
    if fund_match:
        fund_line = f"Linked fund: {fund_match['fund']} ({fund_match['country']})."

    prompt = f"""You are writing a single, short analyst-style comment (max 30 words) for a commodities dashboard.

Headline: {headline}
Price changes: {price_summary}
{fund_line}

Write one sentence connecting the headline to the price data. Be specific and grounded - reference actual numbers. Do not invent facts not given above. If the numbers and headline don't obviously connect, say so honestly rather than forcing a link."""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


@st.cache_data(ttl=1800)
def generate_market_overview(commodity_key, display_name, windows, sensitivity, milestone, current_price):
    price_summary = ", ".join(
        f"{label}: {pct}%" for label, pct in windows.items() if pct is not None
    )

    milestone_line = ""
    if milestone is not None:
        distance = current_price - milestone
        milestone_line = f"Current price is {'above' if distance > 0 else 'below'} the ${milestone:,} milestone by ${abs(distance):.2f}."

    prompt = f"""You are writing a short market overview (120-150 words) for a commodities dashboard, aimed at someone with a finance/economics background.

Commodity: {display_name}
Current price: ${current_price:.2f}
Price changes: {price_summary}
Geopolitical sensitivity: {sensitivity}
{milestone_line}

Write a brief, grounded overview of the current state of this market: what the recent price action suggests, and why this commodity's geopolitical sensitivity rating is what it is (in general terms, not tied to a specific unverified event). Be specific and reference the actual numbers given. Do not invent specific events, deals, or statistics not provided above - if you don't have enough information to explain a move, say so rather than fabricating a cause. Write in a neutral, analytical tone, as if for a research note. Do not include a title, heading, or the word "overview" at the start - begin directly with the first sentence of analysis."""
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "text":
            return block.text
    return ""

if __name__ == "__main__":
    from news import get_articles_for_commodity
    from prices import get_price_windows
    from matching import find_fund_for_article

    articles = get_articles_for_commodity("oil", page_size=2)
    windows = get_price_windows("oil")

    for article in articles:
        fund_match = find_fund_for_article(article, "oil")
        commentary = generate_commentary(article, windows, fund_match)

        print(article["webTitle"])
        print(f"  Commentary: {commentary}")
        print()