from fastapi import FastAPI

from app.core.config import settings
from app.core.db import Base, engine
from app.core.logger import get_logger
from app.api import ingest

logger = get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI backend for document ingestion, semantic search, and AI-driven Q&A using RAG architecture.",
    version="1.0.0"
)

# Create DB tables automatically on startup (temporary for development)
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    logger.info(f"Starting up {settings.PROJECT_NAME} in {settings.ENV} environment.")
    logger.info(f"Connected to database at {settings.DATABASE_URL}")

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify that the service is running.`
    """
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} is running."}

# INGESTION ROUTES
app.include_router(ingest.router)