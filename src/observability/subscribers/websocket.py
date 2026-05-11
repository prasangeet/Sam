import json

from src.observability.server import log_server

class WebsocketSubscriber:

    def handle(
        self,
        event
    ):
        try:
            payload = json.dumps(
                event
            )

            log_server.emit(
                payload
            )

        except Exception as e:
            print(
                f"[WebsocketSubscriber Error] {e}"
            )
