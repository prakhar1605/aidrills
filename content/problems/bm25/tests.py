import math

from submission import *

CORPUS = [
    ["the", "cat", "sat", "on", "the", "mat"],
    ["the", "dog", "sat", "on", "the", "log"],
    ["quantum", "entanglement", "explained"],
    ["the", "cat", "chased", "the", "cat"],
]


def test_empty_corpus():
    out = bm25_scores([], ["cat"])
    assert out == [], f"expected [], got {out!r}"


def test_empty_query_scores_zero():
    out = bm25_scores(CORPUS, [])
    exp = [0.0] * len(CORPUS)
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_one_score_per_document():
    out = bm25_scores(CORPUS, ["cat"])
    assert len(out) == len(CORPUS), f"expected {len(CORPUS)} scores, got {len(out)}"


def test_unmatched_documents_score_zero():
    out = bm25_scores(CORPUS, ["cat"])
    assert out[1] == 0.0, f"doc 1 has no 'cat' so it must score 0.0, got {out[1]!r}"
    assert out[2] == 0.0, f"doc 2 has no 'cat' so it must score 0.0, got {out[2]!r}"


def test_unknown_term_scores_zero_everywhere():
    out = bm25_scores(CORPUS, ["zzzz"])
    exp = [0.0] * len(CORPUS)
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_more_occurrences_ranks_higher():
    out = bm25_scores(CORPUS, ["cat"])
    assert out[3] > out[0], f"doc 3 mentions 'cat' twice in a shorter doc, so {out[3]!r} should beat {out[0]!r}"


def test_rare_term_beats_common_term():
    rare = bm25_scores(CORPUS, ["quantum"])[2]
    common = bm25_scores(CORPUS, ["the"])[0]
    assert rare > common, f"a term in 1 of 4 docs ({rare!r}) must outweigh one in 3 of 4 ({common!r})"


def test_k1_zero_makes_term_frequency_binary():
    # With k1=0 the saturation factor collapses to 1, so the score is just the
    # sum of idf over matched terms -- independent of how often they occur.
    out = bm25_scores(CORPUS, ["cat"], k1=0.0)
    assert math.isclose(out[0], out[3], rel_tol=1e-9), (
        f"k1=0 must ignore term frequency: {out[0]!r} vs {out[3]!r}"
    )
    n, df = 4, 2
    exp = math.log(1 + (n - df + 0.5) / (df + 0.5))
    assert math.isclose(out[0], exp, rel_tol=1e-9), f"expected idf {exp!r}, got {out[0]!r}"


def test_b_zero_disables_length_normalization():
    short = ["error", "code"]
    long_doc = ["error", "code"] + ["filler"] * 50
    corpus = [short, long_doc]
    with_norm = bm25_scores(corpus, ["error"], b=0.75)
    without = bm25_scores(corpus, ["error"], b=0.0)
    assert with_norm[0] > with_norm[1], "with b=0.75 the short doc must win"
    assert math.isclose(without[0], without[1], rel_tol=1e-9), (
        f"with b=0.0 both docs must score the same, got {without!r}"
    )


def test_repeated_query_terms_count_twice():
    once = bm25_scores(CORPUS, ["cat"])[0]
    twice = bm25_scores(CORPUS, ["cat", "cat"])[0]
    assert math.isclose(twice, 2 * once, rel_tol=1e-9), (
        f"expected {2 * once!r} for a doubled query term, got {twice!r}"
    )


def test_handles_empty_documents():
    out = bm25_scores([[], []], ["cat"])
    exp = [0.0, 0.0]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_multi_term_query_sums_contributions():
    both = bm25_scores(CORPUS, ["cat", "mat"])[0]
    cat = bm25_scores(CORPUS, ["cat"])[0]
    mat = bm25_scores(CORPUS, ["mat"])[0]
    assert math.isclose(both, cat + mat, rel_tol=1e-9), (
        f"expected {cat + mat!r}, got {both!r}"
    )
