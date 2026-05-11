import time
import subprocess

from src.tools.base_tool import (
    BaseTool
)

from src.observability.bus import (
    event_bus
)


SAFE_COMMANDS = {
    "fastfetch",
    "pipes.sh",
    "htop"
}


class TerminalTool(BaseTool):

    name = "run_terminal_command"

    def execute(
        self,
        params: dict
    ) -> str:

        command = params.get(
            "command"
        )

        event_bus.emit(
            "terminal_command_started",
            {
                "command": command
            }
        )

        if not command:

            event_bus.emit(
                "terminal_command_failed",
                {
                    "reason": "missing_command"
                }
            )

            return "No command provided"

        base = command.split()[0]

        if base not in SAFE_COMMANDS:

            event_bus.emit(
                "terminal_command_blocked",
                {
                    "command": command,
                    "blocked_base": base
                }
            )

            return (
                f"Blocked command: "
                f"{base}"
            )

        start = time.time()

        try:

            process = subprocess.Popen([
                "kitty",
                "--hold",
                "bash",
                "-c",
                command
            ])

            latency = round(
                time.time() - start,
                3
            )

            event_bus.emit(
                "terminal_command_completed",
                {
                    "command": command,
                    "pid": process.pid,
                    "latency": latency
                }
            )

            return (
                f"Running {command}"
            )

        except Exception as e:

            event_bus.emit(
                "terminal_command_failed",
                {
                    "command": command,
                    "error": str(e)
                }
            )

            return str(e)
