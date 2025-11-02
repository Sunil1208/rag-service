from fastapi import APIRouter, Query
from app.services.embeddings import EmbeddingGenerator
from app.services.vector_store import VectorStore
from app.services.qa_service import QAGenerator
from app.core.logger import get_logger

router = APIRouter(prefix="/api/v1", tags=["Q&A"])
logger = get_logger()

embedder = EmbeddingGenerator()
vector_store = VectorStore()
qa_model = QAGenerator()

@router.get("/qa")
def answer_question(q: str = Query(..., description="User question"), top_k: int = 3):
    """
    Retrieve top-K relevant chunks and generate an answer to the user question.
    """
    logger.info(f"Received QA query: {q}")

    # 1. Retrieve relevant chunks of top-K
    query_vec = embedder.generate(q)
    results = vector_store.query_similar(query_embedding=query_vec, top_k=top_k)

    # 2. Concatenate the retrieved chunks to form context
    context_chunks = results["documents"][0]
    context = "\n".join(context_chunks)

    # 3. Generate answer using the QA model
    answer = qa_model.generate_answer(context=context, question=q)

    return {
        "query": q,
        "answer": answer,
        "sources": context_chunks[:top_k]
    }