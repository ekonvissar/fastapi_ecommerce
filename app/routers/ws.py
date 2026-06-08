from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.ws.auth import get_user_id_from_token
from app.ws.manager import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/echo")
async def echo_websocket(websocket: WebSocket):
    """
    Шаг 1: учебный эндпоинт без авторизации.
    Клиент шлёт текст — сервер возвращает его обратно.
    """
    await websocket.accept()
    await websocket.send_json(
        {"type": "connected", "message": "Echo WebSocket is ready"}
    )

    try:
        while True:
            text = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "message": text})
    except WebSocketDisconnect:
        return


@router.websocket("/ws/orders")
async def orders_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
):
    """
    Шаги 2–4: личный канал пользователя.
    Сюда приходят события о заказах (например, после checkout).
    """
    try:
        user_id = get_user_id_from_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return

    await ws_manager.connect(user_id, websocket)
    await websocket.send_json(
        {
            "type": "connected",
            "message": "Subscribed to order notifications",
            "user_id": user_id,
        }
    )

    try:
        while True:
            text = await websocket.receive_text()
            if text == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
