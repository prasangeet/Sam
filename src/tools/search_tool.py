import webbrowser
from urllib.parse import quote

from src.tools.base_tool import BaseTool


class SearchTool(BaseTool):

    name = "search"

    def execute(self, params: dict):

        query = params.get("query")

        if not query:
            return "No query provided"

        url = f"https://www.google.com/search?q={quote(query)}"

        webbrowser.open(url)

        return f"Searching for {query}"
