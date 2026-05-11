import subprocess
from pathlib import Path

from src.tools.base_tool import BaseTool


FOLDERS = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "projects": Path.home() / "Projects",
}


class OpenFolderTool(BaseTool):

    name = "open_folder"

    def execute(self, params: dict):

        folder = params.get("folder")

        if folder not in FOLDERS:
            return f"Unknown folder: {folder}"

        path = FOLDERS[folder]

        try:
            subprocess.Popen([
                "xdg-open",
                str(path)
            ])

            return f"Opened {folder}"

        except Exception as e:
            return str(e)
