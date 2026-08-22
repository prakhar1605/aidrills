from typing import Any, Callable


def run_agent(
    llm: Any,
    tools: dict[str, Callable[..., Any]],
    prompt: str,
    max_steps: int = 5,
) -> dict[str, Any]:
    transcript = prompt
    trace: list[dict[str, Any]] = []

    for _ in range(max_steps):
        step = llm.tool_call(transcript, list(tools))
        name = step.get("name")

        if name is None:
            return {
                "answer": step.get("content"),
                "steps": len(trace),
                "trace": trace,
                "stopped": "final",
            }

        arguments = step.get("arguments") or {}
        if name not in tools:
            # A hallucinated tool name is data, not an exception -- tell the
            # model what it did wrong and let it try again.
            observation = f"error: unknown tool {name!r}. available: {sorted(tools)}"
        else:
            try:
                observation = str(tools[name](**arguments))
            except Exception as exc:
                observation = f"error: {type(exc).__name__}: {exc}"

        trace.append({"tool": name, "arguments": arguments, "observation": observation})
        transcript += f"\n{name}({arguments}) -> {observation}"

    return {"answer": None, "steps": len(trace), "trace": trace, "stopped": "budget"}


# What the interviewer is checking:
#   - `for _ in range(max_steps)` rather than an unbounded while
#   - the transcript grows, so step 3 can use what step 1 discovered
#   - both failure paths land in `observation`; neither escapes the loop
#   - `stopped` is explicit, so the caller can tell "it answered" from
#     "it gave up", which a bare `answer=None` cannot express
