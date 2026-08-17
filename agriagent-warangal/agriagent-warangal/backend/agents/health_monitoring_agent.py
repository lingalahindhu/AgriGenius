"""
Health Monitoring Agent
Accepts a leaf/plant image path and returns a mock disease classification
result. Real CNN model (trained on PlantVillage + cotton leaf disease
datasets) will replace this placeholder logic in a later phase.
"""
import os
import random
from typing import Optional

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "leaf_disease_model.pt")

DISEASE_CLASSES = {
    "Cotton": ["Healthy", "Bacterial Blight", "Leaf Curl Virus", "Pink Bollworm Damage", "Grey Mildew"],
    "Paddy": ["Healthy", "Bacterial Leaf Blight", "Brown Spot", "Leaf Blast", "Sheath Blight"],
}

SEVERITY_BY_DISEASE = {
    "Healthy": "none",
    "Bacterial Blight": "moderate",
    "Leaf Curl Virus": "high",
    "Pink Bollworm Damage": "high",
    "Grey Mildew": "moderate",
    "Bacterial Leaf Blight": "moderate",
    "Brown Spot": "low",
    "Leaf Blast": "high",
    "Sheath Blight": "moderate",
}

TREATMENT_ADVICE = {
    "Healthy": "No action needed. Continue regular monitoring.",
    "Bacterial Blight": "Apply copper-based bactericide; avoid overhead irrigation.",
    "Leaf Curl Virus": "Remove and destroy infected plants; control whitefly vector with recommended insecticide.",
    "Pink Bollworm Damage": "Install pheromone traps; consider recommended insecticide spray schedule.",
    "Grey Mildew": "Apply sulfur-based fungicide; improve field ventilation.",
    "Bacterial Leaf Blight": "Use resistant varieties next season; apply copper oxychloride.",
    "Brown Spot": "Ensure balanced potassium fertilization; apply fungicide if severe.",
    "Leaf Blast": "Apply tricyclazole-based fungicide promptly; avoid excess nitrogen.",
    "Sheath Blight": "Apply propiconazole fungicide; maintain proper plant spacing.",
}


def _load_model():
    if os.path.exists(MODEL_PATH):
        # Placeholder: real implementation would load a torch CNN here.
        return "loaded_model_placeholder"
    return None


def analyze_leaf_image(
    image_path: str, crop_type: str = "Cotton", growth_stage: Optional[str] = None
) -> dict:
    """Returns disease name, confidence score, treatment advice and a
    severity/damage flag (used to trigger the Insurance Agent in Phase 2)."""
    model = _load_model()
    classes = DISEASE_CLASSES.get(crop_type, DISEASE_CLASSES["Cotton"])

    if model is None:
        # Mock prediction — seeded so repeated calls on the same file give
        # the same result during demos.
        random.seed(hash((image_path, crop_type)) % (2**32))
        disease = random.choice(classes)
        confidence = round(random.uniform(0.65, 0.97), 2)
        source = "mock"
    else:
        # TODO: run real inference with the loaded CNN model.
        disease = classes[0]
        confidence = 0.99
        source = "model"

    severity = SEVERITY_BY_DISEASE.get(disease, "unknown")
    return {
        "source": source,
        "image_path": image_path,
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "disease": disease,
        "confidence": confidence,
        "severity": severity,
        "treatment_recommendation": TREATMENT_ADVICE.get(
            disease, "Consult local agriculture extension officer."
        ),
        "damage_flag": severity in ("moderate", "high"),
    }


if __name__ == "__main__":
    print(analyze_leaf_image("sample_leaf.jpg", crop_type="Cotton"))
