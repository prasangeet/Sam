import time
import subprocess

from pathlib import Path

from src.tools.base_tool import (
    BaseTool
)

from src.observability.bus import (
    event_bus
)


FOLDERS = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "projects": Path.home() / "Projects",
}


class OpenFolderTool(BaseTool):

    name = "open_folder"

    def execute(
        self,
        params: dict
    ):

        folder = params.get(
            "folder"
        )

        event_bus.emit(
            "open_folder_started",
            {
                "folder": folder
            }
        )

        if folder not in FOLDERS:

            event_bus.emit(
                "open_folder_failed",
                {
                    "folder": folder,
                    "reason": "unknown_folder"
                }
            )

            return (
                f"Unknown folder: "
                f"{folder}"
            )

        path = FOLDERS[folder]

        start = time.time()

        try:

            process = subprocess.Popen([
                "xdg-open",
                str(path)
            ])

            latency = round(
                time.time() - start,
                3
            )

            event_bus.emit(
                "open_folder_completed",
                {
                    "folder": folder,
                    "path": str(path),
                    "pid": process.pid,
                    "latency": latency
                }
            )

            return f"Opened {folder}"

        except Exception as e:

            event_bus.emit(
                "open_folder_failed",
                {
                    "folder": folder,
                    "path": str(path),
                    "error": str(e)
                }
            )

            return str(e)
