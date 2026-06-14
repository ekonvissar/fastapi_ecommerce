from fastapi import WebSocket

from app.ws.messages import OrderCreatedMessage


class ConnectionManager:
    """Хранит активные WebSocket-соединения по user_id."""

    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self._connections.get(user_id, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets:
            self._connections.pop(user_id, None)

    async def notify_user(self, user_id: int, message: OrderCreatedMessage) -> None:
        dead_sockets: list[WebSocket] = []
        for websocket in self._connections.get(user_id, []):
            try:
                await websocket.send_json(message)
            except Exception:
                dead_sockets.append(websocket)

        for websocket in dead_sockets:
            self.disconnect(user_id, websocket)

    @property
    def active_users(self) -> int:
        return len(self._connections)


ws_manager = ConnectionManager()
