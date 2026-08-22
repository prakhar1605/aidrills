from mock_llm import MockLLM

from submission import *


def make_tools(log=None):
    def search(q):
        if log is not None:
            log.append(("search", q))
        return f"results for {q}"

    def add(a, b):
        return a + b

    def boom():
        raise RuntimeError("tool exploded")

    return {"search": search, "add": add, "boom": boom}


def test_runs_a_tool_then_answers():
    llm = MockLLM(
        tool_calls=[
            {"name": "search", "arguments": {"q": "weather"}},
            {"name": None, "content": "It is sunny."},
        ]
    )
    out = run_agent(llm, make_tools(), "what is the weather")
    assert out["answer"] == "It is sunny.", f"expected 'It is sunny.', got {out['answer']!r}"
    assert out["stopped"] == "final", f"expected 'final', got {out['stopped']!r}"
    assert out["steps"] == 1, f"expected 1 step, got {out['steps']!r}"


def test_trace_records_each_call():
    llm = MockLLM(
        tool_calls=[
            {"name": "add", "arguments": {"a": 2, "b": 3}},
            {"name": None, "content": "5"},
        ]
    )
    out = run_agent(llm, make_tools(), "2 + 3")
    exp = [{"tool": "add", "arguments": {"a": 2, "b": 3}, "observation": "5"}]
    assert out["trace"] == exp, f"expected {exp!r}, got {out['trace']!r}"


def test_answers_immediately_without_tools():
    llm = MockLLM(responses={"*": "42"})
    out = run_agent(llm, make_tools(), "no tools needed")
    assert out["stopped"] == "final", f"expected 'final', got {out['stopped']!r}"
    assert out["steps"] == 0, f"expected 0 steps, got {out['steps']!r}"
    assert out["trace"] == [], f"expected an empty trace, got {out['trace']!r}"
    assert out["answer"] == "42", f"expected '42', got {out['answer']!r}"


def test_budget_stops_the_loop():
    llm = MockLLM(tool_calls=[{"name": "search", "arguments": {"q": "x"}}] * 10)
    out = run_agent(llm, make_tools(), "loop forever", max_steps=3)
    assert out["stopped"] == "budget", f"expected 'budget', got {out['stopped']!r}"
    assert out["steps"] == 3, f"expected 3 steps, got {out['steps']!r}"
    assert out["answer"] is None, f"expected None, got {out['answer']!r}"
    assert llm.call_count == 3, f"the model must be called at most 3 times, saw {llm.call_count}"


def test_arguments_reach_the_tool():
    log = []
    llm = MockLLM(
        tool_calls=[
            {"name": "search", "arguments": {"q": "pyodide"}},
            {"name": None, "content": "done"},
        ]
    )
    run_agent(llm, make_tools(log), "find it")
    exp = [("search", "pyodide")]
    assert log == exp, f"expected {exp!r}, got {log!r}"


def test_observations_are_fed_back():
    llm = MockLLM(
        tool_calls=[
            {"name": "add", "arguments": {"a": 20, "b": 22}},
            {"name": None, "content": "42"},
        ]
    )
    run_agent(llm, make_tools(), "add them")
    second_prompt = llm.calls[1]["prompt"]
    assert "42" in second_prompt, f"the observation must appear in the next prompt, got {second_prompt!r}"
    assert "add them" in second_prompt, f"the original prompt must survive, got {second_prompt!r}"


def test_unknown_tool_does_not_crash():
    llm = MockLLM(
        tool_calls=[
            {"name": "teleport", "arguments": {}},
            {"name": None, "content": "sorry"},
        ]
    )
    out = run_agent(llm, make_tools(), "do the impossible")
    assert out["stopped"] == "final", f"expected the loop to continue, got {out!r}"
    observation = out["trace"][0]["observation"]
    assert "unknown" in observation.lower(), f"expected an 'unknown tool' observation, got {observation!r}"


def test_tool_exception_becomes_an_observation():
    llm = MockLLM(
        tool_calls=[
            {"name": "boom", "arguments": {}},
            {"name": None, "content": "recovered"},
        ]
    )
    out = run_agent(llm, make_tools(), "break something")
    assert out["answer"] == "recovered", f"the loop must survive the exception, got {out!r}"
    observation = out["trace"][0]["observation"]
    assert "tool exploded" in observation, f"expected the error text in the observation, got {observation!r}"


def test_recovers_after_a_bad_call():
    llm = MockLLM(
        tool_calls=[
            {"name": "boom", "arguments": {}},
            {"name": "add", "arguments": {"a": 1, "b": 1}},
            {"name": None, "content": "2"},
        ]
    )
    out = run_agent(llm, make_tools(), "try again")
    assert out["steps"] == 2, f"expected 2 steps, got {out['steps']!r}"
    assert out["trace"][1]["observation"] == "2", f"expected '2', got {out['trace'][1]['observation']!r}"


def test_observations_are_strings():
    llm = MockLLM(
        tool_calls=[
            {"name": "add", "arguments": {"a": 1, "b": 2}},
            {"name": None, "content": "3"},
        ]
    )
    out = run_agent(llm, make_tools(), "add")
    observation = out["trace"][0]["observation"]
    assert isinstance(observation, str), f"expected a str, got {type(observation).__name__}"


def test_tool_names_are_offered_to_the_model():
    llm = MockLLM(tool_calls=[{"name": None, "content": "hi"}])
    run_agent(llm, make_tools(), "hello")
    offered = llm.calls[0]["tools"]
    assert offered is not None, "the model must be told which tools exist"
    assert set(offered) == {"search", "add", "boom"}, f"expected the three tool names, got {offered!r}"


def test_steps_matches_trace_length():
    llm = MockLLM(tool_calls=[{"name": "add", "arguments": {"a": 1, "b": 1}}] * 4)
    out = run_agent(llm, make_tools(), "count", max_steps=4)
    assert out["steps"] == len(out["trace"]), f"steps {out['steps']!r} != len(trace) {len(out['trace'])}"
