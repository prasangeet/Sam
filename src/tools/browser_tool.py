import webbrowser

from src.tools.base_tool import BaseTool


class BrowserTool(BaseTool):

    name = "open_browser"

    def execute(self, params: dict):

        url = params.get("url")

        if not url:
            return "No URL provided"

        webbrowser.open(url)

        return f"Opened {url}"
