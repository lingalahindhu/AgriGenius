# AgriGenius

**AgriGenius** is a multi-agent, agentic AI platform being piloted for farmers in
Warangal district, Telangana — initially covering **cotton and paddy**. A
LangGraph-based orchestrator agent understands a farmer's natural-language
question and routes it to the right specialist agent — crop recommendation,
market price lookup, or crop health monitoring — with a FastAPI backend, a
Streamlit farmer-facing UI, and a SQLite database for storing farmer profiles,
ingested datasets, and query history.

This repo is the **base scaffold**: every route and agent works end-to-end with
mock/placeholder logic so you can run it immediately, then swap in trained
models and real API integrations module by module.

---

## Project Structure

```
agriagent-warangal/
├── backend/
│   ├── main.py                              # FastAPI app + routes
│   ├── orchestrator/orchestrator_agent.py    # LangGraph orchestrator (intent routing + Claude)
│   ├── agents/
│   │   ├── crop_recommendation_agent.py
│   │   ├── market_price_agent.py
│   │   └── health_monitoring_agent.py
│   ├── services/
│   │   ├── agmarknet_api.py                  # real mandi price API (placeholder)
│   │   ├── weather_api.py                    # OpenWeatherMap (placeholder)
│   │   └── database.py                       # SQLAlchemy models + DB connection
│   ├── models/                               # saved .pkl / .pt model files go here
│   ├── data/                                 # datasets + agrigenius.db go here
│   └── requirements.txt
├── frontend/app.py                           # Streamlit UI (4 tabs)
├── notebooks/                                # exploration / model training notebooks
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

```bash
# 1. Clone and enter the project
cd agriagent-warangal

# 2. Create and activate a virtual environment
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then edit .env and add your ANTHROPIC_API_KEY (and later, AGMARKNET_API_KEY / WEATHER_API_KEY)
```

### Run the backend (FastAPI)

```bash
uvicorn backend.main:app --reload
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- On startup, this automatically creates `backend/data/agrigenius.db` with all tables.

### Run the frontend (Streamlit)

In a second terminal (with the backend still running):

```bash
streamlit run frontend/app.py
```

This opens the farmer-facing UI with four tabs: Crop Recommendation, Market
Price, Health Check, and Chat — all calling the FastAPI backend at
`http://localhost:8000`.

---

## Database — how it connects

`backend/services/database.py` is the single connection point for all
persistence (SQLite via SQLAlchemy, file at `backend/data/agrigenius.db`):

| Table               | Purpose |
|---------------------|---------|
| `farmers`           | Registered farmer profiles (id, name, location, land_size, crop_history) |
| `query_logs`         | Audit trail of every API call (already wired into every route in `main.py`) |
| `soil_health_records`| Ingested rows from the **Soil Health Card** dataset (data.gov.in), used to auto-populate N/P/K/pH for the Crop Recommendation Agent |
| `mandi_price_records` | Ingested rows from the **Variety-wise Daily Market Prices** dataset (data.gov.in), will replace the mock logic in `market_price_agent.py` |

`init_db()` runs automatically on FastAPI startup. To load a downloaded
dataset CSV into the database:

```python
from backend.services.database import load_csv_into_table, SoilHealthRecord

load_csv_into_table(
    "backend/data/soil_health_warangal.csv",
    SoilHealthRecord,
    {"Village": "village", "Mandal": "mandal", "N": "nitrogen",
     "P": "phosphorus", "K": "potassium", "pH": "ph"},
)
```

You can inspect the database directly with any SQLite client, e.g.:

```bash
sqlite3 backend/data/agrigenius.db ".tables"
```

---

## Datasets to plug in

| Dataset | Source | Feeds into |
|---|---|---|
| Variety-wise Daily Market Prices Data of Commodity | data.gov.in (filter State=Telangana, District=Warangal) | `mandi_price_records` → Market Price Agent |
| Crop Recommendation Dataset | Kaggle | Trains `backend/models/crop_recommendation_model.pkl` |
| PlantVillage Dataset | Kaggle | Trains the leaf-disease CNN for the Health Monitoring Agent |
| Cotton Leaf Disease Dataset | Kaggle | Supplements PlantVillage with cotton-specific diseases (pink bollworm, leaf curl) |
| Soil Health Card Data | data.gov.in (Telangana/Warangal) | `soil_health_records` → auto-fills Crop Recommendation inputs |
| District-wise Crop Yield / Area / Production statistics | data.gov.in / Telangana Directorate of Economics & Statistics | Trains the Phase 2 Yield Prediction model |

---

## Roadmap

### Phase 1 (this scaffold)
- Crop Recommendation Agent (N/P/K, pH, temperature, humidity, rainfall → top 2–3 crops)
- Market Price Agent (mandi prices + up/down/stable trend + sell recommendation)
- Health Monitoring Agent (leaf image → disease/healthy classification + treatment advice)

### Phase 2
- Yield Prediction Agent (land area + soil/weather + health signals → predicted yield & harvest date)
- Loan Agent (simulated eligibility, suggested amount/scheme, auto-filled application)
- Insurance Agent (simulated premium estimate + claim simulation, triggered by damage flags from the Health Monitoring Agent)

---

## Tech Stack

- **Backend:** Python 3.11, FastAPI
- **Agent orchestration:** LangGraph
- **Frontend:** Streamlit
- **Storage:** SQLite + SQLAlchemy
- **ML:** scikit-learn, XGBoost
- **LLM:** Claude (Anthropic API) as the orchestrator's coordinator model
