"""
Agmarknet API Service (placeholder)
Real integration point for fetching live/historical mandi prices, either
from the Government of India's Agmarknet portal or the data.gov.in
"Variety-wise Daily Market Prices Data of Commodity" dataset (filtered to
State=Telangana, District=Warangal). Currently unimplemented —
market_price_agent.py uses mock data until this is wired up.
"""
import os
from typing import Optional

import requests

AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY")

# TODO: replace with the real data.gov.in resource ID for the
# "Variety-wise Daily Market Prices Data of Commodity" dataset once you've
# looked it up on the dataset's API page.
BASE_URL = "https://api.data.gov.in/resource/PLACEHOLDER-RESOURCE-ID"


def fetch_mandi_prices(
    state: str = "Telangana",
    district: str = "Warangal",
    commodity: Optional[str] = None,
) -> dict:
    """
    TODO: Wire up a real call to the data.gov.in Agmarknet resource once
    AGMARKNET_API_KEY is set and BASE_URL points at the correct resource ID.
    Until then, market_price_agent.py falls back to mock data.
    """
    if not AGMARKNET_API_KEY:
        raise RuntimeError(
            "AGMARKNET_API_KEY not set. Add it to your .env file, or keep "
            "using the mock data in market_price_agent.py for now."
        )

    params = {
        "api-key": AGMARKNET_API_KEY,
        "format": "json",
        "filters[state.keyword]": state,
        "filters[district.keyword]": district,
    }
    if commodity:
        params["filters[commodity.keyword]"] = commodity

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
