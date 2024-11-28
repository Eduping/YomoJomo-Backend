from sqlalchemy.orm import Session
from models import Message as MessageModel

def create_message(db: Session, question: str, answer: str, chatroom_id: int):
    db_message = MessageModel(question=question, answer=answer, chatroom_id=chatroom_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message