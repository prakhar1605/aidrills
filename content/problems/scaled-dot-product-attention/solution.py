import numpy as np


def attention(
    Q: np.ndarray,
    K: np.ndarray,
    V: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    d_k = Q.shape[-1]
    # swapaxes, not .T -- .T reverses every axis and breaks batched inputs.
    scores = np.matmul(Q, np.swapaxes(K, -1, -2)) / np.sqrt(d_k)

    if mask is not None:
        scores = np.where(mask, scores, -np.inf)

    # Stable softmax over the last axis.
    scores = scores - np.max(scores, axis=-1, keepdims=True)
    exp = np.exp(scores)
    weights = exp / np.sum(exp, axis=-1, keepdims=True)

    return np.matmul(weights, V), weights


def causal_mask(n: int) -> np.ndarray:
    return np.tril(np.ones((n, n), dtype=bool))


# What the interviewer is checking:
#   - the 1/sqrt(d_k) scaling and the variance argument behind it
#   - swapaxes(-1, -2) so leading batch/head axes survive
#   - masking with -inf *before* the softmax, not zeroing weights after it,
#     which would leave the rows un-normalized
#   - max-subtraction; note that a row whose max is -inf would produce nan, so
#     the contract requires at least one visible position per row
