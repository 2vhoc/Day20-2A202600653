"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from langgraph.graph import StateGraph, END
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.agents.critic import CriticAgent


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""

    def build(self) -> object:
        """Create a LangGraph graph."""
        workflow = StateGraph(ResearchState)
        
        supervisor = SupervisorAgent()
        researcher = ResearcherAgent()
        analyst = AnalystAgent()
        writer = WriterAgent()
        critic = CriticAgent()
        
        workflow.add_node("supervisor", supervisor.run)
        workflow.add_node("researcher", researcher.run)
        workflow.add_node("analyst", analyst.run)
        workflow.add_node("writer", writer.run)
        workflow.add_node("critic", critic.run)
        
        workflow.set_entry_point("supervisor")
        
        def route_next(state: ResearchState) -> str:
            return state.route_history[-1] if state.route_history else "__end__"
            
        workflow.add_conditional_edges(
            "supervisor",
            route_next,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                "__end__": END
            }
        )
        
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")
        
        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        app = self.build()
        result = app.invoke(state)
        
        if isinstance(result, dict):
            return ResearchState.model_validate(result)
        return result
