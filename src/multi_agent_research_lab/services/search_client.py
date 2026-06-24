"""Search client abstraction for ResearcherAgent."""

import uuid

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        # Simple mock search to allow the lab to run without external API keys.
        return [
            SourceDocument(
                title=f"Search Result {i+1} for: {query}",
                url=f"https://example.com/search?q={query.replace(' ', '+')}&page={i+1}",
                snippet=f"This is a mocked search snippet providing information about '{query}'. It contains some detailed explanation as if it was extracted from a real webpage. Result index {i+1}.",
                metadata={"source": "mock_search", "score": 0.9 - (i * 0.1)}
            )
            for i in range(min(max_results, 3))
        ]
