# news.py
# Fetches recent news articles from The Guardian API

import os
import requests
import streamlit as st
from dotenv import load_dotenv
from reference import COMMODITIES

load_dotenv()
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")

@st.cache_data(ttl=300)
def get_articles_for_commodity(commodity_key, page_size=5):
    search_terms = COMMODITIES[commodity_key]["search_terms"]
    quoted_terms = [f'"{term}"' for term in search_terms]
    query = " OR ".join(quoted_terms)

    url = "https://content.guardianapis.com/search"
    params = {
        "q": query,
        "api-key": GUARDIAN_API_KEY,
        "page-size": page_size,
        "order-by": "relevance",
        "type": "article",
        "show-fields": "trailText",
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["response"]["results"]

if __name__ == "__main__":
    articles = get_articles_for_commodity("oil")
    for article in articles:
        print(article["webTitle"])
        print(article["webPublicationDate"])
        print(article["webUrl"])
        print()