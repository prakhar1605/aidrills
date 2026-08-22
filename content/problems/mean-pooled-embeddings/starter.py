import numpy as np


def mean_pool(token_embeddings: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """Average token embeddings over the real tokens only.

    Args:
        token_embeddings: (batch, seq, dim).
        attention_mask: (batch, seq); 1 = token, 0 = padding.

    Returns:
        (batch, dim) pooled embeddings.
    """
    raise NotImplementedError


def normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize each row to unit length; zero rows stay zero."""
    raise NotImplementedError
