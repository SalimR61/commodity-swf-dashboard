# Commodity Compass

An interactive dashboard pairing live commodity news with real price movement, an annotated price history chart, AI-generated market analysis, and the sovereign wealth fund tied to the country each story relates to — built to explore how commodity markets and geopolitics intersect.

**Live demo:** *(link coming soon)*

![Dashboard screenshot](Screenshot.png)

## What it does

For a chosen commodity (oil, gas, copper, or gold), the dashboard:
- Pulls recent, relevant news articles (The Guardian API)
- Shows the current price and % change over five time windows (1d, 3d, 1w, 1mo, 12mo), via Yahoo Finance
- Matches each article to the country it's about, and looks up the relevant sovereign wealth fund
- Generates a short, data-grounded commentary on each article using Claude (Anthropic's AI model) — grounded specifically in the real price numbers already calculated, not left to invent figures
- Displays an interactive price chart with hover-based annotations linking headlines to the exact price point they relate to, plus a milestone reference line for commodities with a well-known psychological price level
- Generates a longer market overview per commodity, alongside the per-article commentary, summarizing recent price action and explaining its geopolitical sensitivity rating

## How it works

The project is split into five focused Python modules:

| File | Responsibility |
|---|---|
| `reference.py` | Commodity and country/fund reference data |
| `prices.py` | Live price + historical % change windows (yfinance) |
| `news.py` | Relevance-ranked news fetching (The Guardian API) |
| `matching.py` | Matches an article to a country/fund based on headline text |
| `commentary.py` | Generates grounded AI commentary via the Anthropic API |
| `app.py` | Streamlit dashboard tying everything together |

## Known limitations

Built and documented honestly rather than glossed over:

- **Futures contract roll effects**: price tickers track continuous futures contracts, which can show artificial jumps at monthly contract-roll dates. 1mo/12mo figures should be read as indicative, not precise (flagged directly in the dashboard).
- **Single fund per country**: some countries (e.g. UAE) run multiple sovereign wealth funds; this project matches to one representative fund per country as a deliberate simplification.
- **Single news source**: uses The Guardian specifically, chosen for its production-safe free tier; a fuller version would aggregate across multiple outlets.
- **Headline-based matching**: country matching is based on text mentions in the headline (falling back to the article summary) — a reasonably reliable heuristic, but not full NLP-based entity recognition.

## Future improvements

Deliberately scoped out of this version, noted honestly rather than left unaddressed:

- **Multi-currency support**: prices are currently USD-only; a fuller version would let users switch currency via a live forex API.
- **Full Brent Crude tracking**: oil currently shows Brent as a simple reference price alongside WTI; a fuller version would give Brent its own complete price-window and chart view, toggleable against WTI.
- **Multi-source news aggregation**: currently uses The Guardian only, chosen for its production-safe free tier; a fuller version would aggregate across several outlets.
- **R/Stata quantitative layer**: exporting the underlying price history for a proper time-series analysis (e.g. volatility clustering, return distributions) in R, tying the project to my econometrics coursework directly.

## Tech stack

Python · Streamlit · yfinance · Guardian Open Platform API · Anthropic API (Claude)

## Running it locally

```bash
git clone https://github.com/SalimR61/commodity-swf-dashboard.git
cd commodity-swf-dashboard
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

Create a `.env` file with:

GUARDIAN_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

Then run:
```bash
streamlit run app.py
```

## About

Built by Salim, a third-year Economics student with a strong interest in commodities and geopolitics, as a hands-on project integrating live market data, news APIs, and AI into a working tool.

[LinkedIn](https://www.linkedin.com/in/salim-rachid-3247a8278/)