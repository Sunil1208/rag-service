from sentence_transformers import SentenceTransformer
from app.core.logger import get_logger

logger = get_logger()
_model_instance = None # Singleton instance

class EmbeddingGenerator:
    """
    Generates semantic embeddings using a local model from SentenceTransformers.
    Using this since it works offline without any cost or API key.
    Can be replced with openAi text-embedding-3-small or any other embedding model
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        global _model_instance
        if _model_instance is None:
            logger.info(f"Loading embedding model: {model_name}")
            _model_instance = SentenceTransformer(model_name)
        self.model = _model_instance
        self.model_name = model_name

        

    def generate(self, text: str) -> list[float]:
        """
        Generate a dummy embedding for the given text.
        Output is normalized for cosine similarity queries.
        """
        # Create a hash of the text to ensure consistent embeddings for the same input
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
        
    def generate_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.
        """
        if not texts:
            return []

        logger.info(f"Generating embeddings for {len(texts)} chunks (batch_size={batch_size})")
        try:
            embeddings = self.model.encode(texts, batch_size=batch_size, normalize_embeddings=True, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[] for _ in texts]