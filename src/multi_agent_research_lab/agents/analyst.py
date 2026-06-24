"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        system_prompt = "You are an expert analyst. Extract key claims, compare viewpoints, and flag weak evidence from the given research notes."
        
        user_prompt = f"Research Notes:\n{state.research_notes}"
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.analysis_notes = response.content
        
        return state
