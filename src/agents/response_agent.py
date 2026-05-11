import json
import time

import ollama

from src.schema.response_schema import (
    ResponseSchema
)

from src.prompts.loader import (
    load_prompt
)

from src.observability.bus import (
    event_bus
)


class ResponseAgent:

    def __init__(
        self,
        model="llama3"
    ) -> None:

        self.model = model

        event_bus.emit(
            "response_agent_initialized",
            {
                "model": model
            }
        )

    # -----------------------------------
    # Build prompt
    # -----------------------------------
    def build_prompt(
        self,
        user_input,
        context
    ):

        prompt_data = load_prompt()

        system = prompt_data["system"]

        rules = "\n".join(
            f"- {rule}"
            for rule in prompt_data["rules"]
        )

        actions = "\n".join(
            f"- {action}"
            for action in prompt_data["actions"]
        )

        examples = prompt_data["examples"]

        formatted_examples = []

        for ex in examples:

            formatted_examples.append(
                f"""
    User: "{ex["user"]}"

    {json.dumps(
        ex["output"],
        indent=4
    )}
    """
            )

        examples_text = (
            "\n----------------------------------------\n"
            .join(formatted_examples)
        )

        prompt = f"""
    {system}

    ----------------------------------------
    CONTEXT
    ----------------------------------------

    User Profile:
    {json.dumps(context["profile"], indent=4)}

    Recent Conversation:
    {json.dumps(context["history"], indent=4)}

    Memories:
    {json.dumps(context["memories"], indent=4)}

    ----------------------------------------
    TASK
    ----------------------------------------

    Analyze the user input and produce a structured response.

    ----------------------------------------
    CURRENT USER INPUT
    ----------------------------------------

    "{user_input}"

    ----------------------------------------
    OUTPUT FORMAT (STRICT JSON)
    ----------------------------------------

    {{
        "profile": {{
            "name": string or null,
            "date_of_birth": string or null
        }},
        "memory": {{
            "fact": string or null
        }},
        "action": {{
            "type": string,
            "params": {{}}
        }},
        "response": {{
            "content": string
        }}
    }}

    ----------------------------------------
    ACTION SCHEMAS
    ----------------------------------------

    open_browser:
    {{
        "type": "open_browser",
        "params": {{
            "url": "https://example.com"
        }}
    }}

    search:
    {{
        "type": "search",
        "params": {{
            "query": "python asyncio"
        }}
    }}

    run_terminal_command:
    {{
        "type": "run_terminal_command",
        "params": {{
            "command": "fastfetch"
        }}
    }}

    open_folder:
    {{
        "type": "open_folder",
        "params": {{
            "folder": "downloads"
        }}
    }}

    none:
    {{
        "type": "none",
        "params": {{}}
    }}

    ----------------------------------------
    RULES
    ----------------------------------------

    {rules}

    ----------------------------------------
    ALLOWED ACTIONS
    ----------------------------------------

    {actions}

    ----------------------------------------
    EXAMPLES
    ----------------------------------------

    {examples_text}

    ----------------------------------------
    FINAL INSTRUCTIONS
    ----------------------------------------

    1. Return ONLY valid JSON
    2. Do NOT return markdown
    3. Do NOT explain anything
    4. Every action MUST include correct params
    5. Browser actions MUST include full URL
    6. Search actions MUST include query
    7. Terminal actions MUST include command
    8. Folder actions MUST include folder
    9. Response MUST start with '{{'
    10. Response MUST end with '}}'
    """

        event_bus.emit(
            "prompt_built",
            {
                "input_length": len(
                    user_input
                ),
                "history_count": len(
                    context["history"]
                ),
                "memory_count": len(
                    context["memories"]
                ),
                "example_count": len(
                    examples
                )
            }
        )

        return prompt
    # -----------------------------------
    # Ollama call
    # -----------------------------------
    def call_llm(
        self,
        prompt
    ):

        event_bus.emit(
            "llm_call_started",
            {
                "model": self.model
            }
        )

        start = time.time()

        try:

            res = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            )

            latency = round(
                time.time() - start,
                3
            )

            content = (
                res["message"]["content"]
            )

            event_bus.emit(
                "llm_call_completed",
                {
                    "model": self.model,
                    "latency": latency,
                    "output_length": len(
                        content
                    )
                }
            )

            return content

        except Exception as e:

            event_bus.emit(
                "llm_call_failed",
                {
                    "model": self.model,
                    "error": str(e)
                }
            )

            raise

    # -----------------------------------
    # Clean model output
    # -----------------------------------
    def clean_output(
        self,
        text
    ):

        if not text:
            return text

        original_length = len(text)

        text = text.strip()

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:

            text = text[start:end + 1]

        event_bus.emit(
            "output_cleaned",
            {
                "original_length": original_length,
                "cleaned_length": len(text)
            }
        )

        return text

    # -----------------------------------
    # Parse and validate
    # -----------------------------------
    def safe_parse(
        self,
        text
    ):

        try:

            cleaned = self.clean_output(
                text
            )

            parsed = json.loads(
                cleaned
            )

            validated = (
                ResponseSchema.model_validate(
                    parsed
                )
            )

            event_bus.emit(
                "response_validated",
                {
                    "action": validated.action.type
                }
            )

            return validated

        except Exception as e:

            event_bus.emit(
                "response_validation_failed",
                {
                    "error": str(e),
                    "raw_output": text
                }
            )

            print("[Parse Error]", e)
            print("[Raw Output]", text)

            return None

    # -----------------------------------
    # Fallback response
    # -----------------------------------
    def fallback(self):

        event_bus.emit(
            "fallback_response_used",
            {}
        )

        return ResponseSchema()

    # -----------------------------------
    # Main pipeline
    # -----------------------------------
    def run(
        self,
        user_input,
        context
    ):

        event_bus.emit(
            "response_generation_started",
            {
                "input": user_input
            }
        )

        try:

            prompt = self.build_prompt(
                user_input,
                context
            )

            raw_output = self.call_llm(
                prompt
            )

            parsed = self.safe_parse(
                raw_output
            )

            # repair retry
            if parsed is None:

                event_bus.emit(
                    "repair_attempt_started",
                    {}
                )

                repair_prompt = f"""
Fix the following invalid JSON.

Return ONLY valid JSON.

{raw_output}
"""

                repaired = self.call_llm(
                    repair_prompt
                )

                parsed = self.safe_parse(
                    repaired
                )

            if parsed is None:

                parsed = self.fallback()

            event_bus.emit(
                "response_generation_completed",
                {
                    "action": parsed.action.type
                }
            )

            return parsed

        except Exception as e:

            event_bus.emit(
                "response_generation_failed",
                {
                    "error": str(e)
                }
            )

            raise
