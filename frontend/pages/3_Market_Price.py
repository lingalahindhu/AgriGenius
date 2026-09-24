import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests

st.set_page_config(page_title="Market Price — AgriGenius", page_icon="📊", layout="wide")

API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def api_market_prices(crop: str, mandi: str, harvest_date=None):
    try:
        params = {"crop": crop}
        if mandi and mandi != "All Mandis":
            params["mandi"] = mandi
        if harvest_date:
            params["harvest_date"] = harvest_date
        r = requests.get(f"{API_BASE_URL}/market-price", params=params, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.market_price_agent import get_market_price_analysis
    return get_market_price_analysis(crop=crop, mandi=mandi if mandi != "All Mandis" else None, harvest_date=harvest_date)

st.markdown("""
<style>
    .stApp { background-color: #0b170e !important; color: #ffffff !important; font-size: 1.1rem; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Market Price Agent — AgriGenius Solutions")
st.caption("Warangal, Hanamkonda, Parkal & Narsampet Mandi Intelligence")

yield_signal = st.session_state.get("latest_yield", {})
auto_harvest_date = yield_signal.get("estimated_harvest_date")

m1, m2 = st.columns(2)
with m1:
    crop_name = st.selectbox("Select Crop Name:", ["Cotton", "Paddy", "Maize", "Red Gram", "Groundnut", "Bengal Gram", "Green Gram"])
with m2:
    mandi_name = st.selectbox("Select Mandi Preference:", ["All Mandis", "Warangal", "Hanamkonda", "Parkal", "Narsampet"])

if auto_harvest_date:
    st.write(f"• **Auto-passed Harvest Date from Module 3**: **{auto_harvest_date}**")

if st.button("📊 Fetch Mandi Rates & Selling Advice", type="primary", use_container_width=True):
    mkt_res = api_market_prices(crop_name, mandi_name, harvest_date=auto_harvest_date)
    st.info(f"💡 **Sell Recommendation (When & Where)**: {mkt_res.get('recommendation')}")
    
    prices = mkt_res.get("mandi_prices", [])
    if prices:
        st.table([{
            "Mandi": p["mandi"],
            "Crop": p["crop"],
            "Current Price (₹/Quintal)": f"₹ {p['current_price_per_quintal']:,}",
            "Previous Price": f"₹ {p['previous_price']:,}",
            "Trend": p["trend"].upper()
        } for p in prices])
