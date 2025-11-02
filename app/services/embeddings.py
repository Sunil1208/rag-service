from sentence_transformers import SentenceTransformer
from app.core.logger import get_logger

logger = get_logger()

class EmbeddingGenerator:
    """
    Generates semantic embeddings using a local model from SentenceTransformers.
    Using this since it works offline without any cost or API key.
    Can be replced with openAi text-embedding-3-small or any other embedding model
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
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