from submission import *

DOC = "Alpha beta gamma.\n\nDelta epsilon zeta eta.\nTheta iota.\n\nKappa."


def test_short_text_is_one_chunk():
    out = split_text("hello", size=100)
    assert out == ["hello"], f"expected ['hello'], got {out!r}"


def test_empty_text():
    out = split_text("", size=10)
    assert out == [], f"expected [], got {out!r}"


def test_joining_reproduces_the_text():
    for size in (5, 12, 30, 64):
        out = split_text(DOC, size)
        assert "".join(out) == DOC, f"size={size} lost or duplicated text: {out!r}"


def test_every_chunk_fits():
    for size in (5, 12, 30, 64):
        for chunk in split_text(DOC, size):
            assert len(chunk) <= size, f"size={size} produced a {len(chunk)}-char chunk: {chunk!r}"


def test_prefers_paragraph_breaks():
    out = split_text("aaa\n\nbbb\n\nccc", size=8)
    exp = ["aaa\n\n", "bbb\n\nccc"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_falls_back_to_single_newlines():
    out = split_text("aaaa\nbbbb\ncccc", size=6)
    exp = ["aaaa\n", "bbbb\n", "cccc"]
    assert out == exp, f"expected cuts on the newlines: {exp!r}, got {out!r}"


def test_falls_back_to_spaces():
    out = split_text("one two three four", size=9)
    assert "".join(out) == "one two three four", f"text was lost: {out!r}"
    assert all(len(chunk) <= 9 for chunk in out), f"a chunk overflowed: {out!r}"
    assert len(out) > 1, f"expected more than one chunk, got {out!r}"


def test_a_single_long_word_is_hard_sliced():
    out = split_text("supercalifragilistic", size=6)
    exp = ["superc", "alifra", "gilist", "ic"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_short_lines_are_merged():
    text = "a\nb\nc\nd\ne\nf"
    out = split_text(text, size=6)
    assert "".join(out) == text, f"text was lost: {out!r}"
    assert len(out) <= 2, f"short lines must be packed, not emitted one by one: {out!r}"


def test_merging_never_overflows():
    text = "\n".join(["line"] * 20)
    for chunk in split_text(text, size=10):
        assert len(chunk) <= 10, f"a merged chunk overflowed: {chunk!r}"


def test_leading_and_trailing_separators_survive():
    text = "\n\nmiddle\n\n"
    out = split_text(text, size=4)
    assert "".join(out) == text, f"expected the text back exactly, got {out!r}"


def test_custom_separators():
    out = split_text("a;bb;ccc;dddd", size=5, separators=(";", ""))
    assert "".join(out) == "a;bb;ccc;dddd", f"text was lost: {out!r}"
    assert all(len(chunk) <= 5 for chunk in out), f"a chunk overflowed: {out!r}"


def test_no_empty_chunks():
    for size in (3, 7, 20):
        assert all(split_text(DOC, size)), f"size={size} produced an empty chunk"


def test_non_positive_size_raises():
    try:
        split_text("abc", size=0)
    except ValueError:
        return
    raise AssertionError("size <= 0 must raise ValueError")
