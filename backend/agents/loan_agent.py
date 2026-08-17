"""
Loan Agent for AgriGenius.
Module 4:
- Input Needed: Land size, crop plan, predicted yield (auto-passed from Module 3 Yield Prediction).
- Output: Eligibility status (Yes/No + reason), suggested loan amount and scheme name, auto-filled application summary.
Saves input & output records to MongoDB.
"""
from typing import Dict, Any, Optional
from backend.services.mongodb_service import save_record


def evaluate_loan(
    land_size: float = 1.0,
    crop_plan: str = "Cotton",
    predicted_yield: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluate simulated Kisan Credit Card (KCC) loan eligibility and calculate scale of finance.
    """
    land = max(float(land_size), 0.1)
    crop_norm = crop_plan.strip().capitalize() if crop_plan else "Cotton"

    scale_of_finance = {
        "Cotton": 65000,
        "Paddy": 55000,
        "Maize": 45000,
        "Red Gram": 40000,
        "Groundnut": 50000
    }
    rate_per_ha = scale_of_finance.get(crop_norm, 50000)
    suggested_loan = int(land * rate_per_ha)

    is_eligible = land >= 0.2
    status = "Yes (Eligible)" if is_eligible else "No (Landholding below benchmark)"

    reason = (
        f"Farmer meets KCC credit benchmark for {land} hectares under {crop_norm} crop plan. "
        f"Scale of finance calculated at ₹{rate_per_ha:,}/ha as per Telangana District Level Technical Committee norms."
    ) if is_eligible else "Minimum land size of 0.2 hectares required for standard KCC scale of finance."

    est_yield_str = f"{predicted_yield} Quintals" if predicted_yield else f"{round(land * 20.0, 1)} Quintals"

    summary = (
        f"Pre-approved loan limit recommendation of ₹{suggested_loan:,} for growing {crop_norm} on {land} ha. "
        f"Auto-passed estimated harvest yield: {est_yield_str}."
    )

    output = {
        "disclaimer": "SIMULATION ONLY - Not connected to real financial institutions",
        "eligibility_status": status,
        "is_eligible": is_eligible,
        "land_size_ha": land,
        "crop_plan": crop_norm,
        "predicted_yield_passed": predicted_yield,
        "suggested_loan_amount_inr": suggested_loan,
        "interest_rate": "7% per annum (3% subvention for prompt repayment)",
        "scheme_name": "Kisan Credit Card (KCC) - Telangana Agriculture Scale of Finance",
        "reason": reason,
        "application_summary": summary
    }

    save_record(
        collection_name="loan_evaluations",
        input_data={"land_size": land, "crop_plan": crop_norm, "predicted_yield": predicted_yield},
        output_data=output,
        module_name="Loan Agent"
    )

    return output
