"""Coverage for python/mock_llm.py -- the fake LLM drills are written against."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mock_llm import MockLLM, RateLimitError, ServerError, count_tokens, flaky  # noqa: E402


def test_substring_match_beats_the_default():
    llm = MockLLM(responses={"summarize": "Short summary.", "*": "ok"})
    assert llm.complete("Please summarize this document") == "Short summary."
    assert llm.complete("Anything else") == "ok"


def test_default_response_without_a_star():
    llm = MockLLM(responses={"only": "hit"})
    assert llm.complete("nothing matches") == "ok"


def test_calls_are_recorded_in_order():
    llm = MockLLM()
    llm.complete("first")
    llm.complete("second")
    assert llm.prompts() == ["first", "second"]
    assert [call["n"] for call in llm.calls] == [1, 2]
    assert llm.call_count == 2


def test_fail_on_call_raises_on_that_call_only():
    llm = MockLLM(fail_on_call=[2])
    assert llm.complete("one") == "ok"
    with pytest.raises(RateLimitError):
        llm.complete("two")
    assert llm.complete("three") == "ok"


def test_failed_calls_are_still_recorded():
    llm = MockLLM(fail_on_call=[1])
    with pytest.raises(RateLimitError):
        llm.complete("boom")
    assert llm.call_count == 1


def test_the_error_class_is_configurable():
    llm = MockLLM(fail_on_call=[1], error=ServerError)
    with pytest.raises(ServerError):
        llm.complete("boom")


def test_stream_reassembles_into_the_reply():
    llm = MockLLM(responses={"*": "one two three"})
    assert "".join(llm.stream("go")) == "one two three"


def test_stream_yields_more_than_one_chunk():
    llm = MockLLM(responses={"*": "one two three"})
    assert len(list(llm.stream("go"))) == 3


def test_tool_calls_are_consumed_in_order():
    llm = MockLLM(tool_calls=[{"name": "search", "arguments": {"q": "x"}}, {"name": None}])
    first = llm.tool_call("prompt", ["search"])
    assert first["name"] == "search"
    assert first["arguments"] == {"q": "x"}
    assert llm.tool_call("prompt", ["search"])["name"] is None


def test_exhausted_script_falls_through_to_a_final_answer():
    llm = MockLLM(responses={"*": "done"})
    step = llm.tool_call("prompt", [])
    assert step["name"] is None
    assert step["content"] == "done"


def test_tool_call_fills_in_missing_arguments():
    llm = MockLLM(tool_calls=[{"name": "search"}])
    assert llm.tool_call("prompt", ["search"])["arguments"] == {}


def test_tool_call_records_the_offered_tools():
    llm = MockLLM(tool_calls=[{"name": None}])
    llm.tool_call("prompt", ["a", "b"])
    assert llm.calls[0]["tools"] == ["a", "b"]


def test_the_script_is_not_mutated_across_instances():
    script = [{"name": "search", "arguments": {"q": "x"}}]
    MockLLM(tool_calls=script).tool_call("p", [])
    assert script == [{"name": "search", "arguments": {"q": "x"}}]


def test_reset_clears_calls_and_the_script_position():
    llm = MockLLM(tool_calls=[{"name": "a"}, {"name": "b"}])
    llm.tool_call("p", [])
    llm.reset()
    assert llm.calls == []
    assert llm.tool_call("p", [])["name"] == "a"


@pytest.mark.parametrize(
    "text,expected",
    [("", 0), ("hello", 1), ("hello world", 2), ("hello, world!", 4)],
)
def test_count_tokens(text, expected):
    assert count_tokens(text) == expected


def test_count_tokens_is_deterministic():
    text = "The quick brown fox, jumping."
    assert count_tokens(text) == count_tokens(text)


def test_flaky_raises_until_the_target_attempt():
    call = flaky(succeed_on=3, result="done")
    for _ in range(2):
        with pytest.raises(RateLimitError):
            call()
    assert call() == "done"
    assert call.attempts["n"] == 3


def test_flaky_can_raise_any_error():
    call = flaky(succeed_on=99, error=ValueError)
    with pytest.raises(ValueError):
        call()
