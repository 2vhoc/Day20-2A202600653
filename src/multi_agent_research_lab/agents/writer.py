"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        system_prompt = "You are an expert writer. Synthesize a clear response with citations or source references based on the research and analysis provided."
        
        user_prompt = f"Query: {state.request.query}\nAudience: {state.request.audience}\n\nResearch Notes:\n{state.research_notes}\n\nAnalysis Notes:\n{state.analysis_notes}"
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        
        return state
