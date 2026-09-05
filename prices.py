# prices.py
# Fetches current and historical commodity prices using yfinance

import os
import numpy as np
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

@st.cache_data(ttl=300)
def get_secondary_market_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="1d")
    return data["Close"].iloc[-1]

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

@st.cache_data(ttl=300)
def get_price_history(commodity_key):
    ticker_symbol = COMMODITIES[commodity_key]["ticker"]
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="13mo")
    return data[["Close"]]

@st.cache_data(ttl=300)
def get_rolling_volatility(commodity_key, window=20):
    """
    Computes the most recent 20-day annualised rolling volatility from
    daily log returns - the same methodology used in the offline R
    analysis (r_analysis/analysis.R), reimplemented here in Python so it
    can update live with the rest of the dashboard.

    Returns volatility as a percentage (e.g. 26.8), or None if there
    isn't enough price history yet to compute a full window.
    """
    history = get_price_history(commodity_key)
    closes = history["Close"]

    log_returns = np.log(closes / closes.shift(1))
    rolling_vol = log_returns.rolling(window=window).std() * np.sqrt(252)

    latest_vol = rolling_vol.iloc[-1]
    if np.isnan(latest_vol):
        return None

    return round(latest_vol * 100, 2)

def export_price_history_to_csv(output_dir="r_analysis/data"):
    """
    Exports full price history for every commodity in reference.py to individual CSVs.
    Used as the data source for the R/Stata volatility analysis layer.
    """
    os.makedirs(output_dir, exist_ok=True)
    exported = []

    for commodity_key, commodity in COMMODITIES.items():
        ticker = commodity["ticker"]
        name = commodity["display_name"]

        df = get_price_history(commodity_key)

        if df is None or df.empty:
            print(f"Skipped {name}: no data returned")
            continue

        filename = f"{output_dir}/{ticker.replace('=', '_').replace('.', '_')}.csv"
        df.to_csv(filename)
        exported.append(name)

    print(f"Exported {len(exported)} commodities: {', '.join(exported)}")
    return exported

if __name__ == "__main__":
    for commodity_key in COMMODITIES:
        price = get_current_price(commodity_key)
        display_name = COMMODITIES[commodity_key]["display_name"]
        print(f"\n{display_name}: ${price:.2f}")

        windows = get_price_windows(commodity_key)
        for label, pct in windows.items():
            print(f"  {label}: {pct}%")

    print(f"\nNote: {DATA_CAVEAT}")

    export_price_history_to_csv()