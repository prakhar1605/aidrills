import numpy as np

from submission import *


def reference_attention(q, keys, values):
    """A full attention pass, for comparison against incremental decoding."""
    scores = keys @ q / np.sqrt(q.shape[-1])
    scores = scores - scores.max()
    weights = np.exp(scores)
    return (weights / weights.sum()) @ values


def test_starts_empty():
    cache = KVCache()
    assert len(cache) == 0, f"expected 0, got {len(cache)}"
    assert cache.keys.shape[0] == 0, f"expected no cached keys, got {cache.keys.shape!r}"


def test_append_grows_the_cache():
    cache = KVCache()
    cache.append(np.ones((1, 4)), np.ones((1, 4)))
    assert len(cache) == 1, f"expected 1, got {len(cache)}"
    cache.append(np.ones((3, 4)), np.ones((3, 4)))
    assert len(cache) == 4, f"expected 4, got {len(cache)}"


def test_cached_rows_keep_their_order():
    cache = KVCache()
    for i in range(3):
        cache.append(np.full((1, 2), float(i)), np.full((1, 2), float(-i)))
    exp = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
    assert np.allclose(cache.keys, exp), f"expected {exp!r}, got {cache.keys!r}"


def test_keys_and_values_stay_aligned():
    cache = KVCache()
    for i in range(4):
        cache.append(np.full((1, 2), float(i)), np.full((1, 2), float(i * 10)))
    assert np.allclose(cache.values, cache.keys * 10), (
        f"values drifted from keys: {cache.keys!r} vs {cache.values!r}"
    )


def test_append_copies_the_caller_buffer():
    cache = KVCache()
    buffer = np.ones((1, 3))
    cache.append(buffer, buffer)
    buffer[:] = 99.0  # a real decoder reuses this buffer every step
    assert np.allclose(cache.keys, 1.0), (
        f"the cache must not alias the caller's array, got {cache.keys!r}"
    )


def test_window_evicts_the_oldest():
    cache = KVCache(max_len=3)
    for i in range(5):
        cache.append(np.full((1, 2), float(i)), np.full((1, 2), float(i)))
    assert len(cache) == 3, f"expected 3, got {len(cache)}"
    exp = np.array([[2.0, 2.0], [3.0, 3.0], [4.0, 4.0]])
    assert np.allclose(cache.keys, exp), f"the window must keep the newest: expected {exp!r}, got {cache.keys!r}"


def test_window_handles_a_batch_larger_than_itself():
    cache = KVCache(max_len=2)
    k = np.arange(5, dtype=float).reshape(5, 1)
    cache.append(k, k)
    assert len(cache) == 2, f"expected 2, got {len(cache)}"
    assert np.allclose(cache.keys, [[3.0], [4.0]]), f"expected the last two rows, got {cache.keys!r}"


def test_unbounded_cache_keeps_everything():
    cache = KVCache()
    for _ in range(50):
        cache.append(np.ones((1, 2)), np.ones((1, 2)))
    assert len(cache) == 50, f"expected 50, got {len(cache)}"


def test_reset_empties_the_cache():
    cache = KVCache()
    cache.append(np.ones((2, 2)), np.ones((2, 2)))
    cache.reset()
    assert len(cache) == 0, f"expected 0 after reset, got {len(cache)}"


def test_decode_step_output_shape():
    cache = KVCache()
    q = np.ones(4)
    out = decode_step(q, np.ones((1, 4)), np.ones((1, 6)), cache)
    assert out.shape == (6,), f"expected (6,), got {out.shape}"


def test_single_cached_token_returns_that_value():
    cache = KVCache()
    out = decode_step(np.ones(3), np.ones((1, 3)), np.array([[7.0, 8.0]]), cache)
    exp = np.array([7.0, 8.0])
    assert np.allclose(out, exp), f"expected {exp!r}, got {out!r}"


def test_the_new_token_attends_to_itself():
    cache = KVCache()
    assert len(cache) == 0, "setup: the cache starts empty"
    decode_step(np.ones(3), np.ones((1, 3)), np.ones((1, 3)), cache)
    assert len(cache) == 1, "decode_step must append before attending"


def test_incremental_decoding_matches_a_full_pass():
    dim, seq = 8, 6
    rng = np.random.default_rng(0)
    K = rng.normal(size=(seq, dim))
    V = rng.normal(size=(seq, dim))
    q = rng.normal(size=dim)

    cache = KVCache()
    out = None
    for t in range(seq):
        out = decode_step(q, K[t : t + 1], V[t : t + 1], cache)

    exp = reference_attention(q, K, V)
    assert np.allclose(out, exp), (
        f"the last step must equal attention over the whole prefix: expected {exp!r}, got {out!r}"
    )


def test_every_step_matches_its_own_prefix():
    dim, seq = 4, 5
    rng = np.random.default_rng(1)
    K = rng.normal(size=(seq, dim))
    V = rng.normal(size=(seq, dim))
    q = rng.normal(size=dim)

    cache = KVCache()
    for t in range(seq):
        out = decode_step(q, K[t : t + 1], V[t : t + 1], cache)
        exp = reference_attention(q, K[: t + 1], V[: t + 1])
        assert np.allclose(out, exp), f"step {t} diverged: expected {exp!r}, got {out!r}"


def test_windowed_decode_only_sees_the_window():
    dim, seq, window = 4, 6, 3
    rng = np.random.default_rng(2)
    K = rng.normal(size=(seq, dim))
    V = rng.normal(size=(seq, dim))
    q = rng.normal(size=dim)

    cache = KVCache(max_len=window)
    out = None
    for t in range(seq):
        out = decode_step(q, K[t : t + 1], V[t : t + 1], cache)

    exp = reference_attention(q, K[-window:], V[-window:])
    assert np.allclose(out, exp), f"expected attention over the last {window} only, got {out!r}"


def test_survives_large_scores():
    cache = KVCache()
    q = np.full(4, 100.0)
    out = decode_step(q, np.full((2, 4), 100.0), np.ones((2, 3)), cache)
    assert not np.isnan(out).any(), f"softmax overflowed to nan: {out!r}"
