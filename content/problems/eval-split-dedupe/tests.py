from submission import *


def make(n, prefix="example"):
    return [{"id": i, "text": f"{prefix} number {i}"} for i in range(n)]


def test_normalize_lowercases_and_strips_punctuation():
    out = normalize("What is  the Capital, of France?")
    exp = "what is the capital of france"
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_normalize_collapses_whitespace():
    out = normalize("  a\tb\nc  ")
    assert out == "a b c", f"expected 'a b c', got {out!r}"


def test_empty_input():
    out = dedupe_and_split([])
    assert out["train"] == [] and out["val"] == [] and out["test"] == [], f"got {out!r}"
    assert out["dropped"] == 0, f"expected 0, got {out['dropped']!r}"


def test_exact_counts():
    out = dedupe_and_split(make(10), ratios=(0.8, 0.1, 0.1))
    assert len(out["train"]) == 8, f"expected 8, got {len(out['train'])}"
    assert len(out["val"]) == 1, f"expected 1, got {len(out['val'])}"
    assert len(out["test"]) == 1, f"expected 1, got {len(out['test'])}"


def test_nothing_is_lost_to_rounding():
    for n in range(1, 40):
        out = dedupe_and_split(make(n))
        total = len(out["train"]) + len(out["val"]) + len(out["test"])
        assert total == n, f"n={n}: the splits hold {total}, expected {n}"


def test_largest_remainder_distribution():
    out = dedupe_and_split(make(7), ratios=(0.5, 0.25, 0.25))
    sizes = [len(out["train"]), len(out["val"]), len(out["test"])]
    exp = [3, 2, 2]
    assert sizes == exp, f"expected {exp!r}, got {sizes!r}"


def test_duplicates_are_dropped():
    examples = [
        {"id": 0, "text": "What is the capital of France?"},
        {"id": 1, "text": "what is the capital of france"},
        {"id": 2, "text": "Something else entirely"},
    ]
    out = dedupe_and_split(examples)
    kept = out["train"] + out["val"] + out["test"]
    assert len(kept) == 2, f"expected 2 unique examples, got {kept!r}"
    assert out["dropped"] == 1, f"expected 1 dropped, got {out['dropped']!r}"


def test_first_occurrence_wins():
    examples = [
        {"id": "first", "text": "same thing"},
        {"id": "second", "text": "Same thing!"},
    ]
    out = dedupe_and_split(examples)
    kept = out["train"] + out["val"] + out["test"]
    assert [e["id"] for e in kept] == ["first"], f"expected the first copy, got {kept!r}"


def test_no_duplicates_means_nothing_dropped():
    out = dedupe_and_split(make(12))
    assert out["dropped"] == 0, f"expected 0, got {out['dropped']!r}"


def test_no_leakage_between_splits():
    out = dedupe_and_split(make(30))
    ids = [
        {e["id"] for e in out["train"]},
        {e["id"] for e in out["val"]},
        {e["id"] for e in out["test"]},
    ]
    for i in range(3):
        for j in range(i + 1, 3):
            overlap = ids[i] & ids[j]
            assert overlap == set(), f"splits {i} and {j} share {overlap!r}"


def test_every_example_lands_somewhere():
    examples = make(25)
    out = dedupe_and_split(examples)
    placed = {e["id"] for e in out["train"] + out["val"] + out["test"]}
    assert placed == {e["id"] for e in examples}, f"expected every id placed, got {sorted(placed)!r}"


def test_the_same_seed_is_reproducible():
    examples = make(30)
    a = dedupe_and_split(examples, seed=7)
    b = dedupe_and_split(examples, seed=7)
    assert [e["id"] for e in a["train"]] == [e["id"] for e in b["train"]], "the same seed must reproduce"
    assert [e["id"] for e in a["test"]] == [e["id"] for e in b["test"]], "the same seed must reproduce"


def test_different_seeds_split_differently():
    examples = make(30)
    orders = {
        tuple(e["id"] for e in dedupe_and_split(examples, seed=s)["train"]) for s in range(5)
    }
    assert len(orders) > 1, "different seeds must produce different splits"


def test_original_dicts_are_returned():
    examples = [{"id": 0, "text": "hello", "extra": "kept"}]
    out = dedupe_and_split(examples)
    kept = out["train"] + out["val"] + out["test"]
    assert kept[0]["extra"] == "kept", f"the original fields must survive, got {kept!r}"


def test_input_list_is_not_reordered():
    examples = make(20)
    before = [e["id"] for e in examples]
    dedupe_and_split(examples)
    assert [e["id"] for e in examples] == before, "the caller's list must not be shuffled in place"


def test_all_in_train():
    out = dedupe_and_split(make(9), ratios=(1.0, 0.0, 0.0))
    assert len(out["train"]) == 9, f"expected 9, got {len(out['train'])}"
    assert out["val"] == [] and out["test"] == [], f"expected the others empty, got {out!r}"


def test_bad_ratios_raise():
    for bad in [(0.5, 0.5, 0.5), (0.9, 0.1), (1.2, -0.1, -0.1), (0.3, 0.3, 0.3)]:
        try:
            dedupe_and_split(make(5), ratios=bad)
        except ValueError:
            continue
        raise AssertionError(f"ratios={bad!r} must raise ValueError")
