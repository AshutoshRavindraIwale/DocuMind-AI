"""
Web Search Tool using SerpAPI
"""

from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from typing import Optional
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for current information on any topic"
    serpapi_key: Optional[str] = None
    
    def __init__(self):
        super().__init__()
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not self.serpapi_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables")
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute web search"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "num": 5
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            # Extract search results
            results = []
            if "organic_results" in data:
                for result in data["organic_results"][:5]:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    link = result.get("link", "")
                    results.append(f"Title: {title}\nSnippet: {snippet}\nURL: {link}\n")
            
            return "\n".join(results) if results else "No results found."
            
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    def get_tool(self):
        """Return the tool instance"""
        return self

class WebSearchWrapper:
    """Wrapper for easier integration"""
    def __init__(self):
        self.tool = WebSearchTool()
    
    def search(self, query: str) -> str:
        return self.tool._run(query)