from mock_llm import count_tokens

PROMPT = """Summarize the conversation so far, preserving facts, decisions and open questions.

Previous summary:
{summary}

Conversation:
{transcript}"""


class WindowMemory:
    def __init__(self, llm, max_tokens: int, keep_recent: int = 2) -> None:
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if keep_recent < 0:
            raise ValueError("keep_recent must not be negative")

        self.llm = llm
        self.max_tokens = max_tokens
        self.keep_recent = keep_recent
        self._messages: list[dict] = []
        self._summary: str | None = None

    @property
    def summary(self) -> str | None:
        return self._summary

    def total_tokens(self) -> int:
        total = count_tokens(self._summary) if self._summary else 0
        return total + sum(count_tokens(message["content"]) for message in self._messages)

    def messages(self) -> list[dict]:
        head = [{"role": "system", "content": self._summary}] if self._summary else []
        return head + list(self._messages)

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        if self.total_tokens() > self.max_tokens:
            self._compact()

    def _compact(self) -> None:
        # keep_recent == 0 has to be spelled out: messages[:-0] is empty and
        # messages[-0:] is the whole list, so both slices invert at zero.
        if self.keep_recent == 0:
            folding, keeping = list(self._messages), []
        else:
            folding = self._messages[: -self.keep_recent]
            keeping = self._messages[-self.keep_recent :]

        if not folding:
            return  # the budget cannot fit even the recent turns; not an error

        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in folding)
        prompt = PROMPT.format(summary=self._summary or "(none)", transcript=transcript)

        self._summary = self.llm.complete(prompt)
        self._messages = keeping


# What the interviewer is checking:
#   - the previous summary is fed back in, so compaction is cumulative rather
#     than a rolling amnesia
#   - exactly one llm.complete per overflow; a loop here is a latency spike on
#     the turn that happens to cross the boundary
#   - the keep_recent == 0 special case
#   - an unfoldable window returns quietly instead of raising or looping
