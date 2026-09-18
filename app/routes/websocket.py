from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import ConnectionManager
from app.core.database import SessionLocal
from app.models.message import Message
from app.core.security import decode_token
import json

router = APIRouter()
manager = ConnectionManager()

# WebRTC signaling message types - relayed directly to the other peer(s)
# in the room and never persisted as chat messages.
SIGNALING_TYPES = {"call-offer", "call-answer", "ice-candidate", "call-end"}

@router.websocket("/ws/chat/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: int, token: str = Query(...)):
    payload = decode_token(token)          # validate JWT
    username = payload.get("sub")
    print(f"DEBUG: WebSocket connected. Token payload: {payload}, Username: {username}") # Debug print
    await websocket.accept()

    manager.active_connections.setdefault(chat_id, []).append(websocket)
    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_text()
            print(f"DEBUG: Received message: {data} from {username}") # Debug print

            try:
                message_data = json.loads(data)
                msg_type = message_data.get("type", "text")
            except json.JSONDecodeError:
                message_data = {"text": data}
                msg_type = "text"

            if msg_type in SIGNALING_TYPES:
                # Relay SDP offers/answers and ICE candidates straight to the
                # other participant(s) - not stored in the DB, not sent back
                # to the sender.
                relay_data = json.dumps({**message_data, "sender": username})
                await manager.broadcast_except(chat_id, relay_data, websocket)
                continue

            msg_text = message_data.get("text", "")
            msg = Message(chat_id=chat_id, sender=username, text=msg_text, msg_type=msg_type)
            db.add(msg)
            db.commit()

            response_data = json.dumps({"sender": username, "text": msg_text, "type": msg_type})
            await manager.broadcast(chat_id, response_data)
    except WebSocketDisconnect:
        manager.active_connections[chat_id].remove(websocket)
