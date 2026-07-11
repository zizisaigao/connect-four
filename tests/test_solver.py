"""Tests for the perfect-play solver."""

import time

from connect_four.board import Position
from connect_four.solver import Solver


def test_empty_board_first_player_wins():
    solver = Solver()
    score = solver.solve(Position())
    assert score > 0


def test_solver_beats_random_consistently():
    from connect_four.agents.random_agent import RandomAgent
    from connect_four.agents.solver_agent import SolverAgent
    from connect_four.board import Position
    from connect_four.game import Game, GameResult

    start = Position.from_sequence("35426")
    wins = 0
    for seed in range(3):
        game = Game(start.clone())
        solver = SolverAgent()
        opponent = RandomAgent(seed=seed)
        agents = {1: solver, 2: opponent}
        while not game.is_over():
            player = game.current_player
            col = agents[player].choose_move(game.position, player)
            game.play(col)
        if game.result() == GameResult.PLAYER_ONE_WIN:
            wins += 1
    assert wins == 3


def test_midgame_analysis_speed():
    position = Position.from_sequence("35426")
    solver = Solver()
    start = time.perf_counter()
    best = solver.best_move(position)
    elapsed = time.perf_counter() - start
    assert best in position.legal_columns()
    assert elapsed < 2.0
