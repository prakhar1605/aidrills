from submission import *

PRICING = {
    "big": {"input": 15.0, "output": 75.0, "cached_input": 1.5},
    "small": {"input": 0.8, "output": 4.0},
}


def test_no_usages():
    out = estimate_cost([], PRICING)
    assert out["total_usd"] == 0.0, f"expected 0.0, got {out['total_usd']!r}"
    assert out["by_model"] == {}, f"expected an empty breakdown, got {out['by_model']!r}"


def test_single_call():
    usages = [{"model": "big", "input_tokens": 1_000_000, "output_tokens": 0}]
    out = estimate_cost(usages, PRICING)
    assert out["total_usd"] == 15.0, f"expected 15.0, got {out['total_usd']!r}"


def test_input_and_output_are_priced_separately():
    usages = [{"model": "big", "input_tokens": 1_000_000, "output_tokens": 1_000_000}]
    out = estimate_cost(usages, PRICING)
    assert out["total_usd"] == 90.0, f"expected 90.0, got {out['total_usd']!r}"
    entry = out["by_model"]["big"]
    assert entry["input_usd"] == 15.0, f"expected 15.0, got {entry['input_usd']!r}"
    assert entry["output_usd"] == 75.0, f"expected 75.0, got {entry['output_usd']!r}"


def test_cached_tokens_use_the_cache_rate():
    usages = [
        {
            "model": "big",
            "input_tokens": 0,
            "output_tokens": 0,
            "cached_input_tokens": 1_000_000,
        }
    ]
    out = estimate_cost(usages, PRICING)
    assert out["total_usd"] == 1.5, f"expected the cache rate: 1.5, got {out['total_usd']!r}"


def test_cached_falls_back_to_the_input_rate():
    usages = [
        {
            "model": "small",
            "input_tokens": 0,
            "output_tokens": 0,
            "cached_input_tokens": 1_000_000,
        }
    ]
    out = estimate_cost(usages, PRICING)
    assert out["total_usd"] == 0.8, f"expected the input rate: 0.8, got {out['total_usd']!r}"


def test_cached_is_separate_from_input():
    usages = [
        {
            "model": "big",
            "input_tokens": 1_000_000,
            "output_tokens": 0,
            "cached_input_tokens": 1_000_000,
        }
    ]
    out = estimate_cost(usages, PRICING)
    exp = 16.5
    assert out["total_usd"] == exp, f"cached tokens are not a subset of input: expected {exp!r}, got {out['total_usd']!r}"


def test_calls_are_counted():
    usages = [{"model": "small", "input_tokens": 10, "output_tokens": 10}] * 3
    out = estimate_cost(usages, PRICING)
    assert out["by_model"]["small"]["calls"] == 3, f"expected 3, got {out['by_model']['small']['calls']!r}"


def test_multiple_models():
    usages = [
        {"model": "big", "input_tokens": 1_000_000, "output_tokens": 0},
        {"model": "small", "input_tokens": 1_000_000, "output_tokens": 0},
    ]
    out = estimate_cost(usages, PRICING)
    assert set(out["by_model"]) == {"big", "small"}, f"expected both models, got {sorted(out['by_model'])!r}"
    assert out["total_usd"] == 15.8, f"expected 15.8, got {out['total_usd']!r}"


def test_totals_reconcile_with_the_breakdown():
    usages = [
        {"model": "big", "input_tokens": 12_345, "output_tokens": 6_789},
        {"model": "small", "input_tokens": 98_765, "output_tokens": 4_321},
        {"model": "big", "input_tokens": 3, "output_tokens": 7, "cached_input_tokens": 11},
    ]
    out = estimate_cost(usages, PRICING)
    summed = round(sum(entry["total_usd"] for entry in out["by_model"].values()), 6)
    assert abs(summed - out["total_usd"]) < 1e-6, (
        f"the breakdown sums to {summed!r} but the total says {out['total_usd']!r}"
    )


def test_each_model_subtotal_matches_its_parts():
    usages = [{"model": "big", "input_tokens": 7, "output_tokens": 13, "cached_input_tokens": 21}]
    entry = estimate_cost(usages, PRICING)["by_model"]["big"]
    parts = round(entry["input_usd"] + entry["cached_usd"] + entry["output_usd"], 6)
    assert abs(parts - entry["total_usd"]) < 1e-6, f"{parts!r} != {entry['total_usd']!r}"


def test_missing_token_counts_default_to_zero():
    out = estimate_cost([{"model": "small"}], PRICING)
    assert out["total_usd"] == 0.0, f"expected 0.0, got {out['total_usd']!r}"
    assert out["by_model"]["small"]["calls"] == 1, "the call must still be counted"


def test_results_are_rounded_to_six_places():
    usages = [{"model": "small", "input_tokens": 1, "output_tokens": 1}]
    out = estimate_cost(usages, PRICING)
    for value in (out["total_usd"], out["by_model"]["small"]["input_usd"]):
        assert round(value, 6) == value, f"{value!r} is not rounded to 6 places"


def test_unknown_model_raises_keyerror_naming_it():
    try:
        estimate_cost([{"model": "gpt-9", "input_tokens": 1, "output_tokens": 1}], PRICING)
    except KeyError as exc:
        assert "gpt-9" in str(exc), f"the error must name the model, got {exc!r}"
        return
    raise AssertionError("an unpriced model must raise KeyError")


def test_negative_tokens_raise():
    try:
        estimate_cost([{"model": "small", "input_tokens": -5, "output_tokens": 0}], PRICING)
    except ValueError:
        return
    raise AssertionError("a negative token count must raise ValueError")
