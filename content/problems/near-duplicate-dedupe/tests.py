from submission import *


def test_shingle_count():
    out = shingles("abcdefg", n=3)
    exp = {"abc", "bcd", "cde", "def", "efg"}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_shingles_normalize_case_and_whitespace():
    a = shingles("Hello   World", n=4)
    b = shingles("hello world", n=4)
    assert a == b, f"normalization failed: {a!r} vs {b!r}"


def test_short_text_is_one_shingle():
    out = shingles("abc", n=5)
    assert out == {"abc"}, f"expected the whole string, got {out!r}"


def test_empty_text_has_no_shingles():
    assert shingles("", n=3) == set(), "empty text must give an empty set"
    assert shingles("   ", n=3) == set(), "whitespace-only text must give an empty set"


def test_jaccard_identical():
    out = jaccard({"a", "b"}, {"a", "b"})
    assert out == 1.0, f"expected 1.0, got {out!r}"


def test_jaccard_disjoint():
    out = jaccard({"a"}, {"b"})
    assert out == 0.0, f"expected 0.0, got {out!r}"


def test_jaccard_partial():
    out = jaccard({"a", "b", "c"}, {"b", "c", "d"})
    exp = 0.5
    assert abs(out - exp) < 1e-12, f"expected {exp!r}, got {out!r}"


def test_jaccard_of_two_empty_sets():
    out = jaccard(set(), set())
    assert out == 1.0, f"two empty sets are identical: expected 1.0, got {out!r}"


def test_jaccard_empty_against_nonempty():
    out = jaccard(set(), {"a"})
    assert out == 0.0, f"expected 0.0, got {out!r}"


def test_dedupe_keeps_everything_distinct():
    texts = ["the quick brown fox", "entirely unrelated content here", "a third distinct string"]
    out = dedupe(texts, threshold=0.8)
    assert out == [0, 1, 2], f"expected [0, 1, 2], got {out!r}"


def test_dedupe_drops_exact_duplicates():
    texts = ["the quick brown fox", "the quick brown fox", "something else entirely"]
    out = dedupe(texts, threshold=0.8)
    assert out == [0, 2], f"expected [0, 2], got {out!r}"


def test_dedupe_drops_near_duplicates():
    texts = [
        "Copyright 2024 Example Corp. All rights reserved. Terms apply.",
        "Copyright 2025 Example Corp. All rights reserved. Terms apply.",
        "The mitochondrion is the powerhouse of the cell.",
    ]
    out = dedupe(texts, threshold=0.8)
    assert out == [0, 2], f"the near-duplicate footer must be dropped: expected [0, 2], got {out!r}"


def test_first_occurrence_wins():
    texts = ["alpha beta gamma delta", "alpha beta gamma delta"]
    out = dedupe(texts, threshold=0.5)
    assert out == [0], f"expected the first copy kept: [0], got {out!r}"


def test_threshold_one_keeps_almost_everything():
    texts = ["abcdefghij", "abcdefghik"]
    out = dedupe(texts, threshold=1.0)
    assert out == [0, 1], f"a threshold of 1.0 must only drop identical texts: got {out!r}"


def test_low_threshold_is_aggressive():
    texts = ["the quick brown fox", "the quick red fox", "the slow brown dog"]
    out = dedupe(texts, threshold=0.2)
    assert out[0] == 0, f"the first text is always kept, got {out!r}"
    assert len(out) < 3, f"a threshold of 0.2 must drop something, got {out!r}"


def test_compares_against_kept_not_all_previous():
    # b is close to a and is dropped; c is far from a, so it must survive even
    # though it is close to the dropped b.
    a = "aaaaaaaaaaaaaaaaaaaa"
    b = "aaaaaaaaaammmmmmmmmm"
    c = "mmmmmmmmmmmmmmmmmmmm"
    out = dedupe([a, b, c], threshold=0.3)
    assert 0 in out and 2 in out, f"expected the far-apart texts kept, got {out!r}"


def test_empty_list():
    assert dedupe([], threshold=0.8) == [], "expected []"


def test_indices_are_ascending_and_unique():
    texts = ["one two three", "four five six", "seven eight nine", "one two three"]
    out = dedupe(texts, threshold=0.9)
    assert out == sorted(out), f"expected ascending indices, got {out!r}"
    assert len(out) == len(set(out)), f"expected unique indices, got {out!r}"


def test_bad_threshold_raises():
    for bad in (-0.5, 1.5):
        try:
            dedupe(["a"], threshold=bad)
        except ValueError:
            continue
        raise AssertionError(f"threshold={bad} must raise ValueError")
