import yaml

def load_prompt(path="src/prompts/assistant.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)
