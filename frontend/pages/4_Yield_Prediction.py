import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests

st.set_page_config(page_title="Yield Prediction — AgriGenius", page_icon="📈", layout="wide")

API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def api_yield_prediction(land_area: float, crop: str, health_data=None):
    try:
        r = requests.post(f"{API_BASE_URL}/yield-prediction", json={"land_area_hectares": land_area, "crop": crop}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.yield_prediction_agent import predict_yield
    return predict_yield(land_area_hectares=land_area, crop=crop, health_data=health_data)

st.markdown("""
<style>
    .stApp { background-color: #0b170e !important; color: #ffffff !important; font-size: 1.1rem; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Yield Prediction Agent (v2) — AgriGenius Solutions")
st.caption("Soil/Weather auto-pulled. Crop health disease signals pulled automatically from Module 2.")

y1, y2 = st.columns(2)
with y1:
    area_ha = st.number_input("Land Area (Hectares):", min_value=0.1, max_value=50.0, value=1.5, step=0.1)
with y2:
    crop_sel = st.selectbox("Crop Type:", ["Cotton", "Paddy", "Maize", "Red Gram"])

health_signal = st.session_state.get("latest_health")
if health_signal:
    st.write(f"• **Auto-passed Health Signal from Module 2**: {health_signal.get('disease')} (Severity: `{health_signal.get('severity')}`)")

if st.button("📈 Predict Harvest Yield", type="primary", use_container_width=True):
    res = api_yield_prediction(area_ha, crop_sel, health_data=health_signal)
    st.session_state["latest_yield"] = res

    st.success(f"**Predicted Total Yield**: {res.get('predicted_total_yield_quintals')} Quintals\n\n• **Confidence Range**: {res.get('confidence_range')}\n• **Estimated Harvest-Ready Date**: **{res.get('estimated_harvest_date')}**")
