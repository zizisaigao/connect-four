"""Connect Four search: exact solver and fast heuristic search."""

from __future__ import annotations

from collections import OrderedDict

from connect_four.board import (
    HEIGHT,
    MAX_SCORE,
    MIN_SCORE,
    WIDTH,
    Position,
    column_mask,
)
from connect_four.heuristic import evaluate_position
from connect_four.opening_book import lookup_best_move, lookup_score


INVALID_MOVE = -1000


class LRUCache(OrderedDict[int, int]):
    def __init__(self, maxsize: int = 1 << 20):
        super().__init__()
        self.maxsize = maxsize

    def __setitem__(self, key: int, value: int) -> None:
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            self.popitem(last=False)


class Solver:
    """Connect Four AI with exact endgame solving and fast heuristic opening play."""

    def __init__(self, transposition_size: int = 1 << 18, search_depth: int = 6) -> None:
        self.transposition = LRUCache(transposition_size)
        self.node_count = 0
        self.search_depth = search_depth
        self.column_order = tuple(
            WIDTH // 2 + (1 - 2 * (i % 2)) * (i + 1) // 2 for i in range(WIDTH)
        )

    def reset_stats(self) -> None:
        self.node_count = 0

    def solve(self, position: Position, weak: bool = False, exact: bool = False) -> int:
        if position.can_win_next():
            return (WIDTH * HEIGHT + 1 - position.moves) // 2

        book_score = lookup_score(position.key())
        if book_score is not None:
            return book_score

        if exact or self._should_use_exact(position):
            return self._solve_exact(position, weak=weak)
        return self._solve_heuristic(position, depth=self.search_depth)

    def best_move(self, position: Position, exact: bool = False) -> int:
        book_move = lookup_best_move(position.key())
        if book_move is not None and not exact:
            return book_move

        if position.can_win_next():
            for col in position.legal_columns():
                if position.is_winning_move(col):
                    return col

        alpha = -(WIDTH * HEIGHT - position.moves) // 2
        beta = (WIDTH * HEIGHT + 1 - position.moves) // 2
        best_col = self.column_order[0]
        best_score = -10**9

        for col in self.column_order:
            if not position.can_play(col):
                continue
            if position.is_winning_move(col):
                return col
            position.play_col(col)
            if exact or self._should_use_exact(position):
                score = -self._solve_exact(position, weak=False)
            else:
                score = -self._negamax_heuristic(position, self.search_depth - 1, -beta, -alpha)
            position.undo()
            if score > best_score:
                best_score = score
                best_col = col
            if score > alpha:
                alpha = score
        return best_col

    def analyze(self, position: Position, weak: bool = False, exact: bool = False) -> list[int]:
        scores = [INVALID_MOVE] * WIDTH
        for col in range(WIDTH):
            if not position.can_play(col):
                continue
            if position.is_winning_move(col):
                scores[col] = (WIDTH * HEIGHT + 1 - position.moves) // 2
                continue
            position.play_col(col)
            scores[col] = -self.solve(position, weak=weak, exact=exact)
            position.undo()
        return scores

    def _should_use_exact(self, position: Position) -> bool:
        remaining = WIDTH * HEIGHT - position.moves
        return remaining <= 14

    def _solve_exact(self, position: Position, weak: bool = False) -> int:
        minimum = -(WIDTH * HEIGHT - position.moves) // 2
        maximum = (WIDTH * HEIGHT + 1 - position.moves) // 2
        if weak:
            minimum = -1
            maximum = 1

        while minimum < maximum:
            med = minimum + (maximum - minimum) // 2
            if med <= 0 and minimum // 2 < med:
                med = minimum // 2
            elif med >= 0 and maximum // 2 > med:
                med = maximum // 2
            score = self._negamax_exact(position, med, med + 1)
            if score <= med:
                maximum = score
            else:
                minimum = score
        return minimum

    def _solve_heuristic(self, position: Position, depth: int) -> int:
        return self._negamax_heuristic(position, depth, -(WIDTH * HEIGHT), WIDTH * HEIGHT)

    def _negamax_heuristic(
        self,
        position: Position,
        depth: int,
        alpha: int,
        beta: int,
    ) -> int:
        self.node_count += 1

        if position.can_win_next():
            return (WIDTH * HEIGHT + 1 - position.moves) // 2
        if position.is_draw():
            return 0
        if depth == 0:
            return evaluate_position(position)

        value = -10**9
        for col in self.column_order:
            if not position.can_play(col):
                continue
            position.play_col(col)
            if position.can_win_next():
                score = (WIDTH * HEIGHT + 1 - position.moves) // 2
            else:
                score = -self._negamax_heuristic(position, depth - 1, -beta, -alpha)
            position.undo()
            value = max(value, score)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    def _negamax_exact(self, position: Position, alpha: int, beta: int) -> int:
        assert alpha < beta
        assert not position.can_win_next()

        self.node_count += 1

        possible = position.possible_non_losing_moves()
        if possible == 0:
            return -(WIDTH * HEIGHT - position.moves) // 2

        if position.moves >= WIDTH * HEIGHT - 2:
            return 0

        minimum = -(WIDTH * HEIGHT - 2 - position.moves) // 2
        if alpha < minimum:
            alpha = minimum
            if alpha >= beta:
                return alpha

        maximum = (WIDTH * HEIGHT - 1 - position.moves) // 2
        if beta > maximum:
            beta = maximum
            if alpha >= beta:
                return beta

        key = position.key()
        book_score = lookup_score(key)
        if book_score is not None:
            return book_score

        cached = self.transposition.get(key)
        if cached is not None:
            if cached > MAX_SCORE - MIN_SCORE + 1:
                minimum = cached + 2 * MIN_SCORE - MAX_SCORE - 2
                if alpha < minimum:
                    alpha = minimum
                    if alpha >= beta:
                        return alpha
            else:
                maximum = cached + MIN_SCORE - 1
                if beta > maximum:
                    beta = maximum
                    if alpha >= beta:
                        return beta

        ordered_moves: list[tuple[int, int]] = []
        for col in self.column_order:
            move = possible & column_mask(col)
            if move:
                ordered_moves.append((position.move_score(move), move))
        ordered_moves.sort(reverse=True)

        for _, move in ordered_moves:
            position.play(move)
            score = -self._negamax_exact(position, -beta, -alpha)
            position.undo()
            if score >= beta:
                self.transposition[key] = score + MAX_SCORE - 2 * MIN_SCORE + 2
                return score
            if score > alpha:
                alpha = score

        self.transposition[key] = alpha - MIN_SCORE + 1
        return alpha
