"""
Database Service for AgriGenius
This is the single SQLite/SQLAlchemy connection point every agent and route
should use for persistence. It is wired into backend/main.py already
(init_db() runs on startup, log_query() is called from every route).

Tables:
- Farmer           : registered farmer profiles
- QueryLog         : audit trail of every request made to the API/agents
- SoilHealthRecord : ingested rows from the Soil Health Card dataset
                      (data.gov.in, Telangana/Warangal) — feeds the Crop
                      Recommendation Agent at inference time
- MandiPriceRecord : ingested rows from the data.gov.in "Variety-wise Daily
                      Market Prices Data of Commodity" dataset — will
                      eventually replace the mock logic in
                      market_price_agent.py

Quick start:
    python -m backend.services.database
    -> creates backend/data/agrigenius.db with all tables

Loading a downloaded dataset CSV into the DB:
    from backend.services.database import load_csv_into_table, SoilHealthRecord
    load_csv_into_table(
        "backend/data/soil_health_warangal.csv",
        SoilHealthRecord,
        {"Village": "village", "Mandal": "mandal", "N": "nitrogen",
         "P": "phosphorus", "K": "potassium", "pH": "ph"},
    )
"""
import json
import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "agrigenius.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False so the same SQLite connection can be shared across
# FastAPI's threadpool and Streamlit's script-rerun model during dev.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))  # village/mandal within Warangal district
    land_size = Column(Float)  # in hectares
    crop_history = Column(Text)  # JSON-encoded list of past crops

    query_logs = relationship("QueryLog", back_populates="farmer")


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    query_type = Column(String(64))  # crop-recommendation | market-price | health-check-crop | chat
    payload = Column(Text)  # JSON-encoded request payload
    result = Column(Text)  # JSON-encoded response
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="query_logs")


class SoilHealthRecord(Base):
    """Rows ingested from the data.gov.in Soil Health Card dataset for
    Warangal district. Used to auto-populate N/P/K/pH for the Crop
    Recommendation Agent instead of manual farmer entry."""

    __tablename__ = "soil_health_records"

    id = Column(Integer, primary_key=True, index=True)
    village = Column(String(255))
    mandal = Column(String(255))
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
    ph = Column(Float)
    organic_carbon = Column(Float)
    sample_date = Column(String(32))


class MandiPriceRecord(Base):
    """Rows ingested from the data.gov.in 'Variety-wise Daily Market Prices
    Data of Commodity' dataset, filtered to Warangal district. Used to
    eventually replace the mock logic in market_price_agent.py."""

    __tablename__ = "mandi_price_records"

    id = Column(Integer, primary_key=True, index=True)
    mandi = Column(String(128))
    commodity = Column(String(128))
    variety = Column(String(128))
    arrival_date = Column(String(32))
    min_price = Column(Float)
    max_price = Column(Float)
    modal_price = Column(Float)


def init_db():
    """Creates backend/data/ (if missing) and all tables above."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: `db: Session = Depends(get_db)`."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_query(query_type: str, payload: dict, result: dict, farmer_id: Optional[int] = None):
    """Writes one audit-trail row per API call. Used directly by main.py
    routes so they don't each need a FastAPI Depends(get_db)."""
    db = SessionLocal()
    try:
        entry = QueryLog(
            farmer_id=farmer_id,
            query_type=query_type,
            payload=json.dumps(payload, default=str),
            result=json.dumps(result, default=str),
        )
        db.add(entry)
        db.commit()
    finally:
        db.close()


def load_csv_into_table(csv_path: str, model_class, column_mapping: dict) -> int:
    """Bulk-loads a downloaded dataset CSV (e.g. Soil Health Card or
    Agmarknet/data.gov.in price data) into one of the tables above.

    column_mapping maps {csv_column_name: model_column_name}. Returns the
    number of rows inserted.
    """
    import pandas as pd

    df = pd.read_csv(csv_path)
    df = df.rename(columns=column_mapping)
    keep_cols = [c.name for c in model_class.__table__.columns if c.name in df.columns]
    df = df[keep_cols]

    db = SessionLocal()
    try:
        records = [model_class(**row.to_dict()) for _, row in df.iterrows()]
        db.bulk_save_objects(records)
        db.commit()
        return len(records)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print(f"AgriGenius database initialized at: {os.path.abspath(DB_PATH)}")
