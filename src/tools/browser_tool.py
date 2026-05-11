import time
import webbrowser

from src.tools.base_tool import (
    BaseTool
)

from src.observability.bus import (
    event_bus
)


class BrowserTool(BaseTool):

    name = "open_browser"

    def execute(
        self,
        params: dict
    ):

        url = params.get("url")

        event_bus.emit(
            "browser_tool_started",
            {
                "url": url
            }
        )

        if not url:

            event_bus.emit(
                "browser_tool_failed",
                {
                    "reason": "missing_url"
                }
            )

            return "No URL provided"

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
                    "browser_tool_failed",
                    {
                        "url": url,
                        "reason": "open_failed"
                    }
                )

                return (
                    f"Failed to open {url}"
                )

            event_bus.emit(
                "browser_tool_completed",
                {
                    "url": url,
                    "latency": latency
                }
            )

            return f"Opened {url}"

        except Exception as e:

            event_bus.emit(
                "browser_tool_failed",
                {
                    "url": url,
                    "error": str(e)
                }
            )

            raise
