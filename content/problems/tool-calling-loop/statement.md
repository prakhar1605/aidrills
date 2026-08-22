An agent is a while loop. Strip away the framework and what remains is: ask the
model, run the tool it named, feed the result back, repeat until it stops asking —
with a budget, because otherwise it will not stop.

Implement `run_agent(llm, tools, prompt, max_steps=5)`.

`tools` maps a tool name to a callable. `llm.tool_call(transcript, tool_names)`
returns a dict. A dict whose `name` is `None` is the model's final answer and
carries `content`; otherwise it carries `name` and an `arguments` dict.

Return a dict with four keys:

- `answer` — the final answer string, or `None` if the budget ran out.
- `steps` — how many tools were actually executed.
- `trace` — one dict per executed tool, with keys `tool`, `arguments`,
  `observation`.
- `stopped` — `"final"` or `"budget"`.

Rules:

- Consult the model at most `max_steps` times.
- Feed every observation back: each model call must see the observations from all
  the earlier steps.
- Observations are strings. Convert whatever the tool returned with `str`.
- A tool the model invents must not crash the loop. Record an observation saying
  the tool is unknown and keep going.
- A tool that raises must not crash the loop either. Record the error as the
  observation and keep going.

### What the interviewer is checking

The budget, and that it is a budget on *model calls*, not a `while True` with a
prayer. Then the two failure paths — hallucinated tool names and exceptions inside
tools — because an agent that dies on the first bad tool name is not an agent. The
subtle one is feeding errors back as observations rather than raising: that is what
lets the model recover on the next turn, and it is the single biggest difference
between a demo and something that runs unattended.
