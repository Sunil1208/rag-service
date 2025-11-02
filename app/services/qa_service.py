from transformers import pipeline
from app.core.logger import get_logger

logger = get_logger()

_qa_model_instance = None  # Singleton instance

class QAGenerator:
    """
    Uses a small local instruction-tuned model (Flan-T5-Small)
    to generate answers based on provided context and questions.
    """

    def __init__(self, model_name: str = "google/flan-t5-small"):
        global _qa_model_instance
        if _qa_model_instance is None:
            logger.info(f"Loading QA model: {model_name}")
            _qa_model_instance = pipeline("text2text-generation", model=model_name)
        self.model_name = model_name
        self.generator = _qa_model_instance
        

    def generate_answer(self, context: str, question: str) -> str:
        """
        Build an instruction prompt and run generation
        """
        # prompt = (
        #     f"Answer the follwing questions using only the provided context.\n\n"
        #     f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        # )
        
        prompt = (
            "You are a helpful assistant that answers questions using only the provided context. "
            "Read the context carefully and provide a concise, factual answer. "
            "If the context does not contain enough information to answer, respond with "
            "'Not mentioned in the document.'\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\nAnswer:"
        )


        try:
            output = self.generator(prompt, max_new_tokens=128, temperature=0.3)
            return output[0]["generated_text"].strip()
        except Exception as e:
            logger.error(f"QA generation failed: {e}")
            return "Unable to generate answer at this time."