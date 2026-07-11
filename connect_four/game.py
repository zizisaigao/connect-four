"""Game orchestration for Connect Four."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from connect_four.agents.base import Agent
from connect_four.board import Position, WIDTH


class GameResult(Enum):
    PLAYER_ONE_WIN = 1
    PLAYER_TWO_WIN = 2
    DRAW = 0
    IN_PROGRESS = -1


@dataclass
class Game:
    position: Position = field(default_factory=Position)
    history: list[int] = field(default_factory=list)
    winner: int | None = None

    @property
    def current_player(self) -> int:
        return (self.position.moves % 2) + 1

    def legal_moves(self) -> list[int]:
        return self.position.legal_columns()

    def play(self, col: int) -> bool:
        if not self.position.can_play(col):
            return False
        if self.position.is_winning_move(col):
            self.winner = self.current_player
        self.position.play_col(col)
        self.history.append(col)
        return True

    def result(self) -> GameResult:
        if self.winner == 1:
            return GameResult.PLAYER_ONE_WIN
        if self.winner == 2:
            return GameResult.PLAYER_TWO_WIN
        if self.position.is_draw():
            return GameResult.DRAW
        return GameResult.IN_PROGRESS

    def is_over(self) -> bool:
        return self.result() != GameResult.IN_PROGRESS

    def render(self) -> str:
        return self.position.render()

    def clone(self) -> Game:
        return Game(self.position.clone(), list(self.history))


def play_game(player_one: Agent, player_two: Agent, verbose: bool = False) -> GameResult:
    game = Game()
    agents = {1: player_one, 2: player_two}

    while not game.is_over():
        player = game.current_player
        agent = agents[player]
        col = agent.choose_move(game.position, player)
        if col < 0 or col >= WIDTH or not game.play(col):
            raise ValueError(f"Agent {agent.name} played illegal move: {col}")
        if verbose:
            print(f"\n{agent.name} (P{player}) -> column {col + 1}")
            print(game.render())

    return game.result()
