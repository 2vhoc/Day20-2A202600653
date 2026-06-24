"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        if not state.final_answer or not state.research_notes:
            return state
            
        system_prompt = (
            "You are an expert fact-checker and editor. Review the final answer against the research notes. "
            "Identify any hallucinations, unsupported claims, or missing references. "
            "Rewrite the final answer to be completely factual based only on the research notes. "
            "If the answer is already perfect, just return it as is."
        )
        
        user_prompt = f"Research Notes:\n{state.research_notes}\n\nFinal Answer Draft:\n{state.final_answer}"
        
        from multi_agent_research_lab.services.llm_client import LLMClient
        llm = LLMClient()
        response = llm.complete(system_prompt, user_prompt)
        
        # Append critic's review to the final answer or replace it.
        state.final_answer = response.content
        state.record_route("critic")
        
        return state
