from sqlalchemy.orm import Session
from models import ChatRoom
from schemas import ChatRoomCreate
from fastapi.encoders import jsonable_encoder
def create_chatroom(db: Session, chatroom: ChatRoomCreate, user_id: int):
    db_chatroom = ChatRoom(**jsonable_encoder(chatroom), user_id=user_id)
    db.add(db_chatroom)
    db.commit()
    db.refresh(db_chatroom)
    return db_chatroom