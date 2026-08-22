from submission import *


def test_starts_full():
    bucket = TokenBucket(capacity=10, refill_per_sec=1)
    assert bucket.tokens == 10, f"expected 10, got {bucket.tokens!r}"


def test_consume_reduces_the_level():
    bucket = TokenBucket(capacity=10, refill_per_sec=1)
    assert bucket.consume(3) is True, "consuming 3 of 10 must succeed"
    assert bucket.tokens == 7, f"expected 7, got {bucket.tokens!r}"


def test_burst_up_to_capacity():
    bucket = TokenBucket(capacity=5, refill_per_sec=1)
    for i in range(5):
        assert bucket.consume(1) is True, f"burst call {i + 1} must succeed"
    assert bucket.consume(1) is False, "the sixth call exceeds the burst"


def test_rejection_takes_nothing():
    bucket = TokenBucket(capacity=5, refill_per_sec=1)
    bucket.consume(4)
    assert bucket.consume(3) is False, "3 tokens are not available"
    assert bucket.tokens == 1, f"a rejected request must not drain the bucket, got {bucket.tokens!r}"


def test_refills_over_time():
    bucket = TokenBucket(capacity=10, refill_per_sec=2, now=0.0)
    bucket.consume(10, now=0.0)
    assert bucket.consume(4, now=2.0) is True, "2 seconds at 2/s must refill 4 tokens"
    assert abs(bucket.tokens) < 1e-9, f"expected 0, got {bucket.tokens!r}"


def test_refill_is_capped_at_capacity():
    bucket = TokenBucket(capacity=5, refill_per_sec=1, now=0.0)
    bucket.consume(5, now=0.0)
    bucket.consume(0, now=1000.0)
    assert bucket.tokens == 5, f"an idle bucket must not exceed capacity, got {bucket.tokens!r}"


def test_partial_refill():
    bucket = TokenBucket(capacity=10, refill_per_sec=1, now=0.0)
    bucket.consume(10, now=0.0)
    assert bucket.consume(3, now=2.0) is False, "only 2 tokens have accrued"
    assert bucket.consume(2, now=2.0) is True, "2 tokens have accrued"


def test_sustained_rate():
    bucket = TokenBucket(capacity=1, refill_per_sec=1, now=0.0)
    for second in range(5):
        assert bucket.consume(1, now=float(second)) is True, f"second {second} must succeed"
        assert bucket.consume(1, now=float(second)) is False, f"second {second} must allow only one"


def test_clock_going_backwards_is_ignored():
    bucket = TokenBucket(capacity=10, refill_per_sec=1, now=100.0)
    bucket.consume(10, now=100.0)
    bucket.consume(0, now=50.0)
    assert bucket.tokens == 0, f"a backwards clock must not change the level, got {bucket.tokens!r}"
    assert bucket.consume(5, now=105.0) is True, "the bucket must still refill from the later time"


def test_now_none_means_no_time_passed():
    bucket = TokenBucket(capacity=10, refill_per_sec=1, now=0.0)
    bucket.consume(10, now=0.0)
    assert bucket.consume(1) is False, "with no time passed nothing has refilled"


def test_request_larger_than_capacity_never_succeeds():
    bucket = TokenBucket(capacity=5, refill_per_sec=1, now=0.0)
    assert bucket.consume(6, now=0.0) is False, "6 > capacity must fail"
    assert bucket.consume(6, now=1000.0) is False, "no amount of waiting makes 6 > capacity work"


def test_time_until_zero_when_available():
    bucket = TokenBucket(capacity=10, refill_per_sec=1)
    assert bucket.time_until(5) == 0.0, f"expected 0.0, got {bucket.time_until(5)!r}"


def test_time_until_computes_the_wait():
    bucket = TokenBucket(capacity=10, refill_per_sec=2, now=0.0)
    bucket.consume(10, now=0.0)
    out = bucket.time_until(5, now=0.0)
    exp = 2.5
    assert abs(out - exp) < 1e-9, f"expected {exp!r}, got {out!r}"


def test_time_until_is_infinite_above_capacity():
    bucket = TokenBucket(capacity=5, refill_per_sec=1)
    assert bucket.time_until(99) == float("inf"), "an impossible request waits forever"


def test_time_until_is_infinite_without_refill():
    bucket = TokenBucket(capacity=5, refill_per_sec=0, now=0.0)
    bucket.consume(5, now=0.0)
    assert bucket.time_until(1, now=10.0) == float("inf"), "a bucket that never refills waits forever"


def test_invalid_construction_raises():
    for capacity, rate in ((0, 1), (-1, 1), (5, -1)):
        try:
            TokenBucket(capacity=capacity, refill_per_sec=rate)
        except ValueError:
            continue
        raise AssertionError(f"TokenBucket({capacity}, {rate}) must raise ValueError")


def test_negative_consume_raises():
    bucket = TokenBucket(capacity=5, refill_per_sec=1)
    try:
        bucket.consume(-1)
    except ValueError:
        return
    raise AssertionError("consuming a negative amount must raise ValueError")
