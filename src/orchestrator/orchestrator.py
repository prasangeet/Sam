from src.memory.memory_store import MemoryStore
from src.agents.response_agent import ResponseAgent

from src.tools.executor import ToolExecutor


class Orchestrator:

    def __init__(self) -> None:
        self.memory = MemoryStore()
        self.agent = ResponseAgent()
        self.tool_executor = ToolExecutor()

    # Store user message
    def store_user_event(self, user_input):
        self.memory.add_event(
            role="user",
            content=user_input
        )

    # Build conversation context
    def build_context(self):
        return self.memory.build_context()

    # Generate response from LLM
    def generate_response(self, user_input, context):
        return self.agent.run(
            user_input,
            context
        )

    # Update user profile
    def update_profile(self, result):
        self.memory.update_profile(
            result.profile.model_dump()
        )

    # Store long-term memory
    def store_memory(self, result):

        if result.memory.fact:
            self.memory.add_memory(
                result.memory.fact
            )

    # Execute tool action
    def execute_action(self, result):

        if result.action.type == "none":
            return None

        return self.tool_executor.execute(
            result.action
        )

    # Store assistant response
    def store_assistant_event(
        self,
        result,
        response_text
    ):

        self.memory.add_event(
            role="assistant",
            content=response_text,
            action_type=result.action.type,
            action_params=result.action.params
        )

    # Main pipeline
    def handle(self, user_input):

        # Save user input
        self.store_user_event(user_input)

        # Build memory context
        context = self.build_context()

        # Get LLM result
        result = self.generate_response(
            user_input,
            context
        )

        # Extract response text
        response_text = result.response.content

        # Update profile data
        self.update_profile(result)

        # Store memory facts
        self.store_memory(result)

        # Execute tool
        tool_output = self.execute_action(result)

        # Save assistant response
        self.store_assistant_event(
            result,
            response_text
        )

        return response_text, tool_output
