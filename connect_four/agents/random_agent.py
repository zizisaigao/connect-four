"""Random baseline agent."""

from __future__ import annotations

import random

from connect_four.agents.base import Agent
from connect_four.board import Position


class RandomAgent(Agent):
    name = "random"

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def choose_move(self, position: Position, player: int) -> int:
        return self._rng.choice(position.legal_columns())
