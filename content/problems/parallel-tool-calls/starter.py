def schedule(calls: list[dict]) -> list[list[str]]:
    """Group tool calls into waves that can each run in parallel.

    Args:
        calls: dicts with an id and an optional depends_on list.

    Returns:
        Waves of ids, each wave sorted, in execution order.

    Raises:
        ValueError: on a duplicate id, an unknown dependency, or a cycle.
    """
    raise NotImplementedError
