# reference.py
# Holds our commodity and sovereign wealth fund reference data

# Each commodity maps to its Yahoo Finance ticker (used to fetch live
# prices), a human-readable name (used in the dashboard UI), search
# terms used to find relevant news articles via the Guardian API, an
# optional "milestone" - a well-known round-number price level (e.g.
# $100 oil, $5,000 gold), and a geopolitical_sensitivity label.
#
# milestone is None where no equally famous threshold genuinely exists,
# rather than inventing an arbitrary number.
#
# geopolitical_sensitivity is a simple, manually-assigned label reflecting
# how directly each commodity's price tends to react to geopolitical events
# (sanctions, conflict, export controls) based on observed market behaviour -
# not a modeled or quantitative score.
COMMODITIES = {
    "oil": {
        "ticker": "CL=F",
        "display_name": "Crude Oil (WTI)",
        "search_terms": ["oil price", "crude oil", "oil market", "OPEC"],
        "milestone": 100,
        "geopolitical_sensitivity": "High",
        "secondary_market": {"ticker": "BZ=F", "name": "Brent Crude"},
    },
    "gas": {
        "ticker": "NG=F",
        "display_name": "Natural Gas",
        "search_terms": ["natural gas price", "gas market", "LNG"],
        "milestone": None,
        "geopolitical_sensitivity": "High",
        "secondary_market": None
    },
    "copper": {
        "ticker": "HG=F",
        "display_name": "Copper",
        "search_terms": ["copper price", "copper market", "copper mine"],
        "milestone": None,
        "geopolitical_sensitivity": "Moderate",
        "secondary_market": None,
    },
    "gold": {
        "ticker": "GC=F",
        "display_name": "Gold",
        "search_terms": ["gold price", "gold market", "gold reserves"],
        "milestone": 5000,
        "geopolitical_sensitivity": "Moderate",
        "secondary_market": None,
    },
}

# One fund per country, chosen as the most prominent/commodity-relevant fund.
# Simplification: some countries (e.g. UAE) actually run multiple SWFs -
# a fuller version would need logic to pick between them.
COUNTRY_FUNDS = [
    {"country": "Saudi Arabia", "commodity": "oil", "fund": "Public Investment Fund (PIF)"},
    {"country": "Kuwait", "commodity": "oil", "fund": "Kuwait Investment Authority (KIA)"},
    {"country": "UAE", "commodity": "oil", "fund": "Abu Dhabi Investment Authority (ADIA)"},
    {"country": "Qatar", "commodity": "gas", "fund": "Qatar Investment Authority (QIA)"},
    {"country": "Norway", "commodity": "oil", "fund": "Norges Bank Investment Management (NBIM)"},
    {"country": "Russia", "commodity": "gas", "fund": "National Wealth Fund (NWF)"},
    # Iraq has no dedicated national SWF - noted explicitly rather than
    # inventing one or leaving the country unmatched
    {"country": "Iraq", "commodity": "oil", "fund": "Iraq's sovereign holdings (state-managed, no dedicated SWF)"},
    {"country": "Nigeria", "commodity": "oil", "fund": "Nigeria Sovereign Investment Authority (NSIA)"},
    {"country": "Angola", "commodity": "oil", "fund": "Fundo Soberano de Angola (FSDEA)"},
    {"country": "Kazakhstan", "commodity": "oil", "fund": "Samruk-Kazyna / National Fund of Kazakhstan"},
    {"country": "Azerbaijan", "commodity": "oil", "fund": "State Oil Fund of Azerbaijan (SOFAZ)"},
    {"country": "Oman", "commodity": "oil", "fund": "Oman Investment Authority (OIA)"},
    {"country": "Bahrain", "commodity": "oil", "fund": "Mumtalakat"},
    {"country": "Chile", "commodity": "copper", "fund": "Economic and Social Stabilization Fund (ESSF)"},
    {"country": "Peru", "commodity": "copper", "fund": "Fiscal Stabilization Fund (Peru)"},
    {"country": "Australia", "commodity": "gold", "fund": "Future Fund"},
    {"country": "Botswana", "commodity": "gold", "fund": "Pula Fund"},
    {"country": "Mongolia", "commodity": "copper", "fund": "Fiscal Stability Fund (Mongolia)"},
    # Sub-national funds included deliberately - most G7 countries don't
    # have a national commodity-linked SWF, but these regional ones exist
    {"country": "USA", "commodity": "oil", "fund": "Alaska Permanent Fund (state-level, not federal)"},
    {"country": "Canada", "commodity": "oil", "fund": "Alberta Heritage Savings Trust Fund (provincial, not federal)"},
    {"country": "Iran", "commodity": "oil", "fund": "National Development Fund of Iran (NDFI) - operates under international sanctions"}
]

# Sanity-check block - only runs when this file is executed directly,
# not when other files later import COMMODITIES/COUNTRY_FUNDS from it
if __name__ == "__main__":
    print("Commodities we track:")
    for key, details in COMMODITIES.items():
        print(f"  {key} -> {details['display_name']} (ticker: {details['ticker']})")

    print("\nCountry-fund links:")
    for entry in COUNTRY_FUNDS:
        print(f"  {entry['country']} ({entry['commodity']}) -> {entry['fund']}")