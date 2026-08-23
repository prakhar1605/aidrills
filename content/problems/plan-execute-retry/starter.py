from typing import Any, Callable


def run_plan(
    plan: list[dict],
    tools: dict[str, Callable[..., Any]],
    max_attempts: int = 2,
) -> dict:
    """Validate a plan, then execute it step by step with bounded retries.

    Args:
        plan: steps with an id, a tool name and args.
        tools: tool name -> callable.
        max_attempts: total calls allowed per step.

    Returns:
        A dict with status, results, attempts, failed_step and error.

    Raises:
        ValueError: on a duplicate id, an unknown tool, or a bad reference.
    """
    raise NotImplementedError
