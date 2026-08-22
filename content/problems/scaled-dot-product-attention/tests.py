import numpy as np

from submission import *


def test_uniform_scores_average_the_values():
    Q = np.zeros((1, 4))
    K = np.zeros((3, 4))
    V = np.array([[1.0, 0.0], [3.0, 0.0], [5.0, 0.0]])
    out, w = attention(Q, K, V)
    assert np.allclose(w, 1 / 3), f"expected uniform weights, got {w!r}"
    assert np.allclose(out, [[3.0, 0.0]]), f"expected the mean of V, got {out!r}"


def test_weights_sum_to_one():
    rng = np.random.default_rng(0)
    Q, K, V = rng.normal(size=(5, 8)), rng.normal(size=(7, 8)), rng.normal(size=(7, 3))
    _, w = attention(Q, K, V)
    sums = w.sum(axis=-1)
    assert np.allclose(sums, 1.0), f"rows must sum to 1, got {sums!r}"


def test_output_and_weight_shapes():
    rng = np.random.default_rng(1)
    Q, K, V = rng.normal(size=(5, 8)), rng.normal(size=(7, 8)), rng.normal(size=(7, 3))
    out, w = attention(Q, K, V)
    assert out.shape == (5, 3), f"expected output (5, 3), got {out.shape}"
    assert w.shape == (5, 7), f"expected weights (5, 7), got {w.shape}"


def test_batched_and_multi_head_shapes():
    rng = np.random.default_rng(2)
    Q = rng.normal(size=(2, 4, 6, 16))  # batch 2, 4 heads, 6 queries, d_k 16
    K = rng.normal(size=(2, 4, 9, 16))
    V = rng.normal(size=(2, 4, 9, 5))
    out, w = attention(Q, K, V)
    assert out.shape == (2, 4, 6, 5), f"expected (2, 4, 6, 5), got {out.shape}"
    assert w.shape == (2, 4, 6, 9), f"expected (2, 4, 6, 9), got {w.shape}"
    assert np.allclose(w.sum(axis=-1), 1.0), "batched rows must still sum to 1"


def test_scaling_by_sqrt_dk():
    # One query aligned with the first key. The peak weight depends on d_k only
    # through the 1/sqrt(d_k) factor, so an unscaled implementation misses it.
    d_k = 4
    Q = np.array([[1.0] + [0.0] * (d_k - 1)])
    K = np.eye(d_k)
    V = np.eye(d_k)
    _, w = attention(Q, K, V)
    scaled = np.exp(1 / np.sqrt(d_k))
    exp = scaled / (scaled + (d_k - 1))
    assert np.isclose(w[0, 0], exp), f"expected top weight {exp!r}, got {w[0, 0]!r}"


def test_mask_blocks_attention():
    Q = np.zeros((1, 2))
    K = np.zeros((3, 2))
    V = np.array([[1.0], [2.0], [3.0]])
    mask = np.array([[True, False, False]])
    out, w = attention(Q, K, V, mask)
    assert np.allclose(w, [[1.0, 0.0, 0.0]]), f"expected all mass on index 0, got {w!r}"
    assert np.allclose(out, [[1.0]]), f"expected [[1.0]], got {out!r}"


def test_masked_rows_still_normalize():
    rng = np.random.default_rng(3)
    Q, K, V = rng.normal(size=(4, 8)), rng.normal(size=(4, 8)), rng.normal(size=(4, 2))
    out, w = attention(Q, K, V, causal_mask(4))
    assert np.allclose(w.sum(axis=-1), 1.0), f"masked rows must sum to 1, got {w.sum(axis=-1)!r}"
    assert np.allclose(out[0], V[0]), f"row 0 sees only V[0], expected {V[0]!r}, got {out[0]!r}"


def test_causal_mask_is_lower_triangular():
    m = causal_mask(3)
    exp = np.array([[1, 0, 0], [1, 1, 0], [1, 1, 1]], dtype=bool)
    assert m.dtype == np.bool_, f"expected a boolean mask, got dtype {m.dtype}"
    assert np.array_equal(m, exp), f"expected {exp!r}, got {m!r}"


def test_causal_mask_hides_the_future():
    rng = np.random.default_rng(4)
    Q, K, V = rng.normal(size=(5, 8)), rng.normal(size=(5, 8)), rng.normal(size=(5, 3))
    _, w = attention(Q, K, V, causal_mask(5))
    upper = np.triu(w, k=1)
    assert np.allclose(upper, 0.0), f"future positions must get zero weight, got {upper!r}"


def test_numerically_stable_on_large_scores():
    Q = np.array([[1000.0, 0.0]])
    K = np.array([[1000.0, 0.0], [0.0, 1000.0]])
    V = np.array([[1.0], [2.0]])
    out, w = attention(Q, K, V)
    assert not np.isnan(w).any(), f"softmax overflowed to nan: {w!r}"
    assert np.allclose(out, [[1.0]]), f"expected [[1.0]], got {out!r}"


def test_inputs_are_not_mutated():
    Q, K, V = np.zeros((2, 3)), np.ones((2, 3)), np.ones((2, 4))
    before = (Q.copy(), K.copy(), V.copy())
    attention(Q, K, V)
    for name, now, then in zip("QKV", (Q, K, V), before):
        assert np.array_equal(now, then), f"{name} was mutated"
