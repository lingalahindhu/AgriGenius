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
    mandal: Optional[str] = None,
    village: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    soil_data: Optional[Dict[str, Any]] = None,
    weather_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Recommend top crops for Warangal district with hyper-local village & mandal precision.
    Soil (N, P, K, pH, Soil Type) and Weather (temp, humidity, rainfall) parameters are
    retrieved automatically for the selected village/mandal.
    """
    ws_norm = water_source.strip().capitalize() if water_source else "Irrigated"
    season_norm = season.strip().capitalize() if season else "Kharif"

    if not soil_data:
        soil_data = get_soil_data(location="Warangal", mandal=mandal, village=village)

    lat_to_use = latitude if latitude is not None else soil_data.get("latitude")
    lon_to_use = longitude if longitude is not None else soil_data.get("longitude")

    if not weather_data:
        weather_data = get_weather(location="Warangal", lat=lat_to_use, lon=lon_to_use, mandal=mandal, village=village)

    n_val = soil_data.get("N", 90)
    p_val = soil_data.get("P", 42)
    k_val = soil_data.get("K", 43)
    ph_val = soil_data.get("pH", 6.8)
    soil_type = soil_data.get("soil_type", "Deep Black Cotton Soil")
    nearest_mandi = soil_data.get("nearest_mandi", "Enumamula Warangal")
    mandi_distance = soil_data.get("mandi_distance_km", 10.0)

    temp_val = weather_data.get("temperature", 29.5)
    hum_val = weather_data.get("humidity", 72)
    rain_val = weather_data.get("rainfall", 185.0)

    recommendations: List[Dict[str, Any]] = []

    # 1. Scikit-Learn Model Prediction (if PKL is present)
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
                        "reason": f"Predicted by ML model using local soil ({soil_type}, N={n_val}, pH={ph_val}) and live weather."
                    })
            else:
                pred = model.predict(features)[0]
                recommendations.append({
                    "crop": str(pred).capitalize(),
                    "confidence": 0.90,
                    "reason": f"Predicted by ML model for {soil_type} profile."
                })
        except Exception as e:
            print(f"[Crop Agent] Failed to run ML model at {MODEL_PATH}: {e}")

    # 2. Expert Regional Agronomy Rules (Hyper-local Warangal agronomic logic)
    if not recommendations:
        is_red_soil = ("red" in soil_type.lower()) or ("chalka" in soil_type.lower())

        if is_red_soil:
            # Red Sandy Loams / Chalka soils: Well drained, lighter texture, excellent for groundnut, maize & pulses
            if season_norm == "Kharif":
                if ws_norm == "Irrigated":
                    recommendations = [
                        {
                            "crop": "Maize",
                            "confidence": 0.93,
                            "reason": f"Highly responsive to well-drained {soil_type} (pH {ph_val}); quick market transport to {nearest_mandi} ({mandi_distance} km)."
                        },
                        {
                            "crop": "Groundnut",
                            "confidence": 0.89,
                            "reason": f"Loose, friable red soil allows superior peg penetration and high pod yield with controlled irrigation."
                        },
                        {
                            "crop": "Cotton",
                            "confidence": 0.80,
                            "reason": f"Feasible with regular irrigation and split N-fertilizer application (N={n_val}) to prevent nutrient leaching in light soils."
                        }
                    ]
                else:
                    recommendations = [
                        {
                            "crop": "Red Gram",
                            "confidence": 0.91,
                            "reason": f"Deep taproot thrives in rainfed {soil_type}, tolerating low moisture while enriching soil nitrogen."
                        },
                        {
                            "crop": "Groundnut",
                            "confidence": 0.86,
                            "reason": f"Hardy oilseed suited for rainfed red chalka tracts; low water footprint with strong market demand."
                        },
                        {
                            "crop": "Maize",
                            "confidence": 0.78,
                            "reason": f"Reliable grain crop under moderate rainfall ({rain_val}mm) with quick crop cycle."
                        }
                    ]
            else:  # Rabi Season
                if ws_norm == "Irrigated":
                    recommendations = [
                        {
                            "crop": "Maize",
                            "confidence": 0.92,
                            "reason": f"Premier commercial grain for winter in {mandal or 'Warangal'}; rapid growth in well-drained {soil_type}."
                        },
                        {
                            "crop": "Groundnut",
                            "confidence": 0.88,
                            "reason": f"Thrives in post-monsoon irrigated red loams with high oil content and premium price at {nearest_mandi}."
                        },
                        {
                            "crop": "Bengal Gram",
                            "confidence": 0.82,
                            "reason": f"High return short-duration pulse well-adapted to mild winter temperatures ({temp_val}°C)."
                        }
                    ]
                else:
                    recommendations = [
                        {
                            "crop": "Bengal Gram",
                            "confidence": 0.86,
                            "reason": f"Ideal low-water winter legume; utilizes residual moisture efficiently in {soil_type}."
                        },
                        {
                            "crop": "Red Gram",
                            "confidence": 0.80,
                            "reason": f"Deep-rooted drought-hardy legume suitable for dry Rabi conditions."
                        },
                        {
                            "crop": "Maize",
                            "confidence": 0.75,
                            "reason": f"Requires light moisture; suitable for drought-tolerant winter hybrid varieties."
                        }
                    ]
        else:
            # Heavy Black Cotton Soils / Clay Loams (Wardhannapet, Geesugonda, Narsampet, etc.)
            if season_norm == "Kharif":
                if ws_norm == "Irrigated":
                    recommendations = [
                        {
                            "crop": "Cotton",
                            "confidence": 0.94,
                            "reason": f"Exceptional match for {soil_type} (pH {ph_val}); high trading volume and top returns at {nearest_mandi} ({mandi_distance} km)."
                        },
                        {
                            "crop": "Paddy",
                            "confidence": 0.90,
                            "reason": f"High water-retention clay profile and humidity ({hum_val}%) maximize tillering and grain weight."
                        },
                        {
                            "crop": "Maize",
                            "confidence": 0.81,
                            "reason": f"High yield potential under irrigation with balanced soil fertility (N={n_val}, P={p_val}, K={k_val})."
                        }
                    ]
                else:
                    recommendations = [
                        {
                            "crop": "Cotton",
                            "confidence": 0.91,
                            "reason": f"High moisture retention of {soil_type} buffers dry intervals between monsoon spells in Warangal."
                        },
                        {
                            "crop": "Red Gram",
                            "confidence": 0.85,
                            "reason": f"Deep rooting pattern extracts subsoil moisture; excellent intercrop or sole crop for rainfed black soils."
                        },
                        {
                            "crop": "Green Gram",
                            "confidence": 0.77,
                            "reason": f"Short duration pulse suitable for quick Kharif harvest before winter moisture dries."
                        }
                    ]
            else:  # Rabi Season
                if ws_norm == "Irrigated":
                    recommendations = [
                        {
                            "crop": "Paddy",
                            "confidence": 0.92,
                            "reason": f"High winter sunshine and assured irrigation produce bumper yields in heavy soils near {nearest_mandi}."
                        },
                        {
                            "crop": "Maize",
                            "confidence": 0.87,
                            "reason": f"Top cash grain crop for Rabi in {mandal or 'Warangal'}; stable market price."
                        },
                        {
                            "crop": "Groundnut",
                            "confidence": 0.80,
                            "reason": f"Irrigated winter oilseed crop yielding bold nuts with good market value."
                        }
                    ]
                else:
                    recommendations = [
                        {
                            "crop": "Maize",
                            "confidence": 0.85,
                            "reason": f"Resilient grain crop extracting deep moisture in retentive {soil_type}."
                        },
                        {
                            "crop": "Bengal Gram",
                            "confidence": 0.82,
                            "reason": f"Cold-tolerant legume thriving on residual black soil moisture in cool Rabi nights."
                        },
                        {
                            "crop": "Red Gram",
                            "confidence": 0.78,
                            "reason": f"Hardy pulse utilizing deep moisture stores effectively."
                        }
                    ]

    result = {
        "water_source": ws_norm,
        "season": season_norm,
        "mandal": soil_data.get("mandal", mandal),
        "village": soil_data.get("village", village),
        "retrieved_soil": soil_data,
        "retrieved_weather": weather_data,
        "recommendations": recommendations,
        "model_used": "Scikit-Learn PKL Model" if os.path.exists(MODEL_PATH) else f"Warangal Expert Agro-Rules ({soil_type})"
    }

    # Persist input & output to MongoDB
    save_record(
        collection_name="crop_recommendations",
        input_data={
            "water_source": ws_norm,
            "season": season_norm,
            "mandal": soil_data.get("mandal", mandal),
            "village": soil_data.get("village", village),
            "retrieved_soil": soil_data,
            "retrieved_weather": weather_data
        },
        output_data={"recommendations": recommendations},
        module_name="Crop Recommendation Agent"
    )

    return result

