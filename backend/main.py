"""
AgriGenius FastAPI Application Backend.
Provides RESTful APIs for Multi-Agent Agentic AI Platform tailored for Warangal district farmers.
"""
import os
import shutil
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.services.database import init_db
from backend.agents.crop_recommendation_agent import recommend_crops
from backend.agents.market_price_agent import get_market_price_analysis
from backend.agents.health_monitoring_agent import check_crop_health
from backend.agents.yield_prediction_agent import predict_yield
from backend.agents.loan_agent import evaluate_loan
from backend.agents.insurance_agent import evaluate_insurance
from backend.orchestrator.orchestrator_agent import process_farmer_query


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite Database tables on application startup
    try:
        init_db()
        print("[AgriGenius] SQLite Database initialized successfully.")
    except Exception as e:
        print(f"[AgriGenius] Database initialization warning: {e}")
    yield


app = FastAPI(
    title="AgriGenius API",
    description="Multi-Agent Agentic AI Platform for Farmers in Warangal District, Telangana",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit / web client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request & Response Models ---

class CropRecommendationRequest(BaseModel):
    water_source: str = Field("Irrigated", description="Water access: Irrigated or Rainfed")
    season: str = Field("Kharif", description="Farming season: Kharif or Rabi")


class ChatRequest(BaseModel):
    query: str = Field(..., description="Farmer's natural language query")
    farmer_id: Optional[int] = Field(1, description="Registered farmer ID")


class YieldPredictionRequest(BaseModel):
    land_area_hectares: float = Field(1.0, description="Land area in hectares")
    crop: str = Field("Cotton", description="Crop type")


class LoanEvaluationRequest(BaseModel):
    land_size: float = Field(1.0, description="Land size in hectares")
    crop_plan: str = Field("Cotton", description="Crop plan")
    predicted_yield: Optional[float] = Field(None, description="Estimated yield in quintals")


class InsuranceEvaluationRequest(BaseModel):
    crop_type: str = Field("Cotton", description="Crop type")
    land_area: float = Field(1.0, description="Land area in hectares")
    region: str = Field("Warangal", description="District region")
    damage_flag: bool = Field(False, description="Disease/damage flag from Health Agent")


# --- Endpoints ---

@app.get("/health")
def health_check():
    """
    Health check endpoint returning AgriGenius service status.
    """
    return {
        "status": "healthy",
        "service": "AgriGenius",
        "district": "Warangal, Telangana",
        "architecture": "LangGraph Multi-Agent System"
    }


@app.post("/crop-recommendation")
def get_crop_recommendations(req: CropRecommendationRequest):
    """
    Recommend top crops based on water source and season.
    Soil and weather metrics are automatically retrieved.
    """
    try:
        res = recommend_crops(water_source=req.water_source, season=req.season)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market-price")
def get_mandi_market_prices(
    crop: Optional[str] = Query("Cotton", description="Crop name e.g. Cotton, Paddy, Maize, Red Gram"),
    mandi: Optional[str] = Query(None, description="Optional mandi preference: Warangal, Hanamkonda, Parkal, Narsampet"),
    harvest_date: Optional[str] = Query(None, description="Optional target harvest date")
):
    """
    Get market prices, trends, and selling advice across Warangal district mandis.
    """
    try:
        res = get_market_price_analysis(crop=crop, mandi=mandi, harvest_date=harvest_date)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/health-check-crop")
async def health_check_crop(
    crop_type: str = Form("Cotton"),
    growth_stage: str = Form("Vegetative"),
    file: Optional[UploadFile] = File(None)
):
    """
    Accept an uploaded leaf image with crop type and growth stage to analyze disease severity and treatment.
    """
    saved_image_path = None
    if file:
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "uploads")
        os.makedirs(temp_dir, exist_ok=True)
        saved_image_path = os.path.join(temp_dir, file.filename)
        with open(saved_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    try:
        res = check_crop_health(
            image_path=saved_image_path,
            crop_type=crop_type,
            growth_stage=growth_stage
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat_with_agent(req: ChatRequest):
    """
    Natural-language endpoint routing farmer queries to the LangGraph orchestrator.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        res = process_farmer_query(query=req.query, farmer_id=req.farmer_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Phase 2 Extended Endpoints ---

@app.post("/yield-prediction")
def get_yield_prediction(req: YieldPredictionRequest):
    """
    Phase 2: Yield prediction model simulation endpoint.
    """
    try:
        return predict_yield(land_area_hectares=req.land_area_hectares, crop=req.crop)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/loan-evaluation")
def get_loan_evaluation(req: LoanEvaluationRequest):
    """
    Phase 2: Credit scale of finance evaluation endpoint.
    """
    try:
        return evaluate_loan(land_size=req.land_size, crop_plan=req.crop_plan, predicted_yield=req.predicted_yield)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insurance-evaluation")
def get_insurance_evaluation(req: InsuranceEvaluationRequest):
    """
    Phase 2: PMFBY insurance premium & claim evaluation endpoint.
    """
    try:
        return evaluate_insurance(crop_type=req.crop_type, land_area=req.land_area, region=req.region, damage_flag=req.damage_flag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
