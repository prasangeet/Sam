from src.tools.registry import TOOLS

class ToolExecutor:

    def execute(self, action):
        tool_type = action.type
        tool = TOOLS.get(tool_type)

        if not tool:
            return f"No tool found for '{tool_type}'"

        return tool.execute(action.params)
