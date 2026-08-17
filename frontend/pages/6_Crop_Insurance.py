import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests

st.set_page_config(page_title="Crop Insurance — AgriGenius", page_icon="🛡️", layout="wide")

API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def api_insurance_evaluation(crop_type: str, land_area: float, damage_flag: bool):
    try:
        r = requests.post(f"{API_BASE_URL}/insurance-evaluation", json={"crop_type": crop_type, "land_area": land_area, "damage_flag": damage_flag}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.insurance_agent import evaluate_insurance
    return evaluate_insurance(crop_type=crop_type, land_area=land_area, damage_flag=damage_flag)

st.markdown("""
<style>
    .stApp { background-color: #0b170e !important; color: #ffffff !important; font-size: 1.1rem; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Insurance Agent (v2, Simulated) — AgriGenius Solutions")
st.caption("Pradhan Mantri Fasal Bima Yojana Assessment. Damage flags auto-passed from Module 2.")

health_signal = st.session_state.get("latest_health", {})
auto_damage_flag = health_signal.get("damage_flag", False)

i1, i2 = st.columns(2)
with i1:
    ins_crop = st.selectbox("Insured Crop Type:", ["Cotton", "Paddy", "Maize", "Red Gram"])
    ins_area = st.number_input("Insured Land Area (Hectares):", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
with i2:
    ins_damage = st.checkbox("Disease / Damage Flag Active", value=auto_damage_flag)

if auto_damage_flag:
    st.warning(f"⚠️ **Auto-passed Damage Flag from Module 2**: Active disease detected (`{health_signal.get('disease')}` - `{health_signal.get('severity').upper()}` severity)")

if st.button("🛡️ Assess PMFBY Insurance Policy", type="primary", use_container_width=True):
    ins_res = api_insurance_evaluation(ins_crop, ins_area, ins_damage)
    st.success(f"**Scheme Match**: {ins_res.get('scheme_name')}\n\n• **Total Sum Insured**: **₹ {ins_res.get('sum_insured_inr'):,}**\n• **Estimated Premium Payable**: **₹ {ins_res.get('farmer_premium_payable_inr'):,}** ({ins_res.get('premium_percentage')})")
    st.write(f"• **Claim Status**: {ins_res.get('claim_status')}")
    if ins_damage:
        st.error(f"⚠️ **Simulated Claim Payout Amount**: **₹ {ins_res.get('simulated_claim_payout_inr'):,}**")
    st.caption(f"⚠️ {ins_res.get('disclaimer')}")
