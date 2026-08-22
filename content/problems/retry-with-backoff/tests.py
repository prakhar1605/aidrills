from mock_llm import RateLimitError, ServerError, flaky

from submission import *


class Recorder:
    """Stands in for time.sleep and records what it was asked to wait."""

    def __init__(self):
        self.delays = []

    def __call__(self, seconds):
        self.delays.append(seconds)


def test_returns_immediately_on_success():
    sleeper = Recorder()
    out = call_with_retry(lambda: "done", sleep=sleeper, rand=lambda: 1.0)
    assert out == "done", f"expected 'done', got {out!r}"
    assert sleeper.delays == [], f"expected no sleeps, got {sleeper.delays!r}"


def test_retries_until_it_succeeds():
    sleeper = Recorder()
    fn = flaky(succeed_on=3, result=42)
    out = call_with_retry(fn, sleep=sleeper, rand=lambda: 1.0)
    assert out == 42, f"expected 42, got {out!r}"
    assert fn.attempts["n"] == 3, f"expected 3 calls, got {fn.attempts['n']}"


def test_backoff_schedule_doubles():
    sleeper = Recorder()
    call_with_retry(flaky(succeed_on=4), base_delay=0.5, sleep=sleeper, rand=lambda: 1.0)
    exp = [0.5, 1.0, 2.0]
    assert sleeper.delays == exp, f"expected {exp!r}, got {sleeper.delays!r}"


def test_delay_is_capped():
    sleeper = Recorder()
    call_with_retry(
        flaky(succeed_on=6),
        max_attempts=6,
        base_delay=1.0,
        max_delay=4.0,
        sleep=sleeper,
        rand=lambda: 1.0,
    )
    exp = [1.0, 2.0, 4.0, 4.0, 4.0]
    assert sleeper.delays == exp, f"expected {exp!r}, got {sleeper.delays!r}"


def test_full_jitter_scales_the_whole_wait():
    sleeper = Recorder()
    call_with_retry(flaky(succeed_on=4), base_delay=1.0, sleep=sleeper, rand=lambda: 0.25)
    exp = [0.25, 0.5, 1.0]
    assert sleeper.delays == exp, f"expected {exp!r}, got {sleeper.delays!r}"


def test_jitter_can_reach_zero():
    sleeper = Recorder()
    call_with_retry(flaky(succeed_on=3), sleep=sleeper, rand=lambda: 0.0)
    exp = [0.0, 0.0]
    assert sleeper.delays == exp, f"full jitter must allow 0, got {sleeper.delays!r}"


def test_gives_up_and_reraises():
    sleeper = Recorder()
    fn = flaky(succeed_on=99)
    try:
        call_with_retry(fn, max_attempts=3, sleep=sleeper, rand=lambda: 1.0)
    except RateLimitError:
        assert fn.attempts["n"] == 3, f"expected exactly 3 calls, got {fn.attempts['n']}"
        assert len(sleeper.delays) == 2, f"expected 2 sleeps for 3 attempts, got {sleeper.delays!r}"
        return
    raise AssertionError("exhausting the attempts must re-raise RateLimitError")


def test_no_sleep_after_the_final_failure():
    sleeper = Recorder()
    try:
        call_with_retry(flaky(succeed_on=99), max_attempts=1, sleep=sleeper, rand=lambda: 1.0)
    except RateLimitError:
        assert sleeper.delays == [], f"max_attempts=1 must never sleep, got {sleeper.delays!r}"
        return
    raise AssertionError("expected RateLimitError")


def test_server_errors_are_retried_too():
    sleeper = Recorder()
    fn = flaky(succeed_on=2, error=ServerError, result="recovered")
    out = call_with_retry(fn, sleep=sleeper, rand=lambda: 1.0)
    assert out == "recovered", f"expected 'recovered', got {out!r}"


def test_other_exceptions_are_not_retried():
    sleeper = Recorder()
    fn = flaky(succeed_on=99, error=ValueError)
    try:
        call_with_retry(fn, sleep=sleeper, rand=lambda: 1.0)
    except ValueError:
        assert fn.attempts["n"] == 1, f"a ValueError must not be retried, saw {fn.attempts['n']} calls"
        assert sleeper.delays == [], f"expected no sleeps, got {sleeper.delays!r}"
        return
    raise AssertionError("a ValueError must propagate immediately")


def test_never_sleeps_longer_than_max_delay():
    sleeper = Recorder()
    try:
        call_with_retry(
            flaky(succeed_on=99),
            max_attempts=10,
            base_delay=1.0,
            max_delay=3.0,
            sleep=sleeper,
            rand=lambda: 1.0,
        )
    except RateLimitError:
        pass
    assert all(d <= 3.0 for d in sleeper.delays), f"expected every delay <= 3.0, got {sleeper.delays!r}"
