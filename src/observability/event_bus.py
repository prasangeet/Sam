from collections import defaultdict

class EventBus:

    def __init__(self) -> None:
        self.subscribers = defaultdict(list)

    def subscribe(
        self,
        event_type,
        callback,
    ):
        self.subscribers[event_type].append(
            callback
        )

    def emit(
        self,
        event_type,
        data=None
    ): 
        event = {
            "type": event_type,
            "data": data or {}
        }

        for callback in self.subscribers[event_type]:
            try:
                callback(event)
            except Exception as e:
                print(
                    f"[EventBus Error] {e}"
                )

        for callback in self.subscribers["*"]:
            try:
                callback(event)

            except Exception as e:
                print(
                    f"[EventBus Error] {e}"
                )
