import numpy as np


def attention(
    Q: np.ndarray,
    K: np.ndarray,
    V: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Scaled dot-product attention.

    Args:
        Q: queries, shape (..., n_q, d_k).
        K: keys, shape (..., n_k, d_k).
        V: values, shape (..., n_k, d_v).
        mask: boolean, broadcastable to (..., n_q, n_k). False = do not attend.

    Returns:
        (output, weights) with shapes (..., n_q, d_v) and (..., n_q, n_k).
    """
    raise NotImplementedError


def causal_mask(n: int) -> np.ndarray:
    """A lower-triangular boolean mask: position i may attend to j <= i."""
    raise NotImplementedError
