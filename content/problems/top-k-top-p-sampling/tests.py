import math

from submission import *

NEG_INF = float("-inf")


def test_no_filtering_returns_the_same_values():
    logits = [1.0, 2.0, 3.0]
    out = filter_logits(logits)
    assert out == logits, f"expected {logits!r}, got {out!r}"


def test_does_not_mutate_input():
    logits = [1.0, 2.0, 3.0, 4.0]
    filter_logits(logits, top_k=1)
    exp = [1.0, 2.0, 3.0, 4.0]
    assert logits == exp, f"input was mutated: expected {exp!r}, got {logits!r}"


def test_top_k_keeps_the_highest():
    out = filter_logits([1.0, 2.0, 3.0, 4.0], top_k=2)
    exp = [NEG_INF, NEG_INF, 3.0, 4.0]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_top_k_larger_than_vocab_keeps_everything():
    logits = [1.0, 2.0]
    out = filter_logits(logits, top_k=10)
    assert out == logits, f"expected {logits!r}, got {out!r}"


def test_top_k_ties_break_toward_lower_index():
    out = filter_logits([5.0, 5.0, 5.0], top_k=2)
    exp = [5.0, 5.0, NEG_INF]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_top_p_on_a_uniform_distribution():
    out = filter_logits([0.0, 0.0, 0.0, 0.0], top_p=0.5)
    exp = [0.0, 0.0, NEG_INF, NEG_INF]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_top_p_nucleus_size():
    # softmax([2, 1, 0, -1]) is about [.644, .237, .087, .032]
    logits = [2.0, 1.0, 0.0, -1.0]
    kept = lambda p: sum(1 for v in filter_logits(logits, top_p=p) if v != NEG_INF)
    assert kept(0.6) == 1, f"top_p=0.6 should keep 1 token, kept {kept(0.6)}"
    assert kept(0.8) == 2, f"top_p=0.8 should keep 2 tokens, kept {kept(0.8)}"
    assert kept(0.95) == 3, f"top_p=0.95 should keep 3 tokens, kept {kept(0.95)}"


def test_top_p_always_keeps_at_least_one():
    out = filter_logits([10.0, 0.0, 0.0], top_p=0.01)
    kept = [v for v in out if v != NEG_INF]
    assert kept == [10.0], f"expected exactly the top token kept, got {out!r}"


def test_top_p_keeps_positions_not_sorted_order():
    out = filter_logits([0.0, 5.0, 0.0], top_p=0.5)
    exp = [NEG_INF, 5.0, NEG_INF]
    assert out == exp, f"the survivor must stay at index 1: expected {exp!r}, got {out!r}"


def test_top_k_then_top_p_renormalizes():
    # After top_k=2 only the two 5.0s survive; renormalized they are .5 each,
    # so top_p=0.5 keeps exactly one of them.
    out = filter_logits([5.0, 5.0, 0.0, 0.0], top_k=2, top_p=0.5)
    exp = [5.0, NEG_INF, NEG_INF, NEG_INF]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_survives_large_logits():
    out = filter_logits([900.0, 899.0, 100.0], top_p=0.9)
    assert all(not math.isnan(v) for v in out), f"overflowed to nan: {out!r}"
    assert out[0] == 900.0, f"the top logit must survive, got {out!r}"


def test_empty_logits():
    out = filter_logits([], top_k=5, top_p=0.9)
    assert out == [], f"expected [], got {out!r}"
