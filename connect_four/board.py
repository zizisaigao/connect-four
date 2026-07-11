"""Bitboard representation for Connect Four.

The layout follows Pascal Pons' solver (gamesolver.org):
each column uses HEIGHT+1 bits with a sentinel row on top.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator


WIDTH = 7
HEIGHT = 6
MIN_SCORE = -(WIDTH * HEIGHT) // 2 + 3
MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3


def _bottom_mask(width: int = WIDTH, height: int = HEIGHT) -> int:
    mask = 0
    for col in range(width):
        mask |= 1 << (col * (height + 1))
    return mask


BOTTOM_MASK = _bottom_mask()
BOARD_MASK = BOTTOM_MASK * ((1 << HEIGHT) - 1)


def column_mask(col: int) -> int:
    return ((1 << HEIGHT) - 1) << (col * (HEIGHT + 1))


def top_mask_col(col: int) -> int:
    return 1 << ((HEIGHT - 1) + col * (HEIGHT + 1))


def bottom_mask_col(col: int) -> int:
    return 1 << (col * (HEIGHT + 1))


def popcount(value: int) -> int:
    return value.bit_count()


def compute_winning_position(position: int, mask: int) -> int:
    """Return bitmask of winning spots for the given player."""
    result = (position << 1) & (position << 2) & (position << 3)

    horizontal = (position << (HEIGHT + 1)) & (position << 2 * (HEIGHT + 1))
    result |= horizontal & (position << 3 * (HEIGHT + 1))
    result |= horizontal & (position >> (HEIGHT + 1))
    horizontal = (position >> (HEIGHT + 1)) & (position >> 2 * (HEIGHT + 1))
    result |= horizontal & (position << (HEIGHT + 1))
    result |= horizontal & (position >> 3 * (HEIGHT + 1))

    diagonal = (position << HEIGHT) & (position << 2 * HEIGHT)
    result |= diagonal & (position << 3 * HEIGHT)
    result |= diagonal & (position >> HEIGHT)
    diagonal = (position >> HEIGHT) & (position >> 2 * HEIGHT)
    result |= diagonal & (position << HEIGHT)
    result |= diagonal & (position >> 3 * HEIGHT)

    diagonal = (position << (HEIGHT + 2)) & (position << 2 * (HEIGHT + 2))
    result |= diagonal & (position << 3 * (HEIGHT + 2))
    result |= diagonal & (position >> (HEIGHT + 2))
    diagonal = (position >> (HEIGHT + 2)) & (position >> 2 * (HEIGHT + 2))
    result |= diagonal & (position << (HEIGHT + 2))
    result |= diagonal & (position >> 3 * (HEIGHT + 2))

    return result & (BOARD_MASK ^ mask)


@dataclass
class Position:
    """A Connect Four position from the current player's perspective."""

    current_position: int = 0
    mask: int = 0
    moves: int = 0
    _history: list[tuple[int, int, int]] = field(default_factory=list)

    def key(self) -> int:
        return self.current_position + self.mask

    def can_play(self, col: int) -> bool:
        return (self.mask & top_mask_col(col)) == 0

    def possible(self) -> int:
        return (self.mask + BOTTOM_MASK) & BOARD_MASK

    def winning_position(self) -> int:
        return compute_winning_position(self.current_position, self.mask)

    def opponent_winning_position(self) -> int:
        return compute_winning_position(self.current_position ^ self.mask, self.mask)

    def can_win_next(self) -> bool:
        return bool(self.winning_position() & self.possible())

    def is_winning_move(self, col: int) -> bool:
        return bool(self.winning_position() & self.possible() & column_mask(col))

    def play_col(self, col: int) -> None:
        move = (self.mask + bottom_mask_col(col)) & column_mask(col)
        self.play(move)

    def play(self, move: int) -> None:
        self._history.append((self.current_position, self.mask, move))
        self.current_position ^= self.mask
        self.mask |= move
        self.moves += 1

    def undo(self) -> None:
        if not self._history:
            raise ValueError("No moves to undo")
        current_position, mask, _move = self._history.pop()
        self.current_position = current_position
        self.mask = mask
        self.moves -= 1

    def clone(self) -> Position:
        return Position(
            self.current_position,
            self.mask,
            self.moves,
            list(self._history),
        )

    def play_sequence(self, sequence: str) -> int:
        """Play a sequence of 1-based column digits. Returns processed move count."""
        processed = 0
        for char in sequence:
            col = int(char) - 1
            if col < 0 or col >= WIDTH or not self.can_play(col) or self.is_winning_move(col):
                return processed
            self.play_col(col)
            processed += 1
        return processed

    def possible_non_losing_moves(self) -> int:
        if self.can_win_next():
            raise ValueError("possible_non_losing_moves requires no immediate win")

        possible_mask = self.possible()
        opponent_win = self.opponent_winning_position()
        forced_moves = possible_mask & opponent_win
        if forced_moves:
            if forced_moves & (forced_moves - 1):
                return 0
            possible_mask = forced_moves
        return possible_mask & ~(opponent_win >> 1)

    def move_score(self, move: int) -> int:
        return popcount(
            compute_winning_position(self.current_position | move, self.mask)
        )

    def legal_columns(self) -> list[int]:
        return [col for col in range(WIDTH) if self.can_play(col)]

    def is_draw(self) -> bool:
        return self.moves >= WIDTH * HEIGHT

    def __iter__(self) -> Iterator[tuple[int, int]]:
        for row in range(HEIGHT):
            for col in range(WIDTH):
                bit = 1 << (col * (HEIGHT + 1) + row)
                if self.mask & bit:
                    player = 1 if self.current_position & bit else 2
                    yield row, col, player
                else:
                    yield row, col, 0

    def to_grid(self) -> list[list[int]]:
        """Return a 6x7 grid with 0=empty, 1=current player, 2=opponent."""
        grid = [[0] * WIDTH for _ in range(HEIGHT)]
        for row in range(HEIGHT):
            for col in range(WIDTH):
                bit = 1 << (col * (HEIGHT + 1) + row)
                if self.mask & bit:
                    grid[row][col] = 1 if self.current_position & bit else 2
        return grid

    def render(self, perspective: int | None = None) -> str:
        """Render board. perspective=1 or 2 remaps symbols to that player."""
        symbols = {0: ".", 1: "X", 2: "O"}
        if perspective == 2:
            symbols = {0: ".", 1: "O", 2: "X"}

        lines = []
        for row in reversed(range(HEIGHT)):
            cells = []
            for col in range(WIDTH):
                bit = 1 << (col * (HEIGHT + 1) + row)
                if self.mask & bit:
                    player = 1 if self.current_position & bit else 2
                else:
                    player = 0
                cells.append(symbols[player])
            lines.append(" ".join(cells))
        lines.append(" ".join(str(i + 1) for i in range(WIDTH)))
        return "\n".join(lines)

    @classmethod
    def from_moves(cls, moves: list[int]) -> Position:
        position = cls()
        for col in moves:
            position.play_col(col)
        return position

    @classmethod
    def from_sequence(cls, sequence: str) -> Position:
        position = cls()
        position.play_sequence(sequence)
        return position
