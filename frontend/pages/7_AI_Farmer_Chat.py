import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import requests

st.set_page_config(page_title="AI Farmer Chat — AgriGenius", page_icon="💬", layout="wide")

API_BASE_URL = os.getenv("AGRIGENIUS_API_URL", "http://127.0.0.1:8000")

def api_chat(query: str):
    try:
        r = requests.post(f"{API_BASE_URL}/chat", json={"query": query}, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    from backend.orchestrator.orchestrator_agent import process_farmer_query
    return process_farmer_query(query=query)

st.markdown("""
<style>
    .stApp { background-color: #0b170e !important; color: #ffffff !important; font-size: 1.1rem; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; }
    .stChatMessage { background-color: rgba(28, 58, 38, 0.95) !important; border: 1px solid rgba(255, 255, 255, 0.22) !important; color: #ffffff !important; font-size: 1.15rem !important; }
    .stChatMessage p { color: #ffffff !important; font-size: 1.15rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("💬 AI Farmer Chat Coordinator — AgriGenius Solutions")
st.caption("LangGraph Multi-Agent Intent Router for Warangal Farmers")

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
