# prices.py
# Fetches current and historical commodity prices using yfinance

import yfinance as yf
import streamlit as st
from datetime import timedelta
from reference import COMMODITIES

DATA_CAVEAT = "Price changes use continuous futures contracts, which can show artificial jumps at monthly contract-roll dates - treat 1mo/12mo figures as indicative, not precise."

@st.cache_data(ttl=300)
def get_current_price(commodity_key):
    ticker_symbol = COMMODITIES[commodity_key]["ticker"]
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="1d")
    latest_price = data["Close"].iloc[-1]
    return latest_price

# Compares the latest price to the price roughly N days ago for each
# window. Uses "on or before target date" rather than an exact date match,
# since markets are closed weekends/holidays so an exact date rarely exists
#
# KNOWN LIMITATION: tickers ending in "=F" are continuous futures contracts,
# not spot prices. When the front-month contract rolls (expires and is
# replaced, roughly monthly), the price series can jump in a way that
# doesn't reflect the actual commodity moving. Observed: all four
# commodities in this project show unusually large 1mo/12mo % changes
# compared to their 1d moves, consistent with roll effects rather than
# real market moves. Not fixed here - flagged in the dashboard instead
# (see DATA_CAVEAT above).

@st.cache_data(ttl=300)
def get_price_windows(commodity_key):
    ticker_symbol = COMMODITIES[commodity_key]["ticker"]
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="13mo")
    print(f"DEBUG: {commodity_key} - rows returned: {len(data)}")

    latest_price = data["Close"].iloc[-1]
    latest_date = data.index[-1]

    # Days-back per window - deliberately approximate (e.g. "1mo" = 30
    # calendar days, not the actual number of days in that month)
    windows = {
        "1d": 1,
        "3d": 3,
        "1w": 7,
        "1mo": 30,
        "12mo": 365,
    }

    results = {}
    for label, days_back in windows.items():
        target_date = latest_date - timedelta(days=days_back)
        past_data = data[data.index <= target_date]

        # Guards against commodities with less than a year of trading
        # history available, or gaps at the very start of the dataset
        if past_data.empty:
            results[label] = None
            continue

        past_price = past_data["Close"].iloc[-1]
        pct_change = (latest_price - past_price) / past_price * 100
        results[label] = round(pct_change, 2)

    return results

if __name__ == "__main__":
    for commodity_key in COMMODITIES:
        price = get_current_price(commodity_key)
        display_name = COMMODITIES[commodity_key]["display_name"]
        print(f"\n{display_name}: ${price:.2f}")

        windows = get_price_windows(commodity_key)
        for label, pct in windows.items():
            print(f"  {label}: {pct}%")

    print(f"\nNote: {DATA_CAVEAT}")