from submission import *


def test_overlapping_chunks():
    out = chunk_text("abcdefghij", size=4, overlap=1)
    exp = ["abcd", "defg", "ghij"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_no_overlap_leaves_short_tail():
    out = chunk_text("abcdefghij", size=4, overlap=0)
    exp = ["abcd", "efgh", "ij"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_text_shorter_than_size():
    out = chunk_text("abc", size=10, overlap=2)
    exp = ["abc"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_empty_text():
    out = chunk_text("", size=5, overlap=1)
    assert out == [], f"expected [], got {out!r}"


def test_chunks_actually_overlap():
    text = "the quick brown fox jumps over the lazy dog"
    chunks = chunk_text(text, size=10, overlap=3)
    for a, b in zip(chunks, chunks[1:]):
        assert a[-3:] == b[:3], f"{a!r} and {b!r} do not share 3 characters"


def test_no_redundant_tail_chunk():
    chunks = chunk_text("abcdefgh", size=4, overlap=2)
    for a, b in zip(chunks, chunks[1:]):
        assert b not in a, f"chunk {b!r} is already contained in {a!r}"


def test_covers_every_character():
    text = "abcdefghijklmno"
    chunks = chunk_text(text, size=6, overlap=2)
    joined = chunks[0] + "".join(c[2:] for c in chunks[1:])
    assert joined == text, f"expected {text!r}, got {joined!r}"


def test_rejects_overlap_equal_to_size():
    try:
        chunk_text("abcdef", size=3, overlap=3)
    except ValueError:
        return
    raise AssertionError("overlap == size must raise ValueError")


def test_rejects_non_positive_size():
    try:
        chunk_text("abcdef", size=0, overlap=0)
    except ValueError:
        return
    raise AssertionError("size <= 0 must raise ValueError")
