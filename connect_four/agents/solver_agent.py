"""Perfect-play agent backed by the solver."""

from __future__ import annotations

from connect_four.agents.base import Agent
from connect_four.board import Position
from connect_four.solver import Solver


class SolverAgent(Agent):
    name = "solver"

    def __init__(self) -> None:
        self.solver = Solver()

    def choose_move(self, position: Position, player: int) -> int:
        if player == 2:
            mirrored = position.clone()
            mirrored.current_position ^= mirrored.mask
            return self.solver.best_move(mirrored)
        return self.solver.best_move(position)

    def analyze(self, position: Position, player: int) -> list[int]:
        if player == 2:
            mirrored = position.clone()
            mirrored.current_position ^= mirrored.mask
            return self.solver.analyze(mirrored)
        return self.solver.analyze(position)
