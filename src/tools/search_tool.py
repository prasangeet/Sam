import time
import webbrowser

from urllib.parse import quote

from src.tools.base_tool import (
    BaseTool
)

from src.observability.bus import (
    event_bus
)


class SearchTool(BaseTool):

    name = "search"

    def execute(
        self,
        params: dict
    ):

        query = params.get(
            "query"
        )

        event_bus.emit(
            "search_started",
            {
                "query": query
            }
        )

        if not query:

            event_bus.emit(
                "search_failed",
                {
                    "reason": "missing_query"
                }
            )

            return "No query provided"

        encoded_query = quote(
            query
        )

        url = (
            "https://www.google.com/search?q="
            f"{encoded_query}"
        )

        start = time.time()

        try:

            success = webbrowser.open(
                url
            )

            latency = round(
                time.time() - start,
                3
            )

            if not success:

                event_bus.emit(
                    "search_failed",
                    {
                        "query": query,
                        "reason": "browser_open_failed"
                    }
                )

                return (
                    f"Failed to search "
                    f"for {query}"
                )

            event_bus.emit(
                "search_completed",
                {
                    "query": query,
                    "url": url,
                    "latency": latency
                }
            )

            return (
                f"Searching for "
                f"{query}"
            )

        except Exception as e:

            event_bus.emit(
                "search_failed",
                {
                    "query": query,
                    "error": str(e)
                }
            )

            return str(e)
