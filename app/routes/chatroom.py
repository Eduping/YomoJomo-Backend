from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import ChatRoomCreate, create_response
from fastapi.encoders import jsonable_encoder
from crud.chatroom_crud import create_chatroom
from database import get_db
from util.examples import common_examples, create_example_response
router = APIRouter()
@router.post(
    "/",
    responses={
        200: create_example_response(
            "Chatroom created successfully", common_examples["chatroom_created_success"]
        ),
        400: create_example_response(
            "Invalid request", common_examples["error_400_invalid_request"]
        ),
    },
)
def create_new_chatroom(chatroom: ChatRoomCreate, user_id: int, db: Session = Depends(get_db)):
    chat_room = create_chatroom(db, chatroom, user_id)
    chat_room_data = jsonable_encoder(chat_room)
    return create_response(200, True, "Chatroom created successfully", chat_room_data)