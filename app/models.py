from sqlalchemy import Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.mysql import JSON

class BaseModelMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
class User(Base, BaseModelMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    chatrooms = relationship("ChatRoom", back_populates="owner")

class ChatRoom(Base, BaseModelMixin):
    __tablename__ = "chatrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = relationship("Message", back_populates="chatroom")
    owner = relationship("User", back_populates="chatrooms")

class Message(Base, BaseModelMixin):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"))
    chatroom = relationship("ChatRoom", back_populates="messages")
class StudentRecord(Base, BaseModelMixin):
    __tablename__ = "student_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(2092), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text_data = Column(JSON)
