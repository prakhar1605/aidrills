def validate_args(schema: dict, args: dict) -> list[str]:
    """Check `args` against a small JSON-Schema subset.

    Args:
        schema: properties, required.
        args: the arguments the model produced.

    Returns:
        Sorted error strings; empty if valid.

    Raises:
        ValueError: if the schema names an unsupported type.
    """
    raise NotImplementedError
