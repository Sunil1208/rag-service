import os
import chromadb
from app.core.logger import get_logger

logger = get_logger()
_vector_store_instance = None  # Singleton instance

class VectorStore:
    """
    Wrapper around ChromaDB vector store for storing and retrieving embeddings.
    """

    def __init__(self, collection_name: str = "documents", persist_path: str = "data/chromadb"):
        global _vector_store_instance
        if _vector_store_instance is not None:
            self.client = _vector_store_instance.client
            self.collection = _vector_store_instance.collection
            return
        # Ensure the persistent directory exists
        os.makedirs(persist_path, exist_ok=True)
        
        # Initialize ChromaDB client and collection
        self.client = chromadb.PersistentClient(path=persist_path)

        # create or load the existing collection
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # log on startup
        try:
            count = self.collection.count()
            logger.info(f"ChromaDB collection '{collection_name}' loaded with {count} vectors.")
        except Exception as e:
            logger.error(f"Error loading ChromaDB collection '{collection_name}': {e}")

        _vector_store_instance = self

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