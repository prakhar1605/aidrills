import math

from submission import *

A = [1.0, 0.0]
NEAR_A = [0.99, 0.14]  # cosine with A is about 0.990
B = [0.0, 1.0]


def test_empty_cache_misses():
    cache = SemanticCache()
    assert cache.get(A) is None, "an empty cache must miss"
    assert len(cache) == 0, f"expected 0, got {len(cache)}"


def test_exact_hit():
    cache = SemanticCache()
    cache.put(A, "answer")
    assert cache.get(A) == "answer", "an identical vector must hit"


def test_near_hit_above_threshold():
    cache = SemanticCache(threshold=0.9)
    cache.put(A, "answer")
    assert cache.get(NEAR_A) == "answer", "a 0.99 cosine must hit at a 0.9 threshold"


def test_miss_below_threshold():
    cache = SemanticCache(threshold=0.9)
    cache.put(A, "answer")
    assert cache.get(B) is None, "an orthogonal vector must miss"


def test_threshold_is_inclusive():
    cache = SemanticCache(threshold=1.0)
    cache.put(A, "answer")
    assert cache.get(A) == "answer", "a threshold of 1.0 must still match an exact repeat"


def test_returns_the_closest_match():
    cache = SemanticCache(threshold=0.5)
    cache.put([1.0, 0.0], "east")
    cache.put([0.0, 1.0], "north")
    assert cache.get([0.9, 0.1]) == "east", "the nearer entry must win"
    assert cache.get([0.1, 0.9]) == "north", "the nearer entry must win"


def test_stats_count_hits_and_misses():
    cache = SemanticCache()
    cache.put(A, "answer")
    cache.get(A)
    cache.get(B)
    cache.get(A)
    exp = {"hits": 2, "misses": 1}
    assert cache.stats == exp, f"expected {exp!r}, got {cache.stats!r}"


def test_put_updates_a_near_identical_entry():
    cache = SemanticCache(threshold=0.9)
    cache.put(A, "old")
    cache.put(NEAR_A, "new")
    assert len(cache) == 1, f"a near-duplicate must not grow the cache, got {len(cache)}"
    assert cache.get(A) == "new", "the entry must carry the newer value"


def test_put_adds_a_distinct_entry():
    cache = SemanticCache(threshold=0.9)
    cache.put(A, "east")
    cache.put(B, "north")
    assert len(cache) == 2, f"expected 2, got {len(cache)}"


def test_eviction_at_max_size():
    cache = SemanticCache(threshold=0.99, max_size=2)
    cache.put([1.0, 0.0], "one")
    cache.put([0.0, 1.0], "two")
    cache.put([-1.0, 0.0], "three")
    assert len(cache) == 2, f"expected 2, got {len(cache)}"
    assert cache.get([1.0, 0.0]) is None, "the least recently used entry must be gone"
    assert cache.get([-1.0, 0.0]) == "three", "the newest entry must be present"


def test_a_hit_refreshes_recency():
    cache = SemanticCache(threshold=0.99, max_size=2)
    cache.put([1.0, 0.0], "one")
    cache.put([0.0, 1.0], "two")
    assert cache.get([1.0, 0.0]) == "one", "setup: the first entry must still be there"
    cache.put([-1.0, 0.0], "three")
    assert cache.get([1.0, 0.0]) == "one", "reading an entry must protect it from eviction"
    assert cache.get([0.0, 1.0]) is None, "the untouched entry must have been evicted"


def test_unbounded_by_default():
    cache = SemanticCache(threshold=0.99)
    for i in range(20):
        angle = i * math.pi / 20
        cache.put([math.cos(angle), math.sin(angle)], i)
    assert len(cache) == 20, f"expected 20, got {len(cache)}"


def test_zero_vector_never_hits_and_never_nans():
    cache = SemanticCache(threshold=0.5)
    cache.put([0.0, 0.0], "nothing")
    assert cache.get([1.0, 0.0]) is None, "a zero vector has no direction, so it cannot match"
    assert cache.stats["misses"] == 1, f"expected 1 miss, got {cache.stats!r}"


def test_stored_vector_is_copied():
    cache = SemanticCache(threshold=0.99)
    vector = [1.0, 0.0]
    cache.put(vector, "answer")
    vector[0] = -1.0
    assert cache.get([1.0, 0.0]) == "answer", "the cache must not alias the caller's list"


def test_dimension_mismatch_raises():
    cache = SemanticCache()
    cache.put([1.0, 0.0], "answer")
    try:
        cache.get([1.0, 0.0, 0.0])
    except ValueError:
        return
    raise AssertionError("a mismatched dimension must raise ValueError")


def test_invalid_construction_raises():
    for kwargs in ({"threshold": -0.1}, {"threshold": 1.5}, {"max_size": 0}):
        try:
            SemanticCache(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"SemanticCache({kwargs!r}) must raise ValueError")
