import time

from src.tools.registry import (
    TOOLS
)

from src.observability.bus import (
    event_bus
)


class ToolExecutor:

    def execute(
        self,
        action
    ):

        tool_type = action.type

        event_bus.emit(
            "tool_lookup_started",
            {
                "tool": tool_type
            }
        )

        tool = TOOLS.get(
            tool_type
        )

        if not tool:

            event_bus.emit(
                "tool_lookup_failed",
                {
                    "tool": tool_type
                }
            )

            return (
                f"No tool found for "
                f"'{tool_type}'"
            )

        event_bus.emit(
            "tool_lookup_completed",
            {
                "tool": tool_type
            }
        )

        start = time.time()

        try:

            event_bus.emit(
                "tool_execute_started",
                {
                    "tool": tool_type,
                    "params": action.params
                }
            )

            result = tool.execute(
                action.params
            )

            latency = round(
                time.time() - start,
                3
            )

            event_bus.emit(
                "tool_execute_completed",
                {
                    "tool": tool_type,
                    "latency": latency
                }
            )

            return result

        except Exception as e:

            event_bus.emit(
                "tool_execute_failed",
                {
                    "tool": tool_type,
                    "error": str(e)
                }
            )

            raise
