import asyncio
import threading

from fastapi import FastAPI
from fastapi import WebSocket

from fastapi.websockets import (
    WebSocketDisconnect
)

import uvicorn


class LogServer:

    def __init__(
        self,
        host="127.0.0.1",
        port=8001
    ):

        self.host = host
        self.port = port

        self.app = FastAPI()

        self.clients = set()

        self.loop = None

        self.server_thread = None

        self.setup_routes()

    # -----------------------------------
    # Setup websocket routes
    # -----------------------------------
    def setup_routes(self):

        @self.app.websocket("/logs")
        async def websocket_logs(
            websocket: WebSocket
        ):

            await self.connect(websocket)

            try:

                # passive connection
                while True:
                    await asyncio.sleep(3600)

            except WebSocketDisconnect:

                await self.disconnect(
                    websocket
                )

            except Exception as e:

                print(
                    f"[LogServer Error] {e}"
                )

                await self.disconnect(
                    websocket
                )

    # -----------------------------------
    # Connect websocket client
    # -----------------------------------
    async def connect(
        self,
        websocket: WebSocket
    ):

        try:

            await websocket.accept()

            self.clients.add(
                websocket
            )

            print(
                f"[LogServer] "
                f"Client connected "
                f"({len(self.clients)} total)"
            )

        except Exception as e:

            print(
                f"[LogServer Error] "
                f"Connection failed: {e}"
            )

    # -----------------------------------
    # Disconnect websocket client
    # -----------------------------------
    async def disconnect(
        self,
        websocket: WebSocket
    ):

        try:

            if websocket in self.clients:

                self.clients.remove(
                    websocket
                )

            print(
                f"[LogServer] "
                f"Client disconnected "
                f"({len(self.clients)} total)"
            )

        except Exception as e:

            print(
                f"[LogServer Error] "
                f"Disconnect failed: {e}"
            )

    # -----------------------------------
    # Broadcast message
    # -----------------------------------
    async def broadcast(
        self,
        message: str
    ):

        if not self.clients:
            return

        dead_clients = []

        for client in self.clients:

            try:

                await client.send_text(
                    message
                )

            except Exception as e:

                print(
                    f"[LogServer Error] "
                    f"Broadcast failed: {e}"
                )

                dead_clients.append(
                    client
                )

        # cleanup dead clients
        for client in dead_clients:

            await self.disconnect(
                client
            )

    # -----------------------------------
    # Thread-safe emit
    # -----------------------------------
    def emit(
        self,
        message: str
    ):

        if not self.loop:
            return

        try:

            asyncio.run_coroutine_threadsafe(
                self.broadcast(message),
                self.loop
            )

        except Exception as e:

            print(
                f"[LogServer Error] "
                f"Emit failed: {e}"
            )

    # -----------------------------------
    # Internal server runner
    # -----------------------------------
    def _run_server(self):

        self.loop = asyncio.new_event_loop()

        asyncio.set_event_loop(
            self.loop
        )

        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning"
        )

        server = uvicorn.Server(
            config
        )

        self.loop.run_until_complete(
            server.serve()
        )

    # -----------------------------------
    # Public start method
    # -----------------------------------
    def start(self):

        if self.server_thread:
            return

        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )

        self.server_thread.start()

        print(
            f"[LogServer] Running on "
            f"ws://{self.host}:{self.port}/logs"
        )
