from submission import *

# 0 and 1 are near-duplicates; 2 is unrelated and less relevant.
QUERY_SIM = [0.9, 0.85, 0.2]
DOC_SIM = [
    [1.0, 0.95, 0.1],
    [0.95, 1.0, 0.1],
    [0.1, 0.1, 1.0],
]


def test_first_pick_is_the_most_relevant():
    out = mmr(QUERY_SIM, DOC_SIM, k=1)
    assert out == [0], f"expected [0], got {out!r}"


def test_diversity_demotes_the_near_duplicate():
    out = mmr(QUERY_SIM, DOC_SIM, k=3, lambda_=0.5)
    exp = [0, 2, 1]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_lambda_one_is_pure_relevance():
    out = mmr(QUERY_SIM, DOC_SIM, k=3, lambda_=1.0)
    exp = [0, 1, 2]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_lambda_zero_still_seeds_with_relevance():
    out = mmr(QUERY_SIM, DOC_SIM, k=1, lambda_=0.0)
    assert out == [0], f"the first pick has nothing to diversify against: expected [0], got {out!r}"


def test_lambda_zero_then_maximizes_novelty():
    out = mmr(QUERY_SIM, DOC_SIM, k=2, lambda_=0.0)
    exp = [0, 2]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_penalty_uses_the_max_not_the_mean():
    # 2 is identical to the already-selected 0 but averages low against the set,
    # so a mean-based penalty would wrongly promote it over 1.
    query_sim = [1.0, 0.5, 0.5]
    doc_sim = [
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
    ]
    out = mmr(query_sim, doc_sim, k=2, lambda_=0.5)
    assert out == [0, 1], f"the max similarity must dominate the penalty: expected [0, 1], got {out!r}"


def test_k_truncates():
    out = mmr(QUERY_SIM, DOC_SIM, k=2)
    assert len(out) == 2, f"expected 2 results, got {out!r}"


def test_k_larger_than_the_corpus():
    out = mmr(QUERY_SIM, DOC_SIM, k=99)
    assert sorted(out) == [0, 1, 2], f"expected every index once, got {out!r}"


def test_k_zero_and_negative():
    assert mmr(QUERY_SIM, DOC_SIM, k=0) == [], "k=0 must return []"
    assert mmr(QUERY_SIM, DOC_SIM, k=-2) == [], "k<0 must return []"


def test_empty_corpus():
    out = mmr([], [], k=3)
    assert out == [], f"expected [], got {out!r}"


def test_no_duplicates():
    query_sim = [0.5] * 6
    doc_sim = [[1.0 if i == j else 0.3 for j in range(6)] for i in range(6)]
    out = mmr(query_sim, doc_sim, k=6)
    assert len(set(out)) == len(out) == 6, f"expected 6 distinct indices, got {out!r}"


def test_ties_break_toward_the_lower_index():
    query_sim = [0.5, 0.5, 0.5]
    doc_sim = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]
    out = mmr(query_sim, doc_sim, k=3)
    assert out == [0, 1, 2], f"expected [0, 1, 2], got {out!r}"


def test_bad_lambda_raises():
    for bad in (-0.1, 1.5):
        try:
            mmr(QUERY_SIM, DOC_SIM, k=2, lambda_=bad)
        except ValueError:
            continue
        raise AssertionError(f"lambda_={bad} must raise ValueError")


def test_malformed_matrix_raises():
    try:
        mmr([0.5, 0.5], [[1.0, 0.0]], k=1)
    except ValueError:
        return
    raise AssertionError("a doc_sim that is not n x n must raise ValueError")
