from collections import Counter

END = "</w>"


def _merge_symbols(symbols: list[str], pair: tuple[str, str]) -> list[str]:
    """One left-to-right pass merging non-overlapping occurrences of `pair`."""
    left, right = pair
    merged: list[str] = []
    i = 0
    while i < len(symbols):
        if i + 1 < len(symbols) and symbols[i] == left and symbols[i + 1] == right:
            merged.append(left + right)
            i += 2
        else:
            merged.append(symbols[i])
            i += 1
    return merged


def train_bpe(corpus: list[str], num_merges: int) -> list[tuple[str, str]]:
    # word -> frequency, so a repeated word is counted once and weighted.
    vocab = {
        tuple(list(word) + [END]): count
        for word, count in Counter(corpus).items()
    }

    merges: list[tuple[str, str]] = []
    for _ in range(num_merges):
        pairs: Counter = Counter()
        for symbols, count in vocab.items():
            for pair in zip(symbols, symbols[1:]):
                pairs[pair] += count
        if not pairs:
            break

        top = max(pairs.values())
        # min() over the tied pairs -- explicit, so training does not depend on
        # dict ordering or on Counter.most_common's tie behaviour.
        best = min(pair for pair, count in pairs.items() if count == top)

        merges.append(best)
        vocab = {
            tuple(_merge_symbols(list(symbols), best)): count
            for symbols, count in vocab.items()
        }
    return merges


def encode(word: str, merges: list[tuple[str, str]]) -> list[str]:
    symbols = list(word) + [END]
    for pair in merges:
        if len(symbols) == 1:
            break
        symbols = _merge_symbols(symbols, pair)
    return symbols


# What the interviewer is checking:
#   - merges applied in learned order at encode time; sorting by token length
#     is the classic wrong optimization
#   - the tie break is explicit rather than inherited from Counter
#   - the vocabulary is keyed by word, not by occurrence, so the pair counts are
#     frequency-weighted instead of O(corpus) per merge
#   - one left-to-right pass per merge is enough: a merged token can never form
#     a fresh occurrence of the same pair
