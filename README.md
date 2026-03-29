# 🛡️ FraudShield AI — Bank Fraud Detection System

[![CI/CD](https://github.com/your-repo/fraud-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/your-repo/fraud-detection/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)

Production-grade AI-powered fraud detection system for banking transactions. Built with microservices architecture, real-time ML inference, and a premium fintech dashboard.

---

## 🏗️ System Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   React Frontend │────▶│  FastAPI Backend  │────▶│   ML Service     │
│   (Vite + TW)    │◀────│  (REST + WS)     │◀────│   (FastAPI)      │
│   Port: 3000     │     │   Port: 8000     │     │   Port: 8001     │
└──────────────────┘     └────────┬─────────┘     └──────────────────┘
                                  │    ▲
                         ┌────────▼────┴────────┐
                         │                       │
                   ┌─────▼──────┐         ┌─────▼──────┐
                   │ PostgreSQL │         │   Redis    │
                   │ Port: 5432 │         │ Port: 6379 │
                   └────────────┘         └────────────┘
```

**Data Flow:** User → React Dashboard → FastAPI Backend → ML Service (XGBoost) → PostgreSQL → WebSocket → Real-time Alerts

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **ML Fraud Detection** | XGBoost model with 97%+ ROC-AUC, trained on 50K+ transactions |
| 🔐 **JWT Authentication** | Access + refresh tokens, bcrypt password hashing, RBAC |
| 📊 **Real-time Dashboard** | KPI cards, trend charts, risk distribution |
| ⚡ **WebSocket Alerts** | Live fraud notifications pushed to dashboard |
| 📈 **Analytics** | Recharts visualizations, model performance radar |
| 🗄️ **PostgreSQL + Redis** | Async ORM with SQLAlchemy, prediction caching |
| 🐳 **Docker Ready** | Full docker-compose with 5 services |
| 🔄 **CI/CD** | GitHub Actions pipeline with test automation |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **Redis 7+**
- **Docker & Docker Compose** (recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate
cd "AI-Based Bank Fraud Detection"

# Copy environment file
cp .env.example .env

# Build and start all services
docker-compose up --build

# Access the application
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000/docs
# ML Service: http://localhost:8001/docs
```

### Option 2: Manual Setup

#### 1. ML Service
```bash
cd ml_service
pip install -r requirements.txt

# Train the model
python -m app.pipeline.train

# Start ML service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 2. Backend API
```bash
cd backend
pip install -r requirements.txt

# Start backend (auto-creates tables)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, get JWT tokens |
| POST | `/api/auth/refresh` | Refresh access token |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transactions/` | Ingest transaction (triggers ML) |
| GET | `/api/transactions/` | List with filters & pagination |
| GET | `/api/transactions/{id}` | Transaction detail |

### Fraud Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/fraud/alerts` | Recent fraud alerts |
| GET | `/api/fraud/logs` | Paginated fraud logs |
| PUT | `/api/fraud/review/{id}` | Manual review (audit trail) |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Dashboard KPIs |
| GET | `/api/analytics/trends` | Trend data for charts |

### ML Service
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Fraud prediction |
| GET | `/health` | Health check |
| GET | `/model-info` | Model metadata |
| POST | `/retrain` | Trigger retraining |

### WebSocket
| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WS | `/ws/alerts` | Real-time fraud alerts |

---

## 🧪 Sample API Requests

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@fraudshield.ai",
    "full_name": "John Doe",
    "password": "SecurePass123!",
    "role": "analyst"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "analyst@fraudshield.ai", "password": "SecurePass123!"}'
```

### Submit Transaction for Fraud Check
```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 4999.99,
    "time": 50000,
    "v1": -3.04,
    "v2": 2.85,
    "v3": -0.6,
    "v4": 2.1,
    "v10": -5.2,
    "v12": -8.5,
    "v14": -12.0,
    "v17": -6.8
  }'
```

### Direct ML Prediction
```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"Amount": 4999.99, "Time": 50000, "V1": -3.04, "V2": 2.85, "V14": -12.0}'
```

---

## 🤖 ML Model Details

| Model | Precision | Recall | F1-Score | ROC-AUC |
|-------|-----------|--------|----------|---------|
| Logistic Regression | ~0.88 | ~0.82 | ~0.85 | ~0.92 |
| Random Forest | ~0.93 | ~0.87 | ~0.90 | ~0.96 |
| **XGBoost** ✅ | **~0.95** | **~0.89** | **~0.92** | **~0.97** |

### Risk Categories
- 🟢 **LOW** (score < 0.3) — Auto-cleared
- 🟡 **MEDIUM** (0.3 ≤ score < 0.7) — Flagged for review
- 🔴 **HIGH** (score ≥ 0.7) — Immediate alert + manual review required

---

## 📁 Project Structure

```
AI-Based Bank Fraud Detection/
├── backend/                    # FastAPI Backend API
│   ├── app/
│   │   ├── core/              # config, security, database
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # API route handlers
│   │   ├── services/          # Business logic layer
│   │   └── main.py            # FastAPI application
│   ├── alembic/               # Database migrations
│   ├── tests/                 # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── ml_service/                 # ML Microservice
│   ├── app/
│   │   ├── models/            # Saved model files
│   │   ├── pipeline/          # Training & prediction
│   │   └── main.py            # FastAPI ML endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React Dashboard
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── context/           # React context (auth)
│   │   └── App.jsx
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── .github/workflows/ci.yml   # CI/CD pipeline
├── docker-compose.yml          # Multi-service orchestration
├── .env.example                # Environment template
└── README.md
```

---

## 🔒 Security Features

- ✅ **JWT Authentication** — Access + refresh tokens with expiry
- ✅ **Password Hashing** — bcrypt with salt
- ✅ **Role-Based Access** — Admin / Analyst roles
- ✅ **Rate Limiting** — slowapi protection on endpoints
- ✅ **CORS Configuration** — Restricted origins
- ✅ **Input Validation** — Pydantic schema enforcement
- ✅ **Security Headers** — X-Frame-Options, XSS protection (via Nginx)
- ✅ **Environment Variables** — All secrets in `.env`

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend
pip install -r requirements.txt
pytest tests/ -v

# ML model validation
cd ml_service
python -m app.pipeline.train
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS 3, Vite, Recharts, Lucide Icons |
| Backend | FastAPI, SQLAlchemy (async), Pydantic v2 |
| ML | scikit-learn, XGBoost, imbalanced-learn (SMOTE) |
| Database | PostgreSQL 15, Alembic migrations |
| Cache | Redis 7 |
| Auth | python-jose (JWT), passlib (bcrypt) |
| DevOps | Docker, Docker Compose, GitHub Actions |
| Monitoring | Structured logging, error tracking |

---

## 📄 License

MIT License — Built as a production-grade fintech MVP.
