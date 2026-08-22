from collections import Counter

END = "</w>"


def train_bpe(corpus: list[str], num_merges: int) -> list[tuple[str, str]]:
    """Learn BPE merge rules from a list of words.

    Args:
        corpus: words; repeats carry the frequency.
        num_merges: how many merge rules to learn at most.

    Returns:
        The merges, in the order they were learned.
    """
    raise NotImplementedError


def encode(word: str, merges: list[tuple[str, str]]) -> list[str]:
    """Apply learned merges to a single word.

    Args:
        word: the word to tokenize.
        merges: rules from train_bpe, in training order.

    Returns:
        The symbol list, ending with the "</w>" marker.
    """
    raise NotImplementedError
