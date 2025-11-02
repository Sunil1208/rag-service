from fastapi import APIRouter, Body
from app.services.embeddings import EmbeddingGenerator
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/api/v1", tags=["Completeness"])

embedder = EmbeddingGenerator()
vector_store = VectorStore()

@router.post("/completeness")
def check_completeness(document_id: str = Body(..., embed=True), topics: list[str] = Body(..., embed=True), threshold: float = 0.9):
    """
    Evaluate which topics are covered in a specific document
    """
    
    results = {
        "covered": [],
        "missing": []
    }
    
    for topic in topics:
        topic_vec = embedder.generate(topic)
        # Search only within the specified document
        search_results = vector_store.collection.query(
            query_embeddings=[topic_vec],
            n_results=1,
            where={"document_id": document_id}
        )
        
        score = search_results["distances"][0][0]
        
        if score <= threshold:
            results["covered"].append(topic)
        else:
            results["missing"].append(topic)
            
        coverage = (len(results["covered"]) / len(topics)) * 100 if topics else 0.0
        
        return {
            "document_id": document_id,
            "covered": results["covered"],
            "missing": results["missing"],
            "coverage": round(coverage, 2)
        }
