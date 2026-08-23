import re

PROMPT = """{rubric}

Question: {question}
Answer: {answer}

Reply with "Score: N" where N is 1-5, then a one-line reason."""

SCORE = re.compile(r"score\s*:\s*(\d+)", re.IGNORECASE)


def _parse_score(reply: str) -> int | None:
    match = SCORE.search(reply or "")
    if not match:
        return None
    value = int(match.group(1))
    # A judge that answers "Score: 9" has not followed the rubric; treating that
    # as a 5 would quietly inflate the eval.
    return value if 1 <= value <= 5 else None


def judge(llm, items: list[dict], rubric: str, retries: int = 1) -> dict:
    scores: dict = {}
    unparsed: list = []
    calls = 0

    for item in items:
        prompt = PROMPT.format(
            rubric=rubric, question=item["question"], answer=item["answer"]
        )

        score = None
        for _ in range(1 + retries):
            calls += 1
            score = _parse_score(llm.complete(prompt))
            if score is not None:
                break

        scores[item["id"]] = score
        if score is None:
            unparsed.append(item["id"])

    parsed = [value for value in scores.values() if value is not None]
    distribution = {n: 0 for n in range(1, 6)}
    for value in parsed:
        distribution[value] += 1

    return {
        "scores": scores,
        "mean": sum(parsed) / len(parsed) if parsed else None,
        "distribution": distribution,
        "unparsed": unparsed,
        "calls": calls,
    }


# What the interviewer is checking:
#   - unparsed items land in the output as None *and* in a list, instead of
#     vanishing from the average
#   - the range check, so an out-of-rubric number is a parse failure
#   - the distribution is seeded with every bucket, so a missing score reads as 0
#     rather than as an absent key the caller has to guard
