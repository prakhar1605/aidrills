import numpy as np


class KVCache:
    """Keys and values for every position decoded so far."""

    def __init__(self, max_len: int | None = None) -> None:
        raise NotImplementedError

    def append(self, k: np.ndarray, v: np.ndarray) -> None:
        """Add (n_new, dim) keys and values, evicting the oldest if bounded."""
        raise NotImplementedError

    @property
    def keys(self) -> np.ndarray:
        raise NotImplementedError

    @property
    def values(self) -> np.ndarray:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError


def decode_step(
    q: np.ndarray,
    k_new: np.ndarray,
    v_new: np.ndarray,
    cache: KVCache,
) -> np.ndarray:
    """Cache the new key/value, then attend one query over the whole cache.

    Args:
        q: (dim,) query for the token being decoded.
        k_new: (n_new, dim) keys to cache first.
        v_new: (n_new, dim_v) values to cache first.
        cache: the KV cache, mutated in place.

    Returns:
        (dim_v,) attention output.
    """
    raise NotImplementedError
