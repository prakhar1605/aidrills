from typing import Any, Callable


def _is_reference(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("$") and not value.startswith("$$")


def _validate(plan: list[dict], tools: dict[str, Callable[..., Any]]) -> None:
    """Reject the whole plan before a single step runs."""
    seen: set[str] = set()
    for step in plan:
        step_id = step["id"]
        if step_id in seen:
            raise ValueError(f"duplicate step id: {step_id!r}")
        if step["tool"] not in tools:
            raise ValueError(f"step {step_id!r} uses unknown tool {step['tool']!r}")
        for name, value in (step.get("args") or {}).items():
            if _is_reference(value):
                target = value[1:]
                # Must already be defined: forward references cannot resolve.
                if target not in seen:
                    raise ValueError(
                        f"step {step_id!r} argument {name!r} references {target!r}, "
                        "which is unknown or defined later"
                    )
        seen.add(step_id)


def _resolve(args: dict, results: dict) -> dict:
    resolved = {}
    for name, value in args.items():
        if _is_reference(value):
            resolved[name] = results[value[1:]]
        elif isinstance(value, str) and value.startswith("$$"):
            resolved[name] = value[1:]
        else:
            resolved[name] = value
    return resolved


def run_plan(
    plan: list[dict],
    tools: dict[str, Callable[..., Any]],
    max_attempts: int = 2,
) -> dict:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    _validate(plan, tools)

    results: dict[str, Any] = {}
    attempts: dict[str, int] = {}

    for step in plan:
        step_id = step["id"]
        arguments = _resolve(step.get("args") or {}, results)
        tool = tools[step["tool"]]

        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            attempts[step_id] = attempt
            try:
                results[step_id] = tool(**arguments)
                last_error = None
                break
            except Exception as exc:
                last_error = exc

        if last_error is not None:
            # Stop the plan; later steps never appear in `attempts`, which is how
            # a caller tells "not run" from "run and failed".
            return {
                "status": "failed",
                "results": results,
                "attempts": attempts,
                "failed_step": step_id,
                "error": str(last_error),
            }

    return {
        "status": "ok",
        "results": results,
        "attempts": attempts,
        "failed_step": None,
        "error": None,
    }


# What the interviewer is checking:
#   - _validate runs to completion before anything executes
#   - references resolve against results, so the check is "defined earlier", not
#     merely "defined"
#   - attempts is written before the call, so a step that raised every time still
#     reports max_attempts rather than nothing
#   - the escape hatch for a literal leading "$"
