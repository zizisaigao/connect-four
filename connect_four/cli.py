"""Command-line interface for Connect Four."""

from __future__ import annotations

import argparse
import time

from connect_four.agents.human_agent import HumanAgent
from connect_four.agents.random_agent import RandomAgent
from connect_four.agents.solver_agent import SolverAgent
from connect_four.board import Position
from connect_four.game import Game, GameResult, play_game
from connect_four.solver import Solver


def _format_scores(scores: list[int]) -> str:
    parts = []
    for idx, score in enumerate(scores):
        if score == -1000:
            parts.append(f"{idx + 1}: --")
        else:
            sign = "+" if score > 0 else ""
            parts.append(f"{idx + 1}: {sign}{score}")
    return "  ".join(parts)


def cmd_analyze(args: argparse.Namespace) -> None:
    position = Position.from_sequence(args.sequence) if args.sequence else Position()
    solver = Solver()
    start = time.perf_counter()
    scores = solver.analyze(position, exact=args.exact)
    elapsed = time.perf_counter() - start
    best = solver.best_move(position, exact=args.exact)

    print(position.render())
    print()
    print(f"Scores by column: {_format_scores(scores)}")
    print(f"Best move: column {best + 1}")
    print(f"Score: {solver.solve(position, exact=args.exact)}")
    print(f"Nodes explored: {solver.node_count:,}")
    print(f"Time: {elapsed:.3f}s")
    if not args.exact:
        print("Tip: use --exact for endgame-perfect analysis (slower in opening)")


def cmd_play(args: argparse.Namespace) -> None:
    agents = {
        "human": HumanAgent(),
        "random": RandomAgent(seed=args.seed),
        "solver": SolverAgent(),
    }
    player_one = agents[args.p1]
    player_two = agents[args.p2]

    print(f"Player 1: {player_one.name}")
    print(f"Player 2: {player_two.name}")
    result = play_game(player_one, player_two, verbose=True)

    if result == GameResult.PLAYER_ONE_WIN:
        print(f"\n{player_one.name} wins!")
    elif result == GameResult.PLAYER_TWO_WIN:
        print(f"\n{player_two.name} wins!")
    else:
        print("\nDraw.")


def cmd_benchmark(args: argparse.Namespace) -> None:
    sequences = ["", "3", "35", "354", "3542", "35426"]
    solver = Solver()
    print("Position | Best | Score | Nodes | Time(ms)")
    print("-" * 48)
    for sequence in sequences:
        position = Position.from_sequence(sequence)
        solver.reset_stats()
        start = time.perf_counter()
        score = solver.solve(position)
        best = solver.best_move(position)
        elapsed = (time.perf_counter() - start) * 1000
        label = sequence or "empty"
        print(f"{label:8} | {best + 1:4} | {score:+5} | {solver.node_count:5} | {elapsed:7.1f}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Connect Four perfect-play engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a position")
    analyze.add_argument(
        "--sequence",
        default="",
        help="Move sequence using columns 1-7, e.g. 3542",
    )
    analyze.add_argument(
        "--exact",
        action="store_true",
        help="Use exact solver when the remaining search space is small",
    )
    analyze.set_defaults(func=cmd_analyze)

    play = subparsers.add_parser("play", help="Play a game")
    play.add_argument("--p1", choices=["human", "random", "solver"], default="human")
    play.add_argument("--p2", choices=["human", "random", "solver"], default="solver")
    play.add_argument("--seed", type=int, default=42)
    play.set_defaults(func=cmd_play)

    benchmark = subparsers.add_parser("benchmark", help="Benchmark solver speed")
    benchmark.set_defaults(func=cmd_benchmark)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
