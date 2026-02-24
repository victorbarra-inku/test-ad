"""Custom search toolkit for ROMA demonstrations."""

import os
from typing import List, Dict, Any, Optional
from config.settings import Settings


class CustomSearchToolkit:
    """Search toolkit that can use real APIs or mock data."""
    
    def __init__(self):
        """Initialize search toolkit."""
        self.settings = Settings()
        self.has_api_key = bool(self.settings.SEARCH_API_KEY)
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for information.
        
        If SEARCH_API_KEY is set, uses real API.
        Otherwise, returns mock results for demonstration.
        """
        if self.has_api_key:
            return self._real_search(query, num_results)
        else:
            return self._mock_search(query, num_results)
    
    def _real_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Perform real search using API."""
        # In a real implementation, this would call a search API
        # For now, return mock results even with API key
        # (since we don't know which search API to use)
        return self._mock_search(query, num_results)
    
    def _mock_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Return mock search results for demonstration."""
        query_lower = query.lower()
        
        # Mock results based on query keywords
        if "ai safety" in query_lower or "artificial intelligence safety" in query_lower:
            return [
                {
                    "title": "AI Safety Research: Current Developments and Challenges",
                    "snippet": "Recent advances in AI safety focus on alignment, robustness, and interpretability. Key areas include value alignment, adversarial robustness, and transparency.",
                    "url": "https://example.com/ai-safety-research",
                    "relevance": 0.95
                },
                {
                    "title": "The Alignment Problem in Machine Learning",
                    "snippet": "The alignment problem refers to ensuring AI systems pursue intended goals. Research explores reward modeling, interpretability, and human feedback.",
                    "url": "https://example.com/alignment-problem",
                    "relevance": 0.90
                },
                {
                    "title": "AI Governance and Safety Standards",
                    "snippet": "Governments and organizations are developing frameworks for AI safety. Topics include risk assessment, testing protocols, and deployment guidelines.",
                    "url": "https://example.com/ai-governance",
                    "relevance": 0.85
                },
                {
                    "title": "Recent Breakthroughs in AI Safety Research",
                    "snippet": "2024 has seen significant progress in AI safety, including new techniques for model interpretability and improved alignment methods.",
                    "url": "https://example.com/ai-safety-breakthroughs",
                    "relevance": 0.80
                },
                {
                    "title": "Ethical AI and Safety Considerations",
                    "snippet": "Ethical considerations in AI development include fairness, privacy, and safety. Researchers are developing tools to assess and mitigate risks.",
                    "url": "https://example.com/ethical-ai",
                    "relevance": 0.75
                }
            ]
        
        elif "python" in query_lower or "javascript" in query_lower:
            return [
                {
                    "title": f"Comparison: {query.title()}",
                    "snippet": f"Comprehensive comparison of {query} features, use cases, and best practices.",
                    "url": f"https://example.com/{query.replace(' ', '-')}",
                    "relevance": 0.90
                }
            ] * num_results
        
        else:
            # Generic mock results
            return [
                {
                    "title": f"Information about {query}",
                    "snippet": f"Detailed information and analysis about {query}. This includes key concepts, applications, and recent developments.",
                    "url": f"https://example.com/{query.replace(' ', '-')}",
                    "relevance": 0.85
                }
                for i in range(num_results)
            ]
