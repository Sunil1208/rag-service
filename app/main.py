from fastapi import FastAPI

app = FastAPI(
    title="RAG Service",
    description="FastAPI backend for document ingestion, semantic search, and AI-driven Q&A using RAG architecture.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify that the service is running.
    """
    return {"status": "ok", "message": "RAG Service is running."}