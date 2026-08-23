import re

PROMPT = """{rubric}

Question: {question}
Answer: {answer}

Reply with "Score: N" where N is 1-5, then a one-line reason."""


def judge(llm, items: list[dict], rubric: str, retries: int = 1) -> dict:
    """Score answers with an LLM judge and report what could not be parsed.

    Args:
        llm: object exposing complete(prompt) -> str.
        items: dicts with id, question and answer.
        rubric: the grading instructions, prepended to every prompt.
        retries: extra attempts per item when the reply does not parse.

    Returns:
        A dict with scores, mean, distribution, unparsed and calls.
    """
    raise NotImplementedError
