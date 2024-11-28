from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schemas import MessageCreate, create_response
from models import Message as MessageModel
from crud.message_crud import create_message
from langchainbot.bot import get_chatbot
from database import get_db
from util.examples import common_examples, create_example_response
from auth.oauth2 import get_current_user

router = APIRouter()
@router.post(
    "",
    responses={
        200: create_example_response("Message sent successfully", common_examples["message_sent_success"]),
    },
)
def send_message(chatroom_id: int, message: MessageCreate, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    chatbot = get_chatbot(chatroom_id, db)

    bot_response = chatbot.invoke(message.question)['response']

    create_message(db, question=message.question, answer=bot_response, chatroom_id=chatroom_id)

    data = {"user_message": message.question, "bot_response": bot_response}
    return create_response(200, True, "Message sent successfully", data)

@router.get(
    "",
    responses={
        200: create_example_response("Messages retrieved successfully", common_examples["messages_retrieved_success"]),
        404: create_example_response("No messages found in this chatroom", common_examples["messages_not_found"]),
    },
)
def get_messages(chatroom_id: int, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(MessageModel).filter(MessageModel.chatroom_id == chatroom_id).all()
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found in this chatroom")
    return create_response(200, True, "Messages retrieved successfully", jsonable_encoder(messages))