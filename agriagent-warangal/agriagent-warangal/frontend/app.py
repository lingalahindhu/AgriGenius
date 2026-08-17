"""
AgriGenius Streamlit Frontend
Multi-tab UI: Crop Recommendation | Market Price | Health Check | Chat
Talks to the FastAPI backend at BACKEND_URL.

Run with:
    streamlit run frontend/app.py
"""
import os
import tempfile

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="AgriGenius - Warangal", page_icon="🌾", layout="wide")
st.title("🌾 AgriGenius — Warangal District Farming Assistant")
st.caption("Agentic AI platform piloted for cotton & paddy farmers in Warangal, Telangana.")

tab1, tab2, tab3, tab4 = st.tabs(
    ["🌱 Crop Recommendation", "💰 Market Price", "🩺 Health Check", "💬 Chat"]
)

# ---------------------------------------------------------------------------
# Tab 1: Crop Recommendation
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Get Crop Recommendations")
    col1, col2 = st.columns(2)
    with col1:
        water_source = st.selectbox("Water source", ["irrigated", "rainfed"])
        season = st.selectbox("Season", ["Kharif", "Rabi"])
        village = st.text_input("Village (optional)")
    with col2:
        st.caption("Soil & weather values are optional — leave at 0 to use mock/auto-fetched defaults.")
        nitrogen = st.number_input("Nitrogen (N)", min_value=0.0, value=0.0)
        phosphorus = st.number_input("Phosphorus (P)", min_value=0.0, value=0.0)
        potassium = st.number_input("Potassium (K)", min_value=0.0, value=0.0)
        ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=0.0)
        temperature = st.number_input("Temperature (°C)", value=0.0)
        humidity = st.number_input("Humidity (%)", value=0.0)
        rainfall = st.number_input("Rainfall (mm)", value=0.0)

    if st.button("Recommend Crops", key="crop_btn"):
        payload = {
            "water_source": water_source,
            "season": season,
            "village": village or None,
            "nitrogen": nitrogen or None,
            "phosphorus": phosphorus or None,
            "potassium": potassium or None,
            "ph": ph or None,
            "temperature": temperature or None,
            "humidity": humidity or None,
            "rainfall": rainfall or None,
        }
        try:
            resp = requests.post(f"{BACKEND_URL}/crop-recommendation", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            st.success(f"Source: {data.get('source')}")
            for rec in data.get("recommendations", []):
                st.markdown(f"**{rec['crop'].title()}** — confidence: {rec['confidence']:.0%}")
                st.caption(rec["reason"])
        except Exception as e:
            st.error(f"Could not reach backend: {e}")

# ---------------------------------------------------------------------------
# Tab 2: Market Price
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Mandi Price Lookup")
    crop = st.text_input("Crop name", value="cotton")
    mandi = st.selectbox("Mandi", ["All", "Warangal", "Hanamkonda", "Parkal", "Narsampet"])

    if st.button("Check Price", key="price_btn"):
        payload = {"crop": crop, "mandi": None if mandi == "All" else mandi}
        try:
            resp = requests.post(f"{BACKEND_URL}/market-price", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            st.info(data.get("recommendation"))
            for q in data.get("quotes", []):
                st.write(
                    f"**{q['mandi']}** — Modal ₹{q['modal_price']}/quintal "
                    f"(Min ₹{q['min_price']} / Max ₹{q['max_price']}) — Trend: **{q['trend']}**"
                )
        except Exception as e:
            st.error(f"Could not reach backend: {e}")

# ---------------------------------------------------------------------------
# Tab 3: Health Check
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Leaf / Plant Health Check")
    crop_type = st.selectbox("Crop type", ["Cotton", "Paddy"])
    growth_stage = st.selectbox("Growth stage", ["sowing", "vegetative", "flowering", "maturity"])
    uploaded_file = st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded image", width=300)

    if st.button("Analyze Image", key="health_btn"):
        if uploaded_file is None:
            st.warning("Please upload an image first.")
        else:
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            payload = {"image_path": tmp_path, "crop_type": crop_type, "growth_stage": growth_stage}
            try:
                resp = requests.post(f"{BACKEND_URL}/health-check-crop", json=payload, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                st.success(f"Diagnosis: **{data['disease']}** (confidence: {data['confidence']:.0%})")
                st.write(f"Severity: {data['severity']}")
                st.write(f"Recommended action: {data['treatment_recommendation']}")
                if data.get("damage_flag"):
                    st.warning("⚠️ Damage flag raised — this would be passed to the Insurance Agent (Phase 2).")
            except Exception as e:
                st.error(f"Could not reach backend: {e}")

# ---------------------------------------------------------------------------
# Tab 4: Chat
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Chat with AgriGenius")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(msg)

    user_msg = st.chat_input("Ask about crops, prices, or plant health...")
    if user_msg:
        st.session_state.chat_history.append(("user", user_msg))
        with st.chat_message("user"):
            st.write(user_msg)

        try:
            resp = requests.post(f"{BACKEND_URL}/chat", json={"query": user_msg}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            agent_response = data.get("response", {})
            reply = agent_response.get("result", {}).get("answer") or str(agent_response.get("result"))
        except Exception as e:
            reply = f"Could not reach backend: {e}"

        st.session_state.chat_history.append(("assistant", reply))
        with st.chat_message("assistant"):
            st.write(reply)
