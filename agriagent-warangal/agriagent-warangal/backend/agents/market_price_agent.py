"""
Market Price Agent
Returns mandi price data for Warangal-district mandis. Currently mocked with
sample data; backend/services/agmarknet_api.py will provide the real
Agmarknet / data.gov.in integration later (see the "Variety-wise Daily
Market Prices Data of Commodity" dataset).
"""
import random
from datetime import date
from typing import Optional

MANDIS = ["Warangal", "Hanamkonda", "Parkal", "Narsampet"]

# Mock baseline modal prices (INR per quintal)
BASE_PRICES = {
    "cotton": 7200,
    "paddy": 2100,
    "maize": 1900,
    "chilli": 14000,
    "turmeric": 8500,
    "red gram (tur)": 6800,
    "green gram (moong)": 7500,
    "groundnut": 6200,
    "soybean": 4300,
    "sugarcane": 320,
}


def _mock_price_for(crop: str, mandi: str) -> dict:
    crop_key = crop.lower().strip()
    base = BASE_PRICES.get(crop_key, 4000)

    random.seed(hash((crop_key, mandi, str(date.today()))) % (2**32))
    fluctuation = random.uniform(-0.06, 0.06)
    modal_price = round(base * (1 + fluctuation))
    min_price = round(modal_price * 0.95)
    max_price = round(modal_price * 1.05)

    trend_roll = random.random()
    if trend_roll < 0.4:
        trend = "up"
    elif trend_roll < 0.7:
        trend = "stable"
    else:
        trend = "down"

    return {
        "mandi": mandi,
        "crop": crop_key,
        "date": str(date.today()),
        "min_price": min_price,
        "max_price": max_price,
        "modal_price": modal_price,
        "trend": trend,
    }


def get_market_price(crop: str, mandi: Optional[str] = None) -> dict:
    """Returns current price + trend for one mandi, or all Warangal-area
    mandis if none is specified, plus a simple sell/hold recommendation."""
    target_mandis = [mandi] if mandi else MANDIS
    quotes = [_mock_price_for(crop, m) for m in target_mandis]
    best = max(quotes, key=lambda q: q["modal_price"])

    if best["trend"] == "up":
        recommendation = (
            f"Prices are trending up in {best['mandi']}; consider waiting a "
            "few days before selling if storage allows."
        )
    elif best["trend"] == "down":
        recommendation = (
            f"Prices are trending down in {best['mandi']}; consider selling "
            "soon to avoid further drops."
        )
    else:
        recommendation = f"Prices are stable; {best['mandi']} currently offers the best modal price."

    return {
        "source": "mock",
        "quotes": quotes,
        "best_mandi": best["mandi"],
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    print(get_market_price("cotton"))
