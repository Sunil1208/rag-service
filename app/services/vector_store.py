import chromadb
from app.core.logger import get_logger

logger = get_logger()

class VectorStore:
    """
    Wrapper around ChromaDB vector store for storing and retrieving embeddings.
    """

    def __init__(self, collection_name: str = "documents"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadata: list[dict]):
        """
        Add vectors and metadata
        """
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadata
        )
        logger.info(f"Added {len(ids)} vectors to collection '{self.collection.name}'")


    def query_similar(self, query_embedding: list[float], top_k: int = 3):
        """
        Retrieve top-K most similar chunks
        """
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results