import json
import re


def parse_react(text: str) -> dict:
    """Parse one ReAct-formatted model turn.

    Args:
        text: the raw completion.

    Returns:
        An action dict or a final-answer dict.

    Raises:
        ValueError: if the text has neither an Action nor a Final Answer.
    """
    raise NotImplementedError
