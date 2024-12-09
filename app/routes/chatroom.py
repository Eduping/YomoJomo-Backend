from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    "",
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
    "",
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

    # 최신 메시지를 기준으로 각 채팅방의 정보를 가져오기
    subquery = (
        db.query(
            Message.chatroom_id,
            func.max(Message.created_at).label("latest_message_time")
        )
        .group_by(Message.chatroom_id)
        .subquery()
    )

    # 채팅방과 최신 메시지 결합
    chatrooms_query = (
        db.query(
            ChatRoom.id,
            ChatRoom.name,
            Message.answer.label("last_message"),
            subquery.c.latest_message_time.label("last_message_time"),
        )
        .join(subquery, ChatRoom.id == subquery.c.chatroom_id)
        .join(Message, (Message.chatroom_id == ChatRoom.id) & (Message.created_at == subquery.c.latest_message_time))
        .filter(ChatRoom.user_id == user_id)
        .order_by(subquery.c.latest_message_time.desc())
        .offset(offset)
        .limit(size)
    )

    chatrooms = chatrooms_query.all()
    # 데이터 변환
    data = [
        {
            "id": chatroom.id,
            "name": chatroom.name,
            "last_message": chatroom.last_message,
            "last_message_time": chatroom.last_message_time,
        }
        for chatroom in chatrooms
    ]

    # 전체 개수 계산
    total_count = db.query(ChatRoom).filter(ChatRoom.user_id == user_id).count()

    if not chatrooms:
        return create_response(200, False, "No chatrooms found", {"items": [], "total": 0, "page": page, "size": size})
    
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