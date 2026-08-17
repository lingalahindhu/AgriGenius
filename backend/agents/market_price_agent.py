"""
Market Price Agent for AgriGenius.
Module 5:
- Input Needed: Crop name, mandi preference (Warangal, Hanamkonda, Parkal, Narsampet),
  harvest date (auto-passed from Module 3 if available).
- Output: Current price per quintal at each mandi, trend direction (up/down/stable),
  and a recommendation on when and where to sell.
Saves input & output records to MongoDB.
"""
from typing import Dict, List, Any, Optional
from backend.services.agmarknet_api import fetch_mandi_prices
from backend.services.mongodb_service import save_record


def get_market_price_analysis(
    crop: Optional[str] = "Cotton",
    mandi: Optional[str] = None,
    harvest_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze current market prices across Warangal district mandis and return selling advice.
    """
    target_crop = crop.strip().capitalize() if crop else "Cotton"
    raw_prices = fetch_mandi_prices(crop=target_crop, mandi=mandi)

    if not raw_prices:
        output = {
            "crop": target_crop,
            "mandi_prices": [],
            "best_mandi": None,
            "recommendation": f"No market data currently available for {target_crop} in specified mandis."
        }
        return output

    best_record = max(raw_prices, key=lambda x: x["current_price_per_quintal"])
    best_mandi = best_record["mandi"]
    best_price = best_record["current_price_per_quintal"]
    trend = best_record["trend"]

    if trend == "up":
        recommendation = (
            f"Prices for {target_crop} are trending upward. {best_mandi} mandi currently offers the best price "
            f"at ₹{best_price:,}/quintal. Consider holding stock for 3-5 days or selling at {best_mandi} for maximum returns."
        )
    elif trend == "down":
        recommendation = (
            f"Prices for {target_crop} show a slight downward trend. {best_mandi} mandi offers the top price "
            f"at ₹{best_price:,}/quintal. It is advised to liquidate ready harvest promptly to avoid further drop."
        )
    else:
        recommendation = (
            f"Prices for {target_crop} are stable. {best_mandi} mandi offers the highest rate at ₹{best_price:,}/quintal. "
            f"Selling at {best_mandi} is a safe option."
        )

    output = {
        "crop": target_crop,
        "query_mandi": mandi or "All Warangal District Mandis",
        "mandi_prices": raw_prices,
        "best_mandi": best_mandi,
        "highest_price": best_price,
        "unit": "₹ / Quintal",
        "trend": trend,
        "recommendation": recommendation,
        "harvest_date_noted": harvest_date or "Immediate Harvest"
    }

    save_record(
        collection_name="market_prices",
        input_data={"crop": target_crop, "mandi": mandi, "harvest_date": harvest_date},
        output_data=output,
        module_name="Market Price Agent"
    )

    return output
