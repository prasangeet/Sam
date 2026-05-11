from src.tools.browser_tool import BrowserTool
from src.tools.search_tool import SearchTool
from src.tools.open_folder_tool import OpenFolderTool
from src.tools.terminal_tool import TerminalTool


TOOLS = {
    "open_browser": BrowserTool(),
    "search": SearchTool(),
    "open_folder": OpenFolderTool(),
    "run_terminal_command": TerminalTool(),
}
