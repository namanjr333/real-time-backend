from sqlalchemy import Column, Integer, String
from app.core.database import Base

class ChatRoom(Base):
    __tablename__ = "chatrooms"
    id = Column(Integer, primary_key=True)
    name = Column(String)
