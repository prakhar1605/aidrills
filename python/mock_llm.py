"""A pure-Python fake LLM so RAG / agent / eval drills are testable offline.

No network, no API key, no third-party imports. Ships into the Pyodide
filesystem so it behaves identically in the browser and under pytest.

    from mock_llm import MockLLM, RateLimitError, count_tokens
"""

from __future__ import annotations

import re
import time
from typing import Any, Callable, Iterator


class LLMError(Exception):
    """Base class for every error a MockLLM can raise."""


class RateLimitError(LLMError):
    """Raised when the provider rejects the call with a 429."""

    status_code = 429


class ServerError(LLMError):
    """Raised when the provider returns a 5xx."""

    status_code = 500


def count_tokens(text: str) -> int:
    """Deterministic token approximation: words and punctuation each count once.

    Not a real BPE count, but stable across runs and close enough for
    budget/cost drills.
    """
    if not text:
        return 0
    return len(re.findall(r"\w+|[^\w\s]", text))


class MockLLM:
    """A scripted LLM.

    responses:     substring of the prompt -> reply. "*" is the fallback.
    fail_on_call:  1-indexed call numbers that raise instead of returning.
    error:         the exception class raised by fail_on_call.
    latency_ms:    simulated latency, applied per call.
    tool_calls:    scripted results for tool_call(), consumed in order.
    """

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        fail_on_call: list[int] | None = None,
        latency_ms: int = 0,
        tool_calls: list[dict[str, Any]] | None = None,
        error: type[Exception] = RateLimitError,
    ) -> None:
        self.responses = dict(responses or {"*": "ok"})
        self.fail_on_call = set(fail_on_call or [])
        self.latency_ms = latency_ms
        self.error = error
        self._tool_script = list(tool_calls or [])
        self._tool_index = 0
        self.calls: list[dict[str, Any]] = []

    # -- internals ---------------------------------------------------------

    def _record(self, kind: str, prompt: str, **extra: Any) -> int:
        n = len(self.calls) + 1
        self.calls.append({"n": n, "kind": kind, "prompt": prompt, **extra})
        if self.latency_ms:
            time.sleep(self.latency_ms / 1000.0)
        if n in self.fail_on_call:
            raise self.error(f"{self.error.__name__} on call {n}")
        return n

    def _reply(self, prompt: str) -> str:
        for key, value in self.responses.items():
            if key != "*" and key in prompt:
                return value
        return self.responses.get("*", "ok")

    # -- public API --------------------------------------------------------

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Return the scripted reply for `prompt`."""
        self._record("complete", prompt, **kwargs)
        return self._reply(prompt)

    def stream(self, prompt: str, **kwargs: Any) -> Iterator[str]:
        """Yield the scripted reply one whitespace-separated token at a time."""
        self._record("stream", prompt, **kwargs)
        reply = self._reply(prompt)
        parts = reply.split()
        for i, part in enumerate(parts):
            yield part if i == 0 else " " + part

    def tool_call(self, prompt: str, tools: list[Any] | None = None) -> dict[str, Any]:
        """Return the next scripted tool call.

        Each result is a dict. A result whose "name" is None (or missing) is a
        final answer and carries "content" instead of "arguments".
        """
        self._record("tool_call", prompt, tools=tools)
        if self._tool_index < len(self._tool_script):
            step = dict(self._tool_script[self._tool_index])
            self._tool_index += 1
        else:
            step = {"name": None, "content": self._reply(prompt)}
        step.setdefault("name", None)
        if step["name"] is None:
            step.setdefault("content", self._reply(prompt))
        else:
            step.setdefault("arguments", {})
        return step

    # -- assertion helpers -------------------------------------------------

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def prompts(self) -> list[str]:
        return [c["prompt"] for c in self.calls]

    def reset(self) -> None:
        self.calls.clear()
        self._tool_index = 0


def flaky(
    succeed_on: int,
    error: type[Exception] = RateLimitError,
    result: Any = "ok",
) -> Callable[[], Any]:
    """A zero-arg callable that raises until its `succeed_on`-th invocation."""
    state = {"n": 0}

    def call() -> Any:
        state["n"] += 1
        if state["n"] < succeed_on:
            raise error(f"attempt {state['n']} failed")
        return result

    call.attempts = state  # type: ignore[attr-defined]
    return call
