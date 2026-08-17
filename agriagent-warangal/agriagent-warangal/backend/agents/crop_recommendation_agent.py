"""
Crop Recommendation Agent
Loads a trained scikit-learn model (if present) to recommend the top crops
based on soil N/P/K, pH, temperature, humidity and rainfall. Falls back to
simple rule-based mock logic when no trained model file exists yet.

TODO: Train on the Kaggle "Crop Recommendation Dataset" and save the fitted
classifier to backend/models/crop_recommendation_model.pkl (joblib format,
must expose predict_proba + classes_).
"""
import os
import random
from typing import Optional

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "crop_recommendation_model.pkl"
)

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    if os.path.exists(MODEL_PATH):
        import joblib
        _model = joblib.load(MODEL_PATH)
    return _model


def _mock_recommend(water_source: str, season: str) -> list:
    """Simple rule-of-thumb mock logic used until the real model is trained."""
    if season.lower() == "kharif":
        pool = ["cotton", "paddy", "maize", "red gram (tur)", "soybean"]
    else:
        pool = ["maize", "chilli", "groundnut", "turmeric", "green gram (moong)"]

    if water_source.lower() == "irrigated" and "paddy" not in pool:
        pool = ["paddy"] + pool

    picks = list(dict.fromkeys(pool))[:3]
    random.seed(hash((water_source, season)) % (2**32))
    confidences = sorted([round(random.uniform(0.55, 0.95), 2) for _ in picks], reverse=True)

    return [
        {
            "crop": crop,
            "confidence": conf,
            "reason": (
                f"Historically well-suited for {season} season with "
                f"{water_source} irrigation in Warangal district (mock logic)."
            ),
        }
        for crop, conf in zip(picks, confidences)
    ]


def recommend_crops(
    nitrogen: Optional[float] = None,
    phosphorus: Optional[float] = None,
    potassium: Optional[float] = None,
    ph: Optional[float] = None,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    rainfall: Optional[float] = None,
    water_source: str = "irrigated",
    season: str = "Kharif",
) -> dict:
    """Returns the top-3 recommended crops with confidence scores and a
    plain-language reason for each."""
    model = _load_model()
    inputs_complete = None not in (nitrogen, phosphorus, potassium, ph, temperature, humidity, rainfall)

    if model is not None and inputs_complete:
        features = [[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]]
        try:
            proba = model.predict_proba(features)[0]
            classes = model.classes_
            top_idx = proba.argsort()[::-1][:3]
            top3 = [
                {
                    "crop": str(classes[i]),
                    "confidence": round(float(proba[i]), 2),
                    "reason": "Model prediction based on soil and weather inputs.",
                }
                for i in top_idx
            ]
            return {"source": "model", "recommendations": top3}
        except Exception as e:
            return {
                "source": "model_error_fallback",
                "error": str(e),
                "recommendations": _mock_recommend(water_source, season),
            }

    return {"source": "mock", "recommendations": _mock_recommend(water_source, season)}


if __name__ == "__main__":
    print(recommend_crops(water_source="rainfed", season="Kharif"))
