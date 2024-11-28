from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ChatRoomCreate, ChatRoom
from crud import create_chatroom
from database import get_db
router = APIRouter()
@router.post("/", response_model=ChatRoom)
def create_new_chatroom(chatroom: ChatRoomCreate, user_id: int, db: Session = Depends(get_db)):
    return create_chatroom(db, chatroom, user_id)