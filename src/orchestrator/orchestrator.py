from src.memory.memory_store import (
    MemoryStore
)

from src.agents.response_agent import (
    ResponseAgent
)

from src.tools.executor import (
    ToolExecutor
)

from src.observability.bus import (
    event_bus
)


class Orchestrator:

    def __init__(self) -> None:

        self.memory = MemoryStore()

        self.agent = ResponseAgent()

        self.tool_executor = ToolExecutor()

    # Store user message
    def store_user_event(
        self,
        user_input
    ):

        self.memory.add_event(
            role="user",
            content=user_input
        )

        event_bus.emit(
            "user_event_stored",
            {
                "text": user_input
            }
        )

    # Build conversation context
    def build_context(self):

        context = self.memory.build_context()

        event_bus.emit(
            "context_built",
            {
                "history_count": len(
                    context["history"]
                ),
                "has_profile": bool(
                    context["profile"]
                )
            }
        )

        return context

    # Generate response from LLM
    def generate_response(
        self,
        user_input,
        context
    ):

        event_bus.emit(
            "llm_request_started",
            {}
        )

        result = self.agent.run(
            user_input,
            context
        )

        event_bus.emit(
            "llm_request_completed",
            {
                "action": result.action.type
            }
        )

        return result

    # Update user profile
    def update_profile(
        self,
        result
    ):

        profile_data = (
            result.profile.model_dump()
        )

        self.memory.update_profile(
            profile_data
        )

        event_bus.emit(
            "profile_updated",
            profile_data
        )

    # Store long-term memory
    def store_memory(
        self,
        result
    ):

        if result.memory.fact:

            self.memory.add_memory(
                result.memory.fact
            )

            event_bus.emit(
                "memory_stored",
                {
                    "fact": result.memory.fact
                }
            )

    # Execute tool action
    def execute_action(
        self,
        result
    ):

        if result.action.type == "none":

            event_bus.emit(
                "tool_skipped",
                {}
            )

            return None

        event_bus.emit(
            "tool_execution_started",
            {
                "tool": result.action.type,
                "params": result.action.params
            }
        )

        try:

            output = self.tool_executor.execute(
                result.action
            )

            event_bus.emit(
                "tool_execution_completed",
                {
                    "tool": result.action.type
                }
            )

            return output

        except Exception as e:

            event_bus.emit(
                "tool_execution_failed",
                {
                    "tool": result.action.type,
                    "error": str(e)
                }
            )

            raise

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

        event_bus.emit(
            "assistant_event_stored",
            {
                "response": response_text,
                "action": result.action.type
            }
        )

    # Main pipeline
    def handle(
        self,
        user_input
    ):

        event_bus.emit(
            "request_started",
            {
                "input": user_input
            }
        )

        try:

            # Save user input
            self.store_user_event(
                user_input
            )

            # Build memory context
            context = self.build_context()

            # Get LLM result
            result = self.generate_response(
                user_input,
                context
            )

            # Extract response text
            response_text = (
                result.response.content
            )

            # Update profile data
            self.update_profile(
                result
            )

            # Store memory facts
            self.store_memory(
                result
            )

            # Execute tool
            tool_output = self.execute_action(
                result
            )

            # Save assistant response
            self.store_assistant_event(
                result,
                response_text
            )

            event_bus.emit(
                "request_completed",
                {
                    "response": response_text
                }
            )

            return response_text, tool_output

        except Exception as e:

            event_bus.emit(
                "request_failed",
                {
                    "error": str(e)
                }
            )

            raise
