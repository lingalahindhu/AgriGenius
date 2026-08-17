import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests

st.set_page_config(page_title="Crop Health — AgriGenius", page_icon="🩺", layout="wide")

API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def api_check_health(crop_type: str, growth_stage: str, file_bytes=None, file_name=None):
    try:
        files = {}
        if file_bytes and file_name:
            files = {"file": (file_name, file_bytes)}
        data = {"crop_type": crop_type, "growth_stage": growth_stage}
        r = requests.post(f"{API_BASE_URL}/health-check-crop", data=data, files=files if files else None, timeout=4)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.health_monitoring_agent import check_crop_health
    return check_crop_health(crop_type=crop_type, growth_stage=growth_stage)

st.markdown("""
<style>
    .stApp { background-color: #0b170e !important; color: #ffffff !important; font-size: 1.1rem; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("🩺 Health Monitoring Agent — AgriGenius Solutions")
st.caption("Computer Vision Leaf Disease Diagnostics")

h_col1, h_col2 = st.columns(2)
with h_col1:
    uploaded_file = st.file_uploader("Upload Leaf / Plant Image:", type=["jpg", "png", "jpeg"])
    crop_type = st.selectbox("Select Crop Type:", ["Cotton", "Paddy"])
    growth_stage = st.selectbox("Growth Stage:", ["Sowing", "Vegetative", "Flowering", "Maturity"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Leaf Sample", width=260)
    run_btn = st.button("🩺 Run Diagnostic Check", type="primary", use_container_width=True)

with h_col2:
    if run_btn:
        with st.spinner("Running CNN disease classification..."):
            bytes_data = uploaded_file.getvalue() if uploaded_file else None
            file_name = uploaded_file.name if uploaded_file else None
            h_res = api_check_health(crop_type, growth_stage, bytes_data, file_name)
            st.session_state["latest_health"] = h_res

        severity = h_res.get("severity", "low")
        damage_flag = h_res.get("damage_flag", False)

        st.markdown(f"### Disease Classification: **{h_res.get('disease')}**")
        st.markdown(f"• **Confidence Score**: {int(h_res.get('confidence', 0.9)*100)}%\n• **Severity Flag**: `{severity.upper()}` (Damage Flag: **{damage_flag}**)")
        st.warning(f"**Recommended Treatment / Action**:\n\n{h_res.get('recommended_action')}")
