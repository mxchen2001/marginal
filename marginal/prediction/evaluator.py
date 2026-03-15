"""LLM evaluator — chain-of-thought probability estimation."""

from __future__ import annotations

from dataclasses import dataclass

from marginal.prediction.assembler import MarketContextBundle


@dataclass
class Evaluation:
    """LLM evaluation result for a market."""

    p_yes: float
    confidence: str  # "low" | "medium" | "high"
    edge: float
    reasoning: str


async def evaluate_market(bundle: MarketContextBundle) -> Evaluation:
    """Run the LLM evaluator on a market context bundle."""
    raise NotImplementedError
