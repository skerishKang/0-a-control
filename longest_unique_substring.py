from __future__ import annotations


def length_of_longest_substring(text: str) -> int:
    """Return the length of the longest substring with no repeated characters.

    Python strings are iterated by Unicode code point, which matches the
    repository's current tests for Korean text, emoji, whitespace, and
    zero-width characters.
    """
    start = 0
    best = 0
    last_seen: dict[str, int] = {}

    for index, char in enumerate(text):
        previous = last_seen.get(char)
        if previous is not None and previous >= start:
            start = previous + 1
        last_seen[char] = index
        best = max(best, index - start + 1)

    return best
