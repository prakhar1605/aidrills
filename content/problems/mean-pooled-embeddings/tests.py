import numpy as np

from submission import *


def test_all_ones_mask_is_a_plain_mean():
    emb = np.array([[[1.0, 2.0], [3.0, 4.0]]])
    mask = np.ones((1, 2))
    out = mean_pool(emb, mask)
    exp = np.array([[2.0, 3.0]])
    assert np.allclose(out, exp), f"expected {exp!r}, got {out!r}"


def test_padding_is_excluded():
    emb = np.array([[[1.0, 1.0], [3.0, 3.0], [99.0, 99.0]]])
    mask = np.array([[1, 1, 0]])
    out = mean_pool(emb, mask)
    exp = np.array([[2.0, 2.0]])
    assert np.allclose(out, exp), f"the padded token must not count: expected {exp!r}, got {out!r}"


def test_different_lengths_in_one_batch():
    emb = np.array(
        [
            [[1.0], [3.0], [0.0]],
            [[2.0], [4.0], [6.0]],
        ]
    )
    mask = np.array([[1, 1, 0], [1, 1, 1]])
    out = mean_pool(emb, mask)
    exp = np.array([[2.0], [4.0]])
    assert np.allclose(out, exp), f"expected {exp!r}, got {out!r}"


def test_output_shape():
    emb = np.zeros((4, 7, 16))
    mask = np.ones((4, 7))
    assert mean_pool(emb, mask).shape == (4, 16), f"expected (4, 16), got {mean_pool(emb, mask).shape}"


def test_fully_padded_row_is_zero_not_nan():
    emb = np.array([[[5.0, 5.0], [7.0, 7.0]]])
    mask = np.zeros((1, 2))
    out = mean_pool(emb, mask)
    assert not np.isnan(out).any(), f"a fully padded row must not produce nan, got {out!r}"
    assert np.allclose(out, 0.0), f"expected zeros, got {out!r}"


def test_float_mask_works():
    emb = np.array([[[1.0], [3.0]]])
    out = mean_pool(emb, np.array([[1.0, 0.0]]))
    exp = np.array([[1.0]])
    assert np.allclose(out, exp), f"expected {exp!r}, got {out!r}"


def test_mean_pool_does_not_mutate_inputs():
    emb = np.array([[[1.0, 2.0], [3.0, 4.0]]])
    mask = np.array([[1, 0]])
    before_emb, before_mask = emb.copy(), mask.copy()
    mean_pool(emb, mask)
    assert np.array_equal(emb, before_emb), "token_embeddings was mutated"
    assert np.array_equal(mask, before_mask), "attention_mask was mutated"


def test_normalize_gives_unit_rows():
    vectors = np.array([[3.0, 4.0], [1.0, 0.0], [-1.0, -1.0]])
    out = normalize(vectors)
    norms = np.linalg.norm(out, axis=-1)
    assert np.allclose(norms, 1.0), f"expected unit norms, got {norms!r}"


def test_normalize_keeps_direction():
    out = normalize(np.array([[3.0, 4.0]]))
    exp = np.array([[0.6, 0.8]])
    assert np.allclose(out, exp), f"expected {exp!r}, got {out!r}"


def test_normalize_zero_row_stays_zero():
    out = normalize(np.array([[0.0, 0.0], [3.0, 4.0]]))
    assert not np.isnan(out).any(), f"a zero row must not produce nan, got {out!r}"
    assert np.allclose(out[0], 0.0), f"expected zeros, got {out[0]!r}"
    assert np.allclose(out[1], [0.6, 0.8]), f"the other rows must still normalize, got {out[1]!r}"


def test_normalize_does_not_mutate_input():
    vectors = np.array([[3.0, 4.0]])
    before = vectors.copy()
    normalize(vectors)
    assert np.array_equal(vectors, before), "vectors was mutated"


def test_pool_then_normalize_is_the_usual_pipeline():
    rng = np.random.default_rng(0)
    emb = rng.normal(size=(3, 5, 8))
    mask = np.array([[1, 1, 1, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0]])
    out = normalize(mean_pool(emb, mask))
    assert out.shape == (3, 8), f"expected (3, 8), got {out.shape}"
    assert np.allclose(np.linalg.norm(out, axis=-1), 1.0), "every row must end up on the unit sphere"
