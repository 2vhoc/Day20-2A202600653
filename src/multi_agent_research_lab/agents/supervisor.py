"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        # Safety check to prevent infinite loops
        if state.iteration >= 10:
            state.record_route("__end__")
            return state

        if not state.research_notes:
            state.record_route("researcher")
        elif not state.analysis_notes:
            state.record_route("analyst")
        elif not state.final_answer:
            state.record_route("writer")
        else:
            state.record_route("__end__")
            
        return state
