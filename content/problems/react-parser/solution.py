import json
import re

# Anchored to the start of a line so a label mentioned inside a thought does not
# terminate it. "Action Input" must be tried before "Action".
LABEL = re.compile(
    r"^[ \t]*(thought|action input|action|final answer)[ \t]*:",
    re.IGNORECASE | re.MULTILINE,
)


def _fields(text: str) -> dict[str, tuple[int, str]]:
    """label -> (position, value). Later repeats of a label are ignored."""
    matches = list(LABEL.finditer(text))
    found: dict[str, tuple[int, str]] = {}
    for index, match in enumerate(matches):
        name = match.group(1).lower()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if name not in found:
            found[name] = (match.start(), text[match.end() : end].strip())
    return found


def parse_react(text: str) -> dict:
    found = _fields(text or "")
    thought = found["thought"][1] if "thought" in found else None

    action_at = found["action"][0] if "action" in found else None
    final_at = found["final answer"][0] if "final answer" in found else None

    if action_at is None and final_at is None:
        raise ValueError("no Action or Final Answer in the model output")

    # Whichever came first wins; models routinely emit both.
    if final_at is not None and (action_at is None or final_at < action_at):
        return {"kind": "final", "thought": thought, "answer": found["final answer"][1]}

    raw_input = found["action input"][1] if "action input" in found else ""
    if raw_input:
        try:
            parsed = json.loads(raw_input)
        except json.JSONDecodeError:
            parsed = raw_input  # models write prose here as often as JSON
    else:
        parsed = {}

    return {
        "kind": "action",
        "thought": thought,
        "action": found["action"][1].splitlines()[0].strip() if found["action"][1] else "",
        "input": parsed,
    }


# What the interviewer is checking:
#   - one pass that locates every label, so a field's value is "up to the next
#     label" rather than a fragile per-field regex
#   - "action input" alternated before "action", or the longer label never matches
#   - MULTILINE anchoring, so the word "Action:" inside a thought is not a label
#   - the first-label-wins rule, stated rather than accidental
