import os
import uuid
from fastapi import APIRouter, UploadFile, File
from app.services.text_extractor import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt
)
from app.services.chunker import chunk_text
from app.services.embeddings import EmbeddingGenerator
from app.services.vector_store import VectorStore
from app.core.logger import get_logger

router = APIRouter(prefix="/api/v1", tags=["ingestion"])
logger = get_logger()

UPLOAD_DIR = "data/raw_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """
    Upload a document, extract its text, chunk it, embed it and store it in the vector database.
    """
    file_extension = file.filename.split(".")[-1].lower()
    unique_doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{unique_doc_id}_{file.filename}")

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

    # Generate embeddings and store
    ids = [f"{unique_doc_id}_{i}" for i in range(len(chunks))]
    embeddings = [embedding_generator.generate(chunk) for chunk in chunks]
    logger.info(f"Embeddings generated for {file.filename}")
    metadata = [{"document_id": unique_doc_id, "filename": file.filename} for _ in chunks]

    vector_store.add_documents(ids=ids, texts=chunks, embeddings=embeddings, metadata=metadata)

    return {
        "document_id": unique_doc_id,
        "filename": file.filename,
        "total_chunks": len(chunks),
        "sample_chunk": chunks[0] if chunks else ""
    }