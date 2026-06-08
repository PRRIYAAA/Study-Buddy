import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query):
    """
    Search the web using Tavily.
    Returns a clean string of results.
    """
    try:
        response = client.search(
            query=query,
            max_results=5,
            search_depth="basic"
        )

        results = []
        for r in response.get("results", []):
            results.append(f"Title: {r['title']}\nURL: {r['url']}\nSummary: {r['content']}\n")

        return "\n---\n".join(results)

    except Exception as e:
        return f"Web search failed: {str(e)}"