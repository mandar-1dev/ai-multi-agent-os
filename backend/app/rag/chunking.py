def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """
    Simple sliding-window chunker on whitespace-normalized text.
    chunk_size / overlap are in characters (works well enough without a
    tokenizer dependency; swap for a tiktoken-based splitter if needed).
    """
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
