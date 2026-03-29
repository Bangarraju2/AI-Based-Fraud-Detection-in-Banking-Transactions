@echo off
echo 🛡️ Starting FraudShield AI Unified Server...
echo ------------------------------------------

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Check for FastAPI (simple dependency check)
python -c "import fastapi" >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Missing Python dependencies (fastapi not found).
    echo [INFO] Running environment setup...
    call setup_env.bat
)

:: Check for frontend build
if not exist "frontend\dist" (
    echo [INFO] Frontend build not found. Building now...
    cd frontend && npm run build && cd ..
)

:: Start the unified server
echo [INFO] Starting FastAPI server at http://localhost:8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
