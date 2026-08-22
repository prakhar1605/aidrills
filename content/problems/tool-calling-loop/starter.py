from typing import Any, Callable


def run_agent(
    llm: Any,
    tools: dict[str, Callable[..., Any]],
    prompt: str,
    max_steps: int = 5,
) -> dict[str, Any]:
    """Run a tool-calling agent loop until it answers or runs out of budget.

    Args:
        llm: object exposing tool_call(transcript, tool_names) -> dict.
        tools: tool name -> callable.
        prompt: the user's request.
        max_steps: maximum number of model calls.

    Returns:
        A dict with keys "answer", "steps", "trace", "stopped".
    """
    raise NotImplementedError
