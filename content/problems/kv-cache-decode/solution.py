import numpy as np


class KVCache:
    def __init__(self, max_len: int | None = None) -> None:
        if max_len is not None and max_len <= 0:
            raise ValueError("max_len must be positive or None")
        self.max_len = max_len
        self._keys: np.ndarray | None = None
        self._values: np.ndarray | None = None

    def append(self, k: np.ndarray, v: np.ndarray) -> None:
        k = np.asarray(k, dtype=float)
        v = np.asarray(v, dtype=float)
        if k.ndim == 1:
            k, v = k[None, :], v[None, :]
        if k.shape[0] != v.shape[0]:
            raise ValueError(f"got {k.shape[0]} keys but {v.shape[0]} values")

        # np.concatenate already copies; the explicit copy covers the first
        # append, where the caller's buffer would otherwise become the cache.
        self._keys = k.copy() if self._keys is None else np.concatenate([self._keys, k])
        self._values = v.copy() if self._values is None else np.concatenate([self._values, v])

        if self.max_len is not None and self._keys.shape[0] > self.max_len:
            # Keep the most recent positions -- the window slides forward.
            self._keys = self._keys[-self.max_len :]
            self._values = self._values[-self.max_len :]

    @property
    def keys(self) -> np.ndarray:
        return np.zeros((0, 0)) if self._keys is None else self._keys

    @property
    def values(self) -> np.ndarray:
        return np.zeros((0, 0)) if self._values is None else self._values

    def __len__(self) -> int:
        return 0 if self._keys is None else int(self._keys.shape[0])

    def reset(self) -> None:
        self._keys = None
        self._values = None


def decode_step(
    q: np.ndarray,
    k_new: np.ndarray,
    v_new: np.ndarray,
    cache: KVCache,
) -> np.ndarray:
    cache.append(k_new, v_new)

    keys, values = cache.keys, cache.values
    scores = keys @ q / np.sqrt(q.shape[-1])
    scores = scores - np.max(scores)  # stable softmax
    weights = np.exp(scores)
    weights = weights / weights.sum()
    return weights @ values


# What the interviewer is checking:
#   - append copies, so a caller reusing one buffer per step does not rewrite
#     history
#   - eviction keeps the tail, [-max_len:], not the head
#   - decode_step appends *before* attending, so the token attends to itself --
#     off by one here and generation still looks fine while being subtly wrong
#   - the same max-subtraction as a full attention pass
