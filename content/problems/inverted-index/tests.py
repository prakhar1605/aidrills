from submission import *


def build():
    index = InvertedIndex()
    index.add(1, ["the", "cat", "sat"])
    index.add(2, ["the", "dog", "sat"])
    index.add(3, ["quantum", "entanglement"])
    return index


def test_empty_index():
    index = InvertedIndex()
    assert len(index) == 0, f"expected 0, got {len(index)}"
    assert index.postings("cat") == [], f"expected [], got {index.postings('cat')!r}"
    assert index.df("cat") == 0, f"expected 0, got {index.df('cat')}"


def test_postings_are_sorted():
    index = InvertedIndex()
    index.add(9, ["x"])
    index.add(2, ["x"])
    index.add(5, ["x"])
    exp = [2, 5, 9]
    assert index.postings("x") == exp, f"expected {exp!r}, got {index.postings('x')!r}"


def test_document_frequency():
    index = build()
    assert index.df("the") == 2, f"expected 2, got {index.df('the')}"
    assert index.df("cat") == 1, f"expected 1, got {index.df('cat')}"
    assert index.df("zzz") == 0, f"expected 0, got {index.df('zzz')}"


def test_repeated_tokens_count_once():
    index = InvertedIndex()
    index.add(1, ["cat", "cat", "cat"])
    assert index.postings("cat") == [1], f"expected [1], got {index.postings('cat')!r}"
    assert index.df("cat") == 1, f"expected 1, got {index.df('cat')}"


def test_len_counts_documents():
    index = build()
    assert len(index) == 3, f"expected 3, got {len(index)}"


def test_and_search():
    index = build()
    out = index.search(["the", "sat"], mode="and")
    exp = [1, 2]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_and_search_narrows():
    index = build()
    out = index.search(["the", "cat"], mode="and")
    assert out == [1], f"expected [1], got {out!r}"


def test_and_with_an_unknown_term_is_empty():
    index = build()
    out = index.search(["the", "zzz"], mode="and")
    assert out == [], f"expected [], got {out!r}"


def test_or_search():
    index = build()
    out = index.search(["cat", "quantum"], mode="or")
    exp = [1, 3]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_or_ignores_unknown_terms():
    index = build()
    out = index.search(["cat", "zzz"], mode="or")
    assert out == [1], f"expected [1], got {out!r}"


def test_empty_query():
    index = build()
    assert index.search([], mode="and") == [], "an empty AND query must return []"
    assert index.search([], mode="or") == [], "an empty OR query must return []"


def test_bad_mode_raises():
    index = build()
    try:
        index.search(["cat"], mode="xor")
    except ValueError:
        return
    raise AssertionError('an unknown mode must raise ValueError')


def test_readding_replaces_the_old_terms():
    index = build()
    index.add(1, ["the", "bird"])
    assert index.postings("cat") == [], (
        f"'cat' must no longer point at document 1, got {index.postings('cat')!r}"
    )
    assert index.postings("bird") == [1], f"expected [1], got {index.postings('bird')!r}"
    assert index.postings("the") == [1, 2], f"expected [1, 2], got {index.postings('the')!r}"


def test_readding_does_not_double_count():
    index = build()
    index.add(1, ["the", "cat", "sat"])
    assert len(index) == 3, f"expected 3, got {len(index)}"
    assert index.df("the") == 2, f"expected 2, got {index.df('the')}"


def test_remove():
    index = build()
    index.remove(1)
    assert len(index) == 2, f"expected 2, got {len(index)}"
    assert index.postings("cat") == [], f"expected [], got {index.postings('cat')!r}"
    assert index.postings("the") == [2], f"expected [2], got {index.postings('the')!r}"


def test_removing_an_unknown_document_is_a_noop():
    index = build()
    index.remove(999)
    assert len(index) == 3, f"expected 3, got {len(index)}"


def test_removing_everything_clears_the_terms():
    index = build()
    for doc_id in (1, 2, 3):
        index.remove(doc_id)
    assert len(index) == 0, f"expected 0, got {len(index)}"
    assert index.df("the") == 0, f"expected 0, got {index.df('the')}"
    assert index.search(["the"], mode="or") == [], "nothing should match an empty index"
