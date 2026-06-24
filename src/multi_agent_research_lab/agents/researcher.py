"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.search = SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        query = state.request.query
        
        # 1. Search
        docs = self.search.search(query, max_results=state.request.max_sources)
        state.sources.extend(docs)
        
        # 2. Summarize findings
        system_prompt = "You are a professional research agent. Summarize the provided sources into concise research notes."
        
        sources_text = "\n\n".join([f"Title: {doc.title}\nURL: {doc.url}\nSnippet: {doc.snippet}" for doc in docs])
        user_prompt = f"Query: {query}\n\nSources:\n{sources_text}"
        
        response = self.llm.complete(system_prompt, user_prompt)
        state.research_notes = response.content
        
        return state
