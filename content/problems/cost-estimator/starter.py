PER_MILLION = 1_000_000


def estimate_cost(usages: list[dict], pricing: dict[str, dict]) -> dict:
    """Price a list of usage records against a per-million-token price sheet.

    Args:
        usages: records with model, input_tokens, output_tokens and an optional
            cached_input_tokens.
        pricing: model -> per-million USD rates for input, output and optionally
            cached_input.

    Returns:
        A dict with total_usd and a by_model breakdown.

    Raises:
        KeyError: if a usage names a model that is not priced.
        ValueError: on a negative token count.
    """
    raise NotImplementedError
