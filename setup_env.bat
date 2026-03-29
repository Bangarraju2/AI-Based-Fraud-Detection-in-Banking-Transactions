@echo off
echo 🛡️ FraudShield AI - Dependency Installer
echo ------------------------------------------

:: Install Backend Dependencies
echo [INFO] Installing backend dependencies...
pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b %errorlevel%
)

:: Install Frontend Dependencies
echo [INFO] Installing frontend dependencies...
cd frontend && npm install && cd ..
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies.
    pause
    exit /b %errorlevel%
)

echo [SUCCESS] All dependencies installed successfully!
pause
