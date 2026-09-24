"""
LangGraph Multi-Agent Orchestrator for AgriGenius.
Coordinates incoming natural-language farmer queries for Warangal district, Telangana.
Uses Google Gemini 3.6 Flash when GOOGLE_API_KEY is available,
with automatic rule-based intent router fallback when unconfigured.
"""
import os
from typing import TypedDict, Optional, Dict, Any
import requests
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from backend.agents.crop_recommendation_agent import recommend_crops
from backend.agents.market_price_agent import get_market_price_analysis
from backend.agents.health_monitoring_agent import check_crop_health
from backend.agents.yield_prediction_agent import predict_yield
from backend.agents.loan_agent import evaluate_loan
from backend.agents.insurance_agent import evaluate_insurance
from backend.services.database import log_query

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("ANTHROPIC_API_KEY", "").strip()


class AgentState(TypedDict):
    query: str
    intent: str
    farmer_id: Optional[int]
    response: str
    metadata: Dict[str, Any]


SYSTEM_PROMPT = (
    "A farming assistant coordinator specifically supporting farmers in Warangal district, Telangana. "
    "The coordinator understands agriculture-related queries and routes them to specialized agents "
    "for crop recommendations, market prices, and crop health monitoring. "
    "It should communicate in simple, farmer-friendly language and consider local crops such as cotton and paddy."
)


def intent_router_node(state: AgentState) -> AgentState:
    """
    Determine farmer query intent using Gemini or rule-based fallback.
    """
    query = state.get("query", "").strip()
    query_lower = query.lower()
    intent = "general"

    # Attempt Gemini classification if a key is provided.
    if GOOGLE_API_KEY and not GOOGLE_API_KEY.startswith("your_"):
        try:
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Classify the following query into exactly one of these intents: "
                f"['crop_recommendation', 'market_price', 'health_monitoring', 'yield_prediction', 'loan_evaluation', 'insurance_evaluation', 'general'].\n"
                f"Respond with only the intent key string.\n\n"
                f"Query: {query}"
            )
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
                params={"key": GOOGLE_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=10,
            )
            if response.status_code >= 400:
                raise RuntimeError(f"Gemini request failed with HTTP {response.status_code}")
            response_data = response.json()
            classified = response_data["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
            valid_intents = [
                "crop_recommendation", "market_price", "health_monitoring",
                "yield_prediction", "loan_evaluation", "insurance_evaluation", "general"
            ]
            for v in valid_intents:
                if v in classified:
                    intent = v
                    break
        except Exception as e:
            print(f"[Orchestrator] Gemini call failed or key invalid, using rule-based fallback: {e}")

    # Fallback rule-based routing if LLM was skipped or failed
    if intent == "general":
        if any(w in query_lower for w in ["crop", "sow", "grow", "soil", "plant", "season", "kharif", "rabi", "seed", "recommend"]):
            intent = "crop_recommendation"
        elif any(w in query_lower for w in ["price", "mandi", "market", "sell", "rate", "cost", "quintal", "warangal mandi", "cotton price"]):
            intent = "market_price"
        elif any(w in query_lower for w in ["disease", "leaf", "pest", "yellow", "spot", "curl", "insect", "health", "spray", "treatment", "sick"]):
            intent = "health_monitoring"
        elif any(w in query_lower for w in ["yield", "production", "harvest", "tons", "quintals expected"]):
            intent = "yield_prediction"
        elif any(w in query_lower for w in ["loan", "kcc", "credit", "bank", "money", "finance", "borrow"]):
            intent = "loan_evaluation"
        elif any(w in query_lower for w in ["insurance", "claim", "pmfby", "loss", "damage", "premium"]):
            intent = "insurance_evaluation"

    state["intent"] = intent
    return state


def crop_recommendation_node(state: AgentState) -> AgentState:
    res = recommend_crops(water_source="Irrigated", season="Kharif")
    recs = res.get("recommendations", [])
    rec_text = "\n".join([f"• **{r['crop']}** ({int(r['confidence']*100)}% confidence): {r['reason']}" for r in recs])
    
    response = (
        f"🌾 **AgriGenius Crop Recommendation for Warangal District**\n\n"
        f"Based on local soil health profiles and climate seasonal norms:\n\n"
        f"{rec_text}\n\n"
        f"ℹ️ *Soil and weather data were automatically retrieved for your location.*"
    )
    state["response"] = response
    state["metadata"] = res
    return state


def market_price_node(state: AgentState) -> AgentState:
    # Check if query specifically mentions a crop
    query_lower = state["query"].lower()
    target_crop = "Cotton"
    if "paddy" in query_lower or "rice" in query_lower:
        target_crop = "Paddy"
    elif "maize" in query_lower or "corn" in query_lower:
        target_crop = "Maize"
    elif "red gram" in query_lower or "tur" in query_lower or "pulse" in query_lower:
        target_crop = "Red Gram"

    res = get_market_price_analysis(crop=target_crop)
    prices = res.get("mandi_prices", [])
    price_lines = "\n".join([f"• **{p['mandi']} Mandi**: ₹{p['current_price_per_quintal']:,} / Quintal (Trend: {p['trend'].upper()})" for p in prices])
    
    response = (
        f"📊 **AgriGenius Market Price Intelligence ({target_crop})**\n\n"
        f"Current prices across Warangal District Mandis:\n"
        f"{price_lines}\n\n"
        f"💡 **Recommendation**: {res.get('recommendation')}"
    )
    state["response"] = response
    state["metadata"] = res
    return state


def health_monitoring_node(state: AgentState) -> AgentState:
    query_lower = state["query"].lower()
    crop_type = "Paddy" if "paddy" in query_lower or "rice" in query_lower else "Cotton"
    
    res = check_crop_health(crop_type=crop_type, growth_stage="Vegetative")
    response = (
        f"🩺 **AgriGenius Crop Health Diagnostic ({crop_type})**\n\n"
        f"• **Condition Detected**: {res['disease']}\n"
        f"• **Confidence**: {int(res['confidence']*100)}%\n"
        f"• **Severity Level**: {res['severity'].upper()}\n\n"
        f"🛡️ **Recommended Treatment**: {res['recommended_action']}"
    )
    state["response"] = response
    state["metadata"] = res
    return state


def yield_prediction_node(state: AgentState) -> AgentState:
    res = predict_yield(land_area_hectares=1.5, crop="Cotton")
    response = (
        f"📈 **AgriGenius Yield Forecast (Phase 2 Simulation)**\n\n"
        f"• **Crop**: {res['crop']}\n"
        f"• **Predicted Yield**: {res['predicted_total_yield_quintals']} Quintals ({res['confidence_range']})\n"
        f"• **Estimated Harvest Date**: {res['estimated_harvest_date']}\n"
        f"• **Model Basis**: {res['model_used']}"
    )
    state["response"] = response
    state["metadata"] = res
    return state


def loan_evaluation_node(state: AgentState) -> AgentState:
    res = evaluate_loan(land_size=2.0, crop_plan="Cotton")
    response = (
        f"🏦 **AgriGenius Credit Simulation (Phase 2)**\n\n"
        f"• **Status**: {res['farmer_eligibility']}\n"
        f"• **Suggested Loan Limit**: ₹{res['suggested_loan_amount_inr']:,}\n"
        f"• **Scheme**: {res['scheme_name']}\n"
        f"• **Summary**: {res['application_summary']}\n\n"
        f"⚠️ *{res['disclaimer']}*"
    )
    state["response"] = response
    state["metadata"] = res
    return state


def insurance_evaluation_node(state: AgentState) -> AgentState:
    res = evaluate_insurance(crop_type="Cotton", land_area=2.0, damage_flag=False)
    response = (
        f"🛡️ **AgriGenius Insurance Assessment (Phase 2)**\n\n"
        f"• **Scheme**: {res['scheme_name']}\n"
        f"• **Sum Insured**: ₹{res['sum_insured_inr']:,}\n"
        f"• **Farmer Premium Payable**: ₹{res['farmer_premium_payable_inr']:,} ({res['premium_percentage']})\n"
        f"• **Claim Status**: {res['claim_status']}\n\n"
        f"⚠️ *{res['disclaimer']}*"
    )
    state["response"] = response
    state["metadata"] = res
    return state


def general_node(state: AgentState) -> AgentState:
    response = (
        f"Namaste! I am **AgriGenius**, your AI farming assistant for Warangal district, Telangana.\n\n"
        f"I can help you with:\n"
        f"1. **Crop Recommendations** — Best crops to sow for Kharif/Rabi seasons.\n"
        f"2. **Market Mandi Prices** — Daily rates at Warangal, Hanamkonda, Parkal & Narsampet.\n"
        f"3. **Crop Health Diagnostics** — Identifying cotton & paddy leaf diseases.\n"
        f"4. **Yield & Credit Simulations** — Estimating harvests, KCC loans & insurance claims.\n\n"
        f"How can I support your farm today?"
    )
    state["response"] = response
    state["metadata"] = {}
    return state


def route_decision(state: AgentState) -> str:
    return state.get("intent", "general")


# Build LangGraph StateGraph
builder = StateGraph(AgentState)

builder.add_node("intent_router", intent_router_node)
builder.add_node("crop_recommendation", crop_recommendation_node)
builder.add_node("market_price", market_price_node)
builder.add_node("health_monitoring", health_monitoring_node)
builder.add_node("yield_prediction", yield_prediction_node)
builder.add_node("loan_evaluation", loan_evaluation_node)
builder.add_node("insurance_evaluation", insurance_evaluation_node)
builder.add_node("general", general_node)

builder.add_edge(START, "intent_router")

builder.add_conditional_edges(
    "intent_router",
    route_decision,
    {
        "crop_recommendation": "crop_recommendation",
        "market_price": "market_price",
        "health_monitoring": "health_monitoring",
        "yield_prediction": "yield_prediction",
        "loan_evaluation": "loan_evaluation",
        "insurance_evaluation": "insurance_evaluation",
        "general": "general"
    }
)

builder.add_edge("crop_recommendation", END)
builder.add_edge("market_price", END)
builder.add_edge("health_monitoring", END)
builder.add_edge("yield_prediction", END)
builder.add_edge("loan_evaluation", END)
builder.add_edge("insurance_evaluation", END)
builder.add_edge("general", END)

orchestrator_graph = builder.compile()


def process_farmer_query(query: str, farmer_id: Optional[int] = 1) -> Dict[str, Any]:
    """
    Main entry point for natural language farmer queries.
    Executes LangGraph orchestration workflow and persists query log to database.
    """
    initial_state: AgentState = {
        "query": query,
        "intent": "general",
        "farmer_id": farmer_id,
        "response": "",
        "metadata": {}
    }

    final_state = orchestrator_graph.invoke(initial_state)

    # Log to SQLite DB
    try:
        log_query(
            query=query,
            response=final_state.get("response", ""),
            intent=final_state.get("intent", "general"),
            farmer_id=farmer_id
        )
    except Exception as e:
        print(f"[Orchestrator] DB log warning: {e}")

    return {
        "query": final_state.get("query"),
        "intent": final_state.get("intent"),
        "response": final_state.get("response"),
        "metadata": final_state.get("metadata", {})
    }
