from submission import *


def test_normalize_lowercases_and_strips_punctuation():
    out = normalize_answer("The Eiffel Tower!")
    exp = "eiffel tower"
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_normalize_collapses_whitespace():
    out = normalize_answer("  a   long\tanswer\n")
    exp = "long answer"
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_normalize_only_drops_standalone_articles():
    out = normalize_answer("Athens and Antwerp")
    exp = "athens and antwerp"
    assert out == exp, f"'a' inside a word must survive: expected {exp!r}, got {out!r}"


def test_exact_match_ignores_formatting():
    out = exact_match("The Eiffel Tower.", ["eiffel tower"])
    assert out == 1.0, f"expected 1.0, got {out!r}"


def test_exact_match_rejects_a_different_answer():
    out = exact_match("Big Ben", ["eiffel tower"])
    assert out == 0.0, f"expected 0.0, got {out!r}"


def test_exact_match_takes_the_best_gold():
    out = exact_match("Paris", ["London", "Paris", "Berlin"])
    assert out == 1.0, f"expected 1.0, got {out!r}"


def test_f1_is_one_for_an_exact_answer():
    out = f1_score("the quick brown fox", ["quick brown fox"])
    assert out == 1.0, f"expected 1.0, got {out!r}"


def test_f1_partial_overlap():
    # pred tokens: quick, brown, fox  |  gold tokens: quick, brown
    out = f1_score("the quick brown fox", ["the quick brown"])
    exp = 0.8
    assert abs(out - exp) < 1e-9, f"expected {exp!r}, got {out!r}"


def test_f1_counts_multiplicity_not_set_membership():
    # overlap is min(2, 1) + min(1, 1) = 2, not 2 distinct types out of 2
    out = f1_score("cat cat dog", ["cat dog"])
    exp = 0.8
    assert abs(out - exp) < 1e-9, f"expected {exp!r}, got {out!r}"


def test_f1_no_overlap():
    out = f1_score("completely different", ["eiffel tower"])
    assert out == 0.0, f"expected 0.0, got {out!r}"


def test_f1_empty_prediction():
    out = f1_score("", ["eiffel tower"])
    assert out == 0.0, f"expected 0.0, got {out!r}"


def test_f1_both_empty_is_a_match():
    out = f1_score("", [""])
    assert out == 1.0, f"expected 1.0, got {out!r}"


def test_f1_empty_gold_with_a_prediction():
    out = f1_score("something", [""])
    assert out == 0.0, f"expected 0.0, got {out!r}"


def test_f1_takes_the_max_over_golds():
    out = f1_score("eiffel tower", ["big ben", "eiffel tower", "louvre"])
    assert out == 1.0, f"expected 1.0, got {out!r}"


def test_f1_never_returns_nan():
    for pred, golds in [("", [""]), ("", ["x"]), ("x", [""]), ("a the", ["the a"])]:
        out = f1_score(pred, golds)
        assert out == out, f"f1_score({pred!r}, {golds!r}) returned nan"
        assert 0.0 <= out <= 1.0, f"f1_score({pred!r}, {golds!r}) = {out!r} is out of range"
