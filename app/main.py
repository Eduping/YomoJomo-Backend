from fastapi import FastAPI
from exceptions import http_exception_handler, validation_exception_handler, global_exception_handler, custom_exception_handler, CustomException
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import user, chatroom, message, student_record
app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:3000",
    # "https://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # 쿠키를 포함한 인증 정보를 허용하려면 True
    allow_methods=["*"],  # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],  # 허용할 HTTP 헤더
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(CustomException, custom_exception_handler)
# 라우터 등록
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(chatroom.router, prefix="/chatrooms", tags=["ChatRooms"])
app.include_router(message.router, prefix="/chatrooms/{chatroom_id}/messages", tags=["Messages"])
app.include_router(student_record.router, prefix="/student-records", tags=["Student Records"])
@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot API"}