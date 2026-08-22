from submission import *


def test_basic_substitution():
    out = render("Hello {name}", {"name": "Ada"})
    assert out == "Hello Ada", f"expected 'Hello Ada', got {out!r}"


def test_no_placeholders():
    out = render("just text", {})
    assert out == "just text", f"expected 'just text', got {out!r}"


def test_empty_template():
    out = render("", {})
    assert out == "", f"expected '', got {out!r}"


def test_repeated_placeholder():
    out = render("{x} and {x}", {"x": "a"})
    assert out == "a and a", f"expected 'a and a', got {out!r}"


def test_whitespace_inside_braces_is_ignored():
    out = render("Hello { name }", {"name": "Ada"})
    assert out == "Hello Ada", f"expected 'Hello Ada', got {out!r}"


def test_non_string_values_are_stringified():
    out = render("{n} items, done={flag}", {"n": 3, "flag": True})
    assert out == "3 items, done=True", f"expected '3 items, done=True', got {out!r}"


def test_escaped_braces_become_literals():
    out = render("{{not a placeholder}}", {})
    assert out == "{not a placeholder}", f"expected '{{not a placeholder}}', got {out!r}"


def test_escaped_and_real_braces_together():
    out = render("{{{name}}}", {"name": "Ada"})
    assert out == "{Ada}", f"expected '{{Ada}}', got {out!r}"


def test_substituted_values_are_not_expanded():
    out = render("User said: {msg}", {"msg": "use {secret}", "secret": "hunter2"})
    exp = "User said: use {secret}"
    assert out == exp, f"a value must never be re-expanded: expected {exp!r}, got {out!r}"


def test_substituted_braces_are_not_unescaped():
    out = render("{msg}", {"msg": "{{literal}}"})
    exp = "{{literal}}"
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_missing_variable_raises_naming_it():
    try:
        render("Hello {name}", {})
    except KeyError as exc:
        assert "name" in str(exc), f"the error must name the placeholder, got {exc!r}"
        return
    raise AssertionError("a missing variable must raise KeyError when strict")


def test_non_strict_leaves_the_placeholder():
    out = render("Hello {name}, {greeting}", {"greeting": "hi"}, strict=False)
    exp = "Hello {name}, hi"
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_unmatched_open_brace_raises():
    try:
        render("Hello {name", {"name": "Ada"})
    except ValueError:
        return
    raise AssertionError("an unmatched '{' must raise ValueError")


def test_unmatched_close_brace_raises():
    try:
        render("Hello name}", {})
    except ValueError:
        return
    raise AssertionError("an unmatched '}' must raise ValueError")


def test_empty_placeholder_raises():
    try:
        render("Hello {}", {})
    except ValueError:
        return
    raise AssertionError("an empty placeholder must raise ValueError")


def test_variables_used():
    out = variables_used("Hi {name}, about {topic}: {name} again")
    exp = {"name", "topic"}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_variables_used_ignores_escaped_braces():
    out = variables_used("{{not one}} but {this} is")
    exp = {"this"}
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_variables_used_on_a_plain_template():
    out = variables_used("no placeholders here")
    assert out == set(), f"expected an empty set, got {out!r}"


def test_variables_used_agrees_with_render():
    template = "Hi {name}, you asked about {topic}"
    names = variables_used(template)
    rendered = render(template, dict.fromkeys(names, "x"))
    assert "{" not in rendered, f"every name from variables_used must render: {rendered!r}"
