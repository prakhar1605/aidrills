def rrf_fuse(
    rankings: list[list[str]],
    k: int = 60,
    top_n: int | None = None,
) -> list[str]:
    """Fuse several ranked lists into one by reciprocal rank fusion.

    Args:
        rankings: ranked lists of document ids, best-first.
        k: rank damping constant.
        top_n: how many ids to return; None returns all.

    Returns:
        Document ids, best-first.
    """
    raise NotImplementedError
