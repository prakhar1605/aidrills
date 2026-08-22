def render(template: str, variables: dict, strict: bool = True) -> str:
    """Fill {name} placeholders from `variables`.

    Args:
        template: the template text.
        variables: values to substitute.
        strict: raise on an unknown placeholder instead of leaving it in place.

    Returns:
        The rendered string.

    Raises:
        KeyError: on an unknown placeholder when strict.
        ValueError: on an unmatched or empty brace.
    """
    raise NotImplementedError


def variables_used(template: str) -> set[str]:
    """The placeholder names in `template`, ignoring escaped braces."""
    raise NotImplementedError
