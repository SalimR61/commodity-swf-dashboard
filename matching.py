# matching.py
# Matches a news article to a relevant country/fund based on mentions in the text

from reference import COUNTRY_FUNDS

def find_fund_for_article(article, commodity_key):
    headline = article["webTitle"].lower()
    trail_text = article.get("fields", {}).get("trailText", "").lower()

    relevant_funds = [
        entry for entry in COUNTRY_FUNDS
        if entry["commodity"] == commodity_key
    ]

    # Check the headline first - it's the strongest signal of what the
    # article is actually about, and avoids mismatches where a secondary
    # country mentioned only in passing gets matched instead
    for entry in relevant_funds:
        if entry["country"].lower() in headline:
            return entry

    # Fall back to trail text only if nothing matched in the headline
    for entry in relevant_funds:
        if entry["country"].lower() in trail_text:
            return entry

    return None

if __name__ == "__main__":
    from news import get_articles_for_commodity

    articles = get_articles_for_commodity("oil")
    for article in articles:
        match = find_fund_for_article(article, "oil")
        print(article["webTitle"])
        if match:
            print(f"  -> Matched: {match['country']} ({match['fund']})")
        else:
            print("  -> No country match found")
        print()