import math

from submission import *

BASIS = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]]


def test_identical_vector_scores_one():
    out = cosine_top_k([1.0, 0.0], BASIS, k=1)
    assert out[0][0] == 0, f"expected index 0, got {out!r}"
    assert math.isclose(out[0][1], 1.0), f"expected 1.0, got {out[0][1]!r}"


def test_orthogonal_scores_zero():
    out = cosine_top_k([1.0, 0.0], BASIS, k=3)
    by_index = dict(out)
    assert math.isclose(by_index[1], 0.0, abs_tol=1e-12), f"expected 0.0, got {by_index[1]!r}"


def test_opposite_scores_minus_one():
    out = cosine_top_k([1.0, 0.0], BASIS, k=3)
    by_index = dict(out)
    assert math.isclose(by_index[2], -1.0), f"expected -1.0, got {by_index[2]!r}"


def test_worked_example():
    out = cosine_top_k([1.0, 0.0], BASIS, k=2)
    assert [index for index, _ in out] == [0, 1], f"expected indices [0, 1], got {out!r}"


def test_magnitude_does_not_matter():
    short = cosine_top_k([1.0, 1.0], [[1.0, 1.0]], k=1)[0][1]
    long = cosine_top_k([1.0, 1.0], [[100.0, 100.0]], k=1)[0][1]
    assert math.isclose(short, long), f"cosine ignores magnitude: {short!r} vs {long!r}"


def test_results_are_sorted_descending():
    vectors = [[0.0, 1.0], [1.0, 1.0], [1.0, 0.0]]
    out = cosine_top_k([1.0, 0.0], vectors, k=3)
    scores = [score for _, score in out]
    assert scores == sorted(scores, reverse=True), f"expected descending, got {out!r}"


def test_ties_break_toward_the_lower_index():
    out = cosine_top_k([1.0, 0.0], [[1.0, 0.0], [2.0, 0.0], [3.0, 0.0]], k=2)
    assert [index for index, _ in out] == [0, 1], f"expected [0, 1], got {out!r}"


def test_zero_vector_scores_zero_not_nan():
    out = cosine_top_k([1.0, 0.0], [[0.0, 0.0]], k=1)
    score = out[0][1]
    assert not math.isnan(score), "a zero vector must not produce nan"
    assert score == 0.0, f"expected 0.0, got {score!r}"


def test_zero_query_scores_zero_not_nan():
    out = cosine_top_k([0.0, 0.0], BASIS, k=3)
    for index, score in out:
        assert not math.isnan(score), f"index {index} produced nan for a zero query"
        assert score == 0.0, f"expected 0.0 at index {index}, got {score!r}"


def test_k_larger_than_the_corpus():
    out = cosine_top_k([1.0, 0.0], BASIS, k=99)
    assert len(out) == 3, f"expected all 3, got {out!r}"


def test_k_zero_and_negative():
    assert cosine_top_k([1.0, 0.0], BASIS, k=0) == [], "k=0 must return []"
    assert cosine_top_k([1.0, 0.0], BASIS, k=-1) == [], "k<0 must return []"


def test_empty_corpus():
    out = cosine_top_k([1.0, 0.0], [], k=3)
    assert out == [], f"expected [], got {out!r}"


def test_dimension_mismatch_raises():
    try:
        cosine_top_k([1.0, 0.0], [[1.0, 0.0], [1.0, 0.0, 0.0]], k=2)
    except ValueError:
        return
    raise AssertionError("a vector of the wrong length must raise ValueError")


def test_similarity_stays_in_range():
    vectors = [[3.0, -4.0], [-1.0, 2.0], [0.0, 0.0], [7.0, 7.0]]
    for _, score in cosine_top_k([1.0, 2.0], vectors, k=4):
        assert -1.0 - 1e-9 <= score <= 1.0 + 1e-9, f"{score!r} is outside [-1, 1]"
