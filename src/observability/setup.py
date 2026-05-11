from src.observability.bus import event_bus
from src.observability.subscribers.console import ConsoleSubscriber
from src.observability.subscribers.file import FileSubscriber
from src.observability.subscribers.websocket import WebsocketSubscriber

def setup_observability():
    console = ConsoleSubscriber()
    file = FileSubscriber()
    websocket = WebsocketSubscriber()

    event_bus.subscribe(
        "*",
        console.handle
    )
    event_bus.subscribe(
        "*",
        file.handle
    )
    event_bus.subscribe(
        "*",
        websocket.handle
    )
