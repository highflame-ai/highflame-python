"""Web search tool using DuckDuckGo."""

from langchain_core.tools import tool
from typing import Optional
import os

try:
    # Try new package name first
    from ddgs import DDGS

    DDGS_AVAILABLE = True
except ImportError:
    try:
        # Fallback to old package name
        from duckduckgo_search import DDGS

        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False


@tool
def web_search_tool(query: str, max_results: int = 5) -> str:
    """
    Search the web for current information that may not be in the knowledge base.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)

    Returns:
        A formatted string with search results, or an error message if search fails.
    """
    if not DDGS_AVAILABLE:
        return (
            "Error: DuckDuckGo search is not available. "
            "Install it with: pip install duckduckgo-search"
        )

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"No results found for query: '{query}'"

        result_text = f"Web Search Results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            result_text += f"{i}. {result.get('title', 'No title')}\n"
            result_text += f"   URL: {result.get('href', 'No URL')}\n"
            result_text += f"   {result.get('body', 'No description')[:200]}...\n\n"

        return result_text
    except Exception as e:
        return f"Error performing web search: {str(e)}"


@tool
def web_search_news_tool(query: str, max_results: int = 5) -> str:
    """
    Search for recent news articles related to the query.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)

    Returns:
        A formatted string with news search results.
    """
    if not DDGS_AVAILABLE:
        return (
            "Error: DuckDuckGo search is not available. "
            "Install it with: pip install duckduckgo-search"
        )

    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))

        if not results:
            return f"No news results found for query: '{query}'"

        result_text = f"News Results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            result_text += f"{i}. {result.get('title', 'No title')}\n"
            result_text += f"   Source: {result.get('source', 'Unknown')}\n"
            result_text += f"   URL: {result.get('url', 'No URL')}\n"
            result_text += f"   {result.get('body', 'No description')[:200]}...\n\n"

        return result_text
    except Exception as e:
        return f"Error performing news search: {str(e)}"
