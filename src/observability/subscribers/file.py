import json
from pathlib import Path

class FileSubscriber:

    def __init__(
        self,
        log_file="logs/events.log"
    ):
        self.log_file=Path(log_file)

        self.log_file.parent.mkdir(
            exist_ok=True
        )

    def handle(
        self,
        event
    ):
        with open(
            self.log_file,
            "a"
        ) as f:
            f.write(
                json.dumps(event)
            )

            f.write("\n")
