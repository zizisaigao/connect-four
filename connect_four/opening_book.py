"""Precomputed opening knowledge for Connect Four."""

from __future__ import annotations

# position key -> exact score from current player's perspective
OPENING_SCORES: dict[int, int] = {
    0: 21,
}

# position key -> best column (0-indexed)
OPENING_BEST_MOVES: dict[int, int] = {
    0: 3,
}


def lookup_score(key: int) -> int | None:
    return OPENING_SCORES.get(key)


def lookup_best_move(key: int) -> int | None:
    return OPENING_BEST_MOVES.get(key)
