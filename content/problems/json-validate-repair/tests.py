from submission import *


def test_plain_object():
    out = extract_json('{"ok": true}')
    exp = {"ok": True}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_plain_array():
    out = extract_json("[1, 2, 3]")
    exp = [1, 2, 3]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_fenced_with_a_language_tag():
    out = extract_json('Sure! Here you go:\n```json\n{"ok": true}\n```\nHope that helps.')
    exp = {"ok": True}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_fenced_without_a_language_tag():
    out = extract_json('```\n{"n": 1}\n```')
    exp = {"n": 1}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_prose_on_both_sides():
    out = extract_json('The answer is {"city": "Paris"} — let me know if you need more.')
    exp = {"city": "Paris"}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_trailing_comma_in_an_object():
    out = extract_json('{"a": 1, "b": 2,}')
    exp = {"a": 1, "b": 2}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_trailing_comma_in_an_array():
    out = extract_json("[1, 2, 3,]")
    exp = [1, 2, 3]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_brace_inside_a_string_value():
    out = extract_json('{"note": "close it with } like this"}')
    exp = {"note": "close it with } like this"}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_bracket_inside_a_string_value():
    out = extract_json('{"note": "an unmatched [ bracket"}')
    exp = {"note": "an unmatched [ bracket"}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_escaped_quote_inside_a_string():
    out = extract_json('{"q": "she said \\"hi\\""}')
    exp = {"q": 'she said "hi"'}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_repair_does_not_corrupt_valid_strings():
    # This parses as-is; a regex applied up front would eat the comma and
    # change the value.
    out = extract_json('{"note": "a comma, } then a brace"}')
    exp = {"note": "a comma, } then a brace"}
    assert out == exp, f"the repair must not run on valid JSON: expected {exp!r}, got {out!r}"


def test_nested_structures_survive():
    out = extract_json('{"items": [{"id": 1}, {"id": 2}], "meta": {"n": 2}}')
    exp = {"items": [{"id": 1}, {"id": 2}], "meta": {"n": 2}}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_first_value_wins():
    out = extract_json('{"first": 1} and then {"second": 2}')
    exp = {"first": 1}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_no_json_returns_none():
    out = extract_json("I could not complete that request.")
    assert out is None, f"expected None, got {out!r}"


def test_unbalanced_returns_none():
    out = extract_json('{"a": 1')
    assert out is None, f"expected None, got {out!r}"


def test_garbage_inside_braces_returns_none():
    out = extract_json("{this is not json at all}")
    assert out is None, f"expected None, got {out!r}"


def test_empty_string_returns_none():
    out = extract_json("")
    assert out is None, f"expected None, got {out!r}"


def test_never_raises():
    for bad in ["{", "[", "}{", '{"a": }', "``` ```", "{'a': 1}", '{"a": 1,,}']:
        try:
            extract_json(bad)
        except Exception as exc:
            raise AssertionError(f"extract_json({bad!r}) raised {exc!r}") from exc
