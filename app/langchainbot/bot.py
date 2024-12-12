from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.orm import Session
from models import Message
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def load_chat_history_from_db(chatroom_id: int, db: Session) -> list:
    """
    DB에서 chatroom_id에 해당하는 대화 기록을 가져와 LangChain 메시지 형식의 리스트로 변환.
    """
    messages = db.query(Message).filter(Message.chatroom_id == chatroom_id).order_by(Message.created_at).all()
    return [
        HumanMessage(content=msg.question) if msg.question else AIMessage(content=msg.answer)
        for msg in messages
    ]


def get_chatbot(chatroom_id: int, db: Session) -> ConversationChain:
    """
    LangChain ConversationChain 생성.
    이전 대화를 DB에서 로드하고 ConversationBufferMemory에 연동.
    """
    # ChatGPT 모델 설정
    chat_model = ChatOpenAI(temperature=0.7, 
                            model="gpt-4o",
                            streaming=True,
                            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                            verbose=True)

    # DB에서 대화 기록 로드
    chat_history = load_chat_history_from_db(chatroom_id, db)

    # ConversationBufferMemory에 대화 기록 추가
    memory = ConversationBufferMemory(return_messages=True)
    memory.chat_memory.messages.extend(chat_history)

    # ConversationChain 생성
    return ConversationChain(llm=chat_model, memory=memory)