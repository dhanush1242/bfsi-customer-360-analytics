import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.config import API_TITLE, API_VERSION
from src.api.routes_c360 import router as c360_router
from src.api.routes_analytics import router as analytics_router
from src.api.routes_governance import router as governance_router
from src.api.routes_exports import router as exports_router

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Enterprise BFSI Customer 360 Data Product API with Star Schema, ETL Pipeline, DQ Layer & Lineage.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(c360_router)
app.include_router(analytics_router)
app.include_router(governance_router)
app.include_router(exports_router)

# Mount Static UI Files
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Customer 360 API is running. Visit /docs for Swagger UI or open static/index.html."}

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": API_TITLE,
        "version": API_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    from src.config import API_HOST, API_PORT
    uvicorn.run("src.api.main:app", host=API_HOST, port=API_PORT, reload=True)
