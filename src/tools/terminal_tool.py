import subprocess

from src.tools.base_tool import BaseTool

SAFE_COMMANDS = {
    "fastfetch",
    "pipes.sh",
    "htop"
}

class TerminalTool(BaseTool):

    name = "run_terminal_command"

    def execute(self, params: dict) -> str:
        command = params.get("command")

        if not command:
            return "No command Provided"

        base = command.split()[0]

        if base not in SAFE_COMMANDS:
            return f"Blocked command: {base}"

        try:
            subprocess.Popen([
                "kitty",
                "--hold",
                "bash",
                "-c",
                command
            ])

            return f"Running {command}"

        except Exception as e:
            return str(e)
