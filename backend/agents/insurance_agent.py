"""
Insurance Agent for AgriGenius.
Module 6:
- Input Needed: Crop type, land area, region, damage flag (auto-passed from Module 2 if disease detected).
- Output: Estimated premium and scheme match, plus a simulated claim amount if a damage flag was triggered.
Saves input & output records to MongoDB.
"""
from typing import Dict, Any
from backend.services.mongodb_service import save_record


def evaluate_insurance(
    crop_type: str = "Cotton",
    land_area: float = 1.0,
    region: str = "Warangal",
    damage_flag: bool = False
) -> Dict[str, Any]:
    """
    Simulate Pradhan Mantri Fasal Bima Yojana (PMFBY) insurance assessment.
    Automatically factors damage flags originating from Health Monitoring Agent.
    """
    area = max(float(land_area), 0.1)
    crop_clean = crop_type.strip().lower() if crop_type else "cotton"
    crop_map = {
        "cotton": "Cotton", "paddy": "Paddy", "rice": "Paddy", "maize": "Maize", "corn": "Maize",
        "red gram": "Red Gram", "pigeon pea": "Red Gram", "tur": "Red Gram",
        "groundnut": "Groundnut", "peanut": "Groundnut",
        "bengal gram": "Bengal Gram", "chickpea": "Bengal Gram",
        "green gram": "Green Gram", "mung bean": "Green Gram"
    }
    crop_norm = crop_map.get(crop_clean, crop_type.strip().title() if crop_type else "Cotton")
    region_norm = region.strip().title() if region else "Warangal"

    sum_insured_per_ha = {
        "Cotton": 75000,
        "Paddy": 60000,
        "Maize": 50000,
        "Red Gram": 45000,
        "Groundnut": 52000,
        "Bengal Gram": 48000,
        "Green Gram": 42000
    }
    rate = sum_insured_per_ha.get(crop_norm, 60000)
    total_sum_insured = int(area * rate)

    premium_rate = 0.02
    farmer_premium = int(total_sum_insured * premium_rate)

    claim_amount = 0
    claim_status = "No Active Loss Claim"
    if damage_flag:
        claim_amount = int(total_sum_insured * 0.60)
        claim_status = "Claim Triggered & Under Process (Damage Flag Active)"

    output = {
        "disclaimer": "SIMULATION ONLY - PMFBY Policy Engine Sandbox",
        "region": f"{region_norm} District, Telangana",
        "crop_type": crop_norm,
        "land_area_ha": area,
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY) / Telangana Crop Insurance Scheme",
        "sum_insured_inr": total_sum_insured,
        "farmer_premium_payable_inr": farmer_premium,
        "premium_percentage": "2.0% (Kharif Subsidized Rate)",
        "damage_flag_detected": damage_flag,
        "claim_status": claim_status,
        "simulated_claim_payout_inr": claim_amount,
        "coverage_details": "Comprehensive risk coverage against natural pests, plant diseases, drought, and unseasonal rainfall."
    }

    save_record(
        collection_name="insurance_evaluations",
        input_data={"crop_type": crop_norm, "land_area": area, "region": region_norm, "damage_flag": damage_flag},
        output_data=output,
        module_name="Insurance Agent"
    )

    return output
