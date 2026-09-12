from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def compute_similarity_score(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using sentence embeddings.
    Returns a score between 0 and 1.
    """
    model = get_model()
    emb1 = model.encode([text1], convert_to_numpy=True)
    emb2 = model.encode([text2], convert_to_numpy=True)
    sim = cosine_similarity(emb1, emb2)[0][0]
    # Clip just in case
    sim = float(np.clip(sim, 0.0, 1.0))
    return sim