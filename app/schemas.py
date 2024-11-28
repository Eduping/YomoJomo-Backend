from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any
from fastapi.responses import JSONResponse

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None

def create_response(
    status,
    success: bool,
    message: Optional[str] = None,
    data: Optional[Any] = None

) -> JSONResponse:
    return JSONResponse(
        content={
            "status": status,
            "success": success,
            "message": message,
            "data": data,
        },
        status_code=status,
    )
class MessageCreate(BaseModel):
    question: str

class Message(BaseModel):
    question: str
    answer: str
    id: int
    chatroom_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatRoomBase(BaseModel):
    name: str

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoom(ChatRoomBase):
    id: int
    user_id: int
    messages: List[Message] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

# User 생성용 요청 스키마
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# User 응답 스키마
class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True