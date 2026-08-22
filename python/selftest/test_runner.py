"""Coverage for python/runner.py -- the browser-side test runner.

Named `selftest/` rather than `tests/` so nothing can shadow the `tests` module
the runner imports.
"""

import importlib
import json
import sys
from pathlib import Path

import pytest

PY_DIR = Path(__file__).resolve().parents[1]

PASSING_TESTS = """
from submission import *


def test_first():
    assert add(1, 2) == 3, "1 + 2"


def test_second():
    assert add(0, 0) == 0, "0 + 0"
"""


@pytest.fixture
def run_in_sandbox(tmp_path, monkeypatch):
    """Returns run(submission, tests) -> the runner's decoded payload."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(sys, "dont_write_bytecode", True)

    for name in ("runner.py", "mock_llm.py"):
        (tmp_path / name).write_text((PY_DIR / name).read_text())
    for name in ("runner", "tests", "submission", "mock_llm"):
        sys.modules.pop(name, None)
    importlib.invalidate_caches()

    def run(submission: str, tests: str = PASSING_TESTS) -> dict:
        (tmp_path / "submission.py").write_text(submission)
        (tmp_path / "tests.py").write_text(tests)
        import runner

        return json.loads(runner.run())

    yield run

    for name in ("runner", "tests", "submission", "mock_llm"):
        sys.modules.pop(name, None)


def test_payload_shape(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b): return a + b")
    assert set(payload) == {"results", "stdout"}
    for row in payload["results"]:
        assert set(row) == {"name", "status", "message", "durationMs"}


def test_all_passing(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b): return a + b")
    assert [row["status"] for row in payload["results"]] == ["passed", "passed"]
    assert all(row["message"] == "" for row in payload["results"])


def test_failed_assertion_keeps_its_message(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b): return 99")
    first = payload["results"][0]
    assert first["status"] == "failed"
    assert first["message"] == "1 + 2"


def test_bare_assertion_reports_the_source_line(run_in_sandbox):
    tests = "from submission import *\n\n\ndef test_bare():\n    assert add(1, 1) == 5\n"
    payload = run_in_sandbox("def add(a, b): return a + b", tests)
    assert payload["results"][0]["status"] == "failed"
    assert "add(1, 1) == 5" in payload["results"][0]["message"]


def test_exception_is_an_error_not_a_failure(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b): raise ValueError('nope')")
    first = payload["results"][0]
    assert first["status"] == "error"
    assert "ValueError" in first["message"]
    assert "nope" in first["message"]


def test_missing_name_is_reported_per_test(run_in_sandbox):
    payload = run_in_sandbox("x = 1")
    assert [row["status"] for row in payload["results"]] == ["error", "error"]
    assert "NameError" in payload["results"][0]["message"]


def test_syntax_error_collapses_to_one_collection_error(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b)\n    return a + b")
    assert len(payload["results"]) == 1
    assert payload["results"][0]["name"] == "collection"
    assert payload["results"][0]["status"] == "error"
    assert "SyntaxError" in payload["results"][0]["message"]


def test_no_test_functions(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b): return a + b", "from submission import *\n")
    assert len(payload["results"]) == 1
    assert payload["results"][0]["status"] == "error"
    assert "No test_" in payload["results"][0]["message"]


def test_stdout_is_captured_not_leaked(run_in_sandbox, capsys):
    tests = (
        "from submission import *\n\n\n"
        "def test_prints():\n"
        "    print('hello from the drill')\n"
        "    assert add(1, 1) == 2, 'sum'\n"
    )
    payload = run_in_sandbox("def add(a, b): return a + b", tests)
    assert "hello from the drill" in payload["stdout"]
    assert "hello from the drill" not in capsys.readouterr().out


def test_definition_order_is_preserved(run_in_sandbox):
    tests = (
        "from submission import *\n\n\n"
        "def test_zebra():\n    assert True, 'z'\n\n\n"
        "def test_apple():\n    assert True, 'a'\n"
    )
    payload = run_in_sandbox("def add(a, b): return a + b", tests)
    assert [row["name"] for row in payload["results"]] == ["test_zebra", "test_apple"]


def test_durations_are_reported(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b): return a + b")
    assert all(row["durationMs"] >= 0 for row in payload["results"])


def test_edited_submission_takes_effect_on_the_next_run(run_in_sandbox):
    first = run_in_sandbox("def add(a, b): return 99")
    assert first["results"][0]["status"] == "failed"

    second = run_in_sandbox("def add(a, b): return a + b")
    assert [row["status"] for row in second["results"]] == ["passed", "passed"], (
        "the runner must discard the cached submission module between runs"
    )


def test_mock_llm_is_importable_from_a_drill(run_in_sandbox):
    tests = (
        "from mock_llm import MockLLM\n"
        "from submission import *\n\n\n"
        "def test_uses_the_fake_llm():\n"
        "    llm = MockLLM(responses={'*': 'ok'})\n"
        "    assert reply(llm) == 'ok', 'scripted reply'\n"
    )
    payload = run_in_sandbox("def reply(llm): return llm.complete('anything')", tests)
    assert payload["results"][0]["status"] == "passed", payload["results"][0]["message"]


def test_traceback_is_trimmed(run_in_sandbox):
    payload = run_in_sandbox("def add(a, b): raise RuntimeError('deep')")
    message = payload["results"][0]["message"]
    assert "runner.py" not in message, "the runner's own frames must not appear"
    assert len(message) < 2000
