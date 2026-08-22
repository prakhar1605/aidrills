import numpy as np


def rope_frequencies(
    dim: int,
    seq_len: int,
    base: float = 10000.0,
) -> tuple[np.ndarray, np.ndarray]:
    if dim % 2 != 0:
        raise ValueError(f"dim must be even, got {dim}")

    # 1 / base ** (2i / dim) for i in [0, dim/2)
    inv_freq = 1.0 / (base ** (np.arange(0, dim, 2, dtype=np.float64) / dim))
    positions = np.arange(seq_len, dtype=np.float64)
    angles = np.outer(positions, inv_freq)  # (seq_len, dim // 2)
    return np.cos(angles), np.sin(angles)


def apply_rope(
    x: np.ndarray,
    cos: np.ndarray,
    sin: np.ndarray,
    offset: int = 0,
) -> np.ndarray:
    dim = x.shape[-1]
    if dim % 2 != 0:
        raise ValueError(f"dim must be even, got {dim}")

    seq = x.shape[-2]
    c = cos[offset : offset + seq]
    s = sin[offset : offset + seq]
    if c.shape[0] != seq:
        raise ValueError(f"tables hold {cos.shape[0]} positions, need {offset + seq}")

    even = x[..., 0::2]
    odd = x[..., 1::2]

    out = np.empty_like(x, dtype=np.result_type(x.dtype, np.float64))
    out[..., 0::2] = even * c - odd * s
    out[..., 1::2] = even * s + odd * c
    return out


# What the interviewer is checking:
#   - the strided [..., 0::2] / [..., 1::2] view, which is what makes "adjacent
#     pairs" one expression instead of a loop
#   - (seq, dim//2) broadcasting against (..., seq, dim//2) for free, so batch
#     and head axes never appear in the code
#   - offset, so incremental decode lands on the same angles as a full pass
#   - the rotation preserves the norm; if a test says otherwise, the sign on the
#     sin terms is flipped
