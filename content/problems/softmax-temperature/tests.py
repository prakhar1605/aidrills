import math

from submission import *


def test_sums_to_one():
    out = softmax([1.0, 2.0, 3.0])
    assert math.isclose(sum(out), 1.0, rel_tol=1e-12), f"expected 1.0, got {sum(out)!r}"


def test_uniform_logits_give_uniform_probabilities():
    out = softmax([0.0, 0.0, 0.0, 0.0])
    exp = [0.25] * 4
    assert all(math.isclose(a, b) for a, b in zip(out, exp)), f"expected {exp!r}, got {out!r}"


def test_order_is_preserved():
    out = softmax([1.0, 3.0, 2.0])
    assert out[1] > out[2] > out[0], f"probabilities must follow the logits, got {out!r}"


def test_known_two_way_split():
    out = softmax([0.0, math.log(3)])
    exp = [0.25, 0.75]
    assert all(math.isclose(a, b) for a, b in zip(out, exp)), f"expected {exp!r}, got {out!r}"


def test_low_temperature_sharpens():
    cold = softmax([1.0, 2.0], temperature=0.1)
    warm = softmax([1.0, 2.0], temperature=1.0)
    assert cold[1] > warm[1], f"a colder temperature must concentrate mass: {cold!r} vs {warm!r}"


def test_high_temperature_flattens():
    hot = softmax([1.0, 5.0], temperature=100.0)
    assert abs(hot[0] - hot[1]) < 0.05, f"a hot temperature must flatten, got {hot!r}"


def test_zero_temperature_is_greedy():
    out = softmax([2.0, 1.0, 5.0], temperature=0.0)
    exp = [0.0, 0.0, 1.0]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_zero_temperature_breaks_ties_low():
    out = softmax([5.0, 5.0, 1.0], temperature=0.0)
    exp = [1.0, 0.0, 0.0]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_negative_temperature_raises():
    try:
        softmax([1.0, 2.0], temperature=-1.0)
    except ValueError:
        return
    raise AssertionError("a negative temperature must raise ValueError")


def test_empty_logits():
    out = softmax([])
    assert out == [], f"expected [], got {out!r}"


def test_survives_large_logits():
    out = softmax([900.0, 899.0])
    assert all(not math.isnan(p) for p in out), f"overflowed to nan: {out!r}"
    assert math.isclose(sum(out), 1.0, rel_tol=1e-9), f"expected 1.0, got {sum(out)!r}"


def test_survives_a_tiny_temperature():
    # Dividing by 0.01 multiplies every logit by 100 -- this is the overflow case.
    out = softmax([10.0, 9.0], temperature=0.01)
    assert all(not math.isnan(p) for p in out), f"overflowed to nan: {out!r}"
    assert math.isclose(out[0], 1.0, abs_tol=1e-9), f"expected the top logit to dominate, got {out!r}"


def test_shift_invariance():
    a = softmax([1.0, 2.0, 3.0])
    b = softmax([101.0, 102.0, 103.0])
    assert all(math.isclose(x, y, rel_tol=1e-9) for x, y in zip(a, b)), (
        f"softmax must be shift-invariant: {a!r} vs {b!r}"
    )
