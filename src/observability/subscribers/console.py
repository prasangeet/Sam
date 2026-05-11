from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

class ConsoleSubscriber:

    def __init__(self) -> None:
        self.console = Console()

    def handle(
        self,
        event,
    ):
        event_type = event["type"]

        data = event["data"]

        self.console.print(
            Panel.fit(
                Pretty(data),
                title=event_type,
                border_style="cyan"
            )
        )
