from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import ChatRoomCreate, create_response
from fastapi.encoders import jsonable_encoder
from crud.chatroom_crud import create_chatroom
from database import get_db
from models import ChatRoom, Message
from util.examples import common_examples, create_example_response
from fastapi import Query
from auth.oauth2 import get_current_user
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
def create_new_chatroom(chatroom: ChatRoomCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    chat_room = create_chatroom(db, chatroom, user_id)
    chat_room_data = jsonable_encoder(chat_room)
    return create_response(200, True, "Chatroom created successfully", chat_room_data)

@router.get(
    "/",
    responses={
        200: create_example_response(
            "Chatroom list retrieved successfully", common_examples["chatroom_list_success"]
        ),
        400: create_example_response(
            "Invalid request", common_examples["error_400_invalid_request"]
        ),
    },
)
def get_chatrooms(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
):
    """
    채팅방 목록을 페이지네이션과 함께 반환합니다.
    """
    offset = (page - 1) * size

    # 채팅방과 최신 메시지를 가져오기
    chatrooms = (
        db.query(ChatRoom, Message)
        .join(Message, ChatRoom.id == Message.chatroom_id)
        .filter(ChatRoom.user_id == user_id)
        .order_by(Message.created_at.desc())
        .distinct(ChatRoom.id)
        .offset(offset)
        .limit(size)
        .all()
    )
    for chatroom, message in chatrooms:
        print(chatroom, message)
    # 데이터 변환
    data = [
        {
            "id": chatroom.id,
            "last_message": message.answer if message else None,
            "last_message_time": message.created_at if message else None,
        }
        for chatroom, message in chatrooms
    ]

    # 전체 개수 계산
    total_count = (
        db.query(ChatRoom)
        .filter(ChatRoom.user_id == user_id)
        .count()
    )

    return create_response(
        200,
        True,
        "Chatroom list retrieved successfully",
        {
            "items": jsonable_encoder(data),
            "total": total_count,
            "page": page,
            "size": size,
        },
    )