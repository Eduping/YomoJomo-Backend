from sqlalchemy.orm import Session
from models import ChatRoom, Message as MessageModel
from schemas import UserCreate, ChatRoomCreate
from models import User as UserModel
from fastapi.encoders import jsonable_encoder

def create_user(db: Session, user: UserCreate):
    db_user = UserModel(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_chatroom(db: Session, chatroom: ChatRoomCreate, user_id: int):
    db_chatroom = ChatRoom(**jsonable_encoder(chatroom), user_id=user_id)
    db.add(db_chatroom)
    db.commit()
    db.refresh(db_chatroom)
    return db_chatroom


def create_message(db: Session, question: str, answer: str, chatroom_id: int):
    db_message = MessageModel(question=question, answer=answer, chatroom_id=chatroom_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message