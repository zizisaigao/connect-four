"""Gym-like environment for reinforcement learning experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from connect_four.board import HEIGHT, WIDTH, Position


@dataclass
class ConnectFourEnv:
    """Simple RL environment wrapper around the bitboard engine."""

    position: Position = field(default_factory=Position)

    @property
    def observation_space_shape(self) -> tuple[int, int, int]:
        return (2, HEIGHT, WIDTH)

    @property
    def action_space_n(self) -> int:
        return WIDTH

    def reset(self) -> np.ndarray:
        self.position = Position()
        return self._observation()

    def legal_actions(self) -> list[int]:
        return self.position.legal_columns()

    def step(self, action: int) -> tuple[np.ndarray, float, bool, dict[str, Any]]:
        if not self.position.can_play(action):
            raise ValueError(f"Illegal action: {action}")

        current_player = (self.position.moves % 2) + 1
        winning_move = self.position.is_winning_move(action)
        self.position.play_col(action)

        reward = 0.0
        done = False
        info: dict[str, Any] = {"player": current_player}

        if winning_move:
            reward = 1.0
            done = True
            info["winner"] = current_player
        elif self.position.is_draw():
            reward = 0.0
            done = True
            info["winner"] = 0

        return self._observation(), reward, done, info

    def _observation(self) -> np.ndarray:
        grid = self.position.to_grid()
        current = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
        opponent = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
        for row in range(HEIGHT):
            for col in range(WIDTH):
                if grid[row][col] == 1:
                    current[HEIGHT - 1 - row, col] = 1.0
                elif grid[row][col] == 2:
                    opponent[HEIGHT - 1 - row, col] = 1.0
        return np.stack([current, opponent], axis=0)

    def render(self) -> str:
        return self.position.render()
