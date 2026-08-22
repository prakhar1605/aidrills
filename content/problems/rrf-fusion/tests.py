from submission import *


def test_worked_example():
    out = rrf_fuse([["a", "b", "c"], ["c", "a", "d"]], k=1)
    exp = ["a", "c", "b", "d"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_no_rankings():
    out = rrf_fuse([])
    assert out == [], f"expected [], got {out!r}"


def test_only_empty_rankings():
    out = rrf_fuse([[], []])
    assert out == [], f"expected [], got {out!r}"


def test_single_ranking_is_preserved():
    out = rrf_fuse([["x", "y", "z"]])
    exp = ["x", "y", "z"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_agreement_beats_a_single_top_hit():
    # "b" is second in both lists; "a" and "c" are first in one and absent
    # from the other. With a large k, consistency wins.
    out = rrf_fuse([["a", "b"], ["c", "b"]], k=60)
    assert out[0] == "b", f"expected 'b' to fuse first, got {out!r}"


def test_small_k_lets_a_single_first_place_dominate():
    out = rrf_fuse([["a", "b"], ["c", "b"]], k=0)
    # a: 1/1, c: 1/1, b: 1/2 + 1/2 = 1.0 -- three-way tie broken by best rank
    # (a and c reached rank 1, b only rank 2) then by id.
    exp = ["a", "c", "b"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_duplicate_inside_one_ranking_counts_once():
    dup = rrf_fuse([["a", "a", "b"]], k=1)
    plain = rrf_fuse([["a", "b"]], k=1)
    assert dup == plain, f"duplicates must not change the order: {dup!r} vs {plain!r}"


def test_top_n_truncates():
    out = rrf_fuse([["a", "b", "c", "d"]], top_n=2)
    exp = ["a", "b"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_top_n_larger_than_result():
    out = rrf_fuse([["a", "b"]], top_n=10)
    exp = ["a", "b"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_ties_are_deterministic():
    a = rrf_fuse([["x", "y"], ["y", "x"]])
    b = rrf_fuse([["y", "x"], ["x", "y"]])
    assert a == b == ["x", "y"], f"expected ['x', 'y'] both ways, got {a!r} and {b!r}"


def test_every_id_appears_exactly_once():
    out = rrf_fuse([["a", "b", "c"], ["b", "c", "d"], ["d", "e"]])
    assert sorted(out) == ["a", "b", "c", "d", "e"], f"expected each id once, got {out!r}"


def test_ranks_are_one_indexed():
    # If ranks were 0-indexed, k=0 would divide by zero on the top hit.
    out = rrf_fuse([["a", "b"]], k=0)
    exp = ["a", "b"]
    assert out == exp, f"expected {exp!r}, got {out!r}"
