from fastapi import APIRouter, Query

from app.services.embeddings import EmbeddingGenerator
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/api/v1", tags=["query"])

embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()

@router.get("/query")
def semantic_search(q: str = Query(..., description="Search Query"), top_k: int = 3):
    """
    Retrieve top-K most semantically similar document chunks
    """
    query_embedding = embedding_generator.generate(q)
    results = vector_store.query_similar(query_embedding, top_k=top_k)

    docs = [
        {
            "document_id": meta.get("document_id"),
            "filename": meta.get("filename"),
            "text": text,
            "score": round(dist, 4)
        } for meta, text, dist in zip(results["metadatas"][0], results["documents"][0], results["distances"][0])
    ]

    return {
        "query": q,
        "top_k": top_k,
        "results": docs
    }