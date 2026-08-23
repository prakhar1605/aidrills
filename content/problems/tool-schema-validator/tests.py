from submission import *

SCHEMA = {
    "properties": {
        "q": {"type": "string"},
        "top_k": {"type": "integer"},
        "score": {"type": "number"},
        "verbose": {"type": "boolean"},
        "tags": {"type": "array"},
        "meta": {"type": "object"},
        "mode": {"type": "string", "enum": ["and", "or"]},
    },
    "required": ["q"],
}


def test_valid_arguments():
    out = validate_args(SCHEMA, {"q": "hello"})
    assert out == [], f"expected no errors, got {out!r}"


def test_all_types_accepted():
    args = {
        "q": "x",
        "top_k": 5,
        "score": 1.5,
        "verbose": True,
        "tags": ["a"],
        "meta": {"k": 1},
        "mode": "and",
    }
    out = validate_args(SCHEMA, args)
    assert out == [], f"expected no errors, got {out!r}"


def test_missing_required():
    out = validate_args(SCHEMA, {})
    exp = ["missing required property: q"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_unknown_property():
    out = validate_args(SCHEMA, {"q": "x", "colour": "red"})
    exp = ["unknown property: colour"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_wrong_type():
    out = validate_args(SCHEMA, {"q": 5})
    exp = ["q: expected string, got int"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_string_digits_are_not_an_integer():
    out = validate_args(SCHEMA, {"q": "x", "top_k": "5"})
    exp = ["top_k: expected integer, got str"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_float_is_not_an_integer():
    out = validate_args(SCHEMA, {"q": "x", "top_k": 1.5})
    exp = ["top_k: expected integer, got float"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_integer_is_a_valid_number():
    out = validate_args(SCHEMA, {"q": "x", "score": 3})
    assert out == [], f"an int must satisfy 'number', got {out!r}"


def test_bool_is_not_an_integer():
    out = validate_args(SCHEMA, {"q": "x", "top_k": True})
    exp = ["top_k: expected integer, got bool"]
    assert out == exp, f"isinstance(True, int) is True in Python: expected {exp!r}, got {out!r}"


def test_bool_is_not_a_number():
    out = validate_args(SCHEMA, {"q": "x", "score": False})
    exp = ["score: expected number, got bool"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_integer_is_not_a_boolean():
    out = validate_args(SCHEMA, {"q": "x", "verbose": 1})
    exp = ["verbose: expected boolean, got int"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_enum_violation():
    out = validate_args(SCHEMA, {"q": "x", "mode": "xor"})
    exp = ["mode: expected one of ['and', 'or'], got 'xor'"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_enum_is_not_checked_after_a_type_error():
    out = validate_args(SCHEMA, {"q": "x", "mode": 7})
    exp = ["mode: expected string, got int"]
    assert out == exp, f"one property must produce one error: expected {exp!r}, got {out!r}"


def test_all_errors_are_reported():
    out = validate_args(SCHEMA, {"top_k": "5", "colour": "red"})
    exp = sorted(
        [
            "missing required property: q",
            "top_k: expected integer, got str",
            "unknown property: colour",
        ]
    )
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_errors_are_sorted():
    out = validate_args(SCHEMA, {"zebra": 1, "apple": 2})
    assert out == sorted(out), f"expected sorted errors, got {out!r}"


def test_empty_schema_accepts_nothing_extra():
    out = validate_args({}, {"anything": 1})
    exp = ["unknown property: anything"]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_empty_schema_and_no_args():
    out = validate_args({}, {})
    assert out == [], f"expected no errors, got {out!r}"


def test_unsupported_schema_type_raises():
    try:
        validate_args({"properties": {"x": {"type": "date"}}}, {})
    except ValueError:
        return
    raise AssertionError("an unsupported type in the schema must raise ValueError")
