"""
Crop Recommendation Agent for AgriGenius.
Module 1:
- Input Needed: Water source (irrigated/rainfed), season (Kharif/Rabi)
  (Soil N-P-K, pH, temperature, humidity, rainfall pulled automatically from Soil Health Card + OpenWeatherMap).
- Output: Top 2-3 recommended crops, ranked with confidence scores, plus a plain-language reason for each.
Saves input & output records to MongoDB.
"""
import os
import pickle
import numpy as np
from typing import Dict, List, Any, Optional
from backend.services.weather_api import get_weather, get_soil_data
from backend.services.mongodb_service import save_record

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "crop_recommendation.pkl")


def recommend_crops(
    water_source: str = "Irrigated",
    season: str = "Kharif",
    soil_data: Optional[Dict[str, Any]] = None,
    weather_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Recommend top crops for Warangal district.
    Soil (N, P, K, pH) and Weather (temp, humidity, rainfall) parameters are
    retrieved automatically without prompting the farmer.
    """
    ws_norm = water_source.strip().capitalize() if water_source else "Irrigated"
    season_norm = season.strip().capitalize() if season else "Kharif"

    if not soil_data:
        soil_data = get_soil_data("Warangal")
    if not weather_data:
        weather_data = get_weather("Warangal")

    n_val = soil_data.get("N", 90)
    p_val = soil_data.get("P", 42)
    k_val = soil_data.get("K", 43)
    ph_val = soil_data.get("pH", 6.8)
    temp_val = weather_data.get("temperature", 29.5)
    hum_val = weather_data.get("humidity", 72)
    rain_val = weather_data.get("rainfall", 185.0)

    recommendations: List[Dict[str, Any]] = []

    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)
            features = np.array([[n_val, p_val, k_val, temp_val, hum_val, ph_val, rain_val]])
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(features)[0]
                classes = model.classes_
                top_indices = np.argsort(probs)[::-1][:3]
                for idx in top_indices:
                    recommendations.append({
                        "crop": str(classes[idx]).capitalize(),
                        "confidence": round(float(probs[idx]), 2),
                        "reason": f"Predicted by ML model using soil (N={n_val}, pH={ph_val}) and weather metrics."
                    })
            else:
                pred = model.predict(features)[0]
                recommendations.append({
                    "crop": str(pred).capitalize(),
                    "confidence": 0.90,
                    "reason": "Top prediction from scikit-learn model."
                })
        except Exception as e:
            print(f"[Crop Agent] Failed to run ML model at {MODEL_PATH}: {e}")

    if not recommendations:
        if season_norm == "Kharif":
            if ws_norm == "Irrigated":
                recommendations = [
                    {
                        "crop": "Cotton",
                        "confidence": 0.92,
                        "reason": f"Ideal for Warangal black cotton soil (pH {ph_val}) and irrigated Kharif season."
                    },
                    {
                        "crop": "Paddy",
                        "confidence": 0.88,
                        "reason": f"High yield potential under available irrigation and humidity ({hum_val}%)."
                    },
                    {
                        "crop": "Maize",
                        "confidence": 0.78,
                        "reason": f"Well-suited for medium rainfall ({rain_val}mm) and balanced soil N-P-K."
                    }
                ]
            else:
                recommendations = [
                    {
                        "crop": "Cotton",
                        "confidence": 0.89,
                        "reason": f"Drought-resilient staple crop suited for rainfed black soils in Warangal."
                    },
                    {
                        "crop": "Red Gram",
                        "confidence": 0.84,
                        "reason": f"Excellent pulse crop for rainfed Kharif requiring moderate moisture."
                    },
                    {
                        "crop": "Groundnut",
                        "confidence": 0.76,
                        "reason": f"Good soil-nitrogen fixing crop suitable for rainfed red/loamy patches."
                    }
                ]
        else:
            if ws_norm == "Irrigated":
                recommendations = [
                    {
                        "crop": "Paddy",
                        "confidence": 0.91,
                        "reason": f"Optimal for irrigated Rabi season with controlled water supply."
                    },
                    {
                        "crop": "Maize",
                        "confidence": 0.85,
                        "reason": f"High return commercial grain crop for Rabi season."
                    },
                    {
                        "crop": "Groundnut",
                        "confidence": 0.79,
                        "reason": f"Thrives in post-monsoon irrigated conditions with warm weather."
                    }
                ]
            else:
                recommendations = [
                    {
                        "crop": "Maize",
                        "confidence": 0.84,
                        "reason": f"Resilient grain crop requiring low moisture during Rabi season."
                    },
                    {
                        "crop": "Red Gram",
                        "confidence": 0.80,
                        "reason": f"Deep root system utilizes residual soil moisture effectively."
                    },
                    {
                        "crop": "Bengal Gram",
                        "confidence": 0.75,
                        "reason": f"Low water requirement legume suitable for cool Rabi dry conditions."
                    }
                ]

    result = {
        "water_source": ws_norm,
        "season": season_norm,
        "retrieved_soil": soil_data,
        "retrieved_weather": weather_data,
        "recommendations": recommendations,
        "model_used": "Scikit-Learn PKL Model" if os.path.exists(MODEL_PATH) else "Rule-based Warangal Expert Rules"
    }

    # Persist input & output to MongoDB
    save_record(
        collection_name="crop_recommendations",
        input_data={"water_source": ws_norm, "season": season_norm, "retrieved_soil": soil_data, "retrieved_weather": weather_data},
        output_data={"recommendations": recommendations},
        module_name="Crop Recommendation Agent"
    )

    return result
