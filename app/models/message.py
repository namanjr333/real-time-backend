from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chatrooms.id"))
    sender = Column(String)
    text = Column(String)
    msg_type = Column(String, default="text")
    timestamp = Column(DateTime, default=datetime.utcnow)
