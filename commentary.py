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