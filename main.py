from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from contextlib import asynccontextmanager
# from fastapi.middleware import LifespanMiddleware


app = FastAPI()
data_file = "data.json"

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def chorano(self, data: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(data))

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


conmanager = ConnectionManager()


def read_data():
    try:
        with open(data_file, "r") as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return "not a valid json or file not found"


async def monitor_data():
    current_data = read_data()   
    await conmanager.chorano(current_data)
    await asyncio.sleep(1)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     task = asyncio.create_task(monitor_data())
#     try: 
#         yield 
#     finally:
#         task.cancel()
#         await task


@app.websocket("/ws")
async def webscoket_endpoint(websocket: WebSocket):
    await conmanager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        conmanager.disconnect(websocket)



