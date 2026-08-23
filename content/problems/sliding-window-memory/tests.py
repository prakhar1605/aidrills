from mock_llm import MockLLM, count_tokens

from submission import *


def make(max_tokens=20, keep_recent=2, reply="SUMMARY"):
    return WindowMemory(MockLLM(responses={"*": reply}), max_tokens, keep_recent)


def test_starts_empty():
    memory = make()
    assert memory.messages() == [], f"expected [], got {memory.messages()!r}"
    assert memory.summary is None, f"expected None, got {memory.summary!r}"
    assert memory.total_tokens() == 0, f"expected 0, got {memory.total_tokens()!r}"


def test_add_appends():
    memory = make(max_tokens=1000)
    memory.add("user", "hello there")
    memory.add("assistant", "hi")
    exp = [
        {"role": "user", "content": "hello there"},
        {"role": "assistant", "content": "hi"},
    ]
    assert memory.messages() == exp, f"expected {exp!r}, got {memory.messages()!r}"


def test_no_summarization_under_budget():
    memory = make(max_tokens=1000)
    for i in range(5):
        memory.add("user", f"message number {i}")
    assert memory.summary is None, f"expected no summary, got {memory.summary!r}"
    assert memory.llm.call_count == 0, f"the model must not be called, saw {memory.llm.call_count}"


def test_total_tokens_matches_count_tokens():
    memory = make(max_tokens=1000)
    memory.add("user", "one two three")
    exp = count_tokens("one two three")
    assert memory.total_tokens() == exp, f"expected {exp!r}, got {memory.total_tokens()!r}"


def test_overflow_triggers_exactly_one_call():
    memory = make(max_tokens=5, keep_recent=1)
    memory.add("user", "alpha beta gamma")
    memory.add("user", "delta epsilon zeta")
    assert memory.llm.call_count == 1, f"expected exactly 1 model call, saw {memory.llm.call_count}"
    assert memory.summary == "SUMMARY", f"expected the reply as the summary, got {memory.summary!r}"


def test_only_keep_recent_messages_survive():
    memory = make(max_tokens=5, keep_recent=1)
    memory.add("user", "alpha beta gamma")
    memory.add("user", "delta epsilon zeta")
    retained = [m for m in memory.messages() if m["role"] != "system"]
    assert len(retained) == 1, f"expected 1 retained message, got {retained!r}"
    assert retained[0]["content"] == "delta epsilon zeta", f"the newest turn must survive, got {retained!r}"


def test_summary_leads_as_a_system_message():
    memory = make(max_tokens=5, keep_recent=1)
    memory.add("user", "alpha beta gamma")
    memory.add("user", "delta epsilon zeta")
    first = memory.messages()[0]
    assert first["role"] == "system", f"expected a leading system message, got {first!r}"
    assert first["content"] == "SUMMARY", f"expected the summary, got {first!r}"


def test_folded_content_reaches_the_prompt():
    memory = make(max_tokens=5, keep_recent=1)
    memory.add("user", "alpha beta gamma")
    memory.add("user", "delta epsilon zeta")
    prompt = memory.llm.calls[0]["prompt"]
    assert "alpha beta gamma" in prompt, f"the folded turn must be summarized, got {prompt!r}"


def test_first_compaction_says_no_previous_summary():
    memory = make(max_tokens=5, keep_recent=1)
    memory.add("user", "alpha beta gamma")
    memory.add("user", "delta epsilon zeta")
    assert "(none)" in memory.llm.calls[0]["prompt"], "the first compaction has no previous summary"


def test_previous_summary_is_carried_forward():
    memory = WindowMemory(MockLLM(responses={"*": "RECAP"}), max_tokens=5, keep_recent=1)
    for content in ("alpha beta gamma", "delta epsilon zeta", "eta theta iota"):
        memory.add("user", content)
    assert memory.llm.call_count >= 2, f"expected at least 2 compactions, saw {memory.llm.call_count}"
    second = memory.llm.calls[1]["prompt"]
    assert "RECAP" in second, f"the earlier summary must be fed back in, got {second!r}"


def test_summary_counts_against_the_budget():
    memory = make(max_tokens=5, keep_recent=1)
    memory.add("user", "alpha beta gamma")
    memory.add("user", "delta epsilon zeta")
    expected = count_tokens("SUMMARY") + count_tokens("delta epsilon zeta")
    assert memory.total_tokens() == expected, f"expected {expected!r}, got {memory.total_tokens()!r}"


def test_keep_recent_zero_folds_everything():
    memory = make(max_tokens=4, keep_recent=0)
    memory.add("user", "alpha beta gamma")
    memory.add("user", "delta epsilon zeta")
    retained = [m for m in memory.messages() if m["role"] != "system"]
    assert retained == [], f"keep_recent=0 must retain nothing verbatim, got {retained!r}"
    assert memory.summary == "SUMMARY", f"expected a summary, got {memory.summary!r}"


def test_unfoldable_window_is_not_an_error():
    # keep_recent=2 with only two messages leaves nothing to fold.
    memory = make(max_tokens=1, keep_recent=2)
    memory.add("user", "alpha beta gamma delta")
    memory.add("user", "epsilon zeta eta theta")
    assert memory.llm.call_count == 0, f"there is nothing to fold, saw {memory.llm.call_count} calls"
    assert len(memory.messages()) == 2, f"expected both messages kept, got {memory.messages()!r}"


def test_roles_are_preserved():
    memory = make(max_tokens=1000)
    memory.add("user", "q")
    memory.add("assistant", "a")
    assert [m["role"] for m in memory.messages()] == ["user", "assistant"], (
        f"roles must survive, got {memory.messages()!r}"
    )


def test_invalid_construction_raises():
    for kwargs in ({"max_tokens": 0}, {"max_tokens": 10, "keep_recent": -1}):
        try:
            WindowMemory(MockLLM(), **kwargs)
        except ValueError:
            continue
        raise AssertionError(f"WindowMemory({kwargs!r}) must raise ValueError")
