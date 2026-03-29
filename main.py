import os
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.main import app as api_app
from backend.app.core.config import settings

# Create the main app
app = FastAPI(title=f"{settings.APP_NAME} Unified")

# Mount the API router from the existing backend
app.mount("/api", api_app)

# Path to the frontend build directory
FRONTEND_DIST = os.path.join(os.getcwd(), "frontend", "dist")

# If the frontend is built, serve it as static files
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {
            "message": "Unified Fullstack Server is running!",
            "note": "Frontend not found in 'frontend/dist'. Please run 'npm run build' in the frontend directory.",
            "api_docs": "/api/docs"
        }

# Catch-all route for Single Page Application (SPA) support
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build files not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)
