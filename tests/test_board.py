"""Tests for the Connect Four board."""

from connect_four.board import Position


def test_empty_board_legal_moves():
    position = Position()
    assert position.legal_columns() == list(range(7))


def test_play_sequence():
    position = Position.from_sequence("1234567")
    assert position.moves == 7
    assert position.can_play(0)


def test_winning_move_detection():
    position = Position.from_sequence("434343")
    assert position.is_winning_move(3)


def test_center_is_best_opening():
    from connect_four.solver import Solver

    solver = Solver()
    assert solver.best_move(Position()) == 3


def test_known_winning_position():
    from connect_four.solver import Solver

    solver = Solver()
    score = solver.solve(Position())
    assert score > 0
