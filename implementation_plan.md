# AI-Based Fraud Detection in Banking Transactions

Production-grade fintech SaaS system for real-time fraud detection, designed as a modular microservices architecture.

## System Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   React UI   │────▶│  FastAPI      │────▶│  ML Service  │
│  (Vite+TW)   │◀────│  Backend     │◀────│  (FastAPI)   │
└──────────────┘     └──────┬───────┘     └──────────────┘
                           │    ▲
                    ┌──────▼────┴──────┐
                    │                   │
              ┌─────▼─────┐     ┌──────▼─────┐
              │ PostgreSQL │     │   Redis     │
              │  Database  │     │   Cache     │
              └────────────┘     └────────────┘
```

**Data Flow**: User → React UI → FastAPI Backend → ML Service → PostgreSQL → WebSocket → Dashboard

## Proposed Changes

### Phase 1: Project Foundation

#### [NEW] Project folder structure
```
AI-Based Bank Fraud Detection/
├── backend/
│   ├── app/
│   │   ├── core/              # config, security, database
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API route handlers
│   │   ├── services/          # Business logic
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── ml_service/
│   ├── app/
│   │   ├── models/            # Trained model files
│   │   ├── pipeline/          # Training pipeline
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── context/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
├── .env.example
└── README.md
```

---

### Phase 2: Machine Learning Module

#### [NEW] ml_service/app/pipeline/data_preprocessing.py
- Synthetic credit card fraud data generator (no manual download needed)
- StandardScaler feature scaling
- Feature engineering: time-based features, amount bins
- SMOTE oversampling for class imbalance

#### [NEW] ml_service/app/pipeline/train.py
- Train 3 models: Logistic Regression, Random Forest, XGBoost
- Evaluate with precision, recall, F1, ROC-AUC
- Compare & select best model, save with joblib

#### [NEW] ml_service/app/pipeline/predict.py
- Load saved model, return fraud probability (0.0–1.0)
- Risk categorization: Low (<0.3), Medium (0.3–0.7), High (>0.7)
- Feature importance explanations

#### [NEW] ml_service/app/main.py
- FastAPI `/predict` endpoint with Pydantic validation

---

### Phase 3: Backend API (FastAPI)

#### [NEW] backend/app/core/ — config.py, security.py, database.py
- Settings from `.env`, JWT (access+refresh), bcrypt, SQLAlchemy async engine

#### [NEW] backend/app/models/ — user.py, transaction.py, fraud_log.py
- Users, Transactions (with fraud_score, risk_category), Fraud Logs

#### [NEW] backend/app/schemas/ — Pydantic request/response models

#### [NEW] backend/app/routers/
- `auth.py` — register, login, refresh token
- `transactions.py` — ingest (triggers ML), list, detail
- `fraud.py` — alerts, logs, manual review
- `analytics.py` — KPIs, trends
- `websocket.py` — real-time fraud notifications

#### [NEW] backend/app/services/
- `ml_client.py`, `fraud_service.py`, `cache_service.py`

---

### Phase 4: Redis Cache
- Integrated into backend services
- Cache predictions by transaction hash, TTL-based expiry

---

### Phase 5: Frontend (React + Tailwind CSS v3)

- Vite + React + Tailwind + Recharts + React Router + Axios
- **Pages**: Login, Signup, Dashboard (KPIs + charts), Transactions (table), Fraud Alerts (WebSocket), Analytics
- **Components**: Sidebar, Navbar, StatCard, DataTable, ChartCard, AlertBanner
- Dark mode, responsive, premium fintech design

---

### Phase 6: Testing
- `backend/tests/` — test_auth, test_transactions, test_fraud, conftest
- `ml_service/tests/` — test_predict

---

### Phase 7: DevOps
- Dockerfiles for backend, ml_service, frontend
- `docker-compose.yml` — 5 services with networking
- `.github/workflows/ci.yml` — pytest, Docker build

---

### Phase 8: Documentation
- README.md with setup, architecture, cURL examples
- .env.example with all variables

---

## Verification Plan

### Automated Tests
```bash
cd backend && pip install -r requirements.txt && pytest tests/ -v
cd ml_service && pip install -r requirements.txt && pytest tests/ -v
```

### Manual Verification
1. Run `docker-compose up --build` — verify all services start
2. Open `http://localhost:3000` — verify login, dashboard, dark mode
3. Test API at `http://localhost:8000/docs`
4. Submit sample transaction → verify fraud score returned
5. Check real-time fraud alert on dashboard via WebSocket

> [!IMPORTANT]
> A synthetic data generator is included so no manual dataset download is required.
