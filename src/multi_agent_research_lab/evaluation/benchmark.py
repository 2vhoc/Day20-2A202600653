"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object.

    TODO(student): Add quality scoring, estimated token cost, citation coverage, and error rate.
    """

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    quality_score = 5.0
    if state.final_answer and len(state.final_answer) > 200:
        quality_score += 3.0
    if state.sources:
        quality_score += 2.0
        
    cost = 0.001 * state.iteration
    
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=cost,
        quality_score=min(quality_score, 10.0)
    )
    return state, metrics
