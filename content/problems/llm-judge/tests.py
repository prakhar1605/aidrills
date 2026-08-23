from mock_llm import MockLLM

from submission import *

RUBRIC = "Grade the answer for factual accuracy on a 1-5 scale."

ITEMS = [
    {"id": "q1", "question": "capital of France", "answer": "Paris"},
    {"id": "q2", "question": "capital of Japan", "answer": "Osaka"},
]


class ScriptedLLM:
    """Returns a different reply per call, which MockLLM cannot do."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def complete(self, prompt):
        self.calls.append(prompt)
        return self.replies.pop(0) if self.replies else "no score here"


def test_no_items():
    out = judge(MockLLM(), [], RUBRIC)
    assert out["scores"] == {}, f"expected no scores, got {out['scores']!r}"
    assert out["mean"] is None, f"expected None, got {out['mean']!r}"
    assert out["unparsed"] == [], f"expected [], got {out['unparsed']!r}"
    assert out["distribution"] == {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}, f"got {out['distribution']!r}"
    assert out["calls"] == 0, f"expected 0 calls, got {out['calls']!r}"


def test_parses_scores():
    llm = MockLLM(responses={"France": "Score: 5\nCorrect.", "*": "Score: 1\nWrong."})
    out = judge(llm, ITEMS, RUBRIC)
    exp = {"q1": 5, "q2": 1}
    assert out["scores"] == exp, f"expected {exp!r}, got {out['scores']!r}"


def test_mean_of_parsed_scores():
    llm = MockLLM(responses={"France": "Score: 5", "*": "Score: 1"})
    out = judge(llm, ITEMS, RUBRIC)
    assert out["mean"] == 3.0, f"expected 3.0, got {out['mean']!r}"


def test_distribution():
    llm = MockLLM(responses={"France": "Score: 5", "*": "Score: 1"})
    out = judge(llm, ITEMS, RUBRIC)
    exp = {1: 1, 2: 0, 3: 0, 4: 0, 5: 1}
    assert out["distribution"] == exp, f"expected {exp!r}, got {out['distribution']!r}"


def test_rubric_and_content_reach_the_prompt():
    llm = MockLLM(responses={"*": "Score: 3"})
    judge(llm, ITEMS[:1], RUBRIC)
    prompt = llm.calls[0]["prompt"]
    for fragment in (RUBRIC, "capital of France", "Paris"):
        assert fragment in prompt, f"expected {fragment!r} in the prompt, got {prompt!r}"


def test_score_is_case_insensitive():
    llm = MockLLM(responses={"*": "score: 4 — solid"})
    out = judge(llm, ITEMS[:1], RUBRIC)
    assert out["scores"]["q1"] == 4, f"expected 4, got {out['scores']!r}"


def test_score_embedded_in_prose():
    llm = MockLLM(responses={"*": "After considering the rubric, Score: 2. It misses detail."})
    out = judge(llm, ITEMS[:1], RUBRIC)
    assert out["scores"]["q1"] == 2, f"expected 2, got {out['scores']!r}"


def test_unparseable_reply_is_reported():
    llm = MockLLM(responses={"*": "This answer seems fine to me."})
    out = judge(llm, ITEMS[:1], RUBRIC, retries=0)
    assert out["scores"]["q1"] is None, f"expected None, got {out['scores']!r}"
    assert out["unparsed"] == ["q1"], f"expected ['q1'], got {out['unparsed']!r}"


def test_unparsed_items_are_excluded_from_the_mean():
    llm = ScriptedLLM(["Score: 4", "no number at all"])
    out = judge(llm, ITEMS, RUBRIC, retries=0)
    assert out["mean"] == 4.0, f"the mean must ignore unparsed items: expected 4.0, got {out['mean']!r}"
    assert out["unparsed"] == ["q2"], f"expected ['q2'], got {out['unparsed']!r}"


def test_out_of_range_score_does_not_parse():
    llm = MockLLM(responses={"*": "Score: 9"})
    out = judge(llm, ITEMS[:1], RUBRIC, retries=0)
    assert out["scores"]["q1"] is None, f"9 is outside 1-5: expected None, got {out['scores']!r}"


def test_zero_does_not_parse():
    llm = MockLLM(responses={"*": "Score: 0"})
    out = judge(llm, ITEMS[:1], RUBRIC, retries=0)
    assert out["scores"]["q1"] is None, f"0 is outside 1-5: expected None, got {out['scores']!r}"


def test_retries_are_used():
    llm = MockLLM(responses={"*": "nope"})
    out = judge(llm, ITEMS[:1], RUBRIC, retries=2)
    assert out["calls"] == 3, f"expected 1 + 2 calls, got {out['calls']!r}"


def test_a_retry_can_recover():
    llm = ScriptedLLM(["waffle", "Score: 3"])
    out = judge(llm, ITEMS[:1], RUBRIC, retries=1)
    assert out["scores"]["q1"] == 3, f"the retry must be used: expected 3, got {out['scores']!r}"
    assert out["unparsed"] == [], f"expected [], got {out['unparsed']!r}"


def test_no_retry_after_a_success():
    llm = MockLLM(responses={"*": "Score: 3"})
    out = judge(llm, ITEMS, RUBRIC, retries=3)
    assert out["calls"] == 2, f"one call per item when it parses: expected 2, got {out['calls']!r}"


def test_mean_is_none_when_nothing_parses():
    llm = MockLLM(responses={"*": "no score"})
    out = judge(llm, ITEMS, RUBRIC, retries=0)
    assert out["mean"] is None, f"expected None, got {out['mean']!r}"
    assert out["unparsed"] == ["q1", "q2"], f"expected both ids in order, got {out['unparsed']!r}"


def test_every_item_appears_in_scores():
    llm = ScriptedLLM(["Score: 1", "garbage"])
    out = judge(llm, ITEMS, RUBRIC, retries=0)
    assert set(out["scores"]) == {"q1", "q2"}, f"expected both ids, got {sorted(out['scores'])!r}"
