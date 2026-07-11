"""Heuristic evaluation for depth-limited Connect Four search."""

from __future__ import annotations

from connect_four.board import HEIGHT, WIDTH, Position, compute_winning_position


def count_threats(position: int, mask: int) -> int:
    """Count winning spots available to a player bitmask."""
    return (compute_winning_position(position, mask)).bit_count()


def evaluate_position(position: Position) -> int:
    """Heuristic score from the current player's perspective."""
    current = position.current_position
    opponent = position.current_position ^ position.mask
    mask = position.mask

    current_threats = count_threats(current, mask)
    opponent_threats = count_threats(opponent, mask)

    center_bonus = 0
    for col in range(WIDTH):
        center_bonus += ((current >> (col * (HEIGHT + 1))) & ((1 << HEIGHT) - 1)).bit_count() * (
            3 - abs(col - WIDTH // 2)
        )

    return (current_threats - opponent_threats) * 10 + center_bonus
