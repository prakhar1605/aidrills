"""The test runner that executes inside Pyodide.

The worker writes `submission.py` (the user's code) and `tests.py` (the
problem's cases) into the Pyodide filesystem, then calls `run()`. pytest is
never used in the browser -- the cases are plain `def test_*()` functions with
`assert`, so a ~100 line runner is enough and starts instantly.

Returns a JSON string:
    {"results": [{"name", "status", "message", "durationMs"}], "stdout": "..."}
    status in {"passed", "failed", "error"}
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import sys
import time
import traceback

MAX_FRAMES = 3
MAX_MESSAGE_CHARS = 2000


def _short_traceback(exc: BaseException) -> str:
    """Format `exc` with only the last few frames of user code."""
    tb = exc.__traceback__
    frames = traceback.extract_tb(tb)
    # Drop this runner's own frames -- the user cares about their code.
    frames = [f for f in frames if f.filename not in (__file__, "<runner>")]
    frames = frames[-MAX_FRAMES:]
    lines = []
    if frames:
        lines.append("Traceback (most recent call last):")
        lines.extend(traceback.format_list(frames))
    lines.extend(traceback.format_exception_only(type(exc), exc))
    return "".join(lines).strip()[:MAX_MESSAGE_CHARS]


def _assertion_message(exc: AssertionError) -> str:
    text = str(exc).strip()
    if text:
        return text[:MAX_MESSAGE_CHARS]
    # A bare `assert x == y` has no message -- show where it fired instead.
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename not in (__file__,)]
    if frames and frames[-1].line:
        return f"assertion failed: {frames[-1].line}"
    return "assertion failed"


def _fresh_import(name: str):
    """Import `name`, discarding any module cached by a previous run."""
    sys.modules.pop(name, None)
    importlib.invalidate_caches()
    return importlib.import_module(name)


def _collect(module) -> list[tuple[str, object]]:
    """Every `test_*` callable in the module, in definition order."""
    found = []
    for name, obj in vars(module).items():
        if name.startswith("test_") and callable(obj):
            line = getattr(getattr(obj, "__code__", None), "co_firstlineno", 0)
            found.append((line, name, obj))
    found.sort(key=lambda item: item[0])
    return [(name, obj) for _, name, obj in found]


def run() -> str:
    results: list[dict] = []
    buffer = io.StringIO()

    with contextlib.redirect_stdout(buffer):
        try:
            # tests.py does `from submission import *`, so submission must be
            # evicted first or an edited solution would not take effect.
            sys.modules.pop("submission", None)
            tests = _fresh_import("tests")
        except BaseException as exc:  # noqa: BLE001 -- surfaced to the user
            return json.dumps(
                {
                    "results": [
                        {
                            "name": "collection",
                            "status": "error",
                            "message": _short_traceback(exc),
                            "durationMs": 0,
                        }
                    ],
                    "stdout": buffer.getvalue(),
                }
            )

        cases = _collect(tests)
        if not cases:
            return json.dumps(
                {
                    "results": [
                        {
                            "name": "collection",
                            "status": "error",
                            "message": "No test_* functions found in tests.py",
                            "durationMs": 0,
                        }
                    ],
                    "stdout": buffer.getvalue(),
                }
            )

        for name, fn in cases:
            started = time.perf_counter()
            try:
                fn()
            except AssertionError as exc:
                status, message = "failed", _assertion_message(exc)
            except BaseException as exc:  # noqa: BLE001 -- surfaced to the user
                status, message = "error", _short_traceback(exc)
            else:
                status, message = "passed", ""
            results.append(
                {
                    "name": name,
                    "status": status,
                    "message": message,
                    "durationMs": round((time.perf_counter() - started) * 1000, 2),
                }
            )

    return json.dumps({"results": results, "stdout": buffer.getvalue()})
