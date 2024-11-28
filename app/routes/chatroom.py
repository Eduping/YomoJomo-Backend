from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import ChatRoomCreate, create_response
from fastapi.encoders import jsonable_encoder
from crud import create_chatroom
from database import get_db
router = APIRouter()
@router.post("/")
def create_new_chatroom(chatroom: ChatRoomCreate, user_id: int, db: Session = Depends(get_db)):
    chat_room = create_chatroom(db, chatroom, user_id)
    chat_room_data = jsonable_encoder(chat_room)
    return create_response(200, True, "Chatroom created successfully", chat_room_data)