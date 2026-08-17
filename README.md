# AgriGenius — Multi-Agent Agentic AI Platform for Farmers

**AgriGenius** is a multi-agent agentic AI platform piloted specifically for farmers in **Warangal district, Telangana**. The platform focuses on the region's core staple crops—**Cotton** and **Paddy**—along with commercial rotation crops such as Maize and Red Gram.

It integrates LLM orchestration, Machine Learning, Computer Vision, Soil Health Card data, Weather API abstractions, and Agmarknet Mandi market pricing into an intuitive, accessible dashboard.

---

## 🌟 Key Capabilities & Modules

| Module | Purpose / Functionality | Input | Output |
| :--- | :--- | :--- | :--- |
| **Crop Recommendation** | Recommends optimal crops based on soil & seasonal norms. | Water source (Irrigated/Rainfed), Season (Kharif/Rabi) *(Soil & weather retrieved automatically)* | Top 2–3 crops, confidence scores, reasons |
| **Market Price Agent** | Daily mandi price intelligence & selling recommendations. | Crop name, Mandi (Warangal, Hanamkonda, Parkal, Narsampet) | Current price/quintal, trends (UP/DOWN/STABLE), best mandi |
| **Health Monitoring** | Leaf disease diagnosis & severity assessment. | Leaf photo upload, crop type, growth stage | Disease classification, confidence, severity, treatment |
| **Yield Prediction (Phase 2)** | Machine Learning yield forecast. | Farm area, crop type, soil/weather, health signals | Predicted yield in quintals, harvest date |
| **Loan Agent (Phase 2)** | Credit scale of finance evaluation. | Land size, crop plan, predicted yield | Kisan Credit Card eligibility, limit in ₹, scheme |
| **Insurance Agent (Phase 2)**| PMFBY crop insurance evaluation. | Crop, land area, region, disease damage flag | Policy premium, sum insured, claim payouts |

---

## 🏗 System Architecture

```text
                         ┌─────────────────────────┐
                         │   Streamlit Frontend    │
                         │    (frontend/app.py)    │
                         └────────────┬────────────┘
                                      │ HTTP REST API
                                      ▼
                         ┌─────────────────────────┐
                         │     FastAPI Server      │
                         │    (backend/main.py)    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   LangGraph Multi-Agent │
                         │    Orchestrator Agent   │
                         └────────────┬────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
     Crop Rec Agent           Market Price Agent      Health Monitoring Agent
             │                        │                        │
             ▼                        ▼                        ▼
      Soil + Weather             Agmarknet API             CNN Model
      Data Integration             (Mandis)              (Computer Vision)
             │                        │                        │
             └────────────────────────┼────────────────────────┘
                                      ▼
                            Phase 2 Intelligence
                                      │
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
       Yield Agent               Loan Agent             Insurance Agent
    (XGBoost / ML)             (Credit Engine)         (Claim Simulator)
```

---

## 🚀 Quick Start (Mock-First Setup)

AgriGenius is built **mock-first**. It runs immediately after cloning and installing dependencies without requiring external API keys or pre-trained ML model files.

### 1. Clone & Set Up Virtual Environment

```bash
git clone <repository-url>
cd agriagent-warangal
python -m venv venv
```

**Activate environment:**
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\activate
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Environment Setup (Optional)

```bash
copy .env.example .env
```

*Note: If `ANTHROPIC_API_KEY`, `AGMARKNET_API_KEY`, or `WEATHER_API_KEY` are left blank, AgriGenius automatically operates using local expert rules and mock services.*

---

## 🖥 Running the Application

### Option A: Run Backend FastAPI Server

```bash
uvicorn backend.main:app --reload
```
- **API Base URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`

### Option B: Run Frontend Streamlit Application

In a separate terminal (with venv activated):

```bash
streamlit run frontend/app.py
```
- **Dashboard URL:** `http://localhost:8501`

---

## 📊 Dataset Architecture (Ready for Plugin Integration)

The project structure is designed to ingest real datasets without altering the core API signatures:

1. **Agmarknet Mandi Prices (`data.gov.in`)**: State = Telangana, District = Warangal.
2. **Crop Recommendation Dataset (`Kaggle`)**: Features: `N`, `P`, `K`, `temperature`, `humidity`, `pH`, `rainfall`.
3. **PlantVillage & Cotton Leaf Disease Datasets (`Kaggle`)**: Training images for Cotton (Leaf Curl, Pink Bollworm) and Paddy (Blast).
4. **Soil Health Card Dataset (`data.gov.in`)**: Village/Mandal level N-P-K-pH mapping for Warangal.
5. **Telangana Crop Yield Statistics (`DES Telangana`)**: Historical production statistics for XGBoost yield training.

---

## 🛠 Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic, SQLAlchemy, SQLite
- **Multi-Agent Orchestration**: LangGraph, LangChain Anthropic (Claude Sonnet 4.6)
- **Machine Learning & Data Processing**: scikit-learn, XGBoost, Pandas, NumPy
- **Frontend**: Streamlit, Custom HTML/CSS
- **External Integration Abstractions**: OpenWeatherMap API, Agmarknet API
