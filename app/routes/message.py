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
from models import StudentRecord
import openai
import json

router = APIRouter()

CLASSIFICATION_PROMPT = """
You are an expert in identifying the intent of user queries based on a question.
Categorize the question into one of the following categories:
1. performance: Questions related to analyzing academic performance and trends, and suggesting learning strategies.
2. summary: Questions requiring a summary opinion based on volunteer activities, creative activities, and detailed skills.
3. counseling: Questions requesting counseling plans or strategies for parent-student discussions.
4. recommendation: Questions recommending suitable academic majors or career paths based on student records.
5. unknown: For questions that do not fit into the above categories.

Respond with the category name only.
"""

TASK_PROMPTS = {
    "performance": """
    Context를 바탕으로 학생의 학업 성취도를 분석해 주세요:
    - 과목별 성적이 상위 몇%에 해당하는지 분석해 주세요.
    - 성적 추세(상승 또는 하락)를 판단해 주세요.
    - 분석 결과를 바탕으로 학습 방안을 제시해 주세요.
    답변은 반드시 한국어로 작성해 주세요.
    context:
    """,
    "summary": """
    Context를 바탕으로 학생의 봉사활동, 창의적 체험활동, 세부능력 및 특기사항을 분석해 주세요:
    - 학생의 학업 태도, 강점, 개선점을 포함한 종합 의견을 작성해 주세요.
    - 종합 의견은 10문장 이내로 작성해 주세요.
    - 답변은 반드시 한국어로 작성해 주세요.
    context:
    """,
    "counseling": """
    Context를 바탕으로 학생 상담을 위한 계획과 방향성을 제시해 주세요:
    - 학부모와의 상담 시 효과적인 소통 방안을 포함해 주세요.
    답변은 반드시 한국어로 작성해 주세요.
    context:
    """,
    "recommendation": """
    Context를 바탕으로 학생의 성적, 독서기록, 체험활동을 종합적으로 분석해 주세요:
    - 학생에게 적합한 학과와 진로를 추천해 주세요.
    - 추천 이유를 간단히 설명해 주세요.
    답변은 반드시 한국어로 작성해 주세요.
    context:
    """
}

@router.post(
    "",
    responses={
        200: create_example_response("Message sent successfully", common_examples["message_sent_success"]),
    },
)
def send_message(    
    chatroom_id: int,
    message: MessageCreate,
    student_id: int,  # 학생 id
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    # 1. 판별 단계
    classification_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": f"Question: {message.question}"}
        ]
    )
    category = classification_response.choices[0].message.content
    print(f"사용자의 질문 의도 : {category}")

    # 알 수 없음 처리
    if category == "unknown":
        return {"message": "학업 성취도, 종합 의견 작성, 상담, 학과 추천에 관한 질문에만 답변할 수 있습니다! 궁금하신 사항이 있으면 다시 질문해주세요~"}
    
    # 2. 학생 정보 로드 및 context 생성
    student = (
        db.query(StudentRecord)
        .filter(StudentRecord.id == student_id, StudentRecord.deleted_at.is_(None))
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    text_data = student.text_data

    if isinstance(text_data, str):
        try:
            text_data = json.loads(text_data)
        except json.JSONDecodeError:
            text_data = {}
    if not isinstance(text_data, dict):
        text_data = {}

    if category == "performance":
        filtered_text_data = {
            "교과학습발달상황": text_data.get("수상경력", ""),
            "수상경력": text_data.get("인적사항", ""),
        }
    elif category == "summary":
        filtered_text_data = {
            "독서활동상황": text_data.get("수상경력", ""),
            "창의적 체험활동상황": text_data.get("인적사항", ""),
            "행동특성 및 종합의견": text_data.get("인적사항", ""),
            "자격증 및 인증 취득상황": text_data.get("인적사항", ""),
        }
    elif category == "counseling":
        filtered_text_data = {
            "인적사항": text_data.get("수상경력", ""),
            "교과학습발달상황": text_data.get("인적사항", ""),
            "행동특성 및 종합의견": text_data.get("인적사항", ""),
        }
    elif category == "recommendation": 
        filtered_text_data = {
            "진로희망사항": text_data.get("수상경력", ""),
            "교과학습발달상황": text_data.get("인적사항", ""),
            "독서활동상황": text_data.get("인적사항", ""),
            "수상경력": text_data.get("인적사항", ""),
        }

    filtered_text_data = json.dumps(text_data, ensure_ascii=False)
    print(f"최종 전달 context : {filtered_text_data}")

    chatbot = get_chatbot(chatroom_id, db)

    bot_response = chatbot.invoke(filtered_text_data)['response']

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