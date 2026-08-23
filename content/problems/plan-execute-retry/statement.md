The alternative to a ReAct loop: have the model emit the whole plan up front, then
execute it yourself. You get to validate before anything runs, retry individual
steps, and stop cleanly when one of them will not work — none of which you can do
when the model decides each step as it goes.

Implement `run_plan(plan, tools, max_attempts=2)`.

A step is `{"id": str, "tool": str, "args": dict}`. Any argument whose value is a
string starting with `$` is a reference to an earlier step's result: `"$fetch"`
becomes `results["fetch"]`. `"$$"` at the front escapes to a literal `$`.

**Validate the whole plan first.** Nothing executes until it passes. Raise
`ValueError` on a duplicate id, a tool that is not in `tools`, or a reference to an
id that is unknown or defined later.

Then execute in order:

- Call `tools[step["tool"]](**resolved_args)`.
- On an exception, retry that step up to `max_attempts` calls in total.
- If a step exhausts its attempts, stop. Later steps do not run.

Return:

```python
{
  "status": "ok" | "failed",
  "results": {step_id: value},      # successful steps only
  "attempts": {step_id: int},       # steps that were actually tried
  "failed_step": str | None,
  "error": str | None,              # str() of the last exception
}
```

An empty plan succeeds with nothing in it.

### What the interviewer is checking

That validation is a separate pass. A plan that half-executes and *then* discovers
step four references a typo has already sent the email in step two — the whole
argument for planning ahead is that you can reject the plan before it does anything.
After that, whether `attempts` distinguishes "never ran" from "ran and failed",
because that is the difference between a retryable failure and a bug in the plan.
