from mock_llm import RateLimitError, flaky

from submission import *


def make_tools(log=None):
    def fetch(url):
        if log is not None:
            log.append(("fetch", url))
        return f"body of {url}"

    def upper(text):
        return text.upper()

    def boom():
        raise RuntimeError("tool exploded")

    return {"fetch": fetch, "upper": upper, "boom": boom}


def test_empty_plan():
    out = run_plan([], make_tools())
    assert out["status"] == "ok", f"expected 'ok', got {out['status']!r}"
    assert out["results"] == {}, f"expected no results, got {out['results']!r}"
    assert out["attempts"] == {}, f"expected no attempts, got {out['attempts']!r}"


def test_single_step():
    plan = [{"id": "a", "tool": "fetch", "args": {"url": "x"}}]
    out = run_plan(plan, make_tools())
    assert out["status"] == "ok", f"expected 'ok', got {out['status']!r}"
    assert out["results"]["a"] == "body of x", f"got {out['results']!r}"


def test_reference_resolves_an_earlier_result():
    plan = [
        {"id": "a", "tool": "fetch", "args": {"url": "x"}},
        {"id": "b", "tool": "upper", "args": {"text": "$a"}},
    ]
    out = run_plan(plan, make_tools())
    assert out["results"]["b"] == "BODY OF X", f"expected the resolved reference, got {out['results']!r}"


def test_literal_dollar_is_escaped():
    plan = [{"id": "a", "tool": "upper", "args": {"text": "$$cost"}}]
    out = run_plan(plan, make_tools())
    assert out["results"]["a"] == "$COST", f"expected '$COST', got {out['results']!r}"


def test_plain_strings_pass_through():
    log = []
    plan = [{"id": "a", "tool": "fetch", "args": {"url": "https://example.com"}}]
    run_plan(plan, make_tools(log))
    assert log == [("fetch", "https://example.com")], f"got {log!r}"


def test_attempts_counted_on_success():
    plan = [{"id": "a", "tool": "fetch", "args": {"url": "x"}}]
    out = run_plan(plan, make_tools())
    assert out["attempts"] == {"a": 1}, f"expected one attempt, got {out['attempts']!r}"


def test_retry_then_succeed():
    tools = make_tools()
    tools["flaky"] = flaky(succeed_on=2, result="recovered")
    plan = [{"id": "a", "tool": "flaky", "args": {}}]
    out = run_plan(plan, tools, max_attempts=3)
    assert out["status"] == "ok", f"expected 'ok', got {out['status']!r}"
    assert out["results"]["a"] == "recovered", f"got {out['results']!r}"
    assert out["attempts"]["a"] == 2, f"expected 2 attempts, got {out['attempts']!r}"


def test_exhausted_attempts_fail_the_plan():
    plan = [{"id": "a", "tool": "boom", "args": {}}]
    out = run_plan(plan, make_tools(), max_attempts=3)
    assert out["status"] == "failed", f"expected 'failed', got {out['status']!r}"
    assert out["failed_step"] == "a", f"expected 'a', got {out['failed_step']!r}"
    assert out["attempts"]["a"] == 3, f"expected 3 attempts, got {out['attempts']!r}"
    assert "tool exploded" in out["error"], f"expected the exception text, got {out['error']!r}"


def test_max_attempts_one_does_not_retry():
    plan = [{"id": "a", "tool": "boom", "args": {}}]
    out = run_plan(plan, make_tools(), max_attempts=1)
    assert out["attempts"]["a"] == 1, f"expected 1 attempt, got {out['attempts']!r}"


def test_later_steps_do_not_run_after_a_failure():
    log = []
    plan = [
        {"id": "a", "tool": "boom", "args": {}},
        {"id": "b", "tool": "fetch", "args": {"url": "x"}},
    ]
    out = run_plan(plan, make_tools(log), max_attempts=1)
    assert "b" not in out["attempts"], f"step b must not be attempted, got {out['attempts']!r}"
    assert log == [], f"no later tool may run, got {log!r}"


def test_earlier_results_survive_a_failure():
    plan = [
        {"id": "a", "tool": "fetch", "args": {"url": "x"}},
        {"id": "b", "tool": "boom", "args": {}},
    ]
    out = run_plan(plan, make_tools(), max_attempts=1)
    assert out["results"]["a"] == "body of x", f"the successful step must be reported, got {out['results']!r}"
    assert "b" not in out["results"], f"the failed step must not be in results, got {out['results']!r}"


def test_success_reports_no_failure():
    plan = [{"id": "a", "tool": "fetch", "args": {"url": "x"}}]
    out = run_plan(plan, make_tools())
    assert out["failed_step"] is None, f"expected None, got {out['failed_step']!r}"
    assert out["error"] is None, f"expected None, got {out['error']!r}"


def test_duplicate_id_raises():
    plan = [
        {"id": "a", "tool": "fetch", "args": {"url": "x"}},
        {"id": "a", "tool": "fetch", "args": {"url": "y"}},
    ]
    try:
        run_plan(plan, make_tools())
    except ValueError:
        return
    raise AssertionError("a duplicate step id must raise ValueError")


def test_unknown_tool_raises():
    plan = [{"id": "a", "tool": "teleport", "args": {}}]
    try:
        run_plan(plan, make_tools())
    except ValueError:
        return
    raise AssertionError("an unknown tool must raise ValueError")


def test_unknown_reference_raises():
    plan = [{"id": "a", "tool": "upper", "args": {"text": "$ghost"}}]
    try:
        run_plan(plan, make_tools())
    except ValueError:
        return
    raise AssertionError("a reference to an unknown id must raise ValueError")


def test_forward_reference_raises():
    plan = [
        {"id": "a", "tool": "upper", "args": {"text": "$b"}},
        {"id": "b", "tool": "fetch", "args": {"url": "x"}},
    ]
    try:
        run_plan(plan, make_tools())
    except ValueError:
        return
    raise AssertionError("a forward reference must raise ValueError")


def test_validation_runs_before_any_execution():
    log = []
    plan = [
        {"id": "a", "tool": "fetch", "args": {"url": "x"}},
        {"id": "b", "tool": "upper", "args": {"text": "$ghost"}},
    ]
    try:
        run_plan(plan, make_tools(log))
    except ValueError:
        assert log == [], f"nothing may execute before the plan validates, got {log!r}"
        return
    raise AssertionError("the bad reference must raise ValueError")


def test_missing_args_key_is_allowed():
    plan = [{"id": "a", "tool": "boom"}]
    out = run_plan(plan, make_tools(), max_attempts=1)
    assert out["failed_step"] == "a", f"the step must still run, got {out!r}"
