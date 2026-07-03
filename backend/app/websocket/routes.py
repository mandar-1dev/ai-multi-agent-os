from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/agent-status")
async def agent_status_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Client doesn't need to send anything; this just keeps the socket open.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
