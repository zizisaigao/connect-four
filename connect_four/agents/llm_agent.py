"""Large language model agent placeholder.

The agent formats the board as text and can call an external API when configured.
This is useful for comparing LLM reasoning against the perfect solver baseline.
"""

from __future__ import annotations

import json
import os
import re
from typing import Callable

from connect_four.agents.base import Agent
from connect_four.agents.solver_agent import SolverAgent
from connect_four.board import Position


class LLMAgent(Agent):
    name = "llm"

    def __init__(
        self,
        api_call: Callable[[str], str] | None = None,
        fallback_to_solver: bool = True,
    ) -> None:
        self.api_call = api_call or self._default_api_call
        self.fallback_to_solver = fallback_to_solver
        self._solver = SolverAgent() if fallback_to_solver else None

    def choose_move(self, position: Position, player: int) -> int:
        prompt = self._build_prompt(position, player)
        try:
            response = self.api_call(prompt)
            col = self._parse_column(response, position.legal_columns())
            if col is not None:
                return col
        except Exception:
            pass

        if self._solver is None:
            raise RuntimeError("LLM failed and no solver fallback is configured")
        return self._solver.choose_move(position, player)

    def _build_prompt(self, position: Position, player: int) -> str:
        legal = [col + 1 for col in position.legal_columns()]
        return (
            "You are playing Connect Four on a 7x6 board.\n"
            "Columns are numbered 1-7 from left to right.\n"
            "You are player "
            f"{player}. Current board:\n"
            f"{position.render(perspective=player)}\n"
            f"Legal moves (1-based columns): {legal}\n"
            "Reply with JSON: {\"column\": <number>}."
        )

    def _parse_column(self, response: str, legal: list[int]) -> int | None:
        try:
            payload = json.loads(response)
            col = int(payload["column"]) - 1
            if col in legal:
                return col
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            pass

        match = re.search(r"\b([1-7])\b", response)
        if match:
            col = int(match.group(1)) - 1
            if col in legal:
                return col
        return None

    def _default_api_call(self, prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Configure an api_call or use solver fallback."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai package to use the default LLM backend") from exc

        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=os.getenv("CONNECT_FOUR_LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You play Connect Four optimally when possible."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        return completion.choices[0].message.content or ""
