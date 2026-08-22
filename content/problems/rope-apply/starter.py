import numpy as np


def rope_frequencies(
    dim: int,
    seq_len: int,
    base: float = 10000.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Precompute the rotation tables.

    Args:
        dim: head dimension; must be even.
        seq_len: how many positions to tabulate.
        base: the frequency base, 10000 in the paper.

    Returns:
        (cos, sin), each of shape (seq_len, dim // 2).

    Raises:
        ValueError: if dim is odd.
    """
    raise NotImplementedError


def apply_rope(
    x: np.ndarray,
    cos: np.ndarray,
    sin: np.ndarray,
    offset: int = 0,
) -> np.ndarray:
    """Rotate `x` in adjacent pairs by the tabulated angles.

    Args:
        x: (..., seq, dim).
        cos: (positions, dim // 2).
        sin: (positions, dim // 2).
        offset: absolute position of x[..., 0, :].

    Returns:
        An array shaped like `x`.
    """
    raise NotImplementedError
