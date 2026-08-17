import sys
import os

# Ensure backend root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests

st.set_page_config(page_title="Crop Recommendation — AgriGenius", page_icon="🌱", layout="wide")

API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def api_recommend_crops(water_source: str, season: str):
    try:
        r = requests.post(f"{API_BASE_URL}/crop-recommendation", json={"water_source": water_source, "season": season}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.crop_recommendation_agent import recommend_crops
    return recommend_crops(water_source=water_source, season=season)

# High contrast styling
st.markdown("""
<style>
    .stApp { background-color: #0b170e !important; color: #ffffff !important; font-size: 1.1rem; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; }
    .stRadio label p { color: #ffffff !important; font-size: 1.15rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Crop Recommendation Agent — AgriGenius Solutions")
st.caption("Warangal District, Telangana • Soil Health Card & Local Weather Auto-Retrieved")

st.info("ℹ️ **Automated Data Retrieval Active**: Soil parameters (N, P, K, pH) and weather metrics (temperature, humidity, rainfall) are automatically retrieved for your location instead of farmer entry.")

col1, col2 = st.columns(2)
with col1:
    water_source = st.radio("Water Access Source:", ["Irrigated", "Rainfed"])
with col2:
    season = st.radio("Farming Season:", ["Kharif", "Rabi"])

if st.button("🌾 Get Crop Recommendations", type="primary", use_container_width=True):
    with st.spinner("Analyzing soil & weather parameters for Warangal..."):
        res = api_recommend_crops(water_source, season)

    st.markdown("### Top 2–3 Recommended Crops")
    soil = res.get("retrieved_soil", {})
    weather = res.get("retrieved_weather", {})

    with st.expander("📍 Auto-Retrieved Soil & Weather Metrics Breakdown"):
        st.write(f"• **Soil Profile**: {soil.get('soil_type')} (N: {soil.get('N')} kg/ha, P: {soil.get('P')} kg/ha, K: {soil.get('K')} kg/ha, pH: {soil.get('pH')})")
        st.write(f"• **Weather Profile**: {weather.get('temperature')}°C | {weather.get('humidity')}% Humidity | {weather.get('rainfall')}mm Rainfall")

    for r in res.get("recommendations", []):
        st.success(f"**{r['crop']}** — Confidence Score: **{int(r['confidence']*100)}%**\n\n*Plain-Language Reason*: {r['reason']}")
