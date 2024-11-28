from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schemas import MessageCreate, create_response
from models import Message as MessageModel
from crud import create_message
from langchainbot.bot import get_chatbot
from database import get_db

router = APIRouter()
@router.post("/")
def send_message(chatroom_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    chatbot = get_chatbot(chatroom_id, db)

    bot_response = chatbot.invoke(message.question)['response']

    create_message(db, question=message.question, answer=bot_response, chatroom_id=chatroom_id)

    data = {"user_message": message.question, "bot_response": bot_response}
    return create_response(200, True, "Message sent successfully", data)

@router.get("/chatroom/{chatroom_id}")
def get_messages(chatroom_id: int, db: Session = Depends(get_db)):
    messages = db.query(MessageModel).filter(MessageModel.chatroom_id == chatroom_id).all()
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found in this chatroom")
    return create_response(200, True, "Messages retrieved successfully", jsonable_encoder(messages))