"""
AgriGenius Backend - Main FastAPI Application
Multi-agent agentic AI platform for farmers in Warangal, Telangana.

Run with:
    uvicorn backend.main:app --reload
"""
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from backend.agents.crop_recommendation_agent import recommend_crops
from backend.agents.market_price_agent import get_market_price
from backend.agents.health_monitoring_agent import analyze_leaf_image
from backend.orchestrator.orchestrator_agent import run_orchestrator
from backend.services.database import init_db, log_query

app = FastAPI(
    title="AgriGenius API",
    description="Multi-agent agentic AI platform for farmers in Warangal, Telangana",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    # Creates backend/data/agrigenius.db and all tables if they don't exist yet.
    init_db()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CropRecommendationRequest(BaseModel):
    water_source: str  # "irrigated" | "rainfed"
    season: str  # "Kharif" | "Rabi"
    village: Optional[str] = None
    # Soil/weather inputs are optional here — in production these are pulled
    # automatically from the Soil Health Card dataset + OpenWeatherMap
    # (see backend/services/weather_api.py and database.SoilHealthRecord).
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None


class MarketPriceRequest(BaseModel):
    crop: str
    mandi: Optional[str] = None  # None = check all Warangal-area mandis
    harvest_date: Optional[str] = None


class HealthCheckRequest(BaseModel):
    image_path: str
    crop_type: str  # "Cotton" | "Paddy"
    growth_stage: Optional[str] = None  # sowing | vegetative | flowering | maturity


class ChatRequest(BaseModel):
    query: str
    farmer_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Welcome to AgriGenius API", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Basic service health-check endpoint."""
    return {"status": "ok", "service": "AgriGenius Backend"}


@app.post("/crop-recommendation")
def crop_recommendation(req: CropRecommendationRequest):
    result = recommend_crops(
        nitrogen=req.nitrogen,
        phosphorus=req.phosphorus,
        potassium=req.potassium,
        ph=req.ph,
        temperature=req.temperature,
        humidity=req.humidity,
        rainfall=req.rainfall,
        water_source=req.water_source,
        season=req.season,
    )
    log_query(query_type="crop-recommendation", payload=req.dict(), result=result)
    return result


@app.post("/market-price")
def market_price(req: MarketPriceRequest):
    result = get_market_price(crop=req.crop, mandi=req.mandi)
    log_query(query_type="market-price", payload=req.dict(), result=result)
    return result


@app.post("/health-check-crop")
def health_check_crop(req: HealthCheckRequest):
    result = analyze_leaf_image(
        image_path=req.image_path,
        crop_type=req.crop_type,
        growth_stage=req.growth_stage,
    )
    log_query(query_type="health-check-crop", payload=req.dict(), result=result)
    return result


@app.post("/chat")
def chat(req: ChatRequest):
    """Natural-language entry point. Routes through the LangGraph orchestrator,
    which classifies intent and calls the relevant sub-agent (or Claude
    directly for general questions)."""
    result = run_orchestrator(query=req.query, farmer_id=req.farmer_id)
    log_query(query_type="chat", payload=req.dict(), result=result, farmer_id=req.farmer_id)
    return result
