"""
Orchestrator Agent for AgriGenius
Uses LangGraph to route a farmer's natural-language query to the right
sub-agent (crop advice / market price / health check), and calls Claude
(Anthropic API) to coordinate/answer general questions.
"""
import os
from typing import Literal, Optional, TypedDict

from langgraph.graph import END, StateGraph

try:
    from anthropic import Anthropic
except ImportError:  # anthropic package not installed yet
    Anthropic = None

from backend.agents.crop_recommendation_agent import recommend_crops
from backend.agents.health_monitoring_agent import analyze_leaf_image
from backend.agents.market_price_agent import get_market_price

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are AgriGenius, an agentic AI farming assistant coordinator
for farmers in Warangal district, Telangana, India. Your job is to understand a
farmer's question (which may be in English, Telugu, or a Telugu-English mix)
and either answer directly or hand off to a specialist agent:

- crop_recommendation: which crop to grow, best crop for a season/soil
- market_price: mandi prices, when/where to sell, price trends
- health_check: plant/leaf disease, pest issues, crop health

Your focus areas are cotton and paddy farming across Warangal, Hanamkonda,
Parkal and Narsampet mandals. Be practical, concise, and speak to a farmer
audience in simple, direct language.
"""


class OrchestratorState(TypedDict, total=False):
    query: str
    farmer_id: Optional[int]
    intent: Optional[str]
    response: Optional[dict]


Intent = Literal["crop_recommendation", "market_price", "health_check", "general"]


def _classify_intent(query: str) -> Intent:
    """Simple keyword-based intent classifier (placeholder).
    Replace with an LLM-based classification call for production use."""
    q = query.lower()
    if any(k in q for k in ["price", "mandi", "sell", "rate", "market"]):
        return "market_price"
    if any(k in q for k in ["disease", "leaf", "pest", "spot", "yellow", "infection", "health"]):
        return "health_check"
    if any(k in q for k in ["crop", "grow", "plant", "sow", "recommend", "season"]):
        return "crop_recommendation"
    return "general"


def _call_claude(prompt: str) -> str:
    """Placeholder call to the Anthropic API for general/coordinator responses.
    Falls back to a mock string if ANTHROPIC_API_KEY isn't configured."""
    if not ANTHROPIC_API_KEY or Anthropic is None:
        return (
            "[MOCK RESPONSE] ANTHROPIC_API_KEY not configured (or the "
            "'anthropic' package isn't installed). This is a placeholder "
            f"answer for: '{prompt}'"
        )
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        block.text for block in message.content if getattr(block, "type", None) == "text"
    )


# ---------------------------------------------------------------------------
# LangGraph nodes
# ---------------------------------------------------------------------------

def classify_node(state: OrchestratorState) -> OrchestratorState:
    return {**state, "intent": _classify_intent(state["query"])}


def crop_node(state: OrchestratorState) -> OrchestratorState:
    result = recommend_crops(water_source="irrigated", season="Kharif")
    return {**state, "response": {"agent": "crop_recommendation", "result": result}}


def market_node(state: OrchestratorState) -> OrchestratorState:
    result = get_market_price(crop="cotton", mandi=None)
    return {**state, "response": {"agent": "market_price", "result": result}}


def health_node(state: OrchestratorState) -> OrchestratorState:
    result = analyze_leaf_image(image_path="placeholder.jpg", crop_type="Cotton")
    return {**state, "response": {"agent": "health_check", "result": result}}


def general_node(state: OrchestratorState) -> OrchestratorState:
    answer = _call_claude(state["query"])
    return {**state, "response": {"agent": "general", "result": {"answer": answer}}}


def route_intent(state: OrchestratorState) -> str:
    return state.get("intent", "general")


def build_graph():
    graph = StateGraph(OrchestratorState)
    graph.add_node("classify", classify_node)
    graph.add_node("crop_recommendation", crop_node)
    graph.add_node("market_price", market_node)
    graph.add_node("health_check", health_node)
    graph.add_node("general", general_node)

    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        route_intent,
        {
            "crop_recommendation": "crop_recommendation",
            "market_price": "market_price",
            "health_check": "health_check",
            "general": "general",
        },
    )
    graph.add_edge("crop_recommendation", END)
    graph.add_edge("market_price", END)
    graph.add_edge("health_check", END)
    graph.add_edge("general", END)
    return graph.compile()


_compiled_graph = None


def run_orchestrator(query: str, farmer_id: Optional[int] = None) -> dict:
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()

    initial_state: OrchestratorState = {"query": query, "farmer_id": farmer_id}
    final_state = _compiled_graph.invoke(initial_state)
    return {
        "query": query,
        "intent": final_state.get("intent"),
        "response": final_state.get("response"),
    }


if __name__ == "__main__":
    print(run_orchestrator("What price is cotton at in Warangal mandi today?"))
