"""Reinforcement learning agent placeholder.

This module provides a minimal Q-learning skeleton for experimentation.
For serious training, consider self-play against SolverAgent or AlphaZero-style MCTS.
"""

from __future__ import annotations

import random
from collections import defaultdict

from connect_four.agents.base import Agent
from connect_four.board import Position


class RLAgent(Agent):
    name = "rl"

    def __init__(
        self,
        epsilon: float = 0.1,
        alpha: float = 0.5,
        gamma: float = 0.95,
        seed: int | None = None,
    ) -> None:
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self._rng = random.Random(seed)
        self.q_table: dict[tuple[int, int], float] = defaultdict(float)

    def choose_move(self, position: Position, player: int) -> int:
        legal = position.legal_columns()
        if self._rng.random() < self.epsilon:
            return self._rng.choice(legal)

        state = position.key()
        return max(legal, key=lambda col: self.q_table[(state, col)])

    def update(
        self,
        state: int,
        action: int,
        reward: float,
        next_state: int,
        next_legal: list[int],
    ) -> None:
        best_next = 0.0
        if next_legal:
            best_next = max(self.q_table[(next_state, col)] for col in next_legal)
        old = self.q_table[(state, action)]
        target = reward + self.gamma * best_next
        self.q_table[(state, action)] = old + self.alpha * (target - old)

    def train_episode(self, env, opponent_move_fn) -> float:
        """Run one self-play-ish episode for educational purposes."""
        obs = env.reset()
        state = env.position.key()
        total_reward = 0.0

        while True:
            legal = env.legal_actions()
            action = self.choose_move(env.position, (env.position.moves % 2) + 1)
            _, reward, done, _ = env.step(action)
            total_reward += reward
            next_state = env.position.key()

            if done:
                self.update(state, action, reward, next_state, [])
                break

            opp_action = opponent_move_fn(env.position)
            _, opp_reward, done, _ = env.step(opp_action)
            total_reward -= opp_reward
            next_state = env.position.key()
            self.update(state, action, -opp_reward, next_state, env.legal_actions())
            state = next_state

            if done:
                break

        return total_reward
