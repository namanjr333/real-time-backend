class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, chat_id, websocket):
        await websocket.accept()
        self.active_connections.setdefault(chat_id, []).append(websocket)

    def disconnect(self, chat_id, websocket):
        self.active_connections[chat_id].remove(websocket)

    async def broadcast(self, chat_id, message):
        for ws in self.active_connections.get(chat_id, []):
            await ws.send_text(message)

    async def broadcast_except(self, chat_id, message, exclude_websocket):
        for ws in self.active_connections.get(chat_id, []):
            if ws is not exclude_websocket:
                await ws.send_text(message)
