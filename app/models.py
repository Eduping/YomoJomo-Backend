from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    chatrooms = relationship("ChatRoom", back_populates="owner")

class ChatRoom(Base):
    __tablename__ = "chatrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = relationship("Message", back_populates="chatroom")
    owner = relationship("User", back_populates="chatrooms")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"))
    chatroom = relationship("ChatRoom", back_populates="messages")