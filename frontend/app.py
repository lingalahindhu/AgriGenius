"""
AgriGenius — Main Dashboard Entrypoint.
Uses inline styled HTML span wrapper to guarantee huge, ultra-bold, centered 'AgriGenius' title.
"""
import sys
import os

# Fix sys.path so 'backend' package can be imported reliably
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests
from typing import Dict, Any, Optional, List

# Page configuration
st.set_page_config(
    page_title="AgriGenius",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend API URL
API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def get_current_page() -> str:
    try:
        if hasattr(st, "query_params"):
            page_val = st.query_params.get("page", "home")
            if isinstance(page_val, list):
                return page_val[0]
            return page_val
        else:
            params = st.experimental_get_query_params()
            return params.get("page", ["home"])[0]
    except Exception:
        return st.session_state.get("page", "home")

current_page = get_current_page()

# Helper API functions with Python fallbacks
def api_get_regions() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_BASE_URL}/regions", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.services.weather_api import get_available_regions
    return get_available_regions()

def api_recommend_crops(
    water_source: str,
    season: str,
    mandal: Optional[str] = None,
    village: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> Dict[str, Any]:
    try:
        payload = {
            "water_source": water_source,
            "season": season,
            "mandal": mandal,
            "village": village,
            "latitude": latitude,
            "longitude": longitude
        }
        r = requests.post(f"{API_BASE_URL}/crop-recommendation", json=payload, timeout=4)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.crop_recommendation_agent import recommend_crops
    return recommend_crops(
        water_source=water_source,
        season=season,
        mandal=mandal,
        village=village,
        latitude=latitude,
        longitude=longitude
    )


def api_check_health(crop_type: str, growth_stage: str, file_bytes=None, file_name=None) -> Dict[str, Any]:
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

def api_yield_prediction(land_area: float, crop: str, health_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        r = requests.post(f"{API_BASE_URL}/yield-prediction", json={"land_area_hectares": land_area, "crop": crop}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.yield_prediction_agent import predict_yield
    return predict_yield(land_area_hectares=land_area, crop=crop, health_data=health_data)

def api_loan_evaluation(land_size: float, crop_plan: str, predicted_yield: Optional[float] = None) -> Dict[str, Any]:
    try:
        r = requests.post(f"{API_BASE_URL}/loan-evaluation", json={"land_size": land_size, "crop_plan": crop_plan, "predicted_yield": predicted_yield}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.loan_agent import evaluate_loan
    return evaluate_loan(land_size=land_size, crop_plan=crop_plan, predicted_yield=predicted_yield)

def api_market_prices(crop: str, mandi: str, harvest_date: Optional[str] = None) -> Dict[str, Any]:
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

def api_insurance_evaluation(crop_type: str, land_area: float, damage_flag: bool) -> Dict[str, Any]:
    try:
        r = requests.post(f"{API_BASE_URL}/insurance-evaluation", json={"crop_type": crop_type, "land_area": land_area, "damage_flag": damage_flag}, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.agents.insurance_agent import evaluate_insurance
    return evaluate_insurance(crop_type=crop_type, land_area=land_area, damage_flag=damage_flag)

def api_chat(query: str) -> Dict[str, Any]:
    try:
        r = requests.post(f"{API_BASE_URL}/chat", json={"query": query}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.orchestrator.orchestrator_agent import process_farmer_query
    return process_farmer_query(query=query)


is_module_page = current_page != "home"

module_glass_css = f"""
<style>
    /* Hide top Streamlit header bar */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}

    .stApp {{
        background-color: #0b170e !important;
        background-image: 
            radial-gradient(rgba(200, 246, 104, 0.16) 1.2px, transparent 1.2px),
            radial-gradient(circle at 95% 5%, rgba(200, 246, 104, 0.28) 0%, transparent 45%),
            radial-gradient(circle at 5% 95%, rgba(74, 222, 128, 0.22) 0%, transparent 45%),
            linear-gradient(135deg, #07120a 0%, #0c1d12 50%, #040a06 100%) !important;
        background-size: 24px 24px, 100% 100%, 100% 100%, 100% 100% !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }}

    .main .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 4.0rem !important;
        { "background: rgba(18, 38, 25, 0.85) !important; backdrop-filter: blur(24px) !important; -webkit-backdrop-filter: blur(24px) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 24px !important; margin-top: 20px !important; box-shadow: 0 20px 60px rgba(0,0,0,0.6) !important; max-width: 95% !important;" if is_module_page else "" }
    }}

    .crop-rec-accent {{
        color: #c8f668 !important;
    }}

    .glass-card-container {{
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.16);
        border-radius: 22px;
        padding: 28px;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        transition: transform 0.25s ease, border-color 0.25s ease;
    }}
    .glass-card-container:hover {{
        border-color: rgba(200, 246, 104, 0.45);
        box-shadow: 0 16px 50px rgba(200, 246, 104, 0.18);
        transform: translateY(-3px);
    }}

    .card-content-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }}

    .card-title-text {{
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 10px 0;
    }}

    .card-desc-text {{
        font-size: 0.98rem;
        color: #f1f5f9;
        line-height: 1.48;
        margin: 0;
        max-width: 72%;
        font-weight: 400;
    }}

    .badge-icon-wrap {{
        width: 68px;
        height: 68px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        flex-shrink: 0;
    }}
    
    .glow-green {{ background: radial-gradient(circle, rgba(200, 246, 104, 0.45) 0%, rgba(22, 101, 52, 0.25) 100%); box-shadow: 0 0 25px rgba(200, 246, 104, 0.35); }}
    .glow-gold {{ background: radial-gradient(circle, rgba(250, 204, 21, 0.45) 0%, rgba(133, 77, 14, 0.25) 100%); box-shadow: 0 0 25px rgba(250, 204, 21, 0.35); }}
    .glow-blue {{ background: radial-gradient(circle, rgba(56, 189, 248, 0.45) 0%, rgba(30, 58, 138, 0.25) 100%); box-shadow: 0 0 25px rgba(56, 189, 248, 0.35); }}

    .pill-action-btn {{
        display: inline-block;
        padding: 9px 24px;
        border-radius: 30px;
        font-size: 0.95rem;
        font-weight: 700;
        text-decoration: none !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        cursor: pointer;
        width: fit-content;
    }}
    .pill-action-btn:hover {{ transform: scale(1.04); box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35); }}

    .btn-lime {{ background: #c8f668; color: #143000 !important; }}
    .btn-gold {{ background: #facc15; color: #382000 !important; }}
    .btn-olive {{ background: #857032; color: #ffffff !important; }}
    .btn-blue {{ background: #0388c4; color: #ffffff !important; }}

    h2 {{ font-size: 2.3rem !important; color: #c8f668 !important; font-weight: 800 !important; }}
    h3 {{ font-size: 1.7rem !important; color: #ffffff !important; font-weight: 700 !important; }}
    p, span, div {{ color: #f8fafc !important; font-size: 1.15rem !important; }}

    div[data-testid="stMarkdownContainer"] p, 
    label[data-testid="stWidgetLabel"] p,
    .stRadio label p, .stSelectbox label p, .stNumberInput label p, .stCheckbox label p {{
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    div[role="radiogroup"] label p {{ color: #f8fafc !important; font-size: 1.15rem !important; }}

    .stButton>button {{
        background: linear-gradient(135deg, #c8f668 0%, #a3e635 100%) !important;
        color: #123000 !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        border-radius: 30px !important;
        padding: 12px 30px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(200, 246, 104, 0.4) !important;
    }}

    .stAlert {{
        background-color: rgba(22, 50, 32, 0.95) !important;
        border: 1px solid rgba(200, 246, 104, 0.6) !important;
        color: #ffffff !important;
        border-radius: 16px !important;
        font-size: 1.1rem !important;
    }}

    .stChatMessage {{
        background-color: rgba(28, 58, 38, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: 18px !important;
        color: #ffffff !important;
        font-size: 1.15rem !important;
    }}
    .stChatMessage p {{ color: #ffffff !important; font-size: 1.15rem !important; }}

    div[data-testid="stChatInput"], 
    div[data-testid="stChatInput"] textarea, 
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] {{
        background-color: #122919 !important;
        border-color: rgba(200, 246, 104, 0.5) !important;
        color: #ffffff !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        color: #ffffff !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #94a3b8 !important;
    }}
</style>
"""
st.markdown(module_glass_css, unsafe_allow_html=True)


# =============================================================
# DASHBOARD HOME PAGE (TITLE IS JUST "AgriGenius" - INLINE HUGE & BOLD)
# =============================================================
if current_page == "home":

    # Inline Styled Huge Ultra-Bold Title
    st.markdown("""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 45px; width: 100%;">
        <span style="font-size: 80.8rem !important; font-weight: 900 !important; color: #ffffff !important; letter-spacing: -1.5px; text-shadow: 0 6px 35px rgba(0,0,0,0.8), 0 0 30px rgba(200, 246, 104, 0.4); display: inline-block; font-family: system-ui, -apple-system, sans-serif;">AgriGenius</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="glass-card-container">
            <div class="card-content-header">
                <div>
                    <h3 class="card-title-text">Crop Recommendation</h3>
                    <p class="card-desc-text">Discover the farming and crop need to put your recommendation.</p>
                </div>
                <div class="badge-icon-wrap glow-green">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#c8f668" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 0 1 10 10c0 5.5-4.5 10-10 10S2 17.5 2 12A10 10 0 0 1 12 2z"/><path d="M12 18V8"/><path d="M12 8c2.5 0 5-2 5-5-2.5 0-5 2.5-5 5z"/><path d="M12 12c-2.5 0-5-2-5-5 2.5 0 5 2.5 5 5z"/></svg>
                </div>
            </div>
            <div>
                <a href="?page=Crop+Recommendation" target="_self" class="pill-action-btn btn-lime">Crop Recommendation</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="glass-card-container">
            <div class="card-content-header">
                <div>
                    <h3 class="card-title-text">Crop Loan</h3>
                    <p class="card-desc-text">Get have scientific the crop loan status and healthy status.</p>
                </div>
                <div class="badge-icon-wrap glow-gold">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#facc15" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="3"/><path d="M12 4v6"/><path d="M10 7h4"/><path d="M18 14l-6 3-6-3"/><path d="M6 14v4a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4"/></svg>
                </div>
            </div>
            <div>
                <a href="?page=Crop+Loan" target="_self" class="pill-action-btn btn-gold">Crop Loan</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="glass-card-container">
            <div class="card-content-header">
                <div>
                    <h3 class="card-title-text">Crop Insurance</h3>
                    <p class="card-desc-text">Monitor the relevance promote events and crop Insurance.</p>
                </div>
                <div class="badge-icon-wrap glow-gold">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
                </div>
            </div>
            <div>
                <a href="?page=Crop+Insurance" target="_self" class="pill-action-btn btn-olive">Insurance</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)

    with r1:
        st.markdown("""
        <div class="glass-card-container">
            <div class="card-content-header">
                <div>
                    <h3 class="card-title-text">Crop Health</h3>
                    <p class="card-desc-text">Ensure a health and crop brands to get crop entire health.</p>
                </div>
                <div class="badge-icon-wrap glow-green">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#c8f668" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A9 9 0 0 1 3 12C3 5.5 8.5 2 12 2c0 6.5 5.5 10 9 10a9 9 0 0 1-5 7.7"/><path d="M12 2v18"/><path d="M18 6h4"/><path d="M20 4v4"/></svg>
                </div>
            </div>
            <div>
                <a href="?page=Crop+Health" target="_self" class="pill-action-btn btn-lime">Crop Health</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown("""
        <div class="glass-card-container">
            <div class="card-content-header">
                <div>
                    <h3 class="card-title-text">Yield Prediction</h3>
                    <p class="card-desc-text">Prediction accurate in land to yield yield prediction.</p>
                </div>
                <div class="badge-icon-wrap glow-gold">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#facc15" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/><path d="M14 9h5v5"/></svg>
                </div>
            </div>
            <div>
                <a href="?page=Yield+Prediction" target="_self" class="pill-action-btn btn-gold">Yield Price</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r3:
        st.markdown("""
        <div class="glass-card-container">
            <div class="card-content-header">
                <div>
                    <h3 class="card-title-text">Market Price</h3>
                    <p class="card-desc-text">Market market market price for choice of environments.</p>
                </div>
                <div class="badge-icon-wrap glow-blue">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 7-7 7-4-4-5 5"/><path d="M14 7h5v5"/></svg>
                </div>
            </div>
            <div>
                <a href="?page=Market+Price" target="_self" class="pill-action-btn btn-blue">Learn Price</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.12);'><br>", unsafe_allow_html=True)
    f1, f2 = st.columns([3, 1])
    with f1:
        st.markdown("<p style='font-size: 1.2rem; color:#ffffff;'>💬 <b>Ask AgriGenius AI Assistant:</b> Natural language farming coordinator for Warangal district.</p>", unsafe_allow_html=True)
    with f2:
        st.markdown('<a href="?page=AI+Chat" target="_self" class="pill-action-btn btn-lime">Open AI Chatbot</a>', unsafe_allow_html=True)


# =============================================================
# MODULE 1: CROP RECOMMENDATION AGENT
# =============================================================
elif current_page == "Crop Recommendation":
    st.markdown('<a href="?page=home" target="_self" class="pill-action-btn btn-lime">← Back to AgriGenius Dashboard</a><br><br>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-top: 15px; margin-bottom: 25px;">
        <span style="font-size: 4.0rem !important; font-weight: 900 !important; color: #ffffff !important; letter-spacing: -1px; text-shadow: 0 6px 30px rgba(0,0,0,0.7); display: inline-block;">AgriGenius <span class="crop-rec-accent">Crop Recommendation</span></span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='color:#ffffff !important; font-size:1.2rem;'><b>Hyper-Local Zero-Prompting Engine</b>: Select your Mandal and Village below. Village-specific Soil Health Card metrics, nearest APMC Mandi proximity, and live micro-weather are retrieved automatically without manual laboratory data entry.</p>", unsafe_allow_html=True)

    # Hyper-Local Regional Hierarchy
    regions_data = api_get_regions()
    mandals_dict = regions_data.get("mandals", {})
    mandal_names = sorted(list(mandals_dict.keys())) if mandals_dict else ["Wardhannapet", "Geesugonda", "Narsampet", "Parkal", "Dharmasagar"]

    st.markdown("<h4 style='color:#c8f668; margin-bottom:8px;'>📍 1. Farm Location Hierarchy</h4>", unsafe_allow_html=True)
    reg1, reg2 = st.columns(2)
    with reg1:
        selected_mandal = st.selectbox("Select Mandal / Sub-District:", mandal_names, index=0)

    villages_in_mandal = mandals_dict.get(selected_mandal, [])
    village_names = [v.get("village") for v in villages_in_mandal] if villages_in_mandal else ["Chennaram"]
    with reg2:
        selected_village = st.selectbox("Select Village (Gram Panchayat):", village_names, index=0)

    matched_vinfo = next((v for v in villages_in_mandal if v.get("village") == selected_village), {})
    v_lat = matched_vinfo.get("latitude", 17.9784)
    v_lon = matched_vinfo.get("longitude", 79.5941)
    v_soil = matched_vinfo.get("soil_type", "Deep Black Cotton Soil")
    v_mandi = matched_vinfo.get("nearest_mandi", "Enumamula Warangal")
    v_dist = matched_vinfo.get("mandi_distance_km", 10.0)

    use_gps = st.checkbox("🛰️ Use Hyper-Local GPS Coordinates for Live Weather", value=True)
    if use_gps:
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.06); padding:10px 14px; border-radius:8px; margin-bottom:15px; border-left:4px solid #c8f668;'>"
            f"<span style='color:#ffffff; font-size:0.95rem;'>📌 <b>Target Village</b>: {selected_village}, {selected_mandal} | <b>GPS</b>: {v_lat}°N, {v_lon}°E | <b>Soil</b>: {v_soil} | <b>Nearest Market</b>: {v_mandi} ({v_dist} km)</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("<h4 style='color:#c8f668; margin-top:10px; margin-bottom:8px;'>🌾 2. Farming Setup</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        water_source = st.radio("Water Access Source:", ["Irrigated", "Rainfed"])
    with col2:
        season = st.radio("Farming Season:", ["Kharif", "Rabi"])

    if st.button("🌾 Get Crop Recommendations", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing hyper-local soil & live weather for {selected_village}, {selected_mandal}..."):
            res = api_recommend_crops(
                water_source=water_source,
                season=season,
                mandal=selected_mandal,
                village=selected_village,
                latitude=v_lat if use_gps else None,
                longitude=v_lon if use_gps else None
            )

        st.markdown("<h3 style='color:#c8f668 !important; margin-top:25px;'>🌱 Top Recommended Crops for Your Village</h3>", unsafe_allow_html=True)
        soil = res.get("retrieved_soil", {})
        weather = res.get("retrieved_weather", {})

        # Hyper-Local Metrics Card
        with st.expander("📍 Hyper-Local Village Soil & Weather Metrics Breakdown", expanded=True):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Soil Type", soil.get("soil_type", "Black Soil").split("/")[0].strip())
            m2.metric("Soil pH", f"{soil.get('pH', 6.8)}")
            m3.metric("Live Temperature", f"{weather.get('temperature', 29.5)}°C")
            m4.metric("Live Humidity", f"{weather.get('humidity', 72)}%")

            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Nitrogen (N)", f"{soil.get('N', 90)} kg/ha")
            m6.metric("Phosphorus (P)", f"{soil.get('P', 42)} kg/ha")
            m7.metric("Potassium (K)", f"{soil.get('K', 43)} kg/ha")
            m8.metric("Nearest Mandi", f"{soil.get('nearest_mandi', 'Warangal')} ({soil.get('mandi_distance_km', 10)} km)")

            st.caption(f"Source: {soil.get('source')} | Weather: {weather.get('source')}")

        for r in res.get("recommendations", []):
            st.success(f"**{r['crop']}** — Match Confidence: **{int(r['confidence']*100)}%**\n\n*Plain-Language Reason*: {r['reason']}")



# =============================================================
# MODULE 2: HEALTH MONITORING AGENT
# =============================================================
elif current_page == "Crop Health":
    st.markdown('<a href="?page=home" target="_self" class="pill-action-btn btn-lime">← Back to AgriGenius Dashboard</a><br><br>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:#c8f668 !important;'>🩺 Health Monitoring Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ffffff !important; font-size:1.2rem;'>Computer Vision & CNN Leaf Disease Diagnostic. Automatically passes disease severity flags to downstream agents.</p>", unsafe_allow_html=True)

    h1, h2 = st.columns(2)
    with h1:
        uploaded_file = st.file_uploader("Upload Leaf / Plant Image:", type=["jpg", "png", "jpeg"])
        crop_type = st.selectbox("Select Crop Type:", ["Cotton", "Paddy"])
        growth_stage = st.selectbox("Growth Stage:", ["Sowing", "Vegetative", "Flowering", "Maturity"])
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Leaf Sample", width=260)
        run_btn = st.button("🩺 Run Diagnostic Check", type="primary", use_container_width=True)

    with h2:
        if run_btn:
            with st.spinner("Running CNN disease classification..."):
                bytes_data = uploaded_file.getvalue() if uploaded_file else None
                file_name = uploaded_file.name if uploaded_file else None
                h_res = api_check_health(crop_type, growth_stage, bytes_data, file_name)
                st.session_state["latest_health"] = h_res

            severity = h_res.get("severity", "low")
            damage_flag = h_res.get("damage_flag", False)

            st.markdown(f"<h3 style='color:#ffffff !important;'>Disease Classification: <b>{h_res.get('disease')}</b></h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#ffffff !important;'>• <b>Confidence Score</b>: {int(h_res.get('confidence', 0.9)*100)}%<br>• <b>Severity Flag</b>: <span style='color:#facc15; font-weight:bold;'>{severity.upper()}</span> (Damage Flag: <b>{damage_flag}</b>)</p>", unsafe_allow_html=True)
            st.warning(f"**Recommended Treatment / Action**:\n\n{h_res.get('recommended_action')}")

            if damage_flag:
                st.info("ℹ️ **Data Flow Signal**: Disease severity flag automatically saved and passed to Yield Prediction Agent & Insurance Agent.")


# =============================================================
# MODULE 3: YIELD PREDICTION AGENT (v2)
# =============================================================
elif current_page == "Yield Prediction":
    st.markdown('<a href="?page=home" target="_self" class="pill-action-btn btn-lime">← Back to AgriGenius Dashboard</a><br><br>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:#facc15 !important;'>📈 Yield Prediction Agent (v2)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ffffff !important; font-size:1.2rem;'>Soil/Weather pulled automatically from datasets. Crop-health disease signals pulled automatically from Module 2 (Health Agent).</p>", unsafe_allow_html=True)

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
        st.info("ℹ️ **Data Flow Signal**: Predicted yield & harvest date saved and auto-passed to Loan Agent & Market Price Agent.")


# =============================================================
# MODULE 4: LOAN AGENT (v2, SIMULATED)
# =============================================================
elif current_page == "Crop Loan":
    st.markdown('<a href="?page=home" target="_self" class="pill-action-btn btn-lime">← Back to AgriGenius Dashboard</a><br><br>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:#facc15 !important;'>💰 Loan Agent (v2, Simulated)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ffffff !important; font-size:1.2rem;'>Kisan Credit Card (KCC) scale of finance evaluation. Predicted yield auto-passed from Module 3 (Yield Prediction Agent).</p>", unsafe_allow_html=True)

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


# =============================================================
# MODULE 5: MARKET PRICE AGENT
# =============================================================
elif current_page == "Market Price":
    st.markdown('<a href="?page=home" target="_self" class="pill-action-btn btn-lime">← Back to AgriGenius Dashboard</a><br><br>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:#38bdf8 !important;'>📊 Market Price Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ffffff !important; font-size:1.2rem;'>Real-time Mandi pricing across Warangal district. Harvest date auto-passed from Module 3 if available.</p>", unsafe_allow_html=True)

    yield_signal = st.session_state.get("latest_yield", {})
    auto_harvest_date = yield_signal.get("estimated_harvest_date")

    m1, m2 = st.columns(2)
    with m1:
        crop_name = st.selectbox("Select Crop Name:", ["Cotton", "Paddy", "Maize", "Red Gram"])
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
                "Previous Rate": f"₹ {p['previous_price']:,}",
                "Trend Direction": p["trend"].upper()
            } for p in prices])


# =============================================================
# MODULE 6: INSURANCE AGENT (v2, SIMULATED)
# =============================================================
elif current_page == "Crop Insurance":
    st.markdown('<a href="?page=home" target="_self" class="pill-action-btn btn-lime">← Back to AgriGenius Dashboard</a><br><br>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:#facc15 !important;'>🛡️ Insurance Agent (v2, Simulated)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ffffff !important; font-size:1.2rem;'>Pradhan Mantri Fasal Bima Yojana (PMFBY) assessment. Damage flags auto-passed from Module 2 (Health Monitoring Agent).</p>", unsafe_allow_html=True)

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


# =============================================================
# MODULE 7: AI FARMER CHAT COORDINATOR
# =============================================================
elif current_page == "AI Chat":
    st.markdown('<a href="?page=home" target="_self" class="pill-action-btn btn-lime">← Back to AgriGenius Dashboard</a><br><br>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:#c8f668 !important;'>💬 AI Farmer Chat Coordinator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ffffff !important; font-size:1.2rem;'>LangGraph Multi-Agent Intent Router for Warangal Farmers</p>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Namaste! I am AgriGenius, your farming AI assistant for Warangal district. How can I help you today?"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Type your farming query...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("AgriGenius orchestrator processing query..."):
            reply_obj = api_chat(prompt)
            reply = reply_obj.get("response", "Processing query failed.")
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
