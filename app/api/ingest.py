import os
import uuid
from fastapi import APIRouter, UploadFile, File
from app.services.text_extractor import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt
)
from app.services.chunker import chunk_text
from app.core.logger import get_logger

router = APIRouter(prefix="/api/v1", tags=["ingestion"])
logger = get_logger()

UPLOAD_DIR = "data/raw_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """
    Upload a document, extract its text, and chunk it for further processing.
    """
    file_extension = file.filename.split(".")[-1].lower()
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{unique_id}_{file.filename}")

    # Save the uploaded file locally
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text
    if file_extension == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension == "docx":
        text = extract_text_from_docx(file_path)
    elif file_extension == "txt":
        text = extract_text_from_txt(file_path)
    else:
        logger.error(f"Unsupported file type: {file_extension}")
        return {"error": f"Unsupported file type: {file_extension}"}
    
    # Split into chunks
    chunks = chunk_text(text)

    logger.info(f"Ingestion done {file.filename} | Chunks created: {len(chunks)}")

    return {
        "document_id": unique_id,
        "filename": file.filename,
        "total_chunks": len(chunks),
        "sample_chunk": chunks[0] if chunks else ""
    }