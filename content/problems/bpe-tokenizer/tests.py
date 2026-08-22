from submission import *

CORPUS = ["low"] * 5 + ["lower"] * 2 + ["newest"] * 6 + ["widest"] * 3


def test_empty_corpus():
    out = train_bpe([], 10)
    assert out == [], f"expected [], got {out!r}"


def test_zero_merges():
    out = train_bpe(CORPUS, 0)
    assert out == [], f"expected [], got {out!r}"


def test_learns_at_most_num_merges():
    out = train_bpe(CORPUS, 3)
    assert len(out) == 3, f"expected 3 merges, got {len(out)}: {out!r}"


def test_stops_when_no_pairs_remain():
    # "a" + "</w>" is a single pair; after merging it there is nothing left.
    out = train_bpe(["a"], 5)
    exp = [("a", "</w>")]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_merges_are_tuples_of_two_symbols():
    for pair in train_bpe(CORPUS, 5):
        assert isinstance(pair, tuple) and len(pair) == 2, f"expected a 2-tuple, got {pair!r}"


def test_most_frequent_pair_is_learned_first():
    # "ab" appears in every word; nothing else comes close.
    corpus = ["abc"] * 10 + ["abd"] * 8 + ["xyz"] * 2
    first = train_bpe(corpus, 1)[0]
    exp = ("a", "b")
    assert first == exp, f"expected {exp!r}, got {first!r}"


def test_ties_break_lexicographically():
    # "ab" and "cd" each occur once per word, so their counts tie.
    first = train_bpe(["abcd"], 1)[0]
    exp = ("a", "b")
    assert first == exp, f"the smaller pair must win the tie: expected {exp!r}, got {first!r}"


def test_training_is_deterministic():
    a = train_bpe(CORPUS, 8)
    b = train_bpe(list(reversed(CORPUS)), 8)
    assert a == b, f"corpus order must not matter: {a!r} vs {b!r}"


def test_frequency_is_weighted_not_counted_once():
    # "qz" occurs in one word type but 20 documents; "mn" in two types, once each.
    corpus = ["qz"] * 20 + ["mna", "mnb"]
    first = train_bpe(corpus, 1)[0]
    exp = ("q", "z")
    assert first == exp, f"expected {exp!r}, got {first!r}"


def test_encode_without_merges_is_characters_plus_marker():
    out = encode("low", [])
    exp = ["l", "o", "w", "</w>"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_encode_applies_a_merge():
    out = encode("low", [("l", "o")])
    exp = ["lo", "w", "</w>"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_encode_applies_merges_in_order():
    merges = [("l", "o"), ("lo", "w")]
    out = encode("low", merges)
    exp = ["low", "</w>"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_encode_ignores_merges_that_do_not_apply_yet():
    # ("lo", "w") cannot fire before ("l", "o") has produced "lo".
    merges = [("lo", "w"), ("l", "o")]
    out = encode("low", merges)
    exp = ["lo", "w", "</w>"]
    assert out == exp, f"applying merges out of order changes the result: expected {exp!r}, got {out!r}"


def test_encode_merges_repeated_occurrences():
    out = encode("ababab", [("a", "b")])
    exp = ["ab", "ab", "ab", "</w>"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_encode_does_not_overlap_occurrences():
    out = encode("aaa", [("a", "a")])
    exp = ["aa", "a", "</w>"]
    assert out == exp, f"expected a single left-to-right pass: {exp!r}, got {out!r}"


def test_encoding_round_trips():
    merges = train_bpe(CORPUS, 12)
    for word in ["low", "lower", "newest", "widest", "unseenword", "x"]:
        out = "".join(encode(word, merges)).replace("</w>", "")
        assert out == word, f"expected {word!r}, got {out!r}"


def test_encoding_compresses_a_trained_word():
    merges = train_bpe(CORPUS, 12)
    out = encode("newest", merges)
    assert len(out) < len("newest") + 1, f"expected fewer than 7 symbols, got {out!r}"


def test_every_encoding_ends_with_the_marker():
    merges = train_bpe(CORPUS, 4)
    for word in ["low", "widest", "zzz"]:
        out = encode(word, merges)
        assert out[-1].endswith("</w>"), f"expected {word!r} to end with the marker, got {out!r}"
