from mock_llm import count_tokens

PROMPT = """Summarize the conversation so far, preserving facts, decisions and open questions.

Previous summary:
{summary}

Conversation:
{transcript}"""


class WindowMemory:
    """Keeps recent turns verbatim and folds older ones into a summary."""

    def __init__(self, llm, max_tokens: int, keep_recent: int = 2) -> None:
        """
        Raises:
            ValueError: if max_tokens is below 1 or keep_recent is negative.
        """
        raise NotImplementedError

    def add(self, role: str, content: str) -> None:
        """Append a message, compacting if the budget is exceeded."""
        raise NotImplementedError

    def total_tokens(self) -> int:
        """Tokens in the summary plus every retained message."""
        raise NotImplementedError

    def messages(self) -> list[dict]:
        """The summary (as a system message) followed by the retained messages."""
        raise NotImplementedError

    @property
    def summary(self) -> str | None:
        raise NotImplementedError
