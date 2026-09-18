from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.chat import ChatRoom
from app.models.user import User
from app.core.security import decode_token
from pydantic import BaseModel

router = APIRouter(prefix="/chats")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatCreate(BaseModel):
    name: str

class DirectChatRequest(BaseModel):
    target_username: str

@router.post("/create")
def create_chat(data: ChatCreate, db: Session = Depends(get_db)):
    # Check if chat with same name exists
    existing = db.query(ChatRoom).filter(ChatRoom.name == data.name).first()
    if existing:
        return {"chat_id": existing.id, "name": existing.name, "created": False}
    
    chat = ChatRoom(name=data.name)
    db.add(chat)
    db.commit()
    return {"chat_id": chat.id, "name": chat.name, "created": True}

@router.post("/direct")
def start_direct_chat(data: DirectChatRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
        current_user = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    target = db.query(User).filter(User.username == data.target_username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Create consistent room name
    users = sorted([current_user, data.target_username])
    room_name = f"dm_{users[0]}_{users[1]}"

    existing = db.query(ChatRoom).filter(ChatRoom.name == room_name).first()
    if existing:
        return {"chat_id": existing.id, "name": existing.name, "created": False}

    chat = ChatRoom(name=room_name)
    db.add(chat)
    db.commit()
    return {"chat_id": chat.id, "name": chat.name, "created": True}

@router.get("/dms")
def get_user_dms(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
        current_user = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Find all chats starting with dm_ that contain the username
    # This is a simple implementation. In production, use a many-to-many relationship.
    all_dms = db.query(ChatRoom).filter(ChatRoom.name.like("dm_%")).all()
    
    user_dms = []
    for chat in all_dms:
        parts = chat.name.split("_")
        if len(parts) == 3:
            u1, u2 = parts[1], parts[2]
            if current_user == u1:
                user_dms.append({"chat_id": chat.id, "other_user": u2})
            elif current_user == u2:
                user_dms.append({"chat_id": chat.id, "other_user": u1})
                
    return user_dms

@router.get("/find/{name}")
def find_chat_by_name(name: str, db: Session = Depends(get_db)):
    chat = db.query(ChatRoom).filter(ChatRoom.name == name).first()
    if chat:
        return {"chat_id": chat.id, "name": chat.name}
    return {"error": "Chat not found"}

from app.models.message import Message

@router.get("/{chat_id}/messages")
def get_chat_messages(chat_id: int, db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp).all()
