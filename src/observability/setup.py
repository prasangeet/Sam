from src.observability.bus import event_bus
from src.observability.subscribers.console import ConsoleSubscriber

def setup_observability():
    console = ConsoleSubscriber()

    event_bus.subscribe(
        "*",
        console.handle
    )
