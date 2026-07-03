import httpx
from app.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    """
    Lightweight web-search tool using DuckDuckGo's HTML endpoint (no API key
    required). Requires outbound internet access on the machine running the
    backend. Swap the `_run` body for Bing/Serper/Tavily if you have a key.
    """
    name = "web_search"
    description = "Search the web for a query and return top result titles/snippets/links."

    def validate(self, **kwargs):
        query = kwargs.get("query")
        if not query or not isinstance(query, str):
            return False, "Missing required string field 'query'"
        return True, None

    def _run(self, **kwargs):
        query = kwargs["query"]
        max_results = int(kwargs.get("max_results", 5))
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (AgentOS Research Agent)"},
            )
            resp.raise_for_status()

        # Minimal HTML scrape (kept dependency-free; swap for BeautifulSoup if preferred)
        import re
        results = []
        for m in re.finditer(
            r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', resp.text
        ):
            url, title = m.group(1), re.sub("<.*?>", "", m.group(2))
            results.append({"title": title, "url": url})
            if len(results) >= max_results:
                break

        return {"query": query, "results": results}
