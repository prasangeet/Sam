from pathlib import Path

import yaml


PROMPT_DIR = "src/prompts"


def load_prompt(
    path=PROMPT_DIR
):

    prompt_data = {}

    prompt_path = Path(path)

    yaml_files = list(
        prompt_path.glob("*.yaml")
    )

    for file in yaml_files:

        with open(
            file,
            "r"
        ) as f:

            data = yaml.safe_load(f)

            if data:

                prompt_data.update(data)

    return prompt_data
