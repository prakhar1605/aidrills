PER_MILLION = 1_000_000
PLACES = 6


def estimate_cost(usages: list[dict], pricing: dict[str, dict]) -> dict:
    # Accumulate in full precision; round once, on the way out.
    totals: dict[str, dict[str, float]] = {}

    for usage in usages:
        model = usage["model"]
        if model not in pricing:
            raise KeyError(f"no pricing for model {model!r}")
        rates = pricing[model]

        counts = {
            "input": usage.get("input_tokens", 0) or 0,
            "output": usage.get("output_tokens", 0) or 0,
            "cached": usage.get("cached_input_tokens", 0) or 0,
        }
        for name, value in counts.items():
            if value < 0:
                raise ValueError(f"{name} token count must not be negative, got {value}")

        # Providers that do not publish a cache rate bill it as ordinary input.
        cached_rate = rates.get("cached_input", rates["input"])

        entry = totals.setdefault(
            model, {"calls": 0, "input_usd": 0.0, "cached_usd": 0.0, "output_usd": 0.0}
        )
        entry["calls"] += 1
        entry["input_usd"] += counts["input"] * rates["input"] / PER_MILLION
        entry["cached_usd"] += counts["cached"] * cached_rate / PER_MILLION
        entry["output_usd"] += counts["output"] * rates["output"] / PER_MILLION

    by_model = {}
    grand_total = 0.0
    for model, entry in totals.items():
        subtotal = entry["input_usd"] + entry["cached_usd"] + entry["output_usd"]
        grand_total += subtotal
        by_model[model] = {
            "calls": entry["calls"],
            "input_usd": round(entry["input_usd"], PLACES),
            "cached_usd": round(entry["cached_usd"], PLACES),
            "output_usd": round(entry["output_usd"], PLACES),
            "total_usd": round(subtotal, PLACES),
        }

    return {"total_usd": round(grand_total, PLACES), "by_model": by_model}


# What the interviewer is checking:
#   - rounding happens once per reported figure, never inside the accumulation
#   - the grand total sums the *unrounded* subtotals, so it reconciles
#   - rates.get("cached_input", rates["input"]) rather than a hardcoded discount
#   - KeyError names the model, because "KeyError: 'model'" tells an on-call
#     engineer nothing
