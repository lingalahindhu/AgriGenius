"""
Database Service for AgriGenius.
Uses SQLite and SQLAlchemy for persistence.
"""
import os
from datetime import datetime
from typing import Optional, Generator
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Absolute path or local relative path to agri_genius.db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "agri_genius.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Farmer(Base):
    """
    Farmer profile table storing basic information about registered farmers.
    """
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), default="Warangal")
    land_size = Column(Float, default=1.0)  # in hectares
    crop_history = Column(Text, nullable=True)  # JSON or comma-separated history


class QueryLog(Base):
    """
    Log of all farmer queries, detected intents, and agent responses.
    """
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_id = Column(Integer, nullable=True)
    query = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    """
    Initialize SQLite database and create all tables if they do not exist.
    Seed default sample farmer profile if empty.
    """
    Base.metadata.create_all(bind=engine)
    
    # Create default demo farmer if table is empty
    db = SessionLocal()
    try:
        if db.query(Farmer).count() == 0:
            demo_farmer = Farmer(
                name="Ramesh Kumar",
                location="Warangal",
                land_size=2.5,
                crop_history="Cotton, Paddy"
            )
            db.add(demo_farmer)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] Initial seed error: {e}")
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_query(query: str, response: str, intent: Optional[str] = None, farmer_id: Optional[int] = 1) -> None:
    """
    Helper function to log a farmer's interaction into QueryLog.
    """
    db = SessionLocal()
    try:
        log_entry = QueryLog(
            farmer_id=farmer_id,
            query=query,
            intent=intent or "general",
            response=response
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] Log query error: {e}")
    finally:
        db.close()
