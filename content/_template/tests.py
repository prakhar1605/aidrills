from submission import *


def test_happy_path():
    out = solve()
    exp = None
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_empty_input():
    raise AssertionError("write me")
