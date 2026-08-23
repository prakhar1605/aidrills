from submission import *


def test_worked_example():
    out = schedule(
        [
            {"id": "a"},
            {"id": "b"},
            {"id": "c", "depends_on": ["a"]},
            {"id": "d", "depends_on": ["b", "c"]},
        ]
    )
    exp = [["a", "b"], ["c"], ["d"]]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_no_calls():
    out = schedule([])
    assert out == [], f"expected [], got {out!r}"


def test_all_independent_is_one_wave():
    out = schedule([{"id": "a"}, {"id": "b"}, {"id": "c"}])
    exp = [["a", "b", "c"]]
    assert out == exp, f"independent calls must run together: expected {exp!r}, got {out!r}"


def test_a_chain_is_one_call_per_wave():
    out = schedule(
        [
            {"id": "a"},
            {"id": "b", "depends_on": ["a"]},
            {"id": "c", "depends_on": ["b"]},
        ]
    )
    exp = [["a"], ["b"], ["c"]]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_missing_depends_on_means_no_dependencies():
    out = schedule([{"id": "a"}, {"id": "b", "depends_on": []}])
    exp = [["a", "b"]]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_waves_are_sorted():
    out = schedule([{"id": "z"}, {"id": "m"}, {"id": "a"}])
    assert out == [["a", "m", "z"]], f"expected a sorted wave, got {out!r}"


def test_schedule_is_as_shallow_as_possible():
    # "d" only needs "a", so it belongs in wave 2 with "b", not after "c".
    out = schedule(
        [
            {"id": "a"},
            {"id": "b", "depends_on": ["a"]},
            {"id": "c", "depends_on": ["b"]},
            {"id": "d", "depends_on": ["a"]},
        ]
    )
    exp = [["a"], ["b", "d"], ["c"]]
    assert out == exp, f"the schedule must not be padded: expected {exp!r}, got {out!r}"


def test_diamond():
    out = schedule(
        [
            {"id": "root"},
            {"id": "left", "depends_on": ["root"]},
            {"id": "right", "depends_on": ["root"]},
            {"id": "join", "depends_on": ["left", "right"]},
        ]
    )
    exp = [["root"], ["left", "right"], ["join"]]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_input_order_does_not_matter():
    calls = [
        {"id": "d", "depends_on": ["b", "c"]},
        {"id": "c", "depends_on": ["a"]},
        {"id": "b"},
        {"id": "a"},
    ]
    out = schedule(calls)
    exp = [["a", "b"], ["c"], ["d"]]
    assert out == exp, f"expected {exp!r}, got {out!r}"


def test_every_id_appears_exactly_once():
    calls = [{"id": str(i), "depends_on": [str(i - 1)] if i else []} for i in range(6)]
    flat = [call_id for wave in schedule(calls) for call_id in wave]
    assert sorted(flat) == sorted(str(i) for i in range(6)), f"expected each id once, got {flat!r}"


def test_dependencies_always_land_in_an_earlier_wave():
    calls = [
        {"id": "a"},
        {"id": "b", "depends_on": ["a"]},
        {"id": "c", "depends_on": ["a"]},
        {"id": "d", "depends_on": ["b", "c"]},
        {"id": "e", "depends_on": ["d"]},
    ]
    waves = schedule(calls)
    position = {cid: index for index, wave in enumerate(waves) for cid in wave}
    for call in calls:
        for need in call.get("depends_on", []):
            assert position[need] < position[call["id"]], (
                f"{need!r} must run before {call['id']!r}, got waves {waves!r}"
            )


def test_duplicate_id_raises():
    try:
        schedule([{"id": "a"}, {"id": "a"}])
    except ValueError:
        return
    raise AssertionError("a duplicate id must raise ValueError")


def test_unknown_dependency_raises_naming_it():
    try:
        schedule([{"id": "a", "depends_on": ["ghost"]}])
    except ValueError as exc:
        assert "ghost" in str(exc), f"the error must name the missing id, got {exc!r}"
        return
    raise AssertionError("an unknown dependency must raise ValueError")


def test_self_dependency_raises():
    try:
        schedule([{"id": "a", "depends_on": ["a"]}])
    except ValueError:
        return
    raise AssertionError("a self-dependency must raise ValueError")


def test_cycle_raises_naming_the_ids():
    try:
        schedule([{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}])
    except ValueError as exc:
        message = str(exc)
        assert "a" in message and "b" in message, f"the error must name the stuck ids, got {exc!r}"
        return
    raise AssertionError("a cycle must raise ValueError")


def test_cycle_is_detected_behind_valid_work():
    try:
        schedule(
            [
                {"id": "ok"},
                {"id": "x", "depends_on": ["y"]},
                {"id": "y", "depends_on": ["x"]},
            ]
        )
    except ValueError:
        return
    raise AssertionError("a cycle must raise even when some calls are schedulable")
