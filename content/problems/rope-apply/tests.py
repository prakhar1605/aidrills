import numpy as np

from submission import *


def test_frequency_table_shapes():
    cos, sin = rope_frequencies(8, 5)
    assert cos.shape == (5, 4), f"expected (5, 4), got {cos.shape}"
    assert sin.shape == (5, 4), f"expected (5, 4), got {sin.shape}"


def test_position_zero_is_identity():
    cos, sin = rope_frequencies(4, 3)
    assert np.allclose(cos[0], 1.0), f"cos at position 0 must be 1, got {cos[0]!r}"
    assert np.allclose(sin[0], 0.0), f"sin at position 0 must be 0, got {sin[0]!r}"

    x = np.arange(4, dtype=float).reshape(1, 4)
    out = apply_rope(x, cos, sin)
    assert np.allclose(out, x), f"position 0 must leave x unchanged: expected {x!r}, got {out!r}"


def test_first_pair_rotates_by_one_radian_per_step():
    # The i=0 frequency is base ** 0 == 1, so position m rotates by m radians.
    cos, sin = rope_frequencies(2, 4)
    x = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
    out = apply_rope(x, cos, sin)
    exp = np.stack([np.cos(np.arange(4.0)), np.sin(np.arange(4.0))], axis=-1)
    assert np.allclose(out, exp), f"expected {exp!r}, got {out!r}"


def test_shape_is_preserved():
    cos, sin = rope_frequencies(16, 10)
    x = np.random.default_rng(0).normal(size=(2, 4, 10, 16))
    out = apply_rope(x, cos, sin)
    assert out.shape == x.shape, f"expected {x.shape}, got {out.shape}"


def test_norm_is_preserved():
    cos, sin = rope_frequencies(8, 6)
    x = np.random.default_rng(1).normal(size=(3, 6, 8))
    out = apply_rope(x, cos, sin)
    before = np.linalg.norm(x, axis=-1)
    after = np.linalg.norm(out, axis=-1)
    assert np.allclose(before, after), "a rotation must preserve the norm -- check the signs"


def test_dot_product_depends_only_on_relative_position():
    dim, seq = 8, 10
    rng = np.random.default_rng(2)
    q = rng.normal(size=dim)
    k = rng.normal(size=dim)
    cos, sin = rope_frequencies(dim, seq)

    Q = apply_rope(np.tile(q, (seq, 1)), cos, sin)
    K = apply_rope(np.tile(k, (seq, 1)), cos, sin)

    for m, n in [(0, 0), (1, 3), (4, 6), (2, 7)]:
        base = float(Q[m] @ K[n])
        shifted = float(Q[m + 1] @ K[n + 1])
        assert np.isclose(base, shifted), (
            f"positions ({m}, {n}) and ({m + 1}, {n + 1}) share a delta but scored "
            f"{base!r} and {shifted!r}"
        )


def test_offset_matches_a_full_pass():
    dim, seq = 8, 12
    cos, sin = rope_frequencies(dim, seq)
    x = np.random.default_rng(3).normal(size=(seq, dim))

    full = apply_rope(x, cos, sin)
    for position in (0, 1, 7, 11):
        step = apply_rope(x[position : position + 1], cos, sin, offset=position)
        assert np.allclose(step, full[position : position + 1]), (
            f"decoding one token at position {position} must match the full pass"
        )


def test_offset_on_a_chunk():
    dim, seq = 4, 9
    cos, sin = rope_frequencies(dim, seq)
    x = np.random.default_rng(4).normal(size=(seq, dim))
    full = apply_rope(x, cos, sin)
    chunk = apply_rope(x[4:7], cos, sin, offset=4)
    assert np.allclose(chunk, full[4:7]), "a mid-sequence chunk must match the full pass"


def test_base_changes_the_frequencies():
    small, _ = rope_frequencies(8, 4, base=100.0)
    large, _ = rope_frequencies(8, 4, base=1000000.0)
    assert not np.allclose(small, large), "the base must affect the angles"


def test_odd_dim_raises():
    try:
        rope_frequencies(7, 4)
    except ValueError:
        return
    raise AssertionError("an odd dim must raise ValueError")


def test_input_is_not_mutated():
    cos, sin = rope_frequencies(4, 3)
    x = np.arange(12, dtype=float).reshape(3, 4)
    before = x.copy()
    apply_rope(x, cos, sin)
    assert np.array_equal(x, before), "x was mutated"
