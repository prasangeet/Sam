import json
import ollama

from src.schema.response_schema import ResponseSchema

from src.prompts.loader import load_prompt


class ResponseAgent:
    def __init__(self, model="llama3") -> None:
        self.model = model

    # -----------------------------------
    # 🧠 PROMPT
    # -----------------------------------
    def build_prompt(self, user_input, context):
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

        return f"""
    {system}

    ----------------------------------------
    CONTEXT
    ----------------------------------------

    User Profile:
    {context["profile"]}

    Recent Conversation:
    {context["history"]}

    User Input:
    "{user_input}"

    ----------------------------------------
    TASK
    ----------------------------------------

    Analyze the user input and produce a structured response.

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

    User: "my name is Alex"

    {{
        "profile": {{
            "name": "Alex",
            "date_of_birth": null
        }},
        "memory": {{
            "fact": null
        }},
        "action": {{
            "type": "none",
            "params": {{}}
        }},
        "response": {{
            "content": "Nice to meet you, Alex."
        }}
    }}

    ----------------------------------------

    User: "run fastfetch"

    {{
        "profile": {{
            "name": null,
            "date_of_birth": null
        }},
        "memory": {{
            "fact": null
        }},
        "action": {{
            "type": "run_terminal_command",
            "params": {{
                "command": "fastfetch"
            }}
        }},
        "response": {{
            "content": "Running fastfetch in terminal."
        }}
    }}

    ----------------------------------------

    FINAL INSTRUCTION:

    Return ONLY valid JSON.
    Do NOT include markdown.
    Do NOT include explanations.
    The response MUST start with '{{' and end with '}}'.
    """

    # -----------------------------------
    # 🧠 OLLAMA CALL
    # -----------------------------------
    def call_llm(self, prompt):
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

        return res["message"]["content"]

    # -----------------------------------
    # 🧠 CLEAN OUTPUT
    # -----------------------------------
    def clean_output(self, text):
        if not text:
            return text

        text = text.strip()

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            text = text[start:end + 1]

        return text

    # -----------------------------------
    # 🧠 SAFE PARSE
    # -----------------------------------
    def safe_parse(self, text):
        try:
            text = self.clean_output(text)

            parsed = json.loads(text)

            validated = ResponseSchema.model_validate(parsed)

            return validated

        except Exception as e:
            print("[Parse Error]", e)
            print("[Raw Output]", text)
            return None

    # -----------------------------------
    # 🧠 FALLBACK
    # -----------------------------------
    def fallback(self):
        return ResponseSchema()

    # -----------------------------------
    # 🧠 MAIN
    # -----------------------------------
    def run(self, user_input, context):
        prompt = self.build_prompt(user_input, context)

        raw_output = self.call_llm(prompt)

        parsed = self.safe_parse(raw_output)

        # 🔥 repair retry
        if parsed is None:
            repair_prompt = f"""
Fix the following invalid JSON.

Return ONLY valid JSON.

{raw_output}
"""

            repaired = self.call_llm(repair_prompt)

            parsed = self.safe_parse(repaired)

        if parsed is None:
            parsed = self.fallback()

        return parsed
