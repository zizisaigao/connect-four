"""Interactive human player."""

from __future__ import annotations

from connect_four.agents.base import Agent
from connect_four.board import Position


class HumanAgent(Agent):
    name = "human"

    def choose_move(self, position: Position, player: int) -> int:
        legal = position.legal_columns()
        while True:
            raw = input(f"Player {player}, choose column {legal}: ").strip()
            try:
                col = int(raw) - 1
            except ValueError:
                print("Please enter a number between 1 and 7.")
                continue
            if col in legal:
                return col
            print("Illegal move. Try again.")
