import textwrap

def chunk_text(text, max_chars: int = 500) -> list[str]:
    """
    Split text into smaller chunks of max_chars length
    Simple approximation, later we can do token-based chunking
    """
    clean_text = " ".join(text.split())
    chunks = textwrap.wrap(clean_text, width=max_chars)
    return chunks
