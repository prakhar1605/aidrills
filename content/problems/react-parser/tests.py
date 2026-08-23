from submission import *

ACTION = """Thought: I should look up the weather.
Action: search
Action Input: {"q": "weather in Paris"}"""

FINAL = """Thought: I already know this.
Final Answer: It is sunny in Paris."""


def test_parses_an_action():
    out = parse_react(ACTION)
    assert out["kind"] == "action", f"expected 'action', got {out['kind']!r}"
    assert out["action"] == "search", f"expected 'search', got {out['action']!r}"
    assert out["input"] == {"q": "weather in Paris"}, f"expected the decoded JSON, got {out['input']!r}"


def test_parses_the_thought():
    out = parse_react(ACTION)
    exp = "I should look up the weather."
    assert out["thought"] == exp, f"expected {exp!r}, got {out['thought']!r}"


def test_parses_a_final_answer():
    out = parse_react(FINAL)
    assert out["kind"] == "final", f"expected 'final', got {out['kind']!r}"
    assert out["answer"] == "It is sunny in Paris.", f"got {out['answer']!r}"


def test_missing_thought_is_none():
    out = parse_react("Action: search\nAction Input: {}")
    assert out["thought"] is None, f"expected None, got {out['thought']!r}"


def test_labels_are_case_insensitive():
    out = parse_react("THOUGHT: hmm\naction: search\nACTION INPUT: {}")
    assert out["kind"] == "action", f"expected 'action', got {out['kind']!r}"
    assert out["action"] == "search", f"expected 'search', got {out['action']!r}"


def test_leading_whitespace_is_tolerated():
    out = parse_react("  Action: search\n  Action Input: {}")
    assert out["action"] == "search", f"expected 'search', got {out['action']!r}"


def test_non_json_action_input_stays_a_string():
    out = parse_react("Action: search\nAction Input: weather in Paris")
    assert out["input"] == "weather in Paris", f"expected the raw string, got {out['input']!r}"


def test_missing_action_input_is_an_empty_dict():
    out = parse_react("Action: list_files")
    assert out["input"] == {}, f"expected an empty dict, got {out['input']!r}"


def test_json_array_input():
    out = parse_react('Action: batch\nAction Input: [1, 2, 3]')
    assert out["input"] == [1, 2, 3], f"expected [1, 2, 3], got {out['input']!r}"


def test_action_takes_only_its_first_line():
    out = parse_react("Action: search\nsome trailing commentary\nAction Input: {}")
    assert out["action"] == "search", f"expected 'search', got {out['action']!r}"


def test_multiline_thought():
    out = parse_react("Thought: first line\nstill thinking\nAction: search")
    exp = "first line\nstill thinking"
    assert out["thought"] == exp, f"expected {exp!r}, got {out['thought']!r}"


def test_multiline_final_answer():
    out = parse_react("Final Answer: line one\nline two")
    exp = "line one\nline two"
    assert out["answer"] == exp, f"expected {exp!r}, got {out['answer']!r}"


def test_final_answer_first_wins():
    text = "Final Answer: done\nAction: search\nAction Input: {}"
    out = parse_react(text)
    assert out["kind"] == "final", f"the earlier label must win: got {out['kind']!r}"


def test_action_first_wins():
    text = "Action: search\nAction Input: {}\nFinal Answer: done"
    out = parse_react(text)
    assert out["kind"] == "action", f"the earlier label must win: got {out['kind']!r}"


def test_a_label_inside_a_thought_is_not_a_label():
    out = parse_react("Thought: the format is Action: name\nFinal Answer: ok")
    assert out["kind"] == "final", f"expected 'final', got {out['kind']!r}"
    assert "Action: name" in out["thought"], f"the thought must survive intact, got {out['thought']!r}"


def test_no_action_or_final_raises():
    try:
        parse_react("Thought: I am just thinking out loud.")
    except ValueError:
        return
    raise AssertionError("output with no Action and no Final Answer must raise ValueError")


def test_empty_text_raises():
    try:
        parse_react("")
    except ValueError:
        return
    raise AssertionError("empty output must raise ValueError")
