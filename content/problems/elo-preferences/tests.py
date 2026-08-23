from submission import *


def test_equal_ratings_expect_a_draw():
    out = expected_score(1000.0, 1000.0)
    assert abs(out - 0.5) < 1e-12, f"expected 0.5, got {out!r}"


def test_expectations_are_complementary():
    a, b = expected_score(1200.0, 1000.0), expected_score(1000.0, 1200.0)
    assert abs(a + b - 1.0) < 1e-12, f"expected the two to sum to 1, got {a!r} and {b!r}"


def test_four_hundred_points_is_ten_to_one():
    out = expected_score(1400.0, 1000.0)
    exp = 10 / 11
    assert abs(out - exp) < 1e-9, f"expected {exp!r}, got {out!r}"


def test_a_stronger_player_is_favoured():
    assert expected_score(1500.0, 1000.0) > 0.5, "the higher rating must be favoured"
    assert expected_score(1000.0, 1500.0) < 0.5, "the lower rating must be the underdog"


def test_no_matches():
    out = elo_ratings([])
    assert out == {}, f"expected an empty dict, got {out!r}"


def test_every_player_appears():
    out = elo_ratings([{"a": "x", "b": "y", "winner": "a"}])
    assert set(out) == {"x", "y"}, f"expected both players, got {sorted(out)!r}"


def test_even_match_moves_by_half_k():
    out = elo_ratings([{"a": "x", "b": "y", "winner": "a"}], k=32.0, initial=1000.0)
    assert abs(out["x"] - 1016.0) < 1e-9, f"expected 1016.0, got {out['x']!r}"
    assert abs(out["y"] - 984.0) < 1e-9, f"expected 984.0, got {out['y']!r}"


def test_tie_between_equals_changes_nothing():
    out = elo_ratings([{"a": "x", "b": "y", "winner": "tie"}])
    assert abs(out["x"] - 1000.0) < 1e-9, f"expected 1000.0, got {out['x']!r}"
    assert abs(out["y"] - 1000.0) < 1e-9, f"expected 1000.0, got {out['y']!r}"


def test_loser_loses():
    out = elo_ratings([{"a": "x", "b": "y", "winner": "b"}])
    assert out["x"] < 1000.0, f"the loser must drop, got {out['x']!r}"
    assert out["y"] > 1000.0, f"the winner must rise, got {out['y']!r}"


def test_ratings_are_zero_sum():
    matches = [
        {"a": "x", "b": "y", "winner": "a"},
        {"a": "y", "b": "z", "winner": "tie"},
        {"a": "z", "b": "x", "winner": "b"},
        {"a": "x", "b": "y", "winner": "b"},
    ]
    out = elo_ratings(matches, initial=1000.0)
    total = sum(out.values())
    exp = 1000.0 * len(out)
    assert abs(total - exp) < 1e-6, (
        f"the total must stay at {exp!r} -- update in place and it drifts. Got {total!r}"
    )


def test_an_upset_moves_more_than_an_expected_win():
    strong = [{"a": "sm", "b": "weak", "winner": "a"}] * 10
    underdog = elo_ratings(strong)["weak"]

    upset = elo_ratings(strong + [{"a": "weak", "b": "sm", "winner": "a"}])
    gain = upset["weak"] - underdog
    assert gain > 16.0, f"beating a favourite must gain more than half of k, got {gain!r}"


def test_k_scales_the_movement():
    small = elo_ratings([{"a": "x", "b": "y", "winner": "a"}], k=8.0)
    large = elo_ratings([{"a": "x", "b": "y", "winner": "a"}], k=64.0)
    assert large["x"] - 1000.0 > small["x"] - 1000.0, "a larger k must move ratings further"


def test_initial_rating_is_respected():
    out = elo_ratings([{"a": "x", "b": "y", "winner": "tie"}], initial=1500.0)
    assert abs(out["x"] - 1500.0) < 1e-9, f"expected 1500.0, got {out['x']!r}"


def test_order_matters():
    forward = elo_ratings(
        [
            {"a": "x", "b": "y", "winner": "a"},
            {"a": "y", "b": "z", "winner": "a"},
        ]
    )
    backward = elo_ratings(
        [
            {"a": "y", "b": "z", "winner": "a"},
            {"a": "x", "b": "y", "winner": "a"},
        ]
    )
    assert forward != backward, "sequential Elo depends on the order of the matches"


def test_a_player_who_never_wins_still_appears():
    out = elo_ratings(
        [
            {"a": "x", "b": "loser", "winner": "a"},
            {"a": "y", "b": "loser", "winner": "a"},
        ]
    )
    assert "loser" in out, f"expected 'loser' in {sorted(out)!r}"
    assert out["loser"] < 1000.0, f"expected a rating below the start, got {out['loser']!r}"


def test_unknown_winner_raises():
    try:
        elo_ratings([{"a": "x", "b": "y", "winner": "both"}])
    except ValueError:
        return
    raise AssertionError("an unknown winner must raise ValueError")


def test_self_match_raises():
    try:
        elo_ratings([{"a": "x", "b": "x", "winner": "a"}])
    except ValueError:
        return
    raise AssertionError("a player facing themselves must raise ValueError")
