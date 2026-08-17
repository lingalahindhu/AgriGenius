import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests

st.set_page_config(page_title="Crop Loan — AgriGenius", page_icon="💰", layout="wide")

API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def api_loan_evaluation(land_size: float, crop_plan: str, predicted_yield=None):
    try:
        r = requests.post(f"{API_BASE_URL}/loan-evaluation", json={"land_size": land_size, "crop_plan": crop_plan, "predicted_yield": predicted_yield}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.loan_agent import evaluate_loan
    return evaluate_loan(land_size=land_size, crop_plan=crop_plan, predicted_yield=predicted_yield)

st.markdown("""
<style>
    .stApp { background-color: #0b170e !important; color: #ffffff !important; font-size: 1.1rem; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("💰 Loan Agent (v2, Simulated) — AgriGenius Solutions")
st.caption("Kisan Credit Card (KCC) scale of finance evaluation. Yield auto-passed from Module 3.")

yield_signal = st.session_state.get("latest_yield", {})
auto_yield_val = yield_signal.get("predicted_total_yield_quintals")

l1, l2 = st.columns(2)
with l1:
    land_ha = st.number_input("Farm Landholding Size (Hectares):", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
with l2:
    plan_crop = st.selectbox("Planned Crop Plan:", ["Cotton", "Paddy", "Maize", "Red Gram"])

if auto_yield_val:
    st.write(f"• **Auto-passed Predicted Yield from Module 3**: **{auto_yield_val} Quintals**")

if st.button("💰 Evaluate Loan Eligibility", type="primary", use_container_width=True):
    loan_res = api_loan_evaluation(land_ha, plan_crop, predicted_yield=auto_yield_val)
    st.success(f"**Eligibility Status**: {loan_res.get('eligibility_status')}\n\n• **Reason**: {loan_res.get('reason')}")
    st.write(f"• **Suggested Loan Amount**: **₹ {loan_res.get('suggested_loan_amount_inr'):,}**")
    st.write(f"• **Scheme Name**: **{loan_res.get('scheme_name')}**")
    st.info(f"**Auto-Filled Application Summary**:\n\n{loan_res.get('application_summary')}")
    st.caption(f"⚠️ {loan_res.get('disclaimer')}")
