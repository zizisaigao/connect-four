"""Agent interface for Connect Four players."""

from __future__ import annotations

from abc import ABC, abstractmethod

from connect_four.board import Position


class Agent(ABC):
    name: str = "agent"

    @abstractmethod
    def choose_move(self, position: Position, player: int) -> int:
        """Return a column index in [0, WIDTH)."""
