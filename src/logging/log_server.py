

import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.requests import ClientDisconnect
import uvicorn


class LogServer:

    def __init(
        self,
        host="127.0.0.1",
        port=8001
    ):
        self.host=host
        self.port=port

        self.app = FastAPI()

        self.clients = set()

        self.logger = logging.getLogger(
            "sam.log_server"
        )

        self.setup_routes()

    def setup_routes(self):

        @self.app.websocket("/logs")
        async def websocket_endpoint(
                websocket: WebSocket
        ):
            await self.connect(websocket)

            try:
                while True:
                    await websocket.receive_text()

            except WebSocketDisconnect:
                await self.disconnect(websocket)

            except Exception as e:
                self.logger.error(
                    f"Websocker Error: {e}"
                )

                await self.disconnect(websocket)

    async def connect(
        self,
        websocket: WebSocket
    ):
        try:
            await websocket.accept()

            self.clients.add(websocket)

            self.logger.info(
                f"Client connected"
                f"({len(self.clients)} total)"
            )

        except Exception as e:

            self.logger.error(
                f"Connection failed: {e}"
            )

    async def disconnect(
        self,
        websocket: WebSocket
    ):
        try:
            if websocket in self.clients:
                self.clients.remove(websocket)

            self.logger.info(
                f"Client Disconnected "
                f"({len(self.clients)} total)"
            )

        except Exception as e:

            self.logger.error(
                f"Disconnect failed: {e}"
            )

    async def broadcast(
        self,
        message: str
    ):
        if not self.clients:
            return
        
        dead_clients = []

        for client in self.clients:

            try:
                await client.send_text(message)

            except Exception as e:

                self.logger.warning(
                    f"Failed sending log: {e}"
                )

                dead_clients.append(client)

        for client in dead_clients:
            await self.disconnect(client)

    def emit(
        self,
        message: str
    ):
        try:

            loop = asyncio.get_running_loop()

            loop.create_task(
                self.broadcast(message)
            )

        except RuntimeError:
            pass

        except Exception as e:
            self.logger.error(
                f"Emit failed: {e}"
            )

    def run(self):
        try:
            self.logger.info(
                f"Starting log server ",
                f"on ws://{self.host}:{self.port}/logs"
            )

            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="warning"
            )

        except Exception as e:
            self.logger.critical(
                f"Server crashed: {e}"
            )
