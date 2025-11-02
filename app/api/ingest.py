import os
import uuid
import hashlib
from fastapi import APIRouter, UploadFile, File, HTTPException
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

embedder = EmbeddingGenerator()
vector_store = VectorStore()

def calculate_file_hash(file_bytes: bytes) -> str:
    """Compute a SHA-256 hash of the file content."""
    return hashlib.sha256(file_bytes).hexdigest()

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """
    Upload a document, extract its text, chunk it, embed it and store it in the vector database.
    Detects duplicates automatically via file hash.
    """
    try:
        logger.info(f"Ingestion -> Received file: {file.filename}")

        file_extension = file.filename.split(".")[-1].lower()
        file_bytes = await file.read()
        
        # Compute file hash for duplicate detection
        file_hash = calculate_file_hash(file_bytes)
        logger.info(f"Computed hash for {file.filename}: {file_hash}")
        
        # Check if file (by hash) already exists in chromadb
        existing = vector_store.collection.get(where={"file_hash": file_hash})
        if existing and len(existing["ids"]) > 0:
            logger.info(f"Duplicate file detected: {file.filename} with hash {file_hash}. Skipping ingestion.")
            return {
                "message": "File already ingested.",
                "document_id": existing["metadatas"][0]["document_id"],
                "filename": existing["metadatas"][0]["filename"]
            }
            
        # if same file, but content changed, re-index (incremental update)
        existing_by_name = vector_store.collection.get(where={"filename": file.filename})
        if existing_by_name and len(existing_by_name["ids"]) > 0:
            existing_hash = existing_by_name["metadatas"][0].get("file_hash", "")
            if existing_hash != file_hash:
                logger.info(f"File content changed for: {file.filename}. Re-indexing.")
                vector_store.collection.delete(where={"filename": file.filename})
        
        
        unique_doc_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{unique_doc_id}_{file.filename}")

        # Save the uploaded file locally
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Extract text
        if file_extension == "pdf":
            text = extract_text_from_pdf(file_path)
        elif file_extension == "docx":
            text = extract_text_from_docx(file_path)
        elif file_extension == "txt":
            text = extract_text_from_txt(file_path)
        else:
            logger.error(f"Unsupported file type: {file_extension}")
            return HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        if not text.strip():
            logger.error(f"No text extracted from file: {file.filename}")
            return HTTPException(status_code=400, detail="No readable text found in the document.")
        
        # Split into chunks
        chunks = chunk_text(text)
        logger.info(f"Ingestion done {file.filename} | Chunks created: {len(chunks)}")

        # Generate embeddings and store
        embeddings = embedder.generate_batch(chunks)
        logger.info(f"Embeddings generated for {file.filename}")
        
        # Add to chromadb with metadata including file hash
        ids = [f"{unique_doc_id}_{i}" for i in range(len(chunks))]
        metadata = [{"document_id": unique_doc_id, "filename": file.filename, "file_hash": file_hash} for _ in chunks]

        vector_store.add_documents(ids=ids, texts=chunks, embeddings=embeddings, metadata=metadata)

        return {
            "document_id": unique_doc_id,
            "filename": file.filename,
            "total_chunks": len(chunks),
            "sample_chunk": chunks[0] if chunks else ""
        }
    except Exception as e:
        logger.error(f"Error during ingestion of file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during ingestion.")